"""L'outillage de l'etape des approches : mesurer le blanc entre deux lettres.

Le projet mesure jusqu'ici des glyphes isoles. Une approche ne se voit pas sur un
glyphe isole, et les trois mesures de ce module existent parce que les mesures
deja ecrites ne pouvaient pas repondre.

Ce que chaque fonction corrige, ecrit ici pour ne pas etre redecouvert :

`inter_lettre` — `termes.hors_chasse` dit si un trait sort de sa chasse, pas
combien de blanc reste entre deux lettres. La chasse comprend deux approches et
la voisine avance dans la sienne : un glyphe qui reste dans sa chasse peut
laisser un trou ou toucher. Il faut composer les deux lettres.

`rythme` — `mesure_O.confusion` et `mesure4.confusion` remettent chaque dessin a
la meme largeur avant de comparer (`k = px*0.78 / max(largeur, hauteur)`), ce qui
est indispensable pour juger une forme et fatal pour juger un espacement : deux
groupes de largeurs differentes sortent ramenes a la meme. La mesure qui reste
valable sous cette normalisation est l'ASYMETRIE des blancs, et c'est justement
le levier de l'espacement — dans le m les deux contreformes sont egales par
construction, dans "rn" le crenage creuse la premiere. `rythme` la mesure en
geometrie, sans pixel, donc sans dependre d'une resolution.

`distance_rn_m_kern` — `termes.distance_rn_m` compose r et n a `lr.width` et
ignore donc le crenage, alors que la police en applique deja +10 unites dans les
huit masters. Les chiffres du vingt-et-unieme tour (0,087 a 0,159) sont mesures
a crenage nul. Cette version prend le crenage en argument, ce qui permet de le
balayer — sinon la seule mesure existante sur cette paire est aveugle au seul
levier qui lui reste.

Convention des grandeurs : tout est en unites de 1000, hauteur d'x 496,
capitale 668. Un "blanc moyen" est une aire de blanc divisee par la hauteur de
la bande, donc une largeur : les hauteurs ou le blanc est ferme comptent zero et
ne sont pas exclues. Les exclure comparerait deux moyennes prises sur des
supports differents, ce qui est le piege de la reference du dix-huitieme tour.
"""

import os

import glyphsLib

import dessin as D
from paires_F import PAIRES_F
from paires_bouts import PAIRES_BOUTS
from paires_contacts import PAIRES_CONTACTS
from paires_pieds import PAIRES_PIEDS

XH = 496.0          # hauteur d'x, la bande sur laquelle un blanc de bas de casse se juge
N = 400             # pas d'echantillonnage en hauteur : 1,24 unite
PAS = XH / (N - 1)  # 1,243 unite, tenu constant quelle que soit la bande

#: La bande pleine : de sous la descendante a au-dessus de l'ascendante.
#:
#: **Deux bandes pour deux questions, et les confondre a coute un defaut servi.**
#: `XH` est la bande sur laquelle un blanc de bas de casse se juge : c'est ce
#: que l'oeil lit dans une ligne de texte, et c'est la bonne borne pour comparer
#: des espacements. Elle est fausse pour un garde-fou, qui demande "ces deux
#: lettres peuvent-elles se toucher" : la barre haute du F monte a 668, le point
#: du i a 714, et tout ce qui se passe au-dessus de 496 etait invisible.
#:
#: Mesure du vingt-quatrieme tour, au Regular : l'approche du F laisse 8 unites
#: entre la barre du F et le point du i, la ou Atkinson en laisse 106. Le
#: garde-fou du vingt-troisieme tour declarait la paire conforme, et il ne
#: mentait pas : il s'arretait 218 unites trop bas. Sept familles de paires sont
#: dans ce cas, toutes celles dont le second membre monte au-dessus de la
#: hauteur d'x.
ASC = 800.0
DESC = -320.0

#: Le seuil d'entree dans une table de paires, en unites.
#:
#: En dessous, l'ecart est du bruit d'echantillonnage, et une table qui le
#: porterait ecrirait des centaines de paires qui bougent de moins d'une unite.
#: **Il est partage plutot que recopie** : le controle et la table doivent
#: s'accorder, sinon le controle signale eternellement ce que la table ecarte
#: volontairement — six paires par master au vingt-quatrieme tour, toutes vraies
#: et toutes sans objet.
SEUIL_PAIRE = 20.0

#: Le plancher de jour entre deux lettres, en unites. Ce qui doit rester ouvert.
#:
#: A distinguer de `SEUIL_PAIRE`, qui dit quand une paire vaut d'etre ecrite.
#: Celui-ci dit ce que le couloir ne doit pas descendre en dessous, et il sert
#: aux gestes qui FERMENT un couloir au lieu de l'ouvrir : le garde-fou du F
#: peut exiger « jamais plus serre qu'Atkinson », parce que la coupe du F
#: elargissait ; le lot 1 du vingt-cinquieme tour resserre par construction, et
#: la meme exigence y reviendrait a annuler le geste — 116 a 122 unites
#: d'ecartement, mesure.
#:
#: **La valeur n'est pas posee pour l'occasion.** 24 unites valent deux fois le
#: debord optique des rondes, qui vaut 12 dans cette police : O, C, G, S, le
#: zero, le o et le c descendent tous a -12. C'est le seuil que le projet emploie
#: depuis le dix-septieme tour sur les crochets souscrits, ou il a servi a
#: ecarter deux etats de l'ogonek, et le seul chiffre du projet qui reponde a la
#: question « ce blanc se voit-il encore ». Partage entre la table et son
#: controle, pour la raison ecrite sur `SEUIL_PAIRE`.
JOUR_MIN = 24.0

#: LES GLYPHES DONT LE PROJET A CHANGE LA HAUTEUR, et pour lesquels la
#: comparaison a Atkinson sur la bande pleine cesse de poser la bonne question.
#:
#: Tranche par Nicolas au trente-deuxieme tour, sur mesure. L'allongement de la
#: barre montante du t ajoute de la matiere entre 620 et 690, donc face aux
#: capitales a barre ou a bras haut : 42 paire-masters passent sous le couloir
#: d'Atkinson, dont `F+t` dans les huit masters. Aucune ne cree de contact et
#: aucune ne passe sous `JOUR_MIN` — mesure au couloir EXACT sur 141 paires par
#: master, `mesure_t_voisins.py`.
#:
#: POURQUOI CE N'EST PAS UNE EXEMPTION. Atkinson n'a pas de t a 690. Comparer le
#: couloir de Temoin a celui de sa base sur une paire dont un membre a change de
#: hauteur revient a comparer deux lettres differentes, et le garde-fou
#: repondrait eternellement a une question que le dessin a rendue caduque. Ce
#: qui doit tenir est le PLANCHER DE JOUR, et les controles le verifient et
#: impriment le jour reel — c'est la forme deja retenue pour `F+i` au
#: trente-et-unieme tour, ou l'ecart etait voulu par un crenage plutot que par
#: un dessin.
#:
#: A NE PAS ETENDRE SANS MESURE. Une entree de plus ici retire un critere a un
#: garde-fou : elle ne se justifie que par un geste du projet qui deplace un
#: alignement de la lettre, et elle demande la mesure du voisinage complet.
HAUTEUR_MODIFIEE = ("t",)

#: Le reglage du F, trente-et-unieme tour, sur retour de Nicolas en navigateur.
#:
#: **La mesure lui a donne raison, et elle ne pouvait pas le trouver seule.** Au
#: Regular, `F+i` a 108 unites de couloir quand `F+o` n'en a que 84,5 : la table
#: referme chaque paire de tout ce que sa geometrie permet, mais le blanc PERCU
#: devant une ronde est plus grand que son couloir, puisqu'elle s'eloigne de part
#: et d'autre. Une ronde refermee au maximum de sa geometrie parait donc trop
#: serree, et aucun garde-fou du projet ne pouvait le dire. C'est le navigateur
#: qui l'a montre, comme au vingt-quatrieme tour.
#:
#: Les rondes se desserrent de 15 unites, valeur choisie par Nicolas sur une
#: page a quatre etats, 8, 15 et 25. Desserrer ne peut pas creer de contact,
#: donc aucune borne ne s'y applique.
REGLAGE_F_RONDES = 15.0

#: Les six rondes du point ouvert 44, plus les accentuees qui portent la meme
#: geometrie. **Les accentuees sont dedans et ce n'est pas un detail** : sans
#: elles, « Fevrier » ne suivrait pas « Fondation », et les deux sont dans le
#: corpus des gabarits. Le a et le agrave n'y sont pas — leur flanc gauche est
#: un fut — ni l'ae ni l'AE, dont le flanc gauche est celui du a.
#:
#: LES RONDES CAPITALES Y ENTRENT AU CINQUANTE-QUATRIEME TOUR, et la note
#: d'origine les ecartait par leur casse et non par leur forme : « ni OE et AE,
#: qui sont des capitales ». La raison optique du reglage ne connait pas la
#: casse. Nicolas l'a vu en navigateur sur l'OE — « devant le OE, le F est un
#: peu trop pres » — et la mesure l'a chiffre a l'ExtraBold : les rondes
#: capitales sortaient a 62,2 a 62,7 unites de blanc quand les rondes bas de
#: casse, desserrees par ce meme reglage au trente-et-unieme tour, valent 81,0
#: a 81,7. Dix-neuf unites, sur la seule famille que le reglage avait oubliee.
#:
#: Les quatre bas de casse ajoutes au meme geste — ecircumflex, edieresis,
#: odieresis, oe — entrent parce qu'ils entrent aussi dans `VOISINS_F` au meme
#: tour : une ronde crenee par la table sans recevoir le reglage serait la
#: seule de sa famille a rester au maximum de sa geometrie.
RONDES_F = ("o", "e", "c", "d", "g", "q",
            "eacute", "egrave", "ccedilla", "ocircumflex",
            "ecircumflex", "edieresis", "odieresis", "oe",
            "O", "C", "G", "Q", "OE", "Ccedilla", "Ocircumflex", "Odieresis")

