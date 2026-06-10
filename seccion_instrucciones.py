# seccion_instrucciones.py — Documentación de uso para usuarios no-técnicos

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea
)
import temas


INSTRUCCIONES = [
    (
        "Sección: Simulación — Cargar archivo",
        (
            "• Arrastra y suelta un archivo SDF (.sdf) en el área de carga o usa el botón «Seleccionar archivo». "
            "• El motor requiere una estructura 3D completa de la molécula para generar la topología y ejecutar la dinámica molecular. "
            "• Busca el icono de información junto a cada campo para ver el tooltip con detalles rápidos."
        ),
    ),
    (
        "Parámetros numéricos",
        (
            "• Carga total: carga neta de la molécula en unidades enteras. Usa 0 para neutro, valores positivos para cationes y negativos para aniones.\n"
            "• Pasos: cantidad de pasos de integración. Más pasos aumentan la duración de la simulación y la calidad del muestreo.\n"
            "• Temperatura (K): temperatura del sistema en Kelvin. 300 K es una referencia cercana a condiciones ambientales.\n"
            "• Fricción (ps⁻¹): coeficiente del termostato de Langevin. Valores más altos equilibran más rápido; valores bajos conservan mejor la energía.\n"
            "• Paso de tiempo (fs): intervalo de tiempo entre pasos en femtosegundos. 2 fs es común; reduce el valor si observas inestabilidad."
        ),
    ),
    (
        "Parámetros booleanos",
        (
            "• Solvente implícito: si activas Sí, el efecto del solvente se modela matemáticamente sin incluir moléculas de agua explícitas. "
            "Esto acelera la simulación y reduce el coste computacional.\n"
            "• Mantener IDs: conserva los identificadores originales de los átomos del archivo SDF. Esto es útil cuando necesitas rastrear átomos específicos en los resultados."
        ),
    ),
    (
        "Integrador",
        (
            "• Elige el algoritmo de integración para la dinámica molecular.\n"
            "  - langevin_middle: recomendado para la mayoría de simulaciones por su estabilidad.\n"
            "  - langevin: termostato de Langevin clásico.\n"
            "  - verlet: integrador estándar con buena conservación de energía.\n"
            "  - brownian: movimiento browniano para entornos muy disipativos.\n"
            "  - nose_hoover: controla la temperatura con un barostato de tipo Nose-Hoover."
        ),
    ),
    (
        "Opciones de guardado",
        (
            "• Modo de guardado:\n"
            "  - Por defecto: crea una carpeta nueva en Documentos con prefijo Simulacion_ y marca de tiempo.\n"
            "  - Automático: guarda los resultados junto al archivo SDF usando su nombre como base.\n"
            "  - Manual: permite escribir un nombre personalizado para la carpeta de salida.\n"
            "• El nombre final siempre añade una marca de tiempo para evitar sobrescribir resultados anteriores."
        ),
    ),
    (
        "Sección: Visualización",
        (
            "• Gráficas: genera una visualización con gráficos de ejemplo. Usa la rueda del ratón sobre la imagen para hacer zoom.\n"
            "• Video: reproduce el archivo animacion01.mp4 desde la carpeta del proyecto. Si el archivo no está presente, aparece un mensaje de error."
        ),
    ),
    (
        "Iniciar simulación",
        (
            "• Pulsa «Iniciar simulación» cuando hayas cargado el archivo SDF y configurado todos los parámetros.\n"
            "• La simulación se ejecuta en segundo plano para no bloquear la interfaz.\n"
            "• El área de salida muestra el estado final, los resultados del motor o los errores encontrados."
        ),
    ),
    (
        "Sección: Ajustes",
        (
            "• Ajusta el tamaño de fuente y cambia entre tema claro u oscuro para adaptar la interfaz a tu preferencia.\n"
            "• El checkbox «Mostrar tooltips» activa o desactiva las descripciones emergentes en los campos de la simulación.\n"
            "• «Restaurar valores por defecto» devuelve los ajustes al estado inicial."
        ),
    ),
]


class InstruccionesSection(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        t = temas.CURRENT
        e = temas.generar_estilos(t)
        fs, fs_lg, fs_xl = e["FS"], e["FS_LG"], e["FS_XL"]

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Instrucciones")
        title.setStyleSheet(f"font-size: {fs_xl}px; font-weight: bold; color: {t['ACCENT']};")

        desc = QLabel(
            "Guía de uso orientada a físicos, biólogos y químicos sin experiencia en programación."
        )
        desc.setStyleSheet(f"font-size: {fs_lg}px; color: {t['TEXT_MUTED']};")
        desc.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(desc)

        for seccion, contenido in INSTRUCCIONES:
            card = QFrame()
            card.setObjectName("card")
            card.setStyleSheet(e["CARD"])
            cl = QVBoxLayout(card)
            cl.setContentsMargins(24, 20, 24, 20)
            cl.setSpacing(10)

            sec_title = QLabel(seccion)
            sec_title.setStyleSheet(
                f"font-size: {fs_lg}px; font-weight: bold; color: {t['TEXT_DARK']};"
            )

            body = QLabel(contenido)
            body.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_MUTED']};")
            body.setWordWrap(True)

            cl.addWidget(sec_title)
            cl.addWidget(body)
            layout.addWidget(card)

        layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)
