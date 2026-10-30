# 手势控制贪吃蛇

使用预训练手部关键点检测，将食指位置映射到贪吃蛇轨迹。

> 技术栈：Python / OpenCV / MediaPipe  
> 验证范围：轨迹、碰撞、增长、重置逻辑回归通过；摄像头交互未验证

## 项目内容

合并 SGAME 与认知神经科学中的重复版本；修复首帧轨迹、遍历时删除列表、碰撞检测和重置状态，改为绘制食物，解除缺失图片依赖。这是预训练模型应用，没有自行训练手部检测网络。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
python -m pip install -r requirements.txt
python main.py --camera 0 --model path/to/hand_landmarker.task
```

## 文件导航

- `engine.py`
- `hand_tracker.py`
- `legacy/`：原始学习版本与草稿（不作为验证入口）
- `main.py`
- `requirements.txt`

## 来源与整理边界

SGAME/SGAme.py、SHE2.py 及认知神经科学重复脚本；原代码结构具有教学示例特征，未确认的上游来源见 NOTICE。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)

## 手部检测模型

依照 [MediaPipe Hand Landmarker Python 官方说明](https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python) 获取兼容的 `hand_landmarker.task`，存于本机并通过 `--model` 指定。仓库不重新分发模型文件。程序使用 Tasks 的 VIDEO 模式和单调递增的毫秒时间戳；旧版 `mp.solutions` 脚本仅保留为历史资料。

摄像头需要操作系统授权。程序不会录制或上传视频。按 Esc/Q 退出；所有退出路径均尝试释放摄像头与检测器。
