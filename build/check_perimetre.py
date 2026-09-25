#!/usr/bin/env python3
"""Controle du perimetre de titrage : `lot4.HORS_TITRAGE` dit-il quelque chose.

Un ensemble d'exclusion est le genre de table qui pourrit sans bruit. Le
trente-troisieme tour l'a paye : `uni00A0` et `uni202F` vivaient dans la liste
des separateurs numeriques et n'avaient jamais rien designe, cette source
nommant ses espaces autrement. La liste paraissait couvrir deux caracteres et
n'en couvrait aucun, et rien ne le disait.

QUATORZE SECTIONS, sur les deux sources et les huit masters. Les six premieres
sont decrites ci-dessous ; les 7 et 8 sont nees au trente-sixieme tour (la
saturation de la sortante, et les onze derogations exigees comme etant
exactement les onze), les 9 et 10 au trente-septieme, la 11 et la 12 au
trente-neuvieme, la 13 au quarante-troisieme, la 14 au quarante-septieme :

  14  `lot4.FORMES_FERMEES`, la troisieme famille des chiffres et le O. Ces
      six glyphes n'ont aucune terminaison posee sur un alignement, donc
      aucune des treize autres sections ne les regarde : ils ne sont ni dans
      le perimetre ni dans `HORS_TITRAGE`. Trois sont pourtant tranches. La
      section remesure le FAIT sur lequel chaque decision a ete prise -- le
      nombre de contreformes -- et exige qu'aucun des six ne soit attrape par
      le geste, ce qui est la raison pour laquelle ils ne sont pas dans la
      liste d'exclusion.

  9   depuis que le GESTE et l'ETENDUE ont deux pentes distinctes -- voie B du
      point 66 -- un glyphe pourrait recevoir un geste sans etre dans l'etendue
      dont le perimetre est tire. La section l'interdit, en mesurant le
      DEPLACEMENT et non la designation : sept glyphes sont designes hors de
      l'etendue et aucun ne bouge.
  10  les quarante-quatre petites capitales du lot 3 sont ABSENTES de la source
      amont, que les neuf autres sections lisent : aucun controle de titrage ne
      les avait jamais regardees, alors que `mesure_titrage` les range dans le
      perimetre par heritage de leur capitale. Celle-ci lit la source du PROJET
      et compte, en constat, combien recoivent une sortante et sur combien le
      geste tombe sur l'ACCENT plutot que sur la lettre.

  1  chaque nom exclu existe dans la source. Un nom mort n'exclut rien.
  2  chaque nom exclu etait EFFECTIVEMENT attrape par le reglage general,
     DANS AU MOINS UNE des deux sources. Le critere est l'union et non chaque
     source prise a part : le perimetre est ecrit une fois pour les deux, et le
     point d'interrogation italique n'est pas attrape par la regle quand le
     romain l'est. Un premier jet testait source par source et rendait trois
     anomalies qui n'en etaient pas.
  3  aucun glyphe n'est a la fois prescrit et exclu. `PRESCRIPTIONS` dit
     comment un glyphe porte le geste, `HORS_TITRAGE` dit qu'il ne le porte
     pas : les deux ensemble sont une contradiction, pas une nuance.
  4  `appliquer_reglage` ne touche AUCUN glyphe exclu. Le test est un
     deplacement de noeud mesure, pas une lecture du code.
  5  les glyphes gardes bougent. Un perimetre qui ne laisserait passer que des
     gestes nuls serait un perimetre vide sans le dire. LA CAUSE ANNONCEE ICI
     ETAIT FAUSSE jusqu'au trente-cinquieme tour : elle attribuait les refus a
     `coupe_sortante` sur un flanc courbe, et la mesure dit que
     `coupe_sortante` n'intervient dans aucun d'eux. La section imprime
     maintenant les trois causes separement, parce qu'un seul libelle pour
     trois faits est le defaut le plus tenace de ce projet.
  6  le regime du HAUT est celui qui est ecrit. Tranche par Nicolas au
     trente-cinquieme tour : le titrage ne coupe qu'en bas, `DEFAUT` porte
     `rentrantes="aucune"`, et le r et le u sont les deux seules exceptions,
     decidees au neuvieme tour. Sans cette section, un regime du haut pourrait
     reapparaitre -- par une prescription nouvelle ou par un defaut change --
     sans que rien ne le dise. Elle compte comme anomalie tout glyphe qui
     recoit un geste en haut hors de la liste des exceptions.

Il ne sait pas echouer a moitie : chaque section compte ses anomalies et le
total est imprime en fin de parcours.
"""

import math
import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coupe as K
import lot2 as L
import lot4 as Q
import mesure_titrage as MT
import mesure_haut_titrage as MH
import mesure_point66 as P
import mesure_sortante_lot as MS

#: Les deux seules exceptions au regime du haut, decidees au neuvieme tour et
#: ecrites dans `lot4.PRESCRIPTIONS` au trente-cinquieme. La liste est ici pour
#: que la section 6 puisse EXIGER qu'elles soient les seules : lire la table
#: pour verifier la table ne verifie rien.
HAUT_ATTENDU = frozenset({"r", "u"})

#: LES SEPT GLYPHES QUI PORTENT UNE SORTANTE EN HAUT, section 13, quarante-
#: troisieme tour. A ne pas confondre avec `HAUT_ATTENDU` ci-dessus, qui porte
#: les deux RENTRANTES du haut : une rentrante coupe vers l'interieur du
#: glyphe, une sortante le fait depasser son alignement.
#:
#: Mesure sur l'amont romain a l'etat ecrit, avant le tour : NEUF glyphes en
#: portaient une, `H I K N U V W v w`. Les deux minuscules la perdent au point
#: 75, et le K garde la sienne en perdant son bas au point 77. LE I LA PERD
#: AUSSI, rendu a Atkinson en fin de tour : il en reste SIX.
HAUT_SORTANTE_ATTENDUE = frozenset({"H", "K", "N", "U", "V", "W"})

#: LES DEUX DONT LA SORTANTE DU HAUT EST ECARTEE, point 75. Le v et le w
#: sortaient de 32 unites au-dessus de la hauteur d'x depuis le neuvieme tour ;
#: Nicolas les a remis a plat a 496,0 au quarante-deuxieme, en navigateur.
#:
#: CETTE LISTE EXISTE PARCE QU'AUCUNE AUTRE NE POUVAIT LES ACCUEILLIR, et c'est
#: la raison d'etre de la section 13. `BRUT_ATTENDU` et la section 8 mesurent
#: la sortante du BAS ; le bas du v et du w est exclu par leur prescription,
#: donc la section 8 les range dans `jamais` -- ce qui est vrai et muet. Sans
#: la section 13, le geste le plus visible de ces deux lettres n'aurait AUCUN
#: garde-fou, et le projet gagne ici son premier controle sur la sortante du
#: haut.
#:
#: LE I LES REJOINT en fin de tour, et il est le seul des trois a figurer AUSSI
#: dans `BRUT_ATTENDU` : `sortantes=()` retire ses deux barres d'un coup, donc
#: la section 8 le voit par le bas et la section 13 par le haut. Le v et le w,
#: eux, gardent `exclure` et n'ont jamais rien eu en bas.
HAUT_SORTANTE_ECARTEE = frozenset({"I", "v", "w"})

#: Les DOUZE glyphes dont la sortante du bas est ECARTEE par derogation. Onze
#: tranches par Nicolas au trente-sixieme tour sur
#: `planche-propagation-2-longs.png` et `-3-courts.png` : six ont une barre plus
#: longue que tout ce qui a ete valide, cinq sont dans la fourchette et ecartes
#: sur la forme.
#:
#: L'AE EST LE DOUZIEME, tranche au trente-neuvieme tour sur
#: `planche-ensemble-titrage.png`. Il figurait auparavant dans cette note comme
#: GARDE, avec le plusminus, au motif que sa barre est aussi longue que celle
#: des six premiers. Nicolas a tranche l'inverse sur un fait qui n'etait pas
#: dans la longueur : l'AE dessine le A, dont le `bg` est exclu depuis son
#: arbitrage, et une prescription indexee par nom ne suit pas une composition.
#: Le plusminus, lui, est bien GARDE : il a ete revalide au meme tour.
#:
#: LE I EST LE TREIZIEME, tranche au quarante-et-unieme tour EN NAVIGATEUR, sur
#: le dessin fusionne servi. Il est le premier de cette liste a y entrer depuis
#: `VALIDES_REGLAGE_GENERAL`, d'ou il sort au meme tour : il avait ete valide au
#: reglage general au trente-neuvieme sur planche d'alphabet, et c'est un texte
#: courant a 18 px qui a montre que son fut glisse. Les deux tables bougent
#: ensemble, sinon l'une dit valide ce que l'autre dit ecarte.
#:
#: LE K EST LE QUATORZIEME, tranche au quarante-deuxieme tour EN NAVIGATEUR,
#: avec le K capitale et pour la meme cause que le i : une forme arbitree quand
#: le titrage etait un registre separe, versee dans le texte par la fusion. Il
#: est le SECOND a entrer ici depuis `VALIDES_REGLAGE_GENERAL`, d'ou il sort au
#: meme tour, et donc la seconde validation de planche revisee en texte
#: courant. LES DEUX TABLES BOUGENT DANS LE MEME GESTE, sans quoi l'une dit
#: valide ce que l'autre dit ecarte et aucun controle n'echoue.
#:
#: Ce qu'il portait, mesure au Regular servi : DEUX pieds qui plongent, (72,-32)
#: et (402,-32). Avec le h, c'etaient les deux seules lettres du bas de casse
#: dans ce cas -- toutes les autres plongent par un seul pied. Le h, lui, n'est
#: pas dans cette liste : il garde une sortante, sur son pied DROIT seulement.
#:
#: LE V ET LE W N'Y SONT PAS, bien que leur sortante soit retiree au meme tour :
#: la leur est en HAUT, quand cette liste et la section 8 ne mesurent que le
#: BAS. C'est la SECTION 13 qui les porte.
#:
#: La liste vit ICI, comme HAUT_ATTENDU, et pour la meme raison : la section 8
#: doit pouvoir EXIGER que ces quatorze soient exactement les quatorze. Elle ne
#: lit pas `lot4.PRESCRIPTIONS` -- elle MESURE, en rejouant chaque glyphe avec
#: le regime du bas force au defaut, ce qui separe un glyphe dont la sortante
#: est ecartee d'un glyphe qui n'en a jamais eu.
#: LE I CAPITALE EST LE QUINZIEME, tranche au quarante-troisieme tour en
#: navigateur, sur la section 7 servie. Il portait `sortantes={"bc","hc"}`
#: depuis le huitieme tour et c'etait le seul glyphe dont les DEUX BARRES
#: penchaient -- le I n'a pas de bout de fut, donc une sortante y incline une
#: barre entiere. Il redevient celui d'Atkinson, et `i.sc`, qui suit sa
#: capitale depuis la fusion, redevient plat avec lui.
#:
#: SON HAUT EST ECARTE AU MEME GESTE, et c'est le seul de cette liste dans ce
#: cas : `sortantes=()` retire la barre haute comme la basse, donc le I quitte
#: `HAUT_SORTANTE_ATTENDUE` pour `HAUT_SORTANTE_ECARTEE`. TROIS TABLES BOUGENT
#: ENSEMBLE ici, la ou le k n'en demandait que deux.
#: LE R ENTRE AU QUARANTE-NEUVIEME TOUR, seizieme derogation, sur decision de
#: Nicolas en NAVIGATEUR. Il etait au reglage general et dans
#: `VALIDES_REGLAGE_GENERAL` depuis le trente-neuvieme tour : c'est la
#: CINQUIEME validation de planche revisee en texte, apres le i, le k, le 1 et
#: `idotless`, et les deux tables bougent dans le meme geste.
#: LE `plus` ENTRE AU CINQUANTE-TROISIEME TOUR, dix-septieme derogation, sur
#: decision de Nicolas EN TEXTE, sur la section 8 de `tour51.html`. Il etait au
#: reglage general et dans `VALIDES_REGLAGE_GENERAL` depuis le trente-neuvieme
#: tour : c'est la SIXIEME validation de planche revisee en texte, apres le i,
#: le k, le 1, `idotless` et le R, et les deux tables bougent dans le meme
#: geste. Ce que le reglage lui avait donne et qu'il rend : 32 unites de
#: plongee sous la ligne de base, par la cible deduite de la CASSE DE SON NOM,
#: quand `plus` est un signe et non un bas de casse. Sa barre, elle, n'avait
#: jamais bouge -- c'est `operateurs.py` qui la monte, de 64, au meme tour.
#:
#: LE `plusminus` ET LE `numbersign` RESTENT DANS `VALIDES_REGLAGE_GENERAL`,
#: bien qu'ils portent la meme plongee et de la meme cause : Nicolas les a relus
#: dans la meme phrase au meme tour et gardes. Une cause commune ne fait pas une
#: decision commune, et c'est pour cela que la liste porte des NOMS et non une
#: regle.
BRUT_ATTENDU = frozenset({"Z", "E", "OE", "L", "z", "B",
                          "D", "Eth", "Thorn", "l", "t", "AE", "idotless",
                          "k", "I", "R", "plus"})

