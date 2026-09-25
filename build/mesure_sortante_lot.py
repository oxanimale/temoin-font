#!/usr/bin/env python3
"""Ce que la coupe SORTANTE fait vraiment, sur les trente glyphes qui la
recoivent. Trente-sixieme tour.

LA QUESTION QUE CE SCRIPT POSE N'EST PAS CELLE DU TRENTE-CINQUIEME TOUR. Celui-ci
a mesure que la sortante tient sa promesse : 44,0 unites sur une capitale et
32,0 sur un bas de casse, partout. Le chiffre est le DEPASSEMENT VERTICAL du
bout par rapport a son alignement, et il est juste. Il ne dit rien de ce qui a
tourne pour l'obtenir.

`coupe.coupe_sortante` fait tourner UN SEGMENT autour d'un de ses coins ;
l'autre coin coulisse le long du flanc voisin prolonge. Le depassement obtenu
est le meme que le segment fasse 100 unites ou 600 : seul l'angle change. Sur
un pied de fut de 150 unites, 44 unites de sortie demandent 16 degres et l'oeil
lit un bout coupe. Sur la barre basse du L, longue de plusieurs centaines
d'unites, les memes 44 unites demandent quelques degres et l'oeil lit une barre
qui penche. Ce sont deux gestes de dessin differents sous un seul nombre, et
c'est la septieme fois que ce projet trouve un scalaire qui cache l'essentiel.

CE QUI SERT D'ETALON, et il n'est pas invente : les glyphes dont la sortante est
ARRETEE et validee sur planche par Nicolas -- ceux de `lot4.PRESCRIPTIONS` et de
`lot4.ETENDU` qui recoivent une sortante en bas. Leur longueur de segment donne
la fourchette de ce qui a deja ete juge. Un glyphe du lot dont le segment est
dans cette fourchette recoit un geste de meme nature ; un glyphe tres au-dela
recoit un geste que personne n'a jamais valide.

CE QUI EST MESURE, et d'ou vient chaque chiffre :

    longueur    la corde du segment tourne, lue AVANT la rotation. Le projet a
                deja paye deux fois une longueur mesuree apres coup : les
                localisateurs ne reconnaissent plus un bout coupe.
    theta       du journal de `couper_alignements`, donc du producteur.
    sortie      "sort de N" du meme journal : le depassement vertical obtenu.
    depl        le plus grand deplacement de noeud du contour, et sa
                decomposition dx/dy. Le deplacement de noeud et la descente
                verticale sont DEUX GRANDEURS JUSTES qui ne donnent pas le meme
                chiffre ; les deux sont imprimees, jamais melangees.

LES SEGMENTS SONT REPERES PAR COMPARAISON avant/apres, contour par contour et
indice par indice, et non en rejouant `loc_alignement`. Une verification doit
prendre son objet du producteur.

    python3 mesure_sortante_lot.py                  romain, les 30
    python3 mesure_sortante_lot.py --italique       italique, les 30
    python3 mesure_sortante_lot.py --etalon         les glyphes deja arretes
    python3 mesure_sortante_lot.py --tous           les deux sources, tout
"""

import math
import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coupe as K
import lot2 as L
import lot4 as Q
import mesure_titrage as MT

#: Les trois familles du lot, dans l'ordre ou les planches les traitent. La
#: liste n'est PAS ecrite ici : elle est mesuree par `lot()`, et ces ensembles
#: ne servent qu'a ranger la sortie. Un nom qui apparaitrait dans la mesure sans
#: etre range ici est imprime a part, plutot que tu.
FAMILLES = (
    ("capitales a barre", set("BDEFGLPRTZ") | {"AE", "Aring", "Eth", "OE",
                                               "Thorn"}),
    ("bas de casse", {"a", "f", "germandbls", "idotless", "k", "l", "t", "z"}),
    ("signes", {"ampersand", "dagger", "daggerdbl", "nine", "numbersign",
                "plus", "plusminus"}),
)


def lot(lab, amont, binaire):
    """Les glyphes touches, dans le perimetre, que rien n'a encore ecrit."""
    r = MT.analyser(lab, amont, binaire, verbeux=False)
    if r is None:
        return None
    ecrits = set(Q.ETENDU) | set(Q.PRESCRIPTIONS)
    return sorted(n for n in r["touche"]
                  if n not in ecrits and Q.dans_le_titrage(n))


