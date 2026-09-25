#!/usr/bin/env python3
"""Controle du bras du O : le reglage ecrit rend-il la forme qui a ete validee.

POURQUOI IL EXISTE. Le projet donne un controle a chaque geste neuf, et le
bras du O n'en avait aucun -- il etait arrete depuis le quinzieme tour et
n'etait appele par aucun script de production, donc rien ne pouvait dire que
sa forme avait bouge. `lot4.O_TITRAGE` a change au quarante-septieme tour,
apres trois planches et deux corrections de Nicolas : sans ce fichier, la
prochaine modification du reglage passerait sans que rien ne la mesure.

CINQ SECTIONS. Les quatre premieres mesurent ce que le REGLAGE rend ; la
cinquieme, neuve au quarante-huitieme tour, mesure ce que la SOURCE porte. La
distinction n'est pas theorique : le bras a vecu trente-deux tours arrete,
mesure, et appele par aucun script de production, et les quatre premieres
sections rendaient zero pendant tout ce temps.

  1  LES GRANDEURS VALIDEES. Chaque master romain doit rendre ce que Nicolas a
     regarde : l'epaisseur de base, l'angle du coin blanc, la longueur de
     l'aiguille, les degres noyes. Les valeurs vivent ici et non dans `lot4`,
     pour la meme raison que `VALIDES_REGLAGE_GENERAL` vit dans
     `check_perimetre` : lire la table pour verifier la table ne verifie rien.

  2  LES GARDE-FOUS DE FORME, ceux du quinzieme tour et du dix-huitieme :
     saillie nulle, jour au bout au-dessus de 24 unites, une tache et une
     contreforme aux DEUX resolutions.

  3  LA RELATION QUI LIE LES DEUX TABLES. La racine reste dans la paroi tant
     que `enfoui >= ep_facteur / 2`. Elle est sans dimension, donc vraie dans
     les quatre masters, et elle interdit de toucher une table sans l'autre.

  4  L'ITALIQUE EST ECARTE, ET C'EST UNE DECISION. Nicolas l'a rendue au
     quarante-septieme tour : les O italiques n'ont pas de geste et restent
     ceux d'Atkinson. La section exige que `lot4.MASTERS_SANS_BRAS` porte
     exactement les quatre masters italiques et qu'aucun d'eux ne soit dans
     `O_TITRAGE` -- les deux ensemble seraient une contradiction, comme un
     glyphe a la fois prescrit et exclu au titrage.

  5  LE BRAS EST-IL SERVI, ET EST-CE CELUI DU REGLAGE. Le O romain porte un
     bras dans ses quatre masters, identique noeud a noeud a celui que
     `bras_O.construire` rend ; le O italique n'en porte aucun ; et les
     glyphes qui REDESSINENT un O sous un autre nom n'en portent pas non plus
     -- `o` au dix-neuvieme tour, `o.sc`, `Oslash` et `OE` au quarante-
     huitieme. Sans ce dernier volet, deplacer l'etape avant le lot 3 ferait
     descendre le bras dans `o.sc` sans qu'une ligne du projet le dise.

LE TEMOIN. `--temoin` rejoue la section 1 avec `courbe` fausse de 0,10 : les
quatre masters doivent sortir du gabarit. Il rejoue aussi la section 5 en deux
volets, le bras retire puis le reglage fausse, parce qu'elle pose deux
questions. Un zero ne se distingue pas d'une
mesure morte, et ce projet a deja rencontre un controle qui rendait zero en
etant correct et inutile.

IL LIT `Temoin.glyphs`, la source du PROJET, et non l'amont : le bras se pose
sur le O tel qu'il est servi, et le lot 2 ne le touche pas.

    python3 check_O.py [--temoin]
"""

import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lot2 as L
import lot4 as Q
import mesure_O as M
import bras_O as BR
import coupe as K
import dessin as D

ICI = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(ICI, "Temoin.glyphs")
SOURCE_ITAL = os.path.join(ICI, "Temoin-Italic.glyphs")
MASTERS = ("ExtraLight", "Regular", "Bold", "ExtraBold")

