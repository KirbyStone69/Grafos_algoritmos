"""Tablas de Floyd–Warshall: intermedio k, operandos y celda de resultado."""
from math import inf
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QBrush, QColor
from ...tema import FONDO, NEON, TEXTO


def numero(valor):
    if valor == inf:
        return '∞'
    if valor == -inf:
        return '−∞'
    return f'{valor:.4g}' if abs(valor) > 100000 else f'{valor:g}'


class ModeloFloyd(QAbstractTableModel):
    def __init__(self, tipo, parent=None):
        super().__init__(parent)
        self.tipo, self.nodos, self.paso = tipo, (), None

    def cargar(self, nodos):
        self.beginResetModel()
        self.nodos, self.paso = tuple(nodos), None
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.nodos)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.nodos)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self.nodos[section])
        return None

    def flags(self, index):
        return (Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable) if index.isValid() else Qt.ItemFlag.NoItemFlags

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        i, j = index.row(), index.column()
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if not self.paso:
            return '—' if role == Qt.ItemDataRole.DisplayRole else None
        p = self.paso
        valor = p.distancias[i][j]
        intermedio = p.recorridos[i][j]
        if role == Qt.ItemDataRole.DisplayRole:
            if self.tipo == 'distancias':
                return numero(valor)
            if valor in (inf, -inf):
                return '—'
            return str(intermedio if intermedio is not None else self.nodos[j])
        if role == Qt.ItemDataRole.ToolTipRole:
            return (f'{self.nodos[i]} → {self.nodos[j]}\nDistancia: {valor}\n'
                    + ('Sin recorrido mínimo finito.' if valor in (inf, -inf) else
                       f'Intermedio: {intermedio if intermedio is not None else "directo / camino vacío"}')
                    + '\nClic: consultar este par en el resultado final.')
        focos = {(p.i, p.j), (p.i, p.k), (p.k, p.j)} if p.i is not None else set()
        activo = (i, j) in focos
        cruz = p.k is not None and (i == p.k or j == p.k)
        if role == Qt.ItemDataRole.BackgroundRole:
            return QBrush(QColor(NEON if activo else '#305b3d' if cruz else FONDO))
        if role == Qt.ItemDataRole.ForegroundRole:
            return QBrush(QColor('#102b1a' if activo else TEXTO))
        return None

    def mostrar(self, paso):
        self.paso = paso
        if self.nodos:
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.nodos) - 1, len(self.nodos) - 1))
