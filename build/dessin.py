#!/usr/bin/env python3
"""
Rendu direct des contours d'une source .glyphs, sans passer par une
compilation.

Sert a juger une modification de dessin en quelques secondes plutot qu'en
quelques minutes, et surtout a comparer plusieurs reglages cote a cote dans
la meme image. Pour le rendu d'un vrai texte shape, c'est render.py qui fait
foi : ici il n'y a ni crenage ni features.

ANTICRENELAGE, point ouvert 35, ferme au vingtieme tour. Le remplissage passait
par `ImageDraw.polygon`, qui ne connait pas l'anticrenelage : chaque bord de
lettre etait un escalier de pixels, et agrandir n'agrandissait que les marches.
Le defaut a coute trois passes au specimen du corpus, ou deux corrections
reelles — la taille d'affichage, puis la resolution du dessin — sont restees
inoperantes tant que la troisieme cause tenait. Le trace passe maintenant par un
masque a `SS` fois la resolution, reduit par LANCZOS, comme le fait tout moteur
de rendu de texte. Corrige ici plutot que planche par planche : toutes les
planches du projet qui appellent `dessiner` en heritent.

LE CLASSEMENT DES CONTOURS, point ouvert 85, QUARANTE-NEUVIEME TOUR. Les creux
sont peints apres les pleins, donc un contour positif pose dans une contreforme
est efface, alors qu'une police l'encre par remplissage non nul. C'est le piege
du peintre, tombe trois fois dans ce projet. `peindre` accepte pour cela une
troisieme famille, `ajouts`, peinte apres les creux, et `classer` decide
laquelle recoit quoi. `dessiner` passe par `classer` depuis ce tour : il
classait par le signe de l'aire, et TRENTE-SEPT scripts l'appellent.
"""

import math

from PIL import Image, ImageDraw, ImageFilter
from glyphsLib.classes import GSPath, GSComponent

import coupe as K

SS = 4          # facteur de surechantillonnage du masque


class Source:
    def __init__(self, font, master=None):
        self.font = font
        self.mid = {m.name: m.id for m in font.masters}
        self.master = master or font.masters[1].name
        self.upem = font.upm

    def layer(self, name):
        g = self.font.glyphs[name]
        if g is None:
            return None
        for l in g.layers:
            if l.layerId == self.mid[self.master]:
                return l
        return None

    def anchors(self, layer):
        return {a.name: (a.position.x, a.position.y) for a in layer.anchors}

    def contours(self, name, dx=0.0, dy=0.0, depth=0):
        """Liste de contours, chacun une liste de points (deja aplatis)."""
        layer = self.layer(name)
        if layer is None or depth > 4:
            return []
        out = []
        for s in layer.shapes:
            if isinstance(s, GSPath):
                out.append([(x + dx, y + dy) for x, y in flatten(s)])
            elif isinstance(s, GSComponent):
                t = list(s.transform)
                ox, oy = t[4], t[5]
                if ox == 0 and oy == 0:
                    ox, oy = self.attache(layer, s.componentName)
                out += self.contours(s.componentName, dx + ox, dy + oy, depth + 1)
        return out

    def attache(self, base_layer, mark_name):
        """Position d'une marque par ses ancres, quand le composant est a zero."""
        ml = self.layer(mark_name)
        if ml is None:
            return (0.0, 0.0)
        ma, ba = self.anchors(ml), self.anchors(base_layer)
        for cle in ("_top", "_bottom", "_topright", "_center"):
            if cle in ma and cle[1:] in ba:
                return (ba[cle[1:]][0] - ma[cle][0], ba[cle[1:]][1] - ma[cle][1])
        return (0.0, 0.0)

    def width(self, name):
        l = self.layer(name)
        return l.width if l else 0


def flatten(path, n=24):
    """Contour Glyphs -> polyligne."""
    pts = []
    for s in K.to_segs(path):
        if s["kind"] == "line":
            pts.append(s["p3"])
        else:
            for i in range(1, n + 1):
                p = K.bez(s, i / n)
                pts.append((float(p[0]), float(p[1])))
    return pts


