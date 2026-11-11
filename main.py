from persistence.database import DatabaseManager
from persistence.repository import (
    MateriaRepository, PracticoRepository, EntregaRepository, EvaluacionRepository
)
from services.cursada_service import GestionMateria, AnalisisCursada
from ui.cli import menu

def main():
    db = DatabaseManager()
    db.inicializar_db()

    repo_materia = MateriaRepository(db)
    repo_practico = PracticoRepository(db)

    gestion_service = GestionMateria(
        repo_materia=repo_materia,
        repo_practico=repo_practico,
    )

    menu(gestion_service)

if __name__ == "__main__":
    main()