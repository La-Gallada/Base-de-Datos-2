---------------------------------------------------------------------
--                     BASE DE DATOS PROYECTO                      --
--                     SISTEMA BIBLIOTECA                          --
---------------------------------------------------------------------

/*
    Este script crea la base de datos BibliotecaBD y configura
    los accesos de seguridad mediante:
    - Logins (nivel servidor)
    - Users (nivel base de datos)
    - Roles personalizados
*/

---------------------------------------------------------------------
-- 1. SELECCIONAR BASE DE DATOS DEL SISTEMA
---------------------------------------------------------------------

-- Se utiliza la base de datos master para poder crear una nueva base de datos
USE master;
GO

---------------------------------------------------------------------
-- 2. CREACIÓN DE LA BASE DE DATOS
---------------------------------------------------------------------

-- Se crea la base de datos principal del proyecto
CREATE DATABASE BibliotecaBD;
GO

---------------------------------------------------------------------
-- 3. ACTIVAR BASE DE DATOS
---------------------------------------------------------------------

-- Se selecciona la base de datos recién creada para trabajar en ella
USE BibliotecaBD;
GO

---------------------------------------------------------------------
-- 4. CREACIÓN DE LOGINS (NIVEL SERVIDOR)
---------------------------------------------------------------------

/*
    Los LOGINS permiten autenticarse en el servidor SQL Server.
    Son cuentas a nivel servidor, no aún dentro de la base de datos.
*/

-- Login para el Director de la Biblioteca
CREATE LOGIN login_dirBiblioteca 
WITH PASSWORD = 'quijotedon10',
CHECK_POLICY = ON;   -- Activa políticas de seguridad (contraseña fuerte)

-- Login para los clientes
CREATE LOGIN login_client 
WITH PASSWORD = 'amoleer2026',
CHECK_POLICY = ON;

-- Login para los autores
CREATE LOGIN login_author 
WITH PASSWORD ='amoescribir2024', 
CHECK_POLICY = ON;

---------------------------------------------------------------------
-- 5. CREACIÓN DE USERS (NIVEL BASE DE DATOS)
---------------------------------------------------------------------

/*
    Los USERS se crean dentro de la base de datos y se vinculan
    a un LOGIN previamente creado.
    LOGIN = Acceso al servidor
    USER  = Acceso a la base de datos específica
*/

-- Usuario dentro de BibliotecaBD para el Director
CREATE USER usr_dirBiblioteca 
FOR LOGIN login_dirBiblioteca;

-- Usuario dentro de BibliotecaBD para el Cliente
CREATE USER usr_client 
FOR LOGIN login_client;

-- Usuario dentro de BibliotecaBD para el Autor
CREATE USER usr_author 
FOR LOGIN login_author;

---------------------------------------------------------------------
-- 6. CREACIÓN DE ROLES PERSONALIZADOS
---------------------------------------------------------------------

/*
    Los ROLES permiten agrupar permisos.
    En lugar de asignar permisos directamente a cada usuario,
    se asignan a un rol y luego se agregan los usuarios a ese rol.
    Esto facilita la administración y mejora la seguridad.
*/

-- Rol con permisos de lectura sobre libros
CREATE ROLE rol_lectura_books;

-- Rol con permisos para ejecutar procesos de préstamo
CREATE ROLE rol_ejecuta_lend;

-- Rol con permisos de director (posible control total o administrativo)
CREATE ROLE rol_director;

-- Rol encargado de administrar préstamos
CREATE ROLE rol_admin_lends;

---------------------------------------------------------------------
-- 7. ASIGNACIÓN DE PERMISOS A ROLES
---------------------------------------------------------------------

/*
    Se asignan permisos específicos a cada rol según su función:
    - rol_lectura_books: Solo lectura de libros y consultas básicas
    - rol_ejecuta_lend: Puede ejecutar procesos de préstamo
    - rol_director: Control total sobre todas las tablas
    - rol_admin_lends: Administración completa de préstamos
*/

-- Permisos para rol_lectura_books (Clientes)
GRANT SELECT ON dbo.Books TO rol_lectura_books;
GRANT SELECT ON dbo.Authors TO rol_lectura_books;
GRANT SELECT ON dbo.Categories TO rol_lectura_books;
GRANT SELECT ON dbo.BookAuthors TO rol_lectura_books;
GRANT SELECT ON dbo.Users TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetBooks TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetAuthors TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetCategories TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetUsers TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_SearchBooks TO rol_lectura_books;
GRANT EXECUTE ON dbo.SP_GetBookById TO rol_lectura_books;

