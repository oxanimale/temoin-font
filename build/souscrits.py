#!/usr/bin/env python3
"""
Temoin, etape 2, lot 4, dix-septieme tour : les crochets souscrits.

Le lot 2 a traite la cedille sur deux glyphes, `cedillacomb` et `ccedilla`, et
s'est arrete la. Restent dix-sept glyphes portant un crochet souscrit non
traite. Ce module porte l'inventaire de ces dix-sept, les etats candidats pour
l'ogonek et pour la virgule souscrite, et les mesures qui les separent.

Trois faits mesures avant d'ecrire quoi que ce soit, et qui cadrent le tour.

1. `lot2.loc_bas` designe le bout du crochet sur les dix-sept glyphes, dans les
   huit masters, avec le meme indice de segment et la meme longueur de bout que
   dans le combinant de reference. Les crochets sont des copies exactes collees
   dans les contours des lettres. Aucun localisateur nouveau n'est necessaire,
   et c'est verifie et non suppose : voir `verifier_localisateur`.

2. `lot2.loc_accent_bas`, le localisateur de la virgule, designe sur l'ogonek le
   segment 5, qui est son raccord au corps de la lettre et non son bout. Le
   couper ferait une entaille a la soudure. Un test qui marche sur un glyphe ne
   marche pas sur un autre de la meme famille : on nomme, on ne devine pas.

3. La recopie du reglage de la cedille sur l'ogonek ne marche pas, et le chiffre
   le dit. Les flancs de l'ogonek sont deux fois plus courts (49 et 34 unites en
   ExtraLight, contre 66 et 81 pour la cedille) et son bout est plus large
   (39 a 81 contre 29 a 54). L'angle de bout obtenu vaut 27 degres en
   ExtraLight et 43 en ExtraBold, quand la cedille tient 15 a 28. Egaliser
   demanderait environ 112 unites de saillie. D'ou les etats de ce module.

Un mot sur la direction de la saillie, qui n'est pas la meme pour les trois
crochets, et qui n'est pas celle qu'on croit :

    cedille          sortante (-0,92 / +0,39)  la pointe part a gauche
    ogonek           sortante (+0,93 / +0,37)  la pointe part a droite
    virgule souscrite sortante (-1,00 /  0,00) la pointe part a gauche, a plat

La cedille ne s'enfonce donc pas quand on avance sa pointe, ce que la passation
disait deja. La virgule souscrite non plus, et c'est heureux : elle descend
a -250, qui est le plancher de la police.
"""

import math
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

import coupe as K
import lot2 as L
import dessin as D


# ------------------------------------------------------------- l'inventaire
#
# Dix-sept glyphes, par famille. Le decompte est mesure sur la source et non
# repris d'une liste : voir `inventaire()`.

CEDILLE_FAITS = ["cedillacomb", "ccedilla"]
CEDILLE_A_FAIRE = ["Ccedilla", "Scedilla", "scedilla", "Tcedilla", "tcedilla"]

# Les trois combinants portent exactement le meme crochet : bout de 39 / 54 / 75
# / 81 unites selon le master, identique aux trois. Ils ne different que par
# leur raccord haut, celui qui se soude a la lettre — d'ou trois traces et non
# un composant commun.
OGONEK_COMBS = ["ogonekcomb", "ogonekcomb.case", "ogonekcomb.alt"]
OGONEK_LETTRES = ["Aogonek", "aogonek", "Eogonek", "eogonek",
                  "Iogonek", "iogonek", "Uogonek", "uogonek"]

# Un seul glyphe a traiter, onze qui en heritent comme composant : Gcommaaccent,
# Kcommaaccent, Lcommaaccent, Ncommaaccent, Scommaaccent, Tcommaaccent, plus
# leurs cinq bas de casse. Aucun ne sert au francais.
VIRGULE_SOUS = ["commaaccentcomb"]

TOUS = (CEDILLE_A_FAIRE + OGONEK_COMBS + OGONEK_LETTRES + VIRGULE_SOUS)

# Le seul des dix-sept qui soit servi sur le site : le C cedille capitale.
# U+00C7 est dans `subset_unicodes.txt`, les autres n'y sont pas.
SERVI = ["Ccedilla"]


