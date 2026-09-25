#!/usr/bin/env python3
"""Mesures communes aux formes de O du lot 4.

Sorties de `planche_lot4d.py`, qui les portait en local, pour que la planche du
douzieme tour et le controle chiffre du lot lisent la meme chose. Trois ajouts
par rapport a la version d'origine :

- `topologie` compte a deux resolutions et ne conclut que si les deux
  concordent, comme `check5.py` le fait depuis le lot 3 ;
- `confusion` accepte des contours et non des noms de glyphes, ce qui est
  necessaire ici puisque les variantes n'existent dans aucune source ;
- `brider_haut` cherche par dichotomie le reglage qui ramene le point le plus
  haut sous une cible. Le reglage est deduit, pas choisi, et il est calcule
  master par master : c'est ce que le lot 2 fait deja pour l'angle de la queue
  du g.
"""

import math

import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFilter

import coupe as K
import lot2 as L
import lot4 as Q
import dessin as D


# ------------------------------------------------------------- construction

def contours(paths):
    return [D.flatten(p) for p in paths]


def ep_paroi(lay, ang=180.0):
    """Epaisseur de la paroi de l'anneau a un angle donne, en unites.

    Sert a exprimer les epaisseurs ajoutees en fraction de la paroi mesuree :
    un reglage cale sur le Bold, ou elle vaut 168 unites, donnerait n'importe
    quoi en ExtraLight ou elle en vaut 57.
    """
    _, bords, _ = Q.rayons(L.paths(lay))
    PE, PI = bords(ang)
    return float(np.hypot(*(PE - PI)))


def _refuser_non_resolu(r, quoi):
    """LEVE si un champ du reglage est encore un dict par master.

    `lot4.O_TITRAGE` porte depuis le quarante-septieme tour `ep_facteur` et
    `enfoui` par master. Un appelant qui passe la table brute demanderait a
    multiplier une epaisseur de paroi par un DICTIONNAIRE : selon le champ, ca
    leve loin de la cause ou ca rend une forme absurde, et une planche en
    rendrait l'image sans erreur -- le mode de defaut que ce projet craint le
    plus. La sortie est `lot4.reglage_O(master)`.
    """
    par_master = sorted(k for k, v in r.items() if isinstance(v, dict))
    if par_master:
        raise ValueError(
            f"{quoi} : {', '.join(par_master)} porte(nt) une valeur PAR MASTER "
            f"et le reglage n'est pas resolu. Appeler "
            f"`lot4.reglage_O(nom_du_master)` avant, et ne pas passer "
            f"`lot4.O_TITRAGE` tel quel.")


def famille_O(lay, genre, r):
    """(contours de base, contours ajoutes) pour une variante de O.

    Les ajoutes sont peints apres la base et jamais en blanc : un contour
    positif pose dans une contreforme est encre par le remplissage non nul.
    """
    r = dict(r)
    r.pop("_note", None)
    _refuser_non_resolu(r, "famille_O")
    fac = r.pop("ep_facteur", None)
    ep = ep_paroi(lay) * fac if fac else None
    base = contours(L.paths(lay))
    if genre is None:
        return base, []
    if genre == "contre":
        ext = max(L.paths(lay), key=lambda p: abs(K.area(K.to_segs(p))))
        return [D.flatten(ext), D.flatten(Q.contre_spirale(L.paths(lay), **r))], []
    if genre == "anneau":
        return [D.flatten(Q.anneau_joint(L.paths(lay), **r))], []
    if genre == "bras":
        return base, [D.flatten(Q.bras_spirale(L.paths(lay), epaisseur=ep, **r))]
    if genre == "ancre":
        return base, [D.flatten(Q.bras_ancre(L.paths(lay), epaisseur=ep, **r))]
    if genre == "meche":
        return base, [D.flatten(Q.meche(L.paths(lay), epaisseur=ep, **r))]
    raise ValueError(genre)


# ------------------------------------------------------------------ mesures

