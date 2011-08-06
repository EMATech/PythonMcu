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
from ApplicationSettings import *

import threading
import sys
import time


configuration = ApplicationSettings()

controller_midi_input_default = 'ZeRO MkII: Port 2'
controller_midi_output_default = 'ZeRO MkII: Port 2'
emulated_mcu_model_default = 'Mackie Control'
hardware_controller_default = 'Novation ZeRO SL MkII'
sequencer_midi_input_default = 'In From MIDI Yoke:  2'
sequencer_midi_output_default = 'Out To MIDI Yoke:  1'


HARDWARE_CONTROLLER = configuration.get_option( \
    'Python MCU', 'hardware_controller', hardware_controller_default)

EMULATED_MCU_MODEL = configuration.get_option( \
    'Python MCU', 'emulated_mcu_model', emulated_mcu_model_default)

CONTROLLER_MIDI_INPUT = configuration.get_option( \
    'Python MCU', 'controller_midi_input', controller_midi_input_default)
CONTROLLER_MIDI_OUTPUT = configuration.get_option( \
    'Python MCU', 'controller_midi_output', controller_midi_output_default)

SEQUENCER_MIDI_INPUT = configuration.get_option( \
    'Python MCU', 'sequencer_midi_input', sequencer_midi_input_default)
SEQUENCER_MIDI_OUTPUT = configuration.get_option( \
    'Python MCU', 'sequencer_midi_output', sequencer_midi_output_default)


print
print configuration.get_description(True)
print
print configuration.get_copyrights()
print
print configuration.get_license(True)
print
print
print 'Settings'
print '========'
print 'Python version:          %d.%d.%d' % sys.version_info[:3]
print
print 'Hardware controller:     %s' % HARDWARE_CONTROLLER
print 'Controller MIDI input:   %s' % CONTROLLER_MIDI_INPUT
print 'Controller MIDI output:  %s' % CONTROLLER_MIDI_OUTPUT
print
print 'Emulated MCU model:      %s' % EMULATED_MCU_MODEL
print 'Sequencer MIDI input:    %s' % SEQUENCER_MIDI_INPUT
print 'Sequencer MIDI output:   %s' % SEQUENCER_MIDI_OUTPUT
print

if configuration.has_changed():
    print
    print 'Saving configuration file ...'
    configuration.save_configuration()

print
print 'Starting application...'
print


# Mackie Control model IDs:
# * 0x10: Logic Control
# * 0x11: Logic Control XT
# * 0x14: Mackie Control
# * 0x15: Mackie Control XT
#
# Ableton Live 8 needs 0x14 in order to write to the LCD!
if EMULATED_MCU_MODEL == 'Logic Control':
    MCU_MODEL_ID = 0x10
elif EMULATED_MCU_MODEL == 'Logic Control XT':
    MCU_MODEL_ID = 0x11
elif EMULATED_MCU_MODEL == 'Mackie Control':
    MCU_MODEL_ID = 0x14
elif EMULATED_MCU_MODEL == 'Mackie Control XT':
    MCU_MODEL_ID = 0x15
else:
    assert(False)


try:
    eval_controller_init = \
        '{0!s}.{0!s}(CONTROLLER_MIDI_INPUT, CONTROLLER_MIDI_OUTPUT)'.format( \
        HARDWARE_CONTROLLER.replace(' ', '_'))
    midi_controller = eval(eval_controller_init)

    mackie_host_control = MackieHostControl( \
        SEQUENCER_MIDI_INPUT, SEQUENCER_MIDI_OUTPUT, MCU_MODEL_ID)

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
