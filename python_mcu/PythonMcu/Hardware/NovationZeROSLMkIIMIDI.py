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

from ..Hardware.NovationZeROSLMkII import NovationZeROSLMkII
from ..Midi.MidiPorts import MidiPorts


class NovationZeROSLMkIIMIDI(NovationZeROSLMkII):
    def __init__(self, midi_input, midi_output, callback_log):
        NovationZeROSLMkII.__init__(self, midi_input, midi_output, callback_log)

    @staticmethod
    def get_usage_hint():
        return 'Connect the controller\'s "MIDI Port 1" to your MIDI interface, ' + \
               'switch to preset #32 (Ableton Live Automap) ' + \
               'and change the following settings:\n\n' + \
               '* Global --> Routing --> MIDI To:\n  remove port "M1"\n' + \
               '* Edit --> Routing --> ProgPort:\n  add port "M1"\n' + \
               '* Edit --> Routing --> ComnPort:\n  add port "M1"'

    # --- MIDI processing ---
    @staticmethod
    def get_preferred_midi_input():
        return MidiPorts.get_default_midi_input()

    @staticmethod
    def get_preferred_midi_output():
        return MidiPorts.get_default_midi_output()
