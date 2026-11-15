from datetime import date, datetime
from typing import Literal, overload

from core.enums import (
    CuatrimestreEnum,
    EstadoEntregaEnum,
    EstadoMateriaEnum,
    EstadoPracticoEnum,
    TipoEvaluacionEnum,
)
from services.cursada_service import (
    AnalisisCursada,
    GestionEntrega,
    GestionEvaluacion,
    GestionMateria,
    GestionPractico,
)

# helpers de entrada para q no explote todo por un misclick

def _pedir_int(mensaje: str, opcional: bool = False) -> int | None:
    """Reintenta hasta recibir un entero válido. Si opcional=True, Enter devuelve None."""
    while True:
        valor = input(mensaje).strip()
        if not valor and opcional:
            return None
        try:
            return int(valor)
        except ValueError:
            print("Ingresá un número entero válido.")

def _pedir_float(mensaje: str, opcional: bool = False) -> float | None:
    """Reintenta hasta recibir un decimal válido. Si opcional=True, Enter devuelve None."""
    while True:
        valor = input(mensaje).strip().replace(",", ".")
        if not valor and opcional:
            return None
        try:
            return float(valor)
        except ValueError:
            print("Ingresá una nota válida (ej: 7.5).")

def _pedir_date(mensaje: str, opcional: bool = False) -> date | None:
    """Pide una fecha en formato DD/MM/AAAA o AAAA-MM-DD."""
    while True:
        valor = input(mensaje).strip()
        if not valor and opcional:
            return None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(valor, fmt).date()
            except ValueError:
                continue
        print("Formato inválido. Usá DD/MM/AAAA (ej: 25/11/2026) o AAAA-MM-DD.")

@overload
def _pedir_enum[T](titulo: str, opciones: dict[str, T], opcional: Literal[False] = False) -> T: ...

@overload
def _pedir_enum[T](titulo: str, opciones: dict[str, T], opcional: Literal[True]) -> T | None: ...

def _pedir_enum[T](titulo: str, opciones: dict[str, T], opcional: bool = False) -> T | None:
    """Muestra un diccionario de opciones y fuerza una selección válida."""
    while True:
        opc = input(titulo).strip()
        if not opc and opcional:
            return None
        if opc in opciones:
            return opciones[opc]
        print(f"Opción inválida. Elegí entre: {', '.join(opciones.keys())}")

