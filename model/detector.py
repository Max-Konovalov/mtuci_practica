from ultralytics import YOLO
import cv2
from ultralytics.utils.plotting import Annotator

# Загрузка модели
model = YOLO('yolov8s.pt')  # или ваша собственная модель

# Константы
SUITCASE_CLASS_ID = 28  # COCO ID для 'suitcase'
CLASS_NAME_SUITCASE = 'suitcase'


def detect_objects(image):
    """
    Обнаруживает чемоданы на изображении с помощью YOLO.
    Возвращает изображение с обведенными объектами и количество найденных чемоданов.
    """
    results = model(image)[0]
    boxes = results.boxes

    suitcase_boxes = []

    for i in range(len(boxes)):
        class_id = int(boxes.cls[i].item())
        if class_id == SUITCASE_CLASS_ID:
            bbox = boxes.xyxy[i].cpu().numpy().astype(int)
            confidence = boxes.conf[i].item()
            suitcase_boxes.append({
                'bbox': bbox,
                'confidence': confidence,
                'class_id': class_id
            })

    # Отрисовка чемоданов на кадре
    for box in suitcase_boxes:
        x1, y1, x2, y2 = box['bbox']
        confidence = box['confidence']

        # Рисуем прямоугольник
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Подпись с названием и уверенностью
        label = f'{CLASS_NAME_SUITCASE} {confidence:.2f}'
        cv2.putText(image, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    return image, len(suitcase_boxes)


def process_video(input_path, output_path):
    """
    Обрабатывает видео: детектирует и отрисовывает чемоданы на каждом кадре.
    Сохраняет результат в файл и возвращает максимальное число чемоданов за кадр.
    """
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    max_suitcases = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotator = Annotator(frame)

        count = 0
        for box in results[0].boxes:
            class_id = int(box.cls)
            label = results[0].names[class_id]

            if label == CLASS_NAME_SUITCASE:
                count += 1
                annotator.box_label(box.xyxy[0], label)

        max_suitcases = max(max_suitcases, count)
        out.write(annotator.result())

    cap.release()
    out.release()

    return max_suitcases