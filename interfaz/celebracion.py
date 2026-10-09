"""Parpadeo final de la ruta: cinco ciclos rápidos, sin bloquear la interfaz."""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class ParpadeoRuta(QObject):
    fase_cambiada = pyqtSignal(bool)
    terminado = pyqtSignal()
    CICLOS = 5
    INTERVALO_MS = 80

    def __init__(self, parent=None):
        super().__init__(parent)
        self.transiciones = 0
        self.timer = QTimer(self)
        self.timer.setInterval(self.INTERVALO_MS)
        self.timer.timeout.connect(self.avanzar)

    @property
    def ciclos_completos(self):
        return self.transiciones // 2

    def iniciar(self):
        self.detener()
        self.transiciones = 0
        self.fase_cambiada.emit(True)
        self.timer.start()

    def detener(self):
        self.timer.stop()

    def avanzar(self):
        if not self.timer.isActive():
            return
        self.transiciones += 1
        self.fase_cambiada.emit(self.transiciones % 2 == 0)
        if self.ciclos_completos == self.CICLOS:
            self.detener()
            # El último estado es fosforescente y permanece visible.
            self.terminado.emit()
