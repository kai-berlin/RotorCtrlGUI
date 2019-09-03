#!/usr/bin/python3

import os


#location = "JO63PA"

# Mitte: 105,0005     148,4995 
# Größe: 191x191mm

# Middle of map on A4 page from top in mm
mx = 105.0
my = 148.5

# size of rect
sizemm = 191.0

# desired size in Pixel
sizePixel = 460

# scale factor (in process) for better quality
scale = 4

def GenMap(location):
    # Get map pdf
    cmd = 'wget --post-data "title=Location: '+location+'&location='+ location +'&paper=A4&bluefill=on&iplocationused=false" https://ns6t.net/azimuth/code/azimuth.fcgi -O map.pdf'

    print("Running: "+cmd)

    os.system(cmd)

    dpi = float(scale) * sizePixel / sizemm * 25.4

    #print(f"DPI of picture: {dpi/scale:.1f}")

    cornerX = round( (mx - sizemm/2) / 25.4 * dpi )
    cornerY = round( (my - sizemm/2) / 25.4 * dpi )

    sizeScale = sizePixel * scale
    resizeP = 1.0 / scale * 100
    cmd = f"convert -density {dpi} -depth 8 map.pdf -crop {sizeScale}x{sizeScale}+{cornerX}+{cornerY} +repage -resize {resizeP:.1f}% maps/Map_{location}.png"

    print("Running: " + cmd)

    os.system(cmd)

