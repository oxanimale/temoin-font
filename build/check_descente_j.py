#!/usr/bin/env python3
"""Le controle de la descente du crochet du j. Point 105, soixantieme tour.

QUATRE SECTIONS, et chacune repond a une question que les autres ne posent pas.

    1  le geste est-il POSE, dans les huit masters des deux sources, a la
       valeur exacte que `descente_j.DESCENTE_J` annonce ;
    2  le jour A+j atteint-il le plancher SANS CRENAGE, au couloir exact, et
       depasse-t-il le minimum mesure -- une valeur sous le minimum serait un
       contact, une valeur au-dessus est la decision de Nicolas ;
    3  la FAMILLE suit-elle par composition : `jacute` porte la meme queue et
       n'est dans aucune table de paires, donc c'est le geste seul qui le
       corrige, et rien d'autre ne le dirait ;
    4  le geste coute-t-il quelque chose au VOISINAGE : aucune paire du j ne
       doit devenir pire qu'Atkinson, et le `j+j` de l'ExtraBold est le cas
       limite, a 0,1 unite au-dessus.

LA REFERENCE EST ATKINSON ET JAMAIS ZERO. `idieresis+j` tient +4,5 unites dans
la police de base a l'ExtraBold, et un controle qui exigerait le plancher
crierait sur un etat que le projet n'a pas fabrique.

CODES DE RETOUR, comme `check_perimetre` depuis le cinquante-neuvieme tour :
0 mesure et conforme, 1 mesure et signale, **2 NON MESURE**. Un controle qui
n'a pas lu sa source ne dit pas la meme chose qu'un controle qui n'a rien
trouve, et le code de retour est le seul endroit ou un enchainement lit la
difference.

    python3 check_descente_j.py
    python3 check_descente_j.py --temoin
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import glyphsLib                                              # noqa: E402

import approches as A                                         # noqa: E402
import dessin as D                                            # noqa: E402
import descente_j as DJ                                       # noqa: E402
import mesure_titrage as MT                                   # noqa: E402
from balayage_lot4b import couloir_exact                      # noqa: E402

#: La tolerance de position. `coupe.from_segs` arrondit a 0,1 unite, donc un
#: geste de 15 unites peut se lire 15,0 ou 14,9 selon l'arrondi des noeuds.
TOL = 0.25

#: Les voisins regardes par la section 4. DEDUITS de ce que la mesure du
#: soixantieme tour a signale, et non recopies au hasard : ce sont les seules
#: paires du `j` que le minorant place sous le plancher apres le geste.
VOISINS_SURVEILLES = ("idieresis", "j", "q", "semicolon", "K")


def etat_sans_geste(projet):
    """La source servie, moins le geste. Rend (font, font_sans).

    Le geste etant ECRIT dans le dessin servi, mesurer l'avant demande de le
    defaire : on le rejoue a l'envers, par la meme fonction, avec des valeurs
    opposees. Un avant reconstruit autrement serait un autre dessin.
    """
    font = glyphsLib.GSFont(projet)
    sans = glyphsLib.GSFont(projet)
    DJ.appliquer(sans, valeurs={m: -v for m, v in DJ.DESCENTE_J.items()})
    return font, sans


def section1(font, sans, lab, anomalies):
    """Le geste est-il pose, a la valeur exacte, dans les huit masters."""
    for m in font.masters:
        attendu = DJ.DESCENTE_J.get(m.name)
        if attendu is None:
            anomalies.append(f"1 {lab} {m.name} : aucune valeur ecrite")
            continue
        sv = D.Source(font, m.name)
        ss = D.Source(sans, m.name)
        ecart = (min(y for c in ss.contours("j") for _x, y in c)
                 - min(y for c in sv.contours("j") for _x, y in c))
        if abs(ecart - attendu) > TOL:
            anomalies.append(
                f"1 {lab} {m.name} : le j descend de {ecart:.1f} pour "
                f"{attendu:.1f} ecrit")


def section2(font, lab, anomalies):
    """Le jour A+j, SANS crenage, contre le plancher et contre le minimum."""
    for m in font.masters:
        src = D.Source(font, m.name)
        jour = couloir_exact(src, "A", "j", 0.0)
        if jour is None:
            anomalies.append(f"2 {lab} {m.name} : NON MESURE")
            continue
        if jour < A.JOUR_MIN:
            anomalies.append(
                f"2 {lab} {m.name} : jour A+j {jour:.2f} sous le plancher "
                f"{A.JOUR_MIN:.0f}, sans crenage")
        ecrit, mini = DJ.DESCENTE_J[m.name], DJ.D_MINIMUM[m.name]
        if ecrit < mini - TOL:
            anomalies.append(
                f"2 {lab} {m.name} : descente ecrite {ecrit:.0f} sous le "
                f"minimum mesure {mini:.0f}")


def section3(font, lab, anomalies):
    """La famille suit, et le contact que personne ne regardait a disparu.

    C'EST LA SECTION QUI GARDE LE RESULTAT LE MOINS VISIBLE DU TOUR, et le
    glyphe qui compte n'est pas celui qu'on croit. **`jdotless` n'est dans
    AUCUNE des trois tables de paires ni dans `VOISINS_F`**, et il est SHAPE
    des qu'un `j` porte une marque combinante : mesure au shaping sur le
    binaire servi, `j` + U+0301 rend `jdotless` + `acutecomb`. Il touchait
    donc le A de -81,0 unites au Bold, dans un etat SERVI et ATTEIGNABLE par
    une saisie, quand la table refermait la paire `A+j` a cote.

    `jacute`, lui, existe dans le binaire et **n'est jamais shape** : aucune
    sequence ne le produit, comme les sept glyphes inatteignables du point 88.
    Il portait le meme contact, sans consequence.

    Les deux sont corriges par le geste, parce que les deux portent le meme
    dessin. Aucune table ne les nomme, et aucune n'aurait pu.
    """
    for nom in (DJ.PORTEUR,) + DJ.SUIVEURS:
        if font.glyphs[nom] is None:
            continue
        for m in font.masters:
            src = D.Source(font, m.name)
            jour = couloir_exact(src, "A", nom, A.kern(font, m.id, "A", nom))
            if jour is None:
                anomalies.append(f"3 {lab} {m.name} A+{nom} : NON MESURE")
                continue
            if jour < 0:
                anomalies.append(
                    f"3 {lab} {m.name} : A+{nom} en CONTACT, {jour:.1f}")


def section4(font, sans, amont, lab, anomalies):
    """Le GESTE ne degrade aucune paire du j SOUS la police de base.

    LE CRITERE N'EST PAS "MIEUX QU'ATKINSON", ET UN PREMIER JET S'Y EST
    TROMPE. Il rendait cinq anomalies sur un etat juste : `K+j` est ferme au
    plancher par `paires_contacts` depuis le cinquante-neuvieme tour, donc il
    est PLUS SERRE qu'Atkinson par DECISION, et un controle qui compare a
    l'amont crie sur ce qu'une decision a voulu. Sixieme recidive du garde-fou
    qui crie a tort dans ce projet.

    LE CRITERE TIENT EN DEUX TERMES, ET IL EN FAUT DEUX. Le geste FERME
    reellement une paire, `j+j`, de 0,4 unite au romain et 0,3 en italique a
    l'ExtraBold : les deux j se suivant, le second descend sous le premier.
    C'est mesure, c'est petit, et la valeur d'arrivee reste AU-DESSUS
    d'Atkinson. Une section qui crierait sur toute fermeture interdirait un
    geste que Nicolas a validé ; une section qui ne regarderait qu'Atkinson
    laisserait passer une fermeture sur une paire ou le projet est deja plus
    large. Il faut donc les deux : anomalie quand le geste ferme ET que le
    resultat passe sous la police de base.
    """
    ida = {m.name: m.id for m in amont.masters}
    for m in font.masters:
        if not DJ.DESCENTE_J.get(m.name):
            continue
        st, ss = D.Source(font, m.name), D.Source(sans, m.name)
        sa = D.Source(amont, m.name)
        vus = set()
        for v in VOISINS_SURVEILLES:
            if font.glyphs[v] is None or amont.glyphs[v] is None:
                continue
            for a, b in ((v, "j"), ("j", v)):
                if (a, b) in vus:
                    continue
                vus.add((a, b))
                k = A.kern(font, m.id, a, b)
                ct = couloir_exact(st, a, b, k)
                cs = couloir_exact(ss, a, b, k)
                ca = couloir_exact(sa, a, b,
                                   A.kern(amont, ida[m.name], a, b))
                if ct is None or cs is None or ca is None:
                    anomalies.append(f"4 {lab} {m.name} {a}+{b} : NON MESURE")
                    continue
                if ct < cs - TOL and ct < ca - TOL:
                    anomalies.append(
                        f"4 {lab} {m.name} : le geste ferme {a}+{b} de "
                        f"{cs:.1f} a {ct:.1f}, sous les {ca:.1f} d'Atkinson")


def main(temoin=False):
    total, lus = [], 0
    for isrc, (lab, amont_p, projet, _b) in enumerate(MT.SOURCES):
        if not os.path.exists(projet) or not os.path.exists(amont_p):
            print(f"  {lab} : source absente, NON MESURE")
            continue
        amont = glyphsLib.GSFont(amont_p)
        font, sans = etat_sans_geste(projet)
        if temoin:
            # LE TEMOIN DEFAIT LE GESTE. Il doit agir sur ce que le controle
            # MESURE, et non sur ce qui l'a produit : un temoin qui toucherait
            # le crenage laisserait les sections 1 et 3 muettes.
            font = sans
        lus += 1
        anomalies = []
        if not temoin:
            section1(font, sans, lab, anomalies)
        section2(font, lab, anomalies)
        section3(font, lab, anomalies)
        section4(font, sans, amont, lab, anomalies)
        for a in anomalies:
            print(f"  !! {a}")
        print(f"  {lab} : {len(anomalies)} anomalie(s)")
        total += anomalies
    if lus == 0:
        print("NON MESURE : aucune source lue.")
        return 2
    print(f"TOTAL {len(total)} anomalie(s)")
    if temoin:
        # Sous `--temoin`, un controle qui signale est le succes.
        print("temoin : le geste defait doit faire crier les sections 2, 3 "
              "et 4.")
        return 0 if total else 1
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(temoin="--temoin" in sys.argv))
