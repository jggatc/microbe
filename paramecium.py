"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import pygame
import pygame.bufferproxy
import random
from cell import Cell


class Paramecium(Cell):
    """
    Paramecium species.
    """

    image = None
    count = 0
    id = 0
    evolving = False
    gene = { 1: 3,
             2: 2,
             3: 0,
             4: 1,
             5: 0,
             6: 1,
             7: 50,
             8: 100,
             9: -2,
            10: 3,
            11: 45,
            12: 90}
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

    def __init__(self, matrix, x, y, cell_image='paramecium.png', frames=2,
                 identity=None, inherit=None, mutation_rate=0.5,
                 limit=(9,50)):
        Cell.__init__(self, matrix, x, y, cell_image, frames,
                      identity, inherit, mutation_rate, limit)
        self.velocity = self.trait['vel_sense_f']
        self.prey_success = self.image.get_size()[0] // (self.velocity*2)  #prey capture success
        self.ingest = 4

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

    def evolve(self):
        self.evolution()    #evolve

    def sense (self):
        try:
            sense = 0
            leading_edge_x, leading_edge_y = (
                self.locate_coordinate(25,self.direction,False))  #watch IndexError?
            if self.matrix.toxin_presense:
                if (self.matrix.toxin[leading_edge_x,leading_edge_y] >
                        self.matrix.toxin[self.x,self.y]):
                    sense = 3
                    return sense
            if ((self.matrix.nutrient[leading_edge_x,leading_edge_y] >
                    self.matrix.nutrient[self.x,self.y]) or
                (self.matrix.trace[leading_edge_x,leading_edge_y] >
                     self.matrix.trace[self.x,self.y])):
                sense = 1
            else:
                reverse_direction = self.direction_set(self.direction + 180)
                back_edge_x, back_edge_y = self.locate_coordinate(
                    25,reverse_direction,False)
                if ((self.matrix.nutrient[back_edge_x,back_edge_y] >
                        self.matrix.nutrient[self.x,self.y]) or
                    (self.matrix.trace[back_edge_x,back_edge_y] >
                        self.matrix.trace[self.x,self.y])):
                        sense = 2
        except IndexError:
            sense = 0    #not sense if past edge
        return sense

    def check_interact_members(self):      #interact with other paramecium
        paramecium_bump = pygame.sprite.spritecollide(
            self, self.matrix.cells['paramecium'], False)  #paramecium avoidance
        if len(paramecium_bump) > 1:    #bumping more than self
            for bump in paramecium_bump:    #if not reverse?
                if bump == self:
                    continue
                elif (abs(bump.rect.centerx-self.rect.centerx) < 25 and
                      abs(bump.rect.centery-self.rect.centery) < 25):
                    if not self.interact or (random.random() > 0.99):
                        self.step = 0   #?
                        self.interact = random.randrange(-3,4)
        else:
            self.interact = 0   #not bumping
        if self.interact:
            self.direction = self.direction_set(
                self.direction + self.interact)
            self.rotate_image = True

    def check_interact(self):
        self.check_interact_members()
        if (self.check_edge(self.image.get_width()//2,
            self.image.get_height()//2) or
                self.check_bump_map((self.x,self.y))):
            self.motion_reverse()

    def check_bump_map(self, position):
        try:
            if (self.matrix.nutrient[position] > 10000 and
                    random.random() > 0.9):   #check if contacting nutrient peak
                nutrient_bump = True    #increase bump chance?
            else:
                nutrient_bump = False
        except IndexError:
            nutrient_bump = False
        return nutrient_bump

    def motion_reverse(self):
        if self.reverse != True:    #reverse again
            self.distance = random.randrange(40,60)
        else:
            self.distance = random.randrange(0,60)
        self.velocity *= -1
        self.direction_adj_f = 0
        self.reverse = True

    def motion(self):
        if not self.reverse:
            sense = self.sense()
            if sense == 1:
                self.distance += self.trait['dist_sense_f']()   #evolve = 1 * random.choice((0,1))
                self.velocity = self.trait['vel_sense_f']         #evolve = 3
                if not self.reverse and not self.reverse_redux:
                    self.direction_adj_f = 0
            elif sense == 2:
                self.distance -= self.trait['dist_sense_r']()  #evolve = 3 * random.choice((0,1))
                self.velocity = self.trait['vel_sense_r']       #evolve = 2
            elif sense == 3:     #toxin
                self.velocity = self.trait['vel_sense_f']   #evolve = 3
                self.direction_adj_f = random.randrange(135,180)
        if self.distance <= 0:
            if self.reverse:
                self.velocity = 2
                self.direction_adj_i = random.choice((-3,3))
                self.direction_adj_f = random.randrange(90,135)     #different for bumping nutrient?
                self.distance = random.randrange(50,75)
                self.reverse = False
                self.reverse_redux = True
            else:
                self.distance = self.trait['dist']()  #evolve = random.randrange(50,100)
                self.direction_adj_i = self.trait['dir_i']() #evolve = random.randrange(-2,3)
                self.direction_adj_f = self.trait['dir_f']() #evolve = random.randrange((45,90))
                self.velocity = random.choice((2,2))
        if self.direction_adj_f > 0:
            self.rotate_image = True
            self.direction = self.direction_set(
                self.direction + self.direction_adj_i)
            self.direction_adj_f -= self.direction_adj_i
        self.distance -= 1

    def growth(self):
        prey_collide = []
        prey_collide.extend(pygame.sprite.spritecollide(
            self, self.matrix.cells['bacterium'], False))
        prey_collide.extend(pygame.sprite.spritecollide(
            self, self.matrix.cells['algae'], False))
        for prey in prey_collide:
            if (abs(prey.rect.centerx - self.rect.centerx) <
                    self.prey_success and
                abs(prey.rect.centery - self.rect.centery) <
                    self.prey_success):
                self.ingest += 1    #evolve
                prey.life = False

    def activity(self):
        self.move()
        self.growth()

