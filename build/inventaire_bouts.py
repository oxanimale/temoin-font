"""Le generateur de `paires_bouts.py` : les quatre demandes d'espacement.

Points ouverts 56 (le lot 5 ouvre son couloir), 39 (le l et le S capitale),
47 (le s comme second membre) et le z du lot 2. Nicolas les a groupes au
vingt-sixieme tour : les quatre demandent le meme geste, une table de paires
bornee sur un bout coupe. Traites ensemble au trente-et-unieme.

LE CRITERE, ET IL EST UNIQUE.

Fermeture pleine bornee par Atkinson, arbitree par Nicolas au trente-et-unieme
tour, la meme pour les huit cibles. La valeur vaut le plus petit de deux
grandeurs, et c'est `approches.paire_bornee` dans sa forme :

  - ce que la coupe a OUVERT, sur la bande de jugement, de la ligne de base a
    la hauteur d'x, la ou le blanc d'un bas de casse se lit ;
  - ce qu'on peut REFERMER sans passer sous le couloir d'Atkinson, sur la bande
    pleine, la ou se pose la question du contact.

Le second interdit tout contact par construction : la table ne rend jamais un
couloir plus etroit que celui de la police de base. C'est pourquoi ce
generateur ne porte pas de plancher de jour, contrairement a celui des pieds,
dont le geste FERME le couloir et dont les deux criteres sont incompatibles.

**« Tres legerement » est chiffre, et il vaut « entierement ».** La demande du
vingt-quatrieme tour sur le s ne portait pas de nombre. Mesure du
trente-et-unieme tour : la borne pleine permet de refermer l'integralite de
l'ouverture dans les huit masters, de 20 a 69 unites selon la paire. Nicolas a
retenu la fermeture pleine, donc la doctrine du F, plutot qu'une fraction.

**La regle de departage des paires internes est ecrite bien qu'elle soit sans
objet aujourd'hui.** Six des huit cibles sont voisines les unes des autres :
`z+s`, `C+s`, `l+s`, `s+s`, `C+C`, `c+o`. Si le s recevait un jour une part
plus faible que les autres, c'est LA PART DU s QUI L'EMPORTE sur toute paire
dont il est le second membre, arbitrage de Nicolas au trente-et-unieme tour. La
part etant aujourd'hui la meme pour tous, la regle ne change rien ; elle est ici
pour que la question soit deja tranchee le jour ou elle se posera.

POURQUOI L'ETAT MESURE EST CELUI OU TOUS LES GESTES COEXISTENT.

Un garde-fou qui applique UN geste a la fois est aveugle a toute paire dont les
DEUX membres portent un geste. Point ouvert 52, paye trois fois : `A+X` est
passee sous le plancher dans les huit masters sans qu'aucune passe de balayage
puisse la voir, et c'est le generateur des pieds, qui lit l'etat ecrit, qui l'a
rendue. Ce generateur reconstruit donc l'etat complet, `appliquer_lot` puis
`approches.appliquer(bouts=False)`, et mesure dedans.

`bouts=False` est indispensable et non une precaution : avec sa propre table
deja ecrite, ce generateur mesurerait un couloir qu'il a lui-meme referme, ne
verrait plus rien a corriger et rendrait une table vide. Cinq contrôles de ce
projet ont mesure leur propre reflet, dont deux garde-fous.

LES DEUX CRENAGES, ET C'EST LA CORRECTION QUI A SAUVE CETTE PASSE.

L'ouverture se mesure entre l'amont crene par Atkinson et Temoin crene par
TEMOIN, pas par Atkinson. Un premier jet passait le crenage d'Atkinson aux deux
etats : il rendait 11 paires ouvertes en ExtraLight quand le point 56 en annonce
zero, toutes avec le F pour premier membre et toutes a 105 unites. Il mesurait le
recul de la barre mediane du F, point ouvert 40, que `paires_F.py` referme deja.
Ce qui se corrige ici est ce qui reste ouvert dans l'ETAT SERVI.

C'est aussi pourquoi la valeur totale part du crenage de TEMOIN et non de celui
d'Atkinson : quelques paires par master sont deja crenees par la table du F, et
ecrire l'ajustement sur le crenage d'Atkinson ecraserait son correctif. Piege du
vingt-quatrieme tour, ou la table du F ecrivait l'ajustement seul et sortait
`F+A` 50 unites trop lache, jusqu'a 31 paires par master en italique.

L'ARRONDI VA VERS ZERO, ET C'EST L'INVERSE DE CELUI DES PIEDS.

La table des pieds arrondit vers le haut, `math.ceil` : son plancher doit etre
franchi et non atteint. Ici la contrainte est un plafond — ne jamais refermer
plus que la borne — donc l'arrondi va vers zero, `math.floor` sur la valeur
absolue. Un `ceil` referait exactement le defaut que la borne interdit.

Usage :
    python3 inventaire_bouts.py            # mesure seule, n'ecrit rien
    python3 inventaire_bouts.py --ecrire   # regenere paires_bouts.py
"""

