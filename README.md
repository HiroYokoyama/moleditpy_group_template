# Group Template

[![Tests](https://github.com/HiroYokoyama/moleditpy_group_template/actions/workflows/tests.yml/badge.svg)](https://github.com/HiroYokoyama/moleditpy_group_template/actions/workflows/tests.yml)
![coverage](https://img.shields.io/badge/coverage-%3E90%25-brightgreen)
![license](https://img.shields.io/badge/license-GPL--3.0-blue)

A searchable palette of **310 substituent group abbreviations** for
[MoleditPy](https://github.com/HiroYokoyama/python_molecular_editor) — Me, Ph,
Boc, Ts, TBS, Bpin, amino-acid side chains, nucleobases and more.

Pick a group, then click in the 2D editor. You get MoleditPy's own live hover
preview, and the group is drawn at the editor's standard bond length.

## The `*` is the attachment point

Every thumbnail shows a `*` where the group bonds on:

- **Click an existing atom** → the group is bonded to that atom, which **keeps
  its own element**. Clicking a nitrogen and picking `Ph` gives you N–Ph, not a
  carbon where your nitrogen was.
- **Click empty space** → the group is dropped with its `*` dummy, so the open
  valence stays visible.

This differs from MoleditPy's built-in **User Templates**, where the clicked
atom is *replaced* by the template's first atom. The hover preview shows the
attaching behaviour too: your atom keeps its label, and the connecting terminal
is marked with a circle.

Your own user templates are untouched — they still replace, exactly as before.

## Install

Download `group_template_<version>.zip` from the
[latest release](https://github.com/HiroYokoyama/moleditpy_group_template/releases)
and unzip it into your user plugin directory, or install it from the **Plugin
Installer** plugin. Restart MoleditPy, or use **Plugins → Reload All Plugins**.

## Use

Click **Groups** on the Plugin Toolbar (or **Plugins → Group Template...**).

- **Search** by name, alias or category — `tosyl` finds `Ts`, `silyl` finds the
  whole silyl family. Hyphens, spaces and subscripts are ignored, so
  `tert butyl`, `tert-butyl` and `tertbutyl` all find `tBu`, and `cf3` finds
  `CF₃`. Several words narrow together. The entry the query names outright
  comes first: `me` puts `Me` at the top, not `Methallyl`.
- **Filter** by category with the dropdown, including **Recently used** — the
  last 12 groups you placed, newest first. Tick **Save history** at the bottom
  of the palette to keep that list between sessions; it is **off by default**,
  and unticking it forgets what was stored.
- Click a tile, then click on the canvas. The palette stays open, so you can
  place several groups in a row. The armed group stays highlighted and named at
  the bottom of the palette even while you keep searching.
- **Keyboard**: type, press **Enter** to arm the best match, or **↓** into the
  grid and walk it with the arrow keys, **Enter**/**Space** to arm. **Esc**
  clears the search box first and only closes the palette once it is empty.
- Closing the palette returns the editor to normal drawing.

Tiles are drawn with the editor's own atoms and bonds, so a thumbnail looks
like what you are about to place — same element colours, fonts and 2D settings.

Undo is the editor's own: one Ctrl+Z removes the whole group.

## The library

| Category | Examples |
|---|---|
| Alkyl / Cycloalkyl | Me, Et, iPr, tBu, cHex, 1-Ad, BCP |
| Halogenated | CF₃, CCl₃, C₂F₅, CH₂CF₃ |
| Alkenyl / Alkynyl | vinyl, allyl, prenyl, propargyl, TMS-ethynyl |
| Aryl / Heteroaryl | Ph, Bn, Mes, Dipp, C₆F₅, 2-Py, 3-indolyl, carbazolyl |
| Saturated heterocycle | morpholino, piperidyl, THP, dithianyl, phthalimido |
| Acyl / Ester / Amide | Ac, Bz, Piv, CO₂Me, Weinreb, COCl |
| Protecting groups | Boc, Cbz, Fmoc, Alloc, Troc, MOM, SEM, PMB, Trt, DMTr |
| Silyl | TMS, TES, TBS, TIPS, TBDPS |
| Sulfonyl / S | Ms, Ts, Tf, Ns, SMe, SPh, SCF₃ |
| Phosphorus | PPh₂, PCy₂, PO(OEt)₂, phosphonium |
| B / Sn / Metal | B(OH)₂, Bpin, SnBu₃, MgBr, Li |
| Functional group | OH, OMe, OTf, NH₂, NHBoc, N₃, NO₂, CN, F/Cl/Br/I |
| Amino acid side chain | Ala…Trp (18 side chains) |
| Nucleobase | adenin-9-yl, thymin-1-yl, … |

The library is **static** — the plugin adds nothing to it and touches none of
your files. With **Save history** off, as it ships, it stores nothing at all;
tick it and the only thing written is the list of labels you placed most
recently, in Qt's own settings. To keep your own groups, draw one and use
MoleditPy's **User Templates → Save Current 2D as Template**.

## Development

```bash
pip install pytest pytest-cov PyQt6 rdkit
QT_QPA_PLATFORM=offscreen python -m pytest tests/ -v
```

`tests/test_api.py` additionally validates every host API access against the
main app when the two repos are checked out as siblings.

## License

GPL-3.0. See [LICENSE](LICENSE).
