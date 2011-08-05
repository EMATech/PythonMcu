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

MIDI_IN_CONTROL = 'ZeRO MkII: Port 2'
MIDI_OUT_CONTROL = 'ZeRO MkII: Port 2'

MIDI_IN_SEQUENCER = 'In From MIDI Yoke:  2'
MIDI_OUT_SEQUENCER = 'Out To MIDI Yoke:  1'

# Mackie Control model IDs:
# * 0x10: Logic Control
# * 0x11: Logic Control Extension
# * 0x14: seems to be Mackie Control
#
# Ableton Live 8 needs 0x14 in order to write to the LCD, so let's use this
MCU_MODEL_ID = 0x14


from PythonMcu.Hardware.Novation import *
from PythonMcu.MackieControl.MackieHostControl import MackieHostControl
from PythonMcu.McuInterconnector.McuInterconnector import McuInterconnector

import threading
import sys
import time


print
print 'Starting application...'
print

try:
    midi_controller = ZeroSlMk2.ZeroSlMk2(MIDI_IN_CONTROL, MIDI_OUT_CONTROL)
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
