#!/usr/bin/env python3
"""Le voisinage des trois pieds gauches descendants, et la table qui l'ecarte.

Vingt-sixieme tour, point ouvert 50. Le lot 1 du vingt-cinquieme tour fait
descendre le cote gauche du pied gauche du m, du M et du f sous la ligne de
base, a 22, 32 et 32 unites. La queue du q, elle, descend a droite : les deux se
croisent, et quatre paire-masters se touchent reellement — `q+M` au Bold et a
l'ExtraBold romains, `q+m` a l'ExtraBold, `q+M` en ExtraBold Italic.

**Le sens est l'inverse de celui de la table du F, et c'est ce qui change le
critere.** Le F avait OUVERT un couloir, qu'on refermait par un crenage negatif
borne par ce qu'Atkinson laisse : `approches.paire_bornee` ne descend jamais
sous Atkinson, donc le garde-fou peut exiger « jamais plus serre qu'Atkinson ».
Ici le geste FERME le couloir par construction, sur toutes les paires ou une
queue descendante rencontre un pied descendant. Exiger le couloir d'Atkinson
reviendrait a annuler le geste : il faudrait ecarter de 116 a 122 unites, mesure.
Le critere est donc un plancher de jour et non une comparaison a Atkinson.

**D'ou vient le plancher.** `approches.JOUR_MIN` vaut 24 unites, soit deux fois
le debord optique des rondes, qui vaut 12 dans cette police. C'est le seuil que
le projet emploie deja sur les crochets souscrits depuis le dix-septieme tour
(`souscrits.jour_pointe`), et c'est le seul chiffre du projet qui reponde a la
question « ce blanc se voit-il encore ». Il n'est pas pose pour l'occasion.

**Ce que le script ne fait pas.** Il ne suppose pas que le couloir soit une
fonction affine du crenage. Ecarter deux lettres translate l'une des deux, ce qui
peut deplacer la hauteur ou le couloir est minimal : la valeur est donc trouvee
par dichotomie sur la grandeur elle-meme, a 0,5 unite, puis arrondie vers le
haut pour que le plancher soit franchi et non atteint.

**Il mesure un etat sans sa propre table.** `approches.appliquer(font,
pieds=False)` ecrit le crenage du F et laisse celui des pieds de cote. Sans ce
drapeau le script redecouvrirait son objet : il mesurerait un couloir deja
ecarte, ne verrait plus rien a corriger et rendrait une table vide. C'est le
piege tombe cinq fois dans ce projet, dont deux fois sur un garde-fou.

Usage :
    python3 inventaire_pieds.py             # mesure les deux sources
    python3 inventaire_pieds.py --ecrire    # regenere paires_pieds.py
"""

import math
import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import approches as A
import dessin as D
import lot2 as L
from check_approches import VOISINS_F as VOISINS

ICI = os.path.dirname(os.path.abspath(__file__))
AMONT = {"roman": "/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs",
         "italic": "/tmp/ahn/sources/AtkinsonHyperlegibleNext-Italic.glyphs"}

#: Les trois glyphes que le lot 1 fait descendre, lus et non recopies : la
#: table, son generateur et son controle doivent parler du meme voisinage.
CIBLES = A.CIBLES_PIEDS


def k_pour(src, a, b, k0, cible, plafond):
    """Le plus petit crenage qui porte le couloir plein a `cible`.

    Le plafond est ce qui rendrait le couloir d'Atkinson : ecarter au-dela
    serait plus lache que la police de base, ce qu'aucune raison ne soutient.

    **Quand le plafond mord, la fonction rend le plafond et non None**, et c'est
    une correction du vingt-septieme tour. Le premier jet rendait None, donc la
    paire n'entrait pas dans la table et restait telle quelle : sur `q+y` cela
    laissait un couloir de −9,7 unites, c'est-a-dire un CONTACT servi, au motif
    qu'on ne pouvait pas atteindre le plancher.

    Le cas ne s'etait jamais presente et il se presente au lot 3 : Atkinson
    tient deja `q+y` a 17,9 a 20,0 unites selon le master, donc SOUS le plancher
    de 24. Les deux criteres du point 50 sont alors incompatibles, et le second
    est le bon — rendre le couloir de la police de base est le plus qu'on puisse
    faire sans etre plus lache qu'elle, et cela suffit a supprimer le contact.
    Le second element rendu dit lequel des deux criteres a decide, pour que la
    table ne cache pas ce qu'elle n'a pas pu atteindre.
    """
    if A.couloir_plein(src, a, b, k0) >= cible:
        return 0.0, "deja"
    if A.couloir_plein(src, a, b, k0 + plafond) < cible:
        return plafond, "plafond"
    lo, hi = 0.0, plafond
    while hi - lo > 0.5:
        mi = (lo + hi) / 2
        if A.couloir_plein(src, a, b, k0 + mi) >= cible:
            hi = mi
        else:
            lo = mi
    return hi, "plancher"


