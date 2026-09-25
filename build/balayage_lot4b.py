#!/usr/bin/env python3
"""
Temoin, sous-lot 4b des vingt-deux gestes : les DEUX DIAGONALES, A et X.

Ne dessine rien. Quatre passes, a jouer par numero en argument.

  1  l'inventaire des deux bouts et de leurs localisateurs sur les huit
     masters, l'orientation du flanc voisin — la grandeur qui separe ce
     sous-lot du 4a — le refus des quatre noms de coin, et ce que le
     localisateur rend sur la CONTREFORME du A.
  2  les sorties candidates en unites : l'angle demande et la saturation de la
     borne de `termes.angle_pour_sortie`, puis les TROIS grandeurs du
     deplacement — chemin, plongee, avance — la boite sur ses quatre cotes, le
     hors chasse, l'encre et la topologie a deux resolutions.
  3  l'interligne PAR LE BAS, le point ouvert 21 rejoue sur deux capitales.
  4  le garde-fou de la bande pleine sur les 71 voisins, DANS LES DEUX SENS de
     paire, avec le franchissement par dichotomie et un temoin.

CE QUE LE SOUS-LOT DEMANDE. Nicolas a regarde la planche d'alphabet du
vingt-cinquieme tour et demande, dans la famille « depasse en capitale » : « A
et X, la coupe du titrage ». `lot4.PRESCRIPTIONS` porte les deux formes depuis
le dixieme tour :

  A  `sortantes={"bd"}`, `exclure={"bg","hc"}`, horaire. Le bas droit sort, le
     bas gauche reste plat, le SOMMET reste droit. Sa profondeur propre de 60
     est supprimee au dixieme tour : il prend 44 comme les autres capitales.
  X  `sortantes={"bg"}`, `pointes={"bg":"gauche"}`, `exclure={"bd","hg","hd"}`,
     antihoraire. Un seul bout sortant, en bas a gauche.

**`pointes` NE FAIT AUCUNE MISE EN POINTE.** Lu dans `couper_alignements` :
il ne sert qu'a forcer le sens de rotation par `lot4.sens_pour_pointe`, pour que
le coin qui sort soit celui du cote nomme. Le mot y designe un coin, pas une
operation. La prescription du X est donc une `coupe_sortante` et rien d'autre,
et le prix a chiffrer est celui d'une sortante. Verifie sur les huit masters :
`sens_pour_pointe` et `sens_coin` rendent le meme sens que le coin nomme.

TROIS ARBITRAGES DE CADRAGE, RENDUS AU VINGT-NEUVIEME TOUR AVANT TOUTE MESURE.
Le sommet du A reste droit, comme le titrage : le sous-lot n'a donc qu'une
entree par lettre. La pointe a gauche du X est reprise, ce qui — voir ci-dessus
— revient a la sortante par le coin gauche. Et le regime reste en unites, un
meme nombre ECRIT sur les deux lettres, ce qui fige le point ouvert 51 pour la
cinquieme fois.

CE QUI SEPARE LE 4b DU 4a, ET C'EST LA RAISON DE LA COUPURE. Nicolas a coupe le
lot 4 en deux au vingt-huitieme tour, sur un critere geometrique :

  4a  h, k, N, H — six bouts horizontaux dont les coins coulissent le long d'un
      flanc de FUT, donc vertical, donc le coin part tout droit. Boite
      inchangee en romain, 0,0 unite aux six profondeurs.
  4b  A, X — leurs bouts sont portes par une DIAGONALE. Le coin part de cote,
      la boite s'elargit, et l'approche se paie.

Mesure ici, et la difference entre les deux lettres est du meme ordre que celle
entre les deux sous-lots : le flanc voisin du pied du A est a 69,3 degres de
l'horizontale en romain et 80,6 en italique, celui du X a 54,5 et 47,3. Le A
descend presque droit, le X part de cote.

**LE NOMBRE ECRIT N'EST PAS LA PLONGEE, ET IL FAUT LE DIRE A CHAQUE COLONNE.**
`termes.angle_pour_sortie` vise le chemin parcouru par le coin. Sur un flanc
vertical ce chemin EST la plongee, a un demi-point pres, et les quatre lots
precedents n'ont jamais eu a distinguer les deux. Sur un flanc oblique il se
partage : a 24 unites ecrites, le A plonge de 22,5 et avance de 8,5 en romain,
le X plonge de 19,5 et avance de 13,9. La passe 2 rend les trois grandeurs
separement. Une colonne qui n'en rendrait qu'une a deja fait lire la longueur
d'un bout pour ce que la coupe enlevait, sur le z au vingt-sixieme tour.

**LES DEUX LETTRES NE PAIENT PAS DU MEME COTE, ET LE GARDE-FOU EN DEPEND.** Le
coin du A sort vers la DROITE : son xmax augmente et il quitte sa chasse, donc
c'est le voisin SUIVANT qui paie. Le coin du X sort vers la GAUCHE : son xmin
passe sous zero, donc c'est le voisin PRECEDENT. La passe 4 teste les deux sens
de paire pour les deux cibles, et ce n'est pas du zele : le generateur du point
ouvert 50 n'en testait qu'un jusqu'au vingt-septieme tour, et `f+V` et `f+Y`
ont vecu sous le plancher depuis le lot 1 sans qu'aucun controle puisse le dire.

AUCUN LOCALISATEUR NEUF, ET C'EST LE RESULTAT LE PLUS INATTENDU DU SOUS-LOT. La
passation annonce depuis le vingt-huitieme tour que le A et le X n'ont aucun
localisateur, que le quadrant ne peut pas en tenir lieu, et que c'est le travail
technique principal du lot. Les deux premieres phrases sont vraies, la
troisieme est fausse : `lot2.loc_pied_droit` et `lot2.loc_pied_gauche`, ecrits
pour le lot 1, servent les deux cibles sur les huit masters des deux sources. La
passe 1 le verifie et montre POURQUOI ils departagent au lieu de tomber juste.

**UN CHIFFRE DE LA PASSATION ETAIT FAUX SUR CE POINT PRECIS.** Elle annonce que
`lot4.quadrant` ne rend AUCUN segment droit sur les quatre masters romains du A
et du X, et deux ou trois sur leurs italiques. Mesure : il en rend deux sur le A
et deux ou trois sur le X dans les HUIT masters, romains compris. Ce que le
sondage du vingt-huitieme tour a trouve etait une propriete du sondage. La
conclusion tient quand meme et elle durcit : le quadrant seul ne departage pas,
et ce qui departage est quadrant PLUS horizontalite.

Usage :
    python3 balayage_lot4b.py 1
    python3 balayage_lot4b.py 2 --cible P-A
    python3 balayage_lot4b.py 3
    python3 balayage_lot4b.py 4 --cible P-A
    python3 balayage_lot4b.py 4 --temoin
"""

