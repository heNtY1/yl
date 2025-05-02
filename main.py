import sys
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QLabel,
                             QMessageBox, QCheckBox)
from PyQt6.QtGui import QPixmap, QKeyEvent, QMouseEvent
from PyQt6.QtCore import Qt, QPoint


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_address = 'https://static-maps.yandex.ru/v1?'
        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.geocoder_api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        self.show_postal_code = False
        self.found_addresses = []
        self.current_address_index = -1
        self.map_pixmap = None
        self.map_rect = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Яндекс Карты с поиском по клику")
        self.setGeometry(100, 100, 800, 650)

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
        self.search_button.clicked.connect(self.search_address)  # Исправлено на search_address
        control_layout.addWidget(self.search_button)

        self.reset_button = QPushButton("Сброс")
        self.reset_button.clicked.connect(self.reset)
        control_layout.addWidget(self.reset_button)

        self.postal_checkbox = QCheckBox("Показать почтовый индекс")
        self.postal_checkbox.stateChanged.connect(self.toggle_postal_code)
        control_layout.addWidget(self.postal_checkbox)

        self.prev_address_btn = QPushButton("<")
        self.prev_address_btn.clicked.connect(self.show_prev_address)
        control_layout.addWidget(self.prev_address_btn)

        self.next_address_btn = QPushButton(">")
        self.next_address_btn.clicked.connect(self.show_next_address)
        control_layout.addWidget(self.next_address_btn)

        layout.addLayout(control_layout)

        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_label.setMinimumSize(600, 400)
        self.map_label.mousePressEvent = self.map_click_handler
        layout.addWidget(self.map_label)

        self.address_label = QLabel()
        self.address_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.address_label)

    def map_click_handler(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.map_pixmap:
            click_pos = event.pos()
            map_pos = QPoint(
                click_pos.x() - (self.map_label.width() - self.map_pixmap.width()) // 2,
                click_pos.y() - (self.map_label.height() - self.map_pixmap.height()) // 2
            )

            if (0 <= map_pos.x() < self.map_pixmap.width() and
                    0 <= map_pos.y() < self.map_pixmap.height()):
                lon = float(self.high_Edit.text())
                lat = float(self.wight_Edit.text())
                scale = float(self.size_Edit.text())

                x_ratio = map_pos.x() / self.map_pixmap.width() - 0.5
                y_ratio = 0.5 - map_pos.y() / self.map_pixmap.height()

                new_lon = lon + x_ratio * scale * 2
                new_lat = lat + y_ratio * scale * 2

                self.search_by_coords(new_lon, new_lat)

    def search_by_coords(self, lon: float, lat: float):
        geocoder_request = (
            f'http://geocode-maps.yandex.ru/1.x/?'
            f'apikey={self.geocoder_api_key}&'
            f'geocode={lon},{lat}&'
            f'format=json&'
            f'kind=house&'
            f'results=5'
        )

        try:
            response = requests.get(geocoder_request)
            if response:
                json_response = response.json()
                features = json_response["response"]["GeoObjectCollection"]["featureMember"]

                self.found_addresses = []

                for feature in features:
                    toponym = feature["GeoObject"]
                    address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                    postal_code = toponym["metaDataProperty"]["GeocoderMetaData"].get("Address", {}).get("postal_code",
                                                                                                         "")
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
                    self.wight_Edit.setText(self.found_addresses[0]['lat'])
                    self.high_Edit.setText(self.found_addresses[0]['lon'])
                    self.getImage()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось выполнить запрос к геокодеру")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при поиске по координатам: {str(e)}")

    def search_address(self):  # Переименовано из shere в search_address
        """Поиск по адресу"""
        address = self.search_Edit.text()
        if not address:
            QMessageBox.warning(self, "Ошибка", "Введите адрес для поиска")
            return

        try:
            geocoder_request = (
                f'http://geocode-maps.yandex.ru/1.x/?'
                f'apikey={self.geocoder_api_key}&'
                f'geocode={address}&'
                f'format=json&'
                f'results=5'
            )

            response = requests.get(geocoder_request)
            if response:
                json_response = response.json()
                features = json_response["response"]["GeoObjectCollection"]["featureMember"]

                self.found_addresses = []

                for feature in features:
                    toponym = feature["GeoObject"]
                    address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                    postal_code = toponym["metaDataProperty"]["GeocoderMetaData"].get("Address", {}).get("postal_code",
                                                                                                         "")
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
                    self.wight_Edit.setText(self.found_addresses[0]['lat'])
                    self.high_Edit.setText(self.found_addresses[0]['lon'])
                    self.getImage()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось найти адрес")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при поиске адреса: {str(e)}")

    def update_address_display(self):
        if self.current_address_index >= 0 and self.found_addresses:
            address_info = self.found_addresses[self.current_address_index]
            if self.show_postal_code and address_info['postal_code']:
                self.address_label.setText(
                    f"{address_info['address']} (Почтовый индекс: {address_info['postal_code']})")
            else:
                self.address_label.setText(address_info['address'])

    def toggle_postal_code(self, state):
        self.show_postal_code = state == Qt.CheckState.Checked.value
        self.update_address_display()

    def show_prev_address(self):
        if len(self.found_addresses) > 1:
            self.current_address_index = (self.current_address_index - 1) % len(self.found_addresses)
            self.update_address_display()
            self.wight_Edit.setText(self.found_addresses[self.current_address_index]['lat'])
            self.high_Edit.setText(self.found_addresses[self.current_address_index]['lon'])
            self.getImage()

    def show_next_address(self):
        if len(self.found_addresses) > 1:
            self.current_address_index = (self.current_address_index + 1) % len(self.found_addresses)
            self.update_address_display()
            self.wight_Edit.setText(self.found_addresses[self.current_address_index]['lat'])
            self.high_Edit.setText(self.found_addresses[self.current_address_index]['lon'])
            self.getImage()

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
        self.map_pixmap = self.pixmap
        self.map_label.setPixmap(self.pixmap)

        self.found_addresses = []
        self.current_address_index = -1
        self.address_label.setText("")

    def getImage(self):
        self.a = self.wight_Edit.text()
        self.b = self.high_Edit.text()
        self.c = self.size_Edit.text()
        self.metka = f'pt={self.b},{self.a}'

        self.ll_spn = f'll={self.b},{self.a}&spn={self.c},{self.c}'
        map_request = f"{self.server_address}{self.ll_spn}&{self.metka}&apikey={self.api_key}"

        try:
            response = requests.get(map_request)
            if response:
                self.map_file = "map.png"
                with open(self.map_file, "wb") as file:
                    file.write(response.content)

                self.pixmap = QPixmap(self.map_file)
                self.map_pixmap = self.pixmap
                self.map_label.setPixmap(self.pixmap)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить карту")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке карты: {str(e)}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.a = float(self.wight_Edit.text())
            self.a += 0.01 * float(self.size_Edit.text()) * 50
            self.wight_Edit.setText(str(self.a))
            self.high_Edit.setText(self.high_Edit.text())
            self.getImage()
        elif event.key() == Qt.Key.Key_Down:
            self.a = float(self.wight_Edit.text())
            self.a -= 0.01 * float(self.size_Edit.text()) * 50
            self.wight_Edit.setText(str(self.a))
            self.high_Edit.setText(self.high_Edit.text())
            self.getImage()
        elif event.key() == Qt.Key.Key_Left:
            self.b = float(self.high_Edit.text())
            self.b -= 0.01 * float(self.size_Edit.text()) * 50
            self.high_Edit.setText(str(self.b))
            self.wight_Edit.setText(self.wight_Edit.text())
            self.getImage()
        elif event.key() == Qt.Key.Key_Right:
            self.b = float(self.high_Edit.text())
            self.b += 0.01 * float(self.size_Edit.text()) * 50
            self.high_Edit.setText(str(self.b))
            self.wight_Edit.setText(self.wight_Edit.text())
            self.getImage()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.exit(app.exec())