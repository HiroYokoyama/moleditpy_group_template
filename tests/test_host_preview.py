"""Thumbnails drawn with the editor's own items, and the fallback when the
host does not offer them."""

import pytest

from group_template import host_preview
from group_template.builder import build_template
from group_template.palette_dialog import GroupPaletteDialog

from .fakes import FakeContext


@pytest.fixture
def template():
    return build_template("Ph", "*c1ccccc1")


def test_no_host_means_no_host_thumbnail(qapp, monkeypatch, template):
    monkeypatch.setattr(host_preview, "_helpers", lambda: None)
    assert host_preview.available() is False
    assert host_preview.render_pixmap(template, 120, 84) is None


def test_an_empty_template_is_refused(qapp, monkeypatch, template):
    monkeypatch.setattr(host_preview, "_helpers", lambda: ("a", "b", "c"))
    assert host_preview.render_pixmap({"atoms": []}, 120, 84) is None


def test_a_broken_host_falls_back_instead_of_raising(qapp, monkeypatch, template):
    def explode(*_args, **_kwargs):
        raise RuntimeError("host preview changed shape")

    monkeypatch.setattr(host_preview, "_helpers", lambda: (explode, explode, explode))
    assert host_preview.render_pixmap(template, 120, 84) is None


def test_the_palette_always_gets_a_thumbnail(qapp, monkeypatch):
    """With or without the host renderer, every tile ends up with a pixmap."""
    monkeypatch.setattr(host_preview, "render_pixmap", lambda *a, **k: None)
    win = GroupPaletteDialog(FakeContext())
    try:
        tile = win._tiles[0]
        tile.ensure_pixmap()
        assert not tile.image.pixmap().isNull()
    finally:
        win.close()


def test_the_bond_indices_the_host_wants_are_positions_not_ids(template):
    """build_preview_items indexes into its atom list, so ids must be mapped."""
    shifted = {
        "atoms": [dict(atom, id=atom["id"] + 100) for atom in template["atoms"]],
        "bonds": [
            {**bond, "atom1": bond["atom1"] + 100, "atom2": bond["atom2"] + 100}
            for bond in template["bonds"]
        ],
    }
    _atoms, bonds = host_preview._preview_inputs(shifted)
    assert bonds and all(
        0 <= first < len(shifted["atoms"]) and 0 <= second < len(shifted["atoms"])
        for first, second, *_rest in bonds
    )


def test_a_bond_to_a_missing_atom_is_dropped(template):
    broken = {
        "atoms": template["atoms"],
        "bonds": template["bonds"] + [{"atom1": 0, "atom2": 999, "order": 1}],
    }
    _atoms, bonds = host_preview._preview_inputs(broken)
    assert len(bonds) == len(template["bonds"])
