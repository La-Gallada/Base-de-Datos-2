"""
Interfaz gráfica de la Biblioteca Inteligente.
Incluye:
  - Chat con la IA (solo respuestas de la BD)
  - Panel de libros con tarjetas visuales y botón de préstamo
  - Feedback visual de disponibilidad
"""

import threading
import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta

from assistant_service import ask_biblioteca
from services.biblioteca_service import register_loan


# ─────────────────────────────────────────────
# TEMA Y COLORES
# ─────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_BG           = "#0f1117"
COLOR_PANEL        = "#1a1d27"
COLOR_CARD         = "#22263a"
COLOR_CARD_HOVER   = "#2a2f45"
COLOR_ACCENT       = "#4f8ef7"
COLOR_SUCCESS      = "#22c55e"
COLOR_DANGER       = "#ef4444"
COLOR_WARNING      = "#f59e0b"
COLOR_TEXT         = "#e2e8f0"
COLOR_MUTED        = "#64748b"
COLOR_BORDER       = "#2d3148"

FONT_TITLE   = ("Segoe UI", 22, "bold")
FONT_HEADING = ("Segoe UI", 14, "bold")
FONT_BODY    = ("Segoe UI", 12)
FONT_SMALL   = ("Segoe UI", 10)
FONT_MONO    = ("Consolas", 11)


# ─────────────────────────────────────────────
# COMPONENTE: TARJETA DE LIBRO
# ─────────────────────────────────────────────

class BookCard(ctk.CTkFrame):
    """
    Tarjeta visual para mostrar un libro con su disponibilidad
    y botón de préstamo.
    """

    def __init__(self, parent, book: dict, on_loan_callback, **kwargs):
        super().__init__(
            parent,
            fg_color=COLOR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER,
            **kwargs
        )

        self.book = book
        self.on_loan_callback = on_loan_callback
        disponible = book["disponible"] > 0

        # ── Franja de color lateral según disponibilidad
        accent_color = COLOR_SUCCESS if disponible else COLOR_DANGER
        left_bar = ctk.CTkFrame(self, width=5, fg_color=accent_color, corner_radius=3)
        left_bar.pack(side="left", fill="y", padx=(0, 10))

        # ── Contenido principal
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, pady=12, padx=(0, 12))

        # Título
        ctk.CTkLabel(
            content,
            text=book["titulo"],
            font=FONT_HEADING,
            text_color=COLOR_TEXT,
            anchor="w"
        ).pack(fill="x")

        # Categoría + año
        ctk.CTkLabel(
            content,
            text=f"📂 {book['categoria']}  ·  📅 {book['anio']}",
            font=FONT_SMALL,
            text_color=COLOR_MUTED,
            anchor="w"
        ).pack(fill="x", pady=(2, 6))

        # ISBN
        ctk.CTkLabel(
            content,
            text=f"ISBN: {book['isbn']}",
            font=FONT_SMALL,
            text_color=COLOR_MUTED,
            anchor="w"
        ).pack(fill="x")

        # ── Panel derecho: stock + botón
        right = ctk.CTkFrame(self, fg_color="transparent", width=140)
        right.pack(side="right", fill="y", padx=12, pady=12)
        right.pack_propagate(False)

        # Indicador de stock
        stock_text = f"✅ {book['disponible']} disponible(s)" if disponible else "❌ No disponible"
        stock_color = COLOR_SUCCESS if disponible else COLOR_DANGER
        ctk.CTkLabel(
            right,
            text=stock_text,
            font=FONT_SMALL,
            text_color=stock_color
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            right,
            text=f"Total: {book['total']}",
            font=FONT_SMALL,
            text_color=COLOR_MUTED
        ).pack(pady=(0, 8))

        # Botón de préstamo
        btn = ctk.CTkButton(
            right,
            text="📤 Prestar",
            width=120,
            height=32,
            font=FONT_SMALL,
            fg_color=COLOR_ACCENT if disponible else COLOR_MUTED,
            hover_color="#3b6fd4" if disponible else COLOR_MUTED,
            state="normal" if disponible else "disabled",
            command=self._on_loan_click
        )
        btn.pack()

        if not disponible:
            ctk.CTkLabel(
                right,
                text="Sin ejemplares",
                font=("Segoe UI", 9),
                text_color=COLOR_MUTED
            ).pack(pady=(4, 0))

    def _on_loan_click(self):
        self.on_loan_callback(self.book)


# ─────────────────────────────────────────────
# COMPONENTE: PANEL DE RESULTADOS
# ─────────────────────────────────────────────