#: Le i se resserre de 40 unites, **borne par le plancher de jour master par
#: master**, arbitrage de Nicolas.
#:
#: Le delta demande vaut 40 partout. Il tient dans les clairs, ou `F+i` n'est
#: pas dans la table du F et part donc de zero : le couloir y passe de 108 a 68.
#: Dans les gras la table le crene deja a −58 et −62, et 40 de plus le mettrait
#: a 18,5 unites de jour, sous le plancher du projet. Le delta y est donc borne
#: a ce que le plancher permet, 35 et 34.
#:
#: **Les bornes sont cherchees par dichotomie sur `couloir_exact` et non par
#: soustraction**, parce que le couloir n'est pas lineaire en crenage : c'est la
#: lecon du point 55, ou deux mesures divergent de 30 unites a faible
#: ecartement et coincident au-dela.
REGLAGE_F_I = {"ExtraLight": -40.0, "Regular": -40.0,
               "Bold": -35.0, "ExtraBold": -34.0,
               "ExtraLight Italic": -40.0, "Italic": -40.0,
               "Bold Italic": -35.0, "ExtraBold Italic": -34.0}

#: **Le F devant le A, cinquante-quatrieme tour.** Nicolas, en navigateur sur
#: `tour54.html` : « devant le A et le OE, en gras et extragras, le F est un peu
#: trop pres ». L'OE avait une cause mesuree, les rondes capitales privees du
#: reglage de +15 ; le A n'en avait aucune.
#:
#: **LA MESURE NE POUVAIT PAS TRANCHER, ET LE POINT 93 L'AVAIT ECRIT.** Le blanc
#: vaut 80,8 unites a l'ExtraBold, soit celui d'Atkinson et celui des rondes que
#: Nicolas avait validees au trente-et-unieme tour. Le blanc devant une
#: DIAGONALE n'est mesure par aucun garde-fou du projet, et les deux grandeurs
#: disponibles classent une telle paire aux deux bouts opposes -- `C+AE` est a
#: la fois la plus large par le blanc moyen et la plus serree par la gouttiere.
#: La valeur a donc ete tranchee sur une page a quatre etats,
#: `tour54-etats-FA.html`, servi / +10 / +20 / +30, comme les rondes l'avaient
#: ete. Nicolas a retenu **+30**, l'ecart le plus large des quatre : il lit le A
#: plus serre que les rondes la ou la mesure les donne egaux.
#:
#: **LES TROIS ACCENTUEES SUIVENT, ET C'EST UNE DECISION.** A grave, A
#: circonflexe et A trema portent la meme diagonale et le meme blanc que le A
#: depuis que les vingt-neuf accentuees sont entrees dans `VOISINS_F`, au meme
#: tour. Les omettre les laisserait 30 unites plus serrees que le A dans un
#: titre, et c'est exactement ce que le reglage des rondes venait de couter en
#: oubliant sa moitie capitale.
#:
#: **L'AE N'Y EST PAS**, et Nicolas l'a tranche : son blanc vaut deja 88,2, soit
#: 7,4 unites de plus que les quatre autres, et il n'a pas ete signale. Le
#: desserrer le porterait a 118,2, le plus large du voisinage du F devant une
#: lettre.
#:
#: Desserrer ne peut pas creer de contact, donc aucune borne ne s'y applique.
REGLAGE_F_A = 30.0

#: Les quatre glyphes qui recoivent `REGLAGE_F_A`. Ecrits en liste et non
#: deduits d'un nom : une famille se nomme, elle ne se devine pas.
DIAGONALES_F = ("A", "Agrave", "Acircumflex", "Adieresis")

#: **Le F devant l'ESPACE, quarante-troisieme tour, point ouvert 76.** Arbitre
#: par Nicolas au quarante-deuxieme en navigateur, LE F SEUL.
#:
#: **LA VALEUR EST -60 ET NON -40.** Nicolas a d'abord tranche -40, par analogie
#: avec le reglage F+i du trente-et-unieme tour ; il a rejuge a -60 sur la
#: section 7 d'`espacement.html`, ou le -40 etait SERVI et non simule. Les deux
#: chiffres ont donc ete regardes au meme endroit, l'un apres l'autre, et
#: l'analogie avec F+i ne tient plus -- ce qui est cohérent, le blanc a
#: refermer valant 15,6 unites de plus que la moyenne du repertoire quand le i
#: ne demandait qu'un resserrement de paire ordinaire. **Une page d'etats
#: devient fausse a l'instant ou elle a servi** : c'est pourquoi la section 7
#: montre l'etat servi et porte ses chiffres dans son texte.
#:
#: **Aucun controle du projet ne pouvait voir ce defaut, et la raison est
#: structurelle.** `approches.profil` rend `None` a toutes les hauteurs sur un
#: glyphe sans contour, donc `couloir_plein` y leve une division par zero et
#: aucune des deux tables de paires ne peut porter une paire dont un membre n'a
#: pas d'encre. TOUT GLYPHE SANS CONTOUR EST UN ANGLE MORT PAR CONSTRUCTION,
#: et les quatre espaces ne sont pas les seuls.
#:
#: **La mesure qui designe le F et lui seul.** Blanc moyen a droite du glyphe,
#: sur l'ENCRE REELLE et non sur ses noeuds, de la ligne de base a 668, au
#: Regular : le F passe de 298,2 a 313,8 unites, +15,6, le plus gros gain du
#: repertoire ; la famille du E vient ensuite a +7,0, et neuf glyphes seulement
#: depassent 4 unites, dont huit sont cette famille. La cause est la barre
#: mediane, qui recule de 105,2 / 99,4 / 99,7 / 99,7 unites selon le master --
#: la passation annoncait 108. La chasse du F et son approche droite sont
#: celles d'Atkinson depuis le vingt-quatrieme tour : le trou est dans le
#: dessin, pas dans l'espacement.
#:
#: **Ce qui a leve l'ambiguite de la demande sans avoir a la poser** : toutes
#: les paires F+lettre de Temoin sont DEJA plus serrees qu'Atkinson, de 4 a 116
#: unites, parce que `PAIRES_F` les referme -- F+o a -90,4 au Regular, F+A a
#: -109,4, F+i a -19,8. La seule restee ouverte est F+espace, a 0.
#:
#: **Une paire devant l'espace n'est pas une invention, et elle ne risque aucun
#: contact.** Atkinson crene lui-meme P+espace a -30, T+espace, V+espace et
#: r+espace a -20 ; il laisse F+espace a 0 parce que sa barre y etait a fleur.
#: Un crenage devant un glyphe sans encre ne peut rien toucher, donc aucune
#: borne ne s'y applique -- meme raison que `REGLAGE_F_RONDES`, qui desserre.
#:
#: **La valeur est PLATE sur les huit masters, contrairement a `REGLAGE_F_I`.**
#: Les 40 du i y sont bornes a 35 et 34 dans les gras par le plancher de jour ;
#: ici il n'y a pas de jour a garder, donc rien ne borne et les huit masters
#: prennent la valeur arbitree. C'est aussi ce qui permet a -60 de passer sans
#: qu'aucune mesure ne s'y oppose : **un crenage devant un glyphe sans contour
#: ne peut pas creer de contact**, quelle que soit sa valeur, et la seule
#: limite est ce que l'oeil accepte.
#:
#: **La famille du E n'est PAS traitee**, bien qu'elle soit le second gain :
#: Nicolas a nomme le F seul. A rouvrir si l'ecart se voit en lecture, et le
#: prix serait huit glyphes au lieu d'un.
REGLAGE_F_ESPACE = -60.0

#: Le nom du glyphe d'espace dans cette source. Il est ECRIT plutot que devine :
#: `uni0020` et `uni00A0` n'ont jamais rien designe ici, cette source nommant
#: ses espaces `space`, `nbspace`, `thinspace` et `narrownbspace`, et le
#: trente-troisieme tour a deja paye deux noms morts dans une liste.
#: L'insecable et les deux fines NE SONT PAS DEDANS : Nicolas a juge le F
#: devant l'espace mot, et une espace fine derriere un F ne se compose pas en
#: francais.
GLYPHE_ESPACE = "space"

#: LE BLANC DEVANT L'Æ EN CAPITALES, cinquante-cinquieme tour, troisieme terme
#: du point 93.
#:
#: **Ce n'est pas un defaut des petites capitales, et c'est mesure.** Le point
#: 93 rangeait `C+Æ` parmi les trois termes de l'espacement des petites
#: capitales. Mesure a l'excedent normalise -- le blanc de la paire `.sc` ramene
#: a l'echelle de la capitale, moins le blanc de la capitale -- `C+Æ` sort SOUS
#: la mediane : +17,9 contre 24,7 a l'ExtraBold. La petite capitale herite la
#: paire sans l'aggraver. Le blanc est grand dans les CAPITALES, 433,6 unites au
#: Bold contre 337,7 pour `C+O`, et Atkinson ne crene ni l'une ni l'autre.
#:
#: **La famille se mesure sur les 58 capitales servies**, et non sur les 44
#: bases de petites capitales : c'est la que le cinquante-quatrieme tour avait
#: trouve ses vingt-neuf accentuees oubliees. Elle compte DIX noms, les memes
#: dans les huit masters et dans les deux sources.
#:
#: **`Ecaron`, `Edotaccent`, `Emacron` et `Eogonek` ne sont pas servis** : ils
#: vivent dans la source et ne recoivent rien. Si le sous-ensemble s'elargit,
#: ils devront suivre le E.
#:
#: **La cible est fixee par le -50 que Nicolas a retenu sur `C+Æ`**, et chaque
#: membre recoit ce qu'il lui faut pour l'atteindre. La valeur retenue ne
#: figurait sur aucun des quatre etats de `tour55-etats-sc.html`, qui posait 0,
#: -30, -60 et -90 : elle sera jugee sur la page servie, comme F+espace au
#: quarante-troisieme tour, ou le -40 arbitre est devenu -60 une fois servi.
#:
#: **BORNEE PAR LE PLANCHER DE JOUR, et la cible n'est donc pas atteinte
#: partout.** Le geste FERME, donc il peut fermer trop. `L+Æ` est a la fois la
#: paire la plus large par le blanc moyen et l'une des plus serrees par la
#: gouttiere -- 28 unites en ExtraLight romain -- ce qui est la divergence exacte
#: que le point 93 decrivait sur `C+Æ`, et elle interdit de le refermer : il
#: voudrait -85 et ne peut prendre que -4. Il reste donc la paire la plus large
#: du voisinage de l'Æ dans tous les masters, ET C'EST UNE LIMITE CONNUE. La
#: famille du E est bornee dans les masters clairs, et **le C lui-meme ne tient
#: son -50 que dans sept masters sur huit** : l'ExtraBold italique ne permet
#: que -44.
#:
#: **Des DEPLACEMENTS et non une cible recalculee a la compilation.** Une cible
#: absolue corrigerait en silence un ecart que personne n'a mesure : le garde-fou
#: de `barre_mediane` a leve exactement la-dessus au cinquante-quatrieme tour, ou
#: l'Œ portait sa barre 0,5 unite plus bas que l'E en ExtraLight depuis
#: toujours. Les valeurs ci-dessous sont mesurees une fois ; `check_crenage_sc`
#: remesure qu'elles atteignent la cible ou la borne, et sait signaler.
#:
#: **LA TABLE EST GENEREE DEPUIS LE CINQUANTE-SIXIEME TOUR**, seconde reprise du
#: point 97. Elle etait ecrite a la main et relevee sur les 58 capitales du
#: BINAIRE servi ; la source en porte davantage, et huit noms depassaient la
#: cible sans y figurer. Le producteur est `inventaire_ae.py --ecrire`, qui
#: mesure sur la SOURCE et porte deux temoins. Ne pas editer `reglage_ae.py` a
#: la main, comme les trois tables de paires.
CIBLE_AE_DEPUIS_C = -50.0

