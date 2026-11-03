# -*- coding: utf-8 -*-
"""静态模拟工作流走向，验证分支逻辑（不依赖 Dify）。

用法：python scripts/simulate-dsl.py dsl/ai-search-v6.yml
"""
import sys
import types

import yaml

SRC = sys.argv[1]

TITLE = {}


def run_code(code, fn, **kw):
    m = types.ModuleType("m")
    exec(code, m.__dict__)
    return getattr(m, fn)(**kw)


def main():
    doc = yaml.safe_load(open(SRC, encoding="utf-8"))
    g = doc["workflow"]["graph"]
    nodes = {n["id"]: n for n in g["nodes"]}
    for n in g["nodes"]:
        TITLE[n["id"]] = (n["data"].get("title") or "").strip()

    out_edges = {}
    for e in g["edges"]:
        out_edges.setdefault(e["source"], []).append(e)

    parse_code = nodes["1781491262356"]["data"]["code"]
    build_code = nodes["1900000000003"]["data"]["code"]

    # 知识库样例：三类内容，带相关度分数
    KB = [
        {"content": "title: 恋爱咨询是不是骗局？\ntype: article\nsummary: 三个误区\ncover: c1\nurl: u1\n", "score": 0.86},
        {"content": "title: 亲密关系里的三个信号\ntype: video\ncover: c2\nduration: 06:12\nurl: u2\n", "score": 0.81},
        {"content": "title: 为什么我们会反复吵架\ntype: audio\ncover: c3\nduration: 18:40\nurl: u3\n", "score": 0.74},
    ]
    # 低分召回：模拟「随便说说」这类无意义输入
    KB_LOW = [
        {"content": "title: 恋爱咨询是不是骗局？\ntype: article\nsummary: 三个误区\ncover: c1\nurl: u1\n", "score": 0.12},
        {"content": "title: 亲密关系里的三个信号\ntype: video\ncover: c2\nduration: 06:12\nurl: u2\n", "score": 0.08},
    ]

    def cond(variables, c):
        sel = c["variable_selector"]
        if sel[0] == "sys":
            return True
        val = variables.get(sel[0], {}).get(sel[1])
        op = c["comparison_operator"]
        target = c["value"]
        if op == "is":
            return val == target
        if op == "is not":
            return val != target
        if op == "contains":
            return str(target) in str(val)
        return False

    def walk(start, variables, limit=80):
        path = []
        cur = start
        kb_data = variables.pop("_kb", KB)
        for _ in range(limit):
            node = nodes.get(cur)
            if not node:
                return path + ["<缺失 %s>" % cur]
            title = TITLE[cur]
            path.append(title)
            data = node["data"]
            typ = data.get("type")

            if typ == "if-else":
                nxt = None
                for case in data["cases"]:
                    ok = all(cond(variables, c) for c in case["conditions"]) \
                        if case["logical_operator"] == "and" else \
                        any(cond(variables, c) for c in case["conditions"])
                    if ok:
                        nxt = case["case_id"]
                        break
                edges = out_edges.get(cur, [])
                hit = [e for e in edges if e["sourceHandle"] == nxt] if nxt else \
                    [e for e in edges if e["sourceHandle"] == "false"]
                if not hit:
                    return path + ["<结束，无出口>"]
                if len(hit) > 1:
                    path.append("  (该出口有 %d 条边，模拟取第一条)" % len(hit))
                cur = hit[0]["target"]
                continue

            # 非分支节点：跑一下代码节点，产出变量
            if typ == "code":
                code = data.get("code", "")
                if cur == "1781491262356":
                    res = run_code(code, "main", text=variables.get("_raw", ""))
                elif cur == "1900000000003":
                    res = run_code(
                        code, "main",
                        kb_result=kb_data,
                        stub_json="[]",
                        intents=variables.get("1781491262356", {}).get("intents", ""),
                        keyword=variables.get("1781491262356", {}).get("keyword", ""),
                    )
                elif cur == "1782874059640":
                    # 课程知识库归一：有课名即视为命中单条
                    name = variables.get("1781491262356", {}).get("course_name", "")
                    res = {
                        "kb_match_state": "single" if name else "none",
                        "kb_hit": bool(name),
                        "kb_match_count": "1" if name else "0",
                        "kb_course_id": "C-1001" if name else "",
                        "kb_course_name_full": name,
                        "kb_course_highlight_text": "",
                        "kb_course_options": "",
                    }
                elif cur == "17815990321891":
                    # 期数接口解析：这里按「查得到」模拟
                    res = {
                        "success": True,
                        "result_state": "has_result",
                        "has_result": True,
                        "result_count": "3",
                        "list_json": "[]",
                        "list_json_marked": '@s_obj@[{"id":"S1","title":"《高EQ智慧父母》一阶"}]+2@e_obj@',
                        "message": "",
                    }
                elif cur == "1900000000002":
                    res = run_code(
                        code, "main",
                        intents=variables.get("1781491262356", {}).get("intents", ""),
                        keyword=variables.get("1781491262356", {}).get("keyword", ""),
                        city=variables.get("1781491262356", {}).get("city", ""),
                    )
                else:
                    res = {}
                variables.setdefault(cur, {}).update(res)

            if typ == "knowledge-retrieval":
                variables.setdefault(cur, {})["result"] = kb_data
            if typ == "llm":
                variables.setdefault(cur, {})["text"] = "（导语）"
            if typ == "answer":
                # answer 在 Dify 里不是终点，可以继续往下走
                variables.setdefault("_out", []).append(title)
                edges = out_edges.get(cur, [])
                if not edges:
                    return path
                cur = edges[0]["target"]
                continue

            edges = out_edges.get(cur, [])
            if not edges:
                return path
            cur = edges[0]["target"]
        return path + ["<超过步数上限>"]

    queries = [
        ("智慧父母一阶", '{"intents":["offline_course"],"keyword":"智慧父母一阶","social_chat":false,'
                    ' "ready":true,"slots":{"offline_course":{"course_name":"《高EQ智慧父母》一阶"}}}'),
        ("恋爱咨询", '{"intents":["article","video","audio"],"keyword":"恋爱咨询","social_chat":false,'
                 ' "ready":true,"slots":{"article":{"topic":"恋爱咨询"}}}'),
        ("你好", '{"intents":["general"],"keyword":"你好","social_chat":true,"ready":false,"slots":{}}'),
        ("夏令营", '{"intents":["leader_camp"],"keyword":"夏令营","social_chat":false,'
                ' "ready":true,"slots":{"leader_camp":{"topic":"夏令营"}}}'),
        ("广州有什么课", '{"intents":["offline_course"],"keyword":"广州有什么课","social_chat":false,'
                   ' "ready":true,"slots":{"offline_course":{"city":"广州"}}}'),
        ("智慧父母一阶有没有相关文章", '{"intents":["offline_course","article"],"keyword":"智慧父母一阶有没有相关文章",'
                            ' "social_chat":false,"ready":true,"slots":{"offline_course":'
                            '{"course_name":"《高EQ智慧父母》一阶"},"article":{"topic":"一阶"}}}'),
    ]

    # 低分召回场景单独跑：验证阈值能挡住无关内容
    variables = {"_raw": queries[0][1], "_kb": KB_LOW}
    variables["_raw"] = '{"intents":["general"],"keyword":"随便说说","social_chat":false,"ready":true,"slots":{}}'
    path = walk("1711528708197", variables)
    print("\n【随便说说（知识库只召回低分）】")
    print("  终点:", path[-1])

    for label, raw in queries:
        variables = {"_raw": raw}
        path = walk("1711528708197", variables)
        final = path[-1]
        print("\n【%s】" % label)
        print("  终点: %s" % final)
        print("  路径: " + " → ".join(p for p in path if not p.startswith("  (")))
        payload = variables.get("1900000000003", {})
        if payload.get("has_result"):
            print("  内容卡片: %s / %s" % (payload.get("types_text"), payload.get("counts_text")))


main()
