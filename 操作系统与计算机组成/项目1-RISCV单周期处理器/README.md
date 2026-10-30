# RISCV单周期处理器

使用 Verilog 组织 RV32 单周期数据通路、控制器和测试程序。

> 技术栈：Verilog / RISC-V / Vivado  
> 验证范围：源码与路径已整理；无 Verilog 仿真工具，未运行仿真

## 项目内容

保留 ALU、寄存器堆、存储器、立即数扩展、控制器及顶层连接；修复指令文件绝对路径，测试平台增加超时和明确退出码。RARS 汇编作为配套练习保留，不宣称与测试 ROM 完全对应。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
iverilog -g2012 -s testbench -o simulation src/*.v sim/testbench.v
vvp simulation
```

## 文件导航

- `asm/`
- `imem.txt`
- `riscvtest.txt`
- `sim/`
- `src/`：主要源码

## 来源与整理边界

原目录名为“操纵系统”，内容属于计算机组成/RISC-V 实验，按实际技术调整展示标题。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)