#: Le seuil au-dela duquel une capitale entre dans la famille, en unites de
#: blanc moyen. PARTAGE par le producteur et par `check_crenage_sc` : un seuil
#: recopie devient un desaccord, et le projet l'a paye au vingt-troisieme tour
#: sur le garde-fou du F.
SEUIL_AE = 1.5

#: `HORS_PORTEE_AE` porte la troisieme categorie : les capitales qui depassent
#: la cible et dont la gouttiere est DEJA sous le plancher, donc qu'aucune unite
#: ne peut refermer. `Lslash` y est dans les huit masters, a 5,4 a 21,4 unites
#: pour un plancher de 24 et un crenage amont nul : c'est la police de base, et
#: la forme exacte du point ouvert 96. Elle est ecrite parce qu'un nom decide et
#: un nom jamais regarde sont identiques dans une table -- tous deux absents.
from reglage_ae import REGLAGE_AE, HORS_PORTEE_AE   # noqa: E402  (genere)

#: LE X DEVANT LE A, referme au plancher de jour. Ouvert par Nicolas au
#: cinquante-sixieme tour en navigateur, tranche sur `tour56-etats-XA.html` :
#: la fermeture pleine, chaque master bornant la sienne.
#:
#: **Le +19 d'Atkinson est un garde-fou et non un gout** : sans lui la gouttiere
#: de `X+A` tombe a 24,8 unites en ExtraLight, 20,8 au Regular, 15,8 au Bold et
#: 14,8 a l'ExtraBold, pour un plancher de 24. Ce qui reste a fermer s'INVERSE
#: donc sur l'axe -- 15,8 unites dans les clairs, 8,8 a l'ExtraBold -- et une
#: valeur unique aurait ete fausse d'un bout de l'axe ou de l'autre.
#:
#: **Ecrit sur la CLE DE GROUPE**, et le groupe a ete lu avant d'ecrire :
#: `@MMK_R_A` porte le A, ses neuf accentuees et le Delta, onze glyphes dont la
#: gouttiere avec le X est rigoureusement la meme. Une ecriture glyphe-glyphe
#: aurait laisse `X+À` plus lache que `X+A`, ce qui est le defaut que
#: `VOISINS_F` a coute au cinquante-quatrieme tour.
#:
#: **`A+X` ne recoit rien** : `paires_pieds` l'a deja posee au plancher au
#: vingt-neuvieme tour, sa gouttiere valant 24,2 a 25,2 unites.
CIBLE_XA = ("X", "A")

from reglage_xa import REGLAGE_XA                    # noqa: E402  (genere)

#: Le second membre de la famille ci-dessus. Ecrit plutot que devine, comme
#: `GLYPHE_ESPACE`.
GLYPHE_AE = "AE"

#: Les trois glyphes dont le lot 1 du vingt-cinquieme tour fait descendre le
#: cote gauche du pied gauche, a 22, 32 et 32 unites. Ils sont SECOND membre de
#: la paire : c'est leur cote gauche qui descend, donc c'est l'approche de la
#: lettre precedente qu'ils mangent. Partage par la table, son generateur et son
#: controle — deux codes qui parlent du meme voisinage doivent lire la meme
#: liste, et le vingt-quatrieme tour a laisse F+OE et F+AE ouverts pour l'avoir
#: oublie.
#: **Etendu au lot 3 au vingt-septieme tour**, et le nom devient impropre : ces
#: six glyphes ne sont plus seulement des pieds. Le mecanisme, lui, est le meme
#: et il n'est pas recopie — un second generateur et un second controle auraient
#: fini par diverger du premier, ce que ce projet a paye assez de fois.
#:
#: Les trois cibles du lot 3, et pourquoi elles sont dans la meme liste :
#:
#:   p  le cote gauche du bout de sa jambe descend de 24 unites. Il est SECOND
#:      membre comme les trois pieds. Mesure : il ne resserre rien, dans aucun
#:      master, et son inclusion ici le PROUVE au lieu de le supposer.
#:   y  le bout de sa queue avance de 40 unites vers la gauche, donc lui aussi
#:      mange l'approche de la lettre precedente. C'est la seule des trois qui
#:      demande des valeurs : `q+y` passe sous le plancher dans les huit
#:      masters et en contact dans les deux ExtraLight.
#:   Y  le cote DROIT de son pied descend de 44 unites, donc il mange l'approche
#:      de la lettre SUIVANTE et non de la precedente. Il est premier membre, et
#:      le generateur teste les deux sens : le zero d'un cote ne dit rien de
#:      l'autre. Mesure : il ne resserre rien non plus.
#:
#: **Etendu au lot 4a au vingt-huitieme tour**, et le nom devient franchement
#: faux : le N et le H y entrent pour leur pied de fut gauche, qui plonge de 24
#: unites, mais ils portent AUSSI un sommet de fut qui monte de 24 — et c'est
#: leur pied seul qui est en cause ici. Le h et le k, dont le geste monte, n'y
#: sont pas : ils ne resserrent rien, mesure sur les 71 voisins et les huit
#: masters, et les faire entrer donnerait une table vide et l'illusion d'une
#: couverture.
#:
#:   N, H  le cote gauche de leur pied descend de 24 unites. Meme geometrie que
#:         les trois pieds du lot 1, et meme prix : `q+N` et `q+H` passent de
#:         100,0 a −18,9 unites de couloir en ExtraBold ROMAIN, et dans ce master
#:         seul. Le franchissement se fait entre 12 et 22 unites et la valeur
#:         sature ensuite, donc 24 coute ce que couteraient 44. L'ExtraBold
#:         ITALIQUE tient a 74,1 : l'inclinaison ecarte les deux lettres au lieu
#:         de les rapprocher, ce qui est l'inverse des sept inversions d'axe
#:         mesurees dans ce projet.
#: **Etendu au lot 4b au vingt-neuvieme tour**, et le nom ne veut plus rien dire
#: du tout : le A y entre pour son pied DROIT et le X pour son pied GAUCHE, les
#: deux seules sortantes du projet portees par une DIAGONALE.
#:
#: **Ils y entrent alors qu'ils ne demandent AUCUNE valeur, et c'est un ecart
#: assume avec ce qui est ecrit juste au-dessus pour le h et le k.** L'argument
#: du vingt-huitieme tour etait qu'une cible qui ne resserre rien donne une
#: table vide et l'illusion d'une couverture. Il ne s'applique pas ici, et la
#: difference est mesuree : le h et le k ne resserrent RIEN, zero paire sur les
#: 71 voisins et les huit masters ; le A en resserre huit et le X six a sept, et
#: ce qu'ils ne font pas, c'est passer sous le plancher A 24 UNITES. Le
#: franchissement vaut 28,5 unites sur le A en ExtraBold romain et **26,0 sur le
#: X en ExtraBold Italic**, donc la marge est de 2,0 unites. Une cible a deux
#: unites de son franchissement n'est pas une cible propre, c'est une cible qui
#: tient — et la section 5 est le seul endroit du projet qui le REMESURERA le
#: jour ou autre chose bougera. La table reste a 28 paires, verifie par
#: `inventaire_pieds.py --ecrire` : le fichier ne change pas d'une ligne.
#:
#:   A  le cote droit de son pied droit plonge de 24 unites, donc il mange
#:      l'approche de la lettre SUIVANTE. Premier membre, comme le Y. La paire
#:      critique est `A+j`, et c'est la moitie du point ouvert 52 que le
#:      generateur ne testait pas avant le vingt-septieme tour.
#:   X  le cote gauche de son pied gauche plonge de 24, donc il mange l'approche
#:      de la lettre PRECEDENTE. Second membre. La paire critique est `q+X`,
#:      quatrieme recidive de la queue du q apres le lot 1, le lot 3 et le 4a.
#: QUARANTE-QUATRIEME TOUR : LES QUATRE CHIFFRES QUI PLONGENT Y ENTRENT, et le
#: trou qu'ils ferment est plus ancien que le point 74a.
#:
#: AUCUN CHIFFRE N'ETAIT CIBLE NI VOISIN, dans cette table comme dans celle des
#: bouts. Le 9 plonge de 32 unites DEPUIS LA FUSION DU QUARANTIEME TOUR, et
#: aucun garde-fou ne l'avait jamais regarde : le projet a pourtant ecrit au
#: lot 1 que tout geste faisant sortir de la matiere hors de la boite doit
#: passer par ici avant d'etre cru. Le zero-diff de `inventaire_pieds` a 61
#: paires etait donc une CECITE et non un fait -- un generateur ne peut pas
#: voir ce qui n'est pas dans ses listes, et le compte ne bouge pas pour
#: autant. C'est la troisieme forme du zero-diff trompeur dans ce projet,
#: apres le generateur qui ne relit pas la source et celui qui ignore une
#: etape neuve de la chaine.
#:
#: CE QUE LEUR ENTREE A TROUVE, mesure sur 84 voisins et les huit masters :
#: `q+seven` passe SOUS le plancher dans trois masters -- -1,6 u au Bold,
#: -6,3 a l'ExtraBold, -5,9 en ExtraBold Italic, donc un contact servi -- et
#: `f+seven` frole a 23,9 pour 24 a l'ExtraBold. C'est la cinquieme recidive
#: de la queue du q, apres le lot 1, le lot 3, le lot 4a et le lot 4b. **Le 9
#: ne coute rien dans aucun master**, ce qui se savait d'autant moins que
#: personne ne l'avait mesure.
#:
#: Le 1 et le 4 n'y resserrent rien non plus, et ils y sont quand meme, pour
#: la raison ecrite plus haut a propos du A et du X : une cible qui ne demande
#: aucune valeur aujourd'hui est ce qui REMESURERA le jour ou autre chose
#: bougera. Le 2, le 3, le 5 et le 1 tabulaire n'y sont pas : ils ne portent
#: aucun geste, point 74a.
CIBLES_PIEDS = ("m", "M", "f", "p", "y", "Y", "N", "H", "A", "X",
                "one", "four", "seven", "nine")


