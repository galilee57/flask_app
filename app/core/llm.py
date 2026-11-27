"""Chat Completions client for the configured inference provider."""

import click
import requests
from flask import current_app

MAX_PROMPT_LENGTH = 4000

ERROR_MESSAGES = {
    "configuration": {
        "fr": "Le fournisseur ou le modèle LLM est mal configuré.",
        "en": "The LLM provider or model is misconfigured.",
    },
    "unavailable": {
        "fr": "Le fournisseur LLM est indisponible ou a refusé la requête.",
        "en": "The LLM provider is unavailable or rejected the request.",
    },
    "response": {
        "fr": "Le fournisseur LLM a renvoyé une réponse inattendue.",
        "en": "The LLM provider returned an unexpected response.",
    },
}


class LLMError(Exception):
    pass


def chat_completion(messages, *, tools=None, max_completion_tokens=512):
    """Return the assistant message, including any tool calls for the caller."""
    config = current_app.config
    provider = config["LLM_PROVIDER"]
    headers = {}
    if provider == "local":
        base_url = config["LLM_LOCAL_BASE_URL"]
        model = config["LLM_LOCAL_MODEL"]
    elif provider == "openai" and config["OPENAI_API_KEY"]:
        base_url = "https://api.openai.com/v1"
        model = config["OPENAI_MODEL"]
        headers["Authorization"] = "Bearer " + config["OPENAI_API_KEY"]
    else:
        raise LLMError("configuration")
    if not base_url or not model:
        raise LLMError("configuration")

    payload = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": max_completion_tokens,
    }
    if tools:
        payload["tools"] = tools
    try:
        response = requests.post(
            base_url.rstrip("/") + "/chat/completions",
            headers=headers,
            json=payload,
            timeout=(3, 45),
            allow_redirects=False,
        )
        response.raise_for_status()
    except requests.RequestException:
        raise LLMError("unavailable") from None

    try:
        message = response.json()["choices"][0]["message"]
        if not isinstance(message, dict) or not (
            isinstance(message.get("content"), str) or message.get("tool_calls")
        ):
            raise ValueError
    except (KeyError, IndexError, TypeError, ValueError):
        raise LLMError("response") from None
    return message


def prompt_llm(prompt):
    message = chat_completion([{"role": "user", "content": prompt}])
    if not message.get("content"):
        raise LLMError("response")
    return message["content"]


def register_llm_command(app):
    @app.cli.command("llm-prompt")
    @click.argument("prompt")
    def llm_prompt(prompt):
        """Send one text prompt to the configured LLM."""
        prompt = prompt.strip()
        if not 1 <= len(prompt) <= MAX_PROMPT_LENGTH:
            raise click.BadParameter(f"Enter 1 to {MAX_PROMPT_LENGTH} characters.")
        try:
            click.echo(prompt_llm(prompt))
        except LLMError as exc:
            raise click.ClickException(ERROR_MESSAGES[str(exc)]["en"]) from None
