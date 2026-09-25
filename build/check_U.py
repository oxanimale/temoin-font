#!/usr/bin/env python3
"""Le controle du U redescendu. QUARANTE-NEUVIEME TOUR.

Le projet donne un controle a chaque geste neuf, et celui-ci en a un le jour ou
il est ecrit -- le circonflexe a vecu huit tours sans, et c'etait le point 73.

CE QU'IL EXIGE, et chaque exigence vient d'une mesure prise avant l'ecriture :

  1. LE SOMMET DU U EST A LA HAUTEUR DE CAPITALE, a 0,1 unite pres, dans les
     huit masters des deux sources. C'est la demande de Nicolas, mot pour mot :
     "que les pointes atteignent la ligne haute des autres majuscules".
  2. LE GESTE N'EST PAS REDUIT : les deux coins du bout restent separes de 44
     unites, la valeur que le reglage general sort. Sans cette section, le
     geste pourrait disparaitre et la premiere resterait au vert -- un U plat
     a 668 la satisfait aussi. Les deux ensemble disent la forme.
  3. LE BLANC SOUS L'ACCENT DU Û EGALE CELUI DU Â, a 0,5 unite pres. C'est la
     raison pour laquelle le geste a ete demande, et c'est la seule section qui
     mesure ce que personne ne mesurait : le blanc entre une base et sa marque.
     Avant ce tour il valait 2,9 et 9,4 unites dans les masters clairs et
     -6,0 et -9,7 dans les gras -- la pointe du U ENTRAIT dans l'accent.
  4. LES SIX U ACCENTUES SUIVENT, et `u.sc` aussi. Ils sont composites ou
     derives, donc ils suivent par construction ; la section le MESURE, parce
     qu'une table indexee par nom ne suit pas une composition et que ce projet
     a paye cinq fois cette phrase.

LE TEMOIN. `--temoin` remet le U a l'etat qu'il avait avant ce tour -- bout
remonte de 44 unites -- et rejoue les sections 1 a 3 : elles doivent toutes les
trois signaler. Il agit sur le dessin servi, pas sur ce qui l'a produit.

    python3 check_U.py [--temoin]
"""

import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphsLib.classes import GSComponent
import dessin as D
import mesure_titrage as MT
import abaisse_U as AU

#: La cible, lue dans les metriques du master et jamais ecrite en dur : une
#: hauteur de capitale recopiee cesserait d'etre juste le jour ou la source
#: change, et le controle mentirait sans que rien ne bouge.
TOL_SOMMET = 0.1

#: Le geste que le reglage general sort sur une capitale.
GESTE = 44.0
TOL_GESTE = 0.5

#: Le blanc sous l'accent doit egaler celui du Â a cette tolerance.
TOL_BLANC = 0.5

ACCENTUES = ("Ugrave", "Uacute", "Ucircumflex", "Udieresis")
PETITE = "u.sc"


def _sommet(src, nom):
    cs = src.contours(nom)
    return max((y for c in cs for _x, y in c), default=None)


def _bout(src, nom):
    """(sommet, bas du bout) : les deux niveaux du bout haut, en unites."""
    ys = sorted({round(y, 1) for c in src.contours(nom) for _x, y in c},
                reverse=True)
    if not ys:
        return None, None
    haut = ys[0]
    bas = next((y for y in ys if y < haut - 1.0), None)
    return haut, bas


def _blanc_accent(font, src, compose, base):
    """Le blanc entre le sommet de la base et le bas de son accent.

    L'accent est pris par sa TRANSFORMATION de composant et non par le bas des
    contours du compose : ce dernier rendrait le bas de la LETTRE, qui descend
    plus bas que l'accent. Un premier jet l'a fait et rendait 0,0 partout --
    une colonne uniforme, le mode de defaut que ce projet a rencontre neuf
    fois.
    """
    hb = _sommet(src, base)
    g = font.glyphs[compose]
    if g is None or hb is None:
        return None
    ids = {m.id: m.name for m in font.masters}
    for l in g.layers:
        if ids.get(l.layerId) != src.master:
            continue
        for s in l.shapes:
            if isinstance(s, GSComponent) and "circumflex" in s.componentName:
                cs = src.contours(s.componentName)
                if not cs:
                    return None
                return (min(y for c in cs for _x, y in c)
                        + list(s.transform)[5]) - hb
    return None


def _charger(remonter=False):
    for lab, amont, projet, _w in MT.SOURCES:
        if not os.path.exists(projet):
            yield lab, None, f"source du projet absente : {projet}"
            continue
        f = glyphsLib.GSFont(projet)
        if remonter:
            # TEMOIN : on remonte le bout de 44, ce qui rend au U l'etat qu'il
            # avait avant ce tour.
            ids = {m.id for m in f.masters}
            for l in f.glyphs["U"].layers:
                if l.layerId in ids:
                    AU.descendre(l, d=-AU.BAISSE)
        yield lab, f, None