def _rendu(base, sus, taille):
    k = taille / 1000.0
    im = Image.new("L", (taille, taille), 255)
    dr = ImageDraw.Draw(im)
    ox, oy = taille * 0.12, taille * 0.88
    # `base` PASSE PAR `classer`, point 85, quarante-neuvieme tour. Le bras
    # arrive normalement par `sus`, peint en dernier, donc l'ordre etait deja
    # juste sur le chemin de `check_O`, qui RETIRE le bras ecrit avant de
    # mesurer. Mais rien n'oblige un appelant a le faire : si `base` vient de
    # la source servie, elle porte le bras et le classement par le signe
    # l'effacait. Sur un glyphe sans greffe les deux classements rendent la
    # meme image, donc les chiffres anterieurs tiennent.
    for p, e in D.couches(base):
        if len(p) > 2:
            dr.polygon([(ox + x * k, oy - y * k) for x, y in p],
                       fill=0 if e else 255)
    for p in sus:
        if len(p) > 2:
            dr.polygon([(ox + x * k, oy - y * k) for x, y in p], fill=0)
    return np.asarray(im) < 128


def _compte(a, seuil):
    encre = int(a.sum())
    lab, n = ndimage.label(~a)
    inte = [int((lab == i).sum()) for i in range(1, n + 1)
            if not ((lab == i)[0, :].any() or (lab == i)[-1, :].any()
                    or (lab == i)[:, 0].any() or (lab == i)[:, -1].any())]
    inte = [v for v in sorted(inte, reverse=True) if v > seuil * encre]
    taches = ndimage.label(a, structure=np.ones((3, 3)))[1]
    return taches, inte, encre


def mesures(base, sus, taille=900, seuil=0.002):
    """(taches, contreformes, encre, boite) a une resolution."""
    taches, inte, encre = _compte(_rendu(base, sus, taille), seuil)
    xs = [x for c in base + sus for x, _ in c]
    ys = [y for c in base + sus for _, y in c]
    return taches, inte, encre, (min(xs), min(ys), max(xs), max(ys))


def topologie(base, sus, seuil=0.002):
    """(taches, contreformes, accord) compte a 900 et a 1800 pixels.

    Un compte de contreformes obtenu par rasterisation depend de la resolution
    des qu'il y a une quasi-tangence : le Ccedilla italique changeait de compte
    entre 190 et 1800 px. Ne conclure que si les deux resolutions concordent,
    et le dire quand elles divergent.
    """
    t9, i9, _ = _compte(_rendu(base, sus, 900), seuil)
    t18, i18, _ = _compte(_rendu(base, sus, 1800), seuil)
    return t9, len(i9), (t9 == t18 and len(i9) == len(i18))


def confusion(A, B, px=120, rayon=3.0):
    """Distance entre deux dessins vus a acuite reduite, entre 0 et 1.

    A et B sont des couples (base, ajoutes). L'ordre de peinture n'est pas un
    detail : une premiere version prenait une liste de contours plate et
    peignait tous les positifs puis tous les negatifs en blanc, ce qui efface
    un contour ajoute dans la contreforme. Elle rendait exactement 0,000 sur
    toute la famille du bras rentre — le dessin mesure etait le O lui-meme.
    C'est le meme piege que le peintre des planches du troisieme tour, et il
    s'est vu parce qu'une colonne entiere ne variait pas.

    Meme mesure que `mesure4.confusion`, mais sur des contours : les variantes
    de O n'existent dans aucune source, on ne peut pas les designer par un nom.

    Etalonnage sur la police de base, au Bold, flou 3 px sur 120 : E/F 0,255,
    B/P 0,257, E/B 0,237, F/P 0,228, I/T 0,209, E/L 0,327, F/T 0,473. La paire
    la plus serree de l'echantillon est I/T a 0,209. Sur le groupe des rondes,
    le O d'Atkinson est a 0,160 du C, 0,074 du Q et 0,221 de la volute
    ecartee : une variante qui descend sous le niveau du C se lit moins comme
    un O que le C lui-meme.

    Le cadrage et la normalisation d'aire sont indispensables : sans eux la
    mesure compte surtout la difference de graisse et de taille.
    """
    ims = []
    for base, sus in (A, B):
        cs = base + sus
        xs = [x for c in cs for x, _ in c]
        ys = [y for c in cs for _, y in c]
        k = px * 0.78 / max(max(xs) - min(xs), max(ys) - min(ys))
        im = Image.new("L", (px, px), 255)
        dr = ImageDraw.Draw(im)
        ox = px / 2 - (min(xs) + max(xs)) / 2 * k
        oy = px / 2 + (min(ys) + max(ys)) / 2 * k
        for c, e in list(D.couches(base)) + [(c_, True) for c_ in sus]:
            if len(c) > 2:
                dr.polygon([(ox + x * k, oy - y * k) for x, y in c],
                           fill=0 if e else 255)
        arr = 255.0 - np.asarray(im.filter(ImageFilter.GaussianBlur(rayon)))
        ims.append(arr / (arr.sum() or 1.0))
    return float(np.abs(ims[0] - ims[1]).sum()) / 2.0


