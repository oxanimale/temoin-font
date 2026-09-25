# Témoin

Police de caractères de l'Observatoire de l'Expérimentation Animale, pour le
site oxanimale.fr et ses documents.

Témoin est une version modifiée d'**Atkinson Hyperlegible Next**, publiée sous
SIL Open Font License 1.1. Version 1.000, 25 septembre 2026.

Quatre fichiers variables, romain et italique :

- deux WOFF2 pour le web, axe de graisse 400 à 800, sous-ensemblés au latin
  français
- deux TTF pour l'installation, axe de graisse 200 à 800, répertoire complet

## La police de base, et ce que l'OXA lui doit

Atkinson Hyperlegible Next a été dessinée par Elliott Scott, Megan Eiswerth,
Linus Boman et Theodore Petrosky, avec Letters from Sweden, pour le Braille
Institute of America. Tout ce qui fait la qualité de ses formes vient d'eux.

**Le Braille Institute of America n'a ni approuvé, ni soutenu, ni relu cette
version.** La clause 4 de l'OFL interdit d'employer le nom des auteurs
d'origine pour promouvoir une version modifiée, et autorise explicitement à
reconnaître leur contribution : cette section est cette reconnaissance, et rien
d'autre.

Le renommage tient à la marque probable du Braille Institute et à cette même
clause 4. L'OFL d'Atkinson ne déclare aucun Reserved Font Name, vérifié sur le
fichier.

## Ce que l'OXA a changé

- **Zéro contextuel.** Le zéro barré d'Atkinson devient net dès qu'un chiffre le
  voisine, et reste barré isolé ou collé à une lettre, ce qui préserve la
  distinction entre 0 et O. Jeu stylistique `ss01`, libellé Unslashed zero.
- **Système de coupes de terminaison.** Chaque terminaison libre voit sa coupe
  tourner de 20 degrés, l'angle de la diagonale du A, autour de celui de ses
  deux coins qui fait rentrer l'autre dans la lettre.
- **Petites capitales**, absentes d'Atkinson : 44 glyphes dérivés des capitales,
  avec leur propre crénage. Features `smcp` et `c2sc`.
- **Espacement et crénage**, cinq tables de paires produites par mesure et
  bornées par ce qu'on peut refermer sans passer sous la police de base.
- **Espace fine insécable** U+202F, absente d'Atkinson et nécessaire à la
  ponctuation française.
- **Bras du O capitale**, sur la seule source romaine.
- **Barre médiane du F et de l'E**, dont le décrochage dans les gras vient
  d'Atkinson et se partage ici entre les deux lettres.

## Ce que le projet ne revendique pas

**Ni l'accessibilité, ni la lisibilité.** La relecture par un typographe est
abandonnée pour ce livrable, donc rien n'est affirmé de ce côté. Le projet
montre ce qu'il a mesuré, avec ses chiffres et ses dégradations assumées.

Atkinson Hyperlegible Next est conçue pour la lisibilité. Témoin en dérive et
la modifie : les propriétés de la base ne se transmettent pas automatiquement à
une version modifiée, et l'OXA ne les a pas fait vérifier.

## Limites connues

- Quatre glyphes portent un contour qui se recoupe ou une terminaison qui
  s'aplatit le long de l'axe : `tildecomb` et `brevecomb` dans les deux sources,
  `commaaccentcomb` en italique, plus le `l` romain. Mesuré entre 0,004 et
  0,113 % de l'aire d'encre du glyphe, invisible à 18 px comme à 420 px. À titre
  de comparaison, le bras du O, qui est voulu, se recoupe de 2,6 %. Surveillé
  par `build/check_final.py`, section 8.
- Des paires héritées d'Atkinson passent sous le plancher de jour du projet,
  sur des accents bas de casse devant un chiffre ou une capitale à diagonale.
  Le projet ne les resserre pas et ne les corrige pas.
- Le nom d'affichage accentué est écrit comme nom localisé français, vérifié
  dans la table `name` du binaire servi. Aucun système d'exploitation réel n'a
  encore été interrogé sur son menu de police.

## Employer la police

Le dossier `fonts/` porte deux formats.

