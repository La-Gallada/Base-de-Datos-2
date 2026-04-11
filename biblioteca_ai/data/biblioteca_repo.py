"""
Repositorio de acceso a datos de la biblioteca.
Todas las funciones retornan datos reales de la BD.
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
    """
    Retorna lista de libros con su categoría.
    Columnas: IDLibro, TituloLibro, ISBN, AnioPublicacion,
              CantidadTotal, CantidadDisponible, NombreCategoria
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_GetBooks")
        return cur.fetchall()


def sp_search_books(title: str, user_role=None):
    """
    Busca libros por título (búsqueda parcial).
    Retorna mismas columnas que sp_get_books.
    """
    with get_connection(user_role) as cn:
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


def sp_check_book_availability(title: str, user_role=None):
    """
    Verifica disponibilidad de un libro por título.
    Retorna lista de libros que coincidan con el título dado,
    con su disponibilidad actual.
    """
    with get_connection(user_role) as cn:
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


def sp_insert_loan(id_usuario: int, id_libro: int, fecha_prestamo: str, fecha_devolucion: str, user_role=None):
    """
    Registra un nuevo préstamo usando el stored procedure SP_InsertLoan.
    El SP valida el stock automáticamente y actualiza la cantidad disponible.
    
    Returns:
        True si el préstamo fue registrado exitosamente.
    Raises:
        Exception si no hay stock disponible u otro error.
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_InsertLoan ?, ?, ?, ?", (id_usuario, id_libro, fecha_prestamo, fecha_devolucion))
        cn.commit()
        return True


def sp_get_book_by_id(id_libro: int, user_role=None):
    """
    Obtiene un libro específico por su ID.
    """
    with get_connection(user_role) as cn:
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


def sp_count_books_by_category(category_name: str, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("EXEC dbo.SP_CountBooksByCategory @CategoryName = ?", (category_name,))
        return cur.fetchall()


def sp_top_authors_by_loans_month(year: int, month: int, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute(
            "EXEC dbo.SP_TopAuthorsByLoans @Year = ?, @Month = ?",
            (year, month)
        )
        return cur.fetchall()


def sp_overdue_loans(as_of_date=None, user_role=None):
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        if as_of_date:
            cur.execute("EXEC dbo.SP_OverdueLoans @AsOfDate = ?", (as_of_date,))
        else:
            cur.execute("EXEC dbo.SP_OverdueLoans")
        return cur.fetchall()


# ─────────────────────────────────────────────
# BÚSQUEDAS AVANZADAS POR AUTOR
# ─────────────────────────────────────────────

def sp_search_books_by_author(author_name: str, user_role=None):
    """
    Busca todos los libros de un autor específico.
    """
    with get_connection(user_role) as cn:
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
            INNER JOIN dbo.BookAuthors BA ON B.IDLibro = BA.IDLibros
            INNER JOIN dbo.Authors A ON BA.IDAutores = A.IDAutor
            WHERE A.NombreAutor LIKE ?
            ORDER BY B.TituloLibro
        """, (f"%{author_name}%",))
        return cur.fetchall()


# ─────────────────────────────────────────────
# BÚSQUEDAS AVANZADAS POR AÑO
# ─────────────────────────────────────────────

def sp_search_books_by_year(year: int, user_role=None):
    """
    Busca libros publicados en un año específico.
    """
    with get_connection(user_role) as cn:
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


def sp_get_books_by_year_range(start_year: int, end_year: int, user_role=None):
    """
    Busca libros publicados entre dos años (inclusive).
    """
    with get_connection(user_role) as cn:
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

