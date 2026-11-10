PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    anio_plan INTEGER NOT NULL,
    anio_cursada INTEGER NOT NULL,
    cuatrimestre TEXT NOT NULL CHECK (cuatrimestre IN ('1C', '2C', 'ANUAL')),
    promocionable INTEGER NOT NULL CHECK (promocionable IN (0, 1)),
    estado TEXT NOT NULL CHECK (estado IN ('CURSANDO', 'REGULAR', 'PROMOCIONADA', 'APROBADA', 'LIBRE')),

    UNIQUE(nombre, anio_cursada, cuatrimestre)
);

CREATE TABLE IF NOT EXISTS practicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id INTEGER NOT NULL,
    numero INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('NO_INICIADO', 'EN_PROGRESO', 'COMPLETADO')),
    FOREIGN KEY (materia_id) REFERENCES materias (id) ON DELETE CASCADE
    UNIQUE(materia_id,numero)
);

CREATE TABLE IF NOT EXISTS entregas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id INTEGER NOT NULL,
    practico_id INTEGER,
    numero INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    fecha_entrega TEXT NOT NULL, -- Formato ISO: YYYY-MM-DD
    estado TEXT NOT NULL CHECK (estado IN ('PENDIENTE', 'ENTREGADO', 'APROBADO', 'DESAPROBADO')),
    nota REAL,
    FOREIGN KEY (materia_id) REFERENCES materias (id) ON DELETE CASCADE,
    FOREIGN KEY (practico_id) REFERENCES practicos (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS evaluaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    materia_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    numero INTEGER NOT NULL,
    fecha TEXT NOT NULL, -- Formato ISO: YYYY-MM-DD
    tipo TEXT NOT NULL CHECK (tipo IN ('PARCIAL', 'RECUPERATORIO', 'COLOQUIO', 'FINAL')),
    aprobado INTEGER CHECK (aprobado IN (0, 1)),
    nota REAL,
    eval_recupera_id INTEGER,
    FOREIGN KEY (materia_id) REFERENCES materias (id) ON DELETE CASCADE,
    FOREIGN KEY (eval_recupera_id) REFERENCES evaluaciones (id) ON DELETE SET NULL
);