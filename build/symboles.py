#!/usr/bin/env python3
"""Les symboles du site, soixante-quatorzieme tour : version 1.003.

LA DEMANDE. La session SEO a releve tous les caracteres du site que ni Temoin
1.002 ni l'Open Sans de secours n'affichent
(`echanges-seo/2026-09-28-seo-releve-caracteres.md`). Nicolas a retenu
quatorze caracteres, le 28 septembre 2026 ; les trois erreurs de saisie du
releve se corrigent dans le contenu (point 118).

  - sans dessin : U+1D52 sur `ordmasculine`, U+2043 sur `hyphen`, U+2981 sur
    `bullet` ; U+02D9 (`dotaccent`, deja dans la source) entre au servi par
    `subset_unicodes.txt`, sans geste ici ;
  - construits : la fleche gauche, les cinq formes pleines, la croix, la
    fleche a crochet, et les lettres a point souscrit.

AUCUN DESSIN A MAIN LEVEE, comme au soixante-treizieme tour. Chaque glyphe est
une operation ecrite :

  leftArrow           la fleche de `complements`, construite droite, retournee
                      de gauche a droite, puis penchee comme elle en italique.
  leftHookArrow       la meme tete et la meme hampe, et au bout de la hampe un
                      crochet en demi-cercle, au trait de la hampe, qui monte
                      jusqu'a la hauteur des capitales et s'y coupe d'equerre,
                      son centre a un rayon du dos de la tete.
  blackLargeCircle    un disque de 1 em, centre a mi-hauteur des capitales,
                      qui est aussi le milieu de la ligne (984 - 316) / 2.
                      Cible du site : le grand rond dessine en CSS.
  blackCircle         un disque de 0,45 em, meme centre. Cible du site : le
                      petit rond dessine en CSS.
  blackSquare         un carre de la surface du `blackCircle`, meme centre.
  rightBlackPointer   un triangle equilateral pointe a droite, de la hauteur
                      du carre, meme centre.
  upBlackTriangle     un triangle equilateral pose sur la ligne de base
                      (`VARIANTES_TRIANGLE`, choix de Nicolas sur planche).
  multiplicationX     le `multiply` agrandi a la hauteur des capitales, a son
                      trait : deux barres a 45 degres, bouts coupes d'equerre
                      comme les siens, de la ligne de base a la hauteur des
                      capitales. Le trait se lit sur le `multiply` de chaque
                      master, entre les bords paralleles de ses barres.
  Hdotbelow ...       la lettre, et le point du `dotaccentcomb` sous l'ancre
                      `bottom`, a la meme profondeur pour les quatre lettres :
                      sous leur pied le plus bas, au jour du point suscrit
                      au-dessus de la hauteur d'x (`calque_pointe`). h et T
                      suivent H et t : `case_mapping` de Font Bakery exige la
                      casse opposee de toute lettre servie (tour 73).

FORMES DROITES DANS LES DEUX SOURCES, et identiques aux quatre masters :
precedent des etoiles du soixante-douzieme tour, "une note ne penche pas". La
croix aussi est droite. Les deux fleches, construites sur la hampe du `minus`,
penchent comme la fleche du tour 73. Approche de 50 unites de chaque cote pour
les formes et la croix (`etoiles.APPROCHE`).

EN DERNIER DANS `make_temoin.process`, apres `complements` : les pieces portent
tous les gestes du projet, et aucun des noms neufs n'est dans l'amont. Des
copies de contours, jamais des composites (voir `complements`).

LEVE sur toute anomalie : une piece dont la topologie a change, un glyphe
neuf qui existe deja, un code deja porte, un crochet qui toucherait la tete,
un point souscrit qui toucherait la lettre.
"""

import math

from glyphsLib.classes import GSGlyph, GSLayer, GSNode, GSPath

import lot2 as L
import complements as CP
import etoiles as ET


TRIANGLE, ROND, GRAND_ROND = "upBlackTriangle", "blackCircle", "blackLargeCircle"
CARRE, POINTEUR, CROIX = "blackSquare", "rightBlackPointer", "multiplicationX"
GAUCHE, CROCHET = "leftArrow", "leftHookArrow"

#: Les lettres a point souscrit : nom -> lettre de base.
POINTEES = {"Hdotbelow": "H", "hdotbelow": "h", "Tdotbelow": "T",
            "tdotbelow": "t"}

