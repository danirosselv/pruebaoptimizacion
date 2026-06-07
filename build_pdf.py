# -*- coding: utf-8 -*-
"""Genera el PDF tutorial didactico de la Solemne."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Image, Table, TableStyle, ListFlowable, ListItem,
                                HRFlowable, KeepTogether)

AZUL = colors.HexColor("#1F4E79")
AZUL2 = colors.HexColor("#2E75B6")
GRIS = colors.HexColor("#F2F2F2")
ROJO = colors.HexColor("#C00000")
VERDE = colors.HexColor("#2E7D32")

styles = getSampleStyleSheet()
S = {}
S['titulo'] = ParagraphStyle('titulo', parent=styles['Title'], fontName='Helvetica-Bold',
                             fontSize=22, textColor=AZUL, spaceAfter=6, leading=26)
S['subtitulo'] = ParagraphStyle('subtitulo', parent=styles['Normal'], fontSize=12,
                             textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=18)
S['h1'] = ParagraphStyle('h1', parent=styles['Heading1'], fontName='Helvetica-Bold',
                             fontSize=15, textColor=colors.white, backColor=AZUL,
                             borderPadding=(6,6,6,6), spaceBefore=16, spaceAfter=10, leading=18)
S['h2'] = ParagraphStyle('h2', parent=styles['Heading2'], fontName='Helvetica-Bold',
                             fontSize=12.5, textColor=AZUL, spaceBefore=12, spaceAfter=5, leading=15)
S['h3'] = ParagraphStyle('h3', parent=styles['Heading3'], fontName='Helvetica-Bold',
                             fontSize=11, textColor=AZUL2, spaceBefore=8, spaceAfter=3)
S['body'] = ParagraphStyle('body', parent=styles['Normal'], fontSize=10.3, leading=15,
                             alignment=TA_JUSTIFY, spaceAfter=6)
S['bullet'] = ParagraphStyle('bullet', parent=S['body'], leftIndent=10, spaceAfter=2)
S['note'] = ParagraphStyle('note', parent=S['body'], fontSize=9.8, leading=13.5,
                             leftIndent=8, rightIndent=8, spaceBefore=2, spaceAfter=2)
S['code'] = ParagraphStyle('code', parent=styles['Normal'], fontName='Courier', fontSize=9,
                             leading=12, textColor=colors.HexColor("#1a1a1a"))
S['mono'] = ParagraphStyle('mono', parent=styles['Normal'], fontName='Courier-Bold', fontSize=9.5,
                             leading=13, alignment=TA_CENTER)
S['cap'] = ParagraphStyle('cap', parent=styles['Normal'], fontSize=8.7, leading=11,
                             alignment=TA_CENTER, textColor=colors.HexColor("#666666"), spaceAfter=10)
S['formula'] = ParagraphStyle('formula', parent=styles['Normal'], fontName='Helvetica',
                             fontSize=10.2, leading=15, alignment=TA_CENTER, spaceBefore=4,
                             spaceAfter=4, textColor=colors.HexColor("#222222"))

story = []
def P(t, st='body'): story.append(Paragraph(t, S[st]))
def SP(h=8): story.append(Spacer(1, h))

def callout(titulo, texto, color=AZUL2, bg=colors.HexColor("#EAF1FB")):
    inner = [Paragraph(f"<b>{titulo}</b>", S['note']), Paragraph(texto, S['note'])]
    t = Table([[inner]], colWidths=[16.0*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1), bg),
        ('LINEABOVE',(0,0),(-1,0), 2, color),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(t); SP(8)

def bullets(items, st='bullet'):
    flow = ListFlowable([ListItem(Paragraph(it, S[st]), leftIndent=14, value='•')
                         for it in items], bulletType='bullet', start='•')
    story.append(flow); SP(4)

def tabla(data, colWidths, header=True, font=9.2, aligns=None):
    t = Table(data, colWidths=colWidths, repeatRows=1 if header else 0)
    st = [('FONTSIZE',(0,0),(-1,-1),font),('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#BBBBBB")),
          ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),4),
          ('BOTTOMPADDING',(0,0),(-1,-1),4),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]
    if header:
        st += [('BACKGROUND',(0,0),(-1,0),AZUL),('TEXTCOLOR',(0,0),(-1,0),colors.white),
               ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('ALIGN',(0,0),(-1,0),'CENTER'),
               ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, GRIS])]
    if aligns:
        for col,al in aligns.items(): st.append(('ALIGN',(col,0 if not header else 1),(col,-1),al))
    t.setStyle(TableStyle(st))
    story.append(t); SP(8)

def fig(path, w=14, cap=None):
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(path).getSize()
    h = w * ih / iw
    story.append(Image(path, width=w*cm, height=h*cm, hAlign='CENTER'))
    if cap: P(cap, 'cap')
    else: SP(8)

# ===========================================================================
# PORTADA
# ===========================================================================
SP(40)
P("Solemne IA — Optimización", 'titulo')
P("CINF105 · Distribución de combustibles resuelta con Tabu Search", 'subtitulo')
story.append(HRFlowable(width="100%", thickness=2, color=AZUL, spaceAfter=14))
SP(6)
callout("Cómo leer este documento",
        "Este tutorial explica <b>paso a paso y desde cero</b> toda la prueba: qué se pide, qué "
        "significa cada concepto y cómo llegamos a cada resultado. El código que produce los "
        "números está en el notebook <font face='Courier'>Solemne_Optimizacion.ipynb</font>; aquí "
        "explicamos qué hace y qué entrega. <b>No se inventó ningún dato</b>: todo sale del "
        "enunciado y se verificó ejecutando el código.")
SP(4)
P("<b>Aclaración sobre la herramienta.</b> El enunciado pedía AMPL. Por indicación del curso, "
  "implementamos el modelo en <b>Python / Jupyter Notebook</b> y resolvemos el ruteo con la "
  "metaheurística <b>Tabu Search</b>. La formulación matemática (la \"teoría\") se mantiene igual; "
  "solo cambia la herramienta con la que se resuelve.")
SP(10)

# Indice
P("Contenido", 'h2')
idx = [
 "1.  Glosario: definiciones que necesitas entender primero",
 "2.  ¿Por qué elegimos Tabu Search? (justificación)",
 "3.  Pregunta 1 — Modelo determinista (formulación MILP) + solución",
 "4.  Pregunta 2 — Scheduling de carga en el depósito (makespan)",
 "5.  Pregunta 3 — Análisis de la solución del operador",
 "6.  Pregunta 4 — Extensión estocástica (modelo de dos etapas)",
 "7.  Resumen de resultados y archivos entregados",
]
bullets(idx)
story.append(PageBreak())

# ===========================================================================
# 1. GLOSARIO
# ===========================================================================
P("1. Glosario: conceptos clave explicados simple", 'h1')
P("Antes de resolver, definimos en lenguaje sencillo cada término que aparece en la prueba. "
  "Si entiendes esto, entiendes todo lo demás.", 'body')

defs = [
 ("Optimización", "Buscar la <b>mejor</b> decisión posible (la de menor costo, en nuestro caso) "
  "respetando un conjunto de reglas obligatorias llamadas restricciones."),
 ("Función objetivo", "La fórmula que mide qué tan buena es una solución. Aquí mide el "
  "<b>costo total</b> y queremos <b>minimizarla</b>."),
 ("Restricción", "Una condición que la solución <b>debe</b> cumplir sí o sí (por ejemplo, no "
  "superar la capacidad de un camión)."),
 ("Variable de decisión", "Lo que el modelo decide. Pueden ser: <b>binarias</b> (0 ó 1, tipo "
  "sí/no, ej. \"¿uso este camión?\"), <b>enteras</b> (0,1,2,3...) o <b>continuas</b> (cualquier "
  "número, ej. litros = 5500.0)."),
 ("MILP", "<i>Mixed-Integer Linear Programming</i> (Programación Lineal Entera Mixta). Es un "
  "modelo donde la función objetivo y las restricciones son lineales y algunas variables deben "
  "ser enteras/binarias. Es el tipo de modelo que pide la Pregunta 1."),
 ("Fill ratio (nivel de llenado)", "Cuánto líquido tiene un compartimento respecto de su "
  "capacidad: <b>fill ratio = litros actuales / capacidad</b>. Si un tanque de 8000 L lleva "
  "5500 L, su fill ratio es 5500/8000 = 68.8%."),
 ("Estabilidad de carga (Δ=0.30)", "Por seguridad, los dos compartimentos de un mismo camión "
  "no pueden tener niveles muy distintos: la diferencia de sus fill ratios no puede pasar de "
  "0.30 (30%) <b>en ningún momento</b> del viaje (al salir y después de cada entrega)."),
 ("Ventana de tiempo [a, b]", "Cada estación solo recibe entre una hora de apertura <i>a</i> y "
  "una de cierre <i>b</i>. El camión debe llegar dentro de ese rango (si llega antes, espera)."),
 ("Shortage (faltante)", "Litros de demanda que <b>no</b> se alcanzan a entregar. Cada litro "
  "faltante cuesta una penalización de $10."),
 ("Makespan", "En un calendario de tareas, es el <b>instante en que termina la última tarea</b>. "
  "En la Pregunta 2 es el momento en que el último camión queda listo para salir."),
 ("Metaheurística", "Una estrategia inteligente para encontrar <b>muy buenas</b> soluciones a "
  "problemas difíciles en tiempo razonable, sin garantizar siempre la perfecta (aunque aquí sí "
  "lo logramos y lo comprobamos)."),
 ("Tabu Search", "La metaheurística que usamos. Explora soluciones \"vecinas\", se mueve a la "
  "mejor, y guarda en una <b>lista tabú</b> (memoria) los movimientos recientes para no "
  "repetirlos y así <b>escapar de óptimos locales</b>."),
 ("VRPTW", "<i>Vehicle Routing Problem with Time Windows</i>: el problema de decidir rutas de "
  "varios vehículos con ventanas de tiempo. Es exactamente nuestro caso."),
]
for term, d in defs:
    P(f"<b>{term}.</b> {d}", 'body')
story.append(PageBreak())

# ===========================================================================
# 2. POR QUE TABU SEARCH
# ===========================================================================
P("2. ¿Por qué elegimos Tabu Search?", 'h1')
P("El problema de ruteo (Pregunta 1) es un <b>VRPTW con asignación de compartimentos</b>: hay que "
  "decidir, al mismo tiempo, qué estaciones atiende cada camión, en qué orden, y qué combustible "
  "va en cada compartimento. Este tipo de problema es <b>NP-difícil</b>: el número de "
  "combinaciones crece muy rápido y no existe una fórmula directa para la respuesta.", 'body')
P("Tabu Search es una de las metaheurísticas <b>clásicas y más usadas</b> para problemas de "
  "ruteo de vehículos. La elegimos por estas razones:", 'body')
bullets([
 "<b>Maneja bien lo combinatorio:</b> trabaja moviendo estaciones entre camiones y reordenando "
 "rutas, justo las decisiones de nuestro problema.",
 "<b>Escapa de óptimos locales:</b> gracias a la lista tabú (memoria), acepta movimientos que "
 "empeoran temporalmente para no quedarse atascada en una solución mediocre.",
 "<b>Es simple de entender y programar:</b> no necesita un solver comercial como AMPL/CPLEX; "
 "se implementa con Python puro, lo que hace transparente cada paso (importante para explicarlo).",
 "<b>Es rápida:</b> entrega la solución casi instantáneamente para este tamaño.",
])
callout("Comprobación de calidad",
        "Como nuestro caso es pequeño (4 estaciones, 2 camiones), además ejecutamos una "
        "<b>fuerza bruta</b> que prueba todas las combinaciones factibles. Resultado: Tabu Search "
        "encontró exactamente el <b>óptimo global</b> ($1.130). Así demostramos que la "
        "metaheurística no solo es rápida, sino correcta.", color=VERDE,
        bg=colors.HexColor("#EAF6EC"))
P("<font size=8>Referencia conceptual: la Tabu Search fue propuesta por F. Glover (1986) y es un "
  "estándar para el VRP en la literatura de optimización.</font>", 'note')

# ===========================================================================
# 3. PREGUNTA 1
# ===========================================================================
story.append(PageBreak())
P("3. Pregunta 1 — Modelo determinista (MILP)", 'h1')
P("Se pide formular un modelo MILP completo para el escenario s=1. A continuación damos la "
  "formulación (la teoría) y luego cómo la resolvimos con Tabu Search.", 'body')

P("a) Conjuntos y parámetros", 'h2')
P("<b>Conjuntos:</b>", 'body')
bullets([
 "N = {0,1,2,3,4}: nodos, donde 0 es el depósito.",
 "J = {1,2,3,4}: estaciones de servicio.",
 "K = {T1, T2}: camiones.",
 "C = {C0, C1}: compartimentos de cada camión.",
 "P = {R, D}: productos (R = Regular, D = Diésel).",
])
P("<b>Parámetros (todos del enunciado):</b>", 'body')
bullets([
 "d<sub>i,i'</sub>: distancia entre los nodos i e i' (matriz de distancias).",
 "DR<sub>j</sub>, DD<sub>j</sub>: demanda de Regular y de Diésel de la estación j.",
 "Q<sub>k,c</sub>: capacidad del compartimento c del camión k.",
 "F<sub>k</sub>: costo fijo de usar el camión k ($500 T1, $400 T2).",
 "[a<sub>j</sub>, b<sub>j</sub>]: ventana de tiempo de la estación j.",
 "cd = $2/km (costo de distancia); cp = $10/L (penalización de faltante).",
 "ts = 30 min (servicio); v = 60 km/h (velocidad); Δ = 0.30 (estabilidad).",
])

P("b) Variables de decisión", 'h2')
data = [["Variable","Tipo","Significado"],
 ["x<sub>k,i,i'</sub>","binaria","1 si el camión k viaja directo del nodo i al i'"],
 ["y<sub>k,j</sub>","binaria","1 si el camión k atiende la estación j"],
 ["u<sub>k</sub>","binaria","1 si el camión k se usa (paga costo fijo)"],
 ["z<sub>k,c,p</sub>","binaria","1 si el compartimento c del camión k lleva el producto p"],
 ["l<sub>k,c</sub>","continua","litros cargados en el compartimento c del camión k"],
 ["gR<sub>j</sub>, gD<sub>j</sub>","continua","litros NO entregados (shortage) en la estación j"],
 ["t<sub>k,j</sub>","continua","hora de llegada del camión k a la estación j"],
]
tabla([[Paragraph(c, S['body']) for c in row] for row in data],
      [3.0*cm, 2.2*cm, 9.6*cm])

P("c) Función objetivo", 'h2')
P("Se minimiza el costo total, que tiene tres componentes:", 'body')
P("min  Z = cd · Σ<sub>k,i,i'</sub> d<sub>i,i'</sub> x<sub>k,i,i'</sub>  +  Σ<sub>k</sub> F<sub>k</sub> u<sub>k</sub>  "
  "+  cp · Σ<sub>j</sub> (gR<sub>j</sub> + gD<sub>j</sub>)", 'formula')
bullets([
 "<b>Costo de distancia:</b> $2 por cada km recorrido por todos los camiones.",
 "<b>Costo fijo:</b> $500 y/o $400 por cada camión que se utiliza.",
 "<b>Penalización por faltante:</b> $10 por cada litro de demanda no satisfecha.",
])

P("d) Restricciones (agrupadas)", 'h2')
P("<b>1) Conservación de flujo (routing):</b> si un camión entra a un nodo, debe salir de él; "
  "y cada camión usado sale del depósito.", 'body')
P("Σ<sub>i</sub> x<sub>k,i,j</sub> = Σ<sub>i</sub> x<sub>k,j,i</sub> = y<sub>k,j</sub>      ;      "
  "Σ<sub>j</sub> x<sub>k,0,j</sub> = u<sub>k</sub>", 'formula')
P("<b>2) Satisfacción de demanda con faltante:</b> lo entregado más el faltante iguala la "
  "demanda. Cada estación es atendida por un camión.", 'body')
P("Σ<sub>k</sub> y<sub>k,j</sub> = 1      ;      entregado<sub>j,p</sub> + g<sub>j,p</sub> = D<sub>j,p</sub>", 'formula')
P("<b>3) Compatibilidad compartimento–producto:</b> cada compartimento lleva un único producto, "
  "y un camión transporta los dos productos en compartimentos distintos.", 'body')
P("Σ<sub>p</sub> z<sub>k,c,p</sub> = u<sub>k</sub>      ;      Σ<sub>c</sub> z<sub>k,c,p</sub> = u<sub>k</sub>", 'formula')
P("<b>4) Capacidad de cada compartimento:</b> no se puede cargar más de lo que cabe.", 'body')
P("l<sub>k,c</sub> ≤ Σ<sub>p</sub> Q<sub>k,c</sub> z<sub>k,c,p</sub>", 'formula')
P("<b>5) Estabilidad de carga (Δ=0.30):</b> en cada instante r de la ruta (salida y tras cada "
  "entrega), la diferencia de fill ratios de los dos compartimentos del camión no supera 0.30.", 'body')
P("| l<sup>r</sup><sub>k,C0</sub> / Q<sub>k,C0</sub>  −  l<sup>r</sup><sub>k,C1</sub> / Q<sub>k,C1</sub> | ≤ Δ", 'formula')
P("<b>6) Ventanas de tiempo:</b> el camión debe llegar dentro del horario y se respeta el tiempo "
  "de viaje y de servicio entre estaciones.", 'body')
P("a<sub>j</sub> ≤ t<sub>k,j</sub> ≤ b<sub>j</sub>      ;      "
  "t<sub>k,j'</sub> ≥ t<sub>k,j</sub> + ts + d<sub>j,j'</sub>/v − M(1 − x<sub>k,j,j'</sub>)", 'formula')
P("(Además, restricciones de eliminación de subtours tipo MTZ para que cada ruta sea un único "
  "recorrido conectado al depósito.)", 'note')

P("Solución obtenida con Tabu Search", 'h2')
P("Resolviendo el modelo anterior con Tabu Search (y confirmando con fuerza bruta), la mejor "
  "asignación de rutas para el escenario s=1 es:", 'body')
sol = [["Camión","Ruta óptima","Estaciones","Distancia"],
 ["T1","D → 1 → 2 → 4 → D","1, 2, 4","85 km"],
 ["T2","D → 3 → D","3","30 km"]]
tabla([[Paragraph(c, S['body']) for c in r] for r in sol],
      [2.0*cm, 5.2*cm, 4.0*cm, 3.6*cm])
P("<b>Costo total óptimo = $1.130</b>  =  distancia $230 (115 km × $2)  +  costos fijos $900 "
  "(ambos camiones)  +  shortage $0. Esta solución es <b>factible</b>: cumple capacidad, "
  "estabilidad (Δ ≤ 0.30 en todo instante) y ventanas de tiempo.", 'body')
fig("figuras/rutas_optimo.png", w=10.5, cap="Figura 1. Rutas de la solución óptima encontrada por Tabu Search.")
fig("figuras/convergencia.png", w=13, cap="Figura 2. Convergencia de Tabu Search hacia el óptimo global ($1.130).")

# ===========================================================================
# 4. PREGUNTA 2
# ===========================================================================
story.append(PageBreak())
P("4. Pregunta 2 — Scheduling de carga en el depósito", 'h1')
P("Antes de salir, cada camión carga sus dos compartimentos uno a la vez. Hay <b>una sola bahía "
  "por combustible</b> (una para Regular, otra para Diésel), por lo que dos camiones no pueden "
  "usar la misma bahía a la vez. Buscamos la programación que minimice el <b>makespan</b> "
  "(cuándo el último camión queda listo).", 'body')

P("a) Cálculo de los tiempos de carga", 'h2')
P("Tiempo = litros ÷ tasa de carga + 5 min de limpieza. Tasas: Regular 500 L/min, Diésel "
  "400 L/min.", 'body')
tc = [["Operación","Producto","Litros","Cálculo","Tiempo"],
 ["T1 · C0","Regular","5.000","5000/500 + 5","15.0 min"],
 ["T1 · C1","Diésel","5.000","5000/400 + 5","17.5 min"],
 ["T2 · C0","Diésel","4.000","4000/400 + 5","15.0 min"],
 ["T2 · C1","Regular","3.500","3500/500 + 5","12.0 min"]]
tabla([[Paragraph(c, S['body']) for c in r] for r in tc],
      [2.3*cm, 2.3*cm, 2.0*cm, 4.0*cm, 2.6*cm])

P("b) Formulación del scheduling", 'h2')
P("Variables: s<sub>k,c</sub> = instante de inicio de la carga del compartimento c del camión k; "
  "y<sub>ij</sub> = 1 si la operación i va antes que la j en la misma bahía. Sea p<sub>k,c</sub> la "
  "duración (tabla anterior) y Cmax el makespan.", 'body')
P("min  Cmax", 'formula')
bullets([
 "<b>Makespan:</b> Cmax ≥ s<sub>k,c</sub> + p<sub>k,c</sub>  para toda operación.",
 "<b>Precedencia en el camión:</b> s<sub>k,C1</sub> ≥ s<sub>k,C0</sub> + p<sub>k,C0</sub> "
 "(el segundo compartimento empieza cuando termina el primero).",
 "<b>No-solapamiento en la bahía:</b> para dos operaciones i, j de la misma bahía, "
 "s<sub>j</sub> ≥ s<sub>i</sub> + p<sub>i</sub> − M(1−y<sub>ij</sub>) y "
 "s<sub>i</sub> ≥ s<sub>j</sub> + p<sub>j</sub> − M·y<sub>ij</sub>.",
])

P("c) Secuencia óptima y diagrama de Gantt", 'h2')
P("El cuello de botella es la <b>bahía Diésel</b>, que debe procesar T2·C0 (15 min) y T1·C1 "
  "(17.5 min) en serie = <b>32.5 min</b> como mínimo. La programación óptima es:", 'body')
sched = [["Bahía","Operación 1","Operación 2"],
 ["Regular","T1·C0  (0 → 15)","T2·C1  (15 → 27)"],
 ["Diésel","T2·C0  (0 → 15)","T1·C1  (15 → 32.5)"]]
tabla([[Paragraph(c, S['body']) for c in r] for r in sched],
      [2.4*cm, 5.4*cm, 5.4*cm])
fig("figuras/gantt.png", w=14, cap="Figura 3. Diagrama de Gantt del scheduling. Makespan óptimo = 32.5 min.")
callout("Verificación de salidas",
        "T1 queda listo a los 32.5 min y T2 a los 27 min. Si la carga comienza a las 04:00, "
        "T1 está listo 04:32:30 (sale a las <b>05:00</b> ✓) y T2 a las 04:27 (sale a las "
        "<b>05:30</b> ✓). Ambos camiones cumplen su hora de salida con holgura.",
        color=VERDE, bg=colors.HexColor("#EAF6EC"))

# ===========================================================================
# 5. PREGUNTA 3
# ===========================================================================
story.append(PageBreak())
P("5. Pregunta 3 — Análisis de la solución del operador", 'h1')
P("El operador propone: <b>T1</b>: D→1→3→D (C0=Regular, C1=Diésel) y <b>T2</b>: D→2→4→D "
  "(C0=Diésel, C1=Regular). Declara costo de distancia = $260 y shortage = 0. Verificamos.", 'body')

P("a) Verificación de factibilidad", 'h2')
P("<b>Capacidad de compartimentos — OK.</b> Cada compartimento puede contener lo que debe "
  "entregar:", 'body')
cap = [["Compartimento","Debe entregar","Capacidad","¿Cabe?"],
 ["T1·C0 (Regular)","5.500 L (est. 1+3)","8.000 L","Sí (68.8%)"],
 ["T1·C1 (Diésel)","5.000 L (est. 1+3)","7.000 L","Sí (71.4%)"],
 ["T2·C0 (Diésel)","4.000 L (est. 2+4)","6.000 L","Sí (66.7%)"],
 ["T2·C1 (Regular)","5.000 L (est. 2+4)","9.000 L","Sí (55.6%)"]]
tabla([[Paragraph(c, S['body']) for c in r] for r in cap],
      [3.6*cm, 4.2*cm, 2.8*cm, 3.0*cm])

P("<b>Estabilidad (Δ=0.30) — ¡FALLA en T2!</b> Calculando el fill ratio en cada instante (cargando "
  "lo necesario para cubrir la demanda):", 'body')
P("• <b>T1 (D→1→3):</b> diferencias de 2.7%, 11.6% y 0% → siempre ≤ 30% ✓.", 'bullet')
P("• <b>T2 (D→2→4):</b> al salir 11.1% ✓, pero <b>después de la estación 2 la diferencia llega a "
  "30.6%</b>, que supera el límite de 30% ✗.", 'bullet')
P("La razón: al entregar en la estación 2 una gran cantidad de Regular (4.000 L), el compartimento "
  "C1 queda casi vacío (11.1%) mientras C0 (Diésel) sigue medio lleno (41.7%).", 'note')
fig("figuras/estabilidad_t2.png", w=15,
    cap="Figura 4. Izquierda: ruta del operador D→2→4 viola la estabilidad (30.6%). "
        "Derecha: invirtiendo a D→4→2 el problema se corrige (máx. 19.4%).")
callout("Cómo se corrige",
        "Si T2 invierte su ruta a <b>D→4→2→D</b> (misma distancia, 90 km), la diferencia máxima "
        "baja a 19.4% y la estabilidad se cumple. Es decir, el problema no era la asignación de "
        "estaciones, sino el <b>orden</b> de visita.")

P("<b>Ventanas de tiempo.</b> A 60 km/h (1 km = 1 min) y 30 min de servicio, las horas de llegada "
  "son muy temprano: T1 llega a la est. 1 a las 05:20 y a la est. 3 a las 06:55; T2 llega a la "
  "est. 2 a las 06:05 y a la est. 4 a las 07:45. Bajo el criterio estándar de VRPTW (si el camión "
  "llega antes de la apertura, <b>espera</b>), todas las llegadas ocurren antes del cierre b<sub>j</sub>, "
  "así que las ventanas <b>se respetan</b>. (Nota: si se exigiera llegar estrictamente después de "
  "la apertura a<sub>j</sub>, varias llegadas serían demasiado tempranas.)", 'body')

P("b) Verificación del costo declarado", 'h2')
P("El operador declara $260 de distancia, pero el cálculo real es:", 'body')
costo = [["Concepto","Cálculo","Valor"],
 ["Distancia T1 (D→1→3→D)","20 + 25 + 15","60 km"],
 ["Distancia T2 (D→2→4→D)","35 + 15 + 40","90 km"],
 ["Costo de distancia","150 km × $2","$300"],
 ["Costos fijos","$500 (T1) + $400 (T2)","$900"],
 ["Shortage","0 L × $10","$0"],
 ["COSTO TOTAL REAL","","$1.200"]]
tabla([[Paragraph(c, S['body']) for c in r] for r in costo],
      [5.6*cm, 4.6*cm, 3.0*cm])
P("<b>Hay dos errores:</b> (1) la distancia real es $300, no $260 (el operador subestimó 70 km de "
  "costo); y (2) el operador <b>omitió los costos fijos</b> de $900. El costo total real de su "
  "propuesta es <b>$1.200</b>, no $260.", 'body')

P("c) Propuesta de mejora", 'h2')
P("La solución óptima de Tabu Search reduce el costo manteniendo la factibilidad:", 'body')
mej = [["","Operador (corregido)","Óptimo (Tabu Search)"],
 ["Rutas","T1: D→1→3 · T2: D→2→4","T1: D→1→2→4 · T2: D→3"],
 ["Distancia","150 km","115 km"],
 ["Costo distancia","$300","$230"],
 ["Costos fijos","$900","$900"],
 ["Costo total","$1.200","$1.130"],
 ["Factible","No (T2 viola estabilidad)","Sí (todo cumple)"]]
tabla([[Paragraph(c, S['body']) for c in r] for r in mej],
      [3.2*cm, 5.3*cm, 5.3*cm])
callout("Mejora propuesta",
        "Reasignar la estación 2 al camión T1 (ruta <b>D→1→2→4→D</b>) y dejar a T2 solo con la "
        "estación 3 (<b>D→3→D</b>). Esto baja la distancia de 150 a <b>115 km</b> (ahorro de $70 en "
        "distancia), elimina la violación de estabilidad y respeta todas las capacidades y "
        "ventanas. Una alternativa más simple, si se quiere conservar las rutas del operador, es "
        "<b>invertir T2 a D→4→2→D</b> para al menos volver factible la estabilidad.",
        color=VERDE, bg=colors.HexColor("#EAF6EC"))

# ===========================================================================
# 6. PREGUNTA 4
# ===========================================================================
story.append(PageBreak())
P("6. Pregunta 4 — Extensión estocástica (dos etapas)", 'h1')
P("La demanda real es incierta. Se consideran tres escenarios con sus probabilidades. Solo "
  "cambian las demandas de las estaciones 1, 2 (Regular y Diésel) y 3 (Regular); la estación 4 y "
  "el Diésel de la estación 3 se mantienen.", 'body')
esc = [["Escenario","Prob.","Reg. total","Diésel total","Total"],
 ["s1 Normal","0.50","10.500 L","9.000 L","19.500 L"],
 ["s2 Alta","0.30","14.500 L","10.300 L","24.800 L"],
 ["s3 Baja","0.20","7.800 L","7.700 L","15.500 L"]]
tabla([[Paragraph(c, S['body']) for c in r] for r in esc],
      [3.2*cm, 1.8*cm, 3.2*cm, 3.2*cm, 2.8*cm])

P("a) Modelo de dos etapas", 'h2')
P("La idea del modelo estocástico de dos etapas es separar lo que se decide <b>antes</b> de "
  "conocer la demanda de lo que se ajusta <b>después</b>:", 'body')

P("Decisiones de primera etapa (here-and-now, antes de conocer la demanda):", 'h3')
bullets([
 "Qué camiones usar (u<sub>k</sub>) y sus rutas (x<sub>k,i,i'</sub>, y<sub>k,j</sub>).",
 "La asignación de combustible a cada compartimento (z<sub>k,c,p</sub>).",
])
P("Son decisiones \"físicas\" que deben comprometerse antes (no se puede rehacer la ruta cuando el "
  "camión ya salió).", 'note')

P("Decisiones de segunda etapa (recourse, una por escenario s, ya conocida la demanda):", 'h3')
bullets([
 "Cuántos litros cargar/entregar en cada compartimento: l<sub>k,c,s</sub>.",
 "Cuánto faltante se produce en cada estación: gR<sub>j,s</sub>, gD<sub>j,s</sub>.",
])
P("Son los ajustes (\"recourse\") que reaccionan a la demanda realizada de cada escenario.", 'note')

P("¿Cómo cambia la función objetivo?", 'h3')
P("Antes minimizábamos un costo único. Ahora minimizamos el costo de primera etapa <b>más el "
  "valor esperado</b> del costo de segunda etapa (ponderado por las probabilidades p<sub>s</sub>):", 'body')
P("min  cd·Σ d<sub>i,i'</sub> x<sub>k,i,i'</sub> + Σ F<sub>k</sub> u<sub>k</sub>  +  "
  "Σ<sub>s</sub> p<sub>s</sub> · cp · Σ<sub>j</sub> (gR<sub>j,s</sub> + gD<sub>j,s</sub>)", 'formula')

P("¿Qué restricciones son de cada etapa?", 'h3')
bullets([
 "<b>Primera etapa:</b> conservación de flujo, salida del depósito, compatibilidad "
 "compartimento–producto y ventanas de tiempo (dependen solo de las rutas).",
 "<b>Segunda etapa (para cada escenario s):</b> satisfacción de demanda con faltante, capacidad "
 "de los compartimentos y estabilidad Δ=0.30, usando la demanda D<sub>j,p,s</sub> de ese escenario.",
])
callout("Lectura práctica",
        "La flota tiene capacidad de sobra en total (30.000 L), y dedicando un compartimento por "
        "camión a cada producto alcanza hasta 17.000 L de Regular y 13.000 L de Diésel; los tres "
        "escenarios caben (incluso el \"Alto\": 14.500 L de Regular ≤ 17.000 L). Por eso el "
        "modelo de dos etapas fija rutas robustas y solo ajusta cargas/faltantes según el "
        "escenario que ocurra.")

# ===========================================================================
# 7. RESUMEN
# ===========================================================================
story.append(PageBreak())
P("7. Resumen de resultados y archivos", 'h1')
res = [["Pregunta","Resultado principal"],
 ["P1 — Ruteo óptimo","T1: D→1→2→4→D, T2: D→3→D · 115 km · costo total $1.130 (óptimo global verificado)"],
 ["P2 — Scheduling","Makespan = 32.5 min · ambos camiones listos antes de su hora de salida"],
 ["P3 — Solución operador","Infactible (T2 viola estabilidad 30.6%) y costo mal declarado: real $1.200, no $260"],
 ["P3c — Mejora","Reasignar est. 2 a T1 → 115 km, factible, ahorro de $70 en distancia"],
 ["P4 — Estocástico","Modelo de dos etapas: rutas en 1ª etapa, cargas/faltantes como recourse por escenario"]]
tabla([[Paragraph(c, S['body']) for c in r] for r in res],
      [3.6*cm, 12.0*cm])

P("Archivos entregados (repositorio)", 'h2')
bullets([
 "<font face='Courier'>Solemne_Optimizacion.ipynb</font> — notebook que ejecuta todos los cálculos.",
 "<font face='Courier'>modelo.py</font> — datos del enunciado, función objetivo y restricciones.",
 "<font face='Courier'>tabu.py</font> — implementación de la metaheurística Tabu Search.",
 "<font face='Courier'>figuras.py</font> — genera las figuras (rutas, convergencia, Gantt, estabilidad).",
 "<font face='Courier'>Tutorial_Solemne_Optimizacion.pdf</font> — este documento.",
 "<font face='Courier'>figuras/</font> — imágenes usadas en el informe.",
 "<font face='Courier'>README.md</font> — instrucciones para reproducir los resultados.",
])
P("Para reproducir: instalar <font face='Courier'>matplotlib numpy nbformat jupyter</font>, abrir el "
  "notebook y ejecutar todas las celdas. Cada número de este PDF proviene de esa ejecución.", 'note')

# ---------------------------------------------------------------------------
def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(AZUL); canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.4*cm, 19*cm, 1.4*cm)
    canvas.setFont('Helvetica', 8); canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(2*cm, 1.0*cm, "Solemne IA — Optimización · CINF105 · Tabu Search")
    canvas.drawRightString(19*cm, 1.0*cm, f"Página {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate("Tutorial_Solemne_Optimizacion.pdf", pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=2*cm,
                        title="Tutorial Solemne Optimizacion", author="CINF105")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("PDF generado: Tutorial_Solemne_Optimizacion.pdf")
