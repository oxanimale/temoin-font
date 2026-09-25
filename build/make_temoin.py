#!/usr/bin/env python3
"""
Temoin, etape 2 : la chaine de production des deux sources.

Ajoute aux sources Atkinson Hyperlegible Next :
  - zero.slashless      : contreforme ovale recousue (voir zero_reconstruct.py)
  - zero.tf.slashless   : la meme, en chasse tabulaire
  - calt                : le zero se denude dans un groupe de chiffres
  - ss01                : zero non barre force partout
  - narrownbspace       : l'espace fine insecable U+202F
  - le lot 2, les approches, le lot 3 (petites capitales, smcp / c2sc)
  - le lot 4, la coupe de titrage, FUSIONNEE dans le dessin (`add_fusion`)
  - le bras du O, contour GREFFE dans la contreforme (`bras_O`), sur la seule
    source romaine et APRES le lot 3, donc sans passer a `o.sc`

IL N'Y A QU'UN SEUL DESSIN PAR GLYPHE. Le titrage a d'abord ete compile en jeu
stylistique `ss02` sur 112 doubles `.ti` ; Nicolas a decide au quarantieme tour
d'eliminer la difference entre le corps et le titrage, donc le geste s'applique
au glyphe lui-meme et il n'y a plus ni double, ni feature. `lot4.HORS_FUSION`
porte les trois glyphes qui gardent leur dessin de texte.

Ce docstring annoncait naguere `ss02` et `ss03` comme deux portees du zero, et
c'etait faux depuis longtemps : le dispositif de comparaison a trois regles
empilables du premier lot n'a jamais ete ecrit, et `add_features` ne pose que
`calt` et `ss01`. Une note prise sur un etat anterieur devient fausse a
l'instant ou le code change.
"""

import copy
import sys
import os

import glyphsLib
from glyphsLib.classes import GSGlyph, GSLayer, GSPath, GSNode, GSFeature, GSClass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zero_reconstruct import segments, area, merge_counters
import approches
import crenage_sc as CS
import lot2
import lot3
# `make_temoin` N'IMPORTAIT PAS `lot4`, et la passation le verifiait a chaque
# tour : le titrage n'etait pas compile. Il l'importe depuis le quarantieme,
# pour `HORS_FUSION` seule -- le reste du reglage se resout dans
# `mesure_titrage.appliquer_reglage`, qui reste le seul endroit qui le fait.
import lot4
# Le sommet pointe du circonflexe, quarante-et-unieme tour. L'operation vit
# dans son propre module parce qu'elle ne coupe rien : elle remplace un arc par
# l'intersection de deux flancs, et aucune des cinq operations de `coupe.py` ne
# fait cela -- `coupe.pointe` effile une TERMINAISON, pas un sommet.
import pointe_sommet as PS
# Le bras du O, quarante-huitieme tour. Meme raison que `pointe_sommet` : le
# geste doit vivre dans un module pour que les deux generateurs de tables de
# paires, qui RECONSTRUISENT l'etat, puissent le rejouer.
import bras_O as BR
# Le U redescendu, quarante-neuvieme tour. Meme raison que les deux precedents.
import abaisse_U as AU
# Les huit operateurs remontes, cinquante-troisieme tour. Meme raison que les
# trois precedents, et une de plus : l'operation est NEUVE -- aucune des cinq
# de `coupe.py` ne translate un glyphe entier.
import operateurs as OP
import barre_mediane as BM
# La queue du j descendue, soixantieme tour. Meme raison que les quatre
# precedents : le geste vit dans son module pour que les deux generateurs qui
# RECONSTRUISENT leur etat puissent le rejouer.
import descente_j as DJ
from glyphsLib.classes import GSComponent

THETA = 20.0        # angle de coupe, lot 2

# Lot 3, valeurs tranchees sur planche par Nicolas.
HAUTEUR_SC = 574.0    # 0,859 de la capitale, 1,157 de la hauteur d'x
HAUTEUR_CAP = 668.0   # la hauteur de capitale de cette source, mesuree
LARGEUR_SC = 1.0      # homothetique : les coupes du lot 2 restent intactes
#: L'approche laterale des petites capitales, en unites de chaque cote.
#:
#: **ELLE NE BOUGE PAS AU CINQUANTE-CINQUIEME TOUR, ET C'EST MESURE.** Le point
#: 93 lui imputait la plainte de Nicolas sur `KO`. La decomposition du blanc dit
#: autre chose : ces 28 unites par frontiere tombent sur TOUTES les paires de la
#: meme facon, donc elles reglent un niveau, et ce qui se voit est l'ecart entre
#: `KO` et `KI` -- 58,8 unites contre 25,9 au Regular. La difference vient
#: entierement du crenage absent, et c'est `crenage_sc` qui la traite.
APPROCHE_SC = 14.0

SRC = "/tmp/ahn/sources"
OUT = os.path.dirname(os.path.abspath(__file__))

CHIFFRES = "zero one two three four five six seven eight nine".split()


# ------------------------------------------------------------------ glyphes

def centroid_y(path):
    pts = [s[1] for s in segments(path)]
    return sum(p[1] for p in pts) / len(pts)


