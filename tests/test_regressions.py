import csv
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]

def project(pattern): return next(p for p in ROOT.glob('*/*') if p.is_dir() and pattern in p.name)
def module(file,name):
    spec=importlib.util.spec_from_file_location(name,file);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

class CoreTests(unittest.TestCase):
    def test_textcnn_train_only_vocabulary_and_unknown(self):
        data=module(project('TextCNN')/'data.py','cnn_data_test')
        rows=[([f'label{label}_word{i}'],label) for label in (0,1) for i in range(8)]
        train,valid=data.split_rows(rows,seed=42)
        self.assertEqual((train,valid),data.split_rows(rows,seed=42))
        self.assertFalse({tuple(t) for t,_ in train}&{tuple(t) for t,_ in valid})
        vocab=data.build_vocab(train)
        for tokens,_ in valid:self.assertEqual(data.encode(tokens,vocab,5),[1,0,0,0,0])
        self.assertEqual(vocab['<PAD>'],0)

    def test_keyboard_snake_tail_move_and_reset(self):
        m=module(project('键盘贪吃蛇')/'engine.py','keyboard_test');g=m.Snake(seed=1)
        g.body=[(2,2),(2,3),(1,3),(1,2)];g.direction=(0,-1);g.food=(10,10)
        g.step((-1,0));self.assertFalse(g.over);self.assertEqual(g.body[0],(1,2))
        g.reset();self.assertEqual(g.score,0);self.assertFalse(g.over);self.assertNotIn(g.food,g.body)
        g.body=[(0,0),(1,0),(2,0)];g.direction=(-1,0);g.step();self.assertTrue(g.over)

    def test_keyboard_food_growth_and_reverse(self):
        m=module(project('键盘贪吃蛇')/'engine.py','keyboard_growth_test');g=m.Snake(seed=1)
        head=g.body[0];g.food=(head[0]+1,head[1]);g.step((-1,0))
        self.assertEqual(g.body[0],(head[0]+1,head[1]));self.assertEqual(g.score,10);self.assertEqual(len(g.body),4)

    def test_gesture_first_point_and_reset(self):
        m=module(project('手势控制')/'engine.py','gesture_test');g=m.GestureSnake(seed=1)
        g.update((400,300));self.assertEqual(g.length,0);self.assertFalse(g.over)
        g.food=(420,300);g.update((420,300));self.assertEqual(g.score,1)
        g.reset();self.assertEqual(g.points,[]);self.assertEqual(g.score,0)
        self.assertAlmostEqual(m.distance_to_segment((5,3),(0,0),(10,0)),3)

    def test_gesture_trim_and_real_collision(self):
        m=module(project('手势控制')/'engine.py','gesture_collision_test');g=m.GestureSnake(seed=7)
        g.food=(900,600)
        for x in range(100,500,10):g.update((x,100))
        self.assertLessEqual(g.length,g.allowed);self.assertEqual(len(g.lengths),len(g.points)-1)
        g.reset();g.allowed=1000;g.food=(900,600)
        for point in [(100,100),(200,100),(200,200),(100,200),(100,105)]:g.update(point)
        self.assertTrue(g.over)

    def test_yolo_empty_export_and_class_order(self):
        m=module(project('YOLO')/'export.py','yolo_export_test')
        class Scalar:
            def __init__(self,v):self.v=v
            def item(self):return self.v
        class Values:
            def tolist(self):return [1.234,2.345,11.239,22.349]
        class Box:
            cls=Scalar(0);xyxy=[Values()]
        class Result:
            def __init__(self,name,boxes):self.path=name;self.boxes=boxes
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'empty.csv';stats=m.export_results([Result('a.jpg',[])],path)
            self.assertEqual(list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8')))),[]);self.assertEqual(stats['total_images'],1)
            stats=m.export_results([Result('a.jpg',[Box()]),Result('b.jpg',[])],path)
            rows=list(csv.DictReader(io.StringIO(path.read_text(encoding='utf-8'))))
            self.assertEqual(stats['weed_count'],1);self.assertEqual(stats['crop_count'],0)
            self.assertEqual(stats['total_images'],2);self.assertEqual(stats['images_with_detections'],1)
            self.assertEqual(rows[0]['width'],'10.01')

    def test_research_adapter_requires_real_backend(self):
        m=module(project('空间基因')/'model_wrapper.py','research_wrapper_test')
        with patch.dict(os.environ,{'STFLOW_BACKEND':''}):
            with self.assertRaises(m.ModelUnavailable):m.GenePredictor()
        predictor=object.__new__(m.GenePredictor)
        class Backend:
            def predict(self,img,genes):return {'wrong_gene':1.}
        predictor.backend=Backend()
        with self.assertRaises(ValueError):predictor.predict(None,['EGFR'])

class ResearchApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=project('空间基因');sys.path.insert(0,str(cls.base))
        try:
            import python_multipart
            from fastapi.testclient import TestClient
            cls.api=module(cls.base/'main.py','research_api_test');cls.client=TestClient(cls.api.app)
        except ImportError:raise unittest.SkipTest('Install FastAPI, Pillow, multipart and httpx for API tests')
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'client'):cls.client.close()
        sys.path.remove(str(cls.base))
    def test_health_and_missing_model(self):
        from PIL import Image
        self.api.get_predictor.cache_clear()
        with patch.dict(os.environ,{'STFLOW_BACKEND':''}):
            self.assertFalse(self.client.get('/health').json()['model_ready'])
            image=io.BytesIO();Image.new('RGB',(8,8)).save(image,format='PNG')
            r=self.client.post('/predict',files={'image':('sample.png',image.getvalue(),'image/png')},data={'genes':'EGFR'})
            self.assertEqual(r.status_code,503);self.assertNotIn('heatmap',r.json())
    def test_invalid_image_and_duplicate_genes(self):
        self.assertEqual(self.client.post('/predict',files={'image':('x.png',b'not image')}).status_code,400)
        self.assertEqual(self.client.post('/predict',files={'image':('x.png',b'no')},data={'genes':'EGFR,EGFR'}).status_code,400)
    def test_injected_backend_response_contract(self):
        from PIL import Image
        class TestBackend:
            def predict(self,img,genes):return {gene:float(i+1) for i,gene in enumerate(genes)}
        image=io.BytesIO();Image.new('RGB',(8,8)).save(image,format='PNG')
        # This fixture tests HTTP serialization only; values are not model evaluations.
        with patch.object(self.api,'get_predictor',return_value=TestBackend()):
            r=self.client.post('/predict',files={'image':('sample.png',image.getvalue())},data={'genes':'EGFR,CD3D'})
        self.assertEqual(r.status_code,200);self.assertEqual(r.json()['predictions'],{'EGFR':1.,'CD3D':2.})
        self.assertFalse(r.json()['spatial_map_available'])

if __name__=='__main__':unittest.main()
