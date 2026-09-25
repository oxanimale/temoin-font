#!/usr/bin/env python3
"""Preuve du crenage servi : ce que HarfBuzz applique sur le binaire.

Point ouvert 43. Tout le vingt-troisieme tour compose la table de crenage de la
*source*, lue par `approches.composer` : `dessin.py` ne shape pas. Rien ne disait
que la table ecrite dans le `.glyphs` produit le meme GPOS apres compilation, ni
que HarfBuzz applique les paires de groupes comme la mesure les lit, ni que le
sous-ensemblage les laisse passer. Ce controle ne lit aucune source pour
conclure : il shape le TTF sous-ensemble, celui dont le WOFF2 servi est le
jumeau, et compare a ce que la table annonce.

Quatre sections, sur les quatre points d'axe, pour les deux binaires.

  1. La chasse du F. L'avance que HarfBuzz rend doit valoir la chasse ecrite
     dans le master, et l'ecart au binaire amont doit valoir APPROCHE_F.
  2. Le crenage r+n, valeur totale +20, plus r+m qui partage la paire de
     groupes. C'est la survie des groupes au sous-ensemblage.
  3. Les correctifs du F, un par un, contre la valeur ecrite dans la source.
  4. Le garde-fou sur les 71 voisins du F : aucune paire ne doit etre plus
     serree que dans Atkinson. C'est le controle du vingt-troisieme tour,
     transpose du dessin au binaire.

Le temoin est le binaire amont d'Atkinson, mesure par le meme code : il porte le
F sans approche et r+n a +10, donc un controle qui sait signaler doit y rendre
des ecarts partout ou il rend zero sur Temoin. Il agit bien sur ce que le
controle mesure — le binaire shape — et non sur ce qui l'a produit, piege tombe
au vingt-troisieme tour ou le premier temoin de `check_approches.py` retirait une
entree d'une table qui n'est lue qu'a l'ecriture, et annoncait lui-meme qu'il ne
savait pas signaler.

Usage :
    python3 shape_check_kern.py [TTF romain] [TTF italique]
    TEMOIN_BUILD=/tmp/bN python3 shape_check_kern.py
    python3 shape_check_kern.py --temoin     # rejoue tout sur Atkinson
"""

import os
import sys

import uharfbuzz as hb
from fontTools.ttLib import TTFont

import approches as A
import dessin as D

ICI = os.path.dirname(os.path.abspath(__file__))
BUILD = os.environ.get("TEMOIN_BUILD", "/tmp/build-temoin")
AMONT = "/tmp/ahn/fonts/variable"

#: Les glyphes temoins qui servent a retrouver le point d'axe d'un master.
#: Trois, et aucun n'est touche par le projet : le F l'est par l'approche, et
#: c'est justement ce qu'on veut mesurer. Un seul glyphe ne suffirait pas — deux
#: masters peuvent partager une chasse sur une lettre etroite.
TEMOINS_AXE = ("n", "o", "H")

#: Le voisinage du F fait foi, et il en compte 71. Le premier jet de
#: `CORRECTIFS_F` en testait 36 et oubliait les capitales : F+J n'y figurait pas.
#: L'ESPACE MOT EST DEDANS DEPUIS LE QUARANTE-TROISIEME TOUR, et c'est la seule
#: paire de cette liste dont un membre n'a pas d'encre. Sans elle, le reglage
#: F+espace du point 76 serait ECRIT ET JAMAIS PROUVE sur le binaire servi : la
#: section 4 est le seul controle du projet qui relise le crenage tel que
#: HarfBuzz le compose, et aucune table de paires ne peut porter une paire sans
#: encre -- `approches.profil` y rend `None` et `couloir_plein` y leve.
#:
#: Elle ne retombe pas dans le piege du trente-troisieme tour, ou HarfBuzz
#: SYNTHETISAIT une avance plausible pour une espace absente du cmap et rendait
#: un nombre juste sur un glyphe qui manque : `paires_a_tester` borne la liste a
#: ce que le cmap du binaire mesure sert reellement, et U+0020 y est des deux
#: cotes. La normalisation des espaces est un fait de `canvas.measureText`,
#: dans le navigateur, et non du shaping.
VOISINS_F = (list("abcdefghijklmnopqrstuvwxyz")
             + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
             + list("àâäçéèêëîïôöùûü")
             + list(".,;:!?'\"()-«»…")
             + [" "])

#: Six mots reels, dont les paires consecutives entrent dans la section 4 a cote
#: des voisins du F. Ils portent ce que le projet a touche : le r+n crene, les
#: coupes du l, du s, du t et du f, la cedille, l'accent aigu.
#: **Les quatre derniers portent les trois reglages du cinquantieme tour**, et
#: sans eux aucun controle ne relisait leurs valeurs sur le binaire : `VOISINS_F`
#: porte l'apostrophe DROITE U+0027, jamais la courbe U+2019 que les gabarits
#: emploient seule, et aucun mot ne composait `Ly`. Un controle qui prouve le
#: servi peut ne tester qu'une fraction de ce qui est servi, et une valeur
#: ecrite sans etre relue n'est pas une valeur prouvee.
MOTS = ("France", "information", "protocole", "souffrances",
        "immunodeficience", "reglementaire", "francais", "elevage",
        "l’île", "d’îles", "l’animal", "Lyon")