#: CE QUE NICOLAS A VALIDE, et OU il l'a regarde. Mesure au quarante-septieme
#: tour sur `Temoin.glyphs`, apres trois planches : `planche-O-1b` pour le
#: principe du bras, en TEXTE a 18 px ; `planche-O-4-base` pour l'epaisseur de
#: la base ; `planche-O-6-coin` puis `planche-O-8-fin` pour le coin blanc.
#:
#: PUIS SUR LE BINAIRE SERVI, EN NAVIGATEUR, au quarante-huitieme tour, sur
#: `gabarits/bras-O.html` : le O a 18 px aux quatre masters, le groupe
#: confusable O 0 Q C G, et le sigle en capitales pleines a cote du meme sigle
#: en petites capitales. Chaque bande y opposait le servi a un Temoin SANS
#: BRAS compile dans la meme session, donc les deux termes ne differaient que
#: par ce contour. C'est la validation qui compte : une planche pose des
#: lettres en grille, et le projet a revise le i, le k et le 1 pour cela.
#:
#: base     l'epaisseur du bras a sa racine, en unites.
#: coin     l'angle d'ouverture du blanc au-dessus de la base. PETIT = aiguille.
#: aiguille l'arc avant que le jour atteigne 24 unites. GRAND = longue.
#: noye     les degres de spirale caches dans la paroi. C'est le PRIX de
#:          l'aiguille, et le douzieme tour l'a paye sans le mesurer.
VALIDE = {
    "ExtraLight": dict(base=48, coin=40.6, aiguille=28, noye=6),
    "Regular": dict(base=72, coin=36.0, aiguille=33, noye=13),
    "Bold": dict(base=104, coin=29.6, aiguille=42, noye=30),
    "ExtraBold": dict(base=106, coin=28.6, aiguille=44, noye=34),
}

#: Tolerances. Les mesures sont deterministes ; la marge absorbe un changement
#: de version de scipy ou de PIL, pas un changement de reglage -- 0,10 sur
#: `courbe` deplace le coin de 3 a 5 degres, donc le temoin sort largement.
TOL = dict(base=1.5, coin=1.5, aiguille=2.0, noye=2.0)

#: Le seuil de jour du projet, pose au dix-huitieme tour. A ne pas confondre
#: avec les 52 unites du quinzieme tour, qui etaient la valeur OBSERVEE de
#: l'etat d'alors et que la passation a longtemps lue comme une regle.
SEUIL_JOUR = 24.0


def mesurer(font, mid, master, ecart_courbe=0.0):
    lay = next(l for l in font.glyphs["O"].layers if l.layerId == mid[master])
    genre, r = Q.reglage_O(master)
    if ecart_courbe:
        r = dict(r, courbe=r["courbe"] + ecart_courbe)
    # LE BRAS ECRIT SE RETIRE AVANT DE MESURER, depuis que la chaine le pose.
    # Sans cela `famille_O` rendrait une base qui le contient DEJA et y
    # superposerait celui qu'elle construit : les quatre grandeurs seraient
    # rigoureusement inchangees meme si la source portait un bras faux, parce
    # que la mesure porte sur le bras CONSTRUIT. Un controle qui redecouvre
    # son objet mesure autre chose que ce qu'il croit -- c'est le defaut de la
    # coupe oblique au quatorzieme tour. Ce que la source porte vraiment est
    # l'objet de la section 5, et d'elle seule.
    sauv = list(lay.shapes)
    _base_ecrite, bras_ecrit = BR.separer(lay)
    if bras_ecrit is not None:
        lay.shapes = [s for s in sauv if s is not bras_ecrit]
    try:
        f = M.fente(lay, dict(r))
        base, sus = M.famille_O(lay, genre, dict(r))
    finally:
        lay.shapes = sauv
    taches, creux, accord = M.topologie(base, sus)
    return dict(base=M.ep_paroi(lay) * r["ep_facteur"], coin=f["angle"],
                aiguille=f["L24"], noye=f["cache"], saillie=f["saillie"],
                jour=f["jour_bout"], taches=taches, creux=creux,
                accord=accord, r=r)


