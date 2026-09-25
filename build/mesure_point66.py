#!/usr/bin/env python3
"""Point ouvert 66 : ce que le POINT DE DEPART change au titrage.

Les planches et les mesures de titrage partent de la source AMONT, Atkinson
brut, depuis le trente-quatrieme tour. Le livrable part de `Temoin.glyphs` :
`mesure_poids_titrage.doubler` copie le glyphe du projet, coupe texte comprise,
et `couper_double` applique le reglage de titrage par-dessus. Personne n'a
jamais arbitre ce point de depart -- il a ete herite, et il a tenu trois tours,
pendant lesquels le perimetre, le regime du haut et les onze derogations ont ete
tranches sur des formes qui ne sont pas celles du livrable.

CE QUE CE SCRIPT MESURE, et ce qu'il ne mesure pas. Il ne decide rien et
n'ecrit rien. Il rejoue le reglage general de titrage DEUX FOIS sur chaque
glyphe-master -- une fois depuis l'amont, une fois depuis le projet -- et
compare. Il ne bascule aucun script : le basculement se mesure avant d'etre
ecrit, et sur l'etat servi huit localisateurs du projet ne designent plus leur
cible.

NEUF VOLETS, un par question que le point 66 pose :

  1  CE QUE LE TEXTE PORTE DEJA, sous le geste de titrage, en deplacement de
     noeud entre l'amont et le projet. C'est la grandeur du trente-sixieme
     tour -- le A, le H, le N et le p y tombent a 24,0 pile et le X a 23,9, ce
     qui ne colle qu'avec elle. Les QUATRE masters sont imprimes : un maximum
     sur les masters cache un deficit dans les clairs, et c'est ce qui a fait
     ecrire au trente-cinquieme tour que la sortante tient sa promesse partout.
  2  LA SORTANTE DU BAS depuis chaque depart : le nombre de gestes, le segment
     designe, l'angle, le depassement obtenu.
  3  LE REGIME DU HAUT depuis chaque depart : ce que `partage` range du cote du
     haut, notes de refus comprises.
  4  L'INERTIE DES ONZE DEROGATIONS depuis le projet, mesuree comme la section 8
     de `check_perimetre` : le regime du bas force au defaut, ce qui separe une
     sortante ECARTEE par derogation d'une sortante que la geometrie ne designe
     pas.
  5  CE QUE L'AMONT NE PEUT PAS MONTRER : les glyphes qui entreraient dans le
     geste par le seul effet du texte, et les glyphes que le projet AJOUTE --
     les petites capitales, qu'aucune mesure partie de l'amont n'a jamais vues.
  6  LA CIBLE EST-ELLE TENUE, dans les deux sens. Le trente-sixieme tour a
     corrige la borne haute ; la borne basse de 0,5 degre n'a jamais ete
     regardee, et elle ne peut mordre que sur un bout DEJA coupe.
  7  POURQUOI un bout cesse d'etre designe, mesure sur les deux filtres de
     `loc_alignement`, avec le depassement que le texte a DEJA donne au bout en
     regard de la cible du titrage.
  8  LE TEXTE ET LE TITRAGE INCLINENT-ILS DU MEME COTE. Trouve par Nicolas sur
     la planche : sur le pied droit du n, le texte fait descendre le coin
     DROIT et le titrage le coin GAUCHE. Le depassement obtenu est le meme des
     deux cotes, donc aucun chiffre du projet ne pouvait le dire.
  9  CE QUE PARTIR D'ATKINSON PERDRAIT : les gestes de texte que le titrage
     reprend, parce qu'il vise le meme bout, et ceux qui sont poses ailleurs et
     disparaitraient.

LA LISTE DES GLYPHES VIENT DE L'AMONT, et c'est un choix qui se dit : ce sont
les 69 du perimetre arrete que la regle geometrique attrape directement, tels
que le trente-quatrieme tour les a etablis. Un glyphe que l'amont ne designait
pas et que le projet designerait est cherche a part, volet 5, au lieu d'etre
tu.

LE TROISIEME CHIFFRE DE CHAQUE COMPARAISON EST LE COMPTE DES IDENTIQUES. Un
controle doit distinguer "mesure et conforme" de "pas mesure", et une source
absente ne rend rien ici.

    python3 mesure_point66.py                  les deux sources, les neuf volets
    python3 mesure_point66.py --volet 1        un volet seul
    python3 mesure_point66.py --source romain
    python3 mesure_point66.py --detail         tout, y compris ce qui ne change pas
"""

import argparse
import math
import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coupe as K
import lot2 as L
import lot4 as Q
import mesure_titrage as MT
import mesure_haut_titrage as MH
import mesure_sortante_lot as MS
import check_perimetre as CP

ICI = os.path.dirname(os.path.abspath(__file__))


def charger(chemin):
    if not os.path.exists(chemin):
        print(f"!! source absente : {chemin}")
        print("   Ne rien conclure d'un controle qui n'a pas lu sa source.")
        return None
    with open(chemin, encoding="utf-8") as fh:
        return glyphsLib.load(fh)


