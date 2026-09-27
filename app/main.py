from fastapi import FastAPI

from app.controllers.viagens import router as viagens_router

app = FastAPI(
    title="API Principal - Planejador de Viagens",
    description="API para cadastrar viagens e consultar a previsão do tempo.",
    version="1.0.0",
)

app.include_router(viagens_router)
