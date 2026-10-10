"""Bellman–Ford propio con instantáneas de relajación y detección de ciclos.

No importa Qt ni NetworkX. El formato de pasos sigue las pasadas y preguntas
mostradas en Bellman-Ford__Ejemplo.pdf. En un grafo no dirigido el adaptador
aporta un arco en cada sentido, conservando su clave y peso.
"""
from collections import deque
from dataclasses import dataclass, field
from math import inf, isfinite
from .tipos import Adyacencia, Arista, Paso, Resultado


@dataclass(frozen=True)
class PasoBellmanFord(Paso):
    pasada: int = 0
    indice_arco: int = 0
    distancia_origen: float = inf
    distancia_anterior: float = inf
    candidato: float = inf
    respuesta: bool | None = None
    verificacion: bool = False


@dataclass(frozen=True)
class ResultadoBellmanFord(Resultado):
    distancias: dict = field(default_factory=dict)
    ciclo_negativo: bool = False
    ciclo: tuple = ()
    aristas_ciclo: tuple[Arista, ...] = ()
    afectados: frozenset = frozenset()
    pasadas: int = 0


def listar_arcos(adyacencia: Adyacencia):
    return tuple(Arista(u, c.destino, c.clave, c.peso)
                 for u, conexiones in adyacencia.items() for c in conexiones)


def _extraer_ciclo(arcos, distancias, anteriores, cantidad):
    prueba = distancias.copy()
    previos = anteriores.copy()
    ultimo = None
    for a in arcos:
        if prueba[a.origen] != inf and prueba[a.origen] + a.peso < prueba[a.destino]:
            prueba[a.destino] = prueba[a.origen] + a.peso
            previos[a.destino] = a
            ultimo = a.destino
    if ultimo is None:
        return (), ()
    nodo = ultimo
    for _ in range(cantidad):
        nodo = previos[nodo].origen
    inicio = nodo
    camino = []
    while True:
        a = previos[nodo]
        camino.append(a)
        nodo = a.origen
        if nodo == inicio:
            break
    camino = tuple(reversed(camino))
    return (camino[0].origen,) + tuple(a.destino for a in camino), camino


