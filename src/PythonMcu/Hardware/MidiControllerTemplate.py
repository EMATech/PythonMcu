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

import sys
import types

if __name__ == "__main__":
    # allow "PythonMcu" package imports when executing this module
    sys.path.append('../../../')

from PythonMcu.Midi.MidiConnection import MidiConnection


class MidiControllerTemplate(object):

    MIDI_MANUFACTURER_ID = None
    MIDI_DEVICE_ID = None

    VPOT_MODE_SINGLE_DOT = 0x00
    VPOT_MODE_BOOST_CUT = 0x01
    VPOT_MODE_WRAP = 0x02
    VPOT_MODE_SPREAD = 0x03

    _LED_STATUS = {
        0x00: 'off',
        0x01: 'flashing',
        0x7F: 'on'
        }

    def __init__(self, midi_input, midi_output):
        self.midi = MidiConnection(self.receive_midi, midi_input, midi_output)
        self.unset_mackie_control_host()

        self.display_lcd_available = True
        self.automated_faders_available = True
        self.display_7seg_available = True
        self.display_timecode_available = True
        self.meter_bridge_available = True

        self.display_7seg_characters = []
        for counter in range(4):
            self.display_7seg_characters.append(' ')

        self.display_timecode_characters = []
        for counter in range(20):
            self.display_timecode_characters.append(' ')


    def set_mackie_control_host(self, host):
        self.mackie_control_host = host


    def unset_mackie_control_host(self):
        self.mackie_control_host = None


    def connect(self):
        self._log('Opening MIDI ports...')


    def disconnect(self):
        self.midi.disconnect()
        self._log('Disconnected.')


    def _log(self, message):
        print '[Controller Template]  ' + message


    def has_display_7seg(self):
        return self.display_7seg_available


    def has_display_lcd(self):
        return self.display_lcd_available


    def has_display_timecode(self):
        return self.display_timecode_available


    def has_automated_faders(self):
        return self.automated_faders_available


    def has_meter_bridge(self):
        return self.meter_bridge_available


    def process_midi_input(self):
        self.midi.process_input_buffer()


    def receive_midi(self, status, message):
        message_string = ['status %02X: ' % status]
        for byte in message:
            message_string.append('%02X' % byte)
        self._log(' '.join(message_string))


    def send_midi_control_change(self, channel, cc_number, cc_value):
        self.midi.send_control_change(channel, cc_number, cc_value)


    def send_midi_sysex(self, data):
        assert(type(data) == types.ListType)

        header = []
        header.extend(self.MIDI_MANUFACTURER_ID)
        header.extend(self.MIDI_DEVICE_ID)

        self.midi.send_sysex(header, data)


    def fader_moved(self, fader_id, fader_position):
        self._log('Hardware fader #%d NOT moved to position %04d.' % \
                      (fader_id, fader_position))


    def set_peak_level(self, meter_id, meter_level):
        if meter_level == 0x0F:
            self._log('Meter #%d overload NOT cleared.' % meter_id)
        elif meter_level == 0x0F:
            self._log('Meter #%d NOT set to overload.' % meter_id)
        else:
            self._log('Meter #%d NOT set to %03d%%.' % (meter_id, meter_level * 10))


    def _decode_7seg_character(self, character_code):
        if character_code >= 0x40:
            character_code = character_code - 0x40
            dot = '.'
        else:
            dot = ' '

        if character_code < 0x20:
            return (chr(character_code + 0x40), dot)
        else:
            return (chr(character_code), dot)


    def set_display_7seg(self, position, character_code):
        character = self._decode_7seg_character(character_code)
        position = 23 - (position * 2)

        self.display_7seg_characters[position - 1] = character[0]
        self.display_7seg_characters[position] = character[1]

        string_7seg = ''.join(self.display_7seg_characters)
        self._log('7 segment display NOT set to "%s".' % string_7seg)


    def set_display_timecode(self, position, character_code):
        character = self._decode_7seg_character(character_code)
        position = 19 - (position * 2)

        self.display_timecode_characters[position - 1] = character[0]
        self.display_timecode_characters[position] = character[1]

        # please note that the logged timecode is not necessarily
        # correct: it will only be dumped when the display's last
        # character has been updated -- there may be other updates
        # still pending!
        if position == 19:
            string_timecode = ''.join(self.display_timecode_characters)
            self._log('timecode display NOT set to "%s".' % string_timecode)


    def set_vpot_led_ring(self, vpot_id, vpot_center_led, vpot_mode, vpot_position):
        self._log('V-Pot #%d LED ring NOT set to position %02d (mode %d).' % \
                      (vpot_id, vpot_position, vpot_mode))


    def update_encoder_light(self, position, value):
        pass


    def update_lcd(self, position, new_string):
        """
        send string of maximum 72 bytes to controller LCD

        position 1: top row
        position 2: bottom row
        """
        pass


    def update_led_channel_record_ready(self, channel, status):
        # channel: 0 - 7
        self._log('LED "CHANNEL_RECORD_READY_%d" NOT set to "%s".' % \
                      (channel + 1, self._LED_STATUS[status]))


    def update_led_channel_solo(self, channel, status):
        # channel: 0 - 7
        self._log('LED "CHANNEL_SOLO_%d" NOT set to "%s".' % \
                      (channel + 1, self._LED_STATUS[status]))


    def update_led_channel_mute(self, channel, status):
        # channel: 0 - 7
        self._log('LED "CHANNEL_MUTE_%d" NOT set to "%s".' % \
                      (channel + 1, self._LED_STATUS[status]))


    def update_led_channel_select(self, channel, status):
        # channel: 0 - 7
        self._log('LED "CHANNEL_SELECT_%d" NOT set to "%s".' % \
                      (channel + 1, self._LED_STATUS[status]))


    def update_led_assignment_track(self, status):
        self._log('LED "ASSIGNMENT_TRACK" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_assignment_send(self, status):
        self._log('LED "ASSIGNMENT_SEND" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_assignment_pan_surround(self, status):
        self._log('LED "ASSIGNMENT_PAN_SURROUND" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_assignment_plug_in(self, status):
        self._log('LED "ASSIGNMENT_PLUG_IN" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_assignment_eq(self, status):
        self._log('LED "ASSIGNMENT_EQ" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_assignment_instrument(self, status):
        self._log('LED "ASSIGNMENT_INSTRUMENT" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_flip(self, status):
        self._log('LED "FLIP" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_global_view(self, status):
        self._log('LED "GLOBAL_VIEW" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_automation_read_off(self, status):
        self._log('LED "AUTOMATION_READ_OFF" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_automation_write(self, status):
        self._log('LED "AUTOMATION_WRITE" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_automation_trim(self, status):
        self._log('LED "AUTOMATION_TRIM" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_automation_touch(self, status):
        self._log('LED "AUTOMATION_TOUCH" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_automation_latch(self, status):
        self._log('LED "AUTOMATION_LATCH" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_group(self, status):
        self._log('LED "GROUP" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_utilities_save(self, status):
        self._log('LED "UTILITIES_SAVE" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_utilities_undo(self, status):
        self._log('LED "UTILITIES_UNDO" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_marker(self, status):
        self._log('LED "MARKER" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_nudge(self, status):
        self._log('LED "NUDGE" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_cycle(self, status):
        self._log('LED "CYCLE" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_drop(self, status):
        self._log('LED "DROP" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_replace(self, status):
        self._log('LED "REPLACE" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_click(self, status):
        self._log('LED "CLICK" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_solo(self, status):
        self._log('LED "SOLO" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_rewind(self, status):
        self._log('LED "REWIND" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_fast_forward(self, status):
        self._log('LED "FAST_FORWARD" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_stop(self, status):
        self._log('LED "STOP" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_play(self, status):
        self._log('LED "PLAY" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_record(self, status):
        self._log('LED "RECORD" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_zoom(self, status):
        self._log('LED "ZOOM" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_scrub(self, status):
        self._log('LED "SCRUB" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_smpte(self, status):
        self._log('LED "SMPTE" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_beats(self, status):
        self._log('LED "BEATS" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_rude_solo(self, status):
        self._log('LED "RUDE_SOLO" NOT set to "%s".' % \
                      self._LED_STATUS[status])


    def update_led_relay_click(self, status):
        self._log('LED "RELAY_CLICK" NOT set to "%s".' % \
                      self._LED_STATUS[status])
