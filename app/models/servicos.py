from pydantic import BaseModel


class DistanciaResposta(BaseModel):
    distancia_km: float


class DuracaoResposta(BaseModel):
    duracao_horas: float
