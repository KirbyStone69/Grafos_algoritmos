"""Verifica convenciones matemáticas y validación sin cargar Qt."""
import unittest
import networkx as nx
from modelos.grafos import cargar_grafos
from modelos.matrices import construir_matrices
from modelos.validacion import validar_extremos


class MatricesTests(unittest.TestCase):
    def test_simetria_grados_y_una_columna_por_arista(self):
        grafo = cargar_grafos()['positivo']
        m = construir_matrices(grafo)
        self.assertEqual(len(m.nodos), 30)
        self.assertEqual(len(m.aristas), 64)
        for fila, nodo in enumerate(m.nodos):
            self.assertEqual(sum(m.adyacencia[fila]), grafo.degree(nodo))
            self.assertEqual(sum(m.incidencia[fila]), grafo.degree(nodo))
            for columna in range(len(m.nodos)):
                self.assertEqual(m.adyacencia[fila][columna], m.adyacencia[columna][fila])
        for columna, arista in enumerate(m.aristas):
            self.assertEqual(sum(fila[columna] for fila in m.incidencia), 2)
            extremos = {m.nodos[i] for i, fila in enumerate(m.incidencia) if fila[columna]}
            self.assertEqual(extremos, {arista.origen, arista.destino})

    def test_paralelas_conservan_pesos_y_columnas_independientes(self):
        grafos = cargar_grafos()
        original, positivo = (construir_matrices(grafos[n]) for n in ('original', 'positivo'))
        self.assertEqual(original.adyacencia, positivo.adyacencia)
        self.assertEqual(original.incidencia, positivo.incidencia)
        self.assertEqual(original.nodos, positivo.nodos)
        for a, b in zip(original.aristas, positivo.aristas):
            self.assertEqual((a.origen, a.destino, a.clave), (b.origen, b.destino, b.clave))
            self.assertEqual(abs(a.peso), b.peso)
        aristas = [a for a in positivo.aristas if {a.origen, a.destino} == {12, 16}]
        self.assertEqual(sorted(a.peso for a in aristas), [3, 16])
        self.assertEqual(len({a.clave for a in aristas}), 2)

    def test_bucle_y_peso_cero_no_se_pierden(self):
        grafo = nx.MultiGraph()
        grafo.add_edge(1, 1, weight=0)
        grafo.add_edge(1, 2, weight=0)
        m = construir_matrices(grafo)
        self.assertEqual(m.adyacencia, ((1, 1), (1, 0)))
        self.assertEqual(m.incidencia, ((2, 1), (0, 1)))

    def test_validacion_cero_espacios_y_mensajes(self):
        grafo = cargar_grafos()['positivo']
        self.assertEqual(validar_extremos(grafo, ' 0 ', '10'), (0, 10))
        self.assertEqual(validar_extremos(grafo, '17', '17'), (17, 17))
        casos = [('999', '10', 'Nodo origen no existe.'),
                 ('17', 'x', 'Nodo destino no existe.'),
                 ('', '999', 'Nodo origen y destino no existen.')]
        for origen, destino, mensaje in casos:
            with self.assertRaisesRegex(ValueError, mensaje):
                validar_extremos(grafo, origen, destino)


if __name__ == '__main__':
    unittest.main()