#: Des paires crenees par groupe dans Atkinson et qu'aucune table du projet ne
#: touche. Elles doivent survivre au sous-ensemblage a l'identique : c'est la
#: seule facon de distinguer "les groupes passent" de "il n'y a plus de kern".
PAIRES_INTOUCHEES = (("A", "V"), ("A", "T"), ("T", "o"), ("Y", "a"),
                     ("P", ","), ("V", "a"), ("r", "."), ("o", "v"))


# --------------------------------------------------------------- outillage

def paires_a_tester(cm):
    """Les paires de la section 4 : les voisins du F, plus celles des mots.

    Dedoublonnees, et bornees a ce que le sous-ensemble sert reellement — une
    paire dont un membre manque au cmap rendrait du .notdef, donc une avance qui
    ne veut rien dire.
    """
    servis = set(cm.values())
    out = []
    vus = set()
    for v in VOISINS_F:
        out.append(("F", v))
    for mot in MOTS:
        for i in range(len(mot) - 1):
            out.append((mot[i], mot[i + 1]))
    fin = []
    for a_, b_ in out:
        if (a_, b_) in vus:
            continue
        vus.add((a_, b_))
        if a_ in servis and b_ in servis:
            fin.append((a_, b_))
    return fin


def charger(chemin):
    blob = hb.Blob.from_file_path(chemin)
    face = hb.Face(blob)
    return hb.Font(face)


def cmap_inverse(chemin):
    """nom de glyphe -> caractere, lu sur le binaire mesure.

    Sans elle il faudrait ecrire les caracteres a la main a cote des noms de
    `CORRECTIFS_F`, donc entretenir deux listes qui peuvent diverger.
    """
    cm = TTFont(chemin).getBestCmap()
    out = {}
    for code, nom in cm.items():
        out.setdefault(nom, chr(code))
    return out


def avance(font, texte):
    """L'avance totale d'un texte shape, en unites de police.

    Rend None si le shaping ne produit pas un glyphe par caractere : une
    substitution s'est glissee dans la mesure, et un crenage lu sur une ligature
    ne serait pas celui de la paire.
    """
    buf = hb.Buffer()
    buf.add_str(texte)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    if len(buf.glyph_infos) != len(texte):
        return None
    if any(i.codepoint == 0 for i in buf.glyph_infos):
        return None
    return sum(p.x_advance for p in buf.glyph_positions)


def crenage(font, a, b):
    """Ce que le binaire applique entre a et b : l'avance du couple moins les deux.

    Mesure du resultat, pas de la table. Une valeur juste dans le GPOS mais
    inatteignable par le shaper — mauvaise couverture de lookup, groupe perdu au
    sous-ensemblage — rendrait ici zero, et c'est exactement ce qu'on cherche.
    """
    ab, sa, sb = avance(font, a + b), avance(font, a), avance(font, b)
    if ab is None or sa is None or sb is None:
        return None
    return ab - sa - sb


