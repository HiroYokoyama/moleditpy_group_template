"""Commit a group *next to* the clicked atom instead of overwriting it.

The host's own user-template placement turns the clicked atom into template
atom 0 (``_apply_template_atom_to_existing``). A substituent library wants the
opposite: the clicked atom keeps its element and simply gains a bond to the
group. Since template atom 0 is a ``*`` dummy that lands exactly on the clicked
atom, dropping that dummy and bonding to the clicked atom does it — the geometry the host already computed for the hover preview stays valid.

While the palette owns the mode, ``add_user_template_fragment`` is shadowed on
the scene instance; anything else (the user's own templates) is passed straight
through to the original.
"""

import logging
from typing import Any, Dict, List

from PyQt6.QtGui import QPainterPath

logger = logging.getLogger(__name__)

# The attachment dummy is always written first (see library.py).
ATTACHMENT_INDEX = 0


def place_fragment(scene: Any, template_context: Dict[str, Any]) -> None:
    """Create the group's atoms and bond it to the clicked atom, if any."""
    points = template_context.get("points", [])
    atoms_data = template_context.get("atoms_data", [])
    bonds_info = template_context.get("bonds_info", [])
    attachment_atom = template_context.get("attachment_atom")

    if not points or not atoms_data:
        return

    id_map: Dict[Any, Any] = {}
    for index, (pos, atom_data) in enumerate(zip(points, atoms_data)):
        if index == ATTACHMENT_INDEX and attachment_atom is not None:
            # Bond to the existing atom rather than becoming it: no element change.
            id_map[atom_data["id"]] = attachment_atom.atom_id
            continue
        id_map[atom_data["id"]] = scene.create_atom(
            atom_data.get("symbol", "C"),
            pos,
            atom_data.get("charge", 0),
            atom_data.get("radical", 0),
        )

    index_to_id: List[Any] = [
        atom_data.get("id", i) for i, atom_data in enumerate(atoms_data)
    ]

    for bond_info in bonds_info:
        if not isinstance(bond_info, (list, tuple)) or len(bond_info) < 2:
            continue
        first, second = bond_info[0], bond_info[1]
        order = bond_info[2] if len(bond_info) > 2 else 1
        stereo = bond_info[3] if len(bond_info) > 3 else 0

        if isinstance(first, int) and first < len(index_to_id):
            first = index_to_id[first]
        if isinstance(second, int) and second < len(index_to_id):
            second = index_to_id[second]

        atom1_id = id_map.get(first)
        atom2_id = id_map.get(second)
        if atom1_id is None or atom2_id is None:
            continue
        if (atom1_id, atom2_id) in scene.data.bonds or (
            atom2_id,
            atom1_id,
        ) in scene.data.bonds:
            continue

        atom1_item = scene.atom_items.get(atom1_id)
        atom2_item = scene.atom_items.get(atom2_id)
        if atom1_item and atom2_item:
            scene.create_bond(
                atom1_item, atom2_item, bond_order=order, bond_stereo=stereo
            )

    for atom_id in id_map.values():
        item = scene.atom_items.get(atom_id)
        if item:
            item.update_style()


class PlacementOverride:
    """Installs/removes the scene-level shadow of the host's commit step."""

    def __init__(self, scene: Any, mode_prefix: str) -> None:
        self.scene = scene
        self.mode_prefix = mode_prefix
        self._original: Any = None
        self.installed = False

    def install(self) -> bool:
        """Shadow the host's commit while the palette is open."""
        if self.installed or self.scene is None:
            return self.installed
        try:
            self._original = self.scene.add_user_template_fragment
            self.scene.add_user_template_fragment = self._commit
            self.installed = True
        except (AttributeError, TypeError) as exc:
            logger.warning("Could not install group placement: %s", exc)
            self.installed = False
        return self.installed

    def remove(self) -> None:
        """Restore the host's own commit step."""
        if not self.installed:
            return
        try:
            # Deleting the instance attribute unshadows the host's class method.
            del self.scene.add_user_template_fragment
        except (AttributeError, TypeError):
            pass
        # Nothing underneath means the original was itself an instance attribute.
        if (
            self._original is not None
            and getattr(self.scene, "add_user_template_fragment", None) is None
        ):
            self.scene.add_user_template_fragment = self._original
        self.installed = False

    def _commit(self, template_context: Dict[str, Any]) -> Any:
        mode = getattr(self.scene, "mode", "") or ""
        if not (isinstance(mode, str) and mode.startswith(self.mode_prefix)):
            # A user template is being placed — leave the host's behaviour alone.
            if self._original is not None:
                return self._original(template_context)
            return None
        try:
            place_fragment(self.scene, template_context)
        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
            logger.warning("Could not place group: %s", exc)
        return None


class PreviewOverride:
    """Make the hover preview show attaching, not replacing.

    The host builds its preview for its own semantics: template atom 0 is what
    the clicked atom turns into, so it covers that atom's label and rings the
    terminal with atom 0's *label* background — a tall ellipse around a
    one-character symbol like the ``*`` dummy.

    Neither is true here. Hiding the dummy ghost leaves the clicked atom's label
    alone and makes the host fall back to its fixed-radius circle for the
    connecting terminal, which is what the marker should be.
    """

    def __init__(self, scene: Any, mode_prefix: str) -> None:
        self.scene = scene
        self.mode_prefix = mode_prefix
        self.preview = getattr(scene, "template_preview", None)
        self._original: Any = None
        self.installed = False

    def install(self) -> bool:
        """Shadow the preview's geometry setter while the palette is open."""
        if self.installed or self.preview is None:
            return self.installed
        try:
            self._original = self.preview.set_user_template_geometry
            self.preview.set_user_template_geometry = self._set_geometry
            self.installed = True
        except (AttributeError, TypeError) as exc:
            logger.warning("Could not install preview tweak: %s", exc)
            self.installed = False
        return self.installed

    def remove(self) -> None:
        """Restore the host's own preview behaviour."""
        if not self.installed:
            return
        try:
            del self.preview.set_user_template_geometry
        except (AttributeError, TypeError):
            pass
        if (
            self._original is not None
            and getattr(self.preview, "set_user_template_geometry", None) is None
        ):
            self.preview.set_user_template_geometry = self._original
        self.installed = False

    def _owns_mode(self) -> bool:
        mode = getattr(self.scene, "mode", "") or ""
        return isinstance(mode, str) and mode.startswith(self.mode_prefix)

    def _set_geometry(self, points: Any, bonds_info: Any, atoms_data: Any) -> Any:
        result = None
        if self._original is not None:
            result = self._original(points, bonds_info, atoms_data)
        if not self._owns_mode():
            return result
        try:
            # Free placement really does draw the '*', so only adjust when the
            # group is landing on an existing atom.
            attaching = (getattr(self.scene, "template_context", {}) or {}).get(
                "attachment_atom"
            )
            if attaching is None:
                return result
            ghosts = getattr(self.preview, "ghost_atoms", None) or []
            if ghosts:
                ghosts[ATTACHMENT_INDEX].is_visible = False
            self.preview.replaced_label_path = QPainterPath()
            self.preview.update()
        except (AttributeError, IndexError, RuntimeError, TypeError) as exc:
            logger.warning("Could not adjust template preview: %s", exc)
        return result
