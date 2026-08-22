"""What the palette added on top of a plain grid: search ranking, keyboard
picking, recently used groups, a reflowing grid and the bugs those exposed."""

import pytest
from PyQt6.QtCore import QEvent, QPoint, Qt
from PyQt6.QtGui import QKeyEvent, QMouseEvent

from group_template.builder import MODE_PREFIX
from group_template.palette_dialog import (
    ALL_CATEGORIES,
    MAX_RECENT,
    RECENT_CATEGORY,
    GroupPaletteDialog,
    _RECENT_KEY,
    _SAVE_HISTORY_KEY,
)

from .fakes import FakeContext


@pytest.fixture
def store(monkeypatch):
    """A settings store of our own; a real QSettings would write the user's."""
    values = {_SAVE_HISTORY_KEY: True}
    monkeypatch.setattr(
        GroupPaletteDialog, "_settings", staticmethod(lambda: _FakeSettings(values))
    )
    return values


@pytest.fixture
def dialog(qapp, store):
    context = FakeContext()
    win = GroupPaletteDialog(context)
    yield win
    win.override.remove()
    win.deleteLater()


class _FakeSettings:
    """QSettings stand-in backed by a dict, so tests touch no real store."""

    def __init__(self, values):
        self.values = values

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):  # noqa: N802 (Qt naming)
        self.values[key] = list(value) if isinstance(value, (list, tuple)) else value

    def remove(self, key):
        self.values.pop(key, None)


def key_event(key):
    return QKeyEvent(QEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier)


def press(tile, button):
    return QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPoint(5, 5).toPointF(),
        button,
        button,
        Qt.KeyboardModifier.NoModifier,
    )


# --- search ---


def test_the_exact_abbreviation_comes_first(dialog):
    dialog.search_box.setText("me")
    # "Me" is what someone typing "me" wants, not "Methallyl" or "MEM".
    assert dialog._tiles[0].group.label == "Me"


def test_a_multi_word_query_narrows_instead_of_failing(dialog):
    dialog.search_box.setText("tert butyl")
    assert dialog._tiles[0].group.label == "tBu"


def test_a_category_name_is_searchable(dialog):
    dialog.search_box.setText("nucleobase")
    assert dialog._tiles and all(
        t.group.category == "Nucleobase" for t in dialog._tiles
    )


# --- keyboard ---


def test_enter_in_the_search_box_picks_the_best_match(dialog):
    dialog.search_box.setText("boc")
    dialog.search_box.returnPressed.emit()

    assert dialog.selected_label == "Boc"
    modes = dialog.context.get_main_window().ui_manager.modes
    assert modes[-1] == MODE_PREFIX + "Boc"


def test_enter_with_no_matches_does_nothing(dialog):
    dialog.search_box.setText("definitely-not-a-group")
    dialog.select_first()
    assert dialog.selected_label is None


def test_enter_on_a_focused_tile_picks_it(dialog):
    tile = dialog._tiles[3]
    tile.keyPressEvent(key_event(Qt.Key.Key_Return))
    assert dialog.selected_tile is tile


def test_arrow_keys_walk_the_grid(dialog):
    dialog._tiles[0].setFocus()
    dialog.keyPressEvent(key_event(Qt.Key.Key_Right))
    assert dialog.focusWidget() is dialog._tiles[1]

    dialog.keyPressEvent(key_event(Qt.Key.Key_Down))
    assert dialog.focusWidget() is dialog._tiles[1 + dialog._columns]


def test_arrow_at_the_edge_stays_put(dialog):
    dialog._tiles[0].setFocus()
    dialog.keyPressEvent(key_event(Qt.Key.Key_Left))
    assert dialog.focusWidget() is dialog._tiles[0]


def test_escape_clears_the_filter_before_closing(dialog):
    dialog.search_box.setText("boc")
    dialog.keyPressEvent(key_event(Qt.Key.Key_Escape))

    assert dialog.search_box.text() == ""
    assert not dialog._torn_down  # the palette is still open


# --- mouse ---


def test_a_right_click_is_not_a_pick(dialog):
    tile = dialog._tiles[0]
    tile.mousePressEvent(press(tile, Qt.MouseButton.RightButton))
    assert dialog.selected_tile is None


def test_a_left_click_is(dialog):
    tile = dialog._tiles[0]
    tile.mousePressEvent(press(tile, Qt.MouseButton.LeftButton))
    assert dialog.selected_tile is tile


# --- selection ---