def points_axe(src, font, chemin, hors=None):
    """La coordonnee wght de chaque master, calculee sur le mapping puis verifiee.

    Le nom de master ne dit pas ou il tombe sur l'axe utilisateur : la source
    porte des coordonnees de dessin (60, 94, 158, 170) et le binaire un axe wght
    de 200 a 800. Le pont est le parametre `Axis Mappings` de la source, et il
    reserve une surprise : ses sept entrees sont celles des *instances*, et le
    master Bold est a 158 quand l'instance Bold est a 146. Le master Bold tombe
    donc a wght 750, entre deux entrees, et non a 700.

    Un premier jet balayait l'axe et gardait le premier point ou les chasses
    temoins tombaient. Il rendait 397 et 747 : les chasses etant arrondies a
    l'entier, elles sont identiques sur tout un plateau de points, et le premier
    du plateau n'est pas le master. Trois correctifs du F sortaient alors a une
    unite de la table — un ecart vrai, mesure a cote du master. **Un controle qui
    cherche son point de mesure par ce que la mesure rend le trouve sur un
    plateau**, et un plateau n'a pas de raison d'etre centre sur la valeur juste.

    Le calcul est donc explicite et la verification suit, comme le projet le fait
    pour ses localisateurs : les trois glyphes temoins doivent rendre exactement
    les chasses du master au point calcule, sans quoi le master est rendu None et
    la section se declare non faite.

    UN MASTER HORS DE L'AXE DU BINAIRE N'EST PAS UN MASTER INTROUVABLE. Depuis
    le soixante-et-onzieme tour, le servi s'arrete a 400 (point ouvert 3) : le
    master ExtraLight, a 200, n'y existe plus. HarfBuzz ramene alors 200 a 400
    en silence, les chasses ne tombent pas, et le master sortait "introuvable",
    compte comme une anomalie. Il est desormais rendu None, donc ecarte de
    toutes les sections comme avant, et son nom va dans `hors` : l'appelant le
    dit en NOTE. Le binaire publie, 200-800, se controle en passant ses TTF en
    argument.
    """
    from fontTools.ttLib import TTFont
    axe = TTFont(chemin)["fvar"].axes[0]
    mapping = src.customParameters["Axis Mappings"]["wght"]
    pts = sorted((float(dessin), float(user)) for user, dessin in mapping.items())

    def vers_wght(x):
        for i in range(len(pts) - 1):
            (d0, u0), (d1, u1) = pts[i], pts[i + 1]
            if d0 <= x <= d1:
                if d1 == d0:
                    return u0
                return u0 + (u1 - u0) * (x - d0) / (d1 - d0)
        return pts[0][1] if x < pts[0][0] else pts[-1][1]

    cm = cmap_inverse(chemin)
    car = {nom: cm.get(nom) for nom in TEMOINS_AXE}
    out = {}
    for m in src.masters:
        w = vers_wght(float(m.axes[0]))
        if not axe.minValue <= w <= axe.maxValue:
            out[m.name] = None
            if hors is not None:
                hors.add(m.name)
            continue
        chasses = {}
        for nom in TEMOINS_AXE:
            for l in src.glyphs[nom].layers:
                if l.layerId == m.id:
                    chasses[nom] = round(float(l.width))
        font.set_variations({"wght": w})
        if all(avance(font, car[g]) == chasses[g] for g in TEMOINS_AXE):
            out[m.name] = w
        else:
            out[m.name] = None
    return out


def masters_de(src):
    return [m.name for m in src.masters]


def chasse_source(src, nom_glyphe, nom_master):
    for m in src.masters:
        if m.name == nom_master:
            for l in src.glyphs[nom_glyphe].layers:
                if l.layerId == m.id:
                    return float(l.width)
    return None


def kern_source(src, nom_glyphe_a, nom_glyphe_b, nom_master):
    for m in src.masters:
        if m.name == nom_master:
            return A.kern(src, m.id, nom_glyphe_a, nom_glyphe_b)
    return None


# ---------------------------------------------------------------- sections

