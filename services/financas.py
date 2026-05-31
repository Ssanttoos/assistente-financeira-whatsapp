"""
Serviço de Finanças
Operações de CRUD e consultas financeiras no Firestore
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from database.firebase import get_transacoes_ref, get_usuario_ref
from models.transacao import Transacao, ResumoFinanceiro, TipoTransacao, Usuario

logger = logging.getLogger(__name__)


async def garantir_usuario(telefone: str, nome: str = "Usuário") -> None:
    """Cria o documento do usuário no Firestore se não existir"""
    ref = get_usuario_ref(telefone)
    doc = ref.get()
    if not doc.exists:
        usuario = Usuario(telefone=telefone, nome=nome)
        ref.set(usuario.to_dict())
        logger.info(f"Usuário criado: {telefone}")


async def salvar_transacao(telefone: str, transacao: Transacao) -> str:
    """Salva uma transação na subcoleção do usuário. Retorna o ID do documento."""
    await garantir_usuario(telefone)
    ref = get_transacoes_ref(telefone)
    doc = ref.add(transacao.to_dict())
    doc_id = doc[1].id
    logger.info(f"Transação salva [{doc_id}] para {telefone}: {transacao.tipo} R${transacao.valor}")
    return doc_id


def _get_range(periodo: str) -> tuple[datetime, datetime]:
    """Retorna (inicio, fim) para um período"""
    agora = datetime.now()

    if periodo == "hoje":
        inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
        fim = agora
    elif periodo == "semana":
        inicio = agora - timedelta(days=7)
        fim = agora
    elif periodo == "ano":
        inicio = agora.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        fim = agora
    else:  # mes (padrão)
        inicio = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fim = agora

    return inicio, fim


async def buscar_transacoes(telefone: str, periodo: str = "mes", tipo: Optional[TipoTransacao] = None) -> list[dict]:
    """
    Busca transações de um usuário em um período.
    Filtra opcionalmente por tipo (gasto/receita).
    """
    inicio, fim = _get_range(periodo)
    ref = get_transacoes_ref(telefone)

    query = ref.where("data", ">=", inicio.isoformat()).where("data", "<=", fim.isoformat())

    docs = query.stream()
    transacoes = []
    for doc in docs:
        data = doc.to_dict()
        if tipo is None or data.get("tipo") == tipo.value:
            transacoes.append(data)

    logger.info(f"Transações encontradas para {telefone} [{periodo}]: {len(transacoes)}")
    return transacoes


async def calcular_total(telefone: str, periodo: str, tipo: TipoTransacao) -> float:
    """Calcula o total de gastos ou receitas em um período"""
    transacoes = await buscar_transacoes(telefone, periodo, tipo)
    return sum(t.get("valor", 0) for t in transacoes)


async def maior_despesa(telefone: str, periodo: str = "mes") -> Optional[dict]:
    """Retorna a maior despesa do período"""
    transacoes = await buscar_transacoes(telefone, periodo, TipoTransacao.GASTO)
    if not transacoes:
        return None
    return max(transacoes, key=lambda t: t.get("valor", 0))


async def gastos_por_categoria(telefone: str, periodo: str = "mes") -> dict[str, float]:
    """Agrupa e soma gastos por categoria"""
    transacoes = await buscar_transacoes(telefone, periodo, TipoTransacao.GASTO)
    categorias: dict[str, float] = {}
    for t in transacoes:
        cat = t.get("categoria", "outros")
        categorias[cat] = categorias.get(cat, 0) + t.get("valor", 0)
    # Ordena por valor descrescente
    return dict(sorted(categorias.items(), key=lambda x: x[1], reverse=True))


async def receitas_por_categoria(telefone: str, periodo: str = "mes") -> dict[str, float]:
    """Agrupa e soma receitas por categoria"""
    transacoes = await buscar_transacoes(telefone, periodo, TipoTransacao.RECEITA)
    categorias: dict[str, float] = {}
    for t in transacoes:
        cat = t.get("categoria", "outros")
        categorias[cat] = categorias.get(cat, 0) + t.get("valor", 0)
    return dict(sorted(categorias.items(), key=lambda x: x[1], reverse=True))


async def gerar_resumo(telefone: str, periodo: str = "mes") -> ResumoFinanceiro:
    """Gera um objeto ResumoFinanceiro completo para o período"""
    total_receitas = await calcular_total(telefone, periodo, TipoTransacao.RECEITA)
    total_gastos = await calcular_total(telefone, periodo, TipoTransacao.GASTO)
    g_cat = await gastos_por_categoria(telefone, periodo)
    r_cat = await receitas_por_categoria(telefone, periodo)

    nomes_periodo = {
        "hoje": "Hoje",
        "semana": "Últimos 7 dias",
        "mes": f"Mês de {datetime.now().strftime('%B/%Y')}",
        "ano": f"Ano de {datetime.now().year}",
    }

    return ResumoFinanceiro(
        periodo=nomes_periodo.get(periodo, periodo),
        total_receitas=total_receitas,
        total_gastos=total_gastos,
        saldo=total_receitas - total_gastos,
        gastos_por_categoria=g_cat,
        receitas_por_categoria=r_cat,
    )
