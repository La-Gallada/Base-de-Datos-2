import customtkinter as ctk
from presentation.login_app import LoginApp
from presentation.ui_app import ChatApp


def on_login(user_data, is_admin):
    """
    Callback cuando el usuario inicia sesión.
    Abre la aplicación principal y oculta la ventana raíz.
    """
    # Ocultar la ventana raíz en lugar de destruirla para evitar errores de threading
    root.withdraw()

    # Abrir la aplicación principal en pantalla completa
    app = ChatApp(user_data=user_data, is_admin=is_admin)
    app.mainloop()


if __name__ == "__main__":
    # Crear ventana raíz (oculta)
    root = ctk.CTk()
    root.withdraw()  # Ocultar ventana raíz
    
    # Mostrar login
    login = LoginApp(root, on_login_callback=on_login)
    login.mainloop()

if __name__ == "__main__":
    main()