#!/usr/bin/env python3
"""
Temoin, etape 2, lot 4 : la coupe de titrage.

Deux gestes, et ils repondent a deux constats mesures.

1. L'extension du perimetre. Le lot 2 s'interdisait toute coupe portant un
   alignement, ce qui a exclu par construction quatorze lettres : X V W Y M N U,
   n m r u v w x. Leurs terminaisons sont toutes posees sur la ligne de base ou
   sur la capitale. Le A n'a que trois terminaisons, ses deux pieds et son
   sommet, toutes porteuses. Ce sont exactement les lettres de signature et les
   minuscules jugees fades. Le titrage leve la regle.

   K.coupe choisit deja le pivot qui fait rentrer l'autre coin : la lettre garde
   un point de contact sur sa ligne et ne peut que maigrir. Ce qui change, c'est
   qu'un plat de 113 unites devient un point.

2. L'ouverture de l'anneau. Le O n'a aucun segment droit : deux contours de
   douze noeuds, quatre courbes chacun. La loi du lot 2 n'a aucune prise sur
   lui. Le logo de l'OXA donne la sortie : un ecureuil enroule sur lui-meme,
   dont la queue se defait en meches effilees. L'anneau du O s'ouvre, et ses
   deux bouts s'effilent en pointe. C'est le geste que la virgule et la cedille
   ont deja recu au lot 2.

Ce module fait la geometrie et le choix des terminaisons. Il s'appuie sur
coupe.py pour les primitives et sur lot2.py pour les contours.
"""

import math

import numpy as np
from glyphsLib.classes import GSPath

import coupe as K
import lot2 as L


# ------------------------------------------------------- reperage angulaire

def boite(segs_par_contour):
    xs, ys = [], []
    for segs in segs_par_contour:
        for s in segs:
            for t in (0.0, 0.25, 0.5, 0.75, 1.0):
                p = K.bez(s, t)
                xs.append(float(p[0]))
                ys.append(float(p[1]))
    return min(xs), min(ys), max(xs), max(ys)


def direction(ang_deg):
    a = math.radians(ang_deg)
    return np.array([math.cos(a), math.sin(a)])


def croisement(segs, C, ang_deg):
    """(indice, parametre, point) ou le contour coupe le rayon d'angle `ang`.

    Le rayon, pas la droite : on ne retient que les intersections situees du
    bon cote du centre. Sans ce filtre, un ovale donne toujours deux solutions
    et le choix bascule d'un master a l'autre.
    """
    u = direction(ang_deg)
    C = K.V(C)
    trouve = []
    for i, s in enumerate(segs):
        for near in (0.0, 0.25, 0.5, 0.75, 1.0):
            t = K.hit_line(s, C, u, near)
            if t is None or not (-1e-9 <= t <= 1.0 + 1e-9):
                continue
            t = min(max(t, 0.0), 1.0)
            P = K.bez(s, t)
            if float(np.dot(P - C, u)) <= 0:
                continue
            if not any(j == i and abs(tt - t) < 1e-6 for j, tt, _ in trouve):
                trouve.append((i, t, P))
    if not trouve:
        raise ValueError(f"aucun croisement a {ang_deg:.1f} degres")
    # le plus loin du centre : sur un ovale il n'y en a qu'un, mais un contour
    # legerement concave peut en donner deux et on veut le bord.
    return max(trouve, key=lambda x: float(np.dot(x[2] - C, u)))


def sous_contour(segs, i0, t0, i1, t1):
    """Les segments parcourus de (i0, t0) a (i1, t1), dans le sens du contour."""
    n = len(segs)
    if i0 == i1 and t1 > t0:
        s = K.split_right(segs[i0], t0)
        u = (t1 - t0) / (1.0 - t0) if t0 < 1.0 else 1.0
        return [K.split_left(s, u)]
    out = [K.split_right(segs[i0], t0)]
    i = (i0 + 1) % n
    while i != i1:
        out.append(dict(segs[i], c=list(segs[i]["c"])))
        i = (i + 1) % n
    out.append(K.split_left(segs[i1], t1))
    return out


# ------------------------------------------------------ ouverture d'anneau

def _courbe(P, tP, T, uT, tirage=0.50, retenue=0.32):
    """Courbe de P vers T.

    `tP` est la direction de sortie en P, `uT` la direction d'arrivee en T.
    Les deux poignees pointent donc vers l'interieur du segment, ce qui est la
    seule convention qui ne boursoufle pas : une poignee posee dans le mauvais
    sens fait sortir la courbe de la lettre, et sur une contreforme ca se lit
    comme un defaut de dessin.
    """
    d = float(np.hypot(*(K.V(T) - K.V(P))))
    return {"kind": "curve", "p0": tuple(K.V(P)),
            "c": [tuple(K.V(P) + tirage * d * K.V(tP)),
                  tuple(K.V(T) - retenue * d * K.V(uT))],
            "p3": tuple(K.V(T)), "smooth": False}


def _chaine(pts, t_debut=None, t_fin=None, ferme=False):
    """Segments de Bezier passant par `pts`, tangentes de Catmull-Rom.

    `t_debut` et `t_fin` imposent la tangente aux extremites, ce qui sert a
    raccorder proprement sur un contour existant. A None, la tangente est
    deduite du voisin.
    """
    n = len(pts)
    tg = []
    for k in range(n):
        if k == 0:
            v = (K.V(pts[1]) - K.V(pts[0])) if t_debut is None else \
                K.V(t_debut) * float(np.hypot(*(K.V(pts[1]) - K.V(pts[0]))))
        elif k == n - 1:
            v = (K.V(pts[-1]) - K.V(pts[-2])) if t_fin is None else \
                K.V(t_fin) * float(np.hypot(*(K.V(pts[-1]) - K.V(pts[-2]))))
        else:
            v = (K.V(pts[k + 1]) - K.V(pts[k - 1])) / 2.0
        tg.append(v)
    out = []
    for k in range(n - 1):
        P, Q = K.V(pts[k]), K.V(pts[k + 1])
        out.append({"kind": "curve", "p0": tuple(P),
                    "c": [tuple(P + tg[k] / 3.0), tuple(Q - tg[k + 1] / 3.0)],
                    "p3": tuple(Q), "smooth": True})
    return out


# ------------------------------------------------------------------- la plume
#
# L'anneau reste ferme. La queue est un surplus : le trait depasse son propre
# point de fermeture et se defait en meches effilees. C'est ce que montre le
# logo, et ca vaut mieux qu'un anneau ouvert pour une raison mesurable : la
# contreforme du O reste fermee, donc le groupe O/0/Q/C/G n'est pas attaque
# dans sa topologie. L'anneau ouvert, lui, passait de 1 contreforme a 0.
#
# Chaque meche est un contour distinct, dont la base est enfouie dans la paroi
# de l'anneau. Le remplissage non nul en fait l'union sans operation booleenne.

def meche(paths, phi, longueur, ecart, epaisseur, sens=+1, n=10,
          montee=1.3, effile=0.75):
    """Une meche effilee greffee sur le bord exterieur de l'anneau.

    phi        angle de depart, en degres depuis le centre de la boite
    longueur   arc parcouru, en degres
    ecart      de combien la meche s'ecarte du bord exterieur au bout, en unites
    epaisseur  epaisseur a la base, en unites
    sens       +1 anti-horaire, -1 horaire
    montee     exposant de l'ecartement : au-dela de 1 la meche colle l'anneau
               au depart puis decolle, ce qui est le geste du logo
    effile     exposant de l'amincissement
    """
    aires = [(abs(K.area(K.to_segs(p))), p) for p in paths]
    aires.sort(key=lambda x: -x[0])
    ext = K.to_segs(aires[0][1])
    itr = K.to_segs(aires[1][1]) if len(aires) > 1 else None
    x0, y0, x1, y1 = boite([s for s in (ext, itr) if s])
    C = np.array([(x0 + x1) / 2.0, (y0 + y1) / 2.0])

    axe, demi = [], []
    for k in range(n + 1):
        s = k / n
        ang = phi + sens * longueur * s
        _, _, P = croisement(ext, C, ang)
        u = direction(ang)
        R = float(np.dot(K.V(P) - C, u))
        # la base est enfouie dans la paroi : elle demarre a l'interieur du
        # bord exterieur, sans quoi la greffe se voit comme une soudure.
        rc = R - (1.0 - s) * epaisseur * 0.5 + (s ** montee) * ecart
        axe.append(C + rc * u)
        demi.append(0.5 * epaisseur * max(0.0, (1.0 - s)) ** effile)

    bords = ([], [])
    for k in range(n + 1):
        if k == 0:
            t = K.unit(axe[1] - axe[0])
        elif k == n:
            t = K.unit(axe[-1] - axe[-2])
        else:
            t = K.unit(axe[k + 1] - axe[k - 1])
        nn = K.perp(t)
        bords[0].append(axe[k] + demi[k] * nn)
        bords[1].append(axe[k] - demi[k] * nn)

    # le bout est un point unique : les deux bords s'y rejoignent
    pts = bords[0][:-1] + [axe[-1]] + list(reversed(bords[1][:-1]))
    segs = _chaine(pts + [pts[0]])
    segs[-1] = dict(segs[-1], smooth=False)
    if K.area(segs) < 0:
        pts = list(reversed(pts))
        segs = _chaine(pts + [pts[0]])
        segs[-1] = dict(segs[-1], smooth=False)
    return K.from_segs(segs)


def _retourner(segs):
    """Inverse le sens de parcours d'une chaine de segments.

    Le signe de l'aire decide si un contour est encre ou creux. Retourner une
    liste de segments demande d'inverser chaque segment, poignees comprises :
    inverser la liste seule laisse les Bezier a l'endroit et casse la chaine.
    """
    out = []
    for s in reversed(segs):
        if s["kind"] == "line":
            out.append({"kind": "line", "p0": s["p3"], "c": [], "p3": s["p0"],
                        "smooth": s["smooth"]})
        else:
            out.append({"kind": "curve", "p0": s["p3"],
                        "c": [s["c"][1], s["c"][0]], "p3": s["p0"],
                        "smooth": s["smooth"]})
    return out


def rayons(paths):
    """Centre de la boite, et les deux bords de la paroi a un angle donne.

    Sert aux constructions qui font varier l'epaisseur de l'anneau sans
    toucher a son trace : on lit la paroi d'Atkinson au lieu de la redessiner,
    donc la lettre garde sa modulation, epaisse aux flancs et mince en haut.
    """
    aires = [(abs(K.area(K.to_segs(p))), p) for p in paths]
    aires.sort(key=lambda x: -x[0])
    ext = K.to_segs(aires[0][1])
    itr = K.to_segs(aires[1][1])
    x0, y0, x1, y1 = boite([ext, itr])
    C = np.array([(x0 + x1) / 2.0, (y0 + y1) / 2.0])

    def bords(ang):
        _, _, PE = croisement(ext, C, ang)
        _, _, PI = croisement(itr, C, ang)
        return K.V(PE), K.V(PI)

    return C, bords, (x0, y0, x1, y1)


def contre_spirale(paths, phi=145.0, mince=0.55, epais=1.45, n=72, expo=1.0,
                   sens=-1):
    """La paroi s'epaissit sur un tour. Seul le contour interieur bouge.

    Famille A. Le contour exterieur reste celui d'Atkinson au bit pres, donc
    la silhouette du glyphe est exactement celle du O et le groupe O/0/Q/C/G
    n'est pas attaque de l'exterieur. La spirale se lit dans la contreforme,
    ou elle s'ouvre puis se referme sur un tour, avec un ressaut radial au
    joint. A acuite reduite le detail interne se comble en premier et la
    lettre redevient un O sobre : la degradation joue dans le bon sens.

    mince, epais  epaisseur de la paroi au depart et a l'arrivee, en fraction
                  de son epaisseur naturelle a cet angle. Leur moyenne doit
                  valoir 1 : sinon la lettre change de couleur et fait un trou
                  ou une tache dans la ligne. Mesure : partir de 0,34 pour
                  arriver a 1 coutait 28 % d'encre.
    """
    C, bords, _ = rayons(paths)
    pts = []
    for k in range(n + 1):
        s = k / n
        PE, PI = bords(phi + sens * 360.0 * s)
        w = mince + (epais - mince) * (s ** expo)
        pts.append(PE - w * (PE - PI))
    segs = _chaine(pts)
    segs[-1] = dict(segs[-1], smooth=False)
    segs.append({"kind": "line", "p0": tuple(pts[-1]), "c": [],
                 "p3": tuple(pts[0]), "smooth": False})
    if K.area(segs) > 0:                     # une contreforme est negative
        segs = _retourner(segs)
    return K.from_segs(segs)


def anneau_joint(paths, phi=145.0, mince=0.62, epais=1.38, n=72, expo=1.0,
                 sens=-1, cote="deux"):
    """L'anneau devient un tour de spirale, mince au depart, plein a l'arrivee.

    Famille B. Aucun contour ajoute, aucune contreforme perdue : le trait garde
    l'axe de l'anneau d'Atkinson et ne fait varier que sa demi-epaisseur, de
    part et d'autre. Les deux bouts se rejoignent en un joint franc, coupe net,
    qui est le seul endroit ou la lettre se signale.

    Ici la paroi grossit des deux cotes, donc `epais` au-dela de 1 fait sortir
    le trait de la silhouette du O. Le debord vaut (epais - 1) fois la
    demi-epaisseur, soit 14 unites au Bold pour 1,38 : l'ordre du debord
    optique des rondes d'Atkinson, qui est de 12.

    `cote` decide de quel cote la paroi grossit, et ce n'est pas un detail de
    reglage : c'est ce qui decide de la taille du decrochement au joint. Avec
    "deux", les deux bords bougent, le ressaut vaut (epais - mince) fois
    l'epaisseur entiere, soit 128 unites au Bold, et l'image le lit comme une
    entaille plutot que comme un depart de trait. Avec "dehors", le bord
    interieur est celui d'Atkinson : la contreforme est intacte au bit pres,
    le ressaut est deux fois plus petit, et il ne se voit que sur la
    silhouette. Avec "dedans", c'est la silhouette qui est intacte, ce qui
    ramene a la famille du contre-poincon.

    La position du joint decide autre chose, que la mesure seule montre : elle
    decide ou la lettre perd sa hauteur. A 145 degres et en tournant dans le
    sens horaire, le sommet du O est atteint quand la paroi ne vaut encore que
    0,74 de sa valeur, et il tombe de 17 unites au Bold, sous la ligne de
    capitale. La lettre cesse alors de deborder en haut, c'est-a-dire l'inverse
    de la correction optique que la police pratique.
    """
    C, bords, _ = rayons(paths)
    dehors, dedans = [], []
    for k in range(n + 1):
        s = k / n
        PE, PI = bords(phi + sens * 360.0 * s)
        mil, u = (PE + PI) / 2.0, (PE - PI) / 2.0
        w = mince + (epais - mince) * (s ** expo)
        if cote == "dehors":
            dehors.append(mil + (2.0 * w - 1.0) * u)
            dedans.append(PI)
        elif cote == "dedans":
            dehors.append(PE)
            dedans.append(mil - (2.0 * w - 1.0) * u)
        else:
            dehors.append(mil + w * u)
            dedans.append(mil - w * u)
    pts = dehors + list(reversed(dedans))
    segs = _chaine(pts + [pts[0]])
    segs[n - 1] = dict(segs[n - 1], p3=tuple(dehors[-1]), smooth=False)
    segs[n] = {"kind": "line", "p0": tuple(dehors[-1]), "c": [],
               "p3": tuple(dedans[-1]), "smooth": False}
    segs[-2] = dict(segs[-2], p3=tuple(dedans[0]), smooth=False)
    segs[-1] = {"kind": "line", "p0": tuple(dedans[0]), "c": [],
                "p3": tuple(dehors[0]), "smooth": False}
    if K.area(segs) < 0:
        segs = _retourner(segs)
    return K.from_segs(segs)


def bras_spirale(paths, phi, longueur, epaisseur, r_debut=0.18, r_fin=1.16,
                 sens=-1, n=16, courbe=1.25, pointe_base=0.10, bouts="deux"):
    """Un bras de spirale qui part du centre de la contreforme et sort de l'anneau.

    Synthese des deux essais precedents. La volute ionique donne l'ecart entre
    les spires, mais elle ouvre la contreforme et la lettre se lit comme un 6.
    L'anneau ferme garde la lettre lisible, mais le bout de la grande spire
    ecrase la petite. Ici l'anneau reste entier et la spirale est un trait a
    part : elle demarre en pointe au centre a gauche, monte vers la droite, et
    ressort en passant par-dessus l'anneau. La contreforme reste fermee, et
    l'ecart est libre puisque le bras ne fait plus partie de l'anneau.

    r_debut, r_fin  rayons de depart et d'arrivee, en fraction du rayon exterieur
    pointe_base     epaisseur au depart, en fraction de l'epaisseur
    bouts           "deux" : pointe aux deux extremites, plein au milieu.
                    "rentrant" : plein au depart, pointe a l'arrivee. C'est ce
                    qu'il faut quand le bras demarre soude a la paroi et
                    s'enroule vers le centre sans jamais la traverser. La
                    traversee est le seul vrai defaut mesure de la famille du
                    bras : elle produit un ergot qui depasse de la silhouette.
    """
    aires = [(abs(K.area(K.to_segs(p))), p) for p in paths]
    aires.sort(key=lambda x: -x[0])
    ext = K.to_segs(aires[0][1])
    x0, y0, x1, y1 = boite([ext])
    C = np.array([(x0 + x1) / 2.0, (y0 + y1) / 2.0])
    rx, ry = (x1 - x0) / 2.0, (y1 - y0) / 2.0

    axe, demi = [], []
    for k in range(n + 1):
        s = k / n
        ang = math.radians(phi + sens * longueur * s)
        r = r_debut + (r_fin - r_debut) * (s ** courbe)
        axe.append(np.array([C[0] + rx * r * math.cos(ang),
                             C[1] + ry * r * math.sin(ang)]))
        if bouts == "rentrant":
            f = max(0.0, 1.0 - s) ** 0.55
        else:
            # pointe aux deux bouts, plein au milieu : un trait de pinceau
            f = math.sin(math.pi * min(1.0, max(0.0, s))) ** 0.6
        demi.append(0.5 * epaisseur * (pointe_base + (1.0 - pointe_base) * f))

    bg, bd = [], []
    for k in range(n + 1):
        if k == 0:
            t = K.unit(axe[1] - axe[0])
        elif k == n:
            t = K.unit(axe[-1] - axe[-2])
        else:
            t = K.unit(axe[k + 1] - axe[k - 1])
        nn = K.perp(t)
        bg.append(axe[k] + demi[k] * nn)
        bd.append(axe[k] - demi[k] * nn)

    def tracer(a, b):
        """a et b sont les deux bords. Le depart est un point ou une base."""
        if bouts == "rentrant":
            return [a[0]] + a[1:-1] + [axe[-1]] + list(reversed(b[1:-1])) + [b[0]]
        return [axe[0]] + a[1:-1] + [axe[-1]] + list(reversed(b[1:-1]))

    pts = tracer(bg, bd)
    segs = _chaine(pts + [pts[0]])
    segs[-1] = dict(segs[-1], smooth=False)
    if K.area(segs) < 0:
        pts = tracer(bd, bg)
        segs = _chaine(pts + [pts[0]])
        segs[-1] = dict(segs[-1], smooth=False)
    return K.from_segs(segs)


def _flancs_bras(paths, phi, longueur, epaisseur, enfoui, r_fin, sens, n,
                 courbe, pointe, effile):
    """(axe, flanc gauche, flanc droit) du bras, avant traitement du bout.

    Sorti de `bras_ancre` pour que la verification du bout mesure la meme
    geometrie que celle qui dessine, et non une reconstruction. Le premier
    controle de la coupe oblique retrouvait les coins du bout par une
    heuristique sur le contour aplati : il tombait sur deux points distants de
    2 unites la ou la coupe en fait 20, et rendait un angle de 1,5 degre pour
    une rotation de 20. Un controle qui redecouvre son objet mesure autre
    chose que ce qu'il croit.
    """
    C, bords, _ = rayons(paths)

    def polaire(ang):
        PE, PI = bords(ang)
        ri = float(np.hypot(*(PI - C)))
        return ri, float(np.hypot(*(PE - C))) - ri

    r0, ep0 = polaire(phi)
    axe, demi = [], []
    for k in range(n + 1):
        s = k / n
        ang = phi + sens * longueur * s
        ri, _ = polaire(ang)
        depart = r0 + enfoui * ep0
        r = depart + (r_fin * ri - depart) * (s ** courbe)
        axe.append(C + r * direction(ang))
        f = max(0.0, 1.0 - s) ** effile
        demi.append(0.5 * epaisseur * (pointe + (1.0 - pointe) * f))

    bg, bd = [], []
    for k in range(n + 1):
        if k == 0:
            t = K.unit(axe[1] - axe[0])
        elif k == n:
            t = K.unit(axe[-1] - axe[-2])
        else:
            t = K.unit(axe[k + 1] - axe[k - 1])
        nn = K.perp(t)
        bg.append(axe[k] + demi[k] * nn)
        bd.append(axe[k] - demi[k] * nn)
    return axe, bg, bd


