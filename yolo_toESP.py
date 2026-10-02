
import cv2
import time
import serial
import numpy as np
from ultralytics import YOLO

# =========================
# CAU HINH
# =========================
MODEL_PATH = "best.pt"
SERIAL_PORT = "COM3"
BAUD_RATE = 115200

CONFIDENCE = 0.70
SEND_INTERVAL = 0.25
CAMERA_INDEX = 1
MISSING_TIMEOUT = 0.8

# =========================
# KHOI TAO
# =========================
model = YOLO(MODEL_PATH)
esp = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)

time.sleep(2)
esp.reset_input_buffer()

camera = cv2.VideoCapture(CAMERA_INDEX)

if not camera.isOpened():
    esp.close()
    raise RuntimeError(
        f"Khong mo duoc camera index {CAMERA_INDEX}. "
        "Hay thu CAMERA_INDEX = 0 hoac 1."
    )

last_sent = ""
last_send_time = 0

# =========================
# THONG KE
# =========================
color_aliases = {
    "green": "GREEN",
    "green_leaf": "GREEN",
    "xanh_la": "GREEN",
    "red": "RED",
    "do": "RED",
    "blue": "BLUE",
    "xanh_duong": "BLUE",
}

def reset_statistics():
    global color_counts, total_boxes
    global current_color, object_present
    global last_detection_time, last_sent, last_send_time

    color_counts = {
        "GREEN": 0,
        "RED": 0,
        "BLUE": 0,
    }

    total_boxes = 0
    current_color = None
    object_present = False
    last_detection_time = 0

    # Cho phep gui lai mau ngay sau refresh
    last_sent = ""
    last_send_time = 0

    print("Da lam moi thong ke va trang thai nhan dien.")


reset_statistics()

# =========================
# MAU GIAO DIEN
# =========================
BG_COLOR = (28, 30, 38)
PANEL_COLOR = (42, 45, 56)
WHITE = (245, 245, 245)
GRAY = (175, 180, 190)
GREEN_COLOR = (70, 210, 110)
RED_COLOR = (70, 80, 240)
BLUE_COLOR = (240, 150, 65)
BUTTON_COLOR = (65, 75, 95)
REFRESH_COLOR = (50, 130, 80)
EXIT_COLOR = (60, 60, 200)

COLOR_DISPLAY = {
    "GREEN": GREEN_COLOR,
    "RED": RED_COLOR,
    "BLUE": BLUE_COLOR,
}

WINDOW_NAME = "YOLO Color Sorting Dashboard"

# Kich thuoc va toa do hai nut
REFRESH_BUTTON = (810, 600, 945, 650)
EXIT_BUTTON = (960, 600, 1095, 650)

# Trang thai nut
refresh_requested = False
exit_requested = False


def draw_text(img, text, pos, scale=0.6,
              color=WHITE, thickness=1):
    cv2.putText(
        img, str(text), pos,
        cv2.FONT_HERSHEY_SIMPLEX,
        scale, color, thickness, cv2.LINE_AA
    )


def draw_panel(img, x1, y1, x2, y2, color=PANEL_COLOR):
    cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)


