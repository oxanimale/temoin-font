#!/usr/bin/env python3
"""LES ETOILES, ★ U+2605 et ☆ U+2606, soixante-douzieme tour.

LA DEMANDE. Nicolas : ajouter les etoiles. Elles manquent a la police de base,
et le site les emploie dans l'indicateur de difficulte, ou le navigateur les
prend donc dans une autre police. `temoin.css` contourne leur absence par des
ronds dessines en CSS (`.difficulte`), que ce tour ne touche pas.

CE QUI EST ARRETE AU CADRAGE, par Nicolas ou annonce sans question :

    forme            la variante "large", choisie sur
                     `planche-tour72-etoiles.png` parmi trois (VARIANTES)
    trait de ☆       celui du master par defaut, a toutes les graisses
    italique         droites dans les deux sources : une note ne penche pas
    chasse           la meme pour les deux, sinon une note ne s'aligne pas
    crenage          aucun

LE TRAIT NE SUIT PAS LA GRAISSE, et c'est la planche qui l'a decide. Annonce
au cadrage sans question, le trait du losange de chaque master bouchait le
creux de ☆ en texte : 30 % de l'etoile au Regular, 9 % au Bold, 6 % a
l'ExtraBold pour la variante retenue, et ☆ se lisait ★ dans une note grasse
a 18 px. Au trait du Regular, le creux tient 30 % a toutes les graisses.
Nicolas a tranche sur la planche qui montrait les deux.

LA GEOMETRIE. Une etoile a cinq branches, pointe en haut, est un polygone a
dix sommets sur deux cercles, R pour les pointes et r = `rapport` x R pour les
creux. Ses dix aretes sont a la MEME distance d du centre, par symetrie : le
polygone est circonscrit a un cercle. Deux consequences, et tout le module
repose sur elles :

    le trait de ☆ est une HOMOTHETIE. Decaler les dix aretes de t vers
    l'interieur rend le meme polygone reduit de (d - t) / d, pointes et creux
    compris. Aucun calcul de decalage, aucune intersection a resoudre.

    l'arrondi d'une pointe est un ARC de rayon rho, tangent aux deux aretes,
    centre sur le sommet de l'etoile reduite de (d - rho) / d. Les creux
    restent vifs. Le contour interieur de ☆ garde le meme centre d'arc, au
    rayon rho - t, et devient vif quand le trait depasse l'arrondi.

LA HAUTEUR. Les deux pointes du bas sur la ligne de base, la pointe du haut a
la hauteur de capitale plus `DEBORD` : une pointe vive parait plus basse qu'une
barre a la meme hauteur, comme le sommet d'un A.

LE TRAIT EST LU SUR LE LOSANGE, jamais ecrit en dur. `lozenge` U+25CA est le
seul symbole de la police de base a trait diagonal evide, donc il porte la
reponse d'Atkinson a la question que pose ☆. Mesure au soixante-douzieme tour,
romain : 53,8 / 75,2 / 116,3 / 124,0 unites de l'ExtraLight a l'ExtraBold,
contre des futs de 56 / 94 / 158 / 170 ; en italique, ou le losange penche,
53,5 / 76,3 / 115,6 / 123,4. Atkinson amincit donc ses diagonales, et
d'autant plus que la graisse monte. Le trait retenu se lit sur le losange du
master par defaut, `Variable Font Origin`, soit 75,2 au romain et 76,3 en
italique : une unite d'ecart entre deux etoiles droites, sous tout seuil de
rendu. Un losange absent ou redessine LEVE, comme `add_narrow_nbspace` leve
sans `thinspace` : un trait par defaut serait un mensonge silencieux.
"""

import math

from glyphsLib.classes import GSGlyph, GSLayer, GSNode, GSPath

#: Les noms que `glyphsLib` connait pour U+2605 et U+2606 : categorie Symbol,
#: noms de production uni2605 et uni2606.
PLEINE, VIDE = "blackStar", "whiteStar"
UNICODES = {PLEINE: "2605", VIDE: "2606"}

#: Les trois variantes de la planche. `rapport` = r / R ; 0,382 est le
#: pentagramme regulier, dont les aretes s'alignent deux a deux. `arrondi` est
#: le rayon d'arc des pointes, en fraction de R.
VARIANTES = {
    "vive": dict(rapport=0.382, arrondi=0.0),
    "large": dict(rapport=0.50, arrondi=0.0),
    "adoucie": dict(rapport=0.45, arrondi=0.08),
}

