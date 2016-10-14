CREATE TABLE IF NOT EXISTS estudiante (
    carnet     INTEGER PRIMARY KEY NOT NULL,
    nombre     TEXT                NOT NULL,
    telefono   TEXT                NOT NULL,
    correo     TEXT                NOT NULL,
    creditos_p INTEGER,
    pp         INTEGER -- No hay soporte para bool
);

CREATE TABLE IF NOT EXISTS permiso (
    fk_carnet  INTEGER NOT NULL,
    materia    TEXT    NOT NULL,
    aprobado   INTEGER, -- No hay soporte para bool
    FOREIGN KEY (fk_carnet) REFERENCES estudiante(carnet),
    PRIMARY KEY (fk_carnet,materia)
);

-- INSERT INTO estudiante VALUES(
--     1110552,
--     "Javier López",
--     "0412-9349938",
--     "Javierloplom@gmail.com",
--     NULL,
--     NULL);