def build_slashless_layer(layer):
    """Retourne un GSLayer identique, contreformes recousues."""
    paths = [s for s in layer.shapes if isinstance(s, GSPath)]
    if len(paths) != 3:
        raise ValueError(f"3 contours attendus, {len(paths)} trouves")
    areas = [abs(area([s[1] for s in segments(p)])) for p in paths]
    outer = paths[areas.index(max(areas))]
    inner = sorted([p for p in paths if p is not outer], key=centroid_y)

    merged, diag = merge_counters(inner[0], inner[1])

    new = GSLayer()
    new.layerId = layer.layerId
    new.associatedMasterId = layer.associatedMasterId
    new.width = layer.width
    new.shapes.append(copy.deepcopy(outer))

    counter = GSPath()
    counter.closed = True
    for kind, p0, ctrl, p3 in merged:
        for c in ctrl:
            counter.nodes.append(GSNode((round(c[0], 1), round(c[1], 1)), "offcurve"))
        n = GSNode((round(p3[0], 1), round(p3[1], 1)), "curve" if kind == "curve" else "line")
        n.smooth = True
        counter.nodes.append(n)
    new.shapes.append(counter)
    return new, diag


def add_slashless(font, log):
    src = font.glyphs["zero"]
    g = GSGlyph("zero.slashless")
    g.leftKerningGroup = src.leftKerningGroup
    g.rightKerningGroup = src.rightKerningGroup
    g.category, g.subCategory = src.category, src.subCategory
    g.export = True
    master_ids = {m.id for m in font.masters}
    for layer in src.layers:
        if layer.layerId not in master_ids:
            continue
        new, diag = build_slashless_layer(layer)
        mname = next(m.name for m in font.masters if m.id == layer.layerId)
        log.append((mname, max(d[2] for d in diag)))
        g.layers.append(new)
    font.glyphs.append(g)

    # version tabulaire : simple recomposition
    tf = font.glyphs["zero.tf"]
    g2 = copy.deepcopy(tf)
    g2.name = "zero.tf.slashless"
    g2.unicodes = []
    for layer in g2.layers:
        for s in layer.shapes:
            if getattr(s, "componentName", None) == "zero":
                s.componentName = "zero.slashless"
    font.glyphs.append(g2)


def add_narrow_nbspace(font, log):
    """L'espace fine insecable U+202F, point ouvert 32.

    Elle manque a la police de base, et les gabarits emploient U+00A0 partout a
    sa place. Mesure au trente-troisieme tour : U+00A0 a exactement la chasse de
    l'espace mot, 260 a 330 unites selon le master, et elle se voit devant un
    point d'interrogation.

    Il n'y a rien a dessiner. Une espace n'est qu'une chasse, et l'insecabilite
    n'est pas une propriete du glyphe : c'est le moteur de rendu qui la lit sur
    le code point. La police de base porte deja `thinspace` U+2009, a la moitie
    exacte de l'espace mot, et le sous-ensemble servi la porte aussi. U+202F est
    donc la meme chasse sous un autre code point.

    La chasse est lue sur `thinspace` du master courant, jamais recopiee en dur :
    si la source amont la change, la fine suit. Et l'absence de `thinspace` leve
    au lieu de retomber sur une valeur par defaut, comme `lot2.valeur_master` :
    une espace muette a la mauvaise chasse est exactement le genre de defaut
    qu'aucun controle du projet ne verrait.
    """
    src = font.glyphs["thinspace"]
    if src is None:
        raise KeyError("thinspace absente de la source : la chasse de U+202F "
                       "n'a pas de reference, et une valeur par defaut serait "
                       "un mensonge silencieux")
    g = GSGlyph("narrownbspace")
    g.unicodes = ["202F"]
    g.category, g.subCategory = src.category, src.subCategory
    g.export = True
    # Groupes de cremage a son propre nom, comme `thinspace` et `nbspace` : une
    # espace ne se crene pas, et lui donner le groupe de thinspace la ferait
    # heriter de paires ecrites pour un caractere secable.
    g.leftKerningGroup = g.rightKerningGroup = "narrownbspace"
    ids = {m.id: m.name for m in font.masters}
    largeurs = {}
    for layer in src.layers:
        if layer.layerId not in ids:
            continue
        neuf = GSLayer()
        neuf.layerId = neuf.associatedMasterId = layer.layerId
        neuf.width = layer.width
        g.layers.append(neuf)
        largeurs[ids[layer.layerId]] = layer.width
    if len(largeurs) != len(ids):
        raise ValueError(f"U+202F construite dans {len(largeurs)} master(s) sur "
                         f"{len(ids)} : un master sans calque casse le variable")
    font.glyphs.append(g)
    log.append(("U+202F fine insecable",
                ", ".join(f"{m} {w:g}" for m, w in largeurs.items())))


# ----------------------------------------------------------------- features

def existing(font, names):
    return [n for n in names if font.glyphs[n] is not None]


