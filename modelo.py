"""
modelo.py
=========
Nucleo de calculo para la Solemne de Optimizacion (CINF105).
NO inventa datos: todos los parametros provienen del enunciado.

Contiene:
  - Datos del problema (escenario s=1 y escenarios estocasticos)
  - Funciones de evaluacion de una solucion de ruteo (costo + factibilidad)
  - Verificacion de la solucion propuesta por el operador (Pregunta 3)
  - Tiempos de carga y scheduling (Pregunta 2)
  - Metaheuristica Tabu Search para el ruteo (Pregunta 1, resuelta heuristicamente)
  - Fuerza bruta para verificar que Tabu Search alcanza el optimo global
"""

from itertools import permutations, product
import math

# ---------------------------------------------------------------------------
# 1. DATOS DEL ENUNCIADO (escenario s = 1, "Normal")
# ---------------------------------------------------------------------------

ESTACIONES = [1, 2, 3, 4]

# Demanda por estacion: (Regular, Diesel) en litros
DEMANDA = {
    1: {"R": 3000, "D": 2000},
    2: {"R": 4000, "D": 1500},
    3: {"R": 2500, "D": 3000},
    4: {"R": 1000, "D": 2500},
}

# Ventanas de tiempo [a_j, b_j] en minutos desde medianoche
def hm(h, m=0):
    return h * 60 + m

VENTANA = {
    1: (hm(6), hm(10)),
    2: (hm(7), hm(12)),
    3: (hm(8), hm(14)),
    4: (hm(6), hm(11)),
}

# Camiones: capacidades de compartimentos C0 y C1, costo fijo, hora de salida (min)
CAMIONES = {
    "T1": {"C0": 8000, "C1": 7000, "fijo": 500, "salida": hm(5, 0)},
    "T2": {"C0": 6000, "C1": 9000, "fijo": 400, "salida": hm(5, 30)},
}

VELOCIDAD = 60.0          # km/h  -> 1 km = 1 minuto
SERVICIO = 30             # min de servicio por estacion
COSTO_KM = 2             # $ por km
PENAL_SHORTAGE = 10       # $ por litro no entregado
DELTA = 0.30             # estabilidad de carga (diferencia maxima de fill ratios)

# Matriz de distancias (km). Indice 0 = Deposito
DIST = {
    (0, 0): 0,  (0, 1): 20, (0, 2): 35, (0, 3): 15, (0, 4): 40,
    (1, 0): 20, (1, 1): 0,  (1, 2): 10, (1, 3): 25, (1, 4): 30,
    (2, 0): 35, (2, 1): 10, (2, 2): 0,  (2, 3): 20, (2, 4): 15,
    (3, 0): 15, (3, 1): 25, (3, 2): 20, (3, 3): 0,  (3, 4): 30,
    (4, 0): 40, (4, 1): 30, (4, 2): 15, (4, 3): 30, (4, 4): 0,
}

# Parametros de carga en deposito (Pregunta 2)
TASA = {"R": 500, "D": 400}     # L/min
LIMPIEZA = 5                    # min de limpieza al terminar cada compartimento


# ---------------------------------------------------------------------------
# 2. EVALUACION DE UNA SOLUCION DE RUTEO
# ---------------------------------------------------------------------------
# Una "ruta" de un camion es: lista ordenada de estaciones a visitar.
# Una "asignacion" indica que combustible va en C0 y cual en C1.
#
# Representacion de una solucion completa:
#   sol = {
#       "T1": {"ruta": [1,3], "comp": {"C0":"R", "C1":"D"}},
#       "T2": {"ruta": [2,4], "comp": {"C0":"D", "C1":"R"}},
#   }
# Un camion con ruta vacia ([]) NO se usa (no paga costo fijo).

def distancia_ruta(ruta):
    """Distancia total de un viaje Deposito -> ... -> Deposito."""
    if not ruta:
        return 0
    nodos = [0] + ruta + [0]
    return sum(DIST[(nodos[i], nodos[i + 1])] for i in range(len(nodos) - 1))


def cargas_iniciales(camion, ruta, comp):
    """Litros cargados en cada compartimento = demanda total de las estaciones
    de la ruta para el combustible que transporta ese compartimento, sin pasar
    de la capacidad. Devuelve (carga, shortage) por compartimento."""
    cap = CAMIONES[camion]
    cargas, shortage = {}, {}
    for c in ("C0", "C1"):
        fuel = comp[c]
        requerido = sum(DEMANDA[j][fuel] for j in ruta)
        cargado = min(requerido, cap[c])
        cargas[c] = cargado
        shortage[c] = requerido - cargado     # litros no entregados por capacidad
    return cargas, shortage


