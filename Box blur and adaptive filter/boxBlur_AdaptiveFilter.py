import cv2
import numpy
from matplotlib import pyplot as plt
import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QCheckBox, QComboBox
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


# Среднеарифметический и адаптивный усредняющий фильтры.
# Арифметический усредняющий
def box_filter(img2, n, m):
    # создаём копию изображения
    img = img2.copy()
    text = "Среднеарифметический фильтр " + str(n) + " x " + str(m)
    print(text)
    # вводим переменную средней яркости
    avrg_bright = int(0)

    # итерация по поксилям изображения
    for i in range(1, img.shape[0] - m):
        for j in range(1, img.shape[1] - n):
            avrg_bright = 0

            # итерация по маске отдельного пикселя
            for n_i in range(int(-(n-1)/2), int((n-1)/2 + 1)):
                for m_i in range(int(-(m-1)/2), int((m-1)/2 + 1)):
                    avrg_bright += img[i - n_i][j - m_i]

            # присваиваем пикселю, среднее значение яркости маски
            img[i][j] = avrg_bright/(m*n)
    hist_calc(img, text)
    return img


# Адаптивный усредняющий фильтр
def adaptive_filter(image, n, m):
    # создаём копию изображения
    img = image.copy()
    text = "Адаптивный фильтр " + str(n) + " x " + str(m)
    # вводим переменную средней яркости
    avrg_bright = int(0)
    disp_noise = int(0)
    De = 1000
    # итерация по поксилям изображения
    for i in range(1, image.shape[0] - m):
        for j in range(1, image.shape[1] - n):
            avrg_bright = 0
            disp_noise = 0
            # вычисление средней яркости
            for n_i in range(int(-(n - 1) / 2), int((n - 1) / 2 + 1)):
                for m_i in range(int(-(m - 1) / 2), int((m - 1) / 2 + 1)):
                    avrg_bright += img[i - n_i][j - m_i]
            # значение средней яркости для окрестности
            avrg_bright /= m * n

            # вычисление дисперсии
            for n_i in range(int(-(n - 1) / 2), int((n - 1) / 2 + 1)):
                for m_i in range(int(-(m - 1) / 2), int((m - 1) / 2 + 1)):
                    disp_noise += ((img[i][j] - avrg_bright) ** 2)
            # значение дисперсии для окрестности
            disp_noise /= m * n
            if disp_noise < De:
                img[i][j] = avrg_bright
            else: img[i][j] = img[i][j] - (De/disp_noise)*(img[i][j] - avrg_bright)
            #if disp_noise > De:
            #    img[i][j] = img[i][j]
            #if abs(disp_noise - De) < De:
            #    img[i][j] = avrg_bright
            #else: img[i][j] = img[i][j]
    hist_calc(img, text)
    return img


# Подсчёт и отображение гистограмм
def hist_calc(source_img, text):
    # Создание гистограмм
    plt.hist(source_img.ravel(), 256, [0, 256])
    # Вывод гистограмм
    plt.title(text)
    plt.show()

# класс создания окна интерфейса
class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Drop Image Here \n\n')
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #999
            }
        ''')

    def setPixmap(self, image):
        super().setPixmap(image)


# класс запуска интерфейса
class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        # создание окна
        self.resize(500, 500)
        self.setAcceptDrops(True)
        main_layout = QVBoxLayout()
        # кнопка
        self.button = QPushButton("Calculate")
        main_layout.addWidget(self.button)

        self.filter_type = QComboBox()
        # выбор фильтра
        self.filter_type.addItem('Adaptive filter', ['3 x 3', '5 x 5', '7 x 7', '9 x 9'])
        self.filter_type.addItem('Box blur filter', ['3 x 3', '5 x 5', '7 x 7', '9 x 9'])
        main_layout.addWidget(self.filter_type)
        self.filter_size = QComboBox()

        # действие при нажатии на кнопку
        self.button.clicked.connect(lambda: self.calculate(self.filter_type.currentIndex(), self.filter_size.currentIndex()))

        main_layout.addWidget(self.filter_size)
        self.filter_type.currentIndexChanged.connect(self.update_filters)
        self.update_filters(self.filter_type.currentIndex())
        self.photoViewer = ImageLabel()
        main_layout.addWidget(self.photoViewer)

        self.setLayout(main_layout)

    # Обновление значений из выпадающих списков
    def update_filters(self, index):
        self.filter_size.clear()
        cities = self.filter_type.itemData(index)
        if cities:
            self.filter_size.addItems(cities)

    # Функции для поодержки Drag and Drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        global file_path
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.set_image(file_path)
            print(file_path)
            event.accept()
        else:
            event.ignore()

    def set_image(self, file_path):
        self.photoViewer.setPixmap(QPixmap(file_path))

    # Вызов основных фильтров
    def calculate(self, f_type, nm):
        print(f_type, nm)
        # выбор индекса
        if nm == 0:
            n = m = 3
        if nm == 1:
            n = m = 5
        if nm == 2:
            n = m = 7
        if nm == 3:
            n = m = 9
        img2 = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        # обработка адаптивным фильтром, в случае выбора в выпадающем списке
        if f_type == 0:
            img2 = adaptive_filter(img2, n, m)
        # обработка среднеарифметическим фильтром, в случае выбора в выпадающем списке
        if f_type == 1:
            img2 = box_filter(img2, n, m)
        # self.hist_calc(img2)
        # img2 = cv2.resize(img2, (1200, 1200))
        cv2.imwrite("$yourPath$/yourImage", img2)
        self.set_image("$yourPath$/yourImage")


# Запуск основной части программы
app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())
