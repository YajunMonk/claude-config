#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import requests


DEFAULT_BASENAME = "阿叫一周娱乐热度观察"
WEIBO_COOKIE = "SUB=_2AkMWIuNSf8NxqwJRmP8dy2rhaoV2ygrEieKgfhKJJRMxHRl-yT9jqk86tRB6PaLNvQZR6zYUcYVT1zSjoSreQHidcUq7"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
ALAPI_TOKEN_ENV = "ALAPI_TOKEN"
ALAPI_WBTOP_URL = "https://v3.alapi.cn/api/new/wbtop"
ALAPI_TOPHUB_URL = "https://v3.alapi.cn/api/tophub"
ALAPI_TOUTIAO_URL = "https://v3.alapi.cn/api/new/toutiao"
RISK_KEYWORDS = (
    "爆料", "争议", "被拘", "骚扰", "塌房", "翻车", "劈腿", "出轨", "道歉", "回应", "抵制", "偷拍视频",
    "网暴", "逼迫", "婚闹", "封杀", "违法", "偷税", "嫖娼", "家暴", "吸毒", "丑闻", "负面",
    "轧戏", "掉粉", "下沉口碑"
)
SEVERE_RISK_KEYWORDS = (
    "被拘", "塌房", "骚扰", "违法", "偷税", "嫖娼", "家暴", "吸毒", "封杀", "抵制"
)
NAME_STOPWORDS = {
    "都市爱情", "女性成长", "办公室恋情", "警匪较量", "父子关系", "古装爱情", "甜虐爱情",
    "乱世恋爱", "奇幻爱情", "女性题材", "英雄成长", "轻喜剧", "头脑博弈", "相爱相杀",
    "社会话题", "法庭辩论", "偶像爱情", "游戏娱乐", "真人秀", "内地", "剧情", "战争",
    "爱情", "悬疑", "犯罪", "动作", "古装", "喜剧", "生活", "励志", "青春", "普通话",
    "自制", "文学改编", "近代", "当代", "复仇", "警察", "旅行观光", "微博", "热搜", "娱乐",
    "今日", "热榜", "剧宣", "同框", "合照", "上班", "路透", "修图", "现身", "备孕",
    "结婚证", "音乐", "艺人", "剧集", "综艺", "欧冠", "高会", "阿森纳"
}
FIT_LABELS = {"high": "高", "mid_high": "中高", "mid": "中"}
CONTENT_SOURCES = {"qqvideo", "iqiyi", "maoyan", "tracked"}
SUPPLEMENTAL_SOURCES = {"抖音热搜", "B站热搜"}
REALTIME_BUCKET_SOURCES = {
    "weibo": {"微博娱乐", "ALAPI微博热搜"},
    "aggregator": {"ALAPI今日热榜"},
    "toutiao": {"ALAPI头条热搜"},
}
REALTIME_BUCKET_WEIGHTS = {
    "weibo": 20.0,
    "aggregator": 8.0,
    "toutiao": 10.0,
}
HOT_SEARCH_POSITIVE_KEYWORDS = (
    "演唱会", "上座率", "观众发声", "开分", "好评", "封神", "出圈", "回归", "官宣", "新歌",
    "舞台", "红毯", "造型", "男团味", "高燃", "夺冠", "获奖", "路透", "合体", "同框"
)
ENTERTAINMENT_META_KEYWORDS = ("综艺", "剧集", "音乐", "电影", "影视", "演唱会")
ENTERTAINMENT_HINT_KEYWORDS = (
    "艺人", "歌手", "演员", "导演", "编剧", "音乐", "新歌", "专辑", "演唱会", "电影", "票房",
    "综艺", "剧集", "新剧", "开播", "收官", "定档", "杀青", "剧宣", "路透", "官宣", "主演",
    "客串", "角色", "合照", "同框", "修图", "现身", "回归", "上班", "同款", "合体", "亮相",
    "新节目", "CP", "偶像", "男团", "女团", "姐姐", "公主抱", "妻旅", "巅峰榜", "乐队",
    "内娱", "跑男", "片场", "工作室"
)
NON_ENTERTAINMENT_KEYWORDS = (
    "教育局", "医生", "海军", "国考", "小学", "国际航班", "空乘", "艾滋病", "梅毒", "彩礼", "火箭",
    "手机号", "法拍", "快餐", "微信提现", "海龟", "婚闹", "日本旅行", "摄像头", "公司", "A股",
    "涨价", "读书故事", "地图", "博物馆", "工资", "月卡", "科技巨头", "国家秘密", "补贴读好书"
)
STAR_EVENT_MARKERS = (
    "结婚证", "备孕", "长发现身", "修图", "合照", "同框", "剧宣", "路透", "上班", "新节目", "到达",
    "亮相", "同款", "回归", "合体", "悼念", "飞杭州", "行程图", "婚后生活", "抱", "发声", "现身",
    "演唱会", "上座率", "观众发声", "手势舞", "高会", "掉粉", "拍轧戏", "下沉口碑", "隐藏",
    "工作室", "跑男"
)
COMPOUND_SURNAMES = (
    "欧阳", "司马", "上官", "诸葛", "东方", "独孤", "南宫", "尉迟", "夏侯", "皇甫", "长孙", "宇文", "司徒", "令狐"
)
COMMON_SURNAMES = set(
    "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜"
    "戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳鲍史唐费廉"
    "岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元顾孟平黄和穆萧尹"
    "姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席"
    "季麻强贾路娄危江童颜郭梅盛林钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢"
    "莫经房裘缪干解应宗丁宣贲邓郁单杭洪包左石崔吉龚程邢滑裴陆荣翁荀羊於"
    "惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰"
    "秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎薄印宿白怀蒲台"
    "从鄂索咸籍赖卓蔺屠蒙池乔阴胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍"
    "却璩桑桂濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向"
    "古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩"
    "厍聂晁勾敖融冷訾辛阚那简饶空曾沙乜养鞠须丰巢关蒯相查后荆红游竺权逯"
    "盖益桓公仉督岳帅缑亢况郈有琴归海晋楚闫法汝鄢涂钦岳帅闫"
)


@dataclass
class WorkSignal:
    title: str
    source: str
    category: str
    rank: int
    actors: list[str]
    description: str
    score: float
    url: str = ""


@dataclass
class MentionSignal:
    source: str
    title: str
    rank: int
    flag: str = ""


@dataclass
class StarScore:
    name: str
    score: float = 0.0
    sources: set[str] = field(default_factory=set)
    works: defaultdict[str, float] = field(default_factory=lambda: defaultdict(float))
    work_categories: dict[str, str] = field(default_factory=dict)
    work_details: dict[str, str] = field(default_factory=dict)
    reasons: list[tuple[float, str]] = field(default_factory=list)
    mentions: list[MentionSignal] = field(default_factory=list)
    risk_hits: list[str] = field(default_factory=list)


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_template_path() -> Path:
    return skill_root() / "assets" / "aji-weekly-entertainment-template.html"


def normalize_date(raw: str | None) -> str:
    if not raw:
        return date.today().strftime("%Y.%m.%d")
    for fmt in ("%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y.%m.%d")
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {raw}")


def build_default_output_file(formatted_date: str) -> str:
    date_prefix = datetime.strptime(formatted_date, "%Y.%m.%d").strftime("%y%m%d")
    return f"{date_prefix}-{DEFAULT_BASENAME}.html"