def ecrits_a_sortante(lab, amont, binaire):
    """L'etalon : ce que Nicolas a deja valide sur planche."""
    r = MT.analyser(lab, amont, binaire, verbeux=False)
    if r is None:
        return None
    ecrits = set(Q.ETENDU) | set(Q.PRESCRIPTIONS)
    return sorted(n for n in r["touche"]
                  if n in ecrits and Q.dans_le_titrage(n))


def corde(s):
    return math.hypot(s["p3"][0] - s["p0"][0], s["p3"][1] - s["p0"][1])


def noeuds(segs):
    return [s["p0"] for s in segs]


def direction(s):
    """L'angle de la corde, en degres. Ce qui separe un segment TOURNE d'un
    segment PROLONGE."""
    return math.degrees(math.atan2(s["p3"][1] - s["p0"][1],
                                   s["p3"][0] - s["p0"][0]))


def gestes(avant, apres, journal):
    """Un enregistrement par segment tourne.

    `avant` et `apres` sont les listes de contours, chacune une liste de
    segments. La topologie est conservee par construction -- c'est ce que
    `check3` verifie a chaque tour -- donc les indices se correspondent.

    DEUX SEGMENTS SONT MODIFIES PAR UNE SORTANTE, ET UN SEUL EST LE GESTE.
    `coupe_sortante` remplace segs[i] par une ligne dont un coin a coulisse, et
    PROLONGE le voisin qui partage ce coin. Le premier jet de ce script prenait
    les deux, et il a rendu 668,0 unites -- la hauteur de capitale -- comme
    longueur du segment tourne du B, du D, du E, du F, du L, du P et du Thorn :
    c'etait leur FUT GAUCHE, prolonge vers le bas. Le segment tourne CHANGE DE
    DIRECTION, le segment prolonge garde la sienne : c'est ce qui les separe,
    et c'est un fait de l'operation, pas un seuil.

    L'APPARIEMENT AVEC LE JOURNAL SE FAIT PAR L'INDICE, que `couper_alignements`
    y ecrit. Il ne se fait pas par l'ordre : le producteur parcourt ses
    terminaisons en indice DECROISSANT, et un appariement positionnel attribuait
    l'angle du mauvais segment.
    """
    out = []
    par_i = {}
    for (_n, i, th, v, _s) in journal:
        if isinstance(v, str) and v.startswith("sort de"):
            par_i.setdefault(i, []).append((th, float(v.split()[-1])))
    for ci, (a, b) in enumerate(zip(avant, apres)):
        if len(a) != len(b):
            out.append(dict(err=f"contour {ci} : {len(a)} -> {len(b)} segments"))
            continue
        for i, (sa, sb) in enumerate(zip(a, b)):
            if sa["p0"] == sb["p0"] and sa["p3"] == sb["p3"]:
                continue
            if sb["kind"] != "line":
                continue
            if abs(direction(sa) - direction(sb)) < 0.02:
                continue          # prolonge, pas tourne
            dep = max(math.hypot(p[0] - q[0], p[1] - q[1])
                      for p, q in ((sa["p0"], sb["p0"]), (sa["p3"], sb["p3"])))
            if sa["p0"] != sb["p0"]:
                dx, dy = sb["p0"][0] - sa["p0"][0], sb["p0"][1] - sa["p0"][1]
            else:
                dx, dy = sb["p3"][0] - sa["p3"][0], sb["p3"][1] - sa["p3"][1]
            th = so = None
            if par_i.get(i):
                th, so = par_i[i].pop(0)
            out.append(dict(contour=ci, i=i, lg=corde(sa), depl=dep,
                            dx=dx, dy=dy, theta=th, sortie=so,
                            mx=(sa["p0"][0] + sa["p3"][0]) / 2.0,
                            my=(sa["p0"][1] + sa["p3"][1]) / 2.0,
                            dtheta=abs(direction(sa) - direction(sb))))
    reste = sum(len(v) for v in par_i.values())
    if reste:
        out.append(dict(err=f"{reste} sortante(s) du journal sans segment "
                            f"tourne apparie"))
    return out


