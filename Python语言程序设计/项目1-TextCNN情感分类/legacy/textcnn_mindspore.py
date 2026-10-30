import os
import string
import random
import numpy as np
import mindspore.dataset as ds
import mindspore as ms
from mindspore import nn, ops, Tensor
from mindspore import save_checkpoint, load_checkpoint, load_param_into_net
import time
from download import download


# ==================== 修改部分开始 ====================
# 修复：添加数据下载功能，确保数据存在
def download_data():
    """下载数据集"""
    url = "https://www.cs.cornell.edu/people/pabo/movie-review-data/rt-polaritydata.tar.gz"
    if not os.path.exists('./rt-polaritydata/'):
        print("下载数据...")
        download(url, "./", kind="tar.gz", replace=True)
        print("数据下载完成!")


# ==================== 修改部分结束 ====================

download_data()


class PolarityData:
    def __init__(self, path):
        self.feelMap = {'neg': 0, 'pos': 1}
        self.path = path
        self.vec_set = []
        self.max_len = 0
        self.vocab = dict()

        self.data = self._load()

    def _load(self):
        file = os.listdir(self.path)
        a = []
        for e in file:
            file_name = os.path.join(self.path, e)
            with open(file_name, 'r', encoding='Windows-1252') as sentences_set:
                for sentences in sentences_set.readlines():
                    sentences = sentences.rstrip().translate(str.maketrans('', '', string.punctuation)).lower().split()
                    if 'pos' in file_name:
                        a.append([sentences, self.feelMap['pos']])
                    else:
                        a.append([sentences, self.feelMap['neg']])

                    self.max_len = self.max_len if self.max_len >= len(sentences) else len(sentences)

        for sentences1 in a:
            vectors = [0] * self.max_len
            for index, word in enumerate(sentences1[0]):
                if index >= self.max_len:
                    break
                if word not in self.vocab.keys():
                    self.vocab[word] = len(self.vocab) + 1
                    vectors[index] = len(self.vocab)
                else:
                    vectors[index] = self.vocab[word]

            self.vec_set.append([vectors, sentences1[1]])

        random.shuffle(self.vec_set)
        return self.vec_set

    def get_len(self):
        return self.vocab, len(self.vocab), self.max_len

    def __getitem__(self, item):
        return (np.array(self.data[item][0], dtype=np.int32),
                np.array(self.data[item][1], dtype=np.int32))

    def __len__(self):
        return len(self.vec_set)


# ==================== 修改部分开始 ====================
# 修复：重新设计TextCNN模型结构，修正卷积和池化层
class TextCNN(nn.Cell):
    def __init__(self, vocab_len, word_len, num_classes, vec_length):
        super(TextCNN, self).__init__()
        self.vec_length = vec_length
        self.word_len = word_len
        self.num_classes = num_classes

        # Embedding层
        self.embedding = nn.Embedding(vocab_len + 1, self.vec_length, embedding_table='normal')

        # 三个不同kernel size的卷积层
        self.conv1 = nn.SequentialCell([
            nn.Conv2d(1, 64, (3, vec_length), padding=(1, 0), pad_mode='pad', has_bias=True),
            nn.ReLU(),
            nn.AdaptiveMaxPool2d((1, 1))
        ])

        self.conv2 = nn.SequentialCell([
            nn.Conv2d(1, 64, (4, vec_length), padding=(1, 0), pad_mode='pad', has_bias=True),
            nn.ReLU(),
            nn.AdaptiveMaxPool2d((1, 1))
        ])

        self.conv3 = nn.SequentialCell([
            nn.Conv2d(1, 64, (5, vec_length), padding=(1, 0), pad_mode='pad', has_bias=True),
            nn.ReLU(),
            nn.AdaptiveMaxPool2d((1, 1))
        ])

        # 全连接层
        self.fc = nn.Dense(64 * 3, self.num_classes)
        self.dropout = nn.Dropout(keep_prob=0.5)
        self.reshape = ops.Reshape()
        self.concat = ops.Concat(axis=1)

    def construct(self, x):
        # x: (batch_size, word_len)
        x = self.embedding(x)  # (batch_size, word_len, vec_length)
        x = x.expand_dims(1)  # (batch_size, 1, word_len, vec_length)

        # 三个卷积分支
        x1 = self.conv1(x)  # (batch_size, 64, 1, 1)
        x2 = self.conv2(x)  # (batch_size, 64, 1, 1)
        x3 = self.conv3(x)  # (batch_size, 64, 1, 1)

        # 展平
        x1 = self.reshape(x1, (x1.shape[0], -1))  # (batch_size, 64)
        x2 = self.reshape(x2, (x2.shape[0], -1))  # (batch_size, 64)
        x3 = self.reshape(x3, (x3.shape[0], -1))  # (batch_size, 64)

        # 拼接
        x = self.concat((x1, x2, x3))  # (batch_size, 192)
        x = self.dropout(x)
        x = self.fc(x)  # (batch_size, num_classes)
        return x