def pick_available_output_path(output_dir: Path, formatted_date: str) -> Path:
    base_name = build_default_output_file(formatted_date)
    candidate = output_dir / base_name
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        numbered = output_dir / f"{stem}-{counter:02d}{suffix}"
        if not numbered.exists():
            return numbered
        counter += 1


def load_json(path: Path) -> Any:
    if not path.exists():
        return {} if path.suffix == ".json" else None
    return json.loads(path.read_text(encoding="utf-8"))


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def looks_like_name(token: str) -> bool:
    token = token.strip()
    if not re.fullmatch(r"[\u4e00-\u9fff]{2,4}", token):
        return False
    return token not in NAME_STOPWORDS


def extract_names_from_topic_label(label: str) -> list[str]:
    names: list[str] = []
    for token in label.split("|"):
        token = token.strip()
        if looks_like_person_name(token):
            names.append(token)
    return dedupe_keep_order(names)


def request_text(url: str, **kwargs: Any) -> str:
    try:
        response = requests.get(url, timeout=20, **kwargs)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return ""


def request_json(url: str, **kwargs: Any) -> Any:
    try:
        response = requests.get(url, timeout=20, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {}
    except ValueError:
        return {}


def request_json_loose(url: str, **kwargs: Any) -> Any:
    try:
        response = requests.get(url, timeout=20, **kwargs)
        response.raise_for_status()
        text = response.text.strip()
        if not text:
            return {}
        return json.JSONDecoder().raw_decode(text)[0]
    except Exception:
        return {}


def request_json_post(url: str, **kwargs: Any) -> Any:
    try:
        response = requests.post(url, timeout=20, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {}
    except ValueError:
        return {}


def strip_topic_wrappers(title: str) -> str:
    return clean_text(title).strip("#").strip()


def is_entertainment_title(title: str, metadata: str = "") -> bool:
    combined = f"{title} {metadata}"
    if any(keyword in metadata for keyword in ENTERTAINMENT_META_KEYWORDS):
        return True
    if any(keyword in title for keyword in NON_ENTERTAINMENT_KEYWORDS):
        return False
    if any(keyword in combined for keyword in ENTERTAINMENT_HINT_KEYWORDS):
        return True
    if re.search(r"[\u4e00-\u9fff]{2,4}\s+[\u4e00-\u9fff]{2,4}", title):
        return True
    if any(marker in title for marker in STAR_EVENT_MARKERS):
        return True
    return False


def looks_like_person_name(token: str) -> bool:
    if not looks_like_name(token):
        return False
    if token[:2] in COMPOUND_SURNAMES:
        return len(token) in (3, 4)
    return token[0] in COMMON_SURNAMES and len(token) in (2, 3)


def split_concatenated_names(sequence: str) -> list[str]:
    sequence = re.sub(r"[^\u4e00-\u9fff]", "", sequence)
    if len(sequence) < 2 or len(sequence) > 12:
        return []

    def backtrack(start: int) -> list[str] | None:
        if start == len(sequence):
            return []
        lengths = (4, 3, 2) if sequence[start:start + 2] in COMPOUND_SURNAMES else (3, 2)
        for length in lengths:
            candidate = sequence[start:start + length]
            if len(candidate) != length or not looks_like_person_name(candidate):
                continue
            rest = backtrack(start + length)
            if rest is not None:
                return [candidate, *rest]
        return None

    result = backtrack(0)
    return result or []


def extract_names_from_title_text(title: str) -> list[str]:
    title = strip_topic_wrappers(title)
    names: list[str] = []
    for token in re.split(r"[\s/|,，、&·•:：()（）]+", title):
        token = token.strip()
        if looks_like_person_name(token):
            names.append(token)
        elif re.fullmatch(r"[\u4e00-\u9fff]{4,10}", token):
            names.extend(split_concatenated_names(token))
    for marker in STAR_EVENT_MARKERS:
        if marker not in title:
            continue
        prefix = title.split(marker, 1)[0].strip()
        prefix = re.sub(r"[开发晒谈称说曝爆官宣回应否认]+$", "", prefix)
        if prefix and re.fullmatch(r"[\u4e00-\u9fff]{2,10}", prefix):
            names.extend(split_concatenated_names(prefix))
    return dedupe_keep_order(names)


def collect_known_names(work_overrides: dict[str, Any], priority_tracking: dict[str, dict[str, Any]]) -> set[str]:
    names: set[str] = set(priority_tracking.keys())
    for item in priority_tracking.values():
        names.update(item.get("aliases", []))
    for meta in work_overrides.values():
        names.update(meta.get("actors", []))
    return {name for name in names if looks_like_name(name)}


def extract_known_names_from_title(title: str, known_names: set[str]) -> list[str]:
    spans: list[tuple[int, int, str]] = []
    for name in known_names:
        start = title.find(name)
        while start != -1:
            spans.append((start, start + len(name), name))
            start = title.find(name, start + 1)
    spans.sort(key=lambda item: (item[0], -(item[1] - item[0]), item[2]))
    selected: list[str] = []
    occupied = [False] * max(len(title), 1)
    for start, end, name in spans:
        if any(occupied[idx] for idx in range(start, min(end, len(occupied)))):
            continue
        for idx in range(start, min(end, len(occupied))):
            occupied[idx] = True
        selected.append(name)
    return dedupe_keep_order(selected)


def fetch_alapi_wbtop(alapi_token: str, limit: int = 50) -> list[dict[str, str]]:
    try:
        data = request_json_post(
            ALAPI_WBTOP_URL,
            headers={"token": alapi_token, "Content-Type": "application/json"},
            json={"num": str(limit)},
        )
    except Exception:
        return []
    if not data.get("success"):
        return []
    results: list[dict[str, str]] = []
    for item in data.get("data", []):
        title = strip_topic_wrappers(item.get("hot_word", ""))
        if not title:
            continue
        results.append(
            {
                "title": title,
                "url": item.get("url", ""),
                "hot": str(item.get("hot_num") or ""),
                "flag": "",
            }
        )
    return results


def fetch_alapi_tophub(alapi_token: str) -> list[dict[str, str]]:
    try:
        data = request_json_post(
            ALAPI_TOPHUB_URL,
            headers={"token": alapi_token, "Content-Type": "application/json"},
            json={},
        )
    except Exception:
        return []
    if not data.get("success"):
        return []
    rows = data.get("data", {}).get("list", [])
    results: list[dict[str, str]] = []
    for item in rows:
        title = strip_topic_wrappers(item.get("title", ""))
        if not title:
            continue
        results.append(
            {
                "title": title,
                "url": item.get("link", ""),
                "hot": clean_text(item.get("other", "")),
                "flag": "",
            }
        )
    return results


def fetch_alapi_toutiao(alapi_token: str, news_type: str = "2", page: int = 1) -> list[dict[str, str]]:
    try:
        data = request_json_post(
            ALAPI_TOUTIAO_URL,
            headers={"token": alapi_token, "Content-Type": "application/json"},
            json={"type": str(news_type), "page": str(page)},
        )
    except Exception:
        return []
    if not data.get("success"):
        return []
    results: list[dict[str, str]] = []
    for item in data.get("data", []):
        title = strip_topic_wrappers(item.get("title", ""))
        if not title:
            continue
        results.append(
            {
                "title": title,
                "url": item.get("pc_url", "") or item.get("m_url", ""),
                "hot": clean_text(item.get("source", "")),
                "digest": clean_text(item.get("digest", "")),
                "time": clean_text(item.get("time", "")),
                "flag": "",
            }
        )
    return results


def fetch_weibo_entertainment() -> list[dict[str, str]]:
    url = "https://s.weibo.com/top/summary?cate=entertainment"
    html_text = request_text(
        url,
        headers={"User-Agent": USER_AGENT, "Referer": url, "Cookie": WEIBO_COOKIE},
    )
    table_match = re.search(r"<tbody>(.*?)</tbody>", html_text, re.S)
    if not table_match:
        return []
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_match.group(1), re.S)
    results: list[dict[str, str]] = []
    for row in rows[1:60]:
        link_match = re.search(r'<td class="td-02">.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', row, re.S)
        if not link_match:
            continue
        title = clean_text(link_match.group(2))
        href = link_match.group(1)
        hot_match = re.search(r'<span>([^<]+)</span>', row)
        flag_match = re.search(r'<td class="td-03">([^<]*)</td>', row)
        results.append(
            {
                "title": title,
                "url": f"https://s.weibo.com{href}",
                "hot": clean_text(hot_match.group(1)) if hot_match else "",
                "flag": clean_text(flag_match.group(1)) if flag_match else "",
            }
        )
    return results or fetch_weibo_hot_fallback()


def fetch_weibo_hot_fallback() -> list[dict[str, str]]:
    data = request_json("https://v2.xxapi.cn/api/weibohot", headers={"User-Agent": USER_AGENT})
    rows = data.get("data", []) if isinstance(data, dict) else []
    results: list[dict[str, str]] = []
    for item in rows:
        title = strip_topic_wrappers(str(item.get("title", "")))
        if not title:
            continue
        results.append(
            {
                "title": title,
                "url": item.get("url", ""),
                "hot": str(item.get("hot") or ""),
                "flag": "",
            }
        )
    if results:
        return results

    html_text = request_text("https://api.xk.ee/hot/weibo.php", headers={"User-Agent": USER_AGENT})
    for item in re.findall(r'<div class="item">(.*?)</div>', html_text, re.S):
        title_match = re.search(r'<a[^>]*>(.*?)</a>', item, re.S)
        if not title_match:
            continue
        title = strip_topic_wrappers(clean_text(title_match.group(1)))
        if not title:
            continue
        hot_match = re.search(r'<span class="hot">(.*?)</span>', item, re.S)
        results.append(
            {
                "title": title,
                "url": "",
                "hot": clean_text(hot_match.group(1)) if hot_match else "",
                "flag": "",
            }
        )
    return results


def fetch_iqiyi_signals(work_overrides: dict[str, Any]) -> list[WorkSignal]:
    url = (
        "https://mesh.if.iqiyi.com/portal/lw/v7/channel/card/videoTab?channelName=recommend"
        "&data_source=v7_rec_sec_hot_rank_list&tempId=85&count=30&block_id=hot_ranklist"
        "&device=14a4b5ba98e790dce6dc07482447cf48&from=webapp"
    )
    data = request_json(url, headers={"User-Agent": USER_AGENT, "Referer": "https://www.iqiyi.com"})
    items = data.get("items", [{}])[0].get("video", [{}])[0].get("data", [])
    signals: list[WorkSignal] = []
    for index, item in enumerate(items, start=1):
        title = item.get("title", "").strip()
        if not title:
            continue
        override = work_overrides.get(title, {})
        actors = [person.get("name", "").strip() for person in item.get("creator", []) + item.get("contributor", [])]
        actors.extend(override.get("actors", []))
        actors = dedupe_keep_order([x for x in actors if x])
        tag = item.get("tag", "")
        category = override.get("category") or (
            "variety" if any(key in tag for key in ("真人秀", "游戏娱乐", "综艺", "旅行观光", "搞笑")) else "film_tv"
        )
        description = item.get("desc") or item.get("description") or tag
        base = 88 if category == "variety" else 84
        signals.append(
            WorkSignal(
                title=title,
                source="iqiyi",
                category=category,
                rank=index,
                actors=actors,
                description=description,
                score=max(28, base - index * 2),
                url=item.get("page_url", ""),
            )
        )
    return signals


def fetch_qqvideo_signals(work_overrides: dict[str, Any]) -> list[WorkSignal]:
    url = "https://pbaccess.video.qq.com/trpc.vector_layout.page_view.PageService/getCard?video_appid=3000010&vversion_platform=2"
    payload = {
        "page_params": {
            "rank_channel_id": "100113",
            "rank_name": "HotSearch",
            "rank_page_size": "30",
            "tab_mvl_sub_mod_id": "792ac_19e77Sub_1b2",
            "tab_name": "热搜榜",
            "tab_type": "hot_rank",
            "tab_vl_data_src": "f5200deb4596bbf3",
            "page_id": "scms_shake",
            "page_type": "scms_shake",
            "source_key": "",
            "tag_id": "",
            "tag_type": "",
            "new_mark_label_enabled": "1"
        },
        "page_context": {"page_index": "1"},
        "flip_info": {
            "page_strategy_id": "",
            "page_module_id": "792ac_19e77",
            "module_strategy_id": {},
            "sub_module_id": "20251106065177",
            "flip_params": {
                "folding_screen_show_num": "",
                "is_mvl": "1",
                "mvl_strategy_info": "{\"default_strategy_id\":\"06755800b45b49238582a6fa1ad0f5c5\",\"default_version\":\"3836\",\"hit_page_uuid\":\"b5080d97dc694a5fb50eb9e7c99326ac\",\"hit_tab_info\":null,\"gray_status_info\":null,\"bypass_to_un_exp_id\":\"\"}",
                "mvl_sub_mod_id": "20251106065177",
                "pad_post_show_num": "",
                "pad_pro_post_show_num": "",
                "pad_pro_small_hor_pic_display_num": "",
                "pad_small_hor_pic_display_num": "",
                "page_id": "scms_shake",
                "page_num": "0",
                "page_type": "scms_shake",
                "post_show_num": "",
                "shake_size": "",
                "small_hor_pic_display_num": "",
                "source_key": "100113",
                "un_policy_id": "06755800b45b49238582a6fa1ad0f5c5",
                "un_strategy_id": "06755800b45b49238582a6fa1ad0f5c5"
            },
            "relace_children_key": []
        }
    }
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"User-Agent": USER_AGENT, "Referer": "https://v.qq.com/"},
            timeout=20,
        )
        response.raise_for_status()
        cards = (
            response.json()
            .get("data", {})
            .get("card", {})
            .get("children_list", {})
            .get("list", {})
            .get("cards", [])
        )
    except requests.RequestException:
        return []
    except ValueError:
        return []
    signals: list[WorkSignal] = []
    for index, card in enumerate(cards, start=1):
        params = card.get("params", {})
        title = (params.get("title") or "").strip()
        if not title:
            continue
        override = work_overrides.get(title, {})
        topic_label = params.get("topic_label", "")
        actors = extract_names_from_topic_label(topic_label)
        actors.extend(override.get("actors", []))
        actors = dedupe_keep_order(actors)
        description = params.get("sub_title") or topic_label
        signals.append(
            WorkSignal(
                title=title,
                source="qqvideo",
                category=override.get("category", "film_tv"),
                rank=index,
                actors=actors,
                description=description,
                score=max(30, 92 - index * 2.2),
                url=f"https://v.qq.com/x/cover/{card.get('id', '')}.html",
            )
        )
    return signals


