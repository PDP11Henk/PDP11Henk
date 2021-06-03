import time
import wx
import serial
from threading import Thread


# define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    # define Result Event
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    # simple event to carry arbitrary result data
    def __init__(self, data):
        # init Result Event
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


class ReceiveThread(Thread):
    def __init__(self, wxObject, comPort):
        Thread.__init__(self)
        self.wxObject = wxObject
        self.comPort = comPort
        self.start()             # start the thread


    def run(self):
        # run the thread
        textPrinted = False
        tick = 0
        while self.comPort.isOpen():
            if textPrinted == False:
                textPrinted = True
                print(">   receiver thread started")
                # time.sleep(5)
            # test code to generate an event (based on timer)
            # time.sleep(1)
            # tick = tick + 1
            # wx.PostEvent(self.wxObject, ResultEvent(tick))   # for timer test
            numberOfDataBytes = self.comPort.inWaiting()
            if numberOfDataBytes != 0:
                dataByte = self.comPort.read(1)   # blocking read operation
                #print(">   received data byte %2X", dataByte)
                wx.PostEvent(self.wxObject, ResultEvent(dataByte))
        print(">   receiver thread stopped")

        #if self.comPort.isOpen():
        #    print(">   receiver thread started")
        #numberOfDataBytes = self.comPort.inWaiting()
        #if numberOfDataBytes != 0:
        #    dataByte = self.comPort.read(1)   # blocking read operation
        #for i in range(5):
        #    time.sleep(1)
        #    amtOfTime = i + 1
        #    wx.PostEvent(self.wxObject, ResultEvent(amtOfTime))
        #time.sleep(1)
        #wx.PostEvent(self.wxObject, ResultEvent("Thread finished!"))
        #print(">   receiver thread stopped")


 
###################################################################################################
###################################################################################################
###################################################################################################

class TabPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        wx.StaticLine(self, -1, (5, 260), (615, 3))
        
###################################################################################################


class NotebookDemo(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_TOP)

        self.channelSelection   = "USB"
        self.HSIdevice2Address  = 0x49
        self.commPortID         = ""
        self.previousCommPort   = ""
        self.commPortIDtoClose  = ""
        self.commPortOpened     = False                   # flag COMM port opened
        self.commPortValid      = False                   # only for "error sign" blinking
        self.prevDiagLEDmode    = "heartbeat"
        self.validateDOAdata    = True
        self.bytesInPacket      = 0                       # number of received data bytes
        self.packet             = [0,0,0,0,0,0,0,0]       # 0x77 0x77 HDG[2] CRS[2] CR LF

        self.CDIsliderValue     = 512

        self.crsDriveSetting             = 0                # default "North" (?)
        self.defaultCrsDriveS1offset     = "156"
        self.defaultCrsDriveS2offset     = "497"
        self.defaultCrsDriveS3offset     = "838"
        self.maxCrsDriveOffset           = 1023
        self.crsDriveS1offset            = self.defaultCrsDriveS1offset
        self.crsDriveS2offset            = self.defaultCrsDriveS2offset
        self.crsDriveS3offset            = self.defaultCrsDriveS3offset
        self.CMD_CRS_OFFS_L              = 19
        self.CMD_CRS_OFFS_H              = 20
        self.CMD_LOAD_CRS                = 21
        self.CMD_CRS_Q1                  = 15
        self.crsDriveSettingValid        = True
        self.crsDriveEntryErrorShown     = False
        self.crsCrossOverSettingValid    = True
        self.crsCrossOverEntryErrorShown = False


        # HSI #2 interface commands (from hsi2-main.jal)
        self.CMD_CDI_0        = 0      # CDI indicator
        self.CMD_NAV_WARN     = 4      # Navigation warning flag indicator
        self.CMD_TO_FROM      = 5      # TO / FROM indicators
        self.CMD_HDG_REQ      = 6      # request HEADING data
        self.CMD_HDG_CONV     = 7      # convert HDG data to degree value [Y/N]
        self.CMD_HDG_NOISE    = 8      # set heading signal noise threshold
        self.CMD_CRS_REQ      = 9      # request COURSE data
        self.CMD_CRS_CONV     = 10     # convert CRS data to degree value [Y/N]
        self.CMD_CRS_NOISE    = 11     # set course signal noise threshold
        self.CMD_SINCOS_CROSS = 12     # course sine/cosine 45° cross-over value
        self.CMD_SEND_USB     = 13     # send data via USB method option
        self.CMD_SEND_DELAY   = 14     # set interval between USB transmissions
        self.CMD_SINCOS_ALIGN = 15     # en/disable SIN/COS alignment output mode
        self.CMD_CRS_Q1       = 16     # set Course Exciter
        self.CMD_CRS_OFFS_L   = 20     # load offset value (lo 8 bits)  (1st cmd)
        self.CMD_CRS_OFFS_H   = 21     # load offset value (hi 2 bits)  (2nd cmd)
        self.CMD_LOAD_CRS     = 22     # load COURSE offset value mask  (3rd cmd)
        self.CMD_OUT_A        = 23     # output A
        self.CMD_OUT_B        = 24     # output B
        self.CMD_OUT_SPARE24  = 25     # spare output (24V)

        self.CMD_CRS_S1       = 26     # set output value COURSE S1
        self.CMD_CRS_S2       = 27     # set output value COURSE S2
        self.CMD_CRS_S3       = 28     # set output value COURSE S3
        self.CMD_CRS_POL      = 29     # activate COURSE S1, S2, S3, and polarity
        self.CMD_WTCHDOG_DIS  = 30     # disabled watchdog
        self.CMD_WTCHDOG_ENA  = 31     # enable watchdog
        self.CMD_DIAGMODE     = 32     # set diagnostic LED operating mode
        self.lastSubAddress   = 35     # some undocumented debug commands


        self.smallFont = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.errorImage = wx.Bitmap("error.gif")


        # Exit button
        self.buttonExit = wx.Button(self, label="Exit", pos=(500, 300), size=(100, 25))
        self.buttonExit.SetForegroundColour('#ff0000')
        self.buttonExit.Bind(wx.EVT_BUTTON, self.ExitClick)
        
        # ID myself
        self.IDline = wx.StaticText(self, label='HSI  board #2  test tool  - V1.0.2  October 2019.', pos=(10, 330))
        self.IDline.SetFont(self.smallFont)
        self.IDline.SetForegroundColour("#0000FF")

        # define timer
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timerIsRunning = False
        self.startTimer(500)                  # initially COM port not assigned
        
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.receiveData)