#: Les defauts connus et non corriges que la section 8 imprime au lieu de les
#: compter. ELLE EXIGE AUSSI QU'ILS SOIENT ENCORE LA : un defaut qui disparait
#: sans que la liste suive est un controle qui ment dans l'autre sens.
#:
#: VIDE DEPUIS LE TRENTE-SEPTIEME TOUR. Le Y italique y figurait : sa sortante
#: etait ecartee sans qu'aucune derogation le demande, `lot4.quadrant` classant
#: son pied `bc` au romain et `bg` en italique. C'etait le POINT OUVERT 65, et
#: il est ferme -- `quadrant` desincline le contour par l'angle du master avant
#: de classer, donc les deux sources classent la meme forme. Le Y retrouve sa
#: sortante dans ses quatre masters italiques, et les deux sources tombent a
#: 232 gestes.
BRUT_CONNUS = {"romain": frozenset(), "italique": frozenset()}

SOURCES = (
    ("romain", "/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs"),
    ("italique", "/tmp/ahn/sources/AtkinsonHyperlegibleNext-Italic.glyphs"),
)


def noeuds(lay):
    return [(float(n.position.x), float(n.position.y))
            for p in L.paths(lay) for n in p.nodes]


def deplacement_max(font, mid, nom):
    """Le plus grand deplacement de noeud sur tous les masters, en unites."""
    g = font.glyphs[nom]
    if g is None:
        return None
    pire = 0.0
    for m in mid.values():
        lay = next((l for l in g.layers if l.layerId == m.id), None)
        if lay is None or not L.paths(lay):
            continue
        snap = [K.to_segs(p) for p in L.paths(lay)]
        av = noeuds(lay)
        try:
            MT.appliquer_reglage(lay, nom, m)
            ap = noeuds(lay)
            if len(av) == len(ap):
                pire = max([pire] + [math.hypot(q[0] - p[0], q[1] - p[1])
                                     for p, q in zip(av, ap)])
            else:
                pire = float("inf")
        except Exception:
            pass
        lay.shapes = [K.from_segs(s) for s in snap] + [
            sh for sh in lay.shapes if not hasattr(sh, "nodes")]
    return pire


def bilan_gestes(font, mid, nom, bas=None):
    """Ce que le reglage ecrit fait sur un glyphe : la sortante, le haut, les
    notes de refus. Passe par `mesure_haut_titrage.partage`, et non par une
    seconde lecture du journal : deux codes qui lisent la meme sortie doivent
    lire la meme fonction, sinon ils finissent par en tirer deux verdicts."""
    g = font.glyphs[nom]
    if g is None:
        return None
    sortie = descente = None
    notes, notes_bas = set(), set()
    vus = vides = 0
    for m in mid.values():
        lay = next((l for l in g.layers if l.layerId == m.id), None)
        if lay is None or not L.paths(lay):
            continue
        snap = [K.to_segs(p) for p in L.paths(lay)]
        jour = []
        try:
            MT.appliquer_reglage(lay, nom, m, journal=jour, bas=bas)
        except Exception as e:
            jour.append((nom, -1, f"echec {e}", 0.0, 0))
        # `partage` rend depuis le trente-sixieme tour un CINQUIEME champ, les
        # notes du BAS, separees de celles du haut : `couper_alignements`
        # journalise maintenant la saturation de la sortante, et versee dans le
        # meme sac elle sortait imprimee "haut refuse", ce qui attribue au haut
        # ce que le bas a fait.
        s, de, _th, nt, nb = MH.partage(jour)
        vus += 1
        if not jour:
            vides += 1
        if s is not None:
            sortie = s if sortie is None else max(sortie, s)
        if de is not None:
            descente = de if descente is None else max(descente, de)
        notes |= nt
        notes_bas |= {f"{m.name} : {n}" for n in nb}
        lay.shapes = [K.from_segs(x) for x in snap] + [
            sh for sh in lay.shapes if not hasattr(sh, "nodes")]
    return dict(sortie=sortie, descente=descente, notes=notes,
                notes_bas=notes_bas, vus=vus, vides=vides)


def haut_du_geste(font, mid, nom, marge=1.05):
    """Le geste tombe-t-il AU-DESSUS de la hauteur d'x du glyphe ?

    Mesure le milieu du segment que la sortante fait tourner, avant rotation,
    et le compare a la hauteur d'x du master. Sur une petite capitale
    accentuee, un geste au-dessus est pose sur l'accent et non sur la lettre.
    Le segment se retrouve par son INDICE, que le journal porte : un
    appariement positionnel attribuerait le mauvais.
    """
    g = font.glyphs[nom]
    if g is None:
        return False
    for m in mid.values():
        lay = next((l for l in g.layers if l.layerId == m.id), None)
        if lay is None or not L.paths(lay):
            continue
        snap = [K.to_segs(p) for p in L.paths(lay)]
        jour = []
        try:
            MT.appliquer_reglage(lay, nom, m, journal=jour)
        except Exception:                                     # noqa: BLE001
            pass
        apres = [K.to_segs(p) for p in L.paths(lay)]
        lay.shapes = [K.from_segs(s) for s in snap] + [
            sh for sh in lay.shapes if not hasattr(sh, "nodes")]
        # L'INDICE DU JOURNAL EST LOCAL A SON CONTOUR, et le journal ne dit pas
        # lequel : l'aplatir en une seule liste attribuerait le mauvais segment
        # des qu'un glyphe a deux contours, et une petite capitale accentuee en
        # a trois. Le segment se retrouve donc par comparaison avant/apres,
        # contour par contour, comme `mesure_sortante_lot.gestes` le fait -- et
        # c'est le segment TOURNE qui compte, le voisin etant seulement
        # prolonge.
        for av, ap in zip(snap, apres):
            if len(av) != len(ap):
                continue
            for a, b in zip(av, ap):
                if a["p0"] == b["p0"] and a["p3"] == b["p3"]:
                    continue
                da = math.degrees(math.atan2(a["p3"][1] - a["p0"][1],
                                             a["p3"][0] - a["p0"][0]))
                db = math.degrees(math.atan2(b["p3"][1] - b["p0"][1],
                                             b["p3"][0] - b["p0"][0]))
                dt = abs(da - db) % 360.0
                if min(dt, 360.0 - dt) <= 0.02:
                    continue
                y = (a["p0"][1] + a["p3"][1]) / 2.0
                if y > m.xHeight * marge:
                    return True
    return False


def attrapes_par_le_geste(font, mid):
    """Les glyphes dont `couper_alignements` designerait un segment.

    CE N'EST PAS L'ETENDUE, et les deux ne se confondent plus depuis le
    trente-septieme tour : l'etendue se mesure a `lot4.PENTE_ETENDUE`, 0,3, et
    definit le perimetre ; le geste se mesure a `lot4.PENTE_BAS`, 0,80, parce
    qu'il travaille sur un dessin dont le lot 2 a deja tourne des bouts. Un nom
    exclu doit etre juge sur ce que le GESTE lui ferait, sinon les trois noms
    que la pente elargie fait entrer sortent comptes comme exclusions inutiles.
    """
    out = set()
    for g in font.glyphs:
        for l in g.layers:
            m = mid.get(l.layerId)
            if m is None or not L.paths(l):
                continue
            metr = {"base": 0.0, "xh": m.xHeight, "cap": m.capHeight}
            if MT.terminaisons(l, metr, pente=Q.PENTE_BAS):
                out.add(g.name)
                break
    return out


QUADRANTS_HAUT = frozenset({"hg", "hc", "hd"})


