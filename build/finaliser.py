#!/usr/bin/env python3
"""Finalisation des variables Temoin, ce que la chaine du projet ne posait pas.

DECISION DU SOIXANTE-DEUXIEME TOUR. Le point 10 a ete tranche apres mesure : la
chaine du projet fait foi, `fontmake` direct, et `gftools` reste l'ETALON DE
MESURE sans entrer dans la chaine de publication. Ce module pose ce que
`gftools-fix-font` et `gftools-gen-stat` posaient, et rien de plus : la cible a
ete relevee champ par champ sur leur sortie, reproductible par
`build/config-temoin.yaml`.

CE QUI N'EST PAS ICI, et pourquoi : l'aplatissement des 36 composites
imbriques. C'est un filtre de `fontmake`, pas de gftools, donc il se demande a
la compilation et non apres :

    python3 -m fontmake -g Temoin.glyphs -o variable \\
        --output-path $TEMOIN_BUILD/Temoin-wght.ttf \\
        --no-production-names --filter FlattenComponentsFilter

Un drapeau oublie ne se voit pas : `check_final.py` compte donc les composites
imbriques sur le binaire, pour que l'oubli crie au lieu de passer.

LA CIBLE CHIFFREE, ET POURQUOI ELLE NE SUFFIT PAS. `fontbakery
check-googlefonts` doit rendre 2 FAIL et 14 ERROR, le score d'Atkinson livre,
contre 15 et 16 avant ce module. Mais AUCUN controle de Font Bakery ne voit
manquer les sept noms PostScript d'instance : les deux sorties passent
`opentype.varfont.valid_nameids` et `googlefonts.fvar_instances`. La cible
exterieure est donc necessaire et pas suffisante, et le critere qui mord est
l'egalite avec la sortie gftools.

Lancement :

    TEMOIN_BUILD=/tmp/bN python3 finaliser.py        # les deux variables
    python3 finaliser.py un.ttf deux.ttf             # ou des chemins explicites

Le fichier est ECRIT SOUS SON NOM CANONIQUE, `Temoin[wght].ttf` et
`Temoin-Italic[wght].ttf`, et l'entree est laissee en place. `subset.py` lit le
nom canonique.
"""

import os
import re
import sys

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram

# --------------------------------------------------------------- la cible
# Chaque constante est relevee sur la sortie de `gftools builder`, jamais
# devinee ni reprise d'une documentation.

# `gasp` : un seul intervalle, jusqu'a 65535 ppem, drapeau 15 -- lissage et
# grille dans les deux sens. Version 1.
GASP_RANGES = {65535: 15}
GASP_VERSION = 1

# `prep` : sept octets, b801ff85b0048d. Lu en clair plutot que recopie en
# hexadecimal, pour qu'il soit relisible : SCANCTRL a 511 active le controle de
# dropout a toutes les tailles, SCANTYPE a 4 choisit le dropout INTELLIGENT.
# C'est ce que `smart_dropout` de Font Bakery exige.
PREP_ASSEMBLY = ["PUSHW[ ]", "511", "SCANCTRL[ ]", "PUSHB[ ]", "4",
                 "SCANTYPE[ ]"]

# Les sept graisses de l'axe, dans l'ordre. Les noms sont ceux des instances
# `fvar`, donc ceux du registre d'axes de Google Fonts, et c'est pour cela que
# `gftools-gen-stat` sait deduire la table sans bloc `stat:`.
GRAISSES = [(200, "ExtraLight"), (300, "Light"), (400, "Regular"),
            (500, "Medium"), (600, "SemiBold"), (700, "Bold"),
            (800, "ExtraBold")]

# La valeur liee du gras : le systeme sait alors quel master le bouton Gras
# doit viser depuis le Regular. Meme mecanique sur l'axe `ital`, ou le ROMAIN
# porte la valeur liee vers l'italique -- et pas l'inverse, releve sur la
# sortie gftools : l'italique porte une valeur de Format 1 sans lien.
REGULIER, GRAS_LIE = 400, 700
DRAPEAU_ELIDABLE = 0x2

# `ElidedFallbackNameID` a 2 : quand tous les noms d'axe sont elides, le nom de
# style a afficher est celui de la sous-famille.
ELIDE_PAR_DEFAUT = 2

