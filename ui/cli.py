from services.cursada_service import AnalisisCursada, GestionMateria
from core.enums import EstadoMateriaEnum, CuatrimestreEnum, EstadoPracticoEnum

def menu(gestor_materia: GestionMateria):
    while True:
        print("Gestor de Cursadas")
        print("1. cargar materia")
        print("2. listar materias cargadas")
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
                
                gestor_materia.cargar_materia(
                    nombre=nombre,
                    anio_plan=int(anioplan),
                    anio_cursada=int(aniocursada),
                    cuatrimestre=cuatri,
                    promocionable=bool(prom)
                )

            case "2":
                print("listando materias")
                materias = gestor_materia.listar_materias()
                for m in materias:
                    print(f"Nombre: {m.nombre}")
                    print(f"{m.anio_plan}° Año, {m.cuatrimestre.value}")
                    print(f"Cursada en: {m.anio_cursada}")
                    print(f"Promocionable: {'Si' if m.promocionable else 'No'}")
                    print(f"Estado: {m.estado.value}")
                    if m.id is not None:
                        tps_totales = gestor_materia.repo_practico.listar_por_materia(m.id)
                    print(f"Practicos totales: {len(tps_totales)}")
                    tps_completados = [
                        p for p in tps_totales if p.estado == EstadoPracticoEnum.COMPLETADO
                    ]
                    print(f"Practicos completados: {len(tps_completados)}")

            case "0":
                print("Gracias por usar. Vuelva prontos!")
                break