def calque(font, nom, master_nom):
    """Le calque d'un master DESIGNE PAR SON NOM.

    Les deux sources n'ont aucune raison de partager leurs identifiants de
    master : `make_temoin` reecrit la source. Apparier par le nom, et lever
    quand un nom manque, plutot que de rendre un calque plausible.
    """
    g = font.glyphs[nom]
    if g is None:
        return None
    mid = {m.id: m for m in font.masters}
    for l in g.layers:
        m = mid.get(l.layerId)
        if m is not None and m.name == master_nom:
            return l, m
    return None


def noms_masters(font):
    return [m.name for m in font.masters]


def noeuds(lay):
    return [(float(n.position.x), float(n.position.y))
            for p in L.paths(lay) for n in p.nodes]


def ecart_dessin(la, lp):
    """Le plus grand deplacement de noeud entre le calque amont et celui du
    projet. Rend None quand les comptes de noeuds different : une topologie qui
    diverge ne se mesure pas par un appariement d'indices, elle se signale."""
    a, b = noeuds(la), noeuds(lp)
    if len(a) != len(b):
        return None
    if not a:
        return 0.0
    return max(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(a, b))


def echantillon(lay, n=64):
    out = []
    for p in L.paths(lay):
        for s in K.to_segs(p):
            for t in range(n):
                out.append(K.bez(s, t / float(n)))
    return out


def ecart_forme(la, lp):
    """L'ECART DE FORME, et ce n'est PAS le deplacement de noeud.

    Hausdorff symetrique entre les deux contours echantillonnes : la plus
    grande distance d'un point d'un dessin a l'autre dessin. Elle existe quand
    les comptes de noeuds different, ou le deplacement de noeud n'a pas de sens.

    Les deux grandeurs sont justes et ne donnent pas le meme chiffre -- c'est
    le 1,35x contre 1,00x du trente-cinquieme tour sous une autre forme -- donc
    elles ne se melangent jamais dans une meme colonne. Sur le L au Bold, le
    coin de la barre basse recule de 88,0 unites le long de la ligne de base et
    cet ecart-ci vaut 58,5 : la forme ne s'ecarte que de ce que la coupe retire,
    et le trajet du coin n'est pas l'ecart des deux dessins.
    """
    a, b = echantillon(la), echantillon(lp)
    if not a or not b:
        return None
    d1 = max(min(math.hypot(q[0] - p[0], q[1] - p[1]) for q in b) for p in a)
    d2 = max(min(math.hypot(q[0] - p[0], q[1] - p[1]) for q in a) for p in b)
    return max(d1, d2)


def appliquer(lay, m, nom, bas=None, haut=None):
    """Le reglage de titrage sur un calque, rendu puis REPOSE tel quel.

    Rend les gestes lus par `mesure_sortante_lot.gestes` -- le producteur, et
    non une seconde lecture du journal -- plus le partage haut/bas de
    `mesure_haut_titrage.partage`.
    """
    snap = [K.to_segs(p) for p in L.paths(lay)]
    jour, err = [], None
    try:
        MT.appliquer_reglage(lay, nom, m, journal=jour, bas=bas, haut=haut)
    except Exception as e:                                    # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    apres = [K.to_segs(p) for p in L.paths(lay)]
    gs = [g for g in MS.gestes(snap, apres, jour) if "err" not in g]
    erreurs = [g["err"] for g in MS.gestes(snap, apres, jour) if "err" in g]
    s, de, th, nt, nb = MH.partage(jour)
    lay.shapes = [K.from_segs(x) for x in snap] + [
        sh for sh in lay.shapes if not hasattr(sh, "nodes")]
    return dict(gestes=gs, sortie=s, descente=de, theta=th, notes=nt,
                notes_bas=nb, err=err, erreurs=erreurs, journal=list(jour))


def signature_bas(r):
    """Ce qui identifie la sortante d'un glyphe-master, pour comparer deux
    departs : un enregistrement par segment tourne, (indice, longueur, angle,
    depassement). L'indice vient du journal, jamais de l'ordre de parcours."""
    out = []
    for g in r["gestes"]:
        if g.get("sortie") is None:
            continue
        out.append((g["i"], round(g["lg"], 1), round(g["theta"] or 0.0, 2),
                    round(g["sortie"], 1)))
    return tuple(sorted(out))


def cause(ra, rp, sa, sp):
    """POURQUOI les deux departs different, lu dans le journal et non deduit.

    Un meme libelle pour plusieurs causes est le defaut le plus tenace de ce
    projet. Quatre sont distinguees, et un journal VIDE n'est pas un refus :
    c'est `loc_alignement` qui ne designe plus rien, le bout coupe par le texte
    n'etant plus reconnu par le filtre d'orientation. C'est le piege des huit
    localisateurs du vingt-neuvieme tour, sur le chemin du titrage.
    """
    perdus = {x[0] for x in sa} - {x[0] for x in sp}
    if perdus:
        vus = {e[1] for e in rp["journal"]}
        hauts = {e[1] for e in rp["journal"]
                 if isinstance(e[2], str) and e[2] == "haut non traite"}
        refus = {e[1] for e in rp["journal"]
                 if isinstance(e[2], str) and e[2] != "haut non traite"}
        n = f"{len(perdus)} bout(s) perdu(s) : " if len(sa) != len(perdus) else ""
        if perdus & refus:
            return n + "le projet designe le bout et REFUSE la sortante"
        if perdus & hauts:
            return n + ("le projet designe le bout mais son QUADRANT a "
                        "change : il passe en rentrante")
        if not (perdus & vus):
            return n + "le projet ne DESIGNE plus le bout"
        return n + "le projet designe le bout sans le couper, sans note"
    if sp and not sa:
        return "le bout n'apparait que sur le projet"
    va = sorted(x[3] for x in sa)
    vp = sorted(x[3] for x in sp)
    if len(sa) != len(sp):
        return f"{len(sa)} geste(s) depuis l'amont, {len(sp)} depuis le projet"
    if va != vp:
        return f"depassement obtenu : {va} contre {vp}"
    return "meme depassement, autre segment ou autre angle"


