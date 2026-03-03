"""
twitter.py
Publishes posts to Twitter/X using Tweepy (OAuth 1.0a, v2 API).
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


class TwitterPublisher:
    """
    Posts a tweet using the Twitter v2 API via Tweepy.

    Requires in .env:
        TWITTER_API_KEY
        TWITTER_API_SECRET
        TWITTER_ACCESS_TOKEN
        TWITTER_ACCESS_TOKEN_SECRET
    """

    def __init__(self) -> None:
        try:
            import tweepy  # type: ignore
        except ImportError:
            raise ImportError("tweepy is not installed. Run: pip install tweepy")

        self._client = tweepy.Client(
            consumer_key=self._require("TWITTER_API_KEY"),
            consumer_secret=self._require("TWITTER_API_SECRET"),
            access_token=self._require("TWITTER_ACCESS_TOKEN"),
            access_token_secret=self._require("TWITTER_ACCESS_TOKEN_SECRET"),
        )

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
        Post a tweet.

        Returns:
            dict with 'id' and 'text' of the created tweet.
        """
        if len(text) > 280:
            raise ValueError(f"Tweet exceeds 280 chars ({len(text)}).")

        response = self._client.create_tweet(text=text)
        tweet_id = response.data["id"]
        logger.info(f"[Twitter] Posted tweet ID: {tweet_id}")
        return {"id": tweet_id, "text": text}
