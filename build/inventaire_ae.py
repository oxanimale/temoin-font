#!/usr/bin/env python3
"""Le producteur de `reglage_ae.py` : le blanc devant l'Æ en capitales.

Point 93, tranche par Nicolas au cinquante-cinquieme tour -- la famille de l'Æ
traitee entiere, chacune a sa valeur pour atteindre la cible, BORNEE PAR LE
PLANCHER DE JOUR. Ecrit a la main ce tour-la ; ce producteur est la seconde
reprise du point 97, au cinquante-sixieme.

**POURQUOI UN PRODUCTEUR, ET PAS UNE TABLE ECRITE A LA MAIN.** La famille avait
ete relevee sur les 58 capitales du BINAIRE servi. La source en porte davantage,
et la section 5 de `check_crenage_sc` a trouve huit noms qui depassent la cible
sans etre dans la table : `Cacute`, `Ccaron`, `Cdotaccent`, `Ecaron`,
`Edotaccent`, `Emacron`, `Eogonek`, `Lacute`. Le perimetre d'une MESURE et celui
d'une TABLE ne coincident pas d'eux-memes, et une liste ecrite a la main se
perime sans que rien ne le dise -- `check_approches.VOISINS_F` oubliait
vingt-neuf accentuees depuis vingt-trois tours, et le projet l'a paye au
cinquante-quatrieme.

**CE QUI EST MESURE, ET OU.** La chaine reelle, `make_temoin.process`, relancee
sous `TEMOIN_SANS_APPROCHES=1` : elle rend le DESSIN servi avec le crenage
d'Atkinson, donc l'etat d'avant le reglage. Reconstruire les etapes ici serait
la faute que `inventaire_pieds` et `inventaire_bouts` ont chacun payee une fois
-- un generateur qui rejoue la chaine lui-meme cesse de decrire le livrable le
jour ou elle gagne une etape.

**LE CALCUL EST EXACT, PAS ITERATIF, et c'est une propriete de la mesure.**
`inter_lettre` compose `w = chasse(a) + k` et retranche le profil : le blanc
moyen comme la gouttiere sont donc AFFINES en `k`, de pente 1. Le deplacement
qui amene le blanc a la cible vaut `cible - blanc`, et celui que le plancher
permet vaut `JOUR_MIN - gouttiere`. Aucune dichotomie, aucun balayage.

**L'ARRONDI VA VERS ZERO**, `math.ceil` sur des valeurs negatives, comme la
table des bouts et pour la meme raison : la contrainte qui mord est un plancher
a ne pas franchir, donc arrondir vers le bas referait le defaut que la borne
interdit. Le prix est au plus une unite de blanc en trop, quand la tolerance de
`check_crenage_sc` en vaut 1,5.

**DES DEPLACEMENTS ET NON UNE CIBLE RECALCULEE A LA COMPILATION.** La table
porte un delta par nom et par master ; `approches.appliquer` l'ajoute au crenage
lu. Une cible absolue corrigerait en silence un ecart que personne n'a mesure,
et le garde-fou de `barre_mediane` a leve exactement la-dessus au
cinquante-quatrieme tour.

    python3 inventaire_ae.py [roman|italic] [--ecrire] [--temoin]
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import glyphsLib

import approches as A
import dessin as D
import make_temoin as M
from check_approches import AMONT, MASTERS, mid

ICI = os.path.dirname(os.path.abspath(__file__))
SERVI = {
    "roman": os.path.join(ICI, "Temoin.glyphs"),
    "italic": os.path.join(ICI, "Temoin-Italic.glyphs"),
}

#: La bande sur laquelle le blanc se juge : la hauteur de capitale entiere. Le
#: plancher, lui, se mesure sur la bande pleine par `couloir_plein`. Deux bandes
#: pour deux questions, et les confondre a deja coute un defaut servi au
#: vingt-quatrieme tour.
#:
#: La hauteur se LIT chez `make_temoin` et ne se recopie pas. Mesure : les huit
#: masters des deux sources portent `capHeight` 668, donc un nombre unique est
#: juste aujourd'hui -- et c'est precisement le cas ou une copie se perime sans
#: bruit.
BANDE_CAP = (0.0, M.HAUTEUR_CAP)

#: Le nom du glyphe temoin, et le deplacement que `--temoin` lui pose. Il doit
#: etre HORS de la famille dans tous les masters, faute de quoi le temoin ne
#: prouverait rien.
TEMOIN_NOM = "T"
TEMOIN_K = 100.0


def capitales(font):
    """Les capitales de la SOURCE, par la casse du CARACTERE et non du nom.

    Un nom de glyphe n'est pas une propriete typographique : classer sur
    `nom[:1].isupper()` rangerait `AE` avec les capitales et `germandbls` avec
    les bas de casse. C'est la meme lecture que `check_crenage_sc._caps_servies`,
    et les deux doivent rester d'accord -- deux codes qui parlent du meme
    perimetre doivent lire la meme regle.
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