def fetch_maoyan_web_heat(work_overrides: dict[str, Any]) -> list[WorkSignal]:
    html_text = request_text("https://piaofang.maoyan.com/web-heat", headers={"User-Agent": USER_AGENT})
    row_matches = re.findall(
        r'<tr class="body-row[^"]*">.*?<p class="video-name">(.*?)</p><p class="web-info">(.*?)</p>.*?<div class="heat-num">(.*?)</div>',
        html_text,
        re.S,
    )
    signals: list[WorkSignal] = []
    for index, row in enumerate(row_matches[:20], start=1):
        title = clean_text(row[0])
        info = clean_text(row[1])
        heat = clean_text(row[2])
        override = work_overrides.get(title)
        if not override:
            continue
        description = f"{info} · 实时热度 {heat}"
        signals.append(
            WorkSignal(
                title=title,
                source="maoyan",
                category=override.get("category", "film_tv"),
                rank=index,
                actors=override.get("actors", []),
                description=description,
                score=max(26, 86 - index * 2),
                url="https://piaofang.maoyan.com/web-heat",
            )
        )
    return signals


def fetch_tracked_pages(work_overrides: dict[str, Any]) -> list[WorkSignal]:
    signals: list[WorkSignal] = []
    for title, meta in work_overrides.items():
        monitor_url = meta.get("monitor_url")
        if not monitor_url:
            continue
        try:
            html_text = request_text(monitor_url, headers={"User-Agent": USER_AGENT})
        except Exception:
            continue
        if title not in html_text:
            continue
        heat_match = re.search(r"历史最高热度.*?>([0-9.]+)<", html_text, re.S)
        description = "重点节目跟踪页命中"
        if heat_match:
            description = f"重点节目跟踪页命中 · 历史最高热度 {heat_match.group(1)}"
        signals.append(
            WorkSignal(
                title=title,
                source="tracked",
                category=meta.get("category", "variety"),
                rank=1,
                actors=meta.get("actors", []),
                description=description,
                score=96,
                url=monitor_url,
            )
        )
    return signals


