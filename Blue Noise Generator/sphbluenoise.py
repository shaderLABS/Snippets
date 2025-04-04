import taichi as ti
from taichi import math as tm
import numpy as np
from sys import argv
from PIL import Image

radius = 2.2
itercount = 100
show = 10
fname = None
for i in range(len(argv) - 1, -1, -1):
    equalssplit = argv[i].split("=")
    if equalssplit[0] in ("-r", "--radius"):
        radius = float(argv[i].split("=")[1])
        argv.pop(i)
    elif equalssplit[0] in ("-i", "--iterations"):
        itercount = int(argv[i].split("=")[1])
        argv.pop(i)
    elif equalssplit[0] in ("-s", "--show"):
        show = int(equalssplit[1])
        argv.pop(i)
    elif equalssplit[0] in ("-o", "--output"):
        fname = "=".join(equalssplit[1:]).strip()
        argv.pop(i)
    elif argv[i] in ("-h", "-?", "-help", "--help"):
        print("""
Generate blue noise distributed points on a sphere surface using relaxation

Usage:
$ python sphbluenoise.py [options] [size [y-axis size]]
Generates a blue noise texture with dimensions size x y-axis size.
If y-axis size is unset, it is assumed equal to size.
The default size is 64.

Options:
-r=RADIUS, --radius=RADIUS   Blur radius to use.
    This should be the same radius that is used
    to filter data dithered with the blue noise texture
    later, if it is filtered using a gaussian blur.
    Default value is 2.2 pixels.

-o=OUTPUT, --output=OUTPUT   Output the texture into the file OUTPUT
    Default value is "vectorbluenoise_<RADIUS>px_<size>x<y axis size>.png"

-i=ITER, --iter=ITER         amount of relaxation iterations to perform.
    Default value is 1000.

-s=FRAMES, --show=FRAMES     Show progress every FRAMES iterations steps
    Default value is 10. Negative values suppress the GUI

-h, -?, -help, --help        display this help message and exit
""")
        exit()
    

try:
    noiseshape = (int(argv[1]), int(argv[2]))
except IndexError:
    try:
        noiseshape = (int(argv[1]), int(argv[1]))
    except IndexError:
        noiseshape = (64, 64)

if fname is None:
    fname = f"vectorbluenoise_{radius}_{noiseshape[0]}x{noiseshape[1]}.png"

ti.init(arch=ti.opengl)

vectornoise = ti.field(tm.vec3, shape=noiseshape)

blur_range = int(6 * radius + 1)

@ti.kernel
def init():
    for i, j in vectornoise:
        vectornoise[i, j] = tm.vec3(ti.random(), ti.random(), ti.random()) * 2.0 - 1.0

@ti.func
def get_diff(x, y):
    d = x - y
    return d
    
@ti.func
def clamp_to_manifold(vector):
    return tm.normalize(vector)

@ti.kernel
def iteration(stepsize : float):
    for i, j in vectornoise:
        oldval = vectornoise[i, j]
        force = 0.0 * oldval
        for k, l in ti.ndrange(blur_range, blur_range):
            dx = k - blur_range//2
            dy = l - blur_range//2
            if dx != 0 or dy != 0:
                weight = ti.exp(-(dx*dx+dy*dy)/(2*radius*radius))
                diff = get_diff(oldval, vectornoise[(i+dx)%noiseshape[0], (j+dy)%noiseshape[1]])
                difflen = tm.length(diff)
                force += weight / (difflen * difflen + 1e-10) * diff
        ti.sync()
        if tm.length(force) > 0.0:
            vectornoise[i, j] += tm.normalize(force) * (0.5 + ti.random()) * stepsize
            vectornoise[i, j] = clamp_to_manifold(vectornoise[i, j])

display_field = ti.Vector.field(3, dtype=float, shape=(512, 512))
@ti.kernel
def set_displayfield():
    for i, j in display_field:
        xcoord = i * vectornoise.shape[0] // display_field.shape[0]
        ycoord = j * vectornoise.shape[1] // display_field.shape[1]
        display_field[i, j] = tm.vec3(vectornoise[xcoord, ycoord]) * 0.5 + 0.5

init()
if show > 0:
    gui = ti.GUI("bluenoise", res=display_field.shape, fast_gui=True)
for k in range(itercount):
    iteration(1.0 / (k+10))
    if show > 0 and k % show == 0:
        set_displayfield()
        gui.set_image(display_field)
        gui.show()
Image.fromarray(((vectornoise.to_numpy() * 0.5 + 0.5) * 255.99).astype(np.uint8)).save(fname)
