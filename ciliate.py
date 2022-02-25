"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import random
from paramecium import Paramecium


class Ciliate(Paramecium):
    """
    Ciliate species.
    Evolved from Paramecium.
    """

    image = None
    count = 0
    id = 0
    evolving = False
    gene = {'File': 'ciliate.dat'}
    alleles = { 1: (2, 6),
                2: (2, 6),
                3: (0, 2),
                4: (2, 6),
                5: (0, 2),
                6: (2, 6),
                7: (25, 51),
                8: (75, 301),
                9: (-6, 0),
               10: (1, 7),
               11: (25, 51),
               12: (75, 126)}
    gene_info = { 1: 'Velocity Sense Forward',
                  2: 'Velocity Sense Reverse',
                  3: 'Distance Sense Forward[0]',
                  4: 'Distance Sense Forward[1]',
                  5: 'Distance Sense Reverse[0]',
                  6: 'Distance Sense Reverse[1]',
                  7: 'Distance Range[0]',
                  8: 'Distance Range[1]',
                  9: 'Direction Change Rate[0]',
                 10: 'Direction Change Rate[1]',
                 11: 'Direction Change[0]',
                 12: 'Direction Change[1]'}

    def __init__(self, matrix, x, y, cell_image='ciliate.png', frames=2,
                 identity=None, inherit=None, mutation_rate=0.5):
        Paramecium.__init__(self, matrix, x, y, cell_image, frames,
                            identity, inherit, mutation_rate)

    def set_trait(self, gene):
        #gene = 1:vel_sense_f, 2:vel_sense_r, 3:dist_sense_f-0, 4:dist_sense_f-1, 5:dist_sense_r-0, 6:dist_sense_r-1, 7:dist-0, 8:dist-1, 9:dist_i-0, 10:dist_i-1, 11:dir_f-0, 12:dir_f-1
        trait = {'vel_sense_f': gene[1],
                 'vel_sense_r': gene[2],
                 'dist_sense_f': lambda: (1 * random.choice((gene[3],gene[4]))),
                 'dist_sense_r': lambda: (3 * random.choice((gene[5],gene[6]))),
                 'dist': lambda: random.randrange(gene[7],gene[8]),
                 'dir_i': lambda: random.randrange(gene[9],gene[10]),
                 'dir_f': lambda: random.randrange(gene[11],gene[12])}
        return trait

