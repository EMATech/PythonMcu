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
        self.display_available = True
        self.seg7_available = True
        self.meter_bridge_available = True

        self.seg7_characters = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']


    def connect(self):
        pass


    def disconnect(self):
        pass


    def _log(self, message):
        print '[Controller Template]  ' + message


    def has_seg7(self):
        return self.seg7_available


    def has_display(self):
        return self.display_available


    def has_meter_bridge(self):
        return self.meter_bridge_available


    def receive_midi(self, status, message):
        pass


    def send_midi_cc(self, channel, cc_number, cc_value):
        pass


    def send_midi_sysex(self, data):
        assert(type(data) == types.ListType)
        pass


    def fader_moved(self, fader_id, fader_position):
        self._log('Fader #%d moved to position %04d.' % (fader_id, fader_position))


    def set_led(self, led_id, led_status):
        status = 'is off'
        if led_status == 1:
            status = 'is on'
        elif led_status == 2:
            status = 'flashes'

        self._log('LED #%03d %s.' % (led_id, status))


    def set_peak_level(self, meter_id, meter_level):
        if meter_level == 0x0F:
            self._log('Meter #%d overload cleared.' % meter_id)
        elif meter_level == 0x0F:
            self._log('Meter #%d overload.' % meter_id)
        else:
            self._log('Meter #%d set to %03d%%.' % (meter_id, meter_level * 10))


    def set_seg7(self, seg7_position, seg7_character):
        position = 19 - (seg7_position * 2)

        if seg7_character >= 0x40:
            seg7_character = seg7_character - 0x40
            self.seg7_characters[position] = '.'
        else:
            self.seg7_characters[position] = ' '

        if seg7_character < 0x20:
            self.seg7_characters[position - 1] = chr(seg7_character + 0x40)
        else:
            self.seg7_characters[position - 1] = chr(seg7_character)

        if seg7_position >= 9:
            seg7_string = ''.join(self.seg7_characters)
            self._log('7 segment display set to "%s".' % seg7_string)


    def set_vpot_led(self, vpot_center_led, vpot_mode, vpot_position):
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
