# -*- coding: utf-8 -*-
"""生成 6Q 超级搜索的 drawio 图：
1) 01-现状-Dify流程-过往版本.drawio   生产 DSL 的完整逻辑（as-is）
2) 02-v6-智能体画布-目标架构.drawio   v6 主流程 + 8 子流（to-be）
3) 03-v6-子流标准结构.drawio          以线下课程为例的子流模板
"""
import os
import html

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "diagrams")

S = {
    "start": "rounded=1;arcSize=50;whiteSpace=wrap;html=1;fillColor=#1a1a1a;fontColor=#ffffff;strokeColor=#000000;fontSize=12;fontStyle=1;",
    "llm": "rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;",
    "code": "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=11;",
    "cond": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;",
    "http": "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;",
    "kb": "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;",
    "answer": "rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=11;",
    "del": "rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;fontStyle=1;",
    "todo": "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#b85450;dashed=1;fontSize=11;",
    "ok": "rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;fontStyle=1;",
    "lane": "rounded=0;whiteSpace=wrap;html=1;fillColor=#fbfbfb;strokeColor=#d0d0d0;verticalAlign=top;align=left;fontSize=11;fontColor=#9a9a9a;dashed=1;spacingLeft=8;spacingTop=4;",
    "note": "shape=note;whiteSpace=wrap;html=1;fillColor=#fffbe6;strokeColor=#d6b656;fontSize=11;align=left;spacingLeft=6;size=14;",
}

E_DEF = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;endFill=1;strokeColor=#666666;fontSize=10;labelBackgroundColor=#ffffff;"
E_DASH = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;endFill=1;strokeColor=#b85450;dashed=1;fontSize=10;labelBackgroundColor=#ffffff;"
E_MAIN = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;endFill=1;strokeColor=#333333;strokeWidth=1.5;fontSize=10;labelBackgroundColor=#ffffff;"


class D:
    def __init__(self):
        self.cells = []

    def node(self, nid, label, x, y, w=230, h=66, kind="answer"):
        style = S.get(kind, S["answer"])
        self.cells.append(
            '<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
            '<mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry"/></mxCell>'
            % (nid, html.escape(label).replace("\n", "&#10;"), style, x, y, w, h)
        )

    def lane(self, nid, label, x, y, w, h):
        self.node(nid, label, x, y, w, h, "lane")

    def edge(self, eid, src, tgt, label="", style=E_DEF, points=None,
             exitx=None, exity=None, entryx=None, entryy=None):
        st = style
        if exitx is not None:
            st += "exitX=%s;exitY=%s;exitDx=0;exitDy=0;" % (exitx, exity)
        if entryx is not None:
            st += "entryX=%s;entryY=%s;entryDx=0;entryDy=0;" % (entryx, entryy)
        geom = '<mxGeometry relative="1" as="geometry">'
        if points:
            geom += '<Array as="points">' + "".join(
                '<mxPoint x="%s" y="%s"/>' % (px, py) for px, py in points
            ) + "</Array>"
        geom += "</mxGeometry>"
        self.cells.append(
            '<mxCell id="%s" value="%s" style="%s" edge="1" parent="1" source="%s" target="%s">%s</mxCell>'
            % (eid, html.escape(label), st, src, tgt, geom)
        )

    def save(self, path, page_w, page_h, title):
        xml = (
            '<mxfile host="app.diagrams.net" type="device">'
            '<diagram id="p1" name="%s">'
            '<mxGraphModel dx="%d" dy="%d" grid="1" gridSize="10" guides="1" tooltips="1" '
            'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" math="0" shadow="0">'
            "<root>"
            '<mxCell id="0"/>'
            '<mxCell id="1" parent="0"/>'
        ) % (html.escape(title), page_w, page_h, page_w, page_h)
        xml += "".join(self.cells)
        xml += "</root></mxGraphModel></diagram></mxfile>"
        with open(path, "w", encoding="utf-8") as f:
            f.write(xml)
        print("wrote", path, len(self.cells), "cells")


