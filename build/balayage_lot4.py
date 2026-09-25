#!/usr/bin/env python3
"""
Temoin, lot 4a des vingt-deux gestes : les depassements PAR LE HAUT.

Ne dessine rien. Quatre passes, a jouer par numero en argument.

  1  l'inventaire des six bouts vises, les localisateurs sur les huit masters
     des deux sources, l'ordonnee du bout et l'orientation du flanc voisin.
     C'est ici que se lit pourquoi `loc_sommet_fut` ne peut pas servir au N ni
     au H, et que se remesure l'ascendante annoncee a 796 et mesuree a 708.
  2  les sorties candidates en unites : boite, hors chasse, encre, topologie a
     deux resolutions, et le depassement REEL contre l'ordonnee du bout brut.
     Elle repond a une question que la passation a deja fait rater : est-ce que
     la boite bouge, oui ou non, et dans quel master.
  3  l'interligne PAR LE HAUT, le miroir de la passe 4 du lot 3 : le plafond
     reel du repertoire servi, le jour aux quatre interlignes du CSS du site, et
     la montee gratuite de chaque cible avant qu'elle ne devienne le plafond.
  4  le garde-fou de la bande pleine sur les 71 voisins, avec temoin. Ce
     sous-lot fait SORTIR de la matiere, donc la passe est requise.

CE QUE LE SOUS-LOT DEMANDE. Nicolas a regarde la planche d'alphabet du
vingt-cinquieme tour et demande, dans la famille « franchit l'ascendante vers
le haut » : « h bout de hampe le droit monte ; k bout de hampe le gauche
monte ». Puis, dans « depasse en capitale » : « N en haut a droite le droit
depasse ; H en haut a gauche et en bas a droite ».

**LA DEMANDE SUR LE H NOMMAIT L'AUTRE DIAGONALE, ET NICOLAS A TRANCHE.** « En
haut a gauche et en bas a droite », c'est hg + bd ; la prescription de titrage
arretee au neuvieme tour tient « bg et hd seulement, comme le N ». Ce sont les
deux diagonales opposees du meme glyphe. Interroge au vingt-huitieme tour,
Nicolas a retenu **bg + hd, celle du titrage**. Le H de ce sous-lot est donc le
H du titrage, et non la lettre de la liste.

Le N, lui, ne pose pas ce probleme : la demande ne nomme que hd, qui est la
moitie haute de sa prescription de titrage — un sous-ensemble, pas une
contradiction. `P-N` est mesure quand meme, pour que l'arbitrage puisse
reprendre la moitie basse ou la laisser, et le dire.

CE QUE LE SOUS-LOT 4a N'EST PAS. Le lot 4 entier fait six glyphes quand le lot
3 en faisait trois et a pris une session. Il est coupe en deux au
vingt-huitieme tour, sur decision de Nicolas, et la coupure est GEOMETRIQUE :

  4a  h, k, N, H — les six bouts sont horizontaux et leurs coins coulissent le
      long d'un flanc de fut, donc VERTICAL, donc le coin part tout droit.
  4b  A, X — leurs bouts sont portes par une diagonale, donc le coin part
      surtout de cote, et une sortante sur un flanc diagonal MANGE L'APPROCHE :
      16 unites de boite sur le K, 54 sur le Y, l'approche droite du Y de 0 a
      −20, mesurees au septieme tour. Ce n'est pas le meme prix.

LA REFERENCE EST L'ETAT SERVI, ET C'EST LA CORRECTION LA PLUS COUTEUSE DU
VINGT-SEPTIEME TOUR. La passe 5 du lot 3 mesurait d'abord contre Atkinson brut
et rendait `q+y` en couloir negatif dans les huit masters ; mesuree sur
`Temoin.glyphs`, qui porte la queue du q coupee par le lot 2 depuis le onzieme
tour, la meme paire ne passe negatif que dans deux. **Un verdict rouge sur huit
masters est devenu un verdict rouge sur deux**, et la decision n'etait pas la
meme. La passe 4 d'ici part de l'etat servi.

UN DEFAUT DE LA PASSE 5 DU LOT 3, TROUVE AU VINGT-HUITIEME TOUR ET EVITE ICI.
`balayage_lot3.py 5 --cible Q-y` ne peut plus s'executer : il repose la
sortante sur un bout que `lot2.LOT2` a deja fait sortir, et `_sortante` leve
« aucune sortante possible sur ce bout ». C'est le refus de
`planche_lot4t_termes.refuser_si_perimee`, mais dans un balayage, ou rien ne le
documentait. La passe 4 d'ici REFUSE explicitement toute cible que `LOT2`
traite deja, et elle le dit au lieu de lever.

Usage :
    python3 balayage_lot4.py 1
    python3 balayage_lot4.py 2 --cible H-h
    python3 balayage_lot4.py 3
    python3 balayage_lot4.py 4 --cible H-h
    python3 balayage_lot4.py 4 --temoin
"""

import math
import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import approches as A
import coupe as K
import lot2 as L
import lot4 as Q
import souscrits as S
import termes as T

AMONT = "/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs"
AMONT_IT = "/tmp/ahn/sources/AtkinsonHyperlegibleNext-Italic.glyphs"

ICI = os.path.dirname(os.path.abspath(__file__))

#: Les six cibles du sous-lot, lues dans `termes.LOCS` pour le reste : une table
#: qui repete un parametre ecrit ailleurs finit par en diverger, et
#: `lot4.FAMILLES_O` l'a fait sans que rien le signale.
CIBLES = ["H-h", "H-k", "S-N", "S-H", "P-N", "P-H"]

