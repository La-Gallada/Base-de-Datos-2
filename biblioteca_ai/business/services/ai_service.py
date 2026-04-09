"""
Servicio de IA para la biblioteca inteligente.
La IA SOLO responde con datos reales de la base de datos.
"""

import json
from typing import Any, Dict, Optional

from ollama import chat
from .db_schema_service import DBSchemaService

ALLOWED_INTENTS = {
    "count_books_by_category",
    "top_authors_by_loans_month",
    "overdue_loans",
    "get_users",
    "get_books",
    "search_books",
    "search_books_by_author",     # ← NUEVO: buscar libros por autor
    "search_books_by_year",        # ← NUEVO: buscar libros por año de publicación
    "search_books_by_genre",       # ← NUEVO: buscar libros por género/categoría avanzado
    "get_book_recommendations",    # ← NUEVO: obtener recomendaciones de libros
    "get_author_books",            # ← NUEVO: obtener todos los libros de un autor
    "get_books_by_year_range",     # ← NUEVO: obtener libros en un rango de años
    "compare_authors",             # ← NUEVO: comparar estadísticas de autores
    "get_most_loaned_books",       # ← NUEVO: obtener libros más prestados
    "get_least_loaned_books",      # ← NUEVO: obtener libros menos prestados
    "get_authors",
    "get_categories",
    "active_loans",
    "check_book_availability",     # Verificar si un libro está disponible
    "request_loan",                # Solicitar préstamo de un libro
    "get_loan_history",            # ← NUEVO: obtener historial de préstamos de un usuario
    "get_category_stats",          # ← NUEVO: estadísticas de una categoría
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

=== BÚSQUEDAS BÁSICAS ===
- "¿Cuántos libros de [categoría]?" → count_books_by_category + {{"category_name": "[categoría]"}}
- "¿Autores con más préstamos en [mes/año]?" → top_authors_by_loans_month + {{"year": YYYY, "month": M}}
- "¿Préstamos vencidos?" → overdue_loans + {{"as_of_date": "YYYY-MM-DD"}} (opcional)
- "Lista de usuarios" → get_users
- "Ver libros / ¿Qué libros hay? / ¿Qué libros hay disponibles? / Lista de libros" → get_books
- "¿Categorías? / Ver categorías" → get_categories
- "¿Autores? / Ver autores" → get_authors
- "Buscar [título]" → search_books + {{"title": "[título]"}}
- "¿Préstamos activos? / Ver préstamos activos" → active_loans
- "¿Está disponible [libro]? / Disponibilidad de [libro]" → check_book_availability + {{"title": "[título]"}}
- "Quiero sacar / prestar [libro]" → check_book_availability + {{"title": "[título]"}}

=== BÚSQUEDAS AVANZADAS POR AUTOR ===
- "¿Qué libros escribió [autor]?" → search_books_by_author + {{"author_name": "[nombre]"}}
- "Libros de [autor]" → search_books_by_author + {{"author_name": "[nombre]"}}
- "¿Quién escribió [libro]?" → search_books + {{"title": "[título]"}} (retorna autor)
- "Todos los libros de [autor]" → get_author_books + {{"author_name": "[nombre]"}}
- "Comparar [autor1] vs [autor2]" → compare_authors + {{"author1": "[nombre1]", "author2": "[nombre2]"}}

=== BÚSQUEDAS AVANZADAS POR AÑO ===
- "¿Libros de [año]?" → search_books_by_year + {{"year": YYYY}}
- "Libros publicados en [año]" → search_books_by_year + {{"year": YYYY}}
- "¿Libros entre [año1] y [año2]?" → get_books_by_year_range + {{"start_year": YYYY, "end_year": YYYY}}
- "Libros más recientes" → get_books_by_year_range + {{"start_year": YYYY, "end_year": YYYY}}
- "Libros antiguos de [año]" → search_books_by_year + {{"year": YYYY}}

=== BÚSQUEDAS AVANZADAS POR GÉNERO/CATEGORÍA ===
- "¿Libros de [género/categoría]?" → search_books_by_genre + {{"genre": "[género]"}}
- "¿Recomendaciones de [género]?" → get_book_recommendations + {{"genre": "[género]"}}
- "Mostrar [género]" → search_books_by_genre + {{"genre": "[género]"}}
- "¿Qué libros de ficción hay?" → search_books_by_genre + {{"genre": "Ficción"}}
- "¿Géneros disponibles?" → get_categories

=== RECOMENDACIONES Y ESTADÍSTICAS ===
- "Recomendaciones para mí" → get_book_recommendations + {{}} (sin parámetros, general)
- "¿Cuál es el mejor libro?" → get_most_loaned_books + {{"limit": 1}}
- "Libros más populares" → get_most_loaned_books + {{"limit": 10}}
- "Libros menos prestados" → get_least_loaned_books + {{"limit": 5}}
- "Estadísticas de [categoría]" → get_category_stats + {{"category_name": "[nombre]"}}

=== HISTORIAL Y GESTIÓN ===
- "¿Cuántos libros prestó [usuario]?" → get_loan_history + {{"user_id": N}}
- "Mis préstamos" → get_loan_history + {{"user_id": N}}
- "Historial de [usuario]" → get_loan_history + {{"user_name": "[nombre]}}

VALIDACIONES:
- Si el libro, categoría, autor o usuario no existe en la BD → confianza 0
- Si la fecha es inválida → confianza 0
- Si no tiene relación con la biblioteca → confianza 0
- Preguntas filosóficas, matemáticas, históricas generales, etc. → confianza 0
- Para preguntas generales como "qué libros hay", usar get_books con alta confianza
"""
    return system_prompt



SYSTEM_PROMPT = _build_system_prompt()


def try_parse_intent(user_text: str, model: str = "llama3.2:3b") -> Optional[Dict[str, Any]]:
    """
    Devuelve dict con intent/params/confidence o None si no es confiable.
    
    Soporta intents avanzados incluyendo:
    - Búsquedas por autor, año de publicación, género
    - Recomendaciones de libros
    - Estadísticas y análisis de datos
    - Historial de préstamos
    - Comparación de autores
    
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
        "📚 BÚSQUEDAS BÁSICAS:\n"
        "   • Ver libros / Ver autores / Ver categorías\n"
        "   • Buscar un libro por título\n"
        "   • Ver préstamos activos o vencidos\n\n"
        "🔍 BÚSQUEDAS AVANZADAS:\n"
        "   • Libros de un autor específico (ej: 'Libros de García Márquez')\n"
        "   • Libros de un año/año de publicación (ej: 'Libros de 2020')\n"
        "   • Libros por género/categoría (ej: 'Libros de ficción')\n"
        "   • Comparar autores (estadísticas)\n"
        "   • Recomendaciones de libros\n\n"
        "📊 ESTADÍSTICAS:\n"
        "   • Libros más prestados / menos prestados\n"
        "   • Estadísticas de una categoría\n"
        "   • Autores con más préstamos\n"
        "   • Historial de préstamos de un usuario\n\n"
        "Ejemplos: '¿Qué libros escribió García Márquez?', 'Libros de 2020', "
        "'Recomendaciones de ficción', 'Libros más populares', '¿Está disponible Clean Code?'"
    )