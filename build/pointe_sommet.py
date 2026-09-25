"""L'operation du quarante-et-unieme tour : POINTER UN SOMMET ARRONDI.

Nicolas, en navigateur sur le dessin fusionne : "l'accent circonflexe parait
tres fin", puis, une fois le probleme pose comme une question de graisse : "je
pense que s'arranger pour que la partie haute fasse une pointe plutot qu'elle
soit dullee comme elle est actuellement resoudrait le probleme".

CE QUE L'OPERATION N'EST PAS. Ce n'est pas `coupe.pointe`, qui effile une
TERMINAISON -- un segment droit entre deux flancs, comme le bout de la cedille
ou celui de l'ogonek. Le sommet du circonflexe n'est pas un bout : c'est la
rencontre de deux flancs, fermee par un arc en deux demi-courbes. Il n'y a rien
a effiler, il y a un arc a remplacer par un angle.

CE QU'ELLE FAIT. Elle prolonge les deux flancs exterieurs jusqu'a leur
intersection et remplace les deux demi-courbes du sommet par deux lignes.
L'epaisseur du trait n'est pas touchee, l'angle du chevron non plus, les deux
bouts bas non plus : SEUL LE SOMMET CHANGE. C'est ce qui la rend sure -- toute
autre facon de pointer (redresser les flancs, rapprocher les points de
controle) deplace de la matiere ailleurs et change une proportion que personne
n'a demande de changer.

LE PIEGE QU'ELLE EVITE, et qui est ecrit dans la passation depuis le
dix-septieme tour : raccorder deux bouts par l'intersection de leurs tangentes
explose des que les tangentes sont presque paralleles -- c'est ce qui avait
envoye la virgule de la cedille a plusieurs milliers d'unites sous la ligne de
base. Ici les deux flancs font 84 a 91 degres l'un avec l'autre selon le
master, mesure : l'intersection est franche et bornee. La fonction REFUSE
quand l'angle passe sous un seuil, au lieu de rendre un point lointain.

LA TOPOLOGIE. C'est interpolable tant que TOUS les masters recoivent le geste,
ce que `pointer_font` garantit en levant si un master resiste -- un glyphe
pointu dans trois masters et arrondi dans le quatrieme casse le variable en
silence.

CE PARAGRAPHE ANNONCAIT "16 noeuds deviennent 12", ET C'ETAIT FAUX.
Quarante-neuvieme tour, trente-troisieme chiffre corrige de ce projet, et c'est
le temoin de `check_circonflexe` qui l'a trouve avant Nicolas. Mesure sur les
huit calques des deux sources : le contour porte DOUZE noeuds et HUIT segments
avant comme apres. Le geste remplace deux demi-courbes par deux lignes et en
ajoute deux ailleurs dans le meme contour, donc le compte est invariant. LA
GRANDEUR QUI DIT QUE LA POINTE EST LA EST LE TYPE DES DEUX SEGMENTS QUI SE
RENCONTRENT AU SOMMET : `curve`+`curve` a l'amont, `line`+`line` apres. Un
controle bati sur le compte de noeuds serait reste au vert sur un accent rendu
a Atkinson.
"""

import math

import coupe as K
from glyphsLib.classes import GSPath, GSComponent


#: Sous cet angle entre les deux flancs, l'intersection part trop loin pour
#: etre un sommet : la fonction refuse au lieu de rendre un point. La valeur
#: est large -- le circonflexe mesure 84 a 91 degres -- et elle n'est pas la
#: pour ce glyphe-ci mais pour le jour ou l'operation servira ailleurs.
ANGLE_MINI = 25.0

#: Au-dela de cette montee, rapportee a la hauteur du chevron, l'intersection
#: n'est plus un sommet mais une fleche. Meme raison : borner au lieu de subir.
MONTEE_MAXI = 0.45


def _ymax_idx(segs):
    """L'indice du segment dont le point d'arrivee est le plus haut."""
    return max(range(len(segs)), key=lambda i: segs[i]["p3"][1])