import math
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

import glyphsLib

import approches as A
import dessin as D
import lot2 as L
from balayage_lot4b import couloir_exact
from check_approches import AMONT, MASTERS, VOISINS_F as VOISINS, mid
from mesure_bouts import CIBLES

#: Le s ne porte sa demande qu'en second membre : c'est son bout bas gauche qui
#: recule, donc le blanc AVANT lui. Le sens (s, voisin) est mesure quand meme,
#: parce qu'une table se lit dans les deux sens et qu'un chiffre non mesure ne
#: se devine pas.
SECOND_SEULEMENT = ("s",)


def parcours(cle_src, verbeux=True):
    """Mesure un cote de l'axe d'inclinaison. Rend {master: [(a, b, valeur)]}.

    Les deux sources se mesurent, et il le faut. Le projet a paye quatre fois
    une mesure prise d'un seul cote de cet axe : le plafond de coupe du l, la
    boite du n, le nom de coin du y, et l'etalonnage de la confusion du point 42.
    """
    chemin = AMONT[cle_src]
    if not os.path.exists(chemin):
        print(f"  source amont absente ({chemin}) : rien de mesure. Ce n'est "
              "pas un succes, c'est un inventaire non fait.")
        return None
    amont = glyphsLib.GSFont(chemin)
    tem = glyphsLib.GSFont(chemin)
    L.appliquer_lot(tem)
    A.appliquer(tem, bouts=False)
    # LA FUSION DU LOT 4 : voir la note jumelle dans `inventaire_pieds`. Ce
    # generateur reconstruit son etat, donc il ignorait le lot 4 le jour ou
    # celui-ci est entre dans la chaine, et il rendait une table juste sur un
    # dessin perime.
    import mesure_titrage as MT
    if MT.fusionner(tem, cle_src=0 if cle_src == "roman" else 1) is None:
        print("  perimetre du lot 4 non resoluble : la table porterait sur un "
              "dessin sans titrage. Ce n'est pas un inventaire, c'est un NON "
              "MESURE.")
        return None
    # LE SOMMET POINTE DU CIRCONFLEXE, quarante-et-unieme tour. MEME RAISON,
    # ET C'EST LA SECONDE FOIS : la chaine a gagne une etape, et un generateur
    # qui RECONSTRUIT son etat cesse de decrire le livrable ce jour-la. Le
    # symptome est une ABSENCE de changement, jamais une valeur fausse, donc
    # rien ne l'aurait signale. `ocircumflex` est dans la table de ce
    # generateur : la question n'etait pas theorique.
    import pointe_sommet as PS
    PS.appliquer(tem)
    # LE BRAS DU O : voir la note jumelle dans `inventaire_pieds`. Le O est
    # dans les voisins de cette table, donc la question se pose vraiment ici ;
    # la reponse mesuree est que le bras ne peut pas ouvrir ni fermer un
    # couloir, sa boite etant strictement interieure a celle du glyphe.
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
    # ce generateur doit rejouer. Elle peut vraiment changer cette table : le
    # geste modifie la BOITE du `j` par le bas, de 12 a 27 unites selon le
    # master, et cette table mesure ce que les coupes ont OUVERT entre deux
    # lettres. Ce que la regeneration dira ne se devine pas.
    import descente_j as DJ
    DJ.appliquer(tem)

    par_master = {}
    for mn in MASTERS[cle_src]:
        sa, st = D.Source(amont, mn), D.Source(tem, mn)
        ma, mt = mid(amont, mn), mid(tem, mn)
        table, lignes, ecarts, divergences = [], [], [], []
        vues = set()

        for cible in CIBLES:
            if tem.glyphs[cible] is None:
                continue
            for v in VOISINS:
                nom = v if len(v) > 1 else D.nom_glyphe(amont, v)
                if nom is None or tem.glyphs[nom] is None:
                    continue
                for a, b in ((nom, cible), (cible, nom)):
                    if (a, b) in vues:
                        continue
                    vues.add((a, b))
                    # UNE PAIRE, UN SEUL PRODUCTEUR. Le voisinage du F
                    # appartient a `inventaire_F`, qui le couvre entierement et
                    # dont la valeur recoit ensuite les trois reglages du F --
                    # les rondes a +15, le i a -40, l'espace a -60 -- tranches
                    # par Nicolas EN NAVIGATEUR. Les deux tables s'ecrivent en
                    # valeur TOTALE et en exception glyphe-glyphe, et celle-ci
                    # passe apres : une paire portee par les deux verrait le
                    # reglage valide ECRASE en silence.
                    #
                    # Le cas s'est presente au cinquante-quatrieme tour, et il
                    # a fallu que la barre mediane du F monte pour qu'il
                    # apparaisse : `F+c` franchissait le seuil pour la premiere
                    # fois et entrait ici a -132, contre -112 ecrits par la
                    # table du F et son reglage de ronde. Vingt unites, et rien
                    # ne l'aurait dit.
                    # Le F en PREMIER membre seulement : `paires_F` ne porte
                    # que `F+voisin`, jamais `voisin+F`. Un premier jet ecartait
                    # les deux sens et faisait sortir `C+F`, a -20 dans les deux
                    # masters ExtraBold, qu'aucune autre table ne reprendrait.
                    if a == "F":
                        continue
                    try:
                        ka = A.kern(amont, ma, a, b)
                        kt = A.kern(tem, mt, a, b)
                        oa, _ = A.inter_lettre(sa, a, b, ka)
                        ot, _ = A.inter_lettre(st, a, b, kt)
                        pa = A.couloir_plein(sa, a, b, ka)
                        pt = A.couloir_plein(st, a, b, kt)
                    except Exception:
                        continue
                    if None in (oa, ot, pa, pt):
                        continue
                    ouverture, borne = ot - oa, pt - pa
                    brut = min(ouverture, borne)
                    if ouverture < A.SEUIL_PAIRE or brut < A.SEUIL_PAIRE:
                        continue

                    # Accord avec `paire_bornee` sur toute paire que rien n'a
                    # encore crenee. Un seuil recopie devient un desaccord, et
                    # le projet l'a paye deux fois.
                    deja = abs(kt - ka) > 0.5
                    if not deja:
                        ref = A.paire_bornee(sa, st, a, b, ka)
                        if ref is None or abs(ref + round(brut, 1)) > 0.05:
                            ecarts.append((a, b, -round(brut, 1), ref))

                    # Le couloir exact sur chaque paire retenue. La table est
                    # bornee par Atkinson et non par un plancher, donc sa
                    # decision se prend pres de l'etat non ecarte : c'est la
                    # zone ou le minorant du point 55 peut diverger, et le
                    # resultat mesure sur les deux tables servies ne s'y
                    # transporte pas.
                    xa = couloir_exact(sa, a, b, ka)
                    xt = couloir_exact(st, a, b, kt)
                    if xa is not None and xt is not None:
                        if abs((xt - xa) - borne) > 0.05:
                            divergences.append((a, b, borne, xt - xa))

                    # Arrondi vers zero : ne jamais refermer plus que la borne.
                    delta = -int(math.floor(brut))
                    valeur = int(round(kt)) + delta
                    table.append((a, b, valeur))
                    lignes.append((a, b, ouverture, borne, delta, valeur, deja))

        lignes.sort(key=lambda t: t[4])
        if verbeux:
            print(f"\n  {mn:22s} {len(table)} paire(s)")
            if ecarts:
                print(f"    ALERTE : {len(ecarts)} paire(s) en desaccord avec "
                      "`paire_bornee`. Le critere a derive.")
                for a, b, v, r in ecarts:
                    print(f"      {a}+{b:<12s} ici {v}   paire_bornee {r}")
            if divergences:
                print(f"    ZONE DE DIVERGENCE : {len(divergences)} paire(s) "
                      "ou le minorant borne autrement que le couloir exact")
                for a, b, bp, bx in divergences:
                    print(f"      {a}+{b:<12s} minorant {bp:+8.2f}   exact "
                          f"{bx:+8.2f}   ecart {bx - bp:+8.2f}")
            if lignes:
                print(f"      {'paire':18s} {'ouvre':>8s} {'borne':>8s} "
                      f"{'delta':>7s} {'totale':>8s}")
                for a, b, o, bo, d, val, dj in lignes[:10]:
                    print(f"      {a+'+'+b:18s} {o:+8.1f} {bo:+8.1f} "
                          f"{d:+7d} {val:+8d}"
                          + ("   (deja crenee par une autre table)"
                             if dj else ""))
                if len(lignes) > 10:
                    print(f"      … et {len(lignes)-10} autre(s)")
        par_master[mn] = table
    return par_master


