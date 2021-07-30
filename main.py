from __future__ import unicode_literals

import sys, os

from PyQt5 import Qt, QtGui, QtWidgets
from PyQt5.Qt import *

from heat_sets import *

buttons = {}

helmets_unicode = {"R": u'🔴', "B": u'🔵', "W": u'⚪', "Y": u'🟡'}
helmets = {"R": helmets_unicode["R"].encode('utf8'), "B": helmets_unicode["B"].encode('utf8'),
           "W": helmets_unicode["W"].encode('utf8'), "Y": helmets_unicode["Y"].encode('utf8')}


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.options = None
        self.riders = []
        self.markers = None

        self.interface()
        self.setWindowTitle("Generator do live")
        self.setWindowIcon(QtGui.QIcon(self.resource_path("Logo.png")))
        self.setFixedSize(450, 300)

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)  # blocking window maximizing

        self.centerWindow()
        self.show()

    def interface(self):
        grid = QGridLayout(self)

        away_team = self.team_table(1, "Goście")
        host_team = self.team_table(9, "Gospodarze")

        grid.addWidget(away_team, 0, 0)
        grid.addWidget(host_team, 0, 1)

        self.options = QComboBox()

        self.options.addItem("PGE Ekstraliga - zestaw 1", heat_set_PL_1)
        self.options.addItem("PGE Ekstraliga - zestaw 2", heat_set_PL_2)
        self.options.addItem("eWinner 1. Liga - zestaw 1", heat_set_PL_1)
        self.options.addItem("eWinner 1. Liga - zestaw 2", heat_set_PL_2)
        self.options.addItem("2. Liga Żużlowa - zestaw 1", heat_set_PL_1)
        self.options.addItem("2. Liga Żużlowa - zestaw 2", heat_set_PL_2)
        self.options.addItem("Bauhaus-Ligan", heat_set_SWE)
        self.options.addItem("Zawody indywidualne", heat_set_IND)

        self.options.setCurrentIndex(0)  # set default option

        grid.addWidget(self.options, 1, 0)

        proceed_button = QPushButton()
        proceed_button.clicked.connect(self.generateFile)
        proceed_button.setText("Generuj")
        grid.addWidget(proceed_button, 1, 1)

        self.setLayout(grid)

    @staticmethod
    def team_table(start_num, team_name):  # 0 - away, 1 - host
        group = QGroupBox()
        team = QGridLayout()

        name = QLabel()
        name.setText(team_name)
        name.setAlignment(Qt.AlignCenter)
        team.addWidget(name, 0, 0, 1, 2)

        for i in range(8):  # generating labels for team
            label = QLabel()
            label.setText(str(start_num + i))
            label.setAlignment(Qt.AlignCenter)

            team.addWidget(label, i + 1, 0)

        for i in range(8):  # generating edit boxes for team
            button_id = str(start_num + i)
            line = QLineEdit()
            line.setObjectName(button_id)
            MainWindow.saveButton(line)
            line.setAlignment(Qt.AlignCenter)

            team.addWidget(line, i + 1, 1)

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
        # elif e.key() == Qt.Key_Enter:
        #     self.generateFile()

    def fetchRiders(self):
        for i in range(1, 17, 1):
            self.riders.append(MainWindow.findButton(str(i)).text())
        self.riders.append("")

    def generateFile(self):
        self.fetchRiders()

        heat_set = self.options.currentData()  # get heat set for selected event (tournament)

        file = open('generated.txt', 'wb')
        file.write("===== Biegi =====\n\n".encode("utf-8"))

        if str(heat_set[0]) == "PL":
            if self.options.currentIndex() % 2 == 0:  # Poland - heat set ver. 1
                self.writeHeatsFromHeatSet(file, self.options.currentData())

            else:  # Poland - heat set ver. 2
                self.writeHeatsFromHeatSet(file, self.options.currentData())

            self.writeLineUps(file, self.riders, self.options.currentIndex())

        elif heat_set[0] == "SWE":
            self.writeHeatsFromHeatSet(file, self.options.currentData())
            self.writeLineUps(file, self.riders, self.options.currentIndex())

        elif heat_set[0] == "IND":
            self.writeHeatsFromHeatSet(file, self.options.currentData())
            self.writeLineUps(file, self.riders, self.options.currentIndex())

        file.close()

        self.messageSuccess()

    def messageSuccess(self):
        message = QMessageBox(QMessageBox.Information, "Plik wygenerowany", "Możesz zamknąć okno")
        message.setWindowIcon(QtGui.QIcon(self.resource_path("Logo.png")))
        message.setStandardButtons(QMessageBox.Ok)

        message.exec()

    def writeHeatsFromHeatSet(self, file, heat_sets):
        for i in range(1, len(heat_sets), 1):
            heat_set = heat_sets[i].split(",")
            file.write(("Bieg {heat}\n{helmetA} {riderA}\n{helmetB} {riderB}\n{helmetC} {riderC}\n{helmetD} {riderD}\n\n".format(heat=i,
                               helmetA=helmets_unicode[heat_set[0]], riderA=self.riders[int(heat_set[1]) - 1],
                               helmetB=helmets_unicode[heat_set[2]], riderB=self.riders[int(heat_set[3]) - 1],
                               helmetC=helmets_unicode[heat_set[4]], riderC=self.riders[int(heat_set[5]) - 1],
                               helmetD=helmets_unicode[heat_set[6]], riderD=self.riders[int(heat_set[7]) - 1]).encode("utf-8")))

    def writeLineUps(self, file, riders, index):
        if index <= 6:  # league
            file.write("===== Składy drużyn =====\n\n".encode("utf-8"))

            if index <= 5:  # Polish
                if index >= 4:  # second Polish
                    self.markers = [(0, 7), (8, 15)]
                else:  # extra and first Polish
                    self.markers = [(0, 8), (8, 16)]
                self.writeLineUpPoland(file, riders, self.markers)

            elif index == 6:  # Swedish
                self.markers = [(0, 7), (8, 15)]
                self.writeLineUpSweden(file, riders, self.markers)

        elif index == 7:  # individual
            file.write("===== Lista startowa =====\n\n".encode("utf-8"))
            self.markers = [(0, 16)]
            self.writeLineUpIndividual(file, riders, self.markers)

    @staticmethod
    def writeLineUpPoland(file, riders, markers):
        for i in range(markers[1][0], markers[1][1], 1):  # hosts
            file.write("{number}. {rider}\n".format(number=i + 1, rider=riders[i]).encode("utf-8"))

        file.write("\n".encode("utf-8"))

        for i in range(markers[0][0], markers[0][1], 1):  # away
            file.write("{number}. {rider}\n".format(number=i + 1, rider=riders[i]).encode("utf-8"))

    @staticmethod
    def writeLineUpSweden(file, riders, markers):
        for i in range(markers[1][0], markers[1][1], 1):  # hosts
            file.write("{number}. {rider}\n".format(number=i - 7, rider=riders[i]).encode("utf-8"))  # i - 7 -> hosts numbers 1-7

        file.write("\n".encode("utf-8"))

        for i in range(markers[0][0], markers[0][1], 1):  # away
            file.write("{number}. {rider}\n".format(number=i + 1, rider=riders[i]).encode("utf-8"))

    @staticmethod
    def writeLineUpIndividual(file, riders, markers):
        for i in range(markers[0][0], markers[0][1], 1):  # hosts
            file.write("{number}. {rider}\n".format(number=i + 1, rider=riders[i]).encode("utf-8"))

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
