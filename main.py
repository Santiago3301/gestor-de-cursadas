from persistence.database import DatabaseManager
from persistence.repository import (
    EntregaRepository,
    EvaluacionRepository,
    MateriaRepository,
    PracticoRepository,
)
from services.cursada_service import (
    AnalisisCursada,
    GestionEntrega,
    GestionEvaluacion,
    GestionMateria,
    GestionPractico,
)
from ui.cli import menu


def main():
    db = DatabaseManager()
    db.inicializar_db()

    repo_materia = MateriaRepository(db)
    repo_practico = PracticoRepository(db)
    repo_entrega = EntregaRepository(db)
    repo_evaluacion = EvaluacionRepository(db)

    gestion_mat= GestionMateria(
        repo_materia=repo_materia,
    )
    gestion_prac= GestionPractico(
        repo_practico=repo_practico,
        repo_materia=repo_materia,
    )

    gestion_ent= GestionEntrega(
            repo_entrega=repo_entrega,
            repo_materia=repo_materia,
            repo_practico=repo_practico
        )
    gestion_ev= GestionEvaluacion(
        repo_evaluacion=repo_evaluacion,
        repo_materia=repo_materia,
    )


    analisis = AnalisisCursada(
        repo_entrega=repo_entrega,
        repo_evaluacion=repo_evaluacion,
        repo_materia=repo_materia,
        repo_practico=repo_practico,
    )

    menu(
        analisis_cursada=analisis,
        gestor_materia=gestion_mat,
        gestor_practico=gestion_prac,
        gestor_entrega=gestion_ent,
        gestor_evaluacion=gestion_ev,
    )

if __name__ == "__main__":
    main()
