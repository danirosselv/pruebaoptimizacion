# -*- coding: utf-8 -*-
"""Genera las figuras para el PDF y el notebook."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from modelo import *
from tabu import tabu_search

OUT = "figuras"
os.makedirs(OUT, exist_ok=True)

# Coordenadas aproximadas SOLO para dibujar (no afectan el calculo, que usa la
# matriz de distancias del enunciado). Sirven para visualizar las rutas.
COORD = {0: (0, 0), 1: (-2, 2), 2: (2.5, 1.5), 3: (-0.5, -2.2), 4: (3, -1.5)}
NOMBRE = {0: "Deposito", 1: "Est.1", 2: "Est.2", 3: "Est.3", 4: "Est.4"}

def dibujar_rutas(sol, titulo, fname):
    fig, ax = plt.subplots(figsize=(6, 5))
    colores = {"T1": "#1f77b4", "T2": "#d62728"}
    for n, (x, y) in COORD.items():
        ax.scatter([x], [y], s=600 if n == 0 else 420,
                   c="#333" if n == 0 else "#bbb", zorder=3,
                   marker="s" if n == 0 else "o", edgecolors="k")
        ax.annotate(NOMBRE[n], (x, y), ha="center", va="center",
                    color="white" if n == 0 else "black", fontsize=8, zorder=4)
    for k in ("T1", "T2"):
        ruta = sol[k]["ruta"]
        if not ruta:
            continue
        nodos = [0] + ruta + [0]
        for i in range(len(nodos) - 1):
            a, b = nodos[i], nodos[i + 1]
            (x1, y1), (x2, y2) = COORD[a], COORD[b]
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="->", color=colores[k], lw=2,
                                        shrinkA=18, shrinkB=18), zorder=2)
        d = distancia_ruta(ruta)
        ax.plot([], [], color=colores[k], lw=2,
                label=f"{k}: D->{'->'.join(map(str,ruta))}->D ({d} km)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), fontsize=8)
    ax.set_title(titulo, fontsize=11, weight="bold")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(f"{OUT}/{fname}", dpi=140, bbox_inches="tight")
    plt.close()

# Figura 1: solucion del operador
op = {"T1": {"ruta": [1, 3], "comp": {"C0": "R", "C1": "D"}},
      "T2": {"ruta": [2, 4], "comp": {"C0": "D", "C1": "R"}}}
dibujar_rutas(op, "Solucion del operador  (150 km, $1200 real)", "rutas_operador.png")

# Figura 2: solucion optima (Tabu Search)
mejor, ev, hist = tabu_search(iteraciones=60, tenencia=7)
dibujar_rutas(mejor, f"Solucion optima Tabu Search  (115 km, ${ev['costo']})",
              "rutas_optimo.png")

# Figura 3: convergencia de Tabu Search
fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.plot(range(len(hist)), hist, marker="o", ms=3, color="#1f77b4")
ax.axhline(1130, ls="--", color="#2ca02c", label="Optimo global ($1130)")
ax.set_xlabel("Iteracion"); ax.set_ylabel("Mejor costo ($)")
ax.set_title("Convergencia de Tabu Search", weight="bold")
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(f"{OUT}/convergencia.png", dpi=140); plt.close()

# Figura 4: Gantt del scheduling (Pregunta 2)
dur, ini, fin, listo, mk = scheduling_makespan()
fig, ax = plt.subplots(figsize=(7, 3.2))
filas = {"Bahia Regular": ["T1_C0", "T2_C1"], "Bahia Diesel": ["T2_C0", "T1_C1"]}
ypos = {"Bahia Regular": 1, "Bahia Diesel": 0}
colores_op = {"T1_C0": "#1f77b4", "T1_C1": "#1f77b4",
              "T2_C0": "#d62728", "T2_C1": "#d62728"}
for fila, ops in filas.items():
    for op_id in ops:
        ax.barh(ypos[fila], dur[op_id], left=ini[op_id], height=0.5,
                color=colores_op[op_id], edgecolor="k", alpha=0.85)
        ax.text(ini[op_id] + dur[op_id] / 2, ypos[fila],
                f"{op_id}\n{dur[op_id]:.1f}", ha="center", va="center",
                color="white", fontsize=8, weight="bold")
ax.axvline(mk, ls="--", color="green")
ax.text(mk + 0.3, 1.5, f"makespan = {mk:.1f} min", color="green", fontsize=9)
ax.set_yticks([0, 1]); ax.set_yticklabels(["Bahia Diesel", "Bahia Regular"])
ax.set_xlabel("Minutos desde el inicio de la carga")
ax.set_title("Diagrama de Gantt - Scheduling de carga (makespan optimo)", weight="bold")
ax.set_xlim(0, mk + 6)
plt.tight_layout(); plt.savefig(f"{OUT}/gantt.png", dpi=140); plt.close()

# Figura 5: estabilidad T2 operador (viola) vs reordenado (ok)
fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
for ax, ruta, tit in zip(axes, [[2, 4], [4, 2]],
                         ["T2 operador  D->2->4  (VIOLA)", "T2 reordenado  D->4->2  (OK)"]):
    perfil = perfil_fill_ratios("T2", ruta, {"C0": "D", "C1": "R"})
    etqs = [p[0] for p in perfil]
    c0 = [p[1] * 100 for p in perfil]; c1 = [p[2] * 100 for p in perfil]
    x = range(len(perfil))
    ax.plot(x, c0, marker="o", label="C0 (Diesel)")
    ax.plot(x, c1, marker="s", label="C1 (Regular)")
    for xi, (a, b) in zip(x, zip(c0, c1)):
        dif = abs(a - b)
        ax.annotate(f"{dif:.0f}%", (xi, max(a, b) + 4), ha="center",
                    color="red" if dif > 30 else "gray", fontsize=8)
    ax.set_xticks(list(x)); ax.set_xticklabels(etqs, rotation=20, fontsize=7)
    ax.set_title(tit, fontsize=10, weight="bold"); ax.grid(alpha=0.3); ax.legend(fontsize=8)
axes[0].set_ylabel("Fill ratio (%)")
plt.tight_layout(); plt.savefig(f"{OUT}/estabilidad_t2.png", dpi=140); plt.close()

print("Figuras generadas:", os.listdir(OUT))
