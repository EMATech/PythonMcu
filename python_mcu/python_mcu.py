#!/usr/bin/env python
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
import importlib
import platform
import sys

import PySide6
import rtmidi.version
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QFontMetrics, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QFrame, QApplication, QPlainTextEdit, QStyle, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLabel, QComboBox, QPushButton, QCheckBox

from PythonMcu.MackieControl.MackieHostControl import MackieHostControl
from PythonMcu.McuInterconnector.McuInterconnector import McuInterconnector
from PythonMcu.Midi.MidiPorts import MidiPorts
from PythonMcu.Tools.AboutDialog import AboutDialog
from PythonMcu.Tools.ApplicationConfiguration import ApplicationConfiguration

configuration = ApplicationConfiguration()

DEBUG = True


# noinspection PyArgumentList
class PythonMcuApp(QFrame):
    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super().__init__(parent)

        self._controller_midi_input = None
        self._controller_midi_output = None
        self._hardware_controller = None
        self._hardware_controller_class = None
        self._mcu_connection = None
        self._mcu_emulated_model = None
        self._mcu_midi_input = None
        self._mcu_midi_output = None
        self._mcu_model_id = None

        font = QFont()
        font.setStyleHint(QFont.TypeWriter, QFont.PreferAntialias)

        char_format = QTextCharFormat()
        char_format.setFontFamily(font.defaultFamily())
        text_width = QFontMetrics(char_format.font()).horizontalAdvance('*') * 80

        # must be defined before starting the logger!
        self._edit_logger = QPlainTextEdit()
        self._edit_logger.setReadOnly(True)
        self._edit_logger.setCurrentCharFormat(char_format)
        self._edit_logger.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self._edit_logger.setFixedWidth(text_width)

        # must be defined before reading the configuration file!
        self._edit_usage_hint = QPlainTextEdit()
        self._edit_usage_hint.setReadOnly(True)
        self._edit_usage_hint.setCurrentCharFormat(char_format)

        self.callback_log('')
        self.callback_log(configuration.get_full_description())
        self.callback_log('')
        self.callback_log('')
        self.callback_log('Version numbers')
        self.callback_log('===============')
        self.callback_log('')
        self.callback_log(f'Python: {platform.python_version()} ({platform.python_implementation()})')
        self.callback_log(f'PySide6: {PySide6.__version__}')
        self.callback_log(f'rtmidi: {rtmidi.version.version}')
        self.callback_log('')
        self.callback_log('')

        # auto-scroll log window by setting cursor to end of document
        self._edit_logger.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)

        self._read_configuration()

        self._timer = None
        self._interconnector = None

        icon = self.style().standardIcon(QStyle.SP_TitleBarMenuButton)
        self.setWindowIcon(icon)

        mcu_model_ids = [
            'Logic Control', 'Logic Control XT',
            'Mackie Control', 'Mackie Control XT'
        ]

        # TODO: derive from classes imported via PythonMcu.Hardware *
        hardware_controllers = [
            'Novation ZeRO SL MkII',
            'Novation ZeRO SL MkII (MIDI)'
        ]
        if DEBUG:
            hardware_controllers.append('_Midi Controller Template')

        self.setWindowTitle(configuration.get_version(True))

        # create layouts and add widgets
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout_2 = QVBoxLayout()
        self.layout.addLayout(self.layout_2)

        self.frame_mcu = QFrame()
        self.frame_mcu.setFrameStyle(QFrame.Box)
        self.frame_mcu.setFrameShadow(QFrame.Sunken)
        self.layout_2.addWidget(self.frame_mcu)
        self.grid_layout_mcu = QGridLayout()
        self.frame_mcu.setLayout(self.grid_layout_mcu)

        self.frame_controller = QFrame()
        self.frame_controller.setFrameStyle(QFrame.Box)
        self.frame_controller.setFrameShadow(QFrame.Sunken)
        self.layout_2.addWidget(self.frame_controller)
        self.grid_layout_controller = QGridLayout()
        self.frame_controller.setLayout(self.grid_layout_controller)

        self._combo_mcu_model_id = self._create_combo_box(
            self.grid_layout_mcu, self._mcu_emulated_model,
            'Emulation:', mcu_model_ids
        )

        connection_types = [
            MackieHostControl.ASSUME_SUCCESSFUL_CONNECTION,
            MackieHostControl.CHALLENGE_RESPONSE,
            MackieHostControl.WAIT_FOR_MIDI_DATA
        ]
        self._combo_mcu_connection = self._create_combo_box(
            self.grid_layout_mcu, self._mcu_connection,
            'Connection:', connection_types
        )

        # TODO: create automatically and only show name
        self._combo_mcu_midi_input = self._create_combo_box(
            self.grid_layout_mcu, self._mcu_midi_input,
            'MIDI In:', MidiPorts.get_midi_inputs()
        )

        # TODO: create automatically and only show name
        self._combo_mcu_midi_output = self._create_combo_box(
            self.grid_layout_mcu, self._mcu_midi_output,
            'MIDI Out:', MidiPorts.get_midi_outputs()
        )

        self._combo_hardware_controller = self._create_combo_box(
            self.grid_layout_controller, self._hardware_controller,
            'Controller:', hardware_controllers
        )

        self._combo_controller_midi_input = self._create_combo_box(
            self.grid_layout_controller, self._controller_midi_input,
            'MIDI In:', MidiPorts.get_midi_inputs()
        )
        self._combo_controller_midi_output = self._create_combo_box(
            self.grid_layout_controller, self._controller_midi_output,
            'MIDI Out:', MidiPorts.get_midi_outputs()
        )

        self.button_controller_midi_refresh = QPushButton('Refresh MIDI ports')
        row = self.grid_layout_controller.rowCount()
        self.grid_layout_controller.addWidget(self.button_controller_midi_refresh, row, 1)
        self.button_controller_midi_refresh.clicked.connect(self.midiports_refresh)

        self.grid_layout_controller.addWidget(
            self._edit_usage_hint, self.grid_layout_controller.rowCount(),
            0, 1, 2
        )

        self.layout.addWidget(self._edit_logger)

        self.bottom_layout = QHBoxLayout()
        self.layout_2.addLayout(self.bottom_layout)

        self.button_start_stop = QPushButton('&Start')
        self.bottom_layout.addWidget(self.button_start_stop)
        self.button_start_stop.setDefault(True)
        self.button_start_stop.setFocus()
        self.button_start_stop.clicked.connect(self.interconnector_start_stop)

        # TODO: add autostart checkbox and configuration
        self.checkbox_autostart = QCheckBox('Autostart')
        self.bottom_layout.addWidget(self.checkbox_autostart)

        self.button_close = QPushButton('&Close')
        self.bottom_layout.addWidget(self.button_close)
        self.button_close.clicked.connect(self.close_application)
        self.closeEvent = self.close_event  # Hide PySide's non pythonic method name

        self.button_about = QPushButton('A&bout')
        self.bottom_layout.addWidget(self.button_about)
        self.button_about.clicked.connect(self.display_about)

        self._enable_controls(True)

        self._timer = QTimer(self)
        self._timer.setInterval(int(self._midi_latency))
        self._timer.timeout.connect(self.process_midi_input)

    def _read_configuration(self):
        # initialise defaults for MCU and hardware controller
        mcu_emulated_model_default = MackieHostControl.get_preferred_mcu_model()
        hardware_controller_default = 'Novation ZeRO SL MkII'
        midi_latency_default = '1'

        # retrieve user configuration for MCU and hardware controller
        self._mcu_emulated_model = configuration.get_option(
            'Python MCU', 'mcu_emulated_model', mcu_emulated_model_default)
        self._hardware_controller = configuration.get_option(
            'Python MCU', 'controller_hardware', hardware_controller_default)
        self._midi_latency = configuration.get_option(
            'Python MCU', 'midi_latency', midi_latency_default)

        # calculate MCU model ID from its name
        self._mcu_model_id = MackieHostControl.get_mcu_id_from_model(self._mcu_emulated_model)

        # Logic Control units use MCU challenge-response by default, ...
        if self._mcu_model_id in [0x10, 0x11]:
            mcu_connection_default = MackieHostControl.CHALLENGE_RESPONSE
        # whereas Mackie Control Units don't seem to use it
        else:
            mcu_connection_default = MackieHostControl.WAIT_FOR_MIDI_DATA

        self._mcu_connection = configuration.get_option(
            'Python MCU', 'mcu_connection', mcu_connection_default)

        # get preferred MIDI ports for hardware controller
        (controller_midi_input_default, controller_midi_output_default) = self._initialise_hardware_controller()

        # initialise MIDI port defaults for MCU and hardware
        # controller
        mcu_midi_input_default = MackieHostControl.get_preferred_midi_input()
        mcu_midi_output_default = MackieHostControl.get_preferred_midi_output()

        # retrieve user configuration for MCU's MIDI ports
        self._mcu_midi_input = configuration.get_option(
            'Python MCU', 'mcu_midi_input',
            mcu_midi_input_default
        )
        self._mcu_midi_output = configuration.get_option(
            'Python MCU', 'mcu_midi_output',
            mcu_midi_output_default
        )

        # retrieve user configuration for hardware controller's MIDI
        # ports
        self._controller_midi_input = configuration.get_option(
            'Python MCU', 'controller_midi_input',
            controller_midi_input_default
        )
        self._controller_midi_output = configuration.get_option(
            'Python MCU', 'controller_midi_output',
            controller_midi_output_default
        )

    def _create_combo_box(self, layout, selection, label_text, choices):
        row = layout.rowCount()

        label = QLabel(None)
        label.setText(label_text)
        layout.addWidget(label, row, 0)

        widget = QComboBox()
        layout.addWidget(widget, row, 1)

        choices.sort()
        widget.addItems(choices)

        current_index = widget.findText(selection)
        widget.setCurrentIndex(current_index)
        # noinspection PyUnresolvedReferences
        widget.currentIndexChanged.connect(self.combobox_item_selected)

        return widget

    def _enable_controls(self, state):
        self.frame_mcu.setEnabled(state)
        self.frame_controller.setEnabled(state)

    def _initialise_hardware_controller(self):
        # the hardware controller's class name is simply the
        # controller's manufacturer and name with all spaces
        # and all brackets removed
        self._hardware_controller_class = self._hardware_controller.replace(' ', '')
        self._hardware_controller_class = self._hardware_controller_class.replace('(', '').replace(')', '')
        self._hardware_controller_class = self._hardware_controller_class.replace('[', '').replace(']', '')
        self._hardware_controller_class = self._hardware_controller_class.replace('{', '').replace('}', '')

        # FIXME: factorize into factory method
        module = importlib.import_module('.' + self._hardware_controller_class, package='PythonMcu.Hardware')
        hw_class = getattr(module, self._hardware_controller_class)

        controller_midi_input_default = hw_class.get_preferred_midi_input()
        controller_midi_output_default = hw_class.get_preferred_midi_output()

        # show controller's usage hint
        self._edit_usage_hint.setPlainText(hw_class.get_usage_hint())

        return controller_midi_input_default, controller_midi_output_default

    def callback_log(self, message, repaint=False):
        if repaint:
            self._edit_logger.repaint()

        print(message)
        self._edit_logger.appendPlainText(message)

    def midiports_refresh(self):
        MidiPorts.refresh_ports()

        self._combo_controller_midi_input.clear()
        self._combo_controller_midi_input.addItems(MidiPorts.get_midi_inputs())

        self._combo_controller_midi_output.clear()
        self._combo_controller_midi_output.addItems(MidiPorts.get_midi_outputs())

    def combobox_item_selected(self):
        widget = self.sender()
        selected_text = widget.currentText()

        if widget == self._combo_mcu_model_id:
            self._mcu_emulated_model = selected_text
            configuration.set_option(
                'Python MCU', 'mcu_emulated_model',
                self._mcu_emulated_model
            )

            if self._mcu_emulated_model.startswith('Logic'):
                current_index = self._combo_mcu_connection.findText(MackieHostControl.CHALLENGE_RESPONSE)
            else:
                current_index = self._combo_mcu_connection.findText(MackieHostControl.WAIT_FOR_MIDI_DATA)
            self._combo_mcu_connection.setCurrentIndex(current_index)

        elif widget == self._combo_mcu_midi_input:
            self._mcu_midi_input = selected_text
            configuration.set_option(
                'Python MCU', 'mcu_midi_input',
                self._mcu_midi_input
            )
        elif widget == self._combo_mcu_midi_output:
            self._mcu_midi_output = selected_text
            configuration.set_option(
                'Python MCU', 'mcu_midi_output',
                self._mcu_midi_output
            )
        elif widget == self._combo_hardware_controller:
            self._hardware_controller = selected_text
            configuration.set_option(
                'Python MCU', 'controller_hardware',
                self._hardware_controller
            )

            # get preferred MIDI ports for hardware controller
            (controller_midi_input_default, controller_midi_output_default) = self._initialise_hardware_controller()

            # update hardware controller's MIDI ports in GUI
            current_index = self._combo_controller_midi_input.findText(controller_midi_input_default)
            self._combo_controller_midi_input.setCurrentIndex(current_index)

            current_index = self._combo_controller_midi_output.findText(controller_midi_output_default)
            self._combo_controller_midi_output.setCurrentIndex(current_index)
        elif widget == self._combo_controller_midi_input:
            self._controller_midi_input = selected_text
            configuration.set_option(
                'Python MCU', 'controller_midi_input',
                self._controller_midi_input
            )
        elif widget == self._combo_controller_midi_output:
            self._controller_midi_output = selected_text
            configuration.set_option(
                'Python MCU', 'controller_midi_output',
                self._controller_midi_output
            )
        elif widget == self._combo_mcu_connection:
            self._mcu_connection = selected_text
            configuration.set_option(
                'Python MCU', 'mcu_connection',
                self._mcu_connection
            )
        else:
            self.callback_log(f'QComboBox not handled ("{selected_text}").')

    def process_midi_input(self):
        self._interconnector.process_midi_input()

    def display_about(self):
        AboutDialog(self).show()

    def interconnector_start_stop(self):
        if not self._interconnector:
            self.button_start_stop.setText('&Starting...')
            self._enable_controls(False)

            self.callback_log('Settings')
            self.callback_log('========')
            self.callback_log(f'MCU emulation:  {self._mcu_emulated_model}')
            self.callback_log(f'Connection:     {self._mcu_connection}')
            self.callback_log(f'MIDI input:     {self._mcu_midi_input}')
            self.callback_log(f'MIDI output:    {self._mcu_midi_output}')
            self.callback_log('')
            self.callback_log(f'Controller:     {self._hardware_controller}')
            self.callback_log(f'MIDI input:     {self._controller_midi_input}')
            self.callback_log(f'MIDI output:    {self._controller_midi_output}')
            self.callback_log('')
            self.callback_log(f'MIDI latency:   {self._midi_latency} ms')
            self.callback_log('')
            self.callback_log('')

            if configuration.has_changed():
                self.callback_log('Saving configuration file ...')
                configuration.save_configuration()

            self.callback_log('Starting MCU emulation...')
            self.callback_log('', True)

            # the "interconnector" is the brain of this application -- it
            # interconnects Mackie Control Host and MIDI controller while
            # handling the complete MIDI translation between those two
            self._interconnector = McuInterconnector(
                self,
                self._mcu_model_id,
                self._mcu_connection,
                self._mcu_midi_input,
                self._mcu_midi_output,
                self._hardware_controller_class,
                self._controller_midi_input,
                self._controller_midi_output,
                self.callback_log
            )
            try:
                self._interconnector.connect()
            except ValueError as e:
                self.callback_log(f'Connecting failed with the following error: {e!r}')
                self._interconnector.disconnect()
                self. _interconnector = None
                self._enable_controls(True)
                self.button_start_stop.setText('&Start')
                return

            # We set the button after making sure we can connect
            self._enable_controls(False)
            self.button_start_stop.setText('&Stop')

            self._timer.start()
        else:
            self.button_start_stop.setText('&Stopping')

            self._interconnector_stop()

            # We set the button after making sure we can properly stop
            self._enable_controls(True)
            self.button_start_stop.setText('&Start')

    def _interconnector_stop(self):
        self._timer.stop()

        self.callback_log('')
        self.callback_log('Stopping MCU emulation...')
        self.callback_log('')

        self._interconnector.disconnect()
        self._interconnector = None

        self.callback_log('', True)

    def close_application(self):
        self.close()

    def close_event(self, _):
        if self._interconnector:
            self._interconnector_stop()

        self.callback_log('Exiting application...')
        self.callback_log('', True)


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication()

    # Create and show the form
    python_mcu = PythonMcuApp()
    python_mcu.show()

    # Run the main Qt loop
    sys.exit(app.exec())
