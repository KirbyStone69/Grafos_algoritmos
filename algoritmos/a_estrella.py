"""A* propio: lista abierta/cerrada con heuristica configurable, sin Qt ni NetworkX.

La heuristica predeterminada es 0 (A* optimo, equivalente a Dijkstra con
lista cerrada). La heuristica euclidiana es ilustrativa: puede no ser
admisible en este grafo porque los pesos no son proporcionales a la
distancia en pantalla, por lo que puede encontrar rutas suboptimas.
Solo acepta pesos no negativos.
"""
from heapq import heappop, heappush
from itertools import count
from math import inf, isfinite, sqrt

from .tipos import Adyacencia, Arista, Paso, Resultado


def _dist_euclidiana(pos, a, b):
    ax, ay = pos.get(a, (0, 0))
    bx, by = pos.get(b, (0, 0))
    return sqrt((ax - bx) ** 2 + (ay - by) ** 2)


def ejecutar_a_estrella(adyacencia: Adyacencia, origen, destino,
                        posiciones=None, usar_heuristica=False) -> Resultado:
    """Busca la ruta optima de origen a destino con A*.

    posiciones: dict {nodo: (x, y)} para la heuristica euclidiana.
    usar_heuristica: si True usa distancia euclidiana (ilustrativa, puede no
    ser admisible). Si False la heuristica es 0 y el resultado es siempre optimo.
    """
    if origen not in adyacencia or destino not in adyacencia:
        raise ValueError('El origen y el destino deben existir en el grafo.')
    for conexiones in adyacencia.values():
        for c in conexiones:
            if c.destino not in adyacencia:
                raise ValueError('Una conexion apunta a un nodo inexistente.')
            if not isfinite(c.peso) or c.peso < 0:
                raise ValueError('A* requiere pesos finitos y no negativos.')

    pos = posiciones or {}
    admisible = not usar_heuristica

    if usar_heuristica and pos:
        heuristica = {nodo: _dist_euclidiana(pos, nodo, destino)
                      for nodo in adyacencia}
    else:
        heuristica = {nodo: 0.0 for nodo in adyacencia}

    g = {nodo: inf for nodo in adyacencia}
    g[origen] = 0.0
    predecesores = {}
    aristas_previas = {}
    cerrado = set()
    pasos = []
    orden = count()
    abierto = [(heuristica[origen], 0.0, next(orden), origen)]

    modo = 'h=euclidiana (ilustrativa)' if usar_heuristica else 'h=0 (optimo garantizado)'

    def registrar(tipo, descripcion, actual=None, arista=None, ruta=(), aristas_ruta=()):
        pasos.append(Paso(tipo, descripcion, actual, arista,
                          g.copy(), predecesores.copy(),
                          frozenset(cerrado), ruta, aristas_ruta))

    registrar('inicio',
              f'A* {origen} a {destino}. {modo}. '
              f'f(n)=g(n)+h(n): g=costo real, h=heuristica.', origen)

    while abierto:
        f_actual, g_actual, _, actual = heappop(abierto)
        if actual in cerrado:
            continue
        cerrado.add(actual)
        h_actual = heuristica[actual]
        registrar('seleccionar',
                  f'Expandir {actual}: g={g_actual:g}  h={h_actual:.1f}  f={f_actual:.1f}.', actual)

        if actual == destino:
            ruta = [destino]
            aristas_ruta = []
            while ruta[-1] != origen:
                a = aristas_previas[ruta[-1]]
                aristas_ruta.append(a)
                ruta.append(a.origen)
            ruta = tuple(reversed(ruta))
            aristas_ruta = tuple(reversed(aristas_ruta))
            registrar('fin',
                      f'Ruta: {" -> ".join(map(str, ruta))}. Costo: {g_actual:g}.',
                      actual, ruta=ruta, aristas_ruta=aristas_ruta)
            return Resultado(origen, destino, g_actual, ruta, aristas_ruta, tuple(pasos), True)

        for conexion in adyacencia[actual]:
            vecino = conexion.destino
            arista = Arista(actual, vecino, conexion.clave, conexion.peso)
            if vecino in cerrado:
                registrar('descartar',
                          f'{vecino} ya en lista cerrada.', actual, arista)
                continue
            registrar('examinar',
                      f'Examinar {actual} -> {vecino}, w={conexion.peso:g}.', actual, arista)
            candidato_g = g_actual + conexion.peso
            if candidato_g < g[vecino]:
                g[vecino] = candidato_g
                predecesores[vecino] = actual
                aristas_previas[vecino] = arista
                f_vecino = candidato_g + heuristica[vecino]
                heappush(abierto, (f_vecino, candidato_g, next(orden), vecino))
                registrar('actualizar',
                          f'{vecino}: g={candidato_g:g}  h={heuristica[vecino]:.1f}  '
                          f'f={f_vecino:.1f}. Pred: {actual}.', actual, arista)
            else:
                registrar('descartar',
                          f'g={candidato_g:g} no mejora g={g[vecino]:g} de {vecino}.', actual, arista)

    registrar('sin_ruta', f'No hay ruta de {origen} a {destino}.')
    return Resultado(origen, destino, inf, (), (), tuple(pasos), False)