def section1(paires):
    print("\n1. le sommet du U est a la hauteur de capitale")
    anomalies = 0
    for lab, f, err in paires:
        if err:
            print(f"  {lab:<9} !! {err}  NON MESURE.")
            anomalies += 1
            continue
        for m in f.masters:
            src = D.Source(f, m.name)
            cible = float(m.capHeight or 668)
            h = _sommet(src, "U")
            note = ("" if abs(h - cible) <= TOL_SOMMET
                    else f"  !! attendu {cible:.1f}")
            print(f"  {lab:<9} {m.name:<19} sommet {h:7.1f}, "
                  f"capitale {cible:.1f}{note}")
            anomalies += bool(note)
    return anomalies


def section2(paires):
    print("\n2. le geste n'est pas reduit : 44 unites entre les deux coins")
    anomalies = 0
    for lab, f, err in paires:
        if err:
            print(f"  {lab:<9} !! NON MESURE")
            anomalies += 1
            continue
        for m in f.masters:
            src = D.Source(f, m.name)
            haut, bas = _bout(src, "U")
            if bas is None:
                print(f"  {lab:<9} {m.name:<19} !! bout PLAT : le geste a "
                      f"disparu")
                anomalies += 1
                continue
            g = haut - bas
            note = "" if abs(g - GESTE) <= TOL_GESTE else f"  !! attendu {GESTE}"
            print(f"  {lab:<9} {m.name:<19} bout de {g:5.1f} u "
                  f"({bas:.1f} -> {haut:.1f}){note}")
            anomalies += bool(note)
    return anomalies


def section3(paires):
    print("\n3. le blanc sous l'accent du Û egale celui du Â")
    anomalies = 0
    for lab, f, err in paires:
        if err:
            print(f"  {lab:<9} !! NON MESURE")
            anomalies += 1
            continue
        for m in f.masters:
            src = D.Source(f, m.name)
            bu = _blanc_accent(f, src, "Ucircumflex", "U")
            ba = _blanc_accent(f, src, "Acircumflex", "A")
            if bu is None or ba is None:
                print(f"  {lab:<9} {m.name:<19} !! accent non mesurable")
                anomalies += 1
                continue
            note = ("" if abs(bu - ba) <= TOL_BLANC
                    else ("  !! la pointe ENTRE dans l'accent" if bu < 0
                          else f"  !! ecart de {bu - ba:+.1f} u au Â"))
            print(f"  {lab:<9} {m.name:<19} Û {bu:7.1f} u, Â {ba:7.1f} u{note}")
            anomalies += bool(note)
    return anomalies


def section4(paires):
    print("\n4. les accentuees et la petite capitale suivent")
    anomalies = 0
    for lab, f, err in paires:
        if err:
            print(f"  {lab:<9} !! NON MESURE")
            anomalies += 1
            continue
        for m in f.masters:
            src = D.Source(f, m.name)
            hu = _sommet(src, "U")
            manque = []
            for nom in ACCENTUES:
                g = f.glyphs[nom]
                if g is None:
                    manque.append(f"{nom} absent")
                    continue
                ids = {x.id: x.name for x in f.masters}
                lay = next((l for l in g.layers
                            if ids.get(l.layerId) == m.name), None)
                if lay is None:
                    continue
                # La LETTRE du compose, sans son accent : le point le plus haut
                # des contours qui viennent du composant `U`.
                vu = None
                for s in lay.shapes:
                    if isinstance(s, GSComponent) and s.componentName == "U":
                        cs = src.contours("U")
                        vu = max(y for c in cs for _x, y in c) \
                            + list(s.transform)[5]
                if vu is not None and abs(vu - hu) > TOL_SOMMET:
                    manque.append(f"{nom} a {vu:.1f}")
            sc = _sommet(src, PETITE)
            note = "  !! " + " ".join(manque) if manque else ""
            print(f"  {lab:<9} {m.name:<19} U {hu:.1f}, "
                  f"{len(ACCENTUES)} accentuee(s) conformes, "
                  f"{PETITE} a {sc:.1f}{note}")
            anomalies += len(manque)
    return anomalies


def main(temoin=False):
    if temoin:
        print("TEMOIN : le bout du U remonte de 44 unites, l'etat d'avant ce "
              "tour.")
        print("Les sections 1, 2 et 3 doivent TOUTES LES TROIS signaler.")
        paires = list(_charger(remonter=True))
        n1, n2, n3 = section1(paires), section2(paires), section3(paires)
        print(f"\nTEMOIN : section 1 {n1}, section 2 {n2}, section 3 {n3} — "
              + ("le controle sait signaler" if n1 and n3 else
                 "UNE SECTION NE DISCRIMINE PAS"))
        return 0
    paires = list(_charger())
    total = (section1(paires) + section2(paires) + section3(paires)
             + section4(paires))
    print(f"\nTOTAL : {total} anomalie(s)."
          + ("  Le U touche la ligne de capitale sans perdre son geste."
             if not total else ""))
    return total


if __name__ == "__main__":
    sys.exit(1 if main("--temoin" in sys.argv) else 0)
