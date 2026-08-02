from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from config.paths import RESOURCES_DIR

from ui.pages.base_page import BasePage


def _first_existing_image(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists() and path.is_file():
            return path
    return None


class _BackgroundPanel(QWidget):
    """Lightweight widget that paints a scalable background image."""

    def __init__(self, image_path: Path | None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pixmap = QPixmap(str(image_path)) if image_path is not None else QPixmap()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        if not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x_offset = (scaled.width() - self.width()) // 2
            y_offset = (scaled.height() - self.height()) // 2
            source = QRect(x_offset, y_offset, self.width(), self.height())
            painter.drawPixmap(self.rect(), scaled, source)
        else:
            # Soft neutral fallback if background image is missing.
            painter.fillRect(self.rect(), QColor("#eaf0f3"))

        # Subtle softening layer to mimic a blurred background feel.
        painter.fillRect(self.rect(), QColor(255, 255, 255, 110))
        super().paintEvent(event)


class DashboardPage(BasePage):
    """Initial dashboard page for the application."""

    page_name = "dashboard"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        background_path = _first_existing_image(
            [
                RESOURCES_DIR / "icons" / "dashboard_background.png",
                RESOURCES_DIR / "icons" / "medical_background.png",
                RESOURCES_DIR / "icons" / "app.png",
            ]
        )
        logo_path = _first_existing_image(
            [
                RESOURCES_DIR / "icons" / "clinichain_logo.png",
                RESOURCES_DIR / "icons" / "app.png",
            ]
        )

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.background_panel = _BackgroundPanel(background_path, self)
        root_layout.addWidget(self.background_panel)

        panel_layout = QVBoxLayout(self.background_panel)
        panel_layout.setContentsMargins(48, 48, 48, 48)

        panel_layout.addStretch(1)

        overlay = QWidget(self.background_panel)
        overlay.setStyleSheet(
            "background-color: rgba(255, 255, 255, 190);"
            "border: 1px solid rgba(255, 255, 255, 120);"
            "border-radius: 16px;"
        )

        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(36, 36, 36, 36)
        overlay_layout.setSpacing(12)

        self.logo_label = QLabel(overlay)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumHeight(100)
        self.logo_label.setMaximumHeight(180)
        self.logo_label.setScaledContents(False)
        self._logo_source = QPixmap(str(logo_path)) if logo_path is not None else QPixmap()
        self._refresh_logo()

        welcome_label = QLabel("Welcome to DLMS", overlay)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 28px; font-weight: 700; color: #0f172a;")

        subtitle_label = QLabel("Device Lifecycle Management System", overlay)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 16px; font-weight: 500; color: #334155;")

        overlay_layout.addWidget(self.logo_label)
        overlay_layout.addWidget(welcome_label)
        overlay_layout.addWidget(subtitle_label)

        panel_layout.addWidget(overlay, alignment=Qt.AlignmentFlag.AlignCenter)
        panel_layout.addStretch(1)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        self._refresh_logo()
        super().resizeEvent(event)

    def _refresh_logo(self) -> None:
        if self._logo_source.isNull():
            self.logo_label.clear()
            return

        target_width = max(160, min(420, int(self.width() * 0.32)))
        pixmap = self._logo_source.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