def signature_haut(r):
    """Le cote haut : la descente obtenue, son angle, et les notes de refus."""
    return (None if r["descente"] is None else round(r["descente"], 1),
            None if r["theta"] is None else round(r["theta"], 2),
            tuple(sorted(r["notes"])))


# ----------------------------------------------------------------- les volets

def volet1(lab, fa, fp, noms, detail):
    print(f"\n=== {lab} · VOLET 1 · ce que le dessin de texte porte deja, "
          f"sous le geste de titrage")
    print("    deplacement de noeud entre l'amont et Temoin.glyphs, par master, "
          "en unites")
    ms = noms_masters(fa)
    print(f"{'glyphe':14s} " + " ".join(f"{m[:12]:>12s}" for m in ms))
    porteurs, nuls, divergents = [], [], []
    for nom in noms:
        vals = []
        for mn in ms:
            ca, cp = calque(fa, nom, mn), calque(fp, nom, mn)
            if ca is None or cp is None:
                vals.append(None)
                continue
            vals.append(ecart_dessin(ca[0], cp[0]))
        if any(v is None for v in vals):
            # topologie divergente : le deplacement de noeud n'a pas de sens,
            # l'ecart de forme en a un. La ligne le dit au lieu de rendre un
            # blanc, et la grandeur est nommee pour qu'elle ne se compare pas
            # aux autres colonnes.
            autres = []
            for mn in ms:
                ca, cp = calque(fa, nom, mn), calque(fp, nom, mn)
                autres.append(None if ca is None or cp is None
                              else ecart_forme(ca[0], cp[0]))
            divergents.append((nom, vals, autres))
            porteurs.append((nom, max((v for v in autres if v), default=0.0)))
            continue
        pire = max((v for v in vals if v is not None), default=0.0)
        if pire < 0.05:
            nuls.append(nom)
            if not detail:
                continue
        else:
            porteurs.append((nom, pire))
        cols = " ".join("     topolo." if v is None else f"{v:12.1f}"
                        for v in vals)
        print(f"{nom:14s} {cols}")
    for nom, _vals, autres in divergents:
        cols = " ".join("           ?" if v is None else f"{v:12.1f}"
                        for v in autres)
        print(f"{nom:14s} {cols}   <-- ECART DE FORME, autre grandeur")
    print(f"\n  {len(porteurs)} glyphe(s) portent un geste du texte, "
          f"{len(nuls)} n'en portent aucun, sur {len(noms)} mesures.")
    if divergents:
        noms_d = " ".join(n for n, _v, _a in divergents)
        print(f"  !! topologie divergente amont/projet sur {noms_d} : le "
              f"deplacement de noeud n'y est pas defini.")
        print(f"     Leur ligne porte l'ECART DE FORME (Hausdorff symetrique), "
              f"qui ne se compare pas aux autres.")
    if nuls and not detail:
        print(f"  sans geste du texte : {' '.join(nuls)}")
    return porteurs


def volet23(lab, fa, fp, noms, detail):
    """Les volets 2 et 3 dans un seul parcours : les deux lisent le meme
    journal, et rejouer le reglage deux fois par glyphe-master pour les separer
    couterait le double sans rien prouver de plus."""
    ms = noms_masters(fa)
    ecarts_bas, ecarts_haut = [], []
    id_bas = id_haut = mesures = 0
    erreurs = []
    for nom in noms:
        for mn in ms:
            ca, cp = calque(fa, nom, mn), calque(fp, nom, mn)
            if ca is None or cp is None:
                erreurs.append(f"{nom} {mn} : calque absent d'une source")
                continue
            ra = appliquer(ca[0], ca[1], nom)
            rp = appliquer(cp[0], cp[1], nom)
            mesures += 1
            for r, ou in ((ra, "amont"), (rp, "projet")):
                if r["err"]:
                    erreurs.append(f"{nom} {mn} {ou} : {r['err']}")
                for e in r["erreurs"]:
                    erreurs.append(f"{nom} {mn} {ou} : {e}")
            sa, sp = signature_bas(ra), signature_bas(rp)
            if sa == sp:
                id_bas += 1
            else:
                ecarts_bas.append((nom, mn, sa, sp, cause(ra, rp, sa, sp)))
            ha, hp = signature_haut(ra), signature_haut(rp)
            if ha == hp:
                id_haut += 1
            else:
                ecarts_haut.append((nom, mn, ha, hp))

    print(f"\n=== {lab} · VOLET 2 · la sortante du bas, depuis chaque depart")
    print(f"    {mesures} glyphe-masters rejoues deux fois. "
          f"{id_bas} identiques, {len(ecarts_bas)} differents.")
    if ecarts_bas:
        par_cause = {}
        for _n, _m, _a, _b, c in ecarts_bas:
            par_cause[c] = par_cause.get(c, 0) + 1
        print("    par cause, mesuree dans le journal :")
        for c, n in sorted(par_cause.items(), key=lambda x: -x[1]):
            print(f"      {n:3d}  {c}")
        print(f"\n{'glyphe':14s} {'master':>16s}   "
              f"(indice, longueur, angle, sortie)")
        for nom, mn, sa, sp, c in ecarts_bas:
            print(f"{nom:14s} {mn:>16s}   amont  {sa if sa else 'aucun geste'}")
            print(f"{'':14s} {'':>16s}   projet {sp if sp else 'aucun geste'}"
                  f"   <- {c}")

    print(f"\n=== {lab} · VOLET 3 · le regime du haut, depuis chaque depart")
    print(f"    {mesures} glyphe-masters. {id_haut} identiques, "
          f"{len(ecarts_haut)} differents.")
    if ecarts_haut:
        print(f"\n{'glyphe':14s} {'master':>16s}   (descente, angle, notes)")
        for nom, mn, ha, hp in ecarts_haut:
            print(f"{nom:14s} {mn:>16s}   amont  {ha}")
            print(f"{'':14s} {'':>16s}   projet {hp}")
    if erreurs:
        print(f"\n  !! {len(erreurs)} incident(s) de mesure :")
        for e in erreurs[:40]:
            print(f"     {e}")
    return ecarts_bas, ecarts_haut


