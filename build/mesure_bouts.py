"""Passe B : les quatre demandes d'espacement, mesurees ensemble.

Points ouverts 56 (le lot 5 ouvre son couloir), 39 (le l et le S capitale),
47 (le s comme second membre) et le z du lot 2. Nicolas a decide au vingt-sixieme
tour de les grouper : les quatre demandent le meme geste, une table de paires
bornee sur un bout coupe, et une seule passe les traite mieux que quatre.

CE QUE CETTE PASSE MESURE.

Pour chaque paire (cible, voisin) et (voisin, cible), sur les huit masters des
deux sources, dans l'etat ou LES VINGT-DEUX GESTES COEXISTENT :

  - l'OUVERTURE, sur la bande de jugement : ce que la coupe a cree comme blanc ;
  - la BORNE, sur la bande pleine : ce qu'on peut refermer sans passer sous le
    couloir d'Atkinson ;
  - la VALEUR, par `approches.paire_bornee` elle-meme et non par un critere
    recopie. Le projet a paye deux fois un seuil recopie qui divergeait.

Elle n'ecrit rien. Son objet est de dire ce qui est POSSIBLE, pour que Nicolas
dise ce qui est VOULU — en particulier sur le s, dont la demande du vingt-
quatrieme tour est « a rapprocher tres legerement » et n'a jamais ete chiffree.

POURQUOI L'ETAT LU EST `Temoin.glyphs` ET NON UN GESTE APPLIQUE SEUL.

Un garde-fou qui applique UN geste a la fois est aveugle a toute paire dont les
DEUX membres portent un geste. C'est le point ouvert 52, paye trois fois : `A+X`
est passee sous le plancher dans les huit masters sans qu'aucune passe de
balayage puisse la voir, et c'est le generateur, qui lit l'etat ecrit, qui l'a
rendue. Ici SIX des huit cibles sont voisines les unes des autres — `z+s`,
`C+C`, `C+Q`, `c+o`, `l+s`, `S+s` — donc l'etat ecrit est le seul etat mesurable.

LE CONTROLE DE ZONE DE DIVERGENCE, ET POURQUOI IL EST ICI.

Le point ouvert 55 est ferme au trente-et-unieme tour comme limite connue : sur
les deux tables servies, le minorant n'a coute aucune unite, parce que leur
decision se prend au plancher de 24 unites, au-dela de la zone ou le minorant
diverge du couloir exact. **La table de cette passe est bornee par Atkinson et
non par un plancher**, donc sa decision se prend pres de l'etat non ecarte, et
le resultat du point 55 ne s'y transporte pas. Le controle porte donc sur les
seules paires ou il PEUT se tromper, et cet ensemble se determine au lieu de se
supposer : le defaut exige qu'une des deux lettres presente deux intervalles
d'encre disjoints a une meme hauteur. `lobes_disjoints` les inventorie master
par master, et `couloir_exact` ne tourne que sur ces paires.

Usage :
    python3 mesure_bouts.py roman                 # les quatre masters romains
    python3 mesure_bouts.py roman Bold            # un seul master
    python3 mesure_bouts.py italic Italic Bold\\ Italic
"""

import os
import sys
import time
from collections import defaultdict

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

import glyphsLib

import approches as A
import dessin as D
from balayage_lot4b import couloir_exact
from check_approches import AMONT, TEMOIN, MASTERS, VOISINS_F as VOISINS, mid

#: Les huit cibles des quatre demandes groupees.
#:
#: Lot 5, point 56 : c, C, G, Q, dont les deux bouts visent le centre de leur
#: anneau. Lot 2 : z, coupe de 12 degres sur ses deux bouts libres. Point 39 :
#: l, coupe de 20 degres sur son bout de hampe, et S capitale, dont le bout bas
#: gauche recule. Point 47 : s, comme SECOND membre.
CIBLES = ("c", "C", "G", "Q", "z", "l", "s", "S")

