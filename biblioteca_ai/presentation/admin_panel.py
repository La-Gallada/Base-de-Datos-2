"""
Frame de Administración para agregar libros y autores.
Solo visible para administradores.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import date
import data.biblioteca_repo as biblioteca_repo
from business.services.biblioteca_service import (
    insert_book, insert_author, insert_category,
    get_category_id, get_author_id
)

# ─────────────────────────────────────────────
# TEMA Y COLORES
# ─────────────────────────────────────────────
COLOR_BG = "#0f1117"
COLOR_PANEL = "#1a1d27"
COLOR_CARD = "#22263a"
COLOR_ACCENT = "#4f8ef7"
COLOR_SUCCESS = "#22c55e"
COLOR_DANGER = "#ef4444"
COLOR_WARNING = "#f59e0b"
COLOR_TEXT = "#e2e8f0"
COLOR_MUTED = "#64748b"
COLOR_BORDER = "#2d3148"

FONT_HEADING = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 10)


class AdminPanel(ctk.CTkFrame):
    """
    Panel de administración para agregar libros y autores.
    Solo visible para usuarios con rol administrador.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, **kwargs)
        
        self.build_admin_ui()
    
    def build_admin_ui(self):
        """Construye la interfaz de administración."""
        
        # ── Tabbar para las diferentes secciones
        tabview = ctk.CTkTabview(
            self,
            fg_color=COLOR_PANEL,
            segmented_button_fg_color=COLOR_CARD,
            segmented_button_selected_color=COLOR_ACCENT,
            text_color=COLOR_TEXT
        )
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ── Tab: Agregar Libro
        add_book_tab = tabview.add(" Agregar Libro")
        self.build_add_book_section(add_book_tab)
        
        # ── Tab: Agregar Autor
        add_author_tab = tabview.add(" Agregar Autor")
        self.build_add_author_section(add_author_tab)
        
        # ── Tab: Gestionar Categorías
        manage_cat_tab = tabview.add(" Categorías")
        self.build_categories_section(manage_cat_tab)
    
    def build_add_book_section(self, parent):
        """Sección para agregar libros."""
        
        # Contenedor scrollable para que quepan todos los campos
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=20)
        
        # ── Título
        title = ctk.CTkLabel(
            frame,
            text=" Agregar Nuevo Libro",
            font=FONT_HEADING,
            text_color=COLOR_ACCENT
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # ── Campo: Título
        ctk.CTkLabel(frame, text="Título del libro", font=FONT_BODY).pack(anchor="w", pady=(10, 5))
        titulo_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Ej: Fundación",
            fg_color=COLOR_CARD,
            border_color=COLOR_ACCENT
        )
        titulo_entry.pack(fill="x", pady=(0, 15))
        
        # ── Campo: ISBN
        ctk.CTkLabel(frame, text="ISBN", font=FONT_BODY).pack(anchor="w", pady=(10, 5))
        isbn_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Ej: 978-0-553-29438-0",
            fg_color=COLOR_CARD,
            border_color=COLOR_ACCENT
        )
        isbn_entry.pack(fill="x", pady=(0, 15))
        
        # ── Campo: Año de publicación
        ctk.CTkLabel(frame, text="Año de publicación", font=FONT_BODY).pack(anchor="w", pady=(10, 5))
        year_entry = ctk.CTkEntry(
            frame,
            placeholder_text=f"Ej: {date.today().year}",
            fg_color=COLOR_CARD,
            border_color=COLOR_ACCENT
        )
        year_entry.pack(fill="x", pady=(0, 15))
        
        # ── Campo: Autor
        ctk.CTkLabel(frame, text="Autor", font=FONT_BODY).pack(anchor="w", pady=(10, 5))
        authors = self.get_authors_list()
        author_combo = ctk.CTkComboBox(
            frame,
            values=authors,
            fg_color=COLOR_CARD,
            border_color=COLOR_ACCENT,
            state="readonly"
        )
        author_combo.pack(fill="x", pady=(0, 15))
        if authors:
            author_combo.set(authors[0])
        
        # ── Campo: Categoría
        ctk.CTkLabel(frame, text="Categoría", font=FONT_BODY).pack(anchor="w", pady=(10, 5))
        categories = self.get_categories_list()
        category_combo = ctk.CTkComboBox(
            frame,
            values=categories,
            fg_color=COLOR_CARD,
            border_color=COLOR_ACCENT,
            state="readonly"
        )
        category_combo.pack(fill="x", pady=(0, 15))
        if categories:
            category_combo.set(categories[0])
        
        # ── Campo: Cantidad total
        ctk.CTkLabel(frame, text="Cantidad de ejemplares", font=FONT_BODY).pack(anchor="w", pady=(10, 5))
        cantidad_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Ej: 5",
            fg_color=COLOR_CARD,
            border_color=COLOR_ACCENT
        )
        cantidad_entry.pack(fill="x", pady=(0, 20))
        
        # ── Botón: Agregar
        def add_book():
            titulo = titulo_entry.get().strip()
            isbn = isbn_entry.get().strip()
            year = year_entry.get().strip()
            autor = author_combo.get()
            categoria = category_combo.get()
            cantidad = cantidad_entry.get().strip()
            
            if not all([titulo, isbn, year, autor, categoria, cantidad]):
                messagebox.showerror("Error", "Por favor completa todos los campos.")
                return
            
            try:
                cantidad_int = int(cantidad)
                year_int = int(year)
                
                if cantidad_int <= 0 or year_int < 1000:
                    raise ValueError("Valores inválidos")
                
                # Insertar libro usando la función del servicio
                id_libro = insert_book(
                    titulo=titulo,
                    isbn=isbn,
                    year=year_int,
                    categoria=categoria,
                    cantidad=cantidad_int,
                    autores=[autor],  # Lista con un autor por ahora
                    user_role="Administrador"  # Asumiendo que el admin panel solo es accesible por administradores
                )
                
                if id_libro:
                    messagebox.showinfo(
                        "Éxito",
                        f"✅ Libro '{titulo}' agregado exitosamente.\n\n"
                        f"ISBN: {isbn}\nAño: {year}\nAutor: {autor}\n"
                        f"Categoría: {categoria}\nCantidad: {cantidad}"
                    )
                    
                    # Limpiar campos
                    titulo_entry.delete(0, "end")
                    isbn_entry.delete(0, "end")
                    year_entry.delete(0, "end")
                    cantidad_entry.delete(0, "end")
                else:
                    messagebox.showerror("Error", "No se pudo insertar el libro en la BD.")
                
            except ValueError as ve:
                messagebox.showerror("Error", f"Cantidad y año deben ser números válidos. {str(ve)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar libro: {str(e)}")
        
        add_btn = ctk.CTkButton(
            frame,
            text="✅ Agregar Libro",
            font=FONT_BODY,
            fg_color=COLOR_SUCCESS,
            hover_color="#1ade3a",
            command=add_book
        )
        add_btn.pack(fill="x", pady=(20, 0))
    
    def build_add_author_section(self, parent):
        """Sección para agregar autores."""
        
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=20)
        
        # ── Título
        title = ctk.CTkLabel(
            frame,
            text=" Agregar Nuevo Autor",
            font=FONT_HEADING,
            text_color=COLOR_ACCENT
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # ── Campo: Nombre
        ctk.CTkLabel(frame, text="Nombre del autor", font=FONT_BODY).pack(anchor="w", pady=(10, 5))
        nombre_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Ej: Isaac Asimov",
            fg_color=COLOR_CARD,
            border_color=COLOR_ACCENT
        )
        nombre_entry.pack(fill="x", pady=(0, 15))
        
        # ── Campo: Nacionalidad
        ctk.CTkLabel(frame, text="Nacionalidad", font=FONT_BODY).pack(anchor="w", pady=(10, 5))
        nacionalidad_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Ej: Ruso-Estadounidense",
            fg_color=COLOR_CARD,
            border_color=COLOR_ACCENT
        )
        nacionalidad_entry.pack(fill="x", pady=(0, 20))
        
        # ── Botón: Agregar
        def add_author():
            nombre = nombre_entry.get().strip()
            nacionalidad = nacionalidad_entry.get().strip()
            
            if not nombre or not nacionalidad:
                messagebox.showerror("Error", "Por favor completa todos los campos.")
                return
            
            try:
                # Insertar autor en BD usando la función del servicio
                id_autor = insert_author(
                    nombre=nombre,
                    nacionalidad=nacionalidad,
                    user_role="Administrador"
                )
                
                if id_autor:
                    messagebox.showinfo(
                        "Éxito",
                        f"✅ Autor '{nombre}' agregado exitosamente.\n\n"
                        f"Nacionalidad: {nacionalidad}\nID: {id_autor}"
                    )
                    
                    # Limpiar campos
                    nombre_entry.delete(0, "end")
                    nacionalidad_entry.delete(0, "end")
                else:
                    messagebox.showerror("Error", "No se pudo insertar el autor en la BD.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar autor: {str(e)}")
        
        add_btn = ctk.CTkButton(
            frame,
            text="✅ Agregar Autor",
            font=FONT_BODY,
            fg_color=COLOR_SUCCESS,
            hover_color="#1ade3a",
            command=add_author
        )
        add_btn.pack(fill="x", pady=(20, 0))
    
    def build_categories_section(self, parent):
        """Sección para gestionar categorías."""
        
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=20)
        
        # ── Título
        title = ctk.CTkLabel(
            frame,
            text=" Gestionar Categorías",
            font=FONT_HEADING,
            text_color=COLOR_ACCENT
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # ── Lista de categorías
        categories = self.get_categories_list()
        
        if categories:
            cat_frame = ctk.CTkFrame(frame, fg_color=COLOR_CARD)
            cat_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            label = ctk.CTkLabel(
                cat_frame,
                text="Categorías actuales:",
                font=FONT_BODY,
                text_color=COLOR_TEXT
            )
            label.pack(anchor="w", padx=10, pady=(10, 10))
            
            for i, cat in enumerate(categories, 1):
                cat_label = ctk.CTkLabel(
                    cat_frame,
                    text=f"• {cat}",
                    font=FONT_SMALL,
                    text_color=COLOR_TEXT
                )
                cat_label.pack(anchor="w", padx=20, pady=2)
        
        # ── Agregar categoría
        ctk.CTkLabel(frame, text="Nueva categoría", font=FONT_BODY).pack(anchor="w", pady=(20, 5))
        cat_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Ej: Ciencia Ficción",
            fg_color=COLOR_CARD,
            border_color=COLOR_ACCENT
        )
        cat_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(frame, text="Descripción", font=FONT_BODY).pack(anchor="w", pady=(10, 5))
        desc_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Descripción de la categoría",
            fg_color=COLOR_CARD,
            border_color=COLOR_ACCENT
        )
        desc_entry.pack(fill="x", pady=(0, 20))
        
        def add_category():
            nombre = cat_entry.get().strip()
            descripcion = desc_entry.get().strip()
            
            if not nombre or not descripcion:
                messagebox.showerror("Error", "Por favor completa todos los campos.")
                return
            
            try:
                # Insertar categoría en BD usando la función del servicio
                id_categoria = insert_category(
                    nombre=nombre,
                    descripcion=descripcion,
                    user_role="Administrador"
                )
                
                if id_categoria:
                    messagebox.showinfo(
                        "Éxito",
                        f"✅ Categoría '{nombre}' agregada exitosamente.\n\nID: {id_categoria}"
                    )
                    
                    cat_entry.delete(0, "end")
                    desc_entry.delete(0, "end")
                    
                    # Recargar la sección para mostrar las categorías actualizadas
                    # (opcional: implementar refresh de la lista)
                else:
                    messagebox.showerror("Error", "No se pudo insertar la categoría en la BD.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar categoría: {str(e)}")
        
        add_btn = ctk.CTkButton(
            frame,
            text="✅ Agregar Categoría",
            font=FONT_BODY,
            fg_color=COLOR_SUCCESS,
            hover_color="#1ade3a",
            command=add_category
        )
        add_btn.pack(fill="x")
    
    def get_categories_list(self) -> list:
        """Obtiene la lista de categorías desde BD."""
        try:
            rows = biblioteca_repo.sp_get_categories(user_role="Administrador")
            return [row[1] for row in rows]  # row[1] es el nombre
        except Exception as e:
            print(f"Error al cargar categorías: {e}")
            return []
    
    def get_authors_list(self) -> list:
        """Obtiene la lista de autores desde BD."""
        try:
            rows = biblioteca_repo.sp_get_authors(user_role="Administrador")
            return [row[1] for row in rows]  # row[1] es el nombre
        except Exception as e:
            print(f"Error al cargar autores: {e}")
            return []