#: Le coin que Nicolas a nomme, cible par cible. La passe 1 verifie d'abord que
#: le bout le departage au sens de `lot2._coin_vise_est_P` ; la passe 4 ne peut
#: pas essayer les quatre noms, les 71 voisins fois deux sens fois huit masters
#: depassant le plafond de trois minutes du bac a sable.
COIN = {"H-h": "droite", "H-k": "gauche", "S-N": "droite", "S-H": "droite",
        "P-N": "gauche", "P-H": "gauche"}

#: Le sens du geste, par cible. Sert a nommer la grandeur dans les colonnes :
#: un depassement au-dessus d'un alignement et une plongee au-dessous ne se
#: lisent pas dans le meme signe, et une colonne mal nommee a deja fait lire la
#: longueur d'un bout pour ce que la coupe enlevait, sur le z au vingt-sixieme
#: tour.
MONTE = {"H-h": True, "H-k": True, "S-N": True, "S-H": True,
         "P-N": False, "P-H": False}

#: L'alignement que chaque bout porte, pour l'AFFICHAGE seulement. Le
#: depassement, lui, est toujours mesure contre l'ordonnee du bout BRUT, jamais
#: contre une metrique declaree : la passation a annonce l'ascendante a 796
#: quand le bout de hampe s'arrete a 708, et la descendante a −251 quand la
#: jambe du p s'arrete a −162. Deux fois 88 et 89 unites d'erreur, deux fois sur
#: une metrique de ligne prise pour un fait de la lettre.
ALIGNEMENT = {"H-h": "asc", "H-k": "asc", "S-N": "cap", "S-H": "cap",
              "P-N": "base", "P-H": "base"}

#: Les interlignes que la feuille de style du site emploie reellement, lus dans
#: `gabarits/temoin.css`. 1,15 est celui des titres h1 a h4 et c'est le maillon
#: court ; 1,65 est celui du texte courant.
INTERLIGNES = [1.15, 1.30, 1.50, 1.65]

#: La borne haute des recherches, en unites. 150 et non 60 : le lot 3 a paye une
#: borne a 60 qui se faisait passer pour un refus de la geometrie, sur le p
#: ExtraBold. Ici la marge jusqu'a l'ascendante declaree vaut 88 unites, donc la
#: borne doit la depasser franchement pour ne jamais mordre avant la lettre.
BORNE = 150.0


def sources():
    """Les deux sources amont brutes, ou None si le clone manque.

    Aucune des six cibles n'est dans `lot2.LOT2` — la passe 1 le verifie au lieu
    de le supposer — donc `Temoin.glyphs` les porte telles quelles. Le balayage
    lit tout de meme l'amont pour les passes 1 a 3 : un controle de localisateur
    qui lit une source deja traitee mesure son propre reflet, et
    `check_termes.py` est tombe dedans au vingt-deuxieme tour.

    Rendre None plutot que retomber en silence sur `Temoin.glyphs` : « mesure et
    conforme » et « pas mesure » ne sont pas le meme verdict, et le clone amont
    a manque deux tours de ce projet, dont un en cours de session.
    """
    if not (os.path.exists(AMONT) and os.path.exists(AMONT_IT)):
        return None
    return [("rom", glyphsLib.GSFont(AMONT)),
            ("ital", glyphsLib.GSFont(AMONT_IT))]


def calques(font, nom):
    mid = {m.id: m.name for m in font.masters}
    g = font.glyphs[nom]
    if g is None:
        return []
    return [(mid[l.layerId], l) for l in g.layers if l.layerId in mid]


def metrique(font, master, quoi):
    """La valeur d'un alignement, lue sur le master et non ecrite ici."""
    m = [x for x in font.masters if x.name == master][0]
    return {"base": 0.0, "xh": float(m.xHeight), "asc": float(m.ascender),
            "cap": float(m.capHeight), "desc": float(m.descender)}.get(quoi, 0.0)


def orientation(segs, i):
    """L'ecart en degres a l'horizontale du segment designe."""
    a, b = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    dx, dy = float(b[0] - a[0]), float(b[1] - a[1])
    return abs(math.degrees(math.atan2(abs(dy), abs(dx))))


def segment_vise(lay, cle):
    """Le contour et l'indice que le localisateur designe, ou None.

    Rend aussi la liste des candidats horizontaux du meme contour, parce que
    c'est elle qui dit si le localisateur a DEPARTAGE ou s'il a eu de la chance.
    C'est le resultat de la passe 1 sur le N et le H.
    """
    nom, loc = T.LOCS[cle]
    for k, p in enumerate(L.paths(lay)):
        segs = K.to_segs(p)
        if K.area(segs) < 0:
            continue
        idx = loc(segs)
        if not idx:
            continue
        return k, segs, idx
    return None


def ordonnee_bout(lay, cle):
    """L'ordonnee du bout designe sur le glyphe BRUT.

    C'est contre elle que le depassement se mesure. Deux chiffres de la
    passation ont ete faux pour l'avoir mesure contre une metrique declaree :
    l'ascendante a 796 pour un bout a 708, la descendante a −251 pour une jambe
    a −162.
    """
    r = segment_vise(lay, cle)
    if r is None:
        return None
    _, segs, idx = r
    i = segs and idx[0]
    P, Qp = K.V(segs[i]["p0"]), K.V(segs[i]["p3"])
    return (float(P[1]) + float(Qp[1])) / 2.0


