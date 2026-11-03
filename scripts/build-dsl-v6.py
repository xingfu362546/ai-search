# -*- coding: utf-8 -*-
"""
以生产 DSL 为基线生成 v6 版本。

原则：
1. 线下课程链路（2.15A→2.15B→2.15C→2.15/2.15D→2.16→2.17→2.9/2.9B→2.13）原样保留，只改入口。
2. 2.2 意图 Prompt 换成 8 类数组版，2.3 解析节点同时输出旧字段（课程链不改）。
3. 新增内容类分支：知识库检索 → 占位接口 → 组装分区卡 → 导语 → 回复。
4. 删除「兜底 / 去全部看看」，改为「没找到」。

用法：
  python scripts/build-dsl-v6.py "<生产 yml 路径>" "dsl/ai-search-v6.yml"
"""
import sys
import os
import copy
import uuid

import yaml

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Lenovo\Desktop\（生产勿动）AI超级搜索（加课程说明）.yml"
DST = sys.argv[2] if len(sys.argv) > 2 else "dsl/ai-search-v6.yml"

N_START = "1711528708197"
N_CLEAN = "1783158943079"
N_SHOWN = "1783479266965"
N_LLM = "1781233179039"
N_PARSE = "1781491262356"
N_ROUTE = "1781490823260"
N_COURSE_KB = "1782818657079"
N_COURSE_KB_PARSE = "1782874059640"
N_COURSE_KB_IF = "1782874247920"
N_HTTP_COURSE = "17815990321890"
N_HTTP_GENERAL = "17829761329860"
N_PARSE_RESULT = "17815990321891"
N_RESULT_IF = "17815990321892"
N_GUIDE = "1781598510471"
N_GUIDE_B = "17829793634240"
N_EMPTY = "17815990321893"
N_NO_MORE = "17820974321910"
N_UNIFIED = "1782111091579"
N_NEED_MORE = "1781505092291"
N_CHAT_LLM = "17821201509870"
N_CHAT_ANS = "1782120560448"
N_ERROR = "1782129629050"
N_FALLBACK = "1782113851054"

# 内容类 7 个接口（系统本身接口，URL 待回填）
N_HTTP_ONLINE = "1900000000001"
N_HTTP_CAMP = "1900000000002"
N_HTTP_MENTOR = "1900000000003"
N_HTTP_GOODS = "1900000000004"
N_HTTP_ARTICLE = "1900000000005"
N_HTTP_VIDEO = "1900000000006"
N_HTTP_AUDIO = "1900000000007"
N_CONTENT_BUILD = "1900000000010"
N_CONTENT_IF = "1900000000011"
N_CONTENT_GUIDE = "1900000000012"
N_CONTENT_ANS = "1900000000013"
N_CONTENT_NONE = "1900000000014"
N_ROUTE_B = "1900000000020"
CASE_COURSE = str(uuid.uuid4())
CASE_COURSE_NO_NAME = str(uuid.uuid4())
CASE_CONTENT = str(uuid.uuid4())
CASE_CHAT = str(uuid.uuid4())
CASE_CONTENT_B = str(uuid.uuid4())
CASE_CONTENT_RESULT = str(uuid.uuid4())

