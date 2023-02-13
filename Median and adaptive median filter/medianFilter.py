import cv2
import numpy as np
import statistics
from matplotlib import pyplot as plt
import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


# Обычный и адаптивный медианный фильтры
# медианный фильтр
def med_filter(img2, n, m):
    # создаём копию изображения
    img = img2.copy()
    text = "Медианный фильтр " + str(n) + " x " + str(m)
    # вводим массив значений для медианы
    med = np.ndarray(n*m)

    # итерация по пикселям изображения
    for i in range(1, img.shape[0] - m):
        for j in range(1, img.shape[1] - n):
            k = 0
            # итерация по окрестности отдельного пикселя
            for n_i in range(int(-(n-1)/2), int((n-1)/2 + 1)):
                for m_i in range(int(-(m-1)/2), int((m-1)/2 + 1)):
                    med[k] = img[i - n_i][j - m_i]
                    k += 1
            # присваиваем пикселю, медиану отсортированного массива элементов окрестности
            img[i][j] = statistics.median(sorted(med))
    hist_calc(img, text)
    return img


# Адаптивный усредняющий фильтр
def adaptive_filter(image, n, m):
    # создаём копию изображения
    img = image.copy()
    text = "Адаптивный медианный фильтр " + str(n) + " x " + str(m)
    # вводим массив значений для медианы
    Smax = 15
    # итерация по пикселям изображения
    def loop_adaptive_med(m,n,image, Smax):
            med = np.ndarray(n * m)
            k = 0
            # итерация по окрестности отдельного пикселя
            for n_i in range(int(-(n - 1) / 2), int((n - 1) / 2 + 1)):
                for m_i in range(int(-(m - 1) / 2), int((m - 1) / 2 + 1)):
                    med[k] = image[i - n_i][j - m_i]
                    k += 1
            # медиана области
            med_in_arr = statistics.median(sorted(med))
            # минимум области
            min_in_arr = min(med)
            # максимум области
            max_in_arr = max(med)

            # основное условие
            if min_in_arr < med_in_arr < max_in_arr:
                if min_in_arr < image[i][j] < max_in_arr:
                    return image[i][j]
                else:
                    return statistics.median(sorted(med))
            else:
                # увеличение окрестности
                m+=2
                n+=2
                if m <= Smax:
                    return loop_adaptive_med(m, n, image, Smax)
                else:
                    return statistics.median(sorted(med))

    for i in range(int(Smax/2), img.shape[0] - int(Smax/2)):
        for j in range(int(Smax/2), img.shape[1] - int(Smax/2)):
            img[i][j] = loop_adaptive_med(m, n, image, Smax)
    hist_calc(img, text)
    return img


# Подсчёт и отображение гистограмм
def hist_calc(source_img, text):
    # Создание гистограмм
    plt.hist(source_img.ravel(), bins = 256)
    # Вывод гистограмм
    plt.title(text)
    plt.show()

# класс создания окна интерфейса
class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Картинку сюда \n\n')
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
        self.button = QPushButton("Рассчитать")
        main_layout.addWidget(self.button)

        self.label = QLabel("ОБЫЧНЫЙ И АДАПТИВНЫЙ МЕДИАННЫЙ ФИЛЬТРЫ")
        main_layout.addWidget(self.label)

        self.filter_type = QComboBox()
        # выбор фильтра
        self.filter_type.addItem('Адаптивный Медианный фильтр', ['3 x 3', '5 x 5', '7 x 7', '9 x 9'])
        self.filter_type.addItem('Медианный фильтр', ['3 x 3', '5 x 5', '7 x 7', '9 x 9'])
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
        size = self.filter_type.itemData(index)
        if size:
            self.filter_size.addItems(size)

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
            img2 = med_filter(img2, n, m)
        # self.hist_calc(img2)
        # img2 = cv2.resize(img2, (1200, 1200))
        cv2.imwrite("$yourPath$", img2)
        self.set_image("$yourPath$/img2.png")


# Запуск основной части программы
app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())
