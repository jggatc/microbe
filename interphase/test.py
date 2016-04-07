#!/usr/bin/env python
from __future__ import division

"""
Interphase Demo

Interphase Module
Download Site: http://gatc.ca
"""


import interphase
import pygame
import random


class InterfaceDemo(interphase.Interface):
    """
    Interphase interface.
    """
    def __init__(self):
        self.pygame_initiate()
        interphase.Interface.__init__(self, position=(250,450), color=(43,50,58), size=(350,100),
            moveable=False, position_offset=(0,95), control_minsize=(25,25), control_size='auto',
            font_color=(175,180,185), tips_fontcolor=(175,180,185))
        self.interfacedemo_initiate()

    def add_controls(self):
        """Add interface controls."""
        Control_list = ['Control 1', 'Control 2', 'Layout', 'Puzzle', 'Exit']
        Control_tip = ['Control Panel 1', 'Control Panel 2', 'Control Placement', 'Sliding Control', 'Click to Exit']
        Control_link = [ ['Select1'], ['Setting1', 'Setting2', 'Files'], ['Moveable'], ['Puzzle'], ['Panic'] ]
        self.add(
            identity = 'Control',
            control_type = 'function_select',
            position = (50,50),
            size = 'min',
            control_list = Control_list,
            tip_list = Control_tip,
            link = Control_link,
            link_activated = True,
            control_outline = True,
            event = True)
        self.add(
            identity = 'Select1',
            control_type = 'function_toggle',
            position = (150,50),
            size = (30,30),
            control_list = ['ON', 'OFF'],
            link = [ ['Select2'], [] ])
        self.add(
            identity = 'Select2',
            control_type = 'control_toggle',
            position = (200,50),
            size = (30,30),
            control_list = ['G', 'A', 'T', 'C'])
        self.add(
            identity = 'Setting1',
            control_type = 'control_select',
            position = (230,30),
            size = (30,30),
            control_list = ['__alphanumeric'],
            loop = True)
        self.add(
            identity = 'Setting2',
            control_type = 'control_select',
            position = (230,75),
            size = (30,30),
            control_list = ['__numeric', (0,42)])
        self.add(
            identity = 'Files',
            control_type = 'control_select',
            position = (140,50),
            size = 'auto_width',
            control_list = ['__filelist', '', '', 'py'])
        self.add(
            identity = '__Fix',
            control_type = 'control_toggle',
            position = (295,15),
            color = (0,20,30),
            font_color = (0,120,160),
            control_list = ['!'],
            control_outline = True)
        self.add(
            identity = '__Link',
            control_type = 'control_toggle',
            position = (315,15),
            color = (0,20,30),
            font_color = (0,120,160),
            control_list = ['*'],
            control_outline = True)
        self.add(
            identity = '__Help',
            control_type = 'control_toggle',
            position = (335,15),
            color = (0,20,30),
            font_color = (0,120,160),
            control_list = ['?'],
            control_outline = True)
        self.add(
            identity = '__Position',
            control_type = 'label',
            position = (335,98),
            control_list = [])
        self.add(
            identity = 'Moveable',
            control_type = 'control_toggle',
            position = (175,50),
            size = (40,40),
            control_list = ['Move'],
            tip_list = ['Moveable Control'],
            label_display = False)
        self.add(
            identity = 'Previous',
            control_type = 'control_toggle',
            position = (240,50),
            size = (25,25),
            control_list = ['<'],
            label_display = False,
            active = False)
        self.add(
            identity = 'Next',
            control_type = 'control_toggle',
            position = (265,50),
            size = (25,25),
            control_list = ['>'],
            label_display = False,
            active = False)
        self.add(
            identity = 'Panic',
            control_type = 'control_toggle',
            position = (175,50),
            size = (40,40),
            control_list = ['Panic'],
            tip_list = ["Don't press"],
            label_display = False)
        self.add(
            identity = 'Puzzle',
            control_type = 'control_toggle',
            position = (175,50),
            size = (40,40),
            control_list = ['Start', 'Stop'],
            tip_list = ['Start Puzzle', 'Stop Puzzle'],
            label_display = False)

    def pygame_initiate(self):
        """Initiate pygame."""
        pygame.display.init()   #pygame.init()
        pygame.display.set_caption('Interphase')
        self.screen = pygame.display.set_mode((500,500))
        self.background = pygame.Surface((500,500))
        self.screen_doc = pygame.Surface((500,400))
        self.clock = pygame.time.Clock()
        pygame.display.flip()

    def interfacedemo_initiate(self):
        """Initiate demo."""
        self.puzzle = False
        self.puzzle_init = False
        self.puzzle_panel = None
        self.puzzle_interface = None
        self.doc_initialized = False
        self.doc_browse = False
        self.doc = 0
        self.doc_place = 0
        self.doc_change = False
        self.panic = False
        self.panic_time = 0
        self.panic_toggle = False
        self.dont_panic = False
        self.set_moveable(True)

    def pygame_check(self):
        """Check user input."""
        terminate = False
        for event in pygame.event.get():
            if event.type == interphase.EVENT['controlselect']:
                if event.state.control == 'Control' and event.state.button == 'Control':
                    if event.state.value == 'Exit':
                        if not self.panic:
                            terminate = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate = True
            elif event.type == pygame.QUIT:
                terminate = True
        self.clock.tick(40)
        return terminate

    def documentation(self, action='read'):
        """Interphase documentation."""
        if not self.doc_initialized:
            self.doc_info = interphase.Text(self.screen_doc)
            self.doc_info.set_font_size(12)
            self.doc_info.set_font_color((175,180,185))
            self.interface_doc = []
            for doc in (interphase.__doc__, interphase.Interface.__doc__, interphase.InterfaceControl.__doc__):
                document = doc.splitlines()
                document = [line.strip() for line in document]
                page = []
                null_line = 0
                for line in document:
                    if not line:
                        null_line += 1
                    else:
                        null_line = 0
                    if null_line < 2:
                        page.append(line)
                    else:
                        self.interface_doc.append(page)
                        page = []
                        null_line = 0
                if page:
                    self.interface_doc.append(page)
            self.doc_initialized = True
        page_length = 25
        if action == 'initialize':
            self.doc = 0
            self.doc_place = 0
            self.doc_change = True
        elif action == 'Previous':
            if self.doc_place > 0:
                self.doc_place -= page_length
                if self.doc_place < 0:
                    self.doc_place = 0
            else:
                if self.doc > 0:
                    self.doc -= 1
                    self.doc_place = 0
                    adjust = False
                    while not adjust:
                        if self.doc_place + page_length < len(self.interface_doc[self.doc])-1:
                            self.doc_place += page_length
                        else:
                            adjust = True
            self.doc_change = True
        elif action == 'Next':
            if self.doc_place + page_length < len(self.interface_doc[self.doc])-1:
                self.doc_place += page_length
            else:
                if self.doc < len(self.interface_doc)-1:
                    self.doc += 1
                    self.doc_place = 0
            self.doc_change = True
        elif action == 'Esc':
            self.screen_doc.fill((0,0,0))
            rect = self.screen.blit(self.screen_doc, (0,0))
            pygame.display.update(rect)
            return
        if self.doc_change:
            count = 10
            lines = 0
            self.screen_doc.fill((0,0,0))
            for line in self.interface_doc[self.doc][self.doc_place:]:
                self.doc_info.add(line)
                self.doc_info.set_position((10,count))
                surface = self.doc_info()
                count += 15
                lines += 1
                if lines == page_length:
                    lines = 0
                    count = 5
                    break
            self.doc_change = False
        rect = self.screen.blit(self.screen_doc, (0,0))
        pygame.display.update(rect)

    def update(self):
        """
        Interface update returns state object.

        State Object
            panel:              Interface panel
            controls:           Interface controls
            panel_active        Panel active
            panel_interact:     Pointer interface interact
            control_interact:   Pointer control interact
            button_interact:    Pointer button interact
            control:            Control selected
            button:             Button selected
            value:              Control value
            values:             Panel control values
        """
        state = interphase.Interface.update(self)
        if state.control:
            if state.control == 'Select1':
                if state.value == 'ON':
                    self.set_panel_image()
                    self.set_control_image()
                    self.set_button_image()
                elif state.value == 'OFF':
                    self.set_panel_image('none')
                    self.set_control_image('none')
                    self.set_button_image('none')
            elif state.control == '__Fix':
                self.set_moveable()
            elif state.control == '__Link':
                state.controls['Control'].set_link_activated()
            elif state.control == 'Moveable':
                self.set_control_moveable()
                if self.is_control_moveable():
                    self.set_control_move(state.control, mouse_visible=False)
                    self.disable_control('Control', '__Fix', '__Link', '__Help')
                else:
                    state.controls[self.get_control_move()].set_tip(['Moveable Control'])
                    self.set_control_move(None)
                    self.enable_control('Control', '__Fix', '__Link', '__Help')
            elif state.control == 'Puzzle':
                if not self.puzzle:
                    self.puzzle = True
                    state.controls['Control'].set_active(False)
                else:
                    self.puzzle_panel = None
                    self.puzzle_init = False
                    self.puzzle = False
                    state.controls['Control'].set_active(True)
                    self.screen.blit(self.background, (0,0))
                    pygame.display.flip()
            elif state.control == '__Help':
                if state.controls['Panic'].is_active():
                    if state.controls['Panic'].get_value() == 'Panic':
                        state.controls['Panic'].set_list(["Don't Panic"])
                        state.controls['Panic'].set_value("Don't Panic")
                        state.controls['Panic'].set_tip("Don't Panic","Press for help")
                        self.dont_panic = True
                else:
                    self.set_info_display()
                    self.set_label_display()
                    self.set_tips_display()
                    self.set_pointer_interact()
                    if state.controls['__Position'].get_value():
                        state.controls['__Position'].set_value('')
            elif state.control == 'Panic':
                if state.value == 'Panic':
                    if not self.panic:
                        self.panic = True
                        self.panic_time = 20
                        self.disable_control('__Fix', '__Link', '__Help')
                        self.set_moveable(False)
                    else:
                        if not self.panic_time:
                            self.panic_time = 20
                            state.controls['Panic'].set_list(["Don't Panic"])
                            state.controls['Panic'].set_tip("Don't Panic","Don't press!!!")
                            self.panic = False
                else:
                    if not self.panic_time:
                        if not self.dont_panic:
                            if not self.is_moveable():
                                self.move(250,450)
                                self.set_moveable(True)
                                state.controls['Panic'].set_tip("Don't Panic","Press for help")
                                self.enable_control('__Fix', '__Link', '__Help')
                            self.dont_panic = True
                        if not self.doc_browse:
                            for control in ('Previous', 'Next'):
                                state.controls[control].set_active(True)
                            self.panel_update()
                            self.documentation('initialize')
                            self.doc_browse = True
                        else:
                            self.documentation('Esc')
                            for control in ('Previous', 'Next'):
                                state.controls[control].set_active(False)
                            self.doc_browse = False
            elif state.control in ('Previous', 'Next'):
                if self.doc_browse:
                    self.documentation(state.control)
            elif state.control == 'Control':
                if state.controls['Panic'].is_active():
                    if not self.is_tips_display():
                        self.set_tips_display(True)
                        self.panic_toggle = True
                else:
                    if self.doc_browse:
                        self.documentation('Esc')
                        for control in ('Previous', 'Next'):
                            state.controls[control].set_active(False)
                        self.doc_browse = False
                    if self.panic_toggle:
                        self.set_tips_display()
                        self.panic_toggle = False
        if self.is_control_moveable():
            self.move_control()
            if self.is_tips_display():
                ctrl = self.get_control(self.get_control_move())
                ctrl.set_tip([str(ctrl.get_position())])
        if self.puzzle:
            if not self.puzzle_init:
                self.puzzle_interface = InterfacePuzzle(self.screen)
                self.puzzle_panel = pygame.sprite.RenderUpdates(self.puzzle_interface)
                if state.values['Select1'] == 'OFF':
                    self.puzzle_interface.set_control_image('none')
                    self.puzzle_interface.panel_update()
                self.puzzle_init = True
            self.puzzle_panel.update()
            if self.puzzle_interface.is_active():
                self.puzzle_panel.clear(self.screen, self.background)
                update_rect = self.puzzle_panel.draw(self.screen)
                pygame.display.update(update_rect)
        if self.panic:
            if state.panel_interact:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                x, y = self.get_position()
                if x > mouse_x:
                    x += 5
                else:
                    x -= 5
                if x < 175: x += 5
                elif x > 325: x -= 5
                if y > mouse_y: 
                    y += 5
                else:
                    y -= 5
                if y < 50: y += 5
                elif y > 450: y -= 5
                self.move(x, y)
        if self.panic_time > 0:
            self.panic_time -= 1
        if self.doc_browse:
            self.documentation()
        if self.is_info_display():
            if state.control_interact:
                self.add_info(state.control_interact, ':')
                self.add_info(state.values[state.control_interact])
                if state.button:
                    self.add_info(state.button)
            if self.puzzle and self.puzzle_interface.is_active():
                state_puzzle = self.puzzle_interface.get_state()
                if state_puzzle.control:
                    self.add_info(state_puzzle.control)
            if state.panel_interact:
                mouse_x, mouse_y = self.get_pointer_position()
                x, y = self.get_position()
                size = self.get_size()
                pos = mouse_x - x + (size[0]//2), mouse_y - y + (size[1]//2)
                state.controls['__Position'].set_value(pos)
            else:
                if state.controls['__Position'].get_value():
                    state.controls['__Position'].set_value('')
        if self.pygame_check():
            self.deactivate()
        return state


class InterfacePuzzle(interphase.Interface):
    """
    Puzzle interface.
    """
    def __init__(self, display):
        self.puzzle_initiate()
        interphase.Interface.__init__(self, identity='Interface_Puzzle', position=(0.5,0.5),
            color=(23,30,38), size=(180,180), screen=display.get_size(), font_color=(175,180,185),
            tips_fontcolor=(255,255,255), tips_display=True)
        self.puzzle_outline()

    def add_controls(self):
        """Add interface controls."""
        positions = [pos for pos in self.grid_positions if pos != self.grid_blank]
        for index, pos in enumerate(positions):
            self.add(
                identity = str(index+1),
                control_type = 'control_toggle',
                position = ((pos[0]*self.grid_size[0])+self.grid_xy[0], (pos[1]*self.grid_size[1])+self.grid_xy[1]),
                size = self.grid_size,
                color = (14,20,27),
                fill = 2,
                control_list = [str(index+1)],
                label_display = False)
        self.add(
            identity = 'Start',
            control_type = 'control_toggle',
            position = (150,150),
            size = self.grid_size,
            color = (14,20,27),
            control_list = ['Go'],
            font_color=(255,255,255),
            label_display = False)

    def puzzle_initiate(self):
        """Initiate puzzle."""
        self.grid_positions = [(y,x) for x in xrange(4) for y in xrange(4)]
        self.grid = {}
        for index, pos in enumerate(self.grid_positions):
            self.grid[pos] = str(index+1)
        self.grid_blank = (3,3)
        self.grid_size = (40,40)
        self.grid_xy = (30,30)
        self.control_move = None
        self.move_offset = None
        self.move_rate = self.grid_size[0]//4
        self.move_step = 0
        self.last_move = None
        self.count = 0
        self.grid_timer = 0
        self.grid_initialize = False
        self.puzzle_solving = False

    def puzzle_outline(self):
        """Draw outline around puzzle controls."""
        panel_image = self.get_panel_image(change=True)
        pygame.draw.rect(panel_image, (14,20,27), (10,10,160,160), 2)
        self.panel_update()

    def init(self):
        """Shuffle puzzle controls."""
        ctrl = self.get_control()
        next = {}
        ids = [str(i) for i in range(1,16)]
        try:
            ids.remove(self.last_move)
        except ValueError:
            pass
        random.shuffle(ids)
        for id in ids:
            pos = (ctrl[id].position[0]-self.grid_xy[0]+(ctrl[id].size[0]//2))//ctrl[id].size[0], (ctrl[id].position[1]-self.grid_xy[1]+(ctrl[id].size[1]//2))//ctrl[id].size[1]
            if (pos[0] == self.grid_blank[0] and abs(pos[1]-self.grid_blank[1]) == 1) or (pos[1] == self.grid_blank[1] and abs(pos[0]-self.grid_blank[0]) == 1):
                break
        self.last_move = id
        self.control_move = id
        self.move_offset = (self.grid_blank[0]*self.move_rate - pos[0]*self.move_rate, self.grid_blank[1]*self.move_rate - pos[1]*self.move_rate)
        self.grid_blank = pos
        self.count += 1
        if self.count > 100 and self.grid_blank == (3,3):
            self.count = 0
            return True
        else:
            return False

    def puzzle(self, state):
        """Slide puzzle controls."""
        ctrl = self.get_control(state.control)
        pos = (ctrl.position[0]-self.grid_xy[0]+(ctrl.size[0]//2))//ctrl.size[0], (ctrl.position[1]-self.grid_xy[1]+(ctrl.size[1]//2))//ctrl.size[1]
        if (pos[0] == self.grid_blank[0] and abs(pos[1]-self.grid_blank[1]) == 1) or (pos[1] == self.grid_blank[1] and abs(pos[0]-self.grid_blank[0]) == 1):
            self.move_offset = (self.grid_blank[0]*self.move_rate - pos[0]*self.move_rate, self.grid_blank[1]*self.move_rate - pos[1]*self.move_rate)
            self.control_move = state.control
            self.grid_blank = pos

    def puzzle_final(self):
        """Check if puzzle is complete."""
        controls = self.get_control()
        success = True
        for ctrl_id in xrange(1,16):
            id = str(ctrl_id)
            pos = (controls[id].position[0]-self.grid_xy[0]+(controls[id].size[0]//2))//controls[id].size[0], (controls[id].position[1]-self.grid_xy[1]+(controls[id].size[1]//2))//controls[id].size[1]
            if controls[id].value != self.grid[pos]:
                success = False
                break
        return success

    def move(self):
        """Puzzle control move."""
        if self.move_step < 4:
            self.move_control(self.control_move, offset=self.move_offset)
            self.move_step += 1
            complete = False
        else:
            self.control_move = None
            self.move_step = 0
            complete = True
        return complete

    def update(self):
        """Puzzle update."""
        interphase.Interface.update(self)
        state = self.get_state()
        if state.control == 'Start':
            self.get_control('Start').set_active(False)
            self.grid_initialize = True
        if self.grid_initialize:
            if self.control_move:
                self.move()
                return
            complete = self.init()
            if complete:
                self.grid_initialize = False
                self.puzzle_solving = True
                self.grid_timer = pygame.time.get_ticks()
        if self.puzzle_solving:
            if self.control_move:
                complete = self.move()
                if complete:
                    success = self.puzzle_final()
                    if success:
                        self.puzzle_solving = False
                        time = ( pygame.time.get_ticks() - self.grid_timer ) // 1000
                        control_start = self.get_control('Start')
                        control_start.set_value(str(time)+'s')
                        control_start.set_active(True)
                return
            else:
                if state.control:
                    self.puzzle(state)
            return


def run():
    interface_panel = InterfaceDemo()
    panel = pygame.sprite.RenderUpdates(interface_panel)
    run_demo = True
    while run_demo:
        panel.update()
        if interface_panel.is_active():
            panel.clear(interface_panel.screen,interface_panel.background)
            update_rect = panel.draw(interface_panel.screen)
            pygame.display.update(update_rect)
        else:
            run_demo = False


def main():
    run()

if __name__ == '__main__':
    main()
