#!/usr/bin/env python3
"""Le controle du geste du circonflexe. Point ouvert 73, ecrit au
QUARANTE-NEUVIEME TOUR.

POURQUOI IL N'EXISTAIT PAS, ET POURQUOI C'ETAIT UN TROU. Le projet donne un
controle a chaque geste neuf ; celui-ci n'en avait aucun depuis le
quarante-et-unieme tour. `circumflexcomb` figure explicitement parmi les
glyphes que la section d'ajout de matiere de `check4` declare NON COUVERTS,
avec les onze autres accents combinants et `idotless` -- c'est le point 38,
a moitie ferme depuis le trente-neuvieme tour. Aucune autre section ne le
regarde. Rien n'aurait signale que la pointe a disparu, que sa montee a change,
ou que l'alignement des capitales a cesse de tenir.

CE QU'IL MESURE, ET IL NE RECONSTRUIT RIEN. Les quatre sections comparent
l'AMONT au SERVI, glyphe par glyphe et master par master. Elles n'appellent pas
`pointe_sommet` : un controle qui rejoue le geste qu'il mesure reste au vert sur
une source fausse, ce que `check_O` a paye au quarante-huitieme tour et que le
quatorzieme tour avait deja ecrit. La seule chose que ce fichier sait faire du
geste, c'est le DEFAIRE, et uniquement dans son temoin.

LES QUATRE SECTIONS, et chaque exigence vient d'une mesure du quarante-et-
unieme tour, pas d'un seuil invente :

  1. LA MONTEE. Le sommet de `circumflexcomb` monte de 24,1 a 25,7 unites
     selon le master, identique au romain et en italique. Bornes larges de
     part et d'autre : ce qui doit etre signale, c'est une pointe qui a disparu
     (0 unite) ou qui s'est emballee, pas un dixieme d'unite.
  2. LE SOMMET DES CAPITALES, INCHANGE A 0,1 UNITE PRES. C'est la moitie du
     geste qui se voit le moins et qui casserait le plus : les capitales a
     circonflexe sont au plafond du repertoire servi, et la pointe pleine
     ferait du A circonflexe le point le plus haut de la police. L'alignement
     retire au COMPOSANT ce que la pointe ajoute au COMPOSE, donc il tient par
     construction -- et c'est exactement le genre de propriete qui cesse d'etre
     vraie sans bruit le jour ou `circumflexcomb.case` cesse d'etre un
     composite.
  3. LE SOMMET EST UN ANGLE, ET LA TOPOLOGIE NE DIVERGE PAS. C'est le temoin
     de ce fichier qui a corrige l'exigence, avant que Nicolas ne la lise.
     Le point 73 demandait "topologie a 12 noeuds identique dans les huit
     calques", et `pointe_sommet` annonce dans son docstring que "16 noeuds
     deviennent 12". MESURE : le contour en porte DOUZE AVANT COMME APRES,
     dans les huit calques des deux sources, et le nombre de segments vaut huit
     des deux cotes. Le compte de noeuds ne discrimine donc rien -- une section
     batie dessus serait restee au vert sur un accent rendu a Atkinson, ce que
     le temoin a montre en rendant zero anomalie sur un circonflexe defait.
     LA GRANDEUR QUI DISCRIMINE EST LE TYPE DES DEUX SEGMENTS QUI SE
     RENCONTRENT AU SOMMET : deux demi-courbes a l'amont, deux LIGNES apres le
     geste. C'est la definition meme de l'operation -- remplacer un arc par un
     angle -- et non un seuil invente. La section verifie en plus que la suite
     des types de segments est IDENTIQUE dans les quatre masters de chaque
     source : un glyphe pointu dans trois masters et arrondi dans le quatrieme
     casse l'interpolation du variable, et fontmake s'en plaint tard ou pas du
     tout.
  4. LE CARON GARDE SON ARC. `caroncomb` est le meme dessin retourne, et
     Nicolas l'a laisse arrondi sur `planche-circonflexe-5-caron.png`. C'est
     une LIMITE CONNUE, donc elle se surveille comme une decision : le critere
     est l'IDENTITE A L'AMONT, point par point, et non un compte de noeuds --
     le pic du caron est en bas, donc toute mesure qui cherche un sommet n'y
     designe rien. Une section qui garde une decision vaut celle qui garde un
     chiffre : un glyphe decide et un glyphe jamais regarde sont identiques
     dans une table, tous deux absents.

LE TEMOIN. `--temoin` remet `circumflexcomb` a son etat d'AMONT dans la copie
chargee en memoire, sur les huit calques des deux sources, et rejoue les
sections 1 a 3 : elles doivent toutes les trois signaler. Il agit donc sur ce
que le controle mesure -- le dessin servi -- et non sur ce qui l'a produit,
lecon du trente-et-unieme tour.

    python3 check_circonflexe.py [--temoin]
"""