def section1(font, mid, ecart_courbe=0.0):
    print("\n1. les grandeurs validees par Nicolas")
    anomalies = 0
    for mn in MASTERS:
        m = mesurer(font, mid, mn, ecart_courbe)
        att = VALIDE[mn]
        ecarts = [f"{c} {m[c]:.1f} pour {att[c]} attendu"
                  for c in ("base", "coin", "aiguille", "noye")
                  if abs(m[c] - att[c]) > TOL[c]]
        print(f"  {mn:<12} base {m['base']:>5.0f}u  coin {m['coin']:>5.1f}deg  "
              f"aiguille {m['aiguille']:>4.0f}u  noye {m['noye']:>4.0f}deg"
              + ("   " + " | ".join(ecarts) if ecarts else ""))
        anomalies += len(ecarts)
    return anomalies


def section2(font, mid):
    print("\n2. les garde-fous de forme, quinzieme et dix-huitieme tours")
    anomalies = 0
    for mn in MASTERS:
        m = mesurer(font, mid, mn)
        dr = []
        if m["saillie"] > 0.5:
            dr.append(f"la racine RESSORT de {m['saillie']:.1f}u")
        if m["jour"] < SEUIL_JOUR:
            dr.append(f"jour au bout {m['jour']:.0f}u sous le seuil "
                      f"de {SEUIL_JOUR:.0f}")
        if not (m["taches"] == 1 and m["creux"] == 1):
            dr.append(f"topologie {m['taches']} tache(s), {m['creux']} creux")
        if not m["accord"]:
            dr.append("les deux resolutions NE CONCORDENT PAS")
        print(f"  {mn:<12} saillie {m['saillie']:>4.1f}  jour {m['jour']:>5.0f}u"
              f"  {m['taches']} tache / {m['creux']} creux, deux resolutions "
              f"{'accord' if m['accord'] else 'DESACCORD'}"
              + ("   " + " | ".join(dr) if dr else ""))
        anomalies += len(dr)
    return anomalies


def section3():
    print("\n3. la racine reste dans la paroi : enfoui >= ep_facteur / 2")
    anomalies = 0
    for mn in MASTERS:
        _genre, r = Q.reglage_O(mn)
        marge = r["enfoui"] - r["ep_facteur"] / 2.0
        print(f"  {mn:<12} enfoui {r['enfoui']:.2f}  ep_facteur "
              f"{r['ep_facteur']:.2f}  marge {marge:+.3f}"
              + ("   !! la racine ressortirait" if marge < 0 else ""))
        if marge < 0:
            anomalies += 1
    return anomalies


ITALIQUES = ("ExtraLight Italic", "Italic", "Bold Italic", "ExtraBold Italic")


def section4():
    print("\n4. l'italique est ecarte, et c'est une decision")
    anomalies = 0
    manque = sorted(set(ITALIQUES) - set(Q.MASTERS_SANS_BRAS))
    trop = sorted(set(Q.MASTERS_SANS_BRAS) - set(ITALIQUES))
    if manque:
        print(f"  !! italiques absents de MASTERS_SANS_BRAS : {' '.join(manque)}")
    if trop:
        print(f"  !! MASTERS_SANS_BRAS porte un nom qui n'est pas italique : "
              f"{' '.join(trop)}")
    anomalies += len(manque) + len(trop)
    # Une table qui porterait a la fois la valeur et l'exclusion serait une
    # contradiction, pas une nuance.
    dedans = []
    for cle, val in Q.O_TITRAGE[1].items():
        if isinstance(val, dict):
            dedans += [f"{cle}[{m}]" for m in Q.MASTERS_SANS_BRAS if m in val]
    if dedans:
        print(f"  !! ecartes ET presents dans O_TITRAGE : {' '.join(dedans)}")
    anomalies += len(dedans)
    # Le temoin de la section EST son appel : si `reglage_O` cessait de
    # refuser, la ligne ci-dessous le dirait.
    refuse = 0
    for m in ITALIQUES:
        try:
            Q.reglage_O(m)
        except ValueError:
            refuse += 1
    print(f"  {len(Q.MASTERS_SANS_BRAS)} master(s) ecarte(s), "
          f"{refuse}/{len(ITALIQUES)} refuse(s) par reglage_O : "
          + ("les O italiques restent ceux d'Atkinson"
             if refuse == len(ITALIQUES) else "!! un italique passe"))
    anomalies += len(ITALIQUES) - refuse
    return anomalies


