#!/usr/bin/env python3
"""Controle des tables de finalisation, ce que `finaliser.py` pose.

POURQUOI CE CONTROLE EXISTE. Le soixante-deuxieme tour a mesure que AUCUN des
quatorze controles du projet ne lit `STAT`, `gasp` ni `prep`. Le projet avait
prouve son crenage, ses contacts, ses coupes, son point fixe et son repertoire,
et personne n'avait jamais regarde la table qui nomme les graisses -- si bien
que le binaire servi portait un `STAT` a un seul axe et zero valeur nommee sans
que rien ne le dise. C'est le point ouvert 109.

Le point 10 ayant ete tranche en faveur de la chaine du projet augmentee, le
projet devient PROPRIETAIRE de ces tables. Elles demandent donc leur controle,
avec temoin, comme les quatorze autres.

CE QUE CE CONTROLE NE FAIT PAS, et pourquoi. Il ne dit pas que le dessin est
conforme : douze autres controles s'en chargent sur la source, et l'egalite du
dessin avant et apres finalisation a ete prouvee au soixante-deuxieme tour a
trois positions de l'axe. Il ne remplace pas Font Bakery, qui reste le critere
EXTERIEUR -- 0 FAIL, 14 ERROR, 19 WARN, 163 SKIP et 246 PASS en profil
`check-googlefonts` depuis le soixante-quatrieme tour. Et la cible exterieure
ne suffit pas : aucun controle de Font Bakery ne voit manquer les sept noms
PostScript d'instance, que la section 5 mesure ici, et les sections 9 et 10 ne
crieraient qu'a un lancement manuel de Font Bakery, qui n'est pas dans la
chaine du projet.

DIX SECTIONS depuis le soixante-sixieme tour. Les huit premieres lisent les
deux binaires compiles, les 7 et 10 lisent les WOFF2 SERVIS. Les sections 9 et
10 ferment le point ouvert 112 : elles couvrent les deux gestes de nommage du
soixante-troisieme tour et les noms localises du soixante-cinquieme.

Trois codes de retour, convention du cinquante-neuvieme tour : 0 mesure et
conforme, 1 mesure et signale, 2 NON MESURE.

    TEMOIN_BUILD=/tmp/bN python3 check_final.py
    TEMOIN_BUILD=/tmp/bN python3 check_final.py --temoin
"""

import os
import re
import sys

from fontTools.ttLib import TTFont

import finaliser as FZ
import subset as SU

ICI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.environ.get("TEMOIN_BUILD", "/tmp/build-temoin")

# Les deux variables finalisees, sous leur nom canonique.
CANONIQUES = ("Temoin[wght].ttf", "Temoin-Italic[wght].ttf")

# Les deux binaires servis, que les sections 7 et 10 regardent. Le dossier est
# celui que `subset.py` ecrit, `fonts/` dans le depot, `gabarits/fonts/` dans
# le dossier de travail : point ouvert 116, soixante-et-onzieme tour.
SERVIS = [os.path.join(SU.DEST, n)
          for n in ("Temoin.woff2", "Temoin-Italic.woff2")]

PREP_ATTENDU = "b801ff85b0048d"


# ------------------------------------------------------------------ lecture

def _nom(font, ident):
    return FZ._nom(font, ident)


def _nom_langue(font, ident, cle):
    """La chaine d'un identifiant de nom DANS UNE LANGUE PRECISE, ou None.

    `FZ._nom` se replie sur n'importe quelle plateforme quand la chaine Windows
    anglaise manque, ce qui est juste pour ecrire et faux pour mesurer : un
    repli ferait passer l'entree anglaise pour l'entree francaise, et la section
    10 rendrait conforme un servi qui a perdu ses noms localises. Ici, pas de
    repli.
    """
    for r in font["name"].names:
        if (r.nameID == ident
                and (r.platformID, r.platEncID, r.langID) == cle):
            return str(r)
    return None


def profil_stat(font):
    """Le profil SEMANTIQUE de la STAT : les noms sont resolus en chaines.

    Comparer des identifiants de nom serait comparer une numerotation, qui n'a
    aucune portee : deux tables peuvent nommer la meme chose par des
    identifiants differents. C'est le piege de l'etiquette prise pour une
    mesure, consigne depuis le projet.
    """
    if "STAT" not in font:
        return None
    t = font["STAT"].table
    axes = [(a.AxisTag, a.AxisOrdering, _nom(font, a.AxisNameID))
            for a in t.DesignAxisRecord.Axis]
    av = getattr(t, "AxisValueArray", None)
    valeurs = sorted(
        (v.Format, v.Flags, v.AxisIndex, getattr(v, "Value", None),
         getattr(v, "LinkedValue", None), _nom(font, v.ValueNameID))
        for v in (av.AxisValue if av else []))
    return {"elide": getattr(t, "ElidedFallbackNameID", None),
            "axes": axes, "valeurs": valeurs}


