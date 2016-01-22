
import os

import sys
sys.path.append("/u/libs")  # Macs sans xcode -> JE SAIS !

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from datetime import datetime

#  Coordonnes des lignes et positions en bas a gauche en mm
lines = [82.8, 171.5, 261.9]
positions = [20.9, 116.9, 213.0, 309.0]
blackLineDown = [16, 18, 25]
blackLineUp = [80, 81, 89]
# Taille des images en mm
imgWidth = 94.85
imgHeigth = 53.36
fontSize = 10
width = A3[1]
height = A3[0]
Image.MAX_IMAGE_PIXELS = 1000000000


metas_alias = {'action': 'action', 'a': 'action',
               'dialogue': 'dialogue', 'd': 'dialogue',
               'orientation': 'orientation', 'o': 'orientation',
               'echelle': 'echelle', 'e': 'echelle',
               }

metas = {'action': {'text-align': 'center', 'position': (47.5, 8), 'multiple-lines': True, 'ecart': 5, 'lines-up': False},
         'dialogue': {'text-align': 'center', 'position': (47.5, -56), 'multiple-lines': True, 'ecart': 5, 'lines-up': True},
         'orientation': {'text-align': 'left', 'position': (2, 8), 'multiple-lines': False, 'ecart': 0, 'lines-up': False},
         'echelle': {'text-align': 'right', 'position': (93, 8), 'multiple-lines': False, 'ecart': 0, 'lines-up': False},

         }

gridPath = "/u/storymatic/grille.jpg"

folder = os.path.dirname(sys.argv[1]) + "/"  # Pas clean...
summary = sys.argv[1]

if not summary.endswith(".txt"):
    raise ValueError("Not a txt file")

outputPdf = summary.replace(".txt", ".pdf")


thumbnails = []
title = None


def newThumbnail():
    d = {'name': '-', 'cut': False}
    for m in metas:
        d[m] = [] if metas[m]['multiple-lines'] else None
    return d

# Reading script file
f = open(summary, "r")
for l in f.readlines():
    l = l.replace("\n", "").replace("\r", "")
    print(l)
    if not title:
        title = l
        continue
    if l:
        has_meta = False
        meta = None
        if ":" in l:
            for m in metas_alias:
                if l.lower().replace(" ", "").startswith("%s:" % m):
                    has_meta = True
                    meta = metas_alias[m]
        if l == "." or l == "SAUT DE PAGE":
            t = len(thumbnails)
            p = int(len(thumbnails)/12)
            r = 12-abs(p*12 - t)
            for i in range(0, r):
                thumbnails.append(newThumbnail())
        # elif l.startswith('dialogue:'):
        #     action = ":".join(l.split(":")[1:])
        #     if action:
        #         thumbnails[-1]['dialogue'].append(action)
        # elif l.startswith('action:'):
        #     dialogue = ":".join(l.split(":")[1:])
        #     if dialogue:
        #         thumbnails[-1]['action'].append(dialogue)
        elif has_meta:
            v = ":".join(l.split(":")[1:])
            if metas[meta]['multiple-lines']:
                thumbnails[-1][meta].append(v)
            else:
                thumbnails[-1][meta] = v
        elif l.startswith('CUT'):
            thumbnails[-1]['cut'] = True
        else:
            thumbnail = newThumbnail()
            thumbnail['name'] = l
            thumbnail['cut'] =  True if "/" in l else False
            thumbnails.append(thumbnail)



# Ouverture de la grille et creation du canvas de base
grid = Image.open(gridPath)
c = canvas.Canvas(outputPdf, pagesize=(width, height))


def newPage(c, pageNumber, pages):
    if pageNumber>1:
        c.showPage()
    c.drawInlineImage(grid, 0, 0, width=width, height=height)
    c.drawString(70*mm, height-10*mm, title)
    c.drawRightString(width-15*mm, height-10*mm, "Page %i/%i" % (pageNumber, pages))
    c.drawRightString(width-15*mm, 3*mm, "%02i/%02i/%i  %02i:%02i" % (today.day, today.month, today.year, today.hour, today.minute))