def n_pour(y0, y1):
    """Le nombre de points qui tient le pas d'echantillonnage constant.

    Elargir la bande sans augmenter N diviserait la resolution verticale : la
    bande pleine fait 1120 unites contre 496, donc le pas passerait de 1,24 a
    2,80 et un couloir etroit pourrait etre saute entre deux echantillons.
    """
    return max(2, int(round((y1 - y0) / PAS)) + 1)


# ---------------------------------------------------------------- geometrie

def croisements(contours, y):
    """Abscisses ou la droite d'ordonnee y traverse les contours, triees.

    La regle `lo <= y < hi` (et non `<=` des deux cotes) evite de compter deux
    fois un sommet partage par deux segments : un croisement double rendrait un
    nombre pair errone et decalerait tous les intervalles.
    """
    xs = []
    for poly in contours:
        n = len(poly)
        for k in range(n):
            x1, y1 = poly[k]
            x2, y2 = poly[(k + 1) % n]
            if y1 == y2:
                continue
            lo, hi = (y1, y2) if y1 < y2 else (y2, y1)
            if lo <= y < hi:
                xs.append(x1 + (x2 - x1) * (y - y1) / (y2 - y1))
    return sorted(xs)


def bandes(y0=0.0, y1=XH, n=None):
    n = n or n_pour(y0, y1)
    return [y0 + (y1 - y0) * i / (n - 1) for i in range(n)]


_CACHE_PROFIL = {}


def profil(src, nom, y0=0.0, y1=XH):
    """Bord gauche et bord droit du glyphe, hauteur par hauteur.

    Memoise : un inventaire de 544 paires sur quatre masters reprofile la meme
    lettre des centaines de fois, et le profil est la seule operation couteuse
    de ce module. La cle porte l'identite de la police, le master et les bornes
    — sans le master, les quatre graisses partageraient le meme profil, ce qui
    serait un contresens silencieux.
    """
    cle = (id(src.font), src.master, nom, y0, y1)
    if cle in _CACHE_PROFIL:
        return _CACHE_PROFIL[cle]
    cs = src.contours(nom)
    ga, dr = [], []
    for y in bandes(y0, y1):
        xs = croisements(cs, y)
        ga.append(xs[0] if xs else None)
        dr.append(xs[-1] if xs else None)
    _CACHE_PROFIL[cle] = (ga, dr)
    return ga, dr


def contreformes(src, nom, y0=0.0, y1=XH):
    """Largeur de chaque blanc interne du glyphe, hauteur par hauteur.

    Rend une liste de listes : pour chaque hauteur, les blancs de gauche a
    droite. Une hauteur ou le glyphe est plein rend une liste vide, et c'est le
    `blanc_moyen` qui la compte comme zero.
    """
    cs = src.contours(nom)
    out = []
    for y in bandes(y0, y1):
        xs = croisements(cs, y)
        out.append([xs[j + 1] - xs[j] for j in range(1, len(xs) - 1, 2)])
    return out


def blanc_moyen(valeurs, indice=0):
    """Largeur moyenne d'un blanc sur toute la bande, fermetures comptees zero."""
    tot = 0.0
    for v in valeurs:
        tot += v[indice] if len(v) > indice else 0.0
    return tot / len(valeurs)


# ------------------------------------------------------------- crenage lu

def cles_kern(font, a, b):
    """Les quatre cles possibles d'une paire, de la plus specifique a la moins.

    Glyphs accepte quatre formes, pas deux : glyphe-glyphe, glyphe-groupe,
    groupe-glyphe et groupe-groupe. Une exception y est simplement une cle plus
    specifique, et elle l'emporte.
    """
    ga = font.glyphs[a].rightKerningGroup
    gb = font.glyphs[b].leftKerningGroup
    ka = "@MMK_L_" + ga if ga else a
    kb = "@MMK_R_" + gb if gb else b
    return [(a, b), (a, kb), (ka, b), (ka, kb)]


def kern(font, master_id, a, b):
    """La valeur de crenage que la police applique entre a et b, groupes compris.

    Les quatre cles sont lues de la plus specifique a la moins, dans l'ordre de
    resolution de Glyphs et de ce que fontmake compile.

    **Un premier jet n'en lisait que deux**, la paire de groupes puis la paire
    directe, et son docstring justifiait cet ordre par une affirmation qui etait
    fausse : « aucune des paires du projet n'a d'exception directe ». Atkinson en
    a, et sous la troisieme forme, celle a laquelle personne n'avait pense :
    `@MMK_L_F` porte `icircumflex 30`, `idieresis 30`, `igrave 20` et
    `imacron 30` — groupe a gauche, glyphe a droite. La fonction rendait donc 0
    sur F+i accentue, la ou la police applique 20 a 30 unites.

    Trouve par `shape_check_kern.py`, qui compare ce que le binaire compose a ce
    que cette fonction lit : deux paires par master sortaient a 30 unites, et
    c'est la source qui etait mal lue, pas le binaire qui derapait. Aucun
    correctif du F n'est concerne — les quatre glyphes a exception ne sont dans
    aucune table du projet — et l'erreur allait dans le sens severe : le
    garde-fou du vingt-troisieme tour croyait F+i accentue plus serre de 30
    unites qu'il ne l'est, donc son zero tient a fortiori. Mais elle aurait
    silencieusement mange un correctif le jour ou une table aurait touche une
    paire a exception.
    """
    K = font.kerning.get(master_id, {})
    for ka, kb in cles_kern(font, a, b):
        v = K.get(ka, {}).get(kb)
        if v is not None:
            return float(v)
    return 0.0


def groupes(font, a, b):
    """Les deux cles de crenage d'une paire, et qui les partage.

    Sert a savoir ce qu'une paire de groupes touche en plus de la paire visee :
    le groupe gauche du r vaut "n", partage avec le m, le n et leurs accentuees.
    """
    ga = font.glyphs[a].rightKerningGroup
    gb = font.glyphs[b].leftKerningGroup
    part_a = [g.name for g in font.glyphs if ga and g.rightKerningGroup == ga]
    part_b = [g.name for g in font.glyphs if gb and g.leftKerningGroup == gb]
    return (("@MMK_L_" + ga if ga else a), (part_a or [a]),
            ("@MMK_R_" + gb if gb else b), (part_b or [b]))


# ------------------------------------------------------- mesures d'approche

def inter_lettre(src, a, b, k=0.0, y0=0.0, y1=XH):
    """Le blanc entre deux lettres composees avec leurs chasses et leur crenage.

    Rend (couloir le plus etroit, blanc moyen). Le couloir le plus etroit est ce
    qu'un contact viendrait fermer ; le blanc moyen est ce que l'oeil lit comme
    un espacement. Les deux sont necessaires : la barre du F recule de 99 unites
    au Regular, ce qui ouvre le couloir de 100 et ne change le blanc moyen que
    de 19, parce que le F n'a de matiere qu'a deux hauteurs.

    **La bande par defaut s'arrete a la hauteur d'x, et c'est un choix, pas une
    commodite.** Il est juste pour comparer des espacements de bas de casse et
    faux pour un garde-fou : voir `ASC`, `DESC` et `couloir_plein`. Un appel qui
    demande "ces deux lettres peuvent-elles se toucher" doit passer les bornes
    pleines.
    """
    _, da = profil(src, a, y0, y1)
    gb, _ = profil(src, b, y0, y1)
    w = src.width(a) + k
    v = [(w + gb[i]) - da[i] for i in range(len(da))
         if da[i] is not None and gb[i] is not None]
    if not v:
        return None, None
    return min(v), sum(v) / len(v)


def couloir_plein(src, a, b, k=0.0):
    """Le couloir le plus etroit entre deux lettres, sur toute leur hauteur.

    La grandeur du garde-fou : elle repond a "ces deux lettres peuvent-elles se
    toucher", quand `inter_lettre` par defaut repond a "quel blanc l'oeil lit-il
    dans une ligne". Les deux sont utiles et elles ne se remplacent pas : sur
    F+i au Regular elles rendent 138 et 8.

    Les hauteurs ou l'un des deux glyphes n'a pas de matiere sont ignorees par
    `inter_lettre`, donc elargir la bande ne peut pas fabriquer de faux couloir.

    CE N'EST PAS UN COULOIR, C'EST UN MINORANT. POINT OUVERT 55, FERME AU
    TRENTE-ET-UNIEME TOUR COMME LIMITE CONNUE, AVEC LE CRITERE QUI DIT QUAND
    ELLE MORD.

    La fonction calcule `(chasse + min des bords gauches de b) − max des bords
    droits de a`. C'est le couloir vrai tant que chaque lettre presente UN SEUL
    intervalle d'encre a la hauteur mesuree. Des qu'une des deux en presente
    deux disjoints, elle compare deux morceaux qui ne se font pas face. La
    mesure juste est `balayage_lot4b.couloir_exact`, qui minimise sur les
    COUPLES d'intervalles.

    **Le defaut est conservateur par construction** : le minorant est inferieur
    ou egal a tout ecart reel, donc il peut inventer un contact et jamais en
    rater un. Un zero de sa part reste un verdict fort.

    **Il se trompe, et de beaucoup.** Mesure du trente-et-unieme tour sur l'etat
    ou les vingt-deux gestes coexistent, ExtraBold romain : sur `q+m` il rend
    −21,91 pour un couloir vrai de +8,52 ; sur `q+N` et `q+H`, −18,91 pour
    −6,94 et −7,98. `q+M` est un contact vrai, a −18,91 par les deux mesures.
    La queue du q est le seul lobe disjoint en cause dans le repertoire servi.

    **LE CRITERE, et c'est lui qui vaut d'etre retenu.** Le couloir exact n'est
    pas monotone en `k`. Sur `q+m` a l'ExtraBold il vaut +8,52 a k = 0, descend
    a −6,48 a k = 15 quand l'eperon du pied du m quitte le lobe de la queue et
    vient face a la panse, puis les deux mesures coincident exactement des
    k = 20 et franchissent le plancher au meme endroit, k = 46. **Le minorant ne
    peut donc couter quelque chose que si la decision se prend a FAIBLE
    ECARTEMENT, dans la zone ou les deux mesures divergent.** Une decision prise
    au plancher de `JOUR_MIN` est au-dela de cette zone.

    **Ce que cela a coute, mesure et non suppose : rien.** 675 paire-masters des
    deux tables servies rejouees par les deux mesures — 107 pour
    `paires_pieds.py`, 568 pour le voisinage du F. Zero valeur ecrite change.
    Sur le F, le minorant ne differe pas d'un centieme sur les 568. Voir
    `mesure_point55.py`, qui rejoue les deux producteurs.

    **QUAND SE MEFIER A NOUVEAU.** Une table dont la borne se decide pres de
    l'etat non ecarte, et non a un plancher : c'est le cas d'une table bornee
    par Atkinson. Y verifier la zone de divergence avant de conclure, au lieu de
    transporter le resultat ci-dessus.
    """
    g, _ = inter_lettre(src, a, b, k, DESC, ASC)
    return g


