"""Matrices y registro visual del recorrido de Dijkstra."""
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QLabel, QLayout, QSizePolicy,
    QSplitter, QTableView, QToolButton, QVBoxLayout, QWidget,
)
from modelos.matrices import construir_matrices
from .modelo_matriz import ModeloMatriz


class PanelMatricesDijkstra(QWidget):
    def __init__(self, grafo, parent=None):
        super().__init__(parent)
        self.datos = construir_matrices(grafo)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.boton = QToolButton()
        self.boton.setCheckable(True)
        self.boton.setText('Matrices de adyacencia e incidencia')
        self.boton.setArrowType(Qt.ArrowType.UpArrow)
        self.boton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.boton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.boton.toggled.connect(self.desplegar)
        layout.addWidget(self.boton)
        self.contenido = QFrame()
        self.contenido.setMinimumHeight(0)
        self.contenido.setMaximumHeight(0)
        self.contenido.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        contenido = QVBoxLayout(self.contenido)
        contenido.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        contenido.setContentsMargins(0, 0, 0, 0)
        self.registro = QLabel('Registro matricial · sin búsqueda')
        contenido.addWidget(self.registro)
        divisor = QSplitter(Qt.Orientation.Horizontal)
        self.modelo_adyacencia = ModeloMatriz(self.datos, 'adyacencia', self)
        self.modelo_incidencia = ModeloMatriz(self.datos, 'incidencia', self)
        self.adyacencia = self.crear_tabla(divisor, 'Adyacencia · conexiones por par', self.modelo_adyacencia)
        self.incidencia = self.crear_tabla(divisor, 'Incidencia · una columna por arista', self.modelo_incidencia)
        divisor.setSizes([500, 500])
        contenido.addWidget(divisor, 1)
        ayuda = QLabel('Pesos y extremos: pasa el cursor. Oscuro: visitados · Verde: consultadas · Neón: cruz activa / ruta.')
        ayuda.setWordWrap(True)
        contenido.addWidget(ayuda)
        layout.addWidget(self.contenido)
        self.animacion = QPropertyAnimation(self.contenido, b'maximumHeight', self)
        self.animacion.setDuration(230)
        self.animacion.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def crear_tabla(self, divisor, titulo, modelo):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QLabel(titulo))
        tabla = QTableView()
        tabla.setModel(modelo)
        tabla.setMinimumSize(0, 0)
        tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabla.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tabla.horizontalHeader().setDefaultSectionSize(44)
        tabla.verticalHeader().setDefaultSectionSize(24)
        tabla.horizontalHeader().setMinimumSectionSize(35)
        layout.addWidget(tabla, 1)
        divisor.addWidget(panel)
        return tabla

    def desplegar(self, abierto):
        self.animacion.stop()
        self.animacion.setStartValue(self.contenido.maximumHeight())
        self.animacion.setEndValue(300 if abierto else 0)
        self.animacion.start()
        self.boton.setArrowType(Qt.ArrowType.DownArrow if abierto else Qt.ArrowType.UpArrow)

    def cargar(self, grafo):
        self.datos = construir_matrices(grafo)
        self.modelo_adyacencia.cargar(self.datos)
        self.modelo_incidencia.cargar(self.datos)
        self.registro.setText('Registro matricial · sin búsqueda')
        self.boton.setText('Matrices de adyacencia e incidencia')

    def representar(self, indice=-1, paso=None, resultado=None):
        # Reconstruye el registro hasta el paso mostrado, también al retroceder.
        consultadas = tuple(p.arista for p in resultado.pasos[:indice + 1] if p.arista) if resultado else ()
        self.modelo_adyacencia.representar(paso, consultadas)
        self.modelo_incidencia.representar(paso, consultadas)
        if paso:
            texto = f'Paso {indice + 1}/{len(resultado.pasos)} · {len(paso.visitados)} nodos visitados'
            self.registro.setText(texto)
            self.boton.setText(f'Matrices · {texto}')
            if paso.arista:
                for modelo, tabla in [(self.modelo_adyacencia, self.adyacencia),
                                       (self.modelo_incidencia, self.incidencia)]:
                    fila = modelo.filas[paso.arista.origen]
                    columna = (modelo.filas[paso.arista.destino] if modelo.tipo == 'adyacencia'
                               else modelo.columnas[(frozenset((paso.arista.origen, paso.arista.destino)), paso.arista.clave)])
                    tabla.scrollTo(modelo.index(fila, columna), QAbstractItemView.ScrollHint.EnsureVisible)
        else:
            self.registro.setText('Registro matricial · sin búsqueda')
            self.boton.setText('Matrices de adyacencia e incidencia')

    def animar(self, progreso):
        self.modelo_adyacencia.animar(progreso)
        self.modelo_incidencia.animar(progreso)
