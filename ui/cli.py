from core.enums import CuatrimestreEnum, EstadoMateriaEnum, EstadoPracticoEnum
from services.cursada_service import (
    AnalisisCursada,
    #GestionEntrega,
    #GestionEvaluacion,
    GestionMateria,
    GestionPractico,
)

# helpers de entrada para q no explote todo por un misclick

def _pedir_int(mensaje: str) -> int | None:
    """Pide un entero. Si el usuario deja vacío o escribe texto inválido, retorna None."""
    valor = input(mensaje).strip()
    if not valor:
        return None
    try:
        return int(valor)
    except ValueError:
        print("Ingresá un número válido.")
        return None

def _pedir_enum[T](titulo: str, opciones: dict[str,T]) -> T:
    """Muestra un diccionario de opciones y fuerza una selección válida."""
    while True:
        opc = input(titulo).strip()
        if opc in opciones:
            return opciones[opc]
        print(f"Opción inválida. Elegí entre: {','.join(opciones.keys())}")

# submenú materias
def menu_materias(gestor_materia: GestionMateria, analisis: AnalisisCursada) -> None:
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
                    "Cuatrimestre (1/2): ",
                    {
                        "1": CuatrimestreEnum.PRIMER_CUATRIMESTRE,
                        "2": CuatrimestreEnum.SEGUNDO_CUATRIMESTRE,
                    },
                )
                prom = _pedir_enum("Promocionable (s/n): ", {"s": True, "n": False})

                if gestor_materia.cargar_materia(nombre, anio_plan, anio_cursada, cuatri, prom):
                    print("Materia cargada.")
                else:
                    print("No se pudo cargar. Revisá si ya existe una materia con ese nombre.")

            case "2":
                materias = gestor_materia.listar_materias()
                if not materias:
                    print("No hay materias cargadas.")
                    continue
                for m in materias:
                    print(f"\n[{m.id}] {m.nombre} ({m.estado.value})")
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
                    "Estado (1: Cursando / 2: Regular / 3: Promocionada / 4: Aprobada / 5: Libre / Enter: mantener): ",
                    {
                        "": None,
                        "1": EstadoMateriaEnum.CURSANDO,
                        "2": EstadoMateriaEnum.REGULAR,
                        "3": EstadoMateriaEnum.PROMOCIONADA,
                        "4": EstadoMateriaEnum.APROBADA,
                        "5": EstadoMateriaEnum.LIBRE,
                    },
                )
                if gestor_materia.actualizar_materia(materia_id, nombre=nuevo_nombre, estado=nuevo_estado):
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
                materia_id = _pedir_int("ID de la materia (Enter para ver todos): ")
                estado = _pedir_enum(
                    "Estado (1: No iniciado / 2: En proceso / 3: Completado / Enter para ver todos): ",
                    {"": None, **opciones_estado}
                )
                practicos = gestor_practico.listar_practicos(
                    materia_id=materia_id,
                    estado=estado,
                )
                if not practicos:
                    print("No hay prácticos para mostrar.")
                    continue
                for p in practicos:
                    print(f"[{p.id}] TP {p.numero}: {p.titulo} -> {p.estado.value}")

            case "3":
                practico_id = _pedir_int("ID del práctico a actualizar: ")
                if practico_id is None or (practico := gestor_practico.obtener_practico(practico_id)) is None:
                    print("Práctico no encontrado.")
                    continue

                print(f"Editando TP {practico.numero}: {practico.titulo} [{practico.estado.value}]")
                nuevo_titulo = input("Nuevo título (Enter para mantener): ").strip() or None
                nuevo_estado = _pedir_enum(
                    "Nuevo estado (1: No iniciado / 2: En proceso / 3: Completado / Enter: mantener): ",
                    {"": None, **opciones_estado},
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

def menu(
    analisis_cursada: AnalisisCursada,
    gestor_materia: GestionMateria,
    gestor_practico: GestionPractico,
):
    while True:
        print(">>> >>> Gestor de Cursadas <<< <<<")
        print("1. Materias")
        print("2. Practicos")
        print("3. Entregas")
        print("4. Evaluaciones")
        print("0. Salir")
        opc = input("Opcion: ").strip()

        match opc:
            case "1":
                menu_materias(gestor_materia=gestor_materia,analisis=analisis_cursada)
            case "2":
                menu_practicos(gestor_materia=gestor_materia,gestor_practico=gestor_practico)
            case "3":
                print("Suscribite al Plan Premium+ para desbloquear las Entregas!")
            case "4":
                print("Suscribite al Plan Premium+ para desbloquear las Evaluaciones!")
            case "0":
                print("Gracias por usar. Vuelva prontos!")
                break
            case _:
                print("Opción ♿")
        print(" ")
