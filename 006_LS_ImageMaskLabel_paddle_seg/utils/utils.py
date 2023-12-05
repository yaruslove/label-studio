import numpy as np
import os
import json
import cv2 as cv
import shutil
import random


import yaml


def read_yaml():
    with open('config.yaml') as fh:
        read_data = yaml.load(fh, Loader=yaml.FullLoader)
    return read_data


def relative2absalute(np_arr, resolution_orig):
    np_arr_abs = np.copy(np_arr)
    np_arr_abs[:,:1] = np_arr_abs[:,:1]/100*resolution_orig[1]
    np_arr_abs[:,1:] = np_arr_abs[:,1:]/100*resolution_orig[0]
    # np_arr_abs=np.rint(np_arr_abs).astype(np.int32)
    np_arr_abs=np.rint(np_arr_abs).astype(np.int32)

    return np_arr_abs

def get_resolution(one_imgObj_LS):
    w_orig = one_imgObj_LS["annotations"][0]['result'][0]['original_width']
    h_orig = one_imgObj_LS["annotations"][0]['result'][0]['original_height']
    resolution_orig = (h_orig,w_orig)
    return resolution_orig

def change_ext(name_file, new_ext):
    pre, ext = os.path.splitext(name_file)
    return f"{pre}.{new_ext}"

def LS2paddle_seg(one_imgObj_LS, dict_clas):
    
    resolution_orig=get_resolution(one_imgObj_LS)
    full_mask = np.zeros(shape=resolution_orig, dtype=np.uint32)
    
    
    for result in one_imgObj_LS["annotations"][0]["result"]:
        points=result["value"]['points']
        np_polyg=np.array( [np.array(i) for i in points] )
        # Convert relative points to absolute
        np_polyg_abs=relative2absalute(np_polyg, resolution_orig)
        # Add dimension polyg
        np_polyg_abs=np_polyg_abs[np.newaxis, ... ] 
        # Create temporaty mask
        mask = np.zeros(shape=resolution_orig, dtype=np.uint8)
        
        
        # we can't use here number more than 255 fot this cv.fillPoly functione there fore we fill value=1, then will replace it to => init_ids
        name_label = result["value"]["polygonlabels"][0]
        color_clas=dict_clas[name_label]
        
        filled_mask = cv.fillPoly(mask, pts=np_polyg_abs, color=color_clas)
        filled_mask.max()
    
        full_mask[filled_mask == color_clas] = color_clas
    
    
    # zer_np=  np.zeros(shape=resolution_orig, dtype=np.uint32)
    # # meaning labeled layer in 3d RGB array is last = full_mask
    # result_np = np.stack((zer_np, zer_np, full_mask), axis=-1, dtype=np.uint8)
    print(full_mask.shape)
    full_mask=full_mask.astype(np.uint8)
    return full_mask  # result_np
