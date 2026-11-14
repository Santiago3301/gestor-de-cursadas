from core.dto import EstadisticasMateria
from core.enums import (
    CuatrimestreEnum,
    EstadoEntregaEnum,
    EstadoMateriaEnum,
    EstadoPracticoEnum,
)
from core.models import Evaluacion, Materia, Practico
from persistence.repository import (
    EntregaRepository,
    EvaluacionRepository,
    MateriaRepository,
    PracticoRepository,
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

        pracs = self.repo_practico.listar_practicos(materia_id)
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
            1 for e in evals if e.aprobado is True
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
    ) -> None:
        self.repo_materia = repo_materia

    def obtener_materia(self, materia_id: int) -> Materia | None:
        return self.repo_materia.obtener_por_id(materia_id=materia_id)

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
            nombre=nombre.strip(),
            anio_plan=anio_plan,
            anio_cursada=anio_cursada,
            cuatrimestre=cuatrimestre,
            promocionable=promocionable,
        )
        return self.repo_materia.guardar(materia) is not None

    def eliminar_materia(
        self,
        materia_id: int
    ) -> bool:
        """Eliminar una materia dado un ID. Retorna True si se eliminó correctamente, False si no se encontró la materia."""
        return self.repo_materia.eliminar(materia_id=materia_id)

    def actualizar_materia(
        self,
        materia_id: int,
        nombre: str | None = None,
        anio_plan: int | None = None,
        anio_cursada: int | None = None,
        cuatrimestre: CuatrimestreEnum | None = None,
        promocionable: bool | None = None,
        estado: EstadoMateriaEnum | None = None
    ) -> bool:
        """Permite cambiar uno o mas de los atributos de una materia. Ejemplo: cambiar estado de CURSANDO a APROBADA."""
        materia = self.obtener_materia(materia_id)
        if materia is None:
            return False

        if nombre is not None:
            materia.nombre = nombre.strip()

        if anio_plan is not None:
            materia.anio_plan = anio_plan

        if anio_cursada is not None:
            materia.anio_cursada = anio_cursada

        if cuatrimestre is not None:
            materia.cuatrimestre = cuatrimestre

        if promocionable is not None:
            materia.promocionable = promocionable

        if estado is not None:
            materia.estado = estado

        return self.repo_materia.guardar(materia) is not None

    def listar_materias(
        self,
        anio_plan: int | None = None,
        anio_cursada: int | None = None,
        cuatrimestre: CuatrimestreEnum | None = None,
        promocionable: bool | None = None,
        estado: EstadoMateriaEnum | None = None,
    ) -> list[Materia]:
        """Listar las materias almacenadas. Permite filtrar por sus atributos. Ejemplo: listar_materias(estado=EstadoMateriaEnum.PROMOCIONADA). Si se llama sin parámetros, retorna todas las materias cargadas."""
        materias = self.repo_materia.listar_todas()
        if anio_plan is not None:
            materias = [m for m in materias if m.anio_plan == anio_plan]
        if anio_cursada is not None:
            materias = [m for m in materias if m.anio_cursada == anio_cursada]
        if cuatrimestre is not None:
            materias = [m for m in materias if m.cuatrimestre == cuatrimestre]
        if promocionable is not None:
            materias = [m for m in materias if m.promocionable == promocionable]
        if estado is not None:
            materias = [m for m in materias if m.estado == estado]
        return materias

class GestionPractico:
    def __init__(
        self,
        repo_practico: PracticoRepository,
        repo_materia: MateriaRepository,
    ) -> None:
        self.repo_practico = repo_practico
        self.repo_materia = repo_materia

    def obtener_practico(self, id: int) -> Practico | None:
        return self.repo_practico.obtener_por_id(id)

    def cargar_practico(
        self,
        materia_id: int,
        numero: int,
        titulo: str,
        estado: EstadoPracticoEnum
    ) -> bool:
        """Permite cargar un practico desde la interfaz de usuario. Retorna true si la carga fue exitosa, False si no lo fue."""
        if self.repo_materia.obtener_por_id(materia_id) is None:
            return False
        practico = Practico(
            materia_id=materia_id,
            numero=numero,
            titulo=titulo,
            estado=estado
        )
        return self.repo_practico.guardar(practico=practico) is not None

    def eliminar_practico(self, practico_id: int):
        """Eliminar un practico dado un ID. Retorna True si se eliminó correctamente, False si no se encontró el práctico."""
        return self.repo_practico.eliminar(practico_id=practico_id)

    def actualizar_practico(
        self,
        practico_id: int,
        titulo: str | None = None,
        numero: int | None = None,
        estado: EstadoPracticoEnum | None = None
    ) -> bool:
        """Permite cambiar uno o mas de los atributos de un práctico, excepto cambiarlo de materia. Ejemplo: cambiar estado de EN_PROCESO a COMPLETADO."""

        practico = self.obtener_practico(id=practico_id)

        if practico is None:
            return False
        if titulo is not None:
            practico.titulo= titulo.strip()
        if numero is not None:
            practico.numero = numero
        if estado is not None:
            practico.estado = estado

        return self.repo_practico.guardar(practico=practico) is not None

    def listar_practicos(
        self,
        materia_id: int | None = None,
        estado: EstadoPracticoEnum | None = None,
    ) -> list[Practico]:
        """Listar practico almacenados filtrando por sus atributos y opcionalmente por materia. Ejemplo: listar_practicos(estado=EstadoPracticoEnum.COMPLETADO). Si se llama sin parámetros, retorna todos los prácticos cargados."""
        return self.repo_practico.listar_practicos(materia_id, estado)

class GestionEntrega:
    def __init__(
        self,
        repo_entrega: EntregaRepository,
    ) -> None:
        self.repo_entrega = repo_entrega

class GestionEvaluacion:
    def __init__(
        self,
        repo_evaluacion: EvaluacionRepository,
    ) -> None:
        self.repo_evaluacion = repo_evaluacion
