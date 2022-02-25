"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
from cell import Cell


class Algae(Cell):
    """
    Algae species.
    """

    image = None
    count = 0
    id = 0
    evolving = False
    gene = {}
    alleles = {}

    def __init__(self, matrix, x, y, cell_image='algae.png', frames=1,
                 identity=None, inherit=None, mutation_rate=0.5):
        Cell.__init__(self, matrix, x, y, cell_image, frames,
                      identity, inherit, mutation_rate)

    def display_tag(self, display=True):
        pass

