import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.models.viagem import ViagemEntrada, ViagemResposta


class ViagemRepository:
    def __init__(self, caminho_banco: str) -> None:
        self.caminho_banco = caminho_banco
        Path(caminho_banco).parent.mkdir(parents=True, exist_ok=True)
        self._criar_tabela()

    @contextmanager
    def _conectar(self) -> Iterator[sqlite3.Connection]:
        conexao = sqlite3.connect(self.caminho_banco)
        conexao.row_factory = sqlite3.Row
        try:
            with conexao:
                yield conexao
        finally:
            conexao.close()

    def _criar_tabela(self) -> None:
        with self._conectar() as conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS viagens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    origem TEXT NOT NULL,
                    destino TEXT NOT NULL,
                    data_inicio TEXT NOT NULL,
                    data_fim TEXT NOT NULL,
                    orcamento REAL NOT NULL,
                    meio_transporte TEXT NOT NULL
                )
                """
            )
            colunas_existentes = {
                coluna["name"]
                for coluna in conexao.execute("PRAGMA table_info(viagens)")
            }
            migracoes = {
                "origem": "TEXT NOT NULL DEFAULT ''",
                "orcamento": "REAL NOT NULL DEFAULT 0",
                "meio_transporte": "TEXT NOT NULL DEFAULT 'carro'",
            }
            for coluna, definicao in migracoes.items():
                if coluna not in colunas_existentes:
                    conexao.execute(
                        f"ALTER TABLE viagens ADD COLUMN {coluna} {definicao}"
                    )

    @staticmethod
    def _para_resposta(registro: sqlite3.Row) -> ViagemResposta:
        return ViagemResposta.model_validate(dict(registro))

    def criar(self, viagem: ViagemEntrada) -> ViagemResposta:
        dados = viagem.model_dump()
        with self._conectar() as conexao:
            cursor = conexao.execute(
                """
                INSERT INTO viagens (
                    origem, destino, data_inicio, data_fim, orcamento, meio_transporte
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    dados["origem"],
                    dados["destino"],
                    dados["data_inicio"].isoformat(),
                    dados["data_fim"].isoformat(),
                    dados["orcamento"],
                    dados["meio_transporte"],
                ),
            )
            registro = conexao.execute(
                "SELECT * FROM viagens WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return self._para_resposta(registro)

    def listar(self) -> list[ViagemResposta]:
        with self._conectar() as conexao:
            registros = conexao.execute(
                "SELECT * FROM viagens ORDER BY id"
            ).fetchall()
        return [self._para_resposta(registro) for registro in registros]

    def obter(self, viagem_id: int) -> ViagemResposta | None:
        with self._conectar() as conexao:
            registro = conexao.execute(
                "SELECT * FROM viagens WHERE id = ?", (viagem_id,)
            ).fetchone()
        return self._para_resposta(registro) if registro else None

    def atualizar(
        self, viagem_id: int, viagem: ViagemEntrada
    ) -> ViagemResposta | None:
        dados = viagem.model_dump()
        with self._conectar() as conexao:
            cursor = conexao.execute(
                """
                UPDATE viagens
                SET origem = ?, destino = ?, data_inicio = ?, data_fim = ?,
                    orcamento = ?, meio_transporte = ?
                WHERE id = ?
                """,
                (
                    dados["origem"],
                    dados["destino"],
                    dados["data_inicio"].isoformat(),
                    dados["data_fim"].isoformat(),
                    dados["orcamento"],
                    dados["meio_transporte"],
                    viagem_id,
                ),
            )
            if cursor.rowcount == 0:
                return None
            registro = conexao.execute(
                "SELECT * FROM viagens WHERE id = ?", (viagem_id,)
            ).fetchone()
        return self._para_resposta(registro)

    def deletar(self, viagem_id: int) -> bool:
        with self._conectar() as conexao:
            cursor = conexao.execute(
                "DELETE FROM viagens WHERE id = ?", (viagem_id,)
            )
        return cursor.rowcount > 0
