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
from PythonMcu.Tools.ApplicationSettings import *

import threading
import sys
import time


configuration = ApplicationSettings()

# initialise defaults for MCU and hardware control
emulated_mcu_model_default = MackieHostControl.get_preferred_mcu_model()
hardware_controller_default = 'Novation ZeRO SL MkII'

# retrieve user configuration for MCU and hardware control
EMULATED_MCU_MODEL = configuration.get_option( \
    'Python MCU', 'emulated_mcu_model', emulated_mcu_model_default)
HARDWARE_CONTROLLER = configuration.get_option( \
    'Python MCU', 'hardware_controller', hardware_controller_default)

# calculate MCU model ID from its name
MCU_MODEL_ID = MackieHostControl.get_mcu_id_from_model(EMULATED_MCU_MODEL)

# the hardware controller class name is simply the controller's
# manufacturer and name with all the spaces converted to underscores
HARDWARE_CONTROLLER_CLASS = HARDWARE_CONTROLLER.replace(' ', '_')


# get preferred MIDI connections for hardware control
eval_controller_midi_input = \
    '{0!s}.{0!s}.get_preferred_midi_input()'.format(HARDWARE_CONTROLLER_CLASS)
eval_controller_midi_output = \
    '{0!s}.{0!s}.get_preferred_midi_output()'.format(HARDWARE_CONTROLLER_CLASS)

# initialise MIDI connection defaults for MCU and hardware control
sequencer_midi_input_default = MackieHostControl.get_preferred_midi_input()
sequencer_midi_output_default = MackieHostControl.get_preferred_midi_output()
controller_midi_input_default = eval(eval_controller_midi_input)
controller_midi_output_default = eval(eval_controller_midi_output)

# retrieve user configuration for MIDI connection of MCU
SEQUENCER_MIDI_INPUT = configuration.get_option( \
    'Python MCU', 'sequencer_midi_input', sequencer_midi_input_default)
SEQUENCER_MIDI_OUTPUT = configuration.get_option( \
    'Python MCU', 'sequencer_midi_output', sequencer_midi_output_default)

# retrieve user configuration for MIDI connection of hardware control
CONTROLLER_MIDI_INPUT = configuration.get_option( \
    'Python MCU', 'controller_midi_input', controller_midi_input_default)
CONTROLLER_MIDI_OUTPUT = configuration.get_option( \
    'Python MCU', 'controller_midi_output', controller_midi_output_default)


print
print configuration.get_full_description()
print
print
print 'Settings'
print '========'
print 'Python version:          %d.%d.%d' % sys.version_info[:3]
print
print 'Emulated MCU model:      %s' % EMULATED_MCU_MODEL
print 'Sequencer MIDI input:    %s' % SEQUENCER_MIDI_INPUT
print 'Sequencer MIDI output:   %s' % SEQUENCER_MIDI_OUTPUT
print
print 'Hardware controller:     %s' % HARDWARE_CONTROLLER
print 'Controller MIDI input:   %s' % CONTROLLER_MIDI_INPUT
print 'Controller MIDI output:  %s' % CONTROLLER_MIDI_OUTPUT
print

if configuration.has_changed():
    print
    print 'Saving configuration file ...'
    configuration.save_configuration()

print
print 'Starting application...'
print


try:
    eval_controller_init = \
        '{0!s}.{0!s}(CONTROLLER_MIDI_INPUT, CONTROLLER_MIDI_OUTPUT)'.format( \
        HARDWARE_CONTROLLER_CLASS)
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
