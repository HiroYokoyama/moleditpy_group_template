"""The group palette: a filterable grid of clickable structure tiles.

Clicking a tile hands the group to the host's own user-template placement mode,
which draws the hover preview and snaps to a nearby atom. What that click then
does is this plugin's own (see placement.py): the group is bonded to the clicked
atom instead of replacing it. This plugin never writes anything.
"""

import logging
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .builder import build_template, mode_name, MODE_PREFIX
from .library import Group, categories, search
from .placement import PlacementOverride, PreviewOverride
from .preview import render_pixmap

logger = logging.getLogger(__name__)

ALL_CATEGORIES = "All categories"
_COLUMNS = 5
_TILE_W = 132
_TILE_H = 124
_PREVIEW_W = 120
_PREVIEW_H = 84
_DEFAULT_MODE = "atom_C"

_NORMAL_STYLE = """
QFrame { border: 1px solid palette(mid); border-radius: 6px; }
QFrame:hover { border: 1px solid palette(highlight); background: palette(alternate-base); }
"""
_SELECTED_STYLE = """
QFrame { border: 2px solid palette(highlight); border-radius: 6px;
         background: palette(alternate-base); }
"""


class GroupTile(QFrame):
    """One clickable library entry: structure thumbnail above its name."""

    def __init__(self, group: Group, pixmap: Any, on_click: Any) -> None:
        super().__init__()
        self.group = group
        self._on_click = on_click
        self.setFixedSize(_TILE_W, _TILE_H)
        self.setStyleSheet(_NORMAL_STYLE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        tip = group.aliases or group.label
        self.setToolTip(f"{group.label} — {tip}\nSMILES: {group.smiles}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        image = QLabel()
        image.setPixmap(pixmap)
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.setFixedHeight(_PREVIEW_H)
        layout.addWidget(image)

        name = QLabel(group.label)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setWordWrap(True)
        name.setStyleSheet("border: none;")
        layout.addWidget(name)

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Select this group; the placement itself happens on the canvas."""
        self._on_click(self.group, self)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool) -> None:
        """Highlight or unhighlight the tile."""
        self.setStyleSheet(_SELECTED_STYLE if selected else _NORMAL_STYLE)


class GroupPaletteDialog(QDialog):
    """Non-modal browser over the static group library."""

    def __init__(self, context: Any, parent: Any = None) -> None:
        super().__init__(parent)
        self.context = context
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._pixmaps: Dict[str, Any] = {}
        self._tiles: List[GroupTile] = []
        self.selected_tile: Optional[GroupTile] = None

        self.setWindowTitle("Group Template")
        self.setModal(False)
        self.resize(760, 620)
        self._build_ui()
        self.refresh_grid()

        # Groups bond to the clicked atom; the host would replace it instead.
        self.override = PlacementOverride(self._scene(), MODE_PREFIX)
        self.override.install()
        # ...and the hover preview has to show that, not a replacement.
        self.preview_override = PreviewOverride(self._scene(), MODE_PREFIX)
        self.preview_override.install()

        # The host resets the mode on its own (Esc, another tool); drop our
        # highlight when that happens instead of showing a stale selection.
        self._poll = QTimer(self)
        self._poll.setInterval(400)
        self._poll.timeout.connect(self._sync_selection)
        self._poll.start()

    # --- UI ---

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        filters = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search name or alias (e.g. tosyl, Boc)")
        self.search_box.textChanged.connect(self.refresh_grid)
        filters.addWidget(self.search_box, 1)

        self.category_box = QComboBox()
        self.category_box.addItem(ALL_CATEGORIES)
        self.category_box.addItems(categories())
        self.category_box.currentIndexChanged.connect(self.refresh_grid)
        filters.addWidget(self.category_box)
        layout.addLayout(filters)

        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setSpacing(8)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll = QScrollArea()
        scroll.setWidget(self.grid_host)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll, 1)

        self.hint = QLabel(
            "Pick a group, then click in the 2D editor. The * marks where it "
            "attaches: click an existing atom and the group is bonded to it, "
            "keeping that atom's element. Click empty space to drop the group "
            "with its * dummy."
        )
        self.hint.setWordWrap(True)
        layout.addWidget(self.hint)

        buttons = QHBoxLayout()
        self.count_label = QLabel()
        buttons.addWidget(self.count_label)
        buttons.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    def refresh_grid(self) -> None:
        """Rebuild the tile grid for the current search text and category."""
        category = self.category_box.currentText()
        if category == ALL_CATEGORIES:
            category = ""
        groups = search(self.search_box.text(), category)

        self.grid_host.setUpdatesEnabled(False)
        try:
            for i in reversed(range(self.grid.count())):
                item = self.grid.itemAt(i)
                widget = item.widget() if item else None
                if widget is not None:
                    widget.setParent(None)
            self._tiles = []
            self.selected_tile = None

            for index, group in enumerate(groups):
                pixmap = self._pixmap_for(group)
                if pixmap is None:
                    continue
                tile = GroupTile(group, pixmap, self.select_group)
                self.grid.addWidget(tile, index // _COLUMNS, index % _COLUMNS)
                self._tiles.append(tile)
        finally:
            self.grid_host.setUpdatesEnabled(True)

        self.count_label.setText(f"{len(self._tiles)} of {len(search('', ''))} groups")

    # --- data ---

    def template_for(self, group: Group) -> Optional[Dict[str, Any]]:
        """Build (and cache) the PME template for a group."""
        if group.label not in self._templates:
            try:
                self._templates[group.label] = build_template(group.label, group.smiles)
            except (ValueError, RuntimeError) as exc:
                logger.warning("Could not build template for %s: %s", group.label, exc)
                return None
        return self._templates[group.label]

    def _pixmap_for(self, group: Group) -> Any:
        if group.label not in self._pixmaps:
            template = self.template_for(group)
            if template is None:
                return None
            color = self.palette().color(self.foregroundRole())
            self._pixmaps[group.label] = render_pixmap(
                template,
                _PREVIEW_W,
                _PREVIEW_H,
                color,
                self.devicePixelRatioF(),
            )
        return self._pixmaps[group.label]

    # --- placement ---

    def select_group(self, group: Group, tile: GroupTile) -> None:
        """Hand the group to the host's user-template placement mode."""
        template = self.template_for(group)
        if template is None:
            return

        for other in self._tiles:
            other.set_selected(False)
        tile.set_selected(True)
        self.selected_tile = tile

        main_window = self.context.get_main_window()
        if main_window is None:
            return
        try:
            main_window.set_scene_user_template_data(template)
            main_window.ui_manager.set_mode_and_update_toolbar(mode_name(group.label))
        except (AttributeError, RuntimeError, ValueError, TypeError) as exc:
            logger.warning("Could not enter template mode for %s: %s", group.label, exc)
            self.context.show_status_message(
                f"Could not activate '{group.label}' — the editor rejected the mode."
            )

    def _scene(self) -> Any:
        main_window = self.context.get_main_window()
        try:
            return main_window.init_manager.scene
        except AttributeError:
            return None

    def _in_our_mode(self) -> bool:
        scene = self._scene()
        mode = getattr(scene, "mode", "") or ""
        return isinstance(mode, str) and mode.startswith(MODE_PREFIX)

    def _sync_selection(self) -> None:
        """Unhighlight when the editor has left this plugin's template mode."""
        if self.selected_tile is None or self._in_our_mode():
            return
        try:
            self.selected_tile.set_selected(False)
        except RuntimeError:  # tile already destroyed by a grid rebuild
            pass
        self.selected_tile = None

    def _leave_template_mode(self) -> None:
        """Return the editor to normal drawing, but only if we own the mode."""
        if not self._in_our_mode():
            return
        main_window = self.context.get_main_window()
        scene = self._scene()
        try:
            main_window.ui_manager.set_mode_and_update_toolbar(_DEFAULT_MODE)
        except (AttributeError, RuntimeError, ValueError) as exc:
            logger.warning("Could not reset editor mode: %s", exc)
        try:
            scene.mode = _DEFAULT_MODE
            scene.current_atom_symbol = "C"
            scene.user_template_data = None
            scene.template_context = {}
            scene.clear_template_preview()
            if getattr(scene, "template_preview", None):
                scene.template_preview.hide()
            scene.update()
        except (AttributeError, RuntimeError, ValueError) as exc:
            logger.warning("Could not clear template preview: %s", exc)

    def changeEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Redraw the thumbnails when the theme changes under us.

        They are cached with the text colour baked in, so a palette switch
        (the Dark Mode Theme plugin does exactly this) would otherwise leave
        dark strokes on a dark tile.
        """
        if event.type() == QEvent.Type.PaletteChange and self._pixmaps:
            self._pixmaps.clear()
            self.refresh_grid()
        super().changeEvent(event)

    # --- teardown ---

    def _teardown(self) -> None:
        if self._poll is not None:
            self._poll.stop()
        self.override.remove()
        self.preview_override.remove()
        self._leave_template_mode()
        # Without this the next open reuses a dead window and picking dies.
        self.context.register_window("palette", None)

    def closeEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Leave template mode when the palette is closed."""
        self._teardown()
        event.accept()

    def reject(self) -> None:
        """Esc never reaches closeEvent, so tear down from here too."""
        self._teardown()
        super().reject()
