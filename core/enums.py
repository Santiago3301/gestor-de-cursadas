from enum import Enum

class CuatrimestreEnum(Enum):
    PRIMER_CUATRIMESTRE = "1C"
    SEGUNDO_CUATRIMESTRE = "2C"
    ANUAL = "ANUAL"

class EstadoMateriaEnum(Enum):
    CURSANDO = "CURSANDO"
    REGULAR = "REGULAR"
    APROBADA = "APROBADA"
    PROMOCIONADA = "PROMOCIONADA"
    LIBRE = "LIBRE"

class EstadoEntregaEnum(Enum):
    PENDIENTE = "PENDIENTE"
    ENTREGADO = "ENTREGADO"
    APROBADO = "APROBADO"
    DESAPROBADO = "DESAPROBADO"

class EstadoPracticoEnum(Enum):
    NO_INICIADO = "NO_INICIADO"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADO = "COMPLETADO"

class TipoEvaluacionEnum(Enum):
    PARCIAL = "PARCIAL"
    RECUPERATORIO = "RECUPERATORIO"
    COLOQUIO = "COLOQUIO"
    FINAL = "FINAL"