BUILD = os.environ.get("TEMOIN_BUILD", "/tmp/build-temoin")
ENTREES = ("Temoin-wght.ttf", "Temoin-Italic-wght.ttf")

# Les enregistrements de nom se posent sur la SEULE plateforme que la sortie
# gftools emploie pour ses ajouts : Windows. Ecrire aussi sur Macintosh, ce que
# `addName` et `buildStatTable` font par defaut, ajoute un enregistrement par
# nom sans qu'aucune table n'y renvoie.
WINDOWS = (3, 1, 0x409)

# Le nom d'affichage ACCENTUE, point ouvert 7, tranche au soixante-cinquieme
# tour. Il se pose comme un nom LOCALISE, pas comme un ID 16 : le guide Google
# Fonts interdit tout caractere non ASCII dans un nom de famille, et un ID 16
# accentue fait passer Temoin de 0 a 8 FAIL -- `family_name_compliance`, que
# rien ne leve, plus `match_familyname_fullfont`, `canonical_filename` et
# `font_names`, mesures avant d'ecrire. La voie localisee en coute ZERO et
# rend le meme affichage : un systeme en francais lit l'entree francaise, tout
# le reste lit l'anglaise, et le nom PostScript n'est pas touche.
FRANCAIS = (3, 1, 0x40C)
SANS_ACCENT = "Temoin"
ACCENTUE = "T\u00e9moin"


# ------------------------------------------------------------------ lecture

def _nom(font, ident, defaut=None):
    """Rend la chaine Windows d'un identifiant de nom, ou `defaut`."""
    for r in font["name"].names:
        if (r.nameID == ident and (r.platformID, r.platEncID, r.langID)
                == WINDOWS):
            return str(r)
    for r in font["name"].names:          # repli sur n'importe quelle plateforme
        if r.nameID == ident:
            return str(r)
    return defaut


def _ident_reutilisable(font, chaine):
    """L'identifiant d'un nom deja present, ou None.

    SANS CE RESOLVEUR, `buildStatTable` cree un enregistrement neuf par nom de
    valeur, et le fichier porte 55 enregistrements pour 32 a la cible gftools :
    `Weight`, `ExtraLight`, `Light`, `Medium`, `SemiBold`, `Bold`, `ExtraBold`
    et `Regular` existent tous deja, comme nom d'axe ou de sous-famille
    d'instance dans `fvar`. Mesure du gaspillage : 616 octets.

    Seuls les identifiants a partir de 256 sont reutilises. Les identifiants
    reserves, 1 pour la famille et 2 pour la sous-famille, ne se recyclent pas :
    un nom d'axe pose sur l'identifiant 2 serait lu comme la sous-famille.
    """
    trouves = []
    for r in font["name"].names:
        if (r.nameID >= 256 and str(r) == chaine
                and (r.platformID, r.platEncID, r.langID) == WINDOWS):
            trouves.append(r.nameID)
    return min(trouves) if trouves else None


def _nom_ou_ident(font, chaine):
    """La chaine, ou l'identifiant existant : `buildStatTable` accepte les deux.

    `otlLib.builder._addName` rend l'entier tel quel quand on lui passe un
    entier, et cree un enregistrement quand on lui passe une chaine.
    """
    ident = _ident_reutilisable(font, chaine)
    return ident if ident is not None else chaine


def est_italique(font):
    """Italique ou romain, decide sur TROIS temoins concordants.

    Un seul champ ne suffit pas : `post.italicAngle` peut valoir 0 sur un
    italique mal compile, et `macStyle` est un drapeau qu'un outil peut oublier.
    Les trois sont concordants sur les binaires du projet -- angle -12,0,
    `macStyle` bit 1, `fsSelection` bit 0 -- et un desaccord est une anomalie
    qu'il vaut mieux lever que trancher en silence.
    """
    angle = font["post"].italicAngle != 0
    mac = bool(font["head"].macStyle & 0b10)
    fs = bool(font["OS/2"].fsSelection & 0b1)
    if len({angle, mac, fs}) != 1:
        raise RuntimeError(
            f"italique indecidable : post.italicAngle={font['post'].italicAngle}, "
            f"head.macStyle={font['head'].macStyle}, "
            f"OS/2.fsSelection={font['OS/2'].fsSelection}. Les trois temoins "
            f"doivent s'accorder.")
    return angle


