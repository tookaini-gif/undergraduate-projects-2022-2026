# 键盘贪吃蛇

补齐原脚本缺失的 settingsSnakeFun 模块后，整理为无需外部图片和音频的键盘小游戏。

> 技术栈：Python / Pygame  
> 验证范围：规则回归通过；Pygame 窗口交互未验证

## 项目内容

方向键或 WASD 控制，R 重新开始，Esc 退出。新实现补齐碰撞、计分、重开和棋盘已满的结束逻辑；修复版属于本次整理新增，不能等同于本科期间原有成果。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
python -m pip install -r requirements.txt
python main.py
```

## 文件导航

- `engine.py`
- `legacy/`：原始学习版本与草稿（不作为验证入口）
- `main.py`
- `requirements.txt`

## 来源与整理边界

tooka/untitled1.py 的游戏需求；发布版为补全重构。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)
