from app.models.viagem import ViagemDetalheResposta
from app.services.api_secundaria_service import ApiSecundariaService
from app.services.open_meteo_service import OpenMeteoService
from app.services.viagem_service import ViagemService


class OrquestradorViagemService:
    def __init__(
        self,
        servico_viagens: ViagemService,
        servico_open_meteo: OpenMeteoService,
        servico_api_secundaria: ApiSecundariaService,
    ) -> None:
        self.servico_viagens = servico_viagens
        self.servico_open_meteo = servico_open_meteo
        self.servico_api_secundaria = servico_api_secundaria

    def obter_detalhe(self, viagem_id: int) -> ViagemDetalheResposta | None:
        viagem = self.servico_viagens.obter(viagem_id)
        if viagem is None:
            return None

        coordenadas_origem = self.servico_open_meteo.obter_coordenadas(
            viagem.origem
        )
        coordenadas_destino = self.servico_open_meteo.obter_coordenadas(
            viagem.destino
        )
        distancia_km = self.servico_api_secundaria.calcular_distancia(
            coordenadas_origem, coordenadas_destino
        )
        duracao_horas = self.servico_api_secundaria.calcular_duracao(
            distancia_km, viagem.meio_transporte
        )
        previsao = self.servico_open_meteo.obter_previsao_por_coordenadas(
            viagem.destino,
            coordenadas_destino,
            viagem.data_inicio,
            viagem.data_fim,
        )

        return ViagemDetalheResposta(
            **viagem.model_dump(),
            distancia_km=distancia_km,
            duracao_estimada_horas=duracao_horas,
            previsao_tempo=previsao.previsao,
        )