DRAPEAU = "TEMOIN_SANS_REGLAGE_AE"


def source_sans_reglage(cle_src, dossier):
    """La chaine reelle, sautant la SEULE etape 1ter. Rend le chemin ecrit.

    Pas `TEMOIN_SANS_APPROCHES`, qui saute l'etape entiere : le blanc devant
    l'Æ doit se mesurer la ou la decision se prend, donc avec la table du F et
    les autres reglages deja ecrits. Le premier jet de ce producteur employait
    l'autre drapeau, et `F+Æ` entrait dans la famille a -3 unites alors que
    `paires_F` lui donne deja -202 -- deux tables qui ecrivent en valeur totale
    sur la meme paire, ce que la section 6 de `check_crenage_sc` interdit.
    """
    entree = AMONT[cle_src]
    if not os.path.exists(entree):
        return None
    sortie = os.path.join(dossier, "Temoin.glyphs" if cle_src == "roman"
                          else "Temoin-Italic.glyphs")
    avant = os.environ.get(DRAPEAU)
    os.environ[DRAPEAU] = "1"
    try:
        M.process(entree, sortie)
    finally:
        if avant is None:
            os.environ.pop(DRAPEAU, None)
        else:
            os.environ[DRAPEAU] = avant
    return sortie


def temoin_du_dessin(font, cle_src, noms, verbeux=True):
    """Le RECONSTRUIT compare au SERVI, sur ce que la table regarde.

    La regle du projet pour un generateur qui reconstruit son etat. Les
    approches ne touchent plus aucune chasse depuis le vingt-quatrieme tour ni
    aucun contour : la seule chose qui doit differer est le CRENAGE. Un ecart de
    boite ou de chasse sur une capitale de la famille voudrait dire que le blanc
    est mesure sur un autre dessin que le servi, et toute la table serait posee a
    cote. Zero est un fait, pas un silence.
    """
    chemin = SERVI[cle_src]
    if not os.path.exists(chemin):
        if verbeux:
            print("  %s absent : le temoin du dessin est NON MESURE." % chemin)
        return None
    servi = glyphsLib.GSFont(chemin)
    ecarts = 0
    for mn in MASTERS[cle_src]:
        sr, ss = D.Source(font, mn), D.Source(servi, mn)
        for nom in noms:
            if font.glyphs[nom] is None or servi.glyphs[nom] is None:
                continue
            if abs(sr.width(nom) - ss.width(nom)) > 0.05:
                ecarts += 1
                if verbeux and ecarts <= 6:
                    print("  %s %s : chasse %.1f contre %.1f"
                          % (mn, nom, sr.width(nom), ss.width(nom)))
                continue
            br = [p for c in sr.contours(nom) for p in c]
            bs = [p for c in ss.contours(nom) for p in c]
            if not br or not bs:
                continue
            for i in (0, 1):
                if (abs(min(p[i] for p in br) - min(p[i] for p in bs)) > 0.05
                        or abs(max(p[i] for p in br)
                               - max(p[i] for p in bs)) > 0.05):
                    ecarts += 1
                    if verbeux and ecarts <= 6:
                        print("  %s %s : boite differente du servi" % (mn, nom))
                    break
    if verbeux:
        print("  temoin du dessin : %d ecart(s) sur %d nom(s) et %d master(s)"
              % (ecarts, len(noms), len(MASTERS[cle_src])))
    return ecarts


