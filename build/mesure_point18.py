#!/usr/bin/env python3
"""Point ouvert 18 : les approches du titrage, et d'abord sa VALIDITE.

CE QUE LE POINT ANNONCE, et il a ete ecrit au huitieme tour : "la coupe
etendue avec le coin exterieur resserre la boite du glyphe jusqu'a 39 unites de
chaque cote sans toucher la chasse, donc les approches du titrage sont a
refaire". La mesure d'origine porte sur TREIZE lettres et QUATRE masters, a une
epoque ou le titrage etait un registre separe -- un second dessin, avec ses
propres approches a regler.

CE QUI A CHANGE DEPUIS. Le quarantieme tour a FUSIONNE le titrage dans le
dessin : il n'y a plus qu'un dessin par glyphe, et le resserrement de boite,
s'il existe, vit dans le dessin SERVI. Les trois tables de paires ont ete
regenerees sur l'etat ecrit depuis. Le point 18 peut donc decrire :

    un chantier entier, si la boite se resserre et que rien ne le compense ;
    un chantier reduit, si les tables en referment deja une partie ;
    plus rien du tout, si la fusion l'a regle en chemin.

Un point ouvert peut se tromper sur sa propre etendue -- le projet en a corrige
quarante-quatre, dont le point 100 au tour precedent. La mesure passe avant le
dessin.

CE QUE CE SCRIPT MESURE, volet `--boite`. Pour chaque nom du perimetre arrete,
sur les huit masters des deux sources, l'effet du SEUL geste de titrage sur les
deux approches du glyphe :

    approche gauche  = xMin
    approche droite  = chasse - xMax

en opposant `mesure_titrage.etat_avant_fusion` a `mesure_titrage.etat_fusionne`
-- les deux etats ne different que par une application du geste, ce qui est la
seule facon d'isoler le titrage depuis que la source les porte ensemble. Une
valeur POSITIVE est une approche qui s'OUVRE, donc un blanc qui grandit ; c'est
le sens que le point 18 annonce.

CE QU'IL NE MESURE PAS. Le blanc reellement percu entre deux lettres, qui
depend du voisin et du crenage. Le volet `--tables` dit seulement si les trois
tables de paires REGARDENT les glyphes concernes : un glyphe absent de leurs
univers ne peut etre referme par aucune d'elles, et son zero serait une cecite,
comme le `9` au quarante-quatrieme tour et les huit operateurs au
cinquante-troisieme.

    python3 mesure_point18.py --boite
    python3 mesure_point18.py --boite --seuil 5
    python3 mesure_point18.py --tables
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dessin as D                                            # noqa: E402
import lot4 as Q                                              # noqa: E402
import mesure_titrage as MT                                   # noqa: E402

#: Au-dela de quoi un ecart d'approche est un fait et non du bruit d'arrondi.
#: Meme valeur que `MT.SEUIL_BRUIT`, et elle est LUE chez lui : deux seuils
#: recopies se corrigent dans un seul fichier, piege consigne au
#: cinquante-cinquieme tour.
SEUIL = MT.SEUIL_BRUIT

#: Ce que le point 18 annonce, pour que la mesure puisse le contredire.
ANNONCE = 39.0

#: Au-dela de quoi une boite elargie fait de cette lettre une cible. Trois
#: unites font six fois le bruit d'arrondi du projet. IL VIT ICI et
#: `inventaire_contacts` le LIT : un seuil recopie dans deux fichiers se
#: corrige dans un seul, et les deux filtreraient alors des univers de cibles
#: differents sans qu'aucun message ne le dise.
SEUIL_BOITE = 3.0


def approches(font, master, nom):
    """(gauche, droite, chasse) du glyphe, contours resolus, ou None.

    La gauche est `xMin`, la droite `chasse - xMax`. Les capitales accentuees
    sont des composites dans la source : `dessin.Source.contours` les resout,
    la lire par `layer.paths` rendrait des boites vides.
    """
    g = font.glyphs[nom]
    if g is None:
        return None
    lay = next((l for l in g.layers if l.layerId == master.id), None)
    if lay is None:
        return None
    src = D.Source(font, master.name)
    try:
        cs = src.contours(nom)
    except Exception:                                         # noqa: BLE001
        return None
    pts = [p for c in cs for p in c]
    if not pts:
        return None
    xs = [p[0] for p in pts]
    return (round(min(xs), 2), round(lay.width - max(xs), 2),
            round(lay.width, 2))


def volet_boite(seuil=SEUIL, verbeux=True):
    """L'effet du geste de titrage sur les deux approches, par glyphe-master.

    Rend {(source, nom): {master: (dg, dd, dchasse)}} pour les seuls
    glyphe-masters ou quelque chose bouge au-dela du seuil.
    """
    bouge = {}
    for isrc, (lab, _amont, _projet, _binaire) in enumerate(MT.SOURCES):
        fa = MT.etat_avant_fusion(isrc)
        ff = MT.etat_fusionne(isrc)
        if fa is None or ff is None:
            print(f"  {lab} : l'un des deux etats ne se reconstruit pas. "
                  f"Ce n'est pas un zero, c'est un NON MESURE.")
            continue
        per = MT.perimetre_arrete(isrc)
        masters = {m.name: m for m in ff.masters}
        ecartes = []
        n_mesures = 0
        for nom in sorted(per):
            for mn, m in masters.items():
                ma = next((x for x in fa.masters if x.name == mn), None)
                a = approches(fa, ma, nom) if ma is not None else None
                b = approches(ff, m, nom)
                if a is None or b is None:
                    ecartes.append(f"{nom}/{mn}")
                    continue
                n_mesures += 1
                dg, dd = round(b[0] - a[0], 2), round(b[1] - a[1], 2)
                dc = round(b[2] - a[2], 2)
                if abs(dg) > seuil or abs(dd) > seuil or abs(dc) > seuil:
                    bouge.setdefault((lab, nom), {})[mn] = (dg, dd, dc)
        if verbeux:
            noms = sorted({n for (l, n) in bouge if l == lab})
            print(f"\n=== {lab} : {len(per)} noms du perimetre, "
                  f"{n_mesures} glyphe-masters mesures, "
                  f"{len(noms)} glyphe(s) dont une approche bouge de plus de "
                  f"{seuil:g} unite(s)")
            if ecartes:
                # Un nom ecarte se DIT : une liste vide qui se lirait comme
                # "rien ne bouge" est le defaut que la relecture du tour 58 a
                # trouve dans `ecart_reconstruit`.
                print(f"    {len(ecartes)} glyphe-master(s) non mesurable(s), "
                      f"sans encre ou absents : "
                      f"{' '.join(ecartes[:8])}"
                      + (" …" if len(ecartes) > 8 else ""))
            # LES DEUX SENS, et c'est la ligne qui compte. Un garde-fou ecrit
            # contre un risque ne voit pas le risque inverse, piege consigne
            # depuis le vingt-quatrieme tour : une approche qui S'OUVRE laisse
            # un blanc, une approche qui SE FERME sort de la matiere vers le
            # voisin. Le point 18 annonce le premier ; la mesure doit pouvoir
            # rendre le second.
            ouvre = {"gauche": (0.0, ""), "droite": (0.0, "")}
            ferme = {"gauche": (0.0, ""), "droite": (0.0, "")}
            chasses = []
            for (l, n), par_m in bouge.items():
                if l != lab:
                    continue
                for mn, (dg, dd, dc) in par_m.items():
                    for cote, v in (("gauche", dg), ("droite", dd)):
                        if v > ouvre[cote][0]:
                            ouvre[cote] = (v, f"{n}/{mn}")
                        if v < ferme[cote][0]:
                            ferme[cote] = (v, f"{n}/{mn}")
                    if abs(dc) > seuil:
                        chasses.append(f"{n}/{mn} {dc:+.1f}")
            print(f"    approche qui S'OUVRE le plus  : "
                  f"gauche {ouvre['gauche'][0]:+6.1f} {ouvre['gauche'][1]:14s} "
                  f"droite {ouvre['droite'][0]:+6.1f} {ouvre['droite'][1]}")
            print(f"    approche qui SE FERME le plus : "
                  f"gauche {ferme['gauche'][0]:+6.1f} {ferme['gauche'][1]:14s} "
                  f"droite {ferme['droite'][0]:+6.1f} {ferme['droite'][1]}")
            print(f"    le point 18 annonce une boite RESSERREE jusqu'a "
                  f"{ANNONCE:g} unites, donc une approche qui s'ouvre d'autant")
            print(f"    chasses modifiees par le geste : "
                  + (", ".join(chasses) if chasses else "AUCUNE"))
            for n in noms[:40]:
                par_m = bouge[(lab, n)]
                g = max(v[0] for v in par_m.values())
                d = max(v[1] for v in par_m.values())
                print(f"      {n:18s} {len(par_m)} master(s)   "
                      f"gauche max {g:+6.1f}   droite max {d:+6.1f}")
            if len(noms) > 40:
                print(f"      … et {len(noms)-40} autre(s)")
    return bouge


def temoin_boite():
    """Prouve que `approches` LIT le dessin, en deplacant un contour.

    Un volet qui rendrait zero parce qu'il ne regarde pas est le defaut le plus
    frequent de ce projet. Le temoin pousse un contour de 30 unites vers la
    droite dans l'etat fusionne, en memoire, et exige que les deux approches
    bougent de +30 et -30.
    """
    ff = MT.etat_fusionne(0)
    if ff is None:
        print("  TEMOIN : etat non reconstruit, RIEN N'EST PROUVE.")
        return 1
    m = ff.masters[0]
    nom = "T"
    avant = approches(ff, m, nom)
    g = ff.glyphs[nom]
    lay = next((l for l in g.layers if l.layerId == m.id), None)
    for sh in lay.shapes:
        if hasattr(sh, "nodes"):
            for nd in sh.nodes:
                nd.position = (nd.position.x + 30.0, nd.position.y)
    D._CACHE_CONTOURS = {} if hasattr(D, "_CACHE_CONTOURS") else None
    apres = approches(ff, m, nom)
    ok = (apres is not None and avant is not None
          and abs((apres[0] - avant[0]) - 30.0) < 0.5
          and abs((apres[1] - avant[1]) + 30.0) < 0.5)
    print(f"  TEMOIN : {nom} pousse de +30 unites -> gauche "
          f"{apres[0] - avant[0]:+.1f}, droite {apres[1] - avant[1]:+.1f} — "
          + ("la mesure lit le dessin" if ok else
             "ELLE NE LIT PAS LE DESSIN"))
    return 0 if ok else 1


def volet_tables(bouge=None, seuil=SEUIL):
    """Les glyphes dont une approche bouge sont-ils DANS l'univers des tables ?

    Un glyphe qu'aucune des trois tables ne regarde ne peut etre referme par
    aucune d'elles, et le zero-diff de ces tables serait alors une cecite.
    Troisieme fois que le projet pose cette question : le `9` au
    quarante-quatrieme tour, les huit operateurs au cinquante-troisieme.
    """
    import paires_F as PF
    import paires_bouts as PB
    import paires_pieds as PP

    def univers(table_par_master):
        """Tous les noms que la table REGARDE, cibles et voisins confondus.

        Les trois tables n'ont pas la meme forme, et la lire au lieu de la
        supposer est le seul moyen de ne pas se tromper d'univers : la table du
        F est un dictionnaire indexe par le VOISIN, celles des pieds et des
        bouts sont des listes de triplets (a, b, valeur).
        """
        u = set()
        for entrees in table_par_master.values():
            if isinstance(entrees, dict):
                u.update(entrees)
            else:
                for a, b, _v in entrees:
                    u.update((a, b))
        return u

    if bouge is None:
        bouge = volet_boite(seuil=seuil, verbeux=False)
    noms = sorted({n for (_l, n) in bouge})
    tables = {}
    for lib, table in (("paires_F", PF.PAIRES_F),
                       ("paires_bouts", PB.PAIRES_BOUTS),
                       ("paires_pieds", PP.PAIRES_PIEDS)):
        u = univers(table)
        tables[lib] = u
        print(f"  {lib:14s} univers de {len(u)} nom(s)")
    if "F" not in tables["paires_F"]:
        # La table du F s'indexe par son VOISIN : son univers ne porte pas le
        # F lui-meme, et le dire vaut mieux que de le deduire.
        print("     note : la table du F s'indexe par le voisin, le F n'y "
              "figure donc pas comme cle.")
    dehors = [n for n in noms
              if not any(n in u for u in tables.values())]
    print(f"\n  {len(noms)} glyphe(s) dont une approche bouge ; "
          f"{len(noms) - len(dehors)} sont dans l'univers d'au moins une "
          f"table, {len(dehors)} n'y sont pas :")
    print("     " + (" ".join(dehors) if dehors else "aucun"))
    return dehors


def volet_plancher(seuil_boite=None, verbeux=True):
    """Ce que la boite elargie coute REELLEMENT en gouttiere, sur l'etat servi.

    Le volet `--boite` dit qu'une approche se ferme ; il ne dit pas si une
    paire en souffre. Ici on mesure le couloir entre deux lettres voisines sur
    `Temoin.glyphs`, avec son crenage effectif, et on le compare a celui
    d'Atkinson. Deux precautions que le projet a payees :

        on ne retient que ce que le GESTE a resserre, une paire deja sous le
        plancher dans la police de base n'etant pas un defaut du projet
        (vingt-septieme tour) ;

        on teste le seul SENS ou la matiere sort -- une boite elargie a droite
        mange l'approche de la lettre SUIVANTE, une boite elargie a gauche
        celle de la PRECEDENTE. Tester les deux sens partout doublerait le
        temps sans rien ajouter, et ne pas le dire serait le defaut du
        garde-fou a un seul sens du vingt-septieme tour.
    """
    import glyphsLib

    import approches as A
    from check_approches import VOISINS_F as VOISINS

    seuil_boite = SEUIL_BOITE if seuil_boite is None else seuil_boite
    bouge = volet_boite(seuil=SEUIL, verbeux=False)
    sous = []
    for isrc, (lab, amont_ch, projet, _b) in enumerate(MT.SOURCES):
        if not (os.path.exists(amont_ch) and os.path.exists(projet)):
            print(f"  {lab} : source absente, NON MESURE.")
            continue
        amont = glyphsLib.GSFont(amont_ch)
        servi = glyphsLib.GSFont(projet)
        # Les cibles sont DEDUITES du volet boite, jamais ecrites a la main :
        # une liste ecrite a la main se perime sans que rien ne le dise.
        cotes = {}
        for (l, n), par_m in bouge.items():
            if l != lab:
                continue
            for mn, (dg, dd, _dc) in par_m.items():
                if dg < -seuil_boite:
                    cotes.setdefault((n, mn), set()).add("gauche")
                if dd < -seuil_boite:
                    cotes.setdefault((n, mn), set()).add("droite")
        n_paires = 0
        # Les masters s'apparient par NOM : un identifiant ne vaut que dans
        # son fichier, et `kern` rend 0,0 sans lever sur un identifiant
        # inconnu, donc la reference d'Atkinson serait fausse en silence.
        ida = {m.name: m.id for m in amont.masters}
        for m in servi.masters:
            sa, st = D.Source(amont, m.name), D.Source(servi, m.name)
            for (nom, mn), quels in sorted(cotes.items()):
                if mn != m.name:
                    continue
                for v in VOISINS:
                    autre = v if len(v) > 1 else D.nom_glyphe(amont, v)
                    if (autre is None or amont.glyphs[autre] is None
                            or servi.glyphs[autre] is None):
                        continue
                    paires = []
                    if "droite" in quels:
                        paires.append((nom, autre))
                    if "gauche" in quels:
                        paires.append((autre, nom))
                    for a, b in paires:
                        try:
                            ka = A.kern(amont, ida[m.name], a, b)
                            kt = A.kern(servi, m.id, a, b)
                            ga = A.couloir_plein(sa, a, b, ka)
                            gt = A.couloir_plein(st, a, b, kt)
                        except Exception:                     # noqa: BLE001
                            continue
                        if ga is None or gt is None:
                            continue
                        n_paires += 1
                        if gt >= A.JOUR_MIN or gt >= ga - 0.5:
                            continue
                        sous.append((lab, m.name, a, b, round(ga, 1),
                                     round(gt, 1)))
        if verbeux:
            cibles = sorted({n for (n, _m) in cotes})
            print(f"\n=== {lab} : {len(cibles)} glyphe(s) dont la boite "
                  f"s'elargit de plus de {seuil_boite:g} unites, "
                  f"{n_paires} paire-master(s) mesure(s)")
            print(f"    {' '.join(cibles)}")
            ici = [s for s in sous if s[0] == lab]
            print(f"    sous le plancher de {A.JOUR_MIN:.0f} unites ET "
                  f"resserrees par le projet : {len(ici)}")
            for s in ici[:20]:
                print(f"      {s[1]:18s} {s[2]}+{s[3]:12s} atkinson "
                      f"{s[4]:+7.1f}  servi {s[5]:+7.1f}")
            if len(ici) > 20:
                print(f"      … et {len(ici)-20} autre(s)")
    return sous


def volet_exact(verbeux=True):
    """Les cas du volet `--plancher`, repasses au couloir EXACT.

    `approches.couloir_plein` n'est pas un couloir, c'est un MINORANT : il
    compare le bord le plus a droite de la premiere lettre au bord le plus a
    gauche de la seconde, et il rend un chevauchement qui n'existe pas des
    qu'une des deux presente deux intervalles d'encre disjoints a la meme
    hauteur -- la queue du `q`, le point du `j`, la barre du `x` italique. Le
    defaut est conservateur : il peut inventer un contact, il ne peut pas en
    rater un. **Un cas trouve par le minorant n'est donc pas un defaut tant que
    le couloir exact ne l'a pas confirme.**
    """
    import glyphsLib

    import approches as A
    from balayage_lot4b import couloir_exact

    cas = volet_plancher(verbeux=False)
    fonts = {}
    restent = []
    for lab, mn, a, b, ga, gt in cas:
        isrc = 0 if lab == "romain" else 1
        if lab not in fonts:
            fonts[lab] = glyphsLib.GSFont(MT.SOURCES[isrc][2])
        servi = fonts[lab]
        m = next((x for x in servi.masters if x.name == mn), None)
        if m is None:
            continue
        st = D.Source(servi, mn)
        try:
            k = A.kern(servi, m.id, a, b)
            vrai = couloir_exact(st, a, b, k)
        except Exception:                                     # noqa: BLE001
            continue
        restent.append((lab, mn, a, b, ga, gt, round(vrai, 1)))
    durs = [r for r in restent if r[6] < A.JOUR_MIN]
    if verbeux:
        print(f"\n=== {len(cas)} cas signales par le MINORANT, "
              f"{len(restent)} remesures au couloir EXACT, "
              f"{len(durs)} restent sous le plancher de {A.JOUR_MIN:.0f}")
        vus = set()
        for lab, mn, a, b, ga, gt, vrai in sorted(
                durs, key=lambda r: r[6])[:30]:
            print(f"   {lab:9s} {mn:18s} {a}+{b:12s} atkinson {ga:+7.1f}  "
                  f"minorant {gt:+7.1f}  EXACT {vrai:+7.1f}")
            vus.add((a, b))
        if len(durs) > 30:
            print(f"   … et {len(durs)-30} autre(s)")
        inventes = [r for r in restent if r[6] >= A.JOUR_MIN]
        print(f"\n   {len(inventes)} cas etaient un artefact du minorant, "
              f"dont : "
              + ", ".join(f"{r[2]}+{r[3]} {r[5]:+.0f}->{r[6]:+.0f}"
                          for r in inventes[:6]))
    return durs


def taches(src, mid, texte, px):
    """Le nombre de taches d'encre du texte COMPOSE AVEC SON CRENAGE.

    `dessin.dessiner` avance de la seule chasse : juger un espacement dessus
    juge un texte qui n'existe pas. Le rendu passe donc par
    `approches.composer`, seul peintre du projet qui porte le crenage et qui
    classe les contours par imbrication.
    """
    import numpy as np
    from PIL import Image
    from scipy import ndimage

    import approches as A

    lg = A.largeur_composee(src, mid, texte, px)
    im = Image.new("RGB", (int(lg) + 2 * px, int(2.4 * px)), (255, 255, 255))
    A.composer(im, src, mid, texte, px * 0.5, int(1.7 * px), px)
    a = np.asarray(im.convert("L")) < 128
    return ndimage.label(a, structure=np.ones((3, 3)))[1]


def volet_contacts(source=None, verbeux=True):
    """Les paires du volet `--exact`, jugees au COMPTAGE DE TACHES D'ENCRE.

    C'est le juge du projet depuis le dix-huitième tour, et il est independant
    des deux mesures de couloir : deux lettres se touchent quand le mot rend
    moins de taches que la somme de ses lettres rendues seules. Le compte de
    reference est cette somme, jamais le nombre de lettres -- le `i`, le `j` et
    le `Å` en portent deux.

    Mesure a trois resolutions, et on ne conclut que si elles concordent : un
    contact mesure par rasterisation en depend, deux traits distants de deux
    unites fusionnant a 150 pixels de cadratin et se separant a 600.

    L'AMONT EST MESURE EN FACE, parce qu'un contact qui existe deja dans
    Atkinson n'est pas un defaut du projet -- le vingt-septieme tour a paye
    cinq fausses alertes de cette sorte.
    """
    import glyphsLib

    durs = volet_exact(verbeux=False)
    par_source = {}
    for lab, mn, a, b, _ga, _gt, vrai in durs:
        if source and lab != source:
            continue
        par_source.setdefault(lab, {}).setdefault((a, b), set()).add(mn)

    contacts = []
    for lab, paires in par_source.items():
        isrc = 0 if lab == "romain" else 1
        amont = glyphsLib.GSFont(MT.SOURCES[isrc][1])
        servi = glyphsLib.GSFont(MT.SOURCES[isrc][2])
        mida = {m.name: m.id for m in amont.masters}
        mids = {m.name: m.id for m in servi.masters}
        for (a, b), masters in sorted(paires.items()):
            texte = _texte_de(servi, a, b)
            if texte is None:
                if verbeux:
                    print(f"   {lab} {a}+{b} : pas de caractere pour composer "
                          f"cette paire, NON MESURE au comptage.")
                continue
            for mn in sorted(masters):
                ss = D.Source(servi, mn)
                sa = D.Source(amont, mn)
                nt = [taches(ss, mids[mn], texte, px) for px in (300, 600, 1200)]
                seuls_t = sum(taches(ss, mids[mn], c, 600) for c in texte)
                na = [taches(sa, mida[mn], texte, px) for px in (300, 600, 1200)]
                seuls_a = sum(taches(sa, mida[mn], c, 600) for c in texte)
                fusion_t = all(n < seuls_t for n in nt)
                fusion_a = all(n < seuls_a for n in na)
                if fusion_t and not fusion_a:
                    contacts.append((lab, mn, a, b, texte, nt, seuls_t))
                    if verbeux:
                        print(f"   !! CONTACT SERVI  {lab:9s} {mn:18s} "
                              f"{texte!r:8s} temoin {nt} pour {seuls_t} "
                              f"lettres seules ; Atkinson {na} pour {seuls_a}")
    if verbeux:
        print(f"\n   {len(contacts)} contact(s) servi(s) absent(s) d'Atkinson, "
              f"sur {sum(len(v) for v in par_source.values())} paire(s) "
              f"signalee(s) par le couloir exact")
    return contacts


def _texte_de(font, a, b):
    """Le texte a composer pour la paire, ou None si un membre n'a pas de
    caractere. Une paire qu'aucune saisie ne compose ne peut pas etre jugee au
    comptage, et le dire vaut mieux que de l'omettre."""
    ca = _car(font, a)
    cb = _car(font, b)
    return None if (ca is None or cb is None) else ca + cb


