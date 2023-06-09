# Form implementation generated from reading ui file 'record_window.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.
import requests
import numpy as np
from PyQt6 import QtCore, QtGui, QtWidgets
import cv2
from PyQt6.QtGui import QImage, QPixmap
import face_recognition
import requests
# from .get_user_data import get_users
import numpy as np
import base64


def get_users():
    url = "http://127.0.0.1:8000/users/users/"
    response = requests.get(url)
    if response.status_code == 200:
        datas = response.json()
        for data in datas:
            if data['is_staff'] == True:
                continue
            bin_data = base64.b64decode(data['profile']['face_encodings'])
            data['profile']['face_encodings'] = np.frombuffer(bin_data)
            # print(type(data['profile']['face_encodings']))
        return datas


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        self.users = get_users()
        self.known_face_encodings = []
        for user in self.users:
            if user["is_staff"]:
                continue
            face_encoding = np.frombuffer(user["profile"]["face_encodings"])
            # face_encoding.reshape(2, 171)
            self.known_face_encodings.append(face_encoding)
        # print(known_face_encodings)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(974, 786)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.video_frame = QtWidgets.QLabel(parent=self.centralwidget)
        self.video_frame.setGeometry(QtCore.QRect(10, 40, 640, 640))
        self.video_frame.setFrameShape(QtWidgets.QLabel.Shape.StyledPanel)
        self.video_frame.setFrameShadow(QtWidgets.QLabel.Shadow.Raised)
        self.video_frame.setObjectName("video_frame")

        self.record_button = QtWidgets.QPushButton(parent=self.centralwidget)
        self.record_button.setGeometry(QtCore.QRect(750, 60, 101, 34))
        self.record_button.setObjectName("record_button")
        self.record_button.clicked.connect(self.record_button_clicked)
        self.is_recording = False

        self.name_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.name_label.setGeometry(QtCore.QRect(710, 330, 58, 18))
        self.name_label.setObjectName("name_label")

        self.resident_name = QtWidgets.QLabel(parent=self.centralwidget)
        self.resident_name.setGeometry(QtCore.QRect(770, 330, 221, 18))
        self.resident_name.setObjectName("resident_name")

        self.block_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.block_label.setGeometry(QtCore.QRect(710, 360, 58, 18))
        self.block_label.setObjectName("block_label")

        self.resident_block = QtWidgets.QLabel(parent=self.centralwidget)
        self.resident_block.setGeometry(QtCore.QRect(770, 360, 221, 18))
        self.resident_block.setObjectName("resident_block")

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.record_button.setText(_translate("MainWindow", "Start Recording"))
        self.name_label.setText(_translate("MainWindow", "Name:"))
        self.resident_name.setText(_translate("MainWindow", "Searching"))
        self.block_label.setText(_translate("MainWindow", "Block"))
        self.resident_block.setText(_translate("MainWindow", "Searching"))

    def record_button_clicked(self):
        if not self.is_recording:
            # create a timer to update the video stream
            self.record_button.setText("Stop Recording")
            self.is_recording = True
            self.capture = cv2.VideoCapture(0)
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
        else:
            self.record_button.setText("Start Recording")
            self.is_recording = False
            self.timer.stop()
            self.capture.release()

    def update_frame(self):
        # read a frame from the webcam
        if not self.capture.isOpened():
            print("Could not open webcam.")
            return

        ret, frame = self.capture.read()
        # frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        # self.capture.set(cv2.CAP_PROP_FPS, 15)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 140)
        rgb_frame = frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(
            frame, face_locations)
        # print(self.known_face_encodings[0].shape)
        # print(face_encodings)
        if ret:

            # convert the frame to RGB image
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding)
                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.users[first_match_index+1]["username"]
                    cv2.putText(frame, name, (left + 6, bottom - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 1)
                    self.resident_name.setText(name)
                    self.resident_block.setText(
                        str(self.users[first_match_index+1]["profile"]["block_number"]))
                    self.record_button.setText("Start Recording")
                    self.is_recording = False
                    self.timer.stop()
                    self.capture.release()

                cv2.rectangle(frame, (left, top),
                              (right, bottom), (0, 0, 255), 2)
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # create a QImage from the RGB image
            qimage = QImage(
                rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QImage.Format.Format_RGB888)

            # create a QPixmap from the QImage
            pixmap = QPixmap.fromImage(qimage)

            # set the QPixmap to the QLabel
            self.video_frame.setPixmap(pixmap)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
