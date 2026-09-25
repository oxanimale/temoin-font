#!/usr/bin/env python3
"""
Le controle des approches ecrites au vingt-troisieme tour.

Il repond a une question que les cinq controles existants ne posent pas : est-ce
que le crenage et l'approche ecrits dans la source produisent bien les couloirs
mesures sur planche ? `check3` verifie les chasses, les boites, les aires et la
topologie. Aucun ne mesure le blanc entre deux lettres, et c'est justement la
grandeur que ce tour a corrigee.

**Reecrit au vingt-quatrieme tour, apres le retrait de l'approche du F.** Les
trois premieres sections jugeaient un etat qui n'existe plus : une chasse
modifiee, des futs revenus au couloir d'Atkinson, des rondes gardant un residu.
C'etait exactement la description de l'approche du glyphe. Une tolerance ecrite
en dur decrit un etat, et elle devient fausse le jour ou l'etat change, sans que
son code bouge.

Cinq sections, sur les huit masters des deux sources.

1. Les chasses. Aucune ne doit bouger. C'est le seul controle du projet qui les
   balaie toutes, et il dirait qu'une approche est revenue par accident.

2. Ce que la table laisse ouvert, et ce qu'elle pouvait encore refermer. Le
   critere ne se recopie pas : c'est `approches.paire_bornee`, la fonction meme
   qui produit la table. Une paire refermable et non refermee est une lacune.

3. Le garde-fou, **sur les deux bandes**. Aucune paire du F ne doit etre plus
   serree que dans Atkinson, ni sur la bande de jugement, ni sur la bande
   pleine. La seconde est la correction de fond du tour : ce garde-fou ne
   mesurait que jusqu'a la hauteur d'x, et il declarait conformes six paires de
   capitales qui se touchaient dans le binaire servi.

4. Le crenage r+n. Sa valeur, et la distance rn/m qui en resulte, contre la
   reference de chaque master. La colonne d'ecart doit rester negative : +20 ne
   franchit la reference d'aucun master, c'est mesure et assume, et un chiffre
   positif signalerait une valeur ecrite par erreur.

5. Le voisinage des trois pieds gauches descendants du lot 1, m, M et f, sur la
   bande pleine. **C'est le trou que le lot 1 a revele** : cinq controles
   mesurent des glyphes isoles, et la section 3 ne surveille que le voisinage du
   F. Quatre paire-masters se touchaient donc reellement — `q+M` au Bold et a
   l'ExtraBold, `q+m` a l'ExtraBold, `q+M` en ExtraBold Italic — et il a fallu
   un balayage ecrit a la main pour les trouver.

   **Son critere n'est pas celui de la section 3, et c'est voulu.** La coupe du F
   elargissait un couloir, donc « jamais plus serre qu'Atkinson » est atteignable
   pour elle. Le geste du lot 1 resserre par construction : la meme exigence
   demanderait 116 a 122 unites d'ecartement, c'est-a-dire d'annuler le geste.
   Le critere est un plancher, `approches.JOUR_MIN`, partage avec la table.

`--temoin` retire un correctif de la table et rejoue tout. Un controle qui passe
doit prouver qu'il sait signaler : le lot 4 compte quatre controles qui
mesuraient une grandeur constante, et un cinquieme qui rendait 0,000 sur toute
une famille.

`--sans-source` dit ce que le controle devient quand la source amont n'est pas
clonable. Il ne conclut alors rien sur les couloirs, qui se mesurent contre
Atkinson, et se declare non fait sur les sections 2 et 3. Distinguer « mesure et
conforme » de « pas mesure » a coute une session entiere a ce projet.
"""

import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import approches as A
import dessin as D

ICI = os.path.dirname(os.path.abspath(__file__))
AMONT = {"roman": "/tmp/ahn/sources/AtkinsonHyperlegibleNext.glyphs",
         "italic": "/tmp/ahn/sources/AtkinsonHyperlegibleNext-Italic.glyphs"}
TEMOIN = {"roman": os.path.join(ICI, "Temoin.glyphs"),
          "italic": os.path.join(ICI, "Temoin-Italic.glyphs")}
MASTERS = {"roman": ["ExtraLight", "Regular", "Bold", "ExtraBold"],
           "italic": ["ExtraLight Italic", "Italic", "Bold Italic",
                      "ExtraBold Italic"]}

#: Les voisins du F, 71 en tout puis 81. Le premier jet en testait 36 et
#: oubliait les capitales : F+J est crenee par Atkinson et la coupe ne l'a
#: jamais ouverte, donc l'approche la serrait de sa valeur entiere sans que
#: rien le dise.
#:
#: LES DIX CHIFFRES Y ENTRENT AU QUARANTE-QUATRIEME TOUR, et cette liste n'est
#: plus seulement celle du F : `inventaire_pieds` l'importe comme voisinage de
#: reference, et le projet a ecrit que deux codes qui parlent du meme
#: voisinage doivent lire la meme liste. Sans les chiffres, les paires
#: chiffre+chiffre restaient invisibles a la table des pieds -- or un chiffre
#: suit un chiffre plus souvent que n'importe quel autre caractere, et l'OXA
#: publie des nombres. Le 9 plongeait ainsi depuis le quarantieme tour sans
#: qu'aucune paire ne le teste.
#:
#: CE QUE LEUR ENTREE CHANGE POUR LE F, mesure et non suppose : voir la sortie
#: de `check_approches` apres ce tour. La liste sert a deux choses -- borner le
#: balayage du F et fournir le voisinage des pieds -- et un nom qui entre est
#: teste par les deux.
#: LES VINGT-NEUF ACCENTUEES FRANCAISES, ENTREES AU CINQUANTE-QUATRIEME TOUR.
#: La liste ci-dessus en portait CINQ, choisies a la main -- `eacute`,
#: `egrave`, `agrave`, `ccedilla`, `ocircumflex` -- et son arbitraire se lisait
#: dans le repertoire : `ocircumflex` y etait, `odieresis` n'y etait pas.
#:
#: CE QUE LE TROU COUTAIT, mesure a l'ExtraBold sur l'etat servi, en unites de
#: blanc entre le F et son voisin :
#:
#:     F+e  81,0     F+ê 171,0   F+ë 156,8
#:     F+o  81,7     F+ô  81,0   F+ö 146,8   F+œ 199,7
#:     F+u  85,7     F+ù 164,8   F+û 155,0   F+ü 140,8
#:     F+O  62,7     F+Ô 158,7   F+Ö 158,7
#:     F+A  80,8     F+À 238,8   F+Â 238,8   F+Ä 238,8
#:     F+Y   ?       F+Ÿ  35,0  -- le plus SERRE du voisinage, sous F+T a 50,6
#:
#: Nicolas l'a vu en navigateur sur l'oe, au cinquante-quatrieme tour : « devant
#: le oe, le F est trop loin ». L'inventaire en a rendu vingt-neuf. C'est la
#: meme forme que le point ouvert 80, ferme au quarante-cinquieme tour en
#: faisant entrer les dix chiffres : le producteur existait, il lui manquait
#: des voisins.
ACCENTUEES_FR = [
    "agrave", "acircumflex", "adieresis", "ccedilla",
    "eacute", "egrave", "ecircumflex", "edieresis",
    "icircumflex", "idieresis", "ocircumflex", "odieresis",
    "ugrave", "ucircumflex", "udieresis", "ydieresis", "oe", "ae",
    "Agrave", "Acircumflex", "Adieresis", "Ccedilla",
    "Eacute", "Egrave", "Ecircumflex", "Edieresis",
    "Icircumflex", "Idieresis", "Ocircumflex", "Odieresis",
    "Ugrave", "Ucircumflex", "Udieresis", "Ydieresis",
]