def mesurer(font, mn, ae, noms):
    """Par nom : (crenage lu, blanc moyen, gouttiere). A l'etat non regle."""
    src = D.Source(font, mn)
    m_id = mid(font, mn)
    out = {}
    for n in noms:
        if font.glyphs[n] is None:
            continue
        k = A.kern(font, m_id, n, ae)
        _, blanc = A.inter_lettre(src, n, ae, k, *BANDE_CAP)
        g = A.couloir_plein(src, n, ae, k)
        if blanc is None or g is None:
            continue
        out[n] = (k, blanc, g)
    return out


def parcours(cle_src, dossier, temoin=False, verbeux=True):
    """Mesure une source. Rend {master: {nom: delta}} ou None si non mesure."""
    chemin = source_sans_reglage(cle_src, dossier)
    if chemin is None:
        print("  source amont absente (%s) : rien de mesure. Ce n'est pas un "
              "succes, c'est un inventaire non fait." % AMONT[cle_src])
        return None
    font = glyphsLib.GSFont(chemin)
    ae = A.GLYPHE_AE
    if font.glyphs[ae] is None:
        print("  %s absent : NON MESURE." % ae)
        return None
    # L'Æ EST DANS SA PROPRE FAMILLE, et la table du tour precedent le portait
    # deja : `AE+AE` est une paire de capitales comme une autre, et son blanc
    # est l'un des plus larges. L'ecarter parce qu'il est le second membre
    # serait un classement par le role dans la paire, pas par la forme.
    noms = capitales(font)
    temoin_du_dessin(font, cle_src, noms + [ae], verbeux)

    par_master = {}
    for mn in MASTERS[cle_src]:
        etat = mesurer(font, mn, ae, noms)
        if "C" not in etat:
            print("  %s : C absent, cible non calculable." % mn)
            return None
        k_C, blanc_C, g_C = etat["C"]
        # La cible : le blanc du C UNE FOIS SA DECISION PRISE, bornee comme les
        # autres. C'est la decision de Nicolas au cinquante-cinquieme tour, et
        # elle ne tient pas partout -- l'ExtraBold italique ne permet que -44.
        d_C = max(A.CIBLE_AE_DEPUIS_C, math.ceil(A.JOUR_MIN - g_C))
        cible = blanc_C + d_C
        if temoin:
            # LE TEMOIN POUSSE LE BLANC DU T A `cible + TEMOIN_K`, et il le
            # calcule au lieu de forcer un ecartement fixe. Un premier jet
            # ajoutait 100 unites en aveugle : le T est deja tres ferme devant
            # l'Æ, donc il restait sous la cible et le temoin rendait zero, ce
            # qui se lit comme un producteur qui ne mord pas. Les trois
            # grandeurs etant affines en `k` et de pente 1, le deplacement se
            # deduit exactement.
            k_T, blanc_T, g_T = etat[TEMOIN_NOM]
            dk = cible + TEMOIN_K - blanc_T
            etat[TEMOIN_NOM] = (k_T + dk, blanc_T + dk, g_T + dk)
        table, hors, lignes = {}, {}, []
        for n in sorted(etat):
            k, blanc, g = etat[n]
            if n == "C":
                table[n] = int(d_C)
                lignes.append((n, blanc, A.CIBLE_AE_DEPUIS_C,
                               A.JOUR_MIN - g, int(d_C)))
                continue
            if blanc <= cible + A.SEUIL_AE:
                continue
            voulu = cible - blanc
            permis = A.JOUR_MIN - g
            retenu = int(math.ceil(max(voulu, permis)))
            if retenu >= 0:
                # HORS DE PORTEE : la paire depasse la cible et sa gouttiere est
                # DEJA sous le plancher, donc aucune unite ne peut se fermer.
                # Un nom decide et un nom jamais regarde sont identiques dans
                # une table -- tous deux absents -- donc il s'ecrit, avec la
                # gouttiere qui l'explique. C'est la forme du point 96.
                hors[n] = round(g, 1)
                lignes.append((n, blanc, voulu, permis, None))
                continue
            table[n] = retenu
            lignes.append((n, blanc, voulu, permis, retenu))
        par_master[mn] = (table, hors)
        if verbeux:
            print("\n%-18s cible %.1f (C a %.1f, borne %.1f)"
                  % (mn, cible, blanc_C, A.JOUR_MIN - g_C))
            print("   %-14s %9s %8s %8s %7s"
                  % ("nom", "blanc", "voulu", "permis", "retenu"))
            for n, blanc, voulu, permis, retenu in lignes:
                if retenu is None:
                    print("   %-14s %9.1f %8.1f %8.1f %7s  HORS DE PORTEE, "
                          "gouttiere %.1f" % (n, blanc, voulu, permis, "--",
                                              A.JOUR_MIN - permis))
                    continue
                marque = "  borne" if retenu > math.ceil(voulu) else ""
                print("   %-14s %9.1f %8.1f %8.1f %+7d%s"
                      % (n, blanc, voulu, permis, retenu, marque))
    return par_master


