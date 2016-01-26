#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
Image.MAX_IMAGE_PIXELS = 1000000000
# Default fonts
fontSize = 10
defaultFont = "Helvetica"
# Autres
width = A3[1]
height = A3[0]



texts = {'titre': {'position': (width/2, height-10*mm), 'font-size': 16, 'font': defaultFont},
         'pagination': {'position': (width-15*mm, height-10*mm), 'font-size': 10, 'font': defaultFont},
         'date': {'position': (width-66*mm, 9.6*mm), 'font-size': 9, 'font': defaultFont},
         'shot-name': {'position': (width-15*mm, 3*mm), 'font-size': fontSize, 'font': "Helvetica-Bold"}
         }

metas_alias = {'action': 'action', 'a': 'action',
               'dialogue': 'dialogue',
               'd': 'orientation',
               'orientation': 'orientation', 'o': 'orientation',
               'echelle': 'echelle', 'e': 'echelle',
               }

metas = {'action': {'text-align': 'center', 'position': (47.5, 8), 'multiple-lines': True, 'ecart': 5, 'lines-up': False, 'font-size':fontSize, 'font': defaultFont},
         'dialogue': {'text-align': 'center', 'position': (47.5, -56), 'multiple-lines': True, 'ecart': 5, 'lines-up': True, 'font-size':fontSize, 'font': defaultFont},
         'orientation': {'text-align': 'left', 'position': (2, 8), 'multiple-lines': True, 'ecart': 5, 'lines-up': False, 'font-size':8, 'font': defaultFont},
         'echelle': {'text-align': 'right', 'position': (93, 8), 'multiple-lines': False, 'ecart': 0, 'lines-up': False, 'font-size':8, 'font': defaultFont},

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
    d = {'name': '-', 'cut': False, 'fullpage': False}
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
            p = int(t/12)
            r = 12-abs(p*12 - t)
            for i in range(0, r):
                thumbnails.append(newThumbnail())

        elif l.lower().startswith("page:") or l.lower().startswith("fond:"):
            # pleine page speciale
            # Boucler la page precedente s'il y a
            t = len(thumbnails)
            p = int(t/12)
            r = 12-abs(p*12 - t)
            if r != 12:
                for i in range(0, r):
                    thumbnails.append(newThumbnail())
            # Remplir la page actuelle

            for i in range(0, 12):
                thumbnails.append(newThumbnail())
            # indiquer sur la derniere case le caractere special
            thumbnails[-1]['name'] = l.split(":")[1]
            thumbnails[-1]['fullpage'] = True
        elif has_meta:
            v = ":".join(l.split(":")[1:])
            if metas[meta]['multiple-lines']:
                thumbnails[-1][meta].append(v)
            else:
                thumbnails[-1][meta] = v
        elif l.lower() == "cut":
            thumbnails[-1]['cut'] = True
        else:
            thumbnail = newThumbnail()
            thumbnail['name'] = l
            thumbnail['cut'] =  True if "/" in l else False
            thumbnails.append(thumbnail)



# Ouverture de la grille et creation du canvas de base
grid = Image.open(gridPath)
c = canvas.Canvas(outputPdf, pagesize=(width, height))


def newPage(c, pageNumber, pages, justtext=False):
    if not justtext:
        if pageNumber>1:
            c.showPage()
        c.drawInlineImage(grid, 0, 0, width=width, height=height)


    c.setFont(texts['titre']['font'], texts['titre']['font-size'])
    c.drawCentredString(texts['titre']['position'][0], texts['titre']['position'][1], title)
    c.setFont(texts['pagination']['font'], texts['pagination']['font-size'])
    c.drawRightString(texts['pagination']['position'][0], texts['pagination']['position'][1], "%i/%i" % (pageNumber, pages))
    c.setFont(texts['date']['font'], texts['date']['font-size'])
    c.drawRightString(texts['date']['position'][0], texts['date']['position'][1], "%02i/%02i/%i  %02i:%02i" % (today.day, today.month, today.year, today.hour, today.minute))


pages = int(len(thumbnails)/12)+1
page = 1
line = 0
position = 0
today = datetime.now()
c.setStrokeColorRGB(0, 0, 0)
c.setFillColorRGB(0, 0, 0)

newPage(c, 1, pages)


for k, t in enumerate(thumbnails):
    name = t['name']
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
        elif t['fullpage']:
            c.drawInlineImage(imgPath, 0, 0, width=width, height=height)
            newPage(c, page, pages, justtext=True)
        else:
            c.drawImage(imgPath, positions[position]*mm, height-lines[line]*mm, width=imgWidth*mm, height=imgHeigth*mm)
        
        if not t['fullpage']:
            c.setFont(texts['shot-name']['font'], texts['shot-name']['font-size'])
            c.drawString((positions[position]+2)*mm, height-(lines[line]-62)*mm, "%s" % texte)
            c.setFont(defaultFont, fontSize)
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
                c.setFont(metas[meta]['font'], metas[meta]['font-size'])
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
    if position == 0 and k > 0 and thumbnails[k-1]['cut']:
        c.rect((positions[position]-0.8)*mm, (height-(lines[line]+blackLineDown[line])*mm), 0.8*mm, blackLineUp[line]*mm, stroke=1, fill=1)
    position += 1

# Sauvegarde du fichier
c.save()
