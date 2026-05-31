"""
Rota de Webhook
Recebe eventos da Evolution API (mensagens do WhatsApp)
"""

import logging
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks

from services.processador import processar
from services.whatsapp import enviar_mensagem

router = APIRouter()
logger = logging.getLogger(__name__)


def _extrair_dados_evolution(payload: dict) -> tuple[str, str, str] | None:
    """
    Extrai (telefone, mensagem, nome) do payload da Evolution API.
    Retorna None se o evento não for uma mensagem de texto válida.
    """
    # Ignora eventos que não são mensagens recebidas
    event = payload.get("event", "")
    if event not in ("messages.upsert", "MESSAGES_UPSERT"):
        return None

    data = payload.get("data", {})
    
    # Ignora mensagens enviadas pelo próprio bot
    key = data.get("key", {})
    if key.get("fromMe", False):
        return None

    # Extrai o conteúdo da mensagem
    message = data.get("message", {})
    texto = (
        message.get("conversation")
        or message.get("extendedTextMessage", {}).get("text")
        or ""
    )

    if not texto.strip():
        return None

    # Extrai telefone (remove sufixo @s.whatsapp.net se presente)
    telefone_raw = key.get("remoteJid", "")
    telefone = telefone_raw.replace("@s.whatsapp.net", "").replace("@g.us", "")

    if not telefone:
        return None

    # Nome do contato (se disponível)
    push_name = data.get("pushName", "Usuário")

    return telefone, texto.strip(), push_name


async def _handle_message(telefone: str, texto: str, nome: str):
    """Processa a mensagem e envia a resposta (roda em background)"""
    try:
        resposta = await processar(telefone, texto, nome)
        await enviar_mensagem(telefone, resposta)
    except Exception as e:
        logger.error(f"Erro ao processar mensagem de {telefone}: {e}", exc_info=True)


@router.post("/")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint principal do webhook da Evolution API.
    Recebe todos os eventos e filtra apenas mensagens de texto.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Payload inválido")

    logger.debug(f"Webhook recebido: {payload.get('event', 'sem evento')}")

    dados = _extrair_dados_evolution(payload)
    if dados is None:
        # Evento ignorado (não é mensagem de texto válida)
        return {"status": "ignored"}

    telefone, texto, nome = dados
    logger.info(f"Mensagem recebida de {nome} ({telefone}): '{texto}'")

    # Processa em background para responder rapidamente ao webhook
    background_tasks.add_task(_handle_message, telefone, texto, nome)

    return {"status": "processing"}
