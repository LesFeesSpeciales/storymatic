# STORYMATIC

Storymatic.py est un script python qui genere des pdf. Il est propre au projet Dilili.


# INSTALLATION

Ce script a besoin de Pillow

    pip install Pillow 


et de REPORTLAB

    pip install reportlab

On peut utiliser le script via un shell :

    python storymatic.py S01.txt

On en faisant un processus automatique pour drag and drop (voir AUTOMATOR)

# UTILISATION

Ce script prend en entree un fichier texte qui liste des vignettes qui se trouvent
dans le meme dossier. Il sortira un fichier pdf, a coté du fichier texte, et du
meme nom que le fichier texte.

Exemple : 
S01.txt deviendra S01.pdf

La premiere ligne du fichier texte est le nom de la sequence

Les lignes suivantes peuvent contenir :
- un nom d'image (sans le .jpg)
- une ligne de dialogue
- une ligne d'action
- rien (ne sera pas pris en compte)
- un tiret ("-") qui indique une case blanche
    ou alors "CASE VIDE"
- un point (".") qui indique un saut de page (les cases restantes de la page seront blanches)
    ou alors "SAUT DE PAGE"

## Les vignettes et leur titre

dans le cas d'un nom d'image ou d'un tiret la ligne peut se terminer par un slash
ex :

    S01-P010/
le slash ("/") indiquera qu'il faut marquer en noir une ligne de separation
representant un cut.

le nom de l'image est utilise par defaut au dessus de la case qui la represente
neanmoins on peut changer le nom et texte en placant ce que l'on veut apres deux points (":")
ex :

    S01-P010:Plan 10
n'indiquera pas S01_P010 mais "Plan 10"
On peut le cumuler avec le slash bien sur : S01_P010/:Plan 10
On peut aussi mettre deux points et rien derriere pour ne rien afficher au dessus de la vignette :
ex : 

    S01-P010:

n'indiquera rien au dessus de la vignette

## Les Dialogues

Les indication de dialogue s'afficheront centrées au dessus de la vignette concernée 

apres avoir mis une vignette (ou au moins une case blanche avec le "-"), on peut mettre
une ou plusieurs ligne de dialogue, tout simplement en ecrivant dialogue: suivi de la ligne
a afficher :

Par exemple, pour une ligne de dialogue de la vignette S01_P10 on aurait :

    S01-P10
    dialogue:une ligne de dialogue du P10

Pour avoir plusieurs lignes, on met autant de dialogue: que necessaire, par exemple :

    S01-P10
    dialogue:la premiere ligne de dialogue
    dialogue:la seconde ligne de dialogue
    dialogue:et une 3eme ligne si besoin


Raccourci possible : d

    S01-P10
    dialogue:Un dialogue habituel
    d:Ceci est aussi un dialogue, mais mot cle raccourci

## Les actions

Les actions s'affichent centrées sous la vignette concernée.
La declaration d'une action fonctionne comme pour les dialogues, avec "action:"

Exemple sur 1 ligne :

    S01-P10
    action:Une ligne d'action

Et un exemple pour plusieures lignes :

    S01_P10/
    action:Premiere ligne d'action
    action:Seconde ligne d'action

Raccourci possible : a

## Autres metadonnees

### orientation

Sera placé en bas a gauche de la case

    S01-P10
    orientation:Sud

Raccourci possible : o

### echelle

Sera placé en bas a droite de la case

    S01-P10
    echelle:105%

Raccourci possible : e

## Combiner

on peut maintenant tout combiner :

    S01-P10/:Plan 10
    action:Une ligne d'action
    dialogue:Une premiere ligne de dialogue
    dialogue:Une autre ligne de dialogue

## PLeine page

Dans des cas de planches complexes on peut avoir utilisé la grille habituelle
pour créer une pleine page que l'on veut intégrer dans le story board.
Pour éviter des manipulations de pdf a postériori et des numéros de pages 
décallés, on peut créer la planche spéciale et la mettre avec les autres images.
En utilisant la balise "page:" devant le nom de l'image, le script utilisera
cette image en pleine page, dans une nouvelle planche.

Exemple : 

    S01-P10/:Plan 10
    action:Une ligne d'action

    page:S01-P11

On aura une page avec une simple vignette S01-P10
puis dans une autre page, l'image S01-P11 en pleine page

# Fabriquer un AUTOMATOR (Pour mac)

Pour profiter d'un drag and drop sur un .app automator :

Ouvrir automator
Créer une "Application"

Comme premiere action ajouter un : Get Selected Finder Items

Et comme seconde action un : Run Shell Script
Et y copier (pour python3) :

    for f in "$@"
    do
        /Library/Frameworks/Python.framework/Versions/3.4/bin/python3 /chemin/vers/storymatic.py "$f"
    done

en mettant a jour le chemin vers storymatic.py bien entendu (et la bonne version de python le cas échéant)

# Script d'update si pas de git

Pour Ghis

    cd $TMPDIR
    curl -LOk https://github.com/LesFeesSpeciales/storymatic/archive/master.zip
    unzip master.zip
    mv ./storymatic-master/* /u/storymatic/
