"""
Servicio principal de la biblioteca.
Ejecuta intents y retorna resultados estructurados para la UI.
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple
import biblioteca_repo


# Tipo de respuesta estructurada para la UI
# {
#   "type": "books" | "text" | "loans" | "users" | "authors" | "categories",
#   "data": [...],
#   "message": str   (mensaje opcional para mostrar arriba)
# }


def run_intent_safely(intent_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta el intent y retorna un dict estructurado para la UI.
    Nunca lanza excepciones al llamador.
    """
    intent = intent_data.get("intent")
    params = intent_data.get("params", {})

    try:
        return _dispatch(intent, params)
    except Exception as e:
        return {
            "type": "text",
            "message": f"⚠️ Error al consultar la base de datos: {e}",
            "data": []
        }


def _dispatch(intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
    handlers = {
        "get_books":                _handle_get_books,
        "search_books":             _handle_search_books,
        "check_book_availability":  _handle_check_availability,
        "request_loan":             _handle_check_availability,  # Muestra disponibilidad con opción de préstamo
        "get_users":                _handle_get_users,
        "get_authors":              _handle_get_authors,
        "get_categories":           _handle_get_categories,
        "active_loans":             _handle_active_loans,
        "overdue_loans":            _handle_overdue_loans,
        "count_books_by_category":  _handle_count_by_category,
        "top_authors_by_loans_month": _handle_top_authors,
    }

    handler = handlers.get(intent)
    if not handler:
        return {"type": "text", "message": "Intent no reconocido.", "data": []}

    return handler(params)


# ─────────────────────────────────────────────
# HANDLERS DE LIBROS
# ─────────────────────────────────────────────

def _handle_get_books(params: Dict) -> Dict:
    rows = biblioteca_repo.sp_get_books()
    if not rows:
        return {"type": "text", "message": "No hay libros registrados en la biblioteca.", "data": []}

    books = _rows_to_books(rows)
    return {
        "type": "books",
        "message": f"📚 {len(books)} libro(s) en la biblioteca:",
        "data": books
    }


def _handle_search_books(params: Dict) -> Dict:
    title = params.get("title", "").strip()
    if not title:
        return {"type": "text", "message": "⚠️ Debes especificar un título para buscar.", "data": []}

    rows = biblioteca_repo.sp_search_books(title)
    if not rows:
        return {
            "type": "text",
            "message": f"❌ No se encontraron libros con el título '{title}' en la biblioteca.",
            "data": []
        }

    books = _rows_to_books(rows)
    return {
        "type": "books",
        "message": f"🔍 {len(books)} resultado(s) para '{title}':",
        "data": books
    }


def _handle_check_availability(params: Dict) -> Dict:
    title = params.get("title", "").strip()
    if not title:
        # Si no hay título específico, mostrar todos los libros
        return _handle_get_books(params)

    rows = biblioteca_repo.sp_check_book_availability(title)
    if not rows:
        return {
            "type": "text",
            "message": f"❌ El libro '{title}' no existe en el catálogo de esta biblioteca.",
            "data": []
        }

    books = _rows_to_books(rows)
    available = [b for b in books if b["disponible"] > 0]
    unavailable = [b for b in books if b["disponible"] == 0]

    if available:
        msg = f"✅ '{title}' está disponible para préstamo:"
    else:
        msg = f"❌ '{title}' no tiene ejemplares disponibles actualmente:"

    return {
        "type": "books",
        "message": msg,
        "data": books
    }


# ─────────────────────────────────────────────
# HANDLERS DE USUARIOS / AUTORES / CATEGORÍAS
# ─────────────────────────────────────────────

def _handle_get_users(params: Dict) -> Dict:
    rows = biblioteca_repo.sp_get_users()
    if not rows:
        return {"type": "text", "message": "No hay usuarios registrados.", "data": []}

    users = []
    for row in rows:
        users.append({
            "id": row[0],
            "nombre": f"{row[1]} {row[2]}",
            "email": row[3],
            "tipo": row[4],
            "estado": row[5],
        })

    return {
        "type": "users",
        "message": f"👥 {len(users)} usuario(s) registrado(s):",
        "data": users
    }


def _handle_get_authors(params: Dict) -> Dict:
    rows = biblioteca_repo.sp_get_authors()
    if not rows:
        return {"type": "text", "message": "No hay autores registrados.", "data": []}

    authors = [{"id": r[0], "nombre": r[1], "nacionalidad": r[2]} for r in rows]
    return {
        "type": "authors",
        "message": f"✍️ {len(authors)} autor(es) registrado(s):",
        "data": authors
    }


def _handle_get_categories(params: Dict) -> Dict:
    rows = biblioteca_repo.sp_get_categories()
    if not rows:
        return {"type": "text", "message": "No hay categorías registradas.", "data": []}

    categories = [{"id": r[0], "nombre": r[1], "descripcion": r[2]} for r in rows]
    return {
        "type": "categories",
        "message": f"📂 {len(categories)} categoría(s) disponible(s):",
        "data": categories
    }


# ─────────────────────────────────────────────
# HANDLERS DE PRÉSTAMOS
# ─────────────────────────────────────────────

def _handle_active_loans(params: Dict) -> Dict:
    rows = biblioteca_repo.sp_get_active_loans()
    if not rows:
        return {"type": "text", "message": "✅ No hay préstamos activos en este momento.", "data": []}

    loans = _rows_to_loans(rows)
    return {
        "type": "loans",
        "message": f"📖 {len(loans)} préstamo(s) activo(s):",
        "data": loans
    }


def _handle_overdue_loans(params: Dict) -> Dict:
    as_of = params.get("as_of_date")
    rows = biblioteca_repo.sp_overdue_loans(as_of)
    if not rows:
        return {"type": "text", "message": "✅ No hay préstamos vencidos.", "data": []}

    loans = _rows_to_loans(rows)
    return {
        "type": "loans",
        "message": f"⚠️ {len(loans)} préstamo(s) vencido(s):",
        "data": loans
    }


# ─────────────────────────────────────────────
# HANDLERS DE ESTADÍSTICAS
# ─────────────────────────────────────────────

def _handle_count_by_category(params: Dict) -> Dict:
    category = params.get("category_name", "").strip()
    if not category:
        return {"type": "text", "message": "⚠️ Debes especificar una categoría.", "data": []}

    try:
        rows = biblioteca_repo.sp_count_books_by_category(category)
        count = rows[0][0] if rows else 0
        return {
            "type": "text",
            "message": f"📊 Libros en la categoría '{category}': **{count}**",
            "data": []
        }
    except Exception:
        return {
            "type": "text",
            "message": f"❌ La categoría '{category}' no existe en la biblioteca.",
            "data": []
        }


def _handle_top_authors(params: Dict) -> Dict:
    year = params.get("year")
    month = params.get("month")
    if not year or not month:
        return {"type": "text", "message": "⚠️ Debes especificar año y mes.", "data": []}

    try:
        rows = biblioteca_repo.sp_top_authors_by_loans_month(int(year), int(month))
        if not rows:
            return {
                "type": "text",
                "message": f"No hay datos de préstamos para {month}/{year}.",
                "data": []
            }
        authors = [{"nombre": r[0], "prestamos": r[1]} for r in rows]
        return {
            "type": "authors",
            "message": f"🏆 Top autores con más préstamos en {month}/{year}:",
            "data": authors
        }
    except Exception as e:
        return {"type": "text", "message": f"Error al consultar estadísticas: {e}", "data": []}


# ─────────────────────────────────────────────
# FUNCIÓN PÚBLICA: REGISTRAR PRÉSTAMO
# ─────────────────────────────────────────────

def register_loan(id_libro: int, id_usuario: int = 1) -> Dict[str, Any]:
    """
    Registra un préstamo para un libro.
    Verifica disponibilidad antes de insertar.
    
    Args:
        id_libro: ID del libro a prestar
        id_usuario: ID del usuario (por defecto 1 para demo)
    
    Returns:
        Dict con "success": bool y "message": str
    """
    # Verificar disponibilidad actual
    book = biblioteca_repo.sp_get_book_by_id(id_libro)
    if not book:
        return {"success": False, "message": "El libro no existe en la base de datos."}

    disponible = book[5]  # CantidadDisponible
    titulo = book[1]

    if disponible <= 0:
        return {
            "success": False,
            "message": f"❌ '{titulo}' no tiene ejemplares disponibles en este momento."
        }

    # Calcular fechas
    hoy = date.today()
    devolucion = hoy + timedelta(days=14)  # 2 semanas de préstamo

    try:
        biblioteca_repo.sp_insert_loan(
            id_usuario=id_usuario,
            id_libro=id_libro,
            fecha_prestamo=hoy.strftime("%Y-%m-%d"),
            fecha_devolucion=devolucion.strftime("%Y-%m-%d")
        )
        return {
            "success": True,
            "message": (
                f"✅ Préstamo registrado exitosamente.\n"
                f"📚 Libro: {titulo}\n"
                f"📅 Fecha de préstamo: {hoy.strftime('%d/%m/%Y')}\n"
                f"📅 Fecha de devolución: {devolucion.strftime('%d/%m/%Y')}"
            )
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ No se pudo registrar el préstamo: {e}"
        }


# ─────────────────────────────────────────────
# HELPERS PRIVADOS
# ─────────────────────────────────────────────

def _rows_to_books(rows) -> List[Dict]:
    """
    Convierte rows de BD a lista de dicts de libros.
    Columnas esperadas: IDLibro, TituloLibro, ISBN, AnioPublicacion,
                        CantidadTotal, CantidadDisponible, NombreCategoria
    """
    books = []
    for row in rows:
        books.append({
            "id": row[0],
            "titulo": row[1],
            "isbn": row[2],
            "anio": row[3],
            "total": row[4],
            "disponible": row[5],
            "categoria": row[6],
        })
    return books


def _rows_to_loans(rows) -> List[Dict]:
    """
    Convierte rows de préstamos a lista de dicts.
    Columnas: IDLoan, Usuario, TituloLibro, FechaPrestamo, FechaDevolucion, Estado
    """
    loans = []
    for row in rows:
        loans.append({
            "id": row[0],
            "usuario": row[1],
            "libro": row[2],
            "fecha_prestamo": str(row[3]),
            "fecha_devolucion": str(row[4]),
            "estado": row[5] if len(row) > 5 else "Activo",
        })
    return loans