def stat_attendue(font):
    """La STAT que le projet exige, construite depuis les constantes."""
    valeurs = []
    for valeur, nom in FZ.GRAISSES:
        if valeur == FZ.REGULIER:
            valeurs.append((3, FZ.DRAPEAU_ELIDABLE, 0, float(valeur),
                            float(FZ.GRAS_LIE), nom))
        else:
            valeurs.append((1, 0, 0, float(valeur), None, nom))
    if FZ.est_italique(font):
        valeurs.append((1, 0, 1, 1.0, None, "Italic"))
    else:
        valeurs.append((3, FZ.DRAPEAU_ELIDABLE, 1, 0.0, 1.0, "Roman"))
    return {"elide": FZ.ELIDE_PAR_DEFAUT,
            "axes": [("wght", 0, "Weight"), ("ital", 1, "Italic")],
            "valeurs": sorted(valeurs)}


# ----------------------------------------------------------------- sections

def section1(font):
    """gasp [GARDE]"""
    if "gasp" not in font:
        return ["1. gasp                   [GARDE]  !! table ABSENTE : "
                "smart_dropout et googlefonts.gasp echouent"], 1
    t = font["gasp"]
    obtenu = (t.version, dict(t.gaspRange))
    attendu = (FZ.GASP_VERSION, dict(FZ.GASP_RANGES))
    if obtenu != attendu:
        return [f"1. gasp                   [GARDE]  !! {obtenu} au lieu de "
                f"{attendu}"], 1
    return [f"1. gasp                   [GARDE]  version {t.version}, "
            f"{dict(t.gaspRange)}"], 0


def section2(font):
    """prep [GARDE]"""
    if "prep" not in font:
        return ["2. prep                   [GARDE]  !! table ABSENTE : le "
                "controle de dropout intelligent manque"], 1
    octets = font["prep"].program.getBytecode().hex()
    if octets != PREP_ATTENDU:
        return [f"2. prep                   [GARDE]  !! {octets} au lieu de "
                f"{PREP_ATTENDU}"], 1
    return [f"2. prep                   [GARDE]  {len(octets)//2} octets, "
            f"SCANCTRL 511 puis SCANTYPE 4"], 0


def section3(font):
    """STAT [INVARIANT]"""
    obtenu, attendu = profil_stat(font), stat_attendue(font)
    if obtenu is None:
        return ["3. STAT                   [INVARIANT]  !! table ABSENTE"], 1
    lignes, n = [], 0
    if obtenu["axes"] != attendu["axes"]:
        lignes.append(f"   !! axes {obtenu['axes']} au lieu de "
                      f"{attendu['axes']}")
        n += 1
    if obtenu["elide"] != attendu["elide"]:
        lignes.append(f"   !! ElidedFallbackNameID {obtenu['elide']} au lieu "
                      f"de {attendu['elide']}")
        n += 1
    manquantes = [v for v in attendu["valeurs"] if v not in obtenu["valeurs"]]
    en_trop = [v for v in obtenu["valeurs"] if v not in attendu["valeurs"]]
    for v in manquantes:
        lignes.append(f"   !! valeur manquante ou alteree : {v}")
        n += 1
    for v in en_trop:
        lignes.append(f"   !! valeur inattendue : {v}")
        n += 1
    tete = (f"3. STAT                   [INVARIANT]  "
            f"{len(obtenu['axes'])} axes, {len(obtenu['valeurs'])} valeurs")
    return [tete] + lignes, n


def section4(font):
    """name ID 25 [GARDE]"""
    obtenu = _nom(font, 25)
    attendu = FZ.prefixe_postscript(font)
    if obtenu is None:
        return [f"4. name ID 25             [GARDE]  !! ABSENT, attendu "
                f"{attendu}"], 1
    if obtenu != attendu:
        return [f"4. name ID 25             [GARDE]  !! {obtenu} au lieu de "
                f"{attendu}"], 1
    return [f"4. name ID 25             [GARDE]  {obtenu}"], 0


