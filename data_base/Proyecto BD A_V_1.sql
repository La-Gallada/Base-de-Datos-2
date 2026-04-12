/* =========================================================
   Base de datos: BibliotecaBD
   Motor: Microsoft SQL Server

   OBJETIVO DE ESTA VERSIÓN
   - Evitar errores por CREATE OR ALTER
   - Re-ejecutar el script completo sin que explote
   - Mantener orden correcto de creación
   - Evitar conflictos entre SP y triggers en el manejo de stock
   ========================================================= */

---------------------------------------------------------------------
-- 0. LIMPIEZA PREVIA
---------------------------------------------------------------------

USE master;
GO

/* 
   Si la base ya existe, se elimina para permitir una ejecución limpia.
*/
IF DB_ID('BibliotecaBD') IS NOT NULL
BEGIN
    ALTER DATABASE BibliotecaBD SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE BibliotecaBD;
END
GO

/*
   Si los logins ya existen, se eliminan antes de recrearlos.
*/
IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_dirBiblioteca')
    DROP LOGIN login_dirBiblioteca;
GO

IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_client')
    DROP LOGIN login_client;
GO

IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_author')
    DROP LOGIN login_author;
GO

---------------------------------------------------------------------
-- 1. CREACIÓN DE LA BASE DE DATOS
---------------------------------------------------------------------

CREATE DATABASE BibliotecaBD;
GO

USE BibliotecaBD;
GO

---------------------------------------------------------------------
-- 2. CREACIÓN DE LOGINS (NIVEL SERVIDOR)
---------------------------------------------------------------------

/*
    Los LOGINS permiten autenticarse en el servidor SQL Server.
    Son cuentas a nivel servidor, no aún dentro de la base de datos.
*/

-- Login para el Director de la Biblioteca
CREATE LOGIN login_dirBiblioteca 
WITH PASSWORD = 'quijotedon10',
CHECK_POLICY = ON;

-- Login para los clientes
CREATE LOGIN login_client 
WITH PASSWORD = 'amoleer2026',
CHECK_POLICY = ON;

-- Login para los autores
CREATE LOGIN login_author 
WITH PASSWORD = 'amoescribir2024',
CHECK_POLICY = ON;
GO

---------------------------------------------------------------------
-- 3. CREACIÓN DE USERS (NIVEL BASE DE DATOS)
---------------------------------------------------------------------

USE BibliotecaBD;
GO

/*
    Los USERS se crean dentro de la base de datos y se vinculan
    a un LOGIN previamente creado.
*/

CREATE USER usr_dirBiblioteca FOR LOGIN login_dirBiblioteca;
CREATE USER usr_client FOR LOGIN login_client;
CREATE USER usr_author FOR LOGIN login_author;
GO

---------------------------------------------------------------------
-- 4. CREACIÓN DE ROLES PERSONALIZADOS
---------------------------------------------------------------------

/*
    Los ROLES permiten agrupar permisos.
    En lugar de asignar permisos directamente a cada usuario,
    se asignan a un rol y luego se agregan los usuarios a ese rol.
    Esto facilita la administración y mejora la seguridad.
*/

CREATE ROLE rol_lectura_books;
CREATE ROLE rol_ejecuta_lend;
CREATE ROLE rol_director;
CREATE ROLE rol_admin_lends;
GO

---------------------------------------------------------
--               TABLAS DE LA BASE DE DATOS            --
---------------------------------------------------------

/*
    En esta sección se crean todas las tablas necesarias
    para el funcionamiento del sistema de Biblioteca.

    Se definen:
    - Claves primarias (PRIMARY KEY)
    - Claves foráneas (FOREIGN KEY)
    - Restricciones UNIQUE
    - Campos obligatorios (NOT NULL)
*/

---------------------------------------------------------
-- 1. TABLA USERS
---------------------------------------------------------

CREATE TABLE dbo.Users(
    IDUsuario INT IDENTITY(1,1) NOT NULL,
        -- Clave primaria autoincremental que identifica
        -- de forma única a cada usuario.

    NombreUsuario NVARCHAR(50) NOT NULL,
        -- Nombre del usuario (no permite valores nulos).

    ApellidoUsuario NVARCHAR(50) NOT NULL,
        -- Apellido del usuario.

    EmailUsuario NVARCHAR(100) NOT NULL UNIQUE,
        -- Correo electrónico del usuario.
        -- Se define UNIQUE para evitar duplicados.

    TipoUsuario NVARCHAR(30) NOT NULL,
        -- Define el rol del usuario dentro del sistema
        -- (Ej: Cliente, Administrador, Director).

    EstadoUsuario NVARCHAR(20) NOT NULL,
        -- Indica si el usuario está Activo, Inactivo, Suspendido, etc.

    CONSTRAINT PK_IDUsuario PRIMARY KEY (IDUsuario)
        -- Se define la clave primaria de la tabla.
);
GO

---------------------------------------------------------
-- 2. TABLA CATEGORIES
---------------------------------------------------------

CREATE TABLE dbo.Categories(
    IDCategoria INT IDENTITY(1,1) NOT NULL,
        -- Identificador único de cada categoría.

    NombreCategoria NVARCHAR(50) NOT NULL UNIQUE,
        -- Nombre de la categoría (no se permiten repetidos).

    Descripcion NVARCHAR(200) NOT NULL,
        -- Descripción detallada de la categoría.

    CONSTRAINT PK_IDCategoria PRIMARY KEY(IDCategoria)
);
GO

---------------------------------------------------------
-- 3. TABLA BOOKS
---------------------------------------------------------

CREATE TABLE dbo.Books(
    IDLibro INT IDENTITY(1,1) NOT NULL,
        -- Identificador único del libro.

    TituloLibro NVARCHAR(100) NOT NULL,
        -- Título del libro.

    ISBN VARCHAR(20) NOT NULL UNIQUE,
        -- Código ISBN único para cada libro.

    AnioPublicacion INT NOT NULL,
        -- Año de publicación del libro.

    CantidadTotal INT NOT NULL,
        -- Número total de ejemplares registrados.

    CantidadDisponible INT NOT NULL,
        -- Número de ejemplares disponibles para préstamo.

    IDCategoria INT,
        -- Clave foránea que referencia la categoría del libro.

    CONSTRAINT PK_IDLibro PRIMARY KEY(IDLibro),

    CONSTRAINT FK_IDCategoria 
        FOREIGN KEY(IDCategoria) 
        REFERENCES dbo.Categories(IDCategoria),

    -- Restricciones CHECK agregadas para mayor robustez
    CONSTRAINT CK_Books_CantidadTotal_NoNegativa
        CHECK (CantidadTotal >= 0),

    CONSTRAINT CK_Books_CantidadDisponible_Rango
        CHECK (CantidadDisponible >= 0 AND CantidadDisponible <= CantidadTotal)
);
GO

