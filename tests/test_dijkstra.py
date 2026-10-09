"""Pruebas del algoritmo propio con un oráculo Floyd–Warshall independiente."""
import unittest
from math import inf
from algoritmos.dijkstra import ejecutar_dijkstra
from algoritmos.tipos import Conexion
from modelos.grafos import cargar_grafos, obtener_adyacencia


class DijkstraTests(unittest.TestCase):
    def test_ruta_17_a_10(self):
        grafo = cargar_grafos()['positivo']
        resultado = ejecutar_dijkstra(obtener_adyacencia(grafo), 17, 10)
        self.assertTrue(resultado.encontrado)
        self.assertEqual(resultado.ruta, (17, 2, 1, 10))
        self.assertEqual(resultado.distancia, 13)
        self.assertEqual(sum(a.peso for a in resultado.aristas_ruta), 13)
        for arista in resultado.aristas_ruta:
            self.assertEqual(grafo[arista.origen][arista.destino][arista.clave]['weight'], arista.peso)

    def test_todos_los_pares_con_oraculo_independiente(self):
        grafo = cargar_grafos()['positivo']
        adyacencia = obtener_adyacencia(grafo)
        nodos = list(grafo)
        distancias = {(u, v): 0 if u == v else inf for u in nodos for v in nodos}
        for u, conexiones in adyacencia.items():
            for conexion in conexiones:
                par = (u, conexion.destino)
                distancias[par] = min(distancias[par], conexion.peso)
        for k in nodos:
            for u in nodos:
                for v in nodos:
                    distancias[u, v] = min(distancias[u, v], distancias[u, k] + distancias[k, v])
        for u in nodos:
            for v in nodos:
                with self.subTest(origen=u, destino=v):
                    self.assertEqual(ejecutar_dijkstra(adyacencia, u, v).distancia, distancias[u, v])

    def test_aristas_paralelas_y_actualizacion_de_cola(self):
        adyacencia = {
            'A': (Conexion('B', 'cara', 9), Conexion('B', 'barata', 2), Conexion('C', 0, 10)),
            'B': (Conexion('C', 1, 1),), 'C': (),
        }
        resultado = ejecutar_dijkstra(adyacencia, 'A', 'C')
        self.assertEqual(resultado.ruta, ('A', 'B', 'C'))
        self.assertEqual(resultado.distancia, 3)
        self.assertEqual(resultado.aristas_ruta[0].clave, 'barata')
        self.assertEqual(sum(p.tipo == 'seleccionar' for p in resultado.pasos), 3)

    def test_cero_bucle_y_empates_con_identificadores_distintos(self):
        adyacencia = {0: (Conexion(0, 0, 0), Conexion('A', 0, 0), Conexion(2, 0, 0)),
                      'A': (Conexion(3, 0, 1),), 2: (Conexion(3, 0, 1),), 3: ()}
        resultado = ejecutar_dijkstra(adyacencia, 0, 3)
        self.assertEqual(resultado.distancia, 1)
        self.assertEqual(resultado.ruta[0], 0)
        self.assertEqual(resultado.ruta[-1], 3)

    def test_inaccesible_y_origen_igual_destino(self):
        adyacencia = {1: (), 2: ()}
        resultado = ejecutar_dijkstra(adyacencia, 1, 2)
        self.assertFalse(resultado.encontrado)
        self.assertEqual(resultado.distancia, inf)
        self.assertEqual(resultado.pasos[-1].tipo, 'sin_ruta')
        mismo = ejecutar_dijkstra(adyacencia, 1, 1)
        self.assertEqual(mismo.ruta, (1,))
        self.assertEqual(mismo.distancia, 0)
        self.assertEqual(mismo.aristas_ruta, ())

    def test_rechaza_negativos_incluso_fuera_del_componente(self):
        with self.assertRaisesRegex(ValueError, 'no negativos'):
            ejecutar_dijkstra(obtener_adyacencia(cargar_grafos()['original']), 17, 10)
        for peso in (-1, inf, float('nan')):
            with self.subTest(peso=peso), self.assertRaises(ValueError):
                ejecutar_dijkstra({1: (), 2: (Conexion(2, 0, peso),)}, 1, 1)

    def test_nodos_inexistentes(self):
        with self.assertRaises(ValueError):
            ejecutar_dijkstra({1: ()}, 1, 2)
        with self.assertRaises(ValueError):
            ejecutar_dijkstra({1: (Conexion(2, 0, 1),)}, 1, 1)

    def test_instantaneas_y_no_modifica_datos(self):
        grafo = cargar_grafos()['positivo']
        adyacencia = obtener_adyacencia(grafo)
        antes = dict(adyacencia)
        resultado = ejecutar_dijkstra(adyacencia, 17, 10)
        self.assertEqual(adyacencia, antes)
        self.assertEqual(resultado.pasos[0].distancias[10], inf)
        self.assertEqual(resultado.pasos[-1].distancias[10], 13)
        self.assertEqual(resultado.pasos[0].predecesores, {})
        self.assertEqual(resultado.pasos[0].visitados, frozenset())
        definitivas = []
        for paso in resultado.pasos:
            if paso.tipo == 'seleccionar':
                definitivas.append(paso.distancias[paso.actual])
        self.assertEqual(definitivas, sorted(definitivas))


if __name__ == '__main__':
    unittest.main()
