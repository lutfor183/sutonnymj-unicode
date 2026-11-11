# -*- coding: utf-8 -*-
"""Data tables for the SutonnyMJ -> Unicode rebuild.

Legacy chars are written as the *Unicode characters that the ORIGINAL SutonnyMJ
cmap maps to the glyph* (i.e. cp1252 bytes decoded), exactly as the Bijoy
converters write them.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- Unicode -> legacy letter / mark ---------------------------------------
U2L = {
    # independent vowels (U+0986 AA is a composite, see U2L_SEQ)
    0x0985: 'A', 0x0987: 'B', 0x0988: 'C', 0x0989: 'D', 0x098A: 'E',
    0x098B: 'F', 0x098F: 'G', 0x0990: 'H', 0x0993: 'I', 0x0994: 'J',
    # consonants
    0x0995: 'K', 0x0996: 'L', 0x0997: 'M', 0x0998: 'N', 0x0999: 'O',
    0x099A: 'P', 0x099B: 'Q', 0x099C: 'R', 0x099D: 'S', 0x099E: 'T',
    0x099F: 'U', 0x09A0: 'V', 0x09A1: 'W', 0x09A2: 'X', 0x09A3: 'Y',
    0x09A4: 'Z', 0x09A5: '_', 0x09A6: '`', 0x09A7: 'a', 0x09A8: 'b',
    0x09AA: 'c', 0x09AB: 'd', 0x09AC: 'e', 0x09AD: 'f', 0x09AE: 'g',
    0x09AF: 'h', 0x09B0: 'i', 0x09B2: 'j', 0x09B6: 'k', 0x09B7: 'l',
    0x09B8: 'm', 0x09B9: 'n', 0x09DC: 'o', 0x09DD: 'p', 0x09DF: 'q',
    0x09CE: 'r', 0x0982: 's', 0x0983: 't', 0x0981: 'u',
    # dependent vowel signs (default variants)
    0x09BE: 'v', 0x09BF: 'w', 0x09C0: 'x', 0x09C1: 'y', 0x09C2: '~',
    0x09C3: '\u2026', 0x09C7: '\u2020', 0x09C8: '\u02c6', 0x09D7: '\u0160',
    # hasant (visible fallback form)
    0x09CD: '&',
    # digits
    0x09E6: '0', 0x09E7: '1', 0x09E8: '2', 0x09E9: '3', 0x09EA: '4',
    0x09EB: '5', 0x09EC: '6', 0x09ED: '7', 0x09EE: '8', 0x09EF: '9',
    # signs
    0x09F3: '$',          # taka
    0x0964: '|',          # danda
    0x0965: '\\',         # double danda
    # punctuation shared with ASCII
    0x0020: ' ', 0x0021: '!', 0x0022: '"', 0x0023: '#', 0x0025: '%',
    0x0027: "'", 0x0028: '(', 0x0029: ')', 0x002A: '*', 0x002B: '+',
    0x002C: ',', 0x002D: '-', 0x002E: '.', 0x002F: '/', 0x003A: ':',
    0x003B: ';', 0x003C: '<', 0x003D: '=', 0x003E: '>', 0x003F: '?',
    0x0040: '@', 0x005B: '[', 0x005D: ']', 0x007B: '{', 0x007D: '}',
    # typographic punctuation lives at Latin-1 slots in Bijoy fonts
    0x2018: '\u00d4', 0x2019: '\u00d5', 0x201C: '\u00d2', 0x201D: '\u00d3',
    0x2013: '\u00d1', 0x2014: '\u00d1', 0x2010: '-', 0x2011: '-',
}
# Unicode chars that need a two-glyph legacy sequence
U2L_SEQ = {
    0x0986: ['A', 'v'],       # AA = A + aa-kar in Bijoy
}

CONSONANTS = [0x0995 + i for i in range(0, 0x09B9 - 0x0995 + 1)
              if (0x0995 + i) != 0x09B1 and (0x0995 + i) != 0x09B3 and
              (0x0995 + i) != 0x09B4 and (0x0995 + i) != 0x09B5]
CONSONANTS = [c for c in CONSONANTS if c in U2L]
HALANT = 0x09CD
NUKTA = 0x09BC
ZWNJ, ZWJ = 0x200C, 0x200D

# ---- reference dictionary (Unicode cluster -> legacy string) ---------------
def load_oracle():
    d = json.load(open(os.path.join(HERE, 'oracle_data.json'), encoding='utf8'))
    return d

def conj_dict():
    """Cluster dictionary. Keys: tuple of Unicode code points, values: legacy str."""
    d = load_oracle()
    out = {}
    for k, v in d['uni2bijoy_string_conversion_map']:
        if len(k) < 2:
            continue
        if not all(0x0980 <= ord(c) <= 0x09FF or ord(c) in (ZWNJ, ZWJ) for c in k):
            continue                      # punctuation
        if k in ('\u09cd\u09b0\u09cd\u09af',):    # hasant-ra-hasant-ya
            continue
        out[tuple(ord(c) for c in k)] = v
    # additions / corrections taken from the other Bijoy converters
    extra = {
        'ম্প্র': '¤cÖ',
    }
    for k, v in extra.items():
        out[tuple(ord(c) for c in k)] = v
    # drop entries that are pure variant-handling in Bijoy keyboards but that
    # we implement generically (ra-phala/ya-phala/ba-phala/la-phala tokens)
    for k in list(out):
        if k == (0x09CD, 0x09B0) or k == (0x09CD, 0x09AF):
            del out[k]
    return out

# ---- variant classes (legacy chars) ----------------------------------------
# u-kar / uu-kar use the z / single-low-quote variants after these
Z_SET = set('KPQSUVWXZdf') | set('¶Áþ¾°¼Ü×ä©‹÷ù')
# ri-kar uses the "low" variant (U+201E) after these
R_SET = set('§¥cNgekLMmlR_`abjhY')
# ra-phala variants
RA_PREV_O = set('McKm'.replace('K', ''))          # M c k m -> Ö   (K is a conjunct base)
RA_PREV_O = set('Mckm')
RA_PREV_F = set('d')                                  # d -> «
# ba-phala variants
BA_CARET = set('Yš¤¯')                              # ^
BA_YDIA = set('aen')                                  # Ÿ
BA_BROKEN = set('jk')                                 # ¦
# la-phala
LA_ALT = set('Kdn')                                   # ¬
# ra-phala + u/uu: y-letters use plain y / ~
S_Y = set('NPQSUVWXYbdhjln')
