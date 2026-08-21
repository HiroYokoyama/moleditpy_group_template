"""Turn a library SMILES into a MoleditPy user-template dictionary.

The host consumes the same ``PME Template`` structure its own User Templates
dialog writes, and lines template atom 0 up with the atom you click. Here atom 0
is a ``*`` dummy, so the group's real atoms land one bond away and the clicked
atom keeps its element — ``placement.py`` commits it that way.
"""

from typing import Any, Dict, List

from rdkit import Chem
from rdkit.Chem import AllChem

# RDKit lays 2D structures out with 1.5 units per bond and the editor draws a
# bond as DEFAULT_BOND_LENGTH = 75 px, so 50 px/unit matches hand-drawn bonds.
BOND_SCALE = 50.0

# Prefix keeps this plugin's modes distinct from the user's own templates.
MODE_PREFIX = "template_user_GroupTemplate: "

_BOND_ORDERS = {
    Chem.BondType.SINGLE: 1,
    Chem.BondType.DOUBLE: 2,
    Chem.BondType.TRIPLE: 3,
}


def build_template(label: str, smiles: str) -> Dict[str, Any]:
    """Build a PME Template dict for one group. Raises ValueError on bad SMILES."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES for group '{label}': {smiles}")
    if mol.GetNumAtoms() < 2 or mol.GetAtomWithIdx(0).GetAtomicNum() != 0:
        raise ValueError(
            f"Group '{label}' must start with a '*' attachment dummy: {smiles}"
        )

    # Integer bond orders only: aromatic bonds must become alternating 1/2.
    Chem.Kekulize(mol, clearAromaticFlags=True)
    AllChem.Compute2DCoords(mol)
    conf = mol.GetConformer()

    atoms: List[Dict[str, Any]] = []
    for i, atom in enumerate(mol.GetAtoms()):
        pos = conf.GetAtomPosition(i)
        atoms.append(
            {
                "id": i,
                "symbol": atom.GetSymbol(),
                "x": pos.x * BOND_SCALE,
                # Scene y grows downward, RDKit's grows upward.
                "y": -pos.y * BOND_SCALE,
                "charge": atom.GetFormalCharge(),
                "radical": atom.GetNumRadicalElectrons(),
            }
        )

    bonds: List[Dict[str, Any]] = []
    for bond in mol.GetBonds():
        bonds.append(
            {
                "atom1": bond.GetBeginAtomIdx(),
                "atom2": bond.GetEndAtomIdx(),
                "order": _BOND_ORDERS.get(bond.GetBondType(), 1),
                "stereo": 0,
            }
        )

    return {
        "format": "PME Template",
        "version": "1.0",
        "application": "MoleditPy",
        "name": label,
        "atoms": atoms,
        "bonds": bonds,
    }


def mode_name(label: str) -> str:
    """Scene mode string for a group; keeps the host's ``template_user`` prefix."""
    return f"{MODE_PREFIX}{label}"