def ymax_calque(lay):
    """Le point le plus haut des contours d'encre du calque."""
    ys = [float(K.V(s[k])[1])
          for p in L.paths(lay)
          for segs in [K.to_segs(p)] if K.area(segs) >= 0
          for s in segs for k in ("p0", "p3")]
    return max(ys) if ys else None


def ymin_calque(lay):
    ys = [float(K.V(s[k])[1])
          for p in L.paths(lay)
          for segs in [K.to_segs(p)] if K.area(segs) >= 0
          for s in segs for k in ("p0", "p3")]
    return min(ys) if ys else None


def flanc_du_coin(lay, cle, coin):
    """L'orientation du flanc le long duquel le coin nomme coulisserait.

    C'est la grandeur qui decide de la DIRECTION du geste, et elle est lue sur
    le contour. `lot4.coupe_sortante` fait coulisser le coin le long du flanc
    voisin prolonge : sur un flanc vertical le coin part tout droit et la boite
    ne s'elargit pas d'une unite ; sur un flanc horizontal il avance
    lateralement sans monter.

    C'est ce qui separe le 4a du 4b, et c'est mesure et non suppose : une
    planche qui nommait la direction d'une sortante a la main s'est trompee sur
    la moitie des cas au vingt-cinquieme tour, le pied droit du n plongeant
    quand le bout du crochet du f avance.
    """
    r = segment_vise(lay, cle)
    if r is None:
        return "?"
    _, segs, idx = r
    i, n = idx[0], len(segs)
    try:
        est_P = L._coin_vise_est_P(segs, i, coin)
    except ValueError as e:
        return f"NOM REFUSE : {e}"
    j = (i - 1) % n if est_P else (i + 1) % n
    s = segs[j]
    if s["kind"] != "line":
        return f"seg {j} COURBE"
    o = orientation(segs, j)
    return f"seg {j} {'vert' if o > 45 else 'horiz'} {o:4.1f}deg"


def plafond(cle, lay, coin, pas=0.5, hi=BORNE):
    """La plus grande sortie EN UNITES qui s'applique encore, par dichotomie.

    Cherche la borne et ne la suppose pas. Le plafond du lot 2 avait ete annonce
    a 25 degres sur la queue du l, et ce chiffre etait ROMAIN : en italique il
    tombe a 21,4 degres a l'ExtraBold, et personne ne le savait avant le
    vingt-deuxieme tour. Tout plafond de ce projet se mesure sur les huit
    masters.
    """
    def marche(u):
        try:
            T.segs_etat(lay, cle, T._sortante(u, coin))
            return True
        except Exception:
            return False
    if not marche(1.0):
        return 0.0, False
    lo = 1.0
    if marche(hi):
        # Sature : la geometrie ne refuse rien en dessous de la borne, donc le
        # chiffre rendu est celui de L'OUTIL et non de la lettre. Le dire au
        # lieu de l'afficher nu — le lot 3 a lu « hors de portee » sur le p
        # ExtraBold pour une borne a 60 unites, et ca se lisait comme un refus
        # de la geometrie.
        return hi, True
    while hi - lo > pas:
        mi = (lo + hi) / 2.0
        if marche(mi):
            lo = mi
        else:
            hi = mi
    return lo, False


#: La borne haute, en degres, de la dichotomie de `termes.angle_pour_sortie`.
#:
#: Lue dans le code de la fonction plutot que recopiee ici serait mieux, mais
#: elle y est ecrite en dur dans un `lo, hi = 0.5, 45.0` local et n'est pas
#: exposee. Le chiffre est donc double, et ce commentaire est le garde-fou :
#: **si la valeur change dans `termes.py`, la detection de saturation d'ici
#: devient fausse en silence.**
BORNE_ANGLE = 45.0


def rotation_pour(lay, cle, coin, u):
    """L'angle de rotation que `termes` emploiera pour une sortie de `u` unites.

    Rend `(angle, sature)`. **Pris du PRODUCTEUR et non reconstruit** : c'est le
    protocole du quatorzieme tour, ou une verification qui retrouvait les coins
    d'une coupe par heuristique rendait 1,5 degre pour une rotation de 20.

    `sature` dit que la dichotomie a rendu sa borne haute, 45 degres, au lieu
    d'une valeur trouvee. Dans ce cas **le chiffre rendu est celui de l'outil et
    non de la lettre**, et la sortie reelle est plus petite que demandee sans
    que rien ne le signale. Le lot 3 a paye la meme forme de defaut sur une
    borne en unites : « hors de portee » sur le p ExtraBold se lisait comme un
    refus de la geometrie alors qu'il en fallait 60,0 pour une borne a 60.

    Aucune valeur ecrite dans `lot2.LOT2` ne mord sur cette borne — les entrees
    des lots 1 a 3 vont de 12 a 44 unites et se resolvent entre 4 et 35 degres.
    C'est l'etat a 88 unites du 4a, non candidat, qui l'a revelee.
    """
    r = segment_vise(lay, cle)
    if r is None:
        return None, False
    _, segs, idx = r
    i = idx[0]
    sn = T.sens_pour_sortie(segs, i, coin)
    if sn is None:
        return None, False
    th = T.angle_pour_sortie(segs, i, sn, u)
    if th is None:
        return None, False
    return th, abs(th - BORNE_ANGLE) < 1e-6


def cible_de(etq):
    """La sortie en unites que l'etiquette d'un etat annonce.

    Lue dans l'etiquette de `termes.ETATS` plutot que redonnee dans une seconde
    table : `lot4.FAMILLES_O` a diverge de sa documentation sans que rien le
    signale, et le lot 3 lisait deja ses candidats de cette facon.
    """
    for tok in etq.replace(",", " ").split():
        if tok.isdigit():
            return float(tok)
    return None


