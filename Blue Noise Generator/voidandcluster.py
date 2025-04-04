import taichi as ti
import numpy as np
from sys import argv
from PIL import Image

# read command-line arguments
radius = 2.2
show = 100
fname = None
for i in range(len(argv) - 1, -1, -1):
    equalssplit = argv[i].split("=")
    if equalssplit[0] in ("-r", "--radius"):
        radius = float(equalssplit[1])
        argv.pop(i)
    elif equalssplit[0] in ("-s", "--show"):
        show = int(equalssplit[1])
        argv.pop(i)
    elif equalssplit[0] in ("-o", "--output"):
        fname="=".join(equalssplit[1:]).strip()
        argv.pop(i)
    elif argv[i] in ("-h", "--help", "-?", "-help"):
        print("""
Blue noise generator using the Void and Cluster algorithm

Usage:
$ python voidandcluster.py [options] [size [y-axis size]]
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
    Default value is "bluenoise_<RADIUS>px_<size>x<y axis size>.png"

-s=FRAMES, --show=FRAMES     Show progress every FRAMES iterations steps
    Default value is 100. Negative values suppress the GUI

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
    fname = f"bluenoise_{radius:4.4g}_{noiseshape[0]}x{noiseshape[1]}.png".replace(" ", "")

ti.init(arch=ti.opengl)
tm = ti.math

blurredorder = ti.field(float, shape=noiseshape)
order = ti.field(int, shape=noiseshape)

@ti.kernel
def clear_fields():
    for i, j in blurredorder:
        blurredorder[i, j] = noiseshape[0] + noiseshape[1] + 3.0
        order[i, j] = -1

@ti.kernel
def blur(center : tm.vec2):
    lowerbound = center - 3.5 * radius - 0.5 + tm.vec2(noiseshape)
    upperbound = center + 3.5 * radius + 0.5 + tm.vec2(noiseshape)
    offset_x = int(lowerbound.x)
    offset_y = int(lowerbound.y)
    range_x = int(upperbound.x) + 1 - offset_x
    range_y = int(upperbound.y) + 1 - offset_y
    for i, j in ti.ndrange(range_x, range_y):
        totalweight = 0.0
        val = 0.0
        for k, l in ti.ndrange(int(6 * radius + 1), int(6 * radius + 1)):
            dx = k - int(3 * radius + 1)
            dy = l - int(3 * radius + 1)
            x = (i + offset_x + dx + noiseshape[0]) % noiseshape[0]
            y = (j + offset_y + dy + noiseshape[1]) % noiseshape[1]
            thisweight = tm.exp(- (dx*dx+dy*dy)/(2 * radius * radius))
            totalweight += thisweight
            if order[x, y] != -1:
                val += thisweight
        blurredorder[(i + offset_x) % noiseshape[0], (j + offset_y) % noiseshape[1]] = val / totalweight + 1e-4 * ti.random()

@ti.kernel
def getminval() -> float:
    minval = 1e10
    for i, j in blurredorder:
        if order[i, j] == -1:
            ti.atomic_min(minval, blurredorder[i, j])
    return minval

@ti.kernel
def argval(val : float) -> tm.vec2:
    barrier = 0
    arg = tm.vec2(0)
    # if there are multiple pixels with value val,
    # don't always find the same ones because of thread execution order
    ioffset = int(ti.random() * noiseshape[0])
    joffset = int(ti.random() * noiseshape[1])
    for i0, j0 in blurredorder:
        i = (i0 + ioffset)%noiseshape[0]
        j = (j0 + joffset)%noiseshape[1]
        if blurredorder[i, j] == val and order[i, j] == -1:
            if ti.atomic_or(barrier, 1) == 0:
                arg = tm.vec2(i, j)
    return arg


display_field_shape = (
    (500//noiseshape[0]+1)*noiseshape[0],
    (500//noiseshape[0]+1)*noiseshape[1]
)
display_field = ti.Vector.field(3, dtype=float, shape=display_field_shape)
@ti.kernel
def set_displayfield(n_points : int):
    for i, j in display_field:
        xcoord = i * noiseshape[0] // display_field.shape[0]
        ycoord = j * noiseshape[1] // display_field.shape[1]
        display_field[i, j] = tm.vec3(order[xcoord, ycoord]) / n_points

clear_fields()
if show > 0:
    gui = ti.GUI("bluenoise", res=display_field.shape, fast_gui=True)
for pointcount in range(noiseshape[0] * noiseshape[1]):
    minval = getminval()
    minvalpoint = argval(minval)
    if show > 0 and pointcount%show == 0:
        set_displayfield(pointcount)
        gui.set_image(display_field)
        gui.show()

    order[
        int(minvalpoint.x + 0.5),
        int(minvalpoint.y + 0.5)
    ] = pointcount

    blur(minvalpoint)

    print(f"added point at {minvalpoint} with blurred value {minval:.4g}, {100*pointcount/(noiseshape[0] * noiseshape[1])}% done              ", end="\r")
print()
if show > 0:
    set_displayfield(pointcount)
    gui.set_image(display_field)
    gui.show()
numpy_order_normalized = order.to_numpy()/pointcount
im = Image.fromarray((np.reshape(numpy_order_normalized*256.0, (*order.shape, 1)) * np.array([1, 1, 1])).astype(np.uint8))
im.save(fname)