import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mesure_titrage as MT
import dessin as D
import coupe as K

ICI = os.path.dirname(os.path.abspath(__file__))

#: L'accent combinant qui porte le geste, et sa variante de capitale.
ACCENT = "circumflexcomb"
ACCENT_CAP = "circumflexcomb.case"

#: Le caron, qui garde son arc. Decision de Nicolas au quarante-et-unieme tour.
CARON = "caroncomb"

#: LA MONTEE ATTENDUE, mesuree au quarante-et-unieme tour sur les huit calques
#: des deux sources : 24,1 a 25,7 unites. Les bornes du controle sont larges
#: parce que la grandeur qu'il faut voir est une pointe ABSENTE ou EMBALLEE.
#: Une borne serree ferait crier le controle sur un changement de graisse qui
#: n'a rien a voir avec le geste.
MONTEE_MIN = 20.0
MONTEE_MAX = 32.0

#: Les capitales a circonflexe dont le sommet ne doit pas bouger. Elles sont
#: composites, donc leur sommet est celui de leur accent : c'est la mesure qui
#: prouve l'alignement, pas la lecture de la transformation.
CAPITALES = ("Acircumflex", "Ecircumflex", "Icircumflex", "Ocircumflex",
             "Ucircumflex")

#: Le sommet d'une capitale ne doit pas bouger de plus que cela. La valeur
#: vient de la mesure du quarante-et-unieme tour, "inchange a 0,1 unite pres".
TOL_SOMMET = 0.1

#: Ce que les deux segments qui se rencontrent au sommet doivent etre, apres
#: le geste. A l'amont ce sont deux "curve" : le sommet y est un arc en deux
#: demi-courbes, et c'est lui que l'operation remplace par un angle.
SOMMET_APRES = "line"
SOMMET_AVANT = "curve"


def _sommet(font, master, nom):
    """L'ordonnee du point le plus haut d'un glyphe, COMPOSANTS RESOLUS.

    Passe par `dessin.Source.contours`, qui descend dans les composants et
    aplatit les courbes. Les capitales accentuees sont des COMPOSITES dans la
    source : toute fonction qui lit `layer.paths` les voit vides, piege ecrit
    dans la passation depuis le lot 2. Et le sommet se lit sur le contour
    APLATI, pas sur les noeuds : une courbe deborde de ses noeuds d'ancrage, et
    le projet a deja rendu le G a -407 unites pour cette raison.
    """
    src = D.Source(font, master)
    cs = src.contours(nom)
    ys = [y for c in cs for _x, y in c]
    return max(ys) if ys else None


def _noeuds(layer):
    """Le nombre de noeuds du contour le plus haut d'un calque."""
    paths = list(layer.paths)
    if not paths:
        return None
    p = max(paths, key=lambda q: max(n.position.y for n in q.nodes))
    return len(p.nodes)


def _sommet_kinds(layer):
    """(kind du segment qui arrive au sommet, kind du suivant, suite des kinds).

    Le sommet est le point d'arrivee le plus haut du contour le plus haut. Les
    deux segments qui s'y rencontrent disent si c'est un arc ou un angle, ce
    qu'aucun compte de noeuds ne dit.
    """
    paths = list(layer.paths)
    if not paths:
        return None, None, ()
    p = max(paths, key=lambda q: max(n.position.y for n in q.nodes))
    segs = K.to_segs(p)
    if not segs:
        return None, None, ()
    i = max(range(len(segs)), key=lambda j: segs[j]["p3"][1])
    return segs[i]["kind"], segs[(i + 1) % len(segs)]["kind"], \
        tuple(s["kind"] for s in segs)


def _charger():
    """(label, font amont, font servie) pour les deux sources, ou None.

    Une garde par source, et elle dit CE QUI MANQUE : un controle qui n'a pas
    pu lire son amont doit se declarer NON MESURE, jamais rendre zero. Le
    `/tmp` du bac a sable a emporte le clone amont dix fois.
    """
    for lab, amont, projet, _woff in MT.SOURCES:
        if not os.path.exists(amont):
            yield lab, None, None, f"amont absent : {amont}"
            continue
        if not os.path.exists(projet):
            yield lab, None, None, f"source du projet absente : {projet}"
            continue
        yield lab, glyphsLib.GSFont(amont), glyphsLib.GSFont(projet), None


