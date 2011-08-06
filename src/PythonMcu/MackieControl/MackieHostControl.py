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
import sys

if __name__ == "__main__":
    # allow "PythonMcu" package imports when executing this module
    sys.path.append('../../')

from PythonMcu.Midi.MidiConnection import MidiConnection


class MackieHostControl:
    __module__ = __name__
    __doc__ = 'Mackie Host Control for Novation ZeRO SL MkII'

    SWITCH_RELEASED = 0
    SWITCH_PRESSED = 1
    SWITCH_PRESSED_RELEASED = 2

    VPOT_CLOCKWISE = 0
    VPOT_COUNTER_CLOCKWISE = 1

    _LED_SWITCH_CHANNEL_RECORD_READY = 0x00
    _LED_SWITCH_CHANNEL_SOLO = 0x08

    _LED_SWITCH_CHANNEL_MUTE = 0x10
    _LED_SWITCH_CHANNEL_SELECT = 0x18
    _SWITCH_CHANNEL_VSELECT = 0x20
    _LED_SWITCH_ASSIGNMENT_TRACK = 0x28
    _LED_SWITCH_ASSIGNMENT_SEND = 0x29
    _LED_SWITCH_ASSIGNMENT_PAN_SURROUND = 0x2A
    _LED_SWITCH_ASSIGNMENT_PLUG_IN = 0x2B

    _LED_SWITCH_ASSIGNMENT_EQ = 0x2C
    _LED_SWITCH_ASSIGNMENT_INSTRUMENT = 0x2D
    _SWITCH_FADER_BANKS_BANK_LEFT = 0x2E
    _SWITCH_FADER_BANKS_BANK_RIGHT = 0x2F
    _SWITCH_FADER_BANKS_CHANNEL_LEFT = 0x30
    _SWITCH_FADER_BANKS_CHANNEL_RIGHT = 0x31
    _LED_SWITCH_FLIP = 0x32
    _LED_SWITCH_GLOBAL_VIEW = 0x33
    _SWITCH_NAME_VALUE = 0x34
    _SWITCH_SMPTE_BEATS = 0x35
    _SWITCH_CHANNEL_FUNCTION = 0x36
    _SWITCH_GLOBAL_VIEW_MIDI_TRACKS = 0x3E
    _SWITCH_GLOBAL_VIEW_INPUTS = 0x3F
    _SWITCH_GLOBAL_VIEW_AUDIO_TRACKS = 0x40
    _SWITCH_GLOBAL_VIEW_AUDIO_INSTRUMENTS = 0x41
    _SWITCH_GLOBAL_VIEW_AUX = 0x42
    _SWITCH_GLOBAL_VIEW_BUSSES = 0x43
    _SWITCH_GLOBAL_VIEW_OUTPUTS = 0x44
    _SWITCH_GLOBAL_VIEW_USER = 0x45
    _SWITCH_SHIFT = 0x46
    _SWITCH_OPTION = 0x47
    _SWITCH_CONTROL = 0x48
    _SWITCH_COMMAND_ALT = 0x49
    _LED_SWITCH_AUTOMATION_READ_OFF = 0x4A

    _LED_SWITCH_AUTOMATION_WRITE = 0x4B
    _LED_SWITCH_AUTOMATION_TRIM = 0x4C
    _LED_SWITCH_AUTOMATION_TOUCH = 0x4D
    _LED_SWITCH_AUTOMATION_LATCH = 0x4E
    _LED_SWITCH_GROUP = 0x4F
    _LED_SWITCH_UTILITIES_SAVE = 0x50
    _LED_SWITCH_UTILITIES_UNDO = 0x51
    _SWITCH_UTILITIES_CANCEL = 0x52
    _SWITCH_UTILITIES_ENTER = 0x53
    _LED_SWITCH_MARKER = 0x54
    _LED_SWITCH_NUDGE = 0x55
    _LED_SWITCH_CYCLE = 0x56
    _LED_SWITCH_DROP = 0x57
    _LED_SWITCH_REPLACE = 0x58
    _LED_SWITCH_CLICK = 0x59
    _LED_SWITCH_SOLO = 0x5A
    _LED_SWITCH_REWIND = 0x5B
    _LED_SWITCH_FAST_FORWARD = 0x5C
    _LED_SWITCH_STOP = 0x5D
    _LED_SWITCH_PLAY = 0x5E
    _LED_SWITCH_RECORD = 0x5F
    _SWITCH_CURSOR_UP = 0x60
    _SWITCH_CURSOR_DOWN = 0x61
    _SWITCH_CURSOR_LEFT = 0x62
    _SWITCH_CURSOR_RIGHT = 0x63
    _LED_SWITCH_ZOOM = 0x64
    _LED_SWITCH_SCRUB = 0x65
    _SWITCH_USER_SWITCH_A = 0x66
    _SWITCH_USER_SWITCH_B = 0x67
    _SWITCH_CHANNEL_FADER_TOUCH = 0x68

    _SWITCH_MASTER_FADER_TOUCH = 0x70

    _LED_SMPTE = 0x71
    _LED_BEATS = 0x72
    _LED_RUDE_SOLO = 0x73
    _LED_RELAY_CLICK = 0x76


    def __init__(self, midi_input, midi_output, mcu_model_id):
        self._log('Opening MIDI ports...')
        self._midi = MidiConnection(self.receive_midi, midi_input, midi_output)
        self.unset_hardware_controller()

        # LCD has 2 rows with 56 characters each, fill with spaces
        self._lcd_characters = [' '] * 56 * 2
        self._lcd_strings = ['', '']

        # Mackie Control model IDs:
        # * 0x10: Logic Control
        # * 0x11: Logic Control XT
        # * 0x14: Mackie Control
        # * 0x15: Mackie Control XT
        #
        # Ableton Live 8 needs 0x14 in order to write to the LCD!
        self._mcu_model_id = mcu_model_id


    def _log(self, message):
        print '[Mackie Host Control  ]  ' + message


    # --- initialisation ---

    def set_hardware_controller(self, controller):
        self._hardware_controller = controller

        self._display_lcd_available = \
            self._hardware_controller.has_display_lcd()
        self._automated_faders_available = \
            self._hardware_controller.has_automated_faders()
        self._display_7seg_available = \
            self._hardware_controller.has_display_7seg()
        self._display_timecode_available = \
            self._hardware_controller.has_display_timecode()
        self._meter_bridge_available = \
            self._hardware_controller.has_meter_bridge()


    def unset_hardware_controller(self):
        self._hardware_controller = None

        self._display_lcd_available = False
        self._automated_faders_available = False
        self._display_7seg_available = False
        self._display_timecode_available = False
        self._meter_bridge_available = False


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
            if self._hardware_controller:
                self._hardware_controller.host_connected()

        self._log('Connected.')


    def disconnect(self):
        self._log('Disconnecting...')

        self._midi.disconnect()

        self._log('Disconnected.')


    # --- static methods ---

    @staticmethod
    def get_mcu_model_from_id(id):
        if id == 0x10:
            return 'Logic Control'
        elif id == 0x11:
            return 'Logic Control XT'
        elif id == 0x14:
            return 'Mackie Control'
        elif id == 0x15:
            return 'Mackie Control XT'
        else:
            return None


    @staticmethod
    def get_mcu_id_from_model(model):
        if model == 'Logic Control':
            return 0x10
        elif model == 'Logic Control XT':
            return 0x11
        elif model == 'Mackie Control':
            return 0x14
        elif model == 'Mackie Control XT':
            return 0x15
        else:
            return None


    @staticmethod
    def get_preferred_mcu_model():
        return 'Mackie Control'


    @staticmethod
    def get_preferred_mcu_model_id():
        return MackieHostControl.get_mcu_id_from_model( \
            MackieHostControl.get_preferred_mcu_model())


    @staticmethod
    def get_preferred_midi_input():
        return 'In From MIDI Yoke:  2'


    @staticmethod
    def get_preferred_midi_output():
        return 'Out To MIDI Yoke:  1'


    # --- MIDI processing ---

    def process_midi_input(self):
        self._midi.process_input_buffer()


    def receive_midi(self, status, message):
        if status == MidiConnection.SYSTEM_MESSAGE:
            if message[0:6] == \
                    [0xF0, 0x00, 0x00, 0x66, self._mcu_model_id, 0x12]:
                if self._display_lcd_available:
                    lcd_position = message[6] - 1
                    temp_string = message[7:-1]

                    for hex_code in temp_string:
                        lcd_position += 1
                        if lcd_position >= 112:
                            break

                        # convert illegal characters to asterisk
                        if (hex_code < 0x20) or (hex_code > 0x7F):
                            hex_code = 0x2A
                        self._lcd_characters[lcd_position] = chr(hex_code)

                    line_1 = ''.join(self._lcd_characters[:56])
                    line_2 = ''.join(self._lcd_characters[56:])

                    if self._lcd_strings[0] != line_1:
                        self._lcd_strings[0] = line_1
                        self._hardware_controller.set_lcd(1, line_1)

                    if self._lcd_strings[1] != line_2:
                        self._lcd_strings[1] = line_2
                        self._hardware_controller.set_lcd(2, line_2)
        elif status == MidiConnection.PITCH_WHEEL_CHANGE:
            if self._automated_faders_available:
                fader_id = message[0] & 0x0F
                fader_position = (message[1] + (message[2] << 7)) >> 4
                self._hardware_controller.fader_moved(fader_id, fader_position)
        elif status == MidiConnection.NOTE_ON_EVENT:
            led_id = message[1]
            led_status = 0  # off
            if message[2] == 0x7F:
                led_status = 1  # on
            elif message[2] == 0x01:
                led_status = 2  # flashing
            self._set_led(led_id, led_status)
        elif (status == MidiConnection.CONTROL_CHANGE) and \
                ((message[1] & 0xF0) == 0x30):
            vpot_id = message[1] & 0x0F
            vpot_center_led = (message[2] & 0x40) >> 7
            vpot_mode = (message[2] & 0x30) >> 4
            vpot_position = message[2] & 0x0F
            self._hardware_controller.set_vpot_led_ring(vpot_id, vpot_center_led, vpot_mode, vpot_position)
        elif (status == MidiConnection.CONTROL_CHANGE) and \
                ((message[1] & 0xF0) == 0x40):
            position = message[1] & 0x0F
            character_code = message[2]
            if (position < 10):
                if self._display_timecode_available:
                    self._hardware_controller.set_display_timecode( \
                        position, character_code)
            elif self._display_7seg_available:
                self._hardware_controller.set_display_7seg( \
                    position, character_code)
        elif status == MidiConnection.CHANNEL_PRESSURE:
            if self._meter_bridge_available:
                meter_id = (message[1] & 0x70) >> 4
                meter_level = message[1] & 0x0F
                self._hardware_controller.set_peak_level(meter_id, meter_level)
        else:
            print 'status %02X: ' % status,
            for byte in message:
                print '%02X' % byte,
            print


    def send_midi_control_change(self, midi_channel, cc_number, cc_value):
        self._midi.send_control_change(midi_channel, cc_number, cc_value)


    def send_midi_sysex(self, data):
        assert(type(data) == types.ListType)

        header = [0x00, 0x00, 0x66, 0x11]

        self._midi.send_sysex(header, data)


    # --- commands from hardware control ---

    def move_vpot(self, midi_channel, vpot_id, direction, number_of_ticks):
        vpot_movement = number_of_ticks
        if direction == self.VPOT_COUNTER_CLOCKWISE:
            vpot_movement = vpot_movement + 0x40

        self._midi.send_control_change( \
            midi_channel, 0x10 + vpot_id, vpot_movement)


    def move_vpot_raw(self, midi_channel, vpot_id, vpot_movement):
        self._midi.send_control_change( \
            midi_channel, 0x10 + vpot_id, vpot_movement)


    def move_fader(self, fader_id, fader_value):
        self._midi.send_pitch_wheel_change(fader_id, fader_value)


    def move_fader_7bit(self, fader_id, fader_value):
        self._midi.send_pitch_wheel_change_7bit(fader_id, fader_value)


    def _key_pressed(self, status, switch_id):
        if status == self.SWITCH_RELEASED:
            self._midi.send_note_on(switch_id, 0x00)
        elif status == self.SWITCH_PRESSED:
            self._midi.send_note_on(switch_id, 0x7F)
        elif status == self.SWITCH_PRESSED_RELEASED:
            self._midi.send_note_on(switch_id, 0x7F)
            self._midi.send_note_on(switch_id, 0x00)
        else:
            self._log( \
                'Illegal key press status 0x%02X on switch 0x%02X detected!' % \
                    (status, switch_id))


    def keypress_record_ready_channel(self, channel, status):
        # channel: 1 - 8
        self._key_pressed( \
            status, self._LED_SWITCH_CHANNEL_RECORD_READY + channel - 1)


    def keypress_record_ready_channel_1(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_RECORD_READY)


    def keypress_record_ready_channel_2(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_RECORD_READY + 1)


    def keypress_record_ready_channel_3(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_RECORD_READY + 2)


    def keypress_record_ready_channel_4(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_RECORD_READY + 3)


    def keypress_record_ready_channel_5(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_RECORD_READY + 4)


    def keypress_record_ready_channel_6(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_RECORD_READY + 5)


    def keypress_record_ready_channel_7(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_RECORD_READY + 6)


    def keypress_record_ready_channel_8(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_RECORD_READY + 7)


    def keypress_solo_channel(self, channel, status):
        # channel: 1 - 8
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SOLO + channel - 1)


    def keypress_solo_channel_1(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SOLO)


    def keypress_solo_channel_2(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SOLO + 1)


    def keypress_solo_channel_3(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SOLO + 2)


    def keypress_solo_channel_4(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SOLO + 3)


    def keypress_solo_channel_5(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SOLO + 4)


    def keypress_solo_channel_6(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SOLO + 5)


    def keypress_solo_channel_7(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SOLO + 6)


    def keypress_solo_channel_8(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SOLO + 7)


    def keypress_mute_channel(self, channel, status):
        # channel: 1 - 8
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_MUTE + channel - 1)


    def keypress_mute_channel_1(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_MUTE)


    def keypress_mute_channel_2(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_MUTE + 1)


    def keypress_mute_channel_3(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_MUTE + 2)


    def keypress_mute_channel_4(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_MUTE + 3)


    def keypress_mute_channel_5(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_MUTE + 4)


    def keypress_mute_channel_6(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_MUTE + 5)


    def keypress_mute_channel_7(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_MUTE + 6)


    def keypress_mute_channel_8(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_MUTE + 7)


    def keypress_select_channel(self, channel, status):
        # channel: 1 - 8
        self._key_pressed( \
            status, self._LED_SWITCH_CHANNEL_SELECT + channel - 1)


    def keypress_select_channel_1(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SELECT)


    def keypress_select_channel_2(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SELECT + 1)


    def keypress_select_channel_3(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SELECT + 2)


    def keypress_select_channel_4(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SELECT + 3)


    def keypress_select_channel_5(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SELECT + 4)


    def keypress_select_channel_6(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SELECT + 5)


    def keypress_select_channel_7(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SELECT + 6)


    def keypress_select_channel_8(self, status):
        self._key_pressed(status, self._LED_SWITCH_CHANNEL_SELECT + 7)


    def keypress_vselect_channel(self, channel, status):
        # channel: 1 - 8
        self._key_pressed(status, self._SWITCH_CHANNEL_VSELECT + channel - 1)


    def keypress_vselect_channel_1(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_VSELECT)


    def keypress_vselect_channel_2(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_VSELECT + 1)


    def keypress_vselect_channel_3(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_VSELECT + 2)


    def keypress_vselect_channel_4(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_VSELECT + 3)


    def keypress_vselect_channel_5(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_VSELECT + 4)


    def keypress_vselect_channel_6(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_VSELECT + 5)


    def keypress_vselect_channel_7(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_VSELECT + 6)


    def keypress_vselect_channel_8(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_VSELECT + 7)


    def keypress_function_channel(self, channel, status):
        # channel: 1 - 8
        self._key_pressed(status, self._SWITCH_CHANNEL_FUNCTION + channel - 1)


    def keypress_function_channel_1(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FUNCTION)


    def keypress_function_channel_2(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FUNCTION + 1)


    def keypress_function_channel_3(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FUNCTION + 2)


    def keypress_function_channel_4(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FUNCTION + 3)


    def keypress_function_channel_5(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FUNCTION + 4)


    def keypress_function_channel_6(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FUNCTION + 5)


    def keypress_function_channel_7(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FUNCTION + 6)


    def keypress_function_channel_8(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FUNCTION + 7)


    def keypress_assignment_track(self, status):
        self._key_pressed(status, self._LED_SWITCH_ASSIGNMENT_TRACK)


    def keypress_assignment_send(self, status):
        self._key_pressed(status, self._LED_SWITCH_ASSIGNMENT_SEND)


    def keypress_assignment_pan_surround(self, status):
        self._key_pressed(status, self._LED_SWITCH_ASSIGNMENT_PAN_SURROUND)


    def keypress_assignment_plug_in(self, status):
        self._key_pressed(status, self._LED_SWITCH_ASSIGNMENT_PLUG_IN)


    def keypress_assignment_eq(self, status):
        self._key_pressed(status, self._LED_SWITCH_ASSIGNMENT_EQ)


    def keypress_assignment_instrument(self, status):
        self._key_pressed(status, self._LED_SWITCH_ASSIGNMENT_INSTRUMENT)


    def keypress_fader_banks_bank_left(self, status):
        self._key_pressed(status, self._SWITCH_FADER_BANKS_BANK_LEFT)


    def keypress_fader_banks_bank_right(self, status):
        self._key_pressed(status, self._SWITCH_FADER_BANKS_BANK_RIGHT)


    def keypress_fader_banks_channel_left(self, status):
        self._key_pressed(status, self._SWITCH_FADER_BANKS_CHANNEL_LEFT)


    def keypress_fader_banks_channel_right(self, status):
        self._key_pressed(status, self._SWITCH_FADER_BANKS_CHANNEL_RIGHT)


    def keypress_flip(self, status):
        self._key_pressed(status, self._LED_SWITCH_FLIP)


    def keypress_global_view(self, status):
        self._key_pressed(status, self._LED_SWITCH_GLOBAL_VIEW)


    def keypress_name_value(self, status):
        self._key_pressed(status, self._SWITCH_NAME_VALUE)


    def keypress_smpte_beats(self, status):
        self._key_pressed(status, self._SWITCH_SMPTE_BEATS)


    def keypress_global_view_midi_tracks(self, status):
        self._key_pressed(status, self._SWITCH_GLOBAL_VIEW_MIDI_TRACKS)


    def keypress_global_view_inputs(self, status):
        self._key_pressed(status, self._SWITCH_GLOBAL_VIEW_INPUTS)


    def keypress_global_view_audio_tracks(self, status):
        self._key_pressed(status, self._SWITCH_GLOBAL_VIEW_AUDIO_TRACKS)


    def keypress_global_view_audio_instruments(self, status):
        self._key_pressed(status, self._SWITCH_GLOBAL_VIEW_AUDIO_INSTRUMENTS)


    def keypress_global_view_aux(self, status):
        self._key_pressed(status, self._SWITCH_GLOBAL_VIEW_AUX)


    def keypress_global_view_busses(self, status):
        self._key_pressed(status, self._SWITCH_GLOBAL_VIEW_BUSSES)


    def keypress_global_view_outputs(self, status):
        self._key_pressed(status, self._SWITCH_GLOBAL_VIEW_OUTPUTS)


    def keypress_global_view_user(self, status):
        self._key_pressed(status, self._SWITCH_GLOBAL_VIEW_USER)


    def keypress_shift(self, status):
        self._key_pressed(status, self._SWITCH_SHIFT)


    def keypress_option(self, status):
        self._key_pressed(status, self._SWITCH_OPTION)


    def keypress_control(self, status):
        self._key_pressed(status, self._SWITCH_CONTROL)


    def keypress_command_alt(self, status):
        self._key_pressed(status, self._SWITCH_COMMAND_ALT)


    def keypress_automation_read_off(self, status):
        self._key_pressed(status, self._LED_SWITCH_AUTOMATION_READ_OFF)


    def keypress_automation_write(self, status):
        self._key_pressed(status, self._LED_SWITCH_AUTOMATION_WRITE)


    def keypress_automation_trim(self, status):
        self._key_pressed(status, self._LED_SWITCH_AUTOMATION_TRIM)


    def keypress_automation_touch(self, status):
        self._key_pressed(status, self._LED_SWITCH_AUTOMATION_TOUCH)


    def keypress_automation_latch(self, status):
        self._key_pressed(status, self._LED_SWITCH_AUTOMATION_LATCH)


    def keypress_group(self, status):
        self._key_pressed(status, self._LED_SWITCH_GROUP)


    def keypress_utilities_save(self, status):
        self._key_pressed(status, self._LED_SWITCH_UTILITIES_SAVE)


    def keypress_utilities_undo(self, status):
        self._key_pressed(status, self._LED_SWITCH_UTILITIES_UNDO)


    def keypress_utilities_cancel(self, status):
        self._key_pressed(status, self._SWITCH_UTILITIES_CANCEL)


    def keypress_utilities_enter(self, status):
        self._key_pressed(status, self._SWITCH_UTILITIES_ENTER)


    def keypress_marker(self, status):
        self._key_pressed(status, self._LED_SWITCH_MARKER)


    def keypress_nudge(self, status):
        self._key_pressed(status, self._LED_SWITCH_NUDGE)


    def keypress_cycle(self, status):
        self._key_pressed(status, self._LED_SWITCH_CYCLE)


    def keypress_drop(self, status):
        self._key_pressed(status, self._LED_SWITCH_DROP)


    def keypress_replace(self, status):
        self._key_pressed(status, self._LED_SWITCH_REPLACE)


    def keypress_click(self, status):
        self._key_pressed(status, self._LED_SWITCH_CLICK)


    def keypress_solo(self, status):
        self._key_pressed(status, self._LED_SWITCH_SOLO)


    def keypress_rewind(self, status):
        self._key_pressed(status, self._LED_SWITCH_REWIND)


    def keypress_fast_forward(self, status):
        self._key_pressed(status, self._LED_SWITCH_FAST_FORWARD)


    def keypress_stop(self, status):
        self._key_pressed(status, self._LED_SWITCH_STOP)


    def keypress_play(self, status):
        self._key_pressed(status, self._LED_SWITCH_PLAY)


    def keypress_record(self, status):
        self._key_pressed(status, self._LED_SWITCH_RECORD)


    def keypress_cursor_up(self, status):
        self._key_pressed(status, self._SWITCH_CURSOR_UP)


    def keypress_cursor_down(self, status):
        self._key_pressed(status, self._SWITCH_CURSOR_DOWN)


    def keypress_cursor_left(self, status):
        self._key_pressed(status, self._SWITCH_CURSOR_LEFT)


    def keypress_cursor_right(self, status):
        self._key_pressed(status, self._SWITCH_CURSOR_RIGHT)


    def keypress_zoom(self, status):
        self._key_pressed(status, self._LED_SWITCH_ZOOM)


    def keypress_scrub(self, status):
        self._key_pressed(status, self._LED_SWITCH_SCRUB)


    def keypress_user_switch(self, switch_number, status):
        # switch_number: 1 - 2
        if switch_number == 1:
            self._key_pressed(status, self._SWITCH_USER_SWITCH_A)
        else:
            self._key_pressed(status, self._SWITCH_USER_SWITCH_B)


    def keypress_user_switch_1(self, status):
        self._key_pressed(status, self._SWITCH_USER_SWITCH_A)


    def keypress_user_switch_2(self, status):
        self._key_pressed(status, self._SWITCH_USER_SWITCH_B)


    def keypress_fader_touch_channel(self, channel, status):
        # channel: 1 - 8
        self._key_pressed( \
            status, self._SWITCH_CHANNEL_FADER_TOUCH + channel - 1)


    def keypress_fader_touch_channel_1(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FADER_TOUCH)


    def keypress_fader_touch_channel_2(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FADER_TOUCH + 1)


    def keypress_fader_touch_channel_3(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FADER_TOUCH + 2)


    def keypress_fader_touch_channel_4(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FADER_TOUCH + 3)


    def keypress_fader_touch_channel_5(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FADER_TOUCH + 4)


    def keypress_fader_touch_channel_6(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FADER_TOUCH + 5)


    def keypress_fader_touch_channel_7(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FADER_TOUCH + 6)


    def keypress_fader_touch_channel_8(self, status):
        self._key_pressed(status, self._SWITCH_CHANNEL_FADER_TOUCH + 7)


    def keypress_fader_touch_master(self, status):
        self._key_pressed(status, self._SWITCH_MASTER_FADER_TOUCH)


    # --- commands from Mackie Control host ---

    def _set_led(self, id, status):
        selector = {
            self._LED_SWITCH_CHANNEL_RECORD_READY: \
                'self._hardware_controller.set_led_channel_record_ready(0, status)',
            self._LED_SWITCH_CHANNEL_RECORD_READY + 1: \
                'self._hardware_controller.set_led_channel_record_ready(1, status)',
            self._LED_SWITCH_CHANNEL_RECORD_READY + 2: \
                'self._hardware_controller.set_led_channel_record_ready(2, status)',
            self._LED_SWITCH_CHANNEL_RECORD_READY + 3: \
                'self._hardware_controller.set_led_channel_record_ready(3, status)',
            self._LED_SWITCH_CHANNEL_RECORD_READY + 4: \
                'self._hardware_controller.set_led_channel_record_ready(4, status)',
            self._LED_SWITCH_CHANNEL_RECORD_READY + 5: \
                'self._hardware_controller.set_led_channel_record_ready(5, status)',
            self._LED_SWITCH_CHANNEL_RECORD_READY + 6: \
                'self._hardware_controller.set_led_channel_record_ready(6, status)',
            self._LED_SWITCH_CHANNEL_RECORD_READY + 7: \
                'self._hardware_controller.set_led_channel_record_ready(7, status)',
            self._LED_SWITCH_CHANNEL_SOLO: \
                'self._hardware_controller.set_led_channel_solo(0, status)',
            self._LED_SWITCH_CHANNEL_SOLO + 1: \
                'self._hardware_controller.set_led_channel_solo(1, status)',
            self._LED_SWITCH_CHANNEL_SOLO + 2: \
                'self._hardware_controller.set_led_channel_solo(2, status)',
            self._LED_SWITCH_CHANNEL_SOLO + 3: \
                'self._hardware_controller.set_led_channel_solo(3, status)',
            self._LED_SWITCH_CHANNEL_SOLO + 4: \
                'self._hardware_controller.set_led_channel_solo(4, status)',
            self._LED_SWITCH_CHANNEL_SOLO + 5: \
                'self._hardware_controller.set_led_channel_solo(5, status)',
            self._LED_SWITCH_CHANNEL_SOLO + 6: \
                'self._hardware_controller.set_led_channel_solo(6, status)',
            self._LED_SWITCH_CHANNEL_SOLO + 7: \
                'self._hardware_controller.set_led_channel_solo(7, status)',
            self._LED_SWITCH_CHANNEL_MUTE: \
                'self._hardware_controller.set_led_channel_mute(0, status)',
            self._LED_SWITCH_CHANNEL_MUTE + 1: \
                'self._hardware_controller.set_led_channel_mute(1, status)',
            self._LED_SWITCH_CHANNEL_MUTE + 2: \
                'self._hardware_controller.set_led_channel_mute(2, status)',
            self._LED_SWITCH_CHANNEL_MUTE + 3: \
                'self._hardware_controller.set_led_channel_mute(3, status)',
            self._LED_SWITCH_CHANNEL_MUTE + 4: \
                'self._hardware_controller.set_led_channel_mute(4, status)',
            self._LED_SWITCH_CHANNEL_MUTE + 5: \
                'self._hardware_controller.set_led_channel_mute(5, status)',
            self._LED_SWITCH_CHANNEL_MUTE + 6: \
                'self._hardware_controller.set_led_channel_mute(6, status)',
            self._LED_SWITCH_CHANNEL_MUTE + 7: \
                'self._hardware_controller.set_led_channel_mute(7, status)',
            self._LED_SWITCH_CHANNEL_SELECT: \
                'self._hardware_controller.set_led_channel_select(0, status)',
            self._LED_SWITCH_CHANNEL_SELECT + 1: \
                'self._hardware_controller.set_led_channel_select(1, status)',
            self._LED_SWITCH_CHANNEL_SELECT + 2: \
                'self._hardware_controller.set_led_channel_select(2, status)',
            self._LED_SWITCH_CHANNEL_SELECT + 3: \
                'self._hardware_controller.set_led_channel_select(3, status)',
            self._LED_SWITCH_CHANNEL_SELECT + 4: \
                'self._hardware_controller.set_led_channel_select(4, status)',
            self._LED_SWITCH_CHANNEL_SELECT + 5: \
                'self._hardware_controller.set_led_channel_select(5, status)',
            self._LED_SWITCH_CHANNEL_SELECT + 6: \
                'self._hardware_controller.set_led_channel_select(6, status)',
            self._LED_SWITCH_CHANNEL_SELECT + 7: \
                'self._hardware_controller.set_led_channel_select(7, status)',
            self._LED_SWITCH_ASSIGNMENT_TRACK: \
                'self._hardware_controller.set_led_assignment_track(status)',
            self._LED_SWITCH_ASSIGNMENT_SEND: \
                'self._hardware_controller.set_led_assignment_send(status)',
            self._LED_SWITCH_ASSIGNMENT_PAN_SURROUND: \
                'self._hardware_controller.set_led_assignment_pan_surround(status)',
            self._LED_SWITCH_ASSIGNMENT_PLUG_IN: \
                'self._hardware_controller.set_led_assignment_plug_in(status)',
            self._LED_SWITCH_ASSIGNMENT_EQ: \
                'self._hardware_controller.set_led_assignment_eq(status)',
            self._LED_SWITCH_ASSIGNMENT_INSTRUMENT: \
                'self._hardware_controller.set_led_assignment_instrument(status)',
            self._LED_SWITCH_FLIP: \
                'self._hardware_controller.set_led_flip(status)',
            self._LED_SWITCH_GLOBAL_VIEW: \
                'self._hardware_controller.set_led_global_view(status)',
            self._LED_SWITCH_AUTOMATION_READ_OFF: \
                'self._hardware_controller.set_led_automation_read_off(status)',
            self._LED_SWITCH_AUTOMATION_WRITE: \
                'self._hardware_controller.set_led_automation_write(status)',
            self._LED_SWITCH_AUTOMATION_TRIM: \
                'self._hardware_controller.set_led_automation_trim(status)',
            self._LED_SWITCH_AUTOMATION_TOUCH: \
                'self._hardware_controller.set_led_automation_touch(status)',
            self._LED_SWITCH_AUTOMATION_LATCH: \
                'self._hardware_controller.set_led_automation_latch(status)',
            self._LED_SWITCH_GROUP: \
                'self._hardware_controller.set_led_group(status)',
            self._LED_SWITCH_UTILITIES_SAVE: \
                'self._hardware_controller.set_led_utilities_save(status)',
            self._LED_SWITCH_UTILITIES_UNDO: \
                'self._hardware_controller.set_led_utilities_undo(status)',
            self._LED_SWITCH_MARKER: \
                'self._hardware_controller.set_led_marker(status)',
            self._LED_SWITCH_NUDGE: \
                'self._hardware_controller.set_led_nudge(status)',
            self._LED_SWITCH_CYCLE: \
                'self._hardware_controller.set_led_cycle(status)',
            self._LED_SWITCH_DROP: \
                'self._hardware_controller.set_led_drop(status)',
            self._LED_SWITCH_REPLACE: \
                'self._hardware_controller.set_led_replace(status)',
            self._LED_SWITCH_CLICK: \
                'self._hardware_controller.set_led_click(status)',
            self._LED_SWITCH_SOLO: \
                'self._hardware_controller.set_led_solo(status)',
            self._LED_SWITCH_REWIND: \
                'self._hardware_controller.set_led_rewind(status)',
            self._LED_SWITCH_FAST_FORWARD: \
                'self._hardware_controller.set_led_fast_forward(status)',
            self._LED_SWITCH_STOP: \
                'self._hardware_controller.set_led_stop(status)',
            self._LED_SWITCH_PLAY: \
                'self._hardware_controller.set_led_play(status)',
            self._LED_SWITCH_RECORD: \
                'self._hardware_controller.set_led_record(status)',
            self._LED_SWITCH_ZOOM: \
                'self._hardware_controller.set_led_zoom(status)',
            self._LED_SWITCH_SCRUB: \
                'self._hardware_controller.set_led_scrub(status)',
            self._LED_SMPTE: \
                'self._hardware_controller.set_led_smpte(status)',
            self._LED_BEATS: \
                'self._hardware_controller.set_led_beats(status)',
            self._LED_RUDE_SOLO: \
                'self._hardware_controller.set_led_rude_solo(status)',
            self._LED_RELAY_CLICK: \
                'self._hardware_controller.set_led_relay_click(status)'
            }

        if id in selector:
            eval(selector[id])
        else:
            led_status = 'off'
            if status == 1:
                status = 'on'
            elif status == 2:
                status = 'flashing'

            self._log('LED 0x%02X NOT implemented (%s).' % (id, led_status))


if __name__ == "__main__":
    midi_input = 'In From MIDI Yoke:  2'
    midi_output = 'Out To MIDI Yoke:  1'

    host_control = MackieHostControl(midi_input, midi_output)
    host_control.connect()

    host_control.move_fader_7bit(0, 80)

    host_control.disconnect()