def volet4(lab, fa, fp, detail):
    """Les onze derogations restent-elles inertes quand on part du projet ?

    Meme mesure que la section 8 de `check_perimetre` : le regime du bas force
    au defaut rejoue ce que la geometrie DESIGNERAIT sans la prescription, ce
    qui separe une sortante ecartee par derogation d'une sortante que rien ne
    designe. La liste attendue vient de `check_perimetre.BRUT_ATTENDU`, qui vit
    dans le controle et non dans la table : lire la table pour verifier la table
    ne verifie rien.
    """
    print(f"\n=== {lab} · VOLET 4 · les onze derogations, depuis chaque depart")
    ms = noms_masters(fa)
    attendus = sorted(CP.BRUT_ATTENDU)
    lignes, ecarts = [], []
    for nom in attendus:
        for mn in ms:
            ca, cp = calque(fa, nom, mn), calque(fp, nom, mn)
            if ca is None or cp is None:
                ecarts.append(f"{nom} {mn} : calque absent d'une source")
                continue
            # etat ecrit : la derogation doit rendre le bas inerte
            ea = signature_bas(appliquer(ca[0], ca[1], nom))
            ep = signature_bas(appliquer(cp[0], cp[1], nom))
            # bas force au defaut : la geometrie designe-t-elle un bout ?
            fa_ = signature_bas(appliquer(ca[0], ca[1], nom, bas="bas"))
            fp_ = signature_bas(appliquer(cp[0], cp[1], nom, bas="bas"))
            lignes.append((nom, mn, ea, ep, fa_, fp_))
            if ea or ep:
                ecarts.append(f"{nom} {mn} : la derogation ne rend pas le bas "
                              f"inerte (amont {ea}, projet {ep})")
            if bool(fa_) != bool(fp_):
                ecarts.append(f"{nom} {mn} : le bas force designe "
                              f"{'amont' if fa_ else 'projet'} seulement "
                              f"(amont {len(fa_)} geste(s), "
                              f"projet {len(fp_)} geste(s))")
    inertes = sum(1 for _n, _m, ea, ep, _a, _b in lignes if not ea and not ep)
    designes_a = sum(1 for l in lignes if l[4])
    designes_p = sum(1 for l in lignes if l[5])
    print(f"    {len(lignes)} glyphe-masters sur les onze derogations.")
    print(f"    inertes dans les deux departs : {inertes}/{len(lignes)}")
    print(f"    bas force au defaut, la geometrie designe un bout : "
          f"amont {designes_a}, projet {designes_p}")
    if detail:
        print(f"\n{'glyphe':14s} {'master':>16s}  ecrit-amont ecrit-projet "
              f"force-amont force-projet")
        for nom, mn, ea, ep, a, b in lignes:
            print(f"{nom:14s} {mn:>16s}  {len(ea):11d} {len(ep):12d} "
                  f"{len(a):12d} {len(b):13d}")
    if ecarts:
        print(f"\n  !! {len(ecarts)} ecart(s) :")
        for e in ecarts:
            print(f"     {e}")
    else:
        print("    aucun ecart : les onze derogations font la meme chose "
              "depuis les deux departs.")
    return ecarts


