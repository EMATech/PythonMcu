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

import time
import types

from PythonMcu.Midi.MidiConnection import MidiConnection


class MackieHostControl:
    __module__ = __name__
    __doc__ = 'Mackie Host Control for Novation ZeRO SL MkII'


    def __init__(self, midi_input, midi_output, controller):
        self._log('Opening MIDI ports...')
        self._midi = MidiConnection(self.receive_midi, midi_input, midi_output)
        self._controller = controller


    def connect(self):
        self._log('Querying host...')

        self._connected = False
        while not self._connected:
            # Ableton Live does not support the Mackie Control query
            # system, so we'll make sure the MIDI input buffer is
            # empty ...
            self._midi.process_input_buffer(use_callback=False)

            # ... and simply wait for some MIDI input from the host
            while self._midi.buffer_is_empty():
                time.sleep(0.1)

            self._connected = True

        self._log('Connected.')


    def disconnect(self):
        self._log('Disconnecting...')

        self._midi.disconnect()

        self._log('Disconnected.')


    def receive_midi(self, status, message):
        if status == MidiConnection.SYSTEM_MESSAGE:
            if message[0:6] == [0xF0, 0x00, 0x00, 0x66, 0x14, 0x12]:
                if self._controller.has_display():
                    if message[6] == 56:
                        position = 3
                    else:
                        position = 1

                    temp_codes = message[7:-1]
                    hex_codes = [0x20]

                    for i in range(len(temp_codes)):
                        hex_codes.append(temp_codes[i])
                        if (i%7) == 6:
                            hex_codes.append(0x20)
                            hex_codes.append(0x20)

                    hex_codes.append(0x20)

                    self._controller.update_lcd_raw(position, hex_codes)
        elif status == MidiConnection.PITCH_WHEEL_CHANGE:
            fader_id = message[0] & 0x0F
            fader_position = (message[1] + (message[2] << 7)) >> 4
            self._controller.fader_moved(fader_id, fader_position)
        elif status == MidiConnection.NOTE_ON_EVENT:
            led_id = message[1]
            led_status = 0  # off
            if message[2] == 0x7F:
                led_status = 1  # on
            elif message[2] == 0x01:
                led_status = 2  # flashing
            self._controller.set_led(led_id, led_status)
        elif (status == MidiConnection.CONTROL_CHANGE) and \
                ((message[1] & 0xF0) == 0x30):
            vpot_id = message[1] & 0x0F
            vpot_center_led = (message[2] & 0x40) >> 7
            vpot_mode = (message[2] & 0x30) >> 4
            vpot_position = message[2] & 0x0F
            self._controller.set_vpot_led(vpot_center_led, vpot_mode, vpot_position)
        elif (status == MidiConnection.CONTROL_CHANGE) and \
                ((message[1] & 0xF0) == 0x40):
            if self._controller.has_seg7():
                seg7_position = message[1] & 0x0F
                seg7_character = message[2]
                self._controller.set_seg7(seg7_position, seg7_character)
        elif status == MidiConnection.CHANNEL_PRESSURE:
            if self._controller.has_meter_bridge():
                meter_id = (message[1] & 0x70) >> 4
                meter_level = message[1] & 0x0F
                self._controller.set_peak_level(meter_id, meter_level)
        else:
            print 'status %02X: ' % status,
            for byte in message:
                print '%02X' % byte,
            print


    def poll(self):
        self._midi.process_input_buffer()


    def switch_pressed_and_released(self, switch_id):
        self.switch_pressed(switch_id)
        self.switch_released(switch_id)


    def switch_pressed(self, switch_id):
        self._midi.send_cc(0, switch_id, 0x7f)


    def switch_released(self, switch_id):
        self._midi.send_cc(0, switch_id, 0x00)


    def move_fader(self, fader_id, fader_value):
        fader_value_low = fader_value & 0x7F
        fader_value_high = fader_value >> 7
        self._midi.send(0xE0 + fader_id, fader_value_low, fader_value_high)


    def move_fader_7bit(self, fader_id, fader_value):
        self._midi.send(0xE0 + fader_id, fader_value, fader_value)


    def _log(self, message):
        print '[Mackie Host Control  ]  ' + message


    def send_midi_cc(self, channel, cc_number, cc_value):
        self._midi.send_cc(channel, cc_number, cc_value)


    def send_midi_sysex(self, data):
        assert(type(data) == types.ListType)

        header = [0x00, 0x00, 0x66, 0x11]

        self._midi.send_sysex(header, data)


if __name__ == "__main__":
    midi_input = 'In From MIDI Yoke:  5'
    midi_output = 'Out To MIDI Yoke:  6'
    controller = None

    host_control = MackieHostControl(midi_input, midi_output, controller)
    host_control.connect()

    host_control.move_fader_7bit(0, 80)

    host_control.disconnect()
