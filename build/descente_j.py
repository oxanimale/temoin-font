#!/usr/bin/env python3
"""LA QUEUE DU j DESCEND, soixantieme tour. Point ouvert 105.

LA DEMANDE. Nicolas, sur le binaire servi au cinquante-neuvieme tour : le blanc
entre le A et le j est trop grand en texte, sur `Ajouter` et sur `Ajuster`.

LE CHIFFRE QUI L'A JUSTIFIEE, mesure avant d'ecrire quoi que ce soit. Le blanc
vient du +106 que `paires_pieds` ecrit depuis le vingt-neuvieme tour. Il ferme
un chevauchement REEL, mais **le contact ne vit que dans une bande de quatre
unites de haut** : le pied droit du A plonge a -44 depuis le lot 4b, le coin
gauche du crochet du j est a -42, et des y = -30 le jour vaut deja 35 unites.
Atkinson, dont le A ne plonge pas, tient 59,9 unites sans aucun crenage.

CE QUE LE MODULE FAIT. Il descend le crochet du j d'un bloc, par
`coupe.descendre_crochet` : tout point sous `Y_COUPE` est translate, les deux
flancs du fut s'allongent en suivant, et le crochet garde sa forme exacte.
Aucune courbe n'est deformee.

LE PORTEUR N'EST PAS LE `j`, ET CE N'EST PAS UN DETAIL. Le `j` est un COMPOSE
de `jdotless` et de `dotaccentcomb.large` : une entree ecrite sur le nom `j`
ne toucherait aucun contour.

ET C'EST `jdotless` QUI PORTAIT UN CONTACT SERVI QUE PERSONNE NE REGARDAIT.
Il n'est dans aucune des trois tables de paires ni dans `VOISINS_F`, et il est
SHAPE des qu'un `j` recoit une marque combinante : mesure au shaping sur le
binaire servi, `j` + U+0301 rend `jdotless` + `acutecomb` et jamais `jacute`.
`A+jdotless` valait donc -81,0 unites au Bold, dans un etat servi et
atteignable par une saisie, pendant que la table refermait `A+j` a cote.
`jacute` existe dans le binaire et n'est produit par aucune sequence : il
portait le meme contact, sans consequence, comme les sept glyphes
inatteignables du point 88.

Septieme rencontre du defaut de la table indexee par nom, apres `e.sc`, l'AE,
l'Aring, le double `.ti`, les vingt-neuf accentuees de `VOISINS_F` et les
familles du cinquante-neuvieme tour. **Le geste les corrige tous sans nommer
personne**, parce qu'il porte sur le dessin et non sur un nom.

LES VALEURS SONT PAR MASTER, et les quatre masters clairs recoivent ZERO. Leur
jour A+j vaut 75 a 79 unites a crenage nul, la ou Atkinson tient 59,9 : le
projet y est plus large que sa police de base, et rien n'y est a corriger. Le
geste ne vit donc que dans les quatre masters gras, ce qui est la troisieme
valeur par master du projet apres `ALLONGE_T` et `O_TITRAGE`.

    Bold  15      ExtraBold  27      Bold Italic  12      ExtraBold Italic  22

**Le minimum mesure vaut 9, 21, 6 et 16**, et il porte le jour au plancher de
24 unites, rien de plus. Nicolas a retenu SIX UNITES DE PLUS, sur planche, en
texte a 18 px : c'est une decision de dessin et pas une correction de contact,
et `D_MINIMUM` la garde separee pour qu'un controle puisse dire laquelle des
deux une valeur future respecterait.

POURQUOI APRES LE LOT 2 ET LA FUSION, comme `abaisse_U`. `jdotless` porte deja
deux gestes : une coupe du lot 2 sur son bout gauche, et le geste de titrage,
son nom etant dans le perimetre arrete. Descendre le crochet AVANT les
desarmerait -- `loc_gauche` et `loc_alignement` designent des terminaisons a
une hauteur donnee, et le projet a paye ce piege sur le U au quarante-neuvieme
tour, avec un premier essai qui rendait un U sans aucune coupe.

LE GESTE VIT DANS SON MODULE et pas dans `make_temoin`, pour la raison de
`pointe_sommet`, de `bras_O` et d'`abaisse_U` : les deux generateurs de tables
de paires RECONSTRUISENT leur etat au lieu de lire `Temoin.glyphs`, donc une
etape ecrite dans la chaine seule leur serait invisible, et ils mesureraient un
dessin perime. Le projet a paye cet oubli quatre fois.

CE QUE LE GESTE DOIT PRODUIRE, et qui se verifie apres recompilation :
`paires_pieds` doit retirer DE LUI-MEME les +105 et +106. Une table qui les
garderait voudrait dire que le generateur ne voit pas ce module.
"""

import coupe as K
import lot2 as L

#: La hauteur ou le geste coupe le glyphe en deux. Mesure sur les huit masters
#: des deux sources : le crochet rejoint le fut au plus haut a y = 11,0, et
#: AUCUN noeud ne se trouve entre y = 20 et y = 480. La moitie de la hauteur
#: d'x est donc large des deux cotes, et ce n'est pas un nombre choisi au
#: hasard : c'est la seule bande du glyphe ou rien ne se passe.
Y_COUPE = 248.0