#: L'ecart de position d'un noeud au-dela duquel le bras ECRIT n'est plus
#: celui que le reglage rend. `coupe.from_segs` arrondit a 0,1 unite, donc la
#: tolerance absorbe l'arrondi et rien d'autre : `courbe` faussee de 0,10
#: deplace des noeuds de plusieurs unites, et le temoin le montre.
TOL_NOEUD = 0.15


def _bras_ecrit_contre_reglage(lay, master, ecart_courbe=0.0):
    """(ecart max de noeud, nombre de noeuds) entre le bras ecrit et le bras
    que `bras_O.construire` rend depuis la base du meme calque.

    Elle prend son objet du PRODUCTEUR et ne le reconstruit pas autrement :
    une verification qui redecouvre sa cible mesure autre chose, et ce projet
    l'a paye au quatorzieme tour sur la coupe oblique.
    """
    base, bras = BR.separer(lay)
    if bras is None:
        return None, 0
    sauv = list(lay.shapes)
    lay.shapes = [s for s in sauv if s is not bras]
    try:
        if ecart_courbe:
            genre, r = Q.reglage_O(master)
            r = dict(r)
            r.pop("_note", None)
            r["courbe"] = r["courbe"] + ecart_courbe
            ep = M.ep_paroi(lay) * r.pop("ep_facteur")
            attendu = Q.bras_ancre(L.paths(lay), epaisseur=ep, **r)
        else:
            attendu, _ep = BR.construire(lay, master)
    finally:
        lay.shapes = sauv
    a = [(float(n.position.x), float(n.position.y)) for n in bras.nodes]
    b = [(float(n.position.x), float(n.position.y)) for n in attendu.nodes]
    if len(a) != len(b):
        return float("inf"), len(a)
    return max(max(abs(p[0] - q[0]), abs(p[1] - q[1]))
               for p, q in zip(a, b)), len(a)


def section5(ecart_courbe=0.0, retirer_bras=False):
    """5. LE BRAS EST-IL SERVI, ET EST-CE CELUI DU REGLAGE.

    Les quatre premieres sections mesurent ce que le REGLAGE rend ; aucune ne
    regarde ce que la source PORTE. Le bras a vecu trente-deux tours dans cet
    etat -- arrete, mesure, et appele par aucun script de production -- et le
    point ouvert 84 n'existait que pour cela.

    Trois volets. Le O romain porte un bras dans ses quatre masters, et c'est
    exactement celui que `bras_O.construire` rend depuis sa base, noeud a
    noeud. Le O italique n'en porte aucun, decision du quarante-septieme tour.
    Et les glyphes qui REDESSINENT un O sous un autre nom n'en portent pas non
    plus : `o` ecarte au dix-neuvieme tour, `o.sc`, `Oslash` et `OE` ecartes au
    quarante-huitieme. Sans ce dernier volet, la place de l'etape dans la
    chaine pourrait changer et faire descendre le bras dans `o.sc` sans qu'une
    ligne du projet le dise.
    """
    print("\n5. le bras SERVI, et les glyphes qui n'en portent pas")
    anomalies = 0
    for chemin, ital in ((SOURCE, False), (SOURCE_ITAL, True)):
        lab = "italique" if ital else "romain"
        if not os.path.exists(chemin):
            print(f"  {lab} : source absente. Ce n'est pas un zero, c'est un "
                  f"NON MESURE.")
            anomalies += 1
            continue
        font = glyphsLib.GSFont(chemin)
        ids = {m.id: m.name for m in font.masters}
        for lay in font.glyphs[BR.PORTEUR].layers:
            mn = ids.get(lay.layerId)
            if mn is None:
                continue
            if retirer_bras:
                _b, br = BR.separer(lay)
                if br is not None:
                    lay.shapes = [s for s in lay.shapes if s is not br]
            attendu_bras = mn not in Q.MASTERS_SANS_BRAS
            ecart, n = _bras_ecrit_contre_reglage(lay, mn, ecart_courbe)
            porte = ecart is not None
            note = ""
            if porte and not attendu_bras:
                note = "  !! un master ECARTE porte un bras"
            elif attendu_bras and not porte:
                note = ("  !! le bras N'EST PAS SERVI : le reglage est ecrit, "
                        "le dessin ne l'a pas")
            elif porte and ecart > TOL_NOEUD:
                note = (f"  !! le bras ecrit s'ecarte de {ecart:.2f}u du "
                        f"reglage")
            print(f"  {lab:<9} {mn:<18} "
                  + (f"bras {n} noeuds, ecart au reglage {ecart:.2f}u"
                     if porte else "pas de bras")
                  + note)
            anomalies += bool(note)
        # Les glyphes qui redessinent un O et n'en portent pas.
        sans = []
        for nom in sorted(BR.GLYPHES_SANS_BRAS):
            g = font.glyphs[nom]
            if g is None:
                continue
            for lay in g.layers:
                mn = ids.get(lay.layerId)
                if mn is None:
                    continue
                try:
                    _b, br = BR.separer(lay)
                except ValueError:
                    br = True
                if br is not None:
                    sans.append(f"{nom} {mn}")
        print(f"  {lab:<9} {len(BR.GLYPHES_SANS_BRAS)} glyphe(s) ecarte(s) "
              f"nommes, "
              + ("aucun ne porte de contour greffe"
                 if not sans else f"!! {' '.join(sans)}"))
        anomalies += len(sans)
    return anomalies


