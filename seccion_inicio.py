# seccion_inicio.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea
)
from PySide6.QtCore import Qt
import temas


CONTEXTO_PARRAFOS = [
    (
        "Contexto y motivación",
        [
            "En el ámbito académico actual, la simulación y el modelado computacional constituyen "
            "herramientas fundamentales para el análisis y la investigación en Ciencias Básicas. "
            "No obstante, tecnologías como las librerías especializadas y los motores de simulación "
            "molecular exigen conocimientos avanzados de programación, lo que restringe su uso a "
            "perfiles con formación computacional sólida.",

            "Esta situación genera una brecha tecnológica significativa: investigadores en Biología, "
            "Química y disciplinas afines poseen un dominio profundo de su área, pero carecen de las "
            "competencias en programación necesarias para explotar de forma autónoma las herramientas "
            "de simulación disponibles. El resultado es una implementación desigual que frena el "
            "avance científico y la transferencia de conocimiento.",

            "La problemática afecta directamente a docentes, investigadores y estudiantes involucrados "
            "en procesos de modelado y análisis. Un estudio realizado en la Universidad del Rosario "
            "evidenció que la mayoría de los profesores carece de experiencia en Python, a pesar de "
            "requerirla en su actividad investigativa. Asimismo, el análisis de planes de estudio de "
            "programas de Química y Biología en universidades colombianas reveló la ausencia casi "
            "generalizada de formación en programación, confirmando la persistencia de esta brecha "
            "en la práctica profesional.",
        ],
    ),
    (
        "Propósito de la herramienta",
        [
            "Esta interfaz fue desarrollada para cerrar esa brecha: permite configurar y ejecutar "
            "simulaciones de dinámica molecular sobre moléculas pequeñas mediante una interfaz gráfica "
            "intuitiva, sin necesidad de escribir una sola línea de código. El motor de simulación "
            "subyacente es OpenMM, con parametrización de ligandos a través de OpenFF/GAFF.",
        ],
    ),
]

COMO_EMPEZAR = [
    "1.  Visita Instrucciones para revisar la documentación completa de cada parámetro.",
    "2.  Ve a Simulación, carga tu archivo .sdf y configura las opciones de la corrida.",
    "3.  Pulsa «Iniciar simulación» para generar la configuración lista para ejecutar.",
    "4.  En Ajustes puedes personalizar la apariencia de la interfaz a tu preferencia.",
]


class InicioSection(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        t = temas.CURRENT
        e = temas.generar_estilos(t)
        fs   = e["FS"]
        fs_lg = e["FS_LG"]
        fs_xl = e["FS_XL"]
        pad  = e["PAD"]

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(pad * 2, pad * 2, pad * 2, pad * 2)
        layout.setSpacing(pad)

        # ── Título principal ──
        title = QLabel("Simulación Molecular No-Code")
        title.setStyleSheet(
            f"font-size: {fs_xl + 4}px; font-weight: bold; color: {t['ACCENT']};"
        )

        subtitle = QLabel(
            "Una plataforma accesible para físicos, biólogos y químicos que desean realizar "
            "simulaciones de dinámica molecular sin necesidad de programar."
        )
        subtitle.setStyleSheet(f"font-size: {fs_lg}px; color: {t['TEXT_MUTED']};")
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # ── Tarjetas de contexto ──
        for section_title, paragraphs in CONTEXTO_PARRAFOS:
            card = QFrame()
            card.setObjectName("card")
            card.setStyleSheet(e["CARD"])
            cl = QVBoxLayout(card)
            cl.setContentsMargins(pad, pad, pad, pad)
            cl.setSpacing(int(fs * 0.8))

            lbl_titulo = QLabel(section_title)
            lbl_titulo.setStyleSheet(
                f"font-size: {fs_lg}px; font-weight: bold; color: {t['TEXT_DARK']};"
            )
            cl.addWidget(lbl_titulo)

            for p in paragraphs:
                lbl = QLabel(p)
                lbl.setStyleSheet(
                    f"font-size: {fs}px; color: {t['TEXT_MUTED']}; line-height: 1.6;"
                )
                lbl.setWordWrap(True)
                cl.addWidget(lbl)

            layout.addWidget(card)

        # ── Tarjeta ¿Cómo empezar? ──
        card2 = QFrame()
        card2.setObjectName("card")
        card2.setStyleSheet(e["CARD"])
        cl2 = QVBoxLayout(card2)
        cl2.setContentsMargins(pad, pad, pad, pad)
        cl2.setSpacing(int(fs * 0.6))

        lbl_start = QLabel("¿Cómo empezar?")
        lbl_start.setStyleSheet(
            f"font-size: {fs_lg}px; font-weight: bold; color: {t['TEXT_DARK']};"
        )
        cl2.addWidget(lbl_start)

        for step in COMO_EMPEZAR:
            lbl = QLabel(step)
            lbl.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_MUTED']};")
            lbl.setWordWrap(True)
            cl2.addWidget(lbl)

        layout.addWidget(card2)
        layout.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)
