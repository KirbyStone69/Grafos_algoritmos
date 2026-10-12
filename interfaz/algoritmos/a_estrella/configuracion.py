"""Parametros de A*: origen, destino y heuristica."""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QFormLayout, QLabel, QLineEdit, QWidget
from modelos.validacion import validar_extremos


class ConfiguracionAEstrella(QWidget):
    cambiada = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        formulario = QFormLayout(self)
        self.origen = QLineEdit('17')
        self.destino = QLineEdit('10')
        self.origen.setPlaceholderText('Numero de nodo origen')
        self.destino.setPlaceholderText('Numero de nodo destino')
        for campo in (self.origen, self.destino):
            campo.setClearButtonEnabled(True)
            campo.textChanged.connect(lambda _: self.cambiada.emit())
        formulario.addRow('Origen', self.origen)
        formulario.addRow('Destino', self.destino)
        self.usar_heuristica = QCheckBox('h=euclidiana (ilustrativa)')
        self.usar_heuristica.setChecked(False)
        self.usar_heuristica.setToolTip(
            'h=0: resultado optimo garantizado (como Dijkstra con lista cerrada).\n'
            'h=euclidiana: explora menos nodos pero puede dar ruta suboptima\n'
            'si los pesos no son proporcionales a la distancia en pantalla.')
        self.usar_heuristica.toggled.connect(lambda _: self.cambiada.emit())
        formulario.addRow(self.usar_heuristica)
        nota = QLabel('f(n) = g(n) + h(n)\ng: costo real acumulado\nh: heuristica (0 = optimo)')
        nota.setWordWrap(True)
        formulario.addRow(nota)

    def parametros(self, grafo):
        origen, destino = validar_extremos(grafo, self.origen.text(), self.destino.text())
        return {'origen': origen, 'destino': destino,
                'usar_heuristica': self.usar_heuristica.isChecked()}