sys_prompt = """你是 6Q APP 的 AI 超级搜索助手。

只做两件事：
1. 判断用户当前问题命中了哪几类内容
2. 抽取各类检索需要的字段

不回答业务内容，不生成任何实时信息。

【运行时变量】
- query：用户当前问题
- history：前文摘要
- shown_session_ids：已展示结果 ID 摘要
- user_city：用户定位城市，可为空
- current_date：当前日期

【输出要求】
只输出一个 JSON 对象；不要输出解释、说明、前后缀或 Markdown。

【intents 取值】
只允许以下 9 个值，可多选：
- online_course   线上课程
- offline_course  线下课程 / 期数 / 报读
- leader_camp     领袖营 / 夏令营 / 冬令营 / 营期
- mentor          高EQ导师 / 老师
- mall_goods      6Q商城 / 商品 / 盲盒
- article         文章
- video           视频
- audio           音频
- general         泛搜兜底

【intents 判定】
- 一句可以命中多类，输出数组，例如“恋爱咨询” -> ["article","video","audio"]。
- 按内容本身判断，不要因为某个词往课程上靠。
- 只有完全无法归类时，才输出 ["general"]。
- 纯问候、致谢、告别、闲聊 -> intents 输出 ["general"]，且 social_chat = true。

各类触发词参考：
- offline_course：课程、报读、报名、开课、期数、第几期、还有吗、附近
- online_course：线上课、网课、视频课、线上学习
- leader_camp：夏令营、冬令营、集训营、亲子营、营期、领袖营、研学
- mentor：导师、老师、讲师、教练、谁教
- mall_goods：商城、买、商品、价格、盲盒、周边、书籍
- article：文章、资讯、干货、怎么写的、有没有讲
- video：视频、短片、讲解、看视频
- audio：音频、听、收听、电台、录音

【course_name 固定映射】
只允许使用以下映射，不得自行新增或猜测：
- “一阶” -> 《高EQ智慧父母》一阶
- “二阶” -> 《高EQ智慧父母》(二阶)
- “进阶” -> 进阶
- “高AQ” -> 《高AQ智慧父母》
- “高IQ” -> 《高IQ智慧父母》
- “高CQ” -> 《高CQ智慧父母》
- “高SQ” -> 《高SQ智慧父母》
- “高RQ” -> 《高RQ智慧父母》基础班
- “高RQ 进阶” -> 《高RQ智慧父母》进阶班
- “亲子沟通心灵密码”“分享会” -> 《亲子沟通心灵密码》分享会
- “沙龙” -> 6Q读书沙龙
- “创意沙龙” -> 6Q创意沙龙（定制版）
- “恩爱夫妻工作坊”“恩爱夫妻” -> 高EQ亲密关系工作坊

强约束：
- 明确课程全称优先于泛称映射。
- “专业课”单独出现时，不得判断为一阶或二阶。
- 除以上规则外，不要改动 course_name。

【user_city 使用禁令】
user_city 仅用于“附近 / 本地”类定位搜索。
当前 query 不含“我附近”“附近”“本地”“离我近一点”时：
- 完全忽略 user_city，不得令 city = user_city。
- city 只能来自当前 query 明确城市，或 history 明确继承。

【城市与附近规则】
1. 当前 query 明确出现城市名：city = 该城市，location_mode = city，不继承 history.city。
2. 当前 query 含附近表达：location_mode = nearby；user_city 非空则 city = user_city，否则 city = ""。
3. 当前 query 无城市也无附近表达：忽略 user_city；history 有明确 city 则继承，否则 city = ""，location_mode = none。
4. 不得根据 user_city、示例或常识猜测城市。

【其他字段】
- keyword：输出当前 query 原文，不改写、不截断。
- instructor_name：提取导师姓名；当前没有但 history 有明确值时继承。
- phase_no：“533期”“第533期” -> "533"；“第几期” -> ""。
- date_from / date_to：格式 YYYY-MM-DD。
  - 近期：未来 30 天；这几天：未来 7 天；这周：本周一至周日
  - 这个月：本月 1 日至月末；今年：current_date 至当年 12 月 31 日
  - 未明确时间时，线下课程默认近期
- 各内容类 topic：把用户的检索意图压缩成 2~8 个字的关键词，用于知识库检索；没有则空字符串。

【ready 与 missing】
- ready 表示整体是否可检索：只要有一类能查即为 true。
- social_chat = true 时 ready = false。
- intents 为 ["general"] 时 ready = true（走泛搜）。
- missing 仅在完全无法检索时填写，用英文逗号分隔。

【续聊规则】
- 当前 query 明确条件优先于 history。
- history 只补全缺失字段，不编造、不覆盖当前明确条件。
- 冲突时以当前 query 为准。

【输出格式】
所有字段必须输出；无值统一输出空字符串，不输出 null。
最终只输出一个 JSON 对象。"""

user_prompt = (
    "请根据以下输入进行意图识别和字段提取：\n\n"
    "query: {{#sys.query#}}\n"
    "history: {{#1783158943079.clean_history#}}\n"
    "shown_session_ids: {{#1711528708197.shown_session_ids#}}\n"
    "user_city: {{#1711528708197.user_city#}}\n"
    "current_date: {{#1711528708197.current_date#}}\n"
    "session_id: {{#1711528708197.session_id#}}\n"
    "user_id: {{#1711528708197.user_id#}}\n"
)

