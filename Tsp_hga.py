import random
import numpy as np
import time
import matplotlib.pyplot as plt

# DATOS DEL PROBLEMA
costos = np.array([
    [0.00, 61.82, 18.54, 37.52, 54.08, 1.88, 59.98, 32.82, 69.42, 36.76, 60.26],
    [61.82, 0.00, 50.84, 33.62, 7.50, 59.88, 2.76, 28.84, 7.78, 28.14, 5.80],
    [18.54, 50.84, 0.00, 26.74, 43.38, 18.60, 49.28, 22.00, 58.70, 23.36, 49.30],
    [37.52, 33.62, 26.74, 0.00, 26.16, 35.56, 32.06, 4.80, 41.50, 3.26, 32.08],
    [54.08, 7.50, 43.38, 26.16, 0.00, 52.06, 7.32, 21.38, 15.34, 20.68, 5.92],
    [1.88, 59.88, 18.60, 35.56, 52.06, 0.00, 57.96, 30.86, 67.38, 34.80, 58.30],
    [59.98, 2.76, 49.28, 32.06, 7.32, 57.96, 0.00, 27.28, 10.62, 26.58, 6.76],
    [32.82, 28.84, 22.00, 4.80, 21.38, 30.86, 27.28, 0.00, 36.72, 4.02, 27.30],
    [69.42, 7.78, 58.70, 41.50, 15.34, 67.38, 10.62, 36.72, 0.00, 36.02, 12.14],
    [36.76, 28.14, 23.36, 3.26, 20.68, 34.80, 26.58, 4.02, 36.02, 0.00, 26.60],
    [60.26, 5.80, 49.30, 32.08, 5.92, 58.30, 6.76, 27.30, 12.14, 26.60, 0.00]
])

ventanas = [
    (-np.inf, np.inf),  # 0: New York
    (50.0, 90.0),  # 1: Los Angeles
    (15.0, 25.0),  # 2: Chicago
    (30.0, 55.0),  # 3: Houston
    (15.0, 75.0),  # 4: Phoenix
    (5.0, 35.0),  # 5: Philadelphia
    (150.0, 200.0),  # 6: San Diego
    (25.0, 50.0),  # 7: Dallas
    (65.0, 100.0),  # 8: San Francisco
    (120.0, 150.0),  # 9: Austin
    (30.0, 85.0)  # 10: Las Vegas
]

nombres = ["NY", "LA", "CHI", "HOU", "PHX", "PHI", "SD", "DAL", "SF", "AUS", "LV"]
n_ciudades = 11

# Coordenadas (x, y) aproximadas para el gráfico
coords_ciudades = {
    "NY": (90, 60),
    "LA": (10, 40),
    "CHI": (70, 60),
    "HOU": (60, 20),
    "PHX": (20, 30),
    "PHI": (88, 58),
    "SD": (8, 35),
    "DAL": (58, 30),
    "SF": (5, 55),
    "AUS": (55, 25),
    "LV": (15, 45)
}


# FUNCIÓN DE APTITUD (Según formulación del PDF)
def calcular_aptitud_TSP_TW(ruta, costos, ventanas, lambda_pen=100):
    n = len(ruta)
    T = [0] * n
    for i in range(1, n):
        ciudad_anterior = ruta[i - 1]
        ciudad_actual = ruta[i]
        tiempo_viaje = costos[ciudad_anterior, ciudad_actual]
        tiempo_llegada = T[i - 1] + tiempo_viaje
        inicio_ventana = ventanas[ciudad_actual][0]
        T[i] = max(inicio_ventana, tiempo_llegada)

    tiempo_final = T[-1] + costos[ruta[-1], ruta[0]]
    P = 0
    for i in range(n):
        fin_ventana = ventanas[ruta[i]][1]
        g_i = T[i] - fin_ventana
        if g_i > 0:
            P += g_i ** 2
    VFO = tiempo_final + lambda_pen * P
    return VFO


def calcular_aptitud_TSP_simple(ruta, costos):
    costo = 0
    for i in range(len(ruta)):
        costo += costos[ruta[i], ruta[(i + 1) % len(ruta)]]
    return costo


# OPERADOR: CYCLE CROSSOVER (CX)
def cycle_crossover(padre1, padre2):
    n = len(padre1)
    hijo = [-1] * n
    ciclo_actual = True
    visitados = [False] * n
    idx = 0
    while not all(visitados):
        if hijo[idx] == -1:
            inicio = padre1[idx]
            while True:
                if ciclo_actual:
                    hijo[idx] = padre1[idx]
                else:
                    hijo[idx] = padre2[idx]
                visitados[idx] = True
                valor = padre2[idx]
                idx = padre1.index(valor)
                if valor == inicio:
                    break
            ciclo_actual = not ciclo_actual
        for i in range(n):
            if not visitados[i]:
                idx = i
                break
    return hijo


