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

if __name__ == "__main__":
    # allow "PythonMcu" package imports when executing this module
    sys.path.append('../../../')

from PythonMcu.Hardware.MidiControllerTemplate import MidiControllerTemplate
from PythonMcu.Midi.MidiConnection import MidiConnection


class ZeroSlMk2(MidiControllerTemplate):
    # Novation Digital Music System
    MIDI_MANUFACTURER_ID = [0x00, 0x20, 0x29]

    # MIDI device ID and initialisation of Novation ZeRO SL Mkii
    MIDI_DEVICE_ID = [0x03, 0x03, 0x12, 0x00, 0x04, 0x00]

    # MIDI channel of controller
    _MIDI_DEVICE_CHANNEL = 0

    _MIDI_CC_CLEAR_ALL_LEDS = 0x4E
    _MIDI_CC_ENCODER_LIGHTS = 0x70
    _MIDI_CC_ENCODER_MODE = 0x78
    _MIDI_CC_CONTROLLER_ROW_LIGHTS_LEFT = (0x51, 0x53, 0x54, 0x50, 0x52)
    _MIDI_CC_CONTROLLER_ROW_LIGHTS_RIGHT = (0x55, 0x56, 0x57)

    _MIDI_CC_BUTTONS_LEFT_TOP = 0x18
    _MIDI_CC_BUTTONS_LEFT_BOTTOM = 0x20
    _MIDI_CC_BUTTONS_RIGHT_TOP = 0x28
    _MIDI_CC_BUTTONS_RIGHT_BOTTOM = 0x30

    _MIDI_CC_FADERS = 0x10
    _MIDI_CC_ENCODERS = 0x38
    _MIDI_CC_KNOBS = 0x08

    _MIDI_CC_BUTTON_BANK_UP = 0x58
    _MIDI_CC_BUTTON_BANK_DOWN = 0x59
    _MIDI_CC_BUTTON_REWIND = 0x48
    _MIDI_CC_BUTTON_FAST_FORWARD = 0x49
    _MIDI_CC_BUTTON_STOP = 0x4A
    _MIDI_CC_BUTTON_PLAY = 0x4B
    _MIDI_CC_BUTTON_RECORD = 0x4C
    _MIDI_CC_BUTTON_CYCLE = 0x4D
    _MIDI_CC_BUTTON_MODE_TRANSPORT = 0x4F

    _MIDI_CC_LED_AUTOMAP_LEARN = 0x48
    _MIDI_CC_LED_AUTOMAP_VIEW = 0x49
    _MIDI_CC_LED_AUTOMAP_USER = 0x4A
    _MIDI_CC_LED_AUTOMAP_FX = 0x4B
    _MIDI_CC_LED_AUTOMAP_MIXER = 0x4D

    _MODE_TRACK_OFF = 0
    _MODE_TRACK_MUTE_SOLO = 1
    _MODE_TRACK_RECORD_READY_FUNCTION = 2

    _MODE_EDIT_OFF = 0
    _MODE_EDIT_VSELECT_ASSIGNMENT = 1
    _MODE_EDIT_VSELECT_SELECT = 2

    _MODE_OTHER_OFF = 0
    _MODE_OTHER_TRANSPORT = 1
    _MODE_OTHER_BANK = 2
    _MODE_OTHER_GLOBAL_VIEW = 3
    _MODE_OTHER_AUTOMATION = 4
    _MODE_OTHER_UTILITY = 5


    def __init__(self, midi_input, midi_output):
        MidiControllerTemplate.__init__(self, midi_input, midi_output)

        self.display_lcd_available = True
        self.automated_faders_available = False
        self.display_7seg_available = False
        self.display_timecode_available = False
        self.meter_bridge_available = False

        self._lcd_strings = ['', '']
        self._menu_string = ''

        self._vpot_modes = \
            [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        self._vpot_positions = \
            [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        self._mode_track = self._MODE_TRACK_MUTE_SOLO
        self._mode_edit = self._MODE_EDIT_OFF
        self._mode_other = self._MODE_OTHER_OFF
        self._mode_automap = False


    def connect(self):
        MidiControllerTemplate.connect(self)
        self._is_connected = True

        self._set_lcd(1, 'Novation Zero SL MkII:  initialising...')
        self._set_lcd(2, 'Mackie Host Control:    connecting...')

        self.enter_ableton_mode()

        self.link_control( \
            'shift', self._MIDI_CC_BUTTONS_RIGHT_TOP)
        self.link_control( \
            'control', self._MIDI_CC_BUTTONS_RIGHT_TOP + 1)
        self.link_control( \
            'command', self._MIDI_CC_BUTTONS_RIGHT_TOP + 2)
        self.link_control( \
            'option', self._MIDI_CC_BUTTONS_RIGHT_TOP + 3)
        self.link_control( \
            'cursor_left', self._MIDI_CC_BUTTONS_RIGHT_TOP + 4)
        self.link_control( \
            'cursor_right', self._MIDI_CC_BUTTONS_RIGHT_TOP + 5)
        self.link_control( \
            'cursor_down', self._MIDI_CC_BUTTONS_RIGHT_TOP + 6)
        self.link_control( \
            'cursor_up', self._MIDI_CC_BUTTONS_RIGHT_TOP + 7)

        self.link_control( \
            'name_value', self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 4)
        self.link_control( \
            'flip', self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 5)
        self.link_control( \
            'scrub', self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 6)
        self.link_control( \
            'zoom', self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 7)


        # select "track" mode ("Mute" + "Solo")
        self.change_mode_track(2)

        self._set_lcd(1, 'Novation Zero SL MkII:  initialised.')

        self._log('Connected.')


    def disconnect(self):
        self._log('Disconnecting...')

        self.unlink_all_controls()

        self._set_lcd(1, 'Novation Zero SL MkII:  disconnecting...')
        self._set_lcd(2, '')

        self.leave_ableton_mode()

        self._is_connected = False
        MidiControllerTemplate.disconnect(self)


    def host_connected(self):
        self._set_lcd(2, 'Mackie Host Control:    connected.')


    def link_control(self, mcu_command, midi_control):
        midi_control_change = 'cc%d' % midi_control

        self.interconnector.link_control( \
            mcu_command, midi_control_change)


    def unlink_control(self, mcu_command, midi_control):
        midi_control_change = 'cc%d' % midi_control

        self.interconnector.unlink_control( \
            mcu_command, midi_control_change)


    def unlink_all_controls(self):
        self.interconnector.unlink_all_controls()


    def leave_ableton_mode(self):
        self._log('Leaving "Ableton" mode...')

        # clear all LEDs and switch off "transport" mode
        self.send_midi_control_change(self._MIDI_CC_CLEAR_ALL_LEDS, 0x00)
        self.send_midi_control_change(self._MIDI_CC_BUTTON_MODE_TRANSPORT, 0x00)

        # update special LEDs (do NOT use "set_led_xxx" functions
        # here, otherwise the original status is lost on leaving
        # "Automap" mode!

        # self._set_led( \
        #     self._MIDI_CC_LED_AUTOMAP_LEARN, self._led_status['RELAY_CLICK'])
        # self._set_led( \
        #     self._MIDI_CC_LED_AUTOMAP_VIEW, self._led_status['RUDE_SOLO'])
        # self._set_led( \
        #     self._MIDI_CC_LED_AUTOMAP_USER, self._led_status['BEATS'])
        # self._set_led( \
        #     self._MIDI_CC_LED_AUTOMAP_FX, self._led_status['SMPTE'])

        self.send_midi_sysex([0x02, 0x02, 0x05])
        self.send_midi_sysex([0x01, 0x00])


    def enter_ableton_mode(self):
        self._log('Entering "Ableton" mode...')

        self.send_midi_sysex([0x01, 0x01])

        # clear all LEDs and switch off "transport" mode
        self.send_midi_control_change(self._MIDI_CC_CLEAR_ALL_LEDS, 0x00)
        self.send_midi_control_change(self._MIDI_CC_BUTTON_MODE_TRANSPORT, 0x00)

        # update special LEDs (do NOT use "set_led_xxx" functions
        # here, otherwise the original status is lost on leaving
        # "Automap" mode!

        # self._set_led( \
        #     self._MIDI_CC_LED_AUTOMAP_LEARN, self._led_status['RELAY_CLICK'])
        # self._set_led( \
        #     self._MIDI_CC_LED_AUTOMAP_VIEW, self._led_status['RUDE_SOLO'])
        # self._set_led( \
        #     self._MIDI_CC_LED_AUTOMAP_USER, self._led_status['BEATS'])
        # self._set_led( \
        #     self._MIDI_CC_LED_AUTOMAP_FX, self._led_status['SMPTE'])


    def _log(self, message):
        print '[Novation ZeRO SL MkII]  ' + message


    def send_midi_control_change(self, cc_number, cc_value):
        if not self._is_connected:
            return

        MidiControllerTemplate.send_midi_control_change( \
            self, self._MIDI_DEVICE_CHANNEL, cc_number, cc_value)


    def receive_midi(self, status, message):
        if (message[0] == 0xF0) and (message[-1] == 0xF7):
            if (message[1:4] == self.MIDI_MANUFACTURER_ID) and \
                    (message[4:10] == self.MIDI_DEVICE_ID):
                sysex_message = message[10:-1]

                if sysex_message == [1, 0]:
                    self.leave_ableton_mode()

                    self._mode_automap = True
                    self._is_connected = False
                elif sysex_message == [1, 1]:
                    if self._mode_automap:
                        self._mode_automap = False
                        self._is_connected = True

                        self.enter_ableton_mode()

                        self._restore_previous_mode()
                        # self._restore_leds()
                        self._restore_vpots()

                        self._set_lcd(1, self._lcd_strings[0])
                        self._set_lcd(2, self._lcd_strings[1])

            # all MIDI SysEx messages handled (including invalid
            # ones), so quit processing here
            return

        if not self._is_connected:
            return

        cc_selector = {
            self._MIDI_CC_FADERS: \
                'self.interconnector.move_fader_7bit(0, %d)',
            self._MIDI_CC_FADERS + 1: \
                'self.interconnector.move_fader_7bit(1, %d)',
            self._MIDI_CC_FADERS + 2: \
                'self.interconnector.move_fader_7bit(2, %d)',
            self._MIDI_CC_FADERS + 3: \
                'self.interconnector.move_fader_7bit(3, %d)',
            self._MIDI_CC_FADERS + 4: \
                'self.interconnector.move_fader_7bit(4, %d)',
            self._MIDI_CC_FADERS + 5: \
                'self.interconnector.move_fader_7bit(5, %d)',
            self._MIDI_CC_FADERS + 6: \
                'self.interconnector.move_fader_7bit(6, %d)',
            self._MIDI_CC_FADERS + 7: \
                'self.interconnector.move_fader_7bit(7, %d)',
            self._MIDI_CC_ENCODERS:
                'self.interconnector.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 0, %d)',
            self._MIDI_CC_ENCODERS + 1:
                'self.interconnector.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 1, %d)',
            self._MIDI_CC_ENCODERS + 2:
                'self.interconnector.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 2, %d)',
            self._MIDI_CC_ENCODERS + 3:
                'self.interconnector.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 3, %d)',
            self._MIDI_CC_ENCODERS + 4:
                'self.interconnector.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 4, %d)',
            self._MIDI_CC_ENCODERS + 5:
                'self.interconnector.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 5, %d)',
            self._MIDI_CC_ENCODERS + 6:
                'self.interconnector.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 6, %d)',
            self._MIDI_CC_ENCODERS + 7:
                'self.interconnector.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 7, %d)',
            self._MIDI_CC_BUTTON_BANK_UP:
                'self.change_mode_edit(%d & 0x01)',
            self._MIDI_CC_BUTTON_BANK_DOWN:
                'self.change_mode_track(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM:
                'self.change_mode_bank(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1:
                'self.change_mode_global_view(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2:
                'self.change_mode_automation(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3:
                'self.change_mode_utility(%d & 0x01)',
            self._MIDI_CC_BUTTON_MODE_TRANSPORT:
                'self._keypress_mode_transport(%d & 0x01)',
            }

        if status == (MidiConnection.CONTROL_CHANGE + \
                          self._MIDI_DEVICE_CHANNEL):
            cc_number = message[1]
            cc_value = message[2]

            if cc_number in cc_selector:
                eval(cc_selector[cc_number] % cc_value)
            elif cc_number == 0x6B:
                # this controller change message is sent on entering
                # and leaving "Automap" mode and can be ignored
                pass
            else:
                internal_id = 'cc%d' % cc_number
                status = cc_value & 0x01
                key_processed = self.interconnector.keypress( \
                    internal_id, status)

                if not key_processed:
                    message_string = ['status %02X: ' % status]
                    for byte in message:
                        message_string.append('%02X' % byte)
                    self._log(' '.join(message_string))
        else:
            message_string = ['status %02X: ' % status]
            for byte in message:
                message_string.append('%02X' % byte)
            self._log(' '.join(message_string))


    def _keypress_mode_transport(self, status):
        if status > 0:
            self._mode_other = self._MODE_OTHER_TRANSPORT

            menu_strings = \
                ('Click', 'Solo', 'Marker', 'Nudge', \
                 'SMPTE/Bt', '', 'Drop', 'Replace')
            self._set_menu_string(menu_strings)

            # self._set_led( \
            #     self._MIDI_CC_BUTTONS_RIGHT_BOTTOM, self._led_status['REWIND'])
            # self._set_led( \
            #     self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1, self._led_status['FAST_FORWARD'])
            # self._set_led( \
            #     self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2, self._led_status['STOP'])
            # self._set_led( \
            #     self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3, self._led_status['PLAY'])
            # self._set_led( \
            #     self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 4, self._led_status['CYCLE'])
            # self._set_led( \
            #     self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 5, self._led_status['RECORD'])
        else:
            self._mode_other = self._MODE_OTHER_OFF

            self._clear_menu_string()

            self._set_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM, 0)
            self._set_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1, 0)
            self._set_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2, 0)
            self._set_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3, 0)
            self._set_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 4, 0)
            self._set_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 5, 0)


    def set_display_7seg(self, position, character_code):
        MidiControllerTemplate.set_display_7seg(self, position, character_code)


    def _clear_menu_string(self):
        self._menu_string = ''
        self._set_lcd(4, '')


    def _set_menu_string(self, menu_strings):
        assert(len(menu_strings) == 8)

        self._clear_menu_string()
        for menu_string in menu_strings:
            self._menu_string += menu_string.center(9)

        self._set_lcd(3, self._menu_string)


    def _set_lcd_raw(self, position, hex_codes):
        """
        send hex codes of maximum 72 bytes to controller LCD

        position 1: top row
        position 2: bottom row
        """
        if not self._is_connected:
            return

        if position == 2:
            position = 3
        sysex_data = [0x02, 0x01, 0x00, position, 0x04]

        # convert string
        for hex_code in hex_codes:
            # convert illegal characters to asterisk
            if (hex_code < 0x20) or (hex_code > 0x7F):
                hex_code = 0x2A
            sysex_data.append(hex_code)

        self.send_midi_sysex(sysex_data)

        # update second display page as well:
        # * position 1  -->  top row (left controller block)
        # * position 2  -->  top row (right controller block)
        # * position 3  -->  bottom row (left controller block)
        # * position 4  -->  bottom row (right controller block)
        sysex_data[3] += 1

        self.send_midi_sysex(sysex_data)


    def set_lcd(self, position, new_string):
        """
        send string of maximum 56 bytes to controller LCD

        position 1: top row
        position 2: bottom row
        """
        converted_string = ' '
        for n in range(len(new_string)):
            converted_string += new_string[n]
            if (n%7) == 6:
                converted_string += '  '

        has_changed = False
        converted_string = converted_string.ljust(72)

        if self._lcd_strings[position - 1] != converted_string:
            self._lcd_strings[position - 1] = converted_string
            has_changed = True

        # no need to update, so exit now
        if not has_changed:
            return
        # menu is shown, so update strings silently and exit
        elif (position == 2) and self._menu_string:
            return
        # update display
        else:
            self._set_lcd(position, converted_string)


    def _set_lcd(self, position, new_string):
        """
        send string of maximum 72 bytes to controller LCD

        position 1: top row
        position 2: bottom row
        position 3: display menu (bottom row)
        position 4: clear menu (bottom row)
        """
        if position == 3:
            position = 2
        elif position == 4:
            position = 2
            new_string = self._lcd_strings[1]
        else:
            new_string = new_string.ljust(72)

        # convert string
        hex_codes = []
        for character in new_string:
            hex_codes.append(ord(character))

        self._set_lcd_raw(position, hex_codes)


    def change_mode_track(self, status):
        self._mode_edit = self._MODE_EDIT_OFF
        self._mode_other = self._MODE_OTHER_OFF

        if status == 1:
            self._mode_track = self._MODE_TRACK_RECORD_READY_FUNCTION

            self.link_control( \
                'record_ready_channel_1', self._MIDI_CC_BUTTONS_LEFT_TOP)
            self.link_control( \
                'record_ready_channel_2', self._MIDI_CC_BUTTONS_LEFT_TOP + 1)
            self.link_control( \
                'record_ready_channel_3', self._MIDI_CC_BUTTONS_LEFT_TOP + 2)
            self.link_control( \
                'record_ready_channel_4', self._MIDI_CC_BUTTONS_LEFT_TOP + 3)
            self.link_control( \
                'record_ready_channel_5', self._MIDI_CC_BUTTONS_LEFT_TOP + 4)
            self.link_control( \
                'record_ready_channel_6', self._MIDI_CC_BUTTONS_LEFT_TOP + 5)
            self.link_control( \
                'record_ready_channel_7', self._MIDI_CC_BUTTONS_LEFT_TOP + 6)
            self.link_control( \
                'record_ready_channel_8', self._MIDI_CC_BUTTONS_LEFT_TOP + 7)

            self.link_control( \
                'function_channel_1', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.link_control( \
                'function_channel_2', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.link_control( \
                'function_channel_3', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.link_control( \
                'function_channel_4', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.link_control( \
                'function_channel_5', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.link_control( \
                'function_channel_6', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.link_control( \
                'function_channel_7', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.link_control( \
                'function_channel_8', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)
        else:
            self._mode_track = self._MODE_TRACK_MUTE_SOLO

            self.link_control( \
                'mute_channel_1', self._MIDI_CC_BUTTONS_LEFT_TOP)
            self.link_control( \
                'mute_channel_2', self._MIDI_CC_BUTTONS_LEFT_TOP + 1)
            self.link_control( \
                'mute_channel_3', self._MIDI_CC_BUTTONS_LEFT_TOP + 2)
            self.link_control( \
                'mute_channel_4', self._MIDI_CC_BUTTONS_LEFT_TOP + 3)
            self.link_control( \
                'mute_channel_5', self._MIDI_CC_BUTTONS_LEFT_TOP + 4)
            self.link_control( \
                'mute_channel_6', self._MIDI_CC_BUTTONS_LEFT_TOP + 5)
            self.link_control( \
                'mute_channel_7', self._MIDI_CC_BUTTONS_LEFT_TOP + 6)
            self.link_control( \
                'mute_channel_8', self._MIDI_CC_BUTTONS_LEFT_TOP + 7)

            self.link_control( \
                'solo_channel_1', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.link_control( \
                'solo_channel_2', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.link_control( \
                'solo_channel_3', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.link_control( \
                'solo_channel_4', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.link_control( \
                'solo_channel_5', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.link_control( \
                'solo_channel_6', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.link_control( \
                'solo_channel_7', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.link_control( \
                'solo_channel_8', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)

        self._set_led(self._MIDI_CC_BUTTON_BANK_DOWN, self._mode_track)
        self._set_led(self._MIDI_CC_BUTTON_BANK_UP, self._mode_edit)

        # self._update_leds_top_row()
        # self._update_leds_bottom_row()


    def change_mode_edit(self, status):
        self._mode_track = self._MODE_TRACK_OFF
        self._mode_other = self._MODE_OTHER_OFF

        if status == 1:
            self._mode_edit = self._MODE_EDIT_VSELECT_SELECT

            self.link_control( \
                'vselect_channel_1', self._MIDI_CC_BUTTONS_LEFT_TOP)
            self.link_control( \
                'vselect_channel_2', self._MIDI_CC_BUTTONS_LEFT_TOP + 1)
            self.link_control( \
                'vselect_channel_3', self._MIDI_CC_BUTTONS_LEFT_TOP + 2)
            self.link_control( \
                'vselect_channel_4', self._MIDI_CC_BUTTONS_LEFT_TOP + 3)
            self.link_control( \
                'vselect_channel_5', self._MIDI_CC_BUTTONS_LEFT_TOP + 4)
            self.link_control( \
                'vselect_channel_6', self._MIDI_CC_BUTTONS_LEFT_TOP + 5)
            self.link_control( \
                'vselect_channel_7', self._MIDI_CC_BUTTONS_LEFT_TOP + 6)
            self.link_control( \
                'vselect_channel_8', self._MIDI_CC_BUTTONS_LEFT_TOP + 7)

            self.link_control( \
                'select_channel_1', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.link_control( \
                'select_channel_2', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.link_control( \
                'select_channel_3', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.link_control( \
                'select_channel_4', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.link_control( \
                'select_channel_5', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.link_control( \
                'select_channel_6', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.link_control( \
                'select_channel_7', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.link_control( \
                'select_channel_8', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)
        else:
            self._mode_edit = self._MODE_EDIT_VSELECT_ASSIGNMENT

            self.link_control( \
                'vselect_channel_1', self._MIDI_CC_BUTTONS_LEFT_TOP)
            self.link_control( \
                'vselect_channel_2', self._MIDI_CC_BUTTONS_LEFT_TOP + 1)
            self.link_control( \
                'vselect_channel_3', self._MIDI_CC_BUTTONS_LEFT_TOP + 2)
            self.link_control( \
                'vselect_channel_4', self._MIDI_CC_BUTTONS_LEFT_TOP + 3)
            self.link_control( \
                'vselect_channel_5', self._MIDI_CC_BUTTONS_LEFT_TOP + 4)
            self.link_control( \
                'vselect_channel_6', self._MIDI_CC_BUTTONS_LEFT_TOP + 5)
            self.link_control( \
                'vselect_channel_7', self._MIDI_CC_BUTTONS_LEFT_TOP + 6)
            self.link_control( \
                'vselect_channel_8', self._MIDI_CC_BUTTONS_LEFT_TOP + 7)

            self.link_control( \
                'select_channel_1', self._MIDI_CC_BUTTONS_LEFT_BOTTOM)
            self.link_control( \
                'select_channel_2', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1)
            self.link_control( \
                'select_channel_3', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2)
            self.link_control( \
                'select_channel_4', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3)
            self.link_control( \
                'select_channel_5', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4)
            self.link_control( \
                'select_channel_6', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5)
            self.link_control( \
                'select_channel_7', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6)
            self.link_control( \
                'select_channel_8', self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7)

        self._set_led(self._MIDI_CC_BUTTON_BANK_DOWN, self._mode_track)
        self._set_led(self._MIDI_CC_BUTTON_BANK_UP, self._mode_edit)

        # self._update_leds_top_row()
        # self._update_leds_bottom_row()


    def _restore_previous_mode(self):
        if self._mode_track:
            if self._mode_track == self._MODE_TRACK_RECORD_READY_FUNCTION:
                self.change_mode_track(1)
            else:
                self.change_mode_track(2)
        else:
            if self._mode_edit == self._MODE_EDIT_VSELECT_SELECT:
                self.change_mode_edit(1)
            else:
                self.change_mode_edit(2)


    # def _restore_leds(self):
    #     self.set_led_flip(self._led_status['FLIP'])
    #     self.set_led_scrub(self._led_status['SCRUB'])
    #     self.set_led_zoom(self._led_status['ZOOM'])
    #
    #     self.set_led_relay_click(self._led_status['RELAY_CLICK'])
    #     self.set_led_rude_solo(self._led_status['RUDE_SOLO'])
    #     self.set_led_beats(self._led_status['BEATS'])
    #     self.set_led_smpte(self._led_status['SMPTE'])


    def _restore_vpots(self):
        for id in range(8):
            self._set_led( \
                self._MIDI_CC_ENCODER_MODE + id, self._vpot_modes[id])
            self._set_led( \
                self._MIDI_CC_ENCODER_LIGHTS + id, self._vpot_positions[id])


    def change_mode_bank(self, status):
        # leave other modes as is in order to return to the old one!

        if status == 1:
            self._mode_other = self._MODE_OTHER_BANK
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM, 1)

            menu_strings = \
                ('<<', '<', '>', '>>', \
                 '', '', '', '')
            self._set_menu_string(menu_strings)

            # self._update_leds_bottom_row()
        else:
            self._mode_other = self._MODE_OTHER_OFF
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM, 0)

            self._clear_menu_string()
            self._restore_previous_mode()


    def change_mode_global_view(self, status):
        # leave other modes as is in order to return to the old one!

        if status == 1:
            self._mode_other = self._MODE_OTHER_GLOBAL_VIEW
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1, 1)

            menu_strings = \
                ('MIDI', 'Inputs', 'AudioTr.', 'Instrum.', \
                 'AUX', 'Busses', 'Outputs', 'User')
            self._set_menu_string(menu_strings)

            # self._update_leds_bottom_row()
        else:
            self._mode_other = self._MODE_OTHER_OFF
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1, 0)

            self._clear_menu_string()
            self._restore_previous_mode()


    def change_mode_automation(self, status):
        # leave other modes as is in order to return to the old one!

        if status == 1:
            self._mode_other = self._MODE_OTHER_AUTOMATION
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2, 1)

            menu_strings = \
                ('Read/Off', 'Write', 'Trim', 'Touch', \
                 'Latch', '', '', 'Group')
            self._set_menu_string(menu_strings)

            # self._update_leds_bottom_row()
        else:
            self._mode_other = self._MODE_OTHER_OFF
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2, 0)

            self._clear_menu_string()
            self._restore_previous_mode()


    def change_mode_utility(self, status):
        # leave other modes as is in order to return to the old one!

        if status == 1:
            self._mode_other = self._MODE_OTHER_UTILITY
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3, 1)

            menu_strings = \
                ('Enter', 'Cancel', '', 'Undo', \
                 '', '', '', 'Save')
            self._set_menu_string(menu_strings)

            # self._update_leds_bottom_row()
        else:
            self._mode_other = self._MODE_OTHER_OFF
            self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3, 0)

            self._clear_menu_string()
            self._restore_previous_mode()


    def set_vpot_led_ring(self, id, center_led, mode, position):
        if mode == self.VPOT_MODE_WRAP:
            vpot_mode = 0x00
        elif mode == self.VPOT_MODE_BOOST_CUT:
            vpot_mode = 0x20
        elif mode == self.VPOT_MODE_SPREAD:
            vpot_mode = 0x30
        elif mode == self.VPOT_MODE_SINGLE_DOT:
            vpot_mode = 0x40

        self._vpot_modes[id] = vpot_mode
        self._vpot_positions[id] = position

        self._set_led(self._MIDI_CC_ENCODER_MODE + id, vpot_mode)
        self._set_led(self._MIDI_CC_ENCODER_LIGHTS + id, position)


    def _set_led(self, led_id, led_status):
        if not self._is_connected:
            return

        MidiControllerTemplate.send_midi_control_change( \
            self, self._MIDI_DEVICE_CHANNEL, led_id, led_status)


    def set_led(self, internal_id, led_status):
        if not self._is_connected:
            return

        controller_type = internal_id[:2]
        controller_id = int(internal_id[2:])

        if controller_type == 'cc':
            MidiControllerTemplate.send_midi_control_change( \
                self, self._MIDI_DEVICE_CHANNEL, controller_id, led_status)


    # def _keypress_top_row(self, channel, status):
    #     if self._mode_track:
    #         if self._mode_track == self._MODE_TRACK_MUTE_SOLO:
    #             self.interconnector.keypress_channel_mute(channel, status)
    #         else:
    #             self.interconnector.keypress_channel_record_ready(channel, status)
    #     else:
    #         self.interconnector.keypress_channel_vselect(channel, status)


    # def _keypress_bottom_row(self, channel, status):
    #     if self._mode_other:
    #         if self._mode_other == self._MODE_OTHER_BANK:
    #             if channel == 0:
    #                 self.interconnector.keypress_fader_banks_bank_left( \
    #                     status)
    #             elif channel == 1:
    #                 self.interconnector.keypress_fader_banks_channel_left( \
    #                     status)
    #             elif channel == 2:
    #                 self.interconnector.keypress_fader_banks_channel_right( \
    #                     status)
    #             elif channel == 3:
    #                 self.interconnector.keypress_fader_banks_bank_right( \
    #                     status)
    #     elif self._mode_track:
    #         if self._mode_track == self._MODE_TRACK_MUTE_SOLO:
    #             self.interconnector.keypress_channel_solo(channel, status)
    #         else:
    #             self.interconnector.keypress_channel_function(channel, status)
    #     elif self._mode_edit:
    #         if self._mode_edit == self._MODE_EDIT_VSELECT_ASSIGNMENT:
    #             if channel == 0:
    #                 self.interconnector.keypress_assignment_track(status)
    #             elif channel == 1:
    #                 self.interconnector.keypress_assignment_send(status)
    #             elif channel == 2:
    #                 self.interconnector.keypress_assignment_pan_surround( \
    #                     status)
    #             elif channel == 3:
    #                 self.interconnector.keypress_assignment_eq(status)
    #             elif channel == 4:
    #                 self.interconnector.keypress_assignment_plug_in(status)
    #             elif channel == 5:
    #                 self.interconnector.keypress_assignment_instrument( \
    #                     status)
    #             elif channel == 6:
    #                 self.interconnector.keypress_user_switch(0, status)
    #             elif channel == 7:
    #                 self.interconnector.keypress_user_switch(1, status)
    #         else:
    #             self.interconnector.keypress_channel_select(channel, status)


    # def keypress_name_value(self, status):
    #     self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 4, status)
    #     self.interconnector.keypress_name_value(status)


    # def _update_leds_top_row(self, channel=-1):
    #     if not self._is_connected:
    #         return
    #
    #     if self._mode_track:
    #         if self._mode_track == self._MODE_TRACK_MUTE_SOLO:
    #             if channel >= 0:
    #                 self._set_led( \
    #                     self._MIDI_CC_BUTTONS_LEFT_TOP + channel, \
    #                         self._led_status['CHANNEL_MUTE_%d' % channel])
    #             else:
    #                 if channel >= 0:
    #                     self._set_led( \
    #                         self._MIDI_CC_BUTTONS_LEFT_TOP + channel, \
    #                             self._led_status['CHANNEL_MUTE_%d' % channel])
    #                 else:
    #                     for channel in range(8):
    #                         self._set_led( \
    #                             self._MIDI_CC_BUTTONS_LEFT_TOP + channel, \
    #                                 self._led_status['CHANNEL_MUTE_%d' % \
    #                                                      channel])
    #         else:
    #             if channel >= 0:
    #                 self._set_led( \
    #                     self._MIDI_CC_BUTTONS_LEFT_TOP + channel, \
    #                         self._led_status['CHANNEL_RECORD_READY_%d' % \
    #                                              channel])
    #             else:
    #                 for channel in range(8):
    #                     self._set_led( \
    #                         self._MIDI_CC_BUTTONS_LEFT_TOP + channel, \
    #                             self._led_status['CHANNEL_RECORD_READY_%d' % \
    #                                                  channel])
    #     else:
    #         # CHANNEL_VSELECT
    #         if channel >= 0:
    #             self._set_led( \
    #                 self._MIDI_CC_BUTTONS_LEFT_TOP + channel, 0)
    #         else:
    #             for channel in range(8):
    #                 self._set_led( \
    #                     self._MIDI_CC_BUTTONS_LEFT_TOP + channel, 0)


    # def _update_leds_bottom_row(self, channel=-1):
    #     if not self._is_connected:
    #         return
    #
    #     if self._mode_other:
    #         if self._mode_other == self._MODE_OTHER_BANK:
    #             for channel in range(8):
    #                 self._set_led( \
    #                     self._MIDI_CC_BUTTONS_LEFT_BOTTOM + channel, 0)
    #     elif self._mode_track:
    #         if self._mode_track == self._MODE_TRACK_MUTE_SOLO:
    #             if channel >= 0:
    #                 self._set_led( \
    #                     self._MIDI_CC_BUTTONS_LEFT_BOTTOM + channel, \
    #                         self._led_status['CHANNEL_SOLO_%d' % channel])
    #             else:
    #                 for channel in range(8):
    #                     self._set_led( \
    #                         self._MIDI_CC_BUTTONS_LEFT_BOTTOM + channel, \
    #                             self._led_status['CHANNEL_SOLO_%d' % channel])
    #         else:
    #             # CHANNEL_FUNCTION
    #             if channel >= 0:
    #                 self._set_led( \
    #                     self._MIDI_CC_BUTTONS_LEFT_BOTTOM + channel, 0)
    #             else:
    #                 for channel in range(8):
    #                     self._set_led( \
    #                         self._MIDI_CC_BUTTONS_LEFT_BOTTOM + channel, 0)
    #     elif self._mode_edit:
    #         if self._mode_edit == self._MODE_EDIT_VSELECT_ASSIGNMENT:
    #             self._set_led( \
    #                 self._MIDI_CC_BUTTONS_LEFT_BOTTOM, \
    #                     self._led_status['ASSIGNMENT_TRACK'])
    #             self._set_led( \
    #                 self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1, \
    #                     self._led_status['ASSIGNMENT_SEND'])
    #             self._set_led( \
    #                 self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2, \
    #                     self._led_status['ASSIGNMENT_PAN_SURROUND'])
    #             self._set_led( \
    #                 self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3, \
    #                     self._led_status['ASSIGNMENT_EQ'])
    #             self._set_led( \
    #                 self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4, \
    #                     self._led_status['ASSIGNMENT_PLUG_IN'])
    #             self._set_led( \
    #                 self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5, \
    #                     self._led_status['ASSIGNMENT_INSTRUMENT'])
    #             self._set_led(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6, 0)
    #             self._set_led(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7, 0)
    #         else:
    #             if channel >= 0:
    #                 self._set_led( \
    #                     self._MIDI_CC_BUTTONS_LEFT_BOTTOM + channel, \
    #                         self._led_status['CHANNEL_SELECT_%d' % channel])
    #             else:
    #                 for channel in range(8):
    #                     self._set_led( \
    #                         self._MIDI_CC_BUTTONS_LEFT_BOTTOM + channel, \
    #                             self._led_status['CHANNEL_SELECT_%d' % channel])


    # def set_led_flip(self, status):
    #     self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 5, status)


    # def set_led_scrub(self, status):
    #     self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 6, status)


    # def set_led_zoom(self, status):
    #     self._set_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 7, status)


    # def set_led_cycle(self, status):
    #     if self._mode_other == self._MODE_OTHER_TRANSPORT:
    #         self._keypress_mode_transport(1)


    # def set_led_rewind(self, status):
    #     if self._mode_other == self._MODE_OTHER_TRANSPORT:
    #         self._keypress_mode_transport(1)


    # def set_led_fast_forward(self, status):
    #     if self._mode_other == self._MODE_OTHER_TRANSPORT:
    #         self._keypress_mode_transport(1)


    # def set_led_stop(self, status):
    #     if self._mode_other == self._MODE_OTHER_TRANSPORT:
    #         self._keypress_mode_transport(1)


    # def set_led_play(self, status):
    #     if self._mode_other == self._MODE_OTHER_TRANSPORT:
    #         self._keypress_mode_transport(1)


    # def set_led_record(self, status):
    #     if self._mode_other == self._MODE_OTHER_TRANSPORT:
    #         self._keypress_mode_transport(1)


    # def set_led_relay_click(self, status):
    #     self._set_led(self._MIDI_CC_LED_AUTOMAP_LEARN, status)


    # def set_led_rude_solo(self, status):
    #     self._set_led(self._MIDI_CC_LED_AUTOMAP_VIEW, status)


    # def set_led_beats(self, status):
    #     self._set_led(self._MIDI_CC_LED_AUTOMAP_USER, status)


    # def set_led_smpte(self, status):
    #     self._set_led(self._MIDI_CC_LED_AUTOMAP_FX, status)


if __name__ == "__main__":

    import time

    port_midi_input = 'ZeRO MkII: Port 1'
    port_midi_output = 'ZeRO MkII: Port 1'

    controller = ZeroSlMk2(port_midi_input, port_midi_output)
    controller.connect()

    for id in range(0x00, 0x80):
        print 'testing LED 0x%02X' % id
        controller.set_led(id, 1)
        time.sleep(0.05)
        controller.set_led(id, 0)

    for mode in range(0x00, 0x50, 0x10):
        for id in range(8):
            controller.set_led(0x78 + id, mode)
        for status in range(0x00, 0x0C):
            print 'testing mode 0x%02X, status 0x%02X' % (mode, status)
            for id in range(8):
                controller.set_led(0x70 + id, status)
            time.sleep(0.05)

        for id in range(8):
            controller.set_led(0x70 + id, 0)

    controller.disconnect()