FORMES = (TRIANGLE, ROND, GRAND_ROND, CARRE, POINTEUR)
NEUFS = FORMES + (CROIX, GAUCHE, CROCHET) + tuple(POINTEES)
UNICODES = {TRIANGLE: "25B2", ROND: "25CF", GRAND_ROND: "2B24",
            CARRE: "25A0", POINTEUR: "25BA", CROIX: "2715", GAUCHE: "2190",
            CROCHET: "21A9", "Hdotbelow": "1E24", "hdotbelow": "1E25",
            "Tdotbelow": "1E6C", "tdotbelow": "1E6D"}

#: Les codes ajoutes a des glyphes existants. `ordmasculine` est le `o` en
#: exposant d'Atkinson, dont `emod` et `rmod` suivent la regle ; `hyphen` porte
#: deja U+2010 et U+2011 depuis `complements`.
RENVOIS = {"ordmasculine": ("1D52",), "hyphen": ("2043",),
           "bullet": ("2981",)}

#: Diametres des disques, en em. Cibles du site, CSS du 28 septembre 2026.
DIAMETRE_GRAND = 1.0
DIAMETRE_PETIT = 0.45

#: Le triangle. "etoile" : la hauteur des etoiles, capitales plus
#: `etoiles.DEBORD`, parce qu'une pointe vive parait plus basse qu'une barre.
#: "x" : la hauteur d'x plus le meme debord.
VARIANTES_TRIANGLE = ("etoile", "x")
VARIANTE_TRIANGLE = "etoile"     # choix de Nicolas, planche-tour74-symboles

APPROCHE = ET.APPROCHE
KAPPA = 4.0 / 3.0 * math.tan(math.pi / 8.0)

#: Ecart minimal entre le point souscrit et le point le plus bas de sa lettre,
#: en unites. Les pieds de H et T descendent a -44, ceux de h a -32.
DEGAGEMENT = 40.0

#: Ecart admis entre les deux moities d'un bord de barre du `multiply`. Le
#: plus grand mesure est de 4,4 unites, ExtraBold romain : le dessin d'Atkinson
#: n'est pas une croix exacte. La garde ne vise qu'un multiply redessine.
TOL_BORD = 8.0

#: Jour minimal, a l'horizontale, entre le dos de la tete de la fleche a
#: crochet et le centre de son crochet.
JOUR_CROCHET = 30.0


# ------------------------------------------------------------------ outils

def _master(font, master_id):
    return next(m for m in font.masters if m.id == master_id)


def _calque_vide(master_id, chasse):
    lay = GSLayer()
    lay.layerId = lay.associatedMasterId = master_id
    lay.width = round(chasse)
    return lay


def _chemin(noeuds):
    """noeuds : [((x, y), type)], type 'line', 'curve' ou 'offcurve'."""
    p = GSPath()
    p.closed = True
    for (x, y), ty in noeuds:
        n = GSNode((round(x, 1), round(y, 1)), ty)
        n.smooth = ty == "curve"
        p.nodes.append(n)
    return p


def _polygone(pts):
    if CP._aire(pts) <= 0:
        raise ValueError("contour dans le mauvais sens")
    return _chemin([(pt, "line") for pt in pts])


def _centre(m):
    return m.capHeight / 2.0


# ------------------------------------------------------------------ formes

def _disque(cx, cy, r):
    """Quatre arcs, sens trigonometrique, depart en bas : l'ordre des noeuds
    du point de `dotaccentcomb`."""
    k = KAPPA * r
    return _chemin([
        ((cx + k, cy - r), "offcurve"), ((cx + r, cy - k), "offcurve"),
        ((cx + r, cy), "curve"),
        ((cx + r, cy + k), "offcurve"), ((cx + k, cy + r), "offcurve"),
        ((cx, cy + r), "curve"),
        ((cx - k, cy + r), "offcurve"), ((cx - r, cy + k), "offcurve"),
        ((cx - r, cy), "curve"),
        ((cx - r, cy - k), "offcurve"), ((cx - k, cy - r), "offcurve"),
        ((cx, cy - r), "curve")])