def section5(font):
    """noms PostScript d'instance [GARDE]

    LA SECTION QU'AUCUN CONTROLE EXTERIEUR NE REMPLACE : les binaires passent
    `opentype.varfont.valid_nameids`, `varfont.duplicate_instance_names` et
    `googlefonts.fvar_instances` avec ou sans ces noms.
    """
    famille = FZ.famille_postscript(font)
    lignes, n = [], 0
    vus = []
    for inst in font["fvar"].instances:
        style = _nom(font, inst.subfamilyNameID)
        attendu = f"{famille}-{(style or '').replace(' ', '')}"
        if inst.postscriptNameID in (None, 0xFFFF):
            lignes.append(f"   !! {style} : aucun nom PostScript, attendu "
                          f"{attendu}")
            n += 1
            continue
        obtenu = _nom(font, inst.postscriptNameID)
        if obtenu != attendu:
            lignes.append(f"   !! {style} : {obtenu} au lieu de {attendu}")
            n += 1
        vus.append(obtenu)
    tete = (f"5. noms PS d'instance     [GARDE]  {len(vus)} sur "
            f"{len(font['fvar'].instances)}"
            + (f", {vus[0]} .. {vus[-1]}" if vus else ""))
    return [tete] + lignes, n


def section6(font):
    """composites imbriques [MESURE]

    `finaliser.py` NE SAIT PAS aplatir : le filtre vit dans `fontmake` et se
    demande a la compilation. Un drapeau oublie ne laisse aucune trace, donc il
    se mesure ici. C'est la forme du piege du zero-diff : sans cette section,
    l'absence du filtre serait invisible.
    """
    trouves = FZ.composites_imbriques(font)
    if trouves:
        return [f"6. composites imbriques   [MESURE]  !! {len(trouves)} : "
                f"--filter FlattenComponentsFilter oublie a la compilation. "
                f"Exemples {' '.join(trouves[:4])}"], 1
    return ["6. composites imbriques   [MESURE]  aucun, le filtre a bien "
            "tourne"], 0


def _servis(fontes=None):
    """Les deux WOFF2 servis, ouverts, ou None si l'un manque.

    L'ARGUMENT `fontes` N'EST PAS UN CONFORT : il est ce qui rend les sections
    du servi exercables par un temoin. Avant le soixante-sixieme tour, la
    section 7 lisait ses fichiers elle-meme, donc aucun faussage ne pouvait
    l'atteindre, et elle etait la seule section du controle que le temoin ne
    couvrait pas. Une section jamais exercee est une cecite en puissance.
    """
    if fontes is not None:
        return list(fontes)
    ouverts = []
    for chemin in SERVIS:
        if not os.path.exists(chemin):
            return None
        ouverts.append((os.path.basename(chemin), TTFont(chemin)))
    return ouverts


def section7(fontes=None):
    """le servi porte-t-il les ajouts [DECLARATION]

    Cette section mesure les WOFF2 servis et non la sortie de compilation. Au
    soixante-deuxieme tour elle SIGNALE PAR CONSTRUCTION : la decision a ete
    prise, les binaires servis n'ont pas encore ete regeneres, et c'est le lot 4
    qui la ferme. Un rappel qui crie vaut mieux qu'une dette dans un document.
    """
    lignes, n = [], 0
    ouverts = _servis(fontes)
    if ouverts is None:
        return ["7. le servi               [DECLARATION]",
                "   NON MESURE : un WOFF2 servi est absent"], -1
    # LE SERVI EST REDUIT A AXE_SERVI depuis le soixante-et-onzieme tour, point
    # ouvert 3 : la STAT n'y garde que les graisses de la plage, plus la valeur
    # de l'axe `ital`. Six valeurs a 400-800, contre huit sur le compile.
    lo, defaut, hi = SU.AXE_SERVI
    attendu_nb = sum(1 for v, _ in FZ.GRAISSES if lo <= v <= hi) + 1
    for nom, f in ouverts:
        manque = [t for t in ("gasp", "prep") if t not in f]
        st = profil_stat(f)
        axes = [a[0] for a in st["axes"]] if st else []
        nb = len(st["valeurs"]) if st else 0
        axe = None
        if "fvar" in f:
            a = f["fvar"].axes[0]
            axe = (a.minValue, a.defaultValue, a.maxValue)
        if manque or axes != ["wght", "ital"] or nb != attendu_nb:
            lignes.append(
                f"   !! {nom} : tables absentes {manque or 'aucune'}, "
                f"STAT axes {axes}, {nb} valeur(s) nommee(s) pour "
                f"{attendu_nb} attendues. Le servi date d'avant la decision "
                f"du soixante-deuxieme tour, ou d'avant la reduction d'axe du "
                f"soixante-et-onzieme.")
            n += 1
        elif axe != tuple(float(x) for x in SU.AXE_SERVI):
            lignes.append(
                f"   !! {nom} : axe wght {axe}, attendu {SU.AXE_SERVI}. Le "
                f"sous-ensemblage n'a pas reduit l'axe.")
            n += 1
        else:
            lignes.append(f"   {nom} : gasp, prep, STAT a {nb} valeurs, "
                          f"axe {lo}-{hi}")
    return ["7. le servi               [DECLARATION]"] + lignes, n



