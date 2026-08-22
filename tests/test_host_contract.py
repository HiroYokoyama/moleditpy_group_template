"""Pin the host internals this plugin depends on.

Placement shadows a scene method and relies on how the host routes template
modes. None of that is part of PluginContext, so if the main app renames or
reshapes it this plugin would silently fall back to replacing the clicked atom.
These tests read the main app's source when the repos are siblings.
"""

import os
from pathlib import Path

import pytest

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
_CANDIDATES = [
    Path(os.environ["CI_MAIN_APP_SRC"]).resolve()
    if os.environ.get("CI_MAIN_APP_SRC")
    else None,
    _PLUGIN_ROOT.parent / "python_molecular_editor" / "moleditpy" / "src",
    _PLUGIN_ROOT / "python_molecular_editor" / "moleditpy" / "src",
]
_APP_SRC = next(
    (p for p in _CANDIDATES if p and (p / "moleditpy" / "ui").is_dir()), None
)

pytestmark = pytest.mark.skipif(
    _APP_SRC is None, reason="main app (python_molecular_editor) not found"
)


def read(relative):
    return (_APP_SRC / "moleditpy" / relative).read_text(encoding="utf-8")


def test_scene_still_exposes_the_commit_step_we_shadow():
    assert "def add_user_template_fragment(" in read("ui/molecular_scene_handler.py")


def test_commit_step_is_reached_through_the_scene_click_handler():
    source = read("ui/molecule_scene.py")
    assert 'self.mode.startswith("template_user")' in source
    assert "self.add_user_template_fragment(" in source


def test_host_still_replaces_the_clicked_atom():
    # The behaviour this plugin deliberately bypasses; if it goes away, revisit.
    source = read("ui/molecular_scene_handler.py")
    assert "_apply_template_atom_to_existing" in source


def test_template_context_keys_are_unchanged():
    source = read("ui/molecular_scene_handler.py")
    for key in ("points", "bonds_info", "atoms_data", "attachment_atom"):
        assert f'"{key}"' in source


def test_attachment_lines_up_with_template_atom_zero():
    source = read("ui/molecular_scene_handler.py")
    assert 'atoms[0]["x"]' in source and 'atoms[0]["y"]' in source


def test_main_window_exposes_the_template_data_setter():
    assert "def set_scene_user_template_data(" in read("ui/main_window.py")


def test_ui_manager_accepts_arbitrary_user_template_mode_names():
    source = read("ui/ui_manager.py")
    assert 'mode_str.startswith("template_user")' in source
    assert "def set_mode_and_update_toolbar(" in source


def test_host_pushes_undo_itself_after_placement():
    # Why the plugin must not push its own checkpoint.
    source = read("ui/molecule_scene.py")
    assert "push_undo_state()" in source


def test_editor_bond_length_matches_our_scale():
    from group_template.builder import BOND_SCALE

    source = read("utils/constants.py")
    line = next(
        line for line in source.splitlines() if line.startswith("DEFAULT_BOND_LENGTH")
    )
    default_bond_length = int(line.split("=")[1].split("#")[0].strip())
    # RDKit lays out 1.5 units per bond.
    assert BOND_SCALE * 1.5 == default_bond_length


def test_scene_attributes_reset_on_teardown_exist():
    source = read("ui/molecular_scene_handler.py") + read("ui/molecule_scene.py")
    for attribute in ("user_template_data", "template_context", "template_preview"):
        assert attribute in source


def test_host_preview_helpers_are_still_exported():
    # Thumbnails are drawn with the editor's own items so a tile looks like what
    # gets placed; without these the palette falls back to its plain painter.
    source = read("ui/preview_molecule.py")
    assert "class PreviewScene(" in source
    assert "def build_preview_items(" in source
    assert "def preview_content_rect(" in source


def test_user_template_dialog_renders_thumbnails_the_same_way():
    # The pattern this palette copies; if the host's own dialog stops using it,
    # revisit whether it is still the right thing to imitate.
    source = read("ui/user_template_dialog.py")
    assert "build_preview_items" in source
    assert "preview_content_rect" in source


def test_host_restores_the_drawing_cursor_when_leaving_template_mode():
    # Teardown mirrors this; the palette must not leave a stale canvas cursor.
    source = read("ui/user_template_dialog.py")
    assert "CrossCursor" in source
    assert "scene.views()" in source
