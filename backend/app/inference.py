import time
from pathlib import Path

import numpy as np
from PIL import Image

try:
    # Recommended for Raspberry Pi / modern LiteRT
    from ai_edge_litert.interpreter import Interpreter
except ImportError:
    # Fallback for older TFLite installations
    from tflite_runtime.interpreter import Interpreter

from .config import (
    MODEL_PATH,
    CLASS_NAMES,
    CONFIDENCE_THRESHOLD,
)


class ImageClassifier:

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        num_threads: int = 4,
    ):
        """
        Load and initialize the R4I Ginger TFLite/LiteRT model.
        """

        self.model_path = Path(model_path)

        # ---------------------------------------------------------
        # CHECK MODEL FILE
        # ---------------------------------------------------------

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        if not CLASS_NAMES:
            raise ValueError(
                "CLASS_NAMES is empty. "
                "Check class_names.json."
            )

        print("=" * 60)
        print("Loading R4I Ginger model")
        print("=" * 60)

        print(f"Model: {self.model_path}")
        print(f"Classes: {CLASS_NAMES}")

        # ---------------------------------------------------------
        # LOAD LITERT / TFLITE MODEL
        # ---------------------------------------------------------

        self.interpreter = Interpreter(
            model_path=str(self.model_path),
            num_threads=num_threads,
        )

        # Allocate model tensors
        self.interpreter.allocate_tensors()

        # ---------------------------------------------------------
        # GET INPUT / OUTPUT DETAILS
        # ---------------------------------------------------------

        self.input_details = (
            self.interpreter.get_input_details()
        )

        self.output_details = (
            self.interpreter.get_output_details()
        )

        if len(self.input_details) != 1:
            raise RuntimeError(
                f"Expected 1 model input, "
                f"found {len(self.input_details)}."
            )

        if len(self.output_details) != 1:
            raise RuntimeError(
                f"Expected 1 model output, "
                f"found {len(self.output_details)}."
            )

        # ---------------------------------------------------------
        # INPUT INFORMATION
        # ---------------------------------------------------------

        self.input_index = (
            self.input_details[0]["index"]
        )

        self.input_shape = (
            self.input_details[0]["shape"]
        )

        self.input_dtype = (
            self.input_details[0]["dtype"]
        )

        # ---------------------------------------------------------
        # OUTPUT INFORMATION
        # ---------------------------------------------------------

        self.output_index = (
            self.output_details[0]["index"]
        )

        self.output_shape = (
            self.output_details[0]["shape"]
        )

        self.output_dtype = (
            self.output_details[0]["dtype"]
        )

        # ---------------------------------------------------------
        # DETERMINE INPUT SIZE
        # ---------------------------------------------------------

        if len(self.input_shape) != 4:
            raise RuntimeError(
                f"Unexpected input shape: "
                f"{self.input_shape}. "
                f"Expected [1, height, width, 3]."
            )

        self.input_height = int(
            self.input_shape[1]
        )

        self.input_width = int(
            self.input_shape[2]
        )

        self.input_channels = int(
            self.input_shape[3]
        )

        # ---------------------------------------------------------
        # VALIDATE INPUT
        # ---------------------------------------------------------

        if self.input_channels != 3:
            raise RuntimeError(
                f"Expected RGB input with 3 channels, "
                f"but model expects "
                f"{self.input_channels} channels."
            )

        if self.input_dtype != np.float32:
            raise RuntimeError(
                f"Expected float32 input, "
                f"but model expects {self.input_dtype}."
            )

        # ---------------------------------------------------------
        # VALIDATE OUTPUT
        # ---------------------------------------------------------

        if len(self.output_shape) != 2:
            raise RuntimeError(
                f"Unexpected output shape: "
                f"{self.output_shape}. "
                f"Expected [1, number_of_classes]."
            )

        output_classes = int(
            self.output_shape[1]
        )

        if output_classes != len(CLASS_NAMES):
            raise RuntimeError(
                f"Model outputs {output_classes} classes, "
                f"but class_names.json contains "
                f"{len(CLASS_NAMES)} classes."
            )

        # ---------------------------------------------------------
        # PRINT MODEL INFORMATION
        # ---------------------------------------------------------

        print("\nModel loaded successfully.")

        print("\nInput:")
        print(f"  Shape: {self.input_shape}")
        print(f"  Dtype: {self.input_dtype}")
        print(
            f"  Size: "
            f"{self.input_width}x"
            f"{self.input_height}"
        )
        print(
            f"  Channels: "
            f"{self.input_channels}"
        )

        print("\nOutput:")
        print(f"  Shape: {self.output_shape}")
        print(f"  Dtype: {self.output_dtype}")

        print("\nClasses:")

        for index, class_name in enumerate(
            CLASS_NAMES
        ):
            print(
                f"  {index}: {class_name}"
            )

        print("=" * 60)

    # =============================================================
    # PREPROCESS IMAGE
    # =============================================================

    def preprocess(
        self,
        image: Image.Image
    ) -> np.ndarray:
        """
        Prepare image for the exported model.

        IMPORTANT:
        The MobileNetV2 preprocess_input operation is already
        INSIDE the exported model.

        Therefore we DO NOT divide the image by 255 here.

        Input to TFLite:
            float32
            pixel range approximately 0-255
            shape [1, 256, 256, 3]
        """

        # Convert to RGB
        image = image.convert("RGB")

        # Resize to model input dimensions
        image = image.resize(
            (
                self.input_width,
                self.input_height,
            ),
            Image.Resampling.BILINEAR,
        )

        # Convert PIL image to NumPy array
        image_array = np.asarray(
            image,
            dtype=np.float32,
        )

        # Add batch dimension
        image_array = np.expand_dims(
            image_array,
            axis=0,
        )

        # Make absolutely sure dtype matches model
        image_array = image_array.astype(
            self.input_dtype
        )

        return image_array

    # =============================================================
    # PREDICT
    # =============================================================

    def predict(
        self,
        image: Image.Image
    ):
        """
        Run image classification.

        Returns:
            prediction
            class_index
            confidence
            confidence_percent
            status
            probabilities
            inference_time_ms
        """

        start_time = time.perf_counter()

        # ---------------------------------------------------------
        # PREPROCESS
        # ---------------------------------------------------------

        input_tensor = self.preprocess(image)

        # ---------------------------------------------------------
        # RUN MODEL
        # ---------------------------------------------------------

        self.interpreter.set_tensor(
            self.input_index,
            input_tensor,
        )

        self.interpreter.invoke()

        # ---------------------------------------------------------
        # GET OUTPUT
        # ---------------------------------------------------------

        output = self.interpreter.get_tensor(
            self.output_index
        )

        probabilities = np.squeeze(
            output
        ).astype(np.float32)

        # ---------------------------------------------------------
        # VALIDATE OUTPUT
        # ---------------------------------------------------------

        if probabilities.ndim != 1:
            raise RuntimeError(
                f"Unexpected prediction shape: "
                f"{probabilities.shape}"
            )

        if len(probabilities) != len(
            CLASS_NAMES
        ):
            raise RuntimeError(
                f"Model returned "
                f"{len(probabilities)} probabilities, "
                f"but there are "
                f"{len(CLASS_NAMES)} classes."
            )

        # ---------------------------------------------------------
        # MODEL OUTPUT IS SOFTMAX
        # ---------------------------------------------------------
        #
        # The exported model ends with:
        #
        # Dense(4, activation="softmax")
        #
        # Therefore these values are already probabilities.
        #
        # We only clip tiny numerical values.
        # We DO NOT normalize again.
        # ---------------------------------------------------------

        probabilities = np.clip(
            probabilities,
            0.0,
            1.0,
        )

        # ---------------------------------------------------------
        # PREDICTED CLASS
        # ---------------------------------------------------------

        predicted_index = int(
            np.argmax(probabilities)
        )

        confidence = float(
            probabilities[
                predicted_index
            ]
        )

        predicted_class = (
            CLASS_NAMES[predicted_index]
        )

        # ---------------------------------------------------------
        # CONFIDENCE STATUS
        # ---------------------------------------------------------

        if (
            confidence
            >= CONFIDENCE_THRESHOLD
        ):
            status = "classified"
        else:
            status = "low_confidence"

        # ---------------------------------------------------------
        # INFERENCE TIME
        # ---------------------------------------------------------

        elapsed_time_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        # ---------------------------------------------------------
        # ALL CLASS PROBABILITIES
        # ---------------------------------------------------------

        probability_dict = {
            class_name: round(
                float(
                    probabilities[index]
                ),
                6,
            )
            for index, class_name
            in enumerate(CLASS_NAMES)
        }

        # ---------------------------------------------------------
        # RESULT
        # ---------------------------------------------------------

        return {
            "prediction": predicted_class,

            "class_index": predicted_index,

            "confidence": round(
                confidence,
                6,
            ),

            "confidence_percent": round(
                confidence * 100,
                2,
            ),

            "status": status,

            "probabilities": probability_dict,

            "inference_time_ms": round(
                elapsed_time_ms,
                2,
            ),
        }