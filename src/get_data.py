import pathlib
import time

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QMovie

from src.common_class import Test

import pandas as pd
import datetime as dt
import os
import shutil
import warnings

from src.utils_get_data import format_value, merge_cost


class ResultWindow(Test):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Результат выполнения программы")
        self.setGeometry(0, 0, 400, 600)

        self.center()


class LoadingDataWindow(Test):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Загрузка данных")
        self.setGeometry(0, 350, 400, 300)

        self.count = 0
        self.length = 0

        self.label_loading = QtWidgets.QLabel(f"Загружаю список журналов...")

        self.label_loading_book = QtWidgets.QLabel()

        self.label_gif = QtWidgets.QLabel()
        self.movie = QMovie("source/loading.gif")
        self.label_gif.setMovie(self.movie)
        self.label_gif.setFixedSize(200, 200)
        self.label_gif.setScaledContents(True)

        self.movie.start()

        self.layout_loading = QtWidgets.QVBoxLayout(self)
        self.layout_loading.addWidget(self.label_loading)
        self.layout_loading.addWidget(self.label_loading_book)
        self.layout_loading.addWidget(self.label_gif)

        self.layout_loading.setAlignment(self.label_loading, QtCore.Qt.AlignCenter)
        self.layout_loading.setAlignment(self.label_loading_book, QtCore.Qt.AlignCenter)
        self.layout_loading.setAlignment(self.label_gif, QtCore.Qt.AlignCenter)

        self.container = QtWidgets.QWidget()
        self.container.setLayout(self.layout_loading)
        self.setCentralWidget(self.container)

        # self.setLayout(self.layout_loading)
        self.center()

    def update_progress(self, message):
        self.label_loading.setText(message)

    def update_progress_book(self, message):
        text, color = message.split(";")
        self.label_loading_book.setText(text)

        if color == "green":
            self.label_loading_book.setStyleSheet("color: green;")
        else:
            self.label_loading_book.setStyleSheet("color: red;")


class WindowComposeData(Test):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Составление свода")
        self.setGeometry(0, 350, 400, 300)

        self.label = QtWidgets.QLabel("Укажите параметры:")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))

        self.checkbox = QtWidgets.QCheckBox("Добавить стоимость")

        # Создание поля для выбора даты
        self.label_1 = QtWidgets.QLabel("Дата начала: ")

        self.date_edit_start = QtWidgets.QDateEdit()
        self.date_edit_start.setDate(QtCore.QDate.currentDate())  # Установка текущей даты по умолчанию
        self.date_edit_start.setDisplayFormat("dd.MM.yyyy")  # Формат отображения даты

        # Создание поля для выбора даты
        self.label_2 = QtWidgets.QLabel("Дата окончания: ")
        self.date_edit_end = QtWidgets.QDateEdit()
        self.date_edit_end.setDate(QtCore.QDate.currentDate())  # Установка текущей даты по умолчанию
        self.date_edit_end.setDisplayFormat("dd.MM.yyyy")  # Формат отображения даты

        self.layout_1 = QtWidgets.QHBoxLayout()
        self.layout_1.addWidget(self.label_1)
        self.layout_1.addWidget(self.date_edit_start)

        self.group = QtWidgets.QWidget()
        self.group.setLayout(self.layout_1)

        self.layout_2 = QtWidgets.QHBoxLayout()
        self.layout_2.addWidget(self.label_2)
        self.layout_2.addWidget(self.date_edit_end)

        self.group_2 = QtWidgets.QWidget()
        self.group_2.setLayout(self.layout_2)

        self.layout_dates = QtWidgets.QVBoxLayout()
        self.layout_dates.addWidget(self.group)
        self.layout_dates.addWidget(self.group_2)
        # layout_dates.setSpacing(0)

        self.container_dates = QtWidgets.QWidget()
        self.container_dates.setLayout(self.layout_dates)

        self.button_run = QtWidgets.QPushButton("Составить")
        self.button_run.setFixedSize(200, 80)
        self.button_run.clicked.connect(self.get_data)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.container_dates)
        self.layout.addWidget(self.button_run)

        self.layout.setAlignment(self.checkbox, QtCore.Qt.AlignCenter)
        self.layout.setAlignment(self.button_run, QtCore.Qt.AlignCenter)

        self.container = QtWidgets.QWidget()
        self.container.setLayout(self.layout)

        self.setCentralWidget(self.container)

        # Центрирование окна на экране
        self.center()


    def get_data(self):
        cost_adding = self.checkbox.isChecked()

        file_path = str(pathlib.Path("./data/Пути.xlsx").resolve())
        start_date = self.date_edit_start.date().toString('dd.MM.yyyy')
        end_date = self.date_edit_end.date().toString('dd.MM.yyyy')

        self.close()

        self.loading_window = LoadingDataWindow()
        self.loading_window.show()

        self.thread = Worker(file_path, start_date, end_date, cost_adding=cost_adding)
        self.thread.progress_common.connect(self.loading_window.update_progress)
        self.thread.progress_number.connect(self.loading_window.update_progress_book)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()


    def on_finished(self):
        self.loading_window.close()

        self.result_window = ResultWindow()
        self.result_window.show()


