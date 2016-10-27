/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Manejador;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 *
 * @author naqv1991
 */
public class ManejadorExpediente {

    public Expediente expediente; 
    
    public ManejadorExpediente(String carnet) {
        expediente = new Expediente("./HTML/" + carnet + ".html", carnet);
        
    }
    /**
     *
     * @param pathInicial Carpetas donde se encuentran los archivos de los
     * estudiantes que han solicitado permiso
     * @param mascara Terminacion del archivo que queremos obtener.
     * @param listaFicheros Contiene todos los archivos que esten en el path inicialmente 
     * colocado.  Guarda el path completo en donde estan estos archivos.
     * @param busquedaRecursiva
     */
    
    public static void ListarArchivoEstudiantes(String pathInicial, String mascara,
            LinkedList<File> listaFicheros, boolean busquedaRecursiva) {

        File directorioInicial = new File(pathInicial);
        if (directorioInicial.isDirectory()) {
            File[] ficheros = directorioInicial.listFiles();

            for (File fichero : ficheros) {
                if (fichero.isDirectory() && busquedaRecursiva) {
                    ListarArchivoEstudiantes(fichero.getAbsolutePath(), mascara, listaFicheros, busquedaRecursiva);
                } else if (Pattern.matches(mascara, fichero.getName())) {
                    listaFicheros.add(fichero);
                }
            }
        }
    }
    
/** Funcion que busca la terminación que se le especifica en la entrada
 * 
 * @param mascara : En nuestro caso queremos que sean .txt
 * 
 */
    public static String terminacionArchivo(String mascara) {
        mascara = mascara.replace(".", "\\.");
        mascara = mascara.replace("*", ".*");
        mascara = mascara.replace("?", ".");
        return mascara;
    }

    /** Funcion que se encarga de buscar en las carpetas pendiente, aceptados y rechazados.
     *  Una vez que obtiene estos estudiantes, obtiene el expediente correspondiente con la 
     *  pagina de expediente.dii.usb.ve
     * @throws IOException 
     */
    
    public static void obtenerExpedientes() throws IOException {
        LinkedList<File> ficherosJava = new LinkedList<>();
        String nombrePermiso = "";
        String h = "";

        /*Aqui se obtienen todos los .txt de los estudiantes que hayan pedido permiso    */
        ListarArchivoEstudiantes("./estudiantes/pendientes/", terminacionArchivo("*.txt"), ficherosJava, true);
        ListarArchivoEstudiantes("./estudiantes/aprobados/", terminacionArchivo("*.txt"), ficherosJava, true);
        ListarArchivoEstudiantes("./estudiantes/rechazados/", terminacionArchivo("*.txt"), ficherosJava, true);

        
        /*Se colocan todos los  path de los archivos .txt en una sola linea para aplicar un regex a esa linea   */
        for (File ficherosJava1 : ficherosJava) {
            h += ficherosJava1.toString() + " ";
        }

       
       /* Expresion regular que solo obtiene el carnet de los estudiantes en el path completo de donde estan sus .txt
          Recordemos que los .txt tienen como nombre el carné del estudiante*/

        Pattern p4 = Pattern.compile("(.*?)([0-9]*-[0-9]*).txt(.*?)");
        Matcher m4 = p4.matcher(h);
        ArrayList<String> listaEstudiantesPermisos = new ArrayList<>();

        while (m4.find()) {
            listaEstudiantesPermisos.add(m4.group(2)); // Lista de estudiante tiene todos los carnés.
           
        }

        
        /*Para cada uno de los carnés obtenidos, se obtiene el html asociado a su expediente    */
        
        for (String listaEstudiantesPermiso : listaEstudiantesPermisos) {
            nombrePermiso = "./HTML/crawler.sh" + " " + listaEstudiantesPermiso;
            ArrayList<String> resultado = new ArrayList<>();
            String linea;
            ProcessBuilder proc = new ProcessBuilder("sh", "-c", nombrePermiso);
            Process p = proc.start();
            InputStream stdout = p.getInputStream();
            BufferedReader reader = new BufferedReader(new InputStreamReader(stdout));
            while ((linea = reader.readLine()) != null) {
                resultado.add(linea);
            }
        }

    }