def volet5(lab, fa, fp, noms, servi):
    """Ce que l'amont ne peut pas montrer, en deux cas qui ne se melangent pas.

    5a  Un glyphe present dans les DEUX sources, que l'amont ne designe pas et
        que le projet designerait : le dessin de texte ferait alors ENTRER un
        glyphe dans le geste de titrage, et il ne serait dans aucune liste.

    5b  Un glyphe que le projet AJOUTE, donc absent de l'amont : les quarante-
        quatre petites capitales du lot 3. `mesure_titrage` les range deja dans
        le perimetre par heritage -- une petite capitale est touchee si et
        seulement si sa capitale l'est -- mais AUCUNE mesure de titrage n'a
        jamais pu voir leur geste, puisque toutes lisent l'amont. Une petite
        capitale n'est pas sa capitale a l'echelle : le lot 3 la derive par un
        rapport, et sa terminaison n'a pas la meme largeur.
    """
    print(f"\n=== {lab} · VOLET 5 · ce que l'amont ne peut pas montrer")
    ms = noms_masters(fa)
    entrants, ajoutes = [], []
    for nom in servi:
        if nom in noms or not Q.dans_le_titrage(nom):
            continue
        absent_amont = fa.glyphs[nom] is None
        for mn in ms:
            cp = calque(fp, nom, mn)
            if cp is None or not L.paths(cp[0]):
                continue
            r = appliquer(cp[0], cp[1], nom)
            if r["gestes"] or r["sortie"] is not None:
                (ajoutes if absent_amont else entrants).append(
                    (nom, mn, len(r["gestes"]), r["sortie"]))
                break
    print(f"\n  5a · glyphes des deux sources que seul le projet designerait : "
          f"{len(entrants)}")
    for nom, mn, n, s in entrants:
        print(f"      {nom:14s} {mn:>16s}  {n} geste(s), sortie {s}")
    if not entrants:
        print("      aucun. Le dessin de texte ne fait entrer aucun glyphe "
              "present en amont dans le geste de titrage.")
    print(f"\n  5b · glyphes que le projet AJOUTE et qui recoivent un geste, "
          f"invisibles a toute mesure partie de l'amont : {len(ajoutes)}")
    if ajoutes:
        sorties = sorted({s for _n, _m, _c, s in ajoutes if s is not None})
        print(f"      depassements obtenus : {sorties}")
        print("      " + " ".join(n for n, _m, _c, _s in ajoutes))
    return entrants, ajoutes


def volet6(lab, fa, fp, noms, pcs):
    """LA CIBLE EST-ELLE TENUE, depuis chaque depart, dans les deux sens.

    Le trente-sixieme tour a corrige la borne HAUTE : `angle_pour_depassement`
    bornait sa dichotomie a 45 degres et retournait cette borne au lieu de
    refuser, donc onze glyphe-masters sortaient court sans que rien ne le dise.
    Elle a une borne BASSE, `lo = 0.5`, et cette borne-la n'a jamais ete
    regardee : quand le bout est DEJA coupe par le texte, l'angle minimal
    depasse deja la cible, la dichotomie converge vers 0,5 degre et la fonction
    rend `atteint=True` sur une sortie TROP LONGUE. Le defaut ne peut pas
    exister sur l'amont, ou aucun bout n'est pre-coupe : il n'apparait que sur
    le dessin servi, donc il appartient au point 66.
    """
    print(f"\n=== {lab} · VOLET 6 · la cible est-elle tenue, depuis chaque "
          f"depart")
    lignes = []
    for ou, font, liste in (("amont", fa, noms), ("projet", fp, noms),
                            ("projet", fp, pcs)):
        court, long_ = [], []
        for nom in liste:
            dem = Q.depassement_pour(nom)
            for mn in noms_masters(font):
                c = calque(font, nom, mn)
                if c is None:
                    continue
                for (_i, _lg, th, so) in signature_bas(appliquer(c[0], c[1],
                                                                 nom)):
                    if so < dem - 0.5:
                        court.append((nom, mn, th, so, dem))
                    elif so > dem + 0.5:
                        long_.append((nom, mn, th, so, dem))
        quoi = "petites capitales" if liste is pcs else "69 touches"
        lignes.append((ou, quoi, court, long_))
    for ou, quoi, court, long_ in lignes:
        print(f"\n  depart {ou:7s} · {quoi:18s} : "
              f"{len(court)} sortie(s) COURTE(S), {len(long_)} TROP LONGUE(S)")
        for nom, mn, th, so, dem in court:
            print(f"      court  {nom:14s} {mn:>16s} theta {th:5.1f} -> "
                  f"{so:.0f} u pour {dem:.0f} ({so / dem * 100:.0f} %)")
        for nom, mn, th, so, dem in long_:
            print(f"      long   {nom:14s} {mn:>16s} theta {th:5.1f} -> "
                  f"{so:.0f} u pour {dem:.0f} ({so / dem * 100:.0f} %)")
    return lignes


