# -*- coding: utf-8 -*-
from modelo import *
from tabu import tabu_search, costo_penalizado

print("="*70)
print("PREGUNTA 3 - VERIFICACION DE LA SOLUCION DEL OPERADOR")
print("="*70)

# Solucion propuesta por el operador
op = {
    "T1": {"ruta": [1, 3], "comp": {"C0": "R", "C1": "D"}},
    "T2": {"ruta": [2, 4], "comp": {"C0": "D", "C1": "R"}},
}

print("\n--- (a1) Capacidad de compartimentos ---")
for k in ("T1", "T2"):
    cargas, short = cargas_iniciales(k, op[k]["ruta"], op[k]["comp"])
    cap = CAMIONES[k]
    for c in ("C0", "C1"):
        fuel = op[k]["comp"][c]
        req = sum(DEMANDA[j][fuel] for j in op[k]["ruta"])
        print(f"{k} {c}={fuel}: requiere {req} L, cap {cap[c]} L -> "
              f"{'OK' if req<=cap[c] else 'EXCEDE'} (fill {req/cap[c]*100:.1f}%)")

print("\n--- (a2) Estabilidad Delta=0.30 (cargando para cubrir demanda) ---")
for k in ("T1", "T2"):
    print(f"{k} ruta {op[k]['ruta']} comp {op[k]['comp']}")
    for etq, a, b in perfil_fill_ratios(k, op[k]["ruta"], op[k]["comp"]):
        flag = "OK" if abs(a-b) <= DELTA+1e-9 else ">>> VIOLA"
        print(f"   {etq:18s} fr_C0={a*100:5.1f}%  fr_C1={b*100:5.1f}%  |dif|={abs(a-b)*100:4.1f}%  {flag}")

print("\n--- (a2b) T2 reordenado D->4->2->D (posible correccion) ---")
for etq, a, b in perfil_fill_ratios("T2", [4, 2], op["T2"]["comp"]):
    flag = "OK" if abs(a-b) <= DELTA+1e-9 else ">>> VIOLA"
    print(f"   {etq:18s} fr_C0={a*100:5.1f}%  fr_C1={b*100:5.1f}%  |dif|={abs(a-b)*100:4.1f}%  {flag}")

print("\n--- (a3) Ventanas de tiempo ---")
for k in ("T1", "T2"):
    print(f"{k} sale {CAMIONES[k]['salida']//60:02d}:{CAMIONES[k]['salida']%60:02d}")
    for j, lleg, ini in tiempos_llegada(k, op[k]["ruta"]):
        a, b = VENTANA[j]
        dentro = a <= lleg <= b
        print(f"   Est {j}: llega {lleg//60:02d}:{int(lleg%60):02d}  ventana "
              f"[{a//60:02d}:{a%60:02d}-{b//60:02d}:{b%60:02d}]  "
              f"{'DENTRO' if dentro else ('TARDE' if lleg>b else 'ANTES (espera)')}")

print("\n--- (b) Verificacion del costo declarado ---")
ev_op = evaluar(op)
print(f"Distancia T1 {op['T1']['ruta']}: {distancia_ruta(op['T1']['ruta'])} km")
print(f"Distancia T2 {op['T2']['ruta']}: {distancia_ruta(op['T2']['ruta'])} km")
print(f"Distancia total: {ev_op['dist_km']} km -> costo distancia = ${ev_op['costo_distancia']}")
print(f"Operador declaro: $260  =>  {'CORRECTO' if ev_op['costo_distancia']==260 else 'ERROR'}")
print(f"Costo fijo (ambos camiones): ${ev_op['costo_fijo']}")
print(f"Shortage: {ev_op['shortage']} L -> ${ev_op['shortage']*PENAL_SHORTAGE}")
print(f"COSTO TOTAL REAL: ${ev_op['costo']}")

print("\n" + "="*70)
print("PREGUNTA 1/3c - TABU SEARCH (ruteo optimo desde cero)")
print("="*70)
mejor, ev, hist = tabu_search(iteraciones=60, tenencia=7)
print("Mejor solucion encontrada por Tabu Search:")
for k in ("T1", "T2"):
    print(f"  {k}: ruta D->{'->'.join(map(str,mejor[k]['ruta']))}->D "
          f"comp {mejor[k]['comp']}  ({distancia_ruta(mejor[k]['ruta'])} km)")
print(f"  Distancia total: {ev['dist_km']} km | costo distancia ${ev['costo_distancia']} "
      f"| fijo ${ev['costo_fijo']} | shortage {ev['shortage']} L")
print(f"  COSTO TOTAL: ${ev['costo']} | factible={ev['factible']}")

print("\n--- Verificacion: fuerza bruta (optimo global) ---")
bf_sol, bf_ev, n_fact = optimo_fuerza_bruta()
print(f"Soluciones factibles enumeradas: {n_fact}")
for k in ("T1", "T2"):
    print(f"  {k}: ruta D->{'->'.join(map(str,bf_sol[k]['ruta']))}->D comp {bf_sol[k]['comp']}")
print(f"  Costo optimo global: ${bf_ev['costo']} ({bf_ev['dist_km']} km)")
print(f"  TABU == OPTIMO GLOBAL? {'SI' if ev['costo']==bf_ev['costo'] else 'NO'}")

# perfil de estabilidad de la solucion optima
print("\n--- Estabilidad de la solucion optima ---")
for k in ("T1", "T2"):
    if mejor[k]["ruta"]:
        print(f"{k} ruta {mejor[k]['ruta']} comp {mejor[k]['comp']}")
        for etq, a, b in perfil_fill_ratios(k, mejor[k]["ruta"], mejor[k]["comp"]):
            print(f"   {etq:18s} fr_C0={a*100:5.1f}%  fr_C1={b*100:5.1f}%  |dif|={abs(a-b)*100:4.1f}%")

print("\n" + "="*70)
print("PREGUNTA 2 - TIEMPOS DE CARGA Y SCHEDULING")
print("="*70)
dur, ini, fin, listo, mk = scheduling_makespan()
print("(a) Tiempos de carga (carga + 5 min limpieza):")
for op_id, k, c, fuel, lit in OPERACIONES_CARGA:
    print(f"   {op_id} ({fuel} {lit}L): {lit}/{TASA[fuel]} + 5 = {dur[op_id]:.1f} min")
print("\n(c) Programacion optima (makespan):")
for op_id in ["T1_C0","T1_C1","T2_C0","T2_C1"]:
    print(f"   {op_id}: inicia {ini[op_id]:.1f}  termina {fin[op_id]:.1f}")
print(f"   Camion listo: T1={listo['T1']:.1f} min, T2={listo['T2']:.1f} min")
print(f"   MAKESPAN = {mk:.1f} min")
print(f"   Si la carga inicia 04:00 -> T1 listo {listo['T1']:.1f}min, T2 listo {listo['T2']:.1f}min")
print(f"   T1 debe salir 05:00, T2 05:30 -> ambos alcanzan con holgura.")

print("\n" + "="*70)
print("PREGUNTA 4 - DEMANDA POR ESCENARIO")
print("="*70)
for s, d in demanda_total_por_escenario().items():
    print(f"  {s:10s} p={d['prob']}  Regular={d['R']} L  Diesel={d['D']} L  total={d['total']} L")
cap_R = max(c['C0'] for c in CAMIONES.values()), max(c['C1'] for c in CAMIONES.values())
print(f"  Capacidad total flota: {sum(c['C0']+c['C1'] for c in CAMIONES.values())} L")