#-- TAB #1  Connection  ---------------------------------------------------------------------------
        tabOne = TabPanel(self)
        tabOne.SetBackgroundColour("White")
        self.AddPage(tabOne, "Connection")
 
        # find the available COM ports (code works only for Windows)
        COMports = ['COM%s' % (i + 1) for i in range(64)]
        availableCOMports = []
        for port in COMports:
            try:
                s = serial.Serial(port)
                s.close()
                availableCOMports.append(port)
            except (OSError, serial.SerialException):
                pass
        print("--- discovered COM ports:", availableCOMports)

        # radio buttons for communication type selection: USB or PHCC
        radioButtonList = ['USB', 'PHCC']
        self.rbox = wx.RadioBox(tabOne, label = 'Connection type', pos = (30,40),
                                choices = radioButtonList, majorDimension = 1)
        self.rbox.Bind(wx.EVT_RADIOBOX,self.onConnectionBox)

        # display COM port selection
        wx.StaticBox(tabOne, label='COM ports', pos=(180, 40), size=(170, 120))
        textHSI1 = wx.StaticText(tabOne, label='HSI #2', pos=(194, 65))
        textHSI1.SetFont(self.smallFont)
        textHSI1.SetForegroundColour("#000000")
        self.cbComm1 = wx.ComboBox(tabOne, pos=(240, 60), size=(70, 25), choices=availableCOMports, style=wx.CB_READONLY)
        self.cbComm1.SetToolTip(wx.ToolTip("set COM port"))
        self.cbComm1.Bind(wx.EVT_COMBOBOX, self.OnSelectCommPort)

        statusFont = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)
        openClosedFont = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.textStatus = wx.StaticText(tabOne, label='status', pos=(194, 91))
        self.textStatus.SetFont(statusFont)
        self.textStatus.SetForegroundColour("#0000FF")
        self.textStatusOpened = wx.StaticText(tabOne, label='Opened', pos=(240, 91))
        self.textStatusClosed = wx.StaticText(tabOne, label='Closed', pos=(240, 91))
        self.textStatusOpened.SetFont(openClosedFont)
        self.textStatusClosed.SetFont(openClosedFont)
        self.textStatusOpened.SetForegroundColour("#04B431")
        self.textStatusClosed.SetForegroundColour("#FF0000")
        self.textStatus.Hide()
        self.textStatusOpened.Hide()
        self.textStatusClosed.Hide()

        self.errorCommPort = wx.StaticBitmap(tabOne, -1, self.errorImage)
        self.errorCommPort.SetPosition((315, 58))
        self.errorCommPortShown = True

        # communication channel OPEN button
        self.buttonCommOpen = wx.Button(tabOne, label="", pos=(193, 120), size=(144, 25))
        self.buttonCommOpen.SetBackgroundColour('#cccccc')
        self.buttonCommOpen.SetForegroundColour('#000000')
        self.buttonCommOpen.Bind(wx.EVT_BUTTON, self.onCommOpenClick)

        # diagnostic LED
        wx.StaticBox(tabOne, label='Diagnostics LED', pos=(390, 40), size=(150, 55))

        diagLEDmodes = ['heartbeat', 'off', 'on', 'ACK', 'DOA']
        self.cbDiagLED = wx.ComboBox(tabOne, pos=(400, 60), size=(80, 25), choices=diagLEDmodes, style=wx.CB_READONLY)
        self.cbDiagLED.SetToolTip(wx.ToolTip("select LED diag mode"))
        self.cbDiagLED.SetValue('heartbeat')
        self.cbDiagLED.Bind(wx.EVT_COMBOBOX, self.OnSelectDiagLED)

        self.buttonDiagLED = wx.Button(tabOne, label="Set", pos=(490, 58), size=(40, 25))
        self.buttonDiagLED.SetBackgroundColour('#cccccc')
        self.buttonDiagLED.SetForegroundColour('#000000')
        self.buttonDiagLED.SetToolTip(wx.ToolTip("set LED diag mode"))
        self.buttonDiagLED.Bind(wx.EVT_BUTTON, self.onSendDiagLED)

        # User-defined outputs A, B and 24V
        wx.StaticBox(tabOne, label='User outputs', pos=(390, 120), size=(150, 95))
        self.toggleOutputA = wx.CheckBox(tabOne, label='User output A', pos=(400, 138), size=(100, 25))
        self.toggleOutputB = wx.CheckBox(tabOne, label='User output B', pos=(400, 158), size=(100, 25))
        self.toggleOutputX = wx.CheckBox(tabOne, label='User output X (24V)', pos=(400, 178), size=(120, 25))
        self.toggleOutputA.SetValue(False)
        self.toggleOutputB.SetValue(False)
        self.toggleOutputX.SetValue(False)
        self.toggleOutputA.SetToolTip(wx.ToolTip("toggle user-defined output A"))
        self.toggleOutputB.SetToolTip(wx.ToolTip("toggle user-defined output B"))
        self.toggleOutputX.SetToolTip(wx.ToolTip("toggle user-defined output X (24V)"))
        self.toggleOutputA.Bind(wx.EVT_CHECKBOX, self.toggleOutputACheckbox)
        self.toggleOutputB.Bind(wx.EVT_CHECKBOX, self.toggleOutputBCheckbox)
        self.toggleOutputX.Bind(wx.EVT_CHECKBOX, self.toggleOutputXCheckbox)



#-- TAB #2  Course / Nav indicators  --------------------------------------------------------------
        tabTwo = TabPanel(self)
        self.AddPage(tabTwo, " Course indicators ")
        self.CRSdevImage = wx.Bitmap("front-cdi.gif")
        self.CRSdevAccent = wx.StaticBitmap(tabTwo, -1, self.CRSdevImage)
        self.CRSdevAccent.SetPosition((410, 20))

        # Course Deviation Indicator and Course Deviation Warn flag
        wx.StaticBox(tabTwo, label='Course Deviation', pos=(30, 30), size=(345, 85))

        self.CDIslider = wx.Slider(tabTwo, value=512, minValue=0, maxValue=1023,
                                   pos=(40, 55), size=(200, -1), style=wx.SL_HORIZONTAL)
        self.CDIslider.Bind(wx.EVT_SLIDER, self.OnCDIsliderScroll)
        self.textCDIslider1 = wx.StaticText(tabTwo, label='min', pos=(46, 75))
        self.textCDIslider2 = wx.StaticText(tabTwo, label='ctr', pos=(134, 75))
        self.textCDIslider3 = wx.StaticText(tabTwo, label='max', pos=(216, 75))
        self.textCDIslider1.SetFont(self.smallFont)
        self.textCDIslider2.SetFont(self.smallFont)
        self.textCDIslider3.SetFont(self.smallFont)
        self.textCDIslider1.SetForegroundColour("#000000")
        self.textCDIslider2.SetForegroundColour("#000000")
        self.textCDIslider3.SetForegroundColour("#000000")
        self.CDIentrySet  = wx.Button(tabTwo, label="Set", pos=(260, 54), size=(50, 25))
        self.CDIentrySet.SetToolTip(wx.ToolTip("set CDI"))
        self.CDIentrySet.SetBackgroundColour('#99ccff')
        self.CDIentrySet.SetForegroundColour('#000000')
        self.CDIentrySet.Bind(wx.EVT_BUTTON, self.OnCDIentrySet)

        self.CDIsliderSetValue = wx.StaticText(tabTwo, label=str(self.CDIsliderValue),
                                               style=wx.ALIGN_CENTER, size=(28, 15))
        self.CDIsliderSetValue.SetPosition((127, 92))
        self.CDIsliderSetValue.SetFont(self.smallFont)
        self.CDIsliderSetValue.SetForegroundColour("#0000ff")

        self.buttonCDIwarn = wx.Button(tabTwo, label="WARN", pos=(315, 54), size=(50, 25))
        self.buttonCDIwarn.SetBackgroundColour('#F48C42')
        self.buttonCDIwarn.SetForegroundColour('#000000')
        self.buttonCDIwarn.SetToolTip(wx.ToolTip("toggle NAV warning flag"))
        self.buttonCDIwarn.Bind(wx.EVT_BUTTON, self.CDIwarnFlag)

        # TO / FROM flags
        wx.StaticBox(tabTwo, label='TO / FROM  flags', pos=(30, 143), size=(345, 65))

        self.ToFromRadioButton1 = wx.RadioButton(tabTwo, label='none', pos=(60, 173), style=wx.RB_GROUP)
        self.ToFromRadioButton2 = wx.RadioButton(tabTwo, label='TO', pos=(134, 173))
        self.ToFromRadioButton3 = wx.RadioButton(tabTwo, label='FROM', pos=(208, 173))
        self.ToFromRadioButton1.Bind(wx.EVT_RADIOBUTTON, self.ToFromIndication)
        self.ToFromRadioButton2.Bind(wx.EVT_RADIOBUTTON, self.ToFromIndication)
        self.ToFromRadioButton3.Bind(wx.EVT_RADIOBUTTON, self.ToFromIndication)



