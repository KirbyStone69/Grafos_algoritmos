"""Contenedor general: selección de grafo y pestañas de interfaces independientes."""
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget
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
        self.selector_grafo.addItem('Dirigido · Bellman–Ford', 'dirigido_bf')
        self.selector_grafo.setCurrentIndex(1)
        barra.addWidget(self.selector_grafo)
        self.btn_editor = QPushButton('✎ Editar grafo')
        self.btn_editor.setToolTip('Herramienta para agregar/eliminar nodos y aristas, y modificar pesos')
        self.btn_editor.clicked.connect(self.abrir_editor)
        barra.addWidget(self.btn_editor)
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
        self._dialogo_editor = None

    def abrir_editor(self):
        from .editor import EditorGrafo
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        if self._dialogo_editor is None or not self._dialogo_editor.isVisible():
            self._dialogo_editor = QDialog(self)
            self._dialogo_editor.setWindowTitle('Editor de Grafo (Nodos / Aristas / Pesos)')
            self._dialogo_editor.resize(360, 520)
            layout_diag = QVBoxLayout(self._dialogo_editor)
            self.editor = EditorGrafo(self.grafo, self._dialogo_editor)
            self.editor.grafo_modificado.connect(self.notificar_grafo_editado)
            layout_diag.addWidget(self.editor)
            self._dialogo_editor.show()
        else:
            self.editor.cargar_grafo(self.grafo)
            self._dialogo_editor.raise_()
            self._dialogo_editor.activateWindow()

    def notificar_grafo_editado(self, grafo):
        self.grafo = grafo
        for indice in range(self.pestanas.count()):
            self.pestanas.widget(indice).cargar_grafo(self.grafo)
        self.statusBar().showMessage('Grafo modificado. Pestañas actualizadas.', 4000)

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
