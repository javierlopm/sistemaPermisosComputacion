# Introducción
Este proyecto tiene como primer objetivo automatizar parte del proceso de aprobación
de permisos para la coordinación de computación de la Universidad Simón Bolívar.


# Instalaciones requeridas
* sudo apt-get install build-essential libssl-dev libffi-dev python-dev
* Instalar los siguientes paquetes via pip (usar requirements.txt)
    - gspread
    - pyOpenSSL
    - selenium

# Documentos de ayuda
https://gspread.readthedocs.io/en/latest/#models
http://selenium-python.readthedocs.io/api.html

# Permisos de google
* console.developers.google.com
    -  Google Sheets API
    
# Análisis de formularios
* Crear formulario vía https://docs.google.com/forms
    - Asociar a una hoja de cálculo en google drive
    - Compartir con el correo de servicio consulta-permisos@permisos-coordinacion.iam.gserviceaccount.com