"""Thumbnail geometry (pure) and the rendered pixmap (Qt)."""

import math

import pytest

from group_template.builder import build_template
from group_template.preview import (
    ATTACHMENT_ID,
    atom_label,
    fit_transform,
    render_pixmap,
    transform_point,
)


def atoms(*coords):
    return [{"id": i, "x": x, "y": y, "symbol": "C"} for i, (x, y) in enumerate(coords)]


def test_empty_atom_list_centres_without_dividing_by_zero():
    scale, dx, dy = fit_transform([], 100, 80)
    assert (scale, dx, dy) == (1.0, 50.0, 40.0)


def test_single_atom_is_centred():
    scale, dx, dy = fit_transform(atoms((25, 25)), 100, 80)
    x, y = transform_point({"x": 25, "y": 25}, scale, dx, dy)
    assert math.isclose(x, 50.0) and math.isclose(y, 40.0)


def test_scale_is_capped_so_small_groups_are_not_blown_up():
    scale, _, _ = fit_transform(atoms((0, 0), (10, 0)), 400, 400)
    assert scale == 1.0


def test_large_group_is_scaled_down_to_fit():
    scale, dx, dy = fit_transform(atoms((0, 0), (1000, 0)), 100, 80, pad=10)
    assert scale < 1.0
    x0, _ = transform_point({"x": 0, "y": 0}, scale, dx, dy)
    x1, _ = transform_point({"x": 1000, "y": 0}, scale, dx, dy)
    assert x0 >= 9.9 and x1 <= 90.1


def test_content_is_centred_on_both_axes():
    scale, dx, dy = fit_transform(atoms((-50, -20), (50, 20)), 120, 84)
    xs = [transform_point(a, scale, dx, dy)[0] for a in atoms((-50, -20), (50, 20))]
    ys = [transform_point(a, scale, dx, dy)[1] for a in atoms((-50, -20), (50, 20))]
    assert math.isclose(sum(xs) / 2, 60.0, abs_tol=1e-6)
    assert math.isclose(sum(ys) / 2, 42.0, abs_tol=1e-6)


@pytest.mark.parametrize(
    "atom,expected",
    [
        ({"symbol": "C"}, ""),
        ({"symbol": "O"}, "O"),
        ({"symbol": "*"}, "*"),
        ({"symbol": "N", "charge": 1}, "N+"),
        ({"symbol": "O", "charge": -1}, "O−"),
        ({"symbol": "N", "charge": 2}, "N2+"),
        ({"symbol": "C", "charge": 1}, "C+"),
        ({"symbol": "C", "radical": 1}, "C•"),
        ({"symbol": "C", "charge": None, "radical": None}, ""),
    ],
)
def test_atom_label(atom, expected):
    assert atom_label(atom) == expected


def test_attachment_id_is_zero():
    assert ATTACHMENT_ID == 0


def test_dummy_is_labelled_in_every_library_thumbnail():
    template = build_template("Ph", "*c1ccccc1")
    assert atom_label(template["atoms"][ATTACHMENT_ID]) == "*"


def test_render_pixmap_produces_an_image(qapp):
    from PyQt6.QtGui import QColor

    pixmap = render_pixmap(
        build_template("Boc", "*C(=O)OC(C)(C)C"), 120, 84, QColor("black")
    )
    assert not pixmap.isNull()
    assert (pixmap.width(), pixmap.height()) == (120, 84)


def test_render_pixmap_honours_device_pixel_ratio(qapp):
    from PyQt6.QtGui import QColor

    pixmap = render_pixmap(
        build_template("Me", "*C"), 120, 84, QColor("black"), ratio=2.0
    )
    assert (pixmap.width(), pixmap.height()) == (240, 168)
    assert pixmap.devicePixelRatio() == 2.0


def test_render_pixmap_survives_an_empty_template(qapp):
    from PyQt6.QtGui import QColor

    pixmap = render_pixmap({"atoms": [], "bonds": []}, 40, 40, QColor("black"))
    assert not pixmap.isNull()


def test_render_pixmap_ignores_bonds_with_unknown_atoms(qapp):
    from PyQt6.QtGui import QColor

    template = build_template("Me", "*C")
    template["bonds"].append({"atom1": 0, "atom2": 99, "order": 1, "stereo": 0})
    assert not render_pixmap(template, 60, 60, QColor("black")).isNull()


def test_every_library_group_renders(qapp):
    from PyQt6.QtGui import QColor

    from group_template.library import GROUPS

    for group in GROUPS:
        template = build_template(group.label, group.smiles)
        assert not render_pixmap(template, 120, 84, QColor("black")).isNull()


def test_a_charged_carbon_counts_as_labelled():
    """A bond has to stop short of every label atom_label() actually draws.

    "C+" is written even though the symbol is the hidden one, so keying the
    trim off the raw symbol drew the line straight through the charge.
    """
    from group_template.preview import atom_label

    charged = {"id": 1, "symbol": "C", "x": 0.0, "y": 0.0, "charge": 1}
    plain = {"id": 2, "symbol": "C", "x": 50.0, "y": 0.0, "charge": 0}
    assert atom_label(charged) and not atom_label(plain)


def test_a_charged_carbon_bond_is_trimmed(qapp):
    from PyQt6.QtGui import QColor

    from group_template.preview import render_pixmap

    template = {
        "atoms": [
            {"id": 0, "symbol": "C", "x": -50.0, "y": 0.0, "charge": 1},
            {"id": 1, "symbol": "C", "x": 50.0, "y": 0.0, "charge": 0},
        ],
        "bonds": [{"atom1": 0, "atom2": 1, "order": 1}],
    }
    plain = {
        "atoms": [dict(a, charge=0) for a in template["atoms"]],
        "bonds": template["bonds"],
    }
    charged_image = render_pixmap(template, 120, 84, QColor("black")).toImage()
    plain_image = render_pixmap(plain, 120, 84, QColor("black")).toImage()
    # The charge is drawn and the bond stops short of it; keying the trim off
    # the raw symbol drew the line straight through the label instead.
    assert charged_image != plain_image
