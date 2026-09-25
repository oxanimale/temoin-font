#!/usr/bin/env python3
"""LE CONTROLE DE LA TRANSLATION DES HUIT OPERATEURS, cinquante-troisieme tour.

    python3 check_operateurs.py

CINQ SECTIONS ET UN TEMOIN. Il lit l'etat ECRIT, `Temoin.glyphs` et son
italique, et le compare a la source amont : la translation est exacte par
construction, donc toute exigence se pose en valeur absolue et non en tendance.

POURQUOI UN CONTROLE A LUI, ET NON UNE SECTION DE `check_perimetre`. Celui-la
mesure le PERIMETRE DU TITRAGE -- quels glyphes le geste attrape, avec quelle
sortante, et lesquels en sont ecartes. Une translation n'est pas un geste de
titrage : elle ne coupe rien, ne designe aucune terminaison et n'a pas de
perimetre geometrique. L'y loger aurait mis une mesure hors sujet dans un
controle deja a quatorze sections, comme `HORS_TITRAGE` etait le mauvais endroit
pour les formes fermees au quarante-septieme tour.

CE QUE LA SECTION 5 EXISTE POUR DIRE, ET QUI N'ETAIT SURVEILLE NULLE PART. Une
translation verticale ne touche AUCUNE chasse et AUCUN crenage : elle est donc
invisible a tout ce que ce projet mesure. Pire, le zero-diff des trois tables de
paires, qui est vrai, est une CECITE et non une preuve -- mesure au meme tour :
`inventaire_bouts`, `inventaire_F` et `inventaire_pieds` partagent 81 voisins et
AUCUN des huit operateurs n'y figure, ni en cible ni en voisin. C'est exactement
le defaut du 9 au quarante-quatrieme tour, qui plongeait depuis quatre tours
sans qu'aucun garde-fou le regarde, et dont le zero-diff disait la meme chose
rassurante. La section 5 mesure donc elle-meme ce que la montee ouvre et ferme.

LA BANDE DE MESURE EST LA BANDE PLEINE, ET CE N'EST PAS UN DETAIL. Les huit
montent jusqu'a 560 unites, soit 64 au-dessus de la hauteur d'x. Une mesure de
couloir posee sur `A.XH` ne verrait pas cette matiere -- c'est le defaut qui a
laisse passer six contacts de capitales au vingt-quatrieme tour, le garde-fou
mesurant jusqu'a la hauteur d'x quand la barre du F monte a 668.
`couloir_exact` balaie de `A.DESC` a `A.ASC`, soit -320 a 800, et c'est pour
cela qu'il est employe ici plutot que `A.couloir_plein`, qui est en outre un
minorant et non un couloir.
"""

import os
import sys

import glyphsLib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import approches as A
import dessin as D
import lot2 as L
import operateurs as OP
from balayage_lot4b import couloir_exact
from check_approches import AMONT, MASTERS, mid

ICI = os.path.dirname(os.path.abspath(__file__))
TEMOIN = {"roman": os.path.join(ICI, "Temoin.glyphs"),
          "italic": os.path.join(ICI, "Temoin-Italic.glyphs")}

#: Ce que le projet fait plonger de 32 unites et que Nicolas a GARDE au
#: cinquante-deuxieme tour, apres les avoir relus dans la meme phrase que le
#: `plus`. Ils ont la meme cause que lui -- la cible deduite de la casse du nom
#: -- et pas la meme decision, donc ils sont surveilles ici : un geste futur qui
#: les emporterait ne serait signale par rien d'autre.
PLONGENT_ENCORE = {"plusminus": -32.0, "numbersign": -32.0}

#: L'echantillon de voisins de la section 5. Il n'est pas pris au hasard : la
#: translation MONTE la matiere, donc le risque vit en haut, et ces voisins sont
#: choisis pour ce qu'ils presentent a cette hauteur -- une capitale a fut, une
#: capitale a barre haute, une diagonale, deux chiffres, une parenthese qui
#: monte plus haut que tout, et un bas de casse qui n'y monte pas, comme temoin
#: negatif. Les huit sont mesures dans LES DEUX SENS : un operateur est presque
#: toujours entre deux choses.
VOISINS = ("H", "T", "A", "zero", "eight", "parenleft", "parenright", "x")

#: En dessous de quoi un couloir ne doit pas descendre. Partage avec
#: `approches`, et non recopie : un controle qui tient son propre seuil finit
#: par signaler ce que la table ecarte volontairement.
JOUR_MIN = 24.0


def _charger():
    out = {}
    for cle in ("roman", "italic"):
        out[cle] = (glyphsLib.load(open(AMONT[cle], encoding="utf-8")),
                    glyphsLib.load(open(TEMOIN[cle], encoding="utf-8")))
    return out