def parcours(etiquette, chemin, chemin_amont, src, anomalies, notes):
    print(f"\n{'='*70}\n=== {etiquette} : {os.path.basename(chemin)}")
    font = charger(chemin)
    amont = charger(chemin_amont)
    cm = cmap_inverse(chemin)
    cle = A.source_de(src)
    # Depuis le vingt-quatrieme tour, aucune chasse n'est touchee : l'approche du
    # F est retiree et le trou de sa barre mediane se referme paire par paire.
    # La section 1 verifie donc que la chasse du F est CELLE D'ATKINSON, et elle
    # reste utile : c'est le seul controle qui le dirait si une approche revenait
    # par accident.
    attendue = 0.0

    hors = set()
    pts = points_axe(src, font, chemin, hors)
    pts_amont = points_axe(src, amont, chemin_amont) if amont else {}
    for nom_m, w in pts.items():
        if nom_m in hors:
            notes.append(f"{etiquette} {nom_m} : hors de l'axe du binaire lu, "
                         f"non mesure ici")
        elif w is None:
            anomalies.append(f"{etiquette} {nom_m} : point d'axe introuvable, "
                             f"le binaire ne reproduit pas les chasses du master")
    print("  points d'axe deduits :",
          ", ".join(f"{k} = wght {v}" for k, v in pts.items()))

    # -- 1. la chasse du F
    print(f"\n  --- 1. la chasse du F, ecart attendu {attendue:+.0f} u")
    print(f"  {'master':<20} {'source':>8} {'binaire':>8} {'Atkinson':>9} "
          f"{'ecart':>8}")
    for nom_m, w in pts.items():
        if w is None:
            continue
        font.set_variations({"wght": float(w)})
        b = avance(font, "F")
        s = chasse_source(src, "F", nom_m)
        wa = pts_amont.get(nom_m)
        a_ = None
        if wa:
            amont.set_variations({"wght": float(wa)})
            a_ = avance(amont, "F")
        ecart = (b - a_) if (b is not None and a_ is not None) else None
        print(f"  {nom_m:<20} {s:>8.0f} {b:>8} "
              f"{a_ if a_ is not None else '?':>9} "
              f"{ecart if ecart is not None else '?':>8}")
        if b != round(s):
            anomalies.append(f"{etiquette} {nom_m} : chasse du F {b} servie "
                             f"pour {s:.0f} ecrits dans la source")
        if ecart is not None and abs(ecart - attendue) > 0.5:
            anomalies.append(f"{etiquette} {nom_m} : ecart du F a Atkinson "
                             f"{ecart}, attendu {attendue:+.0f}")

    # -- 2. le crenage des paires, et la survie des groupes
    print(f"\n  --- 2. les paires de KERN_PAIRES, et la paire de groupes")
    for (ga, gb), valeur in A.KERN_PAIRES.items():
        ca, cb = cm.get(ga), cm.get(gb)
        print(f"  {ga}+{gb} attendu {valeur:+.0f} u (valeur totale)")
        print(f"  {'master':<20} {'servi':>8} {'Atkinson':>9}   "
              f"{'meme groupe':<14}{'servi':>8}")
        for nom_m, w in pts.items():
            if w is None:
                continue
            font.set_variations({"wght": float(w)})
            k = crenage(font, ca, cb)
            ka = None
            wa = pts_amont.get(nom_m)
            if wa:
                amont.set_variations({"wght": float(wa)})
                ka = crenage(amont, ca, cb)
            # le m partage le groupe droit du n : @MMK_R_n
            km = crenage(font, ca, cm.get("m"))
            print(f"  {nom_m:<20} {k if k is not None else '?':>8} "
                  f"{ka if ka is not None else '?':>9}   "
                  f"{'r+m':<14}{km if km is not None else '?':>8}")
            if k is None or abs(k - valeur) > 0.5:
                anomalies.append(f"{etiquette} {nom_m} : {ga}+{gb} servi {k}, "
                                 f"table {valeur:+.0f}")
            if km is None or abs(km - valeur) > 0.5:
                anomalies.append(f"{etiquette} {nom_m} : {ga}+m servi {km}, "
                                 f"la paire de groupes n'a pas survecu")

    print(f"\n  --- 2b. huit paires de groupes qu'aucune table du projet ne touche")
    ecarts = []
    for a_, b_ in PAIRES_INTOUCHEES:
        for nom_m, w in pts.items():
            wa = pts_amont.get(nom_m)
            if w is None or not wa:
                continue
            font.set_variations({"wght": float(w)})
            amont.set_variations({"wght": float(wa)})
            k, ka = crenage(font, a_, b_), crenage(amont, a_, b_)
            if k is None or ka is None:
                continue
            if abs(k - ka) > 0.5:
                ecarts.append(f"{a_}+{b_} {nom_m} {k} pour {ka}")
    print(f"  {len(ecarts)} ecart(s) au binaire amont : {ecarts or 'aucun'}")
    anomalies.extend(f"{etiquette} : paire intouchee modifiee, {e}"
                     for e in ecarts)

    # -- 3. la table de paires du F, une par une
    print(f"\n  --- 3. les paires du F, servi contre ecrit dans la source")
    for nom_m, w in pts.items():
        if w is None:
            continue
        font.set_variations({"wght": float(w)})
        tab = A.PAIRES_F.get(nom_m, {})
        mesurees, hors, ecarts = 0, 0, []
        for voisin in sorted(tab):
            car = cm.get(voisin)
            if car is None:
                hors += 1
                continue
            servi = crenage(font, "F", car)
            ecrit = kern_source(src, "F", voisin, nom_m)
            mesurees += 1
            if servi is None or abs(servi - ecrit) > 0.5:
                ecarts.append(f"F+{voisin} {servi}/{ecrit:.0f}")
                anomalies.append(f"{etiquette} {nom_m} : F+{voisin} servi "
                                 f"{servi}, ecrit {ecrit}")
        print(f"  {nom_m:<20} {len(tab):>3} dans la table, {mesurees:>3} servies,"
              f" {hors:>3} hors du sous-ensemble, {len(ecarts)} ecart(s)"
              + (f" : {', '.join(ecarts[:6])}" if ecarts else ""))
        if hors:
            notes.append(f"{etiquette} {nom_m} : {hors} paire(s) de la table "
                         f"hors du sous-ensemble web, non mesurees ici")

    # -- 3b. la table des huit bouts coupes, une par une
    #
    # LA SECTION 5 NE SUFFIT PAS POUR CETTE TABLE, ET C'EST UNE QUESTION DE
    # COUVERTURE. Elle teste 138 paires, choisies pour surveiller le F et les
    # paires intouchees ; la table des bouts en porte 647. Sans cette
    # section-ci, la plupart des valeurs ecrites au trente-et-unieme tour ne
    # seraient jamais relues sur le binaire, et rien ne le dirait. Meme forme
    # que la section 3 pour le F, meme raison, et elle imprime comme elle ce
    # que le sous-ensemble web laisse dehors.
    print(f"\n  --- 3b. les paires des huit bouts coupes, servi contre ecrit")
    inv = {v: k for k, v in cm.items()}
    for nom_m, w in pts.items():
        if w is None:
            continue
        font.set_variations({"wght": float(w)})
        tab = A.PAIRES_BOUTS.get(nom_m, ())
        mesurees, hors, ecarts = 0, 0, []
        for a, b, _ in tab:
            ca, cb = cm.get(a), cm.get(b)
            if ca is None or cb is None:
                hors += 1
                continue
            servi = crenage(font, ca, cb)
            ecrit = kern_source(src, a, b, nom_m)
            mesurees += 1
            if servi is None or abs(servi - ecrit) > 0.5:
                ecarts.append(f"{a}+{b} {servi}/{ecrit:.0f}")
                anomalies.append(f"{etiquette} {nom_m} : {a}+{b} servi "
                                 f"{servi}, ecrit {ecrit}")
        print(f"  {nom_m:<20} {len(tab):>4} dans la table, {mesurees:>4} "
              f"servies, {hors:>3} hors du sous-ensemble, "
              f"{len(ecarts)} ecart(s)"
              + (f" : {', '.join(ecarts[:6])}" if ecarts else ""))
        if hors:
            notes.append(f"{etiquette} {nom_m} : {hors} paire(s) de la table "
                         "des bouts hors du sous-ensemble web, non mesurees")

    # -- 4. la composition servie contre la composition de la source
    print(f"\n  --- 4. ce que le binaire compose contre ce que la source ecrit")
    print("  Un premier jet comparait l'avance de F+voisin a celle d'Atkinson et")
    print("  comptait 75 paires 'sous Atkinson' par master. Il mesurait la")
    print("  mauvaise grandeur : l'approche du F est faite pour raccourcir cette")
    print("  avance, et une avance plus courte ne rapproche pas les traits — le F")
    print("  a un trou de 108 unites a hauteur de barre mediane, et c'est lui que")
    print("  l'approche referme. Le garde-fou du couloir se mesure sur la")
    print("  geometrie, il est dans check_approches.py et il rend zero. Ce que ce")
    print("  controle-ci doit prouver, c'est que le binaire compose comme la")
    print("  source : le garde-fou vaut alors pour le servi, par transitivite.")
    for nom_m, w in pts.items():
        if w is None:
            continue
        font.set_variations({"wght": w})
        ecarts, testees, pire = [], 0, 0.0
        for a_c, b_c in paires_a_tester(cm):
            servi = avance(font, a_c + b_c)
            if servi is None:
                continue
            na = D.nom_glyphe(src, a_c)
            nb = D.nom_glyphe(src, b_c)
            if na is None or nb is None:
                continue
            attendu = (chasse_source(src, na, nom_m)
                       + chasse_source(src, nb, nom_m)
                       + kern_source(src, na, nb, nom_m))
            testees += 1
            d = servi - attendu
            if abs(d) > 0.5:
                ecarts.append(f"{a_c}+{b_c} {servi} pour {attendu:.0f}")
                pire = max(pire, abs(d))
        print(f"  {nom_m:<20} {testees:>4} paire(s) mesuree(s), "
              f"{len(ecarts)} ecart(s)"
              + (f", au pire {pire:.1f} u : {', '.join(ecarts[:6])}"
                 if ecarts else ""))
        anomalies.extend(f"{etiquette} {nom_m} : {e} (servi/source)"
                         for e in ecarts)

    section5(etiquette, font, amont, pts, pts_amont, cm, src, cle, anomalies)
    section6(etiquette, font, pts, src, chemin, anomalies)


