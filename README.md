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
- La configuración de Dijkstra permanece a la derecha de su propia pestaña. Su formulario está en `interfaz/algoritmos/dijkstra/configuracion.py`. Los futuros algoritmos tendrán interfaces completas independientes.
- La barra inferior de la interfaz de Dijkstra despliega, con una transición, sus matrices de adyacencia e incidencia. Sustituyen el historial textual y la tabla de distancias.
- Las matrices conservan el registro visual de las aristas consultadas hasta el paso actual. El recorrido activo se resalta en cruz: fila completa del nodo actual y columna completa del vecino (adyacencia) o de la arista (incidencia), incluidas las celdas con cero. La cruz pulsa como una unidad con la animación. Retroceder reconstruye el registro; reiniciar o cambiar parámetros lo limpia.
- La búsqueda se detiene cuando el destino tiene su distancia definitiva.
- Reproducir/pausar, paso anterior/siguiente, reiniciar y velocidad funcionan sobre el mismo registro. Cambiar el grafo o los extremos cancela el registro anterior.
- Zoom con la rueda o botones; arrastrar para desplazar; **Ajustar** encuadra el grafo. **Guardar PNG** exporta el estado visual actual.
- Los nodos sin visitar usan `#397d5a`; los visitados usan `#20452f`. Durante la búsqueda, solo el nodo actual conserva un borde verde neón. Al terminar, todos los nodos de la ruta ganadora se vuelven verde fosforescente, parpadean cinco ciclos rápidos (80 ms por fase, 800 ms en total) y permanecen fosforescentes. Los demás visitados siguen oscuros. La ruta final también se resalta en sus aristas.
- El despliegue mantiene el panel de configuración en su posición. En modo Ajustar, el grafo se reencuadra automáticamente; si has hecho zoom manual, se conserva.

## Bellman–Ford · interfaz del ejemplo PDF

La pestaña **Bellman–Ford** utiliza una interfaz independiente basada en [Bellman-Ford__Ejemplo.pdf](Bellman-Ford__Ejemplo.pdf), especialmente sus páginas de relajación y solución. Al abrirla se selecciona automáticamente el grafo original con negativos. Su ejecución queda deshabilitada en la variante positiva.

Tiene los cuatro apartados del documento:

1. Grafo con sus pesos, arco actual resaltado y distancia provisional junto a cada nodo.
2. **Lista de arcos** como referencia: una entrada por sentido y por arista paralela (128 para el grafo original). El clic en un arco muestra su paso dentro de la pasada actual.
3. **Vectores V, d y Π**: identificadores, distancias y predecesores, sincronizados con cada relajación.
4. **Paso / Pregunta / Respuesta / Proceso**: comparación numérica, decisión y actualización, seguida de la verificación final.

El origen predeterminado es **17**. El destino es opcional; vacío calcula desde el origen a todos los nodos, como el PDF. Los campos tienen validación de existencia. Los controles permiten reproducir/pausar, ir al arco anterior/siguiente, reiniciar, saltar a la siguiente pasada, entrar en verificación y mostrar directamente el resultado. La reproducción rápida es el modo predeterminado y ofrece tres opciones:

- **Paso a paso:** reproduce cada evento individualmente y permite revisar cada relajación.
- **Rápido · por bloques:** actualiza la pantalla cada 40 ms, avanzando entre 16 y 88 eventos según la velocidad (64 por defecto). Mantiene las 3.872 instantáneas, pero dibuja una muestra de ellas para terminar la reproducción en pocos segundos.
- **Debug · resultado directo:** calcula todas las pasadas y presenta la verificación final de inmediato. El botón **Debug: verificar ahora** activa este modo directamente.

La barra de progreso muestra el evento actual y **Ir al evento** permite inspeccionar cualquier instantánea conservada. Cambiar el modo pausa la reproducción; elegir debug muestra el resultado. El tiempo de cálculo medido se muestra en la interfaz. En una prueba local, cálculo y presentación debug tardaron aproximadamente 81 ms; el tiempo depende del equipo. El ciclo final permanece resaltado sin partículas en movimiento.