# ---------------------------------------------- recouvrements de contour, 64e

# Les recouvrements ACCEPTES, mesures au soixante-quatrieme tour sur les cinq
# positions de l'axe et les deux sources, Atkinson en temoin. La cle est
# (source, nom), la valeur le pourcentage d'aire d'encre reellement recouverte
# au pire master, et le nombre de positions sur cinq ou le recouvrement existe.
#
# POURQUOI UNE TABLE ET PAS UN SEUIL UNIQUE. Un variable GARDE ses
# recouvrements : les supprimer casse l'interpolation, puisque le recouvrement
# change le long de l'axe. Un recouvrement n'est donc pas un defaut en soi, et
# deux des quatre lignes ci-dessous sont VOULUES -- le bras du `O`, ecrit au
# quarante-huitieme tour et valide en navigateur, et le `musicalnote` herite
# d'Atkinson a la valeur pres. Ce qui doit crier, c'est un recouvrement NEUF,
# ou un recouvrement connu qui GROSSIT.
#
# Les deux dernieres lignes sont les limites connues du soixante-quatrieme
# tour, fermeture du point 107 : `brevecomb` et `tildecomb` se recoupent a une
# position sur cinq, de 0,004 a 0,113 % de leur encre, soit trente fois moins
# que le bras du `O` que le projet sert et assume. Invisibles a 18 px comme a
# 420 px, mesure sur planche.
RECOUVREMENTS_CONNUS = {
    ("romain",   "musicalnote"): (2.843, 5, "herite d'Atkinson a l'identique, hors sous-ensemble servi"),
    ("italique", "musicalnote"): (2.843, 5, "herite d'Atkinson a l'identique, hors sous-ensemble servi"),
    ("romain",   "O"):           (2.643, 5, "le bras du O, quarante-huitieme tour, VOULU"),
    ("romain",   "brevecomb"):   (0.085, 1, "limite connue, soixante-quatrieme tour, point 107"),
    ("italique", "brevecomb"):   (0.113, 1, "limite connue, soixante-quatrieme tour, point 107"),
    ("romain",   "tildecomb"):   (0.081, 1, "limite connue, soixante-quatrieme tour, point 107"),
    ("italique", "tildecomb"):   (0.004, 1, "limite connue, soixante-quatrieme tour, point 107"),
}

# En dessous, c'est du bruit numerique de la rasterisation vectorielle.
RECOUVREMENT_PLANCHER = 0.5      # unites carrees
RECOUVREMENT_POSITIONS = (200, 400, 700, 750, 800)


def _marge(pct):
    """Plafond d'un recouvrement connu : moitie en plus, et au moins un
    demi-point de pourcentage. Un dessin qui bouge un peu ne doit pas crier ;
    un dessin qui casse, si."""
    return max(pct * 1.5, pct + 0.5)


