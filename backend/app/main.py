from contextlib import asynccontextmanager
from io import BytesIO
import platform

from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from fastapi.responses import Response, StreamingResponse
import time
from fastapi.middleware.cors import CORSMiddleware

from .config import (
    API_TITLE,
    API_VERSION,
    MODEL_PATH,
    CLASS_NAMES,
    CONFIDENCE_THRESHOLD,
)

from .inference import ImageClassifier
from .camera import Camera


# ============================================================
# Global classifier
# ============================================================



classifier = None
camera = None


# ============================================================
# FastAPI Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    global classifier
    global camera

    print("=" * 60)
    print("Starting R4I Ginger Classification API")
    print("=" * 60)

    try:
        # Load model once when FastAPI starts
        classifier = ImageClassifier(
            model_path=MODEL_PATH,
            num_threads=4,
        )

        print("=" * 60)
        print("Model ready.")
        print("=" * 60)

         # --------------------------------------------------------
        # Start Raspberry Pi camera
        # --------------------------------------------------------

        camera = Camera(
            width=640,
            height=480,
            jpeg_quality=85,
        )

        camera.start()

        print("=" * 60)
        print("Camera ready.")
        print("=" * 60)

        

    except Exception as e:

        print("=" * 60)
        print("MODEL LOADING FAILED")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {str(e)}")
        print("=" * 60)

        # Keep classifier as None so /health can report
        # that the model is unavailable.
        classifier = None
        camera = None

    yield

    print("=" * 60)
    print("Shutting down API...")
    print("=" * 60)

    if camera is not None:
        camera.stop()


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=(
        "Edge AI image classification API running "
        "on Raspberry Pi using LiteRT/TFLite."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
async def root():

    model_loaded = classifier is not None

    response = {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running" if model_loaded else "degraded",
        "model": MODEL_PATH.name,
        "classes": CLASS_NAMES,
        "device": "Raspberry Pi",
        "runtime": "LiteRT/TFLite",
    }

    if model_loaded:
        response["input_shape"] = (classifier.input_shape.tolist())

    return response


# ============================================================
# CAMERA FRAME
# ============================================================

@app.get("/camera/frame")
async def camera_frame():
    if camera is None:
        raise HTTPException(
            status_code=503,
            detail="Camera is not available."
        )

    try:
        frame = camera.capture_frame()

        return Response(
            content=frame,
            media_type="image/jpeg"
        )

    except Exception as e:
        print("=" * 60)
        print("CAMERA ERROR")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {str(e)}")
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail={
                "error": type(e).__name__,
                "message": str(e)
            }
        )


# ============================================================
# LIVE CAMERA STREAM
# ============================================================

@app.get("/camera/stream")
async def camera_stream():

    if camera is None:
        raise HTTPException(
            status_code=503,
            detail="Camera is not available."
        )

    def generate_frames():

        try:
            while True:

                frame = camera.capture_frame()

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: "
                    + str(len(frame)).encode()
                    + b"\r\n\r\n"
                    + frame
                    + b"\r\n"
                )

                time.sleep(1 / 15)

        except GeneratorExit:
            print("Camera stream client disconnected.")

        except Exception as e:
            print("=" * 60)
            print("CAMERA STREAM ERROR")
            print(f"Type: {type(e).__name__}")
            print(f"Error: {str(e)}")
            print("=" * 60)

    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# ============================================================
# Health Check
# ============================================================

@app.get("/health")
async def health():

    if classifier is None:

        return {
            "status": "unhealthy",
            "model_loaded": False,
            "model": MODEL_PATH.name,
        }

    return {
        "status": "healthy",
        "model_loaded": True,
        "model": MODEL_PATH.name,
        "input_shape": classifier.input_shape.tolist(),
        "input_dtype": str(classifier.input_dtype),
        "output_shape": classifier.output_shape.tolist(),
        "output_dtype": str(classifier.output_dtype),
        "classes": len(CLASS_NAMES),
    }


