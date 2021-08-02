import sys
import argparse
import os

from PyQt5 import QtWidgets

from sea_widget_settings_tab import GeneralSettingsTab
from sea_widget_sensors_tab import SensorsSettingsTab
from sea_widget_simulation_tab import SimulationTab
from sea_widget_simulation_tab import close_matlab
from sea_widget_filter_tab import FilterTab
from sea_widget_users_tab import UsersSettingsTab

sys.path.insert(0, '/')
sys.path.insert(1, 'd:/ins_gps_project/sources/fusion_filter')


def clean(item):
    """Clean up the memory by closing and deleting the item if possible."""
    if isinstance(item, list) or isinstance(item, dict):
        for _ in range(len(item)):
            clean(list(item).pop())
    else:
        try:
            item.close()
        except (RuntimeError, AttributeError):  # deleted or no close method
            try:
                item.deleteLater()
            except (RuntimeError, AttributeError):  # deleted or no deleteLater method
                pass


def clean_up(obj):
    # Clean up everything
    for i in obj.__dict__:
        item = obj.__dict__[i]
        clean(item)


class IMUGPSModelApp(QtWidgets.QWidget):

    def __init__(self, paths):

        super().__init__()

        self.paths = paths

        self.h = 500
        self.w = 500
        self.m = 5
        self.x = 50
        self.y = 50

        self.setFixedSize(self.w, self.h)
        self.move(self.x, self.y)
        self.setWindowTitle('INS-GPS Data Fusion System')
        self.init_ui()

    def init_ui(self):
        close_matlab()

        tabs = QtWidgets.QTabWidget(self)
        tabs.resize(self.w - 2 * self.m, self.h - 2 * self.m)
        tabs.move(self.m, self.m)

        tab1 = QtWidgets.QWidget(self)
        tab2 = QtWidgets.QWidget(self)
        tab3 = QtWidgets.QWidget(self)
        tab4 = QtWidgets.QWidget(self)
        tab5 = QtWidgets.QWidget(self)

        tabs.addTab(tab5, 'Simulation Tab')
        tabs.addTab(tab1, 'Settings Tab')
        tabs.addTab(tab2, 'Sensors Tab')
        tabs.addTab(tab3, 'Filter Tab')
        tabs.addTab(tab4, 'Users Tab')

        set_obj = GeneralSettingsTab(tab1, self.paths.open_xml_path)
        sens_obj = SensorsSettingsTab(tab2)
        flt_obj = FilterTab(tab3, self.paths.filter_parameters_path)
        user_obj = UsersSettingsTab(tab4)
        sim_obj = SimulationTab(tab5,
                                self.paths.quat_lib_path,
                                self.paths.xml_lib_path,
                                self.paths.movement_model_path,
                                self.paths.results_path,
                                self.paths.imu_gps_filter_path)
        #
        set_obj.out_signals.out_signal1.connect(sens_obj.settings_tab_out_signal1_response)
        set_obj.out_signals.out_signal1.connect(user_obj.settings_tab_out_signal1_response)
        set_obj.out_signals.out_signal2.connect(sim_obj.settings_tab_out_signal2_response)
        sens_obj.out_signals.out_signal1.connect(set_obj.sensor_tab_out_signal1_response)
        user_obj.out_signals.out_signal1.connect(set_obj.user_tab_out_signal1_response)
        flt_obj.out_signals.out_signal1.connect(sim_obj.filter_tab_out_signal1_response)

        self.show()

    def closeEvent(self, event):
        close_matlab()


if __name__ == '__main__':

    default_path = os.getcwd()
    parser = argparse.ArgumentParser(description='IMU-GPS Fusion Model Config')
    parser.add_argument('--quat_lib_path', type=str,
                        dest='quat_lib_path',
                        default=default_path,
                        help='Path to MATLAB Quaternion functions library')
    parser.add_argument('--xml_lib_path', type=str,
                        dest='xml_lib_path',
                        default=default_path,
                        help='Path to MATLAB XML functions library')
    parser.add_argument('--movement_model_path', type=str,
                        dest='movement_model_path',
                        default=default_path,
                        help='Path to MATLAB Movement Data Generator project')
    parser.add_argument('--imu_gps_filter_path', type=str,
                        dest='imu_gps_filter_path',
                        default=default_path,
                        help='Path to IMU-GPS Fusion Filter python project')
    parser.add_argument('--filter_parameters_path', type=str,
                        dest='filter_parameters_path',
                        default=default_path,
                        help='Path to IMU-GPS Fusion Filter parameters')
    parser.add_argument('--open_xml_path', type=str,
                        dest='open_xml_path',
                        default=default_path,
                        help='Default path to open XML config files')
    parser.add_argument('--save_model_path', type=str,
                        dest='save_model_path',
                        default=default_path,
                        help='Default path to save MATLAB Movement Model results')
    args = parser.parse_args()

    app = QtWidgets.QApplication(sys.argv)
    ex = IMUGPSModelApp(args)
    app.aboutToQuit.connect(clean_up)
    sys.exit(app.exec_())