# ---------------------------------------------------------------- 图1 现状
def build_asis():
    d = D()
    # 泳道
    d.lane("lane1", "① 输入预处理", 20, 20, 1640, 130)
    d.lane("lane2", "② 意图识别与字段提取", 20, 160, 1640, 330)
    d.lane("lane3", "③ 分支路由（2.4 条件分支）", 20, 500, 1640, 170)
    d.lane("lane4", "④ 数据检索与结果判断", 20, 680, 1640, 470)
    d.lane("lane5", "⑤ 内容生成与输出", 20, 1160, 1640, 390)

    d.node("n_start", "2.1 开始\nhistory · user_city · current_date\nsession_id · user_id · shown_session_ids", 750, 45, 250, 78, "start")
    d.node("n_clean", "clean_history\n编码逆修复 latin-1 → utf-8", 750, 150, 250, 62, "code")
    d.node("n_llm", "2.2 LLM 意图识别与字段提取\nqwen3.6-flash · temperature 0.8\n输出 14 个字段的单个 JSON", 730, 245, 290, 78, "llm")
    d.node("n_parse", "2.3 代码 解析意图识别结果\n去掉 ```json 包裹 · 处理嵌套 text", 730, 360, 290, 66, "code")
    d.node("n_clean2", "2.3A 代码 shownSessionIds 清洗\n仅 reply_mode=follow_up 时透传", 730, 455, 290, 66, "code")

    d.node("n_cond", "2.4 条件分支 · 4 CASE + ELSE", 725, 545, 290, 70, "cond")

    # 分支
    d.node("n_ans_supp", "2.5 回复 补充信息\n提示补充课名 / 城市 / 导师", 40, 700, 230, 70, "answer")
    d.node("n_kb", "2.15A 知识库 课程查询\n混合检索 向量0.6+关键词0.4 · top_k 10", 390, 700, 230, 70, "kb")
    d.node("n_http_d", "2.15D HTTP 线下课查询\n按导师 / 城市等条件", 740, 700, 230, 70, "http")
    d.node("n_llm_chat", "2.18 LLM 闲聊回复", 1090, 700, 230, 70, "llm")
    d.node("n_fallback", "兜底 / 去全部看看\n「小Q暂不支持其他类型的\n智能检索哦」+ 按钮", 1440, 700, 230, 70, "del")

    d.node("n_kb2", "2.15B 代码 解析课程知识库结果\n输出 course_id / 全称 / 亮点", 390, 800, 230, 66, "code")
    d.node("n_chat_ans", "闲聊回复\n@hsy 隐藏元数据", 1090, 800, 230, 66, "answer")

    d.node("n_kb3", "2.15C 判断 知识库命中态\nsingle / multiple / none", 355, 900, 300, 66, "cond")

    d.node("n_http_c", "2.15 HTTP 线下课查询\n按课程标准化（带 kb_course_id）", 390, 1010, 230, 70, "http")
    d.node("n_parse2", "2.16 解析查询结果\nresult_state: has_result / empty / no_more / error", 740, 1010, 230, 70, "code")
    d.node("n_judge", "2.17 结果判断\n4 CASE + ELSE", 690, 1110, 300, 62, "cond")

    d.node("n_l1", "2.9 LLM 线下课导语\n课程说明 → 亮点 → 期数说明", 200, 1215, 230, 70, "llm")
    d.node("n_l2", "2.9B LLM 导语通用\n按 reply_mode 分口径", 520, 1215, 230, 70, "llm")
    d.node("n_e1", "2.11 线下课空结果提示", 840, 1215, 230, 70, "answer")
    d.node("n_e2", "2.12 没有更多", 1160, 1215, 230, 70, "answer")
    d.node("n_e3", "线下课其他异常", 1480, 1215, 230, 70, "answer")

    d.node("n_out", "2.13 线下课统一回复\n导语 + list_json_marked(@s_obj@)", 340, 1330, 300, 74, "answer")

    d.node("n_note", "说明\n· 23 个节点与生产 DSL 一一对应，连线按实际条件分支绘制\n· 只有 1 个数据接口：goods/api/product/periods/ai/list\n· 意图仅 course_enroll | other，其余 7 类全部落入 ELSE\n· 红色节点为 v6 待删除", 40, 1430, 640, 112, "note")

    # 主链
    d.edge("e1", "n_start", "n_clean", "", E_MAIN)
    d.edge("e2", "n_clean", "n_llm", "", E_MAIN)
    d.edge("e3", "n_llm", "n_parse", "原始 text", E_MAIN)
    d.edge("e4", "n_parse", "n_clean2", "", E_MAIN)
    d.edge("e5", "n_clean2", "n_cond", "", E_MAIN)

    # 2.4 五个出口
    d.edge("e6", "n_cond", "n_ans_supp", "CASE1",
           E_DEF, points=[(753, 660), (155, 660)], exitx=0.1, exity=1, entryx=0.5, entryy=0)
    d.edge("e7", "n_cond", "n_kb", "CASE2",
           E_MAIN, points=[(809, 686), (505, 686)], exitx=0.3, exity=1, entryx=0.5, entryy=0)
    d.edge("e8", "n_cond", "n_http_d", "CASE3",
           E_DEF, points=[(865, 678), (855, 678)], exitx=0.5, exity=1, entryx=0.5, entryy=0)
    d.edge("e9", "n_cond", "n_llm_chat", "CASE4",
           E_DEF, points=[(921, 672), (1205, 672)], exitx=0.7, exity=1, entryx=0.5, entryy=0)
    d.edge("e10", "n_cond", "n_fallback", "ELSE ★删除",
           E_DASH, points=[(977, 664), (1555, 664)], exitx=0.9, exity=1, entryx=0.5, entryy=0)

    d.edge("e11", "n_kb", "n_kb2")
    d.edge("e12", "n_kb2", "n_kb3")
    d.edge("e13", "n_kb3", "n_http_c", "single", E_MAIN, exitx=0.25, exity=1, entryx=0.5, entryy=0)
    d.edge("e14", "n_kb3", "n_http_c", "multiple（已选最优）", E_MAIN, exitx=0.75, exity=1, entryx=0.5, entryy=0)
    d.edge("e15", "n_kb3", "n_ans_supp", "none 未命中知识库", E_DASH,
           points=[(300, 933), (155, 933)], exitx=0, exity=0.5, entryx=0.5, entryy=1)

    d.edge("e16", "n_http_c", "n_parse2")
    d.edge("e17", "n_http_d", "n_parse2", "", E_DEF, entryx=0.5, entryy=0)
    d.edge("e18", "n_parse2", "n_judge")
    d.edge("e19", "n_llm_chat", "n_chat_ans")

    d.edge("e20", "n_judge", "n_l1", "1", E_MAIN,
           exitx=0.1, exity=1, entryx=0.5, entryy=0, points=[(720, 1185), (315, 1185)])
    d.edge("e21", "n_judge", "n_l2", "2", E_DEF,
           exitx=0.35, exity=1, entryx=0.5, entryy=0, points=[(795, 1192), (635, 1192)])
    d.edge("e22", "n_judge", "n_e1", "3", E_DEF,
           exitx=0.7, exity=1, entryx=0.5, entryy=0, points=[(900, 1199), (955, 1199)])
    d.edge("e23", "n_judge", "n_e2", "4", E_DEF,
           exitx=1, exity=0.5, entryx=0.5, entryy=0, points=[(1275, 1141)])
    d.edge("e24", "n_judge", "n_e3", "ELSE", E_DASH,
           exitx=1, exity=0.2, entryx=0.5, entryy=0, points=[(1595, 1122)])

    d.edge("e25", "n_l1", "n_out", "", E_MAIN, exitx=0.5, exity=1, entryx=0.2, entryy=0,
           points=[(315, 1305), (400, 1305)])
    d.edge("e26", "n_l2", "n_out", "", E_MAIN, exitx=0.5, exity=1, entryx=0.75, entryy=0,
           points=[(635, 1305), (565, 1305)])

    d.node("n_legend", "2.4 分支条件\nCASE1：intent=course_enroll 且 ready_for_api=false\nCASE2：ready_for_api=true 且 course_category=offline_course 且 reply_mode=search_course\nCASE3：ready_for_api=true 且 course_category=offline_course 且 reply_mode≠search_course\nCASE4：reply_mode=social_chat\nELSE：其余（intent=other）→ 兜底 / 去全部看看\n\n2.17 出口条件\n1：success 且 result_state=has_result 且 reply_mode=search_course\n2：success 且 result_state=has_result 且 reply_mode≠search_course\n3：success 且 result_state=empty\n4：success 且 result_state=no_more\nELSE：接口失败或异常", 1060, 1330, 620, 170, "note")

    d.save(os.path.join(OUT_DIR, "01-现状-Dify流程-过往版本.drawio"), 1720, 1570, "现状 Dify 流程（过往版本）")


