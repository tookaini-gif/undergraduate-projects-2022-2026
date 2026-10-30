# MiniChat本地推理

整理 MiniChat 语言模型的单轮命令行推理流程。

> 技术栈：Python / Transformers / PyTorch  
> 验证范围：命令行参数与语法已检查；缺少本地模型，实际推理未运行

## 项目内容

修复强制 CUDA 与 CPU 不兼容问题，增加模型路径、设备、随机种子与生成长度参数，输出只保留新生成文本。原“微调后.txt”为空，未找到微调训练脚本，故不宣称完成微调。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
python -m pip install -r requirements.txt
python minichat.py --model path/to/minichat-2-3b --question "Solve for x: 5x + 3 = 29."
```

## 文件导航

- `legacy/`：原始学习版本与草稿（不作为验证入口）
- `minichat.py`
- `requirements.txt`

## 来源与整理边界

自然大作业/minichat.py；课程要求文件不作为个人成果发布。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)
