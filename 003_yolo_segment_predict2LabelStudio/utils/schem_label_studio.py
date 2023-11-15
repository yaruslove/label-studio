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
