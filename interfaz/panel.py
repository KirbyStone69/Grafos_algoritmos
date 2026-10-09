"""Configuración específica por algoritmo y controles compactos de reproducción."""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QSizePolicy, QTabWidget, QVBoxLayout, QWidget
from algoritmos.registro import ALGORITMOS
from .configuraciones import CONFIGURACIONES


class PanelBusqueda(QWidget):
    parametros_cambiados = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(290)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        titulo = QLabel('Búsqueda de ruta')
        titulo.setObjectName('titulo')
        layout.addWidget(titulo)
        self.pestanas = QTabWidget()
        self.pestanas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.configuraciones = {}
        for algoritmo in ALGORITMOS:
            configuracion = CONFIGURACIONES[algoritmo.identificador]()
            configuracion.cambiada.connect(self.parametros_cambiados)
            self.configuraciones[algoritmo.identificador] = configuracion
            self.pestanas.addTab(configuracion, algoritmo.nombre)
        layout.addWidget(self.pestanas)
        self.compatibilidad = QLabel()
        self.compatibilidad.setWordWrap(True)
        layout.addWidget(self.compatibilidad)
        self.buscar = QPushButton('Buscar y animar')
        layout.addWidget(self.buscar)
        navegacion = QHBoxLayout()
        self.atras = QPushButton('←')
        self.play = QPushButton('Reproducir')
        self.adelante = QPushButton('→')
        self.reiniciar = QPushButton('↺')
        for boton, ayuda in [(self.atras, 'Paso anterior'), (self.play, 'Reproducir / pausar'),
                              (self.adelante, 'Paso siguiente'), (self.reiniciar, 'Reiniciar pasos')]:
            boton.setToolTip(ayuda)
            navegacion.addWidget(boton)
        layout.addLayout(navegacion)
        layout.addWidget(QLabel('Velocidad de reproducción'))
        self.velocidad = QSlider(Qt.Orientation.Horizontal)
        self.velocidad.setRange(1, 10)
        self.velocidad.setValue(7)
        layout.addWidget(self.velocidad)
        self.estado = QLabel()
        self.estado.setObjectName('estado')
        self.estado.setWordWrap(True)
        layout.addWidget(self.estado)
        self.resultado = QLabel()
        self.resultado.setWordWrap(True)
        layout.addWidget(self.resultado)
        leyenda = QLabel('● Visitado: verde oscuro\n◉ Actual: borde verde neón\n● Ruta ganadora: fosforescente\n─ Final: cinco parpadeos rápidos')
        leyenda.setWordWrap(True)
        layout.addWidget(leyenda)
        layout.addStretch()
        self.limpiar()

    @property
    def configuracion(self):
        return self.pestanas.currentWidget()

    @property
    def origen(self):
        return self.configuracion.origen

    @property
    def destino(self):
        return self.configuracion.destino

    def controles(self, cargado):
        for boton in (self.atras, self.play, self.adelante, self.reiniciar):
            boton.setEnabled(cargado)

    def limpiar(self):
        self.controles(False)
        self.estado.setText('Listo para buscar')
        self.resultado.setText('Costo final: —')
        self.play.setText('Reproducir')

    def mostrar(self, indice, paso, resultado):
        actual = str(paso.actual) if paso.actual is not None else '—'
        self.estado.setText(f'Paso {indice + 1}/{len(resultado.pasos)} · Nodo actual: {actual}')
        self.atras.setEnabled(indice > 0)
        self.adelante.setEnabled(indice < len(resultado.pasos) - 1)
        if paso.tipo == 'fin':
            self.resultado.setText(f'Costo: {resultado.distancia:g}\n' + ' → '.join(map(str, resultado.ruta)))
        elif paso.tipo == 'sin_ruta':
            self.resultado.setText('Destino inalcanzable')
        else:
            self.resultado.setText('Costo final: —')
