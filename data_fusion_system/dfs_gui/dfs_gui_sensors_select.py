from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import uic

from copy import deepcopy


class SensorsSelectOutSignals(QtCore.QObject):

    out_selected = QtCore.pyqtSignal(list)


class SensorsSelectGui(QtWidgets.QDialog):

    def __init__(self, x, y, sensors, selected):

        super().__init__()
        uic.loadUi('ui/Sensors_selection.ui', self)

        self.out_signals = SensorsSelectOutSignals()
        self.sensors = sensors
        self.selected_ = selected
        self.selected = deepcopy(self.selected_)

        self.show_list()

        self.ok_button.clicked.connect(self.ok)
        self.revert_button.clicked.connect(self.revert)

        self.move(x - 50, y + 50)

        self.show()

    def ok(self):
        self.selected = []
        for i in range(self.select_list.count()):
            item = self.select_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                self.selected.append(item.text())

        self.out_signals.out_selected.emit(self.selected)
        self.close()

    def revert(self):
        self.selected = deepcopy(self.selected_)
        self.show_list()

    def show_list(self):
        self.select_list.clear()
        for s in self.sensors:
            item = QtWidgets.QListWidgetItem(s)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                          QtCore.Qt.ItemIsEnabled |
                          QtCore.Qt.ItemIsSelectable)
            if s in self.selected:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            self.select_list.addItem(item)