#: La variante servie, tranchee par Nicolas au soixante-douzieme tour sur
#: `planche-tour72-etoiles.png`. A None, `appliquer` leve plutot que de
#: choisir a sa place.
VARIANTE = "large"

#: Le trait de ☆. "graisse" : celui du losange du master courant. "regulier" :
#: celui du losange du master par defaut, a toutes les graisses. La planche
#: montre les deux, parce qu'au Bold le trait du losange, 116 unites, bouche
#: le creux de ☆ en texte : mesure sur la premiere planche du tour, ou la
#: variante vive rendait ★★★★★ pour ★★★☆☆ a 18 px.
TRAIT = "regulier"

#: Debord de la pointe haute au-dessus de la capitale, en unites.
DEBORD = 12.0

#: Approche de chaque cote, en unites. Deux etoiles voisines sont separees de
#: 2 x APPROCHE, soit 1,8 px a 18 px.
APPROCHE = 50.0


# ----------------------------------------------------------------- geometrie

def _sommets(cx, cy, R, rapport):
    """Les dix sommets, pointe haute d'abord, sens trigonometrique."""
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = R if i % 2 == 0 else R * rapport
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def distance_arete(R, rapport):
    """d, la distance commune du centre aux dix aretes."""
    (x1, y1), (x2, y2) = _sommets(0.0, 0.0, R, rapport)[:2]
    return abs(x1 * y2 - x2 * y1) / math.hypot(x2 - x1, y2 - y1)


def contour(cx, cy, R, rapport, rho):
    """Le contour en [(x, y, type)], sens trigonometrique (plein en .glyphs).

    rho <= 0 : dix sommets vifs. Sinon chaque pointe devient un arc de rayon
    rho, tangent aux deux aretes, porte par une seule cubique.
    """
    pts = _sommets(cx, cy, R, rapport)
    if rho <= 0:
        return [(x, y, "line") for x, y in pts]
    d = distance_arete(R, rapport)
    if rho >= d:
        raise ValueError(f"arrondi {rho:.1f} >= distance d'arete {d:.1f}")
    k = (d - rho) / d
    centres = _sommets(cx, cy, R * k, rapport)
    out = []
    for i in range(10):
        x, y = pts[i]
        if i % 2:                       # creux, vif
            out.append((x, y, "line"))
            continue
        # Pointe i : arc de centre C, tangent a l'arete (i-1, i) puis (i, i+1).
        C = centres[i]
        prev, nxt = pts[i - 1], pts[(i + 1) % 10]
        t1 = _pied(C, prev, (x, y))
        t2 = _pied(C, (x, y), nxt)
        a1 = math.atan2(t1[1] - C[1], t1[0] - C[0])
        a2 = math.atan2(t2[1] - C[1], t2[0] - C[0])
        while a2 < a1:
            a2 += 2 * math.pi
        h = 4.0 / 3.0 * math.tan((a2 - a1) / 4.0) * rho
        c1 = (t1[0] - h * math.sin(a1), t1[1] + h * math.cos(a1))
        c2 = (t2[0] + h * math.sin(a2), t2[1] - h * math.cos(a2))
        out.append((t1[0], t1[1], "line"))
        out.append((c1[0], c1[1], "offcurve"))
        out.append((c2[0], c2[1], "offcurve"))
        out.append((t2[0], t2[1], "curve"))
    return out


def _pied(c, a, b):
    """Pied de la perpendiculaire abaissee de c sur la droite (a, b)."""
    ux, uy = b[0] - a[0], b[1] - a[1]
    s = ((c[0] - a[0]) * ux + (c[1] - a[1]) * uy) / (ux * ux + uy * uy)
    return (a[0] + s * ux, a[1] + s * uy)


def _chemin(pts, sens=1):
    p = GSPath()
    p.closed = True
    seq = pts if sens > 0 else _inverser(pts)
    for x, y, kind in seq:
        p.nodes.append(GSNode((round(x, 1), round(y, 1)), kind))
    return p


