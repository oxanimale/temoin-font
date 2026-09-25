#!/usr/bin/env python3
"""Controle du crenage des petites capitales et du blanc devant l'Æ.

Point 93, cinquante-cinquieme tour. Il lit l'ETAT ECRIT, `Temoin.glyphs` et
`Temoin-Italic.glyphs`, et remesure tout ce que `crenage_sc` et
`approches.REGLAGE_AE` prétendent avoir fait.

**Il fallait un controle autonome, et la raison est mesuree.** Aucun garde-fou
du projet ne voit ce geste : `check_approches` surveille le voisinage du F, les
trois tables de paires ne contiennent aucune petite capitale, et les deux
generateurs qui reconstruisent leur etat ne les regardent pas davantage. Au
cinquante-quatrieme tour, `inventaire_F` a rendu un zero-diff exact sur 383
paires pendant que `check_approches` criait douze fois : un controle qui ne
regarde pas rend zero comme un controle qui va bien.

Sept sections :

  1. les 44 `.sc` portent le groupe prefixe de leur capitale, et aucune classe
     n'est partagee entre les deux casses ;
  2. le crenage `.sc` est l'IMAGE EXACTE du crenage capitale au rapport, dans
     les deux sens -- rien ne manque, rien n'est orphelin ;
  3. les bornes de `BORNES_SC` valent ce qu'elles annoncent ;
  4. aucune paire `.sc` ne passe sous le plancher de jour, gouttiere pleine ;
  5. le reglage de l'Æ atteint la cible, ou la borne quand elle mord ;
  6. aucune paire de la famille de l'Æ n'est reprise par une autre table ;
  7. les `.sc` portent bien `APPROCHE_SC` de chaque cote, mesure en DELTA contre
     la meme derivation sans approche.

**Deux sections ont ete refaites au cinquante-sixieme tour**, et les deux
mesuraient autre chose que ce qu'elles annoncaient : la 2 comparait une
resolution a une resolution, donc elle rendait zero sur l'etat que le point 97
decrit ; la 7 mesurait une approche sur la boite englobante, donc elle comptait
l'inclinaison italique et rendait 142 anomalies sur un etat juste.

    python3 check_crenage_sc.py [--temoin]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import glyphsLib

import approches as A
import crenage_sc as CS
import dessin as D
import lot3
import make_temoin as MT

ICI = os.path.dirname(os.path.abspath(__file__))
SOURCES = [("roman", os.path.join(ICI, "Temoin.glyphs")),
           ("italic", os.path.join(ICI, "Temoin-Italic.glyphs"))]

#: LES DEUX HAUTEURS SE LISENT CHEZ `make_temoin`, JAMAIS ICI. Un premier jet
#: les recopiait, et c'est exactement le defaut que le docstring de
#: `crenage_sc` venait de nommer a propos du rapport : deux definitions du meme
#: nombre finissent par vivre dans deux fichiers, et le projet l'a paye sur
#: `quadrant`. Le jour ou la hauteur des petites capitales changerait, les
#: sections 2, 3 et 5 auraient valide contre un rapport perime, en silence,
#: puisqu'elles se comparent a leur propre copie. La section 7 lisait deja `MT`.
HAUTEUR_SC = MT.HAUTEUR_SC
HAUTEUR_CAP = MT.HAUTEUR_CAP
RAPPORT = HAUTEUR_SC / HAUTEUR_CAP

#: La bande sur laquelle le blanc devant l'Æ a ete juge, et celle du plancher.
#: Deux bandes pour deux questions : le blanc moyen se lit sur la hauteur de la
#: lettre, le plancher se mesure sur la bande pleine. Les confondre a deja coute
#: un defaut servi au vingt-quatrieme tour.
BANDE_CAP = (0.0, HAUTEUR_CAP)
BANDE_SC = (0.0, HAUTEUR_SC)
#: `inventaire_ae.BANDE_CAP` doit valoir la meme chose : le producteur et son
#: controle qui mesurent sur deux bandes differentes rendraient deux verdicts
#: justes sur deux objets. Les deux la lisent maintenant chez `make_temoin`.

TOL = 0.55     # l'arrondi de `crenage_sc`, a la dixieme d'unite, plus la marge

#: La section 2 compare une image a son antecedent multiplie par le rapport et
#: arrondi de la MEME facon : c'est une identite arithmetique, pas une mesure de
#: forme, et sa tolerance doit donc etre celle du dernier chiffre. Une tolerance
#: large y laisserait passer un ecart reel.
TOL_IMAGE = 0.05


def _paires_sc(font):
    return CS.jeu(font)


def _boite(lay):
    """(xMin, xMax) d'un calque, quelle que soit la forme que glyphsLib rend.

    Selon la version, `bounds` vaut ((x, y), (largeur, hauteur)) ou
    (x, y, largeur, hauteur). Le controle accepte les deux plutot que de
    dependre de l'une, et leve si c'est une troisieme forme.
    """
    bb = lay.bounds
    if bb is None:
        return None
    if len(bb) == 2:
        (x0, _y0), (larg, _haut) = bb
    elif len(bb) == 4:
        x0, _y0, larg, _haut = bb
    else:
        raise ValueError("forme de bounds inconnue : %r" % (bb,))
    return (float(x0), float(x0) + float(larg))


def _cle_sc(cle):
    """La cle appartient-elle a l'espace des petites capitales.

    Un nom de glyphe `.sc` se reconnait a son suffixe, un nom de classe au
    prefixe que `crenage_sc` pose. Mesure au cinquante-sixieme tour : aucune
    classe de capitale ne s'appelle `sc...`, donc le test ne peut pas confondre
    les deux casses.
    """
    if cle.startswith("@MMK_L_") or cle.startswith("@MMK_R_"):
        return cle[7:].startswith(CS.PREFIXE)
    return cle.endswith(".sc")


def _caps_servies(font):
    """Les capitales du repertoire, par la CASSE DU CARACTERE et non du nom.

    Un nom de glyphe n'est pas une propriete typographique : classer sur
    `nom[:1].isupper()` rangerait `AE` avec les capitales et `germandbls` avec
    les bas de casse, et le projet l'a paye au trente-huitieme tour.
    """
    out = []
    for g in font.glyphs:
        if not g.unicode:
            continue
        try:
            ch = chr(int(g.unicode, 16))
        except ValueError:
            continue
        if ch.isalpha() and ch.isupper() and ch.upper() == ch and len(ch) == 1:
            out.append(g.name)
    return sorted(out)


# ------------------------------------------------------------------ section 1

def section1(font, nom_src, dire):
    anomalies = 0
    groupes_sc_d, groupes_sc_g = set(), set()
    groupes_cap_d, groupes_cap_g = set(), set()
    for nom, cap in _paires_sc(font):
        g, c = font.glyphs[nom], font.glyphs[cap]
        attendu_d = (CS.PREFIXE + c.rightKerningGroup) if c.rightKerningGroup else None
        attendu_g = (CS.PREFIXE + c.leftKerningGroup) if c.leftKerningGroup else None
        if g.rightKerningGroup != attendu_d or g.leftKerningGroup != attendu_g:
            anomalies += 1
            dire("   %s : groupes (%s, %s), attendus (%s, %s)"
                 % (nom, g.rightKerningGroup, g.leftKerningGroup,
                    attendu_d, attendu_g))
        if attendu_d:
            groupes_sc_d.add(attendu_d)
        if attendu_g:
            groupes_sc_g.add(attendu_g)
    for n in _caps_servies(font):
        c = font.glyphs[n]
        if c.rightKerningGroup:
            groupes_cap_d.add(c.rightKerningGroup)
        if c.leftKerningGroup:
            groupes_cap_g.add(c.leftKerningGroup)
    partages = (groupes_sc_d & groupes_cap_d) | (groupes_sc_g & groupes_cap_g)
    if partages:
        anomalies += 1
        dire("   classes PARTAGEES entre les deux casses : %s"
             % ", ".join(sorted(partages)))
    dire("1. groupes des .sc        %d glyphes, %d cles droites, %d gauches, "
         "0 partagee" % (len(_paires_sc(font)), len(groupes_sc_d),
                         len(groupes_sc_g)) if not anomalies else
         "1. groupes des .sc        %d ANOMALIES" % anomalies)
    return anomalies


# ------------------------------------------------------------------ section 2

def section2(font, nom_src, dire):
    """Le crenage des `.sc` est l'IMAGE EXACTE du crenage capitale, au rapport.

    **Elle mesure DEUX SENS, et il en faut deux.** Que chaque entree capitale
    mappable ait son image a la bonne valeur ; et qu'aucune entree `.sc` n'ait
    d'antecedent. Le premier sens seul aurait laisse passer le defaut du point 97
    -- une valeur `.sc` que rien dans la table capitale ne justifie, parce
    qu'elle venait d'une EXCEPTION lue et posee sur un GROUPE. Le second seul
    laisserait passer un oubli. Le premier jet de cette section comparait
    `A.kern(cap_a, cap_b)` a `A.kern(sc_a, sc_b)`, donc resolution contre
    resolution : il rendait zero sur l'etat fautif, les deux cotes resolvant
    vers la meme valeur propagee. Un controle qui refait le geste au lieu de
    lire sa trace ne peut pas voir une erreur de CLE.
    """
    caps, gd, gg = CS.classes(font)
    anomalies = attendues = ecrites = 0
    for m in font.masters:
        K = font.kerning.get(m.id, {})
        bornees = set(CS.BORNES_SC.get(m.name, {}))
        attendu = {}
        for k1, sous in K.items():
            if _cle_sc(k1):
                continue
            for k2, v in sous.items():
                if _cle_sc(k2):
                    continue
                i1 = CS.image_cle(k1, "droite", caps, gd, gg)
                i2 = CS.image_cle(k2, "gauche", caps, gd, gg)
                if i1 is not None and i2 is not None:
                    attendu[(i1, i2)] = round(float(v) * RAPPORT, 1)
        # sens 1 : rien ne manque, rien ne derape
        for (i1, i2), val in sorted(attendu.items()):
            attendues += 1
            if (i1, i2) in bornees:
                continue          # la section 3 les mesure avec leur borne
            ici = K.get(i1, {}).get(i2)
            if ici is None or abs(float(ici) - val) > TOL_IMAGE:
                anomalies += 1
                if anomalies <= 6:
                    dire("   %s %s+%s : %s pour %.1f" % (m.name, i1, i2, ici,
                                                         val))
        # sens 2 : aucune entree .sc sans antecedent capitale
        for k1, sous in K.items():
            if not _cle_sc(k1):
                continue
            for k2 in sous:
                ecrites += 1
                if (k1, k2) not in attendu and (k1, k2) not in bornees:
                    anomalies += 1
                    if anomalies <= 12:
                        dire("   %s %s+%s : ORPHELINE, aucune cle capitale ne "
                             "lui correspond" % (m.name, k1, k2))
    dire("2. image de la capitale   %d entrees attendues, %d ecrites, "
         "%d anomalies" % (attendues, ecrites, anomalies))
    return anomalies


# ------------------------------------------------------------------ section 3

def section3(font, nom_src, dire):
    anomalies = vues = 0
    for m in font.masters:
        for (a, b), rendu in sorted(CS.BORNES_SC.get(m.name, {}).items()):
            if font.glyphs[a] is None or font.glyphs[b] is None:
                continue
            cap_a = dict(_paires_sc(font))[a]
            cap_b = dict(_paires_sc(font))[b]
            base = A.kern(font, m.id, cap_a, cap_b)
            attendu = round(round(base * RAPPORT, 1) + rendu, 1)
            ici = A.kern(font, m.id, a, b)
            vues += 1
            if abs((ici or 0.0) - attendu) > TOL:
                anomalies += 1
                dire("   %s %s+%s borne : %s pour %.1f" % (m.name, a, b, ici,
                                                           attendu))
    dire("3. bornes du plancher     %d paire-masters, %d anomalies"
         % (vues, anomalies))
    return anomalies


# ------------------------------------------------------------------ section 4

def section4(font, nom_src, dire):
    anomalies = vues = 0
    pire = (1e9, None, None)
    paires = _paires_sc(font)
    for m in font.masters:
        src = D.Source(font, m.name)
        for nom_a, _ in paires:
            for nom_b, _ in paires:
                k = A.kern(font, m.id, nom_a, nom_b) or 0.0
                if not k:
                    continue
                g = A.couloir_plein(src, nom_a, nom_b, k)
                if g is None:
                    continue
                vues += 1
                if g < pire[0]:
                    pire = (g, "%s+%s" % (nom_a, nom_b), m.name)
                if g < A.JOUR_MIN:
                    anomalies += 1
                    if anomalies <= 6:
                        dire("   %s %s+%s : couloir %.1f pour un plancher de "
                             "%.1f" % (m.name, nom_a, nom_b, g, A.JOUR_MIN))
    dire("4. plancher de jour       %d paire-masters crenes, %d sous le "
         "plancher, la plus serree %s %s a %.1f"
         % (vues, anomalies, pire[1], pire[2], pire[0]))
    return anomalies


# ------------------------------------------------------------------ section 5

def section5(font, nom_src, dire):
    """Le reglage de l'Æ atteint la cible, ou la borne quand elle mord.

    La reference n'est PAS la source amont : le blanc devant l'Æ porte deja les
    gestes du projet. Elle est l'etat ECRIT prive du seul reglage, obtenu en
    retirant le deplacement. C'est la forme que `check_barre_F` a retenue au
    cinquante-quatrieme tour, et pour la meme raison.
    """
    anomalies = vues = 0
    if font.glyphs[A.GLYPHE_AE] is None:
        dire("5. reglage de l'AE        AE absent : NON MESURE")
        return 1
    for m in font.masters:
        table = A.REGLAGE_AE.get(m.name, {})
        if not table:
            anomalies += 1
            dire("   %s : aucun reglage AE, table incomplete" % m.name)
            continue
        src = D.Source(font, m.name)
        blancs = {}
        for n in _caps_servies(font):
            k = A.kern(font, m.id, n, A.GLYPHE_AE) or 0.0
            _, b = A.inter_lettre(src, n, A.GLYPHE_AE, k, *BANDE_CAP)
            if b is not None:
                blancs[n] = b
        if "C" not in blancs:
            anomalies += 1
            dire("   %s : C absent, cible non calculable" % m.name)
            continue
        cible = blancs["C"]
        for n, delta in sorted(table.items()):
            if n not in blancs:
                anomalies += 1
                dire("   %s : %s dans la table et pas dans le repertoire"
                     % (m.name, n))
                continue
            vues += 1
            ecart = blancs[n] - cible
            # elle atteint la cible, ou elle est bornee par le plancher
            k = A.kern(font, m.id, n, A.GLYPHE_AE) or 0.0
            g = A.couloir_plein(src, n, A.GLYPHE_AE, k)
            borne = g is not None and abs(g - A.JOUR_MIN) <= A.SEUIL_AE
            if abs(ecart) > A.SEUIL_AE and not borne:
                anomalies += 1
                if anomalies <= 8:
                    dire("   %s %s+AE : blanc %.1f, cible %.1f, ecart %+.1f, "
                         "couloir %.1f -- ni a la cible ni a la borne"
                         % (m.name, n, blancs[n], cible, ecart,
                            g if g is not None else float("nan")))
        # aucune capitale hors table ne doit depasser la cible, SAUF celles que
        # le producteur a mesurees hors de portee -- gouttiere deja sous le
        # plancher, donc aucune unite a fermer. Un nom decide et un nom jamais
        # regarde sont identiques dans une table : la troisieme categorie est
        # ecrite, et le controle la remesure au lieu de la croire.
        hors = A.HORS_PORTEE_AE.get(m.name, {})
        for n, b in blancs.items():
            if n in table or n == "C":
                continue
            if b <= cible + A.SEUIL_AE:
                continue
            if n in hors:
                k = A.kern(font, m.id, n, A.GLYPHE_AE) or 0.0
                g = A.couloir_plein(src, n, A.GLYPHE_AE, k)
                if g is None or g > A.JOUR_MIN:
                    anomalies += 1
                    if anomalies <= 8:
                        dire("   %s %s+AE : dit hors de portee, gouttiere %s "
                             "pour un plancher de %.1f -- il pourrait se "
                             "refermer" % (m.name, n, g, A.JOUR_MIN))
                continue
            anomalies += 1
            if anomalies <= 8:
                dire("   %s %s+AE : blanc %.1f au-dessus de la cible %.1f "
                     "et HORS TABLE" % (m.name, n, b, cible))
    dire("5. reglage de l'AE        %d glyphe-masters, %d anomalies"
         % (vues, anomalies))
    return anomalies


# ------------------------------------------------------------------ section 6

def section6(font, nom_src, dire):
    """Aucune paire de la famille de l'Æ n'est reprise par une autre table.

    Deux tables qui ecrivent en valeur TOTALE sur la meme paire, la seconde
    ecrase la premiere : le cinquante-quatrieme tour a failli perdre vingt
    unites sur `F+c` ainsi, et le controle qui l'a vu n'existait pas.
    """
    anomalies = 0
    familles = set()
    for m in font.masters:
        familles |= {(n, A.GLYPHE_AE) for n in A.REGLAGE_AE.get(m.name, {})}
    for m in font.masters:
        for a, b, _v in A.PAIRES_PIEDS.get(m.name, ()):
            if (a, b) in familles:
                anomalies += 1
                dire("   %s : paires_pieds reprend %s+%s" % (m.name, a, b))
        for a, b, _v in A.PAIRES_BOUTS.get(m.name, ()):
            if (a, b) in familles:
                anomalies += 1
                dire("   %s : paires_bouts reprend %s+%s" % (m.name, a, b))
        for voisin in A.PAIRES_F.get(m.name, {}):
            if ("F", voisin) in familles:
                anomalies += 1
                dire("   %s : paires_F reprend F+%s" % (m.name, voisin))
    dire("6. conflits de tables     %d familles, %d anomalies"
         % (len(familles), anomalies))
    return anomalies


# ------------------------------------------------------------------ section 7

def section7(font, nom_src, dire):
    """Les 28 unites d'approche des `.sc` sont bien celles d'`APPROCHE_SC`.

    **REFAITE au cinquante-sixieme tour, parce qu'elle mesurait autre chose.**
    Le premier jet comparait `xMin` et `chasse - xMax` a `APPROCHE_SC` : une
    boite englobante d'italique prend son `xMin` en bas et son `xMax` en haut,
    donc elle compte l'inclinaison, et la section rendait **142 anomalies sur un
    etat juste**. Un controle qui crie a tort sur un etat juste vaut moins que
    pas de controle : il apprend a ignorer sa propre sortie.

    Ce qu'il fallait mesurer est un DELTA, et non une valeur absolue. `lot3` pose
    `width = round(w * kx + 2*sb, 1)` et `x' = round(x * kx + sb, 1)`, ou `w` est
    la chasse de la capitale INTERPOLEE a une coordonnee d'axe deduite de la
    graisse : la valeur absolue n'est pas reconstructible sans recopier la
    formule qu'on verifie, et le projet l'a paye sur l'heritage de l'approche par
    `f.sc` au vingt-troisieme tour. Le delta, lui, ne depend ni de `kx` ni de
    l'interpolation ni de l'inclinaison : la section redemande a `lot3` la MEME
    petite capitale avec `sb = 0`, et l'ecart des deux doit valoir `APPROCHE_SC`
    d'un cote et le double sur la chasse. Elle prend donc son objet du
    producteur, au lieu de le reconstruire.

    Une reserve mesuree : `bras_O` passe APRES `lot3`, donc `o.sc` a ete derive
    d'un O sans bras quand la section le redemande a un O qui en porte un. Le
    bras est un contour greffe dans la contreforme, dont la boite est
    strictement interieure a celle du glyphe : ni `xMin`, ni `xMax`, ni la
    chasse ne bougent. Si cela cessait d'etre vrai, c'est le `o.sc` romain qui
    sortirait, et ce serait un fait a connaitre plutot qu'un faux positif.
    """
    anomalies = vues = 0
    ids = [m.id for m in font.masters]
    cache = lot3.mesures(font)
    for m in font.masters:
        for nom, cap in _paires_sc(font):
            lay = font.glyphs[nom].layers[m.id]
            if lay is None:
                continue
            nue = lot3.petite_capitale(font, cap, m.id, MT.HAUTEUR_SC,
                                       MT.LARGEUR_SC, 0.0, None, True, cache,
                                       ids[1], True)
            b1, b2 = _boite(lay), _boite(nue)
            if b1 is None or b2 is None:
                continue
            vues += 1
            d_gauche = b1[0] - b2[0]
            d_chasse = lay.width - nue.width
            if (abs(d_gauche - MT.APPROCHE_SC) > 0.55
                    or abs(d_chasse - 2 * MT.APPROCHE_SC) > 1.05):
                anomalies += 1
                if anomalies <= 6:
                    dire("   %s %s : +%.1f a gauche et +%.1f de chasse, pour "
                         "%.1f et %.1f" % (m.name, nom, d_gauche, d_chasse,
                                           MT.APPROCHE_SC, 2 * MT.APPROCHE_SC))
    dire("7. approche des .sc       %d glyphe-masters, APPROCHE_SC = %.1f, "
         "%d anomalies" % (vues, MT.APPROCHE_SC, anomalies))
    return anomalies


SECTIONS = [section1, section2, section3, section4, section5, section6,
            section7]


def main():
    temoin = "--temoin" in sys.argv
    total = 0
    for nom_src, chemin in SOURCES:
        if not os.path.exists(chemin):
            print("!! source absente : %s -- NON MESURE" % chemin)
            return 1
        font = glyphsLib.GSFont(chemin)
        if temoin:
            # LE TEMOIN agit sur ce que le controle MESURE, pas sur ce qui l'a
            # produit : une valeur de crenage faussee, un groupe retire, un
            # reglage de l'AE annule. Un temoin qui imite le test ne prouve
            # rien.
            # CHAQUE SECTION A SON PROPRE DECLENCHEUR, et il le faut : une
            # section qu'aucun temoin n'exerce se lit comme une section qui
            # passe, et le projet a paye deux temoins muets -- celui de
            # `check_approches` au trente-et-unieme tour, celui de `check_page`
            # au cinquante-et-unieme. Le premier jet de ce temoin-ci n'exercait
            # que les sections 1, 2, 5 et 7.
            for m in font.masters:
                # 2 : une entree .sc qu'aucune cle capitale ne justifie -- la
                #     forme exacte du defaut du point 97 ;
                # 4 : et elle ferme assez pour passer sous le plancher.
                A.ecrire_kern(font, m.id, "k.sc", "o.sc", -300.0,
                              exception=True)
                # 3 : la borne rendue a zero, donc elle ne rend plus rien.
                for (a, b) in CS.BORNES_SC.get(m.name, {}):
                    A.ecrire_kern(font, m.id, a, b, 0.0, exception=True)
                # 5 : le reglage de l'AE annule sur le L.
                A.ecrire_kern(font, m.id, "L", A.GLYPHE_AE, 0.0, exception=True)
                # 6 : une seconde table qui reprend une paire de la famille.
                A.PAIRES_PIEDS.setdefault(m.name, []).append(
                    ("L", A.GLYPHE_AE, +1))
                # 7 : l'approche laterale deplacee de cinq unites, le seuil
                #     valant un demi.
                lay = font.glyphs["a.sc"].layers[m.id]
                for p in lay.paths:
                    for nd in p.nodes:
                        nd.position = (nd.position.x + 5.0, nd.position.y)
            # 1 : une classe retiree a une petite capitale.
            font.glyphs["c.sc"].rightKerningGroup = None
        print("=== %s%s" % (nom_src, "   TEMOIN" if temoin else ""))
        lignes = []
        n = 0
        muettes = []
        for s in SECTIONS:
            k = s(font, nom_src, lignes.append)
            if temoin and not k:
                muettes.append(s.__name__)
            n += k
        for l in lignes:
            print(l)
        # UN TEMOIN SE LIT SECTION PAR SECTION, jamais sur un total : une
        # section muette disparait derriere les autres, et c'est exactement
        # ainsi que le premier jet de ce temoin a laisse quatre sections sans
        # objet sans que rien ne le dise.
        if temoin:
            print("   sections MUETTES sous le temoin : %s"
                  % (", ".join(muettes) if muettes else "aucune"))
        total += n
    mot = "TEMOIN" if temoin else "TOTAL"
    print("%s : %d anomalies sur %d sections et deux sources"
          % (mot, total, len(SECTIONS)))
    # Le code de sortie d'un temoin est inverse a dessein : un temoin qui ne
    # trouve rien est un echec du controle, pas un succes de la police.
    if temoin:
        return 0 if total else 1
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
