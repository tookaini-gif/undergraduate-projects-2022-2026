import argparse

def main():
    p=argparse.ArgumentParser(description='Probe camera indexes; devices are always released')
    p.add_argument('--limit',type=int,default=4);a=p.parse_args()
    if a.limit<1:p.error('limit must be positive')
    import cv2
    for index in range(a.limit):
        cap=cv2.VideoCapture(index)
        try:
            if cap.isOpened():
                ok,_=cap.read()
                print(f'Camera {index}: '+('ready' if ok else 'open, but no frame'))
        finally:cap.release()
if __name__=='__main__':main()