ENTETE = '''"""Le crenage des huit bouts coupes, paire par paire et master par master.

GENERE, ne pas editer a la main : produit par `inventaire_bouts.py --ecrire`.

Les quatre demandes d'espacement groupees, points ouverts 56, 39, 47 et le z du
lot 2. Nicolas les a groupees au vingt-sixieme tour et elles sont traitees
ensemble au trente-et-unieme : les quatre demandent le meme geste, une table de
paires bornee sur un bout coupe. Cibles : {cibles}.

**Le critere est la fermeture pleine bornee par Atkinson**, arbitrage de Nicolas
au trente-et-unieme tour, le meme pour les huit cibles. La valeur vaut le plus
petit de ce que la coupe a ouvert sur la bande de jugement et de ce qu'on peut
refermer sans passer sous le couloir d'Atkinson sur la bande pleine. Rien n'est
choisi : c'est `approches.paire_bornee`, et l'accord avec elle est verifie a
chaque generation sur toute paire que rien n'a encore crenee.

**Aucun contact n'est possible par construction.** La borne interdit de rendre
un couloir plus etroit que celui de la police de base. C'est pourquoi cette
table ne porte pas de plancher de jour, contrairement a `paires_pieds.py`, dont
le geste ferme le couloir et dont les deux criteres sont incompatibles.

**« Tres legerement » valait « entierement ».** La demande de Nicolas sur le s,
au vingt-quatrieme tour, ne portait pas de nombre. La borne pleine permet de
refermer l'integralite de l'ouverture dans les huit masters, de 20 a 69 unites
selon la paire, et c'est la fermeture pleine qui a ete retenue.

**Regle de departage, sans objet aujourd'hui et deja tranchee.** Six des huit
cibles sont voisines les unes des autres. Si le s recevait un jour une part plus
faible, c'est la part du s qui l'emporte sur toute paire dont il est le second
membre.

**Valeurs TOTALES et en exception glyphe-glyphe**, comme les deux autres tables
et pour la meme raison : la cle de groupe emporterait des paires que rien n'a
ouvertes. Elles valent le crenage de Temoin plus l'ajustement, et non le
crenage d'Atkinson plus l'ajustement — quelques paires par master sont deja
crenees par la table du F, et partir d'Atkinson ecraserait son correctif.

**L'arrondi va vers zero**, `math.floor` sur la valeur absolue, l'inverse de
celui des pieds : la contrainte est un plafond et non un plancher, donc arrondir
vers le haut referait le defaut que la borne interdit.

**Deux paires ne se referment pas et resteront ouvertes** : `F+l` ouvre 100
unites en romain et 113 a 118 en italique, `F+S` de 50 a 118, et leur borne vaut
zero. Le l monte a 708 et la barre haute du F a 668, donc rien n'a bouge en haut
et refermer en bas ecraserait le haut. Mecanisme du vingt-quatrieme tour, celui
qui a fait retirer l'approche du glyphe.

Ecrite en clair et non calculee a l'execution : le bac a sable ne peut pas
toujours cloner la source amont, et un controle qui n'a pas pu lire sa source ne
doit rien conclure.
"""

PAIRES_BOUTS = {{
'''


