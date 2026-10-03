import httpx


# ============================================================
# BACKEND CONFIGURATION
# ============================================================

API_BASE_URL = "http://entra001.local:8000"


CAMERA_STREAM_URL = f"{API_BASE_URL}/camera/stream"
CAMERA_FRAME_URL = f"{API_BASE_URL}/camera/frame"

PREDICT_CAMERA_URL = f"{API_BASE_URL}/predict-camera"

HEALTH_URL = f"{API_BASE_URL}/health"
CLASSES_URL = f"{API_BASE_URL}/classes"
SYSTEM_URL = f"{API_BASE_URL}/system"


# ============================================================
# API REQUEST
# ============================================================

async def get_json(url: str):

    async with httpx.AsyncClient(timeout=30.0) as client:

        response = await client.get(url)

        response.raise_for_status()

        return response.json()


async def post_json(url: str):

    async with httpx.AsyncClient(timeout=60.0) as client:

        response = await client.post(url)

        response.raise_for_status()

        return response.json()