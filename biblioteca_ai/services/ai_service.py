import json
from typing import Any, Dict, Optional

from ollama import chat

ALLOWED_INTENTS = {
    "count_books_by_category",
    "top_authors_by_loans_month",
    "overdue_loans",
    "get_users",
}

SYSTEM_PROMPT = f"""
Sos un router de consultas para una biblioteca en SQL Server.
Respondé SOLO JSON válido (sin texto extra), con este formato:

{{
  "intent": "<uno de {sorted(ALLOWED_INTENTS)}>",
  "params": {{ ... }},
  "confidence": 0.0
}}

Reglas:
- "¿Cuántos libros hay de X?" -> count_books_by_category + {{ "category_name": "X" }}
- "¿Autores con más préstamos este mes?" -> top_authors_by_loans_month + {{ "year": 2026, "month": 3 }}
- "¿Préstamos vencidos?" -> overdue_loans + params opcional {{ "as_of_date": "YYYY-MM-DD" }}
- "Usuarios" -> get_users
"""

def try_parse_intent(user_text: str, model: str = "llama3.2:3b") -> Optional[Dict[str, Any]]:
    """
    Devuelve dict con intent/params/confidence o None si no es confiable.
    """
    resp = chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        options={"temperature": 0}
    )

    raw = resp["message"]["content"].strip()

    try:
        data = json.loads(raw)
    except Exception:
        return None

    intent = data.get("intent")
    params = data.get("params", {})
    try:
        confidence = float(data.get("confidence", 0.0))
    except Exception:
        confidence = 0.0

    if intent not in ALLOWED_INTENTS:
        return None
    if not isinstance(params, dict):
        params = {}

    if confidence < 0.45:
        return None

    return {"intent": intent, "params": params, "confidence": confidence}


def chat_fallback(user_text: str, model: str = "llama3.2:3b") -> str:
    resp = chat(
        model=model,
        messages=[
            {"role": "system", "content": "Sos un asistente amable de biblioteca. Respondé en español."},
            {"role": "user", "content": user_text},
        ],
        options={"temperature": 0.4}
    )
    return resp["message"]["content"].strip()