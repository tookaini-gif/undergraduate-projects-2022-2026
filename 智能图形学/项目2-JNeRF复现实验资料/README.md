# JNeRF复现实验资料

记录原目录中的 JNeRF 实验配置与上游运行入口，避免重复上传完整开源框架。

> 技术栈：Python / JNeRF / Jittor / CUDA  
> 验证范围：上游复现资料；配置语法检查通过，未训练

## 项目内容

仅保留原包的上游配置和许可证，不把 JNeRF 框架算作个人原创。两份重复仓库、依赖副本、模型数据及环境均省略。运行时请先按上游文档准备数据和编译环境。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
git clone https://github.com/Jittor/JNeRF.git
cd JNeRF
python -m pip install -r requirements.txt
python -m pip install -e .
python tools/run_net.py --config-file projects/ngp/configs/ngp_base.py
```

## 文件导航

- `configs/`：上游配置快照
- `UPSTREAM_LICENSE.txt`

## 来源与整理边界

JNeRF 项目由 Jittor 社区提供，Apache-2.0；本地未建立可核实的个人代码变更清单。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)

## 上游与复现记录

上游：[Jittor/JNeRF](https://github.com/Jittor/JNeRF)。配置位于本目录 `configs/`，原许可证随 `UPSTREAM_LICENSE.txt` 保留；请从上游取得完整框架。需要自行准备场景数据、相机参数及 CUDA 环境。

当前保留的是学习资料和配置快照，没有验证出个人算法改进或训练指标。上游 README 中的性能属于上游作者，不列为本项目个人成果。建议后续复现时记录 commit、数据来源、划分、设备、命令与日志后，再填写实验对照表。