def paire_bornee(sa, st, a, b, k_amont, seuil=None):
    """Le crenage qui referme ce que la coupe a ouvert, sans fermer le reste.

    Deux grandeurs, et il faut les deux. **Ce que la coupe a ouvert** se mesure
    sur la bande de jugement, de la ligne de base a la hauteur d'x : c'est la que
    la barre mediane du F a recule, donc c'est la que le blanc s'est cree.
    **Ce qu'on peut refermer** se mesure sur la bande pleine : c'est la marge
    entre le couloir le plus etroit de Temoin et celui d'Atkinson, sur toute la
    hauteur des deux lettres.

    Le crenage retenu est le plus petit des deux. La consequence est nette et
    elle explique tout le vingt-quatrieme tour : devant une lettre qui monte,
    l'ouverture vaut 100 unites en bas et la marge vaut zero en haut, parce que
    rien n'a bouge contre la barre haute du F. Un crenage de -100 y refermerait
    le bas et ecraserait le haut. C'est exactement ce que faisait l'approche du
    glyphe, et c'est pour ca que FI, FT, FV, FW, FX et FY se touchaient dans le
    binaire servi.

    Rend None quand la paire ne demande rien, c'est-a-dire quand l'ouverture
    reste sous le seuil ou quand la marge est nulle. Le seuil ecarte le bruit
    d'echantillonnage : sans lui la table porterait des centaines de paires qui
    bougent de moins d'une unite.
    """
    ouv_t, _ = inter_lettre(st, a, b, k_amont)
    ouv_a, _ = inter_lettre(sa, a, b, k_amont)
    if ouv_t is None or ouv_a is None:
        return None
    seuil = SEUIL_PAIRE if seuil is None else seuil
    ouverture = ouv_t - ouv_a
    if ouverture < seuil:
        return None
    pl_t = couloir_plein(st, a, b, k_amont)
    pl_a = couloir_plein(sa, a, b, k_amont)
    if pl_t is None or pl_a is None:
        return None
    marge = pl_t - pl_a
    valeur = min(ouverture, marge)
    if valeur < seuil:
        return None
    return -round(valeur, 1)


def rythme(src, a, b, k=0.0, seul="m"):
    """L'asymetrie des deux blancs de "ab", comparee a celle de la lettre `seul`.

    Trois verticales et deux blancs des deux cotes : dans "rn" le fut du r, le
    fut du n et la jambe du n ; dans le m ses trois futs. Le premier blanc de
    "rn" est l'inter-lettre, borne en haut par le bras du r ; le second est la
    contreforme du n. Dans le m les deux blancs sont egaux par construction, et
    c'est ce qui rend l'ecart lisible : plus le rapport de "ab" s'eloigne de
    celui de `seul`, plus le groupe cesse de battre comme la lettre.

    Rend un dict. `rapport` est le premier blanc divise par le second ; `ecart`
    est la difference des deux rapports. Aucun pixel n'entre dans cette mesure,
    donc elle ne depend d'aucune resolution et ne peut pas mentir par cadrage.
    """
    b1_min, b1 = inter_lettre(src, a, b, k)
    cf_b = contreformes(src, b)
    b2 = blanc_moyen(cf_b, 0)
    cf_s = contreformes(src, seul)
    s1 = blanc_moyen(cf_s, 0)
    s2 = blanc_moyen(cf_s, 1)
    r_ab = b1 / b2 if b2 else float("inf")
    r_s = s1 / s2 if s2 else float("inf")
    return dict(b1=b1, b1_min=b1_min, b2=b2, rapport=r_ab,
                s1=s1, s2=s2, rapport_seul=r_s, ecart=r_ab - r_s)


def distance_rn_m_kern(font, master_id, k=0.0, px=120, rayon=3.0):
    """`termes.distance_rn_m`, mais avec le crenage.

    L'original compose le n a `lr.width` exactement, donc a crenage nul. La
    police applique +10 dans les huit masters : les chiffres du vingt-et-unieme
    tour sont mesures sur un groupe plus serre que celui qui est compose. Et
    comme la mesure renormalise la largeur, le seul effet d'un crenage qu'elle
    peut enregistrer est le deplacement du fut du n dans le groupe ramene a
    largeur constante. C'est reel mais faible : lire cette colonne seule ferait
    conclure qu'un espacement ne sert a rien. La lire avec `rythme` est le
    protocole.
    """
    import lot2 as L
    import mesure_O as MO

    def lay(nom):
        for l in font.glyphs[nom].layers:
            if l.layerId == master_id:
                return l
        return None

    lr, ln, lm = lay("r"), lay("n"), lay("m")
    groupe = [D.flatten(p) for p in L.paths(lr)]
    dec = float(lr.width) + k
    groupe += [[(x + dec, y) for x, y in D.flatten(p)] for p in L.paths(ln)]
    seul = [D.flatten(p) for p in L.paths(lm)]
    return MO.confusion((groupe, []), (seul, []), px, rayon)


# ------------------------------------------------- composer un texte crene

def table_kern(font, master_id, texte, ajouts=None):
    """Le crenage effectif de chaque paire d'un texte, police plus ajouts.

    `ajouts` est un dict dont la cle est soit une paire ("F", "r"), soit un
    glyphe seul avec un cote — ("F", None) pour l'approche droite du F, donc
    toutes ses paires, et (None, "s") pour l'approche gauche du s. Une approche
    de glyphe est bien un ajout de crenage ici et non une chasse modifiee : le
    resultat compose est le meme, et la planche n'a pas a toucher la source pour
    montrer ce qu'une chasse ferait. La difference apparaitra au moment d'ecrire,
    pas au moment de juger.
    """
    ajouts = ajouts or {}
    out = {}
    noms = [D.nom_glyphe(font, c) for c in texte]
    for i in range(len(noms) - 1):
        a, b = noms[i], noms[i + 1]
        if a is None or b is None:
            continue
        v = kern(font, master_id, a, b)
        v += ajouts.get((a, b), 0.0)
        v += ajouts.get((a, None), 0.0)
        v += ajouts.get((None, b), 0.0)
        out[i] = v
    return out


def composer(img, src, master_id, texte, x, y, taille, ajouts=None,
             encre=(24, 24, 30)):
    """`dessin.dessiner`, mais avec le crenage de la police et les ajouts.

    Ecrit parce que `dessin.dessiner` avance de la seule chasse : toutes les
    planches du projet montrent donc du texte non crene. C'est sans consequence
    tant qu'on juge une forme, et c'est fatal des qu'on juge un espacement —
    comparer une correction a un etat non crene comparerait a un texte qui
    n'existe pas. Rend la largeur avancee.
    """
    k = taille / src.upem
    tab = table_kern(src.font, master_id, texte, ajouts)
    pen = float(x)
    couches = []
    for i, ch in enumerate(texte):
        nom = D.nom_glyphe(src.font, ch)
        if nom is None:
            pen += taille * 0.3
            continue
        # LE CLASSEMENT EST PAR IMBRICATION, ET GLYPHE PAR GLYPHE. Classer par
        # le signe de l'aire mettait le bras du O -- contour positif pose DANS
        # la contreforme -- avec les pleins, donc peint AVANT le creux qui
        # l'efface : toute planche composant un O capitale depuis la source
        # servie montrait un O sans bras, sans erreur et sans avertissement.
        # C'est le piege du peintre du douzieme tour, retombe dans le seul
        # peintre que les planches qui jugent un blanc doivent employer.
        couches += D.couches_ecran(
            src.contours(nom),
            lambda px, py, p=pen: (p + px * k, y - py * k))
        pen += src.width(nom) * k + tab.get(i, 0.0) * k
    D.peindre_couches(img, couches, encre=encre)
    return pen - x


def largeur_composee(src, master_id, texte, taille, ajouts=None):
    k = taille / src.upem
    tab = table_kern(src.font, master_id, texte, ajouts)
    tot = 0.0
    for i, ch in enumerate(texte):
        nom = D.nom_glyphe(src.font, ch)
        tot += (src.width(nom) if nom else src.upem * 0.3) * k + tab.get(i, 0.0) * k
    return tot


# ------------------------------------------------ la table ecrite, vingt-troisieme tour
#
# Tranche par Nicolas au vingt-troisieme tour, sur les planches
# `planche-lot4w-1-F.png` et `-4-F-rondes.png`.
#
# Ce qui est ecrit : l'approche droite du F, et le crenage r+n. Rien d'autre.
# Le l, le s et le S capitale sont mesures et non traites — leur ecart vaut 35 a
# 48 unites contre 101 a 149 pour le F, et Nicolas a choisi de les juger sur du
# texte servi en navigateur plutot que sur planche. Voir le point ouvert 39.

#: Le recul de l'approche droite du F, par source, en unites.
#:
#: La valeur n'est pas choisie, elle est le recul mesure du couloir devant les
#: futs : 99,7 a 105,2 unites en romain, 113,1 a 118,1 en italique. L'ecart
#: entre les deux vient du F italique, dont la barre mediane recule de 121 a
#: 124 unites quand celle du romain en recule 108. Une valeur unique aurait
#: laisse l'italique a moitie corrige, et le projet a deja paye une mesure
#: prise d'un seul cote de l'axe d'inclinaison — le plafond de coupe du l,
#: point ouvert 37.
#:
#: Les rondes en demandaient 118 a 130 : elles gardent donc 18 a 30 unites de
#: plus qu'Atkinson. Nicolas a vu les deux etats en grand, a 18 px et a 72 px,
#: et a retenu l'approche seule.
APPROCHE_F = {"roman": -100.0, "italic": -115.0}

