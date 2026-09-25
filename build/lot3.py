#!/usr/bin/env python3
"""Temoin, etape 2, lot 3 : les petites capitales.

Atkinson Hyperlegible Next n'en a aucune. Elles sont donc derivees, pas
dessinees a la main : chaque petite capitale est une capitale prise plus haut
sur l'axe de graisse, puis reduite.

Le point d'appui est une mesure : dans cette source, la coordonnee de l'axe de
dessin vaut exactement la largeur du fut de la capitale (60 / 94 / 158 / 170
pour des futs de 56 / 94 / 158 / 170). Demander un fut de X unites revient a
demander le point X de l'axe. La compensation de graisse n'est donc pas un
reglage a tatons, elle se resout.

    reduction   s  = hauteur_pc / hauteur_capitale
    source      d' = fut_bas_de_casse(master) / s

La cible est le fut du bas de casse, pas celui de la capitale : une petite
capitale doit avoir la couleur du texte qui l'entoure. Ce rapport n'est pas
constant dans la source (0,89 en Regular, 0,96 a 0,97 dans les trois autres
masters), il est donc mesure master par master et non applique en bloc.

Consequence a assumer : pour les masters gras, d' passe au-dela du dernier
master. On extrapole. Les facteurs sont journalises et verifies.
"""

import math
import statistics

from glyphsLib.classes import (GSGlyph, GSLayer, GSPath, GSNode, GSAnchor,
                               GSComponent)

import coupe as K
import lot2 as L


# --------------------------------------------------------------- geometrie

def crossings(layer, y, tol=0.5):
    """Abscisses ou la droite horizontale y coupe le contour, dedoublonnees."""
    xs = []
    for p in L.paths(layer):
        for s in K.to_segs(p):
            for near in (0.0, 0.25, 0.5, 0.75, 1.0):
                t = K.hit_plane(s, (0.0, 1.0), y, near)
                if t is not None and -1e-6 <= t <= 1 + 1e-6:
                    xs.append(float(K.bez(s, min(max(t, 0.0), 1.0))[0]))
    xs.sort()
    out = []
    for x in xs:
        if not out or abs(x - out[-1]) > tol:
            out.append(x)
    return out


def fut(font, nom, master_id, hauteur, parts=(0.15, 0.22, 0.30, 0.38, 0.62, 0.70)):
    """Largeur du fut gauche d'un glyphe, mediane sur plusieurs hauteurs.

    Mediane et non mesure unique : a une hauteur donnee on peut tomber sur une
    jonction, une barre ou un raccord, et se tromper de plusieurs unites.
    """
    g = font.glyphs[nom]
    if g is None:
        return None
    lay = next((l for l in g.layers if l.layerId == master_id), None)
    if lay is None:
        return None
    vals = []
    for k in parts:
        c = crossings(lay, hauteur * k)
        if len(c) >= 2:
            vals.append(c[1] - c[0])
    return statistics.median(vals) if vals else None


def mesures(font):
    """Par master : (coordonnee d'axe, fut de capitale, fut de bas de casse)."""
    out = {}
    for m in font.masters:
        cap = m.capHeight or 668
        xh = m.xHeight or 496
        c = statistics.median([v for v in (fut(font, "H", m.id, cap),
                                           fut(font, "I", m.id, cap)) if v])
        b = statistics.median([v for v in (fut(font, "n", m.id, xh),
                                           fut(font, "m", m.id, xh)) if v])
        out[m.id] = (m.axes[0], c, b)
    return out


# ------------------------------------------------- interpolation sur l'axe

def formes(font, nom, layer_id, depth=0):
    """Contours d'un calque, composants resolus, sous forme de listes brutes.

    Retourne (points, natures, ferme?) par contour. Les capitales accentuees du
    francais sont toutes des composites — Agrave, Eacute, Ocircumflex... — et
    L.paths() ne voit que les contours dessines : sans cette resolution, elles
    sortaient vides. Les deux exceptions sont Ccedilla, AE et OE, qui sont
    dessines directement.
    """
    g = font.glyphs[nom]
    if g is None or depth > 4:
        return [], [], []
    lay = next((l for l in g.layers if l.layerId == layer_id), None)
    if lay is None:
        return [], [], []
    pts, nat, fer = [], [], []
    for p in L.paths(lay):
        pts.append([(n.position.x, n.position.y) for n in p.nodes])
        nat.append([(n.type, n.smooth) for n in p.nodes])
        fer.append(p.closed)
    for s in lay.shapes:
        if not isinstance(s, GSComponent):
            continue
        t = list(s.transform)
        xx, xy, yx, yy, dx, dy = (t + [0] * 6)[:6]
        if (dx, dy) == (0, 0):
            dx, dy = _attache(font, lay, s.componentName)
        sp, sn, sf = formes(font, s.componentName, layer_id, depth + 1)
        for c in sp:
            pts.append([(xx * x + yx * y + dx, xy * x + yy * y + dy)
                        for x, y in c])
        nat += sn
        fer += sf
    return pts, nat, fer


