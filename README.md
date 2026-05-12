# Sistema de Gestión de Biblioteca Virtual

Proyecto desarrollado para el curso **Base de Datos II** de la **Universidad Latina de Costa Rica**.

Este sistema implementa una base de datos relacional en **SQL Server** para la administración de una biblioteca virtual, incluyendo gestión de usuarios, libros, autores, categorías y préstamos. Además, se integra con una aplicación en **Python** y un módulo conversacional con **Ollama** para consultas en lenguaje natural.

---

## Integrantes

- Christopher Phillips
- Juan Gabriel Sandí
- Santiago Villalta Montero
- Val Sancho Vega

**Docente:** Marlon Esteban Obando Cordero

---

## Descripción del proyecto

El objetivo del proyecto es construir una solución completa para la gestión de una biblioteca, utilizando una base de datos en SQL Server con:

- Tablas relacionadas y normalizadas
- Procedimientos almacenados
- Triggers
- Vistas
- Índices
- Seguridad por usuarios, roles y permisos
- Integración con Python
- Asistente inteligente con Ollama

La solución permite registrar usuarios, libros, autores, categorías y préstamos, así como consultar información de forma estructurada y, en etapas más avanzadas, mediante lenguaje natural.

---

## Tecnologías utilizadas

### Base de datos
- Microsoft SQL Server
- Transact-SQL (T-SQL)

### Aplicación
- Python
- pyodbc
- CustomTkinter

### Inteligencia artificial
- Ollama
- Modelo local `llama3.2:3b`

---

## Estructura general del sistema

El proyecto está compuesto por dos grandes partes:

### 1. Base de datos SQL Server
La base de datos **BibliotecaBD** contiene toda la lógica estructural y de negocio del sistema.

### 2. Aplicación en Python
La aplicación se conecta a SQL Server para ejecutar procedimientos almacenados y mostrar resultados en una interfaz gráfica, además de integrar un chatbot conversacional con Ollama.

---

## Modelo de datos

La base de datos se compone de las siguientes tablas principales:

- **Users**: registra los usuarios del sistema
- **Categories**: almacena las categorías de libros
- **Books**: contiene los libros disponibles
- **Authors**: almacena los autores
- **Loans**: registra los préstamos y devoluciones
- **BookAuthors**: resuelve la relación muchos a muchos entre libros y autores

### Relaciones principales
- Una categoría puede tener muchos libros
- Un usuario puede tener muchos préstamos
- Un libro puede aparecer en muchos préstamos
- Un libro puede tener varios autores y un autor puede tener varios libros

---

## Funcionalidades implementadas

### Gestión de datos
- Registro de usuarios
- Registro de autores
- Registro de categorías
- Registro de libros
- Asociación entre libros y autores
- Registro de préstamos
- Registro de devoluciones

### Consultas
- Listado de usuarios
- Listado de libros
- Búsqueda de libros por título
- Búsqueda de libros por autor
- Búsqueda por año o rango de años
- Búsqueda por género o categoría
- Préstamos activos
- Préstamos vencidos
- Historial de préstamos por usuario
- Estadísticas de categorías
- Autores con más préstamos

---

## Procedimientos almacenados

El sistema implementa procedimientos almacenados para mantenimiento y consulta, entre ellos:

### Usuarios
- `SP_InsertUser`
- `SP_UpdateUser`
- `SP_DeleteUser`
- `SP_GetUsers`

### Autores
- `SP_InsertAuthor`
- `SP_UpdateAuthor`
- `SP_DeleteAuthor`
- `SP_GetAuthors`

### Categorías
- `SP_InsertCategory`
- `SP_UpdateCategory`
- `SP_DeleteCategory`
- `SP_GetCategories`

### Libros
- `SP_InsertBook`
- `SP_UpdateBook`
- `SP_DeleteBook`
- `SP_GetBooks`
- `SP_GetBookById`
- `SP_SearchBooks`

