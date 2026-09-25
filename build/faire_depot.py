#!/usr/bin/env python3
"""Assemble le depot public de Temoin depuis le dossier de travail.

Le dossier de travail reste la seule source. Ce script en extrait le
sous-ensemble publiable et le recopie dans un dossier de depot, sans
jamais ecrire dans la source.

    python3 faire_depot.py                 # mesure, n ecrit rien
    python3 faire_depot.py --ecrire        # assemble

Le tri de build/ n est pas un jugement de gout : il est la FERMETURE
TRANSITIVE des imports a partir de trois familles de racines, calculee
au soixante-sixieme tour et figee ici.

    la chaine       make_temoin, finaliser, subset
    les controles   tout check*.py et shape_check*.py, sauf les deux qui
                    lisent le banc d essai
    les producteurs des six tables generees

62 modules, plus ce script, sur 193 fichiers .py au soixante-et-onzieme
tour (63 sur 190 au soixante-sixieme). Les 130 ecartes sont des
balayages, des generateurs de planches et des essais, qu aucun module
retenu n importe. Le script
le REVERIFIE a chaque passage, section 2 : un module retenu qui
importerait un module ecarte serait signale.

Les fontes vont dans `fonts/`, a la racine du depot, depuis le
soixante-et-onzieme tour (point ouvert 116). Le dossier de travail les
garde dans `gabarits/fonts/`, que le banc d essai lit en relatif ; les
modules de la chaine prennent le premier des deux qui existe, par
`subset.dossier_fontes`. Au soixante-sixieme tour, le renommage avait ete
reporte au tour ou la chaine serait touchee pour une autre raison : c est
ce tour-ci, qui reduit l axe du servi (point 3) et ajoute les TTF (point
115).

Les deux TTF variables, 200-800 et repertoire complet, sont publies a
cote des WOFF2 servis, 400-800 et sous-ensembles au latin francais.
`subset.py` les copie a cote du servi, dans la meme etape.

Trois codes de retour, convention du projet :
    0   conforme
    1   signale
    2   non mesure
"""

import hashlib
import os
import re
import shutil
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
PROJET = os.path.dirname(ICI)
DEPOT = os.path.join(PROJET, "depot-temoin-font")

# ------------------------------------------------------------------
# Ce que le depot porte
# ------------------------------------------------------------------

# Les 62 modules de build/, fermeture transitive des imports.
MODULES = """
abaisse_U approches balayage_lot4 balayage_lot4b barre_F barre_mediane
bras_O check3 check4 check5 check_O check_U check_approches
check_barre_F check_circonflexe check_contacts check_crees check_crenage_sc
check_descente_j check_final check_operateurs check_paires_contacts
check_perimetre check_souscrits check_termes coupe
crenage_sc descente_j dessin finaliser inventaire_F inventaire_ae
inventaire_bouts inventaire_contacts inventaire_pieds inventaire_xa
lot2 lot3 lot4 make_temoin mesure_O mesure_bouts mesure_haut_titrage
mesure_point18 mesure_point66 mesure_sortante_lot mesure_titrage
operateurs paires_F paires_bouts paires_contacts paires_pieds
pointe_sommet reglage_ae reglage_xa
shape_check shape_check3 shape_check_kern souscrits subset termes
zero_reconstruct
""".split()

# Ce script lui-meme, pour que le depot sache se refaire.
AUTRES_BUILD = [
    "faire_depot.py",
    "Temoin.glyphs",
    "Temoin-Italic.glyphs",
    "config-temoin.yaml",
    "subset_unicodes.txt",
]

# source dans le dossier de travail  ->  place dans le depot
FICHIERS = [("OFL.txt", "OFL.txt")]
FICHIERS += [("build/" + m + ".py", "build/" + m + ".py") for m in MODULES]
FICHIERS += [("build/" + f, "build/" + f) for f in AUTRES_BUILD]
FICHIERS += [
    ("gabarits/fonts/Temoin.woff2", "fonts/Temoin.woff2"),
    ("gabarits/fonts/Temoin-Italic.woff2", "fonts/Temoin-Italic.woff2"),
    ("gabarits/fonts/Temoin[wght].ttf", "fonts/Temoin[wght].ttf"),
    ("gabarits/fonts/Temoin-Italic[wght].ttf", "fonts/Temoin-Italic[wght].ttf"),
    ("gabarits/fonts/OFL.txt", "fonts/OFL.txt"),
]

# Ecrits a la main pour le depot, jamais recopies depuis le dossier de
# travail. Le script verifie seulement qu ils sont la.
PROPRES_AU_DEPOT = ["README.md", "FONTLOG.txt", ".gitignore"]

