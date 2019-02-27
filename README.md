
# MOHAI Maker Days: Making the Mold

The [MOHAI](https://mohai.org/), a museum in Seattle's South Lake Union has, a
monthly event called [Maker Days](https://mohai.org/program/maker-days/) where a
local maker comes and gives a free, hands-on, all-ages-appropriate introduction
to an interesting maker skill or craft. In [February of
2019](https://mohai.org/event/maker-day-making-the-mold/), that maker was me!

I ran a booth demonstrating 3D printing, mold-making, and casting, and
how all those elements can be brought together to convert anything you
draw on paper into an plastic medallion with the drawn design embossed
on the front. You can take home the medallion in minutes, and the mold
too if you'd like to make more copies of it.

This repository contains all the software and other files that went
into making the event, in case you'd like to reproduce it.

[Here are some photos](https://photos.app.goo.gl/AzxZ8Njd79hLUo9N7) of
the process and the event.

The idea is this: first someone drew a design on a sheet of paper. We
scanned the paper and turned the design into a 3D model -- a
40mm-diameter circular medallion with your design embossed on
top. Next, I printed the medallion face on a 3D printer. To save time,
we'd pre-printed the body of the medallion before the event. At the
event, we just printed the top layer with the embossed design on it
and snapped it into the pre-printed body.

Next, we helped participants measure out the proper amounts of a
fast-curing silicone compound and pour it over the 3D-printed
medallion. Ten minutes later, the silicone will cured into a
negative of the medallion -- a mold.

The last step was to mix together a two-part resin formula. We had a
dozen different colorants on hand to make the medallion any color!
Pour the liquid resin into your silicone mold, wait a couple of
minutes, and you've got yourself a solid medallion ready to attach to
a lanyard, also available at the booth.

## Detailed Process

We set up four stations at the event: drawing, printing, molding and casting.

The process below was optimized for throughput. If you'd like to
reproduce it for a one-off, it's probably not necessary to use most of
the software I wrote.

### Drawing

* Before the event I first generated 4 QR codes using the Linux
  'qrencode' program.

* In Inkscape, I produced an instruction sheet with a circle to draw
  in, four QR codes in the corners and instructions to only draw in
  red ink.


### Printing

* Take a photo of the completed sheet with a phone, wait for it to pop
  up in the Google Photos web interface (hit reload), and hit shift-d
  to download the photo to local disk.

* Run my Python script that looks for the most-recently-written file in
  the Chrome downloads folder, rotates it according to EXIF data,
  detects the QR codes, crops, filters out everything but red pixels,
  scales the image to the medallion size (using the QR code distance
  data), and feeds it to the 'potrace' program that produces an SVG
  out of a raster image.

* In [FreeCAD](https://www.freecadweb.org), run my macro that opens a
  template medallion face, imports the SVG, extrudes it, and fuses it
  with the base. After adjusting the position manually if necessary,
  export the fused object to STL.

* Slice the STL, drag it to OctoPrint and print. (I hvae a Prusa i3 Mk3.)

The process took a minute or two; the bottleneck was the printer.

### Molding

* Snap the printed medallion face onto one of the reusable preprinted
bases which has the body of the medallion and a built-in mold box.

* Spray mold release lightly.

* Measure out 30g of Part A and 30g of Part B of [Smooth-On Body
Double
Fast](https://www.smooth-on.com/products/body-double-fast-set/). The
[cartridge
applicator](https://www.reynoldsam.com/product/dispensing-guns/) is
much faster and more convenient (5 squirts) than measuring it manually
out of the bottles using a scale. Don't use the mixing nozzle with the
cartridge because its large volume leads to a lot of wasted silicone;
just dispense into a cup and stir with a popsicle stick.

* Mix! Mix quickly because you only have 30 seconds of pot life on
  this stuff!

* Pour into the mold.

* Wait 10 minutes or so for it to cure

### Casting

* Measure out 10g of Part A and 9g of Part B of [Smooth-On Smooth Cast
  300Q](https://www.smooth-on.com/products/smooth-cast-300q/) using
  eyedroppers

* Color as desired using tiny drops of [Smooth-On
  So-Strong](https://www.smooth-on.com/product-line/strong/)

* Combine the two halves of the resin compound and stir quickly

* Pour into mold

* Wait a few minutes for it to cure, remove, and put on a
  [lanyard](https://www.amazon.com/gp/product/B018JW4IBC/ref=oh_aui_search_asin_title?ie=UTF8&psc=1)
  in your choice of color!

