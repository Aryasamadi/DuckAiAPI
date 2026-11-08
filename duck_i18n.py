import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_lang = (os.environ.get("DUCKAI_LANG", "") or "en").strip().lower()
if _lang not in ("en", "fa"):
    _lang = "en"


def set_lang(lang: str | None) -> None:
    global _lang
    if lang:
        _lang = lang if lang in ("en", "fa") else "en"


def get_lang() -> str:
    return _lang


try:
    with open(os.path.join(HERE, "lang_fa.json"), encoding="utf-8") as fh:
        _FA = json.load(fh)
except (OSError, ValueError):
    _FA = {}


def _(s: str) -> str:
    if _lang == "fa":
        return _FA.get(s, s)
    return s
