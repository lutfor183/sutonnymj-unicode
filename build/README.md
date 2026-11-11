# Build

This folder contains the generator for `SutonnyMJ-Unicode-v4.0.ttf`.

Requirements:

* Python 3 + [fontTools](https://github.com/fonttools/fonttools)
* Node.js (only for regenerating the legacy-converter oracle data; not needed for a
  normal rebuild)
* The **genuine ANSI font** `SutonnyMJ Regular.ttf` (2005, Mustafa Jabbar / Ananda
  Computers). It is *not* included here for copyright reasons.

## Rebuild

```bash
cd build
cp /path/to/SutonnyMJ\ Regular.ttf SutonnyMJ.ttf
python3 build_v40.py SutonnyMJ-Unicode-v4.0.ttf
```

`build_v40.py`:

1. reads the ANSI source,
2. maps every Unicode code point to the matching legacy glyph,
3. generates the GSUB features (`features_v3.fea` is written for reference),
4. builds the composed conjuncts as TrueType composite glyphs,
5. keeps hinting (`fpgm`/`prep`/`cvt ` and each original glyph program),
6. copies `hhea`/`OS/2` metrics from the source and upgrades `OS/2` to v4 with the
   Bengali Unicode range bit.

## Data files

* `sdata.py` — Unicode ↔ legacy table, consonant list, variant classes.
* `oracle_data.json` — cluster dictionary (Unicode cluster → legacy string).
* `pairs_oracle.json` — per-pair legacy sequences used to build the `akhn` rules.

Regenerating the oracle data needs the converter package used by the original
project (`node orc.js`); the current files are checked in so a rebuild is offline.
