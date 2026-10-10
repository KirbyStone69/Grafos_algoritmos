"""Algoritmo propio: ejemplo del PDF, arcos paralelos y ciclos negativos."""
import unittest
from math import inf
from algoritmos.bellman_ford import ejecutar_bellman_ford
from algoritmos.tipos import Conexion
from modelos.grafos import cargar_grafos, obtener_adyacencia


def ejemplo_pdf():
    # Orden exacto de Lista de Arcos en Bellman-Ford__Ejemplo.pdf.
    return {
        'u': (Conexion('v', 0, 5), Conexion('x', 0, 8), Conexion('y', 0, -4)),
        'v': (Conexion('u', 0, -2),),
        'x': (Conexion('v', 0, -3), Conexion('y', 0, 9)),
        'y': (Conexion('v', 0, 7), Conexion('z', 0, 2)),
        'z': (Conexion('u', 0, 6), Conexion('x', 0, 7)),
    }


class BellmanFordTests(unittest.TestCase):
    def test_distancias_y_predecesores_de_la_solucion_del_pdf(self):
        resultado = ejecutar_bellman_ford(ejemplo_pdf(), 'z')
        self.assertFalse(resultado.ciclo_negativo)
        self.assertTrue(resultado.encontrado)
        self.assertEqual(resultado.distancias, {'u': 2, 'v': 4, 'x': 7, 'y': -2, 'z': 0})
        self.assertEqual(resultado.pasos[-1].predecesores, {'u': 'v', 'v': 'x', 'x': 'z', 'y': 'u'})
        self.assertEqual(resultado.pasadas, 4)
        self.assertEqual(resultado.pasos[0].distancias['u'], inf)
        self.assertEqual(resultado.pasos[0].distancias['z'], 0)
        primer_arco = next(p for p in resultado.pasos if p.arista)
        self.assertEqual((primer_arco.pasada, primer_arco.indice_arco), (1, 1))
        self.assertFalse(primer_arco.respuesta)
        self.assertEqual(resultado.pasos[-1].tipo, 'fin')

    def test_ruta_y_claves_del_pdf(self):
        r = ejecutar_bellman_ford(ejemplo_pdf(), 'z', 'y')
        self.assertEqual(r.ruta, ('z', 'x', 'v', 'u', 'y'))
        self.assertEqual(r.distancia, -2)
        self.assertEqual(sum(a.peso for a in r.aristas_ruta), -2)

    def test_ciclo_del_grafo_original_y_afectados(self):
        grafo = cargar_grafos()['original']
        r = ejecutar_bellman_ford(obtener_adyacencia(grafo), 17, 10)
        self.assertTrue(r.ciclo_negativo)
        self.assertFalse(r.encontrado)
        self.assertEqual(r.distancia, -inf)
        self.assertEqual(r.afectados, frozenset(grafo))
        self.assertEqual(r.ruta, ())
        self.assertEqual(r.ciclo[0], r.ciclo[-1])
        self.assertLess(sum(a.peso for a in r.aristas_ciclo), 0)
        for a in r.aristas_ciclo:
            self.assertEqual(grafo[a.origen][a.destino][a.clave]['weight'], a.peso)
        for a, b in zip(r.aristas_ciclo, r.aristas_ciclo[1:]):
            self.assertEqual(a.destino, b.origen)
        self.assertTrue(any(p.tipo == 'verificar' and not p.respuesta for p in r.pasos))
        self.assertEqual(r.pasos[-1].tipo, 'ciclo_negativo')

    def test_ciclo_no_alcanzable_no_invalida_el_origen(self):
        ady = {0: (Conexion(1, 0, 4),), 1: (), 2: (Conexion(2, 0, -1),)}
        r = ejecutar_bellman_ford(ady, 0, 1)
        self.assertFalse(r.ciclo_negativo)
        self.assertEqual(r.distancia, 4)
        self.assertEqual(r.distancias[2], inf)

    def test_afectados_y_destino_fuera_del_ciclo(self):
        ady = {0: (Conexion(1, 0, 1), Conexion(3, 0, 7)),
               1: (Conexion(1, 0, -1), Conexion(2, 0, 3)), 2: (), 3: ()}
        r = ejecutar_bellman_ford(ady, 0, 3)
        self.assertTrue(r.ciclo_negativo)
        self.assertEqual(r.afectados, frozenset({1, 2}))
        self.assertTrue(r.encontrado)
        self.assertEqual(r.distancia, 7)
        self.assertEqual(r.ruta, (0, 3))
        self.assertEqual(r.distancias[0], 0)

    def test_paralelas_cero_inaccesible_y_origen_igual_destino(self):
        ady = {0: (Conexion(1, 'cara', 3), Conexion(1, 'barata', -1)),
               1: (Conexion(2, 0, 1),), 2: (), 3: ()}
        r = ejecutar_bellman_ford(ady, 0, 2)
        self.assertEqual(r.distancia, 0)
        self.assertEqual(r.aristas_ruta[0].clave, 'barata')
        self.assertEqual(ejecutar_bellman_ford(ady, 0, 0).ruta, (0,))
        inaccesible = ejecutar_bellman_ford(ady, 0, 3)
        self.assertFalse(inaccesible.encontrado)
        self.assertEqual(inaccesible.distancia, inf)
        self.assertEqual(inaccesible.pasos[-1].tipo, 'sin_ruta')
        self.assertTrue(ejecutar_bellman_ford({0: (Conexion(0, 0, -1),)}, 0).ciclo_negativo)

    def test_pesos_y_nodos_invalidos(self):
        for ady, origen, destino in [({}, 0, None), ({0: ()}, 0, 2),
                                    ({0: (Conexion(2, 0, 1),)}, 0, None),
                                    ({0: (Conexion(0, 0, inf),)}, 0, None),
                                    ({0: (Conexion(0, 0, float('nan')), )}, 0, None)]:
            with self.subTest(ady=ady), self.assertRaises(ValueError):
                ejecutar_bellman_ford(ady, origen, destino)

    def test_grafo_positivo_900_pares_con_oraculo_independiente(self):
        # La lógica general admite positivos; la interfaz se limita al original.
        ady = obtener_adyacencia(cargar_grafos()['positivo'])
        nodos = list(ady)
        d = {(u, v): 0 if u == v else inf for u in nodos for v in nodos}
        for u, conexiones in ady.items():
            for c in conexiones:
                d[u, c.destino] = min(d[u, c.destino], c.peso)
        for k in nodos:
            for u in nodos:
                for v in nodos:
                    d[u, v] = min(d[u, v], d[u, k] + d[k, v])
        for origen in nodos:
            r = ejecutar_bellman_ford(ady, origen)
            self.assertFalse(r.ciclo_negativo)
            for destino in nodos:
                self.assertEqual(r.distancias[destino], d[origen, destino])

    def test_costo_del_origen_y_predecesores_afectados_no_son_finitos(self):
        ady = {0: (Conexion(1, 0, -2),), 1: (Conexion(0, 0, -2),)}
        r = ejecutar_bellman_ford(ady, 0)
        self.assertEqual(r.distancia, -inf)
        self.assertEqual(r.pasos[-1].predecesores, {})
        self.assertTrue(r.aristas_ciclo)
        parcial = ejecutar_bellman_ford({0: (Conexion(1, 0, 1), Conexion(2, 0, 7)),
                                        1: (Conexion(1, 0, -1),), 2: ()}, 0, 2)
        self.assertEqual(parcial.distancia, 7)
        self.assertNotIn(1, parcial.pasos[-1].predecesores)
        self.assertEqual(parcial.pasos[-1].predecesores[2], 0)

    def test_pesos_no_numericos_y_desbordamiento_se_informan(self):
        with self.assertRaisesRegex(ValueError, 'numéricos'):
            ejecutar_bellman_ford({0: (Conexion(1, 0, 'incorrecto'),), 1: ()}, 0)
        with self.assertRaisesRegex(ValueError, 'rango numérico'):
            ejecutar_bellman_ford({0: (Conexion(1, 0, -1e308),),
                                  1: (Conexion(2, 0, -1e308),), 2: ()}, 0)


if __name__ == '__main__':
    unittest.main()
