"""Le crenage qui ecarte les trois pieds gauches descendants. GENERE.

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

PAIRES_PIEDS = {
    "ExtraLight": [
        ("A", "x", +35),
        ("q", "y", +57),
        ("A", "X", +47),
        ("Agrave", "X", +47),
        ("Acircumflex", "X", +47),
        ("Adieresis", "X", +47),
        ("Eogonek", "y", +0),
    ],
    "Regular": [
        ("A", "x", +35),
        ("A", "X", +51),
        ("Agrave", "X", +51),
        ("Acircumflex", "X", +51),
        ("Adieresis", "X", +51),
        ("q", "y", +50),
        ("Eogonek", "y", -4),
        ("f", "Y", +3),
        ("f", "Ydieresis", +3),
    ],
    "Bold": [
        ("q", "X", +112),
        ("A", "x", +36),
        ("q", "M", +38),
        ("q", "H", +38),
        ("A", "X", +56),
        ("Agrave", "X", +56),
        ("Acircumflex", "X", +56),
        ("Adieresis", "X", +56),
        ("q", "seven", +26),
        ("f", "Y", +14),
        ("f", "Ydieresis", +14),
        ("q", "y", +36),
        ("f", "V", +4),
        ("q", "f", +3),
        ("f", "Icircumflex", +2),
    ],
    "ExtraBold": [
        ("q", "X", +113),
        ("q", "m", +46),
        ("A", "x", +36),
        ("q", "M", +44),
        ("q", "H", +44),
        ("A", "X", +58),
        ("Agrave", "X", +58),
        ("Acircumflex", "X", +58),
        ("Adieresis", "X", +58),
        ("q", "seven", +31),
        ("A", "y", -27),
        ("Agrave", "y", -27),
        ("Acircumflex", "y", -27),
        ("Adieresis", "y", -27),
        ("A", "ydieresis", -27),
        ("f", "Y", +15),
        ("f", "Ydieresis", +15),
        ("q", "y", +39),
        ("f", "Icircumflex", +8),
        ("q", "f", +7),
        ("f", "V", +6),
        ("Eogonek", "y", -5),
        ("f", "seven", +1),
    ],
    "ExtraLight Italic": [
        ("A", "x", +35),
        ("q", "y", +57),
        ("A", "X", +47),
        ("Agrave", "X", +47),
        ("Acircumflex", "X", +47),
        ("Adieresis", "X", +47),
        ("Eogonek", "y", +5),
        ("parenleft", "y", +5),
    ],
    "Italic": [
        ("A", "x", +35),
        ("A", "X", +51),
        ("Agrave", "X", +51),
        ("Acircumflex", "X", +51),
        ("Adieresis", "X", +51),
        ("q", "y", +49),
        ("Eogonek", "y", +2),
        ("f", "Y", +4),
        ("f", "Ydieresis", +4),
    ],
    "Bold Italic": [
        ("q", "X", +112),
        ("A", "x", +36),
        ("A", "X", +56),
        ("Agrave", "X", +56),
        ("Acircumflex", "X", +56),
        ("Adieresis", "X", +56),
        ("q", "M", +37),
        ("q", "H", +37),
        ("q", "y", +37),
        ("f", "Y", +13),
        ("f", "Ydieresis", +13),
        ("Eogonek", "y", +1),
        ("f", "V", +3),
    ],
    "ExtraBold Italic": [
        ("q", "X", +113),
        ("A", "x", +36),
        ("q", "M", +43),
        ("q", "H", +43),
        ("A", "X", +57),
        ("Agrave", "X", +57),
        ("Acircumflex", "X", +57),
        ("Adieresis", "X", +57),
        ("q", "seven", +30),
        ("A", "y", -28),
        ("Agrave", "y", -28),
        ("Acircumflex", "y", -28),
        ("Adieresis", "y", -28),
        ("A", "ydieresis", -28),
        ("q", "y", +34),
        ("f", "Y", +15),
        ("f", "Ydieresis", +15),
        ("Eogonek", "y", -4),
        ("f", "V", +5),
        ("q", "f", +5),
    ],
}
