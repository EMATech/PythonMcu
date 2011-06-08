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

from MidiConnection import MidiConnection


class ControllerTemplate(object):
    def __init__(self, midi_input, midi_output):
        pass


    def connect(self):
        pass	


    def disconnect(self):
        pass


    def _log(self, message):
        print '[Controller Template]  ' + message


    def receive_midi(self, message_status, message):
	pass


    def send_midi_cc(self, channel, cc_number, cc_value):
        pass


    def send_midi_sysex(self, data):
        assert(type(data) == types.ListType)

        pass


    def update_encoder_light(self, position, value):
        pass


    def update_lcd_raw(self, position, hex_codes):
        """
        send hex codes of maximum 72 bytes to controller LCD

        position 1: top row (left controller block)
        position 2: top row (right controller block)
        position 3: bottom row (left controller block)
        position 4: bottom row (right controller block)
        """
	pass


    def update_lcd(self, position, strings, preserve_space, shorten):
        """
        send string of maximum 72 bytes to controller LCD

        position 1: top row (left controller block)
        position 2: top row (right controller block)
        position 3: bottom row (left controller block)
        position 4: bottom row (right controller block)
        """
	pass
