#!/usr/bin/env python3
"""
Temoin, etape 2, lot 2 : le systeme de coupes.

Une seule loi geometrique, appliquee a toutes les terminaisons libres qui ne
portent pas d'alignement (ligne de base, hauteur d'x, hauteur de capitale,
ligne d'ascendante, ligne de descendante) :

    la droite de coupe, au lieu d'etre perpendiculaire au trait ou alignee
    sur la grille, tourne d'un angle theta constant, toujours dans le meme
    sens ; le coin qui avance reste fixe, l'autre recule.

Deux consequences voulues :
  - la chasse et les extremes du glyphe ne bougent pas, donc l'approche et
    l'espacement ne sont pas a refaire ;
  - la coupe s'allonge de 1/cos(theta) seulement, le trait ne maigrit pas.

Un seul reglage supplementaire, le roulage `roll` (0 a 1), qui arrondit la
coupe : 0 donne une coupe franche, 1 un bout entierement roule. Les accents
sont le cas roll = 1. Le point extreme d'origine est conserve dans les deux
cas, ce qui protege l'espace entre l'accent et la lettre.

Ce module ne connait aucun glyphe : il ne fait que de la geometrie sur des
contours Glyphs. Le choix des terminaisons est dans lot2.py.
"""

import math
import numpy as np

from glyphsLib.classes import GSPath, GSNode


# --------------------------------------------------------------- vecteurs

def V(p):
    return np.asarray(p, float)


def unit(v):
    n = math.hypot(float(v[0]), float(v[1]))
    if n < 1e-9:
        raise ValueError("vecteur nul")
    return np.array([v[0] / n, v[1] / n])


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])


def perp(v):
    return np.array([-v[1], v[0]])


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


# --------------------------------------------------- segments <-> contour

def _pt(node):
    return (float(node.position.x), float(node.position.y))


def to_segs(path):
    """Contour ferme -> liste de segments, avec les drapeaux `smooth`.

    Le premier segment part du dernier noeud on-curve de la liste, ce qui
    reproduit la lecture de Glyphs. La rotation induite est identique dans
    tous les masters tant qu'on applique la meme transformation partout.
    """
    nodes = list(path.nodes)
    onc = [i for i, n in enumerate(nodes) if n.type != "offcurve"]
    if not onc:
        return []
    start = onc[-1]
    order = nodes[start:] + nodes[:start]
    segs, pending, prev = [], [], _pt(order[0])
    for n in order[1:] + [order[0]]:
        if n.type == "offcurve":
            pending.append(_pt(n))
            continue
        segs.append({
            "kind": "line" if n.type == "line" else "curve",
            "p0": prev,
            "c": pending,
            "p3": _pt(n),
            "smooth": bool(n.smooth),
        })
        pending, prev = [], _pt(n)
    return segs


def from_segs(segs):
    p = GSPath()
    p.closed = True
    for s in segs:
        for c in s["c"]:
            p.nodes.append(GSNode((round(float(c[0]), 1), round(float(c[1]), 1)),
                                  "offcurve"))
        n = GSNode((round(float(s["p3"][0]), 1), round(float(s["p3"][1]), 1)),
                   "curve" if s["kind"] == "curve" else "line")
        n.smooth = s["smooth"]
        p.nodes.append(n)
    return p


def area(segs):
    pts = [s["p3"] for s in segs]
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return a / 2.0


# ------------------------------------------------------------- geometrie

def seg_pts(s):
    """Les 4 points de controle, un segment droit etant un Bezier degenere."""
    p0, p3 = V(s["p0"]), V(s["p3"])
    if s["kind"] == "line" or len(s["c"]) != 2:
        return p0, p0 + (p3 - p0) / 3.0, p0 + 2 * (p3 - p0) / 3.0, p3
    return p0, V(s["c"][0]), V(s["c"][1]), p3


def bez(s, t):
    p0, c1, c2, p3 = seg_pts(s)
    m = 1.0 - t
    return (m ** 3) * p0 + 3 * m * m * t * c1 + 3 * m * t * t * c2 + (t ** 3) * p3