# submenú materias
def menu_materias(gestor_materia: GestionMateria, analisis: AnalisisCursada) -> None:
    opciones_cuatrimestre = {
        "1": CuatrimestreEnum.PRIMER_CUATRIMESTRE,
        "2": CuatrimestreEnum.SEGUNDO_CUATRIMESTRE,
        "3": CuatrimestreEnum.ANUAL,
    }
    while True:
        print("\n--- Gestión de Materias ---")
        print("1. Cargar materia")
        print("2. Listar materias")
        print("3. Actualizar materia")
        print("4. Eliminar materia")
        print("0. Volver")
        opc = input("Opción: ").strip()

        match opc:
            case "1":
                nombre = input("Nombre: ").strip()
                anio_plan = _pedir_int("Año del plan de estudios: ")
                anio_cursada = _pedir_int("Año en que la cursas: ")
                if not nombre or anio_plan is None or anio_cursada is None:
                    print("Datos incompletos o inválidos.")
                    continue

                cuatri = _pedir_enum(
                    "Cuatrimestre (1/2, 3: Anual): ",
                    opciones_cuatrimestre,
                    opcional=False
                )
                prom = _pedir_enum(
                    "Promocionable (s/n): ",
                    {"s": True, "n": False},
                    opcional=False,
                )

                if gestor_materia.cargar_materia(nombre, anio_plan, anio_cursada, cuatri, prom):
                    print("Materia cargada.")
                else:
                    print("No se pudo cargar. Revisá si ya existe una materia con ese nombre.")

            case "2":
                print("Filtros (Enter para omitir):")
                anio_plan = _pedir_int("Año del plan: ", opcional=True)
                anio_cursada = _pedir_int("Año de cursada: ", opcional=True)
                cuatri = _pedir_enum(
                    "Cuatrimestre (1: 1C / 2: 2C / 3: Anual): ",
                    opciones_cuatrimestre,
                    opcional=True,
                )
                prom = _pedir_enum("¿Promocionable? (s/n): ", {"s": True, "n": False}, opcional=True)
                estado = _pedir_enum(
                    "Estado (1: Cursando / 2: Regular / 3: Promocionada / 4: Aprobada / 5: Libre): ",
                    {
                        "1": EstadoMateriaEnum.CURSANDO,
                        "2": EstadoMateriaEnum.REGULAR,
                        "3": EstadoMateriaEnum.PROMOCIONADA,
                        "4": EstadoMateriaEnum.APROBADA,
                        "5": EstadoMateriaEnum.LIBRE,
                    },
                    opcional=True,
                )

                materias = gestor_materia.listar_materias(
                    anio_plan=anio_plan,
                    anio_cursada=anio_cursada,
                    cuatrimestre=cuatri,
                    promocionable=prom,
                    estado=estado,
                )
                if not materias:
                    print("No hay materias que coincidan con los filtros.")
                    continue
                for m in materias:
                    nota_str = f" | Nota final: {m.nota_final}" if m.nota_final is not None else ""
                    print(f"\n[{m.id}] {m.nombre} ({m.estado.value}){nota_str}")
                    print(f"    Plan: {m.anio_plan}° año | Cursada: {m.anio_cursada} ({m.cuatrimestre.value}) | Promocionable: {'Sí' if m.promocionable else 'No'}")
                    if m.id is not None and (stats := analisis.calcular_stats(m.id)):
                        print(f"    TPs: {stats.total_tps_completados}/{stats.total_tps} ({stats.porcentaje_tps_completados}%) | Promedio evals: {stats.promedio_evaluaciones or 'N/A'}")

            case "3":
                materia_id = _pedir_int("ID de la materia a actualizar: ")
                if materia_id is None:
                    continue
                materia = gestor_materia.obtener_materia(materia_id)
                if materia is None:
                    print("Materia no encontrada.")
                    continue

                print(f"Editando '{materia.nombre}' (dejá vacío para mantener el valor actual):")
                nuevo_nombre = input(f"Nombre [{materia.nombre}]: ").strip() or None
                nuevo_estado = _pedir_enum(
                    f"Estado (1: Cursando / 2: Regular / 3: Promocionada / 4: Aprobada / 5: Libre) [{materia.estado.value}] (Enter para mantener): ",
                    {
                        "": None,
                        "1": EstadoMateriaEnum.CURSANDO,
                        "2": EstadoMateriaEnum.REGULAR,
                        "3": EstadoMateriaEnum.PROMOCIONADA,
                        "4": EstadoMateriaEnum.APROBADA,
                        "5": EstadoMateriaEnum.LIBRE,
                    },
                )
                nuevo_año = _pedir_int(f"Año en que la cursas/cursaste [{materia.anio_cursada}]: ", opcional=True)
                nuevo_cuatri = _pedir_enum(
                    f"Cuatrimestre (1/2, 3: Anual) [{materia.cuatrimestre.value}] (Enter para mantener): ",
                    opciones_cuatrimestre,
                    opcional=True
                )
                nota_final = _pedir_float(
                    f"Nota final [{materia.nota_final if materia.nota_final is not None else 'Sin nota'}] (Enter para mantener): ",
                    opcional=True
                )

                if gestor_materia.actualizar_materia(materia_id, nombre=nuevo_nombre, estado=nuevo_estado, anio_cursada=nuevo_año,cuatrimestre=nuevo_cuatri,nota_final=nota_final):
                    print("Materia actualizada.")

            case "4":
                materia_id = _pedir_int("ID de la materia a eliminar: ")
                if materia_id is not None and gestor_materia.eliminar_materia(materia_id):
                    print("Materia eliminada.")
                else:
                    print("No se encontró la materia.")

            case "0":
                break
            case _:
                print("Opción inválida.")

