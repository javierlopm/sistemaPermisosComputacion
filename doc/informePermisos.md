---
graphics: yes
---

\newpage

# Introducción
(Dejar para el final)

# Resumen
(Dejar para el final)

# Planteamiento del problema

La Coordinación de Ingeniería de Computación trimestralmente y como parte de sus funciones debe controlar los permisos de inscripción de los estudiantes adscritos a esta carrera, en los cuales se contempla la inscripción de materias electivas, límite de créditos (superiores e inferiores a la norma), materias cuyos requisitos no han sido cubiertos totalmente y materias fuera del plan de estudio por nombrar algunos. 

Para que los estudiantes de Ingeniería de Computación pudieran solicitar sus permisos debían llenar planillas que la coordinación proporcionaba, en donde era necesario escribir los permisos requeridos y marcar en un grafo (que representa el pensum de la carrera) las materias aprobadas, las cursadas en el trimestre actual y las que se desean inscribir.

La coordinación, para que los estudiantes realizaran este proceso debía imprimir planillas de permisos para cada uno, recibirlas después de llenadas y resolver las posibles inquietudes de cada estudiante. Posteriormente para procesar cada permiso, la coordinadora debía descargar todos los expendientes de los estudiantes para comprobar que los grafos llenados por ellos coincidieran con los datos oficiales de la universidad. Luego, tomando en cuenta el índice de los estudiantes, su situación y la cantidad de cupos disponibles para cada asignatura procedía a aprobar o negar los diferentes permisos soliticitados. 

Por último, la coordinación con todos esos datos generaba de forma manual tres hojas de cálculo para DACE: uno para los permisos de asignaturas, un memo con los permisos de generales y un tercer archivo con datos con permisos generales y de límites de créditos.

Para los permisos del trimestre enero-marzo 2017, hubiese sido necesario procesar de forma manual los permisos de más de 140 estudiantes, lo cual representa, aproximadamente 380 permisos diferentes. La única etapa en el procesamiento de permisos apoyada por software adaptado a las necesidades de la coordinación era la visualización del grafo de los estudiantes, el cual es uno de los módulos realizados como parte de un miniproyecto anterior.

El miniproyecto precedente consistía en una aplicación móvil la cual requería un servidor para atender las solicitudes de todos los estudiantes y una aplicación de escritorio para el procesamiento de estos. Los inconvenientes encontrados con el uso de esta aplicación radicaban en: la ausencia de un servidor para el alojamiento de la aplicación, la ausencia de un módulo para descargar los expendientes de los estudiantes y fallas en el cumplimiento de los requerimientos de coordinación (todos los permisos de un estudiante eran tomados como una unidad monolítica en vez de elementos individuales).


# Objetivos del miniproyecto
El objetivo de este Miniproyecto de Desarrollo de Software es implementar un sistema capaz de proveerle a los estudiantes de Ingeniería de la Computación de la Universidad Simón Bolívar una herramienta para solicitar los permisos relacionados con la inscripción de materias más fácil y cómoda de utilizar y a su vez mucho más barata y ecológica ya que, como se mencionó en el punto anterior, quedaría eliminado el uso innecesario de papel y tinta de impresiones para la solicitud de estos permisos. A su vez, del lado del procesamiento de los permisos, es objetivo del Miniproyecto proveerle a la coordinadora de la carrera una interfaz sencilla pero efectiva y poderosa para el procesamiento manual de los permisos solicitados por los estudiantes mediante la herramienta provista la cual será capaz de descargarlos, almacenarlos y , para cada estudiante, el carnet suministrado por él mismo ser utilizado para descargar su expediente de manera automática para poder ser extraídos datos pertinentes de los estudiantes para el momento de procesar sus permisos y una vez finalizado todo el procesamiento, poder generar un archivo contenedor del resultado de este procesamiento de manera automática. Todo lo mencionado logrará cumplir con el objetivo general de este Miniproyecto de automatizar una serie de tareas que hasta este trimestre han sido manuales y ahorrar una cantidad considerable de tiempo, esfuerzo y dinero a la coordinación de Ingeniería de la Computación.

# Análisis

## Flujo de trabajo ahora en el sistema

## Especificación de reglas

# Diseño


La aplicación se encuentra distribuida en los siguientes módulos y plataformas:

