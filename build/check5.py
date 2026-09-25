#!/usr/bin/env python3
"""Controle chiffre du lot 3, sur les lettres de test.

Quatre questions, quatre mesures. Aucune ne se juge a l'oeil :

  1. la petite capitale a-t-elle exactement la hauteur demandee, dans les
     huit masters ?
  2. son fut vaut-il celui du bas de casse du meme master, qui est toute la
     raison d'etre de la compensation ?
  3. la topologie est-elle identique d'un master a l'autre, donc interpolable ?
  4. les coupes du lot 2 survivent-elles a la reduction, et de combien
     derivent-elles si on elargit la lettre ?

TROIS CODES DE RETOUR depuis le soixante-sixieme tour : 0 mesure et conforme,
1 mesure et signale, 2 NON MESURE. Avant, ce script n'appelait AUCUN
`sys.exit` : il imprimait "TOTAL : n anomalie(s)" et rendait 0, donc un
enchainement de commandes lisait un succes sur un signalement ecrit a l'ecran.
Et prive de son clone amont, il rendait une trace Python et sortait a 1, donc
un signalement sur zero mesure. Deux faces du meme piege, le troisieme du
projet, points ouverts 106 et 111.
"""

import math
import os
import statistics
import sys

import glyphsLib

import coupe as K
import lot2 as L
import lot3 as S3

SRC = "/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs"
SRC_I = "/tmp/ahn/sources/AtkinsonHyperlegibleNext-Italic.glyphs"

NON_MESURE = 2

BASES = None      # None = tout le jeu, accentuees comprises


def haut(layer):
    ys = []
    for p in L.paths(layer):
        for s in K.to_segs(p):
            for t in range(33):
                ys.append(float(K.bez(s, t / 32)[1]))
    return max(ys), min(ys)


#: L'ordre de preference des capitales temoins pour la mesure de hauteur.
#:
#: Le temoin doit avoir un sommet ET un pied EXACTEMENT sur ses alignements :
#: une capitale qui deborde optiquement, comme le O a 680 pour une capitale de
#: 668, rendrait une hauteur de petite capitale plus grande que la cible sans
#: qu'aucun reglage soit en cause.
#:
#: **Le temoin etait `h.sc`, donc le H, et le lot 4a a detruit la propriete meme
#: qui en faisait le bon choix** : son sommet de fut droit monte maintenant de 24
#: unites et son pied gauche plonge de 24, donc `h.sc` mesurait 571,8 pour une
#: cible de 552, soit exactement le rapport 692/668. Le controle a signale quatre
#: anomalies par source, et il avait raison de signaler — il mesurait simplement
#: une grandeur que le projet venait de changer.
#:
#: La sortie n'est pas de choisir un autre nom en dur, qui serait invalide par le
#: lot suivant : le A et le X sont les cibles du lot 4b, et le c, le C, le G et
#: le Q celles du lot 5. Le temoin est donc CHOISI PAR MESURE a chaque
#: execution, dans cet ordre de preference, et le controle imprime lequel il a
#: retenu. Un temoin qu'on ne voit pas est un temoin qu'on ne peut pas
#: contredire.
#:
#: L'ordre prefere les capitales qu'aucune table ne touche — B, D, I, K, P, R —
#: puis celles que la coupe texte traite par un geste rentrant, qui ne deplace
#: pas leur boite. Mesure au vingt-huitieme tour, quinze capitales qualifient sur
#: les huit masters des deux sources : A B D E F I K L P R T V W X Z.
TEMOINS_HAUTEUR = "BDIKPRVWEFLTZAX"


def temoin_hauteur(font, mid, cap):
    """La premiere capitale de `TEMOINS_HAUTEUR` posee exactement sur ses deux
    alignements dans ce master, ou None si aucune ne l'est.

    Rend le nom de la CAPITALE ; la petite capitale correspondante est son nom
    en bas de casse suffixe `.sc`, ce que `lot3` construit.
    """
    for c in TEMOINS_HAUTEUR:
        g = font.glyphs[c]
        if g is None:
            continue
        lay = next((l for l in g.layers if l.layerId == mid), None)
        if lay is None:
            continue
        hi, lo = haut(lay)
        if abs(hi - cap) <= 0.05 and abs(lo) <= 0.05:
            return c
    return None


