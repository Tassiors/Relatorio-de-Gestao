# src/schemas/relatorio_gestao.py
from pydantic import BaseModel, Field
from typing import List, Optional

class ItemEntregaSchema(BaseModel):
    entrega_id: int
    concluida: bool = False
    observacoes: Optional[str] = None

class ItemIndicadorSchema(BaseModel):
    indicador_id: int
    competencia: str = "Bimestre"
    valor_apurado: Optional[float] = None
    meta_atingida: Optional[bool] = None
    meta_operador: Optional[str] = None
    meta_valor: Optional[float] = None
    meta_valor_max: Optional[float] = None
    resultado_indisponivel: bool = False
    justificativa_indisponibilidade: Optional[str] = None
    nao_aplicavel: bool = False

class SalvarRascunhoSchema(BaseModel):
    exercicio_id: int
    bimestre_id: int
    uorg_id: int
    destaques: Optional[str] = ""
    dificuldades: Optional[str] = ""
    itens_entrega: List[ItemEntregaSchema] = []
    itens_indicador: List[ItemIndicadorSchema] = []

class EnviarRelatorioSchema(BaseModel):
    relatorio_id: Optional[int] = None
    exercicio_id: int
    bimestre_id: int
    uorg_id: int
    destaques: str = Field(..., min_length=5)
    dificuldades: str = Field(..., min_length=5)
    itens_entrega: List[ItemEntregaSchema] = []
    itens_indicador: List[ItemIndicadorSchema] = []

class RegistrarFeedbackSchema(BaseModel):
    texto: str = Field(..., min_length=5)

class PrazoExcepcionalSchema(BaseModel):
    exercicio_id: int
    bimestre_id: int
    uorg_id: int
    motivo: str = Field(..., min_length=10)
    data_fim: str = Field(...)