import math
import os
import sys

import numpy as np
import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import approches as A
import coupe as K
import lot2 as L
import lot4 as Q
import termes as T

# La boite a outils du 4a est importee et non recopiee. Deux copies d'une
# mesure finissent par diverger, et le projet l'a paye sur `loc_sommet_fut`,
# porte en deux exemplaires par `lot2` et `termes`, ce qui a fait rater le test
# d'identite de `refuser_si_perimee`. Ce qui est repris ici ne connait aucune
# cible : `repertoire`, `extremes_servis`, `calques`, `ymin_calque`,
# `ymax_calque`, `orientation`, `segment_vise`, `flanc_du_coin`,
# `appliquer_direct`, `plafond`, `dans_lot2`, `sources`.
import balayage_lot4 as B

AMONT = B.AMONT
AMONT_IT = B.AMONT_IT
ICI = os.path.dirname(os.path.abspath(__file__))

#: Les deux cibles du sous-lot, lues dans `termes.LOCS` pour le reste.
CIBLES = ["P-A", "P-X"]

#: Le coin que le titrage fait sortir, cible par cible, et son oppose. Verifie
#: par la passe 1 au sens de `lot2._coin_vise_est_P`, puis confronte a ce que
#: `lot4.sens_pour_pointe` et `lot4.sens_coin` rendent sur le meme bout : trois
#: chemins qui doivent tomber sur le meme sens, et non un seul qu'on croit.
COIN = {"P-A": "droite", "P-X": "gauche"}
AUTRE = {"P-A": "gauche", "P-X": "droite"}

#: Les deux bouts sont poses sur la LIGNE DE BASE, et les deux gestes
#: DESCENDENT. Pour l'affichage seulement : la plongee est toujours mesuree
#: contre l'ordonnee du bout brut et jamais contre une metrique declaree.
ALIGNEMENT = {"P-A": "base", "P-X": "base"}

#: Les interlignes de `gabarits/temoin.css`. 1,15 est celui des titres et c'est
#: le maillon court.
INTERLIGNES = B.INTERLIGNES

#: La borne haute de la recherche de sortie, en unites. Le lot 3 a paye une
#: borne a 60 qui se faisait passer pour un refus de la geometrie.
BORNE = B.BORNE

#: La borne en dur de `termes.angle_pour_sortie`, recopiee — et le point ouvert
#: 53 dit ce que cette recopie coute : une modification dans `termes.py`
#: rendrait la detection fausse en silence. Recopiee quand meme, comme dans
#: `balayage_lot4.py`, faute d'exposition.
BORNE_ANGLE = B.BORNE_ANGLE if hasattr(B, "BORNE_ANGLE") else 45.0

#: La borne de `lot4.plafond_coupe` est a 70 degres EN DUR et la fonction la
#: rend quand rien ne refuse ; elle rend 0,0 la ou aucune rotation ne
#: s'applique, ce qui se lit comme un plafond nul alors que c'est un refus. Les
#: deux se lisent comme des faits de la lettre et n'en sont pas. La passe 1
#: passe 89 degres pour que la borne ne morde jamais avant la geometrie, et elle
#: nomme les deux cas.
BORNE_PLAFOND = 89.0

#: Les profondeurs candidates de la passe 4, lues dans `termes.ETATS` pour le
#: reste. Le majorant sert a trouver l'ensemble des paires concernees en une
#: seule fois : plus le coin sort, plus le couloir se ferme, donc l'etat le plus
#: profond MAJORE le risque. La monotonie n'est pas supposee, la passe 4 la
#: verifie sur l'ensemble candidat et le dit si elle est dementie.
PROFONDEURS = [12.0, 22.0, 24.0, 32.0, 44.0]


# ------------------------------------------------------------------ passes