def blanc_flou(base, sus, px=200, rayon=5.0, seuil=140):
    """Aire de contreforme qui survit a un flou, en pixels au carre.

    La mesure qui manquait, et l'image l'a dite avant les chiffres. L'aire de
    contreforme nette du bras rentre vaut 0,79 a 0,92 de celle du O, ce qui
    parait supportable ; a acuite reduite la meme lettre devient un disque
    presque plein, parce qu'un blanc reduit a un croissant mince se comble des
    que l'oeil perd en resolution. L'aire nette et l'aire perceptible ne sont
    pas la meme grandeur.

    On rend la lettre, on floute, et on compte les pixels restes clairs qui ne
    touchent pas le bord de l'image. Le rayon vaut 2,5 % du cadratin, l'ordre
    de grandeur utilise depuis le lot 1 pour simuler une acuite reduite.

    A lire en rapport de celle du O du meme master, jamais dans l'absolu : le
    blanc d'un ExtraBold est petit avant toute modification.
    """
    k = px / 1000.0
    im = Image.new("L", (px, px), 255)
    dr = ImageDraw.Draw(im)
    ox, oy = px * 0.14, px * 0.86
    for c, e in list(D.couches(base)) + [(c_, True) for c_ in sus]:
        if len(c) > 2:
            dr.polygon([(ox + x * k, oy - y * k) for x, y in c],
                       fill=0 if e else 255)
    a = np.asarray(im.filter(ImageFilter.GaussianBlur(rayon))) > seuil
    lab, n = ndimage.label(a)
    garde = [int((lab == i).sum()) for i in range(1, n + 1)
             if not ((lab == i)[0, :].any() or (lab == i)[-1, :].any()
                     or (lab == i)[:, 0].any() or (lab == i)[:, -1].any())]
    return max(garde) if garde else 0


def taches_mot(pieces, px_cadratin=300):
    """Nombre de taches d'encre d'un mot compose.

    `pieces` est une liste de (base, ajoutes, avance) en unites. Une queue qui
    sort de l'anneau peut rester dans la chasse du glyphe et toucher quand
    meme la lettre suivante, parce que la chasse comprend deux approches et
    que la voisine peut avancer dans la sienne. Le debord hors de la chasse ne
    le dit donc pas : il faut composer le mot et compter.

    Ecrite en regardant TEMOIN, ou la queue de la variante libre parait
    toucher le I alors que le debord hors chasse vaut -30, c'est-a-dire
    dedans. Verdict : elle ne le touche pas, l'oeil etait plus severe que la
    geometrie. C'est la mesure qui a raison, et c'est pour cela qu'elle existe.

    Elle rend zero sur les quinze variantes du douzieme tour, ce qui est le
    resultat attendu et donc le plus suspect. Temoin de controle : en poussant
    l'ecart de la queue vers la droite, elle passe de 3 taches a 2 sur OXA a
    400 unites. Elle discrimine, ses zeros valent quelque chose.
    """
    k = px_cadratin / 1000.0
    larg = int(sum(a for _, _, a in pieces) * k) + 40
    haut_px = int(1.6 * px_cadratin)
    im = Image.new("L", (max(larg, 10), haut_px), 255)
    dr = ImageDraw.Draw(im)
    pen, oy = 20.0, haut_px * 0.75
    for base, sus, av in pieces:
        for c, e in list(D.couches(base)) + [(c_, True) for c_ in sus]:
            if len(c) > 2:
                dr.polygon([(pen + x * k, oy - y * k) for x, y in c],
                           fill=0 if e else 255)
        pen += av * k
    a = np.asarray(im) < 128
    return int(ndimage.label(a, structure=np.ones((3, 3)))[1])