def dans_lot2(cle):
    """Le glyphe de cette cible a-t-il deja une entree qui touche CE bout.

    Rend la liste des entrees de `lot2.LOT2` portant le meme glyphe, ce qui est
    volontairement plus large que « le meme bout » : le l a deux entrees depuis
    le lot 2, sa queue et son bout de hampe, et une cible peut donc coexister
    avec une autre sur la meme lettre. Ce qui doit lever, c'est de reposer un
    geste sur un bout DEJA sorti — et c'est exactement ce qui casse
    `balayage_lot3.py 5 --cible Q-y` depuis que la table porte le lot 3.
    """
    nom, _ = T.LOCS[cle]
    return [e for e in L.LOT2 if e[0] == nom]


# ------------------------------------------------------------------- passes

def passe1(srcs):
    print("\n=== 1. l'inventaire des six bouts, sur les huit masters")
    print("  Ce que la passe verifie, et pourquoi chaque colonne existe :")
    print("   - le contour et l'indice designes, identiques d'un master a")
    print("     l'autre, sinon l'interpolation casse ;")
    print("   - les candidats du meme contour, qui disent si le localisateur")
    print("     a DEPARTAGE ou s'il a eu de la chance ;")
    print("   - l'ordonnee du bout, remesuree et non reprise : la passation")
    print("     annonce l'ascendante a 796 et le bout de hampe est a 708 ;")
    print("   - l'orientation du flanc voisin, qui decide de la direction ;")
    print("   - le plafond de sortie par dichotomie, en unites.")
    for cle in CIBLES:
        nom, loc = T.LOCS[cle]
        dej = dans_lot2(cle)
        print(f"\n  --- {cle} : {nom}, {loc.__name__}, coin « {COIN[cle]} », "
              f"{'monte' if MONTE[cle] else 'plonge'}")
        if dej:
            print(f"      ATTENTION : {len(dej)} entree(s) de LOT2 portent "
                  f"deja le glyphe {nom} — {[e[1] for e in dej]}")
        else:
            print(f"      aucune entree de LOT2 sur {nom} : l'etat servi le "
                  "porte tel quel")
        print(f"      {'master':22s} {'cont/seg':9s} {'cand horiz':30s} "
              f"{'y bout':>8s} {'align':>8s} {'ecart':>7s} "
              f"{'flanc du coin':22s} {'plafond':>12s}")
        for tag, font in srcs:
            for master, lay in calques(font, nom):
                r = segment_vise(lay, cle)
                if r is None:
                    print(f"      {tag} {master:18s} AUCUN SEGMENT DESIGNE")
                    continue
                k, segs, idx = r
                cand = L.lines(segs, vertical=False)
                y = ordonnee_bout(lay, cle)
                al = metrique(font, master, ALIGNEMENT[cle])
                desc = " ".join(f"{i}@{K.mid(segs[i])[1]:.0f}"
                                f"/{K.length(segs[i]):.0f}" for i in cand)
                pl, sat = plafond(cle, lay, COIN[cle])
                pls = f">{pl:.0f} (borne)" if sat else f"{pl:.1f}"
                col = f"{y:8.1f} {al:8.1f} {y - al:+7.1f}"
                print(f"      {tag} {master:18s} {k}/{idx[0]:<7d} "
                      f"{desc:30s} {col} "
                      f"{flanc_du_coin(lay, cle, COIN[cle]):22s} "
                      f"{pls:>12s}")

    # Le refus du nom de coin, essaye sur les quatre noms.
    #
    # `lot2._coin_vise_est_P` doit LEVER sur « bas » et « haut » : les six bouts
    # sont horizontaux, donc leurs deux coins ont la meme ordonnee et ces deux
    # noms n'y designent rien. Le refus est pose au vingt-septieme tour apres
    # qu'une colonne uniforme l'ait revele — la passe 2 du lot 3 rendait
    # exactement le meme deplacement pour les deux « lectures » de la demande.
    #
    # Le verifier ici n'est pas du zele : il rend le nom de coin des futures
    # entrees de `LOT2` verifiable, et sans lui un nom qui ne departage pas
    # applique un geste sans que personne puisse dire lequel des deux coins a
    # bouge.
    print("\n  --- le refus du nom de coin, les quatre noms sur chaque cible")
    print("      Attendu : « gauche » et « droite » passent, « bas » et")
    print("      « haut » LEVENT, les six bouts etant horizontaux.")
    for cle in CIBLES:
        nom, _ = T.LOCS[cle]
        ligne = []
        for coin in ("gauche", "droite", "bas", "haut"):
            ok = 0
            tot = 0
            for tag, font in srcs:
                for master, lay in calques(font, nom):
                    tot += 1
                    r = segment_vise(lay, cle)
                    if r is None:
                        continue
                    _, segs, idx = r
                    try:
                        L._coin_vise_est_P(segs, idx[0], coin)
                        ok += 1
                    except ValueError:
                        pass
            ligne.append(f"{coin} {ok}/{tot}")
        print(f"      {cle:5s} {nom:2s}  " + "   ".join(ligne))


