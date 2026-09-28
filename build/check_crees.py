#!/usr/bin/env python3
"""Controle du DESSIN SERVI des glyphes que la chaine CREE. Point ouvert 103.

LE TROU QU'IL FERME, et il est mesure. Le lot F du cinquante-huitieme tour a
fausse le dessin servi d'une petite capitale de 30 unites, par translation puis
par deformation, et RELANCE tous les controles : aucun n'a bronche. Remesure au
soixante-et-unieme tour sur onze controles qui lisent `Temoin.glyphs` -- trois
de plus qu'alors -- le verdict ne bouge pas. `zero.slashless` est dans le meme
cas. Ce sont 45 glyphes a contour du repertoire servi sans aucun garde-fou de
forme.

    check5 mesure bien le lot 3, mais il le RECONSTRUIT depuis l'amont et ne
    lit jamais le resultat servi. check_crenage_sc lit bien la source du
    projet, mais il y mesure le crenage et la boite, pas le dessin.

L'OBJET EST CE QUE LA CHAINE CREE, et non le lot 3 seul : 55 glyphes par
source, mesures et non recopies -- 44 petites capitales, `zero.slashless`,
`zero.tf.slashless`, `narrownbspace`, depuis le soixante-douzieme tour
`blackStar`, `whiteStar` et `micro`, que la section 8 rejoue, et depuis le
soixante-treizieme `alpha`, `beta`, `rightArrow`, `emod` et `rmod`, que la
section 9 rejoue avec les trois renvois de codes. `zero.tf.slashless`
et `narrownbspace` n'ont aucun contour propre, et la section 7 dit ce que cela
leur coute.

LES DEUX LECTURES, et chaque section dit laquelle elle pose.

  INVARIANT -- une grandeur qui tient sans rien demander au producteur. Elle
  survit a une erreur DU producteur, et elle ne voit que ce qu'elle mesure.
  Sections 2, 3 et 4.

  REJEU -- le producteur rappele sur la source SERVIE, et l'egalite exigee
  noeud par noeud. Elle voit tout ce qui a derive depuis l'ecriture, et elle
  est aveugle a une erreur du producteur lui-meme, qu'elle reproduirait.
  Sections 5 et 6.

  Aucune des deux ne remplace l'autre, et les deux sont necessaires : la
  translation de 30 unites du lot F ne change NI la hauteur NI la structure --
  un contour deplace en bloc emporte ses deux bornes -- donc les sections 3 et
  4 y sont muettes, et ce sont la section 2 et le rejeu qui mordent.

POURQUOI LE REJEU EST EXACT, et c'est un fait de la CHAINE. `make_temoin.process`
ne touche plus une seule capitale apres `lot3` : `crenage_sc` n'ecrit que du
crenage, et `bras_O` ne touche que le `O`, dont la petite capitale est ecartee
par decision du quarante-huitieme tour. La source servie porte donc cote a cote
la capitale et la petite capitale qui en derive, et la derivation se rejoue sur
elle seule -- sans clone amont, sans rejouer la chaine.

    Mesure du soixante-et-unieme tour : le bras du `O` RETIRE comme
    `check_O` le fait, le rejeu tombe juste sur 352 calques sur 352, les deux
    sources et les huit masters, chasse comprise. Sans ce retrait, douze
    calques romains different de 123 noeuds exactement, le compte du bras
    consigne depuis le trente-troisieme tour. Le retrait se MESURE par
    `bras_O.separer`, il n'y a aucune liste de noms a tenir.

IL NE DEPEND D'AUCUNE SOURCE QUI DISPARAIT. Le `/tmp` du bac a sable s'est
efface quinze fois, et `check5` y laisse son clone amont : prive de lui, il
rend une trace Python et le code 1, donc un NON MESURE qui se lit comme un
signalement. Ce controle-ci lit la seule source du projet. Sa section 1, la
seule qui ait besoin de l'amont, se declare NON MESUREE quand il manque et
laisse les six autres conclure.

TROIS CODES DE RETOUR, comme `check_perimetre` depuis le cinquante-neuvieme
tour : 0 mesure et conforme, 1 mesure et signale, 2 NON MESURE.

    python3 check_crees.py [--temoin]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import glyphsLib
from glyphsLib.classes import GSPath

import bras_O as BO
import complements as CP
import dessin as D
import etoiles as ET
import lot3
import make_temoin as MT

ICI = os.path.dirname(os.path.abspath(__file__))

SOURCES = [("roman", os.path.join(ICI, "Temoin.glyphs"),
            "/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs"),
           ("italic", os.path.join(ICI, "Temoin-Italic.glyphs"),
            "/tmp/ahn/sources/AtkinsonHyperlegibleNext-Italic.glyphs")]

#: LES SIX CREATIONS QUI NE SONT PAS DES PETITES CAPITALES. Elles sont
#: nommees ici parce que `make_temoin` ne les porte dans aucune table -- elles
#: naissent dans le corps de `add_slashless`, `add_narrow_nbspace`,
#: `add_micro`, `etoiles.appliquer` et `complements.appliquer`. Une liste ecrite a la main se perime
#: sans que rien ne le dise, et ce projet l'a paye sur `VOISINS_F` : c'est
#: exactement ce que la section 1 surveille, en comparant cette liste au
#: repertoire reellement cree. Elle a mordu au soixante-douzieme tour sur les
#: trois noms neufs, avant que la section 8 ne les prenne.
AUTRES_CREES = ("zero.slashless", "zero.tf.slashless", "narrownbspace",
                ET.PLEINE, ET.VIDE, "micro") + CP.NEUFS

#: Le rapport de derivation du lot 3. LU chez `make_temoin` et jamais recopie :
#: deux definitions du meme nombre finissent par vivre dans deux fichiers, et
#: `check_crenage_sc` l'a paye au cinquante-sixieme tour.
S = MT.HAUTEUR_SC / MT.HAUTEUR_CAP

#: Tolerance du pied, section 2. La dispersion REELLE se mesure avant d'ecrire
#: l'exigence : mediane 0,01 unite sur les 352 calques, maximum 4,78 sur
#: `q.sc` en ExtraBold Italic, dont la queue descend. Le seuil laisse 1,7 fois
#: cette marge et reste quatre fois sous le faussage de 30 unites du lot F.
TOL_PIED = 8.0

#: Tolerance du rapport de hauteur, section 3. Mesure : 0,8527 a 0,8683 pour
#: une cible de 0,8593, l'ecart venant du `q` et du debord des rondes.
TOL_HAUTEUR = 0.015

#: Tolerance du rejeu, sections 5 et 6. `from_segs` arrondit a 0,1 unite ; le
#: projet tient 0,5 unite pour du bruit depuis le cinquante-septieme tour, et
#: un rejeu n'a pas de bruit du tout -- il doit tomber juste.
TOL_REJEU = 0.05


# ------------------------------------------------------------------ lecture

def _bornes(ctrs):
    ys = [y for c in ctrs for _x, y in c]
    return (min(ys), max(ys)) if ys else (None, None)


def _noeuds(layer):
    return [(round(n.position.x, 1), round(n.position.y, 1))
            for sh in layer.shapes for n in (getattr(sh, "nodes", None) or [])]


def _sans_bras(chemin):
    """Une seconde lecture de la source, le bras du `O` retire.

    Une SECONDE LECTURE et non une copie en memoire de la premiere : le projet
    a paye au cinquante-neuvieme tour qu'un cache indexe par `id(font)` survit
    a la modification de son objet, et `lot3.mesures` comme `interpoler`
    lisent la police entiere.

    Rend (police, calques dont le bras a ete retire, porteur absent). Zero
    calque est la bonne reponse sur une source italique, qui n'en porte aucun
    par decision du quarante-septieme tour -- et c'est pourquoi le compte est
    RENDU au lieu d'etre suppose. Le troisieme terme separe ce zero-la du zero
    d'un `O` manquant, que rien d'autre ne distinguerait.
    """
    font = glyphsLib.GSFont(chemin)
    g = font.glyphs[BO.PORTEUR]
    if g is None:
        return font, 0, True
    mids = {m.id for m in font.masters}
    n = 0
    for lay in g.layers:
        if lay.layerId not in mids:
            continue
        base, bras = BO.separer(lay)
        if bras is not None:
            lay.shapes = base
            n += 1
    return font, n, False


# ----------------------------------------------------------------- sections

def section1(servi, amont_path):
    """[GARDE] L'univers des crees, et a-t-il grandi ?

    Elle est la SEULE a demander l'amont, et elle se declare NON MESUREE
    quand il manque au lieu de rendre un zero qui vaudrait succes.
    """
    attendus = set(n for n, _b, _m, _c in lot3.jeu(servi)) | set(AUTRES_CREES)
    manquants = sorted(n for n in attendus if servi.glyphs[n] is None)
    lignes = [f"1. univers des crees      [GARDE] {len(attendus)} attendus, "
              f"{len(manquants)} absents de la source"]
    n = len(manquants)
    for m in manquants:
        lignes.append(f"  !! 1 {m} : attendu dans la source, absent")
    if not os.path.exists(amont_path):
        lignes.append("     NON MESURE : l'amont manque, la completude de "
                      "l'univers n'est pas verifiee (les six autres sections "
                      "n'en ont pas besoin)")
        return lignes, n, True
    amont = glyphsLib.GSFont(amont_path)
    # Un glyphe RENOMME n'est pas un glyphe cree, et sans cette traduction il
    # s'en distinguerait pas : la section compare deux jeux de NOMS, donc un
    # nom neuf porte sur un dessin herite se lit comme une creation. Soixante-
    # troisieme tour, ou `note-musical` est devenu `musicalnote`.
    #
    # LA TABLE SE LIT CHEZ `make_temoin`, elle ne se recopie pas : une copie
    # se serait tue le jour ou la chaine renomme un second glyphe, et ce
    # projet a paye cette lecon sur `approches.table_kern`.
    connus = {MT.RENOMMAGES.get(g.name, g.name) for g in amont.glyphs}
    reels = {g.name for g in servi.glyphs if g.name not in connus}
    trop = sorted(reels - attendus)
    lignes[0] += f", {len(reels)} reellement crees"
    for t in trop:
        n += 1
        lignes.append(f"  !! 1 {t} : cree par la chaine et surveille par "
                      f"personne ; l'univers de ce controle a grandi")
    # Et la traduction ne se contente pas de taire l'alerte : elle MESURE que
    # le renommage n'a touche aucun dessin, calque par calque, contre l'amont
    # sous l'ancien nom. Sans cela, elle serait une excuse ecrite au lieu d'une
    # preuve, et le projet aurait echange un faux positif contre une cecite.
    for ancien, neuf in MT.RENOMMAGES.items():
        ga, gn = amont.glyphs[ancien], servi.glyphs[neuf]
        if ga is None or gn is None:
            n += 1
            lignes.append(f"  !! 1 renommage {ancien} -> {neuf} : "
                          f"{'amont' if ga is None else 'source servie'} sans "
                          "ce glyphe, le renommage n'est pas verifiable")
            continue
        av = {l.layerId: _noeuds(l) for l in ga.layers}
        ap = {l.layerId: _noeuds(l) for l in gn.layers}
        ecarts = [k for k in set(av) | set(ap) if av.get(k) != ap.get(k)]
        if ecarts:
            n += 1
            lignes.append(f"  !! 1 renommage {ancien} -> {neuf} : "
                          f"{len(ecarts)} calque(s) dont le dessin a bouge ; "
                          "un renommage ne dessine pas")
        else:
            lignes.append(f"     renomme {ancien} -> {neuf}, "
                          f"{len(ap)} calque(s) au dessin inchange")
    return lignes, n, False


def _couple(src_sc, src_base, nom, base):
    """Les contours de la petite capitale et ceux de sa base, ou None.

    LA BASE SE PREND SUR LA SOURCE SANS BRAS, et c'est ce qui supprime toute
    exception. Mesure du soixante-et-unieme tour : contre la source servie,
    douze calques romains different d'un contour, et distinguer les vrais
    demandait un test `"O" in base` -- un test de SOUS-CHAINE, qui attrape
    `O`, `OE`, `Ocircumflex` et `Odieresis` quand `OE` est justement ECARTEE
    du bras par `bras_O.GLYPHES_SANS_BRAS`. Un ecart futur sur `oe.sc` aurait
    ete excuse a tort. Contre la source sans bras : zero ecart, aucune
    exception a ecrire, aucune liste a tenir. Trouve par relecture deleguee,
    prouve par execution.
    """
    a, b = src_sc.contours(nom), src_base.contours(base)
    return (a or None), (b or None)


def section2(servi, par_master):
    """[INVARIANT] Le pied de la petite capitale est celui de sa capitale, au
    rapport. C'est la grandeur qui attrape une TRANSLATION, que ni la hauteur
    ni la structure ne voient."""
    lignes, n, pire, sans = [], 0, (-1.0, "", ""), 0
    for mname, src_sc, src_base in par_master:
        for nom, base, _m, _c in lot3.jeu(servi):
            a, b = _couple(src_sc, src_base, nom, base)
            if a is None or b is None:
                # UN GLYPHE SANS CONTOUR N'EST PAS UN GLYPHE CONFORME. Le
                # premier jet passait au suivant : une `.sc` VIDEE de tous ses
                # contours rendait alors zero anomalie sur les trois sections
                # d'invariant, mesure. Les 44 en portent toutes, donc l'absence
                # est une anomalie et non un cas normal.
                n += 1
                sans += 1
                lignes.append(f"  !! 2 {nom} {mname} : contours introuvables "
                              f"({'la .sc' if a is None else 'sa base ' + base})"
                              f" ; rien ne peut etre mesure sur ce calque")
                continue
            amin, _ = _bornes(a)
            bmin, _ = _bornes(b)
            d = abs(amin - bmin * S)
            if d > pire[0]:
                pire = (d, nom, mname)
            if d > TOL_PIED:
                n += 1
                lignes.append(f"  !! 2 {nom} {mname} : pied a {amin:.1f}, "
                              f"attendu {bmin * S:.1f} depuis {base}, "
                              f"ecart {d:.1f} u pour {TOL_PIED:g} tolerees")
    return ([f"2. pied au rapport       [INVARIANT] plus grand ecart "
             f"{pire[0]:.2f} u ({pire[1]} {pire[2]}), tolerance {TOL_PIED:g}"
             + (f", {sans} calque(s) sans contour" if sans else "")]
            + lignes), n


def section3(servi, par_master):
    """[INVARIANT] La hauteur de la petite capitale rapportee a celle de sa
    capitale vaut le rapport du lot 3. MUETTE sur une translation, par
    construction : un contour deplace en bloc emporte ses deux bornes."""
    lignes, n, ext, sans = [], 0, [], 0
    for mname, src_sc, src_base in par_master:
        for nom, base, _m, _c in lot3.jeu(servi):
            a, b = _couple(src_sc, src_base, nom, base)
            if a is None or b is None:
                n += 1
                sans += 1
                lignes.append(f"  !! 3 {nom} {mname} : contours introuvables, "
                              f"aucun rapport de hauteur n'est calculable")
                continue
            amin, amax = _bornes(a)
            bmin, bmax = _bornes(b)
            if bmax - bmin <= 1:
                continue
            r = (amax - amin) / (bmax - bmin)
            ext.append((r, nom, mname))
            if abs(r - S) > TOL_HAUTEUR:
                n += 1
                lignes.append(f"  !! 3 {nom} {mname} : rapport de hauteur "
                              f"{r:.4f} pour {S:.4f}, ecart {abs(r - S):.4f}")
    ext.sort()
    if not ext:
        tete = ("3. rapport de hauteur    [INVARIANT] RIEN A MESURER : aucun "
                "couple lisible, ce n'est pas un succes")
    else:
        tete = (f"3. rapport de hauteur    [INVARIANT] {ext[0][0]:.4f} "
                f"({ext[0][1]} {ext[0][2]}) a {ext[-1][0]:.4f} "
                f"({ext[-1][1]} {ext[-1][2]}), cible {S:.4f} "
                f"+/- {TOL_HAUTEUR}"
                + (f", {sans} calque(s) sans contour" if sans else ""))
    return [tete] + lignes, n


def section4(servi, par_master, n_bras):
    """[INVARIANT] La petite capitale a le meme nombre de contours que sa
    capitale, composants resolus et bras du `O` retire.

    AUCUNE EXCEPTION N'EST ECRITE, et c'est la raison d'etre du retrait : la
    base se prend sur la source sans bras, ou les comptes coincident partout.
    Voir `_couple` pour ce que l'autre voie aurait coute.
    """
    lignes, n, vus = [], 0, 0
    for mname, src_sc, src_base in par_master:
        for nom, base, _m, _c in lot3.jeu(servi):
            a, b = _couple(src_sc, src_base, nom, base)
            if a is None or b is None:
                n += 1
                lignes.append(f"  !! 4 {nom} {mname} : contours introuvables, "
                              f"aucune structure n'est comparable")
                continue
            vus += 1
            if len(a) != len(b):
                n += 1
                lignes.append(f"  !! 4 {nom} {mname} : {len(a)} contours pour "
                              f"{len(b)} sur {base}, bras retire")
    if not vus:
        tete = ("4. structure             [INVARIANT] RIEN A MESURER : aucun "
                "couple lisible, ce n'est pas un succes")
    else:
        tete = (f"4. structure             [INVARIANT] {vus} couples compares "
                f"a la base SANS BRAS ({n_bras} calques degreffes), "
                f"{n} ecart(s), aucune exception ecrite")
    return [tete] + lignes, n


def section5(servi, nu, n_bras):
    """[REJEU] La petite capitale servie est EXACTEMENT ce que `lot3` rend
    depuis la capitale servie, chasse comprise."""
    ids = [m.id for m in nu.masters]
    noms = {m.id: m.name for m in nu.masters}
    cache = lot3.mesures(nu)
    # Le pire part a -1 et non a zero : un rejeu exact rend 0,00 partout, et
    # un `>` strict laisserait alors l'etiquette VIDE. Une etiquette est une
    # mesure, et ce projet en a corrige plus d'une pour moins que cela.
    lignes, n, vus, pire, absents = [], 0, 0, (-1.0, "", ""), 0
    for nom, base, _m, _c in lot3.jeu(nu):
        g = servi.glyphs[nom]
        if g is None:
            # La section 1 le signale deja ; le compter ICI evite qu'un
            # repertoire vide rende "0 anomalie" sur un en-tete muet.
            absents += 1
            n += 1
            lignes.append(f"  !! 5 {nom} : absent de la source servie, rien "
                          f"a rejouer")
            continue
        for mid in ids:
            att = lot3.petite_capitale(nu, base, mid, MT.HAUTEUR_SC,
                                       MT.LARGEUR_SC, MT.APPROCHE_SC, None,
                                       True, cache, ids[1], True)
            lay = g.layers[mid]
            x, y = _noeuds(lay), _noeuds(att)
            vus += 1
            if len(x) != len(y):
                n += 1
                lignes.append(f"  !! 5 {nom} {noms[mid]} : {len(x)} noeuds "
                              f"servis pour {len(y)} rejoues depuis {base}")
                continue
            e = max((max(abs(p[0] - q[0]), abs(p[1] - q[1]))
                     for p, q in zip(x, y)), default=0.0)
            dw = abs(round(lay.width, 1) - round(att.width, 1))
            if max(e, dw) > pire[0]:
                pire = (max(e, dw), nom, noms[mid])
            if e > TOL_REJEU or dw > TOL_REJEU:
                n += 1
                lignes.append(f"  !! 5 {nom} {noms[mid]} : le dessin servi "
                              f"s'ecarte du rejeu de {e:.2f} u, chasse "
                              f"{dw:.2f} u")
    if not vus:
        tete = ("5. image du producteur   [REJEU] RIEN A MESURER : aucun "
                "calque rejoue, ce n'est pas un succes")
    else:
        tete = (f"5. image du producteur   [REJEU] {vus} calques, bras retire "
                f"sur {n_bras}, plus grand ecart {pire[0]:.2f} u "
                f"({pire[1]} {pire[2]}), tolerance {TOL_REJEU}"
                + (f", {absents} .sc absente(s)" if absents else ""))
    return [tete] + lignes, n


def section6(servi):
    """[REJEU] Le zero recousu est ce que `build_slashless_layer` rend depuis
    le `zero` SERVI, et sa version tabulaire le compose bien."""
    lignes, n = [], 0
    g, src = servi.glyphs["zero.slashless"], servi.glyphs["zero"]
    if g is None or src is None:
        return ["6. zero recousu          [REJEU] NON MESURE : zero ou "
                "zero.slashless absent"], -1
    mids = {m.id for m in servi.masters}
    noms = {m.id: m.name for m in servi.masters}
    vus, pire = 0, 0.0
    for lay in src.layers:
        if lay.layerId not in mids:
            continue
        neuf, _diag = MT.build_slashless_layer(lay)
        x, y = _noeuds(g.layers[lay.layerId]), _noeuds(neuf)
        vus += 1
        if len(x) != len(y):
            n += 1
            lignes.append(f"  !! 6 zero.slashless {noms[lay.layerId]} : "
                          f"{len(x)} noeuds servis pour {len(y)} recousus")
            continue
        e = max((max(abs(p[0] - q[0]), abs(p[1] - q[1]))
                 for p, q in zip(x, y)), default=0.0)
        pire = max(pire, e)
        if e > TOL_REJEU:
            n += 1
            lignes.append(f"  !! 6 zero.slashless {noms[lay.layerId]} : "
                          f"s'ecarte du recousu de {e:.2f} u")
    # `zero.tf.slashless` n'a aucun contour propre : ce qui se controle est le
    # nom du composant, pas un dessin. Un composant qui repointerait vers
    # `zero` rendrait un chiffre tabulaire BARRE sans qu'aucune mesure de
    # forme ne le dise.
    tf = servi.glyphs["zero.tf.slashless"]
    if tf is None:
        n += 1
        lignes.append("  !! 6 zero.tf.slashless : absent")
    else:
        mauvais = 0
        for lay in tf.layers:
            if lay.layerId not in mids:
                continue
            cibles = [getattr(s, "componentName", None) for s in lay.shapes]
            if "zero.slashless" not in cibles:
                mauvais += 1
        if mauvais:
            n += 1
            lignes.append(f"  !! 6 zero.tf.slashless : {mauvais} calques ne "
                          f"composent pas zero.slashless")
    return ([f"6. zero recousu          [REJEU] {vus} calques, plus grand "
             f"ecart {pire:.2f} u ; zero.tf.slashless compose bien"] + lignes), n


def _noeuds_chemins(chemins):
    return [(round(n.position.x, 1), round(n.position.y, 1), n.type)
            for p in chemins for n in p.nodes]


def section8(servi):
    """[REJEU] Les etoiles sont ce que `etoiles.calques` rend depuis la source
    SERVIE, et le micro est la copie exacte du `mu` servi.

    Le rejeu des etoiles relit le losange servi, comme le producteur : une
    derive du trait, de la variante ou de la geometrie se voit ici noeud par
    noeud. Le micro se compare au `mu` du meme master, contours, chasse et
    groupes : un composite, qui ferait entrer `mu` dans le perimetre du
    titrage, est un ecart (voir `make_temoin.add_micro`).
    """
    lignes, n = [], 0
    mids = {m.id: m.name for m in servi.masters}
    attendus = {ET.PLEINE: ET.UNICODES[ET.PLEINE], ET.VIDE: ET.UNICODES[ET.VIDE],
                "micro": "00B5"}
    for nom, u in attendus.items():
        g = servi.glyphs[nom]
        if g is None:
            return [f"8. etoiles et micro     [REJEU] NON MESURE : {nom} "
                    "absent"], -1
        if list(g.unicodes or []) != [u]:
            n += 1
            lignes.append(f"  !! 8 {nom} : unicodes {g.unicodes}, attendu {u}")
    try:
        rejeu = ET.calques(servi, ET.VARIANTE, ET.TRAIT)
    except (KeyError, ValueError) as e:
        return [f"8. etoiles et micro     [REJEU] NON MESURE : le producteur "
                f"refuse la source servie ({e})"], -1
    vus, pire = 0, 0.0
    for nom in (ET.PLEINE, ET.VIDE):
        for lay in servi.glyphs[nom].layers:
            if lay.layerId not in mids:
                continue
            m = mids[lay.layerId]
            largeur, plein, evide, _t = rejeu[m]
            ctrs = plein if nom == ET.PLEINE else evide
            attendu = _noeuds_chemins(
                [ET._chemin(c, sens=1 if i == 0 else -1)
                 for i, c in enumerate(ctrs)])
            reel = _noeuds_chemins([s for s in lay.shapes
                                    if isinstance(s, GSPath)])
            vus += 1
            if lay.width != largeur:
                n += 1
                lignes.append(f"  !! 8 {nom} {m} : chasse {lay.width}, "
                              f"rejeu {largeur}")
            if len(reel) != len(attendu) or any(
                    a[2] != b[2] for a, b in zip(reel, attendu)):
                n += 1
                lignes.append(f"  !! 8 {nom} {m} : {len(reel)} noeuds servis "
                              f"pour {len(attendu)} rejoues, ou types differents")
                continue
            e = max((max(abs(a[0] - b[0]), abs(a[1] - b[1]))
                     for a, b in zip(reel, attendu)), default=0.0)
            pire = max(pire, e)
            if e > TOL_REJEU:
                n += 1
                lignes.append(f"  !! 8 {nom} {m} : s'ecarte du rejeu de "
                              f"{e:.2f} u")
    mu, mi = servi.glyphs["mu"], servi.glyphs["micro"]
    if mu is None:
        return [f"8. etoiles et micro     [REJEU] NON MESURE : mu absent"], -1
    if (mi.leftKerningGroup, mi.rightKerningGroup) != (
            mu.leftKerningGroup, mu.rightKerningGroup):
        n += 1
        lignes.append(f"  !! 8 micro : groupes {mi.leftKerningGroup} / "
                      f"{mi.rightKerningGroup}, mu {mu.leftKerningGroup} / "
                      f"{mu.rightKerningGroup}")
    ref = {l.layerId: l for l in mu.layers if l.layerId in mids}
    for lay in mi.layers:
        if lay.layerId not in mids:
            continue
        m = mids[lay.layerId]
        vus += 1
        if any(not isinstance(s, GSPath) for s in lay.shapes):
            n += 1
            lignes.append(f"  !! 8 micro {m} : porte un composant, `mu` "
                          "entrerait dans le perimetre du titrage")
            continue
        r = ref.get(lay.layerId)
        if r is None or lay.width != r.width or _noeuds_chemins(
                lay.shapes) != _noeuds_chemins(
                [s for s in r.shapes if isinstance(s, GSPath)]):
            n += 1
            lignes.append(f"  !! 8 micro {m} : differe de mu")
    return ([f"8. etoiles et micro     [REJEU] {vus} calques, plus grand "
             f"ecart {pire:.2f} u ; micro copie de mu, variante "
             f"{ET.VARIANTE}, trait {ET.TRAIT}"] + lignes), n


def section9(servi):
    """[REJEU] Les cinq glyphes du repertoire du site, soixante-treizieme
    tour, sont ce que `complements.calques` rend depuis la source SERVIE, aux
    variantes arretees ; leurs codes et leurs groupes sont ceux du module, et
    les trois renvois de codes sont poses.

    Le rejeu relit les pieces servies (d, q, o, germandbls, p, minus, greater,
    e, r, ordmasculine), comme le producteur : une piece qui derive, ou une
    variante qui change sans que le glyphe suive, se voit noeud par noeud.
    """
    lignes, n = [], 0
    mids = {m.id: m.name for m in servi.masters}
    for nom in CP.NEUFS:
        g = servi.glyphs[nom]
        if g is None:
            return [f"9. repertoire du site  [REJEU] NON MESURE : {nom} "
                    "absent"], -1
        if list(g.unicodes or []) != [CP.UNICODES[nom]]:
            n += 1
            lignes.append(f"  !! 9 {nom} : unicodes {g.unicodes}, attendu "
                          f"{CP.UNICODES[nom]}")
        if (g.leftKerningGroup, g.rightKerningGroup) != CP.GROUPES[nom]:
            n += 1
            lignes.append(f"  !! 9 {nom} : groupes {g.leftKerningGroup} / "
                          f"{g.rightKerningGroup}, attendu {CP.GROUPES[nom]}")
    for nom, codes in CP.RENVOIS.items():
        g = servi.glyphs[nom]
        portes = {u.upper() for u in ((g.unicodes if g else None) or [])}
        if not set(codes) <= portes:
            n += 1
            lignes.append(f"  !! 9 renvoi {nom} : porte {sorted(portes)}, "
                          f"attendu aussi {list(codes)}")
    try:
        rejeu, _j = CP.calques(servi, CP.VARIANTE_FLECHE, CP.VARIANTE_ALPHA)
    except (KeyError, ValueError) as e:
        return [f"9. repertoire du site  [REJEU] NON MESURE : le producteur "
                f"refuse la source servie ({e})"], -1
    vus, pire = 0, 0.0
    for nom in CP.NEUFS:
        for lay in servi.glyphs[nom].layers:
            if lay.layerId not in mids:
                continue
            m = mids[lay.layerId]
            ref = rejeu[nom][lay.layerId]
            vus += 1
            if any(not isinstance(s_, GSPath) for s_ in lay.shapes):
                n += 1
                lignes.append(f"  !! 9 {nom} {m} : porte un composant")
                continue
            if lay.width != ref.width:
                n += 1
                lignes.append(f"  !! 9 {nom} {m} : chasse {lay.width}, rejeu "
                              f"{ref.width}")
            reel = _noeuds_chemins(lay.shapes)
            attendu = _noeuds_chemins([s_ for s_ in ref.shapes
                                       if isinstance(s_, GSPath)])
            if len(reel) != len(attendu) or any(
                    a[2] != b[2] for a, b in zip(reel, attendu)):
                n += 1
                lignes.append(f"  !! 9 {nom} {m} : {len(reel)} noeuds servis "
                              f"pour {len(attendu)} rejoues, ou types differents")
                continue
            e = max((max(abs(a[0] - b[0]), abs(a[1] - b[1]))
                     for a, b in zip(reel, attendu)), default=0.0)
            pire = max(pire, e)
            if e > TOL_REJEU:
                n += 1
                lignes.append(f"  !! 9 {nom} {m} : s'ecarte du rejeu de "
                              f"{e:.2f} u")
    return ([f"9. repertoire du site  [REJEU] {vus} calques, plus grand ecart "
             f"{pire:.2f} u ; fleche {CP.VARIANTE_FLECHE}, alpha "
             f"{CP.VARIANTE_ALPHA} ; renvois "
             + ", ".join(f"{k} +{len(v)}" for k, v in CP.RENVOIS.items())]
            + lignes), n


def section7(servi):
    """[DECLARATION] Ce que ce controle ne couvre PAS, et pourquoi.

    Elle ne compte aucune anomalie et elle n'est pas decorative : un glyphe
    decide et un glyphe jamais regarde sont identiques dans une table, tous
    deux absents.
    """
    lignes = ["7. hors de portee      [DECLARATION]"]
    for nom in AUTRES_CREES:
        g = servi.glyphs[nom]
        if g is None:
            continue
        encre = any((getattr(s, "nodes", None) or [])
                    for lay in g.layers for s in lay.shapes)
        if encre:
            continue
        if nom == "narrownbspace":
            lignes.append(
                "     narrownbspace : aucun contour, donc aucune mesure de "
                "forme possible -- tout glyphe sans encre est un angle mort "
                "par construction, connu depuis le quarante-deuxieme tour. "
                "Sa chasse est vue sur le BINAIRE par shape_check_kern "
                "section 6.")
        elif nom == "zero.tf.slashless":
            lignes.append(
                "     zero.tf.slashless : composite pur, son dessin est celui "
                "de zero.slashless ; seul le nom du composant se controle, "
                "section 6.")
    return lignes, 0


# ------------------------------------------------------------------- temoin

def _fausser(font, nom, quoi):
    """Les faussages du temoin. Un par section, parce qu'un temoin GENERAL
    n'exerce pas une section neuve et que le total le cache : `check_approches`
    et `check_crenage_sc` l'ont paye le meme jour au cinquante-sixieme tour."""
    g = font.glyphs[nom]
    if g is None:
        return 0
    mids = {m.id for m in font.masters}
    n = 0
    for lay in g.layers:
        if lay.layerId not in mids:
            continue
        formes = [s for s in lay.shapes if (getattr(s, "nodes", None) or [])]
        if not formes:
            continue
        if quoi == "translation":
            for sh in formes:
                for nd in sh.nodes:
                    nd.position.y += 30.0
        elif quoi == "echelle":
            for sh in formes:
                for nd in sh.nodes:
                    nd.position.y = nd.position.y * 1.10
        elif quoi == "contour":
            if len(formes) < 2:
                raise SystemExit(
                    f"!! temoin : {nom} n'a qu'un contour, le retrait ne "
                    f"ferait rien et le silence se lirait comme une cecite.")
            lay.shapes = [s for s in lay.shapes if s is not formes[-1]]
        elif quoi == "noeud":
            formes[0].nodes[0].position.x += 5.0
        n += 1
    return n


