"""
Servicio de asistente: orquesta IA + BD.
La IA NUNCA responde con información genérica — solo datos de la biblioteca.
"""

from typing import Any, Dict

from services import ai_service
from services.biblioteca_service import run_intent_safely


def ask_biblioteca(user_text: str) -> Dict[str, Any]:
    """
    Procesa una consulta del usuario.
    
    Returns:
        Dict estructurado con "type", "message" y "data".
        Nunca retorna texto genérico de IA.
    """
    intent_data = ai_service.try_parse_intent(user_text)

    if intent_data is None:
        # No hay intent reconocido → mensaje restrictivo, NO fallback de IA
        return {
            "type": "text",
            "message": ai_service.get_out_of_scope_message(),
            "data": []
        }

    return run_intent_safely(intent_data)