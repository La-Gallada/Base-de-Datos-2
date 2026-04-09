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


# ─────────────────────────────────────────────
# BÚSQUEDAS AVANZADAS POR AUTOR
# ─────────────────────────────────────────────

def sp_search_books_by_author(author_name: str):
    """
    Busca todos los libros de un autor específico.
    """
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("""
            SELECT DISTINCT
                B.IDLibro,
                B.TituloLibro,
                B.ISBN,
                B.AnioPublicacion,
                B.CantidadTotal,
                B.CantidadDisponible,
                C.NombreCategoria
            FROM dbo.Books B
            INNER JOIN dbo.Categories C ON B.IDCategoria = C.IDCategoria
            INNER JOIN dbo.BookAuthors BA ON B.IDLibro = BA.IDLibro
            INNER JOIN dbo.Authors A ON BA.IDAutor = A.IDAutor
            WHERE A.NombreAutor LIKE ?
            ORDER BY B.TituloLibro
        """, (f"%{author_name}%",))
        return cur.fetchall()


def sp_get_author_books(author_name: str):
    """
    Obtiene todos los libros de un autor con datos completos.
    """
    return sp_search_books_by_author(author_name)


# ─────────────────────────────────────────────
# BÚSQUEDAS AVANZADAS POR AÑO
# ─────────────────────────────────────────────

def sp_search_books_by_year(year: int):
    """
    Busca libros publicados en un año específico.
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
            WHERE B.AnioPublicacion = ?
            ORDER BY B.TituloLibro
        """, (year,))
        return cur.fetchall()


def sp_get_books_by_year_range(start_year: int, end_year: int):
    """
    Busca libros publicados entre dos años (inclusive).
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
            WHERE B.AnioPublicacion BETWEEN ? AND ?
            ORDER BY B.AnioPublicacion DESC, B.TituloLibro
        """, (start_year, end_year))
        return cur.fetchall()


# ─────────────────────────────────────────────
# BÚSQUEDAS AVANZADAS POR GÉNERO/CATEGORÍA
# ─────────────────────────────────────────────

def sp_search_books_by_genre(genre: str):
    """
    Busca libros por género/categoría (búsqueda parcial).
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
            WHERE C.NombreCategoria LIKE ? OR C.DescripcionCategoria LIKE ?
            ORDER BY B.TituloLibro
        """, (f"%{genre}%", f"%{genre}%"))
        return cur.fetchall()


# ─────────────────────────────────────────────
# ESTADÍSTICAS Y RECOMENDACIONES
# ─────────────────────────────────────────────

def sp_get_most_loaned_books(limit: int = 10):
    """
    Obtiene los libros más prestados.
    """
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute(f"""
            SELECT TOP {limit}
                B.IDLibro,
                B.TituloLibro,
                B.ISBN,
                B.AnioPublicacion,
                B.CantidadTotal,
                B.CantidadDisponible,
                C.NombreCategoria,
                COUNT(L.IDPrestamo) AS TotalPrestamos
            FROM dbo.Books B
            INNER JOIN dbo.Categories C ON B.IDCategoria = C.IDCategoria
            LEFT JOIN dbo.Loans L ON B.IDLibro = L.IDLibro
            GROUP BY B.IDLibro, B.TituloLibro, B.ISBN, B.AnioPublicacion, 
                     B.CantidadTotal, B.CantidadDisponible, C.NombreCategoria
            ORDER BY COUNT(L.IDPrestamo) DESC, B.TituloLibro
        """)
        return cur.fetchall()


def sp_get_least_loaned_books(limit: int = 10):
    """
    Obtiene los libros menos prestados.
    """
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute(f"""
            SELECT TOP {limit}
                B.IDLibro,
                B.TituloLibro,
                B.ISBN,
                B.AnioPublicacion,
                B.CantidadTotal,
                B.CantidadDisponible,
                C.NombreCategoria,
                COUNT(L.IDPrestamo) AS TotalPrestamos
            FROM dbo.Books B
            INNER JOIN dbo.Categories C ON B.IDCategoria = C.IDCategoria
            LEFT JOIN dbo.Loans L ON B.IDLibro = L.IDLibro
            GROUP BY B.IDLibro, B.TituloLibro, B.ISBN, B.AnioPublicacion, 
                     B.CantidadTotal, B.CantidadDisponible, C.NombreCategoria
            ORDER BY COUNT(L.IDPrestamo) ASC, B.TituloLibro
        """)
        return cur.fetchall()


