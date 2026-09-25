"""Controle complet : les localisateurs designent-ils la meme chose partout,
et les invariants tiennent-ils ?

TROIS CODES DEPUIS LE SOIXANTE-SEPTIEME TOUR, point ouvert 31 : 0 conforme,
1 signale, 2 non mesure. Le script comptait sans rendre de code.

TROIS CRITERES COMPTENT, DEUX SONT PERIMES. Les localisateurs stables, la
topologie commune aux masters et la chasse inchangee restent vrais du projet.
La boite qui ne grandit pas et l'aire qui ne gonfle pas etaient les invariants
du lot 2, quand tout geste rentrait dans le glyphe ; les gestes sortants des
vingt-deux, arbitres depuis le vingt-cinquieme tour, les contredisent par
construction, et le script les signalait 261 fois. Ils restent affiches, sous
leur nom, et ne comptent pas : leur ecrire des exceptions serait un arbitrage.
"""
import os
import sys

import glyphsLib, coupe as K, lot2 as L

SOURCES = (("/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs", "roman"),
           ("/tmp/ahn/sources/AtkinsonHyperlegibleNext-Italic.glyphs", "ital"))
absentes = [src for src, _lab in SOURCES if not os.path.exists(src)]
if absentes:
    for src in absentes:
        print(f"NON MESURE : source absente, {src}")
    sys.exit(2)

def bbox(layer):
    xs, ys = [], []
    for p in L.paths(layer):
        for s in K.to_segs(p):
            for t in range(21):
                q = K.bez(s, t/20); xs.append(float(q[0])); ys.append(float(q[1]))
    return min(xs), min(ys), max(xs), max(ys)

total = 0            # les trois criteres encore vrais
for src, lab in SOURCES:
    f0 = glyphsLib.load(open(src, encoding="utf-8"))
    f = glyphsLib.load(open(src, encoding="utf-8"))
    mid = {m.id: m.name for m in f.masters}
    # 1. localisateurs stables avant traitement
    souci = []
    for nom, loc, sense, roll, ang in L.LOT2:
        g = f0.glyphs[nom]
        if g is None: continue
        vus = set()
        for l in g.layers:
            if l.layerId in mid:
                vus.add(tuple(loc(K.to_segs(L.main_path(l)))))
        if len(vus) != 1 or not list(vus)[0]:
            souci.append((nom, loc.__name__, vus))
    print(f"--- {lab} : localisateurs instables ou vides : {souci or 'aucun'}")
    total += len(souci)
    # 2. application
    J = []
    L.appliquer_lot(f, 20.0, J)
    noms = sorted({n for n, _, _, _, _ in L.LOT2} | {"E", "F"})
    div = [n for n in noms if f.glyphs[n] is not None and
           len({tuple(tuple(x.type for x in p.nodes) for p in L.paths(l))
                for l in f.glyphs[n].layers if l.layerId in mid}) != 1]
    print(f"    topologie divergente : {div or 'aucune'}   ({len(J)} coupes)")
    total += len(div)
    # 3. chasses et boites
    pb = 0       # boites et aires, criteres perimes, affiches sans compter
    pw = 0       # chasses, critere vrai
    for nom in noms:
        gb, gv = f0.glyphs[nom], f.glyphs[nom]
        if gb is None: continue
        for lb in gb.layers:
            if lb.layerId not in mid: continue
            lv = [x for x in gv.layers if x.layerId == lb.layerId][0]
            if lb.width != lv.width:
                print(f"    CHASSE {nom} {mid[lb.layerId]}"); pw += 1
            a, b_ = bbox(lb), bbox(lv)
            if b_[0] < a[0]-0.6 or b_[1] < a[1]-0.6 or b_[2] > a[2]+0.6 or b_[3] > a[3]+0.6:
                print(f"    BOITE {nom} {mid[lb.layerId]} {tuple(round(x,1) for x in a)} -> {tuple(round(x,1) for x in b_)}"); pb += 1
            # aire : un contour qui se retourne ou se croise saute aux yeux ici
            for p0, p1 in zip(L.paths(lb), L.paths(lv)):
                a0, a1 = K.area(K.to_segs(p0)), K.area(K.to_segs(p1))
                if a1 * a0 <= 0 or abs(a1) > abs(a0) * 1.02 or abs(a1) < abs(a0) * 0.80:
                    print(f"    AIRE {nom} {mid[lb.layerId]} {a0:.0f} -> {a1:.0f}"); pb += 1
    print(f"    chasses : {pw} anomalie(s)   |   boites / aires, criteres "
          f"perimes, affiches sans compter : {pb}")
    total += pw
    # 4. barres du F et du E : les coupes sont-elles alignees ?
    for nom in ("F", "E"):
        for l in f.glyphs[nom].layers:
            if l.layerId not in mid: continue
            segs = K.to_segs(L.main_path(l))
            b = sorted(L.lines(segs, vertical=True), key=lambda i: K.mid(segs[i])[1])
            dirs = [K.unit(K.V(segs[i]["p3"]) - K.V(segs[i]["p0"])) for i in b]
            import math
            angs = [round(math.degrees(math.atan2(d[0], abs(d[1]))), 2) for d in dirs]
            xs = [round(K.mid(segs[i])[0], 1) for i in b]
            print(f"    {nom} {mid[l.layerId][:12]:12s} bouts x={xs} angles={angs}")

print(f"\nTOTAL : {total} anomalie(s) sur les trois criteres qui comptent.")
sys.exit(1 if total else 0)