def perfil_fill_ratios(camion, ruta, comp):
    """Fill ratio de C0 y C1 en cada instante: salida del deposito y despues
    de cada entrega. Devuelve lista de tuplas (etiqueta, fr_C0, fr_C1)."""
    cap = CAMIONES[camion]
    cargas, _ = cargas_iniciales(camion, ruta, comp)
    restante = dict(cargas)
    perfil = [("Salida deposito", restante["C0"] / cap["C0"],
                                   restante["C1"] / cap["C1"])]
    for j in ruta:
        for c in ("C0", "C1"):
            restante[c] = max(0.0, restante[c] - DEMANDA[j][comp[c]])
        perfil.append((f"Tras estacion {j}",
                       restante["C0"] / cap["C0"],
                       restante["C1"] / cap["C1"]))
    return perfil


def estabilidad_ok(camion, ruta, comp):
    """True si |fr_C0 - fr_C1| <= DELTA en todos los instantes."""
    for _, a, b in perfil_fill_ratios(camion, ruta, comp):
        if abs(a - b) > DELTA + 1e-9:
            return False
    return True


def tiempos_llegada(camion, ruta):
    """Hora de llegada (min) a cada estacion. Se permite esperar si se llega
    antes de a_j (interpretacion estandar VRPTW): el servicio inicia en
    max(llegada, a_j). Devuelve lista (estacion, llegada, inicio_servicio)."""
    t = CAMIONES[camion]["salida"]
    pos = 0
    out = []
    for j in ruta:
        t += DIST[(pos, j)]                # viaje (1 km = 1 min a 60 km/h)
        llegada = t
        inicio = max(llegada, VENTANA[j][0])
        out.append((j, llegada, inicio))
        t = inicio + SERVICIO             # espera (si aplica) + servicio
        pos = j
    return out


def ventanas_ok(camion, ruta, estricto=False):
    """Factibilidad de ventanas.
    - estricto=False (estandar VRPTW): basta llegar antes de b_j (se permite
      esperar si se llega antes de a_j).
    - estricto=True: la llegada debe caer dentro de [a_j, b_j]."""
    for j, llegada, _ in tiempos_llegada(camion, ruta):
        a, b = VENTANA[j]
        if llegada > b:
            return False
        if estricto and llegada < a:
            return False
    return True


def evaluar(sol, estricto_ventanas=False):
    """Evalua una solucion completa. Devuelve dict con costo y factibilidad."""
    dist_total = 0
    costo_fijo = 0
    shortage_total = 0
    factible = True
    detalles = {}
    estaciones_cubiertas = []

    for k, info in sol.items():
        ruta, comp = info["ruta"], info["comp"]
        estaciones_cubiertas += ruta
        d = distancia_ruta(ruta)
        dist_total += d
        if ruta:
            costo_fijo += CAMIONES[k]["fijo"]
        _, shortage = cargas_iniciales(k, ruta, comp)
        sc = sum(shortage.values())
        shortage_total += sc
        est_ok = estabilidad_ok(k, ruta, comp) if ruta else True
        ven_ok = ventanas_ok(k, ruta, estricto_ventanas) if ruta else True
        if (not est_ok) or (not ven_ok) or sc > 0:
            factible = False
        detalles[k] = {"dist": d, "estabilidad_ok": est_ok,
                       "ventanas_ok": ven_ok, "shortage": sc}

    # cada estacion debe ser cubierta exactamente una vez
    cobertura_ok = sorted(estaciones_cubiertas) == ESTACIONES
    if not cobertura_ok:
        factible = False

    costo = COSTO_KM * dist_total + costo_fijo + PENAL_SHORTAGE * shortage_total
    return {
        "costo": costo,
        "dist_km": dist_total,
        "costo_distancia": COSTO_KM * dist_total,
        "costo_fijo": costo_fijo,
        "shortage": shortage_total,
        "factible": factible,
        "cobertura_ok": cobertura_ok,
        "detalles": detalles,
    }


# ---------------------------------------------------------------------------
# 3. FUERZA BRUTA (para verificar el optimo global)
# ---------------------------------------------------------------------------

def todas_las_soluciones():
    """Genera todas las soluciones: cada estacion a T1 o T2, todos los ordenes
    de ruta y las 2 asignaciones de combustible por camion."""
    asign_comp = [{"C0": "R", "C1": "D"}, {"C0": "D", "C1": "R"}]
    for mask in product(["T1", "T2"], repeat=len(ESTACIONES)):
        grupos = {"T1": [], "T2": []}
        for est, k in zip(ESTACIONES, mask):
            grupos[k].append(est)
        ordenes = {}
        for k in ("T1", "T2"):
            ordenes[k] = list(permutations(grupos[k])) if grupos[k] else [()]
        for r1 in ordenes["T1"]:
            for r2 in ordenes["T2"]:
                for c1 in asign_comp:
                    for c2 in asign_comp:
                        yield {
                            "T1": {"ruta": list(r1), "comp": c1},
                            "T2": {"ruta": list(r2), "comp": c2},
                        }