# ----------------------------------------------------------- les etats a juger
#
# Chaque etat est ("nom lisible", genre, parametres). Le genre dit quelle
# geometrie s'applique :
#   "brut"   : rien, l'etat d'Atkinson
#   "pointe" : K.pointe(tirage, saillie), la mise en pointe du lot 2
#   "coupe"  : K.coupe(angle, sens), la loi generale du lot 2
#   "egal"   : K.pointe avec la saillie calculee master par master pour que
#              l'angle du bout egale celui de la cedille dans ce master
#
# `saillie` est en unites et non en epaisseurs. La raison est celle du lot 2 :
# proportionnelle, elle faisait descendre la virgule de 51 unites en Regular et
# de 89 en ExtraBold, donc la queue changeait de proportion le long de l'axe.

TIRAGE_CEDILLE, SAILLIE_CEDILLE = L.POINTE_CEDILLE     # (3.5, 45.0)
SAILLIE_VIRGULE = L.POINTE_VIRGULE[1]                  # 55.0

ETATS_OGONEK = [
    ("G0  brut, coupe droite d'Atkinson",          "brut",   None),
    ("G1  reglage cedille recopie (3,5 / 45)",     "pointe", (3.5, 45.0)),
    ("G2  saillie 75",                             "pointe", (3.5, 75.0)),
    ("G3  saillie egalisant l'angle de la cedille", "egal",  (3.5, None)),
    ("G4  coupe simple a 20 degres",               "coupe",  (20.0, L.CCW)),
]

# Sur la virgule souscrite la variable utile n'est pas la saillie mais le
# tirage, et c'est la mesure qui l'a dit. Ses deux flancs font 132 et 224 unites
# en Regular pour un crochet qui mesure 194 de haut : un tirage de 3,5 fois le
# bout depasse les deux, donc `pointe` recule chaque flanc de 85 % de sa
# longueur et le crochet se pince. Au Bold et a l'ExtraBold il se coupe
# franchement en deux — deux taches d'encre au lieu d'une, mesure a 900 et
# 1800 pixels. Le reglage de la virgule ne se recopie donc pas ici, et pour la
# raison inverse de l'ogonek : par exces et non par defaut.
ETATS_VIRGULE = [
    ("V0  brut, coupe droite d'Atkinson",           "brut",   None),
    ("V1  reglage virgule recopie (3,5 / 55)",      "pointe", (3.5, 55.0)),
    ("V2  tirage 1,5 saillie 55",                   "pointe", (1.5, 55.0)),
    ("V3  tirage 1,0 saillie 55",                   "pointe", (1.0, 55.0)),
    ("V4  tirage 1,0 saillie 25",                   "pointe", (1.0, 25.0)),
]

# La cedille n'a rien a trancher : son reglage est arrete depuis le lot 2. Les
# cinq glyphes manquants le recoivent tel quel. Les deux etats servent a
# montrer ce que ca change, pas a choisir.
ETATS_CEDILLE = [
    ("C0  brut, coupe droite d'Atkinson",          "brut",   None),
    ("C1  reglage arrete du lot 2 (3,5 / 45)",     "pointe", L.POINTE_CEDILLE),
]


# --------------------------------------------------------------- application

