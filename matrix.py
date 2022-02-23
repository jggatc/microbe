"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import pygame
import pygame.bufferproxy
import numpy
import random
import os
import pickle

from cells import Algae, Bacterium, Paramecium, Amoeba, Ciliate


class Matrix(object):
    """
    The virtual environment construct.
    """

    def __init__(self, parameters):
        self.x = parameters['matrix_size'][0]     #Matrix dimension
        self.y = parameters['matrix_size'][1]
        self.dx = parameters['display_size'][0]     #Display dimension
        self.dy = parameters['display_size'][1]
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_caption('Microbe')
        iconname = os.path.join('data', 'icon.png')
        icon = pygame.image.load(iconname)
        pygame.display.set_icon(icon)
        pygame.mouse.set_visible(True)
        pygame.surfarray.use_arraytype('numpy')
        if parameters['gamma']:
            gamma_set = pygame.display.set_gamma(parameters['gamma'])
        self.screen = pygame.display.set_mode((self.dx,self.dy))
        if parameters['gamma'] and not gamma_set:   #if prior set_gamma failed
            gamma_set = pygame.display.set_gamma(parameters['gamma'])
        self.screen_toxin = pygame.display.get_surface()
        self.screen_microbe = pygame.display.get_surface()
        self.cells = {}
        self.cells['algae'] = pygame.sprite.RenderUpdates()
        self.cells['bacterium'] = pygame.sprite.RenderUpdates()
        self.cells['paramecium'] = pygame.sprite.RenderUpdates()
        self.cells['amoeba'] = pygame.sprite.RenderUpdates()
        self.cells['creatures'] = pygame.sprite.OrderedUpdates()
        self.species = [Algae,
                        Bacterium,
                        Paramecium,
                        Amoeba,
                        Ciliate]
        self.species_group = {Algae: self.cells['algae'],
                              Bacterium: self.cells['bacterium'],
                              Paramecium: self.cells['paramecium'],
                              Amoeba: self.cells['amoeba'],
                              Ciliate: self.cells['paramecium']}
        self.media = numpy.fromfunction(
            lambda xf,yf: ((1.0 / ((((xf - (self.x/2))**2)
                            + (yf - (self.y/2))**2) + 1.0)) * 1000000),
                           (self.x, self.y))   #+1.0 to avoid div by zero
        self.media = numpy.where(self.media>2, self.media, 0)   #min diffuse level and defines circular edge
        self.media = self.media.astype('i')       #type for pygame.surfarray.blit_array()
        self.nutrient = numpy.zeros((self.x,self.y), 'i')
        self.toxin_presense = False     #if toxin used
        self.trace = numpy.zeros((self.x,self.y), 'B')      #bacteria scent trace
        self.trace_update = 0
        self.trace_x = 0
        self.trace_y = 0
        self.trace_display = False  #visual display of bacterium trace
        self.field_x = 0       #field scroll
        self.field_y = 0
        self.overlap = 50     #screen field overlap?
        self.screen_update = True    #screen update at intervals
        self.screen_update_count = 0
        self.update_list = []    #list of all rect to be updated on display
        self.matrix_surface = pygame.Surface((self.dx,self.dy))
        self.scroll_field = {'x': None, 'y': None}
        self.scroll_step = 2    #scroll_rate:5, bug_follow:2
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_x_pre = 0
        self.mouse_y_pre = 0
        self.zoom_surface = pygame.display.get_surface()
        self.zoom_set = False   #Zoom settings
        self.zoom_power = 2
        self.zoom_init = False
        self.surface_clear = pygame.Surface((200,200))  #zoom clear
        self.bug_tag = None
        self.bug_follow = False  #when bug tagged, determine if view follows
        self.evolution = False  #evolve
        self.tag_display = True     #whether tag is displayed
        self.newspecies = {}    #newspecies objects
        self.control = None

    def setup(self, algae=True, bacterium=True, paramecium=True,
              amoeba=True, ciliate=True):
        creatures = {Algae: algae,
                     Bacterium: bacterium,
                     Paramecium: paramecium,
                     Amoeba: amoeba,
                     Ciliate: ciliate}
        repeat = 3
        for i in range((self.x*self.y) // 150000):
            x = random.randrange(0, self.x)
            y = random.randrange(0, self.y)
            self.gradient(x,y)
            if repeat:
                self.gradient(x,y)
                repeat -= 1
        for cell in self.species:
            if creatures[cell]:
                while(cell.count < cell.minimum):
                    self.add_creature(cell)

    def set_gradient(self, x, y, gradient_type='Nutrient'):
        if gradient_type == 'Nutrient':
            if not self.nutrient[x + self.field_x,
                                 y + self.field_y] > 1000000:     #max nutrient per locale
                self.gradient(x + self.field_x,
                              y + self.field_y,
                              gradient_type='Nutrient')
                self.screen_update_count = 0
                self.screen_update = True
        elif gradient_type == 'Toxin':
            if not self.toxin_presense:
                self.toxin = numpy.zeros((self.x,self.y), 'i')
                self.toxinx = numpy.zeros((self.dx,self.dy), 'i')
                self.toxin_presense = True
            if not self.toxin[x + self.field_x,
                              y + self.field_y] > 1000000:     #max toxin per locale
                self.gradient(x + self.field_x,
                              y + self.field_y,
                              gradient_type='Toxin')
                self.screen_update_count = 0
                self.screen_update = True

    def gradient(self, x, y, gradient_type='Nutrient'):
        dx = abs(x - (self.x//2))   #position offset from matrix center
        dy = abs(y - (self.y//2))
        if x <= self.x//2:        #define overlapping area of matrices to be combined
            matx1 = 0
            matx2 = self.x - dx
            medx1 = 0 + dx
            medx2 = self.x
        else:
            matx1 = 0 + dx
            matx2 = self.x
            medx1 = 0
            medx2 = self.x - dx
        if y <= self.y//2:
            maty1 = 0
            maty2 = self.y - dy
            medy1 = 0 + dy
            medy2 = self.y
        else:
            maty1 = 0 + dy
            maty2 = self.y
            medy1 = 0
            medy2 = self.y - dy
        if gradient_type == 'Nutrient':
            self.nutrient[matx1:matx2,maty1:maty2] = (
                numpy.add(self.nutrient[matx1:matx2, maty1:maty2],
                          self.media[medx1:medx2, medy1:medy2]))
        elif gradient_type == 'Toxin':
            self.toxin[matx1:matx2,maty1:maty2] = (
                numpy.add(self.toxin[matx1:matx2, maty1:maty2],
                          self.media[medx1:medx2, medy1:medy2]))

    def add_creature(self, species, x=None, y=None, clone=False,
                     identity=None, inherit=None):
        if isinstance(species, str):
            species = {'Algae': Algae,
                       'Bacterium': Bacterium,
                       'Paramecium': Paramecium,
                       'Amoeba': Amoeba,
                       'Ciliate': Ciliate}[species]
        if (x is not None) and (y is not None) and not clone:   #x,y is matrix pos when clone, mouse pos is coordinated to screen
            x += self.field_x
            y += self.field_y
            if x < 10:      #x=0 caused random pos
                x = 10
            elif x > self.x-10:
                x = self.x-10
            if y < 10:
                y = 10
            elif y > self.y-10:
                y = self.y-10
        matrix = self
        if species is Algae:
            if Algae.count < Algae.maximum:
                x = x or random.randrange(10, self.x-10)    #boundary -10 to remain in range
                y = y or random.randrange(10, self.y-10)
                self.cells['algae'].add(Algae(matrix, x, y))
        elif species is Bacterium:
            if Bacterium.count < Bacterium.maximum:
                x = x or random.randrange(10, self.x-10)
                y = y or random.randrange(10, self.y-10)
                self.cells['bacterium'].add(
                    Bacterium(matrix, x, y, identity=identity,
                              inherit=inherit))
        elif species is Paramecium:
            if Paramecium.count < Paramecium.maximum:
                x = x or random.randrange(100, self.x-100)
                y = y or random.randrange(100, self.y-100)
                self.cells['paramecium'].add(
                    Paramecium(matrix, x, y, identity=identity,
                               inherit=inherit))
        elif species is Amoeba:
            if Amoeba.count < Amoeba.maximum:
                amoeba_color = random.choice((50, 170, 800, 1000))
                x = x or random.randrange(100, self.x-100)
                y = y or random.randrange(100, self.y-100)
                self.cells['amoeba'].add(
                    Amoeba(matrix, x, y, color=amoeba_color, identity=identity,
                           inherit=inherit))
        elif species is Ciliate:
            if Ciliate.count < Ciliate.maximum:
                x = x or random.randrange(100, self.x-100)
                y = y or random.randrange(100, self.y-100)
                self.cells['paramecium'].add(
                    Ciliate(matrix, x, y, identity=identity,
                            inherit=inherit))
        elif species in self.newspecies.values():
            if species.count < species.maximum:
                x = x or random.randrange(100, self.x-100)
                y = y or random.randrange(100, self.y-100)
                self.species_group[species.progenitor].add(
                    species(matrix, x, y, identity=identity,
                            inherit=inherit))

    def set_scroll(self, direction=None,
                   field_change=None, scroll='manual'):
        if scroll == 'manual' and self.scroll_step == 2:
            self.scroll_step = 5    #manual
            self.matrix_change_x = numpy.zeros(
                (self.scroll_step,self.dy), 'i')
            self.matrix_change_surface_x = pygame.Surface(
                (self.scroll_step,self.dy))
            self.matrix_change_y = numpy.zeros(
                (self.dx,self.scroll_step), 'i')
            self.matrix_change_surface_y = pygame.Surface(
                (self.dx,self.scroll_step))
        elif scroll == 'auto' and self.scroll_step == 5:
            self.scroll_step = 2    #auto
            self.matrix_change_x = numpy.zeros(
                (self.scroll_step,self.dy), 'i')
            self.matrix_change_surface_x = pygame.Surface(
                (self.scroll_step,self.dy))
            self.matrix_change_y = numpy.zeros(
                (self.dx,self.scroll_step), 'i')
            self.matrix_change_surface_y = pygame.Surface(
                (self.dx,self.scroll_step))
        if field_change == 0:
            if direction in ('north', 'south', 'y'):
                self.scroll_field['y'] = None
            elif direction in ('west', 'east', 'x'):
                self.scroll_field['x'] = None
            return
        field_change = self.scroll_step
        if direction == 'north':
            if self.field_y >= field_change:
                self.scroll_field['y'] = direction
            else:
                self.scroll_field['y'] = None
        elif direction == 'south':
            if self.field_y < self.y-self.dy-field_change:
                self.scroll_field['y'] = direction
            else:
                self.scroll_field['y'] = None
        elif direction == 'west':
            if self.field_x >= field_change:
                self.scroll_field['x'] = direction
            else:
                self.scroll_field['x'] = None
        elif direction == 'east':
            if self.field_x < self.x-self.dx-field_change:
                self.scroll_field['x'] = direction
            else:
                self.scroll_field['x'] = None

    def scroll(self):
        step = self.scroll_step
        if self.scroll_field['y']:
            if (self.scroll_field['y'] == 'north' and
                    self.field_y >= step):
                self.field_y -= step
                self.matrix_change_y = self.nutrient[
                    0+self.field_x:self.dx+self.field_x,
                    0+self.field_y:0+self.field_y+step]
                if self.toxin_presense:
                    self.toxin_change_y = self.toxin[
                        0+self.field_x:self.dx+self.field_x,
                        0+self.field_y:0+self.field_y+step]
                    self.toxin_change_y = numpy.where(
                        self.toxin_change_y>10000,
                        self.toxin_change_y, 0)
                    self.matrix_change_y = numpy.subtract(
                        self.matrix_change_y, self.toxin_change_y)
                pygame.surfarray.blit_array(
                    self.matrix_change_surface_y,
                    self.matrix_change_y)
                self.matrix_surface.blit(
                    self.matrix_surface.copy(), (0,step),
                    (0,0,self.dx,self.dy-step))
                self.matrix_surface.blit(
                    self.matrix_change_surface_y, (0,0))
            elif (self.scroll_field['y'] == 'south' and
                    self.field_y < self.y-self.dy-step):
                self.field_y += step
                self.matrix_change_y = self.nutrient[
                    0+self.field_x:self.dx+self.field_x,
                    self.dy+self.field_y-step:self.dy+self.field_y]
                if self.toxin_presense:
                    self.toxin_change_y = self.toxin[
                        0+self.field_x:self.dx+self.field_x,
                        self.dy+self.field_y-step:self.dy+self.field_y]
                    self.toxin_change_y = numpy.where(
                        self.toxin_change_y>10000,
                        self.toxin_change_y, 0)
                    self.matrix_change_y = numpy.subtract(
                        self.matrix_change_y, self.toxin_change_y)
                pygame.surfarray.blit_array(
                    self.matrix_change_surface_y, self.matrix_change_y)
                self.matrix_surface.blit(
                    self.matrix_surface.copy(), (0,0),
                    (0,step,self.dx,self.dy-step))
                self.matrix_surface.blit(
                    self.matrix_change_surface_y, (0,self.dy-step))
            else:
                self.scroll_field['y'] = None
        if self.scroll_field['x']:
            if self.scroll_field['x'] == 'west' and self.field_x >= step:
                self.field_x -= step
                self.matrix_change_x = self.nutrient[
                    0+self.field_x:0+self.field_x+step,
                    0+self.field_y:self.dy+self.field_y]
                if self.toxin_presense:
                    self.toxin_change_x = self.toxin[
                        0+self.field_x:0+self.field_x+step,
                        0+self.field_y:self.dy+self.field_y]
                    self.toxin_change_x = numpy.where(
                        self.toxin_change_x>10000,
                        self.toxin_change_x, 0)
                    self.matrix_change_x = numpy.subtract(
                        self.matrix_change_x, self.toxin_change_x)
                pygame.surfarray.blit_array(
                    self.matrix_change_surface_x,
                    self.matrix_change_x)
                self.matrix_surface.blit(
                    self.matrix_surface.copy(), (step,0),
                    (0,0,self.dx-step,self.dy))
                self.matrix_surface.blit(
                    self.matrix_change_surface_x, (0,0))
            elif (self.scroll_field['x'] == 'east' and
                    self.field_x < self.x-self.dx-step):
                self.field_x += step
                self.matrix_change_x = self.nutrient[
                    self.dx+self.field_x-step:self.dx+self.field_x,
                    0+self.field_y:self.dy+self.field_y]
                if self.toxin_presense:
                    self.toxin_change_x = self.toxin[
                        self.dx+self.field_x-step:self.dx+self.field_x,
                        0+self.field_y:self.dy+self.field_y]
                    self.toxin_change_x = numpy.where(
                        self.toxin_change_x>10000,
                        self.toxin_change_x, 0)
                    self.matrix_change_x = numpy.subtract(
                        self.matrix_change_x, self.toxin_change_x)
                pygame.surfarray.blit_array(
                    self.matrix_change_surface_x,
                    self.matrix_change_x)
                self.matrix_surface.blit(
                    self.matrix_surface.copy(), (0,0),
                    (step,0,self.dx-step,self.dy))
                self.matrix_surface.blit(
                    self.matrix_change_surface_x, (self.dx-step,0))
            else:
                self.scroll_field['x'] = None
        if self.scroll_field['y'] or self.scroll_field['x']:
            self.screen.blit(self.matrix_surface, (0,0))
            self.update_list.append(self.screen.get_rect())

    def bug_track(self):
        adj = 0
        field_change = self.scroll_step-1
        xx = self.bug_tag.rect.centerx - self.field_x
        yy = self.bug_tag.rect.centery - self.field_y
        if xx < (self.dx//2) - field_change-adj:
            self.set_scroll('west', field_change, scroll='auto')
        elif xx > (self.dx//2) + field_change+adj:
            self.set_scroll('east', field_change, scroll='auto')
        else:
            self.set_scroll('x', 0, scroll='auto')
        if yy < (self.dy//2) - field_change-adj:
            self.set_scroll('north', field_change, scroll='auto')
        elif yy > (self.dy//2) + field_change+adj:
            self.set_scroll('south', field_change, scroll='auto')
        else:
            self.set_scroll('y', 0, scroll='auto')

    def bug_select(self, x, y):
        for species in self.cells:
            for bug in self.cells[species]:
                if bug.rect.collidepoint(
                        x + self.field_x, y + self.field_y):
                    return bug
        return None

    def bug_track_set(self, x, y, follow=True):
        bug = self.bug_select(x,y)
        if bug:
            if bug is not self.bug_tag:
                self.bug_tag = bug
            if follow:
                self.bug_follow = True
            else:
                self.bug_follow = False
            return bug
        else:
            self.bug_track_remove()
            return False

    def bug_track_remove(self, bug=None):
        if self.bug_tag and (bug is self.bug_tag or not bug):
            self.bug_tag = None
            self.bug_follow = False
            self.set_scroll('x', 0)
            self.set_scroll('y', 0)
            self.control.panel.info_active(False)
            self.screen_update = True
            return True
        else:
            return False

    def bug_remove(self, x, y):
        bug = self.bug_select(x,y)
        if bug:
            self.bug_track_remove(bug)
            bug.life = False
            return True
        else:
            return False

    def species_evolve_set(self, x, y):
        bug = self.bug_select(x,y)
        if bug:
            if not bug.species.evolving:
                if bug.gene:   #has genes specified
                    bug.species.evolving = True
                return True
            else:
                bug.species.evolving = 'pause'
                return False
        else:
            return False

    def bug_set_id(self, bug, identity):
        bug.identity = identity
        bug.id_tag = None

    def bug_set_gene(self, bug, gene, setting=0, allele=False):
        if not allele:
            genes = bug.gene.copy()
            genes[gene] = setting
            bug.set_gene(genes)
            return True
        else:
            settings = bug.species.alleles[gene]
            return settings

    def bug_save(self, bug, filename='species.dat', path='data',
                 overwrite=False):
        try:
            bug_species_id = self.species.index(bug.species)    #save [Algae, Bacterium, Paramecium, Amoeba, Ciliate]
        except ValueError:
            bug_species_id = self.species.index(bug.species.progenitor)     #save newspecies
        bug_id = bug.identity
        bug_gene = bug.gene.copy()
        bug_info = bug_species_id, bug_id, bug_gene
        if path:
            fn = os.path.join(path, filename)
        check = os.path.exists(fn)
        if check and not overwrite:
            return False
        try:
            bug_file = open(fn, 'wb')
        except IOError:
            return False
        else:
            pickle.dump(bug_info, bug_file)
            bug_file.close()
            return fn

    def bug_load(self, filename='species.dat', path='data',
                 new_species=True):
        try:
            if path:
                fn = os.path.join(path, filename)
            check = os.path.exists(fn)
            if not check:
                return False
            bug_file = open(fn, 'rb')
            bug_info = pickle.load(bug_file)
            bug_file.close()
            bug_species_id, bug_id, bug_gene = bug_info
            bug_species = self.species[bug_species_id]
            img = filename[:-4] + '.png'    #load png of same name if present
            if path:
                imgfile = os.path.join(path, img)
            check = os.path.exists(imgfile)
            if not check:
                img = None
        except IOError:
            print("Load error")
            return False
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if new_species:     #load as newspecies
            species = filename[:-4]
            if (species not in self.newspecies or
                (species in self.newspecies and
                 not issubclass(self.newspecies[species], bug_species))):     #create newspecies class
                newSpecies = self.create_species(
                    bug_species, mouse_x+self.field_x, mouse_y+self.field_y,
                    cell_image=img, frames=None, identity=bug_id,
                    inherit=bug_gene, mutation_rate=0)
                self.species_group[bug_species].add(newSpecies)
                if species in self.newspecies:   #rename if already present, in case saved file was changed
                    key = species
                    while key in self.newspecies:
                        key = key + '_'
                    self.newspecies[key] = self.newspecies[species]
                    del self.newspecies[species]
                self.newspecies[species] = newSpecies.species
            else:   #add instance to created newspecies class
                if (self.newspecies[species].count <
                        self.newspecies[species].maximum):
                    matrix = self
                    self.species_group[bug_species].add(
                        self.newspecies[species](matrix,
                        mouse_x+self.field_x, mouse_y+self.field_y,
                        identity=bug_id, inherit=bug_gene, mutation_rate=0))

    def create_species(self, Progenitor, x, y, cell_image=None, frames=2,
                       identity=None, inherit=None, mutation_rate=0):
        class NewSpecies(Progenitor):
            image = None
            count = 0
            minimum = Progenitor.minimum
            maximum = Progenitor.maximum
            id = 0
            evolving = False
            gene = Progenitor.gene
            alleles = Progenitor.alleles
            gene_info = Progenitor.gene_info
            progenitor = Progenitor
            image_file = None
            def __init__(self, matrix, x, y, cell_image=None, frames=None,
                         identity=None, inherit=None, mutation_rate=0.5):
                self.species = self.__class__
                if not self.species.image_file:
                    progenitors = {Algae: ('algae.png',1),
                                   Bacterium: ('bacterium.png',1),
                                   Paramecium: ('paramecium.png',2),
                                   Ciliate: ('ciliate.png',2),
                                   Amoeba: (None,1)}
                    if not cell_image:
                        cell_image, frames = progenitors[Progenitor]
                        self.species.image_file = cell_image, frames
                    else:
                        frames = progenitors[Progenitor][1]
                        self.species.image_file = cell_image, frames
                else:
                    cell_image, frames = self.species.image_file
                Progenitor.__init__(self, matrix, x, y, cell_image, frames,
                                    identity, inherit, mutation_rate)
        matrix = self
        newSpecies = NewSpecies(matrix, x, y, cell_image, frames,
                                identity, inherit, mutation_rate)
        return newSpecies

    def bug_trace_update(self):
        self.trace_update += 1
        if self.trace_update > 2:   #update trace decay at rate that gradient detectable over cell
            trace_view = self.trace[
                (self.dx*self.trace_x):self.dx+(self.dx*self.trace_x),
                (self.dy*self.trace_y):self.dy+(self.dy*self.trace_y)]
            trace_view[trace_view>9] -= 10
            self.trace_update = 0
            self.trace_x += 1
            if self.trace_x > 2:
                self.trace_x = 0
                self.trace_y += 1
            if self.trace_y > 2:
                self.trace_x = 0
                self.trace_y = 0
            if self.trace_display:
                trace_temp = numpy.array(
                    self.trace[self.field_x:self.dx+self.field_x,
                               self.field_y:self.dy+self.field_y], 'i')
                pygame.surfarray.blit_array(self.screen, trace_temp)
                self.update_list.append(self.screen.get_rect())

    def set_evolution(self, setting='Toggle'):
        if setting == 'Toggle':
            self.evolution = not self.evolution
        elif setting in (True,False):
            self.evolution = setting

    def set_tag_display(self, setting='Toggle'):
        if setting == 'Toggle':
            self.tag_display = not self.tag_display
        elif setting in (True,False):
            self.tag_display = setting

    def set_screen_update(self):
        self.screen_update = True

    def zoom_activate(self, display=True, power=1, zoom_reset=True):
        if display:
            if not self.zoom_set:
                if (not self.bug_follow and
                        not self.scroll_field['x'] and
                        not self.scroll_field['y']):
                    pygame.mouse.set_visible(False)
                    self.zoom_set = True
            else:
                if power == 1:
                    if self.zoom_power < 10:
                        self.zoom_power += power
                    else:
                        if zoom_reset:
                            self.zoom_power = 2
                elif power == -1:
                    if self.zoom_power > 2:
                        self.zoom_power += power
        else:
            if self.zoom_set:
                pygame.mouse.set_visible(True)
                self.zoom_set = False
                self.zoom_init = False
                self.screen_update = True     #surface_clear instead?

    def field_zoom(self, action):
        "Microscopic zoom centered on mouse pointer"
        if action == 'clear':
            self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
            if self.mouse_x < 100:
                self.mouse_x = 100
            elif self.mouse_x > self.dx - 100:
                self.mouse_x = self.dx - 100
            if self.mouse_y < 100:
                self.mouse_y = 100
            elif self.mouse_y > self.dy - 100:
                self.mouse_y = self.dy - 100
            if not self.zoom_init:
                self.mouse_x_pre = self.mouse_x
                self.mouse_y_pre = self.mouse_y
                self.surface_clear = self.screen.subsurface(
                    (self.mouse_x_pre-100, self.mouse_y_pre-100,
                    200,200)).copy()
                self.zoom_init = True
            clear_rect = self.screen.blit(
                self.surface_clear, (self.mouse_x_pre-100,
                                     self.mouse_y_pre-100))
            self.update_list.append(clear_rect)
        elif action == 'activate':
            self.surface_clear = self.screen.subsurface(
                (self.mouse_x-100,self.mouse_y-100,200,200)).copy()
            clear_rect = self.surface_clear.get_rect(
                center=(self.mouse_x,self.mouse_y))
            self.zoom_surface = self.screen.subsurface(
                (self.mouse_x-100//self.zoom_power,
                 self.mouse_y-100//self.zoom_power,
                 200//self.zoom_power,
                 200//self.zoom_power)).copy()
            self.zoom_surface = pygame.transform.smoothscale(
                self.zoom_surface, (200,200))
            pygame.draw.rect(
                self.zoom_surface, (70,130,180), (0,0,200,200), 1)
            zoom_rect = self.zoom_surface.get_rect(center=(self.mouse_x,
                                                           self.mouse_y))
            zoom_rect = self.screen.blit(
                self.zoom_surface, (self.mouse_x-100,
                                    self.mouse_y-100))
            self.update_list.append(zoom_rect)
            self.mouse_x_pre = self.mouse_x
            self.mouse_y_pre = self.mouse_y

    def display(self):
        if self.screen_update:   #only update at intervals
            if not self.screen_update_count:
                self.matrixx = self.nutrient[
                    0+self.field_x:self.dx+self.field_x,
                    0+self.field_y:self.dy+self.field_y]    #Matrix     #overlap?
                if self.toxin_presense:
                    self.toxinx = numpy.array(
                        self.toxin[0+self.field_x:self.dx+self.field_x,
                        0+self.field_y:self.dy+self.field_y])  #require numpy.array or slice?
                    self.toxinx = numpy.where(
                        self.toxinx>10000, self.toxinx, 0)
                    self.matrixx = numpy.subtract(
                        self.matrixx, self.toxinx)
                pygame.surfarray.blit_array(
                    self.matrix_surface, self.matrixx)
            self.screen.blit(self.matrix_surface, (0,0))
            self.update_list.append(self.screen.get_rect())
            self.screen_update = False
        self.screen_update_count += 1
        if self.screen_update_count > 1000:    #change update to compensate for computer load
            self.screen_update_count = 0       #during update, zoom blinks screen...
            self.screen_update = True

    def creature_inview(self, creature):
        if creature in self.cells['creatures']:
            return True
        else:
            return False

    def creatures_update(self):
        "Update all creatures and populate update_list of creatures on screen for display"
        self.cells['algae'].update()
        self.cells['bacterium'].update()
        self.cells['amoeba'].update()
        self.cells['paramecium'].update()
        #update creatures in view
        self.cells['creatures'].empty()     #have bug check and report if onscreen?
        #algae update
        for bug in self.cells['algae']:
            if bug.life_check():
                if (bug.rect.centerx > self.field_x-self.overlap//5 and
                    bug.rect.centerx < self.dx+self.field_x+self.overlap//5 and
                    bug.rect.centery > self.field_y-self.overlap//5 and
                    bug.rect.centery < self.dy+self.field_y+self.overlap//5):
                    self.cells['creatures'].add(bug)    #draw cells onscreen, with display overlap/5
            else:
                self.bug_track_remove(bug)
                self.cells['algae'].remove(bug)
        #bacterium update
        for bug in self.cells['bacterium']:
            if bug.life_check():
                if (bug.rect.centerx > self.field_x-self.overlap//5 and
                    bug.rect.centerx < self.dx+self.field_x+self.overlap//5 and
                    bug.rect.centery > self.field_y-self.overlap//5 and
                    bug.rect.centery < self.dy+self.field_y+self.overlap//5):
                    self.cells['creatures'].add(bug)      #draw cells onscreen, with display overlap/5
            else:
                self.bug_track_remove(bug)
                self.cells['bacterium'].remove(bug)
        #amoeba update
        for bug in self.cells['amoeba']:
            if bug.life_check():
                if (bug.rect.centerx > self.field_x-self.overlap and
                    bug.rect.centerx < self.dx+self.field_x+self.overlap and
                    bug.rect.centery > self.field_y-self.overlap and
                    bug.rect.centery < self.dy+self.field_y+self.overlap):
                    self.cells['creatures'].add(bug)
            else:
                self.bug_track_remove(bug)
                self.cells['amoeba'].remove(bug)
        #paramecium update
        for bug in self.cells['paramecium']:
            if bug.life_check():
                if (bug.rect.centerx > self.field_x-self.overlap and
                    bug.rect.centerx < self.dx+self.field_x+self.overlap and
                    bug.rect.centery > self.field_y-self.overlap and
                    bug.rect.centery < self.dy+self.field_y+self.overlap):
                    self.cells['creatures'].add(bug)    #draw cells onscreen, with display overlap
            else:
                self.bug_track_remove(bug)
                self.cells['paramecium'].remove(bug)
        #Display label
        if self.bug_tag and not self.bug_follow:
            if self.tag_display:
                self.bug_tag.display_tag()
            else:
                self.bug_tag.display_tag(False)
        if self.evolution:
            for bug in self.cells['creatures']:
                if bug.species.evolving:
                    if self.tag_display:
                        bug.display_tag()
                    else:
                        bug.display_tag(False)
        #Update creatures currently on screen
        for bug in self.cells['creatures']:       #adjust display location
            bug.rect.centerx -= self.field_x
            bug.rect.centery -= self.field_y
        self.cells['creatures'].clear(self.screen_microbe,
                                      self.matrix_surface)
        self.update_list.extend(
            self.cells['creatures'].draw(self.screen_microbe))
        for bug in self.cells['creatures']:       #restore location
            bug.rect.centerx += self.field_x
            bug.rect.centery += self.field_y
        self.bug_trace_update()

    def update(self):
        self.update_list = []
        self.display()
        if self.scroll_field['x'] or self.scroll_field['y']:
            self.scroll()
        if self.bug_tag and self.bug_follow:
            self.bug_track()
        self.control.panel_group.clear(self.screen,
                                       self.matrix_surface)
        if not self.zoom_set:
            self.creatures_update()
        else:
            self.field_zoom('clear')
            self.creatures_update()
            self.field_zoom('activate')

