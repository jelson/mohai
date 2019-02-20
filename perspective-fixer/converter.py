#!/usr/bin/python

import sys
import xml.etree.ElementTree
import re
from PIL import Image
import subprocess

def pt_to_int(pt):
    return int(pt.split('.')[0])

def filter_red(inFilename, outFilename):
    pilImage = Image.open(inFilename)
    pixels = pilImage.load()
    for i in range(pilImage.size[0]):
        for j in range(pilImage.size[1]):
            v = pixels[(i,j)]
            if v[0] > 50 and v[0] > 2 * v[1] and v[0] > 2 * v[2]:
                pixels[(i, j)] = (0, 0, 0, 255)
            else:
                pixels[(i, j)] = (255, 255, 255, 255)
    pilImage.save(outFilename)

def trace(inFilename):
    subprocess.call(["potrace", inFilename, "-t", "50", "-s", "--tight"])

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

filter_red('../test.png', '../test.redonly.bmp')
trace("../test.redonly.bmp")
translate_svg('../test.redonly.svg')
