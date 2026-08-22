"""The group palette: a filterable grid of clickable structure tiles.

Clicking a tile hands the group to the host's own user-template placement mode,
which draws the hover preview and snaps to a nearby atom. What that click then
does is this plugin's own (see placement.py): the group is bonded to the clicked
atom instead of replacing it. Nothing here touches the user's files: the only
state the palette can keep is the recently used list, in Qt settings, and only
once the user ticks Save history.

The dialog follows the host's User Templates dialog where the two overlap --
thumbnails drawn with the editor's own items, the same teardown back to
``atom_C`` including the view cursor -- and adds what a 310-entry palette needs
that a handful of user templates does not: ranked search, keyboard picking,
recently used groups and a grid that reflows with the window.
"""

import logging
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QEvent, QSettings, Qt, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
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

from . import host_preview
from .builder import build_template, mode_name, MODE_PREFIX
from .library import Group, categories, search
from .placement import PlacementOverride, PreviewOverride
from .preview import render_pixmap

logger = logging.getLogger(__name__)

# The id __init__.py registers this dialog under; teardown has to release it.
WINDOW_ID = "palette"

ALL_CATEGORIES = "All categories"
RECENT_CATEGORY = "Recently used"
MAX_RECENT = 12

_MIN_COLUMNS = 2
_TILE_W = 132
_TILE_H = 124
_GRID_SPACING = 8
_PREVIEW_W = 120
_PREVIEW_H = 84
_DEFAULT_MODE = "atom_C"
_SETTINGS_ORG = "MoleditPy"
_SETTINGS_APP = "GroupTemplatePlugin"
_RECENT_KEY = "group_template/recent"
_SAVE_HISTORY_KEY = "group_template/save_history"

_NORMAL_STYLE = """
QFrame { border: 1px solid palette(mid); border-radius: 6px; }
QFrame:hover { border: 1px solid palette(highlight); background: palette(alternate-base); }
"""
_SELECTED_STYLE = """
QFrame { border: 2px solid palette(highlight); border-radius: 6px;
         background: palette(alternate-base); }
"""
_FOCUS_STYLE = """
QFrame { border: 1px dashed palette(highlight); border-radius: 6px; }
"""


