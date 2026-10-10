"""Lista de referencia de arcos y selección del arco actual del PDF."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from algoritmos.bellman_ford import listar_arcos


class ListaArcos(QListWidget):
    def cargar(self, adyacencia):
        self.clear()
        self.arcos = listar_arcos(adyacencia)
        self.indices = {}
        for i, a in enumerate(self.arcos):
            item = QListWidgetItem(f'{i + 1:03d}   ({a.origen} → {a.destino})   w = {a.peso:g}')
            item.setData(Qt.ItemDataRole.UserRole, i + 1)
            item.setToolTip(f'Clave de arista: {a.clave}. Clic: mostrar este arco en la pasada actual.')
            self.addItem(item)
            self.indices[a.origen, a.destino, a.clave] = i

    def mostrar(self, paso):
        if paso.arista:
            a = paso.arista
            indice = self.indices[a.origen, a.destino, a.clave]
            self.setCurrentRow(indice)
            self.scrollToItem(self.item(indice))
        else:
            self.setCurrentRow(-1)