def parcours(cle_src, verbeux=True):
    """Mesure un cote de l'axe d'inclinaison. Rend {master: [(a, b, valeur)]}.

    Les deux sources se mesurent, et il le faut : le flanc gauche du fut est
    vertical en romain et penche de 12 degres en italique, donc le pied ne sort
    pas du meme cote ni de la meme quantite. Le projet a deja paye deux fois une
    mesure prise d'un seul cote de cet axe — le plafond de coupe du l, et la
    boite du n dont la passation affirmait qu'elle ne bougeait pas.
    """
    chemin = AMONT[cle_src]
    if not os.path.exists(chemin):
        print(f"  source amont absente ({chemin}) : rien de mesure. Ce n'est "
              "pas un succes, c'est un inventaire non fait.")
        return None
    amont = glyphsLib.GSFont(chemin)
    tem = glyphsLib.GSFont(chemin)
    L.appliquer_lot(tem)
    A.appliquer(tem, pieds=False)
    # LA FUSION DU LOT 4, ET SANS ELLE CETTE TABLE MESURE UN DESSIN QUI N'EST
    # PLUS SERVI. Ce generateur reconstruit son etat au lieu de lire
    # `Temoin.glyphs` ; tant que le lot 4 n'etait pas dans la chaine, les deux
    # coincidaient. Au quarantieme tour la fusion a fait plonger le pied du A
    # de 24 a 44 unites, et une regeneration a rendu la table IDENTIQUE --
    # un chiffre juste sur un objet perime, ce que rien ne signalait.
    import mesure_titrage as MT
    if MT.fusionner(tem, cle_src=0 if cle_src == "roman" else 1) is None:
        print("  perimetre du lot 4 non resoluble : la table porterait sur un "
              "dessin sans titrage. Ce n'est pas un inventaire, c'est un NON "
              "MESURE.")
        return None
    # LE SOMMET POINTE DU CIRCONFLEXE, quarante-et-unieme tour, et c'est la
    # SECONDE fois que ce generateur prend le meme defaut : la chaine a gagne
    # une etape, et un generateur qui RECONSTRUIT son etat cesse de decrire le
    # livrable ce jour-la. Le symptome est une ABSENCE de changement.
    #
    # Le geste ne devrait rien changer a CETTE table, qui mesure des pieds : la
    # pointe vit en haut. L'appel est la quand meme, et c'est deliberé -- un
    # generateur qui reconstruit doit rejouer TOUTE la chaine, faute de quoi la
    # prochaine etape qui comptera sera oubliee pour la meme raison.
    import pointe_sommet as PS
    PS.appliquer(tem)
    # LE BRAS DU O, quarante-huitieme tour, et c'est la TROISIEME fois que la
    # chaine gagne une etape que ce generateur doit rejouer. Il n'a rien a
    # changer a cette table : le bras est un contour greffe DANS la
    # contreforme, sa boite est strictement interieure a celle du glyphe, donc
    # il ne touche ni la chasse ni le couloir entre deux lettres -- mesure
    # avant ecriture, boite du O inchangee a 0,1 unite pres dans les quatre
    # masters romains. L'appel est la quand meme, pour la raison ecrite
    # au-dessus : la prochaine etape serait oubliee pour la meme raison.
    import bras_O as BR
    BR.appliquer(tem)
    # LE U REDESCENDU, quarante-neuvieme tour, et c'est la QUATRIEME etape que
    # ce generateur doit rejouer. Celle-ci, contrairement aux deux precedentes,
    # peut vraiment changer cette table : elle descend de 44 unites les deux
    # bouts hauts du U, donc elle modifie la BOITE du glyphe par le haut. Un
    # couloir mesure entre deux lettres n'en depend que si un voisin monte a
    # cette hauteur -- ce que la regeneration dira, et qui ne se devine pas.
    import abaisse_U as AU
    AU.appliquer(tem)
    # LES HUIT OPERATEURS, cinquante-troisieme tour, et LA BARRE MEDIANE,
    # cinquante-quatrieme. Cinquieme et sixieme etapes que ce generateur doit
    # rejouer, et les deux appels sont ecrits ensemble parce que le premier
    # MANQUAIT : le tour 53 avait mesure qu'aucun des huit operateurs n'est
    # cible ni voisin ici, ce qui rendait l'oubli sans effet et invisible.
    # Un generateur qui reconstruit doit rejouer TOUTE la chaine, y compris ce
    # qui ne le concerne pas, sinon c'est la PROCHAINE etape qui sera oubliee
    # sans que rien ne le dise. Effet mesure des deux : table inchangee.
    import operateurs as OP
    OP.appliquer(tem)
    import barre_mediane as BM
    BM.appliquer(tem)
    # LA QUEUE DU j DESCENDUE, soixantieme tour, et c'est la SEPTIEME etape que
    # ce generateur doit rejouer. Celle-ci le concerne au premier chef : le `A`
    # est une cible de cette table et le `j` un voisin, et le geste existe
    # justement pour que la paire `A+j` n'ait plus besoin du +106 qui est
    # ecrit ici depuis le vingt-neuvieme tour. **Sans cet appel, la table
    # garderait le +106 et le dessin descendu s'ecarterait deux fois.**
    import descente_j as DJ
    DJ.appliquer(tem)
    par_master = {}
    for m in tem.masters:
        sa, st = D.Source(amont, m.name), D.Source(tem, m.name)
        lignes = []
        # Une paire dont les DEUX membres sont des cibles est trouvee deux fois,
        # une par chaque cible. `f+Y` est dans ce cas depuis le lot 3 : le f est
        # une cible du lot 1 et le Y une du lot 3. Sans dedoublonnage la table
        # porterait la meme entree en double, et `ecrire_kern` l'ecrirait deux
        # fois sur la meme cle — ce qui est sans effet ici, les deux valeurs
        # etant egales, et qui cesserait de l'etre au premier ecart.
        vues = set()
        for cible in CIBLES:
            for v in VOISINS:
                nom = v if len(v) > 1 else D.nom_glyphe(amont, v)
                if nom is None or amont.glyphs[nom] is None:
                    continue
                # LES DEUX SENS, et le premier jet n'en testait qu'un.
                #
                # Il posait toujours le voisin en premier et la cible en
                # second, ce qui etait juste pour les trois pieds du lot 1 :
                # leur cote GAUCHE descend, donc ils mangent l'approche de la
                # lettre precedente. Le Y du lot 3 descend par son cote DROIT,
                # donc il mange celle de la lettre SUIVANTE, et le generateur
                # ne l'aurait jamais vu. Un garde-fou qui ne teste qu'un sens
                # doit le dire dans son nom ou dans sa sortie, et celui-ci ne
                # le disait pas.
                for a, b in ((nom, cible), (cible, nom)):
                    try:
                        k0a = A.kern(amont, m.id, a, b)
                        k0t = A.kern(tem, m.id, a, b)
                        ga = A.couloir_plein(sa, a, b, k0a)
                        gt = A.couloir_plein(st, a, b, k0t)
                    except Exception:
                        continue
                    if ga is None or gt is None or gt >= A.JOUR_MIN:
                        continue
                    # Ne retenir que ce que le GESTE a resserre. Une paire deja
                    # sous le plancher dans Atkinson et que le projet ne touche
                    # pas n'a rien a faire dans cette table : `q+p` y est a 18
                    # a 23 unites, `f+Y` a 9,5, `eacute+Y` a 9,4, et les
                    # ecarter serait plus lache que la police de base sans
                    # qu'aucune raison le soutienne.
                    if gt >= ga - 0.5:
                        continue
                    if (a, b) in vues:
                        continue
                    vues.add((a, b))
                    plafond = max(ga - gt, 1.0)
                    k, pourquoi = k_pour(st, a, b, k0t, A.JOUR_MIN, plafond)
                    lignes.append((a, b, k0a, k0t, ga, gt, k, pourquoi))
        lignes.sort(key=lambda t: t[5])
        if verbeux:
            if lignes:
                print(f"  {m.name:22s} Atk    Temoin   ecart   valeur totale")
            else:
                print(f"  {m.name:22s} aucune paire sous le plancher de "
                      f"{A.JOUR_MIN:.0f} unites")
        table = []
        for nom, cible, k0a, k0t, ga, gt, k, pourquoi in lignes:
            # Arrondi vers le haut : le plancher doit etre franchi, pas atteint.
            delta = math.ceil(k)
            # La valeur ecrite est TOTALE, parce qu'elle s'ecrit en exception
            # glyphe-glyphe, qui remplace et ne s'ajoute pas. Un premier jet de
            # la table du F ecrivait l'ajustement seul et sortait 31 paires par
            # master en italique 50 unites trop laches.
            valeur = int(round(k0t)) + delta
            table.append((nom, cible, valeur))
            if verbeux:
                note = ("" if pourquoi == "plancher" else
                        "   PLAFOND : Atkinson tient deja cette paire sous le "
                        f"plancher, a {ga:.1f} u ; la valeur rend son couloir "
                        "et pas le plancher")
                print(f"      {nom}+{cible:2s} {ga:7.1f} {gt:7.1f} "
                      f"{delta:+7d} {valeur:+8d}"
                      + ("" if abs(k0t) < 0.01 else
                         f"   (depart {k0t:+.0f})") + note)
        if table:
            par_master[m.name] = table
    return par_master


