from app.models.viagem import ViagemEntrada, ViagemResposta
from app.repositories.viagem_repository import ViagemRepository


class ViagemService:
    def __init__(self, repositorio: ViagemRepository) -> None:
        self.repositorio = repositorio

    def criar(self, viagem: ViagemEntrada) -> ViagemResposta:
        return self.repositorio.criar(viagem)

    def listar(self) -> list[ViagemResposta]:
        return self.repositorio.listar()

    def obter(self, viagem_id: int) -> ViagemResposta | None:
        return self.repositorio.obter(viagem_id)

    def atualizar(
        self, viagem_id: int, viagem: ViagemEntrada
    ) -> ViagemResposta | None:
        return self.repositorio.atualizar(viagem_id, viagem)

    def deletar(self, viagem_id: int) -> bool:
        return self.repositorio.deletar(viagem_id)
