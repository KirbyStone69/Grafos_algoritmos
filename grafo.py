"""Datos transcritos de grafo.jpeg: nodos, pesos y posiciones.

La fotografía se analizó manualmente; este módulo carga esa transcripción.
Las lecturas dudosas están documentadas en README.md.
"""
from pathlib import Path
import json
import networkx as nx

BASE = Path(__file__).resolve().parent
# Coordenadas (x, y) sobre la fotografía de 1600 x 1200 píxeles.
POSICIONES = {
    29: (58, 328), 7: (275, 325), 21: (54, 484),
    24: (49, 737), 11: (210, 606), 14: (344, 610),
    6: (520, 477), 9: (518, 609), 10: (348, 805),
    27: (318, 981), 4: (526, 956), 18: (631, 958),
    8: (662, 646), 15: (777, 474), 0: (985, 362),
    44: (1152, 306), 1: (980, 646), 12: (801, 832),
    66: (743, 1115), 13: (930, 1113), 16: (1040, 984),
    23: (1037, 775), 3: (1147, 474), 2: (1146, 647),
    5: (1346, 431), 69: (1345, 648), 20: (1538, 530),
    25: (1535, 743), 17: (1191, 856), 70: (1447, 924),
}
# (origen, destino, peso). Se conservan las aristas paralelas.
ARISTAS = [
    (29, 7, 5),
    (29, 21, 3),
    (21, 24, 2),
    (21, 11, -2),
    (24, 11, -7),
    (7, 11, 5),
    (7, 14, 3),
    (7, 6, 10),
    (7, 1, 20),
    (11, 14, 9),
    (11, 10, 7),
    (14, 6, 5),
    (14, 9, 5),
    (14, 10, 9),
    (14, 4, 8),
    (6, 9, -7),
    (6, 8, 4),
    (6, 15, 3),
    (9, 10, -3),
    (10, 27, 9),
    (10, 4, 6),
    (10, 1, 5),
    (27, 4, 3),
    (27, 66, 1),
    (4, 18, 5),
    (4, 8, 15),
    (18, 12, 4),
    (18, 66, 6),
    (8, 15, 2),
    (8, 1, 7),
    (8, 12, 9),
    # Lectura provisional: aparecen 8 y 9 en la conexión 15–0.
    (15, 0, 8),
    (15, 0, 9),
    (15, 1, 8),
    (0, 44, 70),
    (0, 1, 2),
    (44, 3, 80),
    (44, 5, 69),
    (1, 2, 3),
    (1, 12, 7),
    (1, 23, 7),
    (12, 66, 7),
    (12, 13, 9),
    (12, 16, 16),
    (12, 16, 3),
    # Lectura manuscrita provisional: −777.
    (66, 13, -777),
    (13, 16, 3),
    (23, 16, -11),
    (23, 2, 3),
    (16, 17, 7),
    (3, 2, 9),
    (3, 5, 2),
    (3, 69, -6),
    (2, 69, 11),
    (2, 17, 5),
    (5, 69, 3),
    (5, 20, -2),
    (69, 20, 3),
    (69, 25, 6),
    (69, 17, 4),
    (69, 70, 8),
    (20, 25, 7),
    (25, 70, 17),
    (17, 70, 6),
]


def crear_grafo():
    """Carga los datos en un MultiGraph no dirigido, sin dibujarlo.

    `pixel`: (x, y) desde la esquina superior izquierda de la imagen.
    `pos`: (x, -y) en un sistema cartesiano, conservando la distribución.
    """
    grafo = nx.MultiGraph(imagen='grafo.jpeg', dimensiones=(1600, 1200))
    for nodo, (x, y) in POSICIONES.items():
        grafo.add_node(nodo, valor=nodo, pos=(x, -y), pixel=(x, y))
    for origen, destino, peso in ARISTAS:
        grafo.add_edge(origen, destino, weight=peso, valor=peso)
    return grafo


def crear_grafo_positivo():
    """Copia independiente con los mismos nodos y pesos en valor absoluto."""
    grafo = crear_grafo()
    for _, _, datos in grafo.edges(data=True):
        datos['weight'] = abs(datos['weight'])
        datos['valor'] = datos['weight']
    return grafo


if __name__ == '__main__':
    G = crear_grafo()
    salida = BASE / 'grafo_datos.json'
    salida.write_text(
        json.dumps(nx.node_link_data(G), ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(f'Grafo cargado: {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas.')
    print(f'Datos guardados en {salida}')
