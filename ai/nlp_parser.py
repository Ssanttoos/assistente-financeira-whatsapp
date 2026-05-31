"""
Módulo de Inteligência Artificial / NLP
Extrai informações financeiras de mensagens em linguagem natural
Usa regex + dicionários para MVP sem custo de API externa
"""

import re
import logging
from typing import Optional, Tuple

from models.transacao import Transacao, TipoTransacao, Categoria

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Palavras-chave para identificar GASTOS
# ─────────────────────────────────────────────
PALAVRAS_GASTO = [
    "gastei", "gasto", "comprei", "compra", "paguei", "pago",
    "pagamento", "uber", "ifood", "rappi", "despesa", "saiu",
    "debito", "débito", "transferi", "mandei", "enviei",
]

# ─────────────────────────────────────────────
# Palavras-chave para identificar RECEITAS
# ─────────────────────────────────────────────
PALAVRAS_RECEITA = [
    "recebi", "receber", "receita", "ganhei", "ganho",
    "salario", "salário", "pix", "deposito", "depósito",
    "entrou", "entrada", "pagaram", "me pagaram",
    "freelance", "renda", "rendimento",
]

# ─────────────────────────────────────────────
# Mapa de categorias por palavras-chave
# ─────────────────────────────────────────────
MAPA_CATEGORIAS: dict[Categoria, list[str]] = {
    Categoria.ALIMENTACAO: [
        "almoço", "almoco", "janta", "jantar", "cafe", "café", "lanche",
        "pizza", "hamburguer", "hambúrguer", "restaurante", "ifood",
        "mercado", "supermercado", "padaria", "açougue", "acougue",
        "comida", "refeição", "refeicao", "bebida", "delivery",
    ],
    Categoria.TRANSPORTE: [
        "uber", "99", "taxi", "táxi", "onibus", "ônibus", "metro", "metrô",
        "combustivel", "combustível", "gasolina", "passagem", "estacionamento",
        "pedágio", "pedagio", "transporte", "bicicleta", "scooter",
    ],
    Categoria.MORADIA: [
        "aluguel", "condomínio", "condominio", "agua", "água", "luz",
        "energia", "iptu", "casa", "apartamento", "reforma", "móveis", "moveis",
        "internet", "wifi",
    ],
    Categoria.SAUDE: [
        "médico", "medico", "farmácia", "farmacia", "remédio", "remedio",
        "hospital", "consulta", "exame", "plano de saúde", "dentista",
        "academia", "ginástica", "ginastica",
    ],
    Categoria.EDUCACAO: [
        "curso", "faculdade", "escola", "mensalidade", "livro", "apostila",
        "aula", "treinamento", "certificado", "graduação", "graduacao",
    ],
    Categoria.LAZER: [
        "cinema", "teatro", "show", "festa", "bar", "balada", "viagem",
        "hotel", "passeio", "jogo", "streaming", "netflix", "spotify",
        "diversão", "diversao", "lazer",
    ],
    Categoria.COMPRAS: [
        "roupa", "sapato", "eletrônico", "eletronico", "celular", "tv",
        "notebook", "presente", "gift", "shopping", "loja", "mercadolivre",
        "amazon", "shopee",
    ],
    Categoria.ASSINATURAS: [
        "assinatura", "netflix", "spotify", "amazon prime", "youtube",
        "disney", "globo", "mensalidade", "plano", "serviço mensal",
    ],
    Categoria.SALARIO: [
        "salário", "salario", "pagamento", "pro-labore", "prolabore",
        "contracheque", "folha",
    ],
    Categoria.INVESTIMENTOS: [
        "investimento", "renda fixa", "tesouro", "ações", "acoes", "fundo",
        "cdb", "lci", "lca", "dividendo", "lucro",
    ],
}


def extrair_valor(mensagem: str) -> Optional[float]:
    """
    Extrai o valor monetário de uma mensagem.
    Suporta formatos: 25, 25.00, 25,00, R$ 25, 1.500,00
    """
    # Remove símbolo de moeda e espaços
    texto = mensagem.lower().replace("r$", "").replace("reais", "").strip()

    # Padrão: 1.500,00 ou 1500,00 ou 1500.00 ou 1500
    padroes = [
        r"(\d{1,3}(?:\.\d{3})*,\d{2})",   # 1.500,00
        r"(\d+,\d{2})",                      # 150,00
        r"(\d+\.\d{2})",                     # 150.00
        r"(\d+)",                            # 150
    ]

    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            valor_str = match.group(1)
            # Normaliza para float
            valor_str = valor_str.replace(".", "").replace(",", ".")
            try:
                return float(valor_str)
            except ValueError:
                continue

    return None


