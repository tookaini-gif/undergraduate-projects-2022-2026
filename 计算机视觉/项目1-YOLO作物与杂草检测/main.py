import argparse
import json
from pathlib import Path
from export import export_results

def main():
    p = argparse.ArgumentParser(description='YOLO crop/weed training and inference')
    sub = p.add_subparsers(dest='mode', required=True)
    train = sub.add_parser('train')
    train.add_argument('--data', type=Path, default=Path('dataset.yaml'))
    train.add_argument('--weights', default='yolo11n.pt')
    train.add_argument('--epochs', type=int, default=60)
    train.add_argument('--batch', type=int, default=8)
    train.add_argument('--imgsz', type=int, default=640)
    train.add_argument('--device', default='cpu')
    predict = sub.add_parser('predict')
    predict.add_argument('--weights', type=Path, required=True)
    predict.add_argument('--source', type=Path, required=True)
    predict.add_argument('--output', type=Path, default=Path('outputs/detections.csv'))
    predict.add_argument('--conf', type=float, default=0.25)
    predict.add_argument('--save-images', action='store_true')
    args = p.parse_args()
    if args.mode == 'train':
        if not args.data.is_file(): p.error('dataset YAML not found')
        if min(args.epochs, args.batch, args.imgsz) < 1: p.error('training sizes must be positive')
    else:
        if not args.weights.is_file(): p.error('provide a locally trained checkpoint with weed=0, crop=1')
        if not args.source.exists(): p.error('source not found')
        if not 0 < args.conf <= 1: p.error('confidence must be in (0,1]')
    from ultralytics import YOLO
    model = YOLO(str(args.weights))
    if args.mode == 'train':
        model.train(data=str(args.data.resolve()), epochs=args.epochs, batch=args.batch,
                    imgsz=args.imgsz, device=args.device, project='outputs', name='train')
    else:
        actual = {int(k): v for k, v in model.names.items()} if isinstance(model.names, dict) else dict(enumerate(model.names))
        if actual != {0: 'weed', 1: 'crop'}: p.error('checkpoint class names must match dataset: 0=weed, 1=crop')
        results = model.predict(source=str(args.source), conf=args.conf, stream=True,
                                save=args.save_images, project='outputs', name='predict')
        print(json.dumps(export_results(results, args.output)))

if __name__ == '__main__': main()
