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

import pygame.midi
import types

pygame.midi.init()


class MidiConnection:
    __module__ = __name__
    __doc__ = 'MIDI connection handler'

    NOTE_OFF_EVENT = 0x80
    NOTE_ON_EVENT = 0x90
    POLYPHONIC_KEY_PRESSURE = 0xA0
    CONTROL_CHANGE = 0xB0
    PROGRAM_CHANGE = 0xC0
    CHANNEL_PRESSURE = 0xD0
    PITCH_WHEEL_CHANGE = 0xE0
    SYSTEM_MESSAGE = 0xF0

    # --- initialisation ---

    def __init__(self, callback_log, callback):
        self._callback_log = callback_log
        self._callback = callback

        self._midi_input_name = None
        self._midi_output_name = None


    def connect(self, midi_input_name=None, midi_output_name=None):
        self._midi_input_name = midi_input_name
        if self._midi_input_name:
            self._midi_input = self._init_input(self._midi_input_name)

        self._midi_output_name = midi_output_name
        if self._midi_output_name:
            self._midi_output = self._init_output(self._midi_output_name)


    def disconnect(self):
        if self._midi_input:
            self._log('Closing MIDI input "%s"...' % self._midi_input_name)
            self._midi_input.close()

        if self._midi_output:
            self._log('Closing MIDI output "%s"...' % self._midi_output_name)
            self._midi_output.close()


    def _log(self, message):
        self._callback_log('[MIDI Connection      ]  ' + message, True)


    def _init_input(self, device_name):
        if device_name == None:
            return None

        for device_id in range(pygame.midi.get_count()):
            device = pygame.midi.get_device_info(device_id)

            if device[1] == device_name and (device[2] == 1):
                self._log('Opening MIDI input "%s"...' % device_name)
                return pygame.midi.Input(device_id)

        self._log('MIDI In \'%s\' not found.\n' % device_name)
        return None


    def _init_output(self, device_name):
        if device_name == None:
            return None

        for device_id in range(pygame.midi.get_count()):
            device = pygame.midi.get_device_info(device_id)

            if device[1] == device_name and (device[3] == 1):
                self._log('Opening MIDI output "%s"...' % device_name)
                return pygame.midi.Output(device_id, latency=0)

        self._log('MIDI Out \'%s\' not found.\n' % device_name)
        return None


    # --- static methods ---

    @staticmethod
    def get_midi_inputs():
        midi_inputs = []

        for id in range(pygame.midi.get_count()):
            device = pygame.midi.get_device_info(id)
            if device[2] == 1:
                midi_inputs.append(device[1])

        return midi_inputs


    @staticmethod
    def get_midi_outputs():
        midi_outputs = []

        for id in range(pygame.midi.get_count()):
            device = pygame.midi.get_device_info(id)
            if device[3] == 1:
                midi_outputs.append(device[1])

        return midi_outputs


    @staticmethod
    def get_default_midi_input():
        device_id = pygame.midi.get_default_input_id()

        if device_id < 0:
            return None
        else:
            device = pygame.midi.get_device_info(device_id)
            return device[1]


    @staticmethod
    def get_default_midi_output():
        device_id = pygame.midi.get_default_output_id()

        if device_id < 0:
            return None
        else:
            device = pygame.midi.get_device_info(device_id)
            return device[1]


    # --- MIDI processing ---

    def buffer_is_empty(self, use_callback=True):
        return not self._midi_input.poll()


    def process_input_buffer(self, use_callback=True):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

        while self._midi_input.poll():
            (status, message) = self._receive_message()

            if use_callback:
                self._callback(status, message)


    def _receive_message(self):
        message = self._midi_input.read(1)[0][0]
        status_byte = message[0] & 0xF0

        if message[0] == 0xF0:
            while 0xF7 not in message:
                message.extend(self._midi_input.read(1)[0][0])
            while message[-1] != 0xF7:
                del message[-1]

        if status_byte == self.NOTE_OFF_EVENT:
            status = self.NOTE_OFF_EVENT
            del message[3]
        elif status_byte == self.NOTE_ON_EVENT:
            status = self.NOTE_ON_EVENT
            del message[3]
        elif status_byte == self.POLYPHONIC_KEY_PRESSURE:
            status = self.POLYPHONIC_KEY_PRESSURE
            del message[3]
        elif status_byte == self.CONTROL_CHANGE:
            status = self.CONTROL_CHANGE
            del message[3]
        elif status_byte == self.PROGRAM_CHANGE:
            status = self.PROGRAM_CHANGE
            del message[2:3]
        elif status_byte == self.CHANNEL_PRESSURE:
            status = self.CHANNEL_PRESSURE
            del message[2:3]
        elif status_byte == self.PITCH_WHEEL_CHANGE:
            status = self.PITCH_WHEEL_CHANGE
            del message[3]
        elif status_byte == self.SYSTEM_MESSAGE:
            status = self.SYSTEM_MESSAGE

        return (status, message)


    def send(self, status, data_1, data_2):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

        self._midi_output.write_short(status, data_1, data_2)


    def send_note_on(self, key, velocity):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

        #self._log('%02X %02X %02X' % (self.NOTE_ON_EVENT, key, velocity))
        self._midi_output.write_short(self.NOTE_ON_EVENT, key, velocity)


    def send_note_off(self, key, velocity):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

        #self._log('%02X %02X %02X' % (self.NOTE_OFF_EVENT, key, velocity))
        self._midi_output.write_short(self.NOTE_OFF_EVENT, key, velocity)


    def send_control_change(self, channel, cc_number, cc_value):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

#         self._log('%02X %02X %02X' % \
#             (self.CONTROL_CHANGE + channel, cc_number, cc_value))
        self._midi_output.write_short( \
            self.CONTROL_CHANGE + channel, cc_number, cc_value)


    def send_pitch_wheel_change(self, channel, pitch):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

        pitch_high = pitch >> 7
        pitch_low = pitch & 0x7F
#         self._log('%02X %02X %02X' % \
#             (self.PITCH_WHEEL_CHANGE + channel, pitch_low, pitch_high))
        self._midi_output.write_short( \
            self.PITCH_WHEEL_CHANGE + channel, pitch_low, pitch_high)


    def send_pitch_wheel_change_7bit(self, channel, pitch):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

#         self._log('%02X %02X %02X' % \
#             (self.PITCH_WHEEL_CHANGE + channel, pitch, pitch))
        self._midi_output.write_short( \
            self.PITCH_WHEEL_CHANGE + channel, pitch, pitch)


    def send_sysex(self, header, data):
        if not self._midi_output:
            self._log('MIDI output not connected.')
            return

        assert(type(header) == types.ListType)
        assert(type(data) == types.ListType)

        sysex = [0xF0]
        sysex.extend(header)
        sysex.extend(data)
        sysex.append(0xF7)

        self._midi_output.write_sys_ex(0, sysex)


if __name__ == "__main__":
    import time

    def callback_log(message):
        print message

    def callback_midi_in(status_byte, message):
        print 'status %02X: ' % status_byte,
        for byte in message:
            print '%02X' % byte,
        print

    midi_input = 'In From MIDI Yoke:  2'
    midi_output = 'Out To MIDI Yoke:  1'

    midi_connection = MidiConnection(callback_log, callback_midi_in)
    midi_connection.connect(midi_input, midi_output)

    midi_connection.send_control_change(0, 0x07, 0x80)
    midi_connection.send_sysex([0x01, 0x02], [0x11, 0x12, 0x13])

    try:
        while True:
            midi_connection.process_input_buffer()

            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    midi_connection.disconnect()