def passe1(srcs):
    print("\n=== 1. l'inventaire des deux bouts, sur les huit masters")
    print("  Ce que la passe verifie, et pourquoi chaque colonne existe :")
    print("   - le contour et l'indice designes, identiques d'un master a")
    print("     l'autre, sinon l'interpolation casse ;")
    print("   - les candidats du meme contour, qui disent si le localisateur a")
    print("     DEPARTAGE ou s'il a eu de la chance — c'est le defaut de")
    print("     `loc_sommet_fut` sur le N et le H, trouve au 4a ;")
    print("   - l'ecart entre les deux candidats, en unites : un departage a")
    print("     500 unites d'ecart n'est pas un departage a 1 unite, et le t")
    print("     du vingtieme tour se jouait a UNE unite ;")
    print("   - ce que le localisateur rend sur la CONTREFORME du A, qui est")
    print("     un triangle a trois segments droits : il la designe, et ce qui")
    print("     l'arrete est le filtre sur le signe de l'aire du dix-huitieme")
    print("     tour. Le piege du `Aogonek` mot pour mot ;")
    print("   - l'orientation du FLANC VOISIN, la grandeur qui decide de la")
    print("     direction du geste et qui separe ce sous-lot du 4a ;")
    print("   - le plafond de la coupe RENTRANTE, avec la borne portee a")
    print(f"     {BORNE_PLAFOND:.0f} degres : `lot4.plafond_coupe` en porte une a 70 en")
    print("     dur et la rend quand rien ne refuse, et il rend 0,0 la ou")
    print("     aucune rotation ne s'applique. Les deux se lisent comme des")
    print("     faits de la lettre et n'en sont pas.")

    for cle in CIBLES:
        nom, loc = T.LOCS[cle]
        dej = B.dans_lot2(cle)
        etat = ("AUCUNE entree de LOT2" if not dej
                else f"ATTENTION : {len(dej)} entree(s) de LOT2 sur {nom}")
        print(f"\n  --- {cle} : {nom}, {loc.__name__}, coin « {COIN[cle]} », "
              f"plonge   [{etat}]")
        print(f"      {'master':22s} {'cont/seg':9s} {'candidats':14s} "
              f"{'ecart':>7s} {'y bout':>7s} {'quad':5s} {'creux':10s} "
              f"{'flanc du coin':24s} {'plafond rentrante':>18s}")
        for tag, font in srcs:
            for master, lay in B.calques(font, nom):
                r = B.segment_vise(lay, cle)
                if r is None:
                    print(f"      {tag + ' ' + master:22s} AUCUN BOUT DESIGNE")
                    continue
                k, segs, idx = r
                i = idx[0]
                cand = L.lines(segs, vertical=False)
                xs = sorted(K.mid(segs[j])[0] for j in cand
                            if abs(K.mid(segs[j])[1]
                                   - min(K.mid(segs[c])[1] for c in cand)) < 12)
                ecart = (xs[-1] - xs[0]) if len(xs) > 1 else 0.0
                tous = [K.to_segs(p) for p in L.paths(lay)]
                bb = Q.boite([sg for sg in tous if K.area(sg) >= 0])
                qd = Q.quadrant(segs, i, bb)
                # Ce que le localisateur rend sur les contours de CREUX, que le
                # filtre sur le signe de l'aire ecarte. Zero n'est pas la bonne
                # reponse : la reponse utile est « il en designe un, et voici
                # lequel », parce que c'est ce qui dit que le filtre porte.
                creux = []
                for sg in tous:
                    if K.area(sg) >= 0:
                        continue
                    ic = loc(sg)
                    if ic:
                        creux.append(ic[0])
                fl = B.flanc_du_coin(lay, cle, COIN[cle])
                sens = T.sens_pour_sortie(segs, i, COIN[cle]) \
                    if hasattr(T, "sens_pour_sortie") else None
                pl = Q.plafond_coupe(segs, i, sens or -1, hi=BORNE_PLAFOND)
                mot = ("BORNE, rien ne refuse" if pl >= BORNE_PLAFOND - 0.05
                       else "REFUS, aucune rotation" if pl <= 0.05
                       else f"{pl:.1f}deg")
                yb = B.ordonnee_bout(lay, cle)
                print(f"      {tag + ' ' + master:22s} {str(k) + '/' + str(i):9s} "
                      f"{str(cand):14s} {ecart:7.1f} {yb:7.1f} {qd:5s} "
                      f"{str(creux) if creux else 'aucun':10s} {fl:24s} "
                      f"{mot:>18s}")

    print("\n  --- les deux copies de `loc_pied_droit`, `lot2` et `termes`")
    print("      Le projet en porte deux exemplaires du meme nom, et c'est ce")
    print("      qui a fait echouer le test d'identite de")
    print("      `refuser_si_perimee` au vingt-septieme tour. Elles doivent")
    print("      rendre le meme indice, et ce n'est pas suppose ici.")
    ok = True
    for tag, font in srcs:
        for nom in ("A", "X"):
            for master, lay in B.calques(font, nom):
                for p in L.paths(lay):
                    sg = K.to_segs(p)
                    if K.area(sg) < 0:
                        continue
                    a, b = L.loc_pied_droit(sg), T.loc_pied_droit(sg)
                    c, d = L.loc_pied_gauche(sg), T.loc_pied_gauche(sg)
                    if a != b or c != d:
                        ok = False
                        print(f"      ECART {tag} {nom} {master} : "
                              f"droit {a} vs {b}, gauche {c} vs {d}")
    print("      " + ("les deux copies s'accordent sur les huit masters"
                      if ok else "ECART TROUVE, voir ci-dessus"))

    print("\n  --- le refus du nom de coin, les quatre noms sur chaque cible")
    print("      Attendu : « gauche » et « droite » passent, « bas » et")
    print("      « haut » LEVENT, les deux bouts etant horizontaux. C'est le")
    print("      refus pose dans `_coin_vise_est_P` au vingt-septieme tour.")
    for cle in CIBLES:
        nom, _ = T.LOCS[cle]
        cpt = {n: 0 for n in ("gauche", "droite", "bas", "haut")}
        tot = 0
        for tag, font in srcs:
            for master, lay in B.calques(font, nom):
                r = B.segment_vise(lay, cle)
                if r is None:
                    continue
                _, segs, idx = r
                tot += 1
                for n4 in cpt:
                    try:
                        L._coin_vise_est_P(segs, idx[0], n4)
                        cpt[n4] += 1
                    except ValueError:
                        pass
        print(f"      {cle:6s} {nom:2s}   " + "   ".join(
            f"{n} {cpt[n]}/{tot}" for n in ("gauche", "droite", "bas", "haut")))

    print("\n  --- les trois chemins vers le sens de rotation")
    print("      `sens_pour_sortie` par le coin nomme, `sens_pour_pointe` du")
    print("      titrage, et `sens_coin` par le cote de la prescription. Les")
    print("      trois doivent tomber sur le meme sens : un seul chemin qu'on")
    print("      croit est un choix implicite, et le lot 3 a montre qu'un nom")
    print("      de coin peut passer d'un cote de l'axe et lever de l'autre.")
    cote = {"P-A": "horaire", "P-X": "antihoraire"}
    for cle in CIBLES:
        nom, _ = T.LOCS[cle]
        for tag, font in srcs:
            for master, lay in B.calques(font, nom):
                r = B.segment_vise(lay, cle)
                if r is None:
                    continue
                segs, i = r[1], r[2][0]
                xs = [c for s in segs for c in (s["p0"][0], s["p3"][0])]
                cx = (min(xs) + max(xs)) / 2.0
                s1 = T.sens_pour_sortie(segs, i, COIN[cle])
                s2 = Q.sens_pour_pointe(segs, i, COIN[cle])
                s3 = Q.sens_coin(segs, i, cx, cote[cle])
                acc = "OK" if s1 == s2 == s3 else "DESACCORD"
                print(f"      {cle:6s} {tag + ' ' + master:22s} "
                      f"sortie {s1}  pointe {s2}  cote({cote[cle]}) {s3}   {acc}")