# ---------------------------------------------------------------- 图2 v6 目标架构
def build_v6():
    d = D()
    d.lane("laneA", "① 入口与意图识别（1 个 LLM，输出 intents[]）", 20, 20, 1480, 470)
    d.lane("laneB", "② 8 类并行检索子流（每类独立子工作流，接口待开发提供）", 20, 500, 1480, 380)
    d.lane("laneC", "③ 聚合、导语与输出", 20, 890, 1480, 400)

    d.node("v_start", "开始\nquery · history · user_city\ncurrent_date · session_id\nuser_id · shown_ids", 745, 40, 250, 92, "start")
    d.node("v_clean", "clean_history\n（保留，上游编码问题仍在）", 745, 145, 250, 62, "code")
    d.node("v_llm", "2.2 LLM 意图识别 v6\n判 8 类意图 + 抽各类 slot\n输出 intents[] 数组", 720, 225, 300, 82, "llm")
    d.node("v_parse", "解析意图结果\nintents[] · slots · confidence", 745, 325, 250, 66, "code")
    d.node("v_route", "路由分发（并行）\n按 intents[] 拉起对应子流", 705, 405, 330, 62, "cond")

    # 8 子流
    grid = [
        ("v_s1", "① 线上课程子流", 270, 545, "todo"),
        ("v_s2", "② 线下课程子流", 580, 545, "ok"),
        ("v_s3", "③ 领袖营子流", 890, 545, "todo"),
        ("v_s4", "④ 高EQ导师子流", 1200, 545, "todo"),
        ("v_s5", "⑤ 6Q商城子流", 270, 690, "todo"),
        ("v_s6", "⑥ 文章子流", 580, 690, "todo"),
        ("v_s7", "⑦ 视频子流", 890, 690, "todo"),
        ("v_s8", "⑧ 音频子流", 1200, 690, "todo"),
    ]
    for nid, label, x, y, kind in grid:
        sub = "（现状已有）" if kind == "ok" else "检索接口：待开发提供"
        d.node(nid, "%s\n\n接口 → 解析 → 判断 → 卡片\n%s" % (label, sub), x, y, 260, 110, kind)

    d.node("v_agg", "结果聚合\n多类合并 · 按固定顺序排序\n空类不渲染", 690, 915, 360, 76, "code")
    d.node("v_guide", "统一导语 LLM（1 个节点）\n按命中类目生成 1~2 段说明\n不编造接口外信息", 720, 1025, 300, 78, "llm")
    d.node("v_out", "卡片输出协议\n@s_obj@ + JSON（新增 type 字段区分 8 类）\n@hsy 隐藏元数据", 700, 1135, 340, 78, "answer")
    d.node("v_end", "结束（流式返回）", 780, 1245, 180, 46, "start")

    d.node("v_empty", "兜底：全类 0 结果\n8 类泛搜 → 仍为空则\n「没找到相关的内容，换个说法试试」", 1180, 915, 270, 90, "todo")
    d.node("v_chat", "闲聊分支（保留）\nsocial_chat → 1 句自然回应", 80, 300, 200, 90, "answer")

    d.node("v_note", "与现状的差异\n· 意图 course_enroll|other → 8 类 + general\n· 删除「兜底 / 去全部看看」节点与 ELSE 边\n· 新增 7 条子流（接口待定）\n· 导语由 2 个 LLM 合并为 1 个\n· 卡片 JSON 增加 type 字段", 40, 915, 600, 120, "note")

    d.edge("ve1", "v_start", "v_clean", "", E_MAIN)
    d.edge("ve2", "v_clean", "v_llm", "", E_MAIN)
    d.edge("ve3", "v_llm", "v_parse", "JSON", E_MAIN)
    d.edge("ve4", "v_parse", "v_route", "", E_MAIN)

    for i, (nid, _, x, _, _) in enumerate(grid):
        d.edge("ve_s%d" % i, "v_route", nid, "", E_DEF,
               exitx=round(0.06 + i * 0.125, 3), exity=1, entryx=0.5, entryy=0)
    d.edge("ve_chat", "v_route", "v_chat", "social_chat", E_DEF, exitx=0, exity=0.5, entryx=1, entryy=0.5)

    for i, (nid, _, x, _, _) in enumerate(grid):
        d.edge("ve_a%d" % i, nid, "v_agg", "", E_DEF, exitx=0.5, exity=1, entryx=0, entryy=0.5)
    d.edge("ve_empty", "v_agg", "v_empty", "全部为空", E_DASH, exitx=1, exity=0.5, entryx=0, entryy=0.5)
    d.edge("ve5", "v_agg", "v_guide", "", E_MAIN)
    d.edge("ve6", "v_guide", "v_out", "", E_MAIN)
    d.edge("ve7", "v_out", "v_end", "", E_MAIN)

    d.save(os.path.join(OUT_DIR, "02-v6-智能体画布-目标架构.drawio"), 1560, 1340, "v6 智能体画布目标架构")