def mesures_formes(font, master_id, variante=None):
    m = _master(font, master_id)
    em = float(font.upm)
    d = DIAMETRE_PETIT * em
    cote = d * math.sqrt(math.pi) / 2.0          # surface du disque
    variante = variante or VARIANTE_TRIANGLE
    if variante not in VARIANTES_TRIANGLE:
        raise ValueError(f"variante de triangle inconnue : {variante}")
    haut = (m.capHeight if variante == "etoile" else m.xHeight) + ET.DEBORD
    return {"centre": _centre(m), "grand": DIAMETRE_GRAND * em, "petit": d,
            "cote": cote, "triangle": haut, "variante": variante}


def calques_formes(font, master_id, variante=None):
    M = mesures_formes(font, master_id, variante)
    cy, a = M["centre"], APPROCHE
    out = {}
    for nom, D in ((GRAND_ROND, M["grand"]), (ROND, M["petit"])):
        lay = _calque_vide(master_id, D + 2 * a)
        lay.shapes.append(_disque(a + D / 2.0, cy, D / 2.0))
        out[nom] = lay
    c = M["cote"]
    lay = _calque_vide(master_id, c + 2 * a)
    lay.shapes.append(_polygone([(a, cy - c / 2), (a + c, cy - c / 2),
                                 (a + c, cy + c / 2), (a, cy + c / 2)]))
    out[CARRE] = lay
    w = c * math.sqrt(3.0) / 2.0
    lay = _calque_vide(master_id, w + 2 * a)
    lay.shapes.append(_polygone([(a, cy - c / 2), (a + w, cy),
                                 (a, cy + c / 2)]))
    out[POINTEUR] = lay
    h = M["triangle"]
    b = 2.0 * h / math.sqrt(3.0)
    lay = _calque_vide(master_id, b + 2 * a)
    lay.shapes.append(_polygone([(a, 0.0), (a + b, 0.0), (a + b / 2, h)]))
    out[TRIANGLE] = lay
    return out, M


# ------------------------------------------------------------------- croix

def trait_multiply(font, master_id):
    """Le trait du `multiply` : l'ecart entre les deux bords paralleles de
    chacune de ses deux barres, moyenne des deux, sur le dessin tel quel.

    PREMIER JET ABANDONNE : la longueur des bouts coupes d'equerre, apres
    redressement de l'italique. Le `multiply` italique n'est pas le romain
    penche, et ses bouts redresses mesurent 43 et 55 a l'ExtraLight. L'ecart
    entre bords paralleles rend au romain la meme valeur que les bouts, 81,3
    au Regular.

    Chaque bord est pris a son milieu : les bords devient de 0,5 degre au
    romain (noeuds entiers) et jusqu'a 2 degres en italique, ou les barres
    s'effilent. Leve si le multiply n'a plus ses douze noeuds droits, s'il n'a
    pas deux directions de bords, ou si les deux moities d'un bord s'ecartent
    de plus de `TOL_BORD`.
    """
    m = _master(font, master_id)
    lay = CP._calque(font.glyphs["multiply"], master_id)
    ps = L.paths(lay)
    if len(ps) != 1 or len(ps[0].nodes) != 12 or any(
            n.type != "line" for n in ps[0].nodes):
        raise ValueError(f"croix {m.name} : le multiply n'a plus ses 12 noeuds "
                         "droits")
    pts = CP._pts(ps[0])
    aretes = [(pts[i], pts[(i + 1) % 12]) for i in range(12)]
    lg = sorted(math.dist(a, b) for a, b in aretes)
    seuil = (lg[3] + lg[4]) / 2.0                 # quatre bouts, huit bords
    groupes = {}
    for a, b in aretes:
        if math.dist(a, b) < seuil:
            continue
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0
        cle = next((c for c in groupes if abs(c - ang) < 3.0), ang)
        groupes.setdefault(cle, []).append((a, b))
    if len(groupes) != 2 or any(len(v) != 4 for v in groupes.values()):
        raise ValueError(f"croix {m.name} : le multiply n'a pas deux barres "
                         f"({ {round(c): len(v) for c, v in groupes.items()} })")
    traits = []
    for cle, bords in groupes.items():
        t = math.radians(cle)
        nx, ny = -math.sin(t), math.cos(t)
        offs = sorted(nx * (a[0] + b[0]) / 2 + ny * (a[1] + b[1]) / 2
                      for a, b in bords)
        bas, haut = offs[:2], offs[2:]
        if bas[1] - bas[0] > TOL_BORD or haut[1] - haut[0] > TOL_BORD:
            raise ValueError(f"croix {m.name} : bords de barre non alignes "
                             f"({[round(o, 1) for o in offs]})")
        traits.append(sum(haut) / 2.0 - sum(bas) / 2.0)
    return sum(traits) / 2.0


