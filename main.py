import io
import os
import sys
import requests

from PyQt6 import uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt

template = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>729</width>
    <height>460</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <widget class="QLineEdit" name="wight_Edit">
   <property name="geometry">
    <rect>
     <x>120</x>
     <y>10</y>
     <width>113</width>
     <height>20</height>
    </rect>
   </property>
  </widget>
  <widget class="QLineEdit" name="high_Edit">
   <property name="geometry">
    <rect>
     <x>120</x>
     <y>40</y>
     <width>113</width>
     <height>20</height>
    </rect>
   </property>
  </widget>
  <widget class="QLineEdit" name="size_Edit">
   <property name="geometry">
    <rect>
     <x>120</x>
     <y>70</y>
     <width>113</width>
     <height>20</height>
    </rect>
   </property>
  </widget>
  <widget class="QLabel" name="label">
   <property name="geometry">
    <rect>
     <x>20</x>
     <y>10</y>
     <width>91</width>
     <height>16</height>
    </rect>
   </property>
   <property name="text">
    <string>Введите широту:</string>
   </property>
  </widget>
  <widget class="QLabel" name="label_2">
   <property name="geometry">
    <rect>
     <x>20</x>
     <y>40</y>
     <width>101</width>
     <height>16</height>
    </rect>
   </property>
   <property name="text">
    <string>Введите долготу:</string>
   </property>
  </widget>
  <widget class="QLabel" name="label_3">
   <property name="geometry">
    <rect>
     <x>20</x>
     <y>70</y>
     <width>101</width>
     <height>16</height>
    </rect>
   </property>
   <property name="text">
    <string>Введите масштаб:</string>
   </property>
  </widget>
  <widget class="QPushButton" name="ok_button">
   <property name="geometry">
    <rect>
     <x>280</x>
     <y>40</y>
     <width>75</width>
     <height>23</height>
    </rect>
   </property>
   <property name="text">
    <string>Нарисовать</string>
   </property>
  </widget>
  <widget class="QLabel" name="map_label">
   <property name="geometry">
    <rect>
     <x>30</x>
     <y>140</y>
     <width>47</width>
     <height>13</height>
    </rect>
   </property>
   <property name="text">
    <string/>
   </property>
  </widget>
 </widget>
 <resources/>
 <connections/>
</ui>
"""


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_address = 'https://static-maps.yandex.ru/v1?'
        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.initUI()

    def initUI(self):
        f = io.StringIO(template)
        uic.loadUi(f, self)
        self.ok_button.clicked.connect(self.getImage)

    def getImage(self):
        self.a = self.wight_Edit.text()
        self.b = self.high_Edit.text()
        self.c = self.size_Edit.text()
        self.imagee()

    def imagee(self):
        print(self.c)
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.c = float(self.c)
            self.c += 0.001
        if event.key() == Qt.Key.Key_Down:
            self.c = float(self.c)
            self.c -= 0.001
            try:
                self.c = str(self.c)
                self.size_Edit.setText(self.c)
                self.imagee()
            except:
                pass


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MyWidget()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