#-- TAB #3  Course / Nav indicators  --------------------------------------------------------------
        tabThree = TabPanel(self)
        self.AddPage(tabThree, " Course and Heading ")
        self.CRSHDGImage = wx.Bitmap("front-set-crs-hdg.gif")
        self.CRSHDGAccent = wx.StaticBitmap(tabThree, -1, self.CRSHDGImage)
        self.CRSHDGAccent.SetPosition((410, 20))

        dataOutputFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        # Heading setting
        hdgBoxYpos = 10
        wx.StaticBox(tabThree, label='Heading setting', pos=(30, hdgBoxYpos), size=(163, 199))
        hdgSelectionButtonList = ['Raw HDG angle data', 'Degrees converted  ']
        self.hdgOutputType = wx.RadioBox(tabThree, label = ' Data output format ', pos = (44,hdgBoxYpos+25),
                                         choices = hdgSelectionButtonList, majorDimension = 1)
        self.hdgOutputType.Bind(wx.EVT_RADIOBOX,self.onHDGoutputType)
        self.textHDGthreshold = wx.StaticText(tabThree, label='hysteresis', pos=(44, hdgBoxYpos+132))
        self.HDGhysteresisEntry = wx.TextCtrl(tabThree, value="1", pos=(104, hdgBoxYpos+131), size=(32, 21))
        self.HDGhysteresisSet  = wx.Button(tabThree, label="Set", pos=(141, hdgBoxYpos+130), size=(38, 23))
        self.HDGhysteresisSet.SetToolTip(wx.ToolTip("set HDG hysteresis threshold"))
        self.HDGhysteresisSet.SetBackgroundColour('#99ccff')
        self.HDGhysteresisSet.SetForegroundColour('#000000')
        self.HDGhysteresisSet.Bind(wx.EVT_BUTTON, self.OnHDGhysteresisSet)
        self.textShowHDGSetting = wx.TextCtrl(tabThree, value="0",
                                              style=wx.TE_READONLY | wx.TE_CENTRE, pos=(44, hdgBoxYpos+161), size=(134, 25))
        self.textShowHDGSetting.SetFont(dataOutputFont)
        self.textShowHDGSetting.SetBackgroundColour('#eeeeee')
        self.textShowHDGSetting.SetForegroundColour('#0000ff')

        # Course setting
        crsBoxYpos = 10
        wx.StaticBox(tabThree, label='Course setting', pos=(220, crsBoxYpos), size=(163, 199))
        crsSelectionButtonList = ['Raw CRS angle data', 'ADC/period data', 'Degrees converted  ']
        self.crsOutputType = wx.RadioBox(tabThree, label = ' Data output format ', pos = (234,crsBoxYpos+25),
                                         choices = crsSelectionButtonList, majorDimension = 1)
        self.crsOutputType.Bind(wx.EVT_RADIOBOX,self.onCRSoutputType)
        self.textCRSthreshold = wx.StaticText(tabThree, label='hysteresis', pos=(234, crsBoxYpos+132))
        self.CRShysteresisEntry = wx.TextCtrl(tabThree, value="1", pos=(294, crsBoxYpos+131), size=(32, 21))
        self.CRShysteresisSet  = wx.Button(tabThree, label="Set", pos=(331, crsBoxYpos+130), size=(38, 23))
        self.CRShysteresisSet.SetToolTip(wx.ToolTip("set CRS hysteresis threshold"))
        self.CRShysteresisSet.SetBackgroundColour('#99ccff')
        self.CRShysteresisSet.SetForegroundColour('#000000')
        self.CRShysteresisSet.Bind(wx.EVT_BUTTON, self.OnCRShysteresisSet)
        self.textShowCRSSetting = wx.TextCtrl(tabThree, value="0",
                                              style=wx.TE_READONLY | wx.TE_CENTRE, pos=(234, crsBoxYpos+161), size=(134, 25))
        self.textShowCRSSetting.SetFont(dataOutputFont)
        self.textShowCRSSetting.SetBackgroundColour('#eeeeee')
        self.textShowCRSSetting.SetForegroundColour('#0000ff')

        # send update
        updateBoxYpos = 217
        wx.StaticBox(tabThree, label='', pos=(30, updateBoxYpos), size=(353, 38))
        self.textMSGupdate = wx.StaticText(tabThree, label='Update', pos=(45, updateBoxYpos+15))
        self.msgUpdateRadioButton1 = wx.RadioButton(tabThree, label='never', pos=(95, updateBoxYpos+15), style=wx.RB_GROUP)
        self.msgUpdateRadioButton2 = wx.RadioButton(tabThree, label='change', pos=(154, updateBoxYpos+15))
        self.msgUpdateRadioButton3 = wx.RadioButton(tabThree, label='request', pos=(226, updateBoxYpos+15))
        self.msgUpdateRadioButton4 = wx.RadioButton(tabThree, label='interval', pos=(298, updateBoxYpos+15))
        self.msgUpdateRadioButton1.Bind(wx.EVT_RADIOBUTTON, self.msgUpdateSetting)
        self.msgUpdateRadioButton2.Bind(wx.EVT_RADIOBUTTON, self.msgUpdateSetting)
        self.msgUpdateRadioButton3.Bind(wx.EVT_RADIOBUTTON, self.msgUpdateSetting)
        self.msgUpdateRadioButton4.Bind(wx.EVT_RADIOBUTTON, self.msgUpdateSetting)

        self.msgUpdateRequestButton = wx.Button(tabThree, label="Update", pos=(410, updateBoxYpos+9), size=(70, 25))
        self.msgUpdateRequestButton.SetToolTip(wx.ToolTip("Get settings update"))
        self.msgUpdateRequestButton.SetBackgroundColour('#99ccff')
        self.msgUpdateRequestButton.SetForegroundColour('#000000')
        self.msgUpdateRequestButton.Hide()
        self.msgUpdateRequestButton.Bind(wx.EVT_BUTTON, self.OnmsgUpdateRequest)

        self.msgUpdateIntervalEntry = wx.TextCtrl(tabThree, value="50", pos=(410, updateBoxYpos+10), size=(40, 23))
        self.msgUpdateIntervalSet  = wx.Button(tabThree, label="Set", pos=(460, updateBoxYpos+9), size=(40, 25))
        self.msgUpdateIntervalSet.SetToolTip(wx.ToolTip("set update interval [*4 ms]"))
        self.msgUpdateIntervalSet.SetBackgroundColour('#99ccff')
        self.msgUpdateIntervalSet.SetForegroundColour('#000000')
        self.msgUpdateIntervalEntry.Hide()
        self.msgUpdateIntervalSet.Hide()
        self.msgUpdateIntervalSet.Bind(wx.EVT_BUTTON, self.OnmsgUpdateIntervalSet)



#-- TAB #4  Course Exciter  -------------------------------------------------------------------------
        tabFour = TabPanel(self)
        self.AddPage(tabFour, " Course Exciter ")
        self.crsDriveImage = wx.Bitmap("synchro.gif")
        self.crsDriveAccent = wx.StaticBitmap(tabFour, -1, self.crsDriveImage)
        self.crsDriveAccent.SetPosition((410, 20))

        # Course Exciter synchro setpoint entry
        wx.StaticBox(tabFour, label='Course Exciter synchro setpoint', pos=(30, 30), size=(295, 80))

        self.crsDriveEntry = wx.TextCtrl(tabFour, value="0", pos=(45, 60), size=(60, 25))
        textCrsDriveValidValues = wx.StaticText(tabFour, label='(0 ... 1023)', pos=(48, 87))
        textCrsDriveValidValues.SetFont(self.smallFont)
        self.buttonCrsDriveEntry = wx.Button(tabFour, label="Set", pos=(145, 60), size=(60, 25))
        self.buttonCrsDriveEntry.SetToolTip(wx.ToolTip("set Course Exciter angle"))
        self.buttonCrsDriveEntry.SetBackgroundColour('#99ccff')
        self.buttonCrsDriveEntry.SetForegroundColour('#000000')
        self.buttonCrsDriveEntry.Bind(wx.EVT_BUTTON, self.crsDriveEntrySet)
        self.errorCrsDriveEntry = wx.StaticBitmap(tabFour, -1, self.errorImage)
        self.errorCrsDriveEntry.SetPosition((110, 60))
        self.errorCrsDriveEntry.Hide()

        # Course Exciter increment/decrement buttons
        self.buttonCrsDriveDec = wx.Button(tabFour, label="-10", pos=(230, 60), size=(40, 24))
        self.buttonCrsDriveInc = wx.Button(tabFour, label="+10", pos=(275, 60), size=(40, 24))
        self.buttonCrsDriveInc.SetBackgroundColour('#CC3333')
        self.buttonCrsDriveInc.SetForegroundColour('#ffffff')
        self.buttonCrsDriveDec.SetBackgroundColour('#CC3333')
        self.buttonCrsDriveDec.SetForegroundColour('#ffffff')
        self.buttonCrsDriveInc.Bind(wx.EVT_BUTTON, self.crsDriveIncrement)
        self.buttonCrsDriveDec.Bind(wx.EVT_BUTTON, self.crsDriveDecrement)

        # Course Exciter offset entry fields
        wx.StaticBox(tabFour, label='Course Exciter synchro stator offsets', pos=(30, 130), size=(345, 120))

        self.textCrsDriveOffsetS1 = wx.StaticText(tabFour, label='S1 offset', pos=(45, 155))
        self.textCrsDriveOffsetS2 = wx.StaticText(tabFour, label='S2 offset', pos=(120, 155))
        self.textCrsDriveOffsetS3 = wx.StaticText(tabFour, label='S3 offset', pos=(195, 155))
        self.textCrsDriveOffsetS1.SetFont(self.smallFont)
        self.textCrsDriveOffsetS2.SetFont(self.smallFont)
        self.textCrsDriveOffsetS3.SetFont(self.smallFont)

        textCrsDriveValidOffset1 = wx.StaticText(tabFour, label='Valid range  0 ... 1023', pos=(45, 206))
        textCrsDriveValidOffset2 = wx.StaticText(tabFour, label='Delta value  341', pos=(45, 219))
        textCrsDriveValidOffset1.SetFont(self.smallFont)
        textCrsDriveValidOffset1.SetFont(self.smallFont)
        textCrsDriveValidOffset1.SetForegroundColour('#0000ff')
        textCrsDriveValidOffset2.SetForegroundColour('#0000ff')

        self.crsDriveOffsetS1Entry = wx.TextCtrl(tabFour, value=(self.defaultCrsDriveS1offset), pos=(45, 170), size=(60, 25))
        self.crsDriveOffsetS2Entry = wx.TextCtrl(tabFour, value=(self.defaultCrsDriveS2offset),pos=(120, 170), size=(60, 25))
        self.crsDriveOffsetS3Entry = wx.TextCtrl(tabFour, value=(self.defaultCrsDriveS3offset),pos=(195, 170), size=(60, 25))

        self.buttonCrsDriveOffsetSet = wx.Button(tabFour, label="Set  offsets", pos=(270, 170), size=(95, 25))
        self.buttonCrsDriveOffsetSet.SetToolTip(wx.ToolTip("set stator offsets"))
        self.buttonCrsDriveOffsetSet.SetBackgroundColour('#99ccff')
        self.buttonCrsDriveOffsetSet.SetForegroundColour('#000000')
        self.buttonCrsDriveOffsetSet.Bind(wx.EVT_BUTTON, self.sendCrsDriveOffsets)

        self.buttonCrsDriveOffsetDefault = wx.Button(tabFour, label="Load defaults", pos=(270, 210), size=(95, 25))
        self.buttonCrsDriveOffsetDefault.SetToolTip(wx.ToolTip("restore default offsets"))
        self.buttonCrsDriveOffsetDefault.SetBackgroundColour('#ffff00')
        self.buttonCrsDriveOffsetDefault.SetForegroundColour('#000000')
        self.buttonCrsDriveOffsetDefault.Bind(wx.EVT_BUTTON, self.setCrsDriveOffsetDefault)