def ecrire(tables):
    fusion = {}
    for t in tables:
        if t:
            fusion.update(t)
    chemin = os.path.join(ICI, "paires_bouts.py")
    with open(chemin, "w") as f:
        f.write(ENTETE.format(cibles=", ".join(CIBLES)))
        n = 0
        for mn, paires in fusion.items():
            f.write(f'    "{mn}": [\n')
            for a, b, v in sorted(paires, key=lambda t: (t[0], t[1])):
                f.write(f'        ("{a}", "{b}", {v:+d}),\n')
                n += 1
            f.write("    ],\n")
        f.write("}\n")
    print(f"\n{chemin} : {n} paire(s) sur {len(fusion)} master(s)")
    return chemin


if __name__ == "__main__":
    ecr = "--ecrire" in sys.argv
    cles = [a for a in sys.argv[1:] if not a.startswith("--")] or \
        ["roman", "italic"]
    print("=" * 78)
    print("=== inventaire des huit bouts coupes")
    print(f"=== cibles : {', '.join(CIBLES)}   voisins : {len(VOISINS)}, "
          "les deux sens")
    print("=" * 78)
    ts = []
    for c in cles:
        print(f"\n=== {c}")
        ts.append(parcours(c))
    if ecr:
        if any(t is None for t in ts):
            print("\nRIEN ECRIT : un cote n'a pas pu etre mesure. Une table "
                  "partielle serait pire qu'aucune.")
        else:
            ecrire(ts)
    else:
        tot = sum(len(v) for t in ts if t for v in t.values())
        print(f"\n{tot} paire(s) au total (mesure seule ; --ecrire pour "
              "regenerer paires_bouts.py)")