def sortantes_par_quadrant(font, mid, nom, bas=None):
    """Les sortantes REELLEMENT posees, rangees par quadrant : {quadrant: sortie}.

    `bilan_gestes` rend la plus grande sortie d'un glyphe, tous quadrants
    confondus : il ne peut donc pas repondre "ce glyphe sort-il en HAUT ?".
    D'ou cette fonction, qui reprend le critere des sections 11 et 12 -- le
    quadrant est MESURE sur le contour redresse par l'angle du master, jamais
    deduit du nom, et le geste est APPARIE AU JOURNAL DU PRODUCTEUR. Sans cet
    appariement un flanc seulement PROLONGE ressort comme un geste : sur le
    plusminus ExtraLight Italic il tourne de 0,1 degre et se donnait pour une
    sortante `hg` de 54 unites, en haut, sur un glyphe dont le regime du haut
    est "aucune".

    `bas` force le regime des terminaisons du bas, comme dans la section 8.
    Lui passer les quadrants du HAUT fait poser la sortante sur le haut : c'est
    ce qui separe un glyphe dont la sortante du haut est ECARTEE d'un glyphe
    dont la geometrie n'en designerait aucune.
    """
    out = {}
    g = font.glyphs[nom]
    if g is None:
        return out
    for m in font.masters:
        lay = next((l for l in g.layers if l.layerId == m.id), None)
        if lay is None:
            continue
        avant = [K.to_segs(p) for p in L.paths(lay)]
        if not any(avant):
            continue
        jour = []
        try:
            MT.appliquer_reglage(lay, nom, mid[m.id], journal=jour, bas=bas)
        except Exception:                                     # noqa: BLE001
            pass
        apres = [K.to_segs(p) for p in L.paths(lay)]
        bb = Q.boite(avant)
        ita = float(getattr(m, "italicAngle", 0) or 0.0)
        for gg in MS.gestes(avant, apres, jour):
            if ("err" in gg or gg["depl"] <= 0.01
                    or gg.get("theta") is None or gg.get("sortie") is None):
                continue
            qd = Q.quadrant(avant[gg["contour"]], gg["i"], bb, ita)
            out[qd] = max(out.get(qd, 0.0), gg["sortie"])
        lay.shapes = [K.from_segs(x) for x in avant] + [
            sh for sh in lay.shapes if not hasattr(sh, "nodes")]
    return out


def contours_par_master(font, nom):
    """Le nombre de contours de `nom` dans chaque master, ou None.

    Sert au volet D de la section 14 : un glyphe dont la fiche annonce l'etat
    "servi" doit porter un contour de PLUS que son amont. Le compte de
    contreformes ne suffirait pas -- le bras du O est un contour positif pose
    dans le creux, donc il ne change pas le nombre de contreformes, et c'est
    precisement pour cela que la section 14 n'a pas bouge d'une ligne quand le
    bras est entre dans la chaine.
    """
    g = font.glyphs[nom]
    if g is None:
        return None
    out = []
    for m in font.masters:
        lay = next((l for l in g.layers if l.layerId == m.id), None)
        if lay is None:
            return None
        out.append(len(L.paths(lay)))
    return out


def creux_par_master(font, nom):
    """Le nombre de contreformes de `nom` dans chaque master, ou None.

    Une contreforme se reconnait au SIGNE de son aire, oppose a celui du
    contour le plus grand -- et non a sa taille : le zero barre a deux
    demi-contreformes d'aires voisines, et le double accent aigu a deja paye
    le depart par l'aire au dix-huitieme tour.
    """
    g = font.glyphs[nom]
    if g is None:
        return None
    out = []
    for m in font.masters:
        lay = next((l for l in g.layers if l.layerId == m.id), None)
        if lay is None:
            return None
        aires = [K.area(K.to_segs(p)) for p in L.paths(lay)]
        if not aires:
            return None
        ext = max(aires, key=abs)
        signe = 1 if ext > 0 else -1
        out.append(sum(1 for a in aires if a is not ext and a * signe < 0))
    return out


def section14(table=None):
    """14. LA TROISIEME FAMILLE : LE FAIT SOUS CHAQUE DECISION EST-IL ENCORE VRAI.

    Section neuve au quarante-septieme tour, point ouvert 83. Le 3, le 5 et le
    zero ont ete tranches par Nicolas au quarante-sixieme ; le 6, le 8 et le O
    restent a dessiner. Aucune table ne les portait, et les treize autres
    sections sont aveugles a eux par construction : elles partent de
    `loc_alignement`, qui ne designe rien sur une forme fermee.

    TROIS VOLETS.

    A. Le fait mesure. `FORMES_FERMEES[nom]["creux"]` doit valoir le nombre de
       contreformes reellement compte, dans les HUIT masters des deux sources
       -- verifie identique partout au quarante-septieme tour. Une raison
       ecrite sans son fait vieillit sans que rien ne le dise : le jour ou le
       3 gagnerait une contreforme, "aucun anneau" cesserait d'etre vrai et
       cette ligne le dirait.

    B. La coherence entre l'etat et le fait. Un "chantier" sans contreforme
       n'a rien ou ancrer un bras ; un "ecarte" pour absence d'anneau qui en
       gagnerait une redeviendrait une question ouverte.

    C. Chaque nom est du bon cote de `HORS_TITRAGE`, et le critere est
       MESURE : un nom y a sa place si et seulement si un GESTE l'attrape
       dans au moins une des deux sources, ce qui est le critere des sections
       1 et 2. LES SIX NE FONT PAS BLOC, et un premier jet de cette section
       l'annoncait -- le controle a corrige son auteur : le 3 et le 5 SONT
       attrapes, par un bout du haut que le regime `aucune` epargne, donc ils
       sont legitimement dans `HORS_TITRAGE` depuis le trente-quatrieme tour ;
       le zero, le 6, le 8 et le O ne le sont dans aucune source, donc les y
       ecrire remplirait la section 2 -- qui signale un nom inutile sans
       incrementer le total, donc en silence.

    ELLE LIT L'AMONT pour les six, et le PROJET pour `zero.slashless`, qui n'y
    existe pas : c'est le glyphe que le lot 1 recoud et que les nombres
    servent, et il a UNE contreforme entiere. Le fait est imprime en constat,
    parce qu'il borne la portee de la decision sur le zero -- elle est un
    arbitrage de signe, pas une impossibilite geometrique.

    LE TEMOIN. `--temoin` rejoue le volet A avec un `creux` fausse d'une
    unite sur le 6 : la section doit alors signaler. Sans lui, un zero ne se
    distingue pas d'une mesure morte.
    """
    table = table if table is not None else Q.FORMES_FERMEES
    print("\n14. la troisieme famille, formes fermees, point 83")
    anomalies = 0
    attrapes_partout = {}
    for lab, amont, projet, _bin in MT.SOURCES:
        if not os.path.exists(amont):
            print(f"  {lab} : source amont absente. "
                  f"Ce n'est pas un zero, c'est un NON MESURE.")
            anomalies += 1
            continue
        font = glyphsLib.GSFont(amont)
        mid = {m.id: m for m in font.masters}
        geste = attrapes_par_le_geste(font, mid)
        ecarts = []
        for nom, fiche in sorted(table.items()):
            cs = creux_par_master(font, nom)
            if cs is None:
                ecarts.append(f"{nom} ABSENT de la source")
                continue
            if len(set(cs)) != 1 or cs[0] != fiche["creux"]:
                ecarts.append(f"{nom} creux {cs} pour {fiche['creux']} annonce(s)")
            if fiche["etat"] == "chantier" and cs[0] < 1:
                ecarts.append(f"{nom} en chantier sans contreforme")
            if fiche["etat"] == "ecarte" and fiche["creux"] == 0 and cs[0] > 0:
                ecarts.append(f"{nom} ecarte faute d'anneau, mais il en a un")
            if fiche["etat"] not in Q.ETATS_FORMES_FERMEES:
                ecarts.append(f"{nom} porte l'etat inconnu {fiche['etat']!r} : "
                              f"aucun volet ne le controle, et une faute de "
                              f"frappe passerait pour une decision")
            # D. UN NOM "SERVI" PORTE VRAIMENT SON CONTOUR GREFFE. Le fait se
            # lit dans la source du PROJET et se compare a l'amont : un
            # contour de plus, exactement. La FORME du greffon, elle, se
            # verifie noeud a noeud par `check_O` section 5 -- ici c'est
            # sa PRESENCE, et elle ne se deduit d'aucune des treize autres
            # sections. Sans ce volet, retirer l'appel de `make_temoin`
            # laisserait la table annoncer "servi" sans que rien ne crie.
            if fiche["etat"] == "servi":
                fp2 = P.charger(projet)
                if fp2 is None:
                    ecarts.append(f"{nom} annonce servi, source du projet "
                                  f"absente : NON MESURE")
                else:
                    ca = contours_par_master(font, nom)
                    cp = contours_par_master(fp2, nom)
                    # Le romain greffe, l'italique non : la comparaison se
                    # fait source par source, et `MASTERS_SANS_BRAS` dit
                    # laquelle attend quoi.
                    ital = all(m.name in Q.MASTERS_SANS_BRAS
                               for m in fp2.masters)
                    attendu = 0 if ital else 1
                    gains = sorted({b - a for a, b in zip(ca, cp)})
                    if gains != [attendu]:
                        ecarts.append(
                            f"{nom} annonce servi : {ca} contour(s) a "
                            f"l'amont, {cp} au projet, gain {gains} pour "
                            f"{[attendu]} attendu")
            attrapes_partout.setdefault(nom, []).append(nom in geste)
        print(f"  {lab} : {len(table)} noms, "
              f"{len(ecarts)} ecart(s) au fait annonce")
        for e in ecarts:
            print(f"     !! {e}")
        anomalies += len(ecarts)
        # Le glyphe du lot 1, qui n'existe qu'a l'etat servi.
        fp = P.charger(projet)
        if fp is None:
            print(f"     zero.slashless : source du projet absente, NON MESURE.")
        else:
            cs = creux_par_master(fp, "zero.slashless")
            print(f"     zero.slashless (projet) : creux {cs} — le zero recousu "
                  f"a un anneau libre, la decision est un arbitrage de signe")
    pris = sorted(n for n, v in attrapes_partout.items() if any(v))
    faux = sorted(n for n in attrapes_partout
                  if (n in pris) != (n in Q.HORS_TITRAGE))
    print(f"  attrapes par le geste, donc a leur place dans HORS_TITRAGE : "
          f"{' '.join(pris) or 'aucun'}")
    print(f"  jamais attrapes, donc a tenir DEHORS : "
          f"{' '.join(n for n in sorted(attrapes_partout) if n not in pris)}")
    if faux:
        print(f"     !! du mauvais cote de HORS_TITRAGE : {' '.join(faux)}")
    anomalies += len(faux)
    return anomalies


