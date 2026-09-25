#!/usr/bin/env python3
"""Le producteur de `reglage_xa.py` : le X devant le A, refermé au plancher.

Ouvert par Nicolas au cinquante-sixieme tour, en navigateur sur `tour51.html` :
dans `OXA` compose en petites capitales, le X et le A lui paraissent trop
ecartes. Tranche sur `tour56-etats-XA.html` -- la fermeture PLEINE, bornee par le
plancher de jour, sur les quatre graisses et dans les deux sources.

**CE QUE LA MESURE A CORRIGE DE LA DEMANDE, et il y en a trois.**

Un, `X+A` n'est pas un geste du projet : la paire porte +15 a +19 selon le
master, et ces valeurs sont IDENTIQUES dans Atkinson. Ce qui a change au meme
tour, c'est que les petites capitales en ont herite au rapport 574/668 -- elles
portaient zero, elles portent +16. Le crenage neuf a donc ECARTE le X du A,
quand il resserre presque partout ailleurs.

Deux, le +19 d'Atkinson est un GARDE-FOU et non un gout : sans lui, la gouttiere
tombe a 24,8 unites en ExtraLight, 20,8 au Regular, 15,8 au Bold et 14,8 a
l'ExtraBold, pour un plancher de 24. Refermer, c'est manger dans la seule chose
qui separe deux diagonales, et la marge est donc etroite.

Trois, cette marge s'INVERSE sur l'axe : 15,8 unites dans les clairs, 8,8 a
l'ExtraBold. Le gras, ou la reserve est nee, est l'endroit ou il y a le moins de
place. Une valeur unique aurait donc ete fausse d'un bout de l'axe ou de
l'autre, et c'est pourquoi la table porte une valeur par master.

**LE CRITERE.** Fermer tout ce que la gouttiere permet sans franchir
`approches.JOUR_MIN`. C'est celui de `paires_pieds` depuis le vingt-sixieme
tour, pris dans l'autre sens : la table des pieds ECARTE jusqu'au plancher, ici
on FERME jusqu'a lui. Les huit masters atterrissent sur la meme gouttiere de
24,8 unites, ce qui est le signe que le critere mord partout de la meme facon.

**L'ARRONDI VA VERS ZERO**, `math.floor` sur la marge : la contrainte est un
plancher a ne pas franchir, donc arrondir dans l'autre sens referait le defaut
que la borne interdit. Le prix est au plus une unite de fermeture en moins.

**LA TABLE S'ECRIT SUR LA CLE DE GROUPE, et c'est mesure.** Le groupe decide de
l'etendue d'un reglage, et il se lit avant d'ecrire, jamais apres : `@MMK_L_X` ne
contient que le X, et `@MMK_R_A` porte le A, ses neuf accentuees et le Delta --
onze glyphes dont la gouttiere avec le X est rigoureusement la meme, 34,8 unites
au Bold. Une ecriture glyphe-glyphe aurait laisse `X+À` trente-neuf unites plus
lache que `X+A`, ce qui est exactement le defaut que `VOISINS_F` a coute au
cinquante-quatrieme tour. La cle portante d'Atkinson est deja celle-la, verifie.

**`A+X` NE RECOIT RIEN, ET C'EST MESURE.** Nicolas a demande la fermeture pleine
sur les deux paires ; celle-la y est deja. `paires_pieds` l'a posee au plancher
au vingt-neuvieme tour, apres le lot 4b : sa gouttiere vaut 24,2 a 25,2 unites
dans les huit masters, donc il reste 0,2 a 1,2 unite de marge, soit zero une fois
arrondie. Ecrire quoi que ce soit dessus la ferait passer sous le plancher, et
deux tables qui ecrivent en valeur totale sur la meme paire s'ecrasent.

    python3 inventaire_xa.py [roman|italic] [--ecrire] [--temoin]
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

#: La paire visee, ecrite et non deduite.
CIBLE = ("X", "A")

#: La paire jumelle, celle que Nicolas nommait dans la meme phrase. Le
#: producteur la MESURE et refuse de l'ecrire, au lieu de la passer sous
#: silence : un glyphe decide et un glyphe jamais regarde sont identiques dans
#: une table, tous deux absents.
JUMELLE = ("A", "X")

DRAPEAU = "TEMOIN_SANS_REGLAGE_XA"

#: Le temoin ecarte la paire d'autant d'unites avant de mesurer. La marge doit
#: alors croitre d'autant, et le deplacement retenu diminuer d'autant : les deux
#: grandeurs sont affines en `k` et de pente 1.
TEMOIN_K = 100.0


def source_sans_reglage(cle_src, dossier):
    """La chaine reelle, sautant la SEULE etape du reglage `X+A`.

    Pas `TEMOIN_SANS_APPROCHES`, qui sauterait l'etape entiere : la paire doit
    se mesurer la ou la decision se pose, donc avec tout le reste des approches
    deja ecrit. C'est la lecon que le producteur de l'Æ a payee le meme tour.
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


