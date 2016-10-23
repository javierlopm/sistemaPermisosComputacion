/*
    Datos de un estudiante
 */
CREATE TABLE IF NOT EXISTS estudiante (
    carnet     INTEGER PRIMARY KEY NOT NULL,
    nombre     TEXT                NOT NULL,
    telefono   TEXT                NOT NULL,
    correo     TEXT                NOT NULL
);

/*
    Tabla para superclase de permisos
 */
CREATE TABLE IF NOT EXISTS permiso (
    id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
    fk_carnet  INTEGER NOT NULL,
    tipo       CHAR(1) NOT NULL, -- No hay soporte para ENUMS
    aprobado   CHAR(1),          -- No hay soporte para bool
    trimestre  CHAR(1),          -- No hay soporte para ENUMS
    anio       INTEGER,
    FOREIGN KEY (fk_carnet) REFERENCES estudiante(carnet)
);

/*
    Tabla para permisos para electivas
 */
CREATE TABLE IF NOT EXISTS permiso_materia (
    id_permiso INTEGER NOT NULL,
    materia    CHAR(8) NOT NULL,
    FOREIGN KEY (id_permiso) REFERENCES permiso(id_permiso),
    PRIMARY KEY (id_permiso)
);

CREATE TABLE IF NOT EXISTS permiso_creditos (
    id_permiso   INTEGER NOT NULL,
    num_creditos INTEGER NOT NULL,
    FOREIGN KEY (id_permiso) REFERENCES permiso(id_permiso),
    PRIMARY KEY (id_permiso)
);

-- INSERT INTO estudiante VALUES(
--     1110552,
--     "Javier López",
--     "0412-9349938",
--     "Javierloplom@gmail.com",
--     NULL,
--     NULL);
