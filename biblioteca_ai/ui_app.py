import customtkinter as ctk
import threading

from assistant_service import ask_biblioteca


class ChatApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Biblioteca AI Assistant")
        self.geometry("750x540")

        # Chat output
        self.chat_box = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self.chat_box.pack(padx=12, pady=(12, 6), fill="both", expand=True)

        # Status label (thinking...)
        self.loading_label = ctk.CTkLabel(self, text="")
        self.loading_label.pack(pady=(0, 6))

        # Input row
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=12, pady=12)

        self.user_input = ctk.CTkEntry(
            self.input_frame, placeholder_text="Escribe tu pregunta sobre la biblioteca..."
        )
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = ctk.CTkButton(
            self.input_frame, text="Enviar", command=self.send_message
        )
        self.send_button.pack(side="right")

        self.is_busy = False

        # Mensaje inicial (opcional)
        self.append_message("Bot", "Hola 👋 Preguntame cosas como: '¿Cuántos libros hay de matemáticas?'")

    def append_message(self, sender: str, message: str):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", f"{sender}: {message}\n\n")
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def set_busy(self, busy: bool):
        self.is_busy = busy
        self.user_input.configure(state="disabled" if busy else "normal")
        self.send_button.configure(state="disabled" if busy else "normal")
        self.loading_label.configure(text="Pensando..." if busy else "")

    def send_message(self, event=None):
        if self.is_busy:
            return

        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self.user_input.delete(0, "end")
        self.append_message("Tú", user_text)
        self.set_busy(True)

        threading.Thread(
            target=self._worker_process_message,
            args=(user_text,),
            daemon=True
        ).start()

    def _worker_process_message(self, user_text: str):
        try:
            reply = ask_biblioteca(user_text)
        except Exception as e:
            reply = f"Error procesando tu solicitud: {e}"

        # Volver al hilo principal para tocar UI
        self.after(0, lambda: self._finish_reply(reply))

    def _finish_reply(self, reply: str):
        self.append_message("Bot", reply)
        self.set_busy(False)


if __name__ == "__main__":
    app = ChatApp()
    app.mainloop()