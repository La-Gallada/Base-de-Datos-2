"""
Repositorio de acceso a datos de la biblioteca.
Todas las funciones retornan datos reales de la BD.
"""

from db import get_connection


# ─────────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────────

def sp_get_users():
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetUsers")
        return cur.fetchall()


# ─────────────────────────────────────────────
# LIBROS
# ─────────────────────────────────────────────

def sp_get_books():
    """
    Retorna lista de libros con su categoría.
    Columnas: IDLibro, TituloLibro, ISBN, AnioPublicacion,
              CantidadTotal, CantidadDisponible, NombreCategoria
    """
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetBooks")
        return cur.fetchall()


def sp_search_books(title: str):
    """
    Busca libros por título (búsqueda parcial).
    Retorna mismas columnas que sp_get_books.
    """
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("""
            SELECT 
                B.IDLibro,
                B.TituloLibro,
                B.ISBN,
                B.AnioPublicacion,
                B.CantidadTotal,
                B.CantidadDisponible,
                C.NombreCategoria
            FROM dbo.Books B
            INNER JOIN dbo.Categories C ON B.IDCategoria = C.IDCategoria
            WHERE B.TituloLibro LIKE ?
        """, (f"%{title}%",))
        return cur.fetchall()


def sp_check_book_availability(title: str):
    """
    Verifica disponibilidad de un libro por título.
    Retorna lista de libros que coincidan con el título dado,
    con su disponibilidad actual.
    """
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("""
            SELECT 
                B.IDLibro,
                B.TituloLibro,
                B.ISBN,
                B.AnioPublicacion,
                B.CantidadTotal,
                B.CantidadDisponible,
                C.NombreCategoria
            FROM dbo.Books B
            INNER JOIN dbo.Categories C ON B.IDCategoria = C.IDCategoria
            WHERE B.TituloLibro LIKE ?
        """, (f"%{title}%",))
        return cur.fetchall()


def sp_insert_loan(id_usuario: int, id_libro: int, fecha_prestamo: str, fecha_devolucion: str):
    """
    Registra un nuevo préstamo.
    El trigger TR_ValidarStockAntesDePrestamo valida el stock automáticamente.
    
    Returns:
        True si el préstamo fue registrado exitosamente.
    Raises:
        Exception si no hay stock disponible u otro error.
    """
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("""
            INSERT INTO dbo.Loans (IDUsuario, IDLibro, FechaPrestamo, FechaDevolucion, Estado)
            VALUES (?, ?, ?, ?, 'Prestado')
        """, (id_usuario, id_libro, fecha_prestamo, fecha_devolucion))
        cn.commit()
        return True


def sp_get_book_by_id(id_libro: int):
    """
    Obtiene un libro específico por su ID.
    """
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("""
            SELECT 
                B.IDLibro,
                B.TituloLibro,
                B.ISBN,
                B.AnioPublicacion,
                B.CantidadTotal,
                B.CantidadDisponible,
                C.NombreCategoria
            FROM dbo.Books B
            INNER JOIN dbo.Categories C ON B.IDCategoria = C.IDCategoria
            WHERE B.IDLibro = ?
        """, (id_libro,))
        return cur.fetchone()


# ─────────────────────────────────────────────
# AUTORES
# ─────────────────────────────────────────────

def sp_get_authors():
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetAuthors")
        return cur.fetchall()


# ─────────────────────────────────────────────
# CATEGORÍAS
# ─────────────────────────────────────────────

def sp_get_categories():
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetCategories")
        return cur.fetchall()


# ─────────────────────────────────────────────
# PRÉSTAMOS
# ─────────────────────────────────────────────

def sp_get_active_loans():
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetActiveLoans")
        return cur.fetchall()


def sp_count_books_by_category(category_name: str):
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_CountBooksByCategory @CategoryName = ?", (category_name,))
        return cur.fetchall()


def sp_top_authors_by_loans_month(year: int, month: int):
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute(
            "EXEC dbo.SP_TopAuthorsByLoans @Year = ?, @Month = ?",
            (year, month)
        )
        return cur.fetchall()


def sp_overdue_loans(as_of_date=None):
    with get_connection() as cn:
        cur = cn.cursor()
        if as_of_date:
            cur.execute("EXEC dbo.SP_OverdueLoans @AsOfDate = ?", (as_of_date,))
        else:
            cur.execute("EXEC dbo.SP_OverdueLoans")
        return cur.fetchall()