"""Elementos gráficos de nodo y etiquetas; no contienen lógica de búsqueda."""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPen
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsSimpleTextItem
from .tema import FONDO, LINEA, NEON, NODO, TEXTO, VISITADO


class NodoGrafico(QGraphicsEllipseItem):
    def __init__(self, valor, posicion):
        super().__init__(-23, -23, 46, 46)
        self.setPos(*posicion)
        self.setZValue(3)
        self.setToolTip(f'Nodo {valor} · posición {posicion}')
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        texto = self.texto = QGraphicsSimpleTextItem(str(valor), self)
        texto.setFont(QFont('Sans Serif', 14, QFont.Weight.Bold))
        texto.setBrush(QColor(TEXTO))
        rect = texto.boundingRect()
        texto.setPos(-rect.width() / 2, -rect.height() / 2)
        texto.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.estado()

    def estado(self, visitado=False, actual=False, ruta=False):
        self.setBrush(QColor(NEON if ruta else VISITADO if visitado and not actual else NODO))
        self.setPen(QPen(QColor(NEON if actual or ruta else '#326045' if visitado else LINEA),
                         4 if actual or ruta else 2))
        self.texto.setBrush(QColor('#102b1a' if ruta else TEXTO))
        self.setOpacity(1)

    def parpadear(self, iluminado):
        self.setBrush(QColor(NEON if iluminado else VISITADO))
        self.texto.setBrush(QColor('#102b1a' if iluminado else TEXTO))



class EtiquetaPeso(QGraphicsSimpleTextItem):
    def __init__(self, valor):
        super().__init__(str(valor))
        self.setFont(QFont('Sans Serif', 11, QFont.Weight.Bold))
        self.setBrush(QColor(TEXTO))
        self.setZValue(2)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def paint(self, painter, option, widget=None):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(FONDO))
        painter.drawRoundedRect(self.boundingRect().adjusted(-3, -1, 3, 1), 3, 3)
        super().paint(painter, option, widget)