def section8(font, source=None):
    """recouvrements de contour [MESURE]

    Mesure l'aire d'encre qu'un glyphe se recoupe a lui-meme, aux cinq
    positions de l'axe, et la confronte a la table des recouvrements acceptes.

    POURQUOI CETTE SECTION EXISTE. Le soixante-quatrieme tour a ferme le point
    107 en limite connue. Une limite ecrite dans un document se perd ; une
    limite mesuree crie quand elle bouge. La section a par ailleurs trouve
    toute seule ce qu'`interpolatable` ne signale a aucun seuil : le
    `tildecomb` ROMAIN se recoupe aussi, et le bras du `O` se recoupe trente
    fois plus que tout le lot 3 sans que personne l'ait jamais mesure.

    DEPENDANCE. Elle demande `skia-pathops`, que la chaine officielle epingle
    deja. Absent, la section rend NON MESURE et le dit, plutot qu'un zero qui
    se lirait comme un succes.
    """
    try:
        import pathops
    except ImportError:
        return ["8. recouvrements          [MESURE]  NON MESURE : "
                "skia-pathops absent, pip install skia-pathops"], -1
    from fontTools.varLib import instancer

    import io
    if source is None:
        source = "italique" if "Italic" in str(getattr(font, "reader", "")) else "romain"
    # On repart d'une image MEMOIRE du font recu, et non du fichier sur le
    # disque : sans cela un faussage pose par le temoin serait relu depuis le
    # disque intact, et la section serait muette en croyant mesurer.
    tampon = io.BytesIO()
    font.save(tampon)
    vus = {}
    for pos in RECOUVREMENT_POSITIONS:
        tampon.seek(0)
        f = instancer.instantiateVariableFont(
            TTFont(tampon), {"wght": pos}, inplace=True)
        gs = f.getGlyphSet()
        for nom in f.getGlyphOrder():
            try:
                p = pathops.Path()
                gs[nom].draw(p.getPen())
                aire = abs(p.area)
                if aire < 1:
                    continue
                q = pathops.Path(p)
                q.simplify(fix_winding=True, keep_starting_points=False)
                ecart = abs(aire - abs(q.area))
                if ecart > RECOUVREMENT_PLANCHER:
                    pct = 100.0 * ecart / aire
                    prec = vus.get(nom, (0.0, 0))
                    vus[nom] = (max(prec[0], pct), prec[1] + 1)
            except Exception:
                pass

    lignes, n = [], 0
    for nom in sorted(vus, key=lambda k: -vus[k][0]):
        pct, nb = vus[nom]
        connu = RECOUVREMENTS_CONNUS.get((source, nom))
        if connu is None:
            lignes.append(f"   !! {nom} : {pct:.3f} % sur {nb} position(s), "
                          f"RECOUVREMENT NEUF, absent de la table")
            n += 1
        elif pct > _marge(connu[0]):
            lignes.append(f"   !! {nom} : {pct:.3f} % sur {nb} position(s), "
                          f"contre {connu[0]:.3f} % au soixante-quatrieme tour, "
                          f"plafond {_marge(connu[0]):.3f} %. Il GROSSIT.")
            n += 1
        else:
            lignes.append(f"   {nom} : {pct:.3f} % sur {nb} position(s) -- "
                          f"{connu[2]}")
    manquants = [k[1] for k in RECOUVREMENTS_CONNUS
                 if k[0] == source and k[1] not in vus]
    for nom in sorted(manquants):
        lignes.append(f"   {nom} : plus aucun recouvrement, la table le "
                      f"croyait a {RECOUVREMENTS_CONNUS[(source, nom)][0]:.3f} %")
    tete = (f"8. recouvrements          [MESURE]  {len(vus)} glyphe(s) qui se "
            f"recoupent, source {source}")
    return [tete] + lignes, n


# ------------------------------------------- les gestes de nommage, 63e et 65e

# La convention OpenType pour un nom de glyphe : une lettre ou un blanc
# souligne en tete, puis lettres, chiffres, points et blancs soulignes,
# 63 caracteres au plus. `note-musical`, herite d'Atkinson, la violait par son
# tiret, et le soixante-troisieme tour l'a renomme `musicalnote`.
NOM_GLYPHE = re.compile(r"^[A-Za-z_][A-Za-z0-9._]{0,62}$")

# Deux noms RESERVES echappent a la regle, et commencent par un point. Le
# premier jet de cette section signalait `.notdef` dans les deux sources : une
# regle juste sur 310 glyphes et fausse sur celui que toute police porte.
NOMS_RESERVES = {".notdef", ".null"}

# Le libelle du jeu stylistique, arrete au soixante-troisieme tour : un seul
# enregistrement, en anglais.
SS01_LIBELLE = "Unslashed zero"


def _params_ss01(font):
    """Les `FeatureParams` de chaque enregistrement `ss01` du GSUB.

    Il y en a un par couple script-langue, donc plusieurs, et ils pointent
    normalement tous vers le meme enregistrement de nom. Comparer leur
    ensemble, et non le premier, fait crier une divergence entre scripts.
    """
    if "GSUB" not in font:
        return []
    liste = font["GSUB"].table.FeatureList
    return [rec.Feature.FeatureParams for rec in liste.FeatureRecord
            if rec.FeatureTag == "ss01"]


