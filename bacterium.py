"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import math
import random
from cell import Cell


class Bacterium(Cell):
    """
    Bacterium species.
    """

    image = None
    count = 0
    id = 0
    evolving = False
    gene = {1: 1,
            2: 11}
    alleles = {1: (0, 2),
               2: (2, 12)}
    gene_info = {1: 'Sense[0]',
                 2: 'Sense[1]'}

    def __init__(self, matrix, x, y, cell_image='bacterium.png', frames=1,
                 identity=None, inherit=None, mutation_rate=0.5,
                 limit=(90,500)):
        Cell.__init__(self, matrix, x, y, cell_image, frames,
                      identity, inherit, mutation_rate, limit)
        self.sense_previous = 0
        self.sense_previous_toxin = 0
        self.sense_bacteria = 1 #sense bacterium trace, to gauge bacteria density
        self.growth_rate = 1.0  #rate of growth starting at 100%, modulated by population density
        self.ingest = 25000     #initial reserves
        self.max_ingest = 10000
        self.nutrient = 0
        self.consumption = 0
        self.velocity = 2

    def set_trait(self, gene):
        trait = {'sense': lambda: random.randrange(gene[1],gene[2])}
        return trait

    def evolve(self):
        self.evolution(cycle=1, division_threshold=100000)    #evolve

    def sense(self, substance='nutrient'):
        try:
            if self.sensing:    #at high density - allow to explore fresh pastures
                attract = 1
            else:
                if self.matrix.nutrient[self.x,self.y] > 100:
                    attract = -1
                else:
                    self.sensing = True
                    attract = 1
            if substance == 'nutrient':
                if (self.matrix.nutrient[self.x,self.y] >
                        self.sense_previous):
                    self.sense_previous = self.matrix.nutrient[self.x,
                                                               self.y]
                    return self.trait['sense']() * 0.02 * attract      #evolve = random.randrange(1,11)
                else:
                    self.sense_previous = self.matrix.nutrient[self.x,
                                                               self.y]
                    return 0.0
            elif substance == 'toxin':
                if self.matrix.toxin_presense:
                    if (self.matrix.toxin[self.x,self.y] <
                            self.sense_previous_toxin):
                        self.sense_previous_toxin = self.matrix.toxin[self.x,
                                                                      self.y]
                        return (random.randrange(1,11) * 0.02)
                    else:
                        self.sense_previous_toxin = self.matrix.toxin[self.x,
                                                                      self.y]
                        return 0.0
                else:
                    return 0.0
        except IndexError:
            return 0.0

    def motor_check(self):
        if (random.random() > ((0.1*self.velocity)
                                - (self.sense('nutrient')
                                    * self.velocity)
                                - (self.sense('toxin')
                                    * self.velocity))):    #need adjustment with velocity
            motive = True   #1:forward 0:tumble
        else:
            motive = False
        return motive

    def motion(self):
        if not self.fission:
            if self.motor_check():
                direction = 0
            else:
                direction = random.randrange(360)
                self.rotate_image = True
        else:
            if random.random() > 0.2:
                reverse_direction = self.direction_set(
                    self.direction + 180)
                direction = random.choice(
                    (self.direction,reverse_direction))
            else:
                direction = 0
        if direction:
            self.direction = direction

    def bacterium_trace(self):
        try:
            self.matrix.trace[self.x,self.y] = 250      #bacteria scent trace
            #trace not continuous, gaps between steps
        except IndexError:
            pass

    def bacteria_detect(self):
        """
        Bacterium detection of bacteria trace, to judge local
        bacterium density so as to avoid overcrowding.
        """
        try:
            if self.matrix.trace[self.x,self.y] > 150:
                if self.sense_bacteria < 100:
                    self.sense_bacteria += 1
            else:
                if self.sense_bacteria > 1:
                    self.sense_bacteria -= 1
        except IndexError:
            return
        if self.sensing:
            if self.sense_bacteria == 100:
                if random.random() > 0.95:
                    self.sensing = False
        else:
            if random.random() > 0.995:
                self.sensing = True
        self.growth_rate = 1.0 / math.sqrt(self.sense_bacteria)  #high density causes reduce growth rate

    def growth(self):
        if ((not self.fission) and
                (self.species.count < self.species.maximum)):
            try:
                self.nutrient = self.matrix.nutrient[self.x,self.y] * 0.01
                if self.nutrient < self.max_ingest:
                    self.consumption = self.nutrient * self.growth_rate
                else:
                    self.consumption = self.max_ingest * self.growth_rate
                self.ingest += self.consumption
                if self.ingest > 100000 and not self.species.evolving:
                    if not random.randrange(10):    #random start of fission
                        self.fission = 1
                        self.ingest = 0
                        self.velocity = 1
                self.matrix.nutrient[self.x,self.y] -= self.consumption
                if self.matrix.nutrient[self.x,self.y] < 0:
                    self.matrix.nutrient[self.x,self.y] = 0
            except IndexError:
                return
        if self.cell_division():
            self.matrix.add_creature(
                self.species, self.x, self.y, clone=True,
                inherit=self.gene.copy())
            self.velocity = 2
            if random.random() < 0.9:
                self.sensing = True
                self.sense_bacteria = 1
            else:
                self.sensing = False    #random chance to migrate
                self.sense_bacteria = 1

    def activity(self):
        Cell.activity(self)
        self.bacteria_detect()
        self.bacterium_trace()

