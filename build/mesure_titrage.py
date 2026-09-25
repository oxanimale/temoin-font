#!/usr/bin/env python3
"""Point ouvert 16, premiere moitie : combien de glyphes le titrage touche.

Le point 36 tranche que le O modifie reste hors du texte, donc le titrage est
entierement separable. Restait a mesurer l'etendue, parce que c'est elle qui
departage les deux voies du livrable :

  - un fichier statique separe porte tout le repertoire, quelle que soit
    l'etendue du geste ;
  - un jeu stylistique dans le variable existant ne porte que les glyphes
    modifies, MAIS il les porte en double, et un composite qui doit suivre son
    alternative demande sa propre alternative.

La question n'est donc pas "combien de glyphes portent une prescription" -- il
y en a quatorze, ce sont les derogations -- mais "combien de glyphes du
repertoire servi le reglage general modifierait". Le reglage general s'applique
a toute terminaison droite posee sur un alignement, ce qui n'est ni une liste
ni tout le jeu : c'est une propriete geometrique, donc ca se mesure.

Ce que ce script ne fait pas : il ne compile rien et ne pese rien. Le poids se
mesure a part, et dans une seule session, parce qu'un poids de fichier ne
traverse pas les sessions (point 16).

MESURE SUR LA SOURCE AMONT, et c'est un choix, pas une commodite. `loc_alignement`
filtre les segments dont la pente depasse 0.3 en valeur absolue, soit 16.7
degres : un segment deja coupe a 20 degres par le lot 2 n'est plus designe.
Mesurer sur `Temoin.glyphs` sous-compterait donc exactement les glyphes que le
projet a deja traites. Les 47 glyphes que le projet ajoute -- 44 petites
capitales, `narrownbspace`, et deux formes de zero -- sont classes a part : une
petite capitale a les contours propres de sa capitale a l'echelle du lot 3,
donc elle est touchee si et seulement si sa capitale l'est.

Trois comptes rendus separes, parce qu'ils ne coutent pas la meme chose :

  TOUCHE     le glyphe a ses propres contours et au moins une terminaison
             droite posee sur un alignement. Le titrage le redessine.
  HERITE     le glyphe est un composite dont au moins une base est touchee.
             Un statique le suit tout seul ; un jeu stylistique demande sa
             propre alternative, sinon le A accentue garderait le pied du
             texte quand le A nu prendrait celui du titrage.
  INTACT     ni l'un ni l'autre.

Le compte TOUCHE est donne deux fois : au critere permissif de
`lot4.loc_alignement`, puis restreint aux glyphes dont les segments designes
sont les memes dans les quatre masters. C'est le critere de stabilite du projet
(check_termes), et c'est le seul chiffre sur lequel on peut ecrire une table.

Et il est ventile par famille, parce que le reglage general ne distingue pas
une lettre d'une accolade : la regle est geometrique, donc elle attrape des
signes dont personne n'a demande qu'ils portent la signature. Ce partage n'est
pas une mesure, c'est une question a poser -- et c'est le vrai livrable de ce
script.
"""

import copy
import os
import sys
import unicodedata

import glyphsLib
from glyphsLib.classes import GSPath
from fontTools.ttLib import TTFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import coupe as K
import lot2 as L
import lot4 as Q

ICI = os.path.dirname(os.path.abspath(__file__))
# Le dossier que `subset.py` ecrit : `fonts/` dans le depot, `gabarits/fonts/`
# dans le dossier de travail. Point ouvert 116, soixante-et-onzieme tour.
from subset import DEST as SERVI

SOURCES = (
    ("romain", "/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs",
     os.path.join(ICI, "Temoin.glyphs"),
     os.path.join(SERVI, "Temoin.woff2")),
    ("italique", "/tmp/ahn/sources/AtkinsonHyperlegibleNext-Italic.glyphs",
     os.path.join(ICI, "Temoin-Italic.glyphs"),
     os.path.join(SERVI, "Temoin-Italic.woff2")),
)

LETTRES = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")

# Les trois perimetres candidats, nommes une fois et lus partout : le compte de
# glyphes et le poids compile doivent porter sur les memes ensembles, sinon les
# deux moities du point 16 ne se comparent pas.
PERIMETRES = (
    ("tout ce que la geometrie attrape",
     {"lettre", "signe", "chiffre", "chiffre ou fraction",
      "accent combinant"}),
    ("lettres et petites capitales seules", {"lettre"}),
    ("lettres, petites capitales et chiffres",
     {"lettre", "chiffre", "chiffre ou fraction"}),
)


def repertoire_servi(chemin):
    """Les noms de glyphes du binaire servi.

    `subset.py` passe --glyph-names, donc les noms sont ceux de la source et la
    comparaison est directe. Sans ce drapeau la table post passerait en 3.0 et
    ce script comparerait des noms inventes.
    """
    f = TTFont(chemin)
    return [g for g in f.getGlyphOrder() if g != ".notdef"]


def paths(layer):
    return [s for s in layer.shapes if isinstance(s, GSPath)]


def composants(layer):
    """Les glyphes references par ce calque.

    Piege : dans cette version de glyphsLib un GSComponent porte sa reference
    dans `.name`, et n'a pas d'attribut `.ref`. Un premier jet lisait `.ref` et
    rendait zero composant partout, donc zero heritier -- un nombre juste sorti
    d'une mesure fausse, la famille de piege que ce projet connait.
    """
    return [s.name for s in layer.shapes
            if not isinstance(s, GSPath) and getattr(s, "name", None)]


