from dataclasses import dataclass, field
from datetime import date
from core.enums import (
    CuatrimestreEnum,
    EstadoMateriaEnum,
    EstadoEntregaEnum,
    EstadoPracticoEnum,
    TipoEvaluacionEnum
)

@dataclass
class Practico:
    materia_id: int
    numero: int
    titulo: str
    estado: EstadoPracticoEnum = EstadoPracticoEnum.NO_INICIADO

    id: int | None = None

@dataclass
class Entrega:
    materia_id: int
    numero: int
    titulo: str
    fecha_entrega: date
    estado: EstadoEntregaEnum = EstadoEntregaEnum.PENDIENTE

    id: int | None = None
    practico_id: int | None = None
    nota: float | None = None

@dataclass
class Evaluacion:
    materia_id: int
    titulo: str
    numero: int
    fecha: date
    tipo: TipoEvaluacionEnum
    aprobado: bool
    
    id: int | None = None
    nota: float | None = None
    eval_recupera_id : int | None = None

@dataclass
class Materia:
    nombre: str
    anio_plan: int
    anio_cursada: int
    cuatrimestre: CuatrimestreEnum
    promocionable: bool

    id: int | None = None
    estado: EstadoMateriaEnum = EstadoMateriaEnum.CURSANDO
    # las materias se asocian con practicos, entregas y evaluaciones
    practicos: list[Practico] = field(default_factory=list)
    entregas: list[Entrega] = field(default_factory=list)
    evaluaciones: list[Evaluacion] = field(default_factory=list)

    def get_practicos(self):
        return self.practicos

    def calcular_avance(self):
        if not self.practicos:
            return 0.0
        completados = sum(
            1 for p in self.practicos if p.estado == EstadoPracticoEnum.COMPLETADO
        )
        return round((completados / len(self.practicos)) * 100.0, 2)

    def calcular_promedio(self) -> float:
        recuperadas_ids = {
            ev.eval_recupera_id
            for ev in self.evaluaciones
            if ev.eval_recupera_id is not None
        }

        notas_validas = [
            ev.nota
            for ev in self.evaluaciones
            if ev.id not in recuperadas_ids and ev.nota is not None
        ]

        if not notas_validas:
            return 0.0

        return round( sum(notas_validas) / len(notas_validas) , 2)

