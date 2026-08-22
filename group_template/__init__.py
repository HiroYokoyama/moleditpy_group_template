"""
Group Template Plugin for MoleditPy.
A static palette of 310 substituent abbreviations (Me, Ph, Boc, Ts, TBS, ...),
searchable by name, alias or category and pickable from the keyboard.
Pick one and click in the 2D editor: the group is placed through MoleditPy's own
user-template mode, so you get the live hover preview and, when you click an
existing atom, the group is attached to it rather than replacing it.
Thumbnails are drawn with the editor's own atom and bond items, so a tile looks
like what will land on the canvas.

Source code, README, and full license (GNU GPL):
    https://github.com/HiroYokoyama/moleditpy_group_template
Copyright (c) HiroYokoyama. Licensed under the GNU General Public License;
see the LICENSE file in the repository above for the full terms.
"""

import logging

from PyQt6.QtWidgets import QWidget

from .palette_dialog import WINDOW_ID, GroupPaletteDialog

logger = logging.getLogger(__name__)

# --- Plugin Metadata ---
PLUGIN_NAME = "Group Template"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "HiroYokoyama"
PLUGIN_DESCRIPTION = (
    "Searchable palette of 310 substituent group abbreviations (Me, Ph, Boc, Ts, "
    "TBS, ...) placed with the 2D editor's user-template mode."
)
PLUGIN_CATEGORY = "Editing"
PLUGIN_TAGS = ["2D Editor", "Templates", "Structure Drawing"]
PLUGIN_DEPENDENCIES = ["PyQt6", "rdkit"]
PLUGIN_SUPPORTED_MOLEDITPY_VERSION = ">=3.0.0, <5.0.0"
PLUGIN_SUPPORTED_PYTHON_VERSION = ">=3.9, <3.15"
PLUGIN_SUPPORTED_OS = ["Windows", "macOS", "Linux", "WSL"]


def initialize(context):
    """Register the palette on the Plugin Toolbar and in the Plugins menu."""
    context.add_toolbar_action(
        lambda: show_palette(context),
        "Groups",
        tooltip="Group Template — insert a substituent abbreviation",
    )
    context.add_plugin_menu("Group Template...", lambda: show_palette(context))


def show_palette(context):
    """Singleton: reuse the existing palette if it is already open."""
    window = context.get_window(WINDOW_ID)
    if window:
        window.show()
        window.raise_()
        window.activateWindow()
        return window

    main_window = context.get_main_window()
    parent = main_window if isinstance(main_window, QWidget) else None
    dialog = GroupPaletteDialog(context, parent)
    context.register_window(WINDOW_ID, dialog)
    dialog.show()
    return dialog
