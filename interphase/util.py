"""
Interphase
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import pygame
import os
import zipfile
import cStringIO

class Text(object):
    """
    Receives text to display on surface.
    
    Parameters:
        surface: 'surface' destination surface for text.
        font_type: [] list of font names
        font_size: int font size (6,8,10,12,24,32)
    """

    font = {}

    def __init__(self, surface, font_type=None, font_size=None):
        self.screen = surface
        x, y = self.screen.get_size()
        self.dimension = {'x':x, 'y':y}
        self.message = None
        self.messages = []
        if font_size and font_size in (6, 8, 10, 12, 24, 32):
            self.font_size = font_size
        else:
            self.font_size = 10
        if isinstance(font_type, str):
            font_type = [font_type]
        if not Text.font:
            pygame.font.init()
            font = None
            if font_type:
                font_type = ','.join(font_type)
                if font_type.startswith('file:'):
                    font = font_type[5:].strip()
                    if not os.path.exists(font):
                        print('Font not found: %s' % font)
                        font = None
                else:
                    font = pygame.font.match_font(font_type)
            if not font:
                font_type = 'verdana, tahoma, bitstreamverasans, freesans, arial'
                font = pygame.font.match_font(font_type)
            Text.font['default'] = font
            Text.font['defaults'] = font_type
            Text.font[font] = { self.font_size:pygame.font.Font(font,self.font_size) }
        if font_type:
            font_type = ','.join(font_type)
            if font_type != Text.font['defaults']:
                if font_type.startswith('file:'):
                    font_type = font_type[5:].strip()
                    if not os.path.exists(font_type):
                        print('Font not found: %s' % font_type)
                        font_type = None
                else:
                    font_type = pygame.font.match_font(font_type)
                if font_type:
                    if font_type not in Text.font:
                        Text.font[font_type] = { self.font_size:pygame.font.Font(font_type,self.font_size) }
                    else:
                        if self.font_size not in Text.font[font_type]:
                            Text.font[font_type][self.font_size] = pygame.font.Font(font_type,self.font_size)
                else:
                    font_type = Text.font['default']
            else:
                font_type = Text.font['default']
        else:
            font_type = Text.font['default']
        self.font_type = font_type
        self.font = Text.font[self.font_type]
        self.x = 0
        self.y = 0
        self.center = False
        self.font_color = (255,0,0)
        self.font_bgcolor = (0,0,0)
        self.split_text = False

    def __call__(self, surface='default'):
        """Writes text to surface."""
        if surface == 'default':
            self.surface = self.screen
        else:
            self.surface = surface
        self.update()
        return self.surface

    def add(self,*message_append):
        """Add to text."""
        for item in message_append:
            self.message = str(item)
            self.messages.append(self.message)

    def set_position(self, position, center=False):
        """Set position to write text."""
        x, y = position
        if x < self.dimension['x'] and y < self.dimension['y']:
            self.x = x
            self.y = y
            if center:
                self.center = True
            return True
        else:
            return False

    def set_font(self, font_type, default=False):
        """Set font of text."""
        if isinstance(font_type, str):
            font_type = [font_type]
        font_type = ','.join(font_type)
        if font_type == 'default':
            font_type = Text.font['default']
            self.font = Text.font[font_type]
            self.font_type = font_type
        elif font_type != Text.font['defaults']:
            if font_type.startswith('file:'):
                font = font_type[5:].strip()
                if not os.path.exists(font):
                    print('Font not found: %s' % font)
                    font = None
            else:
                font = pygame.font.match_font(font_type)
            if font:
                if font not in Text.font:
                    Text.font[font] = { self.font_size:pygame.font.Font(font,self.font_size) }
                self.font = Text.font[font]
                self.font_type = font
                if default:
                    Text.font['default'] = font
                    Text.font['defaults'] = font_type

    def get_font(self, font_info='font'):
        """Get current font."""
        if font_info == 'font':
            return self.font_type
        elif font_info == 'default':
            return Text.font['default']
        elif font_info == 'system':
            return pygame.font.get_fonts()

    def get_font_size(self):
        """Get current font size."""
        return self.font_size

    def set_font_size(self, size):
        """Set font size of text."""
        if size in (6, 8, 10, 12, 24, 32):
            self.font_size = size
            if size not in Text.font[self.font_type]:
                Text.font[self.font_type][self.font_size] = pygame.font.Font(self.font_type,self.font_size)
            self.font = Text.font[self.font_type]
            return True
        else:
            return False

    def set_font_color(self, color):
        """Set font color of text."""
        self.font_color = color

    def set_font_bgcolor(self, color=None):
        """Set font background color."""
        self.font_bgcolor = color

    def set_split_text(self, split_text=True):
        """Set whether text split to new line at space."""
        self.split_text = split_text

    def check_size(self, text):
        """Get size required for given text."""
        width, height = self.font[self.font_size].size(text)
        return width, height

    def has_text(self):
        """Check whether contains text."""
        if self.messages:
            return True
        else:
            return False

    def clear_text(self):
        """Clear text."""
        self.message = None
        self.messages = []

    def tprint(self):
        """Print text to surface."""
        if self.messages != []:
            text = " ".join(self.messages)
            if not self.split_text or text.strip().count(' ') == 0:
                if self.font_bgcolor:
                    self.text_surface = self.font[self.font_size].render(text, True, self.font_color, self.font_bgcolor)
                else:
                    self.text_surface = self.font[self.font_size].render(text, True, self.font_color)
                if self.center:
                    center = self.text_surface.get_width()//2
                    x = self.x - center
                else:
                    x = self.x
                text_rect = self.text_surface.get_rect()
                self.surface.blit(self.text_surface, (x,self.y))
            else:
                words = text.count(' ')
                position_y = self.y - (words)*((self.font_size+2)//2)
                texts = text.split(' ')
                for count, text in enumerate(texts):
                    if self.font_bgcolor:
                        self.text_surface = self.font[self.font_size].render(text, True, self.font_color, self.font_bgcolor)
                    else:
                        self.text_surface = self.font[self.font_size].render(text, True, self.font_color)
                    if self.center:
                        center = self.text_surface.get_width()//2
                        x = self.x - center
                        y = position_y + (count*(self.font_size+2))
                    else:
                        x = self.x
                        y = position_y + (count*(self.font_size+2))
                    text_rect = self.text_surface.get_rect()
                    self.surface.blit(self.text_surface, (x,y))
            self.message = None
            self.messages = []
            return text_rect

    def update(self):
        self.tprint()


def load_image(filename, frames=1, path='data', zipobj=None, fileobj=None, colorkey=None, errorhandle=True, errorreport=True):
    """Loads images."""
    #Modified from PygameChimpTutorial
    def convert_image(image, colorkey):
        if image.get_alpha():
            image = image.convert_alpha()
        else:
            image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    if zipobj:
        if isinstance(zipobj, str):
            if path:
                data_file = os.path.join(path, zipobj)
            else:
                data_file = zipobj
            dat = zipfile.ZipFile(data_file)
            fileobj = cStringIO.StringIO(dat.open(filename).read())
            dat.close()
        else:
            fileobj = cStringIO.StringIO(zipobj.open(filename).read())
        full_name = fileobj
        namehint = filename
    elif fileobj:
        full_name = fileobj
        namehint = filename
    else:
        if path:
            full_name = os.path.join(path, filename)
        else:
            full_name = filename
        namehint = ''
    try:
        if frames == 1:
            image = pygame.image.load(full_name, namehint)
            image = convert_image(image, colorkey)
            return image
        elif frames > 1:
            images = []
            image = pygame.image.load(full_name, namehint)
            width, height = image.get_size()
            width = width // frames
            for frame in range(frames):
                frame_num = width * frame
                image_frame = image.subsurface((frame_num,0), (width,height)).copy()
                image_frame.set_alpha(image.get_alpha())
                image_frame = convert_image(image_frame, colorkey)
                images.append(image_frame)
            return images
    except pygame.error, message:
        if errorhandle:
            raise
        else:
            if errorreport:
                print(message)
            raise IOError
            return None

