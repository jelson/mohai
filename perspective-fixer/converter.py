#!/usr/bin/python

import sys
import re
import os
import glob
import subprocess
from PIL import Image, ExifTags
import xml.etree.ElementTree
import zbar
import shutil

TARGET_WIDTH_MM = 40.0
MM_PER_INCH = 25.4
TEMP_FILENAME = "/cygdrive/c/Users/jelson/home/mohai/tmp/curr-output.svg"


def rotate(pilImage):
    print("rotating")
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(pilImage._getexif().items())

        if exif[orientation] == 3:
            return pilImage.rotate(180, expand=True)
        elif exif[orientation] == 6:
            return pilImage.rotate(270, expand=True)
        elif exif[orientation] == 8:
            return image.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        return pilImage

    return pilImage

# returns (left, top, right, bot)
def detect(pilImage, baseDebugName):
    greyImage = pilImage.convert(mode="L")
    greyImage.save(baseDebugName + '-grey.jpg')
    #bwImage = greyImage.point(lambda x: 0 if x < 128 else 255, '1')
    #bwImage.save(baseDebugName + '-bw.png')
    width, height = pilImage.size
    rawImage = greyImage.tobytes()

    zimage = zbar.Image(width, height, 'GREY', rawImage)
    print("scanning")
    scanner = zbar.ImageScanner()
    results = scanner.scan(zimage)
    print("enumerating %s results" % results)

    left = None
    top = None
    right = None
    bot = None

    # coordinate system origin is at top-left; symbol locations are
    # 4-tuples of the x-y coordinates of the symbol, counter-clockwise
    # from top-left: [topleft, bottomleft, bottomright, topright]
    #
    # NOTE we intentionally over-write values here. In other words,
    # the top-left and top-right symbols both define the top. But
    # that's fine because it gives us more robustness to symbol
    # detection failures.
    for symbol in zimage:
        name = symbol.data.decode(u'utf-8')
        loc = symbol.location
        print("symbol: %s at %s" % (name, loc))

        if name == 'topleft':
            # We want the bottom-right corner of the top-left symbol
            left = loc[2][0]
            top = loc[2][1]
            print("left: %d, top: %d" % (left, top))

        elif name == 'bottomleft':
            # We want the top-right corner of the bottom-left symbol
            left = loc[3][0]
            bot = loc[3][1]
            print("left: %d, bot: %d" % (left, bot))

        elif name == 'bottomright':
            # We want the top-left corner of the bottom-right symbol
            right = loc[0][0]
            bot = loc[0][1]
            print("right: %d, bot: %d" % (right, bot))

        elif name == 'topright':
            # We want the bottom-left corner of the top-right symbol
            right = loc[1][0]
            top = loc[1][1]
            print("right: %d, top: %d" % (right, top))

        else:
            print("unrecognized symbol %s!" % (name))

    if left == None or right == None or top == None or bot == None:
        raise Exception("didn't find enough anchor points")

    return (left, top, right, bot)

def pt_to_int(pt):
    return int(pt.split('.')[0])

def filter_red(pilImage):
    print("filtering red pixels")
    pixels = pilImage.load()
    for i in range(pilImage.size[0]):
        for j in range(pilImage.size[1]):
            v = pixels[(i,j)]
            if v[0] > 50 and v[0] > 2 * v[1] and v[0] > 2 * v[2]:
                pixels[(i, j)] = (0, 0, 0, 255)
            else:
                pixels[(i, j)] = (255, 255, 255, 255)

def trace(inFilename, width_px):
    print("tracing")

    # -r argument says "one inch in the output correcponds to this
    # many pixels in the input". The diameter of the post-cropped
    # image should be 25mm.
    # x pixels / 25.4mm = cropped_width / 25mm
    res = (MM_PER_INCH / TARGET_WIDTH_MM) * width_px
    print("res: %f" % (res))
    subprocess.call(["potrace", inFilename, "-t", "50", "-s", "--tight",
                     "-r", "%.2f" % (res)])

def translate_svg(filename):
    svg = xml.etree.ElementTree.parse(filename)
    svgroot = svg.getroot()

    # First pull out the width and height of the svg
    width = pt_to_int(svgroot.attrib['width'])
    height = pt_to_int(svgroot.attrib['height'])
    sys.stdout.write("found width=%d, height=%d\n" % (width, height))

    # Now find the transform element
    g_element = svgroot.findall('{http://www.w3.org/2000/svg}g')[0]
    transform = g_element.attrib['transform']
    sys.stdout.write('curr transform: %s\n' % (transform))

    # Search through all transform directives looking for translate
    # sub-directive
    transform_parts = transform.split(' ')
    for i in range(len(transform_parts)):
        transform_part = transform_parts[i]

        if not 'translate' in transform_part:
            continue

        # Pull the numeric values out of the translate sub-directive
        m = re.search('(.*)translate\(([-\d\.]+),([-\d\.]+)\)(.*)',
                      transform_part)

        prefix = m.group(1)
        translate_x = float(m.group(2))
        translate_y = float(m.group(3))
        suffix = m.group(4)

        sys.stdout.write("curr translate: x=%d,y=%d\n" % (
            translate_x, translate_y))

        # Move the translation by half the width to the left and half
        # the height up
        translate_x = translate_x - (width / 2)
        translate_y = translate_y - (height / 2)

        sys.stdout.write("new translate: x=%d,y=%d\n" % (
            translate_x, translate_y))

        # Reassemble the translate sub-directive and put it back into
        # the transform chain
        transform_parts[i] = '%stranslate(%d,%d)%s' % (
            (prefix, translate_x, translate_y, suffix))

    # Rejoin all the parts of transform, including our modified
    # translation, and write it back to the svg
    transform = ' '.join(transform_parts)
    sys.stdout.write("new transform: %s\n" % (transform))
    g_element.attrib['transform'] = transform

    sys.stdout.write("writing: %s\n" % (filename))
    svg.write(filename)

def convert(inFilename):
    print("converting: %s" % (inFilename))
    baseDir, nameOnly = os.path.split(inFilename)
    debugDir = os.path.join(baseDir, "debug")
    if not os.path.exists(debugDir):
        os.mkdir(debugDir)
    baseDebugName = os.path.join(debugDir, os.path.splitext(nameOnly)[0])

    pilImage = Image.open(inFilename)
    pilImage = rotate(pilImage)
    pilImage.save(baseDebugName + "-rotated.jpg")

    corners = detect(pilImage, baseDebugName)
    pilImage = pilImage.crop(corners)
    pilImage.save(baseDebugName + "-cropped.jpg")

    filter_red(pilImage)
    bmpFilename = baseDebugName + ".bmp"
    pilImage.save(bmpFilename)

    width_px = corners[2] - corners[0]
    trace(bmpFilename, width_px)
    svgFilename = baseDebugName + ".svg"
    #translate_svg(svgFilename)

    shutil.copyfile(svgFilename, TEMP_FILENAME)

def main(argv):
    if len(argv) != 2:
        print("usage: %s <dir-name>" % (argv[0]))
        sys.exit(1)

    dirName = sys.argv[1]
    if not os.path.isdir(dirName):
        print("%s is not a directory" % (argv[1]))
        sys.exit(1)

    jpgList = glob.glob(os.path.join(dirName, "*.jpg"))
    latestFile = max(jpgList, key=os.path.getmtime)
    print("latest file: %s" % (latestFile))

    convert(latestFile)
        
main(sys.argv)
