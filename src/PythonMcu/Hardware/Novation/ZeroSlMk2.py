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
    MIDI_MANUFACTURER_ID = (0x00, 0x20, 0x29)

    # MIDI device ID and initialisation of Novation ZeRO SL Mkii
    MIDI_DEVICE_ID = (0x03, 0x03, 0x12, 0x00, 0x04, 0x00)

    # MIDI channel of controller
    _MIDI_DEVICE_CHANNEL = 0

    # number of available channels strips on controller
    _CHANNEL_STRIPS = 8

    # number of available LCD pages on controller
    _LCD_PAGES = 4

    # number of available LCD characters per channel strip
    _LCD_FIELD_LENGTH = 9

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
    _MIDI_CC_BUTTON_TRANSPORT_MODE = 0x4F

    _MIDI_CC_LED_AUTOMAP_LEARN = 0x48
    _MIDI_CC_LED_AUTOMAP_VIEW = 0x49
    _MIDI_CC_LED_AUTOMAP_USER = 0x4A
    _MIDI_CC_LED_AUTOMAP_FX = 0x4B
    _MIDI_CC_LED_AUTOMAP_MIXER = 0x4D


    def __init__(self, midi_input, midi_output):
        MidiControllerTemplate.__init__(self, midi_input, midi_output)

        self.display_available = True
        self.automated_faders_available = False
        self.display_7seg_available = True
        self.display_timecode_available = False
        self.meter_bridge_available = False

        self._menu_string = ''

        self._transport_mode = False

        self._LED_CYCLE = 0
        self._LED_REWIND = 0
        self._LED_FAST_FORWARD = 0
        self._LED_STOP = 0
        self._LED_PLAY = 0
        self._LED_RECORD = 0


    def connect(self):
        MidiControllerTemplate.connect(self)

        self._log('Starting "Ableton" mode...')

        self._lcd_strings = ['', '']

        self._update_lcd(1, 'Initialising Novation Zero SL MkII hardware controller.')
        self._update_lcd(2, 'Connecting to your DAW...')

        self.send_midi_sysex([0x01, 0x01])

        self.send_midi_control_change(self._MIDI_CC_CLEAR_ALL_LEDS, 0x00)

        self._log('Connected.')


    def disconnect(self):
        self._log('Disconnecting...')

        self._log('Stopping "Ableton" mode...')

        self.send_midi_control_change(self._MIDI_CC_CLEAR_ALL_LEDS, 0x00)

        self.send_midi_sysex([0x02, 0x02, 0x05])
        self.send_midi_sysex([0x01, 0x00])

        MidiControllerTemplate.disconnect(self)


    def _log(self, message):
        print '[Novation ZeRO SL MkII]  ' + message


    def send_midi_control_change(self, cc_number, cc_value):
        MidiControllerTemplate.send_midi_control_change( \
            self, self._MIDI_DEVICE_CHANNEL, cc_number, cc_value)


    def receive_midi(self, status, message):
        cc_selector = {
            self._MIDI_CC_FADERS: \
                'self.mackie_control_host.move_fader_7bit(0, %d)',
            self._MIDI_CC_FADERS + 1: \
                'self.mackie_control_host.move_fader_7bit(1, %d)',
            self._MIDI_CC_FADERS + 2: \
                'self.mackie_control_host.move_fader_7bit(2, %d)',
            self._MIDI_CC_FADERS + 3: \
                'self.mackie_control_host.move_fader_7bit(3, %d)',
            self._MIDI_CC_FADERS + 4: \
                'self.mackie_control_host.move_fader_7bit(4, %d)',
            self._MIDI_CC_FADERS + 5: \
                'self.mackie_control_host.move_fader_7bit(5, %d)',
            self._MIDI_CC_FADERS + 6: \
                'self.mackie_control_host.move_fader_7bit(6, %d)',
            self._MIDI_CC_FADERS + 7: \
                'self.mackie_control_host.move_fader_7bit(7, %d)',
            self._MIDI_CC_ENCODERS:
                'self.mackie_control_host.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 0, %d)',
            self._MIDI_CC_ENCODERS + 1:
                'self.mackie_control_host.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 1, %d)',
            self._MIDI_CC_ENCODERS + 2:
                'self.mackie_control_host.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 2, %d)',
            self._MIDI_CC_ENCODERS + 3:
                'self.mackie_control_host.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 3, %d)',
            self._MIDI_CC_ENCODERS + 4:
                'self.mackie_control_host.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 4, %d)',
            self._MIDI_CC_ENCODERS + 5:
                'self.mackie_control_host.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 5, %d)',
            self._MIDI_CC_ENCODERS + 6:
                'self.mackie_control_host.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 6, %d)',
            self._MIDI_CC_ENCODERS + 7:
                'self.mackie_control_host.move_vpot_raw(self._MIDI_DEVICE_CHANNEL, 7, %d)',
            self._MIDI_CC_BUTTONS_LEFT_TOP:
                'self.mackie_control_host.keypress_channel_record_ready(0, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_TOP + 1:
                'self.mackie_control_host.keypress_channel_record_ready(1, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_TOP + 2:
                'self.mackie_control_host.keypress_channel_record_ready(2, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_TOP + 3:
                'self.mackie_control_host.keypress_channel_record_ready(3, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_TOP + 4:
                'self.mackie_control_host.keypress_channel_record_ready(4, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_TOP + 5:
                'self.mackie_control_host.keypress_channel_record_ready(5, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_TOP + 6:
                'self.mackie_control_host.keypress_channel_record_ready(6, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_TOP + 7:
                'self.mackie_control_host.keypress_channel_record_ready(7, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_BOTTOM:
                'self.mackie_control_host.keypress_channel_select(0, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 1:
                'self.mackie_control_host.keypress_channel_select(1, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 2:
                'self.mackie_control_host.keypress_channel_select(2, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 3:
                'self.mackie_control_host.keypress_channel_select(3, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 4:
                'self.mackie_control_host.keypress_channel_select(4, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 5:
                'self.mackie_control_host.keypress_channel_select(5, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 6:
                'self.mackie_control_host.keypress_channel_select(6, %d & 0x01)',
            self._MIDI_CC_BUTTONS_LEFT_BOTTOM + 7:
                'self.mackie_control_host.keypress_channel_select(7, %d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_TOP:
                'self.keypress_shift(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_TOP + 1:
                'self.keypress_control(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_TOP + 2:
                'self.keypress_command_alt(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_TOP + 3:
                'self.keypress_option(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_TOP + 4:
                'self.keypress_cursor_left(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_TOP + 5:
                'self.keypress_cursor_right(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_TOP + 6:
                'self.keypress_cursor_down(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_TOP + 7:
                'self.keypress_cursor_up(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM:
                'self.change_mode_bank(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1:
                'self.change_mode_global(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2:
                'self.change_mode_automation(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3:
                'self.change_mode_utility(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 4:
                'self.keypress_name_value(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 5:
                'self.mackie_control_host.keypress_flip(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 6:
                'self.mackie_control_host.keypress_scrub(%d & 0x01)',
            self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 7:
                'self.mackie_control_host.keypress_zoom(%d & 0x01)',
            self._MIDI_CC_BUTTON_TRANSPORT_MODE:
                'self._keypress_transport_mode(%d & 0x01)',
            self._MIDI_CC_BUTTON_REWIND:
                'self.mackie_control_host.keypress_rewind(%d & 0x01)',
            self._MIDI_CC_BUTTON_FAST_FORWARD:
                'self.mackie_control_host.keypress_fast_forward(%d & 0x01)',
            self._MIDI_CC_BUTTON_STOP:
                'self.mackie_control_host.keypress_stop(%d & 0x01)',
            self._MIDI_CC_BUTTON_PLAY:
                'self.mackie_control_host.keypress_play(%d & 0x01)',
            self._MIDI_CC_BUTTON_RECORD:
                'self.mackie_control_host.keypress_record(%d & 0x01)',
            self._MIDI_CC_BUTTON_CYCLE:
                'self.mackie_control_host.keypress_cycle(%d & 0x01)',
            }

        if status == (MidiConnection.CONTROL_CHANGE + \
                          self._MIDI_DEVICE_CHANNEL):
            cc_number = message[1]
            cc_value = message[2]

            if cc_number in cc_selector:
                eval(cc_selector[cc_number] % cc_value)
            else:
                message_string = ['status %02X: ' % status]
                for byte in message:
                    message_string.append('%02X' % byte)
                self._log(' '.join(message_string))
        else:
            message_string = ['status %02X: ' % status]
            for byte in message:
                message_string.append('%02X' % byte)
            self._log(' '.join(message_string))


    def _keypress_transport_mode(self, status):
        if status > 0:
            self._transport_mode = True

            menu_strings = \
                ('Click', 'Solo', 'Marker', 'Nudge', \
                 'SMPTE/Bt', '', 'Drop', 'Replace')
            self._set_menu_string(menu_strings)

            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM, self._LED_REWIND)
            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1, self._LED_FAST_FORWARD)
            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2, self._LED_STOP)
            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3, self._LED_PLAY)
            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 4, self._LED_CYCLE)
            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 5, self._LED_RECORD)
        else:
            self._transport_mode = False

            self._clear_menu_string()

            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM, 0)
            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 1, 0)
            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 2, 0)
            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 3, 0)
            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 4, 0)
            self.update_led( \
                self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 5, 0)


    def update_encoder_light(self, position, value):
        if self._encoder_positions[position] == value:
            return
        else:
            self._encoder_positions[position] = value

            self.send_midi_control_change(self._MIDI_CC_ENCODER_LIGHTS + position, value)


    def set_display_7seg(self, position, character_code):
        MidiControllerTemplate.set_display_7seg(self, position, character_code)


    def _clear_menu_string(self):
        self._menu_string = ''
        self._log('Menu: cleared.')
        self._update_lcd(4, '')


    def _set_menu_string(self, menu_strings):
        assert(len(menu_strings) == 8)

        self._clear_menu_string()
        for menu_string in menu_strings:
            self._menu_string += menu_string.center(9)

        self._log('Menu: "%s".' % self._menu_string)
        self._update_lcd(3, self._menu_string)


    def _update_lcd_raw(self, position, hex_codes):
        """
        send hex codes of maximum 72 bytes to controller LCD

        position 1: top row
        position 2: bottom row
        """
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


    def update_lcd(self, position, new_string):
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

        self._update_lcd(position, converted_string)


    def _update_lcd(self, position, new_string):
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
            has_changed = False
            new_string = new_string.ljust(72)

            if self._lcd_strings[position - 1] != new_string:
                self._lcd_strings[position - 1] = new_string
                has_changed = True

            if not has_changed or self._menu_string:
                return

        # convert string
        hex_codes = []
        for character in new_string:
            hex_codes.append(ord(character))

        self._update_lcd_raw(position, hex_codes)


    def change_mode_bank(self, status):
        if status:
            menu_strings = \
                ('<<', '<', '>', '>>', \
                 '', '', '', '')
            self._set_menu_string(menu_strings)
        else:
            self._clear_menu_string()


    def change_mode_global(self, status):
        if status:
            menu_strings = \
                ('MIDI', 'Inputs', 'AudioTr.', 'Instrum.', \
                 'AUX', 'Busses', 'Outputs', 'User')
            self._set_menu_string(menu_strings)
        else:
            self._clear_menu_string()


    def change_mode_automation(self, status):
        if status:
            menu_strings = \
                ('Read/Off', 'Write', 'Trim', 'Touch', \
                 'Latch', '', '', 'Group')
            self._set_menu_string(menu_strings)
        else:
            self._clear_menu_string()


    def change_mode_utility(self, status):
        if status:
            menu_strings = \
                ('Enter', 'Cancel', '', 'Undo', \
                 '', '', '', 'Save')
            self._set_menu_string(menu_strings)
        else:
            self._clear_menu_string()


    def keypress_shift(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_TOP, status)
        self.mackie_control_host.keypress_shift(status)


    def keypress_control(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_TOP + 1, status)
        self.mackie_control_host.keypress_control(status)


    def keypress_command_alt(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_TOP + 2, status)
        self.mackie_control_host.keypress_command_alt(status)


    def keypress_option(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_TOP + 3, status)
        self.mackie_control_host.keypress_option(status)


    def keypress_cursor_left(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_TOP + 4, status)
        self.mackie_control_host.keypress_cursor_left(status)


    def keypress_cursor_right(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_TOP + 5, status)
        self.mackie_control_host.keypress_cursor_right(status)


    def keypress_cursor_down(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_TOP + 6, status)
        self.mackie_control_host.keypress_cursor_down(status)


    def keypress_cursor_up(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_TOP + 7, status)
        self.mackie_control_host.keypress_cursor_up(status)


    def keypress_name_value(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 4, status)
        self.mackie_control_host.keypress_name_value(status)


    def set_vpot_led_ring(self, id, center_led, mode, position):
        if mode == self.VPOT_MODE_WRAP:
            vpot_mode = 0x00
        elif mode == self.VPOT_MODE_BOOST_CUT:
            vpot_mode = 0x20
        elif mode == self.VPOT_MODE_SPREAD:
            vpot_mode = 0x30
        elif mode == self.VPOT_MODE_SINGLE_DOT:
            vpot_mode = 0x40

        self.update_led(self._MIDI_CC_ENCODER_MODE + id, vpot_mode)
        self.update_led(self._MIDI_CC_ENCODER_LIGHTS + id, position)


    def update_vpot_mode(self, id, status, inverted=False):
        # channel: 0 - 7
        if inverted:
            if status == 1:
                status = 0
            elif status == 0:
                status = 1



    def update_led(self, id, status, inverted=False):
        # channel: 0 - 7
        if inverted:
            if status == 1:
                status = 0
            elif status == 0:
                status = 1

        MidiControllerTemplate.send_midi_control_change( \
            self, self._MIDI_DEVICE_CHANNEL, id, status)


    def update_led_channel_record_ready(self, channel, status):
        # channel: 0 - 7
        self.update_led(self._MIDI_CC_BUTTONS_LEFT_TOP + channel, status)


    def update_led_channel_select(self, channel, status):
        # channel: 0 - 7
        self.update_led(self._MIDI_CC_BUTTONS_LEFT_BOTTOM + channel, status)


    def update_led_channel_mute(self, channel, status):
        # channel: 0 - 7
        self.update_led( \
            self._MIDI_CC_BUTTONS_RIGHT_TOP + channel, status)


    def update_led_channel_solo(self, channel, status):
        # channel: 0 - 7
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + channel, status)


    def update_led_flip(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 5, status)


    def update_led_scrub(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 6, status)


    def update_led_zoom(self, status):
        self.update_led(self._MIDI_CC_BUTTONS_RIGHT_BOTTOM + 7, status)


    def update_led_cycle(self, status):
        self._LED_CYCLE = status
        if self._transport_mode:
            self._keypress_transport_mode(1)


    def update_led_rewind(self, status):
        self._LED_REWIND = status
        if self._transport_mode:
            self._keypress_transport_mode(1)


    def update_led_fast_forward(self, status):
        self._LED_FAST_FORWARD = status
        if self._transport_mode:
            self._keypress_transport_mode(1)


    def update_led_stop(self, status):
        self._LED_STOP = status
        if self._transport_mode:
            self._keypress_transport_mode(1)


    def update_led_play(self, status):
        self._LED_PLAY = status
        if self._transport_mode:
            self._keypress_transport_mode(1)


    def update_led_record(self, status):
        self._LED_RECORD = status
        if self._transport_mode:
            self._keypress_transport_mode(1)


    def update_led_relay_click(self, status):
        self.update_led(self._MIDI_CC_LED_AUTOMAP_LEARN, status)


    def update_led_rude_solo(self, status):
        self.update_led(self._MIDI_CC_LED_AUTOMAP_VIEW, status)


    def update_led_beats(self, status):
        self.update_led(self._MIDI_CC_LED_AUTOMAP_USER, status)


    def update_led_smpte(self, status):
        self.update_led(self._MIDI_CC_LED_AUTOMAP_FX, status)


if __name__ == "__main__":

    import time

    port_midi_input = 'ZeRO MkII: Port 1'
    port_midi_output = 'ZeRO MkII: Port 1'

    controller = ZeroSlMk2(port_midi_input, port_midi_output)
    controller.connect()

    for id in range(0x00, 0x80):
        print 'testing LED 0x%02X' % id
        controller.update_led(id, 1)
        time.sleep(0.05)
        controller.update_led(id, 0)

    for mode in range(0x00, 0x50, 0x10):
        for id in range(8):
            controller.update_led(0x78 + id, mode)
        for status in range(0x00, 0x0C):
            print 'testing mode 0x%02X, status 0x%02X' % (mode, status)
            for id in range(8):
                controller.update_led(0x70 + id, status)
            time.sleep(0.05)

        for id in range(8):
            controller.update_led(0x70 + id, 0)

    controller.disconnect()
