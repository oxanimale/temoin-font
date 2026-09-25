#!/usr/bin/env python3
"""Aucune lettre n'en touche une autre, mesure sur le binaire SERVI.

QUARANTIEME TOUR, ET CE CONTROLE EST NE D'UN DEFAUT REEL. Le titrage compile en
jeu stylistique faisait se toucher le A et le X -- AXE, TAXE, MAX -- dans treize
mot-graisses au romain et quatorze en italique. Il n'a ete trouve ni par un
chiffre ni par un contrôle : en OUVRANT une image du titrage rendu, puis en
comptant les taches d'encre. Aucun des onze contrôles du projet ne regardait le
binaire servi sous cet angle.

Depuis la FUSION, le geste ne vit plus dans un jeu stylistique separe mais dans
le dessin unique : le risque de contact est donc celui du corps de texte, et
`paires_pieds.py` le ferme au plancher de jour. Ce contrôle verifie que la table
fait bien son travail SUR LE BINAIRE, et non dans la source.

LE CRITERE EST LE COMPTAGE DE TACHES D'ENCRE, et il vient du projet :

  - un test par colonne blanche rend un FAUX POSITIF des que deux boites se
    chevauchent sans que l'encre se touche, ce qui est arrive sur `F+t` ;
  - le SIGNE de l'ecart dit lequel de deux defauts s'est produit -- moins de
    taches signale une fusion, donc un contact ; plus de taches signale une
    separation, donc un trait qui se coupe ;
  - la reference est AUTONOME : le compte attendu est la somme des taches des
    lettres rendues SEULES, dans le meme binaire et a la meme graisse. Aucun
    fichier exterieur, donc rien qui puisse manquer ou dater.

    python3 check_contacts.py [TTF romain] [TTF italique]
    TEMOIN_BUILD=/tmp/bN python3 check_contacts.py
    python3 check_contacts.py --temoin     # prouve qu'il sait signaler

Il lit le TTF sous-ensemble, jumeau du WOFF2 servi : HarfBuzz ne decode pas le
WOFF2 et rend du `.notdef` en silence.
"""

import os
import sys

import numpy as np
import freetype
import uharfbuzz as hb
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BUILD = os.environ.get("TEMOIN_BUILD", "/tmp/build-temoin")

#: Les quatre points de l'axe ou les masters tombent. Un contact nait d'abord
#: dans les GRAS, ou la matiere est plus large : un contrôle qui ne testerait
#: que le Regular raterait l'essentiel.
WGHT = (200.0, 400.0, 700.0, 800.0)

#: Corps de rendu. Assez grand pour qu'un jour de 24 unites -- le plancher du
#: projet, `approches.JOUR_MIN` -- fasse une dizaine de pixels et ne se ferme
#: pas par simple arrondi de rasterisation.
CORPS = 400

#: Les mots. Ceux qui portent les paires que le projet surveille, plus des mots
#: francais ordinaires pour que le contrôle ne teste pas QUE ses propres
#: craintes. `AXE`, `TAXE` et `MAX` portent A+X, la premiere paire de cette
#: famille a exister en francais courant ; les paires du q sont geometriques et
#: sans occurrence, donc elles sont ecrites a la main.
MOTS = [
    "AXE", "TAXE", "MAX", "OXA", "LAXE", "AV", "AW", "AY", "VA", "XA",
    "qm", "qM", "qf", "qN", "qH", "qX", "qy", "fV", "fY", "Aj", "Ax", "Ay",
    "Expérimentation", "Autorisation", "Transparence", "Protocole",
    "Observatoire", "Réglementation", "Primates", "Souffrance",
    "Affixe", "Wagon", "Klaxon", "Vwyz", "jamais", "kiwi", "buvard",
]

#: CE QUE CE CONTROLE NE COUVRE PAS, et il faut le lire avant de croire un zero.
NON_COUVERT = ("il teste des mots, pas un inventaire de paires : "
               "l'inventaire complet vit dans `inventaire_pieds` et "
               "`inventaire_bouts`, qui mesurent la SOURCE. Celui-ci mesure le "
               "SERVI, et sur un echantillon.")


def charger(chemin):
    return hb.Font(hb.Face(hb.Blob.from_file_path(chemin)))