ENTETE = '''"""Le crenage qui ecarte les trois pieds gauches descendants. GENERE.

Ne pas editer a la main : produit par `inventaire_pieds.py --ecrire`.

Point ouvert 50, ouvert par le lot 1 du vingt-cinquieme tour et tranche au
vingt-sixieme. Le cote gauche du pied gauche du m, du M et du f descend sous la
ligne de base ; la queue du q descend a droite. Quatre paire-masters se
touchaient reellement, verifie deux fois et par deux mesures independantes — le
couloir sur la bande pleine, de -13,9 a -21,9 unites, et le comptage de taches
d'encre a 600 pixels de cadratin, ou deux taches devenaient une.

**Le critere n'est pas celui de la table du F.** Le F avait ouvert un couloir et
`paire_bornee` le refermait sans jamais passer sous Atkinson. Ici le geste ferme
le couloir par construction : rendre celui d'Atkinson demanderait d'ecarter de
116 a 122 unites, c'est-a-dire d'annuler le geste. La table porte donc au
plancher de jour du projet, `approches.JOUR_MIN`, 24 unites, soit deux fois le
debord optique des rondes et le seuil deja employe sur les crochets souscrits.

**Valeurs totales, en exception glyphe-glyphe**, comme la table du F et pour la
meme raison : la cle de groupe emporterait des paires que rien n'a resserrees.

**Aucun mot du corpus ne porte ces paires** : le q francais est toujours suivi
d'un u, sauf en fin de mot. La table sert la police publiee sous OFL, pas les
gabarits. C'est pour cette raison qu'elle ecarte au plancher et non au-dela.

Ecrite en clair et non calculee a l'execution : le bac a sable ne peut pas
toujours cloner la source amont, et un controle qui n'a pas pu lire sa source ne
doit rien conclure.
"""

'''


