"""Integración de la interfaz específica de Bellman–Ford basada en el PDF."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import unittest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtTest import QTest
from interfaz.ventana import VentanaGrafo
from interfaz.tema import ESTILO


class BellmanInterfazTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle('Fusion')
        cls.app.setStyleSheet(ESTILO)

    def setUp(self):
        self.w = VentanaGrafo()
        self.w.show()
        self.w.pestanas.setCurrentIndex(1)
        self.b = self.w.interfaz_actual
        self.app.processEvents()

    def tearDown(self):
        self.w.close()
        self.w.deleteLater()
        self.app.processEvents()

    def test_interfaz_propia_y_seleccion_del_negativo(self):
        self.assertEqual(self.w.selector_grafo.currentData(), 'original')
        self.assertEqual(self.b.lista_arcos.count(), 128)
        self.assertEqual((self.b.vectores.rowCount(), self.b.vectores.columnCount()), (3, 30))
        self.assertFalse(hasattr(self.b, 'matrices'))
        self.assertTrue(self.b.ejecutar.isEnabled())
        self.w.selector_grafo.setCurrentIndex(1)
        self.assertFalse(self.b.ejecutar.isEnabled())
        self.b.buscar()
        self.assertIsNone(self.b.reproductor.resultado)
        self.w.pestanas.setCurrentIndex(0)
        self.assertEqual(self.w.selector_grafo.currentData(), 'positivo')
        self.assertTrue(self.w.interfaz_actual.panel.buscar.isEnabled())

    def test_relajacion_vectores_lista_animacion_y_saltos(self):
        b = self.b
        b.buscar()
        b.reproductor.pausar()
        resultado = b.reproductor.resultado
        indice = next(i for i, p in enumerate(resultado.pasos) if p.arista and p.respuesta and not p.verificacion)
        b.saltar(indice)
        paso = resultado.pasos[indice]
        self.assertEqual(b.relajacion.respuesta.text(), 'SÍ')
        self.assertIn('Π[', b.relajacion.proceso.text())
        self.assertEqual(b.lista_arcos.currentRow(), paso.indice_arco - 1)
        col = b.vectores.indices[paso.arista.destino]
        self.assertEqual(b.vectores.item(1, col).text(), f'{paso.candidato:g}')
        self.assertEqual(b.vectores.item(2, col).text(), str(paso.arista.origen))
        b.escena.animar(0.5)
        self.assertTrue(b.escena.particula.isVisible())
        b.siguiente_pasada()
        self.assertEqual(b.reproductor.resultado.pasos[b.reproductor.indice].tipo, 'pasada')
        b.reproductor.siguiente()
        b.ir_arco(b.lista_arcos.item(7))
        self.assertEqual(b.reproductor.resultado.pasos[b.reproductor.indice].indice_arco, 8)
        b.ir_verificacion()
        self.assertEqual(b.reproductor.resultado.pasos[b.reproductor.indice].tipo, 'verificacion')
        b.mostrar_resultado()
        self.assertIn('NO EXISTE MÍNIMO FINITO', b.relajacion.respuesta.text())
        self.assertIn('Peso del ciclo', b.relajacion.proceso.text())
        self.assertTrue(all(b.vectores.item(1, c).text() == '−∞' for c in range(30)))
        self.assertFalse(b.reproductor.timer.isActive())
        b.reproductor.reiniciar()
        self.assertEqual(b.reproductor.indice, 0)
        self.assertEqual(b.relajacion.respuesta.text(), '—')

    def test_errores_de_extremos_y_destino_opcional(self):
        b = self.b
        for origen, destino, texto in [('999', '', 'Nodo origen no existe.'),
                                       ('17', '999', 'Nodo destino no existe.'),
                                       ('999', '10', 'Nodo origen no existe.')]:
            b.configuracion.origen.setText(origen)
            b.configuracion.destino.setText(destino)
            with patch.object(QMessageBox, 'warning') as alerta:
                b.buscar()
                self.assertEqual(alerta.call_args.args[2], texto)
            self.assertIsNone(b.reproductor.resultado)
        b.configuracion.origen.setText('17')
        b.configuracion.destino.setText('')
        b.buscar()
        self.assertIsNone(b.reproductor.resultado.destino)

    def test_cancela_en_cambio_de_parametros_o_pestana(self):
        b = self.b
        b.buscar()
        b.reproductor.duracion = 45
        QTest.qWait(160)
        self.assertGreater(b.reproductor.indice, 0)
        b.configuracion.destino.setText('10')
        self.assertFalse(b.reproductor.timer.isActive())
        self.assertIsNone(b.reproductor.resultado)
        b.buscar()
        self.w.pestanas.setCurrentIndex(0)
        self.assertFalse(b.reproductor.timer.isActive())
        self.assertEqual(self.w.selector_grafo.currentData(), 'positivo')


    def test_debug_directo_conserva_traza_y_permite_inspeccion(self):
        b = self.b
        b.debug.click()
        r = b.reproductor.resultado
        self.assertEqual(b.modo.currentIndex(), 2)
        self.assertEqual(len(r.pasos), 3872)
        self.assertEqual(b.reproductor.indice, len(r.pasos) - 1)
        self.assertFalse(b.reproductor.timer.isActive())
        self.assertEqual(b.progreso_busqueda.value(), len(r.pasos))
        self.assertIn('NO EXISTE MÍNIMO FINITO', b.relajacion.respuesta.text())
        self.assertFalse(b.escena.particula.isVisible())
        b.evento.setValue(125)
        b.evento.editingFinished.emit()
        self.assertEqual(b.reproductor.indice, 124)
        self.assertEqual(b.progreso_busqueda.value(), 125)
        self.assertEqual(b.reproductor.resultado, r)
        b.play.click()
        self.assertEqual(b.reproductor.indice, len(r.pasos) - 1)
        self.assertFalse(b.reproductor.timer.isActive())

    def test_rapido_finaliza_en_segundos_y_da_el_mismo_resultado(self):
        from time import perf_counter
        b = self.b
        self.assertEqual(b.modo.currentIndex(), 1)
        self.assertEqual(b.reproductor.bloque, 64)
        inicio = perf_counter()
        b.buscar()
        r = b.reproductor.resultado
        while b.reproductor.timer.isActive() and perf_counter() - inicio < 8:
            QTest.qWait(20)
        self.assertFalse(b.reproductor.timer.isActive())
        self.assertEqual(b.reproductor.indice, len(r.pasos) - 1)
        self.assertEqual(b.progreso_busqueda.value(), 3872)
        self.assertTrue(r.ciclo_negativo)
        self.assertEqual(len(r.afectados), 30)
        b.reproductor.anterior()
        self.assertEqual(b.reproductor.indice, len(r.pasos) - 2)
        self.assertFalse(b.reproductor.timer.isActive())

    def test_cambio_de_modos_velocidad_y_cancelacion_limpian_progreso(self):
        b = self.b
        b.buscar()
        QTest.qWait(90)
        b.modo.setCurrentIndex(0)
        self.assertFalse(b.reproductor.timer.isActive())
        self.assertEqual(b.reproductor.bloque, 1)
        indice = b.reproductor.indice
        b.reproductor.siguiente()
        self.assertEqual(b.reproductor.indice, indice + 1)
        b.velocidad.setValue(10)
        self.assertEqual(b.reproductor.duracion, 40)
        b.modo.setCurrentIndex(1)
        self.assertEqual(b.reproductor.bloque, 88)
        b.modo.setCurrentIndex(2)
        self.assertEqual(b.reproductor.indice, len(b.reproductor.resultado.pasos) - 1)
        b.configuracion.destino.setText('10')
        self.assertIsNone(b.reproductor.resultado)
        self.assertFalse(b.evento.isEnabled())
        self.assertEqual(b.evento.maximum(), 1)
        self.assertEqual(b.progreso_busqueda.value(), 0)

    def test_un_ciclo_en_otra_rama_no_oculta_destino_finito(self):
        from algoritmos.bellman_ford import ejecutar_bellman_ford
        from algoritmos.tipos import Conexion
        r = ejecutar_bellman_ford({0: (Conexion(1, 0, 1), Conexion(2, 0, 7)),
                                  1: (Conexion(1, 0, -1),), 2: ()}, 0, 2)
        self.b.relajacion.mostrar(r.pasos[-1], r)
        self.assertEqual(self.b.relajacion.respuesta.text(), 'DESTINO CON MÍNIMO FINITO')
        self.assertIn('costo mínimo es 7', self.b.relajacion.proceso.text())


if __name__ == '__main__':
    unittest.main()
