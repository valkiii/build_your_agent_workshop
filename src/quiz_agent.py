# quiz_agent.py — generates 3 comprehension Q&A pairs.
# Only called for approved articles (don't waste a model call on rejects).
import json

import ollama

import config


def generate_quiz(text):
    response = ollama.chat(
        model=config.MODEL_NAME,
        messages=[
            {"role": "system", "content": config.QUIZ_PROMPT},
            {"role": "user", "content": text[:6000]},
        ],
        options={"num_ctx": 8192},
    )
    content = response["message"]["content"].strip()
    content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(content).get("questions", [])
    except json.JSONDecodeError:
        return []
