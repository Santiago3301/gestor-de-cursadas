from datetime import date

from core.dto import EstadisticasMateria, ResumenCarrera
from core.enums import (
    CuatrimestreEnum,
    EstadoEntregaEnum,
    EstadoMateriaEnum,
    EstadoPracticoEnum,
    TipoEvaluacionEnum,
)
from core.models import Entrega, Evaluacion, Materia, Practico
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
        ents  = self.repo_entrega.listar_entregas(materia_id)
        evals = self.repo_evaluacion.listar_evaluaciones(materia_id)

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

# ----- ANALÍTICAS (GEMINI)

    def calcular_resumen_carrera(self, total_plan: int | None = None) -> ResumenCarrera:
            materias = self.repo_materia.listar_todas()
            aprobadas = [
                m for m in materias
                if m.estado in (EstadoMateriaEnum.PROMOCIONADA, EstadoMateriaEnum.APROBADA)
            ]
            regulares = [m for m in materias if m.estado == EstadoMateriaEnum.REGULAR]
            cursando = [m for m in materias if m.estado == EstadoMateriaEnum.CURSANDO]

            notas_todas = [m.nota_final for m in aprobadas if m.nota_final is not None]
            notas_prom = [
                m.nota_final for m in aprobadas
                if m.estado == EstadoMateriaEnum.PROMOCIONADA and m.nota_final is not None
            ]
            notas_final = [
                m.nota_final for m in aprobadas
                if m.estado == EstadoMateriaEnum.APROBADA and m.nota_final is not None
            ]

            base_avance = total_plan if total_plan and total_plan > 0 else len(materias)
            avance = round((len(aprobadas) / base_avance) * 100, 2) if base_avance > 0 else 0.0

            return ResumenCarrera(
                total_materias=len(materias),
                materias_aprobadas=len(aprobadas),
                materias_regulares=len(regulares),
                materias_cursando=len(cursando),
                promedio_general=round(sum(notas_todas) / len(notas_todas), 2) if notas_todas else None,
                promedio_promocionadas=round(sum(notas_prom) / len(notas_prom), 2) if notas_prom else None,
                promedio_finales=round(sum(notas_final) / len(notas_final), 2) if notas_final else None,
                porcentaje_avance=avance,
            )


# ----- FIN ANALÍTICAS (GEMINI)

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
        estado: EstadoMateriaEnum | None = None,
        nota_final: float | None = None
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

        if nota_final is not None:
            materia.nota_final = nota_final

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
            titulo=titulo.strip(),
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
        """Listar practicos almacenados filtrando por sus atributos y opcionalmente por materia. Ejemplo: listar_practicos(estado=EstadoPracticoEnum.COMPLETADO). Si se llama sin parámetros, retorna todos los prácticos cargados."""
        return self.repo_practico.listar_practicos(materia_id, estado)

class GestionEntrega:
    def __init__(
        self,
        repo_entrega: EntregaRepository,
        repo_materia: MateriaRepository,
        repo_practico: PracticoRepository,
    ) -> None:
        self.repo_entrega = repo_entrega
        self.repo_materia = repo_materia
        self.repo_practico = repo_practico

    def obtener_entrega(self, ent_id: int) -> Entrega | None:
        return self.repo_entrega.obtener_por_id(ent_id)

    def cargar_entrega(
        self,
        materia_id: int,
        numero: int,
        titulo: str,
        fecha_entrega: date,
        estado: EstadoEntregaEnum,
        practico_id: int | None = None,
        nota: float | None = None,
    ) -> bool:
        """Permite cargar una entrega desde la interfaz de usuario. Retorna true si la carga fue exitosa, False si no lo fue."""
        if self.repo_materia.obtener_por_id(materia_id) is None:
            return False
        if practico_id is not None:
            practico = self.repo_practico.obtener_por_id(practico_id=practico_id)
            if practico is None or practico.materia_id != materia_id:
                return False
        entrega = Entrega(
            materia_id=materia_id,
            numero=numero,
            titulo=titulo.strip(),
            fecha_entrega=fecha_entrega,
            estado=estado,
            practico_id=practico_id,
            nota=nota,
        )
        return self.repo_entrega.guardar(entrega=entrega) is not None

    def eliminar_entrega(self, entrega_id: int):
        """Eliminar una entrega dado un ID. Retorna True si se eliminó correctamente, False si no se encontró el práctico."""
        return self.repo_entrega.eliminar(entrega_id=entrega_id)

    def actualizar_entrega(
        self,
        entrega_id: int,
        numero: int | None = None,
        titulo: str | None = None,
        fecha_entrega: date | None = None,
        estado: EstadoEntregaEnum | None = None,
        nota: float | None = None,
    ) -> bool:
        """Permite cambiar uno o mas de los atributos de una entrega, excepto cambiarlo de materia. Ejemplo: cambiar estado de PENDIENTE a ENTREGADO."""
        entrega = self.obtener_entrega(ent_id=entrega_id)
        if entrega is None:
            return False
        if titulo is not None:
            entrega.titulo=titulo.strip()
        if numero is not None:
            entrega.numero=numero
        if fecha_entrega is not None:
            entrega.fecha_entrega=fecha_entrega
        if estado is not None:
            entrega.estado=estado
        if nota is not None:
            entrega.nota=nota

        return self.repo_entrega.guardar(entrega=entrega) is not None

    def listar_entregas(
        self,
        materia_id: int | None = None,
        practico_id: int | None = None,
        estado: EstadoEntregaEnum | None = None,
        solo_pendientes: bool = False,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Entrega]:
        """Listar entregas almacenadas filtrando por sus atributos y opcionalmente por materia. Ejemplo: listar_entregas(estado=EstadoEntregaEnum.APROBADA). Si se llama sin parámetros, retorna todos los prácticos cargados."""
        return self.repo_entrega.listar_entregas(
            materia_id,
            practico_id,
            estado,
            solo_pendientes,
            fecha_desde,
            fecha_hasta
        )