---------------------------------------------------------
-- 4. TABLA AUTHORS
---------------------------------------------------------

CREATE TABLE dbo.Authors(
    IDAutor INT IDENTITY(1,1) NOT NULL,
        -- Identificador único del autor.

    NombreAutor NVARCHAR(50) NOT NULL,
        -- Nombre completo del autor.

    Nacionalidad NVARCHAR(50) NOT NULL,
        -- Nacionalidad del autor.

    CONSTRAINT PK_IDAutor PRIMARY KEY(IDAutor)
);
GO

---------------------------------------------------------
-- 5. TABLA LOANS
---------------------------------------------------------

CREATE TABLE dbo.Loans(
    IDLoan INT IDENTITY(1,1) NOT NULL,
        -- Identificador único del préstamo.

    IDUsuario INT NOT NULL,
        -- Usuario que realiza el préstamo.

    IDLibro INT NOT NULL,
        -- Libro que se presta.

    FechaPrestamo DATE NOT NULL,
        -- Fecha en que se realiza el préstamo.

    FechaDevolucion DATE NOT NULL,
        -- Fecha límite de devolución.

    FechaDevolucionReal DATE NULL,
        -- Fecha real en que se devuelve el libro.
        -- Puede ser NULL si aún no se ha devuelto.

    Estado VARCHAR(20) NOT NULL,
        -- Estado del préstamo (Prestado, Devuelto, Atrasado, etc.).

    CONSTRAINT PK_IDLoan PRIMARY KEY(IDLoan),

    CONSTRAINT FK_IDUsuario 
        FOREIGN KEY(IDUsuario) 
        REFERENCES dbo.Users(IDUsuario),

    CONSTRAINT FK_IDLibro 
        FOREIGN KEY(IDLibro) 
        REFERENCES dbo.Books(IDLibro),

    -- Restricción CHECK agregada para estados válidos
    CONSTRAINT CK_Loans_Estado_Valido
        CHECK (Estado IN ('Prestado','Devuelto','Atrasado'))
);
GO

---------------------------------------------------------
-- 6. TABLA BookAuthors (RELACIÓN MUCHOS A MUCHOS)
---------------------------------------------------------

CREATE TABLE dbo.BookAuthors(
    IDLibros INT NOT NULL,
        -- Identificador del libro.

    IDAutores INT NOT NULL,
        -- Identificador del autor.

    CONSTRAINT FK_IDLibros 
        FOREIGN KEY(IDLibros) 
        REFERENCES dbo.Books(IDLibro),

    CONSTRAINT FK_IDAutores 
        FOREIGN KEY(IDAutores) 
        REFERENCES dbo.Authors(IDAutor),

    CONSTRAINT PK_BookAuthors 
        PRIMARY KEY (IDLibros, IDAutores)
);
GO

-------------------------------------------------------------------------
--                    PROCEDIMIENTOS ALMACENADOS
-------------------------------------------------------------------------

USE BibliotecaBD;
GO

/* ============================================================
   TABLA: USERS
   ============================================================ */