def draw_button(img, rect, label, color):
    x1, y1, x2, y2 = rect
    cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
    cv2.rectangle(img, (x1, y1), (x2, y2), WHITE, 1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.48
    thickness = 1

    text_size = cv2.getTextSize(
        label, font, scale, thickness
    )[0]

    text_x = x1 + (x2 - x1 - text_size[0]) // 2
    text_y = y1 + (y2 - y1 + text_size[1]) // 2

    draw_text(
        img, label, (text_x, text_y),
        scale, WHITE, thickness
    )


def mouse_callback(event, x, y, flags, param):
    global refresh_requested, exit_requested

    if event != cv2.EVENT_LBUTTONDOWN:
        return

    x1, y1, x2, y2 = REFRESH_BUTTON
    if x1 <= x <= x2 and y1 <= y <= y2:
        refresh_requested = True
        return

    x1, y1, x2, y2 = EXIT_BUTTON
    if x1 <= x <= x2 and y1 <= y <= y2:
        exit_requested = True


def build_dashboard(frame, detected_color, confidence, status):
    frame = cv2.resize(frame, (760, 570))

    dashboard = np.zeros((700, 1120, 3), dtype=np.uint8)
    dashboard[:] = BG_COLOR

    draw_text(
        dashboard, "YOLO COLOR SORTING SYSTEM",
        (25, 35), 0.85, WHITE, 2
    )
    draw_text(
        dashboard, time.strftime("%d/%m/%Y  %H:%M:%S"),
        (820, 32), 0.48, GRAY
    )

    # Camera
    draw_panel(dashboard, 20, 55, 780, 650)
    dashboard[70:640, 20:780] = frame

    draw_text(
        dashboard, "LIVE CAMERA",
        (35, 670), 0.5, GRAY
    )

    x1, x2 = 800, 1100

    # Mau dang nhan dien
    draw_panel(dashboard, x1, 55, x2, 205)
    draw_text(
        dashboard, "CURRENT COLOR",
        (x1 + 15, 85), 0.55, GRAY
    )

    if detected_color is not None:
        draw_text(
            dashboard, detected_color,
            (x1 + 15, 130), 0.85,
            COLOR_DISPLAY[detected_color], 2
        )
        draw_text(
            dashboard, f"Confidence: {confidence:.2f}",
            (x1 + 15, 165), 0.48, WHITE
        )
    else:
        draw_text(
            dashboard, "NO OBJECT",
            (x1 + 15, 130), 0.65, GRAY, 2
        )
        draw_text(
            dashboard, "Confidence: --",
            (x1 + 15, 165), 0.48, GRAY
        )

    # Trang thai
    draw_panel(dashboard, x1, 220, x2, 295)
    draw_text(
        dashboard, "SYSTEM STATUS",
        (x1 + 15, 245), 0.45, GRAY
    )
    draw_text(
        dashboard, status,
        (x1 + 15, 275), 0.55, GREEN_COLOR
    )

    # Tong so luot nhan dien
    draw_panel(dashboard, x1, 310, x2, 375)
    draw_text(
        dashboard, "TOTAL DETECTED",
        (x1 + 15, 335), 0.45, GRAY
    )
    draw_text(
        dashboard, str(total_boxes),
        (x1 + 15, 363), 0.8, WHITE, 2
    )

    # Thong ke tung mau
    draw_panel(dashboard, x1, 390, x2, 575)
    draw_text(
        dashboard, "COLOR STATISTICS",
        (x1 + 15, 420), 0.5, WHITE
    )

    rows = [
        ("GREEN", 460, GREEN_COLOR),
        ("RED", 500, RED_COLOR),
        ("BLUE", 540, BLUE_COLOR),
    ]

    for color_name, y, color in rows:
        draw_text(
            dashboard, color_name,
            (x1 + 15, y), 0.55, color, 2
        )
        draw_text(
            dashboard, color_counts[color_name],
            (x2 - 35, y), 0.6, WHITE, 2
        )

    # Mau gan nhat
    draw_panel(dashboard, x1, 585, x2, 590)
    if detected_color is not None:
        draw_text(
            dashboard, f"CURRENT: {detected_color}",
            (x1 + 12, 580), 0.42,
            COLOR_DISPLAY[detected_color]
        )

    # Hai nut dieu khien
    draw_button(
        dashboard, REFRESH_BUTTON,
        "REFRESH", REFRESH_COLOR
    )
    draw_button(
        dashboard, EXIT_BUTTON,
        "Q - EXIT", EXIT_COLOR
    )

    draw_text(
        dashboard, "Click REFRESH to reset counters",
        (25, 695), 0.42, GRAY
    )

    return dashboard


# =========================
# CHUONG TRINH CHINH
# =========================
cv2.namedWindow(WINDOW_NAME)
cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

print("Da ket noi ESP32.")
print("Nhan Q de thoat, hoac bam REFRESH de lam moi.")

try:
    while True:
        if exit_requested:
            break

        ret, frame = camera.read()

        if not ret:
            print("Khong doc duoc camera")
            break

        results = model.predict(
            source=frame,
            conf=CONFIDENCE,
            imgsz=640,
            verbose=False
        )

        detected_color = None
        detected_confidence = 0.0

        # Giu logic chon confidence cao nhat
        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue

            boxes = result.boxes
            best_index = int(boxes.conf.argmax())

            class_id = int(boxes.cls[best_index])
            confidence = float(boxes.conf[best_index])
            class_name = result.names[class_id].lower()

            if class_name in color_aliases:
                detected_color = color_aliases[class_name]
                detected_confidence = confidence

        now = time.time()

        # Dem mot luot nhan dien
        if detected_color is not None:
            last_detection_time = now

            if not object_present:
                object_present = True
                current_color = detected_color

                color_counts[detected_color] += 1
                total_boxes += 1

                print(
                    f"Nhan dien luot moi: {detected_color} "
                    f"| Tong: {total_boxes}"
                )
            else:
                current_color = detected_color

        elif (
            object_present
            and now - last_detection_time >= MISSING_TIMEOUT
        ):
            object_present = False
            current_color = None

        # Gui mau qua Serial - giu logic cu
        if detected_color is not None:
            if (
                detected_color != last_sent
                or now - last_send_time >= SEND_INTERVAL
            ):
                esp.write(
                    (detected_color + "\n").encode("utf-8")
                )
                last_sent = detected_color
                last_send_time = now

        # Neu bam REFRESH:
        # xoa thong ke va trang thai dem, khong reset ESP32
        if refresh_requested:
            reset_statistics()
            refresh_requested = False

        # Hien thi camera va bounding box YOLO
        annotated_frame = results[0].plot()

        if detected_color is not None:
            label = (
                f"COLOR: {detected_color} "
                f"({detected_confidence:.2f})"
            )
            cv2.putText(
                annotated_frame, label, (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                COLOR_DISPLAY[detected_color], 2,
                cv2.LINE_AA
            )

        dashboard = build_dashboard(
            annotated_frame,
            detected_color,
            detected_confidence,
            "CONNECTED"
        )

        cv2.imshow(WINDOW_NAME, dashboard)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == ord("Q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()
    esp.close()

    print("\n===== THONG KE CUOI =====")
    print(f"Tong luot nhan dien: {total_boxes}")
    print(f"GREEN: {color_counts['GREEN']}")
    print(f"RED:   {color_counts['RED']}")
    print(f"BLUE:  {color_counts['BLUE']}")
    print("Da dong camera va Serial.")