-- Permisos para rol_ejecuta_lend (Clientes - préstamos)
GRANT SELECT ON dbo.Loans TO rol_ejecuta_lend;
GRANT INSERT ON dbo.Loans TO rol_ejecuta_lend;
GRANT UPDATE ON dbo.Books TO rol_ejecuta_lend;
GRANT EXECUTE ON dbo.SP_InsertLoan TO rol_ejecuta_lend;
GRANT EXECUTE ON dbo.SP_GetLoansByUser TO rol_ejecuta_lend;
GRANT EXECUTE ON dbo.SP_ReturnBook TO rol_ejecuta_lend;

-- Permisos para rol_admin_lends (Administradores - gestión de préstamos)
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

-- Permisos para rol_director (Control total)
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Books TO rol_director;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Authors TO rol_director;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Categories TO rol_director;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Users TO rol_director;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Loans TO rol_director;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.BookAuthors TO rol_director;

-- Todos los permisos de ejecución para rol_director
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
-- Grants directos a login_dirBiblioteca para asegurar ejecución en el entorno actual
GRANT EXECUTE ON dbo.SP_GetUsers TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_GetAuthors TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_GetCategories TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_GetBooks TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_SearchBooks TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_GetBookById TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_InsertLoan TO usr_dirBiblioteca;

---------------------------------------------------------------------
-- 8. ASIGNACIÓN DE USUARIOS A ROLES
---------------------------------------------------------------------

/*
    Se asignan los usuarios creados a sus respectivos roles.
    Cada usuario tendrá los permisos correspondientes a su rol.
*/

-- Asignar usuarios a roles
ALTER ROLE rol_lectura_books ADD MEMBER usr_client;
ALTER ROLE rol_ejecuta_lend ADD MEMBER usr_client;

ALTER ROLE rol_admin_lends ADD MEMBER usr_dirBiblioteca;
ALTER ROLE rol_director ADD MEMBER usr_dirBiblioteca;

-- Permisos directos para el usuario de base de datos del director
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Books TO usr_dirBiblioteca;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Authors TO usr_dirBiblioteca;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Categories TO usr_dirBiblioteca;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.BookAuthors TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_InsertBook TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_InsertAuthor TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_InsertCategory TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_InsertBookAuthor TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_GetUsers TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_GetAuthors TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_GetCategories TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_GetBooks TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_SearchBooks TO usr_dirBiblioteca;
GRANT EXECUTE ON dbo.SP_GetBookById TO usr_dirBiblioteca;

-- El usuario de autor por ahora no tiene permisos específicos asignados
-- ALTER ROLE rol_autor ADD MEMBER usr_author;

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

/*
    Esta tabla almacena la información de los usuarios
    registrados en el sistema (clientes, administradores, etc.).
*/

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

/*
    Esta tabla almacena las categorías o géneros
    de los libros disponibles en la biblioteca.
*/

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

/*
    Esta tabla almacena la información de los libros.
    Se relaciona con la tabla Categories mediante
    una clave foránea.
*/

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
        REFERENCES dbo.Categories(IDCategoria)
        -- Relación entre Books y Categories.
);
GO

---------------------------------------------------------
-- 4. TABLA AUTHORS
---------------------------------------------------------

/*
    Esta tabla almacena la información de los autores
    de los libros.
*/

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

/*
    Esta tabla registra los préstamos de libros.
    Se relaciona con Users y Books.
*/

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
        -- Estado del préstamo (Activo, Devuelto, Atrasado, etc.).

    CONSTRAINT PK_IDLoan PRIMARY KEY(IDLoan),

    CONSTRAINT FK_IDUsuario 
        FOREIGN KEY(IDUsuario) 
        REFERENCES dbo.Users(IDUsuario),
        -- Relación entre Loans y Users.

    CONSTRAINT FK_IDLibro 
        FOREIGN KEY(IDLibro) 
        REFERENCES dbo.Books(IDLibro)
        -- Relación entre Loans y Books.
);
GO

---------------------------------------------------------
-- 6. TABLA BookAuthors (RELACIÓN MUCHOS A MUCHOS)
---------------------------------------------------------

/*
    Esta tabla intermedia permite establecer una relación
    muchos a muchos entre Books y Authors.

    Un libro puede tener varios autores.
    Un autor puede haber escrito varios libros.
*/

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

