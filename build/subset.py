#!/usr/bin/env python3
"""Sous-ensemblage web des variables Temoin.

Deux pieges connus, traites explicitement :
  - pyftsubset supprime les glyphes a suffixe (.tf, .slashless) tout en
    gardant les features qui les appellent : il faut les lister a la main ;
  - sans --glyph-names, la table post passe en 3.0 et toute verification
    par nom de glyphe echoue a tort. On les garde sur le banc d'essai.
"""

import shutil
import subprocess
import sys
import os

CHIFFRES = "zero one two three four five six seven eight nine".split()
LETTRES = "abcdefghijklmnopqrstuvwxyz"
ACCENTUEES = ("agrave acircumflex adieresis ccedilla eacute egrave ecircumflex "
              "edieresis icircumflex idieresis ocircumflex odieresis ugrave "
              "ucircumflex udieresis ydieresis ae oe").split()
# Les 44 petites capitales du lot 3. Sans cette liste, pyftsubset les supprime
# et ne laisse que les features smcp / c2sc, qui pointent alors dans le vide.
PC = [c + ".sc" for c in LETTRES] + [a + ".sc" for a in ACCENTUEES]

GLYPHES = ([c + ".tf" for c in CHIFFRES]
           + ["zero.slashless", "zero.tf.slashless"] + PC)

# SEPT COMBINANTS SONT SERVIS SANS QU'AUCUNE LETTRE SERVIE NE LES EMPLOIE, ET
# NICOLAS A TRANCHE DE LES GARDER. Trente-neuvieme tour, point ouvert 28 ferme.
#
#   brevecomb  caroncomb  ogonekcomb  ogonekcomb.case
#   brevecomb.case  caroncomb.case  macroncomb.case
#
# Ils ont un cmap, donc ils sont atteignables par saisie directe du caractere
# combinant : ce n'est pas du poids mort, c'est la composition libre -- une
# breve, un caron ou un ogonek pose sur une lettre quelconque. Le francais n'en
# a aucun usage ; le polonais, le tcheque et la transcription si, et la police
# est publiee sous OFL pour etre reutilisee hors du site.
#
# LE PRIX EST MESURE, PAS ESTIME : les retirer vaut -1 060 octets au romain et
# -932 en italique, soit environ 2 Ko sur la paire, mesures en les retirant
# vraiment du WOFF2 servi et en le recompressant, avec un temoin de resauvetage
# a +88 octets qui donne le bruit. Le repertoire passe de 311 a 304 glyphes.
#
# `macroncomb` N'EN FAIT PAS PARTIE, contre ce que le point 28 annoncait : le
# macron d'espacement U+00AF est servi et l'emploie comme composant, donc le
# sous-ensembleur le garde de toute facon. Le point comptait cinq combinants et
# il y en a quatre, plus trois variantes `.case`.
#
# NE PAS LES RETIRER PAR OPTIMISATION : c'est une decision, pas un oubli.
# `ss02` A EXISTE LE TEMPS D'UN TOUR, et il ne faut pas le remettre. Le titrage
# a d'abord ete compile en jeu stylistique sur 112 doubles `.ti` ; Nicolas a
# decide au quarantieme tour de FUSIONNER le corps et le titrage, donc il n'y a
# plus qu'un dessin par glyphe, plus de double et plus de feature. Voir
# `lot4.HORS_FUSION` et `make_temoin.add_fusion`.
FEATURES = ("calt,ss01,smcp,c2sc,tnum,pnum,frac,sups,ordn,case,locl,ccmp,"
            "kern,mark,mkmk,aalt")

ICI = os.path.dirname(os.path.abspath(__file__))

# Deux chemins absolus vivaient ici en dur, et la passation demandait de les
# corriger a chaque session : le repertoire de compilation change de nom et le
# dossier de travail est monte ailleurs d'une session a l'autre. Les deux se
# deduisent, donc ils se deduisent -- c'est un piege desamorce a la source
# plutot que documente une fois de plus.
#   TEMOIN_BUILD : le repertoire de compilation, a passer en variable
#   d'environnement puisque /tmp est vide entre deux sessions et qu'un
#   repertoire laisse par une session precedente appartient a un autre
#   utilisateur et ne peut pas etre ecrase.
BUILD = os.environ.get("TEMOIN_BUILD", "/tmp/build-temoin")
# La liste des caracteres vit maintenant a cote de ce fichier et non dans /tmp,
# qui disparait d'une session a l'autre. La precedente avait perdu le Y trema
# (U+0178) sans que rien ne le signale : HarfBuzz decomposait alors le
# caractere en Y + trema, ce qui court-circuitait c2sc et laissait un trema de
# taille de capitale au-dessus d'une petite capitale.
UNICODES = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "subset_unicodes.txt")

