"""
Processador de Mensagens
Orquestra NLP, banco de dados e geração de respostas
"""

import logging

from ai.nlp_parser import (
    parsear_mensagem,
    identificar_intencao,
    identificar_periodo_consulta,
)
from models.transacao import TipoTransacao
from services import financas, mensagens

logger = logging.getLogger(__name__)


async def processar(telefone: str, texto: str, nome: str = "Usuário") -> str:
    """
    Processa uma mensagem recebida e retorna a resposta adequada.
    
    Args:
        telefone: Número do remetente
        texto: Mensagem de texto
        nome: Nome do usuário (se disponível)
    
    Returns:
        Texto da resposta a ser enviada
    """
    logger.info(f"Processando mensagem de {telefone}: '{texto}'")

    intencao = identificar_intencao(texto)
    logger.info(f"Intenção identificada: {intencao}")

    # ── REGISTRAR TRANSAÇÃO ───────────────────────────────────────────────
    if intencao == "registrar":
        transacao = parsear_mensagem(texto)
        if transacao:
            await financas.salvar_transacao(telefone, transacao)
            return mensagens.resposta_transacao_registrada(transacao)
        return mensagens.resposta_nao_entendida()

    # ── RESUMO FINANCEIRO ────────────────────────────────────────────────
    elif intencao == "resumo":
        periodo = identificar_periodo_consulta(texto)
        resumo = await financas.gerar_resumo(telefone, periodo)
        return mensagens.resposta_resumo(resumo)

    # ── CONSULTAS ─────────────────────────────────────────────────────────
    elif intencao == "consulta":
        periodo = identificar_periodo_consulta(texto)
        txt = texto.lower()

        # "quanto gastei"
        if "gastei" in txt or "gasto" in txt or "despesa" in txt:
            total = await financas.calcular_total(telefone, periodo, TipoTransacao.GASTO)
            return mensagens.resposta_total_gastos(total, periodo)

        # "quanto recebi"
        if "recebi" in txt or "receita" in txt or "entrou" in txt:
            total = await financas.calcular_total(telefone, periodo, TipoTransacao.RECEITA)
            return mensagens.resposta_total_receitas(total, periodo)

        # "maior despesa"
        if "maior" in txt and ("despesa" in txt or "gasto" in txt):
            maior = await financas.maior_despesa(telefone, periodo)
            return mensagens.resposta_maior_despesa(maior)

        # "categoria" de gastos
        if "categoria" in txt and ("receita" in txt or "recebi" in txt):
            cats = await financas.receitas_por_categoria(telefone, periodo)
            return mensagens.resposta_categorias(cats, "receitas")

        if "categoria" in txt:
            cats = await financas.gastos_por_categoria(telefone, periodo)
            return mensagens.resposta_categorias(cats, "gastos")

        # Fallback: resumo geral
        resumo = await financas.gerar_resumo(telefone, periodo)
        return mensagens.resposta_resumo(resumo)

    # ── AJUDA ────────────────────────────────────────────────────────────
    elif intencao == "ajuda":
        return mensagens.resposta_ajuda()

    # ── NÃO ENTENDIDO ────────────────────────────────────────────────────
    else:
        return mensagens.resposta_nao_entendida()