def par_glyphe(font, noms, bas=None):
    """Le pire cas par glyphe sur les quatre masters, et le detail par master.

    `bas` FORCE le regime des terminaisons du bas et se transmet tel quel a
    `appliquer_reglage`. Lui passer les quadrants du HAUT fait poser la
    sortante sur le haut, ce qui est le seul moyen de mesurer un glyphe dont la
    seule terminaison est en haut -- le 3 et le 5 sont dans ce cas, et le
    regime tranche au trente-cinquieme tour les epargne. C'est la mecanique de
    la section 13 de `check_perimetre`, et non une seconde.
    """
    out = {}
    for nom in noms:
        g = font.glyphs[nom]
        if g is None:
            continue
        rec = dict(dem=Q.depassement_pour(nom), masters={}, err=[])
        for m in font.masters:
            lay = next((l for l in g.layers if l.layerId == m.id), None)
            if lay is None:
                continue
            avant = [K.to_segs(p) for p in L.paths(lay)]
            jour = []
            try:
                MT.appliquer_reglage(lay, nom, m, haut="aucune", journal=jour,
                                     bas=bas)
            except Exception as e:
                rec["err"].append(f"{m.name} : {e}")
            apres = [K.to_segs(p) for p in L.paths(lay)]
            rec["masters"][m.name] = gestes(avant, apres, jour)
            lay.shapes = [K.from_segs(x) for x in avant] + [
                sh for sh in lay.shapes if not hasattr(sh, "nodes")]
        out[nom] = rec
    return out


def resume(rec):
    """Le segment le plus long tourne, et son geste, sur les quatre masters."""
    pire = None
    for mn, gs in rec["masters"].items():
        for gg in gs:
            if "err" in gg:
                continue
            if pire is None or gg["lg"] > pire["lg"]:
                pire = dict(gg, master=mn)
    return pire


def deficits(rec):
    """Les masters ou la sortante N'ATTEINT PAS sa cible.

    CETTE COLONNE EXISTE PARCE QU'UN MAXIMUM L'AVAIT CACHEE. `mesure_haut_titrage`
    garde le PIRE de chaque geste sur les quatre masters, donc une sortie courte
    dans un master clair disparait derriere une sortie pleine dans un gras : la
    passation a ecrit au trente-cinquieme tour que la sortante tient sa promesse
    partout, a 44,0 et 32,0 unites, sur les 48 glyphes et les huit masters. Elle
    ne la tient pas : huit glyphe-masters sortent court, et le t italique
    ExtraLight rend 17,0 unites pour 32 demandees. Septieme forme du scalaire qui
    cache l'essentiel dans ce projet, et le quatorzieme chiffre corrige.

    La cause est unique et ce n'est pas la lettre : `lot4.angle_pour_depassement`
    borne sa dichotomie a 45 degres en dur et RETOURNE CETTE BORNE quand la cible
    n'y est pas atteinte, au lieu de dire qu'il refuse. Porte a 70 degres, le
    meme calcul atteint la cible dans les huit cas, a des angles de 45,4 a 67,4
    degres. C'est le point ouvert 53, qui mord ici pour la premiere fois.
    """
    out = []
    for mn, gs in rec["masters"].items():
        for gg in gs:
            if "err" in gg or gg["sortie"] is None:
                continue
            if gg["sortie"] < rec["dem"] - 0.5:
                out.append((mn, gg["theta"], gg["sortie"]))
    return sorted(out)


def imprimer(lab, res, titre):
    print(f"\n=== {lab} · {titre} · {len(res)} glyphes")
    print(f"{'glyphe':14s} {'dem':>4s} {'segments':>8s} "
          f"{'lg max':>7s} {'master':>16s} {'theta':>6s} {'sortie':>7s} "
          f"{'depl':>6s} {'dx':>7s} {'dy':>7s}")
    lignes = []
    for nom, rec in sorted(res.items()):
        p = resume(rec)
        n_seg = max((len([g for g in gs if "err" not in g])
                     for gs in rec["masters"].values()), default=0)
        if p is None:
            print(f"{nom:14s} {rec['dem']:4.0f} {n_seg:8d}   "
                  f"aucun segment tourne")
            continue
        print(f"{nom:14s} {rec['dem']:4.0f} {n_seg:8d} "
              f"{p['lg']:7.1f} {p['master']:>16s} "
              f"{(p['theta'] or 0):6.1f} {(p['sortie'] or 0):7.1f} "
              f"{p['depl']:6.1f} {p['dx']:7.1f} {p['dy']:7.1f}")
        lignes.append((nom, p["lg"]))
        for mn, th, so in deficits(rec):
            print(f"               !! SORT COURT  {mn:18s} theta {th:5.1f} "
                  f"-> {so:.1f} u pour {rec['dem']:.0f} demandees "
                  f"({so / rec['dem'] * 100:.0f} %)")
        for e in rec["err"]:
            print(f"               !! {e}")
    return lignes