def _attache(font, base_layer, mark_name):
    """Position d'une marque par ses ancres, quand le composant est a zero."""
    g = font.glyphs[mark_name]
    if g is None:
        return (0.0, 0.0)
    ml = next((l for l in g.layers if l.layerId == base_layer.layerId), None)
    if ml is None:
        return (0.0, 0.0)
    ma = {a.name: (a.position.x, a.position.y) for a in ml.anchors}
    ba = {a.name: (a.position.x, a.position.y) for a in base_layer.anchors}
    for cle in ("_top", "_bottom", "_topright", "_center"):
        if cle in ma and cle[1:] in ba:
            return (ba[cle[1:]][0] - ma[cle][0], ba[cle[1:]][1] - ma[cle][1])
    return (0.0, 0.0)


def largeur_calque(font, nom, layer_id):
    g = font.glyphs[nom]
    lay = next((l for l in g.layers if l.layerId == layer_id), None)
    return lay.width if lay else 0.0


def axe_pour_fut(font, cible, _cache=None):
    """Coordonnee de l'axe ou le fut de la capitale vaut `cible`.

    La coordonnee de l'axe vaut le fut de la capitale sur trois masters sur
    quatre (94, 158, 170), mais pas sur l'ExtraLight, ou l'axe vaut 60 pour un
    fut de 56. Supposer l'identite y donnait une petite capitale 5 % trop
    maigre — mesure de check5.py. La relation est donc inversee pour de bon,
    par morceaux, sur les valeurs mesurees.
    """
    M = _cache or mesures(font)
    pts = sorted((v[0], v[1]) for v in M.values())      # (axe, fut de capitale)
    if cible <= pts[0][1]:
        a, b = pts[0], pts[1]
    elif cible >= pts[-1][1]:
        a, b = pts[-2], pts[-1]
    else:
        a, b = next((pts[i], pts[i + 1]) for i in range(len(pts) - 1)
                    if pts[i][1] <= cible <= pts[i + 1][1])
    return a[0] + (cible - a[1]) * (b[0] - a[0]) / (b[1] - a[1])


def couple(font, d):
    """Les deux masters qui servent a atteindre la coordonnee d.

    A l'interieur de l'axe, les deux qui encadrent. Au-dela, les deux derniers :
    c'est la pente locale qui prolonge le dessin, pas une corde lointaine, dont
    on a mesure qu'elle donne une contreforme de O fausse de 7 %.
    """
    ax = sorted((m.axes[0], m.id) for m in font.masters)
    if d <= ax[0][0]:
        return ax[0], ax[1]
    if d >= ax[-1][0]:
        return ax[-2], ax[-1]
    for i in range(len(ax) - 1):
        if ax[i][0] <= d <= ax[i + 1][0]:
            return ax[i], ax[i + 1]
    return ax[-2], ax[-1]


def interpoler(font, nom, d, ref_id=None):
    """Contours du glyphe `nom` au point d de l'axe de dessin.

    Interpolation lineaire noeud a noeud entre deux masters, c'est-a-dire
    exactement ce que fait fontmake. Au-dela du dernier master, la meme formule
    extrapole.

    `ref_id` designe le master dont on recopie la nature des noeuds. Il n'est
    pas facultatif dans les faits : chaque master vise une source differente,
    donc un couple d'interpolation different, et le drapeau `smooth` n'est pas
    identique partout dans la source (le D l'a en Bold et pas ailleurs). Sans
    reference unique, les calques .sc d'un meme glyphe sortaient avec des
    topologies differentes — trouve par check5.py, pas a l'oeil.
    """
    (da, ida), (db, idb) = couple(font, d)
    A, natA, ferA = formes(font, nom, ida)
    B, _, _ = formes(font, nom, idb)
    natR, ferR = natA, ferA
    if ref_id is not None:
        _, natR, ferR = formes(font, nom, ref_id)
    if [len(c) for c in A] != [len(c) for c in B]:
        raise ValueError(f"{nom} : topologie differente entre {da} et {db}")
    t = (d - da) / (db - da)
    ctrs = [[(pa[0] + t * (pb[0] - pa[0]), pa[1] + t * (pb[1] - pa[1]))
             for pa, pb in zip(ca, cb)] for ca, cb in zip(A, B)]
    anc = {}
    g = font.glyphs[nom]
    la = next(l for l in g.layers if l.layerId == ida)
    lb = next(l for l in g.layers if l.layerId == idb)
    aa = {a.name: (a.position.x, a.position.y) for a in la.anchors}
    ab = {a.name: (a.position.x, a.position.y) for a in lb.anchors}
    for k in aa:
        if k in ab:
            anc[k] = (aa[k][0] + t * (ab[k][0] - aa[k][0]),
                      aa[k][1] + t * (ab[k][1] - aa[k][1]))
    w = la.width + t * (lb.width - la.width)
    return ctrs, natR, ferR, w, anc, t


