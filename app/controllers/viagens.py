import os

from fastapi import APIRouter, HTTPException, Response, status

from app.models.viagem import (
    PrevisaoResposta,
    ViagemDetalheResposta,
    ViagemEntrada,
    ViagemResposta,
)
from app.repositories.viagem_repository import ViagemRepository
from app.services.api_secundaria_service import (
    ApiSecundariaService,
    ErroServicoSecundario,
)
from app.services.open_meteo_service import (
    DestinoNaoEncontrado,
    ErroOpenMeteo,
    OpenMeteoService,
)
from app.services.orquestrador_viagem_service import OrquestradorViagemService
from app.services.viagem_service import ViagemService

router = APIRouter(prefix="/viagens", tags=["Viagens"])
servico_viagens = ViagemService(
    ViagemRepository(os.getenv("DATABASE_PATH", "data/viagens.db"))
)
servico_open_meteo = OpenMeteoService()
orquestrador_viagens = OrquestradorViagemService(
    servico_viagens,
    servico_open_meteo,
    ApiSecundariaService(),
)


@router.post(
    "",
    response_model=ViagemResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_viagem(dados: ViagemEntrada) -> ViagemResposta:
    return servico_viagens.criar(dados)


@router.get("", response_model=list[ViagemResposta])
def listar_viagens() -> list[ViagemResposta]:
    return servico_viagens.listar()


@router.get("/{viagem_id}", response_model=ViagemDetalheResposta)
def obter_viagem(viagem_id: int) -> ViagemDetalheResposta:
    try:
        viagem = orquestrador_viagens.obter_detalhe(viagem_id)
    except DestinoNaoEncontrado as erro:
        raise HTTPException(
            status_code=404,
            detail="Origem ou destino não encontrado na busca de localidades.",
        ) from erro
    except (ErroOpenMeteo, ErroServicoSecundario) as erro:
        raise HTTPException(status_code=502, detail=str(erro)) from erro

    if viagem is None:
        raise HTTPException(status_code=404, detail="Viagem não encontrada.")
    return viagem


@router.put("/{viagem_id}", response_model=ViagemResposta)
def atualizar_viagem(
    viagem_id: int, dados: ViagemEntrada
) -> ViagemResposta:
    viagem = servico_viagens.atualizar(viagem_id, dados)
    if viagem is None:
        raise HTTPException(status_code=404, detail="Viagem não encontrada.")
    return viagem


@router.delete("/{viagem_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_viagem(viagem_id: int) -> Response:
    if not servico_viagens.deletar(viagem_id):
        raise HTTPException(status_code=404, detail="Viagem não encontrada.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{viagem_id}/previsao", response_model=PrevisaoResposta)
def obter_previsao(viagem_id: int) -> PrevisaoResposta:
    viagem = servico_viagens.obter(viagem_id)
    if viagem is None:
        raise HTTPException(status_code=404, detail="Viagem não encontrada.")

    try:
        return servico_open_meteo.obter_previsao(
            viagem.destino,
            viagem.data_inicio,
            viagem.data_fim,
        )
    except DestinoNaoEncontrado as erro:
        raise HTTPException(
            status_code=404,
            detail="Destino não encontrado na busca de localidades.",
        ) from erro
    except ErroOpenMeteo as erro:
        raise HTTPException(status_code=502, detail=str(erro)) from erro
