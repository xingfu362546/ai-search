# v5 意图识别 · 测试用例

| # | 用户输入 | 期望 intent | 期望 ready | 期望 slots 要点 | 期望 APP |
|---|----------|-------------|------------|-----------------|----------|
| 1 | 智慧父母一阶 | course_enroll | true | course_name=智慧父母一阶 | AI + 期数卡 |
| 2 | 广州最近有哪些课程正在开课 | course_enroll | true | city=广州, time_window=30 | AI + 期数卡 |
| 3 | 总导师的课程有哪些 | course_enroll | true | instructor_name=总导师 | AI + 期数卡 |
| 4 | （history 有 #1）南宁站还有吗 | course_enroll | true | city=南宁, 继承课名 | AI 续聊 + 卡 |
| 5 | 6Q潮玩盲盒 | other | false | keyword 保留 | 小Q + 去全部 |
| 6 | 音频 | other | false | keyword=音频 | 小Q + 去全部 |
| 7 | 6Q | other | false | keyword=6Q | 小Q + 去全部 |
| 8 | 课程 | other | false | missing 或引导补充 | 小Q + 去全部 |
| 9 | 一阶 | course_enroll | true* | course_name=智慧父母一阶（词典命中） | AI + 期数卡 |
| 10 | API 返回 0 条 | course_enroll | true | — | 小Q + 去全部 |

\* 依赖实体词典将「一阶」映射到标准课名。
