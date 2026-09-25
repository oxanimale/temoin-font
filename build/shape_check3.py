#!/usr/bin/env python3
"""Preuve du shaping du lot 3 : les petites capitales partent-elles vraiment ?

A lancer sur le TTF sous-ensemble, jamais sur le WOFF2 : HarfBuzz ne decode pas
le WOFF2 et renvoie du .notdef en silence, ce qui donne l'illusion que tout va
bien. C'est le piege du lot 1, il n'a pas change, et la garde le refuse
desormais au lieu de compter sur la memoire du lecteur.

CE SCRIPT AFFICHE, IL NE JUGE PAS. Comme `shape_check.py`, il rend des
tableaux que l'oeil lit et n'ecrit nulle part ce qui serait conforme : il ne
peut donc pas rendre 1 pour signaler.

Deux codes seulement, depuis le soixante-sixieme tour : 0 les tableaux sont
affiches, 2 NON MESURE. Avant, le chemin etait en dur sur `/tmp/b7`, un bac a
sable d'une session ancienne efface depuis, et son absence levait une
`HarfBuzzError` qui sortait a 1. Point ouvert 111.

    TEMOIN_BUILD=/tmp/bN python3 shape_check3.py
    python3 shape_check3.py /chemin/vers/un.ttf
"""

import os
import sys

import uharfbuzz as hb

BUILD = os.environ.get("TEMOIN_BUILD", "/tmp/build-temoin")

NON_MESURE = 2

FONT = None
face = None
font = None


def charger(args):
    """Ouvre la police a shaper, ou dit ce qui manque et rend None.

    `Temoin-sub.ttf` d'abord : c'est le JUMEAU TTF du WOFF2 servi, celui que
    `subset.py` ecrit a cote de lui, donc celui qui porte ce que le site rend.
    Le binaire de compilation ne vient qu'apres.
    """
    global FONT, face, font
    if args:
        chemin = args[0]
        if not os.path.exists(chemin):
            print(f"!! {chemin} : absent")
            print("   NON MESURE. Aucun tableau n'a ete affiche.")
            return None
    else:
        candidats = [os.path.join(BUILD, n) for n in
                     ("Temoin-sub.ttf", "Temoin[wght].ttf", "Temoin-wght.ttf")]
        trouves = [c for c in candidats if os.path.exists(c)]
        if not trouves:
            print(f"!! aucune police dans {BUILD}")
            for c in candidats:
                print(f"   cherche : {os.path.basename(c)}")
            print("   Compiler, finaliser et sous-ensembler, ou passer un "
                  "chemin en argument.")
            print("   NON MESURE. Aucun tableau n'a ete affiche.")
            return None
        chemin = trouves[0]
    if chemin.lower().endswith(".woff2"):
        print(f"!! {chemin} : HarfBuzz ne decode pas le WOFF2 et rendrait du "
              f".notdef en silence.")
        print("   NON MESURE. Passer le TTF sous-ensemble, pas le WOFF2.")
        return None
    FONT = chemin
    face = hb.Face(hb.Blob.from_file_path(chemin))
    font = hb.Font(face)
    print(f"police : {chemin}")
    return chemin

REGLES = {
    "sans feature": {},
    "smcp seul": {"smcp": True},
    "smcp + c2sc": {"smcp": True, "c2sc": True},
}

CAS = [
    ("sigle du gabarit", "RNT"),
    ("sigle du gabarit", "NTS"),
    ("sigle du gabarit", "OFL"),
    ("sigle du gabarit", "ENS"),
    ("reserve d'etape 1", "OXA"),
    ("sigle long", "INSERM"),
    ("sigle long", "ALURES"),
    ("sigle accentue", "ÉCOLE"),
    ("mixte lettres/chiffres", "NTS-FR-504649v1"),
    ("minuscules", "sigle"),
    ("phrase mixte", "Les RNT de l'ENS"),
    ("cedille", "FRANÇAIS"),
    ("ligature", "ŒUVRE"),
]


def rendu(texte, feats):
    buf = hb.Buffer()
    buf.add_str(texte)
    buf.guess_segment_properties()
    hb.shape(font, buf, dict(feats))
    noms = [font.get_glyph_name(i.codepoint) for i in buf.glyph_infos]
    # Notation compacte : une petite capitale s'ecrit en minuscule, une
    # capitale pleine en capitale, tout le reste tel quel.
    out = []
    for n in noms:
        if n.endswith(".sc"):
            out.append(n[:-3] if len(n[:-3]) == 1 else "[" + n[:-3] + "]")
        elif n in ("space", "hyphen", "quoteright"):
            out.append({"space": " ", "hyphen": "-", "quoteright": "'"}[n])
        elif len(n) == 1:
            out.append(n)
        elif n.startswith("zero"):
            out.append("0")
        else:
            out.append({"one": "1", "two": "2", "three": "3", "four": "4",
                        "five": "5", "six": "6", "seven": "7", "eight": "8",
                        "nine": "9"}.get(n, "<" + n + ">"))
    return "".join(out)


def main():
    if charger(sys.argv[1:]) is None:
        return NON_MESURE
    entete = f"{'cas':<24}{'texte':<20}" + "".join(f"{r:<22}" for r in REGLES)
    print(entete)
    print("-" * len(entete))
    for nom, texte in CAS:
        ligne = f"{nom:<24}{texte:<20}"
        for r, feats in REGLES.items():
            ligne += f"{rendu(texte, feats):<22}"
        print(ligne)
    print("\nlecture : MAJUSCULE = capitale pleine, minuscule = petite "
          "capitale, [nom] = glyphe compose")

    # --- chasses : l'approche de 14 u de chaque cote est-elle bien la ?
    from fontTools.ttLib import TTFont
    ordre = TTFont(FONT).getGlyphOrder()
    idx = {n: i for i, n in enumerate(ordre)}
    print(f"\nchasses au master par defaut (upem {face.upem}) :")
    print(f"  {'capitale':<10}{'chasse':>8}{'x 0,859':>10}   "
          f"{'petite cap.':<12}{'chasse':>8}{'ecart':>8}")
    for a, b in (("R", "r.sc"), ("N", "n.sc"), ("T", "t.sc"), ("O", "o.sc"),
                 ("M", "m.sc"), ("I", "i.sc")):
        wa = font.get_glyph_h_advance(font.get_nominal_glyph(ord(a)))
        wb = font.get_glyph_h_advance(idx[b])
        att = wa * 574 / 668
        print(f"  {a:<10}{wa:>8}{att:>10.1f}   {b:<12}{wb:>8}{wb - att:>8.1f}")
    print("  28 u viennent de l'approche ; le reste, de ce que la source est\n"
          "  prise plus haut sur l'axe, donc un peu plus large.")

    # --- le lot 1 n'a pas bouge
    print("\nlot 1 rejoue (le zero doit rester contextuel) :")
    for texte in ("03/08/2026", "0 %", "NTS-FR-504649v1"):
        buf = hb.Buffer()
        buf.add_str(texte)
        buf.guess_segment_properties()
        hb.shape(font, buf, {"calt": True})
        noms = [font.get_glyph_name(i.codepoint) for i in buf.glyph_infos]
        nus = sum(1 for n in noms if "slashless" in n)
        barres = sum(1 for n in noms if n in ("zero", "zero.tf"))
        print(f"  {texte:<20} {nus} zero(s) net(s), {barres} barre(s)")

    print("\nCes tableaux s'affichent, ils ne se jugent pas tout seuls : le "
          "code 0 dit qu'ils ont ete produits, pas qu'ils sont conformes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
