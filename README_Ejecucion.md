# README de Ejecucion

## Archivos principales

- Archivo principal de evaluacion: `Solemne_Optimizacion_Respuesta.pdf`
- Evidencia computacional: `Solemne_Optimizacion_Tabu_Search.ipynb`

## Archivos de apoyo para la ejecucion

- `modelo.py`: datos del problema, evaluacion de soluciones y scheduling.
- `tabu.py`: implementacion de Tabu Search con reinicios reproducibles.
- `figuras.py`: generacion de figuras usadas en el notebook.
- `figuras/`: imagenes generadas para respaldar rutas, convergencia, estabilidad y Gantt.

## Instalacion de dependencias

```bash
pip install -r requirements.txt
```

## Ejecucion del notebook

```bash
jupyter notebook Solemne_Optimizacion_Tabu_Search.ipynb
```

Luego se debe ejecutar el notebook completo de arriba hacia abajo.

## Resultados principales esperados

- La solucion propuesta por el operador resulta infactible por una violacion de estabilidad en T2.
- El costo total real de la propuesta del operador es `$1200`.
- La mejor solucion encontrada por Tabu Search es:
  - `T1: D->1->2->4->D`
  - `T2: D->3->D`
- El costo total de la solucion mejorada es `$1130`.
- El scheduling de carga tiene makespan optimo de `32.5` minutos.
- La validacion exhaustiva confirma que Tabu Search alcanza el mismo costo optimo que la enumeracion completa del espacio factible.

## Nota metodologica

La entrega utiliza Tabu Search en Python como reemplazo de AMPL para la resolucion computacional. La formulacion matematica del problema se mantiene en el informe `Solemne_Optimizacion_Respuesta.pdf`, mientras que la ejecucion reproducible y la validacion de resultados se documentan en el notebook adjunto.
