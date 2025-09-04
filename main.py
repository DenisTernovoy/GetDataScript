from PyQt5 import QtCore, QtGui, QtWidgets
from src.common_class import Test
from src.get_data import WindowComposeData
import sys


class MainWindow(Test):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Основное окно")
        self.setGeometry(0, 350, 400, 300)

        self.label = QtWidgets.QLabel("Выберите функционал:")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setContentsMargins(0, 0, 0, 30)
        self.label.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))

        self.button_compose_data = QtWidgets.QPushButton("Составить свод")
        self.button_compose_data.setFixedSize(200, 80)
        self.button_compose_data.clicked.connect(self.compose_data)

        self.button_check_data = QtWidgets.QPushButton("Проверить журналы")
        self.button_check_data.setFixedSize(200, 80)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignCenter)


        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button_compose_data)
        self.layout.addWidget(self.button_check_data)

        self.layout.setAlignment(self.label, QtCore.Qt.AlignCenter)
        self.layout.setAlignment(self.button_compose_data, QtCore.Qt.AlignCenter)
        self.layout.setAlignment(self.button_check_data, QtCore.Qt.AlignCenter)


        self.container = QtWidgets.QWidget()
        self.container.setLayout(self.layout)

        self.setCentralWidget(self.container)

        # Центрирование окна на экране
        self.center()

    def compose_data(self):
        self.compose_data_window = WindowComposeData()
        self.compose_data_window.show()


# Запуск приложения
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())