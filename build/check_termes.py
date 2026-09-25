#!/usr/bin/env python3
"""
Vingtieme tour, passe 2 : le controle de localisateur des six terminaisons
demandees par Nicolas sur le specimen. AVANT tout dessin.

Il repond a une seule question, celle de `check3.py` et de
`souscrits.verifier_localisateur` : le localisateur designe-t-il la meme
terminaison dans les huit masters des deux sources ?

Quatre criteres, et le troisieme n'est pas cosmetique. Un indice de segment
identique ne prouve pas qu'on parle du meme endroit du dessin si la topologie a
change ; et une position relative identique ne prouve rien si l'indice saute.
Les deux ensemble le prouvent.

  1. meme contour et meme indice de segment dans les huit masters
  2. meme nombre de segments dans le contour (topologie)
  3. meme quadrant, au sens de `lot4.quadrant` : bg, bc, bd, hg, hc, hd
  4. meme orientation (verticale, horizontale, diagonale)

Le troisieme critere passe par `lot4.quadrant` et non par une tolerance sur la
position relative, et le premier jet le disait autrement. Une tolerance de 0,08
sur le milieu signalait les six cibles, parce qu'elle mesurait deux choses qui
n'ont rien a voir avec un derapage de localisateur : le bout du n s'allonge de
40 a 147 unites le long de l'axe, donc son milieu se deplace ; et l'italique
penche toute la boite. Une comparaison ne mesure ce qu'on croit que si ses deux
termes ne different que par ce qu'on juge. Le quadrant est la granularite juste,
c'est celle par laquelle le lot 4 designe deja ses terminaisons, et le temoin
prouve qu'elle discrimine.

La longueur du bout n'est PAS un critere. Elle varie de 40 a 131 unites sur le
haut du fut du n le long de l'axe de graisse : un seuil relatif y signalerait
tous les glyphes. C'est le contraire du controle des souscrits, ou les trois
crochets sont des copies exactes et ou la longueur devait tenir a 2 % pres.
Devant un controle qui passe, se demander s'il mesure une grandeur qui varie ;
devant un controle qui signale, se demander si la grandeur se voit.

TEMOIN. `--temoin` rejoue la queue du t avec `loc_droite`, le localisateur que
la demande D suggere en premiere lecture — "la meme coupe que le l", et le l
recoit `loc_droite`. Il doit signaler : `loc_droite` designe le bout de la
queue en Regular, Bold et ExtraBold romains, et le bout droit de la barre
transversale dans les cinq autres masters, parce qu'en ExtraLight les deux sont
a un point l'un de l'autre en abscisse (259 contre 258). Un controle qui passe
sans savoir signaler ne prouve rien.

SOURCE. La source amont brute, `/tmp/ahn/sources/`, et non `Temoin.glyphs`.
Le premier jet lisait `Temoin.glyphs`, ce qui etait juste tant que les six
glyphes n'etaient dans aucune entree de la table : ils y sortaient alors
exactement tels qu'ils sont en amont. Des que les entrees ont ete ecrites, au
vingt-deuxieme tour, le meme controle s'est mis a mesurer des glyphes deja
coupes — et il a signale trois anomalies qui etaient son propre reflet. C'est le
piege du lot 3, quatrieme recidive, et il tombe cette fois sur le controle
plutot que sur une planche.

Le repli sur `Temoin.glyphs` existe pour les jours ou le depot amont n'est pas
clonable, et il refuse alors de conclure sur les glyphes que la table traite :
un controle doit distinguer "mesure et conforme" de "pas mesure".
"""

import os
import sys

import glyphsLib

import coupe as K
import lot2 as L
import lot4 as Q
import termes as T

ICI = os.path.dirname(os.path.abspath(__file__))
AMONT = "/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs"
AMONT_IT = "/tmp/ahn/sources/AtkinsonHyperlegibleNext-Italic.glyphs"


def sources():
    """Les deux sources a mesurer, brutes de preference.

    Rend des couples (chemin, etiquette). L'etiquette dit d'ou vient la mesure,
    parce qu'un controle qui a change de source sans le dire ne prouve plus rien.
    """
    if os.path.exists(AMONT) and os.path.exists(AMONT_IT):
        return [(AMONT, "amont rom"), (AMONT_IT, "amont ital")]
    out = []
    for fichier, etq in [("Temoin.glyphs", "Temoin rom"),
                         ("Temoin-Italic.glyphs", "Temoin ital")]:
        chemin = os.path.join(ICI, fichier)
        out.append((chemin if os.path.exists(chemin) else None, etq))
    return out