def add_features(font):
    tf = [c + ".tf" for c in CHIFFRES]
    # `uni00A0` et `uni202F` etaient dans cette liste et n'ont jamais rien
    # designe : cette source nomme ses espaces `nbspace`, `thinspace`,
    # `narrownbspace`, pas `uniXXXX`. `existing` les filtrait en silence, donc
    # la liste paraissait couvrir U+00A0 deux fois et U+202F pas du tout.
    # Trente-troisieme tour : les deux noms morts sont retires, et U+202F entre
    # sous son vrai nom, en meme temps que le glyphe.
    #
    # `thinspace` U+2009 reste dehors, et c'est un choix. Elle est servie depuis
    # le vingt-quatrieme tour : l'ajouter ici changerait le comportement du zero
    # contextuel sur un caractere deja en ligne, ce qui est une decision et non
    # un effet de bord. Point ouvert 61.
    seps = existing(font, ["comma", "period", "space", "narrownbspace",
                           "slash", "hyphen", "colon", "nbspace", "figuredash",
                           "endash"])

    classes = {
        "chiffres": CHIFFRES + tf,
        # tout ce qui vaut « chiffre » en contexte, y compris deja denude
        "chiffresCtx": CHIFFRES + tf + ["zero.slashless", "zero.tf.slashless"],
        "sepnum": seps,
    }
    for name, members in classes.items():
        c = GSClass(name, " ".join(members))
        c.automatic = False
        font.classes.append(c)

    # ---- calt : le zero se denude dans un groupe de chiffres.
    # Un chiffre voisin suffit, d'un cote ou de l'autre, directement ou a
    # travers un separateur numerique. Un zero seul, ou colle a une lettre,
    # reste barre : c'est la garantie 0/O.
    calt = (
        "# Temoin : zero non barre dans un groupe de chiffres.\n"
        "# 1. un chiffre colle, a droite ou a gauche\n"
        "sub zero' @chiffresCtx by zero.slashless;\n"
        "sub @chiffresCtx zero' by zero.slashless;\n"
        "sub zero.tf' @chiffresCtx by zero.tf.slashless;\n"
        "sub @chiffresCtx zero.tf' by zero.tf.slashless;\n"
        "# 2. un chiffre a travers un separateur numerique\n"
        "sub zero' @sepnum @chiffresCtx by zero.slashless;\n"
        "sub @chiffresCtx @sepnum zero' by zero.slashless;\n"
        "sub zero.tf' @sepnum @chiffresCtx by zero.tf.slashless;\n"
        "sub @chiffresCtx @sepnum zero.tf' by zero.tf.slashless;\n"
    )
    # ---- ss01 : forcage, pour les contextes purement numeriques
    #
    # `featureNames` porte le libelle que les menus de fonctions affichent.
    # Sans lui, un utilisateur de la police publiee voit un `ss01` nu, et
    # Font Bakery le signale par `stylisticset_description`. Soixante-
    # troisieme tour, point 108, libelle arbitre par Nicolas.
    #
    # EN ANGLAIS, ET C'EST UN CHOIX. La police se publie sous OFL pour etre
    # reutilisee hors du site : la langue par defaut de la table `name` est
    # l'anglais, et un menu de fonctions le montre a des gens dont ce n'est
    # pas la langue. Un enregistrement francais s'ajouterait par
    # `name 3 1 0x040C`, il n'y en a pas.
    #
    # La chaine ne le REPORTE PAS toute seule : `featureNames` est une
    # construction de feaLib, donc elle vit dans le code de la feature et
    # pas dans un parametre. Les deux chaines la voient de la meme facon,
    # puisque les deux appellent `fontmake` sur cette source.
    ss01 = (
        "featureNames {\n"
        '    name "Unslashed zero";\n'
        "};\n"
        "# Temoin : zero non barre force.\n"
        "sub zero by zero.slashless;\n"
        "sub zero.tf by zero.tf.slashless;\n"
    )

    for tag, code in (("calt", calt), ("ss01", ss01)):
        f = GSFeature(tag, code)
        f.automatic = False
        font.features.append(f)

    # tnum / pnum doivent connaitre les nouvelles formes, quel que soit
    # l'ordre d'application des lookups
    for feat in font.features:
        if feat.name == "tnum":
            feat.code = feat.code.rstrip() + "\nsub zero.slashless by zero.tf.slashless;\n"
            feat.automatic = False
        if feat.name == "pnum":
            feat.code = feat.code.rstrip() + "\nsub zero.tf.slashless by zero.slashless;\n"
            feat.automatic = False


def add_smallcaps_features(font):
    """smcp et c2sc.

    Les deux sont necessaires, et c2sc n'est pas un supplement de confort. Les
    gabarits ecrivent leurs sigles en capitales — <span class="sigle">RNT —
    et `font-variant-caps: small-caps` ne transforme que les minuscules : sur
    un texte deja en capitales il ne fait rien du tout. C'est c2sc qui traite
    ce cas, et cote CSS il faut `all-small-caps`, qui active les deux.
    """
    jeu = lot3.jeu(font)
    mid = font.masters[0].id

    def morceaux(nom):
        """Les composants d'un glyphe accentue, dans l'ordre.

        Sert a rattraper les suites decomposees. Un caractere absent du cmap est
        decompose par HarfBuzz avant que smcp ou c2sc n'aient la main : le Y
        passait alors en petite capitale et son trema restait en taille de
        capitale, flottant au-dessus. Mesure faite sur le Y trema, qui manquait
        au sous-ensemble web. La regle est deduite des composants de la source,
        pas devinee.
        """
        g = font.glyphs[nom]
        if g is None:
            return []
        l = next((x for x in g.layers if x.layerId == mid), None)
        if l is None:
            return []
        c = [s.componentName for s in l.shapes if hasattr(s, "componentName")]
        return c if len(c) == 2 else []

    def bloc(paires, titre):
        """Ligatures d'abord : une substitution simple ecrite avant mangerait
        la lettre de base et la ligature ne se declencherait jamais."""
        lig, simple = [], []
        for cible, source in paires:
            if font.glyphs[source] is None:
                continue
            m = morceaux(source)
            if m and all(font.glyphs[x] is not None for x in m):
                lig.append(f"sub {m[0]} {m[1]} by {cible};\n")
            simple.append(f"sub {source} by {cible};\n")
        return f"# {titre}\n" + "".join(lig) + "".join(simple)

    smcp = bloc([(sc, bas) for sc, _, bas, _ in jeu],
                "Temoin : petites capitales depuis les minuscules.")
    c2sc = bloc([(sc, haut) for sc, _, _, haut in jeu],
                "Temoin : petites capitales depuis les capitales.")
    for tag, code in (("smcp", smcp), ("c2sc", c2sc)):
        f = GSFeature(tag, code)
        f.automatic = False
        font.features.append(f)


# --------------------------------------------------------------------- main

