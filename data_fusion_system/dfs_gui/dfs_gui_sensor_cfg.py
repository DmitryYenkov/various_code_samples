from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import uic

from collections import OrderedDict
from copy import deepcopy


ellipsoids = ['wgs84', 'glonass', 'beidou']
ellipsoid_indices = {v: i for i, v in enumerate(ellipsoids)}
ellipsoid_names = {i: v for i, v in enumerate(ellipsoids)}
ellipsoid_official_names = ['WGS84 (GPS)', 'ПЗ-90.02 (GLONASS)', 'CGCS2000 (BeiDou)']


class SensorsCfgOutSignals(QtCore.QObject):

    out_sensors_dict = QtCore.pyqtSignal(dict)
    out_sensors_name = QtCore.pyqtSignal(str)


class SensorsCfgGui(QtWidgets.QDialog):

    def __init__(self, x, y, sdict=None, name='', stype='',
                 ui='ui/Base_Sensor_Cfg.ui'):

        super().__init__()
        uic.loadUi(ui, self)

        self.out_signals = SensorsCfgOutSignals()
        if sdict is None:
            self.sensor = dict()
            self.sensor['name'] = name
            self.sensor['type'] = stype
        else:
            self.sensor = sdict
            self.x_line.setText(self.sensor['position']['x'])
            self.y_line.setText(self.sensor['position']['y'])
            self.z_line.setText(self.sensor['position']['z'])
            self.dt_line.setText(self.sensor['dt'])
            self.show_extra_parameters()
            self.name_line.setEnabled(True)

        self.old_name = deepcopy(self.sensor['name'])

        self.type_line.setText(self.sensor['type'])
        self.name_line.setText(self.sensor['name'])

        self.ok_button.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.ok_button.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.ok)

        self.move(x + 50, y - 100)
        self.show()

    def show_extra_parameters(self):
        self.param1_line.setText('0')

    def cancel(self):
        self.close()

    def ok(self):
        self.sensor['position'] = OrderedDict()
        self.sensor['position']['x'] = self.x_line.text()
        self.sensor['position']['y'] = self.y_line.text()
        self.sensor['position']['z'] = self.z_line.text()
        self.sensor['dt'] = self.dt_line.text()
        self.sensor['name'] = self.name_line.text()

        self.out_signals.out_sensors_dict.emit(self.sensor)
        if self.old_name != self.sensor['name']:
            self.out_signals.out_sensors_name.emit(self.old_name)
        self.close()


class GyrocompassCfgGui(SensorsCfgGui):

    def __init__(self, x, y, sdict=None, name='', stype='gyrocompass'):
        super().__init__(x, y, sdict=sdict, name=name, stype=stype)

        self.param1_label.setText('Precision')

    def show_extra_parameters(self):
        self.param1_line.setText(self.sensor['precision'])

    def ok(self):
        self.sensor['precision'] = self.param1_line.text()
        super().ok()


class LagCfgGui(SensorsCfgGui):

    def __init__(self, x, y, sdict=None, name='', stype='lag'):
        super().__init__(x, y, sdict=sdict, name=name, stype=stype)

        self.param1_label.setText('Sigma')

    def show_extra_parameters(self):
        self.param1_line.setText(self.sensor['sigma'])

    def ok(self):
        self.sensor['sigma'] = self.param1_line.text()
        super().ok()


class SRNSCfgGui(SensorsCfgGui):

    def __init__(self, x, y, sdict=None, name='',
                 stype='srns', ui='ui/SRNS_cfg.ui'):
        super().__init__(x, y, sdict=sdict, name=name, stype=stype, ui=ui)

    def show_extra_parameters(self):
        self.param1_line.setText(self.sensor['sigma_R'])
        self.param2_line.setText(self.sensor['sigma_h'])
        self.param3_line.setText(self.sensor['loss_prob'])
        self.param4_combo.setCurrentIndex(ellipsoid_indices[self.sensor['ell']])

    def ok(self):
        self.sensor['sigma_R'] = self.param1_line.text()
        self.sensor['sigma_h'] = self.param2_line.text()
        self.sensor['loss_prob'] = self.param3_line.text()
        self.sensor['ell'] = ellipsoid_names[self.param4_combo.currentIndex()]
        super().ok()


