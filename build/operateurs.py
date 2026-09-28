#!/usr/bin/env python3
"""LES HUIT OPERATEURS MATHEMATIQUES REMONTENT DE 64 UNITES, cinquante-troisieme
tour.

LA DEMANDE. Nicolas, au cinquante-deuxieme tour, en lisant la section 8 de
`tour51.html` en texte : le `+` de `+32` paraissait trop bas. Mesure faite avant
toute hypothese, sur les deux sources et les masters Regular et Bold :

    barre horizontale du +   Atkinson 208 -> 288, centre 248
                             Temoin   208 -> 288, centre 248
    bas du fut vertical      Atkinson    0,0
                             Temoin    -32,0

LA BARRE N'AVAIT PAS BOUGE D'UN DIXIEME. Le projet avait allonge le PIED de 32
unites sous la ligne de base, par le reglage general, et c'est le piege de la
cible deduite de la casse du nom : `lot4.depassement_pour` rend 32 pour tout nom
qui commence par une minuscule, et `plus` est un SIGNE, pas un bas de casse. Le
`plusminus` et le `numbersign` ont recu la meme chose. Les trois etaient dans
`check_perimetre.VALIDES_REGLAGE_GENERAL` : valides sur planche, jamais lus en
texte. SIXIEME VALIDATION DE PLANCHE REVISEE EN TEXTE, apres le i, le k, le 1,
`idotless` et le R.

CE QUE NICOLAS A TRANCHE, ET SUR QUOI. Cinq binaires compiles dans la meme
session a partir de la meme source, ne differant que par les glyphes en cause,
prouves glyphe par glyphe sur le binaire, et lus sur `gabarits/etats-plus.html`
en texte a 18 px puis a 190 px :

    A  servi                                   barre a 248, pied -32
    B  plongee retiree, le + d'Atkinson        barre a 248, pied 0
    C  glyphe entier translate de +32          barre a 280
    D  huit operateurs remontes de 90          barre a 338
    E  huit operateurs remontes de 64          barre a 312   <- RETENU

CE QUI MONTE : `plus minus divide multiply equal less greater asciitilde`, le
`plus` repartant du dessin d'Atkinson, sa plongee retiree par
`lot4.PRESCRIPTIONS["plus"]`. DOUZE DEPUIS LE SOIXANTE-TREIZIEME TOUR :
`approxequal notequal lessequal greaterequal` suivent, decision de Nicolas.

CE QUI NE MONTE PAS, ET C'EST UNE DECISION : le `plusminus`, le `hyphen`, le
`endash` et le `emdash`. La ponctuation reste a 248. Le `plusminus` et le
`numbersign` gardent en outre leur plongee de 32 unites, relus dans la meme
phrase au meme tour.

LE PRIX, MESURE ET ASSUME. 248 vaut la moitie exacte de la hauteur d'x ; a 312
l'operateur est a 0,63 de cette hauteur, aligne ni sur le bas de casse ni sur
les chiffres, entre les deux et 22 a 28 unites sous le milieu des chiffres --
qui n'est pas un nombre unique, 340 sur un chiffre a fond plat comme le 2 et 334
sur le 3, qui deborde de 12 unites sous la ligne.

ET LE GESTE NE CHANGE PRESQUE RIEN A CE QUE LE SITE AFFICHE. Compte dans les
quatre gabarits reels, balises exclues : ZERO occurrence de `x` `/` `=` `<` `>`
`+-`, une seule de `+`, une seule de `-` U+2212, contre 30 traits d'union et 72
cadratins. Le geste change la police publiee sous OFL. Il ouvre un ecart que la
police ne refermera pas : la ou un gabarit tape un trait d'union pour un moins,
le lecteur verra un signe 64 unites plus bas que le vrai. Le remede est dans les
gabarits, pas ici.

L'OPERATION EST NEUVE, ET C'EST POURQUOI CE MODULE EXISTE. Les cinq operations
de `coupe.py` -- `coupe`, `coupe_sortante`, `bascule`, `pointe`, `allonge` --
travaillent toutes sur une TERMINAISON : elles tournent un segment, en effilent
un bout, ou poussent une droite le long de sa normale. Aucune ne translate un
glyphe ENTIER. `abaisse_U` s'en approche le plus et n'y suffit pas : elle
descend les deux coins d'un bout, pas la lettre.

LE GESTE VIT DANS UN MODULE et pas dans `make_temoin`, pour la raison de
`pointe_sommet`, de `bras_O` et de `abaisse_U` : les deux generateurs de tables
de paires RECONSTRUISENT leur etat au lieu de lire `Temoin.glyphs`, donc une
etape ecrite dans la chaine seule leur serait invisible et ils mesureraient un
dessin perime. Le projet a paye ce defaut deux fois, au quarantieme et au
quarante-et-unieme tour.

SA PLACE DANS LA CHAINE, DECIDEE PAR NICOLAS : apres `abaisse_U` et avant le
lot 3, donc APRES `add_fusion` qui pose le geste de titrage. La raison est celle
d'`abaisse_U` : `lot4.loc_alignement` ne designe que les terminaisons POSEES SUR
un alignement, donc un glyphe translate de 64 avant le geste ne serait plus a
portee et perdrait ce geste en silence. Mesure au cinquante-troisieme tour : des
huit, SEUL le `plus` porte aujourd'hui un geste du projet, les sept autres etant
identiques a Atkinson dans le binaire servi -- donc la place ne change rien
aujourd'hui, et elle protege le jour ou l'un d'eux en recevra un.

LES DEUX SOURCES MONTENT. La decision de Nicolas ne nomme pas l'italique, et le
defaut coherent est que les deux la prennent : l'inverse ferait descendre les
operateurs de 64 unites au passage en italique dans un meme paragraphe. C'est la
decision exceptionnelle qui demanderait un motif, comme le bras du O en a un
dans `lot4.MASTERS_SANS_BRAS`. Si elle se prend, elle s'ecrit ici, en une table
de masters ecartes, et non par un retrait de noms.
"""

