#!/usr/bin/env python3
"""Le regime du HAUT sur tout le lot de propagation. Trente-cinquieme tour.

Separe, glyphe par glyphe et master par master, ce que la coupe SORTANTE fait
de ce que la coupe RENTRANTE du haut fait. Les deux etaient confondues dans la
mesure de regime du trente-quatrieme tour, qui prend le deplacement maximal
tous gestes melanges : elle decrivait donc le haut en croyant decrire la
sortante, et c'est ce que le point ouvert 63 a ecrit.

CE QUI SEPARE LES DEUX GESTES, dans le journal de `couper_alignements` : une
sortante y ecrit la chaine "sort de N", une rentrante y ecrit un nombre. La
sortante a une cible en unites depuis le neuvieme tour ; la rentrante est
restee a l'angle constant du lot 2, ou elle ne coupe que des bouts courts.
Appliquee a une FACE de barre entiere, sa profondeur vaut longueur x tan(theta).

LES TROIS REGIMES sont le parametre `haut` de
`mesure_titrage.appliquer_reglage`, seul endroit qui resout le reglage :
"actuel" l'angle constant, "aucune" le haut intact, "unites" la meme cible en
unites que la sortante.

LE RAPPORT AU DEPASSEMENT DEMANDE est la grandeur, et non les unites : une
capitale demande 44 unites quand un bas de casse en demande 32, donc un seuil
absolu classerait les capitales plus severement pour une raison etrangere a
leur dessin. Trente-quatrieme tour.

CE QUI EST MESURE SUR LES QUATRE MASTERS et non sur les deux graisses d'une
planche : la descente croit avec la graisse, la barre s'epaississant, donc un
meme angle donne quatre resultats.

    python3 mesure_haut_titrage.py                 les trois regimes, romain
    python3 mesure_haut_titrage.py --italique      idem, italique
    python3 mesure_haut_titrage.py --regime unites un seul regime

Le plafond d'un appel du bac a sable est de trois minutes : un regime par
appel tient, les trois d'un coup peuvent ne pas tenir. Le script imprime son
temps pour que ce soit lisible plutot que devine.
"""

import os
import sys
import time

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coupe as K
import lot2 as L
import lot4 as Q
import mesure_titrage as MT

REGIMES = ("actuel", "aucune", "unites")


def lot(lab, amont, binaire):
    """Les glyphes touches, dans le perimetre, que rien n'a encore ecrit."""
    r = MT.analyser(lab, amont, binaire, verbeux=False)
    if r is None:
        return None
    ecrits = set(Q.ETENDU) | set(Q.PRESCRIPTIONS)
    return sorted(n for n in r["touche"]
                  if n not in ecrits and Q.dans_le_titrage(n))


def partage(journal):
    """(sortie, descente, theta, notes, notes_bas) : la sortante d'un cote, le
    haut de l'autre. Rendre un seul maximum melangerait un geste qui tient sa
    promesse et un geste qui ne l'a jamais eue.

    LES NOTES AUSSI SE SEPARENT, et c'est le correctif du trente-sixieme tour.
    `couper_alignements` journalise depuis ce tour la saturation de la SORTANTE ;
    versee dans le meme sac que les refus du haut, elle sortait imprimee "haut
    refuse : sortie SATUREE", qui attribue au haut ce que le bas a fait. Un meme
    libelle pour deux causes est le defaut le plus tenace de ce projet, et il
    serait retombe le jour meme ou le journal a gagne une note."""
    sortie = descente = theta = None
    notes, notes_bas = set(), set()
    for (_n, _i, th, val, _sn) in journal:
        if isinstance(val, str) and val.startswith("sort de"):
            v = float(val.split()[-1])
            sortie = v if sortie is None else max(sortie, v)
        elif isinstance(th, str) and th.startswith("sortie SATUREE"):
            notes_bas.add(th)
        elif isinstance(th, str):
            notes.add(th)
        else:
            s = str(val)
            if "SATURE" in s:
                notes.add("SATURE")
                v = float(s.split()[0])
            else:
                v = float(val)
            descente = v if descente is None else max(descente, v)
            theta = float(th) if theta is None else max(theta, float(th))
    return sortie, descente, theta, notes, notes_bas


