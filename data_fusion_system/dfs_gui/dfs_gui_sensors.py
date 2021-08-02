from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import uic

from copy import deepcopy

from dfs_gui_sensor_cfg import SensorsCfgOutSignals
from dfs_gui_sensor_cfg import GyrocompassCfgGui
from dfs_gui_sensor_cfg import LagCfgGui
from dfs_gui_sensor_cfg import SRNSCfgGui
from dfs_gui_sensor_cfg import SGSCfgGui
from dfs_gui_sensor_cfg import IMUCfgGui


sensor_types = ['gyrocompass', 'lag', 'sgs', 'srns', 'imu']


class SensorsTableGui(QtWidgets.QDialog):

    def __init__(self, x, y, sensors):

        super().__init__()
        uic.loadUi('ui/Sensors.ui', self)

        self.out_signals = SensorsCfgOutSignals()
        self.sensors_ = sensors
        self.sensors = deepcopy(self.sensors_)

        self.add_button.clicked.connect(self.add)
        self.edit_button.clicked.connect(self.edit)
        self.revert_button.clicked.connect(self.revert)
        self.delete_button.clicked.connect(self.delete)

        self.sensor_cfg = None

        self.update_table()

        self.move(x + 50, y + 50)

        self.show()

    def update_table(self):

        self.table.clearContents()
        self.table.setRowCount(len(self.sensors))
        for i, (k, v) in enumerate(self.sensors.items()):
            item = QtWidgets.QTableWidgetItem(v['name'])
            self.table.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(v['type'])
            self.table.setItem(i, 1, item)
        self.out_signals.out_sensors_dict.emit(self.sensors)

    def add(self):

        names = [v['name'] for v in self.sensors.values()]
        new_name = self.sensor_name_line.text()
        if new_name == '' or new_name in names:
            msg = QtWidgets.QMessageBox()
            msg.setInformativeText('No name or existing name!')
            msg.setWindowTitle('Error')
            msg.exec_()
        else:
            self.setWindowModality(QtCore.Qt.NonModal)
            stype = sensor_types[self.sensor_type_combo.currentIndex()]
            if stype == 'gyrocompass':
                self.sensor_cfg = GyrocompassCfgGui(self.geometry().x(), self.geometry().y(),
                                                    name=new_name)
            elif stype == 'lag':
                self.sensor_cfg = LagCfgGui(self.geometry().x(), self.geometry().y(),
                                            name=new_name)
            elif stype == 'sgs':
                self.sensor_cfg = SGSCfgGui(self.geometry().x(), self.geometry().y(),
                                            name=new_name)
            elif stype == 'imu':
                self.sensor_cfg = IMUCfgGui(self.geometry().x(), self.geometry().y(),
                                            name=new_name)
            else:  # 'srns'
                self.sensor_cfg = SRNSCfgGui(self.geometry().x(), self.geometry().y(),
                                             name=new_name)
            self.sensor_cfg.out_signals.out_sensors_dict.connect(self.add_sensor)
            self.sensor_cfg.out_signals.out_sensors_name.connect(self.delete_sensor)
            self.sensor_cfg.setWindowModality(QtCore.Qt.ApplicationModal)

    def add_sensor(self, msg):
        self.sensors[msg['name']] = msg
        self.update_table()

    def delete_sensor(self, name):
        del self.sensors[name]
        self.update_table()

    def edit(self):
        row = self.table.currentRow()
        if row < 0:
            msg = QtWidgets.QMessageBox()
            msg.setInformativeText('Sensor not selected!')
            msg.setWindowTitle('Error')
            msg.exec_()
        else:
            self.setWindowModality(QtCore.Qt.NonModal)
            name = self.table.item(row, 0).text()
            stype = self.table.item(row, 1).text()
            if stype == 'gyrocompass':
                self.sensor_cfg = GyrocompassCfgGui(self.geometry().x(), self.geometry().y(),
                                                    sdict=self.sensors[name])
            elif stype == 'lag':
                self.sensor_cfg = LagCfgGui(self.geometry().x(), self.geometry().y(),
                                            sdict=self.sensors[name])
            elif stype == 'sgs':
                self.sensor_cfg = SGSCfgGui(self.geometry().x(), self.geometry().y(),
                                            sdict=self.sensors[name])
            elif stype == 'imu':
                self.sensor_cfg = IMUCfgGui(self.geometry().x(), self.geometry().y(),
                                            sdict=self.sensors[name])
            else:  # 'srns'
                self.sensor_cfg = SRNSCfgGui(self.geometry().x(), self.geometry().y(),
                                             sdict=self.sensors[name])
            self.sensor_cfg.out_signals.out_sensors_dict.connect(self.add_sensor)
            self.sensor_cfg.out_signals.out_sensors_name.connect(self.delete_sensor)
            self.sensor_cfg.setWindowModality(QtCore.Qt.ApplicationModal)

    def revert(self):

        self.sensors = deepcopy(self.sensors_)
        self.update_table()

    def delete(self):

        row = self.table.currentRow()
        col = self.table.currentColumn()
        name = self.table.item(row, 0).text()
        self.delete_sensor(name)
        if row < self.table.rowCount():
            self.table.setCurrentCell(row, col)

    def closeEvent(self, event):

        if self.sensor_cfg is not None:
            self.sensor_cfg.setWindowModality(QtCore.Qt.NonModal)
            self.setWindowModality(QtCore.Qt.ApplicationModal)
