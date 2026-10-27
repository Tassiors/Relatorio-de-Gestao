# src/providers/interfaces/relatorio_gestao_provider_interface.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class RelatorioGestaoProviderInterface(ABC):
    """Interface (contrato) para provedores de dados do Portal de Relatórios de Gestão."""

    @abstractmethod
    async def listar_gerencias_com_uorgs(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obter_uorg_por_id(self, uorg_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obter_exercicio_ativo(self) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def listar_exercicios(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obter_exercicio_por_id(self, exercicio_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obter_bimestres(self, exercicio_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def listar_entregas_uorg(self, exercicio_id: int, uorg_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def listar_indicadores_uorg(self, exercicio_id: int, uorg_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obter_relatorio(
        self, exercicio_id: int, bimestre_id: int, uorg_id: int
    ) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def salvar_rascunho(
        self, exercicio_id: int, bimestre_id: int, uorg_id: int, dados: Dict[str, Any], usuario: str
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def enviar_relatorio(
        self, relatorio_id: int, usuario: str
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def registrar_feedback(
        self, relatorio_id: int, usuario: str, perfil: str, nome: str, texto: str
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def conceder_prazo_excepcional(
        self, exercicio_id: int, bimestre_id: int, uorg_id: int, motivo: str, data_fim: str, usuario: str
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def obter_matriz_acompanhamento(self, exercicio_id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def listar_notificacoes(
        self, username: str, perfil: Optional[str] = None, uorg_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def marcar_notificacao_lida(self, notificacao_id: int) -> bool:
        pass

    @abstractmethod
    async def criar_entrega(
        self, uorg_id: int, exercicio_id: int, titulo: str, descricao: Optional[str] = None, ordem: int = 1
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def obter_entrega(self, entrega_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def editar_entrega(
        self, entrega_id: int, titulo: str, descricao: Optional[str] = None
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def inativar_entrega(self, entrega_id: int) -> bool:
        pass

    @abstractmethod
    async def criar_indicador(
        self, uorg_id: int, exercicio_id: int, nome: str, descricao: Optional[str],
        periodicidade: str, unidade_medida: str, meta_operador: str,
        meta_valor: float, meta_valor_max: Optional[float] = None, ordem: int = 1
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def obter_indicador(self, indicador_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def editar_indicador(
        self, indicador_id: int, dados: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def inativar_indicador(self, indicador_id: int) -> bool:
        pass

    @abstractmethod
    async def atualizar_status_exercicio(
        self, exercicio_id: int, status: str
    ) -> Dict[str, Any]:
        pass