class Rendu:
    """Shape avec HarfBuzz, rasterise avec FreeType, compte avec scipy."""

    def __init__(self, chemin):
        self.chemin = chemin
        self.face = freetype.Face(chemin)
        self.upem = hb.Face(hb.Blob.from_file_path(chemin)).upem
        self.font = charger(chemin)

    def taches(self, mot, wght, ecart=0.0):
        """Nombre de composantes connexes d'encre.

        `ecart` ajoute des unites entre chaque paire : il sert au TEMOIN, en
        sens inverse -- un ecart negatif rapproche les lettres jusqu'au contact,
        ce qui prouve que la mesure sait le voir.
        """
        self.font.set_variations({"wght": wght})
        buf = hb.Buffer()
        buf.add_str(mot)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"calt": True})
        self.face.set_var_design_coords([wght])
        self.face.set_char_size(CORPS * 64)
        img = Image.new("L", (CORPS * (len(mot) + 2), CORPS * 3), 0)
        x, y = CORPS, CORPS * 2
        for i, p in zip(buf.glyph_infos, buf.glyph_positions):
            self.face.load_glyph(i.codepoint, freetype.FT_LOAD_RENDER)
            bm = self.face.glyph.bitmap
            if bm.width and bm.rows:
                arr = bytes(bm.buffer)
                g = Image.frombytes("L", (bm.width, bm.rows), b"".join(
                    arr[r * bm.pitch:r * bm.pitch + bm.width]
                    for r in range(bm.rows)))
                bx = (int(x + p.x_offset / self.upem * CORPS
                          + self.face.glyph.bitmap_left),
                      int(y - self.face.glyph.bitmap_top))
                if bx[0] >= 0 and bx[1] >= 0:
                    reg = img.crop((bx[0], bx[1], bx[0] + g.size[0],
                                    bx[1] + g.size[1]))
                    img.paste(Image.fromarray(
                        np.maximum(np.array(reg), np.array(g))), bx)
            x += (p.x_advance + ecart) / self.upem * CORPS
        return ndimage.label(np.array(img) > 40)[1]

    def attendu(self, mot, wght):
        """La somme des taches des lettres RENDUES SEULES.

        Reference autonome : elle vit dans le meme binaire, a la meme graisse et
        au meme corps que la mesure, donc les deux ne different que par le
        voisinage -- ce qui est exactement ce qu'on juge.
        """
        return sum(self.taches(c, wght) for c in mot if c.strip())


def une_source(lab, chemin, temoin=False):
    print(f"=== {lab} : {os.path.basename(chemin)}")
    if not os.path.exists(chemin):
        print(f"    !! binaire absent : {chemin}")
        print("       Ce n'est pas un succes, c'est un NON MESURE.")
        return None
    r = Rendu(chemin)
    # UNE GRAISSE HORS DE L'AXE DU BINAIRE NE SE MESURE PAS, elle se dit. Depuis
    # le soixante-et-onzieme tour, le servi s'arrete a 400 (point ouvert 3), et
    # HarfBuzz ramene 200 a 400 sans rien dire : la ligne "wght 200" aurait
    # mesure le Regular une seconde fois sous une etiquette fausse. Le binaire
    # publie, 200-800, se controle en passant ses TTF en argument.
    from fontTools.ttLib import TTFont
    axe = TTFont(chemin)["fvar"].axes[0]
    graisses = [w for w in WGHT if axe.minValue <= w <= axe.maxValue]
    hors = [w for w in WGHT if w not in graisses]
    if hors:
        print(f"    hors de l'axe du binaire ({axe.minValue:.0f}-"
              f"{axe.maxValue:.0f}), non mesure ici : "
              + ", ".join(f"wght {w:.0f}" for w in hors))
    if not graisses:
        print("    !! aucune graisse de WGHT dans l'axe du binaire : NON MESURE.")
        return None
    contacts, separations, essais = [], [], 0
    for mot in MOTS:
        for w in graisses:
            essais += 1
            att = r.attendu(mot, w)
            # Le temoin RAPPROCHE les lettres de 60 unites : si la mesure sait
            # voir un contact, elle doit en trouver ici. Un contrôle qui passe
            # doit prouver qu'il sait signaler, et un temoin doit agir dans le
            # SENS ou le contrôle cherche le defaut.
            vu = r.taches(mot, w, ecart=-60.0 if temoin else 0.0)
            if vu < att:
                contacts.append(f"{mot} a wght {w:.0f} ({att} -> {vu} taches)")
            elif vu > att:
                separations.append(f"{mot} a wght {w:.0f} ({att} -> {vu})")
    etat = "TEMOIN" if temoin else "servi"
    print(f"    {len(MOTS)} mots x {len(graisses)} graisses = {essais} "
          f"mot-graisses, etat {etat}")
    print(f"    {len(contacts)} contact(s), {len(separations)} separation(s)")
    for x in contacts[:10]:
        print(f"     CONTACT : {x}")
    for x in separations[:6]:
        print(f"     separation : {x}")
    return contacts


def main():
    temoin = "--temoin" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    rom = args[0] if args else BUILD + "/Temoin-sub.ttf"
    ital = args[1] if len(args) > 1 else BUILD + "/Temoin-Italic-sub.ttf"
    total = 0
    for lab, chemin in (("romain", rom), ("italique", ital)):
        res = une_source(lab, chemin, temoin)
        if res is None:
            print("\nPAS MESURE.")
            return 2
        total += len(res)
        print()
    print(f"TOTAL : {total} contact(s).")
    if temoin:
        print("        Le temoin rapproche les lettres de 60 unites : un total "
              "NUL signifierait que ce contrôle ne sait pas signaler.")
        return 0 if total else 1
    print(f"        CE QU'IL NE COUVRE PAS : {NON_COUVERT}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