El algoritmo es una implementación propia en `algoritmos/bellman_ford.py`, sin funciones de búsqueda de NetworkX. Conserva instantáneas de cada arco, hace hasta |V|−1 pasadas y verifica si siguen existiendo relajaciones posibles. El PDF utiliza un grafo **dirigido** de cinco nodos; aquí se conserva el grafo original **no dirigido** y por eso se consideran ambos sentidos de cada conexión. No se cambian signos ni se inventan direcciones para obtener una solución finita.

Con el origen 17, el grafo original contiene un ciclo negativo alcanzable **16 → 23 → 16**, de peso **−22**. Afecta a los 30 nodos: el resultado muestra **NO EXISTE MÍNIMO FINITO**, distancias **−∞** y el ciclo resaltado con trazo discontinuo. Los valores durante las pasadas son provisionales. No se presenta una ruta ganadora en este caso.

La prueba del grafo dirigido del PDF reproduce exactamente su solución desde z: **d[u]=2, d[v]=4, d[x]=7, d[y]=−2, d[z]=0** y los predecesores correspondientes. La interfaz del proyecto utiliza los nodos numéricos del grafo original.

Correcciones de Bellman–Ford: el costo del origen se informa como −∞ cuando está afectado, incluso en la consulta a todos los nodos; Π se limpia para los nodos sin mínimo finito; si un ciclo está en otra rama, un destino no afectado conserva su costo y ruta válidos. Los pesos no numéricos y las sumas que desbordan el rango flotante se notifican con un error controlado. El testigo del ciclo se conserva separado de los predecesores de caminos mínimos.

## Floyd–Warshall · interfaz de los documentos XLSX/PDF

La tercera pestaña tiene su propia interfaz basada en `warshall_floyd.xlsx` y sus PDF de Hoja1 y Hoja2: **matriz de distancias D** y **matriz de recorridos R**, actualizadas por vértice intermedio k. Usa lógica propia, sin funciones de caminos mínimos de NetworkX.

- **Datos:** grafo del proyecto (positivo por defecto) o ejemplo A–H, cargado desde la matriz inicial del XLSX con la biblioteca estándar de Python.
- **Por intermedio k:** muestra las matrices al terminar cada iteración. **Paso a paso i,j,k:** inspecciona cada comparación. **Debug:** muestra el resultado directamente.
- La fila y columna del intermedio se resaltan, junto con los operandos D[i,k], D[k,j] y el resultado D[i,j]. Se puede avanzar, retroceder o saltar a cualquier evento.
- Origen y destino son consultas sobre las matrices finales: no recalculan todos los pares. También se puede hacer clic en una celda para consultar ese par. La ruta se resalta y parpadea cinco veces.
- R guarda el **intermedio** como en la hoja; una matriz separada de siguientes saltos reconstruye la ruta real. Un intermedio no se interpreta como una conexión directa.
- Diagonal 0 para el camino vacío; ∞ para pares sin conexión; −∞ para pares afectados por ciclos negativos. Para estos últimos se limpia el recorrido y no se presenta una ruta ganadora.

El ejemplo calcula **A → D → H, costo 8**. El grafo positivo calcula **17 → 2 → 1 → 10, costo 13**. El grafo original negativo produce 900 pares sin mínimo finito.

Se usan las conexiones iniciales del XLSX, no sus iteraciones anotadas: en Hoja1 aparece C→A=0 tras k=A cuando debe ser ∞; Hoja2 mantiene B→G=14 mientras G→B=6. La implementación calcula **6 en ambos sentidos** y respeta la simetría del ejemplo. Las celdas diagonales `null` se interpretan como 0; las conexiones ausentes siguen siendo ∞.

Las instantáneas de Floyd–Warshall comparten filas inmutables que no cambian. Así se conservan los 27.000 cálculos i,j,k del grafo de 30 nodos sin copiar dos matrices completas en cada comparación. Véase la [referencia de Floyd–Warshall](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.dense.floyd_warshall.html).

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
  ejemplo_floyd.py        Lectura de la matriz inicial A–H del XLSX
