"""Parámetros propios: un origen a todos los nodos o a un destino opcional."""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFormLayout, QLabel, QLineEdit, QWidget
from modelos.validacion import validar_extremos


class ConfiguracionBellmanFord(QWidget):
    cambiada = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        formulario = QFormLayout(self)
        self.origen = QLineEdit('17')
        self.destino = QLineEdit()
        self.destino.setPlaceholderText('Vacío: todos los nodos')
        for campo in (self.origen, self.destino):
            campo.setClearButtonEnabled(True)
            campo.textChanged.connect(lambda _: self.cambiada.emit())
        formulario.addRow('Origen', self.origen)
        formulario.addRow('Destino opcional', self.destino)
        nota = QLabel('Solo grafo original con negativos.\nHasta |V|−1 pasadas y verificación final.')
        nota.setWordWrap(True)
        formulario.addRow(nota)

    def parametros(self, grafo):
        texto = self.destino.text().strip()
        if texto:
            origen, destino = validar_extremos(grafo, self.origen.text(), texto)
        else:
            try:
                origen, _ = validar_extremos(grafo, self.origen.text(), self.origen.text())
            except ValueError:
                raise ValueError('Nodo origen no existe.') from None
            destino = None
        return {'origen': origen, 'destino': destino}
