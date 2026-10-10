"""Contenedor general: selección de grafo y pestañas de interfaces independientes."""
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget
from algoritmos.registro import ALGORITMOS
from modelos.grafos import cargar_grafos
from .registro import INTERFACES


class VentanaGrafo(QMainWindow):
    def __init__(self, algoritmos=ALGORITMOS, interfaces=None):
        super().__init__()
        self.setWindowTitle('Rutas · Algoritmos')
        self.resize(1440, 920)
        self.setMinimumSize(1000, 760)
        self.grafos = cargar_grafos()
        self.grafo = self.grafos['positivo']
        self._indice_anterior = 0
        self.algoritmos = tuple(algoritmos)
        fabricas = INTERFACES if interfaces is None else interfaces
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        barra = QHBoxLayout()
        titulo = QLabel('RUTAS / GRAFOS')
        titulo.setObjectName('titulo')
        barra.addWidget(titulo)
        barra.addSpacing(20)
        barra.addWidget(QLabel('Datos'))
        self.selector_grafo = QComboBox()
        self.selector_grafo.addItem('Original · con negativos', 'original')
        self.selector_grafo.addItem('Pesos positivos', 'positivo')
        self.selector_grafo.setCurrentIndex(1)
        barra.addWidget(self.selector_grafo)
        barra.addStretch()
        layout.addLayout(barra)
        self.pestanas = QTabWidget()
        for algoritmo in self.algoritmos:
            interfaz = fabricas[algoritmo.identificador](self.grafo, algoritmo)
            interfaz.mensaje.connect(lambda texto: self.statusBar().showMessage(texto, 5000))
            self.pestanas.addTab(interfaz, algoritmo.nombre)
        layout.addWidget(self.pestanas, 1)
        self.selector_grafo.currentIndexChanged.connect(self.cambiar_grafo)
        self.pestanas.currentChanged.connect(self.cambiar_interfaz)
        self.statusBar().showMessage('Rueda: zoom · Arrastrar: desplazar · Dijkstra: 17 → 10')

    @property
    def interfaz_actual(self):
        return self.pestanas.currentWidget()

    def cambiar_grafo(self, *_):
        self.grafo = self.grafos[self.selector_grafo.currentData()]
        for indice in range(self.pestanas.count()):
            self.pestanas.widget(indice).cargar_grafo(self.grafo)

    def cambiar_interfaz(self, indice):
        anterior = self.pestanas.widget(self._indice_anterior)
        if anterior is not None:
            anterior.detener()
        self._indice_anterior = indice
        self.statusBar().showMessage(f'{self.algoritmos[indice].nombre} · Rueda: zoom · Arrastrar: desplazar')
        preferido = self.algoritmos[indice].grafo_preferido
        if preferido is not None:
            self.selector_grafo.setCurrentIndex(self.selector_grafo.findData(preferido))

    def closeEvent(self, event):
        for indice in range(self.pestanas.count()):
            self.pestanas.widget(indice).detener()
        super().closeEvent(event)
