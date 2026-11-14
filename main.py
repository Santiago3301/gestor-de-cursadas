from persistence.database import DatabaseManager
from persistence.repository import (
    EntregaRepository,
    EvaluacionRepository,
    MateriaRepository,
    PracticoRepository,
)
from services.cursada_service import GestionCursada
from ui.cli import menu


def main():
    db = DatabaseManager()
    db.inicializar_db()

    repo_materia = MateriaRepository(db)
    repo_practico = PracticoRepository(db)
    repo_entrega = EntregaRepository(db)
    repo_evaluacion = EvaluacionRepository(db)

    gestion_service = GestionCursada(
        repo_materia=repo_materia,
        repo_practico=repo_practico,
        repo_entrega=repo_entrega,
        repo_evaluacion=repo_evaluacion,
    )

    menu(gestion_service)

if __name__ == "__main__":
    main()