# Dossiers que le script refait entierement a chaque passage. `gabarits`
# reste dans la liste apres le renommage du soixante-et-onzieme tour : le
# depot d avant portait `gabarits/fonts/`, et ce qui y traine doit etre
# signale en section 6, jamais publie en silence.
GERES = ["build", "fonts", "gabarits"]

# Ecartes volontairement, avec la raison, pour que personne ne les
# rajoute par inadvertance.
ECARTES = {
    "build/check2.py": "RETIRE au soixante-septieme tour, point ouvert 31."
    " Il etait mort en deux endroits et rendait 0 en affichant ECHEC ; ce"
    " qu il verifiait, check3 le verifie. Il ne reste qu un renvoi qui rend"
    " 2, sans rien a publier. Code d origine dans temoin/archive/.",
    "build/planche_lot2.py": "RETIRE au soixante-et-onzieme tour, point"
    " ouvert 12. Planche morte, qui ne partait au depot que parce que"
    " check4 lui empruntait le chemin d Atkinson ; check4 porte sa propre"
    " constante SRC depuis le soixante-neuvieme tour.",
    "build/check_page.py": "il lit une page HTML du banc d essai, plus"
    " Atkinson.woff2 comme reference. Outil de chantier.",
    "build/check_point_fixe.py": "il lit gabarits/temoin.css et un releve"
    " qui PERIME des qu une source change. Outil de chantier.",
    "build/point_fixe.json": "le releve du controle ci-dessus. Publie, il"
    " signalerait une derive qui n existe pas.",
    "build/modifies.json": "inventaire des glyphes modifies, lu par"
    " check_page seul.",
    "gabarits/*.html, gabarits/panneau.js": "banc d essai et pages d etats,"
    " documents de travail internes.",
    "gabarits/temoin.css": "systeme typographique du banc d essai, avec ses"
    " variables de panneau et son cache-buster. Le README du depot donne a la"
    " place le bloc @font-face minimal. subset.py sait s en passer.",
    "gabarits/fonts/Temoin-*.woff2 (etats)": "etats de comparaison d anciens"
    " tours, sans valeur hors du chantier.",
    "gabarits/fonts/Atkinson*.woff2": "la police de base, qui se prend chez"
    " ses auteurs et non ici.",
}


def md5(chemin):
    h = hashlib.md5()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(65536), b""):
            h.update(bloc)
    return h.hexdigest()


def section_1_presence():
    """Chaque fichier annonce existe-t-il dans le dossier de travail ?"""
    manquants = []
    total = 0
    for src, _ in FICHIERS:
        p = os.path.join(PROJET, src)
        if not os.path.exists(p):
            manquants.append(src)
        else:
            total += os.path.getsize(p)
    print("1. PRESENCE DANS LA SOURCE")
    print("   %d fichiers annonces, %.1f Mo" % (len(FICHIERS), total / 1e6))
    if manquants:
        print("   MANQUANTS : " + ", ".join(manquants))
        return 1
    print("   aucun manquant")
    return 0


def section_2_autosuffisance():
    """Un module retenu importe-t-il un module ecarte ?

    C est le controle qui mord. Le tri a ete calcule une fois ; si un
    module retenu gagne un import vers un module ecarte, le depot
    publiera une chaine qui ne tourne pas.
    """
    print("2. AUTOSUFFISANCE DES IMPORTS")
    tous = {f[:-3] for f in os.listdir(ICI) if f.endswith(".py")}
    retenus = set(MODULES) | {"faire_depot"}
    fautes = []
    for m in sorted(retenus):
        p = os.path.join(ICI, m + ".py")
        if not os.path.exists(p):
            continue
        src = open(p, encoding="utf-8", errors="replace").read()
        vises = set(re.findall(r"^\s*(?:from|import)\s+([A-Za-z_]\w*)", src, re.M))
        vises |= set(re.findall(r"import_module\([\"'](\w+)", src))
        for d in sorted(vises & tous):
            if d != m and d not in retenus:
                fautes.append("%s importe %s, qui est ecarte" % (m, d))
    if fautes:
        for f in fautes:
            print("   " + f)
        return 1
    print("   %d modules retenus, aucun import vers un module ecarte" % len(retenus))
    return 0


