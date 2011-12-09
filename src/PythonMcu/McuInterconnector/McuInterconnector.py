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
    sys.path.append('../../')

from PythonMcu.Hardware import *
from PythonMcu.MackieControl.MackieHostControl import MackieHostControl
from PythonMcu.Midi.MidiConnection import MidiConnection
from PythonMcu.Tools.ApplicationConfiguration import *


class McuInterconnector(object):

    _LED_STATUS = {
        0x00: 'off',
        0x01: 'flashing',
        0x7F: 'on'
        }

    _MCU_COMMANDS = [
        'function_channel_1',
        'function_channel_2',
        'function_channel_3',
        'function_channel_4',
        'function_channel_5',
        'function_channel_6',
        'function_channel_7',
        'function_channel_8',
        'mute_channel_1',
        'mute_channel_2',
        'mute_channel_3',
        'mute_channel_4',
        'mute_channel_5',
        'mute_channel_6',
        'mute_channel_7',
        'mute_channel_8',
        'record_ready_channel_1',
        'record_ready_channel_2',
        'record_ready_channel_3',
        'record_ready_channel_4',
        'record_ready_channel_5',
        'record_ready_channel_6',
        'record_ready_channel_7',
        'record_ready_channel_8',
        'select_channel_1',
        'select_channel_2',
        'select_channel_3',
        'select_channel_4',
        'select_channel_5',
        'select_channel_6',
        'select_channel_7',
        'select_channel_8',
        'solo_channel_1',
        'solo_channel_2',
        'solo_channel_3',
        'solo_channel_4',
        'solo_channel_5',
        'solo_channel_6',
        'solo_channel_7',
        'solo_channel_8',
        'vselect_channel_1',
        'vselect_channel_2',
        'vselect_channel_3',
        'vselect_channel_4',
        'vselect_channel_5',
        'vselect_channel_6',
        'vselect_channel_7',
        'vselect_channel_8',

        'assignment_eq',
        'assignment_instrument',
        'assignment_pan_surround',
        'assignment_plug_in',
        'assignment_send',
        'assignment_track',
        'automation_latch',
        'automation_read_off',
        'automation_touch',
        'automation_trim',
        'automation_write',
        'beats',
        'click',
        'command_alt',
        'control',
        'cursor_down',
        'cursor_left',
        'cursor_right',
        'cursor_up',
        'cycle',
        'drop',
        'fader_banks_bank_left',
        'fader_banks_bank_right',
        'fader_banks_channel_left',
        'fader_banks_channel_right',
        'fast_forward',
        'flip',
        'global_view',
        'global_view_audio_instruments',
        'global_view_audio_tracks',
        'global_view_aux',
        'global_view_busses',
        'global_view_inputs',
        'global_view_midi_tracks',
        'global_view_outputs',
        'global_view_user',
        'group',
        'marker',
        'name_value',
        'nudge',
        'option',
        'play',
        'record',
        'relay_click',
        'replace',
        'rewind',
        'rude_solo',
        'scrub',
        'shift',
        'smpte',
        'smpte_beats',
        'solo',
        'stop',
        'user_switch_1',
        'user_switch_2',
        'utilities_cancel',
        'utilities_enter',
        'utilities_save',
        'utilities_undo',
        'zoom',
    ]


    def __init__(self, mcu_model_id, mcu_connection, \
                     mcu_midi_input, mcu_midi_output, \
                     hardware_controller_class, controller_midi_input, \
                     controller_midi_output, callback_log):
        self._play_status = False
        self._callback_log = callback_log

        eval_controller_init = \
            '%(cc)s.%(cc)s("%(midi_in)s", "%(midi_out)s", callback_log)' % \
            {'cc': hardware_controller_class, \
                 'midi_in': controller_midi_input, \
                 'midi_out': controller_midi_output}
        self._hardware_controller = eval(eval_controller_init)

        # get "Python MCU" version number
        python_mcu_version = ApplicationConfiguration().get_version(False)

        self._mackie_host_control = MackieHostControl( \
            mcu_model_id, mcu_connection, python_mcu_version, \
                mcu_midi_input, mcu_midi_output, callback_log)

        # set this here so the hardware controller can notify the user
        # about the connection process
        self._hardware_controller.set_interconnector(self)
        self._mackie_host_control.set_hardware_controller(self)

        self._led__hardware_to_mcu = {}
        self._led__mcu_to_hardware = {}

        self.withdraw_all_controls()


    def _log(self, message, repaint=False):
        self._log_message('[MCU Interconnector   ]  ' + message, repaint)


    # --- initialisation ---

    def connect(self):
        self._hardware_controller.connect()
        self._mackie_host_control.connect()


    def disconnect(self):
        self.withdraw_all_controls()

        self._mackie_host_control.disconnect()
        self._hardware_controller.disconnect()


    def go_online(self):
        self._hardware_controller.go_online()


    def go_offline(self):
        self._hardware_controller.go_offline()


    def process_midi_input(self):
        self._hardware_controller.process_midi_input()
        self._mackie_host_control.process_midi_input()


    # --- registration of MIDI controls ---

    def register_control(self, mcu_command, midi_switch, midi_led):
        self.withdraw_control(midi_switch)

        self._led__hardware_to_mcu[midi_switch] = mcu_command
        self._led__mcu_to_hardware[mcu_command]['midi_switch'] = midi_switch
        self._led__mcu_to_hardware[mcu_command]['midi_led'] = midi_led

        self._update_led(mcu_command)


    def withdraw_control(self, midi_switch):
        if midi_switch in self._led__hardware_to_mcu:
            mcu_command = self._led__hardware_to_mcu[midi_switch]
            midi_led = self._led__mcu_to_hardware[mcu_command]['midi_led']

            if type(midi_led) != types.NoneType:
                self._hardware_controller.set_led(midi_led, 0)

            del self._led__hardware_to_mcu[midi_switch]
            self._led__mcu_to_hardware[mcu_command]['midi_switch'] = None
            self._led__mcu_to_hardware[mcu_command]['midi_led'] = None


    def withdraw_all_controls(self):
        for midi_switch in self._led__hardware_to_mcu.keys():
            mcu_command = self._led__hardware_to_mcu[midi_switch]
            midi_led = self._led__mcu_to_hardware[mcu_command]['midi_led']

            if type(midi_led) != types.NoneType:
                self._hardware_controller.set_led(midi_led, 0)

        self._led__hardware_to_mcu = {}
        self._led__mcu_to_hardware = {}

        for command in self._MCU_COMMANDS:
            self._led__mcu_to_hardware[command] = \
            {
                'midi_switch': None,
                'midi_led': None,
                'value': 0
            }


    # --- MCU Interconnector commands ---

    def keypress(self, internal_id, status):
        if internal_id in self._led__hardware_to_mcu:
            mcu_command = self._led__hardware_to_mcu[internal_id]
            self.keypress_unregistered(mcu_command, status)
            return True
        else:
            return False


    def keypress_unregistered(self, mcu_command, status):
        command = 'self._mackie_host_control.keypress_%s(%d)' % \
            (mcu_command, status)
        eval(command)


    def _set_led(self, mcu_command, status):
        if self._led__mcu_to_hardware[mcu_command]['value'] != status:
            self._led__mcu_to_hardware[mcu_command]['value'] = status

            if type(self._led__mcu_to_hardware[mcu_command]['midi_switch']) != \
                    types.NoneType:
                self._update_led(mcu_command)


    def _update_led(self, mcu_command):
        if type(self._led__mcu_to_hardware[mcu_command]['midi_switch']) != \
                types.NoneType:
            status = self._led__mcu_to_hardware[mcu_command]['value']
            self._hardware_controller.set_led( \
                self._led__mcu_to_hardware[mcu_command]['midi_led'], status)


    def is_playing(self):
        return self._play_status


    # --- hardware controller commands ---

    def has_display_7seg(self):
        return self._hardware_controller.has_display_7seg()


    def has_display_lcd(self):
        return self._hardware_controller.has_display_lcd()


    def has_display_timecode(self):
        return self._hardware_controller.has_display_timecode()


    def has_automated_faders(self):
        return self._hardware_controller.has_automated_faders()


    def has_meter_bridge(self):
        return self._hardware_controller.has_meter_bridge()


    def move_fader(self, fader_id, fader_value):
        self._mackie_host_control.move_fader(fader_id, fader_value)


    def move_fader_7bit(self, fader_id, fader_value):
        self._mackie_host_control.move_fader_7bit(fader_id, fader_value)


    def move_vpot(self, midi_channel, vpot_id, direction, number_of_ticks):
        self._mackie_host_control.move_vpot( \
            midi_channel, vpot_id, direction, number_of_ticks)

    def move_vpot_raw(self, midi_channel, vpot_id, vpot_movement):
        self._mackie_host_control.move_vpot_raw( \
            midi_channel, vpot_id, vpot_movement)


    # --- Mackie Control Unit commands ---

    def fader_moved(self, fader_id, fader_position):
        self._hardware_controller.fader_moved(fader_id, fader_position)


    def set_peak_level(self, meter_id, meter_level):
        self._hardware_controller.set_peak_level(meter_id, meter_level)


    def set_display_7seg(self, position, character_code):
        self._hardware_controller.set_display_7seg(position, character_code)


    def set_display_timecode(self, position, character_code):
        self._hardware_controller.set_display_timecode(position, character_code)


    def set_vpot_led_ring(self, vpot_id, vpot_center_led, \
                              vpot_mode, vpot_position):
        self._hardware_controller.set_vpot_led_ring( \
            vpot_id, vpot_center_led, vpot_mode, vpot_position)


    def set_lcd(self, position, hex_codes):
        self._hardware_controller.set_lcd(position, hex_codes)


    def set_led_channel_record_ready(self, channel, status):
        # channel: 0 - 7
        self._set_led('record_ready_channel_%d' % (channel + 1), status)


    def set_led_channel_solo(self, channel, status):
        # channel: 0 - 7
        self._set_led('solo_channel_%d' % (channel + 1), status)


    def set_led_channel_mute(self, channel, status):
        # channel: 0 - 7
        self._set_led('mute_channel_%d' % (channel + 1), status)


    def set_led_channel_select(self, channel, status):
        # channel: 0 - 7
        self._set_led('select_channel_%d' % (channel + 1), status)


    def set_led_channel_vselect(self, channel, status):
        # channel: 0 - 7
        self._set_led('vselect_channel_%d' % (channel + 1), status)


    def set_led_assignment_track(self, status):
        self._set_led('assignment_track', status)


    def set_led_assignment_send(self, status):
        self._set_led('assignment_send', status)


    def set_led_assignment_pan_surround(self, status):
        self._set_led('assignment_pan_surround', status)


    def set_led_assignment_plug_in(self, status):
        self._set_led('assignment_plug_in', status)


    def set_led_assignment_eq(self, status):
        self._set_led('assignment_eq', status)


    def set_led_assignment_instrument(self, status):
        self._set_led('assignment_instrument', status)


    def set_led_flip(self, status):
        self._set_led('flip', status)


    def set_led_global_view(self, status):
        self._set_led('global_view', status)


    def set_led_automation_read_off(self, status):
        self._set_led('automation_read_off', status)


    def set_led_automation_write(self, status):
        self._set_led('automation_write', status)


    def set_led_automation_trim(self, status):
        self._set_led('automation_trim', status)


    def set_led_automation_touch(self, status):
        self._set_led('automation_touch', status)


    def set_led_automation_latch(self, status):
        self._set_led('automation_latch', status)


    def set_led_group(self, status):
        self._set_led('group', status)


    def set_led_utilities_save(self, status):
        self._set_led('utilities_save', status)


    def set_led_utilities_undo(self, status):
        self._set_led('utilities_undo', status)


    def set_led_marker(self, status):
        self._set_led('marker', status)


    def set_led_nudge(self, status):
        self._set_led('nudge', status)


    def set_led_cycle(self, status):
        self._set_led('cycle', status)


    def set_led_drop(self, status):
        self._set_led('drop', status)


    def set_led_replace(self, status):
        self._set_led('replace', status)


    def set_led_click(self, status):
        self._set_led('click', status)


    def set_led_solo(self, status):
        self._set_led('solo', status)


    def set_led_rewind(self, status):
        self._set_led('rewind', status)


    def set_led_fast_forward(self, status):
        self._set_led('fast_forward', status)


    def set_led_stop(self, status):
        self._set_led('stop', status)


    def set_led_play(self, status):
        if status:
            self._play_status = True
        else:
            self._play_status = False

        self._set_led('play', status)


    def set_led_record(self, status):
        self._set_led('record', status)


    def set_led_zoom(self, status):
        self._set_led('zoom', status)


    def set_led_scrub(self, status):
        self._set_led('scrub', status)


    def set_led_smpte(self, status):
        self._set_led('smpte', status)


    def set_led_beats(self, status):
        self._set_led('beats', status)


    def set_led_rude_solo(self, status):
        self._set_led('rude_solo', status)


    def set_led_relay_click(self, status):
        self._set_led('relay_click', status)


    def faders_to_minimum(self):
        self._hardware_controller.faders_to_minimum()


    def all_leds_off(self):
        self._hardware_controller.all_leds_off()