def section6(fausser=None):
    """6. QUELS GLYPHES PORTENT UN CONTOUR GREFFE, sur tout le repertoire.

    QUARANTE-NEUVIEME TOUR, point ouvert 85. Les cinq sections precedentes
    regardent le O et les quatre noms qui le redessinent ; aucune ne balaie le
    repertoire. Le point 85 en tirait qu'un seul glyphe porte un contour
    greffe, "le O seul aujourd'hui", et que le defaut du peintre "attend le
    prochain". MESURE : il y en a TROIS. `copyright` et `registered` en portent
    un dans les huit masters des DEUX sources, ils viennent d'Atkinson, et le
    projet ne les a jamais touches -- le C du © et le R du ® sont des contours
    positifs poses dans l'anneau, ce qui est la geometrie exacte du bras.

    CE QUE LA SECTION GARDE, et c'est la raison qu'elle existe : le jour ou un
    glyphe gagne ou perd un contour greffe, elle le dit. Sans elle, le prochain
    greffon arriverait dans un projet dont vingt-neuf peintres l'effacaient, et
    la liste de `dessin.PORTEURS_GREFFE` serait une table qui diverge en
    silence -- ce que ce projet a deja paye sur `FAMILLES_O`.

    ELLE NE RECONSTRUIT RIEN. Elle lit les contours tels que la source les
    porte et les passe a `dessin.classer`, qui est le classement que les
    peintres emploient : elle mesure donc le meme objet qu'eux, et non une
    reconstitution qui resterait juste sur une source fausse.

    TEMOIN : `fausser` nomme un glyphe dont on retire le contour greffe en
    memoire ; la section doit alors signaler un porteur manquant.
    """
    print("\n6. les porteurs de contour greffe, sur tout le repertoire")
    anomalies = 0
    attendu = D.PORTEURS_GREFFE
    for chemin, ital in ((SOURCE, False), (SOURCE_ITAL, True)):
        lab = "italique" if ital else "romain"
        if not os.path.exists(chemin):
            print(f"  {lab} : source absente. Ce n'est pas un zero, c'est un "
                  f"NON MESURE.")
            anomalies += 1
            continue
        font = glyphsLib.GSFont(chemin)
        ids = {m.id for m in font.masters}
        trouve = {}
        for g in font.glyphs:
            for lay in g.layers:
                if lay.layerId not in ids:
                    continue
                cs = [D.flatten(p) for p in lay.paths]
                if fausser == g.name and cs:
                    niv = D.profondeurs(cs)
                    cs = [c for c, d in zip(cs, niv)
                          if not (d >= 1 and D.aire(c) >= 0)]
                if len(cs) < 2:
                    continue
                niv = D.profondeurs(cs)
                gr = [c for c, d in zip(cs, niv)
                      if d >= 1 and D.aire(c) >= 0]
                if gr:
                    trouve.setdefault(g.name, 0)
                    trouve[g.name] += len(gr)
        # Un nom attendu dont les masters sont "romains" ne l'est pas ici.
        vises = {n for n, d in attendu.items()
                 if d["masters"] == "tous" or not ital}
        manquants = sorted(vises - set(trouve))
        surnums = sorted(set(trouve) - set(attendu))
        print(f"  {lab:<9} {len(trouve)} nom(s) porteur(s), "
              f"{sum(trouve.values())} glyphe-calque(s) : "
              + " ".join(f"{n}x{trouve[n]}" for n in sorted(trouve)))
        if manquants:
            print(f"  {lab:<9} !! attendu et ABSENT : {' '.join(manquants)}")
        if surnums:
            print(f"  {lab:<9} !! porteur NON DECLARE dans "
                  f"dessin.PORTEURS_GREFFE : {' '.join(surnums)}")
        anomalies += len(manquants) + len(surnums)
    return anomalies


