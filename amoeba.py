"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import pygame
import pygame.bufferproxy
import numpy
import random
try:    #animate.c compiled
    import animate
except:
    try:
        import animate3 as animate
    except:
        pass
from cell import Cell


class Amoeba(Cell):
    """
    Amoeba species.
    """

    image = None
    count = 0
    id = 0
    evolving = False
    gene = {1: 0,
            2: 2,
            3: 0,
            4: 2,
            5: 100,
            6: 200,
            7: -1,
            8: 2}
    alleles = {1: (0, 2),
               2: (2, 6),
               3: (0, 2),
               4: (2, 6),
               5: (10, 101),
               6: (150, 301),
               7: (-5, 0),
               8: (1, 6)}
    gene_info = {1: 'Distance Sense Forward[0]',
                 2: 'Distance Sense Forward[1]',
                 3: 'Distance Sense Reverse[0]',
                 4: 'Distance Sense Reverse[1]',
                 5: 'Distance Range[0]',
                 6: 'Distance Range[1]',
                 7: 'Direction Change[0]',
                 8: 'Direction Change[1]'}

    def __init__(self, matrix, x, y, cell_image=None, color=1,
                 identity=None, inherit=None, mutation_rate=0.5,
                 limit=(3,25)):
        Cell.__init__(self, matrix, x, y, identity=identity,
                      inherit=inherit, mutation_rate=mutation_rate,
                      limit=limit)
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
        self.amoebas[self.step_x-25:self.step_x+25,
                     self.step_y-25:self.step_y+25] = self.amoeba
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
        trait = {'dist_sense_f': lambda: (5 * random.randrange(gene[1],gene[2])),
                 'dist_sense_r': lambda: (5 * random.randrange(gene[3],gene[4])),
                 'dist': lambda: random.randrange(gene[5],gene[6]),
                 'dir': lambda: random.randrange(gene[7],gene[8])}
        return trait

    def evolve(self):
        self.evolution(cycle=5000, division_threshold=5)    #evolve

    def display_tag(self, display=True):
        if display:
            if not self.id_tag:
                label_size = 10
                self.id_tag = self.print_tag.font[label_size].render(
                    str(self.identity), True, (255,0,0))
            imagex, imagey = self.image.get_rect().center
            self.image.blit(self.id_tag, (imagex-3,imagey-3) )

    def sense(self):    #Sensing
        try:
            sense = False
            leading_edge_x, leading_edge_y = self.locate_coordinate(
                25,self.direction,False)  #watch IndexError?
            if self.matrix.toxin_presense:
                if (self.matrix.toxin[leading_edge_x,leading_edge_y] >
                        self.matrix.toxin[self.x,self.y]):
                    sense = False
                    return sense
            if (self.matrix.nutrient[leading_edge_x,leading_edge_y] >
                    self.matrix.nutrient[self.x,self.y] or
                self.matrix.trace[leading_edge_x,leading_edge_y] >
                    self.matrix.trace[self.x,self.y]):
                sense = True
        except IndexError:
            sense = False
        return sense

    def check_interact_members(self):
        if random.random() > 0.995:
            amoeba_bump = pygame.sprite.spritecollide(
                self, self.matrix.cells['amoeba'], False)
            if len(amoeba_bump) > 1:    #bumping more than self
                for bump in amoeba_bump:    #if not reverse?
                    if bump == self:
                        continue
                    elif (abs(bump.rect.centerx-self.rect.centerx) < 50 and
                          abs(bump.rect.centery-self.rect.centery) < 50):
                        self.interact = random.randrange(150,210)
            else:
                self.interact = 0   #not bumping
            if self.interact:
                self.direction = self.direction_set(
                    self.direction + self.interact)
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
            step_x_pos, step_y_pos = self.locate_coordinate(
                10, self.direction, change=False)
            try:
                if ((self.matrix.nutrient[step_x_pos, step_y_pos] < 500 or
                     self.matrix.nutrient[self.x,self.y] >= 500) and
                     not self.check_edge(35,35)):    #turn at nutrient
                    self.x, self.y = self.locate_coordinate(
                        1, self.direction)
                    self.step = 0
                    if self.matrix.creature_inview(self):
                        self.step_y -= 1    #only update animate move if onscreen
                else:
                    self.direction = self.direction_set(
                        self.direction + random.randrange(90,270))   #slower turn?
                    self.reverse = True
            except IndexError:
                self.direction = self.direction_set(
                    self.direction + random.randrange(90,270))
                self.reverse = True
        if self.sense():        #Sensing
            self.distance += self.trait['dist_sense_f']()   #evolve = 5 * random.randrange(0,2)
        else:
            self.distance -= self.trait['dist_sense_r']()   #evolve = 5 * random.randrange(0,2)
        self.distance -= 1
        if self.distance <= 0:
            dir_change = self.trait['dir']()    #evolve = random.randrange(-1,2)
            self.direction = self.direction_set(
                self.direction + dir_change)
            self.distance = self.trait['dist']()    #evolve = random.randrange(100, 200)

    def move_animate(self):
        if self.reverse == True:
            self.amoeba = self.amoebas[self.step_x-25:self.step_x+25,
                                       self.step_y-25:self.step_y+25]
            self.amoebas = numpy.zeros((150,300), numpy.int_)
            self.step_y = 200   #place amoeba at beginning of treadmill
            self.amoeba = numpy.fliplr(self.amoeba)
            self.amoebas[self.step_x-25:self.step_x+25,
                         self.step_y-25:self.step_y+25] = self.amoeba
            self.reverse = False
        if self.step_y < 50:    #when amoeba at end of treadmill
            self.amoeba = self.amoebas[self.step_x-25:self.step_x+25,
                                       self.step_y-25:self.step_y+25]
            self.amoebas = numpy.zeros((150,300), numpy.int_)
            self.step_y = 200   #place amoeba at beginning of treadmill
            self.amoebas[self.step_x-25:self.step_x+25,
                         self.step_y-25:self.step_y+25] = self.amoeba
        self.amoebas = self.animate(
            self.amoebas,
            self.amoebas_indices[self.amoebas_indices_keys[self.amoebas_index]],
            self.step_x, self.step_y, self.color)
        self.amoebas_index += 1
        if self.amoebas_index > 99:
            self.amoebas_index = 0
            random.shuffle(self.amoebas_indices_keys)

    def amoeba_animate(self, amoebas, amoebas_indices,
                       step_x, step_y, colr):
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
        pygame.surfarray.blit_array(
            self.species.screen_amoeba,
            self.amoebas[self.step_x-25:self.step_x+25,
                         self.step_y-25:self.step_y+25])
        image = pygame.transform.rotozoom(
            self.species.screen_amoeba, -self.direction, 1)
        image = image.convert()
        image.set_colorkey((0,0,0), pygame.RLEACCEL)
        rect = image.get_rect(center=(self.x,self.y))   #define rect position when offscreen?
        return image, rect

    def growth(self):
        prey_collide = []
        prey_collide.extend(
            pygame.sprite.spritecollide(
                self, self.matrix.cells['bacterium'], False))
        prey_collide.extend(
            pygame.sprite.spritecollide(
                self, self.matrix.cells['algae'], False))
        for prey in prey_collide:
            if (abs(prey.rect.centerx - self.rect.centerx) < 15 and
                abs(prey.rect.centery - self.rect.centery) < 15):
                self.ingest += 1
                prey.life = False

    def activity(self):
        self.move()
        self.growth()