def pointer(segs, i_sommet=None, cible=None):
    """Remplace l'arc du sommet par l'angle des deux flancs prolonges.

    `i_sommet` est le segment qui ARRIVE au sommet ; laisse a None, il est
    trouve par l'ordonnee maximale. Les deux flancs sont alors les segments qui
    precedent et suivent la paire d'arcs.

    `cible` force l'ordonnee du sommet au lieu de prendre l'intersection : les
    deux flancs sont prolonges jusqu'a cette hauteur et se rejoignent par un
    plat residuel. Sert a la voie "pointe alignee" des capitales, ou la pointe
    doit arriver exactement au plafond deja occupe par l'aigu et le grave.

    Rend `(segs, journal)`. Le journal porte la montee obtenue et l'angle
    mesure : un geste qui ne dit pas ce qu'il a fait ne se controle pas, et ce
    projet a paye trois fois un journal qu'aucun controle ne lisait.
    """
    segs = [dict(s, c=list(s["c"])) for s in segs]
    n = len(segs)
    if i_sommet is None:
        i_sommet = _ymax_idx(segs)
    # i_sommet ARRIVE au sommet ; le suivant en repart. Les flancs les encadrent.
    ia = (i_sommet + 1) % n
    flanc_av = (i_sommet - 1) % n        # avant l'arc
    flanc_ap = (ia + 1) % n              # apres l'arc

    A0, A1 = segs[flanc_av]["p0"], segs[flanc_av]["p3"]
    B0, B1 = segs[flanc_ap]["p0"], segs[flanc_ap]["p3"]
    uA = (A1[0] - A0[0], A1[1] - A0[1])
    uB = (B1[0] - B0[0], B1[1] - B0[1])
    aA = math.degrees(math.atan2(uA[1], uA[0]))
    aB = math.degrees(math.atan2(uB[1], uB[0]))
    ecart = abs(((aA - aB + 180.0) % 360.0) - 180.0)
    angle = 180.0 - ecart if ecart > 90.0 else ecart
    if angle < ANGLE_MINI:
        raise ValueError(
            f"flancs a {angle:.1f} degres, sous le seuil de {ANGLE_MINI} : "
            "l'intersection n'est pas un sommet")

    y_arc = max(segs[i_sommet]["p3"][1], A1[1], B0[1])
    if cible is None:
        P = K.inter_droites(K.V(A0), K.unit(K.V(A1) - K.V(A0)),
                            K.V(B1), K.unit(K.V(B1) - K.V(B0)))
        if P is None:
            raise ValueError("flancs paralleles : aucune intersection")
        sommet = (float(P[0]), float(P[1]))
    else:
        sommet = None

    epaules_y = (A1[1] + B0[1]) / 2.0
    haut_chevron = y_arc - min(A0[1], B1[1])

    if cible is None:
        montee = sommet[1] - segs[i_sommet]["p3"][1]
        if haut_chevron > 0 and montee / haut_chevron > MONTEE_MAXI:
            raise ValueError(
                f"montee de {montee:.1f} u pour un chevron de {haut_chevron:.1f} : "
                "l'intersection fait une fleche, pas un sommet")
        # les deux demi-arcs deviennent deux lignes vers le point d'intersection
        segs[i_sommet] = {"kind": "line", "p0": A1, "c": [],
                          "p3": sommet, "smooth": False}
        segs[ia] = {"kind": "line", "p0": sommet, "c": [],
                    "p3": B0, "smooth": False}
    else:
        # Prolongement borne : chaque flanc monte jusqu'a `cible`, et le plat
        # residuel entre les deux points obtenus ferme le sommet. Quand la
        # cible vaut l'intersection, le plat est nul et le resultat est le
        # meme que ci-dessus -- les deux voies ne se contredisent pas.
        def sur_flanc(P0, P1, y):
            dx, dy = P1[0] - P0[0], P1[1] - P0[1]
            if abs(dy) < 1e-9:
                raise ValueError("flanc horizontal : aucune hauteur a viser")
            t = (y - P0[1]) / dy
            return (P0[0] + t * dx, y)
        G = sur_flanc(A0, A1, cible)
        D = sur_flanc(B1, B0, cible)
        montee = cible - segs[i_sommet]["p3"][1]
        segs[i_sommet] = {"kind": "line", "p0": A1, "c": [],
                          "p3": G, "smooth": False}
        segs[ia] = {"kind": "line", "p0": G, "c": [],
                    "p3": D, "smooth": False}
        segs.insert(ia + 1, {"kind": "line", "p0": D, "c": [],
                             "p3": B0, "smooth": False})
        sommet = ((G[0] + D[0]) / 2.0, cible)

    journal = {"angle": round(angle, 2), "montee": round(montee, 2),
               "sommet": (round(sommet[0], 1), round(sommet[1], 1)),
               "epaules": round(epaules_y, 1),
               "plat_avant": round(abs(B0[0] - A1[0]), 1)}
    return segs, journal


def pointer_layer(layer, cible=None):
    """Applique `pointer` au contour le plus haut du calque, sur place."""
    paths = [s for s in layer.shapes if isinstance(s, GSPath)]
    if not paths:
        raise ValueError("aucun contour propre : glyphe composite")
    # le contour qui porte le point le plus haut
    def haut(p):
        return max(n.position.y for n in p.nodes)
    p = max(paths, key=haut)
    segs, jr = pointer(K.to_segs(p), cible=cible)
    neuf = K.from_segs(segs)
    # Remplacer le CONTENU du contour, jamais l'objet : la collection de formes
    # de glyphsLib n'accepte pas toujours l'affectation par indice, et le
    # projet a paye cette lecon sur les calques au dix-septieme tour.
    i = layer.shapes.index(p)
    layer.shapes[i] = neuf
    return jr


