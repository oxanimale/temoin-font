#!/usr/bin/env python3
"""Le producteur de `paires_contacts.py` : ce que le titrage fusionne fait aux
FAMILLES, et que les trois tables existantes ne regardent pas.

D'OU VIENT CETTE TABLE. Le point ouvert 18 annoncait, depuis le huitieme tour,
que le geste de titrage RESSERRE la boite du glyphe jusqu'a 39 unites, donc
qu'il ouvre un blanc et que les approches sont a refaire. Mesure au
cinquante-neuvieme tour sur l'etat ecrit, par `mesure_point18.py --boite` :
**aucune approche ne s'ouvre, dans aucune des deux sources**, et elles se
FERMENT jusqu'a 30,6 unites au romain et 49,2 en italique. Le point se trompait
de sens, et le vrai risque n'est pas un blanc trop grand, c'est de la matiere
qui sort vers le voisin.

CE QUE LA MESURE A TROUVE. 41 paires sous le plancher de jour au couloir EXACT,
et 86 glyphe-masters en CONTACT prouve par comptage de taches d'encre a trois
resolutions, absents d'Atkinson. La cause n'est pas le geste : c'est que les
trois tables de paires regardent la LETTRE DE BASE et pas les glyphes qui la
redessinent. `A+x` recoit +36 au Bold, `Agrave+x` recoit 0 ; `A+j` recoit +106,
`Agrave+j` recoit 0. C'est la sixieme forme du meme defaut dans ce projet,
apres `e.sc`, l'AE, l'Aring, le double `.ti` et les vingt-neuf accentuees de
`VOISINS_F` au cinquante-quatrieme tour.

LE CRITERE, ET IL EST MESURE A CHAQUE EXECUTION.

    L'UNIVERS des cibles est DEDUIT, jamais ecrit a la main : ce sont les
    glyphes dont le geste de titrage elargit la boite de plus de
    `SEUIL_BOITE`, lus par `mesure_point18.volet_boite`. Une liste ecrite a la
    main se perime sans que rien ne le dise, et c'est ce qui a produit le
    defaut que cette table repare.

    LE SENS suit le cote qui s'elargit : une boite elargie a DROITE mange
    l'approche de la lettre SUIVANTE, une boite elargie a GAUCHE celle de la
    PRECEDENTE. Un garde-fou qui ne teste qu'un sens doit le dire, et le
    vingt-septieme tour a paye l'omission inverse.

    DEUX GRANDEURS, ET CHACUNE A SON ROLE. Ce qui DECIDE qu'une paire entre
    dans la table est le couloir EXACT, `balayage_lot4b.couloir_exact` : le
    minorant `approches.couloir_plein` invente un contact des qu'une lettre
    presente deux intervalles d'encre disjoints a la meme hauteur, ce que font
    la queue du `q`, le point du `j` et la barre du `x` italique. Ce qui
    CALCULE la valeur est le minorant, parce que la dichotomie exige une
    grandeur monotone en `k` et que **le couloir exact ne l'est pas** -- sur
    `q+x` au Bold il vaut +8,4 a l'ecartement nul et -5,0 a +53,7. Le minorant
    ferme donc au moins autant qu'il faut, et le resultat est VERIFIE au
    couloir exact avant d'entrer dans la table.

    LA VALEUR ferme jusqu'au plancher `approches.JOUR_MIN`, bornee par le
    couloir d'Atkinson : ecarter au-dela serait plus lache que la police de
    base, ce qu'aucune raison ne soutient. Le critere ecrit dans chaque entree
    dit laquelle des deux references a decide -- "plancher" quand la cible est
    atteinte, "atkinson" quand le couloir rendu vaut celui de la police de
    base, "insuffisant" quand il reste en deca, ce qui ne se produit sur
    aucune entree aujourd'hui.

    LA CLE se choisit PAR MESURE, arbitrage de Nicolas au cinquante-neuvieme
    tour. Une valeur ecrite sur une cle de GROUPE se propage a tous les membres
    du groupe : elle n'est juste que si tous ont la meme gouttiere devant ce
    voisin. Mesure : le groupe droit du `A` porte onze noms, dont `Aogonek` et
    `Delta`, et l'ecart de gouttiere y atteint 198 unites -- la gouttiere se
    lit sur toute la hauteur, accent compris. **La cle de groupe ne tient donc
    que sur 6 paires des 56, toutes sur le `K`**, dont le groupe n'a que deux
    membres. Le reste s'ecrit en exception glyphe-glyphe. Le critere se
    remesure a chaque execution, il n'est pas fige dans la table.

UNE PAIRE, UN SEUL PRODUCTEUR. Toute paire deja portee par `paires_F`,
`paires_pieds` ou `paires_bouts` est ECARTEE et la raison est imprimee : deux
tables qui ecrivent en valeur totale sur la meme cle, la seconde ecrase la
premiere, et le cinquante-quatrieme tour a vu un reglage valide en navigateur
disparaitre ainsi en silence.

L'ORDRE DANS LA CHAINE. Ce producteur lit l'etat SERVI, donc il tourne APRES
`make_temoin`, comme `inventaire_F`. La table n'entre dans la source qu'au
`make_temoin` suivant, et le point fixe se prouve par une seconde execution qui
ne doit plus rien avoir a ecrire.

    python3 inventaire_contacts.py --source romain
    python3 inventaire_contacts.py --source romain --ecrire
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import glyphsLib                                              # noqa: E402

import approches as A                                         # noqa: E402
import dessin as D                                            # noqa: E402
import mesure_point18 as MP                                   # noqa: E402
import mesure_titrage as MT                                   # noqa: E402
from balayage_lot4b import couloir_exact                      # noqa: E402
from check_approches import VOISINS_F as VOISINS              # noqa: E402

SORTIE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "paires_contacts.py")

#: Au-dela de quoi la boite elargie fait de cette lettre une cible. LU chez
#: `mesure_point18`, qui le possede : le producteur et l'instrument de mesure
#: doivent filtrer le meme univers de cibles, et un seuil recopie devient un
#: desaccord silencieux.
SEUIL_BOITE = MP.SEUIL_BOITE

#: L'ecart de gouttiere sous lequel tous les membres d'un groupe recoivent la
#: meme valeur. Meme critere que le reglage `X+A` du cinquante-sixieme tour.
TOL_FAMILLE = MP.TOL_FAMILLE

#: LES PAIRES QUE NICOLAS A SORTIES DE LA TABLE, avec la raison de chacune.
#: Un nom decide et un nom jamais regarde sont identiques dans une table : ces
#: paires touchent, c'est mesure, et le projet ne les ferme pas. Elles sont
#: ECARTEES du producteur et REMESUREES par le controle, qui exige qu'elles
#: touchent encore -- une limite connue qui cesserait d'etre vraie sans que
#: rien ne le dise serait un oubli deguise en decision.
#:
#: Le q, cinquante-neuvieme tour : aucune de ses six paires n'apparait en
#: francais, la queue du q ne rencontrant que des lettres qui ne la suivent
#: jamais. C'est la meme raison qu'au vingt-sixieme tour pour `q+M` et `q+m`,
#: prise cette fois dans l'autre sens : la, le projet avait ferme ; ici
#: Nicolas a regarde le dessin et juge que la fermeture coute plus qu'elle ne
#: rapporte.
HORS_TABLE = {
    ("q", "x"): "aucune occurrence en francais, contact assume",
    ("q", "F"): "aucune occurrence en francais, contact assume",
    ("q", "P"): "aucune occurrence en francais, contact assume",
    ("q", "b"): "aucune occurrence en francais, contact assume",
    ("q", "germandbls"): "aucune occurrence en francais, contact assume",
    ("q", "plusminus"): "aucune occurrence en francais, contact assume",
}

#: LES PAIRES OU LA BORNE D'ATKINSON EST LEVEE, avec leur cible de jour.
#: Le critere general du projet est de ne jamais ecarter plus que la police de
#: base : ecarter au-dela serait plus lache qu'elle sans qu'aucune raison le
#: soutienne. Ces paires ont leur raison, et c'est que la police de base y est
#: EN CONTACT -- rendre son couloir reviendrait a servir un contact.
#:
#: `K+idieresis` touche dans Atkinson dans les quatre masters gras, de -3,3 a
#: -13,6 unites de chevauchement, mesure au couloir exact sur le binaire servi.
#: Nicolas a tranche au cinquante-neuvieme tour, sur planche : le contact se
#: ferme, donc la borne se leve. C'est le second endroit ou le projet corrige
#: sa police de base, apres les trois reglages du cinquantieme tour.
AU_DELA_ATKINSON = {
    ("K", "idieresis"): A.JOUR_MIN,
}


def deja_portee(a, b, master):
    """La paire est-elle deja ecrite par une autre table, et par laquelle ?"""
    import paires_F as PF
    import paires_bouts as PB
    import paires_pieds as PP

    if PF.PAIRES_F.get(master, {}).get(b) is not None and a == "F":
        return "paires_F"
    for lib, table in (("paires_bouts", PB.PAIRES_BOUTS),
                       ("paires_pieds", PP.PAIRES_PIEDS)):
        for x, y, _v in table.get(master, []):
            if (x, y) == (a, b):
                return lib
    return None


def k_pour(st, a, b, k0, plafond, vrai_amont=None):
    """Le plus petit ecartement qui porte le couloir au plancher de jour.

    LA DICHOTOMIE PORTE SUR LE MINORANT, ET C'EST UNE CORRECTION MESUREE. Un
    premier jet la faisait porter sur `couloir_exact`, qui **n'est pas
    monotone en `k`** -- la passation l'ecrit depuis le point 55, et le cas
    s'est reproduit ici : sur `q+x` au Bold, le couloir exact vaut +8,4 a
    l'ecartement nul et -5,0 a +53,7, parce qu'en glissant vers la droite le
    `x` quitte un couple d'intervalles d'encre pour en rencontrer un autre,
    la queue du `q` sortant de 73 unites hors de sa chasse. Une dichotomie sur
    une grandeur non monotone rend un nombre qui a l'air d'une decision et qui
    n'en est pas une : elle avait ecrit +54 la ou le contact demeure.

    `approches.couloir_plein` est strictement croissant en `k` -- il vaut
    `(w + k + min(bords de b)) - max(bords de a)` -- donc la dichotomie y est
    valide, et c'est la grandeur sur laquelle les trois autres tables du projet
    sont bornees. Il MINORE le couloir vrai, donc une valeur calculee sur lui
    ferme au moins autant qu'il faut.

    LE RESULTAT EST VERIFIE AU COULOIR EXACT, et le verdict se lit contre DEUX
    references, pas une. Le plancher de jour est la cible ; le couloir de la
    police de base est la limite de ce qu'on peut rendre sans etre plus lache
    qu'elle. `Agrave+x` tient 20,8 unites dans Atkinson, donc sous le plancher
    de 24 : exiger 24 y serait exiger mieux que la police de base, et le
    vingt-septieme tour a deja tranche ce cas sur `q+y`.

    Rend (valeur, critere) : "plancher" quand la cible est atteinte,
    "atkinson" quand le couloir rendu vaut celui de la police de base, et
    "insuffisant" quand il reste en deca -- ce dernier cas se DIT, il ne se
    cache pas sous un chiffre qui aurait l'air d'une decision.
    """
    if A.couloir_plein(st, a, b, k0) >= A.JOUR_MIN:
        return 0.0, "deja au-dessus"
    atteint = A.couloir_plein(st, a, b, k0 + plafond) >= A.JOUR_MIN
    if not atteint:
        val = plafond
    else:
        lo, hi = 0.0, plafond
        for _ in range(20):
            mi = (lo + hi) / 2.0
            if A.couloir_plein(st, a, b, k0 + mi) >= A.JOUR_MIN:
                hi = mi
            else:
                lo = mi
        val = hi
    vrai = couloir_exact(st, a, b, k0 + val)
    if vrai is None or vrai >= A.JOUR_MIN:
        return val, "plancher"
    if vrai_amont is not None and vrai >= vrai_amont - 0.5:
        return val, "atkinson"
    return val, "insuffisant"


def membres_du_groupe(font, nom):
    """Les noms qui partagent le groupe de crenage DROIT de `nom`, lus dans la
    source. Une famille se lit, elle ne se recopie pas."""
    g = font.glyphs[nom]
    grp = g.rightKerningGroup if g is not None else None
    if not grp:
        return grp, [nom]
    return grp, sorted(x.name for x in font.glyphs
                       if x.rightKerningGroup == grp)


def verdict_cle(servi, st, m, a, b, cache=None):
    """"groupe" ou "glyphe", MESURE : tous les membres du groupe de crenage
    droit de `a` ont-ils la meme gouttiere devant `b` ?

    Elle vit ici parce que DEUX passes en ont besoin -- le balayage et celle
    des bornes levees -- et que deux codes qui decident la meme chose doivent
    passer par la meme fonction. La passe dediee forcait "glyphe" : elle
    ecrivait une exception la ou la mesure donnait un groupe, donc elle
    corrigeait `K+idieresis` en laissant les autres membres du groupe tels
    quels, sans que rien ne le dise.
    """
    grp, fam = membres_du_groupe(servi, a)
    clef = (grp, b, m.name)
    if cache is not None and clef in cache:
        return cache[clef]
    vals = []
    for n2 in fam:
        if servi.glyphs[n2] is None:
            continue
        try:
            v = couloir_exact(st, n2, b, A.kern(servi, m.id, n2, b))
        except Exception:                                     # noqa: BLE001
            continue
        if v is not None:
            vals.append(v)
    cle = ("groupe" if (len(vals) > 1 and grp
                        and max(vals) - min(vals) <= TOL_FAMILLE)
           else "glyphe")
    if cache is not None:
        cache[clef] = cle
    return cle


def parcours(lab, verbeux=True):
    """Rend {master: [(a, b, valeur, cle, critere), ...]} pour une source."""
    isrc = 0 if lab == "romain" else 1
    amont = glyphsLib.GSFont(MT.SOURCES[isrc][1])
    servi = glyphsLib.GSFont(MT.SOURCES[isrc][2])
    # NE PAS MESURER SON PROPRE REFLET. Une fois la chaine rejouee, l'etat
    # servi porte cette table : sans ce retrait, le producteur ne verrait plus
    # aucune paire a refermer et rendrait une table VIDE, ce qui effacerait le
    # travail sans qu'aucun controle ne le dise. Le retrait passe par
    # `approches`, donc par le meme code que l'ecriture.
    sup, rest, etr = A.retirer_contacts(servi, amont)
    if verbeux:
        print(f"  etat mesure : {sup} cle(s) de cette table supprimee(s), "
              f"{rest} rendue(s) a leur valeur d'Atkinson, {etr} laissee(s) "
              f"parce qu'une autre valeur y est posee"
              + ("" if sup or rest else
                 " — la table n'est pas encore dans la source, ce qui est "
                 "normal a sa premiere ecriture"))

    bouge = MP.volet_boite(seuil=MP.SEUIL, verbeux=False)
    cotes = {}
    for (l, n), par_m in bouge.items():
        if l != lab:
            continue
        for mn, (dg, dd, _dc) in par_m.items():
            if dg < -SEUIL_BOITE:
                cotes.setdefault((n, mn), set()).add("gauche")
            if dd < -SEUIL_BOITE:
                cotes.setdefault((n, mn), set()).add("droite")

    # LES MASTERS S'APPARIENT PAR NOM, jamais par identifiant : ceux d'un
    # fichier ne valent rien dans un autre, et `approches.kern` rend 0,0 sans
    # lever sur un identifiant inconnu. Mesure : dans l'etat d'aujourd'hui les
    # deux sources portent les MEMES identifiants, `Temoin.glyphs` derivant de
    # l'amont, donc le defaut etait latent -- et une source regeneree
    # autrement ferait lire zero partout comme valeur d'Atkinson, ce qui
    # fausserait chaque comparaison avant/apres sans un mot.
    ida = {m.name: m.id for m in amont.masters}
    par_master, ecartees, sorties, cache_cle = {}, [], [], {}
    for m in servi.masters:
        sa, st = D.Source(amont, m.name), D.Source(servi, m.name)
        lignes, vues = [], set()
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
                    if (a, b) in vues:
                        continue
                    # DEUX PASSES, et la premiere est le MINORANT. Filtrer
                    # d'emblee au couloir exact demanderait 48 000 mesures et
                    # fait sauter le plafond de temps du bac a sable. Le
                    # minorant est conservateur -- il peut inventer un
                    # contact, il ne peut pas en rater un -- donc il ne laisse
                    # rien passer, et le couloir exact ne juge ensuite que ce
                    # qu'il signale. Mesure du cinquante-neuvieme tour : sur
                    # les 134 cas signales, il n'en a invente aucun.
                    try:
                        ka = A.kern(amont, ida[m.name], a, b)
                        kt = A.kern(servi, m.id, a, b)
                        pa = A.couloir_plein(sa, a, b, ka)
                        pt = A.couloir_plein(st, a, b, kt)
                    except Exception:                         # noqa: BLE001
                        continue
                    if (pa is None or pt is None or pt >= A.JOUR_MIN
                            or pt >= pa - 0.5):
                        continue
                    try:
                        ga = couloir_exact(sa, a, b, ka)
                        gt = couloir_exact(st, a, b, kt)
                    except Exception:                         # noqa: BLE001
                        continue
                    if ga is None or gt is None or gt >= A.JOUR_MIN:
                        continue
                    # Ne retenir que ce que le PROJET a resserre : une paire
                    # deja sous le plancher dans Atkinson n'est pas un defaut
                    # du projet, et l'ecarter serait plus lache que la police
                    # de base sans qu'aucune raison le soutienne.
                    # Ne retenir que ce que le PROJET a resserre -- une paire
                    # deja sous le plancher dans Atkinson et que le projet ne
                    # touche pas n'est pas un defaut du projet, et l'ecarter
                    # serait plus lache que la police de base.
                    #
                    # SAUF CELLES DONT LA BORNE EST LEVEE, et c'est le sens
                    # meme de la levee : leur defaut est celui de la police de
                    # base, Nicolas a decide de le corriger, donc le filtre qui
                    # protege des fausses alertes les ferait sortir de la table
                    # a la premiere regeneration. Le defaut s'est produit :
                    # apres une passe complete, le retrait rend a `K+idieresis`
                    # sa valeur d'Atkinson, la paire cesse d'etre "resserree par
                    # le projet", et elle disparaissait de la table en silence.
                    if gt >= ga - 0.5:
                        continue
                    porteuse = deja_portee(a, b, m.name)
                    if porteuse:
                        ecartees.append((m.name, a, b, porteuse))
                        continue
                    if (a, b) in HORS_TABLE:
                        # Sortie par DECISION, pas par oubli. Le controle la
                        # remesure et exige qu'elle touche encore.
                        sorties.append((m.name, a, b, HORS_TABLE[(a, b)]))
                        continue
                    vues.add((a, b))
                    # Le plafond se mesure sur la MEME grandeur que la
                    # dichotomie, donc sur le minorant : melanger les deux
                    # ferait borner une recherche par un nombre qui ne vit pas
                    # sur son axe. C'est ce que rendre le couloir d'Atkinson
                    # veut dire pour les trois autres tables du projet.
                    plafond = max(pa - pt, 1.0)
                    if (a, b) in AU_DELA_ATKINSON:
                        # Traitee par la passe dediee, plus bas : son defaut
                        # est celui de la police de base, donc les deux
                        # filtres de ce balayage -- qui ne retiennent que ce
                        # que le PROJET resserre -- la font sortir des qu'une
                        # regeneration lui a rendu sa valeur d'Atkinson.
                        continue
                    val, crit = k_pour(st, a, b, kt, plafond, ga)
                    # La cle se MESURE : groupe si tous les membres ont la
                    # meme gouttiere devant ce voisin, exception sinon.
                    # Le verdict se mesure une fois par (groupe, voisin,
                    # master) et non une fois par paire : sans ce cache, les
                    # sept accentuees du A refont onze mesures chacune devant
                    # le meme voisin.
                    cle = verdict_cle(servi, st, m, a, b, cache_cle)
                    lignes.append((a, b, int(round(kt + val)), cle, crit))
        lignes.sort()
        par_master[m.name] = lignes

    # LA PASSE DES PAIRES DONT LA BORNE EST LEVEE.
    #
    # Elle vit HORS du balayage parce que son critere est l'inverse : le
    # balayage cherche ce que le projet a resserre, celle-ci corrige ce que la
    # police de base laisse en contact. Elle ne s'applique que la ou la raison
    # vaut, mesuree master par master : Atkinson touche sur `K+idieresis` dans
    # les quatre masters gras et tient +18,0 au Regular, donc la levee y suit
    # le dessin et non une liste de masters ecrite a la main.
    for (a, b), cible in AU_DELA_ATKINSON.items():
        if servi.glyphs[a] is None or servi.glyphs[b] is None:
            continue
        for m in servi.masters:
            sa, st = D.Source(amont, m.name), D.Source(servi, m.name)
            try:
                ka = A.kern(amont, ida[m.name], a, b)
                kt = A.kern(servi, m.id, a, b)
                ga = couloir_exact(sa, a, b, ka)
                gt = couloir_exact(st, a, b, kt)
            except Exception:                                 # noqa: BLE001
                continue
            if ga is None or gt is None or ga > 0.0:
                continue
            lo, hi = 0.0, 300.0
            for _ in range(20):
                mi = (lo + hi) / 2.0
                if couloir_exact(st, a, b, kt + mi) >= cible:
                    hi = mi
                else:
                    lo = mi
            lignes = [x for x in par_master.get(m.name, [])
                      if (x[0], x[1]) != (a, b)]
            lignes.append((a, b, int(round(kt + hi)),
                           verdict_cle(servi, st, m, a, b, cache_cle),
                           "au-dela d'atkinson"))
            par_master[m.name] = sorted(lignes)

    # UN VERDICT DE CLE PAR PAIRE, ET NON PAR MASTER. Le meme couple peut
    # rendre "groupe" dans un master et "glyphe" dans un autre, la gouttiere
    # des membres divergeant avec la graisse ; ecrire les deux ferait de la
    # meme paire une exception ici et une valeur de groupe la, ce qu'aucun
    # controle ne saurait lire. En cas de desaccord, l'exception l'emporte :
    # elle ne touche que ce que la mesure a vu.
    desaccords = set()
    verdict = {}
    for lignes in par_master.values():
        for a, b, _v, cle, _c in lignes:
            if verdict.setdefault((a, b), cle) != cle:
                verdict[(a, b)] = "glyphe"
                desaccords.add((a, b))
    for mn, lignes in par_master.items():
        par_master[mn] = [(a, b, v, verdict[(a, b)], c)
                          for a, b, v, _cle, c in lignes]
    if verbeux and desaccords:
        print(f"  {len(desaccords)} paire(s) dont le verdict de cle differe "
              f"selon le master, ramenee(s) a l'exception : "
              + ", ".join(f"{a}+{b}" for a, b in sorted(desaccords)))
    if verbeux:
        # L'impression se fait APRES l'unification des cles, sinon elle
        # annonce un verdict que la table ne porte pas. Elle vivait dans la
        # boucle sur les masters ; l'ajout de l'unification l'a fait tomber
        # dans le bloc voisin sans erreur, et elle ne s'imprimait plus que
        # s'il y avait un desaccord. Un bloc deplace d'un cran ne leve pas.
        for mn, lignes in par_master.items():
            grp = sum(1 for x in lignes if x[3] == "groupe")
            sat = sum(1 for x in lignes if x[4] == "atkinson")
            print(f"  {mn:20s} {len(lignes):3d} paire(s), {grp} sur cle de "
                  f"groupe, {sat} bornee(s) par Atkinson")
            for a, b, val, cle, crit in lignes[:5]:
                print(f"      {a}+{b:14s} {val:+6d}  {cle:9s} {crit}")
            if len(lignes) > 5:
                print(f"      … et {len(lignes)-5} autre(s)")
    if verbeux and sorties:
        vus = sorted({(a, b, r) for _m, a, b, r in sorties})
        print(f"  {len(vus)} paire(s) SORTIES PAR DECISION, elles touchent et "
              f"le projet ne les ferme pas : "
              + ", ".join(f"{a}+{b}" for a, b, _r in vus))
    if verbeux and ecartees:
        vus = sorted({(a, b, p) for _m, a, b, p in ecartees})
        print(f"  {len(vus)} paire(s) ECARTEES, deja portees par une autre "
              f"table : "
              + ", ".join(f"{a}+{b} ({p})" for a, b, p in vus[:6])
              + (" …" if len(vus) > 6 else ""))
    return par_master


def ecrire(tables):
    """Ecrit `paires_contacts.py`. `tables` vaut {source: {master: lignes}}."""
    with open(SORTIE, "w", encoding="utf-8") as fh:
        fh.write('"""Les paires que le titrage fusionne met en CONTACT, et que\n'
                 'les trois autres tables ne regardaient pas.\n\n'
                 'GENEREE par `inventaire_contacts.py --ecrire`. Ne pas\n'
                 'editer a la main : la prochaine execution ecraserait la\n'
                 'correction, et le projet a deja paye une table editee dont\n'
                 'le producteur ne savait rien.\n\n'
                 'Le critere, son sens et le choix de la cle sont dans le\n'
                 'docstring du producteur. Chaque entree porte\n'
                 '(a, b, valeur totale, cle, critere) : `cle` vaut "groupe"\n'
                 'quand tous les membres du groupe de crenage droit de `a` ont\n'
                 'la meme gouttiere devant `b`, "glyphe" sinon ; `critere` dit\n'
                 'si la valeur atteint le plancher de jour ou si le couloir\n'
                 "d'Atkinson l'a bornee.\n\"\"\"\n\n")
        fh.write("PAIRES_CONTACTS = {\n")
        for lab in ("romain", "italique"):
            if lab not in tables:
                continue
            fh.write(f'    # --- {lab}\n')
            for mn, lignes in tables[lab].items():
                fh.write(f'    "{mn}": [\n')
                for a, b, val, cle, crit in lignes:
                    fh.write(f'        ("{a}", "{b}", {val}, "{cle}", '
                             f'"{crit}"),\n')
                fh.write("    ],\n")
        fh.write("}\n")
    print(f"  ecrit : {SORTIE}")


