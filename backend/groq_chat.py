"""
Groq chat integration for the crop disease advisor.
"""

import json
import os
from pathlib import Path

from django.conf import settings
try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - runtime dependency is installed in deployment.
    OpenAI = None


GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MAX_MESSAGE_CHARS = 2200
MAX_HISTORY_MESSAGES = 8
CONFIG_ALIASES = {
    "GROQ_API_KEY": ("GROQ_API_KEY", "GROQ_KEY", "GROQ_APIKEY"),
    "GROQ_MODEL": ("GROQ_MODEL",),
}
MODEL_FALLBACKS = (
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-20b",
    "llama-3.1-8b-instant",
)

SYSTEM_PROMPT = """
You are CropCare AI, a practical crop disease and pest advisor inside a
Django crop disease detection app.

Answer with useful, field-ready guidance for farmers and students. Prefer:
- likely meaning of the detected condition when context is provided
- immediate actions
- treatment or management options
- prevention steps
- when to consult a local agriculture extension officer

Be detailed but readable. Do not invent a diagnosis when the image result is
missing or uncertain. If pesticide, fungicide, bactericide, or fertilizer use is
discussed, advise the user to follow local labels and local expert guidance.
Keep the response focused on crop health, plant disease, pests, nutrition,
irrigation, sanitation, and prevention.
""".strip()


class GroqChatError(Exception):
    """Expected chatbot failure that can be shown safely to the UI."""

    def __init__(self, user_message, status_code=502):
        super().__init__(user_message)
        self.user_message = user_message
        self.status_code = status_code


def get_chat_response(message, history=None, context=None):
    api_key = _resolve_config("GROQ_API_KEY")
    if not api_key:
        raise GroqChatError(
            "Groq API key is not configured on the server.",
            status_code=500,
        )

    if OpenAI is None:
        raise GroqChatError(
            "Chatbot dependency `openai` is not installed on the server. Install project requirements and restart the backend.",
            status_code=500,
        )

    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    messages = _build_messages(message, history, context)
    configured_model = _resolve_config("GROQ_MODEL", "llama-3.3-70b-versatile")

    for model in _candidate_models(configured_model):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.55,
                top_p=0.9,
                max_tokens=900,
            )
            reply = _extract_chat_reply(completion)
            if reply:
                return reply
        except Exception as exc:
            if _should_retry_model(exc, model, configured_model):
                continue
            raise GroqChatError(_format_client_error(exc)) from exc

    raise GroqChatError(
        "Groq did not return a response for any configured model. Check model permissions on the server."
    )


def _resolve_config(name, default=""):
    names = CONFIG_ALIASES.get(name, (name,))

    # Prefer live process environment first so the chatbot picks up server-side
    # config updates without depending on settings.py import-time caching.
    for candidate in names:
        value = os.environ.get(candidate, "")
        if value:
            return _normalize_config_value(value)

    env_file = Path(getattr(settings, "BASE_DIR", Path.cwd())) / ".env"
    try:
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, raw_value = line.split("=", 1)
            if key.strip() in names:
                return _normalize_config_value(raw_value)
    except OSError:
        pass

    # Fallback to settings for compatibility with existing deployments, but
    # only after checking the live environment and local .env file.
    for candidate in names:
        value = getattr(settings, candidate, "")
        if value:
            return _normalize_config_value(value)

    return default


def _normalize_config_value(value):
    text = str(value).strip()
    if text.lower().startswith("bearer "):
        text = text[7:].strip()
    return text.strip('"').strip("'")


def _build_messages(message, history, context):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    context_message = _format_prediction_context(context)
    if context_message:
        messages.append({"role": "system", "content": context_message})

    for item in _sanitize_history(history):
        messages.append(item)

    messages.append({"role": "user", "content": _clean_text(message)})
    return messages


def _candidate_models(configured_model):
    ordered = []

    for model in (configured_model, os.environ.get("GROQ_MODEL", "")):
        if model and model not in ordered:
            ordered.append(model)

    for model in MODEL_FALLBACKS:
        if model not in ordered:
            ordered.append(model)

    return ordered


def _should_retry_model(exc, model, configured_model):
    status_code = getattr(exc, "status_code", None)
    message = str(exc).lower()

    if model != configured_model:
        return False

    if status_code in {400, 404, 405, 422}:
        return True

    return (
        "unknown request url" in message
        or "unknown_url" in message
        or "model" in message and "permission" in message
        or "not found" in message and "model" in message
    )


def _extract_chat_reply(completion):
    choices = getattr(completion, "choices", None)
    if not choices:
        return ""

    first = choices[0]
    message = getattr(first, "message", None)
    content = getattr(message, "content", "")
    if isinstance(content, list):
        return "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    return str(content or "").strip()


def _format_client_error(exc):
    status_code = getattr(exc, "status_code", None)
    message = str(exc).strip()

    if status_code in {401, 403}:
        return "Groq rejected the configured API key or account permissions."
    if status_code == 429:
        return "Groq rate limit reached. Wait a moment and try again."
    if status_code in {400, 404, 405, 422} and message:
        return f"Groq API error: {message}"
    if message:
        return f"Groq API error: {message}"
    return "Groq API error."


def _sanitize_history(history):
    if not isinstance(history, list):
        return []

    cleaned = []
    for item in history[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(item, dict):
            continue

        role = item.get("role")
        content = _clean_text(item.get("content", ""))
        if role in {"user", "assistant"} and content:
            cleaned.append({"role": role, "content": content})

    return cleaned


def _format_prediction_context(context):
    if not isinstance(context, dict):
        return ""

    prediction = _clean_text(context.get("prediction", ""), 140)
    raw_class = _clean_text(context.get("class_raw", ""), 140)
    detected = context.get("detected")
    confidence = context.get("confidence")
    recommendation = context.get("recommendation") or {}

    if not prediction and not raw_class:
        return ""

    try:
        confidence_pct = f"{float(confidence) * 100:.1f}%"
    except (TypeError, ValueError):
        confidence_pct = "not provided"

    lines = [
        "Current image scan context from the app:",
        f"- Displayed result: {prediction or 'not provided'}",
        f"- Raw model class: {raw_class or 'not provided'}",
        f"- Detected object: {'yes' if detected else 'no'}",
        f"- Confidence: {confidence_pct}",
    ]

    if isinstance(recommendation, dict):
        title = _clean_text(recommendation.get("title", ""), 160)
        steps = recommendation.get("steps")
        if title:
            lines.append(f"- Existing app recommendation title: {title}")
        if isinstance(steps, list) and steps:
            compact_steps = [
                _clean_text(step, 220)
                for step in steps[:5]
                if _clean_text(step, 220)
            ]
            if compact_steps:
                lines.append("- Existing app recommendation steps:")
                lines.extend(f"  - {step}" for step in compact_steps)

    lines.append(
        "Use this context when relevant, but do not claim the image model is more certain than the confidence shown."
    )
    return "\n".join(lines)


def _clean_text(value, max_chars=MAX_MESSAGE_CHARS):
    if value is None:
        return ""

    text = str(value).strip()
    if len(text) > max_chars:
        return text[:max_chars].rstrip()
    return text


def _format_groq_error(status_code, body):
    try:
        parsed = json.loads(body)
        detail = parsed.get("error", {}).get("message") or parsed.get("message")
        if detail:
            return f"Groq API error: {detail}"
    except (json.JSONDecodeError, AttributeError):
        pass

    if status_code in {401, 403}:
        return "Groq rejected the configured API key or account permissions."
    if status_code == 429:
        return "Groq rate limit reached. Wait a moment and try again."

    return f"Groq API error (HTTP {status_code})."