#: Les correctifs de l'approche du F, master par master, en unites.
#:
#: Une approche de glyphe touche toutes ses paires, y compris celles que la
#: coupe n'avait jamais ouvertes : F+J est crenee a -30 par Atkinson, F+point,
#: F+virgule et F+apostrophe entre -24 et -50. Sans correctif, l'approche les
#: serrerait de sa valeur entiere. S'y ajoutent F+a et F+agrave dans les
#: masters clairs, ou l'ecart ne vaut que 19 unites au lieu de 113 a 149.
#:
#: Une valeur est un AJOUT au crenage existant de la paire, et elle
#: s'additionne a l'approche : +100 sur une approche de -100 rend la paire a son
#: crenage d'Atkinson. `table_kern` additionne les trois entrees, (a, b),
#: (a, None) et (None, b) — le premier jet rendait des valeurs totales que le
#: garde-fou lisait en remplacement quand la composition les sommait, et les
#: deux annoncaient un accord sur des chiffres differents.
#:
#: Ecrite en clair et non calculee a l'execution : le bac a sable ne peut pas
#: toujours cloner la source amont, et un contrôle qui n'a pas pu lire sa source
#: ne doit rien conclure. `check_approches.py` la recalcule quand la source est
#: la, et se declare non fait quand elle manque.
#:
#: Le premier jet de cette table testait 36 voisins et oubliait les capitales :
#: F+J n'y figurait pas. Le voisinage fait foi, il est dans
#: `planche_lot4w_approches.VOISINS_F`, et il en compte 71.
CORRECTIFS_F = {
    "ExtraLight": {"J": +64.2, "a": +82.0, "agrave": +82.0, "colon": +100.0,
                   "comma": +100.0, "hyphen": +100.0, "period": +100.0,
                   "quotedblleft": +100.0, "quoteright": +100.0,
                   "quotesingle": +100.0, "semicolon": +100.0},
    "Regular": {"J": +89.0, "comma": +100.0, "hyphen": +100.0,
                "period": +100.0, "quotedblleft": +100.0, "quoteright": +100.0,
                "quotesingle": +100.0},
    "Bold": {"J": +100.0, "comma": +100.0, "period": +100.0,
             "quotesingle": +100.0},
    "ExtraBold": {"J": +100.0, "comma": +100.0, "period": +100.0,
                  "quotesingle": +100.0},
    "ExtraLight Italic": {"J": +81.2, "a": +95.7, "agrave": +95.7,
                          "colon": +115.0, "comma": +115.0, "hyphen": +115.0,
                          "period": +115.0, "quotedblleft": +115.0,
                          "quoteright": +115.0, "quotesingle": +115.0,
                          "semicolon": +115.0},
    "Italic": {"J": +105.1, "comma": +115.0, "hyphen": +115.0,
               "period": +115.0, "quotedblleft": +115.0, "quoteright": +115.0,
               "quotesingle": +115.0},
    "Bold Italic": {"J": +115.0, "comma": +115.0, "period": +115.0,
                    "quotesingle": +115.0},
    "ExtraBold Italic": {"J": +115.0, "comma": +115.0, "period": +115.0,
                         "quotesingle": +115.0},
}

#: Le crenage des paires, valeur TOTALE et non ajout, tous masters.
#:
#: r+n a +20 : Atkinson crene deja cette paire a +10 dans les huit masters, et
#: Nicolas a retenu un intermediaire entre cet etat et les +30 de la planche.
#: A savoir, et c'est mesure : +20 ne franchit la reference d'aucun master. Il
#: reste 0,088 en ExtraLight, 0,049 au Regular, 0,039 au Bold et 0,035 a
#: l'ExtraBold sous la paire la plus serree de l'etalonnage. La paire rn/m reste
#: donc plus confusable que la paire la plus confusable de la police de base, et
#: le geste est un choix de dessin. A revoir sur du texte servi une fois la
#: police compilee — decision de Nicolas, point ouvert 39.
#:
#: La valeur porte sur la paire de groupes @MMK_L_r + @MMK_R_n, donc sur r+n,
#: r+m et les accentuees nacute, ncaron, ntilde, ncommaaccent. En francais, r+n
#: et r+m sont les deux qui servent.
KERN_PAIRES = {("r", "n"): +20.0}

# ------------------------------------------- les trois reglages du cinquantieme
#
# TROIS DEMANDES DE NICOLAS, PRISES EN LISANT `tour50.html` A 18 PX, tranchees
# sur `tour50-espacement.html` a quatre sections.
#
# **CE QUI LES DISTINGUE DE TOUT LE RESTE DU CRENAGE DU PROJET.** Les deux
# tables de paires REFERMENT ce que les coupes du projet ont ouvert, et leur
# borne est le couloir d'Atkinson : elles ne vont jamais plus serre que la
# police de base. Ici les trois paires sont IDENTIQUES entre l'amont et l'etat
# servi, au dixieme d'unite pres, dans les quatre masters romains -- le projet
# n'a rien ouvert la, et ces reglages CORRIGENT LA POLICE DE BASE. C'est la
# quatrieme fois que le projet le fait, apres `REGLAGE_F_RONDES`,
# `REGLAGE_F_I` et `REGLAGE_F_ESPACE`, toutes sur le F.
#
# **AUCUN N'EST BORNE PAR UN CONTACT, ET C'EST MESURE.** Le couloir le plus
# etroit avant ajustement vaut 153 unites sur `l+'` et 167 sur `L+y` ; apres, le
# plus serre du lot est `L+w` a l'ExtraBold, a 60 unites, tres au-dessus du
# plancher de jour de 24. La limite etait donc l'oeil, et la page d'etats le
# disait.

#: `l` suivi de l'apostrophe, resserre de 20 unites. Etats juges : servi, -20,
#: -40, -60, -80.
#:
#: **Le l est l'anomalie de sa famille, et le chiffre le designe.** Blanc moyen
#: entre la lettre et l'apostrophe, quatre masters romains : le l vaut 170, 185,
#: 205 et 209 quand le d vaut 141, 145, 126 et 123, le j 122 a 135 et le u 125 a
#: 145. Le n et le m, eux, sont deja crenes par Atkinson a -20 et -40. Aligner
#: le l sur le d aurait demande jusqu'a -86 dans les gras ; Nicolas a retenu -20
#: partout, donc la correction ne ferme qu'un quart de l'ecart.
#:
#: **Ecrit en exception glyphe-glyphe et non sur la cle de groupe** : le groupe
#: de l'apostrophe porte aussi `quotedblright`, que le francais n'emploie pas
#: derriere une lettre, et une valeur par paire dit exactement ce qu'elle fait.
REGLAGE_L_APOSTROPHE = -20.0

#: L'apostrophe suivie de `i` circonflexe ou trema, ECARTEE de 20 unites.
#: Etats juges : servi, +10, +20, +30.
#:
#: **C'est le seul cas geometriquement fautif des trois, et il vient d'Atkinson.**
#: Le couloir de `'+i` circonflexe vaut 44, 30, 17 et 18 unites du clair au gras
#: en romain, et 42, 21, 16, 16 en italique : il passe SOUS le plancher de jour
#: du projet, 24 unites, dans les deux gras des deux sources. Le trema suit a 36
#: a 57. L'accent monte et vient sous l'apostrophe ; le i nu, lui, garde 105 a
#: 129 unites et ne bouge pas.
#:
#: **La pointe du circonflexe du quarante-et-unieme tour n'y est pour rien**, et
#: c'est mesure : les couloirs sont identiques a l'amont. Le geste monte le
#: SOMMET de l'accent, quand le couloir se joue sur son FLANC gauche.
#:
#: **Ecrit sur les deux noms et non sur le groupe du i** : le groupe porte aussi
#: `i`, `idotless`, `iacute` et `igrave`, dont le couloir n'a rien de fautif.
#: Ecarter un couloir sain de 20 unites serait un defaut nouveau.
REGLAGE_APOSTROPHE_I_ACCENTUE = 20.0
NOMS_I_ACCENTUE = ("icircumflex", "idieresis")

#: Le `L` devant les diagonales du bas de casse, resserre de 60 unites.
#: Etats juges : servi, -40, -60, -80, -100.
#:
#: **L'incoherence corrigee est celle d'Atkinson, et elle se lit dans ses
#: propres valeurs** : il crene `L+Y` a -80, `L+V` a -70, `L+T` a -70 et `L+W` a
#: -50, et il laisse `L+y`, `L+v` et `L+w` a ZERO dans les quatre masters
#: romains. Les capitales a diagonale sont crenees, leurs minuscules ne le sont
#: pas.
#:
#: **Ecrit sur la CLE DE GROUPE, et c'est le seul des trois.** Le groupe droit
#: du L ne contient que le L parmi les servis ; le groupe gauche du v en
#: contient cinq : `v w y yacute ydieresis`. Leurs couloirs sont identiques a
#: une unite pres, 167 a 175 au romain. Trois exceptions glyphe-glyphe auraient
#: laisse `Ly` corrige et `Lý` intact, donc ecrit une incoherence nouvelle a la
#: place de celle qu'on corrige.
#:
#: En italique la cle de groupe porte deja -15 a -20, ecrits par Atkinson : le
#: reglage s'y CUMULE, comme partout ailleurs dans ce module.
REGLAGE_L_DIAGONALES = -60.0
CIBLE_L_DIAGONALES = ("L", "y")


def source_de(font):
    """"roman" ou "italic", lu sur les noms de masters et non sur le chemin.

    Un chemin peut etre celui d'une copie, d'un fichier renomme ou d'un flux ;
    les noms de masters, eux, appartiennent a la source.
    """
    return ("italic" if any("Italic" in m.name for m in font.masters)
            else "roman")


