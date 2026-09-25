"""Preuve directe : le nouveau dessin est-il contenu dans l'ancien ?

On rasterise chaque glyphe avant et apres, et on compte les pixels ajoutes.
C'est le seul controle qui verifie vraiment l'affirmation « le glyphe ne peut
que maigrir localement ».

Deux sections depuis le dix-huitieme tour.

La premiere est le controle historique du lot 2, inchange. Il signale ce qui
depasse 0,2 % de la surface, et sa liste d'exceptions attendues est courte : la
cedille et la virgule ajoutent de la matiere, parce que la mise en pointe avance
la pointe au lieu de couper le bout. Tout le reste doit rester muet.

La seconde est le controle des dix-sept glyphes a crochet souscrit, ecrits dans
la table au dix-huitieme tour. Elle n'a pas de seuil : elle imprime le chiffre
de chaque glyphe dans chaque master, parce que ces dix-sept sont des exceptions
par construction et que ce qui compte alors n'est pas de savoir s'ils ajoutent
de la matiere — ils en ajoutent tous — mais combien, et si ce combien se tient
le long de l'axe de graisse. Un chiffre qui saute d'un master a l'autre serait
le signe d'une pointe qui part ailleurs.

Sa reference n'est pas la source brute mais la source ou le lot 2 est applique
sans les dix-sept. C'est un piege rencontre au premier essai de ce controle, et
il faisait mentir la moitie des lignes : ĢĶŅ portent une lettre qu'aucune entree
ne traite, mais ĻļȘșȚț portent le L, le l, le S et le T, qui sont dans la table
depuis le lot 2, et ģ porte un g dont la queue est coupee. Mesures contre la
source brute, ces lettres rendaient jusqu'a 4,8 % de matiere retiree, qui est
celle de la coupe de la lettre et pas du crochet — et ģ, dont la virgule est
suscrite et non souscrite, apparaissait comme le glyphe le plus modifie de la
famille alors que son crochet n'est pas traite du tout. Une comparaison ne
mesure ce qu'on croit que si les deux termes ne different que par ce qu'on juge.

La virgule souscrite n'est pas testee seule : elle l'est a travers les douze
lettres qui la portent en composant. LA CEDILLE ET L'OGONEK LE SONT, depuis le
soixante-neuvieme tour, dans la premiere section : les treize lettres qui les
portent les dessinent en contours propres, donc `cedillacomb` et `ogonekcomb`
n'etaient mesures nulle part, alors qu'ils sont servis et atteignables par une
sequence combinante (point ouvert 28). L'ancienne phrase disait que les trois
combinants etaient testes a travers leurs lettres ; c'etait vrai de la virgule
seule.

PLAFONDS DEPUIS LE SOIXANTE-NEUVIEME TOUR, point ouvert 60. La premiere section
savait qu'un glyphe de `AJOUTENT` ajoute, pas combien : l'allongement du t
aurait pu passer de 60 a 200 unites sans qu'aucun controle du projet le dise,
`check_termes` ne verifiant que le localisateur. Chaque glyphe qui ajoute porte
un plafond par master, 10 % au-dessus de la valeur mesuree au soixante-
neuvieme tour plus 0,05 point. `--plafonds` imprime les valeurs mesurees, pour
les revoir quand une decision change un geste.

Le net, ajoute moins retire, est la grandeur a rapprocher de la mesure d'encre
sur contours : le Ç rend 0,40 ajoute et 0,29 retire en ExtraLight, soit +0,11,
qui est exactement l'encre mesuree par `souscrits.encre` au dix-septieme tour.
Les deux controles, l'un sur pixels et l'autre sur contours, tombent d'accord.
"""
import os
import sys

import numpy as np
import glyphsLib
from PIL import Image, ImageChops
import lot2 as L, dessin as D
# Le chemin d'Atkinson venait de `planche_lot2`, planche morte depuis que
# `LOT2` est une liste : ce seul import la faisait publier dans le depot.
# Soixante-neuvieme tour, point ouvert 12.
SRC = "/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs"
PLAFONDS_SEULS = "--plafonds" in sys.argv[1:]