def volet7(lab, fa, fp, noms):
    """POURQUOI un bout cesse d'etre designe, mesure sur les deux filtres.

    `lot4.loc_alignement` designe par deux conditions, et les confondre serait
    la huitieme fois que ce projet met un seul libelle sur deux causes :

      ORIENTATION  le segment doit etre presque horizontal, |dy| <= 0,3 |dx|,
                   soit 16,7 degres ;
      PROXIMITE    un de ses coins doit tomber a moins de 8 unites de
                   l'alignement.

    Le geste de texte TOURNE le bout : sur un bout etroit, 24 unites de plongee
    demandent 30,9 degres, et le bout sort du filtre d'orientation. Sur un bout
    large, les memes 24 unites demandent 6 degres et il y reste. La perte du
    geste de titrage depend donc de la GRAISSE, ce qu'aucun chiffre agrege ne
    pouvait montrer.
    """
    print(f"\n=== {lab} · VOLET 7 · pourquoi le bout n'est plus designe")
    print(f"{'glyphe':14s} {'master':>16s} {'seg':>4s} "
          f"{'angle amont':>12s} {'angle projet':>13s} {'acquis':>8s} "
          f"{'cible':>6s}  filtre qui ecarte")
    lignes = []
    for nom in noms:
        for mn in noms_masters(fa):
            ca, cp = calque(fa, nom, mn), calque(fp, nom, mn)
            if ca is None or cp is None:
                continue
            ra = appliquer(ca[0], ca[1], nom)
            rp = appliquer(cp[0], cp[1], nom)
            perdus = {x[0] for x in signature_bas(ra)} - {
                x[0] for x in signature_bas(rp)}
            if not perdus:
                continue
            m = cp[1]
            hauteurs = (0.0, m.xHeight, m.capHeight)
            sa = [s for p in L.paths(ca[0]) for s in K.to_segs(p)]
            sp = [s for p in L.paths(cp[0]) for s in K.to_segs(p)]
            for i in sorted(perdus):
                if i >= len(sp) or i >= len(sa):
                    lignes.append((nom, mn, i, None, None, None, None,
                                   "indice hors du contour du projet"))
                    continue
                ang_a = abs(MS.direction(sa[i]))
                ang_p = abs(MS.direction(sp[i]))
                ang_a = min(ang_a, 180.0 - ang_a)
                ang_p = min(ang_p, 180.0 - ang_p)
                d = min(min(abs(sp[i]["p0"][1] - h), abs(sp[i]["p3"][1] - h))
                        for h in hauteurs)
                # CE QUE LE LECTEUR VERRAIT. Le geste de titrage perdu, le bout
                # garde le depassement que le TEXTE lui a deja donne. La cible
                # se mesure a l'alignement le plus proche du milieu du segment,
                # comme `couper_alignements` la mesure.
                ligne = min(hauteurs,
                            key=lambda h: abs(K.mid(sp[i])[1] - h))
                acquis = max(abs(sp[i]["p0"][1] - ligne),
                             abs(sp[i]["p3"][1] - ligne))
                quoi = []
                if ang_p > math.degrees(math.atan(0.3)):
                    quoi.append("ORIENTATION")
                if d > 8.0:
                    quoi.append("PROXIMITE")
                if sp[i]["kind"] != "line":
                    quoi.append("plus une droite")
                lignes.append((nom, mn, i, ang_a, ang_p, acquis,
                               Q.depassement_pour(nom),
                               " + ".join(quoi) or "aucun : autre cause"))
    for nom, mn, i, aa, ap_, acquis, dem, quoi in lignes:
        if aa is None:
            print(f"{nom:14s} {mn:>16s} {i:4d} {'':>12s} {'':>13s} "
                  f"{'':>8s} {'':>6s}  {quoi}")
            continue
        print(f"{nom:14s} {mn:>16s} {i:4d} {aa:11.1f}° {ap_:12.1f}° "
              f"{acquis:8.1f} {dem:6.0f}  {quoi}")
    par = {}
    for l in lignes:
        par[l[7]] = par.get(l[7], 0) + 1
    print(f"\n    {len(lignes)} bout(s) perdu(s), par filtre :")
    for q, n in sorted(par.items(), key=lambda x: -x[1]):
        print(f"      {n:3d}  {q}")
    return lignes


def coin_descendu(sa, sb, seuil=0.5):
    """Lequel des deux coins d'un segment est descendu : 'gauche', 'droite',
    'les deux' ou None.

    Le cote se lit sur l'ABSCISSE des deux coins du segment AVANT le geste, et
    non sur p0/p3 : l'ordre de parcours d'un contour n'est pas une propriete
    typographique, et il change d'un glyphe a l'autre.
    """
    coins = [(sa["p0"], sb["p0"]), (sa["p3"], sb["p3"])]
    coins.sort(key=lambda c: c[0][0])
    (gav, gap), (dav, dap) = coins
    g = (gap[1] - gav[1]) < -seuil
    dr = (dap[1] - dav[1]) < -seuil
    if g and dr:
        return "les deux"
    if g:
        return "gauche"
    if dr:
        return "droite"
    return None