#-- TAB #5  Raw data  -----------------------------------------------------------------------------
        tabFive = TabPanel(self)
        self.AddPage(tabFive, " Raw data ")
        self.rawDataImage = wx.Bitmap("front-raw.gif")
        self.rawDataAccent = wx.StaticBitmap(tabFive, -1, self.rawDataImage)
        self.rawDataAccent.SetPosition((410, 20))

        # Raw data address / sub-address / data
        wx.StaticBox(tabFive, label='Raw data', pos=(30, 30), size=(345, 125))
        ADV_POS = 55
        self.textDeviceAddress = wx.StaticText(tabFive, label='Device address', pos=(45, ADV_POS))
        self.textDeviceSubAddress = wx.StaticText(tabFive, label='Sub-address', pos=(155, ADV_POS))
        self.textDeviceData = wx.StaticText(tabFive, label='Data byte', pos=(265, ADV_POS))
        self.textDeviceAddress.SetFont(self.smallFont)
        self.textDeviceSubAddress.SetFont(self.smallFont)
        self.textDeviceData.SetFont(self.smallFont)

        self.textDeviceAddress.SetToolTip(wx.ToolTip("8-bit DOA DEVICE address"))
        self.textDeviceSubAddress.SetToolTip(wx.ToolTip("8-bit DOA sub-address"))
        self.textDeviceData.SetToolTip(wx.ToolTip("8-bit DOA data"))
        self.deviceAddressEntry = wx.TextCtrl(tabFive, pos=(45, ADV_POS+15), size=(70, 25))
        self.deviceAddressEntry.Value = "0x49"
        self.deviceSubAddressEntry = wx.TextCtrl(tabFive, pos=(155, ADV_POS+15), size=(70, 25))
        self.deviceDataEntry = wx.TextCtrl(tabFive, pos=(265, ADV_POS+15), size=(70, 25))

        self.buttonAdvancedSend = wx.Button(tabFive, label="Send", pos=(287, ADV_POS+60), size=(75, 25))
        self.buttonAdvancedSend.SetToolTip(wx.ToolTip("send data"))
        self.buttonAdvancedSend.SetBackgroundColour('#99ccff')
        self.buttonAdvancedSend.SetForegroundColour('#000000')
        self.buttonAdvancedSend.Bind(wx.EVT_BUTTON, self.advancedSend)

        self.errorDeviceAddress = wx.StaticBitmap(tabFive, -1, self.errorImage)
        self.errorDeviceSubAddress = wx.StaticBitmap(tabFive, -1, self.errorImage)
        self.errorDeviceData = wx.StaticBitmap(tabFive, -1, self.errorImage)
        self.errorDeviceAddress.SetPosition((117, ADV_POS+15))
        self.errorDeviceSubAddress.SetPosition((227, ADV_POS+15))
        self.errorDeviceData.SetPosition((337, ADV_POS+15))
        self.errorDeviceAddress.Hide()
        self.errorDeviceSubAddress.Hide()
        self.errorDeviceData.Hide()

        # "allow all" checkbox
        self.allowAll = wx.CheckBox(tabFive, label='Allow all', pos=(50, 120), size=(100, 25))
        self.allowAll.SetValue(False)
        self.allowAll.SetToolTip(wx.ToolTip("allow any device command"))
        self.allowAll.Bind(wx.EVT_CHECKBOX, self.allowAllCheckbox)



#-- TAB #6  Adjustments  --------------------------------------------------------------------------
        tabSix = TabPanel(self)
        self.AddPage(tabSix, "Adjustment")
        self.gearsImage = wx.Bitmap("gears.gif")
        self.gearsAccent = wx.StaticBitmap(tabSix, -1, self.gearsImage)
        self.gearsAccent.SetPosition((410, 20))

        # Text output: warning
        warningFont = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
        textAdjustWarning = wx.StaticText(tabSix, label='HSI instrument must be DISconnected', pos=(30, 20))
        textAdjustWarning.SetFont(warningFont)
        textAdjustWarning.SetForegroundColour('#ff0000')
        wx.StaticLine(tabSix, -1, (20, 40), (375, 3))

        instructionFont = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.buttonAdjustDrive = wx.Button(tabSix, label="Activate Course Exciter stator coil outputs", pos=(40, 70), size=(245, 25))
        self.buttonAdjustDrive.SetToolTip(wx.ToolTip("Start adjustment: set Course Exciter stator coils to max amplitude"))
        self.buttonAdjustDrive.SetBackgroundColour('#99ccff')
        self.buttonAdjustDrive.SetForegroundColour('#000000')
        self.buttonAdjustDrive.Bind(wx.EVT_BUTTON, self.adjustDriveOutput)
        self.buttonAdjustDriveState = 0

        self.textAdjustDrive1a = wx.StaticText(tabSix, label='Measure AC voltage amplifier output for HSI pin  [ a ]', pos=(50, 120))
        self.textAdjustDrive2a = wx.StaticText(tabSix, label='Measure AC voltage amplifier output for HSI pin  [ b ]', pos=(50, 120))
        self.textAdjustDrive3a = wx.StaticText(tabSix, label='Measure AC voltage amplifier output for HSI pin  [ c ]', pos=(50, 120))
        self.textAdjustDrive1a.SetFont(instructionFont)
        self.textAdjustDrive2a.SetFont(instructionFont)
        self.textAdjustDrive3a.SetFont(instructionFont)
        self.textAdjustDrive1a.SetForegroundColour('#0000ff')
        self.textAdjustDrive2a.SetForegroundColour('#0000ff')
        self.textAdjustDrive3a.SetForegroundColour('#0000ff')
        self.textAdjustDrive1a.Hide()
        self.textAdjustDrive2a.Hide()
        self.textAdjustDrive3a.Hide()
        self.textAdjustDrive1b = wx.StaticText(tabSix, label='Adjust trimpot P9 [S1] -> amplifier output voltage 10.00V', pos=(50, 140))
        self.textAdjustDrive2b = wx.StaticText(tabSix, label='Adjust trimpot P10 [S2] -> amplifier output voltage 10.00V', pos=(50, 140))
        self.textAdjustDrive3b = wx.StaticText(tabSix, label='Adjust trimpot P11 [S3] -> amplifier output voltage 10.00V', pos=(50, 140))
        self.textAdjustDrive1b.SetFont(instructionFont)
        self.textAdjustDrive2b.SetFont(instructionFont)
        self.textAdjustDrive3b.SetFont(instructionFont)
        self.textAdjustDrive1b.SetForegroundColour('#0000ff')
        self.textAdjustDrive2b.SetForegroundColour('#0000ff')
        self.textAdjustDrive3b.SetForegroundColour('#0000ff')
        self.textAdjustDrive1b.Hide()
        self.textAdjustDrive2b.Hide()
        self.textAdjustDrive3b.Hide()

        self.adjustDrive1done = wx.CheckBox(tabSix, label=' Adjustment Course Exciter stator coil S1 done.', pos=(50, 180), size=(260, 25))
        self.adjustDrive1done.SetValue(False)
        self.adjustDrive1done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustDrive1done.Bind(wx.EVT_CHECKBOX, self.adjustDriveS1checkbox)
        self.adjustDrive2done = wx.CheckBox(tabSix, label=' Adjustment Course Exciter stator coil S2 done.', pos=(50, 200), size=(260, 25))
        self.adjustDrive2done.SetValue(False)
        self.adjustDrive2done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustDrive2done.Bind(wx.EVT_CHECKBOX, self.adjustDriveS2checkbox)
        self.adjustDrive3done = wx.CheckBox(tabSix, label=' Adjustment Course Exciter stator coil S3 done.', pos=(50, 220), size=(260, 25))
        self.adjustDrive3done.SetValue(False)
        self.adjustDrive3done.SetToolTip(wx.ToolTip("after adjustment, tick box to finish adjustment"))
        self.adjustDrive3done.Bind(wx.EVT_CHECKBOX, self.adjustDriveS3checkbox)
        self.adjustDrive1done.Hide()
        self.adjustDrive2done.Hide()
        self.adjustDrive3done.Hide()



