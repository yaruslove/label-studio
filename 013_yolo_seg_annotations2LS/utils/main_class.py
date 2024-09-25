import os
import cv2
import numpy as np
import yaml
import glob
# from ultralytics import YOLO

from utils.schem_label_studio import Lab_studio_main, Annotation, Result

from utils.cv_tools import iter_items, get_resolution



def read_yaml():
    with open('config.yaml') as fh:
        read_data = yaml.load(fh, Loader=yaml.FullLoader)
    return read_data


class YoloSeg2LabelStudio:
    def __init__(self):
        self.classes = ["leaf", "stems", "tomato", "death_leaf"]

    def get_labels(self, path_labels, path_images, labelst_part_path):
        self.list_labels = glob.glob(f"{path_labels}/*.txt")
        self.list_images = glob.glob(f"{path_images}/*.jpg")  # TODO make another extensions png PNG jepeg

        l=Lab_studio_main()
        an = Annotation()
        res = Result()
        list_main_part = []
        
        for label_path, path_img in zip(self.list_labels, self.list_images):
            ## Init
            labelst_path = os.path.join(labelst_part_path, os.path.basename(path_img))
            main_part=l.get_main(labelst_path)
            anotation = an.get_annotation()


            ## Main part
            list_polyg, list_clas = iter_items(label_path)
            resolution_label = get_resolution(path_img)

            list_polyg=[xi.tolist() for xi in list_polyg]

            for polyg, anot_clas in zip(list_polyg, list_clas):
                tmp_results = res.get_results(polyg, self.classes[anot_clas], resolution_label)
                anotation["result"].append(tmp_results)
            main_part["annotations"].append(anotation)
            list_main_part.append(main_part)

        return list_main_part