def main(temoin=False):
    if not os.path.exists(SOURCE):
        print(f"!! source absente : {SOURCE}")
        print("   Ce n'est pas un zero, c'est un NON MESURE.")
        return 1
    font = glyphsLib.GSFont(SOURCE)
    mid = {m.name: m.id for m in font.masters}
    if temoin:
        print("TEMOIN : `courbe` faussee de +0,10. La section 1 doit signaler "
              "les quatre masters.")
        n = section1(font, mid, ecart_courbe=0.10)
        print(f"\nTEMOIN : {n} ecart(s) sur 16 mesures — "
              + ("le controle sait signaler" if n else
                 "IL NE DISCRIMINE PLUS"))
        # LE TEMOIN DE LA SECTION 5, EN DEUX VOLETS, parce qu'elle pose deux
        # questions et qu'un temoin qui n'en exerce qu'une laisserait l'autre
        # sans preuve. Volet A : le bras est RETIRE en memoire, et la section
        # doit dire qu'il n'est pas servi -- c'est exactement l'etat que le
        # point ouvert 84 decrivait. Volet B : `courbe` faussee de 0,10, donc
        # le bras est bien servi mais ce n'est plus celui du reglage.
        print("\nTEMOIN section 5, volet A : le bras retire en memoire.")
        a = section5(retirer_bras=True)
        print(f"  -> {a} anomalie(s) — "
              + ("elle voit un bras absent" if a else "ELLE NE LE VOIT PAS"))
        print("\nTEMOIN section 5, volet B : `courbe` faussee de +0,10.")
        b = section5(ecart_courbe=0.10)
        print(f"  -> {b} anomalie(s) — "
              + ("elle voit un bras qui n'est plus celui du reglage" if b
                 else "ELLE NE LE VOIT PAS"))
        # LE TEMOIN DE LA SECTION 6. Le contour greffe du © est retire en
        # memoire dans les deux sources : la section doit signaler un porteur
        # attendu et absent, dans les deux. Le © plutot que le O parce qu'il
        # est le seul porteur present dans les HUIT masters, donc le seul qui
        # exerce les deux branches du filtre `masters`.
        print("\nTEMOIN section 6 : le greffon du © retire en memoire.")
        c = section6(fausser="copyright")
        print(f"  -> {c} anomalie(s) — "
              + ("elle voit un porteur qui a perdu son greffon" if c >= 2
                 else "ELLE NE LE VOIT PAS DANS LES DEUX SOURCES"))
        return 0
    total = (section1(font, mid) + section2(font, mid) + section3()
             + section4() + section5() + section6())
    print(f"\nTOTAL : {total} anomalie(s)."
          + ("" if total else "  Le bras ecrit est celui qui a ete valide."))
    return total


if __name__ == "__main__":
    sys.exit(1 if main("--temoin" in sys.argv) else 0)