def appliquer_etat(layer, genre, params, tol_egal=0.15):
    """Applique un etat a tous les contours du calque ou `loc_bas` trouve un
    bout. Rend une liste de dicts, un par contour touche :

        ip       indice du contour dans le calque
        i        indice du segment de bout, sur le contour d'avant traitement
        angle    angle d'ouverture du bout mis en pointe, None pour une coupe
        pointe   les coordonnees de la pointe reellement dessinee
        saillie  la saillie effective, utile pour le genre "egal"

    Ces deux derniers sont rendus, et non recalcules par l'appelant, parce
    qu'une verification doit prendre son objet du producteur. Le premier essai
    de ce tour passait a la mesure de jour un coin de la boite du glyphe en
    croyant lui passer la pointe : elle rendait 171 unites sur le Ccedilla, la
    distance entre deux points dont l'un n'existe pas sur le contour. C'est le
    meme defaut que la premiere verification de la coupe oblique, au quatorzieme
    tour.
    """
    out = []
    for p in list(L.paths(layer)):
        ip = layer.shapes.index(p)
        segs = K.to_segs(p)
        # Seuls les contours d'encre, jamais les creux. `lot2.appliquer` balaie
        # tous les contours en s'appuyant sur une phrase de son docstring — les
        # contreformes n'ont pas de segment droit et s'ignorent d'elles-memes —
        # qui est vraie des accents et fausse ici : la contreforme du A est un
        # triangle a trois segments droits, et `loc_bas` y trouvait un bout
        # qu'elle mettait en pointe. Le symptome etait un chiffre impossible,
        # une coupe simple qui ajoutait 14 % d'encre au Aogonek, la contreforme
        # ayant perdu un quart de son aire. Le crochet est toujours de la
        # matiere : le filtre est un choix explicite, pas une supposition.
        if K.area(segs) < 0:
            continue
        idx = L.loc_bas(segs)
        if not idx:
            continue
        i = idx[0]
        if genre == "brut":
            out.append(dict(ip=ip, i=i, angle=None, pointe=K.mid(segs[i]),
                            saillie=None))
            continue
        if genre == "coupe":
            theta, sens = params
            segs = K.coupe(segs, i, theta, sens, 0.0)
            out.append(dict(ip=ip, i=i, angle=None, pointe=K.mid(segs[i]),
                            saillie=None))
        else:
            tirage, saillie = params
            if genre == "egal":
                saillie = saillie_egalisante(segs, i, tol=tol_egal)
            segs = K.pointe(segs, i, tirage, saillie)
            out.append(dict(ip=ip, i=i, angle=angle_bout(segs, i),
                            pointe=tuple(segs[i]["p3"]), saillie=saillie))
        layer.shapes[ip] = K.from_segs(segs)
    return out


def angle_bout(segs, i):
    """Angle d'ouverture, en degres, du bout mis en pointe au segment `i`.

    Apres `K.pointe`, le bout est fait de deux courbes qui se rejoignent au
    point T : segs[i] arrive en T, segs[i+1] en repart. L'angle du bout est
    l'angle entre les deux tangentes en T, mesure a l'interieur du trait.
    """
    n = len(segs)
    a = K.tangent_out(segs[i])                 # direction en arrivant en T
    b = K.tangent_in(segs[(i + 1) % n])        # direction en repartant de T
    cos = float(-a[0] * b[0] - a[1] * b[1])
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


def angle_cedille_ref(font, mid, master, tirage=3.5, saillie=45.0):
    """Angle de bout de la cedille arretee, dans un master donne.

    C'est la reference que l'etat G3 egalise. Elle est mesuree sur
    `cedillacomb` a chaque appel, dans le master demande, et non recopiee : un
    etalonnage pris ailleurs que sur l'objet compare n'etalonne rien, et la
    valeur va de 15 degres en ExtraLight a 28 en ExtraBold.
    """
    g = font.glyphs["cedillacomb"]
    lay = next(l for l in g.layers if l.layerId in mid and mid[l.layerId] == master)
    p = L.paths(lay)[0]
    segs = K.to_segs(p)
    i = L.loc_bas(segs)[0]
    return angle_bout(K.pointe(segs, i, tirage, saillie), i)


def saillie_egalisante(segs, i, cible=None, lo=0.0, hi=400.0, tol=0.15, iters=40):
    """Saillie qui donne au bout l'angle `cible`, par dichotomie.

    L'angle decroit quand la saillie croit — la pointe s'allonge. On cherche
    donc par dichotomie sur une fonction monotone decroissante. Si `cible` n'est
    pas donnee, elle est laissee a l'appelant : cette fonction ne connait pas la
    cedille.
    """
    if cible is None:
        cible = _CIBLE_COURANTE[0]
    for _ in range(iters):
        m = (lo + hi) / 2.0
        a = angle_bout(K.pointe(segs, i, 3.5, m), i)
        if abs(a - cible) < tol:
            return m
        if a > cible:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2.0


# La cible de l'etat "egal" est posee avant l'application, master par master.
_CIBLE_COURANTE = [20.0]


def poser_cible(angle):
    _CIBLE_COURANTE[0] = angle


# ------------------------------------------------------------------ mesures

def boite(layer):
    """Boite du calque, contours resolus a plat."""
    cs = [D.flatten(p) for p in L.paths(layer)]
    xs = [x for c in cs for x, _ in c]
    ys = [y for c in cs for _, y in c]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def encre(layer):
    return abs(sum(D.aire(D.flatten(p)) for p in L.paths(layer)))