parse_code = r'''import json
import re

CONTENT_TYPES = (
    "online_course", "offline_course", "leader_camp", "mentor",
    "mall_goods", "article", "video", "audio",
)

EMPTY = {
    "intents": "general",
    "has_course": False,
    "has_content": False,
    "social_chat": False,
    "ready": False,
    "intent": "other",
    "ready_for_api": False,
    "keyword": "",
    "course_category": "",
    "course_id": "",
    "course_name": "",
    "city": "",
    "location_mode": "",
    "instructor_name": "",
    "phase_no": "",
    "date_from": "",
    "date_to": "",
    "missing_fields": "",
    "confidence": "",
    "reply_mode": "general_search",
    "topic": "",
}


def to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return bool(value)


def main(text: str = "", history: str = "") -> dict:
    raw = (text or "").strip()

    m = re.search(r"```(?:json)?\s*\n?(.*?)```", raw, re.DOTALL)
    if m:
        raw = m.group(1).strip()

    if raw and not raw.startswith(("{", "[")):
        j = re.search(r"\{.*\}", raw, re.DOTALL)
        if j:
            raw = j.group(0)

    if not raw:
        return dict(EMPTY)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return dict(EMPTY)

    # 兼容模型把 JSON 再包一层 text 的情况
    if isinstance(data.get("text"), str) and data["text"].strip().startswith("{"):
        try:
            data = json.loads(data["text"].strip())
        except json.JSONDecodeError:
            pass

    # ---- intents 归一化：数组 / 字符串 / 旧版单值都兼容 ----
    raw_intents = data.get("intents")
    if raw_intents is None:
        legacy = str(data.get("intent", "") or "")
        raw_intents = [legacy] if legacy else []

    if isinstance(raw_intents, str):
        raw_intents = re.split(r"[,，、\s]+", raw_intents)

    intents = []
    for item in raw_intents or []:
        value = str(item or "").strip()
        if value == "course_enroll":
            value = "offline_course"
        if value and value not in intents:
            intents.append(value)

    if not intents:
        intents = ["general"]

    social_chat = to_bool(data.get("social_chat", False))

    has_course = "offline_course" in intents
    content_intents = [i for i in intents if i in CONTENT_TYPES and i != "offline_course"]
    has_content = bool(content_intents)
    if "general" in intents:
        has_content = True
    # 闲聊不触发任何检索
    if social_chat:
        has_content = False

    # ---- 课程链沿用的旧字段 ----
    slots = data.get("slots") or {}
    course_slots = slots.get("offline_course") or {}

    def pick(key, default=""):
        value = data.get(key)
        if value in (None, ""):
            value = course_slots.get(key)
        if value is None:
            return default
        return str(value)

    keyword = str(data.get("keyword", "") or "")
    course_name = pick("course_name")
    city = pick("city")
    location_mode = pick("location_mode")
    instructor_name = pick("instructor_name")
    phase_no = pick("phase_no")
    date_from = pick("date_from")
    date_to = pick("date_to")
    course_id = pick("course_id")

    first_content = content_intents[0] if content_intents else ""
    topic = ""
    if first_content:
        block = slots.get(first_content) or {}
        if isinstance(block, dict):
            topic = str(block.get("topic", "") or "")
            if not topic:
                for key in ("mentor_name", "album", "goods_name", "camp_name", "author"):
                    value = str(block.get(key, "") or "").strip()
                    if value:
                        topic = value
                        break
    # 检索词兜底：永远不能为空，否则知识库会召回全库
    if not topic:
        topic = keyword

    reply_mode = str(data.get("reply_mode", "") or "")
    if not reply_mode:
        if social_chat:
            reply_mode = "social_chat"
        elif course_name:
            reply_mode = "search_course"
        elif instructor_name:
            reply_mode = "search_teacher"
        elif city:
            reply_mode = "search_city"
        elif has_course:
            reply_mode = "general_search"
        else:
            reply_mode = "general_search"

    ready = to_bool(data.get("ready", data.get("ready_for_api", False)))
    if social_chat:
        ready = False

    missing = data.get("missing") or data.get("missing_fields") or []
    if isinstance(missing, list):
        missing_fields = ",".join(str(x) for x in missing if str(x).strip())
    else:
        missing_fields = str(missing or "")

    confidence = data.get("confidence", "")
    confidence = "" if confidence is None else str(confidence)

    return {
        "intents": ",".join(intents),
        "has_course": has_course,
        "has_content": has_content,
        "social_chat": social_chat,
        "ready": ready,
        "intent": "course_enroll" if has_course else "other",
        "ready_for_api": to_bool(data.get("ready_for_api", False)),
        "keyword": keyword,
        "course_category": "offline_course" if has_course else "",
        "course_id": course_id,
        "course_name": course_name,
        "city": city,
        "location_mode": location_mode,
        "instructor_name": instructor_name,
        "phase_no": phase_no,
        "date_from": date_from,
        "date_to": date_to,
        "missing_fields": missing_fields,
        "confidence": confidence,
        "reply_mode": reply_mode,
        "topic": topic,
    }
'''