def fetch_douyin_hot() -> list[str]:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    try:
        session.get("https://login.douyin.com/", timeout=20)
        response = session.get(
            "https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&detail_list=1",
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        titles = [item.get("word", "").strip() for item in data.get("data", {}).get("word_list", []) if item.get("word")]
        if titles:
            return titles
    except Exception:
        pass
    return fetch_douyin_hot_fallback()


def fetch_douyin_hot_fallback() -> list[str]:
    candidate_payloads: list[Any] = [
        request_json_loose("https://v.api.aa1.cn/api/douyin-hot/index.php?aa1=json", headers={"User-Agent": USER_AGENT}),
        request_json("https://v2.xxapi.cn/api/douyinhot", headers={"User-Agent": USER_AGENT}),
        request_json("https://api.xhus.cn/api/rdouyin?encode=json", headers={"User-Agent": USER_AGENT}),
    ]
    titles: list[str] = []
    for data in candidate_payloads:
        if not isinstance(data, dict):
            continue
        rows = data.get("word_list")
        if rows is None and isinstance(data.get("data"), dict):
            rows = data["data"].get("word_list")
        if rows is None:
            rows = data.get("data")
        if not isinstance(rows, list):
            continue
        for item in rows:
            if not isinstance(item, dict):
                continue
            title = item.get("word") or item.get("title") or item.get("sentence")
            title = strip_topic_wrappers(str(title or ""))
            if title:
                titles.append(title)
        if titles:
            return dedupe_keep_order(titles)
    return []


def fetch_bilibili_hot_search() -> list[str]:
    try:
        data = request_json("https://s.search.bilibili.com/main/hotword?limit=30", headers={"User-Agent": USER_AGENT})
    except Exception:
        return []
    return [item.get("show_name", "").strip() for item in data.get("list", []) if item.get("show_name")]


def collect_priority_keywords(priority_tracking: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["name"]: item for item in priority_tracking}


def add_work_signal(star_scores: dict[str, StarScore], signal: WorkSignal) -> None:
    for actor in signal.actors:
        star = star_scores.setdefault(actor, StarScore(name=actor))
        star.score += signal.score
        star.sources.add(signal.source)
        star.works[signal.title] += signal.score
        star.work_categories[signal.title] = signal.category
        star.work_details[signal.title] = signal.description
        source_label = {
            "qqvideo": "腾讯视频热搜",
            "iqiyi": "爱奇艺热播",
            "maoyan": "猫眼全网热度",
            "tracked": "重点节目跟踪",
        }.get(signal.source, signal.source)
        star.reasons.append((signal.score, f"{source_label}：{signal.title}"))


def add_mention_signals(
    star_scores: dict[str, StarScore],
    priority_tracking: dict[str, dict[str, Any]],
    mention_titles: list[str],
    source: str,
    base_score: float,
    known_names: set[str] | None = None,
    allow_bootstrap: bool = False,
) -> None:
    if not mention_titles:
        return
    candidate_names = set(star_scores.keys()) | set(priority_tracking.keys()) | set(known_names or set())
    keyword_map: dict[str, list[str]] = {}
    for name in candidate_names:
        tracked = priority_tracking.get(name, {})
        keywords = [name]
        keywords.extend(tracked.get("aliases", []))
        keywords.extend(tracked.get("keywords", []))
        keyword_map[name] = dedupe_keep_order([keyword for keyword in keywords if keyword])
    for rank, title in enumerate(mention_titles, start=1):
        matched_names: list[str] = []
        for name, keywords in keyword_map.items():
            if not any(keyword in title for keyword in keywords):
                continue
            star = star_scores.setdefault(name, StarScore(name=name))
            score = max(8.0, base_score - rank * 0.8)
            star.score += score
            star.sources.add(source)
            star.mentions.append(MentionSignal(source=source, title=title, rank=rank))
            star.reasons.append((score, f"{source}：{title}"))
            matched_names.append(name)
            if any(keyword in title for keyword in RISK_KEYWORDS):
                star.risk_hits.append(title)
        if not allow_bootstrap:
            continue
        if not matched_names and not is_entertainment_title(title):
            continue
        extracted_names = extract_known_names_from_title(title, known_names or set())
        if not extracted_names:
            extracted_names = extract_names_from_title_text(title)
        for name in extracted_names:
            if name in matched_names or not looks_like_person_name(name):
                continue
            star = star_scores.setdefault(name, StarScore(name=name))
            score = max(6.0, base_score - rank * 0.9)
            star.score += score
            star.sources.add(source)
            star.mentions.append(MentionSignal(source=source, title=title, rank=rank))
            star.reasons.append((score, f"{source}：{title}"))
            if any(keyword in title for keyword in RISK_KEYWORDS):
                star.risk_hits.append(title)


def infer_primary_work(star: StarScore) -> tuple[str | None, str]:
    if not star.works:
        return None, "topic"
    work, _ = max(star.works.items(), key=lambda item: item[1])
    return work, star.work_categories.get(work, "film_tv")


def infer_fit(name: str, star: StarScore, work_overrides: dict[str, Any], priority_tracking: dict[str, dict[str, Any]]) -> str:
    tracked_fit = priority_tracking.get(name, {}).get("fit")
    if tracked_fit:
        return tracked_fit
    primary_work, primary_category = infer_primary_work(star)
    if primary_work and primary_work in work_overrides:
        return work_overrides[primary_work].get("fit", "mid")
    if primary_category == "variety":
        return "mid"
    return "mid_high"


def infer_risk(star: StarScore) -> str:
    if any(any(keyword in title for keyword in SEVERE_RISK_KEYWORDS) for title in star.risk_hits):
        return "高风险"
    return "需复核" if star.risk_hits else "低"


def infer_action(fit: str, risk: str, primary_category: str, score: float) -> str:
    if risk == "高风险":
        return "规避"
    if risk == "需复核":
        return "先观察"
    if fit == "high" and primary_category == "film_tv":
        return "优先关注"
    if fit == "high":
        return "可进优先候选"
    if fit == "mid_high" and score >= 55:
        return "值得推进"
    return "可进优先候选"


def best_rank_for_sources(star: StarScore, sources: set[str]) -> int | None:
    ranks = [mention.rank for mention in star.mentions if mention.source in sources]
    return min(ranks) if ranks else None


def realtime_bucket_count(star: StarScore) -> int:
    return sum(1 for sources in REALTIME_BUCKET_SOURCES.values() if star.sources & sources)


def supplemental_source_count(star: StarScore) -> int:
    return len(star.sources & SUPPLEMENTAL_SOURCES)


def content_source_count(star: StarScore) -> int:
    return len(star.sources & CONTENT_SOURCES)


def compute_content_anchor_score(star: StarScore, priority_tracking: dict[str, dict[str, Any]]) -> float:
    if star.works:
        strongest_work = max(star.works.values())
        work_count = len(star.works)
        category_count = len(set(star.work_categories.values()))
        score = min(22.0, strongest_work * 0.25)
        score += min(5.0, max(work_count - 1, 0) * 2.5)
        score += min(3.0, max(category_count - 1, 0) * 3.0)
        score += min(2.0, max(content_source_count(star) - 1, 0) * 2.0)
        return min(32.0, score)

    realtime_buckets = realtime_bucket_count(star)
    mention_count = len(star.mentions)
    if realtime_buckets >= 3:
        return 20.0
    if realtime_buckets >= 2 and mention_count >= 2:
        return 16.0
    if realtime_buckets >= 2:
        return 12.0
    if mention_count >= 2:
        return 8.0
    if star.name in priority_tracking and mention_count >= 1:
        return 6.0
    return 0.0


def compute_realtime_score(star: StarScore) -> float:
    score = 0.0
    for bucket, sources in REALTIME_BUCKET_SOURCES.items():
        rank = best_rank_for_sources(star, sources)
        if rank is None:
            continue
        max_score = REALTIME_BUCKET_WEIGHTS[bucket]
        decay = 0.45 if bucket == "weibo" else 0.3
        floor = 5.0 if bucket == "weibo" else (3.0 if bucket == "toutiao" else 2.0)
        bucket_score = max(floor, max_score - (rank - 1) * decay)
        if bucket == "weibo" and {"微博娱乐", "ALAPI微博热搜"} <= star.sources:
            bucket_score = min(max_score, bucket_score + 1.5)
        score += bucket_score
    return min(38.0, score)


def compute_sustainability_score(star: StarScore) -> float:
    score = 0.0
    if star.works:
        score += 8.0
    realtime_buckets = realtime_bucket_count(star)
    if realtime_buckets >= 2:
        score += 6.0
    elif realtime_buckets == 1:
        score += 2.0
    content_sources = content_source_count(star)
    if content_sources >= 2:
        score += 4.0
    elif content_sources == 1:
        score += 2.0
    if len(star.mentions) >= 3 or len(star.works) >= 2:
        score += 2.0
    return min(20.0, score)


def compute_multisource_score(star: StarScore) -> float:
    score = 0.0
    score += min(6.0, realtime_bucket_count(star) * 2.0)
    if star.works:
        score += 2.0
    if supplemental_source_count(star):
        score += 2.0
    return min(10.0, score)


def discovery_score_breakdown(star: StarScore, priority_tracking: dict[str, dict[str, Any]]) -> dict[str, float]:
    content = compute_content_anchor_score(star, priority_tracking)
    realtime = compute_realtime_score(star)
    sustainability = compute_sustainability_score(star)
    multisource = compute_multisource_score(star)
    risk_penalty = {"低": 0.0, "需复核": 8.0, "高风险": 32.0}.get(infer_risk(star), 0.0)
    total = max(0.0, content + realtime + sustainability + multisource - risk_penalty)
    return {
        "content": round(content, 2),
        "realtime": round(realtime, 2),
        "sustainability": round(sustainability, 2),
        "multisource": round(multisource, 2),
        "total": round(total, 2),
    }


def is_recommendable(star: StarScore, priority_tracking: dict[str, dict[str, Any]]) -> bool:
    if infer_risk(star) == "高风险":
        return False
    breakdown = discovery_score_breakdown(star, priority_tracking)
    if breakdown["content"] >= 16.0:
        return True
    if breakdown["realtime"] >= 18.0 and breakdown["sustainability"] >= 10.0 and realtime_bucket_count(star) >= 2:
        return True
    return breakdown["total"] >= 48.0 and realtime_bucket_count(star) >= 2


def build_star_reason(name: str, star: StarScore, primary_work: str | None, primary_category: str) -> str:
    source_names = {
        "qqvideo": "腾讯视频热搜",
        "iqiyi": "爱奇艺热播",
        "maoyan": "猫眼热度",
        "tracked": "重点跟踪页",
        "微博娱乐": "微博娱乐热搜",
        "ALAPI微博热搜": "ALAPI微博热搜",
        "ALAPI今日热榜": "ALAPI今日热榜",
        "ALAPI头条热搜": "ALAPI头条热搜",
        "抖音热搜": "抖音热搜",
        "B站热搜": "B站热搜",
    }
    if primary_work:
        primary_source = None
        for _, reason in sorted(star.reasons, reverse=True):
            if primary_work in reason:
                primary_source = reason.split("：", 1)[0]
                break
        if primary_source:
            return f"{source_names.get(primary_source, primary_source)} + 《{primary_work}》"
        return f"《{primary_work}》带动热度上升"
    if star.mentions:
        mention = star.mentions[0]
        return f"{mention.source}讨论上升"
    return "近期关注度上升"


def build_star_summary(
    name: str,
    star: StarScore,
    primary_work: str | None,
    primary_category: str,
    fit: str,
    priority_tracking: dict[str, dict[str, Any]],
) -> str:
    tracked_hint = priority_tracking.get(name, {}).get("summary_hint")
    if tracked_hint:
        return tracked_hint
    if primary_work and primary_category == "film_tv":
        if fit == "high":
            return f"当前主要受《{primary_work}》带动，作品窗口明确，也更容易连接家庭、陪伴和成长类品牌表达。"
        return f"当前主要受《{primary_work}》带动，作品热度较稳，适合阶段性合作或节点联动。"
    if primary_work and primary_category == "variety":
        return f"当前主要由《{primary_work}》带动综艺讨论，曝光强，但更适合内容共创或阶段性合作。"
    if realtime_bucket_count(star) >= 2:
        return "当前更偏话题回升或经典内容回流，已经出现跨渠道讨论，不再按单条热搜处理。"
    return "当前更偏事件或讨论带动，建议继续观察后续承接信号，不单独只看单条热搜。"


def star_rank_value(
    star: StarScore,
    work_overrides: dict[str, Any],
    priority_tracking: dict[str, dict[str, Any]],
) -> float:
    return discovery_score_breakdown(star, priority_tracking)["total"]


def pick_top_stars(
    star_scores: dict[str, StarScore],
    work_overrides: dict[str, Any],
    priority_tracking: dict[str, dict[str, Any]],
    limit: int = 10,
) -> list[dict[str, Any]]:
    sorted_stars = sorted(
        star_scores.values(),
        key=lambda item: (-star_rank_value(item, work_overrides, priority_tracking), -item.score, item.name),
    )
    selected: list[dict[str, Any]] = []
    work_quota: defaultdict[str, int] = defaultdict(int)
    for star in sorted_stars:
        if not is_recommendable(star, priority_tracking):
            continue
        primary_work, primary_category = infer_primary_work(star)
        work_key = primary_work or f"topic:{star.name}"
        if primary_work and work_quota[work_key] >= 2:
            continue
        selected.append(
            {
                "star": star,
                "primary_work": primary_work,
                "primary_category": primary_category,
                "discovery": discovery_score_breakdown(star, priority_tracking),
            }
        )
        work_quota[work_key] += 1
        if len(selected) >= limit:
            break
    return selected


def rank_star_candidates(
    star_scores: dict[str, StarScore],
    work_overrides: dict[str, Any],
    priority_tracking: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    ranked = sorted(
        star_scores.values(),
        key=lambda item: (-star_rank_value(item, work_overrides, priority_tracking), -item.score, item.name),
    )
    records: list[dict[str, Any]] = []
    for star in ranked:
        primary_work, primary_category = infer_primary_work(star)
        records.append(
            {
                "star": star,
                "primary_work": primary_work,
                "primary_category": primary_category,
                "discovery": discovery_score_breakdown(star, priority_tracking),
                "recommendable": is_recommendable(star, priority_tracking),
            }
        )
    return records


def render_pill_row(fit: str, risk: str, action: str) -> str:
    fit_label = FIT_LABELS.get(fit, "中")
    return (
        '<div class="pill-row">'
        f'<span class="pill pill-fit-high">匹配 {html.escape(fit_label)}</span>'
        f'<span class="pill {"pill-risk-review" if risk != "低" else "pill-risk-low"}">风险 {html.escape(risk)}</span>'
        f'<span class="pill pill-action">建议 {html.escape(action)}</span>'
        "</div>"
    )


def render_star_cards(top_stars: list[dict[str, Any]], work_overrides: dict[str, Any], priority_tracking: dict[str, dict[str, Any]]) -> str:
    cards: list[str] = []
    for index, item in enumerate(top_stars, start=1):
        star: StarScore = item["star"]
        primary_work = item["primary_work"]
        primary_category = item["primary_category"]
        fit = infer_fit(star.name, star, work_overrides, priority_tracking)
        risk = infer_risk(star)
        action = infer_action(fit, risk, primary_category, star.score)
        reason = build_star_reason(star.name, star, primary_work, primary_category)
        summary = build_star_summary(star.name, star, primary_work, primary_category, fit, priority_tracking)
        card_class = "star-card star-featured" if index <= 4 else "star-card star-compact"
        cards.append(
            f'''
        <article class="{card_class}">
          <div class="star-head">
            <span class="rank-badge">{index:02d}</span>
            <div class="star-title">
              <h3>{html.escape(star.name)}</h3>
              <p>{html.escape(reason)}</p>
            </div>
          </div>
          <p class="star-summary">{html.escape(summary)}</p>
          {render_pill_row(fit, risk, action)}
        </article>'''
        )
    return "\n".join(cards)


def render_watch_cards(candidates: list[dict[str, Any]], work_overrides: dict[str, Any], priority_tracking: dict[str, dict[str, Any]]) -> str:
    cards: list[str] = []
    for item in candidates[:3]:
        star: StarScore = item["star"]
        primary_work = item["primary_work"]
        fit = infer_fit(star.name, star, work_overrides, priority_tracking)
        fit_label = FIT_LABELS.get(fit, "中")
        reason = f"《{primary_work}》带动" if primary_work else "话题热度上升"
        cards.append(
            f'''
        <article class="watch-card">
          <h3>{html.escape(star.name)}</h3>
          <p>{html.escape(reason)}，匹配{fit_label}，先观察。</p>
        </article>'''
        )
    return "\n".join(cards)


def render_content_cards(signals: list[WorkSignal], limit: int) -> str:
    parts: list[str] = []
    seen_titles: set[str] = set()
    for signal in signals:
        if signal.title in seen_titles:
            continue
        seen_titles.add(signal.title)
        parts.append(
            f'''
        <article class="content-card">
          <strong>{html.escape(signal.title)}</strong>
          <p>{html.escape(signal.description)}</p>
        </article>'''
        )
        if len(parts) >= limit:
            break
    return "\n".join(parts)


def build_work_hot_titles(variety_signals: list[WorkSignal], film_signals: list[WorkSignal], limit: int = 10) -> list[str]:
    signals = sorted(
        [*variety_signals, *film_signals],
        key=lambda signal: (-signal.score, signal.rank, signal.title),
    )
    titles: list[str] = []
    seen: set[str] = set()
    for signal in signals:
        if signal.title in seen:
            continue
        seen.add(signal.title)
        label = "综艺" if signal.category == "variety" else "影视"
        titles.append(f"{signal.title}｜{label}")
        if len(titles) >= limit:
            break
    return titles


def compact_topic_label(title: str, max_len: int = 22) -> str:
    title = re.sub(r"\s+", " ", strip_topic_wrappers(title))
    return title if len(title) <= max_len else f"{title[:max_len]}…"


def render_realtime_rank_cards(groups: list[tuple[str, list[str]]]) -> str:
    cards: list[str] = []
    for source, titles in groups:
        visible_titles = [title for title in titles if title][:10]
        if not visible_titles:
            continue
        items = "".join(
            f'<li><span>{index:02d}</span><p>{html.escape(compact_topic_label(title))}</p></li>'
            for index, title in enumerate(visible_titles, start=1)
        )
        cards.append(
            f'''
        <article class="rank-card">
          <h3>{html.escape(source)}</h3>
          <ol>{items}</ol>
        </article>'''
        )
    return "\n".join(cards)


def classify_hot_topic(title: str) -> str:
    if any(keyword in title for keyword in RISK_KEYWORDS):
        return "review"
    if any(keyword in title for keyword in HOT_SEARCH_POSITIVE_KEYWORDS):
        return "positive"
    return "neutral"


def hot_topic_copy(star: StarScore, label: str) -> str:
    mention = min(star.mentions, key=lambda item: item.rank)
    topic = compact_topic_label(mention.title, 30)
    source = {"微博娱乐": "微博热搜"}.get(mention.source, mention.source)
    if label == "review":
        return f"{source}｜{topic}｜先复核口碑与后续发酵。"
    return f"{source}｜{topic}｜可借势，继续看承接。"


def render_hot_observation_cards(star_scores: dict[str, StarScore], top_names: set[str], limit_per_group: int = 3) -> str:
    positive: list[StarScore] = []
    review: list[StarScore] = []
    for star in star_scores.values():
        if star.name in top_names or not star.mentions or not looks_like_person_name(star.name):
            continue
        best_mention = min(star.mentions, key=lambda item: item.rank)
        if best_mention.source not in {"微博娱乐", "ALAPI微博热搜", "ALAPI今日热榜", "ALAPI头条热搜", "抖音热搜", "B站热搜"}:
            continue
        if not star.works and not is_entertainment_title(best_mention.title):
            continue
        label = "review" if infer_risk(star) != "低" or classify_hot_topic(best_mention.title) == "review" else "positive"
        if label == "review":
            review.append(star)
        else:
            positive.append(star)

    def dedupe_by_topic(stars: list[StarScore]) -> list[StarScore]:
        seen_topics: set[str] = set()
        result: list[StarScore] = []
        for star in stars:
            best_mention = min(star.mentions, key=lambda item: item.rank)
            topic_key = best_mention.title
            if topic_key in seen_topics:
                continue
            seen_topics.add(topic_key)
            result.append(star)
        return result

    def sort_key(star: StarScore) -> tuple[int, float, str]:
        best_rank = min(mention.rank for mention in star.mentions)
        return (best_rank, -star.score, star.name)

    positive.sort(key=sort_key)
    review.sort(key=sort_key)
    positive = dedupe_by_topic(positive)
    review = dedupe_by_topic(review)

    cards: list[str] = []
    for label, title, stars in (
        ("positive", "正向/可借势", positive[:limit_per_group]),
        ("review", "负面/需复核", review[:limit_per_group]),
    ):
        if not stars:
            continue
        inner = "".join(
            f'''
          <article class="trend-card trend-{label}">
            <h3>{html.escape(star.name)}</h3>
            <p>{html.escape(hot_topic_copy(star, "review" if label == "review" else "positive"))}</p>
          </article>'''
            for star in stars
        )
        cards.append(
            f'''
        <div class="trend-group">
          <h3>{html.escape(title)}</h3>
          <div class="trend-list">{inner}
          </div>
        </div>'''
        )
    return "\n".join(cards)


def build_alapi_social_label(use_alapi_news: bool) -> str:
    return "ALAPI 今日热榜、微博热搜和头条热搜" if use_alapi_news else "ALAPI 今日热榜和微博热搜"


def build_takeaways(
    variety_signals: list[WorkSignal],
    film_signals: list[WorkSignal],
    top_stars: list[dict[str, Any]],
    weibo_titles: list[str],
    alapi_news_titles: list[str],
    use_alapi: bool,
    use_alapi_news: bool,
) -> list[tuple[str, str]]:
    top_variety = variety_signals[0].title if variety_signals else "综艺热度"
    top_film = film_signals[0].title if film_signals else "剧集热度"
    names = "、".join(item["star"].name for item in top_stars[:3]) or "当前高热艺人"
    risk_titles = [*weibo_titles, *alapi_news_titles]
    award_or_risk = "实时渠道会放大事件性讨论，风险状态必须和热度发现分拆开看。"
    if use_alapi_news:
        award_or_risk = "微博热搜、今日热榜和头条热搜会同时放大事件性讨论，风险状态必须和热度发现分拆开看。"
    if not any(any(word in title for word in RISK_KEYWORDS) for title in risk_titles):
        award_or_risk = "今天社会热度信号更偏作品与节目讨论，事件型风险信号相对可控。"
    social_title = "先做热度发现分"
    social_copy = "先按内容承接 32%、实时渠道 38%、持续性 20%、多源验证 10% 做发现分，再把热搜人物单独拆出正向和需复核两层。"
    if use_alapi:
        social_title = "先看实时渠道层"
        social_copy = f"把 {build_alapi_social_label(use_alapi_news)} 放进 38% 的实时渠道层，再用作品与持续性校正，优先保留 {names} 这类跨渠道持续出现的名字。"
    return [
        (social_title, social_copy),
        ("内容承接负责校正", f"《{top_film}》和《{top_variety}》这类承接信号继续负责验证热度是不是可持续，不让单条话题直接决定最终推荐。"),
        ("风险和匹配度单独看", award_or_risk),
    ]


def build_source_cards(use_tracked_pages: bool, use_alapi: bool, use_alapi_news: bool) -> list[tuple[str, str]]:
    cards = [
        ("爱奇艺 + 腾讯视频", "属于内容承接层，影视和综艺同权看，不再让剧集天然压过综艺。"),
        ("猫眼全网热度", "补作品热区与节目强度，帮助判断热度是不是有承接，不只看标题。"),
        ("微博娱乐", "属于实时渠道层，更适合抓事件热度、综艺出圈片段和需要复核的风险信号。"),
        ("抖音 + B站", "更多补大众扩散和年轻传播，不直接决定主排序。"),
    ]
    if use_alapi:
        cards.insert(0, (build_alapi_social_label(use_alapi_news), "属于实时渠道 38% 这一层，负责发现正在起势的人，但不单独决定最终推荐。"))
    elif use_alapi_news:
        cards.insert(0, ("ALAPI 头条热搜", "补资讯与社会讨论面，对官宣、事件和持续发酵的话题更敏感，但仍要和内容承接分开看。"))
    if use_tracked_pages:
        cards.insert(3 if use_alapi else 2, ("重点节目跟踪页", "对像《乘风2026》这类重点节目做定向跟踪，减少综艺艺人和经典回流话题的漏判。"))
    return cards


def build_main_html(
    formatted_date: str,
    top_stars: list[dict[str, Any]],
    watch_candidates: list[dict[str, Any]],
    star_scores: dict[str, StarScore],
    realtime_rank_groups: list[tuple[str, list[str]]],
    variety_signals: list[WorkSignal],
    film_signals: list[WorkSignal],
    weibo_titles: list[str],
    alapi_news_titles: list[str],
    work_overrides: dict[str, Any],
    priority_tracking: dict[str, dict[str, Any]],
    use_tracked_pages: bool,
    use_alapi: bool,
    use_alapi_news: bool,
) -> str:
    hero_copy = f"截至 {formatted_date}，从全网热点、短视频扩散、社区讨论和影视综艺热度中筛选可用声量；优先关注能承接亲子成长、家庭陪伴和品牌信任感的明星。"
    realtime_rank_html = render_realtime_rank_cards(realtime_rank_groups)
    hot_observation_html = render_hot_observation_cards(star_scores, {item["star"].name for item in top_stars})
    variety_html = render_content_cards(variety_signals, 2)
    film_html = render_content_cards(film_signals, 3)
    top_names = "、".join(item["star"].name for item in top_stars[:4])
    summary_copy = f"今日建议先看 {top_names}：优先选择有作品承接、讨论面稳定且风险较低的名字；事件型热搜只做借势观察，不直接进入合作优先级。"
    return f'''
  <main class="poster">
    <section class="hero">
      <div class="hero-meta">
        <span class="eyebrow">叫叫品牌营销中心</span>
        <div class="hero-date">{html.escape(formatted_date)}</div>
      </div>
      <h1>阿叫热点榜</h1>
      <p class="hero-copy">{html.escape(hero_copy)}</p>
      <div class="hero-stats">
        <div class="hero-stat">
          <span>热点榜单</span>
          <strong>{sum(1 for _, titles in realtime_rank_groups if titles)}</strong>
          <small>微博、抖音、B站、影视综艺</small>
        </div>
        <div class="hero-stat">
          <span>推荐明星</span>
          <strong>{len(top_stars)}</strong>
          <small>兼顾作品承接与当前热搜</small>
        </div>
        <div class="hero-stat">
          <span>热搜观察</span>
          <strong>{hot_observation_html.count('trend-card')}</strong>
          <small>正向和需复核分开看</small>
        </div>
      </div>
    </section>

    <section class="section">
      <span class="section-mark">今日热点</span>
      <div class="rank-grid">
        {realtime_rank_html}
      </div>
    </section>

    <section class="section">
      <span class="section-mark">明星推荐</span>
      <div class="stars">
        {render_star_cards(top_stars, work_overrides, priority_tracking)}
      </div>
    </section>

    <section class="section">
      <span class="section-mark">热搜人名观察</span>
      <h2>正负向分层</h2>
      <div class="trend-grid">
        {hot_observation_html}
      </div>
    </section>

    <section class="section">
      <span class="section-mark">补充观察</span>
      <h2>名单与内容热区</h2>
      <div class="mini-columns">
        <div>
          <h3>观察名单</h3>
          <div class="watch-grid">{render_watch_cards(watch_candidates, work_overrides, priority_tracking)}</div>
        </div>
        <div>
          <h3>综艺热区</h3>
          <div class="content-grid">{variety_html}</div>
        </div>
        <div>
          <h3>影视热区</h3>
          <div class="content-grid">{film_html}</div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="closing">
        <p>{html.escape(summary_copy)}</p>
      </div>
    </section>
  </main>'''


def write_html(output_path: Path, formatted_date: str, main_html: str) -> None:
    template_text = resolve_template_path().read_text(encoding="utf-8").replace("{{OBSERVATION_DATE}}", formatted_date)
    updated = re.sub(r"<main class=\"poster\">.*?</main>", main_html, template_text, count=1, flags=re.S)
    output_path.write_text(updated, encoding="utf-8")


def run_render(output_path: Path) -> None:
    render_script = skill_root() / "scripts" / "render_observation_png.py"
    subprocess.run(
        [sys.executable, str(render_script), "--html", str(output_path)],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the daily entertainment observation HTML and optionally render PNG.")
    parser.add_argument("--output-dir", default=".", help="Directory for generated output files.")
    parser.add_argument("--output-file", default=None, help="Output HTML filename. Defaults to YYMMDD-prefixed report name.")
    parser.add_argument("--date", dest="raw_date", default=None, help="Date in YYYY.MM.DD, YYYY-MM-DD, or YYYY/MM/DD.")
    parser.add_argument("--render", action="store_true", help="Render the PNG after generating the HTML.")
    parser.add_argument("--alapi-token", default=None, help=f"ALAPI token. Falls back to ${ALAPI_TOKEN_ENV} when omitted.")
    args = parser.parse_args()

    formatted_date = normalize_date(args.raw_date)
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / args.output_file if args.output_file else pick_available_output_path(output_dir, formatted_date)

    work_overrides = load_json(skill_root() / "references" / "work_cast_overrides.json")
    priority_tracking_list = load_json(skill_root() / "references" / "priority_tracking.json")
    priority_tracking = collect_priority_keywords(priority_tracking_list)
    known_names = collect_known_names(work_overrides, priority_tracking)
    alapi_token = args.alapi_token or os.getenv(ALAPI_TOKEN_ENV)

    work_signals: list[WorkSignal] = []
    work_signals.extend(fetch_iqiyi_signals(work_overrides))
    work_signals.extend(fetch_qqvideo_signals(work_overrides))
    work_signals.extend(fetch_maoyan_web_heat(work_overrides))
    tracked_signals = fetch_tracked_pages(work_overrides)
    work_signals.extend(tracked_signals)

    star_scores: dict[str, StarScore] = {}
    for signal in work_signals:
        add_work_signal(star_scores, signal)

    weibo_items = fetch_weibo_entertainment()
    weibo_titles = [item["title"] for item in weibo_items]
    add_mention_signals(
        star_scores,
        priority_tracking,
        weibo_titles,
        "微博娱乐",
        34,
        known_names=known_names,
        allow_bootstrap=True,
    )

    alapi_tophub_items = fetch_alapi_tophub(alapi_token) if alapi_token else []
    alapi_wbtop_items = fetch_alapi_wbtop(alapi_token) if alapi_token else []
    alapi_toutiao_items = fetch_alapi_toutiao(alapi_token) if alapi_token else []
    alapi_tophub_titles = [
        item["title"] for item in alapi_tophub_items
        if is_entertainment_title(item["title"], item.get("hot", ""))
    ]
    alapi_tophub_title_set = set(alapi_tophub_titles)
    alapi_wbtop_titles = [
        item["title"] for item in alapi_wbtop_items
        if item["title"] in alapi_tophub_title_set or is_entertainment_title(item["title"], item.get("hot", ""))
    ]
    add_mention_signals(
        star_scores,
        priority_tracking,
        alapi_wbtop_titles,
        "ALAPI微博热搜",
        16,
        known_names=known_names,
        allow_bootstrap=True,
    )
    add_mention_signals(
        star_scores,
        priority_tracking,
        alapi_tophub_titles,
        "ALAPI今日热榜",
        12,
        known_names=known_names,
        allow_bootstrap=True,
    )
    alapi_toutiao_titles = [item["title"] for item in alapi_toutiao_items if item["title"]]
    add_mention_signals(
        star_scores,
        priority_tracking,
        alapi_toutiao_titles,
        "ALAPI头条热搜",
        14,
        known_names=known_names,
        allow_bootstrap=True,
    )
    douyin_titles = fetch_douyin_hot()
    bilibili_titles = fetch_bilibili_hot_search()
    realtime_counts = {
        "微博热搜": len(weibo_titles),
        "抖音热搜": len(douyin_titles),
        "B站热搜": len(bilibili_titles),
    }
    if not any(realtime_counts.values()):
        raise RuntimeError(f"实时热搜抓取失败：{realtime_counts}")
    if len(weibo_titles) < 10:
        print(f"warning: 微博热搜不足 10 条，当前 {len(weibo_titles)} 条", file=sys.stderr)
    if len(douyin_titles) < 10:
        print(f"warning: 抖音热搜不足 10 条，当前 {len(douyin_titles)} 条", file=sys.stderr)
    if len(bilibili_titles) < 10:
        print(f"warning: B站热搜不足 10 条，当前 {len(bilibili_titles)} 条", file=sys.stderr)
    add_mention_signals(star_scores, priority_tracking, douyin_titles, "抖音热搜", 18, known_names=known_names, allow_bootstrap=True)
    add_mention_signals(star_scores, priority_tracking, bilibili_titles, "B站热搜", 12, known_names=known_names, allow_bootstrap=True)

    top_stars = pick_top_stars(star_scores, work_overrides, priority_tracking, limit=10)
    top_names = {item["star"].name for item in top_stars}
    watch_candidates = [
        item
        for item in rank_star_candidates(star_scores, work_overrides, priority_tracking)
        if item["star"].name not in top_names and infer_risk(item["star"]) != "高风险"
    ]

    variety_signals = sorted(
        [signal for signal in work_signals if signal.category == "variety"],
        key=lambda signal: (-signal.score, signal.rank, signal.title),
    )
    film_signals = sorted(
        [signal for signal in work_signals if signal.category == "film_tv"],
        key=lambda signal: (-signal.score, signal.rank, signal.title),
    )

    main_html = build_main_html(
        formatted_date=formatted_date,
        top_stars=top_stars,
        watch_candidates=watch_candidates,
        star_scores=star_scores,
        realtime_rank_groups=[
            ("微博热搜", weibo_titles),
            ("抖音热搜", douyin_titles),
            ("B站热搜", bilibili_titles),
            ("影视综艺热榜", build_work_hot_titles(variety_signals, film_signals)),
        ],
        variety_signals=variety_signals,
        film_signals=film_signals,
        weibo_titles=weibo_titles,
        alapi_news_titles=alapi_toutiao_titles,
        work_overrides=work_overrides,
        priority_tracking=priority_tracking,
        use_tracked_pages=bool(tracked_signals),
        use_alapi=bool(alapi_tophub_titles or alapi_wbtop_titles),
        use_alapi_news=bool(alapi_toutiao_titles),
    )
    write_html(output_path, formatted_date, main_html)
    print(output_path)

    if args.render:
        run_render(output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
