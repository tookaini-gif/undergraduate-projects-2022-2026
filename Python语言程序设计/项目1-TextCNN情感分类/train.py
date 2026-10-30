"""Train and evaluate TextCNN. No data download or training occurs on import."""
import argparse
import json
from pathlib import Path
import random
from data import load_rows, split_rows, build_vocab, encode

def make_model(vocab_size, embedding_dim=40):
    import torch
    from torch import nn
    class TextCNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
            self.convs = nn.ModuleList([nn.Conv1d(embedding_dim, 64, k) for k in (3, 4, 5)])
            self.dropout = nn.Dropout(0.5)
            self.fc = nn.Linear(192, 2)
        def forward(self, x):
            x = self.embedding(x).transpose(1, 2)
            pooled = [torch.relu(conv(x)).amax(dim=2) for conv in self.convs]
            return self.fc(self.dropout(torch.cat(pooled, dim=1)))
    return TextCNN()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--epochs', type=int, default=8)
    parser.add_argument('--batch-size', type=int, default=16)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto')
    parser.add_argument('--output', type=Path, default=Path('outputs/textcnn.pt'))
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1: parser.error('epochs and batch size must be positive')
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset
    torch.manual_seed(args.seed); random.seed(args.seed)
    device = ('cuda' if torch.cuda.is_available() else 'cpu') if args.device == 'auto' else args.device
    train_rows, valid_rows = split_rows(load_rows(args.data_dir), seed=args.seed)
    vocab = build_vocab(train_rows)
    length = max(5, min(256, max(len(words) for words, _ in train_rows)))
    def dataset(rows):
        return TensorDataset(torch.tensor([encode(t, vocab, length) for t, _ in rows], dtype=torch.long),
                             torch.tensor([label for _, label in rows], dtype=torch.long))
    generator = torch.Generator().manual_seed(args.seed)
    loader = DataLoader(dataset(train_rows), batch_size=args.batch_size, shuffle=True, generator=generator)
    valid_loader = DataLoader(dataset(valid_rows), batch_size=args.batch_size)
    model = make_model(len(vocab)).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=3e-5)
    criterion = nn.CrossEntropyLoss()
    for epoch in range(args.epochs):
        model.train(); loss_total = 0
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad(); loss = criterion(model(x), y); loss.backward(); optimizer.step()
            loss_total += loss.item()*len(y)
        print(json.dumps({'epoch': epoch+1, 'train_loss': loss_total/len(train_rows)}))
    model.eval(); correct = 0
    with torch.inference_mode():
        for x, y in valid_loader: correct += (model(x.to(device)).argmax(1).cpu() == y).sum().item()
    metrics = {'validation_accuracy': correct/len(valid_rows), 'train_rows': len(train_rows),
               'validation_rows': len(valid_rows), 'seed': args.seed, 'device': device}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({'state_dict': model.state_dict(), 'vocab': vocab, 'length': length, 'embedding_dim': 40, 'metrics': metrics}, args.output)
    args.output.with_suffix('.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
    print(json.dumps(metrics))

if __name__ == '__main__': main()