def tangent_out(s):
    """Direction de parcours a l'arrivee sur p3."""
    p0, c1, c2, p3 = seg_pts(s)
    for a in (c2, c1, p0):
        if np.hypot(*(p3 - a)) > 1e-6:
            return unit(p3 - a)
    raise ValueError("segment degenere")


def tangent_in(s):
    """Direction de parcours au depart de p0."""
    p0, c1, c2, p3 = seg_pts(s)
    for a in (c1, c2, p3):
        if np.hypot(*(a - p0)) > 1e-6:
            return unit(a - p0)
    raise ValueError("segment degenere")


def split_left(s, t):
    """Sous-segment [0, t]."""
    p0, c1, c2, p3 = seg_pts(s)
    a1 = p0 + t * (c1 - p0)
    a2 = p0 + 2 * t * (c1 - p0) + t * t * (c2 - 2 * c1 + p0)
    a3 = bez(s, t)
    if s["kind"] == "line":
        return {"kind": "line", "p0": tuple(p0), "c": [], "p3": tuple(a3),
                "smooth": s["smooth"]}
    return {"kind": "curve", "p0": tuple(p0), "c": [tuple(a1), tuple(a2)],
            "p3": tuple(a3), "smooth": s["smooth"]}


def split_right(s, t):
    """Sous-segment [t, 1]."""
    p0, c1, c2, p3 = seg_pts(s)
    u = 1.0 - t
    b2 = p3 + u * (c2 - p3)
    b1 = p3 + 2 * u * (c2 - p3) + u * u * (c1 - 2 * c2 + p3)
    b0 = bez(s, t)
    if s["kind"] == "line":
        return {"kind": "line", "p0": tuple(b0), "c": [], "p3": tuple(p3),
                "smooth": s["smooth"]}
    return {"kind": "curve", "p0": tuple(b0), "c": [tuple(b1), tuple(b2)],
            "p3": tuple(p3), "smooth": s["smooth"]}


def _roots(coef, near):
    """Racines reelles de a3 t^3 + a2 t^2 + a1 t + a0, la plus proche de `near`."""
    r = np.roots(coef) if any(abs(c) > 1e-12 for c in coef[:-1]) else []
    cand = [float(x.real) for x in np.atleast_1d(r)
            if abs(np.imag(x)) < 1e-6 and -0.35 <= x.real <= 1.35]
    if not cand:
        return None
    return min(cand, key=lambda t: abs(t - near))


def hit_line(s, F, u, near):
    """Parametre t ou le segment coupe la droite {F + k u}."""
    p0, c1, c2, p3 = seg_pts(s)
    a3 = -p0 + 3 * c1 - 3 * c2 + p3
    a2 = 3 * p0 - 6 * c1 + 3 * c2
    a1 = -3 * p0 + 3 * c1
    a0 = p0 - V(F)
    return _roots([cross(a3, u), cross(a2, u), cross(a1, u), cross(a0, u)], near)


def hit_plane(s, m, value, near):
    """Parametre t ou dot(point, m) vaut `value`."""
    p0, c1, c2, p3 = seg_pts(s)
    a3 = -p0 + 3 * c1 - 3 * c2 + p3
    a2 = 3 * p0 - 6 * c1 + 3 * c2
    a1 = -3 * p0 + 3 * c1
    a0 = p0
    return _roots([np.dot(a3, m), np.dot(a2, m), np.dot(a1, m),
                   np.dot(a0, m) - value], near)


def extreme(s, m, n=48):
    return max(float(np.dot(bez(s, i / n), m)) for i in range(n + 1))


# ------------------------------------------------------------ l'operation

def outward(segs, i):
    """Direction sortante du trait a la terminaison `i`."""
    a = tangent_out(segs[i - 1])
    b = tangent_in(segs[(i + 1) % len(segs)])
    return unit(a - b)


