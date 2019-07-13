Microbe - Microbial Simulation
Version 1.25
http://gatc.ca/projects/microbe/

Microbe is a microbial simulation coded in Python and Pygame. The source is run with 'python microbe.py'. Also available are executables that have Python dependencies included, and run with './microbe' (Linux) or 'microbe.exe' (Windows). Microbe is released under the GPL3 License, see LICENSE.txt for further information.

Dependencies:
    Python 2.7+:         http://www.python.org/
    Pygame 1.8+:         http://www.pygame.org/
    Numpy 1.4+:          http://numpy.scipy.org/

Command line options:
  -h, --help           show this help message and exit
  -d, --doc            display program documentation
  -s SPECIES_ADDED     -s algae:bacterium:paramecium:amoeba:ciliate
  -e SPECIES_EVOLVING  -e bacterium:paramecium:amoeba:ciliate
  -g DISPLAY_GAMMA     -g value (value: 0.5 to 3.0)
  >options can also be set in config.ini

Control panel:
    Tool selection:
        Nutrient, Toxin, Algae, Bacterium, Paramecium, Ciliate, Amoeba,
        Magnify, Track, Tag, Evolution, Set Gene, Set ID, Save, Load
    Click on tool toggles select

Keyboard shortcuts:
    g: Nutrient
    t: Toxin
    v: Algae
    b: Bacterium
    p: Paramecium
    o: Ciliate
    a: Amoeba
    v,b,p,o,a & SHIFT: Add creatures
    i: interface panel toggle
    c: compass/edge-scroll toggle
    e: evolution mode toggle
    UP, DOWN, LEFT, RIGHT: scroll
    x: track remove
    d: tag toggle
    z: zoom on / zoom_power
    z & SHIFT: zoom off
    ESC: track/zoom off
    TAB: Pause toggle
    q & CONTROL: Quit

Mouse functions:
    left: tool activate
    right: track creature
        +SHIFT: tag creature
                select species evolve in evolution mode
        +CTRL&SHIFT: remove creature
    middle: zoom on/off
    wheel: zoom power
    clicking compass rose brings up control panel

Evolution mode:
During evolution, species with defined genes will be under natural selection. Determining which species evolves in evolution mode (determined by asterisk on panel) can be toggled with mouse shift-left click, and if evolving the individuals id of that species will be displayed. Species evolving in evolution mode will have a fitness function derived from survival of the fittest, and if succeed will pass on genes, with possibility of mutation, to a new individual.

Save/Load:
Creature selected can be saved. The saved files will be put in data subfolder with filenames species_xxx.dat, where xxx can be defined during saving. The creatures id and genes will be saved, recording changes from functions set id, set gene, and genes selected in evolution mode. By including a png image of same name, i.e. species_xxx.png, that image will be used, as examples species_bac and species_par in data subfolder. In load mode, saved creatures can be selected, then entered with mouse.