def fut_sc(font, nom, mid, hauteur):
    return S3.fut(font, nom, mid, hauteur,
                  parts=(0.16, 0.24, 0.32, 0.40, 0.60, 0.68))


def angle_seg(layer, i):
    """Angle du segment i par rapport a la verticale."""
    segs = K.to_segs(L.main_path(layer))
    if i >= len(segs):
        return None
    s = segs[i]
    return math.degrees(math.atan2(abs(s["p3"][0] - s["p0"][0]),
                                   abs(s["p3"][1] - s["p0"][1])))


def indice_coupe(layer_brut, loc):
    """Indice du segment que le localisateur designe AVANT le lot 2.

    On ne peut pas relocaliser apres coup : une fois tournee de 20 degres, la
    coupe du L n'est plus verticale, et `lines(vertical=True)` ne la retient
    plus. Le localisateur rendrait alors un autre segment, reste vertical, et
    l'angle mesure vaudrait 0 quoi qu'il arrive — c'est ce que faisait la
    premiere version de ce controle, qui affichait donc « aucune derive »
    partout sans rien mesurer.
    """
    segs = K.to_segs(L.main_path(layer_brut))
    idx = loc(segs)
    return idx[0] if idx else None


def controle(src, lab, hauteur, largeur=1.0, sb=0.0):
    brut = glyphsLib.load(open(src, encoding="utf-8"))
    f = glyphsLib.load(open(src, encoding="utf-8"))
    L.appliquer_lot(f, 20.0)
    base = glyphsLib.load(open(src, encoding="utf-8"))
    L.appliquer_lot(base, 20.0)
    jrn = []
    S3.appliquer_lot(f, hauteur, largeur, sb, jrn, BASES)
    mid = {m.id: m.name for m in f.masters}
    pb = 0

    print(f"\n=== {lab} — hauteur {hauteur} u, largeur x{largeur}, approche +{sb:.0f} u")
    print(f"{'master':<18}{'source':>8}{'extrap.':>9}{'temoin':>7}"
          f"{'hauteur':>9}{'fut .sc':>9}{'cible':>7}{'ecart':>8}")
    for m in f.masters:
        j = next(x for x in jrn if x["master"] == m.name)
        # Le temoin est choisi par mesure sur la source DEJA COUPEE par le lot
        # 2 et le lot 4a, `brut` ne servant qu'aux angles : c'est l'etat dont
        # `lot3` derive les petites capitales, donc c'est lui qui decide si une
        # capitale est encore posee sur ses deux alignements.
        cap = float(m.capHeight or 668)
        tc = temoin_hauteur(base, m.id, cap)
        if tc is None:
            print(f"{m.name:<18}  AUCUN TEMOIN : plus une seule capitale de "
                  f"{TEMOINS_HAUTEUR} n'est posee exactement sur ses deux "
                  "alignements. La hauteur des petites capitales n'est pas "
                  "mesurable ainsi, et le controle refuse plutot que de "
                  "mesurer un debord.")
            pb += 1
            continue
        # DEUX TEMOINS ET NON UN, et c'est la leçon du huitieme tour : un seul
        # nombre pour deux proprietes distinctes se trompe sur l'une des deux.
        #
        # La HAUTEUR demande une capitale posee exactement sur ses deux
        # alignements, donc le temoin mesure ci-dessus — le B au vingt-huitieme
        # tour. Le FUT demande une capitale dont le fut gauche soit ISOLE aux
        # hauteurs ou `lot3.fut` traverse, 0,16 a 0,68 de la hauteur : le B n'en
        # est pas, sa panse s'y trouve, et il rendait 477,3 unites pour une cible
        # de 165 a l'ExtraBold — la largeur de la lettre entiere et non celle du
        # fut. Le H reste le bon temoin pour cette mesure : ses deux futs sont
        # separes par un grand blanc, et le geste du lot 4a ne touche que son
        # sommet et son pied, jamais son fut a mi-hauteur.
        h_mes = haut(next(l for l in f.glyphs[tc.lower() + ".sc"].layers
                          if l.layerId == m.id))[0]
        fs = fut_sc(f, "h.sc", m.id, hauteur)
        cible = j["fut_bdc"]
        ecart = 100 * (fs - cible) / cible
        drapeau = ""
        if abs(h_mes - hauteur) > 0.6:
            drapeau += "  HAUTEUR"; pb += 1
        if abs(ecart) > 2.0:
            drapeau += "  FUT"; pb += 1
        print(f"{m.name:<18}{j['d']:>8.1f}{('oui' if j['t'] > 1 else '-'):>9}"
              f"{tc:>7}{h_mes:>9.1f}{fs:>9.1f}{cible:>7.1f}{ecart:>7.1f}%"
              f"{drapeau}")

    # --- topologie identique d'un master a l'autre
    div = []
    for nom in [n for n, *_ in S3.jeu(f) if f.glyphs[n] is not None]:
        vus = {tuple(tuple((x.type, x.smooth) for x in p.nodes)
                     for p in L.paths(l))
               for l in f.glyphs[nom].layers if l.layerId in mid}
        if len(vus) != 1:
            div.append(nom)
    print(f"  topologie divergente : {div or 'aucune'}"
          f"   ({len(S3.jeu(f))} glyphes prevus, "
          f"{sum(1 for n, *_ in S3.jeu(f) if f.glyphs[n])} construits)")
    pb += len(div)

    # --- aire et sens des contours : detecte un contour retourne ou effondre
    for nom in [n for n, *_ in S3.jeu(f) if f.glyphs[n] is not None]:
        for l in f.glyphs[nom].layers:
            if l.layerId not in mid:
                continue
            src_nom = dict((n, b) for n, b, _, _ in S3.jeu(f))[nom]
            b0 = next(x for x in base.glyphs[src_nom].layers
                      if x.layerId == l.layerId)
            if len(L.paths(b0)) != len(L.paths(l)):
                continue          # capitale composite : compare plus bas au raster
            for p0, p1 in zip(L.paths(b0), L.paths(l)):
                a0, a1 = K.area(K.to_segs(p0)), K.area(K.to_segs(p1))
                if a0 * a1 <= 0:
                    print(f"    CONTOUR RETOURNE {nom} {mid[l.layerId]}")
                    pb += 1

    # --- les coupes du lot 2 survivent-elles ?
    print("  coupes du lot 2, angle a la verticale (capitale -> petite capitale) :")
    for nom, loc in (("L", L.loc_droite), ("S", L.loc_terminaisons_S),
                     ("F", L.loc_barres_F), ("E", L.loc_barres_E),
                     ("I", L.loc_droite)):
        m = f.masters[1]
        i = indice_coupe(next(l for l in brut.glyphs[nom].layers
                              if l.layerId == m.id), loc)
        if i is None:
            continue
        a0 = angle_seg(next(l for l in base.glyphs[nom].layers
                            if l.layerId == m.id), i)
        a1 = angle_seg(next(l for l in f.glyphs[nom.lower() + ".sc"].layers
                            if l.layerId == m.id), i)
        if a0 is None or a1 is None:
            continue
        d = a1 - a0
        print(f"    {nom} -> {nom.lower()}.sc   segment {i:>2}   "
              f"{a0:6.2f}° -> {a1:6.2f}°   derive {d:+.2f}°"
              + ("   DERIVE" if abs(d) > 0.5 else ""))
        if abs(d) > 0.5:
            pb += 1
    # --- preuve par rasterisation que l'extrapolation n'a rien casse
    #
    # Une petite capitale est une capitale reduite : elle doit avoir le meme
    # nombre de taches d'encre et le meme nombre de contreformes. Si une
    # extrapolation avait fait se croiser deux contours ou refermer une
    # contreforme, le compte changerait. C'est le meme raisonnement que
    # check4.py au lot 2 : on ne regarde pas le dessin, on le compte.
    #
    # Deux precautions, apprises en le faisant rater :
    #   - la petite capitale est rendue AGRANDIE au rapport capitale/hauteur,
    #     sinon on compare une lettre a 86 % avec une lettre a 100 % et l'on
    #     mesure la taille, pas la topologie. Quatre fausses alertes sur cinq
    #     venaient de la ;
    #   - la resolution est haute. A 190 px de cadratin, le Ccedilla et l'OE
    #     donnaient de fausses alertes des deux cotes.
    import numpy as np
    from scipy import ndimage
    from PIL import Image
    import dessin as D

    def topo(source, nom, taille=900):
        taille = int(taille)
        im = Image.new("L", (taille * 2, taille * 2), 255)
        dr_ = __import__("PIL.ImageDraw", fromlist=["ImageDraw"]).Draw(im)
        k = taille / source.upem
        # LE CLASSEMENT EST PAR IMBRICATION, point 85, quarante-neuvieme tour.
        # Ce controle compte les TACHES d'encre et de fond pour prouver que la
        # topologie d'une petite capitale suit celle de sa capitale. Un contour
        # greffe efface retire une tache d'encre et en ajoute une de fond : les
        # deux comptes seraient faux dans le meme sens, donc concordants, donc
        # muets. Les petites capitales derivent des capitales, et le O en est
        # une.
        cs = source.contours(nom)
        for c, e in D.couches_ecran(
                cs, lambda x, y: (taille * 0.5 + x * k, taille * 1.5 - y * k)):
            if len(c) > 2:
                dr_.polygon(c, fill=0 if e else 255)
        a = np.array(im) < 128
        _, n_encre = ndimage.label(a, structure=np.ones((3, 3)))
        _, n_fond = ndimage.label(~a)
        return n_encre, n_fond, int(a.sum())

    ecarts = []
    for m in f.masters:
        sc_src = D.Source(f, m.name)
        for nom, bas, _, _ in S3.jeu(f):
            if f.glyphs[nom] is None:
                continue
            # Deux resolutions, et l'on ne signale que si l'ecart tient aux
            # deux. Le Ccedilla italique a une queue dont la pointe frole son
            # propre fut : son compte de contreformes change tout seul selon la
            # resolution, dans la capitale d'origine comme dans la reduction.
            # Un compte instable est une quasi-tangence de la source, pas
            # quelque chose que le lot 3 aurait cree.
            z = (m.capHeight or 668) / hauteur
            t1, t0 = topo(sc_src, nom, 900 * z), topo(sc_src, bas, 900)
            ecarts.append((t1[2] / t0[2], nom, m.name) if t0[2] else (1, nom, m.name))
            if t1[:2] == t0[:2]:
                continue
            u1, u0 = topo(sc_src, nom, 1800 * z), topo(sc_src, bas, 1800)
            if u1[:2] == u0[:2]:
                continue
            # Ce que l'on traque est une fermeture : la petite capitale gagne
            # une contreforme, ou son encre se scinde. Perdre une region de fond
            # veut dire qu'une cloison s'est ouverte, ce qui n'est pas le defaut
            # cherche ; on le signale sans compter d'anomalie.
            ferme = u1[1] > u0[1] or u1[0] != u0[0]
            print(f"    {'TOPOLOGIE RASTER' if ferme else 'note raster'} {nom} "
                  f"{m.name} encre/fond {u0[:2]} -> {u1[:2]}")
            pb += 1 if ferme else 0

    r = sorted(ecarts)
    print(f"  raster : {len(ecarts)} glyphes-masters controles, "
          f"surface relative de {r[0][0]:.3f} ({r[0][1]}/{r[0][2]}) "
          f"a {r[-1][0]:.3f} ({r[-1][1]}/{r[-1][2]})")

    print(f"  --- {pb} anomalie(s)")
    return pb


def main():
    """Les deux sources amont, puis le verdict.

    La garde est EN TETE et pas au premier acces : `glyphsLib` leverait une
    `FileNotFoundError` au milieu du premier controle, apres avoir deja
    imprime des lignes, et la trace se lirait comme un defaut du dessin.
    """
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 552.0
    manquantes = [c for c in (SRC, SRC_I) if not os.path.exists(c)]
    if manquantes:
        for c in manquantes:
            print(f"!! source amont absente : {c}")
        print("   Cloner Atkinson Hyperlegible Next, ou pointer SRC ailleurs.")
        print("   NON MESURE. Ce n'est pas un succes, et ce n'est pas non plus")
        print("   un defaut : aucune mesure n'a eu lieu.")
        return NON_MESURE
    total = 0
    total += controle(SRC, "roman", h, sb=14.0)
    total += controle(SRC_I, "italique", h, sb=14.0)
    print(f"\nTOTAL : {total} anomalie(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