def bout_bras(paths, phi, longueur, epaisseur, enfoui=0.45, r_fin=0.20,
              sens=-1, n=20, courbe=1.0, pointe=0.05, effile=0.55,
              bout="pointe", obl_angle=20.0, obl_cote="gauche"):
    """(pivot, autre coin, direction de la coupe droite) au bout du bras.

    Meme code que `bras_ancre`, memes arguments : c'est le contrat de la
    verification. Rend le couple de coins effectivement dessine, donc l'angle
    et le recul se lisent dessus sans heuristique.
    """
    _, bg, bd = _flancs_bras(paths, phi, longueur, epaisseur, enfoui, r_fin,
                             sens, n, courbe, pointe, effile)
    u0 = K.unit(bd[-1] - bg[-1])
    if bout != "oblique":
        return bg[-1], bd[-1], u0
    if obl_cote == "gauche":
        b2 = _oblique(bg, bd, obl_angle)
        if b2 is None:
            raise ValueError("la coupe oblique ne rencontre pas le flanc")
        return bg[-1], b2[-1], u0
    b2 = _oblique(bd, bg, obl_angle)
    if b2 is None:
        raise ValueError("la coupe oblique ne rencontre pas le flanc")
    return bd[-1], b2[-1], u0


def _oblique(a, b, angle_deg):
    """Tourne la coupe du bout de `angle_deg` autour du dernier point de `a`.

    La loi du lot 2, appliquee au bout du bras : la coupe tourne autour de
    celui de ses deux coins qui fait rentrer l'autre dans la lettre, donc le
    bras ne peut que maigrir. Ici le pivot est impose par l'appelant, `a` est
    le flanc conserve et `b` celui qui recule.

    Le sens de rotation n'est pas suppose : les deux sont essayes et on garde
    celui dont la droite de coupe rencontre le flanc `b` avant son bout. C'est
    le meme protocole que `sens_pour_pointe`, et pour la meme raison — un test
    generique sur la geometrie a echoue trois fois au lot 2.

    Rend le flanc `b` tronque, ou None si aucun des deux sens ne coupe. Le
    None doit remonter jusqu'a l'appelant : une coupe qui ne coupe pas est un
    reglage a corriger, pas un cas a rattraper silencieusement.
    """
    P = a[-1]
    for signe in (+1, -1):
        th = math.radians(signe * angle_deg)
        c, s = math.cos(th), math.sin(th)
        v = b[-1] - P
        w = np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])
        for i in range(len(b) - 2, -1, -1):
            u = b[i + 1] - b[i]
            det = w[0] * (-u[1]) - w[1] * (-u[0])
            if abs(det) < 1e-9:
                continue
            rhs = b[i] - P
            t = (rhs[0] * (-u[1]) - rhs[1] * (-u[0])) / det
            k = (w[0] * rhs[1] - w[1] * rhs[0]) / det
            if t > 1e-6 and -1e-9 <= k <= 1.0 + 1e-9:
                return b[:i + 1] + [b[i] + k * u]
    return None


def bras_ancre(paths, phi, longueur, epaisseur, enfoui=0.45, r_fin=0.20,
               sens=-1, n=20, courbe=1.0, pointe=0.05, effile=0.55,
               bout="pointe", obl_angle=20.0, obl_cote="gauche"):
    """Un bras rentre dont le depart est ancre dans la paroi mesuree.

    Corrige un defaut de `bras_spirale` que seule la mesure sur les quatre
    masters a montre. Son `r_debut` est une fraction du rayon *exterieur*, or
    la paroi de l'anneau passe de 57 unites en ExtraLight a 182 en ExtraBold :
    la meme fraction tombe dans la paroi au Bold et dans le vide en
    ExtraLight. Le bras s'y detachait, et le glyphe rendait deux taches
    d'encre au lieu d'une, dans les deux masters clairs seulement. C'est la
    troisieme fois du projet qu'une relation mesuree s'inverse le long de
    l'axe de graisse.

    Ici le rayon de depart est lu sur le glyphe, par croisement radial avec le
    contour interieur, puis enfoui de `enfoui` fois l'epaisseur de paroi vers
    l'exterieur. La soudure est donc vraie par construction dans tous les
    masters, et non par un reglage qui se trouve marcher dans l'un d'eux.

    L'axe est polaire et non elliptique, contrairement a `bras_spirale`. Sur
    un O de 694 sur 692 la difference est sous l'unite, et la contrepartie est
    qu'un rayon lu sur le contour et un rayon parcouru sont la meme grandeur.

    enfoui  profondeur de la soudure, en fraction de l'epaisseur de paroi
    r_fin   rayon d'arrivee, en fraction du rayon interieur au meme angle
    pointe  epaisseur a l'arrivee, en fraction de `epaisseur`
    effile  exposant de l'amincissement. En dessous de 1 le bras garde son
            epaisseur longtemps puis maigrit d'un coup, ce qui donne une
            pointe courte et franche ; au-dela il maigrit tout de suite et la
            pointe devient un long filet. Le lot 2 a montre qu'un filet trop
            fin ne se lit pas comme une pointe mais comme un bout rond, et
            qu'au flou il devient une bavure.
    bout    "pointe" : les deux bords se rejoignent en un point unique.
            "coupe" : le bout garde l'epaisseur `pointe` et se ferme par un
            segment droit. Une coupe franche est ce que la police pratique
            partout ailleurs, et elle ne peut pas disparaitre au flou.
            "oblique" : la meme coupe, tournee de `obl_angle` autour d'un de
            ses deux coins, selon `obl_cote`. C'est la loi du lot 2 appliquee
            au bout du bras : le O cesse d'echapper au systeme de coupes de la
            police au lieu d'y faire exception. Le bras ne peut que maigrir,
            le coin pivot ne bouge pas.
    courbe  vitesse a laquelle le bras plonge vers le centre. A 1 le rayon
            varie lineairement en s, donc le bras longe le bord interieur de
            l'anneau et le traverse presque tangentiellement : c'est ce qui
            fabrique la fente en aiguille du treizieme tour. En dessous de 1
            il plonge tot et traverse de biais, ce qui ouvre le coin blanc
            sans enfouir le depart. Mesure au Bold, `enfoui` 0,35 : l'angle du
            coin passe de 13,4 a 21,0 degres a `courbe` 0,7 et a 27,7 a 0,5,
            et l'arc de spirale noye dans la paroi tombe de 71 a 48 puis 32
            degres. La soudure profonde du douzieme tour obtenait le meme
            angle en noyant 119 degres, c'est-a-dire en avalant le depart du
            geste.
    enfoui  la racine est entierement dans la paroi si `enfoui` >= son demi-
            diametre rapporte a la paroi, soit `ep_facteur` / 2. Relation sans
            dimension, donc vraie dans les quatre masters. En dessous, la
            racine ressort dans la contreforme et y fait une bosse a coins
            vifs : c'est le defaut que l'oeil voyait sur l'etat affleurant du
            treizieme tour, et que l'angle du coin ne mesurait pas.
    """
    axe, bg, bd = _flancs_bras(paths, phi, longueur, epaisseur, enfoui, r_fin,
                               sens, n, courbe, pointe, effile)

    if bout == "oblique":
        if obl_cote == "gauche":
            bd2 = _oblique(bg, bd, obl_angle)
            if bd2 is None:
                raise ValueError("la coupe oblique ne rencontre pas le flanc")
            bd = bd2
        else:
            bg2 = _oblique(bd, bg, obl_angle)
            if bg2 is None:
                raise ValueError("la coupe oblique ne rencontre pas le flanc")
            bg = bg2

    def tracer(a, b):
        if bout in ("coupe", "oblique"):
            return [a[0]] + a[1:] + list(reversed(b[1:])) + [b[0]]
        return [a[0]] + a[1:-1] + [axe[-1]] + list(reversed(b[1:-1])) + [b[0]]

    pts = tracer(bg, bd)
    segs = _chaine(pts + [pts[0]])
    segs[-1] = dict(segs[-1], smooth=False)
    if K.area(segs) < 0:
        pts = tracer(bd, bg)
        segs = _chaine(pts + [pts[0]])
        segs[-1] = dict(segs[-1], smooth=False)
    return K.from_segs(segs)


def plume(paths, phi, brins, sens=+1):
    """Un faisceau de meches. `brins` est une liste de dictionnaires."""
    return [meche(paths, phi + b.pop("decalage", 0.0), sens=b.pop("sens", sens),
                  **b) for b in [dict(x) for x in brins]]


# Faisceaux proposes, calques sur le logo : une meche longue qui passe par
# dessus et deux ou trois plus courtes qui retombent le long du flanc.
LONGUE = dict(longueur=72, ecart=104, epaisseur=112, sens=-1, montee=1.7)

PLUMES = {
    "une meche": [LONGUE],
    "deux meches": [
        LONGUE,
        dict(longueur=48, ecart=78, epaisseur=60, decalage=6, sens=+1, montee=1.7),
    ],
    "trois meches": [
        LONGUE,
        dict(longueur=50, ecart=82, epaisseur=62, decalage=4, sens=+1, montee=1.7),
        dict(longueur=33, ecart=52, epaisseur=42, decalage=19, sens=+1, montee=1.7),
    ],
    "quatre meches": [
        LONGUE,
        dict(longueur=52, ecart=86, epaisseur=64, decalage=2, sens=+1, montee=1.7),
        dict(longueur=36, ecart=58, epaisseur=45, decalage=15, sens=+1, montee=1.7),
        dict(longueur=24, ecart=36, epaisseur=31, decalage=27, sens=+1, montee=1.7),
    ],
}


def ouvrir_anneau(paths, phi, ouverture, effilement, pointe=0.0,
                  effilement2=None):
    """Ouvre un anneau (contour exterieur + contour interieur) en un contour.

    Le bord interieur va d'une pointe a l'autre. Le bord exterieur, lui,
    s'arrete `effilement` degres plus tot de chaque cote et rejoint la pointe
    par une courbe : c'est cette descente du bord exterieur vers le bord
    interieur qui amincit la paroi. La faire dans l'autre sens epaissit le
    trait vers la pointe au lieu de l'affiner, ce qui donne une lame et non
    une queue. Constat fait sur planche, en regardant le resultat.

    phi         angle du milieu de la rupture, en degres, mesure depuis le
                centre de la boite (0 a droite, 90 en haut)
    ouverture   ecart angulaire entre les deux pointes, mesure au bord interieur
    effilement  longueur de l'amincissement, en degres d'arc
    pointe      position de la pointe en travers de la paroi, 0 sur le bord
                interieur, 1 sur le bord exterieur. A 0 la queue se recourbe
                vers la contreforme, ce qui est le geste de l'ecureuil.
    """
    aires = [(abs(K.area(K.to_segs(p))), p) for p in paths]
    aires.sort(key=lambda x: -x[0])
    ext, itr = K.to_segs(aires[0][1]), K.to_segs(aires[1][1])
    x0, y0, x1, y1 = boite([ext, itr])
    C = np.array([(x0 + x1) / 2.0, (y0 + y1) / 2.0])

    # Les deux bouts ne sont pas traites de la meme facon, et c'est un choix.
    # Effiler les deux donne une forme qui se lit comme une lettre abimee des
    # deux cotes ; le logo, lui, n'a qu'une queue. L'anneau recoit donc une
    # queue d'un cote et une coupe franche de l'autre, ce qui reunit les deux
    # gestes que la police connait deja : la pointe de la cedille et la coupe
    # du lot 2.
    eff2 = effilement if effilement2 is None else effilement2
    a1 = phi + ouverture / 2.0           # pointe cote depart
    a2 = phi - ouverture / 2.0           # pointe cote arrivee
    e1 = a1 + effilement                 # bouts du contour exterieur
    e2 = a2 - eff2

    i0, t0, O1 = croisement(ext, C, e1)
    i1, t1, O2 = croisement(ext, C, e2)
    j0, u0, I2 = croisement(itr, C, a2)
    j1, u1, I1 = croisement(itr, C, a1)

    arc_ext = sous_contour(ext, i0, t0, i1, t1)
    arc_int = sous_contour(itr, j0, u0, j1, u1)
    # Garde-fou : un arc pris du mauvais cote donne un contour croise, et ca ne
    # se voit pas toujours a l'oeil sur une planche.
    for arc, source, nom in ((arc_ext, ext, "exterieur"),
                             (arc_int, itr, "interieur")):
        lg = sum(K.seg_len(s) for s in arc)
        if lg < 0.35 * sum(K.seg_len(s) for s in source):
            raise ValueError(f"arc {nom} pris du mauvais cote ({lg:.0f} u)")

    def bord(ang):
        _, _, PE = croisement(ext, C, ang)
        _, _, PI = croisement(itr, C, ang)
        return PI + pointe * (PE - PI)

    T1, T2 = bord(a1), bord(a2)
    tO1 = K.tangent_in(arc_ext[0])
    tO2 = K.tangent_out(arc_ext[-1])
    tI2 = K.tangent_in(arc_int[0])
    tI1 = K.tangent_out(arc_int[-1])

    def melange(a_pointe, a_bout, n=4, expo=1.15):
        """Points du bord effile, de la pointe vers le bord exterieur.

        La paroi est interpolee entre le bord interieur et le bord exterieur :
        le trait s'amincit en suivant la courbure de l'anneau. Une seule courbe
        de Bezier tendue entre les deux bouts ne suit rien et gonfle en chemin,
        constat fait en regardant la planche.
        """
        out = []
        for k in range(n + 1):
            s = k / n
            ang = a_pointe + (a_bout - a_pointe) * s
            _, _, PE = croisement(ext, C, ang)
            _, _, PI = croisement(itr, C, ang)
            w = pointe + (1.0 - pointe) * (s ** expo)
            out.append(PI + w * (PE - PI))
        return out

    def chaine(pts, t_debut, t_fin):
        """Segments de Bezier passant par `pts`, tangentes de Catmull-Rom."""
        n = len(pts)
        tg = []
        for k in range(n):
            if k == 0:
                v = K.V(pts[1]) - K.V(pts[0]) if t_debut is None else \
                    K.V(t_debut) * float(np.hypot(*(K.V(pts[1]) - K.V(pts[0]))))
            elif k == n - 1:
                v = K.V(pts[-1]) - K.V(pts[-2]) if t_fin is None else \
                    K.V(t_fin) * float(np.hypot(*(K.V(pts[-1]) - K.V(pts[-2]))))
            else:
                v = (K.V(pts[k + 1]) - K.V(pts[k - 1])) / 2.0
            tg.append(v)
        out = []
        for k in range(n - 1):
            P, Q = K.V(pts[k]), K.V(pts[k + 1])
            out.append({"kind": "curve", "p0": tuple(P),
                        "c": [tuple(P + tg[k] / 3.0), tuple(Q - tg[k + 1] / 3.0)],
                        "p3": tuple(Q), "smooth": True})
        return out

    def bout(a_pointe, a_bout, eff, tangente, sens_retour):
        """Effilement echantillonne, ou coupe franche si l'effilement est nul."""
        if eff < 2.0:
            P, Q = (bord(a_pointe), K.V(O1) if sens_retour else K.V(O2))
            seg = {"kind": "line", "p0": tuple(P if sens_retour else Q),
                   "c": [], "p3": tuple(Q if sens_retour else P),
                   "smooth": False}
            return [seg]
        pts = melange(a_pointe, a_bout)
        return (chaine(pts, None, tangente) if sens_retour
                else chaine(list(reversed(pts)), tangente, None))

    taper1 = bout(a1, e1, effilement, tO1, True)
    taper2 = bout(a2, e2, eff2, tO2, False)

    segs = list(taper1)
    segs[-1] = dict(segs[-1], smooth=True)
    segs += arc_ext
    segs[-1] = dict(segs[-1], smooth=True)
    segs += taper2
    segs[-1] = dict(segs[-1], smooth=False)          # la pointe est un angle
    if float(np.hypot(*(K.V(T2) - K.V(I2)))) > 1.0:
        segs.append(_courbe(T2, K.unit(K.V(I2) - K.V(T2)), I2, tI2))
        segs[-1]["smooth"] = True
    else:
        segs[-1] = dict(segs[-1], p3=tuple(K.V(I2)))
    segs += arc_int
    if float(np.hypot(*(K.V(T1) - K.V(I1)))) > 1.0:
        segs[-1] = dict(segs[-1], smooth=True)
        segs.append(_courbe(I1, tI1, T1, K.unit(K.V(T1) - K.V(I1))))
    else:
        segs[-1] = dict(segs[-1], p3=tuple(K.V(T1)), smooth=False)

    for a, b in zip(segs, segs[1:] + [segs[0]]):
        if float(np.hypot(*(K.V(a["p3"]) - K.V(b["p0"])))) > 0.6:
            raise ValueError("chaine de segments rompue")
    if K.area(segs) < 0:
        raise ValueError("contour ouvert oriente a l'envers")
    return K.from_segs(segs)


# --------------------------------------------- extension de la loi du lot 2

#: Le filtre d'orientation de `loc_alignement`, et il en existe DEUX valeurs
#: depuis le trente-septieme tour.
#:
#: `PENTE_ETENDUE`, 0,3, soit 16,7 degres, est celle du troisieme tour. Elle
#: definit l'ETENDUE du titrage : `mesure_titrage.terminaisons` appelle
#: `loc_alignement` sans pente, donc au defaut, et c'est de cette etendue que
#: le perimetre arrete de 149 glyphes est tire. Elle ne bouge pas.
#:
#: `PENTE_BAS`, 0,80, soit 38,7 degres, est celle du GESTE. Elle existe parce
#: que le glyphe de titrage part du dessin servi, coupe texte comprise : le lot
#: 2 a deja tourne certains bouts, de 17,6 a 38,2 degres, et a 0,3 le
#: localisateur ne les reconnaissait plus. Vingt-quatre bouts perdaient leur
#: sortante, tous dans les masters clairs -- le A, le H, le M, le N, le Y, le
#: f, le m et le n -- avec un deficit de 10 a 21,5 unites sur neuf d'entre eux.
#: Point ouvert 66, mesure par `mesure_point66.py` et `mesure_voie1.py`.
#:
#: 0,80 EST CALE AU PLUS JUSTE, ET IL MORD DEJA SUR UN CAS. Mesure du
#: balayage : 0,60 laisse un bout manquant, 0,90 fait entrer trois gestes neufs
#: au romain et cinq en italique. A 0,80, aucun bout ne manque AU ROMAIN, aucun
#: des 32 glyphes ecrits ne change, et le depassement obtenu est identique
#: partout sauf sur le f -- point ouvert 68, la borne basse.
#:
#: LE CAS QUI MORD : le pied du Y en ExtraLight Italic, que le lot 3 a deja
#: tourne de 42,6 degres. Il faudrait une pente de 0,93 pour le rattraper, et
#: le balayage dit ce que cela couterait : un geste neuf des 0,85, cinq a 0,90,
#: sur des formes que personne n'a validees. LE DEFICIT EST DE 1,0 UNITE --
#: le texte donne deja 43,0 des 44 demandees -- donc la limite est ecrite
#: plutot que payee. Elle n'etait pas visible avant ce tour : le Y italique
#: n'avait aucun geste de titrage, et c'est le point 65 ferme qui l'a revelee.
#: `mesure_point66.py --volet 7` l'imprime avec son angle et son deficit.
#:
#: LES DEUX PENTES SONT SEPAREES PAR CHOIX, arbitre par Nicolas au trente-
#: septieme tour, voie B : le perimetre dit QUELS glyphes portent la signature,
#: le filtre du geste dit QUEL segment le recoit. Les confondre faisait passer
#: le perimetre de 149 a 160 au romain et 167 en italique, et il cessait
#: d'etre identique aux deux sources. La consequence a surveiller est qu'un
#: glyphe pourrait recevoir un geste sans etre dans l'etendue : trois l'ont
#: fait, et ils sont ecrits dans `HORS_TITRAGE`. La section 9 de
#: `check_perimetre` exige qu'il n'y en ait pas d'autre.
PENTE_ETENDUE = 0.3
PENTE_BAS = 0.80


