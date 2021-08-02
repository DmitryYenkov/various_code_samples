from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import uic

import xml.etree.ElementTree as Xml_ET
import xmltodict
from collections import OrderedDict
import os

import utils
from dfs_gui_sensor_cfg import ellipsoid_official_names
from dfs_gui_sensor_cfg import ellipsoids
from dfs_gui_sensors_select import SensorsSelectGui
from dfs_gui_users import UsersTableGui


class ProcSettingsOutSignals(QtCore.QObject):

    out_settings_file = QtCore.pyqtSignal(str)


class SettingsGui(QtWidgets.QWidget):

    def __init__(self, x, y, settings_filename, scenario_filename):

        super().__init__()
        uic.loadUi('ui/Settings.ui', self)
        self.out_signals = ProcSettingsOutSignals()

        self.settings_file = settings_filename
        self.scenario = scenario_filename

        self.scenario_params = OrderedDict()
        self.settings_ = OrderedDict()
        self.settings = OrderedDict()
        self.sensors_list = None
        self.selected_list = []
        self.users_table = None
        self.users_dict = dict()

        self.save_as_button.clicked.connect(self.save_changes_as)
        self.save_button.clicked.connect(self.save_changes)
        self.sensors_button.clicked.connect(self.select_sensors)
        self.users_button.clicked.connect(self.config_users)
        self.srns_flt_checkbox.stateChanged.connect(self.select_srns_flt)

        self.revert_changes()

        self.sensors_line.setText(str(len(self.selected_list)))

        self.move(x - 100, y + 100)
        self.show()

    def revert_changes(self):

        if not os.path.isfile(self.scenario):
            return

        xml_data = Xml_ET.parse(self.scenario).getroot()
        xml_str = Xml_ET.tostring(xml_data, encoding='utf-8', method='xml')
        self.scenario_params = dict(xmltodict.parse(xml_str))
        self.scenario_params = self.scenario_params['params']

        dt_min = min([float(v['dt']) for v in self.scenario_params['sensors'].values()])
        self.model_time_line.setText(str(dt_min))

        self.latitude_line.setText(self.scenario_params['location']['latitude'])
        self.longitude_line.setText(self.scenario_params['location']['longitude'])
        self.height_line.setText(self.scenario_params['location']['height'])
        ell = ellipsoid_official_names[ellipsoids.index(self.scenario_params['ell'])]
        self.ellipsoid_line.setText(ell)
        self.course_line.setText(self.scenario_params['course'])
        self.roll_line.setText('0')
        self.pitch_line.setText('0')

        if not os.path.isfile(self.settings_file):
            return

        xml_data = Xml_ET.parse(self.settings_file).getroot()
        xml_str = Xml_ET.tostring(xml_data, encoding='utf-8', method='xml')
        self.settings_ = dict(xmltodict.parse(xml_str))
        self.settings = self.settings_['processing_params']

        self.out_ellipsoid_combo.setCurrentIndex(ellipsoids.index(self.settings['out_ell']))
        self.pos_sigma_line.setText(self.settings['ckf_params']['pos_sigma']['x'])
        self.pos_sigma_line_2.setText(self.settings['ckf_params']['pos_sigma']['y'])
        self.pos_sigma_line_3.setText(self.settings['ckf_params']['pos_sigma']['z'])
        self.speed_sigma_line.setText(self.settings['ckf_params']['speed_sigma']['x'])
        self.speed_sigma_line_2.setText(self.settings['ckf_params']['speed_sigma']['y'])
        self.speed_sigma_line_3.setText(self.settings['ckf_params']['speed_sigma']['z'])
        self.acc_sigma_line.setText(self.settings['ckf_params']['acc_sigma']['x'])
        self.acc_sigma_line_2.setText(self.settings['ckf_params']['acc_sigma']['y'])
        self.acc_sigma_line_3.setText(self.settings['ckf_params']['acc_sigma']['z'])
        self.acc_bias_line.setText(self.settings['ckf_params']['acc_bias']['x'])
        self.acc_bias_line_2.setText(self.settings['ckf_params']['acc_bias']['y'])
        self.acc_bias_line_3.setText(self.settings['ckf_params']['acc_bias']['z'])
        self.gyro_sigma_line.setText(self.settings['ckf_params']['gyro_sigma']['x'])
        self.gyro_sigma_line_2.setText(self.settings['ckf_params']['gyro_sigma']['y'])
        self.gyro_sigma_line_3.setText(self.settings['ckf_params']['gyro_sigma']['z'])
        self.gyro_bias_line.setText(self.settings['ckf_params']['gyro_sigma']['x'])
        self.gyro_bias_line_2.setText(self.settings['ckf_params']['gyro_sigma']['y'])
        self.gyro_bias_line_3.setText(self.settings['ckf_params']['gyro_sigma']['z'])
        srns_flt = self.settings.get('srns_flt', None)
        if srns_flt is None:
            self.srns_flt_checkbox.setChecked(False)
            self.q_pos_line.setText('')
            self.r_pos_line.setText('')
        else:
            if srns_flt == '0':
                self.srns_flt_checkbox.setChecked(False)
                self.q_pos_line.setEnabled(False)
                self.r_pos_line.setEnabled(False)
            else:
                self.srns_flt_checkbox.setChecked(True)
                self.q_pos_line.setEnabled(True)
                self.r_pos_line.setEnabled(True)
            params = self.settings.get('srns_flt_params', None)
            if params is None:
                self.q_pos_line.setText('')
                self.r_pos_line.setText('')
            else:
                self.q_pos_line.setText(self.settings['srns_flt_params']['q_pos_noise'])
                self.r_pos_line.setText(self.settings['srns_flt_params']['r_pos_noise'])

        self.update_selected_list(self.settings['sensors_used'])
        self.update_users_table(self.settings.get('users', dict()))

    def save_changes_as(self):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                            'Save XML file',
                                                            os.path.split(self.settings_file)[0],
                                                            'xml (*.xml)',
                                                            options=options)
        if filename:
            self.settings_file = filename if filename.endswith('.xml') else filename + '.xml'
            self.save_changes()

    def save_changes(self):

        self.update_settings()
        self.settings_['processing_params'] = self.settings

        if self.settings_file == '':
            self.save_changes_as()
            return

        with open(self.settings_file, 'w') as f:
            f.write(xmltodict.unparse(self.settings_, full_document=True, pretty=True))

        self.out_signals.out_settings_file.emit(self.settings_file)

    def select_sensors(self):

        total_list = list(self.scenario_params['sensors'].keys())
        self.setWindowModality(QtCore.Qt.NonModal)
        self.sensors_list = SensorsSelectGui(self.geometry().x(), self.geometry().y(),
                                             total_list, self.selected_list)
        self.sensors_list.setWindowModality(QtCore.Qt.ApplicationModal)
        self.sensors_list.out_signals.out_selected.connect(self.update_selected_list)

    def update_selected_list(self, msg):

        self.selected_list = msg
        self.sensors_line.setText(str(len(self.selected_list)))

    def config_users(self):

        self.setWindowModality(QtCore.Qt.NonModal)
        self.users_table = UsersTableGui(self.geometry().x(), self.geometry().y(),
                                         self.users_dict)
        self.users_table.setWindowModality(QtCore.Qt.ApplicationModal)
        self.users_table.out_signals.out_sensors_dict.connect(self.update_users_table)

    def update_users_table(self, users_dict):

        self.users_dict = users_dict
        self.users_total_line.setText(str(len(self.users_dict)))

    def select_srns_flt(self):
        if self.srns_flt_checkbox.isChecked():
            self.settings['srns_flt'] = 1
            self.q_pos_line.setEnabled(True)
            self.r_pos_line.setEnabled(True)
        else:
            self.settings['srns_flt'] = 0
            self.q_pos_line.setEnabled(False)
            self.r_pos_line.setEnabled(False)

    def update_settings(self):

        conditions = [
            self.pos_sigma_line.text() == '',
            self.pos_sigma_line_2.text() == '',
            self.pos_sigma_line_3.text() == '',
            self.speed_sigma_line.text() == '',
            self.speed_sigma_line_2.text() == '',
            self.speed_sigma_line_3.text() == '',
            self.acc_sigma_line.text() == '',
            self.acc_sigma_line_2.text() == '',
            self.acc_sigma_line_3.text() == '',
            self.acc_bias_line.text() == '',
            self.acc_bias_line_2.text() == '',
            self.acc_bias_line_3.text() == '',
            self.gyro_sigma_line.text() == '',
            self.gyro_sigma_line_2.text() == '',
            self.gyro_sigma_line_3.text() == '',
            self.gyro_bias_line.text() == '',
            self.gyro_bias_line_2.text() == '',
            self.gyro_bias_line_3.text() == '',
            self.q_pos_line.text() == '',
            self.r_pos_line.text() == ''
        ]

        if any(conditions):
            utils.show_error('Filter parameters not set properly!')
            return

        self.settings['out_ell'] = ellipsoids[self.out_ellipsoid_combo.currentIndex()]
        self.settings['ckf_params'] = OrderedDict()
        self.settings['ckf_params']['pos_sigma'] = OrderedDict()
        self.settings['ckf_params']['pos_sigma']['x'] = self.pos_sigma_line.text()
        self.settings['ckf_params']['pos_sigma']['y'] = self.pos_sigma_line_2.text()
        self.settings['ckf_params']['pos_sigma']['z'] = self.pos_sigma_line_3.text()
        self.settings['ckf_params']['speed_sigma'] = OrderedDict()
        self.settings['ckf_params']['speed_sigma']['x'] = self.speed_sigma_line.text()
        self.settings['ckf_params']['speed_sigma']['y'] = self.speed_sigma_line_2.text()
        self.settings['ckf_params']['speed_sigma']['z'] = self.speed_sigma_line_3.text()
        self.settings['ckf_params']['acc_sigma'] = OrderedDict()
        self.settings['ckf_params']['acc_sigma']['x'] = self.acc_sigma_line.text()
        self.settings['ckf_params']['acc_sigma']['y'] = self.acc_sigma_line_2.text()
        self.settings['ckf_params']['acc_sigma']['z'] = self.acc_sigma_line_3.text()
        self.settings['ckf_params']['acc_bias'] = OrderedDict()
        self.settings['ckf_params']['acc_bias']['x'] = self.acc_bias_line.text()
        self.settings['ckf_params']['acc_bias']['y'] = self.acc_bias_line_2.text()
        self.settings['ckf_params']['acc_bias']['z'] = self.acc_bias_line_3.text()
        self.settings['ckf_params']['gyro_sigma'] = OrderedDict()
        self.settings['ckf_params']['gyro_sigma']['x'] = self.gyro_sigma_line.text()
        self.settings['ckf_params']['gyro_sigma']['y'] = self.gyro_sigma_line_2.text()
        self.settings['ckf_params']['gyro_sigma']['z'] = self.gyro_sigma_line_3.text()
        self.settings['ckf_params']['gyro_bias'] = OrderedDict()
        self.settings['ckf_params']['gyro_bias']['x'] = self.gyro_bias_line.text()
        self.settings['ckf_params']['gyro_bias']['y'] = self.gyro_bias_line_2.text()
        self.settings['ckf_params']['gyro_bias']['z'] = self.gyro_bias_line_3.text()
        self.settings['srns_flt'] = 1 if self.srns_flt_checkbox.isChecked() else 0
        self.settings['srns_flt_params'] = OrderedDict()
        self.settings['srns_flt_params']['q_pos_noise'] = self.q_pos_line.text()
        self.settings['srns_flt_params']['r_pos_noise'] = self.r_pos_line.text()
        self.settings['sensors_used'] = self.selected_list
        self.settings['users'] = self.users_dict

    def closeEvent(self, event):

        if self.sensors_list is not None:
            self.setWindowModality(QtCore.Qt.ApplicationModal)

        if self.users_table is not None:
            self.setWindowModality(QtCore.Qt.ApplicationModal)
