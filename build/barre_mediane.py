#!/usr/bin/env python3
"""Temoin, point 94 : la barre mediane du F et de l'E dans les masters gras.

LE DEFAUT EST D'ATKINSON, ET IL EST MESURE. Le centre de la barre mediane du F
vaut 344,0 en ExtraLight, 343,5 au Regular, 313,5 au Bold et 308,0 a
l'ExtraBold, quand l'E tient 343,5 sur tout l'axe. Ce n'est pas un
amaigrissement : les deux barres ont la MEME epaisseur, 139,0 au Bold dans les
deux lettres, 150,0 contre 149,0 a l'ExtraBold. Celle du F est descendue tout
entiere, section pleine comprise, de 30,0 et 35,5 unites. L'italique porte
exactement le meme decrochage, aux memes valeurs.

CE QUE NICOLAS A TRANCHE, sur `planche-F6-partages-romain.png` et ses cinq
etats. Aligner les deux a 343,5 tasse la lettre vers le haut : il a retenu le
partage de la MOITIE, l'E descendant autant que le F monte. La barre commune
tombe donc a 328,5 au Bold et 326,0 a l'ExtraBold, sous la jonction du B, qui
reste a 343,0 et 342,5 et ne bouge pas.

LA TABLE PORTE LA CIBLE, PAS LE DEPLACEMENT. Ecrire les deplacements ferait
deux valeurs par master et par glyphe, qui ne se relisent pas ; ecrire la
hauteur voulue fait une valeur, qui EST la decision, et le module mesure ce
qu'il faut pour l'atteindre. Le journal rend les deplacements obtenus.

LES CINQ NOMS, ET LA MESURE QUI LES A DESIGNES. L'AE, l'OE et l'Eogonek
portent la meme barre que l'E -- meme hauteur, meme epaisseur, dans les huit
masters -- mais ils la DESSINENT en contours propres au lieu de composer l'E.
Une table indexee par nom ne suit pas une composition : le projet l'a paye six
fois, sur `e.sc`, sur l'AE et l'Aring, sur le double `.ti` et sur le
`tcedilla`. Les sept capitales accentuees -- Eacute, Egrave, Ecircumflex,
Edieresis, Ecaron, Edotaccent, Emacron -- composent l'E et suivent sans etre
nommees ; les quatre petites capitales suivent par la derivation du lot 3.

SA PLACE DANS LA CHAINE : apres `operateurs`, donc apres la fusion du titrage,
et AVANT le lot 3. Apres la fusion, parce que le bout de la barre mediane du F
porte une coupe depuis le lot 2 et que cette coupe doit VOYAGER avec la barre au
lieu d'etre reappliquee. Avant le lot 3, pour que `f.sc`, `e.sc`, `ae.sc` et
`oe.sc` heritent du geste : mesure faite, `f.sc` derive du F remonte s'aligne
sur `e.sc` a 0,05 unite pres dans les huit masters, et rien ne s'ecrit sur les
44 petites capitales.

LE GESTE VIT DANS SON MODULE et pas dans `make_temoin`, comme `bras_O`,
`pointe_sommet` et `operateurs` : les deux generateurs de tables de paires
RECONSTRUISENT leur etat au lieu de lire `Temoin.glyphs`, donc ils doivent
pouvoir rejouer cette etape. C'est d'autant plus necessaire ici qu'aucun
garde-fou existant ne voit ce geste -- la barre mediane gouverne le blanc a
droite du F, et `inventaire_F` a rendu un zero-diff exact sur ses 383 paires
quand `check_approches` criait douze fois sur le meme etat.
"""

from glyphsLib.classes import GSPath

import dessin as D


#: (deplacement du F, deplacement de la famille de l'E), par master, en
#: unites. TROISIEME valeur par master du projet, apres `lot2.ALLONGE_T` et les
#: deux champs par master de `lot4.O_TITRAGE`.
#:
#: UN DEPLACEMENT, ET PAS UNE HAUTEUR CIBLE, et c'est le garde-fou de ce module
#: qui l'a impose au premier essai : l'OE ExtraLight porte sa barre a 343,5
#: quand l'E la porte a 344,0, un ecart de 0,5 unite qui vit dans Atkinson et
#: que personne n'avait mesure. Une cible absolue l'aurait corrige en silence,
#: dans un master que Nicolas a valide tel quel. Un deplacement preserve les
#: ecarts de la famille et ne touche que ce que la decision nomme.
#:
#: L'ExtraLight et le Regular portent zero, ecrit et non saute : le module
#: MESURE qu'ils ne bougent pas au lieu de les ignorer.
DEPLACEMENTS = {
    "ExtraLight": (0.0, 0.0),
    "Regular": (0.0, 0.0),
    "Bold": (15.0, -15.0),
    "ExtraBold": (18.0, -17.5),
    "ExtraLight Italic": (0.0, 0.0),
    "Italic": (0.0, 0.0),
    "Bold Italic": (15.0, -15.0),
    "ExtraBold Italic": (18.0, -17.5),
}

