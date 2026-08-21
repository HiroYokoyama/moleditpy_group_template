"""The library is static data, so its invariants are worth pinning down."""

import json
from pathlib import Path

import pytest
from rdkit import Chem

from group_template.library import GROUPS, categories, search


def test_library_is_large():
    assert len(GROUPS) > 250


@pytest.mark.parametrize("group", GROUPS, ids=lambda g: g.label)
def test_every_smiles_parses_with_a_single_attachment_dummy(group):
    mol = Chem.MolFromSmiles(group.smiles)
    assert mol is not None, f"{group.label}: {group.smiles} does not parse"

    dummies = [a for a in mol.GetAtoms() if a.GetAtomicNum() == 0]
    assert len(dummies) == 1, f"{group.label} must have exactly one '*'"

    first = mol.GetAtomWithIdx(0)
    assert first.GetAtomicNum() == 0, f"{group.label}: '*' must be atom 0"
    assert first.GetDegree() == 1, f"{group.label}: '*' must have one bond"
    assert mol.GetNumAtoms() >= 2, f"{group.label} has no real atoms"


@pytest.mark.parametrize("group", GROUPS, ids=lambda g: g.label)
def test_every_group_kekulizes(group):
    mol = Chem.MolFromSmiles(group.smiles)
    Chem.Kekulize(mol, clearAromaticFlags=True)
    for bond in mol.GetBonds():
        assert bond.GetBondType() in (
            Chem.BondType.SINGLE,
            Chem.BondType.DOUBLE,
            Chem.BondType.TRIPLE,
        )


def test_labels_are_unique_per_category():
    seen = set()
    for group in GROUPS:
        key = (group.category, group.label)
        assert key not in seen, f"duplicate entry {key}"
        seen.add(key)


def test_every_group_has_a_category_and_label():
    for group in GROUPS:
        assert group.label.strip() == group.label and group.label
        assert group.category in categories()


def test_categories_are_in_library_order_without_duplicates():
    result = categories()
    assert len(result) == len(set(result))
    assert result[0] == GROUPS[0].category


def test_search_matches_label_case_insensitively():
    assert any(g.label == "Boc" for g in search("boc"))


def test_search_matches_alias():
    labels = [g.label for g in search("tosyl")]
    assert "Ts" in labels


def test_search_filters_by_category():
    result = search("", "Silyl")
    assert result and all(g.category == "Silyl" for g in result)


def test_search_combines_query_and_category():
    result = search("TB", "Silyl")
    assert {g.label for g in result} == {"TBS", "TBDPS"}


def test_empty_search_returns_everything():
    assert len(search("", "")) == len(GROUPS)


def test_search_ignores_surrounding_whitespace():
    assert [g.label for g in search("  Mes  ")][0] == "Mes"


def test_unknown_query_returns_nothing():
    assert search("definitely-not-a-group") == []


# Structures that were wrong once, plus the positional isomers most easily
# mixed up. Each reference is written from the name, independently of library.py.
REFERENCE_STRUCTURES = {
    "9-Anthryl": "*c1c2ccccc2cc2ccccc12",  # was a phenanthrene skeleton
    "1-Pyrenyl": "*c1ccc2ccc3cccc4ccc1c2c34",  # was pyren-2-yl
    "DMB": "*Cc1ccc(OC)cc1OC",  # was the 3,4 isomer (veratryl)
    "1-Ad": "*C12CC3CC(CC(C3)C1)C2",
    "2-Ad": "*C1C2CC3CC(C2)CC1C3",
    "2-Norbornyl": "*C1CC2CCC1C2",
    "Bicyclopentyl": "*C12CC(C1)C2",
    "o-Tol": "*c1ccccc1C",
    "m-Tol": "*c1cccc(C)c1",
    "p-Tol": "*c1ccc(C)cc1",
    "Mes": "*c1c(C)cc(C)cc1C",
    "3-Furyl": "*c1ccoc1",
    "3-Thienyl": "*c1ccsc1",
    "2-Py": "*c1ccccn1",
    "3-Py": "*c1cccnc1",
    "4-Py": "*c1ccncc1",
    "Styryl": "*C=Cc1ccccc1",
    "Cinnamyl": "*CC=Cc1ccccc1",
    "Trp": "*Cc1c[nH]c2ccccc12",
    "Bpin": "*B1OC(C)(C)C(C)(C)O1",
}