#-- TAB #7  Adjustments  --------------------------------------------------------------------------
        tabSeven = TabPanel(self)
        self.AddPage(tabSeven, "Tune")
        #self.gearsImage = wx.Bitmap("gears.gif")
        self.gearsAccent = wx.StaticBitmap(tabSeven, -1, self.gearsImage)
        self.gearsAccent.SetPosition((410, 20))

        # Text output: warning
        #warningFont = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
        textFineTune = wx.StaticText(tabSeven, label='HSI instrument must be connected', pos=(30, 20))
        textFineTune.SetFont(warningFont)
        textFineTune.SetForegroundColour('#ff0000')
        wx.StaticLine(tabSeven, -1, (20, 40), (375, 3))

        # Enable/disable Sin/Cos alignment checkbox
        wx.StaticBox(tabSeven, label='Sin/Cos alignment', pos=(30, 60), size=(350, 190))
        textAdjustGuide = wx.StaticText(tabSeven, label='#  See documentation.', pos=(55, 90))
        textAdjustGuide.SetFont(self.smallFont)
        textAdjustGuide.SetForegroundColour('#0000ff')
        self.checkSinCos = wx.CheckBox(tabSeven, label='Enable Sin/Cos data output', pos=(55, 110), size=(250, 25))
        self.checkSinCos.SetValue(False)
        self.checkSinCos.SetToolTip(wx.ToolTip("enable Sin/Cos raw signal output"))
        self.checkSinCos.Bind(wx.EVT_CHECKBOX, self.checkSinCosCheckbox)

        # SIN and COS raw data output fields
        textSinRawValue = wx.StaticText(tabSeven, label='raw SIN value', pos=(88, 153))
        textSinRawValue.SetFont(self.smallFont)
        textSinRawValue.SetForegroundColour('#0000ff')
        textCosRawValue = wx.StaticText(tabSeven, label='raw COS value', pos=(250, 153))
        textCosRawValue.SetFont(self.smallFont)
        textCosRawValue.SetForegroundColour('#0000ff')

        self.textShowSinSetting = wx.TextCtrl(tabSeven, value=" ",
                                              style=wx.TE_READONLY | wx.TE_CENTRE, pos=(55, 168), size=(134, 25))
        self.textShowSinSetting.SetFont(dataOutputFont)
        self.textShowSinSetting.SetBackgroundColour('#eeeeee')
        self.textShowSinSetting.SetForegroundColour('#0000ff')
        self.textShowCosSetting = wx.TextCtrl(tabSeven, value=" ",
                                              style=wx.TE_READONLY | wx.TE_CENTRE, pos=(220, 168), size=(134, 25))
        self.textShowCosSetting.SetFont(dataOutputFont)
        self.textShowCosSetting.SetBackgroundColour('#eeeeee')
        self.textShowCosSetting.SetForegroundColour('#0000ff')

        self.crsCrossOverEntry = wx.TextCtrl(tabSeven, value="708", style=wx.TE_CENTRE, pos=(175, 206), size=(60, 22))
        textCrsCrossOver = wx.StaticText(tabSeven, label='Sin/Cos cross-over', pos=(70, 208))
        textCrsCrossOverValidValues = wx.StaticText(tabSeven, label='(500 ... 900)', pos=(176, 230))
        textCrsCrossOverValidValues.SetFont(self.smallFont)
        self.buttonCrsCrossOverEntry = wx.Button(tabSeven, label="Set", pos=(270, 205), size=(60, 25))
        self.buttonCrsCrossOverEntry.SetToolTip(wx.ToolTip("set Sin/Cos 45° cross-over value"))
        self.buttonCrsCrossOverEntry.SetBackgroundColour('#99ccff')
        self.buttonCrsCrossOverEntry.SetForegroundColour('#000000')
        self.buttonCrsCrossOverEntry.Bind(wx.EVT_BUTTON, self.crsCrossOverEntrySet)
        self.errorCrsCrossOverEntry = wx.StaticBitmap(tabSeven, -1, self.errorImage)
        self.errorCrsCrossOverEntry.SetPosition((240, 205))
        self.errorCrsCrossOverEntry.Hide()


        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        #self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)


# -------------------------------------------------------------------------------------------------------

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        # print('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        # if leaving the "Adjustment" tab : disable Sin/Cos Alignment
        if old == 6:
            if (self.checkSinCos.GetValue() == True):
                print('>   Sin/Cos alignment disabled\n')
                self.sendData(self.HSIdevice2Address, self.CMD_SINCOS_ALIGN, 0)
            self.checkSinCos.SetValue(False)
            self.checkSinCos.SetToolTip(wx.ToolTip("enable Sin/Cos raw signal output"))
            self.textShowSinSetting.SetValue(" ")
            self.textShowCosSetting.SetValue(" ")
        elif old == 5:
            # hide Course Exciter adjustment procedure and de-activate start button
            self.buttonAdjustDrive.SetLabel("Activate Course Exciter stator coil outputs")
            self.buttonAdjustDrive.SetBackgroundColour('#99ccff')  # blue-ish
            self.buttonAdjustDrive.SetForegroundColour('#000000')
            self.buttonAdjustDrive.SetToolTip(wx.ToolTip("Start adjustment: set Course Exciter stator coils to max amplitude"))
            self.adjustDrive1done.SetValue(False)
            self.adjustDrive2done.SetValue(False)
            self.adjustDrive3done.SetValue(False)
            self.textAdjustDrive1a.Hide()
            self.textAdjustDrive1b.Hide()
            self.textAdjustDrive2a.Hide()
            self.textAdjustDrive2b.Hide()
            self.textAdjustDrive3a.Hide()
            self.textAdjustDrive3b.Hide()
            self.adjustDrive1done.Hide()
            self.adjustDrive2done.Hide()
            self.adjustDrive3done.Hide()
            if self.buttonAdjustDriveState == 1:
                self.buttonAdjustDriveState = 0
                self.sendData(self.HSIdevice2Address, self.CMD_CRS_S1, 0)
                self.sendData(self.HSIdevice2Address, self.CMD_CRS_S2, 0)
                self.sendData(self.HSIdevice2Address, self.CMD_CRS_S3, 0)
                self.sendData(self.HSIdevice2Address, self.CMD_CRS_POL, 0)
                print('>   Course Exciter adjustment de-activated\n')
        event.Skip()

#    def OnPageChanging(self, event):
#        old = event.GetOldSelection()
#        new = event.GetSelection()
#        sel = self.GetSelection()
#        print('OnPageChanging:,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
#        event.Skip()