def section6(etiquette, font, pts, src, chemin, anomalies):
    """L'espace fine insecable U+202F, servie et a la bonne chasse.

    Trente-troisieme tour, point ouvert 32. La police de base ne porte pas
    U+202F et les gabarits employaient U+00A0 a sa place, qui a exactement la
    chasse de l'espace mot. Le correctif ne dessine rien : il donne a U+202F la
    chasse de `thinspace` U+2009, deja presente et deja servie.

    Une espace est le glyphe qu'aucun controle du projet ne voit. Elle n'a pas
    de contour, donc `check3`, `check5` et les planches n'ont rien a mesurer
    dessus ; elle n'a pas de crenage, donc les sections 2 a 5 l'ignorent. Une
    chasse fausse, ou un glyphe perdu au sous-ensemblage, passerait sous les sept
    controles sans un mot. D'ou une section a elle.

    Quatre questions, dans les quatre masters :
      - U+202F est-elle dans le `cmap` du binaire ?
      - son avance vaut-elle exactement U+2009, sa reference de dessin ?
      - vaut-elle ce que la source ecrit pour `narrownbspace` ?
      - differe-t-elle de U+00A0 ? Sans quoi le correctif ne corrige rien.

    **La premiere question se lit dans le `cmap`, et surtout pas par shaping.**
    Premier jet de cette section, ecrit et tombe dans l'heure : il posait la
    question au shaper, comme les cinq sections precedentes le font pour le
    crenage, et le temoin est reste a 1610 anomalies au lieu de monter. Atkinson
    ne porte pas U+202F, et la section rendait pourtant 130 unites dans les huit
    masters. **HarfBuzz synthetise les espaces absentes** : pour un code point
    de categorie Zs sans glyphe, il fabrique une avance plausible au lieu de
    rendre du .notdef. Une mesure par shaping ne distingue donc pas une espace
    presente d'une espace inventee par le moteur, et le controle aurait declare
    servi un glyphe qui n'existait pas.

    C'est le pendant exact du piege du WOFF2 : la ou HarfBuzz rend du .notdef en
    silence sur un format qu'il ne decode pas, il rend ici une valeur juste sur
    un glyphe qui manque. Les deux fois, la mesure sort un nombre.

    Le temoin est naturel : Atkinson ne porte pas U+202F, donc `--temoin` fait
    echouer la premiere question dans les huit masters. C'est le seul temoin du
    projet qui n'a rien coute a fabriquer \u2014 encore fallait-il poser la question
    a qui connait la reponse.
    """
    print(f"\n  --- 6. l'espace fine insecable U+202F, servie contre thinspace")
    print(f"  {'master':<20} {'cmap':>7} {'U+202F':>8} {'U+2009':>8} "
          f"{'source':>8} {'U+00A0':>8}")
    dans_cmap = 0x202F in TTFont(chemin).getBestCmap()
    for nom_m, w in pts.items():
        if w is None:
            continue
        font.set_variations({"wght": float(w)})
        fine = avance(font, "\u202f")
        thin = avance(font, "\u2009")
        nbsp = avance(font, "\u00a0")
        ecrite = chasse_source(src, "narrownbspace", nom_m)
        aff = lambda v: f"{v:.0f}" if v is not None else "ABSENT"
        print(f"  {nom_m:<20} {'oui' if dans_cmap else 'ABSENT':>7} "
              f"{aff(fine):>8} {aff(thin):>8} {aff(ecrite):>8} {aff(nbsp):>8}")
        if not dans_cmap:
            anomalies.append(f"{etiquette} {nom_m} : U+202F absente du cmap du "
                             f"binaire servi (le shaper en rend pourtant "
                             f"{aff(fine)} u, qu'il fabrique)")
            continue
        if fine is None:
            anomalies.append(f"{etiquette} {nom_m} : U+202F dans le cmap mais "
                             f"rendue en .notdef par le shaper")
            continue
        if thin is not None and abs(fine - thin) > 0.5:
            anomalies.append(f"{etiquette} {nom_m} : U+202F a {fine:.1f} u "
                             f"quand U+2009 en fait {thin:.1f}, alors qu'elle "
                             f"en est la copie")
        if ecrite is not None and abs(fine - ecrite) > 0.5:
            anomalies.append(f"{etiquette} {nom_m} : U+202F servie a {fine:.1f} "
                             f"u, ecrite a {ecrite:.1f} dans la source")
        if nbsp is not None and abs(fine - nbsp) < 0.5:
            anomalies.append(f"{etiquette} {nom_m} : U+202F et U+00A0 ont la "
                             f"meme chasse, {fine:.1f} u : le correctif ne "
                             f"corrige rien")


