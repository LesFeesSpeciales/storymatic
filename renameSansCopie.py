import sys
import os

filePath = sys.argv[1]

if " copie." in filePath:

    newPath = filePath.replace(" copie.", ".")
    print filePath, newPath
    if os.path.exists(filePath):
        os.rename(filePath, newPath)
    else:
        print "file does not exists"