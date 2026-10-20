"""Headless Qt + quiet RDKit for the whole suite."""

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from rdkit import RDLogger

    RDLogger.DisableLog("rdApp.*")
except ImportError:  # pragma: no cover - rdkit missing is reported by the tests
    pass


@pytest.fixture(scope="session")
def qapp():
    """One QApplication for the session; widgets need it to exist."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def close_palette_dialogs():
    """Destroy each test's palettes before their Qt callbacks outlive the test."""
    yield
    from PySide6.QtCore import QCoreApplication, QEvent
    from PySide6.QtWidgets import QApplication
    from group_template.palette_dialog import GroupPaletteDialog

    app = QApplication.instance()
    if app is not None:
        for widget in app.topLevelWidgets():
            if isinstance(widget, GroupPaletteDialog):
                widget.close()
                widget.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
