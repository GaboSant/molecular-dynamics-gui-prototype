# seccion_ajustes.py — Configuración de apariencia de la interfaz

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QComboBox, QCheckBox, QApplication
)
from PySide6.QtCore import Qt
import temas


TAMANIOS_LETRA = {
    "Muy pequeño": 12,
    "Pequeño":     16,
    "Mediano":     20,
    "Grande":      24,
    "Muy grande":  28,
}

TAMANIO_DEFAULT = "Mediano"
TEMA_DEFAULT    = "Claro"

# Estado persistente entre reconstrucciones
_estado = {
    "fuente": TAMANIO_DEFAULT,
    "tema":   TEMA_DEFAULT,
    "tips":   True,
}


class AjustesSection(QWidget):
    on_apply = None  # Callback conectado por MainWindow

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        t = temas.CURRENT
        e = temas.generar_estilos(t)
        fs, fs_sm, fs_lg, fs_xl = e["FS"], e["FS_SM"], e["FS_LG"], e["FS_XL"]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)

        title = QLabel("Ajustes")
        title.setStyleSheet(f"font-size: {fs_xl}px; font-weight: bold; color: {t['ACCENT']};")

        desc = QLabel("Personaliza la apariencia de la interfaz a tu gusto.")
        desc.setStyleSheet(f"font-size: {fs_lg}px; color: {t['TEXT_MUTED']};")

        layout.addWidget(title)
        layout.addWidget(desc)

        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(e["CARD"])
        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 24, 28, 24)
        cl.setSpacing(18)

        card_title = QLabel("Apariencia")
        card_title.setStyleSheet(f"font-size: {fs_lg}px; font-weight: bold; color: {t['TEXT_DARK']};")
        cl.addWidget(card_title)

        # — Tamaño de letra —
        row_font = QHBoxLayout()
        lbl_font = QLabel("Tamaño de letra:")
        lbl_font.setFixedWidth(int(fs * 9))
        lbl_font.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_DARK']};")

        self.combo_font = QComboBox()
        self.combo_font.addItems(list(TAMANIOS_LETRA.keys()))
        self.combo_font.setCurrentText(_estado["fuente"])
        self.combo_font.setStyleSheet(e["INPUT"])
        self.combo_font.setFixedWidth(160)

        btn_font = QPushButton("Aplicar tamaño")
        btn_font.setStyleSheet(e["PRIMARY_BTN"])
        btn_font.clicked.connect(self._aplicar_fuente)

        row_font.addWidget(lbl_font)
        row_font.addWidget(self.combo_font)
        row_font.addSpacing(12)
        row_font.addWidget(btn_font)
        row_font.addStretch()
        cl.addLayout(row_font)

        # — Tema de colores —
        row_tema = QHBoxLayout()
        lbl_tema = QLabel("Tema de colores:")
        lbl_tema.setFixedWidth(int(fs * 9))
        lbl_tema.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_DARK']};")

        self.combo_tema = QComboBox()
        self.combo_tema.addItems(["Claro", "Oscuro"])
        self.combo_tema.blockSignals(True)
        self.combo_tema.setCurrentText(_estado["tema"])
        self.combo_tema.blockSignals(False)
        self.combo_tema.setStyleSheet(e["INPUT"])
        self.combo_tema.setFixedWidth(160)
        self.combo_tema.currentTextChanged.connect(self._cambiar_tema)

        row_tema.addWidget(lbl_tema)
        row_tema.addWidget(self.combo_tema)
        row_tema.addStretch()
        cl.addLayout(row_tema)

        # — Tooltips —
        row_tips = QHBoxLayout()
        lbl_tips = QLabel("Mostrar tooltips:")
        lbl_tips.setFixedWidth(int(fs * 9))
        lbl_tips.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_DARK']};")

        self.chk_tips = QCheckBox("Activado")
        self.chk_tips.setChecked(_estado["tips"])
        self.chk_tips.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_DARK']};")
        self.chk_tips.stateChanged.connect(self._toggle_tooltips)

        row_tips.addWidget(lbl_tips)
        row_tips.addWidget(self.chk_tips)
        row_tips.addStretch()
        cl.addLayout(row_tips)

        # — Restaurar —
        btn_reset = QPushButton("Restaurar valores por defecto")
        btn_reset.setStyleSheet(e["SECONDARY_BTN"])
        btn_reset.setFixedWidth(int(fs * 19))
        btn_reset.clicked.connect(self._restaurar)
        cl.addWidget(btn_reset, alignment=Qt.AlignLeft)

        layout.addWidget(card)
        layout.addStretch()

    def _rebuild(self):
        old = self.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old)
        self._build_ui()

    def _aplicar_fuente(self):
        nombre = self.combo_font.currentText()
        _estado["fuente"] = nombre
        temas.aplicar_fuente(TAMANIOS_LETRA[nombre])
        if self.on_apply:
            self.on_apply()

    def _cambiar_tema(self, nombre):
        _estado["tema"] = nombre
        temas.aplicar_tema(nombre)
        if self.on_apply:
            self.on_apply()

    def _toggle_tooltips(self, state):
        _estado["tips"] = (state != Qt.Unchecked)
        app = QApplication.instance()
        if app:
            ss = app.styleSheet().replace("\nQToolTip { opacity: 0; }", "")
            if state == Qt.Unchecked:
                ss += "\nQToolTip { opacity: 0; }"
            app.setStyleSheet(ss)

    def _restaurar(self):
        _estado["fuente"] = TAMANIO_DEFAULT
        _estado["tema"]   = TEMA_DEFAULT
        _estado["tips"]   = True
        temas.aplicar_fuente(TAMANIOS_LETRA[TAMANIO_DEFAULT])
        temas.aplicar_tema(TEMA_DEFAULT)
        if self.on_apply:
            self.on_apply()