# ### FUNCIÓN CORREGIDA ###
# HEURÍSTICA: REMOCIÓN DE ABRUPTOS (CORREGIDA)
def remocion_abruptos(ruta, costos, ventanas, usar_ventanas, m=3):
    """
    Implementación CORREGIDA según el PDF.
    Prueba la inserción en TODAS las 'm' ciudades cercanas, no solo en una al azar.
    """
    n = len(ruta)
    mejor_ruta = ruta[:]  # Empezamos con la ruta actual

    # Obtenemos el costo de la ruta actual
    if usar_ventanas:
        mejor_costo = calcular_aptitud_TSP_TW(mejor_ruta, costos, ventanas)
    else:
        mejor_costo = calcular_aptitud_TSP_simple(mejor_ruta, costos)

    # Iteramos sobre cada ciudad en la ruta para intentar moverla
    for pos_ciudad in range(n):
        ciudad_a_mover = mejor_ruta[pos_ciudad]

        # Encontrar las m ciudades más cercanas a 'ciudad_a_mover'
        distancias = costos[ciudad_a_mover].copy()
        indices_ordenados = np.argsort(distancias)
        ciudades_cercanas = [c for c in indices_ordenados if c != ciudad_a_mover][:m]

        # Remover la ciudad de su posición actual
        # Esta ruta_temp se irá actualizando si encontramos mejoras
        ruta_temp = mejor_ruta[:]
        ruta_temp.pop(pos_ciudad)

        pos_original_para_comparar = pos_ciudad  # Guardamos la posición original

        # Probar insertar cerca de CADA una de las 'm' ciudades cercanas
        for ciudad_cercana in ciudades_cercanas:

            # Si la ciudad cercana todavía está en la ruta
            if ciudad_cercana in ruta_temp:
                pos_cercana_en_temp = ruta_temp.index(ciudad_cercana)

                # --- Prueba 1: Insertar ANTES ---
                ruta_prueba_antes = ruta_temp[:pos_cercana_en_temp] + [ciudad_a_mover] + ruta_temp[pos_cercana_en_temp:]

                if usar_ventanas:
                    costo_antes = calcular_aptitud_TSP_TW(ruta_prueba_antes, costos, ventanas)
                else:
                    costo_antes = calcular_aptitud_TSP_simple(ruta_prueba_antes, costos)

                # Si es mejor, actualizamos la 'mejor_ruta'
                if costo_antes < mejor_costo:
                    mejor_costo = costo_antes
                    mejor_ruta = ruta_prueba_antes[:]
                    # Actualizamos ruta_temp para la siguiente prueba
                    ruta_temp = mejor_ruta[:]
                    ruta_temp.pop(ruta_temp.index(ciudad_a_mover))

                # --- Prueba 2: Insertar DESPUÉS ---
                # Volvemos a encontrar la posición por si 'ruta_temp' cambió
                pos_cercana_en_temp = ruta_temp.index(ciudad_cercana)
                ruta_prueba_despues = ruta_temp[:pos_cercana_en_temp + 1] + [ciudad_a_mover] + ruta_temp[
                    pos_cercana_en_temp + 1:]

                if usar_ventanas:
                    costo_despues = calcular_aptitud_TSP_TW(ruta_prueba_despues, costos, ventanas)
                else:
                    costo_despues = calcular_aptitud_TSP_simple(ruta_prueba_despues, costos)

                # Si es mejor, actualizamos la 'mejor_ruta'
                if costo_despues < mejor_costo:
                    mejor_costo = costo_despues
                    mejor_ruta = ruta_prueba_despues[:]
                    # Actualizamos ruta_temp para la siguiente prueba
                    ruta_temp = mejor_ruta[:]
                    ruta_temp.pop(ruta_temp.index(ciudad_a_mover))

    # Devolvemos la mejor ruta encontrada después de todas las iteraciones
    return mejor_ruta


# *** FUNCIÓN PLOT_RUTA ***
def plot_ruta(ruta, nombres, coords, titulo_archivo):
    plt.figure(figsize=(12, 8))

    ruta_coords = [coords[nombres[i]] for i in ruta]
    ruta_x = [c[0] for c in ruta_coords]
    ruta_y = [c[1] for c in ruta_coords]

    ruta_x.append(ruta_x[0])
    ruta_y.append(ruta_y[0])

    for ciudad, (x, y) in coords.items():
        plt.scatter(x, y, c='red', s=100)
        plt.text(x + 0.5, y + 0.5, ciudad, fontsize=12)

    plt.plot(ruta_x, ruta_y, 'b-', label='Ruta del agente')

    plt.scatter(ruta_x[0], ruta_y[0], c='green', s=200, label=f'Inicio ({nombres[ruta[0]]})', zorder=5)

    plt.title(f"Mejor Ruta Encontrada: {titulo_archivo}")
    plt.xlabel("Coordenada X (simulada)")
    plt.ylabel("Coordenada Y (simulada)")
    plt.legend()
    plt.grid(True)

    plt.savefig(titulo_archivo)
    plt.close()
    print(f"\n  Gráfico guardado en: {titulo_archivo}")


