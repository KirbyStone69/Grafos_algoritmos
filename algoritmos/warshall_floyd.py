"""Floyd–Warshall propio: distancias y recorridos para todos los pares.

Registra cada comparación (i,j,k). Las instantáneas comparten las filas que
no cambiaron, evitando copiar dos matrices completas por cada evento.
R contiene el vértice intermedio, como en el XLSX. S contiene el siguiente
salto, para reconstruir las rutas sin interpretar R como una arista directa.
"""
from dataclasses import dataclass
from math import inf, isfinite
from .tipos import Adyacencia, Arista


@dataclass(frozen=True)
class PasoFloyd:
    tipo: str
    iteracion: int
    k: int | None
    i: int | None
    j: int | None
    distancias: tuple
    recorridos: tuple
    anterior: float = inf
    izquierdo: float = inf
    derecho: float = inf
    candidato: float = inf
    mejora: bool | None = None
    comparaciones: int = 0
    cambios: int = 0


@dataclass(frozen=True)
class ResultadoFloyd:
    nodos: tuple
    distancias: tuple
    recorridos: tuple
    siguientes: tuple
    directas: dict
    ciclos: tuple
    afectados: frozenset
    pasos: tuple[PasoFloyd, ...]
    finales_iteracion: tuple[int, ...]

    def consultar(self, origen, destino):
        indices = {nodo: i for i, nodo in enumerate(self.nodos)}
        if origen not in indices or destino not in indices:
            raise ValueError('El origen y el destino deben existir en el grafo.')
        i, j = indices[origen], indices[destino]
        costo = self.distancias[i][j]
        if costo == -inf:
            raise ValueError('No existe mínimo finito: este par está afectado por un ciclo negativo.')
        if costo == inf:
            return inf, (), ()
        ruta, aristas = [origen], []
        actual = i
        while actual != j:
            siguiente = self.siguientes[actual][j]
            if siguiente is None or len(ruta) > len(self.nodos):
                raise ValueError('No se pudo reconstruir una ruta válida.')
            aristas.append(self.directas[actual, siguiente])
            ruta.append(self.nodos[siguiente])
            actual = siguiente
        return costo, tuple(ruta), tuple(aristas)


def _cambiar(matriz, fila, columna, valor):
    nueva = list(matriz[fila])
    nueva[columna] = valor
    return matriz[:fila] + (tuple(nueva),) + matriz[fila + 1:]


def ejecutar_warshall_floyd(adyacencia: Adyacencia):
    nodos = tuple(adyacencia)
    indices = {nodo: i for i, nodo in enumerate(nodos)}
    n = len(nodos)
    inicial = [[0 if i == j else inf for j in range(n)] for i in range(n)]
    siguientes = [[i if i == j else None for j in range(n)] for i in range(n)]
    directas = {}
    for u, conexiones in adyacencia.items():
        for c in conexiones:
            if c.destino not in indices:
                raise ValueError('Una conexión apunta a un nodo inexistente.')
            try:
                finito = isfinite(c.peso)
            except (TypeError, OverflowError):
                finito = False
            if not finito:
                raise ValueError('Floyd–Warshall requiere pesos numéricos finitos.')
            i, j = indices[u], indices[c.destino]
            if c.peso < inicial[i][j]:
                inicial[i][j] = c.peso
                siguientes[i][j] = j
                directas[i, j] = Arista(u, c.destino, c.clave, c.peso)
    d = tuple(map(tuple, inicial))
    r = tuple(tuple(None for _ in nodos) for _ in nodos)
    pasos = [PasoFloyd('inicio', 0, None, None, None, d, r)]
    finales, comparaciones, cambios = [], 0, 0
    for k in range(n):
        pasos.append(PasoFloyd('intermedio', k + 1, k, None, None, d, r,
                               comparaciones=comparaciones, cambios=cambios))
        for i in range(n):
            for j in range(n):
                antes, izquierda, derecha = d[i][j], d[i][k], d[k][j]
                candidato = izquierda + derecha if izquierda != inf and derecha != inf else inf
                if izquierda != inf and derecha != inf and isinstance(candidato, float) and not isfinite(candidato):
                    raise ValueError('La suma de pesos excede el rango numérico.')
                mejora = candidato < antes
                comparaciones += 1
                if mejora:
                    cambios += 1
                    d = _cambiar(d, i, j, candidato)
                    r = _cambiar(r, i, j, nodos[k])
                    siguientes[i][j] = siguientes[i][k]
                pasos.append(PasoFloyd('comparar', k + 1, k, i, j, d, r, antes,
                                       izquierda, derecha, candidato, mejora, comparaciones, cambios))
        finales.append(len(pasos))
        pasos.append(PasoFloyd('iteracion_fin', k + 1, k, None, None, d, r,
                               comparaciones=comparaciones, cambios=cambios))
    ciclos_indices = tuple(k for k in range(n) if d[k][k] < 0)
    afectados = frozenset((nodos[i], nodos[j]) for i in range(n) for j in range(n)
                         if any(d[i][k] != inf and d[k][j] != inf for k in ciclos_indices))
    # Se determina la alcanzabilidad antes de insertar −∞: evita mezclar
    # nodos inalcanzables con los pares afectados por ciclos negativos.
    for i in range(n):
        for j in range(n):
            if (nodos[i], nodos[j]) in afectados:
                d = _cambiar(d, i, j, -inf)
                r = _cambiar(r, i, j, None)
                siguientes[i][j] = None
    pasos.append(PasoFloyd('fin', n, None, None, None, d, r,
                           comparaciones=comparaciones, cambios=cambios))
    return ResultadoFloyd(nodos, d, r, tuple(map(tuple, siguientes)), directas,
                          tuple(nodos[k] for k in ciclos_indices), afectados,
                          tuple(pasos), tuple(finales))
