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

Interphase Module version 0.81
Download Site: http://gatc.ca
Source:        Interphase.zip

InterphasePack (Interphase Demonstration)
Source:        InterphasePack.zip
Executable:
    Linux:      InterphasePack_exe.tar.gz
    Windows:    InterphasePack_exe.zip

Dependencies:

    Python 2.5:   http://www.python.org/
    Pygame 1.8:   http://www.pygame.org/


Description:

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


Interface Object parameters:

Optional Parameters <default>:
identity: 'id' panel name <'Interface_Panel'>.
position: (x,y) panel placement on screen <None>.
    - values < 1 are %screen.
    - None centers on screen.
image: 'image' panel image <None>.
    - None use default image, 'none' suppress default image.
    - Image in data folder.
color: (r,g,b) panel color <(0,0,0)>.
size: (w,h) dimension of panel <(350,100)>.
screen: (w,h) dimension of screen <(500,500)>.
moveable: bool panel can move <False>.
position_offset: (x,y) panel move offset <(0,0)>.
move_rate: (x,y) panel move rate pix/s <(200,200)>.
    - values < 1 are %position_offset/s.
fixed: bool panel fixed in place <False>.
button_image: ['U','D'] or 'composite' control button image <None>.
    - None use default image, 'none' suppress default image.
    - Image in data folder.
control_image: 'image' control background image <None>.
    - None use default image, 'none' suppress default image.
    - Image in data folder.
color_key: (r,g,b) image color key transparency <None>.
    - transparency set by image alpha value or color_key.
    - value -1 color_key from pixel at (0,0).
control_minsize: (x,y) minimum control size <None>.
control_size: '' global control size if control_minsize set <'min'>.
    - 'auto', 'auto_width': fit items.
    - 'min', 'min_width': fit using control_minsize.
    - 'panel': use exact control_minsize.
button_size: (x,y) button size <(12,12)>.
function_button: placement of buttons of function_select <'left'>.
control_button: placement of buttons of control_select <'right'>.
font_color: (r,g,b) font color of control text <(125,130,135)>.
font_type: [] font type list <None>.
    - None: default system font; []: use first font available.
    - <control>.set_display_text(info='system') gets system fonts.
    - 'file:<font_name>' path to font file.
font_size: int font size of control text. Size:6,8,10,12,24,32 <10>.
label_display: bool label displayed <False>.
info_display: bool info text displayed <False>.
info_fontsize: int font size used for info text <10>.
info_fontcolor: (r,g,b) font color used for info text <(125,130,135)>.
info_position: (x,y) position of info text <(2,0)>.
tips_display: bool tip text displayed <False>.
tips_fontsize: int font size used for tip text <8>.
tips_fontcolor: (r,g,b) font color used for tip text <(125,130,135)>.
tips_position: (x,y) position offset of tip text <(0,-15)>.
control_response: int control click response (ms) <125>.
pointer_interact: bool pointer interact monitored <False>.
data_folder: '' image data folder <'data'>.
data_zip: '' image data zip <None>.
event: bool interaction generates events <False>.


InterfaceControl Object parameters:

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