import lot2 as L

#: Les huit noms qui montent. PERIMETRE TRANCHE PAR NICOLAS sur cinq binaires
#: compiles, il ne se rediscute pas ici.
#:
#: Les huit sont des CONTOURS PURS : mesure sur les deux sources, aucun ne porte
#: de composant, aucun ne porte d'ancre, et AUCUN GLYPHE DU REPERTOIRE NE LES
#: REFERENCE comme composant. Ce dernier fait est le garde-fou du `plusminus` :
#: s'il avait compose le `plus`, il aurait suivi, et la decision de le laisser a
#: 248 serait tombee sans qu'aucun controle le dise. Le fait est REMESURE a
#: chaque appel par `appliquer`, et non suppose -- une police qui change de
#: version peut changer de composition.
OPERATEURS = ("plus", "minus", "divide", "multiply", "equal", "less",
              "greater", "asciitilde",
              # SOIXANTE-TREIZIEME TOUR : les quatre qui manquaient. Le ≈
              # entre au servi ; le ≠, le ≤ et le ≥ y etaient deja, 64 unites
              # sous le = et le <, sans qu'aucun document le dise. Nicolas les
              # remonte tous les quatre, sur `planche-tour73-complements.png`.
              "approxequal", "notequal", "lessequal", "greaterequal")

#: De combien ils montent. Constante et non par master : Nicolas a tranche 64
#: sur des binaires compiles, apres avoir compare 90 et 32 sur la meme page.
MONTEE = 64.0

#: Les quatre qui NE MONTENT PAS, et c'est une decision. Cette table ne sert pas
#: a produire -- un nom absent d'`OPERATEURS` ne bouge pas de toute facon --
#: elle sert au CONTROLE : `check_operateurs` exige que ces quatre soient encore
#: a leur place dans le binaire, faute de quoi un geste futur pourrait les
#: emporter sans que rien ne le signale. C'est la meme raison qui met
#: `check_perimetre.HAUT_ATTENDU` dans le controle et non dans la table.
FIXES = ("plusminus", "hyphen", "endash", "emdash")

#: Les masters ou le geste n'a pas lieu. VIDE, et c'est l'etat decide : les deux
#: sources montent. Elle existe pour que la decision inverse ait un endroit ou
#: s'ecrire, comme `lot4.MASTERS_SANS_BRAS`.
MASTERS_SANS_MONTEE = frozenset()

#: La tolerance de la mesure de verification. Un centieme d'unite : la
#: translation est exacte par construction, donc tout ecart est un defaut et non
#: un arrondi.
TOL = 0.01


def _references(font):
    """Les noms de glyphes utilises comme COMPOSANT quelque part dans la police.

    Sert au garde-fou du `plusminus`. Il est remesure a chaque appel plutot
    qu'ecrit en dur : la police de base peut changer de version, et une
    composition nouvelle ferait suivre un glyphe que Nicolas a decide de laisser
    en place. Le projet a paye CINQ FOIS qu'une table indexee par NOM ne suit
    pas une composition -- l'AE au trente-neuvieme tour, `tcedilla` au meme,
    `Aring`, l'AE et l'OE au quarante-neuvieme, le quart et le trois quarts au
    meme. C'est ici le meme fait, pris par l'autre bout.
    """
    out = set()
    for g in font.glyphs:
        for lay in g.layers:
            for sh in lay.shapes:
                cn = getattr(sh, "componentName", None)
                if cn:
                    out.add(cn)
    return out