def passe2(srcs, seulement=None):
    print("\n=== 2. les sorties candidates, en unites")
    print("  Le regime est en UNITES, choix de cadrage de Nicolas au")
    print("  vingt-huitieme tour : le point ouvert 51 reste ouvert et fige par")
    print("  defaut en unites, comme les lots 1 a 3. Ce que ca coute est connu")
    print("  et mesure — le bout de hampe passe de 54 unites de large en")
    print("  ExtraLight a 165 a l'ExtraBold, donc le meme depassement en")
    print("  unites donne un angle trois fois plus aigu dans les clairs.")
    print("\n  La colonne qui compte est d_gauche / d_droite : elle dit si la")
    print("  BOITE bouge. Sur un flanc vertical elle ne doit pas bouger d'une")
    print("  unite, et c'est l'hypothese de tout le sous-lot 4a — la passation")
    print("  a deja affirme qu'une boite ne bougeait pas alors que ce n'etait")
    print("  vrai qu'en romain, sur le pied droit du n au vingt-deuxieme tour,")
    print("  ou le flanc penche de 12 degres et la boite s'elargit de 2,5 a")
    print("  6,7 unites vers la gauche.")
    print("\n  « d h.chasse » est un DELTA et non une valeur absolue. Le N et")
    print("  le H italiques sortent deja de leur chasse avant tout geste, de")
    print("  35 unites au Bold Italic : lire la valeur absolue ferait passer")
    print("  un debord preexistant pour un cout du geste. C'est le piege de la")
    print("  comparaison dont les deux termes ne different pas par ce qu'on")
    print("  juge, tombe quatre fois dans ce projet.")
    print("\n  « depassement » est mesure contre l'ordonnee du bout BRUT, jamais")
    print("  contre une metrique declaree. « atteint » est l'ordonnee reelle du")
    print("  point le plus haut du glyphe apres geste, ou la plus basse pour un")
    print("  pied : c'est elle que l'interligne verra, passe 3.")
    for cle in [c for c in CIBLES if seulement is None or c == seulement]:
        nom, loc = T.LOCS[cle]
        for tag, font in srcs:
            print(f"\n    {tag} {nom} ({cle}), coin « {COIN[cle]} »")
            print(f"      {'master':20s} {'etat':50s} {'encre':>7s} "
                  f"{'depass':>7s} {'d_g':>6s} {'d_d':>6s} {'d_h':>6s} "
                  f"{'d_b':>6s} {'d h.chasse':>10s} {'atteint':>8s} "
                  f"{'rot':>6s} topo")
            for master, lay in calques(font, nom):
                y0 = ordonnee_bout(lay, cle)
                for code, etq, fn in T.ETATS[cle]:
                    if fn is None:
                        continue
                    try:
                        r = T.mesurer(lay, cle, fn, alignement=y0)
                    except Exception as e:
                        print(f"      {master:20s} {etq:50s} REFUS : {e}")
                        continue
                    try:
                        with T.avec_etat(lay, cle, fn):
                            att = (ymax_calque(lay) if MONTE[cle]
                                   else ymin_calque(lay))
                            topo = S.topologie(lay)
                    except Exception:
                        att, topo = float("nan"), "?"
                    dep = r.get("depassement" if MONTE[cle] else "retrait")
                    u = cible_de(etq)
                    th, sat = (rotation_pour(lay, cle, COIN[cle], u)
                               if u is not None else (None, False))
                    mq = ""
                    if sat:
                        mq = (f"   ANGLE SATURE a {BORNE_ANGLE:.0f}deg : la "
                              "sortie rendue est celle de l'outil, pas de la "
                              "lettre")
                    print(f"      {master:20s} {etq:50s} {r['encre']:7.4f} "
                          f"{dep if dep is not None else float('nan'):7.1f} "
                          f"{r['d_gauche']:+6.1f} {r['d_droite']:+6.1f} "
                          f"{r['d_haut']:+6.1f} {r['d_bas']:+6.1f} "
                          f"{r['hors_chasse'] - r['hors_chasse_avant']:+9.1f} "
                          f"{att:8.1f} "
                          f"{th if th is not None else float('nan'):6.1f} "
                          f"{topo}{mq}")


def repertoire():
    """Les codepoints du sous-ensemble web, lus dans le fichier du projet.

    L'interligne ne se juge que sur ce qui est SERVI. Mesurer le plafond sur les
    450 glyphes de la source ferait entrer des accentuees et des combinants
    qu'aucun texte du site n'emploie : le chiffre serait vrai et sans rapport
    avec une page.
    """
    out = set()
    for ligne in open(os.path.join(ICI, "subset_unicodes.txt")):
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        for tok in ligne.replace(",", " ").split():
            try:
                out.add(int(tok.replace("U+", "").replace("0x", ""), 16))
            except ValueError:
                pass
    return out


