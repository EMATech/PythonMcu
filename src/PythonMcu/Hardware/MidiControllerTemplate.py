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

from PythonMcu.Midi.MidiConnection import MidiConnection


class MidiControllerTemplate(object):
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


#     def set_led(self, led_id, led_status):
#         status = 'is off'
#         if led_status == 1:
#             status = 'is on'
#         elif led_status == 2:
#             status = 'flashes'

#         self._log('LED #%03d %s.' % (led_id, status))


    def update_led_record_ready(self, channel, status):
        # channel: 0 - 7
        self._log('LED "CHANNEL_RECORD_READY_%d" not found.' % channel)


    def update_led_solo(self, channel, status):
        # channel: 0 - 7
        self._log('LED "CHANNEL_SOLO_%d" not found.' % channel)


    def update_led_mute(self, channel, status):
        # channel: 0 - 7
        self._log('LED "CHANNEL_MUTE_%d" not found.' % channel)


    def update_led_select(self, channel, status):
        # channel: 0 - 7
        self._log('LED "CHANNEL_SELECT_%d" not found.' % channel)


    def update_led_assignment_track(self, status):
        self._log('LED "ASSIGNMENT_TRACK" not found.')


    def update_led_assignment_send(self, status):
        self._log('LED "ASSIGNMENT_SEND" not found.')


    def update_led_assignment_pan_surround(self, status):
        self._log('LED "ASSIGNMENT_PAN_SURROUND" not found.')


    def update_led_assignment_plug_in(self, status):
        self._log('LED "ASSIGNMENT_PLUG_IN" not found.')


    def update_led_assignment_eq(self, status):
        self._log('LED "ASSIGNMENT_EQ" not found.')


    def update_led_assignment_instrument(self, status):
        self._log('LED "ASSIGNMENT_INSTRUMENT" not found.')


    def update_led_flip(self, status):
        self._log('LED "FLIP" not found.')


    def update_led_global_view(self, status):
        self._log('LED "GLOBAL_VIEW" not found.')


    def update_led_automation_read_off(self, status):
        self._log('LED "AUTOMATION_READ_OFF" not found.')


    def update_led_automation_write(self, status):
        self._log('LED "AUTOMATION_WRITE" not found.')


    def update_led_automation_trim(self, status):
        self._log('LED "AUTOMATION_TRIM" not found.')


    def update_led_automation_touch(self, status):
        self._log('LED "AUTOMATION_TOUCH" not found.')


    def update_led_automation_latch(self, status):
        self._log('LED "AUTOMATION_LATCH" not found.')


    def update_led_group(self, status):
        self._log('LED "GROUP" not found.')


    def update_led_utilities_save(self, status):
        self._log('LED "UTILITIES_SAVE" not found.')


    def update_led_utilities_undo(self, status):
        self._log('LED "UTILITIES_UNDO" not found.')


    def update_led_marker(self, status):
        self._log('LED "MARKER" not found.')


    def update_led_nudge(self, status):
        self._log('LED "NUDGE" not found.')


    def update_led_cycle(self, status):
        self._log('LED "CYCLE" not found.')


    def update_led_drop(self, status):
        self._log('LED "DROP" not found.')


    def update_led_replace(self, status):
        self._log('LED "REPLACE" not found.')


    def update_led_click(self, status):
        self._log('LED "CLICK" not found.')


    def update_led_solo(self, status):
        self._log('LED "SOLO" not found.')


    def update_led_rewind(self, status):
        self._log('LED "REWIND" not found.')


    def update_led_fast_forward(self, status):
        self._log('LED "FAST_FORWARD" not found.')


    def update_led_stop(self, status):
        self._log('LED "STOP" not found.')


    def update_led_play(self, status):
        self._log('LED "PLAY" not found.')


    def update_led_record(self, status):
        self._log('LED "RECORD" not found.')


    def update_led_zoom(self, status):
        self._log('LED "ZOOM" not found.')


    def update_led_scrub(self, status):
        self._log('LED "SCRUB" not found.')