# =================================================================================================

    def onConnectionBox(self, e): 
        if self.rbox.GetStringSelection() == "PHCC":
            self.channelSelection = "PHCC"
            print("    Connection =", self.channelSelection)
        else:
            self.channelSelection = "USB"
            print("    Connection =", self.channelSelection)


    def OnSelectCommPort(self, entry):
        self.previousCommPort = self.commPortID
        self.commPortID = entry.GetString()
        self.commPortValid = True   # stop error blinking

        if (self.previousCommPort == ""):
            # no COM port ever selected yet : initial situation only
            self.buttonCommOpen.SetBackgroundColour('#99ccff')
            self.buttonCommOpen.SetLabel("Open COM port")
            self.textStatus.Show()
            self.textStatusOpened.Hide()
            self.textStatusClosed.Show()

        if (self.previousCommPort == self.commPortID):
            # selection is the same as current selection : no change
            pass

        if (self.previousCommPort != self.commPortID):
            # if previous selected port was opened, it must be closed
            self.closeCOMMport(self.previousCommPort)
            self.textStatusOpened.Hide()
            self.textStatusClosed.Show()
            self.buttonCommOpen.SetLabel("Open COM port")


    def onCommOpenClick(self, event):
        if self.commPortID != "":
            if (self.buttonCommOpen.GetLabel() == "Open COM port"):
                self.openCOMMport()
                self.buttonCommOpen.SetLabel("Close COM port")
                self.textStatusClosed.Hide()
                self.textStatusOpened.Show()
                ReceiveThread(self, self.ComPort)   # start data receiver thread

            elif (self.buttonCommOpen.GetLabel() == "Close COM port"):
                self.closeCOMMport(self.commPortID)
                self.buttonCommOpen.SetLabel("Open COM port")
                self.textStatusOpened.Hide()
                self.textStatusClosed.Show()


    def receiveData(self, msg):
        # receive data from receiver thread
        data = msg.data
        if isinstance(data, bytes):
            #self.displayLbl.SetLabel("Time since thread started: %s seconds" %data)
            #print(".   bytes in receiver packet =", self.bytesInPacket)
            self.packet[self.bytesInPacket] = data
            self.bytesInPacket = self.bytesInPacket + 1
            # self.packet = [ 0x77 0x77 HDG[2] CRS[2] CR LF ]
            if self.bytesInPacket == 8:
                self.bytesInPacket = 0
                #print("### packet : ", self.packet)
                # output diagnostic message if the two header bytes are not 0x77
                header1 = int.from_bytes(self.packet[0], "big")
                header2 = int.from_bytes(self.packet[1], "big")
                if ( (header1 != 0x77) or (header2 != 0x77) ):   # 'w' = 0x77
                    print("**** header bytes in received packet not 0x77 ***")
                # packet complete, compose HDG and CRS values
                heading = int.from_bytes(self.packet[2], "big") * 256 + int.from_bytes(self.packet[3], "big")
                course  = int.from_bytes(self.packet[4], "big") * 256 + int.from_bytes(self.packet[5], "big")
                #
                # received data can be heading & course or Sin/Cos (alignment data)
                #
                if (self.checkSinCos.GetValue() == False):
                    # heading & course
                    if heading > 32768:
                        heading = 65536 - heading
                        sign = "-"
                    else:
                        sign = "+"
                    if self.hdgOutputType.GetStringSelection() == 'Raw HDG angle data':
                        showHeading = sign + str(heading)
                    else:  # 'Degrees converted  '
                        heading = heading / 10
                        showHeading = sign + str(heading)

                    if self.crsOutputType.GetStringSelection() == 'Raw CRS angle data':
                        showCourse = str(course)
                    elif self.crsOutputType.GetStringSelection() == 'ADC/period data':
                        if course > 32767:
                            # msb is set
                            course = course - 32768   # strip msb
                            showCourse = str(course) + " / 1"
                        else:
                            # msb is clear
                            showCourse = str(course) + " / 0"
                    else:  # 'Degrees converted  '
                        showCourse = str( int( (course * 360) / 4096) )
                    self.textShowHDGSetting.SetValue(showHeading)
                    self.textShowCRSSetting.SetValue(showCourse)
                    print("--- heading =", showHeading, "  course =", showCourse)
                else:
                    # Sin/Cos alignment data output
                    self.textShowSinSetting.SetValue(str(heading))
                    self.textShowCosSetting.SetValue(str(course))
                    avg = int((heading + course) / 2)
                    self.crsCrossOverEntry.SetValue(str(avg))
                    self.crsCrossOverEntry.SetForegroundColour("#FF0000")
        #else:
        #    self.displayLbl.SetLabel("%s" %data)


    def openCOMMport(self):
        print(">   opening COM port", self.commPortID)
        self.ComPort = serial.Serial(self.commPortID, baudrate=115200, parity=serial.PARITY_NONE,
                                      stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        self.commPortOpened = True
        self.textStatusClosed.Hide()
        self.textStatusOpened.Show()


    def closeCOMMport(self, portIDtoClose):
        if (self.commPortOpened == True):
            print(">   closing COM port", portIDtoClose)
            self.ComPort.close()
        self.commPortOpened = False
        self.textStatusOpened.Hide()
        self.textStatusClosed.Show()


#    def onCloseMessageReceived(self, text):
#        self.closeCOMMport(self.commPortID)


    def OnSelectDiagLED(self, event):
        value = self.cbDiagLED.GetValue()
        if (value != self.prevDiagLEDmode):
            self.buttonDiagLED.SetBackgroundColour('#99ccff')
        else:
            self.buttonDiagLED.SetBackgroundColour('#cccccc')


    def onSendDiagLED(self, event):
        value = self.cbDiagLED.GetValue()
        self.prevDiagLEDmode = value
        if value == 'heartbeat':
            self.DiagLEDdatabyte = 2
        elif value == 'on':
            self.DiagLEDdatabyte = 1
        elif value == 'off':
            self.DiagLEDdatabyte = 0
        elif value == 'ACK':
            self.DiagLEDdatabyte = 3
        else:  # 'DOA'
            self.DiagLEDdatabyte = 4
        self.sendData(self.HSIdevice2Address, self.CMD_DIAGMODE, self.DiagLEDdatabyte)
        if (self.commPortOpened == True):
            # update "Set" button color only to grey if data was actually sent!
            self.buttonDiagLED.SetBackgroundColour('#cccccc')


    def toggleOutputACheckbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.sendData(self.HSIdevice2Address, self.CMD_OUT_A, 1)
        else:
            self.sendData(self.HSIdevice2Address, self.CMD_OUT_A, 0)


    def toggleOutputBCheckbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.sendData(self.HSIdevice2Address, self.CMD_OUT_B, 1)
        else:
            self.sendData(self.HSIdevice2Address, self.CMD_OUT_B, 0)


    def toggleOutputXCheckbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.sendData(self.HSIdevice2Address, self.CMD_OUT_SPARE24, 1)
        else:
            self.sendData(self.HSIdevice2Address, self.CMD_OUT_SPARE24, 0)

# =================================================================================================

    # convert a string to a numeric, if string is not a number return 100000.
    def str2int(self, s):
        ctr = i = 0
        inError = False
        for c in reversed(s):
            digit = ord(c) - 48
            if digit < 0 or digit > 9:
                inError = True
            i += digit * (10 ** ctr)
            ctr += 1
        if inError == True:
            return 100000
        else:
            return i

# =================================================================================================

    def ToFromIndication(self, radioButton):
        state1 = str(self.ToFromRadioButton1.GetValue())
        state2 = str(self.ToFromRadioButton2.GetValue())
        state3 = str(self.ToFromRadioButton3.GetValue())
        if state2 == 'True':
            value = 1
        elif state3 == 'True':
            value = 2
        else:
            value = 0
        self.sendData(self.HSIdevice2Address, self.CMD_TO_FROM, value)

    def CDIwarnFlag(self, event):
        button = event.GetEventObject()
        buttonName = button.GetLabel()
        if buttonName == "WARN":
            button.SetLabel("warn")
            self.buttonCDIwarn.SetBackgroundColour('#AAAAAA')
            self.buttonCDIwarn.SetForegroundColour('#FFFFFF')
            self.sendData(self.HSIdevice2Address, self.CMD_NAV_WARN, 1)
        else:
            button.SetLabel("WARN")
            self.buttonCDIwarn.SetBackgroundColour('#F48C42')
            self.buttonCDIwarn.SetForegroundColour('#000000')
            self.sendData(self.HSIdevice2Address, self.CMD_NAV_WARN, 0)

    def OnCDIsliderScroll(self, e):
        obj = e.GetEventObject()
        self.CDIsliderValue = obj.GetValue()
        self.CDIsliderSetValue.SetLabel(str(self.CDIsliderValue))
        # position = "0"    --> xpos = 40
        # position = "max"  --> xpos = 405
        xpos = 40
        xspan = 212 - 40
        if self.CDIsliderValue != 0:
            xpos = xpos + int (( xspan * self.CDIsliderValue ) / 1023)
        self.CDIsliderSetValue.SetPosition((xpos, 92))

    def OnCDIentrySet(self, event):
        value = self.CDIsliderValue
        # determine subaddress and offset
        if value < 256:
            offset = 0
        elif value < 512:
            offset = 1
            value = value - 256
        elif value < 768:
            offset = 2
            value = value - 512
        else:
            offset = 3
            value = value - 768
        CDIaddress = self.CMD_CDI_0 + offset
        self.sendData(self.HSIdevice2Address, CDIaddress, value)

# =================================================================================================

    def onHDGoutputType(self, event):
        if self.hdgOutputType.GetStringSelection() == 'Raw HDG angle data':
            value = 0
        else:  # 'Degrees converted  '
            value = 1
        self.sendData(self.HSIdevice2Address, self.CMD_HDG_CONV, value)  # set HDG format


    def OnHDGhysteresisSet(self, event):
        value = self.HDGhysteresisEntry.GetValue()
        dataValue = self.str2int(value)
        if (dataValue > 127) or (value == "") :
            self.HDGhysteresisSet.SetForegroundColour('#FF0000')
        else:
            self.HDGhysteresisSet.SetForegroundColour('#000000')
            self.sendData(self.HSIdevice2Address, self.CMD_HDG_NOISE, dataValue)  # set HDG hysteresis


    def onCRSoutputType(self, event):
        if self.crsOutputType.GetStringSelection() == 'Raw CRS angle data':
            value = 0
        elif self.crsOutputType.GetStringSelection() == 'ADC/period data':
            value = 2
        else:  # 'Degrees converted  '
            value = 1
        self.sendData(self.HSIdevice2Address, self.CMD_CRS_CONV, value)  # set CRS format



    def OnCRShysteresisSet(self, event):
        value = self.CRShysteresisEntry.GetValue()
        dataValue = self.str2int(value)
        if (dataValue > 127) or (value == "") :
            self.CRShysteresisSet.SetForegroundColour('#FF0000')
        else:
            self.CRShysteresisSet.SetForegroundColour('#000000')
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_NOISE, dataValue)  # set CRS hysteresis


    def msgUpdateSetting(self, event):
        state1 = str(self.msgUpdateRadioButton1.GetValue())  # never
        state2 = str(self.msgUpdateRadioButton2.GetValue())  # change
        state3 = str(self.msgUpdateRadioButton3.GetValue())  # request
        state4 = str(self.msgUpdateRadioButton4.GetValue())  # interval
        if state2 == 'True':
            value = 3  # change
        elif state3 == 'True':
            value = 1  # request
        elif state4 == 'True':
            value = 2  # interval
        else:
            value = 0  # never
        self.sendData(self.HSIdevice2Address, self.CMD_SEND_USB, value)
        if (value == 1):
            self.msgUpdateRequestButton.Show()
        else:
            self.msgUpdateRequestButton.Hide()
        if (value == 2):
            self.msgUpdateIntervalEntry.Show()
            self.msgUpdateIntervalSet.Show()
        else:
            self.msgUpdateIntervalEntry.Hide()
            self.msgUpdateIntervalSet.Hide()


    def OnmsgUpdateRequest(self, event):
        value = 0
        self.sendData(self.HSIdevice2Address, self.CMD_HDG_REQ, value)  # request HDG
        self.sendData(self.HSIdevice2Address, self.CMD_CRS_REQ, value)  # request CRS


    def OnmsgUpdateIntervalSet(self, event):
        value = self.msgUpdateIntervalEntry.GetValue()
        dataValue = self.str2int(value)
        if (dataValue > 255) or (value == "") :
            self.msgUpdateIntervalSet.SetForegroundColour('#FF0000')
        else:
            self.msgUpdateIntervalSet.SetForegroundColour('#000000')
            self.sendData(self.HSIdevice2Address, self.CMD_SEND_DELAY, dataValue)  # set interval time

