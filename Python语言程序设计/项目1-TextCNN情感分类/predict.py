import argparse
from pathlib import Path
from data import tokenize, encode
from train import make_model

def main():
    p = argparse.ArgumentParser(description='Predict sentiment using a locally trained checkpoint')
    p.add_argument('--checkpoint', type=Path, required=True)
    p.add_argument('--text', required=True)
    a = p.parse_args()
    import torch
    checkpoint = torch.load(a.checkpoint, map_location='cpu', weights_only=True)
    model = make_model(len(checkpoint['vocab']), checkpoint['embedding_dim'])
    model.load_state_dict(checkpoint['state_dict']); model.eval()
    x = torch.tensor([encode(tokenize(a.text), checkpoint['vocab'], checkpoint['length'])])
    with torch.inference_mode(): label = model(x).argmax(1).item()
    print('positive' if label else 'negative')

if __name__ == '__main__': main()
