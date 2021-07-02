from __future__ import unicode_literals

import sys, os

from PyQt5 import Qt, QtGui, QtWidgets
from PyQt5.Qt import *

buttons = {}
helmets_unicode = {"R": u'🔴', "B": u'🔵', "W": u'⚪', "Y": u'🟡'}
helmets = {"R": helmets_unicode["R"].encode('utf8'), "B": helmets_unicode["B"].encode('utf8'),
           "W": helmets_unicode["W"].encode('utf8'), "Y": helmets_unicode["Y"].encode('utf8')}

heat_set_1 = {1: "Y,1,R,9,W,3,B,11", 2: "R,15,W,6,B,14,Y,7", 3: "Y,5,B,12,W,2,R,13", 4: "B,14,Y,4,R,10,W,6", 5: "R,11,W,3,B,12,Y,4",
              6: "R,13,W,2,B,15,Y,1", 7: "W,7,B,10,Y,5,R,9", 8: "W,3,R,13,Y,4,B,14", 9: "R,9,Y,1,B,10,W,2", 10: "W,6,R,11,Y,5,B,12",
              11: "B,12,W,4,R,9,Y,1", 12: "Y,2,B,15,W,7,R,11", 13: "B,10,Y,5,R,13,W,3", 14: "Y,17,R,17,W,17,B,17", 15: "R,17,Y,17,B,17,W,17"}

heat_set_2 = {1: "R,9,Y,1,B,11,W,3", 2: "W,6,R,15,Y,7,B,14", 3: "B,12,Y,5,R,13,W,2", 4: "Y,4,B,14,W,6,R,10", 5: "W,3,R,11,Y,4,B,12",
              6: "W,2,R,13,Y,1,B,15", 7: "B,10,W,7,R,9,Y,5", 8: "R,13,W,3,B,14,Y,4", 9: "Y,1,R,9,W,2,B,10", 10: "R,11,W,6,B,12,Y,5",
              11: "W,4,B,12,Y,1,R,9", 12: "B,15,Y,2,R,11,W,7", 13: "Y,5,B,10,W,3,R,13", 14: "R,17,Y,17,B,17,W,17", 15: "Y,17,R,17,W,17,B,17"}


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.interface()
        self.setWindowTitle("Generator do live")
        self.setWindowIcon(QtGui.QIcon(self.resource_path("Logo.png")))
        self.setFixedSize(450, 300)

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)  # blocking window maximizing

        self.riders = []

        self.centerWindow()
        self.show()

    def interface(self):
        grid = QGridLayout(self)

        away_team = self.team_table(1)
        host_team = self.team_table(9)

        grid.addWidget(away_team, 0, 0)
        grid.addWidget(host_team, 0, 1)

        proceed_button = QPushButton()
        proceed_button.clicked.connect(self.whenClicked)
        proceed_button.setText("Generuj")
        grid.addWidget(proceed_button, 1, 0, 1, 2)

        self.setLayout(grid)

    @staticmethod
    def team_table(start_num):  # 0 - away, 1 - host
        group = QGroupBox()
        team = QGridLayout()

        for i in range(8):
            label = QLabel()
            label.setText(str(start_num + i))
            label.setAlignment(Qt.AlignCenter)

            team.addWidget(label, i, 0)

        for i in range(8):
            button_id = str(start_num + i)
            line = QLineEdit()
            line.setObjectName(button_id)
            MainWindow.saveButton(line)
            line.setAlignment(Qt.AlignCenter)

            team.addWidget(line, i, 1)

        group.setLayout(team)

        return group

    @staticmethod
    def saveButton(obj):
        buttons[obj.objectName()] = obj

    @staticmethod
    def findButton(text):
        return buttons[text]

    def centerWindow(self):
        frame_geometry = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def closeEvent(self, event):  # are you sure to quit?
        box = QMessageBox(QMessageBox.Warning, "Wyjście", "Czy na pewno koniec?")
        yes_answer = box.addButton(self.tr("Tak"), QMessageBox.YesRole)
        no_answer = box.addButton(self.tr("Nie"), QMessageBox.NoRole)
        box.setDefaultButton(no_answer)
        box.setWindowIcon(QtGui.QIcon(self.resource_path("Logo.png")))

        box.exec_()

        if box.clickedButton() == yes_answer:
            event.accept()
        elif box.clickedButton() == no_answer:
            event.ignore()

    def keyPressEvent(self, e):  # exit with Escape button
        if e.key() == Qt.Key_Escape:
            self.close()

    def whenClicked(self):
        for i in range(1, 17, 1):
            self.riders.append(MainWindow.findButton(str(i)).text())
        self.riders.append("")

        file = open('generated.txt', 'wb')

        file.write("===== Zestaw 1 =====\n\n".encode("utf-8"))
        self.writeHeatsToFile(file, heat_set_1)
        file.write("===== Zestaw 2 =====\n\n".encode("utf-8"))
        self.writeHeatsToFile(file, heat_set_2)
        file.write("===== Składy drużyn =====\n\n".encode("utf-8"))
        self.writeLineUps(file, self.riders)

        file.close()

        self.messageSuccess()

    def messageSuccess(self):
        message = QMessageBox(QMessageBox.Information, "Plik wygenerowany", "Możesz zamknąć okno")
        message.setWindowIcon(QtGui.QIcon(self.resource_path("Logo.png")))
        message.setStandardButtons(QMessageBox.Ok)

        message.exec()

    def writeHeatsToFile(self, file, heat_sets):
        for i in range(1, 16, 1):
            heat_set = heat_sets[i].split(",")
            file.write(("Bieg {heat}\n{helmetA} {riderA}\n{helmetB} {riderB}\n{helmetC} {riderC}\n{helmetD} {riderD}\n\n".format(heat=i,
                               helmetA=helmets_unicode[heat_set[0]], riderA=self.riders[int(heat_set[1]) - 1],
                               helmetB=helmets_unicode[heat_set[2]], riderB=self.riders[int(heat_set[3]) - 1],
                               helmetC=helmets_unicode[heat_set[4]], riderC=self.riders[int(heat_set[5]) - 1],
                               helmetD=helmets_unicode[heat_set[6]], riderD=self.riders[int(heat_set[7]) - 1]).encode("utf-8")))

    @staticmethod
    def writeLineUps(file, riders):
        for i in range(8, 16, 1):
            file.write("{number}. {rider}\n".format(number=i+1, rider=riders[i]).encode("utf-8"))

        file.write("\n".encode("utf-8"))

        for i in range(0, 8, 1):
            file.write("{number}. {rider}\n".format(number=i+1, rider=riders[i]).encode("utf-8"))

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


app = QApplication(sys.argv)  # creating app

window = MainWindow()
sys.exit(app.exec_())  # starting the app