build_code = r'''import json

ORDER = [
    ("online_course", "线上课程"),
    ("offline_course", "线下课程"),
    ("leader_camp", "领袖营"),
    ("mentor", "高EQ导师"),
    ("mall_goods", "6Q商城"),
    ("article", "文章"),
    ("video", "视频"),
    ("audio", "音频"),
]
LABEL = dict(ORDER)
PER_TYPE_LIMIT = 3

# 各接口字段名不统一，这里做别名映射。
# 接口回填后若字段不在下表，把实际字段名补进对应元组即可，不用改逻辑。
ALIAS = {
    "id": ("id", "courseId", "goodsId", "articleId", "videoId", "audioId",
           "mentorId", "campId", "periodId", "code"),
    "title": ("title", "name", "goodsName", "courseName", "articleTitle",
              "videoTitle", "audioTitle", "campName", "periodName", "mentorName"),
    "cover": ("cover", "coverUrl", "mainImage", "image", "img", "picUrl",
              "avatar", "thumb", "thumbnail"),
    "url": ("url", "link", "detailUrl", "jumpUrl", "href", "shareUrl"),
    "summary": ("summary", "desc", "description", "intro", "brief", "digest"),
    "price": ("price", "salePrice", "sellPrice", "currentPrice", "payPrice"),
    "duration": ("duration", "length", "videoTime", "audioTime", "timeLength"),
    "author": ("author", "authorName", "writer", "teacherName"),
    "specialty": ("specialty", "goodAt", "expertise", "tag", "tags"),
}

# 接口可能把列表包在任意一层，按以下 key 逐层找
LIST_KEYS = ("data", "result", "list", "records", "rows", "items", "content", "voList")


def to_payload(body):
    if isinstance(body, (dict, list)):
        return body
    if isinstance(body, str) and body.strip():
        try:
            return json.loads(body)
        except (TypeError, ValueError):
            return None
    return None


def find_list(payload, depth=0):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and depth < 4:
        for key in LIST_KEYS:
            if key in payload:
                found = find_list(payload[key], depth + 1)
                if found:
                    return found
        for value in payload.values():
            if isinstance(value, dict):
                found = find_list(value, depth + 1)
                if found:
                    return found
    return []


def pick(raw, name):
    for key in ALIAS[name]:
        value = raw.get(key)
        if value not in (None, "", []):
            return value
    return ""


def normalize(raw, ctype):
    if not isinstance(raw, dict):
        return None
    item = {
        "id": str(pick(raw, "id") or "").strip(),
        "type": ctype,
        "title": str(pick(raw, "title") or "").strip(),
        "cover": str(pick(raw, "cover") or "").strip(),
        "url": str(pick(raw, "url") or "").strip(),
        "summary": str(pick(raw, "summary") or "").strip(),
        "author": str(pick(raw, "author") or "").strip(),
        "price": str(pick(raw, "price") or "").strip(),
        "duration": str(pick(raw, "duration") or "").strip(),
        "specialty": str(pick(raw, "specialty") or "").strip(),
    }
    # 无标题无法出卡；无 id 无法去重与跳转
    if not item["title"] or not item["id"]:
        return None
    return item


def main(online_course="", leader_camp="", mentor="", mall_goods="",
         article="", video="", audio="", intents="", keyword=""):
    wanted = [x.strip() for x in (intents or "").split(",") if x.strip()]
    if "general" in wanted or not wanted:
        wanted = [k for k, _ in ORDER]

    bodies = {
        "online_course": online_course,
        "leader_camp": leader_camp,
        "mentor": mentor,
        "mall_goods": mall_goods,
        "article": article,
        "video": video,
        "audio": audio,
    }

    sections = {k: [] for k, _ in ORDER}
    seen = set()
    raw_counts = {}

    for ctype, _ in ORDER:
        if ctype == "offline_course":
            continue                      # 线下课程走既有期数链，不重复查
        if ctype not in wanted:
            continue
        rows = find_list(to_payload(bodies.get(ctype)))
        raw_counts[ctype] = len(rows)
        for raw in rows:
            item = normalize(raw, ctype)
            if not item:
                continue
            key = (ctype, item["id"])
            if key in seen:
                continue
            seen.add(key)
            sections[ctype].append(item)

    blocks = []
    counts = []
    for ctype, label in ORDER:
        items = sections[ctype][:PER_TYPE_LIMIT]
        if not items:
            continue
        blocks.append({"type": ctype, "total": len(items), "items": items})
        counts.append("%s %d" % (label, len(items)))

    # 排查用：每个类目 出卡数/接口原始条数
    debug = "、".join(
        "%s %d/%d" % (LABEL[k], len(sections[k]), raw_counts.get(k, 0))
        for k in wanted if k != "offline_course"
    )

    if not blocks:
        return {
            "sections_marked": "",
            "has_result": False,
            "counts_text": "",
            "types_text": "",
            "state": "empty",
            "debug_text": debug,
        }

    return {
        "sections_marked": "@s_obj@" + json.dumps(blocks, ensure_ascii=False) + "@e_obj@",
        "has_result": True,
        "counts_text": "、".join(counts),
        "types_text": "、".join(LABEL[b["type"]] for b in blocks),
        "state": "has_result",
        "debug_text": debug,
    }
'''

guide_system = """你是 6Q APP 的搜索结果导语生成器。

根据本次命中的内容类目，写 1~2 句中文导语，放在卡片列表上方。

要求：
1. 只用命中的类目名与用户关键词，不要罗列条数以外的细节。
2. 不要编造任何内容，不要提及未被问到的价格、名额、日期。
3. 不要复述字段名，不要输出 JSON，不要输出 Markdown。
4. 结尾不要追加任何跳转引导、道歉或能力边界说明。
5. 语气自然、简短，像助手在交付结果。

示例：
- 仅文章：为你整理了几篇和「恋爱咨询」相关的文章：
- 文章+视频+音频：关于「恋爱咨询」，我找到了相关的文章、视频和音频：
- 多类且含课程：先为你列出课程信息，另外还有这些文章和视频可以参考："""

