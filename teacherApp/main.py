import GlobalShared
from server import client_teacher

from kivymd.app import MDApp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog

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
            # textIp.text =""
        else:
            print("teacherId text empty")
            
    def setClassId(self,app,textIp):
        if textIp != "":
            app.classId = textIp.text.upper()
            GlobalShared.classId = app.classId
            textIp.text = GlobalShared.classId
            print(GlobalShared.classId)
            # textIp.text =""
        else:
            print("classId text empty")

    def setSubjectCode(self):
        try:
            self.field_subject = GlobalShared.subjectname
            # if len(GlobalShared.subjectname)>20:
            #     self.field_subject = GlobalShared.subjectname[:20]+"..."
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
    stdTid.field_class = 'Example: PUL075BCTCD'
    stdTid.field_subject = 'Not Connected'

    
    # def connect_callback(self,app,teacherId,classId):
    #     self.stdTid.setTeacherId(app,teacherId)
    #     self.getSubjectListAndClassList()
    #     self.stdTid.setClassId(app,classId)
    #     self.stdTid.setSubjectCode()
        

    def getSubjectListAndClassList(self):
        try:
            classListFromServer = client_teacher.updateClassAndSubjects(GlobalShared.teacherId)
            
            #print individual class id that teacher teaches        
            for i in classListFromServer["class"]:
                GlobalShared.classList.append(i)
            
            #print(GlobalShared.classList[1][1])
            GlobalShared.classId = classListFromServer["class"][1][0]       #first index 0 is bctAB and 1 is bctCD for now
            GlobalShared.className = classListFromServer["class"][1][1]
            print(GlobalShared.classId,GlobalShared.className)


        except:
            print("Class retrival error from server")
        
        try:
            subjectListFromServer = client_teacher.updateClassAndSubjects(GlobalShared.teacherId)
            
            #get subject list of each class teached by teacher
            for i in subjectListFromServer["subject"]:
                GlobalShared.subjectList.append(i)
            
            #print(GlobalShared.subjectList)
            
            GlobalShared.subjectId = subjectListFromServer["subject"][1][0]     
            GlobalShared.subjectname = subjectListFromServer["subject"][1][1]

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
                    self.widgetRemover()            #removes old instance of datatable,stop and present button
                    self.on_enter()                 #adds data table , stop and present button
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
        try:
            for text in GlobalShared.attendanceToBeDone:
                client_teacher.markAttendance(GlobalShared.teacherId,GlobalShared.classId,text)
        except:
            print("some error occured during manual attendance")        
        #empty selected check for presence
        while len(GlobalShared.attendanceToBeDone) > 0 : GlobalShared.attendanceToBeDone.pop()

        self.updateAttendanceSheet()
        
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
            rows_num = 48,
            check=True,
            # use_pagination=True,
            column_data=[
                ("Roll Number", dp(40)),
                ("Student", dp(30)),
                ("Presence", dp(30)), ],
            row_data=[
                (AttendListMini[i*3], AttendListMini[(i*3)+1], AttendListMini[(i*3)+2])
                for i in range(int(len(AttendListMini)/3))
                # (f"{i + 1}", "2.23", "3.65")
                # for i in range(50)
                ], 
                )
        
        self.data_tables.bind(on_check_press=self.check_press) 
        
        self.stop_btn = MDRaisedButton(
            text="Stop",
            pos_hint = {'center_y': 0.1, 'center_x': 0.6}
        )
        self.stop_btn.bind(on_press = self.finalAttendanceSheet)
        
        self.present_btn = MDRaisedButton(
            text="Mark Present",
            pos_hint = {'center_y': 0.1, 'center_x': 0.3}
        )
        self.present_btn.bind(on_press = self.manualPresent)

        self.add_widget(self.data_tables)
        self.add_widget(self.stop_btn)
        self.add_widget(self.present_btn)
        return layout

    def check_press(self,instance_table,current_row):
        print(current_row)
        GlobalShared.attendanceToBeDone.append(current_row[0])

    def on_enter(self):
        self.load_table()

    def widgetRemover(self):
        self.remove_widget(self.data_tables)
        self.remove_widget(self.stop_btn)
        self.remove_widget(self.present_btn)

################################### Kivy app builder ###################################
sm = ScreenManager()
sm.add_widget(LoginWindow(name='login_control'))
sm.add_widget(AttendanceWindow(name ='attendance_control'))

class MainApp(MDApp):
    def __init__(self, **kwargs):
        self.title = "Smart Attendance"
        super().__init__(**kwargs)

    def build(self):
        screen = Builder.load_file("ui.kv")
        self.messageDialog = MDDialog(text="Dialog",size_hint=(0.8, 0.2),radius=[20, 7, 20, 7])
        return screen


if __name__ == "__main__":
    MainApp().run()