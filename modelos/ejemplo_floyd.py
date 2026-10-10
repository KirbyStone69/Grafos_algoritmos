"""Lee la matriz inicial A–H del documento XLSX, usando solo la biblioteca estándar.

Las iteraciones escritas en el documento no se importan como resultados:
contienen inconsistencias. La diagonal `null` representa el camino vacío, 0.
"""
from math import cos, sin, pi, inf, isfinite
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import networkx as nx

ARCHIVO_EJEMPLO = Path(__file__).resolve().parents[1] / 'warshall_floyd.xlsx'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def cargar_ejemplo_floyd(archivo=ARCHIVO_EJEMPLO):
    try:
        with ZipFile(archivo) as zipfile:
            strings = []
            if 'xl/sharedStrings.xml' in zipfile.namelist():
                root = ET.fromstring(zipfile.read('xl/sharedStrings.xml'))
                strings = [''.join(t.text or '' for t in si.findall('.//m:t', NS)) for si in root]
            sheet = ET.fromstring(zipfile.read('xl/worksheets/sheet1.xml'))
            celdas = {}
            for c in sheet.findall('.//m:c', NS):
                v = c.find('m:v', NS)
                valor = v.text if v is not None else ''
                if c.get('t') == 's' and valor:
                    valor = strings[int(valor)]
                elif c.get('t') == 'inlineStr':
                    valor = ''.join(t.text or '' for t in c.findall('.//m:t', NS))
                celdas[c.get('r')] = valor
    except (OSError, KeyError, ValueError, ET.ParseError) as error:
        raise ValueError(f'No se pudo leer el ejemplo XLSX: {error}') from error
    columnas = 'BCDEFGHI'
    nodos = tuple(celdas.get(f'{col}13') for col in columnas)
    if nodos != tuple('ABCDEFGH'):
        raise ValueError('No se encontró la matriz inicial A–H del documento.')
    distancias = []
    for i, nodo in enumerate(nodos):
        if celdas.get(f'A{i + 14}') != nodo:
            raise ValueError('Los encabezados de la matriz inicial no coinciden.')
        fila = []
        for j, col in enumerate(columnas):
            valor = celdas.get(f'{col}{i + 14}', '').strip()
            if valor.lower() == 'null' and i == j:
                numero = 0
            elif valor == '∞':
                numero = inf
            else:
                try:
                    numero = float(valor)
                except ValueError as error:
                    raise ValueError(f'Peso inválido en {col}{i + 14}.') from error
                if not isfinite(numero):
                    raise ValueError('El XLSX contiene un peso no finito.')
                if numero.is_integer():
                    numero = int(numero)
            fila.append(numero)
        distancias.append(fila)
    if any(distancias[i][j] != distancias[j][i] for i in range(8) for j in range(8)):
        raise ValueError('La matriz inicial del ejemplo debe ser simétrica.')
    grafo = nx.MultiGraph(nombre='Ejemplo A–H del documento')
    for i, nodo in enumerate(nodos):
        x, y = 800 + 400 * cos(2 * pi * i / 8), 600 + 360 * sin(2 * pi * i / 8)
        grafo.add_node(nodo, valor=nodo, pixel=(x, y), pos=(x, -y))
    for i, u in enumerate(nodos):
        for j in range(i, len(nodos)):
            peso = distancias[i][j]
            if peso != inf and (i != j or peso != 0):
                grafo.add_edge(u, nodos[j], weight=peso, valor=peso)
    return grafo
