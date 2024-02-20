from label_studio_converter.imports.yolo import convert_yolo_to_ls
import os

input_dir_ABOVE = "/home/yaroslav/Documents/001_Projects/005_car_number/data/001_raw_data/001_plates/"
image_ext = "jpeg,.JPEG,.jpg,.JPG,.png,.PNG,.BMP,.jpeg"
image_root_url_ABOVE = "/data/local-files/?d=data/car_data/plates"

for dir in os.listdir(input_dir_ABOVE):
    input_dir = os.path.join(input_dir_ABOVE, dir)
    out_file = os.path.join(input_dir_ABOVE, dir, "yolo_LS.json")
    image_root_url = os.path.join(image_root_url_ABOVE,dir,"images")
    # print(dir)

    convert_yolo_to_ls(input_dir=input_dir, 
                       out_file=out_file,
                       image_ext=image_ext,
                       image_root_url=image_root_url)