# submenu practicos
def menu_practicos(gestor_practico: GestionPractico, gestor_materia: GestionMateria) -> None:
    opciones_estado = {
        "1": EstadoPracticoEnum.NO_INICIADO,
        "2": EstadoPracticoEnum.EN_PROGRESO,
        "3": EstadoPracticoEnum.COMPLETADO,
    }
    while True:
        print("\n--- Gestión de Prácticos ---")
        print("1. Cargar práctico/s en una materia")
        print("2. Listar prácticos")
        print("3. Actualizar práctico (estado/título/número)")
        print("4. Eliminar práctico")
        print("0. Volver")
        opc = input("Opción: ").strip()

        match opc:
            case "1":
                materia_id = _pedir_int("ID de la materia: ")
                if materia_id is None or (materia := gestor_materia.obtener_materia(materia_id)) is None:
                    print("Materia no encontrada.")
                    continue

                cant = _pedir_int(f"Cantidad de prácticos a cargar en {materia.nombre}: ") or 0
                for i in range(cant):
                    print(f"\n--- Práctico {i + 1} ---")
                    numero = _pedir_int("Número de práctico: ")
                    titulo = input("Título: ").strip()
                    if numero is None or not titulo:
                        print("Datos inválidos, saltando práctico.")
                        continue
                    estado = _pedir_enum("Estado (1: No iniciado / 2: En proceso / 3: Completado): ", opciones_estado)
                    if gestor_practico.cargar_practico(materia_id, numero, titulo, estado):
                        print("Práctico cargado.")
                    else:
                        print("Error al cargar. Revisá si ya existe un práctico con el mismo título o número en esta materia?).")

            case "2":
                materia_id = _pedir_int("ID de la materia (Enter para ver todos): ", opcional=True)
                estado = _pedir_enum(
                    "Estado (1: No iniciado / 2: En proceso / 3: Completado / Enter: todos): ",
                    {"": None, **opciones_estado},
                )
                practicos = gestor_practico.listar_practicos(materia_id=materia_id, estado=estado)
                if not practicos:
                    print("No hay prácticos para mostrar.")
                    continue
                for p in practicos:
                    print(f"[{p.id}] (Mat {p.materia_id}) TP {p.numero}: {p.titulo} -> {p.estado.value}")

            case "3":
                practico_id = _pedir_int("ID del práctico a actualizar: ")
                if practico_id is None or (practico := gestor_practico.obtener_practico(practico_id)) is None:
                    print("Práctico no encontrado.")
                    continue

                print(f"Editando TP {practico.numero}: {practico.titulo} [{practico.estado.value}]")
                nuevo_titulo = input("Nuevo título (Enter para mantener): ").strip() or None
                nuevo_estado = _pedir_enum(
                    "Nuevo estado (1: No iniciado / 2: En proceso / 3: Completado / Enter: mantener): ",
                    opciones_estado,
                    opcional=True,
                )
                if gestor_practico.actualizar_practico(practico_id, titulo=nuevo_titulo, estado=nuevo_estado):
                    print("Práctico actualizado.")

            case "4":
                practico_id = _pedir_int("ID del práctico a eliminar: ")
                if practico_id is not None and gestor_practico.eliminar_practico(practico_id):
                    print("Práctico eliminado.")
                else:
                    print("No se encontró el práctico.")

            case "0":
                break
            case _:
                print("Opción inválida.")


# submenu entregas