def extremes_servis(font, rep):
    """Le plafond et le plancher du repertoire servi, master par master.

    Les composites sont DECOMPOSES avant mesure, et toute fonction qui lit
    `L.paths` voit un composite vide. Sans decomposition, `Aring` sortirait du
    compte et le plafond des masters gras serait faux de 23 a 27 unites.

    **Rend TOUS les glyphes a un demi-point de l'extreme, et non un seul nom.**
    Le passage par un `max` a nom unique cache les ex aequo et attribue le
    plafond au premier glyphe dans l'ordre d'iteration — le meme defaut que
    `loc_sommet_fut` sur le H, et le meme que le project a paye sur `loc_bas`.
    Ici il n'etait pas theorique : **la passation annonce `Aring` comme plafond
    du repertoire servi, de 838 a 865 selon le master, et c'est faux dans les
    deux masters clairs.** Mesure, le plafond vaut

        ExtraLight  838,0  bar et brokenbar   (Aring n'est qu'a 835,0)
        Regular     838,0  bar, brokenbar ET Aring, les trois a egalite
        Bold        861,0  Aring
        ExtraBold   865,0  Aring

    La barre verticale ne varie pas le long de l'axe de graisse, quand le rond
    du Aring monte avec la graisse : les deux se croisent entre le Regular et
    le Bold. Un plafond attribue a une seule lettre aurait fait croire que
    l'anneau du A commande l'interligne dans tous les masters.
    """
    out = {}
    for mo in font.masters:
        tout = []
        for g in font.glyphs:
            u = g.unicode
            if not u or int(u, 16) not in rep:
                continue
            for lay in g.layers:
                if lay.layerId != mo.id:
                    continue
                try:
                    l2 = lay.copyDecomposedLayer()
                except Exception:
                    l2 = lay
                ys = [float(K.V(s[k])[1])
                      for p in L.paths(l2)
                      for segs in [K.to_segs(p)] if K.area(segs) >= 0
                      for s in segs for k in ("p0", "p3")]
                if ys:
                    tout.append((max(ys), min(ys), g.name))
        hv = max(t[0] for t in tout)
        lv = min(t[1] for t in tout)
        hn = [t[2] for t in tout if t[0] > hv - 0.5]
        ln = [t[2] for t in tout if t[1] < lv + 0.5]
        out[mo.name] = ((hv, " ".join(hn)), (lv, " ".join(ln)))
    return out


def passe3(srcs):
    print("\n=== 3. l'interligne PAR LE HAUT, le miroir de la passe 4 du lot 3")
    print("  Le lot 3 posait la question par le bas et le point ouvert 21 a")
    print("  ete chiffre ainsi : le glyphe le plus bas du repertoire servi")
    print("  n'est pas le p mais le g, donc le p avait 24 a 43 unites de")
    print("  plongee GRATUITE et la valeur retenue ne coute rien.")
    print("\n  La question symetrique se pose ici, et la reponse doit etre")
    print("  MESUREE et non deduite : le plafond du repertoire servi est une")
    print("  capitale accentuee, quand h, k, b, d, l s'arretent a 708.")
    print("\n  Le jour est la distance entre le plancher d'une ligne et le")
    print("  plafond de la suivante : interligne x 1000 − plafond + plancher.")
    rep = repertoire()
    print(f"\n  repertoire du sous-ensemble : {len(rep)} caracteres")
    for tag, font in srcs:
        ext = extremes_servis(font, rep)
        print(f"\n  --- {tag}")
        for mo in font.masters:
            (hi, gh), (lo, gl) = ext[mo.name]
            print(f"\n    {mo.name:20s} plafond {hi:7.1f} ({gh})   "
                  f"plancher {lo:7.1f} ({gl})")
            for cle in CIBLES:
                nom, _ = T.LOCS[cle]
                lays = dict(calques(font, nom))
                if mo.name not in lays:
                    continue
                if MONTE[cle]:
                    yb = ymax_calque(lays[mo.name])
                    print(f"      {nom:2s} ({cle:5s}) ymax {yb:7.1f} -> montee "
                          f"gratuite {hi - yb:6.1f} u avant de devenir le "
                          "plafond")
                else:
                    yb = ymin_calque(lays[mo.name])
                    print(f"      {nom:2s} ({cle:5s}) ymin {yb:7.1f} -> plongee "
                          f"gratuite {yb - lo:6.1f} u avant de devenir le "
                          "plancher")
            for il in INTERLIGNES:
                print(f"      interligne {il:.2f} : jour "
                      f"{il * 1000.0 - hi + lo:7.1f} u")

    # Ce que chaque etat coute sur le jour, a l'interligne le plus serre.
    #
    # Le bloc ci-dessus donne le jour de la police telle qu'elle est ; il ne dit
    # pas ce que chaque profondeur candidate coute. Un geste qui laisse le
    # glyphe SOUS le plafond existant ne coute rien du tout, quelle que soit sa
    # profondeur, et c'est ce que le lot 3 a etabli par le bas.
    #
    # Le nouveau plafond est le plus haut des deux, l'ancien et le glyphe
    # traite, et il est MESURE sur le calque apres geste et non deduit de la
    # profondeur demandee : `angle_pour_sortie` vise le chemin parcouru par le
    # coin et non sa composante verticale, donc la montee reelle vaut un peu
    # moins que la cible des que le flanc penche.
    print("\n  --- ce que chaque etat coute sur le jour, a l'interligne le plus")
    print("      serre du site : 1,15, celui des titres h1 a h4")
    for tag, font in srcs:
        ext = extremes_servis(font, rep)
        for cle in CIBLES:
            nom, _ = T.LOCS[cle]
            print(f"\n    {tag} {nom} ({cle})")
            print(f"      {'master':20s} {'etat':50s} {'atteint':>8s} "
                  f"{'plafond':>9s} {'plancher':>9s} {'jour 1,15':>10s} "
                  f"{'cout':>7s}")
            for master, lay in calques(font, nom):
                (hi, _), (lo, _) = ext[master]
                jour0 = 1.15 * 1000.0 - hi + lo
                for code, etq, fn in T.ETATS[cle]:
                    if fn is None:
                        continue
                    try:
                        with T.avec_etat(lay, cle, fn):
                            att = (ymax_calque(lay) if MONTE[cle]
                                   else ymin_calque(lay))
                    except Exception:
                        print(f"      {master:20s} {etq:50s} REFUS")
                        continue
                    pf = max(hi, att) if MONTE[cle] else hi
                    pl = lo if MONTE[cle] else min(lo, att)
                    jour = 1.15 * 1000.0 - pf + pl
                    cout = jour - jour0
                    marque = "" if cout >= -0.05 else "   PAYE"
                    print(f"      {master:20s} {etq:50s} {att:8.1f} "
                          f"{pf:9.1f} {pl:9.1f} {jour:10.1f} "
                          f"{cout:+7.1f}{marque}")


