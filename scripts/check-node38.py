# -*- coding: utf-8 -*-
"""校验并试跑 3.8 代码节点（从生成的 YAML 里取，确保导出内容可执行）。"""
import io
import json
import types
import yaml

D = yaml.safe_load(io.open("dsl/ai-search-v6.yml", encoding="utf-8"))
g = D["workflow"]["graph"]
node = [n for n in g["nodes"] if n["data"].get("title", "").startswith("3.8")][0]
code = node["data"]["code"]
compile(code, "node38", "exec")

mod = types.ModuleType("node38")
exec(compile(code, "node38", "exec"), mod.__dict__)


def body(payload):
    return json.dumps(payload, ensure_ascii=False)


CASES = [
    ("线上课+领袖营+商城",
     dict(intents="online_course,leader_camp,mall_goods",
          online_course=body({"code": 200, "data": {"records": [
              {"courseId": "c1", "courseName": "智慧父母", "coverUrl": "http://x/1.png", "price": 199},
              {"courseId": "c1", "courseName": "智慧父母", "coverUrl": "http://x/1.png", "price": 199},
              {"courseId": "c2", "courseName": "青少年领袖", "price": 299},
          ]}}),
          leader_camp=body({"data": {"list": [{"campId": "p1", "campName": "8月营", "startDate": "2026-08-01"}]}}),
          mall_goods='{"result":{"rows":[{"goodsId":"g1","goodsName":"6Q笔记本","mainImage":"http://x/g.png"}]}}')),
    ("文章+视频+音频",
     dict(intents="article,video,audio",
          article=body({"data": [{"id": "a1", "title": "如何做情绪管理", "url": "http://a/1"}]}),
          video=body({"data": [{"id": "v1", "title": "三分钟讲清情绪", "duration": "3:00"}]}),
          audio=body({"data": [{"id": "au1", "title": "睡前冥想", "duration": "12:00"}]}))),
    ("接口全空",
     dict(intents="article,video", article="", video='{"data":[]}')),
    ("接口抛错文本",
     dict(intents="article", article="Bad Gateway")),
    ("仅课程意图（不该进内容链，兜底也返回空）",
     dict(intents="", article="")),
]

for name, kw in CASES:
    out = mod.main(**kw)
    blocks = json.loads(out["sections_marked"].replace("@s_obj@", "").replace("@e_obj@", "")) \
        if out["sections_marked"] else []
    print("=" * 70)
    print(name)
    print("  has_result:", out["has_result"], "| types:", out["types_text"] or "-")
    print("  counts    :", out["counts_text"] or "-")
    print("  debug     :", out["debug_text"])
    for b in blocks:
        print("   -", b["type"], b["total"], [i["title"] for i in b["items"]])