#: (nom, fraction de la boite ou commence le balayage). L'AE et l'OE dessinent
#: autre chose a gauche de leur E, et un balayage parti du bord gauche y rend
#: la barre du A : 241,6 en ExtraLight et 343,5 au Bold, deux objets differents
#: sous un seul nombre.
GLYPHES = (("F", 0.0), ("E", 0.0), ("AE", 0.55), ("OE", 0.65), ("Eogonek", 0.0))

#: Les noms qui descendent avec l'E. Ils portent la meme barre que lui a 0,5
#: unite pres, et ils la DESSINENT au lieu de composer l'E.
SOLIDAIRES = ("E", "AE", "OE", "Eogonek")

BANDE = (240.0, 460.0)      # ou chercher la barre mediane, en unites
EP_MAX = 210.0              # au-dela, l'intervalle n'est pas une barre
NOEUDS = 4                  # deux a la jonction du fut, deux au bout
TOL_BORD = 0.6              # un noeud est SUR un bord, pas dans l'intervalle
MARGE_X = 100.0             # a gauche de la colonne ou la barre se separe


def intervalles(contours, x, tol=1e-9):
    """Intervalles d'encre sur la verticale d'abscisse x, remplissage non nul."""
    evts = []
    for c in contours:
        n = len(c)
        for i in range(n):
            x1, y1 = c[i]
            x2, y2 = c[(i + 1) % n]
            if (x1 > x) == (x2 > x) or abs(x2 - x1) < tol:
                continue
            t = (x - x1) / (x2 - x1)
            evts.append((y1 + t * (y2 - y1), 1 if x2 > x1 else -1))
    evts.sort()
    out, w, deb = [], 0, None
    for y, d in evts:
        prev = w
        w += d
        if prev == 0 and w != 0:
            deb = y
        elif prev != 0 and w == 0 and deb is not None:
            out.append((deb, y))
            deb = None
    return out


def barre(src, nom, depart=0.0):
    """(bas, haut, x) de la barre mediane, par balayage d'encre.

    PAS DE SONDE DU FUT A HAUTEUR FIXE. Dans les gras la barre HAUTE du F
    descend jusqu'a 529 : une sonde a 560 rend le bord droit du glyphe entier,
    et la mesure tombe muette dans les quatre masters ou la question se pose.
    Le balayage cherche, colonne par colonne, un intervalle d'encre ISOLE dont
    le centre est dans la bande mediane. La PREMIERE colonne trouvee est contre
    le fut, la ou la barre a sa section pleine, avant que la coupe du bout ne
    la mange.
    """
    cs = src.contours(nom)
    if not cs:
        raise ValueError(f"{nom} : aucun contour")
    xs = [p[0] for c in cs for p in c]
    x0, x1 = min(xs), max(xs)
    deb = x0 + (x1 - x0) * depart
    n = 400
    for i in range(n + 1):
        x = deb + (x1 - deb) * i / n
        cand = [s for s in intervalles(cs, x)
                if BANDE[0] <= (s[0] + s[1]) / 2 <= BANDE[1]
                and (s[1] - s[0]) <= EP_MAX]
        if len(cand) == 1:
            return cand[0][0], cand[0][1], x
    raise ValueError(f"{nom} : aucune colonne isolee a partir de {depart:.2f}")


def centre(src, nom, depart=0.0):
    b, h, _ = barre(src, nom, depart)
    return (b + h) / 2.0


