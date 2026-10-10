"""Interfaz de Floyd–Warshall inspirada en las hojas XLSX/PDF del proyecto."""
from time import perf_counter
from math import inf
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView, QComboBox, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QProgressBar, QPushButton, QSlider,
    QSpinBox, QSplitter, QTableView, QVBoxLayout, QWidget,
)
from algoritmos.tipos import Paso
from modelos.grafos import obtener_adyacencia
from modelos.ejemplo_floyd import ARCHIVO_EJEMPLO, cargar_ejemplo_floyd
from ...base import InterfazAlgoritmo
from ...celebracion import ParpadeoRuta
from ...escena import EscenaGrafo, VistaGrafo
from .modelo import ModeloFloyd, numero
from .reproductor import ReproductorFloyd


class InterfazWarshallFloyd(InterfazAlgoritmo):
    def __init__(self, grafo, algoritmo, parent=None):
        super().__init__(parent)
        self.grafo_proyecto, self.grafo, self.algoritmo = grafo, grafo, algoritmo
        self.reproductor = ReproductorFloyd(self)
        self.celebracion = ParpadeoRuta(self)
        self.escena = EscenaGrafo(self)
        self.vista = VistaGrafo(self.escena)
        self.celebracion.fase_cambiada.connect(self.escena.parpadear_ruta)
        self.modelo_distancias = ModeloFloyd('distancias', self)
        self.modelo_recorridos = ModeloFloyd('recorridos', self)
        self.construir_interfaz()
        self.conectar()
        self.cargar_grafo(grafo)
        self.cambiar_modo()

    def construir_interfaz(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        centro = QVBoxLayout()
        titulo = QLabel('FLOYD–WARSHALL / DISTANCIAS Y RECORRIDOS')
        titulo.setObjectName('titulo')
        centro.addWidget(titulo)
        divisor = QSplitter(Qt.Orientation.Horizontal)
        self.distancias = self.crear_tabla(divisor, 'Matriz de distancias D', self.modelo_distancias)
        self.recorridos = self.crear_tabla(divisor, 'Matriz de recorridos R · vértice intermedio', self.modelo_recorridos)
        divisor.setSizes([600, 600])
        centro.addWidget(divisor, 2)
        self.comparacion = QLabel('D[i,j] ← min(D[i,j], D[i,k] + D[k,j])')
        self.comparacion.setWordWrap(True)
        centro.addWidget(self.comparacion)
        centro.addWidget(QLabel('Diagonal: 0 · ∞: sin conexión · −∞: ciclo negativo · Verde: fila/columna k · Neón: comparación'))
        centro.addWidget(self.vista, 1)
        layout.addLayout(centro, 1)
        lateral = QWidget()
        lateral.setFixedWidth(300)
        controles = QVBoxLayout(lateral)
        controles.setContentsMargins(0, 0, 0, 0)
        self.fuente = QComboBox()
        self.fuente.addItems(['Grafo del proyecto', 'Ejemplo XLSX · A–H'])
        if not ARCHIVO_EJEMPLO.exists():
            self.fuente.model().item(1).setEnabled(False)
        formulario = QFormLayout()
        formulario.addRow('Datos', self.fuente)
        self.origen, self.destino = QLineEdit('17'), QLineEdit('10')
        formulario.addRow('Origen de consulta', self.origen)
        formulario.addRow('Destino de consulta', self.destino)
        controles.addLayout(formulario)
        self.modo = QComboBox()
        self.modo.addItems(['Por intermedio k · rápido', 'Paso a paso · i,j,k', 'Debug · resultado directo'])
        controles.addWidget(self.modo)
        self.ejecutar = QPushButton('Calcular todos los pares')
        self.debug = QPushButton('Debug: resultado directo')
        controles.addWidget(self.ejecutar)
        controles.addWidget(self.debug)
        fila = QHBoxLayout()
        self.atras, self.play, self.adelante, self.reiniciar = (QPushButton(t) for t in ('←', 'Reproducir', '→', '↺'))
        for b in (self.atras, self.play, self.adelante, self.reiniciar):
            fila.addWidget(b)
        controles.addLayout(fila)
        self.siguiente_k = QPushButton('Intermedio siguiente')
        controles.addWidget(self.siguiente_k)
        controles.addWidget(QLabel('Velocidad'))
        self.velocidad = QSlider(Qt.Orientation.Horizontal)
        self.velocidad.setRange(1, 10)
        self.velocidad.setValue(7)
        controles.addWidget(self.velocidad)
        fila = QHBoxLayout()
        fila.addWidget(QLabel('Ir al evento'))
        self.evento = QSpinBox()
        self.evento.setKeyboardTracking(False)
        self.evento.setRange(1, 1)
        fila.addWidget(self.evento)
        controles.addLayout(fila)
        self.progreso = QProgressBar()
        controles.addWidget(self.progreso)
        self.estado, self.consulta = QLabel(), QLabel('Consulta pendiente')
        self.estado.setWordWrap(True)
        self.consulta.setWordWrap(True)
        controles.addWidget(self.estado)
        self.consultar = QPushButton('Consultar ruta en resultado final')
        controles.addWidget(self.consultar)
        controles.addWidget(self.consulta)
        self.final = QPushButton('Mostrar matrices finales')
        controles.addWidget(self.final)
        self.ajustar = QPushButton('Ajustar grafo')
        self.ajustar.clicked.connect(self.vista.ajustar)
        controles.addWidget(self.ajustar)
        nota = QLabel('Calcula todos los pares. La consulta no recalcula las matrices.\n'
                      'El ejemplo se carga desde la matriz inicial del XLSX; las iteraciones se calculan, no se copian.')
        nota.setWordWrap(True)
        controles.addWidget(nota)
        controles.addStretch()
        layout.addWidget(lateral)

    def crear_tabla(self, divisor, titulo, modelo):
        grupo = QGroupBox(titulo)
        layout = QVBoxLayout(grupo)
        tabla = QTableView()
        tabla.setModel(modelo)
        tabla.setMinimumWidth(0)
        tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabla.horizontalHeader().setDefaultSectionSize(62)
        tabla.verticalHeader().setDefaultSectionSize(27)
        layout.addWidget(tabla)
        divisor.addWidget(grupo)
        return tabla

    def conectar(self):
        self.fuente.currentIndexChanged.connect(self.cambiar_fuente)
        self.ejecutar.clicked.connect(self.buscar)
        self.debug.clicked.connect(lambda: self.buscar(debug=True))
        self.modo.currentIndexChanged.connect(self.cambiar_modo)
        self.velocidad.valueChanged.connect(self.cambiar_velocidad)
        self.play.clicked.connect(self.alternar)
        self.atras.clicked.connect(self.reproductor.anterior)
        self.adelante.clicked.connect(self.reproductor.siguiente)
        self.reiniciar.clicked.connect(self.reproductor.reiniciar)
        self.siguiente_k.clicked.connect(self.avanzar_k)
        self.final.clicked.connect(self.mostrar_final)
        self.consultar.clicked.connect(self.consultar_ruta)
        self.evento.editingFinished.connect(lambda: self.saltar(self.evento.value() - 1))
        self.distancias.clicked.connect(self.consultar_celda)
        self.recorridos.clicked.connect(self.consultar_celda)
        self.origen.textChanged.connect(self.limpiar_consulta)
        self.destino.textChanged.connect(self.limpiar_consulta)
        self.reproductor.paso_cambiado.connect(self.mostrar_paso)
        self.reproductor.reproduciendo.connect(lambda activo: self.play.setText('Resultado' if self.modo.currentIndex() == 2 else 'Pausar' if activo else 'Reproducir'))

    def controles(self, activo):
        for b in (self.atras, self.play, self.adelante, self.reiniciar, self.siguiente_k, self.final, self.consultar, self.evento):
            b.setEnabled(activo)

    def cargar_grafo(self, grafo):
        self.grafo_proyecto = grafo
        if self.fuente.currentIndex() == 0:
            self.grafo = grafo
            self.invalidar()
        else:
            self.detener()

    def cambiar_fuente(self, indice):
        try:
            self.grafo = cargar_ejemplo_floyd() if indice else self.grafo_proyecto
        except ValueError as error:
            QMessageBox.warning(self, 'Ejemplo no disponible', str(error))
            self.fuente.setCurrentIndex(0)
            return
        self.origen.setText('A' if indice else '17')
        self.destino.setText('H' if indice else '10')
        self.invalidar()

    def invalidar(self):
        self.detener()
        self.reproductor.limpiar()
        self.modelo_distancias.cargar(self.grafo.nodes)
        self.modelo_recorridos.cargar(self.grafo.nodes)
        self.escena.cargar(self.grafo)
        self.vista.ajustar()
        self.controles(False)
        self.evento.setRange(1, 1)
        self.progreso.setRange(0, 1)
        self.progreso.setValue(0)
        self.estado.setText('Listo para calcular todos los pares.')
        self.consulta.setText('Consulta pendiente')

    def buscar(self, debug=False):
        self.detener()
        if debug:
            self.modo.setCurrentIndex(2)
        inicio = perf_counter()
        try:
            resultado = self.algoritmo.ejecutar(obtener_adyacencia(self.grafo))
        except ValueError as error:
            self.invalidar()
            QMessageBox.warning(self, 'Datos no válidos', str(error))
            return
        self.tiempo_ms = (perf_counter() - inicio) * 1000
        self.controles(True)
        self.evento.setRange(1, len(resultado.pasos))
        self.progreso.setRange(0, len(resultado.pasos))
        self.reproductor.cargar(resultado)
        if self.modo.currentIndex() == 2:
            self.mostrar_final()
        else:
            self.reproductor.iniciar()

    def mostrar_paso(self, indice, paso):
        self.celebracion.detener()
        resultado = self.reproductor.resultado
        self.modelo_distancias.mostrar(paso)
        self.modelo_recorridos.mostrar(paso)
        self.evento.setValue(indice + 1)
        self.progreso.setValue(indice + 1)
        k = resultado.nodos[paso.k] if paso.k is not None else '—'
        self.estado.setText(f'Evento {indice + 1}/{len(resultado.pasos)} · k = {k}\n'
                            f'{paso.comparaciones} comparaciones · {paso.cambios} cambios · cálculo {self.tiempo_ms:.0f} ms')
        if paso.i is not None:
            i, j = resultado.nodos[paso.i], resultado.nodos[paso.j]
            self.comparacion.setText(f'D[{i},{j}] = {numero(paso.anterior)} > '
                                    f'D[{i},{k}] + D[{k},{j}] = {numero(paso.izquierdo)} + {numero(paso.derecho)} = {numero(paso.candidato)} ? '
                                    + ('SÍ · actualizar D y R.' if paso.mejora else 'NO · conservar.'))
            for modelo, tabla in [(self.modelo_distancias, self.distancias), (self.modelo_recorridos, self.recorridos)]:
                tabla.scrollTo(modelo.index(paso.i, paso.j))
        elif paso.tipo == 'fin':
            self.comparacion.setText(f'Final: {len(resultado.afectados)} pares sin mínimo finito por ciclos negativos.'
                                    if resultado.ciclos else 'Matrices finales: todos los caminos mínimos calculados.')
        else:
            self.comparacion.setText(f'Iteración {paso.iteracion}: permitir el intermedio k = {k}.')
        actual = resultado.nodos[paso.k] if paso.k is not None else None
        visitados = frozenset(resultado.nodos[:paso.iteracion])
        self.escena.representar(Paso('intermedio', '', actual, None, {}, {}, visitados))
        self.atras.setEnabled(indice > 0)
        self.adelante.setEnabled(indice + 1 < len(resultado.pasos))

    def limpiar_consulta(self, *_):
        self.celebracion.detener()
        self.consulta.setText('Consulta pendiente')
        if self.reproductor.resultado:
            p = self.reproductor.resultado.pasos[self.reproductor.indice]
            self.mostrar_paso(self.reproductor.indice, p)

    def consultar_ruta(self):
        resultado = self.reproductor.resultado
        if not resultado:
            return
        disponibles = {str(n): n for n in resultado.nodos}
        origen = disponibles.get(self.origen.text().strip())
        destino = disponibles.get(self.destino.text().strip())
        if origen is None or destino is None:
            texto = ('Nodo origen y destino no existen.' if origen is None and destino is None else
                     'Nodo origen no existe.' if origen is None else 'Nodo destino no existe.')
            QMessageBox.warning(self, 'Nodos no válidos', texto)
            return
        self.mostrar_final()
        try:
            costo, ruta, aristas = resultado.consultar(origen, destino)
        except ValueError as error:
            self.consulta.setText(str(error))
            return
        if costo == inf:
            self.consulta.setText('No existe camino para este par.')
            return
        self.consulta.setText(f'Costo: {numero(costo)}\n' + ' → '.join(map(str, ruta)))
        self.escena.representar(Paso('fin', '', destino, None, {}, {}, frozenset(ruta), ruta, aristas))
        self.celebracion.iniciar()

    def consultar_celda(self, index):
        if self.reproductor.resultado:
            nodos = self.reproductor.resultado.nodos
            self.origen.setText(str(nodos[index.row()]))
            self.destino.setText(str(nodos[index.column()]))
            self.consultar_ruta()

    def saltar(self, indice):
        self.reproductor.pausar()
        self.reproductor.mostrar(indice)

    def mostrar_final(self):
        if self.reproductor.resultado:
            self.saltar(len(self.reproductor.resultado.pasos) - 1)

    def avanzar_k(self):
        if self.reproductor.resultado:
            siguiente = next((i for i in self.reproductor.resultado.finales_iteracion if i > self.reproductor.indice), len(self.reproductor.resultado.pasos) - 1)
            self.saltar(siguiente)

    def alternar(self):
        if self.modo.currentIndex() == 2:
            self.mostrar_final()
        elif self.reproductor.timer.isActive():
            self.reproductor.pausar()
        else:
            self.reproductor.iniciar()

    def cambiar_modo(self, *_):
        self.reproductor.pausar()
        self.reproductor.por_intermedio = self.modo.currentIndex() == 0
        self.cambiar_velocidad(self.velocidad.value())
        if self.modo.currentIndex() == 2 and self.reproductor.resultado:
            self.mostrar_final()

    def cambiar_velocidad(self, valor):
        self.reproductor.duracion = 40 + (10 - valor) * 80
        self.reproductor.timer.setInterval(60 + (10 - valor) * 30 if self.reproductor.por_intermedio else 30)

    def detener(self):
        self.reproductor.pausar()
        self.celebracion.detener()