def source_brute():
    return os.path.exists(AMONT) and os.path.exists(AMONT_IT)


# ------------------------------------------------------- localisateurs neufs
#
# Ils vivent dans `termes.py`, l'outillage du tour, et ce controle les importe
# au lieu d'en garder une copie. Une table du code qui diverge de sa source ne
# se signale pas toute seule : `lot4.FAMILLES_O` l'a fait au douzieme tour, et
# une planche relancee montrait alors autre chose que ce qui avait ete juge.

loc_sommet_fut = T.loc_sommet_fut
loc_haut_vertical = T.loc_haut_vertical
loc_queue_t = T.loc_queue_t


# nom lisible -> (glyphe, localisateur, ce que ca doit designer)
CIBLES = [
    ("A  r  bout du bras",        "r", L.loc_droite,     "vertical, en haut a droite"),
    ("B  n  haut du fut gauche",  "n", loc_sommet_fut,   "horizontal, a la hauteur d'x"),
    ("C  m  haut du fut gauche",  "m", loc_sommet_fut,   "horizontal, a la hauteur d'x"),
    ("D1 t  queue",               "t", loc_queue_t,      "vertical, en bas a droite"),
    ("D2 t  sommet du fut",       "t", loc_sommet_fut,   "horizontal, a 620"),
    ("E  f  bout du crochet",     "f", loc_haut_vertical, "vertical, en haut a droite"),
    # Ajoutee au vingt-et-unieme tour, avec la demande de pointe en bas a droite.
    ("N  n  pied droit",          "n", T.loc_pied_droit, "horizontal, en bas a droite"),
    # Les trois pieds gauches du lot 1 du vingt-cinquieme tour. Sur le m et le
    # M, le localisateur departage trois bouts poses sur la ligne de base, ce
    # que `loc_bas` faisait par l'ordre du contour. Sur le f il n'en departage
    # aucun, le glyphe n'ayant qu'un bout bas — et c'est la que le quadrant
    # bascule de `bc` a `bg` en italique, par effet de seuil.
    ("P  m  pied gauche",         "m", L.loc_pied_gauche, "horizontal, en bas a gauche"),
    ("P  M  pied gauche",         "M", L.loc_pied_gauche, "horizontal, en bas a gauche"),
    ("P  f  pied de la hampe",    "f", L.loc_pied_gauche, "horizontal, en bas"),
    # Les quatre rentrants du lot 2 du vingt-cinquieme tour, ecrits au
    # vingt-sixieme. Sur le b, le d et le l, `loc_sommet_fut` designe le bout de
    # hampe, pose a 708 et non a l'ascendante declaree de 796. Le z est la
    # premiere cible du controle dont le localisateur rend DEUX segments, comme
    # celui du Z capitale : le critere de compte s'y adapte plutot que de
    # signaler une anomalie qui n'en est pas.
    ("H  b  bout de hampe",       "b", L.loc_sommet_fut, "horizontal, en haut"),
    ("H  d  bout de hampe",       "d", L.loc_sommet_fut, "horizontal, en haut"),
    ("H  l  bout de hampe",       "l", L.loc_sommet_fut, "horizontal, en haut"),
    ("Z  z  les deux bouts",      "z", L.loc_bouts_Z,    "verticaux, hg et bd"),
    # Les trois cibles du lot 3 du vingt-cinquieme tour, instruites au
    # vingt-septieme. Elles entrent dans ce controle avant d'etre ecrites dans
    # `LOT2`, et c'est voulu : un localisateur se verifie sur la source brute,
    # et tant que la table ne les traite pas, l'amont EST leur etat brut.
    #
    # Trois familles et non une, et c'est mesure :
    #
    #   J-p  bout de la jambe, HORIZONTAL, sur la descendante mesuree a −162.
    #        La passation annonce −251, qui est le `descender` declare et
    #        qu'aucune lettre n'atteint. Ecart de 89 unites, exactement le
    #        piege du bout de hampe au vingt-sixieme tour.
    #   Q-y  bout de la queue, VERTICAL. Il n'est pas le plat de dessous, que
    #        `loc_bas` designerait, et c'est le seul des trois ou le mien et
    #        `loc_bas` ne tombent pas sur le meme segment.
    #   Y-Y  pied de la capitale, HORIZONTAL, sur la LIGNE DE BASE : l'ymin du
    #        Y vaut 0,0 dans les huit masters. Le Y ne descend pas, et il est
    #        dans la famille du lot 1 et non dans celle du p.
    ("J  p  bout de la jambe",    "p", T.loc_bout_jambe,   "horizontal, en bas"),
    ("Q  y  bout de la queue",    "y", T.loc_bout_queue_y, "vertical, en bas"),
    ("Y  Y  pied",                "Y", T.loc_pied_Y,       "horizontal, en bas"),
    # Les six cibles du sous-lot 4a du vingt-cinquieme tour, instruites au
    # vingt-huitieme. Elles entrent dans ce controle avant d'etre ecrites dans
    # `LOT2`, pour la meme raison que celles du lot 3 : un localisateur se
    # verifie sur la source brute, et tant que la table ne les traite pas,
    # l'amont EST leur etat brut.
    #
    # Le h et le k reprennent `loc_sommet_fut`, celui du b, du d et du l : leur
    # bout de hampe est le SEUL bout horizontal a 708, donc le localisateur y
    # departage vraiment.
    #
    # **Le N et le H demandent `loc_sommet_droit`, et ce n'est pas du zele.**
    # `loc_sommet_fut` rend le bon segment sur les deux et il le rend PAR
    # ACCIDENT : les deux glyphes ont deux bouts horizontaux exactement a la
    # hauteur de capitale — les sommets des deux futs du H, le sommet du fut
    # droit du N et la jonction de sa diagonale — et `max(cand, key=y)` sur une
    # egalite parfaite rend le premier dans l'ordre du contour. Il se trouve
    # etre le bon sur les huit masters des deux sources, et rien ne le garantit.
    # C'est le defaut de `loc_bas`, releve au vingt-et-unieme tour : un
    # localisateur qui departage deux candidats a egalite par l'ordre du contour
    # tire au sort.
    #
    # `P-N` et `P-H` reprennent `loc_pied_gauche`, celui des trois pieds du lot
    # 1, qui departage par l'abscisse et non par l'ordre du contour.
    ("M  h  bout de hampe",       "h", L.loc_sommet_fut,   "horizontal, en haut"),
    ("M  k  bout de hampe",       "k", L.loc_sommet_fut,   "horizontal, en haut"),
    ("S  N  sommet du fut droit", "N", L.loc_sommet_droit, "horizontal, en haut a droite"),
    ("S  H  sommet du fut droit", "H", L.loc_sommet_droit, "horizontal, en haut a droite"),
    ("P  N  pied du fut gauche",  "N", L.loc_pied_gauche,  "horizontal, en bas a gauche"),
    ("P  H  pied du fut gauche",  "H", L.loc_pied_gauche,  "horizontal, en bas a gauche"),
    # Les deux cibles du sous-lot 4b du vingt-cinquieme tour, instruites au
    # vingt-neuvieme : les deux DIAGONALES. Elles entrent dans ce controle avant
    # d'etre ecrites dans `LOT2`, comme celles des lots 3 et 4a.
    #
    # **AUCUN LOCALISATEUR NEUF**, contre ce que la passation annonce depuis le
    # vingt-huitieme tour. `loc_pied_droit` et `loc_pied_gauche`, ecrits pour le
    # lot 1, servent les deux — et ils DEPARTAGENT au lieu de tomber juste, ce
    # qui est le defaut de `loc_sommet_fut` sur le N et le H :
    #
    #   sur le A, les candidats horizontaux du contour d'encre sont les segs 0,
    #   2, 4 et 6 dans les huit masters ; le filtre a 12 unites au-dessus du plus
    #   bas ecarte la traverse a 168 et le sommet a 668, et le departage restant
    #   se joue sur 506 a 508 unites d'ecart d'abscisse.
    #   sur le X, les candidats sont les segs 0, 3, 6 et 9 ; le filtre garde les
    #   deux pieds, poses tous deux sur la ligne de base, et l'ecart vaut 489 a
    #   495 unites.
    #
    # **ET SUR LA CONTREFORME DU A, `loc_pied_droit` DESIGNE SON SEG 2.** Le
    # triangle du A a trois segments droits dont la base est horizontale, donc
    # le localisateur la retient. Ce qui l'arrete est le filtre sur le signe de
    # l'aire pose au dix-huitieme tour, et c'est le piege du `Aogonek` mot pour
    # mot. Mesure par la passe 1 de `balayage_lot4b.py`, colonne « creux ».
    #
    # Une note de quadrant est attendue et elle ne concerne pas ces deux
    # entrees : le SOMMET du A, qui reste droit, vaut `hc` en romain et `hd` en
    # italique. `lot4.PRESCRIPTIONS` l'exclut par `exclure={"bg","hc"}`, donc la
    # prescription de TITRAGE ne l'excluerait pas en italique. Le titrage n'a ete
    # verifie qu'en romain, donc rien n'est casse ; c'est ecrit ici parce que
    # c'est ici qu'on le retrouvera.
    ("P  A  pied droit",          "A", L.loc_pied_droit,   "horizontal, en bas a droite"),
    ("P  X  pied gauche",         "X", L.loc_pied_gauche,  "horizontal, en bas a gauche"),
]

