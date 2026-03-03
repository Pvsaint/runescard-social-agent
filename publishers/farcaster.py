"""
farcaster.py
Publishes casts to Farcaster via the Neynar REST API (no local signing required).
"""

from __future__ import annotations

import logging
import os

import requests

logger = logging.getLogger(__name__)

NEYNAR_CAST_URL = "https://api.neynar.com/v2/farcaster/cast"


class FarcasterPublisher:
    """
    Posts a cast to Farcaster using Neynar's managed signer API.

    Requires in .env:
        NEYNAR_API_KEY        — your Neynar API key
        FARCASTER_SIGNER_UUID — UUID of the managed signer for your account
                                (create one at https://dev.neynar.com)
    """

    def __init__(self) -> None:
        self._api_key = self._require("NEYNAR_API_KEY")
        self._signer_uuid = self._require("FARCASTER_SIGNER_UUID")

    @staticmethod
    def _require(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise EnvironmentError(
                f"{key} is not set. Add it to your .env file."
            )
        return value

    def post(self, text: str) -> dict:
        """
        Publish a cast.

        Args:
            text: Cast text (≤320 chars recommended)

        Returns:
            dict with 'hash' of the published cast.
        """
        if len(text) > 320:
            raise ValueError(f"Cast exceeds 320 chars ({len(text)}).")

        headers = {
            "accept": "application/json",
            "api_key": self._api_key,
            "content-type": "application/json",
        }
        payload = {
            "signer_uuid": self._signer_uuid,
            "text": text,
        }

        response = requests.post(NEYNAR_CAST_URL, json=payload, headers=headers, timeout=15)

        if not response.ok:
            raise RuntimeError(
                f"Neynar API error {response.status_code}: {response.text}"
            )

        data = response.json()
        cast_hash = data.get("cast", {}).get("hash", "unknown")
        logger.info(f"[Farcaster] Published cast hash: {cast_hash}")
        return {"hash": cast_hash, "text": text}