def cle_droite(src, nom_glyphe):
    """La cle de crenage du membre droit d'une paire : son groupe, sinon lui-meme."""
    if nom_glyphe is None or src.glyphs[nom_glyphe] is None:
        return None
    g = src.glyphs[nom_glyphe].leftKerningGroup
    return "@MMK_R_" + g if g else nom_glyphe


def section5(etiquette, font, amont, pts, pts_amont, cm, src, cle,
             anomalies):
    """L'ecart des deux binaires contre ce que les tables prevoient, aux deux sens.

    **La section qui manquait, et le tour l'a paye.** Les quatre precedentes
    comparent le binaire a la source : elles sont muettes quand les deux sont
    coherents dans l'erreur. Le garde-fou de `check_approches`, lui, ne teste que
    le sens serre. Entre les deux, une paire 100 unites TROP LARGE passait sous
    les sept controles du projet, et c'est une mesure de largeur dans un
    navigateur qui l'a trouvee : `comma` et `period` partagent le groupe
    @MMK_R_period, la boucle des correctifs ecrivait deux fois sur la meme cle et
    la seconde passe relisait la premiere.

    L'attendu n'est pas un seuil, c'est une addition : pour une paire du F,
    l'ecart d'avance doit valoir l'approche plus le correctif de cette paire, et
    rien d'autre. Pour toute autre paire il doit valoir zero, sauf celles que
    `KERN_PAIRES` vise, dont l'ecart est la valeur totale moins ce qu'Atkinson
    applique. Une intention ecrite quelque part, une mesure en face.
    """
    print(f"\n  --- 5. les deux binaires, contre ce que les tables prevoient")
    approche = A.APPROCHE_F[cle]
    vises = {}
    for (ga, gb), tot in A.KERN_PAIRES.items():
        ca, cb = cm.get(ga), cm.get(gb)
        if ca and cb:
            vises[(ca, cb)] = tot
            # la paire porte sur les groupes : le m partage celui du n
            for autre in ("m",):
                cc = cm.get(autre)
                if cc:
                    vises[(ca, cc)] = tot
    for nom_m, w in pts.items():
        wa = pts_amont.get(nom_m)
        if w is None or not wa:
            continue
        font.set_variations({"wght": w})
        amont.set_variations({"wght": wa})
        # La table du F est ecrite en exception glyphe-glyphe depuis le
        # vingt-quatrieme tour, donc elle se lit par nom de glyphe et non par
        # cle de groupe. Le detour par `cle_droite` avait ete ajoute quand les
        # correctifs s'ecrivaient sur des groupes, et il serait faux ici : une
        # exception ne touche que sa paire.
        tab = A.PAIRES_F.get(nom_m, {})
        # LES DEUX AUTRES TABLES, ET LEUR ABSENCE A FAIT SIGNALER 20 ECARTS
        # VRAIS SUR UN BINAIRE JUSTE.
        #
        # Cette section n'a longtemps connu que la table du F et `KERN_PAIRES`,
        # donc elle attendait zero partout ailleurs. Le trente-et-unieme tour a
        # ecrit `paires_bouts.py`, 647 paires sur huit masters, et la section a
        # signale `c+e`, `c+o`, `l+e`, `c+i` et `c+a` dans les gras des deux
        # sources : le binaire composait exactement ce que la table demande, et
        # c'est l'ATTENDU qui etait perime. Quatrieme fois qu'un controle de ce
        # projet cesse de couvrir parce que le travail a avance, sans qu'une
        # ligne de son code change.
        #
        # Les trois tables sont disjointes, verifie a chaque passage plus bas :
        # aucune paire n'est ecrite deux fois, donc aucune ne s'ecrase.
        bouts = {(a, b): v for a, b, v in A.PAIRES_BOUTS.get(nom_m, ())}
        pieds = {(a, b): v for a, b, v in A.PAIRES_PIEDS.get(nom_m, ())}
        dbl = set(bouts) & set(pieds)
        dbl |= {(a, b) for (a, b) in bouts if a == "F" and b in tab}
        if dbl:
            anomalies.append(
                f"{etiquette} {nom_m} : {len(dbl)} paire(s) ecrite(s) par deux "
                "tables, donc l'une ecrase l'autre : "
                + ", ".join(f"{a}+{b}" for a, b in sorted(dbl)[:5]))
        ecarts, testees = [], 0
        for a_c, b_c in paires_a_tester(cm):
            t = avance(font, a_c + b_c)
            v = avance(amont, a_c + b_c)
            if t is None or v is None:
                continue
            testees += 1
            attendu = 0.0
            na_g, nb_g = D.nom_glyphe(src, a_c), D.nom_glyphe(src, b_c)
            if (na_g, nb_g) in bouts:
                # Valeurs TOTALES, comme la table du F et pour la meme raison :
                # elles remplacent le crenage d'Atkinson au lieu de s'y ajouter.
                attendu = bouts[(na_g, nb_g)] - (crenage(amont, a_c, b_c) or 0.0)
            elif (na_g, nb_g) in pieds:
                attendu = pieds[(na_g, nb_g)] - (crenage(amont, a_c, b_c) or 0.0)
            elif a_c == "F" and (nb_g in A.RONDES_F
                                 or nb_g in A.DIAGONALES_F
                                 or nb_g == A.GLYPHE_ESPACE
                                 or (nb_g == "i" and nom_m in A.REGLAGE_F_I)):
                # LE REGLAGE DU F, trente-et-unieme tour. L'attendu est une
                # ADDITION D'INTENTIONS et non une lecture de la source : la
                # valeur servie doit valoir la table du F, plus le delta que
                # Nicolas a choisi en navigateur, moins ce qu'Atkinson applique.
                #
                # Sans cette branche la section rendait 88 ecarts vrais sur un
                # binaire juste, exactement comme elle en avait rendu 20 sur la
                # table des bouts quelques heures plus tot. **Cinquieme fois
                # qu'un controle de ce projet cesse de couvrir parce que le
                # travail a avance**, et la seconde dans le meme tour : un
                # controle qui additionne des intentions doit connaitre toutes
                # les tables, et une table nouvelle se declare ici.
                base = tab.get(nb_g)
                if base is None:
                    base = crenage(amont, a_c, b_c) or 0.0
                # TROIS REGLAGES, TROIS DELTAS. Le troisieme est F+espace,
                # quarante-troisieme tour : plat sur les huit masters, quand
                # celui du i varie parce que le plancher de jour le borne dans
                # les gras. Une espace n'a pas de jour a garder.
                # QUATRE REGLAGES DEPUIS LE CINQUANTE-QUATRIEME TOUR. Le
                # quatrieme est F+A et ses trois accentuees, a +30, et il est
                # entre ici AU MEME GESTE qui l'a ecrit dans `approches` : la
                # section a rendu 8 ecarts vrais sur un binaire juste avant
                # cette ligne, sixieme fois qu'un controle de ce projet cesse
                # de couvrir parce que le travail a avance.
                if nb_g in A.RONDES_F:
                    delta = A.REGLAGE_F_RONDES
                elif nb_g in A.DIAGONALES_F:
                    delta = A.REGLAGE_F_A
                elif nb_g == A.GLYPHE_ESPACE:
                    delta = A.REGLAGE_F_ESPACE
                else:
                    delta = A.REGLAGE_F_I[nom_m]
                attendu = (base + delta) - (crenage(amont, a_c, b_c) or 0.0)
            elif a_c == "F":
                # La table porte des valeurs TOTALES qui remplacent le crenage
                # d'Atkinson : l'ecart d'avance vaut donc la valeur ecrite moins
                # ce qu'Atkinson applique. Le premier jet lisait la valeur seule
                # et signalait 136 ecarts, tous vrais — c'est ce qui a montre que
                # la table portait des ajustements la ou il fallait des totaux.
                nb = D.nom_glyphe(src, b_c)
                if nb in tab:
                    attendu = tab[nb] - (crenage(amont, a_c, b_c) or 0.0)
            elif (na_g, nb_g) == ("l", "quoteright"):
                # LES TROIS REGLAGES DU CINQUANTIEME TOUR. Ils s'AJOUTENT au
                # crenage d'Atkinson au lieu de le remplacer, donc l'ecart
                # d'avance entre les deux binaires vaut exactement le reglage,
                # sans qu'il faille lire quoi que ce soit dans l'amont. C'est la
                # septieme fois qu'une table neuve doit se declarer ici : un
                # controle qui additionne des intentions doit connaitre tout ce
                # que le projet ecrit.
                attendu = A.REGLAGE_L_APOSTROPHE
            elif na_g == "quoteright" and nb_g in A.NOMS_I_ACCENTUE:
                attendu = A.REGLAGE_APOSTROPHE_I_ACCENTUE
            elif na_g == A.CIBLE_L_DIAGONALES[0] and nb_g in (
                    "y", "v", "w", "yacute", "ydieresis"):
                # Ecrit sur la cle de GROUPE : les cinq glyphes du groupe
                # recoivent la meme valeur, et la section doit les attendre
                # tous les cinq, pas seulement celui que la constante nomme.
                attendu = A.REGLAGE_L_DIAGONALES
            elif (a_c, b_c) in vises:
                attendu = vises[(a_c, b_c)] - crenage(amont, a_c, b_c)
            d = (t - v) - attendu
            if abs(d) > 0.5:
                ecarts.append(f"{a_c}+{b_c} {t - v:+.0f} pour {attendu:+.0f}")
        print(f"  {nom_m:<20} {testees:>4} paire(s), {len(ecarts)} ecart(s)"
              + (f" : {', '.join(ecarts[:8])}" if ecarts else ""))
        anomalies.extend(f"{etiquette} {nom_m} : {e} (Temoin-Atkinson/attendu)"
                         for e in ecarts)


