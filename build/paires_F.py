"""Le crenage du F, paire par paire et master par master. GENERE, ne pas editer a la main.

Produit par `inventaire_F.py --ecrire`, qui regenere lui-meme les deux sources
sous `TEMOIN_SANS_APPROCHES=1`. **Le producteur annonce ici jusqu'au
quarante-cinquieme tour, `inventaire_F_haut.py --ecrire`, n'a jamais existe** :
ce fichier-la est le GARDE-FOU, qui cherche les paires rendues plus serrees
qu'Atkinson, quand cette table referme les paires ouvertes. Deux signes opposes,
point ouvert 80.

**Pourquoi cette table remplace l'approche du glyphe.** Le vingt-troisieme tour
avait retenu une approche de -100 sur la chasse du F, validee par un garde-fou
qui mesurait le couloir de la ligne de base a la hauteur d'x. La barre haute du F
monte a 668 et le point du i a 714 : tout ce qui se passe au-dessus de 496 etait
invisible. Mesure du vingt-quatrieme tour : l'approche laissait 8 unites entre la
barre du F et le point du i, contre 106 dans Atkinson, et **six paires de
capitales se touchaient reellement dans le binaire servi**, FI FT FV FW FX FY,
verifie par rasterisation.

**Comment chaque valeur est obtenue.** `approches.paire_bornee` prend le plus
petit de deux nombres : ce que la coupe a ouvert, mesure sur la bande de
jugement, et ce qu'on peut refermer sans passer sous le couloir d'Atkinson,
mesure sur la bande pleine. Devant une lettre qui monte, le second vaut zero et
la paire n'entre pas dans la table. Rien n'est choisi.

**Les valeurs sont TOTALES et non des ajustements.** Elles valent le crenage
d'Atkinson plus ce qu'il faut refermer, parce qu'elles s'ecrivent en exception
glyphe-glyphe, qui remplace et ne s'ajoute pas. Cette table passe la premiere des
trois dans `approches.appliquer`, donc sa base est bien Atkinson -- c'est
l'inverse de `paires_bouts.py`, qui part du crenage de Temoin.

**Elles sont ecrites en exception glyphe-glyphe et non par groupe.** Un trema
monte et limite ce qu'on peut refermer : sur la cle de groupe, `odieresis`
ramenerait F+o de -124 a -90 et `ydieresis` ramenerait F+v de -100 a -32.

**L'arrondi va vers zero**, comme celui des bouts : la contrainte est un plafond,
et arrondir au plus proche referme parfois une demi-unite de plus que la borne ne
permet. C'est le seul ecart avec la table du vingt-quatrieme tour sur les
lettres, une unite dans le sens plus lache.

**Ce que la regeneration du quarante-cinquieme tour change.** 66 paires
F+chiffre entrent, les dix chiffres etant entres dans `VOISINS_F` au tour
precedent : c'est le point ouvert 80, jusqu'a -168 sur `F+four` en Bold Italic.
Et **`F+t` sort de la table dans les quatre masters clairs** : sa borne vaut
aujourd'hui -3,6 en ExtraLight et +3,1 au Regular, donc il n'y a plus rien a
refermer. Les -43 et -23 qu'elle portait ont ete mesures quand le t culminait a
620 ; `coupe.allonge` l'a monte a 690 au trente-deuxieme tour et le couloir s'est
resserre tout seul. L'entree etait donc plus serree que la borne depuis douze
tours, et aucun controle ne pouvait le dire : la section 2 de `check_approches`
cherche les paires laissees OUVERTES.

Ecrite en clair et non calculee a l'execution : le bac a sable ne peut pas
toujours cloner la source amont, et un controle qui n'a pas pu lire sa source ne
doit rien conclure.
"""

