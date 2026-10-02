
from ultralytics import YOLO

# Load model đã train
model = YOLO("best.pt")

# Chạy nhận diện bằng webcam
model.predict(
    source=1,       # Webcam mặc định
    conf=0.8,       # Ngưỡng tin cậy 50%
    show=True,
    save=False,
    imgsz=640
)