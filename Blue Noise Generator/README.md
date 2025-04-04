# Blue Noise Generator

> by gri573

To be used for generating blue noise distributed sampling points on manifolds as well as blue noise on the [0, 1] interval for dithering

## Dependencies

The scripts are written in Python and use `numpy`, `Pillow` and `taichi`.

## Contents

`voidandcluster.py` implements a simplified version of the Void and Cluster algorithm [1]. This yields high quality blue noise for locally uniform distributions after thresholding with arbitrary thresholds.

`sphbluenoise.py` uses a relaxation method to produce blue noise distributed points on higher dimensional objects, such as (by default) the surface of a sphere.

## Usage

launch either script with python, pass -h or --help for instructions.

## Troubleshooting

If you are having trouble with taichi, try launching the scripts with the environment variable `TI_ARCH=x64` to disable GPU acceleration.

## How to use blue noise
Blue noise isn't fully random. Instead, adjacent points depend on one another, and are unlikely to be close to one another (i.e. negative correlation) This means that one needs to sample blue noise distributed points "in order" to get the desirable characteristics. In a fragment shader, this would look something like the following:
```glsl
#define FRAME_OFFSET ivec2(7, 17)

ivec2 noiseSampleCoord = (ivec2(gl_FragCoord.xy) + FRAME_OFFSET * frameCounter) % textureSize(noiseTexture, 0);

float noiseSample = texelFetch(noiseTexture, noiseSampleCoord, 0).r;
```
The important part here is that gl_FragCoord.xy enters the coordinate directly.

## References

[1] Robert A. Ulichney "Void-and-cluster method for dither array generation", Proc. SPIE 1913, Human Vision, Visual Processing, and Digital Display IV, (8 September 1993)