def _translater(font, nom, depart, mas, layer, dy):
    """Deplace les quatre noeuds de la barre, ou leve.

    DEUX FILTRES, ET LES DEUX SONT NECESSAIRES. L'ordonnee se prend SUR LES
    BORDS et non dans l'intervalle : l'OE porte des noeuds de son O a
    mi-hauteur, dont (46 ; 273) en Bold Italic, a UNE unite du bord bas de la
    barre. L'abscisse se prend sur la colonne ou la barre se separe du fut et
    non sur une fraction de la boite : la fraction ecartait le noeud de jonction
    gauche de l'AE en italique, ou le fut penche.

    LEVE plutot que de rendre une lettre a moitie deplacee. Un compte qui ne
    tombe pas est un fait, et c'est ainsi qu'`abaisse_U` a trouve le sien.
    """
    src = D.Source(font, mas)
    bas, haut, x_col = barre(src, nom, depart)
    x_min = x_col - MARGE_X
    w_avant = layer.width
    n_avant = sum(len(s.nodes) for s in layer.shapes if isinstance(s, GSPath))
    vises = 0
    for s in layer.shapes:
        if not isinstance(s, GSPath):
            continue
        for nd in s.nodes:
            y = nd.position.y
            if min(abs(y - bas), abs(y - haut)) > TOL_BORD:
                continue
            if nd.position.x < x_min:
                continue
            if dy:
                nd.position = (nd.position.x, y + dy)
            vises += 1
    if vises != NOEUDS:
        raise ValueError(
            f"barre_mediane : {nom} {mas} rend {vises} noeuds, {NOEUDS} attendus")
    n_apres = sum(len(s.nodes) for s in layer.shapes if isinstance(s, GSPath))
    if layer.width != w_avant or n_apres != n_avant:
        raise ValueError(
            f"barre_mediane : {nom} {mas} a perdu sa chasse ou sa topologie")
    return bas, haut


def appliquer(font, log=None, sens=1):
    """Deplace la barre mediane du F et de la famille de l'E, master par master.

    Rend le journal : (nom, master, avant, apres, deplacement).

    `sens=-1` REJOUE LE GESTE A L'ENVERS, et ce n'est pas une commodite : un
    controle qui veut imputer un couloir a ce geste doit le comparer a l'etat
    ECRIT prive du geste, jamais a la source amont, sans quoi il impute a la
    translation tout ce que le projet a fait au voisin. Le piege a ete paye au
    cinquante-troisieme tour sur `check_operateurs`. La verification finale ne
    tourne qu'a l'endroit : a l'envers, le F et l'E ne coincident plus, ce qui
    est precisement ce qu'on veut mesurer.
    """
    mid = {m.id: m.name for m in font.masters}
    journal = []
    avant_tout = {}
    for mas in (m.name for m in font.masters):
        if mas not in DEPLACEMENTS:
            # Une entree dont la valeur depend du master doit LEVER quand le
            # master manque : retomber sur zero rendrait une lettre non
            # modifiee, plausible et fausse. C'est la regle de
            # `lot2.valeur_master`.
            raise ValueError(f"barre_mediane : aucun deplacement pour le master {mas}")
        src = D.Source(font, mas)
        avant_tout[mas] = {n: centre(src, n, d) for n, d in GLYPHES}
    for nom, depart in GLYPHES:
        g = font.glyphs[nom]
        if g is None:
            raise ValueError(f"barre_mediane : {nom} absent de la source")
        for layer in g.layers:
            mas = mid.get(layer.layerId)
            if mas is None:
                continue
            dF, dE = DEPLACEMENTS[mas]
            dy = (dF if nom == "F" else dE) * sens
            avant = avant_tout[mas][nom]
            _translater(font, nom, depart, mas, layer, dy)
            apres = centre(D.Source(font, mas), nom, depart)
            if abs(apres - (avant + dy)) > 0.26:
                raise ValueError(
                    f"barre_mediane : {nom} {mas} sort a {apres:.2f} pour "
                    f"{avant:.2f} + {dy:.2f}")
            journal.append((nom, mas, avant, apres, dy))
    if sens > 0:
        _verifier(font, avant_tout)
    if log is not None:
        bouges = sum(1 for j in journal if j[4])
        log.append(("barre mediane",
                    f"{len(journal)} glyphe-masters, {bouges} deplaces"))
    return journal


def _verifier(font, avant_tout):
    """Les deux faits que le geste doit produire, remesures apres lui.

    UN, le F et l'E coincident dans chaque master. DEUX, les ecarts a
    l'interieur de la famille de l'E sont INCHANGES : le geste descend la
    famille, il ne la redresse pas.
    """
    for mas in (m.name for m in font.masters):
        src = D.Source(font, mas)
        apres = {n: centre(src, n, d) for n, d in GLYPHES}
        if abs(apres["F"] - apres["E"]) > 0.26:
            raise ValueError(
                f"barre_mediane : {mas}, le F sort a {apres['F']:.2f} et l'E a "
                f"{apres['E']:.2f}")
        for n in SOLIDAIRES:
            ec_av = avant_tout[mas][n] - avant_tout[mas]["E"]
            ec_ap = apres[n] - apres["E"]
            if abs(ec_ap - ec_av) > 0.26:
                raise ValueError(
                    f"barre_mediane : {mas}, l'ecart {n} - E passe de "
                    f"{ec_av:.2f} a {ec_ap:.2f}")
