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