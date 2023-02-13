import cv2
from matplotlib import pyplot as plt
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QCheckBox, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


# Среднеарифметический и сигма фильтры.
# Среднеарифметический фильтр
def arithmetic_mean_filter(img2, n, m):
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
    histogram(img, text)
    return img


# сигма фильтр
def sigma_filter(img2, n, m):
    # создаём копию изображения
    img = img2.copy()
    text = "Сигма фильтр " + str(n) + " x " + str(m)
    avrg_bright = int(0)
    # Заданное пользовательское значение дисперсии шума
    De = 30
    # Заданное пороговое значение
    brt_treshhold = De * 1
    # итерация по поксилям изображения
    for i in range(1, img.shape[0] - m):
        for j in range(1, img.shape[1] - n):
            avrg_bright = 0
            count = 0
            # вычисление средней яркости
            for n_i in range(int(-(n - 1) / 2), int((n - 1) / 2 + 1)):
                for m_i in range(int(-(m - 1) / 2), int((m - 1) / 2 + 1)):
                    if int(img[i - n_i][j - m_i]) - int(img[i][j]) < brt_treshhold:
                        count += 1
                        avrg_bright += img[i - n_i][j - m_i]
            # значение средней яркости для окрестности
            # print(count)
            avrg_bright /= count
            img[i][j] = avrg_bright

    histogram(img, text)
    return img


# Создание гистограмм
def histogram(source_img, text):
    # Создание гистограмм
    plt.hist(source_img.ravel(), bins = 256)
    # Вывод гистограмм
    plt.title(text)
    plt.show()


# класс создания интерфейса
class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Кидайте сюда картинку \n\n')
        self.setStyleSheet('''
            QLabel{
                border: 2px dashed #777
            }
        ''')

    def setPixmap(self, image):
        super().setPixmap(image)


# класс запуска интерфейса
class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        # Создание окна
        self.resize(400, 400)
        self.setAcceptDrops(True)
        main_layout = QVBoxLayout()
        # Создание кнопки
        self.button = QPushButton("Обработать картинку")


        self.filter_type = QComboBox()
        # Выбор фильтра
        self.filter_type.addItem('Сигма фильтр',
                                 ['Размер маски : 3 x 3',
                                  'Размер маски : 5 x 5',
                                  'Размер маски : 7 x 7'])
        self.filter_type.addItem('Среднеарифметический фильтр',
                                 ['Размер маски : 3 x 3',
                                  'Размер маски : 5 x 5',
                                  'Размер маски : 7 x 7'])
        main_layout.addWidget(self.filter_type)
        self.filter_size = QComboBox()

        # Действие при нажатии на кнопку
        self.button.clicked.connect(lambda: self.calculate(self.filter_type.currentIndex(), self.filter_size.currentIndex()))

        main_layout.addWidget(self.filter_size)
        main_layout.addWidget(self.button)
        self.filter_type.currentIndexChanged.connect(self.update_filters)
        self.update_filters(self.filter_type.currentIndex())
        self.photoViewer = ImageLabel()
        main_layout.addWidget(self.photoViewer)

        self.setLayout(main_layout)

    # Обновление выпадающего списка
    def update_filters(self, index):
        self.filter_size.clear()
        filters = self.filter_type.itemData(index)
        if filters:
            self.filter_size.addItems(filters)

    # Drag and Drop элемент
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
        src_img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        # обработка адаптивным фильтром, в случае выбора в выпадающем списке
        if f_type == 0:
            post_img = sigma_filter(src_img, n, m)
        # обработка среднеарифметическим фильтром, в случае выбора в выпадающем списке
        if f_type == 1:
            post_img = arithmetic_mean_filter(src_img, n, m)
        cv2.imwrite("$yourPath$", post_img)
        self.set_image("$yourPath$/post_processed.png")


# Запуск основной части программы
app = QApplication(sys.argv)
demo = AppDemo()
# Показ интерфейса пользователю
demo.show()
sys.exit(app.exec_())
