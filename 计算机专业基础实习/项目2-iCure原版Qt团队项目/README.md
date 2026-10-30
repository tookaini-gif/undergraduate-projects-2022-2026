# iCure原版Qt团队项目

保留智慧医疗管理系统原 Qt 客户端与 TCP 聊天服务端源码，说明其历史环境依赖。

> 技术栈：C++ / Qt Widgets / Qt Network / Qt SQL  
> 验证范围：历史团队源码；本机无 Qt，构建未验证

## 项目内容

包含注册登录、医患档案、预约、健康记录和聊天协议。原数据库和个人图片不公开；旧版路径与依赖不能假定开箱即用。建议先体验同课程的 Python 本机演示版本。

## 运行方式

在本项目目录打开终端，先确认项目所需的运行环境。Python 项目建议使用独立虚拟环境；下方 `path/to/...` 是需要替换的本地路径。

```text
qmake iCure/iCure.pro
# 使用 Qt Creator 分别打开 iCure/iCure.pro 和 Server/Server.pro
```

## 文件导航

- `eyetest.jpg`
- `healthcare.png`
- `hospital.jpg`
- `icon.png`
- `icon1.png`
- `iCure/`
- `Server/`
- `yourhealth.png`

## 来源与整理边界

iCure 第三组压缩包；用户提供的项目 PPT 第 8 页列明：涂恺倪为 TL（团队领袖），负责医生端系统、聊天机器人、系统翻译功能；对应源码与实现边界见贡献说明。

本仓库于 2026-10-30 整理。补全与重构属于此次维护，不反推为 2022–2026 年期间已完成的工作；原始版本统一收在 `legacy/`（如有）。完整验证范围见[验证记录](../../docs/VALIDATION.md)，署名与上游说明见[来源声明](../../THIRD_PARTY_NOTICES.md)。

[返回课程目录](../README.md) · [返回项目集首页](../../README.md)

## 原环境待补项

原工程依赖 Qt Widgets、Network、SQL、Charts 及 SQLite。`iCure.pro` 中包含客户端界面和数据访问，`Server.pro` 是 TCP 聊天服务端；分别构建。固定开发者路径已改成相对路径，资源和头文件大小写引用已检查。

出于公开展示需要，未附原数据库；代码中的旧数据访问方式仍需整理迁移，不适合作为直接上线版本。当前不提供原个人账号，也没有虚构一个“原系统已成功重新编译”的结论。无需 Qt 的可运行展示入口见同课程项目 1。

## 个人职责

涂恺倪：TL（团队领袖）；PPT 记录的分工为医生端系统、聊天机器人、系统翻译功能。已将原版实际可核对的代码与后续重构分开说明，详见[个人职责与实现证据](../../docs/ICURE_CONTRIBUTIONS.md)。