def prefixe_postscript(font):
    """Le prefixe PostScript des variations, l'identifiant de nom 25.

    Regle relevee sur la sortie gftools : le nom PostScript prive de son tiret,
    et prive de `Regular` quand c'est le style par defaut. `Temoin-Regular`
    donne `Temoin`, `Temoin-Italic` donne `TemoinItalic`.
    """
    ps = _nom(font, 6)
    if ps is None:
        raise RuntimeError("identifiant de nom 6 absent : pas de nom PostScript")
    brut = ps.replace("-", "")
    return re.sub(r"Regular$", "", brut) or brut


def famille_postscript(font):
    """La famille PostScript, ce qui precede le tiret de l'identifiant 6."""
    return _nom(font, 6).split("-")[0]


def nom_canonique(font):
    """`Temoin[wght].ttf` ou `Temoin-Italic[wght].ttf`.

    Le nom de fichier est un critere de Font Bakery, et deux de ses huit refus
    en decoulaient : `canonical_filename` et
    `family.italics_have_roman_counterparts`, ce dernier ne trouvant pas le
    romain d'un italique dont le nom ne suit pas la convention.
    """
    famille = _nom(font, 16) or _nom(font, 1)
    tige = re.sub(r"[^A-Za-z0-9]", "", famille)
    return f"{tige}{'-Italic' if est_italique(font) else ''}[wght].ttf"


def composites_imbriques(font):
    """Les composites dont un composant est lui-meme un composite.

    Mesure et non lecture d'un drapeau : c'est ce qui fait crier l'oubli de
    `--filter FlattenComponentsFilter`, que ce module ne peut pas rattraper.
    """
    if "glyf" not in font:
        return []
    g = font["glyf"]
    trouves = []
    for nom in font.getGlyphOrder():
        gl = g[nom]
        if not gl.isComposite():
            continue
        if any(g[c.glyphName].isComposite() for c in gl.components):
            trouves.append(nom)
    return trouves


# ------------------------------------------------------------------ gestes

def poser_gasp(font):
    t = newTable("gasp")
    t.version = GASP_VERSION
    t.gaspRange = dict(GASP_RANGES)
    font["gasp"] = t


def poser_prep(font):
    """Pose le programme, ou le laisse tel quel s'il y en a deja un.

    Un `prep` existant vient d'un autre hinting, et l'ecraser detruirait du
    travail sans le dire. Le cas n'arrive pas aujourd'hui -- `fontmake` direct
    n'en pose aucun -- mais un jour ou il arriverait, mieux vaut un refus qu'un
    ecrasement silencieux.
    """
    if "prep" in font and font["prep"].program.getBytecode():
        raise RuntimeError(
            "une table `prep` non vide existe deja : elle vient d'un autre "
            "hinting et ce module ne l'ecrase pas.")
    t = newTable("prep")
    p = ttProgram.Program()
    p.fromAssembly(PREP_ASSEMBLY)
    t.program = p
    font["prep"] = t



# --------------------------------------- reconnaissance et fournisseur, 64e tour

# La clause 4 de l'OFL interdit d'employer le nom des auteurs d'origine pour
# promouvoir une version modifiee, AVEC UNE EXCEPTION EXPLICITE : reconnaitre
# leur contribution. Le name ID 10, `description`, etait ABSENT du binaire ; il
# porte maintenant cette reconnaissance, quand les champs createur et fabricant
# sont passes a l'OXA au soixante-quatrieme tour.
DESCRIPTION = (
    "Temoin est une version modifiee d'Atkinson Hyperlegible Next, dessinee "
    "pour le Braille Institute of America, qui n'a ni approuve ni soutenu "
    "cette version. Modifications par l'OXA."
)
# 200 CARACTERES MAXIMUM, et c'est mesure : `googlefonts/name/
# description_max_length` rend WARN au-dela. Le premier jet nommait les cinq
# auteurs d'Atkinson et les six modifications, pour 464 caracteres. La
# reconnaissance nominative des auteurs vit donc dans `README.md` et dans
# `OFL.txt`, que la clause 2 fait accompagner toute redistribution.
assert len(DESCRIPTION) <= 200, len(DESCRIPTION)