def passe2(srcs, seulement=None):
    print("\n=== 2. les sorties candidates : trois grandeurs et non une")
    print("  Le nombre ecrit est le CHEMIN parcouru par le coin, ce que")
    print("  `termes.angle_pour_sortie` vise. Sur les quatre lots precedents")
    print("  les flancs etaient verticaux et ce chemin valait la plongee a un")
    print("  demi-point pres ; ici il se partage entre une plongee et une")
    print("  avance laterale, et les deux se paient a des endroits differents.")
    print("  Les colonnes :")
    print("   - angle : ce que la dichotomie demande, et SATURE quand elle")
    print(f"     touche la borne de {BORNE_ANGLE:.0f} degres de l'outil — point ouvert 53 ;")
    print("   - chemin / plongee / avance : les trois grandeurs ;")
    print("   - la boite sur ses quatre cotes, l'elargissement, et le hors")
    print("     chasse. Un xmin qui passe sous zero est le signe exact qui")
    print("     avait mene aux quatre contacts du lot 1 : de la matiere sort a")
    print("     GAUCHE de l'origine du glyphe, donc devant la lettre d'avant ;")
    print("   - l'encre, seule grandeur qui prouve qu'une coupe a eu lieu")
    print("     quand la geometrie ne bouge pas dans la direction mesuree ;")
    print("   - la topologie a deux resolutions : un compte obtenu par")
    print("     rastérisation depend de la resolution des qu'il y a une")
    print("     quasi-tangence, et le projet l'a paye sur le Ccedilla.")
    import souscrits as S
    for cle in [c for c in CIBLES if seulement is None or c == seulement]:
        nom, loc = T.LOCS[cle]
        print(f"\n  --- {cle} : {nom}, coin « {COIN[cle]} », plonge")
        for tag, font in srcs:
            for master, lay in B.calques(font, nom):
                r = B.segment_vise(lay, cle)
                if r is None:
                    print(f"    {tag} {master} : AUCUN BOUT, rien de mesure")
                    continue
                _, segs, idx = r
                i = idx[0]
                base, place0 = T.segs_etat(lay, cle, None)
                b0 = T.boite(base)
                chasse = float(lay.width)
                # L'orientation du flanc voisin du coin nomme, prise par le
                # meme chemin que `flanc_du_coin` : c'est LA grandeur qui
                # separe ce sous-lot du 4a, et elle est lue sur le contour.
                n = len(segs)
                est_P = L._coin_vise_est_P(segs, i, COIN[cle])
                j = (i - 1) % n if est_P else (i + 1) % n
                fl = B.orientation(segs, j)
                plmax, sature_u = B.plafond(cle, lay, COIN[cle])
                print(f"\n    {tag} {master}   bout {K.seg_len(segs[i]):.0f} u, "
                      f"flanc voisin seg {j} a {fl:.1f}deg, chasse "
                      f"{chasse:.0f}, boite ({b0[0]:.0f},{b0[1]:.0f},"
                      f"{b0[2]:.0f},{b0[3]:.0f}), sortie max {plmax:.1f} u"
                      f"{' (BORNE de l outil)' if sature_u else ''}")
                # `deficit` = le nombre ECRIT moins la plongee REELLE. C'est la
                # colonne qui dit que le nombre de la table n'est pas la
                # profondeur, et elle n'avait aucune raison d'exister aux
                # quatre lots precedents : leurs flancs etaient verticaux, donc
                # elle y aurait valu zero partout — une colonne uniforme, et le
                # projet en a rencontre six.
                print(f"      {'etat':48s} {'angle':>6s} {'chemin':>7s} "
                      f"{'plongee':>8s} {'avance':>7s} {'deficit':>7s} "
                      f"{'xmin':>7s} {'ymin':>7s} {'xmax':>7s} {'d.larg':>7s} "
                      f"{'hors ch':>7s} {'encre%':>7s} {'topo':>10s}")
                for code, etq, fn in T.ETATS[cle]:
                    if fn is None:
                        continue
                    u = B.cible_de(etq)
                    coin_etat = AUTRE[cle] if "autre coin" in etq else COIN[cle]
                    th, sat = B.rotation_pour(lay, cle, coin_etat, u)
                    try:
                        apres, place1 = T.segs_etat(lay, cle, fn)
                    except Exception as e:
                        print(f"      {etq:48s} REFUS : {e}")
                        continue
                    if place1 is None or place0 is None:
                        print(f"      {etq:48s} AUCUN BOUT PLACE")
                        continue
                    # Le coin qui a bouge, et son deplacement decompose. Pris
                    # du producteur : `place` est ce que `appliquer_etat` rend,
                    # jamais une reconstruction du contour apres coup. Le
                    # quatorzieme tour a paye une verification qui retrouvait
                    # les coins d'une coupe par heuristique et rendait
                    # 1,5 degre pour une rotation de 20.
                    dP = np.array(place1[2]) - np.array(place0[2])
                    dQ = np.array(place1[3]) - np.array(place0[3])
                    mv = dP if float(np.hypot(*dP)) > float(np.hypot(*dQ)) else dQ
                    chem = float(np.hypot(*mv))
                    b1 = T.boite(apres)
                    e0, e1 = T.encre(base), T.encre(apres)
                    dl = (b1[2] - b1[0]) - (b0[2] - b0[0])
                    hors = (T.hors_chasse(apres, lay.width)
                            - T.hors_chasse(base, lay.width))
                    try:
                        with T.avec_etat(lay, cle, fn):
                            ta, ct, acc = S.topologie(lay)
                        topo = f"{ta}/{ct}" + ("" if acc else " DIVERGE")
                    except Exception:
                        topo = "?"
                    marque = ""
                    if sat:
                        marque = "  SATURE"
                    elif b1[0] < -0.05 <= b0[0]:
                        marque = "  xmin<0"
                    print(f"      {etq:48s} "
                          f"{'  none' if th is None else f'{th:6.2f}'} "
                          f"{chem:7.1f} {float(mv[1]):8.1f} {float(mv[0]):7.1f} "
                          f"{(u or chem) - abs(float(mv[1])):7.1f} "
                          f"{b1[0]:7.1f} {b1[1]:7.1f} {b1[2]:7.1f} {dl:7.1f} "
                          f"{hors:7.1f} {100.0 * (e1 - e0) / e0:7.2f} "
                          f"{topo:>10s}{marque}")


