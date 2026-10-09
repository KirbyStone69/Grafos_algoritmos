"""Cada algoritmo define sus propios campos y su validación de parámetros."""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFormLayout, QLabel, QLineEdit, QWidget
from modelos.validacion import validar_extremos


class ConfiguracionDijkstra(QWidget):
    cambiada = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        formulario = QFormLayout(self)
        self.origen = QLineEdit('17')
        self.destino = QLineEdit('10')
        self.origen.setPlaceholderText('Número del nodo origen')
        self.destino.setPlaceholderText('Número del nodo destino')
        for campo in (self.origen, self.destino):
            campo.setClearButtonEnabled(True)
            campo.textChanged.connect(lambda _: self.cambiada.emit())
        formulario.addRow('Origen', self.origen)
        formulario.addRow('Destino', self.destino)
        formulario.addRow(QLabel('Cola de prioridad · pesos ≥ 0'))

    def parametros(self, grafo):
        origen, destino = validar_extremos(grafo, self.origen.text(), self.destino.text())
        return {'origen': origen, 'destino': destino}


CONFIGURACIONES = {'dijkstra': ConfiguracionDijkstra}
