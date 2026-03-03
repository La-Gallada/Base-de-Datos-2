---------------------------------------------------------------------
--                     BASE DE DATOS PROYECTO                      --
---------------------------------------------------------------------

USE master
GO;

--Crear la base de datos
CREATE DATABASE BibliotecaBD
GO;

USE BibliotecaBD
GO;

-- Logins 

CREATE LOGIN login_dirBiblioteca WITH PASSWORD = 'quijotedon10',
CHECK_POLICY = ON;

CREATE LOGIN login_client WITH PASSWORD = 'amoleer2026',
CHECK_POLICY = ON;

CREATE LOGIN login_author WITH PASSWORD ='amoescribir2024', 
CHECK_POLICY = ON;


--------------------------

--users
CREATE USER usr_dirBiblioteca FOR LOGIN login_dirBiblioteca;
CREATE USER usr_client FOR LOGIN login_client;
CREATE USER usr_author FOR LOGIN login_author;
--crear roles
CREATE ROLE rol_lectura_books; 
CREATE ROLE rol_ejecuta_lend; 
CREATE ROLE rol_director; 
CREATE ROLE rol_admin_lends; 

---------------------------------------------------------
--               Tablas de la base de datos            --
---------------------------------------------------------

--Tabla usuarios

CREATE TABLE dbo.Users(
IDUsuario INT IDENTITY(1,1) NOT NULL,
NombreUsuario NVARCHAR(50) NOT NULL,
ApellidoUsuario NVARCHAR(50) NOT NULL,
EmailUsuario NVARCHAR(100) NOT NULL UNIQUE,
TipoUsuario NVARCHAR(30) NOT NULL,
EstadoUsuario NVARCHAR(20) NOT NULL,
CONSTRAINT PK_IDUsuario PRIMARY KEY (IDUsuario)
);
GO

--Tabla de categorias

CREATE TABLE dbo.Categories(
IDCategoria INT IDENTITY(1,1) NOT NULL,
NombreCategoria NVARCHAR(50) NOT NULL UNIQUE,
Descripcion NVARCHAR(200) NOT NULL,
CONSTRAINT PK_IDCategoria PRIMARY KEY(IDCategoria)
);
GO

--Tabla de libros

CREATE TABLE dbo.Books(
IDLibro INT IDENTITY(1,1) NOT NULL,
TituloLibro NVARCHAR(100) NOT NULL,
ISBN VARCHAR(20) NOT NULL UNIQUE,
AnioPublicacion INT NOT NULL,
CantidadTotal INT NOT NULL,
CantidadDisponible INT NOT NULL,
IDCategoria INT,
CONSTRAINT PK_IDLibro PRIMARY KEY(IDLibro),
CONSTRAINT FK_IDCategoria FOREIGN KEY(IDCategoria) REFERENCES dbo.Categories(IDCategoria)
);
GO

---Tabla autores
CREATE TABLE dbo.Authors(
IDAutor INT IDENTITY(1,1) NOT NULL,
NombreAutor NVARCHAR(50) NOT NULL,
Nacionalidad NVARCHAR(50) NOT NULL,
CONSTRAINT PK_IDAutor PRIMARY KEY(IDAutor)
);
GO

--Tabla préstamos

CREATE TABLE dbo.Loans(
IDLoan INT IDENTITY(1,1) NOT NULL,
IDUsuario INT NOT NULL,
IDLibro INT NOT NULL,
FechaPrestamo DATE NOT NULL,
FechaDevolucion DATE NOT NULL,
FechaDevolucionReal DATE NULL,
Estado VARCHAR(20) NOT NULL,
CONSTRAINT PK_IDLoan PRIMARY KEY(IDLoan),
CONSTRAINT FK_IDUsuario FOREIGN KEY(IDUsuario) REFERENCES dbo.Users(IDUsuario),
CONSTRAINT FK_IDLibro FOREIGN KEY(IDLibro) REFERENCES dbo.Books(IDLibro)
);
GO

