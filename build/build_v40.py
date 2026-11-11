# -*- coding: utf-8 -*-
import sys, json
import sdata
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

OUT=sys.argv[1] if len(sys.argv)>1 else 'v3.ttf'
f=TTFont('SutonnyMJ.ttf'); ocm=f.getBestCmap(); order=f.getGlyphOrder(); hm=f['hmtx']
ORIG_HINTED={n for n in order if getattr(f['glyf'][n],'program',None) and len(f['glyf'][n].program.getBytecode())>0}
ORIG_HEAD_FLAGS=f['head'].flags
def L(ch): return ocm[ord(ch)]
gs=f.getGlyphSet()
HALc='&'; HAL=L('&')

# ---------- cmap ----------
cmap={}
for u,l in sdata.U2L.items():
    if ord(l) in ocm: cmap[u]=ocm[ord(l)]
for u in (0x0040,0x007B,0x007D,0x0026,0x0024): cmap.pop(u,None)   # not ASCII-mapped (font has no Latin)
cmap[0x09C7]=L('\u2020'); cmap[0x09C8]=L('\u02c6'); cmap[0x09C3]=L('\u2026')
cmap[0x09C2]=L('~'); cmap[0x09C1]=L('y')
cmap.pop(0x09CB,None); cmap.pop(0x09CC,None)
cmap[0x007B]=ocm[0x7b]; cmap[0x007D]=ocm[0x7d]   # real braces
for _cp,_pu in ((0x40,0xF040),(0xb9,0xF0B9),(0xff,0xF0FF),(0x201c,0xF01C),(0x2014,0xF014),(0x2212,0xF212)): cmap[_pu]=ocm[_cp]   # legacy-only slots reachable via PUA
cmap[0x00A0]=ocm[0xA0]   # NBSP -> blank legacy glyph
cmap[0x2013]=L('\u00d0'); cmap[0x2014]=L('\u00d1')

newglyphs={}   # name -> list of glyph names (composite) or None(empty)
lastchar={}    # glyph -> last legacy char (for variant classes)
for c,g in ((ch,ocm[ch]) for ch in ocm): lastchar.setdefault(g,set()).add(chr(c))
def comp_name(S): return 'cj_'+'_'.join('%x'%ord(c) for c in S)
def need(S):
    if len(S)==1: return L(S)
    n=comp_name(S)
    if n not in newglyphs:
        newglyphs[n]=[L(c) for c in S]; lastchar[n]={S[-1]}
    return n

# Explicit composite mappings for Bengali O-kar and AU-kar. Some renderers
# do not canonically decompose U+09CB/U+09CC before cmap lookup, which caused
# visible fallback boxes in real applications. Preserve the source outlines.
cmap[0x09CB] = need('\u2020v')   # e-kar + aa-kar legacy sequence
cmap[0x09CC] = need('\u02c6v')   # ai-kar + aa-kar legacy sequence

def uglyph(cp):
    if cp==0x09CD: return HAL
    return cmap[cp]

# ---------- rules from oracle ----------
PH={'র':'ªÖ«','ব':'¡^Ÿ¦','ল':'ø¬\xad','ন':'œ','ম':'¥','ণ':'è','য':'¨'}
U2=lambda c: ord(c)
pairs=json.load(open('pairs_oracle.json'))
consL={chr(c):sdata.U2L[c] for c in sdata.CONSONANTS}
rules={}   # tuple(cp) -> S
def generic_pair(a,b,S):
    la=consL[a]
    return S==la+'&'+consL[b] or (b in PH and len(S)==2 and S[0]==la and S[1] in PH[b])
for k,S in pairs.items():
    a,b=k[0],k[2]
    if generic_pair(a,b,S): continue
    if a=='র' and S==consL[b]+'©': continue      # reph clusters are done by rphf, not by ligature
    rules[(ord(a),0x09CD,ord(b))]=S
cd=sdata.conj_dict()
for key,S in cd.items():
    if 0x200C in key or 0x200D in key: continue
    if key[0]==ord('র') and len(key)>1 and key[1]==0x09CD and S.endswith('©'): continue
    if key==tuple(map(ord,'ক্ষ্ন')): continue
    if len(key)==3 and chr(key[0]) in consL and chr(key[2]) in consL and generic_pair(chr(key[0]),chr(key[2]),S): continue
    rules[key]=S
