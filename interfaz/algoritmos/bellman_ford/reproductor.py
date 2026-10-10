"""Reproducción por bloques: mantiene toda la traza y reduce los redibujados."""
from ...reproductor import Reproductor


class ReproductorBellmanFord(Reproductor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bloque = 1

    def tick(self):
        if self.bloque == 1:
            return super().tick()
        if not self.resultado:
            self.pausar()
            return
        ultimo = len(self.resultado.pasos) - 1
        self.mostrar(min(self.indice + self.bloque, ultimo))
        if self.indice == ultimo:
            self.pausar()
        else:
            self.progreso.emit(0.5)
