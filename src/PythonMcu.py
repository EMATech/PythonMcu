# -*- coding: utf-8 -*-

"""
PythonMcu
=========
Mackie Host Controller written in Python

Copyright (c) 2011 Martin Zuther (http://www.mzuther.de/)

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

Thank you for using free software!

"""

MIDI_IN_CONTROL = 'ZeRO MkII: Port 1'
MIDI_OUT_CONTROL = MIDI_IN_CONTROL

MIDI_IN_SEQUENCER = 'In From MIDI Yoke:  4'
MIDI_OUT_SEQUENCER = 'Out To MIDI Yoke:  3'


from PythonMcu.Hardware.Novation import *
from PythonMcu.MackieControl.MackieHostControl import MackieHostControl

import threading
import sys
import time


print
print 'Starting application...'
print

try:
    controller = ZeroSlMk2.ZeroSlMk2(MIDI_IN_CONTROL, MIDI_OUT_CONTROL)
    controller.connect()

    host_control = MackieHostControl(MIDI_IN_SEQUENCER, MIDI_OUT_SEQUENCER)
    host_control.connect()

    host_control.set_hardware_controller(controller)
    controller.set_mackie_control_host(host_control)

    host_control.keypress_assignment_pan_surround(MackieHostControl.SWITCH_PRESSED_RELEASED)
    host_control.keypress_shift(MackieHostControl.SWITCH_PRESSED)
    host_control.keypress_global_view(MackieHostControl.SWITCH_PRESSED_RELEASED)
    host_control.keypress_shift(MackieHostControl.SWITCH_RELEASED)
    print

    while True:
        host_control.poll()

        time.sleep(0.01)
except KeyboardInterrupt:
    print

    host_control.disconnect()
    controller.disconnect()

    print
    print 'Exiting application...'
    print
