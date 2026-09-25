#!/usr/bin/env python3
"""
Temoin, lot 4, vingtieme tour : l'outillage des six terminaisons demandees par
Nicolas sur le specimen du corpus.

Meme role que `souscrits.py` au dix-septieme tour. Il porte les localisateurs
neufs, l'operation nouvelle, les etats candidats et les mesures. Rien n'est
ecrit dans `lot2.LOT2` : la table ne recevra que la forme tranchee, et d'un seul
coup, comme les dix-sept souscrits au dix-huitieme tour.

Les six terminaisons :

  A   r   le bout du bras            loc_droite (existant)
  B   n   le haut du fut gauche      loc_sommet_fut
  C   m   le haut du fut gauche      loc_sommet_fut
  D1  t   la queue                   loc_queue_t
  D2  t   le sommet du fut           loc_sommet_fut
  E   f   le bout du crochet         loc_haut_vertical

Chaque fonction porte dans son docstring ce qui l'a fait ecrire, comme
`mesure_O.py` et `souscrits.py`.
"""

import math

import numpy as np

import coupe as K
import lot2 as L
import lot4 as Q


# ------------------------------------------------------------ localisateurs
#
# Verifies par `check_termes.py` sur les huit masters des deux sources : meme
# contour, meme indice, meme topologie, meme quadrant, meme orientation.

