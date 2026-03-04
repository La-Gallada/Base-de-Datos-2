from services import ai_service
from services.biblioteca_service import run_intent_safely


def ask_biblioteca(user_text: str) -> str:
    intent_data = ai_service.try_parse_intent(user_text)

    if intent_data is None:
        return ai_service.chat_fallback(user_text)

    try:
        return run_intent_safely(intent_data)
    except Exception:
        return ai_service.chat_fallback(user_text)