from pathlib import Path
import json


# ============================================================
# Base directory
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# Model
# ============================================================

MODEL_PATH = BASE_DIR / "models" / "r4i_ginger.tflite"

CLASS_NAMES_PATH = BASE_DIR / "models" / "class_names.json"


# ============================================================
# Load class names
# ============================================================

with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
    CLASS_NAMES = json.load(f)


# ============================================================
# Validate class mapping
# ============================================================

if not isinstance(CLASS_NAMES, list):
    raise ValueError(
        "class_names.json must contain a JSON list."
    )

if not CLASS_NAMES:
    raise ValueError(
        "class_names.json is empty."
    )


NUM_CLASSES = len(CLASS_NAMES)


# ============================================================
# Classification settings
# ============================================================

CONFIDENCE_THRESHOLD = 0.60


# ============================================================
# API settings
# ============================================================

API_TITLE = "R4I Ginger Classification API"
API_VERSION = "1.0.0"