def loc_sommet_fut(segs):
    """Le segment droit HORIZONTAL le plus haut.

    Le sommet du fut gauche du n et du m, a la hauteur d'x, et le sommet du fut
    du t, a 620, qui ne porte aucun alignement.

    Pourquoi pas `loc_hampe`, qui rend deja le bon segment sur les trois : il
    filtre par `both_sharp`, donc il depend du drapeau `smooth` des noeuds. Ce
    drapeau n'est pas identique dans tous les masters de la source — le D a un
    noeud lisse au Bold et pas ailleurs, piege du lot 3. Filtrer par orientation
    ne depend d'aucun drapeau.
    """
    cand = L.lines(segs, vertical=False)
    return [max(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


def loc_haut_vertical(segs):
    """Le segment droit VERTICAL le plus haut : le bout du crochet du f."""
    cand = L.lines(segs, vertical=True)
    return [max(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


def loc_queue_t(segs):
    """Le segment droit VERTICAL le plus bas : le bout de la queue du t.

    `loc_droite` ne convient pas, et c'est le resultat du vingtieme tour. Il
    designe la queue en Regular, Bold et ExtraBold romains, et le bout droit de
    la barre transversale dans les cinq autres masters : en ExtraLight les deux
    sont a un point l'un de l'autre en abscisse, 259 contre 258. La demande de
    Nicolas dit "la meme coupe que le l", et le l recoit `loc_droite` — la
    lecture directe menait donc a un localisateur qui bascule. C'est le temoin
    de `check_termes.py`.
    """
    cand = L.lines(segs, vertical=True)
    return [min(cand, key=lambda i: K.mid(segs[i])[1])] if cand else []


def loc_pied_droit(segs):
    """Le pied du fut droit : le plus a droite des bouts poses le plus bas.

    `loc_bas` ne convient pas : le n a deux pieds a la meme hauteur, et
    `min` sur l'ordonnee rend le premier des deux dans l'ordre du contour,
    c'est-a-dire le pied gauche. Un localisateur qui depart deux candidats a
    egalite par l'ordre du contour est un localisateur qui tire au sort.
    """
    cand = L.lines(segs, vertical=False)
    if not cand:
        return []
    ymin = min(K.mid(segs[i])[1] for i in cand)
    bas = [i for i in cand if K.mid(segs[i])[1] < ymin + 12]
    return [max(bas, key=lambda i: K.mid(segs[i])[0])] if bas else []


# `loc_pied_gauche` est descendu dans `lot2.py` au vingt-cinquieme tour, avec
# les trois entrees qu'il sert. L'alias reste pour les planches d'instruction du
# lot 1, qui le nomment par ce module : deux copies d'un localisateur finissent
# par diverger, et c'est le protocole du vingt-deuxieme tour.
loc_pied_gauche = L.loc_pied_gauche

# Lot 3 : descendus dans `lot2.py` avec les trois entrees qu'ils servent au
# vingt-septieme tour. Les alias restent pour le balayage et les planches
# d'instruction, qui les nomment par ce module.
loc_bout_jambe = L.loc_bout_jambe
loc_bout_queue_y = L.loc_bout_queue_y
loc_pied_Y = L.loc_pied_Y

# Lot 4a, vingt-huitieme tour : le sommet du fut droit du N et du H. Ecrit
# directement dans `lot2.py`, l'alias servant au balayage et aux planches.
loc_sommet_droit = L.loc_sommet_droit


LOCS = {
    "A": ("r", L.loc_droite),
    "N": ("n", loc_pied_droit),
    "F": ("f", loc_haut_vertical),
    "B": ("n", loc_sommet_fut),
    "C": ("m", loc_sommet_fut),
    "D1": ("t", loc_queue_t),
    "D2": ("t", loc_sommet_fut),
    "E": ("f", loc_haut_vertical),
    # Lot 1 du vingt-cinquieme tour : les trois pieds gauches qui descendent
    # sous la ligne de base. Meme geometrie que le pied droit du n, en miroir.
    "P-f": ("f", loc_pied_gauche),
    "P-m": ("m", loc_pied_gauche),
    "P-M": ("M", loc_pied_gauche),
    # Lot 2 du vingt-cinquieme tour : les rentrants. Un coin recule, l'autre
    # tient l'alignement. Le bout de hampe du b, du d et du l porte l'ascendante
    # **MESUREE a 708** — la passation l'annoncait a 796, qui est une metrique
    # de ligne qu'aucune lettre de la police n'atteint, et le vingt-sixieme tour
    # a corrige le chiffre ; le commentaire, lui, ne l'avait pas ete. Les deux
    # bouts libres du z portent la hauteur d'x et la ligne de
    # base. Le precedent est le sommet du fut du g et du q, exception assumee
    # depuis le lot 2, ou seul un coin sur deux descend.
    #
    # Ce qui excluait ces quatre lettres du lot 2 est la regle de perimetre,
    # jamais une coupe qui porte un alignement. **Ce n'est pas l'absence de
    # terminaison libre** : l'inventaire du lot 4 liste quatorze lettres sans
    # terminaison libre, X V W Y M N U et n m r u v w x, et aucune des quatre
    # n'y est. Une affirmation contraire de la passation venait d'un inventaire
    # cite de memoire, et elle decourageait la demande.
    "H-b": ("b", loc_sommet_fut),
    "H-d": ("d", loc_sommet_fut),
    "H-l": ("l", loc_sommet_fut),
    "Z-z": ("z", L.loc_bouts_Z),
    # Lot 3 du vingt-cinquieme tour : la descendante, et ce qui n'en est pas.
    # Trois familles et non une, et c'est mesure :
    #
    #   J-p  le bout de la jambe du p, sur la descendante MESUREE a −162.
    #   Q-y  le bout de la queue du y, sur la meme descendante, mais VERTICAL,
    #        donc son coin coulisse a l'horizontale et non vers le bas.
    #   Y-Y  le pied du Y capitale, sur la LIGNE DE BASE : son ymin vaut 0,0
    #        dans les huit masters. Le Y ne descend pas, et il est
    #        geometriquement dans la famille du lot 1 — le pied gauche du m, du
    #        M et du f — et non dans celle du p.
    #
    # **Deux chiffres de la passation sont faux et la passe 1 les corrige.** Le
    # point ouvert 20 annonce que les jambes du p, du q, du y, du j et du g se
    # terminent a −251 : le p et le y s'arretent a −162, le q a −172 a −174, le
    # g a −186 a −205 par le debord de sa courbe, et AUCUNE lettre n'atteint
    # −251, qui est le `descender` declare. Le seul glyphe qui y touche est
    # `commaaccentcomb`, le plancher de la police. C'est le piege du bout de
    # hampe au vingt-sixieme tour, annonce a 796 et mesure a 708.
    #
    # Nicolas a demande au vingt-septieme tour que le y et le Y se traitent
    # separement : « c'est pas la meme demande ». La geometrie le confirme avant
    # toute mesure d'intention.
    "J-p": ("p", loc_bout_jambe),
    "Q-y": ("y", loc_bout_queue_y),
    "Y-Y": ("Y", loc_pied_Y),
    # Lot 4a du vingt-cinquieme tour, instruit au vingt-huitieme : les
    # depassements par le HAUT. C'est le premier lot du projet ou de la matiere
    # sort au-dessus de son alignement — rien de la coupe texte ne le fait.
    #
    #   H-h  le bout de hampe du h, coin DROIT qui monte, sur l'ascendante
    #        mesuree a 708. Meme bout et meme localisateur que le b, le d et le
    #        l du lot 2 ; c'est le sens qui s'inverse, le coin sortant au lieu
    #        de rentrer.
    #   H-k  le bout de hampe du k, coin GAUCHE qui monte. Le k porte en plus un
    #        bout horizontal a la hauteur d'x, la jonction de son bras, 67
    #        unites contre 54 : `loc_sommet_fut` ne le retient pas, le bout de
    #        hampe etant seul a 708.
    #   S-N  le sommet du fut droit du N, coin DROIT qui monte, hauteur de
    #        capitale 668.
    #   S-H  le sommet du fut droit du H, meme geste.
    #   P-N  le pied du fut gauche du N, coin GAUCHE qui descend. Ce n'est pas
    #        dans la demande de Nicolas, qui ne nomme que « en haut a droite »
    #        pour le N ; c'est la moitie basse de la prescription de titrage,
    #        mesuree ici pour que l'arbitrage puisse la reprendre ou non.
    #   P-H  le pied du fut gauche du H, coin GAUCHE qui descend. Celle-la EST
    #        dans le geste retenu : la demande dit « en haut a gauche et en bas
    #        a droite », l'autre diagonale que le titrage, et Nicolas a tranche
    #        au vingt-huitieme tour pour bg + hd, celle du titrage.
    #
    # Les six bouts sont HORIZONTAUX, donc le nom de coin qui les departage est
    # « gauche » ou « droite » et jamais « bas » ni « haut » : `_coin_vise_est_P`
    # leve sur les seconds, et c'est le refus pose au vingt-septieme tour.
    #
    # Les six coins coulissent le long d'un flanc de fut, donc VERTICAL, donc le
    # coin part tout droit et la boite ne s'elargit pas. C'est ce qui separe ce
    # sous-lot du 4b : le A et le X portent leur bout sur une diagonale, et une
    # sortante sur un flanc diagonal mange l'approche — 16 unites de boite sur
    # le K, 54 sur le Y, mesurees au septieme tour. La passe 2 le verifie au
    # lieu de le supposer : la passation a deja affirme qu'une boite ne bougeait
    # pas alors que ce n'etait vrai qu'en romain, sur le pied droit du n.
    "H-h": ("h", loc_sommet_fut),
    "H-k": ("k", loc_sommet_fut),
    "S-N": ("N", loc_sommet_droit),
    "S-H": ("H", loc_sommet_droit),
    "P-N": ("N", loc_pied_gauche),
    "P-H": ("H", loc_pied_gauche),
    # Sous-lot 4b du vingt-cinquieme tour, instruit au vingt-neuvieme : les deux
    # DIAGONALES, A et X, celles qui recoivent la coupe du titrage.
    #
    #   P-A  le pied DROIT du A, coin droit qui plonge sous la ligne de base.
    #        `lot4.PRESCRIPTIONS` porte `sortantes={"bd"}` et
    #        `exclure={"bg","hc"}` depuis le dixieme tour : le bas droit sort,
    #        le bas gauche reste plat, le sommet reste droit. Nicolas a confirme
    #        les trois au vingt-neuvieme tour.
    #   P-X  le pied GAUCHE du X, coin gauche qui plonge.
    #        `PRESCRIPTIONS` porte `sortantes={"bg"}`, `pointes={"bg":"gauche"}`
    #        et `exclure={"bd","hg","hd"}`. **`pointes` ne fait AUCUNE mise en
    #        pointe** : il ne sert qu'a forcer le sens de rotation par
    #        `lot4.sens_pour_pointe`, pour que le coin sortant soit celui du cote
    #        nomme. Le mot y designe un coin, pas une operation, et la
    #        prescription est donc une `coupe_sortante` et rien d'autre.
    #
    # AUCUN LOCALISATEUR NEUF, et c'est mesure et non suppose. La passation
    # annonce que le A et le X n'en ont aucun et que c'est le travail principal
    # du sous-lot ; les deux localisateurs du lot 1 les servent, et ils
    # DEPARTAGENT au lieu de tomber juste, ce qui est le defaut de
    # `loc_sommet_fut` sur le N et le H :
    #
    #   sur le A, les candidats horizontaux du contour d'encre sont les segs 0,
    #   2, 4 et 6 dans les huit masters ; le filtre a 12 unites au-dessus du
    #   plus bas ecarte la traverse a 168 et le sommet a 668, et le departage se
    #   fait sur des milieux a x = 38 et 545 en ExtraLight, sans egalite.
    #   Sur le X, les candidats sont les segs 0, 3, 6 et 9 ; le filtre garde les
    #   deux pieds, poses tous deux sur la ligne de base, et le departage se
    #   fait a x = 47,5 et 542,5.
    #
    # **ET SUR LE CREUX DU A, `loc_pied_droit` REND SON SEG 2.** La contreforme
    # du A est un triangle a trois segments droits, dont la base est
    # horizontale : le localisateur la designe, et ce qui l'arrete est le filtre
    # sur le signe de l'aire pose au dix-huitieme tour. C'est le piege du
    # `Aogonek` mot pour mot, et il est verifie par la passe 1 de
    # `balayage_lot4b.py` au lieu d'etre suppose fermé.
    #
    # Les deux bouts sont HORIZONTAUX, donc « gauche » et « droite » les
    # departagent et « bas » et « haut » LEVENT, comme les six du 4a.
    #
    # **CE QUI SEPARE CE SOUS-LOT DU 4a EST L'ORIENTATION DU FLANC VOISIN**, et
    # elle est mesuree : 69,3 degres a l'horizontale sur le A en romain et 80,6
    # en italique, 54,5 et 47,3 sur le X. Le coin du 4a coulissait le long d'un
    # flanc de fut vertical et partait tout droit ; ici il part de cote, donc la
    # boite s'elargit et l'approche se paie. Les deux lettres ne paient pas du
    # meme cote : le A sort a DROITE et quitte sa chasse, le X sort a GAUCHE et
    # passe son xmin sous zero. Le garde-fou est donc requis dans les DEUX sens
    # de paire, un par lettre — et c'est le trou du point ouvert 52 pris a
    # l'endroit.
    "P-A": ("A", L.loc_pied_droit),
    "P-X": ("X", L.loc_pied_gauche),
}

#: Les cibles dont le localisateur rend plus d'un bout. Le z en rend deux, comme
#: le Z, et `appliquer_etat` les traite tous — de la fin vers le debut, une
#: coupe ne touchant que ses voisins immediats, comme `lot2.appliquer`.
#:
#: Verifie plutot que suppose : sur les dix cibles anterieures, le localisateur
#: rend exactement un indice dans les huit masters des deux sources, donc le
#: passage au multi-bouts ne change rien pour elles. C'est la passe 1 de
#: `balayage_lot2.py` qui le mesure, et elle le dit master par master.
MULTI = ("Z-z",)


# --------------------------------------------------------------- operations

def _flanc_droit(seg):
    return seg["kind"] == "line"


def bascule(segs, i, theta_deg, sense):
    """La coupe tourne autour du MILIEU du bout : un coin descend, l'autre monte.

    Troisieme regime de coupe du projet, et il ne se deduit d'aucun des deux
    autres. `K.coupe` garde le coin qui fait rentrer l'autre, donc la lettre ne
    peut que maigrir ; `lot4.coupe_sortante` fait sortir un coin et laisse
    l'autre fixe, donc elle ne peut que grossir. Ici les deux coins bougent en
    sens contraire, et la matiere perdue d'un cote est regagnee de l'autre.

    C'est ce que la demande B decrit litteralement : "le cote gauche baisse un
    peu, le cote droit monte un tout petit peu". Le prix est que le coin qui
    monte franchit l'alignement — la hauteur d'x sur le n et le m — ce que la
    loi du lot 2 s'interdit. Sur le sommet du fut du t, a 620, il n'y a aucun
    alignement a franchir et le regime est gratuit.

    Les deux flancs voisins doivent etre droits : le coin qui sort coulisse le
    long du flanc prolonge, et prolonger un Bezier au-dela de son domaine rend
    une forme que le dessinateur n'a pas dessinee. Verifie sur les trois cibles
    concernees, n, m et t : les quatre flancs voisins sont droits dans les huit
    masters.
    """
    segs = [dict(s, c=list(s["c"])) for s in segs]
    n = len(segs)
    ib, ia = (i - 1) % n, (i + 1) % n
    if not (_flanc_droit(segs[ib]) and _flanc_droit(segs[ia])):
        raise ValueError("bascule : un flanc voisin est courbe, refuse")
    P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    M = (P + Q) / 2.0
    u = K.rot(K.unit(Q - P), math.radians(theta_deg) * sense)

    Ab = K.V(segs[ib]["p0"])
    Aa = K.V(segs[ia]["p3"])
    Pn = K.inter_droites(M, u, Ab, K.unit(P - Ab))
    Qn = K.inter_droites(M, u, Aa, K.unit(Q - Aa))
    if Pn is None or Qn is None:
        raise ValueError("bascule : flanc parallele a la coupe")
    Pn, Qn = K.V(Pn), K.V(Qn)

    # Un flanc droit se redresse en deplacant son bout : que le point tombe
    # dans le segment ou au-dela, le segment reste la meme droite.
    segs[ib] = dict(segs[ib], p3=tuple(float(v) for v in Pn), smooth=False)
    segs[ia] = dict(segs[ia], p0=tuple(float(v) for v in Qn), smooth=False)
    segs[i] = {"kind": "line", "p0": tuple(float(v) for v in Pn), "c": [],
               "p3": tuple(float(v) for v in Qn), "smooth": False}
    return segs


def sens_pour_coin(segs, i, coin, monte):
    """Le sens de rotation qui fait bouger le coin voulu dans le sens voulu.

    Le sens n'est pas suppose, il est essaye : c'est ce que fait deja
    `lot4.sens_pour_pointe`, et pour la meme raison. Un sens ecrit en dur dans
    une table est juste dans le master ou on l'a regarde et faux ailleurs des
    que la geometrie du glyphe s'inverse le long de l'axe, ce qui est arrive six
    fois dans ce projet.

    coin   "gauche" ou "droite", "haut" ou "bas" : lequel des deux coins du bout
    monte  True si ce coin doit avancer, False s'il doit reculer dans la lettre

    Le pivot est lu dans le calcul meme de `K.coupe` — `pivot_P = dot(w, d) < 0`
    avec `w = rot(v, th) - v` — et non retrouve en comparant les points avant et
    apres. Le premier jet faisait cela : il cherchait, parmi les deux coins du
    bout coupe, le plus proche du coin vise. Quand le coin vise recule beaucoup,
    le plus proche devient le coin fixe, et le test rendait le mauvais sens.
    Une verification doit prendre son objet du producteur, jamais le
    reconstruire apres coup — troisieme rappel du meme piege dans ce projet.

    Le nom de coin est resolu par `lot2._coin_vise_est_P`, seul producteur du
    projet, qui LEVE quand le nom ne departage pas les deux bouts du segment —
    « bas » sur un bout horizontal, « gauche » sur un bout vertical. Une copie
    locale de ce calcul finirait par diverger, et le refus a ete pose au
    vingt-septieme tour apres qu'une colonne uniforme l'ait revele.
    """
    P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    d = K.outward(segs, i)
    vise_est_P = L._coin_vise_est_P(segs, i, coin)
    v = Q - P
    for sn in (+1, -1):
        th = math.radians(20.0) * sn
        pivot_P = float(np.dot(K.rot(v, th) - v, d)) < 0
        recule_est_P = not pivot_P          # le coin qui bouge est l'autre
        if (recule_est_P == vise_est_P) != monte:
            return sn
    return None


def sens_pour_sortie(segs, i, coin):
    """Le sens de rotation qui fait sortir le coin nomme, pour une sortante.

    Lu dans le calcul de `lot4.coupe_sortante` — `sortie_par_Q = dot(w, d) > 0`
    — et non retrouve en comparant les points apres coup.

    Le nom de coin passe par `lot2._coin_vise_est_P`, qui leve quand il ne
    departage pas les deux bouts : c'est ce refus qui separe les deux lectures
    de la demande du lot 3, et sans lui la mesure rendait le meme deplacement
    pour les deux.
    """
    P, Qp = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    d = K.outward(segs, i)
    vise_est_Q = not L._coin_vise_est_P(segs, i, coin)
    v = Qp - P
    for sn in (+1, -1):
        th = math.radians(20.0) * sn
        if (float(np.dot(K.rot(v, th) - v, d)) > 0) == vise_est_Q:
            return sn
    return None


def angle_pour_sortie(segs, i, sn, cible):
    """L'angle de sortante qui deplace le coin sortant de `cible` unites.

    `lot4.angle_pour_depassement` mesure l'ecart a une ligne horizontale, ce qui
    suppose que le coin sort vers le haut ou vers le bas. Le bout du crochet du f
    sort lateralement : son flanc voisin est le sommet du crochet, horizontal,
    donc le coin avance a hauteur constante et un ecart mesure en ordonnee reste
    nul quel que soit l'angle — la dichotomie ne convergerait sur rien.

    La grandeur mesuree ici est le chemin parcouru par le coin, qui vaut la
    profondeur sous la ligne quand le flanc est vertical, et l'avance quand il
    est horizontal. C'est la grandeur qui se voit dans les deux cas.
    """
    P0, Q0 = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])

    def chemin(th):
        try:
            ap = Q.coupe_sortante(segs, i, th, sn)
        except ValueError:
            return None
        Pn, Qn = K.V(ap[i]["p0"]), K.V(ap[i]["p3"])
        return max(float(np.hypot(*(Pn - P0))), float(np.hypot(*(Qn - Q0))))

    lo, hi = 0.5, 45.0
    if chemin(lo) is None:
        return None
    haut = chemin(hi)
    if haut is not None and haut < cible:
        return hi
    for _ in range(24):
        mil = (lo + hi) / 2.0
        v = chemin(mil)
        if v is None or v > cible:
            hi = mil
        else:
            lo = mil
    return lo


# ---------------------------------------------------------------- les etats
#
# (cle, etiquette, fonction) — la fonction prend (segs, i) et rend segs.
# Rien n'est fige : ce sont les candidats de la planche du vingtieme tour.

def _rentrante(theta, coin, monte=False):
    def f(segs, i):
        sn = sens_pour_coin(segs, i, coin, monte)
        if sn is None:
            raise ValueError("aucun sens ne fait bouger le coin demande")
        return K.coupe(segs, i, theta, sn, 0.0)
    return f


def _bascule(theta, coin_bas):
    """Bascule dont le coin `coin_bas` descend."""
    def f(segs, i):
        for sn in (+1, -1):
            essai = bascule(segs, i, theta, sn)
            P, Q = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
            Pn, Qn = K.V(essai[i]["p0"]), K.V(essai[i]["p3"])
            gauche_avant, gauche_apres = (
                (P, Pn) if float(P[0]) < float(Q[0]) else (Q, Qn))
            descend = float(gauche_apres[1]) < float(gauche_avant[1])
            if descend == (coin_bas == "gauche"):
                return essai
        raise ValueError("aucun sens ne fait descendre le coin demande")
    return f


def _sortante(cible, coin):
    """Le coin nomme sort de son alignement de `cible` unites."""
    def f(segs, i):
        sn = sens_pour_sortie(segs, i, coin)
        if sn is None:
            raise ValueError("aucun sens ne fait sortir le coin demande")
        th = angle_pour_sortie(segs, i, sn, cible)
        if th is None:
            raise ValueError("aucune sortante possible sur ce bout")
        return Q.coupe_sortante(segs, i, th, sn)
    return f


def _pointe(tirage, saillie):
    def f(segs, i):
        return K.pointe(segs, i, tirage, saillie)
    return f


def _sens_du_Z():
    """Le sens de rotation que la table applique deja au Z capitale.

    Lu dans `lot2.LOT2` et non recopie. Le z bas de casse doit recevoir ce que
    le Z a, et un sens recopie cesserait d'etre le bon le jour ou l'entree du Z
    changerait, sans que rien le signale — une table du projet a deja diverge de
    sa documentation, et une planche a deja decrit des formes qu'elle
    n'affichait plus.
    """
    for entree in L.LOT2:
        if entree[0] == "Z":
            return entree[2]
    raise ValueError("aucune entree Z dans lot2.LOT2 : le z ne peut pas "
                     "heriter d'un sens qui n'existe pas")


def _comme_Z(theta):
    """La coupe du Z appliquee au bout designe, au sens de sa table."""
    sn = _sens_du_Z()

    def f(segs, i):
        return K.coupe(segs, i, theta, sn, 0.0)
    return f


ETATS = {
    # A. le r. Nicolas le range dans les lettres reussies : la demande porte sur
    #    le bout du bras et sur rien d'autre. Le cote haut du bout doit avancer
    #    vers la droite, donc c'est le coin bas qui recule.
    "A": [
        ("A0", "brut", None),
        ("A1", "coupe 20, le bas recule", _rentrante(20.0, "bas")),
        ("A2", "coupe 12, le bas recule", _rentrante(12.0, "bas")),
        ("A3", "coupe 20, le haut recule", _rentrante(20.0, "haut")),
    ],
    # B et C. le n et le m. Deux regimes, et c'est la question du tour : la loi
    #    du lot 2 tient la hauteur d'x par le coin qui ne bouge pas ; la bascule
    #    la franchit de quelques unites.
    "B": [
        ("B0", "brut", None),
        ("B1", "coupe 20, le gauche descend", _rentrante(20.0, "gauche")),
        ("B2", "coupe 12, le gauche descend", _rentrante(12.0, "gauche")),
        ("B3", "bascule 20, gauche bas droite haut", _bascule(20.0, "gauche")),
        ("B4", "bascule 12, gauche bas droite haut", _bascule(12.0, "gauche")),
    ],
    "D1": [
        ("D0", "brut", None),
        ("D1a", "coupe 20, comme le l", _rentrante(20.0, "haut")),
        ("D1b", "coupe 20, l'autre sens", _rentrante(20.0, "bas")),
        ("D1c", "coupe 12, comme le l", _rentrante(12.0, "haut")),
    ],
    "D2": [
        ("D2-0", "brut", None),
        ("D2a", "coupe 20, le gauche descend", _rentrante(20.0, "gauche")),
        ("D2b", "coupe 20, le droit descend", _rentrante(20.0, "droite")),
        ("D2c", "bascule 20, gauche bas droite haut", _bascule(20.0, "gauche")),
    ],
    "E": [
        ("E0", "brut", None),
        ("E1", "coupe 20, le bas recule", _rentrante(20.0, "bas")),
        ("E2", "coupe 20, le haut recule", _rentrante(20.0, "haut")),
        ("E3", "pointe, reglage cedille 3,5 / 45", _pointe(3.5, 45.0)),
        ("E4", "pointe douce 1,0 / 25", _pointe(1.0, 25.0)),
    ],
    # N. le pied droit du n, vingt-et-unieme tour. Nicolas a tranche : la pointe
    #    plonge sous la ligne de base. Le coin bas droit descend en coulissant le
    #    long du flanc droit du fut, qui est vertical, donc il descend tout droit
    #    et la boite ne s'elargit pas. Le pied devient une diagonale et l'angle
    #    du coin se ferme a mesure qu'il plonge.
    #
    #    C'est une sortie du perimetre du lot 2, assumee : la ligne de base est
    #    un alignement, et la loi s'interdisait d'y toucher. Le lot 4 le fait
    #    deja en titrage, a 32 unites pour les bas de casse.
    "N": [
        ("N0", "brut", None),
        ("N1", "plonge de 12, le debord des rondes", _sortante(12.0, "droite")),
        ("N2", "plonge de 22", _sortante(22.0, "droite")),
        ("N3", "plonge de 32, la valeur du titrage", _sortante(32.0, "droite")),
    ],
    # F. le bout du crochet du f, vingt-et-unieme tour. Nicolas a tranche : le
    #    geste de E1, obtenu en faisant avancer le coin haut vers la droite au
    #    lieu de faire reculer le coin bas. Le glyphe gagne de la matiere au lieu
    #    d'en perdre, et il mange son approche droite.
    "F": [
        ("F0", "brut", None),
        ("F1", "avance de 12", _sortante(12.0, "haut")),
        ("F2", "avance de 25", _sortante(25.0, "haut")),
        ("F3", "avance de 40", _sortante(40.0, "haut")),
    ],
    # Lot 1 du vingt-cinquieme tour. Nicolas a demande, sur la planche
    # d'alphabet : que le cote gauche du pied gauche du m et du M descende sous
    # la ligne, en miroir du n, et que le cote gauche de la hampe du f en fasse
    # autant. Le geste est celui de l'etat N, retenu au vingt-deuxieme tour a 22
    # unites, applique au coin gauche.
    #
    # Les profondeurs candidates sont les trois du n, plus 44 sur le M seul :
    # c'est la valeur des capitales en titrage, et la question de savoir si une
    # capitale plonge de la meme valeur absolue qu'un bas de casse ou de sa
    # valeur propre n'est pas tranchee. Le lot 4 l'a tranchee pour lui-meme,
    # 44 contre 32, sur un argument de proportion et non de securite.
    "P-f": [
        ("Pf0", "brut", None),
        ("Pf1", "plonge de 12, le debord des rondes", _sortante(12.0, "gauche")),
        ("Pf2", "plonge de 22, la valeur du n", _sortante(22.0, "gauche")),
        ("Pf3", "plonge de 32, la valeur du titrage", _sortante(32.0, "gauche")),
    ],
    "P-m": [
        ("Pm0", "brut", None),
        ("Pm1", "plonge de 12, le debord des rondes", _sortante(12.0, "gauche")),
        ("Pm2", "plonge de 22, la valeur du n", _sortante(22.0, "gauche")),
        ("Pm3", "plonge de 32, la valeur du titrage", _sortante(32.0, "gauche")),
    ],
    "P-M": [
        ("PM0", "brut", None),
        ("PM1", "plonge de 12, le debord des rondes", _sortante(12.0, "gauche")),
        ("PM2", "plonge de 22, la valeur du n", _sortante(22.0, "gauche")),
        ("PM3", "plonge de 32, la valeur du titrage bas de casse",
         _sortante(32.0, "gauche")),
        ("PM4", "plonge de 44, la valeur du titrage capitale",
         _sortante(44.0, "gauche")),
    ],
    # Lot 2 : les rentrants. Un coin recule, l'autre tient l'alignement, donc la
    # lettre ne peut que maigrir et la boite ne peut pas s'elargir. Les deux
    # angles sont ceux que le projet emploie deja et non des valeurs posees ici :
    # 20 degres est l'angle du systeme entier, deduit de la diagonale du A ;
    # 12 degres est celui retenu sur le haut du fut gauche du n et du m au
    # vingt-deuxieme tour, seul etat ou le coin franchissait la hauteur d'x sans
    # que la boite bouge dans aucun master.
    #
    # Le coin nomme est celui qui DESCEND, l'autre tenant l'ascendante a 796.
    # C'est la demande de Nicolas, lue sur la planche d'alphabet : le droit sur
    # le b et sur le l, le gauche sur le d.
    "H-b": [
        ("Hb0", "brut", None),
        ("Hb1", "coupe 20, le droit descend", _rentrante(20.0, "droite")),
        ("Hb2", "coupe 12, le droit descend", _rentrante(12.0, "droite")),
    ],
    "H-d": [
        ("Hd0", "brut", None),
        ("Hd1", "coupe 20, le gauche descend", _rentrante(20.0, "gauche")),
        ("Hd2", "coupe 12, le gauche descend", _rentrante(12.0, "gauche")),
    ],
    "H-l": [
        ("Hl0", "brut", None),
        ("Hl1", "coupe 20, le droit descend", _rentrante(20.0, "droite")),
        ("Hl2", "coupe 12, le droit descend", _rentrante(12.0, "droite")),
    ],
    # Le z recoit ce que le Z a deja : ses deux bouts libres, celui de la barre
    # haute a gauche et celui de la barre basse a droite, et non ses jonctions de
    # diagonale. Le sens est celui de la table du Z, horaire, et il est LU dans
    # `lot2.LOT2` plutot que recopie : un sens ecrit en dur est juste dans le
    # master ou on l'a regarde et faux ailleurs des que la geometrie s'inverse le
    # long de l'axe, ce qui est arrive six fois dans ce projet.
    #
    # Ces deux bouts sont verticaux : le coin mobile coulisse le long d'une arete
    # horizontale, donc la montee est exactement nulle et l'alignement est tenu
    # par le coin qui ne bouge pas. C'est ce qui a fait entrer le T et le Z dans
    # la coupe texte au onzieme tour, et le z est dans le meme cas.
    "Z-z": [
        ("Zz0", "brut", None),
        ("Zz1", "coupe 20, le sens du Z", _comme_Z(20.0)),
        ("Zz2", "coupe 12, le sens du Z", _comme_Z(12.0)),
    ],
    # Lot 3 : la descendante, et ce qui n'en est pas.
    #
    # **LA DEMANDE N'A PAS DEUX LECTURES, ET C'EST LA GEOMETRIE QUI LE DIT.**
    # « Le cote bas depasse vers la gauche » paraissait se lire de deux facons,
    # une plongee sous l'alignement ou une avance laterale, et Nicolas a demande
    # que les deux soient instruites. La passe 2 du balayage les a essayees :
    # le coin sortant coulisse le long du flanc voisin PROLONGE, donc c'est
    # l'orientation de ce flanc qui decide, et elle ne laisse jamais le choix.
    #
    #   p et Y : le bout est HORIZONTAL, ses deux flancs sont verticaux, donc
    #            tout coin qui sort PLONGE. L'avance laterale est impossible, et
    #            « bas » n'y designe meme aucun des deux coins.
    #   y      : le bout est VERTICAL, ses deux flancs sont horizontaux, donc
    #            tout coin qui sort AVANCE lateralement. La plongee est
    #            impossible, et « gauche » n'y designe aucun des deux coins.
    #
    # `lot2._coin_vise_est_P` leve maintenant sur un nom de coin que le bout ne
    # departage pas : sans ce refus, « bas » sur le bout du p designait le coin
    # droit en silence et la mesure rendait le meme deplacement pour les deux
    # « lectures ». Sixieme fois qu'une colonne uniforme revele un defaut dans
    # ce projet.
    #
    # Ce qui reste a trancher n'est donc pas la direction, c'est QUEL COIN sort
    # et de combien. Les deux coins sont sur la planche.
    #
    # **Consequence a ne pas perdre sur le y : son geste ne descend pas d'une
    # unite.** Le point ouvert 21 ne le concerne pas ; en revanche il mange son
    # approche gauche, comme le bout du crochet du f mange sa droite.
    #
    # Les valeurs de sortie ne sont pas posees pour l'occasion :
    #   12  le debord optique des rondes, mesure a 12 unites dans cette police.
    #   22  la valeur du pied droit du n et du pied gauche du m.
    #   24  deux fois le debord, soit `approches.JOUR_MIN`, le seuil du projet
    #       depuis le dix-septieme tour. La passe 4 montre que c'est aussi la
    #       plongee gratuite du p en ExtraLight, celle au-dela de laquelle il
    #       devient le plancher du repertoire servi.
    #   32  la valeur des bas de casse en titrage, et celle du M et du f au
    #       lot 1.
    #   44  la valeur des capitales en titrage. Sur le Y seulement, et c'est sa
    #       propre prescription de titrage, arretee au onzieme tour.
    "J-p": [
        ("Jp0", "brut", None),
        ("Jp1", "le gauche plonge de 12, le debord des rondes",
         _sortante(12.0, "gauche")),
        ("Jp2", "le gauche plonge de 22, la valeur du pied du n",
         _sortante(22.0, "gauche")),
        ("Jp3", "le gauche plonge de 24, JOUR_MIN et le gratuit",
         _sortante(24.0, "gauche")),
        ("Jp4", "le gauche plonge de 32, le titrage bas de casse",
         _sortante(32.0, "gauche")),
        ("Jp5", "le DROIT plonge de 24, l'autre coin",
         _sortante(24.0, "droite")),
    ],
    "Q-y": [
        ("Qy0", "brut", None),
        ("Qy1", "le bas avance de 12, le debord des rondes",
         _sortante(12.0, "bas")),
        ("Qy2", "le bas avance de 22, la valeur du pied du n",
         _sortante(22.0, "bas")),
        ("Qy3", "le bas avance de 24, JOUR_MIN", _sortante(24.0, "bas")),
        ("Qy4", "le bas avance de 32, le titrage bas de casse",
         _sortante(32.0, "bas")),
        # Retenu par Nicolas au vingt-septieme tour : « Qy4+ », soit une avance
        # plus grande que le plus grand des candidats. 40 unites n'etait donc
        # pas mesure quand il l'a demande, et l'etat est ajoute pour l'etre.
        ("Qy4p", "le bas avance de 40, retenu par Nicolas",
         _sortante(40.0, "bas")),
        ("Qy5", "le HAUT avance de 24, l'autre coin",
         _sortante(24.0, "haut")),
    ],
    "Y-Y": [
        ("YY0", "brut", None),
        ("YY1", "le gauche plonge de 12, le debord des rondes",
         _sortante(12.0, "gauche")),
        ("YY2", "le gauche plonge de 22, la valeur du pied du n",
         _sortante(22.0, "gauche")),
        ("YY3", "le gauche plonge de 24, JOUR_MIN", _sortante(24.0, "gauche")),
        ("YY4", "le gauche plonge de 32, le titrage bas de casse",
         _sortante(32.0, "gauche")),
        ("YY5", "le gauche plonge de 44, le titrage capitale",
         _sortante(44.0, "gauche")),
        ("YY6", "le DROIT plonge de 24, l'autre coin",
         _sortante(24.0, "droite")),
        # Retenu par Nicolas au vingt-septieme tour : « YY5 mais dans l'autre
        # sens, la droite qui descend plutot que la gauche ». Le coin droit
        # n'avait ete mesure qu'a 24 unites, et le garde-fou n'avait teste que
        # le coin gauche : cet etat est ajoute pour etre mesure des deux cotes.
        #
        # Le coin droit descend du cote de la lettre SUIVANTE, quand le gauche
        # descend du cote de la precedente. Le voisinage n'est donc pas le meme,
        # et le zero du coin gauche ne dit rien de celui-ci.
        ("YY7", "le DROIT plonge de 44, retenu par Nicolas",
         _sortante(44.0, "droite")),
    ],
}


# ------------------------------------------------------- lot 4a : par le haut
#
# Les cinq profondeurs candidates sont celles des lots 1 a 3, et elles sont
# reprises telles quelles pour que les etats se comparent d'un lot a l'autre :
# 12 le debord optique des rondes, 22 le pied droit du n, 24 `approches.JOUR_MIN`,
# 32 le titrage bas de casse, 44 le titrage capitale. Aucune n'est inventee ici.
#
# **Le regime est en unites, et c'est un choix de cadrage de Nicolas au
# vingt-huitieme tour**, pas un defaut : le point ouvert 51 reste ouvert et
# fige par defaut en unites, comme les lots 1 a 3. Ce que ca coute est mesure et
# connu — la largeur du bout de hampe passe de 54 unites en ExtraLight a 165 a
# l'ExtraBold, donc le pied penche trois fois plus dans les clairs.
#
# Un sixieme etat sur le h et le k porte 88 unites, l'ecart mesure entre le bout
# de hampe a 708 et l'ascendante DECLAREE a 796. Il n'est pas un candidat : il
# est la pour chiffrer ce que « monter jusqu'a la metrique » couterait, et pour
# que le refus vienne de la geometrie et non de la borne de l'outil. Le lot 3 a
# paye une borne a 60 unites qui se faisait passer pour un fait de la lettre.
#
# L'etat « l'autre coin » de chaque cible ne sert pas a etre choisi. Il prouve
# que le nom de coin departage vraiment les deux bouts, ce que
# `lot2._coin_vise_est_P` refuse depuis le vingt-septieme tour, et il montre le
# geste en miroir — sur un bout horizontal les deux coins coulissent le long de
# flancs de meme orientation, donc ils sortent dans la meme direction, et ce qui
# se tranche est LEQUEL des deux sort.

def _monte(cle, coin, autre, extra=()):
    """Les six etats d'une cible du lot 4a, dans l'ordre des profondeurs."""
    p = cle.replace("-", "")
    dit = {"gauche": "gauche", "droite": "droit"}
    coin, nom_coin = coin, dit[coin]
    ets = [(p + "0", "brut", None)]
    for n, (u, quoi) in enumerate([(12.0, "le debord des rondes"),
                                   (22.0, "la valeur du pied du n"),
                                   (24.0, "JOUR_MIN"),
                                   (32.0, "le titrage bas de casse"),
                                   (44.0, "le titrage capitale")], start=1):
        ets.append((f"{p}{n}", f"le {nom_coin} monte de {u:.0f}, {quoi}",
                    _sortante(u, coin)))
    for u, quoi in extra:
        ets.append((f"{p}{len(ets)}", f"le {nom_coin} monte de {u:.0f}, {quoi}",
                    _sortante(u, coin)))
    nom_autre = {"gauche": "GAUCHE", "droite": "DROIT"}[autre]
    ets.append((f"{p}{len(ets)}", f"le {nom_autre} monte de 24, l'autre coin",
                _sortante(24.0, autre)))
    return ets


#: Ce que « monter jusqu'a l'ascendante declaree » demanderait, sur les deux
#: hampes : 796 − 708, mesure au vingt-sixieme tour et reverifie ici. Non
#: candidat, voir le commentaire ci-dessus.
JUSQU_ASC = ((88.0, "l'ascendante DECLAREE a 796, non candidat"),)

ETATS["H-h"] = _monte("H-h", "droite", "gauche", JUSQU_ASC)
ETATS["H-k"] = _monte("H-k", "gauche", "droite", JUSQU_ASC)
ETATS["S-N"] = _monte("S-N", "droite", "gauche")
ETATS["S-H"] = _monte("S-H", "droite", "gauche")

# Les deux pieds DESCENDENT : ce sont les moities basses des prescriptions de
# titrage du N et du H, mesurees ici pour que l'arbitrage puisse les reprendre.
# Meme jeu de profondeurs, meme raison, sens inverse.
ETATS["P-N"] = [(c.replace("monte", "plonge"), e.replace("monte", "plonge"), f)
                for c, e, f in _monte("P-N", "gauche", "droite")]
ETATS["P-H"] = [(c.replace("monte", "plonge"), e.replace("monte", "plonge"), f)
                for c, e, f in _monte("P-H", "gauche", "droite")]

# Sous-lot 4b : les deux diagonales. Meme jeu de profondeurs que les lots 1 a
# 4a, et c'est le choix de cadrage de Nicolas au vingt-neuvieme tour — un meme
# nombre ECRIT sur les deux lettres, en unites, ce qui fige le point ouvert 51
# pour la cinquieme fois.
#
# **CE NOMBRE N'EST PAS LA PLONGEE.** `angle_pour_sortie` vise le chemin
# parcouru par le coin, et sur un flanc oblique ce chemin se partage entre une
# plongee et une avance laterale. Mesure : a 24 unites ecrites, le A plonge de
# 22,5 et avance de 8,5 en romain, le X plonge de 19,5 et avance de 13,9. Le
# meme nombre ne donne donc PAS la meme profondeur sur les deux lettres, et
# l'ecart va de 3 unites a 24 a 5,4 unites a 44. Le 4a n'avait pas ce probleme,
# ses six flancs etant verticaux : la plongee y valait la sortie a 0,5 unite
# pres. La passe 2 rend les trois grandeurs separement, parce qu'une colonne qui
# n'en rend qu'une a deja fait lire la longueur d'un bout pour ce que la coupe
# enlevait, sur le z au vingt-sixieme tour.
ETATS["P-A"] = [(c.replace("monte", "plonge"), e.replace("monte", "plonge"), f)
                for c, e, f in _monte("P-A", "droite", "gauche")]
ETATS["P-X"] = [(c.replace("monte", "plonge"), e.replace("monte", "plonge"), f)
                for c, e, f in _monte("P-X", "gauche", "droite")]

ETATS["C"] = [(c.replace("B", "C"), e, f) for c, e, f in ETATS["B"]]


# -------------------------------------------------------------- application

def appliquer_etat(layer, cle, fn):
    """Applique un etat au calque, en place, et rend ce qu'il a place.

    Rend (contour, indice, P, Q) : les deux coins du bout apres traitement, pris
    du producteur et non retrouves apres coup. C'est la sortie du piege tombe
    trois fois dans ce projet — un bout coupe n'est plus vertical, un bout mis
    en pointe n'est plus un segment droit, et le localisateur qui le retrouvait
    designe alors un segment quelconque. `lot2.appliquer` et
    `souscrits.appliquer_etat` rendent tous deux leur pointe pour la meme
    raison.

    Quand le localisateur rend plusieurs bouts, tous sont traites et la place
    rendue est celle du premier dans l'ordre du contour. Les indices sont
    parcourus de la fin vers le debut, une coupe ne touchant que ses voisins
    immediats : c'est ce que `lot2.appliquer` fait depuis le onzieme tour pour
    les deux bouts de barre du T et les deux bouts libres du Z.
    """
    nom, loc = LOCS[cle]
    for ip, p in enumerate(L.paths(layer)):
        segs = K.to_segs(p)
        if K.area(segs) < 0:
            continue
        idx = loc(segs)
        if not idx:
            continue
        if fn is not None:
            for i in sorted(idx, reverse=True):
                segs = fn(segs, i)
        i = idx[0]
        layer.shapes[layer.shapes.index(p)] = K.from_segs(segs)
        return (ip, i, tuple(float(v) for v in segs[i]["p0"]),
                tuple(float(v) for v in segs[i]["p3"]))
    return None


def segs_etat(layer, cle, fn):
    """Les contours du calque apres application, sans toucher au calque.

    Rend (liste de listes de segments, place) ou `place` est ce que rend
    `appliquer_etat`. Sert aux planches, qui doivent pouvoir dessiner un etat
    sans modifier la source — `copy.deepcopy` sur un objet glyphsLib recopie la
    police entiere, d'ou le passage par des listes de segments.
    """
    out, place = [], None
    for ip, p in enumerate(L.paths(layer)):
        segs = K.to_segs(p)
        if K.area(segs) > 0 and place is None:
            nom, loc = LOCS[cle]
            idx = loc(segs)
            if idx:
                if fn is not None:
                    for i in sorted(idx, reverse=True):
                        segs = fn(segs, i)
                i = idx[0]
                place = (ip, i, tuple(float(v) for v in segs[i]["p0"]),
                         tuple(float(v) for v in segs[i]["p3"]))
        out.append(segs)
    return out, place


# ------------------------------------------------------ le r en forme de R
#
# Demande de Nicolas au vingt-et-unieme tour, en remplacement de la coupe du
# bout du bras : essayer un R capitale ramene a l'echelle d'une minuscule.
# Ce n'est plus une terminaison, c'est une lettre derivee, et l'outillage
# existe — c'est celui du lot 3, qui derive les 44 petites capitales.

def r_en_R(font, master_id, hauteur=496.0, largeur=1.0, cache=None,
           journal=None):
    """Un calque de r dessine comme un R, a la hauteur voulue.

    La compensation de graisse est celle du lot 3 : la source est prise plus
    haut sur l'axe pour que le fut de la lettre reduite tombe sur le fut du bas
    de casse, et non sur celui de la capitale. Une lettre qui descend de 668 a
    496 sans compensation sort 26 % trop maigre et fait un trou dans la ligne.
    """
    import lot3
    cache = cache or lot3.mesures(font)
    return lot3.petite_capitale(font, "R", master_id, hauteur,
                                largeur=largeur, sb=0.0, journal=journal,
                                _cache=cache)


def r_en_R_chasse(font, master_id, chasse, hauteur=496.0, cache=None,
                  journal=None, tours=8):
    """Le meme, resserre pour tomber sur une chasse voulue.

    Le facteur de largeur ne se calcule pas d'un coup : le resserrement change
    la compensation de graisse, qui change la source, qui change la largeur. On
    itere, et huit tours suffisent a tomber a l'unite.
    """
    import lot3
    cache = cache or lot3.mesures(font)
    larg = 1.0
    lay = None
    for _ in range(tours):
        j = []
        lay = lot3.petite_capitale(font, "R", master_id, hauteur,
                                   largeur=larg, sb=0.0, journal=j,
                                   _cache=cache)
        if abs(lay.width - chasse) < 1.0:
            break
        larg *= chasse / lay.width
    if journal is not None:
        journal.extend(j)
        journal.append({"largeur": larg, "chasse": lay.width})
    return lay, larg


def distance_rn_m(font, master_id, px=120, rayon=3.0):
    """La distance a acuite reduite entre le groupe "rn" et la lettre "m".

    La mesure de confusion du projet compare deux glyphes isoles. Elle ne peut
    pas repondre a la question rn/m, qui oppose un groupe de deux lettres a une
    lettre : le specimen du corpus a montre qu'a un flou de 3,0 "rn m" se lit
    "m m", et c'est le couple entier qui se confond, pas le r avec le m.

    Le r et le n sont donc composes avec leurs chasses reelles avant d'etre
    compares au m. Un r plus large ecarte le n d'autant, ce que la comparaison
    de glyphes isoles ne voit pas du tout — et c'est justement ce qui change
    quand le r prend la largeur d'un R.
    """
    import dessin as D
    import mesure_O as MO

    def lay(nom):
        for l in font.glyphs[nom].layers:
            if l.layerId == master_id:
                return l
        return None

    lr, ln, lm = lay("r"), lay("n"), lay("m")
    groupe = [c for p in L.paths(lr) for c in [D.flatten(p)]]
    dec = float(lr.width)
    groupe += [[(x + dec, y) for x, y in D.flatten(p)] for p in L.paths(ln)]
    seul = [D.flatten(p) for p in L.paths(lm)]
    return MO.confusion((groupe, []), (seul, []), px, rayon)


class avec_etat:
    """Applique un etat le temps d'un bloc, puis remet le calque comme il etait.

    Une planche qui veut composer un mot doit modifier le glyphe, puis le
    rendre. Recharger la police a chaque etat coute une seconde et demie, et
    `copy.deepcopy` sur un objet glyphsLib recopie la police entiere — cinquante
    secondes pour huit calques, piege tombe deux fois dans la meme session. On
    sauvegarde donc des listes de segments, `K.to_segs`, et on reconstruit par
    `K.from_segs`, qui rend des dictionnaires nus et reconstruit a 0,1 unite
    pres.
    """

    def __init__(self, layer, cle, fn):
        self.layer, self.cle, self.fn = layer, cle, fn
        self.sauve = None
        self.place = None

    def __enter__(self):
        self.sauve = [K.to_segs(p) for p in L.paths(self.layer)]
        self.place = appliquer_etat(self.layer, self.cle, self.fn)
        return self.place

    def __exit__(self, *exc):
        chemins = L.paths(self.layer)
        for p, segs in zip(chemins, self.sauve):
            self.layer.shapes[self.layer.shapes.index(p)] = K.from_segs(segs)
        return False


def polyligne(segs, n=24):
    """Contour en liste de segments -> polyligne, en unites de dessin."""
    pts = []
    for s in segs:
        if s["kind"] == "line":
            pts.append((float(s["p3"][0]), float(s["p3"][1])))
        else:
            for j in range(1, n + 1):
                p = K.bez(s, j / n)
                pts.append((float(p[0]), float(p[1])))
    return pts


# ------------------------------------------------------------------ mesures

def boite(liste_segs):
    xs, ys = [], []
    for segs in liste_segs:
        for s in segs:
            for t in np.linspace(0.0, 1.0, 17):
                p = K.bez(s, float(t))
                xs.append(float(p[0]))
                ys.append(float(p[1]))
    return min(xs), min(ys), max(xs), max(ys)


def encre(liste_segs):
    return sum(K.area(segs) for segs in liste_segs)


def angle_bout(P, Qp):
    """L'angle de la coupe avec l'horizontale, en degres, dans [0, 180)."""
    dx = float(Qp[0]) - float(P[0])
    dy = float(Qp[1]) - float(P[1])
    return math.degrees(math.atan2(dy, dx)) % 180.0


def hors_chasse(liste_segs, width):
    """Ce qui sort de la chasse a droite, en unites.

    La colonne qui a decide l'ogonek au dix-huitieme tour. Une boite qui grandit
    a droite ne dit rien tant qu'on ne la rapporte pas a la chasse : c'est le
    blanc de l'approche qui est mange d'abord, et la voisine n'est atteinte que
    lorsque le depassement excede ce blanc.
    """
    return max(0.0, boite(liste_segs)[2] - float(width))


def mesurer(layer, cle, fn, alignement=None):
    """Ce que l'etat coute et ce qu'il place.

    `alignement` est la valeur y que la terminaison portait — 496 pour le n et
    le m, 0 pour rien. Le depassement au-dessus est ce que la loi du lot 2
    s'interdit, et c'est le chiffre a mettre sous les yeux de Nicolas.
    """
    base, _ = segs_etat(layer, cle, None)
    apres, place = segs_etat(layer, cle, fn)
    x0, y0, x1, y1 = boite(base)
    a0, b0, a1, b1 = boite(apres)
    e0, e1 = encre(base), encre(apres)
    out = dict(
        boite_avant=(x0, y0, x1, y1), boite_apres=(a0, b0, a1, b1),
        d_bas=b0 - y0, d_haut=b1 - y1, d_gauche=a0 - x0, d_droite=a1 - x1,
        encre=(e1 / e0 if e0 else float("nan")),
        place=place,
        hors_chasse=hors_chasse(apres, layer.width),
        hors_chasse_avant=hors_chasse(base, layer.width),
    )
    if place is not None:
        P, Qp = place[2], place[3]
        out["angle"] = angle_bout(P, Qp)
        if alignement is not None:
            out["depassement"] = max(float(P[1]), float(Qp[1])) - alignement
            out["retrait"] = alignement - min(float(P[1]), float(Qp[1]))
    return out
