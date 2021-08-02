import sys
import os

from PyQt5 import QtWidgets
from PyQt5 import uic

import utils
from dfs_gui_generator import GeneratorGui
from dfs_gui_processing import ProcessorGui
from dfs_gui_evaluation import EvaluatorGui


class InsGpsGui(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()
        uic.loadUi(os.path.join('ui', 'INS_GPS_DFS_main.ui'), self)

        self.generating_button.clicked.connect(self.generate)
        self.processing_button.clicked.connect(self.process)
        self.evaluating_button.clicked.connect(self.evaluate)

        self.x = 100
        self.y = 100
        self.setFixedSize(self.geometry().width(), self.geometry().height())
        self.move(self.x, self.y)
        self.show()

        self.generator_dialog = None
        self.processor_dialog = None
        self.evaluator_dialog = None

    def generate(self):
        self.generator_dialog = GeneratorGui(self.x, self.y,
                                             self.geometry().width(),
                                             self.geometry().height())
        if self.evaluator_dialog is not None:
            if self.evaluator_dialog.isVisible():
                self.evaluator_dialog.move(self.x,
                                           self.y + self.geometry().height() +
                                           self.generator_dialog.geometry().height() + 80)

    def process(self):
        self.processor_dialog = ProcessorGui(self.x, self.y,
                                             self.geometry().width())
        if self.evaluator_dialog is not None:
            if self.evaluator_dialog.isVisible():
                self.evaluator_dialog.move(self.x,
                                           self.y + self.processor_dialog.geometry().height() + 40)

    def evaluate(self):
        if self.generator_dialog is None and self.processor_dialog is None:
            h = self.geometry().height() + 40
        else:
            if self.generator_dialog is not None:
                if self.generator_dialog.isVisible():
                    h = self.geometry().height() + self.generator_dialog.geometry().height() + 80
                else:
                    h = self.geometry().height() + 40
            else:
                if self.processor_dialog.isVisible():
                    h = self.processor_dialog.geometry().height() + 40
                else:
                    h = self.geometry().height() + 40
        self.evaluator_dialog = EvaluatorGui(self.x, self.y, h)

    def closeEvent(self, event):
        if self.generator_dialog is not None:
            self.generator_dialog.close()
        if self.processor_dialog is not None:
            self.processor_dialog.close()
        if self.evaluator_dialog is not None:
            self.evaluator_dialog.close()
        utils.close_matlab()


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    # size = app.primaryScreen().size()
    ex = InsGpsGui()
    app.aboutToQuit.connect(utils.clean_up)
    sys.exit(app.exec_())