def loc_alignement(segs, y, tol=8.0, orient="H", pente=PENTE_ETENDUE):
    """Segments droits dont un bout se pose sur la hauteur `y`.

    Choix explicite plutot que test generique : le lot 2 a montre qu'aucun
    critere de terminaison ne separe proprement un bout de trait d'une arete de
    fut sur les huit masters. On designe par position et par orientation, et on
    verifie ensuite que le meme segment est designe partout.

    `pente` est le filtre d'orientation, |dy| <= pente x |dx| en horizontal. Le
    defaut est celui de l'etendue, `PENTE_ETENDUE` ; `couper_alignements` passe
    `PENTE_BAS`, plus large, parce qu'il travaille sur un dessin dont les bouts
    sont deja tournes par le lot 2. Le defaut vaut l'ancienne valeur en dur,
    donc tout appelant qui ne demande rien voit exactement ce qu'il voyait.
    """
    out = []
    for i, s in enumerate(segs):
        if s["kind"] != "line":
            continue
        dx = s["p3"][0] - s["p0"][0]
        dy = s["p3"][1] - s["p0"][1]
        if orient == "H" and abs(dy) > abs(dx) * pente:
            continue
        if orient == "V" and abs(dx) > abs(dy) * pente:
            continue
        if min(abs(s["p0"][1] - y), abs(s["p3"][1] - y)) <= tol:
            out.append(i)
    return out


def sens_coin(segs, i, cx, cote="exterieur"):
    """Le sens de rotation, designe par le coin qu'on veut voir bouger.

    Les deux sens sont geometriquement valables : dans les deux cas le pivot
    est celui des deux coins qui fait rentrer l'autre, donc la lettre ne peut
    que maigrir. Ce qui change, c'est lequel des deux quitte sa ligne.

    `cote` a "exterieur" fait monter le coin le plus loin de l'axe de la
    lettre : le pied s'incline vers le dedans, la silhouette reste pleine sur
    l'exterieur. A "interieur" c'est le coin proche de l'axe qui monte, et le
    pied se termine en pointe vers le dehors. Mesure sur le X au Bold : le
    premier coute 55 unites de montee, le second 93.
    """
    # Un sens unique pour toute la police, sans regarder les coins : les pentes
    # partent alors toutes du meme cote, comme une main qui tient un outil dans
    # une seule position. Les lettres symetriques cessent de l'etre.
    if cote == "horaire":
        return -1
    if cote == "antihoraire":
        return +1
    P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    vise = 0 if abs(P[0] - cx) < abs(Q[0] - cx) else 1
    if cote == "exterieur":
        vise = 1 - vise
    for sn in (+1, -1):
        try:
            ap = K.coupe(segs, i, 5.0, sn, 0.0)
        except Exception:
            continue
        dP = float(np.hypot(*(K.V(ap[i]["p0"]) - P)))
        dQ = float(np.hypot(*(K.V(ap[i]["p3"]) - Q)))
        if (0 if dP > dQ else 1) == vise:
            return sn
    return +1


def plafond_coupe(segs, i, sense, hi=70.0):
    """Le plus grand angle ou la coupe reste dans le trait, par dichotomie.

    Le plafond n'est pas choisi, il est trouve. Meme methode qu'au lot 3 pour
    l'extrapolation : on cherche le point de rupture au lieu de le supposer.
    """
    n = len(segs)

    def tient(th):
        try:
            ib, ia = (i - 1) % n, (i + 1) % n
            P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
            d = K.outward(segs, i)
            v = Q - P
            w = K.rot(v, math.radians(th) * sense) - v
            if float(np.dot(w, d)) < 0:
                t = K.hit_line(segs[ia], P, K.unit(K.rot(v, math.radians(th) * sense)), 0.0)
            else:
                t = K.hit_line(segs[ib], Q, K.unit(K.rot(-v, math.radians(th) * sense)), 1.0)
                t = None if t is None else 1.0 - t
        except Exception:
            return False
        return t is not None and -0.02 <= t <= 1.0

    if not tient(1.0):
        return 0.0
    if tient(hi):
        return hi
    lo, h = 1.0, hi
    for _ in range(22):
        mil = (lo + h) / 2.0
        if tient(mil):
            lo = mil
        else:
            h = mil
    return lo


# `_prolonge` et `coupe_sortante` sont descendues dans `coupe.py` au
# vingt-deuxieme tour, quand le lot 2 en a eu besoin pour la pointe du pied du
# n : `lot4` importe `lot2`, donc `lot2` ne peut pas importer `lot4`. Elles ne
# connaissaient aucun glyphe, leur place etait de toute facon la-bas. Les alias
# gardent le reste de ce fichier et ses planches intacts.

_prolonge = K._prolonge
coupe_sortante = K.coupe_sortante


#: La borne haute de la dichotomie de `angle_pour_depassement`. Elle vivait en
#: dur dans la fonction depuis le troisieme tour, et c'est le point ouvert 53 :
#: quand la cible n'est pas atteinte a cet angle, la fonction RETOURNE la borne
#: au lieu de refuser, donc la borne se fait passer pour un fait de la lettre.
#: Mesure au trente-sixieme tour : elle mord sur huit glyphe-masters du lot de
#: propagation -- le t italique ExtraLight sort de 17,0 unites pour 32
#: demandees. Portee a 70 degres, la cible est atteinte dans les huit cas.
#: La valeur reste 45 tant que Nicolas n'a pas tranche sur planche ; ce qui
#: change ici est que la saturation est JOURNALISEE au lieu d'etre muette.
BORNE_SORTIE = 45.0

#: La borne BASSE de la meme dichotomie, et c'est le point ouvert 68. Elle
#: vivait en dur, `lo = 0.5`, et elle ment dans l'autre sens : quand cet angle
#: minimal fait DEJA depasser plus que la cible, la dichotomie converge vers
#: elle et la fonction rend `atteint=True` sur une sortie TROP LONGUE. Le
#: defaut ne peut naitre que sur un bout que le lot 2 a deja coupe, donc il
#: n'apparait pas depuis la source amont -- il est ne avec le point 66.
#: Elle est nommee ici pour que la mesure puisse la faire varier : le chiffre
#: qui decide est ce que le bout livre a angle NUL, et lui seul dit si la
#: sur-livraison vient de la borne ou du dessin de texte.
#:
#: MESUREE AU TRENTE-HUITIEME TOUR, sur les huit masters des deux sources et
#: les 149 glyphes du perimetre : vingt sorties depassaient leur cible a 0,5
#: degre. SIX venaient de la borne, toutes sur le f, et tombent a la cible des
#: 0,1 ; les QUATORZE autres sont `y.sc` et `ydieresis.sc`, qui depassent
#: encore a 0,001 degre, donc a angle nul -- leur cause est que
#: `depassement_pour` leur demande 32 quand le dessin leur en livre 37,8, et
#: elle appartient au point ouvert 67.
#:
#: Nicolas a tranche 0,1 degre. Le prix est mesure et non estime : 22
#: glyphe-masters sur 1 192 bougent, d'au plus 1,20 unite, soit 0,09 pixel a
#: 72 px de corps quand le seuil de jugement du projet est de six pixels. Le
#: perimetre, le regime du haut et les onze derogations ne bougent pas.
BORNE_BASSE = 0.1

#: La marge au-dela de laquelle une sortie est declaree TROP LONGUE. Elle
#: existe parce que la comparaison stricte `bas > cible` declenche sur un
#: epsilon : un bout qui livre 32,0000001 pour 32 demandees sortait annonce
#: "TROP LONGUE : 32 u pour 32 demandees", ce qui est absurde a lire et faux a
#: compter. La valeur est celle du journal, qui arrondit a l'unite -- un demi
#: est du bruit d'affichage, pas une sur-livraison. **Un controle et le code
#: qu'il controle doivent partager leur seuil** : `mesure_point68.MARGE` lit
#: celui-ci au lieu d'en tenir un second.
TOLERANCE_CIBLE = 0.5


def angle_pour_depassement(segs, i, sense, cible, ligne, hi=None, lo=None):
    """L'angle de coupe sortante qui fait depasser de `cible` unites.

    L'angle n'est pas choisi, il est deduit de la quantite de depassement
    voulue : Nicolas demande que la diagonale depasse legerement, pas qu'elle
    tourne d'un angle donne. Le depassement est la grandeur qui se voit.

    Rend `(theta, atteint)` comme `angle_pour_rentree`, et non le seul angle :
    `atteint` dit si la cible est obtenue ou si c'est la borne qui repond. Sans
    lui, une sortie courte ne se distingue pas d'une sortie pleine, et c'est ce
    qui a fait ecrire au trente-cinquieme tour que la sortante tient sa promesse
    partout.

    `atteint` REPOND DANS LES DEUX SENS depuis le trente-huitieme tour, et
    c'est le point ouvert 68. La borne haute a ete corrigee au trente-sixieme :
    quand la cible n'est pas atteinte a `hi`, la fonction rend `(hi, False)` au
    lieu de faire passer la borne pour un fait de la lettre. La borne BASSE
    mentait de la meme facon, en sens inverse : quand l'angle minimal fait deja
    depasser PLUS que la cible, la dichotomie ne peut que descendre `hi` vers
    `lo`, elle converge sur la borne, et l'ancienne version rendait
    `(lo, True)` sur une sortie trop longue. Elle rend `(lo, False)`.

    Une borne qui se rend elle-meme en reponse ment sans lever, et elle a deux
    bouts : les deux sont maintenant fermes.
    """
    # Les deux bornes se resolvent sous un AUTRE NOM que leur parametre : le
    # trente-septieme tour a perdu un balayage entier parce qu'un parametre
    # masquait la valeur qu'un `with` forcait, et la colonne est sortie
    # uniforme sans qu'un seul appel ne leve.
    hi_max = BORNE_SORTIE if hi is None else hi
    lo_min = BORNE_BASSE if lo is None else lo

    def sortie(th):
        try:
            ap = coupe_sortante(segs, i, th, sense)
        except ValueError:
            return None
        ys = [ap[i]["p0"][1], ap[i]["p3"][1]]
        return max(abs(y - ligne) for y in ys)

    lo, hi = lo_min, hi_max
    bas = sortie(lo)
    if bas is None:
        return None
    # Le bout depasse deja plus que demande a l'angle minimal : aucun angle de
    # la fourchette ne peut faire moins, et la dichotomie convergerait sur la
    # borne en l'annoncant atteinte.
    if bas > cible + TOLERANCE_CIBLE:
        return (lo, False)
    haut = sortie(hi)
    if haut is not None and haut < cible:
        return (hi, False)
    for _ in range(24):
        mil = (lo + hi) / 2.0
        v = sortie(mil)
        if v is None or v > cible:
            hi = mil
        else:
            lo = mil
    return (lo, True)


def angle_pour_rentree(segs, i, sense, cible, hi=70.0):
    """L'angle de coupe RENTRANTE qui fait rentrer le coin de `cible` unites.

    Symetrique de `angle_pour_depassement`, et sa raison d'etre est mesuree au
    trente-cinquieme tour. La sortante a une cible en unites depuis le neuvieme
    tour ; la rentrante est restee a angle constant, heritee du lot 2 ou elle ne
    coupe que des bouts courts. Appliquee par `loc_alignement` a une FACE de
    barre entiere, sa profondeur vaut longueur x tan(theta) : 189,6 unites sur
    la barre haute du E au Bold pour 44 demandees en bas, 271,6 sur l'AE. Et
    elle s'aggrave avec la graisse, la barre s'epaississant, donc un meme angle
    donne quatre resultats.

    C'est le regime que le point ouvert 63 decrivait comme une propriete de la
    sortante. La sortante, elle, tient sa promesse a 44,0 et 32,0 unites
    exactement sur les 48 glyphes et les quatre masters romains.

    La borne est portee a 70 degres, au-dela de ce que la geometrie permet, et
    la saturation est rendue a l'appelant plutot que tue : une borne qui se fait
    passer pour un fait de la lettre est un piege que ce projet a paye au
    vingt-huitieme tour.

    Retourne (theta, atteint) -- `atteint` faux quand la geometrie sature avant
    la cible -- ou None quand aucune coupe ne passe.
    """
    y0, y1 = segs[i]["p0"][1], segs[i]["p3"][1]

    def rentree(th):
        try:
            ap = K.coupe(segs, i, th, sense, 0.0)
        except ValueError:
            return None
        return max(abs(ap[i]["p0"][1] - y0), abs(ap[i]["p3"][1] - y1))

    lo = 0.1
    if rentree(lo) is None:
        return None
    haut = rentree(hi)
    if haut is not None and haut < cible:
        return hi, False
    for _ in range(24):
        mil = (lo + hi) / 2.0
        v = rentree(mil)
        if v is None or v > cible:
            hi = mil
        else:
            lo = mil
    return lo, True


def sens_pour_pointe(segs, i, cote_pointe, theta=6.0):
    """Le sens de coupe sortante qui fait descendre le coin du cote demande.

    Choix explicite puis verification, plutot qu'un test generique. Le lot 2 a
    montre qu'aucun critere abstrait ne separe proprement les cas sur les huit
    masters : on nomme le coin voulu, on essaie les deux sens, et on garde
    celui qui le fait bouger du bon cote. La verification est dans la fonction,
    pas dans un commentaire.

    Demande de Nicolas sur le X et le x : sortant en bas a gauche, et la pointe
    a gauche.

    cote_pointe  "gauche" ou "droite"
    Retourne le sens, ou None si aucun des deux ne donne ce resultat.
    """
    P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    vise_gauche = cote_pointe == "gauche"
    for sn in (+1, -1):
        try:
            ap = coupe_sortante(segs, i, theta, sn)
        except ValueError:
            continue
        dP = float(np.hypot(*(K.V(ap[i]["p0"]) - P)))
        dQ = float(np.hypot(*(K.V(ap[i]["p3"]) - Q)))
        if dP > dQ:
            mobile, fixe = ap[i]["p0"], Q
        else:
            mobile, fixe = ap[i]["p3"], P
        if (float(mobile[0]) < float(fixe[0])) == vise_gauche:
            return sn
    return None


def redresser(segs, angle):
    """Les segments desinclines de `angle` degres autour de la ligne de base.

    Cisaillement pur, x' = x - y tan(a), sur une COPIE : il ne sert qu'au
    classement et aucun contour n'est modifie. La ligne de base est le pivot
    parce que c'est celui de l'italique.
    """
    t = math.tan(math.radians(angle or 0.0))
    if not t:
        return segs
    out = []
    for s in segs:
        d = dict(s)
        for cle in ("p0", "p1", "p2", "p3"):
            if d.get(cle) is not None:
                x, y = d[cle]
                d[cle] = (x - y * t, y)
        out.append(d)
    return out


def quadrant(segs, i, bbox, angle=0.0):
    """Ou se trouve la terminaison `i` dans la lettre : bg, bc, bd, hg, hc, hd.

    Sert a designer une terminaison par sa place et non par son indice, qui
    change d'un master a l'autre. Nicolas designe ses choix comme ca : le bas
    gauche du A reste plat, le bas droit et le haut gauche du X tournent.

    `angle` DESINCLINE le contour avant de classer, et c'est le point ouvert 65
    ferme au trente-septieme tour. La boite d'un italique ne penche pas, mais la
    lettre si : un pied part a gauche, un sommet part a droite, et le meme bout
    changeait de quadrant d'une source a l'autre. Sept prescriptions arretees
    etaient dans ce cas -- A I V W Y v w -- et le Y italique n'avait PLUS AUCUN
    geste de titrage, son `sortantes={"bc"}` ne l'attrapant plus.
    Mesure par `mesure_point65.py` : en redressant, les sept convergent, huit
    gestes reviennent en italique -- le Y dans ses quatre masters, le I dans
    deux -- aucun ne disparait, et les deux sources tombent a 232 gestes.
    LE ROMAIN NE BOUGE PAS D'UNE UNITE, son angle valant zero.
    L'angle est LU dans le master par `appliquer_reglage`, jamais recopie : le
    projet a deja paye une borne recopiee dans un second fichier.
    """
    if angle:
        segs = redresser(segs, angle)
        xs = [c for s in segs for c in (s["p0"][0], s["p3"][0])]
        ys = [c for s in segs for c in (s["p0"][1], s["p3"][1])]
        bbox = (min(xs), min(ys), max(xs), max(ys))
    x0, y0, x1, y1 = bbox
    mx, my = K.mid(segs[i])
    larg = max(x1 - x0, 1.0)
    if mx < x0 + 0.35 * larg:
        h = "g"
    elif mx > x1 - 0.35 * larg:
        h = "d"
    else:
        h = "c"
    v = "b" if my < (y0 + y1) / 2.0 else "h"
    return v + h


def couper_alignements(layer, theta, hauteurs, orient="H", journal=None, nom="",
                       marge=0.75, cote="exterieur", exclure=(),
                       sortantes=(), depassement=22.0, pointes=None,
                       rentrantes="angle", borne_sortie=None,
                       angle_italique=0.0):
    """Applique la loi du lot 2 aux terminaisons posees sur un alignement.

    L'angle demande est plafonne par glyphe et par segment : le X casse a
    32 degres au Bold, le x a 28, alors que la plupart des pieds de minuscules
    n'ont aucune limite utile. Un angle unique impose partout sortirait du
    trait sur les diagonales.

    sortantes  ensemble de quadrants, ou une des deux chaines :
               "tous" toutes les terminaisons non exclues ;
               "bas"  celles du bas seulement.
               L'argument d'appui ne vaut que pour la ligne de base : c'est la
               qu'une lettre parait decollee quand la coupe lui prend son
               assise. En haut il n'y a pas d'assise a perdre, et une sortante
               fait monter le glyphe au-dessus de la ligne de capitale, ce qui
               desaligne le haut du mot. Constat fait en regardant l'alphabet.
    pointes    dictionnaire quadrant -> "gauche" ou "droite", pour imposer de
               quel cote la pointe descend. Verifie par sens_pour_pointe.
    rentrantes le regime des terminaisons NON sortantes, celles du haut avec
               `sortantes="bas"`. Ouvert au trente-cinquieme tour, quand la
               mesure a montre que le gros des deplacements du titrage vient
               d'elles et non de la sortante :
               "angle"   l'angle constant du lot 2, borne par le plafond. Etat
                         de tout ce qui est ecrit, donc le defaut.
               "aucune"  le haut n'est pas touche. C'est ce que les vingt-et-un
                         glyphes ecrits obtiennent par leurs alignements ou par
                         `exclure`, et l'etat du n, du m, du h, du b et du d.
               "unites"  la rentrante prend la meme cible en unites que la
                         sortante, l'angle etant deduit par
                         `angle_pour_rentree`. Trois regimes a montrer sur
                         planche, un seul sera ecrit.
    borne_sortie
               la borne haute de la dichotomie de la SORTANTE. `None` prend
               `BORNE_SORTIE`, 45 degres, qui est l'etat ecrit. Le parametre
               n'existe que pour la planche d'instruction du trente-sixieme
               tour, qui montre ce que la borne coute : elle mord sur huit
               glyphe-masters, et la fonction rendait la borne comme si c'etait
               une reponse. La saturation est maintenant journalisee.
    """
    pointes = pointes or {}
    for p in list(L.paths(layer)):
        segs = K.to_segs(p)
        xs = [c for s in segs for c in (s["p0"][0], s["p3"][0])]
        ys = [c for s in segs for c in (s["p0"][1], s["p3"][1])]
        bbox = (min(xs), min(ys), max(xs), max(ys))
        cx = (min(xs) + max(xs)) / 2.0
        idx = []
        for y in hauteurs:
            # PENTE_BAS et non le defaut : le glyphe de titrage part du dessin
            # servi, dont le lot 2 a deja tourne certains bouts. Voir la note
            # de `PENTE_BAS`, et `mesure_voie1.py` pour le balayage.
            idx += loc_alignement(segs, y, orient=orient, pente=PENTE_BAS)
        idx = sorted(set(idx), reverse=True)
        idx = [i for i in idx
               if quadrant(segs, i, bbox, angle_italique) not in exclure]
        if not idx:
            continue
        for i in idx:
            sn = sens_coin(segs, i, cx, cote)
            avant = (segs[i]["p0"][1], segs[i]["p3"][1])
            qd = quadrant(segs, i, bbox, angle_italique)
            sort = (sortantes == "tous"
                    or (sortantes == "bas" and qd[0] == "b")
                    or (sortantes not in ("tous", "bas") and sortantes
                        and qd in sortantes))
            if sort:
                ligne = min(hauteurs, key=lambda h: abs(K.mid(segs[i])[1] - h))
                if qd in pointes:
                    sp = sens_pour_pointe(segs, i, pointes[qd])
                    if sp is None:
                        if journal is not None:
                            journal.append((nom, i, f"pointe {pointes[qd]} "
                                            f"impossible", 0.0, sn))
                        continue
                    sn = sp
                r = angle_pour_depassement(segs, i, sn, depassement, ligne,
                                           hi=borne_sortie)
                if r is None and qd not in pointes:
                    sn = -sn
                    r = angle_pour_depassement(segs, i, sn, depassement, ligne,
                                               hi=borne_sortie)
                if r is None:
                    if journal is not None:
                        journal.append((nom, i, "sortie impossible", 0.0, sn))
                    continue
                th, atteint = r
                try:
                    segs = coupe_sortante(segs, i, th, sn)
                except ValueError as e:
                    if journal is not None:
                        journal.append((nom, i, f"echec {e}", 0.0, sn))
                    continue
                if journal is not None:
                    dep = max(abs(segs[i]["p0"][1] - ligne),
                              abs(segs[i]["p3"][1] - ligne))
                    journal.append((nom, i, round(th, 1),
                                    f"sort de {dep:.0f}", sn))
                    if not atteint:
                        # Une entree SEPAREE, et non un suffixe sur la chaine :
                        # `partage` lit "sort de N" par son dernier champ, dans
                        # deux scripts. Une note passe par le canal des refus,
                        # qui existe deja et qu'aucun lecteur ne casse.
                        # LE SENS EST DANS LE LIBELLE, et c'est le point 68 :
                        # depuis que la borne BASSE repond elle aussi, un seul
                        # libelle couvrirait une sortie trop courte et une
                        # sortie trop longue. Le prefixe ne bouge pas,
                        # `mesure_haut_titrage.partage` le lit.
                        sens = ("TROP LONGUE"
                                if dep > depassement + TOLERANCE_CIBLE
                                else "trop courte")
                        journal.append(
                            (nom, i, f"sortie SATUREE a {th:.1f} deg, {sens} : "
                             f"{dep:.0f} u pour {depassement:.0f} demandees",
                             0.0, sn))
                continue
            if rentrantes == "aucune":
                if journal is not None:
                    journal.append((nom, i, "haut non traite", 0.0, sn))
                continue
            plaf = marge * plafond_coupe(segs, i, sn)
            sature = False
            if rentrantes == "unites":
                r = angle_pour_rentree(segs, i, sn, depassement)
                if r is None:
                    if journal is not None:
                        journal.append((nom, i, "rentree impossible", 0.0, sn))
                    continue
                th_c, atteint = r
                th = min(th_c, plaf)
                # Le plafond peut mordre la ou l'angle constant ne mordait pas :
                # une cible en unites demande un GRAND angle sur un segment
                # court. Le dire, plutot que sous-livrer en silence.
                sature = (not atteint) or th_c > plaf + 1e-6
            else:
                th = min(theta, plaf)
            if th < 1.0:
                if journal is not None:
                    journal.append((nom, i, "plafond nul", 0.0, sn))
                continue
            try:
                segs = K.coupe(segs, i, th, sn, 0.0)
            except ValueError as e:
                if journal is not None:
                    journal.append((nom, i, f"echec {e}", 0.0, sn))
                continue
            if journal is not None:
                monte = max(abs(segs[i]["p0"][1] - avant[0]),
                            abs(segs[i]["p3"][1] - avant[1]))
                journal.append((nom, i, round(th, 1),
                                (f"{monte:.1f} SATURE" if sature
                                 else round(monte, 1)), sn))
        layer.shapes[layer.shapes.index(p)] = K.from_segs(segs)


