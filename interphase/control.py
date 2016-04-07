"""
Interphase
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import pygame
import os


class InterfaceControl(object):
    """
    InterfaceControl Object: Define panel control.

    Parameters:
    panel: obj panel holding control.
        - automatically set by panel add() method.
    identity: 'id' control name.
    control_type: 'type' control type.
        - 'function_select', 'function_toggle': master control.
        - 'control_select', 'control_toggle': standard control.
        - 'label': label control.
    position: (x,y) control placement on panel. Values < 1 are %panel.
    Optional parameters <default>:
    size: (w,h) control size override panel specified <None>.
        - 'auto', 'auto_width': fit items.
        - 'min', 'min_width': fit using control_minsize.
        - 'panel': use exact control_minsize.
    color: (r,g,b) control color <(40,80,120)>.
    fill: int button edge width, and 0 filled -1 none <1>.
    control_outline: display control edge <None>.
    control_image: 'image' control background image overrides panel <None>.
        - 'none' suppress image.
        - Image in data folder.
    font_color: (r,g,b) font color. Overrides panel <None>.
    font_type: [] font type list. Overrides panel <None>.
    font_size: int font size - 6,8,10,12,24,32. Overrides panel <None>.
    split_text: bool split text at space to new line <True>.
    control_list: [] list held by control <None>.
        - numeric: [0] '__numeric', [1] (start,stop,step).
        - alpha: [0] '__alpha', [1] 'upper','lower','mixed'.
        - alphanumeric: [0] '__alphanumeric' in list[0], [1] 'upper','lower','mixed'.
        - filelist: [0] '__filelist', [1] path, [2] root, [3] ext.
        - 'item': Value listing. Leading '__' not display or display available icon.
    icon_list: [] control icons <None>.
        - replace '__item' in control_list - separate images or a composite image.
    icon_size: (w,h) control icon size <None>.
        - values < 1 are %control size.
        - default use control size.
    tip_list: [] tip list - single tip or multiple tip list <None>.
    link: [] function control link to activate other controls <None>.
    link_activated: bool function control link activated <True>.
    activated_color: (r,g,b) highlight color of activated control <(0,120,160)>.
    activated_toggle: bool control activated toggle <True>.
        - 'lock' for activate lock.
    label: '' supply label to replace 'id' text <None>.
    label_display: bool control label displayed <True>.
    active: bool control active state <True>.
    control_response: int control response (ms). Overrides panel <None>.
    hold_response: int hold (ms) before control response quicken <1000>.
        - 0 no response change.
    delay_response: int initial delay (ms) before control response <0>.
    loop: bool option list loop <False>.
    reverse: bool control switches reversed <False>.
    event: bool interaction generates events. Overrides panel <None>.
