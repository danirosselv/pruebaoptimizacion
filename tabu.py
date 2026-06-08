"""
tabu.py
=======
Metaheuristica Tabu Search para el ruteo y la asignacion de compartimentos.
"""

import random

from modelo import ESTACIONES, evaluar

COMBOS_COMP = [{"C0": "R", "C1": "D"}, {"C0": "D", "C1": "R"}]
PENALIZACION_INF_DEFECTO = 100000


def costo_penalizado(sol, penalizacion_inf=PENALIZACION_INF_DEFECTO):
    """Costo usado por Tabu Search.

    Las soluciones infactibles reciben una penalizacion alta para orientar la
    busqueda hacia la zona factible sin descartar por completo esos estados.
    """
    ev = evaluar(sol)
    costo = ev["costo"]
    if not ev["factible"]:
        costo += penalizacion_inf
    return costo, ev


def solucion_inicial():
    """Solucion base reproducible usada en el primer arranque."""
    return {
        "T1": {"ruta": [1, 2], "comp": {"C0": "R", "C1": "D"}},
        "T2": {"ruta": [3, 4], "comp": {"C0": "R", "C1": "D"}},
    }


def solucion_aleatoria(rng):
    """Construye una solucion de cobertura completa para los reinicios."""
    estaciones = list(ESTACIONES)
    rng.shuffle(estaciones)
    corte = rng.randint(0, len(estaciones))
    ruta_t1 = estaciones[:corte]
    ruta_t2 = estaciones[corte:]
    comp_t1 = dict(rng.choice(COMBOS_COMP))
    comp_t2 = dict(rng.choice(COMBOS_COMP))
    return {
        "T1": {"ruta": ruta_t1, "comp": comp_t1},
        "T2": {"ruta": ruta_t2, "comp": comp_t2},
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


def tabu_search(iteraciones=60, tenencia=7, reinicios=0, semilla=42,
                penalizacion_inf=PENALIZACION_INF_DEFECTO, return_meta=False):
    """Ejecuta Tabu Search con reinicios reproducibles.

    `reinicios` indica la cantidad de arranques adicionales despues del inicial.
    """
    rng = random.Random(semilla)
    historial = []
    meta_reinicios = []
    mejor_global = None
    mejor_costo_global = None
    mejor_eval_global = None

    total_arranques = reinicios + 1
    for reinicio in range(total_arranques):
        actual = solucion_inicial() if reinicio == 0 else solucion_aleatoria(rng)
        costo_actual, ev_actual = costo_penalizado(actual, penalizacion_inf)
        costo_inicial_real = ev_actual["costo"]
        factible_inicial = ev_actual["factible"]
        mejor_local = actual
        mejor_costo_local = costo_actual
        mejor_eval_local = ev_actual
        lista_tabu = {}

        if mejor_costo_global is None or costo_actual < mejor_costo_global:
            mejor_global = actual
            mejor_costo_global = costo_actual
            mejor_eval_global = ev_actual
        historial.append(mejor_costo_global)

        for it in range(1, iteraciones + 1):
            mejor_vecino = None
            mejor_vecino_costo = None
            mejor_vecino_ev = None
            mejor_clave = None

            for vec, _mov in vecinos(actual):
                clave_vecino = clave(vec)
                costo_vecino, ev_vecino = costo_penalizado(vec, penalizacion_inf)
                es_tabu = lista_tabu.get(clave_vecino, 0) > it
                aspira = mejor_costo_global is None or costo_vecino < mejor_costo_global
                if es_tabu and not aspira:
                    continue
                if mejor_vecino_costo is None or costo_vecino < mejor_vecino_costo:
                    mejor_vecino = vec
                    mejor_vecino_costo = costo_vecino
                    mejor_vecino_ev = ev_vecino
                    mejor_clave = clave_vecino

            if mejor_vecino is None:
                break

            actual = mejor_vecino
            costo_actual = mejor_vecino_costo
            ev_actual = mejor_vecino_ev
            lista_tabu[mejor_clave] = it + tenencia

            if costo_actual < mejor_costo_local:
                mejor_local = actual
                mejor_costo_local = costo_actual
                mejor_eval_local = ev_actual
            if mejor_costo_global is None or costo_actual < mejor_costo_global:
                mejor_global = actual
                mejor_costo_global = costo_actual
                mejor_eval_global = ev_actual

            historial.append(mejor_costo_global)

        meta_reinicios.append({
            "reinicio": reinicio,
            "costo_inicial_real": costo_inicial_real,
            "factible_inicial": factible_inicial,
            "mejor_costo_penalizado": mejor_costo_local,
            "mejor_costo_real": mejor_eval_local["costo"],
            "factible": mejor_eval_local["factible"],
        })

    if return_meta:
        meta = {
            "iteraciones": iteraciones,
            "reinicios": reinicios,
            "tenencia": tenencia,
            "semilla": semilla,
            "penalizacion_inf": penalizacion_inf,
            "arranques": meta_reinicios,
        }
        return mejor_global, mejor_eval_global, historial, meta

    return mejor_global, mejor_eval_global, historial
