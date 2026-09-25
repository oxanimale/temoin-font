#!/usr/bin/env python3
"""Le bras du O, GREFFE dans la contreforme. Point ouvert 84.

POURQUOI UN MODULE, ET PAS QUELQUES LIGNES DANS `make_temoin`. Les deux
generateurs de tables de paires ne lisent pas `Temoin.glyphs` : ils
RECONSTRUISENT l'etat en rejouant la chaine. Une etape ecrite dans la chaine
seule serait invisible pour eux, et ce projet a paye la lecon deux fois -- au
quarantieme tour, ou les deux tables sont sorties identiques apres un
changement certain, et au quarante-et-unieme, ou la pointe du circonflexe a
demande exactement ce placement. `pointe_sommet.appliquer` existe pour cette
raison ; `bras_O.appliquer` a la meme.

CE QUE LE GESTE EST. Un contour POSITIF pose dans la contreforme, encre par le
remplissage non nul : le O passe de deux contours a trois. Mesure avant
ecriture sur les quatre masters romains -- l'exterieur est positif, la
contreforme negative, le bras positif, donc il porte le signe de l'exterieur ;
son aire absolue vaut 19 000 a 35 000 unites carrees contre 69 000 a 242 000
pour la contreforme, donc il reste le plus petit des trois et `lot4.rayons`,
qui prend les deux plus grands, ne le voit pas ; et sa boite est strictement
interieure a celle du glyphe, donc la boite du O ne bouge pas d'une unite.
C'est le recouvrement que le point 17 nomme comme la seule limite connue de la
voie B, et Font Bakery le signale.

OU IL SE POSE, ET CE QUE CHAQUE PLACE DECIDE.

  - SUR LA SEULE SOURCE ROMAINE. `lot4.MASTERS_SANS_BRAS` porte les quatre
    masters italiques, decision de Nicolas au quarante-septieme tour, et
    `reglage_O` refuse en disant que c'est un arbitrage. Sur la source
    italique, cette fonction ne pose donc rien ET LE DIT dans son journal : un
    controle doit distinguer "mesure et conforme" de "pas mesure".

  - APRES LE LOT 3, ET C'EST UNE DECISION DE NICOLAS AU QUARANTE-HUITIEME
    TOUR. Le lot 3 derive `o.sc` du O du projet : placee avant, l'etape
    donnerait a la petite capitale un bras reduit au rapport 574/668. Nicolas
    l'a ecarte. C'est l'inverse du choix fait pour la fusion et pour la pointe
    du circonflexe, qui passent toutes deux AVANT le lot 3, et la difference
    se dit : celles-la propagent un geste de titrage a une lettre, celle-ci
    greffe une signature dans un blanc qui a la taille d'une petite capitale.

  - SUR LE `O` SEUL. Six glyphes servis sont des composites purs de `O` --
    `Oacute`, `Ocircumflex`, `Odieresis`, `Ograve`, `Otilde`, et
    `Ohungarumlaut` qui n'est pas servi -- donc ils suivent sans etre nommes,
    comme `four.tf` et `seven.tf` au quarante-quatrieme tour.
    `GLYPHES_SANS_BRAS` porte ceux qui REDESSINENT un O sous un autre nom et
    n'en recoivent pas.

LES GARDE-FOUS, ET ILS LEVENT. Une reapplication laisserait deux bras
superposes, que rien ne distinguerait a l'oeil ni dans un compte de taches ;
un bras qui sortirait de la contreforme changerait la boite du glyphe. Les
deux sont mesures ici, avant et apres.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coupe as K
import lot2 as L
import lot4 as Q
import mesure_O as M


#: LES GLYPHES QUI REDESSINENT UN O ET N'EN PORTENT PAS, avec la raison de
#: chacun. Ils vivent ici pour la meme raison que `MASTERS_SANS_BRAS` :
#: un glyphe decide et un glyphe jamais regarde sont identiques dans une
#: table, tous deux absents, et ce projet l'a paye plusieurs fois -- `e.sc`
#: au trente-septieme tour, l'AE et l'Aring au trente-neuvieme, le double
#: `.ti` au quarantieme. La section 5 de `check_O` les remesure.
GLYPHES_SANS_BRAS = {
    "o": "ecarte par Nicolas au dix-neuvieme tour ; le reglage mesure vit "
         "dans `lot4.o_ECARTE`. Sa paroi est plus epaisse en rapport, le bras "
         "y prendrait 0,39 du diametre de contreforme contre 0,26 sur le O.",
    "o.sc": "ecarte par Nicolas au quarante-huitieme tour. Il est DERIVE du O "
            "par le lot 3, donc la place de l'etape dans la chaine decide "
            "seule : posee apres le lot 3, elle ne l'atteint pas. Le prix "
            "assume est qu'un sigle en petites capitales n'a pas le bras que "
            "le meme sigle en capitales pleines porte.",
    "Oslash": "ecarte par Nicolas au quarante-huitieme tour. Trois contours "
              "propres, dont une barre : y greffer un bras cumulerait deux "
              "signes dans le meme blanc, ce qui est l'argument qui a fait "
              "garder au zero sa seule barre contextuelle au quarante-sixieme.",
    "OE": "ecarte par Nicolas au quarante-huitieme tour. Deux contours "
          "propres : il redessine un O sous un autre nom, et sa contreforme "
          "est plus etroite, donc `ep_facteur` n'y prendrait pas la meme part.",
}

#: Le glyphe qui porte le bras. Un seul, et ecrit plutot que devine.
PORTEUR = "O"

#: Le bras ne doit pas changer la boite du glyphe : il est greffe DANS la
#: contreforme. La tolerance absorbe l'arrondi a 0,1 unite de `from_segs`,
#: pas un bras qui sort.
TOL_BOITE = 0.5


def _boite(paths):
    xs, ys = [], []
    for p in paths:
        for n in p.nodes:
            xs.append(float(n.position.x))
            ys.append(float(n.position.y))
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def construire(lay, master):
    """Le GSPath du bras pour ce calque, sans rien ecrire.

    Partagee par la chaine et par le controle : deux codes qui appliquent le
    meme etat doivent passer par la meme fonction, lecon du vingt-quatrieme
    tour sur `approches.table_kern`.
    """
    genre, r = Q.reglage_O(master)
    if genre != "ancre":
        raise ValueError(
            f"O_TITRAGE annonce le genre {genre!r} ; ce module ne sait poser "
            f"que le bras ancre du quinzieme tour. Le changer demande de "
            f"relire `mesure_O.famille_O`, qui connait les six genres.")
    r = dict(r)
    r.pop("_note", None)
    ep = M.ep_paroi(lay) * r.pop("ep_facteur")
    return Q.bras_ancre(L.paths(lay), epaisseur=ep, **r), ep


def separer(lay):
    """(contours de base, bras ECRIT ou None) pour un calque de O.

    Le bras se reconnait par sa geometrie et non par sa position dans la
    liste : il est le seul contour d'aire POSITIVE dont la boite est
    strictement interieure a celle du glyphe. Un test sur l'indice ou sur le
    dernier ajoute serait vrai aujourd'hui et faux le jour ou un autre geste
    ecrit dans ce glyphe.
    """
    ps = L.paths(lay)
    bo = _boite(ps)
    base, bras = [], None
    for p in ps:
        a = K.area(K.to_segs(p))
        b = _boite([p])
        interieur = (b[0] > bo[0] + TOL_BOITE and b[1] > bo[1] + TOL_BOITE
                     and b[2] < bo[2] - TOL_BOITE and b[3] < bo[3] - TOL_BOITE)
        if a > 0 and interieur:
            if bras is not None:
                raise ValueError(
                    "deux contours positifs interieurs dans le O : le bras a "
                    "ete pose DEUX FOIS, et rien ne les distinguerait a "
                    "l'oeil ni dans un compte de taches d'encre.")
            bras = p
        else:
            base.append(p)
    return base, bras


def appliquer(font, log=None):
    """Greffe le bras dans le O, master par master. Retourne les masters faits.

    LEVE si le bras est deja la, si la boite du glyphe bouge, ou si le O
    manque. Ne leve pas sur une source italique : elle n'en porte pas, et
    c'est une decision -- mais le journal le dit, au lieu de rester muet.
    """
    g = font.glyphs[PORTEUR]
    if g is None:
        raise KeyError(
            f"{PORTEUR} absent de la source : le bras du O n'a pas de "
            f"porteur, et une etape qui ne fait rien en silence est ce que ce "
            f"projet appelle un NON MESURE.")
    ids = {m.id: m.name for m in font.masters}
    faits, ecartes = [], []
    for lay in g.layers:
        mn = ids.get(lay.layerId)
        if mn is None:
            continue
        if mn in Q.MASTERS_SANS_BRAS:
            ecartes.append(mn)
            continue
        _base, deja = separer(lay)
        if deja is not None:
            raise ValueError(
                f"le O porte deja un bras au master {mn!r}. Reappliquer "
                f"laisserait deux contours superposes : un compte de taches "
                f"d'encre et une planche rendraient exactement la meme chose, "
                f"et le defaut ne se verrait que dans le poids du fichier.")
        avant = _boite(L.paths(lay))
        bras, ep = construire(lay, mn)
        if K.area(K.to_segs(bras)) <= 0:
            raise ValueError(
                f"le bras sort avec une aire NEGATIVE au master {mn!r} : pose "
                f"dans la contreforme, il y ferait un trou dans le trou au "
                f"lieu d'etre encre par le remplissage non nul.")
        lay.shapes.append(bras)
        apres = _boite(L.paths(lay))
        d = max(abs(a - b) for a, b in zip(avant, apres))
        if d > TOL_BOITE:
            raise ValueError(
                f"le bras fait bouger la boite du O de {d:.1f} unite(s) au "
                f"master {mn!r} : il sort de la contreforme, donc il change "
                f"l'espacement de la lettre et non seulement son blanc.")
        faits.append((mn, ep, len(bras.nodes)))

    if log is not None:
        if faits:
            log.append(("bras du O",
                        f"{len(faits)} master(s) greffe(s) : "
                        + ", ".join(f"{mn} base {ep:.0f}u {n} noeuds"
                                    for mn, ep, n in faits)))
        if ecartes:
            log.append(("bras du O ecarte",
                        f"{len(ecartes)} master(s) SANS bras, decision de "
                        f"Nicolas au quarante-septieme tour : "
                        + " ".join(sorted(ecartes))))
        if not faits and not ecartes:
            log.append(("bras du O", "AUCUN master reconnu : NON MESURE"))
    return [mn for mn, _ep, _n in faits]


if __name__ == "__main__":
    import glyphsLib
    ici = os.path.dirname(os.path.abspath(__file__))
    for nom in ("Temoin.glyphs", "Temoin-Italic.glyphs"):
        chemin = os.path.join(ici, nom)
        if not os.path.exists(chemin):
            print(f"{nom} : absente. Ce n'est pas un zero, c'est un NON MESURE.")
            continue
        f = glyphsLib.GSFont(chemin)
        ids = {m.id: m.name for m in f.masters}
        print(f"\n{nom}")
        for lay in f.glyphs[PORTEUR].layers:
            mn = ids.get(lay.layerId)
            if mn is None:
                continue
            base, bras = separer(lay)
            print(f"  {mn:<18} {len(base)} contour(s) de base, "
                  + (f"bras ECRIT a {len(bras.nodes)} noeuds"
                     if bras is not None else "pas de bras"))