### Préstamos
- `SP_InsertLoan`
- `SP_ReturnLoan`
- `SP_ReturnBook`
- `SP_UpdateLoan`
- `SP_DeleteLoan`
- `SP_GetLoans`
- `SP_GetAllLoans`
- `SP_GetLoansByUser`
- `SP_GetActiveLoans`
- `SP_OverdueLoans`

### Consultas avanzadas
- `SP_SearchBooksByAuthor`
- `SP_SearchBooksByYear`
- `SP_GetBooksByYearRange`
- `SP_SearchBooksByGenre`
- `SP_GetMostLoanedBooks`
- `SP_GetLeastLoanedBooks`
- `SP_GetLoanHistoryById`
- `SP_GetLoanHistoryByName`
- `SP_GetCategoryStats`
- `SP_CompareAuthors`
- `SP_CountBooksByCategory`
- `SP_TopAuthorsByLoans`

---

## Triggers implementados

### `TR_ValidarStockAntesDePrestamo`
Valida la disponibilidad de ejemplares antes de registrar un préstamo y descuenta automáticamente la cantidad disponible.

### `TR_DevolucionLibro`
Aumenta automáticamente la cantidad disponible cuando se registra una devolución real.

### `TR_ControlStock`
Impide que la cantidad disponible sea negativa o mayor que la cantidad total.

---

## Vistas implementadas

- `vw_BooksFull`
- `vw_ActiveLoans`
- `vw_OverdueLoans`
- `vw_AuthorLoanStats`

Estas vistas facilitan consultas frecuentes y mejoran la organización del acceso a datos.

---

## Índices implementados

Se agregaron índices para optimizar consultas frecuentes sobre:

- Categorías de libros
- Títulos de libros
- Email de usuarios
- Usuario en préstamos
- Libro en préstamos
- Estado de préstamos
- Fecha de devolución
- Estado + fecha
- Nombre de autor
- Nombre de categoría

---

## Seguridad

El sistema implementa seguridad a nivel de SQL Server mediante:

### Logins
- `login_dirBiblioteca`
- `login_client`
- `login_author`

### Users
- `usr_dirBiblioteca`
- `usr_client`
- `usr_author`

### Roles
- `rol_lectura_books`
- `rol_ejecuta_lend`
- `rol_director`
- `rol_admin_lends`

### Ejemplo de permisos
- Lectura de información bibliográfica
- Ejecución de procedimientos de préstamos
- Gestión administrativa de préstamos y usuarios
- Control total para dirección

---

## Aplicación en Python

La aplicación en Python se conecta con la base de datos y permite ejecutar consultas reales desde interfaz gráfica o consola.

### Archivos principales
- `db.py`: conexión a SQL Server mediante `pyodbc`
- `biblioteca_repo.py`: acceso a procedimientos almacenados
- `services.py`: capa de servicios y conexión con Ollama
- `ui_app.py`: interfaz gráfica con CustomTkinter
- `main.py`: prueba por consola

### Funcionalidades actuales
- Listado de usuarios desde la base de datos
- Interfaz gráfica con pestaña de usuarios
- Chat conversacional con Ollama
- Prueba básica por consola

---

## Asistente inteligente

El proyecto integra un asistente conversacional mediante **Ollama** y el modelo local `llama3.2:3b`.

Actualmente permite:
- conversación básica con IA
- integración desde la app Python
- base preparada para futuras consultas en lenguaje natural contra SQL Server

---

## Cómo ejecutar el proyecto

### 1. Ejecutar el script SQL
Abrir **SQL Server Management Studio (SSMS)** y ejecutar el script completo de creación de la base de datos.

### 2. Verificar la base de datos
Confirmar que se hayan creado correctamente:
- tablas
- procedimientos
- triggers
- vistas
- índices
- roles y permisos

### 3. Configurar Python
Instalar dependencias necesarias:

```bash
pip install pyodbc customtkinter ollama