def test_filtering_keeps_the_armed_group_highlighted(dialog):
    tile = next(t for t in dialog._tiles if t.group.label == "Ph")
    dialog.select_group(tile.group, tile)

    dialog.search_box.setText("ph")

    # The editor is still placing Ph, so the palette must still say so.
    assert dialog.selected_label == "Ph"
    assert dialog.selected_tile is not None
    assert dialog.selected_tile.group.label == "Ph"


def test_filtering_the_armed_group_away_leaves_it_armed(dialog):
    tile = next(t for t in dialog._tiles if t.group.label == "Ph")
    dialog.select_group(tile.group, tile)

    dialog.search_box.setText("boc")

    assert dialog.selected_tile is None  # nothing on screen to highlight
    assert dialog.selected_label == "Ph"  # but the editor is still placing it


def test_the_armed_group_is_named_in_the_dialog(dialog):
    tile = next(t for t in dialog._tiles if t.group.label == "Ph")
    dialog.select_group(tile.group, tile)
    assert "Ph" in dialog.armed_label.text()

    dialog.context.get_main_window().scene.mode = "atom_C"
    dialog._sync_selection()
    assert dialog.armed_label.text() == ""


def test_a_rejected_mode_leaves_nothing_highlighted(dialog):
    main_window = dialog.context.get_main_window()

    def refuse(_mode):
        raise RuntimeError("no")

    main_window.ui_manager.set_mode_and_update_toolbar = refuse
    tile = dialog._tiles[0]
    dialog.select_group(tile.group, tile)

    assert dialog.selected_tile is None
    assert dialog.context.messages  # the user was told


# --- recently used ---


def test_picking_a_group_records_it(dialog):
    tile = next(t for t in dialog._tiles if t.group.label == "Ph")
    dialog.select_group(tile.group, tile)
    assert dialog.recent[0] == "Ph"


def test_the_newest_pick_leads_and_never_repeats(dialog):
    for label in ("Ph", "Me", "Ph"):
        tile = next(t for t in dialog._tiles if t.group.label == label)
        dialog.select_group(tile.group, tile)
    assert dialog.recent == ["Ph", "Me"]


def test_the_recent_list_is_capped(dialog):
    for tile in dialog._tiles[: MAX_RECENT + 5]:
        dialog.select_group(tile.group, tile)
    assert len(dialog.recent) == MAX_RECENT


def test_the_recent_category_shows_them_newest_first(dialog):
    for label in ("Ph", "Me", "Boc"):
        tile = next(t for t in dialog._tiles if t.group.label == label)
        dialog.select_group(tile.group, tile)

    dialog.category_box.setCurrentText(RECENT_CATEGORY)

    assert [t.group.label for t in dialog._tiles] == ["Boc", "Me", "Ph"]


def test_the_recent_category_is_empty_before_anything_is_picked(dialog):
    dialog.category_box.setCurrentText(RECENT_CATEGORY)
    assert dialog._tiles == []


def test_search_still_applies_inside_the_recent_category(dialog):
    for label in ("Ph", "Me"):
        tile = next(t for t in dialog._tiles if t.group.label == label)
        dialog.select_group(tile.group, tile)

    dialog.category_box.setCurrentText(RECENT_CATEGORY)
    dialog.search_box.setText("phenyl")

    assert [t.group.label for t in dialog._tiles] == ["Ph"]


@pytest.mark.parametrize(
    "stored,expected",
    [
        (["Ph", 3, None, "Me"], ["Ph", "Me"]),  # a hand-edited store
        ("Ph", ["Ph"]),  # QSettings hands a one-entry list back as a string
        ({"not": "a list"}, []),
        (["X"] * (MAX_RECENT + 4), ["X"] * MAX_RECENT),
    ],
)
def test_a_junk_recent_store_is_ignored(qapp, monkeypatch, stored, expected):
    values = {_SAVE_HISTORY_KEY: True, _RECENT_KEY: stored}
    monkeypatch.setattr(
        GroupPaletteDialog, "_settings", staticmethod(lambda: _FakeSettings(values))
    )
    win = GroupPaletteDialog(FakeContext())
    try:
        assert win.recent == expected
    finally:
        win.close()


# --- layout ---


def test_a_wider_window_fits_more_tiles_per_row():
    assert GroupPaletteDialog._columns_for_width(700) > (
        GroupPaletteDialog._columns_for_width(400)
    )


def test_a_narrow_window_never_drops_below_one_column():
    assert GroupPaletteDialog._columns_for_width(10) >= 2


