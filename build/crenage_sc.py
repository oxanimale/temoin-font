#!/usr/bin/env python3
"""Temoin, point 93 : le crenage des petites capitales.

Ouvert au cinquante-deuxieme tour par trois reserves de Nicolas sur `KO` et sur
l'Æ de `CÆCUM`, mesure et tranche au cinquante-cinquieme, CORRIGE au
cinquante-sixieme.

LE FAIT QUI DECIDE. Les 44 `.sc` ne portaient AUCUNE paire de crenage, prouve
sur les huit masters et 1 936 paires shapees, quand les capitales en portent 553
a 646 selon le master. L'ecart de blanc entre une paire de petites capitales et
la meme paire de capitales reduite se decompose exactement :

    W_sc - s x W_cap  =  2 x APPROCHE_SC  -  s x crenage capitale

verifie a moins d'une unite sur la plainte elle-meme : au Regular, `KO` paie
58,8 unites de blanc en trop et `KI` 25,9 ; la difference de 32,9 vaut le
crenage capitale de `KO` ramene a l'echelle, 33,5.

**L'approche regle donc un NIVEAU et le crenage absent fait l'IRREGULARITE.**
Les 28 unites d'approche tombent sur toutes les paires de la meme facon et
l'oeil s'y fait ; ce qui se voit est l'ecart entre `KO` et `KI`. Reduire
`APPROCHE_SC` les resserrerait du meme montant et laisserait `KO` deux fois plus
lache que `KI`. C'est pourquoi ce module ecrit un crenage et ne touche pas a
l'approche.

LE RAPPORT EST CELUI DE LA DERIVATION, pas un nombre choisi. Nicolas a retenu
« 86 % » sur `tour55-etats-sc.html`, qui posait 0, 50, 86 et 100 % ; la valeur
ecrite est `HAUTEUR_SC / HAUTEUR_CAP`, soit 0,859281, et non 0,86. L'ecart vaut
0,125 unite sur la plus forte paire du repertoire, `F+Æ` a -244, donc moins que
l'arrondi entier d'une table `glyf`. Le rapport est PASSE en parametre par
`make_temoin` au lieu d'etre recopie ici : deux definitions du meme nombre
finissent par vivre dans deux fichiers, et le projet l'a paye sur `quadrant`.

LE MODULE ECRIT UNE IMAGE DE LA TABLE CAPITALE, ET C'EST LA CORRECTION DU POINT
97. Le premier jet parcourait un representant par couple de classes et lisait la
valeur capitale par `approches.kern`, qui resout la cle LA PLUS SPECIFIQUE : il
lisait donc l'EXCEPTION glyphe-glyphe du representant et l'ecrivait sur le GROUPE
ENTIER. `check_crenage_sc` a rendu 14 paires sous le plancher de jour, dont
`q.sc+ae.sc` a -15,4 en ExtraBold italique -- un contact reel, confirme par
`balayage_lot4b.couloir_exact` a la decimale. La cause mesuree au cinquante-
sixieme tour est plus large que le point 97 ne l'annoncait : **8 a 23 valeurs par
master** venaient d'une exception, et pas seulement le `C+Æ` a -50 du tour
precedent -- `A+X` a +47, `F+A` a -142, `E+C` a -76, `B+S` a -22, `C+C` a -50 y
etaient aussi, donc les reglages des diagonales et du F du cinquante-quatrieme
tour se propageaient a des groupes entiers.

Le module ne LIT donc plus une valeur : il MAPPE une cle. Chaque entree du
crenage capitale dont les deux cles ont une image en petites capitales est
recopiee au rapport, sous la cle image -- un nom de groupe devient le meme nom
prefixe, un nom de glyphe devient le `.sc` qui en derive. Les `.sc` heritent
ainsi de la structure capitale EXACTE, groupes et exceptions, et il n'y a plus
de resolution en jeu : une cle ecrite est l'image d'une cle lue. C'est aussi ce
qui borne le miroir a la bonne casse, et c'est mesure : les 21 classes droites et
15 gauches des 44 capitales ne sont portees par AUCUNE minuscule -- les seuls
autres porteurs sont des capitales accentuees, plus `Delta`, `Germandbls`, `IJ`,
`Eth`, `Hbar` et `_Q.tail`.

LES GROUPES SONT LA CONDITION D'ECHELLE, et c'est mesure. Le crenage capitale
des 44 bases tient en 120 a 124 entrees de GROUPE par master ; les 553 paires
mesurees au shaping en sont l'expansion. Sans groupes propres, la meme table
demanderait une entree par paire. Les `.sc` recoivent donc la partition exacte
de leurs capitales -- 21 cles droites, 15 cles gauches -- sous des noms
prefixes, pour que les deux casses ne partagent aucune classe : partager
reviendrait a donner 100 % aux petites capitales.

PLACE DANS LA CHAINE : APRES `lot3`, qui cree les `.sc`, et donc apres
`approches.appliquer`. Les valeurs lues sont celles de l'etat REGLE, reglage de
l'Æ compris, et les petites capitales en heritent au rapport. C'est voulu : le
blanc devant l'Æ existe aussi a l'echelle reduite. Elles heritent de meme des
decisions prises sur le F et sur les diagonales au cinquante-quatrieme tour, ce
qui a ete mesure et dit avant que le geste ne soit pris.
"""

