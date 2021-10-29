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

from ..Midi.MidiConnection import MidiConnection


class _MidiControllerTemplate:
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

    def __init__(self, midi_input_name, midi_output_name, callback_log):
        self.callback_log = callback_log

        # LCD has 2 rows with 56 characters each, fill with spaces
        self._lcd_characters = [' '] * 2
        self._lcd_overlay_characters = [' '] * 2

        for line in range(2):
            # noinspection PyTypeChecker
            self._lcd_characters[line] = [' '] * 56
            # noinspection PyTypeChecker
            self._lcd_overlay_characters[line] = [' '] * 56

        self._show_overlay = [False, False]

        self._log('Initialising MIDI ports...', True)
        self._midi_input_name = midi_input_name
        self._midi_output_name = midi_output_name
        self.midi = MidiConnection(self.callback_log, self.receive_midi)

        # Initialized by set_interconnector()
        self.interconnector = None

        self.display_lcd_available = True
        self.automated_faders_available = True
        self.display_7seg_available = True
        self.display_timecode_available = True
        self.meter_bridge_available = True

        self.display_7seg_characters = []
        for _ in range(4):
            self.display_7seg_characters.append(' ')

        self.display_timecode_characters = []
        for _ in range(20):
            self.display_timecode_characters.append(' ')

    @staticmethod
    def get_usage_hint():
        return ''

    def _log(self, message, repaint=False):
        self.callback_log('[Controller Template]  ' + message, repaint)

    # --- initialisation ---
    def set_interconnector(self, host):
        self.interconnector = host

    def unset_interconnector(self):
        self.interconnector = None

    def connect(self):
        self._log('Opening MIDI ports...', True)
        self.midi.connect(self._midi_input_name, self._midi_output_name)
        #self._register_all_controls()

    def _register_all_controls(self):

        # Register all controls (According to Logic Control specs)
        ## REC/RDY Ch. 1-8 (Switch + LED)
        self.register_control('record_ready_channel_1', 0x00)
        self.register_control('record_ready_channel_2', 0x01)
        self.register_control('record_ready_channel_3', 0x02)
        self.register_control('record_ready_channel_4', 0x03)
        self.register_control('record_ready_channel_5', 0x04)
        self.register_control('record_ready_channel_6', 0x05)
        self.register_control('record_ready_channel_7', 0x06)
        self.register_control('record_ready_channel_8', 0x07)
        ## SOLO Ch. 1-8 (Switch + LED)
        self.register_control('solo_channel_1', 0x08)
        self.register_control('solo_channel_2', 0x09)
        self.register_control('solo_channel_3', 0x0A)
        self.register_control('solo_channel_4', 0x0B)
        self.register_control('solo_channel_5', 0x0C)
        self.register_control('solo_channel_6', 0x0D)
        self.register_control('solo_channel_7', 0x0E)
        self.register_control('solo_channel_8', 0x0F)
        ## MUTE Ch. 1-8 (Switch + LED)
        self.register_control('mute_channel_1', 0x10)
        self.register_control('mute_channel_2', 0x11)
        self.register_control('mute_channel_3', 0x12)
        self.register_control('mute_channel_4', 0x13)
        self.register_control('mute_channel_5', 0x14)
        self.register_control('mute_channel_6', 0x15)
        self.register_control('mute_channel_7', 0x16)
        self.register_control('mute_channel_8', 0x17)
        ## SELECT Ch. 1-8 (Switch + LED)
        self.register_control('select_channel_1', 0x18)
        self.register_control('select_channel_2', 0x19)
        self.register_control('select_channel_3', 0x1A)
        self.register_control('select_channel_4', 0x1B)
        self.register_control('select_channel_5', 0x1C)
        self.register_control('select_channel_6', 0x1D)
        self.register_control('select_channel_7', 0x1E)
        self.register_control('select_channel_8', 0x1F)
        ## V-Select Ch. 1-8 (Switch only)
        self.register_control('vselect_channel_1', 0x20)
        self.register_control('vselect_channel_2', 0x21)
        self.register_control('vselect_channel_3', 0x22)
        self.register_control('vselect_channel_4', 0x23)
        self.register_control('vselect_channel_5', 0x24)
        self.register_control('vselect_channel_6', 0x25)
        self.register_control('vselect_channel_7', 0x26)
        self.register_control('vselect_channel_8', 0x27)
        ## Assignments (Switch + LED)
        self.register_control('assignment_track', 0x28)
        self.register_control('assignment_send', 0x29)
        self.register_control('assignment_pan_surround', 0x2A)
        self.register_control('assignment_plug_in', 0x2B)
        self.register_control('assignment_eq', 0x2C)
        self.register_control('assignment_instrument', 0x2D)
        ## Fader banks (Switc only)
        self.register_control('fader_banks_bank_left', 0x2E)
        self.register_control('fader_banks_channel_left', 0x2F)
        self.register_control('fader_banks_channel_right', 0x30)
        self.register_control('fader_banks_bank_right', 0x31)
        ## Flip (Switch + LED)
        self.register_control('flip', 0x32)
        ## Global View (Switch + LED)
        self.register_control('global_view', 0x33)
        ## Name/Value (Switch only)
        self.register_control('name_value', 0x34)
        ## SMPTE/BEATS (Switch only)
        self.register_control('smpte_beats', 0x35)
        ## F1-F8 (Switch only)
        self.register_control('function_channel_1', 0x36)
        self.register_control('function_channel_2', 0x37)
        self.register_control('function_channel_3', 0x38)
        self.register_control('function_channel_4', 0x39)
        self.register_control('function_channel_5', 0x3A)
        self.register_control('function_channel_6', 0x3B)
        self.register_control('function_channel_7', 0x3C)
        self.register_control('function_channel_8', 0x3D)
        ## Global view: functions (Switch only)
        self.register_control('global_view_midi_tracks', 0x3E)
        self.register_control('global_view_inputs', 0x3F)
        self.register_control('global_view_audio_tracks', 0x40)
        self.register_control('global_view_audio_instruments', 0x41)
        self.register_control('global_view_aux', 0x42)
        self.register_control('global_view_busses', 0x43)
        self.register_control('global_view_outputs', 0x44)
        self.register_control('global_view_user', 0x45)
        ## Nav (Switch only)
        self.register_control('shift', 0x46)
        self.register_control('option', 0x47)
        self.register_control('control', 0x48)
        self.register_control('command_alt', 0x49)
        ## Automation (Switch + LED)
        self.register_control('automation_read_off', 0x4A)
        self.register_control('automation_write', 0x4B)
        self.register_control('automation_trim', 0xC)
        self.register_control('automation_touch', 0x4D)
        self.register_control('automation_latch', 0x4E)
        self.register_control('group', 0x4F)
        ## Utilities
        self.register_control('utilities_save', 0x50)  # Switch + LED
        self.register_control('utilities_undo', 0x51)  # Switch + LED
        self.register_control('utilities_cancel', 0x52)  # Switch only
        self.register_control('utilities_enter', 0x53)  # Switch only
        ## Edit (Switch + LED)
        self.register_control('marker', 0x54)
        self.register_control('nudge', 0x55)
        self.register_control('cycle', 0x56)
        self.register_control('drop', 0x57)
        self.register_control('replace', 0x58)
        self.register_control('click', 0x59)
        self.register_control('solo', 0x5A)
        ## Transport (Switch + LED)
        self.register_control('rewind', 0x5A)
        self.register_control('fast_forward', 0x5B)
        self.register_control('stop', 0x5C)
        self.register_control('play', 0x5D)
        self.register_control('cycle', 0x5E)
        self.register_control('record', 0x5F)
        ## Cursor (Switch only)
        self.register_control('cursor_left', 0x60)
        self.register_control('cursor_right', 0x61)
        self.register_control('cursor_down', 0x62)
        self.register_control('cursor_up', 0x63)
        ## Zoom (Switch + LED)
        self.register_control('zoom', 0x64)
        ## Scrub (Switch + LED)
        self.register_control('scrub', 0x65)
        ## User Switches A-B (Switch only)
        self.register_control('user_switch_1', 0x66)
        self.register_control('user_switch_2', 0x67)
        ## Fader Touch Ch. 1-8 (Switch only)
        self.register_control('fader_touch_1', 0x68)
        self.register_control('fader_touch_2', 0x69)
        self.register_control('fader_touch_3', 0x6A)
        self.register_control('fader_touch_4', 0x6B)
        self.register_control('fader_touch_5', 0x6C)
        self.register_control('fader_touch_6', 0x6D)
        self.register_control('fader_touch_7', 0x6E)
        self.register_control('fader_touch_8', 0x6F)
        self.register_control('fader_touch_master', 0x70)
        ## Status (LED only)
        self.register_control('smpte', 0x71)
        self.register_control('beats', 0x72)
        self.register_control('rude_solo', 0x73)
        self.register_control('relay_click', 0x76)

    def disconnect(self):
        self._log('Closing MIDI ports...')
        self.midi.disconnect()
        self._log('Disconnected.', True)

    def go_online(self):
        self._log('Mackie Host Control went online...', True)

    def go_offline(self):
        self._log('Mackie Host Control went offline...', True)

    # --- abilities of hardware controller ---
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

    # --- MIDI processing ---
    def process_midi_input(self):
        self.midi.process_input_buffer()

    def receive_midi(self, status, message):
        message_string = [f'status {status:02X}: ']
        for byte in message:
            message_string.append(f'{byte:02X}')
        self._log(' '.join(message_string))

    def send_midi_control_change(self, channel, cc_number, cc_value):
        self.midi.send_control_change(channel, cc_number, cc_value)

    def send_midi_sysex(self, data):
        assert isinstance(data, list)

        header = []
        header.extend(self.MIDI_MANUFACTURER_ID)
        header.extend(self.MIDI_DEVICE_ID)

        self.midi.send_sysex(header, data)

    @staticmethod
    def get_preferred_midi_input():
        return ''

    @staticmethod
    def get_preferred_midi_output():
        return ''

    # --- registration of MIDI controls ---
    def register_control(self, mcu_command, midi_switch, midi_led=None):
        if midi_led:
            self.interconnector.register_control(mcu_command, midi_switch, midi_led)
        else:
            self.interconnector.register_control(mcu_command, midi_switch, midi_switch)

    def withdraw_control(self, midi_switch):
        self.interconnector.withdraw_control(midi_switch)

    def withdraw_all_controls(self):
        self.interconnector.withdraw_all_controls()

    # --- handling of Mackie Control commands ---
    def set_lcd(self, position, hex_codes, update=True):
        for hex_code in hex_codes:
            # wrap display and determine position
            position %= 112
            (line, pos) = divmod(position, 56)

            # convert illegal characters to asterisk
            if (hex_code < 0x20) or (hex_code > 0x7F):
                self._lcd_characters[line][pos] = '*'
            else:
                self._lcd_characters[line][pos] = chr(hex_code)

            position += 1

        if update:
            self.update_lcd()

    def set_led(self, internal_id, led_status):
        self._log(f'LED #{internal_id} NOT set to {self._LED_STATUS[led_status]}.')

    def set_display_7seg(self, position, character_code):
        character = self._decode_7seg_character(character_code)
        position = 23 - (position * 2)

        self.display_7seg_characters[position - 1] = character[0]
        self.display_7seg_characters[position] = character[1]

        string_7seg = ''.join(self.display_7seg_characters)
        self._log(f'7 segment display NOT set to "{string_7seg}".')

    @staticmethod
    def _decode_7seg_character(character_code):
        if character_code >= 0x40:
            character_code = character_code - 0x40
            dot = '.'
        else:
            dot = ' '

        if character_code < 0x20:
            return chr(character_code + 0x40), dot

        return chr(character_code), dot

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
            self._log(f'timecode display NOT set to "{string_timecode}".')

    def set_peak_level(self, meter_id, meter_level):
        if meter_level == 0x0F:
            self._log(f'Meter #{meter_id:d} overload NOT cleared.')
        elif meter_level == 0x0F:
            self._log(f'Meter #{meter_id:d} NOT set to overload.')
        else:
            self._log(f'Meter #{meter_id:d} NOT set to {meter_level * 10:03d}%.')

    def fader_moved(self, fader_id, fader_position):
        self._log(f'Hardware fader #{fader_id:d} NOT moved to position {fader_position:04d}.')

    def set_vpot_led_ring(self, vpot_id, vpot_center_led, vpot_mode, vpot_position):
        self._log(f'V-Pot #{vpot_id:d} LED ring NOT set to position {vpot_position:02d} (mode {vpot_mode:d}).')

    def faders_to_minimum(self):
        self._log('Hardware faders NOT set to minimum.')

    def all_leds_off(self):
        self._log('Hardware LEDs NOT set to "off".')

    # --- LCD and menu handling
    def update_lcd(self):
        display = ['', '']
        for line in range(2):
            display[line].join(self.get_lcd_characters(line))
        self._log(f"Display NOT set to\n'{display[0]}'\n'{display[1]}'")

    def get_lcd_characters(self, line):
        line %= 2

        if self._show_overlay[line]:
            return self._lcd_overlay_characters[line]

        return self._lcd_characters[line]

    def show_menu(self, line, menu_strings):
        assert len(menu_strings) == 8

        menu_string_temp = ''
        for menu_string in menu_strings:
            menu_string_temp += menu_string.center(7)[:7]

        menu_characters = list(menu_string_temp)
        self.show_overlay(line, menu_characters)

    def hide_menu(self, line):
        self.hide_overlay(line)

    def show_overlay(self, line, overlay_characters):
        line %= 2
        assert len(overlay_characters) == 56

        self._show_overlay[line] = True
        self._lcd_overlay_characters[line] = overlay_characters
        self.update_lcd()

    def hide_overlay(self, line):
        line %= 2

        self._show_overlay[line] = False
        self.update_lcd()