# Le garde-fou de boite du titrage, LU SUR UNE MESURE et non suppose. Le plus
# grand debordement que le dessin arrete produit vaut 49,2 unites, sur le K en
# italique, et 44,0 sur le V et le W au romain : c'est la sortante elle-meme.
# 120 laisse donc un facteur 2,4 avant de mordre, et ne peut attraper qu'un
# contour parti en vrille.
#
# IL LEVE, IL NE CORRIGE PAS. `mesure_poids_titrage.couper_double` remet le
# calque d'origine quand la marge est franchie, ce qui est juste pour une
# mesure de poids -- un glyphe jamais instruit y est attendu. Ici le dessin est
# arrete et valide sur planche : un debordement serait une regression, et un
# glyphe silencieusement remis a l'etat d'avant donnerait une forme plausible
# que personne n'a validee.
MARGE_TITRAGE = 120.0


def _boite_noeuds(layer):
    xs, ys = [], []
    for p in layer.shapes:
        for n in getattr(p, "nodes", []):
            xs.append(float(n.position.x))
            ys.append(float(n.position.y))
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def add_fusion(font, path, log):
    """Applique le geste du lot 4 aux glyphes du perimetre, `HORS_FUSION` mis a
    part. C'est LA FUSION du corps et du titrage.

    QUARANTIEME TOUR, ET C'EST UN CHANGEMENT DE FORME DU LIVRABLE. Le titrage a
    d'abord ete compile en jeu stylistique `ss02` sur 112 doubles `.ti`, voie B
    tranchee au trente-huitieme tour. Nicolas a ensuite decide d'eliminer la
    difference entre le corps et le titrage : un seul dessin par glyphe, donc le
    geste s'applique au glyphe LUI-MEME, le doublage disparait et `ss02` avec.

    Trente-huit glyphes a contour propre differaient entre les deux etats. Tous
    prennent le geste du titrage sauf le m, le n et le r -- `lot4.HORS_FUSION`,
    ou vit aussi le prix mesure de ce partage sur la paire `n/u`.

    ELLE PASSE AVANT LE LOT 3, ET L'ORDRE EST UNE DECISION. Le lot 3 derive les
    44 petites capitales des capitales DU PROJET : placee avant, la fusion leur
    est transmise au rapport 574/668, ce que Nicolas a choisi. Placee apres,
    elles resteraient seules sur l'ancien dessin et un sigle en petites
    capitales differerait du meme sigle en capitales pleines. Le trente-huitieme
    tour les avait ecartees du titrage, mais cette decision visait un titrage
    SEPARE et tombe avec lui.

    LE PERIMETRE EST RESOLU A UN SEUL ENDROIT, `mesure_titrage.analyser`, qui
    le rend depuis la geometrie de la source amont intersectee au repertoire
    SERVI. La chaine ne tient donc pas sa propre liste de 112 noms : un
    perimetre resolu a deux endroits vaut deux perimetres, et ce projet l'a
    paye trois fois, la derniere dans un COMPTEUR.

    Le prix de ce choix est une dependance a deux fichiers que la chaine ne
    produit pas elle-meme : la source amont `/tmp/ahn`, dont elle depend deja
    puisqu'elle en part, et le WOFF2 SERVI du tour precedent, qui donne le
    repertoire. La fonction LEVE si l'un des deux manque, au lieu d'ecrire des
    sources sans titrage : un contrôle doit distinguer "mesure et conforme" de
    "pas mesure", et `/tmp/ahn` a disparu sept fois dans ce projet. Sur une
    machine neuve, la boucle se casse en deux passes -- compiler et
    sous-ensembler une fois sans titrage, puis relancer.

    `appliquer_reglage` recoit LE NOM DE LA BASE, jamais celui du double : les
    prescriptions, `ETENDU` et `depassement_pour` sont indexes par nom et ne
    suivent aucun suffixe. La fonction leve maintenant si on se trompe.
    """
    import mesure_titrage as MT

    # LA SOURCE SE RECONNAIT PAR SON CHEMIN, et non par `font.familyName` : a
    # ce point de la chaine le nom est encore celui d'Atkinson, et il n'est pas
    # dit qu'il porte "Italic". L'appariement se fait sur le fichier d'entree,
    # qui est ce que `MT.SOURCES` nomme.
    lab = amont = binaire = None
    for l, a, _projet, b in MT.SOURCES:
        if os.path.basename(a) == os.path.basename(path):
            lab, amont, binaire = l, a, b
    if lab is None:
        raise RuntimeError(
            f"source inconnue de mesure_titrage.SOURCES : {path}. Le perimetre "
            "du titrage s'y resout, donc la chaine ne peut pas deviner.")
    if not os.path.exists(binaire):
        raise RuntimeError(
            f"le binaire servi manque, {binaire}. Le perimetre du titrage s'y "
            "lit : sans lui la chaine ecrirait des sources SANS titrage, et "
            "rien ne le dirait. Compiler et sous-ensembler une fois sans "
            "titrage, puis relancer.")
    res = MT.analyser(lab, amont, binaire, verbeux=False)
    if res is None:
        raise RuntimeError(
            f"le perimetre du titrage n'a pas pu etre resolu pour {lab} : la "
            f"source amont {amont} est illisible. Ne rien conclure d'un "
            "controle qui n'a pas lu sa source, et ne rien ecrire non plus.")
    perimetre = res["perimetres"]["le perimetre ARRETE, trente-quatrieme tour"]

    presents = {g.name for g in font.glyphs}
    dedans = sorted(n for n in perimetre
                    if n in presents and n not in lot4.HORS_FUSION)
    manquants = sorted(n for n in perimetre if n not in presents)
    gardes = sorted(n for n in perimetre if n in lot4.HORS_FUSION)

    # La boite AVANT, pour le garde-fou : la fusion elle-meme passe par
    # `mesure_titrage.fusionner`, partagee avec les deux generateurs de tables
    # de paires et avec la mesure de lisibilite. Une copie locale finirait par
    # appliquer autre chose que ce que les tables mesurent.
    mid = {m.id: m for m in font.masters}
    avant = {(nom, l.layerId): _boite_noeuds(l)
             for nom in dedans for l in font.glyphs[nom].layers
             if l.layerId in mid}

    _touches, bouge = MT.fusionner(font, perimetre)

    deborde = []
    for nom in dedans:
        for l in font.glyphs[nom].layers:
            if l.layerId not in mid:
                continue
            b0, b1 = avant.get((nom, l.layerId)), _boite_noeuds(l)
            if b0 and b1:
                d = max(b0[0] - b1[0], b0[1] - b1[1],
                        b1[2] - b0[2], b1[3] - b0[3])
                if d > MARGE_TITRAGE:
                    deborde.append(f"{nom} {mid[l.layerId].name} {d:.1f} u")
    if deborde:
        raise RuntimeError(
            "la fusion fait sortir un glyphe de sa boite de plus de "
            f"{MARGE_TITRAGE:.0f} unites : {', '.join(deborde)}. Le dessin est "
            "arrete et valide, donc c'est une regression, pas un cas nouveau.")
    if not bouge:
        raise RuntimeError(
            "aucun glyphe du perimetre ne porte de geste. La fusion n'a donc "
            "rien fusionne, et la police servie serait celle d'avant le lot 4 "
            "sans que rien ne le dise.")

    log.append(("fusion lot 4",
                f"{len(dedans)} glyphes recoivent le geste, "
                f"{len(bouge)} bougent, {len(gardes)} gardent le texte "
                f"({' '.join(gardes)})"))
    if manquants:
        log.append(("fusion hors source", " ".join(manquants)))
    return dedans