PAIRES_F = {
    "ExtraLight": {
        "A": -172, "AE": -202, "Acircumflex": -172, "Adieresis": -172, "Agrave": -172,
        "C": -113, "Cacute": -113, "Ccaron": -113, "Ccedilla": -113, "Cdotaccent": -113,
        "G": -113, "O": -113, "OE": -113, "Ocircumflex": -113, "Odieresis": -113, "Q": -113,
        "c": -119, "ccedilla": -119, "d": -118, "e": -119, "eacute": -119,
        "ecircumflex": -119, "edieresis": -103, "egrave": -99, "eight": -51, "five": -37,
        "four": -122, "g": -118, "guillemetleft": -122, "m": -105, "n": -105, "nine": -76,
        "o": -119, "ocircumflex": -119, "odieresis": -97, "oe": -119, "p": -105,
        "parenleft": -88, "q": -118, "r": -105, "s": -105, "six": -107, "u": -105,
        "ucircumflex": -105, "udieresis": -57, "ugrave": -53, "v": -105, "w": -105,
        "x": -105, "y": -105, "ydieresis": -29, "z": -122, "zero": -104,
    },
    "Regular": {
        "A": -178, "AE": -208, "Acircumflex": -178, "Adieresis": -178, "Agrave": -178,
        "C": -107, "Cacute": -107, "Ccaron": -107, "Ccedilla": -107, "Cdotaccent": -107,
        "G": -108, "O": -108, "OE": -107, "Ocircumflex": -108, "Odieresis": -108, "Q": -108,
        "S": -29, "T": -29, "Z": -29, "a": -111, "acircumflex": -80, "adieresis": -60,
        "ae": -111, "agrave": -68, "c": -123, "ccedilla": -123, "colon": -99, "d": -122,
        "e": -124, "eacute": -124, "ecircumflex": -117, "edieresis": -97, "egrave": -104,
        "eight": -75, "five": -37, "four": -128, "g": -121, "guillemetleft": -128,
        "icircumflex": 1, "m": -99, "n": -99, "nine": -68, "o": -123, "ocircumflex": -110,
        "odieresis": -90, "oe": -123, "one": -29, "p": -99, "parenleft": -89, "q": -122,
        "question": -29, "r": -99, "s": -100, "semicolon": -99, "six": -97, "three": -29,
        "two": -29, "u": -99, "ucircumflex": -77, "udieresis": -57, "ugrave": -64, "v": -99,
        "w": -99, "x": -99, "y": -99, "ydieresis": -31, "z": -128, "zero": -89,
    },
    "Bold": {
        "A": -204, "AE": -238, "Acircumflex": -204, "Adieresis": -204, "Agrave": -204,
        "C": -98, "Cacute": -98, "Ccaron": -98, "Ccedilla": -98, "Cdotaccent": -98,
        "G": -100, "O": -103, "OE": -99, "Ocircumflex": -103, "Odieresis": -103, "Q": -103,
        "S": -50, "T": -50, "Z": -50, "a": -80, "acircumflex": -43, "ae": -82,
        "agrave": -45, "c": -133, "ccedilla": -133, "colon": -97, "d": -129, "e": -135,
        "eacute": -135, "ecircumflex": -106, "edieresis": -92, "egrave": -114,
        "eight": -126, "f": -99, "five": -38, "four": -155, "g": -127,
        "guillemetleft": -156, "hyphen": -130, "i": -58, "icircumflex": -13, "m": -99,
        "n": -99, "nine": -59, "o": -132, "ocircumflex": -97, "odieresis": -83, "oe": -132,
        "one": -35, "p": -99, "parenleft": -90, "q": -130, "question": -47,
        "quotedblleft": -58, "quoteright": -24, "r": -99, "s": -108, "semicolon": -97,
        "six": -89, "t": -90, "three": -48, "two": -48, "u": -99, "ucircumflex": -69,
        "udieresis": -55, "ugrave": -77, "v": -94, "w": -96, "x": -89, "y": -94,
        "ydieresis": -35, "z": -104, "zero": -83,
    },
    "ExtraBold": {
        "A": -208, "AE": -244, "Acircumflex": -208, "Adieresis": -208, "Agrave": -208,
        "C": -97, "Cacute": -97, "Ccaron": -97, "Ccedilla": -97, "Cdotaccent": -97,
        "G": -98, "O": -100, "OE": -98, "Ocircumflex": -100, "Odieresis": -100, "Q": -100,
        "S": -53, "T": -54, "Z": -54, "a": -97, "acircumflex": -55, "adieresis": -41,
        "ae": -98, "agrave": -65, "c": -133, "ccedilla": -133, "colon": -97, "d": -130,
        "e": -136, "eacute": -136, "ecircumflex": -105, "edieresis": -90, "egrave": -114,
        "eight": -132, "f": -99, "five": -38, "four": -153, "g": -128,
        "guillemetleft": -154, "hyphen": -130, "i": -61, "icircumflex": -15, "m": -99,
        "n": -99, "nine": -58, "o": -133, "ocircumflex": -95, "odieresis": -80, "oe": -133,
        "one": -35, "p": -99, "parenleft": -90, "q": -131, "question": -48,
        "quotedblleft": -66, "quoteright": -26, "r": -99, "s": -110, "semicolon": -97,
        "six": -88, "t": -91, "three": -47, "two": -47, "u": -99, "ucircumflex": -70,
        "udieresis": -55, "ugrave": -79, "v": -93, "w": -95, "x": -86, "y": -92,
        "ydieresis": -36, "z": -107, "zero": -83,
    },
    "ExtraLight Italic": {
        "A": -167, "AE": -217, "Acircumflex": -167, "Adieresis": -167, "Agrave": -167,
        "C": -122, "Cacute": -122, "Ccaron": -122, "Ccedilla": -122, "Cdotaccent": -122,
        "G": -120, "O": -121, "OE": -116, "Ocircumflex": -121, "Odieresis": -121, "Q": -121,
        "U": -27, "Ucircumflex": -27, "Udieresis": -27, "Ugrave": -27, "Z": -20, "ae": -30,
        "c": -124, "ccedilla": -124, "d": -123, "e": -125, "eacute": -125,
        "ecircumflex": -125, "edieresis": -88, "egrave": -91, "eight": -58, "five": -36,
        "four": -137, "g": -128, "guillemetleft": -137, "m": -118, "n": -118, "nine": -50,
        "o": -124, "ocircumflex": -124, "odieresis": -92, "oe": -124, "p": -118,
        "parenleft": -90, "q": -123, "r": -118, "s": -122, "six": -99, "u": -118,
        "ucircumflex": -111, "udieresis": -54, "ugrave": -57, "v": -117, "w": -117,
        "x": -117, "y": -117, "ydieresis": -22, "z": -137, "zero": -93,
    },
    "Italic": {
        "A": -174, "AE": -225, "Acircumflex": -174, "Adieresis": -174, "Agrave": -174,
        "C": -106, "Cacute": -106, "Ccaron": -106, "Ccedilla": -106, "Cdotaccent": -106,
        "G": -105, "O": -105, "OE": -104, "Ocircumflex": -105, "Odieresis": -105, "Q": -105,
        "S": -50, "T": -33, "U": -27, "Ucircumflex": -27, "Udieresis": -27, "Ugrave": -27,
        "Z": -33, "a": -120, "acircumflex": -77, "adieresis": -49, "ae": -120,
        "agrave": -63, "c": -128, "ccedilla": -128, "colon": -117, "d": -127, "e": -129,
        "eacute": -129, "ecircumflex": -107, "edieresis": -79, "egrave": -93, "eight": -86,
        "five": -37, "four": -145, "g": -131, "guillemetleft": -145, "icircumflex": -4,
        "m": -112, "n": -112, "nine": -52, "o": -128, "ocircumflex": -108, "odieresis": -81,
        "oe": -128, "one": -33, "p": -112, "parenleft": -90, "q": -127, "question": -30,
        "r": -112, "s": -117, "semicolon": -117, "six": -90, "three": -33, "two": -33,
        "u": -112, "ucircumflex": -71, "udieresis": -43, "ugrave": -57, "v": -112,
        "w": -112, "x": -112, "y": -112, "ydieresis": -22, "z": -145, "zero": -84,
    },
    "Bold Italic": {
        "A": -195, "AE": -262, "Acircumflex": -195, "Adieresis": -195, "Agrave": -195,
        "C": -92, "Cacute": -92, "Ccaron": -92, "Ccedilla": -92, "Cdotaccent": -92,
        "G": -92, "O": -93, "OE": -93, "Ocircumflex": -93, "Odieresis": -93, "Q": -93,
        "S": -64, "T": -57, "U": -27, "Ucircumflex": -27, "Udieresis": -27, "Ugrave": -27,
        "Z": -57, "a": -101, "acircumflex": -49, "adieresis": -25, "ae": -99, "agrave": -56,
        "c": -138, "ccedilla": -138, "colon": -117, "d": -138, "e": -139, "eacute": -139,
        "ecircumflex": -94, "edieresis": -70, "egrave": -101, "eight": -126, "f": -93,
        "five": -37, "four": -180, "g": -139, "guillemetleft": -180, "hyphen": -152,
        "i": -55, "icircumflex": -18, "m": -117, "n": -117, "nine": -56, "o": -138,
        "ocircumflex": -90, "odieresis": -65, "oe": -138, "one": -40, "p": -117,
        "parenleft": -89, "q": -138, "question": -49, "quotedblleft": -57,
        "quoteright": -20, "r": -117, "s": -123, "semicolon": -117, "six": -86, "t": -98,
        "three": -51, "two": -51, "u": -117, "ucircumflex": -74, "udieresis": -50,
        "ugrave": -81, "v": -112, "w": -113, "x": -106, "y": -111, "ydieresis": -25,
        "z": -122, "zero": -80,
    },
    "ExtraBold Italic": {
        "A": -200, "AE": -265, "Acircumflex": -200, "Adieresis": -200, "Agrave": -200,
        "C": -91, "Cacute": -91, "Ccaron": -91, "Ccedilla": -91, "Cdotaccent": -91,
        "G": -91, "O": -92, "OE": -92, "Ocircumflex": -92, "Odieresis": -92, "Q": -92,
        "S": -64, "T": -61, "U": -27, "Ucircumflex": -27, "Udieresis": -27, "Ugrave": -27,
        "Z": -61, "a": -113, "acircumflex": -59, "adieresis": -36, "ae": -112,
        "agrave": -70, "c": -138, "ccedilla": -138, "colon": -116, "d": -137, "e": -140,
        "eacute": -140, "ecircumflex": -91, "edieresis": -69, "egrave": -103, "eight": -131,
        "f": -94, "five": -37, "four": -178, "g": -140, "guillemetleft": -179,
        "hyphen": -151, "i": -63, "icircumflex": -20, "m": -117, "n": -117, "nine": -58,
        "o": -139, "ocircumflex": -88, "odieresis": -65, "oe": -138, "one": -40, "p": -117,
        "parenleft": -89, "q": -137, "question": -48, "quotedblleft": -61,
        "quoteright": -22, "r": -117, "s": -124, "semicolon": -116, "six": -85, "t": -100,
        "three": -51, "two": -51, "u": -117, "ucircumflex": -73, "udieresis": -51,
        "ugrave": -84, "v": -110, "w": -112, "x": -103, "y": -110, "ydieresis": -26,
        "z": -125, "zero": -80,
    },
}
