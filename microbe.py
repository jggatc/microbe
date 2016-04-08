#!/usr/bin/env python
from __future__ import division

"""
Microbe - Microbial Simulation
Copyright (C) 2009 James Garnon

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Microbe version 1.23
Download Site: http://gatc.ca

Dependencies:
    Python 2.5:             http://www.python.org/
    Pygame 1.8:             http://www.pygame.org/
    Numpy 1.4:              http://numpy.scipy.org/
    Psyco (optional):       http://psyco.sourceforge.net/
"""

version = '1.23'

monitoring = False
profiling = False

try:
    import pygame
    import numpy
except ImportError:
    raise ImportError, "Pygame and Numpy modules are required."

if not monitoring:
    import warnings
    warnings.filterwarnings("ignore")

import optparse

import interphase      #interface control
from matrix import Matrix
from control import Control
from cells import Algae, Bacterium, Paramecium, Amoeba, Ciliate


def program_options():
    config = {'species_added':None, 'species_evolving':None, 'display_gamma':None}
    try:
        config_file = open('config.ini')
        cfg_setting = [line.strip().split(' ',1) for line in config_file if line[:1].isalpha()]
        cfg_setting = dict(cfg_setting)
        for cfg in config:
            if cfg in cfg_setting:
                config[cfg] = cfg_setting[cfg].strip()
        config_file.close()
    except (IOError, ValueError):
        pass
    program_usage = "%prog [options]"
    program_desc = ("Microbe - Microbial Simulation")
    parser = optparse.OptionParser(usage=program_usage,description=program_desc)
    parser = optparse.OptionParser(version="Microbe "+version)
    parser.set_defaults(evolve=False)
    parser.add_option("--license", dest="license", action="store_true", help="display program license")
    parser.add_option("-d", "--doc", dest="doc", action="store_true", help="display program documentation")
    parser.add_option("-s", dest="species_added", action="store", help="-s algae:bacterium:paramecium:amoeba:ciliate")
    parser.add_option("-e", dest="species_evolving", action="store", help="-e bacterium:paramecium:amoeba:ciliate")
    parser.add_option("-g", dest="display_gamma", action="store", help="-g value (value: 0.5 to 3.0)")
    (options, args) = parser.parse_args()
    if options.license:
        try:
            license_info = open('license.txt')
        except IOError:
            print("GNU General Public License version 3 or later: http://www.gnu.org/licenses/")
            sys.exit()
        for line_no, line in enumerate(license_info):
            print(line),
            if line_no and not line_no % 20:
                answer = raw_input("press enter to continue, 'q' to quit: ")
                if answer == 'q':
                    break
        license_info.close()
        sys.exit()
    if options.doc:
        try:
            documentation = open('readme.txt')
        except IOError:
            print("Documentation not found.")
            sys.exit()
        for line_no, line in enumerate(documentation):
            print(line),
            if line_no and not line_no % 20:
                answer = raw_input("press enter to continue, 'q' to quit: ")
                if answer == 'q':
                    break
        documentation.close()
        sys.exit()
    if options.species_added:
        config['species_added'] = options.species_added
    if options.species_evolving:
        config['species_evolving'] = options.species_evolving
    if options.display_gamma:
        config['display_gamma'] = options.display_gamma
    if config['species_added']:
        config['species_added'] = config['species_added'].lower().split(':')
        config['species_added'] = [sp.strip() for sp in config['species_added']]
    if config['species_evolving']:
        config['species_evolving'] = config['species_evolving'].lower().split(':')
        config['species_evolving'] = [sp.strip() for sp in config['species_evolving']]
    if config['display_gamma']:
        try:
            config['display_gamma'] = float(config['display_gamma'])
        except ValueError:
            config['display_gamma'] = None
    return config


def setup():
    species = { 'algae':True, 'bacterium':True, 'paramecium':True, 'amoeba':True, 'ciliate':True }
    species_class = { 'algae':Algae, 'bacterium':Bacterium, 'paramecium':Paramecium, 'amoeba':Amoeba, 'ciliate':Ciliate }
    config = program_options()
    if config['display_gamma']:
        gamma = config['display_gamma']
        if gamma > 0.0 and gamma < 0.5:
            gamma = 0.5
        elif gamma > 3.0:
            gamma = 3.0
    else:
        gamma = 0
    if config['species_added']:
        for sp in species:
            if sp not in config['species_added']:
                species[sp] = False
    parameters = {}
    parameters['matrix_size'] = (1500,1500)
    parameters['display_size'] = (500,500)
    parameters['gamma'] = gamma
    matrix = Matrix(parameters)
    matrix.setup(algae=species['algae'],bacterium=species['bacterium'],paramecium=species['paramecium'],amoeba=species['amoeba'],ciliate=species['ciliate'])
    if config['species_evolving']:
        for sp in species_class:
            if sp in config['species_evolving'] and species_class[sp].gene:
                species_class[sp].evolving = True
                matrix.set_evolution(True)
    control = Control(matrix)
    return matrix, control


def main():
    matrix, control = setup()
    while not control.quit:
        if control.clock.get_fps() > 20:
            pygame.display.update(matrix.update_list)
        else:
            pygame.display.flip()
        matrix.update()
        control.update()


if __name__ == '__main__':
    if not monitoring and not profiling:
        main()
    else:
        if monitoring:
            from util_dev import monitor
            matrix, control = setup()
            print_message = interphase.Text(matrix.screen)
            monitor(matrix,control,print_message)
        elif profiling:
            from util_dev import profile
            profile()