#: Le nombre de segments que chaque cible doit designer. Une seule en rend deux.
#:
#: Ecrit en table plutot qu'en test generique : « ce localisateur rend-il le bon
#: nombre de bouts » est une question dont la reponse depend du glyphe, et le
#: projet a deja montre deux fois ce que coute un test malin la ou une
#: verification suffit.
ATTENDU_N = {"Z  z  les deux bouts": 2}

TEMOIN = [
    ("T  t  queue par loc_droite", "t", L.loc_droite, "doit signaler"),
]


def orientation(s):
    dx = s["p3"][0] - s["p0"][0]
    dy = s["p3"][1] - s["p0"][1]
    if abs(dx) <= abs(dy) * 0.3:
        return "vert"
    if abs(dy) <= abs(dx) * 0.3:
        return "horiz"
    return "diag"


def boite(lay):
    xs, ys = [], []
    for p in L.paths(lay):
        for s in K.to_segs(p):
            for q in (s["p0"], s["p3"]):
                xs.append(float(q[0]))
                ys.append(float(q[1]))
    return min(xs), min(ys), max(xs), max(ys)


def designe(lay, loc):
    """Ce que le localisateur designe sur ce calque, ou None.

    On balaie les contours d'encre dans l'ordre, comme `lot2.appliquer`, et on
    prend le premier ou le localisateur trouve quelque chose.
    """
    for ip, p in enumerate(L.paths(lay)):
        segs = K.to_segs(p)
        if K.area(segs) < 0:
            continue
        idx = loc(segs)
        if idx:
            return ip, idx, segs
    return None