import approches as A
import lot3

#: Le prefixe des groupes de crenage des petites capitales. Il les separe des
#: classes de capitales : sans lui, `a.sc` et `A` partageraient leurs valeurs et
#: le rapport vaudrait 1.
PREFIXE = "sc"

#: LES PAIRES QUE LE PLANCHER DE JOUR BORNE, en unites A RENDRE sur la valeur
#: que le rapport donnerait.
#:
#: Le crenage FERME, donc il peut fermer trop. Balaye sur les huit masters,
#: gouttiere pleine contre `approches.JOUR_MIN`.
#:
#: Ecrites en EXCEPTION glyphe-glyphe, donc par-dessus la valeur de groupe ou
#: par-dessus l'exception heritee : borner le groupe toucherait toutes les
#: paires de ses membres, quand une seule le demande.
#:
#: **REMESUREE au cinquante-sixieme tour, apres la correction du point 97** :
#: les valeurs du tour precedent avaient ete relevees sur un etat ou des
#: exceptions se propageaient a des groupes entiers. Sur l'etat corrige, la
#: section 4 de `check_crenage_sc` ne trouve plus qu'UNE paire sous le plancher,
#: `r.sc+ae.sc` a 21,6 unites a l'ExtraBold des deux sources -- contre quatorze
#: avant la correction, dont un contact reel a -15,4. Le rendu vaut 3 et non
#: 2,4 : l'arrondi va vers le HAUT, la contrainte etant un plancher a franchir,
#: comme la table des pieds et a l'inverse de celle des bouts.
#:
#: La table reste ecrite a la main et c'est la section 4 qui la tient : elle
#: remesure la gouttiere pleine de toutes les paires crenees a chaque execution,
#: donc une valeur devenue fausse se voit. Une liste ecrite a la main ne se
#: perime en silence que lorsque rien ne la remesure.
BORNES_SC = {
    "ExtraBold": {("r.sc", "ae.sc"): 3.0},
    "ExtraBold Italic": {("r.sc", "ae.sc"): 3.0},
}


def jeu(font):
    """Les petites capitales presentes, avec la capitale dont `lot3` les derive.

    La correspondance vient de `lot3.jeu` et n'est pas rededuite ici : deux
    definitions du meme lien finiraient par vivre dans deux fichiers, et
    `quadrant` l'a deja coute au projet. Un `.sc` annonce mais absent de la
    source leve, au lieu d'etre ecarte en silence : une liste qui se vide sans
    le dire est le defaut le plus tenace de ce projet.
    """
    out = []
    for nom, cap, _bas, _haut in lot3.jeu(font):
        if font.glyphs[nom] is None:
            raise ValueError("crenage_sc : %s annonce par lot3.jeu et absent "
                             "de la source -- appeler APRES lot3." % nom)
        if font.glyphs[cap] is None:
            raise ValueError("crenage_sc : %s n'a pas sa capitale %s"
                             % (nom, cap))
        out.append((nom, cap))
    return out


def classes(font):
    """Ce qu'il faut pour mapper une cle : la table capitale -> `.sc`, et les
    deux jeux de noms de classes que les 44 capitales portent.

    `gd` porte les groupes DROITS, ceux que `@MMK_L_` nomme, et `gg` les
    GAUCHES, ceux de `@MMK_R_`. L'inversion est celle de Glyphs et elle est
    reecrite ici parce qu'elle se lit a l'envers : la cle de GAUCHE d'une paire
    nomme le groupe de DROITE de son premier membre.
    """
    paires = jeu(font)
    caps = {cap: nom for nom, cap in paires}
    gd = {font.glyphs[c].rightKerningGroup for c in caps} - {None}
    gg = {font.glyphs[c].leftKerningGroup for c in caps} - {None}
    return caps, gd, gg