```
Temoin.woff2               web, graisse 400 à 800, 311 glyphes, 39 Ko
Temoin-Italic.woff2        web, graisse 400 à 800, 311 glyphes, 42 Ko
Temoin[wght].ttf           installation, graisse 200 à 800, 439 glyphes
Temoin-Italic[wght].ttf    installation, graisse 200 à 800, 439 glyphes
```

Les gabarits de pages de l'OXA emploient les graisses 400 à 700, et retirer
l'ExtraLight allège chaque WOFF2 de 9 Ko. Les graisses 200 et 300 restent dans les TTF.
Avec les WOFF2, le navigateur affiche en Regular une graisse demandée sous 400.

Pour le web, copiez les deux WOFF2 là où votre site les sert, et déclarez-les
ainsi.

```css
@font-face {
  font-family: "Témoin";
  src: url("Temoin.woff2") format("woff2-variations");
  font-weight: 400 800;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: "Témoin";
  src: url("Temoin-Italic.woff2") format("woff2-variations");
  font-weight: 400 800;
  font-style: italic;
  font-display: swap;
}
```

Le zéro contextuel tient à `calt`, actif par défaut. `ss01` dénude le zéro dans
tous les contextes, y compris isolé. Les petites capitales s'activent par
`font-variant-caps: all-small-caps`. La valeur `small-caps` ne transforme que
les minuscules.

## Ce que ce dépôt contient

```
OFL.txt              la licence, avec les deux notices de copyright
FONTLOG.txt          l'historique, convention SIL
fonts/               les deux WOFF2, les deux TTF et une copie de la licence
build/               les sources .glyphs et la chaîne complète
```

`build/` porte 62 modules Python, plus `faire_depot.py`, le script qui assemble
ce dépôt : la chaîne de compilation, les contrôles, et les producteurs des
tables d'espacement. Le dossier de travail du projet compte 193 fichiers
Python. Les 130 écartés sont des balayages, des générateurs de planches et des
essais, qu'aucun module publié n'importe. `faire_depot.py` porte la liste
retenue, dit pourquoi chaque écarté l'est, et vérifie à chaque passage
qu'aucun module publié n'appelle un module absent.

Le dossier de travail range les fontes dans `gabarits/fonts/`, à côté de son
banc d'essai, d'où ce nom dans certains commentaires. La chaîne prend le
premier des deux dossiers qui existe, `fonts/` puis `gabarits/fonts/`.

## Compiler

La chaîne reproduit à l'octet les quatre fichiers de `fonts/` dans
l'environnement suivant, sous Python 3.12.3. Changer la version d'une seule
bibliothèque peut suffire à changer les sources : en septembre 2026, une
réinstallation a déplacé d'un dixième d'unité deux points du glyphe `comma`,
sans que glyphsLib ni fontTools en soient la cause.

```
python3 -m venv .venv
. .venv/bin/activate
pip install attrs==26.1.0 booleanOperations==0.10.0 brotli==1.2.0 \
    cffsubr==0.4.0 compreffor==0.6.0 fontmake==3.12.1 fontMath==0.10.0 \
    fonttools==4.66.0 freetype-py==2.5.1 glyphsLib==6.15.0 lxml==6.1.3 \
    numpy==2.5.3 openstep_plist==0.5.2 pillow==12.3.0 pyclipper==1.4.0 \
    scipy==1.18.1 skia-pathops==0.9.2 ufo2ft==3.9.0 ufoLib2==0.18.1 \
    uharfbuzz==0.56.2 unicodedata2==18.0.0

git clone https://github.com/googlefonts/atkinson-hyperlegible-next.git /tmp/ahn
git -C /tmp/ahn checkout 7925f50

cd build
export TEMOIN_BUILD=/tmp/build-temoin
export SOURCE_DATE_EPOCH=1790294400
mkdir -p "$TEMOIN_BUILD"
python3 make_temoin.py
python3 -m fontmake -g Temoin.glyphs -o variable \
    --output-path "$TEMOIN_BUILD/Temoin-wght.ttf" \
    --no-production-names --filter FlattenComponentsFilter
python3 -m fontmake -g Temoin-Italic.glyphs -o variable \
    --output-path "$TEMOIN_BUILD/Temoin-Italic-wght.ttf" \
    --no-production-names --filter FlattenComponentsFilter
python3 finaliser.py
python3 subset.py
```

