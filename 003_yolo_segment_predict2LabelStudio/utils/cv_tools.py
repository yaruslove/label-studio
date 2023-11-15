import cv2 as cv
import numpy as np
import torch

def mask2polygon(mask):
    mask=mask.astype("uint8")
    contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) # im2, contours, hierarchy
    if len(contours)==0:
        return 0
    contours = contours[0]
    
    ### reduce amount point counturs
    peri = cv.arcLength(contours, True)
    eps = 0.006
    smother=eps*peri
    contours = cv.approxPolyDP(contours,smother, True)
    
    size = contours.shape[0]
    polygon = contours.reshape(size,2)
    return polygon

def polyg_relatived(polygon, resolution):
    polygon=np.float32(polygon)
    polygon[:,:1]=polygon[:,:1]/resolution[1]*100
    polygon[:,1:]=polygon[:,1:]/resolution[0]*100
    polygon=[xi.tolist() for xi in polygon]
    return polygon

def get_mask_byID(result, idx):
    mask_np=result.masks.to().data[idx]
    mask_np=mask_np.cpu().detach().numpy()
    return mask_np

def resize_mask(mask_np, result):
    ## Get image size to resize mask back
    orig_h,orig_w=result.orig_shape
    size_orig=(orig_w,orig_h)

    ### Resize mask to initiale image size
    mask_np = cv.resize(mask_np, size_orig, interpolation = cv.INTER_AREA)
    return mask_np


def first_not_zero(zero_np):
    zero_np_sumed = zero_np.sum(axis=1) 
    zero_np_sumed
    return (zero_np_sumed !=0).argmax()

def last_not_zero(zero_np):
    zero_np_sumed = zero_np.sum(axis=1) 
    zero_np_sumed
    return np.max(np.nonzero(zero_np_sumed))

def slice_non_zero(masks):
    h,w=int(masks[0].shape[0]), int(masks[0].shape[1])
    zero=torch.zeros(h, w)
    for m in masks:
        zero=zero+m
    zero_np = zero.numpy()
    
    fnz=first_not_zero(zero_np)
    lnz=last_not_zero(zero_np)
    return (fnz,lnz)