def _rendu_cadre(contours, taille, marge=0.10):
    """Rendu binaire cadre sur la boite du dessin.

    `mesure_O._rendu` ne sert pas ici : il cadre a 12 % / 88 % de l'image en
    supposant un glyphe pose sur la ligne de base. Un crochet souscrit vit
    entre -250 et +30, il sortirait de l'image par le bas et le compte de
    contreformes serait fait sur un dessin tronque.
    """
    xs = [x for c in contours for x, _ in c]
    ys = [y for c in contours for _, y in c]
    if not xs:
        return None
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    ech = taille * (1 - 2 * marge) / max(w, h, 1e-6)
    ox = taille * marge - min(xs) * ech
    oy = taille * (1 - marge) + min(ys) * ech
    im = Image.new("L", (taille, taille), 255)
    dr = ImageDraw.Draw(im)
    # Point 85, quarante-neuvieme tour : classement par imbrication. Aucun
    # glyphe a souscrit ne porte de contour greffe aujourd'hui, mais ce rendu
    # sert un COMPTE DE TACHES, ou un greffon efface en retire une.
    for c, e in D.couches(contours):
        if len(c) > 2:
            dr.polygon([(ox + x * ech, oy - y * ech) for x, y in c],
                       fill=0 if e else 255)
    return np.asarray(im) < 128


def topologie(layer, seuil=0.002):
    """(taches, contreformes, accord) a 900 et 1800 pixels.

    Deux resolutions parce qu'un compte obtenu par rasterisation depend de la
    resolution des qu'il y a une quasi-tangence — le Ccedilla italique a
    justement ce defaut dans la police d'origine, sa queue frolant son propre
    fut, et il change de compte selon la resolution avant toute modification.
    Ne conclure que si les deux concordent, et le dire quand elles divergent.
    """
    cs = [D.flatten(p) for p in L.paths(layer)]
    out = []
    for taille in (900, 1800):
        a = _rendu_cadre(cs, taille)
        if a is None:
            return (0, 0, True)
        encre_px = int(a.sum())
        lab, n = ndimage.label(~a)
        inte = [int((lab == k).sum()) for k in range(1, n + 1)
                if not ((lab == k)[0, :].any() or (lab == k)[-1, :].any()
                        or (lab == k)[:, 0].any() or (lab == k)[:, -1].any())]
        inte = [v for v in inte if v > seuil * encre_px]
        taches = ndimage.label(a, structure=np.ones((3, 3)))[1]
        out.append((taches, len(inte)))
    return out[0][0], out[0][1], out[0] == out[1]


def jour_pointe(layer, rap):
    """Passe blanche la plus etroite entre la pointe et le reste du dessin.

    La mise en pointe recule les deux flancs du bout. Sur un crochet soude a sa
    lettre dans le meme contour, rien ne garantit que la pointe, en avancant, ne
    vienne pas froler une paroi voisine — la jambe du A pour l'ogonek, le fut du
    t pour la cedille. Le lot 4 a rencontre exactement ce cas sur le bras du O :
    deux traits qui se frolent sans se toucher rendent toujours une tache et une
    contreforme, donc la topologie ne le voit pas.

    Methode reprise de `mesure_O.fente`, qui exclut le voisinage par indice de
    parametre et non par rayon : ici on ecarte les quatre segments que la mise
    en pointe a touches (les deux flancs recules et les deux moities du bout).
    Un seuil en rayon aurait rendu la distance au point suivant du meme flanc,
    c'est-a-dire le pas d'echantillonnage.

    Ce qu'elle mesure, et ce qu'elle ne mesure pas. Le minimum porte sur tout le
    reste du dessin, crochet compris. Sur les six glyphes a cedille elle rend
    donc la meme valeur — 78, 82, 83, 82 unites selon le master — parce que le
    point le plus proche de la pointe appartient au crochet lui-meme, et que les
    crochets sont des copies exactes. Ce n'est pas une panne : la pointe de la
    cedille part vers la gauche, elle s'eloigne du corps de la lettre, et il n'y
    a rien a mesurer de ce cote. Sur l'ogonek, dont la pointe part vers la
    droite et vers le haut, la valeur varie d'une lettre a l'autre et signale les
    cas serres : 22 unites sur le eogonek a saillie 45, 6 sur le Aogonek a
    saillie 75. Une colonne constante n'est un defaut que si la grandeur qu'elle
    mesure varie.
    """
    P = np.array(rap["pointe"], float)
    i = rap["i"]
    best = float("inf")
    for p in L.paths(layer):
        ip = layer.shapes.index(p)
        segs = K.to_segs(p)
        n = len(segs)
        for j, s in enumerate(segs):
            if ip == rap["ip"] and j in {(i - 1) % n, i % n, (i + 1) % n,
                                         (i + 2) % n}:
                continue
            for k in range(25):
                X = K.bez(s, k / 24.0)
                best = min(best, float(np.hypot(X[0] - P[0], X[1] - P[1])))
    return best