def _boite(font, nom, mname):
    g = font.glyphs[nom]
    if g is None:
        return None
    m = [x for x in font.masters if x.name == mname]
    if not m:
        return None
    lay = next((l for l in g.layers if l.layerId == m[0].id), None)
    if lay is None:
        return None
    ys = [n.position.y for p in L.paths(lay) for n in p.nodes]
    return (min(ys), max(ys)) if ys else None


def _chasse(font, nom, mname):
    g = font.glyphs[nom]
    m = [x for x in font.masters if x.name == mname]
    if g is None or not m:
        return None
    lay = next((l for l in g.layers if l.layerId == m[0].id), None)
    return None if lay is None else lay.width


def section1(src, attendu=OP.MONTEE):
    """1. LES HUIT VALENT-ILS ATKINSON PLUS 64, NI PLUS NI MOINS ?

    L'exigence est posee contre la SOURCE AMONT et non contre l'etat servi, et
    cela couvre deux choses d'un coup. La montee, evidemment. Mais aussi que le
    `plus` est bien REPARTI DU DESSIN D'ATKINSON : s'il avait garde sa plongee
    de 32 unites, son ymin sortirait a +32 quand son ymax sort a +64, et la
    ligne creverait. C'est le temoin naturel du retrait, et il ne demande aucun
    montage.
    """
    print(f"\n1. les huit valent Atkinson + {attendu:.0f}, en ymin et en ymax")
    anomalies = 0
    for cle, (amont, tem) in src.items():
        ecarts = []
        for nom in OP.OPERATEURS:
            for mn in MASTERS[cle]:
                ba, bt = _boite(amont, nom, mn), _boite(tem, nom, mn)
                if ba is None or bt is None:
                    print(f"     !! {nom} {mn} : NON MESURE, calque absent")
                    anomalies += 1
                    continue
                for i, (a, b) in enumerate(zip(ba, bt)):
                    d = b - a
                    if abs(d - attendu) > OP.TOL:
                        ecarts.append((nom, mn, "ymin" if i == 0 else "ymax",
                                       d))
        print(f"  {cle} : {len(OP.OPERATEURS)} operateur(s) x "
              f"{len(MASTERS[cle])} master(s) x 2 bords, "
              f"{len(ecarts)} ecart(s)")
        for nom, mn, bord, d in ecarts[:8]:
            print(f"     !! {nom} {mn} {bord} : {d:+.2f} u pour "
                  f"{attendu:+.1f} attendues")
        if len(ecarts) > 8:
            print(f"     … et {len(ecarts) - 8} autre(s)")
        anomalies += len(ecarts)
    return anomalies


def section2(src):
    """2. LES QUATRE QUI NE MONTENT PAS SONT-ILS ENCORE EN PLACE ?

    Le `plusminus`, le `hyphen`, le `endash` et le `emdash` restent a leur
    ordonnee d'Atkinson : c'est une DECISION de Nicolas et non un reste, donc
    elle se surveille. Le `plusminus` et le `numbersign` gardent en outre leur
    plongee de 32 unites, qui a la meme cause que celle du `plus` et pas la meme
    decision -- `PLONGENT_ENCORE` porte les deux chiffres.
    """
    print("\n2. les quatre qui ne montent pas, et les deux qui plongent encore")
    anomalies = 0
    for cle, (amont, tem) in src.items():
        mauvais = []
        for nom in OP.FIXES + tuple(PLONGENT_ENCORE):
            attendu_min = PLONGENT_ENCORE.get(nom, 0.0)
            for mn in MASTERS[cle]:
                ba, bt = _boite(amont, nom, mn), _boite(tem, nom, mn)
                if ba is None or bt is None:
                    mauvais.append((nom, mn, "absent", 0.0))
                    continue
                if abs((bt[0] - ba[0]) - attendu_min) > OP.TOL:
                    mauvais.append((nom, mn, "ymin", bt[0] - ba[0]))
                if abs(bt[1] - ba[1]) > OP.TOL:
                    mauvais.append((nom, mn, "ymax", bt[1] - ba[1]))
        print(f"  {cle} : {len(OP.FIXES) + len(PLONGENT_ENCORE)} signe(s) "
              f"surveille(s), {len(mauvais)} ecart(s)")
        for nom, mn, bord, d in mauvais[:8]:
            print(f"     !! {nom} {mn} {bord} : {d:+.2f} u")
        anomalies += len(mauvais)
    return anomalies


