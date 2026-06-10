# temas.py — Paletas de colores y hojas de estilos globales

# ─── Tema claro ───────────────────────────────────────────────────────────────
LIGHT = dict(
    PRIMARY    = "#1a1a2e",
    ACCENT     = "#4f46e5",
    ACCENT_HOV = "#4338ca",
    BG_MAIN    = "#f8f7ff",
    BG_CARD    = "#ffffff",
    BG_SIDEBAR = "#f0effe",
    TEXT_DARK  = "#1e1b4b",
    TEXT_MUTED = "#6b7280",
    BORDER     = "#e0e7ff",
)

# ─── Tema oscuro ──────────────────────────────────────────────────────────────
DARK = dict(
    PRIMARY    = "#0d0d1a",
    ACCENT     = "#818cf8",
    ACCENT_HOV = "#6366f1",
    BG_MAIN    = "#0f0f1e",
    BG_CARD    = "#1a1a2e",
    BG_SIDEBAR = "#13132a",
    TEXT_DARK  = "#e0e7ff",
    TEXT_MUTED = "#9ca3af",
    BORDER     = "#2e2e50",
)

# Tema activo (mutable en tiempo de ejecución)
CURRENT = dict(LIGHT)

# Tamaño de fuente activo en puntos (se actualiza desde AjustesSection)
FONT_PT: int = 20


def aplicar_tema(nombre: str):
    global CURRENT
    CURRENT.update(LIGHT if nombre == "Claro" else DARK)


def aplicar_fuente(pt: int):
    global FONT_PT
    FONT_PT = pt


def generar_estilos(t: dict) -> dict:
    # Escala tipográfica derivada del tamaño base
    fs    = FONT_PT
    fs_sm = max(fs - 2, 8)
    fs_lg = fs + 2
    fs_xl = fs + 6
    fs_xxl = fs + 12

    # Escala espacial: padding y radios crecen proporcionalmente con la fuente
    pad = max(int(fs * 0.7), 8)          # margen/padding base
    r   = max(int(fs * 0.55), 6)         # border-radius general
    r_lg = max(int(fs * 0.9), 10)        # border-radius tarjetas/áreas

    # Altura de controles interactivos
    ctrl_h   = fs * 2 + 4               # alto de inputs/combos
    btn_pv   = max(int(fs * 0.65), 6)   # padding vertical botón primario
    btn_ph   = max(int(fs * 1.8), 18)   # padding horizontal botón primario
    btn_sv   = max(int(fs * 0.5), 5)    # padding vertical botón secundario
    btn_sh   = max(int(fs * 1.3), 14)   # padding horizontal botón secundario

    # Altura del encabezado y sidebar
    header_h = fs * 3 + 8
    sb_item_pv = max(int(fs * 0.65), 6)
    sb_item_ph = max(int(fs * 1.4), 16)

    return {
        "MAIN": f"""
            QMainWindow, QWidget {{
                background-color: {t['BG_MAIN']};
                color: {t['TEXT_DARK']};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {fs}px;
            }}
        """,
        "HEADER": f"""
            QWidget#header {{
                background-color: {t['BG_CARD']};
                border-bottom: 1px solid {t['BORDER']};
            }}
        """,
        "TITLE": f"""
            QLabel#title {{
                font-size: {fs_lg}px;
                font-weight: bold;
                color: {t['ACCENT']};
                padding: 0 {pad // 2}px;
            }}
        """,
        "NAV_BTN": f"""
            QPushButton {{
                background-color: transparent;
                color: {t['TEXT_MUTED']};
                border: none;
                font-size: {fs}px;
                padding: {btn_sv}px {btn_sh}px;
                border-radius: {r}px;
            }}
            QPushButton:hover {{
                background-color: {t['BG_SIDEBAR']};
                color: {t['ACCENT']};
            }}
            QPushButton[active="true"] {{
                background-color: {t['ACCENT']};
                color: white;
                font-weight: bold;
            }}
        """,
        "SIDEBAR": f"""
            QListWidget {{
                background-color: {t['BG_SIDEBAR']};
                border: none;
                border-right: 1px solid {t['BORDER']};
                font-size: {fs}px;
                padding: {pad // 2}px 0;
                outline: none;
            }}
            QListWidget::item {{
                padding: {sb_item_pv}px {sb_item_ph}px;
                border-radius: {r}px;
                color: {t['TEXT_DARK']};
                margin: 2px {r // 2}px;
            }}
            QListWidget::item:hover {{
                background-color: {t['BORDER']};
            }}
            QListWidget::item:selected {{
                background-color: {t['ACCENT']};
                color: white;
            }}
        """,
        "UPLOAD_AREA": f"""
            QFrame#uploadArea {{
                border: 2px dashed {t['ACCENT']};
                border-radius: {r_lg}px;
                background-color: {t['BG_SIDEBAR']};
                min-height: {fs * 10}px;
            }}
            QFrame#uploadArea:hover {{
                background-color: {t['BG_MAIN']};
            }}
        """,
        "PRIMARY_BTN": f"""
            QPushButton {{
                background-color: {t['ACCENT']};
                color: white;
                border: none;
                font-size: {fs}px;
                font-weight: bold;
                padding: {btn_pv}px {btn_ph}px;
                border-radius: {r}px;
            }}
            QPushButton:hover {{
                background-color: {t['ACCENT_HOV']};
            }}
            QPushButton:pressed {{
                background-color: #3730a3;
            }}
        """,
        "SECONDARY_BTN": f"""
            QPushButton {{
                background-color: {t['BG_CARD']};
                color: {t['ACCENT']};
                border: 1.5px solid {t['ACCENT']};
                font-size: {fs_sm}px;
                padding: {btn_sv}px {btn_sh}px;
                border-radius: {r}px;
            }}
            QPushButton:hover {{
                background-color: {t['BG_SIDEBAR']};
            }}
        """,
        "CARD": f"""
            QFrame#card {{
                background-color: {t['BG_CARD']};
                border: 1px solid {t['BORDER']};
                border-radius: {r_lg}px;
            }}
        """,
        "INPUT": f"""
            QLineEdit, QComboBox, QTextEdit {{
                border: 1.5px solid {t['BORDER']};
                border-radius: {r}px;
                padding: {pad // 2}px {pad}px;
                font-size: {fs}px;
                background-color: {t['BG_CARD']};
                color: {t['TEXT_DARK']};
                min-width: {fs * 10}px;
                min-height: {ctrl_h}px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {t['ACCENT']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: {pad // 2}px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {t['BG_CARD']};
                color: {t['TEXT_DARK']};
                border: 1px solid {t['BORDER']};
                selection-background-color: {t['ACCENT']};
                font-size: {fs}px;
            }}
        """,
        "SPLITTER": f"QSplitter::handle {{ background: {t['BORDER']}; }}",
        "SIDEBAR_LABEL": (
            f"font-size: {fs_sm}px; font-weight: bold; color: {t['TEXT_MUTED']}; "
            f"padding: {pad}px {pad}px {pad // 2}px; letter-spacing: 1px;"
        ),
        # Valores numéricos exportados para usarlos en f-strings de secciones
        "FS":       fs,
        "FS_SM":    fs_sm,
        "FS_LG":    fs_lg,
        "FS_XL":    fs_xl,
        "FS_XXL":   fs_xxl,
        "PAD":      pad,
        "RADIUS":   r,
        "RADIUS_LG": r_lg,
        "HEADER_H": header_h,
        "CTRL_H":   ctrl_h,
    }