def identificar_tipo(mensagem: str) -> Optional[TipoTransacao]:
    """Identifica se a mensagem é gasto ou receita"""
    msg_lower = mensagem.lower()

    for palavra in PALAVRAS_RECEITA:
        if palavra in msg_lower:
            return TipoTransacao.RECEITA

    for palavra in PALAVRAS_GASTO:
        if palavra in msg_lower:
            return TipoTransacao.GASTO

    return None


def identificar_categoria(mensagem: str) -> Categoria:
    """Identifica a categoria financeira com base em palavras-chave"""
    msg_lower = mensagem.lower()

    for categoria, palavras in MAPA_CATEGORIAS.items():
        for palavra in palavras:
            if palavra in msg_lower:
                return categoria

    return Categoria.OUTROS


def extrair_descricao(mensagem: str) -> str:
    """
    Extrai uma descrição limpa da mensagem.
    Remove valores monetários e palavras-gatilho.
    """
    texto = mensagem.strip()

    # Remove padrões de valor
    texto = re.sub(r"r\$\s*[\d.,]+", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"[\d.,]+\s*(reais|real)", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\b\d+\b", "", texto)

    # Remove palavras-gatilho comuns
    palavras_remover = [
        "gastei", "gasto", "comprei", "paguei", "recebi", "ganhei",
        "com", "de", "por", "em", "no", "na", "um", "uma", "o", "a",
        "reais", "real", "r$",
    ]
    for p in palavras_remover:
        texto = re.sub(rf"\b{p}\b", "", texto, flags=re.IGNORECASE)

    # Limpa espaços duplicados e pontuação
    texto = re.sub(r"\s+", " ", texto).strip()
    texto = texto.strip(".,;:-")

    return texto if texto else "não especificado"


def identificar_periodo_consulta(mensagem: str) -> str:
    """
    Identifica o período da consulta: hoje, semana, mes, ano
    """
    msg = mensagem.lower()
    if any(p in msg for p in ["hoje", "dia", "agora"]):
        return "hoje"
    if any(p in msg for p in ["semana", "7 dias", "sete dias"]):
        return "semana"
    if any(p in msg for p in ["ano", "12 meses", "doze meses"]):
        return "ano"
    return "mes"  # padrão: mês atual


def identificar_intencao(mensagem: str) -> str:
    """
    Identifica a intenção do usuário:
    - 'registrar': gasto ou receita
    - 'consulta': pergunta financeira
    - 'resumo': relatório completo
    - 'ajuda': instruções de uso
    - 'desconhecido'
    """
    msg = mensagem.lower()

    # Comandos de resumo / relatório
    if any(p in msg for p in ["resumo", "relatório", "relatorio", "extrato", "balanço", "balanco"]):
        return "resumo"

    # Comandos de ajuda
    if any(p in msg for p in ["ajuda", "help", "comandos", "como usar", "o que você faz", "oi", "olá", "ola"]):
        return "ajuda"

    # Consultas
    if any(p in msg for p in [
        "quanto gastei", "quanto recebi", "quanto tenho", "qual minha",
        "qual foi", "maior despesa", "categoria", "mostre", "me diz",
        "ver gastos", "ver receitas", "listar",
    ]):
        return "consulta"

    # Registro
    if identificar_tipo(mensagem) is not None and extrair_valor(mensagem) is not None:
        return "registrar"

    return "desconhecido"


def parsear_mensagem(mensagem: str) -> Optional[Transacao]:
    """
    Função principal: tenta extrair uma Transacao completa da mensagem.
    Retorna None se não conseguir identificar tipo ou valor.
    """
    tipo = identificar_tipo(mensagem)
    if tipo is None:
        logger.debug(f"Tipo não identificado para: '{mensagem}'")
        return None

    valor = extrair_valor(mensagem)
    if valor is None:
        logger.debug(f"Valor não identificado para: '{mensagem}'")
        return None

    categoria = identificar_categoria(mensagem)
    descricao = extrair_descricao(mensagem)

    transacao = Transacao(
        tipo=tipo,
        valor=valor,
        categoria=categoria,
        descricao=descricao,
    )

    logger.info(f"Transação extraída: {transacao.tipo} R${transacao.valor} [{transacao.categoria}] - {transacao.descricao}")
    return transacao
