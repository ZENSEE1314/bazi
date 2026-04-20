"""Extract palm-reading traits from a photo using the Ollama vision API.

Same shape as ``faceread.vision``: asks a multimodal Ollama model for a
STRICT JSON object mapping each trait to one of our enum values, clamps
anything out-of-vocab back to a safe default, and returns the dict.

Palm photos are visually noisier than faces — the model is asked to use
'medium' values when it isn't sure, which funnels uncertain features to
neutral interpretations rather than dramatic ones.
"""

from __future__ import annotations

import json
import os
import re
from urllib import error, request

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_VISION_MODEL = os.environ.get(
    "OLLAMA_VISION_MODEL", os.environ.get("OLLAMA_MODEL", "gemma3:4b")
)
OLLAMA_TIMEOUT_SEC = float(os.environ.get("OLLAMA_TIMEOUT_SEC", "120"))

PALM_PROMPT = """You are an expert in Chinese palmistry (手相). Look at the photo of an
outstretched palm and identify 12 features. Respond with ONLY a JSON object,
no prose, no code fences, no explanation.

{
  "hand_shape":     one of "earth" | "air" | "water" | "fire",
  "dominant_hand":  one of "left" | "right",
  "finger_length":  one of "short" | "medium" | "long",
  "life_length":    one of "long" | "medium" | "short" | "absent",
  "life_depth":     one of "deep" | "medium" | "shallow" | "broken",
  "heart_length":   one of "long" | "medium" | "short" | "absent",
  "heart_depth":    one of "deep" | "medium" | "shallow" | "broken",
  "head_length":    one of "long" | "medium" | "short" | "absent",
  "head_depth":     one of "deep" | "medium" | "shallow" | "broken",
  "fate_length":    one of "long" | "medium" | "short" | "absent",
  "fate_depth":     one of "deep" | "medium" | "shallow" | "broken",
  "marriage_lines": one of "none" | "one" | "two" | "many"
}

Hand shape guide:
  earth = square palm, short fingers
  air   = square palm, long fingers
  water = long palm, long fingers
  fire  = long palm, short fingers

Rules:
- Pick EXACTLY one value from each list.
- If a line is hard to see, prefer 'medium' / 'one'. Don't guess wildly.
- If dominant hand can't be determined from the photo, pick 'right'.
- Output JSON ONLY. No commentary.
"""

PALM_ALLOWED: dict[str, list[str]] = {
    "hand_shape":     ["earth", "air", "water", "fire"],
    "dominant_hand":  ["left", "right"],
    "finger_length":  ["short", "medium", "long"],
    "life_length":    ["long", "medium", "short", "absent"],
    "life_depth":     ["deep", "medium", "shallow", "broken"],
    "heart_length":   ["long", "medium", "short", "absent"],
    "heart_depth":    ["deep", "medium", "shallow", "broken"],
    "head_length":    ["long", "medium", "short", "absent"],
    "head_depth":     ["deep", "medium", "shallow", "broken"],
    "fate_length":    ["long", "medium", "short", "absent"],
    "fate_depth":     ["deep", "medium", "shallow", "broken"],
    "marriage_lines": ["none", "one", "two", "many"],
}

_SAFE_DEFAULTS: dict[str, str] = {
    "hand_shape":     "earth",
    "dominant_hand":  "right",
    "finger_length":  "medium",
    "life_length":    "medium", "life_depth":  "medium",
    "heart_length":   "medium", "heart_depth": "medium",
    "head_length":    "medium", "head_depth":  "medium",
    "fate_length":    "medium", "fate_depth":  "medium",
    "marriage_lines": "one",
}


def _strip_data_url(b64: str) -> str:
    if b64.startswith("data:"):
        comma = b64.find(",")
        if comma != -1:
            return b64[comma + 1:]
    return b64


_JSON_OBJ_RE = re.compile(r"\{[^{}]*\}", re.S)


def _parse_json_loose(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    for m in _JSON_OBJ_RE.findall(text):
        try:
            return json.loads(m)
        except Exception:
            continue
    raise ValueError(f"No JSON object in vision reply: {text[:200]!r}")


def _call_ollama_vision(prompt: str, image_b64: str) -> str:
    payload = {
        "model": OLLAMA_VISION_MODEL,
        "messages": [
            {"role": "user", "content": prompt, "images": [_strip_data_url(image_b64)]},
        ],
        "stream": False,
        "options": {"temperature": 0.1, "num_ctx": 4096},
    }
    body = json.dumps(payload).encode("utf-8")
    url = OLLAMA_BASE_URL.rstrip("/") + "/api/chat"
    req = request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with request.urlopen(req, timeout=OLLAMA_TIMEOUT_SEC) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except error.URLError as exc:
        raise RuntimeError(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}. "
            "Deploy an Ollama service with a vision-capable model and set "
            "OLLAMA_VISION_MODEL."
        ) from exc
    except TimeoutError as exc:
        raise RuntimeError(
            "Vision analysis timed out. On CPU-only Ollama this is slow — try "
            "a smaller model (moondream) or bump OLLAMA_TIMEOUT_SEC."
        ) from exc
    msg = data.get("message", {}).get("content", "")
    if not msg:
        raise RuntimeError(f"Ollama returned an empty vision reply: {data}")
    return msg.strip()


def extract_palm_traits(image_b64: str) -> dict[str, str]:
    """Return a dict with all 12 trait keys, each clamped to a legal enum value."""
    raw = _call_ollama_vision(PALM_PROMPT, image_b64)
    try:
        data = _parse_json_loose(raw)
    except Exception as exc:
        raise RuntimeError(f"Vision reply was not valid JSON: {raw[:200]}") from exc

    out: dict[str, str] = dict(_SAFE_DEFAULTS)
    for key, allowed in PALM_ALLOWED.items():
        val = data.get(key)
        if isinstance(val, str) and val.strip().lower() in allowed:
            out[key] = val.strip().lower()
    return out