def terminaisons(layer, metr, pente=None):
    """Les segments designes par le reglage general, par contour.

    Meme appel que `couper_alignements` : les trois alignements horizontaux du
    master, et `loc_alignement` pour designer. La descendante n'y est pas, et
    c'est le fait connu du lot 3 -- le p, le q, le y, le j et le g se
    terminent sur un quatrieme alignement que le lot 4 ne traite pas.

    `pente` choisit le filtre d'orientation. `None` prend celui de l'ETENDUE,
    `lot4.PENTE_ETENDUE`, qui est ce que cette fonction doit mesurer : le
    perimetre arrete de 149 glyphes en est tire et il ne bouge pas. Passer
    `lot4.PENTE_BAS` repond a l'autre question, celle du GESTE -- quel segment
    `couper_alignements` designerait -- et c'est `check_perimetre` qui la pose,
    pour verifier qu'aucun glyphe ne recoit un geste hors de l'etendue.
    """
    trouve = []
    for j, p in enumerate(paths(layer)):
        segs = K.to_segs(p)
        idx = []
        for y in (metr["base"], metr["xh"], metr["cap"]):
            idx += (Q.loc_alignement(segs, y, orient="H") if pente is None
                    else Q.loc_alignement(segs, y, orient="H", pente=pente))
        if idx:
            trouve.append((j, tuple(sorted(set(idx)))))
    return tuple(trouve)


def appliquer_reglage(layer, nom, master, haut=None, journal=None, borne=None,
                      bas=None):
    """Applique le reglage general de titrage a un calque, sur place.

    `bas` FORCE le regime des terminaisons du BAS, comme `haut` force celui du
    haut. Il sert au controle et a la planche d'etat : `bas="bas"` rejoue ce que
    la geometrie DESIGNERAIT sans la prescription du glyphe, ce qui est le seul
    moyen de distinguer un glyphe dont la sortante est ECARTEE par une
    derogation ecrite d'un glyphe qui n'en a jamais eu. Sans lui, la section 8
    de `check_perimetre` devrait lire la table pour verifier la table, ce qui ne
    verifie rien -- meme raison que `HAUT_ATTENDU`, qui vit dans le controle.

    `borne` FORCE la borne haute de la dichotomie de la sortante, comme `haut`
    force le regime du haut, et pour la meme raison : une planche d'instruction
    doit pouvoir montrer deux etats cote a cote. `None` prend
    `lot4.BORNE_SORTIE`, 45 degres, qui est l'etat ecrit. Trente-sixieme tour.

    `haut` FORCE le regime des terminaisons du haut, celles que
    `sortantes="bas"` laisse en rentrante. Il ne sert qu'aux planches
    d'instruction, qui montrent plusieurs regimes cote a cote : "actuel"
    l'angle constant du lot 2, "aucune" le haut intact, "unites" la meme cible
    en unites que la sortante.

    Laisse a None -- ce que fait tout le reste du projet -- le regime est LU
    dans la prescription du glyphe, donc `lot4.DEFAUT["rentrantes"]` sauf
    exception ecrite. Nicolas a tranche "aucune" au trente-cinquieme tour, avec
    le r et le u pour seules exceptions. Le parametre vit ICI parce que c'est
    le seul endroit qui resout le reglage : la mesure de poids, le controle de
    perimetre et les planches suivent sans le savoir.

    Rend None sans rien toucher quand le glyphe est hors du perimetre arrete
    par Nicolas au trente-quatrieme tour, `lot4.HORS_TITRAGE`. L'exclusion est
    lue ICI et non chez chaque appelant : un perimetre applique a trois
    endroits finit par valoir trois perimetres.

    Un seul endroit resout les parametres -- la prescription du glyphe ou le
    reglage general, les alignements de `ETENDU` ou les trois par defaut, le
    depassement de casse -- et la planche d'instruction comme la mesure de
    poids passent par lui. Deux resolutions separees des memes parametres
    finiraient par montrer un etat et en mesurer un autre : c'est arrive au
    vingt-quatrieme tour, une planche composant `F+o` a -224 pendant que le
    garde-fou verifiait -124, les deux annoncant un accord.

    `nom` EST LE NOM DE LA BASE, JAMAIS CELUI DU DOUBLE `.ti`, et la fonction
    leve si on lui passe l'autre. Ce n'est pas une precaution de style : les
    quatre parametres du reglage sont indexes par nom -- `dans_le_titrage`,
    `prescription`, `ETENDU` et `depassement_pour` -- et AUCUN ne suit un
    suffixe. Mesure faite avant d'ecrire le quarantieme tour : `A.ti` passe
    `dans_le_titrage`, puis perd `exclure={"bg","hc"}` et `sortantes={"bd"}` du
    A, perd ses alignements restreints `('base','cap')`, et recoit le reglage
    general ; `AE.ti` et `E.ti` perdent leur derogation `sortantes=()`. Les
    douze derogations et les trente-quatre glyphes ecrits tomberaient donc en
    silence, et le titrage servi serait le reglage general partout -- une forme
    plausible que personne n'a validee.

    C'est la QUATRIEME fois que ce projet rencontre une table indexee par nom
    qui ne suit pas un changement de nom : `e.sc` au trente-huitieme tour, l'AE
    et l'Aring au trente-neuvieme, le double `.ti` ici. Les trois premieres ont
    ete trouvees par Nicolas a l'oeil sur une planche. Celle-ci leve.
    """
    if nom.endswith(".ti"):
        raise ValueError(
            f"appliquer_reglage a recu le nom du double, {nom!r}. "
            f"Passer le nom de la BASE, {nom[:-3]!r} : les prescriptions, "
            "ETENDU et depassement_pour sont indexes par nom et ne suivent "
            "aucun suffixe. Voir le docstring.")
    if not Q.dans_le_titrage(nom):
        return None
    metr = {"base": 0.0, "xh": master.xHeight, "cap": master.capHeight}
    pr = Q.prescription(nom)
    cles = Q.ETENDU.get(nom, ("base", "xh", "cap"))
    Q.couper_alignements(
        layer, pr.get("theta", Q.DEFAUT["theta"]),
        [metr[c] for c in cles], "H", journal, nom,
        cote=pr.get("cote", Q.DEFAUT["cote"]),
        exclure=pr.get("exclure", set()),
        sortantes=(pr.get("sortantes", Q.DEFAUT["sortantes"]) if bas is None
                   else bas),
        depassement=Q.depassement_pour(nom),
        pointes=pr.get("pointes"),
        rentrantes=(pr.get("rentrantes", Q.DEFAUT["rentrantes"])
                    if haut is None else
                    {"actuel": "angle", "aucune": "aucune",
                     "unites": "unites"}[haut]),
        borne_sortie=borne,
        # L'ANGLE D'ITALIQUE EST LU DANS LE MASTER, et c'est ici qu'il entre --
        # le seul endroit qui resout le reglage. `quadrant` desincline le
        # contour avant de classer, sinon le meme bout change de quadrant d'une
        # source a l'autre : point ouvert 65, ferme au trente-septieme tour.
        # Zero en romain, 12 degres dans les quatre masters italiques.
        angle_italique=float(getattr(master, "italicAngle", 0) or 0.0))
    return cles


