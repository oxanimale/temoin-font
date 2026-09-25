#!/usr/bin/env python3
"""Le producteur de `paires_F.py` : le crenage qui referme le trou du F.

**Ce fichier n'existait plus, et son absence est le point ouvert 80.** Le
docstring de `paires_F.py` annonce `inventaire_F_haut.py --ecrire` depuis le
vingt-quatrieme tour ; ce drapeau n'a jamais ete dans ce fichier, le
trente-et-unieme tour l'avait consigne sans en tirer la consequence, et le
quarante-quatrieme a rouvert la question en faisant entrer les dix chiffres dans
`VOISINS_F` -- huit anomalies, une par master, toutes F+chiffre.

**Pourquoi un fichier neuf et pas un drapeau dans `inventaire_F_haut.py`.** Ce
dernier est un GARDE-FOU : sa fonction `parcours` cherche les paires que le
projet a rendues PLUS SERREES qu'Atkinson. La table, elle, referme les paires
que la coupe a OUVERTES. Deux signes opposes. Le premier jet du volet F de
`mesure_point55.py` a rejoue `parcours` en croyant tenir le producteur et a
rendu 0 paire sur une table qui en porte 317 : reproduire un producteur demande
d'abord de verifier qu'on a le bon. Le nom suit donc ses jumeaux,
`inventaire_pieds.py` et `inventaire_bouts.py`, qui produisent les deux autres
tables de paires du projet.

**Ce que la mesure prend, et d'ou.** `approches.paire_bornee` rend le plus petit
de deux nombres : ce que la coupe a ouvert, mesure sur la bande de jugement, et
ce qu'on peut refermer sans passer sous le couloir d'Atkinson, mesure sur la
bande pleine. Rien n'est choisi. Elle demande un Temoin ou RIEN n'est encore
crene, sans quoi elle mesurerait l'etat deja corrige : ce generateur regenere
donc lui-meme les deux sources sous `TEMOIN_SANS_APPROCHES=1`, au lieu de lire
un fichier qu'une session anterieure aurait laisse. Une source d'instruction
posee sur le disque devient fausse le jour ou la chaine avance, et le projet a
paye quatre fois cette forme-la.

**Les valeurs sont TOTALES**, crenage d'Atkinson plus ce qu'il faut refermer :
elles s'ecrivent en exception glyphe-glyphe, qui remplace et ne s'ajoute pas.
Cette table passe la premiere des trois dans `approches.appliquer`, donc sa base
est bien Atkinson et non Temoin -- c'est l'inverse de `paires_bouts.py`, ecrite
apres elle.

**L'arrondi va vers zero**, comme celui des bouts et pour la meme raison : la
contrainte est un plafond, donc arrondir au plus proche referme parfois une
demi-unite de plus que la borne ne permet. C'est le seul ecart entre cette table
regeneree et celle du vingt-quatrieme tour sur les lettres : une unite, dans le
sens plus lache, sur environ 160 paire-masters.

Usage :
    python3 inventaire_F.py              # mesure seule, les deux sources
    python3 inventaire_F.py roman        # un cote de l'axe d'inclinaison
    python3 inventaire_F.py --ecrire     # regenere paires_F.py
    python3 inventaire_F.py --temoin     # prouve que le generateur sait voir
"""

import math
import os
import sys
import tempfile

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import approches as A
import dessin as D
import make_temoin as M
from check_approches import AMONT, MASTERS, VOISINS_F as VOISINS, mid

ICI = os.path.dirname(os.path.abspath(__file__))
SERVI = {
    "roman": os.path.join(ICI, "Temoin.glyphs"),
    "italic": os.path.join(ICI, "Temoin-Italic.glyphs"),
}


def source_sans_approches(cle_src, dossier):
    """Regenere la source du projet en sautant l'etape des approches.

    C'est la chaine reelle, `make_temoin.process`, et non une reconstruction :
    un generateur qui rejoue les etapes lui-meme cesse de decrire le livrable le
    jour ou la chaine en gagne une, et `inventaire_pieds` comme
    `inventaire_bouts` ont chacun paye ce defaut une fois.
    """
    entree = AMONT[cle_src]
    if not os.path.exists(entree):
        return None
    sortie = os.path.join(
        dossier, "Temoin.glyphs" if cle_src == "roman" else "Temoin-Italic.glyphs")
    avant = os.environ.get("TEMOIN_SANS_APPROCHES")
    os.environ["TEMOIN_SANS_APPROCHES"] = "1"
    try:
        M.process(entree, sortie)
    finally:
        if avant is None:
            os.environ.pop("TEMOIN_SANS_APPROCHES", None)
        else:
            os.environ["TEMOIN_SANS_APPROCHES"] = avant
    return sortie


