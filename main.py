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
        self.show_postal_code = False
        self.found_addresses = []  # Список для хранения найденных адресов
        self.current_address_index = -1  # Индекс текущего отображаемого адреса
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Яндекс Карты с почтовым индексом")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Панель управления
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

        # Чекбокс для почтового индекса
        self.postal_checkbox = QCheckBox("Показать почтовый индекс")
        self.postal_checkbox.stateChanged.connect(self.toggle_postal_code)
        control_layout.addWidget(self.postal_checkbox)

        # Кнопки для навигации по найденным адресам
        self.prev_address_btn = QPushButton("<")
        self.prev_address_btn.clicked.connect(self.show_prev_address)
        control_layout.addWidget(self.prev_address_btn)

        self.next_address_btn = QPushButton(">")
        self.next_address_btn.clicked.connect(self.show_next_address)
        control_layout.addWidget(self.next_address_btn)

        layout.addLayout(control_layout)

        # Отображение карты
        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_label.setMinimumSize(600, 400)
        layout.addWidget(self.map_label)

        # Отображение адреса
        self.address_label = QLabel()
        self.address_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.address_label)

    def toggle_postal_code(self, state):
        """Переключатель почтового индекса с автоматическим обновлением"""
        self.show_postal_code = state == Qt.CheckState.Checked.value
        self.update_address_display()

    def update_address_display(self):
        """Обновление отображения адреса с учетом текущего состояния переключателя"""
        if self.current_address_index >= 0 and self.found_addresses:
            address_info = self.found_addresses[self.current_address_index]
            if self.show_postal_code and address_info['postal_code']:
                self.address_label.setText(
                    f"{address_info['address']} (Почтовый индекс: {address_info['postal_code']})")
            else:
                self.address_label.setText(address_info['address'])

    def show_prev_address(self):
        """Показать предыдущий адрес из списка найденных"""
        if len(self.found_addresses) > 1:
            self.current_address_index = (self.current_address_index - 1) % len(self.found_addresses)
            self.update_address_display()
            self.show_current_address_on_map()

    def show_next_address(self):
        """Показать следующий адрес из списка найденных"""
        if len(self.found_addresses) > 1:
            self.current_address_index = (self.current_address_index + 1) % len(self.found_addresses)
            self.update_address_display()
            self.show_current_address_on_map()

    def show_current_address_on_map(self):
        """Отобразить текущий адрес на карте"""
        if self.current_address_index >= 0 and self.found_addresses:
            address_info = self.found_addresses[self.current_address_index]
            self.wight_Edit.setText(str(address_info['lat']))
            self.high_Edit.setText(str(address_info['lon']))
            self.getImage()

    def reset(self):
        """Сброс поиска"""
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

        # Очищаем список адресов при сбросе
        self.found_addresses = []
        self.current_address_index = -1
        self.address_label.setText("")

    def shere(self):
        """Поиск адреса с сохранением всех найденных вариантов"""
        geocode = self.search_Edit.text()
        if not geocode:
            return

        geocoder_request = f'http://geocode-maps.yandex.ru/1.x/?apikey={self.geocoder_api_key}&geocode={geocode}&format=json&results=5'
        response = requests.get(geocoder_request)

        if response:
            json_response = response.json()
            features = json_response["response"]["GeoObjectCollection"]["featureMember"]

            # Сохраняем все найденные адреса
            self.found_addresses = []
            for feature in features:
                toponym = feature["GeoObject"]
                address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                postal_code = toponym["metaDataProperty"]["GeocoderMetaData"].get("Address", {}).get("postal_code", "")
                coords = toponym["Point"]["pos"].split()
                self.found_addresses.append({
                    'address': address,
                    'postal_code': postal_code,
                    'lat': coords[1],
                    'lon': coords[0]
                })

            if self.found_addresses:
                self.current_address_index = 0
                self.update_address_display()
                self.show_current_address_on_map()
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")

    def getImage(self):
        """Обновление карты по текущим координатам"""
        self.a = self.wight_Edit.text()
        self.b = self.high_Edit.text()
        self.c = self.size_Edit.text()
        self.metka = f'pt={self.b},{self.a}'
        self.imagee()

    def imagee(self):
        """Загрузка и отображение карты"""
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
        """Обработка клавиш для перемещения по карте"""
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