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

LANGUAGE_INSTRUCTION = {
    "en": (
        "Respond in clear, warm English. Write for someone who has never "
        "studied Chinese metaphysics before. Any Chinese term you use must be "
        "explained in a short phrase right after it, e.g. '日主 (Day Master — "
        "the element that represents you)'."
    ),
    "zh": (
        "请用简体中文回答。读者是普通人，不一定懂命理术语。"
        "使用任何专业词（如日主、用神、十神、纳音、大运）时，请立即用一句大白话解释一下。"
        "语气温和、具体、像朋友聊天。"
    ),
    "ms": (
        "Jawab dalam Bahasa Melayu yang mesra dan mudah difahami. "
        "Pembaca mungkin tidak pernah belajar metafizik Cina — setiap kali anda "
        "guna istilah Cina (日主, 用神, dll), terangkan secara ringkas dalam "
        "bahasa biasa sejurus selepas istilah tersebut."
    ),
}

SYSTEM_PROMPT_TEMPLATE = """You are a seasoned Chinese metaphysics consultant who is known
for explaining charts in a way that anyone can understand. You are fluent in Ba Zi (Four
Pillars), Feng Shui (八宅) and numerology, but you never hide behind jargon.

=== HOW YOU TALK ===

1. PLAIN LANGUAGE FIRST.
   The client is not a scholar. Never dump raw terms on them. Every time you
   use a technical word (Day Master, Useful God, Ten Gods, Luck Pillar, Nayin,
   Life Kua, Sheng Qi, 日主, 用神, 十神, 大运, 流年…), define it in one short
   phrase the first time it appears. Example:

       "Your Useful God is Water — in plain terms, Water is the element that
       most nourishes you. Things associated with Water (careers in finance
       or travel, the direction North, deep blue colors) give you a boost."

2. FRIENDLY ANALOGIES.
   Use everyday pictures so the client can feel the idea:
   - Day Master  ≈ your core self, the captain of your ship.
   - Useful God  ≈ your vitamin — what nourishes you.
   - Avoid God   ≈ your kryptonite — what drains you.
   - Luck Pillar ≈ the weather of a ten-year season of your life.
   - Annual Luck ≈ this year's weather, inside the larger season.
   - Ten Gods    ≈ the roles people and forces play in your life (mentor,
                   partner, rival, child, wealth, etc.).

3. CLEAR STRUCTURE.
   - Open with ONE short headline sentence — the big takeaway.
   - Then 2–4 short paragraphs (2–3 sentences each) explaining it.
   - Close with 1–3 things the client can actually do this month.
   Use blank lines between paragraphs — the UI renders them.

4. ADVISOR, NOT ORACLE.
   Frame everything as tendencies, seasons, and choices — never fixed
   destiny. Respect free will. When you predict, say "more likely" or "a
   good window for…", not "you will".

5. BE SPECIFIC TO THIS CHART.
   Read the client chart below carefully and ground your answer in what's
   actually there — specific pillars, elements, Ten Gods, directions. Don't
   give generic fortune-cookie answers.

6. LENGTH.
   Around 200–280 words. If the question is tiny ("what's my zodiac?"),
   answer in 2–3 sentences. Don't pad.

=== SPECIAL CASE: "EXPLAIN MY CHART" ===

If the client asks you to explain their chart, use this structure:

   • The big picture — one sentence: who are you, at your core?
   • Your element (Day Master) in plain words + what that means socially.
   • Your Useful God & Avoid God as "your vitamin" / "your kryptonite".
   • The current season: where the 10-year Luck Pillar + this year's Annual
     Luck are pointing.
   • One practical suggestion for the next 3 months.

{language_instruction}

If the client has no chart, say so warmly in 1–2 sentences and suggest they
save a profile. Keep general explanations under 150 words.

=== CLIENT CHART ===
{chart_context}
=== END CLIENT CHART ==="""


@dataclass
class ChatTurn:
    role: str   # "user" | "assistant"
    content: str


def _build_chart_context(profile: Profile | None) -> str:
    """Render the profile's deep reading into a clear, labelled block the
    LLM can cite directly. Uses plain English labels the model can echo back
    verbatim when explaining the chart."""
    if profile is None:
        return "No chart available. Answer generally."
    deep = build_deep_bazi(profile.birth_datetime, profile.gender)
    lines: list[str] = []
    lines.append(f"Name: {profile.name}")
    lines.append(
        f"Born: {profile.birth_datetime.isoformat()} | "
        f"Gender: {profile.gender or 'unspecified'} | Zodiac: {deep.zodiac}"
    )
    lines.append("")
    lines.append(f"Four Pillars (year/month/day/hour): {deep.chart_string}")
    lines.append(
        f"Day Master (core self): {deep.day_master.stem} "
        f"({deep.day_master.element}), strength = {deep.day_master.strength_level}"
    )
    lines.append(
        f"Useful God (what nourishes you): {deep.day_master.useful_god}"
    )
    lines.append(
        f"Avoid God (what drains you): {deep.day_master.avoid_god}"
    )
    lines.append(
        f"Dominant element in the chart: {deep.dominant_element} | "
        f"Weakest: {deep.weakest_element}"
    )
    if deep.life_kua:
        lines.append(
            f"Life Kua (feng shui number): {deep.life_kua.number} "
            f"{deep.life_kua.trigram_cn} ({deep.life_kua.group} group)"
        )
        lucky = [d.direction for d in deep.lucky_directions]
        unlucky = [d.direction for d in deep.unlucky_directions]
        lines.append(f"Lucky directions: {', '.join(lucky)}")
        lines.append(f"Unlucky directions: {', '.join(unlucky)}")
    lines.append("")
    lines.append("Life-area strength (Five Factors):")
    for f in deep.five_factors:
        lines.append(f"  - {f.label}: {f.percent:.0f}% ({f.element})")
    lines.append("")
    a = deep.annual_luck
    lines.append(
        f"This year's Annual Luck ({a.year}): {a.stem}{a.branch} — "
        f"{a.stem_ten_god_en} ({a.stem_ten_god_cn})"
    )
    if a.note:
        lines.append(f"  Note: {a.note}")
    lines.append("")
    lines.append("Upcoming 10-year Luck Pillars (first 3):")
    for lp in deep.luck_pillars[:3]:
        lines.append(
            f"  - Age {lp.start_age}-{lp.end_age-1}: {lp.stem}{lp.branch} "
            f"({lp.stem_ten_god_en}, Nayin: {lp.nayin_en})"
        )
    if deep.color_palette_favor:
        lines.append("")
        lines.append(f"Favored colors: {', '.join(deep.color_palette_favor[:6])}")
    if deep.lucky_numbers:
        lines.append(f"Lucky numbers: {', '.join(str(n) for n in deep.lucky_numbers)}")
    if deep.best_careers:
        lines.append(f"Career themes: {', '.join(deep.best_careers[:6])}")
    return "\n".join(lines)


def send_chat(history: list[ChatTurn], question: str, profile: Profile | None, language: str = "en") -> str:
    """Send a chat completion request to Ollama and return the assistant's reply text."""
    chart_context = _build_chart_context(profile)
    lang_instr = LANGUAGE_INSTRUCTION.get(language, LANGUAGE_INSTRUCTION["en"])
    system = SYSTEM_PROMPT_TEMPLATE.format(
        chart_context=chart_context,
        language_instruction=lang_instr,
    )

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
