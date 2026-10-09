"""Validación de extremos introducidos como texto, independiente de Qt."""

def validar_extremos(grafo, texto_origen, texto_destino):
    def convertir(texto):
        try:
            return int(texto.strip())
        except (ValueError, AttributeError):
            return None

    origen, destino = convertir(texto_origen), convertir(texto_destino)
    falta_origen = origen not in grafo
    falta_destino = destino not in grafo
    if falta_origen and falta_destino:
        raise ValueError('Nodo origen y destino no existen.')
    if falta_origen:
        raise ValueError('Nodo origen no existe.')
    if falta_destino:
        raise ValueError('Nodo destino no existe.')
    return origen, destino
