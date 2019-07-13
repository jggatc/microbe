"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import pygame
import pygame.bufferproxy
import numpy
import math
import random
import os
import pickle

import interphase
from util import load_image, sin_table, cos_table
try:    #animate.c compiled
    import animate
except:
    try:
        import animate3 as animate
    except:
        pass


class Evolve(object):
    """
    Manages the evolutional process.
    """

    def genetics(self, inherit=None, mutation_rate=0.5, genome=None, alleles=None):
        """Set genetics of organism. Parameters: inherit - contain copy of self.gene, otherwise, organism genetic makeup set randomly from possibilities in alleles; mutation_rate - rate at which heritable genes are mutated; genome - number of genes; alleles - ranges from which gene settings will be chosen."""
        if self.matrix.evolution and genome:     #evolve trait parameters
            self.inherit = inherit
            gene = {}
            mutation = random.random() < mutation_rate    #if inherit with mutation
            if not inherit or mutation:     #set genes chosen randomly from alleles
                for genex in range(1,genome+1):
                    gene[genex] = random.randrange(*alleles[genex])
                if mutation:
                    mutant_gene = random.choice((gene.keys()))  #mutate single gene
                    mutant_trait = { mutant_gene: gene[mutant_gene] }
            if inherit:
                gene = inherit  #clonal division
                if random.random() > 0.9:   #crossover
                    group = self.matrix.species_group[self.species]
                    gene_xo = random.choice(group.sprites()).gene
                    gene_select = random.sample(range(1,len(gene)+1), len(gene)//2)
                    for gen in gene_select:
                        gene[gen] = gene_xo[gen]
                if mutation:    #clonal division with single mutation
                    gene[mutant_gene] = mutant_trait[mutant_gene]
            return gene

    def evolution(self, cycle=500, division_threshold=18):    #selection
        """Evolutionary selection. Parameters: cycle - rate of cell update; division_threshold - energy required for division."""
        if self.life:   #prosper or perish
            self.exist += 1
            self.ingest -= 1.0/cycle  #energy expenditure
            self.fitness = self.ingest/division_threshold * 100
            if self.exist > 100:
                self.exist = 0
                if self.fitness >= 100:   #replicate when reserves sufficient
                    self.ingest = division_threshold / 4
                    if self.species.count < self.species.maximum:
                        self.matrix.add_creature(self.species, self.x, self.y, clone=True, identity=self.identity, inherit=self.gene.copy())     #give copy of self.gene, so that it's not modified
                elif self.fitness <= 0:   #possible decrease when reserves depleted
                    if random.random() > ( 0.9 - abs(self.fitness*0.1) ):
                        self.life = False
                if self.species.count < self.species.minimum:  #fresh supply to gene pool, and stop extinction
                    self.matrix.add_creature(self.species)


class Cell( pygame.sprite.Sprite, Evolve ):
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

    def __init__(self, matrix, x, y, cell_image=None, frames=1, identity=None, inherit=None, mutation_rate=0.5, limit=(10,100)):      #limit=(min,max)/1500x1500
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
                    image_frame = image.subsurface((frame_num,0), (image_width,height)).copy()
                    self.species.image.append(image_frame)
            size = (self.matrix.x*self.matrix.y) / (1500*1500)
            self.species.minimum = int( math.ceil(limit[0]*size) )
            self.species.maximum = int( math.ceil(limit[1]*size) )
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
        self.print_tag = interphase.Text(self.matrix.screen, font_size=self.label_size)
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
            gene = self.genetics(inherit,mutation_rate,genome,alleles)
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
                    self.id_tag = self.print_tag.font[self.label_size].render(str(self.identity), True, (255,0,0))
                imagex,imagey = self.image.get_rect().center
                self.image.blit(self.id_tag, (imagex-3,imagey-3) )
        else:
            self.image = pygame.transform.rotozoom(self.species.image[self.image_frame], -self.direction, 1.0)

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
        self.x, self.y = self.locate_coordinate(self.velocity, self.direction)
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
                self.image = pygame.transform.rotozoom(self.species.image[self.image_frame], -self.direction, 1.0)
                self.rotate_image = False
        self.rect = self.image.get_rect(center=(self.x,self.y))

    def check_interact(self):
        self.check_edge()

    def check_edge(self, margin_x=0, margin_y=0):
        left_edge = 0 + margin_x
        right_edge = self.matrix.x-1 - margin_x
        top_edge = 0 + margin_y
        bottom_edge = self.matrix.y-1 - margin_y
        if self.x < left_edge or self.x > right_edge or self.y < top_edge or self.y > bottom_edge:
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
        """Calculates coordinate following step in a given direction from starting position self.pos_x, self.pos_y.
           If change is True changes self.pos_x/self.pos_y, otherwise just return calculated position."""
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

    def __init__(self, matrix, x, y, cell_image='algae.png', frames=1, identity=None, inherit=None, mutation_rate=0.5):
        Cell.__init__(self, matrix, x, y, cell_image, frames, identity, inherit, mutation_rate)

    def display_tag(self, display=True):
        pass


class Bacterium(Cell):
    """
    Bacterium species.
    """

    image = None
    count = 0
    id = 0
    evolving = False
    gene = { 1:1, 2:11 }
    alleles = { 1:(0,2), 2:(2,12) }
    gene_info = { 1:'Sense[0]', 2:'Sense[1]' }

    def __init__(self, matrix, x, y, cell_image='bacterium.png', frames=1, identity=None, inherit=None, mutation_rate=0.5, limit=(90,500)):
        Cell.__init__(self, matrix, x, y, cell_image, frames, identity, inherit, mutation_rate, limit)
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
        trait = { 'sense': lambda: random.randrange(gene[1],gene[2]) }
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
            if substance is 'nutrient':
                if self.matrix.nutrient[self.x,self.y] > self.sense_previous:
                    self.sense_previous = self.matrix.nutrient[self.x,self.y]
                    return self.trait['sense']() * 0.02 * attract      #evolve = random.randrange(1,11)
                else:
                    self.sense_previous = self.matrix.nutrient[self.x,self.y]
                    return 0.0
            elif substance is 'toxin':
                if self.matrix.toxin_presense:
                    if self.matrix.toxin[self.x,self.y] < self.sense_previous_toxin:
                        self.sense_previous_toxin = self.matrix.toxin[self.x,self.y]
                        return (random.randrange(1,11) * 0.02)
                    else:
                        self.sense_previous_toxin = self.matrix.toxin[self.x,self.y]
                        return 0.0
                else:
                    return 0.0
        except IndexError:
            return 0.0

    def motor_check(self):
        if random.random() > ( (0.1*self.velocity) - (self.sense('nutrient')*self.velocity) - (self.sense('toxin')*self.velocity) ):    #need adjustment with velocity
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
                reverse_direction = self.direction_set( self.direction + 180 )
                direction = random.choice((self.direction,reverse_direction))
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
        "Bacterium detection of bacteria trace, to judge local bacterium density so as to avoid overcrowding"
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
        if (not self.fission) and (self.species.count < self.species.maximum):
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
            self.matrix.add_creature(self.species, self.x, self.y, clone=True, inherit=self.gene.copy())
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


class Paramecium(Cell):
    """
    Paramecium species.
    """

    image = None
    count = 0
    id = 0
    evolving = False
    gene = { 1:3, 2:2, 3:0, 4:1, 5:0, 6:1, 7:50, 8:100, 9:-2, 10:3, 11:45, 12:90 }
    alleles = { 1:(2,6), 2:(2,6), 3:(0,2), 4:(2,6), 5:(0,2), 6:(2,6), 7:(25,51), 8:(75,301), 9:(-6,0), 10:(1,7), 11:(25,51), 12:(75,126) }
    gene_info = { 1:'Velocity Sense Forward', 2:'Velocity Sense Reverse', 3:'Distance Sense Forward[0]', 4:'Distance Sense Forward[1]', 5:'Distance Sense Reverse[0]', 6:'Distance Sense Reverse[1]', 7:'Distance Range[0]', 8:'Distance Range[1]', 9:'Direction Change Rate[0]', 10:'Direction Change Rate[1]', 11:'Direction Change[0]', 12:'Direction Change[1]' }

    def __init__(self, matrix, x, y, cell_image='paramecium.png', frames=2, identity=None, inherit=None, mutation_rate=0.5, limit=(9,50)):
        Cell.__init__(self, matrix, x, y, cell_image, frames, identity, inherit, mutation_rate, limit)
        self.velocity = self.trait['vel_sense_f']
        self.prey_success = self.image.get_size()[0]//(self.velocity*2)  #prey capture success
        self.ingest = 4

    def set_trait(self, gene):
        #gene = 1:vel_sense_f, 2:vel_sense_r, 3:dist_sense_f-0, 4:dist_sense_f-1, 5:dist_sense_r-0, 6:dist_sense_r-1, 7:dist-0, 8:dist-1, 9:dist_i-0, 10:dist_i-1, 11:dir_f-0, 12:dir_f-1
        trait = { 'vel_sense_f': gene[1], \
                  'vel_sense_r': gene[2],  \
                  'dist_sense_f': lambda: ( 1 * random.choice((gene[3],gene[4])) ), \
                  'dist_sense_r': lambda: ( 3 * random.choice((gene[5],gene[6])) ), \
                  'dist': lambda: random.randrange(gene[7],gene[8]), \
                  'dir_i': lambda: random.randrange(gene[9],gene[10]), \
                  'dir_f': lambda: random.randrange(gene[11],gene[12]) }
        return trait

    def evolve(self):
        self.evolution()    #evolve

    def sense (self):
        try:
            sense = 0
            leading_edge_x, leading_edge_y = self.locate_coordinate(25,self.direction,False)  #watch IndexError?
            if self.matrix.toxin_presense:
                if self.matrix.toxin[leading_edge_x,leading_edge_y] > self.matrix.toxin[self.x,self.y]:
                    sense = 3
                    return sense
            if (self.matrix.nutrient[leading_edge_x,leading_edge_y] > self.matrix.nutrient[self.x,self.y]) or (self.matrix.trace[leading_edge_x,leading_edge_y] > self.matrix.trace[self.x,self.y]):
                sense = 1
            else:
                reverse_direction = self.direction_set( self.direction + 180 )
                back_edge_x, back_edge_y = self.locate_coordinate(25,reverse_direction,False)
                if (self.matrix.nutrient[back_edge_x,back_edge_y] > self.matrix.nutrient[self.x,self.y]) or (self.matrix.trace[back_edge_x,back_edge_y] > self.matrix.trace[self.x,self.y]):
                        sense = 2
        except IndexError:
            sense = 0    #not sense if past edge
        return sense

    def check_interact_members(self):      #interact with other paramecium
        paramecium_bump = pygame.sprite.spritecollide(self, self.matrix.cells['paramecium'], False)  #paramecium avoidance
        if len(paramecium_bump) > 1:    #bumping more than self
            for bump in paramecium_bump:    #if not reverse?
                if bump == self:
                    continue
                elif (abs(bump.rect.centerx-self.rect.centerx) < 25 and abs(bump.rect.centery-self.rect.centery) < 25):
                    if not self.interact or (random.random() > 0.99):
                        self.step = 0   #?
                        self.interact = random.randrange(-3,4)
        else:
            self.interact = 0   #not bumping
        if self.interact:
            self.direction = self.direction_set( self.direction + self.interact )
            self.rotate_image = True

    def check_interact(self):
        self.check_interact_members()
        if self.check_edge(self.image.get_width()//2,self.image.get_height()//2) or self.check_bump_map((self.x,self.y)):
            self.motion_reverse()

    def check_bump_map(self, position):
        try:
            if self.matrix.nutrient[position] > 10000 and random.random() > 0.9:   #check if contacting nutrient peak
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
            self.direction = self.direction_set( self.direction + self.direction_adj_i )
            self.direction_adj_f -= self.direction_adj_i
        self.distance -= 1

    def growth(self):
        prey_collide = []
        prey_collide.extend( pygame.sprite.spritecollide(self, self.matrix.cells['bacterium'], False) )
        prey_collide.extend( pygame.sprite.spritecollide(self, self.matrix.cells['algae'], False) )
        for prey in prey_collide:
            if abs(prey.rect.centerx - self.rect.centerx) < self.prey_success and abs(prey.rect.centery - self.rect.centery) < self.prey_success:
                self.ingest += 1    #evolve
                prey.life = False

    def activity(self):
        self.move()
        self.growth()


class Amoeba(Cell):
    """
    Amoeba species.
    """

    image = None
    count = 0
    id = 0
    evolving = False
    gene = { 1:0, 2:2, 3:0, 4:2, 5:100, 6:200, 7:-1, 8:2 }
    alleles = { 1:(0,2), 2:(2,6), 3:(0,2), 4:(2,6), 5:(10,101), 6:(150,301), 7:(-5,0), 8:(1,6) }
    gene_info = { 1:'Distance Sense Forward[0]', 2:'Distance Sense Forward[1]', 3:'Distance Sense Reverse[0]', 4:'Distance Sense Reverse[1]', 5:'Distance Range[0]', 6:'Distance Range[1]', 7:'Direction Change[0]', 8:'Direction Change[1]' }

    def __init__(self, matrix, x, y, cell_image=None, color=1, identity=None, inherit=None, mutation_rate=0.5, limit=(3,25)):
        Cell.__init__(self, matrix, x, y, identity=identity, inherit=inherit, mutation_rate=mutation_rate, limit=limit)
        self.step = 0
        self.step_x = 75    # step location in animate movement
        self.step_y = 200
        if color < 1000:
            self.color = color * 1000 * 10
        elif color == 1000:
            self.color = 16600585   #16600585   #1000   #15000000   #color800*1000*10
        if self.species.image is None:
            self.species.screen_amoeba = pygame.Surface((50,50))
            self.species.image = self.species.screen_amoeba
        self.amoeba = numpy.zeros((50,50), numpy.int_)
        for x in range(10,40,2):
            for y in range(10,40,2):
                self.amoeba[x,y] = self.color
        self.amoebas = numpy.zeros((150,300), numpy.int_)     #amoeba move array with display overlap
        self.amoebas[self.step_x-25:self.step_x+25,self.step_y-25:self.step_y+25] = self.amoeba
        try:
            self.animate = animate.amoeba_animate   #compiled
        except NameError:
            self.animate = self.amoeba_animate
        amoebas_indices = [(x,y) for x in range(50) for y in range(50)]
        random.shuffle(amoebas_indices)
        self.amoebas_indices = {}
        for i in range(100):
            self.amoebas_indices[i] = amoebas_indices[i*25:(i*25)+25]
        self.amoebas_indices_keys = list(self.amoebas_indices.keys())
        random.shuffle(self.amoebas_indices_keys)
        self.amoebas_index = 0
        for update_count in range(50):
            self.move_animate()     #initial walk to form
        self.image, self.rect = self.update_image()
        self.direction = random.randrange(360)
        self.velocity = 2
        self.distance = 300
        self.reverse = False
        self.ingest = 1

    def set_trait(self, gene):
        #gene = 1:dist_sense_f-0, 2:dist_sense_f-1, 3:dist_sense_r-0, 4:dist_sense_r-1, 5:dist-0, 6:dist-1, 7:dir-0, 8:dir-1
        trait = { 'dist_sense_f': lambda: ( 5 * random.randrange(gene[1],gene[2]) ), \
                  'dist_sense_r': lambda: ( 5 * random.randrange(gene[3],gene[4]) ), \
                  'dist': lambda: random.randrange(gene[5],gene[6]), \
                  'dir': lambda: random.randrange(gene[7],gene[8]) }
        return trait

    def evolve(self):
        self.evolution(cycle=5000, division_threshold=5)    #evolve

    def display_tag(self, display=True):
        if display:
            if not self.id_tag:
                label_size = 10
                self.id_tag = self.print_tag.font[label_size].render(str(self.identity), True, (255,0,0))
            imagex,imagey = self.image.get_rect().center
            self.image.blit(self.id_tag, (imagex-3,imagey-3) )

    def sense(self):    #Sensing
        try:
            sense = False
            leading_edge_x, leading_edge_y = self.locate_coordinate(25,self.direction,False)  #watch IndexError?
            if self.matrix.toxin_presense:
                if self.matrix.toxin[leading_edge_x,leading_edge_y] > self.matrix.toxin[self.x,self.y]:
                    sense = False
                    return sense
            if self.matrix.nutrient[leading_edge_x,leading_edge_y] > self.matrix.nutrient[self.x,self.y] or self.matrix.trace[leading_edge_x,leading_edge_y] > self.matrix.trace[self.x,self.y]:
                sense = True
        except IndexError:
            sense = False
        return sense

    def check_interact_members(self):
        if random.random() > 0.995:
            amoeba_bump = pygame.sprite.spritecollide(self, self.matrix.cells['amoeba'], False)
            if len(amoeba_bump) > 1:    #bumping more than self
                for bump in amoeba_bump:    #if not reverse?
                    if bump == self:
                        continue
                    elif (abs(bump.rect.centerx-self.rect.centerx) < 50 and abs(bump.rect.centery-self.rect.centery) < 50):
                        self.interact = random.randrange(150,210)
            else:
                self.interact = 0   #not bumping
            if self.interact:
                self.direction = self.direction_set( self.direction + self.interact )
                self.interact = 0
                self.reverse = True

    def move(self):
        self.velocity = 2
        for i in range(self.velocity):
            self.motion()
        self.check_interact_members()
        if self.matrix.creature_inview(self):
            for i in range(self.velocity):
                self.move_animate()
            self.image, self.rect = self.update_image()
        else:
            self.rect.center = ((self.x,self.y))

    def motion(self):
        self.step += 1
        if self.step > 12:
            step_x_pos, step_y_pos = self.locate_coordinate(10, self.direction, change=False)
            try:
                if ( self.matrix.nutrient[step_x_pos, step_y_pos] < 500 or self.matrix.nutrient[self.x,self.y] >= 500 ) and not self.check_edge(35,35):    #turn at nutrient
                    self.x, self.y = self.locate_coordinate(1, self.direction)
                    self.step = 0
                    if self.matrix.creature_inview(self):
                        self.step_y -= 1    #only update animate move if onscreen
                else:
                    self.direction = self.direction_set( self.direction + random.randrange(90,270) )   #slower turn?
                    self.reverse = True
            except IndexError:
                self.direction = self.direction_set( self.direction + random.randrange(90,270) )
                self.reverse = True
        if self.sense():        #Sensing
            self.distance += self.trait['dist_sense_f']()   #evolve = 5 * random.randrange(0,2)
        else:
            self.distance -= self.trait['dist_sense_r']()   #evolve = 5 * random.randrange(0,2)
        self.distance -= 1
        if self.distance <= 0:
            dir_change = self.trait['dir']()    #evolve = random.randrange(-1,2)
            self.direction = self.direction_set(self.direction + dir_change)
            self.distance = self.trait['dist']()    #evolve = random.randrange(100, 200)

    def move_animate(self):
        if self.reverse == True:
            self.amoeba = self.amoebas[self.step_x-25:self.step_x+25,self.step_y-25:self.step_y+25]
            self.amoebas = numpy.zeros((150,300), numpy.int_)
            self.step_y = 200   #place amoeba at beginning of treadmill
            self.amoeba = numpy.fliplr(self.amoeba)
            self.amoebas[self.step_x-25:self.step_x+25,self.step_y-25:self.step_y+25] = self.amoeba
            self.reverse = False
        if self.step_y < 50:    #when amoeba at end of treadmill
            self.amoeba = self.amoebas[self.step_x-25:self.step_x+25,self.step_y-25:self.step_y+25]
            self.amoebas = numpy.zeros((150,300), numpy.int_)
            self.step_y = 200   #place amoeba at beginning of treadmill
            self.amoebas[self.step_x-25:self.step_x+25,self.step_y-25:self.step_y+25] = self.amoeba
        self.amoebas = self.animate(self.amoebas, self.amoebas_indices[self.amoebas_indices_keys[self.amoebas_index]], self.step_x, self.step_y, self.color)
        self.amoebas_index += 1
        if self.amoebas_index > 99:
            self.amoebas_index = 0
            random.shuffle(self.amoebas_indices_keys)

    def amoeba_animate(self, amoebas, amoebas_indices, step_x, step_y, colr):
        color = colr
        erase = 0
        stepx = step_x - 25
        stepy = step_y - 25
        left = step_x - 15
        right = step_x + 15
        front = step_y - 15
        color_max = color * 30
        for change in range(25):       #generate amoeba movement
            x = amoebas_indices[change][0] + stepx
            y = amoebas_indices[change][1] + stepy
            pt = amoebas[x,y]
            if pt and pt < color_max:
                flux = 0
                for index_x in range(-2, 3):
                    xx = x + index_x
                    for index_y in range(0, abs(index_x)-3, -1):
                        yy = y + index_y
                        if pt > amoebas[xx,yy]:
                            amoebas[xx,yy] += color
                            if y < front:    #only erase trail in range
                                amoebas[xx,yy+42] = erase     #erase trail
                            if x < left:    #only erase sides in range
                                amoebas[xx+42,yy-25] = erase     #erase sides
                                amoebas[xx+42,yy+25] = erase
                            elif x > right:
                                amoebas[xx-42,yy-25] = erase     #erase sides
                                amoebas[xx-42,yy+25] = erase
                            flux += color
                amoebas[x,y] += flux
        return amoebas

    def update_image(self):
        #update_image
        pygame.surfarray.blit_array(self.species.screen_amoeba, self.amoebas[self.step_x-25:self.step_x+25,self.step_y-25:self.step_y+25])
        image = pygame.transform.rotozoom(self.species.screen_amoeba, -self.direction, 1)
        image = image.convert()
        image.set_colorkey((0,0,0), pygame.RLEACCEL)
        rect = image.get_rect(center=(self.x,self.y))   #define rect position when offscreen?
        return image, rect

    def growth(self):
        prey_collide = []
        prey_collide.extend( pygame.sprite.spritecollide(self, self.matrix.cells['bacterium'], False) )
        prey_collide.extend( pygame.sprite.spritecollide(self, self.matrix.cells['algae'], False) )
        for prey in prey_collide:
            if abs(prey.rect.centerx - self.rect.centerx) < 15 and abs(prey.rect.centery - self.rect.centery) < 15:
                self.ingest += 1
                prey.life = False

    def activity(self):
        self.move()
        self.growth()


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
    alleles = { 1:(2,6), 2:(2,6), 3:(0,2), 4:(2,6), 5:(0,2), 6:(2,6), 7:(25,51), 8:(75,301), 9:(-6,0), 10:(1,7), 11:(25,51), 12:(75,126) }
    gene_info = { 1:'Velocity Sense Forward', 2:'Velocity Sense Reverse', 3:'Distance Sense Forward[0]', 4:'Distance Sense Forward[1]', 5:'Distance Sense Reverse[0]', 6:'Distance Sense Reverse[1]', 7:'Distance Range[0]', 8:'Distance Range[1]', 9:'Direction Change Rate[0]', 10:'Direction Change Rate[1]', 11:'Direction Change[0]', 12:'Direction Change[1]' }

    def __init__(self, matrix, x, y, cell_image='ciliate.png', frames=2, identity=None, inherit=None, mutation_rate=0.5):
        Paramecium.__init__(self, matrix, x, y, cell_image, frames, identity, inherit, mutation_rate)

    def set_trait(self, gene):
        #gene = 1:vel_sense_f, 2:vel_sense_r, 3:dist_sense_f-0, 4:dist_sense_f-1, 5:dist_sense_r-0, 6:dist_sense_r-1, 7:dist-0, 8:dist-1, 9:dist_i-0, 10:dist_i-1, 11:dir_f-0, 12:dir_f-1
        trait = { 'vel_sense_f': gene[1], \
                  'vel_sense_r': gene[2],  \
                  'dist_sense_f': lambda: ( 1 * random.choice((gene[3],gene[4])) ), \
                  'dist_sense_r': lambda: ( 3 * random.choice((gene[5],gene[6])) ), \
                  'dist': lambda: random.randrange(gene[7],gene[8]), \
                  'dir_i': lambda: random.randrange(gene[9],gene[10]), \
                  'dir_f': lambda: random.randrange(gene[11],gene[12]) }
        return trait

