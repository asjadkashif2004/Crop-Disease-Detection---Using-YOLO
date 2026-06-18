from ultralytics import YOLO
import os

# ─────────────────────────────────────────────
# Path to your best trained model weights
# ─────────────────────────────────────────────
WEIGHTS_PATH = r"E:\BUITEMS\9 FINAL YEAR PROJECT\FYP Dataset\Multicrop Disease Dataset\runs\detect\fyp_crop_disease\run1\weights\best.pt"

DATASET_PATH = r"E:\BUITEMS\9 FINAL YEAR PROJECT\FYP Dataset\Multicrop Disease Dataset"
DATA_YAML    = os.path.join(DATASET_PATH, "data_fixed.yaml")

if __name__ == '__main__':

    # Load your trained model
    model = YOLO(WEIGHTS_PATH)
    print(f"[OK] Model loaded from: {WEIGHTS_PATH}")

    # ─────────────────────────────────────────
    # Run evaluation on test set
    # ─────────────────────────────────────────
    print("\n[INFO] Evaluating on test set...")
    metrics = model.val(
        data    = DATA_YAML,
        split   = "test",
        plots   = True,
        workers = 0,
    )

    print("\n─── TEST SET RESULTS ───────────────────")
    print(f"mAP50      : {metrics.box.map50:.4f}   (target: >0.90)")
    print(f"mAP50-95   : {metrics.box.map:.4f}")
    print(f"Precision  : {metrics.box.mp:.4f}")
    print(f"Recall     : {metrics.box.mr:.4f}")
    print("────────────────────────────────────────")

    # ─────────────────────────────────────────
    # Run prediction on a single image
    # ─────────────────────────────────────────
    # Change this to any image path you want to test
    TEST_IMAGE = r"E:\BUITEMS\9 FINAL YEAR PROJECT\FYP Dataset\Multicrop Disease Dataset\test\images"

    print(f"\n[INFO] Running predictions on test images...")
    results = model.predict(
        source  = TEST_IMAGE,
        save    = True,        # saves images with bounding boxes drawn
        conf    = 0.25,        # confidence threshold
        workers = 0,
    )

    print(f"\n[OK] Predictions saved! Check the 'runs/detect/predict' folder")
    print(f"     Open those images to see bounding boxes on detected diseases")