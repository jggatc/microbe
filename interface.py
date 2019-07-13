"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import os
import interphase


class MatrixInterface(interphase.Interface):
    """
    Interface panel.
    """

    def __init__(self, matrix, control):
        self.matrix = matrix
        self.control = control
        self.tool_type = ['Add_Gradient', 'Add_Toxin', 'Add_Algae', 'Add_Bacterium', 'Add_Paramecium', 'Add_Ciliate', 'Add_Amoeba']
        self.command_type = ['Magnify', 'Track', 'Tag', 'Evolution', 'Set Gene', 'Set ID', 'Save', 'Load', 'Config']
        self.tools = []
        for tool in self.tool_type:
            self.tools.append('__'+tool)
        self.tools.extend(self.command_type)
        self.tips_list = ['Add Gradient', 'Add Toxin', 'Add Algae', 'Add Bacterium', 'Add Paramecium', 'Add Ciliate', 'Add Amoeba', 'Use Magnifier', 'Track Microbe', 'Tag Microbe', 'Evolution Mode', 'Set Gene', 'Set ID', 'Save Microbe', 'Load Microbe', 'Configuration']
        interphase.Interface.__init__(self, position=(self.matrix.dx//2,self.matrix.dy-50), image='panel.png', color=(0,5,10), size=(350,100), moveable=True, position_offset=(0,87), control_image='none', button_image=['button.png'], control_minsize=(35,35), control_size='auto', control_response=100)
        self.input_mode = None
        self.bug_tag = None
        self.gene_select = None
        self.tag_id = ''
        self.info = True
        self.info_update = False
        self.initialize = False

    def add_controls(self):
        self.add(
            identity = 'Control',
            control_type = 'function_select',
            position = (50,50),
            size = 'auto',
            control_list = self.tools,
            icon_list = ['icons.png'],
            tip_list = self.tips_list,
            control_outline = True,
            activated_toggle = False,
            link_activated = False,
            hold_response = 0,
            loop = True,
            label_display = False)
        self.add(
            identity = '__Fix',
            control_type = 'control_toggle',
            position = (315,90),
            color = (0,20,30),
            font_color = (0,120,160),
            control_list = ['!'])
        self.add(
            identity = '__Help',
            control_type = 'control_toggle',
            position = (335,90),
            color = (0,20,30),
            font_color = (0,120,160),
            control_list = ['?'])
        self.add(
            identity = '__Label',
            control_type = 'label',
            position = (175,85),
            font_color = (0,120,160),
            control_list = [''])
        self.add(
            identity = '__EvolutionLabel',
            control_type = 'label',
            position = (200,95),
            font_color = (0,120,160),
            control_list = ['Evolution Mode'])
        self.add(
            identity = 'Evolution Mode',
            control_type = 'function_toggle',
            position = (175,30),
            size = 'auto_width',
            control_list = ['Deactivated', 'Activated'],
            tip_list = ['Evolution Deactivated', 'Evolution Activated'],
            link = [ [], ['Evolve'] ])
        self.add(
            identity = 'Evolve',
            control_type = 'control_toggle',
            position = (175,55),
            size = 'auto_width',
            control_list = ['Select'],
            tip_list = ['Species Evolve'],
            activated_toggle = False)
        self.add(
            identity = 'Select Gene',
            control_type = 'control_select',
            position = (230,60),
            size = (25,25),
            reverse = True)
        self.add(
            identity = 'Select Allele',
            control_type = 'control_select',
            position = (230,60),
            size = (25,25),
            control_list = ['__numeric', (1,100)],
            active = False)
        self.add(
            identity = 'Set ID',
            control_type = 'control_select',
            position = (230,60),
            size = (25,25),
            control_list = ['__alphanumeric', 'mixed'],
            tip_list = ['Identity'])
        self.add(
            identity = 'Files',
            control_type = 'control_select',
            position = (165,50),
            size = 'auto_width',
            control_list = ['__filelist', 'data', 'species', '.dat'],
            tip_list = ['Files'])
        self.add(
            identity = 'Query',
            control_type = 'control_select',
            position = (275,60),
            size = (25,25),
            control_list = ['No', 'Yes'],
            tip_list = ['Query'],
            reverse = True,
            active = False)
        self.add(
            identity = 'Info',
            control_type = 'control_toggle',
            position = (135,50),
            control_list = ['ON', 'OFF'],
            tip_list = ['Info Display'])
        self.add(
            identity = 'Tag',
            control_type = 'control_toggle',
            position = (200,50),
            control_list = ['ON', 'OFF'],
            tip_list = ['Tag Display'])
        self.add(
            identity = 'Compass',
            control_type = 'control_toggle',
            position = (265,50),
            control_list = ['ON', 'OFF'],
            tip_list = ['Compass Display'])
        self.add(
            identity = 'ID',
            control_type = 'label',
            position = (35,8),
            control_list = [''],
            active = False)
        self.add(
            identity = 'Genes',
            control_type = 'label',
            position = (184,8),
            control_list = [''],
            active = False)
        self.add(
            identity = 'Fitness',
            control_type = 'label',
            position = (322,8),
            control_list = [''],
            active = False)
        self.add(
            identity = 'Evolving',
            control_type = 'label',
            position = (342,8),
            control_list = ['*'],
            active = False)
        ctrl = self.get_control('Control')
        ctrl.set_link('Evolution', ['Evolution Mode', '__EvolutionLabel'])
        ctrl.set_link('Set Gene', ['Select Gene'])
        ctrl.set_link('Set ID', ['Set ID'])
        ctrl.set_link('Load', ['Files'])
        ctrl.set_link('Save', ['Set ID'])
        ctrl.set_link('Config', ['Info', 'Tag', 'Compass'])

    def set_panel_value(self, control):
        if control in ('Compass', 'Tag', 'Evolution Mode'):
            self.get_control(control).next()

    def display_info(self):
        if (self.matrix.bug_tag or self.matrix.evolution) and self.info:
            try:
                if self.matrix.bug_tag:
                    if self.info_update:
                        self.get_control('ID').set_value('ID:'+str(self.matrix.bug_tag.identity))
                        if self.matrix.bug_tag.gene:
                            genes = '/'.join([str(x) for x in self.matrix.bug_tag.gene.values()])
                            self.get_control('Genes').set_value('Genes:'+genes)
                        self.info_update = False
                if self.matrix.evolution:
                    if self.matrix.bug_tag and self.matrix.bug_tag.species.evolving:
                        fitness = '%0.1f' %self.matrix.bug_tag.fitness
                        self.get_control('Fitness').set_value(fitness)
            except AttributeError:
                pass

    def info_active(self, setting):
        if not self.info:
            return False
        if setting == True:
            if self.matrix.bug_tag:
                ctrl = self.get_control('ID','Genes')
                for ctr in ctrl:
                    ctrl[ctr].set_active(True)
            if self.matrix.evolution:
                self.get_control('Evolving').set_active(True)
                if self.matrix.bug_tag:
                    self.get_control('Fitness').set_active(True)
            self.info_update = True
        elif setting == False:
            if not self.matrix.bug_tag:
                ctrl = self.get_control('ID','Genes','Fitness')
                for ctr in ctrl:
                    ctrl[ctr].set_value('')
                    ctrl[ctr].set_active(False)
            if not self.matrix.evolution:
                self.get_control('Evolving').set_active(False)
                if self.matrix.bug_tag:
                    self.get_control('Fitness').set_active(False)
        return True

    def set_gene(self, state):
        if self.matrix.bug_tag and self.matrix.bug_tag.gene:
            if not self.initialize:
                state.controls['Select Gene'].set_list(list(self.matrix.bug_tag.gene.keys()))
                state.controls['Select Gene'].set_tip(list(self.matrix.bug_tag.gene_info.values()))
                state.controls['Select Gene'].set_active(True)
                state.controls['Select Allele'].set_active(False)
                state.controls['__Label'].set_value('Select gene')
                self.control.tool = 'Track'
                self.gene_select = None
                self.initialize = True
            if not self.gene_select:
                if state.button == 'Select Gene':
                    self.gene_select = int(state.values['Select Gene'])
                    self.allele_select = self.matrix.bug_set_gene(self.matrix.bug_tag, self.gene_select, allele=True)
            else:
                if state.controls['__Label'].get_value() == 'Select gene':
                    state.controls['Select Gene'].set_active(False)
                    state.controls['Select Allele'].set_active(True)
                    state.controls['Select Allele'].set_list(['__numeric', (self.allele_select[0], self.allele_select[1]-1)])
                    state.controls['Select Allele'].set_value(self.matrix.bug_tag.gene[int(state.values['Select Gene'])])
                    state.controls['Select Allele'].set_tip([self.matrix.bug_tag.gene_info[int(state.values['Select Gene'])]])
                    state.controls['__Label'].set_value('Gene '+str(self.gene_select))
                if state.button == 'Select Allele':
                    self.matrix.bug_set_gene(self.matrix.bug_tag, self.gene_select, state.value)
                    state.controls['Select Allele'].set_active(False)
                    state.controls['Select Gene'].set_active(True)
                    state.controls['__Label'].set_value('Select gene')
                    self.gene_select = None
            self.info_update = True
        else:
            if state.controls['__Label'].get_value() != 'Select Microbe':
                state.controls['Select Gene'].set_active(True)
                state.controls['Select Allele'].set_active(False)
                self.control.tool = 'Track'
                state.controls['__Label'].set_value('Select Microbe')
                state.controls['Select Gene'].remove_list()
                self.initialize = False

    def set_id(self, state):
        if self.matrix.bug_tag:
            if not self.bug_tag or self.bug_tag is not self.matrix.bug_tag:
                self.bug_tag = self.matrix.bug_tag
                pad = ' ' * (3-len(self.tag_id))
                state.controls['__Label'].set_value('ID: ' + pad)
                self.control.tool = 'Track'
                self.tag_id = ''
            if state.button == 'Set ID':
                self.tag_id = self.tag_id + state.value
                pad = ' ' * (3-len(self.tag_id))
                state.controls['__Label'].set_value('ID: ' + pad + self.tag_id)
            if len(self.tag_id) == 3:
                self.matrix.bug_set_id(self.bug_tag, self.tag_id)
                self.tag_id = ''
            self.info_update = True
        else:
            self.control.tool = 'Track'
            state.controls['__Label'].set_value('Select Microbe')

    def file_check(self, filename, path='data'):
        if path:
            filename = os.path.join(path, filename)
        check = os.path.exists(filename)
        return check

    def file_save(self, state, file_root='species', file_ext='.dat', file_num=None):
        if self.matrix.bug_tag:
            if not self.initialize:
                self.filename = file_root + '_' + self.tag_id + file_ext
                state.controls['__Label'].set_value('Save to ' + self.filename)
                self.control.tool = 'Track'
                self.initialize = True
            if state.control == 'Set ID' and len(self.tag_id) == 3 and not state.controls['Query'].is_active():
                self.tag_id = ''
                self.filename = file_root + '_' + self.tag_id + file_ext
                state.controls['__Label'].set_value('Save to ' + self.filename)
            if state.button == 'Set ID' and len(self.tag_id) < 3:
                self.tag_id = self.tag_id + state.value
                self.filename = file_root + '_' + self.tag_id + file_ext
                state.controls['__Label'].set_value('Save to ' + self.filename)
                if len(self.tag_id) == 3:
                    self.filename = file_root + '_' + self.tag_id + file_ext
                    if not self.file_check(self.filename):
                        self.matrix.bug_save(self.matrix.bug_tag, self.filename)
                        state.controls['__Label'].set_value('Saved ' + self.filename)
                    else:
                        state.controls['__Label'].set_value('Overwrite ' + self.filename + '?')
                        state.controls['Query'].set_active(True)
            elif state.button == 'Query':
                if state.value == 'Yes':
                    self.matrix.bug_save(self.matrix.bug_tag, self.filename, overwrite=True)
                    state.controls['__Label'].set_value('Saved ' + self.filename)
                elif state.value == 'No':
                    self.tag_id = ''
                    self.filename = file_root + '_' + self.tag_id + file_ext
                    state.controls['__Label'].set_value('Save to ' + self.filename)
                if state.controls['Query'].get_value() == 'Yes':
                    state.controls['Query'].next()
                state.controls['Query'].set_active(False)
        else:
            if state.controls['Query'].is_active():
                if state.controls['Query'].get_value() == 'Yes':
                    state.controls['Query'].next()
                state.controls['Query'].set_active(False)
            self.tag_id = ''
            self.initialize = False
            self.control.tool = 'Track'
            state.controls['__Label'].set_value('Select Microbe')

    def file_load(self, state):
        if not self.initialize:
            state.controls['Files'].set_list(['__filelist', 'data', 'species', '.dat'])
            self.initialize = True
        if state.button == 'Files':
            self.file_select = state.value
            state.controls['__Label'].set_value('Load ' + self.file_select)
            if self.file_check(self.file_select):
                self.control.newspecies = self.file_select
                self.control.tool = 'Load'
            else:
                state.controls['__Label'].set_value(self.file_select + ' not found')

    def quit(self, state=None, cmd=None):
        cancel = False
        if cmd:
            if cmd == 'initialize':
                ctrl = self.get_control()
                ctrl['Control'].set_activated(False)
                ctrl['Control'].set_active(False)
                ctrl['Query'].set_active(True)
                ctrl['__Label'].set_value('Quit?')
                if not self.is_moveable('Fixed'):
                    self.set_moveable('Fixed')
                if not self.is_panel_display():
                    self.set_panel_display(True)
                self.input_mode = 'Quit'
            elif cmd == 'cancel':
                cancel = True
        else:
            if state.button == 'Query':
                if state.value == 'Yes':
                    self.control.quit = True
                elif state.value == 'No':
                    cancel = True
        if cancel:
            ctrl = self.get_control()
            ctrl['Control'].set_active(True)
            ctrl['Query'].set_active(False)
            ctrl['__Label'].set_value('')
            if self.is_moveable('Fixed'):
                self.set_moveable('Fixed')
            if not self.is_panel_display():
                self.set_panel_display(True)
            self.input_mode = None

    def input_commands(self, state):
        if self.input_mode == 'Set Gene':
            self.set_gene(state)
        elif self.input_mode == 'Set ID':
            self.set_id(state)
        elif self.input_mode == 'Save':
            self.file_save(state)
        elif self.input_mode == 'Load':
            self.file_load(state)
        elif self.input_mode == 'Quit':
            self.quit(state)

    def update(self):
        interphase.Interface.update(self)
        state = self.get_state()
        self.control.panel_displayed = state.panel_interact
        if state.control:
            if state.control == 'Control':   
                if state.controls[state.control].is_activated():
                        if state.value[:2] == '__':
                            self.control.tool = state.value[2:]
                        elif state.value in ('Magnify', 'Track', 'Tag'):
                            self.control.tool = state.value
                            if state.value in ('Track', 'Tag'):
                                state.controls['__Label'].set_value(state.value+' selection')
                        elif state.value in ('Set Gene', 'Set ID', 'Save', 'Load'):
                            self.input_mode = state.value
                        elif state.value == 'Config':
                            self.set_label_display(True)
                else:
                    self.control.tool = None
                    self.input_mode = None
                    state.controls['__Label'].set_value('')
                    self.gene_select = None
                    self.tag_id = ''
                    self.bug_tag = None
                    state.controls['Select Gene'].remove_list()
                    state.controls['Select Allele'].set_active(False)
                    self.set_label_display(False)
                    self.initialize = False
            elif state.control == 'Evolution Mode':
                if state.value == 'Activated':
                    self.matrix.set_evolution(True)
                    self.info_active(True)
                elif state.value == 'Deactivated':
                    self.matrix.set_evolution(False)
                    self.info_active(False)
                    self.control.tool = None
            elif state.control == 'Evolve':
                if state.controls[state.control].is_activated():
                    self.control.tool = state.control
                else:
                    self.control.tool = None
            elif state.control == 'Info':
                if state.value == 'ON':
                    self.info = True
                    self.info_active(True)
                elif state.value == 'OFF':
                    self.info = False
                    ctrl = self.get_control('ID','Genes','Fitness','Evolving')
                    for ctr in ctrl:
                        ctrl[ctr].set_active(False)
            elif state.control == 'Tag':
                if state.value == 'ON':
                    self.matrix.set_tag_display(True)
                elif state.value == 'OFF':
                    self.matrix.set_tag_display(False)
            elif state.control == 'Compass':
                folding = False
                if state.value == 'ON':
                    if not self.control.compass_folding:
                        if not self.control.compass_use:
                            self.control.compass_use = True
                            self.control.compass_folding = True
                            self.control.scroll_edge = False
                            self.matrix.set_screen_update()
                    else:
                        folding = True
                elif state.value == 'OFF':
                    if not self.control.compass_folding:
                        if self.control.compass_use:
                            self.control.compass_use = False
                            self.control.compass_folding = True
                            self.control.scroll_edge = True
                            self.matrix.set_screen_update()
                    else:
                        folding = True
                if folding:
                    state.controls['Compass'].previous()
            elif state.control == '__Fix':
                self.set_moveable('Fixed')
                if self.is_moveable('Fixed'):
                    self.set_panel_display(False)
                else:
                    self.set_panel_display(True)
            elif state.control == '__Help':
                self.set_tips_display()
        self.display_info()
        if self.input_mode:
            self.input_commands(state)

