# -*- coding: utf-8 -*-
"""Generacion de figuras para el notebook y el informe final."""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from modelo import distancia_ruta, perfil_fill_ratios, scheduling_makespan
from tabu import tabu_search

OUT = "figuras"
COORD = {0: (0, 0), 1: (-2, 2), 2: (2.5, 1.5), 3: (-0.5, -2.2), 4: (3, -1.5)}
NOMBRE = {0: "Deposito", 1: "Est. 1", 2: "Est. 2", 3: "Est. 3", 4: "Est. 4"}


def dibujar_rutas(sol, titulo, fname, out_dir=OUT):
    fig, ax = plt.subplots(figsize=(6, 5))
    colores = {"T1": "#1f77b4", "T2": "#d62728"}

    for nodo, (x, y) in COORD.items():
        ax.scatter(
            [x],
            [y],
            s=600 if nodo == 0 else 420,
            c="#333333" if nodo == 0 else "#c9d6df",
            zorder=3,
            marker="s" if nodo == 0 else "o",
            edgecolors="k",
        )
        ax.annotate(
            NOMBRE[nodo],
            (x, y),
            ha="center",
            va="center",
            color="white" if nodo == 0 else "black",
            fontsize=8,
            zorder=4,
        )

    for camion in ("T1", "T2"):
        ruta = sol[camion]["ruta"]
        if not ruta:
            continue
        nodos = [0] + ruta + [0]
        for i in range(len(nodos) - 1):
            origen, destino = nodos[i], nodos[i + 1]
            (x1, y1), (x2, y2) = COORD[origen], COORD[destino]
            ax.annotate(
                "",
                xy=(x2, y2),
                xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="->",
                    color=colores[camion],
                    lw=2,
                    shrinkA=18,
                    shrinkB=18,
                ),
                zorder=2,
            )
        distancia = distancia_ruta(ruta)
        ax.plot(
            [],
            [],
            color=colores[camion],
            lw=2,
            label=f"{camion}: D->{'->'.join(map(str, ruta))}->D ({distancia} km)",
        )

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), fontsize=8)
    ax.set_title(titulo, fontsize=11, weight="bold")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, fname), dpi=140, bbox_inches="tight")
    plt.close()


def generar_figuras(iteraciones=80, tenencia=7, reinicios=4, semilla=42, out_dir=OUT):
    os.makedirs(out_dir, exist_ok=True)

    operador = {
        "T1": {"ruta": [1, 3], "comp": {"C0": "R", "C1": "D"}},
        "T2": {"ruta": [2, 4], "comp": {"C0": "D", "C1": "R"}},
    }
    dibujar_rutas(
        operador,
        "Solucion propuesta por el operador",
        "rutas_operador.png",
        out_dir=out_dir,
    )

    mejor, evaluacion, historial, meta = tabu_search(
        iteraciones=iteraciones,
        tenencia=tenencia,
        reinicios=reinicios,
        semilla=semilla,
        return_meta=True,
    )
    dibujar_rutas(
        mejor,
        "Mejor solucion encontrada mediante Tabu Search",
        "rutas_optimo.png",
        out_dir=out_dir,
    )

    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    ax.plot(range(len(historial)), historial, marker="o", ms=3, color="#1f77b4")
    ax.axhline(evaluacion["costo"], ls="--", color="#2ca02c", label=f"Mejor costo = ${evaluacion['costo']}")
    ax.set_xlabel("Iteracion acumulada")
    ax.set_ylabel("Mejor costo penalizado")
    ax.set_title("Convergencia de Tabu Search", weight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "convergencia.png"), dpi=140)
    plt.close()

    duraciones, inicios, _, _, makespan = scheduling_makespan()
    fig, ax = plt.subplots(figsize=(7, 3.2))
    filas = {"Bahia Regular": ["T1_C0", "T2_C1"], "Bahia Diesel": ["T2_C0", "T1_C1"]}
    ypos = {"Bahia Regular": 1, "Bahia Diesel": 0}
    colores_op = {
        "T1_C0": "#1f77b4",
        "T1_C1": "#1f77b4",
        "T2_C0": "#d62728",
        "T2_C1": "#d62728",
    }
    for fila, ops in filas.items():
        for op_id in ops:
            ax.barh(
                ypos[fila],
                duraciones[op_id],
                left=inicios[op_id],
                height=0.5,
                color=colores_op[op_id],
                edgecolor="k",
                alpha=0.85,
            )
            ax.text(
                inicios[op_id] + duraciones[op_id] / 2,
                ypos[fila],
                f"{op_id}\n{duraciones[op_id]:.1f}",
                ha="center",
                va="center",
                color="white",
                fontsize=8,
                weight="bold",
            )
    ax.axvline(makespan, ls="--", color="green")
    ax.text(makespan + 0.3, 1.35, f"Makespan = {makespan:.1f} min", color="green", fontsize=9)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Bahia Diesel", "Bahia Regular"])
    ax.set_xlabel("Minutos desde el inicio de la carga")
    ax.set_title("Programacion optima de carga", weight="bold")
    ax.set_xlim(0, makespan + 6)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gantt.png"), dpi=140)
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, ruta, titulo in zip(
        axes,
        [[2, 4], [4, 2]],
        ["Ruta del operador T2: D->2->4", "Ruta reordenada T2: D->4->2"],
    ):
        perfil = perfil_fill_ratios("T2", ruta, {"C0": "D", "C1": "R"})
        etiquetas = [p[0] for p in perfil]
        c0 = [p[1] * 100 for p in perfil]
        c1 = [p[2] * 100 for p in perfil]
        x = range(len(perfil))
        ax.plot(x, c0, marker="o", label="C0 (Diesel)")
        ax.plot(x, c1, marker="s", label="C1 (Regular)")
        for xi, (a, b) in zip(x, zip(c0, c1)):
            diferencia = abs(a - b)
            ax.annotate(
                f"{diferencia:.1f}%",
                (xi, max(a, b) + 4),
                ha="center",
                color="red" if diferencia > 30 else "gray",
                fontsize=8,
            )
        ax.set_xticks(list(x))
        ax.set_xticklabels(etiquetas, rotation=20, fontsize=7)
        ax.set_title(titulo, fontsize=10, weight="bold")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Fill ratio (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "estabilidad_t2.png"), dpi=140)
    plt.close()

    return {
        "mejor": mejor,
        "evaluacion": evaluacion,
        "historial": historial,
        "meta": meta,
        "archivos": {
            "rutas_operador": os.path.join(out_dir, "rutas_operador.png"),
            "rutas_optimo": os.path.join(out_dir, "rutas_optimo.png"),
            "convergencia": os.path.join(out_dir, "convergencia.png"),
            "gantt": os.path.join(out_dir, "gantt.png"),
            "estabilidad_t2": os.path.join(out_dir, "estabilidad_t2.png"),
        },
    }


if __name__ == "__main__":
    generar_figuras()
    print("Figuras generadas:", sorted(os.listdir(OUT)))