    public void devolverPromedio() throws FileNotFoundException {

        String promedio;
        Pattern p = Pattern.compile("(.*?)Acumulado: ([1-5].[0-9]*)\n(.*?)");
        Matcher prom = p.matcher(this.expediente.getHtml());
        ArrayList<String> listaPromedios = new ArrayList<>();

        while (prom.find()) {
            listaPromedios.add(prom.group(2));

        }
        // Tomamos el ultimo de los promedios que es el actual del estudiante
        promedio = listaPromedios.get(listaPromedios.size() - 1);
        this.expediente.setPromedio(promedio);


    }

    public void obtenerMaterias() throws FileNotFoundException {
        String htmlExp = this.expediente.getHtml();
        Pattern p = Pattern.compile("(.*?)<td width=\"50\" align=\"left\">([A-Z]{2,3}[0-9]*)</td>\n(.*?)");
        Matcher m = p.matcher(htmlExp);
        ArrayList<String> codigo = new ArrayList<>();
        while (m.find()) {
            codigo.add(m.group(2));
        }
        int i = 0;
        int n = codigo.size();

        /*
         Pattern p2 = Pattern.compile("(.*?)<td width=\"380\" align=\"left\">([A-ZÁÉÍÓÚÑ][[A-ZÁÉÍÓÚÑ,.1-3]*:[ \\t\\n\\x0B\\f\\r]]*[A-ZÁÉÍÓÚÑ,.1-3]*)</td>\n(.*?)");
         Matcher m2 = p2.matcher(html);
         ArrayList<String> nombreMateria = new ArrayList<>();

         while (m2.find()) {
         nombreMateria.add(m2.group(2));
         }
     
         int j = 0;
         int nn = nombreMateria.size();
         */
        Pattern p3 = Pattern.compile("(.*?)<td width=\"45\" align=\"center\">([[1-5]R]*)</td>\n(.*?)");
        Matcher m3 = p3.matcher(htmlExp);
        ArrayList<String> nota = new ArrayList<>();

        while (m3.find()) {

            if ("R".equals(m3.group(2))) {

                nota.add("0");

            } else {

                nota.add(m3.group(2));

            }
        }

        int j = 0;
        int nn = nota.size();

        Pattern p4 = Pattern.compile("(.*?)<td width=\"50\" align=\"center\">([2-5])</td>\n(.*?)");
        Matcher m4 = p4.matcher(htmlExp);
        ArrayList<Integer> credito = new ArrayList<>();

        while (m4.find()) {
            credito.add(Integer.parseInt(m4.group(2)));
        }

        //   n = nombreMateria.size();
        ArrayList<Materia> Materia = new ArrayList<>();

        for (i = 0; i < credito.size(); i++) {
            Materia mat = new Materia("hello", codigo.get(i), nota.get(i), credito.get(i));
            Materia.add(mat);
        }

        this.expediente.setListaMaterias(Materia);

    }

    /**
     * Metodo en el cual leemos el String devuelto por el programa en AWK que
     * nos dice los codigos de las materias que desea cursar en el siguiente
     * trimestre y lo almacenamos en un ArrayList de Strings el cual luego sera
     * recorrido para colorear el grafo.
     *
     * @throws IOException
     */
    public void leerMateriasPermisos() throws IOException {
        String carnet = this.expediente.getCarnet();
        ManejadorSolicitudes m = new ManejadorSolicitudes();
        ArrayList<String> listaResultados = new ArrayList<String>();
        String resultado;

        File estudiantePendiente = new File("estudiantes/pendientes/" + carnet + ".txt");
        File estudianteAprobado = new File("estudiantes/aprobados/" + carnet + ".txt");
        File estudianteRechazado = new File("estudiantes/rechazados/" + carnet + ".txt");

        // Indicamos de que carpeta proviene el estudiante para obtener sus datos
        String carpeta = "pendientes";
        if (estudiantePendiente.exists()) {
            carpeta = "pendientes";
        } else if (estudianteAprobado.exists()) {
            carpeta = "aprobados";
        } else if (estudianteRechazado.exists()) {
            carpeta = "rechazados";
        }

        resultado = m.obtenerResultadoString("awk -f ./ScriptsAWK/materiasPermisos.awk estudiantes/" + carpeta + "/" + carnet + ".txt");
        if (resultado != null){
            listaResultados = new ArrayList<>(Arrays.asList(resultado.split(", ")));
        }

        this.expediente.setPermisos(listaResultados);

    }

}
