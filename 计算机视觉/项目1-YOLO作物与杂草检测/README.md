# YOLO作物与杂草检测

整理目标检测训练、图片预测与 CSV 结果导出流程。

> 技术栈：Python / Ultralytics / YOLO  
> 验证范围：空检测、CSV 坐标和类别统计回归通过；未重训/评估 YOLO

## 项目内容

去除 D 盘固定路径；初始训练不再依赖缺失的 best.pt。统一导出逻辑，修复零检测时 CSV 崩溃和类别统计颠倒。类别顺序以原 dataset.yaml 为准；不发布整套数据及未明确授权的样本。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
python -m pip install -r requirements.txt
python main.py train --data dataset.yaml --weights yolo11n.pt --epochs 60
python main.py predict --weights path/to/best.pt --source path/to/images --output detections.csv
```

## 文件导航

- `dataset.yaml`
- `export.py`
- `legacy/`：原始学习版本与草稿（不作为验证入口）
- `main.py`
- `predict.py`
- `requirements.txt`

## 来源与整理边界

WD/Weed_Detection_final/Weed_Detection 的 main.py 与 predict.py。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)