def perimetre_arrete(cle_src=0):
    """Le perimetre du lot 4, resolu a UN SEUL endroit pour toute la chaine.

    Rend `None` quand la source amont ou le binaire servi manquent, et
    l'appelant doit alors se declarer NON MESURE au lieu de continuer sans
    titrage : `/tmp/ahn` a disparu sept fois dans ce projet.
    """
    lab, amont, _projet, binaire = SOURCES[cle_src]
    if not os.path.exists(binaire):
        return None
    r = analyser(lab, amont, binaire, verbeux=False)
    if r is None:
        return None
    return r["perimetres"]["le perimetre ARRETE, trente-quatrieme tour"]


def fusionner(font, perimetre=None, cle_src=0):
    """Applique le geste du lot 4 aux glyphes du perimetre, sur place.

    C'EST LA FUSION DU CORPS ET DU TITRAGE, et elle vit ICI pour que tout le
    monde l'applique par le meme code. Le quarantieme tour l'a appris cher : les
    deux generateurs de tables de paires, `inventaire_pieds` et
    `inventaire_bouts`, ne lisent pas `Temoin.glyphs` -- ils RECONSTRUISENT
    l'etat en appliquant le lot 2 et les approches. Tant que le lot 4 n'etait
    pas dans la chaine, l'etat reconstruit et l'etat servi coincidaient ; le
    jour de la fusion ils ont diverge, et les deux tables sont sorties
    IDENTIQUES d'une regeneration qui aurait du les changer. Elles mesuraient un
    dessin qui n'etait plus celui du livrable, sans que rien ne le dise.

    Rend `(touches, bougent)` ou `None` si le perimetre n'est pas resoluble.

    `HORS_FUSION` est lu ici et nulle part ailleurs : un perimetre applique a
    deux endroits vaut deux perimetres.
    """
    if perimetre is None:
        perimetre = perimetre_arrete(cle_src)
        if perimetre is None:
            return None
    presents = {g.name for g in font.glyphs}
    mid = {m.id: m for m in font.masters}
    journal, bouge, touches = [], set(), 0
    for nom in sorted(perimetre):
        if nom not in presents or nom in Q.HORS_FUSION:
            continue
        touches += 1
        for l in font.glyphs[nom].layers:
            if l.layerId not in mid:
                continue
            n0 = len(journal)
            appliquer_reglage(l, nom, mid[l.layerId], journal=journal)
            if any(isinstance(e[2], (int, float)) for e in journal[n0:]):
                bouge.add(nom)
    return touches, bouge


def etat_avant_fusion(cle_src=0):
    """L'etat que la chaine FUSIONNE : amont + lot 2 + approches.

    ELLE VIT ICI, a cote de `fusionner`, pour que l'etat d'AVANT et le geste qui
    s'y applique sortent du meme fichier. Le cinquante-septieme tour a mesure ce
    que coute de les separer : dix scripts construisaient leur propre point de
    depart, et deux familles de defauts en sont sorties.

    LE PREMIER, la DOUBLE COUPE -- ouvrir `Temoin.glyphs` et lui appliquer le
    geste, que la chaine y ecrit depuis le quarantieme tour. Etroit : sur l'etat
    servi du cinquante-sixieme tour, le `U` et le `u` seuls bougent de plus
    d'une unite, 8 glyphe-masters par source, jusqu'a 78,4 unites au romain et
    103,4 en italique. Voir `double_coupe`.

    LE SECOND, LE GESTE DEJA ECRIT -- le meme point de depart, mais sans que
    rien ne bouge. Sur un bout deja coupe, `appliquer_reglage` est idempotent,
    et ce qu'on mesure ensuite decrit la forme obtenue au lieu du geste. Large :
    33 des 118 noms du perimetre rendent une sortante differente selon la
    lecture -- le `U` 78,9 contre 56,0, le `V` 95,7 contre 60,0. C'est celui qui
    frappe les sections 11 et 12 de `check_perimetre`, et il ne se voit pas en
    regardant si quelque chose bouge. Voir `geste_deja_ecrit`.

    LE TROISIEME -- partir de l'amont BRUT, sans le lot 2 ni les approches. Pas
    de double coupe, mais le geste lui-meme n'est plus le bon : le lot 2 et les
    approches modifient 30 des 118 glyphes du perimetre AVANT la fusion, et le
    deplacement que `appliquer_reglage` produit differe alors sur 28
    glyphe-masters par source -- 43,8 unites sur le Y, 32,0 sur le M, 31,9 sur
    le f -- plus quatre topologies non comparables. C'est ce que cette fonction
    corrige directement.

    Rend `None` si la source amont est absente, jamais un etat plausible : le
    projet prefere un NON MESURE a un chiffre qui ne dit pas d'ou il vient.

    L'IMPORT D'`approches` EST LOCAL A DESSEIN : ce module ne l'importe pas en
    tete, et le remonter poserait un cycle le jour ou `approches` aurait besoin
    de celui-ci -- le message serait alors un ImportError a la racine de tout
    l'outillage. `lot2` et `glyphsLib`, eux, sont deja en tete de ce fichier :
    le premier jet les reimportait localement, ce qui MASQUAIT les noms du
    module par des noms locaux identiques et rendait les imports de tete morts.
    Corrige au cinquante-huitieme tour, trouve par la relecture deleguee. La
    justification ci-dessus ne vaut que pour `approches`, et elle le dit
    maintenant.
    """
    import approches as A

    _lab, amont, _projet, _binaire = SOURCES[cle_src]
    if not os.path.exists(amont):
        return None
    font = glyphsLib.GSFont(amont)
    L.appliquer_lot(font)
    A.appliquer(font)
    return font


