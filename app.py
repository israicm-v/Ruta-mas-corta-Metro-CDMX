
"""
RUTA MAS CORTA DEL METRO DE LA CIUDAD DE MEXICO
Archivo: app.py
Autor: Chalico Montoya Israel 
Descripción: Aplicación web para calcular la ruta más corta en el Metro de la Ciudad de México mediante el algoritmo de Dijkstra.
GitHub: https://github.com/israicm-v
Correo electrónico: israelchalico7@gmail.com
Correo auxiliar: israelchalico8@gmail.com
Contacto Directo: 5613416561
"""

from flask import Flask, render_template, request, jsonify
import heapq
from unidecode import unidecode

app = Flask(__name__)

# Variables globales
grafo = {}
lineas = {}
tiempo_transbordo_minutos = 5  # Tiempo de transbordo en minutos
velocidad_caminata_metros_por_minuto = 80  # Velocidad promedio de caminata en metros por minuto
tiempo_transbordo_metros = tiempo_transbordo_minutos * velocidad_caminata_metros_por_minuto

def normalizar(texto):
    return unidecode(texto).strip().title()

def cargar_aristas(filepath):
    with open(filepath, 'r', encoding='UTF-8') as aristasMetro:
        data = aristasMetro.read().strip().split("\n")
    aristas = [x.split(",") for x in data]
    for arista in aristas:
        arista[0] = normalizar(arista[0])
        arista[1] = normalizar(arista[1])
        arista[2] = int(arista[2])
    return aristas

def cargar_vertices(filepath):
    with open(filepath, 'r', encoding='UTF-8') as vertices:
        return [normalizar(v) for v in vertices.read().strip().split("\n")]

def cargar_lineas(filepath):
    lineas = {}
    with open(filepath, 'r', encoding='UTF-8') as f:
        for line in f:
            parts = line.strip().split(',')
            linea = normalizar(parts[0])
            estaciones = [normalizar(e) for e in parts[1:]]
            lineas[linea] = estaciones
    return lineas

def estaciones_transbordo(vertices, lineas):
    estaciones = {vertice: set() for vertice in vertices}
    for linea, estaciones_linea in lineas.items():
        for estacion in estaciones_linea:
            estacion_normalizada = normalizar(estacion)
            if estacion_normalizada in estaciones:
                estaciones[estacion_normalizada].add(linea)
            else:
                print(f"Advertencia: La estación '{estacion}' en la línea '{linea}' no se encuentra en vertices")
    transbordos = {estacion: list(lineas) for estacion, lineas in estaciones.items() if len(lineas) > 1}
    print("Estaciones de transbordo:", transbordos)
    return transbordos

def construir_grafo(vertices, aristas, estaciones_transbordo):
    grafo = {vertice: {} for vertice in vertices}
    for origen, destino, peso in aristas:
        origen_normalizado = normalizar(origen)
        destino_normalizado = normalizar(destino)
        if origen_normalizado in grafo and destino_normalizado in grafo:
            grafo[origen_normalizado].update({destino_normalizado: peso})
            grafo[destino_normalizado].update({origen_normalizado: peso})
        else:
            print(f"Advertencia: {origen} o {destino} no se encuentran en vertices")
   
    # Añadir tiempo de transbordo en metros
    for estacion, lineas in estaciones_transbordo.items():
        print(f"Estación de transbordo: {estacion} con líneas {lineas}")
        for i in range(len(lineas)):
            for j in range(i + 1, len(lineas)):
                transbordo_origen = f"{estacion}_{lineas[i]}"
                transbordo_destino = f"{estacion}_{lineas[j]}"
                if transbordo_origen not in grafo:
                    grafo[transbordo_origen] = {}
                if transbordo_destino not in grafo:
                    grafo[transbordo_destino] = {}
                grafo[transbordo_origen].update({transbordo_destino: tiempo_transbordo_metros})
                grafo[transbordo_destino].update({transbordo_origen: tiempo_transbordo_metros})
                grafo[estacion].update({transbordo_origen: 0})
                grafo[transbordo_origen].update({estacion: 0})
                grafo[transbordo_destino].update({estacion: 0})
                grafo[estacion].update({transbordo_destino: 0})
    return grafo

# Cargar datos
aristas = cargar_aristas('Aristas.txt')
vertices = cargar_vertices('Vertices.txt')
lineas = cargar_lineas('Lineas.txt')
transbordos = estaciones_transbordo(vertices, lineas)
grafo = construir_grafo(vertices, aristas, transbordos)

def Dijkstra_MenorCamino(grafo, partida, llegada):
    PrimerMomento = {}
    DijkstraActual = {}
    NoVisitado = []
    heapq.heappush(NoVisitado, (0, partida))
    DijkstraActual[partida] = (0, None)
   
    while NoVisitado:
        (distancia_actual, nodo_actual) = heapq.heappop(NoVisitado)
       
        if nodo_actual == llegada:
            break
       
        for vecino, peso in grafo[nodo_actual].items():
            distancia = distancia_actual + peso
            if vecino not in DijkstraActual or distancia < DijkstraActual[vecino][0]:
                DijkstraActual[vecino] = (distancia, nodo_actual)
                heapq.heappush(NoVisitado, (distancia, vecino))
   
    if llegada not in DijkstraActual:
        return f"No se encontró un camino desde {partida} hasta {llegada}."
   
    distancia_total, _ = DijkstraActual[llegada]
    camino = []
    nodo = llegada
    while nodo is not None:
        camino.insert(0, nodo)
        nodo = DijkstraActual[nodo][1]
   
    respuesta1 = f"La menor distancia es: {distancia_total} metros"
    respuesta2 = f"El mejor camino es: {' > '.join(camino)}"
    return f"{respuesta1}\n{respuesta2}"

@app.route('/')
def index():
    return render_template('index.html', lineas=lineas)

@app.route('/get_estaciones', methods=['POST'])
def get_estaciones():
    linea_seleccionada = normalizar(request.form['linea'])
    estaciones = lineas.get(linea_seleccionada, [])
    return jsonify(estaciones)

@app.route('/calcular_ruta', methods=['POST'])
def calcular_ruta():
    origen = normalizar(request.form['origen'])
    destino = normalizar(request.form['destino'])
    resultado = Dijkstra_MenorCamino(grafo, origen, destino)
    return resultado

if __name__ == "__main__":
    app.run(port=8080, debug=True)