def section13():
    """13. LA SORTANTE DU HAUT : QUI EN PORTE UNE, ET QUI EN A PERDU UNE.

    Section neuve au quarante-troisieme tour, point ouvert 75. Le projet n'avait
    AUCUN controle sur la sortante du haut : douze sections, et les deux seules
    qui parlent du haut -- la 6 et la 8 -- parlent de la RENTRANTE ou du BAS.
    Le v et le w montaient de 32 unites au-dessus de la hauteur d'x depuis le
    neuvieme tour sans qu'aucune liste ne les nomme.

    DEUX VOLETS, PARCE QU'UN SEUL LAISSERAIT UN TROU DE CHAQUE COTE.

    A. Qui en porte une, sur TOUT le perimetre. La liste mesuree doit valoir
       exactement `HAUT_SORTANTE_ATTENDUE`. Un ENTRANT est un glyphe qui gagne
       une sortante du haut sans que personne l'ait vue -- c'est exactement ce
       qui est arrive au v et au w, arbitres quand le titrage etait un registre
       separe puis verses dans le texte par la fusion. Un SORTANT est un geste
       arbitre qui disparait sans decision.

    B. Qui en a perdu une. Pour chacun des deux de `HAUT_SORTANTE_ECARTEE`,
       le haut est rejoue FORCE : le glyphe doit n'en porter aucune a l'etat
       ecrit et en recevoir une quand on la force. C'est la distinction que la
       section 8 fait pour le bas entre `ecartes` et `jamais`, et sans elle une
       derogation ne se distinguerait pas d'un glyphe que la geometrie ne
       designe pas.

    CE QUE LE VOLET B NE PEUT PAS FAIRE, ET C'EST MESURE : demander que le v et
    le w soient les deux SEULS ecartes du perimetre entier n'a aucun sens. Le
    haut force pose une sortante sur 64 glyphes des 103 du perimetre romain --
    la plupart des lettres ont une terminaison plate en haut. L'univers du
    volet B est donc la FAMILLE ARBITREE en haut, les neuf noms des deux listes
    de ce fichier, et c'est le volet A qui interdit que la famille s'agrandisse
    en silence. Les deux volets ne se recouvrent pas : A garde la porte
    d'entree, B prouve que la sortie est une decision et non une absence.

    ELLE LIT L'AMONT, comme les sections 1 a 9 : la sortante du haut est un
    geste du lot 4, et le rejouer sur `Temoin.glyphs`, ou la fusion l'a deja
    ecrit, l'appliquerait deux fois.
    """
    print("\n13. la sortante du HAUT, point ouvert 75")
    anomalies = 0
    for lab, chemin in SOURCES:
        if not os.path.exists(chemin):
            print(f"  {lab} : source absente, {chemin}. "
                  f"Ce n'est pas un zero, c'est un NON MESURE.")
            anomalies += 1
            continue
        font = glyphsLib.GSFont(chemin)
        mid = {m.id: m for m in font.masters}
        gardes = sorted(n for n in (attrapes_par_le_geste(font, mid)
                                    | set(Q.PRESCRIPTIONS))
                        if Q.dans_le_titrage(n) and font.glyphs[n] is not None)

        # A. qui porte une sortante en haut, a l'etat ECRIT
        porteurs = {}
        for nom in gardes:
            q = sortantes_par_quadrant(font, mid, nom)
            haut = {k: v for k, v in q.items() if k in QUADRANTS_HAUT}
            if haut:
                porteurs[nom] = haut
        entrants = sorted(set(porteurs) - HAUT_SORTANTE_ATTENDUE)
        sortants = sorted(HAUT_SORTANTE_ATTENDUE - set(porteurs))
        detail = "  ".join(
            f"{n} " + "/".join(f"{k}={v:.0f}" for k, v in sorted(porteurs[n].items()))
            for n in sorted(porteurs))
        print(f"  {lab} A : {len(porteurs)}/{len(HAUT_SORTANTE_ATTENDUE)} "
              f"glyphe(s) du perimetre portent une sortante en HAUT, "
              f"sur {len(gardes)} gardes")
        print(f"      {detail or 'aucun'}")
        if entrants:
            print(f"      !! ENTRANTS, sortante du haut que personne n'a "
                  f"arbitree : {' '.join(entrants)}")
        if sortants:
            print(f"      !! SORTANTS, sortante du haut disparue sans "
                  f"decision : {' '.join(sortants)}")
        anomalies += len(entrants) + len(sortants)

        # B. les deux ecartes : rien a l'etat ecrit, une sortante quand on force
        ecartes, jamais, fautifs = [], [], []
        for nom in sorted(HAUT_SORTANTE_ECARTEE):
            if font.glyphs[nom] is None:
                fautifs.append(f"{nom} absent de la source")
                continue
            if nom in porteurs:
                fautifs.append(f"{nom} PORTE encore une sortante en haut "
                               + "/".join(f"{k}={v:.0f}"
                                          for k, v in sorted(porteurs[nom].items())))
                continue
            forcee = sortantes_par_quadrant(font, mid, nom, bas=QUADRANTS_HAUT)
            h = {k: v for k, v in forcee.items() if k in QUADRANTS_HAUT}
            if h:
                vals = "/".join(f"{k}={v:.0f}" for k, v in sorted(h.items()))
                ecartes.append(f"{nom} ({vals} si forcee)")
            else:
                jamais.append(nom)
        print(f"  {lab} B : sortante du haut ECARTEE par derogation : "
              f"{len(ecartes)}/{len(HAUT_SORTANTE_ECARTEE)}   "
              f"{'  '.join(ecartes) or 'aucune'}")
        if jamais:
            print(f"      !! attendus ECARTES mais la geometrie n'y designe "
                  f"aucune sortante du haut : {' '.join(jamais)} — la "
                  f"derogation ne derogerait a rien")
        for f in fautifs:
            print(f"      !! {f}")
        anomalies += len(jamais) + len(fautifs)

        # LE TEMOIN. Un zero ne se distingue pas d'une grandeur morte : la
        # sortante du haut est REMISE au v en memoire, dans l'etat exact qui
        # etait le sien avant ce tour, et le volet A doit la voir. Il agit sur
        # ce que la section MESURE et dans le sens ou elle cherche le defaut --
        # un entrant -- ce que le temoin general de `check_approches` avait
        # appris a ses depens.
        vu = None
        if "v" in Q.PRESCRIPTIONS:
            sauv = Q.PRESCRIPTIONS["v"]
            Q.PRESCRIPTIONS["v"] = dict(sauv, sortantes={"hg", "hd"})
            try:
                q = sortantes_par_quadrant(font, mid, "v")
                vu = bool(QUADRANTS_HAUT & set(q))
            finally:
                Q.PRESCRIPTIONS["v"] = sauv
        print(f"      TEMOIN : v rendu a sortantes={{hg,hd}} "
              + ("RETROUVE sa sortante du haut, la section sait signaler"
                 if vu else
                 "NE BOUGE PAS — la section ne discrimine plus"))
        if vu is not True:
            anomalies += 1
    return anomalies


#: Ce que `main` rend quand il n'a PAS mesure, par opposition a un total nul.
#: Une relecture deleguee du cinquante-neuvieme tour l'a trouve : `main`
#: rendait `None` sur source absente, et `1 if main() else 0` traduisait ce
#: non-mesure en SUCCES, comme un total de zero. Un controle qui n'a pas lu sa
#: source ne dit pas la meme chose qu'un controle qui n'a rien trouve, et le
#: code de retour est le seul endroit ou un enchainement de commandes lit la
#: difference. Le 2 est celui des refus cables au cinquante-huitieme tour.
NON_MESURE = -1