def passe3(srcs):
    print("\n=== 3. l'interligne PAR LE BAS, le point ouvert 21 rejoue")
    print("  Le lot 3 a chiffre ce point sur le p, le y et le Y : le glyphe le")
    print("  plus bas du repertoire servi n'est pas le p mais le g, par le")
    print("  debord de sa courbe, donc le p avait 24 a 43 unites de plongee")
    print("  gratuite. Les deux cibles d'ici sont des CAPITALES posees sur la")
    print("  ligne de base, comme le Y du lot 3 dont l'ymin vaut 0,0 : leur")
    print("  plongee gratuite est donc celle du Y, et elle doit etre mesuree")
    print("  et non deduite de sa valeur.")
    print("\n  Le jour est interligne x 1000 − plafond + plancher, mesure sur")
    print("  le repertoire du sous-ensemble, composites decomposes.")
    rep = B.repertoire()
    print(f"\n  repertoire du sous-ensemble : {len(rep)} caracteres")
    for tag, font in srcs:
        ext = B.extremes_servis(font, rep)
        print(f"\n  --- {tag}")
        for mo in font.masters:
            (hi, gh), (lo, gl) = ext[mo.name]
            print(f"\n    {mo.name:20s} plafond {hi:7.1f} ({gh})   "
                  f"plancher {lo:7.1f} ({gl})")
            for cle in CIBLES:
                nom, _ = T.LOCS[cle]
                lays = dict(B.calques(font, nom))
                if mo.name not in lays:
                    continue
                yb = B.ymin_calque(lays[mo.name])
                print(f"      {nom:2s} ({cle:5s}) ymin {yb:7.1f} -> plongee "
                      f"gratuite {yb - lo:6.1f} u avant de devenir le plancher")
            for il in INTERLIGNES:
                print(f"      interligne {il:.2f} : jour "
                      f"{il * 1000.0 - hi + lo:7.1f} u")

    print("\n  --- ce que chaque etat coute sur le jour, a l'interligne le plus")
    print("      serre du site : 1,15, celui des titres h1 a h4")
    print("      L'atteint est MESURE sur le calque apres geste et non deduit")
    print("      de la profondeur demandee, `angle_pour_sortie` visant le")
    print("      chemin du coin et non sa composante verticale — et sur une")
    print("      diagonale l'ecart entre les deux est de 8 a 22 %.")
    pires = []
    for tag, font in srcs:
        ext = B.extremes_servis(font, rep)
        for cle in CIBLES:
            nom, _ = T.LOCS[cle]
            print(f"\n    {tag} {nom} ({cle})")
            print(f"      {'master':20s} {'etat':48s} {'atteint':>8s} "
                  f"{'plafond':>9s} {'plancher':>9s} {'jour 1,15':>10s} "
                  f"{'cout':>7s}")
            for master, lay in B.calques(font, nom):
                (hi, _), (lo, _) = ext[master]
                jour0 = 1.15 * 1000.0 - hi + lo
                for code, etq, fn in T.ETATS[cle]:
                    if fn is None:
                        continue
                    try:
                        with T.avec_etat(lay, cle, fn):
                            att = B.ymin_calque(lay)
                    except Exception:
                        print(f"      {master:20s} {etq:48s} REFUS")
                        continue
                    pl = min(lo, att)
                    jour = 1.15 * 1000.0 - hi + pl
                    cout = jour - jour0
                    marque = "" if cout >= -0.05 else "   PAYE"
                    pires.append((att - lo, tag, nom, master, etq, cout))
                    print(f"      {master:20s} {etq:48s} {att:8.1f} "
                          f"{hi:9.1f} {pl:9.1f} {jour:10.1f} "
                          f"{cout:+7.1f}{marque}")

    # La colonne de cout peut etre uniforme a +0,0 et ne rien cacher, mais elle
    # ne doit pas pouvoir se lire comme une grandeur morte : le projet a
    # rencontre six colonnes uniformes, dont deux qui mentaient. La marge la
    # plus courte est donc imprimee, et c'est elle qui dit pourquoi le zero
    # tient — le meme raisonnement que la plongee gratuite du p au lot 3.
    if pires:
        marge, tg, nm, ms, eq, ct = min(pires, key=lambda t: t[0])
        payants = [p for p in pires if p[5] < -0.05]
        print(f"\n  --- pourquoi le zero de la colonne de cout n'est pas "
              "trivial")
        print(f"      {len(pires)} etats mesures, {len(payants)} qui coutent "
              "quelque chose sur le jour.")
        print(f"      L'etat le plus profond des deux cibles reste a "
              f"{marge:.1f} unites AU-DESSUS du plancher du repertoire servi :")
        print(f"      {tg} {nm} {ms}, « {eq} ».")
        print("      Le plancher est le g par le debord de sa courbe, comme au")
        print("      lot 3, et aucune des deux capitales ne s'en approche.")