/*
    En esta sección se crean los procedimientos almacenados (Stored Procedures)
    del sistema BibliotecaBD.

    Los procedimientos almacenados permiten:
*/


/* ============================================================
   TABLA: USERS
   ============================================================ */

-- SP_InsertUser
/*
    Inserta un nuevo usuario en la tabla Users.
*/
CREATE PROCEDURE dbo.SP_InsertUser
    @NombreUsuario NVARCHAR(50),
    @ApellidoUsuario NVARCHAR(50),
    @EmailUsuario NVARCHAR(100),
    @TipoUsuario NVARCHAR(30),
    @EstadoUsuario NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;  -- Evita mensajes de filas afectadas (mejora rendimiento)

    INSERT INTO dbo.Users
    (NombreUsuario, ApellidoUsuario, EmailUsuario, TipoUsuario, EstadoUsuario)
    VALUES
    (@NombreUsuario, @ApellidoUsuario, @EmailUsuario, @TipoUsuario, @EstadoUsuario);
END
GO

-- SP_UpdateUser
/*
    Actualiza los datos de un usuario existente
    según su IDUsuario.
*/
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
/*
    Elimina un usuario por su ID.
*/
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
/*
    Retorna todos los usuarios registrados.
*/
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
/*
    Inserta un nuevo autor en la tabla Authors.
*/
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
/*
    Actualiza la información de un autor.
*/
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
/*
    Elimina un autor por su ID.
*/
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
/*
    Retorna todos los autores registrados.
*/
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

-- SP_UpdateCategory
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

-- SP_DeleteCategory
CREATE PROCEDURE dbo.SP_DeleteCategory
    @IDCategoria INT
AS
BEGIN
    SET NOCOUNT ON;

    -- Verificar que no tenga libros asociados
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

-- SP_InsertBook
-- SP_InsertBook
/*
    Inserta un nuevo libro.
    La CantidadDisponible se inicializa igual a CantidadTotal.
*/
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
/*
    Actualiza la información de un libro.
*/
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
/*
    Procedimiento: SP_DeleteBook
    Descripción:
        Elimina un libro de la tabla Books según su ID.

    Parámetros:
        @IDLibro -> Identificador del libro a eliminar.
*/
CREATE PROCEDURE dbo.SP_DeleteBook
    @IDLibro INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY

        -- 1️ Verificar que el libro exista
        IF NOT EXISTS (SELECT 1 FROM dbo.Books WHERE IDLibro = @IDLibro)
        BEGIN
            RAISERROR('El libro no existe.', 16, 1);
            RETURN;
        END

        -- 2️ Verificar que no tenga préstamos asociados
        IF EXISTS (SELECT 1 FROM dbo.Loans WHERE IDLibro = @IDLibro)
        BEGIN
            RAISERROR('No se puede eliminar el libro porque tiene préstamos asociados.', 16, 1);
            RETURN;
        END

        -- 3️ Eliminar relaciones en BookAuthors 
        DELETE FROM dbo.BookAuthors
        WHERE IDLibros = @IDLibro;

        -- 4 Eliminar libro
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

-- SP_GetBooks
/*
    Procedimiento: SP_GetBooks
    Descripción:
        Devuelve la lista de libros junto con el nombre
        de su categoría correspondiente.

    Funcionamiento:
        Realiza un INNER JOIN entre Books y Categories
        para mostrar información más completa.
*/
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

-- SP_GetBookById
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

-- SP_SearchBooks
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
GO


/* ============================================================
   TABLA: LOANS
   ============================================================ */

-- SP_InsertLoan
/*
    Procedimiento: SP_InsertLoan
    Descripción:
        Registra un nuevo préstamo si existen ejemplares disponibles.

    Lógica:
        1. Verifica que el libro tenga CantidadDisponible > 0.
        2. Inserta el préstamo con estado 'Prestado'.
        3. Reduce en 1 la cantidad disponible del libro.
        4. Si no hay disponibilidad, genera un error.

    Este procedimiento implementa la lógica central
    del sistema de préstamos.
*/
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
/*
    Procedimiento: SP_ReturnLoan
    Descripción:
        Registra la devolución de un libro prestado.

    Lógica:
        1. Obtiene el ID del libro asociado al préstamo.
        2. Actualiza la fecha de devolución real.
        3. Cambia el estado a 'Devuelto'.
        4. Incrementa la cantidad disponible del libro.
*/
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
/*
    Procedimiento: SP_GetAllLoans
    Descripción:
        Devuelve el listado completo de préstamos.

    Funcionamiento:
        Une Loans, Users y Books para mostrar:
        - Usuario (nombre completo)
        - Libro
        - Fechas
        - Estado
*/
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

