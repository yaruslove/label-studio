import os
import cv2
import numpy as np
import yaml
from ultralytics import YOLO

from utils.schem_label_studio import Lab_studio_main, Annotation, Result
from utils.cv_tools import mask2polygon, polyg_relatived, get_mask_byID, resize_mask, slice_non_zero



def read_yaml():
    with open('config.yaml') as fh:
        read_data = yaml.load(fh, Loader=yaml.FullLoader)
    return read_data

class YoloSeg2LabelStudio:
    def __init__(self, weight_model, labelst_part_path):
        self.model = YOLO(weight_model)
        self.classes = self.model.names
        # self.labelst_part_path = "/data/local-files/?d=data/001_raw_data/001_video_data/002_GO_PRO_SBER_20231101_ALL/selected_imgs/"
        self.labelst_part_path = labelst_part_path

    def get_labels(self, pth_imgs):

        l=Lab_studio_main()
        an = Annotation()
        res = Result()
        list_main_part = []
        
        for pth_img in os.listdir(pth_imgs):
            if pth_img!="GX010038_17.jpg":
                continue
            labelst_path = os.path.join(self.labelst_part_path, pth_img)
            pth_img_ful = os.path.join(pth_imgs,pth_img)
            image = cv2.imread(pth_img_ful)
            h_orig,w_orig,_=image.shape
            resolution_label = (h_orig,w_orig)

            # Label studio json schema
            main_part=l.get_main(labelst_path)
            anotation = an.get_annotation()

            # inference model # TODO be attentive about retina_masks=True 
            retina_masks=True 
            result=self.model(image, iou=0.35, conf=0.2, retina_masks=retina_masks )[0] # retina_masks=True

            # There are paddind, therefore we need to crop it
            if retina_masks==False: 
                fnz,lnz =slice_non_zero(result.masks.data) # # TODO uncoment insted prevuios string
                # fnz,lnz =  12,371 #  slice_non_zero(result.masks.data) # TODO check
                val_crop=(fnz,lnz)
                print(f"val_crop {val_crop}")
            

            amount_masks=len(result.masks.data)

            for idx_mask, cls in zip(range(amount_masks), result.boxes.cls):
                cls=int(cls)
                # val_crop attribute => crop slice because of padding
                mask_np=get_mask_byID(result, idx_mask)

                # TODO del because of padding
                if not retina_masks:   # fnz,lnz = val_crop
                    mask_np = mask_np[fnz:lnz,:]

                mask_np = resize_mask(mask_np, result)
                
                polyg = mask2polygon(mask_np)
                # print(type(polyg))
                if not type(polyg) == np.ndarray:
                    continue
                    
                polyg=polyg_relatived(polyg, resolution_label)
                # Fill json schema 
                tmp_results = res.get_results(polyg, self.classes[cls], resolution_label)
                anotation["result"].append(tmp_results)
            main_part["annotations"].append(anotation)
            list_main_part.append(main_part)
        return list_main_part