algoritmos/
  tipos.py                Contrato de conexiones, pasos y resultados
  dijkstra.py             Búsqueda propia, sin Qt ni NetworkX
  bellman_ford.py         Relajación propia, verificación y ciclos negativos
  warshall_floyd.py       Todos los pares, distancias, intermedios y rutas
  registro.py             Catálogo y requisitos de los algoritmos
interfaz/
  ventana.py              Contenedor: selector de grafo y pestañas
  base.py                 Contrato mínimo de una interfaz independiente
  registro.py             Relación algoritmo → interfaz completa
  algoritmos/dijkstra/
    vista.py              Coordinación exclusiva de Dijkstra
    configuracion.py      Parámetros y validación de Dijkstra
    panel.py              Controles de reproducción de Dijkstra
    matrices.py           Panel inferior de matrices de Dijkstra
    modelo_matriz.py      Modelos y recorrido en cruz de Dijkstra
  algoritmos/bellman_ford/
    vista.py              Interfaz propia inspirada en el PDF
    configuracion.py      Origen y destino opcional
    arcos.py              Lista de referencia de arcos
    vectores.py           Vectores V, d y Π
    relajacion.py         Paso, pregunta, respuesta y proceso
    escena.py             Grafo con distancias y ciclo resaltado
    reproductor.py        Reproducción rápida por bloques
  algoritmos/warshall_floyd/
    vista.py              Configuración y visualización de las dos matrices
    modelo.py             Tablas de distancias y recorridos
    reproductor.py        Reproducción por intermedio o por comparación
  escena.py               Dibujo del grafo, reutilizable si se desea
  nodos.py                Elementos gráficos de nodos y etiquetas
  reproductor.py          Reproducción de pasos, reutilizable si se desea
  celebracion.py          Cinco parpadeos de la ruta ganadora
  tema.py                 Paleta y estilos
tests/
  test_dijkstra.py        Verificación matemática de la búsqueda
  test_bellman_ford.py    Solución del PDF y ciclos negativos
  test_bellman_interfaz.py Interfaz y navegación de Bellman–Ford
  test_warshall_floyd.py  Matrices documentales, rutas y ciclos negativos
  test_floyd_interfaz.py  Controles y consultas de Floyd–Warshall
  test_interfaz.py        Interfaz de Dijkstra sin pantalla
  test_interfaces.py      Independencia de las interfaces por algoritmo
  test_matrices.py        Convenciones de matrices y validación
```

Se aplicó la separación entre datos, presentación e interacción descrita en la [documentación de Qt sobre modelo/vista](https://doc.qt.io/qt-6/model-view-programming.html). La lógica del algoritmo recibe una lista de adyacencia, no objetos gráficos. Los pasos contienen copias de las distancias y predecesores para que la reproducción no cambie estados anteriores.

`grafo.py` conserva `crear_grafo()` y `crear_grafo_positivo()`. La segunda variante es una copia independiente: solo cambia cada peso negativo por su valor absoluto. Las coordenadas `pixel` usan y hacia abajo; `pos` usa `(x, -y)` para coordenadas cartesianas. `nx.MultiGraph` conserva las aristas paralelas, y Dijkstra recuerda la clave exacta de la arista que mejora la distancia.

## Añadir los siguientes algoritmos

Están implementados Dijkstra, Bellman–Ford y Floyd–Warshall. Para incorporar el cuarto algoritmo:

1. Crear su módulo en `algoritmos/`, separado de Qt y NetworkX. Puede definir sus propios parámetros, resultados y eventos. Dijkstra y Bellman–Ford comparten un contrato; Floyd–Warshall tiene uno propio para matrices de todos los pares.
2. Añadir una entrada `Algoritmo` en `registro.py`, declarando `acepta_negativos`.
3. Crear una interfaz completa en `interfaz/algoritmos/<nombre>/`, derivada de `InterfazAlgoritmo`. Su constructor recibe `(grafo, algoritmo, parent=None)` y debe implementar `cargar_grafo(grafo)` y `detener()`. Registrar su clase en `INTERFACES`, en `interfaz/registro.py`. Cada algoritmo decide sus formularios, tablas, matrices y animaciones; no hereda el panel ni las matrices de Dijkstra. Los componentes gráficos comunes son opcionales. La ventana general solo crea pestañas, entrega el grafo y detiene la interfaz al cambiar de pestaña.
4. Añadir pruebas de sus requisitos, caminos y casos sin solución.

Dijkstra requiere pesos no negativos; la interfaz bloquea su ejecución en el grafo original y el algoritmo valida también esta condición. Bellman–Ford admite pesos negativos, pero debe detectar ciclos negativos. El grafo original es **no dirigido**: una arista negativa permite recorrerla de ida y vuelta disminuyendo indefinidamente el costo, por lo que en ese caso no existe un mínimo finito. La implementación de Bellman–Ford detecta esa situación y muestra el ciclo y sus nodos afectados. Véase la [documentación de Bellman–Ford y ciclos negativos](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.weighted.bellman_ford_predecessor_and_distance.html).

## Pruebas

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -v
```