def ecrire(tables):
    """Ecrit paires_pieds.py. Les deux sources partagent la table, leurs noms de
    master etant distincts."""
    fusion = {}
    for t in tables:
        fusion.update(t or {})
    chemin = os.path.join(ICI, "paires_pieds.py")
    with open(chemin, "w") as f:
        f.write(ENTETE)
        f.write("PAIRES_PIEDS = {\n")
        for mn in fusion:
            f.write(f'    "{mn}": [\n')
            for a, b, v in fusion[mn]:
                f.write(f'        ("{a}", "{b}", {v:+d}),\n')
            f.write("    ],\n")
        f.write("}\n")
    n = sum(len(v) for v in fusion.values())
    print(f"\n{chemin} : {n} paire(s) sur {len(fusion)} master(s)")
    return chemin


if __name__ == "__main__":
    print(f"=== le voisinage des trois pieds descendants, plancher "
          f"{A.JOUR_MIN:.0f} unites")
    print("  le glyphe traite est SECOND membre : son cote gauche descend.")
    tables = [parcours(c) for c in ("roman", "italic")]
    if any(t is None for t in tables):
        print("\nNON FAIT : une source manque, la table n'est pas regeneree.")
        sys.exit(1)
    if "--ecrire" in sys.argv:
        ecrire(tables)
    else:
        print("\n(mesure seule ; --ecrire pour regenerer paires_pieds.py)")