def E_titrage(layer, theta=20.0):
    """Le E de la coupe de titrage : la droite du F, et la barre basse a rebours.

    Le F a ses deux bouts de barre sur une seule droite. Le E n'y arrivait pas,
    pour deux raisons distinctes qu'il a fallu lever separement.

    1. *La bride sur la barre mediane.* La droite du lot 2 ne peut que
       raccourcir. Elle ne mord qu'au Bold et a l'ExtraBold, ou elle retient la
       barre mediane de 42 et de 52 unites : autrement dit **la droite du E
       n'existait pas dans les deux masters gras**. `brider=False` la leve, ce
       qui est reserve au titrage — a une taille de titre, une contreforme un
       peu plus fermee ne coute pas ce qu'elle coute dans un paragraphe.

    2. *La barre basse.* La mener sur la droite la fait passer de 514 a 318
       unites au Bold et casse la lettre : la distance E/F a acuite reduite
       tombe de 0,242 a 0,142, quand la paire la plus serree de l'etalonnage,
       I/T, vaut 0,209. Le E passerait sous la paire la plus confusable de
       l'alphabet, et a l'image floutee ELEVE se lit FLFVF.

       La sortie retenue par Nicolas garde la longueur et retourne le geste :
       la barre basse garde sa coupe, **tournee dans l'autre sens**. Les trois
       bouts ne sont plus sur une droite, mais les deux du haut le sont et le
       troisieme leur repond au lieu de les suivre. La longueur ne bouge pas,
       donc la distinction E/F non plus.

    Les trois bouts sont designes une seule fois, sur le glyphe encore droit,
    puis tournes du dernier vers le premier. Les relocaliser entre les deux
    rotations rendrait autre chose : une coupe tournee de 20 degres n'est plus
    verticale, et `lines(vertical=True)` ne la retient plus. C'est le piege du
    lot 3, et il ne coute rien de l'eviter par construction.
    """
    L.barres(layer, L.loc_barres_E, theta, L.CW, garder_basse=True,
             brider=False)
    for p in list(L.paths(layer)):
        segs = K.to_segs(p)
        idx = L.loc_barres_E(segs)
        if len(idx) < 3:
            continue
        bas_vers_haut = sorted(idx, key=lambda i: K.mid(segs[i])[1])
        sens = {bas_vers_haut[0]: L.CCW}
        for i in bas_vers_haut[1:]:
            sens[i] = L.CW
        for i in sorted(idx, reverse=True):
            segs = K.coupe(segs, i, theta, sens[i], 0.0)
        layer.shapes[layer.shapes.index(p)] = K.from_segs(segs)


# ----------------------------------------------------------------- le O spirale
#
# Le O de titrage n'est pas derive du O d'Atkinson : il est dessine. Demande de
# Nicolas : un debut de spirale qui part du centre a gauche, monte vers la
# droite, redescend, remonte vers la gauche et passe au-dessus de son depart.
# Soit un tour et un huitieme, dans le sens horaire, le rayon croissant.
#
# L'anneau exterieur reste un anneau presque complet, ce qui protege la lecture
# du O ; la spirale ne se voit que dans la contreforme, ou elle apporte la
# signature. Le trait garde la modulation d'Atkinson, epais aux flancs et mince
# en haut et en bas, pour que la lettre reste de la meme famille.

def spirale(rx, ry, cx, cy, epaisseur, modulation=1.29,
            depart=180.0, balayage=-410.0, rayon_debut=0.32, s_plein=0.20,
            ep_debut=0.16, s_epaisseur=0.55, n=20, fin_coupee=0.0,
            profil="arc", derive=(0.0, 0.0)):
    """Un contour de spirale, dessine et non derive.

    rx, ry          demi-axes de la lettre
    cx, cy          centre
    epaisseur       epaisseur du trait au plus epais, en unites
    modulation      rapport epais sur mince, celui du O d'Atkinson
    depart          angle de depart, en degres (180 = a gauche)
    balayage        arc parcouru, negatif pour le sens horaire
    rayon_debut     rayon du bout interieur, en fraction du rayon plein
    s_plein         fraction du parcours au bout de laquelle le rayon est plein
    ep_debut        epaisseur du bout interieur, en fraction de l'epaisseur
    s_epaisseur     fraction du parcours au bout de laquelle le trait est plein
    fin_coupee      rotation de la coupe du bout exterieur, en degres, la loi
                    du lot 2 appliquee au dernier segment droit du glyphe
    """
    axe, demi = [], []
    for k in range(n + 1):
        s = k / n
        ang = math.radians(depart + balayage * s)
        if profil == "volute":
            # Volute ionique : le rayon decroit du dehors vers l'oeil sur tout
            # le parcours, et le centre se deplace. C'est ce deplacement qui
            # donne l'ecart entre les spires, y compris en haut, la ou ma
            # premiere version ecrasait la petite spire contre la grande.
            r = rayon_debut + (1.0 - rayon_debut) * s
        elif profil == "log":
            # Spirale logarithmique : le rayon croit de facon geometrique.
            r = rayon_debut * (1.0 / rayon_debut) ** s
        else:
            f = min(1.0, s / s_plein) ** 0.92
            r = rayon_debut + (1.0 - rayon_debut) * f
        dcx = cx + (1.0 - s) * derive[0]
        dcy = cy + (1.0 - s) * derive[1]
        g = min(1.0, s / s_epaisseur) ** 0.85
        e = epaisseur * (ep_debut + (1.0 - ep_debut) * g)
        # modulation d'Atkinson : le trait est plus epais aux flancs
        mince = e / modulation
        e = mince + (e - mince) * (math.cos(ang) ** 2)
        axe.append(np.array([dcx + rx * r * math.cos(ang),
                             dcy + ry * r * math.sin(ang)]))
        demi.append(e / 2.0)

    gauche, droite = [], []
    for k in range(n + 1):
        if k == 0:
            t = K.unit(axe[1] - axe[0])
        elif k == n:
            t = K.unit(axe[-1] - axe[-2])
        else:
            t = K.unit(axe[k + 1] - axe[k - 1])
        nn = K.perp(t)
        gauche.append(axe[k] + demi[k] * nn)
        droite.append(axe[k] - demi[k] * nn)

    # Bout interieur en pointe, bout exterieur coupe net. L'ordre de parcours
    # n'est pas libre : en tournant dans le sens horaire, le bord gauche du
    # deplacement est le bord exterieur, donc parcourir gauche puis droite
    # donne un contour horaire, donc une aire negative, donc un trou au lieu
    # d'une lettre. On part par le bord interieur.
    pts = [axe[0]] + droite[1:] + list(reversed(gauche[1:]))
    segs = _chaine(pts + [pts[0]])
    segs[-1] = dict(segs[-1], smooth=False)          # la pointe est un angle
    i_fin = n                                        # segment droite[n] -> gauche[n]
    segs[i_fin] = {"kind": "line", "p0": tuple(droite[-1]), "c": [],
                   "p3": tuple(gauche[-1]), "smooth": False}
    segs[i_fin - 1] = dict(segs[i_fin - 1], p3=tuple(droite[-1]), smooth=False)
    if K.area(segs) < 0:
        raise ValueError("spirale orientee a l'envers")
    if fin_coupee:
        segs = K.coupe(segs, i_fin, abs(fin_coupee),
                       1 if fin_coupee > 0 else -1, 0.0)
    return K.from_segs(segs)


def O_spirale(layer, marge_haut=0.0, **r):
    """Remplace les contours d'un calque de O par la spirale.

    Les demi-axes et l'epaisseur sont pris sur le O d'origine : la lettre garde
    sa hauteur, sa largeur et sa couleur, seul son trace change.
    """
    ps = L.paths(layer)
    x0, y0, x1, y1 = boite([K.to_segs(p) for p in ps])
    ext = K.to_segs(max(ps, key=lambda p: abs(K.area(K.to_segs(p)))))
    itr = K.to_segs(min(ps, key=lambda p: abs(K.area(K.to_segs(p)))))
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    # epaisseur au flanc : distance entre les deux contours a mi-hauteur
    C = np.array([cx, cy])
    _, _, PE = croisement(ext, C, 180.0)
    _, _, PI = croisement(itr, C, 180.0)
    ep = float(np.hypot(*(K.V(PE) - K.V(PI))))
    # Le rayon passe par l'axe du trait, pas par son bord. Retirer la
    # demi-epaisseur ne suffit pas : la modulation amincit le trait en haut et
    # en bas, et l'echantillonnage rogne les extremes. La lettre sortait 67
    # unites plus courte que le O, ce qui se serait vu dans un mot. On ajuste
    # donc les demi-axes sur la boite mesuree, en deux passes.
    rx = (x1 - x0) / 2.0 - ep / 2.0
    ry = (y1 - y0) / 2.0 - ep / 2.0 - marge_haut
    vise_l, vise_h = x1 - x0, y1 - y0 - 2 * marge_haut
    p = None
    for _ in range(3):
        p = spirale(rx, ry, cx, cy, ep, **r)
        a0, b0, a1, b1 = boite([K.to_segs(p)])
        if a1 - a0 < 1 or b1 - b0 < 1:
            break
        rx *= vise_l / (a1 - a0)
        ry *= vise_h / (b1 - b0)
    # recalage vertical sur la boite du O : la spirale n'est pas symetrique,
    # son centre ne tombe pas sur celui de l'ellipse.
    a0, b0, a1, b1 = boite([K.to_segs(p)])
    dx, dy = x0 - a0, y0 + marge_haut - b0
    if abs(dx) > 0.1 or abs(dy) > 0.1:
        for n_ in p.nodes:
            n_.position.x = round(n_.position.x + dx, 1)
            n_.position.y = round(n_.position.y + dy, 1)
    return p


# Le O de titrage : le reglage arrete par Nicolas au quinzieme tour, et lui
# seul. Cette table portait jusqu'ici les quatre familles explorees au
# quatrieme tour et un avertissement disant qu'elle etait perimee ; les deux
# sont retires, la question qu'ils gardaient ouverte est tranchee.
#
# La forme : famille C, le bras rentre, en miroir horizontal. Le miroir se fait
# sur le parametrage et non sur le glyphe — `phi` passe de 150 a 30 degres et
# `sens` s'inverse — de sorte que le O reste celui d'Atkinson au bit pres et que
# tout le dessin ajoute tienne dans un seul contour pose par-dessus.
#
# Les trois reponses du quinzieme tour, dans l'ordre ou elles ont ete posees :
#   A4  `courbe` 0,35, la plongee raide. Le bras traverse le bord interieur de
#       l'anneau de biais au lieu de le longer, ce qui ouvre le coin blanc a
#       l'emergence : 43,7 degres en ExtraLight, 34,2 en ExtraBold. Il ne
#       s'effondre dans aucun master, quand `courbe` 1,0 y fabriquait une
#       aiguille a 12,8 degres au Bold.
#   B0  `pointe` 0,05, le bout le plus fin des six soumis.
#   C1  `r_fin` 0,20, la boucle serree. Elle n'est pas independante de la
#       plongee : a 0,40 le bras reste plus longtemps parallele a la paroi et
#       l'aiguille revient.
#
# `enfoui` 0,35 tient a une inegalite sans dimension, donc vraie dans les
# quatre masters : la racine est enfouie si `enfoui` >= `ep_facteur` / 2, soit
# 0,275 ici. Ne pas descendre sous cette valeur sans relire `mesure_O.fente`,
# qui lit la saillie sur les deux coins reellement dessines et non sur la
# formule — une coupe droite posee sur une paroi courbe peut ressortir par un
# coin que l'inegalite ne voit pas.
#
# `ep_facteur` multiplie l'epaisseur de paroi mesuree sur le glyphe : les
# reglages restent valables d'un master a l'autre au lieu d'etre cales sur le
# Bold, ou la paroi vaut 168 unites et l'ExtraLight 57.
#
# Un piege ecarte, et la mesure qui l'a ecarte. `pointe` etant une fraction de
# l'epaisseur du bras, le bout dessine ne fait pas la meme chose d'un master a
# l'autre : 1,6 unite en ExtraLight contre 5,0 en ExtraBold. Un bout exprime en
# unites a ete dessine a cote et rasterise a 36, 60 et 96 pixels de cadratin :
# les deux rendent la meme image, y compris en ExtraLight ou le rapport est de
# 1 a 3. Le bout est trop loin dans l'effilement pour que sa largeur decide de
# quoi que ce soit. Ne pas rouvrir sans rasteriser : une loupe vectorielle
# montre toujours une pointe, quelle que soit sa largeur, parce qu'elle n'a pas
# de pixels. Preuve dans `temoin/planche-lot4p-retenu.png`, section 3.
#
# Verifie sur les quatre masters romains, quinzieme tour : saillie 0,0 partout,
# jour au bout jamais sous 52 unites pour un seuil de 24, une tache et une
# contreforme aux deux resolutions, aucun contact dans OXA, TEMOIN, PROTOCOLE.
# Distance au O d'origine 0,091 a 0,125 selon le master, quand le G est a 0,159
# et le C a 0,253 en ExtraBold : le signe reste un O.
# QUARANTE-SEPTIEME TOUR : LA BASE S'EPAISSIT, ET LE COIN BLANC S'EFFILE.
# Nicolas a validé le bras interieur sur `planche-O-1b-lecture-18px.png`, en
# TEXTE et aux quatre graisses, puis a demande deux corrections successives,
# chacune regardee sur sa propre planche. OU IL A REGARDE EST ECRIT ICI, parce
# que le projet a revise quatre validations prises ailleurs qu'a la taille de
# lecture -- le i, le k et le 1.
#
# 1. LA BASE, sur `planche-O-4-base.png`. Elle etait trop maigre des le
#    Regular. Le seul parametre qui l'epaissit est `ep_facteur` : a la racine
#    le bras vaut exactement `ep_paroi x ep_facteur`, et `effile` n'y change
#    rien par construction. Mais la paroi du O passe de 57 unites en ExtraLight
#    a 182 en ExtraBold, donc une fraction unique donne 31 unites d'un cote et
#    100 de l'autre. D'ou une valeur PAR MASTER, la deuxieme du projet apres
#    `lot2.ALLONGE_T` : les clairs rattrapent, les gras ne bougent presque pas.
#
# 2. LE COIN BLANC, sur `planche-O-6-coin.png` puis `planche-O-8-fin.png`.
#    Epaissir seul faisait une RUPTURE : le blanc coince entre le dos du bras
#    et la paroi haute devenait une bande qui se fermait d'un coup. Le levier
#    qui l'effile est `courbe`, l'exposant de la loi du rayon de l'axe. Sous 1
#    le bras plonge vers l'interieur des le depart et s'ecarte vite de la
#    paroi ; plus pres de 1 il la LONGE avant de plonger, donc le blanc
#    au-dessus devient une aiguille. Nicolas a retenu 0,45 apres avoir vu
#    0,35 / 0,40 / 0,45 / 0,50 / 0,55 cote a cote.
#
# LE PRIX EST MESURE ET IL EST DANS UNE SEULE GRANDEUR : plus le bras longe la
# paroi, plus il y reste NOYE. `mesure_O.fente` le rend en degres de spirale
# caches -- 6 / 13 / 30 / 34 selon le master, contre 3 / 7 / 22 / 25 avant.
# C'est ce que le douzieme tour a paye sans le voir : M7 obtenait un bel angle
# en noyant 119 degres du geste, et la table lisait ce gain comme du blanc.
# A 1,00 le bras devient un croissant dans les gras, 83 degres noyes sur 210 ;
# 0,45 en laisse 34 au pire.
#
# CE QUE L'ETAT RETENU MESURE, sur les quatre masters romains, ExtraLight a
# ExtraBold : base 48 / 72 / 104 / 106 unites ; coin blanc 41 / 36 / 30 / 29
# degres ; aiguille 28 / 33 / 42 / 44 unites ; saillie 0,0 partout ; jour au
# bout 107 / 90 / 63 / 59, pour un seuil de 24 ; une tache et une contreforme
# aux deux resolutions. `check_O.py` remesure tout cela et sait signaler.
#
#     LE 52 DU QUINZIEME TOUR N'ETAIT PAS UN SEUIL, et la ligne ci-dessus le
#     redisait : c'etait le MINIMUM OBSERVE du jour au bout sur l'etat d'alors.
#     Le seuil du projet est 24, pose au dix-huitieme tour. L'etat retenu est
#     au-dessus des deux.
#
# `enfoui` SUIT `ep_facteur` ET NE SE LIT PAS SEUL : la racine reste dans la
# paroi tant que `enfoui >= ep_facteur / 2`, relation sans dimension donc vraie
# dans les quatre masters. Les deux tables bougent ensemble ou pas du tout.
O_TITRAGE = ("ancre", dict(phi=30.0, longueur=210.0, sens=+1,
                           enfoui={"ExtraLight": 0.45, "Regular": 0.40,
                                   "Bold": 0.35, "ExtraBold": 0.35},
                           r_fin=0.20,
                           ep_facteur={"ExtraLight": 0.85, "Regular": 0.75,
                                       "Bold": 0.62, "ExtraBold": 0.58},
                           effile=0.55, pointe=0.05, courbe=0.45))

