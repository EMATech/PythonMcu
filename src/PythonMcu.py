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

from PythonMcu.Hardware import *
from PythonMcu.MackieControl.MackieHostControl import MackieHostControl
from PythonMcu.McuInterconnector.McuInterconnector import McuInterconnector
from Settings import *

import threading
import sys
import time


# Mackie Control model IDs:
# * 0x10: Logic Control
# * 0x11: Logic Control XT
# * 0x14: Mackie Control
# * 0x15: Mackie Control XT
#
# Ableton Live 8 needs 0x14 in order to write to the LCD, so let's use this
HARDWARE_CONTROLLER = settings.get( \
    'Python MCU', 'Hardware controller', False)

MCU_MODEL_ID = int(settings.get( \
        'Python MCU', 'MCU Model ID', False), 16)

MIDI_IN_CONTROLLER = settings.get( \
    'Python MCU', 'MIDI input (controller)', False)
MIDI_OUT_CONTROLLER = settings.get( \
    'Python MCU', 'MIDI output (controller)', False)

MIDI_IN_SEQUENCER = settings.get( \
    'Python MCU', 'MIDI input (sequencer)', False)
MIDI_OUT_SEQUENCER = settings.get( \
    'Python MCU', 'MIDI output (sequencer)', False)


print
print settings.get_description(True)
print
print settings.get_copyrights()
print
print settings.get_license(True)
print
print
print 'Settings'
print '========'
print 'Python version:            %d.%d.%d' % sys.version_info[:3]
print
print 'Hardware controller:       %s' % HARDWARE_CONTROLLER.replace('_', ' ')
print 'MCU model ID:              0x%x' % MCU_MODEL_ID
print 'MIDI input (controller):   %s' % MIDI_IN_CONTROLLER
print 'MIDI output (controller):  %s' % MIDI_OUT_CONTROLLER
print 'MIDI input (sequencer):    %s' % MIDI_IN_SEQUENCER
print 'MIDI output (sequencer):   %s' % MIDI_OUT_SEQUENCER
print

print
print 'Starting application...'
print

try:
    eval_controller_init = '%s.%s(MIDI_IN_CONTROLLER, MIDI_OUT_CONTROLLER)' % \
        (HARDWARE_CONTROLLER, HARDWARE_CONTROLLER)
    midi_controller = eval(eval_controller_init)

    mackie_host_control = MackieHostControl( \
        MIDI_IN_SEQUENCER, MIDI_OUT_SEQUENCER, MCU_MODEL_ID)

    # the "interconnector" is the brain of this application -- it
    # interconnects Mackie Control Host and MIDI controller while
    # handling the complete MIDI translation between those two
    interconnector = McuInterconnector(mackie_host_control, midi_controller)
    interconnector.connect()

    print
    while True:
        interconnector.process_midi_input()

        time.sleep(0.01)
except KeyboardInterrupt:
    print

    interconnector.disconnect()

    print
    print 'Exiting application...'
    print