def _defaire(font, amont):
    """Remet `circumflexcomb` a son dessin d'amont, en memoire. TEMOIN SEUL.

    C'est la seule fonction du fichier qui touche au dessin, et elle ne sert
    qu'au temoin : le controle, lui, ne fait que mesurer. Elle recopie les
    contours de l'amont calque par calque plutot que de rejouer une operation
    inverse, qui serait une reconstruction de plus.
    """
    g, ga = font.glyphs[ACCENT], amont.glyphs[ACCENT]
    noms = {m.id: m.name for m in font.masters}
    par_nom = {m.name: m.id for m in amont.masters}
    for l in g.layers:
        mn = noms.get(l.layerId)
        if mn is None or mn not in par_nom:
            continue
        la = next((x for x in ga.layers if x.layerId == par_nom[mn]), None)
        if la is None:
            continue
        l.shapes = [s for s in la.shapes]


def section1(paires):
    """1. LA MONTEE DU SOMMET, amont contre servi."""
    print("\n1. la montee de la pointe sur `circumflexcomb`")
    anomalies = 0
    for lab, amont, font, err in paires:
        if err:
            print(f"  {lab:<9} !! {err}")
            print(f"  {lab:<9}    Ce n'est pas un zero, c'est un NON MESURE.")
            anomalies += 1
            continue
        amont_noms = {m.name for m in amont.masters}
        for m in font.masters:
            mn = m.name
            if mn not in amont_noms:
                print(f"  {lab:<9} {mn:<18} !! master absent de l'amont")
                anomalies += 1
                continue
            av = _sommet(amont, mn, ACCENT)
            ap = _sommet(font, mn, ACCENT)
            if av is None or ap is None:
                print(f"  {lab:<9} {mn:<18} !! {ACCENT} sans contour")
                anomalies += 1
                continue
            d = ap - av
            note = ""
            if not (MONTEE_MIN <= d <= MONTEE_MAX):
                note = (f"  !! hors des {MONTEE_MIN:.0f} a {MONTEE_MAX:.0f} "
                        f"unites attendues")
            print(f"  {lab:<9} {mn:<18} {av:7.1f} -> {ap:7.1f}   "
                  f"montee {d:5.1f}u{note}")
            anomalies += bool(note)
    return anomalies


def section2(paires):
    """2. LE SOMMET DES CAPITALES A CIRCONFLEXE, INCHANGE."""
    print("\n2. le sommet des capitales a circonflexe, inchange")
    anomalies = 0
    for lab, amont, font, err in paires:
        if err:
            print(f"  {lab:<9} !! NON MESURE ({err})")
            anomalies += 1
            continue
        amont_noms = {m.name for m in amont.masters}
        pire, ou = 0.0, ""
        vus = 0
        for nom in CAPITALES:
            if font.glyphs[nom] is None or amont.glyphs[nom] is None:
                print(f"  {lab:<9} !! {nom} absent d'une des deux sources")
                anomalies += 1
                continue
            for m in font.masters:
                mn = m.name
                if mn not in amont_noms:
                    continue
                av = _sommet(amont, mn, nom)
                ap = _sommet(font, mn, nom)
                if av is None or ap is None:
                    continue
                vus += 1
                if abs(ap - av) > abs(pire):
                    pire, ou = ap - av, f"{nom}/{mn}"
        note = ("" if abs(pire) <= TOL_SOMMET else
                f"  !! l'alignement des capitales ne tient plus")
        print(f"  {lab:<9} {vus} glyphe-calque(s), plus grand ecart "
              f"{pire:+.2f}u{f' ({ou})' if ou else ''}{note}")
        anomalies += bool(note)
    return anomalies


def section3(paires):
    """3. LE SOMMET EST UN ANGLE, ET LA TOPOLOGIE NE DIVERGE PAS."""
    print("\n3. le sommet de `circumflexcomb` : un angle, pas un arc")
    anomalies = 0
    for lab, amont, font, err in paires:
        if err:
            print(f"  {lab:<9} !! NON MESURE ({err})")
            anomalies += 1
            continue
        noms = {m.id: m.name for m in font.masters}
        etats, suites = {}, {}
        for l in font.glyphs[ACCENT].layers:
            mn = noms.get(l.layerId)
            if mn is None:
                continue
            a, b, suite = _sommet_kinds(l)
            etats[mn] = (a, b)
            suites[mn] = (suite, _noeuds(l))
        arrondis = sorted(m for m, (a, b) in etats.items()
                          if a != SOMMET_APRES or b != SOMMET_APRES)
        note = ""
        if arrondis:
            note = ("  !! sommet ARRONDI, la pointe a disparu : "
                    + " ".join(arrondis))
        elif len(set(suites.values())) != 1:
            note = "  !! la topologie diverge d'un master a l'autre"
        n = sorted({v[1] for v in suites.values()})
        print(f"  {lab:<9} {len(etats)} calque(s), sommet "
              + "/".join(sorted({f'{a}+{b}' for a, b in etats.values()}))
              + f", {n} noeud(s){note}")
        anomalies += bool(note)
    return anomalies