def boite(src, nom):
    """La boite d'encre, contours resolus. Rend None sur un glyphe sans encre."""
    pts = [p for c in src.contours(nom) for p in c]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return (round(min(xs), 1), round(min(ys), 1),
            round(max(xs), 1), round(max(ys), 1))


def temoin_du_dessin(sans, cle_src, verbeux=True):
    """Le RECONSTRUIT compare au SERVI, sur ce que la table regarde.

    La regle du projet pour un generateur qui reconstruit son etat. Ici la
    source est produite par la chaine, donc la seule chose qui doit differer de
    `Temoin.glyphs` est le CRENAGE : les approches ne touchent plus aucune
    chasse depuis le vingt-quatrieme tour, ni aucun contour. Un ecart de contour
    ou de chasse sur le F ou sur un chiffre voudrait dire que la source mesuree
    n'est pas le dessin servi, et toute la table serait posee a cote.

    Rend le nombre d'ecarts ; zero est un fait, pas un silence.
    """
    chemin = SERVI[cle_src]
    if not os.path.exists(chemin):
        print("  temoin NON FAIT : la source servie manque")
        return None
    serv = glyphsLib.GSFont(chemin)
    noms = ["F"] + ["zero", "one", "two", "three", "four", "five", "six",
                    "seven", "eight", "nine"]
    ecarts = []
    for mn in MASTERS[cle_src]:
        ss, sv = D.Source(sans, mn), D.Source(serv, mn)
        for n in noms:
            if sans.glyphs[n] is None or serv.glyphs[n] is None:
                continue
            bs, bv = boite(ss, n), boite(sv, n)
            ws, wv = ss.width(n), sv.width(n)
            if bs is None or bv is None:
                continue
            if max(abs(a - b) for a, b in zip(bs, bv)) > 0.05 or abs(ws - wv) > 0.05:
                ecarts.append((mn, n, bs, bv, ws, wv))
    if verbeux:
        if ecarts:
            print(f"  TEMOIN EN ECHEC : {len(ecarts)} ecart(s) entre le "
                  "reconstruit et le servi")
            for mn, n, bs, bv, ws, wv in ecarts[:6]:
                print(f"    {mn:20s} {n:8s} boite {bs} pour {bv}, "
                      f"chasse {ws:.1f} pour {wv:.1f}")
        else:
            print(f"  temoin : {len(noms)} glyphe(s) x {len(MASTERS[cle_src])} "
                  "master(s) identiques au servi, boite et chasse. Le "
                  "crenage seul differe, et c'est ce que la table ecrit.")
    return len(ecarts)


def parcours(cle_src, sans, verbeux=True):
    """Rend {master: {voisin: valeur totale}} pour un cote de l'axe."""
    amont = glyphsLib.GSFont(AMONT[cle_src])
    par_master = {}
    for mn in MASTERS[cle_src]:
        sa, st = D.Source(amont, mn), D.Source(sans, mn)
        ma, mt = mid(amont, mn), mid(sans, mn)
        table, lignes, refus = {}, [], 0
        for v in VOISINS:
            nom = v if len(v) > 1 else D.nom_glyphe(amont, v)
            if nom is None or sans.glyphs[nom] is None or amont.glyphs[nom] is None:
                continue
            try:
                ka = A.kern(amont, ma, "F", nom)
                brut = A.paire_bornee(sa, st, "F", nom, ka)
            except Exception:
                refus += 1
                continue
            if brut is None:
                continue
            # Arrondi vers zero : ne jamais refermer plus que la borne permet.
            delta = -int(math.floor(abs(brut)))
            table[nom] = int(round(ka)) + delta
            lignes.append((nom, ka, brut, table[nom]))
        lignes.sort(key=lambda t: t[2])
        if verbeux:
            print(f"\n  {mn:22s} {len(table)} paire(s)"
                  + (f", {refus} voisin(s) non mesurable(s)" if refus else ""))
            for nom, ka, brut, val in lignes[:6]:
                print(f"      F+{nom:14s} atkinson {ka:+7.1f}   referme "
                      f"{brut:+7.1f}   totale {val:+6d}")
            if len(lignes) > 6:
                print(f"      … et {len(lignes)-6} autre(s)")
        par_master[mn] = table
    return par_master


