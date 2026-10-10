"""Pestaña independiente, ejemplo documental, matrices, controles y consultas."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import patch
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMessageBox
from interfaz.ventana import VentanaGrafo
from interfaz.tema import ESTILO


class FloydInterfazTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])
        cls.app.setStyle('Fusion'); cls.app.setStyleSheet(ESTILO)

    def setUp(self):
        self.w=VentanaGrafo(); self.w.show(); self.w.pestanas.setCurrentIndex(2)
        self.f=self.w.interfaz_actual; self.app.processEvents()

    def tearDown(self):
        self.w.close(); self.w.deleteLater(); self.app.processEvents()

    def test_debug_matrices_proyecto_y_consulta_sin_recalcular(self):
        f=self.f; f.debug.click(); r=f.reproductor.resultado
        self.assertEqual(f.reproductor.indice,len(r.pasos)-1)
        self.assertFalse(f.reproductor.timer.isActive())
        self.assertEqual(f.modelo_distancias.rowCount(),30)
        f.consultar.click()
        self.assertIn('Costo: 13',f.consulta.text())
        self.assertIn('17 → 2 → 1 → 10',f.consulta.text())
        f.origen.setText('0'); f.destino.setText('0'); f.consultar.click()
        self.assertIn('Costo: 0',f.consulta.text())
        self.assertIs(f.reproductor.resultado,r)
        f.origen.setText('999')
        with patch.object(QMessageBox,'warning') as alerta:
            f.consultar.click(); self.assertEqual(alerta.call_args.args[2],'Nodo origen no existe.')

    def test_ejemplo_documental_y_consulta_celda(self):
        f=self.f; f.fuente.setCurrentIndex(1); f.buscar(debug=True)
        self.assertEqual(f.modelo_distancias.rowCount(),8)
        self.assertEqual(f.reproductor.resultado.distancias[1][6],6)
        f.consultar_celda(f.modelo_distancias.index(1,6))
        self.assertIn('B → D → H → G',f.consulta.text())
        self.assertIn('Costo: 6',f.consulta.text())
        r=f.reproductor.resultado
        self.w.selector_grafo.setCurrentIndex(0)
        self.assertIs(f.reproductor.resultado,r)
        self.assertEqual(tuple(f.grafo.nodes),tuple('ABCDEFGH'))

    def test_intermedio_comparacion_cruz_retroceso_y_cambio_de_fuente(self):
        f=self.f; f.buscar(); f.reproductor.pausar()
        f.avanzar_k()
        self.assertEqual(f.reproductor.resultado.pasos[f.reproductor.indice].tipo,'iteracion_fin')
        f.reproductor.mostrar(2)
        p=f.reproductor.resultado.pasos[2]
        self.assertEqual(p.tipo,'comparar')
        self.assertIn('D[',f.comparacion.text())
        modelo=f.modelo_distancias
        self.assertIsNotNone(modelo.data(modelo.index(p.k,4),Qt.ItemDataRole.BackgroundRole))
        self.assertFalse(modelo.flags(modelo.index(0,0)) & Qt.ItemFlag.ItemIsEditable)
        f.reproductor.anterior(); self.assertEqual(f.reproductor.indice,1)
        f.fuente.setCurrentIndex(1)
        self.assertIsNone(f.reproductor.resultado)
        self.assertFalse(f.consultar.isEnabled())
        self.assertEqual(f.modelo_distancias.rowCount(),8)

    def test_original_negativo_no_muestra_camino_ganador(self):
        f=self.f; self.w.selector_grafo.setCurrentIndex(0); f.buscar(debug=True)
        self.assertEqual(len(f.reproductor.resultado.afectados),900)
        f.consultar_ruta()
        self.assertIn('No existe mínimo finito',f.consulta.text())
        self.assertFalse(f.celebracion.timer.isActive())
        self.assertEqual(f.modelo_distancias.data(f.modelo_distancias.index(0,0)),'−∞')
        self.assertEqual(f.modelo_recorridos.data(f.modelo_recorridos.index(0,0)),'—')

    def test_detencion_por_pestana_y_modo_debug(self):
        f=self.f; f.buscar(); self.assertTrue(f.reproductor.timer.isActive())
        self.w.pestanas.setCurrentIndex(0); self.assertFalse(f.reproductor.timer.isActive())
        self.w.pestanas.setCurrentIndex(2); f.buscar()
        f.modo.setCurrentIndex(2)
        self.assertEqual(f.reproductor.indice,len(f.reproductor.resultado.pasos)-1)
        self.assertFalse(f.reproductor.timer.isActive())


if __name__=='__main__': unittest.main()