def section3(src):
    """3. LA TRANSLATION A-T-ELLE TOUCHE UNE CHASSE ?

    Elle ne doit en toucher aucune : c'est ce qui la rend sure, et c'est ce qui
    la rend invisible. La verifier vaut d'etre ecrit parce que le projet a
    modifie une chasse une fois, au vingt-troisieme tour sur le F, et l'a
    retiree au vingt-quatrieme apres qu'elle eut cree six contacts que le
    garde-fou ne pouvait pas voir.
    """
    print("\n3. aucune chasse n'est touchee")
    anomalies = 0
    noms = OP.OPERATEURS + OP.FIXES + tuple(PLONGENT_ENCORE)
    for cle, (amont, tem) in src.items():
        mauvais = []
        for nom in noms:
            for mn in MASTERS[cle]:
                wa, wt = _chasse(amont, nom, mn), _chasse(tem, nom, mn)
                if wa is None or wt is None or abs(wa - wt) > OP.TOL:
                    mauvais.append((nom, mn, wa, wt))
        print(f"  {cle} : {len(noms)} signe(s) x {len(MASTERS[cle])} "
              f"master(s), {len(mauvais)} chasse(s) modifiee(s)")
        for nom, mn, wa, wt in mauvais[:6]:
            print(f"     !! {nom} {mn} : {wa} -> {wt}")
        anomalies += len(mauvais)
    return anomalies


def section4(src):
    """4. LA BARRE DU + EST-ELLE A 312, ET SON PIED EST-IL REMONTE ?

    C'est l'etat E, celui que Nicolas a retenu sur `etats-plus.html` contre
    quatre autres. La barre se lit par les ordonnees DISTINCTES du glyphe, et
    non par une boite : au Regular romain elles passent de [-32, 0, 208, 288,
    496] a [64, 272, 352, 560], donc la plongee disparait et le centre de la
    barre vaut (272 + 352) / 2 = 312. La mesure est faite master par master, la
    barre s'epaississant avec la graisse.
    """
    print("\n4. la barre du + et la disparition de sa plongee")
    anomalies = 0
    for cle, (amont, tem) in src.items():
        for mn in MASTERS[cle]:
            ga = [x for x in amont.glyphs["plus"].layers
                  if x.layerId == mid(amont, mn)][0]
            gt = [x for x in tem.glyphs["plus"].layers
                  if x.layerId == mid(tem, mn)][0]
            ya = sorted({round(n.position.y, 1)
                         for p in L.paths(ga) for n in p.nodes})
            yt = sorted({round(n.position.y, 1)
                         for p in L.paths(gt) for n in p.nodes})
            # La barre horizontale est la paire d'ordonnees interieure : le
            # glyphe en a quatre distinctes, bas du fut, bas de barre, haut de
            # barre, haut du fut.
            if len(ya) != 4 or len(yt) != 4:
                print(f"     !! plus {cle} {mn} : {len(ya)} ordonnee(s) amont "
                      f"et {len(yt)} ecrite(s), 4 attendues de chaque cote")
                anomalies += 1
                continue
            ca, ct = (ya[1] + ya[2]) / 2, (yt[1] + yt[2]) / 2
            ok = abs(ct - (ca + OP.MONTEE)) <= OP.TOL
            print(f"  {cle} {mn:<18} barre {ca:.1f} -> {ct:.1f}"
                  f"   pied {ya[0]:.1f} -> {yt[0]:.1f}"
                  f"{'' if ok else '   !! ECART'}")
            if not ok:
                anomalies += 1
    return anomalies


def _sans_montee(font):
    """L'etat ECRIT avec les huit redescendus de `MONTEE`. Modifie sur place.

    C'EST LA REFERENCE QUI ISOLE LA TRANSLATION, et le premier jet de la
    section 5 ne l'avait pas : il comparait a la SOURCE AMONT, ce qui melange
    la montee avec tout ce que le projet a fait au VOISIN. Le piege est ecrit
    dans la passation -- un glyphe qu'on croit deplace peut etre intact, son
    voisin de contour ayant bouge -- et il visait juste : la paire la plus
    resserree de cette section met en face un T, qui porte la coupe de ses deux
    bouts de barre depuis le onzieme tour. Ici la mesure a disculpe le T, qui
    rend exactement la valeur d'Atkinson, mais l'imputation etait due au hasard
    du repertoire et non a la mesure. La translation inverse la rend exacte par
    construction, et elle reste juste apres la recompilation, quand l'etat
    ecrit sera devenu l'etat servi.
    """
    for nom in OP.OPERATEURS:
        g = font.glyphs[nom]
        if g is None:
            continue
        for lay in g.layers:
            OP.monter_calque(lay, -OP.MONTEE)
    return font