# TROIS CODES DEPUIS LE SOIXANTE-SEPTIEME TOUR, point ouvert 31 : 0 conforme,
# 1 signale, 2 non mesure. Le critere n'est pas neuf, il est celui que ce
# fichier ecrit depuis le lot 2 : au-dela de 0,2 % de matiere ajoutee, un
# glyphe hors de `AJOUTENT` est un defaut. Il s'imprimait sans compter, et le
# script rendait 0 quoi qu'il affiche ; sans la source, il sortait a 1 sur une
# trace Python.
_SOURCES = (SRC, SRC.replace("Next.glyphs", "Next-Italic.glyphs"))
_ABSENTES = [p for p in _SOURCES if not os.path.exists(p)]
if _ABSENTES and __name__ == "__main__":
    for p in _ABSENTES:
        print(f"NON MESURE : source absente, {p}")
    sys.exit(2)

TAILLE = 900

# La section historique du lot 2.
#
# Cette liste etait ecrite en dur et n'a jamais suivi la table : les six
# terminaisons ecrites au vingt-deuxieme tour — n, m, t, f — n'y figuraient pas,
# donc le controle ne les regardait pas. Il ne mentait pas, il ne les couvrait
# pas, ce qui se voit moins et se corrige de la meme facon. Le bilan de
# couverture imprime en fin de section dit maintenant quelles entrees de la
# table aucun caractere de cette liste n'atteint.
# Le M entre au vingt-cinquieme tour, avec la plongee de son pied gauche : il
# etait la seule entree de la table que cette section n'ait jamais regardee, et
# c'est son propre bilan de couverture qui l'a dit.
# Le b, le d et le z rejoignent la liste au vingt-sixieme tour avec les quatre
# rentrants du lot 2. Le l y etait deja pour sa queue, et il porte maintenant
# deux coupes : c'est le premier glyphe du projet dans ce cas, et le contrôle de
# contenance mesure la somme des deux.
# Le lot 3 du vingt-septieme tour ajoute le p, le y et le Y : les trois
# n'etaient pas dans le champ de ce controle, donc leur contenance n'aurait pas
# ete mesuree et rien ne l'aurait signale. Un controle qui ne couvre pas est
# plus discret qu'un controle qui ment, et la liste de ce fichier a deja rate
# les quatre lettres du vingt-deuxieme tour pour cette raison.
# Le c, le C, le G et le Q rejoignent la liste au trentieme tour, avec le lot 5.
# C'est son propre bilan de couverture qui l'a dit, en les nommant en tete des
# non couverts le jour ou la table les a recus — quatrieme fois que ce bilan
# rattrape sa propre liste, et la raison de l'avoir ecrit.
# Ils comptent plus que les autres ici : le lot 5 est celui qui deplace le plus
# de matiere du projet, et dans les DEUX SENS selon le master — le C ExtraLight
# en gagne 1 057 unites carrees quand le Q ExtraBold en perd 7 548.
#: Completee une CINQUIEME fois au trente-neuvieme tour : `ţ` U+0163 et `Ţ`
#: U+0162 entrent, le jour ou la table leur donne les gestes de leur base. Sans
#: eux le controle restait MUET sur deux glyphes qui ajoutent 5 % de matiere,
#: et un controle qui ne couvre pas est plus discret qu'un controle qui ment.
#: NE PAS CONFONDRE avec `ț` U+021B et `Ț` U+021A, les formes a VIRGULE : ce
#: sont des composites de `t` et `T`, ils suivent leur base sans entree propre,
#: donc ils n'ont rien a couvrir ici.
#: LE T ET LE Z ENTRENT AU MEME TOUR, ce qui ferme la moitie du point ouvert 38 :
#: ils sont dans la table depuis le onzieme tour et cette section ne les avait
#: jamais regardes. Les deux restent muets, sous le seuil de 0,2 %, ce qui est
#: le bon comportement d'une coupe qui retire -- mais il fallait le MESURER, et
#: c'est le `Ţ` qui l'a fait remarquer en ajoutant sans etre declare.
# L'Æ ET L'Œ ENTRENT AU QUARANTE-NEUVIEME TOUR, le jour ou la table les recoit,
# et c'est la SIXIEME fois que le bilan de couverture de ce controle rattrape sa
# propre liste. Il les nommait lui-meme parmi les "non couverts par cette
# section" avant qu'ils y soient ajoutes : un controle qui travaille sur une
# liste doit imprimer ce que sa liste laisse dehors, et celui-ci le fait depuis
# le vingt-deuxieme tour.
#: SEPTIEME COMPLEMENT au soixante-neuvieme tour, point ouvert 38, mesure par
#: les noms que la liste n'atteignait pas : `É` et `À` pour `acutecomb.case` et
#: `gravecomb.case`, les accents capitales du francais ; `ő`, `č` et `ă` pour
#: le double aigu, le caron et la breve ; la cedille et l'ogonek seuls.
#: `idotless` et `jdotless` n'y entrent pas : le `i` et le `j` en sont les
#: composes, donc ils sont couverts. Restent hors d'atteinte `ogonekcomb.case`
#: et `ogonekcomb.alt`, qu'aucun caractere ne rend.
LOT2_CHARS = ("éêàçãilj FELSsgq,nmtfMbdzpyYhkNHAXcCGQţŢTZÆŒ"
              "ÉÀőčă\u0327\u0328")

