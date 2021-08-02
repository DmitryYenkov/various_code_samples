from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import uic

import xml.etree.ElementTree as Xml_ET
import xmltodict
import os
import json
from copy import deepcopy
from collections import OrderedDict

from dfs_gui_sensors import SensorsTableGui
from dfs_gui_sensor_cfg import ellipsoid_indices
from dfs_gui_sensor_cfg import ellipsoid_names


# def dict_compare(d1, d2):
#     d1_keys = set(d1.keys())
#     d2_keys = set(d2.keys())
#     shared_keys = d1_keys.intersection(d2_keys)
#     added = d1_keys - d2_keys
#     removed = d2_keys - d1_keys
#     modified = {o : (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
#     same = set(o for o in shared_keys if d1[o] == d2[o])
#     return modified


class ScenarioCfgOutSignals(QtCore.QObject):

    out_new_scenario = QtCore.pyqtSignal(str)


class ScenarioGui(QtWidgets.QWidget):

    def __init__(self, x, y, filename):

        super().__init__()
        self.out_signals = ScenarioCfgOutSignals()
        self.scenario = filename
        self.settings_ = dict()
        self.settings = dict()
        self.sensors_table = None

        uic.loadUi('ui/Scenario.ui', self)

        self.revert_changes()
        self.save_as_button.clicked.connect(self.save_changes_as)
        self.save_button.clicked.connect(self.save_changes)
        self.sensors_button.clicked.connect(self.config_sensors)
        self.wave_period_slider.valueChanged[int].connect(self.set_wave_period)
        self.wave_height_slider.valueChanged[int].connect(self.set_wave_height)

        self.move(x + 100, y - 100)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.show()

    def revert_changes(self):

        xml_data = Xml_ET.parse(self.scenario).getroot()
        xml_str = Xml_ET.tostring(xml_data, encoding='utf-8', method='xml')
        self.settings_ = dict(xmltodict.parse(xml_str))
        self.settings = deepcopy(self.settings_['params'])

        if self.settings['sensors'] is None:
            self.settings['sensors'] = dict()
        self.sensors_total_line.setText(str(len(self.settings['sensors'])))
        if len(self.settings['sensors']) > 0:
            dt_min = min([float(v['dt']) for v in self.settings['sensors'].values()])
            self.min_dt_line.setText(str(dt_min))
        else:
            self.min_dt_line.setText('0')

        self.latitude_line.setText(self.settings['location']['latitude'])
        self.longitude_line.setText(self.settings['location']['longitude'])
        self.height_line.setText(self.settings['location']['height'])
        self.ellipsoid_combo.setCurrentIndex(ellipsoid_indices[self.settings['ell']])
        self.course_line.setText(self.settings['course'])
        self.roll_line.setText('0')
        self.pitch_line.setText('0')
        self.model_time_line.setText(str(int(float(self.settings['Tmod']) * 60)))
        self.motion_seed_line.setText(self.settings['seed'])
        self.loss_prob_line.setText(self.settings['srns_loss_prob'])
        self.min_loss_time_line.setText(self.settings['srns_loss_time']['min'])
        self.max_loss_time_line.setText(self.settings['srns_loss_time']['max'])
        #
        self.min_speed_line.setText(self.settings['v_lim']['min'])
        self.max_speed_line.setText(self.settings['v_lim']['max'])
        self.min_radius_line.setText(self.settings['r_lim']['min'])
        self.max_radius_line.setText(self.settings['r_lim']['max'])
        self.min_straight_line.setText(self.settings['t_lim']['min'])
        self.max_straight_line.setText(self.settings['t_lim']['max'])

        self.acc_prob_line.setText(self.settings['acc_prob'])
        self.zero_start_speed_checkbox.setChecked(self.settings['init_acc'] == 1)
        self.wave_period_line.setText(self.settings['wave_t'])
        self.wave_height_line.setText(self.settings['wave_h'])
        self.wave_period_slider.setValue(int((float(self.settings['wave_t']) - 3) * 2.5))
        self.wave_height_slider.setValue(int((float(self.settings['wave_h']) - 1) * 2))

    def set_wave_period(self, val):
        self.wave_period_line.setText(str(round(3 + val / 2.5, 1)))

    def set_wave_height(self, val):
        self.wave_height_line.setText(str(round((1 + val) / 2, 1)))

    def save_changes_as(self):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                            'Save XML file',
                                                            os.path.split(self.scenario)[0],
                                                            'xml (*.xml)',
                                                            options=options)
        if filename:
            self.scenario = filename if filename.endswith('.xml') else filename + '.xml'
            self.save_changes()

    def update_settings(self):
        self.settings['location'] = OrderedDict()
        self.settings['location']['latitude'] = self.latitude_line.text()
        self.settings['location']['longitude'] = self.longitude_line.text()
        self.settings['location']['height'] = self.height_line.text()
        self.settings['ell'] = ellipsoid_names[self.ellipsoid_combo.currentIndex()]
        self.settings['Tmod'] = str(float(self.model_time_line.text()) / 60)
        self.settings['course'] = self.course_line.text()
        self.settings['seed'] = self.motion_seed_line.text()
        self.settings['srns_loss_prob'] = self.loss_prob_line.text()
        self.settings['srns_loss_time'] = OrderedDict()
        self.settings['srns_loss_time']['min'] = self.min_loss_time_line.text()
        self.settings['srns_loss_time']['max'] = self.max_loss_time_line.text()
        self.settings['v_lim'] = OrderedDict()
        self.settings['v_lim']['min'] = self.min_speed_line.text()
        self.settings['v_lim']['max'] = self.max_speed_line.text()
        self.settings['r_lim'] = OrderedDict()
        self.settings['r_lim']['min'] = self.min_radius_line.text()
        self.settings['r_lim']['max'] = self.max_radius_line.text()
        self.settings['t_lim'] = OrderedDict()
        self.settings['t_lim']['min'] = self.min_straight_line.text()
        self.settings['t_lim']['max'] = self.max_straight_line.text()
        self.settings['acc_prob'] = self.acc_prob_line.text()
        self.settings['init_acc'] = '0' if self.zero_start_speed_checkbox.checkState() == 0 else '1'
        self.settings['wave_t'] = self.wave_period_line.text()
        self.settings['wave_h'] = self.wave_height_line.text()

    def save_changes(self):

        self.update_settings()
        self.settings_['params'] = self.settings

        with open(self.scenario, 'w') as f:
            f.write(xmltodict.unparse(self.settings_, full_document=True, pretty=True))

        self.out_signals.out_new_scenario.emit(self.scenario)

    def config_sensors(self):
        self.setWindowModality(QtCore.Qt.NonModal)
        self.sensors_table = SensorsTableGui(self.geometry().x(), self.geometry().y(),
                                             self.settings['sensors'])
        self.sensors_table.setWindowModality(QtCore.Qt.ApplicationModal)
        self.sensors_table.out_signals.out_sensors_dict.connect(self.update_sensors)

    def update_sensors(self, msg):
        self.settings['sensors'] = msg
        self.sensors_total_line.setText(str(len(self.settings['sensors'])))

    def closeEvent(self, event):

        if self.sensors_table is not None:
            self.sensors_table.setWindowModality(QtCore.Qt.NonModal)
            self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.update_settings()
        dict1 = json.dumps(self.settings_['params'])
        dict2 = json.dumps(self.settings)
        if dict1 != dict2:
            close = QtWidgets.QMessageBox()
            msg = 'Are you sure you want to close window?\n' + \
                  '(unsaved settings will be lost!)'
            close.setText(msg)
            close.setWindowTitle('Close scenario settings')
            close.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
            close = close.exec()

            if close == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