@pytest.mark.parametrize("label,reference", sorted(REFERENCE_STRUCTURES.items()))
def test_structure_matches_its_name(label, reference):
    group = next(g for g in GROUPS if g.label == label)
    assert Chem.CanonSmiles(group.smiles) == Chem.CanonSmiles(reference)


def test_no_two_entries_in_a_category_share_a_structure():
    # Cross-category repeats are deliberate (Bn is findable under Aryl and as a
    # protecting group); two identical tiles in one category are just noise.
    seen = {}
    for group in GROUPS:
        key = (group.category, Chem.CanonSmiles(group.smiles))
        assert key not in seen, f"{group.label} duplicates {seen.get(key)}"
        seen[key] = group.label


def test_styryl_and_cinnamyl_are_distinct():
    styryl = next(g for g in GROUPS if g.label == "Styryl")
    cinnamyl = next(g for g in GROUPS if g.label == "Cinnamyl")
    assert Chem.CanonSmiles(styryl.smiles) != Chem.CanonSmiles(cinnamyl.smiles)
    assert "cinnamyl" not in styryl.aliases.lower()


# --- name-verified structures -------------------------------------------

# tests/opsin_reference.json records, per entry, a name from its own label or
# aliases that OPSIN (the IUPAC name parser) read as exactly this structure.
# It is the audit that caught 9-Anthryl, 1-Pyrenyl, DMB and 3-Pyridazinyl.
_REFERENCE_PATH = Path(__file__).parent / "opsin_reference.json"
_REFERENCE = json.loads(_REFERENCE_PATH.read_text(encoding="utf-8"))["structures"]

# Entries no name parser can confirm: pure abbreviations (OTs, NHBoc), organo-
# metallics (MgBr, Li) and trivial names with no systematic form. Each was
# checked by hand and by molecular formula instead. Adding a group means either
# a name OPSIN understands, or a deliberate line here.
NAME_UNVERIFIABLE = {
    "Ac-O",
    "Asn",
    "B(OH)2",
    "BF3-",
    "Bn-N",
    "Bneop",
    "Bpin",
    "Bz-O",
    "CO2Bn",
    "CO2Ph",
    "CO2tBu",
    "COF",
    "CONHMe",
    "CONHPh",
    "CONMe2",
    "COSMe",
    "CSNH2",
    "Cys",
    "Gln",
    "Glu",
    "HgCl",
    "Li",
    "Met",
    "MgBr",
    "N-Succinimidyl",
    "NHBoc",
    "NHCbz",
    "NHTs",
    "NMe3+",
    "NO2",
    "OMs",
    "OPO(OEt)2",
    "OTBS",
    "OTf",
    "OTs",
    "Oxalyl-OMe",
    "PO(OEt)2",
    "PO(OMe)2",
    "PPh3+",
    "Piv-O",
    "SAc",
    "SO2Cl",
    "Thr",
    "Trt-N",
    "Weinreb",
    "Xanthate",
    "ZnBr",
}


@pytest.mark.parametrize("label", sorted(_REFERENCE))
def test_structure_still_matches_the_name_opsin_read(label):
    group = next((g for g in GROUPS if g.label == label), None)
    assert group is not None, f"{label} vanished from the library"
    assert Chem.CanonSmiles(group.smiles) == _REFERENCE[label]["smiles"], (
        f"{label} no longer matches '{_REFERENCE[label]['name']}'"
    )


def test_every_group_is_name_verified_or_explicitly_exempt():
    unchecked = {
        g.label
        for g in GROUPS
        if g.label not in _REFERENCE and g.label not in NAME_UNVERIFIABLE
    }
    assert not unchecked, (
        f"add a parseable name or an exemption for: {sorted(unchecked)}"
    )


def test_exemption_list_has_no_stale_entries():
    labels = {g.label for g in GROUPS}
    assert not (NAME_UNVERIFIABLE - labels), "exemption list mentions missing groups"
    assert not (NAME_UNVERIFIABLE & set(_REFERENCE)), (
        "exempt entry is actually verified"
    )
