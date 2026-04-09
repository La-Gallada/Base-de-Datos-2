"""
Frame de Login para la Biblioteca Inteligente.
Permite al usuario seleccionar su cuenta y acceder al sistema.
"""

import customtkinter as ctk
from tkinter import messagebox
from business.services.auth_service import get_users_for_login, get_users_error, validate_user, is_admin

# ─────────────────────────────────────────────
# TEMA Y COLORES
# ─────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_BG = "#0f1117"
COLOR_PANEL = "#1a1d27"
COLOR_CARD = "#22263a"
COLOR_ACCENT = "#4f8ef7"
COLOR_SUCCESS = "#22c55e"
COLOR_DANGER = "#ef4444"
COLOR_TEXT = "#e2e8f0"
COLOR_MUTED = "#64748b"

FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 10)


class LoginApp(ctk.CTkToplevel):
    """
    Ventana de login para seleccionar usuario y acceder al sistema.
    """

    def __init__(self, parent, on_login_callback):
        """
        Args:
            parent: Ventana padre
            on_login_callback: Función a llamar cuando se loguea:
                             on_login_callback(user_data, is_admin)
        """
        super().__init__(parent)
        self.title(" Biblioteca Inteligente - Login")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)
        
        # Centrar la ventana en la pantalla
        self.center_window()
        
        self.on_login_callback = on_login_callback
        self.selected_user = None
        
        # Cargar usuarios desde BD
        self.users = get_users_for_login()
        
        # ── Panel principal
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ── Logo/Título
        title = ctk.CTkLabel(
            main_frame,
            text=" BIBLIOTECA INTELIGENTE",
            font=FONT_TITLE,
            text_color=COLOR_ACCENT
        )
        title.pack(pady=(0, 10))
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Sistema de Gestión y Búsqueda de Libros",
            font=FONT_SMALL,
            text_color=COLOR_MUTED
        )
        subtitle.pack(pady=(0, 30))
        
        # ── Sección de selección de usuario
        user_label = ctk.CTkLabel(
            main_frame,
            text=" Selecciona tu usuario:",
            font=FONT_BODY,
            text_color=COLOR_TEXT
        )
        user_label.pack(anchor="w", pady=(20, 10))
        
        # ── Dropdown de usuarios
        if self.users:
            user_names = [f"{u['nombre']} ({u['tipo']})" for u in self.users]
            self.user_combo = ctk.CTkComboBox(
                main_frame,
                values=user_names,
                font=FONT_BODY,
                fg_color=COLOR_PANEL,
                text_color=COLOR_TEXT,
                dropdown_fg_color=COLOR_CARD,
                border_color=COLOR_ACCENT,
                state="readonly"
            )
            self.user_combo.pack(fill="x", pady=(0, 20))
            
            if user_names:
                self.user_combo.set(user_names[0])
        else:
            error_text = "❌ No hay usuarios disponibles en la base de datos."
            users_error = get_users_error()
            if users_error:
                error_text += f"\n{users_error}"

            error_label = ctk.CTkLabel(
                main_frame,
                text=error_text,
                font=FONT_BODY,
                text_color=COLOR_DANGER,
                wraplength=440,
                justify="left"
            )
            error_label.pack(pady=20)
        
        # ── Sección de contraseña
        pwd_label = ctk.CTkLabel(
            main_frame,
            text=" Contraseña:",
            font=FONT_BODY,
            text_color=COLOR_TEXT
        )
        pwd_label.pack(anchor="w", pady=(20, 10))
        
        self.password_entry = ctk.CTkEntry(
            main_frame,
            font=FONT_BODY,
            fg_color=COLOR_PANEL,
            text_color=COLOR_TEXT,
            border_color=COLOR_ACCENT,
            show="●"
        )
        self.password_entry.pack(fill="x", pady=(0, 20))
        
        # ── Info de seguridad
        info_label = ctk.CTkLabel(
            main_frame,
            text="ℹ Por seguridad, ingresa cualquier contraseña para continuar.",
            font=FONT_SMALL,
            text_color=COLOR_MUTED
        )
        info_label.pack(anchor="w", pady=(0, 20))
        
        # ── Botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        login_btn = ctk.CTkButton(
            button_frame,
            text=" Iniciar Sesión",
            font=FONT_BODY,
            fg_color=COLOR_SUCCESS,
            hover_color="#1ade3a",
            command=self.handle_login
        )
        login_btn.pack(fill="x", pady=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Salir",
            font=FONT_BODY,
            fg_color=COLOR_DANGER,
            hover_color="#d32f2f",
            command=self.destroy
        )
        cancel_btn.pack(fill="x")
        
        # ── Footer con info de usuario actual
        if self.users:
            footer_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_PANEL)
            footer_frame.pack(fill="x", pady=(20, 0))
            
            footer_label = ctk.CTkLabel(
                footer_frame,
                text=" Usuarios disponibles:",
                font=FONT_SMALL,
                text_color=COLOR_MUTED
            )
            footer_label.pack(anchor="w", padx=10, pady=(10, 5))
            
            for user in self.users:
                user_info = ctk.CTkLabel(
                    footer_frame,
                    text=f"• {user['nombre']} ({user['tipo']})",
                    font=FONT_SMALL,
                    text_color=COLOR_TEXT
                )
                user_info.pack(anchor="w", padx=20, pady=2)
            
            footer_label2 = ctk.CTkLabel(
                footer_frame,
                text="Contraseña: cualquiera (demo)",
                font=FONT_SMALL,
                text_color=COLOR_MUTED
            )
            footer_label2.pack(anchor="w", padx=10, pady=(5, 10))
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def handle_login(self):
        """Valida el login y abre la aplicación correspondiente."""
        
        if not hasattr(self, 'user_combo') or not self.user_combo.get():
            messagebox.showerror("Error", "Por favor selecciona un usuario.")
            return
        
        password = self.password_entry.get()
        if not password:
            messagebox.showerror("Error", "Por favor ingresa una contraseña.")
            return
        
        # Obtener usuario seleccionado
        selected_text = self.user_combo.get()
        selected_name = selected_text.split(" (")[0]
        
        user_data = None
        for user in self.users:
            if user['nombre'] == selected_name:
                user_data = user
                break
        
        if not user_data:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return
        
        # Validar usuario (en demo, siempre es válido si existe)
        validated_user = validate_user(user_data['id'], password)
        
        if not validated_user:
            messagebox.showerror("Error", "Usuario no válido o inactivo.")
            return
        
        # Login exitoso
        messagebox.showinfo("Éxito", f"¡Bienvenido {user_data['nombre']}!")
        
        # Llamar callback
        from business.services.auth_service import is_admin
        admin = is_admin(user_data)
        self.on_login_callback(user_data, admin)
        
        # Cerrar login
        self.destroy()
