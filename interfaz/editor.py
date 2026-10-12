"""Panel de edicion del grafo: agregar/eliminar nodos y aristas, editar pesos.

Trabaja directamente sobre el grafo NetworkX activo (MultiGraph o MultiDiGraph).
Emite la senal grafo_modificado cuando hay cambios para que la ventana recargue
todas las interfaces de algoritmos.
"""
import networkx as nx
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QSpinBox, QVBoxLayout, QWidget,
)


class EditorGrafo(QWidget):
    """Barra lateral de edicion: se muestra como panel a la derecha del grafo."""
    grafo_modificado = pyqtSignal(object)  # emite el grafo actualizado

    def __init__(self, grafo, parent=None):
        super().__init__(parent)
        self.grafo = grafo
        self._construir()

    # ------------------------------------------------------------------
    def _construir(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        titulo = QLabel('Editor de grafo')
        titulo.setObjectName('titulo')
        layout.addWidget(titulo)

        # --- Agregar nodo ---
        layout.addWidget(QLabel('Agregar nodo'))
        form_nodo = QFormLayout()
        self.campo_nodo = QLineEdit()
        self.campo_nodo.setPlaceholderText('ID del nodo (ej: 21)')
        fila_coords = QHBoxLayout()
        self.campo_nodo_x = QLineEdit()
        self.campo_nodo_x.setPlaceholderText('X (opcional)')
        self.campo_nodo_y = QLineEdit()
        self.campo_nodo_y.setPlaceholderText('Y (opcional)')
        fila_coords.addWidget(self.campo_nodo_x)
        fila_coords.addWidget(self.campo_nodo_y)
        form_nodo.addRow('ID', self.campo_nodo)
        form_nodo.addRow('Posición', fila_coords)
        layout.addLayout(form_nodo)
        btn_add_nodo = QPushButton('+Nodo')
        btn_add_nodo.setToolTip('Agrega un nodo con el ID y posición indicados')
        btn_add_nodo.clicked.connect(self.agregar_nodo)
        layout.addWidget(btn_add_nodo)

        # --- Eliminar nodo ---
        fila_del_nodo = QHBoxLayout()
        self.campo_del_nodo = QLineEdit()
        self.campo_del_nodo.setPlaceholderText('ID del nodo')
        self.campo_del_nodo.setMaximumWidth(120)
        btn_del_nodo = QPushButton('-Nodo')
        btn_del_nodo.setToolTip('Elimina el nodo y todas sus aristas')
        btn_del_nodo.clicked.connect(self.eliminar_nodo)
        fila_del_nodo.addWidget(self.campo_del_nodo)
        fila_del_nodo.addWidget(btn_del_nodo)
        layout.addLayout(fila_del_nodo)

        layout.addSpacing(8)

        # --- Agregar arista ---
        layout.addWidget(QLabel('Agregar arista'))
        form_arista = QFormLayout()
        self.campo_origen_a = QLineEdit()
        self.campo_origen_a.setPlaceholderText('Origen')
        self.campo_destino_a = QLineEdit()
        self.campo_destino_a.setPlaceholderText('Destino')
        self.campo_peso_a = QLineEdit('1')
        self.campo_peso_a.setPlaceholderText('Peso')
        form_arista.addRow('Origen', self.campo_origen_a)
        form_arista.addRow('Destino', self.campo_destino_a)
        form_arista.addRow('Peso', self.campo_peso_a)
        layout.addLayout(form_arista)
        btn_add_arista = QPushButton('+Arista')
        btn_add_arista.clicked.connect(self.agregar_arista)
        layout.addWidget(btn_add_arista)

        layout.addSpacing(8)

        # --- Editar peso ---
        layout.addWidget(QLabel('Editar peso de arista'))
        form_peso = QFormLayout()
        self.campo_origen_p = QLineEdit()
        self.campo_origen_p.setPlaceholderText('Origen')
        self.campo_destino_p = QLineEdit()
        self.campo_destino_p.setPlaceholderText('Destino')
        self.campo_clave_p = QLineEdit('0')
        self.campo_clave_p.setPlaceholderText('Clave (0 si no hay paralelas)')
        self.campo_nuevo_peso = QLineEdit()
        self.campo_nuevo_peso.setPlaceholderText('Nuevo peso')
        form_peso.addRow('Origen', self.campo_origen_p)
        form_peso.addRow('Destino', self.campo_destino_p)
        form_peso.addRow('Clave', self.campo_clave_p)
        form_peso.addRow('Nuevo peso', self.campo_nuevo_peso)
        layout.addLayout(form_peso)
        btn_editar_peso = QPushButton('Actualizar peso')
        btn_editar_peso.clicked.connect(self.editar_peso)
        layout.addWidget(btn_editar_peso)

        layout.addSpacing(8)

        # --- Eliminar arista ---
        layout.addWidget(QLabel('Eliminar arista'))
        form_del_arista = QFormLayout()
        self.campo_origen_d = QLineEdit()
        self.campo_origen_d.setPlaceholderText('Origen')
        self.campo_destino_d = QLineEdit()
        self.campo_destino_d.setPlaceholderText('Destino')
        self.campo_clave_d = QLineEdit('0')
        self.campo_clave_d.setPlaceholderText('Clave (0 si no hay paralelas)')
        form_del_arista.addRow('Origen', self.campo_origen_d)
        form_del_arista.addRow('Destino', self.campo_destino_d)
        form_del_arista.addRow('Clave', self.campo_clave_d)
        layout.addLayout(form_del_arista)
        btn_del_arista = QPushButton('-Arista')
        btn_del_arista.clicked.connect(self.eliminar_arista)
        layout.addWidget(btn_del_arista)

        layout.addSpacing(8)

        # --- Info ---
        self.info = QLabel()
        self.info.setObjectName('estado')
        self.info.setWordWrap(True)
        layout.addWidget(self.info)

        layout.addStretch()

    # ------------------------------------------------------------------
    def cargar_grafo(self, grafo):
        self.grafo = grafo
        self._actualizar_info('Grafo cargado.')

    def _actualizar_info(self, msg=''):
        n = self.grafo.number_of_nodes()
        e = self.grafo.number_of_edges()
        self.info.setText(f'{msg}\n{n} nodos · {e} aristas')

    def _parse_nodo(self, texto):
        texto = texto.strip()
        if not texto:
            raise ValueError('El ID del nodo no puede estar vacio.')
        try:
            return int(texto)
        except ValueError:
            return texto  # nodos de texto tambien son validos

    def _parse_peso(self, texto):
        texto = texto.strip()
        try:
            return float(texto)
        except ValueError:
            raise ValueError(f'Peso no valido: "{texto}". Ingresa un numero.')

    def _parse_clave(self, texto):
        texto = texto.strip()
        try:
            return int(texto)
        except ValueError:
            return texto

    def _aviso(self, msg):
        QMessageBox.warning(self, 'Editor', msg)

    # ------------------------------------------------------------------
    def agregar_nodo(self):
        try:
            nodo = self._parse_nodo(self.campo_nodo.text())
        except ValueError as e:
            self._aviso(str(e))
            return
        if nodo in self.grafo.nodes:
            self._aviso(f'El nodo {nodo} ya existe.')
            return
        # Posicion: usar las ingresadas o auto-calcular una libre
        try:
            texto_x = self.campo_nodo_x.text().strip()
            texto_y = self.campo_nodo_y.text().strip()
            if texto_x and texto_y:
                cx, cy = int(float(texto_x)), int(float(texto_y))
            else:
                xs = [d.get('pixel', (0, 0))[0] for _, d in self.grafo.nodes(data=True)]
                ys = [d.get('pixel', (0, 0))[1] for _, d in self.grafo.nodes(data=True)]
                cx = int(sum(xs) / len(xs)) + (len(self.grafo.nodes) * 20 % 200) if xs else 100
                cy = int(sum(ys) / len(ys)) + (len(self.grafo.nodes) * 25 % 200) if ys else 100
        except ValueError:
            self._aviso('Las coordenadas X y Y deben ser números.')
            return
        self.grafo.add_node(nodo, valor=nodo, pos=(cx, -cy), pixel=(cx, cy))
        self.campo_nodo.clear()
        self.campo_nodo_x.clear()
        self.campo_nodo_y.clear()
        self._actualizar_info(f'Nodo {nodo} agregado en ({cx}, {cy}).')
        self.grafo_modificado.emit(self.grafo)

    def eliminar_nodo(self):
        try:
            nodo = self._parse_nodo(self.campo_del_nodo.text())
        except ValueError as e:
            self._aviso(str(e))
            return
        if nodo not in self.grafo.nodes:
            self._aviso(f'El nodo {nodo} no existe.')
            return
        self.grafo.remove_node(nodo)
        self.campo_del_nodo.clear()
        self._actualizar_info(f'Nodo {nodo} eliminado.')
        self.grafo_modificado.emit(self.grafo)

    def agregar_arista(self):
        try:
            u = self._parse_nodo(self.campo_origen_a.text())
            v = self._parse_nodo(self.campo_destino_a.text())
            w = self._parse_peso(self.campo_peso_a.text())
        except ValueError as e:
            self._aviso(str(e))
            return
        for nodo in (u, v):
            if nodo not in self.grafo.nodes:
                self._aviso(f'El nodo {nodo} no existe. Agregalo primero.')
                return
        self.grafo.add_edge(u, v, weight=w, valor=w)
        self.campo_origen_a.clear()
        self.campo_destino_a.clear()
        self.campo_peso_a.setText('1')
        self._actualizar_info(f'Arista {u}↔{v} (w={w}) agregada.')
        self.grafo_modificado.emit(self.grafo)

    def eliminar_arista(self):
        try:
            u = self._parse_nodo(self.campo_origen_d.text())
            v = self._parse_nodo(self.campo_destino_d.text())
            clave = self._parse_clave(self.campo_clave_d.text())
        except ValueError as e:
            self._aviso(str(e))
            return
        if not self.grafo.has_edge(u, v, clave):
            # Intentar sin clave (primera arista entre u y v)
            if self.grafo.has_edge(u, v):
                claves = list(self.grafo[u][v].keys())
                clave = claves[0]
            else:
                self._aviso(f'No existe arista entre {u} y {v} con clave {clave}.')
                return
        self.grafo.remove_edge(u, v, clave)
        self._actualizar_info(f'Arista {u}↔{v} (clave={clave}) eliminada.')
        self.grafo_modificado.emit(self.grafo)

    def editar_peso(self):
        try:
            u = self._parse_nodo(self.campo_origen_p.text())
            v = self._parse_nodo(self.campo_destino_p.text())
            clave = self._parse_clave(self.campo_clave_p.text())
            nuevo_peso = self._parse_peso(self.campo_nuevo_peso.text())
        except ValueError as e:
            self._aviso(str(e))
            return
        if not self.grafo.has_edge(u, v, clave):
            if self.grafo.has_edge(u, v):
                claves = list(self.grafo[u][v].keys())
                clave = claves[0]
            else:
                self._aviso(f'No existe arista entre {u} y {v}.')
                return
        self.grafo[u][v][clave]['weight'] = nuevo_peso
        self.grafo[u][v][clave]['valor'] = nuevo_peso
        self._actualizar_info(f'Arista {u}↔{v} (clave={clave}) -> peso={nuevo_peso}.')
        self.grafo_modificado.emit(self.grafo)
