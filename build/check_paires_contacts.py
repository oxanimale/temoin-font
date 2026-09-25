#!/usr/bin/env python3
"""Le controle de `paires_contacts.py` : la table est-elle SERVIE, et tient-elle ?

POURQUOI UN CONTROLE A PART. `check_approches` coute deja 126 secondes, et le
plafond d'un appel du bac a sable est de 180 : y loger une section qui mesure
un couloir exact sur 117 entrees ferait sauter le plafond au milieu d'une
chaine. Le projet loge un controle par objet depuis `check_barre_F`.

CE QU'IL VERIFIE, et chaque section repond a une question que le tour a posee.

    1. LA TABLE EST-ELLE SERVIE ? Chaque entree doit se retrouver dans la
       source du projet, a la valeur ecrite. Deux tables qui ecrivent en valeur
       totale sur la meme cle, la seconde ecrase la premiere : le
       cinquante-quatrieme tour a vu un reglage valide en navigateur
       disparaitre ainsi, en silence, et rien ne le disait.

    2. LES CONTACTS SONT-ILS FERMES ? Le couloir exact de chaque paire doit
       etre positif, ET LA REFERENCE EST ATKINSON, pas zero : `K+idieresis`
       tient -13,4 unites dans la police de base aux deux gras, donc un
       controle qui exigerait un couloir positif crierait sur un etat que le
       projet n'a pas fabrique et qu'il ne peut pas fermer sans etre plus
       serre que sa base. Le vingt-septieme tour a paye cinq fausses alertes
       de cette sorte, et un garde-fou qui crie a tort finit par etre ignore.
       Les paires sous le plancher sans contact sont imprimees avec le critere
       que la table leur donne -- une paire bornee par le couloir d'Atkinson y
       reste par decision, pas par oubli.

    3. LES ENTREES DE GROUPE SONT-ELLES ENCORE JUSTIFIEES ? Une valeur ecrite
       sur une cle de groupe se propage a tous les membres ; elle n'est juste
       que tant qu'ils ont la meme gouttiere devant ce voisin. Un geste futur
       sur un seul membre defait cette egalite sans que rien ne le dise, et la
       section 9 de `check_approches` remesure le reglage `X+A` pour la meme
       raison depuis le cinquante-sixieme tour.

LE TEMOIN RETIRE LA TABLE et exige que la section 2 signale. Il agit sur ce que
le controle mesure, et dans le sens ou le controle cherche le defaut : un
temoin general qui n'exercerait pas la bonne section rendrait zero sans rien
prouver, ce que le cinquante-sixieme tour a paye sur deux controles le meme
jour.

    python3 check_paires_contacts.py
    python3 check_paires_contacts.py --temoin
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
from paires_contacts import PAIRES_CONTACTS                   # noqa: E402

#: LU chez `mesure_point18`, qui le possede, et non recopie : le controle et
#: le producteur doivent juger une famille au meme critere, sinon le controle
#: valide une table que son producteur n'ecrirait plus.
TOL_FAMILLE = MP.TOL_FAMILLE


def sources():
    """(label, amont, servi) pour les deux sources, ou un NON MESURE."""
    out = []
    for lab, amont, projet, _b in MT.SOURCES:
        if not (os.path.exists(amont) and os.path.exists(projet)):
            print(f"  {lab} : source absente. Ce n'est pas un zero, c'est un "
                  f"NON MESURE.")
            out.append((lab, None, None))
            continue
        out.append((lab, glyphsLib.GSFont(amont), glyphsLib.GSFont(projet)))
    return out


def section1(paires):
    """1. LA TABLE EST-ELLE SERVIE, valeur par valeur ?"""
    print("\n1. la table est-elle servie, entree par entree")
    anomalies = 0
    for lab, _amont, servi in paires:
        if servi is None:
            anomalies += 1
            continue
        manque, ecrasees = [], []
        n = 0
        for m in servi.masters:
            for a, b, val, cle, _crit in PAIRES_CONTACTS.get(m.name, ()):
                if servi.glyphs[a] is None or servi.glyphs[b] is None:
                    continue
                n += 1
                vu = A.kern(servi, m.id, a, b)
                if vu is None:
                    manque.append(f"{a}+{b}/{m.name}")
                elif abs(vu - val) > 0.01:
                    ecrasees.append(f"{a}+{b}/{m.name} {val:+.0f} -> {vu:+.0f}")
        print(f"  {lab} : {n} entree(s) mesuree(s), {len(manque)} absente(s), "
              f"{len(ecrasees)} ecrasee(s) par une autre etape")
        for x in (manque + ecrasees)[:8]:
            print(f"     !! {x}")
        anomalies += len(manque) + len(ecrasees)
    return anomalies


#: Les paires que la section 2 n'a pas su juger. Elles comptaient comme des
#: anomalies jusqu'au soixante-septieme tour ; elles sont un NON MESURE, et
#: `main` les rend par le code 2. Point ouvert 31.
NON_MESUREES = []


def section2(paires, retirer=False):
    """2. LES CONTACTS SONT-ILS FERMES ?"""
    print(f"\n2. les contacts sont-ils fermes"
          + (" — TEMOIN, table retiree" if retirer else ""))
    anomalies = 0
    for lab, amont, servi in paires:
        if servi is None:
            anomalies += 1
            continue
        if retirer:
            servi = glyphsLib.GSFont(
                MT.SOURCES[0 if lab == "romain" else 1][2])
            A.retirer_contacts(servi, amont)
        contacts, sous, herites, muets = [], [], [], []
        ida = {m.name: m.id for m in amont.masters} if amont else {}
        for m in servi.masters:
            st = D.Source(servi, m.name)
            sa = D.Source(amont, m.name) if amont else None
            for a, b, _val, _cle, crit in PAIRES_CONTACTS.get(m.name, ()):
                if servi.glyphs[a] is None or servi.glyphs[b] is None:
                    continue
                try:
                    g = couloir_exact(st, a, b, A.kern(servi, m.id, a, b))
                except Exception as exc:                      # noqa: BLE001
                    # Un cas ecarte se DIT. Sans cette trace, une entree que
                    # la mesure ne sait pas juger disparaitrait du compte et
                    # le controle imprimerait un succes pour une paire qu'il
                    # n'a jamais regardee -- le defaut que la relecture du
                    # tour 58 a trouve dans `ecart_reconstruit`.
                    muets.append(f"{a}+{b}/{m.name} ({type(exc).__name__})")
                    continue
                if g is None:
                    muets.append(f"{a}+{b}/{m.name} (pas de couloir)")
                    continue
                ga = None
                if sa is not None and m.name in ida:
                    try:
                        ga = couloir_exact(
                            sa, a, b, A.kern(amont, ida[m.name], a, b))
                    except Exception:                         # noqa: BLE001
                        ga = None
                if g <= 0.0:
                    # La reference est Atkinson : un contact que la police de
                    # base porte deja n'est pas un defaut du projet, et le
                    # signaler comme tel apprendrait a ignorer ce controle.
                    if ga is not None and ga <= 0.0 and g >= ga - 0.5:
                        herites.append(f"{a}+{b}/{m.name} {g:+.1f} "
                                       f"(Atkinson {ga:+.1f})")
                    else:
                        contacts.append(f"{a}+{b}/{m.name} {g:+.1f}"
                                        + ("" if ga is None
                                           else f" (Atkinson {ga:+.1f})"))
                elif g < A.JOUR_MIN:
                    sous.append(f"{a}+{b}/{m.name} {g:+.1f} ({crit})")
        print(f"  {lab} : {len(contacts)} contact(s) du projet, "
              f"{len(herites)} herite(s) d'Atkinson, {len(sous)} paire(s) "
              f"sous le plancher de {A.JOUR_MIN:.0f} mais sans contact, "
              f"{len(muets)} NON MESUREE(S)")
        for x in muets[:6]:
            print(f"     !! NON MESUREE, ce n'est pas un zero : {x}")
        for x in herites[:4]:
            print(f"     note : contact deja dans la police de base, {x}")
        for x in contacts[:8]:
            print(f"     !! CONTACT {x}")
        for x in sous[:4]:
            print(f"     note : {x}")
        if len(sous) > 4:
            print(f"     note : … et {len(sous)-4} autre(s)")
        anomalies += len(contacts)
        NON_MESUREES.extend(muets)
    return anomalies


def section3(paires):
    """3. LES ENTREES DE GROUPE SONT-ELLES ENCORE JUSTIFIEES ?"""
    print("\n3. les entrees de groupe, remesurees sur l'etat ecrit")
    anomalies = 0
    for lab, _amont, servi in paires:
        if servi is None:
            anomalies += 1
            continue
        vues, mauvaises = 0, []
        for m in servi.masters:
            st = D.Source(servi, m.name)
            for a, b, _val, cle, _crit in PAIRES_CONTACTS.get(m.name, ()):
                if cle != "groupe" or servi.glyphs[a] is None:
                    continue
                grp = servi.glyphs[a].rightKerningGroup
                fam = [g.name for g in servi.glyphs
                       if g.rightKerningGroup == grp]
                vals = []
                for n2 in fam:
                    try:
                        v = couloir_exact(st, n2, b,
                                          A.kern(servi, m.id, n2, b))
                    except Exception:                         # noqa: BLE001
                        continue
                    if v is not None:
                        vals.append(v)
                if len(vals) < 2:
                    continue
                vues += 1
                ecart = max(vals) - min(vals)
                if ecart > TOL_FAMILLE:
                    mauvaises.append(f"{a}+{b}/{m.name} ecart {ecart:.1f} u "
                                     f"sur {len(vals)} membre(s)")
        print(f"  {lab} : {vues} entree(s) de groupe remesuree(s), "
              f"{len(mauvaises)} dont la famille a diverge")
        for x in mauvaises[:6]:
            print(f"     !! {x}")
        anomalies += len(mauvaises)
    return anomalies


def section4(paires):
    """4. LES PAIRES SORTIES PAR DECISION TOUCHENT-ELLES ENCORE ?

    `inventaire_contacts.HORS_TABLE` porte les paires que Nicolas a decide de
    ne pas fermer, chacune avec sa raison. Un nom decide et un nom jamais
    regarde sont identiques dans une table : sans cette section, le jour ou un
    geste separerait l'une d'elles, la table continuerait d'annoncer un contact
    assume qui n'existe plus, et personne ne le saurait. Elle ne compte pas
    d'anomalie quand la paire touche -- c'est l'etat voulu -- mais quand elle
    a cesse de toucher, parce que la decision n'a alors plus d'objet.
    """
    from inventaire_contacts import HORS_TABLE

    print("\n4. les paires sorties par decision, remesurees")
    anomalies = 0
    for lab, _amont, servi in paires:
        if servi is None:
            anomalies += 1
            continue
        # LE CRITERE EST PAR PAIRE, PAS PAR GLYPHE-MASTER, et un premier jet
        # s'est trompe la-dessus : ces paires ne touchent que dans les gras,
        # ou la matiere est large. Compter chaque master clair ou elles ne
        # touchent pas rendait 27 anomalies sur un etat voulu, ce qui est le
        # garde-fou qui crie a tort, cinquieme recidive du projet. Une
        # decision n'a plus d'objet quand la paire ne touche dans AUCUN
        # master ; tant qu'elle touche quelque part, la ligne est exacte.
        par_paire = {}
        for m in servi.masters:
            st = D.Source(servi, m.name)
            for (a, b) in HORS_TABLE:
                if servi.glyphs[a] is None or servi.glyphs[b] is None:
                    continue
                try:
                    g = couloir_exact(st, a, b, A.kern(servi, m.id, a, b))
                except Exception:                             # noqa: BLE001
                    continue
                if g is None:
                    continue
                if g <= 0.0:
                    par_paire.setdefault((a, b), []).append(m.name)
        sans_objet = [f"{a}+{b}" for (a, b) in HORS_TABLE
                      if servi.glyphs[a] is not None
                      and servi.glyphs[b] is not None
                      and not par_paire.get((a, b))]
        print(f"  {lab} : {len(HORS_TABLE)} paire(s) sorties, "
              f"{len(par_paire)} touchent encore, "
              f"{len(sans_objet)} ne touchent plus dans aucun master")
        for (a, b), ms in sorted(par_paire.items()):
            print(f"     note : {a}+{b} touche dans {len(ms)} master(s), "
                  f"contact assume")
        for x in sans_objet:
            print(f"     !! la decision n'a plus d'objet : {x}")
        anomalies += len(sans_objet)
    return anomalies


def main(temoin=False):
    """0 conforme, 1 signale, 2 non mesure. En mode temoin, 0 si la section 2
    retrouve des contacts table retiree, 1 sinon, 2 si les sources manquent."""
    paires = sources()
    # UNE SOURCE ABSENTE EST UN NON MESURE, code 2. Jusqu'au soixante-septieme
    # tour, chaque section comptait une anomalie par source absente, huit en
    # tout, et le TEMOIN comptait ces absences comme des contacts retrouves :
    # il se declarait mordant sans avoir rien lu. Point ouvert 31.
    if any(servi is None for _lab, _amont, servi in paires):
        print("\nNON MESURE : sans les deux sources, aucune section ne mesure.")
        return 2
    if temoin:
        # Le temoin exerce la SECTION 2, celle dont le zero doit etre prouve.
        n = section2(paires, retirer=True)
        print(f"\nTEMOIN : {n} contact(s) retrouve(s) table retiree — "
              + ("la section sait signaler" if n else
                 "ELLE NE DISCRIMINE PLUS"))
        return 0 if n else 1
    total = (section1(paires) + section2(paires)
             + section3(paires) + section4(paires))
    print(f"\nTOTAL : {total} anomalie(s)."
          + ("" if total or NON_MESUREES else
             "  La table des contacts est servie et tient."))
    if NON_MESUREES:
        print(f"{len(NON_MESUREES)} paire(s) NON MESUREE(S), ce ne sont pas "
              "des zeros.")
    if total:
        return 1
    return 2 if NON_MESUREES else 0


if __name__ == "__main__":
    raise SystemExit(main("--temoin" in sys.argv))
