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

MIDI_CC_CLEAR_ALL_LEDS = 0x4E
MIDI_CC_ENCODER_LIGHTS = 0x70
MIDI_CC_CONTROLLER_ROW_LIGHTS_LEFT = (0x51, 0x53, 0x54, 0x50, 0x52)
MIDI_CC_CONTROLLER_ROW_LIGHTS_RIGHT = (0x55, 0x56, 0x57)

MIDI_CC_FADERS = 0x10
MIDI_CC_ENCODERS = 0x38
MIDI_CC_KNOBS = 0x08

MIDI_CC_BUTTONS_LEFT_TOP = 0x18
MIDI_CC_BUTTONS_LEFT_BOTTOM = 0x20
MIDI_CC_BUTTONS_RIGHT_TOP = 0x28
MIDI_CC_BUTTONS_RIGHT_BOTTOM = 0x30

MIDI_CC_BUTTON_BANK_UP = 0x58
MIDI_CC_BUTTON_BANK_DOWN = 0x59
