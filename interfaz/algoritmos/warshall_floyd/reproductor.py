"""Reproducción rápida de las matrices al terminar cada intermedio k."""
from ...reproductor import Reproductor


class ReproductorFloyd(Reproductor):
    por_intermedio = True

    def tick(self):
        if not self.por_intermedio:
            return super().tick()
        if not self.resultado:
            self.pausar()
            return
        ultimo = len(self.resultado.pasos) - 1
        siguiente = next((i for i in self.resultado.finales_iteracion if i > self.indice), ultimo)
        self.mostrar(siguiente)
        if self.indice == ultimo:
            self.pausar()