ENTETE = '''"""Le crenage qui referme le blanc devant l'Æ en capitales. GENERE.

Ne pas editer a la main : produit par `inventaire_ae.py --ecrire`.

Point 93, tranche par Nicolas au cinquante-cinquieme tour sur
`tour55-etats-sc.html` : le C devant l'Æ a {cible:+.0f}, puis la famille entiere
traitee, chacune a sa valeur pour atteindre la meme cible, BORNEE PAR LE
PLANCHER DE JOUR de {jour:.0f} unites.

**Des DEPLACEMENTS et non une cible recalculee a la compilation.**
`approches.appliquer` les ajoute au crenage lu, etape 1ter.

**La cible n'est pas atteinte partout, et c'est une LIMITE CONNUE.** `L+Æ` est a
la fois la paire la plus large par le blanc moyen et l'une des plus serrees par
la gouttiere -- 28 unites en ExtraLight romain -- ce qui est la divergence exacte
que le point 93 decrivait sur `C+Æ`, et elle interdit de le refermer. Le L reste
la paire la plus large du voisinage de l'Æ dans tous les masters. Le C lui-meme
ne tient son {cible:+.0f} que dans sept masters sur huit : l'ExtraBold italique
ne permet que -44.

**LA FAMILLE SE MESURE SUR LA SOURCE, pas sur le sous-ensemble servi**, et c'est
la seconde reprise du point 97. Relevee sur les 58 capitales du binaire au tour
precedent, elle en oubliait DIX qui vivent dans la source et depassent la cible :
`Cacute`, `Ccaron`, `Cdotaccent`, `Ecaron`, `Edotaccent`, `Emacron`, `Eogonek`,
`Lacute`, `Lcaron`, `Lcommaaccent`. La section 5 de `check_crenage_sc` en avait
nomme huit -- elle s'arrete a huit lignes par master -- et c'est le producteur
qui a rendu les deux dernieres. Elles ne pesent rien sur le binaire servi, ou
elles ne sont pas ; elles pesent sur la police publiee sous OFL, et sur le jour
ou le sous-ensemble s'elargira.

**LA FAMILLE N'EST PAS LA MEME DANS LES HUIT MASTERS**, contre ce que le tour
precedent annoncait : `Eogonek` sort au Bold et a l'ExtraBold romains, `AE`,
`OE` et `Eogonek` a l'ExtraBold italique, leur blanc y passant sous la cible.
Un nom absent d'un master est un nom qui n'y depasse pas, et non un oubli.

**CE QUE `HORS_PORTEE_AE` PORTE.** Des capitales qui depassent la cible et dont
la gouttiere est DEJA sous le plancher de jour, donc qu'aucune unite ne peut
refermer. `Lslash` y est dans les huit masters, a 5,4 a 21,4 unites de gouttiere
pour un plancher de 24, et son crenage amont vaut zero : c'est un etat de la
police de base, la forme exacte du point ouvert 96. La valeur ecrite est la
gouttiere mesuree, pour que la ligne dise pourquoi elle est la.

Ecrite en clair et non calculee a l'execution : le bac a sable ne peut pas
toujours cloner la source amont, et un controle qui n'a pas pu lire sa source ne
doit rien conclure.
"""

REGLAGE_AE = {{
'''


