import os
import tempfile

import matplotlib.pyplot as plt
import numpy as np
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QScrollArea
)

import temas

VIDEO_FILENAME = "animacion01.mp4"


class ZoomableImageLabel(QLabel):
    def __init__(self, pixmap=None):
        super().__init__()
        self._base_pixmap = None
        self._scale_factor = 1.0
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setScaledContents(False)
        if pixmap is not None:
            self.set_pixmap(pixmap)

    def set_pixmap(self, pixmap):
        self._base_pixmap = pixmap
        self._scale_factor = 1.0
        self._update_pixmap()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self._scale_factor *= 1.1
        else:
            self._scale_factor *= 0.9
        self._scale_factor = max(0.2, min(self._scale_factor, 5.0))
        self._update_pixmap()

    def _update_pixmap(self):
        if self._base_pixmap is None:
            return
        scaled_pixmap = self._base_pixmap.scaled(
            self._base_pixmap.size() * self._scale_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        super().setPixmap(scaled_pixmap)


class VisualizacionSection(QWidget):
    def __init__(self):
        super().__init__()
        self._player = None
        self._audio_output = None
        self._video_widget = None
        self._build_ui()

    def _build_ui(self):
        t = temas.CURRENT
        e = temas.generar_estilos(t)
        fs, fs_lg, fs_xl = e["FS"], e["FS_LG"], e["FS_XL"]

        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 40, 40, 40)
        outer.setSpacing(20)

        title = QLabel("Visualización")
        title.setStyleSheet(
            f"font-size: {fs_xl}px; font-weight: bold; color: {t['ACCENT']};"
        )

        description = QLabel(
            "Selecciona una vista: muestra gráficas de ejemplo o reproduce el video animacion01.mp4."
        )
        description.setWordWrap(True)
        description.setStyleSheet(f"font-size: {fs_lg}px; color: {t['TEXT_MUTED']};")

        outer.addWidget(title)
        outer.addWidget(description)

        button_row = QHBoxLayout()
        button_row.setSpacing(16)

        btn_graphs = QPushButton("Gráficas")
        btn_graphs.setStyleSheet(e["PRIMARY_BTN"])
        btn_graphs.clicked.connect(self._show_graphs)
        btn_graphs.setCursor(Qt.PointingHandCursor)

        btn_video = QPushButton("Video")
        btn_video.setStyleSheet(e["SECONDARY_BTN"])
        btn_video.clicked.connect(self._show_video)
        btn_video.setCursor(Qt.PointingHandCursor)

        button_row.addWidget(btn_graphs)
        button_row.addWidget(btn_video)
        button_row.addStretch()

        outer.addLayout(button_row)

        self.content_frame = QFrame()
        self.content_frame.setObjectName("card")
        self.content_frame.setStyleSheet(e["CARD"])
        self.content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(16)

        self.message_label = QLabel("Pulsa un botón para visualizar contenido.")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet(f"font-size: {fs}px; color: {t['TEXT_MUTED']};")

        self.content_layout.addWidget(self.message_label)
        outer.addWidget(self.content_frame)

    def _clear_content(self):
        if self._player is not None:
            self._player.stop()
            self._player = None
        if self._audio_output is not None:
            self._audio_output = None
        self._video_widget = None

        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _show_graphs(self):
        self._clear_content()

        image_path = self._create_graph_image()
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            error_label = QLabel("No se pudo cargar la imagen de visualización.")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #b00020; font-size: 14px;")
            self.content_layout.addWidget(error_label)
            return

        image_label = ZoomableImageLabel(pixmap)
        scroll_area = QScrollArea()
        scroll_area.setWidget(image_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignCenter)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        hint_label = QLabel("Desplaza la rueda del ratón sobre la imagen para hacer zoom.")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #777777; font-size: 13px;")

        self.content_layout.addWidget(hint_label)
        self.content_layout.addWidget(scroll_area)

    def _show_video(self):
        self._clear_content()

        video_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, VIDEO_FILENAME)
        )
        if not os.path.exists(video_path):
            error_label = QLabel("No se encontró el archivo animacion01.mp4 en la carpeta del proyecto.")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: #b00020; font-size: 14px;")
            self.content_layout.addWidget(error_label)
            return

        self._video_widget = QVideoWidget()
        self._video_widget.setMinimumHeight(360)
        self._video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._audio_output = QAudioOutput(self)
        self._player = QMediaPlayer(self)
        self._player.setAudioOutput(self._audio_output)
        self._player.setVideoOutput(self._video_widget)
        self._player.setSource(QUrl.fromLocalFile(video_path))
        self._player.play()

        self.content_layout.addWidget(self._video_widget)

    def _create_graph_image(self) -> str:
        x = np.linspace(0, 10, 300)
        fig, axs = plt.subplots(3, 1, figsize=(8, 8), constrained_layout=True)

        axs[0].plot(x, x, color="#2b7cff")
        axs[0].set_title("y = x")
        axs[0].grid(True, alpha=0.3)

        axs[1].plot(x, x**2, color="#ff7f0e")
        axs[1].set_title("y = x^2")
        axs[1].grid(True, alpha=0.3)

        axs[2].plot(x, np.sin(x), color="#2ca02c")
        axs[2].set_title("y = sen(x)")
        axs[2].grid(True, alpha=0.3)

        for ax in axs:
            ax.set_xlabel("x")
            ax.set_ylabel("y")

        temp_path = os.path.join(tempfile.gettempdir(), "visualizacion_graficas.png")
        fig.savefig(temp_path, dpi=120)
        plt.close(fig)
        return temp_path