guide_user = "用户关键词：{{#1781491262356.keyword#}}\n命中类目：{{#1900000000010.types_text#}}\n各类条数：{{#1900000000010.counts_text#}}"


def load():
    with open(SRC, encoding="utf-8") as f:
        return yaml.safe_load(f)


def node_index(graph):
    return {n["id"]: n for n in graph["nodes"]}


def new_node(nid, data, x, y, w=242, h=90):
    return {
        "data": data,
        "height": h,
        "id": nid,
        "position": {"x": x, "y": y},
        "positionAbsolute": {"x": x, "y": y},
        "selected": False,
        "sourcePosition": "right",
        "targetPosition": "left",
        "type": "custom",
        "width": w,
    }


def edge(src, dst, handle="source"):
    return {
        "data": {
            "isInIteration": False,
            "isInLoop": False,
            "sourceType": "custom",
            "targetType": "custom",
        },
        "id": "%s-%s-%s" % (src, handle, dst),
        "selected": False,
        "source": src,
        "sourceHandle": handle,
        "target": dst,
        "targetHandle": "target",
        "type": "custom",
        "zIndex": 0,
    }


def main():
    doc = load()
    graph = doc["workflow"]["graph"]
    NL = chr(10)
    NOT_FOUND_TEXT = (
        "没找到和「{{#1781491262356.keyword#}}」相关的内容，换个说法试试～" + NL
        + "@hsy{{#1781491262356.keyword#}}@_hsy"
    )

    nodes = node_index(graph)

    # ---------- 1. 意图节点 ----------
    llm = nodes[N_LLM]["data"]
    llm["model"]["completion_params"]["temperature"] = 0.1
    llm["prompt_template"][0]["text"] = sys_prompt
    llm["prompt_template"][1]["text"] = user_prompt
    llm["title"] = "2.2 LLM-意图识别 v6（8 类）"

    # ---------- 2. 解析节点 ----------
    parse = nodes[N_PARSE]["data"]
    parse["code"] = parse_code
    parse["title"] = "2.3 代码-解析意图 v6"
    parse["outputs"] = {}
    for key, kind in [
        ("intents", "string"), ("has_course", "boolean"), ("has_content", "boolean"),
        ("social_chat", "boolean"), ("ready", "boolean"),
        ("intent", "string"), ("ready_for_api", "boolean"), ("keyword", "string"),
        ("course_category", "string"), ("course_id", "string"), ("course_name", "string"),
        ("city", "string"), ("location_mode", "string"), ("instructor_name", "string"),
        ("phase_no", "string"), ("date_from", "string"), ("date_to", "string"),
        ("missing_fields", "string"), ("confidence", "string"),
        ("reply_mode", "string"), ("topic", "string"),
    ]:
        parse["outputs"][key] = {"children": None, "type": kind}

    # ---------- 3. 主路由 ----------
    route = nodes[N_ROUTE]["data"]
    route["title"] = "2.4 条件-主路由 v6"

    def cond(var, value, kind="boolean", op="is"):
        return {
            "comparison_operator": op,
            "id": str(uuid.uuid4()),
            "value": value,
            "varType": kind,
            "variable_selector": [N_PARSE, var],
        }

    route["cases"] = [
        {
            "case_id": CASE_COURSE,
            "conditions": [
                cond("has_course", True),
                cond("course_name", "", "string", "is not"),
            ],
            "id": CASE_COURSE,
            "logical_operator": "and",
        },
        {
            "case_id": CASE_COURSE_NO_NAME,
            "conditions": [
                cond("has_course", True),
                cond("course_name", "", "string", "is"),
            ],
            "id": CASE_COURSE_NO_NAME,
            "logical_operator": "and",
        },
        {
            "case_id": CASE_CONTENT,
            "conditions": [cond("has_content", True)],
            "id": CASE_CONTENT,
            "logical_operator": "and",
        },
        {
            "case_id": CASE_CHAT,
            "conditions": [cond("social_chat", True)],
            "id": CASE_CHAT,
            "logical_operator": "and",
        },
    ]
    route["desc"] = (
        "CASE1 课程名明确 -> 2.15A 知识库归一再查期数\n"
        "CASE2 只有城市/导师 -> 2.15D 直接按条件查期数\n"
        "CASE3 命中内容类 -> 3.1~3.7 系统接口检索链\n"
        "CASE4 闲聊 -> 2.18\n"
        "ELSE -> 没找到"
    )

    # ---------- 4. 兜底改写 ----------
    fb = nodes[N_FALLBACK]["data"]
    fb["title"] = "没找到内容"
    fb["answer"] = (
        "没找到和「{{#1781491262356.keyword#}}」相关的内容，换个说法试试～\n"
        "@hsy{{#1781491262356.keyword#}}@_hsy"
    )

    # ---------- 5. 内容链：7 个系统接口 ----------
    BODY_TMPL = (
        "{\n"
        '  "userId": {{#1711528708197.user_id#}},\n'
        '  "sessionId": {{#1711528708197.session_id#}},\n'
        '  "keyword": "{{#1781491262356.keyword#}}",\n'
        '  "city": "{{#1781491262356.city#}}",\n'
        '  "page": 1,\n'
        '  "size": 20\n'
        "}"
    )

    DESC_TMPL = (
        "【待回填】%s\n"
        "需回填：接口地址、请求方式、鉴权、入参、出参\n"
        "出参要求：%s\n"
        "接口返回分页对象时，3.8 会自动取第一层列表；"
        "字段名不一致时改 3.8 的 ALIAS 映射，不要改本节点结构"
    )

    def make_http(nid, title, ctype, url_ph, field_hint):
        body = BODY_TMPL
        return {
            "authorization": {"config": None, "type": "no-auth"},
            "body": {
                "data": [{"id": "kv-" + nid, "key": "", "type": "text", "value": body}],
                "type": "json",
            },
            "desc": DESC_TMPL % (url_ph, field_hint),
            "headers": "Content-Type:application/json",
            "isInIteration": False,
            "isInLoop": False,
            "method": "post",
            "params": "",
            "retry_config": {"max_retries": 3, "retry_enabled": False, "retry_interval": 100},
            "selected": False,
            "ssl_verify": True,
            "timeout": {"connect": 10, "max_connect_timeout": 0, "max_read_timeout": 0,
                        "max_write_timeout": 0, "read": 10, "write": 10},
            "title": title,
            "type": "http-request",
            "url": url_ph,
            "variables": [],
        }

    CONTENT_APIS = [
        (N_HTTP_ONLINE, "3.1 HTTP-线上课程 · 待回填", "online_course",
         "https://FILL-ME.example.com/api/online-course/list",
         "id、title、cover、price"),
        (N_HTTP_CAMP, "3.2 HTTP-领袖营 · 待回填", "leader_camp",
         "https://FILL-ME.example.com/api/leader-camp/periods",
         "id、title、cover、campType、startDate"),
        (N_HTTP_MENTOR, "3.3 HTTP-高EQ导师 · 待回填", "mentor",
         "https://FILL-ME.example.com/api/mentor/list",
         "id、name、avatar、specialty"),
        (N_HTTP_GOODS, "3.4 HTTP-6Q商城 · 待回填", "mall_goods",
         "https://FILL-ME.example.com/api/mall/goods",
         "id、title、mainImage、price"),
        (N_HTTP_ARTICLE, "3.5 HTTP-文章 · 待回填", "article",
         "https://FILL-ME.example.com/api/article/list",
         "id、title、cover、summary、url"),
        (N_HTTP_VIDEO, "3.6 HTTP-视频 · 待回填", "video",
         "https://FILL-ME.example.com/api/video/list",
         "id、title、cover、duration、url"),
        (N_HTTP_AUDIO, "3.7 HTTP-音频 · 待回填", "audio",
         "https://FILL-ME.example.com/api/audio/list",
         "id、title、cover、duration、url"),
    ]

    build_data = {
        "code": build_code,
        "code_language": "python3",
        "desc": "7 个接口的 body -> 按 type 分组、去重、组装分区卡片",
        "outputs": {
            "sections_marked": {"children": None, "type": "string"},
            "has_result": {"children": None, "type": "boolean"},
            "counts_text": {"children": None, "type": "string"},
            "types_text": {"children": None, "type": "string"},
            "state": {"children": None, "type": "string"},
            "debug_text": {"children": None, "type": "string"},
        },
        "retry_config": {"max_retries": 3, "retry_enabled": False, "retry_interval": 1000},
        "selected": False,
        "title": "3.8 代码-解析与组装卡片",
        "type": "code",
        "variables": [
            {"value_selector": [nid, "body"], "value_type": "string", "variable": ctype}
            for nid, _, ctype, _, _ in CONTENT_APIS
        ] + [
            {"value_selector": [N_PARSE, "intents"], "value_type": "string", "variable": "intents"},
            {"value_selector": [N_PARSE, "keyword"], "value_type": "string", "variable": "keyword"},
        ],
    }

    guide_data = {
        "context": {"enabled": False, "variable_selector": []},
        "isInIteration": False,
        "isInLoop": False,
        "model": {
            "completion_params": {"temperature": 0.3},
            "mode": "chat",
            "name": "qwen3.6-flash-2026-04-16",
            "provider": "langgenius/tongyi/tongyi",
        },
        "prompt_config": {"jinja2_variables": []},
        "prompt_template": [
            {"id": str(uuid.uuid4()), "role": "system", "text": guide_system},
            {"edition_type": "basic", "id": str(uuid.uuid4()), "jinja2_text": "", "role": "user",
             "text": guide_user},
        ],
        "selected": False,
        "title": "3.10 LLM-内容导语",
        "type": "llm",
        "vision": {"enabled": False},
    }

    ans_data = {
        "answer": ("{{#%s.text#}}" + NL + "{{#%s.sections_marked#}}") % (N_CONTENT_GUIDE, N_CONTENT_BUILD),
        "selected": False,
        "title": "3.11 回复-内容分区卡片",
        "type": "answer",
        "variables": [],
    }

    none_data = {
        "answer": NOT_FOUND_TEXT,
        "selected": False,
        "title": "3.12 回复-内容未找到",
        "type": "answer",
        "variables": [],
    }

    route_b = {
        "cases": [
            {
                "case_id": CASE_CONTENT_B,
                "conditions": [cond("has_content", True)],
                "id": CASE_CONTENT_B,
                "logical_operator": "and",
            }
        ],
        "desc": "命中内容类才继续；纯课程查询在此结束",
        "selected": False,
        "title": "2.4B 条件-是否检索内容类",
        "type": "if-else",
    }

    content_if = {
        "cases": [
            {
                "case_id": CASE_CONTENT_RESULT,
                "conditions": [{
                    "comparison_operator": "is",
                    "id": str(uuid.uuid4()),
                    "value": True,
                    "varType": "boolean",
                    "variable_selector": [N_CONTENT_BUILD, "has_result"],
                }],
                "id": CASE_CONTENT_RESULT,
                "logical_operator": "and",
            }
        ],
        "desc": "有结果才出导语和卡片；无结果直接走未找到，避免空导语",
        "selected": False,
        "title": "3.9 条件-内容是否有结果",
        "type": "if-else",
    }

    new_nodes = [new_node(N_ROUTE_B, route_b, 0, 0, 240, 200)]
    for nid, title, ctype, url_ph, hint in CONTENT_APIS:
        new_nodes.append(new_node(nid, make_http(nid, title, ctype, url_ph, hint), 0, 0, 240, 120))
    new_nodes += [
        new_node(N_CONTENT_BUILD, build_data, 0, 0, 240, 130),
        new_node(N_CONTENT_IF, content_if, 0, 0, 240, 90),
        new_node(N_CONTENT_GUIDE, guide_data, 0, 0, 240, 110),
        new_node(N_CONTENT_ANS, ans_data, 0, 0, 240, 90),
        new_node(N_CONTENT_NONE, none_data, 0, 0, 240, 90),
    ]

    keep_ids = set(nodes.keys())
    graph["nodes"] = [n for n in graph["nodes"] if n["id"] in keep_ids] + new_nodes

    # ---------- 6. 重连边 ----------
    course_edges = [
        (N_COURSE_KB, N_COURSE_KB_PARSE, "source"),
        (N_COURSE_KB_PARSE, N_COURSE_KB_IF, "source"),
        (N_COURSE_KB_IF, N_HTTP_COURSE, "true"),
        (N_COURSE_KB_IF, N_HTTP_COURSE, "1c828d14-e08c-46c0-a7c1-c8b91253451d"),
        (N_COURSE_KB_IF, N_NEED_MORE, "false"),
        (N_COURSE_KB_IF, N_NEED_MORE, "cf02afda-72e2-42c2-8122-3a4da74f7b91"),
        (N_HTTP_COURSE, N_PARSE_RESULT, "source"),
        (N_HTTP_GENERAL, N_PARSE_RESULT, "source"),
        (N_PARSE_RESULT, N_RESULT_IF, "source"),
        (N_RESULT_IF, N_GUIDE, "true"),
        (N_RESULT_IF, N_ERROR, "false"),
        (N_RESULT_IF, N_NO_MORE, "d1b98a85-cbf4-4884-8ff9-6f4b08d56d78"),
        (N_RESULT_IF, N_EMPTY, "94bf1b3b-17ad-4f7a-8e54-587f5a5bbfc0"),
        (N_RESULT_IF, N_GUIDE_B, "756be1c8-bbc9-43c4-a997-7451ee96b1c7"),
        (N_GUIDE, N_UNIFIED, "source"),
        (N_GUIDE_B, N_UNIFIED, "source"),
        (N_CHAT_LLM, N_CHAT_ANS, "source"),
    ]

    content_edges = [
        (N_ROUTE_B, N_HTTP_ONLINE, CASE_CONTENT_B),
        (N_HTTP_ONLINE, N_HTTP_CAMP, "source"),
        (N_HTTP_CAMP, N_HTTP_MENTOR, "source"),
        (N_HTTP_MENTOR, N_HTTP_GOODS, "source"),
        (N_HTTP_GOODS, N_HTTP_ARTICLE, "source"),
        (N_HTTP_ARTICLE, N_HTTP_VIDEO, "source"),
        (N_HTTP_VIDEO, N_HTTP_AUDIO, "source"),
        (N_HTTP_AUDIO, N_CONTENT_BUILD, "source"),
        (N_CONTENT_BUILD, N_CONTENT_IF, "source"),
        (N_CONTENT_IF, N_CONTENT_GUIDE, CASE_CONTENT_RESULT),
        (N_CONTENT_IF, N_CONTENT_NONE, "false"),
        (N_CONTENT_GUIDE, N_CONTENT_ANS, "source"),
    ]

    edges = [
        edge(N_START, N_CLEAN, "source"),
        edge(N_CLEAN, N_LLM, "source"),
        edge(N_LLM, N_PARSE, "source"),
        edge(N_PARSE, N_SHOWN, "source"),
        edge(N_SHOWN, N_ROUTE, "source"),
        # 主路由
        edge(N_ROUTE, N_COURSE_KB, CASE_COURSE),
        edge(N_ROUTE, N_HTTP_GENERAL, CASE_COURSE_NO_NAME),
        edge(N_ROUTE, N_ROUTE_B, CASE_CONTENT),
        edge(N_ROUTE, N_CHAT_LLM, CASE_CHAT),
        edge(N_ROUTE, N_FALLBACK, "false"),
    ]

    for s, t, h in course_edges + content_edges:
        edges.append(edge(s, t, h))

    # 课程链终点补内容分支
    for terminal in (N_UNIFIED, N_NO_MORE, N_ERROR, N_NEED_MORE):
        edges.append(edge(terminal, N_ROUTE_B, "source"))


    graph["edges"] = edges

    # ---------- 7. 元信息 ----------
    doc["app"]["name"] = "AI超级搜索 v6（全站 8 类）"
    doc["app"]["description"] = "6Q 全站智能搜索 v6：8 类内容按意图命中，内容类走系统接口，课程走既有期数接口"

    os.makedirs(os.path.dirname(DST) or ".", exist_ok=True)

    # ---------- 8. 显式布局：分泳道摆放，避免与旧节点混在一起 ----------
    apply_layout(graph)

    with open(DST, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=1000)

    print("wrote", DST)
    print("nodes", len(graph["nodes"]), "edges", len(graph["edges"]))