def recule(s, dist, depuis_fin):
    """Parametre du point situe a `dist` du bout du segment, en ligne droite."""
    if s["kind"] == "line":
        L = float(np.hypot(*(V(s["p3"]) - V(s["p0"]))))
        t = min(dist / L, 0.999) if L > 1e-9 else 0.5
        return 1.0 - t if depuis_fin else t
    bout = V(s["p3"] if depuis_fin else s["p0"])
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2.0
        t = 1.0 - mid if depuis_fin else mid
        if float(np.hypot(*(bez(s, t) - bout))) < dist:
            lo = mid
        else:
            hi = mid
    m = (lo + hi) / 2.0
    return 1.0 - m if depuis_fin else m


def coupe(segs, i, theta_deg, sense=1, roll=0.0):
    """Applique la loi a la terminaison `i` (un segment droit).

    La reference d'angle est la coupe existante, pas la perpendiculaire au
    trait. C'est un choix, et il se defend : les orientations de coupe
    d'Atkinson encodent des decisions de lisibilite (alignement sur la grille
    pour les barres, perpendicularite pour le S). On les fait tourner, on ne
    les refait pas. La modification reste bornee, ce qui est aussi ce qui
    garde le risque a zero.

    theta_deg  rotation de la droite de coupe
    sense      +1 anti-horaire, -1 horaire ; un seul sens pour toute la police
    roll       0 coupe franche, 1 bout entierement roule

    Le pivot n'est pas un choix libre : des deux coins, on garde celui qui
    fait rentrer l'autre dans la lettre. Le glyphe ne peut donc que maigrir
    localement, jamais s'etendre : chasse et approches restent valables.
    """
    segs = [dict(s, c=list(s["c"])) for s in segs]
    n = len(segs)
    ib, ia = (i - 1) % n, (i + 1) % n
    P, Q = V(segs[i]["p0"]), V(segs[i]["p3"])
    d = outward(segs, i)

    # normale sortante de la coupe d'origine : reference d'extreme
    m = perp(unit(Q - P))
    if np.dot(m, d) < 0:
        m = -m
    e0 = max(float(np.dot(P, m)), float(np.dot(Q, m)))

    # Un bout entierement roule n'a plus d'angle : le faire tourner avant de
    # le rouler ne ferait que casser la symetrie du circonflexe. Les accents
    # recoivent donc le roulage, pas l'angle.
    if roll >= 0.999:
        theta_deg = 0.0

    th = math.radians(theta_deg) * sense
    v = Q - P
    w = rot(v, th) - v                     # deplacement de Q si le pivot est P
    pivot_P = float(np.dot(w, d)) < 0

    if theta_deg != 0:
        if pivot_P:
            u = unit(rot(v, th))
            t = hit_line(segs[ia], P, u, 0.0)
            if t is None:
                raise ValueError(f"coupe {i} : pas d'intersection cote sortie")
            segs[ia] = split_right(segs[ia], t)
            Q = V(segs[ia]["p0"])
        else:
            u = unit(rot(-v, th))
            t = hit_line(segs[ib], Q, u, 1.0)
            if t is None:
                raise ValueError(f"coupe {i} : pas d'intersection cote entree")
            segs[ib] = split_left(segs[ib], t)
            P = V(segs[ib]["p3"])
        segs[i] = {"kind": "line", "p0": tuple(P), "c": [], "p3": tuple(Q),
                   "smooth": False}

    if roll <= 0:
        return segs

    # ---- roulage : on ne roule qu'un coin sur deux, le coin obtus.
    # La pointe est conservee telle quelle. C'est la demande de Nicolas sur
    # l'accent aigu (« garder la pointe ») et sur la virgule (« un arrondi
    # sur la partie en bas a droite ») : dans les deux cas le coin vise est
    # l'obtus, et c'est aussi le seul choix qui laisse le point extreme
    # exactement ou il etait, puisque la pointe ne bouge pas.
    u_cut = unit(Q - P)
    ang_P = ecart(u_cut, -tangent_out(segs[ib]))
    ang_Q = ecart(-u_cut, tangent_in(segs[ia]))
    s = roll * float(np.hypot(*(Q - P)))
    # Garde-fou : le roulage ne peut pas manger plus d'un huitieme du contour.
    # Sans lui, la breve — dont les flancs sont courts et courbes — perdait un
    # tiers de sa surface. Le recul est reduit jusqu'a rentrer dans la limite.
    a0 = abs(area(segs))
    for _ in range(6):
        essai = _rouler(segs, i, ib, ia, P, Q, u_cut, s, ang_P <= ang_Q)
        if a0 < 1e-9 or abs(abs(area(essai)) - a0) <= 0.125 * a0:
            return essai
        s *= 0.6
    return essai


