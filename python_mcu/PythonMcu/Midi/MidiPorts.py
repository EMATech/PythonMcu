# -*- coding: utf-8 -*-

"""
PythonMcu
=========
Mackie Host Controller written in Python
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
"""
import string

import rtmidi


def _clean_port_names(ports):
    """
    Removes port ID numbers from rtmidi’s names to keep them human friendly.

    Note: this may induce name collisions if multiple interfaces with the same
    name are available.
    """
    clean_ports = []
    for port in ports:
        clean_ports.append(port.rstrip(string.digits).rstrip(string.whitespace))
    return sorted(clean_ports)


class MidiPorts:
    _inputs = rtmidi.MidiIn()
    _outputs = rtmidi.MidiOut()

    input_ports = _clean_port_names(_inputs.get_ports())
    output_ports = _clean_port_names(_outputs.get_ports())

    @staticmethod
    def get_midi_inputs():
        return MidiPorts.input_ports

    @staticmethod
    def get_midi_outputs():
        return MidiPorts.output_ports

    @staticmethod
    def get_default_midi_input():
        return MidiPorts.input_ports[0]

    @staticmethod
    def get_default_midi_output():
        return MidiPorts.output_ports[0]

    @staticmethod
    def refresh_ports():
        MidiPorts.input_ports = _clean_port_names(MidiPorts._inputs.get_ports())
        MidiPorts.output_ports = _clean_port_names(MidiPorts._outputs.get_ports())
