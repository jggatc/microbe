"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon
"""

from __future__ import division
import pygame
import os
import math


def load_image(file_name, frames=1, path='data', colorkey=None, errorhandle=True):
    #Modified from PygameChimpTutorial
    full_name = os.path.join(path, file_name)
    try:
        if frames == 1:
            image = pygame.image.load(full_name)
        elif frames > 1:
            images = []
            image = pygame.image.load(full_name)
            width, height = image.get_size()
            width = width // frames
            for frame in range(frames):
                frame_num = width * frame
                image_frame = image.subsurface((frame_num,0), (width,height)).copy()
                images.append(image_frame)
            return images
    except pygame.error:
        if errorhandle:
            raise
        else:
            print(message)
            return None
    if image.get_alpha():
        image = image.convert_alpha()
    else:
        image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)
    return image


def trig_compute():
    sin_table = {}
    cos_table = {}
    for angle in range(0,360):
        angle_rad = angle * math.pi/180
        sin_angle = math.sin(angle_rad)
        cos_angle = math.cos(angle_rad)
        sin_table[angle] = sin_angle
        cos_table[angle] = cos_angle
    return sin_table, cos_table
sin_table, cos_table = trig_compute()