def _prolonge(seg, cle, point):
    """Deplace un bout de segment droit sans changer sa direction.

    Refuse les courbes : prolonger un Bezier au-dela de son domaine se fait,
    mais la forme obtenue n'est plus celle qu'a dessinee le dessinateur.
    """
    if seg["kind"] != "line":
        raise ValueError("flanc courbe, prolongement refuse")
    return dict(seg, **{cle: tuple(V(point))})


def allonge(segs, i, dist):
    """ALLONGE un trait en poussant sa terminaison, sans la tourner.

    **La cinquieme operation du projet, et la premiere qui ne tourne rien.**
    Ecrite au trente-et-unieme tour pour la barre montante du t, dont Nicolas a
    demande qu'elle atteigne le niveau des autres lettres hautes. Les quatre
    autres — `coupe`, `coupe_sortante`, `bascule`, `pointe` — tournent un bout
    ou le mettent en pointe, et aucune n'allonge.

    POURQUOI AUCUNE NE POUVAIT LE FAIRE, ET C'EST MESURE. Une `sortante` fait
    sortir un coin en tournant le bout : son levier est la largeur du bout, donc
    son effet depend de la graisse. Sur le sommet du fut du t, ce bout fait 54
    unites en ExtraLight et 165 a l'ExtraBold. La bascule poussee a 45 degres,
    borne de l'outil, monte le sommet a 647 en ExtraLight et 696 au Bold, pour
    une cible a 690 : elle ne peut pas y arriver dans les masters clairs, et
    l'ecart de 55 unites qu'elle creerait sur l'axe ferait changer la lettre de
    proportion avec la graisse, ce qu'aucun autre glyphe du projet ne fait.

    CE QUE FAIT CETTE FONCTION. La droite du bout est translatee de `dist` le
    long de la normale sortante, puis les deux flancs voisins sont PROLONGES
    jusqu'a cette droite, chacun dans sa propre direction. Le bout garde donc
    son orientation et le trait garde sa largeur, ce qui est le geste demande :
    on pousse la terminaison, on ne la couche pas. Une translation naive des
    deux coins le long de la normale ferait autre chose des que les flancs sont
    obliques — elle deplacerait le trait au lieu de l'allonger.

    REFUSE LES FLANCS COURBES, par `_prolonge`, et c'est un refus et non une
    approximation : prolonger un Bezier au-dela de son domaine rend une forme
    que le dessinateur n'a pas dessinee. Sur le t les deux flancs sont des
    lignes parfaitement verticales de la hauteur d'x au sommet, donc le geste y
    est exact et non approche.

    `dist` positif allonge. Un `dist` negatif raccourcit, et rien ne l'interdit
    ici, mais aucune entree ne s'en sert : le raccourcissement d'un trait change
    la hauteur d'une lettre sans qu'un alignement le rattrape.
    """
    n = len(segs)
    s = segs[i]
    if s["kind"] != "line":
        raise ValueError("le bout a allonger n'est pas un segment droit")
    ia, ib = (i - 1) % n, (i + 1) % n
    u = outward(segs, i)
    P, Q = V(s["p0"]), V(s["p3"])
    # La droite du bout, translatee. On garde sa direction, donc son vecteur
    # directeur ne change pas ; seul un point de passage se deplace.
    P2, dirn = P + float(dist) * V(u), unit(Q - P)
    # Chaque flanc est prolonge dans SA direction jusqu'a la nouvelle droite.
    # C'est ce qui garde la largeur du trait quand les flancs sont obliques.
    av, ap = segs[ia], segs[ib]
    if av["kind"] != "line" or ap["kind"] != "line":
        raise ValueError("flanc voisin courbe, allongement refuse")
    ua = unit(V(av["p3"]) - V(av["p0"]))
    ub = unit(V(ap["p3"]) - V(ap["p0"]))
    A = inter_droites(P2, dirn, V(av["p0"]), ua)
    B = inter_droites(P2, dirn, V(ap["p3"]), ub)
    if A is None or B is None:
        raise ValueError("flanc parallele au bout, allongement impossible")
    out = list(segs)
    out[ia] = _prolonge(av, "p3", A)
    out[i] = dict(s, p0=tuple(A), p3=tuple(B))
    out[ib] = _prolonge(ap, "p0", B)
    return out


