
import os
import json
import cv2 as cv

from utils.utils import read_yaml, LS2paddle_seg, change_ext

# Parse args
read_data=read_yaml()
print(read_data)

selected_images = read_data["selected_images"]
LS_json_path = read_data["LS_json_path"]
classes  = read_data["classes"]
dst_anot = read_data["dst_anot"]


print(f"selected_images {selected_images}")
print(f"LS_json_path {LS_json_path}")
print(f"classes {classes}")
print(f"dst_anot {dst_anot}")


# Select need labels
with open( LS_json_path ) as user_file:
    parsed_json = json.load(user_file)
### Select just labeled agree with set
need_labels= []
for n in parsed_json:
    if os.path.basename(n['data']['image']) in selected_images:
        need_labels.append(n)

print(f"need_labels {need_labels}")


# Main loop  
# dst="/Users/YaVolkonskiy/Documents/Projects/tomato/data/002_data_experiments/004_train_Mask2Former_panoptic_23_10_23/paddle_paddle_gray/Annotations_gray/"

for one_imgObj_LS in need_labels:
    result_np = LS2paddle_seg(one_imgObj_LS, classes)
    # naming path 
    name_image = os.path.basename(one_imgObj_LS['data']['image'])
    name_image= change_ext(name_image, "png")
    dst_path = os.path.join(dst_anot, name_image)
    print(f"dst_path {dst_path}")

    # save img
    cv.imwrite(dst_path, result_np)

