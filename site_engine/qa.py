"""Quality check for generated websites. Runs after every build, prints a short report, saves `site_qa.json`.

1. Copy check: small models sometimes write placeholders, doubled words, one-word answers or duplicates.
   A part that fails is dropped (the site falls back to the generic text for that part) and reported.
2. Page check: the HTML must be well formed, every nav link needs a matching section, there must be one
   <h1>, and no "undefined" / "None" / "[object" leaks.
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

PLACEHOLDER = re.compile(r"\b(lorem|ipsum|placeholder|tbd|n/?a|xxx|string|your text|insert)\b|\.\.\.$", re.I)
DOUBLED = re.compile(r"\b(\w{2,})\s+\1\b", re.I)
LEAKS = ("undefined", "[object", "NaN", "None", "{{", "}}", "__PROJECT", "__DATA")
VOID = {"meta", "link", "br", "hr", "img", "input", "source", "area", "base", "col", "embed", "param", "track", "wbr", "path", "circle", "stop"}
MIN_LEN = {"stats": (1, 1), "reviews": (25, 2), "faq": (6, 15)}  # (min length of 1st field, min length of 2nd field)


def _bad_text(*fields):
    for text in fields:
        if PLACEHOLDER.search(text) or DOUBLED.search(text):
            return "placeholder or doubled word in " + repr(text[:40])
    return None


def check_copy(copy: dict):
    """Return (clean copy, issues). Parts that fail are removed so generic text is used instead."""
    clean, issues = {}, []
    for part, rows in (copy or {}).items():
        rows = [tuple(r) for r in rows]
        problem = None
        if part == "faq":  # a question must read like one: add the missing "?"
            rows = [(q if q.endswith("?") else q.rstrip(".!") + "?", a) for q, a in rows]
        if len({r[0].lower() for r in rows}) < len(rows):
            problem = "duplicate entries"
        for first, second in rows:
            if problem:
                break
            if len(first) < MIN_LEN.get(part, (1, 1))[0] or len(second) < MIN_LEN.get(part, (1, 1))[1]:
                problem = "entry too short: " + repr((first + " / " + second)[:40])
            elif part == "stats" and not re.search(r"\d", first):
                problem = "stat without a number: " + repr(first)
            else:
                problem = _bad_text(first, second)
        if problem:
            issues.append(f"{part}: {problem} -> generic text used")
        else:
            clean[part] = rows
    return clean, issues


class _Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.ids, self.hrefs, self.h1, self.errors = [], set(), [], 0, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and (a.get("href") or "").startswith("#") and len(a["href"]) > 1:
            self.hrefs.append(a["href"][1:])
        if tag == "h1":
            self.h1 += 1
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"unexpected </{tag}>")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass


def check_page(html: str):
    """Return (number of checks run, issues)."""
    parser = _Structure()
    parser.feed(html)
    body = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", body)
    issues = list(parser.errors[:3])
    if parser.stack:
        issues.append("unclosed tags: " + ", ".join(parser.stack[:3]))
    issues += [f"nav link #{h} has no section" for h in dict.fromkeys(parser.hrefs) if h not in parser.ids]
    if parser.h1 != 1:
        issues.append(f"expected one <h1>, found {parser.h1}")
    issues += [f"text leak: {leak!r}" for leak in LEAKS if leak in text]
    if 'name="viewport"' not in html or "<html lang=" not in html:
        issues.append("missing viewport meta or lang attribute")
    if len(html) > 300_000:
        issues.append("page is unusually large")
    return 7, issues


def report(project_dir: Path, copy_issues, page_checks, page_issues) -> dict:
    result = {"checks": page_checks + 3, "issues": copy_issues + page_issues, "passed": not (copy_issues or page_issues)}
    (project_dir / "site_qa.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    if result["passed"]:
        print(f"Quality check: all {result['checks']} checks passed.", flush=True)
    else:
        print("Quality check: " + str(len(result["issues"])) + " issue(s) found and handled:", flush=True)
        for issue in result["issues"]:
            print("  - " + issue, flush=True)
    return result
