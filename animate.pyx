"""
Amoeba Animate

Animate function compiled using Cython. Called by Microbe.py, and if import fails (not Linux/Windows or error), will use incode Python animate function.

Linux (create .so):
NumPy <v1.4:
cython animate.pyx
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.6 -o animate.so animate.c
NumPy >v1.4:
Note: need to have new compilation because of incompatible numpy.dtype. Numpy v1.4 was compiled from source to /usr/local/lib, so require to include path.
cython -I/usr/include/python2.6 -I/usr/local/lib/python2.6/dist-packages/numpy/core/include/numpy animate_1_4.pyx
gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.6 -I/usr/local/lib/python2.6/dist-packages/numpy/core/include -o animate_1_4.so animate_1_4.c

Windows (create .pyd):
python setup.py build_ext --inplace (create .pyd)
"""

import random
import numpy
cimport numpy

DTYPE = numpy.int
ctypedef numpy.int_t DTYPE_t

cimport cython
@cython.boundscheck(False)
def amoeba_animate(numpy.ndarray[DTYPE_t, ndim=2] amoebas not None, amoebas_indices, int step_x, int step_y, int colr):
    assert amoebas.dtype == DTYPE
    cdef int left, right, front, change, index_x, index_y
    cdef unsigned int x, y, xx, yy, stepx, stepy
    cdef DTYPE_t flux, erase, color, color_max, pt
    color = <DTYPE_t>colr
    erase = 0
    stepx = step_x - 25
    stepy = step_y - 25
    left = step_x - 15
    right = step_x + 15
    front = step_y - 15
    color_max = color * 30
    for change in range(25):       #generate amoeba movement
        x = <unsigned int>(amoebas_indices[change][0] + stepx)
        y = <unsigned int>(amoebas_indices[change][1] + stepy)
        pt = amoebas[x,y]
        if pt and pt < color_max:
            flux = 0
            for index_x in range(-2, 3):
                xx = <unsigned int>(x + index_x)
                for index_y in range(0, abs(index_x)-3, -1):
                    yy = <unsigned int>(y + index_y)
                    if pt > amoebas[xx,yy]:
                        amoebas[xx,yy] += color
                        if y < front:    #only erase trail in range
                            amoebas[xx,<unsigned int>(yy+42)] = erase     #erase trail
                        if x < left:    #only erase sides in range
                            amoebas[<unsigned int>(xx+42),<unsigned int>(yy-25)] = erase    #erase sides
                            amoebas[<unsigned int>(xx+42),<unsigned int>(yy+25)] = erase
                        elif x > right:
                            amoebas[<unsigned int>(xx-42),<unsigned int>(yy-25)] = erase    #erase sides
                            amoebas[<unsigned int>(xx-42),<unsigned int>(yy+25)] = erase
                        flux += color
            amoebas[x,y] += flux
    return amoebas

