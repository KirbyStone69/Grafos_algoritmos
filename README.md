# Visualizador de rutas · PyQt6

Aplicación de solo lectura con tema gris oscuro y líneas verdes. Conserva los 30 nodos, 64 aristas, valores y posiciones de `grafo.jpeg`. No permite editar el grafo ni cargar una imagen de fondo.

## Ejecutar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

Selecciona **Pesos positivos**, la pestaña **Dijkstra** y pulsa **Buscar y animar**. El origen predeterminado es **17** y el destino **10**. El resultado es **17 → 2 → 1 → 10**, con costo **13** (5 + 3 + 5).

- La búsqueda se calcula con una implementación propia; NetworkX solo almacena nodos y aristas.
- La animación reproduce los eventos reales: elegir el nodo de menor distancia, examinar cada arista, actualizar o descartar un candidato y reconstruir la ruta.
- Origen y destino se introducen como texto. Se valida la existencia de ambos nodos y se muestra una alerta específica si falta el origen, el destino o ambos. Los campos vacíos o no numéricos también se rechazan.
- La configuración del algoritmo permanece a la derecha. Cada algoritmo tiene su propio formulario en `interfaz/configuraciones.py`.
- La barra inferior del área del grafo despliega, con una transición, las matrices de adyacencia e incidencia. Sustituyen el historial textual y la tabla de distancias.
- Las matrices conservan el registro visual de las aristas consultadas hasta el paso actual. El recorrido activo se resalta en cruz: fila completa del nodo actual y columna completa del vecino (adyacencia) o de la arista (incidencia), incluidas las celdas con cero. La cruz pulsa como una unidad con la animación. Retroceder reconstruye el registro; reiniciar o cambiar parámetros lo limpia.
- La búsqueda se detiene cuando el destino tiene su distancia definitiva.
- Reproducir/pausar, paso anterior/siguiente, reiniciar y velocidad funcionan sobre el mismo registro. Cambiar el grafo o los extremos cancela el registro anterior.
- Zoom con la rueda o botones; arrastrar para desplazar; **Ajustar** encuadra el grafo. **Guardar PNG** exporta el estado visual actual.
- Los nodos sin visitar usan `#397d5a`; los visitados usan `#20452f`. Durante la búsqueda, solo el nodo actual conserva un borde verde neón. Al terminar, todos los nodos de la ruta ganadora se vuelven verde fosforescente, parpadean cinco ciclos rápidos (80 ms por fase, 800 ms en total) y permanecen fosforescentes. Los demás visitados siguen oscuros. La ruta final también se resalta en sus aristas.
- El despliegue mantiene el panel de configuración en su posición. En modo Ajustar, el grafo se reencuadra automáticamente; si has hecho zoom manual, se conserva.

## Convenciones de las matrices

- **Adyacencia (30×30):** número de aristas entre cada par de nodos. Es simétrica; 0 significa que no hay conexión y 2 conserva dos aristas paralelas. El cursor muestra todos sus pesos. No se suman los pesos ni se confunde una arista de peso cero con la ausencia de conexión.
- **Incidencia (30×64):** filas de nodos y una columna por arista, incluidos duplicados. Para este grafo no dirigido, cada columna tiene 1 en sus dos extremos. La cabecera `eN` muestra los extremos, clave y peso al pasar el cursor. Para un bucle se utiliza 2 en su nodo.
- Ambas matrices son de solo lectura. Oscuro identifica nodos visitados, verde las conexiones consultadas y neón la arista activa o la ruta final. Los pesos cambian al seleccionar el grafo original o positivo; la estructura de las matrices se mantiene.

## Organización

```text
main.py                   Entrada de la aplicación
grafo.py                  Nodos, pesos y posiciones transcritos
modelos/
  grafos.py               Carga de las dos variantes y adaptador de adyacencia
  matrices.py             Construcción matemática de las dos matrices
  validacion.py           Validación de nodos introducidos como texto
algoritmos/
  tipos.py                Contrato de conexiones, pasos y resultados
  dijkstra.py             Búsqueda propia, sin Qt ni NetworkX
  registro.py             Catálogo y requisitos de los algoritmos
interfaz/
  ventana.py              Coordinación de la aplicación
  panel.py                Controles compactos de búsqueda
  configuraciones.py      Formulario específico de cada algoritmo
  matrices.py             Panel inferior desplegable
  modelo_matriz.py         Modelos de tablas y registro visual de eventos
  escena.py               Dibujo de aristas y representación de estados
  nodos.py                Elementos gráficos de nodos y etiquetas
  reproductor.py          Tiempo, animación y navegación de pasos
  celebracion.py           Cinco parpadeos de la ruta ganadora
  tema.py                 Paleta y estilos
tests/
  test_dijkstra.py         Verificación matemática de la búsqueda
  test_interfaz.py         Integración de la interfaz sin pantalla
  test_matrices.py         Convenciones de matrices y validación
```