def temoin_du_dessin(font, cle_src, verbeux=True):
    """Le RECONSTRUIT compare au SERVI, sur les deux lettres de la paire.

    Les approches ne touchent aucun contour ni aucune chasse depuis le
    vingt-quatrieme tour : la seule chose qui doit differer est le CRENAGE. Un
    ecart de boite sur le X ou sur le A voudrait dire que la gouttiere est
    mesuree sur un autre dessin que le servi, et la borne serait posee a cote.
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
        for nom in CIBLE:
            if abs(sr.width(nom) - ss.width(nom)) > 0.05:
                ecarts += 1
                if verbeux:
                    print("  %s %s : chasse %.1f contre %.1f"
                          % (mn, nom, sr.width(nom), ss.width(nom)))
                continue
            br = [p for c in sr.contours(nom) for p in c]
            bs = [p for c in ss.contours(nom) for p in c]
            for i in (0, 1):
                if (abs(min(p[i] for p in br) - min(p[i] for p in bs)) > 0.05
                        or abs(max(p[i] for p in br)
                               - max(p[i] for p in bs)) > 0.05):
                    ecarts += 1
                    if verbeux:
                        print("  %s %s : boite differente du servi" % (mn, nom))
                    break
    if verbeux:
        print("  temoin du dessin : %d ecart(s) sur %d master(s)"
              % (ecarts, len(MASTERS[cle_src])))
    return ecarts


def conflits(font, m_id):
    """Les tables qui ecrivent deja sur la cible. Doit rendre une liste vide.

    Deux tables qui ecrivent en valeur TOTALE sur la meme paire, la seconde
    ecrase la premiere : le cinquante-quatrieme tour a failli perdre vingt
    unites sur `F+c` ainsi, et le controle qui l'a vu n'existait pas.
    """
    out = []
    mn = next(m.name for m in font.masters if m.id == m_id)
    for etiq, table in (("paires_pieds", A.PAIRES_PIEDS),
                        ("paires_bouts", A.PAIRES_BOUTS)):
        for a, b, _v in table.get(mn, ()):
            if (a, b) == CIBLE:
                out.append(etiq)
    if CIBLE[0] == "F" and CIBLE[1] in A.PAIRES_F.get(mn, {}):
        out.append("paires_F")
    return out


def parcours(cle_src, dossier, temoin=False, verbeux=True):
    """Mesure une source. Rend {master: deplacement} ou None si non mesure."""
    chemin = source_sans_reglage(cle_src, dossier)
    if chemin is None:
        print("  source amont absente (%s) : rien de mesure. Ce n'est pas un "
              "succes, c'est un inventaire non fait." % AMONT[cle_src])
        return None
    font = glyphsLib.GSFont(chemin)
    for nom in CIBLE + JUMELLE:
        if font.glyphs[nom] is None:
            print("  %s absent : NON MESURE." % nom)
            return None
    temoin_du_dessin(font, cle_src, verbeux)

    # L'ETENDUE DU REGLAGE SE LIT AVANT D'ECRIRE. La cle de groupe touche onze
    # glyphes ; ils doivent tous presenter la meme gouttiere au X, faute de quoi
    # le reglage donnerait a certains une valeur que leur forme ne justifie pas.
    if verbeux:
        _ka, _ma, kb, membres = A.groupes(font, *CIBLE)
        print("  cle droite %s : %d glyphe(s) -- %s"
              % (kb, len(membres), " ".join(membres)))

    table = {}
    for mn in MASTERS[cle_src]:
        m_id = mid(font, mn)
        src = D.Source(font, mn)
        repris = conflits(font, m_id)
        if repris:
            print("  %s : %s ecrit deja sur %s+%s. RIEN ECRIT."
                  % (mn, ", ".join(repris), *CIBLE))
            return None
        k = A.kern(font, m_id, *CIBLE)
        if temoin:
            k += TEMOIN_K
        g = A.couloir_plein(src, CIBLE[0], CIBLE[1], k)
        if g is None:
            print("  %s : gouttiere non mesurable. NON MESURE." % mn)
            return None
        marge = g - A.JOUR_MIN
        d = -int(math.floor(marge))
        # Le groupe doit repondre comme son representant, et c'est MESURE a
        # chaque execution plutot que suppose.
        _ka, _ma, _kb, membres = A.groupes(font, *CIBLE)
        divergents = []
        for n in membres:
            if font.glyphs[n] is None:
                continue
            gn = A.couloir_plein(src, CIBLE[0], n, k)
            if gn is None or abs(gn - g) > 0.55:
                divergents.append("%s %s" % (n, "?" if gn is None
                                             else "%.1f" % gn))
        if divergents:
            print("  %s : le groupe ne repond pas comme le %s -- %s. RIEN "
                  "ECRIT." % (mn, CIBLE[1], ", ".join(divergents)))
            return None
        table[mn] = d
        if verbeux:
            kj = A.kern(font, m_id, *JUMELLE)
            gj = A.couloir_plein(src, JUMELLE[0], JUMELLE[1], kj)
            print("  %-18s %s%s %+3.0f  gouttiere %5.1f  marge %5.1f  "
                  "retenu %+4d  -> %5.1f   |  %s%s deja a %5.1f"
                  % (mn, CIBLE[0], CIBLE[1], k, g, marge, d, g + d,
                     JUMELLE[0], JUMELLE[1], gj))
    return table


ENTETE = '''"""Le crenage qui referme le X devant le A. GENERE.