def main():
    mode_temoin = "--temoin" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rom = args[0] if args else BUILD + "/Temoin-sub.ttf"
    ital = args[1] if len(args) > 1 else BUILD + "/Temoin-Italic-sub.ttf"
    am_rom = AMONT + "/AtkinsonHyperlegibleNext[wght].ttf"
    am_ital = AMONT + "/AtkinsonHyperlegibleNext-Italic[wght].ttf"

    if mode_temoin:
        # Le temoin remplace le binaire mesure par celui d'Atkinson, en gardant
        # tout le reste : les memes tables, le meme code, le meme amont en
        # reference. Un controle qui sait signaler doit alors trouver l'approche
        # du F absente, r+n a +10 et les correctifs a zero.
        rom, ital = am_rom, am_ital
        print("TEMOIN : le binaire mesure est celui d'Atkinson. Toutes les "
              "anomalies attendues ci-dessous sont la preuve que le controle "
              "sait signaler.")

    manquants = [p for p in (rom, ital, am_rom, am_ital)
                 if not os.path.exists(p)]
    if manquants:
        print("SANS SOURCE : " + ", ".join(manquants))
        print("\nVerdict : NON FAIT. Un controle qui n'a pas pu lire ce qu'il "
              "mesure ne conclut pas.")
        return 2

    import glyphsLib
    src_rom = glyphsLib.load(open(os.path.join(ICI, "Temoin.glyphs")))
    src_ital = glyphsLib.load(open(os.path.join(ICI, "Temoin-Italic.glyphs")))

    anomalies, notes = [], []
    parcours("roman", rom, am_rom, src_rom, anomalies, notes)
    parcours("italic", ital, am_ital, src_ital, anomalies, notes)

    print(f"\n{'='*70}")
    for n in notes:
        print("NOTE ", n)
    if mode_temoin:
        print(f"\nTEMOIN : {len(anomalies)} anomalie(s) rendue(s). "
              + ("Le controle sait signaler."
                 if anomalies else
                 "AUCUNE : le controle ne sait pas signaler, il ne prouve rien."))
        return 0 if anomalies else 1
    if anomalies:
        print(f"\n{len(anomalies)} anomalie(s) :")
        for a_ in anomalies:
            print("   ", a_)
        return 1
    print("\nAucune anomalie : le crenage servi est celui que la table ecrit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