def optimo_fuerza_bruta(estricto_ventanas=False):
    mejor, mejor_eval = None, None
    factibles = 0
    for sol in todas_las_soluciones():
        ev = evaluar(sol, estricto_ventanas)
        if ev["factible"]:
            factibles += 1
            if mejor_eval is None or ev["costo"] < mejor_eval["costo"]:
                mejor, mejor_eval = sol, ev
    return mejor, mejor_eval, factibles


# ---------------------------------------------------------------------------
# 4. PREGUNTA 2: TIEMPOS DE CARGA Y SCHEDULING
# ---------------------------------------------------------------------------

# Volumenes fijos del enunciado (Pregunta 2):
#   T1: 5000 L Regular en C0, 5000 L Diesel en C1
#   T2: 4000 L Diesel en C0,  3500 L Regular en C1
OPERACIONES_CARGA = [
    # (id, camion, compartimento, combustible, litros)
    ("T1_C0", "T1", "C0", "R", 5000),
    ("T1_C1", "T1", "C1", "D", 5000),
    ("T2_C0", "T2", "C0", "D", 4000),
    ("T2_C1", "T2", "C1", "R", 3500),
]

def tiempo_carga(litros, fuel):
    """Minutos de carga + 5 min de limpieza."""
    return litros / TASA[fuel] + LIMPIEZA


def calcular_tiempos_carga():
    return {op[0]: tiempo_carga(op[4], op[3]) for op in OPERACIONES_CARGA}


def scheduling_makespan():
    """Programa la carga minimizando el makespan.
    Reglas: dentro de un camion C0 precede a C1; cada bahia (R y D) procesa
    una operacion a la vez. Se construye la programacion optima por listas."""
    dur = calcular_tiempos_carga()
    # Bahias: R -> {T1_C0, T2_C1}; D -> {T1_C1, T2_C0}
    # Precedencia: T1_C1 despues de T1_C0 ; T2_C1 despues de T2_C0
    # Estrategia optima (cuello de botella = bahia Diesel = 17.5+15 = 32.5):
    #   Bahia D: T2_C0 (0->15), luego T1_C1 (15->32.5)
    #   Bahia R: T1_C0 (0->15), luego T2_C1 (15->27)
    inicio = {"T2_C0": 0.0, "T1_C0": 0.0}
    fin = {"T2_C0": dur["T2_C0"], "T1_C0": dur["T1_C0"]}
    # T1_C1 en bahia D: tras T1_C0 (precedencia) y tras T2_C0 (bahia libre)
    inicio["T1_C1"] = max(fin["T1_C0"], fin["T2_C0"])
    fin["T1_C1"] = inicio["T1_C1"] + dur["T1_C1"]
    # T2_C1 en bahia R: tras T2_C0 (precedencia) y tras T1_C0 (bahia libre)
    inicio["T2_C1"] = max(fin["T2_C0"], fin["T1_C0"])
    fin["T2_C1"] = inicio["T2_C1"] + dur["T2_C1"]
    listo = {"T1": fin["T1_C1"], "T2": fin["T2_C1"]}
    makespan = max(fin.values())
    return dur, inicio, fin, listo, makespan


# ---------------------------------------------------------------------------
# 5. PREGUNTA 4: ESCENARIOS ESTOCASTICOS
# ---------------------------------------------------------------------------
# Solo varia la demanda de Est.1, Est.2 (R y D) y Est.3 (Regular).
# Est.3 Diesel y Est.4 se mantienen como el contexto (s=1).
ESCENARIOS = {
    "s1_Normal": {"prob": 0.5,
        1: {"R": 3000, "D": 2000}, 2: {"R": 4000, "D": 1500},
        3: {"R": 2500, "D": 3000}, 4: {"R": 1000, "D": 2500}},
    "s2_Alta":   {"prob": 0.3,
        1: {"R": 4500, "D": 2800}, 2: {"R": 5500, "D": 2000},
        3: {"R": 3500, "D": 3000}, 4: {"R": 1000, "D": 2500}},
    "s3_Baja":   {"prob": 0.2,
        1: {"R": 2000, "D": 1200}, 2: {"R": 3000, "D": 1000},
        3: {"R": 1800, "D": 3000}, 4: {"R": 1000, "D": 2500}},
}

def demanda_total_por_escenario():
    out = {}
    for s, d in ESCENARIOS.items():
        R = sum(d[j]["R"] for j in ESTACIONES)
        D = sum(d[j]["D"] for j in ESTACIONES)
        out[s] = {"prob": d["prob"], "R": R, "D": D, "total": R + D}
    return out