# Repertoire minimal a garantir : si l'un de ces caracteres manque au resultat,
# le sous-ensemblage a mange quelque chose d'utile au francais.
FRANCAIS = ("ÀÂÄÆÇÉÈÊËÎÏÔÖŒÙÛÜŸàâäæçéèêëîïôöœùûüÿ«»“”‘’…–—€°"
            " ’")
# Les polices servies vivent a cote des gabarits, qui sont le repertoire voisin
# de celui-ci. Deduit et non ecrit : ce chemin etait faux a chaque session.
#
# DEUX EMPLACEMENTS DEPUIS LE SOIXANTE-ET-ONZIEME TOUR, point ouvert 116. Le
# depot public range les fontes dans `fonts/`, a sa racine ; le dossier de
# travail les garde dans `gabarits/fonts/`, que le banc d'essai et ses pages
# lisent en relatif. Le premier des deux qui existe gagne, le depot d'abord :
# un clone du depot n'a jamais de `gabarits/`, et le dossier de travail n'a pas
# de `fonts/` a sa racine. `check_final` et `mesure_titrage` lisent ce DEST, et
# aucun autre chemin : les trois modules ne peuvent pas diverger.
def dossier_fontes():
    for d in (os.path.join(ICI, "..", "fonts"),
              os.path.join(ICI, "..", "gabarits", "fonts")):
        if os.path.isdir(d):
            return os.path.normpath(d)
    return os.path.normpath(os.path.join(ICI, "..", "gabarits", "fonts"))


DEST = dossier_fontes()

# L'AXE DU SERVI, point ouvert 3, tranche au soixante-huitieme tour et ecrit au
# soixante-et-onzieme. Le servi garde 400 a 800 : les gabarits emploient 400,
# 500, 600 et 700, et couper 200 retire 9,1 Ko a chaque WOFF2. 300 ne faisait
# rien gagner, n'etant pas un master ; 400-750 gagnait le double en perdant
# l'ExtraBold, ecarte. LA POLICE PUBLIEE GARDE 200-800 : seul le servi est
# reduit, et les TTF copies a cote de lui sortent de `finaliser` intacts.
# Mesure au soixante-huitieme tour : cinq instances nommees, STAT a six
# valeurs, gasp et prep intacts, 0,5 unite d'ecart de dessin au plus aux
# positions gardees, l'arrondi des deltas.
AXE_SERVI = (400, 400, 800)


def refuser_les_doubles(src):
    """Refuse un binaire qui porterait encore des doubles `.ti`.

    LA FUSION LES A SUPPRIMES, et leur retour signalerait une chaine a moitie
    revenue en arriere : des doubles compiles sans la feature qui les appelle
    sont du poids mort que rien n'atteint, et le sous-ensembleur les garderait
    en silence si la liste des glyphes les nommait.
    """
    from fontTools.ttLib import TTFont
    ti = [g for g in TTFont(src).getGlyphOrder() if g.endswith(".ti")]
    if ti:
        raise RuntimeError(
            f"{len(ti)} glyphe(s) `.ti` dans {src}, alors que la fusion du "
            "quarantieme tour les a supprimes. Relancer make_temoin.py.")


def subset(src, out, flavor="woff2"):
    refuser_les_doubles(src)
    cmd = [
        sys.executable, "-m", "fontTools.subset", src,
        "--unicodes-file=" + UNICODES,
        "--glyphs=" + ",".join(GLYPHES),
        "--layout-features=" + FEATURES,
        "--glyph-names",
        "--output-file=" + out,
        "--drop-tables+=DSIG",
        "--name-IDs=*",
        # SANS CETTE LIGNE, LE NOM LOCALISE DISPARAIT DU LIVRABLE. `--name-IDs`
        # choisit les identifiants, pas les langues : `fontTools.subset` ne
        # garde par defaut que l'anglais (0x0409), donc les entrees francaises
        # que `finaliser.poser_noms_localises` ecrit etaient supprimees ici, en
        # silence. Mesure au soixante-cinquieme tour : le TTF compile les
        # portait, le WOFF2 servi rendait 32 enregistrements de nom identiques
        # a ceux d'avant le geste, et le point 7 aurait ete annonce fait sur un
        # livrable qui ne le portait pas.
        "--name-languages=*",
    ]
    if flavor:
        cmd.append("--flavor=" + flavor)
    subprocess.run(cmd, check=True)
    limiter_axe(out)
    return os.path.getsize(out)


