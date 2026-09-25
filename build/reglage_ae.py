"""Le crenage qui referme le blanc devant l'Æ en capitales. GENERE.

Ne pas editer a la main : produit par `inventaire_ae.py --ecrire`.

Point 93, tranche par Nicolas au cinquante-cinquieme tour sur
`tour55-etats-sc.html` : le C devant l'Æ a -50, puis la famille entiere
traitee, chacune a sa valeur pour atteindre la meme cible, BORNEE PAR LE
PLANCHER DE JOUR de 24 unites.

**Des DEPLACEMENTS et non une cible recalculee a la compilation.**
`approches.appliquer` les ajoute au crenage lu, etape 1ter.

**La cible n'est pas atteinte partout, et c'est une LIMITE CONNUE.** `L+Æ` est a
la fois la paire la plus large par le blanc moyen et l'une des plus serrees par
la gouttiere -- 28 unites en ExtraLight romain -- ce qui est la divergence exacte
que le point 93 decrivait sur `C+Æ`, et elle interdit de le refermer. Le L reste
la paire la plus large du voisinage de l'Æ dans tous les masters. Le C lui-meme
ne tient son -50 que dans sept masters sur huit : l'ExtraBold italique
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

REGLAGE_AE = {
    "ExtraLight": {
        "AE": -33,
        "C": -50,
        "Cacute": -50,
        "Ccaron": -50,
        "Ccedilla": -49,
        "Cdotaccent": -50,
        "E": -33,
        "Eacute": -33,
        "Ecaron": -33,
        "Ecircumflex": -33,
        "Edieresis": -33,
        "Edotaccent": -33,
        "Egrave": -33,
        "Emacron": -33,
        "Eogonek": -16,
        "L": -3,
        "Lacute": -3,
        "Lcaron": -3,
        "Lcommaaccent": -3,
        "OE": -33,
    },
    "Regular": {
        "AE": -21,
        "C": -50,
        "Cacute": -50,
        "Ccaron": -50,
        "Ccedilla": -47,
        "Cdotaccent": -50,
        "E": -42,
        "Eacute": -42,
        "Ecaron": -42,
        "Ecircumflex": -42,
        "Edieresis": -42,
        "Edotaccent": -42,
        "Egrave": -42,
        "Emacron": -42,
        "Eogonek": -14,
        "L": -24,
        "Lacute": -24,
        "Lcaron": -24,
        "Lcommaaccent": -24,
        "OE": -24,
    },
    "Bold": {
        "AE": -4,
        "C": -50,
        "Cacute": -50,
        "Ccaron": -50,
        "Ccedilla": -42,
        "Cdotaccent": -50,
        "E": -16,
        "Eacute": -16,
        "Ecaron": -16,
        "Ecircumflex": -16,
        "Edieresis": -16,
        "Edotaccent": -16,
        "Egrave": -16,
        "Emacron": -16,
        "L": -62,
        "Lacute": -62,
        "Lcaron": -34,
        "Lcommaaccent": -62,
        "OE": -6,
    },
    "ExtraBold": {
        "AE": -2,
        "C": -50,
        "Cacute": -50,
        "Ccaron": -50,
        "Ccedilla": -41,
        "Cdotaccent": -50,
        "E": -13,
        "Eacute": -13,
        "Ecaron": -13,
        "Ecircumflex": -13,
        "Edieresis": -13,
        "Edotaccent": -13,
        "Egrave": -13,
        "Emacron": -13,
        "L": -68,
        "Lacute": -68,
        "Lcaron": -31,
        "Lcommaaccent": -68,
        "OE": -5,
    },
    "ExtraLight Italic": {
        "AE": -35,
        "C": -50,
        "Cacute": -50,
        "Ccaron": -50,
        "Ccedilla": -49,
        "Cdotaccent": -50,
        "E": -35,
        "Eacute": -35,
        "Ecaron": -35,
        "Ecircumflex": -35,
        "Edieresis": -35,
        "Edotaccent": -35,
        "Egrave": -35,
        "Emacron": -35,
        "Eogonek": -16,
        "L": -5,
        "Lacute": -5,
        "Lcaron": -5,
        "Lcommaaccent": -5,
        "OE": -32,
    },
    "Italic": {
        "AE": -25,
        "C": -50,
        "Cacute": -50,
        "Ccaron": -50,
        "Ccedilla": -47,
        "Cdotaccent": -50,
        "E": -47,
        "Eacute": -47,
        "Ecaron": -47,
        "Ecircumflex": -47,
        "Edieresis": -47,
        "Edotaccent": -47,
        "Egrave": -47,
        "Emacron": -47,
        "Eogonek": -14,
        "L": -27,
        "Lacute": -27,
        "Lcaron": -27,
        "Lcommaaccent": -27,
        "OE": -28,
    },
    "Bold Italic": {
        "AE": -6,
        "C": -50,
        "Cacute": -50,
        "Ccaron": -50,
        "Ccedilla": -42,
        "Cdotaccent": -50,
        "E": -19,
        "Eacute": -19,
        "Ecaron": -19,
        "Ecircumflex": -19,
        "Edieresis": -19,
        "Edotaccent": -19,
        "Egrave": -19,
        "Emacron": -19,
        "L": -65,
        "Lacute": -65,
        "Lcaron": -35,
        "Lcommaaccent": -65,
        "OE": -9,
    },
    "ExtraBold Italic": {
        "C": -43,
        "Cacute": -43,
        "Ccaron": -43,
        "Ccedilla": -34,
        "Cdotaccent": -43,
        "E": -9,
        "Eacute": -9,
        "Ecaron": -9,
        "Ecircumflex": -9,
        "Edieresis": -9,
        "Edotaccent": -9,
        "Egrave": -9,
        "Emacron": -9,
        "L": -72,
        "Lacute": -72,
        "Lcaron": -25,
        "Lcommaaccent": -72,
    },
}

#: Les capitales qui depassent la cible et qu'AUCUNE unite ne peut refermer :
#: leur gouttiere est deja sous le plancher de jour. La valeur est la
#: gouttiere mesuree, en unites. Voir le point ouvert 96.
HORS_PORTEE_AE = {
    "ExtraLight": {
        "Lslash": 5.4,
    },
    "Regular": {
        "Lslash": 10.4,
    },
    "Bold": {
        "Lslash": 20.4,
    },
    "ExtraBold": {
        "Lslash": 21.4,
    },
    "ExtraLight Italic": {
        "Lslash": 5.4,
    },
    "Italic": {
        "Lslash": 10.4,
    },
    "Bold Italic": {
        "Lslash": 20.4,
    },
    "ExtraBold Italic": {
        "Lslash": 21.4,
    },
}
