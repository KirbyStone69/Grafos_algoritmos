"""Dijkstra propio: cola de prioridad, relajaciones y reconstrucción de ruta.

No importa NetworkX ni Qt. Recibe una lista de adyacencia y produce eventos
con instantáneas para visualizar el algoritmo sin mezclarlo con el dibujo.
"""
from heapq import heappop, heappush
from itertools import count
from math import inf, isfinite

from .tipos import Adyacencia, Arista, Paso, Resultado


def ejecutar_dijkstra(adyacencia: Adyacencia, origen, destino) -> Resultado:
    if origen not in adyacencia or destino not in adyacencia:
        raise ValueError('El origen y el destino deben existir en el grafo.')
    for conexiones in adyacencia.values():
        for conexion in conexiones:
            if conexion.destino not in adyacencia:
                raise ValueError('Una conexión apunta a un nodo inexistente.')
            if not isfinite(conexion.peso) or conexion.peso < 0:
                raise ValueError('Dijkstra requiere pesos finitos y no negativos.')

    distancias = {nodo: inf for nodo in adyacencia}
    distancias[origen] = 0
    predecesores = {}
    aristas_previas = {}
    visitados = set()
    pasos = []
    orden = count()  # Permite empates sin comparar identificadores de nodos.
    pendientes = [(0, next(orden), origen)]

    def registrar(tipo, descripcion, actual=None, arista=None,
                  ruta=(), aristas_ruta=()):
        pasos.append(Paso(tipo, descripcion, actual, arista,
                          distancias.copy(), predecesores.copy(),
                          frozenset(visitados), ruta, aristas_ruta))

    registrar('inicio', f'Iniciar en {origen}: distancia 0; los demás nodos, ∞.', origen)
    while pendientes:
        distancia, _, actual = heappop(pendientes)
        if actual in visitados or distancia != distancias[actual]:
            continue  # Entrada desactualizada de la cola de prioridad.
        visitados.add(actual)
        registrar('seleccionar', f'Fijar nodo {actual}, el pendiente de menor distancia: {distancia:g}.', actual)
        if actual == destino:
            ruta = [destino]
            aristas_ruta = []
            while ruta[-1] != origen:
                arista = aristas_previas[ruta[-1]]
                aristas_ruta.append(arista)
                ruta.append(arista.origen)
            ruta = tuple(reversed(ruta))
            aristas_ruta = tuple(reversed(aristas_ruta))
            registrar('fin', f'Ruta {" → ".join(map(str, ruta))}. Costo total: {distancia:g}.',
                      actual, ruta=ruta, aristas_ruta=aristas_ruta)
            return Resultado(origen, destino, distancia, ruta, aristas_ruta,
                             tuple(pasos), True)

        for conexion in adyacencia[actual]:
            vecino = conexion.destino
            arista = Arista(actual, vecino, conexion.clave, conexion.peso)
            registrar('examinar', f'Examinar {actual} → {vecino}, peso {conexion.peso:g}.', actual, arista)
            if vecino in visitados:
                registrar('descartar', f'{vecino} ya tiene una distancia definitiva.', actual, arista)
                continue
            candidato = distancia + conexion.peso
            anterior = distancias[vecino]
            if candidato < anterior:
                distancias[vecino] = candidato
                predecesores[vecino] = actual
                aristas_previas[vecino] = arista
                heappush(pendientes, (candidato, next(orden), vecino))
                antes = '∞' if anterior == inf else f'{anterior:g}'
                registrar('actualizar', f'{vecino}: {antes} → {candidato:g} = {distancia:g} + {conexion.peso:g}; predecesor {actual}.', actual, arista)
            else:
                registrar('descartar', f'{candidato:g} no mejora la distancia {anterior:g} de {vecino}.', actual, arista)

    registrar('sin_ruta', f'No existe una ruta de {origen} a {destino}.')
    return Resultado(origen, destino, inf, (), (), tuple(pasos), False)