# 泳道布局：(x, y)。入口在最左，课程链横向展开，内容链在右侧单独一条，课程分支出口收成一列。
LAYOUT = {
    # 入口
    N_START: (-900, -133),
    N_CLEAN: (-580, -25),
    N_SHOWN: (-280, -55),
    N_LLM: (20, -43),
    N_PARSE: (300, -39),
    N_ROUTE: (580, -410),
    # 课程链主路
    N_COURSE_KB: (980, -44),
    N_COURSE_KB_PARSE: (1280, -25),
    N_COURSE_KB_IF: (1580, -183),
    N_HTTP_GENERAL: (1880, -285),
    N_HTTP_COURSE: (1880, -67),
    N_PARSE_RESULT: (2180, -25),
    N_RESULT_IF: (2480, -353),
    N_GUIDE: (2780, -43),
    N_GUIDE_B: (2780, 100),
    N_UNIFIED: (3080, -73),
    # 课程分支出口（收成一列）
    N_EMPTY: (2780, 560),
    N_NO_MORE: (2780, 900),
    N_ERROR: (2780, 1180),
    N_NEED_MORE: (2780, 1460),
    # 闲聊与兜底
    N_CHAT_LLM: (980, 620),
    N_CHAT_ANS: (1280, 500),
    N_FALLBACK: (980, 900),
    # 内容链：7 个接口竖向排列，末端接组装
    N_ROUTE_B: (3380, 300),
    N_HTTP_ONLINE: (3680, 300),
    N_HTTP_CAMP: (3680, 440),
    N_HTTP_MENTOR: (3680, 580),
    N_HTTP_GOODS: (3680, 720),
    N_HTTP_ARTICLE: (3680, 860),
    N_HTTP_VIDEO: (3680, 1000),
    N_HTTP_AUDIO: (3680, 1140),
    N_CONTENT_BUILD: (3980, 1145),
    N_CONTENT_IF: (4280, 1155),
    N_CONTENT_GUIDE: (4580, 1140),
    N_CONTENT_ANS: (4880, 1150),
    N_CONTENT_NONE: (4280, 1330),
}


def apply_layout(graph):
    for n in graph["nodes"]:
        pos = LAYOUT.get(n["id"])
        if not pos:
            raise SystemExit("缺少布局坐标: %s %s" % (n["id"], n["data"].get("title")))
        n["position"] = {"x": float(pos[0]), "y": float(pos[1])}
        n["positionAbsolute"] = {"x": float(pos[0]), "y": float(pos[1])}
        n["sourcePosition"] = "right"
        n["targetPosition"] = "left"

    graph["viewport"] = {"x": 415.0, "y": 243.0, "zoom": 0.35}


if __name__ == "__main__":
    main()
