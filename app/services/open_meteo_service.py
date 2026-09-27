from datetime import date

import requests

from app.models.viagem import DiaPrevisao, PrevisaoResposta


class DestinoNaoEncontrado(Exception):
    pass


class ErroOpenMeteo(Exception):
    pass


class OpenMeteoService:
    _URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
    _URL_PREVISAO = "https://api.open-meteo.com/v1/forecast"

    def obter_previsao(self, destino: str) -> PrevisaoResposta:
        try:
            resposta_cidade = requests.get(
                self._URL_GEOCODING,
                params={"name": destino, "count": 1},
                timeout=10,
            )
            resposta_cidade.raise_for_status()
            resultados = resposta_cidade.json().get("results", [])
            if not resultados:
                raise DestinoNaoEncontrado

            cidade = resultados[0]
            resposta_tempo = requests.get(
                self._URL_PREVISAO,
                params={
                    "latitude": cidade["latitude"],
                    "longitude": cidade["longitude"],
                    "daily": (
                        "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                        "precipitation_probability_max"
                    ),
                    "timezone": "auto",
                },
                timeout=10,
            )
            resposta_tempo.raise_for_status()
            dados_diarios = resposta_tempo.json()["daily"]
            previsoes = [
                DiaPrevisao(
                    data=date.fromisoformat(dados_diarios["time"][indice]),
                    temperatura_maxima_c=dados_diarios["temperature_2m_max"][indice],
                    temperatura_minima_c=dados_diarios["temperature_2m_min"][indice],
                    precipitacao_mm=dados_diarios["precipitation_sum"][indice],
                    chance_chuva_percentual=dados_diarios[
                        "precipitation_probability_max"
                    ][indice],
                )
                for indice in range(len(dados_diarios["time"]))
            ]
            return PrevisaoResposta(destino=destino, previsao=previsoes)
        except DestinoNaoEncontrado:
            raise
        except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as erro:
            raise ErroOpenMeteo("Não foi possível obter a previsão do tempo.") from erro