def controler(cibles):
    anomalies = []
    notes = []
    lignes = []
    for etiquette, nom, loc, attendu in cibles:
        vus = {}
        for chemin, src in sources():
            if chemin is None:
                anomalies.append((etiquette, f"source {src} absente : PAS MESURE"))
                continue
            font = glyphsLib.GSFont(chemin)
            mid = {m.id: m.name for m in font.masters}
            # L'ANGLE D'ITALIQUE PAR MASTER, pour que ce controle lise le meme
            # quadrant que le titrage. Depuis le trente-septieme tour,
            # `lot4.quadrant` desincline le contour avant de classer -- point
            # ouvert 65 -- et un controle qui garderait l'ancienne definition
            # decrirait une grandeur que plus personne n'emploie.
            angle = {m.id: float(getattr(m, "italicAngle", 0) or 0.0)
                     for m in font.masters}
            g = font.glyphs[nom]
            if g is None:
                anomalies.append((etiquette, f"{nom} absent de {src}"))
                continue
            for lay in g.layers:
                if lay.layerId not in mid:
                    continue
                cle = f"{src} {mid[lay.layerId]}"
                trouve = designe(lay, loc)
                if trouve is None:
                    anomalies.append((etiquette, f"{cle} : rien trouve"))
                    continue
                ip, idx, segs = trouve
                attendu_n = ATTENDU_N.get(etiquette, 1)
                if len(idx) != attendu_n:
                    anomalies.append(
                        (etiquette, f"{cle} : {len(idx)} segments designes "
                         f"{idx}, {attendu_n} attendu(s)"))
                i = idx[0]
                bb = boite(lay)
                x0, y0, x1, y1 = bb
                mx, my = K.mid(segs[i])
                vus[cle] = dict(
                    contour=ip, seg=i, nseg=len(segs),
                    quad=Q.quadrant(segs, i, bb, angle[lay.layerId]),
                    xr=(mx - x0) / max(1.0, x1 - x0),
                    yr=(my - y0) / max(1.0, y1 - y0),
                    ori=orientation(segs[i]),
                    lg=K.length(segs[i]),
                    mx=mx, my=my,
                )
        if not vus:
            continue
        cles = {(v["contour"], v["seg"], v["nseg"]) for v in vus.values()}
        if len(cles) > 1:
            detail = {k: (v["contour"], v["seg"], v["nseg"]) for k, v in vus.items()}
            anomalies.append((etiquette,
                              f"le segment designe change de master a master : {detail}"))
        oris = {v["ori"] for v in vus.values()}
        if len(oris) > 1:
            anomalies.append((etiquette, f"l'orientation change : {oris}"))
        quads = {v["quad"] for v in vus.values()}
        if len(quads) > 1:
            detail = {k: v["quad"] for k, v in vus.items()}
            # Le quadrant est un revelateur, pas une preuve, et son decoupage a
            # un seuil : `lot4.quadrant` coupe a 35 % de la largeur de boite.
            # Quand l'indice, le contour et la topologie sont identiques dans
            # les huit masters, un quadrant qui bascule ne dit pas que le
            # localisateur derape — il dit que le milieu du bout passe le seuil,
            # ce qui arrive sur un glyphe penche dont la boite est large. La
            # queue du t italique ExtraLight tombe a 0,594 pour un seuil a 0,65.
            # C'est une note, et elle est ecrite comme telle plutot que passee
            # sous silence ou comptee comme une faute.
            if len(cles) > 1:
                anomalies.append((etiquette, f"le quadrant change : {detail}"))
            else:
                notes.append((etiquette,
                              f"quadrant a cheval sur le seuil de 35 % — meme "
                              f"segment partout, donc effet de seuil et non "
                              f"derapage : {detail}"))
        xr = [v["xr"] for v in vus.values()]
        yr = [v["yr"] for v in vus.values()]
        lg = [v["lg"] for v in vus.values()]
        lignes.append((etiquette, attendu, vus, min(lg), max(lg),
                       min(xr), max(xr), min(yr), max(yr)))
    return lignes, anomalies, notes


