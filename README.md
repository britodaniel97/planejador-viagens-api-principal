# API Principal - Planejador de Viagens

Serviço REST em FastAPI para criar, consultar, atualizar e remover viagens usando SQLite. Também consulta o geocoding e a previsão do tempo do Open-Meteo e devolve os dados em um formato simplificado.

## Instalação e execução

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

A documentação interativa fica em `http://localhost:8000/docs`.

## Executar com Docker

```bash
docker build -t planejador-viagens-principal .
docker run --rm -p 8000:8000 -v "$(pwd)/data:/app/data" planejador-viagens-principal
```

O volume mantém o arquivo SQLite `viagens.db` no diretório `data` do computador.

## Rotas

- `POST /viagens` — cria uma viagem com `destino`, `data_inicio` e `data_fim`.
- `GET /viagens` — lista as viagens.
- `GET /viagens/{id}` — consulta uma viagem.
- `PUT /viagens/{id}` — substitui os dados da viagem.
- `DELETE /viagens/{id}` — remove uma viagem.
- `GET /viagens/{id}/previsao` — procura o destino no Open-Meteo e retorna a previsão formatada, incluindo temperaturas, precipitação em milímetros e probabilidade de chuva.

Exemplo do corpo para criar ou atualizar:

```json
{
  "destino": "Rio de Janeiro",
  "data_inicio": "2026-12-01",
  "data_fim": "2026-12-07"
}
```

## Arquitetura

As rotas/controllers, os modelos Pydantic, o serviço de previsão e o repositório SQLite estão separados em arquivos próprios.

<!-- Inserir aqui a imagem do fluxograma da arquitetura. -->