--Tabla LibroAutores

CREATE TABLE dbo.BookAuthors(
IDLibros INT NOT NULL,
IDAutores INT NOT NULL,
CONSTRAINT FK_IDLibros FOREIGN KEY(IDLibros) REFERENCES dbo.Books(IDLibro),
CONSTRAINT FK_IDAutores FOREIGN KEY(IDAutores) REFERENCES dbo.Authors(IDAutor)
);
GO

-------------------------------------------------------------------------
--                    PROCEDIMIENTOS ALMACENADOS
-------------------------------------------------------------------------


/* ============================================================
   TABLA: USERS
   ============================================================ */

-- SP_InsertUser
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

-- SP_UpdateUser
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

-- SP_DeleteUser
CREATE PROCEDURE dbo.SP_DeleteUser
    @IDUsuario INT
AS
BEGIN
    SET NOCOUNT ON;

    DELETE FROM dbo.Users
    WHERE IDUsuario = @IDUsuario;
END
GO

-- SP_GetUsers
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

-- SP_InsertAuthor
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

-- SP_UpdateAuthor
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

-- SP_DeleteAuthor
CREATE PROCEDURE dbo.SP_DeleteAuthor
    @IDAutor INT
AS
BEGIN
    SET NOCOUNT ON;

    DELETE FROM dbo.Authors
    WHERE IDAutor = @IDAutor;
END
GO

-- SP_GetAuthors
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

-- SP_InsertCategory
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

-- SP_GetCategories
CREATE PROCEDURE dbo.SP_GetCategories
AS
BEGIN
    SET NOCOUNT ON;

    SELECT * FROM dbo.Categories;
END
GO


/* ============================================================
   TABLA: BOOKS
   ============================================================ */

-- SP_InsertBook
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

-- SP_UpdateBook
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

-- SP_DeleteBook
CREATE PROCEDURE dbo.SP_DeleteBook
    @IDLibro INT
AS
BEGIN
    SET NOCOUNT ON;

    DELETE FROM dbo.Books
    WHERE IDLibro = @IDLibro;
END
GO

-- SP_GetBooks
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


/* ============================================================
   TABLA: LOANS
   ============================================================ */

-- SP_InsertLoan
CREATE PROCEDURE dbo.SP_InsertLoan
    @IDUsuario INT,
    @IDLibro INT,
    @FechaPrestamo DATE,
    @FechaDevolucion DATE
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM dbo.Books 
               WHERE IDLibro = @IDLibro 
               AND CantidadDisponible > 0)
    BEGIN
        INSERT INTO dbo.Loans
        (IDUsuario, IDLibro, FechaPrestamo, FechaDevolucion, Estado)
        VALUES
        (@IDUsuario, @IDLibro, @FechaPrestamo, @FechaDevolucion, 'Prestado');

        UPDATE dbo.Books
        SET CantidadDisponible = CantidadDisponible - 1
        WHERE IDLibro = @IDLibro;
    END
    ELSE
    BEGIN
        RAISERROR('No hay ejemplares disponibles.',16,1);
    END
END
GO

-- SP_ReturnLoan
CREATE PROCEDURE dbo.SP_ReturnLoan
    @IDLoan INT,
    @FechaDevolucionReal DATE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @IDLibro INT;

    SELECT @IDLibro = IDLibro
    FROM dbo.Loans
    WHERE IDLoan = @IDLoan;

    UPDATE dbo.Loans
    SET FechaDevolucionReal = @FechaDevolucionReal,
        Estado = 'Devuelto'
    WHERE IDLoan = @IDLoan;

    UPDATE dbo.Books
    SET CantidadDisponible = CantidadDisponible + 1
    WHERE IDLibro = @IDLibro;
END
GO

-- SP_GetAllLoans
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

-- SP_DeleteLoan
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

-- SP_GetActiveLoans
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

-- SP_InsertBookAuthor
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

-- SP_DeleteBookAuthor
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

-- SP_GetBookAuthors
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




