from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from sea_widget_sensor_cfg import SensorCfgWindow
import copy


class SensorTabOutSignals(QtCore.QObject):

    out_signal1 = QtCore.pyqtSignal(dict)
    out_signal2 = QtCore.pyqtSignal(dict)


class SensorsSettingsTab(QtWidgets.QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        self.sensors = dict()
        self.sensors_backup = dict()

        self.table_widget = QtWidgets.QTableWidget(14, 2)

        self.out_signals = SensorTabOutSignals()

        self.sensors_settings_tab_layout(parent)

    def sensors_settings_tab_layout(self, parent):

        layout = QtWidgets.QGridLayout(parent)
        layout.setSpacing(5)

        dummy_label = QtWidgets.QLabel('', parent)
        label_color = dummy_label.palette().color(QtGui.QPalette.Background)
        text_palette = dummy_label.palette()
        text_palette.setColor(dummy_label.backgroundRole(), label_color)
        bold_font = QtGui.QFont()
        bold_font.setBold(True)

        self.table_widget.setHorizontalHeaderLabels(['Name', 'Type'])
        self.table_widget.setColumnWidth(1, 100)
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        add_button = QtWidgets.QPushButton('Add')
        add_func = lambda: self.add_lambda()
        add_button.clicked.connect(add_func)

        edit_button = QtWidgets.QPushButton('Edit')
        edit_func = lambda: self.edit_lambda()
        edit_button.clicked.connect(edit_func)

        delete_button = QtWidgets.QPushButton('Delete')
        delete_func = lambda: self.delete_lambda()
        delete_button.clicked.connect(delete_func)

        revert_button = QtWidgets.QPushButton('Revert')
        revert_func = lambda: self.revert_lambda()
        revert_button.clicked.connect(revert_func)

        layout.addWidget(self.table_widget, 0, 0, 12, 6)
        layout.addWidget(add_button, 0, 7, 1, 1)
        layout.addWidget(edit_button, 1, 7, 1, 1)
        layout.addWidget(delete_button, 2, 7, 1, 1)
        layout.addWidget(revert_button, 3, 7, 1, 1)

        parent.setLayout(layout)

    def add_lambda(self):

        add_dialog = SensorCfgWindow()
        add_dialog.out_signals.out_signal1.connect(self.cfg_out_signal1_response)

    def edit_lambda(self):

        rows = [s.row() for s in self.table_widget.selectedItems()]
        if not rows:
            return
        name = self.table_widget.item(rows[0], 0).text()

        edit_dialog = SensorCfgWindow()
        self.out_signals.out_signal2.connect(edit_dialog.sensors_out_signal2_response)
        edit_dialog.out_signals.out_signal1.connect(self.cfg_out_signal2_response)
        self.out_signals.out_signal2.emit(self.sensors[name])
        self.out_signals.out_signal2.disconnect()

        del self.sensors[name]

    def delete_lambda(self):

        selected = self.table_widget.selectedItems()
        if not selected:
            return
        rows = [s.row() for s in self.table_widget.selectedItems()]
        names = [self.table_widget.item(row, 0).text() for row in rows]
        for name in names:
            del self.sensors[name]
        self.update_table()

    def revert_lambda(self):

        self.sensors = copy.deepcopy(self.sensors_backup)
        self.update_table()

    def update_table(self):

        self.table_widget.clear()
        for i, k in enumerate(self.sensors.keys()):
            item = QtWidgets.QTableWidgetItem(k)
            self.table_widget.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(self.sensors[k]['type'])
            self.table_widget.setItem(i, 1, item)

        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.out_signals.out_signal1.emit(self.sensors)

    def settings_tab_out_signal1_response(self, msg):

        if len(msg) > 0:
            for k, v in msg.items():
                if v['type'] != 'user':
                    self.sensors[k] = v

        self.sensors_backup = copy.deepcopy(self.sensors)
        self.update_table()

    def cfg_out_signal1_response(self, msg):

        if msg['name'] in self.sensors.keys():
            err = QtWidgets.QMessageBox()
            err.setIcon(QtWidgets.QMessageBox.Critical)
            err.setText('This name already exists! Entry will be overwritten')
            err.setWindowTitle('Error')
            err.exec_()
        else:
            self.cfg_out_signal2_response(msg)

    def cfg_out_signal2_response(self, msg):

        self.sensors[msg['name']] = msg
        self.update_table()
