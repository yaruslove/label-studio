import cv2 as cv
import numpy as np
import torch


def iter_items(label_path):
    list_clas = []
    list_polyg = []

    # print(f"resolution_label {resolution_label}")
    with open(label_path) as f:
        lines = f.readlines()

    for line in lines:
        polyg_class = line[0]
        data_line = line[1:]

        arr=np.array(data_line.strip().split(" ")).astype("f2")* np.asarray(100, dtype='f2')
        arr = np.reshape(arr, (int(len(arr)/2), 2 ))

        list_clas.append(int(polyg_class))
        list_polyg.append(arr)

    return list_polyg, list_clas



def get_resolution(path_img):
    h_orig,w_orig,_ = cv.imread(path_img).shape
    resolution_label = (h_orig,w_orig)
    return resolution_label