def taches_mot(src, mot, px_cadratin=300, attendu=None):
    """Nombre de taches d'encre d'un mot compose, et l'ecart a l'attendu.

    Trouvee a l'oeil et non par un chiffre : dans "zwierzeta" a saillie 45, le
    crochet du e ogonek part vers la droite et vient sous le pied du t. Aucune
    des colonnes du balayage ne pouvait le dire — la boite du glyphe, sa chasse
    et sa topologie sont celles d'un glyphe isole, et un crochet qui reste dans
    sa chasse peut toucher la voisine, puisque la chasse comprend deux approches
    et que la voisine avance dans la sienne.

    Meme mesure que `mesure_O.taches_mot`, rendue ici pour un mot dessine par
    `dessin.py` plutot que pour des contours poses a la main. `attendu` est le
    compte du meme mot avant traitement : c'est lui qui fait foi, le nombre de
    taches d'un mot n'etant pas le nombre de ses lettres — le i et le j en
    portent deux, et deux lettres peuvent se toucher deja dans la police de
    base.
    """
    taille = float(px_cadratin)
    lg = D.largeur(src, mot, taille)
    im = Image.new("L", (int(lg) + 2 * px_cadratin, 2 * px_cadratin), 255)
    D.dessiner(im, src, mot, px_cadratin * 0.5, int(1.4 * px_cadratin), taille,
               encre=0, fond=255)
    a = np.asarray(im) < 128
    n = ndimage.label(a, structure=np.ones((3, 3)))[1]
    return n, (None if attendu is None else n - attendu)


# ------------------------------------------------------------- verifications

def verifier_localisateur(fonts, noms, loc=None):
    """Le localisateur designe-t-il le meme bout dans tous les masters ?

    C'est le controle de `check3.py` du lot 2, applique aux dix-sept glyphes
    avant de les traiter. Rend la liste des anomalies : indice de segment qui
    change d'un master a l'autre, ou longueur de bout qui s'ecarte de plus de
    2 % de la mediane du glyphe.
    """
    loc = loc or L.loc_bas
    anomalies = []
    for font in fonts:
        mid = {m.id: m.name for m in font.masters}
        for nom in noms:
            g = font.glyphs[nom]
            if g is None:
                anomalies.append((nom, "absent de la source"))
                continue
            vus = {}
            for lay in g.layers:
                if lay.layerId not in mid:
                    continue
                trouve = None
                for ip, p in enumerate(L.paths(lay)):
                    segs = K.to_segs(p)
                    idx = loc(segs)
                    if idx:
                        trouve = (ip, idx[0], len(segs), K.length(segs[idx[0]]))
                        break
                if trouve is None:
                    anomalies.append((nom, f"{mid[lay.layerId]} : rien trouve"))
                else:
                    vus[mid[lay.layerId]] = trouve
            cles = {(v[0], v[1], v[2]) for v in vus.values()}
            if len(cles) > 1:
                anomalies.append(
                    (nom, f"le segment designe change de master a master : {cles}"))
    return anomalies


def inventaire(font):
    """Le decompte des dix-sept, lu sur la source et non sur une liste.

    Rend (a_traiter, deja_faits, heritent). `heritent` sont les glyphes qui
    portent un crochet en composant : ils suivent sans etre nommes.
    """
    mid = {m.id: m.name for m in font.masters}
    ref = next(iter(mid.values()))

    def calque(g):
        for l in g.layers:
            if l.layerId in mid and mid[l.layerId] == ref:
                return l

    from glyphsLib.classes import GSComponent
    heritent = []
    for g in font.glyphs:
        lay = calque(g)
        if lay is None:
            continue
        cs = [s.componentName for s in lay.shapes if isinstance(s, GSComponent)]
        if any(c in ("cedillacomb", "ogonekcomb", "ogonekcomb.case",
                     "ogonekcomb.alt", "commaaccentcomb") for c in cs):
            heritent.append(g.name)
    return TOUS, CEDILLE_FAITS, heritent
