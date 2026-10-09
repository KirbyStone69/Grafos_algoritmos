"""Control del tiempo y navegación de eventos; no ejecuta la búsqueda."""
from PyQt6.QtCore import QObject, QElapsedTimer, QTimer, pyqtSignal


class Reproductor(QObject):
    paso_cambiado = pyqtSignal(int, object)
    progreso = pyqtSignal(float)
    reproduciendo = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resultado = None
        self.indice = -1
        self.duracion = 600
        self.transcurrido = 0
        self.reloj = QElapsedTimer()
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self.tick)

    def cargar(self, resultado):
        self.pausar()
        self.resultado = resultado
        self.mostrar(0)

    def limpiar(self):
        self.pausar()
        self.resultado = None
        self.indice = -1
        self.transcurrido = 0

    def mostrar(self, indice):
        if not self.resultado:
            return
        self.indice = max(0, min(indice, len(self.resultado.pasos) - 1))
        self.transcurrido = 0
        self.paso_cambiado.emit(self.indice, self.resultado.pasos[self.indice])
        self.progreso.emit(0)

    def iniciar(self):
        if not self.resultado:
            return
        if self.indice == len(self.resultado.pasos) - 1:
            self.mostrar(0)
        self.reloj.start()
        self.timer.start()
        self.reproduciendo.emit(True)

    def pausar(self):
        self.timer.stop()
        self.reproduciendo.emit(False)

    def siguiente(self):
        self.pausar()
        self.mostrar(self.indice + 1)

    def anterior(self):
        self.pausar()
        self.mostrar(self.indice - 1)

    def reiniciar(self):
        self.pausar()
        self.mostrar(0)

    def tick(self):
        if not self.resultado:
            self.pausar()
            return
        self.transcurrido += self.reloj.restart()
        self.progreso.emit(min(1, self.transcurrido / self.duracion))
        if self.transcurrido >= self.duracion:
            if self.indice + 1 < len(self.resultado.pasos):
                self.mostrar(self.indice + 1)
            if self.indice == len(self.resultado.pasos) - 1:
                self.pausar()
