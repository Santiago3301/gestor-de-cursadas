import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "cursadas.db"
SCHEMA_PATH = BASE_DIR / "persistence" / "schema.sql"

class DatabaseManager:
    def __init__(self, db_path: Path | str = DB_PATH):
        self.db_path = Path(db_path)
        # aseguro que exista el directorio data
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        # habilitar acceso por nombre de columna
        conn.row_factory = sqlite3.Row
        # activar foreign keys
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def inicializar_db(self):
        """ ejecuta schema.sql para crear las tablas si no existen """
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            script_ddl = f.read()

        with self.get_connection() as conn:
            conn.executescript(script_ddl)