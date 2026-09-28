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

## Testar as APIs com Docker

Crie uma rede Docker compartilhada e inicie primeiro a API secundária:

```bash
docker network create planejador-rede
docker run -d --name planejador-api-secundaria --network planejador-rede -p 8002:8001 planejador-viagens-secundaria
```

Depois, inicie a API principal na mesma rede:

```bash
docker run -d --name planejador-api-principal --network planejador-rede \
  -e API_SECUNDARIA_URL=http://planejador-api-secundaria:8001 \
  -p 8000:8000 \
  -v "$(pwd)/data:/app/data" \
  planejador-viagens-principal
```

O Swagger da principal fica em `http://localhost:8000/docs`. A porta 8002 expõe a secundária para facilitar testes; a principal comunica-se com ela pela rede Docker, usando a porta interna 8001.

## Executar com Docker

```bash
docker build -t planejador-viagens-principal .
```

O volume mantém o arquivo SQLite `viagens.db` no diretório `data` do computador.

## Rotas

- `POST /viagens` — cria uma viagem e retorna também distância, duração estimada e previsão do tempo.
- `GET /viagens` — lista as viagens com distância, duração estimada e previsão do tempo calculadas.
- `GET /viagens/{id}` — busca os dados no SQLite, obtém coordenadas e previsão no Open-Meteo, chama a API secundária para distância e duração e retorna uma resposta consolidada.
- `PUT /viagens/{id}` — substitui os dados da viagem.
- `DELETE /viagens/{id}` — remove uma viagem.
- `GET /viagens/{id}/previsao` — retorna separadamente a previsão diária formatada entre as datas da viagem.

Exemplo do corpo para criar ou atualizar:

```json
{
  "origem": "Rio de Janeiro",
  "destino": "São Paulo",
  "data_inicio": "2026-10-01",
  "data_fim": "2026-10-03",
  "meio_transporte": "carro"
}
```

Os endpoints `POST /viagens`, `GET /viagens` e `GET /viagens/{id}` incluem `distancia_km`, `duracao_estimada_horas` e a previsão diária em `previsao_tempo`, obtidos por orquestração da API principal. O cálculo de distância e duração é feito pela API secundária via REST. A previsão disponível é limitada ao horizonte de até 16 dias da Open-Meteo; escolha datas dentro desse horizonte para receber os dados previstos. Em registros antigos sem origem válida ou quando um serviço externo falhar, a listagem mantém os dados persistidos e informa `erro_calculo`, deixando os campos derivados como `null`.

Exemplo simplificado da resposta de detalhe:

```json
{
  "id": 1,
  "origem": "Rio de Janeiro",
  "destino": "São Paulo",
  "data_inicio": "2026-10-01",
  "data_fim": "2026-10-03",
  "meio_transporte": "carro",
  "distancia_km": 357.12,
  "duracao_estimada_horas": 3.57,
  "previsao_tempo": [
    {
      "data": "2026-10-01",
      "temperatura_maxima_c": 27,
      "temperatura_minima_c": 18,
      "precipitacao_mm": 2.4,
      "chance_chuva_percentual": 30
    }
  ]
}
```

Os valores meteorológicos acima são ilustrativos; a lista real terá um item para cada dia disponível no período solicitado.

## Arquitetura

As rotas/controllers, os modelos Pydantic, o serviço de previsão e o repositório SQLite estão separados em arquivos próprios.

<!-- Inserir aqui a imagem do fluxograma da arquitetura. -->
