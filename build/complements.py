#!/usr/bin/env python3
"""Le repertoire du site, soixante-treizieme tour : version 1.002.

LA DEMANDE. La session SEO a releve les caracteres que les fiches
d'oxanimale.fr emploient et que le WOFF2 servi n'a pas
(`seo/recommandations-temoin-2026-09-27.md`). Nicolas a retenu les deux
priorites, plus l'exposant e et l'exposant r :

  - sans dessin : U+2010 et U+2011 sur `hyphen`, U+2206 sur `Delta`, et
    U+0391 U+0392 sur `A` et `B` pour `case_mapping` de Font Bakery ;
    mu, Delta et approxequal entrent au servi par `subset_unicodes.txt` ;
  - a dessiner : alpha, beta, la fleche, e et r en exposant.

AUCUN DESSIN A MAIN LEVEE. Atkinson n'a ni alpha, ni beta, ni fleche, ni
exposant, et la version du Braille Institute n'en a pas davantage (point 6,
ferme au meme tour). Chaque glyphe neuf est donc CONSTRUIT a partir de pieces
que la police sert deja, et la construction est une operation ecrite, pas un
dessin :

  alpha   la panse du `o`, traversee a droite par un trait courbe dont les
          deux bouts depassent en haut et en bas : un arc de cercle de rayon
          1,5 fois la demi-hauteur de la panse, au trait du cote droit de la
          panse a mi-hauteur. DEUX CONTOURS QUI SE RECOUVRENT, comme le bras
          du O : les fondre casserait l'interpolation. Choisi par Nicolas sur
          `planche-tour73-alpha.png`, apres le refus d'un premier jet.
  beta    le `germandbls`, dont le fut descend a la profondeur du `p`, le long
          de ses propres bords : les deux noeuds du bas du fut prennent la
          hauteur des deux noeuds du bas du fut du `p`, plongee comprise.
  fleche  la hampe du `minus`, a sa hauteur et a son epaisseur, et une tete
          dont les bras ont le trait de la hampe et le bout plat du `greater`,
          a 30 degres (`VARIANTES_FLECHE`, choix de Nicolas sur planche). La
          tete a la hauteur de celle du `greater` reduite de `TETE`, et
          grandit dans les gras quand il le faut pour que les bras depassent
          la hampe d'au moins `BRAS` fois son epaisseur.
  emod    le `e` et le `r` passes par la regle qu'Atkinson applique a ses
  rmod    ordinaux, MESUREE : `ordmasculine` est le `o` pris plus haut sur
          l'axe de dessin, reduit et monte (2 a 3 unites d'ecart rms sur les
          noeuds). La regle se remesure a chaque passage, master par master,
          sur le couple o / ordmasculine de la source, et s'applique telle
          quelle au e et au r.

EN DERNIER DANS `make_temoin.process`, apres le micro : les pieces portent
alors tous les gestes du projet, et aucune etape posterieure ne touche les
glyphes neufs (piege du soixante-douzieme tour : un nom absent de l'amont
n'entre dans aucun perimetre). Des copies de contours, jamais des composites :
un composite ferait entrer ses composants au servi, donc au perimetre du
titrage.

LEVE sur toute anomalie : une piece dont la topologie a change, un glyphe
neuf qui existe deja, un code deja porte.
"""

import math

import numpy as np
from glyphsLib.classes import GSGlyph, GSLayer, GSPath, GSNode

import lot2 as L
import lot3


ALPHA, BETA, FLECHE, EXP_E, EXP_R = "alpha", "beta", "rightArrow", "emod", "rmod"
NEUFS = (ALPHA, BETA, FLECHE, EXP_E, EXP_R)
UNICODES = {ALPHA: "03B1", BETA: "03B2", FLECHE: "2192", EXP_E: "1D49",
            EXP_R: "02B3"}