def appliquer(font, log=None):
    """LE GESTE DU TOUR, ET LE SEUL ENDROIT QUI LE RESOUT.

    Il vit ici et non dans `make_temoin` parce que la chaine n'est pas seule a
    devoir l'appliquer : les deux generateurs de tables de paires RECONSTRUISENT
    leur etat au lieu de lire `Temoin.glyphs`, donc ils doivent rejouer la meme
    etape ou mesurer un dessin perime. Le quarantieme tour l'a appris sur la
    fusion, et la lecon est ecrite : DEUX CODES QUI APPLIQUENT LE MEME ETAT
    DOIVENT PASSER PAR LA MEME FONCTION.

    Le geste, en deux moitiés :

      bas de casse   POINTE PLEINE sur `circumflexcomb`. Les deux flancs
                     exterieurs prolonges jusqu'a leur intersection. Montee de
                     24,1 a 25,7 unites selon le master, identique au romain et
                     en italique. Gratuite : 726 devient 751 au Bold pour un
                     plafond de repertoire a 883.
      capitale       POINTE ALIGNEE. `circumflexcomb.case` n'est qu'un
                     composant decale ; on lui retire sa propre montee, master
                     par master, et le sommet retombe EXACTEMENT ou il etait --
                     par construction, puisqu'on soustrait au composant ce
                     qu'on vient d'ajouter au composé. Mesure : 866,96 au
                     Regular, 883,05 au Bold, 886,0 a l'ExtraBold, contre 867,
                     883 et 886 avant.

    POURQUOI LES CAPITALES N'ONT PAS LA POINTE PLEINE : les capitales a
    circonflexe sont au PLAFOND DU REPERTOIRE SERVI, a egalite ou presque avec
    `acutecomb.case` et `gravecomb.case`. La pointe pleine ferait du A
    circonflexe le point le plus haut de la police, 25 unites au-dessus de tous
    les autres accents de capitale.

    CE QUE L'ALIGNEMENT COUTE, limite connue : le blanc entre la hauteur de
    capitale et le bas de l'accent passe de 79 a 53 unites au Regular, de 71 a
    47 en ExtraLight, de 63 a 38 au Bold et de 60 a 34 a l'ExtraBold.

    LE CARON GARDE SON ARC, tranche par Nicolas sur
    `planche-circonflexe-5-caron.png`. `caroncomb` est le meme dessin retourne,
    donc deux glyphes jusqu'ici identiques divergent : c'est une LIMITE CONNUE
    et non un oubli, justifiee par l'emploi -- la police est faite pour le
    francais, qui n'a pas de caron. `pointer` s'y appliquerait en cherchant
    l'ordonnee minimale.
    """
    journal = []
    pointer_font(font, ["circumflexcomb"], journal=journal)
    montees = {mas: jr["montee"] for _, mas, jr in journal}
    mid = {m.id: m.name for m in font.masters}
    g = font.glyphs["circumflexcomb.case"]
    if g is None:
        raise ValueError("circumflexcomb.case absent : l'accent de capitale "
                         "n'est plus un composant, le geste ne s'aligne plus")
    alignes = 0
    for l in g.layers:
        if l.layerId not in mid:
            continue
        trouve = False
        for s in l.shapes:
            if isinstance(s, GSComponent) and s.componentName == "circumflexcomb":
                t = list(s.transform)
                t[5] -= montees[mid[l.layerId]]
                s.transform = tuple(t)
                trouve = True
        if not trouve:
            raise ValueError(
                f"circumflexcomb.case {mid[l.layerId]} ne compose pas "
                "circumflexcomb : l'alignement porterait sur rien")
        alignes += 1
    if log is not None:
        log.append(("accent pointe", f"{len(journal)} calques, montee "
                    f"{min(montees.values()):.1f} a {max(montees.values()):.1f} u"))
        log.append(("accent capitale aligne", f"{alignes} calques"))
    return montees


def pointer_font(font, noms, cible_par_master=None, journal=None):
    """Pointe `noms` dans TOUS les masters, ou leve.

    Un glyphe pointu dans trois masters et arrondi dans le quatrieme casse
    l'interpolation du variable sans qu'aucun controle de glyphe le dise : la
    topologie differe, et fontmake s'en plaint tard ou pas du tout. La fonction
    exige donc que chaque master reponde, et rend le compte de ce qu'elle a
    touche pour qu'un appelant puisse le verifier.
    """
    mid = {m.id: m for m in font.masters}
    faits = 0
    for nom in noms:
        g = font.glyphs[nom]
        if g is None:
            raise ValueError(f"{nom} absent de la source")
        for l in g.layers:
            if l.layerId not in mid:
                continue
            cible = None
            if cible_par_master:
                cible = cible_par_master.get(mid[l.layerId].name)
            jr = pointer_layer(l, cible=cible)
            if journal is not None:
                journal.append((nom, mid[l.layerId].name, jr))
            faits += 1
    return faits
