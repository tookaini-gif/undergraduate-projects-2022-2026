import os
import string
import random
import tarfile
import urllib.request
from torch.utils.data import Dataset, DataLoader
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from tqdm import tqdm
import time


# 下载数据
def download_data():
    url = "https://www.cs.cornell.edu/people/pabo/movie-review-data/rt-polaritydata.tar.gz"
    filename = "rt-polaritydata.tar.gz"

    if not os.path.exists('./rt-polaritydata/'):
        print("下载数据...")
        urllib.request.urlretrieve(url, filename)

        # 解压文件
        with tarfile.open(filename, 'r:gz') as tar:
            tar.extractall('./')

        os.remove(filename)
        print("数据下载完成!")


download_data()


# 数据集类
class PolarityData(Dataset):
    def __init__(self, path):
        self.feelMap = {'neg': 0, 'pos': 1}
        self.path = path
        self.vec_set = []
        self.max_len = 0
        self.vocab = dict()

        self._load()

    def _load(self):
        files = os.listdir(self.path)
        sentences_list = []

        for file in files:
            file_name = os.path.join(self.path, file)
            with open(file_name, 'r', encoding='Windows-1252') as f:
                for line in f.readlines():
                    # 预处理
                    words = line.rstrip().translate(str.maketrans('', '', string.punctuation)).lower().split()
                    if 'pos' in file:
                        sentences_list.append([words, self.feelMap['pos']])
                    else:
                        sentences_list.append([words, self.feelMap['neg']])

                    self.max_len = max(self.max_len, len(words))

        # 构建词汇表
        for words, label in sentences_list:
            vectors = [0] * self.max_len
            for idx, word in enumerate(words):
                if idx >= self.max_len:
                    break
                if word not in self.vocab:
                    self.vocab[word] = len(self.vocab) + 1
                vectors[idx] = self.vocab[word]

            self.vec_set.append((vectors, label))

        random.shuffle(self.vec_set)

    def get_len(self):
        return self.vocab, len(self.vocab), self.max_len

    def __len__(self):
        return len(self.vec_set)

    def __getitem__(self, idx):
        vectors, label = self.vec_set[idx]
        return torch.tensor(vectors, dtype=torch.long), torch.tensor(label, dtype=torch.long)


# TextCNN模型
class TextCNN(nn.Module):
    def __init__(self, vocab_len, word_len, num_classes, vec_length):
        super(TextCNN, self).__init__()
        self.vec_length = vec_length
        self.word_len = word_len
        self.num_classes = num_classes

        # Embedding层
        self.embedding = nn.Embedding(vocab_len + 1, vec_length)

        # 卷积层
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 64, (3, vec_length), padding=(1, 0)),
            nn.ReLU(),
            nn.AdaptiveMaxPool2d((1, 1))
        )

        self.conv2 = nn.Sequential(
            nn.Conv2d(1, 64, (4, vec_length), padding=(1, 0)),
            nn.ReLU(),
            nn.AdaptiveMaxPool2d((1, 1))
        )

        self.conv3 = nn.Sequential(
            nn.Conv2d(1, 64, (5, vec_length), padding=(1, 0)),
            nn.ReLU(),
            nn.AdaptiveMaxPool2d((1, 1))
        )

        # 全连接层
        self.fc = nn.Linear(64 * 3, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        # x: (batch_size, word_len)
        x = self.embedding(x)  # (batch_size, word_len, vec_length)
        x = x.unsqueeze(1)  # (batch_size, 1, word_len, vec_length)

        # 三个卷积分支
        x1 = self.conv1(x)  # (batch_size, 64, 1, 1)
        x2 = self.conv2(x)  # (batch_size, 64, 1, 1)
        x3 = self.conv3(x)  # (batch_size, 64, 1, 1)

        # 展平
        x1 = x1.view(x1.size(0), -1)  # (batch_size, 64)
        x2 = x2.view(x2.size(0), -1)  # (batch_size, 64)
        x3 = x3.view(x3.size(0), -1)  # (batch_size, 64)

        # 拼接
        x = torch.cat((x1, x2, x3), dim=1)  # (batch_size, 192)
        x = self.dropout(x)
        x = self.fc(x)  # (batch_size, num_classes)
        return x


# 训练函数
def train_model():
    # 参数设置
    data_path = './rt-polaritydata/'
    batch_size = 16
    epoch_size = 8
    vec_length = 40
    num_classes = 2

    # 创建数据集
    dataset = PolarityData(data_path)
    vocab, vocab_size, word_len = dataset.get_len()

    # 分割数据集
    train_size = int(0.7 * len(dataset))
    valid_size = len(dataset) - train_size
    train_dataset, valid_dataset = torch.utils.data.random_split(dataset, [train_size, valid_size])

    # 创建数据加载器
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    valid_loader = DataLoader(valid_dataset, batch_size=1, shuffle=False, drop_last=True)

    # 模型实例化
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")

    net = TextCNN(vocab_len=vocab_size, word_len=word_len,
                  num_classes=num_classes, vec_length=vec_length).to(device)

    # 优化器和损失函数
    optimizer = optim.Adam(net.parameters(), lr=0.001, weight_decay=3e-5)
    criterion = nn.CrossEntropyLoss()

    # 训练循环
    print("开始训练!")
    step_num = len(train_loader)

    for epoch in range(epoch_size):
        net.train()
        total_loss = 0
        start_time = time.time()

        for i, (data, labels) in enumerate(train_loader):
            data, labels = data.to(device), labels.to(device)

            # 前向传播
            outputs = net(data)
            loss = criterion(outputs, labels)

            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

            if i % 20 == 0:
                print(f'Epoch:[{epoch + 1:>3d}/{epoch_size:>3d}], '
                      f'step:[{i:>4d}/{step_num:>4d}], '
                      f'loss:{loss.item():>6f}')

        epoch_time = time.time() - start_time
        avg_loss = total_loss / step_num
        print(f'Epoch {epoch + 1} 完成, 平均loss: {avg_loss:.4f}, 用时: {epoch_time:.2f}s')

        # 保存模型
        if (epoch + 1) % 2 == 0:
            torch.save(net.state_dict(), f'./textcnn_{epoch + 1}.pth')

    print("训练结束!")

    # 验证模型
    net.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for data, labels in valid_loader:
            data, labels = data.to(device), labels.to(device)
            outputs = net(data)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    print(f'验证准确率: {accuracy:.2f}%')

    return net, vocab, word_len


# 预测函数
def predict(model, vocab, word_len, sentence, device):
    model.eval()

    # 预处理
    words = sentence.rstrip().translate(str.maketrans('', '', string.punctuation)).lower().split()
    vectors = [0] * word_len

    for idx, word in enumerate(words):
        if idx >= word_len:
            break
        if word in vocab:
            vectors[idx] = vocab[word]

    # 预测
    with torch.no_grad():
        input_tensor = torch.tensor([vectors], dtype=torch.long).to(device)
        output = model(input_tensor)
        prediction = torch.argmax(output, dim=1).item()

    sentiment = "Positive!" if prediction == 1 else "Negative"
    print(f"句子: '{sentence}' → 情感: {sentiment}")
    return prediction


# 主函数
if __name__ == "__main__":
    # 训练模型
    net, vocab, word_len = train_model()

    # 测试预测
    device = next(net.parameters()).device

    test_sentences = [
        'This is a film well worth seeing .',
        'On its own , it is not very interesting .',
        'I love this movie!',
        'This is terrible.'
    ]

    print("\n预测测试:")
    for sentence in test_sentences:
        predict(net, vocab, word_len, sentence, device)