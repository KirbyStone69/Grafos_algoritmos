"""Integración de Qt sin pantalla: reproducción, aristas y controles reales."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PyQt6.QtGui import QImage
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QPushButton, QLineEdit
from interfaz.tema import ESTILO, FONDO, LINEA, NEON, NODO, VISITADO
from interfaz.ventana import VentanaGrafo


class InterfazTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle('Fusion')
        cls.app.setStyleSheet(ESTILO)

    def setUp(self):
        self.ventana = VentanaGrafo()
        self.ventana.show()
        self.app.processEvents()

    def tearDown(self):
        self.ventana.close()
        self.ventana.deleteLater()
        self.app.processEvents()

    def test_solo_lectura_colores_y_posiciones(self):
        w = self.ventana
        self.assertEqual(len(w.escena.nodos), 30)
        self.assertEqual(len(w.escena.aristas), 64)
        for nodo, item in w.escena.nodos.items():
            self.assertEqual((item.pos().x(), item.pos().y()), w.grafo.nodes[nodo]['pixel'])
            self.assertEqual(item.brush().color().name(), NODO)
        for arista in w.escena.aristas.values():
            self.assertEqual(arista.item.pen().color().name(), LINEA)
        botones = [b.text() for b in w.findChildren(QPushButton)]
        self.assertFalse(any('Editar' in b or 'Eliminar' in b or 'Añadir' in b for b in botones))
        self.assertFalse(hasattr(w, 'fotografia'))
        self.assertFalse(hasattr(w, 'detalles'))
        self.assertEqual(w.panel.origen.text(), '17')
        self.assertIsInstance(w.panel.origen, QLineEdit)
        self.assertFalse(hasattr(w.panel, 'historial'))
        self.assertFalse(hasattr(w.panel, 'tabla'))
        self.assertEqual(w.panel.destino.text(), '10')

    def test_todos_los_pasos_y_ruta_final(self):
        w = self.ventana
        w.panel.buscar.click()
        w.reproductor.pausar()
        resultado = w.reproductor.resultado
        self.assertEqual(resultado.distancia, 13)
        for indice, paso in enumerate(resultado.pasos):
            w.reproductor.mostrar(indice)
            self.assertEqual(w.escena.paso, paso)
            self.assertEqual(w.matrices.modelo_adyacencia.actual, paso.actual)
            self.assertEqual(w.matrices.modelo_incidencia.visitados, paso.visitados)
            if paso.arista:
                w.escena.animar(0.5)
                self.assertTrue(w.escena.particula.isVisible())
        self.assertIn('17 → 2 → 1 → 10', w.panel.resultado.text())
        self.assertIn('13', w.panel.resultado.text())
        for arista in resultado.aristas_ruta:
            identificador = w.escena.identificador(arista.origen, arista.destino, arista.clave)
            self.assertEqual(w.escena.aristas[identificador].item.pen().color().name(), NEON)
        self.assertFalse(w.panel.adelante.isEnabled())
        w.panel.atras.click()
        self.assertEqual(w.reproductor.indice, len(resultado.pasos) - 2)
        w.panel.reiniciar.click()
        self.assertEqual(w.reproductor.indice, 0)
        self.assertEqual(w.panel.resultado.text(), 'Costo final: —')

    def test_animacion_pausa_velocidad_y_cancelacion(self):
        w = self.ventana
        w.buscar()
        w.reproductor.duracion = 45
        QTest.qWait(180)
        self.assertGreater(w.reproductor.indice, 0)
        w.panel.play.click()
        self.assertFalse(w.reproductor.timer.isActive())
        indice = w.reproductor.indice
        QTest.qWait(80)
        self.assertEqual(w.reproductor.indice, indice)
        w.panel.play.click()
        self.assertTrue(w.reproductor.timer.isActive())
        w.panel.velocidad.setValue(10)
        self.assertEqual(w.reproductor.duracion, 150)
        w.panel.destino.setText('16')
        self.assertFalse(w.reproductor.timer.isActive())
        self.assertIsNone(w.reproductor.resultado)
        self.assertFalse(w.panel.play.isEnabled())

    def test_grafo_negativo_bloqueado_y_pesos_ocultos(self):
        w = self.ventana
        w.buscar()
        w.pesos.setChecked(False)
        w.selector_grafo.setCurrentIndex(0)
        self.assertFalse(w.panel.buscar.isEnabled())
        self.assertFalse(w.reproductor.timer.isActive())
        self.assertIsNone(w.reproductor.resultado)
        w.buscar()
        self.assertIsNone(w.reproductor.resultado)
        self.assertTrue(all(not a.etiqueta.isVisible() for a in w.escena.aristas.values()))
        self.assertEqual(w.grafo[66][13][0]['weight'], -777)
        w.selector_grafo.setCurrentIndex(1)
        self.assertTrue(w.panel.buscar.isEnabled())
        self.assertEqual(w.grafo[66][13][0]['weight'], 777)

    def test_aristas_paralelas_y_animacion_en_sentido_correcto(self):
        w = self.ventana
        w.panel.origen.setText('12')
        w.panel.destino.setText('16')
        w.buscar()
        w.reproductor.pausar()
        resultado = w.reproductor.resultado
        self.assertEqual(resultado.distancia, 3)
        self.assertEqual(resultado.aristas_ruta[0].clave, 1)
        w.reproductor.mostrar(len(resultado.pasos) - 1)
        menor = w.escena.aristas[w.escena.identificador(12, 16, 1)]
        mayor = w.escena.aristas[w.escena.identificador(12, 16, 0)]
        self.assertEqual(menor.item.pen().color().name(), NEON)
        self.assertEqual(mayor.item.pen().color().name(), LINEA)
        w.panel.origen.setText('17')
        w.panel.destino.setText('10')
        w.buscar()
        w.reproductor.pausar()
        indice = next(i for i, p in enumerate(w.reproductor.resultado.pasos)
                      if p.arista and p.arista.origen == 17 and p.arista.destino == 2)
        w.reproductor.mostrar(indice)
        w.escena.animar(0)
        inicio = w.escena.particula.pos()
        w.escena.animar(1)
        fin = w.escena.particula.pos()
        self.assertLess((inicio - w.escena.nodos[17].pos()).manhattanLength(),
                        (fin - w.escena.nodos[17].pos()).manhattanLength())

    def test_exportacion_png_oscura(self):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = str(Path(carpeta) / 'grafo.png')
            with patch.object(QFileDialog, 'getSaveFileName', return_value=(destino, 'PNG')):
                self.ventana.guardar_png()
            imagen = QImage(destino)
            self.assertFalse(imagen.isNull())
            self.assertEqual(imagen.pixelColor(0, 0).name(), FONDO)


    def test_alertas_de_validacion_y_no_inicia_busqueda(self):
        w = self.ventana
        casos = [('999', '10', 'Nodo origen no existe.'),
                 ('17', '999', 'Nodo destino no existe.'),
                 ('999', '888', 'Nodo origen y destino no existen.'),
                 ('', '', 'Nodo origen y destino no existen.'),
                 ('abc', '10', 'Nodo origen no existe.')]
        for origen, destino, mensaje in casos:
            with self.subTest(origen=origen, destino=destino):
                w.panel.origen.setText(origen)
                w.panel.destino.setText(destino)
                with patch.object(QMessageBox, 'warning') as alerta:
                    w.panel.buscar.click()
                    alerta.assert_called_once_with(w, 'Nodos no válidos', mensaje)
                self.assertIsNone(w.reproductor.resultado)
                self.assertFalse(w.reproductor.timer.isActive())
                self.assertFalse(w.panel.play.isEnabled())
        w.panel.origen.setText(' 17 ')
        w.panel.destino.setText(' 10 ')
        w.buscar()
        self.assertEqual(w.reproductor.resultado.distancia, 13)

    def test_visitados_oscuros_y_solo_actual_neon(self):
        w = self.ventana
        w.buscar()
        w.reproductor.pausar()
        resultado = w.reproductor.resultado
        for indice, paso in enumerate(resultado.pasos):
            w.reproductor.mostrar(indice)
            for nodo, item in w.escena.nodos.items():
                if nodo in paso.ruta:
                    self.assertEqual(item.pen().color().name(), NEON)
                    self.assertEqual(item.brush().color().name(), NEON)
                elif nodo == paso.actual:
                    self.assertEqual(item.pen().color().name(), NEON)
                    self.assertEqual(item.brush().color().name(), NODO)
                elif nodo in paso.visitados:
                    self.assertEqual(item.brush().color().name(), VISITADO)
                    self.assertNotEqual(item.pen().color().name(), NEON)
                else:
                    self.assertEqual(item.brush().color().name(), NODO)

    def test_desplegable_y_configuracion_en_posicion_fija(self):
        w = self.ventana
        antes = w.panel.mapTo(w, w.panel.rect().topLeft())
        self.assertEqual(w.matrices.contenido.maximumHeight(), 0)
        w.matrices.boton.click()
        QTest.qWait(280)
        self.assertEqual(w.matrices.contenido.maximumHeight(), 300)
        self.assertEqual(w.panel.mapTo(w, w.panel.rect().topLeft()), antes)
        w.matrices.boton.click()
        QTest.qWait(280)
        self.assertEqual(w.matrices.contenido.maximumHeight(), 0)
        self.assertEqual(w.panel.mapTo(w, w.panel.rect().topLeft()), antes)
        # El zoom manual se conserva al cambiar el tamaño disponible.
        w.vista.zoom(1.2)
        escala = w.vista.transform().m11()
        w.matrices.boton.click()
        QTest.qWait(280)
        self.assertAlmostEqual(w.vista.transform().m11(), escala)

    def test_registro_matricial_pulso_retroceso_y_reset(self):
        w = self.ventana
        w.buscar()
        w.reproductor.pausar()
        resultado = w.reproductor.resultado
        indice = next(i for i, p in enumerate(resultado.pasos) if p.arista)
        w.reproductor.mostrar(indice)
        paso = resultado.pasos[indice]
        for modelo in (w.matrices.modelo_adyacencia, w.matrices.modelo_incidencia):
            activas = modelo.celdas_arista(paso.arista)
            cruz = modelo.celdas_cruz(modelo.fila_cruz, modelo.columna_cruz)
            self.assertEqual(modelo.activas, cruz)
            self.assertTrue((modelo.filas[paso.arista.origen],
                             modelo.columna_cruz) in modelo.activas)
            self.assertTrue(activas.issubset(modelo.consultadas))
            celda = modelo.index(modelo.fila_cruz, modelo.columna_cruz)
            antes = modelo.data(celda, Qt.ItemDataRole.BackgroundRole).color()
            w.matrices.animar(0.5)
            despues = modelo.data(celda, Qt.ItemDataRole.BackgroundRole).color()
            self.assertNotEqual(antes, despues)
            w.matrices.animar(0)
        w.reproductor.mostrar(indice - 1)
        self.assertFalse(w.matrices.modelo_adyacencia.consultadas)
        self.assertIsNone(w.matrices.modelo_incidencia.columna_cruz)
        self.assertEqual(len(w.matrices.modelo_incidencia.activas), 64)
        w.reproductor.mostrar(len(resultado.pasos) - 1)
        self.assertTrue(w.matrices.modelo_adyacencia.activas)
        w.panel.destino.setText('16')
        self.assertFalse(w.matrices.modelo_adyacencia.activas)
        self.assertFalse(w.matrices.modelo_incidencia.consultadas)

    def test_matrices_sin_edicion_y_pesos_originales(self):
        w = self.ventana
        ady, inc = w.matrices.modelo_adyacencia, w.matrices.modelo_incidencia
        self.assertEqual((ady.rowCount(), ady.columnCount()), (30, 30))
        self.assertEqual((inc.rowCount(), inc.columnCount()), (30, 64))
        indice = ady.index(ady.filas[12], ady.filas[16])
        self.assertEqual(ady.data(indice), '2')
        self.assertFalse(ady.flags(indice) & Qt.ItemFlag.ItemIsEditable)
        self.assertIn('16, 3', ady.data(indice, Qt.ItemDataRole.ToolTipRole))
        w.selector_grafo.setCurrentIndex(0)
        indice = ady.index(ady.filas[66], ady.filas[13])
        self.assertIn('-777', ady.data(indice, Qt.ItemDataRole.ToolTipRole))


    def test_cruces_completas_y_pulso_sin_modificar_matrices(self):
        w = self.ventana
        w.buscar()
        w.reproductor.pausar()
        resultado = w.reproductor.resultado
        indice = next(i for i, p in enumerate(resultado.pasos) if p.arista)
        w.reproductor.mostrar(indice)
        for modelo in (w.matrices.modelo_adyacencia, w.matrices.modelo_incidencia):
            f, c = modelo.fila_cruz, modelo.columna_cruz
            esperadas = {(f, col) for col in range(modelo.columnCount())}
            esperadas.update((fila, c) for fila in range(modelo.rowCount()))
            self.assertEqual(modelo.activas, esperadas)
            self.assertEqual(len(modelo.activas), modelo.rowCount() + modelo.columnCount() - 1)
            valores = modelo.valores
            modelo.animar(0.5)
            centro = modelo.data(modelo.index(f, c), Qt.ItemDataRole.BackgroundRole).color()
            for fila, columna in esperadas:
                self.assertEqual(modelo.data(modelo.index(fila, columna), Qt.ItemDataRole.BackgroundRole).color(), centro)
            self.assertEqual(modelo.valores, valores)

    def test_ruta_parpadea_cinco_veces_y_permanece_fosforescente(self):
        w = self.ventana
        w.buscar()
        w.reproductor.pausar()
        fases, finales = [], []
        w.celebracion.fase_cambiada.connect(fases.append)
        w.celebracion.terminado.connect(lambda: finales.append(True))
        w.reproductor.mostrar(len(w.reproductor.resultado.pasos) - 1)
        paso = w.escena.paso
        self.assertTrue(w.celebracion.timer.isActive())
        for transicion in range(1, 11):
            w.celebracion.avanzar()
            iluminado = transicion % 2 == 0
            for nodo in paso.ruta:
                self.assertEqual(w.escena.nodos[nodo].brush().color().name(), NEON if iluminado else VISITADO)
        self.assertEqual(fases, [True] + [i % 2 == 0 for i in range(1, 11)])
        self.assertEqual(fases.count(False), 5)
        self.assertEqual(w.celebracion.ciclos_completos, 5)
        self.assertEqual(finales, [True])
        self.assertFalse(w.celebracion.timer.isActive())
        w.celebracion.avanzar()
        self.assertEqual(len(fases), 11)
        for nodo in paso.visitados - set(paso.ruta):
            self.assertEqual(w.escena.nodos[nodo].brush().color().name(), VISITADO)

    def test_parpadeo_real_y_cancelacion(self):
        w = self.ventana
        w.buscar()
        w.reproductor.pausar()
        ultimo = len(w.reproductor.resultado.pasos) - 1
        w.reproductor.mostrar(ultimo)
        QTest.qWait(1050)
        self.assertEqual(w.celebracion.ciclos_completos, 5)
        self.assertFalse(w.celebracion.timer.isActive())
        w.reproductor.mostrar(ultimo)
        self.assertTrue(w.celebracion.timer.isActive())
        w.panel.atras.click()
        self.assertFalse(w.celebracion.timer.isActive())
        w.reproductor.mostrar(ultimo)
        w.panel.destino.setText('16')
        self.assertFalse(w.celebracion.timer.isActive())
        self.assertIsNone(w.reproductor.resultado)
        self.assertTrue(all(n.brush().color().name() == NODO for n in w.escena.nodos.values()))
        w.buscar()
        w.reproductor.pausar()
        w.reproductor.mostrar(len(w.reproductor.resultado.pasos) - 1)
        w.selector_grafo.setCurrentIndex(0)
        self.assertFalse(w.celebracion.timer.isActive())


if __name__ == '__main__':
    unittest.main()