def volet8(lab, fa, fp, noms, detail):
    """LE GESTE DU TEXTE ET CELUI DU TITRAGE VONT-ILS DU MEME COTE ?

    Trouve par Nicolas en regardant `planche-point66.png` : sur le pied droit du
    n, le texte fait descendre le coin DROIT et le titrage le coin GAUCHE. Les
    deux gestes s'opposent, et aucune mesure du projet ne le disait -- le
    depassement obtenu, 32 unites, est le meme des deux cotes.

    La cause est dans le choix du coin. `lot4.couper_alignements` passe par
    `sens_coin` avec le `cote` du reglage general, qui fait MONTER le coin le
    plus loin de l'axe de la lettre ; les entrees du lot 2 nomment leur coin une
    par une, arbitrees sur planche geste par geste. Rien ne garantissait
    l'accord des deux.

    La mesure porte sur le segment que le TITRAGE vise depuis l'amont, et
    compare deux gestes sur ce meme segment : celui du titrage, lu avant/apres
    sur l'amont, et celui du texte, lu entre l'amont et le projet.
    """
    print(f"\n=== {lab} · VOLET 8 · le texte et le titrage inclinent-ils du "
          f"meme cote")
    print(f"{'glyphe':14s} {'master':>16s} {'seg':>4s} {'titrage':>10s} "
          f"{'texte':>10s}  verdict")
    accord = oppose = texte_ailleurs = titrage_ailleurs = 0
    lignes = []
    for nom in noms:
        for mn in noms_masters(fa):
            ca, cp = calque(fa, nom, mn), calque(fp, nom, mn)
            if ca is None or cp is None:
                continue
            av = [s for p in L.paths(ca[0]) for s in K.to_segs(p)]
            pr = [s for p in L.paths(cp[0]) for s in K.to_segs(p)]
            ra = appliquer(ca[0], ca[1], nom)
            ap_ = [s for p in L.paths(ca[0]) for s in K.to_segs(p)]
            # `appliquer` repose le calque, donc l'etat coupe se relit ici en
            # rejouant le geste sur une copie de la liste de segments.
            snap = [K.to_segs(p) for p in L.paths(ca[0])]
            jour = []
            try:
                MT.appliquer_reglage(ca[0], nom, ca[1], journal=jour)
            except Exception:                                 # noqa: BLE001
                pass
            ap_ = [s for p in L.paths(ca[0]) for s in K.to_segs(p)]
            ca[0].shapes = [K.from_segs(x) for x in snap] + [
                sh for sh in ca[0].shapes if not hasattr(sh, "nodes")]
            for (i, _lg, _th, _so) in signature_bas(ra):
                if i >= len(ap_) or i >= len(pr) or i >= len(av):
                    continue
                ct = coin_descendu(av[i], ap_[i])
                cx = coin_descendu(av[i], pr[i])
                if cx is None:
                    verdict = "le texte ne touche pas ce bout"
                    texte_ailleurs += 1
                elif ct is None:
                    # LE CAS SYMETRIQUE MANQUAIT, ET IL TOMBAIT DANS "OPPOSES".
                    # Deux gestes ne peuvent pas aller en sens contraire quand
                    # l'un des deux n'existe pas : le titrage ne pose rien sur
                    # ce bout, il n'a donc aucun sens a contredire. Le compte
                    # rendait 8 OPPOSES, tous sur le U et tous faux.
                    #
                    # LA CAUSE EST ECRITE AILLEURS DANS LE PROJET. Le U descend
                    # de 44 unites depuis le quarante-neuvieme tour, donc son
                    # bout n'est plus sur la hauteur de capitale et
                    # `loc_alignement` ne le designe plus : un geste qui vise un
                    # alignement se desarme si on deplace sa cible avant lui.
                    # Le dessin servi est juste, c'est l'ETIQUETTE qui mentait.
                    #
                    # L'exigence ne s'affaiblit pas pour autant : elle reste
                    # "aucun bout ne recoit deux gestes de sens contraire", et
                    # un bout sans geste de titrage n'a jamais pu la violer.
                    verdict = "le titrage ne touche pas ce bout"
                    titrage_ailleurs += 1
                elif ct == cx:
                    verdict = "accord"
                    accord += 1
                else:
                    verdict = "OPPOSES"
                    oppose += 1
                lignes.append((nom, mn, i, ct, cx, verdict))
    for nom, mn, i, ct, cx, v in lignes:
        if v.startswith("le ") and v.endswith("pas ce bout") and not detail:
            continue
        print(f"{nom:14s} {mn:>16s} {i:4d} {str(ct):>10s} {str(cx):>10s}  {v}")
    print(f"\n    {accord} bout(s) ou les deux gestes vont du meme cote, "
          f"{oppose} OPPOSES, {texte_ailleurs} ou le texte ne touche pas ce "
          f"bout, {titrage_ailleurs} ou le TITRAGE ne le touche pas.")
    return lignes


