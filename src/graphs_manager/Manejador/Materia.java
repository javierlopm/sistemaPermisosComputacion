/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Manejador;

import java.util.ArrayList;

/**
 *
 * @author naqv1991
 */
public class Materia {

    private final String nombre;
    private final String codigo;
    private final String nota;
    private final int creditos;
    private ArrayList<String> listaPermisos;

    public Materia(String nombre, String codigo, String nota, int creditos) {
        this.nombre = nombre;
        this.codigo = codigo;
        this.nota = nota;
        this.creditos = creditos;
        listaPermisos = new ArrayList<>();
    }


    public void setListaPermisos(ArrayList<String> listaPermisos) {
        this.listaPermisos = listaPermisos;

    }

    public ArrayList<String> getListaPermisos() {
        return this.listaPermisos;

    }

    public String getNombre() {

        return nombre;
    }

    public String getCodigo() {

        return codigo;
    }

    public String getNota() {

        return nota;
    }

    public int getCredito() {

        return creditos;
    }

}
