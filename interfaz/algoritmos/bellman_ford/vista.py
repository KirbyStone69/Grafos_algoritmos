"""Interfaz de Bellman–Ford basada en los cuatro apartados del PDF de referencia."""
from time import perf_counter
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QProgressBar, QPushButton, QSpinBox,
    QSlider, QSplitter, QVBoxLayout, QWidget,
)
from modelos.grafos import obtener_adyacencia, tiene_negativos
from ...base import InterfazAlgoritmo
from ...escena import VistaGrafo
from .reproductor import ReproductorBellmanFord
from .arcos import ListaArcos
from .configuracion import ConfiguracionBellmanFord
from .escena import EscenaBellmanFord
from .relajacion import PanelRelajacion
from .vectores import TablaVectores


class InterfazBellmanFord(InterfazAlgoritmo):
    def __init__(self, grafo, algoritmo, parent=None):
        super().__init__(parent)
        self.grafo, self.algoritmo = grafo, algoritmo
        self.reproductor = ReproductorBellmanFord(self)
        self.tiempo_calculo_ms = 0
        self.escena = EscenaBellmanFord(self)
        self.vista = VistaGrafo(self.escena)
        self.configuracion = ConfiguracionBellmanFord()
        self.lista_arcos = ListaArcos()
        self.vectores = TablaVectores(grafo.nodes)
        self.relajacion = PanelRelajacion()
        self.construir_interfaz()
        self.conectar()
        self.cargar_grafo(grafo)
        self.cambiar_velocidad(self.velocidad.value())
        QTimer.singleShot(0, self.vista.ajustar)

    def construir_interfaz(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        barra = QHBoxLayout()
        titulo = QLabel('BELLMAN–FORD / RELAX')
        titulo.setObjectName('titulo')
        barra.addWidget(titulo)
        barra.addStretch()
        for texto, accion in [('Ajustar', self.vista.ajustar), ('＋', lambda: self.vista.zoom(1.2)),
                               ('−', lambda: self.vista.zoom(1 / 1.2))]:
            boton = QPushButton(texto)
            boton.clicked.connect(accion)
            barra.addWidget(boton)
        self.pesos = QCheckBox('Pesos')
        self.pesos.setChecked(True)
        barra.addWidget(self.pesos)
        layout.addLayout(barra)
        cuerpo = QHBoxLayout()
        izquierda = QVBoxLayout()
        izquierda.addWidget(self.vista, 1)
        inferior = QSplitter(Qt.Orientation.Horizontal)
        grupo = QGroupBox('Vectores V · d · Π')
        vectores = QVBoxLayout(grupo)
        vectores.addWidget(self.vectores)
        nota = QLabel('d: distancia · Π: predecesor · −∞: sin mínimo finito. Distancias provisionales hasta verificar.')
        nota.setWordWrap(True)
        vectores.addWidget(nota)
        inferior.addWidget(grupo)
        inferior.addWidget(self.relajacion)
        inferior.setSizes([450, 550])
        inferior.setMinimumHeight(205)
        inferior.setMaximumHeight(240)
        izquierda.addWidget(inferior)
        cuerpo.addLayout(izquierda, 1)
        lateral = QWidget()
        lateral.setFixedWidth(310)
        controles = QVBoxLayout(lateral)
        controles.setContentsMargins(0, 0, 0, 0)
        controles.addWidget(self.configuracion)
        self.compatibilidad = QLabel()
        self.compatibilidad.setWordWrap(True)
        controles.addWidget(self.compatibilidad)
        self.modo = QComboBox()
        self.modo.addItems(['Paso a paso', 'Rápido · por bloques', 'Debug · resultado directo'])
        self.modo.setCurrentIndex(1)
        controles.addWidget(QLabel('Modo de ejecución'))
        controles.addWidget(self.modo)
        self.ejecutar = QPushButton('Ejecutar rápido')
        controles.addWidget(self.ejecutar)
        self.debug = QPushButton('Debug: verificar ahora')
        self.debug.setToolTip('Calcula toda la búsqueda y muestra directamente el resultado. Conserva los pasos para inspección.')
        controles.addWidget(self.debug)
        navegacion = QHBoxLayout()
        self.atras, self.play, self.adelante, self.reiniciar = (QPushButton(t) for t in ('←', 'Reproducir', '→', '↺'))
        for boton, ayuda in [(self.atras, 'Paso anterior'), (self.play, 'Reproducir / pausar'),
                              (self.adelante, 'Paso siguiente'), (self.reiniciar, 'Reiniciar')]:
            boton.setToolTip(ayuda)
            navegacion.addWidget(boton)
        controles.addLayout(navegacion)
        saltos = QHBoxLayout()
        self.pasada, self.verificar = QPushButton('Siguiente pasada'), QPushButton('Verificar')
        saltos.addWidget(self.pasada)
        saltos.addWidget(self.verificar)
        controles.addLayout(saltos)
        controles.addWidget(QLabel('Velocidad'))
        self.velocidad = QSlider(Qt.Orientation.Horizontal)
        self.velocidad.setRange(1, 10)
        self.velocidad.setValue(7)
        controles.addWidget(self.velocidad)
        self.rendimiento = QLabel()
        self.rendimiento.setWordWrap(True)
        controles.addWidget(self.rendimiento)
        self.progreso_busqueda = QProgressBar()
        self.progreso_busqueda.setRange(0, 1)
        self.progreso_busqueda.setValue(0)
        self.progreso_busqueda.setFormat('%v / %m eventos')
        controles.addWidget(self.progreso_busqueda)
        fila_evento = QHBoxLayout()
        fila_evento.addWidget(QLabel('Ir al evento'))
        self.evento = QSpinBox()
        self.evento.setRange(1, 1)
        self.evento.setKeyboardTracking(False)
        fila_evento.addWidget(self.evento)
        controles.addLayout(fila_evento)
        self.estado = QLabel()
        self.estado.setWordWrap(True)
        controles.addWidget(self.estado)
        self.final = QPushButton('Mostrar resultado')
        controles.addWidget(self.final)
        controles.addWidget(QLabel('Lista de arcos · referencia'))
        controles.addWidget(self.lista_arcos, 1)
        cuerpo.addWidget(lateral)
        layout.addLayout(cuerpo, 1)

    def conectar(self):
        self.configuracion.cambiada.connect(self.invalidar)
        self.ejecutar.clicked.connect(self.buscar)
        self.debug.clicked.connect(lambda: self.buscar(debug=True))
        self.modo.currentIndexChanged.connect(self.cambiar_modo)
        self.evento.editingFinished.connect(self.ir_evento)
        self.atras.clicked.connect(self.reproductor.anterior)
        self.adelante.clicked.connect(self.reproductor.siguiente)
        self.reiniciar.clicked.connect(self.reproductor.reiniciar)
        self.play.clicked.connect(self.alternar)
        self.pasada.clicked.connect(self.siguiente_pasada)
        self.verificar.clicked.connect(self.ir_verificacion)
        self.final.clicked.connect(self.mostrar_resultado)
        self.velocidad.valueChanged.connect(self.cambiar_velocidad)
        self.lista_arcos.itemClicked.connect(self.ir_arco)
        self.pesos.toggled.connect(self.escena.mostrar_pesos)
        self.reproductor.paso_cambiado.connect(self.mostrar_paso)
        self.reproductor.progreso.connect(self.escena.animar)
        self.reproductor.reproduciendo.connect(lambda activo: self.play.setText('Resultado' if self.modo.currentIndex() == 2 else 'Pausar' if activo else 'Reproducir'))

    def controles(self, activo):
        for boton in (self.atras, self.play, self.adelante, self.reiniciar, self.pasada, self.verificar, self.final):
            boton.setEnabled(activo)
        self.evento.setEnabled(activo)

    def actualizar_compatibilidad(self):
        compatible = tiene_negativos(self.grafo)
        self.ejecutar.setEnabled(compatible)
        self.debug.setEnabled(compatible)
        self.compatibilidad.setText('Grafo original: se evalúan ambos sentidos y se comprueban ciclos negativos.' if compatible else
                                    'Esta interfaz usa solo el grafo con negativos. Selecciona «Original».')

    def invalidar(self):
        self.reproductor.limpiar()
        self.escena.representar()
        self.vectores.cargar(self.grafo.nodes)
        self.relajacion.limpiar()
        self.lista_arcos.setCurrentRow(-1)
        self.controles(False)
        self.progreso_busqueda.setRange(0, 1)
        self.progreso_busqueda.setValue(0)
        self.evento.setRange(1, 1)
        self.tiempo_calculo_ms = 0
        self.actualizar_rendimiento()
        self.estado.setText('Listo: un origen a todos los nodos.')
        self.actualizar_compatibilidad()

    def cargar_grafo(self, grafo):
        self.reproductor.limpiar()
        self.grafo = grafo
        self.escena.cargar(grafo)
        self.lista_arcos.cargar(obtener_adyacencia(grafo))
        self.invalidar()
        self.vista.ajustar()

    def buscar(self, debug=False):
        if not tiene_negativos(self.grafo):
            self.actualizar_compatibilidad()
            return
        if debug:
            self.modo.setCurrentIndex(2)
        self.reproductor.limpiar()
        try:
            parametros = self.configuracion.parametros(self.grafo)
            inicio = perf_counter()
            resultado = self.algoritmo.ejecutar(obtener_adyacencia(self.grafo), **parametros)
        except ValueError as error:
            self.invalidar()
            QMessageBox.warning(self, 'Nodos o datos no válidos', str(error))
            return
        self.tiempo_calculo_ms = (perf_counter() - inicio) * 1000
        self.progreso_busqueda.setRange(0, len(resultado.pasos))
        self.evento.setRange(1, len(resultado.pasos))
        self.controles(True)
        self.reproductor.cargar(resultado)
        self.actualizar_rendimiento()
        if debug or self.modo.currentIndex() == 2:
            self.mostrar_resultado()
        else:
            self.reproductor.iniciar()

    def mostrar_paso(self, indice, paso):
        resultado = self.reproductor.resultado
        self.escena.representar(paso)
        self.lista_arcos.mostrar(paso)
        self.vectores.mostrar(paso)
        self.relajacion.mostrar(paso, resultado)
        self.progreso_busqueda.setValue(indice + 1)
        self.evento.setValue(indice + 1)
        self.estado.setText(f'Evento {indice + 1}/{len(resultado.pasos)} · Paso {paso.pasada}.{paso.indice_arco}')
        self.atras.setEnabled(indice > 0)
        self.adelante.setEnabled(indice + 1 < len(resultado.pasos))
        if paso.tipo == 'ciclo_negativo':
            self.escena.mostrar_ciclo(resultado)

    def alternar(self):
        if self.modo.currentIndex() == 2:
            self.mostrar_resultado()
        else:
            self.reproductor.pausar() if self.reproductor.timer.isActive() else self.reproductor.iniciar()

    def saltar(self, indice):
        self.reproductor.pausar()
        self.reproductor.mostrar(indice)

    def siguiente_pasada(self):
        if self.reproductor.resultado:
            pasos = self.reproductor.resultado.pasos
            indice = next((i for i in range(self.reproductor.indice + 1, len(pasos))
                           if pasos[i].tipo in {'pasada', 'verificacion'}), len(pasos) - 1)
            self.saltar(indice)

    def ir_verificacion(self):
        if self.reproductor.resultado:
            self.saltar(next(i for i, p in enumerate(self.reproductor.resultado.pasos) if p.tipo == 'verificacion'))

    def mostrar_resultado(self):
        if self.reproductor.resultado:
            self.saltar(len(self.reproductor.resultado.pasos) - 1)

    def ir_arco(self, item):
        if not self.reproductor.resultado:
            return
        numero = item.data(Qt.ItemDataRole.UserRole)
        pasos = self.reproductor.resultado.pasos
        actual = pasos[self.reproductor.indice]
        indice = next((i for i, p in enumerate(pasos) if p.indice_arco == numero
                       and p.pasada == actual.pasada and p.arista), None)
        if indice is not None:
            self.saltar(indice)

    def ir_evento(self):
        if self.reproductor.resultado:
            self.saltar(self.evento.value() - 1)

    def cambiar_modo(self, *_):
        self.reproductor.pausar()
        self.cambiar_velocidad(self.velocidad.value())
        self.ejecutar.setText(['Ejecutar paso a paso', 'Ejecutar rápido', 'Verificar (debug)'][self.modo.currentIndex()])
        if self.modo.currentIndex() == 2 and self.reproductor.resultado:
            self.mostrar_resultado()

    def cambiar_velocidad(self, valor):
        rapido = self.modo.currentIndex() == 1
        self.reproductor.bloque = 16 + 8 * (valor - 1) if rapido else 1
        self.reproductor.timer.setInterval(40 if rapido else 30)
        self.reproductor.duracion = 40 + (10 - valor) * 120
        self.actualizar_rendimiento()

    def actualizar_rendimiento(self):
        modo = self.modo.currentIndex()
        if modo == 1:
            texto = f'{self.reproductor.bloque} eventos por fotograma. Traza completa; animación resumida.'
        elif modo == 2:
            texto = 'Resultado directo; usa los controles para inspeccionar cualquier evento.'
        else:
            texto = f'{self.reproductor.duracion} ms por evento.'
        if self.tiempo_calculo_ms:
            texto += f' Cálculo: {self.tiempo_calculo_ms:.0f} ms.'
        self.rendimiento.setText(texto)

    def detener(self):
        self.reproductor.pausar()
