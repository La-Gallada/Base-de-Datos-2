"""
Servicio principal de la biblioteca.
Ejecuta intents y retorna resultados estructurados para la UI.
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional
import data.biblioteca_repo as biblioteca_repo


# Tipo de respuesta estructurada para la UI
# {
#   "type": "books" | "text" | "loans" | "users" | "authors" | "categories",
#   "data": [...],
#   "message": str   (mensaje opcional para mostrar arriba)
# }


def run_intent_safely(intent_data: Dict[str, Any], user_role: str = None) -> Dict[str, Any]:
    intent = intent_data.get("intent")
    params = intent_data.get("params", {})

    try:
        return _dispatch(intent, params, user_role)
    except Exception as e:
        if '229' in str(e):
            return {
                "type": "text",
                "message": "🔒 No tienes permisos para realizar esta consulta.",
                "data": []
            }
        return {
            "type": "text",
            "message": f"⚠️ Error al consultar la base de datos: {e}",
            "data": []
        }


def _dispatch(intent: str, params: Dict[str, Any], user_role: str = None) -> Dict[str, Any]:
    handlers = {
        "get_books":                    lambda p: _handle_get_books(p, user_role),
        "search_books":                 lambda p: _handle_search_books(p, user_role),
        "check_book_availability":      lambda p: _handle_check_availability(p, user_role),
        "request_loan":                 lambda p: _handle_check_availability(p, user_role),
        "search_books_by_author":       lambda p: _handle_search_books_by_author(p, user_role),
        "search_books_by_year":         lambda p: _handle_search_books_by_year(p, user_role),
        "search_books_by_genre":        lambda p: _handle_search_books_by_genre(p, user_role),
        "get_author_books":             lambda p: _handle_search_books_by_author(p, user_role),
        "get_books_by_year_range":      lambda p: _handle_books_by_year_range(p, user_role),
        "get_most_loaned_books":        lambda p: _handle_most_loaned_books(p, user_role),
        "get_least_loaned_books":       lambda p: _handle_least_loaned_books(p, user_role),
        "get_loan_history":             lambda p: _handle_loan_history(p, user_role),
        "get_category_stats":           lambda p: _handle_category_stats(p, user_role),
        "compare_authors":              lambda p: _handle_compare_authors(p, user_role),
        "get_book_recommendations":     lambda p: _handle_book_recommendations(p, user_role),
        "get_users":                    lambda p: _handle_get_users(p, user_role),
        "get_authors":                  lambda p: _handle_get_authors(p, user_role),
        "get_categories":               lambda p: _handle_get_categories(p, user_role),
        "active_loans":                 lambda p: _handle_active_loans(p, user_role),
        "overdue_loans":                lambda p: _handle_overdue_loans(p, user_role),
        "count_books_by_category":      lambda p: _handle_count_by_category(p, user_role),
        "top_authors_by_loans_month":   lambda p: _handle_top_authors(p, user_role),
    }

    handler = handlers.get(intent)
    if not handler:
        return {"type": "text", "message": "Intent no reconocido.", "data": []}

    return handler(params)


# ─────────────────────────────────────────────
# HANDLERS DE LIBROS
# ─────────────────────────────────────────────

def _handle_get_books(params: Dict, user_role: str = None) -> Dict:
    rows = biblioteca_repo.sp_get_books(user_role=user_role)
    if not rows:
        return {"type": "text", "message": "No hay libros registrados en la biblioteca.", "data": []}

    books = _rows_to_books(rows)
    return {
        "type": "books",
        "message": f"📚 {len(books)} libro(s) en la biblioteca:",
        "data": books
    }


def _handle_search_books(params: Dict, user_role: str = None) -> Dict:
    title = params.get("title", "").strip()
    if not title:
        return {"type": "text", "message": "⚠️ Debes especificar un título para buscar.", "data": []}

    rows = biblioteca_repo.sp_search_books(title, user_role=user_role)
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


def _handle_check_availability(params: Dict, user_role: str = None) -> Dict:
    title = params.get("title", "").strip()
    if not title:
        # Si no hay título específico, mostrar todos los libros
        return _handle_get_books(params, user_role)

    rows = biblioteca_repo.sp_check_book_availability(title, user_role=user_role)
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

def _handle_get_users(params: Dict, user_role: str = None) -> Dict:
    rows = biblioteca_repo.sp_get_users(user_role=user_role)
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


def _handle_get_authors(params: Dict, user_role: str = None) -> Dict:
    rows = biblioteca_repo.sp_get_authors(user_role=user_role)
    if not rows:
        return {"type": "text", "message": "No hay autores registrados.", "data": []}

    authors = [{"id": r[0], "nombre": r[1], "nacionalidad": r[2]} for r in rows]
    return {
        "type": "authors",
        "message": f"✍️ {len(authors)} autor(es) registrado(s):",
        "data": authors
    }


def _handle_get_categories(params: Dict, user_role: str = None) -> Dict:
    rows = biblioteca_repo.sp_get_categories(user_role=user_role)
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

def _handle_active_loans(params: Dict, user_role: str = None) -> Dict:
    if user_role not in ("Administrador", "Director"):
        return {
            "type": "text",
            "message": "🔒 No tienes permisos para ver los préstamos activos.",
            "data": []
        }
    try:
        rows = biblioteca_repo.sp_get_active_loans(user_role=user_role)
    except Exception as e:
        if '229' in str(e):
            return {
                "type": "text",
                "message": "🔒 No tienes permisos para realizar esta consulta.",
                "data": []
            }
        raise

    if not rows:
        return {"type": "text", "message": "✅ No hay préstamos activos en este momento.", "data": []}

    loans = _rows_to_loans(rows)
    return {
        "type": "loans",
        "message": f"📖 {len(loans)} préstamo(s) activo(s):",
        "data": loans
    }


def _handle_active_loans(params: Dict, user_role: str = None) -> Dict:
    if user_role not in ("Administrador", "Director"):
        return {
            "type": "text",
            "message": "🔒 Esta consulta es solo para administradores.",
            "data": []
        }
    try:
        rows = biblioteca_repo.sp_get_active_loans(user_role=user_role)
    except Exception as e:
        if '229' in str(e):
            return {
                "type": "text",
                "message": "🔒 No tienes permisos para realizar esta consulta.",
                "data": []
            }
        raise

    if not rows:
        return {"type": "text", "message": "✅ No hay préstamos activos en este momento.", "data": []}

    loans = _rows_to_loans(rows)
    return {
        "type": "loans",
        "message": f"📖 {len(loans)} préstamo(s) activo(s):",
        "data": loans
    }


# ─────────────────────────────────────────────
# HANDLERS DE ESTADÍSTICAS
# ─────────────────────────────────────────────

def _handle_count_by_category(params: Dict, user_role: str = None) -> Dict:
    category = params.get("category_name", "").strip()
    if not category:
        return {"type": "text", "message": "⚠️ Debes especificar una categoría.", "data": []}

    try:
        rows = biblioteca_repo.sp_count_books_by_category(category, user_role=user_role)
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


def _handle_top_authors(params: Dict, user_role: str = None) -> Dict:
    year = params.get("year")
    month = params.get("month")
    if not year or not month:
        return {"type": "text", "message": "⚠️ Debes especificar año y mes.", "data": []}

    try:
        rows = biblioteca_repo.sp_top_authors_by_loans_month(int(year), int(month), user_role=user_role)
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
# HANDLERS AVANZADOS (BÚSQUEDAS Y ESTADÍSTICAS)
# ─────────────────────────────────────────────

def _handle_search_books_by_author(params: Dict, user_role: str = None) -> Dict:
    """Busca libros por autor."""
    author = params.get("author_name", "").strip()
    if not author:
        return {"type": "text", "message": "⚠️ Debes especificar un autor.", "data": []}

    rows = biblioteca_repo.sp_search_books_by_author(author, user_role=user_role)
    if not rows:
        return {
            "type": "text",
            "message": f"❌ No se encontraron libros del autor '{author}'.",
            "data": []
        }

    books = _rows_to_books(rows)
    return {
        "type": "books",
        "message": f"📚 Libros de {author}:",
        "data": books
    }


def _handle_search_books_by_year(params: Dict, user_role: str = None) -> Dict:
    """Busca libros por año de publicación."""
    year = params.get("year")
    if not year:
        return {"type": "text", "message": "⚠️ Debes especificar un año.", "data": []}

    try:
        rows = biblioteca_repo.sp_search_books_by_year(int(year), user_role=user_role)
        if not rows:
            return {
                "type": "text",
                "message": f"❌ No hay libros publicados en {year}.",
                "data": []
            }

        books = _rows_to_books(rows)
        return {
            "type": "books",
            "message": f"📚 Libros publicados en {year}:",
            "data": books
        }
    except Exception as e:
        return {"type": "text", "message": f"⚠️ Error: {e}", "data": []}


def _handle_search_books_by_genre(params: Dict, user_role: str = None) -> Dict:
    """Busca libros por género/categoría."""
    genre = params.get("genre", "").strip()
    if not genre:
        return {"type": "text", "message": "⚠️ Debes especificar un género.", "data": []}

    rows = biblioteca_repo.sp_search_books_by_genre(genre, user_role=user_role)
    if not rows:
        return {
            "type": "text",
            "message": f"❌ No hay libros de género '{genre}'.",
            "data": []
        }

    books = _rows_to_books(rows)
    return {
        "type": "books",
        "message": f"📚 Libros de género '{genre}':",
        "data": books
    }


def _handle_books_by_year_range(params: Dict, user_role: str = None) -> Dict:
    """Busca libros entre dos años."""
    start_year = params.get("start_year")
    end_year = params.get("end_year")
    if not start_year or not end_year:
        return {"type": "text", "message": "⚠️ Debes especificar rango de años.", "data": []}

    try:
        rows = biblioteca_repo.sp_get_books_by_year_range(int(start_year), int(end_year), user_role=user_role)
        if not rows:
            return {
                "type": "text",
                "message": f"❌ No hay libros publicados entre {start_year} y {end_year}.",
                "data": []
            }

        books = _rows_to_books(rows)
        return {
            "type": "books",
            "message": f"📚 Libros publicados entre {start_year} y {end_year}:",
            "data": books
        }
    except Exception as e:
        return {"type": "text", "message": f"⚠️ Error: {e}", "data": []}


def _handle_most_loaned_books(params: Dict, user_role: str = None) -> Dict:
    """Obtiene los libros más prestados."""
    limit = params.get("limit", 10)
    try:
        rows = biblioteca_repo.sp_get_most_loaned_books(int(limit), user_role=user_role)
        if not rows:
            return {"type": "text", "message": "No hay datos de préstamos.", "data": []}

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
                "prestamos": row[7],
            })

        return {
            "type": "books",
            "message": f"🏆 Top {len(books)} libros más prestados:",
            "data": books
        }
    except Exception as e:
        return {"type": "text", "message": f"⚠️ Error: {e}", "data": []}


def _handle_least_loaned_books(params: Dict, user_role: str = None) -> Dict:
    """Obtiene los libros menos prestados."""
    limit = params.get("limit", 10)
    try:
        rows = biblioteca_repo.sp_get_least_loaned_books(int(limit), user_role=user_role)
        if not rows:
            return {"type": "text", "message": "No hay datos de préstamos.", "data": []}

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
                "prestamos": row[7],
            })

        return {
            "type": "books",
            "message": f"📚 Libros menos prestados:",
            "data": books
        }
    except Exception as e:
        return {"type": "text", "message": f"⚠️ Error: {e}", "data": []}


def _handle_loan_history(params: Dict, user_role: str = None) -> Dict:
    """Obtiene el historial de préstamos de un usuario."""
    user_id = params.get("user_id")
    user_name = params.get("user_name", "").strip()

    identifier = user_id if user_id else user_name
    if not identifier:
        return {"type": "text", "message": "⚠️ Debes especificar un usuario.", "data": []}

    try:
        rows = biblioteca_repo.sp_get_loan_history(identifier, user_role=user_role)
        if not rows:
            return {
                "type": "text",
                "message": f"❌ No hay historial de préstamos para este usuario.",
                "data": []
            }

        loans = _rows_to_loans(rows)
        return {
            "type": "loans",
            "message": f"📖 Historial de préstamos:",
            "data": loans
        }
    except Exception as e:
        return {"type": "text", "message": f"⚠️ Error: {e}", "data": []}


def _handle_category_stats(params: Dict, user_role: str = None) -> Dict:
    """Obtiene estadísticas de una categoría."""
    category = params.get("category_name", "").strip()
    if not category:
        return {"type": "text", "message": "⚠️ Debes especificar una categoría.", "data": []}

    try:
        rows = biblioteca_repo.sp_get_category_stats(category, user_role=user_role)
        if not rows:
            return {
                "type": "text",
                "message": f"❌ La categoría '{category}' no existe.",
                "data": []
            }

        stats = []
        for row in rows:
            stats.append({
                "nombre": row[1],
                "descripcion": row[2],
                "total_libros": row[3],
                "total_prestamos": row[4],
                "disponibles": row[5],
                "prestados": row[6],
            })

        return {
            "type": "text",
            "message": f"📊 Estadísticas de '{category}':\n"
                       f"   📚 Total de libros: {stats[0]['total_libros']}\n"
                       f"   ✅ Disponibles: {stats[0]['disponibles']}\n"
                       f"   📖 Prestados: {stats[0]['prestados']}\n"
                       f"   🔄 Total de préstamos: {stats[0]['total_prestamos']}",
            "data": stats
        }
    except Exception as e:
        return {"type": "text", "message": f"⚠️ Error: {e}", "data": []}


def _handle_compare_authors(params: Dict, user_role: str = None) -> Dict:
    """Compara estadísticas de dos autores."""
    author1 = params.get("author1", "").strip()
    author2 = params.get("author2", "").strip()

    if not author1 or not author2:
        return {"type": "text", "message": "⚠️ Debes especificar dos autores.", "data": []}

    try:
        rows = biblioteca_repo.sp_compare_authors(author1, author2, user_role=user_role)
        if not rows:
            return {
                "type": "text",
                "message": f"❌ No se encontraron datos para los autores especificados.",
                "data": []
            }

        authors = [
            {"nombre": r[0], "libros": r[1], "prestamos": r[2]}
            for r in rows
        ]

        msg_parts = ["🏆 Comparación de autores:\n"]
        for author in authors:
            msg_parts.append(f"\n📝 {author['nombre']}:\n")
            msg_parts.append(f"   📚 Libros: {author['libros']}\n")
            msg_parts.append(f"   🔄 Préstamos: {author['prestamos']}")

        return {
            "type": "authors",
            "message": "".join(msg_parts),
            "data": authors
        }
    except Exception as e:
        return {"type": "text", "message": f"⚠️ Error: {e}", "data": []}


def _handle_book_recommendations(params: Dict, user_role: str = None) -> Dict:
    """Obtiene recomendaciones de libros."""
    genre = params.get("genre", "").strip()

    try:
        if genre:
            # Recomendaciones de un género específico
            rows = biblioteca_repo.sp_search_books_by_genre(genre, user_role=user_role)
            msg = f"💡 Recomendaciones de {genre}:"
        else:
            # Recomendaciones generales: libros más prestados
            rows = biblioteca_repo.sp_get_most_loaned_books(5, user_role=user_role)
            msg = "💡 Nuestras recomendaciones (libros populares):"

        if not rows:
            return {
                "type": "text",
                "message": f"❌ No hay recomendaciones disponibles.",
                "data": []
            }

        books = _rows_to_books(rows)
        return {
            "type": "books",
            "message": msg,
            "data": books
        }
    except Exception as e:
        return {"type": "text", "message": f"⚠️ Error: {e}", "data": []}


# ─────────────────────────────────────────────
# FUNCIÓN PÚBLICA: REGISTRAR PRÉSTAMO
# ─────────────────────────────────────────────

def register_loan(id_libro: int, id_usuario: int = 1, user_role: str = None) -> Dict[str, Any]:
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
    book = biblioteca_repo.sp_get_book_by_id(id_libro, user_role=user_role)
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
            fecha_devolucion=devolucion.strftime("%Y-%m-%d"),
            user_role=user_role
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
# FUNCIONES PARA OPERACIONES ADMINISTRATIVAS
# ─────────────────────────────────────────────

def get_category_id(category_name: str, user_role: str = None) -> Optional[int]:
    """
    Obtiene el ID de una categoría por nombre.
    """
    try:
        rows = biblioteca_repo.sp_get_categories(user_role=user_role)
        for row in rows:
            if row[1].lower() == category_name.lower():  # row[1] es NombreCategoria
                return row[0]  # row[0] es IDCategoria
        return None
    except Exception as e:
        print(f"Error obteniendo ID de categoría: {e}")
        return None


def get_author_id(author_name: str, user_role: str = None) -> Optional[int]:
    """
    Obtiene el ID de un autor por nombre.
    """
    try:
        rows = biblioteca_repo.sp_get_authors(user_role=user_role)
        for row in rows:
            if row[1].lower() == author_name.lower():  # row[1] es NombreAutor
                return row[0]  # row[0] es IDAutor
        return None
    except Exception as e:
        print(f"Error obteniendo ID de autor: {e}")
        return None


def insert_book(titulo: str, isbn: str, year: int, categoria: str, cantidad: int, autores: List[str], user_role: str = None) -> Optional[int]:
    """
    Inserta un nuevo libro con sus autores.
    Retorna el ID del libro insertado o None si falla.
    """
    try:
        # Obtener ID de categoría
        id_categoria = get_category_id(categoria, user_role)
        if id_categoria is None:
            raise ValueError(f"Categoría '{categoria}' no encontrada")

        # Insertar libro
        id_libro = biblioteca_repo.sp_insert_book(titulo, isbn, year, id_categoria, cantidad, user_role)

        # Insertar relaciones libro-autor
        for autor in autores:
            id_autor = get_author_id(autor, user_role)
            if id_autor is None:
                raise ValueError(f"Autor '{autor}' no encontrado")
            biblioteca_repo.sp_insert_book_author(id_libro, id_autor, user_role)

        return id_libro
    except Exception as e:
        print(f"Error insertando libro: {e}")
        return None


def insert_author(nombre: str, nacionalidad: str, user_role: str = None) -> Optional[int]:
    """
    Inserta un nuevo autor.
    Retorna el ID del autor insertado o None si falla.
    """
    try:
        return biblioteca_repo.sp_insert_author(nombre, nacionalidad, user_role)
    except Exception as e:
        print(f"Error insertando autor: {e}")
        return None


def insert_category(nombre: str, descripcion: str, user_role: str = None) -> Optional[int]:
    """
    Inserta una nueva categoría.
    Retorna el ID de la categoría insertada o None si falla.
    """
    try:
        return biblioteca_repo.sp_insert_category(nombre, descripcion, user_role)
    except Exception as e:
        print(f"Error insertando categoría: {e}")
        return None


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