"""Export YOLO results without importing the inference framework."""
import csv
from pathlib import Path
COLUMNS = ['ID', 'image_id', 'class_id', 'x_min', 'y_min', 'width', 'height']
# Original dataset.yaml explicitly defines weed=0, crop=1.
CLASS_NAMES = {0: 'weed', 1: 'crop'}

def export_results(results, output):
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    stats = {'total_images': 0, 'images_with_detections': 0, 'total_detections': 0,
             'weed_count': 0, 'crop_count': 0}
    with output.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS); writer.writeheader()
        for result in results:
            stats['total_images'] += 1
            boxes = result.boxes
            if boxes is None: continue
            detected = False
            for box in boxes:
                detected = True
                cls = int(box.cls.item())
                x1, y1, x2, y2 = (float(v) for v in box.xyxy[0].tolist())
                stats['total_detections'] += 1
                writer.writerow(dict(zip(COLUMNS, [stats['total_detections'], Path(result.path).stem,
                    cls, round(x1, 2), round(y1, 2), round(max(0., x2-x1), 2), round(max(0., y2-y1), 2)])))
                if cls == 0: stats['weed_count'] += 1
                elif cls == 1: stats['crop_count'] += 1
            stats['images_with_detections'] += int(detected)
    return stats
