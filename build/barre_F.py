"""Point 94 : remonter la barre mediane du F au niveau de celle de l'E.

MODULE D'ESSAI, POUR LA PLANCHE SEULEMENT. Rien n'est ecrit dans les tables du
projet : la planche doit montrer ce que le geste ferait, pas le faire.

L'OPERATION EST UNE TRANSLATION DE BARRE, ET C'EST BIEN UNE OPERATION NEUVE.
`coupe.allonge` translate une TERMINAISON le long de sa normale sortante, et
`operateurs.py` translate un GLYPHE ENTIER. Ici, quatre noeuds d'un contour de
dix, choisis par leur ordonnee, se deplacent a l'interieur d'une lettre dont le
reste ne bouge pas.

LE GESTE EST MESURE, PAS SUPPOSE. Le F Bold est un contour unique de dix
noeuds, tout en lignes ; sa barre mediane est portee par (214, 244),
(379,7 , 244), (430,3 , 383), (214, 383) -- deux a la jonction du fut, deux au
bout deja coupe par le lot 2. L'E du meme master porte exactement les memes
formes 30 unites plus haut. Le bout oblique voyage avec la barre : la coupe du
lot 2 n'est pas retouchee, elle est deplacee.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphsLib.classes import GSPath
import dessin as D


def intervalles(contours, x, tol=1e-9):
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
        prev = w; w += d
        if prev == 0 and w != 0: deb = y
        elif prev != 0 and w == 0 and deb is not None:
            out.append((deb, y)); deb = None
    return out


def barre_mediane(src, nom, bande=(240, 460), ep_max=210):
    """(bas, haut, x_jonction) de la barre mediane, par balayage d'encre.

    PAS DE SONDE DU FUT A HAUTEUR FIXE : dans les gras la barre HAUTE descend
    jusqu'a 529, donc une sonde a 560 rend le bord droit du glyphe entier et la
    mesure tombe muette dans les quatre masters ou la question se pose.
    """
    cs = src.contours(nom)
    xs = [p[0] for c in cs for p in c]
    x0, x1 = min(xs), max(xs)
    trouve = []
    n = 400
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        cand = [s for s in intervalles(cs, x)
                if bande[0] <= (s[0] + s[1]) / 2 <= bande[1] and (s[1] - s[0]) <= ep_max]
        if len(cand) == 1:
            trouve.append((x, cand[0][0], cand[0][1]))
    if not trouve:
        raise ValueError(f"{nom} : aucune colonne isolee dans la bande {bande}")
    # La premiere colonne isolee est contre le fut : c'est la que la barre a
    # sa section pleine, avant que la coupe du bout ne la mange.
    x_j, bas, haut = trouve[0]
    return bas, haut, x_j


def dy_par_master(font, base="F", ref="E"):
    """Ce qu'il faut ajouter a la barre du F pour que son centre vaille celui de l'E."""
    out = {}
    for m in font.masters:
        src = D.Source(font, m.name)
        b1, h1, _ = barre_mediane(src, base)
        b2, h2, _ = barre_mediane(src, ref)
        out[m.name] = round(((b2 + h2) - (b1 + h1)) / 2.0, 2)
    return out


def remonter(font, dys, nom="F", journal=None):
    """Translate la barre mediane de `nom` de dys[master], master par master.

    LE FILTRE EST L'ORDONNEE SEULE, ET C'EST UNE CORRECTION MESUREE. Un
    premier jet exigeait en plus `x >= x_jonction`, ce qui marche au romain et
    LEVE dans les quatre masters italiques : le fut y penche, donc le noeud de
    jonction BAS de la barre est a gauche de la colonne ou la barre se separe
    du fut. Le fut du F ne porte aucun noeud entre la ligne de base et la barre
    haute -- ses quatre autres noeuds sont a y = -44, 0, 529 et 668 -- donc
    l'ordonnee seule designe exactement les quatre noeuds de la barre.

    LEVE plutot que de rendre une lettre a moitie deplacee. Quatre noeuds sont
    attendus ; un autre compte signale que le dessin n'est pas celui que la
    mesure a lu, et c'est exactement ce que le projet a paye au vingt-huitieme
    tour sur le U -- un compte qui ne tombe pas est un fait.
    """
    mid = {m.id: m.name for m in font.masters}
    g = font.glyphs[nom]
    for l in g.layers:
        mas = mid.get(l.layerId)
        if mas is None:
            continue
        dy = dys.get(mas, 0.0)
        src = D.Source(font, mas)
        bas, haut, x_j = barre_mediane(src, nom)
        w_avant, n_avant = l.width, sum(len(s.nodes) for s in l.shapes
                                        if isinstance(s, GSPath))
        bouges = 0
        for s in l.shapes:
            if not isinstance(s, GSPath):
                continue
            for nd in s.nodes:
                if bas - 1.0 <= nd.position.y <= haut + 1.0:
                    if dy:
                        nd.position = (nd.position.x, nd.position.y + dy)
                    bouges += 1
        if bouges != 4:
            raise ValueError(f"{nom} {mas} : {bouges} noeuds vises, 4 attendus")
        n_apres = sum(len(s.nodes) for s in l.shapes if isinstance(s, GSPath))
        if l.width != w_avant or n_apres != n_avant:
            raise ValueError(f"{nom} {mas} : chasse ou topologie touchee")
        if journal is not None:
            journal.append((nom, mas, dy, bas, haut, x_j))
    return font


# ---------------------------------------------------------------- tour 54 bis

def barre_dans(src, nom, depart=0.0, bande=(240, 460), ep_max=210):
    """La barre mediane cherchee a partir d'une FRACTION de la boite.

    Un balayage parti de la gauche rend la barre du A sur l'AE : 241,6 en
    ExtraLight et 343,5 au Bold, deux objets differents sous un seul nombre.
    Sur les glyphes qui portent une autre forme a gauche de leur E, le
    balayage part de `depart`.
    """
    cs = src.contours(nom)
    xs = [p[0] for c in cs for p in c]
    x0, x1 = min(xs), max(xs)
    deb = x0 + (x1 - x0) * depart
    n = 400
    for i in range(n + 1):
        x = deb + (x1 - deb) * i / n
        cand = [s for s in intervalles(cs, x)
                if bande[0] <= (s[0] + s[1]) / 2 <= bande[1]
                and (s[1] - s[0]) <= ep_max]
        if len(cand) == 1:
            return cand[0][0], cand[0][1], x
    raise ValueError(f"{nom} : aucune colonne isolee a partir de {depart:.2f}")


def translater_barre(font, nom, dys, depart=0.0, bande=(240, 460), ep_max=210,
                     attendus=4, marge_x=100.0, journal=None):
    """Translate la barre mediane de `nom` de dys[master], master par master.

    LE FILTRE EST L'ORDONNEE SEULE sur le F et sur l'E, dont le fut ne porte
    aucun noeud entre la ligne de base et la barre haute. Sur un glyphe qui
    dessine autre chose a gauche -- l'AE, l'OE -- il faut en plus une abscisse
    minimale, et le compte attendu la verifie.

    LEVE plutot que de rendre une lettre a moitie deplacee : un compte qui ne
    tombe pas est un fait.
    """
    mid = {m.id: m.name for m in font.masters}
    g = font.glyphs[nom]
    if g is None:
        raise ValueError(f"{nom} : absent de la source")
    for l in g.layers:
        mas = mid.get(l.layerId)
        if mas is None:
            continue
        dy = dys.get(mas, 0.0)
        src = D.Source(font, mas)
        bas, haut, x_col = barre_dans(src, nom, depart, bande, ep_max)
        # LE FILTRE EN X SE PREND SUR LA COLONNE TROUVEE, pas sur une fraction
        # de la boite. La fraction ecartait le noeud de jonction gauche de l'AE
        # en italique, ou le fut penche, et laissait passer les noeuds de l'O
        # dans l'OE : deux comptes instables pour un seul filtre mal choisi.
        x_min = x_col - marge_x
        w_avant = l.width
        n_avant = sum(len(s.nodes) for s in l.shapes if isinstance(s, GSPath))
        bouges = 0
        for s in l.shapes:
            if not isinstance(s, GSPath):
                continue
            for nd in s.nodes:
                # AUX BORDS, PAS DANS L'INTERVALLE. L'OE porte des noeuds de
                # son O a mi-hauteur -- (555, 336) en ExtraLight, (46, 273) en
                # Bold Italic a UNE unite du bord bas de la barre -- et un
                # filtre par intervalle les emportait. Les deux conditions sont
                # necessaires : l'ordonnee ecarte le premier, l'abscisse le
                # second.
                y = nd.position.y
                if min(abs(y - bas), abs(y - haut)) > 0.6:
                    continue
                if nd.position.x < x_min:
                    continue
                if dy:
                    nd.position = (nd.position.x, nd.position.y + dy)
                bouges += 1
        if bouges != attendus:
            raise ValueError(
                f"{nom} {mas} : {bouges} noeuds vises, {attendus} attendus")
        n_apres = sum(len(s.nodes) for s in l.shapes if isinstance(s, GSPath))
        if l.width != w_avant or n_apres != n_avant:
            raise ValueError(f"{nom} {mas} : chasse ou topologie touchee")
        if journal is not None:
            journal.append((nom, mas, dy, bas, haut))
    return font


def partage(font, t, base="F", ref="E"):
    """Les deux deplacements pour poser les deux barres a la meme hauteur.

    `t` est la part de l'ecart que l'E PARCOURT vers le bas : t=0 laisse l'E en
    place et monte le F de tout l'ecart, t=1 descend l'E jusqu'au F. Rend
    ({master: dy_F}, {master: dy_E}, {master: cible}), arrondis a la demi-unite
    pour que les deux tombent sur la meme valeur.
    """
    dF, dE, cible = {}, {}, {}
    for m in font.masters:
        src = D.Source(font, m.name)
        b1, h1, _ = barre_mediane(src, base)
        b2, h2, _ = barre_mediane(src, ref)
        cf, ce = (b1 + h1) / 2.0, (b2 + h2) / 2.0
        c = round((ce - (ce - cf) * t) * 2.0) / 2.0
        cible[m.name] = c
        dF[m.name] = round(c - cf, 2)
        dE[m.name] = round(c - ce, 2)
    return dF, dE, cible