def main():
    total = 0
    attrapes_union = set()
    geste_union = set()
    presents_union = set()
    hors_etendue = {}
    for lab, chemin in SOURCES:
        if not os.path.exists(chemin):
            print(f"!! source absente : {chemin}")
            print("   Ne rien conclure d'un controle qui n'a pas lu sa source.")
            return NON_MESURE
        font = glyphsLib.GSFont(chemin)
        mid = {m.id: m for m in font.masters}
        res = MT.analyser(lab, chemin, MT.SOURCES[0 if lab == "romain" else 1][3],
                          verbeux=False)
        attrapes = set(res["touche"])
        print(f"\n=== {lab} : {len(Q.HORS_TITRAGE)} noms exclus, "
              f"{len(attrapes)} glyphes attrapes par le reglage")

        geste = attrapes_par_le_geste(font, mid)
        attrapes_union |= attrapes
        geste_union |= geste
        presents_union |= {n for n in Q.HORS_TITRAGE
                           if font.glyphs[n] is not None}
        # 9. Ce que le GESTE attrape hors de l'ETENDUE, et que rien n'exclut.
        # La voie B du point 66 separe les deux pentes, donc un glyphe peut
        # recevoir un geste sans etre dans l'etendue dont le perimetre est
        # tire. Trois l'ont fait au trente-septieme tour et sont ecrits dans
        # HORS_TITRAGE ; cette section exige qu'il n'y en ait pas d'autre.
        # DESIGNE N'EST PAS COUPE, et confondre les deux serait la neuvieme
        # fois qu'un libelle de ce projet couvre deux causes. `loc_alignement`
        # designe un segment ; `appliquer_reglage` ne le coupe que si son
        # quadrant est du bas et si la sortante aboutit. Le critere est donc le
        # DEPLACEMENT REEL, mesure sur les quatre masters, et non la
        # designation : sept glyphes sont designes hors de l'etendue et aucun
        # ne bouge.
        servi = set(res["servi"])
        hors_etendue[lab] = sorted(
            n for n in geste - attrapes
            if Q.dans_le_titrage(n) and n in servi
            and (deplacement_max(font, mid, n) or 0.0) > 0.05)

        # 1. et 2. sont juges sur l'union, et imprimes en fin de parcours.
        absents = sorted(n for n in Q.HORS_TITRAGE if font.glyphs[n] is None)
        muets = sorted(n for n in Q.HORS_TITRAGE
                       if font.glyphs[n] is not None and n not in geste)
        print(f"  1./2. dans cette source : {len(absents)} absent(s), "
              f"{len(muets)} non attrape(s)"
              + (f" — {' '.join(muets)}" if muets else ""))

        # 3. contradiction avec PRESCRIPTIONS
        double = sorted(Q.HORS_TITRAGE & set(Q.PRESCRIPTIONS))
        print(f"  3. a la fois prescrits et exclus : "
              f"{' '.join(double) or 'aucun'}")
        total += len(double)

        # 4. aucun geste sur un exclu
        touches = []
        for nom in sorted(Q.HORS_TITRAGE):
            if font.glyphs[nom] is None:
                continue
            d = deplacement_max(font, mid, nom)
            if d and d > 0.001:
                touches.append(f"{nom} {d:.1f}u")
        print(f"  4. exclus que appliquer_reglage deplace quand meme : "
              f"{' '.join(touches) or 'aucun'}")
        total += len(touches)

        # 5. les gardes bougent
        gardes = sorted(attrapes - Q.HORS_TITRAGE)
        nuls = []
        for nom in gardes:
            d = deplacement_max(font, mid, nom)
            if d is not None and d < 0.001:
                nuls.append(nom)
        print(f"  5. gardes dans le titrage que le geste ne deplace pas : "
              f"{len(nuls)}")
        # Trois causes, imprimees separement. Le libelle unique d'avant
        # attribuait tout a coupe_sortante sur un flanc courbe : mesure au
        # trente-cinquieme tour, coupe_sortante n'intervient dans aucun cas.
        # QUATRE CAUSES ET NON TROIS depuis le trente-sixieme tour. Le libelle
        # "haut seul, non traite par le regime" couvrait aussi les onze glyphes
        # dont c'est la SORTANTE DU BAS qui est ecartee par derogation : il
        # disait du bas ce qui n'est vrai que du haut, et c'est la famille de
        # defaut la plus tenace du projet. La cause se mesure, elle ne se lit pas
        # dans la table : on rejoue le glyphe avec le regime du bas force au
        # defaut, et une sortante qui apparait alors dit que la derogation agit.
        causes = {"rien de designe": [], "geste refuse": [],
                  "sortante du bas ECARTEE par derogation": [],
                  "haut seul, non traite par le regime": [], "autre": []}
        for nom in nuls:
            b = bilan_gestes(font, mid, nom)
            if b is None:
                continue
            if b["vides"] == b["vus"]:
                causes["rien de designe"].append(nom)
            elif b["sortie"] is None and b["descente"] is None and (
                    b["notes"] & {"haut non traite"}):
                forcee = bilan_gestes(font, mid, nom, bas="bas")
                cle = ("sortante du bas ECARTEE par derogation"
                       if forcee and forcee["sortie"] is not None
                       else "haut seul, non traite par le regime")
                causes[cle].append(nom)
            elif b["notes"] - {"haut non traite"}:
                causes["geste refuse"].append(
                    f"{nom} ({', '.join(sorted(b['notes'] - {'haut non traite'}))})")
            else:
                causes["autre"].append(nom)
        for lib, gl in causes.items():
            if gl:
                print(f"     {lib} : {len(gl)}   {' '.join(gl)}")
        print(f"     (constat, pas anomalie : le regime du haut est tranche, "
              f"donc un glyphe sans sortante ne recoit plus rien)")

        # 6. le regime du haut est celui qui est ecrit
        avec_haut, exceptions = [], []
        for nom in sorted(attrapes | set(Q.PRESCRIPTIONS)):
            if nom in Q.HORS_TITRAGE or font.glyphs[nom] is None:
                continue
            b = bilan_gestes(font, mid, nom)
            if b is None or b["descente"] is None:
                continue
            reg = Q.prescription(nom).get("rentrantes",
                                          Q.DEFAUT["rentrantes"])
            (exceptions if nom in HAUT_ATTENDU else avec_haut).append(
                f"{nom} {b['descente']:.0f}u ({reg})")
        print(f"  6. regime du haut, defaut ecrit : "
              f"{Q.DEFAUT['rentrantes']}")
        print(f"     exceptions attendues qui recoivent bien un haut : "
              f"{len(exceptions)}/{len(HAUT_ATTENDU)}   "
              f"{' '.join(exceptions) or 'aucune'}")
        print(f"     glyphes hors exception qui recoivent un haut : "
              f"{' '.join(avec_haut) or 'aucun'}")
        total += len(avec_haut) + (len(HAUT_ATTENDU) - len(exceptions))

        # 7. la sortante atteint-elle sa cible ? Section neuve au trente-sixieme
        # tour. Elle existe parce que la reponse etait NON sans que rien ne le
        # dise : `angle_pour_depassement` bornait sa dichotomie a 45 degres et
        # RENDAIT cette borne quand la cible n'y etait pas atteinte, donc une
        # sortie courte ne se distinguait pas d'une sortie pleine. Le
        # trente-cinquieme tour a ecrit que la sortante tient sa promesse
        # partout, a 44,0 et 32,0 unites : elle ne la tient pas, et le t
        # italique ExtraLight sort de 17,0 unites pour 32 demandees.
        satures = []
        for nom in sorted(attrapes | set(Q.PRESCRIPTIONS)):
            if nom in Q.HORS_TITRAGE or font.glyphs[nom] is None:
                continue
            b = bilan_gestes(font, mid, nom)
            if b and b["notes_bas"]:
                for n in sorted(b["notes_bas"]):
                    satures.append(f"{nom} · {n}")
        # DEUX BORNES, DEUX COMPTES. Le point 68, tranche au trente-huitieme
        # tour, fait repondre la borne BASSE comme la haute : une sortie trop
        # longue et une sortie trop courte arrivent par le meme canal, et un
        # libelle unique attribuerait a la borne de 45 degres ce que celle de
        # 0,1 a fait. Les deux restent des constats.
        longues = [s for s in satures if "TROP LONGUE" in s]
        courtes = [s for s in satures if "TROP LONGUE" not in s]
        print(f"  7. sortantes SATUREES : {len(satures)}  "
              f"({len(courtes)} trop courtes par la borne haute de "
              f"{Q.BORNE_SORTIE:.0f} deg, {len(longues)} TROP LONGUES par la "
              f"borne basse de {Q.BORNE_BASSE:g} deg)")
        for s in satures:
            print(f"     {s}")
        print(f"     (constat, pas anomalie. Trop courtes : la borne haute est "
              f"l'etat ecrit, et portee a 70 degres la cible est atteinte dans "
              f"tous ces cas. Trop longues : le bout depasse deja la cible a "
              f"angle nul, donc aucun angle ne peut faire moins et la borne "
              f"basse n'y est pour rien -- point ouvert 67.)")
        print(f"     CE QUE CETTE SECTION NE COUVRE PAS : les petites "
              f"capitales, absentes de la source amont qu'elle lit. Les "
              f"quatorze sorties TROP LONGUES du trente-huitieme tour y sont "
              f"toutes, et c'est la section 10 qui les compte.")

        # 8. les derogations du bas sont-elles exactement celles qui sont
        # attendues ? Section neuve au trente-sixieme tour. Elle MESURE et ne
        # lit pas la table : chaque glyphe du perimetre est rejoue une seconde
        # fois avec `bas="bas"`, le regime du defaut, et la comparaison des deux
        # passes separe trois cas qu'un seul libelle confondrait -- la sortante
        # ECARTEE par une derogation ecrite, la sortante que la geometrie ne
        # designe pas, et la sortante appliquee.
        ecartes, jamais = [], []
        for nom in sorted(gardes):
            if font.glyphs[nom] is None:
                continue
            b = bilan_gestes(font, mid, nom)
            if b is None or b["sortie"] is not None:
                continue
            forcee = bilan_gestes(font, mid, nom, bas="bas")
            (ecartes if forcee and forcee["sortie"] is not None
             else jamais).append(nom)
        connus = BRUT_CONNUS.get(lab, frozenset())
        voulus = sorted(n for n in ecartes if n not in connus)
        manque = sorted(BRUT_ATTENDU - set(voulus))
        trop = sorted(set(voulus) - BRUT_ATTENDU)
        perdus = sorted(connus - set(ecartes))
        print(f"  8. sortante du bas ECARTEE par derogation : "
              f"{len(voulus)}/{len(BRUT_ATTENDU)}   {' '.join(voulus)}")
        if manque:
            print(f"     !! attendus et absents : {' '.join(manque)}")
        if trop:
            print(f"     !! ecartes sans derogation attendue : "
                  f"{' '.join(trop)}")
        if connus:
            etat = ("toujours la" if not perdus
                    else f"DISPARU(S) : {' '.join(perdus)} — le point 65 a-t-il "
                         f"ete corrige ? mettre a jour BRUT_CONNUS")
            print(f"     defaut connu, point ouvert 65, NON CORRIGE : "
                  f"{' '.join(sorted(connus))}  ({etat})")
        print(f"     sans sortante parce que la geometrie n'en designe "
              f"aucune : {len(jamais)}   {' '.join(jamais)}")
        total += len(manque) + len(trop) + len(perdus)

        print(f"  perimetre effectif : {len(gardes)} glyphes gardes, "
              f"{len(attrapes & Q.HORS_TITRAGE)} ecartes")

    morts = sorted(n for n in Q.HORS_TITRAGE if n not in presents_union)
    inutiles = sorted(n for n in presents_union if n not in geste_union)
    print(f"\n--- sur l'union des deux sources")
    print(f"  1. noms exclus qui n'existent dans aucune source : "
          f"{' '.join(morts) or 'aucun'}")
    print(f"  2. noms exclus qu'aucun GESTE n'attrapait : "
          f"{' '.join(inutiles) or 'aucun'}")
    print(f"     (le geste se mesure a la pente {Q.PENTE_BAS}, l'etendue a "
          f"{Q.PENTE_ETENDUE} : un nom exclu se juge sur ce que le geste lui "
          f"ferait)")
    ho = sorted({n for v in hors_etendue.values() for n in v})
    print(f"  9. glyphes que le GESTE attrape hors de l'ETENDUE, et que rien "
          f"n'exclut : {' '.join(ho) or 'aucun'}")
    if ho:
        print("     Chacun recevrait un geste sans etre dans le perimetre "
              "arrete. A ecarter par HORS_TITRAGE, ou a arbitrer.")
    # 10. LES GLYPHES QUE LE PROJET AJOUTE, que ce controle ne voyait pas.
    # Les neuf premieres sections lisent la source AMONT : les quarante-quatre
    # petites capitales du lot 3 n'y sont pas, donc aucune n'a jamais ete
    # regardee par un controle de titrage, alors que `mesure_titrage` les range
    # dans le perimetre par heritage de leur capitale. La pente du geste leur
    # ajoute douze gestes au romain et trente en italique, dont cinq familles
    # ou le geste tombe sur l'ACCENT et non sur le pied. Constat chiffre, pas
    # anomalie : rien n'est tranche sur elles, et rien n'est compile.
    print(f"\n--- 10. les petites capitales, lues dans la source du PROJET")
    for i, (lab, _chemin) in enumerate(SOURCES):
        projet = MT.SOURCES[i][2]
        if not os.path.exists(projet):
            print(f"  {lab} : source du projet absente, RIEN N'EST MESURE ici.")
            continue
        fp = glyphsLib.GSFont(projet)
        midp = {m.id: m for m in fp.masters}
        # TOUTES les petites capitales servies, et non celles que le titrage
        # garde : depuis que Nicolas les a ecartees au trente-huitieme tour,
        # filtrer par `dans_le_titrage` rendrait "0 sur 0" et la section
        # cesserait de discriminer. Elle verifie maintenant l'EXCLUSION, ce qui
        # est la propriete qu'il faut tenir.
        pcs = [g.name for g in fp.glyphs if g.name.endswith(".sc")]
        gardees = [n for n in pcs if Q.dans_le_titrage(n)]
        porteurs, accents, longues = [], [], []
        for nom in sorted(pcs):
            r = bilan_gestes(fp, midp, nom)
            if not r or r["sortie"] is None:
                continue
            porteurs.append(nom)
            # LES SUR-LIVRAISONS SONT ICI ET NULLE PART AILLEURS. La section 7
            # lit l'amont, ou les petites capitales n'existent pas : les
            # quatorze sorties trop longues du trente-huitieme tour lui sont
            # invisibles. Leur cause est mesuree et ce n'est pas la borne
            # basse -- `y.sc` herite de la plongee de 44 unites du Y, reduite
            # au rapport du lot 3, donc 37,8, quand `depassement_pour` lui en
            # demande 32 parce que son nom commence par une minuscule.
            for n in sorted(r["notes_bas"]):
                if "TROP LONGUE" in n:
                    longues.append(f"{nom} · {n}")
            # OU TOMBE LE GESTE : mesure, et non deduit du nom. Un premier jet
            # classait `acircumflex.sc` comme geste sur l'accent parce que son
            # nom porte "circumflex" -- alors qu'au romain le geste tombe sur
            # le pied de la lettre. Le critere est la hauteur du bout coupe :
            # au-dessus de la hauteur d'x de la petite capitale, c'est
            # l'accent. Une etiquette est une mesure.
            if haut_du_geste(fp, midp, nom):
                accents.append(nom)
        print(f"  {lab} : {len(pcs)} petite(s) capitale(s) servie(s), "
              f"{len(gardees)} gardee(s) dans le titrage, "
              f"{len(porteurs)} qui recoivent une sortante DIRECTEMENT")
        # L'ETIQUETTE DIT "DIRECTEMENT", ET CE MOT EST UNE MESURE. Depuis la
        # fusion du quarantieme tour, les 44 petites capitales PORTENT le geste
        # du lot 4 : le lot 3 les derive des capitales du projet, apres
        # `add_fusion`, donc elles en heritent au rapport 574/668. Ce que cette
        # section verifie est autre chose -- qu'aucune ne recoive le reglage
        # appliquee A ELLE-MEME, ce que `dans_le_titrage` interdit toujours par
        # `nom.endswith(".sc")`. Un zero mal etiquete se lirait ici comme
        # "les petites capitales n'ont pas le geste", ce qui est faux.
        print("     (elles le portent en revanche par HERITAGE depuis leur "
              "capitale, ce qui est l'etat voulu depuis la fusion)")
        if gardees or porteurs:
            print(f"     !! le point 67 ecarte TOUTES les petites capitales : "
                  f"gardees {' '.join(gardees)} ; porteuses "
                  f"{' '.join(porteurs)}")
            total += len(gardees) + len(porteurs)
        if accents:
            print(f"     dont {len(accents)} ou le geste tombe sur l'ACCENT : "
                  f"{' '.join(accents)}")
        print(f"     dont {len(longues)} sortie(s) TROP LONGUE(S), que la "
              f"section 7 ne peut pas voir :")
        for s in longues:
            print(f"       {s}")
        else:
            # LE TEMOIN VIT ICI. Un zero ne se distingue pas d'une grandeur
            # morte : la section rejoue une petite capitale en la forcant dans
            # le titrage, et doit la voir bouger. Sans lui, la ligne
            # au-dessus passerait aussi bien le jour ou `bilan_gestes`
            # cesserait de mesurer quoi que ce soit.
            temoin = next((n for n in pcs if n in ("n.sc", "a.sc", "e.sc")),
                          None)
            vu = None
            if temoin is not None:
                anc = Q.HORS_TITRAGE
                try:
                    orig = Q.dans_le_titrage
                    Q.dans_le_titrage = lambda nom: (
                        True if nom == temoin else orig(nom))
                    r = bilan_gestes(fp, midp, temoin)
                    vu = r and r["sortie"] is not None
                finally:
                    Q.dans_le_titrage = orig
                    Q.HORS_TITRAGE = anc
            print(f"     aucune ne recoit rien, ce qui est l'etat tranche. "
                  f"TEMOIN : {temoin} force dans le titrage "
                  f"{'BOUGE, la section sait signaler' if vu else 'NE BOUGE PAS — la section ne discrimine plus'}")
            if temoin is not None and not vu:
                total += 1

    total += len(morts) + len(inutiles) + len(ho)
    total += section11()
    total += section12()
    total += section13()
    total += section14()

    print(f"\nTOTAL : {total} anomalie(s)."
          + ("" if total else "  Le perimetre ecrit dit ce qu'il annonce."))
    # LE CODE DE RETOUR, corrige au cinquante-neuvieme tour. `main` ne rendait
    # rien et le bloc d'entree ne propageait rien : ce controle sortait a 0
    # avec deux anomalies imprimees, seul des cinq controles du projet dans ce
    # cas -- `check_approches`, `check_barre_F`, `check_operateurs` et
    # `check_O` rendent 1. C'est le defaut du tour precedent sur les planches,
    # dans un controle : un signalement qui rend 0 est un signalement qu'un
    # enchainement de commandes ne voit pas. Trouve en exercant la section 12
    # sur un faussage, pas par lecture.
    return total