# Ce qui ajoute de la matiere par construction, et qui doit donc rester muet
# dans le bilan des depassements. La cedille et la virgule avancent leur pointe ;
# le pied droit du n plonge sous la ligne de base et le bout du crochet du f
# avance vers la droite, deux coupes sortantes ; le sommet du fut du t bascule,
# ce qui rend l'encre a cinq dix-millemes pres mais deplace de la matiere
# au-dessus de la ligne d'origine.
# Le m et le M rejoignent la famille au vingt-cinquieme tour : la plongee de
# leur pied gauche est une sortante, donc elle ajoute de la matiere par
# construction, comme celle du pied droit du n. Sans cette ligne, le m etait
# signale sans etre classe, ce qui est le bon comportement d'un controle devant
# un glyphe qui change — et la mauvaise sortie si personne ne met la table a
# jour.
# Le h, le k, le N et le H rejoignent la famille au vingt-huitieme tour, avec le
# lot 4a. Leurs quatre gestes sont des sortantes, donc ils ajoutent par
# construction — et ce sont les PREMIERS du projet a ajouter de la matiere
# VERS LE HAUT : le N et le H portent en plus un pied qui plonge, donc chacun
# des deux ajoute des deux cotes de sa boite.
# Le A et le X rejoignent la famille au vingt-neuvieme tour, avec le lot 4b.
# Leurs deux gestes sont des sortantes, donc ils ajoutent par construction. Ce
# sont les PREMIERS du projet dont le coin coulisse le long d'une DIAGONALE :
# les onze sortantes ecrites avant elles portaient toutes leur bout sur un flanc
# vertical ou horizontal, donc le coin partait tout droit ou tout de cote. Ici
# il fait les deux a la fois, et la matiere s'ajoute en bas ET lateralement.
# AUCUNE des quatre cibles du lot 5 n'entre ici, et il a fallu une contradiction
# entre deux controles pour l'etablir.
#
# Cette section les a d'abord vues classees comme ajoutant et mesurees a 0,00 %,
# parce que `coupe.area` disait le contraire de son rendu : elle donnait
# +1 057 unites carrees sur le C ExtraLight quand cette section rendait
# « retire 0,686 % ». **C'est `coupe.area` qui mesurait autre chose.** Elle somme
# le polygone des NOEUDS D'ANCRAGE et ignore les points de controle : sur le C
# ExtraLight elle rend 52 606 pour 77 240 unites carrees d'encre reelle, soit
# 68 %. Elle sert au SIGNE, donc a l'orientation d'un contour, et a comparer des
# topologies identiques ; elle ne mesure pas une aire d'encre, et une coupe qui
# pousse un noeud hors du polygone des noeuds la fait monter pendant que l'encre
# baisse.
#
# L'ENCRE REELLE, mesuree par rasterisation a 1 600 px de cadratin sur les
# trente-deux etats : le lot 5 RETIRE partout, de 0,22 % sur le G ExtraLight a
# 3,09 % sur le c ExtraBold, sans une seule inversion de signe. « Une coupe
# rentrante ne peut que retirer » tient donc sur une ronde, contre ce que le
# balayage du trentieme tour avait d'abord conclu de `coupe.area`.
#: `ţ` ajoute comme le `t` : l'allongement de la barre montante est la seule
#: operation du projet qui ne tourne rien, donc elle ne peut qu'ajouter.
#:
#: `Ţ` AJOUTE PAR SA CEDILLE, ET NON PAR LE GESTE DU T. Trente-neuvieme tour,
#: mesure et non suppose. Cette section compare a la source BRUTE, donc elle
#: cumule la mise en pointe de la cedille du dix-huitieme tour et la coupe des
#: deux bouts de barre : 0,25 a 0,47 % selon le master. Le T lui-meme, entre
#: dans `LOT2_CHARS` au meme tour, reste MUET sous le seuil de 0,2 %. Et la
#: section 2, qui prend pour reference la source ou le lot 2 est applique sans
#: les dix-sept souscrits, rend le `Ţ` a -1,04 a -4,07 % au net : il RETIRE une
#: fois sa cedille mise a part. C'est la meme raison qui met `ç` dans cette
#: liste depuis l'origine.
#: `À` ajoute par le pied du A qui plonge, et non par son accent : 0,72 a
#: 0,81 % contre 0,77 a 0,85 % pour le A, le meme ajout dilue par l'accent.
#: La cedille et l'ogonek seuls ajoutent par leur mise en pointe, comme le `ç`.
AJOUTENT = set("ç,ntfmMpyYhkNHAXţŢÀ\u0327\u0328")