def pentes_flancs(segs, y_coupe):
    """Les pentes dx/dy des segments qui traversent `y_coupe`, dans l'ordre.

    Lue a part de `descendre_crochet` pour qu'un controle puisse mesurer le
    meme fait sans rejouer le geste.
    """
    out = []
    for i, s in enumerate(segs):
        if (s["p0"][1] - y_coupe) * (s["p3"][1] - y_coupe) >= 0:
            continue
        ddy = s["p3"][1] - s["p0"][1]
        out.append((i, (s["p3"][0] - s["p0"][0]) / ddy))
    return out


def descendre_crochet(segs, dist, y_coupe):
    """DESCEND tout ce qui est sous `y_coupe`, en allongeant les deux flancs.

    **La sixieme operation du projet, et la seconde qui ne tourne rien**, apres
    `allonge`. Ecrite au soixantieme tour pour la queue du j, point ouvert 105 :
    le coin gauche du crochet, a y = -42, touche le pied droit du A qui plonge
    a -44 depuis le lot 4b, et le projet paie ce contact depuis le vingt-
    neuvieme tour par un crenage de +106 unites que Nicolas juge trop grand en
    texte sur `Ajouter`.

    POURQUOI AUCUNE OPERATION EXISTANTE NE POUVAIT LE FAIRE, ET C'EST MESURE.
    `allonge` pousse un bout le long de sa normale sortante et PROLONGE ses
    deux flancs voisins : elle refuse un flanc courbe, et le flanc qui suit le
    bout de la queue du j est une courbe dans les huit masters. Elle ne
    servirait a rien de toute facon, parce que **le bout du bas n'est pas ce
    qui touche** : le pousser laisserait le coin gauche exactement ou il est.
    La translation verticale des deux coins du bout n'est exacte que sur des
    flancs verticaux, et le flanc gauche du crochet est oblique partout.

    CE QUE FAIT CETTE FONCTION. Tout point de controle sous `y_coupe` est
    translate d'un vecteur, et les deux segments qui TRAVERSENT `y_coupe` -- les
    deux flancs du fut -- voient leur extremite basse suivre. Le crochet garde
    donc sa forme exacte, aucune courbe n'est deformee, et le fut s'allonge.

    LE VECTEUR SUIT LA PENTE DES FLANCS, ET C'EST CE QUI REND LE GESTE EXACT.
    Une translation verticale ferait TOURNER un flanc oblique : en italique les
    deux flancs du fut penchent de 11,93 a 12,07 degres, et une descente de 15
    unites appliquee a la verticale les ramenerait a 11,64. Le vecteur vaut
    donc `(-pente * dist, -dist)`, ou `pente` est la moyenne des deux flancs.

        LE PRIX EST MESURE ET IL N'EST PAS NUL. Les deux flancs n'ont pas
        exactement la meme pente -- 0,21387 et 0,21553 en ExtraLight Italic,
        soit 0,00166 d'ecart -- donc une translation unique ne peut pas les
        prolonger tous les deux a l'identique. A 15 unites de descente, chacun
        tourne de 0,0007 degre. Au romain les deux pentes valent zero et le
        geste est exact. `pentes_flancs` rend de quoi le remesurer.

    REFUSE TOUTE STRUCTURE AUTRE, et c'est un refus et non une approximation :
    exactement deux segments doivent traverser `y_coupe`, et tous deux doivent
    etre des lignes. Une structure a trois traversees ou a flanc courbe rendrait
    une forme que le dessinateur n'a pas dessinee.

    `dist` positif descend. Un `dist` negatif remonte, et rien ne l'interdit,
    mais aucune entree ne s'en sert.
    """
    flancs = pentes_flancs(segs, y_coupe)
    if len(flancs) != 2:
        raise ValueError(f"{len(flancs)} segment(s) traversent la coupe a "
                         f"y = {y_coupe}, il en faut exactement deux")
    for i, _p in flancs:
        if segs[i]["kind"] != "line":
            raise ValueError(f"le flanc {i} est courbe, descente refusee")
    pente = sum(p for _i, p in flancs) / 2.0
    dx, dy = -pente * float(dist), -float(dist)

    def bouge(p):
        return (p[0] + dx, p[1] + dy) if p[1] <= y_coupe else (p[0], p[1])

    return [dict(s, p0=bouge(s["p0"]), p3=bouge(s["p3"]),
                 c=[bouge(c) for c in s["c"]]) for s in segs]


