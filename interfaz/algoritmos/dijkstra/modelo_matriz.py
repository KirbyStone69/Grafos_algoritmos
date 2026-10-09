"""Modelos de tabla de solo lectura, sincronizados con los pasos de búsqueda."""
import math
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QBrush, QColor, QFont
from ...tema import FONDO, NEON, TEXTO, VISITADO


def identidad(arista):
    return frozenset((arista.origen, arista.destino)), arista.clave


class ModeloMatriz(QAbstractTableModel):
    def __init__(self, matrices, tipo, parent=None):
        super().__init__(parent)
        self.tipo = tipo
        self.cargar(matrices)

    def cargar(self, matrices):
        self.beginResetModel()
        self.matrices = matrices
        self.valores = getattr(matrices, self.tipo)
        self.filas = {nodo: indice for indice, nodo in enumerate(matrices.nodos)}
        self.columnas = {identidad(arista): indice for indice, arista in enumerate(matrices.aristas)}
        self.pesos = {}
        for arista in matrices.aristas:
            par = frozenset((arista.origen, arista.destino))
            self.pesos.setdefault(par, []).append(arista.peso)
        self.actual = None
        self.visitados = frozenset()
        self.consultadas = set()
        self.activas = set()
        self.columnas_activas = set()
        self.fila_cruz = None
        self.columna_cruz = None
        self.paso = None
        self.progreso = 0
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.matrices.nodos)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.matrices.nodos) if self.tipo == 'adyacencia' else len(self.matrices.aristas)

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled if index.isValid() else Qt.ItemFlag.NoItemFlags

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        nodos = self.matrices.nodos
        es_nodo = orientation == Qt.Orientation.Vertical or self.tipo == 'adyacencia'
        if role == Qt.ItemDataRole.DisplayRole:
            return str(nodos[section]) if es_nodo else f'e{section + 1}'
        if role == Qt.ItemDataRole.ToolTipRole:
            if es_nodo:
                return f'Nodo {nodos[section]}'
            a = self.matrices.aristas[section]
            return f'e{section + 1}: {a.origen} ↔ {a.destino} · clave {a.clave} · peso {a.peso:g}'
        activo = (section == self.fila_cruz if orientation == Qt.Orientation.Vertical
                  else section == self.columna_cruz if self.columna_cruz is not None
                  else section in self.columnas_activas if not es_nodo else False)
        visitado = es_nodo and nodos[section] in self.visitados
        if role == Qt.ItemDataRole.ForegroundRole:
            return QBrush(QColor(NEON if activo else '#91b49d'))
        if role == Qt.ItemDataRole.BackgroundRole and visitado:
            return QBrush(QColor(VISITADO))
        if role == Qt.ItemDataRole.FontRole and activo:
            fuente = QFont()
            fuente.setBold(True)
            return fuente
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        fila, columna = index.row(), index.column()
        celda = (fila, columna)
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self.valores[fila][columna])
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.ToolTipRole:
            nodo = self.matrices.nodos[fila]
            if self.tipo == 'adyacencia':
                vecino = self.matrices.nodos[columna]
                pesos = self.pesos.get(frozenset((nodo, vecino)), [])
                return f'{nodo} ↔ {vecino}: {len(pesos)} arista(s)\nPesos: ' + (', '.join(f'{p:g}' for p in pesos) or '—')
            a = self.matrices.aristas[columna]
            return f'Nodo {nodo} · e{columna + 1}: {a.origen} ↔ {a.destino}\nPeso: {a.peso:g} · clave: {a.clave}'
        if role == Qt.ItemDataRole.ForegroundRole:
            if celda in self.activas:
                return QBrush(QColor('#102b1a'))
            return QBrush(QColor(TEXTO if self.valores[fila][columna] else '#667e6e'))
        if role == Qt.ItemDataRole.BackgroundRole:
            if celda in self.activas:
                # Pulso suave sincronizado con la partícula de la arista activa.
                intensidad = 0.60 + 0.35 * math.sin(math.pi * self.progreso)
                neon, base = QColor(NEON), QColor(VISITADO)
                color = QColor(*(round(a * intensidad + b * (1 - intensidad))
                                 for a, b in zip(neon.getRgb()[:3], base.getRgb()[:3])))
                return QBrush(color)
            if celda in self.consultadas:
                return QBrush(QColor('#305b3d'))
            if self.matrices.nodos[fila] in self.visitados:
                return QBrush(QColor(VISITADO))
            return QBrush(QColor(FONDO))
        return None

    def celdas_arista(self, arista):
        u, v = self.filas[arista.origen], self.filas[arista.destino]
        if self.tipo == 'adyacencia':
            return {(u, v), (v, u)}
        columna = self.columnas[identidad(arista)]
        return {(u, columna), (v, columna)}

    def celdas_cruz(self, fila, columna=None):
        """Fila y columna completas, incluidas celdas con valor cero."""
        celdas = {(fila, c) for c in range(self.columnCount())}
        if columna is not None:
            celdas.update((f, columna) for f in range(self.rowCount()))
        return celdas

    def representar(self, paso=None, consultadas=()):
        self.paso = paso
        self.progreso = 0
        self.actual = paso.actual if paso else None
        self.visitados = paso.visitados if paso else frozenset()
        self.consultadas = set()
        for arista in consultadas:
            self.consultadas.update(self.celdas_arista(arista))
        self.activas = set()
        self.columnas_activas = set()
        self.fila_cruz = None
        self.columna_cruz = None
        if paso and paso.actual is not None:
            self.fila_cruz = self.filas[paso.actual]
            if paso.arista:
                self.fila_cruz = self.filas[paso.arista.origen]
                self.columna_cruz = (self.filas[paso.arista.destino]
                                     if self.tipo == 'adyacencia'
                                     else self.columnas[identidad(paso.arista)])
                self.columnas_activas.add(self.columnas[identidad(paso.arista)])
            elif self.tipo == 'adyacencia':
                self.columna_cruz = self.fila_cruz
            self.activas.update(self.celdas_cruz(self.fila_cruz, self.columna_cruz))
        # Al terminar también se conservan las conexiones de la ruta ganadora.
        for arista in paso.aristas_ruta if paso else ():
            self.activas.update(self.celdas_arista(arista))
            self.columnas_activas.add(self.columnas[identidad(arista)])
        if self.rowCount() and self.columnCount():
            self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1))
            self.headerDataChanged.emit(Qt.Orientation.Vertical, 0, self.rowCount() - 1)
            self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, self.columnCount() - 1)

    def animar(self, progreso):
        if not self.paso or not self.paso.arista:
            return
        self.progreso = progreso
        # La cruz se pulsa como una unidad, no celda por celda.
        if self.fila_cruz is not None and self.columnCount():
            self.dataChanged.emit(self.index(self.fila_cruz, 0),
                                  self.index(self.fila_cruz, self.columnCount() - 1),
                                  [Qt.ItemDataRole.BackgroundRole])
        if self.columna_cruz is not None and self.rowCount():
            self.dataChanged.emit(self.index(0, self.columna_cruz),
                                  self.index(self.rowCount() - 1, self.columna_cruz),
                                  [Qt.ItemDataRole.BackgroundRole])