# ---------------------------------------------------------------- 图3 子流模板
def build_subflow():
    d = D()
    d.lane("lane1", "子流标准结构（8 类共用同一模板，以线下课程为例）", 20, 20, 1560, 300)

    d.node("s_in", "子流入口\n继承 intents / slots / shown_ids", 40, 80, 210, 80, "start")
    d.node("s_kb", "知识库 课程归一化\n仅课程类需要；内容类可跳过", 300, 80, 210, 80, "kb")
    d.node("s_parse", "代码 解析归一化结果\ncourse_id / 全称 / 亮点", 560, 80, 200, 80, "code")
    d.node("s_judge", "判断 是否可直接检索\nsingle / multiple / none", 810, 80, 200, 80, "cond")
    d.node("s_http", "HTTP 检索接口\nURL / 参数：待开发提供", 1060, 80, 210, 80, "todo")
    d.node("s_parse2", "代码 解析检索结果\nhas_result / empty / no_more / error", 1320, 80, 230, 80, "code")

    d.node("s_card", "卡片组装\n每类统一字段 + type 标识", 1320, 220, 230, 70, "code")
    d.node("s_back", "返回主流程聚合", 1060, 220, 210, 70, "answer")
    d.node("s_supp", "补充信息出口\n字段不足 → 提示补课名/城市", 560, 220, 230, 70, "answer")
    d.node("s_empty", "空 / 全部已展示出口\n按 result_state 出不同话术", 810, 220, 230, 70, "answer")

    d.node("s_note", "8 类字段契约（必填）\n课程：title/phase_no/city/start_date\n商城：title/main_image/price\n文章：title/summary/cover\n视频：title/cover/duration\n音频：title/cover/duration\n导师：avatar/name/specialty/course_count", 40, 200, 480, 130, "note")

    d.edge("se1", "s_in", "s_kb", "", E_MAIN)
    d.edge("se2", "s_kb", "s_parse", "", E_MAIN)
    d.edge("se3", "s_parse", "s_judge", "", E_MAIN)
    d.edge("se4", "s_judge", "s_http", "命中", E_MAIN)
    d.edge("se5", "s_judge", "s_supp", "none", E_DEF, exitx=0.5, exity=1, entryx=0.5, entryy=0)
    d.edge("se6", "s_http", "s_parse2", "", E_MAIN)
    d.edge("se7", "s_parse2", "s_card", "has_result", E_MAIN, exitx=0.5, exity=1, entryx=0.5, entryy=0)
    d.edge("se8", "s_parse2", "s_empty", "empty / no_more", E_DEF, exitx=0, exity=0.5, entryx=0.5, entryy=1,
           points=[(1300, 120), (1300, 320), (925, 320)])
    d.edge("se9", "s_card", "s_back", "", E_MAIN, exitx=0, exity=0.5, entryx=1, entryy=0.5)

    d.save(os.path.join(OUT_DIR, "03-v6-子流标准结构.drawio"), 1620, 420, "v6 子流标准结构")