#: Les codes ajoutes a des glyphes existants. Un seul dessin, deux codes : le
#: trait d'union (U+2010) et le trait d'union insecable (U+2011) sont le
#: `hyphen` ; l'increment (U+2206) est le Delta. Les capitales grecques alpha
#: (U+0391) et beta (U+0392) sont le A et le B : sans elles, `case_mapping` de
#: Font Bakery passe en FAIL des que l'alpha et le beta sont dans la police,
#: mesure au soixante-treizieme tour.
RENVOIS = {"hyphen": ("2010", "2011"), "Delta": ("2206",),
           "A": ("0391",), "B": ("0392",)}

#: Groupes de crenage : (gauche, droite). L'alpha a la panse du o a gauche, et
#: a droite un groupe a son nom : aucun glyphe n'a son trait croise. Le beta a
#: les deux bords du germandbls. La fleche et les exposants prennent un groupe
#: a leur propre nom, comme les etoiles : aucune paire ne les vise.
GROUPES = {ALPHA: ("o", ALPHA), BETA: ("germandbls", "germandbls"),
           FLECHE: (FLECHE, FLECHE), EXP_E: (EXP_E, EXP_E),
           EXP_R: (EXP_R, EXP_R)}

#: Angle des bras de la tete sur la hampe, en degres. Le `greater` est a 24 :
#: a cet angle, des bras au trait de la hampe donnent une tete aussi longue
#: que la fleche, mesure au premier essai.
VARIANTES_FLECHE = {"30": 30.0, "40": 40.0, "50": 50.0}
VARIANTE_FLECHE = "30"           # choix de Nicolas, planche du tour 73

#: Longueur de la fleche, en part de la longueur d'encre du `minus`.
LONGUEUR = 1.3

#: Demi-hauteur de la tete, en part de celle du `greater`.
TETE = 0.8

#: Depassement minimal des bras au-dela de la hampe, en epaisseurs de hampe.
BRAS = 0.5


# ------------------------------------------------------------------ outils

def _penche(m):
    return math.tan(math.radians(m.italicAngle or 0.0))


def _calque(glyphe, master_id):
    lay = next((l for l in glyphe.layers if l.layerId == master_id), None)
    if lay is None:
        raise ValueError(f"{glyphe.name} n'a pas de calque pour {master_id}")
    if any(not isinstance(s, GSPath) for s in lay.shapes):
        raise ValueError(f"{glyphe.name} porte un composant : la copie par les "
                         "contours le perdrait")
    return lay


def _exterieur(lay):
    """Le contour qui porte le fut : le plus grand en nombre de noeuds."""
    ps = L.paths(lay)
    return max(range(len(ps)), key=lambda i: len(ps[i].nodes))


def _pts(p):
    return [(n.position.x, n.position.y) for n in p.nodes]


def _copier(lay):
    neuf = GSLayer()
    neuf.layerId = neuf.associatedMasterId = lay.layerId
    neuf.width = lay.width
    for s in lay.shapes:
        neuf.shapes.append(s.clone())
    return neuf


def _poser(p, i, x, y):
    n = p.nodes[i]
    n.position = type(n.position)(round(x, 1), round(y, 1))


def _chemin(pts):
    p = GSPath()
    p.closed = True
    for x, y in pts:
        p.nodes.append(GSNode((round(x, 1), round(y, 1)), "line"))
    return p