def coupe_sortante(segs, i, theta_deg, sense):
    """Fait sortir un coin de son alignement, au lieu de l'y faire rentrer.

    `coupe` choisit toujours le pivot qui fait rentrer l'autre coin : le glyphe
    ne peut alors que maigrir. C'est ce qui garde le risque a zero dans le
    texte, et c'est justement ce qu'il ne faut pas ici.

    Le coin sortant coulisse le long du flanc voisin prolonge. La lettre gagne
    donc de la matiere, et son depassement se mesure.

    La matiere n'est pas gagnee en hauteur seulement : le coin suit la direction
    du flanc, pas la verticale. Sur un flanc vertical la boite ne s'elargit pas
    d'une unite ; sur un bras diagonal peu pentu le coin part surtout de cote.
    Mesure au Bold, sortante de 32 unites sur la ligne de capitale : Y +54
    unites de largeur de boite, V +29, W +20, K +16, H I N U +0. La chasse, elle,
    ne bouge dans aucun cas : c'est le blanc de l'approche qui est mange.

    Vient de `lot4.py`, ou elle est nee au troisieme tour. Elle est descendue
    ici au vingt-deuxieme tour, quand le lot 2 en a eu besoin pour la pointe du
    pied du n : `lot4` importe `lot2`, donc `lot2` ne peut pas importer `lot4`.
    Sa place etait de toute facon ici, elle ne connait aucun glyphe. `lot4`
    garde un alias.
    """
    segs = [dict(s, c=list(s["c"])) for s in segs]
    n = len(segs)
    ib, ia = (i - 1) % n, (i + 1) % n
    P, Q = V(segs[i]["p0"]), V(segs[i]["p3"])
    d = outward(segs, i)
    th = math.radians(theta_deg) * sense
    v = Q - P
    w = rot(v, th) - v
    sortie_par_Q = float(np.dot(w, d)) > 0
    if sortie_par_Q:
        u = unit(rot(v, th))
        tn = tangent_in(segs[ia])
        Qn = inter_droites(P, u, Q, tn)
        if Qn is None or float(np.dot(V(Qn) - Q, d)) <= 0:
            raise ValueError("le coin ne sort pas")
        segs[ia] = _prolonge(segs[ia], "p0", Qn)
        segs[i] = {"kind": "line", "p0": tuple(P), "c": [], "p3": tuple(Qn),
                   "smooth": False}
    else:
        u = unit(rot(-v, th))
        tn = tangent_out(segs[ib])
        Pn = inter_droites(Q, u, P, tn)
        if Pn is None or float(np.dot(V(Pn) - P, d)) <= 0:
            raise ValueError("le coin ne sort pas")
        segs[ib] = _prolonge(segs[ib], "p3", Pn)
        segs[i] = {"kind": "line", "p0": tuple(Pn), "c": [], "p3": tuple(Q),
                   "smooth": False}
    return segs