def test_reflowing_keeps_every_tile(dialog):
    before = len(dialog._tiles)
    dialog._columns = 3
    dialog.refresh_grid()
    assert len(dialog._tiles) == before
    positions = {
        (dialog.grid.getItemPosition(i)[0], dialog.grid.getItemPosition(i)[1])
        for i in range(dialog.grid.count())
    }
    assert len(positions) == before  # no two tiles share a cell


# --- teardown ---


def test_teardown_runs_once(dialog):
    scene = dialog.context.get_main_window().scene
    tile = dialog._tiles[0]
    dialog.select_group(tile.group, tile)
    scene.mode = MODE_PREFIX + tile.group.label

    dialog.reject()
    dialog.close()  # a second teardown must not re-enter the host

    assert scene.mode == "atom_C"
    assert dialog.context.windows["palette"] is None


def test_the_default_category_is_still_everything(dialog):
    assert dialog.category_box.currentText() == ALL_CATEGORIES


# --- host plumbing ---


def test_the_palette_sits_beside_the_editor(qapp):
    from PyQt6.QtWidgets import QWidget

    parent = QWidget()
    parent.setGeometry(100, 100, 1200, 800)
    win = GroupPaletteDialog(FakeContext(), parent)
    try:
        # Top-right of the editor, like the host's own User Templates dialog.
        assert win.x() > parent.x()
        assert win.y() >= parent.y()
    finally:
        win.close()
        parent.deleteLater()


def test_a_parent_without_a_geometry_is_survived(qapp, monkeypatch):
    win = GroupPaletteDialog(FakeContext())
    try:
        monkeypatch.setattr(win, "parent", lambda: object())
        win._place_beside_parent()  # must not raise
    finally:
        win.close()


def test_teardown_puts_the_drawing_cursor_back(dialog):
    scene = dialog.context.get_main_window().scene
    view = _FakeView()
    scene.views = lambda: [view]
    tile = dialog._tiles[0]
    dialog.select_group(tile.group, tile)
    scene.mode = MODE_PREFIX + tile.group.label

    dialog.close()

    assert view.cursor == Qt.CursorShape.CrossCursor
    assert view.viewport_updates == 1


def test_a_view_that_refuses_a_cursor_is_survived(dialog):
    scene = dialog.context.get_main_window().scene

    class Hostile:
        def setCursor(self, _shape):  # noqa: N802 (Qt naming)
            raise RuntimeError("gone")

    scene.views = lambda: [Hostile()]
    tile = dialog._tiles[0]
    dialog.select_group(tile.group, tile)
    scene.mode = MODE_PREFIX + tile.group.label

    dialog.close()  # must not raise

    assert scene.mode == "atom_C"


def test_a_scene_without_views_is_survived(dialog):
    scene = dialog.context.get_main_window().scene
    tile = dialog._tiles[0]
    dialog.select_group(tile.group, tile)
    scene.mode = MODE_PREFIX + tile.group.label

    dialog.close()  # FakeScene has no views()

    assert scene.mode == "atom_C"


class _FakeView:
    """Stands in for the editor's QGraphicsView during teardown."""

    def __init__(self):
        self.cursor = None
        self.viewport_updates = 0

    def setCursor(self, shape):  # noqa: N802 (Qt naming)
        self.cursor = shape

    def viewport(self):
        return self

    def update(self):
        self.viewport_updates += 1


# --- odds and ends ---


def test_an_unrelated_key_reaches_the_dialog(dialog):
    dialog.keyPressEvent(key_event(Qt.Key.Key_A))  # must not be swallowed
    assert not dialog._torn_down


def test_arrows_do_nothing_when_no_tile_has_focus(dialog):
    dialog.search_box.setFocus()
    assert dialog._move_focus(Qt.Key.Key_Right) is False


def test_a_resize_reflows_the_grid(qapp, dialog):
    dialog.show()
    dialog.resize(420, 620)
    qapp.processEvents()  # the reflow waits for the layout to settle
    narrow = dialog._columns

    dialog.resize(1100, 620)
    qapp.processEvents()

    assert dialog._columns > narrow
    assert dialog._columns == dialog._columns_for_width(
        dialog.scroll.viewport().width()
    )
    assert len(dialog._tiles) > 0


