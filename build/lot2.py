#!/usr/bin/env python3
"""
Temoin, etape 2, lot 2 : reperage des terminaisons et application de la loi.

coupe.py fait la geometrie. Ce module dit ou l'appliquer.

Regle de perimetre : on ne touche jamais une terminaison qui porte un
alignement (ligne de base, hauteur d'x, capitale, ascendante, descendante).
C'est ce qui garde le risque d'accessibilite a zero : les hampes, les jambages
et les sommets de fut restent exactement ou ils sont.
"""

import math

import numpy as np

from glyphsLib.classes import GSPath

import coupe as K


# ------------------------------------------------------------- reperage

def paths(layer):
    return [s for s in layer.shapes if isinstance(s, GSPath)]


def main_path(layer):
    """Le contour exterieur, celui de plus grande aire absolue."""
    ps = paths(layer)
    return max(ps, key=lambda p: abs(K.area(K.to_segs(p))))


def est_terminaison(segs, i):
    """Vrai si le segment `i` est un bout de trait, pas un flanc.

    Trois conditions. Les deux traits voisins doivent repartir en sens
    contraire — un flanc de fut a ses deux voisins qui partent du meme cote, et
    sa direction sortante n'est meme pas definie. Les deux coins doivent
    tourner dans le sens du contour, c'est-a-dire etre convexes : c'est ce qui
    distingue un bout de trait d'une encoche. Et le segment doit etre court
    devant ses voisins.
    """
    n = len(segs)
    try:
        a = K.tangent_out(segs[i - 1])
        b = K.tangent_in(segs[(i + 1) % n])
        ti, to = K.tangent_in(segs[i]), K.tangent_out(segs[i])
    except ValueError:
        return False
    if float(a[0] * b[0] + a[1] * b[1]) > -0.2:
        return False
    sens = 1.0 if K.area(segs) > 0 else -1.0
    debut = (a[0] * ti[1] - a[1] * ti[0]) * sens
    fin = (to[0] * b[1] - to[1] * b[0]) * sens
    if debut <= 0.05 or fin <= 0.05:
        return False
    # Deux mesures de longueur, cumulatives, parce qu'aucune ne suffit seule.
    #
    # Devant ses voisins : un bout de trait vaut l'epaisseur du trait, un flanc
    # vaut sa longueur. La comparaison porte sur la moyenne des deux voisins,
    # pas sur le plus court — la queue du l a un voisin tres court, et un test
    # sur le minimum la rejetait dans les masters gras, d'ou un l non modifie.
    #
    # Devant le glyphe : le flanc gauche du fut du E a deux voisins aussi longs
    # que lui, le premier test le laisse donc passer. Mais il fait toute la
    # hauteur de capitale. Un bout de trait, jamais.
    voisin = (K.seg_len(segs[i - 1]) + K.seg_len(segs[(i + 1) % n])) / 2.0
    if K.length(segs[i]) > 2.2 * voisin:
        return False
    xs = [p for s in segs for p in (s["p0"][0], s["p3"][0])]
    ys = [p for s in segs for p in (s["p0"][1], s["p3"][1])]
    taille = max(max(xs) - min(xs), max(ys) - min(ys))
    return K.length(segs[i]) <= 0.75 * taille


def lines(segs, vertical=None, both_sharp=False, terminal=False):
    """Segments droits d'un contour, filtres par orientation et par nature.

    `terminal` est desactive par defaut, et ce n'est pas un oubli. Le test de
    est_terminaison a ete essaye comme filtre general : aucun seuil ne separe
    proprement la queue du l de l'arete du fut du E sur les huit masters, les
    deux se croisent. Les localisateurs, eux, choisissent deja par position et
    par orientation, ce qui suffit — et check3.py verifie qu'ils designent bien
    le meme segment dans tous les masters, ce qui est la vraie garantie.
    """
    out = []
    for i, s in enumerate(segs):
        if s["kind"] != "line":
            continue
        dx = s["p3"][0] - s["p0"][0]
        dy = s["p3"][1] - s["p0"][1]
        if vertical is True and abs(dx) > abs(dy) * 0.3:
            continue
        if vertical is False and abs(dy) > abs(dx) * 0.3:
            continue
        if both_sharp and (s["smooth"] or segs[i - 1]["smooth"]):
            continue
        if terminal and not est_terminaison(segs, i):
            continue
        out.append(i)
    return out


# --------------------------------------------------- localisateurs par glyphe
#
# Chacun retourne la liste des indices de segments a traiter, dans un contour
# donne. Ils sont geometriques, pas positionnels : le meme localisateur doit
# retrouver la meme terminaison dans les quatre masters.

def loc_accent_bas(segs):
    """Les pieds d'accent : segments droits horizontaux les plus bas."""
    cand = lines(segs, vertical=False)
    if not cand:
        return []
    ymin = min(K.mid(segs[i])[1] for i in cand)
    return [i for i in cand if K.mid(segs[i])[1] < ymin + 12]


def loc_accent_haut(segs):
    """Cas du caron : ses bouts libres pointent vers le haut."""
    cand = lines(segs, vertical=False)
    if not cand:
        return []
    ymax = max(K.mid(segs[i])[1] for i in cand)
    return [i for i in cand if K.mid(segs[i])[1] > ymax - 12]


def loc_gauche(segs):
    """Terminaison verticale la plus a gauche (bras du i, queue du j)."""
    cand = lines(segs, vertical=True)
    return [min(cand, key=lambda i: K.mid(segs[i])[0])] if cand else []


def loc_droite(segs):
    """Terminaison verticale la plus a droite (queue du l, du q, barre du L)."""
    cand = lines(segs, vertical=True)
    return [max(cand, key=lambda i: K.mid(segs[i])[0])] if cand else []


def loc_barres_F(segs):
    """Les deux bouts de barre du F : verticaux, les plus a droite."""
    cand = lines(segs, vertical=True)
    cand.sort(key=lambda i: K.mid(segs[i])[0], reverse=True)
    return cand[:2]


def loc_barres_E(segs):
    """Les trois bouts de barre du E."""
    cand = lines(segs, vertical=True)
    cand.sort(key=lambda i: K.mid(segs[i])[0], reverse=True)
    return cand[:3]


def loc_barres_T(segs):
    """Les deux bouts de la barre du T.

    Le T a deux flancs de fut verticaux, longs d'une hauteur de capitale, et
    deux bouts de barre longs d'une largeur de trait. Le rapport entre les deux
    ne descend pas sous 3,5 dans les quatre masters romains, donc un plafond a
    45 % du plus long les separe sans ambiguite. Verifie master par master :
    ce sont les memes deux quadrants, hg et hd, qui sont designes partout, et
    leur longueur vaut exactement la largeur du fut.
    """
    v = lines(segs, vertical=True)
    if not v:
        return []
    lg = {i: abs(segs[i]["p3"][1] - segs[i]["p0"][1]) for i in v}
    plafond = 0.45 * max(lg.values())
    return [i for i in v if lg[i] <= plafond]


def loc_bouts_Z(segs):
    """Les deux bouts libres du Z : celui de la barre haute a gauche, celui de
    la barre basse a droite.

    Le meme filtre que pour le T ne marche pas ici, et l'essai l'a montre de la
    facon la plus utile : le Z n'a aucun flanc de fut, ses quatre segments
    verticaux font tous a peu pres la largeur du trait, donc un plafond relatif
    au plus long les ecartait tous les quatre. Le localisateur rendait une liste
    vide, et la mesure qui suivait annoncait "montee nulle, chasse inchangee"
    sur un glyphe ou rien n'avait ete fait.

    Les separer par la longueur ne marche pas non plus : le rapport s'inverse
    le long de l'axe. En ExtraLight les jonctions de la diagonale mesurent 60
    pour des bouts a 50 ; au Bold, 121 pour des bouts a 139. Meme piege qu'au
    lot 3, ou la relation axe/fut s'inversait par morceaux.

    On designe donc par position, et la mesure confirme le partage : le plafond
    de coupe des deux bouts retenus n'a pas de limite utile, celui des deux
    jonctions tombe a 32 degres au Bold. Ce ne sont pas des bouts de trait.
    """
    v = lines(segs, vertical=True)
    if not v:
        return []
    ys = [c for s in segs for c in (s["p0"][1], s["p3"][1])]
    milieu = (min(ys) + max(ys)) / 2.0
    haut = [i for i in v if K.mid(segs[i])[1] > milieu]
    bas = [i for i in v if K.mid(segs[i])[1] <= milieu]
    out = []
    if haut:
        out.append(min(haut, key=lambda i: K.mid(segs[i])[0]))
    if bas:
        out.append(max(bas, key=lambda i: K.mid(segs[i])[0]))
    return out


