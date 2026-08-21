"""Test doubles shaped like the parts of MoleditPy this plugin touches."""

from typing import Any, Dict, List, Optional


class FakeAtomItem:
    """Stands in for the host's AtomItem."""

    def __init__(self, atom_id: int, symbol: str = "C") -> None:
        self.atom_id = atom_id
        self.symbol = symbol
        self.charge = 0
        self.radical = 0
        self.styled = 0

    def update_style(self) -> None:
        self.styled += 1


class FakeData:
    def __init__(self) -> None:
        self.atoms: Dict[int, Dict[str, Any]] = {}
        self.bonds: Dict[Any, Dict[str, Any]] = {}


class FakeScene:
    """Minimal MoleculeScene: enough for placement and mode handling."""

    def __init__(self) -> None:
        self.data = FakeData()
        self.atom_items: Dict[int, FakeAtomItem] = {}
        self.mode = "atom_C"
        self.current_atom_symbol = "C"
        self.user_template_data: Optional[Dict[str, Any]] = None
        self.template_context: Dict[str, Any] = {}
        self.template_preview = FakePreview()
        self.created: List[str] = []
        self.bonded: List[Any] = []
        self.cleared = 0
        self.updated = 0
        self._next_id = 100

    def add_existing_atom(self, symbol: str = "C") -> FakeAtomItem:
        """Seed an atom that is already drawn on the canvas."""
        self._next_id += 1
        item = FakeAtomItem(self._next_id, symbol)
        self.atom_items[item.atom_id] = item
        self.data.atoms[item.atom_id] = {"symbol": symbol, "charge": 0, "radical": 0}
        return item

    def create_atom(
        self, symbol: str, pos: Any, charge: int = 0, radical: int = 0
    ) -> int:
        self._next_id += 1
        item = FakeAtomItem(self._next_id, symbol)
        item.charge, item.radical = charge, radical
        self.atom_items[item.atom_id] = item
        self.data.atoms[item.atom_id] = {
            "symbol": symbol,
            "charge": charge,
            "radical": radical,
            "pos": pos,
        }
        self.created.append(symbol)
        return item.atom_id

    def create_bond(
        self, atom1: Any, atom2: Any, bond_order: int = 1, bond_stereo: int = 0
    ) -> None:
        self.data.bonds[(atom1.atom_id, atom2.atom_id)] = {
            "order": bond_order,
            "stereo": bond_stereo,
        }
        self.bonded.append((atom1.atom_id, atom2.atom_id, bond_order))

    def add_user_template_fragment(self, template_context: Dict[str, Any]) -> str:
        """The host's own commit step, which this plugin shadows."""
        return "host"

    def clear_template_preview(self) -> None:
        self.cleared += 1

    def update(self) -> None:
        self.updated += 1


class FakePreview:
    def __init__(self) -> None:
        self.hidden = 0

    def hide(self) -> None:
        self.hidden += 1


class FakeUiManager:
    def __init__(self) -> None:
        self.modes: List[str] = []

    def set_mode_and_update_toolbar(self, mode: str) -> None:
        self.modes.append(mode)


class FakeInitManager:
    def __init__(self, scene: FakeScene) -> None:
        self.scene = scene


class FakeMainWindow:
    def __init__(self) -> None:
        self.scene = FakeScene()
        self.init_manager = FakeInitManager(self.scene)
        self.ui_manager = FakeUiManager()
        self.template_data: Optional[Dict[str, Any]] = None

    def set_scene_user_template_data(self, data: Dict[str, Any]) -> None:
        self.template_data = data
        self.scene.user_template_data = data


class FakeContext:
    """Stands in for PluginContext."""

    def __init__(self, main_window: Optional[FakeMainWindow] = None) -> None:
        self.main_window = main_window if main_window is not None else FakeMainWindow()
        self.windows: Dict[str, Any] = {}
        self.toolbar_actions: List[Any] = []
        self.menu_actions: List[Any] = []
        self.messages: List[str] = []

    def get_main_window(self) -> Optional[FakeMainWindow]:
        return self.main_window

    def add_toolbar_action(self, callback, text, icon=None, tooltip=None) -> None:
        self.toolbar_actions.append((callback, text, icon, tooltip))

    def add_plugin_menu(self, path, callback, **kwargs) -> None:
        self.menu_actions.append((path, callback))

    def register_window(self, window_id: str, window: Any) -> None:
        self.windows[window_id] = window

    def get_window(self, window_id: str) -> Any:
        return self.windows.get(window_id)

    def show_status_message(self, message: str, timeout: int = 3000) -> None:
        self.messages.append(message)
