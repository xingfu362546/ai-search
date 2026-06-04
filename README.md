# AI 超级搜索（原型 + 方案 v5）

## 入口

打开 [index.html](./index.html) 选择「交互原型」或「技术方案」。

| 文件 | 说明 |
|------|------|
| [index.html](./index.html) | 项目导航页 |
| [ai-search-v1.html](./ai-search-v1.html) | 交互原型（侧栏含「查看技术方案 v5」入口） |
| [ai-search-dify-architecture-draft.html](./ai-search-dify-architecture-draft.html) | 意图识别技术方案 v5 |

## v5 落地文件

| 路径 | 用途 |
|------|------|
| [config/intent-slots-v5.json](./config/intent-slots-v5.json) | 前置检索字段定义 + ready 规则 + JSON Schema |
| [config/entity-dictionary.example.json](./config/entity-dictionary.example.json) | 课名/城市/导师词典示例（进知识库或 BFF） |
| [docs/dify-prompt-node1-v5.txt](./docs/dify-prompt-node1-v5.txt) | Dify 节点① 系统 Prompt（可直接复制） |
| [docs/test-queries-v5.md](./docs/test-queries-v5.md) | 10 条验收用例 |

## v5 概述

**course_enroll** → 字段抽取 → 期数 HTTP → 卡片；**other / 字段不足** → 小Q +「去全部看看」（带 keyword）。

## 参考

| 文件 | 说明 |
|------|------|
| [ai-search-v2-all.html](./ai-search-v2-all.html) | 仅「全部 Tab」瀑布 UI 参考 |
