"""Placement must bond to the clicked atom, never overwrite it."""

from group_template.builder import build_template
from group_template.placement import PlacementOverride, place_fragment

from .fakes import FakeScene

MODE_PREFIX = "template_user_GroupTemplate: "


def context_for(label, smiles, attachment=None):
    """Mimic the template_context the host hands to the commit step."""
    template = build_template(label, smiles)
    return template, {
        "points": [(a["x"], a["y"]) for a in template["atoms"]],
        "atoms_data": template["atoms"],
        "bonds_info": [
            (b["atom1"], b["atom2"], b["order"], b["stereo"]) for b in template["bonds"]
        ],
        "attachment_atom": attachment,
    }


def test_clicked_atom_keeps_its_element():
    scene = FakeScene()
    clicked = scene.add_existing_atom("C")
    _, ctx = context_for("OMe", "*OC", clicked)

    place_fragment(scene, ctx)

    assert clicked.symbol == "C"
    assert scene.data.atoms[clicked.atom_id]["symbol"] == "C"


def test_dummy_is_not_created_when_attaching():
    scene = FakeScene()
    clicked = scene.add_existing_atom("C")
    template, ctx = context_for("Ph", "*c1ccccc1", clicked)

    place_fragment(scene, ctx)

    assert "*" not in scene.created
    assert len(scene.created) == len(template["atoms"]) - 1


def test_group_is_bonded_to_the_clicked_atom():
    scene = FakeScene()
    clicked = scene.add_existing_atom("N")
    _, ctx = context_for("Ph", "*c1ccccc1", clicked)

    place_fragment(scene, ctx)

    attached = [b for b in scene.bonded if clicked.atom_id in b[:2]]
    assert len(attached) == 1
    assert clicked.symbol == "N"


def test_free_placement_keeps_the_dummy_visible():
    scene = FakeScene()
    template, ctx = context_for("Ph", "*c1ccccc1", None)

    place_fragment(scene, ctx)

    assert scene.created.count("*") == 1
    assert len(scene.created) == len(template["atoms"])


def test_bond_orders_are_preserved():
    scene = FakeScene()
    clicked = scene.add_existing_atom("C")
    _, ctx = context_for("CN", "*C#N", clicked)

    place_fragment(scene, ctx)

    assert 3 in [b[2] for b in scene.bonded]


def test_existing_bond_is_not_duplicated():
    scene = FakeScene()
    clicked = scene.add_existing_atom("C")
    _, ctx = context_for("Me", "*C", clicked)

    place_fragment(scene, ctx)
    first = len(scene.bonded)
    place_fragment(scene, ctx)

    assert len(scene.bonded) > first  # a second methyl is a new atom, new bond
    assert len(set(scene.data.bonds)) == len(scene.data.bonds)


def test_placed_atoms_are_restyled():
    scene = FakeScene()
    clicked = scene.add_existing_atom("C")
    _, ctx = context_for("Ph", "*c1ccccc1", clicked)

    place_fragment(scene, ctx)

    assert clicked.styled >= 1


def test_empty_context_is_ignored():
    scene = FakeScene()
    place_fragment(scene, {"points": [], "atoms_data": []})
    assert scene.created == []


def test_malformed_bond_entries_are_skipped():
    scene = FakeScene()
    _, ctx = context_for("Me", "*C", None)
    ctx["bonds_info"] = [(0,), "nonsense", (0, 1, 1, 0)]

    place_fragment(scene, ctx)

    assert len(scene.bonded) == 1


def test_override_intercepts_our_mode():
    scene = FakeScene()
    override = PlacementOverride(scene, MODE_PREFIX)
    assert override.install()

    scene.mode = MODE_PREFIX + "Ph"
    clicked = scene.add_existing_atom("C")
    _, ctx = context_for("Ph", "*c1ccccc1", clicked)
    result = scene.add_user_template_fragment(ctx)

    assert result != "host"
    assert clicked.symbol == "C"
    assert len(scene.created) == 6


def test_override_passes_foreign_modes_to_the_host():
    scene = FakeScene()
    override = PlacementOverride(scene, MODE_PREFIX)
    override.install()

    scene.mode = "template_user_MyOwnTemplate"
    _, ctx = context_for("Ph", "*c1ccccc1", None)
    assert scene.add_user_template_fragment(ctx) == "host"
    assert scene.created == []


def test_override_restores_the_host_method():
    scene = FakeScene()
    override = PlacementOverride(scene, MODE_PREFIX)
    override.install()
    assert "add_user_template_fragment" in scene.__dict__

    override.remove()

    assert "add_user_template_fragment" not in scene.__dict__
    assert scene.add_user_template_fragment({}) == "host"
    assert not override.installed


def test_remove_is_idempotent():
    scene = FakeScene()
    override = PlacementOverride(scene, MODE_PREFIX)
    override.install()
    override.remove()
    override.remove()
    assert scene.add_user_template_fragment({}) == "host"


def test_install_without_a_scene_is_harmless():
    override = PlacementOverride(None, MODE_PREFIX)
    assert override.install() is False
    override.remove()


def test_install_is_not_doubled():
    scene = FakeScene()
    override = PlacementOverride(scene, MODE_PREFIX)
    override.install()
    shadow = scene.add_user_template_fragment
    override.install()
    assert scene.add_user_template_fragment is shadow


def test_commit_failure_is_swallowed():
    scene = FakeScene()
    override = PlacementOverride(scene, MODE_PREFIX)
    override.install()
    scene.mode = MODE_PREFIX + "Ph"

    # atoms_data without the 'id' key raises inside place_fragment
    scene.add_user_template_fragment(
        {"points": [(0, 0)], "atoms_data": [{"symbol": "C"}], "bonds_info": []}
    )
