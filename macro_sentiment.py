from __future__ import annotations

import re

import feedparser
from textblob import TextBlob


FEEDS = [
    "https://news.google.com/rss/search?q=Pakistan+economy",
    "https://news.google.com/rss/search?q=IMF+Pakistan",
    "https://news.google.com/rss/search?q=SBP+interest+rate",
    "https://news.google.com/rss/search?q=KSE-100",
    "https://news.google.com/rss/search?q=Pakistan+rupee+dollar",
    "https://www.dawn.com/feeds/business",
    "https://www.thenews.com.pk/rss/2/8",
]

POSITIVE = {"approval", "tranche", "surplus", "growth", "cut", "bullish", "rally", "record", "inflows", "cpec"}
NEGATIVE = {"default", "inflation", "surge", "depreciation", "deficit", "hike", "bearish", "fall", "crisis", "oil"}


def _keyword_score(text: str) -> float:
    """Score Pakistan macro keywords. / پاکستان macro keywords کو score کریں۔"""
    words = set(re.findall(r"[a-z]+", text.lower()))
    return (len(words & POSITIVE) - len(words & NEGATIVE)) / 10


def _macro_rules(text: str) -> tuple[float, list[str]]:
    """Pakistan-specific hardcoded macro links. / پاکستان مخصوص macro تعلقات۔"""
    t, reasons, score = text.lower(), [], 0.0
    if "oil" in t and ("surge" in t or "rise" in t):
        score -= 0.3; reasons.append("Oil surge hurts Pakistan import bill / تیل اضافہ درآمدی بل بڑھاتا ہے")
    if "imf" in t and ("approval" in t or "tranche" in t):
        score += 0.5; reasons.append("IMF tranche approval bullish / IMF قسط منظوری bullish")
    if "fed" in t and "cut" in t:
        score += 0.2; reasons.append("Fed cut supports EM flows / Fed cut EM flows کے لیے مثبت")
    if ("pkr" in t or "rupee" in t) and ("depreci" in t or "fall" in t):
        score -= 0.25; reasons.append("PKR depreciation broadly negative / PKR کمزوری عمومی منفی")
    if "cpec" in t:
        score += 0.25; reasons.append("CPEC positive for cement steel energy / CPEC cement steel energy مثبت")
    if ("sbp" in t or "policy rate" in t) and "cut" in t:
        score += 0.25; reasons.append("SBP cut helps leveraged sectors / SBP cut leveraged sectors کے لیے مثبت")
    return score, reasons


def get_macro_sentiment() -> dict:
    """Return daily macro multiplier -1..1. / روزانہ macro multiplier -1..1 دیں۔"""
    headlines: list[str] = []
    for url in FEEDS:
        try:
            headlines += [e.get("title", "") for e in feedparser.parse(url).entries[:10]]
        except Exception:
            continue

    if not headlines:
        return {"score": 0.0, "headlines": [], "reasons": ["No RSS data / RSS data نہیں ملا"]}

    text = " ".join(headlines)
    blob_score = sum(TextBlob(h).sentiment.polarity for h in headlines) / max(len(headlines), 1)
    rule_score, reasons = _macro_rules(text)
    score = max(-1.0, min(1.0, blob_score + _keyword_score(text) + rule_score))
    return {"score": round(score, 3), "headlines": headlines[:8], "reasons": reasons}
