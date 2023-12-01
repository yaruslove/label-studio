import yaml
import numpy as np
import os
import json
import cv2 as cv

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

def LS2panoptic_map(one_imgObj_LS, classes, init_id):
    
    resolution_orig=get_resolution(one_imgObj_LS)
    full_mask = np.zeros(shape=resolution_orig, dtype=np.uint32)
    inst2class = {}
    
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
        filled_mask = cv.fillPoly(mask, pts=np_polyg_abs, color=1)

        # fill filled_mask by target id
        filled_mask=filled_mask.astype(np.uint32)
        filled_mask[filled_mask == 1] = init_id
        # join full_mask and curent filed mask
        full_mask[filled_mask == init_id] = init_id
        # fill inst2class
        name_label = result["value"]["polygonlabels"][0]
        # print(f"name_label {name_label}")
        inst2class[init_id] = classes[name_label]
        init_id+=1

    ## add background
    full_mask[full_mask==0]=init_id
    inst2class[init_id] = classes["background"]
    init_id+=1

    return full_mask, inst2class, init_id