# ALGORITMO GENÉTICO HÍBRIDO (EXACTO SEGÚN PDF)
def algoritmo_genetico_hibrido(usar_ventanas=True, tam_poblacion=60, num_generaciones=100,
                               prob_mezcla=0.1, m_abruptos=3):
    print(f"\n{'=' * 60}")
    print(f"  ALGORITMO GENÉTICO HÍBRIDO - TSP{'‑TW' if usar_ventanas else ''}")
    print(f"{'=' * 60}")

    # PASO 1: Generación aleatoria de población inicial
    print("\n▶ PASO 1: Generando población inicial...")
    poblacion = []
    for i in range(tam_poblacion):
        ruta = list(range(n_ciudades))
        random.shuffle(ruta)
        poblacion.append(ruta)

    aptitudes = []
    for ruta in poblacion:
        if usar_ventanas:
            apt = calcular_aptitud_TSP_TW(ruta, costos, ventanas)
        else:
            apt = calcular_aptitud_TSP_simple(ruta, costos)
        aptitudes.append(apt)
    mejor_inicial = min(aptitudes)
    print(f"  Mejor aptitud inicial (antes de heurística): {mejor_inicial:.2f}")

    # PASO 2: Aplicar Remoción de Abruptos a toda la población inicial
    print("\n▶ PASO 2: Aplicando Remoción de Abruptos (CORREGIDA) a población inicial...")
    for i in range(len(poblacion)):
        poblacion[i] = remocion_abruptos(poblacion[i], costos, ventanas, usar_ventanas, m_abruptos)

    aptitudes = []
    for ruta in poblacion:
        if usar_ventanas:
            apt = calcular_aptitud_TSP_TW(ruta, costos, ventanas)
        else:
            apt = calcular_aptitud_TSP_simple(ruta, costos)
        aptitudes.append(apt)
    mejor_despues_paso2 = min(aptitudes)
    print(f"  Mejor aptitud (después de heurística): {mejor_despues_paso2:.2f}")

    mejor_global = poblacion[np.argmin(aptitudes)]  # Iniciar con el mejor de la pob. inicial
    mejor_aptitud_global = mejor_despues_paso2

    # PASO 6: Repetir pasos 3-5 por número de generaciones
    print(f"\n▶ PASO 6: Ejecutando {num_generaciones} generaciones...")

    for gen in range(num_generaciones):
        nueva_poblacion = []
        while len(nueva_poblacion) < tam_poblacion:

            # PASO 3: Selección, cruce y mejora
            idx1, idx2 = random.sample(range(len(poblacion)), 2)
            padre1 = poblacion[idx1]
            padre2 = poblacion[idx2]

            descendiente = cycle_crossover(padre1, padre2)

            # Aplicar Remoción de Abruptos al descendiente
            descendiente = remocion_abruptos(descendiente, costos, ventanas, usar_ventanas, m_abruptos)

            # Re-evaluar después de mejora
            if usar_ventanas:
                apt_desc = calcular_aptitud_TSP_TW(descendiente, costos, ventanas)
                apt_p1 = calcular_aptitud_TSP_TW(padre1, costos, ventanas)
                apt_p2 = calcular_aptitud_TSP_TW(padre2, costos, ventanas)
            else:
                apt_desc = calcular_aptitud_TSP_simple(descendiente, costos)
                apt_p1 = calcular_aptitud_TSP_simple(padre1, costos)
                apt_p2 = calcular_aptitud_TSP_simple(padre2, costos)

            # PASO 4: Ordenar familia y pasar los DOS mejores
            familia = [(padre1, apt_p1), (padre2, apt_p2), (descendiente, apt_desc)]
            familia.sort(key=lambda x: x[1])
            nueva_poblacion.append(familia[0][0])
            if len(nueva_poblacion) < tam_poblacion:
                nueva_poblacion.append(familia[1][0])

        # PASO 5: Generar ruta aleatoria bajo cierta probabilidad
        for i in range(len(nueva_poblacion)):
            if random.random() < prob_mezcla:
                ruta_aleatoria = list(range(n_ciudades))
                random.shuffle(ruta_aleatoria)
                # Aplicamos heurística también a la ruta aleatoria
                ruta_aleatoria = remocion_abruptos(ruta_aleatoria, costos, ventanas, usar_ventanas, m_abruptos)
                nueva_poblacion[i] = ruta_aleatoria

        poblacion = nueva_poblacion[:tam_poblacion]

        # Buscar mejor de la generación
        for ruta in poblacion:
            if usar_ventanas:
                apt = calcular_aptitud_TSP_TW(ruta, costos, ventanas)
            else:
                apt = calcular_aptitud_TSP_simple(ruta, costos)

            if apt < mejor_aptitud_global:
                mejor_aptitud_global = apt
                mejor_global = ruta[:]

        if (gen + 1) % 20 == 0:
            print(f"  Generación {gen + 1:3d}: Mejor = {mejor_aptitud_global:.2f}")

    return mejor_global, mejor_aptitud_global


