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


def test_initialize_registers_a_toolbar_button_only(qapp):
    """initialize() must NOT call add_plugin_menu; run() is the menu entry point."""
    context = FakeContext()
    plugin.initialize(context)

    assert len(context.toolbar_actions) == 1
    _, text, _, tooltip = context.toolbar_actions[0]
    assert text == "Groups"
    assert "Group Template" in tooltip
    assert len(context.menu_actions) == 0


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


def test_run_opens_the_palette(qapp):
    """run(mw) is the entry point the host calls from the Plugins menu."""
    context = FakeContext()
    plugin.initialize(context)

    plugin.run(context.get_main_window())

    window = context.get_window("palette")
    assert window is not None
    window.override.remove()
    window.deleteLater()


def test_run_before_initialize_is_a_no_op():
    """run() called before initialize() must not raise."""
    import group_template as fresh

    saved = fresh.PLUGIN_CONTEXT
    fresh.PLUGIN_CONTEXT = None
    try:
        fresh.run(object())  # should return silently
    finally:
        fresh.PLUGIN_CONTEXT = saved


@pytest.mark.parametrize("hook", ["initialize", "run", "show_palette"])
def test_public_hooks_exist(hook):
    assert callable(getattr(plugin, hook))