#: Le reglage du quinzieme tour, garde pour memoire de ce qui a ete vu et
#: jamais comme un reglage. Il vit ici parce que trois planches historiques le
#: composent encore, et parce qu'un chiffre de la passation s'y rapporte.
O_TITRAGE_QUINZIEME = ("ancre", dict(phi=30.0, longueur=210.0, sens=+1,
                                     enfoui=0.35, r_fin=0.20, ep_facteur=0.55,
                                     effile=0.55, pointe=0.05, courbe=0.35))


#: LES QUATRE MASTERS ITALIQUES N'ONT PAS DE BRAS, et c'est une DECISION de
#: Nicolas, prise au quarante-septieme tour apres l'ecriture du reglage romain.
#: Elle vit ici pour que `reglage_O` puisse la dire : sans cette liste, la
#: levee sur un master italique se lirait comme une valeur manquante, donc
#: comme un trou a combler, alors que c'est un arbitrage rendu. C'est la
#: distinction que ce projet a payee plusieurs fois -- un glyphe decide et un
#: glyphe jamais regarde sont identiques dans une table, tous deux absents.
#:
#: Consequence pour le branchement, point ouvert 84 : la chaine ne pose le
#: bras que sur `Temoin.glyphs`, jamais sur `Temoin-Italic.glyphs`, et le O
#: italique reste celui d'Atkinson.
MASTERS_SANS_BRAS = frozenset({"ExtraLight Italic", "Italic", "Bold Italic",
                               "ExtraBold Italic"})


def reglage_O(master, genre_et_reglage=None):
    """(genre, reglage) avec les valeurs du master RESOLUES.

    `O_TITRAGE` porte depuis le quarante-septieme tour deux champs par master.
    Toute fonction qui dessine ou qui mesure le bras doit passer par ici, et
    `mesure_O.famille_O` LEVE si elle recoit un dict non resolu : un reglage
    par master pris pour un scalaire ne rendrait pas une forme approchee, il
    rendrait n'importe quoi, et une planche en rendrait l'image sans erreur.

    LEVE quand le master manque, comme `lot2.valeur_master`, et ne retombe pas
    sur une valeur par defaut.
    """
    if master in MASTERS_SANS_BRAS:
        raise ValueError(
            f"le master {master!r} ne porte PAS le bras du O, et c'est une "
            f"decision de Nicolas au quarante-septieme tour, pas une valeur "
            f"manquante. Les O italiques restent ceux d'Atkinson.")
    genre, r = genre_et_reglage or O_TITRAGE
    out = {}
    for cle, val in r.items():
        if isinstance(val, dict):
            if master not in val:
                raise ValueError(
                    f"O_TITRAGE[{cle!r}] : aucune valeur pour le master "
                    f"{master!r} (la table en porte {sorted(val)})")
            out[cle] = val[master]
        else:
            out[cle] = val
    return genre, out

# Le o bas de casse de titrage, arrete par Nicolas au seizieme tour. Meme
# construction, meme angle, un seul reglage different : `ep_facteur`, 0,30 au
# lieu de 0,55.
#
# Pourquoi la recopie echoue. La paroi du o fait presque la meme epaisseur
# absolue que celle du O, 155 unites contre 168 au Bold, mais sa contreforme
# est bien plus petite : rayon interieur 108 contre 179, 99 contre 168 en
# ExtraBold. Rapporte au rayon exterieur, le o est donc bien plus epais de
# paroi, 0,59 contre 0,48 au Bold. `ep_facteur` 0,55 y met un bras qui prend
# 39 % du diametre de la contreforme, la ou celui du O en prend 26, et le o
# rendrait 0,713 de son blanc au Bold quand le O en rend 0,798.
#
# Ce que la mesure donnait, et ce que Nicolas a tranche. Deux criteres
# independants pointaient 0,37 : la part de contreforme que le geste coute,
# lue par rasterisation, et la part que le bras prend dans la contreforme, qui
# ne regarde aucun pixel et se lit sur deux rayons. Les deux egalisent le o au
# O. Nicolas a retenu 0,30, plus maigre d'un cran, sur l'argument qu'aucun des
# deux criteres ne pouvait faire : ils tiennent le O pour reference, donc ils
# demandent tous les deux comment donner au o le geste du O, et aucun ne
# demande si le o doit etre tenu au standard du O. Une lettre plus petite
# demande proportionnellement plus de contreforme a la meme graisse.
#
# Ne pas relire ce 0,30 comme une erreur de recopie de 0,37 : les deux
# valeurs ont ete dessinees, mesurees et vues cote a cote dans le mot
# `protocole`, sur `temoin/planche-lot4q-o.png`.
#
# `courbe` 0,35 et `r_fin` 0,20 se recopient du O, et c'est verifie sur le
# reglage retenu et non sur un voisin. Mesure a `ep_facteur` 0,30, en
# ExtraBold : `courbe` 0,5 referme le coin blanc a 26,8 degres et `r_fin` 0,28
# a 31,1, quand les valeurs du O le tiennent a 37,2. Dans l'autre sens `r_fin`
# 0,14 ouvre le coin a 40,3 mais ramene le jour au bout de 39 a 31 unites,
# donc plus pres du seuil de 24 sans le franchir.
#
# Une precision de methode. Ces trois essais avaient d'abord ete mesures a
# `ep_facteur` 0,37, la valeur que les criteres donnaient, et les chiffres
# n'etaient pas les memes : `r_fin` 0,14 y faisait tomber le jour au bout a 26
# unites, contre 31 ici. Un voisin mesure autour d'un reglage ecarte ne dit
# rien du reglage retenu.
#
# Verifie sur les quatre masters romains, seizieme tour : contreforme 0,960 /
# 0,928 / 0,839 / 0,812, soit jusqu'a 0,042 de blanc de plus que le O, saillie
# 0,0 partout, jour au bout jamais sous 39 unites, une tache et une
# contreforme aux deux resolutions, aucun contact dans protocole, oxa, Oo.
# ECARTE PAR NICOLAS AU DIX-NEUVIEME TOUR. Le o bas de casse garde la forme
# d'Atkinson, sans bras. Ce reglage est conserve pour memoire de ce qui a ete
# explore, jamais pour etre relu comme un reglage — meme traitement que
# FAMILLES_O_ECARTEES. Le seizieme tour l'avait arrete et verifie sur les
# quatre masters, et les mesures ci-dessus restent justes : c'est la decision
# qui a change, pas les chiffres.
#
# Aucun script ne doit le lire pour dessiner. Ceux qui le lisaient au moment de
# la decision : `planche_lot4q_o.py`, qui est la planche du seizieme tour et
# garde son objet historique, et `mesure_garde_fou.py`, qui compare des etats.
# `specimen_corpus.py` ne le lit plus.
o_ECARTE = ("ancre", dict(O_TITRAGE[1], ep_facteur=0.30))

# Nom conserve le temps que les planches historiques du seizieme tour tournent
# encore. Ne pas s'en servir pour un nouveau dessin.
o_TITRAGE = o_ECARTE

# Les trois autres familles du quatrieme tour, gardees pour memoire de ce qui a
# ete explore et ecarte, jamais pour etre relues comme un reglage. Leurs
# chiffres ont diverge des tableaux de la passation, c'est documente, et le
# douzieme tour a perdu du temps a repartir de la. Le point commun des quatre :
# aucune ne traverse la paroi de l'anneau, la traversee etant le seul defaut du
# bras que la mesure ne voyait pas et que l'image montre.
FAMILLES_O_ECARTEES = {
    "A. contre-poincon spirale": ("contre", dict(phi=145.0, mince=0.55,
                                                epais=1.45)),
    "B. anneau a joint": ("anneau", dict(phi=145.0, mince=0.62, epais=1.38)),
    "D. queue exterieure": ("meche", dict(phi=100.0, longueur=118.0, sens=+1,
                                          ecart=118.0, montee=1.6, effile=0.8,
                                          ep_facteur=0.70)),
}


# LA TROISIEME FAMILLE DES CHIFFRES, ET LE O. Point ouvert 83, ecrite au
# quarante-septieme tour.
#
# POURQUOI ELLE EXISTE. Ces six glyphes n'ont AUCUNE terminaison posee sur un
# alignement, donc ni `loc_alignement` ni le filtre de l'etendue ne les voit :
# ils ne sont ni dans le perimetre, ni dans `HORS_TITRAGE`, et rien ne les
# distingue d'un glyphe que personne n'a regarde. Trois d'entre eux ont
# pourtant ete tranches par Nicolas au quarante-sixieme tour.
#
# POURQUOI PAS DANS `HORS_TITRAGE`, ET LES SIX NE FONT PAS BLOC. Cette
# liste-la est verifiee par les sections 1 et 2 de `check_perimetre` contre la
# source AMONT : un nom qu'aucun GESTE n'attrape y est signale comme inutile.
# Mesure au quarante-septieme tour, `attrapes_par_le_geste` sur les deux
# sources : le 3 et le 5 SONT attrapes, par un bout du haut que le regime
# `aucune` epargne -- ils sont donc a leur place dans `HORS_TITRAGE`, ou la
# planche du trente-quatrieme tour les a mis. Le zero, le 6, le 8 et le O ne
# le sont dans aucune source : les y ecrire remplirait en silence la section
# qui existe pour dire qu'un nom y est de trop, sans incrementer le total.
#
# UN PREMIER JET DE CE COMMENTAIRE ANNONCAIT LES SIX D'UN BLOC, et c'est la
# section 14 qui l'a corrige avant qu'il ne soit lu. Une famille de decision
# n'est pas une famille de mecanisme.
#
# CE QUE `etat` VEUT DIRE. "ecarte" est une decision de Nicolas, "chantier" un
# nom retenu que personne n'a encore dessine. `creux` est le nombre de
# contreformes attendu dans les quatre masters romains : c'est le FAIT sur
# lequel la decision a ete prise, et la section 14 de `check_perimetre` le
# remesure. Une raison ecrite sans son fait vieillit sans que rien ne le dise.
FORMES_FERMEES = {
    # Un seul contour dans les quatre masters romains, a l'amont comme a
    # l'etat servi : aucune contreforme, donc aucun anneau ou ancrer un bras.
    # Ils restent plats, au meme titre que le 2 et le 1 tabulaire, et leur
    # presence dans `HORS_TITRAGE` tient a la planche du trente-quatrieme
    # tour, qui est une AUTRE raison -- ne pas lire l'une pour l'autre.
    "three": dict(etat="ecarte", creux=0,
                  raison="aucune contreforme, donc pas d'anneau"),
    "five": dict(etat="ecarte", creux=0,
                 raison="aucune contreforme, donc pas d'anneau"),
    # DECISION DE NICOLAS, PRISE SUR LA MESURE ET SANS PLANCHE, quarante-
    # sixieme tour : le zero garde sa barre contextuelle du lot 1, SEULE. Un
    # bras cumulerait deux signes dans le meme blanc.
    #
    # ET LA RAISON N'EST PAS L'ABSENCE D'ANNEAU, contrairement au 3 et au 5 :
    # `zero` barre a deux demi-contreformes d'aires voisines, ou `rayons` en
    # retient une au hasard de l'aire, mais `zero.slashless` -- le glyphe que
    # le lot 1 recoud et que les nombres servent reellement -- a UNE
    # contreforme entiere, mesuree dans les quatre masters de `Temoin.glyphs`.
    # Il a donc un anneau libre. Ecrit ici pour que la decision ne se relise
    # pas comme une impossibilite geometrique : c'est un arbitrage de signe,
    # un seul par blanc, et il tient quel que soit l'etat du glyphe.
    "zero": dict(etat="ecarte", creux=2,
                 raison="garde sa barre contextuelle du lot 1, seule"),
    # LES TROIS QUI RESTENT. Ils ont un anneau lisible, et c'est tout ce qui
    # est acquis : le localisateur qui le trouve n'est pas ecrit.
    #
    # CE QUE LE QUARANTE-SEPTIEME TOUR A MESURE ET QUI CADRE LE CHANTIER, sur
    # les quatre masters romains de l'amont :
    #   - le centre se prend sur la CONTREFORME, pas sur la boite des deux
    #     plus grands contours. L'ecart vaut 114 a 122 unites sur le 6 et 128
    #     a 149 sur le 8, et c'est lui qui faisait lever `rayons`.
    #   - un anneau ne se lit pas sur 360 degres. Le col du 6 et la taille du
    #     8 n'ont pas de paroi, quelle que soit la regle de lecture. Le
    #     secteur sain contient phi=30, l'angle du reglage du O.
    #   - LES NEUF PARAMETRES DE `O_TITRAGE` NE SE RECOPIENT PAS. A
    #     `ep_facteur` 0,55 le bras prend 0,236 du diametre de contreforme sur
    #     le O au Bold, 0,376 sur le 6, 0,355 sur l'anneau bas du 8 et 0,500
    #     sur son anneau haut ; a l'ExtraBold, 0,272 / 0,430 / 0,418 / 0,605.
    #     C'est le fait qui a fait ecarter le o bas de casse au dix-neuvieme
    #     tour, a 0,39 contre 0,26, et il est ici plus grand.
    # DECISION DE NICOLAS, QUARANTE-HUITIEME TOUR : NI LE 6 NI LE 8 NE PORTENT
    # LE BRAS, et le 8 a ete tranche en premier, anneau par anneau, avant que
    # la question ne se pose pour le 6. Aucun chiffre n'en porte donc, et la
    # troisieme famille se reduit au O seul.
    #
    # LA RAISON N'EST PAS GEOMETRIQUE, ET IL FAUT QUE CELA RESTE LISIBLE. Le
    # tour precedent a mesure le contraire de ce qu'une lecture pressee
    # supposerait : les deux ont un anneau qui se lit, leur secteur sain
    # contient phi=30, l'angle du reglage du O, et le centre pris sur la
    # contreforme supprime toutes les levees de `rayons`. Le localisateur
    # d'anneau etait donc faisable, et il n'a pas ete ecrit parce que le
    # dessin n'est pas demande -- pas parce qu'il etait impossible. C'est
    # exactement la forme de la decision sur le zero au quarante-sixieme tour,
    # et le projet a deja paye qu'une raison ecrite de travers se relit des
    # tours plus tard comme un fait etabli.
    #
    # CE QUE LA DECISION LAISSE OUVERT, ET QUI EST MESURE : `five/six` vaut
    # 0,120 a l'ExtraBold, la paire la plus serree du repertoire servi. Elle
    # ne se refermera par aucun des deux cotes.
    "six": dict(etat="ecarte", creux=1,
                raison="arbitrage de Nicolas au quarante-huitieme tour ; "
                       "l'anneau se lit, le bras n'est pas voulu"),
    "eight": dict(etat="ecarte", creux=2,
                  raison="arbitrage de Nicolas au quarante-huitieme tour, "
                         "aucun de ses deux anneaux ne porte le bras"),
    # SERVI ET VALIDE EN NAVIGATEUR au quarante-huitieme tour, sur
    # `gabarits/bras-O.html` et contre un Temoin sans bras compile dans la
    # meme session : le O a 18 px aux quatre masters, le groupe confusable
    # O 0 Q C G, et le sigle en petites capitales sans bras a cote du sigle en
    # capitales pleines qui en porte un. Points ouverts 70 et 84 fermes. Le bras
    # est greffe par `bras_O.appliquer`, appele par `make_temoin` APRES le lot
    # 3 et sur la seule source romaine. Le fait sous cet etat -- le glyphe
    # porte un contour de plus que son amont -- est remesure par le volet D de
    # la section 14 de `check_perimetre` ; sa FORME, noeud a noeud contre le
    # reglage, par la section 5 de `check_O`.
    "O": dict(etat="servi", creux=1,
              raison="bras greffe dans la contreforme, quatre masters romains"),
}

#: Les trois etats qu'une fiche de `FORMES_FERMEES` peut porter. Ecrits ici
#: pour que la section 14 puisse refuser un etat inconnu : une faute de frappe
#: sur "ecarte" passerait sinon tous les volets sans rien declencher, et une
#: etiquette est une mesure.
ETATS_FORMES_FERMEES = ("ecarte", "chantier", "servi")


# Les terminaisons que le lot 2 ne pouvait pas toucher, glyphe par glyphe.
# `hauteurs` est resolu master par master depuis les metriques.
ETENDU = {
    "X": ("base", "cap"), "A": ("base", "cap"), "V": ("base", "cap"),
    "W": ("base", "cap"), "Y": ("base", "cap"), "M": ("base", "cap"),
    "N": ("base", "cap"), "U": ("cap",), "K": ("base", "cap"),
    "H": ("base", "cap"), "I": ("base", "cap"),
    "n": ("base",), "m": ("base",), "r": ("base", "xh"), "u": ("base", "xh"),
    "v": ("base", "xh"), "w": ("base", "xh"), "x": ("base", "xh"),
    "h": ("base",), "b": ("base",), "d": ("base",),
    # Le p a ete retire : verifie sur les quatre masters, il n'a aucune
    # terminaison posee sur la ligne de base. Sa jambe se termine sur la
    # descendante, comme celles du q, du y, du j et du g. Ce quatrieme
    # alignement n'est pas encore traite.
}

# La coupe rentrante coute l'assise. Mesure a la bande de 24 unites, au Bold :
# l'appui percu du n tombe a 26 % de sa valeur d'origine, celui du I a 15 %,
# celui du X a 20 %. La coupe sortante, elle, rend le dessus intact et
# quadruple le dessous, donc l'appui remonte a 145 %. C'est le mecanisme du
# debord optique des rondes : une lettre dont la matiere descend sous la ligne
# parait posee. Voir mesure4.appui.
#
# Consequence : sur une terminaison posee sur la ligne de base, la sortante
# n'est pas un ornement, c'est la reparation d'un defaut que la rentrante
# introduit.
DEPASSEMENT = 32.0

# Les capitales descendent plus bas que les bas de casse. Choix de Nicolas au
# neuvieme tour, apres avoir vu 32 et 60 cote a cote : 44 unites, soit 32 plus
# le debord optique des rondes. La raison de les separer est de proportion, une
# capitale fait 668 quand une hauteur d'x en fait 496, et non de securite : le
# cout en approche d'une descente plus profonde est nul sur tout pied vertical,
# puisque le coin descend tout droit. Seules les deux diagonales paient, et
# elles ont leurs propres entrees.
DEPASSEMENT_CAP = 44.0


def depassement_pour(nom):
    """Le depassement effectif d'un glyphe, avant sa prescription propre.

    Une prescription qui porte `depassement` gagne toujours : le A est a 60 par
    decision explicite, pas par la regle de casse.
    """
    pr = PRESCRIPTIONS.get(nom, {})
    if "depassement" in pr:
        return pr["depassement"]
    return DEPASSEMENT_CAP if nom[:1].isupper() else DEPASSEMENT

# La coupe sortante est le reglage general : Nicolas la prefere, et la mesure
# d'appui dit pourquoi elle est aussi la plus sure. 32 unites, soit deux fois
# et demie le debord optique des rondes.
#
# En bas seulement. L'argument d'appui ne vaut que pour la ligne de base : en
# haut il n'y a pas d'assise a perdre, donc la sortante y serait un ornement
# pur, et elle coute. Mesure au Bold, sortante appliquee a la ligne de
# capitale : la boite s'elargit de 54 unites sur le Y, 29 sur le V, 20 sur le
# W, 16 sur le K, et l'approche droite du Y passe de 0 a -20 unites, celle du
# K de 10 a -6. La raison est geometrique : le coin sortant coulisse le long
# du flanc voisin prolonge, et sur un bras diagonal peu pentu il part surtout
# de cote. Sur un flanc vertical il monte tout droit, et l'elargissement
# mesure vaut exactement 0.
#
# D'ou le partage retenu par Nicolas : la sortante monte la ou le flanc est
# vertical, H I N U, et nulle part ailleurs en haut. Ce sont des entrees
# explicites de PRESCRIPTIONS, pas une regle qui devinerait la pente : le lot 2
# a montre qu'un test generique se paie plus cher qu'un choix ecrit et verifie.
# `rentrantes` est tranche par Nicolas au trente-cinquieme tour, sur la planche
# `planche-propagation-1-haut.png` : le titrage ne coupe qu'en BAS, et un haut
# se prescrit glyphe par glyphe quand il est voulu. La raison est celle que ce
# fichier ecrit deja pour la sortante -- en haut il n'y a pas d'assise a
# perdre, donc le geste y est un ornement pur et il coute -- et la mesure du
# trente-cinquieme tour la chiffre : la rentrante du haut, restee a l'angle
# constant du lot 2, descend jusqu'a 6,17 fois le depassement demande au
# romain et 6,91 en italique, parce que sa profondeur vaut longueur de segment
# x tan(theta) et que la barre s'epaissit avec la graisse. Le point ouvert 63
# attribuait ce regime a la sortante ; la sortante, elle, tient sa promesse a
# 1,00x sur les 48 glyphes et les huit masters.
DEFAUT = dict(exclure=set(), cote="antihoraire", theta=20.0, sortantes="bas",
              rentrantes="aucune")

