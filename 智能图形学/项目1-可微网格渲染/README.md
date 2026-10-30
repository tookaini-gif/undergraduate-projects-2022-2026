# 可微网格渲染

使用 Jittor 与 JRender 渲染 OBJ 网格的旋转动画，并观察 SoftRas 参数变化。

> 技术栈：Python / Jittor / JRender  
> 验证范围：源码整理；未配置 Linux/CUDA/JRender 运行环境

## 项目内容

原文件虽名为 nerf.py，实际执行已知网格的可微渲染，不是从图片训练 NeRF。保留真实实现并补充外部 OBJ/纹理依赖检查；另附未完成的网格优化草稿说明。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
python -m pip install -r requirements.txt
python render.py --filename-input path/to/model.obj --output-dir outputs
```

## 文件导航

- `legacy/`：原始学习版本与草稿（不作为验证入口）
- `render.py`
- `requirements.txt`

## 来源与整理边界

CGRAPHICS/demonerf/nerf.py 与 JITTOR/jitto.py；与 JRender 示例结构近似，上游确认见 NOTICE。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)

## 输入和输出

需自行提供有使用权的 OBJ 网格及其 MTL/纹理资源。输出包括 `rotation.gif`、`bluring.gif` 和导出的 OBJ。此例来自/参考 [JRender](https://github.com/Jittor/jrender) 的渲染流程，重点是接口实践和结果观察。没有有效网格资源时不会宣称已经运行成功。

`legacy/mesh_optimization_draft.py` 仅为草稿，尚存在图像加载、相机与优化接口假设，未构成完整的从单张照片重建三维物体的系统。