def _hauteur_min(sa, a, b):
    """La hauteur ou le couloir est le plus etroit, pour dire OU ca se referme.

    Un scalaire cache l'essentiel -- le projet l'a paye huit fois -- et ici la
    valeur seule ne dit pas si la fermeture vient du bras haut de l'operateur
    ou d'autre chose. Le balayage reprend celui de `couloir_exact`, en gardant
    la hauteur au lieu du seul minimum.
    """
    w = sa.layer(a).width
    ca, cb = sa.contours(a), sa.contours(b)
    best = (None, None)
    for y in A.bandes(A.DESC, A.ASC):
        xa, xb = A.croisements(ca, y), A.croisements(cb, y)
        if not xa or not xb:
            continue
        d = (w + xb[0]) - xa[-1]
        if best[0] is None or d < best[0]:
            best = (d, y)
    return best[1]


def section5(src):
    """5. CE QUE LA MONTEE OUVRE ET FERME, MESURE PUISQUE RIEN NE LE MESURE.

    Couloir vrai entre chaque operateur et huit voisins, dans les deux sens, sur
    la bande pleine et sans crenage -- les huit n'en portent aucun, ce que la
    section verifie en passant puisqu'elle mesure a k = 0 des deux cotes et
    compare des ecarts.

    LA REFERENCE EST L'ETAT ECRIT REDESCENDU DE 64, et non la source amont :
    voir `_sans_montee`. L'ecart imprime est donc imputable a la translation et
    a elle seule.

    ELLE NE PEUT PAS EXIGER « JAMAIS PLUS SERRE QU'AVANT », et c'est le meme
    raisonnement qu'au vingt-cinquieme tour : le geste RESSERRE par
    construction du cote ou il monte, donc cette exigence reviendrait a
    l'annuler. Elle exige le PLANCHER DE JOUR, 24 unites, qui est le seuil que
    le projet emploie depuis le dix-septieme tour. Ce qui reste au-dessus du
    plancher est imprime comme un COUT, pas comme une anomalie : Nicolas a
    tranche la montee sur des binaires compiles, en connaissant son prix.
    """
    print("\n5. les couloirs devant et derriere les huit, bande pleine")
    anomalies = 0
    for cle, (_amont, tem) in src.items():
        avant = _sans_montee(glyphsLib.load(open(TEMOIN[cle],
                                                 encoding="utf-8")))
        pire, sous = [], []
        for mn in MASTERS[cle]:
            s0, st = D.Source(avant, mn), D.Source(tem, mn)
            for op in OP.OPERATEURS:
                for v in VOISINS:
                    if tem.glyphs[v] is None:
                        continue
                    for a, b in ((op, v), (v, op)):
                        c0 = couloir_exact(s0, a, b)
                        ct = couloir_exact(st, a, b)
                        if ct < JOUR_MIN:
                            sous.append((mn, a, b, c0, ct))
                        pire.append((ct - c0, mn, a, b, c0, ct))
        pire.sort()
        print(f"  {cle} : {len(pire)} paire-master(s) mesuree(s), "
              f"{len(sous)} sous le plancher de {JOUR_MIN:.0f} u")
        for d, mn, a, b, c0, ct in pire[:5]:
            y = _hauteur_min(D.Source(tem, mn), a, b)
            oy = f" a y = {y:.0f}" if y is not None else ""
            print(f"     le plus resserre : {a}+{b} {mn}  "
                  f"sans montee {c0:.1f} -> avec {ct:.1f}  ({d:+.1f}){oy}")
        for mn, a, b, c0, ct in sous[:8]:
            print(f"     !! SOUS LE PLANCHER : {a}+{b} {mn}  "
                  f"{c0:.1f} -> {ct:.1f}")
        anomalies += len(sous)
    return anomalies


def temoin(src):
    """LE TEMOIN. La section 1 rejouee avec une attente de ZERO.

    Elle doit alors crier sur les seize bords de chaque source -- huit
    operateurs, deux bords, et le compte se fait par master. Si elle se tait, la
    mesure ne mesure plus, et les quatre premieres sections sont muettes sans
    que leur zero le dise. C'est la forme de temoin que le projet emploie depuis
    `shape_check_kern` : ne pas verifier que le controle passe, verifier qu'il
    SAIT ECHOUER.
    """
    print("\n--- TEMOIN : la section 1 rejouee en exigeant +0,0 ---")
    attendu = sum(len(OP.OPERATEURS) * len(MASTERS[c]) * 2 for c in src)
    n = section1(src, attendu=0.0)
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
    for f in (section1, section2, section3, section4, section5):
        total += f(src)
    print(f"\nTOTAL : {total} anomalie(s).")
    total += temoin(src)
    sys.exit(1 if total else 0)
