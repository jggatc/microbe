"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import pygame
import os
import interphase      #interface control
from interface import MatrixInterface


class Control(object):
    """
    User control.
    """

    def __init__(self, matrix):
        self.matrix = matrix
        self.matrix.control = self
        pygame.key.set_repeat(100,10)
        self.tool = None
        self.direction = {pygame.K_UP:'north', pygame.K_DOWN:'south', pygame.K_LEFT:'west', pygame.K_RIGHT:'east'}
        self.mouse_x = 0
        self.mouse_y = 0
        self.quit = False
        self.scroll = False
        self.scroll_x = False
        self.scroll_y = False
        self.scroll_timer = 0
        self.scroll_edge = False
        self.compass_display = False
        self.compass_use = True
        x, y = self.matrix.dx-40, self.matrix.dy-40
        self.compass_rose = pygame.Rect(x-35,y-35,72,72)
        self.compass_rose_bud = pygame.Rect(0,0,10,10)
        self.compass_rose_bud.center = (x,y)
        self.trace1 = [(x-35,y),(x-10,y-10),(x,y-35),(x+10,y-10),(x+35,y),(x+10,y+10),(x,y+35),(x-10,y+10)]
        self.trace2 = [(x-20,y-20),(x,y-10),(x+20,y-20),(x+10,y),(x+20,y+20),(x,y+10),(x-20,y+20),(x-10,y)]
        n = pygame.Rect((0,0),(20,30))
        s = pygame.Rect((0,0),(20,30))
        w = pygame.Rect((0,0),(30,20))
        e = pygame.Rect((0,0),(30,20))
        nw = pygame.Rect((0,0),(20,20))
        ne = pygame.Rect((0,0),(20,20))
        sw = pygame.Rect((0,0),(20,20))
        se = pygame.Rect((0,0),(20,20))
        offset=10
        n.center=(x,y-35+offset)
        s.center=(x,y+35-offset)
        w.center=(x-35+offset,y)
        e.center=(x+35-offset,y)
        nw.center=(x-20+offset,y-20+offset)
        ne.center=(x+20-offset,y-20+offset)
        sw.center=(x-20+offset,y+20-offset)
        se.center=(x+20-offset,y+20-offset)
        self.dir = {'n':n, 's':s, 'w':w, 'e':e, 'nw':nw, 'ne':ne, 'sw':sw, 'se':se}
        self.clock = pygame.time.Clock()
        self.pause = False
        self.compass_folding = False
        self.fold_step = 0
        self.compass_surface = pygame.Surface((50,50))
        self.compass_surface.fill((0,0,0))
        self.panel, self.panel_group = self.define_controls()
        self.panel_displayed = False     #when displayed, ignore click in panel area
        self.newspecies = None  #filename of saved species
        self.tool_activated = False
        self.tool_timer = 0
        self.tool_timer_i = 0

    def define_controls(self):
        panel = MatrixInterface(self.matrix,self)
        panel_group = pygame.sprite.RenderUpdates(panel)
        return panel, panel_group

    def use_tool(self):
        self.tool_timer += (pygame.time.get_ticks()-self.tool_timer_i)
        if self.tool_timer < 250:
            return
        else:
            self.tool_timer = 0
            self.tool_timer_i = pygame.time.get_ticks()
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        if self.tool == 'Add_Gradient':
            self.matrix.set_gradient(self.mouse_x, self.mouse_y, gradient_type='Nutrient')
        elif self.tool == 'Add_Toxin':
            self.matrix.set_gradient(self.mouse_x, self.mouse_y, gradient_type='Toxin')
        elif self.tool == 'Add_Algae':
            self.matrix.add_creature('Algae', self.mouse_x, self.mouse_y)
        elif self.tool == 'Add_Bacterium':
            self.matrix.add_creature('Bacterium', self.mouse_x, self.mouse_y)
        elif self.tool == 'Add_Paramecium':
            self.matrix.add_creature('Paramecium', self.mouse_x, self.mouse_y)
        elif self.tool == 'Add_Amoeba':
            self.matrix.add_creature('Amoeba', self.mouse_x, self.mouse_y)
        elif self.tool == 'Add_Ciliate':
            self.matrix.add_creature('Ciliate', self.mouse_x, self.mouse_y)
        elif self.tool == 'Track':
            bug_tag = self.matrix.bug_track_set(self.mouse_x, self.mouse_y, follow=True)
            self.panel.info_active(True)
            self.panel.initialize = False
            self.tool_activated = False
        elif self.tool == 'Tag':
            bug_tag = self.matrix.bug_track_set(self.mouse_x, self.mouse_y, follow=False)
            self.panel.info_active(True)
            self.panel.initialize = False
            self.tool_activated = False
        elif self.tool == 'Evolve':
            self.matrix.species_evolve_set(self.mouse_x, self.mouse_y)
            self.tool_activated = False
        elif self.tool == 'Magnify':
            self.matrix.zoom_activate(True)
            self.tool_activated = False
        elif self.tool == 'Load':
            if self.newspecies:
                self.matrix.bug_load(self.newspecies)   #set bug_load tool

    def check_events(self):
        "Monitor keyboard input"
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and not self.panel_displayed:
                mousex, mousey = event.pos
                if event.button == 1 and not self.matrix.zoom_set:
                    if not pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        if self.compass_display:
                            if self.compass_rose_bud.collidepoint(mousex,mousey):
                                self.panel.set_moveable('Fixed')
                                self.panel.set_panel_display(True)
                        else:
                            self.tool_activated = True
                            self.tool_timer = 250
                    else:   #select evolving species
                        self.matrix.species_evolve_set(mousex, mousey)
                elif event.button == 2:
                    if not self.matrix.zoom_set:
                        if not self.matrix.bug_follow and not self.matrix.scroll_field['x'] and not self.matrix.scroll_field['y']:
                            self.matrix.zoom_activate(True)
                    else:
                        self.matrix.zoom_activate(False)
                elif event.button == 3:
                    if not self.matrix.zoom_set:
                        self.mouse_x, self.mouse_y = event.pos
                        mod = pygame.key.get_mods()
                        if not mod:
                            bug_tag = self.matrix.bug_track_set(self.mouse_x, self.mouse_y, follow=True)
                            self.panel.info_active(True)
                            self.panel.initialize = False
                        elif (mod & pygame.KMOD_CTRL) and (mod & pygame.KMOD_SHIFT):
                            bug_tag = False
                            self.matrix.bug_remove(self.mouse_x, self.mouse_y)
                        elif mod & pygame.KMOD_SHIFT:
                            bug_tag = self.matrix.bug_track_set(self.mouse_x, self.mouse_y, follow=False)
                            self.panel.info_active(True)
                            self.panel.initialize = False
                        self.panel.bug_tag = None
                elif event.button == 4:
                    if self.matrix.zoom_set:
                        self.matrix.zoom_activate(power=1, zoom_reset=False)
                    else:
                        self.matrix.zoom_activate(True)
                elif event.button == 5:
                    if self.matrix.zoom_set:
                        self.matrix.zoom_activate(power=-1)
                    else:
                        self.matrix.zoom_activate(True)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.tool_activated = False
            elif event.type == pygame.MOUSEMOTION:
                if not self.matrix.bug_follow and not self.scroll:
                    mousex, mousey = event.pos
                    if self.compass_use and not self.matrix.zoom_set:
                        if self.compass_rose.collidepoint(mousex,mousey):
                            self.compass_display = True
                        else:
                            self.compass_display = False
                    if self.compass_display and not self.scroll_edge and not self.matrix.zoom_set:
                        if self.dir['n'].collidepoint(mousex,mousey) or self.dir['nw'].collidepoint(mousex,mousey) or self.dir['ne'].collidepoint(mousex,mousey):
                            self.matrix.set_scroll('north', 5)
                            self.scroll_y = True
                        elif self.dir['s'].collidepoint(mousex,mousey) or self.dir['sw'].collidepoint(mousex,mousey) or self.dir['se'].collidepoint(mousex,mousey):
                            self.matrix.set_scroll('south', 5)
                            self.scroll_y = True
                        else:
                            self.matrix.set_scroll('y', 0)
                            self.scroll_y = False
                        if self.dir['w'].collidepoint(mousex,mousey) or self.dir['nw'].collidepoint(mousex,mousey) or self.dir['sw'].collidepoint(mousex,mousey):
                            self.matrix.set_scroll('west', 5)
                            self.scroll_x = True
                        elif self.dir['e'].collidepoint(mousex,mousey) or self.dir['ne'].collidepoint(mousex,mousey) or self.dir['se'].collidepoint(mousex,mousey):
                            self.matrix.set_scroll('east', 5)
                            self.scroll_x = True
                        else:
                            self.matrix.set_scroll('x', 0)
                            self.scroll_x = False
                        if self.compass_rose_bud.collidepoint(mousex,mousey):
                            self.matrix.set_scroll('y', 0)
                            self.matrix.set_scroll('x', 0)
                            self.scroll_y = False
                            self.scroll_x = False
                    else:
                        self.matrix.set_scroll('y', 0)
                        self.matrix.set_scroll('x', 0)
                        self.scroll_y = False
                        self.scroll_x = False
                    if self.scroll_edge and not self.matrix.zoom_set:
                        if mousey < 20:
                            self.matrix.set_scroll('north', 5)
                            self.scroll_y = True
                        elif mousey > self.matrix.dy - 20:
                            self.matrix.set_scroll('south', 5)
                            self.scroll_y = True
                        else:
                            self.matrix.set_scroll('y', 0)
                            self.scroll_y = False
                        if mousex < 20:
                            self.matrix.set_scroll('west', 5)
                            self.scroll_x = True
                        elif mousex > self.matrix.dx - 20:
                            self.matrix.set_scroll('east', 5)
                            self.scroll_x = True
                        else:
                            self.matrix.set_scroll('x', 0)
                            self.scroll_x = False
                        if self.scroll_x or self.scroll_y:
                            pygame.time.set_timer(pygame.USEREVENT,10)
                        else:
                            pygame.time.set_timer(pygame.USEREVENT,0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    self.tool = 'Add_Gradient'
                elif event.key == pygame.K_t:
                    self.tool = 'Add_Toxin'
                elif event.key == pygame.K_b:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.matrix.add_creature('Bacterium')
                    else:
                        self.tool = 'Add_Bacterium'
                elif event.key == pygame.K_v:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.matrix.add_creature('Algae')
                    else:
                        self.tool = 'Add_Algae'
                elif event.key == pygame.K_p:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.matrix.add_creature('Paramecium')
                    else:
                        self.tool = 'Add_Paramecium'
                elif event.key == pygame.K_a:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.matrix.add_creature('Amoeba')
                    else:
                        self.tool = 'Add_Amoeba'
                elif event.key == pygame.K_o:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        self.matrix.add_creature('Ciliate')
                    else:
                        self.tool = 'Add_Ciliate'
                elif event.key == pygame.K_e:  #toggle evolution mode
                    self.matrix.set_evolution()
                    self.panel.set_panel_value('Evolution Mode')
                    if self.matrix.evolution:
                        self.panel.info_active(True)
                    else:
                        self.panel.info_active(False)
                elif event.key == pygame.K_d:  #toggle tag display
                    self.matrix.set_tag_display()
                    self.panel.set_panel_value('Tag')
                elif event.key == pygame.K_i:  #interface panel toggle
                    self.panel.set_moveable('Fixed')
                    self.panel.set_panel_display(True)
                elif event.key == pygame.K_c:     #Use compass
                    if not self.compass_folding:
                        self.compass_use = not self.compass_use
                        self.compass_folding = True
                        self.panel.set_panel_value('Compass')
                    if self.compass_use:
                        self.scroll_edge = False
                    else:
                        self.scroll_edge = True
                    self.matrix.set_screen_update()
                elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    if not self.scroll_x and not self.scroll_y:
                        if not self.scroll:
                            if self.matrix.zoom_set:
                                self.matrix.zoom_activate(False)
                            if self.matrix.bug_follow:
                                self.matrix.bug_track_remove()
                            self.scroll = True
                        direction = self.direction[event.key]
                        self.matrix.set_scroll(direction, 5)
                elif event.key == pygame.K_x:
                    self.matrix.bug_track_remove()
                elif event.key == pygame.K_z:
                    if not (pygame.key.get_mods() & pygame.KMOD_SHIFT):
                        self.matrix.zoom_activate(True)
                    else:
                        self.matrix.zoom_activate(False)
                elif event.key == pygame.K_q:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.panel.quit(cmd='initialize')
                elif event.key in (pygame.K_y, pygame.K_n):
                    if self.panel.input_mode == 'Quit':
                        if event.key == pygame.K_y:
                            self.quit = True
                        elif event.key == pygame.K_n:
                            self.panel.quit(cmd='cancel')
                elif event.key == pygame.K_TAB:
                    self.pause = True
                elif event.key == pygame.K_ESCAPE:
                    self.matrix.bug_track_remove()
                    self.matrix.zoom_activate(False)
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    direction = self.direction[event.key]
                    self.matrix.set_scroll(direction, 0)
                    self.scroll = False
            elif event.type == pygame.USEREVENT:
                if ( self.scroll_x or self.scroll_y ) and not pygame.mouse.get_focused():
                    pygame.time.set_timer(pygame.USEREVENT,0)
                    self.matrix.set_scroll('x', 0)
                    self.matrix.set_scroll('y', 0)
            elif event.type == pygame.QUIT:
                pygame.quit()
                self.quit = True

    def compass(self):
        def fold(point,step,center=self.compass_rose_bud.center):
            point = ( int(point[0]+(center[0]-point[0])*step),int(point[1]+(center[1]-point[1])*step) )
            return point
        if self.compass_use and not self.compass_folding:
            compass1 = self.trace1
            compass2 = self.trace2
            update = False
        elif self.compass_folding:
            update = True
            if self.fold_step >= 0:
                self.fold_step += 0.1
                step = self.fold_step
                if self.fold_step >= 0.9:
                    self.fold_step = -1.0
                    self.compass_folding = False
            else:
                step = abs(self.fold_step)
                self.fold_step += 0.1
                if self.fold_step >= -0.1:
                    self.fold_step = 0
                    self.compass_folding = False
            compass1 = self.trace1[:]
            compass2 = self.trace2[:]
            for point,value in enumerate(self.trace1):
                compass1[point] = fold(value,step)
            for point,value in enumerate(self.trace2):
                compass2[point] = fold(value,step)
        else:
            return False
        if self.compass_display:
            color1 = 60,120,200
            color2 = 40,80,120
        else:
            color1 = 15,30,50
            color2 = 10,20,30
        compass_axis1 = pygame.draw.aalines(self.matrix.screen,color1,True,compass1,0)
        compass_axis2 = pygame.draw.aalines(self.matrix.screen,color2,True,compass2,0)
        self.matrix.update_list.append(compass_axis1)
        self.matrix.update_list.append(compass_axis2)
        if update:
            self.matrix.screen_update = True
        return True

    def pause_events(self):
        while self.pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB or event.key == pygame.K_ESCAPE:
                        self.pause = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    self.quit = True
                    self.pause = False

    def update(self):
        self.panel_group.update()
        panel_update = self.panel_group.draw(self.matrix.screen)
        self.matrix.update_list.extend(panel_update)
        self.compass()
        self.check_events()
        if self.tool_activated:
            self.use_tool()
        if self.pause:
            self.pause_events()
        self.clock.tick(40)

