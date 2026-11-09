# Gestor de Cursadas

Sistema de gestión académica y seguimiento de cursadas universitarias desarrollado en Python con persistencia en SQLite. Permite administrar materias, trabajos prácticos, entregas y evaluaciones, calculando automáticamente porcentajes de avance y promedios académicos ponderados.

---

## Características

- **Seguimiento de Materias:** Registro de cursadas identificadas de forma unívoca por nombre, año lectivo y cuatrimestre, permitiendo recursadas sin colisiones.
- **Entregas y Trabajos Prácticos:** Control de estados de avance (pendiente, entregado, completado) y registro de calificaciones.
- **Cálculo de Métricas Académicas:**
  - Porcentaje de avance de cursada basado en prácticos aprobados/completados.
  - Promedio ponderado de evaluaciones con exclusión automática de parciales recuperados.

---

## Estructura del Proyecto

```text
gestor-cursadas/
├── core/                  # Dominio: entidades, dataclasses y enums
│   ├── enums.py
│   └── models.py
├── persistence/           # Persistencia: SQLite, esquemas y repositorios
│   ├── database.py
│   ├── repositories.py
│   └── schema.sql
├── data/                  # Almacenamiento local de la base de datos)
│   └── cursadas.db
├── tests/                 # Pruebas automatizadas y scripts de verificación
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Requisitos

- Python 3.10+
- SQLite3 (incluido en la biblioteca estándar de Python)

---

## Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd gestor-cursadas
   ```

2. **Crear y activar el entorno virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias de desarrollo (opcional):**
   ```bash
   pip install -r requirements.txt
   ```

---

## Inicialización y Pruebas

Si sos otra persona viendo esto (lo cual no debería ocurrir porque tengo el repo en privado por ahora), no vas a poder ejecutar nada todavía. Si sos yo, hacé esto:

Para inicializar la base de datos SQLite y correr las pruebas de verificación de entidades y repositorios, ejecutá desde la raíz del proyecto:

```bash
# Ejecutar verificación de dominio y modelos
python test_core.py

# Ejecutar verificación de esquemas y repositorios SQLite
python test_db.py
```

---

## Modelo de Datos

La persistencia utiliza claves foráneas habilitadas (`PRAGMA foreign_keys = ON`) y cascada en relaciones dependientes:

- `materias`: Entidad principal con restricción `UNIQUE(nombre, anio_cursada, cuatrimestre)`.
- `practicos`: Trabajos prácticos asociados a una materia (`ON DELETE CASCADE`).
- `entregas`: Hitos de entrega vinculados a una materia y opcionalmente a un práctico (`ON DELETE SET NULL`).
- `evaluaciones`: Parciales, recuperatorios y finales con autoreferencia `eval_recupera_id` para el descarte de notas en el cálculo del promedio.

Si llegaste hasta acá: sí. Como sospechas, esto lo hizo la IA.