def _car(font, nom):
    g = font.glyphs[nom]
    uni = getattr(g, "unicode", None) if g is not None else None
    if not uni:
        return None
    try:
        return chr(int(uni, 16))
    except (TypeError, ValueError):
        return None


#: Sous cet ecart, deux gouttieres sont la MEME gouttiere, et une valeur ecrite
#: sur la cle de groupe vaut pour tous les membres. Le cinquante-sixieme tour a
#: employe "la meme a un dixieme pres" pour le reglage X+A, premier du projet
#: ecrit sur une cle de groupe ; le meme critere est repris ici.
TOL_FAMILLE = 0.5


def volet_familles(verbeux=True):
    """Chaque paire fautive peut-elle s'ecrire sur une CLE DE GROUPE ?

    Le groupe de crenage decide de l'etendue d'un reglage, et c'est une
    decision de dessin, pas une commodite : ecrire sur un groupe propage la
    valeur a tous ses membres. La question se pose donc paire par paire, et
    elle se MESURE -- le groupe droit du `A` porte ses six accentuees, qui
    dessinent le meme pied ; le groupe droit du `Q` est `O`, qui porte aussi le
    `O`, le `C` et le `G`, dont aucun n'a la queue du Q.

    Rend {(a, b): ("groupe"|"exception", membres, ecart)} pour chaque paire
    signalee par le couloir exact.
    """
    import glyphsLib

    import approches as A

    durs = volet_exact(verbeux=False)
    par_source = {}
    for lab, mn, a, b, *_r in durs:
        par_source.setdefault(lab, {}).setdefault((a, b), set()).add(mn)

    verdicts = {}
    for lab, paires in par_source.items():
        isrc = 0 if lab == "romain" else 1
        servi = glyphsLib.GSFont(MT.SOURCES[isrc][2])
        # Les membres d'un groupe se LISENT dans la source, jamais d'une liste.
        membres = {}
        for g in servi.glyphs:
            if g.rightKerningGroup:
                membres.setdefault(g.rightKerningGroup, []).append(g.name)
        if verbeux:
            print(f"\n=== {lab} : {len(paires)} paire(s) a loger")
        for (a, b), masters in sorted(paires.items()):
            ga = servi.glyphs[a]
            grp = ga.rightKerningGroup if ga is not None else None
            fam = sorted(membres.get(grp, [])) if grp else [a]
            mn = sorted(masters)[0]
            st = D.Source(servi, mn)
            m = next(x for x in servi.masters if x.name == mn)
            vals = {}
            for n in fam:
                if servi.glyphs[n] is None:
                    continue
                try:
                    k = A.kern(servi, m.id, n, b)
                    vals[n] = A.couloir_plein(st, n, b, k)
                except Exception:                             # noqa: BLE001
                    continue
            propres = {n: v for n, v in vals.items() if v is not None}
            if len(propres) <= 1:
                verdict, ecart = "exception", 0.0
            else:
                ecart = max(propres.values()) - min(propres.values())
                verdict = ("groupe" if ecart <= TOL_FAMILLE else "exception")
            verdicts[(lab, a, b)] = (verdict, grp, sorted(propres), ecart)
            if verbeux:
                print(f"   {a}+{b:12s} groupe {str(grp):6s} "
                      f"{len(propres):2d} membre(s)  ecart {ecart:6.1f} u  "
                      f"-> {verdict.upper()}"
                      + ("" if verdict == "groupe" or len(propres) <= 1
                         else f"   ({' '.join(sorted(propres))})"))
    if verbeux:
        g = sum(1 for v in verdicts.values() if v[0] == "groupe")
        print(f"\n   {g} paire(s) s'ecrivent sur une cle de GROUPE, "
              f"{len(verdicts)-g} demandent une EXCEPTION glyphe-glyphe")
    return verdicts


def main():
    if "--familles" in sys.argv:
        volet_familles()
        return 0
    if "--contacts" in sys.argv:
        src = None
        if "--source" in sys.argv:
            src = sys.argv[sys.argv.index("--source") + 1]
        volet_contacts(source=src)
        return 0
    if "--exact" in sys.argv:
        volet_exact()
        return 0
    if "--plancher" in sys.argv:
        volet_plancher()
        return 0
    if "--tables" in sys.argv:
        volet_tables()
        return 0
    if "--boite" in sys.argv:
        seuil = SEUIL
        if "--seuil" in sys.argv:
            seuil = float(sys.argv[sys.argv.index("--seuil") + 1])
        volet_boite(seuil=seuil)
        print()
        return temoin_boite()
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
