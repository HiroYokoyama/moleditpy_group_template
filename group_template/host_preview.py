"""Draw palette thumbnails with the editor's own atom and bond items.

The host's User Templates dialog renders its thumbnails through
``moleditpy.ui.preview_molecule`` (``PreviewScene`` + ``build_preview_items``),
so they inherit the editor's element colours, fonts, bond spacing and the
user's own 2D settings. Doing the same here means a group tile looks like what
the group will look like once it is drawn.

That module is host internals, not PluginContext, so every use of it is guarded:
when it cannot be imported -- an older host, or the headless test suite -- the
caller falls back to ``preview.render_pixmap``, which needs nothing but Qt.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPainter, QPixmap

logger = logging.getLogger(__name__)

# Keep a little air around the structure, as the host's own dialog does.
_MIN_PADDING = 6.0
_RELATIVE_PADDING = 0.05


# Looked up once: a failing import rescans sys.path every single time, and a
# palette full of thumbnails would pay for it on every tile.
_HELPERS: Optional[Tuple[Any, Any, Any]] = None
_LOOKED_UP = False


def _helpers() -> Optional[Tuple[Any, Any, Any]]:
    """(PreviewScene, build_preview_items, preview_content_rect), or None."""
    global _HELPERS, _LOOKED_UP  # pylint: disable=global-statement
    if _LOOKED_UP:
        return _HELPERS
    _LOOKED_UP = True
    _HELPERS = _import_helpers()
    return _HELPERS


def _import_helpers() -> Optional[Tuple[Any, Any, Any]]:
    """Import the host's preview helpers, or None when they are not there."""
    try:
        from moleditpy.ui.preview_molecule import (  # pylint: disable=import-outside-toplevel
            PreviewScene,
            build_preview_items,
            preview_content_rect,
        )
    except ImportError:
        return None
    return PreviewScene, build_preview_items, preview_content_rect


def available() -> bool:
    """True when the host exposes the preview helpers this module needs."""
    return _helpers() is not None


def _preview_inputs(template: Dict[str, Any]) -> Tuple[List[Any], List[Any]]:
    """Convert a PME template into the (atoms, bonds) build_preview_items wants."""
    from PyQt6.QtCore import QPointF  # local: only needed on the host path

    atoms = template.get("atoms", [])
    index_of_id = {atom.get("id", i): i for i, atom in enumerate(atoms)}
    preview_atoms = [
        {
            "symbol": atom.get("symbol", "C"),
            "charge": atom.get("charge", 0),
            "radical": atom.get("radical", 0),
            "pos": QPointF(atom["x"], atom["y"]),
        }
        for atom in atoms
    ]

    preview_bonds = []
    for bond in template.get("bonds", []):
        first = index_of_id.get(bond.get("atom1"))
        second = index_of_id.get(bond.get("atom2"))
        if first is None or second is None:
            continue
        preview_bonds.append(
            (first, second, bond.get("order", 1), bond.get("stereo", 0))
        )
    return preview_atoms, preview_bonds


def render_pixmap(
    template: Dict[str, Any],
    width: int,
    height: int,
    editor_scene: Any = None,
    ratio: float = 1.0,
) -> Optional[QPixmap]:
    """Thumbnail drawn with the editor's items, or None if the host cannot."""
    helpers = _helpers()
    if helpers is None or not template.get("atoms"):
        return None
    preview_scene_cls, build_preview_items, preview_content_rect = helpers

    try:
        atoms, bonds = _preview_inputs(template)
        scene = preview_scene_cls(editor_scene)
        atom_items, bond_items, _ = build_preview_items(atoms, bonds)
        for item in bond_items:
            scene.addItem(item)
        for item in atom_items:
            scene.addItem(item)

        # The item bounding rects carry hit padding; fit what is drawn instead.
        content = preview_content_rect(atom_items, bond_items)
        if content.isEmpty():
            return None
        pad = max(
            _MIN_PADDING, max(content.width(), content.height()) * _RELATIVE_PADDING
        )
        content = content.adjusted(-pad, -pad, pad, pad)

        pixmap = QPixmap(round(width * ratio), round(height * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        try:
            scene.render(
                painter,
                QRectF(0, 0, width, height),
                content,
                Qt.AspectRatioMode.KeepAspectRatio,
            )
        finally:
            painter.end()
        # Items belong to the scene; dropping it here would outlive the pixmap.
        scene.clear()
        return pixmap
    except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
        logger.warning("Host thumbnail rendering failed, falling back: %s", exc)
        return None
