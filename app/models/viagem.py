from datetime import date
from typing import Literal

from pydantic import BaseModel


class ViagemEntrada(BaseModel):
    origem: str
    destino: str
    data_inicio: date
    data_fim: date
    orcamento: float
    meio_transporte: Literal["carro", "onibus", "aviao"]


class ViagemResposta(ViagemEntrada):
    id: int


class Coordenadas(BaseModel):
    latitude: float
    longitude: float


class DiaPrevisao(BaseModel):
    data: date
    temperatura_maxima_c: float
    temperatura_minima_c: float
    precipitacao_mm: float
    chance_chuva_percentual: int


class PrevisaoResposta(BaseModel):
    destino: str
    previsao: list[DiaPrevisao]


class ViagemDetalheResposta(ViagemResposta):
    distancia_km: float
    duracao_estimada_horas: float
    previsao_tempo: list[DiaPrevisao]