# corrections where a converter package is wrong (verified visually against glyph sheets)
rules[tuple(map(ord,'ণ্ড'))]='\u00ca'      # Ê
rules[tuple(map(ord,'গ্দ'))]='\u00ba'      # º
rules.pop(tuple(map(ord,'ক্ষ্ন')),None)
rules[tuple(map(ord,'গ্রু'))]='M\u00d6\u00e6'   # MÖæ (dictionary had ª)
akhn=[]; akhn_m=[]
MATRAS=set(range(0x09BE,0x09D8))-{0x09CD}
for key,S in rules.items():
    if '\xad' in S: pass
    rhs=need(S); lhs=[uglyph(c) for c in key]
    if rhs==L(S[0]) and len(lhs)==1: continue
    (akhn_m if (len(key)==2 and key[1] in MATRAS) else akhn).append((lhs,rhs))

# swaps / composites for post-reorder quirks
def seqname(chars): return need(chars)
karset=['y','z','~','\u201a']
swap_ya=[]     # [kar, ya] -> composite kar+ya
for k in karset+['u']:
    swap_ya.append((L(k),seqname(k+'¨')))
uv=need('uv')   # chandrabindu before aa-kar
# ---------- variant classes ----------
def SET(chars):
    names=[g for g,cs in lastchar.items() if cs & set(chars)]
    return sorted(set(names))
Z=SET(sdata.Z_SET); R=SET(sdata.R_SET)
RA_ALL=[L('ª'),L('Ö'),L('«')]
RA_AFTER=sorted(set(RA_ALL+[L('Î'),L('å')]+SET('ªÖ«')))
SY=SET(sdata.S_Y); RAO=SET(sdata.RA_PREV_O); RAF=SET(sdata.RA_PREV_F)
BAC=SET(sdata.BA_CARET); BAY=SET(sdata.BA_YDIA); BAB=SET(sdata.BA_BROKEN); LAA=SET(sdata.LA_ALT)
openers=[ocm[c] for c in (ord('('),ord('['),ord('{'),ord("'"),ord('"'),ord('-'),0xD4,0xD2) if c in ocm]
startctx=openers+[ocm[c] for c in (0x20,0xA0) if c in ocm]
alln=[g for g in order if g not in startctx and g not in ('.notdef',)]+list(newglyphs)
# ---------- FEA ----------
S=' '.join
fea=['languagesystem DFLT dflt;','languagesystem bng2 dflt;','languagesystem beng dflt;','languagesystem beng dflt;'][:3]
fea.append('feature ccmp { sub abeng_aa by %s %s; } ccmp;'%(L('A'),L('v')))
fea.append('feature nukt {'); 
for u,l in (('ড','o'),('ঢ','p'),('য','q')): fea.append(' sub %s nukta by %s;'%(cmap[ord(u)],L(l)))
fea.append('} nukt;')
fea.append('feature akhn {')
fea.append(' lookup AK0 {')
for lhs,rhs in akhn: fea.append('  sub %s by %s;'%(S(lhs),rhs))
fea.append('  sub %s zwj %s by %s;'%(HAL,cmap[ord('য')],L('¨')))      # C + halant + ZWJ + ya  (Android keyboards): ya-phala
fea.append('  sub %s zwj %s by %s;'%(HAL,cmap[ord('র')],L('ª')))      # ... ra-phala (variant picked later by calt)
fea.append(' } AK0;')
fea.append('} akhn;')

fea.append('feature rphf { sub %s %s by %s; } rphf;'%(cmap[ord('র')],HAL,L('©')))
fea.append('feature blwf {')
for c,m in (('র','ª'),('ব','¡'),('ল','ø'),('ন','œ'),('ম','¥'),('ণ','è')):
    fea.append(' sub %s %s by %s;'%(HAL,cmap[ord(c)],L(m)))
