"""Vectores V, d y Π del PDF, presentados como tres filas de solo lectura."""
from math import inf
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem
from ...tema import NEON, TEXTO, VISITADO, FONDO


def numero(valor):
    if valor == inf:
        return '∞'
    if valor == -inf:
        return '−∞'
    return f'{valor:g}'


class TablaVectores(QTableWidget):
    def __init__(self, nodos, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.horizontalHeader().hide()
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setMinimumHeight(128)
        self.setMaximumHeight(155)
        self.cargar(nodos)

    def cargar(self, nodos):
        self.nodos = tuple(nodos)
        self.indices = {n: i for i, n in enumerate(self.nodos)}
        self.setRowCount(3)
        self.setColumnCount(len(self.nodos))
        self.setVerticalHeaderLabels(['V', 'd', 'Π'])
        for col, nodo in enumerate(self.nodos):
            self.setColumnWidth(col, 62)
            for fila, texto in enumerate((str(nodo), '—', '—')):
                self.setItem(fila, col, QTableWidgetItem(texto))
                self.item(fila, col).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def mostrar(self, paso):
        extremos = {paso.arista.origen, paso.arista.destino} if paso.arista else {paso.actual}
        for col, nodo in enumerate(self.nodos):
            self.item(1, col).setText(numero(paso.distancias[nodo]))
            self.item(2, col).setText(str(paso.predecesores.get(nodo, '—')))
            activo = nodo in extremos
            for fila in range(3):
                item = self.item(fila, col)
                item.setBackground(QBrush(QColor(NEON if activo else VISITADO if nodo in paso.visitados else FONDO)))
                item.setForeground(QBrush(QColor('#102b1a' if activo else TEXTO)))
                item.setToolTip('Distancia provisional hasta completar la verificación.'
                                if paso.tipo not in {'fin', 'ciclo_negativo', 'sin_ruta'} else
                                '−∞: afectado por ciclo negativo (Π no definido); ∞: inalcanzable.')
        if paso.arista:
            col = self.indices[paso.arista.destino]
            self.scrollToItem(self.item(1, col), QAbstractItemView.ScrollHint.EnsureVisible)
