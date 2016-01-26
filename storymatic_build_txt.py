#!/usr/bin/env python
# coding: utf-8

import os
import glob
import sys
import re

folder = os.path.dirname(sys.argv[1]) + "/"

listImages = glob.glob(folder + "*.jpg")
listImages.sort()

images = []
shots = {}

for i in listImages:
    img = os.path.basename(i).replace('.jpg', '')
    r = re.match(r'.*\-P(\d+).*', img)
    if r:
        shot = r.group(1)
        if shot not in shots:
            shots[shot] = []
        shots[shot].append(img)
        shots[shot].sort()
        images.append((img, shot))
        
    else:
        print("Image mal nommee ? %s" % img)
    

output = u"SEQUENCE"

for i in images:
    if len(shots[i[1]]) > 1:  # si shot multiplce vignettes
        if i[0] == shots[i[1]][0]:  # si image premiere vignette
            output += "\n\n%s:P%s" % (i[0], i[1])
        elif i[0] == shots[i[1]][-1]:  # si derniere vignette du shot
            output += "\n%s/:" % (i[0])
        else:
            output += "\n%s:" % (i[0])
    else:
        output += "\n\n%s/" % (i[0])
    output += "\ndialogue:\naction:\norientation:\nechelle:"

f = open(folder + "prepa.txt", 'w')
f.write(output)
f.close()