def test_focus_and_selection_style_the_tile_differently(qapp, dialog):
    dialog.show()
    qapp.processEvents()
    tile = dialog._tiles[0]
    plain = tile.styleSheet()
    tile.setFocus()
    assert tile.hasFocus()
    assert tile.styleSheet() != plain
    tile.set_selected(True)
    selected = tile.styleSheet()
    tile.clearFocus()
    assert tile.styleSheet() == selected  # selection outranks focus
    tile.set_selected(False)
    assert tile.styleSheet() == plain


def test_a_broken_settings_store_does_not_stop_the_palette(qapp, monkeypatch):
    class Broken:
        def value(self, *_a, **_k):
            raise RuntimeError("registry is unhappy")

        def setValue(self, *_a, **_k):  # noqa: N802 (Qt naming)
            raise RuntimeError("registry is unhappy")

    monkeypatch.setattr(GroupPaletteDialog, "_settings", staticmethod(Broken))
    win = GroupPaletteDialog(FakeContext())
    try:
        assert win.recent == []
        win.save_history = True  # even then, a store that raises is survivable
        tile = win._tiles[0]
        win.select_group(tile.group, tile)  # must not raise
        assert win.recent == [tile.group.label]
    finally:
        win.close()


# --- the save-history setting ---


def test_history_is_not_saved_unless_asked_for(qapp, monkeypatch):
    values = {}  # a first-ever run: nothing stored at all
    monkeypatch.setattr(
        GroupPaletteDialog, "_settings", staticmethod(lambda: _FakeSettings(values))
    )
    win = GroupPaletteDialog(FakeContext())
    try:
        assert win.save_history is False
        assert win.history_box.isChecked() is False

        tile = win._tiles[0]
        win.select_group(tile.group, tile)

        # Usable this session, but nothing was written down.
        assert win.recent == [tile.group.label]
        assert _RECENT_KEY not in values
    finally:
        win.close()


def test_a_stored_history_is_ignored_while_the_box_is_off(qapp, monkeypatch):
    values = {_RECENT_KEY: ["Ph"]}  # left over from when it was switched on
    monkeypatch.setattr(
        GroupPaletteDialog, "_settings", staticmethod(lambda: _FakeSettings(values))
    )
    win = GroupPaletteDialog(FakeContext())
    try:
        assert win.recent == []
    finally:
        win.close()


def test_ticking_the_box_starts_saving(qapp, monkeypatch):
    values = {}
    monkeypatch.setattr(
        GroupPaletteDialog, "_settings", staticmethod(lambda: _FakeSettings(values))
    )
    win = GroupPaletteDialog(FakeContext())
    try:
        tile = win._tiles[0]
        win.select_group(tile.group, tile)

        win.history_box.setChecked(True)

        assert values[_SAVE_HISTORY_KEY] is True
        # What is already in the list is saved too, not just what comes next.
        assert values[_RECENT_KEY] == [tile.group.label]
    finally:
        win.close()


def test_unticking_the_box_forgets_what_was_stored(qapp, store):
    win = GroupPaletteDialog(FakeContext())
    try:
        tile = win._tiles[0]
        win.select_group(tile.group, tile)
        assert store[_RECENT_KEY] == [tile.group.label]

        win.history_box.setChecked(False)

        assert store[_SAVE_HISTORY_KEY] is False
        assert _RECENT_KEY not in store
        # The list still works for the rest of the session.
        assert win.recent == [tile.group.label]
    finally:
        win.close()


def test_the_setting_survives_a_reopen(qapp, monkeypatch):
    values = {}
    monkeypatch.setattr(
        GroupPaletteDialog, "_settings", staticmethod(lambda: _FakeSettings(values))
    )
    first = GroupPaletteDialog(FakeContext())
    first.history_box.setChecked(True)
    tile = first._tiles[0]
    first.select_group(tile.group, tile)
    first.close()

    second = GroupPaletteDialog(FakeContext())
    try:
        assert second.save_history is True
        assert second.history_box.isChecked() is True
        assert second.recent == [tile.group.label]
    finally:
        second.close()


@pytest.mark.parametrize(
    "stored,expected",
    [("true", True), ("false", False), ("1", True), (True, True), (0, False)],
)
def test_a_text_boolean_from_the_settings_backend_is_read(
    qapp, monkeypatch, stored, expected
):
    values = {_SAVE_HISTORY_KEY: stored}
    monkeypatch.setattr(
        GroupPaletteDialog, "_settings", staticmethod(lambda: _FakeSettings(values))
    )
    win = GroupPaletteDialog(FakeContext())
    try:
        assert win.save_history is expected
    finally:
        win.close()