IF OBJECT_ID('dbo.SP_InsertUser', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_InsertUser;
GO
CREATE PROCEDURE dbo.SP_InsertUser
    @NombreUsuario NVARCHAR(50),
    @ApellidoUsuario NVARCHAR(50),
    @EmailUsuario NVARCHAR(100),
    @TipoUsuario NVARCHAR(30),
    @EstadoUsuario NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.Users
    (NombreUsuario, ApellidoUsuario, EmailUsuario, TipoUsuario, EstadoUsuario)
    VALUES
    (@NombreUsuario, @ApellidoUsuario, @EmailUsuario, @TipoUsuario, @EstadoUsuario);
END
GO

IF OBJECT_ID('dbo.SP_UpdateUser', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_UpdateUser;
GO
CREATE PROCEDURE dbo.SP_UpdateUser
    @IDUsuario INT,
    @NombreUsuario NVARCHAR(50),
    @ApellidoUsuario NVARCHAR(50),
    @EmailUsuario NVARCHAR(100),
    @TipoUsuario NVARCHAR(30),
    @EstadoUsuario NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE dbo.Users
    SET NombreUsuario = @NombreUsuario,
        ApellidoUsuario = @ApellidoUsuario,
        EmailUsuario = @EmailUsuario,
        TipoUsuario = @TipoUsuario,
        EstadoUsuario = @EstadoUsuario
    WHERE IDUsuario = @IDUsuario;
END
GO

IF OBJECT_ID('dbo.SP_DeleteUser', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_DeleteUser;
GO
CREATE PROCEDURE dbo.SP_DeleteUser
    @IDUsuario INT
AS
BEGIN
    SET NOCOUNT ON;

    DELETE FROM dbo.Users
    WHERE IDUsuario = @IDUsuario;
END
GO

IF OBJECT_ID('dbo.SP_GetUsers', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetUsers;
GO
CREATE PROCEDURE dbo.SP_GetUsers
AS
BEGIN
    SET NOCOUNT ON;

    SELECT * FROM dbo.Users;
END
GO

/* ============================================================
   TABLA: AUTHORS
   ============================================================ */

IF OBJECT_ID('dbo.SP_InsertAuthor', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_InsertAuthor;
GO
CREATE PROCEDURE dbo.SP_InsertAuthor
    @NombreAutor NVARCHAR(50),
    @Nacionalidad NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.Authors (NombreAutor, Nacionalidad)
    VALUES (@NombreAutor, @Nacionalidad);
END
GO

IF OBJECT_ID('dbo.SP_UpdateAuthor', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_UpdateAuthor;
GO
CREATE PROCEDURE dbo.SP_UpdateAuthor
    @IDAutor INT,
    @NombreAutor NVARCHAR(50),
    @Nacionalidad NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE dbo.Authors
    SET NombreAutor = @NombreAutor,
        Nacionalidad = @Nacionalidad
    WHERE IDAutor = @IDAutor;
END
GO

IF OBJECT_ID('dbo.SP_DeleteAuthor', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_DeleteAuthor;
GO
CREATE PROCEDURE dbo.SP_DeleteAuthor
    @IDAutor INT
AS
BEGIN
    SET NOCOUNT ON;

    DELETE FROM dbo.Authors
    WHERE IDAutor = @IDAutor;
END
GO

IF OBJECT_ID('dbo.SP_GetAuthors', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetAuthors;
GO
CREATE PROCEDURE dbo.SP_GetAuthors
AS
BEGIN
    SET NOCOUNT ON;

    SELECT * FROM dbo.Authors;
END
GO

/* ============================================================
   TABLA: CATEGORIES
   ============================================================ */

IF OBJECT_ID('dbo.SP_InsertCategory', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_InsertCategory;
GO
CREATE PROCEDURE dbo.SP_InsertCategory
    @NombreCategoria NVARCHAR(50),
    @Descripcion NVARCHAR(200)
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.Categories (NombreCategoria, Descripcion)
    VALUES (@NombreCategoria, @Descripcion);
END
GO

IF OBJECT_ID('dbo.SP_GetCategories', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetCategories;
GO
CREATE PROCEDURE dbo.SP_GetCategories
AS
BEGIN
    SET NOCOUNT ON;

    SELECT * FROM dbo.Categories;
END
GO

IF OBJECT_ID('dbo.SP_UpdateCategory', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_UpdateCategory;
GO
CREATE PROCEDURE dbo.SP_UpdateCategory
    @IDCategoria INT,
    @NombreCategoria NVARCHAR(50),
    @Descripcion NVARCHAR(200)
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE dbo.Categories
    SET NombreCategoria = @NombreCategoria,
        Descripcion = @Descripcion
    WHERE IDCategoria = @IDCategoria;
END
GO

IF OBJECT_ID('dbo.SP_DeleteCategory', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_DeleteCategory;
GO
CREATE PROCEDURE dbo.SP_DeleteCategory
    @IDCategoria INT
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM dbo.Books WHERE IDCategoria = @IDCategoria)
    BEGIN
        RAISERROR('No se puede eliminar la categoría porque tiene libros asociados.', 16, 1);
        RETURN;
    END

    DELETE FROM dbo.Categories
    WHERE IDCategoria = @IDCategoria;
END
GO

/* ============================================================
   TABLA: BOOKS
   ============================================================ */

IF OBJECT_ID('dbo.SP_InsertBook', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_InsertBook;
GO
CREATE PROCEDURE dbo.SP_InsertBook
    @TituloLibro NVARCHAR(100),
    @ISBN VARCHAR(20),
    @AnioPublicacion INT,
    @CantidadTotal INT,
    @IDCategoria INT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.Books
    (TituloLibro, ISBN, AnioPublicacion, CantidadTotal, CantidadDisponible, IDCategoria)
    VALUES
    (@TituloLibro, @ISBN, @AnioPublicacion, @CantidadTotal, @CantidadTotal, @IDCategoria);
END
GO

IF OBJECT_ID('dbo.SP_UpdateBook', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_UpdateBook;
GO
CREATE PROCEDURE dbo.SP_UpdateBook
    @IDLibro INT,
    @TituloLibro NVARCHAR(100),
    @AnioPublicacion INT,
    @CantidadTotal INT,
    @CantidadDisponible INT,
    @IDCategoria INT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE dbo.Books
    SET TituloLibro = @TituloLibro,
        AnioPublicacion = @AnioPublicacion,
        CantidadTotal = @CantidadTotal,
        CantidadDisponible = @CantidadDisponible,
        IDCategoria = @IDCategoria
    WHERE IDLibro = @IDLibro;
END
GO

IF OBJECT_ID('dbo.SP_DeleteBook', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_DeleteBook;
GO
CREATE PROCEDURE dbo.SP_DeleteBook
    @IDLibro INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM dbo.Books WHERE IDLibro = @IDLibro)
        BEGIN
            RAISERROR('El libro no existe.', 16, 1);
            RETURN;
        END

        IF EXISTS (SELECT 1 FROM dbo.Loans WHERE IDLibro = @IDLibro)
        BEGIN
            RAISERROR('No se puede eliminar el libro porque tiene préstamos asociados.', 16, 1);
            RETURN;
        END

        DELETE FROM dbo.BookAuthors
        WHERE IDLibros = @IDLibro;

        DELETE FROM dbo.Books
        WHERE IDLibro = @IDLibro;

        PRINT 'Libro eliminado correctamente.';
    END TRY
    BEGIN CATCH
        DECLARE @MensajeError NVARCHAR(4000);
        SET @MensajeError = ERROR_MESSAGE();
        RAISERROR(@MensajeError, 16, 1);
    END CATCH
END
GO

IF OBJECT_ID('dbo.SP_GetBooks', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetBooks;
GO
CREATE PROCEDURE dbo.SP_GetBooks
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        B.IDLibro,
        B.TituloLibro,
        B.ISBN,
        B.AnioPublicacion,
        B.CantidadTotal,
        B.CantidadDisponible,
        C.NombreCategoria
    FROM dbo.Books B
    INNER JOIN dbo.Categories C
        ON B.IDCategoria = C.IDCategoria;
END
GO

IF OBJECT_ID('dbo.SP_GetBookById', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetBookById;
GO
CREATE PROCEDURE dbo.SP_GetBookById
    @IDLibro INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        B.IDLibro,
        B.TituloLibro,
        B.ISBN,
        B.AnioPublicacion,
        B.CantidadTotal,
        B.CantidadDisponible,
        C.NombreCategoria
    FROM dbo.Books B
    INNER JOIN dbo.Categories C
        ON B.IDCategoria = C.IDCategoria
    WHERE B.IDLibro = @IDLibro;
END
GO

IF OBJECT_ID('dbo.SP_SearchBooks', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_SearchBooks;
GO
CREATE PROCEDURE dbo.SP_SearchBooks
    @Title NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        B.IDLibro,
        B.TituloLibro,
        B.ISBN,
        B.AnioPublicacion,
        B.CantidadTotal,
        B.CantidadDisponible,
        C.NombreCategoria
    FROM dbo.Books B
    INNER JOIN dbo.Categories C
        ON B.IDCategoria = C.IDCategoria
    WHERE B.TituloLibro LIKE '%' + @Title + '%';
END
GO

/* ============================================================
   TABLA: LOANS
   ============================================================ */

IF OBJECT_ID('dbo.SP_InsertLoan', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_InsertLoan;
GO
CREATE PROCEDURE dbo.SP_InsertLoan
    @IDUsuario INT,
    @IDLibro INT,
    @FechaPrestamo DATE,
    @FechaDevolucion DATE
AS
BEGIN
    SET NOCOUNT ON;

    /*
        La validación de stock y el descuento de CantidadDisponible
        se centralizan en el trigger TR_ValidarStockAntesDePrestamo.
    */
    INSERT INTO dbo.Loans
    (IDUsuario, IDLibro, FechaPrestamo, FechaDevolucion, Estado)
    VALUES
    (@IDUsuario, @IDLibro, @FechaPrestamo, @FechaDevolucion, 'Prestado');
END
GO

IF OBJECT_ID('dbo.SP_ReturnLoan', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_ReturnLoan;
GO
CREATE PROCEDURE dbo.SP_ReturnLoan
    @IDLoan INT,
    @FechaDevolucionReal DATE
AS
BEGIN
    SET NOCOUNT ON;

    /*
        El aumento de stock se centraliza en el trigger TR_DevolucionLibro.
    */
    UPDATE dbo.Loans
    SET FechaDevolucionReal = @FechaDevolucionReal,
        Estado = 'Devuelto'
    WHERE IDLoan = @IDLoan;
END
GO

IF OBJECT_ID('dbo.SP_GetAllLoans', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetAllLoans;
GO
CREATE PROCEDURE dbo.SP_GetAllLoans
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        L.IDLoan,
        U.NombreUsuario + ' ' + U.ApellidoUsuario AS Usuario,
        B.TituloLibro,
        L.FechaPrestamo,
        L.FechaDevolucion,
        L.FechaDevolucionReal,
        L.Estado
    FROM dbo.Loans L
    INNER JOIN dbo.Users U ON L.IDUsuario = U.IDUsuario
    INNER JOIN dbo.Books B ON L.IDLibro = B.IDLibro;
END
GO

IF OBJECT_ID('dbo.SP_UpdateLoan', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_UpdateLoan;
GO
CREATE PROCEDURE dbo.SP_UpdateLoan
    @IDLoan INT,
    @IDUsuario INT,
    @IDLibro INT,
    @FechaPrestamo DATE,
    @FechaDevolucion DATE,
    @FechaDevolucionReal DATE = NULL,
    @Estado VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE dbo.Loans
    SET IDUsuario = @IDUsuario,
        IDLibro = @IDLibro,
        FechaPrestamo = @FechaPrestamo,
        FechaDevolucion = @FechaDevolucion,
        FechaDevolucionReal = @FechaDevolucionReal,
        Estado = @Estado
    WHERE IDLoan = @IDLoan;
END
GO

IF OBJECT_ID('dbo.SP_GetLoans', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetLoans;
GO
CREATE PROCEDURE dbo.SP_GetLoans
AS
BEGIN
    EXEC dbo.SP_GetAllLoans;
END
GO

IF OBJECT_ID('dbo.SP_GetLoansByUser', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetLoansByUser;
GO
CREATE PROCEDURE dbo.SP_GetLoansByUser
    @IDUsuario INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        L.IDLoan,
        B.TituloLibro,
        L.FechaPrestamo,
        L.FechaDevolucion,
        L.FechaDevolucionReal,
        L.Estado
    FROM dbo.Loans L
    INNER JOIN dbo.Books B ON L.IDLibro = B.IDLibro
    WHERE L.IDUsuario = @IDUsuario;
END
GO

IF OBJECT_ID('dbo.SP_ReturnBook', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_ReturnBook;
GO
CREATE PROCEDURE dbo.SP_ReturnBook
    @IDLoan INT,
    @FechaDevolucionReal DATE
AS
BEGIN
    EXEC dbo.SP_ReturnLoan @IDLoan, @FechaDevolucionReal;
END
GO

IF OBJECT_ID('dbo.SP_DeleteLoan', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_DeleteLoan;
GO
CREATE PROCEDURE dbo.SP_DeleteLoan
    @IDLoan INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @IDLibro INT;
    DECLARE @Estado VARCHAR(20);

    SELECT 
        @IDLibro = IDLibro,
        @Estado = Estado
    FROM dbo.Loans
    WHERE IDLoan = @IDLoan;

    IF @Estado = 'Prestado'
    BEGIN
        UPDATE dbo.Books
        SET CantidadDisponible = CantidadDisponible + 1
        WHERE IDLibro = @IDLibro;
    END

    DELETE FROM dbo.Loans
    WHERE IDLoan = @IDLoan;
END
GO

IF OBJECT_ID('dbo.SP_GetActiveLoans', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetActiveLoans;
GO
CREATE PROCEDURE dbo.SP_GetActiveLoans
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        L.IDLoan,
        U.NombreUsuario + ' ' + U.ApellidoUsuario AS Usuario,
        B.TituloLibro,
        L.FechaPrestamo,
        L.FechaDevolucion,
        L.Estado
    FROM dbo.Loans L
    INNER JOIN dbo.Users U ON L.IDUsuario = U.IDUsuario
    INNER JOIN dbo.Books B ON L.IDLibro = B.IDLibro
    WHERE L.Estado = 'Prestado';
END
GO

/* ============================================================
   TABLA: BOOKAUTHORS
   ============================================================ */

IF OBJECT_ID('dbo.SP_InsertBookAuthor', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_InsertBookAuthor;
GO
CREATE PROCEDURE dbo.SP_InsertBookAuthor
    @IDLibro INT,
    @IDAutor INT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.BookAuthors (IDLibros, IDAutores)
    VALUES (@IDLibro, @IDAutor);
END
GO

IF OBJECT_ID('dbo.SP_DeleteBookAuthor', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_DeleteBookAuthor;
GO
CREATE PROCEDURE dbo.SP_DeleteBookAuthor
    @IDLibro INT,
    @IDAutor INT
AS
BEGIN
    SET NOCOUNT ON;

    DELETE FROM dbo.BookAuthors
    WHERE IDLibros = @IDLibro
      AND IDAutores = @IDAutor;
END
GO

IF OBJECT_ID('dbo.SP_GetBookAuthors', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetBookAuthors;
GO
CREATE PROCEDURE dbo.SP_GetBookAuthors
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        B.IDLibro,
        B.TituloLibro,
        A.IDAutor,
        A.NombreAutor,
        A.Nacionalidad
    FROM dbo.BookAuthors BA
    INNER JOIN dbo.Books B ON BA.IDLibros = B.IDLibro
    INNER JOIN dbo.Authors A ON BA.IDAutores = A.IDAutor;
END
GO

IF OBJECT_ID('dbo.SP_SearchBooksByAuthor', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_SearchBooksByAuthor;
GO
CREATE PROCEDURE dbo.SP_SearchBooksByAuthor
    @AuthorName NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
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
    WHERE A.NombreAutor LIKE '%' + @AuthorName + '%'
    ORDER BY B.TituloLibro;
END
GO

IF OBJECT_ID('dbo.SP_SearchBooksByYear', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_SearchBooksByYear;
GO
CREATE PROCEDURE dbo.SP_SearchBooksByYear
    @Year INT
AS
BEGIN
    SET NOCOUNT ON;
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
    WHERE B.AnioPublicacion = @Year
    ORDER BY B.TituloLibro;
END
GO

IF OBJECT_ID('dbo.SP_GetBooksByYearRange', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetBooksByYearRange;
GO
CREATE PROCEDURE dbo.SP_GetBooksByYearRange
    @StartYear INT,
    @EndYear INT
AS
BEGIN
    SET NOCOUNT ON;
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
    WHERE B.AnioPublicacion BETWEEN @StartYear AND @EndYear
    ORDER BY B.AnioPublicacion DESC, B.TituloLibro;
END
GO

IF OBJECT_ID('dbo.SP_SearchBooksByGenre', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_SearchBooksByGenre;
GO
CREATE PROCEDURE dbo.SP_SearchBooksByGenre
    @Genre NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
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
    WHERE C.NombreCategoria LIKE '%' + @Genre + '%'
       OR C.Descripcion LIKE '%' + @Genre + '%'
    ORDER BY B.TituloLibro;
END
GO

IF OBJECT_ID('dbo.SP_GetMostLoanedBooks', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetMostLoanedBooks;
GO
CREATE PROCEDURE dbo.SP_GetMostLoanedBooks
    @Limit INT = 10
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP (@Limit)
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
    ORDER BY COUNT(L.IDLoan) DESC, B.TituloLibro;
END
GO

IF OBJECT_ID('dbo.SP_GetLeastLoanedBooks', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetLeastLoanedBooks;
GO
CREATE PROCEDURE dbo.SP_GetLeastLoanedBooks
    @Limit INT = 10
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP (@Limit)
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
    ORDER BY COUNT(L.IDLoan) ASC, B.TituloLibro;
END
GO

IF OBJECT_ID('dbo.SP_GetLoanHistoryById', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetLoanHistoryById;
GO
CREATE PROCEDURE dbo.SP_GetLoanHistoryById
    @IDUsuario INT
AS
BEGIN
    SET NOCOUNT ON;
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
    WHERE L.IDUsuario = @IDUsuario
    ORDER BY L.FechaPrestamo DESC;
END
GO

IF OBJECT_ID('dbo.SP_GetLoanHistoryByName', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetLoanHistoryByName;
GO
CREATE PROCEDURE dbo.SP_GetLoanHistoryByName
    @UserName NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
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
    WHERE CONCAT(U.NombreUsuario, ' ', U.ApellidoUsuario) LIKE '%' + @UserName + '%'
    ORDER BY L.FechaPrestamo DESC;
END
GO

IF OBJECT_ID('dbo.SP_GetCategoryStats', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_GetCategoryStats;
GO
CREATE PROCEDURE dbo.SP_GetCategoryStats
    @CategoryName NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
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
    WHERE C.NombreCategoria LIKE '%' + @CategoryName + '%'
    GROUP BY C.IDCategoria, C.NombreCategoria, C.Descripcion;
END
GO

IF OBJECT_ID('dbo.SP_CompareAuthors', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_CompareAuthors;
GO
CREATE PROCEDURE dbo.SP_CompareAuthors
    @Author1 NVARCHAR(50),
    @Author2 NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        A.NombreAutor,
        COUNT(DISTINCT B.IDLibro) AS TotalLibros,
        COUNT(L.IDLoan) AS TotalPrestamos
    FROM dbo.Authors A
    LEFT JOIN dbo.BookAuthors BA ON A.IDAutor = BA.IDAutores
    LEFT JOIN dbo.Books B ON BA.IDLibros = B.IDLibro
    LEFT JOIN dbo.Loans L ON B.IDLibro = L.IDLibro
    WHERE A.NombreAutor LIKE '%' + @Author1 + '%'
       OR A.NombreAutor LIKE '%' + @Author2 + '%'
    GROUP BY A.IDAutor, A.NombreAutor
    ORDER BY A.NombreAutor;
END
GO

IF OBJECT_ID('dbo.SP_CountBooksByCategory', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_CountBooksByCategory;
GO
CREATE PROCEDURE dbo.SP_CountBooksByCategory
    @CategoryName NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT COUNT(*) AS TotalLibros
    FROM dbo.Books B
    INNER JOIN dbo.Categories C ON B.IDCategoria = C.IDCategoria
    WHERE C.NombreCategoria LIKE '%' + @CategoryName + '%';
END
GO

IF OBJECT_ID('dbo.SP_TopAuthorsByLoans', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_TopAuthorsByLoans;
GO
CREATE PROCEDURE dbo.SP_TopAuthorsByLoans
    @Year INT,
    @Month INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT 
        A.NombreAutor,
        COUNT(*) AS TotalPrestamos
    FROM dbo.Loans L
    INNER JOIN dbo.Books B ON L.IDLibro = B.IDLibro
    INNER JOIN dbo.BookAuthors BA ON B.IDLibro = BA.IDLibros
    INNER JOIN dbo.Authors A ON BA.IDAutores = A.IDAutor
    WHERE YEAR(L.FechaPrestamo) = @Year
      AND MONTH(L.FechaPrestamo) = @Month
    GROUP BY A.IDAutor, A.NombreAutor
    ORDER BY TotalPrestamos DESC;
END
GO

IF OBJECT_ID('dbo.SP_OverdueLoans', 'P') IS NOT NULL
    DROP PROCEDURE dbo.SP_OverdueLoans;
GO
CREATE PROCEDURE dbo.SP_OverdueLoans
    @AsOfDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Fecha DATE = ISNULL(@AsOfDate, GETDATE());

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
    WHERE L.Estado = 'Prestado'
      AND L.FechaDevolucion < @Fecha;
END
GO

/* =========================================================
   TRIGGERS
   ========================================================= */

USE BibliotecaBD;
GO

IF OBJECT_ID('dbo.TR_ValidarStockAntesDePrestamo', 'TR') IS NOT NULL
    DROP TRIGGER dbo.TR_ValidarStockAntesDePrestamo;
GO
CREATE TRIGGER dbo.TR_ValidarStockAntesDePrestamo
ON dbo.Loans
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM inserted)
        RETURN;

    IF EXISTS (
        SELECT 1
        FROM inserted
        WHERE IDLibro IS NULL
    )
    BEGIN
        RAISERROR('IDLibro es obligatorio para registrar préstamos.', 16, 1);
        RETURN;
    END

    DECLARE @Demanda TABLE (
        IDLibro INT PRIMARY KEY,
        CantSolicitada INT NOT NULL
    );

    INSERT INTO @Demanda (IDLibro, CantSolicitada)
    SELECT IDLibro, COUNT(*)
    FROM inserted
    GROUP BY IDLibro;

    IF EXISTS (
        SELECT 1
        FROM @Demanda D
        INNER JOIN dbo.Books B ON B.IDLibro = D.IDLibro
        WHERE B.CantidadDisponible < D.CantSolicitada
    )
    BEGIN
        RAISERROR('No hay ejemplares disponibles para completar el préstamo.', 16, 1);
        RETURN;
    END

    INSERT INTO dbo.Loans (
        IDUsuario,
        IDLibro,
        FechaPrestamo,
        FechaDevolucion,
        FechaDevolucionReal,
        Estado
    )
    SELECT
        IDUsuario,
        IDLibro,
        FechaPrestamo,
        FechaDevolucion,
        FechaDevolucionReal,
        Estado
    FROM inserted;

    UPDATE B
    SET B.CantidadDisponible = B.CantidadDisponible - D.CantSolicitada
    FROM dbo.Books B
    INNER JOIN @Demanda D ON B.IDLibro = D.IDLibro;
END;
GO

IF OBJECT_ID('dbo.TR_DevolucionLibro', 'TR') IS NOT NULL
    DROP TRIGGER dbo.TR_DevolucionLibro;
GO
CREATE TRIGGER dbo.TR_DevolucionLibro
ON dbo.Loans
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF UPDATE(FechaDevolucionReal)
    BEGIN
        DECLARE @Devoluciones TABLE (
            IDLibro INT PRIMARY KEY,
            CantDevuelta INT NOT NULL
        );

        INSERT INTO @Devoluciones (IDLibro, CantDevuelta)
        SELECT I.IDLibro, COUNT(*)
        FROM inserted I
        INNER JOIN deleted D ON I.IDLoan = D.IDLoan
        WHERE D.FechaDevolucionReal IS NULL
          AND I.FechaDevolucionReal IS NOT NULL
        GROUP BY I.IDLibro;

        IF EXISTS (
            SELECT 1
            FROM @Devoluciones DV
            INNER JOIN dbo.Books B ON B.IDLibro = DV.IDLibro
            WHERE B.CantidadDisponible + DV.CantDevuelta > B.CantidadTotal
        )
        BEGIN
            RAISERROR('La devolución excede CantidadTotal para uno o más libros.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        UPDATE B
        SET B.CantidadDisponible = B.CantidadDisponible + DV.CantDevuelta
        FROM dbo.Books B
        INNER JOIN @Devoluciones DV ON B.IDLibro = DV.IDLibro;
    END
END;
GO

IF OBJECT_ID('dbo.TR_ControlStock', 'TR') IS NOT NULL
    DROP TRIGGER dbo.TR_ControlStock;
GO
CREATE TRIGGER dbo.TR_ControlStock
ON dbo.Books
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (
        SELECT 1
        FROM inserted
        WHERE CantidadDisponible < 0
           OR CantidadDisponible > CantidadTotal
    )
    BEGIN
        RAISERROR('CantidadDisponible no puede ser negativa ni mayor que CantidadTotal.',16,1);
        ROLLBACK TRANSACTION;
    END
END;
GO

---------------------------------------------------------
-- INSERTAR CATEGORÍAS
---------------------------------------------------------

EXEC dbo.SP_InsertCategory 'Novela', 'Libros narrativos de ficción';
EXEC dbo.SP_InsertCategory 'Tecnología', 'Libros relacionados con informática y sistemas';
EXEC dbo.SP_InsertCategory 'Historia', 'Libros históricos y biográficos';
GO

---------------------------------------------------------
-- INSERTAR AUTORES
---------------------------------------------------------

EXEC dbo.SP_InsertAuthor 'Gabriel García Márquez', 'Colombiana';
EXEC dbo.SP_InsertAuthor 'Robert C. Martin', 'Estadounidense';
EXEC dbo.SP_InsertAuthor 'Yuval Noah Harari', 'Israelí';
GO

---------------------------------------------------------
-- INSERTAR USUARIOS
---------------------------------------------------------

EXEC dbo.SP_InsertUser 'Carlos', 'Ramírez', 'carlos@gmail.com', 'Cliente', 'Activo';
EXEC dbo.SP_InsertUser 'Laura', 'Fernández', 'laura@gmail.com', 'Cliente', 'Activo';
EXEC dbo.SP_InsertUser 'Mario', 'Vargas', 'mario@gmail.com', 'Administrador', 'Activo';
GO

---------------------------------------------------------
-- INSERTAR LIBROS
---------------------------------------------------------
-- Nota: IDCategoria depende del orden en que se insertaron.
-- Asumimos:
-- 1 = Novela
-- 2 = Tecnología
-- 3 = Historia

EXEC dbo.SP_InsertBook 
    'Cien años de soledad',
    '9780307474728',
    1967,
    5,
    1;

EXEC dbo.SP_InsertBook 
    'Clean Code',
    '9780132350884',
    2008,
    3,
    2;

EXEC dbo.SP_InsertBook 
    'Sapiens',
    '9780062316110',
    2011,
    4,
    3;
GO

---------------------------------------------------------
-- RELACIONAR LIBROS Y AUTORES
---------------------------------------------------------

EXEC dbo.SP_InsertBookAuthor 1, 1;
EXEC dbo.SP_InsertBookAuthor 2, 2;
EXEC dbo.SP_InsertBookAuthor 3, 3;
GO

---------------------------------------------------------
-- CREAR PRÉSTAMOS
---------------------------------------------------------

EXEC dbo.SP_InsertLoan 1, 1, '2026-02-20', '2026-03-01';
EXEC dbo.SP_InsertLoan 2, 2, '2026-02-22', '2026-03-05';
GO

-------------------------------
-----Creación de los index-----
-------------------------------

CREATE INDEX idx_books_categoria ON dbo.Books (IDCategoria);
CREATE INDEX idx_books_titulo ON dbo.Books (TituloLibro);
CREATE INDEX idx_users_email ON dbo.Users (EmailUsuario);
CREATE INDEX idx_loans_usuario ON dbo.Loans (IDUsuario);
CREATE INDEX idx_loans_libro ON dbo.Loans (IDLibro);
CREATE INDEX idx_loans_estado ON dbo.Loans (Estado);
CREATE INDEX idx_loans_fecha_devolucion ON dbo.Loans (FechaDevolucion);
CREATE INDEX idx_loans_estado_fecha ON dbo.Loans (Estado, FechaDevolucion);
CREATE INDEX idx_authors_nombre ON dbo.Authors (NombreAutor);
CREATE INDEX idx_categories_nombre ON dbo.Categories (NombreCategoria);
GO

--Justificación de los índices
--idx_books_categoria: Optimiza las consultas que relacionan libros con sus categorías mediante JOIN.
--idx_books_titulo: Mejora la velocidad de búsqueda de libros por título.
--idx_users_email: Acelera la autenticación o búsqueda de usuarios por correo electrónico.
--idx_loans_usuario: Permite obtener rápidamente los préstamos asociados a un usuario.
--idx_loans_libro: Facilita la consulta de préstamos relacionados con un libro específico.
--idx_loans_estado: Mejora el filtrado por estado del préstamo.
--idx_loans_fecha_devolucion: Optimiza consultas que dependen de fechas.
--idx_loans_estado_fecha: Mejora consultas que combinan estado y fecha.
--idx_authors_nombre: Permite búsquedas rápidas de autores por nombre.
--idx_categories_nombre: Mejora la consulta de categorías por nombre.

--------------------------------
-----Creacion de las vistas-----
--------------------------------

USE BibliotecaBD;
GO

IF OBJECT_ID('dbo.vw_BooksFull', 'V') IS NOT NULL
    DROP VIEW dbo.vw_BooksFull;
GO
CREATE VIEW dbo.vw_BooksFull AS
SELECT 
    B.IDLibro,
    B.TituloLibro,
    B.ISBN,
    B.AnioPublicacion,
    B.CantidadTotal,
    B.CantidadDisponible,
    C.NombreCategoria
FROM dbo.Books B
INNER JOIN dbo.Categories C ON B.IDCategoria = C.IDCategoria;
GO

IF OBJECT_ID('dbo.vw_ActiveLoans', 'V') IS NOT NULL
    DROP VIEW dbo.vw_ActiveLoans;
GO
CREATE VIEW dbo.vw_ActiveLoans AS
SELECT 
    L.IDLoan,
    U.NombreUsuario + ' ' + U.ApellidoUsuario AS Usuario,
    B.TituloLibro,
    L.FechaPrestamo,
    L.FechaDevolucion,
    L.Estado
FROM dbo.Loans L
JOIN dbo.Users U ON L.IDUsuario = U.IDUsuario
JOIN dbo.Books B ON L.IDLibro = B.IDLibro
WHERE L.Estado = 'Prestado';
GO

IF OBJECT_ID('dbo.vw_OverdueLoans', 'V') IS NOT NULL
    DROP VIEW dbo.vw_OverdueLoans;
GO
CREATE VIEW dbo.vw_OverdueLoans AS
SELECT *
FROM dbo.vw_ActiveLoans
WHERE FechaDevolucion < GETDATE();
GO

IF OBJECT_ID('dbo.vw_AuthorLoanStats', 'V') IS NOT NULL
    DROP VIEW dbo.vw_AuthorLoanStats;
GO
CREATE VIEW dbo.vw_AuthorLoanStats AS
SELECT 
    A.NombreAutor,
    COUNT(*) AS TotalPrestamos,
    FORMAT(L.FechaPrestamo, 'yyyy-MM') AS Periodo
FROM dbo.Loans L
JOIN dbo.Books B ON L.IDLibro = B.IDLibro
JOIN dbo.BookAuthors BA ON B.IDLibro = BA.IDLibros
JOIN dbo.Authors A ON BA.IDAutores = A.IDAutor
GROUP BY A.NombreAutor, FORMAT(L.FechaPrestamo, 'yyyy-MM');
GO

--Justificación de las vistas
--vw_BooksFull: Centraliza la información de libros junto con su categoría.
--vw_ActiveLoans: Facilita la obtención de préstamos activos.
--vw_OverdueLoans: Permite identificar rápidamente préstamos vencidos.
--vw_AuthorLoanStats: Base para análisis estadísticos de préstamos por autor y período.

---------------------------------------------------------------------
-- 5. ASIGNACIÓN DE PERMISOS A ROLES
---------------------------------------------------------------------

USE BibliotecaBD;
GO

/*
    Esta sección va al final para que todos los objetos ya existan.
*/

-- Permisos para rol_lectura_books
GRANT SELECT ON dbo.Books TO rol_lectura_books;
GRANT SELECT ON dbo.Authors TO rol_lectura_books;
GRANT SELECT ON dbo.Categories TO rol_lectura_books;
GRANT SELECT ON dbo.BookAuthors TO rol_lectura_books;

GRANT EXECUTE ON dbo.SP_GetBooks TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetAuthors TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetCategories TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_SearchBooks TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetBookById TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_SearchBooksByAuthor TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_SearchBooksByYear TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetBooksByYearRange TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_SearchBooksByGenre TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetMostLoanedBooks TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetLeastLoanedBooks TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetCategoryStats TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_CompareAuthors TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_CountBooksByCategory TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_TopAuthorsByLoans TO rol_lectura_books;

DENY SELECT ON dbo.Users TO rol_lectura_books;
DENY EXECUTE ON dbo.SP_GetUsers TO rol_lectura_books;
GO

-- Permisos para rol_ejecuta_lend
GRANT SELECT ON dbo.Loans TO rol_ejecuta_lend;
GRANT EXECUTE ON dbo.SP_InsertLoan TO rol_ejecuta_lend;
GRANT EXECUTE ON dbo.SP_GetLoansByUser TO rol_ejecuta_lend;
GRANT EXECUTE ON dbo.SP_ReturnBook TO rol_ejecuta_lend;
GRANT EXECUTE ON dbo.SP_OverdueLoans TO rol_ejecuta_lend;

-- Se retiran accesos directos a tablas sensibles
REVOKE INSERT ON dbo.Loans FROM rol_ejecuta_lend;
REVOKE UPDATE ON dbo.Books FROM rol_ejecuta_lend;
REVOKE EXECUTE ON dbo.SP_GetLoanHistoryById FROM rol_ejecuta_lend;
REVOKE EXECUTE ON dbo.SP_GetLoanHistoryByName FROM rol_ejecuta_lend;
GO

-- Permisos para rol_admin_lends
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Loans TO rol_admin_lends;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Users TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_InsertLoan TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_UpdateLoan TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_DeleteLoan TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_GetLoans TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_GetLoansByUser TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_ReturnBook TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_InsertUser TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_UpdateUser TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_DeleteUser TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_GetUsers TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_GetActiveLoans TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_SearchBooksByAuthor TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_SearchBooksByYear TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_GetBooksByYearRange TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_SearchBooksByGenre TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_GetMostLoanedBooks TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_GetLeastLoanedBooks TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_GetLoanHistoryById TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_GetLoanHistoryByName TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_GetCategoryStats TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_CompareAuthors TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_CountBooksByCategory TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_TopAuthorsByLoans TO rol_admin_lends;
GRANT EXECUTE ON dbo.SP_OverdueLoans TO rol_admin_lends;
GO

-- Permisos para rol_director
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Books TO rol_director;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Authors TO rol_director;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Categories TO rol_director;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Users TO rol_director;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Loans TO rol_director;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.BookAuthors TO rol_director;

GRANT EXECUTE ON dbo.SP_InsertBook TO rol_director;
GRANT EXECUTE ON dbo.SP_UpdateBook TO rol_director;
GRANT EXECUTE ON dbo.SP_DeleteBook TO rol_director;
GRANT EXECUTE ON dbo.SP_GetBooks TO rol_director;
GRANT EXECUTE ON dbo.SP_GetBookById TO rol_director;
GRANT EXECUTE ON dbo.SP_SearchBooks TO rol_director;
GRANT EXECUTE ON dbo.SP_InsertAuthor TO rol_director;
GRANT EXECUTE ON dbo.SP_UpdateAuthor TO rol_director;
GRANT EXECUTE ON dbo.SP_DeleteAuthor TO rol_director;
GRANT EXECUTE ON dbo.SP_GetAuthors TO rol_director;
GRANT EXECUTE ON dbo.SP_InsertCategory TO rol_director;
GRANT EXECUTE ON dbo.SP_UpdateCategory TO rol_director;
GRANT EXECUTE ON dbo.SP_DeleteCategory TO rol_director;
GRANT EXECUTE ON dbo.SP_GetCategories TO rol_director;
GRANT EXECUTE ON dbo.SP_InsertUser TO rol_director;
GRANT EXECUTE ON dbo.SP_UpdateUser TO rol_director;
GRANT EXECUTE ON dbo.SP_DeleteUser TO rol_director;
GRANT EXECUTE ON dbo.SP_GetUsers TO rol_director;
GRANT EXECUTE ON dbo.SP_InsertLoan TO rol_director;
GRANT EXECUTE ON dbo.SP_UpdateLoan TO rol_director;
GRANT EXECUTE ON dbo.SP_DeleteLoan TO rol_director;
GRANT EXECUTE ON dbo.SP_GetLoans TO rol_director;
GRANT EXECUTE ON dbo.SP_GetLoansByUser TO rol_director;
GRANT EXECUTE ON dbo.SP_ReturnBook TO rol_director;
GRANT EXECUTE ON dbo.SP_InsertBookAuthor TO rol_director;
GRANT EXECUTE ON dbo.SP_DeleteBookAuthor TO rol_director;
GRANT EXECUTE ON dbo.SP_SearchBooksByAuthor TO rol_director;
GRANT EXECUTE ON dbo.SP_SearchBooksByYear TO rol_director;
GRANT EXECUTE ON dbo.SP_GetBooksByYearRange TO rol_director;
GRANT EXECUTE ON dbo.SP_SearchBooksByGenre TO rol_director;
GRANT EXECUTE ON dbo.SP_GetMostLoanedBooks TO rol_director;
GRANT EXECUTE ON dbo.SP_GetLeastLoanedBooks TO rol_director;
GRANT EXECUTE ON dbo.SP_GetLoanHistoryById TO rol_director;
GRANT EXECUTE ON dbo.SP_GetLoanHistoryByName TO rol_director;
GRANT EXECUTE ON dbo.SP_GetCategoryStats TO rol_director;
GRANT EXECUTE ON dbo.SP_CompareAuthors TO rol_director;
GRANT EXECUTE ON dbo.SP_CountBooksByCategory TO rol_director;
GRANT EXECUTE ON dbo.SP_TopAuthorsByLoans TO rol_director;
GRANT EXECUTE ON dbo.SP_OverdueLoans TO rol_director;
GRANT EXECUTE ON dbo.SP_GetActiveLoans TO rol_director;
GO

---------------------------------------------------------------------
-- 6. ASIGNACIÓN DE USUARIOS A ROLES
---------------------------------------------------------------------

ALTER ROLE rol_lectura_books ADD MEMBER usr_client;
ALTER ROLE rol_ejecuta_lend ADD MEMBER usr_client;
ALTER ROLE rol_admin_lends ADD MEMBER usr_dirBiblioteca;
ALTER ROLE rol_director ADD MEMBER usr_dirBiblioteca;
GO

---------------------------------------------------------------------
-- PRUEBAS FINALES ORDENADAS
---------------------------------------------------------------------

/*
-- 1. Verificar datos base
EXEC dbo.SP_GetUsers;
EXEC dbo.SP_GetBooks;
EXEC dbo.SP_GetAuthors;
EXEC dbo.SP_GetCategories;
EXEC dbo.SP_GetLoans;
GO
*/

 /*
-- 2. Verificar préstamos activos y vencidos
EXEC dbo.SP_GetActiveLoans;
EXEC dbo.SP_OverdueLoans;
GO
*/

 /*
-- 3. Prueba de permisos del cliente
EXECUTE AS USER = 'usr_client';
GO

EXEC dbo.SP_GetBooks;
GO

EXEC dbo.SP_SearchBooks @Title = 'Code';
GO

DECLARE @FechaPrestamo DATE = CAST(GETDATE() AS DATE);
DECLARE @FechaDevolucion DATE = DATEADD(DAY, 7, @FechaPrestamo);

EXEC dbo.SP_InsertLoan
    @IDUsuario = 1,
    @IDLibro = 3,
    @FechaPrestamo = @FechaPrestamo,
    @FechaDevolucion = @FechaDevolucion;
GO

EXEC dbo.SP_GetUsers;
GO

REVERT;
GO
*/

 /*
-- 4. Prueba de devolución
DECLARE @FechaDevReal DATE = CAST(GETDATE() AS DATE);

EXEC dbo.SP_ReturnBook
    @IDLoan = 1,
    @FechaDevolucionReal = @FechaDevReal;
GO
*/

 /*
-- 5. Prueba multi-row de stock
BEGIN TRAN;
    INSERT INTO dbo.Loans (IDUsuario, IDLibro, FechaPrestamo, FechaDevolucion, Estado)
    VALUES
    (1, 1, GETDATE(), DATEADD(DAY, 7, GETDATE()), 'Prestado'),
    (2, 1, GETDATE(), DATEADD(DAY, 7, GETDATE()), 'Prestado');
ROLLBACK;
GO
*/

 /*
-- 6. Verificar vistas
SELECT * FROM dbo.vw_BooksFull;
SELECT * FROM dbo.vw_ActiveLoans;
SELECT * FROM dbo.vw_OverdueLoans;
SELECT * FROM dbo.vw_AuthorLoanStats;
GO
*/

---------------------------------------------------------------------
-- LIMPIEZA FINAL OPCIONAL
---------------------------------------------------------------------

/*
USE master;
GO

IF DB_ID('BibliotecaBD') IS NOT NULL
BEGIN
    ALTER DATABASE BibliotecaBD SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE BibliotecaBD;
END
GO

IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_dirBiblioteca')
    DROP LOGIN login_dirBiblioteca;
GO

IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_client')
    DROP LOGIN login_client;
GO

IF EXISTS (SELECT 1 FROM sys.server_principals WHERE name = 'login_author')
    DROP LOGIN login_author;
GO
*/