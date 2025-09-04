from PyQt5 import QtCore, QtGui, QtWidgets


class Test(QtWidgets.QMainWindow):

    def __init__(self):
        super(Test, self).__init__()

    def center(self):
        # Получение информации о экране
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()

        # Вычисление координат для центрирования
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2

        # Установка нового положения окна
        self.move(x, y)