def contour_croix(cx, cy, E, T):
    """Deux barres a 45 degres, bouts d'equerre, dans le carre de demi-cote E.
    L'ordre des noeuds est celui du `multiply` : creux du bas, puis les bras
    dans le sens trigonometrique."""
    a = T / 2.0
    Lb = E * math.sqrt(2.0) - a                   # demi-longueur d'une barre
    s = math.sqrt(2.0)
    c = a * s
    rel = [(0.0, -c), ((Lb - a) / s, (-Lb - a) / s), ((Lb + a) / s, (-Lb + a) / s),
           (c, 0.0), ((Lb + a) / s, (Lb - a) / s), ((Lb - a) / s, (Lb + a) / s),
           (0.0, c), ((-Lb + a) / s, (Lb + a) / s), ((-Lb - a) / s, (Lb - a) / s),
           (-c, 0.0), ((-Lb - a) / s, (-Lb + a) / s), ((-Lb + a) / s, (-Lb - a) / s)]
    return [(cx + x, cy + y) for x, y in rel]


def calque_croix(font, master_id):
    m = _master(font, master_id)
    T = trait_multiply(font, master_id)
    E = m.capHeight / 2.0
    lay = _calque_vide(master_id, 2 * E + 2 * APPROCHE)
    lay.shapes.append(_polygone(contour_croix(APPROCHE + E, _centre(m), E, T)))
    return lay, T


# ----------------------------------------------------------------- fleches

def _fleche_droite(font, master_id):
    """La fleche de `complements`, construite DROITE : (pts, chasse, M)."""
    M = CP.mesures_fleche(font, master_id)
    pts, chasse, h = CP.contour_fleche(dict(M, k=0.0),
                                       CP.VARIANTES_FLECHE[CP.VARIANTE_FLECHE])
    return pts, chasse, dict(M, tete=h)


def _retourner(pts, chasse):
    """Miroir gauche-droite, ordre inverse pour garder le sens du contour."""
    return [(chasse - x, y) for x, y in reversed(pts)]


def _pencher(noeuds, yc, k):
    return [((x + (y - yc) * k, y), ty) for (x, y), ty in noeuds]


def calque_gauche(font, master_id):
    pts, chasse, M = _fleche_droite(font, master_id)
    g = _retourner(pts, chasse)
    if CP._aire(g) <= 0:
        raise ValueError("fleche gauche : contour dans le mauvais sens")
    lay = _calque_vide(master_id, chasse)
    lay.shapes.append(_chemin(_pencher([(p, "line") for p in g],
                                       M["yc"], M["k"])))
    return lay, M