def appliquer_direct(lay, loc, fn):
    """Applique un etat en passant le localisateur, sans passer par `LOCS`.

    Sert au temoin de la passe 4, qui replonge le pied gauche du m — une cible
    qui a son entree dans `lot2.LOT2` et pas dans `termes.LOCS`, et c'est
    justement pourquoi son contact est un chiffre connu.
    """
    for p in list(L.paths(lay)):
        segs = K.to_segs(p)
        if K.area(segs) < 0:
            continue
        idx = loc(segs)
        if not idx:
            continue
        for i in sorted(idx, reverse=True):
            segs = fn(segs, i)
        lay.shapes[lay.shapes.index(p)] = K.from_segs(segs)
        return True
    return False


def passe4(srcs, seulement=None, temoin=False):
    """Le garde-fou de la bande pleine : ce que le geste peut faire TOUCHER.

    Requis et non joue en confirmation. Le prompt du projet l'impose pour tout
    geste qui fait sortir de la matiere hors de la boite d'origine, et la raison
    est mesuree : la plongee des pieds gauches du lot 1 ne touchait ni la
    chasse, ni la topologie, ni la boite en romain, les six controles etaient
    passes, et quatre paire-masters se touchaient quand meme.

    **LE SENS DU RISQUE EST INVERSE DE CELUI DES LOTS 1 ET 3.** Ceux-la
    faisaient descendre de la matiere, donc le risque etait le voisin LATERAL a
    hauteur de descendante — la queue du q contre le pied du m. Ici la matiere
    monte, et deux risques coexistent :

      - le voisin lateral en haut, a hauteur d'ascendante et de capitale. C'est
        ce que cette passe mesure, sur la bande pleine, comme les lots 1 et 3.
      - la DESCENDANTE DE LA LIGNE AU-DESSUS, qui n'est pas un voisin et
        qu'aucune mesure de paire ne peut voir. C'est la passe 3 qui la traite,
        par le jour d'interligne, et les deux passes ne se remplacent pas.

    La bande de jugement ne peut rien voir des deux : elle va de la ligne de
    base a la hauteur d'x, quand le geste vit entre 668 et 796. Elle rendrait un
    zero trivialement vrai — le defaut exact du garde-fou du F au
    vingt-troisieme tour, qui s'arretait 218 unites trop bas, et de la passe 3
    du lot 2, qui mesurait l'ouverture du bout de hampe sous elle.

    Le critere est le plancher de jour, `approches.JOUR_MIN`, 24 unites, celui
    du vingt-sixieme tour, et non « jamais plus serre qu'Atkinson » : la
    comparaison a Atkinson demanderait d'annuler le geste sur toute paire ou une
    matiere montante rencontre une matiere montante.

    **LA REFERENCE EST L'ETAT SERVI.** `Temoin.glyphs` porte les lots 1, 2 et 3,
    donc le bout de hampe du b, du d et du l deja coupe, et c'est la police a
    laquelle le 4a s'ajoutera. Mesure contre Atkinson brut, le verdict du lot 3
    est passe de huit masters a deux quand la reference a ete corrigee : c'est
    la correction la plus couteuse du vingt-septieme tour.

    **LE REFUS QUI MANQUAIT AU LOT 3.** `balayage_lot3.py 5 --cible Q-y` leve
    aujourd'hui « aucune sortante possible sur ce bout » : il repose la sortante
    sur un bout que la table a deja fait sortir. Le refus est ici explicite et
    porte un message, plutot que de remonter du fond de `_sortante`.

    Une cible par appel : les 71 voisins fois deux sens fois huit masters fois
    sept etats depassent le plafond de trois minutes du bac a sable.
    """
    print("\n=== 4. le garde-fou de la bande pleine, sur les 71 voisins")
    print("  Ce sous-lot fait MONTER de la matiere. Deux risques, et cette")
    print("  passe n'en couvre qu'un : le voisin LATERAL en haut. La")
    print("  descendante de la ligne au-dessus est traitee par la passe 3, et")
    print("  aucune mesure de paire ne peut la voir.")
    print(f"  Critere : le plancher de jour de {A.JOUR_MIN:.0f} unites, celui du")
    print("  vingt-sixieme tour, et non « jamais plus serre qu'Atkinson ».")
    import dessin as D
    import check_approches as CA
    if temoin:
        # Le temoin reste sur l'AMONT, et il le faut : il replonge le pied
        # gauche du m, qui EST dans `lot2.LOT2` depuis le vingt-cinquieme tour,
        # donc l'etat servi le porte deja et son crenage est corrige par
        # `paires_pieds.py`. Mesure sur l'amont, il retrouve `q+m` a −22,0, la
        # valeur que la passation annonce. Un temoin calibre sur rien ne prouve
        # rien, et le projet a rencontre un temoin qui ne savait pas echouer.
        cas = [("TEMOIN", "m", L.loc_pied_gauche,
                ("Tm", "pied gauche du m a 22 u, le contact connu du lot 1",
                 T._sortante(22.0, "gauche")))]
    else:
        cas = []
        for cle in [c for c in CIBLES if seulement is None or c == seulement]:
            nom, loc = T.LOCS[cle]
            dej = dans_lot2(cle)
            if dej:
                print(f"\n  {cle} : REFUS. {len(dej)} entree(s) de LOT2 "
                      f"portent deja {nom} — {[e[1] for e in dej]}.")
                print("    Reposer une sortante sur un bout deja sorti laisse")
                print("    deux points confondus, et `_sortante` leve. Pour")
                print("    mesurer un etat ECRIT, c'est une planche de")
                print("    verification qu'il faut, pas ce balayage.")
                continue
            coin = COIN[cle]
            # Toutes les profondeurs candidates, et non la seule plus grande.
            #
            # Le maximum majore le risque, c'est vrai et insuffisant : un
            # garde-fou qui rend « non » sans dire « a partir de quelle
            # profondeur » fait refaire le tour. Sur le y du lot 3, la reponse
            # « a partir de 32 unites, et dans deux masters » est ce qui a
            # permis a Nicolas de trancher 40.
            for code, etq, fn in T.ETATS[cle]:
                if fn is None:
                    continue
                cas.append((cle, nom, loc, (code, etq, fn)))
    bases = ((("rom", os.path.join(ICI, "Temoin.glyphs")),
              ("ital", os.path.join(ICI, "Temoin-Italic.glyphs")))
             if not temoin else (("rom", AMONT), ("ital", AMONT_IT)))
    quoi = ("l'amont brut" if temoin
            else "l'etat servi, lots 1, 2 et 3 compris")
    print(f"  Reference : {quoi}.")
    for cle, nom, loc, (code, etq, fn) in cas:
        print(f"\n  {cle} {nom} : {etq}")
        for tag, chemin in bases:
            if not os.path.exists(chemin):
                print(f"    {tag} : {chemin} absent, rien de mesure.")
                continue
            amont = glyphsLib.GSFont(chemin)
            tem = glyphsLib.GSFont(chemin)
            rate = False
            for master, lay in calques(tem, nom):
                if not appliquer_direct(lay, loc, fn):
                    print(f"    {tag} {master} : AUCUN BOUT, etat non applique")
                    rate = True
            if rate:
                continue
            for m in tem.masters:
                sa, st = D.Source(amont, m.name), D.Source(tem, m.name)
                serre, sous, deja = [], [], []
                for v in CA.VOISINS_F:
                    vn = v if len(v) > 1 else D.nom_glyphe(amont, v)
                    if vn is None or amont.glyphs[vn] is None:
                        continue
                    for a, b in ((vn, nom), (nom, vn)):
                        try:
                            k = A.kern(amont, m.id, a, b)
                            pa = A.couloir_plein(sa, a, b, k)
                            pt = A.couloir_plein(st, a, b, k)
                        except Exception:
                            continue
                        if None in (pa, pt):
                            continue
                        if pt < pa - 0.5:
                            serre.append((a, b, pa, pt))
                        # Trois cas et non deux, distinction posee au
                        # vingt-septieme tour : une paire sous le plancher n'est
                        # une anomalie que si le geste l'a AGGRAVEE. Une paire
                        # deja serree que le geste ne bouge pas est une
                        # information ; une paire deja serree que le geste
                        # aggrave est le PIRE cas, pas le plus anodin, et le
                        # premier critere corrige l'avait masque.
                        if pt < A.JOUR_MIN and pt < pa - 0.5:
                            sous.append((a, b, pa, pt))
                        elif pt < A.JOUR_MIN:
                            deja.append((a, b, pa, pt))
                serre.sort(key=lambda t: t[3])
                det = ("rien ne se resserre" if not serre else
                       ", ".join(f"{a}+{b} {pa:.1f}->{pt:.1f}"
                                 for a, b, pa, pt in serre[:5]))
                al = ("" if not sous else
                      f"   PASSE SOUS {A.JOUR_MIN:.0f} u : " +
                      ", ".join(f"{a}+{b} {pa:.1f}->{pt:.1f}"
                                for a, b, pa, pt
                                in sorted(sous, key=lambda t: t[3])[:4]))
                inf = ("" if not deja else
                       f"   [deja sous {A.JOUR_MIN:.0f} u dans Atkinson, "
                       "sans rapport avec le geste : " +
                       ", ".join(f"{a}+{b} {pa:.1f}"
                                 for a, b, pa, pt
                                 in sorted(deja, key=lambda t: t[3])[:4]) + "]")
                print(f"    {tag} {code:6s} {m.name:20s} "
                      f"{len(serre):2d} resserree(s), {len(sous):2d} passee(s) "
                      f"sous le plancher ; {det}{al}{inf}")


def main(argv):
    quelles = [a for a in argv if a.isdigit()]
    cible = argv[argv.index("--cible") + 1] if "--cible" in argv else None
    temoin = "--temoin" in argv
    if not quelles:
        print(__doc__)
        return 2
    if cible is not None and cible not in CIBLES:
        print(f"cible inconnue : {cible}. Les six sont {CIBLES}.")
        return 2
    srcs = sources()
    if srcs is None:
        print("La source amont n'est pas clonee : aucune passe ne peut mesurer.")
        print(f"  attendu : {AMONT}")
        print("  git clone --depth 1 "
              "https://github.com/googlefonts/atkinson-hyperlegible-next.git "
              "/tmp/ahn")
        print("\nVERDICT : NON FAIT. Ce n'est pas « aucune anomalie ».")
        return 1
    for n in quelles:
        if n == "1":
            passe1(srcs)
        elif n == "2":
            passe2(srcs, cible)
        elif n == "3":
            passe3(srcs)
        elif n == "4":
            passe4(srcs, cible, temoin)
        else:
            print(f"passe {n} inconnue")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