def etat_fusionne(cle_src=0):
    """`etat_avant_fusion`, plus UNE application du geste. `None` si l'une des
    deux etapes ne peut pas se faire.

    C'est ce qu'une planche ou une mesure doit regarder quand elle veut decrire
    le titrage tel que la chaine l'ecrit. Lire `Temoin.glyphs` decrit le meme
    etat, mais on ne peut plus lui appliquer le geste pour l'observer -- et
    c'est precisement ce que dix scripts faisaient.
    """
    font = etat_avant_fusion(cle_src)
    if font is None:
        return None
    if fusionner(font, cle_src=cle_src) is None:
        return None
    return font


#: Sous cette valeur, un deplacement de noeud est du bruit d'arrondi et non un
#: geste. Mesure du cinquante-septieme tour : reappliquer le geste au projet
#: deplace le `A` de 0,3 unite et le `M` de 0,2, quand le `U` bouge de 44,0 et
#: le `u` de 78,4. Il n'y a rien entre les deux. Le nombre est ECRIT ICI et lu
#: par les deux mesures : un seuil recopie dans deux fonctions se corrige dans
#: une seule.
SEUIL_BRUIT = 0.5


def noms_mesurables(noms, cle_src=0):
    """Ceux des `noms` que `double_coupe` et `geste_deja_ecrit` regardent.

    Les deux mesures ecartent en silence le glyphe absent, celui de
    `lot4.HORS_FUSION` et celui que `dans_le_titrage` refuse. Un appelant qui
    leur passerait six noms tous ecartes recevrait une liste vide et la lirait
    comme un etat sain : c'est le piege du controle qui rend zero parce qu'il ne
    regarde pas, et il n'a ete vu qu'a la relecture de ce tour.

    Rend `(mesurables, ecartes)`, ou `None` si la source du projet manque.
    """
    import glyphsLib

    _lab, _amont, projet, _binaire = SOURCES[cle_src]
    if not os.path.exists(projet):
        return None
    font = glyphsLib.GSFont(projet)
    dedans, dehors = [], []
    for nom in sorted(set(noms)):
        if (font.glyphs[nom] is not None
                and nom not in Q.HORS_FUSION
                and Q.dans_le_titrage(nom)):
            dedans.append(nom)
        else:
            dehors.append(nom)
    return dedans, dehors


def double_coupe(noms, cle_src=0, seuil=SEUIL_BRUIT):
    """Les glyphe-masters ou REAPPLIQUER le geste au projet deplace encore.

    C'est le defaut le plus visible du cinquante-septieme tour, et le plus
    ETROIT des trois : mesure sur l'etat servi du tour precedent, seuls le `U`
    et le `u` bougent de plus d'une unite, 8 glyphe-masters par source, 78,4
    unites au romain et 103,4 en italique. Les autres noms du perimetre
    enregistrent une entree au journal pour moins d'une unite de deplacement --
    du bruit d'arrondi, que le dessin ne porte pas.

    **UN JOURNAL QUI ENREGISTRE N'EST PAS UN DESSIN QUI BOUGE.** Un premier jet
    de ce tour comptait les noms rendus par `fusionner`, qui les tient du
    journal, et annoncait 33 noms deplaces la ou il y en a deux. Le compte est
    fait ici sur les COORDONNEES.

    Rend `[(nom, master, deplacement)]` trie du plus grand au plus petit, ou
    `None` quand la source du projet manque -- un NON MESURE, pas un feu vert.
    Un appelant qui traiterait `None` comme une liste vide reintroduirait le
    defaut, donc la valeur est d'un autre type que le resultat normal.

    Une liste vide ne dit NI que l'appelant est sain, NI meme que le geste est
    idempotent : elle peut aussi ne porter que des noms ecartes -- glyphe
    absent, `lot4.HORS_FUSION`, hors titrage. Passe par `noms_mesurables` pour
    savoir sur quoi la mesure a vraiment porte. Et le defaut large est ailleurs,
    voir `geste_deja_ecrit`.
    """
    import glyphsLib

    _lab, _amont, projet, _binaire = SOURCES[cle_src]
    if not os.path.exists(projet):
        return None
    font = glyphsLib.GSFont(projet)
    mid = {m.id: m for m in font.masters}
    out = []
    for nom in sorted(set(noms)):
        g = font.glyphs[nom]
        if g is None or nom in Q.HORS_FUSION or not Q.dans_le_titrage(nom):
            continue
        for lay in g.layers:
            m = mid.get(lay.layerId)
            if m is None:
                continue
            avant = [(n.position.x, n.position.y)
                     for sh in lay.shapes
                     for n in (getattr(sh, "nodes", []) or [])]
            appliquer_reglage(lay, nom, m)
            apres = [(n.position.x, n.position.y)
                     for sh in lay.shapes
                     for n in (getattr(sh, "nodes", []) or [])]
            if len(avant) != len(apres):
                out.append((nom, m.name, float("inf")))
                continue
            d = max((max(abs(x1 - x0), abs(y1 - y0))
                     for (x0, y0), (x1, y1) in zip(avant, apres)), default=0.0)
            if d > seuil:
                out.append((nom, m.name, round(d, 1)))
    out.sort(key=lambda t: -t[2])
    return out