def volet9(lab, fa, fp, noms, detail):
    """CE QUE L'OPTION << PARTIR D'ATKINSON >> PERDRAIT.

    Poser le geste de titrage sur la source amont rend au titrage son geste
    plein -- c'est ce que les planches montrent depuis le trente-quatrieme tour.
    Le prix est que le glyphe de titrage cesse de porter le dessin de texte.
    La question se chiffre en deux tas : les bouts que le titrage REPREND,
    puisqu'il vise le meme segment, et les gestes de texte qui seraient
    PUREMENT PERDUS, poses ailleurs sur la lettre.
    """
    print(f"\n=== {lab} · VOLET 9 · ce que partir d'Atkinson perdrait")
    repris, perdus = {}, {}
    for nom in noms:
        for mn in noms_masters(fa):
            ca, cp = calque(fa, nom, mn), calque(fp, nom, mn)
            if ca is None or cp is None:
                continue
            av = [s for p in L.paths(ca[0]) for s in K.to_segs(p)]
            pr = [s for p in L.paths(cp[0]) for s in K.to_segs(p)]
            if len(av) != len(pr):
                perdus.setdefault(nom, set()).add("topologie")
                continue
            vises = {i for (i, _l, _t, _s)
                     in signature_bas(appliquer(ca[0], ca[1], nom))}
            for i, (a, b) in enumerate(zip(av, pr)):
                if a["p0"] == b["p0"] and a["p3"] == b["p3"]:
                    continue
                # DEUX SEGMENTS SONT MODIFIES PAR UNE COUPE ET UN SEUL EST LE
                # GESTE : le segment tourne change de direction, le voisin est
                # seulement prolonge le long de sa tangente. Sans ce filtre, le
                # A sortait avec un "geste ailleurs" qui etait le flanc de son
                # pied, prolonge par sa propre plongee.
                # L'ecart d'angle se prend MODULO 180 : la direction d'une
                # corde passe par +-180 degres, et un premier jet rendait
                # 351,36 pour une rotation de 8,64 sur le sommet du fut du H.
                dt = abs(MS.direction(a) - MS.direction(b)) % 360.0
                dt = min(dt, 360.0 - dt)
                if dt <= 0.02:
                    continue
                (repris if i in vises else perdus).setdefault(
                    nom, set()).add(mn)
    tous = sorted(set(repris) | set(perdus))
    print(f"    {len(tous)} glyphe(s) du perimetre portent un geste de texte.")
    print(f"    {len(repris)} ont un geste sur un bout que le titrage vise "
          f"aussi : le titrage le REPREND, a sa propre profondeur.")
    print(f"      {' '.join(sorted(repris))}")
    seuls = sorted(set(perdus) - set(repris))
    print(f"    {len(seuls)} ont leur geste de texte AILLEURS : partir "
          f"d'Atkinson le perd entierement.")
    print(f"      {' '.join(seuls)}")
    melange = sorted(set(perdus) & set(repris))
    if melange:
        print(f"    {len(melange)} portent les deux cas a la fois : "
              f"{' '.join(melange)}")
    return repris, perdus


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["romain", "italique"])
    ap.add_argument("--volet", type=int, choices=[1,2,3,4,5,6,7,8,9])
    ap.add_argument("--detail", action="store_true")
    a = ap.parse_args()

    for isrc, (lab, amont, projet, binaire) in enumerate(MT.SOURCES):
        if a.source and lab != a.source:
            continue
        r = MT.analyser(lab, amont, binaire, verbeux=False)
        if r is None:
            print(f"!! {lab} : analyse impossible, source amont absente. "
                  f"RIEN N'EST MESURE pour cette source.")
            continue
        noms = sorted(n for n in r["touche"] if Q.dans_le_titrage(n))
        # LES DEUX TERMES DE LA COMPARAISON, et ils ne se corrigent pas de la
        # meme facon. `fa` reste l'amont BRUT : c'est l'un des deux points de
        # depart que ce script existe pour opposer, donc le point 101 ne le
        # vise pas. `fp` etait `Temoin.glyphs`, et c'est la qu'etait le defaut
        # -- la chaine y ecrit la fusion depuis le quarantieme tour, donc le
        # "geste du texte", lu comme l'ecart entre `fa` et `fp`, portait AUSSI
        # le titrage fusionne. Le script attribuait au texte ce que le titrage
        # avait fait, et c'est precisement la grandeur du volet 8.
        #
        # `etat_avant_fusion` est le terme juste : c'est ce que la chaine
        # fusionne, donc le dessin de texte et rien d'autre.
        fa, fp = charger(amont), MT.etat_avant_fusion(isrc)
        if fa is None or fp is None:
            print(f"!! {lab} : l'amont manque, ou l'etat d'avant fusion ne se "
                  f"reconstruit pas. RIEN N'EST MESURE pour cette source.")
            continue
        ma, mp = noms_masters(fa), noms_masters(fp)
        if ma != mp:
            print(f"!! {lab} : les masters different entre les deux sources, "
                  f"{ma} contre {mp}. RIEN N'EST MESURE.")
            continue
        print(f"\n{'=' * 72}")
        print(f"{lab} · {len(noms)} glyphes du perimetre touches directement · "
              f"{len(ma)} masters")
        print(f"  amont  {amont}")
        print(f"  dessin de texte : RECONSTRUIT par "
              f"mesure_titrage.etat_avant_fusion -- amont + lot 2 + approches, "
              f"l'etat que la chaine fusionne. Ce n'est PAS {projet}, ou le "
              f"geste de titrage est deja ecrit.")
        print("=" * 72)

        if a.volet in (None, 1):
            volet1(lab, fa, fp, noms, a.detail)
        if a.volet in (None, 2, 3):
            volet23(lab, fa, fp, noms, a.detail)
        if a.volet in (None, 4):
            volet4(lab, fa, fp, a.detail)
        if a.volet in (None, 5):
            volet5(lab, fa, fp, set(noms), r["servi"])
        if a.volet in (None, 6):
            pcs = sorted(n for n in r["servi"]
                         if n.endswith(".sc") and Q.dans_le_titrage(n))
            volet6(lab, fa, fp, noms, pcs)
        if a.volet in (None, 7):
            volet7(lab, fa, fp, noms)
        if a.volet in (None, 8):
            volet8(lab, fa, fp, noms, a.detail)
        if a.volet in (None, 9):
            volet9(lab, fa, fp, noms, a.detail)


if __name__ == "__main__":
    main()
