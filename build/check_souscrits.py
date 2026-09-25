#!/usr/bin/env python3
"""
Controle de contact des dix-sept crochets souscrits, sur la table ecrite.

Le dix-septieme tour avait mesure les contacts en reposant les etats a la main,
sur le romain seul. Celui-ci les mesure sur ce que `lot2.appliquer_lot` produit,
et sur les deux sources : c'est le chemin de code qui sera compile.

Ce qu'il compte, et pourquoi ce n'est pas la topologie. Une pointe qui reste
dans sa chasse peut toucher sa voisine, parce que la chasse comprend deux
approches dans lesquelles la voisine avance. La boite, la chasse et la topologie
se mesurent sur un glyphe isole et ne peuvent donc rien en dire. On compte donc
les taches d'encre d'un mot compose, a trois resolutions, et on les compare au
meme mot dans une police ou le lot 2 est applique sans les dix-sept.

Le signe de l'ecart compte, et les confondre ferait un controle menteur :
moins de taches signale une fusion, donc un contact avec la voisine ; plus de
taches signale une separation, donc un crochet qui se coupe.

La reference n'est pas la source brute. C'est le meme piege que dans check4 :
ĻļȘșȚț portent le L, le l, le S et le T, que le lot 2 traite depuis longtemps,
et comparer a la source brute melangerait la coupe de la lettre au crochet.

Il passe a zero sur la table ecrite, et un controle qui passe doit prouver
qu'il sait signaler. D'ou `--temoin` : il rejoue le tout avec la virgule
souscrite a l'etat V1, tirage 3,5, connu pour pincer le crochet et le couper en
deux dans les gras. Il rend alors 26 mot-masters en separation sur les deux
sources, jusqu'a six taches de plus. Le zero de la table est donc un vrai zero.
"""

import sys
import os

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lot2 as L
import dessin as D
import souscrits as S

SRC = "/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs"
SRC_IT = "/tmp/ahn/sources/AtkinsonHyperlegibleNext-Italic.glyphs"

RES = [150, 300, 600]

MOTS = [
    ("cedille", ["FRANÇAIS", "leçon reçue", "Ç Ş ş Ţ ţ ç", "ŢŞ Çi ţa"]),
    ("ogonek",  ["zwierzęta", "ZWIERZĘTA", "Ąą", "ĘęĮįŲų", "ąb ęd įn ųm",
                 "Ąt ęt Įl"]),
    ("virgule", ["ȘTIINȚĂ", "ȘȚĢĶĻŅ", "șțļņ", "ș, ț.", "Ķķ Ļļ Ņņ"]),
]


def deux_polices(src):
    """(sans les dix-sept, avec), le lot 2 applique dans les deux cas."""
    plein = list(L.LOT2)
    sans_t = [e for e in plein if e[0] not in set(S.TOUS)]
    out = []
    for entrees in (sans_t, plein):
        with open(src, encoding="utf-8") as fh:
            f = glyphsLib.load(fh)
        L.LOT2[:] = entrees
        try:
            L.appliquer_lot(f, 20.0)
        finally:
            L.LOT2[:] = plein
        out.append(f)
    return out


def main():
    # UNE SOURCE ABSENTE EST UN NON MESURE, code 2, jamais un signalement.
    # Jusqu'au soixante-septieme tour, l'ouverture levait une trace Python et
    # le script sortait a 1. Vaut aussi en mode temoin : un temoin qui n'a
    # rien lu ne prouve rien. Point ouvert 31.
    absentes = [p for p in (SRC, SRC_IT) if not os.path.exists(p)]
    if absentes:
        for p in absentes:
            print(f"NON MESURE : source absente, {p}")
        return 2
    if "--temoin" in sys.argv:
        print("MODE TEMOIN : la virgule souscrite est repassee a l'etat V1, "
              "tirage 3,5. Le controle doit signaler.\n")
        L.LOT2[:] = [(n, l, s, r,
                      (L.POINTE_VIRGULE if n == "commaaccentcomb" else a))
                     for (n, l, s, r, a) in L.LOT2]
    total = 0
    for src, lab in ((SRC, "romain"), (SRC_IT, "italique")):
        sans, avec = deux_polices(src)
        masters = [m.name for m in sans.masters]
        print(f"=== {lab} : taches d'encre par mot, a "
              f"{', '.join(str(r) for r in RES)} pixels de cadratin")
        for famille, mots in MOTS:
            for mot in mots:
                lignes = []
                for m in masters:
                    a = D.Source(sans, m)
                    b = D.Source(avec, m)
                    ref = [S.taches_mot(a, mot, r)[0] for r in RES]
                    cnt = [S.taches_mot(b, mot, r)[0] for r in RES]
                    ecarts = [c - r for c, r in zip(cnt, ref)]
                    if any(e != 0 for e in ecarts):
                        total += 1
                        quoi = ("FUSION, contact avec la voisine"
                                if any(e < 0 for e in ecarts)
                                else "SEPARATION, le crochet se coupe")
                        lignes.append(f"      {m:18s} {ref} -> {cnt}   {quoi}")
                if lignes:
                    print(f"   {famille:8s} {mot!r}")
                    for lg in lignes:
                        print(lg)
        print(f"--- {lab} : parcouru")
    print()
    print(f"TOTAL : {total} mot-master(s) ou le compte de taches change."
          + ("" if total else "  Aucun contact, aucune separation."))
    if "--temoin" in sys.argv:
        print("Le temoin doit rendre un total non nul : "
              + ("le controle sait signaler." if total else
                 "ANOMALIE, le controle ne mesure rien."))
        return 0 if total else 1
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