def sp_search_books_by_genre(genre: str, user_role=None):
    """
    Busca libros por género/categoría (búsqueda parcial).
    """
    with get_connection(user_role) as cn:
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
            WHERE C.NombreCategoria LIKE ? OR C.Descripcion LIKE ?
            ORDER BY B.TituloLibro
        """, (f"%{genre}%", f"%{genre}%"))
        return cur.fetchall()


# ─────────────────────────────────────────────
# ESTADÍSTICAS Y RECOMENDACIONES
# ─────────────────────────────────────────────

def sp_get_most_loaned_books(limit: int = 10, user_role=None):
    """
    Obtiene los libros más prestados.
    """
    with get_connection(user_role) as cn:
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
                COUNT(L.IDLoan) AS TotalPrestamos
            FROM dbo.Books B
            INNER JOIN dbo.Categories C ON B.IDCategoria = C.IDCategoria
            LEFT JOIN dbo.Loans L ON B.IDLibro = L.IDLibro
            GROUP BY B.IDLibro, B.TituloLibro, B.ISBN, B.AnioPublicacion, 
                     B.CantidadTotal, B.CantidadDisponible, C.NombreCategoria
            ORDER BY COUNT(L.IDLoan) DESC, B.TituloLibro
        """)
        return cur.fetchall()


def sp_get_least_loaned_books(limit: int = 10, user_role=None):
    """
    Obtiene los libros menos prestados.
    """
    with get_connection(user_role) as cn:
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
                COUNT(L.IDLoan) AS TotalPrestamos
            FROM dbo.Books B
            INNER JOIN dbo.Categories C ON B.IDCategoria = C.IDCategoria
            LEFT JOIN dbo.Loans L ON B.IDLibro = L.IDLibro
            GROUP BY B.IDLibro, B.TituloLibro, B.ISBN, B.AnioPublicacion, 
                     B.CantidadTotal, B.CantidadDisponible, C.NombreCategoria
            ORDER BY COUNT(L.IDLoan) ASC, B.TituloLibro
        """)
        return cur.fetchall()


def sp_get_loan_history(user_identifier, user_role=None):
    """
    Obtiene el historial de préstamos de un usuario.
    user_identifier puede ser un ID numérico o un nombre.
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        # Primero intentar como ID, si no, como nombre
        if isinstance(user_identifier, int):
            cur.execute("""
                SELECT 
                    L.IDLoan,
                    CONCAT(U.NombreUsuario, ' ', U.ApellidoUsuario) AS Usuario,
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
                    L.IDLoan,
                    CONCAT(U.NombreUsuario, ' ', U.ApellidoUsuario) AS Usuario,
                    B.TituloLibro,
                    L.FechaPrestamo,
                    L.FechaDevolucion,
                    L.Estado
                FROM dbo.Loans L
                INNER JOIN dbo.Users U ON L.IDUsuario = U.IDUsuario
                INNER JOIN dbo.Books B ON L.IDLibro = B.IDLibro
                WHERE CONCAT(U.NombreUsuario, ' ', U.ApellidoUsuario) LIKE ?
                ORDER BY L.FechaPrestamo DESC
            """, (f"%{user_identifier}%",))
        return cur.fetchall()


def sp_get_category_stats(category_name: str, user_role=None):
    """
    Obtiene estadísticas detalladas de una categoría.
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("""
            SELECT 
                C.IDCategoria,
                C.NombreCategoria,
                C.Descripcion,
                COUNT(DISTINCT B.IDLibro) AS TotalLibros,
                COUNT(DISTINCT L.IDLoan) AS TotalPrestamos,
                SUM(B.CantidadDisponible) AS LibrosDisponibles,
                SUM(B.CantidadTotal - B.CantidadDisponible) AS LibrosPrestados
            FROM dbo.Categories C
            LEFT JOIN dbo.Books B ON C.IDCategoria = B.IDCategoria
            LEFT JOIN dbo.Loans L ON B.IDLibro = L.IDLibro
            WHERE C.NombreCategoria LIKE ?
            GROUP BY C.IDCategoria, C.NombreCategoria, C.Descripcion
        """, (f"%{category_name}%",))
        return cur.fetchall()


def sp_compare_authors(author1: str, author2: str, user_role=None):
    """
    Compara estadísticas de dos autores.
    Retorna: (author_name, libro_count, loan_count)
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("""
            SELECT 
                A.NombreAutor,
                COUNT(DISTINCT B.IDLibro) AS TotalLibros,
                COUNT(L.IDLoan) AS TotalPrestamos
            FROM dbo.Authors A
            LEFT JOIN dbo.BookAuthors BA ON A.IDAutor = BA.IDAutores
            LEFT JOIN dbo.Books B ON BA.IDLibros = B.IDLibro
            LEFT JOIN dbo.Loans L ON B.IDLibro = L.IDLibro
            WHERE A.NombreAutor LIKE ? OR A.NombreAutor LIKE ?
            GROUP BY A.IDAutor, A.NombreAutor
            ORDER BY A.NombreAutor
        """, (f"%{author1}%", f"%{author2}%"))
        return cur.fetchall()