# Prescriptions tranchees par Nicolas, planche apres planche. Elles derogent au
# reglage general, chacune pour une raison ecrite.
# `exclure` liste les quadrants qui restent plats, `sortantes` ceux qui sortent
# de leur alignement, `pointes` impose de quel cote la pointe descend.
PRESCRIPTIONS = {
    # X et x : un seul bout sortant, en bas a gauche, pointe a gauche. Les
    # trois autres restent poses a plat sur leur ligne. C'est la prescription la
    # plus econome du jeu : elle donne une signature a une lettre tres visible
    # sans toucher a sa symetrie de rotation ailleurs.
    "X": dict(exclure={"bd", "hg", "hd"}, cote="antihoraire", theta=20.0,
              sortantes={"bg"}, pointes={"bg": "gauche"}),
    "x": dict(exclure={"bd", "hg", "hd"}, cote="antihoraire", theta=20.0,
              sortantes={"bg"}, pointes={"bg": "gauche"}),
    # A : le bas gauche reste plat, le bas droit sort, et le sommet reste
    # droit. Le repli du sommet, garde du texte, est abandonne ici.
    #
    # Le A n'a plus de profondeur propre. Il en a eu une, 60 unites, tant que
    # les capitales sortaient a 32 : c'etait un exces voulu sur une lettre de
    # signature, et la mesure ne l'a jamais soutenu — a 32 son encre sous ligne
    # valait deja 95 a 106 % du pied du fut du N, et son profil d'encre
    # s'eteignait a la meme profondeur. Les capitales passees a 44, l'ecart
    # tombait de 28 a 16 unites, et Nicolas l'a supprime : le A prend la
    # profondeur de casse comme les autres.
    "A": dict(exclure={"bg", "hc"}, cote="horaire", theta=20.0,
              sortantes={"bd"}),
    # L'ARING RECOIT LE REGLAGE DU A, dont il dessine la lettre. Trente-neuvieme
    # tour, trouve en instruisant l'AE et non designe par Nicolas : sans cette
    # entree il prenait le reglage general et ses DEUX pieds plongeaient, bg et
    # bd, quand le A n'en accepte qu'un. Meme cause que l'AE -- une prescription
    # indexee par nom ne suit pas une composition -- et meme remede.
    #
    # LE QUADRANT EST VERIFIE STABLE DANS LES HUIT MASTERS avant d'etre nomme :
    # bg va de 56 a 190 u et bd de 54 a 186, sans jamais permuter. `quadrant`
    # desincline par l'italicAngle depuis le trente-septieme tour, mais cela se
    # verifie plutot que se suppose -- c'est ce que le point 65 a coute.
    #
    # L'ENTREE LEVE DEUX DEFAUTS QUE LE REGLAGE GENERAL CREAIT, et les deux
    # sont mesures APRES ecriture et non deduits avant :
    #   - la SATURATION disparait. Sous le reglage general, `cote="antihoraire"`
    #     portait le bd a 45,0 degres en ExtraLight romain -- la borne -- et a
    #     43,0 en ExtraLight Italic, donc il sortait court. Sous `horaire`, le
    #     coin vise change et l'angle tombe a 30,9 et 35,7 : la cible est
    #     atteinte dans les huit masters.
    #   - le DEBORD LATERAL disparait. Le coin partait de +14,7 a +15,7 u vers
    #     la droite au romain et +5,4 a +6,8 en italique ; il est a +0,0 u
    #     partout, donc la boite ne bouge plus.
    # Un premier jet de ce commentaire annoncait la saturation comme une limite
    # connue, ce qui etait vrai de l'etat d'AVANT : une note prise sur l'etat
    # anterieur devient fausse a l'instant ou la table est ecrite.
    "Aring": dict(exclure={"bg", "hc"}, cote="horaire", theta=20.0,
                  sortantes={"bd"}),
    # M : seul le pied gauche sort. Le milieu et le pied droit restent plats,
    # ni sortants ni rentrants : la coupe rentrante leur enlevait leur assise
    # sans rien apporter, et l'appui du M tombait a 67 % avec 76 % de son poids
    # sur le seul tiers gauche. A plat, ils gardent leur contact d'origine et
    # c'est le pied gauche seul qui porte la signature.
    "M": dict(exclure={"bc", "bd", "hg", "hd"}, cote="antihoraire", theta=20.0,
              sortantes={"bg"}),
    # --- Le N, CINQUANTE-TROISIEME TOUR : LA SORTANTE DU BAS EST RETIREE.
    # Demande de Nicolas au cinquante-deuxieme tour, EN NAVIGATEUR, sur la
    # section 1 de `tour51.html` -- les treize sigles dans leurs phrases
    # reelles, en texte a 18 px, et non sur une planche. Le N garde sa sortante
    # en HAUT A DROITE et perd celle du BAS A GAUCHE, capitales et petites
    # capitales.
    #
    # ETAT ANTERIEUR, garde parce que le fait de geometrie reste vrai : le N a
    # ses deux seuls bouts de fut sortants des deux cotes, `sortantes={"bg",
    # "hd"}`, et ils sont en symetrie de rotation exacte, donc le geste comptait
    # double. C'est cette symetrie que la demande casse, et elle la casse du
    # cote ou elle se lit -- le bas d'une ligne de texte.
    #
    # IL RECOIT LA PRESCRIPTION DU K, mot pour mot, `sortantes={"hd"}` avec
    # `exclure={"bd","hg"}` conserve, ecrite au quarante-troisieme tour pour la
    # meme cause : une forme qu'un texte courant a fait rejuger.
    #
    # LE H PORTE LA MEME ENTREE CARACTERE POUR CARACTERE, ET IL RESTE TEL QUEL.
    # C'EST UNE DECISION DE NICOLAS, prise au meme regard et en connaissance du
    # fait qui la fragilise : AUCUN des treize sigles de la section 1 ne
    # contient de H, donc il n'a pas pu comparer les deux lettres cote a cote.
    # Sa prescription est plus bas dans cette table et elle n'a pas bouge.
    #
    # LE PRIX EST ECRIT, comme celui du K et celui du U. Le M plonge encore par
    # son pied gauche, le P et le F par le reglage general : le N devient la
    # TROISIEME irregularite de cette famille de capitales a fut, apres le K au
    # quarante-troisieme tour et le U au quarante-neuvieme.
    #
    # CETTE LIGNE NE SUFFIT PAS, ET C'EST LA MESURE QUI L'A DIT. Ecrite seule,
    # elle laisse le N a -24,0 et non a plat : son pied portait DEUX gestes, et
    # la demande n'en nommait qu'un. Mesure en ordonnees absolues sur les huit
    # masters des deux sources -- c'est la lecon du point 69, ou deux gestes
    # opposes s'annulaient sans qu'aucun deplacement le dise :
    #
    #     Atkinson         N et H   ymin    0,0   ymax  668,0
    #     servi            N et H   ymin  -44,0   ymax  712,0
    #     cette ligne      N        ymin  -24,0   ymax  712,0  (-23,5 italique)
    #     + retrait lot 2  N        ymin    0,0   ymax  712,0
    #     H, inchange               ymin  -44,0   ymax  712,0
    #     K, dans tous les etats    ymin    0,0
    #
    # LA SECONDE MOITIE DU GESTE VIT DANS `lot2.LOT2`, et la raison y est
    # ecrite : le N et le H y portent deux entrees depuis le lot 4a du
    # vingt-huitieme tour, `loc_sommet_droit` a 24,0 et `loc_pied_gauche` a
    # 24,0, un geste de TEXTE que la sortante de titrage portait ensuite a 44.
    # Le pied du N sort de cette table au meme tour ; son SOMMET y reste, et sa
    # sortante `hd` reste ici. Le K n'a jamais eu d'entree de pied dans
    # `lot2.LOT2`, et c'est pour cela que la meme prescription le rend plat.
    # DEUX TABLES BOUGENT DANS LE MEME GESTE, dans deux fichiers cette fois.
    #
    # AUCUNE ENTREE SEPAREE POUR `n.sc`, et ce n'est pas un oubli : le lot 3
    # derive les petites capitales APRES `add_fusion`, donc `n.sc` suit son
    # capitale au rapport 574/668 comme elle suit tout le reste. Verifie et non
    # suppose, le compte tombant a chaque etat : -37,8 servi, -20,6 avec cette
    # ligne seule, 0,0 apres le retrait du lot 2.
    "N": dict(exclure={"bd", "hg"}, cote="antihoraire", theta=20.0,
              sortantes={"hd"}),
    # --- Le v et le w, QUARANTE-TROISIEME TOUR : LA SORTANTE DU HAUT EST
    # RETIREE. Point ouvert 75, arbitre par Nicolas au quarante-deuxieme tour
    # en navigateur, sur le dessin fusionne servi.
    #
    # ILS SORTAIENT PAR LE HAUT DEPUIS LE NEUVIEME TOUR, `sortantes={"hg","hd"}`
    # -- les deux seules minuscules dans ce cas, et le seul endroit du projet
    # ou une sortante monte sur une lettre de bas de casse. Le choix se
    # justifiait alors : le titrage etait un REGISTRE SEPARE, donc un ornement
    # qui ne se lisait qu'en grand. La fusion du quarantieme tour l'a verse
    # dans le texte, et rien ne l'a re-soumis au jugement. C'est la meme cause
    # que le i au quarante-et-unieme tour et que le h et le k ci-dessous : une
    # forme arbitree pour un registre separe devient une forme de texte, et le
    # projet n'a aucune liste de ce qui reste a rejuger apres la fusion.
    #
    # MESURE AVANT ECRITURE, les huit masters, romain et italique identiques :
    # Atkinson pose le v et le w a plat a 496,0, la hauteur d'x ; Temoin les
    # met a 528,0. A 18 px, 496 unites font 8,93 pixels et 528 en font 9,50 :
    # le v franchit la rangee de pixels que toutes ses voisines partagent, et
    # l'arrondi rend ENTIER un ecart qui vaut 0,57 pixel. C'est pourquoi le
    # defaut se voit en texte courant et pas sur une planche d'alphabet.
    #
    # LE V ET LE W CAPITALES NE BOUGENT PAS. Leur montee de 44 unites au-dessus
    # de la ligne de capitale est arbitree au onzieme tour et n'est pas
    # contestee : une capitale qui depasse la ligne de capitale ne franchit
    # aucune rangee partagee avec ses voisines de bas de casse.
    #
    # `exclure` EST CONSERVE, ET CE N'EST PAS DE L'INERTIE. Les treize
    # derogations du bas n'ecrivent que `sortantes=()`, parce qu'un jeu de
    # quadrants pourrait s'appliquer a une source et pas a l'autre. Ici le
    # quadrant sert a autre chose : sans `exclure={"bc"}`, la section 8 de
    # `check_perimetre`, qui rejoue chaque glyphe avec `bas="bas"` force,
    # trouverait une sortante possible sur le sommet bas du v et le classerait
    # "ecarte sans derogation attendue". Le v et le w n'ont pas de derogation
    # du BAS a declarer : leur bas n'a jamais rien recu. `exclure` garde donc
    # la propriete qui les range dans `jamais`, et c'est la SECTION 13, neuve
    # au meme tour, qui surveille leur haut.
    "v": dict(exclure={"bc"}, cote="antihoraire", theta=20.0,
              sortantes=()),
    "w": dict(exclure={"bc", "bg", "bd", "hc"}, cote="antihoraire", theta=20.0,
              sortantes=()),

    # ---- la passe V W Y K, onzieme tour ----
    #
    # Ces quatre-la etaient restees au reglage general, tout le bas sortant et
    # tout le haut rentrant, ce qui laissait deux choses bancales : le V et le
    # W faisaient l'inverse de leurs bas de casse, et le K portait sa sortie sur
    # un bras diagonal alors que ses deux flancs verticaux ne servaient a rien.
    #
    # V et W : exactement le geste du v et du w. Les sommets bas restent plats,
    # les deux sommets hauts exterieurs sortent. Cout mesure au Bold, approches
    # avant et apres : V 28/10 -> 10/-5, W 28/15 -> 15/4. Le sommet du milieu
    # du W reste plat, comme celui du w.
    "V": dict(exclure={"bc"}, cote="antihoraire", theta=20.0,
              sortantes={"hg", "hd"}),
    "W": dict(exclure={"bg", "bd", "hc"}, cote="antihoraire", theta=20.0,
              sortantes={"hg", "hd"}),

    # Y : le pied sort, sur son fut vertical, et les deux bras du haut restent
    # poses a plat. C'est le seul des trois etats ou la lettre reste dans sa
    # chasse : les faire sortir amenait l'approche droite a -28, la pire valeur
    # des douze mesurees au tour.
    #
    # `pointes` AJOUTE AU TRENTE-HUITIEME TOUR, point ouvert 69 : le pied du Y
    # est le seul bout du glyphe ou le geste de texte et celui de titrage se
    # rencontrent, et ils visaient des coins OPPOSES. Le lot 3 fait descendre
    # le coin droit a -44 depuis le vingt-septieme tour ; le titrage descendait
    # le gauche a -44, donc le pied finissait PLAT, parallele a la ligne de
    # base et 44 unites plus bas, et la pointe du lot 3 disparaissait. Le
    # depassement obtenu valait 44 des deux cotes, donc aucun chiffre ne
    # pouvait le dire : ce sont les ORDONNEES ABSOLUES qui l'ont montre, et
    # Nicolas a tranche sur `planche-point69.png`.
    #
    # CE QUE CETTE LIGNE FAIT, MESURE SUR LES HUIT MASTERS : au romain, RIEN.
    # Le texte livre deja les 44 unites demandees, donc le Y romain ne recoit
    # plus aucun geste de titrage et rejoint les glyphes du perimetre que rien
    # ne deplace. En italique elle comble le deficit d'une unite, -43 a -44,
    # dans l'Italic, le Bold Italic et l'ExtraBold Italic. L'ExtraLight Italic
    # ne bouge pas : son pied est tourne de 42,6 degres par le lot 3, au-dela
    # des 38,7 de PENTE_BAS, et c'est la limite connue du point 66.
    "Y": dict(exclure={"hg", "hd"}, cote="antihoraire", theta=20.0,
              sortantes={"bc"}, pointes={"bc": "droite"}),

    # K : LE HAUT SEUL DEPUIS LE QUARANTE-TROISIEME TOUR. Il portait `bg` et
    # `hd`, en symetrie de rotation comme le H et le N ; le `bg` est retire.
    # Point ouvert 77, arbitre par Nicolas au quarante-deuxieme tour en
    # navigateur, en meme temps que le k bas de casse et pour la meme raison de
    # fond -- une forme du titrage devenue forme de texte par la fusion.
    #
    # LE PRIX EST CONNU ET IL A ETE PRIS EN CONNAISSANCE DE CAUSE. Le K est
    # REGULIER dans le regime du bas : il plonge une seule fois, par le coin
    # exterieur de son fut, a -44, exactement comme le H, le N, le M, le P et
    # le F. Le mettre a plat en fait LA SEULE CAPITALE A FUT SANS PLONGEE du
    # repertoire. Ce n'est donc pas la correction d'une anomalie, comme sur le
    # k et le h, c'est un choix de dessin qui en cree une -- et Nicolas l'a
    # tranche apres l'avoir vu ecrit.
    #
    # SA MONTEE DE 44 EN HAUT SURVIT, et c'est la moitie de l'entree qui ne
    # change pas. `hd` reste dans `sortantes` ; mesure a l'amont romain avant
    # ecriture, le K sortait bg=44,0 et hd=44,0, il doit sortir hd=44,0 seul.
    # Le geste du haut est arbitre au onzieme tour et n'est pas conteste.
    #
    # `bg` N'EST PAS AJOUTE A `exclure` : il suffit qu'il quitte `sortantes`
    # pour retomber dans la branche rentrante, que `DEFAUT` laisse a "aucune".
    # Une ligne qui dit la meme chose deux fois finit par n'en dire qu'une.
    "K": dict(exclure={"bd", "hg"}, cote="antihoraire", theta=20.0,
              sortantes={"hd"}),
    # Les trois glyphes dont le haut sort, avec le N ci-dessus. Leur point
    # commun est mesure, pas suppose : le flanc qui porte la terminaison est
    # vertical, donc le coin monte tout droit et la boite ne s'elargit pas
    # d'une unite. Verifie sur les quatre masters romains, quadrants
    # identiques partout (inventaire par quadrant).
    #
    # Le H et le U ont deux bouts de fut chacun, hg et hd, larges comme le fut.
    # Le I n'a pas de bout de fut : sa terminaison haute est sa barre entiere,
    # hc, large de 282 unites en Regular et 344 au Bold. La sortante lui
    # incline donc toute la barre, ce que sa barre basse subit deja par le
    # reglage general. Les deux barres penchent du meme cote.
    #
    # Le H ne sort que par bg et hd, comme le N : deux coins en symetrie de
    # rotation, les deux autres plats. Choix de Nicolas, huitieme tour. Le
    # geste devient alors le meme sur les deux lettres a futs paralleles, et
    # la silhouette du mot garde deux points d'appui francs au lieu de quatre
    # coupes qui se repondent.
    #
    # LE PARAGRAPHE SUR LE I CI-DESSUS DECRIT UN ETAT REVOLU : le I est rendu
    # a Atkinson au quarante-troisieme tour, et sa prescription est plus bas
    # dans cette table, avec les derogations. Ce qu'il en reste de vrai, et qui
    # vaut d'etre garde, c'est le FAIT DE GEOMETRIE : le I n'a pas de bout de
    # fut, donc une sortante y incline une barre entiere. C'est ce fait qui a
    # decide de l'ecarter.
    # LE H RESTE TEL QUEL AU CINQUANTE-TROISIEME TOUR, ALORS QUE LE N CHANGE.
    # C'est une DECISION de Nicolas et non un reste : les deux entrees etaient
    # identiques caractere pour caractere, le N perd sa sortante du bas et le H
    # garde les deux. Le fait qui la fragilise est ecrit a cote du N, avec le
    # prix : aucun des treize sigles de la section 1 de `tour51.html` ne
    # contient de H, donc les deux lettres n'ont pas pu etre comparees cote a
    # cote, et le H reste la seule capitale a fut a sortir des deux cotes.
    "H": dict(exclure={"bd", "hg"}, cote="antihoraire", theta=20.0,
              sortantes={"bg", "hd"}),
    # --- Le I, QUARANTE-TROISIEME TOUR : IL REDEVIENT CELUI D'ATKINSON.
    # LA QUINZIEME DEROGATION. Arbitre par Nicolas en navigateur, sur la
    # section 7 servie, au meme regard que les quatre gestes du tour.
    #
    # Il portait `sortantes={"bc","hc"}` depuis le huitieme tour, et c'est le
    # seul glyphe du projet dont les DEUX BARRES ENTIERES penchent. Le I n'a
    # pas de bout de fut : ses terminaisons SONT ses barres, 282 unites de
    # large au Regular et 344 au Bold, donc la sortante ne coupe pas un bout,
    # elle incline la barre. Mesure au Regular, romain : la barre basse va de
    # (55, -44) a (337, 0) et la haute de (55, 668) a (337, 712), quand
    # Atkinson les pose toutes deux a plat. `sortantes=()` rend exactement les
    # douze noeuds d'Atkinson.
    #
    # LE PROJET AVAIT ECRIT CE GESTE COMME UNE SIGNATURE, ET C'EST LE POINT 63
    # SOUS SA FORME CORRIGEE : le regime de la barre entiere a d'abord ete
    # attribue a la sortante, puis mesure et rendu a la rentrante du haut ; le
    # I est resté le cas ou la sortante fait bel et bien pencher une barre.
    # Nicolas l'avait accepte sur le I en tranchant le perimetre au
    # trente-quatrieme tour -- sur une planche, quand le titrage etait un
    # registre separe. Meme cause que le v, le w, le h, le k et le i : la
    # fusion l'a verse dans le texte, et l'endroit du regard a tranche
    # autrement.
    #
    # CE QUE CETTE ENTREE TOUCHE ET QUI N'EST PAS DANS LE I : `i.sc` SUIT SA
    # CAPITALE depuis la fusion, au rapport 574/668 du lot 3. Il portait donc
    # -37,8 et 611,8, et le quarante-et-unieme tour l'avait ecrit comme une
    # bizarrerie assumee -- un sigle en petites capitales gardait un i
    # descendant quand le i bas de casse etait sorti du titrage. La bizarrerie
    # disparait ici sans avoir ete visee, et c'est la propagation par
    # COMPOSANT jouant pour une fois dans le bon sens.
    #
    # `sortantes=()` ET NON `exclure`, pour la raison des quatorze autres : un
    # jeu de quadrants se lit dans une boite que l'italique fait pencher.
    "I": dict(sortantes=()),            # (55,-44)->(337,0) et (55,668)->(337,712)
    # LE R EST RENDU A ATKINSON, quarante-neuvieme tour, decision de Nicolas
    # en NAVIGATEUR sur `tour49.html`. Il etait au reglage general et VALIDE
    # depuis le trente-neuvieme tour, sur une planche d'alphabet.
    #
    # C'EST LA CINQUIEME VALIDATION DE PLANCHE REVISEE EN TEXTE, apres le i au
    # quarante-et-unieme tour, le k au quarante-troisieme, le 1 au quarante-
    # cinquieme et `idotless`. Une planche pose les lettres en grille, a un
    # corps ou le geste fait cinq pixels et sans voisine ; ce qu'une liste de
    # validés porte, c'est "Nicolas l'a regarde et l'a garde", donc l'endroit
    # du regard compte autant que le regard.
    #
    # TROIS TABLES BOUGENT DANS LE MEME GESTE, et c'est la lecon du k : cette
    # ligne, plus `BRUT_ATTENDU` qui passe de quinze a SEIZE derogations, plus
    # `VALIDES_REGLAGE_GENERAL` qui tombe de dix-sept a SEIZE. Une seule des
    # trois, et un controle dit valide ce qu'un autre dit ecarte, sans
    # qu'aucun echoue.
    #
    # VALIDE PAR NICOLAS EN NAVIGATEUR sur `tour49.html`, sur le binaire servi.
    "R": dict(sortantes=()),
    # LE U, ET LA RESERVE DE NICOLAS SUR LE Û -- LIMITE CONNUE, quarante-
    # neuvieme tour. Le geste n'est PAS en miroir, et c'est mesure au Regular :
    # il fait monter a 712 le bord INTERIEUR de la branche gauche (x=170) et le
    # bord EXTERIEUR de la branche droite (x=614). Le coin qui monte pres du
    # centre est donc celui de gauche, et c'est lui qui vient sous la pointe de
    # l'accent circonflexe.
    #
    # NICOLAS L'A VU SUR LA PLANCHE DU REPERTOIRE ENTIER et a choisi de LE
    # LAISSER TEL QUEL, apres qu'il a ete etabli que le Û est un COMPOSITE PUR
    # du U -- comme les cinq autres U accentues -- donc qu'il ne peut pas
    # porter un geste que le U n'a pas sans etre decompose. Les deux voies
    # etaient : changer le U, et ses six accentuees suivent ; ou decomposer le
    # Û, et tenir deux dessins de U.
    #
    # ECRIT ICI PARCE QU'UNE RESERVE NON ECRITE SE RELIT COMME UNE ABSENCE DE
    # RESERVE. Le U est valide, le Û est valide AVEC cette reserve, et la
    # difference doit rester lisible le jour ou quelqu'un rouvrira le U.
    "U": dict(exclure=set(), cote="antihoraire", theta=20.0,
              sortantes={"hg", "hd"}),
    # LES DEUX FRACTIONS, QUARANTE-NEUVIEME TOUR. Demande de Nicolas sur la
    # planche du repertoire entier : leur 4 doit porter le geste du 4.
    #
    # `sortantes={"bd"}` ET NON LE REGLAGE GENERAL, et c'est la mesure qui
    # l'impose. Laisses au reglage general, les deux recoivent DEUX gestes :
    # celui du 4, voulu, et celui de leur NUMERATEUR -- le pied du 1 sur
    # `onequarter`, celui du 3 sur `threequarters`. Or le 1 a perdu son geste
    # au quarante-cinquieme tour, en navigateur, et le 3 est ecarte depuis le
    # quarante-quatrieme. Le reglage general aurait donc rendu a ces deux
    # chiffres, dans une fraction, le geste que Nicolas leur a retire ailleurs,
    # et aucun controle ne l'aurait dit : le glyphe porte un nom qui ne nomme
    # aucun des deux.
    #
    # LE QUADRANT SEPARE SANS AMBIGUITE, mesure sur les huit masters des deux
    # sources : le pied du 4 est a 0,81 de la largeur de boite sur
    # `onequarter` au Regular, celui du 1 a 0,087, et `quadrant` coupe a 0,35.
    # Apres ecriture, UN SEUL noeud bouge par glyphe et par master -- le pied
    # du 4, qui plonge de 32 unites -- dans les huit, et le numerateur ne bouge
    # pas d'un centieme.
    #
    # `onehalf` RESTE DEHORS : son 1 et son 2 sont plats tous les deux par
    # decision, donc il n'a rien a recevoir.
    #
    # VALIDES PAR NICOLAS EN NAVIGATEUR sur `tour49.html`, dans des nombres et
    # en regard du 4, du 1 et du 3 pleins aux quatre masters, avec le ½ dans la
    # meme bande pour que la divergence des trois fractions se voie.
    "onequarter": dict(sortantes={"bd"}),
    "threequarters": dict(sortantes={"bd"}),
    # Le r et le u gardent la RENTRANTE de leur bout haut, et ce sont les deux
    # seules exceptions au regime tranche au trente-cinquieme tour. La decision
    # est du neuvieme tour et ce fichier l'ecrit deja pour la sortante : "le r
    # et le u, qui montaient sans rien couter, restent rentrants". Le geste
    # existe donc par choix explicite, et non parce qu'un regime general
    # passait par la.
    #
    # Ce qu'elles valent est mesure au trente-cinquieme tour, en deplacement de
    # noeud sur les quatre masters de chaque source : sans elles le r tombe de
    # 47,7 a 32,0 unites au romain et de 52,8 a 32,7 en italique, le u de 60,1
    # a 33,4 et de 66,5 a 32,2. Les deux entrees sont donc la difference entre
    # une lettre a deux gestes et une lettre a un seul, et sans elles le
    # passage au regime "aucune" aurait retire un geste arrete sans que rien ne
    # le dise -- une table qui change en silence est le piege que ce projet a
    # paye sur FAMILLES_O.
    #
    # Elles ne portent que `rentrantes` : les cles absentes retombent sur
    # DEFAUT, donc theta, cote et sortantes restent ceux du reglage general.
    "r": dict(rentrantes="angle"),
    "u": dict(rentrantes="angle"),

    # --- Les onze du trente-sixieme tour : la sortante du bas ECARTEE.
    #
    # Le regime du haut tranche au tour precedent laisse trente glyphes du
    # perimetre recevoir la sortante, qui est le DEFAUT : aucune ecriture n'est
    # necessaire la ou elle convient. Nicolas a regarde les trente sur deux
    # planches et en a ecarte onze. Dix-neuf gardent donc le geste sans qu'une
    # ligne soit ecrite pour eux, et ces onze-ci sont les derogations.
    #
    # ELLES NE PORTENT QUE `sortantes=()`, ET CE N'EST PAS `exclure`. Un jeu de
    # quadrants aurait ete lu par `lot4.quadrant`, qui classe par position dans
    # une boite que l'italique fait pencher : le pied du Y est `bc` au romain et
    # `bg` en italique, et cinq prescriptions ne designent deja pas la meme
    # chose dans les deux sources -- c'est le point ouvert 65. Une derogation
    # ecrite en quadrants aurait donc pu s'appliquer au romain et pas en
    # italique, en silence. `sortantes=()` ne lit aucun quadrant : le bout part
    # en branche rentrante, que `DEFAUT` laisse a "aucune", et le glyphe reste
    # Atkinson intact dans les huit masters des deux sources.
    #
    # CE QUE CELA ENGAGE, ET QUI EST MESURE : ces onze ne portent alors plus
    # AUCUN geste de titrage, le haut etant deja ecarte. Ils rejoignent les
    # dix-huit glyphes que le perimetre garde sans qu'aucun geste les touche,
    # qui passent donc a vingt-neuf sur 149. Nicolas a tranche au meme tour de
    # laisser les dix-huit tels quels, donc ce nombre est assume.
    #
    # LES SIX DE LA PLANCHE 2, dont le segment tourne sort de la fourchette des
    # vingt glyphes deja valides -- 144 a 354 unites, mesure sur les quatre
    # masters de chaque source. Sur une barre de cette longueur la sortante ne
    # coupe pas un bout : elle fait pencher la barre entiere, l'angle etant
    # d'autant plus petit que le segment est long. Vu sur
    # `planche-propagation-2-longs.png`, ou "LŒSS ÆGLE" compose au Bold montre
    # quatre barres basses qui penchent ensemble.
    "Z": dict(sortantes=()),            # 564 u, la plus longue barre du lot
    "E": dict(sortantes=()),            # 525 u
    "OE": dict(sortantes=()),           # 488 u, la barre du E de la ligature
    "L": dict(sortantes=()),            # 483 u
    "z": dict(sortantes=()),            # 480 u
    "B": dict(sortantes=()),            # 308 u au romain, 387 en italique
    #
    # LES CINQ DE LA PLANCHE 3, dont le segment est DANS la fourchette : leur
    # geste est de meme nature que celui des vingt glyphes valides, et Nicolas
    # les a ecartes sur la forme et non sur la longueur. Vu sur
    # `planche-propagation-3-courts.png`.
    "D": dict(sortantes=()),            # 227 u au romain, 312 en italique
    "Eth": dict(sortantes=()),          # meme dessin que le D, barre en plus
    "Thorn": dict(sortantes=()),        # 170 u
    "l": dict(sortantes=()),            # 107 u au romain, 67 en italique
    "t": dict(sortantes=()),            # 100 u au romain, 76 en italique
    #
    # --- L'AE, trente-neuvieme tour. LA DOUZIEME DEROGATION.
    #
    # Nicolas l'a ecarte sur `planche-ensemble-titrage.png` : "ce AE qui bave
    # vers le bas a gauche". Il portait DEUX gestes, mesures dans les huit
    # masters et de nature differente :
    #
    #   bg   le pied de la diagonale du A, 58 a 200 u. Il descend de 44 ET
    #        SORT A GAUCHE HORS DE LA BOITE, -24,5 a -24,8 u au romain et
    #        -33,1 a -33,9 en italique -- le debord lateral hors origine qui a
    #        fabrique les contacts q+M du lot 1.
    #   bd   la barre basse du E, 420 a 495 u. Elle bascule entiere, son coin
    #        droit restant pose, comme celle du plusminus.
    #
    # LE FAIT QUI A DECIDE N'ETAIT PAS DANS L'AE, IL ETAIT DEJA ECRIT : le A
    # porte `exclure={"hc", "bg"}` depuis son arbitrage, donc Nicolas avait
    # deja refuse ce pied-la. UNE PRESCRIPTION INDEXEE PAR NOM NE SUIT PAS UNE
    # COMPOSITION : l'AE dessine le meme A sous un autre nom et ne recevait
    # rien. C'est la forme du defaut de `e.sc` du trente-huitieme tour, deplacee
    # des DERIVATIONS vers les COMPOSITIONS.
    #
    # Nicolas a tranche la lecture lettre par lettre plutot que la longueur :
    # le A refuse son bg, le E est deja dans cette liste, donc l'AE ne recoit
    # plus rien. Le plusminus garde sa bascule, valide au meme tour.
    "AE": dict(sortantes=()),           # 420 a 495 u au bd, 58 a 200 au bg
    #
    # --- Le n, trente-huitieme tour, point ouvert 69.
    #
    # C'est la seule entree de la table dont le SEUL role est de nommer un
    # coin. Le n n'avait aucune prescription : il prenait le reglage general,
    # qui fait descendre le coin gauche de son pied droit a -32 quand le lot 2
    # fait descendre le coin DROIT a -22 depuis le vingt-deuxieme tour. La
    # pointe du texte etait donc d'abord ecrasee, puis inversee.
    #
    # `pointes={"bd": "droite"}` fait viser au titrage le cote du texte :
    # mesure sur les huit masters des deux sources, le coin droit passe de -22
    # a -32 partout, ce qui est le geste du lot 2 porte a la profondeur du
    # titrage. Le PIED GAUCHE n'est pas touche et garde son coin gauche a -32 :
    # il n'est en conflit avec rien, le lot 2 ne l'ayant jamais coupe.
    #
    # Les autres cles retombent sur DEFAUT, comme pour le r et le u : ecrire
    # ici `cote`, `theta` ou `sortantes` ferait diverger le n du reglage
    # general le jour ou celui-ci changerait, et le projet a paye une table qui
    # diverge en silence sur FAMILLES_O.
    "n": dict(pointes={"bd": "droite"}),
    #
    # --- Le h, QUARANTE-TROISIEME TOUR. Point ouvert 78, arbitre par Nicolas
    # au quarante-deuxieme sur `planche-pied-*.png`, quatre etats.
    #
    # LE H N'AVAIT JAMAIS ETE ARBITRE : `PRESCRIPTIONS["h"]` valait `None`, il
    # prenait le reglage general, et personne ne l'avait ni valide ni ecarte --
    # il n'est meme pas dans `check_perimetre.VALIDES_REGLAGE_GENERAL`. C'est
    # le troisieme etat possible d'un glyphe dans ce projet, entre l'ecrit et
    # le valide : le NON REGARDE, que rien ne distingue du valide dans la table.
    #
    # LE DEFAUT N'ETAIT NI UNE PROFONDEUR NI UNE DIRECTION, C'ETAIT UN COMPTE.
    # Inventorie coin par coin sur tout le repertoire au quarante-deuxieme
    # tour, le regime du bas est regulier : CHAQUE LETTRE PLONGE PAR UN SEUL
    # PIED -- le b par son fut, le d, le u et le a par leur coin droit, le m
    # par son coin gauche, le n par son coin droit, le x par son coin gauche,
    # le f par son crochet. Le h et le k etaient les deux seules a en avoir
    # DEUX, mesure au Regular servi : h (72,-32) et (396,-32), k (72,-32) et
    # (402,-32), les deux fois par le coin gauche. Aucune mesure de depassement
    # ne pouvait le dire, puisque chaque plongee livre bien ses 32 unites : un
    # systeme ne se verifie qu'en l'inventoriant en entier.
    #
    # LE H ET LE N ONT EXACTEMENT LE MEME PIED DANS ATKINSON, (72,0) (156,0)
    # (396,0) (480,0) au Regular. Temoin en faisait deux lettres qui plongent
    # par des coins opposes, sur un nombre de pieds different. `sortantes={"bd"}`
    # ne garde que le pied DROIT et `pointes={"bd": "droite"}` lui fait viser
    # le coin droit, ce qui est rigoureusement le geste ecrit sur le n.
    #
    # LA CIBLE EST 32, LA CIBLE GENERALE DU BAS DE CASSE, ET NON 22. Nicolas a
    # d'abord retenu 22 sur la planche -- l'etat `n22`, ou le pied du h est
    # celui du n a l'unite pres -- puis a revise a 32 en le regardant. LE PRIX
    # EST ECRIT ET ACCEPTE : le n servi plonge a -22 et non a -32, parce qu'il
    # est dans `HORS_FUSION` et garde donc son etat de TEXTE ; le h, lui, prend
    # l'etat de titrage. Les deux lettres cote a cote dans un mot auront donc
    # le meme geste a dix unites de profondeur pres. Aucune valeur n'est ecrite
    # ici : `depassement_pour("h")` rend `DEPASSEMENT`, 32, par la casse du nom,
    # et une cible propre n'aurait fait que figer le meme nombre deux fois.
    #
    # Les autres cles retombent sur DEFAUT, comme pour le n, le r et le u.
    "h": dict(sortantes={"bd"}, pointes={"bd": "droite"}),
    #
    # --- Le k, QUARANTE-TROISIEME TOUR. LA QUATORZIEME DEROGATION.
    # Point ouvert 77, arbitre au quarante-deuxieme tour avec le K capitale.
    #
    # Il est l'autre moitie du compte ci-dessus : deux pieds qui plongent, par
    # le coin gauche, a -32. Nicolas l'a mis A PLAT plutot que de lui laisser
    # un seul pied comme au h, et la difference entre les deux lettres est
    # ecrite dans leur dessin -- le pied droit du h est un fut, celui du k est
    # le bout d'une jambe diagonale.
    #
    # CE QUI REND CETTE ENTREE PARTICULIERE : LE K ETAIT VALIDE. Il figurait
    # dans `check_perimetre.VALIDES_REGLAGE_GENERAL` depuis le trente-neuvieme
    # tour, retenu sur `planche-ensemble-titrage.png`. La validation est donc
    # REVISEE, et c'est la DEUXIEME apres celle du i au quarante-et-unieme
    # tour. LES DEUX TABLES BOUGENT DANS LE MEME GESTE : le k entre dans
    # `BRUT_ATTENDU`, qui passe a quatorze, et sort de
    # `VALIDES_REGLAGE_GENERAL`, qui tombe a quinze. Si une seule bougeait, une
    # table dirait valide ce que l'autre dit ecarte et aucun controle
    # n'echouerait.
    #
    # Et c'est la seconde fois que l'ENDROIT DU REGARD tranche : une planche
    # d'alphabet pose les lettres en grille, a un corps ou 32 unites font cinq
    # pixels et sans voisine posee ; un texte courant a 18 px met le k entre
    # deux lettres. Ce qu'une liste de valides porte, c'est "Nicolas l'a
    # regarde et l'a garde", donc l'endroit compte autant que le regard.
    #
    # `sortantes=()` ET NON `exclure`, pour la raison des treize autres : un
    # jeu de quadrants se lit dans une boite que l'italique fait pencher, et la
    # derogation pourrait s'appliquer a une source et pas a l'autre en silence.
    "k": dict(sortantes=()),            # (72,-32) et (402,-32) au Regular servi
    #
    # --- Le `plus`, CINQUANTE-TROISIEME TOUR. LA DIX-SEPTIEME DEROGATION.
    #
    # Nicolas a signale le `+` de `+32` a la section 8 de `tour51.html`, en
    # texte. Mesure faite avant toute hypothese, sur les deux sources : LA BARRE
    # N'AVAIT PAS BOUGE D'UN DIXIEME, 208 -> 288 et centre a 248 des deux cotes.
    # Ce qui avait bouge est le PIED, allonge de 32 unites sous la ligne de
    # base par le reglage general -- `depassement_pour` rend 32 pour tout nom
    # qui commence par une minuscule, et `plus` est un SIGNE, pas un bas de
    # casse. SIXIEME VALIDATION DE PLANCHE REVISEE EN TEXTE, apres le i, le k,
    # le 1, `idotless` et le R.
    #
    # `sortantes=()` le rend au dessin d'Atkinson par le bas ; `operateurs.py`
    # le remonte ensuite de 64 avec ses sept freres, ce qui porte sa barre a
    # 312. Les deux gestes sont dans deux modules et dans cet ordre, et l'ordre
    # compte : la derogation s'applique pendant la fusion, la translation apres.
    #
    # TROIS TABLES BOUGENT DANS LE MEME GESTE, et c'est une de plus que pour le
    # k : cette ligne, plus `check_perimetre.BRUT_ATTENDU` qui passe de seize a
    # DIX-SEPT, plus `VALIDES_REGLAGE_GENERAL` qui tombe de seize a QUINZE. Si
    # une seule bougeait, une table dirait valide ce que l'autre dit ecarte et
    # aucun controle n'echouerait.
    #
    # LE `plusminus` ET LE `numbersign` NE SUIVENT PAS, et c'est une decision :
    # ils portent la meme plongee de 32 unites, de la meme cause, et Nicolas les
    # a RELUS DANS LA MEME PHRASE au meme tour et gardes tels quels. Ils restent
    # donc dans `VALIDES_REGLAGE_GENERAL`. Une cause commune ne fait pas une
    # decision commune.
    "plus": dict(sortantes=()),         # pied a -32,0 au servi, 0,0 chez Atkinson
    #
    # --- Le i, quarante-et-unieme tour. LA TREIZIEME DEROGATION.
    #
    # Nicolas a ecarte la sortante du i EN NAVIGATEUR, sur le dessin fusionne
    # servi : "le i ne devrait pas descendre bg, garder le bas sans coupe".
    #
    # CE QUI REND CETTE ENTREE PARTICULIERE : le i etait VALIDE. Il figurait
    # dans `check_perimetre.VALIDES_REGLAGE_GENERAL` depuis le trente-neuvieme
    # tour, retenu sur `planche-ensemble-titrage.png` parmi les dix-sept que
    # rien n'ecrivait. La validation est donc REVISEE, et la liste des valides
    # tombe a seize au meme tour -- les deux tables se contrediraient en
    # silence si une seule bougeait.
    #
    # ET C'EST LE TROISIEME DEFAUT QUE SEUL LE NAVIGATEUR A MONTRE, apres le
    # contact de capitales du vingt-quatrieme tour et le blanc des rondes du
    # trente-et-unieme. Une planche d'alphabet pose les lettres en grille, a un
    # corps ou 32 unites font cinq pixels ; un texte courant a 18 px met le i
    # entre deux lettres posees, et la descente se lit comme un glissement du
    # fut. Le geste etait juste au regard de sa mesure dans les huit masters.
    #
    # MESURE AVANT ECRITURE, sur `Temoin.glyphs` servi contre l'amont :
    # `idotless` descend a -32,0 dans les quatre masters romains quand Atkinson
    # le pose a 0,0. Le `l` et le `jdotless`, qui portent la MEME pente du lot 2
    # par `loc_gauche`, ne bougent pas d'une unite : la descente vient du lot 4
    # et d'aucune autre etape, et la pente du pied reste intacte apres cette
    # entree.
    #
    # `sortantes=()` ET NON `exclure={"bg"}`, pour la raison des douze autres :
    # un jeu de quadrants se lit dans une boite que l'italique fait pencher, et
    # la derogation pourrait s'appliquer a une source et pas a l'autre en
    # silence. Le i n'a qu'un seul bout designe, donc les deux ecritures
    # donnent aujourd'hui le meme dessin ; seule celle-ci le garantit demain.
    #
    # LA FAMILLE SUIT SANS ETRE NOMMEE, et c'est une composition qui joue POUR
    # une fois dans le bon sens : le i, le iacute, le icircumflex, le igrave,
    # le idieresis et le idotaccent n'ont aucun trace propre -- ils composent
    # `idotless`. Le piege de l'AE et de l'Aring se retourne ici, le contour
    # etant DANS le composant et non dans la lettre qui le porte.
    #
    # CE QUE CETTE ENTREE NE TOUCHE PAS, et qui est assume : `i.sc` suit sa
    # CAPITALE depuis la fusion, pas le i bas de casse, et le I descend a -44.
    # Un sigle en petites capitales garde donc son i descendant. Nicolas a
    # valide les petites capitales des sigles au meme passage en navigateur.
    "idotless": dict(sortantes=()),     # -32,0 dans les quatre masters romains
    #
    # L'AE ET LE PLUSMINUS GARDENT LEUR SORTANTE et n'ont donc aucune entree
    # ici, bien qu'ils soient dans la meme planche que les six premiers : 495 et
    # 519 unites, hors de la fourchette comme eux, et retenus quand meme. Le
    # dire ici plutot que nulle part : une absence d'entree ne se distingue pas
    # d'un oubli, et `check_perimetre` section 8 exige que les QUATORZE soient
    # exactement les quatorze depuis que le k les a rejoints.
    #
    # LE V ET LE W N'Y SONT PAS ET N'ONT PAS A Y ETRE. Leur `sortantes=()` du
    # quarante-troisieme tour retire une sortante du HAUT, quand `BRUT_ATTENDU`
    # et la section 8 ne mesurent que le BAS. Ils gardent `exclure`, donc leur
    # bas reste dans `jamais` -- la geometrie n'y designe rien une fois le
    # sommet bas exclu -- et c'est la SECTION 13 qui porte leur cas.
}


