"""The palette dialog: filtering, tile clicks, mode handling and teardown."""

import pytest

from group_template.builder import MODE_PREFIX
from group_template.library import GROUPS
from group_template.palette_dialog import ALL_CATEGORIES, GroupPaletteDialog

from .fakes import FakeContext


@pytest.fixture
def dialog(qapp):
    context = FakeContext()
    win = GroupPaletteDialog(context)
    yield win
    win.override.remove()
    win.deleteLater()


def test_all_groups_are_shown_by_default(dialog):
    assert len(dialog._tiles) == len(GROUPS)
    assert dialog.category_box.currentText() == ALL_CATEGORIES


def test_every_tile_shows_its_name_and_a_thumbnail(dialog):
    tile = dialog._tiles[0]
    labels = tile.findChildren(type(tile.children()[-1]))
    assert tile.group.label in [w.text() for w in labels if hasattr(w, "text")]
    assert any(
        getattr(w, "pixmap", lambda: None)() is not None and not w.pixmap().isNull()
        for w in tile.findChildren(object)
        if hasattr(w, "pixmap")
    )


def test_tooltip_carries_the_alias_and_smiles(dialog):
    tile = next(t for t in dialog._tiles if t.group.label == "Ts")
    assert "tosyl" in tile.toolTip()
    assert tile.group.smiles in tile.toolTip()


def test_search_narrows_the_grid(dialog):
    dialog.search_box.setText("tosyl")
    assert [t.group.label for t in dialog._tiles] == ["Ts", "OTs", "NHTs"]


def test_category_filter_narrows_the_grid(dialog):
    dialog.category_box.setCurrentText("Silyl")
    assert dialog._tiles and all(t.group.category == "Silyl" for t in dialog._tiles)


def test_count_label_reports_the_filtered_total(dialog):
    dialog.search_box.setText("tosyl")
    assert dialog.count_label.text() == f"3 of {len(GROUPS)} groups"


def test_clearing_the_search_restores_everything(dialog):
    dialog.search_box.setText("tosyl")
    dialog.search_box.setText("")
    assert len(dialog._tiles) == len(GROUPS)


def test_clicking_a_tile_enters_our_template_mode(dialog):
    tile = next(t for t in dialog._tiles if t.group.label == "Ph")
    dialog.select_group(tile.group, tile)

    main_window = dialog.context.get_main_window()
    assert main_window.ui_manager.modes[-1] == MODE_PREFIX + "Ph"
    assert main_window.template_data["name"] == "Ph"
    assert main_window.template_data["atoms"][0]["symbol"] == "*"
    assert dialog.selected_tile is tile


def test_only_one_tile_is_highlighted(dialog):
    first, second = dialog._tiles[0], dialog._tiles[1]
    dialog.select_group(first.group, first)
    dialog.select_group(second.group, second)
    assert dialog.selected_tile is second


def test_placement_override_is_installed_on_open(dialog):
    scene = dialog.context.get_main_window().scene
    assert dialog.override.installed
    assert "add_user_template_fragment" in scene.__dict__


def test_templates_are_cached(dialog):
    group = dialog._tiles[0].group
    assert dialog.template_for(group) is dialog.template_for(group)


def test_selection_clears_when_the_editor_leaves_our_mode(dialog):
    tile = dialog._tiles[0]
    dialog.select_group(tile.group, tile)
    dialog.context.get_main_window().scene.mode = "atom_C"

    dialog._sync_selection()

    assert dialog.selected_tile is None


def test_selection_is_kept_while_our_mode_is_active(dialog):
    tile = dialog._tiles[0]
    dialog.select_group(tile.group, tile)
    dialog.context.get_main_window().scene.mode = MODE_PREFIX + tile.group.label

    dialog._sync_selection()

    assert dialog.selected_tile is tile


def test_close_restores_the_editor_and_releases_the_window(qapp):
    context = FakeContext()
    win = GroupPaletteDialog(context)
    scene = context.get_main_window().scene
    tile = win._tiles[0]
    win.select_group(tile.group, tile)
    scene.mode = MODE_PREFIX + tile.group.label

    win.close()

    assert scene.mode == "atom_C"
    assert scene.user_template_data is None
    assert scene.template_context == {}
    assert "add_user_template_fragment" not in scene.__dict__
    assert context.windows["palette"] is None


def test_escape_tears_down_too(qapp):
    context = FakeContext()
    win = GroupPaletteDialog(context)
    scene = context.get_main_window().scene
    tile = win._tiles[0]
    win.select_group(tile.group, tile)
    scene.mode = MODE_PREFIX + tile.group.label

    win.reject()  # Esc goes here, never through closeEvent

    assert scene.mode == "atom_C"
    assert not win.override.installed


def test_close_leaves_a_foreign_template_mode_alone(qapp):
    context = FakeContext()
    win = GroupPaletteDialog(context)
    scene = context.get_main_window().scene
    scene.mode = "template_user_SomeUserTemplate"
    scene.user_template_data = {"name": "SomeUserTemplate"}

    win.close()

    assert scene.mode == "template_user_SomeUserTemplate"
    assert scene.user_template_data == {"name": "SomeUserTemplate"}


def test_dialog_without_a_main_window_does_not_crash(qapp):
    context = FakeContext(main_window=None)
    context.main_window = None
    win = GroupPaletteDialog(context)
    tile = win._tiles[0]
    win.select_group(tile.group, tile)  # no host to talk to
    win.close()
    assert context.windows["palette"] is None


def test_thumbnails_are_redrawn_when_the_theme_changes(dialog):
    from PyQt6.QtCore import QEvent

    dialog.search_box.setText("Boc")
    first = dialog._pixmaps["Boc"]

    dialog.changeEvent(QEvent(QEvent.Type.PaletteChange))

    # Stale pixmaps would be dark strokes on a dark tile after a theme switch.
    assert dialog._pixmaps["Boc"] is not first
    assert [t.group.label for t in dialog._tiles] == ["Boc", "NHBoc"]


def test_theme_change_before_anything_is_drawn_is_harmless(qapp):
    from PyQt6.QtCore import QEvent

    context = FakeContext()
    win = GroupPaletteDialog(context)
    win._pixmaps.clear()
    win.changeEvent(QEvent(QEvent.Type.PaletteChange))
    win.close()