#: LES DIX-SEPT VALIDES AU REGLAGE GENERAL, trente-neuvieme tour. Nicolas les a
#: regardes sur `planche-ensemble-titrage.png`, romain, ExtraLight et
#: ExtraBold, deux etats cote a cote, et les a valides tels quels : ils gardent
#: le reglage general et AUCUNE LIGNE N'EST ECRITE POUR EUX.
#:
#: LA LISTE VIT ICI PARCE QUE LA TABLE NE PEUT PAS LA PORTER. Un glyphe valide
#: au reglage general et un glyphe que personne n'a jamais regarde sont
#: rigoureusement identiques dans `lot4.PRESCRIPTIONS` : tous deux absents.
#: Sans cette liste, la validation du trente-neuvieme tour n'existerait nulle
#: part, et le jour ou un glyphe entrerait dans le lot -- par un geste de texte
#: nouveau, par un elargissement du repertoire servi -- il prendrait le reglage
#: general sans que personne ne l'ait vu.
#:
#: CE QUI RESTE EN LIMITE CONNUE SUR CES DIX-SEPT, dit au moment du verdict :
#: le G et le R SATURENT la borne de 45 degres dans les masters clairs et
#: sortent donc court -- ce sont deux des quatre saturations que la section 7
#: compte ; le f ne bouge que de 0,3 unite, le lot 2 ayant deja coupe son bout ;
#: le #, le k et le R recoivent DEUX gestes chacun.
#:
#: ILS SONT SEIZE DEPUIS LE QUARANTE-ET-UNIEME TOUR, ET NON DIX-SEPT. `idotless`
#: en sort : Nicolas a ecarte sa sortante en navigateur, sur le dessin fusionne
#: servi, et il rejoint `BRUT_ATTENDU`. UNE VALIDATION SE REVISE COMME UNE
#: MESURE : celle-ci avait ete prise sur une planche d'alphabet, ou 32 unites
#: font cinq pixels et ou aucune lettre n'a de voisine posee. Ce que la liste
#: porte, c'est "Nicolas l'a regarde et l'a garde", pas "le geste est juste" --
#: donc l'endroit ou il l'a regarde compte autant que le fait qu'il l'ait fait.
#:
#: ILS SONT QUINZE DEPUIS LE QUARANTE-TROISIEME TOUR. `k` en sort a son tour,
#: ecarte en navigateur au quarante-deuxieme, et il entre dans `BRUT_ATTENDU`
#: au meme geste -- une seule des deux ecritures, et les deux tables se
#: contrediraient sans qu'aucun controle echoue. C'est la SECONDE validation
#: revisee, apres le i, et les deux fois par le meme deplacement du regard :
#: de la planche d'alphabet vers un texte courant a 18 px. DEUX SUR DIX-SEPT EN
#: DEUX TOURS -- ce que cette liste porte reste a rejuger APRES LA FUSION, et
#: cette liste-la n'existe nulle part.
#:
#: La note ci-dessus annoncait le k parmi les glyphes qui recoivent DEUX gestes
#: chacun, avec le # et le R. Elle reste vraie du # et du R ; le k n'en recoit
#: plus aucun en bas.
#: ILS SONT DIX-HUIT DEPUIS LE QUARANTE-QUATRIEME TOUR, point 74a : le 1, le 4
#: et le 7 entrent. C'est la premiere fois que cette liste GRANDIT -- elle
#: avait perdu le i puis le k, et n'avait jamais rien gagne.
#:
#: OU NICOLAS LES A REGARDES, et la question compte autant que le verdict,
#: puisque c'est ce deplacement du regard qui a fait reviser le i et le k :
#: sur `planche-chiffres-1a-nombres-regular.png` et sa jumelle au Bold, qui
#: composent de VRAIS NOMBRES -- la suite des dix chiffres, "12 480 animaux",
#: "1947 2024 375 %" -- a 200 px de corps, avec le crenage servi par
#: `approches.composer` et non la seule chasse, et les trois etats empiles a la
#: meme abscisse pour que les pieds se comparent a la verticale. Plus
#: `planche-chiffres-2-regime.png`, qui met les deux natures de geste en loupe
#: a 560 px, ligne de base tiree.
#:
#: CE N'EST PAS ENCORE UNE VALIDATION EN NAVIGATEUR, et la distinction est
#: celle que ce projet a payee deux fois. Une planche de nombres composes avec
#: le crenage est plus proche d'un texte qu'une grille d'alphabet -- les
#: chiffres y ont leurs voisins et leur espacement reel -- mais elle n'est pas
#: un texte a 18 px. Nicolas a choisi de NE PAS SERVIR 74a tant que le 0, le 6
#: et le 8 ne sont pas tranches, donc le verdict en navigateur viendra avec
#: 74b, sur les dix chiffres ensemble. Jusque-la, ces trois noms sont a
#: rejuger, comme les 112 autres du perimetre.
#:
#: ILS SONT DIX-SEPT DEPUIS LE QUARANTE-CINQUIEME TOUR : LE 1 EN SORT, LE 4 ET
#: LE 7 RESTENT. Verdict de Nicolas EN NAVIGATEUR, sur le binaire servi de ce
#: tour, `projets-approuves.html` -- un gabarit de cartes RNT, donc du texte
#: courant et des tableaux de chiffres, et non une planche. La reserve ecrite au
#: tour precedent est levee pour le 4, le 7 et le 9 ; elle a mordu sur le 1.
#: TROISIEME VALIDATION DE PLANCHE REVISEE EN TEXTE, apres le i et le k, et les
#: trois fois par le meme deplacement du regard.
#:
#: CE QUE LE NAVIGATEUR MONTRAIT ET QU'AUCUNE PLANCHE NE POUVAIT MONTRER : les
#: gabarits composent presque tous leurs nombres en chiffres TABULAIRES -- le
#: compteur, les references NTS-FR, les effectifs, les colonnes de valeurs --
#: donc le 1 qu'on y lit est `one.tf`, reste PLAT par la decision du tour
#: precedent. Le 1 coupe n'apparait que dans les paragraphes, en proportionnel,
#: ou il penche seul entre un 2 et un 0 plats. Les deux 1 du meme ecran ne se
#: ressemblaient plus, et c'est un fait de GABARIT, invisible sur toute planche.
#:
#: LE 4, LE 7 ET LE 9 NE SONT PAS DANS CE CAS, et c'est ce qui les sauve :
#: `four.tf`, `seven.tf` et `nine.tf` sont des composites purs de leur base,
#: donc ils portent le meme geste dans les deux jeux et rien ne diverge.
#:
#: DEUX TABLES BOUGENT DANS CE GESTE, et non trois : le 1 quitte cette liste ET
#: retourne dans `lot4.HORS_TITRAGE`, donc il sort du perimetre. Il n'entre pas
#: dans `BRUT_ATTENDU`, qui ne porte que des glyphes DU perimetre dont la
#: sortante est ecartee par derogation -- c'est ce qui le distingue du k et du
#: I, restes gardes avec `sortantes=()`.
#: LE R EN SORT AU QUARANTE-NEUVIEME TOUR, et la liste tombe de dix-sept a
#: SEIZE. Voir `BRUT_ATTENDU`, qui le recoit au meme geste : une seule des deux
#: tables modifiee, et un controle dirait valide ce que l'autre dit ecarte.
#: LE `plus` EN SORT AU CINQUANTE-TROISIEME TOUR, et la liste tombe de seize a
#: QUINZE. Voir `BRUT_ATTENDU`, qui le recoit au meme geste : une seule des deux
#: tables modifiee, et un controle dirait valide ce que l'autre dit ecarte sans
#: qu'aucun echoue. Le `plusminus` et le `numbersign` restent ici, relus dans la
#: meme phrase et gardes avec leur plongee.
VALIDES_REGLAGE_GENERAL = frozenset({
    "F", "G", "P", "T", "a", "ampersand", "dagger", "daggerdbl", "f",
    "four", "germandbls", "nine", "numbersign", "plusminus",
    "seven"})