# ==================== 修改部分结束 ====================

# 数据预处理和加载
data_path = './rt-polaritydata/'
batch_size = 16
epoch_size = 8
vec_length = 40
num_classes = 2

dataset = ds.GeneratorDataset(source=PolarityData(path=data_path),
                              column_names=["data", "label"],
                              shuffle=False)

# 分训练和验证数据集
dataset_train, dataset_valid = dataset.split([0.7, 0.3])
valid_size = dataset_valid.get_dataset_size()

dataset_train = dataset_train.batch(batch_size=batch_size, drop_remainder=True)
dataset_valid = dataset_valid.batch(batch_size=1, drop_remainder=True)
step_num = dataset_train.get_dataset_size()
vocab, vocab_size, word_len = PolarityData(path=data_path).get_len()

# ==================== 修改部分开始 ====================
# 修复：优化学习率策略和优化器配置
# 学习率配置
total_steps = epoch_size * step_num
warmup_steps = int(total_steps * 0.1)


def lr_scheduler(current_step):
    if current_step < warmup_steps:
        return 0.001 * (current_step + 1) / warmup_steps
    else:
        return 0.001


learning_rate = [lr_scheduler(i) for i in range(total_steps)]

# 模型实例化
net = TextCNN(vocab_len=vocab_size, word_len=word_len,
              num_classes=num_classes, vec_length=vec_length)

# 优化器
opt = nn.Adam(net.trainable_params(), learning_rate=learning_rate, weight_decay=3e-5)

# 损失函数 - 修复：使用正确的损失函数
loss = nn.SoftmaxCrossEntropyWithLogits(sparse=True, reduction='mean')
# ==================== 修改部分结束 ====================

# 训练过程
from mindspore import context

context.set_context(mode=context.PYNATIVE_MODE, device_target='Ascend', device_id=0)


# 前向计算
def forward_fn(data, label):
    logits = net(data)
    loss_val = loss(logits, label)
    return loss_val


grad_fn = ms.value_and_grad(forward_fn, None, net.trainable_params())


# 训练步骤
def train_step(data, label):
    loss_val, grads = grad_fn(data, label)
    opt(grads)
    return loss_val


print("开始训练!")
for epoch in range(epoch_size):
    start = time.time()
    total_loss = 0

    for i, batch in enumerate(dataset_train.create_dict_iterator()):
        data = batch['data']
        label = batch['label']

        loss_val = train_step(data, label)
        total_loss += loss_val.asnumpy()

        if i % 20 == 0:
            print(f"Epoch:[{int(epoch + 1):>3d}/{int(epoch_size):>3d}], "
                  f"step:[{int(i):>4d}/{int(step_num):>4d}], "
                  f"loss:{loss_val.asnumpy():>6f}")

    epoch_time = time.time() - start
    avg_loss = total_loss / step_num
    print(f"Epoch {epoch + 1} 完成, 平均loss: {avg_loss:.4f}, 用时: {epoch_time:.2f}s")

    # 保存模型
    if (epoch + 1) % 2 == 0:
        save_checkpoint(net, f"./textcnn_{epoch + 1}.ckpt")

print("训练结束!")


# ==================== 修改部分开始 ====================
# 修复：改进验证过程，使用更准确的评估方法
def evaluate_model():
    """评估模型准确率"""
    test_ckpt = './textcnn_8.ckpt'
    parameter = load_checkpoint(test_ckpt)
    load_param_into_net(net, parameter)

    correct = 0
    total = 0

    for batch in dataset_valid.create_dict_iterator():
        data = batch['data']
        label = batch['label']

        output = net(data)
        predicted = np.argmax(output.asnumpy(), axis=1)
        true_label = label.asnumpy()

        correct += np.sum(predicted == true_label)
        total += len(true_label)

    accuracy = correct / total
    print(f"验证准确率: {accuracy:.4f} ({correct}/{total})")
    return accuracy


# 运行验证
accuracy = evaluate_model()


# ==================== 修改部分结束 ====================

# 预测函数
def predict(sentence):
    """预测单个句子的情感"""
    # 预处理
    words = sentence.rstrip().translate(str.maketrans('', '', string.punctuation)).lower().split()
    vectors = [0] * word_len

    for idx, word in enumerate(words):
        if idx >= word_len:
            break
        if word in vocab:
            vectors[idx] = vocab[word]

    # 预测
    input_tensor = Tensor([vectors], dtype=ms.int32)
    output = net(input_tensor)
    prediction = np.argmax(output.asnumpy(), axis=1)[0]

    sentiment = "Positive!" if prediction == 1 else "Negative"
    print(f"句子: '{sentence}' → 情感: {sentiment}")
    return prediction


# 测试预测
print("\n预测测试:")
test_sentences = [
    'This is a film well worth seeing .',
    'On its own , it is not very interesting .',
    'I love this movie!',
    'This is terrible.'
]

for sentence in test_sentences:
    predict(sentence)