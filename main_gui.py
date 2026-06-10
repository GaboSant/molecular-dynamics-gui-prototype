# main.py — Punto de entrada. Ejecuta este archivo para abrir la interfaz.

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSplitter, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt

import temas
from seccion_inicio        import InicioSection
from seccion_instrucciones import InstruccionesSection
from seccion_simulacion    import SimulacionSection
from seccion_ajustes       import AjustesSection
from seccion_visualizacion import VisualizacionSection


SECCIONES = ["Inicio", "Instrucciones", "Simulación", "Visualización", "Ajustes"]

# Índice de la sección Ajustes dentro de SECCIONES
IDX_AJUSTES = 4


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz No-Code")
        self.resize(980, 680)
        self.setMinimumSize(760, 500)
        self._build_chrome()          # encabezado, sidebar, stack (vacío)
        self._populate_stack()        # instanciar y añadir todas las secciones
        self._apply_styles()
        self._switch_section(0)

    # ── Estructura fija (no se reconstruye al cambiar tema) ───────────────────
    def _build_chrome(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Encabezado
        self.header = QWidget()
        self.header.setObjectName("header")
        self.header.setFixedHeight(80)
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(20, 0, 20, 0)

        self.app_title = QLabel("Interfaz No-Code")
        self.app_title.setObjectName("title")
        h_layout.addWidget(self.app_title)
        h_layout.addStretch()

        self.nav_buttons = []
        for i, name in enumerate(SECCIONES):
            btn = QPushButton(name)
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda checked, idx=i: self._switch_section(idx))
            h_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        root.addWidget(self.header)

        # Cuerpo
        self.body = QSplitter(Qt.Horizontal)
        self.body.setHandleWidth(1)

        sidebar_container = QWidget()
        sidebar_container.setFixedWidth(280)
        sb_layout = QVBoxLayout(sidebar_container)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        self.sidebar_label = QLabel("  Índice")
        self.sidebar_list  = QListWidget()
        for name in SECCIONES:
            self.sidebar_list.addItem(QListWidgetItem(name))
        self.sidebar_list.currentRowChanged.connect(self._switch_section)

        sb_layout.addWidget(self.sidebar_label)
        sb_layout.addWidget(self.sidebar_list)

        self.stack = QStackedWidget()

        self.body.addWidget(sidebar_container)
        self.body.addWidget(self.stack)
        self.body.setStretchFactor(0, 0)
        self.body.setStretchFactor(1, 1)

        root.addWidget(self.body)

    def _populate_stack(self):
        """Instancia las secciones y las añade al stack."""
        ajustes = AjustesSection()
        ajustes.on_apply = self._refresh_all

        self._sections = [
            InicioSection(),
            InstruccionesSection(),
            SimulacionSection(),
            VisualizacionSection(),
            ajustes,
        ]
        for sec in self._sections:
            self.stack.addWidget(sec)

    # ── Estilos del chrome (encabezado, sidebar…) ─────────────────────────────
    def _apply_styles(self):
        t = temas.CURRENT
        e = temas.generar_estilos(t)

        self.setStyleSheet(e["MAIN"])
        self.header.setStyleSheet(e["HEADER"])
        self.app_title.setStyleSheet(
            f"font-size: {e['FS_LG']}px; font-weight: bold; color: {t['ACCENT']}; padding: 0 8px;"
        )
        self.body.setStyleSheet(e["SPLITTER"])
        self.sidebar_label.setStyleSheet(e["SIDEBAR_LABEL"])
        self.sidebar_list.setStyleSheet(e["SIDEBAR"])
        for btn in self.nav_buttons:
            btn.setStyleSheet(e["NAV_BTN"])

    # ── Reconstruir todas las secciones al cambiar tema o fuente ─────────────
    def _refresh_all(self):
        current_idx = self.stack.currentIndex()

        # Reconstruir cada sección: las que tienen _rebuild lo llaman;
        # las demás se reemplazan por una instancia nueva.
        factories = {
            0: InicioSection,
            1: InstruccionesSection,
            2: SimulacionSection,
            3: VisualizacionSection,
            # Ajustes (idx 4) tiene su propio _rebuild
        }

        for idx, cls in factories.items():
            old = self.stack.widget(idx)
            new = cls()
            self.stack.insertWidget(idx, new)
            self.stack.removeWidget(old)
            old.deleteLater()
            self._sections[idx] = new

        # Ajustes se reconstruye in-place
        self._sections[IDX_AJUSTES]._rebuild()

        self._apply_styles()
        self._switch_section(current_idx)

    # ── Navegación ────────────────────────────────────────────────────────────
    def _switch_section(self, index: int):
        self.stack.setCurrentIndex(index)
        self.sidebar_list.blockSignals(True)
        self.sidebar_list.setCurrentRow(index)
        self.sidebar_list.blockSignals(False)
        e = temas.generar_estilos(temas.CURRENT)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.setStyleSheet(e["NAV_BTN"])


# ── Punto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