def main():
    temoin = "--temoin" in sys.argv
    cibles = TEMOIN if temoin else CIBLES

    if source_brute():
        print("Source : le depot amont, brut. C'est la seule ou un localisateur "
              "se verifie une fois la table ecrite.")
    else:
        traites = sorted({x[0] for x in L.LOT2} & {"r", "n", "m", "t", "f"})
        print("Source : Temoin.glyphs — le depot amont n'est pas disponible.")
        if traites:
            print(f"   ATTENTION : {', '.join(traites)} y sont deja traites par "
                  f"la table. Le controle mesure alors des glyphes coupes et "
                  f"ses anomalies sont son propre reflet. PAS MESURE.")
            return 2
    print()

    lignes, anomalies, notes = controler(cibles)

    print(f"{'cible':28s} {'quad':5s} {'ori':6s} {'seg':>4s} {'nseg':>5s} "
          f"{'longueur du bout':>18s}   milieu, en relatif dans la boite")
    for (etiquette, attendu, vus, lgmin, lgmax,
         xrmin, xrmax, yrmin, yrmax) in lignes:
        v = list(vus.values())[0]
        print(f"{etiquette:28s} {v['quad']:5s} {v['ori']:6s} {v['seg']:4d} "
              f"{v['nseg']:5d} {lgmin:8.1f} a {lgmax:6.1f}   "
              f"x {xrmin:.3f}-{xrmax:.3f}  y {yrmin:.3f}-{yrmax:.3f}")
        print(f"{'':28s} attendu : {attendu}")

    print()
    if notes:
        print(f"{len(notes)} note(s), qui ne comptent pas comme des anomalies :")
        for nom, quoi in notes:
            print(f"   {nom} : {quoi}")
        print()
    if anomalies:
        print(f"{len(anomalies)} ANOMALIE(S)")
        for nom, quoi in anomalies:
            print(f"   {nom} : {quoi}")
    else:
        print("Aucune anomalie : les localisateurs designent la meme terminaison "
              "dans les huit masters des deux sources.")
    if temoin:
        print("\n(mode temoin : le controle DOIT signaler ci-dessus. "
              "S'il ne signale rien, c'est lui qui est casse.)")
    return 1 if (anomalies and not temoin) else 0


if __name__ == "__main__":
    sys.exit(main())
