# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Tello_Gui_E_ver.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import tello
import cv2
import traceback
import datetime
import os

class Ui_Dialog(object):
    def __init__(self, Dialog, device, bObjectDetection):
        super().__init__()
        self.setupUi(Dialog)
        self.bindFuncs()

        self.logBuffer = []
        self.QtUpdateTimer = QtCore.QTimer()
        self.QtUpdateTimer.timeout.connect(self.QtUpdate)
        self.QtUpdateTimer.start(10)

        self.delta_height=20
        self.delta_rotate=45
        self.delta_LR=20
        self.delta_FB=20
        self.delta_LD=20
        self.delta_RD=20
        self.stateDict = {
            "pitch": "0",
            "roll": "0",
            "yaw": "0",
            "vgx": "0",
            "vgy": "0",
            "vgz": "0",
            "templ": "0",
            "temph": "0",
            "tof": "0",
            "h": "0",
            "bat": "0",
            "baro": "0.0",
            "time": "0",
            "agx": '0.0',
            "agy": '0.0',
            "agz": '0.0',
            "wifi": '99'
        }

        ######
        self.picRenderW = 100
        self.picRenderH = 100
        self.Qt_pics = []
        self.Qt_picTimes = []
        self.picDateTime = [None]*6
        self.timerStartTime = None
        self.latestDetectedLabel = ''

        self.Qt_pics.append(self.P1)
        self.Qt_pics.append(self.P2)
        self.Qt_pics.append(self.P3)
        self.Qt_pics.append(self.P4)
        self.Qt_pics.append(self.P5)
        self.Qt_pics.append(self.P6)
        self.Qt_picTimes.append([self.P1_1,self.P1_2,self.P1_3])
        self.Qt_picTimes.append([self.P2_1,self.P2_2,self.P2_3])
        self.Qt_picTimes.append([self.P3_1,self.P3_2,self.P3_3])
        self.Qt_picTimes.append([self.P4_1,self.P4_2,self.P4_3])
        self.Qt_picTimes.append([self.P5_1,self.P5_2,self.P5_3])
        self.Qt_picTimes.append([self.P6_1,self.P6_2,self.P6_3])
        self.picLabels = ['dog','plane','car','boat','bird','horse']
        self.labelDetectCounts = [0,0,0,0,0,0]
        self.labelbDetect = [False,False,False,False,False,False]
        self.labelDetectInfo = [None]*6
        self.DETECTION_FRAME_COUNT = 10
        ######

        self.tello = tello.Tello(self.log, self.stateReceive)
        self.updateIP()


        self.originFrame = None

        self.bObjectDetection = bObjectDetection
        if self.bObjectDetection:
            print('Object Detector initialize...')
            from ObjectDetector_Mobilenet_SSD import ObjectDetector_Mobilenet_SSD
            self.objDetector = ObjectDetector_Mobilenet_SSD(device, self.getOriginFrame)
        self.requestSNR = False

        self.button_on_off(False)
        self.resetDetectionInfo()

    def QtUpdate(self):
        self.updateImage()
        for logStr in self.logBuffer:
            self.loglist.append(logStr)
        if len(self.logBuffer) > 0:
            self.loglist.verticalScrollBar().setValue(self.loglist.verticalScrollBar().maximum())
            self.logBuffer.clear()
        self.updateState()
    def log(self, logStr):
        logStr = logStr.strip()
        self.logBuffer.append(logStr)
    def stateReceive(self, stateData):
        stateData = stateData.decode('utf-8')
        states = stateData.split(';')[:-1]
        for state in states:
            keyValue = state.split(':')
            key = keyValue[0]
            value = keyValue[1]
            self.stateDict[key] = value
        return self.stateDict
    def updateState(self):
        self.TOF.setText(self.TOF_TextFormat % int(self.stateDict['tof']))
        self.Height.setText(self.HeightTextFormat % int(self.stateDict['h']))
        sec = int(self.stateDict['time'])
        hour = int(sec / 3600)
        sec = sec - hour * 3600
        minute = int(sec / 60)
        sec = sec - minute * 60
        self.F_Time.setText(self.F_TimeTextFormat % (hour, minute, sec))
        self.temp.setText(self.tempTextFormat % (int(self.stateDict['templ']), int(self.stateDict['temph'])))
        self.Battery.setProperty("value", int(self.stateDict['bat']))
        if self.requestSNR:
            try:
                wifi_SNR = int(self.tello.response)
                self.wifi_snr.setProperty('value', wifi_SNR)
                self.requestSNR = False
            except:
                pass
    def updateImage(self):
        try:
            if self.tello.cap is not None:
                self.originFrame = self.tello.readFrame()
                if self.originFrame is not None:
                    renderImg = cv2.cvtColor(self.originFrame, cv2.COLOR_BGR2RGB)
                    originW = self.getCapW()
                    originH = self.getCapH()
                    renderingW = 700
                    renderingH = 525

                    # 모두 인식하면 최종 걸린시간 계산
                    bFishedAllObjDetection = True
                    for i in range(6):
                        if self.picDateTime[i] is None:
                            bFishedAllObjDetection = False
                            break
                    if bFishedAllObjDetection:
                        timerDateTime = self.picDateTime[5] - self.timerStartTime
                        allSec = timerDateTime.seconds
                        minute = int(allSec/60)
                        sec = allSec - minute*60
                        self.T1.display(minute)
                        self.T2.display(sec)
                        self.T3.display(int(timerDateTime.microseconds/10000))
                    elif self.picDateTime[0] is not None:
                        if self.timerStartTime is None:
                            self.timerStartTime = self.picDateTime[0]
                        timerDateTime = datetime.datetime.now() - self.timerStartTime
                        allSec = timerDateTime.seconds
                        minute = int(allSec/60)
                        sec = allSec - minute*60
                        self.T1.display(minute)
                        self.T2.display(sec)
                        self.T3.display(int(timerDateTime.microseconds/10000))

                    if self.bObjectDetection:
                        for i in range(6):
                            self.labelbDetect[i] = False
                        # 추론결과물 받기
                        infer_time, detectedObjects = self.objDetector.getProcessedData()
                        if detectedObjects is not None:
                            for object in detectedObjects:
                                obj3, obj4, obj5, obj6, class_id, percent = object
                                xmin = int(obj3 * originW)
                                ymin = int(obj4 * originH)
                                xmax = int(obj5 * originW)
                                ymax = int(obj6 * originH)

                                for i in range(6):
                                    if self.latestDetectedLabel != self.picLabels[i] and self.objDetector.labels[class_id] == self.picLabels[i]:
                                        self.labelbDetect[i] = True
                                        self.labelDetectInfo[i] = (xmin,ymin,xmax,ymax)


                                # object 표시
                                cv2.rectangle(renderImg, (xmin,ymin),
                                              (xmax, ymax), (0,0,0), 2)
                                cv2.putText(renderImg, self.objDetector.labels[class_id], (xmin, ymin), cv2.FONT_HERSHEY_COMPLEX, 1.5,
                                            (200, 10, 10), 1)

                        for i in range(6):
                            if self.labelbDetect[i]:
                                self.labelDetectCounts[i] += 1
                            else:
                                self.labelDetectCounts[i] = 0

                        for i in range(6):
                            if self.labelDetectCounts[i] > self.DETECTION_FRAME_COUNT:
                                # 현재시간
                                curTime = datetime.datetime.now()
                                millisecond = int(curTime.microsecond / 10000)
                                # 시간 업데이트
                                self.Qt_picTimes[i][0].display(curTime.minute)
                                self.Qt_picTimes[i][1].display(curTime.second)
                                self.Qt_picTimes[i][2].display(millisecond)
                                self.picDateTime[i] = curTime

                                # 이미지 업데이트
                                onlyObjFrameBGR = self.originFrame[self.labelDetectInfo[i][1]:self.labelDetectInfo[i][3], self.labelDetectInfo[i][0]:self.labelDetectInfo[i][2]]
                                onlyObjFrameRGB = cv2.cvtColor(onlyObjFrameBGR, cv2.COLOR_BGR2RGB)
                                objRenderImg = cv2.resize(onlyObjFrameRGB, (self.picRenderW, self.picRenderH))
                                bytesPerLine = 3 * self.picRenderW
                                qImg = QtGui.QImage(objRenderImg.data, self.picRenderW, self.picRenderH,
                                                    bytesPerLine, QtGui.QImage.Format_RGB888)
                                self.Qt_pics[i].setPixmap(QtGui.QPixmap(qImg))
                                self.latestDetectedLabel = self.picLabels[i]
                                self.log(self.latestDetectedLabel + ' captured')
                                cv2.imwrite('./captureResult/' + self.latestDetectedLabel + curTime.__str__() + '.jpg',
                                            onlyObjFrameBGR)

                    #QtLabel에 뿌리기
                    renderImg = cv2.resize(renderImg, (renderingW, renderingH))

                    if self.bObjectDetection:
                        # frame에대한 정보 그리기
                        inf_time_message = "Inference time: {:.3f} ms".format(infer_time * 1000)
                        cv2.putText(renderImg, inf_time_message, (15, 15), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                    (200, 10, 10), 1)

                    bytesPerLine = 3 * renderingW
                    qImg = QtGui.QImage(renderImg.data, renderingW, renderingH, bytesPerLine, QtGui.QImage.Format_RGB888)
                    self.videoimg.setPixmap(QtGui.QPixmap(qImg))

        except Exception as error:
                traceback.print_exc()
                print("catch error")
    def resetDetectionInfo(self):
        for i in range(6):
            self.Qt_pics[i].setPixmap(QtGui.QPixmap("./res/."+(i+1).__str__()+".jpg"))
            self.Qt_picTimes[i][0].display(0)
            self.Qt_picTimes[i][1].display(0)
            self.Qt_picTimes[i][2].display(0)
            self.latestDetectedLabel=''
            self.picDateTime[i] = None
        self.timerStartTime = None
        self.T1.display(0)
        self.T2.display(0)
        self.T3.display(0)
        os.system('rm -f ./captureResult/*.jpg')
    def getCapW(self):
        if self.tello.cap is not None:
            return self.tello.cap.get(3)
        return -1
    def getCapH(self):
        if self.tello.cap is not None:
            return self.tello.cap.get(4)
        return -1
    def getOriginFrame(self):
        return self.originFrame

    #########QT###########
    def bindFuncs(self):
        #drone control button binding
        self.Forward_M1.clicked.connect(self.moveforward)
        self.Forward_M2.clicked.connect(self.moveforward)
        self.Backward_M1.clicked.connect(self.movebackward)
        self.Backward_M2.clicked.connect(self.movebackward)
        self.Left_M1.clicked.connect(self.moveleft)
        self.Left_M2.clicked.connect(self.moveleft)
        self.Right_M1.clicked.connect(self.moveright)
        self.Right_M2.clicked.connect(self.moveright)
        self.Up_M1.clicked.connect(self.Up)
        self.Up_M2.clicked.connect(self.Up)
        self.Down_M1.clicked.connect(self.Down)
        self.Down_M2.clicked.connect(self.Down)
        self.CW_M1.clicked.connect(self.rotateCW)
        self.CW_M2.clicked.connect(self.rotateCW)
        self.CCW_M1.clicked.connect(self.rotateCCW)
        self.CCW_M2.clicked.connect(self.rotateCCW)
        self.TakeOff_M1.clicked.connect(self.takeoff)
        self.TakeOff_M2.clicked.connect(self.takeoff)
        self.Land_M1.clicked.connect(self.land)
        self.Land_M2.clicked.connect(self.land)
        # connect
        self.Connect_M1.clicked.connect(self.connect)
        self.Connect_M2.clicked.connect(self.connect)
        self.SNR_Check.clicked.connect(self.check)
        self.IPAddress.textChanged.connect(self.updateIP)
        self.TimerReset.clicked.connect(self.resetDetectionInfo)

        # Change delta values
        self.Height_Spinbox.valueChanged.connect(self.updateHeight)
        self.Rotation_Spinbox.valueChanged.connect(self.updateRotation)
        self.Master_Spinbox.valueChanged.connect(self.updateAll)
        self.L_R_Spinbox.valueChanged.connect(self.updateLR)
        self.F_B_SpinBox.valueChanged.connect(self.updateFB)
        # radio button
        self.radioButton1.clicked.connect(self.enable)
        self.radioButton3.clicked.connect(self.enable)

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1400, 900)
        Dialog.setMinimumSize(QtCore.QSize(1400, 900))
        Dialog.setMaximumSize(QtCore.QSize(1400, 960))
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.videoimg = QtWidgets.QLabel(Dialog)
        self.videoimg.setMinimumSize(QtCore.QSize(700, 525))
        self.videoimg.setMaximumSize(QtCore.QSize(700, 525))
        self.videoimg.setText("")
        self.videoimg.setPixmap(QtGui.QPixmap(":/Picture/sponsor.jpg"))
        self.videoimg.setObjectName("videoimg")
        self.verticalLayout_3.addWidget(self.videoimg)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.contorlWidget = QtWidgets.QTabWidget(Dialog)
        self.contorlWidget.setObjectName("contorlWidget")
        self.mode1 = QtWidgets.QWidget()
        self.mode1.setObjectName("mode1")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.mode1)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.Forward_M1 = QtWidgets.QPushButton(self.mode1)
        self.Forward_M1.setEnabled(False)
        self.Forward_M1.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Forward_M1.setFont(font)
        self.Forward_M1.setObjectName("Forward_M1")
        self.gridLayout_5.addWidget(self.Forward_M1, 0, 1, 1, 1)
        self.Left_M1 = QtWidgets.QPushButton(self.mode1)
        self.Left_M1.setEnabled(False)
        self.Left_M1.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Left_M1.setFont(font)
        self.Left_M1.setObjectName("Left_M1")
        self.gridLayout_5.addWidget(self.Left_M1, 1, 0, 1, 1)
        self.Right_M1 = QtWidgets.QPushButton(self.mode1)
        self.Right_M1.setEnabled(False)
        self.Right_M1.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Right_M1.setFont(font)
        self.Right_M1.setObjectName("Right_M1")
        self.gridLayout_5.addWidget(self.Right_M1, 1, 2, 1, 1)
        self.Backward_M1 = QtWidgets.QPushButton(self.mode1)
        self.Backward_M1.setEnabled(False)
        self.Backward_M1.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Backward_M1.setFont(font)
        self.Backward_M1.setObjectName("Backward_M1")
        self.gridLayout_5.addWidget(self.Backward_M1, 2, 1, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 2, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.TakeOff_M1 = QtWidgets.QPushButton(self.mode1)
        self.TakeOff_M1.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.TakeOff_M1.setFont(font)
        self.TakeOff_M1.setObjectName("TakeOff_M1")
        self.verticalLayout_2.addWidget(self.TakeOff_M1)
        self.Connect_M1 = QtWidgets.QPushButton(self.mode1)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Connect_M1.setFont(font)
        self.Connect_M1.setObjectName("Connect_M1")
        self.verticalLayout_2.addWidget(self.Connect_M1)
        self.Land_M1 = QtWidgets.QPushButton(self.mode1)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Land_M1.setFont(font)
        self.Land_M1.setObjectName("Land_M1")
        self.verticalLayout_2.addWidget(self.Land_M1)
        self.gridLayout_6.addLayout(self.verticalLayout_2, 0, 1, 1, 1)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.Up_M1 = QtWidgets.QPushButton(self.mode1)
        self.Up_M1.setEnabled(False)
        self.Up_M1.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Up_M1.setFont(font)
        self.Up_M1.setObjectName("Up_M1")
        self.gridLayout_4.addWidget(self.Up_M1, 0, 1, 1, 1)
        self.CCW_M1 = QtWidgets.QPushButton(self.mode1)
        self.CCW_M1.setEnabled(False)
        self.CCW_M1.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.CCW_M1.setFont(font)
        self.CCW_M1.setObjectName("CCW_M1")
        self.gridLayout_4.addWidget(self.CCW_M1, 1, 0, 1, 1)
        self.CW_M1 = QtWidgets.QPushButton(self.mode1)
        self.CW_M1.setEnabled(False)
        self.CW_M1.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.CW_M1.setFont(font)
        self.CW_M1.setObjectName("CW_M1")
        self.gridLayout_4.addWidget(self.CW_M1, 1, 2, 1, 1)
        self.Down_M1 = QtWidgets.QPushButton(self.mode1)
        self.Down_M1.setEnabled(False)
        self.Down_M1.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Down_M1.setFont(font)
        self.Down_M1.setObjectName("Down_M1")
        self.gridLayout_4.addWidget(self.Down_M1, 2, 1, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_4, 0, 0, 1, 1)
        self.contorlWidget.addTab(self.mode1, "")
        self.tab2 = QtWidgets.QWidget()
        self.tab2.setObjectName("tab2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.Forward_M2 = QtWidgets.QPushButton(self.tab2)
        self.Forward_M2.setEnabled(False)
        self.Forward_M2.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Forward_M2.setFont(font)
        self.Forward_M2.setObjectName("Forward_M2")
        self.gridLayout.addWidget(self.Forward_M2, 0, 1, 1, 1)
        self.CCW_M2 = QtWidgets.QPushButton(self.tab2)
        self.CCW_M2.setEnabled(False)
        self.CCW_M2.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.CCW_M2.setFont(font)
        self.CCW_M2.setObjectName("CCW_M2")
        self.gridLayout.addWidget(self.CCW_M2, 1, 0, 1, 1)
        self.CW_M2 = QtWidgets.QPushButton(self.tab2)
        self.CW_M2.setEnabled(False)
        self.CW_M2.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.CW_M2.setFont(font)
        self.CW_M2.setObjectName("CW_M2")
        self.gridLayout.addWidget(self.CW_M2, 1, 2, 1, 1)
        self.Backward_M2 = QtWidgets.QPushButton(self.tab2)
        self.Backward_M2.setEnabled(False)
        self.Backward_M2.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Backward_M2.setFont(font)
        self.Backward_M2.setObjectName("Backward_M2")
        self.gridLayout.addWidget(self.Backward_M2, 2, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.TakeOff_M2 = QtWidgets.QPushButton(self.tab2)
        self.TakeOff_M2.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.TakeOff_M2.setFont(font)
        self.TakeOff_M2.setObjectName("TakeOff_M2")
        self.verticalLayout.addWidget(self.TakeOff_M2)
        self.Connect_M2 = QtWidgets.QPushButton(self.tab2)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Connect_M2.setFont(font)
        self.Connect_M2.setObjectName("Connect_M2")
        self.verticalLayout.addWidget(self.Connect_M2)
        self.Land_M2 = QtWidgets.QPushButton(self.tab2)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Land_M2.setFont(font)
        self.Land_M2.setObjectName("Land_M2")
        self.verticalLayout.addWidget(self.Land_M2)
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.Left_M2 = QtWidgets.QPushButton(self.tab2)
        self.Left_M2.setEnabled(False)
        self.Left_M2.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Left_M2.setFont(font)
        self.Left_M2.setObjectName("Left_M2")
        self.gridLayout_2.addWidget(self.Left_M2, 1, 0, 1, 1)
        self.Right_M2 = QtWidgets.QPushButton(self.tab2)
        self.Right_M2.setEnabled(False)
        self.Right_M2.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Right_M2.setFont(font)
        self.Right_M2.setObjectName("Right_M2")
        self.gridLayout_2.addWidget(self.Right_M2, 1, 2, 1, 1)
        self.Up_M2 = QtWidgets.QPushButton(self.tab2)
        self.Up_M2.setEnabled(False)
        self.Up_M2.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Up_M2.setFont(font)
        self.Up_M2.setObjectName("Up_M2")
        self.gridLayout_2.addWidget(self.Up_M2, 0, 1, 1, 1)
        self.Down_M2 = QtWidgets.QPushButton(self.tab2)
        self.Down_M2.setEnabled(False)
        self.Down_M2.setMinimumSize(QtCore.QSize(60, 60))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.Down_M2.setFont(font)
        self.Down_M2.setObjectName("Down_M2")
        self.gridLayout_2.addWidget(self.Down_M2, 2, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 2, 1, 1)
        self.contorlWidget.addTab(self.tab2, "")
        self.verticalLayout_3.addWidget(self.contorlWidget)
        self.horizontalLayout_18.addLayout(self.verticalLayout_3)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.TimerReset = QtWidgets.QPushButton(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.TimerReset.setFont(font)
        self.TimerReset.setObjectName("TimerReset")
        self.verticalLayout_4.addWidget(self.TimerReset)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_53 = QtWidgets.QLabel(Dialog)
        self.label_53.setText("")
        self.label_53.setPixmap(QtGui.QPixmap(":/Picture/time.jpg"))
        self.label_53.setObjectName("label_53")
        self.horizontalLayout_2.addWidget(self.label_53)
        self.T1 = QtWidgets.QLCDNumber(Dialog)
        self.T1.setDigitCount(2)
        self.T1.setProperty("intValue", 99)
        self.T1.setObjectName("T1")
        self.horizontalLayout_2.addWidget(self.T1)
        self.label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.T2 = QtWidgets.QLCDNumber(Dialog)
        self.T2.setDigitCount(2)
        self.T2.setProperty("intValue", 99)
        self.T2.setObjectName("T2")
        self.horizontalLayout_2.addWidget(self.T2)
        self.label_2 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.T3 = QtWidgets.QLCDNumber(Dialog)
        self.T3.setDigitCount(2)
        self.T3.setProperty("intValue", 99)
        self.T3.setObjectName("T3")
        self.horizontalLayout_2.addWidget(self.T3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.verticalLayout_8.addLayout(self.verticalLayout_4)
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.P1 = QtWidgets.QLabel(Dialog)
        self.P1.setText("")
        self.P1.setPixmap(QtGui.QPixmap("./res/.1.jpg"))
        self.P1.setObjectName("P1")
        self.horizontalLayout_3.addWidget(self.P1)
        self.P1_1 = QtWidgets.QLCDNumber(Dialog)
        self.P1_1.setDigitCount(2)
        self.P1_1.setProperty("intValue", 99)
        self.P1_1.setObjectName("P1_1")
        self.horizontalLayout_3.addWidget(self.P1_1)
        self.label_7 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_3.addWidget(self.label_7)
        self.P1_2 = QtWidgets.QLCDNumber(Dialog)
        self.P1_2.setDigitCount(2)
        self.P1_2.setProperty("intValue", 99)
        self.P1_2.setObjectName("P_1_2")
        self.horizontalLayout_3.addWidget(self.P1_2)
        self.label_12 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_3.addWidget(self.label_12)
        self.P1_3 = QtWidgets.QLCDNumber(Dialog)
        self.P1_3.setDigitCount(2)
        self.P1_3.setProperty("intValue", 99)
        self.P1_3.setObjectName("P_1_3")
        self.horizontalLayout_3.addWidget(self.P1_3)
        self.gridLayout_7.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.P4 = QtWidgets.QLabel(Dialog)
        self.P4.setText("")
        self.P4.setPixmap(QtGui.QPixmap("./res/.4.jpg"))
        self.P4.setObjectName("P4")
        self.horizontalLayout_5.addWidget(self.P4)
        self.P4_1 = QtWidgets.QLCDNumber(Dialog)
        self.P4_1.setDigitCount(2)
        self.P4_1.setProperty("intValue", 99)
        self.P4_1.setObjectName("P4_1")
        self.horizontalLayout_5.addWidget(self.P4_1)
        self.label_8 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_5.addWidget(self.label_8)
        self.P4_2 = QtWidgets.QLCDNumber(Dialog)
        self.P4_2.setDigitCount(2)
        self.P4_2.setProperty("intValue", 99)
        self.P4_2.setObjectName("P4_2")
        self.horizontalLayout_5.addWidget(self.P4_2)
        self.label_13 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_5.addWidget(self.label_13)
        self.P4_3 = QtWidgets.QLCDNumber(Dialog)
        self.P4_3.setDigitCount(2)
        self.P4_3.setProperty("intValue", 99)
        self.P4_3.setObjectName("P4_3")
        self.horizontalLayout_5.addWidget(self.P4_3)
        self.gridLayout_7.addLayout(self.horizontalLayout_5, 0, 1, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.P2 = QtWidgets.QLabel(Dialog)
        self.P2.setText("")
        self.P2.setPixmap(QtGui.QPixmap("./res/.2.jpg"))
        self.P2.setObjectName("P2")
        self.horizontalLayout_4.addWidget(self.P2)
        self.P2_1 = QtWidgets.QLCDNumber(Dialog)
        self.P2_1.setDigitCount(2)
        self.P2_1.setProperty("intValue", 99)
        self.P2_1.setObjectName("P2_1")
        self.horizontalLayout_4.addWidget(self.P2_1)
        self.label_49 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_49.setFont(font)
        self.label_49.setObjectName("label_49")
        self.horizontalLayout_4.addWidget(self.label_49)
        self.P2_2 = QtWidgets.QLCDNumber(Dialog)
        self.P2_2.setDigitCount(2)
        self.P2_2.setProperty("intValue", 99)
        self.P2_2.setObjectName("P2_2")
        self.horizontalLayout_4.addWidget(self.P2_2)
        self.label_50 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_50.setFont(font)
        self.label_50.setObjectName("label_50")
        self.horizontalLayout_4.addWidget(self.label_50)
        self.P2_3 = QtWidgets.QLCDNumber(Dialog)
        self.P2_3.setDigitCount(2)
        self.P2_3.setProperty("intValue", 99)
        self.P2_3.setObjectName("P2_3")
        self.horizontalLayout_4.addWidget(self.P2_3)
        self.gridLayout_7.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.P5 = QtWidgets.QLabel(Dialog)
        self.P5.setText("")
        self.P5.setPixmap(QtGui.QPixmap("./res/.5.jpg"))
        self.P5.setObjectName("P5")
        self.horizontalLayout_6.addWidget(self.P5)
        self.P5_1 = QtWidgets.QLCDNumber(Dialog)
        self.P5_1.setDigitCount(2)
        self.P5_1.setProperty("intValue", 99)
        self.P5_1.setObjectName("P5_1")
        self.horizontalLayout_6.addWidget(self.P5_1)
        self.label_51 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_51.setFont(font)
        self.label_51.setObjectName("label_51")
        self.horizontalLayout_6.addWidget(self.label_51)
        self.P5_2 = QtWidgets.QLCDNumber(Dialog)
        self.P5_2.setDigitCount(2)
        self.P5_2.setProperty("intValue", 99)
        self.P5_2.setObjectName("P5_2")
        self.horizontalLayout_6.addWidget(self.P5_2)
        self.label_52 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_52.setFont(font)
        self.label_52.setObjectName("label_52")
        self.horizontalLayout_6.addWidget(self.label_52)
        self.P5_3 = QtWidgets.QLCDNumber(Dialog)
        self.P5_3.setDigitCount(2)
        self.P5_3.setProperty("intValue", 99)
        self.P5_3.setObjectName("P5_3")
        self.horizontalLayout_6.addWidget(self.P5_3)
        self.gridLayout_7.addLayout(self.horizontalLayout_6, 1, 1, 1, 1)
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.P3 = QtWidgets.QLabel(Dialog)
        self.P3.setText("")
        self.P3.setPixmap(QtGui.QPixmap("./res/.3.jpg"))
        self.P3.setObjectName("P3")
        self.horizontalLayout_17.addWidget(self.P3)
        self.P3_1 = QtWidgets.QLCDNumber(Dialog)
        self.P3_1.setDigitCount(2)
        self.P3_1.setProperty("intValue", 99)
        self.P3_1.setObjectName("P3_1")
        self.horizontalLayout_17.addWidget(self.P3_1)
        self.label_56 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_56.setFont(font)
        self.label_56.setObjectName("label_56")
        self.horizontalLayout_17.addWidget(self.label_56)
        self.P3_2 = QtWidgets.QLCDNumber(Dialog)
        self.P3_2.setDigitCount(2)
        self.P3_2.setProperty("intValue", 99)
        self.P3_2.setObjectName("P3_2")
        self.horizontalLayout_17.addWidget(self.P3_2)
        self.label_57 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_57.setFont(font)
        self.label_57.setObjectName("label_57")
        self.horizontalLayout_17.addWidget(self.label_57)
        self.P3_3 = QtWidgets.QLCDNumber(Dialog)
        self.P3_3.setDigitCount(2)
        self.P3_3.setProperty("intValue", 99)
        self.P3_3.setObjectName("P3_3")
        self.horizontalLayout_17.addWidget(self.P3_3)
        self.gridLayout_7.addLayout(self.horizontalLayout_17, 2, 0, 1, 1)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.P6 = QtWidgets.QLabel(Dialog)
        self.P6.setText("")
        self.P6.setPixmap(QtGui.QPixmap("./res/.6.jpg"))
        self.P6.setObjectName("P6")
        self.horizontalLayout_7.addWidget(self.P6)
        self.P6_1 = QtWidgets.QLCDNumber(Dialog)
        self.P6_1.setDigitCount(2)
        self.P6_1.setProperty("intValue", 99)
        self.P6_1.setObjectName("P6_1")
        self.horizontalLayout_7.addWidget(self.P6_1)
        self.label_54 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_54.setFont(font)
        self.label_54.setObjectName("label_54")
        self.horizontalLayout_7.addWidget(self.label_54)
        self.P6_2 = QtWidgets.QLCDNumber(Dialog)
        self.P6_2.setDigitCount(2)
        self.P6_2.setProperty("intValue", 99)
        self.P6_2.setObjectName("P6_2")
        self.horizontalLayout_7.addWidget(self.P6_2)
        self.label_55 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.label_55.setFont(font)
        self.label_55.setObjectName("label_55")
        self.horizontalLayout_7.addWidget(self.label_55)
        self.P6_3 = QtWidgets.QLCDNumber(Dialog)
        self.P6_3.setDigitCount(2)
        self.P6_3.setProperty("intValue", 99)
        self.P6_3.setObjectName("P6_3")
        self.horizontalLayout_7.addWidget(self.P6_3)
        self.gridLayout_7.addLayout(self.horizontalLayout_7, 2, 1, 1, 1)
        self.verticalLayout_8.addLayout(self.gridLayout_7)
        self.verticalLayout_9.addLayout(self.verticalLayout_8)
        self.table = QtWidgets.QTabWidget(Dialog)
        self.table.setObjectName("table")
        self.droneinfo = QtWidgets.QWidget()
        self.droneinfo.setObjectName("droneinfo")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.droneinfo)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.label_5 = QtWidgets.QLabel(self.droneinfo)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_10.addWidget(self.label_5)
        self.Battery = QtWidgets.QProgressBar(self.droneinfo)
        self.Battery.setProperty("value", 100)
        self.Battery.setObjectName("Battery")
        self.horizontalLayout_10.addWidget(self.Battery)
        self.verticalLayout_6.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_6 = QtWidgets.QLabel(self.droneinfo)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_11.addWidget(self.label_6)
        self.wifi_snr = QtWidgets.QProgressBar(self.droneinfo)
        self.wifi_snr.setProperty("value", 99)
        self.wifi_snr.setObjectName("wifi_snr")
        self.horizontalLayout_11.addWidget(self.wifi_snr)
        self.SNR_Check = QtWidgets.QPushButton(self.droneinfo)
        self.SNR_Check.setObjectName("SNR_Check")
        self.horizontalLayout_11.addWidget(self.SNR_Check)
        self.verticalLayout_6.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.Height = QtWidgets.QLabel(self.droneinfo)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Height.setFont(font)
        self.Height.setObjectName("Height")
        self.horizontalLayout_12.addWidget(self.Height)
        self.TOF = QtWidgets.QLabel(self.droneinfo)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.TOF.setFont(font)
        self.TOF.setAcceptDrops(False)
        self.TOF.setObjectName("TOF")
        self.horizontalLayout_12.addWidget(self.TOF)
        self.verticalLayout_6.addLayout(self.horizontalLayout_12)
        self.F_Time = QtWidgets.QLabel(self.droneinfo)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.F_Time.setFont(font)
        self.F_Time.setObjectName("F_Time")
        self.verticalLayout_6.addWidget(self.F_Time)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_9 = QtWidgets.QLabel(self.droneinfo)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_9.setFont(font)
        self.label_9.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_5.addWidget(self.label_9)
        self.temp = QtWidgets.QLabel(self.droneinfo)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.temp.setFont(font)
        self.temp.setObjectName("temp")
        self.verticalLayout_5.addWidget(self.temp)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.table.addTab(self.droneinfo, "")
        self.setting = QtWidgets.QWidget()
        self.setting.setObjectName("setting")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.setting)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.label_11 = QtWidgets.QLabel(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_11.setFont(font)
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_16.addWidget(self.label_11)
        self.IPAddress = QtWidgets.QLineEdit(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.IPAddress.setFont(font)
        self.IPAddress.setAlignment(QtCore.Qt.AlignCenter)
        self.IPAddress.setObjectName("IPAddress")
        self.horizontalLayout_16.addWidget(self.IPAddress)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_16.addItem(spacerItem1)
        self.verticalLayout_7.addLayout(self.horizontalLayout_16)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_27 = QtWidgets.QLabel(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_27.setFont(font)
        self.label_27.setObjectName("label_27")
        self.horizontalLayout_14.addWidget(self.label_27)
        self.Height_Spinbox = QtWidgets.QSpinBox(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Height_Spinbox.setFont(font)
        self.Height_Spinbox.setMinimum(20)
        self.Height_Spinbox.setMaximum(500)
        self.Height_Spinbox.setObjectName("Height_Spinbox")
        self.horizontalLayout_14.addWidget(self.Height_Spinbox)
        self.label_28 = QtWidgets.QLabel(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_28.setFont(font)
        self.label_28.setObjectName("label_28")
        self.horizontalLayout_14.addWidget(self.label_28)
        self.horizontalLayout_15.addLayout(self.horizontalLayout_14)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_31 = QtWidgets.QLabel(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_31.setFont(font)
        self.label_31.setObjectName("label_31")
        self.horizontalLayout_13.addWidget(self.label_31)
        self.Rotation_Spinbox = QtWidgets.QSpinBox(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Rotation_Spinbox.setFont(font)
        self.Rotation_Spinbox.setMinimum(1)
        self.Rotation_Spinbox.setMaximum(360)
        self.Rotation_Spinbox.setProperty("value", 45)
        self.Rotation_Spinbox.setObjectName("Rotation_Spinbox")
        self.horizontalLayout_13.addWidget(self.Rotation_Spinbox)
        self.label_32 = QtWidgets.QLabel(self.setting)
        self.label_32.setObjectName("label_32")
        self.horizontalLayout_13.addWidget(self.label_32)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem2)
        self.horizontalLayout_15.addLayout(self.horizontalLayout_13)
        self.verticalLayout_7.addLayout(self.horizontalLayout_15)
        self.horizontalLayout_33 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_33.setObjectName("horizontalLayout_33")
        self.radioButton1 = QtWidgets.QRadioButton(self.setting)
        self.radioButton1.setText("")
        self.radioButton1.setChecked(True)
        self.radioButton1.setObjectName("radioButton1")
        self.horizontalLayout_33.addWidget(self.radioButton1)
        self.horizontalLayout_34 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_34.setObjectName("horizontalLayout_34")
        self.label_35 = QtWidgets.QLabel(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_35.setFont(font)
        self.label_35.setObjectName("label_35")
        self.horizontalLayout_34.addWidget(self.label_35)
        self.Master_Spinbox = QtWidgets.QSpinBox(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Master_Spinbox.setFont(font)
        self.Master_Spinbox.setMinimum(20)
        self.Master_Spinbox.setMaximum(500)
        self.Master_Spinbox.setProperty("value", 20)
        self.Master_Spinbox.setObjectName("Master_Spinbox")
        self.horizontalLayout_34.addWidget(self.Master_Spinbox)
        self.label_36 = QtWidgets.QLabel(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_36.setFont(font)
        self.label_36.setObjectName("label_36")
        self.horizontalLayout_34.addWidget(self.label_36)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_34.addItem(spacerItem3)
        self.horizontalLayout_33.addLayout(self.horizontalLayout_34)
        self.verticalLayout_7.addLayout(self.horizontalLayout_33)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.radioButton3 = QtWidgets.QRadioButton(self.setting)
        self.radioButton3.setText("")
        self.radioButton3.setObjectName("radioButton3")
        self.horizontalLayout_9.addWidget(self.radioButton3)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout_41 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_41.setObjectName("horizontalLayout_41")
        self.label_41 = QtWidgets.QLabel(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_41.setFont(font)
        self.label_41.setObjectName("label_41")
        self.horizontalLayout_41.addWidget(self.label_41)
        self.F_B_SpinBox = QtWidgets.QSpinBox(self.setting)
        self.F_B_SpinBox.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.F_B_SpinBox.setFont(font)
        self.F_B_SpinBox.setMinimum(20)
        self.F_B_SpinBox.setMaximum(500)
        self.F_B_SpinBox.setProperty("value", 20)
        self.F_B_SpinBox.setObjectName("F_B_SpinBox")
        self.horizontalLayout_41.addWidget(self.F_B_SpinBox)
        self.label_42 = QtWidgets.QLabel(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_42.setFont(font)
        self.label_42.setObjectName("label_42")
        self.horizontalLayout_41.addWidget(self.label_42)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_41)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_43 = QtWidgets.QLabel(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_43.setFont(font)
        self.label_43.setObjectName("label_43")
        self.horizontalLayout.addWidget(self.label_43)
        self.L_R_Spinbox = QtWidgets.QSpinBox(self.setting)
        self.L_R_Spinbox.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.L_R_Spinbox.setFont(font)
        self.L_R_Spinbox.setMinimum(20)
        self.L_R_Spinbox.setMaximum(500)
        self.L_R_Spinbox.setProperty("value", 20)
        self.L_R_Spinbox.setObjectName("L_R_Spinbox")
        self.horizontalLayout.addWidget(self.L_R_Spinbox)
        self.label_44 = QtWidgets.QLabel(self.setting)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.label_44.setFont(font)
        self.label_44.setObjectName("label_44")
        self.horizontalLayout.addWidget(self.label_44)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.horizontalLayout_8.addLayout(self.horizontalLayout)
        self.horizontalLayout_9.addLayout(self.horizontalLayout_8)
        self.verticalLayout_7.addLayout(self.horizontalLayout_9)
        self.table.addTab(self.setting, "")
        self.verticalLayout_9.addWidget(self.table)
        self.loglist = QtWidgets.QTextEdit(Dialog)
        self.loglist.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.loglist.setObjectName("loglist")
        self.verticalLayout_9.addWidget(self.loglist)
        self.horizontalLayout_18.addLayout(self.verticalLayout_9)

        self.retranslateUi(Dialog)
        self.contorlWidget.setCurrentIndex(0)
        self.table.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Tello_Gui_M_ver"))
        self.Forward_M1.setText(_translate("Dialog", "↑"))
        self.Left_M1.setText(_translate("Dialog", "← "))
        self.Right_M1.setText(_translate("Dialog", "→ "))
        self.Backward_M1.setText(_translate("Dialog", "↓"))
        self.TakeOff_M1.setText(_translate("Dialog", "Take Off"))
        self.Connect_M1.setText(_translate("Dialog", "Connect"))
        self.Land_M1.setText(_translate("Dialog", "Land"))
        self.Up_M1.setText(_translate("Dialog", "Up"))
        self.CCW_M1.setText(_translate("Dialog", "CCW"))
        self.CW_M1.setText(_translate("Dialog", "CW"))
        self.Down_M1.setText(_translate("Dialog", "Down"))
        self.contorlWidget.setTabText(self.contorlWidget.indexOf(self.mode1), _translate("Dialog", "Mode1"))
        self.Forward_M2.setText(_translate("Dialog", "↑"))
        self.CCW_M2.setText(_translate("Dialog", "CCW"))
        self.CW_M2.setText(_translate("Dialog", "CW"))
        self.Backward_M2.setText(_translate("Dialog", "↓"))
        self.TakeOff_M2.setText(_translate("Dialog", "Take Off"))
        self.Connect_M2.setText(_translate("Dialog", "Connect"))
        self.Land_M2.setText(_translate("Dialog", "Land"))
        self.Left_M2.setText(_translate("Dialog", "← "))
        self.Right_M2.setText(_translate("Dialog", "→ "))
        self.Up_M2.setText(_translate("Dialog", "Up"))
        self.Down_M2.setText(_translate("Dialog", "Down"))
        self.contorlWidget.setTabText(self.contorlWidget.indexOf(self.tab2), _translate("Dialog", "Mode2"))
        self.TimerReset.setText(_translate("Dialog", "RESET"))
        self.label.setText(_translate("Dialog", "분"))
        self.label_2.setText(_translate("Dialog", "초"))
        self.label_7.setText(_translate("Dialog", "분"))
        self.label_12.setText(_translate("Dialog", "초"))
        self.label_8.setText(_translate("Dialog", "분"))
        self.label_13.setText(_translate("Dialog", "초"))
        self.label_49.setText(_translate("Dialog", "분"))
        self.label_50.setText(_translate("Dialog", "초"))
        self.label_51.setText(_translate("Dialog", "분"))
        self.label_52.setText(_translate("Dialog", "초"))
        self.label_56.setText(_translate("Dialog", "분"))
        self.label_57.setText(_translate("Dialog", "초"))
        self.label_54.setText(_translate("Dialog", "분"))
        self.label_55.setText(_translate("Dialog", "초"))
        self.label_5.setText(_translate("Dialog", "BATTERY"))
        self.label_6.setText(_translate("Dialog", "Wi-Fi SNR"))
        self.SNR_Check.setText(_translate("Dialog", "Check"))
        self.Height.setText(_translate("Dialog", "Height: 1234cm"))
        self.TOF.setText(_translate("Dialog", "TOF: 1234cm"))
        self.F_Time.setText(_translate("Dialog", "Flight Time: 00:00:00"))
        self.label_9.setText(_translate("Dialog", "Temperature"))
        self.temp.setText(_translate("Dialog", "Min: 00ºC Max: 00ºC"))
        self.table.setTabText(self.table.indexOf(self.droneinfo), _translate("Dialog", "Drone info"))
        self.label_11.setText(_translate("Dialog", "My IP  Address"))
        self.IPAddress.setText(_translate("Dialog", "192.168.10.2"))
        self.label_27.setText(_translate("Dialog", "Height(Up,Down)"))
        self.label_28.setText(_translate("Dialog", "CM"))
        self.label_31.setText(_translate("Dialog", "CCW,CW"))
        self.label_32.setText(_translate("Dialog", "º"))
        self.label_35.setText(_translate("Dialog", "Move(↑,↓,←, →,)"))
        self.label_36.setText(_translate("Dialog", "CM"))
        self.label_41.setText(_translate("Dialog", "Forward,Back(↑,↓)"))
        self.label_42.setText(_translate("Dialog", "CM"))
        self.label_43.setText(_translate("Dialog", "Left,Right(←, →) "))
        self.label_44.setText(_translate("Dialog", "CM"))
        self.table.setTabText(self.table.indexOf(self.setting), _translate("Dialog", "Setting"))
        self.tempTextFormat = "Min: %02dºC Max: %02dºC"
        self.HeightTextFormat = "Height: %4dcm"
        self.TOF_TextFormat = "TOF: %4dcm"
        self.F_Time.setText(_translate("Dialog", "Flight Time: 00:00:00"))
        self.F_TimeTextFormat = "Flight Time: %02d:%02d:%02d"

    def updateIP(self):
        ip = self.IPAddress.text()
        self.tello.local_main_ip = ip
        self.log('IP updated : %s' % ip)
    def enable(self):
        if self.radioButton1.isChecked():
            self.Master_Spinbox.setEnabled(True)
            self.F_B_SpinBox.setEnabled(False)
            self.L_R_Spinbox.setEnabled(False)
            self.updateAll()
        else:
            self.Master_Spinbox.setEnabled(False)
            self.F_B_SpinBox.setEnabled(True)
            self.L_R_Spinbox.setEnabled(True)
            self.updateFB()
            self.updateLR()

    def updateLR(self):
        self.delta_LR = self.L_R_Spinbox.value()
    def updateFB(self):
        self.delta_FB = self.F_B_SpinBox.value()
    def updateAll(self):
        self.delta_FB = self.Master_Spinbox.value()
        self.delta_LR = self.Master_Spinbox.value()
    def updateRotation(self):
        self.delta_rotate = self.Rotation_Spinbox.value()
    def updateHeight(self):
        self.delta_height = self.Height_Spinbox.value()
    def connect(self):
        _translate = QtCore.QCoreApplication.translate
        print("Connecting...")
        self.resetDetectionInfo()
        if self.tello.tryConnect():
            print("Connnected Successfuly")
            self.Connect_M1.setText(_translate("Dialog", "DisConnect"))
            self.Connect_M2.setText(_translate("Dialog", "DisConnect"))
            self.Connect_M1.clicked.disconnect()
            self.Connect_M2.clicked.disconnect()
            self.Connect_M1.clicked.connect(self.disconnect)
            self.Connect_M2.clicked.connect(self.disconnect)
            self.button_on_off(True)
            self.log('connected')
        else:
            print("Connection failed")
            self.log("연결실패")
    def disconnect(self):
        _translate = QtCore.QCoreApplication.translate
        self.tello.disconnect()
        self.Connect_M1.setText(_translate("Dialog", "Connect"))
        self.Connect_M2.setText(_translate("Dialog", "Connect"))
        self.Connect_M1.clicked.disconnect()
        self.Connect_M2.clicked.disconnect()
        self.Connect_M1.clicked.connect(self.connect)
        self.Connect_M2.clicked.connect(self.connect)
        self.videoimg.setPixmap(QtGui.QPixmap(":/Picture/sponsor.jpg"))
        self.button_on_off(False)
        self.log('disconnected')
    def button_on_off(self, state):
        self.Forward_M1.setEnabled(state)
        self.Forward_M2.setEnabled(state)
        # backward
        self.Backward_M1.setEnabled(state)
        self.Backward_M2.setEnabled(state)
        # left
        self.Left_M1.setEnabled(state)
        self.Left_M2.setEnabled(state)
        # right
        self.Right_M1.setEnabled(state)
        self.Right_M2.setEnabled(state)
        # Up
        self.Up_M1.setEnabled(state)
        self.Up_M2.setEnabled(state)
        # Down
        self.Down_M1.setEnabled(state)
        self.Down_M2.setEnabled(state)
        # CW
        self.CW_M1.setEnabled(state)
        self.CW_M2.setEnabled(state)
        # CCW
        self.CCW_M1.setEnabled(state)
        self.CCW_M2.setEnabled(state)
        # takeoff
        self.TakeOff_M1.setEnabled(state)
        self.TakeOff_M2.setEnabled(state)
        # snrCheck
        self.SNR_Check.setEnabled(state)
        self.SNR_Check.setEnabled(state)
    def takeoff(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        cmd = "takeoff"
        self.log(cmd)
        self.tello.send_command(cmd)
    def land(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        cmd = "land"
        self.log(cmd)
        self.tello.send_command(cmd)
    def moveforward(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        cmd = "forward %d" % self.delta_FB
        self.log(cmd)
        self.tello.send_command(cmd)
    def movebackward(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        cmd = "back %d" % self.delta_FB
        self.log(cmd)
        self.tello.send_command(cmd)
    def moveleft(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        cmd = "left %d" % self.delta_LR
        self.log(cmd)
        self.tello.send_command(cmd)
    def moveright(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        cmd = "right %d" % self.delta_LR
        self.log(cmd)
        self.tello.send_command(cmd)
    def Up(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        cmd = "up %d" % self.delta_height
        self.log(cmd)
        self.tello.send_command(cmd)
    def Down(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        cmd = "down %d" % self.delta_height
        self.log(cmd)
        self.tello.send_command(cmd)
    def rotateCW(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        cmd = "cw %d" % self.delta_rotate
        self.log(cmd)
        self.tello.send_command(cmd)
    def rotateCCW(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        cmd = "ccw %d" % self.delta_rotate
        self.log(cmd)
        self.tello.send_command(cmd)
    def check(self):
        if self.tello.socket is None:
            self.log("tello is not connected.")
            return
        self.requestSNR = True
        cmd = "wifi?"
        self.log(cmd)
        self.tello.send_command(cmd)
import Tello_rc

if __name__ == "__main__":

    import sys
    try:
        if not os.path.exists('./captureResult'):
            os.makedirs('./captureResult')
    except Exception as err:
        print('captureResult디렉토리 확인중에 문제가 발생했습니다.')
        print(err.__str__())
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    if len(sys.argv) < 2:
        print("usage : python Tello_Gui_M_ver.py [True|False]")
        exit(0)
    if sys.argv[1] == "False":
        bObjectDetection =  False
    elif sys.argv[1] == "True":
        bObjectDetection = True
    else:
        print("잘못된 매개변수 : %s"%sys.argv[1])
        exit(0)
    ui = Ui_Dialog(Dialog, 'GPU', bObjectDetection)
    Dialog.show()
    o = app.exec_()
    if ui.tello.cap is not None:
        ui.tello.cap.release()
        print('cap release')
    sys.exit(o)