# ─────────────────────────────────────────────
# INSERCIONES - CRUD PARA ADMIN
# ─────────────────────────────────────────────

def sp_insert_author(nombre: str, nacionalidad: str, user_role=None):
    """
    Inserta un nuevo autor en la BD.
    Retorna: IDAutor del autor creado
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        try:
            cur.execute("""
                INSERT INTO dbo.Authors (NombreAutor, Nacionalidad)
                VALUES (?, ?)
            """, (nombre, nacionalidad))
            cn.commit()
            
            # Obtener el ID del autor insertado
            cur.execute("SELECT IDENT_CURRENT('dbo.Authors') AS IDAutor")
            result = cur.fetchone()
            return int(result[0]) if result else None
        except Exception as e:
            cn.rollback()
            raise Exception(f"Error al insertar autor: {str(e)}")


def sp_insert_category(nombre: str, descripcion: str, user_role=None):
    """
    Inserta una nueva categoría en la BD.
    Retorna: IDCategoria de la categoría creada
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        try:
            cur.execute("""
                INSERT INTO dbo.Categories (NombreCategoria, Descripcion)
                VALUES (?, ?)
            """, (nombre, descripcion))
            cn.commit()
            
            # Obtener el ID de la categoría insertada
            cur.execute("SELECT IDENT_CURRENT('dbo.Categories') AS IDCategoria")
            result = cur.fetchone()
            return int(result[0]) if result else None
        except Exception as e:
            cn.rollback()
            raise Exception(f"Error al insertar categoría: {str(e)}")


def sp_insert_book(titulo: str, isbn: str, year: int, id_categoria: int, cantidad: int, user_role=None):
    """
    Inserta un nuevo libro en la BD.
    Retorna: IDLibro del libro creado
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        try:
            cur.execute("""
                INSERT INTO dbo.Books (TituloLibro, ISBN, AnioPublicacion, IDCategoria, CantidadTotal, CantidadDisponible)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (titulo, isbn, year, id_categoria, cantidad, cantidad))
            cn.commit()
            
            # Obtener el ID del libro insertado
            cur.execute("SELECT IDENT_CURRENT('dbo.Books') AS IDLibro")
            result = cur.fetchone()
            return int(result[0]) if result else None
        except Exception as e:
            cn.rollback()
            raise Exception(f"Error al insertar libro: {str(e)}")


def sp_insert_book_author(id_libro: int, id_autor: int, user_role=None):
    """
    Crea una relación entre un libro y un autor usando el stored procedure.
    Retorna: True si se insertó correctamente
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        try:
            cur.execute(
                "EXEC dbo.SP_InsertBookAuthor @IDLibro = ?, @IDAutor = ?",
                (id_libro, id_autor)
            )
            cn.commit()
            return True
        except Exception as e:
            cn.rollback()
            raise Exception(f"Error al crear relación libro-autor: {str(e)}")


def get_category_id(category_name: str, user_role=None):
    """
    Obtiene el ID de una categoría por nombre.
    Retorna: IDCategoria o None si no existe
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("SELECT IDCategoria FROM dbo.Categories WHERE NombreCategoria = ?", (category_name,))
        result = cur.fetchone()
        return result[0] if result else None


def get_author_id(author_name: str, user_role=None):
    """
    Obtiene el ID de un autor por nombre.
    Retorna: IDAutor o None si no existe
    """
    with get_connection(user_role) as cn:
        cur = cn.cursor()
        cur.execute("SELECT IDAutor FROM dbo.Authors WHERE NombreAutor = ?", (author_name,))
        result = cur.fetchone()
        return result[0] if result else None