# Identifiant de fournisseur. `NONE` etait celui d'Atkinson, herite sans etre
# choisi. `OXA ` n'est PAS enregistre aupres de Microsoft, et `googlefonts/
# vendor_id` rend donc WARN [unknown] -- mais il le rendait DEJA sur `NONE`,
# mesure au soixante-quatrieme tour avant l'ecriture. Le critere exterieur ne
# regresse pas, et le champ dit desormais quelque chose de vrai.
VENDOR_ID = "OXA "


def poser_description(font):
    font["name"].setName(DESCRIPTION, 10, *WINDOWS)
    return DESCRIPTION


def poser_vendor_id(font):
    """Pose l'identifiant de fournisseur, dans OS/2 ET dans le name ID 3.

    Le name ID 3, l'identifiant unique, est bati par `fontmake` sous la forme
    "version;fournisseur;nomPostScript" AVANT que ce module ne tourne : il
    portait donc "1.000;NONE;Temoin-Regular", avec le `NONE` herite d'Atkinson,
    alors qu'OS/2 disait deja autre chose. Deux champs qui se contredisent sur
    la meme question valent moins qu'un seul.
    """
    font["OS/2"].achVendID = VENDOR_ID
    ident = font["name"].getDebugName(3)
    if ident and ";NONE;" in ident:
        font["name"].setName(ident.replace(";NONE;", ";%s;" % VENDOR_ID.strip()),
                             3, *WINDOWS)
    return VENDOR_ID


def poser_noms_localises(font):
    """Pose la famille et le nom complet en francais accentue.

    ELLE REFUSE DE SE TAIRE, comme `make_temoin.poser_identite` : si l'entree
    anglaise n'est pas celle qu'on attend, c'est que le nommage a change en
    amont et que ce module ecrirait un nom faux a cote d'un nom juste. Le
    quinzieme piege du projet dit pourquoi cela se verifie ici et non sur la
    source : une ecriture qui ne leve pas n'est pas une ecriture qui a eu lieu.

    Les identifiants 1 et 4 seulement. L'identifiant 6, le nom PostScript, doit
    rester en ASCII pur et n'est pas touche ; les identifiants 16 et 17 restent
    absents, par la mesure ci-dessus.
    """
    famille = _nom(font, 1)
    if famille != SANS_ACCENT:
        raise ValueError(
            "la famille amont vaut %r et non %r : le nommage a change, "
            "le nom localise n'est pas ecrit" % (famille, SANS_ACCENT))
    complet = _nom(font, 4)
    if not complet or not complet.startswith(SANS_ACCENT):
        raise ValueError(
            "le nom complet amont vaut %r et ne commence pas par %r"
            % (complet, SANS_ACCENT))
    complet_fr = ACCENTUE + complet[len(SANS_ACCENT):]
    font["name"].setName(ACCENTUE, 1, *FRANCAIS)
    font["name"].setName(complet_fr, 4, *FRANCAIS)
    return ACCENTUE, complet_fr


def poser_nom25(font):
    prefixe = prefixe_postscript(font)
    font["name"].setName(prefixe, 25, *WINDOWS)
    return prefixe


def poser_noms_dinstance(font):
    """Un nom PostScript sur chacune des sept instances de `fvar`.

    C'EST L'AJOUT QU'AUCUN CONTROLE EXTERIEUR NE RECLAME : les deux sorties
    passent `opentype.varfont.valid_nameids`, `duplicate_instance_names` et
    `googlefonts.fvar_instances`, avec ou sans ces noms. La sortie du projet
    portait `postscriptNameID = 65535` partout, c'est-a-dire aucun nom, donc une
    application qui instancie une graisse nommee n'avait pas de nom PostScript
    a lui donner.
    """
    famille = famille_postscript(font)
    poses = []
    for inst in font["fvar"].instances:
        style = _nom(font, inst.subfamilyNameID)
        if style is None:
            raise RuntimeError(
                f"instance sans nom de sous-famille lisible : "
                f"subfamilyNameID={inst.subfamilyNameID}")
        ps = f"{famille}-{style.replace(' ', '')}"
        ident = _ident_reutilisable(font, ps)
        # `addName` rend l'identifiant, un entier, et non l'enregistrement.
        # `platforms` restreint a Windows : sans cela `addName` pose AUSSI un
        # enregistrement Macintosh (1, 0, 0) par nom, et le fichier porte dix a
        # quinze enregistrements de plus que la cible gftools, qui n'ecrit que
        # sur Windows. Mesure : 41 et 51 enregistrements contre 32 et 37.
        inst.postscriptNameID = (ident if ident is not None
                                 else font["name"].addName(ps, (WINDOWS,)))
        poses.append(ps)
    return poses