def limiter_axe(chemin):
    """Reduit l'axe `wght` du servi a AXE_SERVI, sur place.

    `instancer` apres le sous-ensemblage, comme la mesure du soixante-huitieme
    tour : il retire les instances hors plage et les valeurs de STAT qui vont
    avec, et garde le lien du Regular vers le Bold. Le WOFF2 reste un WOFF2, le
    format suit le fichier. Le jumeau TTF passe par ici aussi : il doit porter
    exactement ce que le servi porte.
    """
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    f = TTFont(chemin)
    lo, defaut, hi = AXE_SERVI
    instancer.instantiateVariableFont(f, {"wght": (lo, defaut, hi)},
                                      inplace=True)
    f.save(chemin)


def estampiller_css(fichiers):
    """Pose l'empreinte de chaque WOFF2 dans les url() de temoin.css.

    Le piege est connu du projet pour les feuilles de style — `http.server` laisse
    le navigateur servir depuis son cache — et il vaut aussi pour les polices,
    ce qui est pire : une mesure de largeur faite sur un binaire perime ne se
    voit pas, elle rend simplement de mauvais chiffres. Au vingt-quatrieme tour
    le navigateur a mesure l'ancien F pendant deux essais.

    L'empreinte est celle du contenu, pas une date : elle ne change que si le
    fichier change, donc un rechargement n'invalide rien inutilement.
    """
    import hashlib
    import re

    css = os.path.normpath(os.path.join(ICI, "..", "gabarits", "temoin.css"))
    if not os.path.exists(css):
        return
    with open(css, encoding="utf-8") as fh:
        texte = fh.read()
    avant = texte
    for chemin in fichiers:
        nom = os.path.basename(chemin)
        with open(chemin, "rb") as fh:
            emp = hashlib.sha1(fh.read()).hexdigest()[:8]
        texte = re.sub(r'url\("fonts/' + re.escape(nom) + r'(\?v=[0-9a-f]+)?"\)',
                       'url("fonts/' + nom + '?v=' + emp + '")', texte)
    if texte != avant:
        with open(css, "w", encoding="utf-8") as fh:
            fh.write(texte)
        print("   temoin.css estampille")


if __name__ == "__main__":
    ecrits = []
    # LES NOMS D'ENTREE SONT LES NOMS CANONIQUES depuis le soixante-deuxieme
    # tour : `finaliser.py` ecrit `Temoin[wght].ttf` et
    # `Temoin-Italic[wght].ttf`, et deux des huit refus de Font Bakery
    # decoulaient du nom de fichier -- `canonical_filename`, et
    # `family.italics_have_roman_counterparts`, qui ne trouvait pas le romain
    # d'un italique hors convention. Les crochets sont litteraux.
    for src, out in ((BUILD + "/Temoin[wght].ttf", DEST + "/Temoin.woff2"),
                     (BUILD + "/Temoin-Italic[wght].ttf",
                      DEST + "/Temoin-Italic.woff2")):
        taille = subset(src, out)
        print(f"{os.path.basename(out)} : {taille/1024:.1f} Ko")
        # Le meme sous-ensemble en TTF, pour la verification de shaping :
        # HarfBuzz ne decode pas le WOFF2 et renvoie du .notdef en silence.
        # Sans ce jumeau, toute preuve de substitution serait faite sur le
        # binaire non sous-ensemble, donc sur autre chose que ce qui est servi.
        jumeau = BUILD + "/" + os.path.basename(out).replace(".woff2", "-sub.ttf")
        subset(src, jumeau, flavor=None)
        print(f"   jumeau de controle : {jumeau}")

        from fontTools.ttLib import TTFont
        cm = TTFont(jumeau).getBestCmap()
        manque = [c for c in FRANCAIS if ord(c) not in cm]
        gl = set(TTFont(jumeau).getGlyphOrder())
        perdus = [g for g in GLYPHES if g not in gl]
        print(f"   francais manquant : "
              f"{' '.join(f'{c} U+{ord(c):04X}' for c in manque) or 'rien'}")
        print(f"   glyphes a suffixe perdus : {perdus or 'aucun'}")
        ecrits.append(out)
        # LES TTF PUBLIES, point ouvert 115 : le variable finalise, 200-800 et
        # repertoire complet, copie tel quel a cote du servi. C'est la meme
        # etape qui les pose, pour qu'un servi neuf ne cotoie jamais un TTF
        # d'une compilation precedente dans le depot.
        shutil.copy2(src, os.path.join(DEST, os.path.basename(src)))
        print(f"   TTF publie : {os.path.basename(src)}")

    estampiller_css(ecrits)
