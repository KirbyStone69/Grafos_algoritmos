"""Apartado Paso/Pregunta/Respuesta/Proceso inspirado en el documento."""
from PyQt6.QtWidgets import QFormLayout, QGroupBox, QLabel, QVBoxLayout
from .vectores import numero


class PanelRelajacion(QGroupBox):
    def __init__(self, parent=None):
        super().__init__('Paso · Relajación y verificación', parent)
        layout = QVBoxLayout(self)
        self.paso = QLabel('Paso 0.0 · Pendiente de inicializar')
        self.paso.setWordWrap(True)
        layout.addWidget(self.paso)
        formulario = QFormLayout()
        self.pregunta, self.respuesta, self.proceso = QLabel(), QLabel(), QLabel()
        for titulo, campo in [('Pregunta', self.pregunta), ('Respuesta', self.respuesta), ('Proceso', self.proceso)]:
            campo.setWordWrap(True)
            formulario.addRow(titulo, campo)
        layout.addLayout(formulario)
        self.limpiar()

    def limpiar(self):
        self.paso.setText('Paso 0.0 · Pendiente de inicializar')
        self.pregunta.setText('d[v] > d[u] + w(u,v) ?')
        self.respuesta.setText('—')
        self.proceso.setText('Pulsa Ejecutar para inicializar los vectores.')

    def mostrar(self, paso, resultado):
        self.paso.setText(f'Paso {paso.pasada}.{paso.indice_arco} · {paso.descripcion}')
        if paso.arista and paso.respuesta is not None:
            a = paso.arista
            signo = '≤' if paso.verificacion else '>'
            self.pregunta.setText(f'd[{a.destino}] {signo} d[{a.origen}] + w({a.origen},{a.destino}) ?\n'
                                  f'{numero(paso.distancia_anterior)} {signo} {numero(paso.distancia_origen)} + ({numero(a.peso)}) = {numero(paso.candidato)}')
            self.respuesta.setText('SÍ' if paso.respuesta else 'NO')
            if paso.verificacion:
                texto = 'La condición se cumple.' if paso.respuesta else 'La distancia aún puede disminuir: hay un ciclo negativo alcanzable.'
            elif paso.respuesta:
                texto = f'd[{a.destino}] ← {numero(paso.candidato)}\nΠ[{a.destino}] ← {a.origen}'
            else:
                texto = 'No se hace nada.'
            self.proceso.setText(texto)
        else:
            self.pregunta.setText('d[v] ≤ d[u] + w(u,v) en todos los arcos' if paso.verificacion else '—')
            self.respuesta.setText('DESTINO CON MÍNIMO FINITO' if paso.tipo == 'ciclo_negativo' and resultado.destino is not None and resultado.encontrado else 'NO EXISTE MÍNIMO FINITO' if paso.tipo == 'ciclo_negativo' else 'VERIFICACIÓN CORRECTA' if paso.tipo == 'fin' else 'DESTINO INALCANZABLE' if paso.tipo == 'sin_ruta' else '—')
            self.proceso.setText(paso.descripcion)
            if paso.tipo == 'ciclo_negativo':
                self.proceso.setText(paso.descripcion + '\nPeso del ciclo: ' + numero(sum(a.peso for a in resultado.aristas_ciclo)))