# FUNCIÓN PRINCIPAL
def main():
    print("\n" + "=" * 60)
    print("  TSP-TW: ALGORITMO GENÉTICO HÍBRIDO (CÓDIGO CORREGIDO)")
    print("=" * 60)

    N_CORRIDAS = 5  # Como pide la práctica

    # --- Experimento 1: CON ventanas de tiempo ---
    print("\n\n🔴 EXPERIMENTO 1: CON VENTANAS DE TIEMPO")
    print("-" * 60)
    resultados_tw = []
    mejor_ruta_tw = None
    mejor_aptitud_tw = float('inf')
    for corrida in range(N_CORRIDAS):
        print(f"\nCorrida {corrida + 1}/{N_CORRIDAS}:")
        mejor, aptitud = algoritmo_genetico_hibrido(usar_ventanas=True)
        resultados_tw.append(aptitud)
        if aptitud < mejor_aptitud_tw:
            mejor_aptitud_tw = aptitud
            mejor_ruta_tw = mejor
        print(f"\n✅ Resultado corrida {corrida + 1}: {aptitud:.2f}")
        print(f"Ruta: {' → '.join([nombres[c] for c in mejor])}")

    resultados_tw = np.array(resultados_tw)
    print(f"\n📊 ESTADÍSTICAS CON VENTANAS:")
    print(f"  Mejor:      {resultados_tw.min():.2f}")
    print(f"  Promedio:   {resultados_tw.mean():.2f}")
    print(f"  Peor:       {resultados_tw.max():.2f}")
    print(f"  Desv. Est:  {resultados_tw.std():.2f}")
    print(f"  Mejor Ruta Global: {' → '.join([nombres[c] for c in mejor_ruta_tw])}")

    # --- Experimento 2: SIN ventanas de tiempo ---
    print("\n\n🟢 EXPERIMENTO 2: SIN VENTANAS DE TIEMPO")
    print("-" * 60)
    resultados_sin = []
    mejor_ruta_sin = None
    mejor_aptitud_sin = float('inf')
    for corrida in range(N_CORRIDAS):
        print(f"\nCorrida {corrida + 1}/{N_CORRIDAS}:")
        mejor, aptitud = algoritmo_genetico_hibrido(usar_ventanas=False)
        resultados_sin.append(aptitud)
        if aptitud < mejor_aptitud_sin:
            mejor_aptitud_sin = aptitud
            mejor_ruta_sin = mejor
        print(f"\n✅ Resultado corrida {corrida + 1}: {aptitud:.2f}")
        print(f"Ruta: {' → '.join([nombres[c] for c in mejor])}")

    resultados_sin = np.array(resultados_sin)
    print(f"\n📊 ESTADÍSTICAS SIN VENTANAS:")
    print(f"  Mejor:      {resultados_sin.min():.2f}")
    print(f"  Promedio:   {resultados_sin.mean():.2f}")
    print(f"  Peor:       {resultados_sin.max():.2f}")
    print(f"  Desv. Est:  {resultados_sin.std():.2f}")
    print(f"  Mejor Ruta Global: {' → '.join([nombres[c] for c in mejor_ruta_sin])}")

    # --- GENERACIÓN DE GRÁFICOS ---
    print("\n\n🖼️  GENERANDO GRÁFICOS DE MEJORES RUTAS...")
    try:
        plot_ruta(mejor_ruta_tw, nombres, coords_ciudades, "ruta_optima_CON_TW_corregida.png")
        plot_ruta(mejor_ruta_sin, nombres, coords_ciudades, "ruta_optima_SIN_TW_corregida.png")
        print("Gráficos corregidos generados con éxito.")
    except Exception as e:
        print(f"Error al generar gráficos: {e}")
        print("Asegúrate de tener matplotlib instalado: pip install matplotlib")

    print("\n" + "=" * 60)
    print("  FIN DE EXPERIMENTOS")
    print("=" * 60)


if __name__ == "__main__":
    main()