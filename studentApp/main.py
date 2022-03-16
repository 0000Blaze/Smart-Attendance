import server.client_student

import cv2
import face_recognition
import os


from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.uix.textinput import TextInput

Window.size = (540, 960)
filePresent = True
pictureRemoved = False
try:
    fileP = open("./userData.txt", "r")
except:
    filePresent = False
    pass


class StudentApp(MDApp):
    rollNoSaved = ""

    def build(self):
        # app LOGO
        self.imageObj = Image(source="./assets/logo.png")
        # layout for image of logo
        self.imageLayout = BoxLayout(size_hint=(0.5, 0.5),
                                     pos_hint={'x': 0.25, 'y': 0.2})
        self.imageLayout.add_widget(self.imageObj)
        # widgets for input
        self.rollNoL = MDLabel(text="Roll No:")
        self.AttendanceCodeL = MDLabel(text="Attendance Code: ")

        self.rollNoT = TextInput(hint_text="Enter Roll no :")
        self.AttendanceCodeT = TextInput(hint_text="Enter Attendance Code : ")

        self.inputLayout = BoxLayout(orientation="vertical",
                                     size_hint=(0.8, 0.25),
                                     pos_hint={'x': 0.1, 'y': 0.1}
                                     )

        # setting text of roll no from saved file
        if filePresent:
            self.rollNoT.text = fileP.readline()

        # Adding widgets for input to input layout
        self.inputLayout.add_widget(self.rollNoL)
        self.inputLayout.add_widget(self.rollNoT)
        self.inputLayout.add_widget(self.AttendanceCodeL)
        self.inputLayout.add_widget(self.AttendanceCodeT)

        # Message label
        self.messageL = MDLabel(text="Authenticate your face:")
        # Layout for Message
        self.messageLayout = BoxLayout(orientation="vertical",
                                       size_hint=(0.8, 0.2),
                                       pos_hint={'x': 0.1, 'y': 0.1}
                                       )

        self.messageLayout.add_widget(self.messageL)

        # Camera object
        self.cameraObj = Camera()
        self.cameraObj.resolution = (640, 480)

        # Capture Button
        self.buttonObj = MDRaisedButton(text="Capture")
        self.buttonObj.size_hint = (.2, .15)
        self.buttonObj.pos_hint = {'x': .45, 'y': .2}
        self.buttonObj.bind(on_press=self.takeImage)
        # layout for camera and capture button
        myBoxLayout = BoxLayout(orientation="vertical")
        myBoxLayout.add_widget(self.imageLayout)
        myBoxLayout.add_widget(self.inputLayout)
        myBoxLayout.add_widget(self.messageLayout)
        myBoxLayout.add_widget(self.cameraObj)
        myBoxLayout.add_widget(self.buttonObj)

        return myBoxLayout

    def takeImage(self, *args):
        self.filename = str(self.rollNoT.text + "+" +
                            self.AttendanceCodeT.text+".png")
        self.rollNo = str(self.rollNoT.text)
        self.acode = self.AttendanceCodeT.text
        print(self.filename)

        try:
            self.cameraObj.export_to_png(self.filename)
            imag = face_recognition.load_image_file(self.filename)
            imag = cv2.cvtColor(imag, cv2.COLOR_BGR2RGB)
            self.encodingsData = face_recognition.face_encodings(imag)[0]
            self.encodingsData = self.encodingsData.tolist()
            self.encodingsSuccess = True
            # print(self.encodingsData)
            #  Send embeddings to server
            print(self.rollNo)
            dataFromServer = server.client_student.markAttendance(
                self.rollNo, int(self.acode), self.encodingsData)
            print(dataFromServer)
            if "error" in dataFromServer:
                print(dataFromServer["error"])
                self.messageL.text = str(dataFromServer["error"])
            else:
                print(dataFromServer["success"])
                self.messageL.text = str(dataFromServer["success"])
            os.remove(self.filename)
            pictureRemoved = True
            if filePresent:
                os.remove("./userData.txt")

            fileP = open("./userData.txt", "w")
            fileP.write(self.rollNo)
        except Exception as e:
            print("No face detected.")
            print("error :", e)
            if not pictureRemoved:
                os.remove(self.filename)
            self.encodingsSuccess = False
            self.encodingsData = None


if __name__ == "__main__":
    StudentApp().run()