class SGSCfgGui(SensorsCfgGui):

    def __init__(self, x, y, sdict=None, name='',
                 stype='sgs', ui='ui/SGS_cfg.ui'):
        super().__init__(x, y, sdict=sdict, name=name, stype=stype, ui=ui)

    def show_extra_parameters(self):
        self.param1_line.setText(self.sensor['pitch_prec'])
        self.param2_line.setText(self.sensor['roll_prec'])
        self.param4_line.setText(self.sensor['acc_scale'])
        self.param311_line.setText(self.sensor['NBK_acc_x']['N'])
        self.param312_line.setText(self.sensor['NBK_acc_x']['B'])
        self.param313_line.setText(self.sensor['NBK_acc_x']['K'])
        self.param321_line.setText(self.sensor['NBK_acc_y']['N'])
        self.param322_line.setText(self.sensor['NBK_acc_y']['B'])
        self.param323_line.setText(self.sensor['NBK_acc_y']['K'])

    def ok(self):
        self.sensor['pitch_prec'] = self.param1_line.text()
        self.sensor['roll_prec'] = self.param2_line.text()
        self.sensor['acc_scale'] = self.param4_line.text()
        self.sensor['NBK_acc_x'] = OrderedDict()
        self.sensor['NBK_acc_x']['N'] = self.param311_line.text()
        self.sensor['NBK_acc_x']['B'] = self.param312_line.text()
        self.sensor['NBK_acc_x']['K'] = self.param313_line.text()
        self.sensor['NBK_acc_y'] = OrderedDict()
        self.sensor['NBK_acc_y']['N'] = self.param321_line.text()
        self.sensor['NBK_acc_y']['B'] = self.param322_line.text()
        self.sensor['NBK_acc_y']['K'] = self.param323_line.text()
        super().ok()


