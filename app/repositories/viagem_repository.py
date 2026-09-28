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
                    meio_transporte TEXT NOT NULL
                )
                """
            )
            colunas_existentes = {
                coluna["name"]
                for coluna in conexao.execute("PRAGMA table_info(viagens)")
            }
            colunas_esperadas = {
                "id",
                "origem",
                "destino",
                "data_inicio",
                "data_fim",
                "meio_transporte",
            }
            if colunas_existentes != colunas_esperadas:
                self._migrar_tabela(conexao, colunas_existentes)

    @staticmethod
    def _migrar_tabela(
        conexao: sqlite3.Connection, colunas_existentes: set[str]
    ) -> None:
        colunas = (
            "id",
            "origem",
            "destino",
            "data_inicio",
            "data_fim",
            "meio_transporte",
        )
        valores_padrao = {
            "origem": "''",
            "destino": "''",
            "data_inicio": "''",
            "data_fim": "''",
            "meio_transporte": "'carro'",
        }
        selecoes = []
        for coluna in colunas:
            if coluna == "id":
                selecoes.append("id")
            elif coluna in colunas_existentes:
                selecoes.append(
                    f"COALESCE({coluna}, {valores_padrao[coluna]})"
                )
            else:
                selecoes.append(valores_padrao[coluna])
        conexao.execute("DROP TABLE IF EXISTS viagens_nova")
        conexao.execute(
            """
            CREATE TABLE viagens_nova (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origem TEXT NOT NULL,
                destino TEXT NOT NULL,
                data_inicio TEXT NOT NULL,
                data_fim TEXT NOT NULL,
                meio_transporte TEXT NOT NULL
            )
            """
        )
        conexao.execute(
            f"""
            INSERT INTO viagens_nova ({", ".join(colunas)})
            SELECT {", ".join(selecoes)} FROM viagens
            """
        )
        conexao.execute("DROP TABLE viagens")
        conexao.execute("ALTER TABLE viagens_nova RENAME TO viagens")

    @staticmethod
    def _para_resposta(registro: sqlite3.Row) -> ViagemResposta:
        return ViagemResposta.model_validate(dict(registro))

    def criar(self, viagem: ViagemEntrada) -> ViagemResposta:
        dados = viagem.model_dump()
        with self._conectar() as conexao:
            cursor = conexao.execute(
                """
                INSERT INTO viagens (
                    origem, destino, data_inicio, data_fim, meio_transporte
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    dados["origem"],
                    dados["destino"],
                    dados["data_inicio"].isoformat(),
                    dados["data_fim"].isoformat(),
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
                    meio_transporte = ?
                WHERE id = ?
                """,
                (
                    dados["origem"],
                    dados["destino"],
                    dados["data_inicio"].isoformat(),
                    dados["data_fim"].isoformat(),
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
