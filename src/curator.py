# curator.py — Decide step.
# Judges an article summary against the reader's stated interest and returns
# {"approved": bool, "reason": str, "tags": [...]}.
import json

import ollama

import config


def evaluate(summary):
    # Build the prompt per call from the current config values so the Streamlit
    # app's in-session edits to the interest prompt actually take effect.
    system_prompt = config.CURATOR_PROMPT.replace(
        "[READER_INTEREST]", config.INTEREST_PROMPT.strip()
    )
    response = ollama.chat(
        model=config.MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": summary},
        ],
        options={"num_ctx": 8192},
    )
    content = response["message"]["content"].strip()
    content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        result = json.loads(content)
        result.setdefault("approved", False)
        result.setdefault("reason", "")
        result.setdefault("tags", [])  # safety net if the model omits it
        return result
    except json.JSONDecodeError:
        return {"approved": False, "reason": "parse error", "tags": []}
