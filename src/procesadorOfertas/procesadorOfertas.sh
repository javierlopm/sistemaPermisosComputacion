# Nombre: Daniel Leones
# Carné: 09-10977
# Fecha: 26/10/2016
# Descripción: Interfaz que abstrae el entorno de ejecución procesadorOfertas y
# procesa los argumentos para dicho programa.
# Funciones:
#   - Preprocesa los archivos DOC a FODT. Paso previo a esto es que Libreoffice
#     no esté ejecutandose.
#   - Ejecuta el procesadorOfertas con los argumentos recibidos
function usoAyuda() {
    echo "Instrucciones de uso: "
    echo -e "- Uso 1:\n\tprocesadorOfertas -f camino/nombre_archivo_salida -d nombre_archivo_dace"
    echo -e "\t-m archivo_materias_requeridas -e nomDir \n"
    echo -e "\tLos archivos en -m y -d deben estar incluidos en <nomDir>"
    echo -e "- Uso 2:\n\tprocesadorOfertas -f camino/nombre_archivo_salida -d nombre_archivo_dace"
    echo -e "\t-m archivo_materias_requeridas archivo1.pdf archivo2.xls ... archivoN\n"
    echo "- Ayuda: procesadorOfertas -h"
    return
}

reanalisis=0

function pasajeParametros() {
    while getopts ":f:d:m:e:hr" opt; do
      case $opt in
        f)
            nombreArchSalida=$OPTARG
        ;;
        e)
            caminoDirArchs=$OPTARG
        ;;
        d)
            nombreArchDace=$OPTARG
        ;;
        m)
            nomArchMaterias=$OPTARG
        ;;
        r)
            reanalisis=1
        ;;
        h)
            usoAyuda
            exit 0
        ;;
        \?)
            echo "ERROR:Opcion Invalida -$OPTARG" >&2
            exit 1
        ;;
        :)
            echo "ERROR: Opcion -$OPTARG requiere un argumento." >&2
            exit 1
        ;;
        esac
    done


    # Comprobar que los nombres proporcionados en los flags esten en el directorio
    if [[ -z $caminoDirArchs ]]; then
        # echo 'Set $caminoDirArchs'
        # echo $caminoDirArchs
        caminoDirArchs="./"
        # echo $caminoDirArchs
        # echo 'Fin $caminoDirArchs'
    fi

    if [[ $# == 0 ]]; then
        echo "ERROR: suministre los argumentos apropiados."
        exit 1
    fi
    
    # Acceder a los operandos
    shift $((OPTIND-1))
    if [[ $reanalisis -eq 1 ]]; then
        if [[ !( -a "$1")]]; then
            if [[ -z "$1" ]]; then
                echo "ERROR: Especifique el archivo de ofertas"                
            else
                echo "ERROR: Verifica que $1 exista"                
            fi
            exit 1
        elif [[ !( -a "$nombreArchDace" ) ]]; then
            echo "ERROR: Verifique que $nombreArchDace exista"
            exit 1
        fi
    else
        # Verificar que los flags sean usados
        if [[ -z "$nombreArchDace" || -z "$nomArchMaterias" || -z "$nombreArchSalida" ]]; then
            echo "ERROR: -d -m -f son parametros obligatorios" >&2
            exit 1
        elif [[ -d "$caminoDirArchs" && -a "$caminoDirArchs$nomArchMaterias" \
            && -a "$caminoDirArchs$nombreArchDace" ]]; then
            return
        else
            echo "ERROR: Los archivos $nombreArchDace o $nomArchMaterias no se encuentran"
            echo "en el directorio $caminoDirArchs. Asegurese que esten allí."
            exit 1
        fi
    fi
    return
}


#Procesar la entrada estandar
pasajeParametros $@
shift $((OPTIND-1))
# Preprocesar los DOCS para Flat XML de libreoffice
existe=$(exec ps -U $(whoami) | awk '/soffice/ {print $4}' | wc -l)
python_bin=$(whereis python3 | grep -oE '/usr\/bin\/python3[[:space:]]')
# Linea para obtener python 3.x
#$(whereis python3 | grep -oE '/usr\/bin\/python3(\.[[:digit:]])?[[:space:]]' | awk '{ print $1}')
# Pedir reanalsiis de ofertas
if [[ $reanalisis -eq 1 ]]; then
    $python_bin procesadorOfertas.py -r -f $nombreArchSalida -d $nombreArchDace $1
    exit
# Generar ofertas a partir de los documentos de las coordinaciones
elif [[ $existe -eq 1 ]]; then
        echo "Libreoffice esta ejecutandose. Cierre el programa y vuelva a ejecutar" >&2
        exit 1
    else
        listaInsumos=$(ls $caminoDirArchs | grep .doc)
        # Para debugging
        #echo $listaInsumos
        echo "Procesando los DOCS..."
        office=$(whereis soffice | awk '{print $2}')
        for arch in $listaInsumos; do
            echo -e "\t$caminoDirArchs$arch"
            $office --convert-to fodt "$caminoDirArchs$arch" --outdir \
                "$caminoDirArchs" --headless 1> /dev/null
        done
        echo "Completo"
        if [[ $? -eq 0 ]]; then
            echo "Ejecutando procesadorOfertas"
            if [[ -z $caminoDirArchs ]]; then
                echo "Archivos por argumentos"
                $python_bin procesadorOfertas.py -m $nomArchMaterias \
                    -f $nombreArchSalida -d $nombreArchDace $@
                # Linea para debugging
                # $python_bin pruebas/pruebaShell.py -m $nomArchMaterias \
                #     -f $nombreArchSalida -d $nombreArchDace $@
                exit
            else
                echo "Directorio como argumento"
                $python_bin procesadorOfertas.py -m $nomArchMaterias \
                    -f $nombreArchSalida -d $nombreArchDace \
                        --input-dir=$caminoDirArchs \
                # Linea para debugging
                # $python_bin pruebas/pruebaShell.py -m $nomArchMaterias \
                #     -f $nombreArchSalida -d $nombreArchDace \
                #         --input-dir=$caminoDirArchs
                exit
            fi
        else
            echo "No se pudo preprocesar los DOCS"
            exit 1
        fi
    fi
fi

#whereis python3 | grep -oE '/usr\/bin\/python3(\.[[:digit:]])?[[:space:]]'