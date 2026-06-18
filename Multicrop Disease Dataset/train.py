from ultralytics import YOLO
import yaml
import os

DATASET_PATH = r"E:\BUITEMS\9 FINAL YEAR PROJECT\FYP Dataset\Multicrop Disease Dataset"

def fix_yaml():
    yaml_path = os.path.join(DATASET_PATH, "data.yaml")
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    data["path"]  = DATASET_PATH
    data["train"] = os.path.join(DATASET_PATH, "train", "images")
    data["val"]   = os.path.join(DATASET_PATH, "valid", "images")
    data["test"]  = os.path.join(DATASET_PATH, "test",  "images")
    fixed_yaml = os.path.join(DATASET_PATH, "data_fixed.yaml")
    with open(fixed_yaml, "w") as f:
        yaml.dump(data, f, allow_unicode=True)
    print(f"[OK] Fixed yaml saved")
    print(f"[OK] Classes ({data['nc']}): {data['names']}")
    return fixed_yaml

if __name__ == '__main__':
    fixed_yaml = fix_yaml()

    # 🔁 CHANGED: load last checkpoint instead of yolov8n.pt
    model = YOLO(r"E:\BUITEMS\9 FINAL YEAR PROJECT\FYP Dataset\Multicrop Disease Dataset\runs\detect\fyp_crop_disease\run1\weights\last.pt")
    print("[OK] Resuming YOLO training from last checkpoint")
    # 🔁 CHANGED: resume training
    results = model.train(resume=True)

    print("\n[DONE] Training complete!")
    print(f"Best model at: fyp_crop_disease/run1/weights/best.pt")

    print("\n[INFO] Evaluating on test set...")
    metrics = model.val(
        data   = fixed_yaml,
        split  = "test",
        plots  = True,
    )

    print("\n─── YOUR RESULTS ───────────────────────")
    print(f"mAP50      : {metrics.box.map50:.4f}   (target: >0.90)")
    print(f"mAP50-95   : {metrics.box.map:.4f}")
    print(f"Precision  : {metrics.box.mp:.4f}")
    print(f"Recall     : {metrics.box.mr:.4f}")
    print("────────────────────────────────────────")