#: Plafond par master de chaque glyphe d'AJOUTENT, en % de la surface : 10 %
#: au-dessus de la valeur mesuree au soixante-neuvieme tour, plus 0,05 point.
#: Ce n'est pas une table a ajuster pour faire taire le controle : un geste qui
#: change par decision se remesure par `--plafonds`, et la table se reecrit
#: avec la raison du changement.
PLAFONDS = {
    ("roman", ','): {"ExtraLight": 4.00, "Regular": 3.01, "Bold": 2.12, "ExtraBold": 1.98},
    ("roman", 'A'): {"ExtraLight": 0.90, "Regular": 0.94, "Bold": 0.99, "ExtraBold": 0.99},
    ("roman", 'H'): {"ExtraLight": 1.66, "Regular": 1.68, "Bold": 1.74, "ExtraBold": 1.75},
    ("roman", 'M'): {"ExtraLight": 0.74, "Regular": 0.76, "Bold": 0.82, "ExtraBold": 0.82},
    ("roman", 'N'): {"ExtraLight": 0.70, "Regular": 0.74, "Bold": 0.77, "ExtraBold": 0.77},
    ("roman", 'X'): {"ExtraLight": 0.89, "Regular": 0.91, "Bold": 0.96, "ExtraBold": 0.96},
    ("roman", 'Y'): {"ExtraLight": 2.20, "Regular": 2.32, "Bold": 2.30, "ExtraBold": 2.30},
    ("roman", 'f'): {"ExtraLight": 3.24, "Regular": 3.23, "Bold": 3.13, "ExtraBold": 3.10},
    ("roman", 'h'): {"ExtraLight": 1.28, "Regular": 1.32, "Bold": 1.41, "ExtraBold": 1.41},
    ("roman", 'k'): {"ExtraLight": 1.37, "Regular": 1.36, "Bold": 1.41, "ExtraBold": 1.42},
    ("roman", 'm'): {"ExtraLight": 0.69, "Regular": 0.72, "Bold": 0.77, "ExtraBold": 0.77},
    ("roman", 'n'): {"ExtraLight": 1.07, "Regular": 1.10, "Bold": 1.17, "ExtraBold": 1.17},
    ("roman", 'p'): {"ExtraLight": 0.85, "Regular": 0.88, "Bold": 0.98, "ExtraBold": 1.00},
    ("roman", 't'): {"ExtraLight": 7.78, "Regular": 7.13, "Bold": 5.58, "ExtraBold": 5.31},
    ("roman", 'y'): {"ExtraLight": 1.74, "Regular": 1.66, "Bold": 1.54, "ExtraBold": 1.51},
    ("roman", 'À'): {"ExtraLight": 0.85, "Regular": 0.87, "Bold": 0.91, "ExtraBold": 0.92},
    ("roman", 'ç'): {"ExtraLight": 0.62, "Regular": 0.52, "Bold": 0.45, "ExtraBold": 0.45},
    ("roman", 'Ţ'): {"ExtraLight": 0.57, "Regular": 0.46, "Bold": 0.38, "ExtraBold": 0.37},
    ("roman", 'ţ'): {"ExtraLight": 6.72, "Regular": 6.29, "Bold": 5.15, "ExtraBold": 4.93},
    ("roman", "\u0327"): {"ExtraLight": 2.87, "Regular": 2.71, "Bold": 2.68, "ExtraBold": 2.65},
    ("roman", "\u0328"): {"ExtraLight": 6.34, "Regular": 5.06, "Bold": 3.73, "ExtraBold": 3.57},
    ("ital", ','): {"ExtraLight Italic": 3.67, "Italic": 2.85, "Bold Italic": 1.90, "ExtraBold Italic": 1.76},
    ("ital", 'A'): {"ExtraLight Italic": 0.90, "Italic": 0.95, "Bold Italic": 1.02, "ExtraBold Italic": 1.03},
    ("ital", 'H'): {"ExtraLight Italic": 1.63, "Italic": 1.65, "Bold Italic": 1.71, "ExtraBold Italic": 1.72},
    ("ital", 'M'): {"ExtraLight Italic": 0.73, "Italic": 0.76, "Bold Italic": 0.80, "ExtraBold Italic": 0.81},
    ("ital", 'N'): {"ExtraLight Italic": 0.72, "Italic": 0.74, "Bold Italic": 0.77, "ExtraBold Italic": 0.77},
    ("ital", 'X'): {"ExtraLight Italic": 0.85, "Italic": 0.84, "Bold Italic": 0.88, "ExtraBold Italic": 0.89},
    ("ital", 'Y'): {"ExtraLight Italic": 2.14, "Italic": 2.17, "Bold Italic": 2.27, "ExtraBold Italic": 2.27},
    ("ital", 'f'): {"ExtraLight Italic": 3.16, "Italic": 3.12, "Bold Italic": 3.07, "ExtraBold Italic": 3.06},
    ("ital", 'h'): {"ExtraLight Italic": 1.27, "Italic": 1.32, "Bold Italic": 1.39, "ExtraBold Italic": 1.40},
    ("ital", 'k'): {"ExtraLight Italic": 1.34, "Italic": 1.36, "Bold Italic": 1.40, "ExtraBold Italic": 1.41},
    ("ital", 'm'): {"ExtraLight Italic": 0.68, "Italic": 0.72, "Bold Italic": 0.75, "ExtraBold Italic": 0.76},
    ("ital", 'n'): {"ExtraLight Italic": 1.04, "Italic": 1.09, "Bold Italic": 1.14, "ExtraBold Italic": 1.14},
    ("ital", 'p'): {"ExtraLight Italic": 0.82, "Italic": 0.87, "Bold Italic": 0.96, "ExtraBold Italic": 0.98},
    ("ital", 't'): {"ExtraLight Italic": 7.94, "Italic": 7.13, "Bold Italic": 5.36, "ExtraBold Italic": 4.98},
    ("ital", 'y'): {"ExtraLight Italic": 1.71, "Italic": 1.74, "Bold Italic": 1.53, "ExtraBold Italic": 1.54},
    ("ital", 'À'): {"ExtraLight Italic": 0.85, "Italic": 0.89, "Bold Italic": 0.95, "ExtraBold Italic": 0.96},
    ("ital", 'ç'): {"ExtraLight Italic": 0.59, "Italic": 0.48, "Bold Italic": 0.40, "ExtraBold Italic": 0.40},
    ("ital", 'Ţ'): {"ExtraLight Italic": 0.56, "Italic": 0.42, "Bold Italic": 0.34, "ExtraBold Italic": 0.33},
    ("ital", 'ţ'): {"ExtraLight Italic": 6.81, "Italic": 6.23, "Bold Italic": 4.91, "ExtraBold Italic": 4.59},
    ("ital", "\u0327"): {"ExtraLight Italic": 2.76, "Italic": 2.49, "Bold Italic": 2.33, "ExtraBold Italic": 2.32},
    ("ital", "\u0328"): {"ExtraLight Italic": 7.12, "Italic": 5.88, "Bold Italic": 5.16, "ExtraBold Italic": 4.96},
}

