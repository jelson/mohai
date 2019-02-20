#!/usr/bin/python

# sudo apt install python-zbar
#https://stackoverflow.com/questions/50436423/how-to-get-the-x-y-position-of-a-detected-qr-code-on-an-image-with-zbar

import zbar
import io
from PIL import Image

class Fixer:
    def __init__(self, filename):
        print("Load image")
        pilImage = Image.open(filename)
        greyImage = pilImage.convert(mode="L")
        greyImage.save('grey.jpg')
        width, height = pilImage.size
        rawImage = greyImage.tobytes()

        zimage = zbar.Image(width, height, 'GREY', rawImage)
        print("scanning")
        scanner = zbar.ImageScanner()
        results = scanner.scan(zimage)
        print("enumerating %s results" % results)
        for symbol in zimage:
            print("symbol: %s at %s" % (symbol.data.decode(u'utf-8'), symbol.location))

Fixer("../example1.jpg")