def temoin_du_critere(sans, cle_src):
    """Prouve que la mesure lit le DESSIN, en lui rendant le F d'Atkinson.

    **Un premier jet de ce temoin ne pouvait pas marcher**, et c'est la
    cinquieme forme du meme defaut dans ce projet : il reposait `paire_bornee`
    avec la valeur deja ajoutee au crenage, en attendant un refus.
    `paire_bornee` passe le MEME crenage aux deux etats -- l'ouverture est une
    difference, donc elle est invariante par translation, et le temoin rendait
    exactement la meme valeur. Un temoin doit agir sur ce que le controle
    mesure : ici le dessin du F, dont la barre mediane a recule.

    Le temoin remet donc le calque amont du F dans la source mesuree, sur un
    master, et exige que les paires retenues disparaissent.

    **Et il faut vider `approches._CACHE_PROFIL` pour que la modification se
    voie.** La memoisation du profil porte sur `id(src.font)` : elle survit a
    toute modification du dessin dans le meme objet, donc le contour changeait
    bien et la mesure rendait l'ancienne valeur, a la decimale pres. Un cache
    indexe par identite d'objet est un etat qui ne se perime pas tout seul.
    """
    amont = glyphsLib.GSFont(AMONT[cle_src])
    mn = MASTERS[cle_src][1]
    sa = D.Source(amont, mn)
    ma, mt = mid(amont, mn), mid(sans, mn)
    cibles = [c for c in ("four", "A", "o", "e") if sans.glyphs[c] is not None]

    st = D.Source(sans, mn)
    avant = {c: A.paire_bornee(sa, st, "F", c, A.kern(amont, ma, "F", c))
             for c in cibles}

    lay_t = [l for l in sans.glyphs["F"].layers if l.layerId == mt][0]
    lay_a = [l for l in amont.glyphs["F"].layers if l.layerId == ma][0]
    garde, garde_w = list(lay_t.shapes), lay_t.width
    lay_t.shapes = list(lay_a.shapes)
    lay_t.width = lay_a.width
    A._CACHE_PROFIL.clear()
    st2 = D.Source(sans, mn)
    apres = {c: A.paire_bornee(sa, st2, "F", c, A.kern(amont, ma, "F", c))
             for c in cibles}
    lay_t.shapes = garde
    lay_t.width = garde_w
    A._CACHE_PROFIL.clear()

    restants = [c for c in cibles if apres[c] is not None]
    detail = ", ".join(f"F+{c} {avant[c]:+.1f} -> "
                       + ("refusee" if apres[c] is None else f"{apres[c]:+.1f}")
                       for c in cibles)
    if restants:
        print(f"  TEMOIN DU CRITERE EN ECHEC, {mn} : le F rendu a Atkinson "
              f"laisse {len(restants)} paire(s) dans la table. {detail}")
    else:
        print(f"  temoin du critere, {mn} : le F rendu a Atkinson fait sortir "
              f"les {len(cibles)} paires temoins. {detail}")
    return not restants


