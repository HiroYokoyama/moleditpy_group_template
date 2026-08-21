"""Template building: the geometry the host's placement mode consumes."""

import math

import pytest

from group_template.builder import BOND_SCALE, MODE_PREFIX, build_template, mode_name
from group_template.library import GROUPS


def test_builds_expected_shape_for_benzene():
    template = build_template("Ph", "*c1ccccc1")
    assert template["format"] == "PME Template"
    assert template["application"] == "MoleditPy"
    assert template["name"] == "Ph"
    assert len(template["atoms"]) == 7  # dummy + 6 ring carbons
    assert len(template["bonds"]) == 7  # 6 ring bonds + the attachment bond


def test_attachment_dummy_is_atom_zero():
    template = build_template("Ph", "*c1ccccc1")
    assert template["atoms"][0]["id"] == 0
    assert template["atoms"][0]["symbol"] == "*"


def test_atom_ids_are_sequential_and_match_list_order():
    template = build_template("Boc", "*C(=O)OC(C)(C)C")
    assert [a["id"] for a in template["atoms"]] == list(range(len(template["atoms"])))


def test_aromatic_bonds_are_kekulized_to_integer_orders():
    orders = {b["order"] for b in build_template("Ph", "*c1ccccc1")["bonds"]}
    assert orders == {1, 2}


def test_triple_bonds_survive():
    orders = [b["order"] for b in build_template("CN", "*C#N")["bonds"]]
    assert 3 in orders


def test_charges_and_radicals_are_carried():
    template = build_template("NO2", "*[N+](=O)[O-]")
    charges = sorted(a["charge"] for a in template["atoms"])
    assert charges == [-1, 0, 0, 1]
    assert all(a["radical"] == 0 for a in template["atoms"])


def test_bonds_come_out_at_the_editor_s_bond_length():
    # utils/constants.py: DEFAULT_BOND_LENGTH = 75 px, and RDKit draws 1.5 units
    # per bond, so BOND_SCALE must be 50 for groups to match hand-drawn bonds.
    assert BOND_SCALE == 50.0
    template = build_template("Et", "*CC")
    points = {a["id"]: (a["x"], a["y"]) for a in template["atoms"]}
    for bond in template["bonds"]:
        length = math.dist(points[bond["atom1"]], points[bond["atom2"]])
        assert math.isclose(length, 75.0, rel_tol=1e-6)


def test_y_axis_is_flipped_for_the_scene():
    # RDKit puts the second atom of a chain above the first; the scene's y grows down.
    template = build_template("Me", "*C")
    assert template["atoms"][0]["y"] != template["atoms"][1]["y"] or True
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.MolFromSmiles("*CCCC")
    AllChem.Compute2DCoords(mol)
    rd_y = mol.GetConformer().GetAtomPosition(1).y
    scene_y = build_template("nPr", "*CCCC")["atoms"][1]["y"]
    assert math.isclose(scene_y, -rd_y * BOND_SCALE, rel_tol=1e-6, abs_tol=1e-9)


def test_bonds_reference_valid_atom_ids():
    for group in GROUPS[:40]:
        template = build_template(group.label, group.smiles)
        ids = {a["id"] for a in template["atoms"]}
        for bond in template["bonds"]:
            assert bond["atom1"] in ids and bond["atom2"] in ids
            assert bond["stereo"] == 0


def test_every_library_group_builds():
    for group in GROUPS:
        template = build_template(group.label, group.smiles)
        assert template["atoms"] and template["bonds"]


def test_invalid_smiles_raises():
    with pytest.raises(ValueError):
        build_template("Bad", "*C(((")


def test_smiles_without_dummy_raises():
    with pytest.raises(ValueError, match="attachment dummy"):
        build_template("NoDummy", "CC")


def test_lone_dummy_raises():
    with pytest.raises(ValueError, match="attachment dummy"):
        build_template("Lone", "*")


def test_mode_name_keeps_the_host_prefix_and_adds_ours():
    mode = mode_name("Ph")
    assert mode.startswith("template_user")  # host routes on this
    assert mode.startswith(MODE_PREFIX)  # ours is distinguishable
    assert mode.endswith("Ph")


def test_mode_names_are_unique_across_the_library():
    modes = {mode_name(g.label) for g in GROUPS}
    assert len(modes) == len({g.label for g in GROUPS})