def monter_calque(layer, d=MONTEE):
    """Translate tous les noeuds du calque de `d` vers le haut. Rend le compte.

    Les ancres suivent, s'il y en a. Il n'y en a sur aucun des huit -- mesure --
    mais une ancre laissee derriere poserait la marque d'un glyphe accentue au
    mauvais endroit, et ce module ne doit pas dependre de ce que le repertoire
    contient aujourd'hui.

    LA TRANSLATION PORTE SUR LES NOEUDS ET SUR EUX SEULS. Elle ne touche ni la
    chasse, ni le crenage, ni la topologie : c'est ce qui la rend sure, et c'est
    aussi ce qui la rend invisible aux garde-fous du projet, qui mesurent des
    bouts, des couloirs et des contacts. D'ou `check_operateurs`.
    """
    faits = 0
    for p in L.paths(layer):
        for nd in p.nodes:
            nd.position = type(nd.position)(nd.position.x,
                                            nd.position.y + d)
            faits += 1
    for a in (layer.anchors or []):
        a.position = type(a.position)(a.position.x, a.position.y + d)
    return faits


def _ymin_ymax(layer):
    pts = [n.position.y for p in L.paths(layer) for n in p.nodes]
    return (min(pts), max(pts)) if pts else None


def appliquer(font, log=None):
    """Monte les `OPERATEURS` de `MONTEE`, dans tous les masters de la police.

    LEVE sur toute anomalie plutot que de corriger. Un glyphe monte dans trois
    masters et intact dans le quatrieme casse l'interpolation du variable sans
    qu'aucun controle de glyphe le dise, et `fontmake` s'en plaint tard ou pas
    du tout -- c'est la garde que `pointe_sommet` et `abaisse_U` portent pour la
    meme raison.
    """
    ids = {m.id: m.name for m in font.masters}
    refs = _references(font)
    total = 0
    calques = 0
    for nom in OPERATEURS:
        g = font.glyphs[nom]
        if g is None:
            raise ValueError(f"{nom} absent de la source")
        if nom in refs:
            raise ValueError(
                f"{nom} est utilise comme COMPOSANT par un autre glyphe : le "
                "translater emporterait ce glyphe-la, qui n'a pas ete juge. "
                "C'est le garde-fou du plusminus, et il vient de mordre.")
        for lay in g.layers:
            if lay.layerId not in ids:
                continue
            if ids[lay.layerId] in MASTERS_SANS_MONTEE:
                continue
            if any(getattr(sh, "componentName", None) for sh in lay.shapes):
                raise ValueError(
                    f"{nom} {ids[lay.layerId]} porte un COMPOSANT : une "
                    "translation par les noeuds le laisserait sur place, et le "
                    "glyphe sortirait coupe en deux.")
            avant = _ymin_ymax(lay)
            if avant is None:
                raise ValueError(
                    f"{nom} {ids[lay.layerId]} : aucun contour. Un glyphe sans "
                    "encre echappe a tout garde-fou de ce projet, et ce n'est "
                    "pas ici qu'il doit passer inapercu.")
            n = monter_calque(lay)
            apres = _ymin_ymax(lay)
            for i, (a, b) in enumerate(zip(avant, apres)):
                if abs((b - a) - MONTEE) > TOL:
                    raise ValueError(
                        f"{nom} {ids[lay.layerId]} : la boite a bouge de "
                        f"{b - a:.3f} u pour {MONTEE:.1f} demandees "
                        f"({'ymin' if i == 0 else 'ymax'}).")
            total += n
            calques += 1
    attendu = len(OPERATEURS) * len([m for m in font.masters
                                     if m.name not in MASTERS_SANS_MONTEE])
    if calques != attendu:
        raise ValueError(
            f"{calques} calque(s) traite(s) pour {attendu} attendus. Un "
            "operateur monte dans trois masters sur quatre casse "
            "l'interpolation sans qu'aucun controle de glyphe le dise.")
    if log is not None:
        log.append(("operateurs remontes",
                    f"{calques} calque(s), {total} noeud(s), "
                    f"+{MONTEE:.0f} u : {' '.join(OPERATEURS)}"))
    return total