def add_pointe_accent(font, log):
    """Le sommet du circonflexe devient une pointe. Quarante-et-unieme tour.

    LE GESTE LUI-MEME VIT DANS `pointe_sommet.appliquer`, ET PAS ICI. Les deux
    generateurs de tables de paires reconstruisent leur etat au lieu de lire
    `Temoin.glyphs` : ils doivent rejouer cette etape, donc elle ne peut pas
    appartenir a la chaine. Deux codes qui appliquent le meme etat doivent
    passer par la meme fonction, et ce projet a paye la lecon au vingt-
    quatrieme tour sur `approches.table_kern`.

    OU CETTE ETAPE SE PLACE : apres `add_fusion` et AVANT le lot 3,
    exactement comme elle, pour que les 44 petites capitales heritent de
    l'accent aligne. Un sigle en petites capitales accentuees differerait
    sinon du meme sigle en capitales pleines.
    """
    PS.appliquer(font, log)


#: Les noms de glyphes que la convention OpenType refuse, et leur remplacement.
#:
#: Soixante-troisieme tour, point 110. `valid_glyphnames` de Font Bakery
#: refuse le tiret, et c'est le seul FAIL de fond que les deux chaines de
#: compilation partageaient. Le nom passe chez Atkinson parce que le binaire
#: livre le porte renommé par ses noms de production ; le projet refuse ces
#: noms depuis le cinquante-troisieme tour, pour que ses controles restent
#: voyants sur 61 glyphes, donc il expose le nom de sa source et doit le
#: corriger a la source.
#:
#: `musicalnote` EST le nom de production que l'AGL donne a U+266A, donc les
#: deux chaines convergent sur lui : avec `--no-production-names` il est
#: garde tel quel, sans le drapeau il serait produit a l'identique.
#:
#: Coût mesuré : nul cote servi. Le glyphe n'est pas dans le binaire
#: sous-ensemble, U+266A n'est pas dans son cmap, et aucun autre fichier du
#: projet ne nomme ce glyphe -- verifie par balayage avant l'ecriture.

# --------------------------------------------------- identite du fork, 64e tour
#
# POURQUOI CES CHAMPS BOUGENT. Jusqu'au soixante-quatrieme tour, `make_temoin`
# ne changeait que le nom de famille : Temoin sortait donc en declarant
# l'equipe d'Atkinson comme SES createurs, Applied Design Works comme SON
# fabricant, brailleinstitute.org comme SON fournisseur, et la version 2.001
# d'Atkinson comme la sienne. Un systeme qui installe la police affiche ces
# champs. La clause 4 de l'OFL autorise a RECONNAITRE la contribution des
# auteurs d'origine, elle interdit d'employer leur nom pour une version
# modifiee : s'attribuer leurs auteurs depasse la reconnaissance.
#
# CE QUI RESTE INTACT, et c'est une obligation de la clause 1 : la notice de
# copyright d'Atkinson. Elle est CONSERVEE et la notice de Temoin s'ajoute
# apres elle. Retirer la premiere serait une violation.
#
# LA RECONNAISSANCE DE LA CONTRIBUTION vit dans le name ID 10, pose par
# `finaliser.py`, ou l'equipe d'Atkinson est nommee pour ce qu'elle a fait.
# C'est l'exception que la clause 4 prevoit explicitement.
#
# ATTENTION AU CONTROLE EXTERIEUR. `googlefonts/font_copyright` est de severite
# maximale et exige le motif "Copyright YYYY The ... Project Authors (URL)".
# La chaine ci-dessous le satisfait, mais **par la ligne d'Atkinson** : le
# controle s'accroche sur elle et reste aveugle au format de la seconde.
# Mesure au soixante-quatrieme tour. Ne pas en conclure que la ligne de l'OXA
# est validee par quoi que ce soit.
COPYRIGHT_AMONT = (
    "Copyright 2020-2024 The Atkinson Hyperlegible Next Project Authors "
    "(https://github.com/googlefonts/atkinson-hyperlegible-next)")

