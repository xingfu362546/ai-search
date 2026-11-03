# -*- coding: utf-8 -*-
"""静态模拟工作流走向，验证分支逻辑（不依赖 Dify）。

用法：python scripts/simulate-dsl.py dsl/ai-search-v6.yml

内容类现在是 7 个系统接口节点，这里用样例报文代替真实返回：
- HIT   ：接口返回 1~2 条，走导语 + 卡片
- EMPTY ：接口返回空列表，走「内容未找到」
"""
import json
import sys
import types

import yaml

SRC = sys.argv[1] if len(sys.argv) > 1 else "dsl/ai-search-v6.yml"

TITLE = {}

# 接口节点 -> 内容类目
API_NODES = {
    "1900000000001": "online_course",
    "1900000000002": "leader_camp",
    "1900000000003": "mentor",
    "1900000000004": "mall_goods",
    "1900000000005": "article",
    "1900000000006": "video",
    "1900000000007": "audio",
}

# 样例报文：故意用不同的包裹层级和字段名，验证 ALIAS / find_list 的兼容性
SAMPLES = {
    "online_course": {"code": 200, "data": {"records": [
        {"courseId": "c-1", "courseName": "《高EQ智慧父母》一阶", "coverUrl": "http://img/c1.png", "price": 1980},
    ]}},
    "leader_camp": {"data": {"list": [
        {"campId": "p-1", "campName": "2026 少年领袖营 8 月期", "startDate": "2026-08-01"},
    ]}},
    "mentor": {"result": {"rows": [
        {"mentorId": "m-1", "name": "林老师", "avatar": "http://img/m1.png", "specialty": "亲子沟通"},
    ]}},
    "mall_goods": {"data": [
        {"goodsId": "g-1", "goodsName": "6Q 情绪卡牌", "mainImage": "http://img/g1.png", "price": 99},
    ]},
    "article": {"data": [
        {"id": "a-1", "title": "恋爱咨询是不是骗局？", "url": "http://a/1", "summary": "三个误区"},
        {"id": "a-2", "title": "亲密关系里的三个信号", "url": "http://a/2"},
    ]},
    "video": {"data": [
        {"id": "v-1", "title": "为什么我们会反复吵架", "duration": "06:12", "url": "http://v/1"},
    ]},
    "audio": {"data": [
        {"id": "au-1", "title": "睡前十分钟：把情绪放下", "duration": "18:40", "url": "http://au/1"},
    ]},
}


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

    BUILD_ID = [i for i, n in nodes.items()
                if n["data"].get("title", "").startswith("3.8")][0]

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
        empty_api = variables.pop("_api_empty", False)

        for _ in range(limit):
            node = nodes.get(cur)
            if not node:
                return path + ["<缺失 %s>" % cur]
            path.append(TITLE[cur])
            data = node["data"]
            typ = data.get("type")

            if typ == "if-else":
                nxt = None
                for case in data["cases"]:
                    conds = case["conditions"]
                    ok = all(cond(variables, c) for c in conds) \
                        if case["logical_operator"] == "and" else \
                        any(cond(variables, c) for c in conds)
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

            # 接口节点：塞入样例报文
            if typ == "http-request":
                ctype = API_NODES.get(cur)
                if ctype:
                    payload = {"data": []} if empty_api else SAMPLES[ctype]
                    variables.setdefault(cur, {})["body"] = json.dumps(payload, ensure_ascii=False)

            # 代码节点
            if typ == "code":
                code = data.get("code", "")
                if cur == "1781491262356":
                    res = run_code(code, "main", text=variables.get("_raw", ""))
                elif cur == BUILD_ID:
                    kw = {ctype: variables.get(nid, {}).get("body", "")
                          for nid, ctype in API_NODES.items()}
                    kw["intents"] = variables.get("1781491262356", {}).get("intents", "")
                    kw["keyword"] = variables.get("1781491262356", {}).get("keyword", "")
                    res = run_code(code, "main", **kw)
                elif cur == "1782874059640":
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
                    res = {
                        "success": True,
                        "result_state": "has_result",
                        "has_result": True,
                        "result_count": "3",
                        "list_json": "[]",
                        "list_json_marked": '@s_obj@[{"id":"S1","title":"《高EQ智慧父母》一阶"}]+2@e_obj@',
                        "message": "",
                    }
                else:
                    res = {}
                variables.setdefault(cur, {}).update(res)

            if typ == "llm":
                variables.setdefault(cur, {})["text"] = "（导语）"

            if typ == "answer":
                variables.setdefault("_out", []).append(TITLE[cur])
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

    QUERIES = [
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
        ("随便说说", '{"intents":["article","video"],"keyword":"随便说说","social_chat":false,'
                 ' "ready":true,"slots":{}}'),
    ]

    failures = []

    for label, raw in QUERIES:
        for empty in (False, True):
            variables = {"_raw": raw, "_api_empty": empty}
            path = walk("1711528708197", variables)
            tag = "接口有结果" if not empty else "接口无结果"
            print("\n【%s · %s】" % (label, tag))
            print("  终点: %s" % path[-1])
            print("  路径: " + " → ".join(p for p in path if not p.startswith("  (")))
            payload = variables.get(BUILD_ID, {})
            if payload:
                print("  组装: has_result=%s types=%s counts=%s"
                      % (payload.get("has_result"), payload.get("types_text") or "-",
                         payload.get("counts_text") or "-"))
                print("  明细: %s" % (payload.get("debug_text") or "-"))

            final = path[-1]
            if empty and ("导语" in final or "分区卡片" in final):
                failures.append("%s/%s 无结果却出了卡片" % (label, tag))
            if not empty and "未找到" in final:
                failures.append("%s/%s 有结果却走未找到" % (label, tag))

    print("\n" + "=" * 60)
    if failures:
        print("异常：")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("全部用例通过")


main()