`SOURCE_DATE_EPOCH` fixe la date de modification inscrite dans les binaires au
25 septembre 2026, 0 h UTC. Sans elle, chaque compilation inscrit l'heure
courante, et deux compilations identiques diffèrent de quelques octets.

`finaliser.py` écrit `Temoin[wght].ttf` et `Temoin-Italic[wght].ttf` dans
`$TEMOIN_BUILD`. `subset.py` en tire les deux WOFF2, réduit leur axe à 400-800,
les écrit dans `fonts/` et y copie les deux TTF.

Les deux drapeaux de `fontmake` sont portants. Sans `--no-production-names`,
61 glyphes sortent renommés. Sans `--filter FlattenComponentsFilter`,
36 composites restent imbriqués et Font Bakery refuse.

`make_temoin.py` **régénère intégralement** les deux fichiers `.glyphs` à partir
des sources d'Atkinson : une modification écrite à la main dedans disparaît au
premier passage. Le dessin vit dans les modules Python.

La chaîne lit le clone d'Atkinson Hyperlegible Next dans `/tmp/ahn`. **Ce
chemin est en dur dans quatorze modules.** Cloner ailleurs demande de les
modifier tous.

`make_temoin.py` lit aussi le WOFF2 de `fonts/`, dont il tire le périmètre de
la coupe de titrage. Il refuse de tourner sans lui plutôt que d'écrire des
sources incomplètes en silence.

## Vérifier

```
cd build
python3 check_final.py            # dix sections
python3 check_final.py --temoin   # treize mesures, aucune muette
python3 check_approches.py        # espacement et crénage
python3 check_crees.py            # les 47 glyphes créés
```

Avec `TEMOIN_BUILD` exporté comme ci-dessus. `check_final.py` lit les deux
binaires compilés et les deux WOFF2 de `fonts/`. Son mode `--temoin` casse une
chose à la fois dans une copie en mémoire et vérifie que la section
correspondante la voit : une section muette sous son propre faussage est une
cécité.

Tous les contrôles suivent la même convention de retour : **0 conforme,
1 signalé, 2 non mesuré**. Un contrôle qui ne trouve pas le clone d'Atkinson ou
le binaire qu'il lit rend 2 et le dit, puisqu'il n'a rien mesuré. Trois
contrôles ne lisent que les sources du projet et mesurent dans tous les cas :
`check_O.py`, `check_U.py` et `check_crenage_sc.py`. Deux affichent des
tableaux de shaping destinés à l'œil, `shape_check.py` et `shape_check3.py` :
ils rendent 0 dès qu'ils ont lu le binaire, et laissent le jugement au
lecteur.

Les contrôles qui lisent un binaire prennent par défaut les TTF sous-ensemblés
de `$TEMOIN_BUILD`, jumeaux des WOFF2, donc l'axe 400-800. Ils signalent en
note une graisse hors de cet axe, sans la mesurer. Pour mesurer les TTF de
`fonts/`, ExtraLight compris, passez leurs chemins en argument, romain puis
italique :

```
python3 check_contacts.py "../fonts/Temoin[wght].ttf" "../fonts/Temoin-Italic[wght].ttf"
python3 shape_check_kern.py "../fonts/Temoin[wght].ttf" "../fonts/Temoin-Italic[wght].ttf"
```

Critère extérieur, `fontbakery check-googlefonts` 1.1.0 sur les deux TTF, avec
`OFL.txt` à côté d'eux : 0 FAIL, 0 ERROR, 19 WARN, 13 INFO, 173 SKIP et
250 PASS. Sans accès au réseau, les 14 contrôles qui l'appellent passent en
ERROR.

## Licence

SIL Open Font License 1.1, texte complet dans `OFL.txt`. Les deux notices de
copyright, celle d'Atkinson et celle de l'OXA, y figurent et **doivent toutes
deux accompagner toute redistribution**, avec le texte de licence. C'est la
clause 2.

Le binaire porte ces mentions dans sa table `name` : copyright en ID 0,
reconnaissance de la base en ID 10, adresse de ce dépôt en ID 11, texte de
licence en ID 13, URL de la licence en ID 14.
