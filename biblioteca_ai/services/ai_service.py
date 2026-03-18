"""
Servicio de IA para la biblioteca inteligente.
La IA SOLO responde con datos reales de la base de datos.
"""

import json
from typing import Any, Dict, Optional

from ollama import chat
from services.db_schema_service import DBSchemaService

ALLOWED_INTENTS = {
    "count_books_by_category",
    "top_authors_by_loans_month",
    "overdue_loans",
    "get_users",
    "get_books",
    "search_books",
    "get_authors",
    "get_categories",
    "active_loans",
    "check_book_availability",   # ← NUEVO: verificar si un libro está disponible
    "request_loan",              # ← NUEVO: solicitar préstamo de un libro
}


def _build_system_prompt() -> str:
    """
    Construye el prompt del sistema incluyendo la estructura actual de la BD.
    La IA SOLO puede hablar de datos que existan en la base de datos.
    """
    schema_summary = DBSchemaService.get_schema_summary()

    system_prompt = f"""
ERES EL ASISTENTE OFICIAL DEL SISTEMA DE BIBLIOTECA
====================================================

Tu ÚNICA función es responder consultas sobre la biblioteca usando datos reales de la BD.

RESTRICCIONES ABSOLUTAS (NUNCA las violes):
- ⛔ NO respondas preguntas generales, chistes, saludos extendidos ni nada ajeno a la biblioteca
- ⛔ NO inventes libros, autores, categorías ni usuarios que no existan en la BD
- ⛔ NO des información que no esté en la base de datos
- ⛔ Si el usuario pregunta algo que NO tiene relación con la biblioteca → confianza 0
- ⛔ Si el dato no existe en la BD → confianza 0
- ✅ SOLO responde sobre: libros, préstamos, usuarios, autores, categorías de ESTA biblioteca

{schema_summary}

RESPONDE SOLO CON JSON VÁLIDO (sin texto extra, sin markdown, sin explicaciones):
{{
  "intent": "uno de {sorted(ALLOWED_INTENTS)}",
  "params": {{ ...parámetros según intent }},
  "confidence": 0.0 a 1.0,
  "reasoning": "explicación breve"
}}

REGLAS DE MAPPING:
- "¿Cuántos libros de [categoría]?" → count_books_by_category + {{"category_name": "[categoría]"}}
- "¿Autores con más préstamos en [mes/año]?" → top_authors_by_loans_month + {{"year": YYYY, "month": M}}
- "¿Préstamos vencidos?" → overdue_loans + {{"as_of_date": "YYYY-MM-DD"}} (opcional)
- "Lista de usuarios" → get_users
- "Ver libros / ¿Qué libros hay?" → get_books
- "¿Categorías?" → get_categories
- "¿Autores?" → get_authors
- "Buscar [título]" → search_books + {{"title": "[título]"}}
- "¿Préstamos activos?" → active_loans
- "¿Está disponible [libro]?" → check_book_availability + {{"title": "[título]"}}
- "Quiero sacar / prestar [libro]" → check_book_availability + {{"title": "[título]"}}

VALIDACIONES:
- Si el libro, categoría, autor o usuario no existe en la BD → confianza 0
- Si la fecha es inválida → confianza 0
- Si no tiene relación con la biblioteca → confianza 0
- Preguntas filosóficas, matemáticas, históricas generales, etc. → confianza 0
"""
    return system_prompt


SYSTEM_PROMPT = _build_system_prompt()


def try_parse_intent(user_text: str, model: str = "llama3.2:3b") -> Optional[Dict[str, Any]]:
    """
    Devuelve dict con intent/params/confidence o None si no es confiable.
    Nunca retorna None para forzar un fallback genérico — si no hay intent válido,
    el llamador debe mostrar un mensaje restringido al dominio biblioteca.
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

    # Limpiar posible markdown
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

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


def get_out_of_scope_message() -> str:
    """
    Mensaje estándar cuando la consulta está fuera del dominio de la biblioteca.
    NO usa IA genérica — solo informa al usuario de las capacidades del sistema.
    """
    return (
        "⚠️ Solo puedo responder preguntas relacionadas con esta biblioteca.\n\n"
        "Puedo ayudarte con:\n"
        "• 📚 Ver libros disponibles\n"
        "• 🔍 Buscar un libro por título\n"
        "• 📖 Ver préstamos activos o vencidos\n"
        "• 👥 Consultar usuarios o autores\n"
        "• 📂 Ver categorías\n\n"
        "Ejemplo: '¿Qué libros hay disponibles?' o '¿Está disponible Sapiens?'"
    )