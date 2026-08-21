# Group Template

[![Tests](https://github.com/HiroYokoyama/moleditpy_group_template/actions/workflows/tests.yml/badge.svg)](https://github.com/HiroYokoyama/moleditpy_group_template/actions/workflows/tests.yml)
![coverage](https://img.shields.io/badge/coverage-%3E90%25-brightgreen)
![license](https://img.shields.io/badge/license-GPL--3.0-blue)

A searchable palette of **313 substituent group abbreviations** for
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
atom is *replaced* by the template's first atom.

## Install

Download `group_template_<version>.zip` from the
[latest release](https://github.com/HiroYokoyama/moleditpy_group_template/releases)
and unzip it into your user plugin directory, or install it from the **Plugin
Installer** plugin. Restart MoleditPy, or use **Plugins → Reload All Plugins**.

## Use

Click **Groups** on the Plugin Toolbar (or **Plugins → Group Template...**).

- **Search** by name or alias — `tosyl` finds `Ts`, `trityl` finds `Trt`.
- **Filter** by category with the dropdown.
- Click a tile, then click on the canvas. The palette stays open, so you can
  place several groups in a row.
- Closing the palette (or pressing Esc) returns the editor to normal drawing.

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

The library is **static and read-only** — this plugin never writes to disk. To
keep your own groups, draw one and use MoleditPy's **User Templates → Save
Current 2D as Template**.

## Development

```bash
pip install pytest pytest-cov PyQt6 rdkit
QT_QPA_PLATFORM=offscreen python -m pytest tests/ -v
```

`tests/test_api.py` additionally validates every host API access against the
main app when the two repos are checked out as siblings.

## License

GPL-3.0. See [LICENSE](LICENSE).
