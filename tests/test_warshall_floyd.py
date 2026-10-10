"""Matrices y rutas calculadas, contrastadas con documentos y otros algoritmos."""
import random
import unittest
from math import inf
from algoritmos.warshall_floyd import ejecutar_warshall_floyd
from algoritmos.dijkstra import ejecutar_dijkstra
from algoritmos.bellman_ford import ejecutar_bellman_ford
from algoritmos.tipos import Conexion
from modelos.grafos import cargar_grafos, obtener_adyacencia
from modelos.ejemplo_floyd import cargar_ejemplo_floyd


class FloydTests(unittest.TestCase):
    def test_matriz_del_documento_calculada_y_errores_de_hoja_corregidos(self):
        grafo = cargar_ejemplo_floyd()
        self.assertEqual(grafo.number_of_nodes(), 8)
        self.assertEqual(grafo.number_of_edges(), 14)
        r = ejecutar_warshall_floyd(obtener_adyacencia(grafo))
        esperada = (
            (0,6,9,5,11,11,8,8), (6,0,5,1,7,7,6,4),
            (9,5,0,4,4,2,8,6), (5,1,4,0,6,6,5,3),
            (11,7,4,6,0,2,8,6), (11,7,2,6,2,0,6,4),
            (8,6,8,5,8,6,0,2), (8,4,6,3,6,4,2,0))
        self.assertEqual(r.distancias, esperada)
        self.assertEqual(r.consultar('A','H')[0:2], (8, ('A','D','H')))
        # En Hoja1 aparece 0 tras k=A para C→A; debe seguir siendo ∞.
        self.assertEqual(r.pasos[r.finales_iteracion[0]].distancias[2][0], inf)
        # Hoja2 mantiene B→G=14 pero G→B=6; el mínimo correcto es 6 en ambos.
        self.assertEqual(r.distancias[1][6], r.distancias[6][1])
        self.assertEqual(r.distancias[1][6], 6)

    def test_900_pares_y_rutas_coinciden_con_dijkstra(self):
        ady = obtener_adyacencia(cargar_grafos()['positivo'])
        r = ejecutar_warshall_floyd(ady)
        self.assertFalse(r.ciclos)
        for origen in ady:
            for destino in ady:
                costo, ruta, aristas = r.consultar(origen, destino)
                referencia = ejecutar_dijkstra(ady, origen, destino)
                self.assertEqual(costo, referencia.distancia)
                self.assertEqual(ruta[0], origen)
                self.assertEqual(ruta[-1], destino)
                self.assertEqual(sum(a.peso for a in aristas), costo)
                for a in aristas:
                    self.assertTrue(any(c.destino == a.destino and c.clave == a.clave and c.peso == a.peso for c in ady[a.origen]))

    def test_negativos_del_pdf_bellman_sin_ciclos(self):
        from test_bellman_ford import ejemplo_pdf
        ady = ejemplo_pdf()
        r = ejecutar_warshall_floyd(ady)
        for origen in ady:
            b = ejecutar_bellman_ford(ady, origen)
            for destino in ady:
                self.assertEqual(r.consultar(origen, destino)[0], b.distancias[destino])
        self.assertEqual(r.consultar('z','y')[0:2], (-2, ('z','x','v','u','y')))

    def test_ciclos_afectan_solo_pares_con_acceso_y_salida(self):
        ady = {0:(Conexion(1,0,2), Conexion(3,0,7)), 1:(Conexion(1,0,-1), Conexion(2,0,1)), 2:(), 3:(), 4:()}
        r = ejecutar_warshall_floyd(ady)
        self.assertEqual(r.afectados, frozenset({(0,1),(0,2),(1,1),(1,2)}))
        self.assertEqual(r.consultar(0,3)[0:2], (7,(0,3)))
        self.assertEqual(r.consultar(4,1), (inf,(),()))
        with self.assertRaisesRegex(ValueError,'ciclo negativo'):
            r.consultar(0,2)
        self.assertIsNone(r.siguientes[0][2])

    def test_grafo_original_900_pares_sin_minimo(self):
        ady = obtener_adyacencia(cargar_grafos()['original'])
        r = ejecutar_warshall_floyd(ady)
        self.assertEqual(len(r.afectados), 900)
        self.assertTrue(all(d == -inf for fila in r.distancias for d in fila))
        self.assertTrue(all(n is None for fila in r.siguientes for n in fila))
        with self.assertRaises(ValueError):
            r.consultar(17,10)

    def test_paralelas_cero_origen_destino_igual_y_desconectados(self):
        ady = {0:(Conexion(1,'cara',9), Conexion(1,'cero',0)), 1:(Conexion(2,0,2),), 2:(), 3:()}
        r = ejecutar_warshall_floyd(ady)
        self.assertEqual(r.consultar(0,2)[0], 2)
        self.assertEqual(r.consultar(0,2)[2][0].clave, 'cero')
        self.assertEqual(r.consultar(0,0), (0,(0,),()))
        self.assertEqual(r.consultar(3,0), (inf,(),()))
        self.assertEqual(ejecutar_warshall_floyd({}).distancias, ())
        with self.assertRaises(ValueError): r.consultar(0,99)

    def test_instantaneas_y_recorridos_intermedios_no_son_saltos_directos(self):
        r = ejecutar_warshall_floyd(obtener_adyacencia(cargar_ejemplo_floyd()))
        self.assertEqual(r.pasos[0].distancias[1][6], inf)
        self.assertEqual(r.pasos[-1].distancias[1][6], 6)
        self.assertEqual(r.recorridos[1][6], 'H')
        self.assertEqual(r.consultar('B','G')[1], ('B','D','H','G'))
        # Las comparaciones sin mejora comparten la matriz inmutable.
        indice = next(i for i,p in enumerate(r.pasos) if p.tipo=='comparar' and not p.mejora)
        self.assertIs(r.pasos[indice].distancias, r.pasos[indice-1].distancias)
        self.assertEqual(r.pasos[-1].comparaciones, 8**3)

    def test_negativos_aleatorios_sin_ciclos_por_enumeracion_independiente(self):
        rng=random.Random(17)
        for _ in range(30):
            ady = {i: tuple(Conexion(j,0,rng.randint(-8,9)) for j in range(i+1,6) if rng.random()<0.5) for i in range(6)}
            r=ejecutar_warshall_floyd(ady)
            for origen in ady:
                esperadas={i:inf for i in ady}
                def recorrer(actual,costo):
                    esperadas[actual]=min(esperadas[actual],costo)
                    for c in ady[actual]: recorrer(c.destino,costo+c.peso)
                recorrer(origen,0)
                b=ejecutar_bellman_ford(ady,origen)
                for destino in ady:
                    self.assertEqual(r.consultar(origen,destino)[0],esperadas[destino])
                    self.assertEqual(b.distancias[destino],esperadas[destino])

    def test_validacion_de_pesos_y_destinos(self):
        for peso in (inf, float('nan'), 'x'):
            with self.assertRaises(ValueError): ejecutar_warshall_floyd({0:(Conexion(0,0,peso),)})
        with self.assertRaises(ValueError): ejecutar_warshall_floyd({0:(Conexion(1,0,2),)})
        with self.assertRaisesRegex(ValueError,'rango numérico'):
            ejecutar_warshall_floyd({0:(Conexion(1,0,-1e308),),1:(Conexion(2,0,-1e308),),2:()})


if __name__=='__main__': unittest.main()
