#!/usr/bin/env python3
"""Preuve de la substitution : on shape reellement avec HarfBuzz et on lit
   les noms de glyphes obtenus, feature par feature.

CE SCRIPT AFFICHE, IL NE JUGE PAS. Il rend un tableau que l'oeil lit : pour
chaque cas de texte et chaque jeu de features, quel zero sort barre et quel
zero sort net. Aucune ligne n'ecrit ce qui serait conforme, donc il ne peut
pas rendre 1 pour signaler -- il n'a pas d'opinion. Le distinguer d'un
controle est le sujet du sixieme piege du projet : une etiquette est une
mesure.

Deux codes seulement, depuis le soixante-sixieme tour : 0 le tableau est
affiche, 2 NON MESURE. Avant, le chemin de la police etait en dur sur un bac
a sable efface depuis, et son absence levait une `HarfBuzzError` qui sortait
a 1 : un signalement sur zero mesure, ce qui se lit comme un defaut du
dessin. Point ouvert 111.

    TEMOIN_BUILD=/tmp/bN python3 shape_check.py
    python3 shape_check.py /chemin/vers/un.ttf

JAMAIS sur un WOFF2 : HarfBuzz ne le decode pas et rend du `.notdef` en
silence, ce qui donne l'illusion que tout va bien. La garde le refuse.
"""

import os
import sys

import uharfbuzz as hb

BUILD = os.environ.get("TEMOIN_BUILD", "/tmp/build-temoin")

NON_MESURE = 2

font = None

REGLES = {
    "police de base": {"calt": False},
    "Temoin (calt)": {"calt": True},
    "cellule chiffree": {"calt": True, "ss01": True},
}

CAS = [
    ("date RNT", "03/08/2026"),
    ("date courte", "31/07/2026"),
    ("reference NTS", "NTS-FR-504649v1"),
    ("reference NTS bis", "NTS-FR-502314v1"),
    ("reference a zero initial", "NTS-FR-012345v1"),
    ("effectif", "13 209"),
    ("effectif court", "1 440"),
    ("annee seule", "2021"),
    ("zero isole", "0 animaux"),
    ("decimale", "0,5 mg/kg"),
    ("pourcentage", "100 %"),
    ("pourcentage zero", "0 %"),
    ("zero colle a une lettre", "O0Oo0"),
    ("code mixte", "A0B0"),
    ("nombre rond", "10 000"),
    ("severite", "0 / 12 / 305"),
]


def rendu(texte, feats, tnum=False):
    buf = hb.Buffer()
    buf.add_str(texte)
    buf.guess_segment_properties()
    f = dict(feats)
    f["tnum"] = tnum
    hb.shape(font, buf, f)
    noms = [font.get_glyph_name(i.codepoint) for i in buf.glyph_infos]
    out = []
    for n, ch in zip(noms, texte):
        if n == "zero.slashless" or n == "zero.tf.slashless":
            out.append("0")           # non barre
        elif n == "zero" or n == "zero.tf":
            out.append("Ø")      # barre
        else:
            out.append(ch)
    return "".join(out)


def charger(args):
    """Ouvre la police a shaper, ou dit ce qui manque et rend None.

    L'ordre des candidats n'est pas indifferent : `Temoin-sub.ttf` est le
    JUMEAU TTF du WOFF2 servi, celui que `subset.py` ecrit a cote de lui, donc
    c'est lui qui porte ce que le site rend vraiment. Le binaire de
    compilation ne vient qu'apres, et il porte des glyphes que le
    sous-ensemblage retire.
    """
    global font
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
    blob = hb.Blob.from_file_path(chemin)
    font = hb.Font(hb.Face(blob))
    print(f"police : {chemin}")
    return chemin


def main():
    if charger(sys.argv[1:]) is None:
        return NON_MESURE
    for tnum in (False, True):
        print(f"\n===== chiffres {'tabulaires (tnum)' if tnum else 'proportionnels'} =====")
        entete = f"{'cas':<26}{'texte':<18}" + "".join(f"{r:<20}" for r in REGLES)
        print(entete)
        print("-" * len(entete))
        for nom, texte in CAS:
            ligne = f"{nom:<26}{texte:<18}"
            for r, feats in REGLES.items():
                ligne += f"{rendu(texte, feats, tnum):<20}"
            print(ligne)
    print("\nlecture : 0 = zero non barre, Ø = zero barre")
    print("Ce tableau s'affiche, il ne se juge pas tout seul : le code 0 dit "
          "qu'il a ete produit, pas qu'il est conforme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