def ecrire(tables):
    fusion = {}
    for t in tables:
        if t:
            fusion.update(t)
    chemin = os.path.join(ICI, "reglage_ae.py")
    with open(chemin, "w") as f:
        f.write(ENTETE.format(cible=A.CIBLE_AE_DEPUIS_C, jour=A.JOUR_MIN))
        n = h = 0
        for mn, (table, _hors) in fusion.items():
            f.write('    "%s": {\n' % mn)
            for nom in sorted(table):
                f.write('        "%s": %+d,\n' % (nom, table[nom]))
                n += 1
            f.write("    },\n")
        f.write("}\n\n")
        f.write("#: Les capitales qui depassent la cible et qu'AUCUNE unite ne "
                "peut refermer :\n#: leur gouttiere est deja sous le plancher "
                "de jour. La valeur est la\n#: gouttiere mesuree, en unites. "
                "Voir le point ouvert 96.\nHORS_PORTEE_AE = {\n")
        for mn, (_table, hors) in fusion.items():
            f.write('    "%s": {\n' % mn)
            for nom in sorted(hors):
                f.write('        "%s": %.1f,\n' % (nom, hors[nom]))
                h += 1
            f.write("    },\n")
        f.write("}\n")
    print("\n%s : %d valeur(s) et %d hors de portee, sur %d master(s)"
          % (chemin, n, h, len(fusion)))
    return chemin


def main():
    ecr = "--ecrire" in sys.argv
    tem = "--temoin" in sys.argv
    cles = [a for a in sys.argv[1:] if not a.startswith("--")] or \
        ["roman", "italic"]
    dossier = os.environ.get("TEMOIN_BUILD", "/tmp/build-temoin-ae")
    os.makedirs(dossier, exist_ok=True)
    tables, manque = [], False
    for cle in cles:
        print("=" * 78)
        print("=== la famille de l'AE, source %s%s"
              % (cle, "   TEMOIN" if tem else ""))
        t = parcours(cle, dossier, temoin=tem)
        if t is None:
            manque = True
            continue
        tables.append(t)
        if tem:
            vus = [mn for mn, (tab, _h) in t.items() if TEMOIN_NOM in tab]
            bons = [mn for mn in vus
                    if -TEMOIN_K - 2 <= t[mn][0][TEMOIN_NOM] <= -TEMOIN_K + 2]
            print("\n  TEMOIN : %s force de %+.0f, retrouve dans %d master(s) "
                  "sur %d, a la bonne valeur dans %d"
                  % (TEMOIN_NOM, -TEMOIN_K, len(vus), len(t), len(bons)))
            if len(bons) != len(t):
                print("  LE TEMOIN NE MORD PAS : le producteur ne sait pas "
                      "signaler un blanc en trop.")
                return 1
    if manque:
        print("\nUne source au moins n'a pas ete mesuree : RIEN ECRIT.")
        return 1
    if tem:
        print("\nTEMOIN : le producteur mord dans tous les masters.")
        return 0
    if ecr:
        ecrire(tables)
    else:
        print("\n(--ecrire pour regenerer reglage_ae.py)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