def gestes_reels(fp, midp, nom):
    """Les sortantes REELLEMENT posees sur un glyphe, a l'etat servi.

    LE CRITERE EST L'APPARIEMENT AU JOURNAL DU PRODUCTEUR, et non la direction
    du segment. `mesure_sortante_lot.gestes` separe le segment tourne du
    segment PROLONGE par un seuil de 0,02 degre ; sur le plusminus ExtraLight
    Italic le flanc prolonge tourne de 0,1 degre, parce qu'il n'est pas
    rigoureusement colineaire au coulissement du coin, et il ressortait comme
    un geste `hg` de 54 unites -- en HAUT, sur un glyphe dont le regime du haut
    est `aucune`. `couper_alignements` ecrit l'angle et la sortie de chaque
    sortante qu'il pose : sans entree au journal, rien n'a ete pose.
    """
    out = []
    g = fp.glyphs[nom]
    if g is None:
        return out
    for m in fp.masters:
        lay = next((l for l in g.layers if l.layerId == m.id), None)
        if lay is None:
            continue
        avant = [K.to_segs(p) for p in L.paths(lay)]
        if not any(avant):
            continue
        jour = []
        try:
            MT.appliquer_reglage(lay, nom, midp[m.id], journal=jour)
        except Exception:                                     # noqa: BLE001
            pass
        apres = [K.to_segs(p) for p in L.paths(lay)]
        for gg in MS.gestes(avant, apres, jour):
            if ("err" in gg or gg["depl"] <= 0.01
                    or gg.get("theta") is None or gg.get("sortie") is None):
                continue
            out.append(dict(gg, master=m.name))
        lay.shapes = [K.from_segs(x) for x in avant] + [
            sh for sh in lay.shapes if not hasattr(sh, "nodes")]
    return out


#: Les deux points de depart de la section 12, nommes une fois et lus partout.
#: L'ordre compte pour la lecture : la question de la TABLE d'abord, celle du
#: DESSIN ensuite.
LECTURES_12 = ("etat reconstruit", "dessin servi")


def vus_section12(fp, per, ecrits):
    """Les noms du perimetre, non ecrits, qui recoivent une sortante sur `fp`.

    Le corps est le meme pour les deux lectures de la section 12, et il vit
    ici pour cette raison : deux codes qui appliquent le meme etat doivent
    passer par la meme fonction, piege consigne depuis le vingt-troisieme
    tour. Ce qui change entre les deux lectures est `fp`, et rien d'autre.
    """
    midp = {m.id: m for m in fp.masters}
    return {n for n in per if n not in ecrits and gestes_reels(fp, midp, n)}


def section12():
    """12. LE LOT VALIDE AU REGLAGE GENERAL EST-IL ENCORE CELUI QUI A ETE VU ?

    Exige que les glyphes du perimetre, non ecrits, qui recoivent une sortante
    soient EXACTEMENT les dix-sept de `VALIDES_REGLAGE_GENERAL`. Un entrant est
    un glyphe que Nicolas n'a jamais vu et qui porte pourtant la signature ; un
    sortant est un geste disparu sans decision.

    Elle n'a pas besoin d'un temoin separe : sa liste EST son temoin. Le jour
    ou la mesure cesserait de mesurer, ils manqueraient tous a la fois.

    DEUX LECTURES, arbitrage de Nicolas au cinquante-neuvieme tour. La section
    pose deux questions distinctes, et les deux sont legitimes :

        sur `mesure_titrage.etat_avant_fusion` -- LA TABLE EST-ELLE COHERENTE
        AVEC LE GESTE ? C'est la question du point 100, et le point de depart
        juste pour y repondre : le geste se rejoue sur l'etat que la chaine
        fusionne, donc une seule fois.

        sur `Temoin.glyphs` -- LE DESSIN SERVI EST-IL CONFORME ? C'est la
        question que le point 72 a fait apparaitre, et personne ne l'avait
        nommee. Le geste y est rejoue sur un dessin qui le porte deja, ce qui
        est exactement le defaut du point 100 -- et cette relecture idempotente
        est precisement ce qui rend la lecture sensible a une derive du dessin
        servi.

    CE QUE LA SECONDE LECTURE RATTRAPE, MESURE AU LOT F DU CINQUANTE-HUITIEME
    TOUR. Sur le faussage massif de `mesure_couverture` -- dix glyphes deplaces
    de 30 unites dans les deux sources -- la lecture sur `Temoin.glyphs` rend
    2 anomalies, un `F` SORTANT par source, et la lecture reconstruite en rend
    0. La correction du point 100, juste sur sa propre question, avait retire a
    la section toute sensibilite au dessin servi.

    POURQUOI LA CORRECTION DU POINT 100 NE CHANGEAIT RIEN SUR L'ETAT SAIN.
    `gestes_reels` apparie au JOURNAL du producteur, et `couper_alignements`
    ecrit son entree des qu'il pose une sortante, que le dessin bouge ou non.
    C'est le point 102 pris a l'envers : un journal qui enregistre n'est pas un
    dessin qui bouge, et ici cette propriete PROTEGE la section de
    l'idempotence au lieu de la tromper. Le zero d'avant la correction etait
    juste, pour une raison que personne n'avait ecrite.

    MESURE avant d'ecrire, cinquante-huitieme tour : aucun des 118 noms du
    perimetre n'est absent de l'etat reconstruit, dans les deux sources. Aucune
    des deux lectures ne retire un glyphe de la surveillance.

    LE COMPTE NE DOUBLE PAS. Un ecart vu par les deux lectures est UN ecart :
    les anomalies sont comptees sur l'union des couples (sens, nom), et chaque
    ligne dit quelles lectures la voient. Un compte gonfle est un chiffre faux,
    et c'est le chiffre qui sert a juger un tour.

    UNE LECTURE QUI MANQUE EST UN NON MESURE, jamais un zero : si la source du
    projet est absente, ou si l'etat d'avant fusion ne se reconstruit pas, la
    section le dit et compte une anomalie.
    """
    print("\n12. le lot valide au reglage general, trente-neuvieme tour")
    anomalies = 0
    for isrc, (lab, amont, projet, binaire) in enumerate(MT.SOURCES):
        r = MT.analyser(lab, amont, binaire, verbeux=False)
        if r is None:
            print(f"  {lab} : le perimetre est incalculable. "
                  f"Ce n'est pas un zero, c'est un NON MESURE.")
            anomalies += 1
            continue
        per = r["perimetres"]["le perimetre ARRETE, trente-quatrieme tour"]
        ecrits = set(Q.ETENDU) | set(Q.PRESCRIPTIONS)

        # `if fp is not None` et non `if fp` : la seconde forme interroge la
        # VERACITE d'un `GSFont`, donc son `__len__` le jour ou il en aurait
        # un, et une source vide se lirait comme une source absente.
        fp = MT.etat_avant_fusion(isrc)
        fserv = (glyphsLib.GSFont(projet) if os.path.exists(projet) else None)
        # Les deux lectures sont appariees a `LECTURES_12` par position, et
        # non renommees ici : deux listes de cles ecrites a la main dans le
        # meme fichier finissent par diverger, et une lecture ajoutee d'un
        # seul cote serait ignoree sans un mot. Trouve par une relecture
        # deleguee, avant que la seconde liste n'existe depuis assez longtemps
        # pour mordre.
        etats = dict(zip(LECTURES_12, (fp, fserv)))

        lues = {}
        for cle in LECTURES_12:
            src = etats[cle]
            if src is None:
                print(f"  {lab}, {cle} : la source ne s'ouvre pas ou ne se "
                      f"reconstruit pas. Ce n'est pas un zero, c'est un NON "
                      f"MESURE.")
                anomalies += 1
                continue
            lues[cle] = vus_section12(src, per, ecrits)
            print(f"  {lab}, {cle} : {len(lues[cle])} glyphe(s) non ecrit(s) "
                  f"recoivent une sortante, pour "
                  f"{len(VALIDES_REGLAGE_GENERAL)} valides")

        ecarts = {}
        for cle, vus in lues.items():
            for n in vus - VALIDES_REGLAGE_GENERAL:
                ecarts.setdefault(("ENTRANTS, jamais vus par Nicolas", n),
                                  []).append(cle)
            for n in VALIDES_REGLAGE_GENERAL - vus:
                ecarts.setdefault(("SORTANTS, geste disparu sans decision", n),
                                  []).append(cle)
        for (sens, n), qui in sorted(ecarts.items()):
            ou = ("les deux lectures" if len(qui) == len(LECTURES_12)
                  else f"lecture {qui[0]} SEULE")
            print(f"     !! {sens} : {n}  [{ou}]")
        anomalies += len(ecarts)
    return anomalies


