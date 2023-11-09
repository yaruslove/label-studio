import hashlib
import secrets
import copy

class Lab_studio_main:
    def __init__(self):
        self.main={  'id': 0,
                     'annotations':[],
                     'drafts': [],
                     'predictions': [],
                     'data': {'image': '/data/local-files/?d=scripts/test_yolo_format/imgs/001_img.png'},
                     'meta': {},
                     'created_at': '2023-11-02T08:26:26.003600Z',
                     'updated_at': '2023-11-02T10:40:33.794656Z',
                     'inner_id': 1,
                     'total_annotations': 1,
                     'cancelled_annotations': 0,
                     'total_predictions': 0,
                     'comment_count': 0,
                     'unresolved_comment_count': 0,
                     'last_comment_updated_at': None,
                     'project': 30,
                     'updated_by': 1,
                     'comment_authors': []}

    def get_main(self, path_image):
        self.main["id"]=self.main["id"]+1
        self.main["data"]["image"] = path_image
        self.main["inner_id"] = self.main["inner_id"]+1

        # return self.main.copy()
        return copy.deepcopy(self.main)

class Annotation:
    def __init__ (self):
        self.anot={ "id" : 0,
        'result': [],
        "completed_by" : 1,
        "was_cancelled" : False,
        "ground_truth" : False,
        "created_at" : '2023-11-02T08:27:31.516935Z',
        "updated_at": '2023-11-02T10:40:33.779911Z',
        "draft_created_at": '2023-11-02T08:27:25.041385Z',
        "lead_time:":  1.0,
        "prediction":  {},
        "result_count":  0,
        "unique_id":  '5a63a12d-7f3e-4ef3-a84b-99c5263762c6',
        "import_id":  None,
        "last_action":  None,
        "task":  0,
        "project":  0,
        "updated_by":  1,
        "parent_prediction":  None,
        "parent_annotation":  None,
        "last_created_by":  None}

    def get_id_hash(self, n):
        return secrets.token_urlsafe(n)
        
    def hexdigest_hash(self, n):
        return hashlib.sha1(self.get_id_hash(n).encode("UTF-8")).hexdigest()[:n]
    
    def get_unique_id(self):
        return f"{self.hexdigest_hash(8)}-{self.hexdigest_hash(4)}-{self.hexdigest_hash(4)}-{self.hexdigest_hash(12)}"

    def get_annotation(self):
        self.anot["id"]=self.anot["id"]+1
        self.anot["unique_id"] = self.get_unique_id()
        self.anot["task"] = self.anot["task"] +1

        return copy.deepcopy(self.anot)


class Result:
    def __init__ (self):
        self.result={
            'original_width': 2704,
            'original_height': 1521,
            'image_rotation': 0,
            'value': {'points': [],
            'closed': True,
            'polygonlabels': ['leaf']},
            'id': '6O1Cl8I0jD',
            'from_name': 'label',
            'to_name': 'image',
            'type': 'polygonlabels',
            'origin': 'manual'}

    def get_id_hash(self, n):
        return secrets.token_urlsafe(n)[:n]
    
    def get_results(self, points, polygonlabels, resolution ):
        self.result["value"]["points"]=points
        self.result["value"]["polygonlabels"]=[polygonlabels]
        self.result["id"] = self.get_id_hash(10)
        self.result["original_height"] = resolution[0]
        self.result["original_width"] = resolution[1]
        return copy.deepcopy(self.result)


# Up-load model

from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor

sam_checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"

device = "cuda"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

mask_generator = SamAutomaticMaskGenerator(sam)


# prepared functions

import cv2 as cv

def mask2polygon(mask):
    mask=mask.astype("uint8")
    contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) # im2, contours, hierarchy
    contours = contours[0]
    
    # reduce amount point counturs
    peri = cv.arcLength(contours, True)
    eps = 0.006
    smother=eps*peri
    contours = cv.approxPolyDP(contours,smother, True)
    size = contours.shape[0]
    
    polygon = contours.reshape(size,2)
    
    return polygon

def polyg_relatived(polygon, resoution):
    polygon=np.float32(polygon)
    polygon[:,:1]=polygon[:,:1]/resoution[1]*100
    polygon[:,1:]=polygon[:,1:]/resoution[0]*100
    return polygon


def masks2listpolyg(masks):
    list_polygs=[]

    for mask in masks:
        mask = mask["segmentation"]

        polygon = mask2polygon(mask)

        # relative polyg
        h_res, w_res = mask.shape
        resoution = (h_res, w_res)
        polygon=polyg_relatived(polygon, resoution)
        polygon=[xi.tolist() for xi in polygon]


        list_polygs.append(polygon)
    return list_polygs


import os
import numpy as np

list_main_part=[]

pths_imgs = "/home/jovyan/tomato/data/selected/"
list_imgs=os.listdir(pths_imgs)
paths_images_LabelStudio="/data/local-files/?d=scripts/test_yolo_format/imgs/"

l=Lab_studio_main()
an = Annotation()
res = Result()

for pth_img in list_imgs:
    # json_1
    path_image_LabelStudio = os.path.join(paths_images_LabelStudio,pth_img)
    main_part=l.get_main(path_image_LabelStudio)
    anotation = an.get_annotation()
    
    full_pth = os.path.join(pths_imgs, pth_img)
    image = cv.imread(full_pth)
    
    masks = mask_generator.generate(image)
    list_polygs=masks2listpolyg(masks)
    
    # # relative polyg
    # h_res, w_res = mask.shape
    # resolution = (h_res, w_res)
    
    h_orig,w_orig,_=image.shape
    resolution_label = (h_orig,w_orig)
    
    for polyg in list_polygs:
        tmp_results = res.get_results(polyg, "leaf", resolution_label)
        anotation["result"].append(tmp_results)
    
    main_part["annotations"].append(anotation)
    list_main_part.append(main_part)



import json

with open('project_label_studio_many.json', 'w') as f:
    json.dump(list_main_part, f)