/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Manejador;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;

/**
 *
 * @author naqv1991
 */
public class Expediente {

    private String html;
    private ArrayList<Materia> listaMaterias;
    private String promedio;
    private ArrayList<String> listaPermisos;
    private String carnet;

    public Expediente(String html, String carnet) {
        listaMaterias = new ArrayList<>();
        this.html = html;
        this.promedio = "";
        this.listaPermisos = new ArrayList<>();
        this.carnet = carnet;
    }

    public void htmlAString() throws FileNotFoundException {
        StringBuilder contentBuilder = new StringBuilder();
        try {
            BufferedReader in = new BufferedReader(new InputStreamReader(new FileInputStream(this.html)));
            String str;
            while ((str = in.readLine()) != null) {
                contentBuilder.append(str);
                contentBuilder.append("\n");
            }
            in.close();
        } catch (IOException e) {
            //NO MANEJAN LA PUTA EXCEPCION DEJAN ESTO VACIO
        }
        this.html = contentBuilder.toString();
        //return this.html;
    }

    public void setListaMaterias(ArrayList<Materia> ListaMaterias) {
        this.listaMaterias = ListaMaterias;

    }

    public void setPromedio(String prom) {
        this.promedio = prom;

    }

    public ArrayList<Materia> getListaMaterias() {

        return this.listaMaterias;
    }

    public String getHtml() {

        return this.html;
    }

    public void setPermisos(ArrayList<String> Permisos) {
        this.listaPermisos = Permisos;

    }

    public ArrayList<String> getPermisos() {
        return this.listaPermisos;

    }

    public String getPromedio() {
        return this.promedio;

    }

    public void setCarnet(String carnet) {
        this.carnet = carnet;

    }

    public String getCarnet() {
        return this.carnet;

    }

}
