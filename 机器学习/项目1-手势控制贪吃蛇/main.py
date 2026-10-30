import argparse
from pathlib import Path
from engine import GestureSnake
from hand_tracker import HandTracker

def main():
    p=argparse.ArgumentParser(description='Hand-controlled snake: R restart, Esc/Q exit')
    p.add_argument('--camera',type=int,default=0);p.add_argument('--model',type=Path,required=True)
    a=p.parse_args()
    if not a.model.is_file():p.error('hand_landmarker.task is missing; see README')
    import cv2
    cap=cv2.VideoCapture(a.camera)
    tracker=None
    try:
        if not cap.isOpened():raise RuntimeError('Camera unavailable; try camera_check.py in the tracking project')
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280);cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
        tracker=HandTracker(a.model);game=None
        while True:
            ok,frame=cap.read()
            if not ok:raise RuntimeError('Camera frame capture failed')
            frame=cv2.flip(frame,1);h,w=frame.shape[:2]
            if game is None:game=GestureSnake(w,h)
            landmarks=tracker.detect(frame)
            if landmarks:game.update(landmarks[8])
            for start,end in zip(game.points,game.points[1:]):cv2.line(frame,start,end,(70,205,170),14)
            if game.points:cv2.circle(frame,game.points[-1],10,(40,240,210),-1)
            cv2.circle(frame,game.food,16,(50,130,245),-1)
            label=f'Score: {game.score} | R restart | Esc exit'
            if game.over:label='GAME OVER | '+label
            if not landmarks:label='Show one hand | '+label
            cv2.putText(frame,label,(20,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(245,245,245),2)
            cv2.imshow('Gesture Snake',frame);key=cv2.waitKey(1)&0xff
            if key in (27,ord('q')):break
            if key==ord('r'):game.reset()
            if cv2.getWindowProperty('Gesture Snake',cv2.WND_PROP_VISIBLE)<1:break
    finally:
        if tracker:tracker.close()
        cap.release();cv2.destroyAllWindows()
if __name__=='__main__':main()
