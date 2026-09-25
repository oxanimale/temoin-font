"""Les paires que le titrage fusionne met en CONTACT, et que
les trois autres tables ne regardaient pas.

GENEREE par `inventaire_contacts.py --ecrire`. Ne pas
editer a la main : la prochaine execution ecraserait la
correction, et le projet a deja paye une table editee dont
le producteur ne savait rien.

Le critere, son sens et le choix de la cle sont dans le
docstring du producteur. Chaque entree porte
(a, b, valeur totale, cle, critere) : `cle` vaut "groupe"
quand tous les membres du groupe de crenage droit de `a` ont
la meme gouttiere devant `b`, "glyphe" sinon ; `critere` dit
si la valeur atteint le plancher de jour ou si le couloir
d'Atkinson l'a bornee.
"""

PAIRES_CONTACTS = {
    # --- romain
    "ExtraLight": [
        ("Aacute", "X", 46, "glyphe", "plancher"),
        ("Aacute", "x", 34, "glyphe", "atkinson"),
        ("Acircumflex", "x", 34, "glyphe", "atkinson"),
        ("Adieresis", "x", 34, "glyphe", "atkinson"),
        ("Agrave", "x", 34, "glyphe", "atkinson"),
        ("Aring", "X", 46, "glyphe", "plancher"),
        ("Aring", "x", 34, "glyphe", "atkinson"),
        ("Atilde", "X", 46, "glyphe", "plancher"),
        ("Atilde", "x", 34, "glyphe", "atkinson"),
        ("Q", "x", 3, "glyphe", "atkinson"),
    ],
    "Regular": [
        ("Aacute", "X", 50, "glyphe", "plancher"),
        ("Aacute", "x", 35, "glyphe", "atkinson"),
        ("Acircumflex", "x", 35, "glyphe", "atkinson"),
        ("Adieresis", "x", 35, "glyphe", "atkinson"),
        ("Agrave", "x", 35, "glyphe", "atkinson"),
        ("Aring", "X", 50, "glyphe", "plancher"),
        ("Aring", "x", 35, "glyphe", "atkinson"),
        ("Atilde", "X", 50, "glyphe", "plancher"),
        ("Atilde", "x", 35, "glyphe", "atkinson"),
    ],
    "Bold": [
        ("Aacute", "X", 56, "glyphe", "plancher"),
        ("Aacute", "x", 35, "glyphe", "atkinson"),
        ("Acircumflex", "x", 35, "glyphe", "atkinson"),
        ("Adieresis", "x", 35, "glyphe", "atkinson"),
        ("Agrave", "x", 35, "glyphe", "atkinson"),
        ("Aring", "X", 56, "glyphe", "plancher"),
        ("Aring", "x", 35, "glyphe", "atkinson"),
        ("Atilde", "X", 56, "glyphe", "plancher"),
        ("Atilde", "x", 35, "glyphe", "atkinson"),
        ("K", "Icircumflex", 17, "groupe", "plancher"),
        ("K", "idieresis", 8, "groupe", "au-dela d'atkinson"),
        ("V", "Icircumflex", 7, "glyphe", "plancher"),
    ],
    "ExtraBold": [
        ("Aacute", "X", 57, "glyphe", "plancher"),
        ("Aacute", "x", 35, "glyphe", "atkinson"),
        ("Aacute", "y", -27, "glyphe", "plancher"),
        ("Aacute", "ydieresis", -27, "glyphe", "plancher"),
        ("Acircumflex", "x", 35, "glyphe", "atkinson"),
        ("Acircumflex", "ydieresis", -27, "glyphe", "plancher"),
        ("Adieresis", "x", 35, "glyphe", "atkinson"),
        ("Adieresis", "ydieresis", -27, "glyphe", "plancher"),
        ("Agrave", "x", 35, "glyphe", "atkinson"),
        ("Agrave", "ydieresis", -27, "glyphe", "plancher"),
        ("Aring", "X", 57, "glyphe", "plancher"),
        ("Aring", "x", 35, "glyphe", "atkinson"),
        ("Aring", "y", -27, "glyphe", "plancher"),
        ("Aring", "ydieresis", -27, "glyphe", "plancher"),
        ("Atilde", "X", 57, "glyphe", "plancher"),
        ("Atilde", "x", 35, "glyphe", "atkinson"),
        ("Atilde", "y", -27, "glyphe", "plancher"),
        ("Atilde", "ydieresis", -27, "glyphe", "plancher"),
        ("K", "Icircumflex", 22, "groupe", "plancher"),
        ("K", "idieresis", 11, "groupe", "au-dela d'atkinson"),
        ("V", "Icircumflex", 11, "glyphe", "plancher"),
        ("W", "Icircumflex", 3, "groupe", "plancher"),
    ],
    # --- italique
    "ExtraLight Italic": [
        ("Acircumflex", "x", 34, "glyphe", "atkinson"),
        ("Adieresis", "x", 34, "glyphe", "atkinson"),
        ("Agrave", "x", 34, "glyphe", "atkinson"),
        ("Aring", "X", 46, "glyphe", "plancher"),
        ("Aring", "x", 34, "glyphe", "atkinson"),
        ("Q", "x", 3, "glyphe", "atkinson"),
    ],
    "Italic": [
        ("Acircumflex", "x", 35, "glyphe", "atkinson"),
        ("Adieresis", "x", 35, "glyphe", "atkinson"),
        ("Agrave", "x", 35, "glyphe", "atkinson"),
        ("Aring", "X", 50, "glyphe", "plancher"),
        ("Aring", "x", 35, "glyphe", "atkinson"),
    ],
    "Bold Italic": [
        ("Acircumflex", "x", 35, "glyphe", "atkinson"),
        ("Adieresis", "x", 35, "glyphe", "atkinson"),
        ("Agrave", "x", 35, "glyphe", "atkinson"),
        ("Aring", "X", 56, "glyphe", "plancher"),
        ("Aring", "x", 35, "glyphe", "atkinson"),
        ("K", "Icircumflex", 7, "groupe", "plancher"),
        ("K", "idieresis", 22, "groupe", "au-dela d'atkinson"),
        ("U", "icircumflex", 1, "glyphe", "plancher"),
        ("Uacute", "icircumflex", 1, "glyphe", "plancher"),
        ("Ucircumflex", "icircumflex", 1, "glyphe", "plancher"),
        ("Udieresis", "icircumflex", 1, "glyphe", "plancher"),
        ("Ugrave", "icircumflex", 1, "glyphe", "plancher"),
    ],
    "ExtraBold Italic": [
        ("Acircumflex", "x", 35, "glyphe", "atkinson"),
        ("Adieresis", "x", 35, "glyphe", "atkinson"),
        ("Agrave", "x", 35, "glyphe", "atkinson"),
        ("Agrave", "ydieresis", -28, "glyphe", "plancher"),
        ("Aring", "X", 57, "glyphe", "plancher"),
        ("Aring", "x", 35, "glyphe", "atkinson"),
        ("Aring", "y", -28, "glyphe", "plancher"),
        ("Aring", "ydieresis", -28, "glyphe", "plancher"),
        ("K", "Icircumflex", 14, "groupe", "plancher"),
        ("K", "idieresis", 23, "groupe", "au-dela d'atkinson"),
        ("K", "j", 5, "groupe", "plancher"),
        ("V", "Icircumflex", 4, "glyphe", "plancher"),
    ],
}
