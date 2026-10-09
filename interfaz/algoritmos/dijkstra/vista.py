"""Interfaz completa de Dijkstra: dibujo, configuración, matrices y reproducción."""
import math
from PyQt6.QtCore import QRectF, QTimer
from PyQt6.QtGui import QColor, QImage, QPainter
from PyQt6.QtWidgets import (
    QCheckBox, QFileDialog, QHBoxLayout, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)
from modelos.grafos import obtener_adyacencia, tiene_negativos
from ...escena import EscenaGrafo, VistaGrafo
from .panel import PanelDijkstra
from .matrices import PanelMatricesDijkstra
from ...reproductor import Reproductor
from ...celebracion import ParpadeoRuta
from ...tema import FONDO
from ...base import InterfazAlgoritmo


class InterfazDijkstra(InterfazAlgoritmo):
    def __init__(self, grafo, algoritmo, parent=None):
        super().__init__(parent)
        self.algoritmo = algoritmo
        self.grafo = grafo
        self.escena = EscenaGrafo(self)
        self.vista = VistaGrafo(self.escena)
        self.reproductor = Reproductor(self)
        self.celebracion = ParpadeoRuta(self)
        self.celebracion.fase_cambiada.connect(self.escena.parpadear_ruta)
        self.panel = PanelDijkstra()
        self.matrices = PanelMatricesDijkstra(self.grafo)
        self.construir_interfaz()
        self.conectar()
        self.escena.cargar(self.grafo)
        self.actualizar_compatibilidad()
        self.cambiar_velocidad(self.panel.velocidad.value())
        QTimer.singleShot(0, self.vista.ajustar)

    def construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        barra = QHBoxLayout()
        barra.addStretch()
        for texto, accion in [('Ajustar', self.vista.ajustar),
                               ('＋', lambda: self.vista.zoom(1.2)),
                               ('−', lambda: self.vista.zoom(1 / 1.2)),
                               ('Guardar PNG', self.guardar_png)]:
            boton = QPushButton(texto)
            boton.clicked.connect(accion)
            barra.addWidget(boton)
        self.pesos = QCheckBox('Pesos')
        self.pesos.setChecked(True)
        barra.addWidget(self.pesos)
        layout.addLayout(barra)
        cuerpo = QHBoxLayout()
        area_grafo = QWidget()
        area = QVBoxLayout(area_grafo)
        area.setContentsMargins(0, 0, 0, 0)
        area.addWidget(self.vista, 1)
        area.addWidget(self.matrices)
        cuerpo.addWidget(area_grafo, 1)
        cuerpo.addSpacing(6)
        cuerpo.addWidget(self.panel)
        layout.addLayout(cuerpo, 1)

    def conectar(self):
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
        self.reproductor.progreso.connect(self.matrices.animar)
        self.reproductor.reproduciendo.connect(
            lambda activo: self.panel.play.setText('Pausar' if activo else 'Reproducir'))

    def actualizar_compatibilidad(self):
        compatible = self.algoritmo.acepta_negativos or not tiene_negativos(self.grafo)
        self.panel.buscar.setEnabled(compatible)
        self.panel.compatibilidad.setText(
            f'Listo para {self.algoritmo.nombre}' if compatible else
            f'{self.algoritmo.nombre} requiere pesos ≥ 0. Selecciona «Pesos positivos».')

    def invalidar(self, *_):
        self.celebracion.detener()
        self.reproductor.limpiar()
        self.panel.limpiar()
        self.escena.representar()
        self.matrices.representar()
        self.actualizar_compatibilidad()

    def cargar_grafo(self, grafo):
        self.celebracion.detener()
        self.reproductor.limpiar()
        self.grafo = grafo
        self.escena.cargar(self.grafo)
        self.matrices.cargar(self.grafo)
        self.panel.limpiar()
        self.actualizar_compatibilidad()
        self.vista.ajustar()

    def buscar(self):
        self.celebracion.detener()
        if not self.algoritmo.acepta_negativos and tiene_negativos(self.grafo):
            self.actualizar_compatibilidad()
            return
        self.reproductor.limpiar()
        try:
            parametros = self.panel.configuracion.parametros(self.grafo)
        except ValueError as error:
            self.panel.limpiar()
            self.escena.representar()
            self.matrices.representar()
            QMessageBox.warning(self, 'Nodos no válidos', str(error))
            return
        try:
            resultado = self.algoritmo.ejecutar(obtener_adyacencia(self.grafo), **parametros)
        except ValueError as error:
            self.panel.estado.setText(str(error))
            return
        self.panel.controles(True)
        self.reproductor.cargar(resultado)
        self.reproductor.iniciar()

    def mostrar_paso(self, indice, paso):
        self.celebracion.detener()
        self.escena.representar(paso)
        self.panel.mostrar(indice, paso, self.reproductor.resultado)
        self.matrices.representar(indice, paso, self.reproductor.resultado)
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
        destino, _ = QFileDialog.getSaveFileName(self, 'Guardar grafo', 'ruta_dijkstra.png', 'PNG (*.png)')
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
        self.matrices.animacion.stop()
        self.matrices.contenido.setMaximumHeight(300 if self.matrices.boton.isChecked() else 0)