def section11():
    """11. UNE PRESCRIPTION NE SUIT PAS UNE COMPOSITION, et rien ne le disait.

    Ouverte au trente-neuvieme tour par l'AE. Le A porte `exclure={"bg","hc"}`
    depuis son arbitrage ; l'AE et l'Aring dessinent le meme A sous un autre
    nom, ne recevaient rien, et leur pied gauche plongeait. C'est la forme du
    defaut de `e.sc` -- une table indexee par nom ne suit pas une DERIVATION --
    deplacee vers les COMPOSITIONS, et la passation posait deja la question :
    que devient une table indexee par nom sur les 47 glyphes que le projet
    ajoute, et sur ceux qui redessinent une lettre arretee.

    LE NOM NE SERT QU'A SELECTIONNER DES CANDIDATS, le quadrant MESURE decide.
    Deux filets, parce qu'un seul raterait la moitie des cas : le nom, sensible
    a la casse et strictement plus long que la lettre -- un premier jet
    comparait en minuscules et rangeait le T comme une composition du t --, et
    la decomposition canonique Unicode du caractere servi, qui attrape ce que
    le nom ne dit pas.

    POINT DE DEPART, corrige au cinquante-huitieme tour, point ouvert 100.

    Elle lisait `Temoin.glyphs` et y appliquait le geste dans
    `quadrants_coupes`, en se justifiant ainsi : une composition n'existe qu'a
    l'etat servi. MESURE, c'est faux pour ce que cette section regarde --
    l'AE, l'Aring et l'Eth sont des compositions d'ATKINSON, et aucun des 118
    noms du perimetre n'est absent de l'etat reconstruit, dans les deux
    sources. Ce qui n'existe qu'au servi, ce sont les 47 glyphes que le projet
    AJOUTE, et le perimetre n'en contient aucun.

    Elle lit maintenant `mesure_titrage.etat_avant_fusion`, pour la raison que
    la section 13 ecrit deja dans son docstring : rejouer un geste la ou il est
    deja ecrit ne mesure pas ce geste.

    CE QUE LA CORRECTION CHANGE : RIEN, ET LA RAISON EST MESUREE. Les trois
    glyphes que la section regarde rendent exactement les memes quadrants dans
    les deux lectures -- `AE` et `Eth` aucun, `Aring` un `bd` -- dans les deux
    sources. La cause n'est pas que le point de depart serait sans effet : sur
    l'Aring, la mesure du cinquante-huitieme tour donne 44,0 unites de
    deplacement par le geste reconstruit contre 0,2 a 0,4 par le geste rejoue
    sur le projet. **C'est que cette section mesure un QUADRANT et non une
    amplitude**, et le quadrant ne depend pas du point de depart tant que le
    geste a lieu.

    Le zero de cette section etait donc juste avant la correction, et il
    l'etait pour une raison que personne n'avait ecrite. Le point ouvert 100
    annonce un ecart sur 33 des 118 noms du perimetre : cet ecart porte sur la
    LONGUEUR de la sortante, qui n'est pas la grandeur lue ici. La correction
    reste ecrite parce qu'un point de depart faux finit par mordre -- le jour
    ou le filtre `gg["depl"] <= 0.01` rencontrera un glyphe dont la
    reapplication ne deplace rien du tout, le quadrant disparaitra de `qs` sans
    qu'aucune ligne ne change.
    """
    import unicodedata
    print("\n11. prescriptions qui ne suivent pas une COMPOSITION")
    anomalies = 0
    for isrc, (lab, amont, projet, binaire) in enumerate(MT.SOURCES):
        fp = MT.etat_avant_fusion(isrc)
        if fp is None:
            print(f"  {lab} : l'etat d'avant fusion ne se reconstruit pas. "
                  f"Ce n'est pas un zero, c'est un NON MESURE.")
            anomalies += 1
            continue
        midp = {m.id: m for m in fp.masters}
        r = MT.analyser(lab, amont, binaire, verbeux=False)
        if r is None:
            print(f"  {lab} : perimetre non calculable. NON MESURE.")
            anomalies += 1
            continue
        per = r["perimetres"]["le perimetre ARRETE, trente-quatrieme tour"]
        herite = set(r["herite"])
        bas = {"bg", "bc", "bd"}
        ecarte = {n: (bas - set(pr["sortantes"]) if pr.get("sortantes")
                      else bas)
                  for n, pr in Q.PRESCRIPTIONS.items()
                  if pr.get("sortantes") is not None}
        car = {}
        for g in fp.glyphs:
            u = getattr(g, "unicode", None)
            if u:
                try:
                    car[g.name] = chr(int(u, 16))
                except Exception:                             # noqa: BLE001
                    pass
        inv = {v: k for k, v in car.items()}

        def bases_de(nom):
            # LE FILET PAR LE NOM NE VAUT QUE SUR DES LETTRES, et c'est le
            # quarante-neuvieme tour qui l'a appris. `threequarters` entre dans
            # le perimetre a ce tour et `startswith` le rangeait parmi les
            # compositions du `t` : le nom du chiffre commence par la meme
            # lettre, et rien d'autre ne les rapproche. La section signalait
            # donc que la fraction coupe un quadrant que le `t` ecarte, sur un
            # dessin ou aucun `t` n'existe. Un nom de glyphe n'est pas une
            # propriete typographique -- piege du trente-sixieme tour -- et
            # ici il ne selectionne des candidats que si le glyphe long EST une
            # lettre au sens d'Unicode. `AE`, `Aring` et `Eth` le sont ;
            # `threequarters`, de categorie No, ne l'est pas. Le second filet,
            # celui de la decomposition canonique, portait deja cette exigence
            # sans qu'elle soit dite.
            out = set()
            cn = car.get(nom)
            est_lettre = bool(cn) and unicodedata.category(cn).startswith("L")
            for lettre, q in ecarte.items():
                if not q or not est_lettre:
                    continue
                if (nom != lettre and nom.startswith(lettre)
                        and len(nom) > len(lettre)):
                    out.add(lettre)
            c = car.get(nom)
            if c:
                for ch in unicodedata.normalize("NFD", c):
                    b = inv.get(ch)
                    if b and b != nom and ecarte.get(b):
                        out.add(b)
            return out

        def quadrants_coupes(nom):
            qs = set()
            g = fp.glyphs[nom]
            if g is None:
                return qs
            for m in fp.masters:
                lay = next((l for l in g.layers if l.layerId == m.id), None)
                if lay is None:
                    continue
                avant = [K.to_segs(p) for p in L.paths(lay)]
                if not any(avant):
                    continue
                jour = []
                try:
                    MT.appliquer_reglage(lay, nom, midp[m.id], journal=jour)
                except Exception:                             # noqa: BLE001
                    pass
                apres = [K.to_segs(p) for p in L.paths(lay)]
                bb = Q.boite(avant)
                ita = float(getattr(m, "italicAngle", 0) or 0.0)
                for gg in MS.gestes(avant, apres, jour):
                    if "err" in gg or gg["depl"] <= 0.01:
                        continue
                    qs.add(Q.quadrant(avant[gg["contour"]], gg["i"], bb, ita))
                lay.shapes = [K.from_segs(x) for x in avant] + [
                    sh for sh in lay.shapes if not hasattr(sh, "nodes")]
            return qs

        vus, mauvais = [], []
        for nom in sorted(n for n in per if n not in herite):
            bs = bases_de(nom)
            if not bs:
                continue
            qs = quadrants_coupes(nom)
            conflit = set()
            for b in bs:
                conflit |= qs & ecarte[b]
            vus.append(nom)
            if conflit:
                mauvais.append((nom, sorted(bs), sorted(conflit)))
        print(f"  {lab} : {len(vus)} glyphe(s) du perimetre redessinent une "
              f"lettre arretee : {' '.join(vus)}")
        for nom, bs, conflit in mauvais:
            print(f"     !! {nom} coupe {conflit}, que {'/'.join(bs)} "
                  f"ECARTE sur lui-meme")
        anomalies += len(mauvais)

        # LE TEMOIN. Un zero ne se distingue pas d'une grandeur morte : la
        # prescription de l'Aring est retiree en memoire, et son bg -- que le A
        # ecarte -- doit reapparaitre.
        vu = None
        if "Aring" in Q.PRESCRIPTIONS and ecarte.get("A"):
            sauv = Q.PRESCRIPTIONS.pop("Aring")
            try:
                vu = bool(quadrants_coupes("Aring") & ecarte["A"])
            finally:
                Q.PRESCRIPTIONS["Aring"] = sauv
        print(f"     TEMOIN : Aring prive de sa prescription "
              f"{'RETROUVE son bg, la section sait signaler' if vu else 'NE BOUGE PAS — la section ne discrimine plus'}")
        if vu is not True:
            anomalies += 1
    return anomalies


if __name__ == "__main__":
    if "--temoin" in sys.argv:
        # LE TEMOIN DE LA SECTION 14. Il ne rejoue pas une mesure, il fausse
        # le FAIT : le 6 est annonce avec une contreforme de plus qu'il n'en
        # a. Une section qui ne signalerait pas ici ne saurait rien signaler.
        faussee = {n: dict(f) for n, f in Q.FORMES_FERMEES.items()}
        faussee["six"]["creux"] = faussee["six"]["creux"] + 1
        n = section14(faussee)
        print(f"\nTEMOIN section 14 : {n} anomalie(s) — "
              + ("la section sait signaler" if n else
                 "ELLE NE DISCRIMINE PLUS"))
        # LE TEMOIN DU VOLET D, quarante-huitieme tour. Il fausse l'ETAT et
        # non le fait : le 6 est annonce SERVI alors qu'il ne porte aucun
        # contour greffe. Un volet qui ne signalerait pas ici laisserait
        # `FORMES_FERMEES` annoncer un glyphe servi le jour ou l'appel
        # disparaitrait de `make_temoin` -- exactement l'etat dans lequel le
        # bras du O a vecu trente-deux tours.
        f2 = {n2: dict(f) for n2, f in Q.FORMES_FERMEES.items()}
        f2["six"]["etat"] = "servi"
        f2["O"]["etat"] = "chantier"
        n2 = section14(f2)
        print(f"\nTEMOIN volet D : le 6 annonce SERVI, le O ramene a "
              f"chantier — {n2} anomalie(s) — "
              + ("le volet sait signaler une presence qui manque" if n2 else
                 "IL NE DISCRIMINE PAS"))
        # Sous `--temoin`, un temoin qui SIGNALE est le succes : le code de
        # retour vaut 0 quand les deux mordent, 1 quand l'un reste muet.
        raise SystemExit(0 if (n and n2) else 1)
    else:
        # Trois etats, trois codes, et le troisieme est celui qui manquait :
        # 0 mesure et conforme, 1 mesure et signale, 2 NON MESURE.
        code = main()
        raise SystemExit(2 if code == NON_MESURE else (1 if code else 0))