fea.append('} blwf;')
fea.append('feature pstf { sub %s %s by %s; } pstf;'%(HAL,cmap[ord('য')],L('¨')))
fea.append('feature cjct {')
for lhs,rhs in akhn_m: fea.append(' sub %s by %s;'%(S(lhs),rhs))
fea.append('} cjct;')
fea.append('feature calt {')
fea.append(' lookup SP {')
for sp_,t_ in (('¸','M¨©z'),('ï','k¨©z'),('û','n¨©z'),('ü','n¨©\u2026')):
    fea.append('  sub %s %s %s by %s;'%(need(sp_),L('©'),L('¨'),need(t_)))
for sp_,ya_,rp_ in (('¸','My¨','M©z'),('ï','ky¨','k©z'),('û','ny¨','n©z'),('ü','n¨\u2026','n©\u2026'),('iæ',None,'i©z'),('iƒ',None,'i©\u201a')):
    if ya_: fea.append('  sub %s %s by %s;'%(need(sp_),L('¨'),need(ya_)))
    fea.append('  sub %s %s by %s;'%(need(sp_),L('©'),need(rp_)))
fea.append(' } SP;')
kv={'y':'z','~':'\u201a','\u2026':'\u2026','u':'u'}
for nm,items in (('SWc',[(['%s','©','¨'],'¨©%s')]),('SWa',[(['%s','©'],'©%s')]),):
    fea.append(' lookup %s {'%nm)
    for k,v in kv.items():
        lhs=[L(k)]+[L('©')]+([L('¨')] if nm=='SWc' else [])
        rhs=need(('¨©' if nm=='SWc' else '©')+v)
        fea.append('  sub %s by %s;'%(S(lhs),rhs))
    fea.append(' } %s;'%nm)
fea.append(' lookup SWb { sub %s %s by %s; } SWb;'%(L('©'),L('¨'),need('¨©')))
fea.append(' lookup SW3 { sub %s %s by %s; } SW3;'%(L('\u2026'),L('¨'),need('¨\u2026')))
fea.append(' lookup SW1 {')
for k,c in swap_ya: fea.append('  sub %s %s by %s;'%(L('¨'),k,c))
fea.append('  sub %s %s by %s;'%(L('v'),L('u'),uv))
fea.append(' } SW1;')
fea.append(' lookup SW2 { sub %s %s by %s; } SW2;'%(L('¨'),uv,need('u¨v')))
# e-kar / oi-kar: default word-start glyph, mid-word variant after any non-opener glyph
fea.append(' lookup EK {')
fea.append('  sub [%s] %s\' by %s;'%(S(alln),L('\u2020'),L('\u2021')))
fea.append('  sub [%s] %s\' by %s;'%(S(alln),L('\u02c6'),L('\u2030')))
fea.append('  sub [%s] %s\' by %s;'%(S(alln),need('\u2020v'),need('\u2021v')))
fea.append('  sub [%s] %s\' by %s;'%(S(alln),need('\u02c6v'),need('\u2030v')))
fea.append(' } EK;')
fea.append(' lookup UK1 {')
fea.append('  ignore sub [%s] [%s] %s\';'%(S(SY),S(RA_ALL),L('y')))
fea.append('  ignore sub [%s] [%s] %s\';'%(S(SY),S(RA_ALL),L('~')))
fea.append('  sub [%s] %s\' by %s;'%(S(RA_AFTER),L('y'),L('\u00e6')))
fea.append('  sub [%s] %s\' by %s;'%(S(RA_AFTER),L('~'),L('\u0192')))
fea.append(' } UK1;')
fea.append(' lookup UK2 {')
fea.append('  sub [%s] %s\' by %s;'%(S(Z),L('y'),L('z')))
fea.append('  sub [%s] %s\' by %s;'%(S(Z),L('~'),L('\u201a')))
fea.append('  sub [%s] %s\' by %s;'%(S(R),L('\u2026'),L('\u201e')))
for k,c in swap_ya:
    pass
