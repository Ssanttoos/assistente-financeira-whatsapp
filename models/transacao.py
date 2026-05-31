"""
Modelos de dados com Pydantic
Define estruturas de Transação, Usuário e Consulta
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TipoTransacao(str, Enum):
    GASTO = "gasto"
    RECEITA = "receita"


class Categoria(str, Enum):
    ALIMENTACAO = "alimentacao"
    TRANSPORTE = "transporte"
    MORADIA = "moradia"
    SAUDE = "saude"
    EDUCACAO = "educacao"
    LAZER = "lazer"
    COMPRAS = "compras"
    ASSINATURAS = "assinaturas"
    SALARIO = "salario"
    INVESTIMENTOS = "investimentos"
    OUTROS = "outros"


class Transacao(BaseModel):
    """Representa uma transação financeira (gasto ou receita)"""
    tipo: TipoTransacao
    valor: float = Field(gt=0, description="Valor em reais, deve ser positivo")
    categoria: Categoria = Categoria.OUTROS
    descricao: str = ""
    data: datetime = Field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "tipo": self.tipo.value,
            "valor": self.valor,
            "categoria": self.categoria.value,
            "descricao": self.descricao,
            "data": self.data.isoformat(),
        }


class Usuario(BaseModel):
    """Representa um usuário do sistema"""
    telefone: str
    nome: str = "Usuário"

    def to_dict(self) -> dict:
        return {
            "telefone": self.telefone,
            "nome": self.nome,
        }


class ResumoFinanceiro(BaseModel):
    """Resumo financeiro de um período"""
    periodo: str
    total_receitas: float = 0.0
    total_gastos: float = 0.0
    saldo: float = 0.0
    gastos_por_categoria: dict[str, float] = Field(default_factory=dict)
    receitas_por_categoria: dict[str, float] = Field(default_factory=dict)


class IncomingMessage(BaseModel):
    """Mensagem recebida do WhatsApp via Evolution API"""
    telefone: str
    mensagem: str
    nome: Optional[str] = "Usuário"
    timestamp: datetime = Field(default_factory=datetime.now)
