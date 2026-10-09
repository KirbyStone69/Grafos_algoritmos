"""Contrato común para los algoritmos y su reproducción paso a paso."""
from dataclasses import dataclass
from typing import Hashable, Mapping

NodoId = Hashable


@dataclass(frozen=True)
class Conexion:
    destino: NodoId
    clave: Hashable
    peso: float


Adyacencia = Mapping[NodoId, tuple[Conexion, ...]]


@dataclass(frozen=True)
class Arista:
    origen: NodoId
    destino: NodoId
    clave: Hashable
    peso: float


@dataclass(frozen=True)
class Paso:
    tipo: str
    descripcion: str
    actual: NodoId | None
    arista: Arista | None
    distancias: dict[NodoId, float]
    predecesores: dict[NodoId, NodoId]
    visitados: frozenset[NodoId]
    ruta: tuple[NodoId, ...] = ()
    aristas_ruta: tuple[Arista, ...] = ()


@dataclass(frozen=True)
class Resultado:
    origen: NodoId
    destino: NodoId
    distancia: float
    ruta: tuple[NodoId, ...]
    aristas_ruta: tuple[Arista, ...]
    pasos: tuple[Paso, ...]
    encontrado: bool