def passe4(srcs, seulement=None, temoin=False):
    """Le garde-fou de la bande pleine, avec le franchissement par dichotomie.

    Requis et non joue en confirmation. Le prompt du projet l'impose pour tout
    geste qui fait sortir de la matiere hors de la boite d'origine, et les deux
    cibles le font : le A par la droite, hors de sa chasse ; le X par la
    gauche, sous l'origine du glyphe.

    **LES DEUX SENS DE PAIRE, ET UN PAR LETTRE.** Le generateur du point ouvert
    50 n'en testait qu'un jusqu'au vingt-septieme tour — le voisin en premier —
    ce qui etait juste pour les trois pieds du lot 1 dont le cote gauche
    descend et aveugle au Y, dont le cote droit descend. `f+V` et `f+Y` ont
    vecu sous le plancher depuis le lot 1 sans qu'aucun controle puisse le
    dire. Ici les deux cas coexistent dans le meme sous-lot, donc les deux sens
    sont testes pour les deux cibles.

    **LA REFERENCE EST L'ETAT SERVI.** `Temoin.glyphs` porte les lots 1 a 4a,
    donc entre autres la queue du q coupee a 12 degres depuis le onzieme tour,
    qui ouvre le couloir de 1 a 6 unites. Mesure contre Atkinson brut, le
    verdict du lot 3 est passe de huit masters a deux quand la reference a ete
    corrigee : c'est la correction la plus couteuse du vingt-septieme tour.

    **LE FRANCHISSEMENT ET NON UN VERDICT.** Un garde-fou qui rend « non » sans
    dire a partir de quelle profondeur fait refaire le tour. La passe procede
    en trois temps, et le premier est ce qui la rend rapide :

      A. l'etat le plus profond, 44 unites, sur les 71 voisins fois deux sens
         fois huit masters. Plus le coin sort, plus le couloir se ferme, donc
         cet etat MAJORE le risque et il donne l'ensemble des paires
         concernees en un seul balayage complet.
      B. les cinq profondeurs candidates sur cet ensemble seul, qui est petit.
         La monotonie n'est pas supposee : elle est verifiee ici et la passe le
         dit si elle est dementie, auquel cas l'etape A ne majore plus rien.
      C. une dichotomie entre les deux profondeurs qui encadrent le passage
         sous le plancher, pour rendre le chiffre exact.

    Le critere est le plancher de jour, `approches.JOUR_MIN`, celui du
    vingt-sixieme tour, et non « jamais plus serre qu'Atkinson » : sur une
    paire ou une matiere descendante rencontre une matiere descendante, rendre
    le couloir d'Atkinson demanderait d'annuler le geste.

    Trois cas et non deux, distinction posee au vingt-septieme tour : une paire
    sous le plancher n'est une anomalie que si le geste l'a AGGRAVEE. Une paire
    deja serree que le geste ne bouge pas est une information — et le 4a en a
    trouve quatre sur le k, dont `k+A` a 7,8 unites et `k+X` a 14,0, deux
    paires qui concernent justement les lettres d'ici.
    """
    print("\n=== 4. le garde-fou de la bande pleine, sur les 71 voisins")
    print("  Ce sous-lot fait DESCENDRE de la matiere et la fait sortir")
    print("  LATERALEMENT, des deux cotes selon la lettre. Deux risques, et")
    print("  cette passe n'en couvre qu'un : le voisin lateral. La descendante")
    print("  de la ligne suivante est traitee par la passe 3, et aucune mesure")
    print("  de paire ne peut la voir.")
    print(f"  Critere : le plancher de jour de {A.JOUR_MIN:.0f} unites.")
    print("  Les DEUX sens de paire, pour les deux cibles : le A sort a")
    print("  droite donc c'est le voisin SUIVANT qui paie, le X sort a gauche")
    print("  donc c'est le PRECEDENT.")
    import dessin as D
    import check_approches as CA

    if temoin:
        # Le temoin reste sur l'AMONT, et il le faut : il replonge le pied
        # gauche du m, qui EST dans `lot2.LOT2` depuis le vingt-cinquieme tour,
        # donc l'etat servi le porte deja et son crenage est corrige par
        # `paires_pieds.py`. Mesure sur l'amont il retrouve `q+m` a −22,0, la
        # valeur du lot 1. Un temoin calibre sur rien ne prouve rien.
        cas = [("TEMOIN", "m", L.loc_pied_gauche, "gauche", [22.0])]
    else:
        cas = []
        for cle in [c for c in CIBLES if seulement is None or c == seulement]:
            nom, loc = T.LOCS[cle]
            dej = B.dans_lot2(cle)
            if dej:
                print(f"\n  {cle} : REFUS. {len(dej)} entree(s) de LOT2 "
                      f"portent deja {nom} — {[e[1] for e in dej]}.")
                print("    Reposer une sortante sur un bout deja sorti laisse")
                print("    deux points confondus, et `_sortante` leve. Pour")
                print("    mesurer un etat ECRIT, c'est une planche de")
                print("    verification qu'il faut, pas ce balayage.")
                continue
            cas.append((cle, nom, loc, COIN[cle], list(PROFONDEURS)))

    bases = ((("rom", os.path.join(ICI, "Temoin.glyphs")),
              ("ital", os.path.join(ICI, "Temoin-Italic.glyphs")))
             if not temoin else (("rom", AMONT), ("ital", AMONT_IT)))
    print(f"  Reference : {'l amont brut' if temoin else 'l etat servi, lots 1 a 4a compris'}.")

    for cle, nom, loc, coin, profs in cas:
        print(f"\n  {cle} {nom} : le coin « {coin} » plonge")
        for tag, chemin in bases:
            if not os.path.exists(chemin):
                print(f"    {tag} : {chemin} absent, RIEN DE MESURE.")
                continue
            amont = glyphsLib.GSFont(chemin)
            umax = max(profs)

            # --- A. le majorant, balayage complet des 71 voisins, deux sens
            tem = glyphsLib.GSFont(chemin)
            rate = False
            for master, lay in B.calques(tem, nom):
                if not B.appliquer_direct(lay, loc, T._sortante(umax, coin)):
                    print(f"    {tag} {master} : AUCUN BOUT, etat non applique")
                    rate = True
            if rate:
                continue
            candidats = {}
            for m in tem.masters:
                sa, st = D.Source(amont, m.name), D.Source(tem, m.name)
                serre, sous, deja = [], [], []
                for v in CA.VOISINS_F:
                    vn = v if len(v) > 1 else D.nom_glyphe(amont, v)
                    if vn is None or amont.glyphs[vn] is None:
                        continue
                    for a, b in ((vn, nom), (nom, vn)):
                        try:
                            k = A.kern(amont, m.id, a, b)
                            pa = A.couloir_plein(sa, a, b, k)
                            pt = A.couloir_plein(st, a, b, k)
                        except Exception:
                            continue
                        if None in (pa, pt):
                            continue
                        if pt < pa - 0.5:
                            serre.append((a, b, pa, pt))
                        if pt < A.JOUR_MIN and pt < pa - 0.5:
                            sous.append((a, b, pa, pt))
                        elif pt < A.JOUR_MIN:
                            deja.append((a, b, pa, pt))
                serre.sort(key=lambda t: t[3])
                # Le couloir EXACT, sur les seules paires que `couloir_plein`
                # signale. Il est conservateur par construction — voir
                # `couloir_exact` — donc ce qu'il ne signale pas est sur, et il
                # n'y a rien a verifier ailleurs. C'est aussi ce qui rend la
                # verification gratuite : l'ensemble signale est petit.
                faux = []
                for a, b, pa, pt in list(sous):
                    xt = couloir_exact(st, a, b, A.kern(amont, m.id, a, b))
                    if xt is not None and xt >= A.JOUR_MIN:
                        faux.append((a, b, pt, xt))
                det = ("rien ne se resserre" if not serre else
                       ", ".join(f"{a}+{b} {pa:.1f}->{pt:.1f}"
                                 for a, b, pa, pt in serre[:5]))
                al = ("" if not sous else
                      f"   PASSE SOUS {A.JOUR_MIN:.0f} u : " +
                      ", ".join(f"{a}+{b} {pa:.1f}->{pt:.1f}"
                                for a, b, pa, pt
                                in sorted(sous, key=lambda t: t[3])[:4]))
                if faux:
                    al += ("   [FAUSSE ALERTE de couloir_plein, le couloir "
                           "EXACT tient : " +
                           ", ".join(f"{a}+{b} {pt:.1f} -> vrai {xt:.1f}"
                                     for a, b, pt, xt in faux) + "]")
                inf = ("" if not deja else
                       f"   [deja sous {A.JOUR_MIN:.0f} u dans Atkinson, sans "
                       "rapport avec le geste : " +
                       ", ".join(f"{a}+{b} {pa:.1f}"
                                 for a, b, pa, pt
                                 in sorted(deja, key=lambda t: t[3])[:4]) + "]")
                print(f"    {tag} a{umax:.0f}u  {m.name:20s} "
                      f"{len(serre):2d} resserree(s), {len(sous):2d} passee(s) "
                      f"sous le plancher ; {det}{al}{inf}")
                if sous:
                    candidats[m.name] = [(a, b) for a, b, _, _ in sous]

            if not candidats:
                print(f"    {tag} : aucune paire ne passe sous le plancher a "
                      f"{umax:.0f} u, l'etat le plus profond. Les profondeurs "
                      "moindres sont donc gratuites a fortiori — la monotonie "
                      "est verifiee ci-dessous.")

            # --- B. les profondeurs candidates sur l'ensemble candidat, et la
            #        monotonie verifiee au lieu d'etre supposee.
            paires = sorted({p for ps in candidats.values() for p in ps})
            if not paires:
                paires = []
            if paires:
                print(f"\n    {tag} : le franchissement, sur les "
                      f"{len(paires)} paire(s) concernee(s)")
                print("      Deux lignes par paire : `plein` est ce que")
                print("      `approches.couloir_plein` rend et il est")
                print("      CONSERVATEUR ; `exact` est le minimum sur les")
                print("      couples d'intervalles d'encre. Voir")
                print("      `couloir_exact` pour ce qui les separe.")
                print(f"      {'paire':16s} {'master':20s} {'mesure':7s} " +
                      " ".join(f"{u:>8.0f}u" for u in profs) +
                      f" {'franchit':>12s}")
            couloirs, exacts = {}, {}
            for u in profs:
                tem = glyphsLib.GSFont(chemin)
                for master, lay in B.calques(tem, nom):
                    B.appliquer_direct(lay, loc, T._sortante(u, coin))
                for m in tem.masters:
                    if m.name not in candidats:
                        continue
                    st = D.Source(tem, m.name)
                    for a, b in candidats[m.name]:
                        try:
                            k = A.kern(amont, m.id, a, b)
                            couloirs[(m.name, a, b, u)] = \
                                A.couloir_plein(st, a, b, k)
                            exacts[(m.name, a, b, u)] = \
                                couloir_exact(st, a, b, k)
                        except Exception:
                            couloirs[(m.name, a, b, u)] = None
                            exacts[(m.name, a, b, u)] = None
            monotone = True
            for mname, ps in candidats.items():
                for a, b in ps:
                    vals = [couloirs.get((mname, a, b, u)) for u in profs]
                    if any(v is None for v in vals):
                        continue
                    if any(vals[j + 1] > vals[j] + 0.5
                           for j in range(len(vals) - 1)):
                        monotone = False
            for a, b in paires:
                for mname in sorted(candidats):
                    if (a, b) not in candidats[mname]:
                        continue
                    vals = [couloirs.get((mname, a, b, u)) for u in profs]
                    vex = [exacts.get((mname, a, b, u)) for u in profs]
                    # --- C. la dichotomie entre les deux profondeurs qui
                    #        encadrent le passage sous le plancher. Elle porte
                    #        sur la mesure EXACTE : c'est celle qui dit ou la
                    #        lettre gene vraiment, et le franchissement de la
                    #        mesure conservatrice n'est qu'une borne basse.
                    for nomm, v, dicho in (("plein", vals, False),
                                           ("exact", vex, True)):
                        cols = " ".join("    none" if x is None else f"{x:9.1f}"
                                        for x in v)
                        seuil = _franchissement(chemin, nom, loc, coin, mname,
                                                a, b, amont, D, profs, v,
                                                exact=dicho)
                        print(f"      {a + '+' + b if nomm == 'plein' else '':16s} "
                              f"{mname if nomm == 'plein' else '':20s} "
                              f"{nomm:7s} {cols} {seuil:>12s}")
            if paires:
                print("      monotonie du couloir en fonction de la "
                      f"profondeur : {'verifiee' if monotone else 'DEMENTIE'}")
                if not monotone:
                    print("      Le majorant a 44 u ne majore donc plus, et")
                    print("      l'etape A de cette passe ne suffit plus a")
                    print("      trouver l'ensemble des paires concernees.")


