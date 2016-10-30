/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Manejador;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Iterator;

/**
 *
 * @author karen
 */
public class ManejadorSolicitudes {

    public ArrayList<String> est = new ArrayList<>();

    public ManejadorSolicitudes() {

    }

    /**
     *
     * @param nombrePermiso: Es el nombre del permiso que ha sido seleccionado
     * el cual debe estar escrito en el siguiente formato ./nombrePermiso.sh
     * @return Una lista de Strings que contiene los carnets resultantes de la
     * consulta. Necesitamos esta lista para los casos en que debamos
     * intersectar varios permisos
     * @throws IOException
     */
    public ArrayList<String> obtenerResultados(String nombrePermiso) throws IOException {
        ArrayList<String> resultado = new ArrayList<>();
        String linea;
        ProcessBuilder proc = new ProcessBuilder("sh", "-c", nombrePermiso);
        Process p = proc.start();

        InputStream stdout = p.getInputStream();
        BufferedReader reader = new BufferedReader(new InputStreamReader(stdout));

        while ((linea = reader.readLine()) != null) {
            resultado.add(linea);
        }
        return (resultado);
    }

    /*
     * Esta funcion nos devuelve un String con el resultado cuando sabemos que el resultado
     * es solo una linea
     */
    public String obtenerResultadoString(String nombrePermiso) throws IOException {
        String resultado = "";
        ProcessBuilder proc = new ProcessBuilder("sh", "-c", nombrePermiso);
        Process p = proc.start();

        InputStream stdout = p.getInputStream();
        BufferedReader reader = new BufferedReader(new InputStreamReader(stdout));

        return (reader.readLine());
    }

    /**
     *
     * @param lista: Una lista de Strings con los carnets seleccionados.
     * @return devuelve un arreglo de Strings con los carnets de la consulta
     */
    public String[] resultadosATexto(ArrayList<String> lista) {
        String[] textoResultado = new String[1000];
        Iterator<String> it = lista.iterator();
        int i = 0;
        while (it.hasNext()) {
            String actual = it.next();
            textoResultado[i] = actual;
            i++;
        }
        return textoResultado;
    }

    /**
     * Se agregan los elementos de la lista1 en la lista2 verificando que el
     * elemento que se agregara no este previamente en la lista2 para evitar los
     * duplicados.
     *
     * @param lista1 Lista que sera agregada a lista2
     * @param lista2 Lista a la que se le agregaran los elementos de lista1
     */
    public void agregarSinDuplicados(ArrayList<String> lista1, ArrayList<String> lista2) {
        for (String carnet : lista1) {
            if (!lista2.contains(carnet)) {
                lista2.add(carnet);
            }
        }
    }

    /**
     * Se utiliza para la lista de permisos en los que se quiere que en dicha lista
     * se tengan aquellos estudiantes que hayan pedido todos esos permisos, es decir,
     * es una conjuncion de permisos
     * @param lista1 Resultados de estudiantes filtrados por una consulta dada
     * @param lista2 Lista que posee los estudiantes filtrados y que se le hara la conjuncion
     * con la nueva lista1
     */
    public void conjuncion(ArrayList<String> lista1, ArrayList<String> lista2) {
        if (lista2.isEmpty()) {
            for (String carnet : lista1) {
                lista2.add(carnet);
            }
        } else {

            // Eliminamos de la lista 2 los que no esten en la lista 1
            for (String carnet : lista1) {
                if (!lista1.contains(carnet) && lista2.contains(carnet)) {
                    lista2.remove(carnet);
                }
            }
            // Eliminamos de la lista 2 todos los que no estan en la lista 1
            ArrayList<String> copiaLista2 = new ArrayList<>();
            copiaLista2.addAll(lista2);
            for (String carnet : copiaLista2) {
                if (lista2.contains(carnet) && !lista1.contains(carnet)) {
                    lista2.remove(carnet);
                }
            }
        }
    }

}