#: LA DESCENTE RETENUE PAR NICOLAS, sur la planche, en texte a 18 px. Voir
#: `planche_j.py` et `temoin/tour60-registre.md`.
DESCENTE_J = {
    "ExtraLight": 0.0,
    "Regular": 0.0,
    "Bold": 15.0,
    "ExtraBold": 27.0,
    "ExtraLight Italic": 0.0,
    "Italic": 0.0,
    "Bold Italic": 12.0,
    "ExtraBold Italic": 22.0,
}

#: Le MINIMUM mesure, celui qui porte le jour A+j au plancher `JOUR_MIN` et
#: pas plus. Garde a part de la valeur ecrite : une descente qui tomberait
#: SOUS lui serait un contact, une descente au-dessus est une decision de
#: dessin. Un controle doit pouvoir faire la difference.
D_MINIMUM = {
    "ExtraLight": 0.0,
    "Regular": 0.0,
    "Bold": 9.0,
    "ExtraBold": 21.0,
    "ExtraLight Italic": 0.0,
    "Italic": 0.0,
    "Bold Italic": 6.0,
    "ExtraBold Italic": 16.0,
}

#: Le glyphe qui PORTE le dessin. Un seul, et tout le reste suit par
#: composition : `j`, `jacute` et `ij` le composent, ce qui est verifie a
#: chaque execution par `appliquer` et non supposé.
PORTEUR = "jdotless"

#: Les glyphes qui doivent suivre par COMPOSITION. La liste sert de garde, pas
#: de cible : le module n'y touche pas, il verifie qu'ils composent bien le
#: porteur. Un jour ou l'un d'eux cesserait de le composer, le geste cesserait
#: de l'atteindre sans qu'aucun controle de glyphe le dise.
SUIVEURS = ("j", "jacute")


def descendre(layer, d):
    """Descend le crochet d'un calque. Rend 1 si le geste a eu lieu, 0 sinon.

    LEVE si le contour n'a pas la structure attendue : `coupe.descendre_crochet`
    exige exactement deux segments traversant `Y_COUPE`, tous deux des lignes.
    Un refus vaut mieux qu'une approximation, et c'est la regle du projet
    depuis `make_temoin` refusant la coupe de la queue du t au vingt-deuxieme
    tour.
    """
    faits = 0
    for p in list(L.paths(layer)):
        segs = K.to_segs(p)
        if K.area(segs) < 0:
            continue                      # une contreforme ne descend pas
        layer.shapes[layer.shapes.index(p)] = K.from_segs(
            K.descendre_crochet(segs, float(d), Y_COUPE))
        faits += 1
    return faits


def appliquer(font, log=None, valeurs=None):
    """Descend le crochet du porteur, master par master.

    LEVE si un master attendu ne repond pas : un glyphe descendu dans trois
    masters et intact dans le quatrieme casse l'interpolation du variable sans
    qu'aucun controle de glyphe le dise.
    """
    table = DESCENTE_J if valeurs is None else valeurs
    g = font.glyphs[PORTEUR]
    if g is None:
        raise ValueError(f"{PORTEUR} absent de la source")
    # LA COMPOSITION SE VERIFIE, elle ne se suppose pas. C'est le defaut que ce
    # geste corrige : un nom ne suit pas un dessin.
    ids = {m.id: m.name for m in font.masters}
    for nom in SUIVEURS:
        gs = font.glyphs[nom]
        if gs is None:
            continue
        lay = [l for l in gs.layers if l.layerId in ids]
        if not lay:
            continue
        compose = any(getattr(s, "componentName", None) == PORTEUR
                      for s in lay[0].shapes)
        if not compose:
            raise ValueError(
                f"{nom} ne compose plus {PORTEUR} : le geste ne l'atteindrait "
                "pas, et rien d'autre ne le dirait.")
    total, touches = 0, 0
    for l in g.layers:
        if l.layerId not in ids:
            continue
        mn = ids[l.layerId]
        if mn not in table:
            raise ValueError(f"{PORTEUR} : le master {mn} n'a pas de valeur. "
                             "Un master sans valeur casse l'interpolation.")
        d = table[mn]
        total += 1
        if not d:
            continue
        n = descendre(l, d)
        if n != 1:
            raise ValueError(
                f"{PORTEUR} {mn} : {n} contour(s) descendu(s) pour un seul "
                "attendu. Le geste de titrage a-t-il eu lieu ? Ce module "
                "passe APRES la fusion, jamais avant.")
        touches += 1
    # LE COMPTE EST UNE EXIGENCE, PAS UNE INFORMATION. Quatre masters portent
    # une valeur non nulle dans chaque source, et rien d'autre n'est
    # acceptable : un compte qui ne tombe pas veut dire qu'un master a ete
    # apparie par un identifiant au lieu de son nom, et `kern` comme les
    # calques rendent alors du silence.
    attendu = sum(1 for m in ids.values() if table.get(m))
    if touches != attendu:
        raise ValueError(
            f"{touches} master(s) descendu(s) pour {attendu} attendus sur "
            f"{total} lus.")
    if log is not None:
        log.append(("queue du j descendue",
                    f"{touches} master(s), "
                    + ", ".join(f"{m} {table[m]:.0f}"
                                for m in ids.values() if table.get(m))))
    return touches
