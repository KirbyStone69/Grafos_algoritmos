"""Dibujo del grafo y representación visual de los eventos de búsqueda."""
import math
from dataclasses import dataclass
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView
from .nodos import EtiquetaPeso, NodoGrafico
from .tema import ACTIVO, FONDO, LINEA, NEON


@dataclass
class AristaGrafica:
    origen: object
    destino: object
    item: object
    etiqueta: EtiquetaPeso


class EscenaGrafo(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodos = {}
        self.aristas = {}
        self.paso = None
        self.particula = None
        self.pesos_visibles = True
        self.setBackgroundBrush(QColor(FONDO))

    @staticmethod
    def identificador(origen, destino, clave):
        return (frozenset((origen, destino)), clave)

    def cargar(self, grafo):
        self.nodos.clear()
        self.aristas.clear()
        self.clear()
        self.paso = None
        for nodo, datos in grafo.nodes(data=True):
            item = NodoGrafico(datos['valor'], datos['pixel'])
            self.addItem(item)
            self.nodos[nodo] = item
        for u, v, clave, datos in grafo.edges(keys=True, data=True):
            inicio = self.nodos[u].pos()
            fin = self.nodos[v].pos()
            dx, dy = fin.x() - inicio.x(), fin.y() - inicio.y()
            distancia = math.hypot(dx, dy)
            claves = list(grafo[u][v])
            indice = claves.index(clave)
            offset = (indice - (len(claves) - 1) / 2) * 65
            control = (inicio + fin) / 2 + QPointF(
                -dy / (distancia or 1) * offset, dx / (distancia or 1) * offset)
            camino = QPainterPath(inicio)
            if distancia:
                camino.quadTo(control, fin)
            else:
                camino.cubicTo(inicio + QPointF(-70, -90), fin + QPointF(70, -90), fin)
            item = self.addPath(camino, QPen(QColor(LINEA), 2))
            item.setOpacity(0.75)
            item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
            item.setToolTip(f'{u} ↔ {v} · peso {datos["weight"]} · arista {clave}')
            etiqueta = EtiquetaPeso(datos['weight'])
            centro = camino.pointAtPercent(0.5)
            rect = etiqueta.boundingRect()
            etiqueta.setPos(centro.x() - rect.width() / 2, centro.y() - rect.height() / 2)
            etiqueta.setVisible(self.pesos_visibles)
            self.addItem(etiqueta)
            self.aristas[self.identificador(u, v, clave)] = AristaGrafica(u, v, item, etiqueta)
        limites = self.itemsBoundingRect().adjusted(-60, -60, 60, 60)
        self.setSceneRect(limites)
        self.particula = self.addEllipse(-5, -5, 10, 10,
                                         QPen(Qt.PenStyle.NoPen), QColor(NEON))
        self.particula.setZValue(4)
        self.particula.setVisible(False)
        self.particula.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def mostrar_pesos(self, visible):
        self.pesos_visibles = visible
        for arista in self.aristas.values():
            arista.etiqueta.setVisible(visible)

    def representar(self, paso=None):
        self.paso = paso
        self.particula.setVisible(False)
        ruta = set(paso.ruta) if paso else set()
        for nodo, item in self.nodos.items():
            item.estado(visitado=bool(paso and nodo in paso.visitados),
                        actual=bool(paso and nodo == paso.actual), ruta=nodo in ruta)
        ruta_aristas = {self.identificador(a.origen, a.destino, a.clave)
                        for a in paso.aristas_ruta} if paso else set()
        activa = self.identificador(paso.arista.origen, paso.arista.destino,
                                   paso.arista.clave) if paso and paso.arista else None
        for identificador, arista in self.aristas.items():
            resaltada = identificador == activa or identificador in ruta_aristas
            arista.item.setPen(QPen(QColor(NEON if resaltada else LINEA),
                                   4 if resaltada else 2))
            arista.item.setOpacity(1 if resaltada or not paso else 0.45)
            arista.etiqueta.setBrush(QColor(ACTIVO if resaltada else '#e1f5e8'))

    def parpadear_ruta(self, iluminado):
        if self.paso and self.paso.tipo == 'fin':
            for nodo in self.paso.ruta:
                self.nodos[nodo].parpadear(iluminado)

    def animar(self, progreso):
        if not self.paso or not self.paso.arista:
            self.particula.setVisible(False)
            return
        paso = self.paso.arista
        arista = self.aristas[self.identificador(paso.origen, paso.destino, paso.clave)]
        t = 0.1 + 0.8 * progreso
        if arista.origen != paso.origen:
            t = 1 - t
        self.particula.setPos(arista.item.path().pointAtPercent(t))
        self.particula.setVisible(True)


class VistaGrafo(QGraphicsView):
    def __init__(self, escena):
        super().__init__(escena)
        self.ajuste_automatico = True
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        self.setBackgroundBrush(QColor(FONDO))
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def zoom(self, factor):
        if 0.15 <= self.transform().m11() * factor <= 6:
            self.ajuste_automatico = False
            self.scale(factor, factor)

    def wheelEvent(self, event):
        self.zoom(1.15 if event.angleDelta().y() > 0 else 1 / 1.15)
        event.accept()

    def ajustar(self):
        self.ajuste_automatico = True
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.ajuste_automatico and not self.sceneRect().isEmpty():
            self.ajustar()