def menu_entregas(
    gestor_entrega: GestionEntrega,
    gestor_materia: GestionMateria,
) -> None:
    opciones_estado = {
        "1": EstadoEntregaEnum.PENDIENTE,
        "2": EstadoEntregaEnum.ENTREGADO,
        "3": EstadoEntregaEnum.APROBADO,
        "4": EstadoEntregaEnum.DESAPROBADO,
    }
    while True:
        print("\n--- Gestión de Entregas ---")
        print("1. Cargar entrega")
        print("2. Listar entregas")
        print("3. Actualizar entrega (estado/nota/fecha)")
        print("4. Eliminar entrega")
        print("0. Volver")
        opc = input("Opción: ").strip()

        match opc:
            case "1":
                materia_id = _pedir_int("ID de la materia: ", opcional=True)
                if materia_id is None or (materia := gestor_materia.obtener_materia(materia_id)) is None:
                    print("Materia no encontrada.")
                    continue

                print(f"Nueva entrega para {materia.nombre}:")
                numero = _pedir_int("Número de entrega: ")
                titulo = input("Título: ").strip()
                if numero is None or not titulo:
                    print("Título y número son obligatorios.")
                    continue

                fecha_entrega = _pedir_date("Fecha de entrega (DD/MM/AAAA): ")
                assert fecha_entrega is not None

                practico_id = _pedir_int("ID del práctico asociado (Enter si no aplica): ", opcional=True)
                estado = _pedir_enum(
                    "Estado (1: Pendiente / 2: Entregado / 3: Aprobado / 4: Desaprobado): ",
                    opciones_estado,
                )
                nota = _pedir_float("Nota (Enter si aún no tiene): ", opcional=True)

                if gestor_entrega.cargar_entrega(
                    materia_id=materia_id,
                    numero=numero,
                    titulo=titulo,
                    fecha_entrega=fecha_entrega,
                    estado=estado,
                    practico_id=practico_id,
                    nota=nota,
                ):
                    print("Entrega cargada.")
                else:
                    print("No se pudo cargar (revisá el ID del práctico asociado o restricciones duplicadas).")

            case "2":
                materia_id = _pedir_int("ID de la materia (Enter para ver todas): ", opcional=True)
                solo_pend = _pedir_enum("¿Solo pendientes/desaprobadas? (s/n): ", {"s": True, "n": False})
                estado = None
                if not solo_pend:
                    estado = _pedir_enum(
                        "Estado (1: Pendiente / 2: Entregado / 3: Aprobado / 4: Desaprobado / Enter: todos): ",
                        {"": None, **opciones_estado},
                    )

                entregas = gestor_entrega.listar_entregas(
                    materia_id=materia_id,
                    estado=estado,
                    solo_pendientes=solo_pend,
                )
                if not entregas:
                    print("No hay entregas para mostrar.")
                    continue
                for e in entregas:
                    nota_str = f" | Nota: {e.nota}" if e.nota is not None else ""
                    tp_str = f" (TP ID {e.practico_id})" if e.practico_id is not None else ""
                    print(
                        f"[{e.id}] (Mat {e.materia_id}) #{e.numero} {e.titulo}{tp_str} "
                        f"| Vence: {e.fecha_entrega.strftime('%d/%m/%Y')} -> {e.estado.value}{nota_str}"
                    )

            case "3":
                entrega_id = _pedir_int("ID de la entrega a actualizar (Enter para cancelar): ", opcional=True)
                if entrega_id is None or (entrega := gestor_entrega.obtener_entrega(entrega_id)) is None:
                    print("Entrega no encontrada.")
                    continue

                print(f"Editando #{entrega.numero}: {entrega.titulo} [{entrega.estado.value}]")
                nuevo_titulo = input("Nuevo título (Enter para mantener): ").strip() or None
                nueva_fecha = _pedir_date(
                    f"Nueva fecha [{entrega.fecha_entrega.strftime('%d/%m/%Y')}] (Enter para mantener): ",
                    opcional=True,
                )
                nuevo_estado = _pedir_enum(
                    "Nuevo estado (1: Pendiente / 2: Entregado / 3: Aprobado / 4: Desaprobado / Enter: mantener): ",
                    opciones_estado,
                    opcional=True
                )
                nueva_nota = _pedir_float(
                    f"Nueva nota [{entrega.nota if entrega.nota is not None else 'sin nota'}] (Enter para mantener): ",
                    opcional=True,
                )

                if gestor_entrega.actualizar_entrega(
                    entrega_id=entrega_id,
                    titulo=nuevo_titulo,
                    fecha_entrega=nueva_fecha,
                    estado=nuevo_estado,
                    nota=nueva_nota,
                ):
                    print("Entrega actualizada.")
                else:
                    print("Error al actualizar la entrega.")

            case "4":
                entrega_id = _pedir_int("ID de la entrega a eliminar (Enter para cancelar): ", opcional=True)
                if entrega_id is not None and gestor_entrega.eliminar_entrega(entrega_id):
                    print("Entrega eliminada.")
                else:
                    print("No se encontró la entrega.")

            case "0":
                break
            case _:
                print("Opción inválida.")

# submenu evaluaciones

