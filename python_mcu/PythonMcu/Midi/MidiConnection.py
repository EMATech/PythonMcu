# -*- coding: utf-8 -*-

"""
PythonMcu
=========
Mackie Host Controller written in Python
Copyright (c) 2011 Martin Zuther (http://www.mzuther.de/)
Copyright (c) 2021 Raphaël Doursenaud <rdoursenaud@free.fr>

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
from binascii import hexlify

import rtmidi
import rtmidi.midiutil
import rtmidi.midiconstants


class MidiConnection:
    __module__ = __name__
    __doc__ = 'MIDI connection handler'

    NOTE_OFF_EVENT = rtmidi.midiconstants.NOTE_OFF
    NOTE_ON_EVENT = rtmidi.midiconstants.NOTE_ON
    POLYPHONIC_KEY_PRESSURE = rtmidi.midiconstants.POLYPHONIC_PRESSURE
    CONTROL_CHANGE = rtmidi.midiconstants.CONTROL_CHANGE
    PROGRAM_CHANGE = rtmidi.midiconstants.PROGRAM_CHANGE
    CHANNEL_PRESSURE = rtmidi.midiconstants.CHANNEL_PRESSURE
    PITCH_WHEEL_CHANGE = rtmidi.midiconstants.PITCH_BEND
    SYSTEM_MESSAGE = rtmidi.midiconstants.SYSTEM_EXCLUSIVE

    # --- initialisation ---

    def __init__(self, callback_log, callback):
        self._callback_log = callback_log
        self._callback = callback

        self._midi_input_name = None
        self._midi_output_name = None

        self._midi_input = None
        self._midi_output = None

        self._input_buffer = []

    def connect(self, midi_input_name=None, midi_output_name=None):
        if midi_input_name:
            midi_input = self._init_input(midi_input_name)
            if midi_input:
                midi_in_port, in_name = midi_input
                self._midi_input = midi_in_port
                self._midi_input_name = in_name
                self._midi_input.ignore_types(sysex=False)  # Make sure rtmidi doesn't filter out SysEx
            else:
                raise ValueError(f'MIDI input {midi_input_name} not found')

        if midi_output_name:
            midi_output = self._init_output(midi_output_name)
            if midi_output:
                midi_out_port, out_name = midi_output
                self._midi_output = midi_out_port
                self._midi_output_name = out_name
            else:
                raise ValueError(f'MIDI output {midi_output_name} not found')

    def disconnect(self):
        if self._midi_input:
            self._log(f'Closing MIDI input "{self._midi_input_name}"...')
            self._midi_input.close_port()
            self._midi_input_name = None
            self._midi_input = None

        if self._midi_output:
            self._log(f'Closing MIDI output "{self._midi_output_name}"...')
            self._midi_output.close_port()
            self._midi_output_name = None
            self._midi_output = None

    def _log(self, message):
        self._callback_log('[MIDI Connection      ]  ' + message, True)

    def _init_input(self, device_name):
        if device_name is None:
            return None

        self._log(f'Opening MIDI input "{device_name}"...')
        try:
            midi_input = rtmidi.midiutil.open_midiinput(device_name, interactive=False, client_name="PythonMCU")
        except(rtmidi.InvalidPortError, rtmidi.NoDevicesError, rtmidi.SystemError) as e:
            self._log(f'MIDI In \'{device_name}\' not found.\nReason: {e}\n')
            return None

        return midi_input

    def _init_output(self, device_name):
        if device_name is None:
            return None

        self._log(f'Opening MIDI output "{device_name}"...')
        try:
            midi_output = rtmidi.midiutil.open_midioutput(device_name, interactive=False, client_name="PythonMCU")
        except(rtmidi.InvalidPortError, rtmidi.NoDevicesError, rtmidi.SystemError) as e:
            self._log(f'MIDI Out \'{device_name}\' not found.\nReason: {e}\n')
            return None

        return midi_output

    # --- MIDI processing ---
    def buffer_is_empty(self):
        if not self._midi_input:
            self._log('MIDI input not connected.')
            return False

        if msg := self._midi_input.get_message():
            self._input_buffer.append([msg[0]])  # Ignore timestamp
        del msg

        return not self._input_buffer

    def process_input_buffer(self, use_callback=True):
        if not self._midi_input:
            self._log('MIDI input not connected.')
            return

        while msg := self._midi_input.get_message():
            self._input_buffer.append([msg[0]])  # Ignore timestamp
        del msg

        if self._input_buffer:
            for message in self._input_buffer.pop(0):
                (status, message) = self._receive_message(message)

                # FIXME: Factorize and only display in DEBUG mode
                output = f'status {status:02X}: '
                for byte in message:
                    output += f'{byte:02X} '
                self._log('Raw message received: ' + output.strip())

                if use_callback:
                    self._callback(status, message)

    def _receive_message(self, message):
        status_byte = message[0] & 0xF0

        status = 0x00
        if status_byte == rtmidi.midiconstants.NOTE_OFF:
            status = self.NOTE_OFF_EVENT
        elif status_byte == rtmidi.midiconstants.NOTE_ON:
            status = self.NOTE_ON_EVENT
        elif status_byte == rtmidi.midiconstants.POLYPHONIC_PRESSURE:
            status = self.POLYPHONIC_KEY_PRESSURE
        elif status_byte == rtmidi.midiconstants.CONTROL_CHANGE:
            status = self.CONTROL_CHANGE
        elif status_byte == rtmidi.midiconstants.PROGRAM_CHANGE:
            status = self.PROGRAM_CHANGE
        elif status_byte == rtmidi.midiconstants.CHANNEL_PRESSURE:
            status = self.CHANNEL_PRESSURE
        elif status_byte == rtmidi.midiconstants.PITCH_BEND:
            status = self.PITCH_WHEEL_CHANGE
        elif status_byte == rtmidi.midiconstants.SYSTEM_EXCLUSIVE:
            status = self.SYSTEM_MESSAGE

        return status, message

    def _raw_send(self, message):

        # FIXME: Factorize and only display in DEBUG mode
        output = ''
        for byte in message:
            output += f'{byte:02X} '
        self._log('Raw message sent: ' + output.strip())

        self._midi_output.send_message(message)

    def send(self, status, data_1, data_2):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return
        msg = [status, data_1, data_2]
        self._raw_send(msg)

    def send_note_on(self, key, velocity):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

#        self._log(f'{self.NOTE_ON_EVENT:02X} {key:02X} {velocity:02X}')
        msg = [self.NOTE_ON_EVENT, key, velocity]
        self._raw_send(msg)

    def send_note_off(self, key, velocity):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

#        self._log(f'{self.NOTE_OFF_EVENT:02X} {key:02X} {velocity:02X}')
        msg = [self.NOTE_OFF_EVENT, key, velocity]
        self._raw_send(msg)

    def send_control_change(self, channel, cc_number, cc_value):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

#        self._log(f'{self.CONTROL_CHANGE + channel:02X} {cc_number:02X} {cc_value:02X}')
        msg = [self.CONTROL_CHANGE + channel, cc_number, cc_value]
        self._raw_send(msg)

    def send_pitch_wheel_change(self, channel, pitch):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

        pitch_high = pitch >> 7
        pitch_low = pitch & 0x7F
#        self._log(f'{self.PITCH_WHEEL_CHANGE + channel:02X} {pitch_low:02X} {pitch_high:02X}')
        msg = [self.PITCH_WHEEL_CHANGE + channel, pitch_low, pitch_high]
        self._raw_send(msg)

    def send_pitch_wheel_change_7bit(self, channel, pitch):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

#        self._log(f'{self.PITCH_WHEEL_CHANGE + channel:02X} {pitch:02X} {pitch:02X}')
        msg = [self.PITCH_WHEEL_CHANGE + channel, pitch, pitch]
        self._raw_send(msg)

    def send_sysex(self, header, data):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

        assert isinstance(header, list)
        assert isinstance(data, list)

        sysex = [rtmidi.midiconstants.SYSTEM_EXCLUSIVE]
        sysex.extend(header)
        sysex.extend(data)
        sysex.append(rtmidi.midiconstants.END_OF_EXCLUSIVE)

        assert sysex[0] == rtmidi.midiconstants.SYSTEM_EXCLUSIVE and sysex[-1] == rtmidi.midiconstants.END_OF_EXCLUSIVE

        self._raw_send(sysex)


if __name__ == "__main__":
    import time

    def log_callback(message):
        print(message)

    def midi_in_callback(status_byte, message):
        print(f'status {status_byte:02X}: ', )
        for byte in message:
            print(f'{byte:02X}', )

    MIDI_INPUT = 'In From MIDI Yoke:  2'
    MIDI_OUTPUT = 'Out To MIDI Yoke:  1'

    midi_connection = MidiConnection(log_callback, midi_in_callback)
    midi_connection.connect(MIDI_INPUT, MIDI_OUTPUT)

    midi_connection.send_control_change(0, 0x07, 0x80)
    midi_connection.send_sysex([0x01, 0x02], [0x11, 0x12, 0x13])

    try:
        while True:
            midi_connection.process_input_buffer()

            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    midi_connection.disconnect()
