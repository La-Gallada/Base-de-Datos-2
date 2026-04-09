import pyodbc

SERVER = r"DESKTOP-MQ0NP7T\SQLEXPRESS"
DATABASE = "BibliotecaBD"

# Credenciales por rol
CREDENTIALS = {
    "Cliente": {
        "username": "login_client",
        "password": "amoleer2026"
    },
    "Administrador": {
        "username": "login_dirBiblioteca",
        "password": "quijotedon10"
    }
}

def get_connection(user_role=None):
    """
    Crea una conexión a la base de datos usando el rol del usuario.
    Si no se especifica rol, usa autenticación de Windows (para desarrollo).
    """
    if user_role and user_role in CREDENTIALS:
        # Usar autenticación SQL Server con credenciales específicas del rol
        creds = CREDENTIALS[user_role]
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"UID={creds['username']};"
            f"PWD={creds['password']};"
            "TrustServerCertificate=yes;"
        )
    else:
        # Fallback: autenticación de Windows (para desarrollo/administración)
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

    return pyodbc.connect(conn_str)

def get_connection_by_user_type(user_type):
    """
    Alias para get_connection para mantener compatibilidad.
    """
    return get_connection(user_type)