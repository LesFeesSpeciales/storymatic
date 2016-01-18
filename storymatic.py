
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3
from reportlab.lib.units import mm
from datetime import datetime

import sys



# Coordonnes des lignes et positions en bas a gauche en mm
lines = [82.8, 171.5, 261.9]
positions = [20.9, 116.9, 213.0, 309.0]
# Taille des images en mm
imgWidth = 94.85
imgHeigth = 53.36
fontSize = 10
width = A3[1]
height = A3[0]
Image.MAX_IMAGE_PIXELS = 1000000000

gridPath = "/u/storymatic/grille.jpg"



folder = os.path.dirname(sys.argv[1]) + "/"
summary = sys.argv[1]

if not summary.endswith(".txt"):
    raise ValueError("Not a txt file")

outputPdf = summary.replace(".txt", ".pdf")



thumbnails = []
title = None

# Reading script file
f = open(summary, "r")
for l in f.readlines():
    l = l.replace("\n", "").replace("\r", "")
    print(l)
    if not title:
        title = l
        continue
    if l:
        if l == "." or l == "SAUT DE PAGE":
            t = len(thumbnails)
            p = int(len(thumbnails)/12)
            r = 12-abs(p*12 -t)
            for i in range(0,r):
                thumbnails.append({'name': '-', 'dialogue': [], 'action': []})
        elif l.startswith('dialogue:'):
            thumbnails[-1]['dialogue'].append(":".join(l.split(":")[1:]))
        elif l.startswith('action:'):
            thumbnails[-1]['action'].append(":".join(l.split(":")[1:]))
        else:
            thumbnails.append({'name': l, 'dialogue': [], 'action': []})



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
    dialogue = t['dialogue']
    action = t['action']
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
            texte = name.split("-")[1]
        else:
            texte = name.split(':')[-1].replace('/', '')
        print(page, line, position, img)
        imgPath = folder + img + '.jpg'
        if not os.path.exists(imgPath):
            c.drawString((positions[position]+10)*mm, height-(lines[line]-imgHeigth/2)*mm, "Fichier introuvable : %s.jpg" % img)
        else:
            c.drawImage(imgPath, positions[position]*mm, height-lines[line]*mm, width=imgWidth*mm, height=imgHeigth*mm)
            c.setFont("Helvetica-Bold", fontSize)
            c.drawString((positions[position]+2)*mm, height-(lines[line]-62)*mm, "%s" % texte)
            c.setFont("Helvetica", fontSize)
        if dialogue:
            dialogue.reverse()
            print("DIALOGUE: ", dialogue)
            dialogueLine = 0
            for d in dialogue:
                c.drawCentredString((positions[position]+47.5)*mm, height-(lines[line]-56-dialogueLine*5)*mm, "%s" % d)
                dialogueLine += 1
        if action:
            print("ACTION: ", action)
            actionLine = 0
            for a in action:
                c.drawCentredString((positions[position]+47.5)*mm, height-(lines[line]+8+actionLine*5)*mm, "%s" % a)
                actionLine += 1
    if "/" in name:
        # Marquage noir
        c.rect((positions[position]+imgWidth)*mm, (height-(lines[line]+5)*mm), 0.8*mm, (imgHeigth+10)*mm, stroke=1, fill=1)

    position += 1

# Sauvegarde du fichier
c.save()