def menu_evaluaciones(
    gestor_evaluacion: GestionEvaluacion,
    gestor_materia: GestionMateria,
) -> None:
    opciones_tipo = {
        "1": TipoEvaluacionEnum.PARCIAL,
        "2": TipoEvaluacionEnum.RECUPERATORIO,
        "3": TipoEvaluacionEnum.FINAL,
    }
    opciones_aprobado = {
        "": None,
        "s": True,
        "n": False,
    }
    while True:
        print("\n--- Gestión de Evaluaciones ---")
        print("1. Cargar evaluación")
        print("2. Listar evaluaciones")
        print("3. Actualizar evaluación (cargar nota/resultado)")
        print("4. Eliminar evaluación")
        print("0. Volver")
        opc = input("Opción: ").strip()

        match opc:
            case "1":
                materia_id = _pedir_int("ID de la materia: ", opcional=True)
                if materia_id is None or (materia := gestor_materia.obtener_materia(materia_id)) is None:
                    print("Materia no encontrada.")
                    continue

                print(f"Nueva evaluación para {materia.nombre}:")
                tipo = _pedir_enum("Tipo (1: Parcial / 2: Recuperatorio / 3: Final): ", opciones_tipo)
                numero = _pedir_int("Número (ej: 1 para 1er Parcial): ")
                titulo = input("Título: ").strip()
                if numero is None or not titulo:
                    print("Número y título son obligatorios.")
                    continue

                fecha = _pedir_date("Fecha (DD/MM/AAAA): ")
                assert fecha is not None

                eval_recupera_id = None
                if tipo == TipoEvaluacionEnum.RECUPERATORIO:
                    eval_recupera_id = _pedir_int(
                        "ID de la evaluación que recupera (Enter si no vincula): ",
                        opcional=True,
                    )

                aprobado = _pedir_enum("¿Aprobado? (s: Sí / n: No / Enter: Aún no rendida/corregida): ", opciones_aprobado)
                nota = _pedir_float("Nota (Enter si aún no tiene): ", opcional=True)

                if gestor_evaluacion.cargar_evaluacion(
                    materia_id=materia_id,
                    titulo=titulo,
                    numero=numero,
                    fecha=fecha,
                    tipo=tipo,
                    aprobado=aprobado,
                    nota=nota,
                    eval_recupera_id=eval_recupera_id,
                ):
                    print("Evaluación cargada.")
                else:
                    print("No se pudo cargar (revisá el ID de evaluación recuperada o datos duplicados).")

            case "2":
                materia_id = _pedir_int("ID de la materia (Enter para ver todas): ", opcional=True)
                tipo = _pedir_enum(
                    "Tipo (1: Parcial / 2: Recuperatorio / 3: Final / Enter: todos): ",
                    {"": None, **opciones_tipo},
                )
                solo_pend = _pedir_enum("¿Ver solo pendientes de rendir/corregir? (s/n): ", {"s": True, "n": False})

                evaluaciones = gestor_evaluacion.listar_evaluaciones(
                    materia_id=materia_id,
                    tipo=tipo,
                    solo_pendientes=solo_pend,
                )
                if not evaluaciones:
                    print("No hay evaluaciones para mostrar.")
                    continue

                hoy = date.today()
                for ev in evaluaciones:
                    if ev.aprobado is None:
                        res = "Pendiente de rendir" if ev.fecha >= hoy else "Sin corregir"
                    elif ev.aprobado:
                        res = f"Aprobado ({ev.nota})" if ev.nota is not None else "Aprobado"
                    else:
                        res = f"Desaprobado ({ev.nota})" if ev.nota is not None else "Desaprobado"
                    recup_str = f" [Recupera ID {ev.eval_recupera_id}]" if ev.eval_recupera_id else ""
                    print(
                        f"[{ev.id}] (Mat {ev.materia_id}) {ev.tipo.value} #{ev.numero}: {ev.titulo}{recup_str} "
                        f"| Fecha: {ev.fecha.strftime('%d/%m/%Y')} -> {res}"
                    )

            case "3":
                ev_id = _pedir_int("ID de la evaluación a actualizar (Enter para cancelar): ", opcional=True)
                if ev_id is None or (ev := gestor_evaluacion.obtener_evaluacion(ev_id)) is None:
                    print("Evaluación no encontrada.")
                    continue

                print(f"Editando {ev.tipo.value} #{ev.numero}: {ev.titulo}")
                nuevo_titulo = input("Nuevo título (Enter para mantener): ").strip() or None
                nueva_fecha = _pedir_date(
                    f"Nueva fecha [{ev.fecha.strftime('%d/%m/%Y')}] (Enter para mantener): ",
                    opcional=True,
                )
                nuevo_aprobado = _pedir_enum(
                    "Resultado (s: Aprobado / n: Desaprobado / Enter: mantener): ",
                    {"s": True, "n": False},
                    opcional=True,
                )
                nueva_nota = _pedir_float(
                    f"Nota [{ev.nota if ev.nota is not None else 'sin nota'}] (Enter para mantener): ",
                    opcional=True,
                )

                if gestor_evaluacion.actualizar_evaluacion(
                    evaluacion_id=ev_id,
                    titulo=nuevo_titulo,
                    fecha=nueva_fecha,
                    aprobado=nuevo_aprobado,
                    nota=nueva_nota,
                ):
                    print("Evaluación actualizada.")
                else:
                    print("Error al actualizar la evaluación.")

            case "4":
                ev_id = _pedir_int("ID de la evaluación a eliminar (Enter para cancelar): ", opcional=True)
                if ev_id is not None and gestor_evaluacion.eliminar_evaluacion(ev_id):
                    print("Evaluación eliminada.")
                else:
                    print("No se encontró la evaluación.")

            case "0":
                break
            case _:
                print("Opción inválida.")