def _inverser(pts):
    """Le meme contour parcouru a l'envers, types de noeuds recales.

    Dans un chemin ferme, un noeud 'curve' ferme la cubique qui le precede.
    A l'envers, c'est le noeud d'ARRIVEE qui porte le type du segment : on
    retourne la liste des segments, pas la liste des noeuds.
    """
    segs, courant = [], []
    for x, y, kind in pts:
        courant.append((x, y))
        if kind != "offcurve":
            segs.append((kind, courant))
            courant = []
    # segment i : de l'extremite du segment i-1 a son dernier point
    out = []
    n = len(segs)
    for i in range(n - 1, -1, -1):
        kind, ptsseg = segs[i]
        depart = segs[i - 1][1][-1]
        ctrl = ptsseg[:-1][::-1]
        for c in ctrl:
            out.append((c[0], c[1], "offcurve"))
        out.append((depart[0], depart[1], kind))
    return out


# --------------------------------------------------------------------- trait

def trait_losange(layer):
    """Le trait perpendiculaire du losange, arete par arete, et sa dispersion.

    Chaque arete exterieure est appariee a l'arete interieure parallele la
    plus proche ; le trait est la distance entre leurs deux droites.
    """
    chemins = [s for s in layer.shapes if isinstance(s, GSPath)]
    if len(chemins) != 2 or any(len(p.nodes) != 4 for p in chemins) or any(
            n.type != "line" for p in chemins for n in p.nodes):
        raise ValueError(
            "lozenge n'est plus deux contours de quatre droites : le trait de "
            "whiteStar n'a plus de reference, et une valeur par defaut serait "
            "un mensonge silencieux")
    aretes = []
    for p in chemins:
        q = [(n.position.x, n.position.y) for n in p.nodes]
        aretes.append(list(zip(q, q[1:] + q[:1])))
    aire = [sum(a[0] * b[1] - b[0] * a[1] for a, b in ar) for ar in aretes]
    ext, inte = (aretes[0], aretes[1]) if abs(aire[0]) > abs(aire[1]) else (
        aretes[1], aretes[0])
    # Un losange a DEUX aretes interieures paralleles a chaque arete
    # exterieure, la sienne et celle d'en face : parmi les paralleles, la
    # bonne est la plus proche. Le premier jet prenait la plus parallele, et
    # rendait 196 unites au Regular pour un trait de 75.
    mesures = []
    for a, b in ext:
        u = (b[0] - a[0], b[1] - a[1])
        lu = math.hypot(*u)
        dists = []
        for c, d in inte:
            v = (d[0] - c[0], d[1] - c[1])
            par = abs(u[0] * v[1] - u[1] * v[0]) / (lu * math.hypot(*v))
            if par < 0.02:
                dists.append(abs(u[0] * (c[1] - a[1])
                                 - u[1] * (c[0] - a[0])) / lu)
        if not dists:
            raise ValueError("lozenge : une arete exterieure sans arete "
                             "interieure parallele, le trait n'est pas lisible")
        mesures.append(min(dists))
    return sum(mesures) / len(mesures), max(mesures) - min(mesures)


def mesures_etoile(haut, reg):
    """(R, cy, demi-largeur, rho) pour une etoile qui tient de 0 a `haut`.

    L'arrondi fait RECULER les pointes : un arc de rayon rho sur une pointe
    de 36 degres la raccourcit de rho / sin 18 - rho, soit 67 unites pour
    rho = 30, mesure au premier jet qui rendait une etoile de 24 a 638. R se
    recale donc pour que le dessin arrondi garde la hauteur demandee :

        haut = R k (1 + cos 36) + 2 rho,   k = (d - rho) / d,   rho = a R
    """
    c36, c18 = math.cos(math.pi / 5), math.cos(math.pi / 10)
    dd = distance_arete(1.0, reg["rapport"])
    a = reg["arrondi"]
    k = (dd - a) / dd
    R = haut / (k * (1.0 + c36) + 2.0 * a)
    rho = a * R
    cy = R * k * c36 + rho
    return R, cy, R * k * c18 + rho, rho


# ------------------------------------------------------------------- calques

def _origine(font):
    """L'identifiant du master par defaut, lu et non suppose."""
    cp = font.customParameters["Variable Font Origin"]
    if cp is None or cp not in {m.id for m in font.masters}:
        raise KeyError("Variable Font Origin absent ou inconnu : le master par "
                       "defaut, dont le trait de whiteStar se lit, est "
                       "introuvable")
    return cp


