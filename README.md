# Prueba Optimización — Solemne IA (CINF105)

Distribución de combustibles resuelta con **Jupyter Notebook** y la metaheurística
**Tabu Search**. Todos los datos provienen del enunciado (`Solemne_Optimizacion.pdf`);
no se inventó ningún valor.

> El enunciado pedía AMPL. Por indicación del curso, el modelo se implementa en
> Python/Jupyter y el ruteo se resuelve con Tabu Search. La formulación matemática
> (la teoría) se mantiene; solo cambia la herramienta de resolución.

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `Tutorial_Solemne_Optimizacion.pdf` | Informe didáctico: definiciones, formulación, resultados y figuras. |
| `Solemne_Optimizacion.ipynb` | Notebook que **ejecuta** todos los cálculos. |
| `modelo.py` | Datos del enunciado, función objetivo y restricciones. |
| `tabu.py` | Implementación de Tabu Search (más fuerza bruta de verificación). |
| `figuras.py` | Genera las figuras (rutas, convergencia, Gantt, estabilidad). |
| `verificar.py` | Script que imprime todas las verificaciones en consola. |
| `figuras/` | Imágenes usadas en el informe y el notebook. |
| `Solemne_Optimizacion.pdf` | Enunciado original de la prueba. |
| `requirements.txt` | Dependencias de Python. |

## Cómo reproducir los resultados

```bash
pip install -r requirements.txt
jupyter notebook Solemne_Optimizacion.ipynb   # ejecutar todas las celdas
# o, sin Jupyter, ver las verificaciones por consola:
python verificar.py
```

## Resultados principales

- **P1 — Ruteo óptimo:** T1: D→1→2→4→D, T2: D→3→D · 115 km · **costo total $1.130**
  (óptimo global, verificado por fuerza bruta).
- **P2 — Scheduling:** makespan = **32.5 min**; ambos camiones listos antes de su hora de salida.
- **P3 — Solución del operador:** infactible (T2 viola la estabilidad: 30.6 % > 30 %) y el costo
  está mal declarado (real **$1.200**, no $260).
- **P3c — Mejora:** reasignar la estación 2 a T1 → 115 km, factible, ahorro de $70 en distancia.
- **P4 — Estocástico:** modelo de dos etapas (rutas en 1ª etapa; cargas y faltantes como
  *recourse* por escenario).

## ¿Por qué Tabu Search?

El ruteo es un VRPTW con asignación de compartimentos: combinatorio y NP-difícil.
Tabu Search explora soluciones vecinas y usa una lista tabú (memoria) para escapar de
óptimos locales. Es simple, rápida y no requiere un solver comercial. Como el caso es
pequeño, comprobamos con fuerza bruta que alcanza el óptimo global.