# =================================================================================================

    def setCrsDriveOffsetDefault(self, event):
        self.crsDriveOffsetS1Entry.SetValue(self.defaultCrsDriveS1offset)
        self.crsDriveOffsetS2Entry.SetValue(self.defaultCrsDriveS2offset)
        self.crsDriveOffsetS3Entry.SetValue(self.defaultCrsDriveS3offset)
        # default values are "always" correct ==> no error flags up, "set" button OK!
        self.buttonCrsDriveOffsetSet.SetBackgroundColour('#99ccff')

    def crsDriveEntrySet(self, event):
        crsDriveValue = self.crsDriveEntry.GetValue()
        value = self.str2int(crsDriveValue)
        if value > 1024:
            self.crsDriveValueSettingValid = False
            self.crsDriveEntryErrorShown = True
            self.errorCrsDriveEntry.Show()
        else:
            self.crsDriveSetting = value
            self.crsDriveSettingValid = True
            self.crsDriveEntryErrorShown = False
            self.errorCrsDriveEntry.Hide()
            # create correct command subaddress and data
            if value == 1024:
                value = 0
            command = int(value / 256)
            data = value - (command * 256)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_Q1 + command, data)
            print("[i] Course Exciter setpoint updated")


    def crsDriveIncrement(self, e):
        self.crsDriveSetting = self.crsDriveSetting + 10
        if self.crsDriveSetting >= 1024:
            self.crsDriveSetting = self.crsDriveSetting - 1024
        self.crsDriveEntryErrorShown = False
        self.errorCrsDriveEntry.Hide()
        self.crsDriveEntry.SetValue(str(self.crsDriveSetting))
        # send to Course Exciter
        value = self.crsDriveSetting
        if value == 1024:
            value = 0
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.HSIdevice2Address, self.CMD_CRS_Q1 + command, data)
        print("[i] Course Exciter setpoint updated")


    def crsDriveDecrement(self, e):
        if self.crsDriveSetting >= 10:
            self.crsDriveSetting = self.crsDriveSetting - 10
        else:
            diff = 10 - self.crsDriveSetting
            self.crsDriveSetting = 1024 - diff
        self.crsDriveEntryErrorShown = False
        self.errorCrsDriveEntry.Hide()
        self.crsDriveEntry.SetValue(str(self.crsDriveSetting))
        # send to Course Exciter
        value = self.crsDriveSetting
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.HSIdevice2Address, self.CMD_CRS_Q1 + command, data)
        print("[i] Course Exciter setpoint updated")


    def sendCrsDriveOffsets(self, e):
        offset1 = self.crsDriveOffsetS1Entry.GetValue()
        offset2 = self.crsDriveOffsetS2Entry.GetValue()
        offset3 = self.crsDriveOffsetS3Entry.GetValue()
        self.crsDriveS1offset = offset1
        self.crsDriveS2offset = offset2
        self.crsDriveS3offset = offset3
        # validate data
        allDataValid = True
        max = self.maxCrsDriveOffset
        s1Offset = self.str2int(offset1)
        s2Offset = self.str2int(offset2)
        s3Offset = self.str2int(offset3)
        if (s1Offset > max) or (offset1 == ""):
            allDataValid = False
        if (s2Offset > max) or (offset2 == ""):
            allDataValid = False
        if (s3Offset > max) or (offset3 == ""):
            allDataValid = False
        if allDataValid == True:
            self.buttonCrsDriveOffsetSet.SetBackgroundColour('#99ccff')
            # send data: LSB first, then MSB offset
            msb = int(s1Offset / 256)
            lsb = s1Offset - (msb * 256)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_OFFS_L, lsb)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_OFFS_H, msb)
            self.sendData(self.HSIdevice2Address, self.CMD_LOAD_CRS, 1)
            msb = int(s2Offset / 256)
            lsb = s2Offset - (msb * 256)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_OFFS_L, lsb)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_OFFS_H, msb)
            self.sendData(self.HSIdevice2Address, self.CMD_LOAD_CRS, 2)
            msb = int(s3Offset / 256)
            lsb = s3Offset - (msb * 256)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_OFFS_L, lsb)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_OFFS_H, msb)
            self.sendData(self.HSIdevice2Address, self.CMD_LOAD_CRS, 4)
            print("[i] Course Exciter offsets updated")
        else:
            self.buttonCrsDriveOffsetSet.SetBackgroundColour('#e05040')

