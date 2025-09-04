import sys
import time
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import QThread, pyqtSignal

class Worker(QThread):
    progress = pyqtSignal(str)  # Сигнал для передачи промежуточных результатов
    finished = pyqtSignal()  # Сигнал для уведомления о завершении работы

    def __init__(self, iterations, delay, message, parent=None):
        super().__init__(parent)
        self.iterations = iterations  # Сохраняем количество итераций
        self.delay = delay  # Сохраняем задержку
        self.message = message  # Сохраняем сообщение

    def run(self):
        for i in range(self.iterations):
            time.sleep(5)  # Симуляция длительной задачи
            self.progress.emit(f"{0} - Шаг {i + 1} завершен")  # Отправляем обновление
        self.finished.emit()  # Уведомляем о завершении работы

class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Результат работы")
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout(self)  # Создаем layout и связываем его с текущим виджетом
        self.label = QLabel("Ожидание результата...", self)  # Начальный текст
        layout.addWidget(self.label)  # Добавляем QLabel в layout
        self.setLayout(layout)  # Устанавливаем layout для окна

    def update_label(self, message):
        self.label.setText(message)  # Обновляем текст QLabel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Многопоточность в PyQt5")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout(self)

        self.button = QPushButton("Начать работу", self)
        self.button.clicked.connect(self.start_work)  # Подключаем кнопку к методу
        layout.addWidget(self.button)

        self.setLayout(layout)

    def start_work(self):
        iterations = 5  # Количество итераций
        delay = 1  # Задержка в секундах
        message = "Процесс"  # Сообщение для обновления

        self.result_window = ResultWindow()  # Создаем новое окно
        self.result_window.show()  # Показываем новое окно

        self.thread = Worker(iterations, delay, message)  # Передаем параметры в Worker
        self.thread.progress.connect(self.result_window.update_label)  # Подключаем сигнал к методу обновления
        self.thread.finished.connect(self.on_finished)  # Подключаем сигнал завершения
        self.thread.start()  # Запускаем поток

    def on_finished(self):
        self.result_window.update_label("Работа завершена!")  # Обновляем текст по завершении

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
