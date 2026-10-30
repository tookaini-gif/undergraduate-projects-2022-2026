# Java基础算法练习

以独立控制台程序练习字符串、循环、数值精度与输入边界处理。

> 技术栈：Java / 标准库  
> 验证范围：已编译；18 项输入与边界检查通过

## 项目内容

覆盖后缀删除、后缀匹配、成绩筛选、连分式、最大值表达式、整数立方根和任意精度的 2 的幂。文件名保留原练习入口，README 给出输入输出。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
javac -encoding UTF-8 -d out src/*.java
java -cp out Delete
```

## 文件导航

- `src/`：主要源码

## 来源与整理边界

原 Java 目录中的七个练习；不纳入同学署名的 C++ 作业。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)

## 输入输出示例

| 入口 | 输入 | 输出 | 规则 |
| --- | --- | --- | --- |
| Delete | `working` | `work` | 去除 ing/er/ly；不匹配时保留原词 |
| strcmp | `hello lo` | `true` | 检查第二个字符串是否为第一个的后缀 |
| Score | `3 -5 Alice -2 Bob -2 Carol` | `Bob` | 最高分；并列时保留先出现者；n 必须大于 0 |
| Twopowern | `100` | `1267650600228229401496703205376` | 任意精度非负整数幂 |
| root3 | `-28` | `-3` | 整数立方根，向零截断 |
| fxn | `2 2` | `0.75` | 初值 a=x，依次令 a=x/(i+a)，i 从 1 到 n |
| m | `1 2 3` | `0.200` | max(a,b,c)/(max(a+b,b,c) × max(a,b,b+c)) |

PowerShell 编译时如不支持通配符展开，可使用 `javac -encoding UTF-8 -d out (Get-ChildItem src/*.java).FullName`。批量回归入口为仓库根目录 `python tools/check_native.py`。
