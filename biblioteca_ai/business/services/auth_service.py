"""
Servicio de autenticación.
Gestiona logins y validación de usuarios.
"""

from typing import Optional, Dict, Any
import data.biblioteca_repo as biblioteca_repo

_last_users_error: str = ""


def get_users_for_login() -> list:
    """
    Obtiene todos los usuarios disponibles para login.
    Se cargan desde la base de datos.
    """
    global _last_users_error
    _last_users_error = ""

    try:
        rows = biblioteca_repo.sp_get_users(user_role="Administrador")
    except Exception as e:
        _last_users_error = f"Error admin DB: {e}"
        print(f"Error al cargar usuarios con rol Administrador: {e}")
        try:
            rows = biblioteca_repo.sp_get_users()
        except Exception as e2:
            _last_users_error += f" | Fallback error: {e2}"
            print(f"Error al cargar usuarios con conexión por defecto: {e2}")
            return []

    if not rows:
        _last_users_error = _last_users_error or "La base de datos no devolvió usuarios. Verifica que la tabla Users tenga registros."

    users = []
    for row in rows:
        users.append({
            "id": row[0],
            "nombre": f"{row[1]} {row[2]}",
            "email": row[3],
            "tipo": row[4],  # Cliente, Administrador, Director
            "estado": row[5]
        })
    return users


def get_users_error() -> str:
    """Retorna el último error encontrado al cargar usuarios."""
    return _last_users_error


def validate_user(user_id: int, password: str) -> Optional[Dict[str, Any]]:
    """
    Valida un usuario (en una aplicación real, verificaría contraseña en BD).
    Por ahora, simplemente valida que el usuario exista.
    
    Args:
        user_id: ID del usuario
        password: Contraseña (no verificada en este prototipo)
        
    Returns:
        Dict con datos del usuario si es válido, None si no.
    """
    users = get_users_for_login()
    
    for user in users:
        if user["id"] == user_id and user["estado"] == "Activo":
            return user
    
    return None


def is_admin(user: Dict[str, Any]) -> bool:
    """Verifica si un usuario es administrador."""
    return user.get("tipo") in ["Administrador", "Director"]


def is_normal_user(user: Dict[str, Any]) -> bool:
    """Verifica si un usuario es normal."""
    return user.get("tipo") == "Cliente"