def geste_deja_ecrit(noms, cle_src=0, seuil=SEUIL_BRUIT):
    """Les glyphe-masters ou le PROJET porte deja la coupe que le geste pose.

    C'EST LE DEFAUT LARGE, et il ne se voit pas en reappliquant le geste. Sur un
    bout deja coupe, `appliquer_reglage` ne deplace rien -- il est idempotent --
    mais tout ce qu'on mesure ensuite decrit ce que le bout EST DEVENU, et non
    ce que le geste fait. Une section qui croit chiffrer un geste chiffre une
    forme. Mesure au cinquante-septieme tour, sur la sortante reellement posee :
    33 des 118 noms du perimetre rendent une longueur differente selon qu'on
    part du projet ou de l'etat d'avant fusion -- le `U` 78,9 contre 56,0, le
    `V` 95,7 contre 60,0, le `W` 92,4 contre 60,0.

    Le critere est la comparaison du dessin du projet a `etat_avant_fusion`, sur
    les seuls noms demandes. Rend `[(nom, master, ecart)]`, ou `None` si l'une
    des deux sources manque.

    LIMITE ECRITE : le projet porte aussi le lot 3, le bras du O, la pointe du
    circonflexe, les operateurs et la barre mediane, qu'`etat_avant_fusion` ne
    rejoue pas. Sur un nom que l'un de ces gestes touche, l'ecart rendu n'est
    pas entierement du a la fusion. Le refus s'en accommode -- il demande
    seulement de savoir que le projet n'est pas l'etat d'avant -- mais un
    appelant qui chiffrerait la fusion a partir de ce nombre se tromperait.
    """
    import glyphsLib

    _lab, amont, projet, _binaire = SOURCES[cle_src]
    if not (os.path.exists(projet) and os.path.exists(amont)):
        return None
    av = etat_avant_fusion(cle_src)
    if av is None:
        return None
    font = glyphsLib.GSFont(projet)
    mid = {m.id: m for m in font.masters}
    mia = {m.id: m.name for m in av.masters}

    def pts(lay):
        return [(n.position.x, n.position.y)
                for sh in lay.shapes
                for n in (getattr(sh, "nodes", []) or [])]

    ref = {}
    for g in av.glyphs:
        for lay in g.layers:
            if lay.layerId in mia:
                ref[(g.name, mia[lay.layerId])] = pts(lay)

    out = []
    for nom in sorted(set(noms)):
        g = font.glyphs[nom]
        if g is None or nom in Q.HORS_FUSION or not Q.dans_le_titrage(nom):
            continue
        for lay in g.layers:
            m = mid.get(lay.layerId)
            if m is None:
                continue
            a = ref.get((nom, m.name))
            b = pts(lay)
            if a is None:
                continue
            if len(a) != len(b):
                out.append((nom, m.name, float("inf")))
                continue
            d = max((max(abs(x1 - x0), abs(y1 - y0))
                     for (x0, y0), (x1, y1) in zip(a, b)), default=0.0)
            if d > seuil:
                out.append((nom, m.name, round(d, 1)))
    out.sort(key=lambda t: -t[2])
    return out


def _ligne_ecart(t):
    """Une entree de `double_coupe` ou `geste_deja_ecrit`, imprimee.

    L'infini n'est pas une distance, c'est le marqueur des deux dessins dont le
    nombre de noeuds differe -- le `O` en est un, son bras n'etant pas rejoue
    par `etat_avant_fusion`. Imprime comme un nombre, il annoncait "jusqu'a inf
    unites d'ecart", ce qui se lit comme une mesure. Une etiquette est une
    mesure, et le projet a paye ce defaut assez souvent pour le dire ici.
    """
    nom, master, d = t
    if d == float("inf"):
        return "%s %s topologie differente" % (nom, master)
    return "%s %s %.1f u" % (nom, master, d)


def _ampleur(entrees):
    """Le plus grand ecart CHIFFRABLE d'une liste, en toutes lettres.

    Rend une chaine vide quand la liste ne porte que des topologies
    differentes : il n'y a alors aucune unite a annoncer.
    """
    finis = [d for _n, _m, d in entrees if d != float("inf")]
    topo = len(entrees) - len(finis)
    bouts = []
    if finis:
        bouts.append("jusqu'a %.1f unites d'ecart avec l'etat d'avant fusion"
                     % max(finis))
    if topo:
        bouts.append("%d ou les deux dessins n'ont pas le meme nombre de "
                     "noeuds" % topo)
    return (", " + ", dont ".join(bouts)) if bouts else ""


