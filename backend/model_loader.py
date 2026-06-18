"""
model_loader.py
Loads the YOLOv8 model once when the Django server starts.
All prediction requests reuse this single loaded instance.
"""

import os
from django.conf import settings

_model = None


def get_model():
    """
    Returns the loaded YOLO model.
    Loads it on first call, then caches it for all future requests.
    """
    global _model

    if _model is not None:
        return _model

    try:
        from ultralytics import YOLO

        weights_path = settings.MODEL_WEIGHTS_PATH

        if not os.path.exists(weights_path):
            raise FileNotFoundError(
                f"Model weights not found at: {weights_path}\n"
                f"Please update MODEL_WEIGHTS_PATH in settings.py"
            )

        print(f"[MODEL] Loading YOLOv8 model from: {weights_path}")
        _model = YOLO(weights_path)
        print(f"[MODEL] Model loaded successfully!")
        return _model

    except Exception as e:
        print(f"[MODEL ERROR] Failed to load model: {e}")
        raise