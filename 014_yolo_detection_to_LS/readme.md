# YOLO to Label Studio

1. Установите необходимые зависимости:
```bash
pip install ultralytics pillow pyyaml
```

2. Создайте и настройте файл конфигурации `config.yml` с вашими путями:
```yaml
paths:
  image_dir: "/путь/к/изображениям"
  labels_dir: "/путь/к/yolo/разметке"
  model_path: "/путь/к/модели.pt"  # опционально
  output: "/путь/для/сохранения/tasks.json"

label_studio:
  images_prefix: "prefix/path/in/labelstudio"

class_names: # опционально
  0: front_bach # название класса в Label Studio
  1: background_batch # название класса в Label Studio
```

3. Запустите скрипт:
```bash
python yolo_to_labelstudio.py --config config.yml
```