ENTETE = '''"""Le crenage du F, paire par paire et master par master. GENERE, ne pas editer a la main.

Produit par `inventaire_F.py --ecrire`, qui regenere lui-meme les deux sources
sous `TEMOIN_SANS_APPROCHES=1`. **Le producteur annonce ici jusqu'au
quarante-cinquieme tour, `inventaire_F_haut.py --ecrire`, n'a jamais existe** :
ce fichier-la est le GARDE-FOU, qui cherche les paires rendues plus serrees
qu'Atkinson, quand cette table referme les paires ouvertes. Deux signes opposes,
point ouvert 80.

**Pourquoi cette table remplace l'approche du glyphe.** Le vingt-troisieme tour
avait retenu une approche de -100 sur la chasse du F, validee par un garde-fou
qui mesurait le couloir de la ligne de base a la hauteur d'x. La barre haute du F
monte a 668 et le point du i a 714 : tout ce qui se passe au-dessus de 496 etait
invisible. Mesure du vingt-quatrieme tour : l'approche laissait 8 unites entre la
barre du F et le point du i, contre 106 dans Atkinson, et **six paires de
capitales se touchaient reellement dans le binaire servi**, FI FT FV FW FX FY,
verifie par rasterisation.

**Comment chaque valeur est obtenue.** `approches.paire_bornee` prend le plus
petit de deux nombres : ce que la coupe a ouvert, mesure sur la bande de
jugement, et ce qu'on peut refermer sans passer sous le couloir d'Atkinson,
mesure sur la bande pleine. Devant une lettre qui monte, le second vaut zero et
la paire n'entre pas dans la table. Rien n'est choisi.

**Les valeurs sont TOTALES et non des ajustements.** Elles valent le crenage
d'Atkinson plus ce qu'il faut refermer, parce qu'elles s'ecrivent en exception
glyphe-glyphe, qui remplace et ne s'ajoute pas. Cette table passe la premiere des
trois dans `approches.appliquer`, donc sa base est bien Atkinson -- c'est
l'inverse de `paires_bouts.py`, qui part du crenage de Temoin.

**Elles sont ecrites en exception glyphe-glyphe et non par groupe.** Un trema
monte et limite ce qu'on peut refermer : sur la cle de groupe, `odieresis`
ramenerait F+o de -124 a -90 et `ydieresis` ramenerait F+v de -100 a -32.

**L'arrondi va vers zero**, comme celui des bouts : la contrainte est un plafond,
et arrondir au plus proche referme parfois une demi-unite de plus que la borne ne
permet. C'est le seul ecart avec la table du vingt-quatrieme tour sur les
lettres, une unite dans le sens plus lache.

**Ce que la regeneration du quarante-cinquieme tour change.** {n_ch} paires
F+chiffre entrent, les dix chiffres etant entres dans `VOISINS_F` au tour
precedent : c'est le point ouvert 80, jusqu'a -168 sur `F+four` en Bold Italic.
Et **`F+t` sort de la table dans les quatre masters clairs** : sa borne vaut
aujourd'hui -3,6 en ExtraLight et +3,1 au Regular, donc il n'y a plus rien a
refermer. Les -43 et -23 qu'elle portait ont ete mesures quand le t culminait a
620 ; `coupe.allonge` l'a monte a 690 au trente-deuxieme tour et le couloir s'est
resserre tout seul. L'entree etait donc plus serree que la borne depuis douze
tours, et aucun controle ne pouvait le dire : la section 2 de `check_approches`
cherche les paires laissees OUVERTES.

Ecrite en clair et non calculee a l'execution : le bac a sable ne peut pas
toujours cloner la source amont, et un controle qui n'a pas pu lire sa source ne
doit rien conclure.
"""

PAIRES_F = {{
'''

CHIFFRES = ("zero", "one", "two", "three", "four", "five", "six", "seven",
            "eight", "nine")


def ecrire(tables):
    fusion = {}
    for t in tables:
        if t:
            fusion.update(t)
    n_ch = sum(1 for t in fusion.values() for k in t if k in CHIFFRES)
    chemin = os.path.join(ICI, "paires_F.py")
    with open(chemin, "w") as f:
        f.write(ENTETE.format(n_ch=n_ch))
        n = 0
        for mn, paires in fusion.items():
            f.write(f'    "{mn}": {{\n')
            ligne = "       "
            for nom in sorted(paires):
                bout = f' "{nom}": {paires[nom]},'
                if len(ligne) + len(bout) > 92:
                    f.write(ligne + "\n")
                    ligne = "       "
                ligne += bout
                n += 1
            if ligne.strip():
                f.write(ligne + "\n")
            f.write("    },\n")
        f.write("}\n")
    print(f"\n{chemin} : {n} paire(s) sur {len(fusion)} master(s), "
          f"dont {n_ch} F+chiffre")
    return chemin


if __name__ == "__main__":
    ecr = "--ecrire" in sys.argv
    tem = "--temoin" in sys.argv
    cles = [a for a in sys.argv[1:] if not a.startswith("--")] or \
        ["roman", "italic"]
    print("=" * 78)
    print("=== le voisinage du F, et ce que la borne permet de refermer")
    print(f"=== voisins : {len(VOISINS)}   valeurs : approches.paire_bornee")
    print("=" * 78)
    tables, manque = [], False
    with tempfile.TemporaryDirectory() as dossier:
        for c in cles:
            print(f"\n=== {c}")
            chemin = source_sans_approches(c, dossier)
            if chemin is None:
                print(f"  source amont absente ({AMONT[c]}) : rien de mesure. "
                      "Ce n'est pas un succes, c'est un inventaire NON FAIT.")
                manque = True
                continue
            sans = glyphsLib.GSFont(chemin)
            if temoin_du_dessin(sans, c):
                manque = True
            tables.append(parcours(c, sans))
            if tem:
                temoin_du_critere(sans, c)
        if ecr:
            if manque or len(tables) != len(cles):
                print("\nRIEN ECRIT : un cote n'a pas pu etre mesure, ou le "
                      "temoin du dessin a echoue. Une table partielle serait "
                      "pire qu'aucune.")
            else:
                ecrire(tables)
        else:
            tot = sum(len(v) for t in tables for v in t.values())
            print(f"\n{tot} paire(s) au total (mesure seule ; --ecrire pour "
                  "regenerer paires_F.py)")