def calques(font, variante, trait="graisse"):
    """{master : (largeur, contours de ★, contours de ☆, trait)} pour la police.

    Le dessin ne depend du master que par le trait de ☆ ; la silhouette est la
    meme partout, pour que ★ et ☆ restent superposables a toute graisse.
    """
    reg = VARIANTES[variante]
    loz = font.glyphs["lozenge"]
    if loz is None:
        raise KeyError("lozenge absent de la source : le trait de whiteStar "
                       "n'a pas de reference")
    ids = {m.id: m for m in font.masters}
    traits = {lay.layerId: trait_losange(lay)[0] for lay in loz.layers
              if lay.layerId in ids}
    if trait not in ("graisse", "regulier"):
        raise ValueError(f"trait {trait!r} inconnu")
    out = {}
    for lay in loz.layers:
        if lay.layerId not in ids:
            continue
        m = ids[lay.layerId]
        t = (traits[lay.layerId] if trait == "graisse"
             else traits[_origine(font)])
        R, cy, demi, rho = mesures_etoile(m.capHeight + DEBORD, reg)
        largeur = round(2 * demi + 2 * APPROCHE)
        cx = largeur / 2.0
        d = distance_arete(R, reg["rapport"])
        # LA GARDE DU TRAIT. Au-dela de d, l'homothetie (d - t) / d devient
        # NEGATIVE et rend une etoile retournee au fond de la premiere : la
        # variante vive au Bold, sur la premiere planche du tour, montrait un
        # point la ou il fallait un creux. Un creux sous 5 % de l'etoile ne
        # distingue plus ☆ de ★ en texte, mesure sur la meme planche.
        if ((d - t) / d) ** 2 < 0.05:
            raise ValueError(
                f"{variante} {m.name} : trait {t:.1f} pour une distance "
                f"d'arete de {d:.1f}, le creux de whiteStar fait "
                f"{max(d - t, 0) ** 2 / d ** 2:.0%} de l'etoile et ☆ se lit ★")
        ext = contour(cx, cy, R, reg["rapport"], rho)
        inte = contour(cx, cy, R * (d - t) / d, reg["rapport"],
                       max(rho - t, 0.0))
        out[m.name] = (largeur, [ext], [ext, inte], t)
    if len(out) != len(ids):
        raise ValueError(f"lozenge lu dans {len(out)} master(s) sur "
                         f"{len(ids)} : un master sans calque casse le variable")
    return out


def appliquer(font, log=None, variante=None, trait=None):
    """Ajoute blackStar et whiteStar a la police, dans tous ses masters."""
    variante = variante or VARIANTE
    trait = trait or TRAIT
    if variante is None or trait is None:
        raise ValueError("aucune variante d'etoile n'est tranchee "
                         "(etoiles.VARIANTE ou etoiles.TRAIT vaut None)")
    for nom in (PLEINE, VIDE):
        if font.glyphs[nom] is not None:
            raise ValueError(f"{nom} existe deja dans la source : la police de "
                             "base a change, et ce module ne l'ecrase pas")
    par_master = calques(font, variante, trait)
    ids = {m.name: m.id for m in font.masters}
    for nom in (PLEINE, VIDE):
        g = GSGlyph(nom)
        g.unicodes = [UNICODES[nom]]
        g.export = True
        # Groupes de crenage a leur propre nom, comme `narrownbspace` : aucune
        # paire ne les vise, et un groupe emprunte les ferait heriter.
        g.leftKerningGroup = g.rightKerningGroup = nom
        for mnom, (largeur, plein, evide, _t) in par_master.items():
            lay = GSLayer()
            lay.layerId = lay.associatedMasterId = ids[mnom]
            lay.width = largeur
            ctrs = plein if nom == PLEINE else evide
            for i, c in enumerate(ctrs):
                lay.shapes.append(_chemin(c, sens=1 if i == 0 else -1))
            g.layers.append(lay)
        font.glyphs.append(g)
    if log is not None:
        log.append((f"etoiles {variante}, trait {trait}", ", ".join(
            f"{m} trait {v[3]:.1f} chasse {v[0]}"
            for m, v in par_master.items())))
    return par_master
