# 验证记录

日期：2026-10-30（北京时间）。环境：Windows、Python 3.12、JDK 和 MinGW g++，另使用本机已有的 PyTorch、FastAPI 等库。以下“通过”对应发布副本，原始目录未修改。

| 范围 | 结果 | 实际验证内容 |
| --- | --- | --- |
| Java 七个程序 | 18 项通过 | 无匹配后缀、负分/零分、大整数幂、正负整数立方根、字符串后缀、公式结果、非法 n 与零分母 |
| KMeans CPU | 7 项通过 | 编译，自带 100×20 数据，空簇/相同点、异常维度、空输入、k 越界、非法数字 |
| 项目集回归 | 10 项通过 | 训练/验证隔离、未知词、两个游戏的规则、YOLO 空结果/类别/坐标、研究后端约定及 HTTP 输入与状态 |
| iCure 本机版 | 11 组通过 | 零旧数据初始化、密码哈希、身份/CSRF、注册/修改回滚、预约冲突、病历权限、附件访问、健康数据、离线助手、在线调用模拟、导出和静态资源 |
| TextCNN 冒烟验证 | 通过 | 12 条专门生成的合成短句，CPU 一轮训练、保存参数/词表/长度、重新加载并推理。该结果不用于宣称真实数据准确率 |
| JavaScript | 通过 | `node --check dist/app.js`；此检查不等同于真实浏览器回归 |
| 源码与文档 | 通过 | Python AST 解析、每项目 README、仓库内相对链接、发布目录大文件与本地数据类型检查 |

## 重复验证

根目录执行：

```text
python tools/check_portfolio.py
python -m unittest discover -s tests -v
python tools/check_native.py
```

研究 API 的三项测试需要 FastAPI、Pillow、python-multipart 和 httpx；未安装时会明确跳过该测试类，其余七项不要求模型框架。安装方式：`python -m pip install fastapi Pillow python-multipart httpx`。原生代码检查需要 `javac`、`java`、`g++` 位于 PATH，测试产物写到临时目录。

iCure 的 11 组测试在其项目目录执行 `python -m unittest discover -s tests -v`。测试自建临时数据库，未使用原始患者或医生资料。

## 未验证的范围

- CUDA：无 nvcc/GPU 工具链，未编译并行版本，未测加速比。
- RISC-V：无 Verilog 仿真器，未验证功能仿真或上板。
- Qt：无 Qt Creator/qmake 环境，未重新编译原版；固定路径与文件大小写引用仅作静态修复。
- 摄像头：未启用用户设备；MediaPipe 模型与实时交互未验证。Pygame 仅验证规则，未操作窗口。
- YOLO：未重训、未加载原始权重，不报告 mAP、召回率或竞赛分数。
- MiniChat/JNeRF/JRender：未下载模型/训练场景，未实际推理或渲染。
- 毕业设计：缺实际研究模型、权重、训练代码和基因顺序。API 使用测试夹具验证响应格式，夹具数值不是科学实验结果。
- MySQL：本机无服务，SQL 已修正可静态识别的问题，语法与事务行为仍待实际服务验证。

测试通过只覆盖表中列出的行为，不代表所有历史实验、设备和模型均已复现。未来增加实际模型、数据或依赖后，应重新核验对应项目并更新此记录。
