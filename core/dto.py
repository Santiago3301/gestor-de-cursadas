# DTO = Data Transfer Objects
# intermediario entre el modelo y la UI
# repositories los utilizan para coordinar las entidades
# basicamente es la recolección de estadísticas
from dataclasses import dataclass

from core.enums import EstadoMateriaEnum


@dataclass
class EstadisticasMateria:
    materia_id: int
    nombre: str

    promocionable: bool

    estado_actual: EstadoMateriaEnum

    total_tps: int
    total_tps_completados: int
    porcentaje_tps_completados: float
    total_entregas: int
    total_entregas_entregadas: int #xd
    total_evaluaciones: int
    total_evaluaciones_rendidas: int
    total_evaluaciones_aprobadas: int

    promedio_evaluaciones: float | None

# ----- ANALÍTICAS (GEMINI)

@dataclass
class ResumenCarrera:
    total_materias: int
    materias_aprobadas: int       # PROMOCIONADA + APROBADA
    materias_regulares: int
    materias_cursando: int
    promedio_general: float | None
    promedio_promocionadas: float | None
    promedio_finales: float | None
    porcentaje_avance: float

# ----- FIN ANALÍTICAS (GEMINI)
