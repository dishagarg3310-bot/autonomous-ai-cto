"""Copywriter: stats, reviews and FAQ written for THIS business instead of generic sample text.

One small, capped model call returns a JSON object. Every piece is validated and clipped, anything
missing falls back to the generic text, and the result is cached in `site_copy.json` so re-runs
and design tweaks are instant. Set CTO_AI_COPY=0 to skip the call, CTO_REDESIGN=1 to rewrite it.
"""
import json
import os
import re
import time
from pathlib import Path

PROMPT = """You write website copy for a FICTIONAL sample business.
Business: "{name}" ({kind}). Tagline: "{tagline}". Services: {services}. Mood: {mood}.
Reply with ONLY a JSON object, no markdown, in exactly this shape:
{{"stats":[{{"value":"short number like 4.9★, 12k+ or 10 yrs","label":"2-3 words"}}, (exactly 3)],
 "reviews":[{{"quote":"one specific sentence about this business, max 120 chars","name":"First name and initial"}}, (exactly 3)],
 "faq":[{{"q":"a real question customers ask this kind of business","a":"helpful answer in one or two sentences"}}, (exactly 3)]}}"""


def _text(value, limit):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        value = str(value)  # small models often return 4.9 instead of "4.9"
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(c) for c in ".!?")
    return cut[:end + 1] if end > limit * 0.5 else cut.rsplit(" ", 1)[0].rstrip(",;:-") + "…"


# small models rename keys, so accept the usual alternatives
ALIASES = {"value": ("value", "number", "stat", "count"), "label": ("label", "title", "name", "text", "description"),
           "quote": ("quote", "text", "review", "comment", "content"), "name": ("name", "author", "customer", "reviewer", "user"),
           "q": ("q", "question"), "a": ("a", "answer", "response")}


def _get(item, key):
    for alias in ALIASES[key]:
        if alias in item and item[alias] not in (None, ""):
            return item[alias]
    return None


def _items(raw, keys, limits):
    """2-3 dicts whose `keys` are all usable text, else None (-> generic fallback)."""
    if isinstance(raw, dict):  # {"1": {...}, "2": {...}} or a single wrapped list
        raw = next((v for v in raw.values() if isinstance(v, list)), list(raw.values()))
    if not isinstance(raw, list) or len(raw) < 2:
        return None
    out = []
    for item in raw[:3]:
        if isinstance(item, (list, tuple)) and len(item) >= len(keys):  # format used in site_copy.json
            row = [_text(v, n) for v, n in zip(item, limits)]
        elif isinstance(item, dict):
            row = [_text(_get(item, k), n) for k, n in zip(keys, limits)]
        else:
            return None
        if not all(row):
            return None
        out.append(tuple(row))
    return out


def validate(raw) -> dict:
    """Keep only the well-formed parts of the model's answer."""
    if isinstance(raw, dict) and isinstance(raw.get("copy"), dict):
        raw = raw["copy"]
    if not isinstance(raw, dict):
        return {}
    parts = {"stats": _items(raw.get("stats"), ("value", "label"), (10, 26)),
             "reviews": _items(raw.get("reviews") or raw.get("testimonials"), ("quote", "name"), (170, 28)),
             "faq": _items(raw.get("faq") or raw.get("faqs") or raw.get("questions"), ("q", "a"), (90, 240))}
    return {k: v for k, v in parts.items() if v}


def ai_copy(plan) -> dict:
    if os.environ.get("CTO_AI_COPY", "1") == "0":
        return {}
    try:
        import ollama
        timeout = float(os.environ.get("CTO_AI_COPY_TIMEOUT", "240"))
        model = os.environ.get("CTO_MODEL", "qwen2.5-coder:7b")
        print(f"[{time.strftime('%H:%M:%S')}] Copywriter: asking the AI for stats, reviews and FAQ (up to {int(timeout)}s)...", flush=True)
        prompt = PROMPT.format(name=plan["name"], kind=plan["kind"] or "local business", tagline=plan["tagline"],
                               services=", ".join(t for _, t, _ in plan["services"]), mood=plan["look"]["mood"])
        reply = ollama.Client(timeout=timeout).chat(
            model=model, format="json", messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.7, "num_predict": 700})
        content = reply["message"]["content"] if isinstance(reply, dict) else reply.message.content
        text = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.M).strip()
        copy = validate(json.loads(text))
        if copy:
            print("Copywriter: used " + ", ".join(sorted(copy)) + " from the AI.", flush=True)
        else:
            print("Copywriter: the AI answer could not be used, generic text kept. It started with: " + text[:140].replace("\n", " "), flush=True)
        return copy
    except Exception as exc:  # slow, offline or bad JSON -> generic text
        print(f"Copywriter: AI copy unavailable ({type(exc).__name__}); using generic text.", flush=True)
        return {}


def load_or_write(project_dir: Path, plan, allow_ai=True) -> dict:
    cache = project_dir / "site_copy.json"
    if cache.exists() and not os.environ.get("CTO_REDESIGN"):
        try:
            data = json.loads(cache.read_text(encoding="utf-8"))
            return validate(data) if isinstance(data, dict) else {}
        except ValueError:
            pass
    if not allow_ai:
        return {}
    copy = ai_copy(plan)
    if copy:
        cache.write_text(json.dumps(copy, ensure_ascii=False, indent=2), encoding="utf-8")
    return copy


def apply_copy(plan, copy: dict) -> None:
    for key in ("stats", "reviews", "faq"):
        if copy.get(key):
            plan[key] = [tuple(row) for row in copy[key]]
