"""Dataset preparation with a training-only vocabulary and deterministic split."""
from collections import Counter
from pathlib import Path
import random
import string

def tokenize(text):
    return text.lower().translate(str.maketrans('', '', string.punctuation)).split()

def load_rows(directory):
    rows = []
    for label, suffix in [(0, 'neg'), (1, 'pos')]:
        path = Path(directory) / f'rt-polarity.{suffix}'
        for line in path.read_text(encoding='cp1252').splitlines():
            if line.strip(): rows.append((tokenize(line), label))
    return rows

def split_rows(rows, fraction=0.7, seed=42):
    if not 0 < fraction < 1: raise ValueError('fraction must be between zero and one')
    rng = random.Random(seed); train, valid = [], []
    for label in (0, 1):
        group = [r for r in rows if r[1] == label]
        if len(group) < 2: raise ValueError('At least two examples per class are required')
        rng.shuffle(group)
        cut = min(len(group)-1, max(1, int(len(group)*fraction)))
        train.extend(group[:cut]); valid.extend(group[cut:])
    rng.shuffle(train); rng.shuffle(valid)
    return train, valid

def build_vocab(rows):
    words = Counter(word for tokens, _ in rows for word in tokens)
    vocab = {'<PAD>': 0, '<UNK>': 1}
    for word, _ in sorted(words.items(), key=lambda x: (-x[1], x[0])):
        if word not in vocab: vocab[word] = len(vocab)
    return vocab

def encode(tokens, vocab, length):
    ids = [vocab.get(word, 1) for word in tokens[:length]]
    return ids + [0] * (length - len(ids))