def section9(font):
    """gestes de nommage sur le COMPILE [MESURE]

    POURQUOI CETTE SECTION EXISTE. Les deux gestes du soixante-troisieme tour
    ne sont vus que par Font Bakery, qui n'est PAS dans la chaine du projet :
    une regression ne crierait qu'au prochain lancement manuel, et le
    soixante-deuxieme tour a etabli que le projet ne peut pas s'en remettre a
    un controle exterieur qu'il ne lance pas. Point ouvert 112.

    Elle mesure ce que le producteur ecrit, `make_temoin.renommer` et le
    `featureNames` d'`add_features`, sur le binaire qui en sort. La source ne
    prouverait rien : le quinzieme piege du projet dit qu'un lecteur qui passe
    par le meme accesseur que l'ecrivain rend le meme faux positif.
    """
    lignes, n = [], 0
    ordre = font.getGlyphOrder()

    fautifs = [g for g in ordre
               if g not in NOMS_RESERVES and not NOM_GLYPHE.match(g)]
    if fautifs:
        lignes.append(f"9. nommage compile       [MESURE]  !! {len(fautifs)} "
                      f"nom(s) de glyphe hors convention OpenType : "
                      f"{' '.join(fautifs[:4])}")
        n += 1
    else:
        lignes.append(f"9. nommage compile       [MESURE]  {len(ordre)} noms "
                      f"de glyphe conformes")

    params = _params_ss01(font)
    if not params:
        lignes.append("   !! ss01 : aucun enregistrement dans le GSUB")
        n += 1
    else:
        libelles = {_nom(font, getattr(p, "UINameID", 0xFFFF))
                    for p in params}
        if libelles != {SS01_LIBELLE}:
            lignes.append(f"   !! ss01 : libelle(s) "
                          f"{sorted(repr(x) for x in libelles)}, attendu "
                          f"{SS01_LIBELLE!r} et lui seul")
            n += 1
        else:
            lignes.append(f"   ss01 : {len(params)} enregistrement(s), "
                          f"libelle {SS01_LIBELLE!r}")
    return lignes, n


def section10(fontes=None):
    """noms localises francais sur le SERVI [MESURE]

    LA MESURE PORTE SUR LE SERVI ET NON SUR LE COMPILE, et c'est tout le sujet.
    Au soixante-cinquieme tour, `finaliser.poser_noms_localises` ecrivait bien
    les deux noms francais dans le TTF compile, et `fontTools.subset` les
    supprimait ensuite : `--name-IDs=*` choisit les identifiants et pas les
    langues, et le sous-ensemblage ne garde par defaut que l'anglais. Le premier
    releve du servi rendait 32 enregistrements de nom, exactement ceux d'avant
    le geste, et le point 7 aurait ete annonce fait sur un livrable qui ne le
    portait pas. C'est le seizieme piege : une ecriture qui a eu lieu peut
    mourir plus loin dans la chaine.

    La garde de `poser_noms_localises` protege l'ECRITURE. Cette section protege
    le LIVRABLE, et les deux ne se remplacent pas.
    """
    lignes, n = [], 0
    ouverts = _servis(fontes)
    if ouverts is None:
        return ["10. noms localises       [MESURE]",
                "   NON MESURE : un WOFF2 servi est absent"], -1
    lignes.append("10. noms localises       [MESURE]")
    for nom, f in ouverts:
        famille = _nom_langue(f, 1, FZ.FRANCAIS)
        complet = _nom_langue(f, 4, FZ.FRANCAIS)
        ps = _nom_langue(f, 6, FZ.WINDOWS)
        defauts = []
        if famille != FZ.ACCENTUE:
            defauts.append(f"ID 1 francais = {famille!r}, attendu "
                           f"{FZ.ACCENTUE!r}")
        if not complet or not complet.startswith(FZ.ACCENTUE):
            defauts.append(f"ID 4 francais = {complet!r}, attendu un nom "
                           f"commencant par {FZ.ACCENTUE!r}")
        if ps is None or not ps.isascii():
            defauts.append(f"ID 6 PostScript = {ps!r}, il doit rester en "
                           f"ASCII pur")
        if defauts:
            for d in defauts:
                lignes.append(f"   !! {nom} : {d}")
            n += 1
        else:
            lignes.append(f"   {nom} : {famille!r} / {complet!r}, "
                          f"PostScript {ps!r} en ASCII")
    return lignes, n


SECTIONS = (section1, section2, section3, section4, section5,
            section6, section8, section9)


# ------------------------------------------------------------------- temoin

def _fausser(font, quoi):
    """Casse une seule chose, pour verifier que la section correspondante voit."""
    if quoi == "gasp":
        del font["gasp"]
    elif quoi == "prep":
        del font["prep"]
    elif quoi == "STAT":
        del font["STAT"]
    elif quoi == "nom25":
        font["name"].names = [r for r in font["name"].names if r.nameID != 25]
    elif quoi == "instances":
        for inst in font["fvar"].instances:
            inst.postscriptNameID = 0xFFFF
    elif quoi == "recouvrement":
        # On fait traverser le fut du `n` par un point de son propre contour,
        # sur un glyphe que la table des recouvrements connus ignore.
        #
        # LE PREMIER FAUSSAGE ESSAYE ETAIT MUET, et c'est la lecon : translater
        # un point de 60 unites DEFORME le glyphe sans le faire se recouper,
        # et la section rendait zero en ayant raison. Mesure au soixante-
        # quatrieme tour : translation de (-60, +60) -> 0,00 u2 ; echange de
        # deux points voisins -> 0,00 ; echange de deux points eloignes ->
        # 1 223 ; point pousse au-dela du bord droit -> 10 735. Un faussage
        # qui ne fausse pas la grandeur mesuree ne prouve rien.
        g = font["glyf"]
        if "n" not in font.getGlyphOrder() or g["n"].numberOfContours <= 0:
            return False
        c = g["n"].coordinates
        c[2] = (max(p[0] for p in c) + 200, c[2][1])
        g["n"].coordinates = c
    elif quoi == "nom-glyphe":
        # Remet un tiret dans un nom de glyphe, la faute exacte que le
        # soixante-troisieme tour a corrigee sur `note-musical`.
        ordre = list(font.getGlyphOrder())
        if len(ordre) < 2:
            return False
        ordre[-1] = "note-musical"
        font.setGlyphOrder(ordre)
    elif quoi == "ss01":
        params = _params_ss01(font)
        if not params:
            return False
        for p in params:
            p.UINameID = 0xFFFF
    elif quoi == "imbriques":
        # Refabrique un composite imbrique : `Agrave` pointe vers `gravecomb`,
        # on le fait pointer vers un composite. Sans glyphe composite sous la
        # main, la section ne peut pas etre exercee et le dit.
        g = font["glyf"]
        composites = [n for n in font.getGlyphOrder() if g[n].isComposite()]
        if len(composites) < 2:
            return False
        porteur, cible = composites[0], composites[1]
        g[porteur].components[0].glyphName = cible
    return True


# Chaque faussage, et la section qui doit le voir. UNE TABLE ET PLUS DEUX
# TUPLES PARALLELES, depuis le soixante-sixieme tour : la section 9 porte deux
# mesures et demande donc deux faussages, ce qu'un index commun interdisait.
EXERCICES = (
    ("gasp", section1), ("prep", section2), ("STAT", section3),
    ("nom25", section4), ("instances", section5), ("imbriques", section6),
    ("recouvrement", section8),
    ("nom-glyphe", section9), ("ss01", section9),
)


def _fausser_servi(f, quoi):
    """Casse une seule chose dans une copie en memoire d'un WOFF2 servi."""
    if quoi == "servi-gasp":
        del f["gasp"]
    elif quoi == "servi-loc1":
        f["name"].names = [r for r in f["name"].names
                           if not (r.nameID == 1 and r.langID == 0x40C)]
    elif quoi == "servi-loc4":
        f["name"].setName("Temoin Regular", 4, *FZ.FRANCAIS)
    elif quoi == "servi-ps":
        f["name"].setName("Témoin-Regular", 6, *FZ.WINDOWS)
    else:
        return False
    return True


EXERCICES_SERVI = (
    ("servi-gasp", section7),
    ("servi-loc1", section10), ("servi-loc4", section10),
    ("servi-ps", section10),
)


def temoin():
    """Chaque section doit mordre sur son propre faussage, et AUCUNE ne doit
    rester muette. Une section muette sous faussage est une cecite, pas un
    succes.

    LES SECTIONS DU SERVI SONT EXERCEES DEPUIS LE SOIXANTE-SIXIEME TOUR. Avant
    lui, la section 7 lisait ses fichiers elle-meme et aucun faussage ne
    l'atteignait : elle etait la seule section du controle qui n'avait jamais
    ete prouvee voyante.
    """
    chemins = [os.path.join(BUILD, n) for n in CANONIQUES]
    present = [c for c in chemins if os.path.exists(c)]
    if not present:
        print("NON MESURE : aucun binaire canonique dans "
              f"{BUILD}. Le temoin ne prouve rien.")
        return 2
    muettes, i = [], 0

    print(f"=== temoin sur {os.path.basename(present[0])}")
    for q, section in EXERCICES:
        i += 1
        font = TTFont(present[0])
        if not _fausser(font, q):
            print(f"  {i}. {q:<13} NON EXERCEE : le faussage n'a pas pu "
                  f"etre pose")
            muettes.append(q)
            continue
        lignes, n = (section(font, "romain") if section is section8
                     else section(font))
        etat = "MORD" if n > 0 else "MUETTE"
        if n <= 0:
            muettes.append(q)
        print(f"  {i}. {q:<13} {etat} ({n} anomalie(s))")

    sains = _servis()
    print("=== temoin sur le servi")
    if sains is None:
        print("  NON EXERCEES : un WOFF2 servi est absent, les sections 7 "
              "et 10 ne sont pas prouvees voyantes.")
        muettes.extend(q for q, _ in EXERCICES_SERVI)
    else:
        for q, section in EXERCICES_SERVI:
            i += 1
            copies = [(nom, TTFont(c)) for (nom, _), c
                      in zip(sains, SERVIS)]
            if not _fausser_servi(copies[0][1], q):
                print(f"  {i}. {q:<13} NON EXERCEE : le faussage n'a pas pu "
                      f"etre pose")
                muettes.append(q)
                continue
            lignes, n = section(copies)
            etat = "MORD" if n > 0 else "MUETTE"
            if n <= 0:
                muettes.append(q)
            print(f"  {i}. {q:<13} {etat} ({n} anomalie(s))")

    print()
    if muettes:
        print(f"!! {len(muettes)} section(s) MUETTE(S) sous leur propre "
              f"faussage : {' '.join(muettes)}")
        return 1
    print(f"Les {i} mesures mordent, AUCUNE MUETTE.")
    return 0


# --------------------------------------------------------------------- main

def main():
    if "--temoin" in sys.argv:
        return temoin()
    # Deux compteurs et pas un : une SOURCE absente et une SECTION non mesuree
    # ne sont pas la meme chose, et les additionner sous une seule etiquette
    # ferait dire au total "2 sections non mesurees" quand ce sont deux
    # binaires qui manquent. Une etiquette est une mesure.
    total, src_absentes, sect_non_mesurees, nb_sections = 0, 0, 0, 0
    for nom in CANONIQUES:
        chemin = os.path.join(BUILD, nom)
        print(f"=== {nom}")
        if not os.path.exists(chemin):
            print(f"  NON MESURE : {chemin} absent. Ce n'est pas un succes, "
                  f"c'est une mesure qui n'a pas eu lieu.")
            print(f"  Compiler avec --no-production-names ET "
                  f"--filter FlattenComponentsFilter, puis finaliser.py.")
            src_absentes += 1
            continue
        font = TTFont(chemin)
        n = 0
        source = "italique" if "Italic" in nom else "romain"
        for section in SECTIONS:
            lignes, k = (section8(font, source) if section is section8
                         else section(font))
            for ligne in lignes:
                print("  " + ligne)
            if k < 0:
                sect_non_mesurees += 1
            else:
                n += k
        print(f"  --- {nom} : {n} anomalie(s)")
        total += n
        nb_sections = len(SECTIONS)

    print("=== le binaire servi")
    for section in (section7, section10):
        lignes, k = section()
        for ligne in lignes:
            print("  " + ligne)
        if k < 0:
            sect_non_mesurees += 1
        else:
            total += k
        nb_sections += 1

    print(f"\nTOTAL : {total} anomalie(s) sur {nb_sections} section(s) jouee(s)")
    if src_absentes:
        print(f"  {src_absentes} binaire(s) canonique(s) ABSENT(S) : leurs "
              f"six sections n'ont pas ete jouees.")
    if sect_non_mesurees:
        print(f"  {sect_non_mesurees} section(s) NON MESUREE(S).")
    if src_absentes or sect_non_mesurees:
        print(f"  Ce n'est pas un succes, c'est une mesure qui ne prouve rien.")
        return 2 if total == 0 else 1
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