def loc_bas(segs):
    """Terminaison la plus basse (queue de la cedille)."""
    cand = lines(segs)
    return [min(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


def loc_hampe(segs):
    """Sommet du fut du g et du q : segment droit horizontal le plus haut.

    Exception assumee au perimetre : cette coupe porte la hauteur d'x. Elle
    n'est faite tourner que d'un cote, l'autre coin restant a 496 : la
    hauteur d'x est donc tenue par le coin qui ne bouge pas.
    """
    cand = lines(segs, both_sharp=True)
    return [max(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


# Les quatre localisateurs des vingtieme et vingt-et-unieme tours. Ils vivaient
# dans `termes.py` le temps de l'instruction et descendent ici avec les entrees
# qu'ils servent. Verifies par `check_termes.py` sur les huit masters des deux
# sources : meme contour, meme indice, meme topologie, meme quadrant, meme
# orientation, avec un temoin qui prouve que le controle sait signaler.

def loc_sommet_fut(segs):
    """Le segment droit HORIZONTAL le plus haut.

    Le sommet du fut gauche du n et du m, a la hauteur d'x, et le sommet du fut
    du t, a 620, qui ne porte aucun alignement.

    Pourquoi pas `loc_hampe`, qui rend deja le bon segment sur les trois : il
    filtre par `both_sharp`, donc il depend du drapeau `smooth` des noeuds. Ce
    drapeau n'est pas identique dans tous les masters de la source — le D a un
    noeud lisse au Bold et pas ailleurs, piege du lot 3. Filtrer par orientation
    ne depend d'aucun drapeau.
    """
    cand = lines(segs, vertical=False)
    return [max(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


def loc_haut_vertical(segs):
    """Le segment droit VERTICAL le plus haut : le bout du crochet du f."""
    cand = lines(segs, vertical=True)
    return [max(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


def loc_queue_t(segs):
    """Le segment droit VERTICAL le plus bas : le bout de la queue du t.

    `loc_droite` ne convient pas, et c'est le resultat du vingtieme tour. Il
    designe la queue en Regular, Bold et ExtraBold romains, et le bout droit de
    la barre transversale dans les cinq autres masters : en ExtraLight les deux
    sont a un point l'un de l'autre en abscisse, 259 contre 258. La demande de
    Nicolas disait "la meme coupe que le l", et le l recoit `loc_droite` — la
    lecture directe menait donc a un localisateur qui bascule d'un master a
    l'autre. C'est le temoin de `check_termes.py`.
    """
    cand = lines(segs, vertical=True)
    return [min(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


def loc_pied_droit(segs):
    """Le pied du fut droit : le plus a droite des bouts poses le plus bas.

    `loc_bas` ne convient pas : le n a deux pieds a la meme hauteur, et `min`
    sur l'ordonnee rend le premier des deux dans l'ordre du contour, donc le
    pied gauche. Un localisateur qui departage deux candidats a egalite par
    l'ordre du contour tire au sort.
    """
    cand = lines(segs, vertical=False)
    if not cand:
        return []
    ymin = min(K.mid(segs[i])[1] for i in cand)
    bas = [i for i in cand if K.mid(segs[i])[1] < ymin + 12]
    return [max(bas, key=lambda i: K.mid(segs[i])[0])] if bas else []


def loc_pied_gauche(segs):
    """Le pied du fut gauche : le plus a gauche des bouts poses le plus bas.

    Le symetrique exact de `loc_pied_droit`, et il est ecrit pour la meme
    raison : `loc_bas` departage par l'ordre du contour, donc il tire au sort
    des que deux bouts sont a la meme hauteur. Le m en a trois, a x = 114, 424
    et 733 au Regular, et le M aussi, bg, bc et bd.

    Verifie par `check_termes.py` sur les huit masters des deux sources pour le
    f, le m et le M : meme contour, meme indice de segment, meme quadrant, meme
    orientation. Sur le M, le bout du milieu est une diagonale de 130 unites
    posee exactement sur la ligne de base, donc il entre dans les candidats, et
    rien ne garantissait a priori que le plus a gauche soit le pied du fut.

    Une note connue sur le f : son quadrant vaut `bc` en romain et `bg` en
    italique. Le f n'a qu'un seul bout bas, donc le localisateur ne departage
    rien ; c'est le seuil de 35 % de largeur de boite de `lot4.quadrant` qui
    bascule sur un glyphe penche, comme sur la queue du t en ExtraLight Italic.
    """
    cand = lines(segs, vertical=False)
    if not cand:
        return []
    ymin = min(K.mid(segs[i])[1] for i in cand)
    bas = [i for i in cand if K.mid(segs[i])[1] < ymin + 12]
    return [min(bas, key=lambda i: K.mid(segs[i])[0])] if bas else []


def loc_sommet_droit(segs):
    """Le sommet du fut droit : le plus a droite des bouts poses le plus haut.

    Le symetrique exact de `loc_pied_gauche`, retourne vers le haut, et il est
    ecrit pour la meme raison : departager deux candidats a egalite par l'ordre
    du contour, c'est tirer au sort.

    **`loc_sommet_fut` rend le bon segment sur le N et sur le H aujourd'hui, et
    il le rend par accident.** Les deux glyphes ont DEUX bouts horizontaux a la
    hauteur de capitale — sur le H les sommets de ses deux futs, a x = 110 et
    556 au Regular ; sur le N le sommet du fut droit a 551 et la jonction de la
    diagonale a 128, longue de 91 unites contre 56 et qui n'est pas un bout de
    trait. `max(cand, key=y)` ne voit qu'une egalite parfaite en ordonnee et
    rend le PREMIER dans l'ordre du contour, qui se trouve etre le bon sur les
    huit masters des deux sources. Rien ne le garantit : le lot 3 a montre qu'un
    localisateur juste par un detail qui peut basculer est un localisateur qui
    ne marche pas, et `loc_hampe` a ete ecarte au vingtieme tour pour ce motif
    exact — il dependait du drapeau `smooth`, qui varie d'un master a l'autre.

    Sur le h et le k, en revanche, le bout de hampe est le SEUL bout horizontal
    a 708 : `loc_sommet_fut` y departage vraiment, et c'est celui du b, du d et
    du l depuis le lot 2. Aucun localisateur nouveau pour eux.

    La tolerance de 12 unites est celle de `loc_pied_gauche` et de
    `loc_pied_droit`, et c'est le debord optique des rondes de cette police,
    mesure au lot 4. Deux bouts qu'elle separe ne sont pas sur le meme
    alignement.
    """
    cand = lines(segs, vertical=False)
    if not cand:
        return []
    ymax = max(K.mid(segs[i])[1] for i in cand)
    haut = [i for i in cand if K.mid(segs[i])[1] > ymax - 12]
    return [max(haut, key=lambda i: K.mid(segs[i])[0])] if haut else []


# Lot 3 des vingt-deux gestes, vingt-septieme tour : la descendante, et ce qui
# n'en est pas. Trois localisateurs descendus de `termes.py` avec les entrees
# qu'ils servent, `termes` n'en gardant que des alias — deux copies d'un
# localisateur finissent par diverger, et c'est le protocole du vingt-deuxieme
# tour.

def loc_bout_jambe(segs):
    """Le segment droit HORIZONTAL le plus bas : le bout de la jambe du p.

    Symetrique exact de `loc_sommet_fut`, qui rend l'horizontal le plus haut et
    sert le bout de hampe du b, du d et du l depuis le vingt-sixieme tour.
    Filtrer par orientation ne depend d'aucun drapeau `smooth`, dont la valeur
    n'est pas identique dans tous les masters de la source : c'est ce qui a fait
    ecarter `loc_hampe` au vingtieme tour.

    **La jambe se termine a −162 et non a −251.** Le point ouvert 20 annonce la
    descendante declaree, que le p n'atteint pas et qu'aucune lettre de la
    police n'atteint : le seul glyphe qui y touche est `commaaccentcomb`. Un
    depassement mesure contre le `descender` serait faux de 89 unites, comme le
    bout de hampe l'a ete de 88 au vingt-sixieme tour.

    Verifie par `check_termes.py` sur les huit masters des deux sources :
    contour 0, segment 0, quadrant `bg`, horizontal a 0,0 degre.
    """
    cand = lines(segs, vertical=False)
    return [min(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


def loc_bout_queue_y(segs):
    """Le segment droit VERTICAL le plus bas : le bout de la queue du y.

    **Le bout de la queue du y est vertical, et personne ne l'avait mesure.** La
    queue descend vers la gauche et se termine par une coupe verticale, ses deux
    flancs etant les deux plats horizontaux qui l'encadrent. En ExtraLight
    romain, le bout va de (32, −162) a (32, −114) sur 48 unites.

    Consequence directe, et c'est elle qui a decide de la forme du geste : le
    coin sortant coulisse le long d'un flanc HORIZONTAL, donc il avance
    lateralement sans descendre d'une unite. C'est la structure du bout du
    crochet du f, en miroir et en bas.

    Pourquoi pas `loc_bas` : il rend le plat de DESSOUS, qui est un flanc et non
    le bout. C'est la seule des trois cibles du lot 3 ou les deux localisateurs
    ne tombent pas sur le meme segment.
    """
    cand = lines(segs, vertical=True)
    return [min(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


def loc_pied_Y(segs):
    """Le segment droit HORIZONTAL le plus bas : le pied du Y capitale.

    Meme filtre que `loc_bout_jambe`, et c'est volontaire : les deux designent
    un bout horizontal encadre par deux flancs verticaux. Ce qui les separe
    n'est pas dans le localisateur, c'est dans le glyphe — **le bout du p porte
    la descendante, mesuree a −162, et celui du Y porte la ligne de base, a
    0,0**. L'ymin du Y vaut 0,0 dans les huit masters : il ne descend pas.

    Deux noms plutot qu'un alias parce que les deux cibles ne recoivent pas le
    meme geste et ne relevent pas du meme alignement. Nicolas a demande au
    vingt-septieme tour que le y et le Y se traitent separement, « ce n'est pas
    la meme demande », et la geometrie le confirme.

    Le Y n'a qu'un seul bout bas, donc le localisateur ne departage rien : la
    note de quadrant est celle du pied du f, `bc` en romain et `bg` en italique,
    par le seuil de 35 % de `lot4.quadrant` sur un glyphe penche.
    """
    cand = lines(segs, vertical=False)
    return [min(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


def loc_terminaisons_S(segs):
    """Les deux coupes du S : segments droits a coins vifs des deux cotes.

    Les parties droites de la panse ont un noeud lisse, ce qui les exclut.
    """
    return lines(segs, both_sharp=True)


def loc_queue_g(segs):
    """La seule coupe du g : celle de la queue, la plus basse.

    Les deux autres segments droits a coins vifs sont le sommet du fut, qui
    porte la hauteur d'x, et l'arete de l'attaque. Ni l'un ni l'autre n'est
    une terminaison libre hors alignement.
    """
    cand = lines(segs, both_sharp=True)
    return [min(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


# ------------------------------------------- les trois bouts du lot 5
#
# LES RONDES DU LOT 5 PORTENT DES SEGMENTS DROITS, et la passation redoutait le
# contraire. Mesure au trentieme tour sur les huit masters des deux sources :
# le O et le o n'en ont aucun — deux contours de douze noeuds — mais le c et le
# C en portent deux, qui sont leurs bouts, le G huit, dont un bout, et le Q
# trois sur son contour exterieur et trois dans son creux.
#
# Les trois localisateurs ci-dessous ne filtrent ni par orientation, ni par
# longueur, ni par le drapeau `smooth` : ils lisent la NATURE DES VOISINS, qui
# ne peut pas basculer d'un master a l'autre. C'est la lecon de `loc_hampe`,
# qui rendait le bon bout par un detail fragile.

def loc_bout_de_ronde(segs):
    """Le ou les segments droits ENCADRES DE DEUX COURBES.

    C'est la definition d'un bout de trait sur une ronde : le plat terminal,
    entre deux flancs courbes. Rend [1, 6] sur le c et le C, [12] sur le G, et
    RIEN sur le Q, dont les trois segments droits ont chacun un voisin droit.
    Les indices sont identiques dans les huit masters des deux sources.

    Le corollaire compte autant que le localisateur : deux flancs voisins
    COURBES font refuser `coupe.coupe_sortante` et `coupe.bascule`, qui exigent
    de prolonger un flanc droit. Ces bouts ne peuvent recevoir que la
    rentrante, et c'est pourquoi le lot 5 est le premier depuis le lot 2 qui ne
    franchit aucun alignement.
    """
    n = len(segs)
    return [i for i, s in enumerate(segs)
            if s["kind"] == "line"
            and segs[(i - 1) % n]["kind"] == "curve"
            and segs[(i + 1) % n]["kind"] == "curve"]


def loc_repli_G(segs):
    """Le bout du repli interieur du G : droit, precede d'un droit, suivi d'une courbe.

    Le G porte huit segments droits ; celui-ci est le seul dont le voisin AVANT
    est droit et le voisin APRES courbe. Son symetrique — courbe avant, droit
    apres — est le pied de la barre verticale, et c'est le sens de parcours qui
    les distingue. Rend [7] dans les huit masters.
    """
    n = len(segs)
    return [i for i, s in enumerate(segs)
            if s["kind"] == "line"
            and segs[(i - 1) % n]["kind"] == "line"
            and segs[(i + 1) % n]["kind"] == "curve"]


def loc_ligne_interieure_Q(segs):
    """Le bout de la queue du Q DANS SA CONTREFORME : droit entre deux droits.

    Rend [5] dans les huit masters, sur le contour de creux. Sur le contour
    exterieur il rend [2], qui est le bout EXTERIEUR de la queue — celui que
    Nicolas a arbitre de ne pas toucher au trentieme tour, parce qu'il porte a
    la fois le ymin et le xmax du glyphe.

    IL TRAVAILLE SUR UN CONTOUR DE CREUX, ET C'EST UN ECART ASSUME. Le filtre
    sur le signe de l'aire, pose au dix-huitieme tour apres le piege du
    `Aogonek`, ecarte ces contours partout ailleurs dans le projet, et il le
    fait pour une bonne raison : il protege contre une coupe INVOLONTAIRE dans
    une contreforme. Ici la coupe est demandee. Le drapeau `sur_creux` ci-
    dessous leve le filtre pour ce localisateur SEUL, ce qui lie l'exception a
    l'objet qui la justifie au lieu de l'ecrire dans la table.
    """
    n = len(segs)
    return [i for i, s in enumerate(segs)
            if s["kind"] == "line"
            and segs[(i - 1) % n]["kind"] == "line"
            and segs[(i + 1) % n]["kind"] == "line"]


#: Le seul localisateur du projet autorise a designer un contour de creux.
#: Lu par `appliquer`, qui garde son filtre pour tous les autres.
loc_ligne_interieure_Q.sur_creux = True


# ------------------------------------------------------------ le catalogue
#
# nom du glyphe -> (localisateur, roulage)
# Le roulage vaut 1 pour les accents (bout roule) et 0 partout ailleurs.

CCW, CW = +1, -1

VISE_HAMPE = "vise_hampe"     # angle calcule pour que la coupe vise le fut

# --- les trois angles deduits du lot 5, trentieme tour.
#
# Comme `VISE_HAMPE`, ils ne sont pas des angles : ce sont des MARQUEURS, et
# l'angle est recalcule dans chaque master parce que la geometrie du glyphe
# change le long de l'axe. Le precedent est la queue du g, dont l'angle vaut
# 42,1 degres au Regular et 31,5 a l'ExtraBold en romain, 35,3 et 26,4 en
# italique, pour une seule et meme demande.
VISE_CENTRE = "vise_centre"   # la droite du bout passe par le centre de l'anneau
SUIT_BOUT = "suit_bout"       # le bout prend l'angle du bout de ronde du glyphe
VERTICALE_AXE = "verticale_axe"   # le bout devient vertical DANS L'AXE du dessin

#: La fraction de l'angle qui vise le centre, arretee par Nicolas au trentieme
#: tour SUR PLANCHE : a mi-chemin, et non au centre plein.
#:
#: Ce n'est pas un reglage esthetique seulement. Le prix du lot est une
#: OUVERTURE de couloir proportionnelle a la rotation, et la moitie d'angle le
#: divise par deux a trois : 0, 9, 43 et 72 paires ouvertes au-dela de 20 unites
#: dans les quatre masters romains, contre 15, 72, 127 et 128 au centre plein ;
#: le pire ecart tombe de 95 a 46 unites. Mesure sur l'etat ou les SEPT gestes
#: du lot coexistent, dans les deux sens de paire.
#:
#: Le Q ne la prend pas : sa coupe est verticale ou elle ne l'est pas, et une
#: demi-verticale ne veut rien dire.
PART_LOT5 = 0.5

POINTE = "pointe"             # roulage : pas de coupe du tout, un bout effile
BASCULE = "bascule"           # roulage : les deux coins bougent en sens contraire
SORTANTE = "sortante"         # roulage : un coin sort de son alignement
ALLONGE = "allonge"           # roulage : le bout est POUSSE, sans tourner


def valeur_master(theta, master, nom=""):
    """La valeur d'une entree, qui peut dependre du master.

    Toutes les entrees ecrites jusqu'au trentieme tour portent UN nombre pour
    les huit masters, et le point ouvert 51 dit pourquoi : le regime en unites
    est un choix de cadrage, rendu quatre fois par Nicolas. L'allongement du t
    est la premiere entree du projet qui porte une valeur PAR MASTER, et c'est
    aussi un arbitrage de Nicolas : la cible etant le sommet reel de la lettre
    et le levier de la bascule variant avec la graisse, un nombre unique
    donnerait huit hauteurs differentes.

    LEVE quand le master manque, et ne retombe pas sur zero. Un defaut
    silencieux rendrait une lettre non allongee sans que rien ne le dise, et le
    projet a deja paye plusieurs fois une valeur manquante prise pour une
    valeur nulle.
    """
    if not isinstance(theta, dict):
        return theta
    if master not in theta:
        raise ValueError(f"{nom} : aucune valeur pour le master {master!r} "
                         f"(la table en porte {sorted(theta)})")
    return theta[master]

# Quand le champ `sens` porte une de ces chaines au lieu de CCW ou CW, le sens
# de rotation est deduit du coin vise au lieu d'etre ecrit en dur. Un sens ecrit
# en dur est juste dans le master ou on l'a regarde et faux ailleurs des que la
# geometrie s'inverse le long de l'axe, ce qui est arrive six fois dans ce
# projet. Le coin, lui, se nomme et se verifie.
#
#   pour une coupe   : le coin nomme est celui qui RECULE dans la lettre
#   pour une bascule : le coin nomme est celui qui DESCEND
#   pour une sortante: le coin nomme est celui qui SORT
COINS = ("gauche", "droite", "haut", "bas")

# (glyphe, localisateur, sens, roulage, angle)
#
# `angle` vaut None pour l'angle general (20 degres), un nombre pour un angle
# propre au glyphe, ou VISE_HAMPE pour un angle recalcule dans chaque master.
#
# Les sens ne sont plus uniformes : ils ont ete tranches glyphe par glyphe sur
# planche. Le systeme tient par l'angle, 20 degres partout ; c'est le sens qui
# est choisi selon ce que la lettre demande.
#
# Un glyphe peut apparaitre deux fois : le g et le q recoivent un traitement
# sur leur queue et un autre sur le sommet de leur fut.

THETA_Q = 12.0        # le q est volontairement moins marque que le reste

# La queue du t ne peut pas prendre les 20 degres du l, et ce n'est pas un choix
# de dessin mais un plafond mesure. Son flanc voisin est le dessous du crochet,
# long de 30 unites pour un bout qui en fait 127 au Bold Italic : au-dela de
# 18,5 degres la droite de coupe ne rencontre plus ce flanc et l'operation
# refuse de s'executer. Plafonds par dichotomie sur les huit masters : romain
# 51,7 / 43,5 / 25,6 / 23,1, italique 43,0 / 30,5 / 18,5 / 16,7. Le plus bas
# commande, et 12 degres y laisse 4,7 degres de marge, la meme que celle que le
# lot 2 s'etait donnee.
#
# Ce plafond en a revele un autre, que personne n'avait mesure : le l, dont la
# passation annonce un plafond de 25 degres, est mesure en ROMAIN. En italique
# il tombe a 21,4 degres a l'ExtraBold. La coupe generale de 20 degres y passe
# avec 1,4 degre de marge et non 5, et c'est vrai depuis le lot 2.
THETA_T = 12.0

# L'allongement de la barre montante du t, tranche par Nicolas au
# trente-deuxieme tour sur `planche-lot6a-1-lectures.png` et ses trois voisines.
#
# LA DEMANDE. Que la barre montante atteigne le niveau des autres lettres
# hautes. Deux demandes independantes avaient ete faites sur le t ; la seconde,
# augmenter l'angle de la bascule, n'est PAS retenue a ce tour et la valeur de
# 20 degres ci-dessous ne bouge pas.
#
# LA CIBLE EST LE SOMMET REEL, ET C'EST L'ARBITRAGE. Quatre lectures ont ete
# dessinees, deux cibles (690 et 708, la hauteur des hampes) fois deux points
# mesures (la barre ou le sommet). Nicolas a retenu SOMMET A 690. La bascule
# releve un coin par-dessus l'allongement, de 10 a 30 unites selon la graisse,
# donc viser le sommet demande une valeur PAR MASTER — la premiere du projet.
# Ce que l'autre famille aurait donne, mesure : un allongement unique de 70
# unites met la barre a 690 partout et le sommet de 699,8 en ExtraLight a 720,0
# a l'ExtraBold, donc le t serait sous le l dans les clairs et 12 unites
# au-dessus dans les gras. C'est le defaut du point ouvert 51 transpose sur la
# hauteur : un nombre stable et un resultat qui ne l'est pas.
#
# LES VALEURS SONT CHERCHEES PAR DICHOTOMIE, pas deduites. Le sommet est affine
# en allongement a angle fixe, mais la relation passe par la bascule et une
# soustraction ne saurait pas le dire. `mesure_t.dist_pour_sommet` les rend, et
# les huit sont arrondies a l'entier : le sommet obtenu tient alors a 0,4 unite
# de la cible, ce qui est sous le dixieme de pixel a la taille de lecture.
#
# LA GEOMETRIE S'Y PRETE, ET C'EST POURQUOI L'OPERATION EST EXACTE. Le bout du
# fut est horizontal et ses deux flancs sont parfaitement verticaux de la
# hauteur d'x a 620 : `coupe.allonge` refuse les flancs courbes, donc elle ne
# s'appliquerait pas ailleurs sans mesure.
ALLONGE_T = {
    "ExtraLight": 60.0,
    "Regular": 55.0,
    "Bold": 42.0,
    "ExtraBold": 40.0,
    "ExtraLight Italic": 61.0,
    "Italic": 55.0,
    "Bold Italic": 41.0,
    "ExtraBold Italic": 38.0,
}
# Longueur de l'effilement, en epaisseurs de bout. Elle vaut plus sur la
# cedille, dont on veut un vrai crochet, que sur la virgule, qui doit garder
# assez de matiere pour rester distincte du point au corps du texte.
# (tirage, saillie) : longueur de l'effilement et avancee de la pointe,
# toutes deux en epaisseurs de bout. La saillie est ce qui rend la pointe
# franche : sans elle l'angle du bout reste plafonne par la longueur des
# flancs, 33 degres au mieux sur la cedille.
POINTE_CEDILLE = (3.5, 45.0)
POINTE_VIRGULE = (3.5, 55.0)

# Les deux reglages des crochets souscrits, tranches au dix-huitieme tour sur la
# planche `planche-lot4r-souscrits.png`. Ils portent les memes noms de grandeurs
# que les deux precedents, et pourtant aucun des deux ne s'y recopie : les trois
# crochets n'ont ni les memes flancs, ni le meme bout, ni la meme direction de
# saillie. Les chiffres sont volontairement ecrits ici et non deduits de
# POINTE_CEDILLE ou de POINTE_VIRGULE, pour qu'un futur reglage de la cedille ne
# deplace pas silencieusement l'ogonek.
#
# L'ogonek : la saillie de la cedille, telle quelle. Le tirage y est sature —
# ses flancs mesurent 49 et 34 unites en ExtraLight contre 66 et 81 pour la
# cedille, et 3,5 fois le bout demanderait 137 a 284 unites de recul. Seule la
# saillie agit. Le bout obtenu va de 25,3 a 41,2 degres selon le master, plus
# obtus donc que la cedille (15,9 a 25,2) : egaliser demanderait 91 a 108 unites
# de saillie et ferait sortir le crochet de 107 unites hors de sa chasse. La
# geometrie de l'ogonek interdit l'effilement de la cedille, et c'est assume.
# Prix paye a 45 : le crochet sort de 31 unites hors chasse au Regular et de 41
# a l'ExtraBold, contre 10 en dedans a l'etat brut. Aucun contact ni separation
# mesure sur cinq mots et quatre masters, et les approches du titrage sont a
# refaire de toute facon.
POINTE_OGONEK = (3.5, 45.0)

# La virgule souscrite : la saillie de la virgule, mais le quart de son tirage.
# Ses flancs font 132 et 224 unites pour un crochet de 194 de haut, si bien
# qu'un tirage de 3,5 recule chaque flanc de 85 % de sa longueur et pince le
# crochet — deux taches d'encre au lieu d'une au Bold et a l'ExtraBold, et
# jusqu'a six taches de plus dans SsTtGgKkLlNn a virgule. Le tirage 1,5 casse a
# l'autre bout de l'axe, en ExtraLight : sixieme inversion mesuree le long de
# l'axe de graisse. A 1,0 la topologie tient sur les quatre masters, le bas du
# glyphe reste a -249 quand le plancher de la police est a -250, et le bout
# tombe exactement dans la famille de la cedille : 19,7 degres contre 18,6 au
# Regular, 26,3 contre 25,2 a l'ExtraBold.
POINTE_VIRGULE_SOUS = (1.0, 55.0)

LOT2 = [
    # 1. accents : bout roule sur le coin obtus, la pointe est conservee.
    #    Les .case du circonflexe, du tilde, du caron, de la breve et du double
    #    accent aigu sont de simples composants translates : ils heritent.
    #    Huit .case ont leur propre trace dans les deux sources d'Atkinson :
    #    aigu, grave, point, rond, ogonek, strokeshortcomb, slashshortcomb et
    #    slashlongcomb. Le lot en coupe trois : l'aigu et le grave ici,
    #    l'ogonek en 3 bis.
    ("acutecomb",           loc_accent_bas,      CCW, 1.0, None),
    ("acutecomb.case",      loc_accent_bas,      CCW, 1.0, None),
    ("gravecomb",           loc_accent_bas,      CCW, 1.0, None),
    ("gravecomb.case",      loc_accent_bas,      CCW, 1.0, None),
    ("circumflexcomb",      loc_accent_bas,      CCW, 1.0, None),
    ("hungarumlautcomb",    loc_accent_bas,      CCW, 1.0, None),
    ("tildecomb",           loc_accent_bas,      CCW, 1.0, None),
    ("caroncomb",           loc_accent_haut,     CCW, 1.0, None),
    ("brevecomb",           loc_accent_haut,     CCW, 1.0, None),

    # 2. la virgule prend le meme traitement que les accents, sans pivot :
    #    le coin obtus de sa pointe est justement celui d'en bas a droite.
    ("comma",               loc_accent_bas,      CCW, POINTE, POINTE_VIRGULE),

    # 3. la cedille : meme loi, mais l'angle est pousse jusqu'a ce que le bout
    #    devienne une pointe. Ses deux flancs sont paralleles, on ne peut donc
    #    pas la rendre pointue en prolongeant les flancs jusqu'a leur
    #    intersection : il n'y en a pas. C'est la coupe elle-meme qui, tres
    #    inclinee, effile le bout.
    ("cedillacomb",         loc_bas,             CCW, POINTE, POINTE_CEDILLE),
    ("ccedilla",            loc_bas,             CCW, POINTE, POINTE_CEDILLE),
    #    Les cinq cedilles manquantes rejoignent la famille au dix-huitieme
    #    tour. Elles ne demandent aucun arbitrage : le reglage arrete du lot 2
    #    s'y applique tel quel, et `ccedilla` sert de temoin en tombant sur les
    #    memes chiffres. Angle de bout de 15,9 a 25,2 degres selon le master,
    #    identique aux six, boite et chasse inchangees, encre a +0,01 % pres,
    #    topologie 1/0, aucun contact dans FRANCAIS ni dans les mots roumains et
    #    turcs, a quatre masters et trois resolutions.
    #    `Tcedilla`, `Scedilla` et `scedilla` portent aussi en contours propres
    #    une lettre que la table traite ailleurs, sans en heriter : c'est un
    #    trou distinct, ouvert, et qui ne se comble pas par `loc_bas`.
    ("Ccedilla",            loc_bas,             CCW, POINTE, POINTE_CEDILLE),
    ("Scedilla",            loc_bas,             CCW, POINTE, POINTE_CEDILLE),
    ("scedilla",            loc_bas,             CCW, POINTE, POINTE_CEDILLE),
    ("Tcedilla",            loc_bas,             CCW, POINTE, POINTE_CEDILLE),
    ("tcedilla",            loc_bas,             CCW, POINTE, POINTE_CEDILLE),

    # 3 bis. l'ogonek, etat G1. Les trois combinants portent exactement le meme
    #    crochet — bout de 39 / 54 / 75 / 81 unites selon le master, identique
    #    aux trois — et ne different que par leur raccord haut, celui qui se
    #    soude a la lettre : d'ou trois traces et non un composant commun.
    #    `ogonekcomb.alt` manquait a l'inventaire de la passation.
    #    Les huit lettres portent le crochet en contours propres, colle dans le
    #    contour de la lettre : elles n'heritent de rien et se nomment.
    ("ogonekcomb",          loc_bas,             CCW, POINTE, POINTE_OGONEK),
    ("ogonekcomb.case",     loc_bas,             CCW, POINTE, POINTE_OGONEK),
    ("ogonekcomb.alt",      loc_bas,             CCW, POINTE, POINTE_OGONEK),
    ("Aogonek",             loc_bas,             CCW, POINTE, POINTE_OGONEK),
    ("aogonek",             loc_bas,             CCW, POINTE, POINTE_OGONEK),
    ("Eogonek",             loc_bas,             CCW, POINTE, POINTE_OGONEK),
    ("eogonek",             loc_bas,             CCW, POINTE, POINTE_OGONEK),
    ("Iogonek",             loc_bas,             CCW, POINTE, POINTE_OGONEK),
    ("iogonek",             loc_bas,             CCW, POINTE, POINTE_OGONEK),
    ("Uogonek",             loc_bas,             CCW, POINTE, POINTE_OGONEK),
    ("uogonek",             loc_bas,             CCW, POINTE, POINTE_OGONEK),

    # 3 ter. la virgule souscrite, etat V3. Un seul glyphe a traiter : les onze
    #    lettres de la famille — G K L N S T et leurs cinq bas de casse, plus le
    #    T roumain — la portent en composant et suivent sans etre nommees.
    #    `loc_accent_bas`, le localisateur de la virgule suscrite, ne convient
    #    pas ici : sur l'ogonek il designe le segment 5, qui est le raccord au
    #    corps de la lettre, et le couper ferait une entaille a la soudure. Un
    #    localisateur qui marche sur un glyphe ne marche pas sur un autre de la
    #    meme famille.
    ("commaaccentcomb",     loc_bas,             CCW, POINTE, POINTE_VIRGULE_SOUS),

    # 4. pentes et queues
    ("idotless",            loc_gauche,          CW,  0.0, None),
    ("jdotless",            loc_gauche,          CCW, 0.0, None),
    ("l",                   loc_droite,          CCW, 0.0, None),

    # 5. barres. Le sens est horaire, et les longueurs sont calculees pour que
    #    les coupes du F soient deux morceaux d'une meme droite. Voir barres().
    ("F",                   loc_barres_F,        CW,  0.0, None),
    ("E",                   loc_barres_E,        CW,  0.0, None),
    #    L'Æ ET L'Œ, QUARANTE-NEUVIEME TOUR, demandes par Nicolas sur la
    #    planche du repertoire entier. Les deux DESSINENT un E sous un autre
    #    nom -- deux contours propres chacun, aucun composant -- donc une table
    #    indexee par nom ne les atteint pas. C'est la CINQUIEME forme du meme
    #    defaut dans ce projet, apres `e.sc` qui gardait un geste que le E
    #    n'avait plus, l'Æ et l'Aring dont le pied plongeait faute de suivre la
    #    prescription du A, et le double `.ti` qui perdait la sienne. Les
    #    quatre premieres fois, c'est Nicolas qui a vu la forme sur une
    #    planche ; la cinquieme aussi.
    #
    #    A NE PAS CONFONDRE AVEC LA DEROGATION DU TRENTE-NEUVIEME TOUR. `AE` et
    #    `OE` portent `sortantes=()` dans `lot4.PRESCRIPTIONS`, ce qui les
    #    ecarte du reglage de TITRAGE, et cette decision-la tient. Ce qui est
    #    ecrit ici est la coupe TEXTE du lot 2, celle que le E porte depuis le
    #    troisieme tour et que personne n'avait portee sur ces deux-la.
    #
    #    `loc_barres_E` S'Y APPLIQUE TEL QUEL, et c'est mesure sur les huit
    #    masters des deux sources avant d'etre ecrit : il designe les trois
    #    memes bouts de barre, aux memes ordonnees et a la meme longueur que
    #    sur le E. Sur l'Æ il attrape en plus le flanc du A, long de 0,415 a
    #    0,50 fois la hauteur de capitale quand le plus long BOUT de barre en
    #    fait 0,225 -- mais ce flanc vit dans le contour NEGATIF de la
    #    contreforme du A, que `appliquer` ecarte par son filtre sur le signe
    #    de l'aire depuis le dix-huitieme tour. Verifie par la mesure et non
    #    par le raisonnement : trois noeuds bougent sur l'Æ au Regular, aux
    #    ordonnees 0, 303 et 587, et AUCUN autre glyphe du repertoire ne bouge
    #    d'un centieme. La marge entre 0,225 et 0,415 est la reserve qui reste
    #    si un jour un flanc long arrivait dans un contour positif.
    #
    # VALIDES PAR NICOLAS EN NAVIGATEUR, sur `gabarits/tour49.html` et sur le
    # BINAIRE SERVI : les deux lettres dans des mots ("sœur", "cœur", "bœuf",
    # "œuvre"), puis en capitales, puis en regard du E aux quatre masters. Ou
    # le regard a eu lieu compte autant que le regard, et ce projet a revise le
    # i, le k, le 1 et `idotless` apres les avoir valides sur une planche.
    ("AE",                  loc_barres_E,        CW,  0.0, None),
    ("OE",                  loc_barres_E,        CW,  0.0, None),
    #    Le T et le Z rejoignent la famille au onzieme tour. Ils avaient ete
    #    ecartes par un critere d'inventaire trop prudent, pas par un risque :
    #    leurs bouts de barre sont verticaux, donc le coin mobile coulisse le
    #    long d'une arete horizontale et la montee est exactement nulle. Ni la
    #    hauteur de capitale, ni la ligne de base, ni la boite, ni la chasse ne
    #    bougent — verifie sur les quatre masters romains. Ce que la coupe
    #    coute, c'est de l'encre : 1,4 a 4,6 % sur le T, 1,1 a 3,4 % sur le Z.
    #    C'est cette perte qui prouve que la coupe a bien eu lieu, la boite ne
    #    le dirait pas.
    ("T",                   loc_barres_T,        CW,  0.0, None),
    #    LE TCEDILLA CAPITALE RECOIT LES DEUX BOUTS DE BARRE DU T, meme
    #    localisateur et meme sens. Trente-neuvieme tour, meme cause que son bas
    #    de casse : trace propre, sans composant, donc rien ne se propage. LE
    #    POINT 29 NE LE NOMMAIT PAS -- il nommait `tcommaaccent`, qui est un
    #    COMPOSITE de `t` et `commaaccentcomb` et n'a donc besoin de rien. Les
    #    deux erreurs ont ete trouvees en mesurant, pas en relisant le point.
    #    `loc_barres_T` rend les memes deux segments sur la base et sur le
    #    compose dans les huit masters.
    ("Tcedilla",            loc_barres_T,        CW,  0.0, None),
    ("Z",                   loc_bouts_Z,         CW,  0.0, None),
    ("L",                   loc_droite,          CW,  0.25, None),
    ("S",                   loc_terminaisons_S,  CCW, 0.0, None),
    ("s",                   loc_terminaisons_S,  CCW, 0.0, None),

    # 6. g et q : queue puis sommet du fut.
    #    Sur le g le sommet du fut baisse a gauche, sur le q il baisse a droite.
    #    Ce sont deux gestes differents, pas deux miroirs : d'ou deux sens.
    #    La coupe de la queue du g ne prend pas l'angle general : elle est
    #    calculee pour viser le sommet du fut, ce qui donne, du Regular a
    #    l'ExtraBold, 42,1 a 31,5 degres en romain et 35,3 a 26,4 en italique.
    ("g",                   loc_queue_g,         CCW, 0.0, VISE_HAMPE),
    ("g",                   loc_hampe,           CCW, 0.0, None),
    ("q",                   loc_droite,          CW,  0.0, THETA_Q),
    ("q",                   loc_hampe,           CW,  0.0, THETA_Q),

    # 7. les six terminaisons demandees par Nicolas sur le specimen du corpus,
    #    instruites au vingtieme tour, tranchees au vingt-et-unieme, ecrites au
    #    vingt-deuxieme. Le r n'y est pas : Nicolas a d'abord demande une coupe
    #    de son bras, puis un R reduit a l'echelle d'une minuscule, puis a
    #    retenu le r d'Atkinson tel quel. Sa forme ne change pas.
    #
    #    Deux d'entre elles franchissent un alignement, ce que la loi de ce
    #    module s'interdit depuis le lot 2, et c'est assume glyphe par glyphe :
    #    le sommet du fut du t bascule au-dessus de 620, qui ne porte aucun
    #    alignement, et le pied droit du n plonge sous la ligne de base, qui en
    #    porte un. Le second est une vraie exception, prise en connaissance de
    #    cause, et le lot 4 fait deja ce geste en titrage.
    #
    #    Les angles sont a 12 degres sur le n et le m et non a 20 : le sommet du
    #    fut porte la hauteur d'x, et a 12 degres le coin qui monte reste sous le
    #    debord optique de l'epaule dans les quatre masters, donc la boite du
    #    glyphe ne bouge pas d'un dixieme. A 20 degres elle bouge dans les gras.
    ("n",                   loc_sommet_fut,      "gauche", 0.0, 12.0),
    ("m",                   loc_sommet_fut,      "gauche", 0.0, 12.0),
    #    La pointe du pied droit du n plonge de 22 unites. La plongee est en
    #    unites et la largeur du pied ne l'est pas, 54 en ExtraLight contre 152
    #    au Bold : le pied penche donc de 22 degres dans le premier et de 8 dans
    #    le second. C'est un fait mesure et non un defaut, mais il est a
    #    connaitre avant de changer la valeur.
    ("n",                   loc_pied_droit,      "droite", SORTANTE, 22.0),
    #    La queue du t prend le geste du l : meme sens, le coin haut recule.
    #    `loc_droite`, le localisateur du l, bascule d'un master a l'autre sur le
    #    t — voir `loc_queue_t`. L'angle, lui, ne peut pas etre celui du l :
    #    voir THETA_T, c'est un plafond mesure et non un choix.
    ("t",                   loc_queue_t,         "haut",   0.0, THETA_T),
    #    L'ALLONGEMENT DE LA BARRE MONTANTE PASSE AVANT LA BASCULE, et l'ordre
    #    n'est pas une preference. Apres allongement le bout reste horizontal,
    #    donc `loc_sommet_fut` le retrouve ; apres bascule il ne l'est plus, et
    #    l'ordre inverse leve « vecteur nul » dans les quatre masters romains.
    #    Rejoue au trente-deuxieme tour par `mesure_t.verif_ordre` : un refus
    #    franc, donc pas de lettre plausible et fausse.
    ("t",                   loc_sommet_fut,      "gauche", ALLONGE, ALLONGE_T),
    #    Le sommet du fut du t bascule : le coin gauche descend, le coin droit
    #    monte. La lettre gagne 15 unites de hauteur au Regular et 28 au Bold.
    ("t",                   loc_sommet_fut,      "gauche", BASCULE, 20.0),
    #    LE TCEDILLA RECOIT LES TROIS GESTES DU T, dans le meme ordre et avec
    #    les memes valeurs. Point 29, tranche au trente-troisieme tour, ecrit au
    #    trente-neuvieme. Son trace est PROPRE, sans composant : rien ne se
    #    propage, donc sans ces trois lignes un t vaut 690 et un ț 620 dans les
    #    huit masters.
    #
    #    LES LOCALISATEURS NE DERAPENT PAS, et c'est mesure sur les HUIT
    #    masters avant d'ecrire : `loc_queue_t` et `loc_sommet_fut` designent
    #    exactement le meme segment que sur le t, aux memes coordonnees. Seul
    #    l'INDICE change -- i6 au lieu de i1 -- parce que le crochet ajoute des
    #    segments au contour, et c'est precisement pourquoi le projet localise
    #    par position. Le point 29 annoncait qu'il faudrait des localisateurs
    #    restreints : c'est faux ici, et vrai pour l'Eogonek, le Scedilla et le
    #    scedilla, qui restent en limite connue.
    #
    #    AUCUN EFFET SERVI : ni U+0162, ni U+0163, ni U+021A, ni U+021B ne sont
    #    dans le binaire, cmap et glyphes verifies dans les deux sources. C'est
    #    la coherence du depot publie, ou quelqu'un peut recompiler sans le
    #    filtre de glyphes.
    ("tcedilla",            loc_queue_t,         "haut",   0.0, THETA_T),
    ("tcedilla",            loc_sommet_fut,      "gauche", ALLONGE, ALLONGE_T),
    ("tcedilla",            loc_sommet_fut,      "gauche", BASCULE, 20.0),
    #    Le bout du crochet du f avance de 25 unites vers la droite. Le f a 28
    #    unites d'approche droite au Regular : l'avance les mange sans les
    #    depasser, sauf d'une unite a l'ExtraBold. A 40 elle sortait de 10 a 16
    #    unites hors de la chasse.
    ("f",                   loc_haut_vertical,   "haut",   SORTANTE, 25.0),

    # 8. le lot 1 du vingt-cinquieme tour : les trois pieds gauches qui
    #    descendent sous la ligne de base. Demandes par Nicolas sur la planche
    #    d'alphabet, instruits par `balayage_lot1.py`, tranches sur
    #    `planche-lot4z-1-m-pointe.png` et ses deux voisines.
    #
    #    Le geste est celui du pied droit du n, en miroir : le coin bas gauche
    #    sort de la ligne de base en coulissant le long du flanc gauche du fut.
    #
    #    CE QUE LE PRIX EST, mesure sur les trois glyphes et quatre profondeurs.
    #    En romain la boite ne s'elargit d'aucune unite : le flanc gauche est
    #    vertical a 0,0 degre, donc le coin descend tout droit. En italique il
    #    penche de 12 degres, la boite s'elargit de 2,5 a 6,7 unites vers la
    #    gauche, et la plongee reelle vaut 21,5 unites pour une cible de 22 —
    #    `angle_pour_sortie` vise le chemin parcouru par le coin, pas sa
    #    composante verticale. **Le pied droit du n est dans ce cas depuis le
    #    vingt-deuxieme tour**, et le vingt-cinquieme est le premier a le
    #    mesurer : la passation affirmait que la boite ne bougeait pas, ce qui
    #    n'etait vrai qu'en romain.
    #
    #    LES TROIS VALEURS NE SONT PAS UNIFORMES, et c'est le choix de Nicolas.
    #    Le m prend 22, la valeur du n, donc la symetrie est exacte. Le M et le f
    #    prennent 32, la valeur des bas de casse en titrage. Douze unites a ete
    #    ecarte par la mesure et non par le gout : a cette profondeur le geste
    #    ne gagne rien sur la paire rn/m, et il rend un millieme de moins au
    #    Bold et a l'ExtraBold Italic.
    #
    #    CE QUE LA POINTE DU m ACHETE, mesure sur l'etat servi, crenage r+n a
    #    +20 compris : rn/m gagne +0,031 en ExtraLight et +0,008 au Bold a 22
    #    unites. La paire reste sous la reference de son master dans les quatre
    #    masters romains, de 0,025 a 0,057. Le geste ameliore la paire partout
    #    et ne la sauve nulle part, et c'est le seul levier de forme qui restait
    #    depuis que le r garde celui d'Atkinson.
    #
    #    POINT OUVERT QUE CES TROIS ENTREES FIGENT PAR DEFAUT. La plongee est en
    #    unites et la largeur du pied ne l'est pas, 54 en ExtraLight contre 165 a
    #    l'ExtraBold : a 22 unites le pied penche de 22 degres dans le premier et
    #    de 7,6 dans le second. Le geste est trois fois plus aigu dans les
    #    clairs. Le vingt-et-unieme tour l'avait releve sur le n, et le choix
    #    entre plongee constante et angle constant n'est pas fait.
    ("m",                   loc_pied_gauche,     "gauche", SORTANTE, 22.0),
    ("M",                   loc_pied_gauche,     "gauche", SORTANTE, 32.0),
    ("f",                   loc_pied_gauche,     "gauche", SORTANTE, 32.0),

    # 9. le lot 2 du vingt-cinquieme tour : les rentrants. Demandes par Nicolas
    #    sur la planche d'alphabet, instruits par `balayage_lot2.py`, tranches
    #    sur `planche-lot4za-1-b-hampe.png` et ses trois voisines.
    #
    #    Un coin recule, l'autre tient l'alignement. Le precedent est le sommet
    #    du fut du g et du q, exception assumee au perimetre depuis le lot 2 :
    #    la coupe porte un alignement, et c'est le coin qui ne bouge pas qui l'y
    #    tient.
    #
    #    L'ALIGNEMENT PORTE EST 708 ET NON 796. La passation annonçait
    #    l'ascendante. Mesure sur les huit masters : b, d, h, k, l montent a 708
    #    exactement, et aucune lettre de la police n'atteint 796, qui est une
    #    metrique de ligne. Le f monte a 716 ou 718 par le debord de son crochet
    #    courbe, comme le O a 680 pour une capitale de 668. Le lot 4 en aura
    #    besoin : le h et le k qu'il doit faire monter franchissent 708, avec 88
    #    unites de marge jusqu'a l'ascendante declaree.
    #
    #    CE QUE LE PRIX EST, mesure sur les huit masters et les deux angles
    #    candidats. Boite inchangee sur ses quatre cotes, hors chasse nul,
    #    plafond de coupe au-dela de 60 degres sur les quatre cibles, topologie
    #    stable entre 900 et 1800 pixels. La lettre ne peut que maigrir : c'est
    #    la propriete du pivot que la loi choisit, et elle est verifiee ici et
    #    non heritee.
    #
    #    POINT OUVERT QUE CES ENTREES FIGENT PAR DEFAUT, le meme que celui des
    #    trois pieds gauches, pris par l'autre bout. Ici l'angle est constant et
    #    la largeur du bout ne l'est pas, 54 unites en ExtraLight contre 165 a
    #    l'ExtraBold : le coin descend donc de 19,7 unites dans le premier et de
    #    60,1 dans le second, trois fois plus. Le choix entre angle constant et
    #    retrait constant n'est pas fait.
    ("b",                   loc_sommet_fut,      "droite", 0.0, 20.0),
    #    Le miroir exact du b, et c'est la demande : sur le b le coin droit
    #    descend, sur le d le coin gauche. Les deux lettres se lisent alors en
    #    symetrie, ce qui va dans le sens de la distinction b/d et non contre
    #    elle — les deux appartiennent au groupe confusable b/d/p/q. Leurs
    #    chiffres d'encre tombent a 0,02 % l'un de l'autre, ce qui est la
    #    confirmation numerique du miroir.
    ("d",                   loc_sommet_fut,      "gauche", 0.0, 20.0),
    #    Le l est la premiere lettre du projet coupee aux deux bouts : sa queue
    #    porte `loc_droite` depuis le lot 2, et ce bout-ci est le haut de la
    #    meme hampe. Deux entrees sur un meme glyphe, ce que `appliquer_lot`
    #    traite en les appliquant l'une apres l'autre.
    #
    #    Attention en relisant les chiffres du l : il perd 1,38 a 4,22 % d'encre
    #    sur l'etat servi et 1,37 a 4,11 % depuis la source brute. Les deux sont
    #    justes, la perte relative etant plus forte sur une lettre dont la queue
    #    est deja coupee. Le plafond de coupe de CE bout est au-dela de 60
    #    degres ; celui de sa queue tombe a 21,4 en ExtraBold Italic, et c'est
    #    le maillon court du projet, point ouvert 37.
    ("l",                   loc_sommet_fut,      "droite", 0.0, 20.0),
    #    Le z recoit ce que le Z a depuis le onzieme tour : ses deux bouts
    #    libres, celui de la barre haute a gauche et celui de la barre basse a
    #    droite, sens horaire. Ses jonctions de diagonale restent intactes, ce
    #    ne sont pas des bouts de trait.
    #
    #    L'ORDONNEE NE BOUGE PAS D'UN CENTIEME : ces bouts sont verticaux, le
    #    coin coulisse le long d'une arete horizontale, donc la hauteur d'x et
    #    la ligne de base restent atteintes. C'est ce qui avait fait entrer le T
    #    et le Z dans la coupe texte, verifie ici sur le z. La seule grandeur
    #    qui prouve que la coupe a eu lieu est la perte d'encre, de 0,84 a
    #    2,09 % a 12 degres.
    #
    #    L'ANGLE EST 12 ET NON 20, ET C'EST UN CHOIX D'ESPACEMENT. Le z est la
    #    seule des quatre cibles dont les bouts sont sur les flancs exterieurs
    #    de la lettre : les couper recule un bord, donc ouvre un couloir, comme
    #    la barre mediane du F et la queue du l. Mesure sur la bande pleine et
    #    les 71 voisins : a 20 degres, 10 a 13 paires par master s'ouvrent de 27
    #    a 47 unites ; a 12 degres, les deux masters clairs ne bougent plus du
    #    tout et les gras gardent 11 a 12 paires a +26.
    #
    #    L'OUVERTURE RESTANTE EST UN POINT OUVERT, groupe avec le s (point 47)
    #    et le l (point 39) : les trois demandent le meme geste, une table de
    #    paires bornee sur un bout coupe, et une seule passe les traite mieux
    #    que trois. Les paires touchees sont y+z, Y+z, z+A, z+X, z+AE et
    #    quoteright+z, et aucune n'apparait dans les 1 966 mots des gabarits.
    ("z",                   loc_bouts_Z,         CW,       0.0, 12.0),
    # LOT 3 DES VINGT-DEUX GESTES, vingt-septieme tour : la descendante, et ce
    # qui n'en est pas. Trois cibles, trois familles, et deux alignements.
    #
    # DEUX CHIFFRES DE LA PASSATION SONT FAUX, ET LES ENTREES REPOSENT SUR LES
    # VALEURS MESUREES. Le point ouvert 20 annonce que « les jambes du p, du q,
    # du y, du j et du g se terminent a −251 ». Mesure sur les huit masters : le
    # p, le y et `jdotless` s'arretent a −162, le q a −172 a −174, le g a −186 a
    # −205 par le debord de leurs courbes. Aucune lettre n'atteint −251, qui est
    # le `descender` declare. Et l'ymin du Y vaut 0,0 : **le Y ne descend pas**,
    # son pied est pose sur la ligne de base, donc il releve de la famille du
    # lot 1 et non de celle du p.
    #
    # LA DEMANDE N'AVAIT PAS DEUX LECTURES, ET C'EST LA GEOMETRIE QUI L'A DIT.
    # « Le cote bas depasse vers la gauche » paraissait se lire comme une
    # plongee ou comme une avance laterale. Le coin sortant coulisse le long du
    # flanc voisin PROLONGE : sur le p et le Y le bout est horizontal et ses
    # deux flancs sont verticaux, donc tout coin qui sort plonge ; sur le y le
    # bout est vertical et ses deux flancs sont horizontaux, donc tout coin qui
    # sort avance. Ce qui restait a trancher etait lequel des deux coins sort.
    #
    # Le defaut qui l'a revele est corrige a la source, dans
    # `_coin_vise_est_P` : un nom de coin que le bout ne departage pas etait
    # accepte et designait l'autre coin en silence, et la mesure rendait le meme
    # deplacement pour les deux « lectures ».
    #
    # LE POINT OUVERT 21 EST CHIFFRE ET IL NE MORD PAS. Le glyphe le plus bas du
    # repertoire servi n'est pas le p, c'est le g. Le p a donc 24 unites de
    # plongee gratuite en ExtraLight, 30 au Regular, 41 au Bold, 43 a
    # l'ExtraBold : a 24 le jour d'interligne ne bouge pas d'un dixieme, a
    # aucune des quatre valeurs du CSS du site. Le y ne descend pas d'une unite,
    # donc l'interligne l'ignore. Le Y peut plonger de 186 unites avant de
    # devenir le plancher.
    #
    #    Le p a 24 unites : la valeur que Nicolas a retenue, et elle tombe sur
    #    `approches.JOUR_MIN`, deux fois le debord optique des rondes, le seuil
    #    que le projet emploie depuis le dix-septieme tour. Que ce chiffre soit
    #    aussi la plongee gratuite de l'ExtraLight est une coincidence mesuree
    #    et non un raisonnement.
    #
    #    Le geste ne coute rien : boite inchangee en romain, le flanc du fut
    #    etant vertical a 0,0 degre ; en italique elle gagne 5,0 unites vers la
    #    gauche, le flanc penchant de 78 degres, et la plongee reelle vaut 23,5
    #    pour une cible de 24, `angle_pour_sortie` visant le chemin parcouru par
    #    le coin. Hors chasse nul, topologie stable aux deux resolutions, zero
    #    paire resserree sur les 71 voisins et les huit masters.
    #
    #    POINT OUVERT QUE CETTE ENTREE FIGE PAR DEFAUT, le meme que celui du
    #    pied du n et des rentrants du lot 2 : la plongee est en unites et la
    #    largeur du bout ne l'est pas, 54 en ExtraLight contre 165 a
    #    l'ExtraBold, donc le pied penche de 24,0 degres dans le premier et de
    #    8,3 dans le second. Le regime a angle constant a ete mesure et il
    #    ecarte 20 degres : la sortie y va de 19,6 a 60,0 unites, ce qui met le
    #    p a −222, 17 unites sous le g. A 12 degres il tient sur les quatre
    #    masters, de 11,4 a 35,1 unites. Le choix n'est pas fait.
    ("p",                   loc_bout_jambe,      "gauche", "sortante", 24.0),
    #    Le y a 40 unites, et c'est LA SEULE DES TROIS QUI COUTE UN ESPACEMENT.
    #    Nicolas a demande « Qy4+ », plus que le plus grand des candidats
    #    mesures : 40 a donc ete mesure apres coup, et le prix est ecrit.
    #
    #    Le bout est vertical, donc le coin avance lateralement et n'approche
    #    aucun alignement : l'ordonnee du glyphe ne bouge pas d'un centieme,
    #    l'interligne l'ignore, et le hors chasse ne bouge pas non plus — les 43
    #    unites du y italique sont son etat d'origine, la lettre penchee sortant
    #    deja de sa chasse dans Atkinson. Ce que le geste deplace est la boite,
    #    de 18 unites vers la gauche en ExtraLight romain et de 40 en italique.
    #
    #    LE PRIX, mesure sur l'etat servi et non sur Atkinson brut : `q+y` passe
    #    sous le plancher de 24 unites dans les huit masters et en contact dans
    #    les deux ExtraLight, a −9,7 et −8,9 ; `parenleft+y` passe sous le
    #    plancher en ExtraLight Italic, a 14,6. La queue du q descend a droite,
    #    le bout du y avance a gauche, et les deux se croisent : c'est le
    #    mecanisme du lot 1 sur `q+m` et `q+M`. **La table `paires_y.py` le
    #    ferme**, par le meme critere que le point 50.
    #
    #    La reference compte, et le premier jet du garde-fou l'avait fausse : il
    #    mesurait contre Atkinson brut, ou la queue du q n'a pas encore sa coupe
    #    du lot 2, ce qui ouvre le couloir de 1 a 6 unites. La planche l'a
    #    revele en rendant `q+y` a 36 unites au Bold quand le balayage disait
    #    30. C'est l'etat servi qui fait foi.
    #
    #    Ce que le corpus dit, et il ne dit pas la meme chose des deux paires :
    #    aucune occurrence de `q+y` dans les 13 752 caracteres des gabarits, le
    #    q francais etant toujours suivi d'un u sauf en fin de mot. Une
    #    parenthese ouvrante devant un y, elle, existe, dans « (y compris ».
    ("y",                   loc_bout_queue_y,    "bas",    "sortante", 40.0),
    #    Le Y a 44 unites PAR SON COIN DROIT, choix de Nicolas contre la
    #    symetrie du y : sur le y c'est le bout bas qui avance vers la gauche,
    #    sur le Y c'est le cote droit du pied qui descend. Les deux lettres ne
    #    se lisent donc pas en miroir, et c'est assume.
    #
    #    44 est la valeur des capitales en titrage, celle de la prescription du
    #    Y dans `lot4.PRESCRIPTIONS` depuis le onzieme tour. La question de
    #    savoir si une capitale plonge de la valeur d'un bas de casse ou de la
    #    sienne est donc tranchee ici comme le lot 4 l'avait tranchee pour
    #    lui-meme : de la sienne, sur un argument de proportion.
    #
    #    Le coin droit n'avait jamais ete mesure au-dela de 24 unites, et le
    #    garde-fou n'avait teste que le coin gauche : le coin droit descend du
    #    cote de la lettre SUIVANTE, donc son voisinage n'est pas le meme et le
    #    zero du gauche n'en disait rien. Mesure : zero paire resserree dans les
    #    huit masters, boite inchangee d'aucune unite meme a 44, hors chasse
    #    inchange. La raison est de position — le pied du Y est le bout du fut,
    #    entre les deux bras, donc son coin descend le long d'un flanc interieur
    #    et ne s'approche d'aucun voisin.
    #
    #    Deux paires sont deja sous le plancher dans Atkinson, sans rapport avec
    #    le geste et relevees en passant : `f+Y` a 9,5 unites a l'ExtraBold et
    #    `eacute+Y` a 9,4 a l'ExtraBold Italic.
    ("Y",                   loc_pied_Y,          "droite", "sortante", 44.0),
    # --- Lot 4a du vingt-cinquieme tour, ecrit au vingt-huitieme : les
    #     depassements PAR LE HAUT, et les deux pieds de capitale qui les
    #     accompagnent.
    #
    #     **C'EST LE PREMIER GESTE DU PROJET QUI SORT VERS LE HAUT.** Rien de la
    #     coupe texte ne le fait : les six terminaisons du vingt-deuxieme tour,
    #     les dix-sept souscrits, les trois pieds du lot 1, les quatre rentrants
    #     du lot 2 et les trois descendantes du lot 3 vont vers le bas, vers
    #     l'interieur ou lateralement. Le risque change de nature et il est
    #     DOUBLE : le voisin lateral en haut, et la descendante de la LIGNE
    #     AU-DESSUS, qui n'est pas un voisin et qu'aucune mesure de paire ne peut
    #     voir. Les deux sont mesures, par deux passes distinctes de
    #     `balayage_lot4.py`, et aucun ne mord.
    #
    #     L'INTERLIGNE NE COUTE RIEN, et c'est la reponse symetrique du point
    #     ouvert 21. Montee gratuite avant de devenir le plafond du repertoire
    #     servi : 130 unites en ExtraLight et au Regular, 153 au Bold, 157 a
    #     l'ExtraBold pour le h et le k ; 170 a 197 pour le N et le H. Sur les 88
    #     etats mesures aux quatre interlignes du CSS du site, aucun n'entame le
    #     jour.
    #
    #     UN CHIFFRE DE LA PASSATION ETAIT FAUX : le plafond du repertoire servi
    #     n'est pas `Aring` dans tous les masters. Mesure, composites decomposes,
    #     il vaut 838,0 en ExtraLight porte par `bar` et `brokenbar`, `Aring`
    #     n'y etant qu'a 835,0 ; 838,0 au Regular ou les trois sont a egalite ;
    #     861,0 au Bold et 865,0 a l'ExtraBold, portes par `Aring`. La barre
    #     verticale ne varie pas le long de l'axe, l'anneau du A monte avec la
    #     graisse, et les deux se croisent entre le Regular et le Bold.
    #
    #     LE REGIME EST EN UNITES, choix de cadrage de Nicolas : le point ouvert
    #     51 reste ouvert et fige par defaut en unites, comme les lots 1 a 3.
    #
    #     Le h et le k prennent 32 unites, la valeur des bas de casse en
    #     titrage ; le N et le H prennent 24, `approches.JOUR_MIN`, deux fois le
    #     debord optique des rondes. Nicolas a donc ecarte les 44 unites des
    #     capitales en titrage sur ces deux lettres : le geste y reste sous le
    #     seuil que le projet emploie depuis le dix-septieme tour, et il est plus
    #     discret que celui des deux minuscules.
    #
    #     Le bout de hampe du h et du k est a 708 et non a 796, confirme sur les
    #     huit masters : 796 est une metrique de ligne qu'aucune lettre de la
    #     police n'atteint, et il reste 88 unites de marge. Meme bout et meme
    #     localisateur que le b, le d et le l du lot 2 ; c'est le SENS qui
    #     s'inverse, le coin sortant au lieu de rentrer.
    #
    #     LE h ET LE k NE COUTENT RIEN, ET C'EST PLUS QUE PREVU. La boite ne
    #     bouge d'aucune unite, romain compris ET italique compris. En italique
    #     le flanc du fut penche a 78 degres, donc le coin part de cote et la
    #     boite devrait s'elargir comme celle du pied gauche du m au lot 1 : elle
    #     ne bouge pas parce que le point le plus a droite du h est son fut droit
    #     et celui du k son bras, jamais le bout de hampe. Fait de ces deux
    #     lettres, pas propriete du flanc. Une seule paire se resserre, `f+h` de
    #     0,6 unite et `f+k` de 2,2 a 4,5, et elles restent entre 49 et 86.
    ("h",                   loc_sommet_fut,      "droite", SORTANTE, 32.0),
    ("k",                   loc_sommet_fut,      "gauche", SORTANTE, 32.0),
    #     LE N ET LE H PRENNENT bg + hd, LA DIAGONALE DU TITRAGE. La demande du
    #     vingt-cinquieme tour dit « H en haut a gauche et en bas a droite »,
    #     soit hg + bd ; la prescription arretee au neuvieme tour tient « bg et
    #     hd seulement, comme le N ». Ce sont les deux diagonales OPPOSEES du
    #     meme glyphe, et Nicolas a tranche pour celle du titrage. La demande sur
    #     le N ne nommait que « en haut a droite » : il a retenu le N symetrique
    #     du H, donc les deux bouts.
    #
    #     UN LOCALISATEUR NOUVEAU, `loc_sommet_droit`, ET IL N'EST PAS DU ZELE.
    #     `loc_sommet_fut` rend le bon segment sur le N et le H et il le rend PAR
    #     ACCIDENT : les deux ont DEUX bouts horizontaux exactement a 668 — les
    #     sommets des deux futs du H, de meme longueur a l'unite pres, et sur le N
    #     le sommet du fut droit face a la jonction de sa diagonale. `max` sur
    #     une egalite parfaite rend le premier dans l'ordre du contour, et il se
    #     trouve etre le bon sur les huit masters des deux sources. Rien ne le
    #     garantit : c'est le defaut de `loc_bas`, releve au vingt-et-unieme
    #     tour.
    #
    #     LES SOMMETS NE COUTENT RIEN EN ROMAIN ET COUTENT EN ITALIQUE, et la
    #     raison est l'inverse de celle du h : le sommet du fut droit EST le point
    #     le plus a droite de la capitale italique. Boite inchangee sur les
    #     quatre cotes en romain ; en italique elle gagne 5,0 unites vers la
    #     droite a 24 u et la matiere sort de la chasse d'autant. Zero paire sous
    #     le plancher ; `N+j` et `H+j` se resserrent de 2 a 3 unites en Bold et
    #     ExtraBold Italic et restent a 90–94.
    ("N",                   loc_sommet_droit,    "droite", SORTANTE, 24.0),
    ("H",                   loc_sommet_droit,    "droite", SORTANTE, 24.0),
    #     LES DEUX PIEDS REJOUENT EXACTEMENT LE DEFAUT DU LOT 1, ET LA TABLE LE
    #     FERME. `q+N` et `q+H` passent de 100,0 a −18,9 unites de couloir en
    #     **ExtraBold romain**, et dans ce master seul a 24 unites. Meme
    #     mecanisme que le `q+M` du lot 1, aux memes chiffres : la queue du q
    #     descend a DROITE, le pied du fut gauche descend a GAUCHE, et les deux se
    #     croisent. `approches.CIBLES_PIEDS` recoit donc le N et le H, et
    #     `paires_pieds.py` est regenere par `inventaire_pieds.py --ecrire` : le
    #     critere est le plancher de jour de 24 unites du point ouvert 50, et non
    #     « jamais plus serre qu'Atkinson ».
    #
    #     DEUX FAITS DE CE CONTACT MERITENT D'ETRE ECRITS. Le franchissement se
    #     fait entre 12 et 22 unites en ExtraBold, et au-dela la valeur SATURE a
    #     −18,9 : 24 unites coutent donc exactement ce que couteraient 44 sur ce
    #     master, et 12 ne couteraient rien du tout. Et le contact est en
    #     ExtraBold ROMAIN quand l'ExtraBold ITALIQUE tient a 74,1 — l'inclinaison
    #     ecarte les deux lettres au lieu de les rapprocher, ce qui est l'inverse
    #     de ce que les sept inversions d'axe de ce projet laissaient attendre.
    #
    #     Ce que le corpus dit : aucun des mots des quatre gabarits ne porte
    #     `q+N` ni `q+H`, le q francais etant toujours suivi d'un u sauf en fin de
    #     mot, et un q minuscule devant une capitale n'existe pas dans un texte
    #     courant. Le defaut serait geometrique et sans occurrence, comme le S
    #     capitale du point 41 et les paires du q du point 50. Ce n'est pas une
    #     raison de le laisser : la police est publiee sous OFL et composera
    #     autre chose que du francais OXA.
    #
    #     LE PIED DU N SORT DE CETTE TABLE AU CINQUANTE-TROISIEME TOUR, ET LE
    #     PIED DU H RESTE. Decision de Nicolas, prise sur une MESURE et non sur
    #     la demande telle qu'elle avait ete formulee. Il avait demande, en
    #     navigateur sur la section 1 de `tour51.html`, que le N perde sa
    #     sortante en bas a gauche ; retirer la sortante de TITRAGE seule
    #     (`lot4.PRESCRIPTIONS["N"]`, meme tour) laissait le N a -24,0 et non a
    #     plat, parce que le pied portait DEUX gestes et que la demande n'en
    #     nommait qu'un. Le K, que la decision prend pour modele, n'a jamais eu
    #     d'entree de pied ici : c'est pour cela que la meme prescription le rend
    #     plat a 0,0. Les DEUX entrees doivent donc bouger pour que le N
    #     rejoigne le K, et c'est ce que Nicolas a tranche apres avoir vu les
    #     trois etats chiffres -- -44,0 servi, -24,0 titrage seul retire, 0,0
    #     les deux retires.
    #
    #     CE QUE CE RETRAIT REND, ET CE QU'IL COUTE. Il rend `q+N`, le contact
    #     que cette entree seule avait cree au vingt-huitieme tour et que
    #     `paires_pieds.py` referme depuis : la paire n'a plus lieu d'etre
    #     corrigee, donc la table bouge et son zero-diff demande son temoin. Il
    #     coute l'ecart avec le H, qui garde ses deux gestes et ses -44,0 : il
    #     passe de 0 a 44 unites entre deux lettres a futs paralleles, quand la
    #     symetrie des deux entrees etait l'argument du huitieme tour.
    #
    #     LE SOMMET DU N NE BOUGE PAS. Sa montee de 24 unites reste ici, ligne
    #     plus haut, et la sortante `hd` du titrage reste dans `lot4` : Nicolas
    #     garde le haut du N entier, et c'est le bas seul qui est rendu a plat.
    ("H",                   loc_pied_gauche,     "gauche", SORTANTE, 24.0),
    # SOUS-LOT 4b du vingt-cinquieme tour, instruit et ecrit au vingt-neuvieme :
    # LES DEUX DIAGONALES. Demande de Nicolas sur la planche d'alphabet, dans la
    # famille « depasse en capitale » : « A et X, la coupe du titrage ».
    #
    #     A  le pied DROIT plonge de 24 unites par son coin droit.
    #     X  le pied GAUCHE plonge de 24 par son coin gauche.
    #
    #     `lot4.PRESCRIPTIONS` porte les deux formes depuis le dixieme tour, et
    #     Nicolas les a confirmees telles quelles : `sortantes={"bd"}` et
    #     `exclure={"bg","hc"}` sur le A, donc le bas droit sort, le bas gauche
    #     reste plat et LE SOMMET RESTE DROIT ; `sortantes={"bg"}` et
    #     `pointes={"bg":"gauche"}` sur le X, donc un seul bout sortant, en bas a
    #     gauche.
    #
    #     **`pointes` NE FAIT AUCUNE MISE EN POINTE.** Lu dans
    #     `lot4.couper_alignements` : il ne sert qu'a forcer le sens de rotation
    #     par `sens_pour_pointe`, pour que le coin qui sort soit celui du cote
    #     nomme. Le mot y designe un coin, pas une operation. Les deux entrees
    #     d'ici sont donc des sortantes ordinaires, comme les neuf des lots 1 a
    #     4a.
    #
    #     LES 24 UNITES SONT `approches.JOUR_MIN`, la valeur du N et du H au 4a,
    #     et le regime reste en unites — cinquieme fois que le point ouvert 51
    #     est fige par defaut, et la seconde ou c'est un choix explicite de
    #     Nicolas. Les 44 du titrage capitale ne sont PAS disponibles ici, et
    #     c'est mesure : elles mettent cinq paire-masters du A et quatre du X
    #     sous le plancher, dont six contacts francs.
    #
    # AUCUN LOCALISATEUR NEUF, ET LA PASSATION ANNONCAIT LE CONTRAIRE. Elle tient
    # depuis le vingt-huitieme tour que le A et le X n'ont aucun localisateur,
    # que le quadrant ne peut pas en tenir lieu, et que c'est le travail
    # technique principal du sous-lot. Les deux premieres phrases sont vraies, la
    # troisieme est fausse : `loc_pied_droit` et `loc_pied_gauche`, ecrits pour
    # le lot 1, servent les deux cibles sur les huit masters des deux sources, et
    # ils DEPARTAGENT au lieu de tomber juste — le defaut de `loc_sommet_fut` sur
    # le N et le H. Sur le A les candidats horizontaux sont les segs 0, 2, 4 et
    # 6, le filtre a 12 unites au-dessus du plus bas ecarte la traverse a 168 et
    # le sommet a 668, et il reste 506 a 508 unites d'ecart d'abscisse entre les
    # deux pieds. Sur le X les candidats sont les segs 0, 3, 6 et 9, et l'ecart
    # vaut 489 a 495.
    #
    # **ET SUR LA CONTREFORME DU A, `loc_pied_droit` DESIGNE SON SEG 2.** Le
    # triangle du A a trois segments droits dont la base est horizontale : le
    # localisateur la retient, et ce qui l'arrete est le FILTRE SUR LE SIGNE DE
    # L'AIRE pose au dix-huitieme tour, quand ce meme triangle recevait une mise
    # en pointe dans le `Aogonek`. Mesure par la passe 1 de
    # `balayage_lot4b.py`, colonne « creux », et non suppose ferme.
    #
    # CE QUI SEPARE CE SOUS-LOT DU 4a EST L'ORIENTATION DU FLANC VOISIN. Les six
    # coins du 4a coulissaient le long d'un flanc de fut, donc vertical, et la
    # boite ne bougeait d'aucune unite en romain. Ici le flanc est une diagonale
    # — 69,3 degres a l'horizontale sur le A en romain et 80,6 en italique, 54,5
    # et 47,3 sur le X — donc le coin part de cote et la boite s'elargit : 8,5
    # unites sur le A et 13,9 sur le X a 24 unites.
    #
    # **LE NOMBRE ECRIT N'EST PAS LA PLONGEE, et c'est nouveau.**
    # `termes.angle_pour_sortie` vise le chemin parcouru par le coin. Sur les
    # flancs verticaux des quatre lots precedents ce chemin VALAIT la plongee a
    # un demi-point pres ; sur une diagonale il se partage. A 24 unites ecrites,
    # le A plonge de 22,5 et avance de 8,5, le X plonge de 19,5 et avance de
    # 13,9. Les deux lettres ne descendent donc pas a la meme profondeur, et
    # l'ecart vaut 3 unites.
    #
    # LES DEUX LETTRES PAIENT DE COTES OPPOSES, ET C'EST LE POINT OUVERT 52 PRIS
    # A L'ENDROIT. Le coin du A sort vers la DROITE, donc c'est le voisin SUIVANT
    # qui paie et la paire critique est `A+j` ; le coin du X sort vers la GAUCHE,
    # donc c'est le PRECEDENT et la paire critique est `q+X`, quatrieme recidive
    # de la queue du q apres `q+m` et `q+M` au lot 1, `q+y` au lot 3, `q+N` et
    # `q+H` au 4a. A 24 unites, ni `A+j` ni `q+X` ne passe sous le plancher dans
    # aucun des huit masters : le franchissement le plus bas vaut 28,5 unites sur
    # le A en ExtraBold romain et 26,0 sur le X en ExtraBold Italic, donc la
    # marge la plus courte du sous-lot est de 2,0 unites.
    #
    # **MAIS `A+X` PASSE SOUS LE PLANCHER DANS LES HUIT MASTERS, ET AUCUN
    # GARDE-FOU DU PROJET NE POUVAIT LE VOIR.** C'est la paire des deux lettres
    # du sous-lot l'une contre l'autre : le pied du A descend a DROITE, celui du
    # X descend a GAUCHE, et les deux se ferment l'un sur l'autre. La passe 4 de
    # `balayage_lot4b.py` ne pouvait pas la trouver parce qu'elle applique UN
    # geste a la fois et mesure la cible contre des voisins intacts — dans son
    # etat, `A+X` reste a 32,8 unites, au-dessus du plancher. C'est
    # `inventaire_pieds.py`, qui lit l'etat ECRIT ou les deux gestes coexistent,
    # qui l'a rendue. **Un garde-fou qui teste un geste a la fois est aveugle a
    # toute paire dont les DEUX membres portent un geste**, et c'est une forme
    # nouvelle du trou que le point ouvert 52 decrit pour les sens de paire.
    #
    # Le couloir passe de 39,8 a 18,2 unites en ExtraLight et de 32,8 a 11,1 a
    # l'ExtraBold. Mesure REELLE et non artefact : `couloir_plein` et la mesure
    # exacte de `balayage_lot4b.couloir_exact` s'accordent au dixieme dans les
    # huit masters, le chiffre ne bouge pas quand le pas d'echantillonnage passe
    # de 1,24 a 0,01 unite, et le compte de taches d'encre par
    # `approches.composer` rend deux taches partout — donc un resserrement franc
    # et non un contact. Le meme compte par `souscrits.taches_mot` annonce une
    # fusion dans cinq masters, et c'est faux : il passe par `dessin.dessiner`,
    # aveugle au crenage, et le crenage d'Atkinson sur `A+X` vaut **+18** a
    # l'ExtraBold. Le piege du vingt-sixieme tour, ou la meme mesure etait juste
    # par accident.
    #
    # **Le point ouvert 50 se ferme donc une QUATRIEME fois.**
    # `approches.CIBLES_PIEDS` passe de huit a dix glyphes et `paires_pieds.py`
    # de 28 a 36 paires, `A+X` de +19 a +32 selon le master. Le diff ne porte que
    # ces huit ajouts et aucune ligne retiree : les 28 paires anterieures sont
    # inchangees au chiffre pres.
    ("A",                   loc_pied_droit,      "droite", SORTANTE, 24.0),
    ("X",                   loc_pied_gauche,     "gauche", SORTANTE, 24.0),

    # 11. LOT 5 des vingt-deux gestes, trentieme tour : les ANGLES DEDUITS.
    #
    # Demande de Nicolas au vingt-cinquieme tour, famille « angle deduit,
    # geometrie nouvelle » : « c et C, les bouts ouverts de facon a viser le
    # centre de la lettre ; G le haut comme le C, plus le repli interieur pour
    # faire une droite entre les deux coupes ; Q coupe verticale sur la ligne
    # interieure ». Le precedent nomme dans la demande est la queue du g.
    #
    # AUCUNE DE CES ENTREES N'ECRIT UN ANGLE, et c'est ce qui les separe des
    # quatre lots precedents. Elles ecrivent un MARQUEUR, et l'angle est
    # recalcule dans chaque master : 10 a 16 degres sur le c et le C, 9 a 15
    # sur le bout haut du G, 37 a 44 sur le Q. Le nombre commun aux lots 1 a 4
    # n'a pas d'equivalent ici, puisque la demande porte sur une VISEE et non
    # sur une profondeur — le point ouvert 51, unites contre angle constant,
    # ne s'y applique donc pas et n'est pas fige une sixieme fois.
    #
    # LA PASSATION REDOUTAIT QUE CES RONDES N'AIENT AUCUN SEGMENT DROIT, ce qui
    # aurait mis tout l'outillage hors service. Mesure au trentieme tour sur
    # les huit masters des deux sources : c'est vrai du O et du o, et FAUX des
    # quatre cibles. Septieme chiffre de la passation corrige par le projet.
    #
    # LE RISQUE DE CE LOT VA DANS L'AUTRE SENS QUE CELUI DES QUATRE PRECEDENTS.
    # Ceux-la faisaient sortir de la matiere, donc leur risque etait le
    # CONTACT ; une rentrante retire, donc le risque est l'OUVERTURE du
    # couloir, que le projet a paye deux fois — la barre du F au vingt-
    # troisieme tour, la queue du l au vingt-sixieme. A PART_LOT5 = 0,5, le lot
    # ouvre 0, 9, 43 et 72 paires au-dela de 20 unites dans les quatre masters
    # romains, 0, 5, 54 et 80 en italique, le pire ecart valant 39 a 46 unites.
    # C'est plus que le z du lot 2, qui en ouvrait 11 a 13 de 26 a 34 unites et
    # que cela a suffi a differer. **A refermer ou a differer : c'est le seul
    # cout ouvert de ce lot.**
    #
    # CE QUE LE LOT NE COUTE PAS, ET C'EST MESURE. La chasse ne bouge dans
    # aucun master. La boite du Q ne bouge d'aucune unite sur ses quatre cotes,
    # celle du G de 0 a 3, celle du c et du C de 1 a 16 unites sur le seul
    # xmax. L'interligne n'est pas touche, aucune de ces lettres ne franchissant
    # d'alignement. La topologie tient a 600 et a 1800 px de cadratin.
    #
    # LE LOT RETIRE DE L'ENCRE PARTOUT, et il a fallu deux controles en
    # desaccord pour l'etablir. `check3` signale dix alertes d'AIRE sur ces
    # quatre lettres, jusqu'a +3 344 unites carrees sur le G ExtraLight, et
    # `check4` rendait « retire 0,7 a 1,9 % » sur les memes. **C'est
    # `coupe.area` qui mesurait autre chose** : elle somme le polygone des
    # NOEUDS D'ANCRAGE et ignore les points de controle, donc elle rend 68 % de
    # l'encre reelle sur une ronde, et une coupe qui pousse un noeud vers
    # l'exterieur la fait monter pendant que l'encre baisse. Mesuree par
    # rasterisation sur les trente-deux etats, l'encre RECULE de 0,22 % sur le
    # G ExtraLight a 3,09 % sur le c ExtraBold, sans une seule inversion.
    # Les dix alertes de `check3` sont donc attendues et ne disent pas ce que
    # leur etiquette annonce.
    #
    # ET LA CONFUSION DU GROUPE O/0/Q/C/G S'AMELIORE, alors que trois des cinq
    # membres du groupe le plus surveille du projet sont ici. O/C gagne 0,038
    # au Bold, C/G 0,026, Q/C 0,016. Une seule paire franchit son seuil, O/Q a
    # l'ExtraBold Italic, a 0,001 pres, et c'est le geste du Q qui la porte.
    # L'etalonnage est mesure PAR MASTER : le point ouvert 42 est romain et
    # incomplet, la paire la plus serree etant h/b, P/R ou D/O selon le master
    # et jamais E/F ni I/T ni F/P hors de l'ExtraLight romain.
    ("c",                   loc_bout_de_ronde,   CCW, 0.0, VISE_CENTRE),
    ("C",                   loc_bout_de_ronde,   CCW, 0.0, VISE_CENTRE),
    # L'ORDRE DES DEUX ENTREES DU G COMPTE, et il n'est pas cosmetique : le
    # repli prend l'angle du bout haut TEL QU'IL EST, donc apres sa rotation.
    # Les inverser poserait le repli sur l'angle d'origine et « les deux
    # coupes » ne seraient plus paralleles.
    ("G",                   loc_bout_de_ronde,   CCW, 0.0, VISE_CENTRE),
    ("G",                   loc_repli_G,         CCW, 0.0, SUIT_BOUT),
    # Le Q ne prend pas PART_LOT5 : sa coupe est verticale ou elle ne l'est
    # pas. Son localisateur est le seul du projet a travailler sur un contour
    # de CREUX, et il porte le drapeau qui leve le filtre du dix-huitieme tour.
    # Le bout EXTERIEUR de sa queue ne bouge pas, sur arbitrage de Nicolas : il
    # porte a la fois le ymin et le xmax du glyphe.
    # Contre-intuitif et mesure : la coupe AGRANDIT la panse du Q au lieu de la
    # reduire — l'aire du creux passe de 81 a 92 % de celle du O a l'ExtraBold,
    # dans les huit masters sans exception — parce que rendre le bout interieur
    # vertical RACCOURCIT la pointe qui empietait dans la contreforme. L'oeil
    # avait conclu l'inverse sur la planche, deux fois.
    ("Q",                   loc_ligne_interieure_Q, CCW, 0.0, VERTICALE_AXE),
]


# --------------------------------------------------------------- operations

#: La part de la longueur du bout que l'ecart doit atteindre dans la direction
#: nommee pour que le nom departage vraiment les deux coins.
#:
#: Un pour cent, et le chiffre est large des deux cotes : sur un bout horizontal
#: l'ecart en ordonnee vaut exactement zero, sur le bout vertical du y en
#: italique l'ecart en abscisse vaut 16 unites pour un bout de 49, soit 33 %.
#: Les cinq entrees sortantes et les onze rentrantes de `LOT2` nomment toutes un
#: coin que leur bout departage, et c'est mesure et non suppose — les six
#: controles ont ete rejoues apres la pose de ce refus.
SEUIL_COIN = 0.01


def _coin_vise_est_P(segs, i, coin):
    """Lequel des deux bouts du segment le nom de coin designe.

    **Leve quand le nom ne departage pas les deux coins**, et c'est ce refus qui
    compte. Sur un bout HORIZONTAL les deux coins ont la meme ordonnee : « bas »
    et « haut » n'y designent rien, et le test d'inegalite stricte tombait alors
    sur un sens arbitraire au lieu d'echouer. Sur un bout VERTICAL c'est
    « gauche » et « droite » qui ne designent rien.

    Le defaut a ete trouve au vingt-septieme tour, et il s'est vu par une
    colonne uniforme : la passe 2 de `balayage_lot3.py` mesurait les deux
    lectures de la demande de Nicolas sur le p et rendait exactement le meme
    deplacement pour les deux, parce que « bas » y designait le coin droit sans
    le dire. C'est la sixieme fois qu'une mesure uniforme revele un defaut dans
    ce projet, et la premiere ou le defaut est dans le nommage plutot que dans
    la mesure.

    Ce que le refus fait gagner, au-dela du balayage : il rend le nom de coin
    d'une entree de `LOT2` verifiable. Un nom qui ne departage pas etait
    accepte, appliquait un geste, et personne ne pouvait dire lequel des deux
    coins il avait fait bouger.
    """
    P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    lg = K.length(segs[i])
    axe = 0 if coin in ("gauche", "droite") else 1
    ecart = abs(float(P[axe]) - float(Q[axe]))
    if lg > 0 and ecart < SEUIL_COIN * lg:
        quoi = "abscisse" if axe == 0 else "ordonnee"
        autres = ("« bas » ou « haut »" if axe == 0
                  else "« gauche » ou « droite »")
        raise ValueError(
            f"le coin « {coin} » ne departage pas les deux bouts de ce "
            f"segment : ils ont la meme {quoi} a {ecart:.2f} unite pres pour "
            f"une longueur de {lg:.1f}. Nommer {autres}.")
    if axe == 0:
        return (float(P[0]) < float(Q[0])) == (coin == "gauche")
    return (float(P[1]) < float(Q[1])) == (coin == "bas")


def sens_pour_coin(segs, i, coin):
    """Le sens de rotation qui fait RECULER le coin nomme, pour une coupe.

    Le pivot est lu dans le calcul meme de `K.coupe` — `pivot_P = dot(w, d) < 0`
    avec `w = rot(v, th) - v` — et non retrouve en comparant les points avant et
    apres. Le premier jet cherchait, parmi les deux coins du bout coupe, le plus
    proche du coin vise : quand le coin vise recule beaucoup, le plus proche
    devient le coin fixe, et le test rendait le mauvais sens. Une verification
    doit prendre son objet du producteur.
    """
    P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    d = K.outward(segs, i)
    vise_est_P = _coin_vise_est_P(segs, i, coin)
    v = Q - P
    for sn in (+1, -1):
        th = math.radians(20.0) * sn
        pivot_P = float(np.dot(K.rot(v, th) - v, d)) < 0
        if (not pivot_P) == vise_est_P:      # le coin qui recule est l'autre
            return sn
    return None


def sens_pour_sortie(segs, i, coin):
    """Le sens qui fait SORTIR le coin nomme, pour une sortante.

    Lu dans le calcul de `K.coupe_sortante` : `sortie_par_Q = dot(w, d) > 0`.
    """
    P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    d = K.outward(segs, i)
    vise_est_Q = not _coin_vise_est_P(segs, i, coin)
    v = Q - P
    for sn in (+1, -1):
        th = math.radians(20.0) * sn
        if (float(np.dot(K.rot(v, th) - v, d)) > 0) == vise_est_Q:
            return sn
    return None


def sens_pour_bascule(segs, i, coin):
    """Le sens qui fait DESCENDRE le coin nomme, pour une bascule.

    Les deux sens sont essayes et le resultat est lu sur le bout reellement
    dessine : la bascule n'a pas de pivot dont on puisse lire le signe, ses deux
    coins bougent.
    """
    P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    vise_est_P = _coin_vise_est_P(segs, i, coin)
    for sn in (+1, -1):
        try:
            ap = K.bascule(segs, i, 20.0, sn)
        except ValueError:
            continue
        avant = P if vise_est_P else Q
        apres = K.V(ap[i]["p0"] if vise_est_P else ap[i]["p3"])
        if float(apres[1]) < float(avant[1]):
            return sn
    return None


def angle_pour_sortie(segs, i, sn, cible):
    """L'angle de sortante qui deplace le coin sortant de `cible` unites.

    `lot4.angle_pour_depassement` mesure l'ecart a une ligne horizontale, ce qui
    suppose que le coin sort vers le haut ou vers le bas. Le bout du crochet du
    f sort lateralement — son flanc voisin est le sommet du crochet, horizontal,
    donc le coin avance a hauteur constante et un ecart mesure en ordonnee reste
    nul quel que soit l'angle : la dichotomie ne convergerait sur rien.

    La grandeur mesuree ici est le chemin parcouru par le coin. Elle vaut la
    profondeur sous la ligne quand le flanc est vertical, comme au pied du n, et
    l'avance quand il est horizontal, comme au crochet du f. C'est la grandeur
    qui se voit dans les deux cas.
    """
    P0, Q0 = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])

    def chemin(th):
        try:
            ap = K.coupe_sortante(segs, i, th, sn)
        except ValueError:
            return None
        Pn, Qn = K.V(ap[i]["p0"]), K.V(ap[i]["p3"])
        return max(float(np.hypot(*(Pn - P0))), float(np.hypot(*(Qn - Q0))))

    lo, hi = 0.5, 45.0
    if chemin(lo) is None:
        return None
    haut = chemin(hi)
    if haut is not None and haut < cible:
        return hi
    for _ in range(24):
        mil = (lo + hi) / 2.0
        v = chemin(mil)
        if v is None or v > cible:
            hi = mil
        else:
            lo = mil
    return lo


def appliquer(layer, loc, theta, sense, roll, journal=None, nom="",
              master=None):
    """Applique la loi a tous les contours d'un calque ou le localisateur trouve
    une terminaison.

    On balaie tous les contours d'encre, pas seulement le plus grand : le double
    accent aigu est fait de deux traits d'aire quasi egale, et departager les
    deux par l'aire donnait un resultat different selon le master — donc une
    topologie divergente et une interpolation cassee.

    Les contreformes sont ecartees par un filtre explicite sur le signe de
    l'aire, et non laissees a s'ecarter d'elles-memes. Ce docstring affirmait le
    contraire — les contreformes n'ont pas de segment droit — ce qui est vrai des
    accents et faux des lettres : la contreforme du A est un triangle a trois
    segments droits, et `loc_bas` y trouve un bout. Mesure au dix-huitieme tour,
    par `verif_contreformes.py` : le filtre attrape 24 contours sur les huit
    masters des deux sources, tous dans Aogonek, aogonek et eogonek, et zero
    dans les glyphes deja presents dans la table. Il pouvait donc etre pose sans
    rien changer a ce qui etait deja compile. Sans lui, les huit lettres a
    ogonek auraient recu une pointe dans leur contreforme.
    """
    # Le filtre sur le signe de l'aire reste pose pour TOUS les localisateurs
    # sauf ceux qui portent `sur_creux`. Un seul le porte, celui de la ligne
    # interieure du Q, ecrit au trentieme tour : sa coupe est demandee DANS une
    # contreforme, ce que le filtre du dix-huitieme tour interdit a bon droit
    # partout ailleurs. L'exception est ainsi attachee au localisateur qui la
    # justifie, et non ecrite dans la table ou personne ne la relierait au
    # piege du `Aogonek`.
    creux_permis = bool(getattr(loc, "sur_creux", False))
    for p in list(paths(layer)):
        segs = K.to_segs(p)
        if K.area(segs) < 0 and not creux_permis:
            continue
        if K.area(segs) >= 0 and creux_permis:
            continue
        idx = loc(segs)
        if not idx:
            continue
        # de la fin vers le debut : une coupe ne touche que ses voisins immediats
        for i in sorted(idx, reverse=True):
            avant = K.length(segs[i])
            if roll == POINTE:
                tir, ext = theta if isinstance(theta, tuple) else (theta, 0.0)
                segs, th = K.pointe(segs, i, tir, ext), 0.0
                # La pointe reellement placee, rendue par le producteur. Une
                # planche ou un controle qui la cherche apres coup se trompe :
                # le bout mis en pointe n'est plus un segment droit, et
                # `loc_bas` ne le reconnait plus. Le projet est tombe trois
                # fois dans ce piege, la derniere au dix-septieme tour.
                pt = tuple(float(v) for v in segs[i]["p3"])
            elif roll == BASCULE:
                sn = sense if sense in (CCW, CW) else sens_pour_bascule(
                    segs, i, sense)
                if sn is None:
                    raise ValueError(f"{nom} : aucun sens ne fait descendre "
                                     f"le coin {sense}")
                th = theta
                segs = K.bascule(segs, i, th, sn)
                # Le point remarquable d'une bascule est le coin qui monte :
                # c'est lui qui franchit l'alignement, c'est lui qu'une loupe
                # doit cadrer, et c'est lui que le journal rend.
                P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
                haut = P if float(P[1]) > float(Q[1]) else Q
                pt = tuple(float(v) for v in haut)
            elif roll == ALLONGE:
                # LE SEUL GESTE DU PROJET QUI NE TOURNE RIEN. Le bout est
                # pousse le long de sa normale sortante et les deux flancs
                # sont prolonges : le trait garde sa largeur et le bout son
                # orientation. Voir `coupe.allonge`.
                dist = valeur_master(theta, master, nom)
                if dist is None:
                    raise ValueError(f"{nom} : allongement sans valeur")
                segs = K.allonge(segs, i, float(dist))
                th = 0.0
                # Le point remarquable d'un allongement est le MILIEU du bout
                # deplace, et non un coin : les deux coins avancent d'autant.
                pt = tuple(float(v) for v in K.mid(segs[i]))
            elif roll == SORTANTE:
                cible = theta[0] if isinstance(theta, tuple) else theta
                coin = theta[1] if isinstance(theta, tuple) else sense
                sn = sens_pour_sortie(segs, i, coin)
                if sn is None:
                    raise ValueError(f"{nom} : aucun sens ne fait sortir le "
                                     f"coin {coin}")
                th = angle_pour_sortie(segs, i, sn, cible)
                if th is None:
                    raise ValueError(f"{nom} : aucune sortante possible")
                avant_pts = (K.V(segs[i]["p0"]), K.V(segs[i]["p3"]))
                segs = K.coupe_sortante(segs, i, th, sn)
                # Le point remarquable d'une sortante est le coin qui a bouge.
                apres_pts = (K.V(segs[i]["p0"]), K.V(segs[i]["p3"]))
                bouge = max(range(2),
                            key=lambda j: float(np.hypot(
                                *(apres_pts[j] - avant_pts[j]))))
                pt = tuple(float(v) for v in apres_pts[bouge])
            else:
                if sense in COINS:
                    sn = sens_pour_coin(segs, i, sense)
                    if sn is None:
                        raise ValueError(f"{nom} : aucun sens ne fait reculer "
                                         f"le coin {sense}")
                    th = theta
                elif theta == VISE_HAMPE:
                    th, sn = angle_vise(segs, i, sense)
                elif theta == VISE_CENTRE:
                    # Le c, le C et le bout haut du G. La cible est le centre
                    # de l'anneau, pas celui de la boite, et elle est prise a
                    # PART_LOT5 du chemin.
                    cible = centre_anneau(layer, nom)
                    if cible is None:
                        raise ValueError(f"{nom} : pas de O de reference pour "
                                         f"deduire le centre de l'anneau")
                    th, sn = angle_pour_viser(segs, i, sense, cible, PART_LOT5)
                    if th <= 0:
                        raise ValueError(f"{nom} : aucun sens ne fait viser le "
                                         f"centre depuis le bout {i}")
                elif theta == SUIT_BOUT:
                    th, sn = angle_du_bout_haut(segs, i)
                elif theta == VERTICALE_AXE:
                    th, sn = angle_verticale_axe(layer, segs, i)
                else:
                    th, sn = theta, sense
                segs = K.coupe(segs, i, th, sn, roll)
                pt = None
            if journal is not None:
                journal.append((nom, i, avant, K.length(segs[i]), th, pt))
        layer.shapes[layer.shapes.index(p)] = K.from_segs(segs)


def angle_vise(segs, i, sense):
    """Angle pour que la coupe `i` pointe vers le sommet du fut du glyphe.

    Demande de Nicolas sur le g : que la droite prolongeant le petit morceau du
    bas de la hampe vise le haut de cette hampe. L'angle n'est donc pas donne,
    il est deduit — et il change d'un master a l'autre, de 42,1 degres en
    Regular a 31,5 en ExtraBold au romain, de 35,3 a 26,4 en italique,
    puisque la geometrie du glyphe change.
    """
    j = loc_hampe(segs)
    if not j:
        return 20.0, sense
    hampe = [K.V(segs[j[0]]["p0"]), K.V(segs[j[0]]["p3"])]
    cible = max(hampe, key=lambda p: p[0])          # coin externe du sommet
    P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    d = K.outward(segs, i)
    v = Q - P
    # pivot : le coin qui fait rentrer l'autre, pour un petit angle du bon sens
    sonde = K.rot(v, math.radians(sense)) - v
    pivot_P = float(sonde[0] * d[0] + sonde[1] * d[1]) < 0
    base = K.unit(v if pivot_P else -v)
    u = K.unit(cible - (P if pivot_P else Q))
    ang = math.degrees(math.atan2(K.cross(base, u), float(base[0] * u[0] + base[1] * u[1])))
    # une coupe est une droite, pas un vecteur : on ramene dans ]-90, 90].
    while ang > 90:
        ang -= 180
    while ang <= -90:
        ang += 180
    return abs(ang), (1 if ang >= 0 else -1)


def _angle_seg(segs, i):
    """L'angle d'un segment modulo 180 : une droite n'a pas d'orientation."""
    d = K.V(segs[i]["p3"]) - K.V(segs[i]["p0"])
    return math.degrees(math.atan2(float(d[1]), float(d[0]))) % 180.0


def _boite_du_glyphe(font, nom, layer_id):
    """La boite des contours d'encre d'un glyphe, dans le master donne."""
    g = font.glyphs[nom]
    if g is None:
        return None
    for lay in g.layers:
        if lay.layerId != layer_id:
            continue
        pos = [K.to_segs(p) for p in paths(lay)]
        pos = [sg for sg in pos if K.area(sg) >= 0]
        if not pos:
            return None
        xs, ys = [], []
        for sg in pos:
            for s in sg:
                for t in (0.0, 0.25, 0.5, 0.75, 1.0):
                    q = K.bez(s, t)
                    xs.append(float(q[0]))
                    ys.append(float(q[1]))
        return min(xs), min(ys), max(xs), max(ys)
    return None


def centre_anneau(layer, nom):
    """Le centre de l'anneau du glyphe : celui du O, ou du o pour un bas de casse.

    LA CIBLE EST L'ANNEAU ET NON LA BOITE, arbitrage de Nicolas au trentieme
    tour, et la raison est mesuree : le C est ouvert a droite, donc son xmax
    EST celui de ses bouts, et le centre de sa boite serait DEPLACE par le
    geste qui le vise — une cible qui fuit. Le centre du O ne bouge pas. Les
    deux different de 13 a 39 unites selon la lettre et le master.

    Le O est le seul endroit du repertoire ou cet anneau est ferme, donc
    mesurable ; le c, le C et le G en sont l'interruption.
    """
    ref = "o" if nom[:1].islower() else "O"
    font = layer.parent.parent if layer.parent is not None else None
    if font is None:
        return None
    bb = _boite_du_glyphe(font, ref, layer.layerId)
    if bb is None:
        return None
    return (bb[0] + bb[2]) / 2.0, (bb[1] + bb[3]) / 2.0


def angle_vers_centre(segs, i, sense, cible, part=1.0):
    """Angle pour que la droite du bout `i` passe par `cible`.

    Exact et non cherche par dichotomie : la droite tourne autour du pivot,
    donc l'angle est l'ecart entre la direction du bout et la direction
    pivot -> cible.

    UN SEUL DES DEUX SENS ATTEINT LA CIBLE, ET C'EST UN FAIT DE L'OUTIL.
    `coupe.coupe` choisit son pivot d'apres le sens — le sens +1 garde P, le
    sens -1 garde Q. Pour un bout donne, un seul des deux pivots met la droite
    sur le centre par une rotation POSITIVE ; l'autre en demanderait une
    negative, que la fonction n'offre pas puisqu'elle recalculerait alors
    l'autre pivot. Rend `(angle, sens)` avec un angle nul quand ce sens ne
    convient pas, ce qui laisse l'appelant essayer l'autre.
    """
    P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    d = K.outward(segs, i)
    v = Q - P
    sonde = K.rot(v, math.radians(sense)) - v
    pivot_P = float(sonde[0] * d[0] + sonde[1] * d[1]) < 0
    piv = P if pivot_P else Q
    a0 = math.atan2(float(v[1]), float(v[0]))
    c = K.V(cible) - piv
    a1 = math.atan2(float(c[1]), float(c[0]))
    da = a1 - a0
    while da > math.pi / 2:
        da -= math.pi
    while da <= -math.pi / 2:
        da += math.pi
    th = math.degrees(da) * sense
    return (th * part, sense) if th > 0 else (0.0, sense)


def angle_pour_viser(segs, i, sense, cible, part=1.0):
    """Le sens qui atteint la cible, et son angle. Essaie les deux."""
    for sn in (sense, -sense):
        th, _ = angle_vers_centre(segs, i, sn, cible, part)
        if th > 0:
            return th, sn
    return 0.0, sense


def angle_vers(segs, i, vise):
    """Tourne le bout `i` jusqu'a l'angle absolu `vise`, et rend (angle, sens).

    LES DEUX SENS SONT ESSAYES ET C'EST LE RESULTAT QUI TRANCHE, jamais le
    signe devine : `coupe.coupe` choisit son pivot d'apres le sens, donc
    appliquer la rotation au sens suppose fait tourner autour de l'autre coin
    et atterrir ailleurs. Le balayage du trentieme tour a rendu quatre lignes
    de bruit pour avoir devine ce signe une premiere fois.
    """
    a0 = _angle_seg(segs, i)
    da = (vise - a0 + 90.0) % 180.0 - 90.0
    best = None
    for sn in (CCW, CW):
        try:
            r = K.coupe(segs, i, abs(da), sn)
        except Exception:
            continue
        obt = _angle_seg(r, i)
        ec = min(abs(obt - vise), 180.0 - abs(obt - vise))
        if best is None or ec < best[0]:
            best = (ec, sn)
    return (abs(da), best[1] if best else CCW)


def angle_du_bout_haut(segs, i):
    """L'angle qui pose le repli du G sur le MEME ANGLE que son bout de ronde.

    LA DEMANDE DE NICOLAS EST UN ANGLE, PAS UNE DROITE, et le trentieme tour a
    essaye les deux. « Le repli interieur pour faire une droite entre les deux
    coupes » : poser le bout du repli sur le PROLONGEMENT du bout haut creuse
    une encoche en biseau dans la barre, parce que cette droite traverse la
    lettre — petite au Regular, franche a l'ExtraBold ou elle coupe le coin de
    la barre. Vu sur planche, tranche par Nicolas : c'est le meme angle, sans
    la meme droite, ce qui est le geste de la barre du F du lot 2.

    L'angle est pris sur le bout haut TEL QU'IL EST AU MOMENT DE L'APPEL, donc
    apres sa propre rotation. Les deux gestes ne sont pas independants et
    l'ordre compte : le bout haut d'abord, le repli ensuite.
    """
    h = loc_bout_de_ronde(segs)
    if not h:
        return 0.0, CCW
    return angle_vers(segs, i, _angle_seg(segs, h[0]))


def angle_verticale_axe(layer, segs, i):
    """L'angle qui rend le bout `i` vertical DANS L'AXE de la lettre.

    Arbitrage de Nicolas au trentieme tour : la verticale est celle de l'axe du
    dessin — 90 degres en romain, penchee de l'inclinaison en italique — et non
    la verticale absolue, qui ferait perdre a la coupe l'axe de la lettre dans
    les quatre masters italiques.

    L'INCLINAISON EST MESUREE SUR LE FUT DU I DU MASTER, jamais reprise d'une
    metrique declaree. C'est le seul trait droit du repertoire dont
    l'inclinaison est celle de l'axe et rien d'autre, et le projet a deja
    corrige six chiffres repris sans remesure. Elle vaut 90,0 en romain et 77,8
    a 78,2 en italique selon le master.
    """
    axe = 90.0
    font = layer.parent.parent if layer.parent is not None else None
    if font is not None:
        g = font.glyphs["I"]
        if g is not None:
            for lay in g.layers:
                if lay.layerId != layer.layerId:
                    continue
                for p in paths(lay):
                    sg = K.to_segs(p)
                    if K.area(sg) < 0:
                        continue
                    for s in sg:
                        if (s["kind"] == "line"
                                and abs(K.V(s["p3"])[1]
                                        - K.V(s["p0"])[1]) > 100):
                            d = K.V(s["p3"]) - K.V(s["p0"])
                            axe = math.degrees(math.atan2(
                                float(d[1]), float(d[0]))) % 180.0
                            break
                    break
    return angle_vers(segs, i, axe)


def barres(layer, loc, theta, sense, garder_basse=False, brider=True):
    """Aligne les bouts de barre sur une seule droite.

    Demande de Nicolas : que l'on puisse tracer une ligne droite entre le bout
    de la barre haute du F et celui de sa barre mediane. La longueur de la
    barre mediane n'est donc plus un rapport choisi, elle est deduite : c'est
    l'endroit ou la droite de coupe de la barre haute, prolongee, croise la
    hauteur de la barre mediane. Les deux coupes deviennent alors deux morceaux
    d'un meme trait.

    Effet mesure en Regular : la barre mediane passe de 508 a 409, tres proche
    des 403 retenus au tour precedent par un tout autre chemin.

    Le E recoit le meme geste sur sa barre mediane, mais garde sa barre basse :
    la droite l'amenerait a 313, ce qui ne serait plus un E.

    La direction de la droite est prise sur la geometrie, pas supposee
    verticale : dans l'italique les barres sont inclinees de 12 degres.
    """
    p = main_path(layer)
    segs = K.to_segs(p)
    n = len(segs)
    bouts = sorted(loc(segs), key=lambda i: K.mid(segs[i])[1])
    if len(bouts) < 2:
        raise ValueError(f"{len(bouts)} bouts de barre trouves, 2 attendus au moins")
    ref = bouts[-1]

    # direction de la coupe apres rotation, vue depuis le coin qui reste
    P, Q = K.V(segs[ref]["p0"]), K.V(segs[ref]["p3"])
    d = K.outward(segs, ref)
    v = Q - P
    sonde = K.rot(v, math.radians(sense)) - v
    pivot_P = float(sonde[0] * d[0] + sonde[1] * d[1]) < 0
    pivot = P if pivot_P else Q
    u = K.rot(v if pivot_P else -v, math.radians(theta) * sense)
    if abs(u[1]) < 1e-6:
        return
    pente = u[0] / u[1]

    # le coin de reference est en haut ou en bas de la coupe : on prend le
    # meme cote sur les autres barres, faute de quoi la droite serait decalee
    # de l'epaisseur d'une barre.
    en_haut = pivot[1] >= max(P[1], Q[1]) - 1e-6
    choisir = (lambda a, b: max((a, b), key=lambda p_: p_[1])) if en_haut \
        else (lambda a, b: min((a, b), key=lambda p_: p_[1]))

    a_bouger = bouts[:-1] if not garder_basse else bouts[1:-1]
    for i in a_bouger:
        coin = choisir(K.V(segs[i]["p0"]), K.V(segs[i]["p3"]))
        cible = pivot[0] + (coin[1] - pivot[1]) * pente
        # la droite ne peut que raccourcir. Dans les masters gras la barre
        # mediane du E est deja plus courte que ce que la droite donnerait :
        # l'allonger refermerait ses contreformes, ce qu'on ne fait pas pour
        # un motif de dessin. La ligne droite se lit donc sur les graisses
        # claires et se relache en gras. Le F, lui, raccourcit partout.
        #
        # `brider` a False leve cette retenue. Elle n'a de sens que dans la
        # coupe de titrage : a une taille de titre, une contreforme un peu plus
        # fermee ne coute pas ce qu'elle coute dans un paragraphe, et la droite
        # tient alors sur les quatre masters. Mesure : la bride ne mord que sur
        # la barre mediane du E, au Bold et a l'ExtraBold, ou elle retient
        # 42 et 52 unites.
        if brider:
            cible = min(cible, coin[0])
        delta = cible - coin[0]
        for j, cle in ((i, "p0"), (i, "p3"), (i - 1, "p3"), ((i + 1) % n, "p0")):
            x, y = segs[j][cle]
            segs[j][cle] = (x + delta, y)
    layer.shapes[layer.shapes.index(p)] = K.from_segs(segs)


def barre_F(layer, part=0.75):
    """Raccourcit la barre mediane du F a `part` de sa barre haute.

    Constat mesure : dans les quatre masters romains, la barre mediane du F
    s'arrete a 4 unites seulement de sa barre haute (508 contre 512 en
    Regular). Le F a donc deux barres de meme longueur, ce qui est inhabituel
    pour une grotesque et lui coute sa silhouette. Les longueurs se comptent
    depuis le fut, ce qui rend le rapport interpolable : il tient tout seul sur
    l'axe de graisse et sur l'italique.
    """
    p = main_path(layer)
    segs = K.to_segs(p)
    n = len(segs)
    bouts = sorted(lines(segs, vertical=True), key=lambda i: K.mid(segs[i])[1])
    if len(bouts) != 2:
        raise ValueError(f"F : {len(bouts)} bouts de barre trouves, 2 attendus")
    bas, haut = bouts[0], bouts[-1]

    def gauche(i):
        """Abscisse du bord gauche de la lettre, a la hauteur de la barre.

        Mesuree a la hauteur, et non une fois pour toutes : dans l'italique le
        fut est incline, et un bord gauche unique fausserait le rapport.
        """
        y = K.mid(segs[i])[1]
        xs = []
        for s in segs:
            for depart in (0.0, 0.5, 1.0):
                t = K.hit_plane(s, (0.0, 1.0), y, depart)
                if t is not None and -0.001 <= t <= 1.001:
                    xs.append(float(K.bez(s, min(max(t, 0.0), 1.0))[0]))
        return min(xs)

    cible = gauche(bas) + part * (K.mid(segs[haut])[0] - gauche(haut))
    delta = cible - K.mid(segs[bas])[0]
    avant = K.mid(segs[bas])[0]
    for j, cle in ((bas, "p0"), (bas, "p3"), (bas - 1, "p3"), ((bas + 1) % n, "p0")):
        x, y = segs[j][cle]
        segs[j][cle] = (x + delta, y)
    layer.shapes[layer.shapes.index(p)] = K.from_segs(segs)
    return avant, cible


def appliquer_lot(font, theta=20.0, journal=None):
    """Applique tout le lot 2 a une source .glyphs chargee.

    Les longueurs de barres passent en premier : les coupes s'appliquent
    ensuite aux barres deja mises a la bonne longueur.
    """
    mid = {m.id: m.name for m in font.masters}
    for nom, loc, garder in (("F", loc_barres_F, False), ("E", loc_barres_E, True)):
        g = font.glyphs[nom]
        if g is None:
            continue
        for l in g.layers:
            if l.layerId in mid:
                barres(l, loc, theta, CW, garder_basse=garder)
    for nom, loc, sense, roll, angle in LOT2:
        g = font.glyphs[nom]
        if g is None:
            continue
        th = theta if angle is None else angle
        for l in g.layers:
            if l.layerId in mid:
                # Le nom du master est passe explicitement, et non deduit de
                # l'etiquette du journal : une entree dont la valeur depend du
                # master ne doit pas dependre du decoupage d'une chaine.
                appliquer(l, loc, th, sense, roll, journal,
                          f"{nom}/{mid[l.layerId]}", master=mid[l.layerId])
    return font