# ------------------------------------------------------------------ outils

def couloir_exact(src, a, b, k=0.0):
    """Le couloir vrai entre deux lettres : le minimum sur les COUPLES d'encre.

    **`approches.couloir_plein` n'est pas un couloir, c'est un minorant**, et le
    vingt-neuvieme tour l'a mesure. Il calcule `(w + min(croisements de b)) −
    max(croisements de a)`, c'est-a-dire l'ecart entre le bord le plus a droite
    de la premiere lettre et le bord le plus a gauche de la seconde. C'est le
    couloir vrai tant que chaque lettre presente UN SEUL intervalle d'encre a la
    hauteur mesuree. Des qu'une des deux en presente deux disjoints, la mesure
    compare deux morceaux qui ne se font pas face, et elle rend un
    chevauchement qui n'existe pas.

    LE CAS MESURE, ET IL EST DANS LE REPERTOIRE SERVI. La queue du q a un LOBE
    disjoint de sa panse : a l'ExtraBold, a y = −20,42, le q presente
    (397,4 – 580,7) pour sa panse et (683,4 – 684,9) pour la pointe de sa
    queue, qui sort de 73 unites hors de sa chasse de 612. Sur `q+X` a
    25,5 unites de sortante, l'eperon du X occupe (607,5 – 611,2) a cette
    hauteur : il tient ENTIEREMENT dans le blanc du q, entre 580,7 et 683,4.
    Le couloir vrai vaut 26,8 unites a gauche et 72,2 a droite, et
    `couloir_plein` rend **−77,44**, soit un contact franc. Le comptage de
    taches d'encre a 600 et 1800 pixels de cadratin rend deux taches, sans
    fusion, aux deux resolutions : c'est la mesure independante qui a fait
    chercher.

    CE QUE LE DEFAUT PEUT ET NE PEUT PAS FAIRE, ET C'EST LA PARTIE RASSURANTE.
    `min(bords gauches de b) − max(bords droits de a)` est inferieur ou egal a
    tout ecart reel entre un morceau de a et un morceau de b. **Le defaut est
    donc conservateur par construction : il peut inventer un contact, il ne
    peut pas en rater un.** Aucun defaut servi ne peut se cacher derriere lui,
    et un zero de sa part reste un verdict fort. Ce qu'il peut avoir coute, en
    revanche, c'est un ecartement plus large que necessaire dans
    `paires_pieds.py` et `paires_F.py`, dont les valeurs sont bornees par lui.

    Cette fonction reste ICI et ne touche pas `approches.py`. Ce balayage
    n'ecrit rien ; changer le garde-fou du projet toucherait
    `check_approches.py`, `paires_pieds.py`, `paires_F.py` et les quatre lots
    ecrits, et c'est un arbitrage de Nicolas, pas un effet de bord de ce tour.
    """
    ca, cb = src.contours(a), src.contours(b)
    w = src.width(a) + k
    pire = None
    for y in A.bandes(A.DESC, A.ASC):
        xa, xb = A.croisements(ca, y), A.croisements(cb, y)
        if not xa or not xb:
            continue
        ia = [(xa[j], xa[j + 1]) for j in range(0, len(xa) - 1, 2)]
        ib = [(xb[j] + w, xb[j + 1] + w) for j in range(0, len(xb) - 1, 2)]
        for p, q in ia:
            for r, s in ib:
                # Deux intervalles qui se chevauchent vraiment : ecart negatif,
                # et c'est la profondeur du chevauchement. Sinon, l'ecart est la
                # distance entre eux, dans l'ordre ou ils se presentent.
                ec = (-min(q - r, s - p) if (p < s and r < q)
                      else (r - q if r >= q else p - s))
                if pire is None or ec < pire:
                    pire = ec
    return pire


