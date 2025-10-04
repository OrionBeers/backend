"""openai_connection.py
Utility to create an OpenAI client and helper functions.

Usage:
- Set environment variable OPENAI_API_KEY with your key, or pass api_key to get_client().
- Do NOT commit your API key to source control.
"""

import os
from openai import OpenAI

def get_client(api_key: str | None = None) -> OpenAI:
    """Return initialized OpenAI client.

    Priority:
      1) api_key argument
      2) OPENAI_API_KEY environment variable

    Raises:
      RuntimeError if no key found.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OpenAI API key not provided. Set OPENAI_API_KEY env var or pass api_key."
        )
    return OpenAI(api_key=key)

def chat_completion(prompt: str, model: str = "gpt-4o-mini", api_key: str | None = None, max_tokens: int = 512):
    """Send a simple chat completion request and return assistant reply (str)."""
    client = get_client(api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
    )
    # Try typical response structure
    try:
        return resp.choices[0].message.content
    except Exception:
        # Fallback: return raw response for debugging
        return resp

if __name__ == "__main__":
    # Quick local test. Do NOT commit your API key.
    # Before running:
    #   export OPENAI_API_KEY="sk-..."
    import sys

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Say hello and summarize 'It Rain My Parada' project idea in one sentence."

    try:
        reply = chat_completion(prompt)
        print("Assistant response:\n", reply)
    except Exception as e:
        print("Error:", e)