def bascule(segs, i, theta_deg, sense):
    """La coupe tourne autour du MILIEU du bout : un coin descend, l'autre monte.

    Troisieme regime de coupe du projet, et il ne se deduit d'aucun des deux
    autres. `coupe` garde le coin qui fait rentrer l'autre, donc la lettre ne
    peut que maigrir ; `coupe_sortante` fait sortir un coin et laisse l'autre
    fixe, donc elle ne peut que grossir. Ici les deux coins bougent en sens
    contraire, et la matiere perdue d'un cote est regagnee de l'autre : l'encre
    ne varie pas de plus de cinq dix-millemes sur les huit mesures du vingtieme
    tour.

    Les deux flancs voisins doivent etre droits : le coin qui sort coulisse le
    long du flanc prolonge, et prolonger un Bezier au-dela de son domaine rend
    une forme que le dessinateur n'a pas dessinee.
    """
    segs = [dict(s, c=list(s["c"])) for s in segs]
    n = len(segs)
    ib, ia = (i - 1) % n, (i + 1) % n
    if segs[ib]["kind"] != "line" or segs[ia]["kind"] != "line":
        raise ValueError("bascule : un flanc voisin est courbe, refuse")
    P, Q = V(segs[i]["p0"]), V(segs[i]["p3"])
    M = (P + Q) / 2.0
    u = rot(unit(Q - P), math.radians(theta_deg) * sense)
    Ab, Aa = V(segs[ib]["p0"]), V(segs[ia]["p3"])
    Pn = inter_droites(M, u, Ab, unit(P - Ab))
    Qn = inter_droites(M, u, Aa, unit(Q - Aa))
    if Pn is None or Qn is None:
        raise ValueError("bascule : flanc parallele a la coupe")
    Pn, Qn = V(Pn), V(Qn)
    segs[ib] = dict(segs[ib], p3=tuple(float(t) for t in Pn), smooth=False)
    segs[ia] = dict(segs[ia], p0=tuple(float(t) for t in Qn), smooth=False)
    segs[i] = {"kind": "line", "p0": tuple(float(t) for t in Pn), "c": [],
               "p3": tuple(float(t) for t in Qn), "smooth": False}
    return segs


def pointe(segs, i, tirage=3.0, saillie=0.0):
    """Effile la terminaison `i` jusqu'a une pointe, sans coupe.

    La coupe droite disparait : le bout devient un crochet qui se termine en
    pointe. Ce n'est pas une rotation poussee a l'extreme — sur la cedille les
    deux flancs sont paralleles, aucune rotation ne les fait se rejoindre. Il
    faut effiler : un des deux flancs est recule et raccorde a la pointe par
    une courbe tangente. `tirage` regle la longueur de l'effilement, en
    multiples de l'epaisseur du bout.

    Le nombre de noeuds ne change pas : le segment droit devient une courbe,
    comme dans le roulage. La topologie reste donc interpolable.
    """
    segs = [dict(s, c=list(s["c"])) for s in segs]
    n = len(segs)
    ib, ia = (i - 1) % n, (i + 1) % n
    P, Q = V(segs[i]["p0"]), V(segs[i]["p3"])
    L = float(np.hypot(*(Q - P)))
    # La pointe part du milieu de l'ancien bout et avance de `saillie` fois
    # l'epaisseur, dans la direction sortante du trait.
    #
    # Sans cette saillie la pointe reste emoussee, et ce n'est pas un defaut de
    # reglage : l'angle du bout vaut 2.atan(demi-epaisseur / recul), et le
    # recul est plafonne par la longueur des flancs. Sur la cedille les flancs
    # font 60 et 90 unites pour un bout de 38 : meme en reculant au maximum on
    # ne descend pas sous 33 degres. Faire avancer la pointe allonge le
    # triangle sans toucher aux flancs.
    # `saillie` est en unites, pas en epaisseurs : proportionnelle a
    # l'epaisseur, elle faisait descendre la virgule de 51 unites en Regular
    # mais de 89 en ExtraBold, et la queue changeait de proportion d'un bout de
    # l'axe a l'autre. En absolu, l'avancee est la meme partout.
    d = outward(segs, i)
    T = (P + Q) / 2.0 + saillie * d

    # les deux flancs reculent et convergent vers T
    sb = min(tirage * L, 0.85 * seg_len(segs[ib]))
    sa = min(tirage * L, 0.85 * seg_len(segs[ia]))
    segs[ib] = split_left(segs[ib], recule(segs[ib], sb, True))
    segs[ia] = split_right(segs[ia], recule(segs[ia], sa, False))
    I, J = V(segs[ib]["p3"]), V(segs[ia]["p0"])
    tI, tJ = tangent_out(segs[ib]), tangent_in(segs[ia])
    dI, dJ = float(np.hypot(*(T - I))), float(np.hypot(*(J - T)))
    uI = unit(T - I) if dI > 1e-9 else tI
    uJ = unit(J - T) if dJ > 1e-9 else tJ

    segs[ib]["smooth"] = True
    entree = {"kind": "curve", "p0": tuple(I),
              "c": [tuple(I + 0.5 * dI * tI), tuple(T - 0.35 * dI * uI)],
              "p3": tuple(T), "smooth": False}
    sortie = {"kind": "curve", "p0": tuple(T),
              "c": [tuple(T + 0.35 * dJ * uJ), tuple(J - 0.5 * dJ * tJ)],
              "p3": tuple(J), "smooth": True}
    return segs[:i] + [entree, sortie] + segs[i + 1:]


