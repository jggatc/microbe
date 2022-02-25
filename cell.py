"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import pygame
import pygame.bufferproxy
import math
import random
import os
import pickle
import interphase
from util import load_image, sin_table, cos_table
from evolve import Evolve


class Cell(pygame.sprite.Sprite, Evolve):
    """
    Cell class is the base class of cells.
    """

    image = None
    count = 0
    minimum = 10
    maximum = 100
    id = 0      #id when created
    evolving = False    #species evolving
    gene = {}
    alleles = {}
    gene_info = {}

    def __init__(self, matrix, x, y, cell_image=None, frames=1,
                 identity=None, inherit=None, mutation_rate=0.5,
                 limit=(10,100)):      #limit=(min,max)/1500x1500
        pygame.sprite.Sprite.__init__(self)
        self.species = self.__class__
        self.matrix = matrix
        self.species.count += 1     #number of species in matrix
        self.species.id += 1
        self.identity = self.species.id
        self.gene = {}
        self.x = x  #location in matrix
        self.y = y
        self.pos_x = float(self.x)     #float version
        self.pos_y = float(self.y)
        self.distance = 0       #Distance to move before changing direction, unless adjustment with sense
        self.direction = random.randrange(360)
        self.direction_adj_i = 0    #fine directional adjustment
        self.direction_adj_f = 0    #full directional adjustment
        self.move_x = 1
        self.move_y = 1
        self.velocity = 1
        self.reverse = False    #if in avoidance behaviour
        self.reverse_redux = False
        self.rotate = 0     #image rotation - none = 0, ccr = -1, cr =1
        self.rotate_count = 0   #?
        self.interact = 0   #response taken to bumping other paramecium
        self.life = True
        self.exist = 0    #time since instance created
        self.ingest = 0
        self.fitness = 100
        self.fission = 0
        if self.species.image is None:       #init on first class instance
            if cell_image:
                self.species.image = []
                image = load_image(cell_image)
                width, height = image.get_size()
                image_width = width // frames
                for frame in range(frames):
                    frame_num = image_width * frame
                    image_frame = image.subsurface(
                        (frame_num,0), (image_width,height)).copy()
                    self.species.image.append(image_frame)
            size = (self.matrix.x*self.matrix.y) / (1500*1500)
            self.species.minimum = int(math.ceil(limit[0] * size))
            self.species.maximum = int(math.ceil(limit[1] * size))
        self.phenotype(self.species, cell_image, frames)     #default image
        if identity:
            self.identity = identity
        self.gene, self.trait = self.genotype(inherit,mutation_rate)
        self.rotate_image = True   #rotate with direction change
        self.sensing = True     #if sensing
        self.label_display = True
        self.id_tag = None  #text id label
        try:
            if self.species.image[0].get_size()[0] <= 10:
                self.label_size = 6
            else:
                self.label_size = 10
        except:
            self.label_size = 10
        self.print_tag = interphase.Text(self.matrix.screen,
                                         font_size=self.label_size)
        self.growth_rate = 1.0

    def set_trait(self, gene):
        "Set in species class"
        trait = {}
        return trait

    def genotype(self, inherit, mutation_rate):
        if not inherit:
            gene = self.species.gene.copy()
        else:
            gene = inherit
        if 'File' in gene:      #For evolved species, gene in file
            fn = os.path.join('data', gene['File'])
            bug_file = open(fn, 'rb')
            gene = pickle.load(bug_file)
            bug_file.close()
        if self.matrix.evolution and self.species.evolving:
            genome = len(gene)
            alleles = self.species.alleles.copy()
            gene = self.genetics(inherit, mutation_rate,
                                 genome, alleles)
        trait = self.set_trait(gene)
        return gene, trait

    def set_gene(self, gene):
        self.gene = gene
        self.trait = self.set_trait(gene)

    def evolve(self):
        self.evolution()

    def phenotype(self, species, cell_image, frames):
        if cell_image:
            self.image = species.image[0].copy()
            self.rect = self.image.get_rect(center=(self.x,self.y))
            if frames == 1:
                self.image_multiframe = 0    #single_frame
            else:
                self.image_multiframe = frames    #multi_frame
            self.image_frame = 0    #current image frame
            self.image_frame_counter = 0    #frame switch timer

    def display_tag(self, display=True):
        if display:
            if not self.rotate_image:
                if not self.id_tag:
                    self.id_tag = self.print_tag.font[self.label_size].render(
                        str(self.identity), True, (255,0,0))
                imagex,imagey = self.image.get_rect().center
                self.image.blit(self.id_tag, (imagex-3,imagey-3) )
        else:
            self.image = pygame.transform.rotozoom(
                self.species.image[self.image_frame],
                -self.direction, 1.0)

    def life_check(self):
        if self.life:
            return True
        else:
            self.species.count -= 1
            return False

    def motion(self):
        self.direction = random.randrange(360)

    def move(self):
        self.motion()
        self.locate()

    def sense(self):    #sense() in species
        pass

    def growth(self):
        pass

    def locate(self):
        self.x, self.y = self.locate_coordinate(self.velocity,
                                                self.direction)
        self.check_interact()   #check if pass edge, adjust position accordingly
        if self.matrix.creature_inview(self):   #image update if inview
            if self.image_multiframe:
                self.image_frame_counter += 1
                if self.image_frame_counter > 2:
                    self.image_frame_counter = 0
                    self.image_frame += 1
                    if self.image_frame >= self.image_multiframe:
                        self.image_frame = 0
                self.rotate_image = True
            if self.rotate_image:   #rotozoom better quality than rotate
                self.image = pygame.transform.rotozoom(
                    self.species.image[self.image_frame],
                    -self.direction, 1.0)
                self.rotate_image = False
        self.rect = self.image.get_rect(center=(self.x,self.y))

    def check_interact(self):
        self.check_edge()

    def check_edge(self, margin_x=0, margin_y=0):
        left_edge = 0 + margin_x
        right_edge = self.matrix.x-1 - margin_x
        top_edge = 0 + margin_y
        bottom_edge = self.matrix.y-1 - margin_y
        if (self.x < left_edge or self.x > right_edge or
            self.y < top_edge or self.y > bottom_edge):
            if self.x < left_edge:
                self.x = left_edge
            elif self.x > right_edge:
                self.x = right_edge
            if self.y < top_edge:
                self.y = top_edge
            elif self.y > bottom_edge:
                self.y = bottom_edge
            self.pos_x, self.pos_y = float(self.x), float(self.y)
            return True
        else:
            return False

    def locate_coordinate(self, step, direction, change=True):
        """
        Calculates coordinate following step in a given direction
        from starting position self.pos_x, self.pos_y. If change
        is True changes self.pos_x/self.pos_y, otherwise just
        return calculated position.
        """
        x = self.pos_x
        y = self.pos_y
        x += +step*sin_table[direction]     # x += +step*math.sin(direction*math.pi/180)
        y += -step*cos_table[direction]     # y += -step*math.cos(direction*math.pi/180)
        if change:      #maintain float position
            self.pos_x = x
            self.pos_y = y
        return int(x), int(y)

    def direction_set(self, direction):
        if direction >= 360:
            direction -= 360
        elif direction < 0:
            direction += 360
        return direction

    def cell_division(self, time=500):
        if self.fission:
            self.fission += 1
            if self.fission > time:
                self.fission = 0
                return True
            else:
                return False
        else:
            return False

    def activity(self):
        self.move()
        self.growth()

    def update(self):
        self.activity()
        if self.matrix.evolution and self.species.evolving:
            if self.species.evolving != 'pause':
                self.evolve()
            else:
                self.display_tag(False)
                self.species.evolving = False

