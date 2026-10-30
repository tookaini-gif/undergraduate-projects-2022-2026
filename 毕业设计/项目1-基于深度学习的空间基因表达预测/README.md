# 基于深度学习的空间基因表达预测

保留毕业设计 Web 原型、模型适配接口与数据准备工具，明确可复现边界。

> 技术栈：Python / FastAPI / PyTorch / 空间转录组  
> 验证范围：Web 接口及错误状态回归通过；真实模型实现、权重与基因映射缺失

## 项目内容

压缩包未包含 stflow.flow.model.STFlowDKAN 和训练权重，不能恢复完整训练实验。公开版移除随机伪热图及按任意基因顺序分配结果，模型不可用时返回明确的 503；不输出临床风险判断。原近似指标绘图移入 legacy 并标为未复核，不能作为评测成绩。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
python -m pip install -r requirements.txt
python main.py
# http://127.0.0.1:8000；真实预测还需模型实现、权重与基因映射
```

## 文件导航

- `check_key.py`
- `download.py`
- `index.html`
- `legacy/`：原始学习版本与草稿（不作为验证入口）
- `main.py`
- `model_wrapper.py`
- `requirements-research.txt`
- `requirements.txt`

## 来源与整理边界

本人署名毕业设计源代码包；验收表、查重报告、指导记录及带签字材料不发布。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)

## 实际缺失内容

验收包只含网页服务、适配脚本与辅助绘图，未包含 `stflow.flow.model.STFlowDKAN`、训练数据处理主流程、训练权重和训练输出基因顺序。原适配器按请求顺序切片输出并产生随机热图，无法支撑可靠的基因对应或空间定位；发布入口已移除这些行为。

无需模型即可启动页面；`GET /health` 用 `model_ready` 表示模型状态。合法图片预测在未配置模型时返回 HTTP 503，而不是合成表达值。

如恢复了真实研究代码，设置 `STFLOW_BACKEND=你的Python模块:工厂函数`。工厂返回有 `predict(PIL.Image, list[str]) -> dict[str, float]` 方法的对象，并负责训练时的预处理、权重加载和真实基因映射。返回的键必须与请求一致，值必须为有限数。不要仅补一个随机网络或按用户输入的顺序猜测基因名。

接口：`POST /predict` 使用 multipart 字段 `image` 和 `genes`，接受最多 10 MB 的 PNG/JPEG。只有后端确实可用时才返回预测值；当前不输出空间热图、风险评分或临床诊断。

`legacy/chart*.py` 中数值包含近似与示例处理，未与原训练日志交叉验证，不作为实验成绩。原验收截图、签字材料、论文查重记录与个人表格不公开。
