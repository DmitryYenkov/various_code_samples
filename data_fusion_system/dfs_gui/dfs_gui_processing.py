import os
import json
import shutil
import subprocess
from copy import deepcopy
import time

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import uic

import xml.etree.ElementTree as Xml_ET
import xmltodict

from dfs_gui_settings import SettingsGui
import utils


class ProcessorGui(QtWidgets.QWidget):

    def __init__(self, x, y, w):

        super().__init__()

        self.python_path = utils.join(utils.root_folder, 'ins_gps_project', 'python', 'python')
        self.script = utils.join(utils.root_folder, 'ins_gps_project',
                                 'sources', 'fusion_filter', 'sensor_processing.py')
        self.script_arg = utils.join(utils.root_folder, 'ins_gps_project', 'sources',
                                     'dfs_gui', utils.cfg_filename)
        self.log_file = utils.join(utils.root_folder, 'ins_gps_project',
                                   'sources', 'dfs_gui', 'processing_log.txt')

        if os.path.isfile(utils.cfg_filename):
            with open(utils.cfg_filename, 'r') as cfg:
                self.paths = json.load(cfg)
        else:
            self.paths = dict()

        uic.loadUi(utils.join('ui', 'Processing.ui'), self)

        file = self.paths.get('processing_scenario', '')
        self.scenario_file = file if os.path.isfile(file) else ''
        self.scenario_line.setText(self.scenario_file)
        file = self.paths.get('processing_settings', '')
        self.settings_file = file if os.path.isfile(file) else ''
        self.settings_line.setText(self.settings_file)

        self.show_sensors_used()

        folder = self.paths.get('processing_data', '')
        self.data_path = folder if os.path.isdir(folder) else ''
        self.data_folder_line.setText(self.data_path)
        folder = self.paths.get('processing_results', '')
        self.result_path = folder if os.path.isdir(folder) else ''
        self.result_folder_line.setText(self.result_path)

        self.scenario_open_button.clicked.connect(self.open_scenario)
        self.settings_open_button.clicked.connect(self.open_settings)
        self.data_folder_select_button.clicked.connect(self.open_data_path)
        self.result_folder_select_button.clicked.connect(self.open_result_path)
        self.edit_settings_button.clicked.connect(self.edit_settings)
        self.process_button.clicked.connect(self.process)
        self.create_folder_checkbox.stateChanged.connect(self.set_folder)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.display_process)

        self.status_line.setText('Idle')

        self.setFixedSize(self.geometry().width(), self.geometry().height())
        self.move(x + w + 17, y)
        self.show()

        self.settings_dialog = None
        self.pid = None

    def set_folder(self):
        if self.create_folder_checkbox.isChecked():
            if self.result_folder_line.text() == '':
                self.result_path = deepcopy(self.data_path)
            else:
                self.result_path = utils.join(self.result_path,
                                              os.path.split(self.data_path)[-1])
        else:
            self.result_path = self.paths['processing_results']
        self.result_folder_line.setText(self.result_path)

    def process(self):
        if self.pid is None:
            if (not os.path.isdir(self.result_path)) or (not os.path.isdir(self.data_path)):
                utils.show_error('Data or result paths not set!')
                return
            if not os.path.isdir(self.result_path):
                os.mkdir(self.result_path)

            self.paths['processing_results'] = self.result_path
            utils.save_cfg(self.paths)

            self.process_button.setText('STOP')

            self.pid = subprocess.Popen([self.python_path, self.script, '--cfg', self.script_arg])
            time.sleep(1)
            self.timer.start(1000)

            settings_file_name = utils.join(self.result_path, os.path.basename(self.settings_file))
            scenario_file_name = utils.join(self.result_path, os.path.basename(self.scenario_file))
            shutil.copyfile(self.settings_file, settings_file_name)
            shutil.copyfile(self.scenario_file, scenario_file_name)
        else:
            self.pid.terminate()
            self.pid = None
            self.timer.stop()
            self.process_button.setText('PROCESS')
            self.status_line.setText('Idle')
            self.processing_progress_bar.setValue(0)

    def display_process(self):
        f = open(self.log_file, 'r')
        lines = f.readlines()
        f.close()
        if len(lines) > 0:
            last_line = lines[-1].strip()
            if last_line.isdigit():
                self.processing_progress_bar.setValue(int(last_line))
            else:
                if 'Done' in last_line:
                    self.pid = None
                    self.timer.stop()
                    self.process_button.setText('PROCESS')
                    self.status_line.setText('Idle')
                    self.processing_progress_bar.setValue(0)
                else:
                    self.status_line.setText(last_line)

    def edit_settings(self):
        self.setWindowModality(QtCore.Qt.NonModal)
        self.settings_dialog = SettingsGui(self.geometry().x(), self.geometry().y(),
                                           self.settings_file, self.scenario_file)
        self.settings_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.settings_dialog.out_signals.out_settings_file.connect(self.set_settings_file)

    def open_scenario(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        open_path = self.paths.get('processing_scenario', '')
        if not os.path.isdir(open_path):
            open_path = ''
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            'Open XML file',
                                                            open_path,
                                                            'xml (*.xml)',
                                                            options=options)
        if filename:
            self.paths['processing_scenario'] = filename
            self.scenario_file = self.paths['processing_scenario']
            self.scenario_line.setText(self.paths['processing_scenario'])

    def open_settings(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        open_path = self.paths.get('processing_settings', '')
        if not os.path.isdir(open_path):
            open_path = ''
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            'Open XML file',
                                                            open_path,
                                                            'xml (*.xml)',
                                                            options=options)
        if filename:
            self.set_settings_file(filename)

    def set_settings_file(self, filename):

        self.paths['processing_settings'] = filename
        self.settings_file = self.paths['processing_settings']
        self.settings_line.setText(self.paths['processing_settings'])
        self.show_sensors_used()

    def show_sensors_used(self):
        if os.path.isfile(self.settings_file):
            xml_data = Xml_ET.parse(self.settings_file).getroot()
        else:
            utils.show_error('XML File Error!')
            return
        xml_str = Xml_ET.tostring(xml_data, encoding='utf-8', method='xml')
        settings = dict(xmltodict.parse(xml_str))
        sensors_used = len(settings['processing_params']['sensors_used'])
        self.sensors_used_line.setText(str(sensors_used))
        users = len(settings['processing_params']['users'])
        self.users_total_line.setText(str(users))

    def open_data_path(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        open_path = self.paths.get('processing_data', '')
        if not os.path.isdir(open_path):
            open_path = ''
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                             'Select Folder',
                                                             os.path.split(open_path)[0],
                                                             options=options)
        if dirname:
            self.paths['processing_data'] = dirname
            self.data_folder_line.setText(self.paths['processing_data'])
            self.data_path = self.paths['processing_data']

    def open_result_path(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        open_path = self.paths.get('processing_results', '')
        if not os.path.isdir(open_path):
            open_path = ''
        dirname = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                             'Select Folder',
                                                             os.path.split(open_path)[0],
                                                             options=options)
        if dirname:
            self.paths['processing_results'] = dirname
            self.result_folder_line.setText(self.paths['processing_results'])
            self.result_path = self.paths['processing_results']

    def closeEvent(self, event):

        utils.save_cfg(self.paths)
