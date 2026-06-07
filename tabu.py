"""
tabu.py
=======
Metaheuristica TABU SEARCH para el ruteo + asignacion de compartimentos.

Idea general de Tabu Search (Glover, 1986):
  - Se parte de una solucion inicial.
  - En cada iteracion se exploran TODOS los vecinos (soluciones parecidas) y se
    elige el MEJOR, aunque empeore (eso permite escapar de optimos locales).
  - El movimiento recien hecho se guarda en una "lista tabu" para no deshacerlo
    enseguida y evitar ciclar.
  - Criterio de aspiracion: si un movimiento tabu mejora el mejor global, se acepta.
"""

import random
from modelo import (ESTACIONES, evaluar, distancia_ruta)

random.seed(42)

COMBOS_COMP = [{"C0": "R", "C1": "D"}, {"C0": "D", "C1": "R"}]


def costo_penalizado(sol):
    """Costo usado por Tabu Search. Si la solucion es infactible se le suma una
    penalizacion grande para empujar la busqueda hacia la zona factible."""
    ev = evaluar(sol)
    costo = ev["costo"]
    if not ev["factible"]:
        costo += 100000  # penalizacion por infactibilidad (estabilidad/ventanas/cobertura)
    return costo, ev


def solucion_inicial():
    """Asignacion sencilla y valida en cobertura: estaciones 1-2 a T1, 3-4 a T2."""
    return {
        "T1": {"ruta": [1, 2], "comp": {"C0": "R", "C1": "D"}},
        "T2": {"ruta": [3, 4], "comp": {"C0": "R", "C1": "D"}},
    }


def clave(sol):
    """Representacion hashable de una solucion (para la lista tabu)."""
    return (tuple(sol["T1"]["ruta"]), tuple(sorted(sol["T1"]["comp"].items())),
            tuple(sol["T2"]["ruta"]), tuple(sorted(sol["T2"]["comp"].items())))


def vecinos(sol):
    """Genera soluciones vecinas con 4 tipos de movimiento:
       1) mover una estacion de un camion a otro
       2) intercambiar dos estaciones entre camiones
       3) reordenar (2-opt simple) la ruta de un camion
       4) cambiar la asignacion de combustible de un camion
    Devuelve lista de (vecino, etiqueta_movimiento)."""
    out = []
    r = {k: list(sol[k]["ruta"]) for k in ("T1", "T2")}
    c = {k: dict(sol[k]["comp"]) for k in ("T1", "T2")}

    def construir(rT1, rT2, cT1, cT2):
        return {"T1": {"ruta": rT1, "comp": cT1},
                "T2": {"ruta": rT2, "comp": cT2}}

    # 1) mover una estacion de un camion al otro (en todas las posiciones)
    for orig, dest in (("T1", "T2"), ("T2", "T1")):
        for est in r[orig]:
            nuevo_orig = [x for x in r[orig] if x != est]
            for pos in range(len(r[dest]) + 1):
                nuevo_dest = r[dest][:pos] + [est] + r[dest][pos:]
                rr = {orig: nuevo_orig, dest: nuevo_dest}
                out.append((construir(rr["T1"], rr["T2"], dict(c["T1"]), dict(c["T2"])),
                            f"mover {est}:{orig}->{dest}"))

    # 2) intercambiar dos estaciones entre camiones
    for e1 in r["T1"]:
        for e2 in r["T2"]:
            rT1 = [e2 if x == e1 else x for x in r["T1"]]
            rT2 = [e1 if x == e2 else x for x in r["T2"]]
            out.append((construir(rT1, rT2, dict(c["T1"]), dict(c["T2"])),
                        f"swap {e1}<->{e2}"))

    # 3) reordenar la ruta de un camion (invertir segmentos = 2-opt)
    for k in ("T1", "T2"):
        ruta = r[k]
        for i in range(len(ruta)):
            for j in range(i + 1, len(ruta)):
                nueva = ruta[:i] + ruta[i:j + 1][::-1] + ruta[j + 1:]
                rr = {"T1": list(r["T1"]), "T2": list(r["T2"])}
                rr[k] = nueva
                out.append((construir(rr["T1"], rr["T2"], dict(c["T1"]), dict(c["T2"])),
                            f"2opt {k} {i},{j}"))

    # 4) cambiar asignacion de combustible de un camion
    for k in ("T1", "T2"):
        cc = {"T1": dict(c["T1"]), "T2": dict(c["T2"])}
        cc[k] = {"C0": c[k]["C1"], "C1": c[k]["C0"]}
        out.append((construir(list(r["T1"]), list(r["T2"]), cc["T1"], cc["T2"]),
                    f"flip comp {k}"))

    return out


def tabu_search(iteraciones=60, tenencia=7, verbose=True):
    """Ejecuta Tabu Search y devuelve (mejor_sol, mejor_eval, historial)."""
    actual = solucion_inicial()
    costo_actual, ev_actual = costo_penalizado(actual)
    mejor, mejor_costo, mejor_ev = actual, costo_actual, ev_actual

    lista_tabu = {}          # clave -> iteracion en que deja de ser tabu
    historial = [mejor_costo]

    for it in range(1, iteraciones + 1):
        mejor_vecino, mejor_vecino_costo, mejor_vecino_ev, mejor_clave = None, None, None, None
        for vec, _mov in vecinos(actual):
            k = clave(vec)
            cv, ev = costo_penalizado(vec)
            es_tabu = lista_tabu.get(k, 0) > it
            aspira = cv < mejor_costo                  # criterio de aspiracion
            if es_tabu and not aspira:
                continue
            if mejor_vecino_costo is None or cv < mejor_vecino_costo:
                mejor_vecino, mejor_vecino_costo = vec, cv
                mejor_vecino_ev, mejor_clave = ev, k
        if mejor_vecino is None:
            break
        # moverse al mejor vecino admisible
        actual, costo_actual, ev_actual = mejor_vecino, mejor_vecino_costo, mejor_vecino_ev
        lista_tabu[mejor_clave] = it + tenencia
        if costo_actual < mejor_costo:
            mejor, mejor_costo, mejor_ev = actual, costo_actual, ev_actual
        historial.append(mejor_costo)

    return mejor, mejor_ev, historial