#: LES DIX NOMS DE LA FAMILLE DE L'AE, ENTRES AU SOIXANTE-ET-ONZIEME TOUR,
#: point ouvert 99. `REGLAGE_AE` leur donne un reglage depuis le
#: cinquante-sixieme tour, et aucun garde-fou ne surveillait leur voisinage :
#: un zero-diff des tables a leur sujet etait une cecite. Mesure au
#: soixante-huitieme tour sur les tables d'alors : 15 anomalies, F+Cacute,
#: F+Ccaron, F+Cdotaccent ouverts aux huit masters, et Eogonek+y sous le
#: plancher dans sept, 9,7 a 19,4 unites contre 62 a 88 chez Atkinson.
#: Aucun n'est une lettre du francais ni n'entre dans le servi : le defaut
#: vivait dans la police publiee seule.
FAMILLE_AE = [
    "Cacute", "Ccaron", "Cdotaccent", "Ecaron", "Edotaccent",
    "Emacron", "Eogonek", "Lacute", "Lcaron", "Lcommaaccent",
]

VOISINS_F = ([chr(c) for c in range(ord("a"), ord("z") + 1)]
             + [chr(c) for c in range(ord("A"), ord("Z") + 1)]
             + ["zero", "one", "two", "three", "four", "five", "six",
                "seven", "eight", "nine"]
             + ["period", "comma", "quotesingle", "quotedblleft", "quoteright",
                "hyphen", "colon", "semicolon", "exclam", "question",
                "parenleft", "guillemetleft", "OE", "AE"]
             + ACCENTUEES_FR
             + FAMILLE_AE)

#: La chasse de `f.sc` telle que le lot 3 la produit SANS les approches, par
#: master. Mesuree en regenerant les deux sources avec TEMOIN_SANS_APPROCHES=1.
#:
#: Ecrite en clair parce que le controle ne peut pas la recalculer : le lot 3
#: pose `width = round(w * kx + 2 * sb, 1)` ou `w` est la chasse INTERPOLEE du F
#: a une coordonnee d'axe deduite de la graisse, et non celle du master courant.
#: Un controle qui reconstruirait cette formule verifierait sa propre copie.
#: Trois premiers jets ont echoue avant celui-la, tous parce qu'ils supposaient
#: `chasse(F) x ratio` : les ecarts allaient de +2 a +8 unites, sans regularite.
#:
#: Ce qui la perime : tout changement de `lot3.fabriquer`, de HAUTEUR_SC ou de
#: APPROCHE_SC. Le controle le dira, puisque le delta cessera de tomber.
F_SC_SANS_APPROCHE = {
    "ExtraLight": 490.3, "Regular": 503.2, "Bold": 523.7, "ExtraBold": 529.1,
    "ExtraLight Italic": 490.3, "Italic": 503.2, "Bold Italic": 523.7,
    "ExtraBold Italic": 529.2,
}

FUTS = ["r", "n", "m", "i", "l", "u", "t", "p", "h", "b", "k"]
RONDES = ["o", "e", "c", "d", "g", "q"]

TOL = 5.0            # unites : en dessous, l'ecart est du bruit d'echantillonnage
RONDE_MIN = 10.0     # le reste attendu devant une ronde, borne basse
RONDE_MAX = 40.0     # borne haute


def mid(f, nom):
    return [m for m in f.masters if m.name == nom][0].id


def couloir(src, font, m, a, b, ajout=0.0):
    k = A.kern(font, m, a, b) + ajout
    g, _ = A.inter_lettre(src, a, b, k)
    return g


def _exact(src, a, b, k=0.0):
    """Le couloir vrai, par `balayage_lot4b.couloir_exact`.

    Import differe et non au niveau du module : `balayage_lot4b` importe ce
    fichier dans une de ses fonctions, et un import croise au niveau module
    ferait un cycle. Sert la ou le minorant du point 55 ferait crier a tort un
    garde-fou, c'est-a-dire sur une paire volontairement resserree.
    """
    from balayage_lot4b import couloir_exact
    return couloir_exact(src, a, b, k)