Ne pas editer a la main : produit par `inventaire_xa.py --ecrire`.

Ouvert par Nicolas au cinquante-sixieme tour en navigateur, tranche sur
`tour56-etats-XA.html` : la fermeture PLEINE, bornee par le plancher de jour de
{jour:.0f} unites, sur les quatre graisses et dans les deux sources.

**Des DEPLACEMENTS et non une cible recalculee a la compilation.**
`approches.appliquer` les ajoute au crenage lu, etape 1quater.

**Une valeur par master, parce que la marge s'inverse sur l'axe.** Le +19
d'Atkinson est un garde-fou : sans lui, la gouttiere de `X+A` tombe sous le
plancher dans trois masters sur quatre. Ce qui reste a fermer vaut 15,8 unites
dans les clairs et 8,8 a l'ExtraBold, donc le gras -- ou la reserve est nee --
est l'endroit ou il y a le moins de place. Les huit masters atterrissent sur la
meme gouttiere de 24,8 unites.

**Ecrite sur la CLE DE GROUPE**, `@MMK_L_X` x `@MMK_R_A`, qui porte le A, ses
neuf accentuees et le Delta : onze glyphes dont la gouttiere avec le X est
rigoureusement la meme. Le producteur le remesure a chaque execution et refuse
d'ecrire si le groupe cesse de repondre comme son representant.

**`A+X` ne recoit rien**, et c'est mesure : `paires_pieds` l'a deja posee au
plancher au vingt-neuvieme tour, sa gouttiere valant 24,2 a 25,2 unites.

Ecrite en clair et non calculee a l'execution : le bac a sable ne peut pas
toujours cloner la source amont, et un controle qui n'a pas pu lire sa source ne
doit rien conclure.
"""

REGLAGE_XA = {{
'''


def ecrire(tables):
    fusion = {}
    for t in tables:
        if t:
            fusion.update(t)
    chemin = os.path.join(ICI, "reglage_xa.py")
    with open(chemin, "w") as f:
        f.write(ENTETE.format(jour=A.JOUR_MIN))
        for mn in fusion:
            f.write('    "%s": %+d,\n' % (mn, fusion[mn]))
        f.write("}\n")
    print("\n%s : %d master(s)" % (chemin, len(fusion)))
    return chemin


def main():
    ecr = "--ecrire" in sys.argv
    tem = "--temoin" in sys.argv
    cles = [a for a in sys.argv[1:] if not a.startswith("--")] or \
        ["roman", "italic"]
    dossier = os.environ.get("TEMOIN_BUILD", "/tmp/build-temoin-xa")
    os.makedirs(dossier, exist_ok=True)
    tables, manque = [], False
    for cle in cles:
        print("=" * 78)
        print("=== le %s devant le %s, source %s%s"
              % (CIBLE[0], CIBLE[1], cle, "   TEMOIN" if tem else ""))
        t = parcours(cle, dossier, temoin=tem)
        if t is None:
            manque = True
            continue
        tables.append(t)
    if manque:
        print("\nUne source au moins n'a pas ete mesuree : RIEN ECRIT.")
        return 1
    if tem:
        # Le temoin ecarte la paire de TEMOIN_K avant de mesurer : le
        # deplacement retenu doit avoir baisse d'autant, a une unite pres.
        ref = {}
        for cle in cles:
            r = parcours(cle, dossier, temoin=False, verbeux=False)
            if r:
                ref.update(r)
        fusion = {}
        for t in tables:
            fusion.update(t)
        mauvais = [mn for mn in fusion
                   if abs((ref[mn] - fusion[mn]) - TEMOIN_K) > 1.5]
        print("\n  TEMOIN : paire ecartee de %+.0f, le deplacement suit dans "
              "%d master(s) sur %d" % (TEMOIN_K, len(fusion) - len(mauvais),
                                       len(fusion)))
        if mauvais:
            print("  LE TEMOIN NE MORD PAS sur : %s" % ", ".join(mauvais))
            return 1
        print("  Le producteur mord dans tous les masters. RIEN ECRIT.")
        return 0
    if ecr:
        ecrire(tables)
    else:
        print("\n(--ecrire pour regenerer reglage_xa.py)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
