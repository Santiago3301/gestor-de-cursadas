import sqlite3
from datetime import date

from core.enums import (
    CuatrimestreEnum,
    EstadoEntregaEnum,
    EstadoMateriaEnum,
    EstadoPracticoEnum,
    TipoEvaluacionEnum,
)
from core.models import Entrega, Evaluacion, Materia, Practico

from .database import DatabaseManager


class MateriaRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _insertar(self, materia: Materia) -> Materia | None:
        query = """
            INSERT INTO materias (
                nombre, anio_plan, anio_cursada, cuatrimestre, promocionable, estado, nota_final
            ) VALUES (?,?,?,?,?,?,?)
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
                        materia.estado.value,
                        materia.nota_final,
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
            promocionable = ?, estado = ?, nota_final = ?
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
                    materia.nota_final,
                    materia.id,
                ),
            )
        return materia

    def guardar(self, materia: Materia) -> Materia | None:
        """Insertar una materia nueva o actualizar existente."""
        if materia.id is None:
            return self._insertar(materia)
        else:
            return self._actualizar(materia)

    def eliminar(self, materia_id: int) -> bool:
        """Elimina una materia por su ID. Retorna True si existía y se eliminó, False si no existía."""
        query = "DELETE FROM materias WHERE id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (materia_id,))
            return cursor.rowcount > 0

    def obtener_por_id(self, materia_id: int) -> Materia | None:
        """Obtener la materia junto con sus practicos, entregas y evals """
        query_materia = "SELECT * FROM materias WHERE id = ?"

        with self.db.get_connection() as conn:
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
                nota_final=row["nota_final"],
            )

            # cargar practicos asociados

            cur_p = conn.execute(
                "SELECT * FROM practicos WHERE materia_id = ? ORDER BY numero ASC",
                (materia_id,)
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
                (materia_id,)
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
                    materia_id=e["materia_id"],
                    titulo=e["titulo"],
                    numero=e["numero"],
                    fecha=date.fromisoformat(e["fecha"]),
                    tipo=TipoEvaluacionEnum(e["tipo"]),
                    aprobado=bool(e["aprobado"]) if e["aprobado"] is not None else None,
                    nota=e["nota"],
                    eval_recupera_id=e["eval_recupera_id"]
                )
                for e in cur_ev.fetchall()
            ]

            return materia

    def listar_todas(self) -> list[Materia]:
        """Devuelve todas las materias registradas (resumen básico sin cargar colecciones)."""
        query = "SELECT * FROM materias ORDER BY anio_cursada ASC, cuatrimestre ASC, nombre ASC"
        with self.db.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [
                Materia(
                    id=r["id"],
                    nombre=r["nombre"],
                    anio_plan=r["anio_plan"],
                    anio_cursada=r["anio_cursada"],
                    cuatrimestre=CuatrimestreEnum(r["cuatrimestre"]),
                    promocionable=bool(r["promocionable"]),
                    estado=EstadoMateriaEnum(r["estado"]),
                    nota_final=r["nota_final"],
                )
                for r in rows
            ]

class PracticoRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def _insertar(self, practico: Practico) -> Practico | None:
        query = """
            INSERT INTO practicos (
                materia_id, numero, titulo, estado
            ) VALUES (?,?,?,?)
            """

        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute(
                    query,
                    (
                        practico.materia_id,
                        practico.numero,
                        practico.titulo,
                        practico.estado.value
                    ),
                )
                practico.id = cursor.lastrowid
            return practico
        except sqlite3.IntegrityError:
            # violacion de la restriccion UNIQUE (materia_id, numero)
            return None

    def _actualizar(self, practico: Practico) -> Practico | None:
        query = """
            UPDATE practicos
            SET materia_id = ?, numero = ?, titulo = ?, estado = ?
            WHERE id = ?
        """
        try:
            with self.db.get_connection() as conn:
                conn.execute(
                    query,
                    (
                        practico.materia_id,
                        practico.numero,
                        practico.titulo,
                        practico.estado.value,
                        practico.id
                    ),
                )
            return practico
        except sqlite3.IntegrityError:
            # violacion de la restriccion UNIQUE (materia_id, numero)
            return None

    def guardar(self, practico: Practico) -> Practico | None:
        """Inserta un practico nuevo o actualiza uno existente."""
        if practico.id is None:
            return self._insertar(practico)
        else:
            return self._actualizar(practico)

    def eliminar(self, practico_id: int) -> bool:
        """Elimina un practico por ID. Retorna True si existía y se eliminó, False si no existía."""
        query = "DELETE FROM practicos WHERE id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (practico_id,))
            return cursor.rowcount > 0

    def obtener_por_id(self, practico_id: int) -> Practico | None:
        """Obtener el práctico dado un ID"""
        query = "SELECT * FROM practicos WHERE id = ?"

        with self.db.get_connection() as conn:
            row = conn.execute(query, (practico_id,)).fetchone()
            if not row:
                return None

        practico = Practico(
            id=row["id"],
            materia_id=row["materia_id"],
            numero=row["numero"],
            titulo=row["titulo"],
            estado=EstadoPracticoEnum(row["estado"]),
        )

        return practico

    def listar_practicos(
        self,
        materia_id: int | None = None,
        estado: EstadoPracticoEnum | None = None,
    ) -> list[Practico]:
        query = " SELECT * FROM practicos WHERE 1 = 1"
        params: list[object] = []

        if materia_id is not None:
            query += " AND materia_id = ?"
            params.append(materia_id)
        if estado is not None:
            query += " AND estado = ?"
            params.append(estado.value)

        query += " ORDER BY materia_id ASC, numero ASC"

        with self.db.get_connection() as conn:
            rows = conn.execute(query,tuple(params)).fetchall()
            return [
                Practico(
                    id=r["id"],
                    materia_id=r["materia_id"],
                    numero=r["numero"],
                    titulo=r["titulo"],
                    estado=EstadoPracticoEnum(r["estado"])
                )
                for r in rows
            ]

class EntregaRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def _insertar(self, entrega: Entrega) -> Entrega | None:
        query = """
            INSERT INTO entregas (
                materia_id, numero, titulo, fecha_entrega, estado, practico_id, nota
            ) VALUES (?,?,?,?,?,?,?)
            """

        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute(
                    query,
                    (
                        entrega.materia_id,
                        entrega.numero,
                        entrega.titulo,
                        # no entiendo este control, lo hizo gemini jaja
                        entrega.fecha_entrega.isoformat() if isinstance(entrega.fecha_entrega, date) else entrega.fecha_entrega,
                        entrega.estado.value,
                        entrega.practico_id,
                        entrega.nota,
                    ),
                )
                entrega.id = cursor.lastrowid
            return entrega
        except sqlite3.IntegrityError:
            # Por ejemplo, si falla la clave foránea de materia_id o practico_id
            return None

    def _actualizar(self, entrega: Entrega) -> Entrega:
        query = """
            UPDATE entregas
            SET materia_id = ?, numero = ?, titulo = ?, fecha_entrega = ?, estado = ?, practico_id = ?, nota = ?
            WHERE id = ?
        """

        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    entrega.materia_id,
                    entrega.numero,
                    entrega.titulo,
                    entrega.fecha_entrega.isoformat() if isinstance(entrega.fecha_entrega, date) else entrega.fecha_entrega,
                    entrega.estado.value,
                    entrega.practico_id,
                    entrega.nota,
                    entrega.id,
                ),
            )
        return entrega


    def guardar(self, entrega: Entrega) -> Entrega | None:
        """Inserta una entrega nueva o actualiza una existente."""
        if entrega.id is None:
            return self._insertar(entrega)
        else:
            return self._actualizar(entrega)

    def eliminar(self, entrega_id: int) -> bool:
        """Elimina una entrega por ID. Retorna True si existia y fue eliminada, False si no existía."""
        query = "DELETE FROM entregas WHERE id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (entrega_id,))
            return cursor.rowcount > 0

    # pintó dry
    def _row_a_entrega(self, row: sqlite3.Row) -> Entrega:
        """Helper privado para mapear una fila de SQLite a la entidad Entrega."""
        raw_fecha = row["fecha_entrega"]
        fecha = date.fromisoformat(raw_fecha) if isinstance(raw_fecha,str) else raw_fecha
        return Entrega(
            id=row["id"],
            materia_id=row["materia_id"],
            numero=row["numero"],
            titulo=row["titulo"],
            fecha_entrega=fecha,
            estado=EstadoEntregaEnum(row["estado"]),
            practico_id=row["practico_id"],
            nota=row["nota"],
        )

    def obtener_por_id(self, entrega_id: int) -> Entrega | None:
        """Obtener una entrega dado un ID."""
        query = "SELECT * FROM entregas WHERE id = ?"

        with self.db.get_connection() as conn:
            row = conn.execute(query, (entrega_id,)).fetchone()
            if not row:
                return None
        return self._row_a_entrega(row)

    def listar_entregas(
        self,
        materia_id: int | None = None,
        practico_id: int | None = None,
        estado: EstadoEntregaEnum | None = None,
        solo_pendientes: bool = False,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Entrega]:
        """Devuelve todas las entregas correspondientes a una materia."""
        query = "SELECT * FROM entregas WHERE 1 = 1"
        params: list[object] = []

        if materia_id is not None:
            query += " AND materia_id = ?"
            params.append(materia_id)
        if practico_id is not None:
            query += " AND practico_id = ?"
            params.append(practico_id)
        if estado is not None:
            query += " AND estado = ?"
            params.append(estado.value)
        elif solo_pendientes:
            query += " AND estado IN (?,?)"
            params.extend([EstadoEntregaEnum.PENDIENTE.value, EstadoEntregaEnum.DESAPROBADO.value])
        if fecha_desde is not None:
            query += " AND fecha_entrega >= ?"
            params.append(fecha_desde.isoformat())
        if fecha_hasta is not None:
            query += " AND fecha_entrega <= ?"
            params.append(fecha_hasta.isoformat())

        query += " ORDER BY fecha_entrega IS NULL, fecha_entrega ASC"

        with self.db.get_connection() as conn:
            rows = conn.execute(query,(tuple(params))).fetchall()
            return [self._row_a_entrega(r) for r in rows]

class EvaluacionRepository:
    def __init__(self, db : DatabaseManager) -> None:
        self.db = db

    def _insertar(self, evaluacion: Evaluacion) -> Evaluacion | None:
        query = """
            INSERT INTO evaluaciones (
                materia_id, titulo, numero, fecha, tipo, aprobado, nota, eval_recupera_id
            ) VALUES (?,?,?,?,?,?,?,?)
        """

        # le podria poner un try except pero no sé qué colisión puede ocurrir
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute(
                    query,
                    (
                        evaluacion.materia_id,
                        evaluacion.titulo,
                        evaluacion.numero,
                        evaluacion.fecha.isoformat() if isinstance(evaluacion.fecha, date) else evaluacion.fecha,
                        evaluacion.tipo.value,
                        evaluacion.aprobado,
                        evaluacion.nota,
                        evaluacion.eval_recupera_id,
                    ),
                )
                evaluacion.id = cursor.lastrowid
            return evaluacion
        except sqlite3.IntegrityError:
            return None


    def _actualizar(self, evaluacion: Evaluacion) -> Evaluacion:
        query = """
            UPDATE evaluaciones
            SET materia_id = ?, titulo = ?, numero = ?, fecha = ?, tipo = ?, aprobado = ?, nota = ?, eval_recupera_id = ?
            WHERE id = ?
        """

        with self.db.get_connection() as conn:
            conn.execute(
                query,
                (
                    evaluacion.materia_id,
                    evaluacion.titulo,
                    evaluacion.numero,
                    evaluacion.fecha.isoformat() if isinstance(evaluacion.fecha, date) else evaluacion.fecha,
                    evaluacion.tipo.value,
                    int(evaluacion.aprobado) if evaluacion.aprobado is not None else None,
                    evaluacion.nota,
                    evaluacion.eval_recupera_id,
                    evaluacion.id,
                ),
            )
        return evaluacion

    def guardar(self, evaluacion: Evaluacion) -> Evaluacion | None:
        """Inserta una nueva evaluación o actualiza una existente"""
        if evaluacion.id is None:
            return self._insertar(evaluacion)
        else:
            return self._actualizar(evaluacion)

    def eliminar(self, evaluacion_id: int) -> bool:
        """Elimina una evaluación por ID. Retorna True si existía y fue eliminada, False si no existía"""
        query = "DELETE FROM evaluaciones WHERE id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (evaluacion_id,))
            return cursor.rowcount > 0

    def _row_a_evaluacion(self, row: sqlite3.Row) -> Evaluacion:
        """Helper privado para mapear una fila de SQLite a la entidad Evaluacion."""
        raw_fecha = row["fecha"]
        raw_aprobado = row["aprobado"]
        fecha = date.fromisoformat(raw_fecha) if isinstance(raw_fecha, str) else raw_fecha
        aprobado = bool(raw_aprobado) if raw_aprobado is not None else None
        return Evaluacion(
            id=row["id"],
            materia_id=row["materia_id"],
            titulo=row["titulo"],
            numero=row["numero"],
            fecha=fecha,
            tipo=TipoEvaluacionEnum(row["tipo"]),
            aprobado=aprobado,
            nota=row["nota"],
            eval_recupera_id=row["eval_recupera_id"],
        )

    def obtener_por_id(self, evaluacion_id: int) -> Evaluacion | None:
        """Obtener una evaluación dado un ID."""
        query = "SELECT * FROM evaluaciones WHERE id = ?"

        with self.db.get_connection() as conn:
            row = conn.execute(query, (evaluacion_id,)).fetchone()
            if not row:
                return None
        return self._row_a_evaluacion(row)

    def listar_evaluaciones(
        self,
        materia_id: int | None = None,
        tipo: TipoEvaluacionEnum | None = None,
        aprobado: bool | None = None,
        solo_pendientes: bool = False,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[Evaluacion]:
        query = "SELECT * FROM evaluaciones WHERE 1 = 1"
        params: list[object] = []

        if materia_id is not None:
            query += " AND materia_id = ?"
            params.append(materia_id)
        if tipo is not None:
            query += " AND tipo = ?"
            params.append(tipo.value)
        if solo_pendientes:
                query += " AND aprobado IS NULL"
        elif aprobado is not None:
            query += " AND aprobado = ?"
            params.append(int(aprobado))  # SQLite guarda bools como 0 y 1
        if fecha_desde is not None:
            query += " AND fecha >= ?"
            params.append(fecha_desde.isoformat())
        if fecha_hasta is not None:
            query += " AND fecha <= ?"
            params.append(fecha_hasta.isoformat())

        query += " ORDER BY fecha IS NULL, fecha ASC, numero ASC"

        with self.db.get_connection() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
            return [ self._row_a_evaluacion(r) for r in rows ]
