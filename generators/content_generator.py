"""
content_generator.py
Generates on-brand social media content for RunesCard using Gemini or OpenAI.
"""

from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Literal

POST_TYPES = [
    "feature_spotlight",
    "engagement_question",
    "educational",
    "milestone_stat",
    "seasonal_trending",
    "call_to_action",
]

PLATFORM_LIMITS = {
    "twitter": 280,
    "farcaster": 320,
}

_CONTEXT_PATH = Path(__file__).parent.parent / "templates" / "runescard_context.txt"


def _load_context() -> str:
    return _CONTEXT_PATH.read_text(encoding="utf-8")


def _build_prompt(platform: str, post_type: str, extra_hint: str = "") -> str:
    context = _load_context()
    char_limit = PLATFORM_LIMITS.get(platform, 280)

    hint_block = f"\nAdditional context / hook: {extra_hint}" if extra_hint else ""

    return f"""You are the social media manager for RunesCard. Use the brand guide below to write a single {platform} post.

=== BRAND GUIDE ===
{context}
===================

Post type: {post_type.replace("_", " ").title()}
Platform: {platform.title()}
Character limit: {char_limit} characters (STRICT — do not exceed)
{hint_block}

Rules:
- Return ONLY the post text. No quotes, no labels, no explanation.
- Respect the character limit strictly.
- Be natural, punchy, and on-brand.
- Include 1–3 relevant hashtags from the brand guide when appropriate.
- Do NOT use em-dashes (—) excessively.
"""


class ContentGenerator:
    """
    Generates social media posts using Gemini (default) or OpenAI.

    Usage:
        gen = ContentGenerator()
        post = gen.generate("twitter", "feature_spotlight")
    """

    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or os.getenv("LLM_PROVIDER", "gemini")).lower()
        self._client = self._init_client()

    # ── client initialisation ───────────────────────────────────────────────

    def _init_client(self):
        if self.provider == "gemini":
            from google import genai  # type: ignore

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise EnvironmentError("GEMINI_API_KEY is not set.")
            return genai.Client(api_key=api_key)

        elif self.provider == "openai":
            from openai import OpenAI  # type: ignore

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise EnvironmentError("OPENAI_API_KEY is not set.")
            return OpenAI(api_key=api_key)

        else:
            raise ValueError(f"Unknown LLM_PROVIDER: '{self.provider}'. Use 'gemini' or 'openai'.")

    # ── generation ──────────────────────────────────────────────────────────

    def generate(
        self,
        platform: Literal["twitter", "farcaster"],
        post_type: str | None = None,
        extra_hint: str = "",
    ) -> str:
        """
        Generate a single post for *platform*.

        Args:
            platform:   "twitter" or "farcaster"
            post_type:  one of POST_TYPES (random if None)
            extra_hint: optional freeform context to steer the LLM

        Returns:
            Generated post text (str)
        """
        if post_type is None:
            post_type = random.choice(POST_TYPES)

        prompt = _build_prompt(platform, post_type, extra_hint)

        if self.provider == "gemini":
            response = self._client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            text = response.text.strip()

        else:  # openai
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.85,
            )
            text = response.choices[0].message.content.strip()

        # Safety trim — never exceed platform limit
        limit = PLATFORM_LIMITS.get(platform, 280)
        if len(text) > limit:
            text = text[: limit - 1].rsplit(" ", 1)[0] + "…"

        return text