def ejecutar_bellman_ford(adyacencia: Adyacencia, origen, destino=None):
    if origen not in adyacencia:
        raise ValueError('Nodo origen no existe.')
    if destino is not None and destino not in adyacencia:
        raise ValueError('Nodo destino no existe.')
    arcos = listar_arcos(adyacencia)
    for a in arcos:
        if a.destino not in adyacencia:
            raise ValueError('Una conexión apunta a un nodo inexistente.')
        try:
            finito = isfinite(a.peso)
        except (TypeError, OverflowError):
            finito = False
        if not finito:
            raise ValueError('Bellman–Ford requiere pesos numéricos finitos.')
    distancias = {n: inf for n in adyacencia}
    distancias[origen] = 0
    predecesores, anteriores, pasos = {}, {}, []
    pasadas = 0

    def registrar(tipo, descripcion, actual=None, arista=None, pasada=0,
                  indice_arco=0, du=inf, antes=inf, candidato=inf,
                  respuesta=None, verificacion=False, ruta=(), aristas_ruta=()):
        pasos.append(PasoBellmanFord(
            tipo=tipo, descripcion=descripcion, actual=actual, arista=arista,
            distancias=distancias.copy(), predecesores=predecesores.copy(),
            visitados=frozenset(n for n, d in distancias.items() if d != inf),
            ruta=ruta, aristas_ruta=aristas_ruta, pasada=pasada, indice_arco=indice_arco,
            distancia_origen=du, distancia_anterior=antes, candidato=candidato,
            respuesta=respuesta, verificacion=verificacion))

    registrar('inicio', f'Inicializar d[{origen}] = 0; las demás distancias, ∞.', origen,
              indice_arco=1)
    for pasada in range(1, len(adyacencia)):
        pasadas = pasada
        cambios = False
        registrar('pasada', f'Iniciar pasada {pasada} de {len(adyacencia) - 1}.', pasada=pasada)
        for indice, a in enumerate(arcos, 1):
            du, antes = distancias[a.origen], distancias[a.destino]
            candidato = du + a.peso if du != inf else inf
            if du != inf and isinstance(candidato, float) and not isfinite(candidato):
                raise ValueError('La suma de pesos excede el rango numérico.')
            mejora = candidato < antes
            if mejora:
                distancias[a.destino] = candidato
                predecesores[a.destino] = a.origen
                anteriores[a.destino] = a
                cambios = True
            registrar('actualizar' if mejora else 'descartar',
                      f'Aplicar Relax al arco ({a.origen}, {a.destino}).', a.origen, a,
                      pasada, indice, du, antes, candidato, mejora)
        if not cambios:
            registrar('estable', 'No hubo cambios: terminar las pasadas y verificar.', pasada=pasada)
            break

    fase = len(adyacencia)
    registrar('verificacion', 'Verificar que d[v] ≤ d[u] + w(u,v) en cada arco alcanzable.',
              pasada=fase, verificacion=True)
    semillas = set()
    for indice, a in enumerate(arcos, 1):
        du, antes = distancias[a.origen], distancias[a.destino]
        candidato = du + a.peso if du != inf else inf
        if du != inf and isinstance(candidato, float) and not isfinite(candidato):
            raise ValueError('La suma de pesos excede el rango numérico.')
        cumple = antes <= candidato
        if du != inf and not cumple:
            semillas.add(a.destino)
        registrar('verificar', f'Verificar el arco ({a.origen}, {a.destino}).', a.origen, a,
                  fase, indice, du, antes, candidato, cumple, True)
    afectados = set(semillas)
    pendientes = deque(semillas)
    while pendientes:
        for conexion in adyacencia[pendientes.popleft()]:
            if conexion.destino not in afectados:
                afectados.add(conexion.destino)
                pendientes.append(conexion.destino)
    ciclo, aristas_ciclo = _extraer_ciclo(arcos, distancias, anteriores, len(adyacencia)) if semillas else ((), ())
    for n in afectados:
        distancias[n] = -inf
        # Π no define un camino mínimo cuando d = −∞. El testigo del ciclo
        # se conserva aparte y se extrajo antes de limpiar estos enlaces.
        predecesores.pop(n, None)
        anteriores.pop(n, None)
    ruta, aristas_ruta = (), ()
    distancia = distancias[destino] if destino is not None else distancias[origen]
    encontrado = (not semillas) if destino is None else distancia not in (inf, -inf)
    if destino is not None and encontrado:
        inversa, enlaces = [destino], []
        vistos = set()
        while inversa[-1] != origen:
            if inversa[-1] in vistos or inversa[-1] not in anteriores:
                raise ValueError('No se pudo reconstruir un camino mínimo válido.')
            vistos.add(inversa[-1])
            a = anteriores[inversa[-1]]
            enlaces.append(a)
            inversa.append(a.origen)
        ruta, aristas_ruta = tuple(reversed(inversa)), tuple(reversed(enlaces))
    if semillas:
        descripcion = 'Ciclo negativo alcanzable: ' + ' → '.join(map(str, ciclo))
        descripcion += '. Los nodos afectados no tienen distancia mínima finita.'
        if destino is not None and encontrado:
            descripcion += f' El destino {destino} no está afectado; su costo mínimo es {distancia:g}.'
        registrar('ciclo_negativo', descripcion, arista=aristas_ciclo[0] if aristas_ciclo else None,
                  actual=ciclo[0] if ciclo else None, pasada=fase, verificacion=True,
                  ruta=ruta, aristas_ruta=aristas_ruta)
    elif destino is not None and not encontrado:
        registrar('sin_ruta', f'No hay camino de {origen} a {destino}.', pasada=fase)
    else:
        registrar('fin', 'Verificación correcta: distancias y predecesores finales.', destino,
                  pasada=fase, ruta=ruta, aristas_ruta=aristas_ruta)
    return ResultadoBellmanFord(origen, destino, distancia, ruta, aristas_ruta,
                               tuple(pasos), encontrado, distancias.copy(), bool(semillas),
                               ciclo, aristas_ciclo, frozenset(afectados), pasadas)
