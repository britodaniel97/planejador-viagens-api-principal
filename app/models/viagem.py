from datetime import date

from pydantic import BaseModel


class ViagemEntrada(BaseModel):
    destino: str
    data_inicio: date
    data_fim: date


class ViagemResposta(ViagemEntrada):
    id: int


class DiaPrevisao(BaseModel):
    data: date
    temperatura_maxima_c: float
    temperatura_minima_c: float
    precipitacao_mm: float
    chance_chuva_percentual: int


class PrevisaoResposta(BaseModel):
    destino: str
    previsao: list[DiaPrevisao]
