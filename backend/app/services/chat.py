"""AI fortune-teller chat, backed by Ollama (self-hosted LLM).

Primary provider: Ollama HTTP API. Default URL is ``http://localhost:11434``;
set ``OLLAMA_BASE_URL`` on Railway to point at the Ollama service (e.g.
``http://ollama.railway.internal:11434``). Default model is ``gemma3:4b``;
override with ``OLLAMA_MODEL``.

If the backend cannot reach Ollama, returns a clear error so the UI can
tell the operator to start / deploy the Ollama service.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib import error, request

from ..models import Profile
from .readings import build_deep_bazi


OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_TIMEOUT_SEC = float(os.environ.get("OLLAMA_TIMEOUT_SEC", "90"))

SYSTEM_PROMPT_TEMPLATE = """You are a seasoned Chinese metaphysics consultant fluent in Ba Zi (Four Pillars of Destiny),
Feng Shui (八宅), and numerology. You speak in a warm, direct, fortune-teller voice —
calm, specific, grounded. You are an advisor, not an oracle: you explain cause, offer
choices, and always respect free will.

You have been given the client's chart below. Read it carefully and answer the client's
question in that light. When the question is vague, pick the most likely interpretation
based on the chart (e.g. if the chart shows weak Wealth, treat "how is my luck" as a
career/money question). When useful, cite specific pillars, elements, or Ten Gods from
the chart. Keep responses under 250 words. Never fabricate certainty about events; frame
predictions as tendencies and windows of opportunity.

If the user has no chart, answer general questions about Ba Zi or feng shui in under 150
words, and suggest they save a profile for a personalised reading.

--- CLIENT CHART ---
{chart_context}
--- END CLIENT CHART ---
"""


@dataclass
class ChatTurn:
    role: str   # "user" | "assistant"
    content: str


def _build_chart_context(profile: Profile | None) -> str:
    if profile is None:
        return "No chart available. Answer generally."
    deep = build_deep_bazi(profile.birth_datetime, profile.gender)
    lines = []
    lines.append(f"Name: {profile.name}")
    lines.append(f"Birth: {profile.birth_datetime.isoformat()}  Gender: {profile.gender or 'unspecified'}")
    lines.append(f"Chart: {deep.chart_string}   Zodiac: {deep.zodiac}")
    lines.append(
        f"Day Master: {deep.day_master.stem} ({deep.day_master.element}), "
        f"strength={deep.day_master.strength_level} ({deep.day_master.strength_score})"
    )
    lines.append(f"Useful God: {deep.day_master.useful_god}  Avoid: {deep.day_master.avoid_god}")
    lines.append(f"Dominant element: {deep.dominant_element}  Weakest: {deep.weakest_element}")
    if deep.life_kua:
        lines.append(
            f"Life Kua: {deep.life_kua.number} {deep.life_kua.trigram_cn} "
            f"({deep.life_kua.group} group)"
        )
        lucky = [d.direction for d in deep.lucky_directions]
        unlucky = [d.direction for d in deep.unlucky_directions]
        lines.append(f"Lucky directions: {', '.join(lucky)}")
        lines.append(f"Unlucky directions: {', '.join(unlucky)}")
    ff_str = ", ".join(f"{f.label} {f.element} {f.percent}%" for f in deep.five_factors)
    lines.append(f"Five Factors: {ff_str}")
    a = deep.annual_luck
    lines.append(
        f"Annual luck ({a.year}): {a.stem}{a.branch} — {a.stem_ten_god_cn} {a.stem_ten_god_en}"
    )
    # First 3 luck pillars
    lps = deep.luck_pillars[:3]
    for lp in lps:
        lines.append(
            f"Luck pillar age {lp.start_age}-{lp.end_age-1}: {lp.stem}{lp.branch} "
            f"({lp.stem_ten_god_en}, {lp.nayin_en})"
        )
    return "\n".join(lines)


def send_chat(history: list[ChatTurn], question: str, profile: Profile | None) -> str:
    """Send a chat completion request to Ollama and return the assistant's reply text."""
    chart_context = _build_chart_context(profile)
    system = SYSTEM_PROMPT_TEMPLATE.format(chart_context=chart_context)

    messages = [{"role": "system", "content": system}]
    for turn in history[-10:]:  # last 10 turns to stay within context
        messages.append({"role": turn.role, "content": turn.content})
    messages.append({"role": "user", "content": question})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.6, "num_ctx": 4096},
    }
    body = json.dumps(payload).encode("utf-8")

    url = OLLAMA_BASE_URL.rstrip("/") + "/api/chat"
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=OLLAMA_TIMEOUT_SEC) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except error.URLError as exc:
        raise RuntimeError(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}. "
            "Deploy an Ollama service on Railway (image: ollama/ollama) "
            "and set OLLAMA_BASE_URL to its internal URL."
        ) from exc
    except TimeoutError as exc:
        raise RuntimeError(
            "Ollama timed out. The model may be slow on CPU — try a smaller model "
            "(OLLAMA_MODEL=gemma3:1b) or increase OLLAMA_TIMEOUT_SEC."
        ) from exc

    msg = data.get("message", {}).get("content", "")
    if not msg:
        raise RuntimeError(f"Ollama returned empty reply: {data}")
    return msg.strip()