def refuser_si_perimee(qui, noms, cle_src=0):
    """Le refus ecrit UNE fois, appele par les planches qui le doivent.

    Trois planches portaient le meme defaut au cinquante-septieme tour et
    auraient recopie le meme refus. Un refus recopie trois fois se corrige deux
    fois : le tour precedent l'a paye sur la hauteur des petites capitales,
    recopiee au lieu d'etre lue.

    Le refus SE MESURE, il ne lit pas un numero de tour. Il porte sur le defaut
    LARGE -- le projet porte deja la coupe -- et non sur la double coupe, qui ne
    frappe que le `U` et le `u` et laisserait passer tout le reste.

    Rend `True` quand l'appelant doit s'arreter, apres avoir imprime pourquoi.
    """
    mesurables = noms_mesurables(noms, cle_src=cle_src)
    ec = geste_deja_ecrit(noms, cle_src=cle_src)
    dc = double_coupe(noms, cle_src=cle_src)
    if mesurables is None or ec is None or dc is None:
        print("!! une source manque : le refus NE PEUT PAS se mesurer, donc "
              "rien n'est produit. Ce n'est pas un feu vert.")
        return True
    dedans, dehors = mesurables
    if not dedans:
        print("!! aucun des %d noms demandes n'est mesurable -- absent de la "
              "source, dans `lot4.HORS_FUSION`, ou hors titrage : %s"
              % (len(dehors), " ".join(dehors[:8])))
        print("   Le refus N'A RIEN MESURE, donc il ne dit rien. Un appelant "
              "qui le lirait comme un feu vert se tromperait.")
        return True
    if dehors:
        print("   note : %d nom%s hors mesure, qui n'entre%s dans aucun compte "
              "-- %s" % (len(dehors), "s" if len(dehors) > 1 else "",
                         "nt" if len(dehors) > 1 else "",
                         " ".join(dehors[:8])))
    if not ec:
        return False
    print("!! %s PERIMEE : elle ouvre `Temoin.glyphs` et y mesure le geste, "
          "que la chaine ecrit dans cette source depuis le quarantieme tour."
          % qui)
    print("   MESURE : %d glyphe-masters y portent deja la coupe%s."
          % (len(ec), _ampleur(ec)))
    print("   " + ", ".join(_ligne_ecart(t) for t in ec[:6]))
    if dc:
        print("   Et sur %d d'entre eux le geste coupe une SECONDE fois%s : %s"
              % (len(dc), _ampleur(dc),
                 ", ".join("%s %s" % (n, m) for n, m, _ in dc[:4])))
    else:
        print("   Le geste y est idempotent, donc rien ne bouge et l'image "
              "sortirait sans erreur : c'est ce qui rend ce defaut couteux.")
    print("   Pour rejouer : `mesure_titrage.etat_avant_fusion` puis le geste "
          "UNE fois, ou `etat_fusionne` pour l'etat servi reconstruit.")
    return True


def doubler_en_memoire(font, perimetre):
    """Ajoute a `font` un double `nom.ti` pour chaque nom du perimetre present.

    Ne coupe rien : le double sort avec le dessin de sa base, et c'est
    `appliquer_reglage` qui fait ensuite le titrage, sur le NOM DE LA BASE.

    Rend `(dedans, manquants)`, les noms doubles et ceux que le perimetre
    demande sans que la source les porte.

    Un composite double reference le double de sa base quand celle-ci est dans
    le perimetre. Sans ce remappage, `Aacute.ti` porterait le pied du TEXTE
    pendant que `A.ti` porte celui du titrage : la substitution aurait lieu et
    ne changerait rien, ce qui est le pire des trois etats possibles -- une
    feature vivante sur un dessin faux. Les 43 composites du perimetre en
    dependent entierement, ils n'ont aucun contour propre.

    `copy.deepcopy` sur un GSGlyph suit `parent` et recopie TOUTE la fonte :
    le glyphe se detache avant, sinon 112 doubles recopient 112 fois 451
    glyphes. Le script n'echoue pas, il rame -- donc rien ne dit ce qui se
    passe. Piege tombe deux fois dans ce projet.

    Cette fonction est partagee par la chaine de production, `make_temoin`, et
    par la mesure de poids, `mesure_poids_titrage`. Deux codes qui doublent
    finiraient par doubler deux choses differentes, et c'est la mesure de poids
    qui deciderait d'un livrable qu'elle ne decrit plus.
    """
    perimetre = set(perimetre)
    presents = {g.name for g in font.glyphs}
    dedans = sorted(n for n in perimetre if n in presents)
    manquants = sorted(n for n in perimetre if n not in presents)

    for nom in dedans:
        source = font.glyphs[nom]
        parent = source.parent
        source.parent = None
        g = copy.deepcopy(source)
        source.parent = parent
        g.name = nom + ".ti"
        g.unicodes = []
        g.export = True
        for l in g.layers:
            for sh in l.shapes:
                ref = getattr(sh, "name", None)
                if ref and not hasattr(sh, "nodes") and ref in perimetre:
                    sh.name = ref + ".ti"
        font.glyphs.append(g)
    return dedans, manquants


def famille(nom):
    """Lettre, chiffre, accent combinant, ou signe.

    Le partage se lit sur le nom de glyphe et non sur le cmap, parce que les
    variantes a suffixe (.tf, .sc, .case) n'ont pas toutes un code point.
    """
    base = nom.split(".")[0]
    if base.endswith("comb"):
        return "accent combinant"
    if nom.endswith(".sc"):
        return "petite capitale"
    if base in LETTRES or len(base) == 1 and base.isalpha():
        return "lettre"
    for essai in (base, base.capitalize()):
        try:
            c = unicodedata.lookup({
                "zero": "DIGIT ZERO", "one": "DIGIT ONE", "two": "DIGIT TWO",
                "three": "DIGIT THREE", "four": "DIGIT FOUR",
                "five": "DIGIT FIVE", "six": "DIGIT SIX",
                "seven": "DIGIT SEVEN", "eight": "DIGIT EIGHT",
                "nine": "DIGIT NINE"}[base])
            return "chiffre"
        except KeyError:
            break
    if base in ("AE", "OE", "ae", "oe", "germandbls", "Eth", "eth", "Thorn",
                "thorn", "idotless", "jdotless", "florin", "Aring", "aring"):
        return "lettre"
    if base.endswith("superior") or base in ("onehalf", "onequarter",
                                             "threequarters", "fraction",
                                             "percent", "perthousand"):
        return "chiffre ou fraction"
    return "signe"