class IMUCfgGui(SensorsCfgGui):

    def __init__(self, x, y, sdict=None, name='',
                 stype='imu', ui='ui/IMU_cfg.ui'):
        super().__init__(x, y, sdict=sdict, name=name, stype=stype, ui=ui)

    def show_extra_parameters(self):
        self.param1_line.setText(self.sensor['acc_scale'])
        self.param2_line.setText(self.sensor['gyr_scale'])
        self.param311_line.setText(self.sensor['NBK_acc_x']['N'])
        self.param312_line.setText(self.sensor['NBK_acc_x']['B'])
        self.param313_line.setText(self.sensor['NBK_acc_x']['K'])
        self.param321_line.setText(self.sensor['NBK_acc_y']['N'])
        self.param322_line.setText(self.sensor['NBK_acc_y']['B'])
        self.param323_line.setText(self.sensor['NBK_acc_y']['K'])
        self.param331_line.setText(self.sensor['NBK_acc_z']['N'])
        self.param332_line.setText(self.sensor['NBK_acc_z']['B'])
        self.param333_line.setText(self.sensor['NBK_acc_z']['K'])
        self.param341_line.setText(self.sensor['NBK_gyr_x']['N'])
        self.param342_line.setText(self.sensor['NBK_gyr_x']['B'])
        self.param343_line.setText(self.sensor['NBK_gyr_x']['K'])
        self.param351_line.setText(self.sensor['NBK_gyr_y']['N'])
        self.param352_line.setText(self.sensor['NBK_gyr_y']['B'])
        self.param353_line.setText(self.sensor['NBK_gyr_y']['K'])
        self.param361_line.setText(self.sensor['NBK_gyr_z']['N'])
        self.param362_line.setText(self.sensor['NBK_gyr_z']['B'])
        self.param363_line.setText(self.sensor['NBK_gyr_z']['K'])

    def ok(self):
        self.sensor['acc_scale'] = self.param1_line.text()
        self.sensor['gyr_scale'] = self.param2_line.text()
        self.sensor['NBK_acc_x'] = OrderedDict()
        self.sensor['NBK_acc_x']['N'] = self.param311_line.text()
        self.sensor['NBK_acc_x']['B'] = self.param312_line.text()
        self.sensor['NBK_acc_x']['K'] = self.param313_line.text()
        self.sensor['NBK_acc_y'] = OrderedDict()
        self.sensor['NBK_acc_y']['N'] = self.param321_line.text()
        self.sensor['NBK_acc_y']['B'] = self.param322_line.text()
        self.sensor['NBK_acc_y']['K'] = self.param323_line.text()
        self.sensor['NBK_acc_z'] = OrderedDict()
        self.sensor['NBK_acc_z']['N'] = self.param331_line.text()
        self.sensor['NBK_acc_z']['B'] = self.param332_line.text()
        self.sensor['NBK_acc_z']['K'] = self.param333_line.text()
        self.sensor['NBK_gyr_x'] = OrderedDict()
        self.sensor['NBK_gyr_x']['N'] = self.param341_line.text()
        self.sensor['NBK_gyr_x']['B'] = self.param342_line.text()
        self.sensor['NBK_gyr_x']['K'] = self.param343_line.text()
        self.sensor['NBK_gyr_y'] = OrderedDict()
        self.sensor['NBK_gyr_y']['N'] = self.param351_line.text()
        self.sensor['NBK_gyr_y']['B'] = self.param352_line.text()
        self.sensor['NBK_gyr_y']['K'] = self.param353_line.text()
        self.sensor['NBK_gyr_z'] = OrderedDict()
        self.sensor['NBK_gyr_z']['N'] = self.param361_line.text()
        self.sensor['NBK_gyr_z']['B'] = self.param362_line.text()
        self.sensor['NBK_gyr_z']['K'] = self.param363_line.text()
        super().ok()


class UserCfgGui(QtWidgets.QDialog):

    def __init__(self, x, y, sdict=None, name='', ui='ui/User_cfg.ui'):

        super().__init__()
        uic.loadUi(ui, self)

        self.out_signals = SensorsCfgOutSignals()

        if sdict is None:
            self.user = dict()
            self.user['name'] = name
        else:
            self.user = sdict
            self.x_line.setText(self.user['position']['x'])
            self.y_line.setText(self.user['position']['y'])
            self.z_line.setText(self.user['position']['z'])
            self.dt_line.setText(self.user['dt'])
            self.show_extra_parameters()
            self.name_line.setEnabled(True)
        print(self.user)
        self.old_name = deepcopy(self.user['name'])

        self.name_line.setText(self.user['name'])

        self.ok_button.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.ok_button.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.ok)

        self.move(x + 50, y - 100)
        self.show()

    def show_extra_parameters(self):
        self.param1_line.setText(self.user['delay'])
        self.param2_combo.setCurrentIndex(ellipsoid_indices[self.user['ell']])

    def ok(self):
        self.user['delay'] = self.param1_line.text()
        self.user['ell'] = ellipsoid_names[self.param2_combo.currentIndex()]

        self.user['position'] = OrderedDict()
        self.user['position']['x'] = self.x_line.text()
        self.user['position']['y'] = self.y_line.text()
        self.user['position']['z'] = self.z_line.text()
        self.user['dt'] = self.dt_line.text()
        self.user['name'] = self.name_line.text()

        self.out_signals.out_sensors_dict.emit(self.user)
        if self.old_name != self.user['name']:
            self.out_signals.out_sensors_name.emit(self.old_name)
        self.close()

    def cancel(self):
        self.close()