def _franchissement(chemin, nom, loc, coin, mname, a, b, amont, D, profs, vals,
                    exact=False):
    """La profondeur exacte ou la paire passe sous le plancher, par dichotomie.

    Rend un intervalle nomme plutot qu'un nombre nu quand le passage tombe hors
    des profondeurs candidates : « des 12 u » et « jamais » ne sont pas des
    chiffres, et les ecrire comme tels ferait lire une precision qui n'existe
    pas.

    `exact` fait porter la dichotomie sur `couloir_exact` au lieu de
    `approches.couloir_plein`. Les deux sont imprimees : la premiere est la
    borne basse que le garde-fou du projet emploie aujourd'hui, la seconde est
    ce que la geometrie fait vraiment.
    """
    mesure = couloir_exact if exact else A.couloir_plein
    ok = [v is not None and v >= A.JOUR_MIN for v in vals]
    if all(ok):
        return "jamais"
    if not any(ok):
        return f"des {profs[0]:.0f} u"
    dernier_ok = max(j for j, o in enumerate(ok) if o)
    if dernier_ok + 1 >= len(profs):
        return "jamais"
    lo, hi = profs[dernier_ok], profs[dernier_ok + 1]
    for _ in range(7):
        mi = (lo + hi) / 2.0
        tem = glyphsLib.GSFont(chemin)
        for master, lay in B.calques(tem, nom):
            B.appliquer_direct(lay, loc, T._sortante(mi, coin))
        st = D.Source(tem, mname)
        m = [x for x in tem.masters if x.name == mname][0]
        try:
            k = A.kern(amont, m.id, a, b)
            v = mesure(st, a, b, k)
        except Exception:
            v = None
        if v is not None and v >= A.JOUR_MIN:
            lo = mi
        else:
            hi = mi
    return f"{lo:.1f}-{hi:.1f} u"


def main(argv):
    quelles = [x for x in argv if x.isdigit()]
    cible = argv[argv.index("--cible") + 1] if "--cible" in argv else None
    temoin = "--temoin" in argv
    if not quelles:
        print(__doc__)
        return 2
    if cible is not None and cible not in CIBLES:
        print(f"cible inconnue : {cible}. Les deux sont {CIBLES}.")
        return 2
    srcs = B.sources()
    if srcs is None:
        print("La source amont n'est pas clonee : aucune passe ne peut mesurer.")
        print(f"  attendu : {AMONT}")
        print("  git clone --depth 1 "
              "https://github.com/googlefonts/atkinson-hyperlegible-next.git "
              "/tmp/ahn")
        print("\nVERDICT : NON FAIT. Ce n'est pas « aucune anomalie ».")
        return 1
    for n in quelles:
        if n == "1":
            passe1(srcs)
        elif n == "2":
            passe2(srcs, cible)
        elif n == "3":
            passe3(srcs)
        elif n == "4":
            passe4(srcs, cible, temoin)
        else:
            print(f"passe {n} inconnue")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
