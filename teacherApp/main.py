import GlobalShared
from server import client_teacher

from kivymd.app import MDApp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.datatables import MDDataTable

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget

############################# classes for various data to and fro from kv and python side ###############################
#teacher id input class
class TeacherInput(Widget):
    field_id = StringProperty(None)
    field_class = StringProperty(None)
    field_subject = StringProperty(None)

    def setTeacherId(self, app, textIp):
        if textIp != "":
            app.teacherId = textIp.text
            GlobalShared.teacherId = app.teacherId
            print(GlobalShared.teacherId)
        else:
            print("text empty")
            
    def setClassId(self):
        try:
            self.field_class = GlobalShared.classId
        except:
            print("error setting ClassCode")
    
    def setSubjectCode(self):
        try:
            self.field_subject = GlobalShared.subjectname
            # if len(GlobalShared.subjectname)>20:
            #     self.field_subject = GlobalShared.subjectname[:18]+"..."
            print(self.field_subject)
        except:
            print("error setting scode")
    
#attendance code class
class AttendanceDetail(Widget):
    field_AttendanceId = StringProperty(None)

    def setAttendanceId(self):
        try:
            self.field_AttendanceId = "Attendance code: " + str(GlobalShared.attendanceId)
            print(self.field_AttendanceId)
        except:
            print("error attendance code update")
    pass

    def clearAttendanceCode(self):
        GlobalShared.attendanceId = ""
        self.field_AttendanceId = "No attendance code"

########################################## kivy window classes #################################
class LoginWindow(Screen):
    stdTid = TeacherInput()
    stdTid.field_id = 'Example : 011'
    stdTid.field_class = 'Example : PUL075BCTCD'
    stdTid.field_subject = 'Example : Database Management System'

    def getSubjectListAndClassList(self):
        try:
            classListFromServer = client_teacher.updateClassAndSubjects(GlobalShared.teacherId)
            GlobalShared.classId = classListFromServer["class"][0][0]
            GlobalShared.className = classListFromServer["class"][0][1]
            print(GlobalShared.classId, GlobalShared.className)
        except:
            print("Class retrival error")
        
        try:
            subjectListFromServer = client_teacher.updateClassAndSubjects(GlobalShared.teacherId)
            GlobalShared.subjectId = subjectListFromServer["subject"][0][0]
            GlobalShared.subjectname = subjectListFromServer["subject"][0][1]
            print(GlobalShared.subjectId, GlobalShared.subjectname)
        except:
            print("Subject retrival error")


    def startAttendanceSheet(self):
        try:
            AttendanceListFromServer = client_teacher.startAttendance(GlobalShared.teacherId, GlobalShared.classId, GlobalShared.subjectId)
            if "error" in AttendanceListFromServer:
                print(AttendanceListFromServer["error"])
            else:
                #save attendance code
                GlobalShared.attendanceId = AttendanceListFromServer["acode"]
                for list in AttendanceListFromServer["student_list"]:
                    #print(list[0], list[1])
                    presence ="Absent"
                    presenceList = [list[1],presence]
                    GlobalShared.attendanceList[list[0]] = presenceList
                print(AttendanceListFromServer["timeout"])

        except Exception as e:
            print("error :", e)
        

class AttendanceWindow(Screen):
    attendanceInstance = AttendanceDetail()        
    attendanceInstance.field_AttendanceId = 'No attendance code'

    def updateAttendanceSheet(self):
        try:
            AttendanceListFromServer = client_teacher.getAttendance(GlobalShared.teacherId,GlobalShared.classId)
            if "error" in AttendanceListFromServer:
                print(AttendanceListFromServer["error"])
            else:
                #update presence in list
                keys = AttendanceListFromServer["student_list"]
                for key in keys:
                    GlobalShared.attendanceList[key][1] = "Present"
                    self.on_enter()
                #display attendance list
                # self.addPresentList()
        except Exception as e:
            print(e)

    def finalAttendanceSheet(self,*args):
        try:
            AttendanceListFromServer = client_teacher.stopAttendance(GlobalShared.teacherId,GlobalShared.classId)
            if "error" in AttendanceListFromServer:
                print(AttendanceListFromServer["error"])
            else:
                print(AttendanceListFromServer["success"])
        except Exception as e:
            print(e)

    def manualPresent(self,*args):
        #print("Before",GlobalShared.attendanceToBeDone)
        try:
            for text in GlobalShared.attendanceToBeDone:
                client_teacher.markAttendance(GlobalShared.teacherId,GlobalShared.classId,text)
        except:
            print("some error occured during manual attendance")        

        while len(GlobalShared.attendanceToBeDone) > 0 : GlobalShared.attendanceToBeDone.pop()
        #print("After",GlobalShared.attendanceToBeDone)

    def load_table(self):
        #list to make attendance list a list for initial insert in data table
        AttendListMini = [] 
        for key in GlobalShared.attendanceList:
            AttendListMini.append(key)
            AttendListMini.append(GlobalShared.attendanceList[key][0])
            AttendListMini.append(GlobalShared.attendanceList[key][1])

        layout = MDBoxLayout()

        self.data_tables = MDDataTable(
            pos_hint={'center_y': 0.5, 'center_x': 0.5},
            size_hint=(0.7, 0.6),
            rows_num = 48 ,
            check=True,
            column_data=[
                ("Roll Number", dp(40)),
                ("Student", dp(30)),
                ("Presence", dp(30)), ],
            row_data=[(AttendListMini[i*3], AttendListMini[(i*3)+1], AttendListMini[(i*3)+2])
                for i in range(int(len(AttendListMini)/3))], 
                )
        
        self.data_tables.bind(on_check_press=self.check_press) 

        self.stop_btn = MDRaisedButton(
            text="Stop",
            pos_hint = {'center_y': 0.1, 'center_x': 0.6}
        )
        self.stop_btn.bind(on_press = self.finalAttendanceSheet)
        
        self.present_btn = MDRaisedButton(
            text="Present",
            pos_hint = {'center_y': 0.1, 'center_x': 0.3}
        )
        self.present_btn.bind(on_press = self.manualPresent)

        self.add_widget(self.data_tables)
        self.add_widget(self.stop_btn)
        self.add_widget(self.present_btn)
        return layout


############### ERROR , multiple calls for a single click after 3 clicks apparent

    def check_press(self,instance_table,current_row):
        print(current_row[0])
        GlobalShared.attendanceToBeDone.append(current_row[0])

    def on_enter(self):
        self.load_table()

################################### Kivy app builder ###################################
sm = ScreenManager()
sm.add_widget(LoginWindow())
sm.add_widget(AttendanceWindow(name ='attendance_control'))

class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.title = "Smart Attendance"
        super().__init__(**kwargs)

    def build(self):
        screen = Builder.load_file("ui.kv")
        return screen

if __name__ == "__main__":
    MainApp().run()