#!/usr/bin/env python3
"""LE U REDESCEND SOUS LA LIGNE DE CAPITALE, quarante-neuvieme tour.

LA DEMANDE. Nicolas, en navigateur sur `tour49.html` : "il faut faire
redescendre la hauteur pour que les pointes atteignent la ligne haute des
autres majuscules, sans reduire le geste - et ca arrangera le probleme de
l'accent circonflexe".

LE CHIFFRE QUI L'A JUSTIFIEE, mesure sur la source servie AVANT d'ecrire quoi
que ce soit. Le blanc entre le sommet de la lettre et le bas de son accent
circonflexe, master par master au romain :

    Â, Ê   46,9   53,4   38,0   34,3
    Ô      34,9   41,4   26,0   22,3
    Û       2,9    9,4   -6,0   -9,7

Au Bold et a l'ExtraBold LE BLANC EST NEGATIF : la pointe du U entre dans
l'accent de 6,0 et 9,7 unites. Ce n'est pas une gene de lecture, c'est un
chevauchement, et aucun controle du projet ne le voyait -- ils mesurent des
bouts, des couloirs et des contacts entre lettres voisines, jamais le blanc
entre une base et sa marque.

CE QUE LE MODULE FAIT. Il descend de 44 unites les DEUX EXTREMITES du bout haut
de chaque branche du U, apres que le geste de titrage les a coupees. Le bout
garde donc son inclinaison -- le geste n'est pas reduit, il vaut toujours 44
unites entre ses deux coins -- et les deux flancs verticaux qui l'encadrent
raccourcissent d'autant. Mesure apres ecriture, sur les huit masters des deux
sources : sommet du U a 668,0 exactement, a egalite avec le A et le E ; bout
haut de 44,0 unites ; et le blanc sous l'accent du Û devient EGAL a celui du
Â, dans chaque master.

POURQUOI APRES LE GESTE ET NON AVANT, et c'est un essai qui l'a tranche.
Descendre le bout AVANT le reglage le desarme : `loc_alignement` designe les
terminaisons POSEES SUR UN ALIGNEMENT, donc un bout descendu a 624 n'est plus
sur la hauteur de capitale et le geste ne s'y pose plus. Le premier essai a
rendu un U a 624 sans aucune coupe. C'est le piege ecrit depuis le trente-
septieme tour -- sur l'etat servi, huit localisateurs du projet ne designent
plus leur cible -- retombe dans une etape de chaine.

POURQUOI PAS `coupe.allonge` AVEC UNE DISTANCE NEGATIVE. Elle translate la
droite du bout le long de sa NORMALE SORTANTE, ce qui est exact sur un bout
horizontal et faux sur un bout coupe : apres le geste, le bout du U penche de
14 a 38 degres selon le master, donc la normale n'est plus verticale. A 38
degres, une poussee de 44 ne ferait descendre que 34,7 unites et decalerait le
bout de 27 sur le cote. La translation verticale des deux coins est le geste
juste, et elle est exacte parce que les deux flancs sont verticaux.

VALIDE PAR NICOLAS EN NAVIGATEUR, sur `gabarits/tour49.html` et sur le BINAIRE
SERVI, section 3 : le U et ses cinq accentuees aux quatre masters, plus "coût",
"bûche", "sûr", "DÛMENT", "SÛRETÉ" a la taille de lecture. Ou le regard a eu
lieu compte autant que le regard.

LE PRIX, MESURE ET ASSUME. Le U n'etait pas seul a depasser la ligne de
capitale : le H et le N montent aussi a 712, par leur sommet de fut droit. Le U
descendu a 668 devient donc la seule capitale a fut qui ne depasse plus, comme
le K est devenu au quarante-troisieme tour la seule capitale a fut sans
plongee. Le prix est connu avant d'etre pris.

LE GESTE VIT DANS SON MODULE et pas dans `make_temoin`, pour la raison de
`pointe_sommet` et de `bras_O` : les deux generateurs de tables de paires
RECONSTRUISENT leur etat au lieu de lire `Temoin.glyphs`, donc une etape ecrite
dans la chaine seule leur serait invisible, et ils mesureraient un dessin
perime.
"""

import coupe as K
import lot2 as L

#: De combien le bout descend. Constante et non par master : le geste de
#: titrage sort de 44,0 unites exactement dans les huit masters des deux
#: sources -- mesure, et non deduit de la cible -- donc une seule valeur ramene
#: partout le sommet a la hauteur de capitale.
BAISSE = 44.0

#: Les glyphes qui recoivent l'abaissement. Le U seul : ses six accentuees sont
#: des COMPOSITES purs et suivent, ce qui est verifie et non suppose, et `u.sc`
#: en derive par le lot 3, qui passe apres.
#:
#: LE `u` BAS DE CASSE N'EST PAS ICI, et ce n'est pas un oubli : son geste est
#: une RENTRANTE du haut, l'une des deux seules exceptions au regime tranche au
#: trente-cinquieme tour, et elle ne fait rien depasser.
PORTEURS = ("U",)

#: La tolerance pour reconnaitre le bout au sommet du contour. Un demi-point,
#: comme partout dans ce projet : le geste laisse les deux coins a 668 et 712,
#: donc rien n'est ambigu a cette echelle.
TOL = 0.5


