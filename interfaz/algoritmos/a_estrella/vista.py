"""Interfaz completa de A*: dibujo, configuracion, panel y reproduccion."""
import math
from PyQt6.QtCore import QRectF, QTimer
from PyQt6.QtGui import QColor, QImage, QPainter
from PyQt6.QtWidgets import (
    QCheckBox, QFileDialog, QHBoxLayout, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)
from modelos.grafos import obtener_adyacencia, tiene_negativos
from ...escena import EscenaGrafo, VistaGrafo
from .panel import PanelAEstrella
from ...reproductor import Reproductor
from ...celebracion import ParpadeoRuta
from ...tema import FONDO
from ...base import InterfazAlgoritmo


class InterfazAEstrella(InterfazAlgoritmo):
    def __init__(self, grafo, algoritmo, parent=None):
        super().__init__(parent)
        self.algoritmo = algoritmo
        self.grafo = grafo
        self.escena = EscenaGrafo(self)
        self.vista = VistaGrafo(self.escena)
        self.reproductor = Reproductor(self)
        self.celebracion = ParpadeoRuta(self)
        self.celebracion.fase_cambiada.connect(self.escena.parpadear_ruta)
        self.panel = PanelAEstrella()
        self._construir()
        self._conectar()
        self.escena.cargar(self.grafo)
        self.actualizar_compatibilidad()
        self.cambiar_velocidad(self.panel.velocidad.value())
        QTimer.singleShot(0, self.vista.ajustar)

    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        barra = QHBoxLayout()
        barra.addStretch()
        for texto, accion in [('Ajustar', self.vista.ajustar),
                               ('+', lambda: self.vista.zoom(1.2)),
                               ('-', lambda: self.vista.zoom(1 / 1.2)),
                               ('Guardar PNG', self.guardar_png)]:
            boton = QPushButton(texto)
            boton.clicked.connect(accion)
            barra.addWidget(boton)
        self.pesos = QCheckBox('Pesos')
        self.pesos.setChecked(True)
        barra.addWidget(self.pesos)
        layout.addLayout(barra)
        cuerpo = QHBoxLayout()
        cuerpo.addWidget(self.vista, 1)
        cuerpo.addSpacing(6)
        cuerpo.addWidget(self.panel)
        layout.addLayout(cuerpo, 1)

    def _conectar(self):
        self.pesos.toggled.connect(self.escena.mostrar_pesos)
        self.panel.buscar.clicked.connect(self.buscar)
        self.panel.play.clicked.connect(self.alternar)
        self.panel.atras.clicked.connect(self.reproductor.anterior)
        self.panel.adelante.clicked.connect(self.reproductor.siguiente)
        self.panel.reiniciar.clicked.connect(self.reproductor.reiniciar)
        self.panel.velocidad.valueChanged.connect(self.cambiar_velocidad)
        self.panel.parametros_cambiados.connect(self.invalidar)
        self.reproductor.paso_cambiado.connect(self.mostrar_paso)
        self.reproductor.progreso.connect(self.escena.animar)
        self.reproductor.reproduciendo.connect(
            lambda activo: self.panel.play.setText('Pausar' if activo else 'Reproducir'))

    def actualizar_compatibilidad(self):
        compatible = not tiene_negativos(self.grafo)
        self.panel.buscar.setEnabled(compatible)
        self.panel.compatibilidad.setText(
            'Listo para A*' if compatible else
            'A* requiere pesos >= 0. Selecciona "Pesos positivos".')

    def invalidar(self, *_):
        self.celebracion.detener()
        self.reproductor.limpiar()
        self.panel.limpiar()
        self.escena.representar()
        self.actualizar_compatibilidad()

    def cargar_grafo(self, grafo):
        self.celebracion.detener()
        self.reproductor.limpiar()
        self.grafo = grafo
        self.escena.cargar(self.grafo)
        self.panel.limpiar()
        self.actualizar_compatibilidad()
        self.vista.ajustar()

    def buscar(self):
        self.celebracion.detener()
        if tiene_negativos(self.grafo):
            self.actualizar_compatibilidad()
            return
        self.reproductor.limpiar()
        try:
            params = self.panel.configuracion.parametros(self.grafo)
        except ValueError as e:
            self.panel.limpiar()
            self.escena.representar()
            QMessageBox.warning(self, 'Nodos no validos', str(e))
            return

        # Extraer posiciones del grafo para la heuristica
        usar_h = params.pop('usar_heuristica', False)
        posiciones = None
        if usar_h:
            posiciones = {
                nodo: self.grafo.nodes[nodo].get('pixel', (0, 0))
                for nodo in self.grafo.nodes
            }

        try:
            resultado = self.algoritmo.ejecutar(
                obtener_adyacencia(self.grafo),
                origen=params['origen'],
                destino=params['destino'],
                posiciones=posiciones,
                usar_heuristica=usar_h,
            )

        except ValueError as e:
            self.panel.estado.setText(str(e))
            return
        self.panel.controles(True)
        self.reproductor.cargar(resultado)
        self.reproductor.iniciar()

    def mostrar_paso(self, indice, paso):
        self.celebracion.detener()
        self.escena.representar(paso)
        self.panel.mostrar(indice, paso, self.reproductor.resultado)
        if paso.tipo == 'fin' and paso.ruta:
            self.celebracion.iniciar()

    def alternar(self):
        if self.reproductor.timer.isActive():
            self.reproductor.pausar()
        else:
            self.reproductor.iniciar()

    def cambiar_velocidad(self, valor):
        self.reproductor.duracion = 150 + (10 - valor) * 180

    def guardar_png(self):
        destino, _ = QFileDialog.getSaveFileName(self, 'Guardar grafo', 'ruta_a_estrella.png', 'PNG (*.png)')
        if not destino:
            return
        rect = self.escena.sceneRect()
        imagen = QImage(math.ceil(rect.width() * 2), math.ceil(rect.height() * 2),
                        QImage.Format.Format_ARGB32)
        imagen.fill(QColor(FONDO))
        painter = QPainter(imagen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.escena.render(painter, QRectF(0, 0, imagen.width(), imagen.height()), rect)
        painter.end()
        if not imagen.save(destino, 'PNG'):
            QMessageBox.warning(self, 'Error', 'No se pudo guardar la imagen.')
        else:
            self.mensaje.emit(f'Imagen guardada: {destino}')

    def detener(self):
        self.celebracion.detener()
        self.reproductor.pausar()