def appliquer(font, journal=None, pieds=True, bouts=True, contacts=True):
    """Ecrit le crenage du projet dans la source. Modifie `font`.

    `pieds=False` ecrit tout sauf la table du point ouvert 50. Le drapeau existe
    pour son generateur : `inventaire_pieds.py` doit mesurer un couloir que sa
    propre table n'a pas encore ecarte, sans quoi il ne verrait plus rien a
    corriger et rendrait une table vide. Cinq contrôles de ce projet ont deja
    mesure leur propre reflet, dont deux garde-fous.

    **Aucune chasse n'est touchee depuis le vingt-quatrieme tour.** L'approche du
    F, retenue au vingt-troisieme, est retiree : elle creait six contacts de
    capitales dans le binaire servi et demandait 28 cles de correctifs par master
    pour les rattraper, dont 21 qui l'annulaient. La raison de fond est dans
    `paires_F.py` et le detail dans la passation. Le F retrouve donc sa chasse
    d'origine et le trou de sa barre mediane se referme paire par paire, avec la
    valeur que `paire_bornee` mesure.

    A appeler entre le lot 2 et le lot 3. L'ordre importait tant que l'approche
    se posait sur la chasse, pour que `f.sc` en herite au rapport du lot 3 au
    lieu de la recevoir deux fois. Il n'a plus d'effet sur les approches, et il
    est conserve : le crenage ne se propage pas aux petites capitales, donc
    `f.sc` porte encore le trou de sa barre mediane. **C'est un point ouvert, et
    il est nouveau** : un sigle en petites capitales commencant par F composera
    plus lache que le meme en capitales pleines.
    """
    journal = journal if journal is not None else []

    # 1. le crenage du F, paire par paire et en exception glyphe-glyphe
    for m in font.masters:
        for voisin, valeur in PAIRES_F.get(m.name, {}).items():
            if font.glyphs[voisin] is None:
                continue
            ecrire_kern(font, m.id, "F", voisin, valeur, exception=True)
            journal.append(("paire F", f"F+{voisin}", m.name, valeur, None))

    # 1bis. le reglage du F sur retour navigateur, trente-et-unieme tour
    #
    # Lu APRES l'etape 1 et ecrit une seule fois par paire : la base est donc
    # la valeur que la table vient d'ecrire, et non celle d'Atkinson. Le piege
    # du vingt-quatrieme tour est ailleurs et il ne retombe pas ici — il venait
    # de deux entrees partageant une cle de GROUPE, `comma` et `period`, quand
    # ces ecritures sont toutes en exception glyphe-glyphe, donc une cle par
    # paire et aucune relecture croisee.
    for m in font.masters:
        for b in RONDES_F:
            if font.glyphs[b] is None:
                continue
            base = kern(font, m.id, "F", b)
            v = round(base + REGLAGE_F_RONDES, 1)
            ecrire_kern(font, m.id, "F", b, v, exception=True)
            journal.append(("reglage F ronde", f"F+{b}", m.name, v, None))
        # LE F DEVANT LE A, cinquante-quatrieme tour. Meme forme que le
        # reglage des rondes : base lue APRES la table du F, ecriture en
        # exception glyphe-glyphe, une seule cle par paire. Les trois
        # accentuees suivent le A, decision de Nicolas ; l'AE n'y est pas.
        for b in DIAGONALES_F:
            if font.glyphs[b] is None:
                continue
            base = kern(font, m.id, "F", b)
            v = round(base + REGLAGE_F_A, 1)
            ecrire_kern(font, m.id, "F", b, v, exception=True)
            journal.append(("reglage F diagonale", f"F+{b}", m.name, v, None))
        di = REGLAGE_F_I.get(m.name)
        if di is not None and font.glyphs["i"] is not None:
            base = kern(font, m.id, "F", "i")
            v = round(base + di, 1)
            ecrire_kern(font, m.id, "F", "i", v, exception=True)
            journal.append(("reglage F i", "F+i", m.name, v, None))
        # LE F DEVANT L'ESPACE, quarante-troisieme tour, point ouvert 76.
        #
        # Meme forme que les deux reglages ci-dessus -- base lue APRES la table
        # du F, ecriture en exception glyphe-glyphe, une seule cle par paire --
        # et la base vaut ici le crenage d'Atkinson, `PAIRES_F` ne pouvant pas
        # porter une paire dont un membre n'a pas d'encre.
        if font.glyphs[GLYPHE_ESPACE] is not None:
            base = kern(font, m.id, "F", GLYPHE_ESPACE)
            v = round(base + REGLAGE_F_ESPACE, 1)
            ecrire_kern(font, m.id, "F", GLYPHE_ESPACE, v, exception=True)
            journal.append(("reglage F espace", f"F+{GLYPHE_ESPACE}",
                            m.name, v, None))

    # 1ter. LE BLANC DEVANT L'Æ EN CAPITALES, cinquante-cinquieme tour.
    #
    # Meme forme que les reglages du F : base lue sur l'etat courant, ecriture
    # en exception glyphe-glyphe, une seule cle par paire. La base vaut ici le
    # crenage d'Atkinson, qui est NUL sur les dix paires -- aucune n'est crenee
    # en amont, et c'est ce qui a fait ouvrir le chantier.
    #
    # Sa place est APRES les reglages du F et AVANT les tables des pieds et des
    # bouts, pour la meme raison qu'eux : deux tables qui ecrivent en valeur
    # TOTALE sur la meme paire, la seconde ecrase la premiere, et le
    # cinquante-quatrieme tour a failli perdre vingt unites sur `F+c` ainsi.
    # Aucune des dix paires n'est dans les trois tables, et
    # `check_crenage_sc` le remesure au lieu de le supposer.
    #
    # TEMOIN_SANS_REGLAGE_AE=1 saute CETTE SEULE etape, et c'est la source que
    # demande `inventaire_ae.py` : il mesure le blanc devant l'Æ tel qu'il est
    # au moment ou le reglage se pose, donc avec tout le reste des approches
    # deja ecrit. `TEMOIN_SANS_APPROCHES=1` ne pouvait pas servir ici, et le
    # premier jet du producteur l'a paye : sans la table du F, `F+Æ` paraissait
    # depasser la cible de 3,7 unites et entrait dans la famille, alors que
    # `paires_F` lui donne deja -202. Un etat de mesure se choisit sur l'endroit
    # de la chaine ou la decision se prend, pas sur le drapeau qui existe deja.
    if not os.environ.get("TEMOIN_SANS_REGLAGE_AE"):
        for m in font.masters:
            for a, delta in sorted(REGLAGE_AE.get(m.name, {}).items()):
                if font.glyphs[a] is None or font.glyphs[GLYPHE_AE] is None:
                    continue
                base = kern(font, m.id, a, GLYPHE_AE)
                v = round(base + delta, 1)
                ecrire_kern(font, m.id, a, GLYPHE_AE, v, exception=True)
                journal.append(("reglage AE", f"{a}+{GLYPHE_AE}", m.name, v,
                                None))

    # 1quater. LE X DEVANT LE A, cinquante-sixieme tour.
    #
    # ECRIT SUR LA CLE DE GROUPE et non en exception, contrairement aux
    # reglages ci-dessus, et la raison est mesuree : `@MMK_R_A` porte le A, ses
    # neuf accentuees et le Delta, dont la gouttiere avec le X est la meme a
    # moins d'un dixieme d'unite. La raison optique du reglage est le flanc
    # diagonal du A, que les onze partagent -- et une prescription indexee par
    # nom ne suit pas une composition, ce que ce projet a paye cinq fois.
    #
    # Sa place est avec les autres reglages, AVANT les tables des pieds et des
    # bouts : deux tables qui ecrivent en valeur TOTALE sur la meme paire, la
    # seconde ecrase la premiere. `X+A` n'est dans aucune des trois, et
    # `inventaire_xa` le remesure avant d'ecrire au lieu de le supposer.
    #
    # TEMOIN_SANS_REGLAGE_XA=1 saute cette seule etape, et c'est la source que
    # demande le producteur : il mesure ce que la gouttiere permet de fermer,
    # donc il lui faut l'etat d'avant la fermeture.
    if not os.environ.get("TEMOIN_SANS_REGLAGE_XA"):
        a, b = CIBLE_XA
        for m in font.masters:
            delta = REGLAGE_XA.get(m.name)
            if delta is None or font.glyphs[a] is None or font.glyphs[b] is None:
                continue
            base = kern(font, m.id, a, b)
            v = round(base + delta, 1)
            ecrire_kern(font, m.id, a, b, v)
            journal.append(("reglage XA", f"{a}+{b}", m.name, v, None))

    # 2. les trois pieds gauches descendants, ecartes au plancher de jour
    #
    # Sens inverse de la table du F : le geste du lot 1 FERME le couloir, donc
    # le crenage est positif et sa borne haute est le couloir d'Atkinson. La
    # raison de chaque valeur est dans `paires_pieds.py` et son generateur.
    if pieds:
        for m in font.masters:
            for a, b, valeur in PAIRES_PIEDS.get(m.name, ()):
                if font.glyphs[a] is None or font.glyphs[b] is None:
                    continue
                ecrire_kern(font, m.id, a, b, valeur, exception=True)
                journal.append(("paire pied", f"{a}+{b}", m.name, valeur, None))

    # 2bis. les huit bouts coupes, refermes au plus que la borne permette
    #
    # Points ouverts 56, 39, 47 et le z du lot 2, groupes sur decision de
    # Nicolas au vingt-sixieme tour et traites ensemble au trente-et-unieme.
    # Meme sens et meme critere que la table du F : le geste OUVRE le couloir,
    # donc le crenage est negatif et sa borne est le couloir d'Atkinson, jamais
    # au-dela. La raison de chaque valeur est dans `paires_bouts.py`.
    #
    # `bouts=False` existe pour le generateur, comme `pieds=False` : il doit
    # mesurer une ouverture que sa propre table n'a pas encore refermee, sans
    # quoi il ne verrait plus rien et rendrait une table vide. Le projet a
    # mesure son propre reflet cinq fois, dont deux fois dans un garde-fou.
    if bouts:
        for m in font.masters:
            for a, b, valeur in PAIRES_BOUTS.get(m.name, ()):
                if font.glyphs[a] is None or font.glyphs[b] is None:
                    continue
                ecrire_kern(font, m.id, a, b, valeur, exception=True)
                journal.append(("paire bout", f"{a}+{b}", m.name, valeur, None))

    # 2quater. les paires que le titrage fusionne met en CONTACT
    #
    # Cinquante-neuvieme tour, point ouvert 18 -- qui se trompait de sens. Le
    # geste de titrage n'ouvre aucune approche : il ELARGIT la boite, jusqu'a
    # 30,6 unites au romain et 49,2 en italique, et la matiere sort vers le
    # voisin. Les trois tables ci-dessus regardent la LETTRE DE BASE et pas les
    # glyphes qui la redessinent : `A+x` recoit +36 au Bold quand `Agrave+x`
    # recoit 0, et 86 glyphe-masters etaient en CONTACT dans l'etat servi,
    # prouve au comptage de taches d'encre a trois resolutions et absent
    # d'Atkinson.
    #
    # LA CLE EST CELLE QUE LA MESURE DONNE, et elle est ecrite dans la table :
    # "groupe" quand tous les membres du groupe de crenage droit de `a` ont la
    # meme gouttiere devant `b`, "glyphe" sinon. Mesure : le groupe droit du
    # `A` porte onze noms, dont `Aogonek` et `Delta`, et l'ecart y atteint 198
    # unites -- la gouttiere se lit sur toute la hauteur, accent compris. Six
    # paires seulement s'ecrivent sur un groupe.
    #
    # `contacts=False` existe pour le generateur, comme `pieds` et `bouts`.
    if contacts:
        for m in font.masters:
            for a, b, valeur, cle, _crit in PAIRES_CONTACTS.get(m.name, ()):
                if font.glyphs[a] is None or font.glyphs[b] is None:
                    continue
                ecrire_kern(font, m.id, a, b, valeur,
                            exception=(cle == "glyphe"))
                journal.append(("paire contact", f"{a}+{b}", m.name, valeur,
                                cle))

    # 2ter. les trois reglages du cinquantieme tour
    #
    # Places APRES les deux tables, comme les trois reglages du F : la base est
    # l'etat que la chaine vient d'ecrire, jamais celui d'Atkinson suppose.
    # Aucune des trois paires n'est dans une table aujourd'hui -- mesure, et non
    # suppose -- mais lire la base au lieu de l'ecrire en valeur totale est ce
    # qui rend le bloc vrai le jour ou une table les recevra.
    #
    # Les deux premiers s'ecrivent en exception glyphe-glyphe, le troisieme sur
    # la cle de groupe : la raison de chacun vit a cote de sa constante.
    for m in font.masters:
        if font.glyphs["l"] is not None and font.glyphs["quoteright"] is not None:
            base = kern(font, m.id, "l", "quoteright")
            v = round(base + REGLAGE_L_APOSTROPHE, 1)
            ecrire_kern(font, m.id, "l", "quoteright", v, exception=True)
            journal.append(("reglage l apostrophe", "l+quoteright",
                            m.name, v, None))
        for nom in NOMS_I_ACCENTUE:
            if font.glyphs[nom] is None or font.glyphs["quoteright"] is None:
                continue
            base = kern(font, m.id, "quoteright", nom)
            v = round(base + REGLAGE_APOSTROPHE_I_ACCENTUE, 1)
            ecrire_kern(font, m.id, "quoteright", nom, v, exception=True)
            journal.append(("reglage apostrophe i accentue",
                            f"quoteright+{nom}", m.name, v, None))
        a, b = CIBLE_L_DIAGONALES
        if font.glyphs[a] is not None and font.glyphs[b] is not None:
            base = kern(font, m.id, a, b)
            v = round(base + REGLAGE_L_DIAGONALES, 1)
            # exception=False : la cle de GROUPE, qui porte v w y yacute
            # ydieresis. `ecrire_kern` leve si une cle plus specifique existe
            # deja et rendrait l'ecriture sans effet.
            ecrire_kern(font, m.id, a, b, v, exception=False)
            journal.append(("reglage L diagonales", f"{a}+{b} (groupe)",
                            m.name, v, None))

    # 3. les autres paires, en valeur totale et sur la cle de groupe
    for (a, b), valeur in KERN_PAIRES.items():
        for m in font.masters:
            ecrire_kern(font, m.id, a, b, valeur)
            journal.append(("paire", f"{a}+{b}", m.name, valeur, None))
    return journal