#: Le s ne se demande qu'en second membre. La demande du vingt-quatrieme tour
#: porte sur le blanc AVANT le s, pas apres : c'est son bout bas gauche qui
#: recule. Le sens (s, voisin) est mesure quand meme et rapporte a part, parce
#: qu'une table de paires se lit dans les deux sens et qu'un chiffre non mesure
#: ne se devine pas.
SECOND_SEULEMENT = ("s",)


def lobes_disjoints(src, noms):
    """Les glyphes qui presentent deux intervalles d'encre a une meme hauteur.

    C'est la condition NECESSAIRE du defaut du point 55 : `couloir_plein`
    compare le bord le plus a droite de a au bord le plus a gauche de b, ce qui
    est le couloir vrai tant que chaque lettre n'a qu'un intervalle. Determiner
    cet ensemble evite de faire tourner `couloir_exact` sur des milliers de
    paires ou il ne peut rien changer, et evite surtout de SUPPOSER qu'il ne
    peut rien changer.

    Rend {nom: (nombre de hauteurs concernees, plus grand nombre d'intervalles)}.
    """
    out = {}
    for nom in noms:
        try:
            cs = src.contours(nom)
        except Exception:
            continue
        if not cs:
            continue
        n_h, pire = 0, 1
        for y in A.bandes(A.DESC, A.ASC):
            xs = A.croisements(cs, y)
            if len(xs) > 2:
                n_h += 1
                pire = max(pire, len(xs) // 2)
        if n_h:
            out[nom] = (n_h, pire)
    return out


def volet(cle_src, masters):
    chemin_a, chemin_t = AMONT[cle_src], TEMOIN[cle_src]
    if not os.path.exists(chemin_a):
        print(f"  {cle_src} : source amont absente ({chemin_a}), RIEN DE "
              "MESURE. Ce n'est pas un succes, c'est une passe non faite.")
        return None
    amont = glyphsLib.GSFont(chemin_a)
    tem = glyphsLib.GSFont(chemin_t)

    res = {}
    for mn in masters:
        t0 = time.time()
        sa, st = D.Source(amont, mn), D.Source(tem, mn)
        ma, mt = mid(amont, mn), mid(tem, mn)

        noms = set()
        for c in CIBLES:
            if tem.glyphs[c] is not None:
                noms.add(c)
        for v in VOISINS:
            n = v if len(v) > 1 else D.nom_glyphe(amont, v)
            if n and tem.glyphs[n] is not None:
                noms.add(n)
        lobes = lobes_disjoints(st, sorted(noms))

        par_cible = defaultdict(list)
        internes, divergences, s_second = [], [], []
        ecarts_critere = []
        n_mes, n_exact = 0, 0
        vues = set()

        for cible in CIBLES:
            if tem.glyphs[cible] is None:
                continue
            for v in VOISINS:
                nom = v if len(v) > 1 else D.nom_glyphe(amont, v)
                if nom is None or tem.glyphs[nom] is None:
                    continue
                sens = ((nom, cible),) if cible in SECOND_SEULEMENT else \
                       ((nom, cible), (cible, nom))
                if cible in SECOND_SEULEMENT:
                    sens = sens + ((cible, nom),)
                for a, b in sens:
                    if (a, b) in vues:
                        continue
                    vues.add((a, b))
                    try:
                        # LES DEUX CRENAGES, ET C'EST LA CORRECTION DE FOND.
                        #
                        # Un premier jet passait le crenage d'Atkinson aux deux
                        # etats. Il rendait 11 paires ouvertes en ExtraLight
                        # quand le point 56 en annonce ZERO, toutes avec le F
                        # pour premier membre et toutes a 105 unites : il
                        # mesurait le recul de la barre mediane du F, point
                        # ouvert 40, que `paires_F.py` referme deja. Ce que
                        # cette passe doit mesurer est ce qui reste ouvert dans
                        # l'ETAT SERVI, donc avec le crenage que les tables du
                        # projet ecrivent. Meme forme que la section 2 de
                        # `check_approches`, et meme raison.
                        ka = A.kern(amont, ma, a, b)
                        kt = A.kern(tem, mt, a, b)
                        oa, _ = A.inter_lettre(sa, a, b, ka)
                        ot, _ = A.inter_lettre(st, a, b, kt)
                        pa = A.couloir_plein(sa, a, b, ka)
                        pt = A.couloir_plein(st, a, b, kt)
                    except Exception:
                        continue
                    if None in (oa, ot, pa, pt):
                        continue
                    n_mes += 1
                    ouverture = ot - oa
                    if ouverture < A.SEUIL_PAIRE:
                        continue
                    borne = pt - pa
                    deja = abs(kt - ka) > 0.5
                    # Le critere du projet, applique a l'etat courant : le plus
                    # petit de ce que la coupe a ouvert et de ce qu'on peut
                    # refermer sans passer sous Atkinson. C'est `paire_bornee`
                    # dans sa forme, et l'egalite avec elle est VERIFIEE plus
                    # bas sur toute paire que rien n'a encore crenee — un seuil
                    # recopie devient un desaccord, le projet l'a paye deux fois.
                    val = -round(min(ouverture, borne), 1)
                    if min(ouverture, borne) < A.SEUIL_PAIRE:
                        val = None
                    if not deja:
                        ref = A.paire_bornee(sa, st, a, b, ka)
                        if (ref is None) != (val is None) or (
                                ref is not None and val is not None
                                and abs(ref - val) > 0.05):
                            ecarts_critere.append((a, b, val, ref))

                    # Zone de divergence. La condition necessaire du defaut est
                    # large — toute lettre fermee presente deux parois a une
                    # meme hauteur — donc le filtre par lobe ne discrimine
                    # presque rien et l'exact tourne sur toutes les paires
                    # retenues. Elles sont peu nombreuses, la mesure est donc
                    # gratuite et complete.
                    xa = couloir_exact(sa, a, b, ka)
                    xt = couloir_exact(st, a, b, kt)
                    n_exact += 1
                    if xa is not None and xt is not None:
                        b_ex = xt - xa
                        if abs(b_ex - borne) > 0.05:
                            divergences.append((a, b, borne, b_ex, val))

                    ligne = (a, b, ouverture, borne, val, deja)
                    par_cible[cible].append(ligne)
                    if a in CIBLES and b in CIBLES:
                        internes.append(ligne)
                    if b == "s":
                        s_second.append(ligne)

        print(f"\n{'='*78}")
        print(f"=== {cle_src} / {mn}   ({n_mes} paire-masters mesurees, "
              f"{n_exact} verifiees au couloir exact)")
        if lobes:
            det = ", ".join(f"{n} ({v[0]} hauteurs, {v[1]} intervalles)"
                            for n, v in sorted(lobes.items()))
            print(f"    lobes disjoints dans ce master : {det}")
        else:
            print("    aucun glyphe a lobe disjoint : le minorant est exact "
                  "sur toutes ces paires")

        print(f"\n    {'cible':6s} {'ouvertes':>9s} {'pire ouv.':>10s} "
              f"{'pire borne':>11s} {'refermable':>11s} {'deja crenees':>13s}")
        for cible in CIBLES:
            L = par_cible.get(cible, [])
            if not L:
                print(f"    {cible:6s} {0:>9d}")
                continue
            pire_o = max(x[2] for x in L)
            pire_b = max(x[3] for x in L)
            refer = sum(1 for x in L if x[4] is not None)
            ndeja = sum(1 for x in L if x[5])
            print(f"    {cible:6s} {len(L):>9d} {pire_o:>10.1f} "
                  f"{pire_b:>11.1f} {refer:>11d} {ndeja:>13d}")

        tot = sum(len(v) for v in par_cible.values())
        print(f"\n    TOTAL {tot} paire(s) ouverte(s) au-dela de "
              f"{A.SEUIL_PAIRE:.0f} unites")

        # Les plus ouvertes par cible, nommees. Un compte ne dit pas quelle
        # paire paie, et c'est la paire qui se juge en navigateur.
        for cible in CIBLES:
            L = sorted(par_cible.get(cible, []), key=lambda x: -x[2])[:4]
            if not L:
                continue
            det = ", ".join(
                f"{a}+{b} {o:+.0f}/{bo:+.0f}"
                + ("" if v is None else "")
                for a, b, o, bo, v, dj in L)
            print(f"      {cible:3s} (ouv./borne) : {det}")

        if internes:
            print(f"\n    PAIRES INTERNES ({len(internes)}), dont les deux "
                  "membres portent un geste :")
            for a, b, o, bo, val, dj in sorted(internes,
                                               key=lambda x: -x[2]):
                sv = "rien" if val is None else f"{val:+.1f}"
                print(f"      {a}+{b:<14s} ouvre {o:+7.1f}   borne "
                      f"{bo:+7.1f}   valeur {sv}"
                      + ("   (deja crenee)" if dj else ""))

        if s_second:
            print(f"\n    LE s EN SECOND ({len(s_second)} paires), "
                  "point ouvert 47 :")
            vals = [x[4] for x in s_second if x[4] is not None]
            print(f"      ouverture de {min(x[2] for x in s_second):.1f} a "
                  f"{max(x[2] for x in s_second):.1f} unites")
            if vals:
                print(f"      la borne pleine permet de refermer de "
                      f"{-max(vals):.1f} a {-min(vals):.1f} unites "
                      f"sur {len(vals)} paire(s)")
            else:
                print("      la borne pleine ne permet de refermer aucune "
                      "paire : marge nulle")
            for a, b, o, bo, val, dj in sorted(s_second,
                                               key=lambda x: -x[2])[:8]:
                sv = "rien" if val is None else f"{val:+.1f}"
                print(f"      {a}+{b:<14s} ouvre {o:+7.1f}   borne "
                      f"{bo:+7.1f}   valeur {sv}")

        if divergences:
            print(f"\n    ZONE DE DIVERGENCE : {len(divergences)} paire(s) ou "
                  "le minorant borne autrement que le couloir exact")
            for a, b, bp, bx, val in divergences:
                sv = "rien" if val is None else f"{val:+.1f}"
                print(f"      {a}+{b:<14s} borne minorant {bp:+8.2f}   "
                      f"exact {bx:+8.2f}   ecart {bx - bp:+8.2f}   "
                      f"valeur retenue {sv}")
        elif n_exact:
            print(f"\n    zone de divergence : aucune, sur {n_exact} paire(s) "
                  "retenue(s) et toutes verifiees")

        if ecarts_critere:
            print(f"\n    ALERTE : {len(ecarts_critere)} paire(s) ou mon "
                  "calcul s'ecarte de `paire_bornee`. Le critere a derive.")
            for a, b, v, r in ecarts_critere:
                print(f"      {a}+{b:<14s} ici {v}   paire_bornee {r}")
        else:
            print("    critere : accord exact avec `paire_bornee` sur toute "
                  "paire que rien n'a encore crenee")

        res[mn] = dict(par_cible=dict(par_cible), internes=internes,
                       s_second=s_second, divergences=divergences,
                       n_mes=n_mes, n_exact=n_exact, lobes=lobes,
                       duree=time.time() - t0)
        print(f"\n    ({res[mn]['duree']:.0f} s)")
    return res


if __name__ == "__main__":
    cle = sys.argv[1] if len(sys.argv) > 1 else "roman"
    ms = sys.argv[2:] or MASTERS[cle]
    print("=" * 78)
    print("=== PASSE B : les quatre demandes d'espacement groupees")
    print(f"=== cibles : {', '.join(CIBLES)}")
    print(f"=== voisins : {len(VOISINS)}, les deux sens, etat ou les "
          "vingt-deux gestes coexistent")
    print("=" * 78)
    volet(cle, ms)
