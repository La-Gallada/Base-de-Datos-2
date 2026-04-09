# Datos de Prueba - Admin Panel

## Instrucciones

Para probar la funcionalidad del Admin Panel:

1. **Inicia la aplicación**: `python main.py`
2. **Login con administrador**: 
   - Email: `mario@gmail.com`
   - Contraseña: (verifica en BD o login_app.py)
3. **Presiona el tab "Admin Panel"**
4. **Prueba cada formulario** con los datos de abajo

---

## Test 1: Agregar un Nuevo Autor

**Pestaña**: ✍️ Agregar Autor

| Campo | Valor |
|-------|-------|
| Nombre del autor | David Goggins |
| Nacionalidad | Estadounidense |

**Resultado esperado**: 
- ✅ Mensaje de éxito con ID asignado
- El autor debe aparecer en el combobox "Autor" de la pestaña de libros

---

## Test 2: Agregar una Nueva Categoría

**Pestaña**: 📂 Categorías

| Campo | Valor |
|-------|-------|
| Nueva categoría | Memorias y Autobiografías |
| Descripción | Historias de vida y autobiografías inspiradoras |

**Resultado esperado**:
- ✅ Mensaje de éxito con ID asignado
- La categoría debe aparecer en la lista de "Categorías actuales"
- Debe estar disponible en el combobox de libros

---

## Test 3: Agregar un Libro Completo

**Pestaña**: 📖 Agregar Libro

| Campo | Valor |
|-------|-------|
| Título del libro | Can't Hurt Me |
| ISBN | 978-1544512280 |
| Año de publicación | 2018 |
| Autor | David Goggins |
| Categoría | Memorias y Autobiografías |
| Cantidad de ejemplares | 3 |

**Resultado esperado**:
- ✅ Mensaje de éxito con todos los datos
- ID del libro asignado
- En la BD:
  - Fila nueva en tabla `Books`
  - Fila nueva en tabla `BookAuthors` (relación)

---

## Test 4: Validaciones

Prueba que las validaciones funcionen:

### 4a. Campo vacío
- Intenta agregar un libro sin completar todos los campos
- **Esperado**: ❌ Mensaje "Por favor completa todos los campos"

### 4b. Valor inválido
- Año de publicación: "abc"
- Cantidad: "-5"
- **Esperado**: ❌ Mensaje "Cantidad y año deben ser números válidos"

### 4c. Categoría no existe
- Selecciona una categoría válida pero elimínala manualmente de BD antes de insertar
- **Esperado**: ❌ Mensaje "Categoría no encontrada en BD"

---

## Test 5: Verificación en SQL

Después de realizar las inserciones, verifica en SQL Server:

```sql
-- Ver nuevos autores
SELECT IDAutor, NombreAutor, Nacionalidad 
FROM Authors 
WHERE NombreAutor LIKE '%Goggins%'

-- Ver nuevas categorías
SELECT IDCategoria, NombreCategoria, DescripcionCategoria 
FROM Categories 
WHERE NombreCategoria LIKE '%Memorias%'

-- Ver nuevos libros
SELECT IDLibro, TituloLibro, ISBN, AnioPublicacion, CantidadTotal 
FROM Books 
WHERE TituloLibro LIKE '%Can''t Hurt Me%'

-- Ver relaciones libro-autor
SELECT BA.IDLibros, BA.IDAutores, B.TituloLibro, A.NombreAutor
FROM BookAuthors BA
JOIN Books B ON BA.IDLibros = B.IDLibro
JOIN Authors A ON BA.IDAutores = A.IDAutor
WHERE B.TituloLibro LIKE '%Can''t Hurt Me%'
```

---

## Datos Adicionales para Pruebas Extensivas

### Más Libros de David Goggins
```
1. Título: Goggins: Living With a Seal | ISBN: 978-1250304766 | Año: 2017
2. Título: Never Finished | ISBN: 978-0306922282 | Año: 2023
```

### Autores Adicionales
```
1. Stephen King | Estadounidense
2. J.K. Rowling | Británica
3. Paulo Coelho | Brasileño
4. Agatha Christie | Británica
```

### Categorías Adicionales
```
1. Novela Negra | Historias de misterio y crimen
2. Fantasía | Mundos imaginarios y magia
3. Educación | Libros sobre aprendizaje y desarrollo
4. Filosofía | Pensamiento y reflexión
```

---

## Checklist de Funcionalidad

Marca con ✅ después de verificar cada punto:

### Inserción de Autores
- [ ] Se puede agregar nuevo autor sin errores
- [ ] Aparece en combobox de libros inmediatamente (F5 refresca)
- [ ] Los datos se guardan en BD correctamente

### Inserción de Categorías  
- [ ] Se puede agregar nueva categoría sin errores
- [ ] Aparece en lista de categorías actuales
- [ ] Disponible en combobox de libros

### Inserción de Libros
- [ ] Se puede agregar libro sin errores
- [ ] Se crea relación con autor en BookAuthors
- [ ] ISBN se valida como texto
- [ ] Año se valida como número >= 1000
- [ ] Cantidad se valida como número > 0
- [ ] CantidadDisponible = CantidadTotal al crear

### Validaciones
- [ ] No permite campos vacíos
- [ ] No permite números inválidos
- [ ] Verifica que autor exista
- [ ] Verifica que categoría exista
- [ ] Mensajes de error son descriptivos

### Interfaz
- [ ] Botones funcionan correctamente
- [ ] Campos se limpian después de inserción exitosa
- [ ] Mensajes son claros y útiles
- [ ] Colores y estilos se ven bien

---

## Solución de Problemas

**P**: ¿Por qué no aparece el nuevo autor en el combobox?
**R**: Actualiza/recarga la pestaña o reinicia la aplicación. Implementar refresh automático es mejora futura.

**P**: ¿Cuál es el formato correcto del ISBN?
**R**: Texto libre - puede ser con o sin guiones. Ej: "978-0-553-29438-0" o "9780553294380"

**P**: ¿Qué pasa si selecciono un autor pero cargo un libro con otro autor?
**R**: Está permitido tener mismo libro con múltiples autores - se crearía múltiples filas en BookAuthors

**P**: ¿Puedo agregar el mismo libro dos veces?
**R**: Sí (por ahora), pero es mejor hacer validación de ISBN único en mejoras futuras.

---

**Última actualización**: Implementación completada - Admin Panel fully functional
