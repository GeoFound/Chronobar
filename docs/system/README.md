# System Protocol Documents

本目录包含系统组织与接入层文档，定义模块如何组合、配置如何进入系统、前端如何访问核心。

## 文档列表

- **architecture.md** - 系统架构设计（七层架构、主引擎协调模式、实时/回放主流程、依赖方向约束）
- **config_protocol.md** - 系统配置管理（系统/市场/规则/指标/工作区配置、schema 校验、migration 规则）
- **ui_bridge_protocol.md** - 前后端协作边界（Query API、Command API、Subscription API、状态同步、错误模型）

## 层级归属

这些文档属于第二层：系统组织与接入层。它们建立的是"系统运行方式"，而不是某个具体功能的实现细节。
