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

# MIDI channel of controller
MIDI_DEVICE_CHANNEL = 0

# number of available channels strips on controller
CHANNEL_STRIPS = 8

# number of available LCD pages on controller
LCD_PAGES = 4

# number of available LCD characters per channel strip
LCD_FIELD_LENGTH = 9


# Novation Digital Music System
MIDI_MANUFACTURER_ID = (0x00, 0x20, 0x29)

# MIDI device ID and initialisation of Novation ZeRO SL Mkii
MIDI_DEVICE_ID = (0x03, 0x03, 0x12, 0x00, 0x04, 0x00)


# MIDI status bytes (for channel 1)
MIDI_STATUS_NOTE_OFF = 0x80
MIDI_STATUS_NOTE_ON = 0x90
MIDI_STATUS_CONTROL_CHANGE = 0xB0
MIDI_STATUS_PITCH_BEND = 0xE0


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
