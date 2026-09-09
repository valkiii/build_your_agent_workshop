# summarizer.py — Extract step, LLM summarization.
import ollama

import config


def summarize(text):
    response = ollama.chat(
        model=config.MODEL_NAME,
        messages=[
            {"role": "system", "content": config.SUMMARIZER_PROMPT},
            {"role": "user", "content": text[:6000]},
        ],
        options={"num_ctx": 8192},
    )
    return response["message"]["content"].strip()
