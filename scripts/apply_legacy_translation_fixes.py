"""Apply the reviewed editorial glossary to legacy bilingual static pages.

The newer homepage, About page and flagship case studies are generated from
structured content and are intentionally excluded here. Chat Matías is also
excluded until its separate editorial pass is complete.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "language-catalog.json"
GENERATED = {"index.html", "caso-1.html", "caso-2.html", "caso-3.html", "caso-daizzy-gear.html", "sobre-mi.html"}

UNCATALOGED_ES_FIXES: dict[str, list[tuple[str, str]]] = {
    "index.html": [
        ("Contactarme", "Hablemos"),
        ("ayudar a marcas de ecommerce a aumentar conversión y rentabilidad", "ayudar a marcas de ecommerce a mejorar su conversión y rentabilidad"),
        ("decisiones comerciales ejecutables", "decisiones comerciales concretas"),
        ("pauta y economics", "pauta y unit economics"),
        ("Una práctica híbrida", "Un perfil híbrido"),
        ("Sin claim causal de conversión", "Sin atribuir un efecto causal en la conversión"),
    ],
    "index-es.html": [
        ("Contactarme", "Hablemos"),
        ("ayudar a marcas de ecommerce a aumentar conversión y rentabilidad", "ayudar a marcas de ecommerce a mejorar su conversión y rentabilidad"),
        ("decisiones comerciales ejecutables", "decisiones comerciales concretas"),
        ("pauta y economics", "pauta y unit economics"),
        ("Una práctica híbrida", "Un perfil híbrido"),
        ("Sin claim causal de conversión", "Sin atribuir un efecto causal en la conversión"),
    ],
    "caso-1.html": [("Contactarme", "Hablemos"), ("contenido y economics", "contenido y rentabilidad")],
    "caso-1-es.html": [("Contactarme", "Hablemos"), ("contenido y economics", "contenido y rentabilidad")],
    "caso-2.html": [("Contactarme", "Hablemos"), ("eficiencia publicitaria y economics", "eficiencia publicitaria y rentabilidad")],
    "caso-2-es.html": [("Contactarme", "Hablemos"), ("eficiencia publicitaria y economics", "eficiencia publicitaria y rentabilidad")],
    "caso-3.html": [("Contactarme", "Hablemos"), ("Sin claim causal de conversión", "Sin atribuir un efecto causal en la conversión")],
    "caso-3-es.html": [("Contactarme", "Hablemos"), ("Sin claim causal de conversión", "Sin atribuir un efecto causal en la conversión")],
    "caso-daizzy-gear.html": [("Contactarme", "Hablemos")],
    "caso-daizzy-gear-es.html": [("Contactarme", "Hablemos")],
    "sobre-mi.html": [("Contactarme", "Hablemos"), ("podemos ordenar el diagnóstico", "podemos ordenar juntos el diagnóstico")],
    "sobre-mi-es.html": [("Contactarme", "Hablemos"), ("podemos ordenar el diagnóstico", "podemos ordenar juntos el diagnóstico")],
    "search-es.html": [("páginas del portfolio", "páginas del portafolio")],
    "404.html": [("Volvé al portfolio", "Volvé al portafolio")],
    "SEO-es.html": [
        ("ChatMatias - Portfolio SEO", "ChatMatias — Portafolio SEO"),
        ("creative strategy portfolio", "estrategia creativa"),
        ("Escribe tu consulta aquí", "Escribí tu consulta acá"),
        ("Escribe términos", "Escribí términos"),
        ("para este portfolio", "para este portafolio"),
    ],
}


COMMON_ES = [
    ("\u200b", ""),
    ("Matías Gaglio — ecommerce, analytics and creative strategy portfolio", "Matías Gaglio — ecommerce, analítica y estrategia creativa"),
    ("Portfolio personal", "Portafolio personal"),
    ("listado Amazon", "listing de Amazon"),
    ("listados Amazon", "listings de Amazon"),
    ("listado de Amazon", "listing de Amazon"),
    ("listados de Amazon", "listings de Amazon"),
    ("Lista de verificación de auditoría de listado", "Lista de verificación para auditar un listing"),
    ("capacidad de descubrimiento", "visibilidad en búsquedas"),
    ("capacidad de búsqueda", "visibilidad en búsquedas"),
    ("unidades abandonadas", "inventario varado"),
    ("tasa de retorno", "tasa de devoluciones"),
    ("rendimientos crecientes", "aumento de las devoluciones"),
    ("porcentaje de impresiones", "cuota de impresiones"),
    ("adiciones al carrito", "agregados al carrito"),
    ("tipo de coincidencia", "tipo de concordancia"),
    ("métricas de acciones", "métricas de participación"),
    ("métricas de acción", "métricas de participación"),
    ("recorrido por el panel", "recorrido por el dashboard"),
    ("el cuota de impresiones", "la cuota de impresiones"),
    ("activos creativos", "piezas creativas"),
    ("activos de listado", "piezas del listing"),
    ("soportes visuales", "recursos visuales"),
    ("línea de base", "línea base"),
    ("sólo", "solo"),
]

COMMON_EN = [
    ("\u200b", ""),
    ("Does Amazon understand when this product belongs?", "Does Amazon understand where this product belongs?"),
    ("Medical Sales Representative", "Pharmaceutical Sales Representative"),
]


PAGE_FIXES: dict[str, dict[str, list[tuple[str, str]]]] = {
    "Cases/DayParting-Case.html": {
        "es": [
            ("Caso de separación del día", "Caso de Dayparting"),
            ("La cuenta no era débil. El momento fue ineficiente.", "La cuenta no tenía un problema de demanda. El gasto se concentraba en horarios ineficientes."),
            ("El problema empresarial escondido dentro de un promedio diario", "El problema de negocio oculto dentro de un promedio diario"),
            ("Por qué la división horaria puede mejorar la eficiencia del PPC", "Por qué el dayparting puede mejorar la eficiencia de PPC"),
            ("De los informes horarios a la asignación presupuestaria", "De los reportes por hora a la asignación de presupuesto"),
            ("La división diaria es una asignación dinámica de cartera", "El dayparting es una asignación dinámica de presupuesto"),
            ("división horaria", "programación horaria"),
            ("división diaria", "dayparting"),
        ]
    },
    "Cases/amazon-listing-audit-checklist.html": {
        "es": [
            ("No optimice la copia visible antes de demostrar que el anuncio se puede vender.", "No optimices el contenido visible antes de comprobar que el listing está en condiciones de vender."),
            ("¿Puede el comprador realmente completar la compra?", "¿El comprador puede completar la compra?"),
            ("Estado del listado", "Estado del listing"),
            ("Compra Caja y oferta", "Buy Box y oferta"),
            ("Integridad de la variación", "Integridad de las variaciones"),
            ("¿Amazon entiende a qué pertenece este producto?", "¿Amazon entiende en qué categoría y contexto debe aparecer este producto?"),
            ("Cobertura de bala", "Cobertura de bullets"),
            ("Backend e indexación", "Términos de backend e indexación"),
            ("Impresiones abajo", "Caída de impresiones"),
            ("Clics hacia abajo", "Caída de clics"),
            ("Conversión baja", "Caída de conversión"),
            ("Bajada de beneficios", "Caída de rentabilidad"),
            ("Una alerta de margen requería una conciliación, no una reescritura de la copia.", "Una alerta de margen exigía conciliar los datos, no reescribir el contenido."),
            ("Convierta los hallazgos en un registro de cambios priorizados.", "Convierte los hallazgos en un registro de cambios priorizado."),
            ("Siga la cadena de dependencia antes de puntuar la creatividad.", "Sigue la cadena de dependencias antes de evaluar el contenido creativo."),
            ("Eliminar los obstáculos que impiden la preparación para el comercio minorista", "Eliminar los bloqueos de retail readiness"),
            ("Conciliar rendimiento y economía", "Conciliar rendimiento y rentabilidad"),
            ("Lo que la evidencia disponible puede (y no puede) eliminar.", "Lo que la evidencia disponible permite concluir (y lo que no)."),
            ("Documento</h3>", "Documentar</h3>"),
            ("priorizar</h3>", "Priorizar</h3>"),
            ("Medida</h3>", "Medir</h3>"),
            ("mandatos prioritarios", "términos prioritarios"),
            ("cargos patrocinados", "posiciones patrocinadas"),
            ("Evidencia de auditoría anónima", "Evidencia de una auditoría anonimizada"),
            ("eran irrelevantes", "no eran materiales"),
            ("Los retornos no explicaron", "Las devoluciones no explicaron"),
            ("altos posiciones patrocinadas", "posiciones patrocinadas destacadas"),
            ("cambios selectivos de ofertas", "cambios selectivos de pujas"),
            ("<th>lo que debilita</th>", "<th>Lo que debilita</th>"),
            ("Próximo cheque", "Próxima verificación"),
            ("Puente de aportación", "Puente de margen de contribución"),
            ("Los aumento de las devoluciones", "El aumento de las devoluciones"),
            ("cambio en la cuota de impresiones", "cambio en la cuota de impresiones"),
            ("búsquedas compartidas", "cuota de búsquedas"),
            ("Combinación de ubicación", "Mix de ubicaciones"),
            ("Opinión sobre reseñas", "Sentimiento de las reseñas"),
            ("puente de aportación", "puente de margen de contribución"),
            ("la copia visible", "el contenido visible"),
            ("reescritura de la copia", "reescritura del contenido"),
            ("las inventario varado", "el inventario varado"),
            ("Copia de galería duplicada", "Contenido de galería duplicado"),
            ("revisiones críticas", "reseñas críticas"),
            ("La cotización promete", "El listing promete"),
            ("<td>oferta competitiva</td>", "<td>Oferta competitiva</td>"),
            ("el porcentaje de búsqueda", "la cuota de búsqueda"),
            ("un evento bursátil", "un evento de stock"),
            ("el niño exacto", "el ASIN hijo correcto"),
            ("Preservar componentes", "Preserve los componentes"),
            ("Nombra una barrera", "Nombre un criterio de control"),
            ("las métricas de la barrera de seguridad", "las métricas de control"),
            ("barreras de seguridad", "criterios de control"),
            ("la creatividad actual", "las piezas creativas actuales"),
            ("una variación incumplida", "una variación mal configurada"),
            ("Preparación para el comercio minorista", "Retail readiness"),
            ("preparación para la venta minorista", "retail readiness"),
        ]
    },
    "Cases/automotive-fitment-seo.html": {
        "es": [
            ("SEO de compatibilidad para publicaciones automotrices en Amazon", "SEO de compatibilidad para listings automotrices en Amazon"),
            ("Evidencia real de compatibilidad adyacente, no una carcasa automotriz fabricada.", "Evidencia real de un producto automotriz comparable, no un caso inventado."),
            ("El lenguaje variante correspondía a un comportamiento de campaña materialmente diferente.", "Las variantes de lenguaje mostraban comportamientos de campaña claramente diferentes."),
            ("Costo publicitario de las ventas.", "Costo publicitario sobre ventas"),
            ("Cree el registro de compatibilidad en capas para que se pueda rastrear cada reclamo.", "Construye el registro de compatibilidad por capas para poder rastrear cada afirmación."),
            ("Almacene una decisión, su motivo y su fuente, no solo una cadena de palabras clave.", "Registra la decisión, el motivo y la fuente; no guardes solo una cadena de palabras clave."),
            ("Pase de una especificación sin formato a un listing con visibilidad en búsquedas en una secuencia controlada.", "Pasa de una especificación sin procesar a un listing visible en búsquedas mediante una secuencia controlada."),
            ("Pase de una especificación sin formato a un listado con visibilidad en búsquedas en una secuencia controlada.", "Pasa de una especificación sin procesar a un listing visible en búsquedas mediante una secuencia controlada."),
            ("Normalizar la especificación", "Normaliza la especificación"),
            ("Normalice los registros", "Normaliza los registros"),
            ("Une el contexto", "Conecta el contexto"),
            ("Escriba un texto fácil de encontrar dentro de los límites del reclamo aprobado.", "Redacta contenido fácil de encontrar dentro de los límites de las afirmaciones aprobadas."),
            ("Mida la calidad después del lanzamiento, no solo la visibilidad.", "Mide la calidad después del lanzamiento, no solo la visibilidad."),
            ("Asigne un trabajo a cada elemento del listado.", "Asigna una función a cada elemento del listing."),
            ("Identifique la pieza y la especificación decisiva.", "Identifica la pieza y la especificación decisiva."),
            ("Ayude al comprador a verificar la interfaz.", "Ayuda al comprador a verificar la interfaz."),
            ("Mostrar puntos de referencia de geometría y medición.", "Muestra referencias de geometría y medición."),
            ("Capture sinónimos sin inventar compatibilidad.", "Incorpora sinónimos sin inventar compatibilidad."),
            ("Diseñe comprobaciones sobre las formas más costosas en las que los datos pueden estar equivocados.", "Diseña controles para los errores de datos más costosos."),
            ("Evalúe juntos el descubrimiento cualificado y la calidad de las decisiones.", "Evalúa en conjunto el descubrimiento cualificado y la calidad de la decisión."),
            ("Lo observado, calculado, ilustrativo y documentado externamente.", "Qué se observó, qué se calculó, qué es ilustrativo y qué se documentó con fuentes externas."),
            ("convertir el movimiento en un reclamo causal", "convertir el movimiento en una afirmación causal"),
            ("reclamos", "afirmaciones"),
            ("reclamo", "afirmación"),
        ]
    },
    "Cases/market-share-loss-diagnosis.html": {
        "es": [
            ("Los ingresos son un resultado. No es un diagnóstico.", "Los ingresos son un resultado, no un diagnóstico."),
            ("Localiza la ruptura antes de explicarla.", "Localiza el punto de quiebre antes de explicarlo."),
            ("Una caída del 50% con clasificación estable y rendimientos mejorados", "Una caída del 50% con ranking estable y una menor tasa de devoluciones"),
            ("Una caída del 50% con ranking estable y mejores devoluciones", "Una caída del 50% con ranking estable y una menor tasa de devoluciones"),
            ("Las métricas de participación cuentan una historia diferente en cada etapa del embudo.", "Las métricas de participación cuentan una historia distinta en cada etapa del embudo."),
            ("Cuota de marca ponderada por etapa del embudo de mercado", "Cuota de marca ponderada por etapa del embudo"),
            ("Termine con una explicación clasificada, no con un recorrido por el dashboard.", "Termina con hipótesis priorizadas, no con un recorrido por el dashboard."),
            ("Pasar del síntoma al mecanismo en un orden fijo.", "Del síntoma al mecanismo, en un orden fijo."),
            ("Ciencias económicas", "Rentabilidad"),
            ("el cuota de impresiones", "la cuota de impresiones"),
            ("barandilla", "criterio de control"),
            ("echarle la culpa a la calidad del contenido o a la rentabilidad", "atribuirla a la calidad del contenido o a la tasa de devoluciones"),
            ("interrupción del stock de material", "interrupción relevante de stock"),
            ("No admitido durante el período revisado.", "No respaldado para el período revisado."),
            ("Choque de tarifas", "Aumento abrupto de tarifas"),
            ("Los retornos se movieron", "Las devoluciones se movieron"),
            ("altos cargos patrocinados", "posiciones patrocinadas destacadas"),
            ("reducir o eliminar la oferta", "reducir o eliminar la puja"),
            ("1. Defina la comparación antes de leer el delta.", "1. Definir la comparación antes de interpretar la variación."),
            ("2. Separar el volumen de la economía unitaria.", "2. Separar el volumen de la rentabilidad por unidad."),
            ("3. Pruebe primero las pausas operativas estrictas.", "3. Comprobar primero los bloqueos operativos."),
            ("4. Lea las acciones del embudo de arriba a abajo.", "4. Leer las cuotas del embudo de arriba abajo."),
            ("5. Clasifique las explicaciones según su confianza.", "5. Clasificar las explicaciones según el nivel de confianza."),
            ("\"No admitido\" no significa \"imposible\"", "\"No respaldado\" no significa \"imposible\""),
            ("La exportación separada de la visión de marca", "La exportación separada de Brand View"),
            ("El cuota de impresiones ponderado", "La cuota de impresiones ponderada"),
            ("La participación de compras", "La cuota de compras"),
            ("El aumento dla cuota de impresiones a compras", "El aumento entre la cuota de impresiones y la cuota de compras"),
            ("cuando la cuota de impresiones es mayor que el de impresiones", "cuando la cuota de compras es mayor que la cuota de impresiones"),
            ("Las posiciones estables de las palabras clave muestreadas determinan una historia amplia de colapso de la clasificación", "Las posiciones estables de las keywords muestreadas debilitan una explicación basada en un colapso general del ranking"),
            ("La mejora de los retornos", "La mejora de las devoluciones"),
            ("toda la cartera de consultas", "todo el conjunto de consultas"),
            ("pérdida de participación de mercado Amazon", "pérdida de participación en el mercado de Amazon"),
            ("proteja los activos de conversión", "proteja las piezas orientadas a la conversión"),
            ("<small>Ganancia</small>", "<small>Ingresos</small>"),
            ("<small>Tasa de retorno</small>", "<small>Tasa de devoluciones</small>"),
            ("-50.1%", "-50,1%"),
            ("-63.6%", "-63,6%"),
            ("1.05% → 0.63%", "1,05% → 0,63%"),
            ("Mejorado durante el declive", "Mejoró durante la caída"),
            ("Anota promociones", "Anote promociones"),
            ("asigne un propietario", "asigne un responsable"),
            ("la criterio de control", "el criterio de control"),
            ("etiquetas: admitido, descartado", "etiquetas: respaldado, descartado"),
            ("economía se debilitó", "rentabilidad se deterioró"),
            ("una narrativa segura", "una conclusión tajante"),
        ]
    },
    "Cases/search-query-keyword-harvesting.html": {
        "es": [
            ("Rendimiento de consultas de búsqueda y recolección de palabras clave", "Rendimiento de consultas y keyword harvesting"),
            ("Un término de búsqueda es una evidencia, no automáticamente una palabra clave.", "Un término de búsqueda es evidencia; no se convierte automáticamente en keyword."),
            ("La marca ganó participación a medida que los compradores se adentraban más en el embudo.", "La marca ganó participación a medida que los compradores avanzaban en el embudo."),
            ("La cola larga consumió la mayor parte del gasto probado sin pedidos", "La long tail concentró la mayor parte del gasto observado sin pedidos"),
            ("Recolectar</h3>", "Seleccionar</h3>"),
            ("Promover</h3>", "Promocionar</h3>"),
            ("La recolección es un circuito cerrado, no una tarea de limpieza", "El keyword harvesting es un circuito cerrado, no una tarea de limpieza"),
            ("El objetivo no es más palabras clave. Es mejor propiedad de la consulta.", "El objetivo no es sumar keywords, sino controlar mejor cada consulta."),
            ("Promocionar solo cuando el control agregue valor", "Promociona solo cuando el control aporte valor"),
            ("Una decisión de consulta debe dejar un rastro de auditoría.", "Cada decisión sobre una consulta debe dejar un rastro de auditoría."),
            ("Gastar sin orden", "Gasto sin pedidos"),
            ("ofertas", "pujas"),
            (">Barandilla<", ">Criterio de control<"),
            ("Ofrezca a un término probado una oferta independiente y una medición limpia.", "Asigna a un término probado una puja propia y una medición clara."),
            ("La frase puede derivar.", "La concordancia de frase puede ampliar demasiado la intención."),
            ("Explore el idioma y la demanda adyacente", "Explora el lenguaje y la demanda adyacente"),
            ("Ciencias económicas", "Rentabilidad"),
            ("Establezca umbrales a partir de la conversión del punto de equilibrio, no del hábito", "Define umbrales a partir de la conversión de equilibrio, no de la costumbre"),
            ("Aprendizaje de orientación amplio y automático; se distinguen estructuras exactas y sintagmáticas; los negativos evitan el desperdicio y la superposición; Los informes de rendimiento de consultas revelan si las ganancias publicitarias se están traduciendo en una presencia más sólida en el mercado.", "Las campañas automáticas y amplias sostienen el descubrimiento; las estructuras de concordancia exacta y de frase aíslan términos valiosos; las negativas reducen desperdicio y solapamiento; y Search Query Performance muestra si las mejoras publicitarias se traducen en una presencia más sólida en el mercado."),
            ("Es una cartera en la que", "Es un portafolio en el que"),
            ("porcentaje de impresiones bajo, porcentaje de compras más fuerte", "cuota de impresiones baja y cuota de compras más sólida"),
            ("debilitar las barandillas", "debilitar los criterios de control"),
            ("plazo de descubrimiento", "término de descubrimiento"),
            ("La decisión de cosecha", "La decisión de selección"),
            ("Flujo de trabajo de cosecha", "Flujo de keyword harvesting"),
            ("Puntuación de cosecha", "Puntuación de selección"),
            ("Un sistema de recolección maduro", "Un sistema maduro de keyword harvesting"),
            ("La participación increasing", "El aumento de la participación"),
            ("Carrito añade", "Agregados al carrito"),
            ("DÓLAR ESTADOUNIDENSE;", "Importes en dólares estadounidenses ·"),
            ("Condiciones con pedidos", "Términos con pedidos"),
            ("términos sin orden observado", "términos sin pedidos observados"),
            ("términos sin orden son", "términos sin pedidos representan"),
            ("diez clics sin una orden", "diez clics sin un pedido"),
            ("una tasa de conversión de clic para realizar pedidos", "una tasa de conversión de clic a pedido"),
            ("La conversión de clic para ordenar", "La conversión de clic a pedido"),
            ("Cada ratio", "Cada proporción"),
            ("una lógica de oferta y presupuesto", "una lógica de puja y presupuesto"),
            ("una oferta, un contexto presupuestario", "una puja, un contexto presupuestario"),
            ("con una oferta cautelosa", "con una puja cautelosa"),
            ("oferta reducida", "puja reducida"),
            ("Reducir la oferta", "Reducir la puja"),
            ("El tipo de concordancia debe expresar confianza y control", "El tipo de concordancia debe reflejar el nivel de confianza y control"),
            ("Implicación de decisión:</strong> descubrimiento, asignación y exclusión separados.", "Implicación de decisión:</strong> conviene separar el descubrimiento, la asignación y la exclusión."),
            ("una fórmula universal Amazon", "una fórmula universal para Amazon"),
            ("Muestra de visualización de marca", "Muestra de Brand Analytics"),
        ]
    },
    "Cases/search-suppression-catalog-recovery.html": {
        "es": [
            ("Exposición comercial real, sin reclamo de recuperación inventado.", "Evidencia comercial real, sin afirmar una recuperación no demostrada."),
            ("¿Amazon aceptó la entrada del listing?", "¿Amazon aceptó los datos del listing?"),
            ("Lea el resultado del procesamiento, no solo la confirmación de la carga.", "Revisa el resultado del procesamiento, no solo la confirmación de carga."),
            ("Relaciona el síntoma con la evidencia que puede refutarlo.", "Relaciona cada síntoma con la evidencia que podría refutarlo."),
            ("Cero impresiones no se suprime automáticamente.", "Cero impresiones no implica automáticamente una supresión."),
            ("Una presentación aceptada no es una aceptación final.", "Un envío aceptado no equivale a una aceptación final."),
            ("Lo que se observa, se deriva y se documenta externamente.", "Qué se observó, qué se calculó y qué se documentó con fuentes externas."),
            ("reclamo de recuperación", "afirmación de recuperación"),
            ("una cotización suprimida", "un listing suprimido"),
        ]
    },
    "Cases/voice-of-customer-conversion-brief.html": {
        "es": [
            ("Voz del cliente al resumen de conversión", "De la voz del cliente a un brief de conversión"),
            ("Del ruido de revisión a un <em>resumen de conversión.</em>", "Del ruido de las reseñas a un <em>brief de conversión.</em>"),
            ("Resultado deseado versus fricción de conversión.", "Resultado deseado frente a fricción de conversión."),
            ("Agrupar el idioma", "Agrupar el lenguaje"),
            ("Fricción en la decisión de rango", "Priorizar la fricción en la decisión"),
            ("Asigne cada reclamo a un marco", "Asigna cada afirmación a una pieza"),
            ("El resumen creativo", "El brief creativo"),
            ("Reclamo a prueba", "De la afirmación a la evidencia"),
            ("Revisar la minería encuentra preguntas. No fabrica pruebas.", "El análisis de reseñas revela preguntas. No fabrica pruebas."),
            ("Cómo las menciones codificadas se convierten en un escrito defendible.", "Cómo convertir menciones codificadas en un brief defendible."),
            ("Mantenga las mesas más pequeñas direccionales", "Trata las muestras pequeñas como indicios"),
            ("Ejecute cada informe de voz del cliente a través de seis puertas.", "Evalúa cada informe de voz del cliente con seis criterios."),
            ("reclamo", "afirmación"),
            ("reclamos", "afirmaciones"),
            ("retornos", "devoluciones"),
            ("barrera contra expectativas engañosas", "control para evitar expectativas engañosas"),
        ]
    },
    "Revolution_creative_case.html": {
        "es": [
            ("Estudio de caso de actualización de listing de Amazon", "Caso de rediseño de listings de Amazon"),
            ("Reconstrucción de listings de Amazon mediante sistemas visuales, estructura de SEO y contenido centrado en la conversión", "Reconstrucción de listings de Amazon mediante sistemas visuales, arquitectura SEO y contenido orientado a conversión"),
            ("experiencia de cotización", "experiencia del listing"),
            ("cotización que podía indexarse", "listing que Amazon podía indexar"),
            ("toma de decisiones del Amazon", "toma de decisiones en Amazon"),
            ("Lógica de copia antigua", "Lógica del contenido anterior"),
            ("Nueva lógica de copia", "Nueva lógica de contenido"),
            ("más allá de las balas", "más allá de los bullets"),
            ("una lista más sólida", "un listing más sólido"),
            ("la lista fuera más legible", "el listing fuera más legible"),
            ("sistema de listing combinado", "sistema combinado del listing"),
            ("Habilidades demostradas en este proyecto.", "Habilidades demostradas en este proyecto"),
            ("control deslizante", "comparador interactivo"),
            ("una listing que Amazon podía indexar por Amazon", "un listing que Amazon podía indexar"),
            ("Codificación de tareas de producción repetidas automatizadas", "La automatización estandarizó tareas de producción repetitivas"),
            ("los piezas del listing", "las piezas del listing"),
            ("Las balas posteriores", "Los bullets siguientes"),
            ("cotización anterior", "listing anterior"),
            ("mejoras de cotización", "mejoras del listing"),
            ("período de cotización", "período del listing"),
            ("estilo antiguo", "versión anterior"),
            ("Nuevo estilo", "Versión nueva"),
            ("visita la tienda", "Visitá la tienda"),
            ("añadir a la cesta", "Agregar al carrito"),
            ("POSVENCIÓN", "POSVENTA"),
            ("posvención", "posventa"),
            ("Amazon Confirm Fit", "Amazon Confirmed Fit"),
            ("AMAZON CONFIRM FIT", "AMAZON CONFIRMED FIT"),
            ("Chevrolet 2002-13 Avalancha", "Chevrolet Avalanche 2002-13"),
            ("1991+ Chaqueta", "Blazer 1991+"),
            ("2015+ Cañón", "Canyon 2015+"),
            ("1992+ Yukón", "Yukon 1992+"),
            ("Perspectivas de Saturno 2007-10", "Saturn Outlook 2007-10"),
            ("Navegador Lincoln", "Lincoln Navigator"),
            ("Hilos precisos de alta calidad", "Roscas de alta precisión"),
            ("Sólo para ruedas de repuesto", "Solo para ruedas de posventa"),
            ("Calificación de muestra", "Valoración de muestra"),
            ("un listado", "un listing"),
            ("los listados", "los listings"),
            ("del listado", "del listing"),
            ("de listado", "del listing"),
            ("la lista", "el listing"),
            ("análisis del listings competitivos", "análisis de listings competitivos"),
        ]
    },
    "BI-case-2.html": {
        "es": [
            ("Estudio de caso de crecimiento de BI Marketplace", "Caso de Business Intelligence para el crecimiento en marketplaces"),
            ("crecimiento del mercado Amazon", "crecimiento en Amazon"),
            ("inteligencia empresarial", "Business Intelligence"),
            ("calidad de listado", "calidad del listing"),
            ("+26.3%", "+26,3%"),
            ("+119.4%", "+119,4%"),
            ("+19.4%", "+19,4%"),
            ("+5.5%", "+5,5%"),
            ("El tráfico Increasing es fácil", "Aumentar el tráfico es fácil"),
            ("La portafolio", "El portafolio"),
            ("la portafolio", "el portafolio"),
            ("el resto de la portafolio", "el resto del portafolio"),
            ("la cuenta podría evaluarse", "la cuenta podía evaluarse"),
            ("propiedad de palabras clave", "control de keywords"),
            ("Propiedad de palabras clave", "Control de keywords"),
            ("administrar y escalar", "gestionar y escalar"),
            ("Tasa de conversión versus tasa de reembolso", "Tasa de conversión frente a tasa de devoluciones"),
            ("tasa de reembolso disminuye", "tasa de devoluciones disminuye"),
            ("presión de reembolso", "presión de las devoluciones"),
            (">Contáctame<", ">Hablemos<"),
            ("Creación de un sistema de crecimiento Marketplace para una cartera técnica de automoción", "Sistema de crecimiento para un portafolio técnico del sector automotriz"),
            ("escala minorista", "escala de ventas retail"),
            ("Índice de ventas y tasa de conversión", "Ventas indexadas y tasa de conversión"),
            ("Índice de impulsores del crecimiento", "Índice de factores de crecimiento"),
            ("Cambio medido KPI", "Variación medida de KPI"),
            ("Exacto</h3>", "Concordancia exacta</h3>"),
            ("Frase</h3>", "Concordancia de frase</h3>"),
            ("Amplio</h3>", "Concordancia amplia</h3>"),
            ("Instantánea del anuncio", "Captura publicitaria"),
            ("Trayectoria en el ranking de mejor vendedor", "Evolución del Best Sellers Rank"),
            ("Propiedad de la palabra clave", "Control de keywords"),
            ("Buscar señales de demanda", "Señales de demanda en búsquedas"),
            ("Ruta de defensa de palabras clave", "Ruta de defensa de keywords"),
            ("automoción", "sector automotriz"),
            ("cartera", "portafolio"),
            ("recolección de términos de búsqueda", "selección de términos de búsqueda"),
            ("Retail sales index", "Índice de ventas retail"),
            ("Ad spend index", "Índice de inversión publicitaria"),
            ("Est. profit index", "Índice de beneficio estimado"),
            ("Conversion rate index", "Índice de tasa de conversión"),
            ("Keyword ownership %", "Control de keywords %"),
            ("label:'Before'", "label:'Antes'"),
            ("label:'After'", "label:'Después'"),
            ("labels:['Our Brand','Competition','Other']", "labels:['Nuestra marca','Competencia','Otros']"),
            ("labels:['Our Brand','Competition']", "labels:['Nuestra marca','Competencia']"),
        ]
    },
    "animation-01.html": {"es": [("Hacer que la luz parezca dimensional.", "Construir profundidad con luz."), ("Plataforma de capa de forma", "Sistema de capas de forma")]},
    "animation-02.html": {"es": [("flujo del sistema del centro de menús", "flujo del sistema Menu Hub"), ("acabado CRT", "Acabado CRT")]},
    "animation-03.html": {"es": [("Sé tú · Tipo cinético", "Be You · Tipografía cinética"), ("Tipo de construcción", "Construcción tipográfica"), ("animadores de texto", "Animadores de texto"), ("la transición", "La transición"), ("Espacio negativo y mantener", "Espacio negativo y pausa"), ("Después de los efectos", "After Effects"), ("Selectores", "Selectores")]},
    "animation-04.html": {"es": [("Volumen de dibujo con una sola línea en movimiento.", "Dibujar volumen con una sola línea en movimiento."), ("Camino y revelación", "Trayectoria y revelado")]},
    "ecommerce-video-01.html": {"es": [("Desde la característica del producto hasta el motivo de compra.", "De la característica del producto a una razón de compra.")]},
    "ecommerce-video-02.html": {"es": [("Hacer que un reclamo parezca creíble.", "Convertir una afirmación en evidencia creíble.")]},
    "ecommerce-video-04.html": {"es": [("Poniendo la portabilidad en contexto.", "Mostrar la portabilidad en contexto.")]},
    "ecommerce-video-05.html": {"es": [("Convertir el tacto en evidencia visual.", "Hacer visible la sensación del material.")]},
    "ecommerce-video-case.html": {"es": [
        ("Convierta las afirmaciones en pruebas", "Convierte las afirmaciones en evidencia"),
        ("Doblar. Almacenar. Sigue moviéndote.", "Plegar. Guardar. Seguir avanzando."),
        ("como activos de conversión en lugar de contenido pasivo", "como piezas orientadas a la conversión, no como contenido pasivo"),
        ("vídeos centrados", "videos centrados"),
        ("formato listo para el mercado", "formato listo para marketplaces"),
    ]},
    "consultora.html": {
        "es": [("Pulso de laopinión pública", "Pulso de la opinión pública"), ("balance neto", "Balance neto"), ("El meme deMilei Chad", "El meme de Milei Chad"), ("De entender una audienciaa construir una campaña", "De entender una audiencia a construir una campaña")],
        "en": [("Pulse of the public opinion", "Public Opinion Pulse"), ("Pulse of public opinion", "Public Opinion Pulse"), ("Pulse of thepublic opinion", "Public Opinion Pulse"), ("The wear and tear is not only presidential", "The decline extends beyond the president"), ("Karina Milei's net worth", "Karina Milei's net image balance"), ("His negative image reaches", "Her negative image reaches"), ("To understand an audience to build a campaign", "From understanding an audience to building a campaign"), ("To understand an audienceto build a campaign", "From understanding an audience to building a campaign"), ("the meme of Milei Chad", "The Milei Chad Meme"), ("the meme ofMilei Chad", "The Milei Chad Meme")],
    },
    "otros.html": {"en": [("Work lines", "Areas of work"), ("Are you interested in any?", "Interested in one of these projects?")]},
    "creatives.html": {"es": [
        ("Variety of Pills", "Variedad de comprimidos"),
        ("¿Querés ver un caso completo?", "¿Querés ver un caso de estudio completo?"),
        ("View Animation 02: Menu Hub system flow", "Ver Animación 02: flujo del sistema Menu Hub"),
        ("View Animation 03: Be You kinetic typography", "Ver Animación 03: tipografía cinética Be You"),
    ], "en": [("Do you want to see a complete case?", "Want to see a full case study?")]},
    "caso-hogar-cocina-ppc.html": {
        "es": [
            ("Caso de Estudio Hogar y Cocina - Escalamiento de PPC", "Caso de estudio Hogar y Cocina · Escalado de PPC"),
            ("Hogar y Cocina: Estrategia Integral de Escalamiento de PPC en Junio", "Hogar y Cocina: estrategia integral de escalado de PPC en junio"),
            ("Pago Por Clic", "pago por clic"),
            ("optimización continua del listado", "optimización continua del listing"),
            ("Resumen de Rendimiento", "Resumen de rendimiento"),
            ("Resultados Comerciales de Alto Nivel", "Resultados comerciales destacados"),
            ("Ventas de Productos Ordenados", "Ventas de productos pedidos"),
            ("Unidades Ordenadas", "Unidades pedidas"),
            ("ACOS Mantenido", "ACOS mantenido"),
            ("TACoS Alcanzado", "TACoS alcanzado"),
            ("Ejecución Estratégica", "Ejecución estratégica"),
            ("Preparación para Prime Day y Segmentación Avanzada", "Preparación para Prime Day y segmentación avanzada"),
            ("Arquitectura del Catálogo", "Arquitectura del catálogo"),
            ("Mejora de BSR y Estrategias de Variaciones", "Mejora del BSR y estrategia de variaciones"),
            ("Rango de los Más Vendidos (BSR)", "Best Sellers Rank (BSR)"),
            ("Expansión de Margen Impulsada", "Expansión del margen"),
            ("Crecimiento de BSR", "Mejora del BSR"),
            ("Eficiencia de Capital", "Eficiencia del capital"),
            ("Optimización de Conversión", "Optimización de la conversión"),
            ("Análisis de Mercado y Refinamientos de Listados", "Análisis de mercado y mejoras de listings"),
            ("imágenes principales del listado", "imágenes principales del listing"),
            ("la interfaz del listado", "la experiencia del listing"),
            ("dentro del mercado", "dentro del marketplace"),
            ("Volver al Portafolio de Ecommerce", "Volver al portafolio de ecommerce"),
            ("Portafolio Profesional", "Portafolio profesional"),
        ],
        "en": [("PPC Upscaling with TACoS Upgrade", "PPC Scaling with Improved TACoS"), ("Sales of Ordered Products", "Ordered Product Sales"), ("Home and Kitchen: Comprehensive Scaling Strategy for PPC in June", "Home & Kitchen: June PPC Scaling Strategy")]
    },
    "amazon-lifecycle-operating-system.html": {"es": [
        ("Un listing no se lanza.<br>Se opera.", "Un listing no solo se lanza.<br>Se gestiona."),
        ("Cuando cae revenue", "Cuando caen los ingresos"),
        ("Monthly diagnostic", "Diagnóstico mensual"),
        (">Revenue<", ">Ingresos<"),
        ("Revenue is driven by visibility, conversion and price", "Los ingresos dependen de la visibilidad, la conversión y el precio"),
        ("Amazon Operations · Product Lifecycle · Growth System", "Operaciones de Amazon · Ciclo de vida del producto · Sistema de crecimiento"),
        ("desde pre-launch hasta madurez", "desde la preparación hasta la madurez"),
        ("Operating model", "Modelo operativo"),
        (">Pre-launch<", ">Preparación<"),
        (">Launch<", ">Lanzamiento<"),
        (">Growth<", ">Crecimiento<"),
        (">Maturity<", ">Madurez<"),
        ("keyword research", "investigación de keywords"),
        ("Retail readiness", "Preparación comercial"),
        ("Ranking", "Ranking"),
        ("rank y señales", "ranking y señales"),
        (">Harvesting<", ">Selección de keywords<"),
        ("Forecast de inventario", "Pronóstico de inventario"),
        ("Impression share", "Cuota de impresiones"),
        ("Conversion rate", "Tasa de conversión"),
        ("Launch gates", "Criterios de lanzamiento"),
        (">Identity<", ">Identidad<"),
        (">Relevance<", ">Relevancia<"),
        (">Conversion<", ">Conversión<"),
        (">Economics<", ">Rentabilidad<"),
        (">Operations<", ">Operaciones<"),
        (">Measurement<", ">Medición<"),
        ("fees, landed cost y margen", "comisiones, landed cost y margen"),
        ("Trackers y responsables definidos antes del go-live", "Tableros de seguimiento y responsables definidos antes de publicar"),
        ("impresión compartida", "cuota de impresiones"),
        ("reviews, competencia", "reseñas, competencia"),
        ("fees, pauta", "comisiones, pauta"),
        ("Closed-loop learning", "Aprendizaje de ciclo cerrado"),
        ("más checklists", "más listas de control"),
        ("un buen revenue", "un buen nivel de ingresos"),
    ]},
    "amazon-content-architecture.html": {"es": [
        ("Una secuencia, no una colección de assets.", "Una secuencia, no una colección de piezas."),
        ("De keyword a confianza", "De la keyword a la confianza"),
        ("Gallery narrative", "Narrativa de galería"),
        (">Recognition<", ">Reconocimiento<"),
        (">Primary outcome<", ">Resultado principal<"),
        (">Mechanism<", ">Mecanismo<"),
        (">Fit &amp; scale<", ">Compatibilidad y escala<"),
        (">Objection<", ">Objeción<"),
        (">Decision<", ">Decisión<"),
        ("Message ownership", "Responsabilidad del mensaje"),
        ("Amazon Content · Conversion Design · Information Architecture", "Contenido para Amazon · Diseño para conversión · Arquitectura de la información"),
        ("The content stack", "La arquitectura de contenido"),
        ("el mismo claim repetido", "la misma promesa repetida"),
        ("Five layers", "Cinco capas"),
        ("01 · Discovery", "01 · Descubrimiento"),
        ("02 · Orientation", "02 · Orientación"),
        ("03 · Evidence", "03 · Evidencia"),
        ("04 · Understanding", "04 · Comprensión"),
        ("05 · Confidence", "05 · Confianza"),
        ("uso, escala, fit, mecanismos", "uso, escala, compatibilidad y mecanismos"),
        ("primer viewport", "primer pantallazo"),
        ("sin claims vacíos", "sin promesas vacías"),
        ("Keyword stuffing", "Acumulación de keywords"),
        ("Slideshow redundante", "Carrusel redundante"),
        ("Measurement loop", "Ciclo de medición"),
        ("queries, reviews", "consultas, reseñas"),
        ("copy, imagen", "texto, imagen"),
    ]},
    "shulex-voc-creative-case.html": {"es": [
        ("Estos assets históricos", "Estas piezas históricas"),
        ("Macrocultivo", "Detalle macro"),
        ("VOC encuentra la pregunta. No prueba la respuesta.", "VOC revela la pregunta. No demuestra la respuesta."),
        ("El desempeño creativo", "El rendimiento creativo"),
        ("Aclaración del portfolio", "Aclaración del portafolio"),
        ("La estrategia le dio un trabajo", "La estrategia le asignó una función"),
        ("Agrupe el lenguaje de revisión", "Agrupá el lenguaje de las reseñas"),
        ("Compare los elogios recurrentes", "Compará los elogios recurrentes"),
        ("tensiones en las decisiones", "tensiones de decisión"),
        ("Convierta cada tensión en un trabajo de imagen", "Convertí cada tensión en una función para la imagen"),
        ("demuestre el agarre, aclare el ajuste, explique el drenaje o haga visible la comodidad", "demostrá el agarre, aclará el ajuste, explicá el drenaje o hacé visible la comodidad"),
        ("Cree composiciones", "Creá composiciones"),
        ("Verifique las dimensiones", "Verificá las dimensiones"),
        ("temas de revisión", "temas de las reseñas"),
        ("La frecuencia de revisión", "La frecuencia de una mención en reseñas"),
        ("El situación de la patente", "El estado de la patente"),
        ("una afirmación de venta causal", "una atribución causal de ventas"),
    ]},
    "unimac-case.html": {"es": [
        ("estudio de caso de narración de productos", "caso de comunicación de producto"),
        ("calentador de ventilador industrial electric", "calefactor industrial eléctrico"),
        ("Diseño héroe calentador industrial", "Imagen principal del calefactor industrial"),
        ("Construido con panel de campaña de resistencia de acero.", "Pieza de campaña sobre la resistencia de la estructura de acero."),
        ("Construido con resistencia de acero.", "Construcción resistente de acero"),
        ("en lugar de simplemente reclamarla", "en lugar de limitarse a afirmarla"),
        ("Ayude a los compradores a reconocer su mundo", "Ayudá a los compradores a reconocer su entorno"),
        ("Calor directo donde sea necesario", "Calor dirigido donde hace falta"),
        ("conectan un marco ajustable para calentar y secar enfocados", "muestran cómo el marco ajustable dirige el calor para calefaccionar o secar"),
        ("Cierra con confianza", "Cerrar con confianza"),
        ("Revisión de clientes y categorías.", "Revisión de clientes y categoría"),
        ("Mapeó las características del producto", "Mapeé las características del producto"),
        ("Mantenga el calor creíble.", "Mantener una representación creíble del calor."),
        ("Volver a Creatividades", "Volver a Creatives"),
    ]},
    "Articles.html": {"es": [("recolección de palabras clave", "keyword harvesting"), ("listados de autopartes", "listings de autopartes")]},
    "ecommerce.html": {
        "es": [
            ("portfolio", "portafolio"),
            ("revenue", "ingresos"),
            ("un test controlado", "una prueba controlada"),
            ("claims de producto", "afirmaciones de producto"),
            ("Storefront", "Brand Store"),
            ("activos de conversión", "piezas orientadas a la conversión"),
            ("—fit, peso", "—ajuste, peso"),
            ("Ecommerce & Performance", "Ecommerce y performance"),
            ("Ecommerce &amp; Performance", "Ecommerce y performance"),
            ("<span>TITLE</span><b>Relevance</b>", "<span>TÍTULO</span><b>Relevancia</b>"),
            ("<span>BULLETS</span><b>Value</b>", "<span>BULLETS</span><b>Beneficios</b>"),
            ("<span>GALLERY</span><b>Evidence</b>", "<span>GALERÍA</span><b>Evidencia</b>"),
            ("<span>VIDEO</span><b>Use</b>", "<span>VIDEO</span><b>Uso</b>"),
            ("<span>A+</span><b>Confidence</b>", "<span>A+</span><b>Confianza</b>"),
            ("PPC Scaling & Prime Day", "Escalado de PPC y Prime Day"),
            ("Estrategia de escalamiento PPC", "Estrategia de escalado de PPC"),
            ("microauditorías constantes de Search Terms", "microauditorías constantes de términos de búsqueda"),
            ("refinamiento de imágenes principales", "mejora de las imágenes principales"),
            ("fricción en el listado", "fricción en el listing"),
            ("Unidades ordenadas", "Unidades pedidas"),
            ("ROAS subió de 4.1 a 6.26", "ROAS subió de 4,1 a 6,26"),
            ("Cliente de Performance Ads", "Cliente de performance marketing"),
            ("Cliente de CRO y Diseño", "Cliente de CRO y diseño"),
            ("cuando ads, contenido indexable, pricing, fitment y disponibilidad", "cuando la pauta, el contenido indexable, el pricing, la compatibilidad y la disponibilidad"),
        ],
        "en": [("PPC Upscaling with TACoS Upgrade", "PPC Scaling with Improved TACoS"), ("Sales of ordered products", "Ordered Product Sales")],
    },
    "icon-system-case.html": {"es": [("Un sistema.<br>Cientos de mensajes.", "Un sistema.<br>Cientos de mensajes.")]},
}


def paths_for(entry: dict[str, str], lang: str) -> list[Path]:
    result = [ROOT / entry["spanish" if lang == "es" else "english"]]
    if entry["sourceLanguage"] == lang:
        result.append(ROOT / entry["page"])
    return result


def transform(text: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if reviewed fixes have not been applied")
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["pages"]
    stale: list[str] = []
    changed: list[str] = []

    for entry in catalog:
        page = entry["page"]
        if page in GENERATED or page.startswith("SEO"):
            continue
        specific = PAGE_FIXES.get(page, {})
        for lang, common in (("es", COMMON_ES), ("en", COMMON_EN)):
            replacements = common + specific.get(lang, [])
            for path in paths_for(entry, lang):
                if not path.exists():
                    continue
                original = path.read_text(encoding="utf-8")
                updated = transform(original, replacements)
                if updated == original:
                    continue
                if args.check:
                    stale.append(path.relative_to(ROOT).as_posix())
                else:
                    path.write_text(updated, encoding="utf-8", newline="\n")
                    changed.append(path.relative_to(ROOT).as_posix())

    for relative, replacements in UNCATALOGED_ES_FIXES.items():
        path = ROOT / relative
        original = path.read_text(encoding="utf-8")
        updated = transform(original, replacements)
        if updated == original:
            continue
        if args.check:
            stale.append(relative)
        else:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed.append(relative)

    if stale:
        print("Legacy translation fixes are stale: " + ", ".join(stale))
        return 1
    if args.check:
        print("Reviewed legacy translations are current.")
    else:
        print(f"Updated {len(changed)} localized legacy files.")
        for item in changed:
            print(f"  {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