def _aire(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return a / 2.0


# ------------------------------------------------------------------- alpha
#
# PREMIER JET REFUSE PAR NICOLAS au soixante-treizieme tour : le `d` coupe a
# la hauteur d'x par la tete du `q` "ne ressemble pas du tout a un alpha". Il
# se lisait comme un a a un seul etage. Trois constructions le remplacent.

#: crochet   le `q`, dont le crochet remonte sur la ligne de base : une panse,
#:           un fut, et une queue qui part vers la droite.
#: croise    la panse du `o`, traversee a droite par un trait courbe dont les
#:           deux bouts depassent en haut et en bas. Arc de rayon 2 fois la
#:           demi-hauteur de la panse.
#: marque    le meme, arc de rayon 1,5 fois : le trait courbe davantage et les
#:           bouts depassent plus.
VARIANTES_ALPHA = {"crochet": None, "croise": 2.0, "marque": 1.5}
VARIANTE_ALPHA = "marque"        # choix de Nicolas, planche-tour73-alpha


def _crochet(font, master_id):
    m = next(m for m in font.masters if m.id == master_id)
    xh = m.xHeight or 496
    k = _penche(m)
    q = _copier(_calque(font.glyphs["q"], master_id))
    pq = L.paths(q)[_exterieur(q)]
    N = len(pq.nodes)
    on = [i for i, n in enumerate(pq.nodes) if n.type != "offcurve"]
    # le haut du fut : deux noeuds droits a la hauteur d'x
    hauts = [i for i in on if pq.nodes[i].type == "line"
             and abs(pq.nodes[i].position.y - xh) <= 40]
    if len(hauts) != 2 or (hauts[1] - hauts[0]) % N != 1:
        raise ValueError(f"alpha {m.name} : le haut du fut du q introuvable "
                         f"({hauts})")
    # le bas droit du fut : le noeud de courbe qui precede le haut du fut
    rb = max(i for i in on if i < hauts[0]) if hauts[0] > min(on) else max(on)
    # le bas gauche : le noeud droit le plus a gauche sous la mi-hauteur
    # d'x. L'autre noeud droit du bas est le bout de la queue, a droite. Le
    # bas du fut n'est pas toujours sous la ligne de base : a 6 et 39 unites
    # au-dessus dans le Bold italique.
    lbs = [i for i in on if pq.nodes[i].type == "line" and i not in hauts
           and pq.nodes[i].position.y < xh / 2]
    lb = min(lbs, key=lambda i: pq.nodes[i].position.x)
    crochet = [(lb + t) % N for t in range((rb - lb) % N + 1)]
    reste = [i for i in range(N) if i not in crochet]
    fond = min(pq.nodes[i].position.y for i in reste)
    D = fond - min(pq.nodes[i].position.y for i in crochet)
    if D <= 0:
        raise ValueError(f"alpha {m.name} : le crochet du q ne descend pas")
    for i in crochet:
        n = pq.nodes[i]
        _poser(pq, i, n.position.x + D * k, n.position.y + D)
    # le bas gauche du fut passe au-dessus de la jonction de la panse : il
    # disparait, et la jonction rejoint directement la courbe du crochet
    jonction = pq.nodes[(lb - 1) % N]
    if pq.nodes[lb].position.y > jonction.position.y:
        del pq.nodes[lb]
    return q


def _arc(cx, cy, r, a1, a2):
    """Les deux poignees d'un arc de cercle de a1 a a2 (radians)."""
    d = a2 - a1
    h = 4.0 / 3.0 * math.tan(d / 4.0) * r
    p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
    p2 = (cx + r * math.cos(a2), cy + r * math.sin(a2))
    t1 = (-math.sin(a1), math.cos(a1))
    t2 = (-math.sin(a2), math.cos(a2))
    return ((p1[0] + h * t1[0], p1[1] + h * t1[1]),
            (p2[0] - h * t2[0], p2[1] - h * t2[1]), p2)


def _croise(font, master_id, courbure):
    """La panse du `o` et un trait courbe qui la traverse a droite."""
    m = next(m for m in font.masters if m.id == master_id)
    k = _penche(m)
    o = _copier(_calque(font.glyphs["o"], master_id))
    ys = [n.position.y for p in L.paths(o) for n in p.nodes]
    bas, haut = min(ys), max(ys)
    yc, h = (bas + haut) / 2, (haut - bas) / 2
    # le cote droit de la panse a mi-hauteur : bord de la contreforme, bord
    # exterieur
    xs = lot3.crossings(o, yc)
    if len(xs) != 4:
        raise ValueError(f"alpha {m.name} : la panse du o ne coupe pas quatre "
                         f"fois sa mi-hauteur ({xs})")
    x_in, x_out = xs[2], xs[3]
    T = x_out - x_in
    xm = (x_in + x_out) / 2
    R = courbure * h
    Ro, Ri = R + T / 2, R - T / 2
    if Ri <= h:
        raise ValueError(f"alpha {m.name} : arc trop serre pour son trait")
    cx = xm + R
    ao, ai = math.asin(h / Ro), math.asin(h / Ri)
    P = lambda r, a: (cx + r * math.cos(a), yc + r * math.sin(a))
    BL, TL = P(Ro, math.pi + ao), P(Ro, math.pi - ao)
    BR, TR = P(Ri, math.pi + ai), P(Ri, math.pi - ai)
    # bord droit montant (angle decroissant), bord gauche descendant
    c1, c2, MR = _arc(cx, yc, Ri, math.pi + ai, math.pi)
    c3, c4, _ = _arc(cx, yc, Ri, math.pi, math.pi - ai)
    c5, c6, ML = _arc(cx, yc, Ro, math.pi - ao, math.pi)
    c7, c8, _ = _arc(cx, yc, Ro, math.pi, math.pi + ao)
    trait = [(BR, "line"), (c1, "offcurve"), (c2, "offcurve"), (MR, "curve"),
             (c3, "offcurve"), (c4, "offcurve"), (TR, "curve"), (TL, "line"),
             (c5, "offcurve"), (c6, "offcurve"), (ML, "curve"),
             (c7, "offcurve"), (c8, "offcurve"), (BL, "curve")]
    on_pts = [BR, MR, TR, TL, ML, BL]
    if _aire(on_pts) <= 0:
        raise ValueError(f"alpha {m.name} : trait dans le mauvais sens")
    p = GSPath()
    p.closed = True
    for (x, y), ty in trait:
        n = GSNode((round(x + (y - yc) * k, 1), round(y, 1)), ty)
        n.smooth = ty == "curve"
        p.nodes.append(n)
    o.shapes.append(p)
    droite = max(x + (y - yc) * k for (x, y), _ in trait)
    approche = o.width - max(n.position.x for pp in L.paths(o)[:2]
                             for n in pp.nodes)
    o.width = round(droite + approche)
    return o


def calque_alpha(font, master_id, variante=None):
    variante = variante or VARIANTE_ALPHA
    if variante not in VARIANTES_ALPHA:
        raise ValueError(f"variante d'alpha inconnue : {variante}")
    if VARIANTES_ALPHA[variante] is None:
        return _crochet(font, master_id), None
    return _croise(font, master_id, VARIANTES_ALPHA[variante]), None


# -------------------------------------------------------------------- beta

def _vers(a, b, y):
    """Le point de la droite (a, b) a la hauteur y."""
    (xa, ya), (xb, yb) = a, b
    if abs(yb - ya) < 1e-9:
        raise ValueError("bord horizontal : pas de prolongement vertical")
    return xa + (y - ya) * (xb - xa) / (yb - ya), y


def calque_beta(font, master_id):
    """Le `germandbls` a fut de `p`. Rend (calque, (y gauche, y droit))."""
    m = next(m for m in font.masters if m.id == master_id)
    s = _copier(_calque(font.glyphs["germandbls"], master_id))
    p = _calque(font.glyphs["p"], master_id)
    ps = L.paths(s)[_exterieur(s)]
    pp = L.paths(p)[_exterieur(p)]
    N = len(ps.nodes)
    # le bas du fut du germandbls : les deux noeuds sur la ligne de base dont
    # un voisin est en haut du fut. La panse basse a aussi un noeud droit a
    # y < 0, son bout, mais ses voisins restent bas.
    m_h = (m.xHeight or 496) * 0.6
    bas = [i for i, n in enumerate(ps.nodes)
           if n.type == "line" and n.position.y <= 1.0
           and max(ps.nodes[(i - 1) % N].position.y,
                   ps.nodes[(i + 1) % N].position.y) > m_h]
    if len(bas) != 2 or (bas[1] - bas[0]) % N != 1:
        raise ValueError(f"beta {m.name} : le fut du germandbls n'a pas deux "
                         f"noeuds bas consecutifs ({bas})")
    g_i, d_i = bas                               # gauche puis droit
    if ps.nodes[g_i].position.x > ps.nodes[d_i].position.x:
        raise ValueError(f"beta {m.name} : ordre des noeuds du fut inattendu")
    # la profondeur du p : ses deux noeuds les plus bas
    pbas = sorted((n for n in pp.nodes if n.type != "offcurve"),
                  key=lambda n: n.position.y)[:2]
    pbas.sort(key=lambda n: n.position.x)
    yg, yd = pbas[0].position.y, pbas[1].position.y
    if min(yg, yd) > -100:
        raise ValueError(f"beta {m.name} : le p ne descend pas ({yg}, {yd})")
    # prolonger chaque bord du fut le long de lui-meme
    ag = _pts(ps)[(g_i - 1) % N]                 # le bord gauche monte avant
    ad = _pts(ps)[(d_i + 1) % N]                 # le bord droit monte apres
    xg, _ = _vers(ag, _pts(ps)[g_i], yg)
    xd, _ = _vers(_pts(ps)[d_i], ad, yd)
    _poser(ps, g_i, xg, yg)
    _poser(ps, d_i, xd, yd)
    return s, (yg, yd)


# ------------------------------------------------------------------ fleche

def mesures_fleche(font, master_id):
    """Les mesures du `minus` et du `greater`, redressees en italique.

    En italique les operateurs sont les romains penches autour de l'axe des
    operateurs (le centre du minus) : on redresse autour de ce centre, on
    construit droit, on repenche.
    """
    m = next(m for m in font.masters if m.id == master_id)
    k = _penche(m)
    mi = _pts(L.paths(_calque(font.glyphs["minus"], master_id))[0])
    ys = sorted({round(y, 3) for _, y in mi})
    if len(ys) != 2:
        raise ValueError(f"fleche {m.name} : le minus n'est pas une barre")
    yc = (ys[0] + ys[1]) / 2
    droit = lambda pts: [(x - (y - yc) * k, y) for x, y in pts]
    mi = droit(mi)
    gr_lay = _calque(font.glyphs["greater"], master_id)
    gr = droit(_pts(L.paths(gr_lay)[0]))
    if len(gr) != 7:
        raise ValueError(f"fleche {m.name} : le greater n'a plus ses 7 noeuds")
    xt = max(x for x, _ in gr)
    bout = sorted(y for x, y in gr if abs(x - xt) < 2.0)
    xb = min(x for x, _ in gr)
    dos = sorted(y for x, y in gr if abs(x - xb) < 2.0)
    if len(bout) != 2 or len(dos) != 4:
        raise ValueError(f"fleche {m.name} : le greater n'a pas un bout plat "
                         "et un dos droit")
    f_bout = bout[1] - bout[0]
    v_dos = dos[3] - dos[2]
    angle = math.degrees(math.atan2(dos[3] - bout[1], xt - xb))
    trait = v_dos * math.cos(math.radians(angle))
    return {
        "yc": yc, "k": k,
        "hampe": ys[1] - ys[0],
        "x0": min(x for x, _ in mi),
        "longueur_minus": max(x for x, _ in mi) - min(x for x, _ in mi),
        "approche_droite": gr_lay.width - xt,
        "angle_greater": angle, "trait": trait, "bout": f_bout,
        "demi_hauteur": dos[3] - yc,
    }


def contour_fleche(M, angle):
    """Le contour de la fleche, sens trigonometrique. Rend (pts, chasse, h)."""
    th = math.radians(angle)
    t, yc = M["hampe"], M["yc"]
    v = t / math.cos(th)                         # epaisseur verticale d'un bras
    f = M["bout"]                                # le bout plat du greater
    h = max(TETE * M["demi_hauteur"], v + t / 2 + BRAS * t)
    x0 = M["x0"]
    xt = x0 + LONGUEUR * M["longueur_minus"]
    tg = math.tan(th)
    xb = xt - (h - f / 2) / tg
    xj = xt - (v + t / 2 - f / 2) / tg
    if not (x0 < xb < xj < xt):
        raise ValueError(f"fleche : tete impossible (x0 {x0:.0f}, dos {xb:.0f}, "
                         f"jonction {xj:.0f}, bout {xt:.0f})")
    pts = [(x0, yc - t / 2), (xj, yc - t / 2), (xb, yc - h + v), (xb, yc - h),
           (xt, yc - f / 2), (xt, yc + f / 2), (xb, yc + h), (xb, yc + h - v),
           (xj, yc + t / 2), (x0, yc + t / 2)]
    if _aire(pts) <= 0:
        raise ValueError("fleche : contour dans le mauvais sens")
    k = M["k"]
    pts = [(x + (y - yc) * k, y) for x, y in pts]
    chasse = round(xt + M["approche_droite"])
    return pts, chasse, h


def calque_fleche(font, master_id, variante):
    M = mesures_fleche(font, master_id)
    pts, chasse, h = contour_fleche(M, VARIANTES_FLECHE[variante])
    M = dict(M, tete=h)
    lay = GSLayer()
    lay.layerId = lay.associatedMasterId = master_id
    lay.width = chasse
    lay.shapes.append(_chemin(pts))
    return lay, M


# --------------------------------------------------------------- exposants

def regle_ordinal(font, master_id, base="o", ordinal="ordmasculine"):
    """La regle de l'ordinal d'Atkinson, mesuree sur le couple o / ordmasculine.

    L'ordinal est la base prise au point d de l'axe, reduite de s et deplacee
    de (u, w). L'interpolation est lineaire entre deux masters, donc pour un
    couple (A, B) le modele Q = s A + (s t) (B - A) + (u, w) est LINEAIRE en
    (s, s t, u, w) : moindres carres exacts, sans balayage. On garde le couple
    dont le t tombe dans son intervalle, ou le couple d'extrapolation.

    Rend un dict : d, s, u, w, rms, et le supplement de chasse de l'ordinal.
    """
    lay_o = _calque(font.glyphs[ordinal], master_id)
    Q = np.array([pt for p in L.paths(lay_o) for pt in _pts(p)])
    ax = sorted((mm.axes[0], mm.id) for mm in font.masters)
    meilleur = None
    for i in range(len(ax) - 1):
        (da, ida), (db, idb) = ax[i], ax[i + 1]
        A, _, _ = lot3.formes(font, base, ida)
        B, _, _ = lot3.formes(font, base, idb)
        A = np.array([pt for c in A for pt in c])
        B = np.array([pt for c in B for pt in c])
        if A.shape != Q.shape or B.shape != Q.shape:
            raise ValueError(f"{base} et {ordinal} n'ont pas la meme topologie")
        n = len(A)
        D = B - A
        X = np.zeros((2 * n, 4))
        X[:n, 0], X[n:, 0] = A[:, 0], A[:, 1]
        X[:n, 1], X[n:, 1] = D[:, 0], D[:, 1]
        X[:n, 2] = 1.0
        X[n:, 3] = 1.0
        y = np.r_[Q[:, 0], Q[:, 1]]
        sol, *_ = np.linalg.lstsq(X, y, rcond=None)
        s, st, u, w = sol
        t = st / s
        rms = float(np.sqrt(np.mean((X @ sol - y) ** 2)))
        dedans = 0.0 <= t <= 1.0
        bord = (i == 0 and t < 0) or (i == len(ax) - 2 and t > 1)
        if dedans or bord:
            cand = (rms, da + t * (db - da), s, u, w)
            if meilleur is None or cand[0] < meilleur[0]:
                meilleur = cand
    if meilleur is None:
        raise ValueError(f"regle de {ordinal} introuvable")
    rms, d, s, u, w = meilleur
    lb = _calque(font.glyphs[base], master_id).width
    supplement = lay_o.width - s * lb
    return {"d": d, "s": s, "u": u, "w": w, "rms": rms,
            "supplement": supplement}


def calque_exposant(font, master_id, base, regle):
    d = lot3.plafonner(font, base, master_id, master_id, regle["d"])
    ctrs, types, closed, w, _anc, _t = lot3.interpoler(font, base, d, master_id)
    s, u, v = regle["s"], regle["u"], regle["w"]
    lay = GSLayer()
    lay.layerId = lay.associatedMasterId = master_id
    lay.width = round(s * w + regle["supplement"])
    for pts, ty, cl in zip(ctrs, types, closed):
        p = GSPath()
        p.closed = cl
        for (x, y), (kind, smooth) in zip(pts, ty):
            n = GSNode((round(s * x + u, 1), round(s * y + v, 1)), kind)
            n.smooth = smooth
            p.nodes.append(n)
        lay.shapes.append(p)
    return lay, d


# -------------------------------------------------------------- appliquer

def renvoyer(font, log=None):
    """Ajoute les codes de `RENVOIS` aux glyphes existants."""
    portes = {u.upper() for g in font.glyphs for u in (g.unicodes or [])}
    for nom, codes in RENVOIS.items():
        g = font.glyphs[nom]
        if g is None:
            raise ValueError(f"{nom} absent de la source")
        for c in codes:
            if c in portes:
                raise ValueError(f"U+{c} est deja porte par un glyphe : la police "
                                 "de base a change, et ce module ne l'ecrase pas")
        g.unicodes = list(g.unicodes) + list(codes)
    if log is not None:
        log.append(("renvois", ", ".join(f"{n} + U+{' U+'.join(c)}"
                                         for n, c in RENVOIS.items())))


def calques(font, variante=None, alpha=None):
    """Les calques des cinq glyphes neufs, par master. Rend (dict, journal)."""
    variante = variante or VARIANTE_FLECHE
    if variante not in VARIANTES_FLECHE:
        raise ValueError(f"variante de fleche inconnue : {variante}")
    out = {n: {} for n in NEUFS}
    jrn = {}
    for m in font.masters:
        a, _ = calque_alpha(font, m.id, alpha)
        b, yb = calque_beta(font, m.id)
        fl, M = calque_fleche(font, m.id, variante)
        R = regle_ordinal(font, m.id)
        e, de = calque_exposant(font, m.id, "e", R)
        r, dr = calque_exposant(font, m.id, "r", R)
        for n, lay in ((ALPHA, a), (BETA, b), (FLECHE, fl), (EXP_E, e),
                       (EXP_R, r)):
            out[n][m.id] = lay
    # un variable exige la meme structure dans tous les masters
    for n in NEUFS:
        formes = {tuple((len(p.nodes), tuple(nd.type for nd in p.nodes))
                        for p in L.paths(lay)) for lay in out[n].values()}
        if len(formes) != 1:
            raise ValueError(f"{n} : structure differente selon les masters, "
                             "le variable ne s'interpolerait pas")
        jrn[m.name] = {"beta_y": yb, "fleche": M, "regle": R,
                       "d_e": de, "d_r": dr}
    return out, jrn


def appliquer(font, log=None, variante=None, alpha=None):
    """Renvois, puis les cinq glyphes neufs, dans tous les masters."""
    for nom in NEUFS:
        if font.glyphs[nom] is not None:
            raise ValueError(f"{nom} existe deja dans la source : la police de "
                             "base a change, et ce module ne l'ecrase pas")
    portes = {u.upper() for g in font.glyphs for u in (g.unicodes or [])}
    for nom, c in UNICODES.items():
        if c in portes:
            raise ValueError(f"U+{c} ({nom}) est deja porte par un glyphe")
    renvoyer(font, log)
    par, jrn = calques(font, variante, alpha)
    for nom in NEUFS:
        g = GSGlyph(nom)
        g.unicodes = [UNICODES[nom]]
        g.export = True
        g.leftKerningGroup, g.rightKerningGroup = GROUPES[nom]
        for m in font.masters:
            g.layers.append(par[nom][m.id])
        font.glyphs.append(g)
    if log is not None:
        log.append((f"complements, fleche {variante or VARIANTE_FLECHE}",
                    ", ".join(f"{mn} regle s {j['regle']['s']:.4f} d "
                              f"{j['regle']['d']:.0f} rms {j['regle']['rms']:.2f}"
                              for mn, j in jrn.items())))
    return par, jrn
