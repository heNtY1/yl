import sys
import os
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QLabel,
                             QMessageBox, QCheckBox)
from PyQt6.QtGui import QPixmap, QKeyEvent
from PyQt6.QtCore import Qt


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_address = 'https://static-maps.yandex.ru/v1?'
        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.geocoder_api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        self.show_postal_code = False  # Флаг для отображения почтового индекса
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Яндекс Карты с почтовым индексом")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        control_layout = QHBoxLayout()

        self.wight_Edit = QLineEdit('55.755811')
        self.wight_Edit.setPlaceholderText("Широта")
        control_layout.addWidget(self.wight_Edit)

        self.high_Edit = QLineEdit('37.617617')
        self.high_Edit.setPlaceholderText("Долгота")
        control_layout.addWidget(self.high_Edit)

        self.size_Edit = QLineEdit('0.05')
        self.size_Edit.setPlaceholderText("Масштаб")
        control_layout.addWidget(self.size_Edit)

        self.ok_button = QPushButton("Нарисовать")
        self.ok_button.clicked.connect(self.getImage)
        control_layout.addWidget(self.ok_button)

        self.search_Edit = QLineEdit()
        self.search_Edit.setPlaceholderText("Поиск адреса")
        control_layout.addWidget(self.search_Edit)

        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.shere)
        control_layout.addWidget(self.search_button)

        self.reset_button = QPushButton("Сброс")
        self.reset_button.clicked.connect(self.reset)
        control_layout.addWidget(self.reset_button)

        self.postal_checkbox = QCheckBox("Показать почтовый индекс")
        self.postal_checkbox.stateChanged.connect(self.toggle_postal_code)
        control_layout.addWidget(self.postal_checkbox)

        layout.addLayout(control_layout)

        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_label.setMinimumSize(600, 400)
        layout.addWidget(self.map_label)

        self.address_label = QLabel()
        self.address_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.address_label)

    def toggle_postal_code(self, state):
        self.show_postal_code = state == Qt.CheckState.Checked.value
        if hasattr(self, 'current_address'):
            self.update_address_display()

    def update_address_display(self):
        if self.show_postal_code and hasattr(self, 'postal_code'):
            self.address_label.setText(f"{self.current_address} (Почтовый индекс: {self.postal_code})")
        else:
            self.address_label.setText(self.current_address if hasattr(self, 'current_address') else "")

    def reset(self):
        self.ll_spn = f'll={self.high_Edit.text()},{self.wight_Edit.text()}&spn={self.size_Edit.text()},{self.size_Edit.text()}'
        map_request = f"{self.server_address}{self.ll_spn}&apikey={self.api_key}"
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
        self.map_label.setPixmap(self.pixmap)

        if hasattr(self, 'current_address'):
            del self.current_address
        self.address_label.setText("")

    def shere(self):
        geocode = self.search_Edit.text()
        geocoder_request = f'http://geocode-maps.yandex.ru/1.x/?apikey={self.geocoder_api_key}&geocode={geocode}&format=json'
        response = requests.get(geocoder_request)

        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

            toponym_coodrinates = toponym["Point"]["pos"].split()
            self.wight_Edit.setText(toponym_coodrinates[1])
            self.high_Edit.setText(toponym_coodrinates[0])
            self.metka = f'pt={toponym_coodrinates[0]},{toponym_coodrinates[1]}'

            self.current_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            self.postal_code = toponym["metaDataProperty"]["GeocoderMetaData"].get("Address", {}).get("postal_code",
                                                                                                      "не указан")
            self.update_address_display()

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
        self.ll_spn = f'll={self.b},{self.a}&spn={self.c},{self.c}'
        map_request = f"{self.server_address}{self.ll_spn}&{self.metka}&apikey={self.api_key}"
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
        self.map_label.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.a = float(self.wight_Edit.text())
            self.a += 0.01 * float(self.size_Edit.text()) * 50
            self.wight_Edit.setText(str(self.a))
            self.high_Edit.setText(self.high_Edit.text())
            self.imagee()
        elif event.key() == Qt.Key.Key_Down:
            self.a = float(self.wight_Edit.text())
            self.a -= 0.01 * float(self.size_Edit.text()) * 50
            self.wight_Edit.setText(str(self.a))
            self.high_Edit.setText(self.high_Edit.text())
            self.imagee()
        elif event.key() == Qt.Key.Key_Left:
            self.b = float(self.high_Edit.text())
            self.b -= 0.01 * float(self.size_Edit.text()) * 50
            self.high_Edit.setText(str(self.b))
            self.wight_Edit.setText(self.wight_Edit.text())
            self.imagee()
        elif event.key() == Qt.Key.Key_Right:
            self.b = float(self.high_Edit.text())
            self.b += 0.01 * float(self.size_Edit.text()) * 50
            self.high_Edit.setText(str(self.b))
            self.wight_Edit.setText(self.wight_Edit.text())
            self.imagee()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.exit(app.exec())