def main():
    tous = "--tous" in sys.argv
    etalon = "--etalon" in sys.argv or tous
    isrcs = (0, 1) if (tous or "--italique" not in sys.argv and
                       "--romain" in sys.argv) else \
            ((1,) if "--italique" in sys.argv else (0,))
    if tous:
        isrcs = (0, 1)
    tout = {}
    for isrc in isrcs:
        lab, amont, _projet, binaire = MT.SOURCES[isrc]
        if not os.path.exists(amont):
            print(f"!! source absente : {amont}")
            print("   Rien n'est mesure. Ce n'est pas un zero, c'est un "
                  "NON MESURE.")
            return
        noms = lot(lab, amont, binaire)
        if noms is None:
            return
        # POINT DE DEPART, corrige au cinquante-huitieme tour, point 101. Ce
        # script mesurait la sortante sur l'Atkinson BRUT, donc sur un geste
        # que la chaine n'applique pas : le lot 2 et les approches modifient 30
        # des 118 glyphes du perimetre AVANT la fusion, et la longueur du
        # segment tourne -- la grandeur meme que ce script existe pour lire --
        # est celle qui change le plus. Le `A` romain passe de 57,0 unites de
        # corde a 69,2 en ExtraLight, et l'angle de 30,9 degres a 11,9.
        #
        # L'etalon, lui, garde tout son sens : il est tire des memes glyphes
        # lus dans le meme etat, donc la fourchette et le lot se comparent.
        font = MT.etat_avant_fusion(isrc)
        if font is None:
            print(f"!! {lab} : l'etat d'avant fusion ne se reconstruit pas. "
                  f"Rien n'est mesure. Ce n'est pas un zero, c'est un "
                  f"NON MESURE.")
            return
        res = par_glyphe(font, noms)
        avec = {n: r for n, r in res.items() if resume(r) is not None}
        sans = sorted(n for n in res if resume(res[n]) is None)
        for titre, ens in FAMILLES:
            sous = {n: r for n, r in avec.items() if n in ens}
            if sous:
                imprimer(lab, sous, titre)
        reste = {n: r for n, r in avec.items()
                 if not any(n in e for _t, e in FAMILLES)}
        if reste:
            imprimer(lab, reste, "NON RANGE dans une famille -- a verifier")
        print(f"\n  {len(avec)} glyphes recoivent la sortante, "
              f"{len(sans)} n'en recoivent aucune :")
        print("    " + " ".join(sans))
        tout[lab] = avec

        if etalon:
            ecr = ecrits_a_sortante(lab, amont, binaire)
            rese = par_glyphe(font, ecr)
            avec_e = {n: r for n, r in rese.items() if resume(r) is not None}
            lg = imprimer(lab, avec_e, "ETALON : deja arrete et valide")
            if lg:
                lg.sort(key=lambda t: t[1])
                print(f"\n  fourchette des longueurs deja validees : "
                      f"{lg[0][1]:.0f} u ({lg[0][0]}) a {lg[-1][1]:.0f} u "
                      f"({lg[-1][0]})")
                seuil = lg[-1][1]
                au_dela = sorted(
                    ((n, resume(r)["lg"]) for n, r in avec.items()
                     if resume(r)["lg"] > seuil), key=lambda t: -t[1])
                print(f"  glyphes du lot au-dela de cette fourchette : "
                      f"{len(au_dela)} sur {len(avec)}")
                for n, v in au_dela:
                    print(f"     {n:14s} {v:7.1f} u  "
                          f"= {v / seuil:4.1f}x le plus long deja valide")
    return tout


if __name__ == "__main__":
    main()