59 pruebas: ruta 17→10, comparación de los 900 pares contra un oráculo independiente Floyd–Warshall, empates, aristas paralelas, pesos cero, bucles, entradas desactualizadas de la cola, destino inalcanzable, origen igual al destino, validación de pesos/nodos, integridad de instantáneas, controles de reproducción, cancelación al cambiar parámetros, colores de nodos visitados/actuales, posiciones, exportación PNG, alertas de extremos inexistentes, despliegue del panel inferior, persistencia del zoom manual, integridad de ambas matrices y registro sincronizado al avanzar/retroceder, cruces completas, cinco ciclos exactos de parpadeo y cancelación de la celebración e independencia frente a una segunda interfaz de prueba con controles distintos y sin matrices, solución exacta del PDF, casos con ciclos negativos alcanzables/no alcanzables, destinos no afectados, vectores V/d/Π, lista de arcos, saltos de pasada y verificación, debug inmediato, reproducción rápida completa en segundos, inspección de la traza y cambio de modos. Bellman–Ford también se compara en los 900 pares del grafo positivo contra un oráculo independiente. Floyd–Warshall se contrasta con las 64 distancias calculadas del ejemplo A–H, los 900 pares y rutas de Dijkstra, el PDF de Bellman–Ford, grafos dirigidos aleatorios sin ciclos mediante enumeración independiente, ciclos negativos que afectan solo algunos pares y controles de su nueva interfaz. Se verifican además las regresiones corregidas de Bellman–Ford.

Las pruebas de interfaz se ejecutan sin pantalla. Para usar la aplicación interactiva se necesita una sesión gráfica.

## Interpretaciones de la fotografía

- Las anotaciones manuscritas se leen como −2 (21–11), −7 (24–11), −7 (6–9), −3 (9–10), −6 (3–69), −2 (5–20), −11 (23–16) y −777 (66–13). La última tiene trazos superpuestos: su lectura es provisional.
- El marco tapa parcialmente los nodos de la derecha: se leen como 20 y 25.
- Se conservan los dos valores visibles en 15–0 (8 y 9) como aristas paralelas. La superposición de la línea naranja y el marco dificulta distinguir si el 9 sustituía al 8; esta interpretación es provisional.
- Entre 12 y 16 se conservan las dos aristas visibles, de pesos 16 y 3, mediante `nx.MultiGraph`.
- El peso 20 cercano a la línea 6–15 corresponde a la diagonal larga 7–1; el peso 3 corresponde a 6–15.

Todas las transcripciones y posiciones se pueden editar en `POSICIONES` y `ARISTAS`.


## Contributors

- [KirbyStone69](https://github.com/KirbyStone69): autor del proyecto y responsable del repositorio.
- **OpenAI Codex**: asistencia en implementación, estructura de interfaces y pruebas.

Este crédito es explícito en la documentación y en el mensaje del commit (`Assisted-by: OpenAI Codex`). La lista automática de Contributors de GitHub vincula autores y coautores a cuentas por su correo; no depende de quién ejecuta el push. Un crédito textual a Codex no garantiza una cuenta en esa lista. Véanse [Contributors de GitHub](https://docs.github.com/en/repositories/viewing-activity-and-data-for-your-repository/viewing-a-projects-contributors) y [commits con coautores](https://docs.github.com/en/pull-requests/how-tos/commit-changes/creating-a-commit-with-multiple-authors).