def temoin():
    """Chaque section est exercee SEPAREMENT, et les muettes sont imprimees.

    Le compte attendu n'est pas ecrit en dur : ce qui est exige est qu'une
    section qui doit mordre morde, et qu'une section qui ne peut pas voir ce
    faussage-la soit NOMMEE. Un temoin dont on ne lit que le total laisse une
    section neuve rester muette.
    """
    print("=== TEMOIN, un faussage par section, sur la source romaine\n")
    chemin, amont = SOURCES[0][1], SOURCES[0][2]
    essais = (
        ("2 pied",      "b.sc",           "translation", "section2"),
        ("3 hauteur",   "c.sc",           "echelle",     "section3"),
        ("4 structure", "d.sc",           "contour",     "section4"),
        ("5 rejeu",     "e.sc",           "noeud",       "section5"),
        ("6 zero",      "zero.slashless", "noeud",       "section6"),
        ("8 etoile",    ET.VIDE,          "noeud",       "section8"),
        ("8 micro",     "micro",          "noeud",       "section8"),
        ("9 alpha",     CP.ALPHA,         "noeud",       "section9"),
        ("9 fleche",    CP.FLECHE,        "noeud",       "section9"),
        ("9 exposant",  CP.EXP_R,         "noeud",       "section9"),
    )
    faux = 0
    for etq, nom, quoi, cible in essais:
        servi = glyphsLib.GSFont(chemin)
        if _fausser(servi, nom, quoi) == 0:
            raise SystemExit(f"!! temoin : {nom} introuvable, le faussage n'a "
                             f"rien touche. RIEN N'EST CONCLU.")
        nu, n_bras, _sp = _sans_bras(chemin)
        spm = [(m.name, D.Source(servi, m.name), D.Source(nu, m.name))
               for m in servi.masters]
        res = {
            "section2": lambda: section2(servi, spm),
            "section3": lambda: section3(servi, spm),
            "section4": lambda: section4(servi, spm, n_bras),
            "section5": lambda: section5(servi, nu, n_bras),
            "section6": lambda: section6(servi),
            "section8": lambda: section8(servi),
            "section9": lambda: section9(servi),
        }
        ligne = []
        for clef, fn in res.items():
            _l, k = fn()
            if clef == cible:
                etat = "MORD" if k > 0 else "MUETTE"
                ligne.append(f"{clef} {etat} ({k})")
                if k <= 0:
                    faux += 1
            elif k > 0:
                ligne.append(f"{clef} mord aussi ({k})")
        print(f"  {etq:12s} {nom:16s} {quoi:12s} -> {', '.join(ligne)}")
    # La section 1 s'exerce autrement : son objet est l'univers, pas un dessin.
    servi = glyphsLib.GSFont(chemin)
    g = servi.glyphs["a.sc"]
    g.name = "aaa.sc.intrus"
    _l, k, non_mesure = section1(servi, amont)
    etat = ("NON MESUREE, l'amont manque" if non_mesure
            else ("MORD" if k > 0 else "MUETTE"))
    print(f"  {'1 univers':12s} {'a.sc renommee':16s} {'intrus':12s} "
          f"-> section1 {etat} ({k})")
    if not non_mesure and k <= 0:
        faux += 1
    print(f"\n  {'AUCUNE SECTION MUETTE' if not faux else str(faux) + ' SECTION(S) MUETTE(S)'}")
    return 1 if faux else 0