def main(temoin=False, sans_source=False):
    """Rend le code de sortie : 0 conforme, 1 signale, 2 non mesure.

    TROIS CODES DEPUIS LE SOIXANTE-SEPTIEME TOUR, point ouvert 31. Avant, une
    paire dont la reference d'Atkinson manquait comptait comme une anomalie,
    "verdict impossible" ecrit a cote, et le script sortait a 1 : sans le
    clone, `icircumflex+M` a -4,9 passait pour un contact, quand il est tenu
    tel quel par Atkinson. Une anomalie MESUREE rend 1 meme si d'autres
    sections n'ont pas mesure, parce qu'un defaut mesure reste un defaut ;
    sinon, une section non mesuree rend 2.

    En mode temoin : 0 si le temoin signale, 1 s'il reste muet, 2 si la
    source amont manque, la section 3 ne pouvant alors pas mordre.
    """
    anomalies, notes, non_mesures = [], [], []
    source_la = all(os.path.exists(p) for p in AMONT.values()) and not sans_source
    if not source_la:
        non_mesures.append("la source amont n'est pas lisible : les sections "
                           "2 et 3 ne sont pas faites, elles se mesurent "
                           "contre Atkinson")

    if temoin:
        notes.append("mode temoin : le crenage F+period, la table des pieds et "
                     "la table des bouts sont effaces de la copie en memoire "
                     "de la source, les sections 3, 5 et 6 doivent signaler")

    for cle in ("roman", "italic"):
        tem = glyphsLib.load(open(TEMOIN[cle]))
        if temoin:
            # Le temoin doit agir sur ce que le controle MESURE, et le controle
            # mesure la source ecrite. Le premier jet retirait l'entree de
            # `approches.CORRECTIFS_F` en memoire : la table n'est lue qu'a
            # l'ecriture, donc le controle ne voyait aucune difference et
            # annoncait qu'il ne savait pas echouer. On efface donc le crenage
            # dans la copie chargee, ce qui reproduit exactement un correctif
            # oublie.
            for m in tem.masters:
                K = tem.kerning.get(m.id, {})
                for ka in list(K):
                    if ka in ("F", "@MMK_L_F"):
                        for kb in list(K[ka]):
                            if "period" in kb:
                                del K[ka][kb]
                # Et la table des pieds, pour que la section 5 ait son propre
                # temoin : sans lui, son zero ne se distinguerait pas d'une
                # grandeur morte. Effacer le crenage ecrit reproduit exactement
                # une table oubliee, et les quatre contacts du lot 1 doivent
                # revenir.
                for a, b, _ in A.PAIRES_PIEDS.get(m.name, ()):
                    for ka, kb in A.cles_kern(tem, a, b):
                        if K.get(ka, {}).get(kb) is not None:
                            del K[ka][kb]
                # Et la table des huit bouts coupes, pour que la section 6 ait
                # son propre temoin. Effacer le crenage ecrit reproduit
                # exactement une table oubliee, et les 647 ouvertures que le
                # trente-et-unieme tour a refermees doivent revenir.
                for a, b, _ in A.PAIRES_BOUTS.get(m.name, ()):
                    for ka, kb in A.cles_kern(tem, a, b):
                        if K.get(ka, {}).get(kb) is not None:
                            del K[ka][kb]
                # Et les trois reglages du cinquantieme tour, pour que la
                # section 8 ait son temoin. Elle attend une valeur exacte par
                # paire : les effacer fait tomber les trois a leur valeur
                # d'Atkinson, donc hors cible, et la section doit le dire.
                for a, b in ([("l", "quoteright")]
                             + [("quoteright", n) for n in A.NOMS_I_ACCENTUE]
                             + [A.CIBLE_L_DIAGONALES]):
                    for ka, kb in A.cles_kern(tem, a, b):
                        if K.get(ka, {}).get(kb) is not None:
                            del K[ka][kb]
                # Et le reglage du X devant le A, pour que la section 9 ait son
                # temoin. Sans lui elle reste MUETTE : le temoin general efface
                # le crenage de `tem` et non de l'amont, mais la section 9 est
                # la seule a lire une table generee dont la valeur ne depend pas
                # de ce qui a ete efface. L'effacer fait tomber la paire a zero,
                # donc hors cible ET sous le plancher : les deux exigences de la
                # section doivent mordre. Une section qu'aucun temoin n'exerce
                # se lit comme une section qui passe, et ce projet l'a paye deux
                # fois le jour meme.
                for ka, kb in A.cles_kern(tem, *A.CIBLE_XA):
                    if K.get(ka, {}).get(kb) is not None:
                        del K[ka][kb]
        amont = glyphsLib.load(open(AMONT[cle])) if source_la else None
        # Depuis le vingt-quatrieme tour, aucune chasse n'est touchee : l'approche
        # du F est retiree et le trou de sa barre mediane se referme paire par
        # paire. La section 1 verifie donc l'inverse de ce qu'elle verifiait :
        # que RIEN n'a bouge. Elle garde tout son interet, c'est le seul controle
        # du projet qui balaie toutes les chasses des deux sources.
        base = 0.0
        print(f"\n=== {cle} : aucune chasse ne doit bouger "
              f"({len(A.PAIRES_F.get(MASTERS[cle][0], {}))} paires du F "
              f"au premier master)")

        # --- 1. les chasses
        if source_la:
            for mn in MASTERS[cle]:
                ma, mt = mid(amont, mn), mid(tem, mn)
                bouges = []
                for g in amont.glyphs:
                    gt = tem.glyphs[g.name]
                    if gt is None:
                        continue
                    la = next((l for l in g.layers if l.layerId == ma), None)
                    lt = next((l for l in gt.layers if l.layerId == mt), None)
                    if la is None or lt is None:
                        continue
                    if abs(float(lt.width) - float(la.width)) > 0.5:
                        bouges.append((g.name, float(la.width), float(lt.width)))
                if bouges:
                    anomalies.append(f"{cle} {mn} : {len(bouges)} chasse(s) "
                                     f"modifiee(s), aucune n'est attendue : "
                                     + ", ".join(f"{n} {a:.0f}->{b:.0f}"
                                                 for n, a, b in bouges[:5]))
                # L'heritage par le lot 3 : `f.sc` est derivee du F avec une
                # chasse homothetique, donc elle doit avoir baisse de la valeur
                # de l'approche fois le rapport du lot 3. La verifier ici est
                # necessaire : `f.sc` n'existe pas dans la source amont, donc la
                # boucle sur ses glyphes ne peut pas la voir, et l'heritage
                # serait passe sans controle.
                import make_temoin as MT
                ratio = MT.HAUTEUR_SC / 668.0
                gsc = tem.glyphs["f.sc"]
                lsc = next((l for l in gsc.layers if l.layerId == mt), None) \
                    if gsc else None
                herite = None
                if lsc is not None:
                    # Le controle est differentiel : la valeur absolue de f.sc
                    # depend d'une interpolation, son DELTA ne depend que de
                    # l'approche et du rapport du lot 3.
                    herite = float(lsc.width)
                    avant = F_SC_SANS_APPROCHE.get(mn)
                    if avant is None:
                        notes.append(f"{cle} {mn} : pas de reference f.sc, "
                                     "heritage non verifie")
                    else:
                        attendu_d = base * ratio
                        obtenu_d = herite - avant
                        if abs(obtenu_d - attendu_d) > 1.0:
                            anomalies.append(
                                f"{cle} {mn} : f.sc a bouge de {obtenu_d:+.1f}, "
                                f"attendu {attendu_d:+.1f} (approche {base:+.0f} "
                                f"au rapport {ratio:.4f})")
                print(f"  {mn:20s} {len(bouges)} chasse(s) modifiee(s), "
                      f"f.sc {herite:.1f}, ecart a la reference sans approche "
                      f"{herite - F_SC_SANS_APPROCHE.get(mn, herite):+.1f} "
                      f"pour {base * ratio:+.1f} attendu")
        else:
            print("  section 1 non faite, pas de source amont")

        # --- 2. la table referme-t-elle tout ce que la borne permet ?
        #
        # **Cette section jugeait un etat qui n'existe plus.** Elle attendait que
        # les futs reviennent au couloir d'Atkinson et que les rondes gardent 10 a
        # 40 unites, ce qui decrivait exactement l'approche du glyphe : elle
        # refermait tout devant les futs et laissait un residu devant les rondes.
        # Avec la table de paires du vingt-quatrieme tour, c'est l'inverse : les
        # rondes reviennent a zero et les futs gardent ce que la borne pleine
        # interdit de refermer. Une tolerance ecrite en dur decrit un etat, et
        # elle devient fausse le jour ou l'etat change, sans que son code bouge.
        #
        # Le critere ne se recopie donc plus : c'est `paire_bornee` elle-meme. Le
        # reste attendu vaut l'ouverture moins ce qu'on pouvait refermer, et un
        # reste plus grand signale une paire que la table a oubliee.
        if source_la:
            print(f"  {'master':20s} {'paires laissees ouvertes':>26s}"
                  f"{'  manque a la table':>22s}")
            for mn in MASTERS[cle]:
                sa, st = D.Source(amont, mn), D.Source(tem, mn)
                ma, mt = mid(amont, mn), mid(tem, mn)
                restes, manques = [], []
                for b in VOISINS_F:
                    if tem.glyphs[b] is None:
                        continue
                    ka = A.kern(amont, ma, "F", b)
                    g1 = couloir(sa, amont, ma, "F", b)
                    g2 = couloir(st, tem, mt, "F", b)
                    if g1 is None or g2 is None:
                        continue
                    reste = g2 - g1
                    if reste > TOL:
                        restes.append((b, reste))
                        # Ce qu'on pourrait encore refermer, mesure APRES la
                        # table et non avant. Un premier jet rappelait
                        # `paire_bornee` avec le crenage d'Atkinson : il
                        # retrouvait l'ouverture d'origine et signalait comme
                        # oubliees les paires que la table venait de traiter.
                        # C'est le piege du controle qui redecouvre son objet,
                        # cinquieme recidive du projet — une verification prend
                        # l'etat courant, jamais celui d'ou l'on part.
                        kt = A.kern(tem, mt, "F", b)
                        p1 = A.couloir_plein(sa, "F", b, ka)
                        p2 = A.couloir_plein(st, "F", b, kt)
                        if p1 is None or p2 is None:
                            continue
                        encore = min(reste, p2 - p1)
                        # CE QU'UN REGLAGE VALIDE A VOULU LAISSER OUVERT n'est
                        # pas un oubli de la table, et la section doit le
                        # retirer avant de conclure. Trois reglages desserrent
                        # apres la table : les rondes a +15 depuis le
                        # trente-et-unieme tour, les rondes CAPITALES au meme
                        # +15 depuis le cinquante-quatrieme, et les quatre
                        # diagonales du A a +30 au meme tour.
                        #
                        # LA SECTION ETAIT MUETTE PAR CHANCE, PAS PAR
                        # CONSTRUCTION. `SEUIL_PAIRE` vaut 20 : le +15 des
                        # rondes passait dessous et ne se voyait pas, le +30 du
                        # A le depasse et criait sur quatre paires par master
                        # gras. Le seuil absorbait un reglage valide au lieu de
                        # le connaitre, ce qui est la forme la plus discrete du
                        # garde-fou qui crie a tort.
                        regle = 0.0
                        if b in A.RONDES_F:
                            regle = A.REGLAGE_F_RONDES
                        elif b in A.DIAGONALES_F:
                            regle = A.REGLAGE_F_A
                        if encore - regle > A.SEUIL_PAIRE:
                            manques.append((b, encore - regle))
                print(f"  {mn:20s} {len(restes):>4} paire(s), au pire "
                      f"{max((r for _, r in restes), default=0):+7.1f} u"
                      f"{len(manques):>12} paire(s)"
                      + ("  " + ", ".join(f"F+{b} {v:+.0f}"
                                          for b, v in manques[:4])
                         if manques else ""))
                if manques:
                    anomalies.append(
                        f"{cle} {mn} : {len(manques)} paire(s) que la table "
                        f"pouvait refermer et n'a pas refermee, "
                        + ", ".join(f"F+{b}" for b, _ in manques[:6]))

            # --- 3. le garde-fou, sur les DEUX bandes
            #
            # **La bande pleine est la correction de fond du vingt-quatrieme
            # tour.** Ce garde-fou ne mesurait que de la ligne de base a la
            # hauteur d'x, la bande sur laquelle un blanc de bas de casse se
            # juge. Elle est fausse pour la question qu'il pose : la barre haute
            # du F monte a 668 et le point du i a 714. Il declarait donc
            # conformes six paires de capitales qui se touchaient reellement
            # dans le binaire servi, FI FT FV FW FX FY, et il ne mentait pas —
            # il s'arretait 218 unites trop bas.
            for mn in MASTERS[cle]:
                sa, st = D.Source(amont, mn), D.Source(tem, mn)
                ma, mt = mid(amont, mn), mid(tem, mn)
                # L'EXCEPTION DECLAREE DU TRENTE-ET-UNIEME TOUR, ET ELLE CHANGE
                # LA QUESTION POSEE PLUTOT QUE DE LEVER LE CONTROLE.
                #
                # Nicolas a demande de resserrer `F+i` sur retour navigateur.
                # C'est le seul endroit du projet plus serre que sa police de
                # base, et c'est un choix. Le garde-fou le signalait donc huit
                # fois, a juste titre selon son critere et a tort selon
                # l'intention — et un garde-fou qui crie a tort finit par etre
                # ignore, ce que le projet a deja paye deux fois.
                #
                # La sortie n'est pas de l'exempter : c'est de lui poser LA
                # BONNE question. Sur une paire que `approches.REGLAGE_F_I`
                # nomme, passer sous Atkinson est voulu, et ce qui doit tenir
                # est le PLANCHER DE JOUR. Une exception qui ne verifie plus
                # rien serait pire que le faux positif qu'elle remplace.
                #
                # LA SECONDE EXCEPTION DECLAREE, TRENTE-DEUXIEME TOUR, ET SON
                # MOTIF N'EST PAS LE MEME. `F+i` est plus serre parce qu'un
                # crenage le veut ; `F+t` l'est parce que le DESSIN du t a
                # monte de 620 a 690, et Atkinson n'a pas de t a cette hauteur.
                # La question juste est encore le plancher de jour, mais les
                # deux cas sont imprimes separement : confondre un crenage
                # voulu et un alignement deplace ferait lire la meme cause a
                # deux endroits qui n'en ont pas.
                exc = {"i"} if mn in A.REGLAGE_F_I else set()
                montes = set(A.HAUTEUR_MODIFIEE)
                sous_j, sous_p, regles, hauts = [], [], [], []
                for b in VOISINS_F:
                    if tem.glyphs[b] is None:
                        continue
                    ka = A.kern(amont, ma, "F", b)
                    kt = A.kern(tem, mt, "F", b)
                    g1 = couloir(sa, amont, ma, "F", b)
                    g2 = couloir(st, tem, mt, "F", b)
                    p1 = A.couloir_plein(sa, "F", b, ka)
                    p2 = A.couloir_plein(st, "F", b, kt)
                    if b in exc:
                        # Le plancher est mesure par le couloir EXACT et non par
                        # le minorant : sur une paire volontairement serree, un
                        # minorant conservateur ferait crier a tort une seconde
                        # fois. Point 55, et son critere dit que la divergence
                        # vit a faible ecartement, donc precisement ici.
                        x2 = _exact(st, "F", b, kt)
                        regles.append((b, p2, p1, x2))
                        if x2 is not None and x2 < A.JOUR_MIN - 0.05:
                            anomalies.append(
                                f"{cle} {mn} : F+{b} est resserre par "
                                f"REGLAGE_F_I sous le plancher de jour, "
                                f"{x2:.1f} pour {A.JOUR_MIN:.0f} unites")
                        continue
                    if b in montes:
                        x2 = _exact(st, "F", b, kt)
                        hauts.append((b, p2, p1, x2))
                        if x2 is not None and x2 < A.JOUR_MIN - 0.05:
                            anomalies.append(
                                f"{cle} {mn} : F+{b} est resserre par la "
                                f"montee du dessin sous le plancher de jour, "
                                f"{x2:.1f} pour {A.JOUR_MIN:.0f} unites")
                        continue
                    if g1 is not None and g2 is not None and g2 < g1 - TOL:
                        sous_j.append((b, g2, g1))
                    if p1 is not None and p2 is not None and p2 < p1 - TOL:
                        sous_p.append((b, p2, p1))
                print(f"  {mn:20s} garde-fou : {len(sous_j)} sous Atkinson sur la "
                      f"bande de jugement, {len(sous_p)} sur la bande pleine"
                      + ("  " + ", ".join(f"F+{b} {c:.0f}<{r:.0f}"
                                          for b, c, r in sous_p[:4])
                         if sous_p else ""))
                for b, p2, p1, x2 in regles:
                    print(f"  {'':20s} REGLE  F+{b} volontairement resserre, "
                          f"{p2:.0f} pour {p1:.0f} dans Atkinson ; jour reel "
                          f"{x2:.1f} pour un plancher de {A.JOUR_MIN:.0f}")
                for b, p2, p1, x2 in hauts:
                    print(f"  {'':20s} MONTE  F+{b} plus serre par la hauteur "
                          f"du {b}, {p2:.0f} pour {p1:.0f} dans Atkinson ; "
                          f"jour reel {x2:.1f} pour un plancher de "
                          f"{A.JOUR_MIN:.0f}")
                for etq, sous in (("bande de jugement", sous_j),
                                  ("bande pleine", sous_p)):
                    if sous:
                        anomalies.append(
                            f"{cle} {mn} : {len(sous)} paire(s) du F plus "
                            f"serrees que dans Atkinson sur la {etq}, "
                            + ", ".join(f"F+{b}" for b, _, _ in sous[:6]))
        else:
            print("  sections 2 et 3 non faites, pas de source amont")

        # --- 4. le crenage r+n, et ce qu'il achete
        attendu = A.KERN_PAIRES[("r", "n")]
        print(f"  {'master':20s} {'r+n':>6s} {'rn/m':>7s} {'reference':>10s} "
              f"{'ecart':>7s}")
        for mn in MASTERS[cle]:
            mt = mid(tem, mn)
            k = A.kern(tem, mt, "r", "n")
            if abs(k - attendu) > 0.01:
                anomalies.append(f"{cle} {mn} : crenage r+n = {k:+.0f}, "
                                 f"attendu {attendu:+.0f}")
            d = A.distance_rn_m_kern(tem, mt, k)
            ref = None
            if source_la:
                import mesure_O as MO
                import lot2 as L
                ma = mid(amont, mn)

                def cont(nom):
                    for l in amont.glyphs[nom].layers:
                        if l.layerId == ma:
                            return [D.flatten(p) for p in L.paths(l)]
                    return []
                ref = min(MO.confusion((cont(a), []), (cont(b), []), 120, 3.0)
                          for a, b in (("I", "T"), ("E", "F"), ("B", "P"),
                                       ("E", "B"), ("F", "P")))
                if d > ref:
                    # Ce cas existe et il n'est pas un defaut : la reference
                    # italique descend plus bas que la romaine, jusqu'a 0,163 a
                    # l'ExtraBold Italic contre 0,209 au Bold romain. La paire
                    # la plus serree de l'echantillon italique est donc plus
                    # confusable, et +20 suffit a la depasser de ce cote.
                    # L'etalonnage italique n'avait jamais ete mesure avant ce
                    # tour.
                    notes.append(f"{cle} {mn} : rn/m {d:.3f} passe au-dessus de "
                                 f"la reference {ref:.3f}. La reference "
                                 "italique est plus basse que la romaine, +20 "
                                 "la franchit de ce cote")
            print(f"  {mn:20s} {k:+6.0f} {d:7.3f} "
                  + (f"{ref:10.3f} {d - ref:+7.3f}" if ref else
                     f"{'non fait':>10s} {'':>7s}"))

        # --- 5. le voisinage des trois pieds gauches descendants du lot 1
        #
        # Ce que la section 3 ne pouvait pas voir : elle ne teste que le
        # voisinage du F. Quatre paire-masters se touchaient reellement, et
        # aucun des six controles du projet ne les voyait — cinq mesurent des
        # glyphes isoles, ou ni la chasse, ni la topologie, ni la boite en
        # romain ne bougent.
        #
        # Le critere est un PLANCHER et non une comparaison a Atkinson, parce
        # que le geste ferme le couloir par construction. Consequence utile :
        # la section conclut sans la source amont, la comparaison a Atkinson
        # n'etant qu'une colonne d'information. Le projet a deja perdu deux
        # tours sur un clone indisponible.
        # L'etiquette est LUE dans `approches.CIBLES_PIEDS` et non ecrite ici.
        # Elle annoncait « le voisinage de m, M et f » jusqu'au vingt-neuvieme
        # tour, alors que la liste avait triple depuis : le p, le y et le Y y
        # sont entres au vingt-septieme, le N et le H au vingt-huitieme, le A et
        # le X au vingt-neuvieme. Une etiquette qui nomme trois cibles quand le
        # controle en surveille dix fait croire a un trou de couverture qui
        # n'existe pas — et elle ferait croire a une couverture qui n'existe pas
        # si elle allait dans l'autre sens. C'est le piege de `CORRECTIFS_F`,
        # qui nomme `period` et touche tout son groupe.
        print(f"\n  {'master':20s} le voisinage de "
              f"{', '.join(A.CIBLES_PIEDS)} sur la bande "
              f"pleine, plancher {A.JOUR_MIN:.0f} u")
        for mn in MASTERS[cle]:
            mt = mid(tem, mn)
            st = D.Source(tem, mn)
            sa = D.Source(amont, mn) if source_la else None
            ma = mid(amont, mn) if source_la else None
            bas, tenues, indecis, pire = [], [], [], None
            # Dedoublonnage, comme dans le generateur : une paire dont les deux
            # membres sont des cibles est trouvee une fois par chaque cible.
            # `f+Y` est dans ce cas depuis le lot 3, et le temoin le comptait
            # deux fois, ce qui gonflait le nombre d'anomalies sans en ajouter.
            vues = set()
            # LES DEUX SENS, comme le generateur depuis le vingt-septieme tour.
            # Le Y descend par son cote droit, donc il mange l'approche de la
            # lettre SUIVANTE : un controle qui ne teste qu'un sens laisserait
            # passer la moitie du voisinage de cette cible.
            for cible in A.CIBLES_PIEDS:
                for v in VOISINS_F:
                    if tem.glyphs[v] is None or tem.glyphs[cible] is None:
                        continue
                    for a, b in ((v, cible), (cible, v)):
                        if (a, b) in vues:
                            continue
                        try:
                            g = A.couloir_plein(st, a, b,
                                                A.kern(tem, mt, a, b))
                        except Exception:
                            continue
                        if g is None:
                            continue
                        vues.add((a, b))
                        ga = None
                        if source_la:
                            try:
                                ga = A.couloir_plein(
                                    sa, a, b, A.kern(amont, ma, a, b))
                            except Exception:
                                ga = None
                        if pire is None or g < pire[2]:
                            pire = (a, b, g, ga)
                        if g >= A.JOUR_MIN:
                            continue
                        # TROIS CAS ET NON DEUX, et les confondre a fait rendre
                        # sept anomalies dont cinq n'en etaient pas.
                        #
                        # Une paire sous le plancher n'est une anomalie du
                        # projet que si le projet l'a RESSERREE. Deux cas
                        # innocents, mesures au vingt-septieme tour :
                        #
                        #   `q+p` a 18,0 a 23,1 unites et `eacute+Y` a 9,4 y
                        #   sont DEJA dans Atkinson, a la meme valeur au
                        #   dixieme. Le projet ne les touche pas.
                        #
                        #   `q+y` y est porte par la table, mais le plafond a
                        #   mordu : Atkinson le tient a 17,9 a 20,0, donc sous
                        #   le plancher, et la table a rendu son couloir sans
                        #   pouvoir faire mieux. Ecarter au-dela serait plus
                        #   lache que la police de base.
                        #
                        # Sans la source amont ces deux cas sont indiscernables
                        # d'un vrai defaut, et la section le dit alors au lieu
                        # de conclure : c'est le seul endroit ou elle a besoin
                        # de l'amont.
                        if ga is None:
                            indecis.append((a, b, g, ga))
                        elif g >= ga - 0.5:
                            tenues.append((a, b, g, ga))
                        else:
                            bas.append((a, b, g, ga))
            n_ecrites = len(A.PAIRES_PIEDS.get(mn, ()))
            detail = (f"le plus serre {pire[0]}+{pire[1]} a {pire[2]:.1f}"
                      + (f" (Atkinson {pire[3]:.1f})"
                         if pire and pire[3] is not None else "")
                      if pire else "rien de mesurable")
            info = ("" if not tenues else
                    f" ; {len(tenues)} sous le plancher que le projet ne "
                    "resserre pas : " + ", ".join(
                        f"{a}+{b} {g:.1f} (Atkinson {ga:.1f})"
                        for a, b, g, ga in sorted(tenues,
                                                  key=lambda t: t[2])[:4]))
            print(f"  {mn:20s} {len(bas):2d} resserree(s) sous le plancher, "
                  f"{n_ecrites} paire(s) ecrite(s) ; {detail}{info}")
            if bas:
                anomalies.append(
                    f"{cle} {mn} : {len(bas)} paire(s) que le projet resserre "
                    f"sous le plancher de {A.JOUR_MIN:.0f} unites sur la bande "
                    "pleine, "
                    + ", ".join(
                        f"{a}+{b} {g:.1f}"
                        + (f" (Atkinson {ga:.1f})" if ga is not None else
                           " (amont absent, verdict impossible)")
                        for a, b, g, ga in bas[:6])
                    + ("   CONTACT" if any(g <= 0 for _, _, g, _ in bas)
                       else ""))
            if indecis:
                non_mesures.append(
                    f"{cle} {mn} : {len(indecis)} paire(s) sous le plancher "
                    "sans reference d'Atkinson, verdict impossible — "
                    + ", ".join(f"{a}+{b} {g:.1f}"
                                for a, b, g, _ga in indecis[:6]))
            if tenues:
                notes.append(
                    f"{cle} {mn} : {len(tenues)} paire(s) sous le plancher que "
                    "le projet ne resserre pas, donc hors de sa portee — "
                    + ", ".join(f"{a}+{b} {g:.1f} pour {ga:.1f} dans Atkinson"
                                for a, b, g, ga in sorted(
                                    tenues, key=lambda t: t[2])[:4]))

        # --- 6. le voisinage des huit bouts coupes
        #
        # Points ouverts 56, 39, 47 et le z du lot 2, groupes et traites au
        # trente-et-unieme tour. Aucun des six controles ne surveillait le
        # voisinage de ces huit glyphes, et c'est le meme trou de couverture que
        # la section 5 a ferme pour les trois pieds gauches du lot 1.
        #
        # DEUX RISQUES, ET ILS SONT DE SENS CONTRAIRES. Un garde-fou qui ne
        # teste qu'un sens rate la moitie de son objet, et le projet l'a paye
        # trois fois.
        #
        #   - la table a referme AU-DELA d'Atkinson, donc elle a fabrique un
        #     risque de contact la ou la police de base n'en avait pas. C'est
        #     l'anomalie grave, et elle est en principe impossible : la borne
        #     de `paire_bornee` l'interdit. « En principe » n'est pas une
        #     mesure, d'ou cette verification.
        #   - la table a laisse ouvert ce qu'elle pouvait refermer, donc une
        #     paire est oubliee. Meme critere que la section 2 pour le F :
        #     le reste apres la table, borne par ce qui restait refermable.
        #
        # CE QUE CETTE SECTION NE COUVRE PAS, ET ELLE LE DIT. Elle parcourt les
        # paires ECRITES et non les 1 136 paires du perimetre par master, qui
        # demanderaient douze minutes. La couverture des paires non ecrites est
        # assuree par `inventaire_bouts.py`, qui est le balayage complet : il
        # est a relancer des que le dessin d'une des huit cibles change. Un
        # controle qui travaille sur une liste doit imprimer ce que sa liste
        # laisse dehors, sans quoi il est plus discret qu'un controle qui mente.
        if source_la:
            print(f"\n  --- 6. les huit bouts coupes "
                  f"({len(A.PAIRES_BOUTS.get(MASTERS[cle][0], ()))} paires "
                  f"ecrites au premier master)")
            for mn in MASTERS[cle]:
                sa, st = D.Source(amont, mn), D.Source(tem, mn)
                ma, mt = mid(amont, mn), mid(tem, mn)
                sous, oublis, n_lues = [], [], 0
                for a, b, _ in A.PAIRES_BOUTS.get(mn, ()):
                    if tem.glyphs[a] is None or tem.glyphs[b] is None:
                        continue
                    ka = A.kern(amont, ma, a, b)
                    kt = A.kern(tem, mt, a, b)
                    pa = A.couloir_plein(sa, a, b, ka)
                    pt = A.couloir_plein(st, a, b, kt)
                    oa, _ = A.inter_lettre(sa, a, b, ka)
                    ot, _ = A.inter_lettre(st, a, b, kt)
                    if None in (pa, pt, oa, ot):
                        continue
                    n_lues += 1
                    if pt < pa - TOL:
                        sous.append((a, b, pt, pa))
                    encore = min(ot - oa, pt - pa)
                    if encore > A.SEUIL_PAIRE:
                        oublis.append((a, b, ot - oa, encore))
                print(f"  {mn:20s} {n_lues:>4} paire(s) relue(s), "
                      f"{len(sous)} sous Atkinson, {len(oublis)} oubli(s)")
                if sous:
                    anomalies.append(
                        f"{cle} {mn} : {len(sous)} paire(s) que la table des "
                        f"bouts a refermee(s) SOUS Atkinson, "
                        + ", ".join(f"{a}+{b} {p:.1f} pour {q:.1f}"
                                    for a, b, p, q in sous[:5]))
                if oublis:
                    anomalies.append(
                        f"{cle} {mn} : {len(oublis)} paire(s) que la table des "
                        f"bouts pouvait refermer et n'a pas refermee, "
                        + ", ".join(f"{a}+{b} {e:+.0f}"
                                    for a, b, _, e in oublis[:5]))

        # --- 7. le voisinage des glyphes dont la hauteur a change
        #
        # Trente-deuxieme tour, et c'est le troisieme trou de couverture du
        # meme genre : aucun des six controles ne surveillait le voisinage du
        # t, comme aucun ne surveillait celui des trois pieds gauches avant la
        # section 5 ni celui des huit bouts avant la section 6.
        #
        # LE GESTE POUSSE DANS L'AUTRE SENS QUE TOUS LES PRECEDENTS. Les cinq
        # lots de terminaisons RETIRENT de la matiere, donc leur risque est
        # l'ouverture du couloir. `coupe.allonge` AJOUTE — 7,0 % de la surface
        # du t en ExtraLight, le plus gros ajout du projet — donc son risque
        # est le resserrement, et jusqu'au contact. Le sens dans lequel un
        # geste pousse se demande avant d'ecrire un garde-fou.
        #
        # LE CRITERE EST LE PLANCHER DE JOUR ET NON LA COMPARAISON A ATKINSON,
        # et c'est l'arbitrage de Nicolas au trente-deuxieme tour. Atkinson n'a
        # pas de t a 690 : sur une paire dont un membre a change de hauteur, la
        # comparaison au couloir de la police de base repond a une question que
        # le dessin a rendue caduque. 42 paire-masters passent sous ce couloir
        # et c'est ecrit comme limite connue, `approches.HAUTEUR_MODIFIEE`. Ce
        # qui doit tenir est le jour, et la section imprime le plus tendu a
        # chaque passage : un critere qu'on ne voit pas est un critere qu'on ne
        # peut pas contredire.
        #
        # LES DEUX SENS DE PAIRE SONT MESURES. Un garde-fou qui n'en teste
        # qu'un rate la moitie de son objet, paye trois fois par ce projet.
        #
        # SON TEMOIN N'EST PAS CELUI DES AUTRES SECTIONS, ET IL A FALLU LE
        # MESURER POUR LE SAVOIR. Le temoin general efface le crenage de la
        # copie chargee, ce qui ELARGIT les couloirs : il ne pouvait donc rien
        # faire signaler a une section dont le risque est le resserrement, et
        # il rendait zero sur les huit masters. Un temoin doit agir sur ce que
        # le controle mesure, et celui-ci resserre les paires de la cible de 60
        # unites — une valeur qui n'a rien de geometrique, elle exerce le
        # chemin de detection.
        #
        # Pourquoi ne pas allonger le t davantage, ce qui serait plus direct :
        # mesure faite, le resserrement PLAFONNE. Passe la hauteur de la barre
        # du F, le fut du t n'a plus rien en face, donc un allongement
        # excessif ne referme pas plus. Le geste ne peut pas fabriquer le
        # defaut que la section cherche, et c'est un fait a connaitre.
        if source_la and A.HAUTEUR_MODIFIEE:
            resserre_temoin = -60.0 if temoin else 0.0
            print(f"\n  --- 7. le voisinage de "
                  f"{', '.join(A.HAUTEUR_MODIFIEE)}, dont le projet a change "
                  f"la hauteur (critere : plancher de {A.JOUR_MIN:.0f} u)"
                  + ("   TEMOIN : paires resserrees de 60 u"
                     if temoin else ""))
            for mn in MASTERS[cle]:
                sa, st = D.Source(amont, mn), D.Source(tem, mn)
                ma, mt = mid(amont, mn), mid(tem, mn)
                bas, n_lues, pire = [], 0, None
                for cible in A.HAUTEUR_MODIFIEE:
                    if tem.glyphs[cible] is None:
                        continue
                    for v in VOISINS_F:
                        nom = v if len(v) > 1 else D.nom_glyphe(amont, v)
                        if nom is None or tem.glyphs[nom] is None:
                            continue
                        for a, b in ((nom, cible), (cible, nom)):
                            ka = A.kern(amont, ma, a, b)
                            kt = A.kern(tem, mt, a, b) + resserre_temoin
                            xt = _exact(st, a, b, kt)
                            xa = _exact(sa, a, b, ka)
                            if xt is None:
                                continue
                            n_lues += 1
                            if pire is None or xt < pire[2]:
                                pire = (a, b, xt, xa)
                            # Une paire deja sous le plancher dans Atkinson
                            # n'est pas un defaut du projet : c'est la limite
                            # de la police de base, et la section 5 fait deja
                            # cette distinction depuis le vingt-septieme tour.
                            if xt < A.JOUR_MIN - 0.05 and not (
                                    xa is not None and xa < A.JOUR_MIN - 0.05):
                                bas.append((a, b, xt, xa))
                det = ("rien de mesurable" if pire is None else
                       f"le plus tendu {pire[0]}+{pire[1]} a {pire[2]:.1f}"
                       + (f" (Atkinson {pire[3]:.1f})"
                          if pire[3] is not None else ""))
                print(f"  {mn:20s} {n_lues:>4} paire(s) mesuree(s), "
                      f"{len(bas)} sous le plancher ; {det}")
                if bas:
                    anomalies.append(
                        f"{cle} {mn} : {len(bas)} paire(s) que la montee du "
                        f"dessin met sous le plancher de {A.JOUR_MIN:.0f} "
                        f"unites, "
                        + ", ".join(
                            f"{a}+{b} {g:.1f}"
                            + (f" (Atkinson {ga:.1f})" if ga is not None
                               else "")
                            for a, b, g, ga in sorted(
                                bas, key=lambda t: t[2])[:6])
                        + ("   CONTACT" if any(g <= 0 for _, _, g, _ in bas)
                           else ""))

        # --- 8. les trois reglages du cinquantieme tour
        #
        # POURQUOI CETTE SECTION EXISTE. Les trois reglages vont PLUS SERRE que
        # la police de base sur deux d'entre eux, ce qu'aucune table du projet
        # ne fait : les deux tables de paires sont bornees par le couloir
        # d'Atkinson, par construction. Rien n'aurait donc signale qu'une
        # valeur avait derive, ni qu'un groupe avait attrape un glyphe de plus.
        #
        # ELLE MESURE TROIS CHOSES, ET LA TROISIEME EST CELLE QU'ON OUBLIE.
        # D'abord que la valeur ecrite vaut bien celle d'Atkinson plus le
        # reglage, master par master -- le cumul est le comportement voulu, et
        # l'italique en depend, lui qui part deja a -5 et -20. Ensuite que le
        # couloir reste au-dessus du plancher de jour. Enfin, et c'est le
        # risque propre a une ECRITURE PAR GROUPE, que le reglage ne deborde
        # pas sur des paires qui ne l'ont pas demande : `L+e` et `L+a` doivent
        # rester intacts, et `'+i` NU aussi, son couloir de 105 a 129 unites
        # n'ayant rien de fautif.
        #
        # SON TEMOIN EST LE TEMOIN GENERAL. Effacer le crenage de la copie
        # chargee retire aussi ces trois entrees, donc les valeurs attendues ne
        # tombent plus et la section signale. C'est le sens dans lequel elle
        # cherche le defaut, contrairement a la section 7.
        if source_la:
            cas = ([("l", "quoteright", A.REGLAGE_L_APOSTROPHE)]
                   + [("quoteright", n, A.REGLAGE_APOSTROPHE_I_ACCENTUE)
                      for n in A.NOMS_I_ACCENTUE]
                   + [(A.CIBLE_L_DIAGONALES[0], b, A.REGLAGE_L_DIAGONALES)
                      for b in ("y", "v", "w", "yacute", "ydieresis")])
            # Ce que le reglage ne doit PAS toucher. `L+e` et `L+a` sont dans un
            # autre groupe droit, `'+i` dans le meme groupe que les deux i
            # accentues mais ecrit en exception, et `l+quotedblright` partage le
            # groupe de l'apostrophe.
            intacts = [("L", "e"), ("L", "a"), ("quoteright", "i"),
                       ("l", "quotedblright")]
            print(f"\n  --- 8. les trois reglages du cinquantieme tour "
                  f"(l+' {A.REGLAGE_L_APOSTROPHE:+.0f}, "
                  f"'+i accentue {A.REGLAGE_APOSTROPHE_I_ACCENTUE:+.0f}, "
                  f"L+diagonales {A.REGLAGE_L_DIAGONALES:+.0f})")
            for mn in MASTERS[cle]:
                ma, mt = mid(amont, mn), mid(tem, mn)
                st = D.Source(tem, mn)
                faux, bas, deborde, pire = [], [], [], None
                for a, b, delta in cas:
                    if tem.glyphs[a] is None or tem.glyphs[b] is None:
                        continue
                    attendu = round(A.kern(amont, ma, a, b) + delta, 1)
                    obtenu = A.kern(tem, mt, a, b)
                    if abs(obtenu - attendu) > 0.05:
                        faux.append(f"{a}+{b} {obtenu:+.0f} pour "
                                    f"{attendu:+.0f} attendu")
                    g = A.couloir_plein(st, a, b, obtenu)
                    if pire is None or g < pire[2]:
                        pire = (a, b, g)
                    if g < A.JOUR_MIN:
                        bas.append(f"{a}+{b} {g:.1f}")
                for a, b in intacts:
                    if tem.glyphs[a] is None or tem.glyphs[b] is None:
                        continue
                    av, ap = A.kern(amont, ma, a, b), A.kern(tem, mt, a, b)
                    if abs(av - ap) > 0.05:
                        deborde.append(f"{a}+{b} {av:+.0f} -> {ap:+.0f}")
                print(f"  {mn:20s} {len(cas)} paire(s) reglee(s), "
                      f"{len(faux)} hors valeur, {len(bas)} sous le plancher, "
                      f"{len(deborde)} debordement(s) ; plus tendue "
                      f"{pire[0]}+{pire[1]} {pire[2]:.1f} u")
                if faux:
                    anomalies.append(f"{cle} {mn} : valeur(s) de reglage hors "
                                     f"cible, " + ", ".join(faux))
                if bas:
                    anomalies.append(
                        f"{cle} {mn} : {len(bas)} paire(s) reglee(s) sous le "
                        f"plancher de {A.JOUR_MIN:.0f} unites, "
                        + ", ".join(bas))
                if deborde:
                    anomalies.append(
                        f"{cle} {mn} : le reglage deborde sur "
                        + ", ".join(deborde))

        # --- 9. le X devant le A, referme au plancher
        #
        # POURQUOI CETTE SECTION EXISTE. Le reglage est le seul du projet ecrit
        # sur une CLE DE GROUPE, et c'est ce qui fait sa force et son risque :
        # il touche onze glyphes d'un coup, le A, ses neuf accentuees et le
        # Delta. Le producteur verifie avant d'ecrire que les onze presentent la
        # meme gouttiere au X ; cette section le REMESURE sur l'etat ecrit,
        # parce qu'un geste futur sur une accentuee pourrait defaire cette
        # egalite sans que rien ne le dise.
        #
        # ELLE MESURE QUATRE CHOSES. Que la valeur ecrite vaille celle de
        # l'amont plus le reglage. Que la fermeture soit PLEINE, donc que la
        # gouttiere atterrisse AU plancher et non au-dessus -- une fermeture qui
        # s'arrete trop tot est une decision perdue, et le projet n'a pas de
        # garde-fou qui cherche ce sens-la. Que les onze membres du groupe
        # repondent ensemble. Et que `A+X`, la paire jumelle que
        # `paires_pieds` tient deja au plancher, n'ait pas bouge d'une unite.
        #
        # SON TEMOIN EST LE TEMOIN GENERAL, comme la section 8 : effacer le
        # crenage de la copie chargee retire l'entree, donc la valeur attendue
        # ne tombe plus.
        if source_la and A.REGLAGE_XA:
            xa = A.CIBLE_XA
            ax = (xa[1], xa[0])
            print(f"\n  --- 9. le {xa[0]} devant le {xa[1]}, ferme au plancher "
                  f"de {A.JOUR_MIN:.0f} u (cle de groupe, 11 glyphes)")
            for mn in MASTERS[cle]:
                delta = A.REGLAGE_XA.get(mn)
                if delta is None or tem.glyphs[xa[0]] is None:
                    continue
                ma, mt = mid(amont, mn), mid(tem, mn)
                st = D.Source(tem, mn)
                attendu = round(A.kern(amont, ma, *xa) + delta, 1)
                obtenu = A.kern(tem, mt, *xa)
                g = A.couloir_plein(st, xa[0], xa[1], obtenu)
                _ka, _ma2, _kb, membres = A.groupes(tem, *xa)
                divergents = []
                for n in membres:
                    if tem.glyphs[n] is None:
                        continue
                    gn = A.couloir_plein(st, xa[0], n, obtenu)
                    if gn is None or abs(gn - g) > 0.55:
                        divergents.append(n)
                # LA PAIRE JUMELLE SE COMPARE A CE QUE `paires_pieds` DECLARE,
                # ET NON A L'AMONT. Un premier jet la comparait au crenage
                # d'Atkinson et criait huit fois sur un etat juste : `A+X` a
                # bouge de +15 a +47 au vingt-neuvieme tour, et c'est la
                # decision qui l'a sortie de sous le plancher apres le lot 4b.
                # Un controle qui crie sur un etat voulu apprend a etre ignore,
                # et le projet l'a paye sur la section 5 au vingt-septieme tour.
                # Ce qui merite d'etre verifie est qu'UN SEUL producteur
                # l'ecrive : si la valeur servie cesse d'etre celle de la table
                # des pieds, une autre l'a ecrasee.
                jum_ap = A.kern(tem, mt, *ax)
                declare = [v for a2, b2, v in A.PAIRES_PIEDS.get(mn, ())
                           if (a2, b2) == ax]
                jum_av = declare[0] if declare else A.kern(amont, ma, *ax)
                g_jum = A.couloir_plein(st, ax[0], ax[1], jum_ap)
                print(f"  {mn:20s} {xa[0]}+{xa[1]} {obtenu:+.0f} pour "
                      f"{attendu:+.0f}, gouttiere {g:.1f} ; les {len(membres)} "
                      f"du groupe suivent : {len(membres) - len(divergents)} ; "
                      f"{ax[0]}+{ax[1]} {jum_ap:+.0f} a {g_jum:.1f} u")
                if abs(obtenu - attendu) > 0.05:
                    anomalies.append(
                        f"{cle} {mn} : {xa[0]}+{xa[1]} vaut {obtenu:+.0f} pour "
                        f"{attendu:+.0f} attendu")
                if g < A.JOUR_MIN:
                    anomalies.append(
                        f"{cle} {mn} : {xa[0]}+{xa[1]} a {g:.1f} u, sous le "
                        f"plancher de {A.JOUR_MIN:.0f}")
                elif g > A.JOUR_MIN + 1.5:
                    anomalies.append(
                        f"{cle} {mn} : {xa[0]}+{xa[1]} a {g:.1f} u, la "
                        f"fermeture n'est plus PLEINE -- le plancher vaut "
                        f"{A.JOUR_MIN:.0f} et la decision etait de fermer tout "
                        f"ce qu'il permet")
                if divergents:
                    anomalies.append(
                        f"{cle} {mn} : le groupe ne repond plus comme le "
                        f"{xa[1]} -- " + ", ".join(divergents))
                if abs(jum_av - jum_ap) > 0.05:
                    anomalies.append(
                        f"{cle} {mn} : {ax[0]}+{ax[1]} vaut {jum_ap:+.0f} "
                        f"quand paires_pieds declare {jum_av:+.0f} — une "
                        f"seconde table l'a ecrasee")
                if g_jum < A.JOUR_MIN:
                    anomalies.append(
                        f"{cle} {mn} : {ax[0]}+{ax[1]} a {g_jum:.1f} u, sous "
                        f"le plancher de {A.JOUR_MIN:.0f}")

    print("\n" + "=" * 70)
    for n in notes:
        print(f"NOTE  {n}")
    if anomalies:
        print(f"\n{len(anomalies)} ANOMALIE(S)")
        for a in anomalies:
            print(f"  - {a}")
    if non_mesures:
        print(f"\n{len(non_mesures)} NON MESURE(S), ce ne sont pas des zeros")
        for x in non_mesures:
            print(f"  - {x}")
    if not anomalies:
        print("\nAucune anomalie parmi ce qui a ete mesure."
              if non_mesures else "\nAucune anomalie.")
    if temoin:
        if not source_la:
            print("\nTEMOIN NON MESURE : sans la source amont, la section 3 "
                  "ne peut pas mordre.")
            return 2
        if not anomalies:
            print("\nATTENTION : le mode temoin n'a rien signale. Un controle "
                  "qui ne sait pas echouer ne prouve rien.")
            return 1
        return 0
    if anomalies:
        return 1
    return 2 if non_mesures else 0


if __name__ == "__main__":
    sys.exit(main("--temoin" in sys.argv, "--sans-source" in sys.argv))
