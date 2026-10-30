import argparse
from pathlib import Path
import time
from hand_tracker import HandTracker
CONNECTIONS=[(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(0,17),(17,18),(18,19),(19,20)]

def main():
    p=argparse.ArgumentParser(description='Hand landmark visualization: Esc/Q exit')
    p.add_argument('--camera',type=int,default=0);p.add_argument('--model',type=Path,required=True);a=p.parse_args()
    if not a.model.is_file():p.error('hand_landmarker.task is missing; see README')
    import cv2
    cap=cv2.VideoCapture(a.camera);tracker=None;previous=time.perf_counter()
    try:
        if not cap.isOpened():raise RuntimeError('Camera unavailable')
        tracker=HandTracker(a.model)
        while True:
            ok,frame=cap.read()
            if not ok:raise RuntimeError('Camera frame capture failed')
            frame=cv2.flip(frame,1);points=tracker.detect(frame)
            if points:
                for start,end in CONNECTIONS:cv2.line(frame,points[start],points[end],(30,200,170),2)
                for point in points:cv2.circle(frame,point,4,(30,130,250),-1)
                cv2.putText(frame,f'Index fingertip: {points[8]}',(15,65),cv2.FONT_HERSHEY_SIMPLEX,0.7,(240,240,240),2)
            current=time.perf_counter();fps=1/max(current-previous,1e-6);previous=current
            cv2.putText(frame,f'{fps:.0f} FPS | Esc/Q exit',(15,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(240,240,240),2)
            cv2.imshow('Hand Landmarks',frame);key=cv2.waitKey(1)&0xff
            if key in (27,ord('q')):break
            if cv2.getWindowProperty('Hand Landmarks',cv2.WND_PROP_VISIBLE)<1:break
    finally:
        if tracker:tracker.close()
        cap.release();cv2.destroyAllWindows()
if __name__=='__main__':main()