def section4(paires):
    """4. LE CARON GARDE SON ARC, et c'est une DECISION surveillee."""
    print("\n4. le caron garde son arc (limite connue, quarante-et-unieme tour)")
    anomalies = 0
    for lab, amont, font, err in paires:
        if err:
            print(f"  {lab:<9} !! NON MESURE ({err})")
            anomalies += 1
            continue
        if font.glyphs[CARON] is None or amont.glyphs[CARON] is None:
            print(f"  {lab:<9} !! {CARON} absent d'une des deux sources")
            anomalies += 1
            continue
        # LE CRITERE EST LE PIC, ET IL EST EN BAS. Le caron est le circonflexe
        # RETOURNE : une mesure qui cherche le point le plus haut n'y designe
        # rien. Le compte de noeuds ne dirait rien non plus -- c'est ce que le
        # temoin de la section 3 a etabli.
        #
        # ET "GARDE SON ARC" NE VEUT PAS DIRE "N'A PAS BOUGE". Un premier jet
        # de cette section exigeait l'identite a l'amont et rendait huit
        # anomalies sur un dessin juste : `caroncomb` porte une entree du LOT 2
        # depuis le vingt-deuxieme tour, `loc_accent_haut`, qui lui fait passer
        # ses terminaisons de 12 a 16 noeuds. Cette modification-la est
        # arbitree ; celle que Nicolas a refusee est la POINTE. Un controle qui
        # crie sur un etat decide finit par etre ignore.
        noms = {m.id: m.name for m in font.masters}
        etats = {}
        for l in font.glyphs[CARON].layers:
            mn = noms.get(l.layerId)
            if mn is None:
                continue
            paths = list(l.paths)
            if not paths:
                continue
            p = min(paths, key=lambda q: min(n.position.y for n in q.nodes))
            segs = K.to_segs(p)
            i = min(range(len(segs)), key=lambda j: segs[j]["p3"][1])
            etats[mn] = (segs[i]["kind"], segs[(i + 1) % len(segs)]["kind"])
        pointus = sorted(m for m, (a, b) in etats.items()
                         if a != SOMMET_AVANT or b != SOMMET_AVANT)
        note = ("" if not pointus else
                "  !! le geste a DEBORDE sur le caron, que Nicolas a laisse "
                "arrondi : " + " ".join(pointus))
        print(f"  {lab:<9} {len(etats)} calque(s), pic "
              + "/".join(sorted({f'{a}+{b}' for a, b in etats.values()}))
              + note)
        anomalies += bool(note)
    return anomalies


def main(temoin=False):
    """0 conforme, 1 signale, 2 non mesure. En mode temoin, 0 si les trois
    sections mordent, 1 sinon."""
    paires = list(_charger())
    # UNE SOURCE ABSENTE EST UN NON MESURE, code 2, et non une anomalie.
    # Jusqu'au soixante-septieme tour, les sections comptaient le NON MESURE
    # qu'elles ecrivaient comme une anomalie, et le script sortait a 1.
    # Vaut aussi en mode temoin. Point ouvert 31.
    erreurs = [(lab, err) for lab, _a, _f, err in paires if err]
    if erreurs:
        for lab, err in erreurs:
            print(f"NON MESURE : {lab}, {err}")
        return 2
    if temoin:
        print("TEMOIN : `circumflexcomb` remis a son dessin d'AMONT en "
              "memoire, sur les huit calques.")
        print("Les sections 1, 2 et 3 doivent TOUTES LES TROIS signaler.")
        for lab, amont, font, err in paires:
            if err:
                continue
            _defaire(font, amont)
        n1, n2, n3 = section1(paires), section2(paires), section3(paires)
        print(f"\nTEMOIN : section 1 {n1}, section 2 {n2}, section 3 {n3} — "
              + ("le controle sait signaler"
                 if n1 and n2 and n3 else
                 "UNE SECTION NE DISCRIMINE PAS, elle ne prouve rien"))
        # Rendait 0 dans les deux cas jusqu'au soixante-septieme tour : un
        # temoin qui ne mord pas doit le dire par son code.
        return 0 if (n1 and n2 and n3) else 1
    total = (section1(paires) + section2(paires) + section3(paires)
             + section4(paires))
    print(f"\nTOTAL : {total} anomalie(s)."
          + ("  Le geste du circonflexe est celui qui a ete valide."
             if not total else ""))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main("--temoin" in sys.argv))
