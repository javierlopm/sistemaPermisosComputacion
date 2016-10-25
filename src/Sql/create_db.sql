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
    id_permiso   INTEGER PRIMARY KEY AUTOINCREMENT,
    fk_carnet    INTEGER NOT NULL,
    tipo         CHAR(1) NOT NULL, 
    aprobado     CHAR(1) NOT NULL DEFAULT 'p',
    trimestre    CHAR(1),          
    anio         INTEGER,
    string_extra CHAR(16),
    int_extra    INTEGER,
    FOREIGN KEY (fk_carnet) REFERENCES estudiante(carnet)
);
