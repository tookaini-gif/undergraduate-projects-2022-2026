# CPU与CUDA的KMeans聚类

对照串行聚类与 CUDA 并行实现，整理构建入口及数据格式。

> 技术栈：C++ / CUDA / CMake  
> 验证范围：CPU 编译及 7 项检查通过；CUDA 未编译

## 项目内容

CPU 版本修复固定绝对路径、越界读取和空簇除零；保留 CUDA 课程代码并去除重复 I/O 定义。CUDA 代码使用 POSIX 接口，建议 WSL/Linux；本机无 nvcc，不宣称 GPU 加速比。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
cmake -S . -B build
cmake --build build
# CPU: build/kmeans_cpu data/texture100.txt 3
```

## 文件导航

- `CMakeLists.txt`
- `cuda/`
- `data/`：课程提供的小型样例数据
- `src/`：主要源码

## 来源与整理边界

原 CUDA Kmeans 压缩包；串行源文件署名 yangyuhan，保留在源文件及 THIRD_PARTY_NOTICES.md 中。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)

## 数据与 CUDA 构建

输入每行第一列为样本 ID，之后为等长数值特征。自带 `texture100.txt` 为 100 行、20 维；CPU 版正确跳过 ID 列，输出含中心、归属、惯性值与实际耗时的 JSON。异常行或不合法 k 会返回非零退出码。

Windows 的构建输出也可能位于 `build/Debug/kmeans_cpu.exe`。Linux/WSL 中已安装 CUDA Toolkit 时可额外构建：

```text
cmake -S . -B build -DBUILD_CUDA=ON
cmake --build build
./build/kmeans_cuda -i data/texture100.txt -n 3 -o
```

CUDA 课程代码保留原始的 POSIX I/O 和聚类终止条件；CPU 与 CUDA 停止标准不同，比较性能前必须统一参数并核对聚类输出。当前没有可核实的 GPU 加速比。
