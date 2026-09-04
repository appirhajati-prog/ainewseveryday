"""
HuggingFace Collector
"""
import logging
import requests
from datetime import datetime, timezone
from config import Settings
from utils.helpers import DigestItem, utc_now


def _is_recent(updated_at):
    if not updated_at:
        return False
    try:
        u = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - u).days <= 7
    except Exception:
        return False


def _safe_get(url, settings, params):
    return requests.get(url, params=params, timeout=settings.request_timeout_seconds)


def _human_title(model_id, tags):
    name = model_id.split("/")[-1] if "/" in model_id else model_id
    readable = name.replace("-", " ").replace("_", " ")
    skip = {"pytorch","tf","jax","onnx","safetensors","rust","license","model-index"}
    ok = [t for t in tags if t not in skip]
    if ok:
        return readable + " (" + ", ".join(ok[:2]) + ")"
    return readable


_TASK_MAP = {
    "sentence-similarity": "\u062c\u0633\u062a\u062c\u0648\u06cc \u0645\u0639\u0646\u0627\u06cc\u06cc \u0648 \u0645\u0642\u0627\u06cc\u0633\u0647 \u0645\u062a\u0646",
    "feature-extraction": "\u0627\u0633\u062a\u062e\u0631\u0627\u062c \u0648\u06cc\u0698\u06af\u06cc \u0645\u062a\u0646\u06cc",
    "text-classification": "\u0637\u0628\u0642\u0647\u200c\u0628\u0646\u062f\u06cc \u0645\u062a\u0646",
    "text-generation": "\u062a\u0648\u0644\u06cc\u062f \u0645\u062a\u0646 \u0648 \u0686\u062a\u200c\u0628\u0627\u062a",
    "text-to-image": "\u062a\u0628\u062f\u06cc\u0644 \u0645\u062a\u0646 \u0628\u0647 \u062a\u0635\u0648\u06cc\u0631",
    "image-classification": "\u062a\u0634\u062e\u06cc\u0635 \u062a\u0635\u0627\u0648\u06cc\u0631",
    "question-answering": "\u067e\u0631\u0633\u0634 \u0648 \u067e\u0627\u0633\u062e \u0647\u0648\u0634\u0645\u0646\u062f",
    "summarization": "\u062e\u0644\u0627\u0635\u0647\u200c\u0633\u0627\u0632\u06cc \u0645\u062a\u0646",
    "translation": "\u062a\u0631\u062c\u0645\u0647 \u0645\u0627\u0634\u06cc\u0646\u06cc",
    "fill-mask": "\u062a\u06a9\u0645\u06cc\u0644 \u06a9\u0644\u0645\u0627\u062a \u062c\u0627\u0627\u0641\u062a\u0627\u062f\u0647",
    "token-classification": "\u062a\u0634\u062e\u06cc\u0635 \u0645\u0648\u062c\u0648\u062f\u06cc\u062a (NER)",
}


def _human_description(m):
    dl = m.get("downloads", 0)
    lk = m.get("likes", 0)
    tags = m.get("tags", [])
    pt = m.get("pipeline_tag", "")
    parts = []
    td = _TASK_MAP.get(pt, "")
    if td:
        parts.append("\U0001f527 \u06a9\u0627\u0631\u0628\u0631\u062f: " + td)
    else:
        skip = {"pytorch","tf","jax","onnx","safetensors","rust","license","model-index"}
        top = [t for t in tags if t not in skip][:3]
        if top:
            parts.append("\U0001f3f7\ufe0f \u062d\u0648\u0632\u0647: " + ", ".join(top))
    parts.append("\U0001f4e5 " + str(dl) + " \u062f\u0627\u0646\u0644\u0648\u062f | \u2764\ufe0f " + str(lk) + " \u0644\u0627\u06cc\u06a9")
    return "\n".join(parts)



def collect(settings, logger):
    items = []
    # Models
    try:
        res = _safe_get("https://huggingface.co/api/models", settings, {"sort": "downloads", "direction": "-1", "limit": 3})
        if res.status_code == 200:
            for i, m in enumerate(res.json()[:3]):
                mid = m.get("id", "")
                dl = m.get("downloads", 0)
                lk = m.get("likes", 0)
                tags = m.get("tags", [])
                items.append(DigestItem(
                    title=_human_title(mid, tags),
                    description=_human_description(m),
                    url="https://huggingface.co/" + mid,
                    source="HuggingFace Models",
                    published_at=utc_now(),
                    metadata={"downloads": dl, "likes": lk},
                    is_top_trend=(i == 0),
                    is_new=_is_recent(m.get("lastModified", "")),
                ))
    except Exception as e:
        logger.error("HuggingFace models error: %s" % e)
    # Spaces
    try:
        res = _safe_get("https://huggingface.co/api/spaces", settings, {"sort": "likes", "direction": "-1", "limit": 2})
        if res.status_code == 200:
            for s in res.json()[:2]:
                sid = s.get("id", "")
                lk = s.get("likes", 0)
                sdk = s.get("sdk", "unknown")
                items.append(DigestItem(
                    title=_human_title(sid, []),
                    description="\U0001f3af \u062f\u0645\u0648\u06cc \u0632\u0646\u062f\u0647 \u0647\u0648\u0634 \u0645\u0635\u0646\u0648\u0639\u06cc \u0628\u0627 " + str(lk) + " \u0644\u0627\u06cc\u06a9. \u0633\u0627\u062e\u062a\u200c\u0634\u062f\u0647 \u0628\u0627 " + sdk,
                    url="https://huggingface.co/spaces/" + sid,
                    source="HuggingFace Spaces",
                    published_at=utc_now(),
                    metadata={"likes": lk, "score": lk},
                    is_top_trend=False,
                    is_new=_is_recent(s.get("lastModified", "")),
                ))
    except Exception as e:
        logger.error("HuggingFace spaces error: %s" % e)
    # Datasets
    try:
        res = _safe_get("https://huggingface.co/api/datasets", settings, {"sort": "downloads", "direction": "-1", "limit": 2})
        if res.status_code == 200:
            for d in res.json()[:2]:
                did = d.get("id", "")
                dl = d.get("downloads", 0)
                items.append(DigestItem(
                    title=_human_title(did, []),
                    description="\U0001f4ca \u062f\u06cc\u062a\u0627\u0633\u062a \u067e\u0631\u06a9\u0627\u0631\u0628\u0631\u062f \u0628\u0627 " + str(dl) + " \u062f\u0627\u0646\u0644\u0648\u062f. \u0645\u0646\u0628\u0639 \u0645\u062d\u0628\u0648\u0628 \u0628\u0631\u0627\u06cc \u0622\u0645\u0648\u0632\u0634 \u0645\u062f\u0644",
                    url="https://huggingface.co/datasets/" + did,
                    source="HuggingFace Datasets",
                    published_at=utc_now(),
                    metadata={"downloads": dl},
                    is_top_trend=False,
                    is_new=_is_recent(d.get("lastModified", "")),
                ))
    except Exception as e:
        logger.error("HuggingFace datasets error: %s" % e)
    return items
