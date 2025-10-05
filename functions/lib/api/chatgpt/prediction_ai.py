"""Minimal helpers for connecting to the OpenAI API."""

from __future__ import annotations

import os
from typing import Sequence

from openai import OpenAI


def get_client(api_key: str | None = None) -> OpenAI:
    """Create an OpenAI client using the provided key or environment variable."""
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OpenAI API key not provided. Set OPENAI_API_KEY env var or pass api_key."
        )
    return OpenAI(api_key=key)


def send_chat_messages(
    messages: Sequence[dict[str, str]],
    *,
    model: str = "gpt-4o-mini",
    api_key: str | None = None,
    max_tokens: int = 256,
) -> str:
    """Generic helper that sends chat messages and returns the assistant reply."""
    client = get_client(api_key)
    response = client.chat.completions.create(
        model=model,
        messages=list(messages),
        max_tokens=max_tokens,
    )
    try:
        return response.choices[0].message.content or ""
    except Exception:
        return str(response)


def connection_check(api_key: str | None = None) -> str:
    """Return the ID of the first available model to confirm connectivity."""
    client = get_client(api_key)
    models = client.models.list()
    if not models.data:
        raise RuntimeError("No models returned by OpenAI API.")
    return models.data[0].id


if __name__ == "__main__":
    try:
        first_model = connection_check()
        print("Connection successful. First model id:", first_model)
    except Exception as exc:
        print("Connection failed:", exc)