# LES CLES SONT CELLES DE `font.properties`, ET C'EST MESURE. Les affecter par
# attribut (`font.copyright = ...`) NE MARCHE PAS pour les cles au pluriel :
# `designerURL` et `manufacturerURL` prenaient l'affectation, `copyrights`,
# `designers` et `manufacturers` la perdaient en silence, et le binaire sortait
# en declarant toujours l'equipe d'Atkinson. Trouve en relisant la table `name`
# du binaire compile, pas la source. Ecrire dans `properties` par cle.
IDENTITE = {
    # UNE SEULE LIGNE, ET C'EST UNE CONTRAINTE MESUREE. Un saut de ligne dans
    # un enregistrement de nom fait echouer `googlefonts/name/line_breaks`, de
    # FAIL : le premier jet en posait un entre les deux notices et faisait
    # passer Temoin de 0 a 2 FAIL. Les deux notices tiennent donc sur une ligne,
    # separees par une barre verticale.
    "copyrights": COPYRIGHT_AMONT + " | "
                  "Copyright 2026 Observatoire de l'Expérimentation Animale "
                  "(https://oxanimale.fr)",
    "designers": "Observatoire de l'Expérimentation Animale",
    "designerURL": "https://oxanimale.fr",
    "manufacturers": "Observatoire de l'Expérimentation Animale",
    # Le name ID 11 pointe vers le depot public, usage du domaine : point
    # ouvert 115, ecrit au soixante-et-onzieme tour. Le createur, ID 12, et la
    # notice de copyright gardent le site de l'association.
    "manufacturerURL": "https://github.com/oxanimale/temoin-font",
}

# Temoin repart de 1.000 : reprendre le 2.001 d'Atkinson ferait passer un fork
# pour une revision de la police d'origine.
VERSION = (1, 0)

AMONT_ATTENDU = {
    "copyrights": COPYRIGHT_AMONT,
    "designers": "Elliott Scott, Megan Eiswerth, Linus Boman, "
                 "Theodore Petrosky, Letters from Sweden",
    "designerURL": "http://helloapplied.com",
    "manufacturers": "Applied Design Works, Letters from Sweden",
    "manufacturerURL": "https://www.brailleinstitute.org/",
}


def _ecrire_propriete(prop, valeur):
    """Ecrit une propriete de `font.properties`, localisee ou non.

    DEFAUT DE `glyphsLib`, mesure au soixante-quatrieme tour et corrige ici :
    le setter de `GSFontInfoValue.value` ecrit dans `_value`, mais
    `_serialize_to_plist` prefere `_localized_values` des qu'elle existe. Une
    affectation par `.value` sur une cle localisee -- `copyrights`,
    `designers`, `manufacturers` -- est donc SANS EFFET, et la source repart
    avec l'identite d'Atkinson sans qu'aucune erreur ne soit levee. Les cles
    non localisees, `designerURL` et `manufacturerURL`, prenaient
    l'affectation : c'est ce qui rendait le defaut difficile a voir, trois
    champs sur cinq changeant bien.

    Trouve en relisant la table `name` du BINAIRE compile, pas la source.
    """
    prop.value = valeur
    if getattr(prop, "_localized_values", None):
        for langue in list(prop._localized_values):
            prop._localized_values[langue] = valeur


def poser_identite(font):
    """Pose les champs d'identite du fork, et REFUSE de se taire.

    Elle leve si un champ qu'elle ecrase ne portait pas la valeur amont
    attendue, ou si une cle manque : une source amont qui change d'identite
    doit faire crier la chaine plutot que produire un binaire dont la
    titularite est fausse en silence. Meme discipline que `renommer`.
    """
    vus = {p.key: p for p in font.properties}
    for cle, amont in AMONT_ATTENDU.items():
        if cle not in vus:
            raise ValueError(
                f"identite : la cle `{cle}` manque dans `font.properties` de "
                f"l'amont. La nomenclature des proprietes a change : verifier "
                f"avant de compiler.")
        if vus[cle].value != amont:
            raise ValueError(
                f"identite : `{cle}` vaut {vus[cle].value!r} en amont et non "
                f"{amont!r}. La source amont a change d'identite, donc la "
                f"notice de copyright de Temoin est peut-etre fausse.")
    for cle, valeur in IDENTITE.items():
        _ecrire_propriete(vus[cle], valeur)
    font.versionMajor, font.versionMinor = VERSION
    return [("identite du fork",
             f"copyright a deux lignes, createur et fabricant a l'OXA, "
             f"version {VERSION[0]}.{VERSION[1]:03d}")]


RENOMMAGES = {"note-musical": "musicalnote"}


def renommer(font, log):
    """Applique `RENOMMAGES`, et REFUSE de se taire.

    Une etape muette ne se distingue pas d'une etape oubliee, et ce projet a
    paye la lecon assez souvent. Si un nom d'origine a disparu de l'amont, ou
    si sa cible existe deja, l'etape leve au lieu de passer son tour : une
    source amont qui aurait change de nomenclature doit faire crier la chaine,
    pas la laisser produire un binaire que `valid_glyphnames` refuserait de
    nouveau en silence.
    """
    for ancien, neuf in RENOMMAGES.items():
        if font.glyphs[ancien] is None:
            raise SystemExit(
                f"renommer : '{ancien}' est absent de la source amont. "
                "La nomenclature a change, ou le renommage est deja fait "
                "ailleurs : le verifier avant de retirer cette garde."
            )
        if font.glyphs[neuf] is not None:
            raise SystemExit(
                f"renommer : '{neuf}' existe deja dans la source amont. "
                "Le renommage ecraserait un glyphe."
            )
        font.glyphs[ancien].name = neuf
        log.append(("renomme", f"{ancien} -> {neuf}"))