# ---------------------------------------------------------------- 图4 数据源双通道
def build_channels():
    d = D()
    d.node("c_title", "子流检索节点的数据源选型：按「数据是否会变」分成三种通道", 40, 20, 1440, 46, "start")

    d.node("c_hA", "通道 A｜HTTP 接口\n动态数据 · 必须实时", 40, 90, 460, 66, "http")
    d.node("c_hB", "通道 B｜知识库检索\n静态元数据 · 语义召回", 530, 90, 460, 66, "kb")
    d.node("c_hC", "通道 C｜知识库召回 + HTTP 校验\n目录靠召回 · 数值靠接口", 1020, 90, 460, 66, "todo")

    A = [
        "线下课程：期数 · 开课日期 · 剩余名额",
        "线上课程：价格 · 是否在售 · 购买人数",
        "领袖营：营期 · 剩余名额 · 报名状态",
        "6Q商城：价格 · 库存 · 上下架状态",
    ]
    B = [
        "文章：标题 · 摘要 · 封面 · 跳转链接",
        "视频：标题 · 封面 · 时长 · 播放页链接",
        "音频：标题 · 封面 · 时长 · 专辑信息",
        "高EQ导师：姓名 · 擅长 · 简介 · 头像链接",
    ]
    C = [
        "6Q商城：知识库出商品目录 → 接口补价格库存",
        "线上课程：知识库出课程名 → 接口补价格",
        "线下课程：知识库出课名 → 接口出期数（现状已这么做）",
        "注意：知识库只负责「有哪些」，不负责「多少钱」",
    ]
    for i, t in enumerate(A):
        d.node("c_a%d" % i, t, 40, 176 + i * 76, 460, 62, "todo")
    for i, t in enumerate(B):
        d.node("c_b%d" % i, t, 530, 176 + i * 76, 460, 62, "ok")
    for i, t in enumerate(C):
        d.node("c_c%d" % i, t, 1020, 176 + i * 76, 460, 62, "code")

    d.node("c_parse", "统一解析节点（每类一个 code 节点）\n知识库 chunk / HTTP body → 卡片字段\n强制包含 type 与 url，缺则不出卡", 380, 520, 760, 78, "code")
    d.node("c_red", "红线\n期数 · 名额 · 价格 · 库存这类数值，只能来自 HTTP。\n知识库与模型都不得生成或推算，缺失时该字段留空、不展示。", 380, 640, 760, 76, "del")
    d.node("c_note", "为什么内容类可以用知识库\n· 文章 / 视频 / 音频 / 导师的元数据变化低频，天级同步足够\n· 检索诉求是「语义相关」而非「精确筛选」，正好是向量检索强项\n· 无需等后端排期，可先用知识库把 4 类跑通\n\n为什么商城必须走接口\n· 价格、库存、上下架是秒级变化，知识库跟不上\n· 用户要的是「能买到的」，语义召回解决不了\n· 价格区间这类结构化筛选知识库做不了", 1190, 520, 480, 200, "note")

    d.edge("ce1", "c_hA", "c_a0", "", E_DEF, exitx=0.5, exity=1, entryx=0.5, entryy=0)
    d.edge("ce2", "c_hB", "c_b0", "", E_DEF, exitx=0.5, exity=1, entryx=0.5, entryy=0)
    d.edge("ce3", "c_hC", "c_c0", "", E_DEF, exitx=0.5, exity=1, entryx=0.5, entryy=0)
    for i in range(3):
        d.edge("cae%d" % i, "c_a%d" % i, "c_a%d" % (i + 1), "", E_DEF)
        d.edge("cbe%d" % i, "c_b%d" % i, "c_b%d" % (i + 1), "", E_DEF)
        d.edge("cce%d" % i, "c_c%d" % i, "c_c%d" % (i + 1), "", E_DEF)
    d.edge("ce4", "c_a3", "c_parse", "", E_DEF, exitx=0.5, exity=1, entryx=0.1, entryy=0)
    d.edge("ce5", "c_b3", "c_parse", "", E_MAIN, exitx=0.5, exity=1, entryx=0.5, entryy=0)
    d.edge("ce6", "c_c3", "c_parse", "", E_DEF, exitx=0.5, exity=1, entryx=0.9, entryy=0)

    d.save(os.path.join(OUT_DIR, "04-数据源双通道-知识库与HTTP.drawio"), 1700, 760, "数据源双通道选型")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    build_asis()
    build_v6()
    build_subflow()
    build_channels()
