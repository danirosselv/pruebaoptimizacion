# README de Ejecucion

## Archivos principales

- Archivo principal: `Solemne_Optimizacion_Tabu.pdf`
- Evidencia computacional: `Solemne_Optimizacion_Tabu_Search.ipynb`

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion

```bash
jupyter notebook Solemne_Optimizacion_Tabu_Search.ipynb
```

El notebook ya queda guardado con salidas visibles y puede volver a ejecutarse de arriba hacia abajo.

## Resultados esperados principales

- La solucion propuesta por el operador presenta una violacion de estabilidad en T2.
- Bajo cargas corregidas para shortage cero, el costo operacional de la propuesta del operador es $1200; sin embargo, los fill ratios declarados no son consistentes con shortage cero.
- La mejor solucion encontrada mediante Tabu Search es:
  - `T1: D->1->2->4->D`
  - `T2: D->3->D`
- El costo total de la solucion mejorada es `$1130`.
- El scheduling de carga tiene makespan optimo de `32.5` minutos.
- La validacion exhaustiva confirma que Tabu Search coincide con el mejor costo factible enumerado bajo los supuestos implementados.

## Nota metodologica

La entrega utiliza Tabu Search en Python como reemplazo de AMPL para la resolucion computacional. La formulacion matematica se conserva en `Solemne_Optimizacion_Tabu.pdf` y la implementacion reproducible se adjunta en `Solemne_Optimizacion_Tabu_Search.ipynb`.