-- SP_UpdateLoan
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

-- SP_GetLoans (alias para SP_GetAllLoans)
CREATE PROCEDURE dbo.SP_GetLoans
AS
BEGIN
    EXEC dbo.SP_GetAllLoans;
END
GO

-- SP_GetLoansByUser
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

-- SP_ReturnBook (alias para SP_ReturnLoan)
CREATE PROCEDURE dbo.SP_ReturnBook
    @IDLoan INT,
    @FechaDevolucionReal DATE
AS
BEGIN
    EXEC dbo.SP_ReturnLoan @IDLoan, @FechaDevolucionReal;
END
GO
-- SP_DeleteLoan
/*
    Procedimiento: SP_DeleteLoan
    Descripción:
        Elimina un préstamo del sistema.

    Lógica:
        1. Obtiene el ID del libro y el estado del préstamo.
        2. Si el préstamo estaba activo ('Prestado'),
           se incrementa la cantidad disponible.
        3. Elimina el registro del préstamo.

    Esto evita inconsistencias en el inventario.
*/
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
/*
    Procedimiento: SP_GetActiveLoans
    Descripción:
        Devuelve únicamente los préstamos activos
        (Estado = 'Prestado').

    Utilidad:
        Permite consultar libros que aún no han sido devueltos.
*/
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
/*
    Procedimiento: SP_InsertBookAuthor
    Descripción:
        Asocia un libro con un autor.
        Representa la relación muchos a muchos.
*/
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
/*
    Procedimiento: SP_DeleteBookAuthor
    Descripción:
        Elimina la relación entre un libro y un autor.
*/
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
/*
    Procedimiento: SP_GetBookAuthors
    Descripción:
        Devuelve la relación completa entre libros y autores,
        mostrando información detallada de ambos.
*/
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
-- Asumimos:
-- Libro 1 -> Autor 1
-- Libro 2 -> Autor 2
-- Libro 3 -> Autor 3

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

/* =========================================================
   TRIGGER 1
   Nombre: TR_ValidarStockAntesDePrestamo
   Tipo: INSTEAD OF INSERT
   Tabla: Loans

   Descripción:
   - Evita que se registre un préstamo si el libro no tiene stock disponible.
   - Si el stock es válido:
        1) Inserta el préstamo.
        2) Reduce automáticamente la CantidadDisponible del libro.
   ========================================================= */

CREATE OR ALTER TRIGGER TR_ValidarStockAntesDePrestamo
ON dbo.Loans
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Validar que el libro tenga stock disponible
    IF EXISTS (
        SELECT 1
        FROM inserted I
        INNER JOIN dbo.Books B ON I.IDLibro = B.IDLibro
        WHERE B.CantidadDisponible <= 0
    )
    BEGIN
        RAISERROR('No hay ejemplares disponibles para este libro.',16,1);
        RETURN;
    END

    -- Insertar el préstamo si pasa la validación
    INSERT INTO dbo.Loans (IDUsuario, IDLibro, FechaPrestamo, FechaDevolucion, FechaDevolucionReal, Estado)
    SELECT IDUsuario, IDLibro, FechaPrestamo, FechaDevolucion, FechaDevolucionReal, Estado
    FROM inserted;

    -- Reducir el stock disponible del libro
    UPDATE B
    SET CantidadDisponible = CantidadDisponible - 1
    FROM dbo.Books B
    INNER JOIN inserted I ON B.IDLibro = I.IDLibro;

END;
GO


/* =========================================================
   TRIGGER 2
   Nombre: TR_DevolucionLibro
   Tipo: AFTER UPDATE
   Tabla: Loans

   Descripción:
   - Cuando se registra una devolución (FechaDevolucionReal pasa
     de NULL a una fecha válida):
        1) Aumenta automáticamente la CantidadDisponible del libro.
   - Evita duplicar el incremento si ya estaba devuelto.
   ========================================================= */

CREATE OR ALTER TRIGGER TR_DevolucionLibro
ON dbo.Loans
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF UPDATE(FechaDevolucionReal)
    BEGIN
        UPDATE B
        SET CantidadDisponible = CantidadDisponible + 1
        FROM dbo.Books B
        INNER JOIN inserted I ON B.IDLibro = I.IDLibro
        INNER JOIN deleted D ON I.IDLoan = D.IDLoan
        WHERE D.FechaDevolucionReal IS NULL
          AND I.FechaDevolucionReal IS NOT NULL;
    END
