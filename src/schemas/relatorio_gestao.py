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
    motivo: Optional[str] = None
    data_fim: str = Field(...)

PrazoExcepcionalCreate = PrazoExcepcionalSchema

class AtualizarBimestreSchema(BaseModel):
    status: Optional[str] = None
    data_fechamento_regular: Optional[str] = None

class CriarEntregaSchema(BaseModel):
    uorg_id: int
    exercicio_id: int
    titulo: str = Field(..., min_length=3)
    descricao: Optional[str] = None
    ordem: Optional[int] = 1

class EditarEntregaSchema(BaseModel):
    titulo: str = Field(..., min_length=3)
    descricao: Optional[str] = None

class CriarIndicadorSchema(BaseModel):
    uorg_id: int
    exercicio_id: int
    nome: str = Field(..., min_length=3)
    descricao: Optional[str] = None
    periodicidade: str = Field("BIMESTRAL", pattern="^(MENSAL|BIMESTRAL|TRIMESTRAL|QUADRIMESTRAL|SEMESTRAL)$")
    unidade_medida: str = Field(..., min_length=1)
    meta_operador: str = Field("MAIOR_IGUAL", pattern="^(MAIOR_IGUAL|MENOR_IGUAL|IGUAL|ENTRE)$")
    meta_valor: float
    meta_valor_max: Optional[float] = None
    ordem: Optional[int] = 1

class EditarIndicadorSchema(BaseModel):
    nome: str = Field(..., min_length=3)
    descricao: Optional[str] = None
    periodicidade: str = Field("BIMESTRAL", pattern="^(MENSAL|BIMESTRAL|TRIMESTRAL|QUADRIMESTRAL|SEMESTRAL)$")
    unidade_medida: str = Field(..., min_length=1)
    meta_operador: str = Field("MAIOR_IGUAL", pattern="^(MAIOR_IGUAL|MENOR_IGUAL|IGUAL|ENTRE)$")
    meta_valor: float
    meta_valor_max: Optional[float] = None

class AlterarStatusExercicioSchema(BaseModel):
    status: str = Field(..., pattern="^(PLANEJAMENTO|EM_ANDAMENTO|ENCERRADO)$")

