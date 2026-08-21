"""Plugin metadata and registration."""

import re

import pytest

import group_template as plugin

from .fakes import FakeContext


def test_metadata():
    assert plugin.PLUGIN_NAME == "Group Template"
    assert re.fullmatch(r"\d+\.\d+\.\d+", plugin.PLUGIN_VERSION)
    assert plugin.PLUGIN_AUTHOR
    assert plugin.PLUGIN_DESCRIPTION
    assert plugin.PLUGIN_CATEGORY
    assert isinstance(plugin.PLUGIN_TAGS, list) and plugin.PLUGIN_TAGS


def test_declared_dependencies_match_the_imports():
    assert set(plugin.PLUGIN_DEPENDENCIES) == {"PyQt6", "rdkit"}


def test_supported_os_and_python():
    assert set(plugin.PLUGIN_SUPPORTED_OS) == {"Windows", "macOS", "Linux", "WSL"}
    assert plugin.PLUGIN_SUPPORTED_PYTHON_VERSION.startswith(">=3.9")
    assert plugin.PLUGIN_SUPPORTED_MOLEDITPY_VERSION.startswith(">=3.0.0")


def test_initialize_registers_a_toolbar_button_and_a_menu_entry(qapp):
    context = FakeContext()
    plugin.initialize(context)

    assert len(context.toolbar_actions) == 1
    _, text, _, tooltip = context.toolbar_actions[0]
    assert text == "Groups"
    assert "Group Template" in tooltip
    assert len(context.menu_actions) == 1


def test_toolbar_callback_opens_the_palette(qapp):
    context = FakeContext()
    plugin.initialize(context)
    callback = context.toolbar_actions[0][0]

    callback()

    window = context.get_window("palette")
    assert window is not None
    window.override.remove()
    window.deleteLater()


def test_show_palette_is_a_singleton(qapp):
    context = FakeContext()
    first = plugin.show_palette(context)
    second = plugin.show_palette(context)

    assert first is second
    first.override.remove()
    first.deleteLater()


def test_menu_callback_opens_the_same_window(qapp):
    context = FakeContext()
    plugin.initialize(context)
    opened = context.menu_actions[0][1]()
    assert context.get_window("palette") is opened
    opened.override.remove()
    opened.deleteLater()


@pytest.mark.parametrize("hook", ["initialize", "show_palette"])
def test_public_hooks_exist(hook):
    assert callable(getattr(plugin, hook))