END;
GO


/* =========================================================
   TRIGGER 3
   Nombre: TR_ControlStock
   Tipo: AFTER UPDATE
   Tabla: Books

   Descripción:
   - Garantiza integridad lógica del inventario.
   - Impide que:
        1) CantidadDisponible sea negativa.
        2) CantidadDisponible sea mayor que CantidadTotal.
   - Si detecta inconsistencia, revierte la transacción.
   ========================================================= */

CREATE OR ALTER TRIGGER TR_ControlStock
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

-------------------------------
-----Creación de los index-----
-------------------------------
--  BOOKS
CREATE INDEX idx_books_categoria 
ON dbo.Books (IDCategoria);
CREATE INDEX idx_books_titulo 
ON dbo.Books (TituloLibro);
-- USERS
CREATE INDEX idx_users_email 
ON dbo.Users (EmailUsuario);
-- LOANS
CREATE INDEX idx_loans_usuario 
ON dbo.Loans (IDUsuario);
CREATE INDEX idx_loans_libro 
ON dbo.Loans (IDLibro);
CREATE INDEX idx_loans_estado 
ON dbo.Loans (Estado);
CREATE INDEX idx_loans_fecha_devolucion 
ON dbo.Loans (FechaDevolucion);
CREATE INDEX idx_loans_estado_fecha 
ON dbo.Loans (Estado, FechaDevolucion);
-- AUTHORS
CREATE INDEX idx_authors_nombre 
ON dbo.Authors (NombreAutor);
-- CATEGORIES
CREATE INDEX idx_categories_nombre 
ON dbo.Categories (NombreCategoria);

--Justificación de los índices
--idx_books_categoria: Optimiza las consultas que relacionan libros con sus categorías mediante JOIN.
--idx_books_titulo: Mejora la velocidad de búsqueda de libros por título.
--idx_users_email: Acelera la autenticación o búsqueda de usuarios por correo electrónico.
--idx_loans_usuario: Permite obtener rápidamente los préstamos asociados a un usuario.
--idx_loans_libro: Facilita la consulta de préstamos relacionados con un libro específico.
--idx_loans_estado: Mejora el filtrado por estado del préstamo (por ejemplo, “Prestado”).
--idx_loans_fecha_devolucion: Optimiza consultas que dependen de fechas (como préstamos vencidos).
--idx_loans_estado_fecha: Índice compuesto que mejora significativamente consultas que combinan estado y fecha, especialmente para detectar préstamos vencidos.
--idx_authors_nombre: Permite búsquedas rápidas de autores por nombre.
--idx_categories_nombre: Mejora la consulta de categorías por nombre.


--------------------------------
-----Creacion de las vistas-----
--------------------------------

-- Vista de libros con categoría
CREATE VIEW vw_BooksFull AS
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
-- Vista de préstamos activos
CREATE VIEW vw_ActiveLoans AS
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
-- Vista de préstamos vencidos
CREATE VIEW vw_OverdueLoans AS
SELECT *
FROM vw_ActiveLoans
WHERE FechaDevolucion < GETDATE();
--  Vista de estadísticas de préstamos por autor
CREATE VIEW vw_AuthorLoanStats AS
SELECT 
    A.NombreAutor,
    COUNT(*) AS TotalPrestamos,
    FORMAT(L.FechaPrestamo, 'yyyy-MM') AS Periodo
FROM Loans L
JOIN Books B ON L.IDLibro = B.IDLibro
JOIN dbo.BookAuthors BA ON B.IDLibro = BA.IDLibros
JOIN dbo.Authors A ON BA.IDAutores = A.IDAutor
GROUP BY A.NombreAutor, FORMAT(L.FechaPrestamo, 'yyyy-MM');
 
--Justificación de las vistas
--vw_BooksFull: Centraliza la información de libros junto con su categoría, evitando repetir JOINs en múltiples consultas.
--vw_ActiveLoans: Facilita la obtención de préstamos activos, simplificando consultas frecuentes del sistema.
--vw_OverdueLoans: Permite identificar rápidamente los préstamos vencidos sin necesidad de lógica adicional en cada consulta.
--vw_AuthorLoanStats: Proporciona una base para análisis estadísticos de préstamos por autor y periodo, útil para reportes.








