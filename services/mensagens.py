"""
Serviço de Formatação de Respostas
Gera mensagens amigáveis para o WhatsApp
"""

from models.transacao import Transacao, ResumoFinanceiro, TipoTransacao, Categoria

# Emojis por categoria
EMOJI_CATEGORIA: dict[str, str] = {
    "alimentacao": "🍽️",
    "transporte": "🚗",
    "moradia": "🏠",
    "saude": "❤️‍🩹",
    "educacao": "📚",
    "lazer": "🎉",
    "compras": "🛍️",
    "assinaturas": "📱",
    "salario": "💼",
    "investimentos": "📈",
    "outros": "💰",
}

NOME_CATEGORIA: dict[str, str] = {
    "alimentacao": "Alimentação",
    "transporte": "Transporte",
    "moradia": "Moradia",
    "saude": "Saúde",
    "educacao": "Educação",
    "lazer": "Lazer",
    "compras": "Compras",
    "assinaturas": "Assinaturas",
    "salario": "Salário",
    "investimentos": "Investimentos",
    "outros": "Outros",
}


def formatar_valor(valor: float) -> str:
    """Formata valor como moeda brasileira: R$ 1.500,00"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def resposta_transacao_registrada(transacao: Transacao) -> str:
    """Confirmação de registro de gasto ou receita"""
    emoji = EMOJI_CATEGORIA.get(transacao.categoria.value, "💰")
    nome_cat = NOME_CATEGORIA.get(transacao.categoria.value, "Outros")

    if transacao.tipo == TipoTransacao.GASTO:
        return (
            f"✅ *Gasto registrado!*\n\n"
            f"{emoji} *Categoria:* {nome_cat}\n"
            f"💸 *Valor:* {formatar_valor(transacao.valor)}\n"
            f"📝 *Descrição:* {transacao.descricao.capitalize()}\n"
            f"📅 *Data:* {transacao.data.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"_Tudo anotado! 😊_"
        )
    else:
        return (
            f"✅ *Receita registrada!*\n\n"
            f"{emoji} *Categoria:* {nome_cat}\n"
            f"💵 *Valor:* {formatar_valor(transacao.valor)}\n"
            f"📝 *Descrição:* {transacao.descricao.capitalize()}\n"
            f"📅 *Data:* {transacao.data.strftime('%d/%m/%Y %H:%M')}\n\n"
            f"_Ótimo! 🎉_"
        )


def resposta_total_gastos(total: float, periodo: str) -> str:
    """Resposta para 'quanto gastei?'"""
    nomes = {"hoje": "hoje", "semana": "nos últimos 7 dias", "mes": "este mês", "ano": "este ano"}
    periodo_nome = nomes.get(periodo, periodo)
    return f"💸 Você gastou *{formatar_valor(total)}* {periodo_nome}."


def resposta_total_receitas(total: float, periodo: str) -> str:
    """Resposta para 'quanto recebi?'"""
    nomes = {"hoje": "hoje", "semana": "nos últimos 7 dias", "mes": "este mês", "ano": "este ano"}
    periodo_nome = nomes.get(periodo, periodo)
    return f"💵 Você recebeu *{formatar_valor(total)}* {periodo_nome}."


def resposta_maior_despesa(transacao: dict | None) -> str:
    """Resposta para 'qual minha maior despesa?'"""
    if not transacao:
        return "📭 Nenhuma despesa registrada neste período."
    emoji = EMOJI_CATEGORIA.get(transacao.get("categoria", "outros"), "💰")
    nome_cat = NOME_CATEGORIA.get(transacao.get("categoria", "outros"), "Outros")
    return (
        f"🏆 *Sua maior despesa foi:*\n\n"
        f"{emoji} {nome_cat}: *{formatar_valor(transacao.get('valor', 0))}*\n"
        f"📝 {transacao.get('descricao', 'sem descrição').capitalize()}"
    )


def resposta_categorias(categorias: dict[str, float], tipo: str = "gastos") -> str:
    """Resposta para 'qual categoria gastei mais?'"""
    if not categorias:
        return f"📭 Nenhum {tipo} registrado neste período."

    emoji_tipo = "💸" if tipo == "gastos" else "💵"
    linhas = [f"{emoji_tipo} *{tipo.capitalize()} por categoria:*\n"]

    for cat, valor in categorias.items():
        emoji = EMOJI_CATEGORIA.get(cat, "💰")
        nome = NOME_CATEGORIA.get(cat, cat.capitalize())
        linhas.append(f"{emoji} {nome}: *{formatar_valor(valor)}*")

    return "\n".join(linhas)


def resposta_resumo(resumo: ResumoFinanceiro) -> str:
    """Gera o resumo financeiro completo formatado"""
    saldo_emoji = "✅" if resumo.saldo >= 0 else "⚠️"

    linhas = [
        f"📊 *Resumo Financeiro — {resumo.periodo}*\n",
        f"💵 *Receitas:* {formatar_valor(resumo.total_receitas)}",
        f"💸 *Despesas:* {formatar_valor(resumo.total_gastos)}",
        f"{saldo_emoji} *Saldo:* {formatar_valor(resumo.saldo)}",
    ]

    if resumo.gastos_por_categoria:
        linhas.append("\n📂 *Gastos por categoria:*")
        for cat, valor in resumo.gastos_por_categoria.items():
            emoji = EMOJI_CATEGORIA.get(cat, "💰")
            nome = NOME_CATEGORIA.get(cat, cat.capitalize())
            linhas.append(f"  {emoji} {nome}: {formatar_valor(valor)}")

    if resumo.receitas_por_categoria:
        linhas.append("\n📂 *Receitas por categoria:*")
        for cat, valor in resumo.receitas_por_categoria.items():
            emoji = EMOJI_CATEGORIA.get(cat, "💰")
            nome = NOME_CATEGORIA.get(cat, cat.capitalize())
            linhas.append(f"  {emoji} {nome}: {formatar_valor(valor)}")

    if resumo.saldo < 0:
        linhas.append("\n⚠️ _Suas despesas estão maiores que suas receitas. Cuidado! 💪_")
    else:
        linhas.append("\n🎉 _Parabéns! Você está no positivo. Continue assim! 🚀_")

    return "\n".join(linhas)


def resposta_ajuda() -> str:
    """Mensagem de ajuda com exemplos de uso"""
    return (
        "👋 *Olá! Sou sua Assistente Financeira!* 💰\n\n"
        "Posso te ajudar a controlar suas finanças de forma simples. Veja o que você pode me dizer:\n\n"
        "💸 *Registrar gasto:*\n"
        "• Gastei 25 reais com almoço\n"
        "• Paguei 120 de internet\n"
        "• Uber 18 reais\n\n"
        "💵 *Registrar receita:*\n"
        "• Recebi 1500 de salário\n"
        "• Ganhei 200 reais de freelance\n\n"
        "🔍 *Consultar:*\n"
        "• Quanto gastei hoje?\n"
        "• Quanto gastei este mês?\n"
        "• Quanto recebi este mês?\n"
        "• Qual minha maior despesa?\n"
        "• Qual categoria gastei mais?\n"
        "• Resumo financeiro\n\n"
        "_É simples assim! Pode começar! 😊_"
    )


def resposta_nao_entendida() -> str:
    """Mensagem quando não entender o comando"""
    return (
        "🤔 Não entendi muito bem...\n\n"
        "Tente algo como:\n"
        "• _Gastei 50 reais com mercado_\n"
        "• _Recebi 2000 de salário_\n"
        "• _Quanto gastei este mês?_\n"
        "• _Resumo financeiro_\n\n"
        "Ou diga *ajuda* para ver todos os comandos 😊"
    )
