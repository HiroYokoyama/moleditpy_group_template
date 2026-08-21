"""The library is static data, so its invariants are worth pinning down."""

import pytest
from rdkit import Chem

from Group_Template.library import GROUPS, categories, search


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