class GroupTile(QFrame):
    """One clickable library entry: structure thumbnail above its name.

    The thumbnail is drawn the first time the tile is actually painted. Drawing
    all 310 up front costs over a second, and a filtered palette never shows
    more than a screenful of them.
    """

    def __init__(self, group: Group, pixmap_source: Any, on_click: Any) -> None:
        super().__init__()
        self.group = group
        self._pixmap_source = pixmap_source
        self._on_click = on_click
        self._selected = False
        self.setFixedSize(_TILE_W, _TILE_H)
        self.setStyleSheet(_NORMAL_STYLE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Pickable from the keyboard, so search -> arrows -> Enter never needs
        # the mouse.
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        tip = group.aliases or group.label
        self.setToolTip(f"{group.label} — {tip}\nSMILES: {group.smiles}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setFixedHeight(_PREVIEW_H)
        self.image.setStyleSheet("border: none;")
        layout.addWidget(self.image)

        name = QLabel(group.label)
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name.setWordWrap(True)
        name.setStyleSheet("border: none;")
        layout.addWidget(name)

    def ensure_pixmap(self) -> None:
        """Draw the thumbnail if it has not been drawn yet."""
        if not self.image.pixmap().isNull():
            return
        pixmap = self._pixmap_source(self.group)
        if pixmap is not None:
            self.image.setPixmap(pixmap)

    def invalidate_pixmap(self) -> None:
        """Forget the thumbnail; the next paint redraws it (theme changes)."""
        self.image.clear()

    def paintEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Fill in the thumbnail on the first paint, then paint as usual."""
        self.ensure_pixmap()
        super().paintEvent(event)

    def mousePressEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Select this group; the placement itself happens on the canvas."""
        # A right-click belongs to a context menu somewhere else, not to a pick.
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus(Qt.FocusReason.MouseFocusReason)
            self._on_click(self.group, self)
        super().mousePressEvent(event)

    def keyPressEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Enter or Space picks the focused tile; the arrows are the grid's."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self._on_click(self.group, self)
            event.accept()
            return
        super().keyPressEvent(event)

    def set_selected(self, selected: bool) -> None:
        """Highlight or unhighlight the tile."""
        self._selected = selected
        self._restyle()

    def _restyle(self) -> None:
        if self._selected:
            self.setStyleSheet(_SELECTED_STYLE)
        elif self.hasFocus():
            self.setStyleSheet(_FOCUS_STYLE)
        else:
            self.setStyleSheet(_NORMAL_STYLE)

    def focusInEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Show where the keyboard is without claiming to be the pick."""
        super().focusInEvent(event)
        self._restyle()

    def focusOutEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        super().focusOutEvent(event)
        self._restyle()


class GroupPaletteDialog(QDialog):
    """Non-modal browser over the static group library."""

    def __init__(self, context: Any, parent: Any = None) -> None:
        super().__init__(parent)
        self.context = context
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._pixmaps: Dict[str, Any] = {}
        self._tile_cache: Dict[str, GroupTile] = {}
        self._tiles: List[GroupTile] = []
        self._columns = 5
        self._torn_down = False
        self.selected_tile: Optional[GroupTile] = None
        self.selected_label: Optional[str] = None
        self.save_history: bool = self._load_save_history()
        self.recent: List[str] = self._load_recent()

        self.setWindowTitle("Group Template")
        self.setModal(False)
        self.resize(760, 620)
        self._place_beside_parent()
        self._build_ui()
        self.refresh_grid()

        # Groups bond to the clicked atom; the host would replace it instead.
        self.override = PlacementOverride(self._scene(), MODE_PREFIX)
        self.override.install()
        # ...and the hover preview has to show that, not a replacement.
        self.preview_override = PreviewOverride(self._scene(), MODE_PREFIX)
        self.preview_override.install()

        # The host resets the mode on its own (Esc, another tool) and offers no
        # signal for it; drop our highlight when that happens instead of showing
        # a stale selection.
        self._poll = QTimer(self)
        self._poll.setInterval(400)
        self._poll.timeout.connect(self._sync_selection)
        self._poll.start()

    # --- UI ---

    def _place_beside_parent(self) -> None:
        """Sit top-right of the editor, like the host's User Templates dialog."""
        parent = self.parent()
        if parent is None:
            return
        try:
            geometry = parent.geometry()
            self.move(geometry.right() - self.width() - 20, geometry.top() + 50)
        except (AttributeError, RuntimeError, TypeError):
            pass

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        filters = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Search name, alias or category (e.g. tosyl, tert butyl, silyl)"
        )
        self.search_box.setClearButtonEnabled(True)
        self.search_box.textChanged.connect(self.refresh_grid)
        self.search_box.returnPressed.connect(self.select_first)
        filters.addWidget(self.search_box, 1)

        self.category_box = QComboBox()
        self.category_box.addItem(ALL_CATEGORIES)
        self.category_box.addItem(RECENT_CATEGORY)
        self.category_box.addItems(categories())
        self.category_box.currentIndexChanged.connect(self.refresh_grid)
        filters.addWidget(self.category_box)
        layout.addLayout(filters)

        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setSpacing(_GRID_SPACING)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.grid_host)
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll, 1)

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
        self.armed_label = QLabel()
        buttons.addWidget(self.armed_label)
        buttons.addStretch()

        self.history_box = QCheckBox("Save history")
        self.history_box.setToolTip(
            "Keep the Recently used list between sessions. Off by default; "
            "unticking it forgets what was stored."
        )
        # Set before connecting, so restoring the saved state is not itself a
        # change the user made.
        self.history_box.setChecked(self.save_history)
        self.history_box.toggled.connect(self.set_save_history)
        buttons.addWidget(self.history_box)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    # --- filtering ---

    def visible_groups(self) -> List[Group]:
        """The groups the current search text and category select, in tile order."""
        category = self.category_box.currentText()
        if category == RECENT_CATEGORY:
            matched = {g.label: g for g in search(self.search_box.text(), "")}
            return [matched[label] for label in self.recent if label in matched]
        if category == ALL_CATEGORIES:
            category = ""
        return search(self.search_box.text(), category)

    def refresh_grid(self) -> None:
        """Re-lay the tile grid for the current search text and category."""
        groups = self.visible_groups()

        self.grid_host.setUpdatesEnabled(False)
        try:
            for tile in self._tiles:
                self.grid.removeWidget(tile)
                tile.hide()
            self._tiles = []

            position = 0
            for group in groups:
                tile = self._tile_for(group)
                if tile is None:
                    # No thumbnail: skip the entry without leaving a hole.
                    continue
                self.grid.addWidget(
                    tile, position // self._columns, position % self._columns
                )
                tile.show()
                self._tiles.append(tile)
                position += 1
        finally:
            self.grid_host.setUpdatesEnabled(True)

        self._restore_selection()
        self.count_label.setText(f"{len(self._tiles)} of {len(search('', ''))} groups")

    def _restore_selection(self) -> None:
        """Re-highlight the armed group after a rebuild, if it is still on show.

        Filtering does not disarm the editor, so the highlight has to survive a
        rebuild -- otherwise the canvas is still placing Ph with nothing in the
        palette saying so.
        """
        self.selected_tile = None
        if self.selected_label is None:
            return
        for tile in self._tiles:
            tile.set_selected(tile.group.label == self.selected_label)
            if tile.group.label == self.selected_label:
                self.selected_tile = tile

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
            ratio = self.devicePixelRatioF()
            # First choice: the editor's own items, so a tile looks like what
            # gets drawn. Falls back to the plugin's plain painter off-host.
            pixmap = host_preview.render_pixmap(
                template, _PREVIEW_W, _PREVIEW_H, self._scene(), ratio
            )
            if pixmap is None:
                pixmap = render_pixmap(
                    template,
                    _PREVIEW_W,
                    _PREVIEW_H,
                    self.palette().color(self.foregroundRole()),
                    ratio,
                )
            self._pixmaps[group.label] = pixmap
        return self._pixmaps[group.label]

    def _tile_for(self, group: Group) -> Optional[GroupTile]:
        """Reuse this group's tile; rebuilding 310 of them per keystroke is waste."""
        tile = self._tile_cache.get(group.label)
        if tile is not None:
            return tile
        # A group whose SMILES will not build has nothing to show; the thumbnail
        # itself is drawn later, on the tile's first paint.
        if self.template_for(group) is None:
            return None
        tile = GroupTile(group, self._pixmap_for, self.select_group)
        self._tile_cache[group.label] = tile
        return tile

    # --- placement ---

    def select_first(self) -> None:
        """Pick the best match for the current search; Enter in the search box."""
        if self._tiles:
            self.select_group(self._tiles[0].group, self._tiles[0])

    def select_group(self, group: Group, tile: GroupTile) -> None:
        """Hand the group to the host's user-template placement mode."""
        template = self.template_for(group)
        if template is None:
            return

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
            # Nothing is armed, so nothing should look armed.
            self._set_selection(None)
            return

        self._set_selection(tile)
        self._remember(group.label)
        self.context.show_status_message(
            f"Group: {group.label} — click in the 2D editor"
        )

    def _set_selection(self, tile: Optional[GroupTile]) -> None:
        """Make ``tile`` the one highlighted tile, or clear the highlight."""
        for other in self._tiles:
            other.set_selected(other is tile)
        self.selected_tile = tile
        self.selected_label = tile.group.label if tile is not None else None
        self.armed_label.setText(
            f"Placing: {tile.group.label}" if tile is not None else ""
        )

    # --- recently used ---

    @staticmethod
    def _settings() -> QSettings:
        return QSettings(_SETTINGS_ORG, _SETTINGS_APP)

    def _load_save_history(self) -> bool:
        """Whether the user asked for the recent list to outlive the session.

        Off unless asked for: a palette should not start writing what you drew
        into the settings store on its own.
        """
        try:
            stored = self._settings().value(_SAVE_HISTORY_KEY, False)
        except (RuntimeError, TypeError, ValueError) as exc:
            logger.warning("Could not read the save-history setting: %s", exc)
            return False
        if isinstance(stored, str):  # some backends store booleans as text
            return stored.strip().lower() in ("true", "1", "yes")
        return bool(stored)

    def _load_recent(self) -> List[str]:
        """Labels used last time, newest first; junk in the store is ignored."""
        if not self.save_history:
            return []
        try:
            stored = self._settings().value(_RECENT_KEY, [])
        except (RuntimeError, TypeError, ValueError) as exc:
            logger.warning("Could not read recent groups: %s", exc)
            return []
        if isinstance(stored, str):  # a one-entry list comes back as a bare string
            stored = [stored]
        if not isinstance(stored, (list, tuple)):
            return []
        return [item for item in stored if isinstance(item, str)][:MAX_RECENT]

    def _remember(self, label: str) -> None:
        """Move a group to the front of the recent list, saving it if asked to."""
        self.recent = [label] + [item for item in self.recent if item != label]
        del self.recent[MAX_RECENT:]
        self._save_recent()

    def _save_recent(self) -> None:
        """Write the recent list out, but only while saving is switched on."""
        if not self.save_history:
            return
        try:
            self._settings().setValue(_RECENT_KEY, self.recent)
        except (RuntimeError, TypeError, ValueError) as exc:
            logger.warning("Could not save recent groups: %s", exc)

    def set_save_history(self, enabled: bool) -> None:
        """Turn persistence of the recent list on or off, and act on it now.

        Switching it off is also a request to forget: what is already in the
        settings store goes, and the list only lives until the palette closes.
        """
        self.save_history = bool(enabled)
        try:
            settings = self._settings()
            settings.setValue(_SAVE_HISTORY_KEY, self.save_history)
            if not self.save_history:
                settings.remove(_RECENT_KEY)
        except (AttributeError, RuntimeError, TypeError, ValueError) as exc:
            logger.warning("Could not store the save-history setting: %s", exc)
            return
        self._save_recent()

    # --- keyboard and layout ---

    def keyPressEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Esc clears a filter first; only an empty search box closes the palette."""
        if event.key() == Qt.Key.Key_Escape and self.search_box.text():
            self.search_box.clear()
            event.accept()
            return
        if (
            event.key() == Qt.Key.Key_Down
            and self.search_box.hasFocus()
            and self._tiles
        ):
            self._tiles[0].setFocus(Qt.FocusReason.TabFocusReason)
            event.accept()
            return
        if self._move_focus(event.key()):
            event.accept()
            return
        super().keyPressEvent(event)

    def _move_focus(self, key: int) -> bool:
        """Walk the grid with the arrow keys; True when the key was ours."""
        steps = {
            Qt.Key.Key_Left: -1,
            Qt.Key.Key_Right: 1,
            Qt.Key.Key_Up: -self._columns,
            Qt.Key.Key_Down: self._columns,
        }
        if key not in steps or not self._tiles:
            return False
        focused = self.focusWidget()
        current = next(
            (i for i, tile in enumerate(self._tiles) if tile is focused), None
        )
        if current is None:
            return False
        target = current + steps[key]
        if not 0 <= target < len(self._tiles):
            return True  # at an edge: swallow it rather than jumping elsewhere
        self._tiles[target].setFocus(Qt.FocusReason.TabFocusReason)
        return True

    def resizeEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Reflow the grid so a wider window shows more tiles per row."""
        super().resizeEvent(event)
        # The scroll area has not been re-laid out yet at this point, so its
        # viewport still reports the old width; let the layout settle first.
        # The host's own dialog defers its preview refit for the same reason.
        QTimer.singleShot(0, self.reflow)

    def reflow(self) -> None:
        """Re-lay the grid if the window now fits a different number of tiles."""
        columns = self._columns_for_width(self.scroll.viewport().width())
        if columns != self._columns:
            self._columns = columns
            self.refresh_grid()

    @staticmethod
    def _columns_for_width(width: int) -> int:
        """How many tiles fit across ``width``, never fewer than _MIN_COLUMNS."""
        return max(_MIN_COLUMNS, (width + _GRID_SPACING) // (_TILE_W + _GRID_SPACING))

    # --- host plumbing ---

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
        if self.selected_label is None or self._in_our_mode():
            return
        try:
            self._set_selection(None)
        except RuntimeError:  # a tile was already destroyed under us
            self.selected_tile = None
            self.selected_label = None

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
            self._restore_view_cursor(scene)
            scene.update()
        except (AttributeError, RuntimeError, ValueError) as exc:
            logger.warning("Could not clear template preview: %s", exc)

    @staticmethod
    def _restore_view_cursor(scene: Any) -> None:
        """Put the drawing cursor back, as the host's own dialog does.

        Without it the canvas keeps whatever cursor template mode left behind.
        """
        try:
            views = scene.views()
        except (AttributeError, RuntimeError, TypeError):
            return
        for view in views:
            try:
                view.setCursor(Qt.CursorShape.CrossCursor)
                view.viewport().update()
            except (AttributeError, RuntimeError, TypeError) as exc:
                logger.warning("Could not restore the canvas cursor: %s", exc)

    def changeEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Redraw the thumbnails when the theme changes under us.

        They are cached with the text colour baked in, so a palette switch
        (the Dark Mode Theme plugin does exactly this) would otherwise leave
        dark strokes on a dark tile.
        """
        if event.type() == QEvent.Type.PaletteChange and self._pixmaps:
            self._pixmaps.clear()
            for tile in self._tile_cache.values():
                tile.invalidate_pixmap()
            self.refresh_grid()
        super().changeEvent(event)

    # --- teardown ---

    def _teardown(self) -> None:
        # close() after reject() would otherwise run all of this twice.
        if self._torn_down:
            return
        self._torn_down = True
        self._poll.stop()
        self.override.remove()
        self.preview_override.remove()
        self._leave_template_mode()
        # Without this the next open reuses a dead window and picking dies.
        self.context.register_window(WINDOW_ID, None)

    def closeEvent(self, event: Any) -> None:  # noqa: N802 (Qt naming)
        """Leave template mode when the palette is closed."""
        self._teardown()
        event.accept()

    def reject(self) -> None:
        """Esc never reaches closeEvent, so tear down from here too."""
        self._teardown()
        super().reject()