# --------------------------------------------------------- fabrication .sc

# -------------------------------------------- plafond d'extrapolation mesure

RASTER = 1600


def _topologie(ctrs, nat, fer, taille=RASTER):
    """(nombre de taches d'encre, nombre de regions de fond) d'un jeu de
    contours, par rasterisation."""
    import numpy as np
    from scipy import ndimage
    from PIL import Image, ImageDraw

    plats = []
    for pts, ty, cl in zip(ctrs, nat, fer):
        p = GSPath()
        p.closed = cl
        for (x, y), (kind, sm) in zip(pts, ty):
            n = GSNode((x, y), kind)
            n.smooth = sm
            p.nodes.append(n)
        segs = K.to_segs(p)
        plat = []
        for s in segs:
            if s["kind"] == "line":
                plat.append(s["p3"])
            else:
                for i in range(1, 13):
                    q = K.bez(s, i / 12)
                    plat.append((float(q[0]), float(q[1])))
        plats.append(plat)

    # LE CLASSEMENT EST PAR IMBRICATION, point 85, quarante-neuvieme tour.
    # Cette fonction compte les TACHES d'encre, et un contour greffe efface en
    # retire une : le compte tomberait d'une unite sans qu'aucune erreur ne
    # sorte, et c'est sur ce compte que `plafonner` decide ou la topologie
    # change. Le lot 3 derive du O, donc le jour ou `o.sc` recevrait le bras --
    # ecarte au quarante-huitieme tour, et c'est un arbitrage revisable -- la
    # mesure serait fausse en silence.
    import dessin as D

    k = taille / 1000.0
    im = Image.new("L", (int(taille * 1.8), int(taille * 1.8)), 255)
    d = ImageDraw.Draw(im)
    for c, e in D.couches_ecran(
            plats, lambda x, y: (taille * 0.4 + x * k, taille * 1.4 - y * k)):
        if len(c) > 2:
            d.polygon(c, fill=0 if e else 255)
    a = np.array(im) < 128
    return (ndimage.label(a, structure=np.ones((3, 3)))[1],
            ndimage.label(~a)[1])


def plafonner(font, base, master_id, ref_id, d_cible, journal=None, nom=""):
    """Ramene d_cible sous le point ou le glyphe change de topologie.

    Une petite capitale est une capitale reduite : elle doit avoir le meme
    nombre de taches d'encre et de contreformes que sa capitale. L'extrapolation
    au-dela du dernier master peut casser cette egalite — mesure : le M
    italique referme son sommet gauche vers 178, alors que la source visee vaut
    200. Le plafond n'est donc pas choisi, il est trouve par dichotomie.

    Le romain ne declenche jamais ce plafond : ses 26 lettres tiennent au-dela
    de 215.
    """
    dmax = max(m.axes[0] for m in font.masters)
    if d_cible <= dmax:
        return d_cible
    ref = _topologie(*formes(font, base, master_id)[:3])
    if _topologie(*interpoler(font, base, d_cible, ref_id)[:3]) == ref:
        return d_cible
    lo, hi = dmax, d_cible
    for _ in range(7):
        mil = (lo + hi) / 2
        if _topologie(*interpoler(font, base, mil, ref_id)[:3]) == ref:
            lo = mil
        else:
            hi = mil
    if journal is not None:
        journal.append({"plafond": nom, "base": base, "vise": d_cible,
                        "retenu": lo,
                        "master": next(m.name for m in font.masters
                                       if m.id == master_id)})
    return lo


