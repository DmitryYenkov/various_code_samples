from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import xml.etree.ElementTree as Xml_ET
import xmltodict

from collections import OrderedDict


class Tab1OutSignals(QtCore.QObject):

    out_signal1 = QtCore.pyqtSignal(dict)
    out_signal2 = QtCore.pyqtSignal(str)


class GeneralSettingsTab(QtWidgets.QWidget):

    def __init__(self, parent, open_path):
        super().__init__(parent)

        self.open_path = open_path

        self.settings = dict()
        self.settings_ = dict()

        self.latitude_text = QtWidgets.QLineEdit(parent)
        self.longitude_text = QtWidgets.QLineEdit(parent)
        self.height_text = QtWidgets.QLineEdit(parent)
        self.ellipsoid_text = QtWidgets.QLineEdit(parent)
        self.t_mod_text = QtWidgets.QLineEdit(parent)
        self.course_text = QtWidgets.QLineEdit(parent)
        self.seed_text = QtWidgets.QLineEdit(parent)
        self.srns_loss_prob_text = QtWidgets.QLineEdit(parent)
        self.srns_loss_time_text = QtWidgets.QLineEdit(parent)
        self.rr_number_max_text = QtWidgets.QLineEdit(parent)
        self.rr_number_min_text = QtWidgets.QLineEdit(parent)
        self.rr_speed_max_text = QtWidgets.QLineEdit(parent)
        self.rr_speed_min_text = QtWidgets.QLineEdit(parent)
        self.rr_radius_max_text = QtWidgets.QLineEdit(parent)
        self.rr_radius_min_text = QtWidgets.QLineEdit(parent)
        self.rr_time_max_text = QtWidgets.QLineEdit(parent)
        self.rr_time_min_text = QtWidgets.QLineEdit(parent)
        self.sensors_num = QtWidgets.QLineEdit(parent)
        self.users_num = QtWidgets.QLineEdit(parent)
        self.min_dt = QtWidgets.QLineEdit(parent)
        self.xml_file_path = QtWidgets.QLineEdit(parent)
        self.open_xml_filename = ''

        self.out_signals = Tab1OutSignals()

        self.general_settings_tab_layout(parent)

    def general_settings_tab_layout(self, parent):

        layout = QtWidgets.QGridLayout(parent)
        layout.setSpacing(5)

        dummy_label = QtWidgets.QLabel('', parent)
        label_color = dummy_label.palette().color(QtGui.QPalette.Background)
        text_palette = dummy_label.palette()
        text_palette.setColor(dummy_label.backgroundRole(), label_color)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        location_label = QtWidgets.QLabel('Geographical location:', parent)
        location_label.setFont(bold_font)
        location_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        latitude_label = QtWidgets.QLabel('Latitude:', parent)
        latitude_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.latitude_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.latitude_text.setText('0.0')

        longitude_label = QtWidgets.QLabel('Longitude:', parent)
        longitude_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.longitude_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.longitude_text.setText('0.0')

        height_label = QtWidgets.QLabel('Height:', parent)
        height_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.height_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.height_text.setText('0.0')

        ellipsoid_label = QtWidgets.QLabel('Ellipsoid:', parent)
        ellipsoid_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.ellipsoid_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.ellipsoid_text.setText('unitsphere')

        start_params_label = QtWidgets.QLabel('Movement initial parameters:', parent)
        start_params_label.setFont(bold_font)
        start_params_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        t_mod_label = QtWidgets.QLabel('Time, min:', parent)
        t_mod_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.t_mod_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.t_mod_text.setText('0')

        course_label = QtWidgets.QLabel('Course, deg:', parent)
        course_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.course_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.course_text.setText('0')

        random_force_label = QtWidgets.QLabel('Random components generation parameters:', parent)
        random_force_label.setFont(bold_font)
        random_force_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        srns_los_param_label = QtWidgets.QLabel('SRNS Loss parameters:', parent)
        srns_los_param_label.setFont(bold_font)
        srns_los_param_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        seed_label = QtWidgets.QLabel('seed:', parent)
        seed_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.seed_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.seed_text.setText('0')

        srns_loss_prob_label = QtWidgets.QLabel('Loss prob.:', parent)
        srns_loss_prob_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.srns_loss_prob_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.srns_loss_prob_text.setText('0')

        srns_loss_time_label = QtWidgets.QLabel('Loss time:', parent)
        srns_loss_time_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.srns_loss_time_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.srns_loss_time_text.setText('0,0')

        random_route_label = QtWidgets.QLabel('Random route parameters:', parent)
        random_route_label.setFont(bold_font)
        random_route_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        rr_number_label = QtWidgets.QLabel('Maneuvers #:', parent)
        rr_number_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_number_max_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_number_max_text.setText('10')
        self.rr_number_min_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_number_min_text.setText('20')

        rr_speed_label = QtWidgets.QLabel('Speed limits:', parent)
        rr_speed_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_speed_max_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_speed_max_text.setText('5')
        self.rr_speed_min_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_speed_min_text.setText('10')

        rr_radius_label = QtWidgets.QLabel('Radius limits:', parent)
        rr_radius_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_radius_max_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_radius_max_text.setText('500')
        self.rr_radius_min_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_radius_min_text.setText('1000')

        rr_time_label = QtWidgets.QLabel('Time intervals:', parent)
        rr_time_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_time_max_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_time_max_text.setText('1000')
        self.rr_time_min_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.rr_time_min_text.setText('2000')

        sensors_num_label = QtWidgets.QLabel('Sensors:', parent)
        sensors_num_label.setFont(bold_font)
        sensors_num_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.sensors_num.setText('0')
        self.sensors_num.setEnabled(False)
        users_num_label = QtWidgets.QLabel('Users:', parent)
        users_num_label.setFont(bold_font)
        users_num_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.users_num.setText('0')
        self.users_num.setEnabled(False)
        min_dt_label = QtWidgets.QLabel('Min. timestep:', parent)
        min_dt_label.setFont(bold_font)
        min_dt_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.min_dt.setText('0')
        self.min_dt.setEnabled(False)

        xml_file_label = QtWidgets.QLabel('XML File:', parent)
        xml_file_label.setFont(bold_font)
        xml_file_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.xml_file_path.setText('not selected')
        self.xml_file_path.setEnabled(False)

        open_xml_button = QtWidgets.QPushButton('Open XML File', parent)
        open_xml_func = lambda: self.open_xml_lambda(parent)
        open_xml_button.clicked.connect(open_xml_func)

        revert_changes_button = QtWidgets.QPushButton('Revert Changes', parent)
        revert_changes_func = lambda: self.revert_changes_lambda()
        revert_changes_button.clicked.connect(revert_changes_func)

        save_xml_button = QtWidgets.QPushButton('Save XML File', parent)
        save_xml_func = lambda: self.save_xml_lambda(parent)
        save_xml_button.clicked.connect(save_xml_func)

        layout.addWidget(location_label, 0, 0, 1, 8)
        layout.addWidget(latitude_label, 1, 0, 1, 2)
        layout.addWidget(self.latitude_text, 1, 2, 1, 2)
        layout.addWidget(longitude_label, 1, 4, 1, 2)
        layout.addWidget(self.longitude_text, 1, 6, 1, 2)
        layout.addWidget(height_label, 2, 0, 1, 2)
        layout.addWidget(self.height_text, 2, 2, 1, 2)
        layout.addWidget(ellipsoid_label, 2, 4, 1, 2)
        layout.addWidget(self.ellipsoid_text, 2, 6, 1, 2)

        layout.addWidget(start_params_label, 3, 0, 1, 8)
        layout.addWidget(t_mod_label, 4, 0, 1, 2)
        layout.addWidget(self.t_mod_text, 4, 2, 1, 2)
        layout.addWidget(course_label, 4, 4, 1, 2)
        layout.addWidget(self.course_text, 4, 6, 1, 2)

        layout.addWidget(random_force_label, 5, 0, 1, 5)
        layout.addWidget(srns_los_param_label, 5, 5, 1, 3)
        layout.addWidget(srns_loss_prob_label, 6, 5, 1, 2)
        layout.addWidget(self.srns_loss_prob_text, 6, 7, 1, 1)
        layout.addWidget(seed_label, 6, 0, 1, 1)
        layout.addWidget(self.seed_text, 6, 1, 1, 2)
        layout.addWidget(srns_loss_time_label, 7, 5, 1, 2)
        layout.addWidget(self.srns_loss_time_text, 7, 7, 1, 1)

        layout.addWidget(random_route_label, 8, 0, 1, 8)
        layout.addWidget(rr_number_label, 9, 0, 1, 2)
        layout.addWidget(rr_speed_label, 9, 2, 1, 2)
        layout.addWidget(rr_radius_label, 9, 4, 1, 2)
        layout.addWidget(rr_time_label, 9, 6, 1, 2)
        layout.addWidget(self.rr_number_min_text, 10, 0, 1, 2)
        layout.addWidget(self.rr_speed_min_text, 10, 2, 1, 2)
        layout.addWidget(self.rr_radius_min_text, 10, 4, 1, 2)
        layout.addWidget(self.rr_time_min_text, 10, 6, 1, 2)
        layout.addWidget(self.rr_number_max_text, 11, 0, 1, 2)
        layout.addWidget(self.rr_speed_max_text, 11, 2, 1, 2)
        layout.addWidget(self.rr_radius_max_text, 11, 4, 1, 2)
        layout.addWidget(self.rr_time_max_text, 11, 6, 1, 2)

        layout.addWidget(sensors_num_label, 12, 0, 1, 1)
        layout.addWidget(self.sensors_num, 12, 1, 1, 1)
        layout.addWidget(users_num_label, 12, 2, 1, 1)
        layout.addWidget(self.users_num, 12, 3, 1, 1)
        layout.addWidget(min_dt_label, 12, 4, 1, 3)
        layout.addWidget(self.min_dt, 12, 7, 1, 1)

        layout.addWidget(xml_file_label, 13, 0, 1, 8)
        layout.addWidget(self.xml_file_path, 14, 0, 1, 8)
        layout.addWidget(open_xml_button, 15, 0, 1, 2)
        layout.addWidget(revert_changes_button, 15, 2, 1, 4)
        layout.addWidget(save_xml_button, 15, 6, 1, 2)

        self.out_signals.out_signal1.emit(self.settings.get('sensors', dict()))

        parent.setLayout(layout)

    def open_xml_lambda(self, parent):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(parent,
                                                            'Open XML file',
                                                            self.open_path,
                                                            'xml (*.xml)',
                                                            options=options)
        if filename:
            self.open_xml_filename = filename
            self.xml_file_path.setText(self.open_xml_filename)
            self.revert_changes_lambda()
            self.out_signals.out_signal2.emit(self.open_xml_filename)
        else:
            return

    def revert_changes_lambda(self):

        if not self.open_xml_filename:
            return
        xml_data = Xml_ET.parse(self.open_xml_filename).getroot()
        xml_str = Xml_ET.tostring(xml_data, encoding='utf-8', method='xml')
        self.settings_ = dict(xmltodict.parse(xml_str))
        self.settings = self.settings_['params']

        self.latitude_text.setText(self.settings['location']['latitude'])
        self.longitude_text.setText(self.settings['location']['longitude'])
        self.height_text.setText(self.settings['location']['height'])
        self.ellipsoid_text.setText(self.settings['ell'])

        self.t_mod_text.setText(str(float(self.settings['Tmod']) * 60))
        self.course_text.setText(self.settings['course'])

        self.seed_text.setText(self.settings['seed'])
        self.srns_loss_prob_text.setText(self.settings['srns_loss_prob'])
        self.srns_loss_time_text.setText(str(self.settings['srns_loss_time']['min']) + ',' +
                                         str(self.settings['srns_loss_time']['max']))

        self.rr_number_min_text.setText(self.settings['n_lim']['min'])
        self.rr_number_max_text.setText(self.settings['n_lim']['max'])
        self.rr_speed_min_text.setText(self.settings['v_lim']['min'])
        self.rr_speed_max_text.setText(self.settings['v_lim']['max'])
        self.rr_radius_min_text.setText(self.settings['r_lim']['min'])
        self.rr_radius_max_text.setText(self.settings['r_lim']['max'])
        self.rr_time_min_text.setText(self.settings['t_lim']['min'])
        self.rr_time_max_text.setText(self.settings['t_lim']['max'])
        if self.settings['sensors'] is None:
            self.settings['sensors'] = dict()
        if len(self.settings['sensors']) > 0:
            self.sensors_num.setText(str(len(self.settings['sensors'])))
            dt_min = min([float(v['dt']) for v in self.settings['sensors'].values()])
            self.min_dt.setText(str(dt_min))
        else:
            self.min_dt.setText('0')
        self.out_signals.out_signal1.emit(self.settings.get('sensors', dict()))

    def save_xml_lambda(self, parent):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(parent,
                                                            'Save XML file',
                                                            self.open_path,
                                                            'xml (*.xml)',
                                                            options=options)
        if filename:
            self.settings['location'] = OrderedDict()
            self.settings['location']['latitude'] = self.latitude_text.text()
            self.settings['location']['longitude'] = self.longitude_text.text()
            self.settings['location']['height'] = self.height_text.text()
            self.settings['ell'] = self.ellipsoid_text.text()

            self.settings['Tmod'] = str(float(self.t_mod_text.text()) / 60)
            self.settings['course'] = self.course_text.text()

            self.settings['seed'] = self.seed_text.text()
            self.settings['srns_loss_prob'] = self.srns_loss_prob_text.text()
            srns_loss_time = [s.strip() for s in self.srns_loss_time_text.text().strip().split(',')]
            self.settings['srns_loss_time'] = OrderedDict()
            self.settings['srns_loss_time']['min'] = srns_loss_time[0]
            self.settings['srns_loss_time']['max'] = srns_loss_time[1]

            self.settings['n_lim'] = OrderedDict()
            self.settings['n_lim']['min'] = self.rr_number_min_text.text()
            self.settings['n_lim']['max'] = self.rr_number_max_text.text()
            self.settings['v_lim'] = OrderedDict()
            self.settings['v_lim']['min'] = self.rr_speed_min_text.text()
            self.settings['v_lim']['max'] = self.rr_speed_max_text.text()
            self.settings['r_lim'] = OrderedDict()
            self.settings['r_lim']['min'] = self.rr_radius_min_text.text()
            self.settings['r_lim']['max'] = self.rr_radius_max_text.text()
            self.settings['t_lim'] = OrderedDict()
            self.settings['t_lim']['min'] = self.rr_time_min_text.text()
            self.settings['t_lim']['max'] = self.rr_time_max_text.text()

            self.open_xml_filename = filename if filename.endswith('.xml') else filename + '.xml'
            self.xml_file_path.setText(self.open_xml_filename)
            self.settings_['params'] = self.settings

            with open(self.open_xml_filename, 'w') as f:
                f.write(xmltodict.unparse(self.settings_,
                                          full_document=True,
                                          pretty=True))
            self.out_signals.out_signal1.emit(self.settings.get('sensors', dict()))
            self.out_signals.out_signal2.emit(self.open_xml_filename)
        else:
            return

    def sensor_tab_out_signal1_response(self, msg):

        if 'sensors' not in self.settings.keys():
            self.settings['sensors'] = {}

        if len(self.settings['sensors']) > 0:
            all_sens_keys = [k for k, v in self.settings['sensors'].items() if v['type'] != 'user']
            for k in all_sens_keys:
                try:
                    del self.settings['sensors'][k]
                except KeyError:
                    pass

        if len(msg) > 0:
            for k, v in msg.items():
                self.settings['sensors'][k] = v

        if len(self.settings['sensors']) > 0:
            sens_num = len([v for v in self.settings['sensors'].values() if v['type'] != 'user'])
            self.sensors_num.setText(str(sens_num))
            dt_min = max(min([float(v['dt']) for v in self.settings['sensors'].values()]), 0)
            self.min_dt.setText(str(dt_min))

    def user_tab_out_signal1_response(self, msg):

        if 'sensors' not in self.settings.keys():
            self.settings['sensors'] = {}

        if len(self.settings['sensors']) > 0:
            all_user_keys = [k for k, v in self.settings['sensors'].items() if v['type'] == 'user']
            for k in all_user_keys:
                try:
                    del self.settings['sensors'][k]
                except KeyError:
                    pass

        if len(msg) > 0:
            for k, v in msg.items():
                self.settings['sensors'][k] = v

        if len(self.settings['sensors']) > 0:
            user_num = len([v for v in self.settings['sensors'].values() if v['type'] == 'user'])
            self.users_num.setText(str(user_num))
            dt_min = min([float(v['dt']) for v in self.settings['sensors'].values()])
            self.min_dt.setText(str(dt_min))
