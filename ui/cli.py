from core.enums import CuatrimestreEnum, EstadoPracticoEnum
from services.cursada_service import AnalisisCursada, GestionCursada


def menu(gestor_cursada: GestionCursada):
    analisis_cursada = AnalisisCursada(
        gestor_cursada.repo_materia,
        gestor_cursada.repo_practico,
        gestor_cursada.repo_entrega,
        gestor_cursada.repo_evaluacion,
    )
    while True:
        print(">>> >>> Gestor de Cursadas <<< <<<")
        print("1. cargar materia")
        print("2. listar materias cargadas")
        print("3. cargar practicos de una materia")
        print("4. Listar practicos de una materia")
        print("0. salir")
        opc = input("Opcion: ").strip()

        match opc:
            case "1":
                print("Cargar materia")
                nombre = input("Nombre: ").strip()
                anioplan = input("Año del plan de estudios: ").strip()
                aniocursada=input("Año de cursado: ").strip()
                cuatri=input("Cuatrimestre (1/2): ").strip()
                while True:
                    if cuatri == "1":
                        cuatri = CuatrimestreEnum.PRIMER_CUATRIMESTRE
                        break
                    elif cuatri == "2":
                        cuatri = CuatrimestreEnum.SEGUNDO_CUATRIMESTRE
                        break
                    print("wacho culia pone 1 o 2!!")
                prom=input("Promocionable (s/n): ").strip().lower()
                while True:
                    if prom == "s":
                        prom = True
                        break
                    elif prom == "n":
                        prom = False
                        break
                    print("wacho culia pone s o n!!")

                if gestor_cursada.cargar_materia(
                    nombre=nombre,
                    anio_plan=int(anioplan),
                    anio_cursada=int(aniocursada),
                    cuatrimestre=cuatri,
                    promocionable=bool(prom)
                ):
                    print("Materia Cargada!")

            case "2":
                print("listando materias")
                materias = gestor_cursada.listar_materias()
                for m in materias:
                    print(" ")
                    print(f">>> >>> {m.nombre} <<< <<<")
                    print(f"ID: {m.id}")
                    print(f"{m.anio_plan}° Año, {m.cuatrimestre.value}")
                    print(f"Cursada en: {m.anio_cursada}")
                    print(f"Promocionable: {'Si' if m.promocionable else 'No'}")
                    print(f"Estado: {m.estado.value}")
                    if m.id is not None:
                        stats = analisis_cursada.calcular_stats(m.id)
                        if stats:
                            print(f"Practicos totales: {stats.total_tps}")
                            print(f"Practicos completados: {stats.total_tps_completados}")
                    print(">>> >>> ------ <<< <<<")
                    print(" ")

            case "3":
                print("Cargar practicos en una materia")
                nombre = input("Nombre de la materia: ")
                materia_id = gestor_cursada.obtener_id_materia_por_nombre(nombre)
                if materia_id is None:
                    print(f"No se hayó la materia llamada {nombre} en el sistema.")
                else:
                    n = int(input("Cantidad de practicos a cargar: "))
                    for i in range(n):
                        print(f"\n --- Practico {i + 1} ---")
                        titulo = input("Titulo: ")
                        numero = int(input("Numero de practico: "))
                        opciones_estado = {
                            "1": EstadoPracticoEnum.NO_INICIADO,
                            "2": EstadoPracticoEnum.EN_PROGRESO,
                            "3": EstadoPracticoEnum.COMPLETADO,
                        }
                        estado: EstadoPracticoEnum
                        while True:
                            opc_est = input("Estado: 1. No iniciado / 2. En proceso / 3. Completado").strip()
                            if opc_est in opciones_estado:
                                estado = opciones_estado[opc_est]
                                break
                            print("Opcion inválida. Ingrese 1, 2 o 3")
                        if gestor_cursada.cargar_practico(
                            materia_id=materia_id,
                            numero=numero,
                            titulo=titulo,
                            estado=estado,
                        ):
                            print("Practico cargado!")

            case "4":
                print("Listar practicos de una materia")
                nombre = input("Nombre de la materia: ")
                materia_id = gestor_cursada.obtener_id_materia_por_nombre(nombre)
                if materia_id is None:
                    print(f"No se hayó la materia llamada {nombre} en el sistema.")
                else:
                    print(" ")
                    print(f">>> >>> Practicos de {nombre} <<< <<<")
                    for p in gestor_cursada.listar_practicos_materia(materia_id=materia_id):
                        print("--------------------------------")
                        print(f"{p.numero}. {p.titulo}")
                        print(f"{p.estado.value}")
                        print("--------------------------------")

            case "0":
                print("Gracias por usar. Vuelva prontos!")
                break

        print(" ")