pages = int(len(thumbnails)/12)+1
page = 1
line = 0
position = 0
today = datetime.now()
c.setStrokeColorRGB(0, 0, 0)
c.setFillColorRGB(0, 0, 0)

newPage(c, 1, pages)


for t in thumbnails:
    name = t['name']
    #dialogue = t['dialogue']
    #action = t['action']
    cut = t['cut']
    # Calcul des positions/lignes et pages
    if line == 2 and position == 4:
        # Fin de la 4e position de la 3e ligne : nouvelle page
        page += 1
        position = 0
        line = 0
        newPage(c, page, pages)
    elif position == 4:
        line += 1
        position = 0

    if name in ["-", "-/", "CASE VIDE", "CASE VIDE/"]:
        # Case blanche je ne fais rien
        print(page, line, position, "BLANC")
    else:
        # Image
        img = name.split(':')[0].replace('/', '')

        if not ":" in name and "-" in name:
            texte = name.split("-")[1].replace('/', '')
        else:
            texte = name.split(':')[-1]
        print(page, line, position, img)
        imgPath = folder + img + '.jpg'
        if not os.path.exists(imgPath):
            c.drawString((positions[position]+10)*mm, height-(lines[line]-imgHeigth/2)*mm, "Fichier introuvable : %s.jpg" % img)
        else:
            c.drawImage(imgPath, positions[position]*mm, height-lines[line]*mm, width=imgWidth*mm, height=imgHeigth*mm)
        c.setFont("Helvetica-Bold", fontSize)
        c.drawString((positions[position]+2)*mm, height-(lines[line]-62)*mm, "%s" % texte)
        c.setFont("Helvetica", fontSize)
    # if dialogue:
    #     dialogue.reverse()
    #     print("DIALOGUE: ", dialogue)
    #     dialogueLine = 0
    #     for d in dialogue:
    #         c.drawCentredString((positions[position]+47.5)*mm, height-(lines[line]-56-dialogueLine*5)*mm, "%s" % d)
    #         dialogueLine += 1
    # if action:
    #     print("ACTION: ", action)
    #     actionLine = 0
    #     for a in action:
    #         c.drawCentredString((positions[position]+47.5)*mm, height-(lines[line]+8+actionLine*5)*mm, "%s" % a)
    #         actionLine += 1
    for meta in metas:
        if t[meta]:
            l = 0
            if metas[meta]['lines-up']:
                t[meta].reverse()
            for i in range(0, 1 if not metas[meta]["multiple-lines"] else len(t[meta])):
                positionX = (positions[position]+metas[meta]['position'][0])*mm
                ecart = l*metas[meta]['ecart']
                if metas[meta]['lines-up']:
                    ecart = 0-ecart
                positionY = height-(lines[line]+metas[meta]['position'][1]+ecart)*mm

                value = t[meta][l] if metas[meta]["multiple-lines"] else t[meta]
                if metas[meta]['text-align'] == "right":
                    c.drawRightString(positionX, positionY, "%s" % value)
                elif metas[meta]['text-align'] == "center":
                    c.drawCentredString(positionX, positionY, "%s" % value)
                else:
                    c.drawString(positionX, positionY, "%s" % value)

                l += 1

    if cut:  # "/" in name:
        # Marquage noir
        c.rect((positions[position]+imgWidth)*mm, (height-(lines[line]+blackLineDown[line])*mm), 0.8*mm, blackLineUp[line]*mm, stroke=1, fill=1)
        #c.rect((positions[position]+imgWidth)*mm, (height-(lines[line]+16)*mm), 0.8*mm, (imgHeigth+10)*mm, stroke=1, fill=1)

    position += 1

# Sauvegarde du fichier
c.save()