fea.append(' } UK2;')
fea.append(' lookup PH {')
fea.append('  sub [%s] %s\' by %s;'%(S(RAO),L('ª'),L('Ö')))
fea.append('  sub [%s] %s\' by %s;'%(S(RAF),L('ª'),L('«')))
fea.append('  sub [%s] %s\' by %s;'%(S(BAC),L('¡'),L('^')))
fea.append('  sub [%s] %s\' by %s;'%(S(BAY),L('¡'),L('Ÿ')))
fea.append('  sub [%s] %s\' by %s;'%(S(BAB),L('¡'),L('¦')))
fea.append('  sub [%s] %s\' by %s;'%(S(LAA),L('ø'),L('¬')))
fea.append(' } PH;')
fea.append('} calt;')
fea='\n'.join(fea); open('features_v3.fea','w').write(fea)

# ---------- composites ----------
for n in ('nukta','zwj','zwnj','abeng_aa'):
    g=Glyph(); g.numberOfContours=0; f['glyf'].glyphs[n]=g; hm[n]=(0,0)
for n,parts in newglyphs.items():
    # Keep the composed conjuncts as real TrueType composites so each component
    # keeps its original hinting and renders exactly like the ANSI text run.
    g=Glyph(); g.numberOfContours=-1; g.components=[]; x=0
    for p in parts:
        c=GlyphComponent(); c.glyphName=p; c.x=x; c.y=0; c.flags=0
        g.components.append(c); x+=hm[p][0]
    f['glyf'].glyphs[n]=g
    g.recalcBounds(f['glyf']); hm[n]=(x,getattr(g,'xMin',0) if g.numberOfContours<0 else 0)
f.setGlyphOrder(order+['nukta','zwj','zwnj','abeng_aa']+list(newglyphs))
cmap.update({0x09BC:'nukta',0x200D:'zwj',0x200C:'zwnj',0x0986:'abeng_aa'})
for n in f.getGlyphOrder():
    g=f['glyf'][n]
    if g.numberOfContours>0 and n not in ORIG_HINTED:
        g.program=ttProgram.Program(); g.program.fromBytecode(b'')
for t in ('hdmx','LTSH','VDMX'):      # per-glyph caches, invalid after adding glyphs; fpgm/prep/cvt + original glyph programs are KEPT
    if t in f: del f[t]
cm=newTable('cmap'); cm.tableVersion=0; cm.tables=[]
for pid,eid in ((0,3),(3,1)):
    t=CmapSubtable.newSubtable(4); t.platformID=pid; t.platEncID=eid; t.language=0; t.cmap=dict(cmap); cm.tables.append(t)
f['cmap']=cm
addOpenTypeFeaturesFromString(f,fea)
nm=f['name']; nm.names=[r for r in nm.names if r.nameID==0]
fam='SutonnyMJ Unicode'
for pid,eid,lid in ((3,1,0x409),(1,0,0)):
    for i,s in ((1,fam),(2,'Regular'),(3,fam+' v4.0'),(4,fam),(5,'Version 4.0 (Unicode conversion of SutonnyMJ ANSI outlines)'),(6,'SutonnyMJ-Unicode-v4.0')):
        nm.setName(s,i,pid,eid,lid)
# OS/2 + hhea left exactly as in the original SutonnyMJ (incl. fsType)
f['head'].flags=ORIG_HEAD_FLAGS
os2=f['OS/2']
os2.recalcUnicodeRanges(f)
# OS/2 v4: declare the Bengali Unicode range explicitly so Word/Windows do not
# skip the family as "no Bengali glyphs"; add required v4 fields.
os2.version=4
os2.ulUnicodeRange1 |= 1            # Basic Latin
os2.ulUnicodeRange3 |= (1 << 1)     # Bengali block (bit 65)
os2.sxHeight=getattr(os2,'sxHeight',0) or 0
os2.sCapHeight=getattr(os2,'sCapHeight',0) or 0
os2.usDefaultChar=0
os2.usBreakChar=32
os2.usMaxContext=4
os2.ulCodePageRange1=0
os2.ulCodePageRange2=0
f['post'].formatType=2.0
f.save(OUT); print('saved',OUT,len(f.getGlyphOrder()),'glyphs;',len(akhn),'conjunct rules;',len(newglyphs),'composites')