def section_3_documents():
    """Les documents propres au depot sont-ils la ?"""
    print("3. DOCUMENTS PROPRES AU DEPOT")
    if not os.path.isdir(DEPOT):
        print("   le depot n existe pas encore, rien a verifier")
        return 0
    manquants = [f for f in PROPRES_AU_DEPOT if not os.path.exists(os.path.join(DEPOT, f))]
    if manquants:
        print("   MANQUANTS, a ecrire a la main : " + ", ".join(manquants))
        return 1
    print("   " + ", ".join(PROPRES_AU_DEPOT) + " : presents, non touches")
    return 0


def assembler():
    """Copie les fichiers retenus par-dessus le depot.

    Le script NE SUPPRIME RIEN. La section 6 signale ce qu il trouve en
    trop dans les dossiers geres, et laisse la suppression a une main
    humaine : un script qui efface dans un depot est un script qui peut
    effacer ce qu on vient d y ajouter.
    """
    os.makedirs(DEPOT, exist_ok=True)
    for src, dst in FICHIERS:
        p_src = os.path.join(PROJET, src)
        p_dst = os.path.join(DEPOT, dst)
        os.makedirs(os.path.dirname(p_dst), exist_ok=True)
        shutil.copy2(p_src, p_dst)


def section_4_copie():
    """Chaque fichier copie a-t-il le md5 de son original ?"""
    print("4. FIDELITE DE LA COPIE")
    ecarts = []
    for src, dst in FICHIERS:
        p_src = os.path.join(PROJET, src)
        p_dst = os.path.join(DEPOT, dst)
        if not os.path.exists(p_dst):
            ecarts.append(dst + " : absent du depot")
        elif md5(p_src) != md5(p_dst):
            ecarts.append(dst + " : md5 different de la source")
    if ecarts:
        for e in ecarts:
            print("   " + e)
        return 1
    print("   %d fichiers, md5 identique a la source" % len(FICHIERS))
    return 0


def section_5_source_intacte(avant):
    """Le dossier de travail a-t-il bouge ?

    Le script ne doit rien y ecrire. Le releve est pris avant et apres.
    """
    print("5. SOURCE INTACTE")
    apres = releve_source()
    bouges = [k for k in avant if avant[k] != apres.get(k)]
    neufs = [k for k in apres if k not in avant]
    if bouges or neufs:
        for b in bouges:
            print("   MODIFIE : " + b)
        for n in neufs:
            print("   AJOUTE : " + n)
        return 1
    print("   %d fichiers de la source, aucun modifie, aucun ajoute" % len(avant))
    return 0


def section_6_intrus():
    """Le depot porte-t-il des fichiers que ce script n annonce pas ?

    Le script ne supprime rien : il signale. Un fichier reste dans le
    depot longtemps apres que la liste l a lache, et il se publierait
    sans que personne le voie.
    """
    print("6. FICHIERS EN TROP DANS LES DOSSIERS GERES")
    attendus = {dst for _, dst in FICHIERS}
    intrus = []
    for d in GERES:
        racine = os.path.join(DEPOT, d)
        for dossier, _, fichiers in os.walk(racine):
            if "__pycache__" in dossier:
                continue
            for f in fichiers:
                rel = os.path.relpath(os.path.join(dossier, f), DEPOT)
                if rel not in attendus:
                    intrus.append(rel)
    if intrus:
        for i in sorted(intrus):
            print("   EN TROP : " + i)
        print("   a retirer a la main, ou a ajouter a la liste")
        return 1
    print("   aucun")
    return 0


def releve_source():
    """md5 de tout ce que le script lit dans le dossier de travail."""
    r = {}
    for src, _ in FICHIERS:
        p = os.path.join(PROJET, src)
        if os.path.exists(p):
            r[src] = md5(p)
    return r


def main():
    ecrire = "--ecrire" in sys.argv
    print("Assemblage du depot public de Temoin")
    print("   source : " + PROJET)
    print("   depot  : " + DEPOT)
    print("   mode   : " + ("ECRITURE" if ecrire else "mesure seule"))
    print()

    codes = [section_1_presence(), section_2_autosuffisance()]
    if codes[0] == 1:
        print()
        print("Un fichier annonce manque dans la source. Rien n est ecrit.")
        return 2

    if ecrire:
        avant = releve_source()
        assembler()
        print()
        codes.append(section_4_copie())
        codes.append(section_5_source_intacte(avant))
        print()
        codes.append(section_6_intrus())
    print()
    codes.append(section_3_documents())

    print()
    print("ECARTES VOLONTAIREMENT")
    for quoi, pourquoi in ECARTES.items():
        print("   %s" % quoi)
        print("      %s" % pourquoi)

    print()
    signales = sum(1 for c in codes if c == 1)
    if signales:
        print("%d section(s) signalent." % signales)
        return 1
    print("0 anomalie sur %d sections." % len(codes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
