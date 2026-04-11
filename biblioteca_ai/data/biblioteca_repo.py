"""
Repositorio de acceso a datos de la biblioteca.
Todas las funciones retornan datos reales de la BD via Stored Procedures.
"""

from db import get_connection


# ─────────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────────

def sp_get_users(user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetUsers")
        return cur.fetchall()


# ─────────────────────────────────────────────
# LIBROS
# ─────────────────────────────────────────────

def sp_get_books(user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetBooks")
        return cur.fetchall()


def sp_search_books(title: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_SearchBooks @Title = ?", (title,))
        return cur.fetchall()


def sp_check_book_availability(title: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_SearchBooks @Title = ?", (title,))
        return cur.fetchall()


def sp_get_book_by_id(id_libro: int, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetBookById @IDLibro = ?", (id_libro,))
        return cur.fetchone()


def sp_insert_loan(id_usuario: int, id_libro: int, fecha_prestamo: str, fecha_devolucion: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_InsertLoan ?, ?, ?, ?", (id_usuario, id_libro, fecha_prestamo, fecha_devolucion))
        cn.commit()
        return True


# ─────────────────────────────────────────────
# AUTORES
# ─────────────────────────────────────────────

def sp_get_authors(user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetAuthors")
        return cur.fetchall()


# ─────────────────────────────────────────────
# CATEGORÍAS
# ─────────────────────────────────────────────

def sp_get_categories(user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetCategories")
        return cur.fetchall()


# ─────────────────────────────────────────────
# PRÉSTAMOS
# ─────────────────────────────────────────────

def sp_get_active_loans(user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        try:
            cur.execute("EXEC dbo.SP_GetActiveLoans")
            return cur.fetchall()
        except Exception as e:
            if '229' in str(e):
                raise PermissionError("No tienes permisos para ver los préstamos activos.")
            raise


def sp_overdue_loans(as_of_date=None, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        if as_of_date:
            cur.execute("EXEC dbo.SP_OverdueLoans @AsOfDate = ?", (as_of_date,))
        else:
            cur.execute("EXEC dbo.SP_OverdueLoans")
        return cur.fetchall()


def sp_count_books_by_category(category_name: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_CountBooksByCategory @CategoryName = ?", (category_name,))
        return cur.fetchall()


def sp_top_authors_by_loans_month(year: int, month: int, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_TopAuthorsByLoans @Year = ?, @Month = ?", (year, month))
        return cur.fetchall()


# ─────────────────────────────────────────────
# BÚSQUEDAS AVANZADAS POR AUTOR
# ─────────────────────────────────────────────

def sp_search_books_by_author(author_name: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_SearchBooksByAuthor @AuthorName = ?", (author_name,))
        return cur.fetchall()


# ─────────────────────────────────────────────
# BÚSQUEDAS AVANZADAS POR AÑO
# ─────────────────────────────────────────────

def sp_search_books_by_year(year: int, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_SearchBooksByYear @Year = ?", (year,))
        return cur.fetchall()


def sp_get_books_by_year_range(start_year: int, end_year: int, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetBooksByYearRange @StartYear = ?, @EndYear = ?", (start_year, end_year))
        return cur.fetchall()


# ─────────────────────────────────────────────
# BÚSQUEDAS AVANZADAS POR GÉNERO/CATEGORÍA
# ─────────────────────────────────────────────

def sp_search_books_by_genre(genre: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_SearchBooksByGenre @Genre = ?", (genre,))
        return cur.fetchall()


# ─────────────────────────────────────────────
# ESTADÍSTICAS Y RECOMENDACIONES
# ─────────────────────────────────────────────

def sp_get_most_loaned_books(limit: int = 10, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetMostLoanedBooks @Limit = ?", (limit,))
        return cur.fetchall()


def sp_get_least_loaned_books(limit: int = 10, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetLeastLoanedBooks @Limit = ?", (limit,))
        return cur.fetchall()


def sp_get_loan_history(user_identifier, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        if isinstance(user_identifier, int):
            cur.execute("EXEC dbo.SP_GetLoanHistoryById @IDUsuario = ?", (user_identifier,))
        else:
            cur.execute("EXEC dbo.SP_GetLoanHistoryByName @UserName = ?", (user_identifier,))
        return cur.fetchall()


def sp_get_category_stats(category_name: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetCategoryStats @CategoryName = ?", (category_name,))
        return cur.fetchall()


def sp_compare_authors(author1: str, author2: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_CompareAuthors @Author1 = ?, @Author2 = ?", (author1, author2))
        return cur.fetchall()


# ─────────────────────────────────────────────
# INSERCIONES - CRUD PARA ADMIN
# ─────────────────────────────────────────────

def sp_insert_author(nombre: str, nacionalidad: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        try:
            cur.execute("EXEC dbo.SP_InsertAuthor @NombreAutor = ?, @Nacionalidad = ?", (nombre, nacionalidad))
            cn.commit()
            cur.execute("SELECT IDENT_CURRENT('dbo.Authors')")
            result = cur.fetchone()
            return int(result[0]) if result else None
        except Exception as e:
            cn.rollback()
            raise Exception(f"Error al insertar autor: {str(e)}")


def sp_insert_category(nombre: str, descripcion: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        try:
            cur.execute("EXEC dbo.SP_InsertCategory @NombreCategoria = ?, @Descripcion = ?", (nombre, descripcion))
            cn.commit()
            cur.execute("SELECT IDENT_CURRENT('dbo.Categories')")
            result = cur.fetchone()
            return int(result[0]) if result else None
        except Exception as e:
            cn.rollback()
            raise Exception(f"Error al insertar categoría: {str(e)}")


def sp_insert_book(titulo: str, isbn: str, year: int, id_categoria: int, cantidad: int, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        try:
            cur.execute(
                "EXEC dbo.SP_InsertBook @TituloLibro = ?, @ISBN = ?, @AnioPublicacion = ?, @CantidadTotal = ?, @IDCategoria = ?",
                (titulo, isbn, year, cantidad, id_categoria)
            )
            cn.commit()
            cur.execute("SELECT IDENT_CURRENT('dbo.Books')")
            result = cur.fetchone()
            return int(result[0]) if result else None
        except Exception as e:
            cn.rollback()
            raise Exception(f"Error al insertar libro: {str(e)}")


def sp_insert_book_author(id_libro: int, id_autor: int, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        try:
            cur.execute("EXEC dbo.SP_InsertBookAuthor @IDLibro = ?, @IDAutor = ?", (id_libro, id_autor))
            cn.commit()
            return True
        except Exception as e:
            cn.rollback()
            raise Exception(f"Error al crear relación libro-autor: {str(e)}")


def get_category_id(category_name: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("SELECT IDCategoria FROM dbo.Categories WHERE NombreCategoria = ?", (category_name,))
        result = cur.fetchone()
        return result[0] if result else None


def get_author_id(author_name: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("SELECT IDAutor FROM dbo.Authors WHERE NombreAutor = ?", (author_name,))
        result = cur.fetchone()
        return result[0] if result else None