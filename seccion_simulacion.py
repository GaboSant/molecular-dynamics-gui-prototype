# seccion_simulacion.py — Configuración y lanzamiento de simulaciones MD

import sys
import os
import subprocess
import json
import traceback
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QFileDialog, QMessageBox, QLineEdit, QComboBox,
    QTextEdit, QSizePolicy, QScrollArea, QPushButton, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
import temas

TIPO_ARCHIVO = ("Archivos SDF (*.sdf)", ".sdf")

# ─── Worker: ejecuta la simulación en un hilo separado ───────────────
class SimWorker(QObject):
    finished = Signal(str)
    error    = Signal(str)

    def __init__(self, config_dict: dict):
        super().__init__()
        self._config_dict = config_dict

    def run(self):
        try:
            if getattr(sys, 'frozen', False):
                ruta_raiz_win = sys._MEIPASS
            else:
                ruta_raiz_win = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

            drive = ruta_raiz_win[0].lower()
            path_rest = ruta_raiz_win[2:].replace('\\', '/')
            ruta_raiz_wsl = f"/mnt/{drive}{path_rest}"
            
            path_wrapper_wsl = f"{ruta_raiz_wsl}/gui/motor_wrapper.py"
            
            path_wrapper_wsl = f"{ruta_raiz_wsl}/gui/motor_wrapper.py"
            
            config_json = json.dumps(self._config_dict)

            comando_bash = (
                f"export PYTHONPATH=$PYTHONPATH:{ruta_raiz_wsl} && "
                f"~/bin/micromamba run -n sim_env python3 {path_wrapper_wsl} '{config_json}'"
            )

            comando_wsl = ["wsl", "-d", "Ubuntu", "bash", "-c", comando_bash]

            proceso = subprocess.run(
                comando_wsl,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            if proceso.returncode == 0:
                try:
                    res = json.loads(proceso.stdout.strip())
                    if res["status"] == "success":
                        self.finished.emit(f"Éxito:\n{res['data']}")
                    else:
                        self.error.emit(f"Error en la ciencia: {res['message']}")
                except:
                    self.finished.emit(f"Salida directa:\n{proceso.stdout}")
            else:
                self.error.emit(f"Error de Sistema (WSL):\n{proceso.stderr}")

        except Exception as e:
            self.error.emit(f"No se pudo conectar con WSL: {str(e)}")


class DropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("uploadArea")
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.file_path_win = None  # Guardamos la original de Windows
        self.file_path_wsl = None  # Guardamos la traducida para el motor
        self._build_ui()

    def _build_ui(self):
        t = temas.CURRENT
        e = temas.generar_estilos(t)
        fs = e["FS"]

        self.setMinimumHeight(int(fs * 15))
        self.setMaximumHeight(int(fs * 20))
        self.setStyleSheet(e["UPLOAD_AREA"])

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(int(fs * 0.8))

        icon = QLabel("🧪")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(f"font-size: {int(fs * 2.2)}px; background: transparent;")

        ext = TIPO_ARCHIVO[1]
        hint = QLabel(f"Arrastra y suelta un archivo {ext} aquí")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"color: {t['TEXT_MUTED']}; font-size: {fs}px; background: transparent;")

        self.file_label = QLabel("")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setStyleSheet(f"color: {t['ACCENT']}; font-size: {e['FS_SM']}px; font-weight: bold; background: transparent;")

        sep = QLabel("— o —")
        sep.setAlignment(Qt.AlignCenter)
        sep.setStyleSheet(f"color: {t['TEXT_MUTED']}; font-size: {e['FS_SM']}px; background: transparent;")

        btn = QPushButton("  Seleccionar archivo")
        btn.setStyleSheet(e["SECONDARY_BTN"])
        btn.setMinimumWidth(int(fs * 10))
        btn.setMaximumWidth(int(fs * 14))
        btn.setMinimumHeight(int(fs * 2.2))
        btn.clicked.connect(self._open_dialog)

        layout.addWidget(icon)
        layout.addWidget(hint)
        layout.addWidget(self.file_label)
        layout.addWidget(sep)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

    def _open_dialog(self):
        filtro, _ = TIPO_ARCHIVO
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo SDF", "", filtro)
        if path:
            self._set_file(path)

    def _set_file(self, path):
        ext = TIPO_ARCHIVO[1]
        if not path.lower().endswith(ext):
            QMessageBox.warning(self, "Formato no permitido", f"⚠️  Solo se permiten archivos {ext}.")
            return
        
        self.file_path_win = os.path.abspath(path)
        

        drive = self.file_path_win[0].lower()
        path_rest = self.file_path_win[2:].replace('\\', '/')
        self.file_path_wsl = f"/mnt/{drive}{path_rest}"
        
        
        self.file_label.setText(f"✓  {os.path.basename(path)}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self._set_file(urls[0].toLocalFile())


# ─── Sección Simulación ───────────────────────────────────────────────────────
class SimulacionSection(QWidget):
    def __init__(self):
        super().__init__()
        self._thread = None
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        t = temas.CURRENT
        e = temas.generar_estilos(t)
        fs, fs_sm, fs_lg, fs_xl = e["FS"], e["FS_SM"], e["FS_LG"], e["FS_XL"]

        tooltip_style = f"""
        QToolTip {{
            background-color: {t['BG_MAIN']};
            color: {t['TEXT_DARK']};
            border: 1px solid {t['ACCENT']};
            padding: 6px; border-radius: 4px; font-size: {e['FS_SM']}px;
        }}
        """
        self.setStyleSheet(self.styleSheet() + tooltip_style)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Simulación")
        title.setStyleSheet(f"font-size: {fs_xl}px; font-weight: bold; color: {t['ACCENT']};")

        desc = QLabel("Carga un archivo SDF y configura los parámetros antes de iniciar la simulación.")
        desc.setStyleSheet(f"font-size: {fs_lg}px; color: {t['TEXT_MUTED']};")
        desc.setWordWrap(True)

        self.drop_area = DropArea()

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(self.drop_area)

        # ── Parámetros numéricos ──
        layout.addWidget(self._sec_lbl("Parámetros numéricos", t, fs_lg))
        num_card = self._card(e)
        num_layout = QVBoxLayout(num_card)
        num_layout.setContentsMargins(24, 20, 24, 20)
        num_layout.setSpacing(12)

        self.campos_num = {}
        for key, label, default, tooltip in [
            ("carga_total",       "Carga total",          "0",    "Carga eléctrica neta (entero)"),
            ("pasos",             "Pasos",                "5000", "Número de pasos de integración"),
            ("temperatura",       "Temperatura (K)",      "300.0","Temperatura del sistema"),
            ("friction",          "Fricción (ps⁻¹)",      "1.0",  "Coeficiente de fricción del termostato"),
            ("timestep_fs",       "Paso de tiempo (fs)",  "2.0",  "Intervalo de tiempo por paso"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setFixedWidth(int(fs * 12))
            lbl.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_DARK']};")
            lbl.setToolTip(tooltip)
            field = QLineEdit(default)
            field.setStyleSheet(e["INPUT"])
            field.setFixedWidth(int(fs * 8))
            field.setToolTip(tooltip)
            row.addWidget(lbl)
            row.addWidget(field)
            row.addWidget(self._tooltip_icon(tooltip, t, fs))
            row.addStretch()
            num_layout.addLayout(row)
            self.campos_num[key] = field

        layout.addWidget(num_card)

        # ── Parámetros booleanos ──
        layout.addWidget(self._sec_lbl("Parámetros booleanos", t, fs_lg))
        bool_card = self._card(e)
        bool_layout = QVBoxLayout(bool_card)
        bool_layout.setContentsMargins(24, 20, 24, 20)
        bool_layout.setSpacing(12)

        self.campos_bool = {}
        for key, label, tooltip in [
            ("solvente_implicito", "Solvente implícito", "Modela el solvente de forma matemática sin moléculas explícitas"),
            ("keep_ids", "Mantener IDs", "Mantiene los identificadores originales de la estructura"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setFixedWidth(int(fs * 12))
            lbl.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_DARK']};")
            lbl.setToolTip(tooltip)
            combo = QComboBox()
            combo.addItems(["Sí", "No"])
            combo.setStyleSheet(e["INPUT"])
            combo.setFixedWidth(int(fs * 8))
            combo.setToolTip(tooltip)
            row.addWidget(lbl)
            row.addWidget(combo)
            row.addWidget(self._tooltip_icon(tooltip, t, fs))
            row.addStretch()
            bool_layout.addLayout(row)
            self.campos_bool[key] = combo

        layout.addWidget(bool_card)

        # ── Opciones (Integrador y Forcefields) ──
        layout.addWidget(self._sec_lbl("Integrador y opciones", t, fs_lg))
        opt_card = self._card(e)
        opt_layout = QVBoxLayout(opt_card)
        opt_layout.setContentsMargins(24, 20, 24, 20)
        opt_layout.setSpacing(12)

        self.campos_opt = {}
        for key, label, opciones, tooltip in [
            ("integrador", 
             "Integrador", 
             ["langevin_middle", "langevin", "verlet", "brownian", "nose_hoover"], 
             "Algoritmo integrador para la dinámica"),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setFixedWidth(int(fs * 12))
            lbl.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_DARK']};")
            lbl.setToolTip(tooltip)
            combo = QComboBox()
            combo.addItems(opciones)
            combo.setStyleSheet(e["INPUT"])
            combo.setFixedWidth(int(fs * 8))
            combo.setToolTip(tooltip)
            row.addWidget(lbl)
            row.addWidget(combo)
            row.addWidget(self._tooltip_icon(tooltip, t, fs))
            row.addStretch()
            opt_layout.addLayout(row)
            self.campos_opt[key] = combo

        layout.addWidget(opt_card)

        # ── Opciones de guardado de archivos ──
        layout.addWidget(self._sec_lbl("Guardado de archivos", t, fs_lg))
        save_card = self._card(e)
        save_layout = QVBoxLayout(save_card)
        save_layout.setContentsMargins(24, 20, 24, 20)
        save_layout.setSpacing(12)

        row_save = QHBoxLayout()
        lbl_save = QLabel("Modo de guardado:")
        lbl_save.setFixedWidth(int(fs * 12))
        lbl_save.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_DARK']};")
        lbl_save.setToolTip("Selecciona como deseas guardar los archivos de la simulacion")
        
        self.combo_save_mode = QComboBox()
        self.combo_save_mode.addItems(["Por defecto", "Automatico", "Manual"])
        self.combo_save_mode.setStyleSheet(e["INPUT"])
        self.combo_save_mode.setFixedWidth(int(fs * 8))
        self.combo_save_mode.setToolTip("Por defecto: carpeta 'Simulacion' | Automatico: nombre del archivo | Manual: personalizado")
        self.combo_save_mode.currentTextChanged.connect(self._on_save_mode_changed)
        
        row_save.addWidget(lbl_save)
        row_save.addWidget(self.combo_save_mode)
        row_save.addWidget(self._tooltip_icon(self.combo_save_mode.toolTip(), t, fs))
        row_save.addStretch()
        save_layout.addLayout(row_save)

        row_custom = QHBoxLayout()
        lbl_custom = QLabel("Nombre personalizado:")
        lbl_custom.setFixedWidth(int(fs * 12))
        lbl_custom.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_DARK']};")
        lbl_custom.setToolTip("Nombre de la carpeta (solo disponible en modo Manual)")
        
        self.input_custom_folder = QLineEdit()
        self.input_custom_folder.setPlaceholderText("Ej: mi_simulacion")
        self.input_custom_folder.setStyleSheet(e["INPUT"])
        self.input_custom_folder.setFixedWidth(int(fs * 8))
        self.input_custom_folder.setEnabled(False)
        self.input_custom_folder.setToolTip("Se anadira automaticamente una marca de tiempo")
        
        row_custom.addWidget(lbl_custom)
        row_custom.addWidget(self.input_custom_folder)
        row_custom.addWidget(self._tooltip_icon(self.input_custom_folder.toolTip(), t, fs))
        row_custom.addStretch()
        save_layout.addLayout(row_custom)

        layout.addWidget(save_card)

        # ── Botón + barra de progreso ──
        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("▶   Iniciar simulación")
        self.start_btn.setStyleSheet(e["PRIMARY_BTN"])
        self.start_btn.setFixedWidth(int(fs * 20))
        self.start_btn.clicked.connect(self._iniciar)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)   # Modo indeterminado (cargando)
        self.progress.setVisible(False)
        self.progress.setFixedHeight(10)
        self.progress.setStyleSheet(
            f"QProgressBar {{ border: none; border-radius: 5px; background: {t['BORDER']}; }}"
            f"QProgressBar::chunk {{ background: {t['ACCENT']}; border-radius: 5px; }}"
        )

        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.progress)
        btn_row.addStretch()

        # ── Salida ──
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("La salida y resultados aparecerán aquí...")
        self.output.setStyleSheet(
            f"background-color: {t['BG_CARD']}; border: 1px solid {t['BORDER']}; "
            f"border-radius: 10px; padding: 12px; font-size: {fs_sm}px; "
            f"font-family: 'Consolas', monospace; color: {t['TEXT_DARK']};"
        )
        self.output.setMinimumHeight(180)

        layout.addLayout(btn_row)
        layout.addWidget(self.output)
        layout.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _sec_lbl(text, t, fs_lg):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: {fs_lg}px; font-weight: bold; color: {t['TEXT_DARK']}; padding-top: 8px;")
        return lbl

    @staticmethod
    def _card(e):
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(e["CARD"])
        return card

    @staticmethod
    def _tooltip_icon(tooltip, t, fs):
        icon = QLabel("🛈")
        icon.setToolTip(tooltip)
        icon.setAlignment(Qt.AlignCenter)
        icon.setFixedWidth(int(fs * 1.2))
        icon.setStyleSheet(
            f"color: {t['TEXT_MUTED']}; font-size: {int(fs * 1.1)}px; background: {t['BG_CARD']};"
        )
        icon.setCursor(Qt.PointingHandCursor)
        return icon

    def _on_save_mode_changed(self, mode):
        """Habilita/deshabilita el campo de nombre personalizado segun el modo."""
        self.input_custom_folder.setEnabled(mode == "Manual")

    def _get_output_folder(self):
        """Genera la ruta de salida segun el modo seleccionado, con marca de tiempo."""
        mode = self.combo_save_mode.currentText()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if mode == "Por defecto":
            folder_name = f"Simulacion_{timestamp}"
            output_dir = os.path.join(os.path.expanduser("~"), "Documentos", folder_name)
        elif mode == "Automatico":
            base_name = os.path.splitext(os.path.basename(self.drop_area.file_path_win))[0]
            folder_name = f"{base_name}_{timestamp}"
            output_dir = os.path.join(os.path.dirname(self.drop_area.file_path_win), folder_name)
        else:  # Manual
            custom_name = self.input_custom_folder.text().strip()
            if not custom_name:
                raise ValueError("En modo Manual, debes proporcionar un nombre para la carpeta.")
            folder_name = f"{custom_name}_{timestamp}"
            output_dir = os.path.join(os.path.expanduser("~"), "Documentos", folder_name)
        
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _convert_path_to_wsl(self, windows_path):
        """Convierte una ruta de Windows a formato WSL."""
        abs_path = os.path.abspath(windows_path)
        drive = abs_path[0].lower()
        path_rest = abs_path[2:].replace('\\', '/')
        return f"/mnt/{drive}{path_rest}"


    # ── Lógica con hilo separado ──────────────────────────────────────────────
    def _iniciar(self):
        if not self.drop_area.file_path_wsl:
            QMessageBox.information(self, "Sin archivo", "Por favor carga un archivo .sdf antes de iniciar la simulación.")
            return

        def bool_val(combo):
            return combo.currentText() == "Sí"

        # Obtener la ruta de salida
        try:
            output_dir = self._get_output_folder()
            output_dir_wsl = self._convert_path_to_wsl(output_dir)
        except ValueError as e:
            QMessageBox.critical(self, "Error en configuración", str(e))
            return

        # Validamos los tipos de dato. Esto es crucial porque el motor espera ints y floats
        try:
            config_kwargs = {
                "ruta_sdf":           self.drop_area.file_path_wsl,
                "ruta_salida":        output_dir_wsl,
                "carga_total":        int(self.campos_num["carga_total"].text().strip()),
                "pasos":              int(self.campos_num["pasos"].text().strip()),
                "temperatura":        float(self.campos_num["temperatura"].text().strip()),
                "friction":           float(self.campos_num["friction"].text().strip()),
                "timestep_fs":        float(self.campos_num["timestep_fs"].text().strip()),
                "solvente_implicito": bool_val(self.campos_bool["solvente_implicito"]),
                "keep_ids":           bool_val(self.campos_bool["keep_ids"]),
                "integrador":         self.campos_opt["integrador"].currentText(),
            }
        except ValueError:
            QMessageBox.critical(self, "Error de validación", "Verifica que los valores numéricos sean válidos (ej. usa punto para los decimales y enteros sin letras).")
            return

        # Bloquear botón y mostrar spinner mientras corre el worker
        self.start_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.output.setPlainText(f"Iniciando motor de simulación.\nArchivos guardados en: {output_dir}\nPor favor espera...")

        self._thread = QThread()
        self._worker = SimWorker(config_kwargs)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        
        # Limpieza de hilos
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def _on_done(self, text: str):
        self.output.setPlainText(text)
        self.progress.setVisible(False)
        self.start_btn.setEnabled(True)

    def _on_error(self, msg: str):
        self.output.setPlainText(f"La simulación falló.\n\n{msg}")
        self.progress.setVisible(False)
        self.start_btn.setEnabled(True)