# Les dix-sept du dix-huitieme tour, par famille, sous la forme ou ils se
# lisent. Les cinq cedilles et les huit lettres a ogonek portent leur crochet en
# contours propres ; les douze lettres a virgule souscrite le portent en
# composant, et c'est par elles que `commaaccentcomb` est teste.
# `ģ` n'y figure pas : sa virgule est suscrite (`commaturnedabovecomb`) et non
# souscrite, elle n'est traitee par aucune entree de la table, et c'est un point
# ouvert du projet. La mettre ici ferait croire a un dix-huitieme glyphe.
SOUSCRITS = [
    ("cedille",  "ÇŞşŢţ"),
    ("ogonek",   "ĄąĘęĮįŲų"),
    ("virgule",  "ĢĶķĻļŅņȘșȚț"),
]


def _rendu(source, ch):
    im = Image.new("L", (TAILLE * 2, TAILLE * 2), 255)
    D.dessiner(im, source, ch, TAILLE // 2, int(TAILLE * 1.4), TAILLE,
               encre=0, fond=255)
    return im


def _ajoute(im_base, im_neuf):
    """(part de matiere ajoutee, part de matiere retiree), en % de la base."""
    a = np.asarray(ImageChops.subtract(im_base, im_neuf)) > 128
    r = np.asarray(ImageChops.subtract(im_neuf, im_base)) > 128
    b = np.asarray(im_base) < 128
    n_base = max(int(b.sum()), 1)
    return 100.0 * int(a.sum()) / n_base, 100.0 * int(r.sum()) / n_base


