"""Generador automático de capturas paso a paso en orden numérico para cada algoritmo.

Uso:
    python capturar_pasos.py
    python capturar_pasos.py --algoritmo dijkstra
    python capturar_pasos.py --algoritmo a_estrella
    python capturar_pasos.py --algoritmo bellman_ford
    python capturar_pasos.py --algoritmo warshall_floyd
    python capturar_pasos.py --max-pasos 50
"""
import argparse
import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from interfaz.tema import ESTILO
from interfaz.ventana import VentanaGrafo

CARPETA_CAPTURAS = Path("capturas_pasos")


def capturar_algoritmo(ventana, indice_pestana, nombre_id, max_pasos=None, paso_a_paso=True):
    app = QApplication.instance()
    carpeta_algo = CARPETA_CAPTURAS / nombre_id
    carpeta_algo.mkdir(parents=True, exist_ok=True)

    print(f"\n==========================================")
    print(f"Iniciando capturas de: {nombre_id.upper()}")
    print(f"Carpeta destino: {carpeta_algo.resolve()}")
    print(f"==========================================")

    # Cambiar a la pestaña correspondiente
    ventana.pestanas.setCurrentIndex(indice_pestana)
    app.processEvents()

    interfaz = ventana.pestanas.widget(indice_pestana)

    # Disparar búsqueda / cálculo
    if hasattr(interfaz, "buscar"):
        interfaz.buscar()
    elif hasattr(interfaz, "ejecutar"):
        # Floyd-Warshall
        interfaz.ejecutar.click()

    app.processEvents()

    if not hasattr(interfaz, "reproductor") or not interfaz.reproductor.resultado:
        print(f"Advertencia: No se generó resultado para {nombre_id}")
        return []

    resultado = interfaz.reproductor.resultado
    total_pasos = len(resultado.pasos)
    print(f"Total de pasos disponibles: {total_pasos}")

    # Determinar qué índices de pasos capturar
    if nombre_id == "warshall_floyd" and not paso_a_paso:
        # En Floyd-Warshall, los pasos por intermedio k son los más representativos
        indices = list(resultado.finales_iteracion)
        if 0 not in indices:
            indices = [0] + indices
        if total_pasos - 1 not in indices:
            indices.append(total_pasos - 1)
    else:
        indices = list(range(total_pasos))
        if max_pasos and len(indices) > max_pasos:
            # Seleccionar pasos espaciados uniformemente asegurando el inicial y final
            salto = max(1, len(indices) // max_pasos)
            indices = indices[::salto]
            if (total_pasos - 1) not in indices:
                indices.append(total_pasos - 1)

    rutas_imagenes = []
    print(f"Capturando {len(indices)} fotogramas...")

    for num_orden, idx_paso in enumerate(indices, start=1):
        paso = resultado.pasos[idx_paso]
        interfaz.mostrar_paso(idx_paso, paso)
        app.processEvents()

        # Nombre con formato numérico secuencial: 001_paso_000.png
        nombre_archivo = f"{num_orden:04d}_paso_{idx_paso:04d}.png"
        ruta_archivo = carpeta_algo / nombre_archivo
        ventana.grab().save(str(ruta_archivo))
        rutas_imagenes.append(ruta_archivo)

        if num_orden % 20 == 0 or num_orden == len(indices):
            print(f"  Progreso: {num_orden}/{len(indices)} capturas guardadas...")

    print(f"[OK] Finalizadas {len(rutas_imagenes)} capturas de {nombre_id}.")
    return rutas_imagenes


def ejecutar(algoritmos_seleccionados=None, max_pasos=None):
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Capturas de Algoritmos")
    app.setStyle("Fusion")
    app.setStyleSheet(ESTILO)

    ventana = VentanaGrafo()
    ventana.show()
    app.processEvents()

    mapa_pestanas = {
        "dijkstra": 0,
        "bellman_ford": 1,
        "warshall_floyd": 2,
        "a_estrella": 3,
    }

    if not algoritmos_seleccionados:
        algoritmos_seleccionados = ["dijkstra", "bellman_ford", "warshall_floyd", "a_estrella"]

    resultados = {}
    for algo_id in algoritmos_seleccionados:
        if algo_id in mapa_pestanas:
            # Para warshall_floyd, por defecto usamos finales de k si no se fija max_pasos
            paso_a_paso = (algo_id != "warshall_floyd")
            imgs = capturar_algoritmo(
                ventana,
                mapa_pestanas[algo_id],
                algo_id,
                max_pasos=max_pasos,
                paso_a_paso=paso_a_paso,
            )
            resultados[algo_id] = imgs

    app.quit()
    return resultados


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Captura en orden numérico cada paso de los algoritmos.")
    parser.add_argument("--algoritmo", choices=["dijkstra", "bellman_ford", "warshall_floyd", "a_estrella", "todos"],
                        default="todos", help="Algoritmo a capturar (por defecto: todos)")
    parser.add_argument("--max-pasos", type=int, default=None,
                        help="Número máximo de capturas a generar por algoritmo (opcional)")
    args = parser.parse_args()

    algos = None if args.algoritmo == "todos" else [args.algoritmo]
    ejecutar(algos, max_pasos=args.max_pasos)
