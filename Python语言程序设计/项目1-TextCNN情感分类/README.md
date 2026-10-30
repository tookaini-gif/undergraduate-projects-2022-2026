# TextCNN情感分类

用卷积神经网络对英文电影短评进行二分类，并保留两种框架的学习轨迹。

> 技术栈：Python / PyTorch / MindSpore  
> 验证范围：数据划分回归通过；合成样本训练、保存和重新加载通过；完整语料训练未复现

## 项目内容

发布版提供训练集专用词表、固定随机种子、独立验证、保存词表与参数的检查点。原 MindSpore 版本保留在 legacy 中，仅作为待适配的实验版本；不包含旧权重或整份数据集。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
python -m pip install -r requirements.txt
python train.py --data-dir path/to/rt-polaritydata --epochs 8
```

## 文件导航

- `data.py`
- `DATASET_LICENSE.txt`
- `legacy/`：原始学习版本与草稿（不作为验证入口）
- `predict.py`
- `requirements.txt`
- `train.py`

## 来源与整理边界

tooka/pythonProject/classword.py 与 xg.py；发布版训练流程经整理重构。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)

## 数据与评估

从 [Cornell Movie Review Data](https://www.cs.cornell.edu/people/pabo/movie-review-data/) 取得 RT polarity 数据并遵守数据说明。`--data-dir` 内应有 `rt-polarity.pos` 与 `rt-polarity.neg` 两个文件，编码按原数据使用 CP1252。保留的 `DATASET_LICENSE.txt` 记录数据来源。

先按标签用固定 seed 划分 70% 训练、30% 验证，再仅用训练文本建立词表。未知词与填充分别为 1 和 0；序列长度至少为 5，以覆盖各卷积窗口。词表、长度、参数、seed 与验证统计随检查点保存。单次随机划分只是课程实验，不代表跨数据集的泛化效果。

```text
python predict.py --checkpoint outputs/textcnn.pt --text "This is a good movie."
```

`legacy/textcnn_mindspore.py` 是原 Ascend 实验版本，存在独立创建词表、旧接口及设备假设，未完成适配。当前受验证的入口为 `train.py` / `predict.py`，不要直接运行 legacy 作为复现入口。