Se aplicó la separación entre datos, presentación e interacción descrita en la [documentación de Qt sobre modelo/vista](https://doc.qt.io/qt-6/model-view-programming.html). La lógica del algoritmo recibe una lista de adyacencia, no objetos gráficos. Los pasos contienen copias de las distancias y predecesores para que la reproducción no cambie estados anteriores.

`grafo.py` conserva `crear_grafo()` y `crear_grafo_positivo()`. La segunda variante es una copia independiente: solo cambia cada peso negativo por su valor absoluto. Las coordenadas `pixel` usan y hacia abajo; `pos` usa `(x, -y)` para coordenadas cartesianas. `nx.MultiGraph` conserva las aristas paralelas, y Dijkstra recuerda la clave exacta de la arista que mejora la distancia.

## Añadir los siguientes algoritmos

Por ahora solo está implementado Dijkstra. Para incorporar cada uno de los otros tres:

1. Crear su módulo en `algoritmos/`, con una función que reciba `(adyacencia, origen, destino)` y devuelva `Resultado` con eventos `Paso`.
2. Añadir una entrada `Algoritmo` en `registro.py`, declarando `acepta_negativos`.
3. Crear su configuración en `interfaz/configuraciones.py` y registrarla en `CONFIGURACIONES`. Cada formulario emite `cambiada` y devuelve sus parámetros validados mediante `parametros(grafo)`. La pestaña se crea desde el registro del algoritmo. El reproductor y el dibujo consumen el mismo contrato de pasos.
4. Añadir pruebas de sus requisitos, caminos y casos sin solución.

Dijkstra requiere pesos no negativos; la interfaz bloquea su ejecución en el grafo original y el algoritmo valida también esta condición. Bellman–Ford admite pesos negativos, pero debe detectar ciclos negativos. El grafo original es **no dirigido**: una arista negativa permite recorrerla de ida y vuelta disminuyendo indefinidamente el costo, por lo que en ese caso no existe un mínimo finito. Una futura implementación deberá informar esa situación; no basta con habilitar el grafo original. Véase la [documentación de Bellman–Ford y ciclos negativos](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.bellman_ford_predecessor_and_distance.html).

## Pruebas

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -v
```

26 pruebas: ruta 17→10, comparación de los 900 pares contra un oráculo independiente Floyd–Warshall, empates, aristas paralelas, pesos cero, bucles, entradas desactualizadas de la cola, destino inalcanzable, origen igual al destino, validación de pesos/nodos, integridad de instantáneas, controles de reproducción, cancelación al cambiar parámetros, colores de nodos visitados/actuales, posiciones, exportación PNG, alertas de extremos inexistentes, despliegue del panel inferior, persistencia del zoom manual, integridad de ambas matrices y registro sincronizado al avanzar/retroceder, cruces completas, cinco ciclos exactos de parpadeo y cancelación de la celebración.

Las pruebas de interfaz se ejecutan sin pantalla. Para usar la aplicación interactiva se necesita una sesión gráfica.

## Interpretaciones de la fotografía

- Las anotaciones manuscritas se leen como −2 (21–11), −7 (24–11), −7 (6–9), −3 (9–10), −6 (3–69), −2 (5–20), −11 (23–16) y −777 (66–13). La última tiene trazos superpuestos: su lectura es provisional.
- El marco tapa parcialmente los nodos de la derecha: se leen como 20 y 25.
- Se conservan los dos valores visibles en 15–0 (8 y 9) como aristas paralelas. La superposición de la línea naranja y el marco dificulta distinguir si el 9 sustituía al 8; esta interpretación es provisional.
- Entre 12 y 16 se conservan las dos aristas visibles, de pesos 16 y 3, mediante `nx.MultiGraph`.
- El peso 20 cercano a la línea 6–15 corresponde a la diagonal larga 7–1; el peso 3 corresponde a 6–15.

Todas las transcripciones y posiciones se pueden editar en `POSICIONES` y `ARISTAS`.