def fente(lay, r, n=400):
    """Le raccord du bras a la paroi, en quatre nombres.

    Le treizieme tour a trouve la fente en aiguille a l'oeil, sur une loupe, et
    rien ne la mesurait. Les nombres rendus ici :

    `angle`   l'angle d'ouverture du coin blanc au point ou le bras sort de la
              paroi. Un des deux bords du coin est le bord interieur de
              l'anneau, donc l'angle se lit directement comme
              atan(jour / arc parcouru). Petit = aiguille.
    `L24`     l'arc, en unites, a parcourir avant que le jour atteigne 24
              unites, soit la bande du debord des rondes que `mesure4.appui`
              utilise deja. Grand = aiguille longue.
    `cache`   les degres de spirale pendant lesquels le bras reste noye dans la
              paroi. C'est ce que la soudure profonde coute, et le douzieme
              tour ne le mesurait pas : M7 obtenait son bel angle en noyant 119
              degres du geste, ce que la table lisait comme un gain de blanc.
    `saillie` de combien la racine ressort dans la contreforme, lue sur les
              deux coins reellement dessines par `lot4._flancs_bras`.
    `jour_bout` la passe blanche la plus etroite a cote du bout, contre le
              corps du bras et contre la paroi. Trouvee a l'oeil sur la plongee
              raide, ou le bout revient frôler le corps qu'il vient de
              quitter.

    Pourquoi les quatre ensemble. Le premier controle ecrit ne rendait que
    l'angle, et il classait l'etat affleurant du treizieme tour *au-dessus* de
    l'etat de depart, quand la loupe le donnait pour le pire des huit. Les deux
    disaient vrai sur deux objets differents : l'oeil condamnait la racine qui
    ressort, la mesure decrivait la fente. Un seul nombre pour deux defauts
    distincts se trompe forcement sur l'un des deux.

    Le jour est mesure radialement, comme la construction elle-meme, et
    `saillie` a la place l'est sur les coins : la relation `enfoui` >=
    `ep_facteur` / 2 suffit a garantir l'enfouissement au seul angle de depart,
    pas aux deux coins d'une coupe droite posee sur une paroi courbe.
    """
    r = dict(r)
    _refuser_non_resolu(r, "fente")
    fac = r.pop("ep_facteur", 0.55)
    r.pop("_note", None)
    ep = ep_paroi(lay) * fac
    C, bords, _ = Q.rayons(L.paths(lay))
    cache_p = {}

    def polaire(ang):
        if ang not in cache_p:
            PE, PI = bords(ang)
            ri = float(np.hypot(*(PI - C)))
            cache_p[ang] = (ri, float(np.hypot(*(PE - C))) - ri)
        return cache_p[ang]

    phi, lg, sens = r["phi"], r["longueur"], r["sens"]
    courbe, effile, pointe = r.get("courbe", 1.0), r.get("effile", 0.55), r.get("pointe", 0.05)
    r0, ep0 = polaire(phi)
    depart = r0 + r["enfoui"] * ep0
    arc, prev, emerg, arc_e, ang_e, L24 = 0.0, None, None, None, None, None
    for k in range(n + 1):
        s = k / n
        ang = phi + sens * lg * s
        ri, _ = polaire(ang)
        rad = depart + (r["r_fin"] * ri - depart) * (s ** courbe)
        demi = 0.5 * ep * (pointe + (1.0 - pointe) * max(0.0, 1.0 - s) ** effile)
        jour = ri - (rad + demi)
        P = C + rad * Q.direction(ang)
        if prev is not None:
            arc += float(np.hypot(*(P - prev)))
        prev = P
        if emerg is None and jour > 0:
            emerg, arc_e, ang_e = P, arc, ang
        if emerg is not None and L24 is None and jour >= 24.0:
            L24 = arc - arc_e

    axe, bg, bd = Q._flancs_bras(L.paths(lay), phi, lg, ep, r["enfoui"],
                                 r["r_fin"], sens, r.get("n", 20), courbe,
                                 pointe, effile)
    saillie = 0.0
    for P in (bg[0], bd[0]):
        v = P - C
        ang = math.degrees(math.atan2(v[1], v[0]))
        ri, _ = polaire(ang)
        saillie = max(saillie, ri - float(np.hypot(*v)))

    # --- Le jour au bout : la passe blanche la plus etroite a cote du bout,
    # --- contre le corps du bras d'un cote et contre la paroi de l'autre.
    # --- Trouve a l'oeil sur la plongee raide, ou le bout revient frôler le
    # --- corps qu'il vient de quitter. Aucune colonne ne le disait, et la
    # --- topologie non plus : deux traits qui se frôlent sans se toucher font
    # --- toujours une tache et une contreforme, mais le blanc entre eux se
    # --- comble a acuite reduite et le geste devient une masse.
    nb = len(axe) - 1
    dem = [float(np.hypot(*(bg[k] - axe[k]))) for k in range(nb + 1)]
    inter = [c for c in contours(L.paths(lay)) if D.aire(c) < 0]
    jour_b = float("inf")
    for P, dP in ((bg[-1], 0.0), (bd[-1], 0.0), (axe[-1], dem[-1])):
        for k in range(int(nb * 0.6)):
            jour_b = min(jour_b, float(np.hypot(*(P - axe[k]))) - dP - dem[k])
        for c in inter:
            for X in c:
                jour_b = min(jour_b, float(np.hypot(*(P - np.asarray(X)))) - dP)

    if emerg is None:                     # le bras ne sort jamais de la paroi
        return dict(angle=0.0, L24=float("inf"), cache=abs(sens * lg),
                    saillie=saillie, jour_bout=jour_b, emerg=None)
    return dict(angle=math.degrees(math.atan(24.0 / L24)) if L24 else 90.0,
                L24=L24 if L24 is not None else float("inf"),
                cache=abs(ang_e - phi), saillie=saillie, jour_bout=jour_b,
                emerg=emerg)


def haut(lay, genre, r):
    """Point le plus haut du dessin, en unites."""
    b, s = famille_O(lay, genre, r)
    return max(y for c in b + s for _, y in c)


def brider_haut(lay, genre, r, cle, cible, lo=0.0, hi=None, tol=0.5, iters=40):
    """La plus grande valeur de `cle` dont le point haut reste sous `cible`.

    Dichotomie, comme les plafonds de rotation du lot 2 et le plafond
    d'extrapolation du lot 3 : la valeur est deduite d'une contrainte, pas
    choisie a la main. Elle est calculee master par master, le dessin de
    l'anneau n'etant pas homothetique d'un bout de l'axe a l'autre.

    Rend None si la valeur la plus basse depasse deja la cible : c'est le cas
    ou la contrainte ne peut pas etre tenue par ce parametre, et il vaut mieux
    le dire que rendre un chiffre.
    """
    hi = r[cle] if hi is None else hi
    if haut(lay, genre, dict(r, **{cle: lo})) > cible:
        return None
    if haut(lay, genre, dict(r, **{cle: hi})) <= cible:
        return hi
    for _ in range(iters):
        mid = (lo + hi) / 2.0
        if haut(lay, genre, dict(r, **{cle: mid})) <= cible:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return lo