#: Au-dela de cette pente, un segment qui touche le sommet est un FLANC et non
#: un bout. C'est `lot4.PENTE_BAS`, la valeur que le projet emploie depuis le
#: trente-septieme tour pour reconnaitre un bout DEJA COUPE : le bout du U
#: penche de 25 degres apres le geste, soit une pente de 0,47, et les flancs
#: sont verticaux.
PENTE = 0.80


def bouts_hauts(segs, tol=TOL, pente=PENTE):
    """Les segments DROITS, PEU INCLINES, dont une extremite touche le sommet.

    Le U en a DEUX, un par branche, a la meme hauteur. `lot2.loc_sommet_fut`
    ne peut pas servir : il rend `[max(cand, key=...)]`, donc UN seul segment,
    et sur deux ex aequo il attribue au premier venu. Le projet a paye ce
    defaut sur le plafond du repertoire, annonce a `Aring` alors que la barre
    verticale y etait a egalite -- une mesure qui rend un nom unique cache les
    ex aequo.

    LE FILTRE DE PENTE N'EST PAS UNE PRECAUTION, ET C'EST UN COMPTE QUI L'A
    DIT. Un premier jet ne demandait qu'une extremite au sommet : apres le
    geste, le coin haut du bout est AUSSI l'extremite haute de son flanc, donc
    les deux flancs entraient dans la selection -- 433 et 440 unites de long au
    Regular -- et leur extremite BASSE, a la jonction avec la panse du U,
    descendait de 44 unites avec le reste. La lettre se serait deformee a
    mi-hauteur. Rien ne le signalait : le sommet, le bas du bout et le geste
    mesuraient tous trois la bonne valeur. Ce qui l'a rendu est le JOURNAL, qui
    annoncait 24 coins deplaces par source la ou 16 sont attendus -- 2 bouts x
    2 coins x 4 masters. Un compte qui ne tombe pas est un fait, et celui-la a
    ete lu avant que Nicolas ne voie la forme.
    """
    if not segs:
        return []
    top = max(max(s["p0"][1], s["p3"][1]) for s in segs)
    out = []
    for i, s in enumerate(segs):
        if s["kind"] != "line":
            continue
        if max(s["p0"][1], s["p3"][1]) < top - tol:
            continue
        dx = abs(s["p3"][0] - s["p0"][0])
        dy = abs(s["p3"][1] - s["p0"][1])
        if dy <= pente * dx:
            out.append(i)
    return out


def descendre(layer, d=BAISSE, tol=TOL):
    """Descend de `d` les deux extremites de chaque bout haut. Rend le compte.

    Le deplacement se fait sur les NOEUDS du contour et non sur les segments,
    parce qu'un coin est partage par deux segments : le bout et son flanc. Les
    deplacer par les segments le bougerait deux fois.
    """
    faits = 0
    for p in list(L.paths(layer)):
        segs = K.to_segs(p)
        vises = bouts_hauts(segs, tol)
        if not vises:
            continue
        cles = set()
        for i in vises:
            for q in (segs[i]["p0"], segs[i]["p3"]):
                cles.add((round(q[0], 2), round(q[1], 2)))
        for nd in p.nodes:
            if (round(nd.position.x, 2), round(nd.position.y, 2)) in cles:
                nd.position = type(nd.position)(nd.position.x,
                                                nd.position.y - d)
                faits += 1
    return faits


def appliquer(font, log=None):
    """Descend les bouts hauts des `PORTEURS`, dans tous les masters.

    LEVE si un master ne repond pas. Un glyphe descendu dans trois masters et
    intact dans le quatrieme casse l'interpolation du variable sans qu'aucun
    controle de glyphe le dise, et fontmake s'en plaint tard ou pas du tout --
    c'est la garde que `pointe_sommet.pointer_font` porte pour la meme raison.
    """
    ids = {m.id: m.name for m in font.masters}
    total = 0
    for nom in PORTEURS:
        g = font.glyphs[nom]
        if g is None:
            raise ValueError(f"{nom} absent de la source")
        vus = 0
        for l in g.layers:
            if l.layerId not in ids:
                continue
            n = descendre(l)
            if not n:
                raise ValueError(
                    f"{nom} {ids[l.layerId]} : aucun bout haut trouve. Le "
                    "geste de titrage a-t-il eu lieu ? Ce module passe APRES "
                    "la fusion, jamais avant.")
            vus += 1
            total += n
    # LE COMPTE EST UNE EXIGENCE, PAS UNE INFORMATION. Deux bouts, deux coins
    # chacun, quatre masters : seize coins par source, et rien d'autre n'est
    # acceptable. C'est ce compte qui a revele que les flancs entraient dans la
    # selection, et le laisser en simple ligne de journal aurait rendu la
    # decouverte dependante de qui la lit.
    attendu = 16 * len(PORTEURS)
    if total != attendu:
        raise ValueError(
            f"{total} coin(s) deplace(s) pour {attendu} attendus. Deux bouts, "
            "deux coins, quatre masters : tout autre compte veut dire que la "
            "selection a pris un segment qui n'est pas un bout, et la lettre "
            "se deformerait ailleurs sans que rien ne le dise.")
    if log is not None:
        log.append(("U redescendu",
                    f"{total} coin(s) sur {len(PORTEURS)} glyphe(s), "
                    f"-{BAISSE:.0f} u"))
    return total