"""

    def __init__(self, panel, identity, control_type, position, size=None, color=(40,80,120), fill=1, control_outline=None, control_image=None, font_color=None, font_type=None, font_size=None, split_text=True, control_list=None, icon_list=None, icon_size=None, tip_list=None, link=None, link_activated=True, activated_color=(0,120,160), activated_toggle=True, label=None, label_display=True, active=True, control_response=None, hold_response=1000, delay_response=0, loop=False, reverse=False, event=None):
        self.id = identity      #control identity
        self.panel = panel      #panel holding control
        if control_type in ['function_select', 'function_toggle', 'control_select', 'control_toggle', 'label']:
            self.control_type = control_type    #functional type of control
        else:
            raise ValueError('Incorrect control type.')
        self.listing = []   #list item held by control
        self.place = 0      #current place in list
        if not control_list:
            control_list = []
        if not icon_list:
            icon_list = []
        if not tip_list:
            tip_list = []
        self.reverse = reverse
        if not self.reverse:
            self.button_forward = self.id+'_bottom'
            self.button_reverse = self.id+'_top'
        else:
            self.button_forward = self.id+'_top'
            self.button_reverse = self.id+'_bottom'
        if not size:
            self.size = self.panel._control_size
        else:
            self.size = size
        if self.size == 'min' and not self.panel._control_minsize:
            self.size = 'auto'
        if not font_color:
            self.font_color = self.panel._font_color
        else:
            self.font_color = font_color
        self.font_type = font_type
        if not font_size:
            self.font_size = self.panel._font_size
        else:
            self.font_size = font_size
        self.split_text = split_text
        self.list_type = ''     #list/_numeric...
        self.control_icon = {}
        self.icon_size = icon_size
        self.listing, self.value, self.control_icon, self.icon_size, self.size = self.set_listing(control_list, icon_list, self.size)
        pos_x, pos_y = position     #control position in panel
        if pos_x < 1:
            pos_x = int(pos_x*self.panel._size[0])
        if pos_y < 1:
            pos_y = int(pos_y*self.panel._size[1])
        pos_x, pos_y = pos_x - (self.size[0]//2), pos_y - (self.size[1]//2)
        self.position = int(pos_x), int(pos_y)
        self.display = self.set_display_info(self.size, self.font_color, self.font_type, self.font_size)
        self.label = self.set_label_info(self.size, self.font_color, self.font_type, self.font_size)
        if label:
            self.label_text = label
        else:
            self.label_text = self.id
        self.label_display = label_display
        self.tips = self.set_tips(tip_list)
        self.color = {'normal':color, 'activated':activated_color, 'fill':fill}
        self.active_color = self.color['normal']
        if activated_toggle == 'lock':
            self.activated_toggle = False
            self.activated_lock = True
        else:
            self.activated_toggle = activated_toggle
            self.activated_lock = False
        self.control_image = {}
        if control_image:
            self.set_control_image(control_image)
        else:
            self.control_image = self.panel._control_image
        if control_outline is None:
            if not self.control_image:
                self.control_outline = True
            else:
                self.control_outline = False
        elif control_outline in (True, False):
            self.control_outline = control_outline
        self.outline = self.control_outline
        self.button, self.rects = self.define_buttons(self.control_type, self.size, color, fill)
        self.loop = loop    #listing loops back
        if control_response is not None:
            self.control_response = control_response
        else:
            self.control_response = self.panel._control_response
        self.hold_response_set = hold_response
        self.control_response_hold = 25
        self.delay_response = delay_response
        if self.listing:
            if ( (len(self.listing) > (self.hold_response_set//100)) or (self.listing[0][:-2] == '__numeric' and abs(self.numeric['h']-self.numeric['l']) > (self.hold_response_set//100)) ) and (self.control_response > self.control_response_hold):
                self.hold_response = self.hold_response_set      #response increase with hold
            else:
                self.hold_response = 0
        else:
            self.hold_response = 0
        if link:
            self.link = {}
            for item in self.listing:
                try:
                    self.link[item] = link.pop(0)
                except IndexError:
                    self.link[item] = []
        else:
            self.link = {}
        self.link_activated = link_activated
        if event is not None:
            self.event = event
        else:
            self.event = self.panel._event
        self.enabled = True
        self.activated = False
        self.active = active
        self.button_list = self.set_buttonlist()

    def define_buttons(self, control_type, size, color, fill, initialize=True):
        """Define control layout."""
        button = {}
        rects = {}
        if control_type in ('function_select', 'control_select'):
            if self.panel._button_placement[control_type] == 'left':
                x, y = self.position
                x1 = x-(self.panel._button_size[0]//2+2)
                y1 = int(y+(0.25*size[1])+4)
                x2 = x-(self.panel._button_size[0]//2+2)
                y2 = int(y+(0.75*size[1])-4)
            elif self.panel._button_placement[control_type] == 'right':
                x, y = self.position
                x1 = x+size[0]+(self.panel._button_size[0]//2+2)
                y1 = int(y+(0.25*size[1])+4)
                x2 = x+size[0]+(self.panel._button_size[0]//2+2)
                y2 = int(y+(0.75*size[1])-4)
        if control_type == 'function_select':
            if not self.control_image:
                button[self.id] = lambda: pygame.draw.rect(self.panel.image, self.active_color, (self.position,size), fill)
            else:
                background = pygame.transform.smoothscale(self.control_image['bg'], size)
                button[self.id+'_bg'] = lambda: self.panel.image.blit(background, self.position)
                button[self.id] = lambda: pygame.draw.rect(self.panel.image, self.active_color, (self.position,size), fill)
            if not self.panel._button_image:
                button[self.id+'_top'] = lambda: pygame.draw.polygon(self.panel.image, color, ((x1,y1-10),(x1-5,y1),(x1+5,y1)), fill)
            else:
                button[self.id+'_top'] = lambda: self.panel.image.blit(self.panel._button_image['t'], (x1-self.panel._button_size[0]//2,y1-self.panel._button_size[1]))
            if not self.panel._button_image:
                button[self.id+'_bottom'] = lambda: pygame.draw.polygon(self.panel.image, color, ((x2,y2+10),(x2-5,y2),(x2+5,y2)), fill)
            else:
                button[self.id+'_bottom'] = lambda: self.panel.image.blit(self.panel._button_image['b'], (x2-self.panel._button_size[0]//2,y2))
        elif control_type == 'function_toggle':
            if not self.control_image:
                button[self.id] = lambda: pygame.draw.rect(self.panel.image, self.active_color, (self.position,size), fill)
            else:
                background = pygame.transform.smoothscale(self.control_image['bg'], size)
                button[self.id+'_bg'] = lambda: self.panel.image.blit(background, self.position)
                button[self.id] = lambda: pygame.draw.rect(self.panel.image, self.active_color, (self.position,size), fill)
        elif control_type == 'control_select':
            if not self.control_image:
                button[self.id] = lambda: pygame.draw.rect(self.panel.image, self.active_color, (self.position,size), fill)
            else:
                background = pygame.transform.smoothscale(self.control_image['bg'], size)
                button[self.id+'_bg'] = lambda: self.panel.image.blit(background, self.position)
                button[self.id] = lambda: pygame.draw.rect(self.panel.image, self.active_color, (self.position,size), fill)
            if not self.panel._button_image:
                button[self.id+'_top'] = lambda: pygame.draw.polygon(self.panel.image, color, ((x1,y1-10),(x1-5,y1),(x1+5,y1)), fill)
            else:
                button[self.id+'_top'] = lambda: self.panel.image.blit(self.panel._button_image['t'], (x1-self.panel._button_size[0]//2,y1-self.panel._button_size[1]))
            if not self.panel._button_image:
                button[self.id+'_bottom'] = lambda: pygame.draw.polygon(self.panel.image, color, ((x2,y2+10),(x2-5,y2),(x2+5,y2)), fill)
            else:
                button[self.id+'_bottom'] = lambda: self.panel.image.blit(self.panel._button_image['b'], (x2-self.panel._button_size[0]//2,y2))
        elif control_type == 'control_toggle':
            if not self.control_image:
                button[self.id] = lambda: pygame.draw.rect(self.panel.image, self.active_color, (self.position,size), fill)
            else:
                background = pygame.transform.smoothscale(self.control_image['bg'], size)
                button[self.id+'_bg'] = lambda: self.panel.image.blit(background, self.position)
                button[self.id] = lambda: pygame.draw.rect(self.panel.image, self.active_color, (self.position,size), fill)
        elif control_type == 'label':
            button[self.id] = lambda:None
        self.button = button
        if initialize:
            if control_type != 'label':
                for btn in button:
                    if btn not in self.panel._controls_disabled:
                        offset_x, offset_y = self.panel._panel_rect[0], self.panel._panel_rect[1]
                        rect = button[btn]()
                        rect[0], rect[1] = rect[0] + offset_x, rect[1] + offset_y
                        rects[btn] = rect
            return button, rects

    def set_listing(self, control_list=None, icon_list=None, size='auto', case=False, data_folder=None, data_zip=None, file_obj=None, color_key=None, surface=None):
        """Initiate control option list."""
        if not control_list:
            control_list = []
        if not icon_list and not surface:
            icon_list = []
        control_icon = {}
        icon_size = None
        self.value = ''
        self.place = 0
        if control_list:
            if control_list[0] == '__numeric':
                self.numeric = {}
                try:
                    if len(control_list[1]) == 1:
                        self.numeric['l'] = 0
                        self.numeric['h'] = control_list[1][0]
                        self.numeric['step'] = 1
                    elif len(control_list[1]) == 2:
                        self.numeric['l'] = control_list[1][0]
                        self.numeric['h'] = control_list[1][1]
                        self.numeric['step'] = 1
                    elif len(control_list[1]) == 3:
                        self.numeric['l'] = control_list[1][0]
                        self.numeric['h'] = control_list[1][1]
                        self.numeric['step'] = control_list[1][2]
                except IndexError:
                        self.numeric['l'] = 0
                        self.numeric['h'] = 100
                        self.numeric['step'] = 1
                numeric_type = 'integer'
                for num in ('l','h','step'):
                    if isinstance(self.numeric[num], float):
                        numeric_type = 'float'
                        break
                if numeric_type == 'integer':
                    self.list_type = control_list[0]+'_i'
                    self.listing = [self.list_type]
                    self.numeric['value'] = str(self.numeric['l'])
                elif numeric_type == 'float':
                    self.list_type = control_list[0]+'_f'
                    self.listing = [self.list_type]
                    precision = 1
                    for num in ('l','h','step'):
                        self.numeric[num] = float(self.numeric[num])
                        fractional = len(str(self.numeric[num]).rsplit('.')[1])
                        if fractional > precision:
                            precision = fractional
                    self.numeric['precision'] = precision
                    integer, fractional = str(self.numeric['l']).rsplit('.')
                    fractional = fractional[:self.numeric['precision']]
                    self.numeric['value'] = integer + '.' + fractional
                if self.control_type[:8] == 'function':
                    self.control_type = 'control'+self.control_type[8:]
                if self.numeric['step'] > 0:
                    if not self.reverse:
                        self.button_forward = self.id+'_top'
                        self.button_reverse = self.id+'_bottom'
                    else:
                        self.button_forward = self.id+'_bottom'
                        self.button_reverse = self.id+'_top'
                else:
                    if not self.reverse:
                        self.button_forward = self.id+'_bottom'
                        self.button_reverse = self.id+'_top'
                    else:
                        self.button_forward = self.id+'_top'
                        self.button_reverse = self.id+'_bottom'
                self.value = self.numeric['l']
            elif control_list[0] == '__alpha':
                self.list_type = control_list[0]
                if not case:
                    try:
                        case = control_list[1]
                    except IndexError:
                        case = 'upper'
                if case == 'upper':
                    char = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                elif case == 'lower':
                    char = ' abcdefghijklmnopqrstuvwxyz'
                elif case == 'mixed':
                    char = ' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                self.listing = char
                self.value = self.listing[self.place]
            elif control_list[0] == '__alphanumeric':
                self.list_type = control_list[0]
                if not case:
                    try:
                        case = control_list[1]
                    except IndexError:
                        case = 'upper'
                if case == 'upper':
                    char = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                elif case == 'lower':
                    char = ' abcdefghijklmnopqrstuvwxyz0123456789'
                elif case == 'mixed':
                    char = ' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                self.listing = char
                self.value = self.listing[self.place]
            elif control_list[0] == '__filelist':
                self.list_type = control_list[0]
                try:
                    file_path = control_list[1]
                except IndexError:
                    file_path = None
                try:
                    file_root = control_list[2]
                except IndexError:
                    file_root = None
                try:
                    file_ext = control_list[3]
                except IndexError:
                    file_ext = None
                if not file_path:
                    file_path = os.curdir
                file_list = os.listdir(file_path)
                file_list = [item for item in file_list if os.path.isfile(os.path.join(file_path,item))]
                if file_root:
                    file_list = [item for item in file_list if item.startswith(file_root)]
                if file_ext:
                    file_list = [item for item in file_list if item.endswith(file_ext)]
                self.listing = file_list
                self.listing.sort()
                if self.listing:
                    self.value = self.listing[0]
                else:
                    self.listing.append('None')
                    self.value = 'None'
            else:
                self.list_type = 'list'
                for item in control_list:
                    self.listing.append(str(item))
                self.value = self.listing[self.place]
                if icon_list or surface:      #icon in listing
                    listing_icon = []
                    for item in self.listing:
                        if item.startswith('__'):
                            listing_icon.append(item)
                    if listing_icon:
                        control_icon = self.set_listing_icon(listing_icon, icon_list, data_folder, data_zip, file_obj, color_key, surface)
        self.panel._control_values[self.id] = self.value
        self.size, self.icon_size = self.set_control_size(self.listing, control_icon, size, self.font_size)
        if control_icon:
            self.control_icon = self.set_icon_size(control_icon, self.icon_size)
        return self.listing, self.value, self.control_icon, self.icon_size, self.size

    def set_listing_icon(self, listing_icon, icon_list=None, data_folder=None, data_zip=None, file_obj=None, color_key=None, surface=None):
        """Set icons of control list."""
        if isinstance(icon_list, str):
            icon_list = [icon_list]
        control_icon = {}
        frames = len(listing_icon)
        if icon_list:
            data_folder, data_zip, color_key = self.panel._data_source(data_folder, data_zip, color_key, file_obj)
            if len(icon_list) == 1 and frames > 1:
                images = self.panel._load_image(icon_list[0], frames, path=data_folder, zipobj=data_zip, fileobj=file_obj, colorkey=color_key)
                for num, item in enumerate(listing_icon):
                    control_icon[item] = images[num]
            else:
                for num, item in enumerate(listing_icon):
                    img = self.panel._load_image(icon_list[num], path=data_folder, zipobj=data_zip, fileobj=file_obj, colorkey=color_key)
                    control_icon[item] = img
        elif surface:
            for num, item in enumerate(listing_icon):
                img = surface[num]
                if color_key:
                    if color_key is -1:
                        color_key = img.get_at((0,0))
                    img.set_colorkey(color_key, pygame.RLEACCEL)
                control_icon[item] = img
        else:
            return None
        return control_icon

    def set_icon_size(self, control_icon, size):
        """Resize icon to control dimension."""
        for icon in control_icon:
            width, height = control_icon[icon].get_size()
            if not (width == size[0] and height == size[1]):
                if width != size[0]:
                    w = size[0]
                    h = int( (w/width) * height )
                    if h > size[1]:
                        h = size[1]
                        w = int( (h/height) * width )
                elif height != size[1]:
                    h = size[1]
                    w = int( (h/height) * width )
                    if w > size[0]:
                        w = size[0]
                        h = int( (w/width) * height )
                control_icon[icon] = pygame.transform.smoothscale(control_icon[icon], (w,h))
        return control_icon

    def set_control_size(self, listing, control_icon, size, font_size):
        """Set control size."""
        if not isinstance(size, str):
            width, height = size
        elif size in ('auto', 'auto_width', 'min', 'min_width'):   #size adjusted to largest string
            if listing:
                text_display = self.panel._text(self.panel.image, self.font_type)
                text_display.set_font_size(font_size)
                if listing[0][:-2] != '__numeric':
                    lst = []
                    num_lines = 1
                    for item in listing:
                        if item.startswith('__'):
                            continue
                        item = str(item)
                        if self.split_text:
                            items = item.split(' ')
                            if len(items) > num_lines:
                                num_lines = len(items)
                            lst.extend(items)
                        else:
                            lst.append(item)
                    longest_string = 'x'
                    widest, height = text_display.check_size(longest_string)
                    for item in lst:
                        width, height = text_display.check_size(str(item))
                        if width > widest:
                            longest_string = item
                            widest = width
                    width, height = text_display.check_size(str(longest_string))
                    if num_lines > 1:
                        height = (height * num_lines) + (num_lines)
                else:
                    if len(str(self.numeric['h'])) > len(str(self.numeric['l'])):
                        longest_string = self.numeric['h']
                    else:
                        longest_string = self.numeric['l']
                    width, height = text_display.check_size(str(longest_string))
                if size in ('auto'):
                    if width > height:
                        dim = width
                    else:
                        dim = height
                    width, height = dim, dim
                elif size == 'min':
                    if self.panel._control_minsize:
                        minsize = self.panel._control_minsize
                        if width < minsize['min'][0]:
                            width = minsize['min'][0]
                        if height < minsize['min'][1]:
                            height = minsize['min'][1]
                        if width/height > minsize['size'][0]/minsize['size'][1]:
                            height = int( width * (minsize['size'][1]/minsize['size'][0]) )
                        else:
                            width = int( height * (minsize['size'][0]/minsize['size'][1]) )
                elif size == 'min_width':
                    if self.panel._control_minsize:
                        if self.panel._control_minsize['min'][0] > width:
                            width = self.panel._control_minsize['min'][0]
            else:
                if self.panel._control_minsize:
                    width, height = self.panel._control_minsize['min']
                else:
                    width, height = (20,20)
        else:
            if self.panel._control_minsize:
                width, height = self.panel._control_minsize['size']
            else:
                width, height = (20,20)
        if control_icon:
            if size in ('auto', 'auto_width'):
                w_max = h_max = 0
                for icon in control_icon:
                    icon_w, icon_h = control_icon[icon].get_size()
                    if icon_w > w_max:
                        w_max = icon_w
                    if icon_h > h_max:
                        h_max = icon_h
                icon_width, icon_height = w_max, h_max
                if icon_width > icon_height:
                    if icon_width > width:
                        change = icon_width-width
                        width += change
                        height += change
                else:
                    if icon_height > height:
                        change = icon_height-height
                        width += change
                        height += change
            else:
                icon_width, icon_height = width, height
        else:
            icon_width, icon_height = width, height
        if self.icon_size:
            if self.icon_size[0] > 1:
                icon_width, icon_height = int(self.icon_size[0]), int(self.icon_size[1])
                if size in ('auto', 'auto_width', 'min', 'min_width'):
                    if width < icon_width:
                        width = icon_width
                    if height < icon_height:
                        height = icon_height
                if size == 'min' and self.panel._control_minsize:
                    minsize = self.panel._control_minsize
                    if width/height > minsize['size'][0]/minsize['size'][1]:
                        height = int( width * (minsize['size'][1]/minsize['size'][0]) )
                    else:
                        width = int( height * (minsize['size'][0]/minsize['size'][1]) )
            else:
                icon_width, icon_height = int(width*self.icon_size[0]), int(height*self.icon_size[1])
                self.icon_size = None
        if size in ('min', 'min_width') and self.panel._control_minsize and width <= self.panel._control_minsize['min'][0]:
            padding = self.panel._control_minsize['pad']
        else:
            padding = ( min(width,height) // 10 ) + 4
            if padding % 2:
                padding -= 1
        if size in ('auto', 'auto_width', 'min', 'min_width'):
            width, height = width+padding, height+padding
        else:
            if not self.icon_size:
                if width > 10 and height > 10:
                    icon_width -= padding
                    icon_height -= padding
        size = width, height
        icon_size = icon_width, icon_height
        return size, icon_size

    def set_control_image(self, control_image=None, data_folder=None, data_zip=None, file_obj=None, color_key=None, surface=None):
        """Set image of control."""
        if control_image:
            if isinstance(control_image, str):
                control_image = [control_image]
            if control_image[0] != 'none':
                data_folder, data_zip, color_key = self.panel._data_source(data_folder, data_zip, color_key, file_obj)
                self.control_image['bg'] = self.panel._load_image(control_image[0], path=data_folder, zipobj=data_zip, fileobj=file_obj, colorkey=color_key)
            else:
                if 'bg' in self.control_image:
                    del self.control_image['bg']
        elif surface:
            self.control_image['bg'] = surface.copy()
            if color_key:
                if color_key is -1:
                    color_key = self.control_image['bg'].get_at((0,0))
                self.control_image['bg'].set_colorkey(color_key, pygame.RLEACCEL)
        else:
            try:
                self.control_image['bg'] = self.panel._image_default['control_image']['bg'].copy()
            except:
                if 'bg' in self.control_image:
                    del self.control_image['bg']
        if self.panel._initialized:
            if not self.control_image:
                self.control_outline = True
            else:
                self.control_outline = self.outline
            self.set_buttonlist()
            self.define_buttons(self.control_type, self.size, self.color['normal'], self.color['fill'], initialize=False)
            self.panel.panel_update()
        return self.control_image

    def set_color(self, color=None, activated_color=None, fill=None):
        """Set control color."""
        if color:
            self.color['normal'] = color
        if activated_color:
            self.color['activated'] = activated_color
        if fill:
            self.color['fill'] = fill
        self.define_buttons(self.control_type, self.size, self.color['normal'], self.color['fill'], initialize=False)
        if not self.activated:
            self.active_color = self.color['normal']
        else:
            self.active_color = self.color['activated']
        self.panel._update_panel = True

    def set_tips(self, tip_list=None):
        """Set tips of control list."""
        if tip_list:
            self.tips = {}
            if len(tip_list) == 1:
                self.tips[self.id] = tip_list[0]
            else:
                for item in self.listing:
                    try:
                        self.tips[item] = tip_list.pop(0)
                    except IndexError:
                        self.tips[item] = ''
        else:
            self.tips = {}
        return self.tips

    def set_list(self, control_list, icon_list=None, size=None, icon_size=None, case=False, data_folder=None, data_zip=None, file_obj=None, color_key=None, surface=None, append=False, index=None, keep_link=True, keep_tip=True):
        """Set control listing of a control."""
        if not control_list:
            return
        if not size:
            size = self.size
        if control_list[0] not in ('__numeric_i', '__numeric_f', '__alpha', '__alphanumeric', '__filelist'):
            if append:
                for item in control_list:
                    self.listing.append(str(item))
                self.value = self.listing[self.place]
                self.panel._control_values[self.id] = self.value
                for item in control_list:
                    if self.link:
                        if item not in self.link:
                            self.link[item] = []
                    if self.tips:
                        if item not in self.tips:
                            self.tips[item] = ''
                if icon_list or surface:      #icon in listing
                    listing_icon = []
                    for item in control_list:
                        if item.startswith('__'):
                            listing_icon.append(item)
                    if listing_icon:
                        control_icon = self.set_listing_icon(listing_icon, icon_list, data_folder, data_zip, file_obj, color_key, surface)
                        control_icon = self.set_icon_size(control_icon, self.icon_size)
                        for icon in control_icon:
                            self.control_icon[icon] = control_icon[icon]
            elif index is not None:
                item = str(control_list[0])
                self.listing[index] = item
                if index == self.place:
                    self.value = self.listing[self.place]
                    self.panel._control_values[self.id] = self.value
                if self.link:
                    if item not in self.link:
                        self.link[item] = []
                if self.tips:
                    if item not in self.tips:
                        self.tips[item] = ''
                if icon_list or surface:
                    listing_icon = []
                    if item.startswith('__'):
                        listing_icon.append(item)
                    if listing_icon:
                        control_icon = self.set_listing_icon(listing_icon, icon_list, data_folder, data_zip, file_obj, color_key, surface)
                        control_icon = self.set_icon_size(control_icon, self.icon_size)
                        for icon in control_icon:
                            self.control_icon[icon] = control_icon[icon]
            else:
                size_old = self.size
                pos_old = self.position[0]+self.size[0]//2, self.position[1]+self.size[1]//2
                place_old = self.place
                if not (set(control_list) & set(self.listing)):
                    keep_link = False
                    keep_tip = False
                self.size = size
                self.listing = []
                if keep_link:
                    if self.link:
                        link = self.link
                        self.link = {}
                        for item in control_list:
                            if item in link:
                                self.link[item] = link[item]
                            else:
                                self.link[item] = []
                else:
                    self.link = {}
                if keep_tip:
                    if self.tips:
                        tips = self.tips
                        self.tips = {}
                        for item in control_list:
                            if item in tips:
                                self.tips[item] = tips[item]
                            else:
                                self.tips[item] = ''
                else:
                    self.tips = {}
                if icon_list or surface:
                    if not icon_size:
                        self.icon_size = None
                    else:
                        self.icon_size = icon_size
                self.listing, self.value, self.control_icon, self.icon_size, self.size = self.set_listing(control_list, icon_list, size, case, data_folder, data_zip, file_obj, color_key, surface)
                if self.size != size_old:
                    self.position = pos_old[0]-self.size[0]//2, pos_old[1]-self.size[1]//2
                    if not self.control_image:
                        self.control_outline = True
                    else:
                        self.control_outline = self.outline
                    self.set_buttonlist()
                    self.button, self.rects = self.define_buttons(self.control_type, self.size, self.color['normal'], self.color['fill'])
                try:
                    if self.place > len(self.listing):
                        self.place = len(self.listing)
                    else:
                        self.place = place_old
                    self.value = self.listing[self.place]
                    self.panel._control_values[self.id] = self.value
                except IndexError:
                    self.place = 0
                    self.value = ''
                    self.panel._control_values[self.id] = self.value
        else:
            self.listing = []
            self.set_listing(control_list, icon_list, size)
        if self.listing:
            if ( len(self.listing) > self.hold_response_set ) or ( self.listing[0][:-2] == '__numeric' and abs(self.numeric['h']-self.numeric['l']) > self.hold_response_set ):
                self.hold_response = self.hold_response_set
            else:
                self.hold_response = 0
        self.panel._update_panel = True

    def set_list_icon(self, control_list, icon_list=None, data_folder=None, data_zip=None, file_obj=None, color_key=None, surface=None, icon_size=None):
        """Set control listing icon of a control, changing if item in listing or appending new item."""
        for num, item in enumerate(control_list):
            if not item.startswith('__'):
                control_list[num] = '__'+control_list[num]
        control_icon = self.set_listing_icon(control_list, icon_list, data_folder, data_zip, file_obj, color_key, surface)
        if icon_size:
            if icon_size[0] > 1:
                icon_width, icon_height = int(icon_size[0]), int(icon_size[1])
            else:
                icon_width, icon_height = int(self.size[0]*icon_size[0]), int(self.size[0]*icon_size[1])
                if icon_width % 2:
                    icon_width += 1
                if icon_height % 2:
                    icon_height += 1
            icon_size = icon_width, icon_height
        else:
            icon_size = self.icon_size
        control_icon = self.set_icon_size(control_icon, icon_size)
        for icon in control_icon:
            self.control_icon[icon] = control_icon[icon]
        for item in control_list:
            if item not in self.listing:
                self.listing.append(str(item))
                if self.link:
                    if item not in self.link:
                        self.link[item] = []
                if self.tips:
                    if item not in self.tips:
                        self.tips[item] = ''
        self.define_buttons(self.control_type, self.size, self.color['normal'], self.color['fill'], initialize=False)
        self.panel.panel_update()
        return control_icon

    def get_list(self):
        """Return control listing."""
        return self.listing[:]

    def remove_list(self, items=None, index=None):
        """Remove specified items (or item at index) from control listing, including corresponding tips and links. Passing no parameter removes complete control list."""
        if index is not None:
            item = self.listing[index]
            items = [item]
        elif items is None:
            items = self.listing[:]
        for item in items:
            if item in self.listing:
                self.listing.remove(item)
            if item in self.tips:
                del self.tips[item]
            if item in self.link:
                del self.link[item]
        try:
            if self.place > len(self.listing):
                self.place = len(self.listing)
            self.value = self.listing[self.place]
            self.panel._control_values[self.id] = self.value
        except IndexError:
            self.place = 0
            self.value = ''
            self.panel._control_values[self.id] = self.value
        self.panel._update_panel = True

    def set_label(self, label=None):
        """Set control label."""
        if label is None:
            self.label_text = ''
        else:
            self.label_text = label
        self.panel._update_panel = True

    def get_label(self):
        """Get control label."""
        return self.label_text

    def set_tip(self, *tip):
        """Set tip for a control item. Parameters: tip:str/[] single control tip or tip list for control list items; or tuple item:str,tip:str tip for control list item."""
        tip_length = len(tip)
        if tip_length == 1:
            item = None
            tip = tip[0]
        elif tip_length == 2:
            item = tip[0]
            tip = tip[1]
        elif tip_length == 0:
            tip = 0
        else:
            raise TypeError('set_tip() arguments incorrect.')
        if tip:
            if isinstance(tip, str):
                tip = [tip]
            if item is not None:
                if item in self.listing:
                    if not self.tips:
                        for item in self.listing:
                            self.tips[item] = ''
                    self.tips[item] = tip[0]
                    return True
                else:
                    return False
            else:
                self.set_tips(tip)
                return True
        else:
            if self.tips:
                if item:
                    self.tips[item] = ''
                else:
                    self.tips = {}
            return True

    def get_tip(self, item=None):
        """Get the tip for a control item, or list of tips if no parameter given. Parameter: item:str"""
        if item:
            if item in self.tips:
                return self.tips[item]
            else:
                return None
        else:
            return self.tips

    def set_link(self, control, link):
        """Set linked controls. Parameters: control:str, link:[]."""
        if control in self.listing:
            if not self.link:
                for item in self.listing:
                    self.link[item] = []
            self.link[control] = link
            return True
        else:
            return False

    def set_link_activated(self, setting='Toggle'):
        """Set whether linked control active immediately or upon control button activation."""
        link_change = False
        if setting == 'Toggle':
            self.link_activated = not self.link_activated
            link_change = True
        elif setting in (True, False):
            self.link_activated = setting
            link_change = True
        if link_change:
            if self.control_type == 'function_select':
                self.check_link(self.id, True)
            return self.link_activated
        else:
            return None

    def get_id(self):
        """Get control identity"""
        return self.id

    def get_position(self):
        """Retrieve control position."""
        pos_x, pos_y = self.position
        pos_x, pos_y = pos_x + (self.size[0]//2), pos_y + (self.size[1]//2)
        return pos_x, pos_y

    def get_size(self):
        """Retrieve control size."""
        return self.size

    def is_activated(self):
        """Check whether control is activated."""
        return self.activated

    def set_activated(self, setting='Toggle'):
        """Set control activated."""
        change = False
        if setting == 'Toggle':
            self.activated = not self.activated
            change = True
        elif setting in (True, False):
            self.activated = setting
            change = True
        if change:
            if self.link and not self.link_activated:
                for button in self.link[self.value]:
                    self.panel._controls[button].active = self.activated
            if not self.activated:
                self.active_color = self.color['normal']
            else:
                self.active_color = self.color['activated']
            self.panel._update_panel = True
            return self.activated
        else:
            return None

    def is_activated_lock(self):
        """Check control activate lock."""
        return self.activated_lock

    def set_activated_lock(self, setting='Toggle'):
        """Set control activate lock."""
        if setting == 'Toggle':
            self.activated_lock = not self.activated_lock
        elif setting in (True, False):
            self.activated_lock = setting
        self.activated_toggle = not self.activated_lock
        self.panel._update_panel = True
        return self.activated_lock

    def set_value(self, value, change_index=True):
        """Set the value of a control. Parameters: value - control value; change_index - True change list index to first available value, False to leave index position unchanged, index number for specific index if is value."""
        self.check_link(self.id, False)
        if self.list_type[:9] != '__numeric':
            self.value = str(value)
        else:
            if self.list_type[9:] == '_i':
                try:
                    value = int(value)
                    self.value = value
                    self.numeric['value'] = str(self.value)
                except ValueError:
                    self.value = value
                    change_index = False
            else:
                try:
                    value = round(float(value),self.numeric['precision'])
                    self.value = value
                    self.numeric['value'] = str(self.value)
                except ValueError:
                    self.value = value
                    change_index = False
        self.panel._control_values[self.id] = self.value
        if change_index is not False:
            if change_index is True:
                if value in self.listing:
                    self.place = self.listing.index(value)
            else:
                try:
                    if self.listing[change_index] == self.value:
                        self.place = change_index
                except IndexError:
                    pass
        if self.is_active():
            self.check_link(self.id, True)
        self.panel._update_panel = True
        return self.value, self.place

    def get_value(self):
        """Get the value of a control."""
        return self.value

    def set_list_index(self, index):
        """Set the place in control listing."""
        if self.list_type[:9] != '__numeric':
            if index >= 0 and index < len(self.listing):
                self.place = index
                self.set_value(self.listing[self.place], change_index=False)
        else:
            self.set_value(index)
        return self.value

    def get_list_index(self, item=None):
        """Get the current place in control listing, or index of first occurrence of item."""
        if self.list_type[:9] != '__numeric':
            if item is None:
                return self.place
            else:
                try:
                    index = self.listing.index(item)
                    return index
                except ValueError:
                    return None
        else:
            return self.value

    def is_active(self):
        """Check whether a control is active."""
        return self.active

    def set_active(self, setting='Toggle'):
        """Set control active setting."""
        if setting == 'Toggle':
            self.active = not self.active
            self.panel._update_panel = True
            return self.active
        elif setting in (True, False):
            self.active = setting
            self.panel._update_panel = True
            return self.active
        else:
            return None

    def is_enabled(self):
        """Check whether control is enabled."""
        return self.enabled

    def set_enabled(self, setting='Toggle'):
        """Set control enabled setting."""
        if setting == 'Toggle':
            if not self.enabled:
                self.panel.enable_control(self.id)
            else:
                self.panel.disable_control(self.id)
            return self.enabled
        elif setting in (True, False):
            if setting:
                self.panel.enable_control(self.id)
            else:
                self.panel.disable_control(self.id)
            return self.enabled
        else:
            return None

    def set_buttonlist(self):
        """List specifying button members of a control. Designations for control 'id': main button:'id', button switches:'id_top'/'id_bottom'."""
        self.button_list = []
        if self.control_type in ('function_select', 'function_toggle', 'control_select', 'control_toggle'):
            if self.control_image:
                self.button_list.append(self.id+'_bg')
                if self.control_outline:
                    self.button_list.append(self.id)
            else:
                if self.control_outline:
                    self.button_list.append(self.id)
            if self.control_type in ('function_select', 'control_select'):
                self.button_list.extend([self.id+'_top', self.id+'_bottom'])
        return self.button_list

    def resize_control(self, size):
        """Resize control."""
        self.icon_size = None
        pos_old = self.position[0]+self.size[0]//2, self.position[1]+self.size[1]//2
        self.size, self.icon_size = self.set_control_size(self.listing, self.control_icon, size, self.font_size)
        if self.control_icon:
            self.control_icon = self.set_icon_size(self.control_icon, self.icon_size)
        self.position = pos_old[0]-self.size[0]//2, pos_old[1]-self.size[1]//2
        self.button, self.rects = self.define_buttons(self.control_type, self.size, self.color['normal'], self.color['fill'])
        label_size = self.label.get_font_size()
        label_position = ( self.position[0]+(self.size[0]//2), self.position[1]-(label_size+3) )
        self.label.set_position((label_position),center=True)
        self.panel._update_panel = True        

    def set_display_info(self, size, font_color, font_type, font_size, position=None, text=None):
        """Initiate control display text."""
        if text:    #set display text
            self.value = text
            self.panel._control_values[self.id] = self.value
        display = self.panel._text(self.panel.image, font_type)
        display.set_font_size(font_size)
        display.set_font_color(font_color)
        display.set_font_bgcolor(None)
        if self.control_type == 'label':
            display.set_position((self.position),center=True)
            return display
        display.split_text = self.split_text
        if not position:
            width, height = display.check_size('x')
            position = ( self.position[0]+(size[0]//2), self.position[1]+(size[1]//2)-(height//2) )
        display.set_position((position),center=True)
        return display

    def set_display_text(self, font_color=None, font_bgcolor=None, font_type=None, font_size=None, split_text=None, size=None, info=False):
        """Set display text properties."""
        update_control = False
        if font_color:
            self.font_color = font_color
            self.display.set_font_color(self.font_color)
        if font_bgcolor:
            self.display.set_font_bgcolor(font_bgcolor)
        if font_type:
            if isinstance(font_type, str):
                font_type = [font_type]
            self.display.set_font(font_type)
            update_control=True
        if font_size:
            self.font_size = font_size
            self.display.set_font_size(self.font_size)
            update_control = True
        if split_text is not None:
            self.split_text = split_text
            self.display.set_split_text(self.split_text)
            update_control = True
        if update_control:
            if not size:
                size = self.size
            self.icon_size = None
            pos_old = self.position[0]+self.size[0]//2, self.position[1]+self.size[1]//2
            self.size, self.icon_size = self.set_control_size(self.listing, self.control_icon, size, self.font_size)
            if self.control_icon:
                self.control_icon = self.set_icon_size(self.control_icon, self.icon_size)
            self.position = pos_old[0]-self.size[0]//2, pos_old[1]-self.size[1]//2
            self.button, self.rects = self.define_buttons(self.control_type, self.size, self.color['normal'], self.color['fill'])
            width, height = self.display.check_size('x')
            position = ( self.position[0]+(self.size[0]//2), self.position[1]+(self.size[1]//2)-(height//2) )
            self.display.set_position((position),center=True)
            label_size = self.label.get_font_size()
            label_position = ( self.position[0]+(self.size[0]//2), self.position[1]-(label_size+3) )
            self.label.set_position((label_position),center=True)
        self.panel._update_panel = True
        if info:
            if info == 'font':
                return self.display.get_font()
            elif info == 'default':
                return self.display.get_font('default')
            elif info == 'system':
                return self.display.get_font('system')

    def set_label_info(self, size, font_color, font_type, font_size, position=None, text=None):
        """Initiate control label text."""
        if text:    #set label text
            self.label_text = text
            return
        label = self.panel._text(self.panel.image, font_type)
        label.set_font_size(font_size)
        label.set_font_color(font_color)
        label.set_font_bgcolor(None)
        if self.control_type == 'label':
            label.set_position((self.position[0], self.position[1]-(font_size+3)),center=True)
            return label
        if not position:
            position = ( self.position[0]+(size[0]//2), self.position[1]-(font_size+3) )
        if not text:
            text = self.id
        label.set_position((position),center=True)
        return label

    def set_label_text(self, font_color=None, font_bgcolor=None, font_type=None, font_size=None, split_text=None):
        """Set label text properties."""
        update_position = False
        if font_color:
            self.label.set_font_color(font_color)
        if font_bgcolor:
            self.label.set_font_bgcolor(font_bgcolor)
        if font_type:
            if isinstance(font_type, str):
                font_type = [font_type]
            self.label.set_font(font_type)
        if font_size:
            self.label.set_font_size(font_size)
            update_position = True
        if split_text is not None:
            self.label.set_split_text(split_text)
            update_position = True
        if update_position:
            if self.label.split_text and self.label_text.count(' '):
                num_lines = len(self.label_text.split(' '))
                self.label.y = self.position[1]-(((self.label.font_size-2)*num_lines)+2)
            else:
                self.label.y = self.position[1]-(self.label.font_size+2)
        self.panel._update_panel = True

    def check_link(self, ctrl, activate):
        """Maintain active state of linked controls."""
        control = self.panel._controls[ctrl]
        if control.link:
            if not activate:
                try:
                    for ctr in control.link[control.value]:
                        self.panel._controls[ctr].set_active(False)
                        if not self.panel._controls[ctr].is_activated_lock():
                            self.panel._controls[ctr].set_activated(False)
                        self.check_link(ctr, activate)
                except KeyError:
                    pass
            else:
                if (control.control_type == 'function_select' and control.link_activated) or control.control_type == 'function_toggle':
                    try:
                        for ctr in control.link[control.value]:
                            self.panel._controls[ctr].set_active(True)
                            self.check_link(ctr, activate)
                    except KeyError:
                        pass
                else:
                    try:
                        for ctr in control.link[control.value]:
                            self.panel._controls[ctr].set_active(control.activated)
                            self.check_link(ctr, control.activated)
                    except KeyError:
                        pass

    def reset(self, change_index=True):
        """Reset value to start of control list."""
        if self.list_type[:9] == '__numeric':
            if change_index:
                self.value = self.numeric['l']
            else:
                if self.listing[0][-1] == 'i':
                    self.value = int(self.numeric['value'])
                else:
                    self.value = float(self.numeric['value'])
            self.panel._control_values[self.id] = self.value
        else:
            self.check_link(self.id, False)
            if change_index:
                self.place = 0
            self.value = self.listing[self.place]
            self.panel._control_values[self.id] = self.value
            if self.is_active():
                self.check_link(self.id, True)
        self.panel._update_panel = True
        return self.value

    def next(self):
        """Set value to next in control list."""
        if self.list_type[:9] == '__numeric':
            self.action(self.button_forward)
        else:
            self.check_link(self.id, False)
            if self.place < len(self.listing)-1:
                self.place += 1
            else:
                self.place = 0
            self.value = self.listing[self.place]
            self.panel._control_values[self.id] = self.value
            if self.is_active():
                self.check_link(self.id, True)
        self.panel._update_panel = True
        return self.value

    def previous(self):
        """Set value to previous in control list."""
        if self.list_type[:9] == '__numeric':
            self.action(self.button_reverse)
        else:
            self.check_link(self.id, False)
            if self.place > 0:
                self.place -= 1
            else:
                self.place = len(self.listing)-1
            self.value = self.listing[self.place]
            self.panel._control_values[self.id] = self.value
            if self.is_active():
                self.check_link(self.id, True)
        self.panel._update_panel = True
        return self.value

    def action_numeric_i(self, button):
        """Function of integer numeric control."""
        def greater(val1, val2, direction=1):
            if val1 > val2:
                return direction >= 0
            else:
                return not (direction >= 0)
        if button == self.id:
            self.activated = not self.activated
        elif button == self.button_forward:
            self.activated = False
            try:
                self.value += self.numeric['step']
            except TypeError:
                if self.listing[0][-1] == 'i':
                    self.value = int(self.numeric['value']) + self.numeric['step']
                else:
                    self.value = float(self.numeric['value']) + self.numeric['step']
            if greater(self.value, self.numeric['h'], self.numeric['step']) and self.value != self.numeric['h']:
                if self.loop:
                    self.value = self.numeric['l']
                else:
                    self.value = self.numeric['h']
            self.numeric['value'] = str(self.value)
        elif button == self.button_reverse:
            self.activated = False
            try:
                self.value -= self.numeric['step']
            except TypeError:
                if self.listing[0][-1] == 'i':
                    self.value = int(self.numeric['value']) - self.numeric['step']
                else:
                    self.value = float(self.numeric['value']) - self.numeric['step']
            if not greater(self.value, self.numeric['l'], self.numeric['step']) and self.value != self.numeric['l']:
                if self.loop:
                    self.value = self.numeric['h']
                else:
                    self.value = self.numeric['l']
            self.numeric['value'] = str(self.value)

    def action_numeric_f(self, button):
        """Function of float numeric control."""
        self.action_numeric_i(button)
        self.value = round(self.value, self.numeric['precision'])
        integer, fractional = str(self.value).rsplit('.')
        fractional = fractional[:self.numeric['precision']]
        self.numeric['value'] = integer + '.' + fractional

    def action(self, button):
        """Function of control."""
        if self.control_type == 'function_select':
            if button == self.id:
                self.activated = not self.activated
                self.check_link(self.id, self.activated)
            elif button == self.button_forward:
                self.activated = False
                self.check_link(self.id, False)
                if self.place < len(self.listing)-1:
                    self.place += 1
                else:
                    if self.loop:
                        self.place = 0
                    else:
                        self.place = len(self.listing)-1
                try:
                    self.value = self.listing[self.place]
                except IndexError:
                    self.value = ''
                self.check_link(self.id, True)
            elif button == self.button_reverse:
                self.activated = False
                self.check_link(self.id, False)
                if self.place > 0:
                    self.place -= 1
                else:
                    if self.loop:
                        self.place = len(self.listing)-1
                    else:
                        self.place = 0
                try:
                    self.value = self.listing[self.place]
                except IndexError:
                    self.value = ''
                self.check_link(self.id, True)
        elif self.control_type == 'function_toggle':
            if button == self.id:
                self.check_link(self.id, False)
                self.activated = not self.activated
                if self.place < len(self.listing)-1:
                    self.place += 1
                else:
                    self.place = 0
                try:
                    self.value = self.listing[self.place]
                except IndexError:
                    self.value = ''
                self.check_link(self.id, True)
        elif self.control_type == 'control_select':
            if self.listing:
                if self.listing[0][:-2] == '__numeric':
                    { 'i':self.action_numeric_i,'f':self.action_numeric_f }[self.listing[0][-1]](button)
                else:
                    if button == self.id:
                        self.activated = not self.activated
                        self.value = self.listing[self.place]
                    elif button == self.button_forward:
                        self.activated = False
                        if self.place < len(self.listing)-1:
                            self.place += 1
                        else:
                            if self.loop:
                                self.place = 0
                            else:
                                self.place = len(self.listing)-1
                        self.value = self.listing[self.place]
                    elif button == self.button_reverse:
                        self.activated = False
                        if self.place > 0:
                            self.place -= 1
                        else:
                            if self.loop:
                                self.place = len(self.listing)-1
                            else:
                                self.place = 0
                        self.value = self.listing[self.place]
        elif self.control_type == 'control_toggle':
            if self.listing[0][:-2] == '__numeric':
                if button == self.id:
                    button = self.button_forward
                { 'i':self.action_numeric_i,'f':self.action_numeric_f }[self.listing[0][-1]](button)
            else:
                if button == self.id:
                    self.activated = not self.activated
                    if self.place < len(self.listing)-1:
                        self.place += 1
                    else:
                        self.place = 0
                try:
                    self.value = self.listing[self.place]
                except IndexError:
                    self.value = ''
        if not self.activated:
            self.active_color = self.color['normal']
        else:
            self.active_color = self.color['activated']
        self.panel._control_values[self.id] = self.value
        return self.value