def calque_crochet(font, master_id):
    """La fleche gauche, et un crochet en demi-cercle au bout de sa hampe.

    Les dix points de la fleche droite sont, dans l'ordre : bout de la hampe
    en bas, jonction en bas, deux points du bras bas, pointe en bas, pointe
    en haut, deux points du bras haut, jonction en haut, bout en haut. Une
    fois retournes et pris en sens inverse : bout en haut (0), jonction en
    haut (1), dos du bras haut (2 et 3), pointe (4 et 5), dos du bras bas (6
    et 7), jonction en bas (8), bout en bas (9). Le crochet remplace le bout.

    PREMIER JET ABANDONNE avant la planche : un bras du haut qui revenait
    jusqu'a l'aplomb du dos de la tete. La tete grandit dans les gras
    (`complements.BRAS`) et monte a 588 au Bold, quand le bras descend a 540 :
    ils se touchaient. Le crochet est donc un demi-cercle coupe d'equerre a
    son sommet.

    SECOND JET ABANDONNE sur la premiere planche : l'encre de la pointe au
    crochet egale a celle de la fleche. La tete des gras est longue, et il ne
    restait que 32 unites de hampe entre elle et le crochet a l'ExtraBold. Le
    centre du crochet est donc a UN RAYON du dos de la tete, a toutes les
    graisses : la chasse suit la tete, et au Regular elle ne perd que 7 unites
    sur celle de la fleche. La garde mesure le jour a l'horizontale.
    """
    m = _master(font, master_id)
    pts, chasse, M = _fleche_droite(font, master_id)
    g = _retourner(pts, chasse)
    if len(g) != 10 or abs(g[2][0] - g[3][0]) > 0.01:
        raise ValueError(f"crochet {m.name} : la fleche n'a plus ses dix points")
    t, yc = M["hampe"], M["yc"]
    pointe, dos = g[4][0], g[3][0]
    r = (m.capHeight - yc - t / 2.0) / 2.0                # rayon au trait
    Ro, Ri = r + t / 2.0, r - t / 2.0
    if Ri <= 0:
        raise ValueError(f"crochet {m.name} : trait plus gros que le crochet")
    xc = dos + r                                          # centre du crochet
    jour = xc - dos
    if jour < JOUR_CROCHET:
        raise ValueError(f"crochet {m.name} : le crochet touche la tete "
                         f"({jour:.0f} u)")
    cy = yc + r
    noeuds = [((xc, yc + t / 2.0), "line")]
    noeuds += [(p, "line") for p in g[1:-1]]
    noeuds.append(((xc, yc - t / 2.0), "line"))
    # arc exterieur, du bas vers le haut, sens trigonometrique
    for a1, a2 in ((-math.pi / 2, 0.0), (0.0, math.pi / 2)):
        c1, c2, p2 = CP._arc(xc, cy, Ro, a1, a2)
        noeuds += [(c1, "offcurve"), (c2, "offcurve"), (p2, "curve")]
    noeuds.append(((xc, cy + Ri), "line"))                # la coupe du sommet
    # arc interieur, du haut vers le bas
    for a1, a2 in ((math.pi / 2, 0.0), (0.0, -math.pi / 2)):
        c1, c2, p2 = CP._arc(xc, cy, Ri, a1, a2)
        noeuds += [(c1, "offcurve"), (c2, "offcurve"), (p2, "curve")]
    # le dernier point de l'arc interieur est le premier du contour
    fin = noeuds.pop()
    if math.dist(fin[0], noeuds[0][0]) > 0.01:
        raise ValueError(f"crochet {m.name} : l'arc ne se referme pas")
    noeuds[0] = (noeuds[0][0], "curve")
    on = [p for p, ty in noeuds if ty != "offcurve"]
    if CP._aire(on) <= 0:
        raise ValueError(f"crochet {m.name} : contour dans le mauvais sens")
    lay = _calque_vide(master_id, xc + Ro + M["x0"])
    lay.shapes.append(_chemin(_pencher(noeuds, yc, M["k"])))
    return lay, dict(M, rayon=r, jour=jour)


# ---------------------------------------------------------- point souscrit

def _ancre(lay, nom):
    a = [x for x in lay.anchors if x.name == nom]
    if len(a) != 1:
        raise ValueError(f"ancre {nom} absente ou double")
    return a[0].position.x, a[0].position.y


def _fond(font, master_id):
    """Le point le plus bas des lettres de base, dans ce master."""
    return min(n.position.y for b in set(POINTEES.values())
               for p in L.paths(CP._calque(font.glyphs[b], master_id))
               for n in p.nodes)


def calque_pointe(font, master_id, base):
    """La lettre et le point du `dotaccentcomb`, sous l'ancre `bottom`.

    PREMIER JET ABANDONNE avant la planche : le point en miroir du point
    suscrit, aussi loin sous l'ancre `bottom` que le point suscrit est
    au-dessus de l'ancre `_top`. Les pieds de H et de T descendent a -44, et au
    Bold le point n'y laissait que 32 unites.

    La regle : les quatre lettres ont leur point a la MEME profondeur, pour
    qu'une ligne de translitteration garde ses points alignes. Le haut du point
    est sous le point le plus bas des quatre lettres (`_fond`), au jour qui
    separe le point suscrit de la hauteur d'x (le bas du point moins l'ancre
    `_top` du diacritique). A l'horizontale, le centre du point suit l'ancre
    `bottom`, penche en italique.
    """
    m = _master(font, master_id)
    k = CP._penche(m)
    src = CP._calque(font.glyphs[base], master_id)
    lay = CP._copier(src)
    ax, ay = _ancre(src, "bottom")
    diac = CP._calque(font.glyphs["dotaccentcomb"], master_id)
    tx, ty = _ancre(diac, "_top")
    ps = L.paths(diac)
    if len(ps) != 1:
        raise ValueError(f"point {m.name} : dotaccentcomb n'a plus un contour")
    pt = CP._pts(ps[0])
    xs, ys = [x for x, _ in pt], [y for _, y in pt]
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    demi = (max(ys) - min(ys)) / 2.0
    jour = min(ys) - ty
    if jour <= 0:
        raise ValueError(f"point {m.name} : le point suscrit touche son ancre")
    dx = (cx - tx) - (cy - ty) * k                # decalage redresse
    ny = _fond(font, master_id) - jour - demi
    nx = ax + dx + (ny - ay) * k
    point = ps[0].clone()
    for n in point.nodes:
        n.position = type(n.position)(round(n.position.x + nx - cx, 1),
                                      round(n.position.y + ny - cy, 1))
    bas = min(n.position.y for p in L.paths(lay) for n in p.nodes)
    haut_point = max(n.position.y for n in point.nodes)
    if bas - haut_point < DEGAGEMENT:
        raise ValueError(f"point {base} {m.name} : {bas - haut_point:.0f} u "
                         f"sous la lettre, moins que {DEGAGEMENT}")
    lay.shapes.append(point)
    return lay, bas - haut_point


