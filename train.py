
from ultralytics import YOLO

# Dataset Roboflow
DATA_YAML = (
    "phanloaimau.v1-phanloaimau.yolov8/data.yaml"
)

# Model YOLOv8 Nano pretrained
model = YOLO("yolov8n.pt")

# Train
model.train(
    data=DATA_YAML,
    epochs=100,
    imgsz=640,
    batch=8,
    patience=20,
    workers=4,
    device="cpu",
    project="runs/color",
    name="yolov8_color",
    plots=True,
    save=True
)

print("Training completed!")
print("Best model: runs/color/yolov8_color/weights/best.pt")