def profondeurs(contours):
    """Pour chaque contour, dans combien d'autres il est IMBRIQUE.

    QUARANTE-HUITIEME TOUR, ET ELLE CORRIGE UN DEFAUT REEL. Tout peintre du
    projet classait ses contours par le SIGNE DE L'AIRE -- positifs en encre,
    negatifs en blanc -- ce qui est exact tant qu'un glyphe n'est qu'un plein
    troue. Le bras du O est un contour POSITIF pose DANS la contreforme :
    classe par son signe, il est peint avec les pleins, donc AVANT le creux
    qui l'efface. `mesure4.confusion` rendait alors exactement la meme
    distance avec et sans bras, sur les quatre masters -- une colonne
    uniforme, le mode de defaut que ce projet a rencontre huit fois.

    Le classement juste est celui du remplissage NON NUL, qui est la regle
    qu'applique un moteur de rendu : la profondeur d'imbrication, et l'encre
    aux profondeurs paires. Le signe de l'aire ne sert plus qu'a orienter.

    LE TEST EST UN POINT, ET PAS UNE BOITE. Un premier jet pre-filtrait par
    l'inclusion des boites, et il rendait le bras du O au groupe peint en
    BLANC : la racine du bras est ENFOUIE dans la paroi, donc sa boite deborde
    de celle de la contreforme alors que le contour y est, pour l'essentiel,
    a l'interieur. Le bras sortait tronque sur la planche, sans erreur.
    Une boite n'est pas une forme, et un contour greffe est precisement le cas
    ou les deux divergent.

    LE POINT SE CHERCHE, IL NE SE DEVINE PAS. Le milieu d'une corde entre deux
    sommets opposes tombe hors du contour des qu'il est courbe ou mince, ce
    qu'un bras en spirale est par construction : la fonction essaie les cordes
    l'une apres l'autre et garde la premiere dont le milieu est reellement
    dans le contour. Les contours d'une police ne se coupent pas, donc un
    point interieur decide pour tout le contour.
    """
    def dedans(pt, poly):
        x, y = pt
        n, ok = len(poly), False
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            if (y1 > y) != (y2 > y):
                xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                if x < xi:
                    ok = not ok
        return ok

    def point_interieur(c):
        """Un point DANS LE TRAIT du contour, contre son bord.

        Pas n'importe quel point interieur au sens du trace : le centre d'un
        anneau est "dans" son contour exterieur pour un lancer de rayon, et il
        est pourtant dans le trou pour l'encre. Un premier jet prenait le
        milieu d'une corde et rangeait donc l'exterieur du O a la profondeur
        1, c'est-a-dire parmi les creux, ce qui aurait peint la lettre en
        blanc. Le point juste est le milieu d'une arete pousse de quelques
        centiemes vers l'interieur : il appartient a la paroi, jamais au
        creux qu'elle entoure.
        """
        n = len(c)
        for i in range(n):
            p, q = c[i], c[(i + 1) % n]
            dx, dy = q[0] - p[0], q[1] - p[1]
            lg = math.hypot(dx, dy)
            if lg < 1e-9:
                continue
            mx, my = (p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0
            e = min(lg * 0.25, 0.75)
            for sx, sy in ((-dy / lg, dx / lg), (dy / lg, -dx / lg)):
                pt = (mx + sx * e, my + sy * e)
                if dedans(pt, c):
                    return pt
        return None

    out = []
    for i, c in enumerate(contours):
        pt = point_interieur(c) if len(c) >= 3 else None
        if pt is None:
            # Aucun point interieur trouve : la profondeur ne se decide pas,
            # et zero est la valeur qui peint le contour comme un plein. Un
            # contour degenere vaut mieux visible qu'efface.
            out.append(0)
            continue
        d = 0
        for j, c2 in enumerate(contours):
            if i == j or len(c2) < 3:
                continue
            if dedans(pt, c2):
                d += 1
        out.append(d)
    return out


def couches(contours):
    """[(contour, encre)] DANS L'ORDRE DE PEINTURE, par profondeur croissante.

    C'EST LA REGLE DU REMPLISSAGE NON NUL, ET ELLE N'A PAS DE PALIER. Un moteur
    de rendu ne connait ni "pleins", ni "creux", ni "greffes" : il encre un
    point selon le nombre d'enroulements des contours qui l'entourent. La seule
    chose qu'un peintre par polygones doit reproduire est l'ORDRE -- un contour
    plus profond se peint apres celui qui le contient -- et la COULEUR, que
    l'orientation donne.

    POURQUOI TROIS GROUPES NE SUFFISENT PAS, et c'est Nicolas qui l'a vu a
    l'oeil sur une planche, au quarante-neuvieme tour. Le `classer` de ce tour
    rendait (pleins, creux, greffes) et peignait dans cet ordre, ce qui est
    juste jusqu'a TROIS niveaux d'imbrication. Le ® en a QUATRE : l'anneau
    exterieur a la profondeur 0, le blanc du disque a 1, le R a 2, et LE TROU
    DU R a 3. Le trou tombait dans les creux, donc il etait peint avant le R
    qui le recouvrait, et le ® sortait avec un R plein. Le correctif du point
    85 avait rendu son R au ® et lui avait pris son blanc.

    UN PALIER EST TOUJOURS UN PARI SUR LA PROFONDEUR MAXIMALE DU DESSIN. Le
    projet en a pose trois -- deux familles, puis trois -- et les deux fois le
    repertoire est alle plus loin. La profondeur n'a pas de borne connue : un
    accent dans un cercle dans un cadre en aurait cinq.

    LE RACCOURCI EST EXACT, PAS UNE HEURISTIQUE, et il est necessaire.
    `profondeurs` teste un point contre chaque autre contour, donc son cout est
    quadratique ; `dessiner` l'appelle par glyphe et le specimen du corpus en
    compose des milliers, ce qui depasserait le plafond de trois minutes d'un
    appel. Un contour imbrique dans un autre CONTOUR POSITIF implique au moins
    deux contours positifs : un glyphe qui n'en a qu'un, ou aucun, se peint par
    le signe de l'aire, pleins puis creux, et c'est le cas de la quasi-totalite
    du repertoire.
    """
    pos = sum(1 for c in contours if aire(c) >= 0)
    if pos <= 1:
        return ([(c, True) for c in contours if aire(c) >= 0]
                + [(c, False) for c in contours if aire(c) < 0])
    niv = profondeurs(contours)
    return [(c, aire(c) >= 0)
            for _d, c in sorted(zip(niv, contours),
                                key=lambda x: (x[0], -abs(aire(x[1]))))]


def peindre_couches(img, couches_, encre=(26, 26, 26)):
    """Peint ce que `couches` rend, DANS SON ORDRE, avec anticrenelage.

    UN SEUL MASQUE POUR TOUTES LES COUCHES, et c'est la seule facon. Le premier
    jet appelait `peindre` une fois par contour, ce qui paraissait elegant :
    chaque couche peinte seule, l'ordre respecte sans nommer de famille. Il
    rendait des DISQUES PLEINS. `peindre` construit un masque neuf a chaque
    appel et le colle sur l'image ; un creux peint seul ne soustrait donc rien
    de ce qu'un appel precedent a depose, il pose un masque vide. C'est la
    forme exacte du piege du peintre, retombee dans le correctif du piege du
    peintre : ce qui compte n'est pas l'ordre des APPELS, c'est l'ordre des
    TRACES A L'INTERIEUR DU MASQUE. Trouve en regardant l'image, pas en
    relisant le code.
    """
    tous = [c for c, _e in couches_ if len(c) > 2]
    if not tous:
        return
    xs = [q[0] for p in tous for q in p]
    ys = [q[1] for p in tous for q in p]
    x0, y0 = int(math.floor(min(xs))) - 1, int(math.floor(min(ys))) - 1
    x1, y1 = int(math.ceil(max(xs))) + 1, int(math.ceil(max(ys))) + 1
    larg, haut = x1 - x0, y1 - y0
    if larg <= 0 or haut <= 0 or larg * haut > 80_000_000:
        return
    masque = Image.new("L", (larg * SS, haut * SS), 0)
    dm = ImageDraw.Draw(masque)
    for c, e in couches_:
        if len(c) > 2:
            dm.polygon([((qx - x0) * SS, (qy - y0) * SS) for qx, qy in c],
                       fill=255 if e else 0)
    masque = masque.resize((larg, haut), Image.LANCZOS)
    if img.mode == "RGB":
        teinte = encre if isinstance(encre, tuple) else (encre,) * 3
    else:
        teinte = encre if isinstance(encre, int) else int(sum(encre) / 3)
    couleur = Image.new(img.mode, masque.size, teinte)
    img.paste(couleur, (x0, y0), masque)


def couches_ecran(contours, tr):
    """`couches`, chaque point passe par `tr(x, y)`.

    Quarante-neuvieme tour. Le motif que les peintres du projet ecrivaient tous
    a la main melait le classement et le cadrage en trois lignes, et c'est cet
    emmelement qui a fait recopier le classement faux dans vingt-neuf fichiers.
    Une seule ligne les remplace, et le classement ne peut plus diverger d'un
    peintre a l'autre.
    """
    return [([tr(x, y) for x, y in c], e) for c, e in couches(contours)]


def classer(contours):
    """(pleins, creux, greffes) : l'ORIENTATION dit l'encre, la profondeur dit
    l'ORDRE.

    OBSOLETE AU QUARANTE-NEUVIEME TOUR, GARDEE POUR MEMOIRE ET POUR LEVER.
    Elle est JUSTE jusqu'a trois niveaux d'imbrication et FAUSSE au-dela : le
    trou du R du ®, qui est au quatrieme, tombait dans les creux et se faisait
    recouvrir. `couches` la remplace et n'a pas de palier. La fonction leve
    plutot que de rendre un resultat faux sur les glyphes ou elle ne vaut plus,
    parce que ce projet a deja paye qu'un code faux laisse en place finit par
    etre rappele.

    Rend les trois groupes que `peindre` attend, et un appelant qui classait
    par `aire(c) > 0` peut la substituer telle quelle.

    POURQUOI PAS LA PROFONDEUR SEULE. Le bras du O chevauche la paroi et la
    contreforme : sa racine est enfouie dans le trait, sa pointe est dans le
    blanc. Sa profondeur n'est donc pas constante le long du contour, et un
    classement qui la lirait rangerait le bras tantot en greffe, tantot en
    creux, selon le point ou la mesure tombe -- ce qui l'aurait peint en
    BLANC. Le remplissage non nul, lui, encre le bras des deux cotes, parce
    que son orientation est celle de l'exterieur : dans la paroi le nombre
    d'enroulement vaut 2, dans la contreforme il vaut 1, et les deux encrent.

    Le critere est donc : orientation positive et profondeur 0, c'est un
    plein ; orientation negative, c'est un creux ; orientation positive et
    profondeur au moins 1, c'est un contour GREFFE, qui se peint apres les
    creux pour ne pas etre efface par eux.

    ELLE LEVE AU-DELA DE TROIS NIVEAUX plutot que de rendre un dessin faux.
    """
    niv = profondeurs(contours)
    if any(d >= 3 for d in niv):
        raise ValueError(
            "classer() est fausse au-dela de trois niveaux d'imbrication : "
            f"le contour le plus profond de ce glyphe est au niveau "
            f"{max(niv)}, et il serait recouvert. Employer dessin.couches(), "
            "qui n'a pas de palier.")
    pleins, creux, greffes = [], [], []
    for c, d in zip(contours, niv):
        if aire(c) < 0:
            creux.append(c)
        elif d == 0:
            pleins.append(c)
        else:
            greffes.append(c)
    return pleins, creux, greffes


def classer_ecran(contours, tr):
    """OBSOLETE : `couches_ecran` la remplace. Voir `classer`."""
    return tuple([[tr(x, y) for x, y in c] for c in grp]
                 for grp in classer(contours))


#: Les glyphes qui portent un contour GREFFE, mesures au quarante-neuvieme
#: tour sur les huit masters des deux sources par `check_O` section 6, qui
#: remesure cette table et signale tout ecart.
#:
#: ELLE EXISTE PARCE QUE LE POINT 85 SE TROMPAIT SUR SON ETENDUE. Il annonce
#: que le defaut du peintre "ne mord que sur le O seul aujourd'hui" et qu'il
#: "attend le prochain contour greffe". Mesure : il mord depuis le premier tour
#: sur DEUX AUTRES GLYPHES, qui viennent d'Atkinson et que le projet n'a jamais
#: touches, dans les deux sources et les huit masters. Le compte est de douze
#: glyphe-calques au romain et huit en italique.
#:
#: CE QUE CELA NE REMET PAS EN CAUSE, et il faut que cela reste lisible : le
#: BINAIRE rend juste, c'est le moteur de rendu qui peint et il applique le
#: remplissage non nul. Le defaut vit dans les outils du projet, pas dans la
#: police livree. Et aucun arbitrage passe n'a pu etre pris sur un © ou un ®
#: faux : ni les cinq gabarits ni `textes.py` n'en contiennent un seul, ce qui
#: est verifie et non suppose.
#:
#: LE © ET LE ® NE RECOIVENT AUCUN GESTE, decision de Nicolas au quarante-
#: neuvieme tour. Ils sont ici parce qu'ils sont des PORTEURS, ce qui est un
#: fait de geometrie qui decide du classement d'un peintre, et non parce qu'ils
#: seraient un chantier de dessin. Un glyphe decide et un glyphe jamais regarde
#: sont identiques dans une table, tous deux absents.
PORTEURS_GREFFE = {
    "O": dict(source="projet", masters="romains", greffes=1,
              raison="le bras du O, greffe au quarante-huitieme tour"),
    "copyright": dict(source="amont", masters="tous", greffes=1,
                      raison="le C pose dans l'anneau, dessin d'Atkinson"),
    "registered": dict(source="amont", masters="tous", greffes=1,
                       raison="le R pose dans l'anneau, dessin d'Atkinson"),
}

#: Les peintres qui classent ENCORE par le signe de l'aire, et pourquoi ils
#: n'en ont pas besoin. Decision de Nicolas au quarante-neuvieme tour, prise
#: apres l'inventaire : les corriger ne changerait aucune image.
#:
#: Ce sont onze planches d'INSTRUCTION dont l'arbitrage est rendu, et trois
#: faits mesures les couvrent toutes les onze :
#:   - les onze lisent `AtkinsonHyperlegibleNext.glyphs`, l'amont BRUT, ou le
#:     O n'a pas de bras. C'est verifie fichier par fichier, pas suppose.
#:   - celles qui montrent un bras le CONSTRUISENT et le passent par un groupe
#:     `sus`, peint en dernier : l'ordre y est deja juste, et leur classement
#:     par le signe ne porte que sur une base sans greffe.
#:   - aucune ne compose ni © ni ®, les deux seuls porteurs de l'amont.
#:
#: A NE PAS LIRE COMME "ces planches sont justes". Elles sont justes sur ce
#: qu'elles montraient ; toute planche neuve passe par `classer`.
PEINTRES_LAISSES = (
    "planche_lot3", "planche_lot4", "planche_lot4b", "planche_lot4c",
    "planche_lot4d", "planche_lot4e", "planche_lot4m_O", "planche_lot4n_O",
    "planche_lot4o_O", "planche_lot4p_retenu", "planche_lot4q_o",
)


def peindre(img, pleins, creux=(), ajouts=(), encre=(26, 26, 26)):
    """Peint des contours donnes en pixels image, avec anticrenelage.

    `pleins`, `creux` et `ajouts` sont des listes de polylignes en coordonnees
    d'image. L'ordre de peinture est impose et il compte : la base, puis les
    creux, puis les ajouts. Peindre un contour greffe avant les creux l'efface,
    et le premier essai du bras du O paraissait vide pour cette raison.

    Le masque est trace a SS fois la resolution puis reduit par LANCZOS. Il sert
    d'alpha : ce qui est deja dans l'image sous les blancs du glyphe n'est pas
    repeint, ce que l'ancien remplissage en couleur de fond faisait a tort.
    """
    tous = [p for grp in (pleins, creux, ajouts) for p in grp if len(p) > 2]
    if not tous:
        return
    xs = [q[0] for p in tous for q in p]
    ys = [q[1] for p in tous for q in p]
    x0, y0 = int(math.floor(min(xs))) - 1, int(math.floor(min(ys))) - 1
    x1, y1 = int(math.ceil(max(xs))) + 1, int(math.ceil(max(ys))) + 1
    larg, haut = x1 - x0, y1 - y0
    if larg <= 0 or haut <= 0 or larg * haut > 80_000_000:
        return
    masque = Image.new("L", (larg * SS, haut * SS), 0)
    dm = ImageDraw.Draw(masque)

    def poser(groupe, valeur):
        for p in groupe:
            if len(p) > 2:
                dm.polygon([((qx - x0) * SS, (qy - y0) * SS) for qx, qy in p],
                           fill=valeur)

    poser(pleins, 255)
    poser(creux, 0)
    poser(ajouts, 255)
    masque = masque.resize((larg, haut), Image.LANCZOS)
    # Le mode suit celui de l'image cible : les controles de contact rasterisent
    # en niveaux de gris, et coller du RGB dans une image "L" leve.
    if img.mode == "RGB":
        teinte = encre if isinstance(encre, tuple) else (encre,) * 3
    else:
        teinte = encre if isinstance(encre, int) else int(sum(encre) / 3)
    couleur = Image.new(img.mode, masque.size, teinte)
    img.paste(couleur, (x0, y0), masque)


def dessiner(img, src, texte, x, y, taille, encre=(26, 26, 26), fond=(255, 255, 255),
             suivi=0.0):
    """Ecrit `texte` en (x, y) = origine de la ligne de base, en pixels.

    Retourne la largeur avancee. `fond` n'est plus employe — le trace passe par
    un masque, donc les creux laissent voir l'image au lieu d'etre repeints — et
    l'argument reste pour les planches qui le passent encore.

    LE CLASSEMENT SE FAIT PAR GLYPHE, jamais sur la ligne entiere. Point ouvert
    85, quarante-neuvieme tour. Cette fonction classait par le signe de l'aire,
    donc elle effacait tout contour greffe : le © sortait sans son C, le ® sans
    son R, le O sans son bras. Elle est le peintre commun du projet, appele par
    trente-sept scripts, et c'est ce qui rendait le defaut contagieux. Le
    classement passe par `classer`, et il se prend contour par contour DU MEME
    GLYPHE : sur la ligne entiere, le test d'imbrication croiserait les
    contours de deux lettres voisines, qui ne s'imbriquent jamais mais dont les
    boites se chevauchent des que le crenage est serre.
    """
    k = taille / src.upem
    pen = float(x)
    couches_ = []
    for ch in texte:
        name = nom_glyphe(src.font, ch)
        if name is None:
            pen += taille * 0.3
            continue
        couches_ += couches_ecran(
            src.contours(name),
            lambda px, py, p=pen: (p + px * k, y - py * k))
        pen += src.width(name) * k + suivi
    peindre_couches(img, couches_, encre=encre)
    return pen - x


def largeur(src, texte, taille, suivi=0.0):
    k = taille / src.upem
    return sum(src.width(nom_glyphe(src.font, ch) or "space") * k + suivi
               for ch in texte)


def aire(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return a / 2.0


_CACHE = {}


def nom_glyphe(font, ch):
    cle = id(font)
    if cle not in _CACHE:
        t = {}
        for g in font.glyphs:
            for u in (g.unicodes or []):
                try:
                    t[chr(int(u, 16))] = g.name
                except ValueError:
                    pass
        _CACHE[cle] = t
    return _CACHE[cle].get(ch)


def flou(img, box, rayon):
    zone = img.crop(box).filter(ImageFilter.GaussianBlur(rayon))
    img.paste(zone, box[:2])