def petite_capitale(font, base, master_id, hauteur, largeur=1.0, sb=0.0,
                    journal=None, compenser=True, _cache=None, ref_id=None,
                    plafond=True):
    """Un calque de petite capitale, derive de la capitale `base`.

    `hauteur` est la hauteur voulue de la petite capitale, en unites.
    `largeur` est le facteur applique en plus horizontalement : 1.0 donne une
    reduction homothetique, qui conserve exactement les angles de coupe du
    lot 2 ; au-dela, la lettre s'elargit et les angles derivent un peu.
    `sb` est l'approche ajoutee de chaque cote, en unites.
    `compenser` a False donne la reduction nue, sans rattrapage de graisse :
    c'est le temoin de comparaison, pas un reglage utilisable.
    """
    m = next(m for m in font.masters if m.id == master_id)
    cap = m.capHeight or 668
    cache = _cache or mesures(font)
    _, c_fut, b_fut = cache[master_id]
    s = hauteur / cap
    # Le fut vertical est mis a l'echelle par kx, pas par s. Elargir la lettre
    # sans l'alourdir demande donc de prendre la source un peu plus bas sur
    # l'axe : `largeur` ouvre les contreformes a graisse constante, ce qui est
    # le seul reglage de chasse qui ait un sens ici.
    kx, ky = s * largeur, s
    d = axe_pour_fut(font, b_fut / kx, cache) if compenser else m.axes[0]
    if plafond and compenser:
        d = plafonner(font, base, master_id, ref_id, d, journal, base)

    ctrs, types, closed, w, anc, t = interpoler(font, base, d, ref_id)
    lay = GSLayer()
    lay.layerId = master_id
    lay.associatedMasterId = master_id
    lay.width = round(w * kx + 2 * sb, 1)
    for pts, ty, cl in zip(ctrs, types, closed):
        p = GSPath()
        p.closed = cl
        for (x, y), (kind, smooth) in zip(pts, ty):
            n = GSNode((round(x * kx + sb, 1), round(y * ky, 1)), kind)
            n.smooth = smooth
            p.nodes.append(n)
        lay.shapes.append(p)
    for name, (ax_, ay_) in anc.items():
        lay.anchors.append(GSAnchor(name, (round(ax_ * kx + sb, 1),
                                           round(ay_ * ky, 1))))
    if journal is not None:
        journal.append({"master": m.name, "base": base, "s": s, "d": d,
                        "extrapolation": t > 1.0 or t < 0.0, "t": t,
                        "fut_bdc": b_fut, "fut_cap": c_fut,
                        "fut_vise": b_fut * largeur})
    return lay


LETTRES = "abcdefghijklmnopqrstuvwxyz"

# Capitales accentuees utiles au francais, plus les deux ligatures.
ACCENTUEES = {
    "agrave": "Agrave", "acircumflex": "Acircumflex", "adieresis": "Adieresis",
    "ccedilla": "Ccedilla",
    "eacute": "Eacute", "egrave": "Egrave", "ecircumflex": "Ecircumflex",
    "edieresis": "Edieresis",
    "icircumflex": "Icircumflex", "idieresis": "Idieresis",
    "ocircumflex": "Ocircumflex", "odieresis": "Odieresis",
    "ugrave": "Ugrave", "ucircumflex": "Ucircumflex", "udieresis": "Udieresis",
    "ydieresis": "Ydieresis",
    "ae": "AE", "oe": "OE",
}


def jeu(font):
    """Le jeu minimal pour le francais : 26 lettres + 18 formes accentuees.

    (nom du glyphe .sc, capitale source, minuscule qui le declenche en smcp,
     capitale qui le declenche en c2sc)
    """
    out = []
    for ch in LETTRES:
        out.append((ch + ".sc", ch.upper(), ch, ch.upper()))
    for bas, haut in ACCENTUEES.items():
        if font.glyphs[haut] is not None and font.glyphs[bas] is not None:
            out.append((bas + ".sc", haut, bas, haut))
    return out


def appliquer_lot(font, hauteur, largeur=1.0, sb=0.0, journal=None,
                  bases=None, compenser=True, plafond=True):
    """Ajoute tous les glyphes .sc a une source deja traitee par les lots 1 et 2.

    L'ordre compte : les petites capitales heritent des coupes du lot 2, elles
    ne les recoivent pas une seconde fois. Une reduction homothetique conserve
    exactement l'angle d'une coupe, et une affinite conserve l'alignement des
    bouts de barre du F : les deux proprietes du lot 2 traversent la reduction.
    """
    ids = [m.id for m in font.masters]
    cache = mesures(font)
    ajoutes = []
    for nom, base, _, _ in jeu(font):
        src = font.glyphs[base]
        if src is None or (bases is not None and base not in bases):
            continue
        g = GSGlyph(nom)
        g.category, g.subCategory = src.category, src.subCategory
        g.export = True
        for mid in ids:
            g.layers.append(petite_capitale(font, base, mid, hauteur,
                                            largeur, sb, journal,
                                            compenser, cache, ids[1], plafond))
        font.glyphs.append(g)
        ajoutes.append(nom)
    return ajoutes