def _rouler(segs, i, ib, ia, P, Q, u_cut, s, pointe_en_P):
    segs = [dict(x, c=list(x["c"])) for x in segs]

    if pointe_en_P:                          # la pointe est en P, on roule en Q
        t = recule(segs[ia], min(s, 0.72 * seg_len(segs[ia])), False)
        segs[ia] = split_right(segs[ia], t)
        Q3 = V(segs[ia]["p0"])
        T = inter_droites(P, u_cut, Q3, tangent_in(segs[ia]))
        if T is None:
            T = (P + Q3) / 2.0
        segs[i] = {"kind": "curve", "p0": tuple(P),
                   "c": [tuple(P + (2.0 / 3) * (T - P)),
                         tuple(Q3 + (2.0 / 3) * (T - Q3))],
                   "p3": tuple(Q3), "smooth": True}
    else:                                    # la pointe est en Q, on roule en P
        t = recule(segs[ib], min(s, 0.72 * seg_len(segs[ib])), True)
        segs[ib] = split_left(segs[ib], t)
        P3 = V(segs[ib]["p3"])
        T = inter_droites(P3, tangent_out(segs[ib]), Q, u_cut)
        if T is None:
            T = (P3 + Q) / 2.0
        segs[ib]["smooth"] = True
        segs[i] = {"kind": "curve", "p0": tuple(P3),
                   "c": [tuple(P3 + (2.0 / 3) * (T - P3)),
                         tuple(Q + (2.0 / 3) * (T - Q))],
                   "p3": tuple(Q), "smooth": False}
    return segs


def ecart(a, b):
    """Angle entre deux directions, en degres."""
    return math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(a, b))))))


def inter_droites(P, u, Q, v):
    """Intersection des droites {P + a.u} et {Q + b.v}."""
    den = cross(u, v)
    if abs(den) < 1e-9:
        return None
    return V(P) + (cross(V(Q) - V(P), v) / den) * V(u)


def seg_len(s, n=24):
    p = [bez(s, k / n) for k in range(n + 1)]
    return sum(float(np.hypot(*(p[k + 1] - p[k]))) for k in range(n))


# ----------------------------------------------------------- utilitaires

def find_line(segs, key):
    """Indice du segment droit qui maximise `key(segment)`."""
    cand = [(k, s) for k, s in enumerate(segs) if s["kind"] == "line"]
    if not cand:
        raise ValueError("aucun segment droit")
    return max(cand, key=lambda ks: key(ks[1]))[0]


def mid(s):
    return ((s["p0"][0] + s["p3"][0]) / 2.0, (s["p0"][1] + s["p3"][1]) / 2.0)


def length(s):
    return math.hypot(s["p3"][0] - s["p0"][0], s["p3"][1] - s["p0"][1])
