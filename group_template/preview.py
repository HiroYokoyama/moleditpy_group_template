"""Small structure thumbnails for the palette tiles.

The fitting maths is kept free of Qt so it can be unit tested directly; only
``render_pixmap`` touches QtGui.
"""

import math
from typing import Any, Dict, List, Tuple

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QPixmap

# Carbons are drawn as bare vertices, like the 2D editor does.
_HIDDEN_SYMBOL = "C"
_DOUBLE_GAP = 2.2
_TRIPLE_GAP = 3.4
_LABEL_CLEARANCE = 5.0

# The '*' dummy written first marks where the group bonds on (see library.py).
ATTACHMENT_ID = 0


def atom_label(atom: Dict[str, Any]) -> str:
    """Text to draw for an atom, or "" for a plain carbon vertex."""
    charge = int(atom.get("charge") or 0)
    radical = int(atom.get("radical") or 0)
    symbol = atom["symbol"]
    if symbol == _HIDDEN_SYMBOL and not charge and not radical:
        return ""

    text = symbol
    if charge:
        sign = "+" if charge > 0 else "−"
        text += sign if abs(charge) == 1 else f"{abs(charge)}{sign}"
    if radical:
        text += "•"
    return text


def fit_transform(
    atoms: List[Dict[str, Any]], width: float, height: float, pad: float = 12.0
) -> Tuple[float, float, float]:
    """Return (scale, dx, dy) mapping template coords into a width x height box."""
    if not atoms:
        return 1.0, width / 2.0, height / 2.0

    xs = [a["x"] for a in atoms]
    ys = [a["y"] for a in atoms]
    span_x = max(xs) - min(xs)
    span_y = max(ys) - min(ys)

    usable_w = max(width - 2 * pad, 1.0)
    usable_h = max(height - 2 * pad, 1.0)
    scale_x = usable_w / span_x if span_x > 1e-9 else float("inf")
    scale_y = usable_h / span_y if span_y > 1e-9 else float("inf")
    scale = min(scale_x, scale_y)
    if math.isinf(scale):
        scale = 1.0
    # Never blow a one-bond group up to fill the whole tile.
    scale = min(scale, 1.0)

    mid_x = (max(xs) + min(xs)) / 2.0
    mid_y = (max(ys) + min(ys)) / 2.0
    return scale, width / 2.0 - mid_x * scale, height / 2.0 - mid_y * scale


def transform_point(
    atom: Dict[str, Any], scale: float, dx: float, dy: float
) -> Tuple[float, float]:
    """Apply a fit_transform result to one template atom."""
    return atom["x"] * scale + dx, atom["y"] * scale + dy


def _offset_pairs(
    p1: QPointF, p2: QPointF, gap: float, count: int
) -> List[Tuple[QPointF, QPointF]]:
    """Parallel line pairs for multiple bonds, offset perpendicular to the bond."""
    dx, dy = p2.x() - p1.x(), p2.y() - p1.y()
    length = math.hypot(dx, dy)
    if length < 1e-9:
        return [(p1, p2)]
    nx, ny = -dy / length * gap, dx / length * gap

    if count == 2:
        shifts = (-0.5, 0.5)
    elif count == 3:
        shifts = (-1.0, 0.0, 1.0)
    else:
        shifts = (0.0,)

    return [
        (
            QPointF(p1.x() + nx * s, p1.y() + ny * s),
            QPointF(p2.x() + nx * s, p2.y() + ny * s),
        )
        for s in shifts
    ]


def render_pixmap(
    template: Dict[str, Any],
    width: int,
    height: int,
    color: QColor,
    ratio: float = 1.0,
) -> QPixmap:
    """Draw a template thumbnail. ``ratio`` is the device pixel ratio (Retina)."""
    pixmap = QPixmap(round(width * ratio), round(height * ratio))
    pixmap.setDevicePixelRatio(ratio)
    pixmap.fill(Qt.GlobalColor.transparent)

    atoms = template.get("atoms", [])
    if not atoms:
        return pixmap

    scale, dx, dy = fit_transform(atoms, width, height)
    points = {a["id"]: QPointF(*transform_point(a, scale, dx, dy)) for a in atoms}
    # Whatever atom_label() actually draws is what a bond has to stop short of:
    # a charged carbon is written "C+" even though its symbol is the hidden one.
    labelled = {a["id"] for a in atoms if atom_label(a)}

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(color, 1.3))

    for bond in template.get("bonds", []):
        p1, p2 = points.get(bond["atom1"]), points.get(bond["atom2"])
        if p1 is None or p2 is None:
            continue
        # Stop short of drawn element labels so the line does not run through them.
        p1, p2 = _trim(p1, p2, bond["atom1"] in labelled, bond["atom2"] in labelled)
        order = bond.get("order", 1)
        gap = _TRIPLE_GAP if order == 3 else _DOUBLE_GAP
        for a, b in _offset_pairs(p1, p2, gap, order):
            painter.drawLine(a, b)

    font = QFont()
    font.setPointSizeF(7.5)
    painter.setFont(font)
    for atom in atoms:
        text = atom_label(atom)
        if not text:
            continue
        point = points[atom["id"]]
        box = QRectF(point.x() - 11, point.y() - 7, 22, 14)
        painter.drawText(box, Qt.AlignmentFlag.AlignCenter, text)

    painter.end()
    return pixmap


def _trim(
    p1: QPointF, p2: QPointF, trim_start: bool, trim_end: bool
) -> Tuple[QPointF, QPointF]:
    """Shorten a bond line at whichever ends carry an element label."""
    dx, dy = p2.x() - p1.x(), p2.y() - p1.y()
    length = math.hypot(dx, dy)
    if length < 2 * _LABEL_CLEARANCE:
        return p1, p2
    ux, uy = dx / length, dy / length
    if trim_start:
        p1 = QPointF(p1.x() + ux * _LABEL_CLEARANCE, p1.y() + uy * _LABEL_CLEARANCE)
    if trim_end:
        p2 = QPointF(p2.x() - ux * _LABEL_CLEARANCE, p2.y() - uy * _LABEL_CLEARANCE)
    return p1, p2
