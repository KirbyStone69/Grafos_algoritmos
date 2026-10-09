"""Adaptador: NetworkX almacena los datos; los algoritmos reciben adyacencia."""
from grafo import crear_grafo, crear_grafo_positivo
from algoritmos.tipos import Conexion


def cargar_grafos():
    return {'original': crear_grafo(), 'positivo': crear_grafo_positivo()}


def obtener_adyacencia(grafo):
    return {
        nodo: tuple(Conexion(vecino, clave, datos['weight'])
                    for vecino, aristas in grafo[nodo].items()
                    for clave, datos in aristas.items())
        for nodo in grafo.nodes
    }


def tiene_negativos(grafo):
    return any(datos['weight'] < 0 for _, _, datos in grafo.edges(data=True))
