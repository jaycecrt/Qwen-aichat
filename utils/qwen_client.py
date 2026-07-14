import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Generator

load_dotenv()

_client = OpenAI(
    api_key=os.getenv("QWEN_API_KEY"),
    base_url=os.getenv("QWEN_BASE_URL"),
)

MODEL = os.getenv("QWEN_MODEL", "Qwen-3.7Max")


def stream_chat(messages: List[Dict[str, str]]) -> Generator[str, None, None]:
    """
    Call Qwen API with streaming enabled.
    Yields each content token as it arrives from the model.
    """
    response = _client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
    )

    for chunk in response:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            yield delta.content