def ecrire_kern(font, master_id, a, b, valeur, exception=False):
    """Ecrit une valeur de crenage sur la cle que la police emploie pour la paire.

    Les groupes d'abord, comme `kern` les lit : ecrire une paire directe la ou
    Atkinson crene par groupe laisserait la valeur de groupe en place et
    dependrait de l'ordre de resolution du moteur. Une seule des deux doit
    exister.

    Un garde, ajoute apres la decouverte des exceptions a cle mixte : si une cle
    plus specifique que celle qu'on ecrit porte deja une valeur, elle l'emportera
    et **l'ecriture ne servirait a rien**. Le cas ne se presente sur aucune paire
    des tables actuelles, et c'est verifie a chaque passage plutot que suppose —
    la phrase « aucune paire du projet n'en a » etait deja ecrite une fois, et
    elle etait fausse. On leve, parce qu'un refus vaut mieux qu'un avertissement :
    `make_temoin.py` a refuse de s'executer sur la coupe de la queue du t au
    vingt-deuxieme tour, et c'est ce refus qui a fait decouvrir que 20 degres
    etaient impossibles en italique gras.
    """
    K = font.kerning.setdefault(master_id, {})
    cles = cles_kern(font, a, b)
    if exception:
        # La cle glyphe-glyphe, la plus specifique : elle l'emporte sur le
        # groupe et ne touche que cette paire. C'est ainsi que la table du F est
        # ecrite depuis le vingt-quatrieme tour, et la raison est mesuree : sur
        # la cle de groupe, `odieresis` ramenerait F+o de -124 a -90 et
        # `ydieresis` ramenerait F+v de -100 a -32, parce qu'un trema monte et
        # limite ce qu'on peut refermer. Une valeur par paire dit exactement ce
        # qu'elle fait, et le raisonnement par groupe a deja coute deux bugs
        # dans ce projet.
        K.setdefault(cles[0][0], {})[cles[0][1]] = valeur
        return
    cible = cles[-1]
    for ka, kb in cles[:-1]:
        if K.get(ka, {}).get(kb) is not None:
            raise ValueError(
                f"crenage {a}+{b} : la cle ({ka}, {kb}) est plus specifique que "
                f"({cible[0]}, {cible[1]}) et l'emporterait. Ecrire sur la cle "
                f"de groupe ne servirait a rien.")
    K.setdefault(cible[0], {})[cible[1]] = valeur


def retirer_contacts(font, amont=None):
    """Defait, EN MEMOIRE, ce que `PAIRES_CONTACTS` a ecrit dans cette source.

    Son producteur lit l'etat SERVI et non une reconstruction : sans ce
    retrait, il mesurerait des paires que sa propre table vient de refermer,
    ne verrait plus rien a corriger, et rendrait une table VIDE. Le projet a
    mesure son propre reflet cinq fois, dont deux fois dans un garde-fou, et
    `pieds=False` comme `bouts=False` existent pour la meme raison.

    Le retrait vise la cle REELLEMENT ecrite, et elle seule : la plus
    specifique pour une exception, la moins pour une valeur de groupe. Balayer
    les quatre effacerait une valeur qu'Atkinson porte et que cette table n'a
    jamais posee.

    SUPPRIMER NE SUFFIT PAS, ET C'EST MESURE. Trois des entrees de groupe
    ecrivent sur une cle qu'Atkinson porte deja -- la table y ecrit une valeur
    TOTALE, donc elle l'ecrase. Les supprimer rendrait un etat plus lache que
    la police de base, et le producteur mesurerait alors un defaut qu'il aurait
    lui-meme fabrique. Avec `amont`, la valeur d'origine est RESTAUREE ; sans
    lui, la cle est supprimee et le compte des restaurations vaut zero. Les
    masters s'apparient par NOM : leurs identifiants different d'un fichier a
    l'autre.

    UNE CLE NE SE RETIRE QUE SI ELLE PORTE LA VALEUR DE LA TABLE. Rien dans la
    source ne dit qui a ecrit une cle : trois des entrees de groupe visent une
    cle qu'Atkinson porte deja, et deux etapes posterieures -- `crenage_sc` et
    le reglage `X+A` -- ecrivent elles aussi sur des cles de groupe. Retirer
    sur le seul nom de la cle effacerait le travail d'un autre. Une cle qui
    porte une AUTRE valeur est donc laissee en place et comptee a part : c'est
    le signe qu'une etape posterieure a repris la paire, et cela se signale au
    lieu de s'ecraser.

    Rend (supprimees, restaurees, etrangeres), pour qu'un retrait qui ne
    retire rien se voie.
    """
    n = r = e = 0
    ida = ({m.name: m.id for m in amont.masters} if amont is not None else {})
    for m in font.masters:
        K = font.kerning.get(m.id, {})
        KA = (amont.kerning.get(ida.get(m.name), {})
              if amont is not None and m.name in ida else {})
        for a, b, v, cle, _c in PAIRES_CONTACTS.get(m.name, ()):
            if font.glyphs[a] is None or font.glyphs[b] is None:
                continue
            cles = cles_kern(font, a, b)
            ka, kb = cles[0] if cle == "glyphe" else cles[-1]
            pose = K.get(ka, {}).get(kb)
            if pose is None:
                continue
            if abs(pose - v) > 0.01:
                e += 1
                continue
            avant = KA.get(ka, {}).get(kb)
            if avant is None:
                del K[ka][kb]
                n += 1
            else:
                K[ka][kb] = avant
                r += 1
    return n, r, e


# ------------------------------------------------------------------ temoin

def temoin(chemin="Temoin.glyphs", master="Bold"):
    """Prouve que les deux mesures savent signaler, avant de croire un zero.

    Le projet compte trois controles qui rendaient une valeur constante et un
    quatrieme qui rendait 0,000 sur toute une famille. Une mesure d'espacement
    qui ne bouge pas quand on bouge l'espacement est du meme genre. On pousse
    donc le crenage a +200 unites, valeur absurde, et on verifie que les deux
    grandeurs bougent dans le sens attendu.
    """
    f = glyphsLib.load(open(chemin))
    mid = [m for m in f.masters if m.name == master][0].id
    s = D.Source(f, master)
    k0 = kern(f, mid, "r", "n")
    lignes = []
    for k in (k0, k0 + 200.0):
        R = rythme(s, "r", "n", k)
        d = distance_rn_m_kern(f, mid, k)
        lignes.append((k, R["b1"], R["rapport"], R["ecart"], d))
    (ka, b1a, ra, ea, da), (kb, b1b, rb, eb, db) = lignes
    print(f"temoin sur {master}, crenage {ka:.0f} -> {kb:.0f}")
    print(f"  blanc 1        {b1a:8.1f} -> {b1b:8.1f}   {b1b-b1a:+8.1f}")
    print(f"  rapport b1/b2  {ra:8.3f} -> {rb:8.3f}   {rb-ra:+8.3f}")
    print(f"  ecart au m     {ea:8.3f} -> {eb:8.3f}   {eb-ea:+8.3f}")
    print(f"  rn/m rasterise {da:8.3f} -> {db:8.3f}   {db-da:+8.3f}")
    ok = (b1b - b1a > 150) and (rb - ra > 0.5) and (db > da)
    print("  -> les deux mesures discriminent" if ok
          else "  -> AU MOINS UNE MESURE NE DISCRIMINE PAS, ne rien conclure d'elle")
    return ok


if __name__ == "__main__":
    import sys
    if "--temoin" in sys.argv:
        temoin()