def poser_stat(font):
    """La STAT complete, deux axes et huit valeurs.

    La sortie de `fontmake` direct porte UN axe et ZERO valeur nommee, ce qui
    fait plus qu'echouer un controle : `name.family_and_style_max_length` de
    Font Bakery LEVE un AttributeError dessus, faute d'`AxisValue`. Un controle
    qui plante est un non mesure qui ne dit meme pas son nom.

    Les noms de valeur sont ceux des instances `fvar`, donc `buildStatTable`
    reutilise les enregistrements existants au lieu d'en creer des doubles.
    C'est ce que fait `gftools-gen-stat`, qui reutilise jusqu'a l'identifiant 2
    quand le nom de valeur est celui de la sous-famille.
    """
    ref = lambda chaine: _nom_ou_ident(font, chaine)

    valeurs_wght = []
    for valeur, nom in GRAISSES:
        entree = {"value": valeur, "name": ref(nom)}
        if valeur == REGULIER:
            entree["flags"] = DRAPEAU_ELIDABLE
            entree["linkedValue"] = GRAS_LIE
        valeurs_wght.append(entree)

    if est_italique(font):
        # Format 1, sans lien : c'est le ROMAIN qui pointe vers l'italique.
        valeurs_ital = [{"value": 1, "name": ref("Italic")}]
    else:
        valeurs_ital = [{"value": 0, "name": ref("Roman"),
                         "flags": DRAPEAU_ELIDABLE, "linkedValue": 1}]

    buildStatTable(font, [
        {"tag": "wght", "name": ref("Weight"), "ordering": 0,
         "values": valeurs_wght},
        {"tag": "ital", "name": ref("Italic"), "ordering": 1,
         "values": valeurs_ital},
    ], elidedFallbackName=ELIDE_PAR_DEFAUT, macNames=False)


# -------------------------------------------------------------------- main

def finaliser(chemin, dest=None):
    font = TTFont(chemin)
    imbriques = composites_imbriques(font)
    poser_gasp(font)
    poser_prep(font)
    prefixe = poser_nom25(font)
    instances = poser_noms_dinstance(font)
    poser_stat(font)
    poser_description(font)
    poser_vendor_id(font)
    localises = poser_noms_localises(font)
    sortie = dest or os.path.join(os.path.dirname(os.path.abspath(chemin)),
                                  nom_canonique(font))
    font.save(sortie)
    return sortie, prefixe, instances, imbriques, localises


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    chemins = args or [os.path.join(BUILD, n) for n in ENTREES]
    manquants = [c for c in chemins if not os.path.exists(c)]
    if manquants:
        print("NON MESURE : rien n'a ete finalise, ces entrees manquent :")
        for c in manquants:
            print(f"  {c}")
        print("  Ce n'est pas un succes. Compiler d'abord, avec "
              "--no-production-names ET --filter FlattenComponentsFilter.")
        return 2
    code = 0
    for chemin in chemins:
        sortie, prefixe, instances, imbriques, localises = finaliser(chemin)
        print(f"{os.path.basename(chemin)} -> {os.path.basename(sortie)} "
              f"({os.path.getsize(sortie)} octets)")
        print(f"   gasp {GASP_RANGES}, prep {len(PREP_ASSEMBLY)} operations, "
              f"STAT 2 axes et {len(GRAISSES) + 1} valeurs")
        print(f"   nom 25 : {prefixe}")
        print(f"   instances : {instances[0]} ... {instances[-1]}")
        print(f"   noms francais : {localises[0]} / {localises[1]}")
        if imbriques:
            # Ce module ne sait PAS aplatir : le filtre vit dans fontmake, donc
            # un oubli se signale ici et se corrige a la compilation.
            print(f"   !! {len(imbriques)} composite(s) imbrique(s) : "
                  f"--filter FlattenComponentsFilter a ete oublie a la "
                  f"compilation. Exemples : {' '.join(imbriques[:4])}")
            code = 1
        else:
            print("   composites imbriques : aucun")
    return code


if __name__ == "__main__":
    sys.exit(main())