# =================================================================================================

    def adjustDriveOutput(self, event):
        if self.buttonAdjustDriveState == 0:
            self.buttonAdjustDriveState = 1
            self.buttonAdjustDrive.SetLabel("De-activate Course Exciter stator coil outputs")
            self.buttonAdjustDrive.SetBackgroundColour('#F48C42')  # red-ish
            self.buttonAdjustDrive.SetForegroundColour('#ffffff')
            self.buttonAdjustDrive.SetToolTip(wx.ToolTip("Stop adjustment: set Course Exciter stator coils to zero"))
            # start measurement procedure
            self.textAdjustDrive1a.Show()
            self.textAdjustDrive1b.Show()
            self.adjustDrive1done.Show()
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_S1, 255)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_S2, 255)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_S3, 255)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_POL, 0)
            print("[i] Course Exciter adjustment started")
        else:
            self.buttonAdjustDriveState = 0
            self.buttonAdjustDrive.SetLabel("Activate Course Exciter stator coil outputs")
            self.buttonAdjustDrive.SetBackgroundColour('#99ccff')  # blue-ish
            self.buttonAdjustDrive.SetForegroundColour('#000000')
            self.buttonAdjustDrive.SetToolTip(wx.ToolTip("Start adjustment: set Course Exciter stator coils to max amplitude"))
            self.adjustDrive1done.SetValue(False)
            self.adjustDrive2done.SetValue(False)
            self.adjustDrive3done.SetValue(False)
            self.textAdjustDrive1a.Hide()
            self.textAdjustDrive1b.Hide()
            self.textAdjustDrive2a.Hide()
            self.textAdjustDrive2b.Hide()
            self.textAdjustDrive3a.Hide()
            self.textAdjustDrive3b.Hide()
            self.adjustDrive1done.Hide()
            self.adjustDrive2done.Hide()
            self.adjustDrive3done.Hide()
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_S1, 0)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_S2, 0)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_S3, 0)
            self.sendData(self.HSIdevice2Address, self.CMD_CRS_POL, 0)
            print("[i] Course Exciter adjustment terminated")


    def adjustDriveS1checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S2
            self.textAdjustDrive1a.Hide()
            self.textAdjustDrive1b.Hide()
            self.textAdjustDrive3a.Hide()
            self.textAdjustDrive3b.Hide()
            self.textAdjustDrive2a.Show()
            self.textAdjustDrive2b.Show()
            self.adjustDrive2done.SetValue(False)
            self.adjustDrive2done.Show()
        else:
            # back to check coil S1 (hide check S2 and S3)
            self.textAdjustDrive2a.Hide()
            self.textAdjustDrive2b.Hide()
            self.textAdjustDrive3a.Hide()
            self.textAdjustDrive3b.Hide()
            self.textAdjustDrive1a.Show()
            self.textAdjustDrive1b.Show()
            self.adjustDrive2done.SetValue(False)
            self.adjustDrive2done.Hide()
            self.adjustDrive3done.SetValue(False)
            self.adjustDrive3done.Hide()


    def adjustDriveS2checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S3
            self.textAdjustDrive1a.Hide()
            self.textAdjustDrive1b.Hide()
            self.textAdjustDrive2a.Hide()
            self.textAdjustDrive2b.Hide()
            self.textAdjustDrive3a.Show()
            self.textAdjustDrive3b.Show()
            self.adjustDrive3done.SetValue(False)
            self.adjustDrive3done.Show()
        else:
            # back to check coil S2 (hide check S3)
            self.textAdjustDrive1a.Hide()
            self.textAdjustDrive1b.Hide()
            self.textAdjustDrive3a.Hide()
            self.textAdjustDrive3b.Hide()
            self.textAdjustDrive2a.Show()
            self.textAdjustDrive2b.Show()
            self.adjustDrive2done.SetValue(False)
            self.adjustDrive2done.Show()
            self.adjustDrive3done.SetValue(False)
            self.adjustDrive3done.Hide()


    def adjustDriveS3checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # check done!
            self.textAdjustDrive1a.Hide()
            self.textAdjustDrive1b.Hide()
            self.textAdjustDrive2a.Hide()
            self.textAdjustDrive2b.Hide()
            self.textAdjustDrive3a.Hide()
            self.textAdjustDrive3b.Hide()
        else:
            # back to check coil S3
            self.textAdjustDrive1a.Hide()
            self.textAdjustDrive1b.Hide()
            self.textAdjustDrive2a.Hide()
            self.textAdjustDrive2b.Hide()
            self.textAdjustDrive3a.Show()
            self.textAdjustDrive3b.Show()
            self.adjustDrive3done.SetValue(False)

# =================================================================================================

    def crsCrossOverEntrySet(self, event):
        entry = self.crsCrossOverEntry.GetValue()
        value = self.str2int(entry)
        if (value < 500 or value > 900):
            self.crsCrossOverValueSettingValid = False
            self.crsCrossOverEntryErrorShown = True
            self.errorCrsCrossOverEntry.Show()
        else:
            self.crsCrossOverSetting = value
            self.crsCrossOverSettingValid = True
            self.crsCrossOverEntryErrorShown = False
            self.errorCrsCrossOverEntry.Hide()
            # create correct command subaddress and data
            data = int(value / 4)
            self.sendData(self.HSIdevice2Address, self.CMD_SINCOS_CROSS, data)
            print("[i] Course Sin/Cos cross-over setting updated")

# =================================================================================================

    def advancedSend(self, event):
        advDeviceAddress = self.deviceAddressEntry.GetValue()
        advDeviceSubAddress = self.deviceSubAddressEntry.GetValue()
        advData = self.deviceDataEntry.GetValue()
        allDataValid = True
        # process entry fields
        addressValue = 73
        if self.validateDOAdata == True:
            if advDeviceAddress == "0x49" or advDeviceAddress == "0X49" or advDeviceAddress == "73" :
                portID = "HSI-2"
            else:
                portID = ""
            if portID == "":
                self.errorDeviceAddress.Show()
                allDataValid = False
            else:
                self.errorDeviceAddress.Hide()
        else:
            addressValue = self.str2int(advDeviceAddress)
            if addressValue == 100000:
                # allow 0x.. or 0X.. format
                if (advDeviceAddress[0] == "0") and (advDeviceAddress[1] == "x" or advDeviceAddress[1] == "X"):
                    number = hex_int = int(advDeviceAddress, 16)
                    if number > 255:
                        self.errorDeviceAddress.Show()
                        allDataValid = False
                    else:
                        self.errorDeviceAddress.Hide()
                else:
                    self.errorDeviceAddress.Show()
                    allDataValid = False
            elif (addressValue > 255) and (addressValue != 100000):
                self.errorDeviceAddress.Show()
                allDataValid = False
            else:
                self.errorDeviceAddress.Hide()
        #
        subValue = self.str2int(advDeviceSubAddress)
        if self.validateDOAdata == True:
            if (subValue > self.lastSubAddress) or (advDeviceSubAddress == ""):
                self.errorDeviceSubAddress.Show()
                allDataValid = False
            else:
                self.errorDeviceSubAddress.Hide()
        else:
            if (subValue > 255) or (advDeviceSubAddress == ""):
                self.errorDeviceSubAddress.Show()
                allDataValid = False
            else:
                self.errorDeviceSubAddress.Hide()
        #
        dataValue = self.str2int(advData)
        if (dataValue > 255) or (advData == "") :
            self.errorDeviceData.Show()
            allDataValid = False
        else:
            self.errorDeviceData.Hide()
        if allDataValid == True:
            self.buttonAdvancedSend.SetBackgroundColour('#99ccff')
            self.sendData(addressValue, subValue, dataValue)
        else:
            self.buttonAdvancedSend.SetBackgroundColour('#e05040')

    def allowAllCheckbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.validateDOAdata = False
            self.errorDeviceAddress.Hide()
            self.errorDeviceSubAddress.Hide()
            self.errorDeviceData.Hide()
        else:
            self.validateDOAdata = True

# =================================================================================================

    def checkSinCosCheckbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.sendData(self.HSIdevice2Address, self.CMD_SINCOS_ALIGN, 1)
            self.checkSinCos.SetToolTip(wx.ToolTip("disable Sin/Cos raw signal output"))
        else:
            self.sendData(self.HSIdevice2Address, self.CMD_SINCOS_ALIGN, 0)
            self.checkSinCos.SetToolTip(wx.ToolTip("enable Sin/Cos raw signal output"))
            self.textShowSinSetting.SetValue(" ")
            self.textShowCosSetting.SetValue(" ")

# =================================================================================================

    def ExitClick(self, event):
        print("--- Exit HSI board #2 test tool.")
        self.closeCOMMport(self.commPortID)
        frame.Close()


# =================================================================================================
#  COMMUNICATION  routine: send data
# =================================================================================================

    def sendData(self, address, subAddress, data):
        if self.commPortOpened == True:
            if address == self.HSIdevice2Address:
                if self.channelSelection == "PHCC":
                    # using PHCC Motherboard
                    print("... sendData to", self.commPortID, \
                          "address", address, "subAddress", subAddress, "data", data)
                    phccId = 0x07
                    if self.ComPort.isOpen():
                        self.ComPort.write(phccId.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(address.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(subAddress.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                    else:
                        print("!!! COM port for HSI #2 is not open!")
                elif self.channelSelection == "USB":
                    if self.ComPort.isOpen():
                        print("... sendData to", self.commPortID, \
                              "subAddress", subAddress, "data", data)
                        self.ComPort.write(subAddress.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                    else:
                        print("!!! COM port for HSI #2 is not open!")
                else:
                    print("!!! no communication type selected (software bug)")
        else:
            print("COM port not opened: no data sent")

# =================================================================================================

    def stopTimer(self):
        if self.timerIsRunning == True:
            self.timer.Stop()
            self.timerIsRunning = False

    def startTimer(self, rate):
        if self.timerIsRunning == False:
            self.timerIsRunning = True
            self.timer.Start(rate)

    def OnTimer(self, event):
        self.stopTimer()
        # ---- handle no COM port defined flashing ERROR signs
        if self.commPortValid == False:
            # COM port not (yet) assigned
            if self.errorCommPortShown == True:
                self.errorCommPortShown = False
                self.errorCommPort.Hide()
                self.startTimer(300)
            else:
                self.errorCommPortShown = True
                self.errorCommPort.Show()
                self.startTimer(500)
        else:
            if self.errorCommPortShown == True:
                self.errorCommPortShown = False
                self.errorCommPort.Hide()
            self.startTimer(300)
        # ----
        # ----
        # ----



###################################################################################################
class HSIFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "HSI #2 demonstrator", size=(660,395))
        panel = wx.Panel(self)

        notebook = NotebookDemo(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()

        self.Show()

 
#--------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = HSIFrame()
    app.MainLoop()