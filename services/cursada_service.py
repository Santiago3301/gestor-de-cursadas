from core.models import Materia, Practico, Evaluacion, Entrega
from core.enums import EstadoMateriaEnum, EstadoPracticoEnum, EstadoEntregaEnum, CuatrimestreEnum 
from core.dto import EstadisticasMateria
from persistence.repository import (
    MateriaRepository,
    EntregaRepository,
    PracticoRepository,
    EvaluacionRepository,
)

class AnalisisCursada:
    def __init__(
            self,
            repo_materia: MateriaRepository,
            repo_practico: PracticoRepository,
            repo_entrega: EntregaRepository,
            repo_evaluacion: EvaluacionRepository,
    ) -> None:
        self.repo_materia = repo_materia
        self.repo_practico = repo_practico
        self.repo_entrega = repo_entrega
        self.repo_evaluacion = repo_evaluacion

    def calcular_stats(self, materia_id: int) -> EstadisticasMateria | None:
        """Calcula las estadísticas de una materia dada por ID y retorna un objeto 'EstadisticasCursada'. Si la materia no se hayó, retorna None."""
        materia = self.repo_materia.obtener_por_id(materia_id)

        if not materia:
            return None

        pracs = self.repo_practico.listar_por_materia(materia_id)
        ents  = self.repo_entrega.listar_por_materia(materia_id)
        evals = self.repo_evaluacion.listar_por_materia(materia_id)

        total_tps = len(pracs)
        tps_completados = sum(
            1 for p in pracs if p.estado == EstadoPracticoEnum.COMPLETADO
        )
        porcentaje_tps_completados = self._calcular_porcentaje_avance(pracs)
        total_ents = len(ents)
        ents_entregadas = sum(
            1 for e in ents if e.estado == EstadoEntregaEnum.ENTREGADO or e.estado == EstadoEntregaEnum.APROBADO
        )
        total_evals = len(evals)
        evals_rendidas = sum(
            1 for e in evals if e.aprobado is not None
        )
        evals_aprobadas = sum(
            1 for e in evals if e.aprobado == True
        )

        promedio_evals = self._calcular_promedio_evals(evals)

        return EstadisticasMateria(
            materia_id,
            materia.nombre,
            materia.promocionable,
            materia.estado,
            total_tps,
            tps_completados,
            porcentaje_tps_completados,
            total_ents,
            ents_entregadas,
            total_evals,
            evals_rendidas,
            evals_aprobadas,
            promedio_evals,
        )

    def _calcular_promedio_evals(self, evals: list[Evaluacion]) -> float | None:
        recuperadas_ids = {
            ev.eval_recupera_id
            for ev in evals
            if ev.eval_recupera_id is not None
        }

        notas_validas = [
            ev.nota
            for ev in evals
            if ev.id not in recuperadas_ids and ev.nota is not None
        ]

        if not notas_validas:
            return None

        return round( sum(notas_validas) / len(notas_validas), 2)

    def _calcular_porcentaje_avance(self, pracs: list[Practico]) -> float:
        if not pracs:
            return 0.0
        completados = sum(
            1 for p in pracs if p.estado == EstadoPracticoEnum.COMPLETADO
        )
        return round( (completados/len(pracs)) * 100.0, 2)

class GestionMateria:
    def __init__(
            self,
            repo_materia: MateriaRepository,
            repo_practico: PracticoRepository,

    ) -> None:
        self.repo_materia = repo_materia
        self.repo_practico = repo_practico

    def cargar_materia(
            self,
            nombre: str,
            anio_plan: int,
            anio_cursada: int,
            cuatrimestre: CuatrimestreEnum,
            promocionable: bool,
    ) -> bool:
        """Permite cargar una materia desde la interfaz de usuario. Retorna True si la carga fue exitosa, False si no lo fue."""
        materia = Materia(
            nombre=nombre,
            anio_plan=anio_plan,
            anio_cursada=anio_cursada,
            cuatrimestre=cuatrimestre,
            promocionable=promocionable,
        )

        return self.repo_materia.guardar(materia) is not None

    def listar_materias(self) -> list[Materia]:
        return self.repo_materia.listar_todas()

    def listar_practicos_materia(self, materia_id: int):
        return self.repo_practico.listar_por_materia(materia_id)