import souscrits as S

LOT2_PLEIN = list(L.LOT2)
LOT2_SANS_SOUSCRITS = [e for e in LOT2_PLEIN if e[0] not in set(S.TOUS)]


def appliquer(src, entrees):
    """Le lot 2 applique a une copie fraiche de la source, avec la table donnee."""
    f = glyphsLib.load(open(src, encoding="utf-8"))
    L.LOT2[:] = entrees
    try:
        return L.appliquer_lot(f, 20.0)
    finally:
        L.LOT2[:] = LOT2_PLEIN


INATTENDUS = []      # section 1 : au-dela du seuil, hors d'AJOUTENT
DEPASSEMENTS = []    # section 1 : un glyphe d'AJOUTENT au-dela de son plafond
MESURES = {}         # (source, caractere) -> {master: ajout}, pour --plafonds
NON_MESURES = []     # section 2 : glyphe absent de la source

for src, lab in ((SRC, "roman"),
                 (SRC.replace("Next.glyphs", "Next-Italic.glyphs"), "ital")):
    base = glyphsLib.load(open(src, encoding="utf-8"))
    neuf = appliquer(src, LOT2_PLEIN)
    # la reference de la seconde section : tout le lot 2 sauf les dix-sept
    sans = appliquer(src, LOT2_SANS_SOUSCRITS)

    for master in [m.name for m in base.masters]:
        b, n = D.Source(base, master), D.Source(neuf, master)
        for ch in LOT2_CHARS:
            if D.nom_glyphe(base, ch) is None:
                continue
            ajout, _ = _ajoute(_rendu(b, ch), _rendu(n, ch))
            if ch in AJOUTENT:
                MESURES.setdefault((lab, ch), {})[master] = ajout
                plafond = PLAFONDS.get((lab, ch), {}).get(master)
                if plafond is None:
                    DEPASSEMENTS.append(f"{lab} {master} {ch!r} {ajout:.2f} %, "
                                        f"AUCUN PLAFOND")
                elif ajout > plafond:
                    DEPASSEMENTS.append(f"{lab} {master} {ch!r} {ajout:.2f} % "
                                        f"au-dela du plafond {plafond:.2f}")
            if ajout > 0.2:
                attendu = " (attendu)" if ch in AJOUTENT else ""
                if not attendu:
                    INATTENDUS.append(f"{lab} {master} {ch!r} {ajout:.2f} %")
                print(f"  {lab} {master[:12]:12s} {ch!r} matiere ajoutee "
                      f"{ajout:.2f} % de la surface{attendu}")
            elif ch in AJOUTENT and master == base.masters[0].name:
                # Un glyphe classe comme ajoutant de la matiere et qui n'en
                # ajoute pas merite d'etre dit : soit la table a change, soit
                # l'operation n'a pas eu lieu. La bascule du t est dans ce cas
                # par construction, son encre ne bouge pas.
                print(f"  {lab} {master[:12]:12s} {ch!r} classe comme ajoutant, "
                      f"mesure a {ajout:.2f} % : a verifier")
    # Bilan de couverture : quelles entrees de la table cette section ne
    # regarde-t-elle pas ? Une liste de caracteres ecrite en dur ne suit pas la
    # table toute seule, et le projet a deja paye ce genre de divergence.
    # LE BILAN SUIT LES COMPOSANTS depuis le soixante-neuvieme tour. Il ne
    # comptait que le glyphe que nomme chaque caractere, donc il annoncait non
    # couverts `acutecomb`, `idotless` et quatre autres que `é` ou `i` rendent
    # bel et bien ; c'est ce bilan qui avait fait ecrire au point ouvert 38 que
    # les combinants et les deux sans-point etaient hors champ.
    def _feuilles(nom, vus):
        if not nom or nom in vus:
            return
        vus.add(nom)
        g = base.glyphs[nom]
        if g is not None:
            for couche in g.layers:
                for c in couche.components:
                    _feuilles(c.name, vus)
    vus = set()
    for c in LOT2_CHARS + "".join(chars for _, chars in SOUSCRITS):
        _feuilles(D.nom_glyphe(base, c), vus)
    manquants = sorted({e[0] for e in LOT2_PLEIN} - {v for v in vus if v}
                       - set(S.TOUS))
    print(f"--- {lab} : controle de contenance du lot 2 termine")
    if manquants:
        print(f"    non couverts par cette section : {', '.join(manquants)}")

    print(f"--- {lab} : les dix-sept crochets souscrits, matiere ajoutee en %")
    for famille, chars in SOUSCRITS:
        for ch in chars:
            if D.nom_glyphe(base, ch) is None:
                print(f"    {famille:8s} {ch}  ABSENT DE LA SOURCE")
                NON_MESURES.append(f"{lab} {ch}")
                continue
            vals = []
            for master in [m.name for m in base.masters]:
                b, n = D.Source(sans, master), D.Source(neuf, master)
                ajout, retire = _ajoute(_rendu(b, ch), _rendu(n, ch))
                vals.append((ajout, retire))
            cols = "  ".join(f"{a - r:+5.2f}" for a, r in vals)
            nets = [a - r for a, r in vals]
            print(f"    {famille:8s} {ch}  {cols}   ecart {max(nets) - min(nets):.2f}"
                  f"   retire max {max(r for _, r in vals):.2f}")
    print(f"    (net ajoute moins retire, en % de la surface, par master : "
          f"{' '.join(m.name[:9] for m in base.masters)})")

if PLAFONDS_SEULS:
    print("\nValeurs mesurees des glyphes d'AJOUTENT, en % de la surface :")
    for (lab, ch), vals in sorted(MESURES.items()):
        print(f"  {lab:5s} {ch!r:10s} " + "  ".join(
            f"{m}={v:.2f}" for m, v in vals.items()))

print(f"\nTOTAL : {len(INATTENDUS)} depassement(s) hors de la liste des "
      f"exceptions, {len(DEPASSEMENTS)} au-dela d'un plafond, "
      f"{len(NON_MESURES)} glyphe(s) NON MESURE(S).")
for x in INATTENDUS + DEPASSEMENTS:
    print(f"  !! {x}")
sys.exit(1 if INATTENDUS or DEPASSEMENTS else (2 if NON_MESURES else 0))
