# SutonnyMJ Unicode

A Unicode (OpenType/GSUB) conversion of the legacy **SutonnyMJ** ANSI/Bijoy font, so the
same Bengali shapes can be typed and searched as real Unicode text (copy, spell-check,
search, web) while still looking exactly like SutonnyMJ on paper/screen.

**Latest release: v4.0 — 2026-11-11**

| File | Use |
|---|---|
| `SutonnyMJ-Unicode-v4.0.ttf` | Desktop install (Windows/macOS/Linux) |
| `SutonnyMJ-Unicode-v4.0.woff2` | Web (`@font-face`) |
| `SutonnyMJ Unicode.ttf` | Same font as v4.0 (canonical file name) |
| `SPECIMEN_ANSI_vs_v4.png` | ANSI vs v4.0 at the same point size |

## What was wrong (and what v4.0 fixes)

The earlier builds were a Unicode *transliteration* of an **older 1999 Fontographer
copy** of SutonnyMJ, not of the current ANSI release. They also shipped an **unhinted**
"final" (v3.9.3) and flattened the composed conjuncts. Result: at the same point size
the Unicode text was narrower, sat lower on the line, used different advances, and
looked "smaller" than ANSI.

v4.0 was rebuilt from the genuine ANSI release (`SutonnyMJ Regular.ttf`, 2005,
Copyright Mustafa Jabbar / Ananda Computers) and fixes:

1. **Exact glyph size** — all 228 source glyph outlines and advance widths are
   carried over 1:1. Per-glyph rendering is pixel-identical to ANSI at 12, 16, 24,
   48 and 96 px.
2. **Exact vertical metrics** — `hhea` (800/200) and `OS/2` typo/win
   (800/200, 863/315) are copied from ANSI, so baseline, ascent, descent and line
   height match instead of the old 863/-315 and 703/297.
3. **Hinting preserved** — `fpgm`, `prep`, `cvt ` and every original glyph program
   are kept (v3.9.3 had none).
4. **Composed conjuncts are real TrueType composites** — components keep their
   original hinting instead of being flattened, so conjuncts render like the ANSI
   text run.
5. **OS/2 v4** with the Bengali Unicode range bit (65) and Basic Latin set, so
   Word/Windows no longer skips the family.
6. **Removed the bogus U+0040 `@` mapping** to a Bengali glyph (a v3.9.3 bug).
   `@` and other Latin slots now correctly fall back to another font.
7. WOFF2 build included. Chrome's OTS sanitizer loads the TTF without errors.

Verification (against `SutonnyMJ Regular.ttf`, 2005):

```
glyph outlines + advances identical ....... 228 / 228
per-glyph renders pixel-identical ......... 508 / 510
  (the 2 excluded are legacy-only slots that must not be Unicode-mapped)
Chrome canvas text widths ................ 0.00 px difference
HarfBuzz shaping vs v3.9.3 ................ identical (one glyph was renamed mu1 -> mu)
regression vs the Bijoy converter oracle .. 5662 / 5740
```

## Install

* **Windows:** right-click the TTF → *Install for all users*.
* **macOS:** double-click the TTF → *Install Font*.
* **Linux:** `cp SutonnyMJ-Unicode-v4.0.ttf ~/.local/share/fonts/ && fc-cache -f`
* **Web:** see `SutonnyMJ-Unicode-v4.0.woff2`.

The family name is **SutonnyMJ Unicode**. Select it like any other font and type
normal Unicode Bengali.

## Known limitations

* **No Latin letters/digits.** The legacy font stores Bengali glyphs in the ASCII
  slots, so those slots are intentionally not Unicode-mapped. Use a Bengali+Latin
  font (e.g. Noto Sans Bengali, Kalpurush) as a fallback for English text.
* Original glyphs for **ৰ ৱ ঽ ৠ** do not exist in SutonnyMJ and therefore are not
  in this font.
* No `GPOS`/`GDEF`; shaping relies on `GSUB` (`ccmp nukt akhn rphf blwf pstf cjct calt`).
* A handful of rare conjuncts / converter quirks remain (see `build/`).
* Real-device testing in MS Word, Chrome, Android and Apple apps is still recommended.

## Licence / copyright

The original **SutonnyMJ** outlines and name are © Mustafa Jabbar / Ananda Computers.
This repository only contains a conversion/modification of those outlines. Redistribution
and modification rights for the original font have **not** been confirmed; treat this as
a personal-use/interoperability conversion and obtain permission from the rights holder
before redistributing the font commercially.

## Build

See [`build/README.md`](build/README.md).

## History

* **v4.0** (2026-11-11) — rebased on the 2005 ANSI release, exact metrics, hinting,
  composite conjuncts, OS/2 v4, WOFF2.
* v3.9.3 — OS/2 v4 patch on v3.9.2 (unhinted, wrong source).
* v3.8 — first "exact-ANSI" attempt (still using the 1999 copy).
* v3.0–v3.7 — shaping fixes (e-kar, ya-phala, reph, র্য, legacy-only slots).