# ============================================================
# Classes Endpoint
# ============================================================

@app.get("/classes")
async def classes():

    return {
        "classes": [
            {
                "index": index,
                "name": class_name,
            }
            for index, class_name in enumerate(CLASS_NAMES)
        ],
        "confidence_threshold": CONFIDENCE_THRESHOLD,
    }


# ============================================================
# Prediction Endpoint
# ============================================================

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    # --------------------------------------------------------
    # Check model
    # --------------------------------------------------------

    if classifier is None:

        raise HTTPException(
            status_code=503,
            detail="Model is not loaded.",
        )

    # --------------------------------------------------------
    # Read uploaded file
    # --------------------------------------------------------

    image_bytes = await file.read()

    if not image_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    try:

        # ====================================================
        # 1. Open image
        # ====================================================

        image = Image.open(BytesIO(image_bytes))

        detected_format = image.format

        original_size = {
            "width": image.width,
            "height": image.height,
        }

        print("=" * 60)
        print("IMAGE RECEIVED")
        print(f"Filename: {file.filename}")
        print(f"MIME type: {file.content_type}")
        print(f"Format: {detected_format}")
        print(f"Size: {image.size}")
        print(f"Mode: {image.mode}")
        print("=" * 60)

        # ====================================================
        # 2. Verify image
        # ====================================================

        image.verify()

        # ====================================================
        # 3. Re-open image after verify()
        # ====================================================

        image = Image.open(
            BytesIO(image_bytes)
        )

        # ====================================================
        # 4. Convert to RGB
        # ====================================================

        image = image.convert("RGB")

        print(
            "Image ready for inference: "
            f"size={image.size}, "
            f"mode={image.mode}"
        )

        # ====================================================
        # 5. Run LiteRT inference
        # ====================================================

        result = classifier.predict(image)

        # ====================================================
        # 6. Add image/file information
        # ====================================================

        result["filename"] = file.filename
        result["content_type"] = file.content_type
        result["detected_format"] = detected_format
        result["original_size"] = original_size

        # ====================================================
        # 7. Return response
        # ====================================================

        return {
            "success": True,
            **result,
        }

    # ========================================================
    # Invalid image
    # ========================================================

    except UnidentifiedImageError:

        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded file is not a valid "
                "JPEG, JPG, PNG, WEBP, or BMP image."
            ),
        )

    # ========================================================
    # Other errors
    # ========================================================

    except Exception as e:

        print("=" * 60)
        print("IMAGE CLASSIFICATION ERROR")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {str(e)}")
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail={
                "error": type(e).__name__,
                "message": str(e),
            },
        )


# ============================================================
# CAMERA PREDICTION
# ============================================================

@app.post("/predict-camera")
async def predict_camera():

    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded.",
        )

    if camera is None:
        raise HTTPException(
            status_code=503,
            detail="Camera is not available.",
        )

    try:

        # ----------------------------------------------------
        # Capture current camera image
        # ----------------------------------------------------

        image = camera.capture_image()

        # ----------------------------------------------------
        # Run inference
        # ----------------------------------------------------

        result = classifier.predict(image)

        # ----------------------------------------------------
        # Add camera information
        # ----------------------------------------------------

        result["source"] = "raspberry_pi_camera"
        result["image_size"] = {
            "width": image.width,
            "height": image.height,
        }

        return {
            "success": True,
            **result,
        }

    except Exception as e:

        print("=" * 60)
        print("CAMERA CLASSIFICATION ERROR")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {str(e)}")
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail={
                "error": type(e).__name__,
                "message": str(e),
            },
        )


# ============================================================
# System Information
# ============================================================

@app.get("/system")
async def system_info():

    return {
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "processor": platform.processor(),
        "runtime": "LiteRT/TFLite",
        "model": MODEL_PATH.name,
    }