# Le perimetre du titrage, tranche par Nicolas au trente-quatrieme tour sur
# trois planches d'instruction : `planche-perimetre-1-signes.png`, `-2-chiffres`
# et `-3-accents`. Les glyphes nommes ici gardent la forme d'Atkinson.
#
# POURQUOI CET ENSEMBLE EXISTE. Le reglage general est geometrique : il coupe
# toute terminaison droite posee sur un alignement. Il attrape donc des glyphes
# par propriete et non par intention -- 27 signes, 16 chiffres et fractions,
# 5 accents combinants, mesures par `mesure_titrage.py`. `PRESCRIPTIONS` deroge
# sur la FORME d'un glyphe qui porte le geste ; cet ensemble dit qu'un glyphe
# ne le porte pas du tout. Les deux ne se remplacent pas.
#
# CE QUE LA MESURE A MONTRE, et qui a servi a trancher. Le deplacement de noeud,
# lu en rapport au depassement demande, separe quatre regimes. Au-dela du double
# du depassement, le geste ne deplace plus un bout : il fait pivoter un segment
# entier, dont le bout libre parcourt d'autant plus qu'il est long. Le 5 voit un
# noeud partir de 172 unites pour 32 demandees, le yen de 99, le souligne de 95.
# La plupart des exclusions sont dans ce regime.
#: LA FUSION DU QUARANTIEME TOUR : ces glyphes gardent leur dessin de TEXTE.
#:
#: Nicolas a decide d'eliminer la difference entre le corps et le titrage, donc
#: le reglage de titrage devient le dessin unique : il s'applique desormais au
#: glyphe lui-meme et non a un double, et le jeu stylistique `ss02` disparait.
#:
#: Trente-huit glyphes a contour propre differaient entre les deux etats,
#: mesures sur les huit masters -- trente-sept au romain, plus le Y dont l'ecart
#: ne vit qu'en italique. Nicolas les a tranches un par un, seize de memoire sur
#: la page de controle puis dix-neuf sur `planche-fusion.png` : TOUS prennent le
#: geste du titrage sauf ces trois.
#:
#: Le `r` garde la forme d'Atkinson depuis le vingt-deuxieme tour, et c'est une
#: decision reconduite : le titrage lui posait une RENTRANTE en haut, le r etant
#: avec le u l'une des deux seules exceptions au regime `aucune`. Le `m` et le
#: `n` portent leur plongee de pied arretee sur planche au vingt-cinquieme et au
#: vingt-deuxieme tour, et le titrage l'amplifiait de 32 unites.
#:
#: Le Y n'est PAS ici, et il aurait pu : son ecart vaut 0,3 unite au romain, que
#: la table `glyf` arrondit a zero, et 1,0 en italique. Le faire entrer ou le
#: laisser sortir ne change aucun dessin servi.
#:
#: LE `u` N'EST PAS ICI NON PLUS, ET C'EST UNE LIMITE CONNUE, PAS UN OUBLI.
#: Il porte la MEME et unique prescription que le `r`, `rentrantes="angle"` :
#: tous deux sont les seules exceptions au regime du haut, et leur geste de
#: titrage est la coupe rentrante qui REFERME le haut des futs. Nicolas a
#: refuse ce geste sur le r et l'a garde sur le u, en connaissance du chiffre.
#:
#: Le prix est mesure par `mesure_fusion.py`, la police comparee a elle-meme
#: dans une seule session : `n/u` passe de 0,193 a 0,166 au Bold et de 0,184 a
#: 0,153 a l'ExtraBold, et elle devient LA PAIRE LA PLUS CONFUSABLE DE
#: L'ALPHABET, devant `D/O` qui tenait ce rang a 0,170 et 0,160. Le u degrade
#: aussi `u/v` et `U/V`, de 0,046 au pire. Mettre le u avec le r rendait zero
#: paire sous le plancher et faisait tomber les degradations de neuf a quatre.
#:
#: A RESSORTIR si la lisibilite est mise en cause : le projet publie sous le nom
#: de l'OXA une police presentee comme accessible, et c'est le seul endroit ou
#: un chiffre de confusion se degrade par une decision et non par un defaut.
HORS_FUSION = frozenset({"m", "n", "r"})


