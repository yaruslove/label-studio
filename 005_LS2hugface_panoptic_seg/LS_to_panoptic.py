import os
import json
import cv2 as cv
import numpy as np
import pickle

from utils.utils import read_yaml, LS2panoptic_map

# Parse args
read_data=read_yaml()
print(read_data)

selected_images = read_data["selected_images"]
LS_json_path = read_data["LS_json_path"]
classes  = read_data["classes"] 
init_id = read_data["init_id"]
path_image = read_data["path_image"]
path_savePickle = read_data["path_savePickle"]


print(f"selected_images {selected_images}")
print(f"LS_json_path {LS_json_path}")
print(f"classes {classes}")
print(f"init_id {init_id}")
print(f"path_image {path_image}")
print(f"path_savePickle {path_savePickle}")



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
panoptic_seg_gt={}
for one_imgObj_LS in need_labels:
    name_image = os.path.basename(one_imgObj_LS['data']['image'])

    # img_read cv2
    full_img_path = os.path.join(path_image, name_image)
    image_np = cv.cvtColor(  cv.imread(full_img_path) , cv.COLOR_BGR2RGB).astype(np.float32)
    
    panoptic_mask, inst2class, init_id = LS2panoptic_map(one_imgObj_LS, classes, init_id)

    panoptic_seg_gt[name_image] = {"panoptic_mask" : panoptic_mask,
                                  "inst2class" : inst2class,
                                  "image":image_np}
    

## Save  pickle
with open(path_savePickle, 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(panoptic_seg_gt, f, pickle.HIGHEST_PROTOCOL)