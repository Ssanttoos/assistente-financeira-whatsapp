"""
Serviço de integração com Evolution API
Responsável por enviar mensagens de volta ao WhatsApp
"""

import logging
import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


async def enviar_mensagem(telefone: str, mensagem: str) -> bool:
    """
    Envia uma mensagem de texto para o WhatsApp via Evolution API.
    
    Args:
        telefone: Número do destinatário (ex: "5511999999999")
        mensagem: Texto a ser enviado (suporta markdown do WhatsApp)
    
    Returns:
        True se enviado com sucesso, False caso contrário
    """
    if not settings.evolution_api_url or not settings.evolution_api_key:
        logger.warning("Evolution API não configurada. Mensagem não enviada.")
        logger.info(f"[SIMULADO] Mensagem para {telefone}:\n{mensagem}")
        return False

    url = f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance_name}"

    payload = {
        "number": telefone,
        "options": {
            "delay": 500,
            "presence": "composing",
        },
        "textMessage": {
            "text": mensagem
        }
    }

    headers = {
        "apikey": settings.evolution_api_key,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"Mensagem enviada para {telefone}: status {response.status_code}")
            return True
    except httpx.HTTPStatusError as e:
        logger.error(f"Erro HTTP ao enviar mensagem: {e.response.status_code} - {e.response.text}")
        return False
    except httpx.RequestError as e:
        logger.error(f"Erro de conexão com Evolution API: {e}")
        return False
