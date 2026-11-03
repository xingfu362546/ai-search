# AI 超级搜索（原型 + 方案 v5 / v6）

## 版本与分支

| Tag | 提交 | 内容 | 维护分支 |
|-----|------|------|----------|
| `v1.0.0` | `2e1ee7e` | 仅线下课程期数 1 类，其余走「去全部看看」 | `release/v1.0` |
| `v1.1.0` | `7386d8e` | 全站 8 类按意图命中，内容类走知识库 | `release/v1.1` |

- `main` 是主干，新版本从 `main` 开 `feature/*` 开发，交付后打 tag 并合并回 `main`
- `release/*` 只用于线上问题的补丁，不再接新功能
- **版本号与文档命名不同步**：仓库里的 v5 / v6 字样是文档的迭代代号，
  对应关系是 **v5 文档 = v1.0.0**、**v6 文档 = v1.1.0**。以 tag 为准。

| 文档中的叫法 | 版本号 |
|--------------|--------|
| v5 原型 / v5 方案 / `intent-slots-v5.json` | v1.0.0 |
| v6 原型 / v6 方案 / `spec-v6.md` / `ai-search-v6.yml` | v1.1.0 |

## 入口

打开 [index.html](./index.html) 选择「交互原型」或「技术方案」。

| 文件 | 说明 |
|------|------|
| [index.html](./index.html) | 项目导航页 |
| [ai-search-v1.html](./ai-search-v1.html) | 交互原型（侧栏含「查看技术方案 v5」入口） |
| [ai-search-dify-architecture-draft.html](./ai-search-dify-architecture-draft.html) | 意图识别技术方案 v5 |
| [ai-search-dify-architecture-v6.html](./ai-search-dify-architecture-v6.html) | **技术方案 v6**（8 类子流、接口占位清单、HTTP 与知识库双通道） |

## v5 落地文件

| 路径 | 用途 |
|------|------|
| [config/intent-slots-v5.json](./config/intent-slots-v5.json) | 前置检索字段定义 + ready 规则 + JSON Schema |
| [config/entity-dictionary.example.json](./config/entity-dictionary.example.json) | 课名/城市/导师词典示例（进知识库或 BFF） |
| [docs/dify-prompt-node1-v5.txt](./docs/dify-prompt-node1-v5.txt) | Dify 节点① 系统 Prompt（可直接复制） |
| [docs/test-queries-v5.md](./docs/test-queries-v5.md) | 10 条验收用例 |

## v6 规划

| 路径 | 用途 |
|------|------|
| [docs/spec-v6.md](./docs/spec-v6.md) | **v6 需求说明书**（8 类意图 Prompt、路由规则、子流字段、导语 Prompt、验收用例） |
| [dsl/ai-search-v6.yml](./dsl/ai-search-v6.yml) | **v6 Dify DSL**（可导入；课程链保留，内容类走知识库） |
| [dsl/README.md](./dsl/README.md) | DSL 导入后待填项、节点地图、验证方式 |
| [ai-search-dify-architecture-v6.html](./ai-search-dify-architecture-v6.html) | **v6 技术方案**（节点规格、接口待填补模板、知识库方案、联调顺序） |
| [ai-search-v6.html](./ai-search-v6.html) | **v6 原型**（全站 8 类按意图命中，无「去全部看看」） |
| [docs/plan-v6-full-scope.md](./docs/plan-v6-full-scope.md) | 全站智能检索版本规划 |
| [docs/dsl-analysis.md](./docs/dsl-analysis.md) | 生产 Dify DSL 现状解析（实际只实现 1 类，v6 改造清单） |
| [config/intent-slots-v6.json](./config/intent-slots-v6.json) | v6 意图枚举（8 类 + general）+ 各类抽参字段 + 结果编排策略 |
| [docs/diagrams/](./docs/diagrams/) | 四张图：现状流程 / v6 画布目标架构 / 子流标准结构 / 数据源双通道（drawio + PNG） |

## v5 概述

**course_enroll** → 字段抽取 → 期数 HTTP → 卡片；**other / 字段不足** → 小Q +「去全部看看」（带 keyword）。

## 参考

| 文件 | 说明 |
|------|------|
| [ai-search-v2-all.html](./ai-search-v2-all.html) | 仅「全部 Tab」瀑布 UI 参考 |