class ResultsPanel(ctk.CTkScrollableFrame):
    """
    Panel scrollable que muestra resultados de la BD en formato visual.
    """

    def __init__(self, parent, on_loan_callback, **kwargs):
        super().__init__(
            parent,
            fg_color=COLOR_BG,
            scrollbar_button_color=COLOR_BORDER,
            **kwargs
        )
        self.on_loan_callback = on_loan_callback

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_books(self, message: str, books: list):
        self.clear()

        # Mensaje encabezado
        ctk.CTkLabel(
            self,
            text=message,
            font=FONT_HEADING,
            text_color=COLOR_TEXT,
            anchor="w"
        ).pack(fill="x", padx=8, pady=(8, 12))

        if not books:
            ctk.CTkLabel(
                self,
                text="No se encontraron libros.",
                font=FONT_BODY,
                text_color=COLOR_MUTED
            ).pack(padx=8)
            return

        for book in books:
            card = BookCard(self, book, self.on_loan_callback)
            card.pack(fill="x", padx=8, pady=4)

    def show_text(self, message: str):
        self.clear()
        ctk.CTkLabel(
            self,
            text=message,
            font=FONT_BODY,
            text_color=COLOR_TEXT,
            anchor="nw",
            wraplength=520,
            justify="left"
        ).pack(fill="both", expand=True, padx=16, pady=16)

    def show_table(self, message: str, headers: list, rows: list):
        self.clear()
        ctk.CTkLabel(
            self,
            text=message,
            font=FONT_HEADING,
            text_color=COLOR_TEXT,
            anchor="w"
        ).pack(fill="x", padx=8, pady=(8, 12))

        # Encabezados
        header_frame = ctk.CTkFrame(self, fg_color=COLOR_BORDER, corner_radius=6)
        header_frame.pack(fill="x", padx=8, pady=(0, 2))
        for h in headers:
            ctk.CTkLabel(
                header_frame, text=h, font=("Segoe UI", 11, "bold"),
                text_color=COLOR_TEXT
            ).pack(side="left", expand=True, padx=8, pady=6)

        # Filas
        for i, row in enumerate(rows):
            bg = COLOR_CARD if i % 2 == 0 else COLOR_PANEL
            row_frame = ctk.CTkFrame(self, fg_color=bg, corner_radius=4)
            row_frame.pack(fill="x", padx=8, pady=1)
            for cell in row:
                ctk.CTkLabel(
                    row_frame, text=str(cell), font=FONT_SMALL,
                    text_color=COLOR_TEXT
                ).pack(side="left", expand=True, padx=8, pady=5)


# ─────────────────────────────────────────────
# VENTANA PRINCIPAL
# ─────────────────────────────────────────────