def main():
    lab = None
    if "--source" in sys.argv:
        lab = sys.argv[sys.argv.index("--source") + 1]
    if lab not in ("romain", "italique"):
        # Sans source nommee, rien n'est mesure ni ecrit. Rendre 0 ici faisait
        # passer un `--ecrire` sans `--source`, ou une faute de frappe, pour
        # une table regeneree a l'identique : mesure au soixante-huitieme
        # tour, piege 17. Non fait, donc 2.
        print(__doc__)
        print(f"NON FAIT : --source romain ou --source italique attendu, "
              f"recu {lab!r}. Rien n'est mesure, rien n'est ecrit.")
        return 2
    print(f"=== {lab}")
    tables = {lab: parcours(lab)}
    if "--ecrire" in sys.argv:
        # L'ecriture FUSIONNE avec ce qui existe deja pour l'autre source :
        # regenerer une source ne doit pas effacer l'autre, et le projet a
        # deja perdu une table ainsi.
        try:
            import paires_contacts as PC
            ancien = dict(PC.PAIRES_CONTACTS)
        except Exception:                                     # noqa: BLE001
            ancien = {}
        autre = "italique" if lab == "romain" else "romain"
        garde = {mn: [tuple(x) for x in v] for mn, v in ancien.items()
                 if mn not in tables[lab]}
        ecrire({lab: tables[lab], autre: garde} if garde else tables)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