def mesurer(font, noms, regime):
    """Par glyphe : le pire de chaque geste sur les quatre masters."""
    out = {}
    for nom in noms:
        g = font.glyphs[nom]
        dem = Q.depassement_pour(nom)
        pires = dict(sortie=None, descente=None, theta=None, notes=set(),
                     notes_bas=set(), vides=0, calques=0)
        for m in font.masters:
            lay = next((l for l in g.layers if l.layerId == m.id), None)
            if lay is None:
                continue
            av = [K.to_segs(p) for p in L.paths(lay)]
            jour = []
            try:
                MT.appliquer_reglage(lay, nom, m, haut=regime, journal=jour)
            except Exception as e:
                jour.append((nom, -1, f"echec {e}", 0.0, 0))
            s, de, th, notes, notes_bas = partage(jour)
            pires["calques"] += 1
            if not jour:
                pires["vides"] += 1
            for cle, v in (("sortie", s), ("descente", de), ("theta", th)):
                if v is not None:
                    pires[cle] = v if pires[cle] is None else max(pires[cle], v)
            pires["notes"] |= notes
            pires["notes_bas"] |= {f"{m.name} : {n}" for n in notes_bas}
            lay.shapes = [K.from_segs(x) for x in av] + [
                sh for sh in lay.shapes if not hasattr(sh, "nodes")]
        pires["dem"] = dem
        out[nom] = pires
    return out


def imprimer(lab, regime, res):
    print(f"\n=== {lab} · regime du haut : {regime} · {len(res)} glyphes")
    print(f"{'glyphe':16s} {'dem':>4s} {'sortante':>9s} {'x':>5s} "
          f"{'haut':>8s} {'x':>5s} {'theta':>6s}  etat")
    pire_s = pire_h = 0.0
    bas = 0
    compte = {}
    for nom, p in sorted(res.items()):
        dem = p["dem"]
        rs = p["sortie"] / dem if p["sortie"] else 0.0
        rh = p["descente"] / dem if p["descente"] else 0.0
        pire_s, pire_h = max(pire_s, rs), max(pire_h, rh)
        if p["vides"] == p["calques"]:
            etat = "aucun segment designe, aucun master"
        elif p["notes"] == {"haut non traite"}:
            # Le regime "aucune" ecrit sa propre note dans le journal, et le
            # premier jet la classait comme un refus : il annoncait 41 refus
            # dans un regime qui ne refuse rien. Une note n'est pas un defaut.
            etat = "haut non traite par le regime"
        elif p["descente"] is None and p["notes"]:
            etat = "haut refuse : " + ", ".join(sorted(p["notes"]))
        elif p["descente"] is None:
            etat = ("haut non traite par le regime" if regime == "aucune"
                    else "aucun segment haut designe")
        elif rh > 1.0:
            etat = "HAUT PLUS PROFOND QUE LE DEPASSEMENT"
        else:
            etat = "haut dans le depassement"
        if p["notes"] and p["descente"] is not None:
            etat += "  (" + ", ".join(sorted(p["notes"])) + ")"
        compte[etat.split("  (")[0]] = compte.get(etat.split("  (")[0], 0) + 1
        print(f"{nom:16s} {dem:4.0f} "
              f"{(p['sortie'] or 0):9.1f} {rs:5.2f} "
              f"{(p['descente'] or 0):8.1f} {rh:5.2f} "
              f"{(p['theta'] or 0):6.1f}  {etat}")
        for n in sorted(p.get("notes_bas", ())):
            print(f"{'':16s} !! LE BAS, ET NON LE HAUT : {n}")
            bas += 1
    print(f"\n  pire rapport : sortante {pire_s:.2f}x · haut {pire_h:.2f}x")
    if bas:
        print(f"  {bas} sortante(s) SATUREE(S) par la borne de "
              f"{Q.BORNE_SORTIE:.0f} degres : la colonne 'sortante' n'est pas "
              f"la cible demandee sur ces glyphe-masters.")
    for k, v in sorted(compte.items(), key=lambda kv: -kv[1]):
        print(f"    {v:3d}  {k}")
    return pire_s, pire_h


def main():
    isrc = 1 if "--italique" in sys.argv else 0
    regimes = REGIMES
    if "--regime" in sys.argv:
        regimes = (sys.argv[sys.argv.index("--regime") + 1],)
    lab, amont, _projet, binaire = MT.SOURCES[isrc]
    if not os.path.exists(amont):
        print(f"!! source absente : {amont}")
        print("   Rien n'est mesure. Ce n'est pas un zero, c'est un NON MESURE.")
        return
    noms = lot(lab, amont, binaire)
    if noms is None:
        return
    with open(amont, encoding="utf-8") as fh:
        font = glyphsLib.load(fh)
    bilan = {}
    for regime in regimes:
        t0 = time.time()
        res = mesurer(font, noms, regime)
        bilan[regime] = imprimer(lab, regime, res)
        print(f"  ({time.time() - t0:.0f} s)")
    if len(bilan) > 1:
        print("\n--- le pire rapport au depassement demande, par regime")
        for regime, (ps, ph) in bilan.items():
            print(f"    {regime:8s} sortante {ps:.2f}x · haut {ph:.2f}x")


if __name__ == "__main__":
    main()