def image_cle(cle, cote, caps, gd, gg):
    """L'image en petites capitales d'une cle de crenage capitale, ou None.

    Un nom de GROUPE devient le meme nom prefixe ; un nom de GLYPHE devient le
    `.sc` qui en derive. Une cle sans image -- le groupe d'une minuscule, une
    capitale dont aucune petite capitale ne derive, un signe -- n'est pas mappee,
    et **c'est ce filtre seul qui borne le miroir aux paires de capitale a
    capitale**. Il ne repose pas sur la casse d'un nom, qui n'est pas une
    propriete typographique dans ce projet, mais sur l'appartenance mesuree aux
    classes des 44 bases.

    `cote` vaut "droite" pour la premiere cle de la paire et "gauche" pour la
    seconde, dans le vocabulaire de `classes`.
    """
    if cle.startswith("@MMK_L_") or cle.startswith("@MMK_R_"):
        pref, nom = cle[:7], cle[7:]
        connu = (nom in gd) if cote == "droite" else (nom in gg)
        return (pref + PREFIXE + nom) if connu else None
    return caps.get(cle)


def poser_groupes(font, journal=None):
    """Donne a chaque `.sc` la partition de crenage de sa capitale.

    Rend (nombre de glyphes touches, cles droites, cles gauches).
    """
    journal = journal if journal is not None else []
    droites, gauches, n = set(), set(), 0
    for nom, haut in jeu(font):
        g, cap = font.glyphs[nom], font.glyphs[haut]
        d = cap.rightKerningGroup
        ga = cap.leftKerningGroup
        g.rightKerningGroup = (PREFIXE + d) if d else None
        g.leftKerningGroup = (PREFIXE + ga) if ga else None
        if d:
            droites.add(PREFIXE + d)
        if ga:
            gauches.add(PREFIXE + ga)
        n += 1
        journal.append(("groupe sc", nom, haut, d, ga))
    return n, sorted(droites), sorted(gauches)


def _ecrire_cle(font, master_id, k1, k2, valeur):
    """Pose une valeur sur une cle NOMMEE, sans la choisir.

    `approches.ecrire_kern` prend une PAIRE DE GLYPHES et deduit la cle a
    employer ; ce module, lui, connait deja la cle, puisqu'elle est l'image
    d'une cle capitale. Passer par la deduction reintroduirait exactement le
    defaut que le point 97 corrige : une cle ecrite qui n'est pas celle qu'on a
    lue. Le garde d'`ecrire_kern` -- refuser d'ecrire sur un groupe quand une
    cle plus specifique existe -- n'a pas d'objet ici, la structure ecrite etant
    l'image exacte de la structure lue : la ou une exception capitale existe,
    son image existe aussi.
    """
    font.kerning.setdefault(master_id, {}).setdefault(k1, {})[k2] = valeur


def appliquer(font, rapport, journal=None):
    """Ecrit le crenage des petites capitales. Modifie `font`.

    `rapport` vient de `make_temoin` : `HAUTEUR_SC / HAUTEUR_CAP`.

    Rend (glyphes groupes, entrees de groupe, exceptions, cles droites,
    cles gauches). La signature a CHANGE au cinquante-sixieme tour, et c'est
    voulu : un appelant qui compte encore deux nombres doit lever plutot que
    continuer a imprimer un total qui ne dit plus la meme chose.
    """
    journal = journal if journal is not None else []
    n, droites, gauches = poser_groupes(font, journal)
    caps, gd, gg = classes(font)

    n_grp = n_exc = 0
    for m in font.masters:
        K = font.kerning.setdefault(m.id, {})
        # UN INSTANTANE, parce qu'on ecrit dans la table qu'on parcourt. Les
        # entrees `.sc` que la boucle pose n'ont de toute facon aucune image --
        # ni `scO` ni `c.sc` ne sont dans les classes des capitales -- donc le
        # miroir est idempotent ; l'instantane est la pour le parcours, pas pour
        # la justesse.
        lues = [(k1, k2, v) for k1, sous in K.items() for k2, v in sous.items()]
        for k1, k2, v in lues:
            i1 = image_cle(k1, "droite", caps, gd, gg)
            i2 = image_cle(k2, "gauche", caps, gd, gg)
            if i1 is None or i2 is None:
                continue
            val = round(float(v) * rapport, 1)
            _ecrire_cle(font, m.id, i1, i2, val)
            if k1.startswith("@MMK_") and k2.startswith("@MMK_"):
                n_grp += 1
            else:
                n_exc += 1
            journal.append(("crenage sc", "%s+%s" % (i1, i2), m.name, val,
                            float(v)))
        # les bornes, en exception glyphe-glyphe, donc par-dessus le groupe
        for (a, b), rendu in sorted(BORNES_SC.get(m.name, {}).items()):
            if font.glyphs[a] is None or font.glyphs[b] is None:
                continue
            base = A.kern(font, m.id, a, b)
            val = round(base + rendu, 1)
            A.ecrire_kern(font, m.id, a, b, val, exception=True)
            journal.append(("borne sc", "%s+%s" % (a, b), m.name, val, base))
    return n, n_grp, n_exc, droites, gauches
