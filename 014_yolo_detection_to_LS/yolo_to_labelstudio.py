import os
from PIL import Image
import json
import yaml
import argparse
from ultralytics import YOLO

def load_config(config_path):
    """Загрузка конфигурации из YAML файла"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def yolo_to_labelstudio(image_base, labels_dir, images_prefix, class_names):
    """
    Конвертирует разметку из формата YOLO в формат Label Studio
    
    Args:
        image_base (str): Путь к директории с изображениями
        labels_dir (str): Путь к директории с YOLO-разметкой
        images_prefix (str): Префикс пути для изображений в Label Studio
        class_names (list): Список названий классов из модели YOLO
    
    Returns:
        list: Список задач в формате Label Studio
    """
    tasks = []
    processed = 0
    skipped = 0
    
    for img_file in os.listdir(image_base):
        if not img_file.lower().endswith(('.png', '.jpg', '.jpeg', '.heic')):
            continue
            
        image_path = os.path.join(image_base, img_file)
        base_name = os.path.splitext(img_file)[0]
        label_file = os.path.join(labels_dir, f"{base_name}.txt")
        
        if not os.path.exists(label_file):
            print(f"Пропуск {img_file}: файл разметки не найден")
            skipped += 1
            continue
            
        task = {
            "data": {
                "image": f"/data/local-files/?d={images_prefix}/{img_file}"
            },
            "annotations": [{
                "result": []
            }]
        }
        
        try:
            image = Image.open(image_path)
            img_width, img_height = image.size
        except Exception as e:
            print(f"Ошибка при открытии {img_file}: {e}")
            skipped += 1
            continue
        
        try:
            with open(label_file, 'r') as f:
                for line in f:
                    label_id, x_center, y_center, width, height = map(float, line.strip().split())
                    label_id = int(label_id)
                    
                    # Получаем название класса из списка
                    class_name = class_names[label_id] if label_id < len(class_names) else f"class_{label_id}"
                    
                    x_center *= img_width
                    y_center *= img_height
                    width *= img_width
                    height *= img_height
                    
                    result_item = {
                        "original_width": img_width,
                        "original_height": img_height,
                        "image_rotation": 0,
                        "value": {
                            "x": (x_center - width/2) * 100 / img_width,
                            "y": (y_center - height/2) * 100 / img_height,
                            "width": width * 100 / img_width,
                            "height": height * 100 / img_height,
                            "rotation": 0,
                            "rectanglelabels": [class_name]
                        },
                        "from_name": "label",
                        "to_name": "image",
                        "type": "rectanglelabels",
                        "origin": "manual"
                    }
                    
                    task["annotations"][0]["result"].append(result_item)
            
            tasks.append(task)
            processed += 1
            print(f"Обработано: {img_file}")
            
        except Exception as e:
            print(f"Ошибка при обработке разметки {label_file}: {e}")
            skipped += 1
            continue
    
    print(f"\nСтатистика обработки:")
    print(f"Успешно обработано: {processed}")
    print(f"Пропущено: {skipped}")
    
    return tasks

def main():
    parser = argparse.ArgumentParser(description='Конвертация YOLO разметки в формат Label Studio')
    parser.add_argument('--config', required=True, help='Путь к конфигурационному YAML файлу')
    
    args = parser.parse_args()
    config = load_config(args.config)
    
    print("Загрузка модели YOLO...")
    model = YOLO(config['paths']['model_path'])
    class_names = model.names
    print(f"Загружены классы: {class_names}")
    
    print("\nНачало конвертации...")
    tasks = yolo_to_labelstudio(
        config['paths']['image_dir'],
        config['paths']['labels_dir'],
        config['label_studio']['images_prefix'],
        class_names
    )
    
    output_path = config['paths']['output']
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    
    print(f"\nКонвертация завершена.")
    print(f"Результат сохранен в: {output_path}")

if __name__ == "__main__":
    main() 