# --------------------------------------------------------------------- main

def main():
    if "--temoin" in sys.argv:
        return temoin()
    # `nb_sections` est initialise ICI et pas dans la boucle : si toutes les
    # sources manquaient, la boucle ne s'executerait jamais et la ligne de
    # total leverait un NameError au lieu de dire NON MESURE.
    total, non_mesure, nb_sections = 0, 0, 0
    for lab, chemin, amont in SOURCES:
        print(f"=== {lab}")
        if not os.path.exists(chemin):
            print(f"  NON MESURE : {chemin} absent. Ce n'est pas un succes.")
            non_mesure += 1
            continue
        servi = glyphsLib.GSFont(chemin)
        nu, n_bras, sans_porteur = _sans_bras(chemin)
        pm = [(m.name, D.Source(servi, m.name), D.Source(nu, m.name))
              for m in servi.masters]
        l1, n1, nm = section1(servi, amont)
        non_mesure += 1 if nm else 0
        if sans_porteur:
            l1.append(f"  !! 1 {BO.PORTEUR} absent de la source : le bras "
                      f"n'a pas de porteur, et son retrait n'a rien fait")
            n1 += 1
        blocs = [(l1, n1)]
        blocs.append(section2(servi, pm))
        blocs.append(section3(servi, pm))
        blocs.append(section4(servi, pm, n_bras))
        blocs.append(section5(servi, nu, n_bras))
        blocs.append(section6(servi))
        blocs.append(section7(servi))
        blocs.append(section8(servi))
        blocs.append(section9(servi))
        n = 0
        for lignes, k in blocs:
            for ligne in lignes:
                print("  " + ligne if not ligne.startswith("  ") else ligne)
            if k < 0:
                non_mesure += 1
            else:
                n += k
        print(f"  --- {lab} : {n} anomalie(s)")
        total += n
        nb_sections = len(blocs)
    # Le compte des sections se LIT sur les blocs reellement joues. Ecrit en
    # dur, il annoncerait encore sept le jour ou une huitieme serait ajoutee,
    # et `check_crenage_sc` imprime deja `len(SECTIONS)` pour cette raison.
    print(f"\nTOTAL : {total} anomalie(s) sur {nb_sections} sections et "
          f"{len(SOURCES)} sources")
    if non_mesure:
        print(f"  dont {non_mesure} section(s) NON MESUREE(S) : ce n'est pas "
              f"un succes, c'est une mesure qui ne prouve rien.")
        return 2 if total == 0 else 1
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
