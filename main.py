"""Entrada de la aplicación. Ejecutar: python main.py."""
import sys
from PyQt6.QtWidgets import QApplication
from interfaz.tema import ESTILO
from interfaz.ventana import VentanaGrafo


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Rutas · Dijkstra')
    app.setStyle('Fusion')
    app.setStyleSheet(ESTILO)
    ventana = VentanaGrafo()
    ventana.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