* Plataforma google: a través de google form los usuarios realizan sus solicitudes de permisos, estos resultados son almacenados en una hoja de cálculo disponible en google drive para ser procesada posteriormente por la aplicación de escritorio.
* Generador de grafos: módulo del miniproyecto anterior, genera archivos png con los grafos coloreados con las materias aprobadas de un estudiante cualquier en computación.
* Módulo de extración de expedientes: automatiza la búsqueda de expedientes mediante las credenciales de la coordinadora de computación, realiza consultas en la página [http://expediente.dii.usb.ve/] http://expediente.dii.usb.ve/ y almacena los archivos en formato html.
* Módulo csv: permite la generación de tablas en formato csv, requerido por dace, es el producto resultante del procesamiento de todos los permisos.
* Módulo de bd: mantiene en disco los datos de todos los estudiantes que se encuentran solicitando permisos, los tipos de permisos que requieren y el estado en el que se encuentran (aprobados, negados o pendientes).
* Módulo consulta de formulario: integra las hojas de cálculo de la plataforma de google, el de extracción de expedientes, generación de grafos y el manejador de base de datos.
* Aplicación de escritorio: unifica todos los módulos ya mencionados empleando una interfaz gráfica intuitiva para ser manejada por la coordinadora de computación.

Para el módulo de procesamiento de formularios y expedientes seguimos el siguiente algoritmo
```
proc procesar_formulario(form):
    por cada fila en form:
        obtener_expediente(fila['carnet'])
        generar_grafo(archivo_carnet,fila[carnet])
        insertar_en_bd(fila['datos_de_estudiante'])

        por cada permiso en fila:
            insertart_en_bd(permiso)
```

El diseño de las vistas para la aplicación de escritorio se realizó mediante la extensión de clases proporcionadas por Gtk para python. (CAMBIAR O ELIMINAR)

## Arquitectura
Este miniproyecto fue desarrollado en *python3*, haciendo uso de las siguiente bibliotecas disponibles a través del manejador de paquete *pip*:

* gspread: utilizado para realizar consultas a las hojas de cálculo almacenadas en google drive.
* oauth2client: necesario para el proceso de autenticación de google drive.
* selenium: biblioteca para realizar automatizaciones sobre exploradores web, adicionalmente hacemos uso de chromium webdriver de 64 bits para mantener el explorador web en un entorno aislado e indpendente del administrador de paquetes del sistema operativo.  [1]
* gi, gi.repository,Gtk: bibliotecas estándar de python3 (en versiones nuevas), permiten crear interfaces de escritorio orientadas a eventos.
* easygui: biblioteca que provee ventanas y pop-ups de interacción preelaborados.
* sqlite3: *wrapper* de C en *python3* para el sistema de gestión de  bases de datos portable *sqlite3*. No requiere ser instalada, es parte de python3
* csv: biblioteca estándar de python3 que ayuda a generar archivos csv (Comma Separated Values), los cuales pueden ser importados en cualquier programa de hojas de cálculo (requerido por DACE).
* bs4: módulo de la biblioteca BeautifulSoup, parser de html, permite la extración del nombre, índice y número de créditos aprobados por cada estudiante desde su expediente.

Este proyecto, adicionalmente hace uso de de la máquina virtual de java 8 para la generación de los grafos de cada estudiante y del selenium webdriver (el cual es dependiente de la arquitectura x86_64 pero puede ser sustuido por x86).

La aplicación de escritorio ya se encuentra operativa en uno de los equipos de la coordinación.

## Plan de pruebas y resultados
(Describir el an y resultados de ejecución)
Durante el desarrollo del Miniproyecto constantemente cada módulo fue probado mediante permisos de prueba creados por los desarrolladores directamente en el formulario de Google los cuales cumplían la función de asegurar la inexistencia de errores en el procesamiento para cada tipo de permiso.

Al momento de finalizado el sistema con todos sus módulos listos se decidió que la mejor manera de realizar la prueba era mediante la solicitud de permisos formal para el trimestre Enero - Marzo 2017, de esta manera se propagó por todos los medios al alcance el link hacia el formulario de Google donde los estudiantes por una semana enviaron sus solicitudes de permisos que vendrían siendo la primera suite de pruebas completa para el sistema desarrollado.

Esta decisión para las pruebas se debió a que en caso de cualquier error estos no iban a significar algún tipo de pérdida de la información suministrada por los estudiantes asomando la posibilidad de realizar una segunda jornada de solicitud de permisos, ya que en la arquitectura del sistema al momento de tratar con la información almacenada en la nube es únicamente para su lectura. Se descargan los permisos, se almacenan localmente y luego se realiza cualquier prueba necesaria sobre éstos y en el peor de los casos sencillamente se vuelven a descargar sin ningún inconveniente. 

Proceso de realización de las pruebas:

* Recopilación de 416 permisos solicitados entre 142 estudiantes de Ingeniería de la Computación a través del Google Form
* Pruebas de modificar errores cometidos por los estudiantes al momento de solicitar los permisos. Errores leves, reconocibles y fáciles de arreglar directamente en la hoja de cálculo en la nube
* Procesamiento de los permisos
* Creación de los CSV de salida de 366 permisos correctos procesados
* Envío de correos anunciando permisos negados

Durante la ejecución de las tareas mencionadas anteriormente se pudo comprobar la correctitud del sistema salvo por errores leves que fueron solucionados fácilmente sin exponer la integridad de los datos de los estudiantes en ningún momento

Los resultados fueron 366 permisos procesados, 50 permisos incorrectos por errores de los estudiantes al momento de ingresar

Errores típicos de código solían ser de inconsistencia de datos. Por parte de los solicitantes de permisos solían ser ingreso de texto en campos de códigos de materias lo cual el sistema reconocía cada palabra como un código de materia lo cual no es causante de mayores inconvenientes ya que con ser dejados en modo "pendiente" son ignorados por el sistema al momento de generar la salida en CSV



# Conclusión
(Dejar para el final)

# Bibliografía
(Dejar para el final)

[1] 