# -*- coding: utf-8 -*-
"""把 DSL 的节点坐标渲染成 PNG 预览，用于检查重叠与连线走向。

用法：python scripts/preview-dsl.py dsl/ai-search-v6.yml output/out.png
"""
import sys
from PIL import Image, ImageDraw, ImageFont

import yaml

SRC = sys.argv[1]
DST = sys.argv[2]

COLOR = {
    "start": ("#dbeafe", "#1e40af"),
    "llm": ("#fde68a", "#92400e"),
    "code": ("#e9d5ff", "#6b21a8"),
    "if-else": ("#fecaca", "#991b1b"),
    "answer": ("#bbf7d0", "#166534"),
    "http-request": ("#bfdbfe", "#1e3a8a"),
    "knowledge-retrieval": ("#a5f3fc", "#155e75"),
}


def font(size):
    for name in ("msyh.ttc", "simhei.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype("C:/Windows/Fonts/" + name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    doc = yaml.safe_load(open(SRC, encoding="utf-8"))
    g = doc["workflow"]["graph"]
    nodes = {n["id"]: n for n in g["nodes"]}

    pad = 80
    xs0 = min(n["position"]["x"] for n in g["nodes"])
    ys0 = min(n["position"]["y"] for n in g["nodes"])
    xs1 = max(n["position"]["x"] + n["width"] for n in g["nodes"])
    ys1 = max(n["position"]["y"] + n["height"] for n in g["nodes"])

    scale = 0.75
    W = int((xs1 - xs0 + pad * 2) * scale)
    H = int((ys1 - ys0 + pad * 2) * scale)
    img = Image.new("RGB", (W, H), "#f7f6f3")
    d = ImageDraw.Draw(img)

    f_title = font(11)
    f_id = font(8)

    def tx(x):
        return int((x - xs0 + pad) * scale)

    def ty(y):
        return int((y - ys0 + pad) * scale)

    # 先画边
    for e in g["edges"]:
        s, t = nodes.get(e["source"]), nodes.get(e["target"])
        if not s or not t:
            continue
        sx = s["position"]["x"] + s["width"]
        sy = sy0 = s["position"]["y"] + s["height"] / 2
        txx = t["position"]["x"]
        tyy = t["position"]["y"] + t["height"] / 2
        if txx < sx:
            sx = s["position"]["x"]
            txx = t["position"]["x"] + t["width"]
        # 三次贝塞尔近似
        mx = (sx + txx) / 2
        pts = []
        for i in range(0, 41):
            u = i / 40.0
            x = (1 - u) ** 3 * sx + 3 * (1 - u) ** 2 * u * mx + 3 * (1 - u) * u ** 2 * mx + u ** 3 * txx
            y = (1 - u) ** 3 * sy + 3 * (1 - u) ** 2 * u * sy + 3 * (1 - u) * u ** 2 * tyy + u ** 3 * tyy
            pts.append((tx(x), ty(y)))
        d.line(pts, fill="#c084fc", width=1)

    # 再画节点
    for n in g["nodes"]:
        p = n["position"]
        x0, y0 = tx(p["x"]), ty(p["y"])
        x1, y1 = tx(p["x"] + n["width"]), ty(p["y"] + n["height"])
        fill, line = COLOR.get(n["data"].get("type"), ("#e5e7eb", "#374151"))
        d.rectangle([x0, y0, x1, y1], fill=fill, outline=line, width=1)
        title = (n["data"].get("title") or "").strip()
        parts = []
        while len(title) > 10:
            parts.append(title[:10])
            title = title[10:]
        parts.append(title)
        for i, part in enumerate(parts[:6]):
            d.text((x0 + 3, y0 + 3 + i * 12), part, fill="#111827", font=f_title)
        d.text((x0 + 3, y1 - 11), n["id"], fill="#6b7280", font=f_id)

    img.save(DST)

    # 重叠检查
    import itertools
    bad = 0
    for a, b in itertools.combinations(g["nodes"], 2):
        ax0, ay0 = a["position"]["x"], a["position"]["y"]
        ax1, ay1 = ax0 + a["width"], ay0 + a["height"]
        bx0, by0 = b["position"]["x"], b["position"]["y"]
        bx1, by1 = bx0 + b["width"], by0 + b["height"]
        if min(ax1, bx1) - max(ax0, bx0) > 0 and min(ay1, by1) - max(ay0, by0) > 0:
            bad += 1
            print("OVERLAP:", a["data"]["title"], "<->", b["data"]["title"])
    print("saved", DST, "overlaps:", bad)


main()

