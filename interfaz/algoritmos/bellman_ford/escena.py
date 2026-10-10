"""Grafo de Bellman–Ford con distancias provisionales visibles junto a los nodos."""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen
from ...escena import EscenaGrafo
from ...nodos import EtiquetaPeso
from ...tema import NEON
from .vectores import numero


class EscenaBellmanFord(EscenaGrafo):
    def cargar(self, grafo):
        super().cargar(grafo)
        self.distancias_graficas = {}
        for nodo, item in self.nodos.items():
            distancia = EtiquetaPeso('—')
            distancia.setParentItem(item)
            distancia.setPos(-distancia.boundingRect().width() / 2, 27)
            self.distancias_graficas[nodo] = distancia

    def representar(self, paso=None):
        super().representar(paso)
        for nodo, etiqueta in self.distancias_graficas.items():
            etiqueta.setText(numero(paso.distancias[nodo]) if paso else '—')
            etiqueta.setPos(-etiqueta.boundingRect().width() / 2, 27)

    def animar(self, progreso):
        if self.paso and self.paso.tipo == 'ciclo_negativo':
            self.particula.setVisible(False)
            return
        super().animar(progreso)

    def mostrar_ciclo(self, resultado):
        for arco in resultado.aristas_ciclo:
            item = self.aristas[self.identificador(arco.origen, arco.destino, arco.clave)].item
            item.setPen(QPen(QColor(NEON), 4, Qt.PenStyle.DashLine))
            item.setOpacity(1)
