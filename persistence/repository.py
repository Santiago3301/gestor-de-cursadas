import sqlite3
from datetime import date
from core.enums import (
    CuatrimestreEnum,
    EstadoMateriaEnum,
    EstadoEntregaEnum,
    EstadoPracticoEnum,
    TipoEvaluacionEnum,
)

from core.models import Materia, Practico, Entrega, Evaluacion
from persistence.database import DatabaseManager

class MateriaRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _insertar(self, materia: Materia) -> Materia:
        query = """
            INSERT INTO materias (
                nombre, anio_plan, anio_cursada, cuatrimestre, promocionable, estado
            ) VALUES (?,?,?,?,?,?)
            """

        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute(
                    query,
                    (
                        materia.nombre,
                        materia.anio_plan,
                        materia.anio_cursada,
                        materia.cuatrimestre.value,
                        1 if materia.promocionable else 0,
                        materia.estado.value
                    ),
                )
                materia.id = cursor.lastrowid
            return materia
        except sqlite3.IntegrityError:
            # violacion de la restriccion de UNIQUE (nombre, anio_cursada, cuatrimestre)
            return None

    def _actualizar(self, materia: Materia) -> Materia:
        query = """
            UPDATE materias
            SET nombre = ?, anio_plan = ?, anio_cursada = ?, cuatrimestre = ?,
            promocionable = ?, estado = ?
            WHERE id = ?
        """

        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    materia.nombre,
                    materia.anio_plan,
                    materia.anio_cursada,
                    materia.cuatrimestre.value,
                    1 if materia.promocionable else 0,
                    materia.estado.value,
                    materia.id,
                ),
            )
        return materia

    def guardar(self, materia: Materia) -> Materia:
        """ insertar una materia nueva o actualizar existente """
        if materia.id is None:
            return self._insertar(materia)
        else:
            return self._actualizar(materia)

    def obtener_por_id(self, materia_id: int) -> Materia | None:
        """ obtener la materia junto con sus practicos, entregas y evals """
        query_materia = "SELECT * FROM materias WHERE id = ?"

        with self.db.get() as conn:
            row = conn.execute(query_materia, (materia_id,)).fetchone()
            if not row:
                return None

            materia = Materia(
                id=row["id"],
                nombre=row["nombre"],
                anio_plan=row["anio_plan"],
                anio_cursada=row["anio_cursada"],
                cuatrimestre=CuatrimestreEnum(row["cuatrimestre"]),
                promocionable=bool(row["promocionable"]),
                estado=EstadoMateriaEnum(row["estado"]),
            )

            # cargar practicos asociados

            cur_p = conn.execute(
                "SELECT * FROM practicos WHERE materia_id = ? ORDER BY numero ASC",
                (materia_id)
            )

            materia.practicos = [
                Practico(
                    id=p["id"],
                    materia_id=p["materia_id"],
                    numero=p["numero"],
                    titulo=p["titulo"],
                    estado=EstadoPracticoEnum(p["estado"])
                )
                for p in cur_p.fetchall()
            ]

            # cargar entregas asociadas
            cur_ent = conn.execute(
                "SELECT * FROM entregas WHERE materia_id = ? ORDER BY numero ASC",
                (materia_id)
            )

            materia.entregas = [
                Entrega(
                    id=e["id"],
                    materia_id=e["materia_id"],
                    numero=e["numero"],
                    titulo=e["titulo"],
                    fecha_entrega=date.fromisoformat(e["fecha_entrega"]),
                    estado=EstadoEntregaEnum(e["estado"]),
                    practico_id=e["practico_id"],
                    nota=e["nota"]
                )
                for e in cur_ent.fetchall()
            ]

            # cargar evaluaciones asociadas
            cur_ev = conn.execute(
                "SELECT * FROM evaluaciones WHERE materia_id = ? ORDER BY numero ASC",
                (materia_id,)
            )

            materia.evaluaciones = [
                Evaluacion(
                    id=e["id"],
                    titulo=e["titulo"],
                    numero=e["numero"],
                    fecha=date.fromisoformat(e["fecha"]),
                    tipo=TipoEvaluacionEnum(e["tipo"]),
                    aprobado=bool(e["aprobado"]),
                    nota=e["nota"],
                    eval_recupera_id=e["eval_recupera_id"]
                )
                for e in cur_ev.fetchall()
            ]

            return materia

    def listar_todas(self) -> list[Materia]:
        """Devuelve todas las materias registradas (resumen básico sin cargar colecciones)."""
        query = "SELECT * FROM materias ORDER BY anio_cursada DESC, cuatrimestre ASC, nombre ASC"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [
                Materia(
                    id=r["id"],
                    nombre=r["nombre"],
                    anio_plan=r["anio_plan"],
                    anio_cursada=r["anio_cursada"],
                    cuatrimestre=CuatrimestreEnum(r["cuatrimestre"]),
                    promocionable=bool(r["promocionable"]),                        estado=EstadoMateriaEnum(r["estado"])
                )
                for r in rows
            ]