def process(path, out_path):
    with open(path, encoding="utf-8") as fh:
        font = glyphsLib.load(fh)
    log = []
    # En premier : les etapes suivantes indexent par nom, et un renommage
    # tardif laisserait derriere lui des tables ecrites sur l'ancien nom.
    # Aucune ne nomme ce glyphe aujourd'hui, ce qui est mesure, mais l'ordre
    # est le seul qui reste juste si une le nomme un jour.
    renommer(font, log)
    add_slashless(font, log)
    # Avant `add_features` : la classe des separateurs est construite par
    # `existing`, qui ne voit que ce qui est deja dans la police.
    add_narrow_nbspace(font, log)
    add_features(font)
    # lot 2 : le systeme de coupes. Il s'applique apres le zero, sur lequel il
    # n'a aucune prise (le zero n'a pas de terminaison libre).
    lot2.appliquer_lot(font, THETA)
    # les approches. Vingt-troisieme tour : une approche de -100 sur la chasse du
    # F, plus des correctifs. Vingt-quatrieme : l'approche est retiree, elle
    # creait six contacts de capitales dans le binaire servi, et le trou de la
    # barre mediane se referme paire par paire (`paires_F.py`). Aucune chasse
    # n'est donc plus touchee. L'etape reste entre le lot 2 et le lot 3, meme si
    # ce placement n'a plus d'effet sur l'heritage des petites capitales : le
    # crenage ne s'y propage pas, et `f.sc` porte encore le trou.
    # TEMOIN_SANS_APPROCHES=1 saute cette etape. C'est la source qu'il faut pour
    # recalculer la table : `paire_bornee` mesure ce que la coupe a ouvert, donc
    # elle demande un Temoin ou rien n'est encore crene.
    jrn_ap = ([] if os.environ.get("TEMOIN_SANS_APPROCHES")
              else approches.appliquer(font))
    # Le journal se compte par ce qu'il porte, et non par une liste d'etiquettes
    # ecrite a la main : au vingt-quatrieme tour le compteur a annonce "0
    # correctifs" sur une table de 401 paires, parce que ses etiquettes avaient
    # change sous lui. Un compteur qui ne compte pas ce qui a ete fait est un
    # controle muet.
    from collections import Counter
    compte = Counter(x[0] for x in jrn_ap)
    log.append(("approches",
                ", ".join(f"{n} {k}" for k, n in sorted(compte.items()))
                or "rien"))
    # lot 3 : les petites capitales. Apres le lot 2, et l'ordre n'est pas
    # indifferent : elles heritent des coupes au lieu de les recevoir une
    # seconde fois. Une reduction homothetique conserve l'angle d'une coupe, et
    # toute affinite conserve l'alignement des bouts de barre du F.
    # lot 4 : la coupe de titrage, FUSIONNEE dans le dessin unique. AVANT le
    # lot 3, pour que les 44 petites capitales en heritent au rapport 574/668 :
    # sinon elles resteraient seules sur l'ancien dessin, et un sigle en petites
    # capitales differerait du meme sigle en capitales pleines.
    #
    # Et APRES le lot 2 et les approches, ce qui est le point ouvert 66 : le
    # geste se pose sur l'etat servi, la ou le lot 2 a deja coupe. Le temoin de
    # ce choix est le `f`, qui rend 32,0 unites de sortie depuis Atkinson brut
    # et 0,3 depuis l'etat servi -- partir de l'amont donnerait une forme que
    # personne ne verra.
    add_fusion(font, path, log)
    add_pointe_accent(font, log)
    # LE U REDESCEND, quarante-neuvieme tour, et sa place est ici : APRES la
    # fusion, qui pose le geste, et AVANT le lot 3, pour que `u.sc` en herite
    # au rapport 574/668 comme elle herite de tout le reste. Descendre le bout
    # avant le geste le desarmerait -- `loc_alignement` ne designe que les
    # terminaisons posees SUR un alignement -- et le premier essai a rendu un U
    # a 624 sans aucune coupe. Voir `abaisse_U`.
    AU.appliquer(font, log)
    # LES HUIT OPERATEURS REMONTENT DE 64, cinquante-troisieme tour, et leur
    # place est celle d'`abaisse_U`, decidee par Nicolas : APRES la fusion, qui
    # pose le geste de titrage, et AVANT le lot 3. Un glyphe translate avant le
    # geste ne serait plus a portee de son alignement et le perdrait en silence,
    # ce que `loc_alignement` fait sans lever.
    #
    # Aucun des huit n'a de petite capitale, donc la frontiere du lot 3 ne joue
    # pas pour eux : ce qui decide la place est le geste de titrage, pas
    # l'heritage. Mesure du meme tour : des huit, SEUL le `plus` porte
    # aujourd'hui un geste du projet -- sa plongee de 32 unites, que
    # `lot4.PRESCRIPTIONS["plus"]` retire au meme tour -- et les sept autres
    # sont identiques a Atkinson dans le binaire servi. La place ne change donc
    # rien aujourd'hui, et elle protege le jour ou l'un d'eux recevra un geste.
    OP.appliquer(font, log)
    # LA BARRE MEDIANE DU F ET DE L'E, point 94, cinquante-quatrieme tour. Sa
    # place est celle d'`abaisse_U` et des operateurs : APRES la fusion, et
    # AVANT le lot 3.
    #
    # Apres la fusion, parce que le bout de la barre mediane du F porte une
    # coupe depuis le lot 2 : la translation la fait VOYAGER avec la barre au
    # lieu de la reappliquer a une hauteur neuve.
    #
    # Avant le lot 3, parce que les quatre petites capitales concernees --
    # `f.sc`, `e.sc`, `ae.sc`, `oe.sc` -- doivent en heriter. Mesure du meme
    # tour : `f.sc` derive du F deplace s'aligne sur `e.sc` a 0,05 unite pres
    # dans les huit masters, donc RIEN ne s'ecrit sur les 44 petites capitales.
    # L'ecart y valait 33,2 unites au Bold et 39,2 a l'ExtraBold, plus grand
    # que sur la capitale, la derivation prenant celle-ci plus haut sur l'axe
    # de graisse.
    BM.appliquer(font, log)
    # LA QUEUE DU j DESCEND, point 105, soixantieme tour. Sa place est celle
    # d'`abaisse_U`, des operateurs et de la barre mediane : APRES la fusion.
    #
    # Apres la fusion et apres le lot 2, parce que `jdotless` porte DEJA deux
    # gestes -- une coupe du lot 2 sur son bout gauche, et le geste de titrage,
    # son nom etant dans le perimetre arrete. Descendre le crochet avant les
    # desarmerait : `loc_gauche` et `loc_alignement` designent des terminaisons
    # a une hauteur donnee, et le premier essai du U a rendu au quarante-
    # neuvieme tour un glyphe sans aucune coupe pour cette raison.
    #
    # La frontiere du lot 3 ne joue pas ici : `j.sc` derive du `J` CAPITALE et
    # non du `j`, donc il n'herite rien de ce geste. Mesure et non supposee.
    DJ.appliquer(font, log)
    jrn = []
    lot3.appliquer_lot(font, HAUTEUR_SC, LARGEUR_SC, APPROCHE_SC, jrn)
    add_smallcaps_features(font)
    log.append(("petites capitales", len(lot3.jeu(font))))
    # LE CRENAGE DES PETITES CAPITALES, point 93, cinquante-cinquieme tour.
    #
    # APRES le lot 3, qui cree les `.sc` : le module leve si on l'appelle avant.
    # Donc apres `approches.appliquer`, et c'est voulu : les valeurs lues sont
    # celles de l'etat REGLE, le blanc devant l'Æ compris, et les petites
    # capitales en heritent au rapport. Le blanc devant l'Æ existe aussi a
    # l'echelle reduite.
    #
    # Le rapport est PASSE et non recopie la-bas : deux definitions du meme
    # nombre finissent par vivre dans deux fichiers.
    # Le module ecrit une IMAGE de la table capitale, cle par cle, depuis la
    # correction du point 97 au cinquante-sixieme tour : il ne LIT plus une
    # valeur par `approches.kern`, qui rendait l'exception du representant de
    # groupe et l'ecrivait sur le groupe entier. Le compte se lit donc en deux
    # nombres, les entrees de groupe et les exceptions heritees, et la signature
    # a change pour que cette ligne ne puisse pas rester muette.
    n_sc, n_grp, n_exc, cd, cg = CS.appliquer(font, HAUTEUR_SC / HAUTEUR_CAP,
                                              jrn_ap)
    log.append(("crenage petites capitales",
                f"{n_sc} glyphes groupes, {len(cd)} cles droites, "
                f"{len(cg)} cles gauches, {n_grp} entrees de groupe et "
                f"{n_exc} exceptions heritees"))
    # Le bras du O, point ouvert 84. APRES LE LOT 3, ET C'EST UNE DECISION DE
    # NICOLAS : le lot 3 derive `o.sc` du O du projet, donc une etape posee
    # avant donnerait a la petite capitale un bras reduit au rapport 574/668.
    # Nicolas l'a ecarte au quarante-huitieme tour, avec `Oslash` et `OE` qui
    # redessinent un O sous un autre nom -- `bras_O.GLYPHES_SANS_BRAS` porte
    # les trois avec leur raison. C'est l'inverse du placement de `add_fusion`
    # et de `add_pointe_accent`, et la difference se dit : celles-la propagent
    # un geste de titrage a une lettre, celle-ci greffe une signature dans un
    # blanc qui aurait la taille d'une petite capitale.
    #
    # LE GESTE VIT DANS SON MODULE et pas ici, comme `pointe_sommet` : les deux
    # generateurs de tables de paires reconstruisent leur etat au lieu de lire
    # `Temoin.glyphs`, donc ils doivent pouvoir rejouer cette etape.
    #
    # Sur la source italique, l'appel ne pose rien et le journal le dit :
    # `lot4.MASTERS_SANS_BRAS` porte les quatre masters italiques, decision du
    # quarante-septieme tour, et une etape muette ne se distinguerait pas d'une
    # etape oubliee.
    BR.appliquer(font, log)
    for x in jrn:
        if "plafond" in x:
            log.append((f"plafond {x['base']} {x['master']}",
                        f"{x['vise']:.1f} -> {x['retenu']:.1f}"))
    # fork : le nom doit changer (marque probable du Braille Institute,
    # clause 4 de l'OFL). Nom ASCII pour rester sur au niveau PostScript.
    font.familyName = "Temoin" + ("" if "Italic" not in path else "")
    # et avec lui l'identite : createur, fabricant, URL, version, copyright.
    log.extend(poser_identite(font))
    font.save(out_path)
    return font, log


if __name__ == "__main__":
    for name in ("AtkinsonHyperlegibleNext.glyphs",
                 "AtkinsonHyperlegibleNext-Italic.glyphs"):
        out = os.path.join(OUT, name.replace("AtkinsonHyperlegibleNext", "Temoin"))
        font, log = process(os.path.join(SRC, name), out)
        print(f"{name}: {len(font.glyphs)} glyphes -> {out}")
        for cle, val in log:
            if isinstance(val, float):
                print(f"   {cle:<24} residu de recousure {val:.3f} u")
            else:
                print(f"   {cle:<24} {val}")
        print("   features:", [f.name for f in font.features])
