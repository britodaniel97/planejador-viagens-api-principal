import os

import requests
from pydantic import ValidationError

from app.models.servicos import DistanciaResposta, DuracaoResposta
from app.models.viagem import Coordenadas


class ErroServicoSecundario(Exception):
    pass


class ApiSecundariaService:
    def __init__(self, url_base: str | None = None) -> None:
        self.url_base = (
            url_base or os.getenv("API_SECUNDARIA_URL", "http://localhost:8001")
        ).rstrip("/")

    def calcular_distancia(
        self, origem: Coordenadas, destino: Coordenadas
    ) -> float:
        try:
            resposta = requests.post(
                f"{self.url_base}/distancia",
                json={
                    "origem_lat": origem.latitude,
                    "origem_lon": origem.longitude,
                    "destino_lat": destino.latitude,
                    "destino_lon": destino.longitude,
                },
                timeout=10,
            )
            resposta.raise_for_status()
            return DistanciaResposta.model_validate(resposta.json()).distancia_km
        except (requests.RequestException, ValidationError, ValueError) as erro:
            raise ErroServicoSecundario(
                "Não foi possível calcular a distância pela API secundária."
            ) from erro

    def calcular_duracao(
        self, distancia_km: float, meio_transporte: str
    ) -> float:
        try:
            resposta = requests.post(
                f"{self.url_base}/duracao-estimada",
                json={
                    "distancia_km": distancia_km,
                    "meio_transporte": meio_transporte,
                },
                timeout=10,
            )
            resposta.raise_for_status()
            return DuracaoResposta.model_validate(resposta.json()).duracao_horas
        except (requests.RequestException, ValidationError, ValueError) as erro:
            raise ErroServicoSecundario(
                "Não foi possível calcular a duração pela API secundária."
            ) from erro