class Worker(QThread):

    progress_common = pyqtSignal(str)
    progress_number = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self,
                 file_path,
                 start_date,
                 end_date,
                 sheet="Производственный контроль",
                 cost_adding=False):
        super().__init__()

        self.file_path = file_path
        self.start_date = start_date
        self.end_date = end_date
        self.sheet = sheet
        self.cost_adding = cost_adding


    def run(self) -> None:
        """Функция получает данные времени и возвращает таблицу excel с анализами, проведенными за указанный период"""

        # Игнорировать все предупреждения
        warnings.filterwarnings("ignore")

        # Преобразование даты в нужный формат
        start_date_format = dt.datetime.strptime(self.start_date, "%d.%m.%Y")
        start_date_format = start_date_format.strftime("%Y-%m-%d")

        end_date_format = dt.datetime.strptime(self.end_date, "%d.%m.%Y")
        end_date_format = end_date_format.strftime("%Y-%m-%d")

        # Форматирование пути до файла со сводом
        file_path = self.file_path.replace("\\", "/")

        # Проверка, что путь до файла со сводом не указан и файл находится в текущей директории
        if not file_path:
            file_path = "Пути.xlsx"

        # Попытка прочитать файл Excel и создать DataFrame на его основе
        try:
            df = pd.read_excel(file_path)
        except Exception as error:
            raise error

        # Название столбца, в котором в файле Свод.xlsx в ПЕРВОЙ книге перечислены пути до журналов
        column_name = "FilePath"

        # Получение списка путей до журналов без пустых строк
        data = df[column_name].dropna().tolist()

        # Пустой список, куда добавляются DataFrames после фильтрации каждого журнала по дате
        dataframes = []

        # Счетчик для подсчета общего количества журналов
        count = 0

        # Счетчик для подсчета количества считываемых журналов
        count_ok = 0

        base_folder = "Свод"

        # Проверка на валидность корневой директории
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)

        # Директория, куда будут копироваться журналы Excel ДО фильтрации
        directory_name = dt.datetime.now().strftime("%d.%m.%Y_%H-%M")

        # Проверка на валидность директории
        if not os.path.exists(f"Свод\\{directory_name}"):
            os.makedirs(f"Свод\\{directory_name}")

        # Цикл создания DataFrames по каждому пути
        for i in data:

            count += 1

            file_name = i.split("\\")[-1]

            try:
                # Название листа, где находится таблица
                if self.sheet == "":
                    sheet_name = "Производственный контроль"
                else:
                    sheet_name = self.sheet

                # Полный путь для нового файла
                destination_file = os.path.join(
                    f"{base_folder}\\{directory_name}", f"Свод_{file_name}"
                )

                # Создание копии файла
                shutil.copy(i, destination_file)

                # Попытка прочитать файл Excel по его пути в книге sheet_name и создать df только по первым 3-м строкам
                df = pd.read_excel(i, sheet_name=sheet_name, nrows=3)

                # Проверка, что значение "Сцепка" содержится внутри таблицы
                # (проверка исключает, что заданное значение находится в заголовке)
                # Она возвращает DataFrame того же размера, где каждое значение заменяется на True,
                # если оно содержится в заданном наборе, и на False, если нет.

                result = df.isin(["Сцепка"])
                # result = df.isin(["Юридическое лицо"])

                # Проверка, есть ли хотя бы одно истинное (True) значение в объекте.
                # В зависимости от параметра axis (0-столбцы (по умолчанию), 1-строки)
                # Первый вызов any() создает Series, второй только одно логическое значение
                if not result.any().any():
                    # Получение индекса столбца под названием "Сцепка"
                    # У df.columns.get_loc() - получение индекса (строки), у df.index.get_loc() - получение номера столбца

                    start_col = df.columns.get_loc("Сцепка")
                    # start_col = df.columns.get_loc("Юридическое лицо")

                    header = -1
                else:
                    indices = result.stack()[result.stack()].index
                    header = int(indices[0][0])
                    start_col = int(indices[0][1][-2:])

                df = pd.read_excel(i, sheet_name=sheet_name, header=header + 1)

                # Удаление лишних пробелов в названиях столбцов
                df.columns = df.columns.str.strip().str.replace(r"\s+", " ", regex=True)

                result = df.columns.tolist()

                # Переименование столбца
                if "Результаты PQ" in result:
                    df.rename(columns={"Результаты PQ": "Результат PQ"}, inplace=True)

                # Переименование столбца
                if "Результат" in result:
                    df.rename(columns={"Результат": "Результат PQ"}, inplace=True)

                # Поиск номера столбца по наименование
                end_col = df.columns.tolist().index("Отправка протокола")

                # Фильтрация df по диапазону строк и столбцов (разделяются через запятую)
                df = df.iloc[:, start_col : end_col + 1]

                # Фильтрация строк, где указанный столбец не пустой
                df = df[df["Наименование исследования"].notna()]

                # Удаление лишних пробелов в наименовании исследования
                df["Наименование исследования"] = df["Наименование исследования"].apply(lambda x: x.strip())

                # Если вы хотите также исключить строки с пустыми строками
                df = df[df["Наименование исследования"].astype(bool)]

                for j in df.columns.tolist():
                    df[j] = df[j].astype(str)

                df["Наименование исследования"] = df[
                    "Наименование исследования"
                ].str.lower()

                # Добавление столбца с указанием пути до файла
                df["Путь до файла"] = i

                # Преобразование типа данных столбца в datetime
                df["Дата подготовки образца"] = pd.to_datetime(
                    df["Дата подготовки образца"], errors='coerce'
                )

                df = df[df["Дата подготовки образца"].notna()]

                # Преобразование даты в формате str "YYYY-MM-DD" в формат Timestamp
                start_date_format = pd.Timestamp(start_date_format)
                end_date_format = pd.Timestamp(end_date_format)

                # Фильтрация df по дате
                df = df[
                    (df["Дата подготовки образца"] >= start_date_format)
                    & (df["Дата подготовки образца"] <= end_date_format)
                ]

                if not df.empty:
                    # Добавление DataFrame в список dataframes
                    dataframes.append(df)
                else:
                    raise ValueError("НЕТ ИССЛЕДОВАНИЙ")

                self.progress_number.emit(f"{file_name};green")

            except Exception as error:
                print(f"{count}. {file_name} - {str(error)}")

                self.progress_number.emit(f"{file_name};red")

            else:
                count_ok += 1

                print(f"{count}. {file_name} - УСПЕШНО")

            self.progress_common.emit(f"Загружено журналов: {count}/{len(data)}")
            time.sleep(2)


        try:
            # Объединение всех DataFrame в один
            combined_df = pd.concat(dataframes, ignore_index=True)

            # Укажите имя столбца, который вы хотите переместить
            column_to_move = "Путь до файла"  # Замените на имя вашего столбца
            new_position = 0  # Укажите новую позицию (индекс) для перемещения столбца

            # Перемещение столбца
            # Сначала извлекаем столбец
            column_data = combined_df.pop(column_to_move)

            # Затем вставляем его на новую позицию(номер столбца, имя столбца, данные столбца)
            combined_df.insert(new_position, column_to_move, column_data)

            # Заполнение столбца КОЛ-ВО ОБРАЗЦОВ ДЛЯ СЕРОЛОГИИ
            combined_df["Количество анализов"] = combined_df.apply(
                lambda x: format_value(x), axis=1
            )

            if self.cost_adding:
                options = QtWidgets.QFileDialog.Options()
                file_path_cost, _ = QtWidgets.QFileDialog.getOpenFileName(
                    options=options,
                )
                self.progress_common.emit("Добавление стоимости к анализам...")
                self.progress_number.emit(" ; black")

                try:
                    df = merge_cost(combined_df, file_path_cost)
                    df["Стоимость всех анализов"] = df["Количество анализов"] * df["Стоимость"]
                except Exception as error:
                    print(error)
            else:
                df = combined_df


            # Создание файла свода по всем журналам в Excel
            df.to_excel(
                f"Свод/{directory_name}/Свод за {self.start_date} - {self.end_date}.xlsx", index=False
            )  # Замените на желаемое имя файла

        except Exception as error:
            print(error)
        else:
            print()
            print(f"Считано журналов: {count_ok}/{count}")
            if count == count_ok:
                print(f"Свод за {self.start_date} - {self.end_date}.xlsx создан УСПЕШНО")
            else:
                print(f"Свод за {self.start_date} - {self.end_date}.xlsx создан С НЕПОЛНЫМИ ДАННЫМИ")

        self.finished.emit()