def sp_get_loan_history(user_identifier):
    """
    Obtiene el historial de préstamos de un usuario.
    user_identifier puede ser un ID numérico o un nombre.
    """
    with get_connection() as cn:
        cur = cn.cursor()
        # Primero intentar como ID, si no, como nombre
        if isinstance(user_identifier, int):
            cur.execute("""
                SELECT 
                    L.IDPrestamo,
                    CONCAT(U.Nombre, ' ', U.Apellido) AS Usuario,
                    B.TituloLibro,
                    L.FechaPrestamo,
                    L.FechaDevolucion,
                    L.Estado
                FROM dbo.Loans L
                INNER JOIN dbo.Users U ON L.IDUsuario = U.IDUsuario
                INNER JOIN dbo.Books B ON L.IDLibro = B.IDLibro
                WHERE L.IDUsuario = ?
                ORDER BY L.FechaPrestamo DESC
            """, (user_identifier,))
        else:
            cur.execute("""
                SELECT 
                    L.IDPrestamo,
                    CONCAT(U.Nombre, ' ', U.Apellido) AS Usuario,
                    B.TituloLibro,
                    L.FechaPrestamo,
                    L.FechaDevolucion,
                    L.Estado
                FROM dbo.Loans L
                INNER JOIN dbo.Users U ON L.IDUsuario = U.IDUsuario
                INNER JOIN dbo.Books B ON L.IDLibro = B.IDLibro
                WHERE CONCAT(U.Nombre, ' ', U.Apellido) LIKE ?
                ORDER BY L.FechaPrestamo DESC
            """, (f"%{user_identifier}%",))
        return cur.fetchall()


def sp_get_category_stats(category_name: str):
    """
    Obtiene estadísticas detalladas de una categoría.
    """
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("""
            SELECT 
                C.IDCategoria,
                C.NombreCategoria,
                C.DescripcionCategoria,
                COUNT(DISTINCT B.IDLibro) AS TotalLibros,
                COUNT(DISTINCT L.IDPrestamo) AS TotalPrestamos,
                SUM(B.CantidadDisponible) AS LibrosDisponibles,
                SUM(B.CantidadTotal - B.CantidadDisponible) AS LibrosPrestados
            FROM dbo.Categories C
            LEFT JOIN dbo.Books B ON C.IDCategoria = B.IDCategoria
            LEFT JOIN dbo.Loans L ON B.IDLibro = L.IDLibro
            WHERE C.NombreCategoria LIKE ?
            GROUP BY C.IDCategoria, C.NombreCategoria, C.DescripcionCategoria
        """, (f"%{category_name}%",))
        return cur.fetchall()


def sp_compare_authors(author1: str, author2: str):
    """
    Compara estadísticas de dos autores.
    Retorna: (author_name, libro_count, loan_count)
    """
    with get_connection() as cn:
        cur = cn.cursor()
        cur.execute("""
            SELECT 
                A.NombreAutor,
                COUNT(DISTINCT B.IDLibro) AS TotalLibros,
                COUNT(L.IDPrestamo) AS TotalPrestamos
            FROM dbo.Authors A
            LEFT JOIN dbo.BookAuthors BA ON A.IDAutor = BA.IDAutor
            LEFT JOIN dbo.Books B ON BA.IDLibro = B.IDLibro
            LEFT JOIN dbo.Loans L ON B.IDLibro = L.IDLibro
            WHERE A.NombreAutor LIKE ? OR A.NombreAutor LIKE ?
            GROUP BY A.IDAutor, A.NombreAutor
            ORDER BY A.NombreAutor
        """, (f"%{author1}%", f"%{author2}%"))
        return cur.fetchall()