class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("📚 Biblioteca Inteligente")
        self.geometry("1100x680")
        self.minsize(900, 580)
        self.configure(fg_color=COLOR_BG)

        self._build_layout()
        self._welcome()

    def _build_layout(self):
        # ── Header
        header = ctk.CTkFrame(self, fg_color=COLOR_PANEL, height=60, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📚  Biblioteca Inteligente",
            font=FONT_TITLE,
            text_color=COLOR_TEXT
        ).pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            header,
            text="Solo respondo con datos reales de la biblioteca",
            font=FONT_SMALL,
            text_color=COLOR_MUTED
        ).pack(side="right", padx=20)

        # ── Cuerpo: chat izquierda + resultados derecha
        body = ctk.CTkFrame(self, fg_color=COLOR_BG)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        # Panel izquierdo: chat
        left = ctk.CTkFrame(body, fg_color=COLOR_PANEL, corner_radius=0, width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(
            left, text="💬 Chat", font=FONT_HEADING, text_color=COLOR_TEXT
        ).pack(anchor="w", padx=16, pady=(12, 6))

        # Historial de chat
        self.chat_box = ctk.CTkTextbox(
            left,
            state="disabled",
            wrap="word",
            fg_color=COLOR_BG,
            font=FONT_BODY,
            text_color=COLOR_TEXT,
            corner_radius=8
        )
        self.chat_box.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        # Status "pensando..."
        self.loading_label = ctk.CTkLabel(left, text="", font=FONT_SMALL, text_color=COLOR_ACCENT)
        self.loading_label.pack()

        # Entrada de texto
        input_frame = ctk.CTkFrame(left, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=(0, 12))

        self.user_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Escribe tu consulta...",
            fg_color=COLOR_CARD,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT,
            font=FONT_BODY,
            height=38
        )
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = ctk.CTkButton(
            input_frame,
            text="▶",
            width=38,
            height=38,
            fg_color=COLOR_ACCENT,
            hover_color="#3b6fd4",
            font=("Segoe UI", 16),
            command=self.send_message
        )
        self.send_button.pack(side="right")

        # Separador vertical
        sep = ctk.CTkFrame(body, fg_color=COLOR_BORDER, width=1)
        sep.pack(side="left", fill="y")

        # Panel derecho: resultados
        right = ctk.CTkFrame(body, fg_color=COLOR_BG)
        right.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            right, text="📊 Resultados", font=FONT_HEADING, text_color=COLOR_TEXT
        ).pack(anchor="w", padx=16, pady=(12, 6))

        self.results_panel = ResultsPanel(
            right,
            on_loan_callback=self._on_loan_requested
        )
        self.results_panel.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.is_busy = False

    def _welcome(self):
        self._append_bot(
            "Hola 👋 Soy el asistente de la biblioteca.\n\n"
            "Solo puedo responder sobre los datos de esta biblioteca.\n\n"
            "Prueba con:\n"
            "• '¿Qué libros hay?'\n"
            "• '¿Está disponible Sapiens?'\n"
            "• '¿Préstamos activos?'"
        )
        self.results_panel.show_text(
            "Escribe una consulta en el chat para ver los resultados aquí.\n\n"
            "💡 Tip: Pregunta '¿Qué libros hay?' para ver el catálogo completo con opciones de préstamo."
        )

    # ── CHAT ─────────────────────────────────

    def _append_bot(self, text: str):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"🤖 Bot:\n{text}\n\n")
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def _append_user(self, text: str):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"👤 Tú:\n{text}\n\n")
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def _set_busy(self, busy: bool):
        self.is_busy = busy
        state = "disabled" if busy else "normal"
        self.user_input.configure(state=state)
        self.send_button.configure(state=state)
        self.loading_label.configure(text="⏳ Consultando la biblioteca..." if busy else "")

    def send_message(self, event=None):
        if self.is_busy:
            return
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self.user_input.delete(0, "end")
        self._append_user(user_text)
        self._set_busy(True)

        threading.Thread(
            target=self._worker,
            args=(user_text,),
            daemon=True
        ).start()

    def _worker(self, user_text: str):
        try:
            result = ask_biblioteca(user_text)
        except Exception as e:
            result = {"type": "text", "message": f"⚠️ Error: {e}", "data": []}

        self.after(0, lambda: self._handle_result(result))

    def _handle_result(self, result: dict):
        rtype   = result.get("type", "text")
        message = result.get("message", "")
        data    = result.get("data", [])

        # Siempre mostrar mensaje en chat
        self._append_bot(message)
        self._set_busy(False)

        # Mostrar datos en panel derecho según tipo
        if rtype == "books":
            self.results_panel.show_books(message, data)

        elif rtype == "users":
            self.results_panel.show_table(
                message,
                ["ID", "Nombre", "Email", "Tipo", "Estado"],
                [[u["id"], u["nombre"], u["email"], u["tipo"], u["estado"]] for u in data]
            )

        elif rtype == "authors":
            headers = ["ID", "Nombre", "Nacionalidad"] if data and "nacionalidad" in data[0] else ["Nombre", "Préstamos"]
            rows = (
                [[a["id"], a["nombre"], a["nacionalidad"]] for a in data]
                if data and "nacionalidad" in data[0]
                else [[a["nombre"], a["prestamos"]] for a in data]
            )
            self.results_panel.show_table(message, headers, rows)

        elif rtype == "categories":
            self.results_panel.show_table(
                message,
                ["ID", "Nombre", "Descripción"],
                [[c["id"], c["nombre"], c["descripcion"]] for c in data]
            )

        elif rtype == "loans":
            self.results_panel.show_table(
                message,
                ["ID", "Usuario", "Libro", "Préstamo", "Devolución", "Estado"],
                [[l["id"], l["usuario"], l["libro"], l["fecha_prestamo"], l["fecha_devolucion"], l["estado"]] for l in data]
            )

        else:
            self.results_panel.show_text(message)

    # ── PRÉSTAMOS ────────────────────────────

    def _on_loan_requested(self, book: dict):
        """
        Callback cuando el usuario hace clic en 'Prestar' en una tarjeta.
        Muestra confirmación y registra el préstamo si confirma.
        """
        titulo     = book["titulo"]
        disponible = book["disponible"]

        if disponible <= 0:
            messagebox.showwarning(
                "Sin disponibilidad",
                f"'{titulo}' no tiene ejemplares disponibles en este momento."
            )
            return

        hoy       = date.today()
        devolucion = hoy + timedelta(days=14)

        confirm = messagebox.askyesno(
            "Confirmar préstamo",
            f"¿Deseas prestar el libro?\n\n"
            f"📚 {titulo}\n"
            f"📅 Préstamo: {hoy.strftime('%d/%m/%Y')}\n"
            f"📅 Devolución: {devolucion.strftime('%d/%m/%Y')}\n\n"
            f"Ejemplares disponibles: {disponible}"
        )

        if not confirm:
            return

        # Registrar préstamo en hilo secundario para no bloquear UI
        self._set_busy(True)
        threading.Thread(
            target=self._worker_loan,
            args=(book["id"],),
            daemon=True
        ).start()

    def _worker_loan(self, id_libro: int):
        result = register_loan(id_libro=id_libro, id_usuario=1)
        self.after(0, lambda: self._finish_loan(result, id_libro))

    def _finish_loan(self, result: dict, id_libro: int):
        self._set_busy(False)
        success = result.get("success", False)
        message = result.get("message", "")

        if success:
            self._append_bot(message)
            messagebox.showinfo("✅ Préstamo registrado", message)
            # Refrescar el panel de libros automáticamente
            self._refresh_books_panel()
        else:
            self._append_bot(message)
            messagebox.showerror("❌ Error", message)

    def _refresh_books_panel(self):
        """
        Recarga la lista de libros en el panel derecho tras un préstamo.
        """
        from assistant_service import ask_biblioteca
        threading.Thread(
            target=lambda: self.after(
                0,
                lambda: self._handle_result(ask_biblioteca("ver todos los libros"))
            ),
            daemon=True
        ).start()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()