from datetime import date

import requests

from app.models.viagem import Coordenadas, DiaPrevisao, PrevisaoResposta


class DestinoNaoEncontrado(Exception):
    pass


class ErroOpenMeteo(Exception):
    pass


class OpenMeteoService:
    _URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
    _URL_PREVISAO = "https://api.open-meteo.com/v1/forecast"

    def obter_coordenadas(self, cidade: str) -> Coordenadas:
        try:
            resposta_cidade = requests.get(
                self._URL_GEOCODING,
                params={"name": cidade, "count": 1},
                timeout=10,
            )
            resposta_cidade.raise_for_status()
            resultados = resposta_cidade.json().get("results", [])
            if not resultados:
                raise DestinoNaoEncontrado

            cidade = resultados[0]
            return Coordenadas(
                latitude=cidade["latitude"],
                longitude=cidade["longitude"],
            )
        except DestinoNaoEncontrado:
            raise
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as erro:
            raise ErroOpenMeteo(
                "Não foi possível obter as coordenadas da localidade."
            ) from erro

    def obter_previsao(
        self, destino: str, data_inicio: date, data_fim: date
    ) -> PrevisaoResposta:
        coordenadas = self.obter_coordenadas(destino)
        return self.obter_previsao_por_coordenadas(
            destino, coordenadas, data_inicio, data_fim
        )

    def obter_previsao_por_coordenadas(
        self,
        destino: str,
        coordenadas: Coordenadas,
        data_inicio: date,
        data_fim: date,
    ) -> PrevisaoResposta:
        try:
            resposta_tempo = requests.get(
                self._URL_PREVISAO,
                params={
                    "latitude": coordenadas.latitude,
                    "longitude": coordenadas.longitude,
                    "daily": (
                        "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                        "precipitation_probability_max"
                    ),
                    "timezone": "auto",
                    "forecast_days": 16,
                },
                timeout=10,
            )
            resposta_tempo.raise_for_status()
            dados_diarios = resposta_tempo.json()["daily"]
            previsoes = []
            for indice, data_texto in enumerate(dados_diarios["time"]):
                data_previsao = date.fromisoformat(data_texto)
                if data_inicio <= data_previsao <= data_fim:
                    previsoes.append(
                        DiaPrevisao(
                            data=data_previsao,
                            temperatura_maxima_c=dados_diarios[
                                "temperature_2m_max"
                            ][indice],
                            temperatura_minima_c=dados_diarios[
                                "temperature_2m_min"
                            ][indice],
                            precipitacao_mm=dados_diarios["precipitation_sum"][
                                indice
                            ],
                            chance_chuva_percentual=dados_diarios[
                                "precipitation_probability_max"
                            ][indice],
                        )
                    )
            return PrevisaoResposta(destino=destino, previsao=previsoes)
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as erro:
            raise ErroOpenMeteo(
                "Não foi possível obter a previsão do tempo."
            ) from erro
