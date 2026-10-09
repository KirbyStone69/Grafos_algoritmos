"""Cada algoritmo aporta una interfaz completa, sin reutilización obligatoria."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from PyQt6.QtWidgets import QApplication, QLabel, QSpinBox, QVBoxLayout
from algoritmos.registro import ALGORITMOS, Algoritmo
from interfaz.base import InterfazAlgoritmo
from interfaz.registro import INTERFACES
from interfaz.ventana import VentanaGrafo


class InterfazDePrueba(InterfazAlgoritmo):
    """Diseño de prueba sin matrices, origen/destino ni reproductor de Dijkstra."""
    def __init__(self, grafo, algoritmo, parent=None):
        super().__init__(parent)
        self.algoritmo = algoritmo
        self.grafo = grafo
        self.detenciones = 0
        self.cargas = 0
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Configuración propia de otro algoritmo'))
        self.profundidad = QSpinBox()
        layout.addWidget(self.profundidad)

    def cargar_grafo(self, grafo):
        self.grafo = grafo
        self.cargas += 1

    def detener(self):
        self.detenciones += 1


class InterfacesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_cada_pestana_posee_su_interfaz_configuracion_y_matrices(self):
        # Esta entrada solo existe en la prueba: no anuncia un algoritmo ficticio.
        especificacion = Algoritmo('prueba', 'Otro diseño', True, lambda *_: None)
        fabricas = dict(INTERFACES, prueba=InterfazDePrueba)
        w = VentanaGrafo(ALGORITMOS + (especificacion,), fabricas)
        try:
            dijkstra = w.interfaz_actual
            self.assertTrue(dijkstra.isAncestorOf(dijkstra.panel))
            self.assertTrue(dijkstra.isAncestorOf(dijkstra.matrices))
            self.assertFalse(hasattr(w, 'panel'))
            self.assertFalse(hasattr(w, 'matrices'))
            dijkstra.buscar()
            self.assertTrue(dijkstra.reproductor.timer.isActive())
            w.pestanas.setCurrentIndex(1)
            otra = w.interfaz_actual
            self.assertIsInstance(otra, InterfazDePrueba)
            self.assertFalse(hasattr(otra, 'matrices'))
            self.assertFalse(hasattr(otra, 'panel'))
            self.assertFalse(dijkstra.reproductor.timer.isActive())
            otra.profundidad.setValue(7)
            w.selector_grafo.setCurrentIndex(0)
            self.assertEqual(otra.cargas, 1)
            self.assertEqual(otra.grafo[66][13][0]['weight'], -777)
            self.assertFalse(dijkstra.panel.buscar.isEnabled())
            w.pestanas.setCurrentIndex(0)
            self.assertEqual(otra.detenciones, 1)
            self.assertEqual(otra.profundidad.value(), 7)
            w.selector_grafo.setCurrentIndex(1)
            self.assertTrue(dijkstra.panel.buscar.isEnabled())
            dijkstra.buscar()
            self.assertEqual(dijkstra.reproductor.resultado.distancia, 13)
            dijkstra.reproductor.pausar()
            dijkstra.reproductor.mostrar(len(dijkstra.reproductor.resultado.pasos) - 1)
            self.assertTrue(dijkstra.celebracion.timer.isActive())
            w.pestanas.setCurrentIndex(1)
            self.assertFalse(dijkstra.celebracion.timer.isActive())
        finally:
            w.close()
            w.deleteLater()
            self.app.processEvents()


if __name__ == '__main__':
    unittest.main()
