#!/usr/bin/env python

"""
Interphase
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

Interphase version 0.81
Download Site: http://gatc.ca

Dependencies:

    Python 2.5:   http://www.python.org/
    Pygame 1.8:   http://www.pygame.org/


The module adds interface panel functionality to a Pygame application.
Place the interphase folder in the path or within script folder, and
use 'import interphase'. A zip of the interphase folder can also be
used with the statement "sys.path.insert(0,'./interphase_zipfile')"
prior to import. Run interphase.py separately for an interface panel
demo that is coded in test.py.

To design an interface panel, interphase.Interface can be subclassed.
Within the __init__() method call interphase.Interface.__init__().
Interface Object provides several methods to design and utilize an
interface panel. Use add() to add controls to panel, place into a method
called add_controls(); if added otherwise call activate() after to
activate the panel. The Interface class/subclass instance can be added
to a pygame sprite group that provides methods update/draw/clear to
update the panel. The program maintains the update of the panel including
changes through the methods, however panel_update() can be used to force
an update if required. If the Interface Object is subclassed, when
overriding the update() method call interphase.Interface.update().
Interface interaction can be maintained with the InterfaceState object,
that is returned by update() or get_state(), or through pygame event
queue checking for event.type interphase.EVENT['controlselect']
and interphase.EVENT['controlinteract'] with the attribute event.state
that references the InterfaceState object. To turn the panel off,
deactivate() sets state.active to false.


InterfaceState Object:

panel:
  - Interface panel (instance panel object)
controls:
  - Interface controls (dict {id:object} panel controls object)
panel_active:
  - Panel active (bool panel active)
panel_interact:
  - Pointer interface interact (bool pointer interact with panel)
control_interact:
  - Pointer control interact ('id' control interact)
button_interact:
  - Pointer button interact ('id' button interact)
control:
  - Control selected ('id' selected control)
button:
  - Button selected ('id' selected button ('id','id_top','id_bottom'))
value:
  - Control value ('value' current value of selected control)
values:
  - Panel control values (dict {'id':value} values of all controls)


Interface Object methods:

add()/add_control(), activate(), deactivate(), is_active(), get_state(),
get_value(), get_control(), remove_control(), enable_control(),
disable_control(), update(), panel_update(), set_panel_display(),
get_id(), set_panel_image(), set_control_image(), set_button_image(),
get_panel_image(), get_default_image(), move(), set_moveable(),
is_moveable(), set_label_display(), is_label_display(), get_size(),
get_position(), move_control(), get_control_move(), set_control_move(),
set_control_moveable(), is_control_moveable(), set_tips_display(),
is_tips_display(), get_pointer_position(), set_pointer_interact(),
set_info_display(), is_info_display(), add_info(), clear_info().


InterfaceControl Object methods:

get_value(), set_value(), get_list(), set_list(), remove_list(), 
set_list_icon(), set_control_image(), set_link(), set_link_activated(),
set_activated(), is_activated(), set_activated_lock(), is_activated_lock(),
set_active(), is_active(), next(), previous(), reset(), get_position(),
set_display_text(), set_label_text(), get_tip(), set_tip(), get_id(),
set_label(), get_label(), resize_control(), set_enabled(), is_enabled(),
get_size(), set_color(), get_list_index(), set_list_index().
"""


from interface import Interface, EVENT
from control import InterfaceControl
from util import Text, load_image
from version import __version__
import warnings
warnings.filterwarnings("ignore")


def main():
    try:
        import test
        test.run()
    except ImportError:
        print("Warning: test.py not found.")

if __name__ == '__main__':
    main()

