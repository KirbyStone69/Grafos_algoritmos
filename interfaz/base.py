"""Contrato mínimo: cada algoritmo decide cómo configurar y visualizar su búsqueda."""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget


class InterfazAlgoritmo(QWidget):
    mensaje = pyqtSignal(str)

    def cargar_grafo(self, grafo):
        """Recibe el grafo seleccionado. Cada interfaz decide cómo representarlo."""
        raise NotImplementedError

    def detener(self):
        """Cancela sus animaciones al salir de la pestaña o cerrar la aplicación."""
        raise NotImplementedError