# ----- ANALÍTICAS (GEMINI)

def menu_resumen(
    analisis: AnalisisCursada,
    gestor_materia: GestionMateria,
    gestor_entrega: GestionEntrega,
    gestor_evaluacion: GestionEvaluacion,
) -> None:
    # Si querés el % sobre el total del plan de Ingeniería en Computación (ej. 42 materias), pasalo acá
    resumen = analisis.calcular_resumen_carrera(total_plan=44)

    print("\n=== Resumen General de Carrera ===")
    print(f"Materias aprobadas/promocionadas: {resumen.materias_aprobadas} ({resumen.porcentaje_avance}% del plan)")
    print(f"Regulares (pendientes de final): {resumen.materias_regulares} | Cursando actualmente: {resumen.materias_cursando}")
    print(f"Promedio general: {resumen.promedio_general or 'N/A'}")
    print(f"  -> Promocionadas: {resumen.promedio_promocionadas or 'N/A'} | Con Final: {resumen.promedio_finales or 'N/A'}")

    print("\n=== Estado de Cursada Actual ===")
    for m in gestor_materia.listar_materias(estado=EstadoMateriaEnum.CURSANDO):
        if m.id is not None and (stats := analisis.calcular_stats(m.id)):
            print(
                f"• {m.nombre}: TPs {stats.total_tps_completados}/{stats.total_tps} "
                f"({stats.porcentaje_tps_completados}%) | Promedio parciales: {stats.promedio_evaluaciones or 'N/A'}"
            )

    proximas_evals = gestor_evaluacion.listar_evaluaciones(solo_pendientes=True)
    if proximas_evals:
        print("\n=== Próximos Exámenes ===")
        hoy = date.today()
        for ev in proximas_evals:
            res = "PENDIENTE" if ev.fecha > hoy else "ESPERANDO RESULTADO"
            print(f"• {ev.fecha.strftime('%d/%m/%Y')} - {ev.tipo.value} #{ev.numero}: {ev.titulo} (Mat ID {ev.materia_id}) [{res}]")

    entregas_pend = gestor_entrega.listar_entregas(solo_pendientes=True)
    if entregas_pend:
        print("\n=== Entregas Pendientes ===")
        for ent in entregas_pend:
            print(f"• {ent.fecha_entrega.strftime('%d/%m/%Y')} - #{ent.numero} {ent.titulo} (Mat ID {ent.materia_id})")

# ----- FIN ANALÍTICAS (GEMINI)

def menu(
    analisis_cursada: AnalisisCursada,
    gestor_materia: GestionMateria,
    gestor_practico: GestionPractico,
    gestor_entrega: GestionEntrega,
    gestor_evaluacion: GestionEvaluacion,
):
    while True:
        print(">>> >>> Gestor de Cursadas <<< <<<")
        print("1. Materias")
        print("2. Practicos")
        print("3. Entregas")
        print("4. Evaluaciones")
        print("5. Resumen")
        print("0. Salir")
        opc = input("Opcion: ").strip()

        match opc:
            case "1":
                menu_materias(gestor_materia=gestor_materia,analisis=analisis_cursada)
            case "2":
                menu_practicos(gestor_materia=gestor_materia,gestor_practico=gestor_practico)
            case "3":
                menu_entregas(gestor_entrega=gestor_entrega,gestor_materia=gestor_materia)
            case "4":
                menu_evaluaciones(gestor_evaluacion=gestor_evaluacion,gestor_materia=gestor_materia)
            case "5":
                menu_resumen(analisis=analisis_cursada, gestor_entrega=gestor_entrega, gestor_materia=gestor_materia,gestor_evaluacion=gestor_evaluacion)
            case "0":
                print("Gracias por usar. Vuelva prontos!")
                break
            case _:
                print("Opción ♿")
        print(" ")