class GestionEvaluacion:
    def __init__(
        self,
        repo_evaluacion: EvaluacionRepository,
        repo_materia: MateriaRepository
    ) -> None:
        self.repo_evaluacion = repo_evaluacion
        self.repo_materia = repo_materia

    def obtener_evaluacion(self, evaluacion_id: int) -> Evaluacion | None:
        return self.repo_evaluacion.obtener_por_id(evaluacion_id)

    def cargar_evaluacion(
        self,
        materia_id: int,
        titulo: str,
        numero: int,
        fecha: date,
        tipo: TipoEvaluacionEnum,
        aprobado: bool | None = None,
        nota: float | None = None,
        eval_recupera_id: int | None = None
    ) -> bool:
        """Permite cargar una evaluacion desde la interfaz de usuario. Retorna true si la carga fue exitosa, False si no lo fue."""
        if eval_recupera_id is not None:
            eval_recup = self.obtener_evaluacion(eval_recupera_id)
            if eval_recup is None or eval_recup.materia_id != materia_id:
                return False
        if self.repo_materia.obtener_por_id(materia_id=materia_id) is None:
            return False
        evaluacion = Evaluacion(
            materia_id=materia_id,
            titulo=titulo.strip(),
            numero=numero,
            fecha=fecha,
            tipo=tipo,
            aprobado=aprobado,
            nota=nota,
            eval_recupera_id=eval_recupera_id
        )

        return self.repo_evaluacion.guardar(evaluacion) is not None

    def eliminar_evaluacion(self, evaluacion_id: int):
        """Eliminar una evaluacion dado un ID. Retorna True si se eliminó correctamente, False si no se encontró el práctico."""
        return self.repo_evaluacion.eliminar(evaluacion_id=evaluacion_id)

    def actualizar_evaluacion(
        self,
        evaluacion_id: int,
        numero: int | None = None,
        titulo: str | None = None,
        fecha: date | None = None,
        tipo: TipoEvaluacionEnum | None = None,
        aprobado: bool | None = None,
        nota: float | None = None,
        eval_recupera_id: int | None = None

    ) -> bool:
        """Permite cambiar uno o mas de los atributos de una evaluacion, excepto cambiarlo de materia. Ejemplo: cambiar estado de PENDIENTE a ENTREGADO."""
        evaluacion = self.obtener_evaluacion(evaluacion_id=evaluacion_id)
        if evaluacion is None:
            return False
        if numero is not None:
            evaluacion.numero = numero
        if titulo is not None:
            evaluacion.titulo = titulo.strip()
        if fecha is not None:
            evaluacion.fecha = fecha
        if tipo is not None:
            evaluacion.tipo = tipo
        if aprobado is not None:
            evaluacion.aprobado = aprobado
        if nota is not None:
            evaluacion.nota = nota
        if eval_recupera_id is not None:
            eval_recup = self.obtener_evaluacion(eval_recupera_id)
            if eval_recup is None or eval_recup.materia_id != evaluacion.materia_id:
                return False
            else:
                evaluacion.eval_recupera_id = eval_recupera_id

        return self.repo_evaluacion.guardar(evaluacion=evaluacion) is not None

    def listar_evaluaciones(
        self,
        materia_id: int | None = None,
        tipo: TipoEvaluacionEnum | None = None,
        aprobado: bool | None = None,
        solo_pendientes: bool = False,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Evaluacion]:
        """Listar evaluaciones almacenadas filtrando por sus atributos y opcionalmente por materia. Ejemplo: listar_evaluaciones(tipo=TipoEvaluacionEnum.FINAL). Si se llama sin parámetros, retorna todos los prácticos cargados."""
        return self.repo_evaluacion.listar_evaluaciones(
            materia_id=materia_id,
            tipo=tipo,
            aprobado=aprobado,
            solo_pendientes=solo_pendientes,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )
