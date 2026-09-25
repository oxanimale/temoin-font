#!/usr/bin/env python3
"""Controle du point 94 : la barre mediane du F et de la famille de l'E.

Sept sections et un temoin. Il lit l'etat ECRIT et le compare a la source
amont, en valeur absolue : la translation est exacte par construction, donc
rien ne s'y mesure en tendance.

POURQUOI UN CONTROLE AUTONOME. Aucun garde-fou du projet ne voit ce geste.
`check_perimetre` mesure des sortantes et un perimetre de titrage ; les trois
tables de paires ne regardent pas la hauteur d'une barre INTERNE ; et le temoin
d'`inventaire_F` compare la BOITE et la CHASSE du reconstruit au servi, qu'une
barre deplacee a l'interieur d'une lettre ne change ni l'une ni l'autre. Mesure
du cinquante-quatrieme tour : le geste applique seul, `inventaire_F` rend un
zero-diff exact sur ses 383 paires pendant que `check_approches` crie douze
fois. Une boite n'est pas une forme, et c'est ici la troisieme fois que le
projet le paie.
"""

import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dessin as D
import lot2 as L
import barre_mediane as BM
from balayage_lot4b import couloir_exact
from check_approches import AMONT, MASTERS

ICI = os.path.dirname(os.path.abspath(__file__))
TEMOIN = {"roman": os.path.join(ICI, "Temoin.glyphs"),
          "italic": os.path.join(ICI, "Temoin-Italic.glyphs")}

#: Les sept capitales accentuees qui COMPOSENT l'E. Elles suivent le geste sans
#: etre nommees, et la section 5 le remesure : une composition decomposee en
#: amont les laisserait sur place sans que rien d'autre le dise.
ACCENTUEES = ("Eacute", "Egrave", "Ecircumflex", "Edieresis",
              "Ecaron", "Edotaccent", "Emacron")

#: Les quatre petites capitales qui heritent par la derivation du lot 3.
PETITES = (("f.sc", 0.0), ("e.sc", 0.0), ("ae.sc", 0.55), ("oe.sc", 0.65))
BANDE_SC = (150.0, 420.0)

#: Les voisins de la section 7. La barre mediane gouverne le blanc a MI-HAUTEUR
#: a droite du F et de l'E : l'echantillon prend ce qui presente de la matiere
#: a cette hauteur -- deux rondes, une diagonale montante, une descendante, une
#: capitale a barre haute, un point, et un l comme temoin negatif, dont le fut
#: ne change rien a cette hauteur.
VOISINS = ("o", "a", "v", "x", "T", "period", "l")

#: Partage avec `approches` et non recopie.
JOUR_MIN = 24.0

TOL = 0.26

#: Le rapport de derivation du lot 3, `make_temoin.HAUTEUR_SC` sur la hauteur
#: de capitale. Il ne se recopie pas a la main : la section 6 en a besoin pour
#: savoir quel ecart la petite capitale doit heriter.
RAPPORT_SC = 574.0 / 668.0
TOL_SC = 0.3


def _charger():
    out = {}
    for cle in ("roman", "italic"):
        out[cle] = (glyphsLib.load(open(AMONT[cle], encoding="utf-8")),
                    glyphsLib.load(open(TEMOIN[cle], encoding="utf-8")))
    return out


def _centre(font, mn, nom, depart=0.0, bande=None):
    vieille = BM.BANDE
    if bande:
        BM.BANDE = bande
    try:
        return BM.centre(D.Source(font, mn), nom, depart)
    finally:
        BM.BANDE = vieille


def _barre(font, mn, nom, depart=0.0):
    b, h, _ = BM.barre(D.Source(font, mn), nom, depart)
    return b, h


def _chasse(font, nom, mn):
    g = font.glyphs[nom]
    m = [x for x in font.masters if x.name == mn]
    if g is None or not m:
        return None
    lay = next((l for l in g.layers if l.layerId == m[0].id), None)
    return None if lay is None else lay.width


def section1(src, facteur=1.0):
    """1. CHAQUE BARRE VAUT-ELLE ATKINSON PLUS SON DEPLACEMENT ?

    L'exigence est posee contre la SOURCE AMONT, ce qui couvre deux choses : le
    deplacement lui-meme, et le fait qu'aucune etape anterieure n'a touche
    cette barre. Le projet n'en a jamais touche la hauteur ; il en a coupe le
    BOUT au lot 2, et cette coupe voyage avec elle.
    """
    print("\n1. chaque barre vaut Atkinson plus son deplacement")
    anomalies = 0
    for cle, (amont, tem) in src.items():
        ecarts = []
        for mn in MASTERS[cle]:
            dF, dE = BM.DEPLACEMENTS[mn]
            for nom, dep in BM.GLYPHES:
                attendu = (dF if nom == "F" else dE) * facteur
                a = _centre(amont, mn, nom, dep)
                t = _centre(tem, mn, nom, dep)
                if abs((t - a) - attendu) > TOL:
                    ecarts.append((mn, nom, a, t, attendu))
        n = len(MASTERS[cle]) * len(BM.GLYPHES)
        print(f"  {cle} : {len(ecarts)} ecart(s) sur {n} glyphe-masters")
        for mn, nom, a, t, att in ecarts[:8]:
            print(f"     !! {nom} {mn} : {a:.1f} -> {t:.1f}, attendu {att:+.1f}")
        anomalies += len(ecarts)
    return anomalies


def section2(src):
    """2. LE F REJOINT-IL L'E, ET LA FAMILLE GARDE-T-ELLE SES ECARTS ?

    Les deux faits que la decision de Nicolas demande. Le second n'est pas une
    formalite : l'OE ExtraLight porte sa barre 0,5 unite sous celle de l'E, un
    fait d'Atkinson que personne n'avait mesure, et une cible absolue l'aurait
    corrige en silence dans un master valide tel quel.
    """
    print("\n2. le F rejoint l'E, et la famille garde ses ecarts")
    anomalies = 0
    for cle, (amont, tem) in src.items():
        mauvais = []
        for mn in MASTERS[cle]:
            cf, ce = _centre(tem, mn, "F"), _centre(tem, mn, "E")
            if abs(cf - ce) > TOL:
                mauvais.append((mn, f"F {cf:.1f} contre E {ce:.1f}"))
            for nom, dep in BM.GLYPHES:
                if nom not in BM.SOLIDAIRES:
                    continue
                ea = _centre(amont, mn, nom, dep) - _centre(amont, mn, "E")
                et = _centre(tem, mn, nom, dep) - ce
                if abs(et - ea) > TOL:
                    mauvais.append((mn, f"{nom}-E : {ea:+.1f} -> {et:+.1f}"))
        print(f"  {cle} : {len(mauvais)} ecart(s) sur "
              f"{len(MASTERS[cle]) * (1 + len(BM.SOLIDAIRES))} mesures")
        for mn, txt in mauvais[:8]:
            print(f"     !! {mn} : {txt}")
        anomalies += len(mauvais)
    return anomalies


def section3(src):
    """3. LES EPAISSEURS SONT-ELLES INTACTES ?

    Le decrochage d'Atkinson est une TRANSLATION et pas un amaigrissement : les
    deux barres ont la meme epaisseur avant le geste, et elles doivent l'avoir
    apres. Une epaisseur qui bouge signalerait que le filtre a pris un bord et
    pas l'autre.
    """
    print("\n3. les epaisseurs de barre sont intactes")
    anomalies = 0
    for cle, (amont, tem) in src.items():
        ecarts = []
        for mn in MASTERS[cle]:
            for nom, dep in BM.GLYPHES:
                ba, ha = _barre(amont, mn, nom, dep)
                bt, ht = _barre(tem, mn, nom, dep)
                if abs((ht - bt) - (ha - ba)) > TOL:
                    ecarts.append((mn, nom, ha - ba, ht - bt))
        print(f"  {cle} : {len(ecarts)} ecart(s) sur "
              f"{len(MASTERS[cle]) * len(BM.GLYPHES)} glyphe-masters")
        for mn, nom, a, t in ecarts[:8]:
            print(f"     !! {nom} {mn} : {a:.1f} -> {t:.1f}")
        anomalies += len(ecarts)
    return anomalies


def section4(src):
    """4. AUCUNE CHASSE N'EST TOUCHEE.

    Ni sur les cinq nommes, ni sur les sept accentuees qui les composent. Le
    projet ne touche plus aucune chasse depuis le vingt-quatrieme tour.
    """
    print("\n4. aucune chasse n'est touchee")
    anomalies = 0
    noms = [n for n, _ in BM.GLYPHES] + list(ACCENTUEES)
    for cle, (amont, tem) in src.items():
        ecarts = []
        for mn in MASTERS[cle]:
            for nom in noms:
                a, t = _chasse(amont, nom, mn), _chasse(tem, nom, mn)
                if a is None or t is None or abs(a - t) > 0.01:
                    ecarts.append((mn, nom, a, t))
        print(f"  {cle} : {len(ecarts)} ecart(s) sur "
              f"{len(MASTERS[cle]) * len(noms)} glyphe-masters")
        for mn, nom, a, t in ecarts[:8]:
            print(f"     !! {nom} {mn} : {a} -> {t}")
        anomalies += len(ecarts)
    return anomalies


def section5(src):
    """5. LES SEPT ACCENTUEES SUIVENT L'E.

    Elles le COMPOSENT, donc elles suivent par construction -- et c'est
    justement ce qui se mesure ici. Une table indexee par nom ne suit pas une
    composition, le projet l'a paye six fois dans l'autre sens ; si une de ces
    sept etait decomposee en contours propres par une etape amont, elle
    resterait sur l'ancienne hauteur sans que rien d'autre le signale.
    """
    print("\n5. les sept capitales accentuees suivent l'E")
    anomalies = 0
    for cle, (_amont, tem) in src.items():
        ecarts = []
        for mn in MASTERS[cle]:
            ce = _centre(tem, mn, "E")
            for nom in ACCENTUEES:
                if tem.glyphs[nom] is None:
                    ecarts.append((mn, nom, None))
                    continue
                c = _centre(tem, mn, nom)
                if abs(c - ce) > TOL:
                    ecarts.append((mn, nom, c))
        print(f"  {cle} : {len(ecarts)} ecart(s) sur "
              f"{len(MASTERS[cle]) * len(ACCENTUEES)} glyphe-masters")
        for mn, nom, c in ecarts[:8]:
            print(f"     !! {nom} {mn} : {c}")
        anomalies += len(ecarts)
    return anomalies


def section6(src):
    """6. LES QUATRE PETITES CAPITALES HERITENT.

    Elles ne sont ecrites nulle part : le lot 3 les derive de la capitale, et
    l'appel du geste est place AVANT lui pour cela. L'ecart y valait 33,2 unites
    au Bold et 39,2 a l'ExtraBold, plus grand que sur la capitale, la derivation
    prenant celle-ci plus haut sur l'axe de graisse.

    L'EXIGENCE N'EST PAS L'EGALITE, ET UN PREMIER JET S'Y EST TROMPE. `oe.sc`
    sort 0,35 unite sous `e.sc` en ExtraLight, parce que l'OE capitale porte
    0,5 unite d'ecart a l'E dans Atkinson et que la derivation la reduit au
    rapport 574/668. La section exige donc l'ecart HERITE de la capitale du
    meme master : zero la ou la capitale est alignee, et la fraction juste la
    ou elle ne l'est pas.
    """
    print("\n6. les quatre petites capitales heritent, f.sc comprise")
    anomalies = 0
    for cle, (_amont, tem) in src.items():
        ecarts = []
        for mn in MASTERS[cle]:
            ref = _centre(tem, mn, "e.sc", 0.0, BANDE_SC)
            ce = _centre(tem, mn, "E")
            for nom, dep in PETITES:
                if tem.glyphs[nom] is None:
                    ecarts.append((mn, nom, None, ref, 0.0))
                    continue
                base = {"f.sc": "F", "e.sc": "E", "ae.sc": "AE", "oe.sc": "OE"}[nom]
                dep_cap = dict(BM.GLYPHES)[base]
                attendu = (_centre(tem, mn, base, dep_cap) - ce) * RAPPORT_SC
                c = _centre(tem, mn, nom, dep, BANDE_SC)
                if abs((c - ref) - attendu) > TOL_SC:
                    ecarts.append((mn, nom, c, ref, attendu))
        print(f"  {cle} : {len(ecarts)} ecart(s) sur "
              f"{len(MASTERS[cle]) * len(PETITES)} glyphe-masters")
        for mn, nom, c, ref, att in ecarts[:8]:
            print(f"     !! {nom} {mn} : {c} contre e.sc {ref:.1f}, attendu {att:+.2f}")
        anomalies += len(ecarts)
    return anomalies


def section7(src):
    """7. CE QUE LE DEPLACEMENT OUVRE ET FERME, PUISQUE RIEN NE LE MESURE.

    Couloir vrai entre le F ou l'E et sept voisins, dans les deux sens, bande
    pleine et sans crenage.

    LA REFERENCE EST L'ETAT ECRIT PRIVE DU GESTE, et non la source amont : le F
    porte une coupe de bout de barre depuis le lot 2 et une plongee de pied,
    donc comparer a l'amont imputerait au deplacement ce que le projet a fait
    ailleurs. Le piege a ete paye au cinquante-troisieme tour.

    ELLE NE PEUT PAS EXIGER « JAMAIS PLUS SERRE QU'AVANT » : le geste monte la
    barre du F, donc il resserre par construction du cote ou il monte. Elle
    exige le PLANCHER DE JOUR, 24 unites. Ce qui reste au-dessus est imprime
    comme un COUT.
    """
    print("\n7. les couloirs devant et derriere le F et l'E, bande pleine")
    anomalies = 0
    for cle, (_amont, tem) in src.items():
        avant = glyphsLib.load(open(TEMOIN[cle], encoding="utf-8"))
        BM.appliquer(avant, sens=-1)
        pire, sous = [], []
        for mn in MASTERS[cle]:
            s0, st = D.Source(avant, mn), D.Source(tem, mn)
            for cible in ("F", "E"):
                for v in VOISINS:
                    if tem.glyphs[v] is None:
                        continue
                    for a, b in ((cible, v), (v, cible)):
                        c0 = couloir_exact(s0, a, b)
                        ct = couloir_exact(st, a, b)
                        if ct < JOUR_MIN:
                            sous.append((mn, a, b, c0, ct))
                        pire.append((ct - c0, mn, a, b, c0, ct))
        pire.sort()
        print(f"  {cle} : {len(pire)} paire-master(s) mesuree(s), "
              f"{len(sous)} sous le plancher de {JOUR_MIN:.0f} u")
        for d, mn, a, b, c0, ct in pire[:5]:
            print(f"     le plus resserre : {a}+{b} {mn}  "
                  f"sans geste {c0:.1f} -> avec {ct:.1f}  ({d:+.1f})")
        for mn, a, b, c0, ct in sous[:8]:
            print(f"     !! SOUS LE PLANCHER : {a}+{b} {mn}  "
                  f"{c0:.1f} -> {ct:.1f}")
        anomalies += len(sous)
    return anomalies


def temoin(src):
    """LE TEMOIN. La section 1 rejouee en exigeant un deplacement NUL.

    Elle doit alors crier sur les dix glyphe-masters deplaces de chaque source
    -- cinq glyphes dans les deux masters gras. Si elle se tait, la mesure ne
    mesure plus, et les six premieres sections sont muettes sans que leur zero
    le dise.
    """
    print("\n--- TEMOIN : la section 1 rejouee en exigeant +0,0 ---")
    attendu = sum(sum(1 for mn in MASTERS[c] if any(BM.DEPLACEMENTS[mn]))
                  * len(BM.GLYPHES) for c in src)
    n = section1(src, facteur=0.0)
    ok = n == attendu
    print(f"  temoin : {n} anomalie(s) pour {attendu} attendues — "
          f"{'il sait echouer' if ok else 'IL NE MORD PAS'}")
    return 0 if ok else 1


if __name__ == "__main__":
    # UNE SOURCE ABSENTE EST UN NON MESURE, code 2, jamais un signalement.
    # Jusqu'au soixante-septieme tour, le chargement levait une trace Python
    # et le script sortait a 1, ce qui se lisait comme un defaut du dessin.
    # Point ouvert 31.
    absentes = [p for c in ("roman", "italic") for p in (AMONT[c], TEMOIN[c])
                if not os.path.exists(p)]
    if absentes:
        for p in absentes:
            print(f"NON MESURE : source absente, {p}")
        sys.exit(2)
    src = _charger()
    total = 0
    for f in (section1, section2, section3, section4, section5, section6, section7):
        total += f(src)
    print(f"\nTOTAL : {total} anomalie(s).")
    total += temoin(src)
    sys.exit(1 if total else 0)