def analyser(lab, amont, binaire, verbeux=True):
    """Classe le repertoire servi et rend les trois perimetres.

    Rendue reutilisable pour `mesure_poids_titrage.py`, qui a besoin des memes
    ensembles pour doubler les glyphes : deux calculs separes de la meme
    etendue finiraient par diverger sans que rien ne le dise.
    """
    if not os.path.exists(amont):
        print(f"!! source absente : {amont}")
        print("   Ne rien conclure d'un controle qui n'a pas lu sa source.")
        return None
    with open(amont, encoding="utf-8") as fh:
        font = glyphsLib.load(fh)
    mid = {m.id: m for m in font.masters}
    servi = repertoire_servi(binaire)

    etat = {}
    for nom in servi:
        g = font.glyphs[nom]
        if g is None:
            continue
        vus, comps, a_contours = set(), set(), False
        for l in g.layers:
            if l.layerId not in mid:
                continue
            m = mid[l.layerId]
            metr = {"base": 0.0, "xh": m.xHeight, "cap": m.capHeight}
            if paths(l):
                a_contours = True
                vus.add(terminaisons(l, metr))
            comps |= set(composants(l))
        etat[nom] = dict(vus=vus, comps=comps, contours=a_contours)

    touche, stable, instable = [], [], []
    for nom in servi:
        e = etat.get(nom)
        if not e or not e["contours"]:
            continue
        if not any(v for v in e["vus"]):
            continue
        touche.append(nom)
        (stable if len(e["vus"]) == 1 else instable).append(nom)
    vus_touches = set(touche)

    def base_touchee(nom, vu=None):
        vu = set() if vu is None else vu
        if nom in vu:
            return False
        vu.add(nom)
        if nom in vus_touches:
            return True
        e = etat.get(nom)
        if not e:
            # hors du servi : on descend quand meme, un composite peut
            # referencer une base que le sous-ensemble ne sert pas
            g = font.glyphs[nom]
            if g is None:
                return False
            for l in g.layers:
                if l.layerId not in mid:
                    continue
                m = mid[l.layerId]
                metr = {"base": 0.0, "xh": m.xHeight, "cap": m.capHeight}
                if paths(l) and terminaisons(l, metr):
                    return True
                if any(base_touchee(c, vu) for c in composants(l)):
                    return True
            return False
        return any(base_touchee(c, vu) for c in e["comps"])

    herite, intact = [], []
    for nom in servi:
        e = etat.get(nom)
        if not e or nom in vus_touches:
            continue
        (herite if any(base_touchee(c) for c in e["comps"])
         else intact).append(nom)

    # Les glyphes que le projet ajoute : absents de l'amont, donc classes a
    # part. Une petite capitale porte les contours propres de sa capitale a
    # l'echelle du lot 3, donc elle est touchee si et seulement si sa
    # capitale l'est. Le reste est une espace ou une forme de zero.
    ajoutes = [n for n in servi if n not in etat]
    pc_touchees, pc_intactes, autres_ajouts = [], [], []
    for nom in ajoutes:
        if not nom.endswith(".sc"):
            autres_ajouts.append(nom)
            continue
        base = nom[:-3]
        cap = base.upper() if len(base) == 1 else {
            "ae": "AE", "oe": "OE", "agrave": "Agrave",
            "acircumflex": "Acircumflex", "adieresis": "Adieresis",
            "ccedilla": "Ccedilla", "eacute": "Eacute",
            "egrave": "Egrave", "ecircumflex": "Ecircumflex",
            "edieresis": "Edieresis", "icircumflex": "Icircumflex",
            "idieresis": "Idieresis", "ocircumflex": "Ocircumflex",
            "odieresis": "Odieresis", "ugrave": "Ugrave",
            "ucircumflex": "Ucircumflex", "udieresis": "Udieresis",
            "ydieresis": "Ydieresis"}.get(base, base.upper())
        (pc_touchees if base_touchee(cap) else pc_intactes).append(nom)

    ecrits = set(Q.ETENDU) | set(Q.PRESCRIPTIONS)
    nouveaux = sorted(n for n in touche if n not in ecrits)

    # Trois perimetres, parce que le reglage general n'est pas une intention :
    # c'est une propriete geometrique, et elle attrape des signes dont personne
    # n'a demande qu'ils portent la signature. Le chiffre qui departage les
    # deux voies du livrable depend du perimetre retenu, donc les trois sont
    # calcules et rendus a l'appelant.
    def perimetre(familles):
        noms = {n for n in touche if famille(n) in familles}
        # les heritiers ne suivent que si leur base est dans le perimetre
        h = {n for n in herite
             if any(c in noms or famille(c) in familles
                    for c in etat[n]["comps"])}
        pc = set(pc_touchees) if "lettre" in familles else set()
        return noms | h | pc

    pers = {lib: perimetre(fams) for lib, fams in PERIMETRES}

    # Le perimetre ARRETE, et non plus candidat : les trois ci-dessus etaient
    # les voies posees a Nicolas au trente-quatrieme tour, celui-ci est ce
    # qu'il a tranche. Les heritiers sont recalcules contre l'ensemble GARDE et
    # non contre l'ensemble attrape : exclure `macroncomb` doit sortir le
    # macron d'espacement du perimetre, puisqu'il n'est qu'un composite de la
    # marque -- un heritier compte contre sa base reelle, pas contre l'ancienne.
    gardes = {n for n in touche if Q.dans_le_titrage(n)}

    def suit_un_garde(nom, vu=None):
        vu = set() if vu is None else vu
        if nom in vu:
            return False
        vu.add(nom)
        if nom in gardes:
            return True
        e = etat.get(nom)
        if not e:
            return False
        return any(suit_un_garde(c, vu) for c in e["comps"])

    arrete = set(gardes)
    arrete |= {n for n in herite if suit_un_garde(n)}
    # Les petites capitales suivent en entier, et c'est verifie plutot que
    # suppose : aucune capitale n'est ecartee du perimetre, donc aucune petite
    # capitale ne peut l'etre. Le jour ou une capitale entrerait dans
    # HORS_TITRAGE, cette ligne mentirait, donc elle leve.
    cap_ecartees = sorted(n for n in Q.HORS_TITRAGE
                          if famille(n) == "lettre" and n[:1].isupper())
    if cap_ecartees:
        raise ValueError(
            "une capitale est hors du titrage, les petites capitales ne "
            f"peuvent plus suivre en bloc : {' '.join(cap_ecartees)}")
    # LES PETITES CAPITALES PASSENT PAR `dans_le_titrage` COMME LE RESTE, et
    # non par un `|=` qui les ajoutait en bloc. Nicolas les a ecartees au
    # trente-huitieme tour, point 67 : la regle vit dans `lot4`, et ce filtre
    # est ce qui la fait arriver jusqu'au perimetre. Sans lui le compte
    # resterait a 149 alors que le geste ne les touche plus, et les deux
    # moities du point 16 cesseraient de porter sur le meme ensemble.
    arrete |= {n for n in pc_touchees if Q.dans_le_titrage(n)}
    pers["le perimetre ARRETE, trente-quatrieme tour"] = arrete

    dire = print if verbeux else (lambda *a, **k: None)
    dire(f"=== {lab} : {len(servi)} glyphes servis hors .notdef, "
          f"{len(mid)} masters")
    dire(f"  presents dans l'amont : {len(etat)} ; "
          f"ajoutes par le projet : {len(ajoutes)}")
    dire()
    dire(f"  TOUCHE   contours propres + terminaison sur un alignement : "
          f"{len(touche)}")
    dire(f"     segments identiques dans les {len(mid)} masters : "
          f"{len(stable)}")
    dire(f"     segments differents selon le master              : "
          f"{len(instable)}")
    dire(f"  HERITE   composite dont une base est touchee : {len(herite)}")
    dire(f"  INTACT                                       : {len(intact)}")
    dire(f"  ---> a redessiner ou a doubler : {len(touche) + len(herite)}"
          f" sur {len(etat)} glyphes d'amont servis")
    dire()
    dire(f"  petites capitales touchees par leur capitale : "
          f"{len(pc_touchees)} sur {len(pc_touchees) + len(pc_intactes)}")
    dire(f"  autres ajouts du projet, hors du geste : "
          f"{' '.join(sorted(autres_ajouts))}")
    dire()
    tot_touche = len(touche) + len(herite) + len(pc_touchees)
    dire(f"  ETENDUE TOTALE du titrage sur le repertoire servi : "
          f"{tot_touche} / {len(servi)} glyphes "
          f"({100.0 * tot_touche / len(servi):.0f} %)")
    dire()
    dire("  ventilation du compte TOUCHE par famille :")
    fam = {}
    for nom in touche:
        fam.setdefault(famille(nom), []).append(nom)
    for f_, noms in sorted(fam.items(), key=lambda kv: -len(kv[1])):
        dire(f"     {f_:20s} {len(noms):3d}   {' '.join(sorted(noms))}")
    dire()
    dire("  perimetres, les trois candidats puis celui qui est ecrit :")
    # LE RAPPORT SE PREND SUR LE REPERTOIRE DE TEXTE, DOUBLES EXCLUS. Depuis
    # que le titrage est compile, le binaire servi porte ses propres 112
    # doubles : rapporter le perimetre a 423 glyphes au lieu de 311 faisait
    # tomber le chiffre de 36 a 27 % sans qu'aucune decision ait change, et
    # la grandeur cessait de dire ce que son etiquette annonce -- quelle part
    # du texte le titrage touche. Une etiquette est une mesure.
    base_servie = [n for n in servi if not n.endswith(".ti")]
    for lib in [l for l, _ in PERIMETRES] + [
            "le perimetre ARRETE, trente-quatrieme tour"]:
        dire(f"     {lib:44s} {len(pers[lib]):3d} glyphes "
             f"({100.0 * len(pers[lib]) / len(base_servie):.0f} % du texte "
             f"servi, {len(base_servie)} glyphes)")
    dire(f"     ecartes par lot4.HORS_TITRAGE : "
         f"{len(pers['tout ce que la geometrie attrape'] - arrete)} glyphes")
    dire()
    dire(f"  deja ecrits (ETENDU + PRESCRIPTIONS) : "
          f"{len([n for n in ecrits if n in servi])}")
    dire(f"  touches que rien n'a encore ecrit    : {len(nouveaux)}")
    dire(f"  INSTABLES, a designer a la main comme au lot 2 : "
          f"{' '.join(sorted(instable))}")
    dire(f"  HERITIERS : {' '.join(sorted(herite))}")
    dire()

    return dict(servi=servi, touche=touche, stable=stable, instable=instable,
                herite=herite, intact=intact, pc_touchees=pc_touchees,
                perimetres=pers)


def main():
    for lab, amont, _projet, binaire in SOURCES:
        analyser(lab, amont, binaire, verbeux=True)


if __name__ == "__main__":
    main()
