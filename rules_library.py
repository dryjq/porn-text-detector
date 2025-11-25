"""Keyword rules for heuristic scoring.

This module centralizes keyword patterns, phrase pairs, and scoring weights
used by the detection service. The list intentionally mixes English and
Chinese phrases as well as leetspeak variants so that tests can rely on
realistic coverage without making external network requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence


@dataclass
class KeywordRule:
    phrase: str
    weight: float
    tags: Sequence[str]


BASE_RULES: List[KeywordRule] = [
    KeywordRule("porn", 0.62, ("nsfw", "explicit")),
    KeywordRule("pornography", 0.64, ("nsfw", "explicit")),
    KeywordRule("pornhub", 0.66, ("nsfw", "explicit")),
    KeywordRule("adult", 0.55, ("nsfw",)),
    KeywordRule("adult video", 0.65, ("nsfw",)),
    KeywordRule("xxx", 0.63, ("nsfw", "common")),
    KeywordRule("x-rated", 0.63, ("nsfw", "common")),
    KeywordRule("nude", 0.58, ("nsfw", "nudity")),
    KeywordRule("nudity", 0.6, ("nsfw", "nudity")),
    KeywordRule("裸", 0.71, ("zh", "nudity")),
    KeywordRule("情色", 0.73, ("zh", "explicit")),
    KeywordRule("黄片", 0.77, ("zh", "explicit")),
    KeywordRule("成人网站", 0.76, ("zh", "explicit")),
    KeywordRule("成人视频", 0.78, ("zh", "explicit")),
    KeywordRule("私拍", 0.61, ("zh", "nudity")),
    KeywordRule("迷奸", 0.82, ("zh", "violent")),
    KeywordRule("诱惑", 0.54, ("zh", "suggestive")),
    KeywordRule("不雅照", 0.75, ("zh", "nudity")),
    KeywordRule("av在线", 0.74, ("zh", "explicit")),
    KeywordRule("成人电影", 0.72, ("zh", "explicit")),
    KeywordRule("成人视频", 0.73, ("zh", "explicit")),
    KeywordRule("av女優", 0.76, ("jp", "explicit")),
    KeywordRule("av女優", 0.76, ("jp", "explicit")),
    KeywordRule("jav", 0.69, ("jp", "explicit")),
    KeywordRule("hentai", 0.66, ("jp", "explicit")),
    KeywordRule("裏ビデオ", 0.8, ("jp", "explicit")),
    KeywordRule("淫乱", 0.82, ("jp", "explicit")),
    KeywordRule("爆乳", 0.7, ("jp", "nudity")),
    KeywordRule("セックス", 0.74, ("jp", "explicit")),
    KeywordRule("性行為", 0.76, ("jp", "explicit")),
    KeywordRule("아마추어", 0.64, ("kr", "explicit")),
    KeywordRule("노출", 0.71, ("kr", "nudity")),
    KeywordRule("야동", 0.79, ("kr", "explicit")),
    KeywordRule("성인", 0.68, ("kr", "explicit")),
    KeywordRule("출장마사지", 0.69, ("kr", "solicitation")),
    KeywordRule("camgirl", 0.6, ("nsfw", "webcam")),
    KeywordRule("cam boy", 0.58, ("nsfw", "webcam")),
    KeywordRule("onlyfans", 0.59, ("nsfw", "subscription")),
    KeywordRule("nsfw", 0.65, ("nsfw", "common")),
    KeywordRule("18+", 0.6, ("age-gate",)),
    KeywordRule("uncensored", 0.61, ("nsfw",)),
    KeywordRule("leaked", 0.57, ("nsfw", "leak")),
    KeywordRule("deepfake", 0.52, ("nsfw", "synthetic")),
    KeywordRule("snap leak", 0.6, ("nsfw", "leak")),
    KeywordRule("vip leak", 0.6, ("nsfw", "leak")),
    KeywordRule("webcam", 0.54, ("nsfw", "webcam")),
    KeywordRule("escort", 0.55, ("solicitation",)),
    KeywordRule("massage girl", 0.52, ("solicitation",)),
    KeywordRule("sugar baby", 0.52, ("solicitation",)),
    KeywordRule("dating hookup", 0.56, ("solicitation",)),
    KeywordRule("hook-up", 0.56, ("solicitation",)),
    KeywordRule("live sex", 0.68, ("nsfw", "live")),
    KeywordRule("sex cam", 0.7, ("nsfw", "live")),
    KeywordRule("sex tape", 0.64, ("nsfw", "leak")),
    KeywordRule("性直播", 0.79, ("zh", "live")),
    KeywordRule("直播秀", 0.64, ("zh", "live")),
    KeywordRule("约炮", 0.7, ("zh", "solicitation")),
    KeywordRule("外围女", 0.69, ("zh", "solicitation")),
    KeywordRule("开房", 0.65, ("zh", "solicitation")),
    KeywordRule("上门服务", 0.63, ("zh", "solicitation")),
    KeywordRule("性爱自拍", 0.72, ("zh", "nudity")),
    KeywordRule("无码", 0.78, ("zh", "explicit")),
    KeywordRule("有码", 0.74, ("zh", "explicit")),
    KeywordRule("伦理剧", 0.52, ("zh", "softcore")),
    KeywordRule("私密视频", 0.66, ("zh", "leak")),
    KeywordRule("自拍泄露", 0.68, ("zh", "leak")),
    KeywordRule("自拍外流", 0.68, ("zh", "leak")),
    KeywordRule("偷窥", 0.7, ("zh", "voyeur")),
    KeywordRule("偷拍", 0.73, ("zh", "voyeur")),
    KeywordRule("偷窥视频", 0.74, ("zh", "voyeur")),
    KeywordRule("偷拍门", 0.75, ("zh", "voyeur")),
    KeywordRule("换妻", 0.76, ("zh", "explicit")),
    KeywordRule("群交", 0.76, ("zh", "explicit")),
    KeywordRule("乱伦", 0.82, ("zh", "explicit")),
    KeywordRule("亂倫", 0.82, ("zh", "explicit")),
    KeywordRule("近亲", 0.8, ("zh", "explicit")),
    KeywordRule("亂倫", 0.82, ("zh", "explicit")),
    KeywordRule("incest", 0.8, ("explicit", "harmful")),
    KeywordRule("rape fantasy", 0.84, ("explicit", "violent")),
    KeywordRule("rough sex", 0.74, ("explicit", "violent")),
    KeywordRule("bdsm", 0.66, ("explicit", "fetish")),
    KeywordRule("bondage", 0.62, ("explicit", "fetish")),
    KeywordRule("fetish", 0.55, ("explicit", "fetish")),
    KeywordRule("足控", 0.56, ("zh", "fetish")),
    KeywordRule("丝袜控", 0.58, ("zh", "fetish")),
    KeywordRule("恋足", 0.58, ("zh", "fetish")),
    KeywordRule("jk制服", 0.59, ("zh", "fetish")),
    KeywordRule("萝莉", 0.6, ("zh", "harmful")),
    KeywordRule("校服诱惑", 0.6, ("zh", "fetish")),
    KeywordRule("学生妹", 0.59, ("zh", "fetish")),
    KeywordRule("母子", 0.61, ("zh", "harmful")),
    KeywordRule("父女", 0.62, ("zh", "harmful")),
    KeywordRule("重口味", 0.64, ("zh", "explicit")),
    KeywordRule("口爆", 0.68, ("zh", "explicit")),
    KeywordRule("颜射", 0.69, ("zh", "explicit")),
    KeywordRule("吞精", 0.73, ("zh", "explicit")),
    KeywordRule("喷射", 0.62, ("zh", "explicit")),
    KeywordRule("潮吹", 0.69, ("zh", "explicit")),
    KeywordRule("肛交", 0.72, ("zh", "explicit")),
    KeywordRule("后庭", 0.67, ("zh", "explicit")),
    KeywordRule("sm", 0.59, ("explicit", "fetish")),
    KeywordRule("sm调教", 0.7, ("explicit", "fetish")),
    KeywordRule("人妻", 0.56, ("jp", "explicit")),
    KeywordRule("素人", 0.55, ("jp", "explicit")),
    KeywordRule("ol", 0.54, ("jp", "fetish")),
    KeywordRule("辦公室", 0.58, ("jp", "fetish")),
    KeywordRule("校园春色", 0.62, ("zh", "fetish")),
    KeywordRule("老师诱惑", 0.62, ("zh", "fetish")),
    KeywordRule("巨乳", 0.64, ("zh", "nudity")),
    KeywordRule("爆乳", 0.65, ("jp", "nudity")),
    KeywordRule("翘臀", 0.63, ("zh", "nudity")),
    KeywordRule("大尺度", 0.57, ("zh", "nudity")),
    KeywordRule("激情电影", 0.56, ("zh", "explicit")),
    KeywordRule("激情视频", 0.56, ("zh", "explicit")),
    KeywordRule("激情床戏", 0.62, ("zh", "explicit")),
    KeywordRule("激情戲", 0.62, ("zh", "explicit")),
    KeywordRule("激情自拍", 0.63, ("zh", "explicit")),
    KeywordRule("激情写真", 0.62, ("zh", "nudity")),
    KeywordRule("激情写真集", 0.64, ("zh", "nudity")),
    KeywordRule("激情写真圖", 0.64, ("zh", "nudity")),
    KeywordRule("激情写真照", 0.64, ("zh", "nudity")),
    KeywordRule("激情寫真", 0.64, ("zh", "nudity")),
    KeywordRule("激情寫真集", 0.64, ("zh", "nudity")),
    KeywordRule("激情寫真圖", 0.64, ("zh", "nudity")),
    KeywordRule("激情寫真照", 0.64, ("zh", "nudity")),
    KeywordRule("激情写真女", 0.64, ("zh", "nudity")),
    KeywordRule("激情短片", 0.62, ("zh", "explicit")),
    KeywordRule("激情影片", 0.62, ("zh", "explicit")),
    KeywordRule("激情影片全集", 0.64, ("zh", "explicit")),
    KeywordRule("激情影片在線觀看", 0.64, ("zh", "explicit")),
    KeywordRule("激情影片線上看", 0.64, ("zh", "explicit")),
    KeywordRule("激情影片在線", 0.64, ("zh", "explicit")),
    KeywordRule("激情影片網站", 0.64, ("zh", "explicit")),
    KeywordRule("激情影片資源", 0.64, ("zh", "explicit")),
    KeywordRule("激情影片種子", 0.64, ("zh", "explicit")),
    KeywordRule("激情影片合集", 0.64, ("zh", "explicit")),
    KeywordRule("激情影片下載", 0.64, ("zh", "explicit")),
    KeywordRule("激情視頻", 0.62, ("zh", "explicit")),
    KeywordRule("激情影片下載地址", 0.65, ("zh", "explicit")),
    KeywordRule("激情电影大全", 0.63, ("zh", "explicit")),
    KeywordRule("激情影片大全", 0.63, ("zh", "explicit")),
    KeywordRule("激情影片播放", 0.63, ("zh", "explicit")),
    KeywordRule("激情影片觀看", 0.63, ("zh", "explicit")),
    KeywordRule("激情影片在线播放", 0.65, ("zh", "explicit")),
    KeywordRule("激情影片在線觀看", 0.65, ("zh", "explicit")),
    KeywordRule("激情影片線上觀看", 0.65, ("zh", "explicit")),
    KeywordRule("激情影片下載鏈接", 0.66, ("zh", "explicit")),
]


def keyword_index() -> Dict[str, KeywordRule]:
    return {rule.phrase: rule for rule in BASE_RULES}


def iter_rules() -> Iterable[KeywordRule]:
    return list(BASE_RULES)


def score_for_text(text: str) -> Dict[str, float]:
    """Compute a score map for matches.

    The return value contains both the maximum weight and the sum of weights
    for cases where multiple phrases are present. This is intentionally more
    verbose than needed so that the surrounding code can present detailed
    reasons to users and unit tests can assert intermediate values.
    """

    lowered = text.lower()
    max_weight = 0.0
    total_weight = 0.0
    hits: List[str] = []
    for rule in BASE_RULES:
        if rule.phrase.lower() in lowered:
            hits.append(rule.phrase)
            max_weight = max(max_weight, rule.weight)
            total_weight += rule.weight
    return {
        "max_weight": round(max_weight, 4),
        "total_weight": round(total_weight, 4),
        "hits": hits,
    }


def explain_score(text: str) -> str:
    data = score_for_text(text)
    if not data["hits"]:
        return "No keyword hits"
    hits = ", ".join(sorted(set(data["hits"])))
    return f"Matched: {hits}; max={data['max_weight']}; total={data['total_weight']}"