# -------------------------------------------------------------- appliquer

def groupes(font):
    g = {n: (n, n) for n in FORMES + (CROIX, GAUCHE, CROCHET)}
    for nom, base in POINTEES.items():
        b = font.glyphs[base]
        g[nom] = (b.leftKerningGroup, b.rightKerningGroup)
    return g


def renvoyer(font, log=None):
    portes = {u.upper() for g in font.glyphs for u in (g.unicodes or [])}
    for nom, codes in RENVOIS.items():
        g = font.glyphs[nom]
        if g is None:
            raise ValueError(f"{nom} absent de la source")
        for c in codes:
            if c in portes:
                raise ValueError(f"U+{c} est deja porte par un glyphe")
        g.unicodes = list(g.unicodes) + list(codes)
    if log is not None:
        log.append(("renvois symboles", ", ".join(
            f"{n} + U+{' U+'.join(c)}" for n, c in RENVOIS.items())))


def calques(font, variante=None):
    """Les calques des glyphes neufs, par master. Rend (dict, journal)."""
    out = {n: {} for n in NEUFS}
    jrn = {}
    for m in font.masters:
        f, M = calques_formes(font, m.id, variante)
        for n, lay in f.items():
            out[n][m.id] = lay
        out[CROIX][m.id], T = calque_croix(font, m.id)
        out[GAUCHE][m.id], _ = calque_gauche(font, m.id)
        out[CROCHET][m.id], C = calque_crochet(font, m.id)
        jours = {}
        for nom, base in POINTEES.items():
            out[nom][m.id], jours[nom] = calque_pointe(font, m.id, base)
        jrn[m.name] = {"trait_croix": T, "rayon": C["rayon"],
                       "jour_crochet": C["jour"], "jours_point": jours,
                       "triangle": M["triangle"]}
    for n in NEUFS:
        formes = {tuple((len(p.nodes), tuple(nd.type for nd in p.nodes))
                        for p in L.paths(lay)) for lay in out[n].values()}
        if len(formes) != 1:
            raise ValueError(f"{n} : structure differente selon les masters")
    return out, jrn


def appliquer(font, log=None, variante=None):
    for nom in NEUFS:
        if font.glyphs[nom] is not None:
            raise ValueError(f"{nom} existe deja dans la source")
    portes = {u.upper() for g in font.glyphs for u in (g.unicodes or [])}
    for nom, c in UNICODES.items():
        if c in portes:
            raise ValueError(f"U+{c} ({nom}) est deja porte par un glyphe")
    renvoyer(font, log)
    par, jrn = calques(font, variante)
    grp = groupes(font)
    for nom in NEUFS:
        g = GSGlyph(nom)
        g.unicodes = [UNICODES[nom]]
        g.export = True
        g.leftKerningGroup, g.rightKerningGroup = grp[nom]
        for m in font.masters:
            g.layers.append(par[nom][m.id])
        font.glyphs.append(g)
    if log is not None:
        log.append((f"symboles, triangle {variante or VARIANTE_TRIANGLE}",
                    ", ".join(f"{mn} croix {j['trait_croix']:.1f} crochet "
                              f"r {j['rayon']:.0f} jour {j['jour_crochet']:.0f}"
                              for mn, j in jrn.items())))
    return par, jrn
