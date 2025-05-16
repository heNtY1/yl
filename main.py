import io
import os
import sys
import requests

from PyQt6 import uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_address = 'https://static-maps.yandex.ru/v1?'
        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.initUI()

    def initUI(self):
        uic.loadUi('ui_file.ui', self)
        self.ok_button.clicked.connect(self.getImage)
        self.search_button.clicked.connect(self.shere)
        self.reset_button.clicked.connect(self.reset)
        self.wight_Edit.setText('55.755811')
        self.high_Edit.setText('37.617617')
        self.size_Edit.setText('0.05')
        self.a = self.wight_Edit.text()
        self.b = self.high_Edit.text()
        self.c = self.size_Edit.text()

    def reset(self):
        server_address = 'https://static-maps.yandex.ru/v1?'
        api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.ll_spn = f'll={self.b},{self.a}&spn={self.c},{self.c}'
        map_request = f"{server_address}{self.ll_spn}&apikey={api_key}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.map_label.resize(640, 300)
        self.map_label.setPixmap(self.pixmap)

    def shere(self):
        server_address = 'http://geocode-maps.yandex.ru/1.x/?'
        api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        geocode = self.search_Edit.text()
        geocoder_request = f'{server_address}apikey={api_key}&geocode={geocode}&format=json'
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"].split()
            self.wight_Edit.setText(toponym_coodrinates[1])
            self.high_Edit.setText(toponym_coodrinates[0])
            self.metka = f'pt={toponym_coodrinates[0]},{toponym_coodrinates[1]}'
            self.getImage()
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")

    def getImage(self):
        self.a = self.wight_Edit.text()
        self.b = self.high_Edit.text()
        self.c = self.size_Edit.text()
        self.metka = f'pt={self.b},{self.a}'
        self.imagee()

    def imagee(self):
        server_address = 'https://static-maps.yandex.ru/v1?'
        api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.ll_spn = f'll={self.b},{self.a}&spn={self.c},{self.c}'
        map_request = f"{server_address}{self.ll_spn}&{self.metka}&apikey={api_key}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap = QPixmap(self.map_file)
        self.map_label.resize(640, 300)
        self.map_label.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.a = float(self.a)
            self.a += 0.01 * float(self.c) * 50
            self.wight_Edit.setText(str(self.a))
            self.high_Edit.setText(str(self.b))
            self.imagee()
        if event.key() == Qt.Key.Key_Down:
            self.a = float(self.a)
            self.a -= 0.01 * float(self.c) * 50
            self.wight_Edit.setText(str(self.a))
            self.high_Edit.setText(str(self.b))
            self.imagee()
        if event.key() == 16777249:
            self.b = float(self.b)
            self.b += 0.01 * float(self.c) * 50
            self.wight_Edit.setText(str(self.a))
            self.high_Edit.setText(str(self.b))
            self.imagee()
        if event.key() == 16777251:
            self.b = float(self.b)
            self.b -= 0.01 * float(self.c) * 50
            self.wight_Edit.setText(str(self.a))
            self.high_Edit.setText(str(self.b))
            self.imagee()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
