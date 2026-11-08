"""Persistência SQLite. Mantém o mesmo caminho e esquema da versão anterior."""
import os
import sqlite3
from pathlib import Path
from datetime import timedelta

APP_DIR = Path(os.environ.get("FLET_APP_STORAGE_DATA") or (Path.home() / ".organizador_semanal"))
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = APP_DIR / "tarefas.db"

def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dia TEXT NOT NULL,
        inicio INTEGER NOT NULL,
        fim INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        descricao TEXT NOT NULL DEFAULT '',
        cor TEXT NOT NULL DEFAULT 'Azul',
        concluida INTEGER NOT NULL DEFAULT 0,
        CHECK (inicio >= 0 AND fim <= 1440 AND inicio < fim)
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tarefas_dia ON tarefas(dia, inicio)")
    conn.commit()
    return conn

def carregar_semana(db, inicio_semana):
    inicio = inicio_semana.isoformat()
    fim = (inicio_semana + timedelta(days=6)).isoformat()
    return [dict(item) for item in db.execute(
        "SELECT * FROM tarefas WHERE dia BETWEEN ? AND ? ORDER BY dia, inicio",
        (inicio, fim),
    ).fetchall()]
