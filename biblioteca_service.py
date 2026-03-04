from typing import Any, Dict

from biblioteca_repo import (
    sp_get_users,
    sp_count_books_by_category,
    sp_top_authors_by_loans_month,
    sp_overdue_loans,
)


def run_intent_safely(intent_data: Dict[str, Any]) -> str:
    intent = intent_data.get("intent")
    params = intent_data.get("params") or {}

    if intent == "get_users":
        rows = sp_get_users()
        if not rows:
            return "No hay usuarios registrados."
        first = rows[0]
        # Asumiendo tabla Users: ID, Nombre, Apellido, Email, Tipo, Estado
        return f"Hay {len(rows)} usuarios. Por ejemplo: {first[1]} {first[2]}."

    if intent == "count_books_by_category":
        category = str(params.get("category_name", "")).strip()
        if not category:
            return "Decime la categoría. Ej: Matemáticas, Historia, Programación."
        rows = sp_count_books_by_category(category)
        total = int(rows[0][0]) if rows else 0
        return f"Hay {total} libros en la categoría '{category}'."

    if intent == "top_authors_by_loans_month":
        if "year" not in params or "month" not in params:
            return "Decime el año y el mes. Ej: 'autores con más préstamos en marzo 2026'."
        year = int(params["year"])
        month = int(params["month"])
        rows = sp_top_authors_by_loans_month(year, month)
        if not rows:
            return f"No hay préstamos registrados para {month:02d}/{year}."
        top_author, total = rows[0][0], rows[0][1]
        return f"El autor con más préstamos en {month:02d}/{year} es {top_author} con {total} préstamos."

    if intent == "overdue_loans":
        as_of = params.get("as_of_date")  # puede ser None
        rows = sp_overdue_loans(as_of_date=as_of)
        if not rows:
            return "No hay préstamos vencidos. Todo está al día 📚✨"
        return f"Hay {len(rows)} préstamos vencidos."

    raise ValueError(f"Intent no soportado: {intent}")