HORS_TITRAGE = frozenset({
    # --- planche 1, les signes.
    # L'asterisque, le souligne, le TM et le yen : le geste y fait pivoter une
    # barre entiere au lieu de sortir un bout.
    "asterisk", "underscore", "trademark", "yen",
    # Les signes construits sur le = : la coupe casse le parallelisme des deux
    # barres, qui est ce qui fait lire le signe. Le + et le ± restent DANS le
    # titrage, et le partage se defend par la mesure : le + deplace son bout de
    # 32 a 47 unites, l'ordre du depassement, quand le ≠ en deplace 68.
    "greaterequal", "lessequal", "notequal",
    # Le point d'interrogation. Le renverse suit, pour que la paire ? / ¿ garde
    # une terminaison commune -- et le geste ne le deplacait d'aucune unite.
    "question", "questiondown",
    # --- planche 2, les chiffres et les fractions.
    # QUARANTE-QUATRIEME TOUR, POINT 74a : LE 1, LE 4 ET LE 7 SORTENT DE CETTE
    # LISTE et rejoignent le 9, qui portait le geste tout seul. LE 1 Y EST
    # REVENU AU TOUR SUIVANT, en navigateur -- voir la note du 1 plus bas. Nicolas les a
    # arbitres sur `planche-chiffres-1a-nombres-regular.png` et sa jumelle au
    # Bold, qui composent de VRAIS NOMBRES avec le crenage servi, et sur
    # `planche-chiffres-2-regime.png`, qui montre les deux natures de geste en
    # loupe. Leur segment tourne fait 54 a 201 unites selon le master, quand
    # les 36 sortantes deja arretees en font 40 a 219 : meme nature de geste,
    # et c'est mesure au meme endroit et non repris de la passation.
    #
    # LES QUATRE QUI RESTENT NE RESTENT PLUS POUR LA MEME RAISON, et la raison
    # ecrite ici etait fausse : le trente-quatrieme tour disait que Nicolas les
    # avait ecartes a la main, ce qui est vrai et ne dit pas ce que la
    # geometrie fait. Mesure au quarante-quatrieme tour, huit masters, deux
    # sources, geste pris dans le JOURNAL du producteur :
    #
    #   `two` et `one.tf`  une terminaison en BAS, mais le segment tourne est
    #                      leur BARRE ENTIERE -- 454 a 514 unites sur le 2,
    #                      400 a 432 sur le 1 tabulaire, deux fois le plus long
    #                      segment jamais valide du projet. L'angle tombe a
    #                      3,5-4,6 degres : l'oeil ne lit pas un bout coupe, il
    #                      lit un socle qui bascule. C'EST LE REGIME QUE NICOLAS
    #                      A DEJA ECARTE DEUX FOIS, sur l'asterisque, le
    #                      souligne, le TM et le yen au trente-quatrieme tour,
    #                      et sur les chevrons au trente-septieme.
    #   `five`             une terminaison en HAUT, quadrant `hc` : sa barre
    #                      superieure, 347 a 459 unites, angle 4,0 a 5,3
    #                      degres. Meme regime que le 2, par le haut.
    #   `three`           RIEN, et la raison ecrite ici au quarante-quatrieme
    #                      tour etait fausse. Remesure au quarante-cinquieme sur
    #                      les quatre masters, journal du producteur : il est
    #                      VIDE dans trois d'entre eux -- aucune terminaison
    #                      n'est meme designee -- et au Regular le seul segment
    #                      designe rend `sortie impossible`, force comme non
    #                      force. Le 3 n'est donc pas un cas de DESIGNATION a
    #                      traiter a la main comme au lot 2 : il est dans la
    #                      situation du 0, du 6 et du 8, et il rejoint la
    #                      famille des formes fermees. VINGT-ET-UNIEME CHIFFRE
    #                      DE LA PASSATION CORRIGE.
    #
    # QUARANTE-CINQUIEME TOUR, POINT 74b : NICOLAS REFUSE LES TROIS, sur
    # `planche-74b-1b-regime.png` et `-1c-regime.png`, deux etats en loupe a 560
    # px avec la ligne de base tiree en bande, plus les nombres composes avec le
    # crenage servi au Regular et au Bold. Le 2, le 5 et le 1 tabulaire restent
    # plats ; le 1 proportionnel garde le geste ecrit au tour precedent.
    # **C'est la troisieme fois que ce regime est ecarte**, apres les signes au
    # trente-quatrieme tour et les chevrons au trente-septieme, et la premiere
    # ou il l'est sur une planche qui le montre applique.
    #
    # LE CAS DU 5 DEMANDAIT DEUX DECISIONS ET NON UNE, ce que le point ouvert ne
    # disait pas : son seul segment etant en haut, l'accepter aurait demande de
    # rouvrir `DEFAUT["rentrantes"] = "aucune"`, arrete au trente-cinquieme
    # tour. Le refus ferme les deux questions d'un coup.
    #
    # LE 1 ET LE 1 TABULAIRE DIVERGENT DONC POUR DE BON, et c'est confirme au vu
    # de la planche : le 1 penche, le 1 tabulaire garde son empattement plat.
    # C'est l'inverse de la regle posee pour `fraction` et `divisionslash`, et
    # c'est delibere -- ce sont deux dessins differents.
    #
    # DESIGNE N'EST PAS COUPE, et c'est ce qui rendait le point 74a plus gros
    # qu'il n'est : `loc_alignement` designe une terminaison sur le 3 et le 5,
    # ce que la passation lisait comme "une terminaison designee", et
    # `couper_alignements` ne pose rien -- le regime du haut est `aucune`.
    # Et sur le 3, meme le haut FORCE ne pose rien : la designation elle-meme
    # manque dans trois masters sur quatre. Designe n'est pas coupe, et sur ce
    # glyphe-la il n'est meme pas designe.
    #
    # Le 9 tabulaire est un composite du 9, donc il suit tout seul, et
    # `four.tf` comme `seven.tf` suivent de meme leur base qui entre -- verifie
    # plutot que suppose. Le 1 tabulaire porte son propre contour, donc il est
    # nomme a part.
    #
    # LA DIVERGENCE DES DEUX 1 EST LEVEE AU QUARANTE-CINQUIEME TOUR, et elle
    # l'est par le haut : le quarante-quatrieme avait tranche que le 1 et le 1
    # tabulaire pouvaient diverger, ce sont deux dessins differents -- puis le
    # navigateur a montre ce que cette divergence donne dans un gabarit qui
    # compose ses nombres en tabulaire. Les deux sont plats maintenant, et
    # l'exception a la regle posee pour `fraction` et `divisionslash` n'a plus
    # d'objet.
    # QUARANTE-CINQUIEME TOUR : LE 1 REVIENT DANS CETTE LISTE. Verdict de
    # Nicolas en NAVIGATEUR sur le binaire servi de ce tour, gabarit des cartes
    # RNT. Le 4, le 7 et le 9 gardent leur geste ; le 1 le perd. La cause n'est
    # pas sa forme mais un fait de GABARIT qu'aucune planche ne pouvait montrer :
    # les pages composent presque tous leurs nombres en chiffres TABULAIRES,
    # donc le 1 qu'on y lit est `one.tf`, plat par la decision du tour
    # precedent, pendant que le 1 des paragraphes penchait. Les deux 1 du meme
    # ecran ne se ressemblaient plus. Le 4, le 7 et le 9 echappent a cette
    # divergence parce que leurs tabulaires sont des composites purs de leur
    # base. `check_perimetre.VALIDES_REGLAGE_GENERAL` tombe de dix-huit a
    # dix-sept AU MEME GESTE.
    "one", "one.tf", "two", "three", "five",
    # Les barres de fraction : le geste leur pose un eperon en bas, qui les
    # fait lire comme une barre cassee. `divisionslash` rejoint `fraction` sur
    # decision de Nicolas -- deux barres de fraction du meme repertoire ne
    # peuvent pas avoir deux terminaisons.
    "fraction", "divisionslash",
    # `onequarter` ET `threequarters` SORTENT DE CETTE LISTE au quarante-
    # neuvieme tour, sur demande de Nicolas devant la planche du repertoire
    # entier : leur 4 doit porter le geste du 4, comme le 4 plein. Ils restent
    # ici pour memoire de ce que le trente-quatrieme tour en avait fait, et
    # `onehalf` y reste, son 1 et son 2 etant tous deux plats par decision.
    "onehalf", "percent", "perthousand",
    "twosuperior", "threesuperior",
    # --- planche 3, les accents combinants. Aucun.
    # Le macron devient un coin : sa barre pivote de 72 unites au Bold et le
    # signe cesse d'etre un macron. Le macron d'espacement U+00AF est un
    # composite de `macroncomb`, donc il suit.
    # FAIT QUI VIDE PRESQUE LA QUESTION, mesure sur le repertoire servi :
    # aucune lettre servie n'emploie aucun de ces cinq combinants. C'est le
    # point ouvert 28 etendu de l'ogonek aux quatre autres.
    # L'exclusion ne porte QUE sur le reglage de titrage : la pointe d'ogonek
    # du lot 2, ecrite au dix-huitieme tour, reste.
    "brevecomb", "caroncomb", "macroncomb",
    "ogonekcomb", "ogonekcomb.case",
    # --- trente-septieme tour, les trois que PENTE_BAS fait entrer.
    # Le filtre du geste passe de 0,3 a 0,80 pour rattraper les bouts que le
    # lot 2 a deja tournes ; il designe du meme coup trois bouts que personne
    # n'avait vus, et les trois sont mesures sur les deux sources et les huit
    # masters, avec ou sans le dessin de texte.
    # Les chevrons : leur barre haute penche a 28 degres et le geste ne sort
    # pas un bout, il fait BASCULER LA BARRE ENTIERE -- 213 unites sur le >
    # romain et 211 sur le < italique, pour 32 demandees. C'est le regime que
    # Nicolas a ecarte sur les signes au trente-quatrieme tour, sous la meme
    # forme que l'asterisque et le souligne.
    "less", "greater",
    # L'accent circonflexe combinant, en italique seulement : 93 unites pour 32
    # demandees, sur une mèche dont la pente est celle du signe. Il rejoint les
    # cinq combinants exclus au trente-quatrieme tour, et le meme fait les vide
    # de leur enjeu -- aucune lettre servie n'emploie ce combinant, ses seuls
    # employeurs servis etant ses propres variantes.
    "circumflexcomb",
})


def dans_le_titrage(nom):
    """Ce glyphe recoit-il le reglage general de titrage.

    Une prescription ne suffit pas a repondre : `PRESCRIPTIONS` dit COMMENT un
    glyphe porte le geste, `HORS_TITRAGE` dit s'il le porte. Un glyphe absent
    des deux le porte au reglage general.

    LES PETITES CAPITALES SONT ECARTEES, et c'est une REGLE et non une liste.
    Tranche par Nicolas au trente-huitieme tour sur `planche-point67.png`,
    point ouvert 67. Trois faits mesures, et le troisieme est celui qui decide.

      1  Il n'existe pas de petite capitale non coupee. Atkinson n'en a
         aucune : le lot 3 les derive des capitales DU PROJET, donc elles
         heritent deja de tous les gestes du texte au rapport 574/668 --
         `n.sc` descend a -20,6 et `s.sc` a -10,3 avant tout titrage.
      2  Elles ne servent qu'aux sigles, et le titrage y serait heterogene :
         sur les treize sigles du corpus, DEUX seulement sont homogenes, RNT
         et INRAE. Le S, le O, le C et le U n'ont aucun segment droit a
         couper, donc ENS donne E coupe, N coupe, S intact.
      3  **AUCUNE PRESCRIPTION NE SE PROPAGE A UNE PETITE CAPITALE.** Une table
         indexee par nom de glyphe ne suit pas une derivation qui CHANGE le
         nom : le E porte `sortantes=()` depuis le trente-sixieme tour, et
         `e.sc` recevait quand meme 32 unites. Sept glyphes etaient dans ce
         cas -- b.sc d.sc e.sc l.sc oe.sc t.sc z.sc -- et ils portaient
         exactement le geste que Nicolas avait ECARTE sur leur capitale. Il
         l'a retrouve a l'oeil sur la planche, sur le E, avant qu'aucun
         controle ne le signale.

    C'est une regle plutot que 44 noms dans `HORS_TITRAGE` pour deux raisons.
    Elle suit le jour ou le lot 3 s'etend, alors qu'une liste serait a tenir.
    Et `HORS_TITRAGE` est verifie par les sections 1 et 2 de `check_perimetre`,
    qui lisent la source AMONT : y mettre des noms qui n'existent que dans la
    source du projet ferait crier le controle sur sa propre exclusion.
    """
    if nom.endswith(".sc"):
        return False
    return nom not in HORS_TITRAGE


def prescription(nom):
    """La prescription effective d'un glyphe : la sienne, ou le reglage general."""
    return dict(PRESCRIPTIONS.get(nom, DEFAUT))
