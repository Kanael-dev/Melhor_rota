from geopy.distance import geodesic
import pandas as pd
import random
import math
import openpyxl

def calcular_distancia(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

def encontrar_locais_proximos(coord_referencia, lista_coords, distancia_maxima):
    locais_proximos = []
    for coord in lista_coords:
        distancia = calcular_distancia(coord_referencia, coord)
        if distancia <= distancia_maxima:
            locais_proximos.append(coord)
    return locais_proximos

def nearest_neighbor_algorithm(coord_referencia, lista_coords, distancia_maxima_km):
    locais_proximos = encontrar_locais_proximos(coord_referencia, lista_coords, distancia_maxima_km)
    locais_proximos.insert(0, coord_referencia)

    num_locais = len(locais_proximos)
    visitados = [False] * num_locais
    rota = []

    # Iniciar a rota com a coordenada de referência
    rota.append(coord_referencia)
    visitados[0] = True

    for _ in range(num_locais - 1):
        pos_atual = rota[-1]
        menor_distancia = float("inf")
        proximo_local = None

        for i, coord in enumerate(locais_proximos):
            if not visitados[i]:
                distancia = calcular_distancia(pos_atual, coord)
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    proximo_local = coord

        if proximo_local is not None:
            rota.append(proximo_local)
            visitados[locais_proximos.index(proximo_local)] = True

    return rota

def simulated_annealing(dist_matrix, rota_inicial, temperatura_inicial, taxa_resfriamento, iteracoes_por_temp):
    rota_atual = rota_inicial
    melhor_rota = rota_inicial
    distancia_atual = calcular_distancia_total(dist_matrix, rota_atual)
    melhor_distancia = distancia_atual

    for _ in range(iteracoes_por_temp):
        temperatura = temperatura_inicial
        while temperatura > 1 and len(rota_atual) > 2:  # Adicione a verificação aqui
            i, j = sorted(random.sample(range(1, len(rota_atual) - 1), 2))
            nova_rota = rota_atual[:i] + rota_atual[j:j+1] + rota_atual[i+1:j] + rota_atual[i:i+1] + rota_atual[j+1:]
            nova_distancia = calcular_distancia_total(dist_matrix, nova_rota)

            if nova_distancia < distancia_atual or random.uniform(0, 1) < math.exp((distancia_atual - nova_distancia) / temperatura):
                rota_atual = nova_rota
                distancia_atual = nova_distancia

            if nova_distancia < melhor_distancia:
                melhor_rota = nova_rota
                melhor_distancia = nova_distancia

            temperatura *= taxa_resfriamento

    return melhor_rota


def calcular_distancia_total(dist_matrix, rota):
    distancia_total = 0
    for i in range(len(rota) - 1):
        origem = rota[i]
        destino = rota[i + 1]
        origem_index = dist_matrix[0].index(origem)
        destino_index = dist_matrix[0].index(destino)
        distancia_total += dist_matrix[origem_index][destino_index]
    return distancia_total

def main():
    latitude_referencia = float(input("Digite a Latitude inicial: ").replace(",", "."))
    longitude_referencia = float(input("Digite a Longitude inicial: ").replace(",", "."))
    coord_referencia = (latitude_referencia, longitude_referencia)

    dados = pd.read_excel(r"C:\Users\kka\PycharmProjects\coordenadas\teste.xlsx")

    lista_coords = list(zip(dados["Latitude"], dados["Longitude"]))

    distancia_maxima_km = 3

    rota_inicial = nearest_neighbor_algorithm(coord_referencia, lista_coords, distancia_maxima_km)

    num_locais = len(rota_inicial)
    dist_matrix = [[0] * num_locais for _ in range(num_locais)]
    for i in range(num_locais):
        for j in range(num_locais):
            dist_matrix[i][j] = calcular_distancia(rota_inicial[i], rota_inicial[j])

    temperatura_inicial = 1000
    taxa_resfriamento = 0.99
    iteracoes_por_temp = 1000
    rota_otima = simulated_annealing(dist_matrix, rota_inicial, temperatura_inicial, taxa_resfriamento, iteracoes_por_temp)

    print("Localizações próximas:")
    for lat, lon in rota_inicial:
        print(f"Latitude: {lat}, Longitude: {lon}")

    print("\nMelhor rota:")
    for lat, lon in rota_otima:
        print(f"Latitude: {lat}, Longitude: {lon}")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Latitude", "Longitude"])
    for lat, lon in rota_otima:
        ws.append([lat, lon])
    wb.save(r"C:\Users\kka\PycharmProjects\coordenadas\melhor_rota.xlsx")

if __name__ == "__main__":
    main()
