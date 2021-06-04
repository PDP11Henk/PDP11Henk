
import wx
import serial

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
        self.HYDdeviceAddress   = 0x59
        self.commPortID         = ""
        self.previousCommPort   = ""
        self.commPortIDtoClose  = ""
        self.commPortOpened     = False                   # flag COMM port opened
        self.commPortValid      = False                   # only for "error sign" blinking
        self.prevDiagLEDmode    = "heartbeat"
        self.validateDOAdata    = True
        self.printTxData        = False

        self.smallFont = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.errorImage = wx.Bitmap("error.gif")

        self.HydAsetting           = 0
        self.maxHydAOffset         = 1023
        self.HydAsettingValid      = True
        self.defaultHydAS1offset   = "231"
        self.defaultHydAS2offset   = "402"
        self.HydAS1offset          = self.defaultHydAS1offset
        self.HydAS2offset          = self.defaultHydAS2offset
        self.HydAEntryErrorShown   = False

        self.HydBsetting           = 0
        self.maxHydBOffset         = 1023
        self.HydBsettingValid      = True
        self.defaultHydBS1offset   = "231"
        self.defaultHydBS2offset   = "402"
        self.HydBS1offset          = self.defaultHydBS1offset
        self.HydBS2offset          = self.defaultHydBS2offset
        self.HydBEntryErrorShown   = False

        self.simHydAStartValue     = 0
        self.simHydBStartValue     = 0
        self.simulateARunningValue = 0
        self.simulateBRunningValue = 0
        self.simulateAStepIndex    = 0
        self.simulateBStepIndex    = 0
        self.simulateAFirstStart   = True
        self.simulateBFirstStart   = True
        self.simulateStatus        = 0     # bitmask: bit0 = HydA // bit1 = HydB

        # HYD A/B interface commands (from hyd-main.jal)
        self.CMD_HYD_AQ1      = 0      # set HYD A indicator base
        self.CMD_HYD_BQ1      = 4      # set HYD B indicator base
#
        self.CMD_LD_OFFS_L    = 8      # load offset value (lo 8 bits)  -> 1st cmd
        self.CMD_LD_OFFS_H    = 9      # load offset value (hi 2 bits)  -> 2nd cmd
        self.CMD_LOAD_HYD     = 10     # load HYD PRS offset value mask -> 3rd cmd
#
        self.CMD_HYD_AX       = 11     # set output value HYD A S1
        self.CMD_HYD_AY       = 12     # set output value HYD A S3
        self.CMD_HYDA_POL     = 13     # activate HYD A S1 and S3 polarity
        self.CMD_HYD_BX       = 14     # set output value HYD B S1
        self.CMD_HYD_BY       = 15     # set output value HYD B S3
        self.CMD_HYDB_POL     = 16     # activate HYD B S1 and S3 polarity
#
        self.CMD_XA1          = 17     # control spare output XA1
        self.CMD_XA5          = 18     # control spare output XA5
        self.CMD_XB7          = 19     # control spare output XB7
#
        self.CMD_WTCHDOG_DIS  = 20     # disabled watchdog
        self.CMD_WTCHDOG_ENA  = 21     # enable watchdog
        self.CMD_DIAGMODE     = 22     # set diagnostic LED operating mode

        # Exit button
        self.buttonExit = wx.Button(self, label="Exit", pos=(500, 300), size=(100, 25))
        self.buttonExit.SetForegroundColour('#ff0000')
        self.buttonExit.Bind(wx.EVT_BUTTON, self.ExitClick)
        
        # ID myself
        self.IDline = wx.StaticText(self, label='HYDRAULIC PRESSURE A/B Indicators controller interface test tool  - V1.0  December 2020.', pos=(10, 330))
        self.IDline.SetFont(self.smallFont)
        self.IDline.SetForegroundColour("#0000FF")

        # define timer
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timerIsRunning = False
        self.startTimer(500)                  # initially COM port not assigned


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

        # checkbox to print transmitted messages
        self.enaTXdataPrint = wx.CheckBox(tabOne, label=' Display TX data', pos=(35, 178), size=(120, 25))
        self.enaTXdataPrint.SetValue(False)
        self.enaTXdataPrint.SetToolTip(wx.ToolTip("display transmitted data"))
        self.enaTXdataPrint.Bind(wx.EVT_CHECKBOX, self.enaTXdataPrintCheckbox)
        
        # display COM port selection
        wx.StaticBox(tabOne, label='COM port', pos=(180, 40), size=(175, 120))
        textHYD = wx.StaticText(tabOne, label='HYD A/B', pos=(194, 65))
        textHYD.SetFont(self.smallFont)
        textHYD.SetForegroundColour("#000000")
        self.cbComm1 = wx.ComboBox(tabOne, pos=(250, 60), size=(65, 25), choices=availableCOMports, style=wx.CB_READONLY)
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
        self.errorCommPort.SetPosition((320, 58))
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
        self.cbDiagLED.SetToolTip(wx.ToolTip("set LED diag mode"))
        self.cbDiagLED.SetValue('heartbeat')
        self.cbDiagLED.Bind(wx.EVT_COMBOBOX, self.OnSelectDiagLED)

        self.buttonDiagLED = wx.Button(tabOne, label="Set", pos=(490, 58), size=(40, 25))
        self.buttonDiagLED.SetBackgroundColour('#cccccc')
        self.buttonDiagLED.SetForegroundColour('#000000')
        self.buttonDiagLED.Bind(wx.EVT_BUTTON, self.onSendDiagLED)

        # User-defined outputs XA1, XA5, XB7
        wx.StaticBox(tabOne, label='User outputs', pos=(390, 120), size=(150, 90))
        self.toggleOutputXA1 = wx.CheckBox(tabOne, label=' User output XA1', pos=(400, 138), size=(120, 25))
        self.toggleOutputXA5 = wx.CheckBox(tabOne, label=' User output XA5', pos=(400, 158), size=(120, 25))
        self.toggleOutputXB7 = wx.CheckBox(tabOne, label=' User output XB7', pos=(400, 178), size=(120, 25))
        self.toggleOutputXA1.SetValue(False)
        self.toggleOutputXA5.SetValue(False)
        self.toggleOutputXB7.SetValue(False)
        self.toggleOutputXA1.SetToolTip(wx.ToolTip("toggle user-defined output XA1"))
        self.toggleOutputXA5.SetToolTip(wx.ToolTip("toggle user-defined output XA5"))
        self.toggleOutputXB7.SetToolTip(wx.ToolTip("toggle user-defined output XB7"))
        self.toggleOutputXA1.Bind(wx.EVT_CHECKBOX, self.toggleOutputXA1Checkbox)
        self.toggleOutputXA5.Bind(wx.EVT_CHECKBOX, self.toggleOutputXA5Checkbox)
        self.toggleOutputXB7.Bind(wx.EVT_CHECKBOX, self.toggleOutputXB7Checkbox)


#-- TAB #2  HYD A  --------------------------------------------------------------------------------
        tabTwo = TabPanel(self)
        self.AddPage(tabTwo, "HYD PRS A")
        self.hydAImage = wx.Bitmap("hyd-image.gif")
        self.hydAAccent = wx.StaticBitmap(tabTwo, -1, self.hydAImage)
        self.hydAAccent.SetPosition((410, 40))

        # HydA setpoint entry
        wx.StaticBox(tabTwo, label='Hyd A setpoint', pos=(30, 30), size=(295, 80))

        self.HydAentry = wx.TextCtrl(tabTwo, value="0", pos=(45, 60), size=(60, 25))
        textHydAValidValues = wx.StaticText(tabTwo, label='(0 ... 1023)', pos=(48, 87))
        textHydAValidValues.SetFont(self.smallFont)

        self.buttonHydAentrySet = wx.Button(tabTwo, label="Set", pos=(145, 60), size=(60, 25))
        self.buttonHydAentrySet.SetToolTip(wx.ToolTip("set HydA angle"))
        self.buttonHydAentrySet.SetBackgroundColour('#99ccff')
        self.buttonHydAentrySet.SetForegroundColour('#000000')
        self.buttonHydAentrySet.Bind(wx.EVT_BUTTON, self.HydAentrySet)
        self.errorHydAentry = wx.StaticBitmap(tabTwo, -1, self.errorImage)
        self.errorHydAentry.SetPosition((110, 60))
        self.errorHydAentry.Hide()

        # HydA increment/decrement buttons
        self.buttonHydAdec = wx.Button(tabTwo, label="-10", pos=(230, 60), size=(40, 24))
        self.buttonHydAinc = wx.Button(tabTwo, label="+10", pos=(275, 60), size=(40, 24))
        self.buttonHydAinc.SetBackgroundColour('#CC3333')
        self.buttonHydAinc.SetForegroundColour('#ffffff')
        self.buttonHydAdec.SetBackgroundColour('#CC3333')
        self.buttonHydAdec.SetForegroundColour('#ffffff')
        self.buttonHydAinc.Bind(wx.EVT_BUTTON, self.HydAincrement)
        self.buttonHydAdec.Bind(wx.EVT_BUTTON, self.HydAdecrement)

        # HydA offset entry fields
        wx.StaticBox(tabTwo, label='Synchro stator offsets', pos=(30, 130), size=(295, 120))

        self.textHydAOffsetS1 = wx.StaticText(tabTwo, label='S1 offset', pos=(45, 155))
        self.textHydAOffsetS2 = wx.StaticText(tabTwo, label='S3 offset', pos=(120, 155))
        self.textHydAOffsetS1.SetFont(self.smallFont)
        self.textHydAOffsetS2.SetFont(self.smallFont)

        textHydAValidOffset1 = wx.StaticText(tabTwo, label='Valid range  0 ... 1023', pos=(45, 206))
        textHydAValidOffset2 = wx.StaticText(tabTwo, label='Delta value  171', pos=(45, 219))
        textHydAValidOffset1.SetFont(self.smallFont)
        textHydAValidOffset1.SetFont(self.smallFont)
        textHydAValidOffset1.SetForegroundColour('#0000ff')
        textHydAValidOffset2.SetForegroundColour('#0000ff')

        self.HydAOffsetS1Entry = wx.TextCtrl(tabTwo, value=(self.defaultHydAS1offset), pos=(45, 170), size=(60, 25))
        self.HydAOffsetS2Entry = wx.TextCtrl(tabTwo, value=(self.defaultHydAS2offset),pos=(120, 170), size=(60, 25))

        self.buttonHydAOffsetSet = wx.Button(tabTwo, label="Set  offsets", pos=(220, 170), size=(95, 25))
        self.buttonHydAOffsetSet.SetToolTip(wx.ToolTip("set stator offsets"))
        self.buttonHydAOffsetSet.SetBackgroundColour('#99ccff')
        self.buttonHydAOffsetSet.SetForegroundColour('#000000')
        self.buttonHydAOffsetSet.Bind(wx.EVT_BUTTON, self.sendHydAOffsets)

        self.buttonHydAOffsetDefault = wx.Button(tabTwo, label="Load defaults", pos=(220, 210), size=(95, 25))
        self.buttonHydAOffsetDefault.SetToolTip(wx.ToolTip("restore default offsets"))
        self.buttonHydAOffsetDefault.SetBackgroundColour('#ffff00')
        self.buttonHydAOffsetDefault.SetForegroundColour('#000000')
        self.buttonHydAOffsetDefault.Bind(wx.EVT_BUTTON, self.setHydAOffsetDefault)



#-- TAB #3  HYD B  --------------------------------------------------------------------------------
        tabThree = TabPanel(self)
        self.AddPage(tabThree, "HYD PRS B")
        self.hydBImage = wx.Bitmap("hyd-image.gif")
        self.hydBAccent = wx.StaticBitmap(tabThree, -1, self.hydBImage)
        self.hydBAccent.SetPosition((410, 40))

        # HydB setpoint entry
        wx.StaticBox(tabThree, label='Hyd B setpoint', pos=(30, 30), size=(295, 80))

        self.HydBentry = wx.TextCtrl(tabThree, value="0", pos=(45, 60), size=(60, 25))
        textHydBValidValues = wx.StaticText(tabThree, label='(0 ... 1023)', pos=(48, 87))
        textHydBValidValues.SetFont(self.smallFont)
        self.buttonHydBentrySet = wx.Button(tabThree, label="Set", pos=(145, 60), size=(60, 25))
        self.buttonHydBentrySet.SetToolTip(wx.ToolTip("set HydB angle"))
        self.buttonHydBentrySet.SetBackgroundColour('#99ccff')
        self.buttonHydBentrySet.SetForegroundColour('#000000')
        self.buttonHydBentrySet.Bind(wx.EVT_BUTTON, self.HydBentrySet)
        self.errorHydBentry = wx.StaticBitmap(tabThree, -1, self.errorImage)
        self.errorHydBentry.SetPosition((110, 60))
        self.errorHydBentry.Hide()

        # HydB increment/decrement buttons
        self.buttonHydBdec = wx.Button(tabThree, label="-10", pos=(230, 60), size=(40, 24))
        self.buttonHydBinc = wx.Button(tabThree, label="+10", pos=(275, 60), size=(40, 24))
        self.buttonHydBinc.SetBackgroundColour('#CC3333')
        self.buttonHydBinc.SetForegroundColour('#ffffff')
        self.buttonHydBdec.SetBackgroundColour('#CC3333')
        self.buttonHydBdec.SetForegroundColour('#ffffff')
        self.buttonHydBinc.Bind(wx.EVT_BUTTON, self.HydBincrement)
        self.buttonHydBdec.Bind(wx.EVT_BUTTON, self.HydBdecrement)

        # HydB offset entry fields
        wx.StaticBox(tabThree, label='Synchro stator offsets', pos=(30, 130), size=(295, 120))

        self.textHydBOffsetS1 = wx.StaticText(tabThree, label='S1 offset', pos=(45, 155))
        self.textHydBOffsetS2 = wx.StaticText(tabThree, label='S3 offset', pos=(120, 155))
        self.textHydBOffsetS1.SetFont(self.smallFont)
        self.textHydBOffsetS2.SetFont(self.smallFont)

        textHydBValidOffset1 = wx.StaticText(tabThree, label='Valid range  0 ... 1023', pos=(45, 206))
        textHydBValidOffset2 = wx.StaticText(tabThree, label='Delta value  171', pos=(45, 219))
        textHydBValidOffset1.SetFont(self.smallFont)
        textHydBValidOffset1.SetFont(self.smallFont)
        textHydBValidOffset1.SetForegroundColour('#0000ff')
        textHydBValidOffset2.SetForegroundColour('#0000ff')

        self.HydBOffsetS1Entry = wx.TextCtrl(tabThree, value=(self.defaultHydBS1offset), pos=(45, 170), size=(60, 25))
        self.HydBOffsetS2Entry = wx.TextCtrl(tabThree, value=(self.defaultHydBS2offset),pos=(120, 170), size=(60, 25))

        self.buttonHydBOffsetSet = wx.Button(tabThree, label="Set  offsets", pos=(220, 170), size=(95, 25))
        self.buttonHydBOffsetSet.SetToolTip(wx.ToolTip("set stator offsets"))
        self.buttonHydBOffsetSet.SetBackgroundColour('#99ccff')
        self.buttonHydBOffsetSet.SetForegroundColour('#000000')
        self.buttonHydBOffsetSet.Bind(wx.EVT_BUTTON, self.sendHydBOffsets)

        self.buttonHydBOffsetDefault = wx.Button(tabThree, label="Load defaults", pos=(220, 210), size=(95, 25))
        self.buttonHydBOffsetDefault.SetToolTip(wx.ToolTip("restore default offsets"))
        self.buttonHydBOffsetDefault.SetBackgroundColour('#ffff00')
        self.buttonHydBOffsetDefault.SetForegroundColour('#000000')
        self.buttonHydBOffsetDefault.Bind(wx.EVT_BUTTON, self.setHydBOffsetDefault)


#-- TAB #5  Simulate  -----------------------------------------------------------------------------
        tabFive = TabPanel(self)
        self.AddPage(tabFive, "Simulate")
        self.rawDataImage = wx.Bitmap("hyd-image.gif")
        self.rawDataAccent = wx.StaticBitmap(tabFive, -1, self.rawDataImage)
        self.rawDataAccent.SetPosition((410, 40))

        simulateButtonList = ['Hyd A', 'Hyd B']
        self.simulateObjectBox = wx.RadioBox(tabFive, label = 'Simulate indicator', pos = (20,30),
                                             choices = simulateButtonList, majorDimension = 1)
        self.simulateObjectBox.Bind(wx.EVT_RADIOBOX,self.onSimulateObject)
        self.simulateObject = 0

        wx.StaticBox(tabFive, label=' Step increment', pos=(20, 135), size=(115, 55))
        self.simulateStepList = ['1', '2', '5', '10', '20' ]
        self.cbSimulateStepSelection = wx.ComboBox(tabFive, pos=(30, 155), size=(75, 25), value=self.simulateStepList[0],
                                                   choices=self.simulateStepList, style=wx.CB_READONLY)
        self.cbSimulateStepSelection.SetToolTip(wx.ToolTip("set step size"))
        self.cbSimulateStepSelection.Bind(wx.EVT_COMBOBOX, self.OnSelectSimStepSize)
        self.simulateUpdateStepASelection = 1
        self.simulateUpdateStepBSelection = 1
        self.simulateAStepValue = 1
        self.simulateBStepValue = 1

        wx.StaticBox(tabFive, label=' Update rate', pos=(20, 200), size=(115, 55))
        simulateUpdateList = ['200 ms', '400 ms', '600 ms', '800 ms', '1000 ms' ]
        self.cbSimulateRateSelection = wx.ComboBox(tabFive, pos=(30, 220), size=(75, 25), value=simulateUpdateList[1],
                                                   choices=simulateUpdateList, style=wx.CB_READONLY)
        self.cbSimulateRateSelection.SetToolTip(wx.ToolTip("set update rate"))
        self.cbSimulateRateSelection.Bind(wx.EVT_COMBOBOX, self.OnSelectSimUpdateRate)
        self.simulateUpdateRateSelection = 1
        self.simulateUpdateTime = 400

        wx.StaticBox(tabFive, label=' Start setpoint', pos=(150, 30), size=(195, 73))
        self.simulateStartEntry = wx.TextCtrl(tabFive, value=str(self.simHydAStartValue), pos=(165, 55), size=(60, 25))
        textSimulateValidValues = wx.StaticText(tabFive, label='(0 ... 1023)', pos=(168, 82))
        textSimulateValidValues.SetFont(self.smallFont)
        self.buttonsimulateStartEntrySet = wx.Button(tabFive, label="Set", pos=(265, 55), size=(60, 25))
        self.buttonsimulateStartEntrySet.SetToolTip(wx.ToolTip("set start value"))
        self.buttonsimulateStartEntrySet.SetBackgroundColour('#99ccff')
        self.buttonsimulateStartEntrySet.SetForegroundColour('#000000')
        self.buttonsimulateStartEntrySet.Bind(wx.EVT_BUTTON, self.simulateStartEntrySet)
        self.errorsimulateStartEntry = wx.StaticBitmap(tabFive, -1, self.errorImage)
        self.errorsimulateStartEntry.SetPosition((230, 55))
        self.errorsimulateStartEntry.Hide()

        wx.StaticBox(tabFive, label=' Simulate indication', pos=(150, 135), size=(195, 100))
        simulateDigitFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.textSimulateShowSetpoint = wx.TextCtrl(tabFive, value=str(self.simHydAStartValue),
                                                    style=wx.TE_READONLY | wx.TE_CENTRE, pos=(210, 160), size=(80, 25))
        self.textSimulateShowSetpoint.SetFont(simulateDigitFont)
        self.textSimulateShowSetpoint.SetBackgroundColour('#eeeeee')
        self.textSimulateShowSetpoint.SetForegroundColour('#0000ff')

        self.simulateStartButton = wx.Button(tabFive, label="Start", pos=(180, 195), size=(60, 25))
        self.simulateStartButton.SetToolTip(wx.ToolTip("start simulation"))
        self.simulateStartButton.SetBackgroundColour('#99ccff')
        self.simulateStartButton.SetForegroundColour('#000000')
        self.simulateStartButton.Bind(wx.EVT_BUTTON, self.simulateStartSimulation)
        self.simulateStopButton = wx.Button(tabFive, label="Stop", pos=(260, 195), size=(60, 25))
        self.simulateStopButton.SetToolTip(wx.ToolTip("stop simulation"))
        self.simulateStopButton.SetBackgroundColour('#eeeeee')
        self.simulateStopButton.SetForegroundColour('#000000')
        self.simulateStopButton.Bind(wx.EVT_BUTTON, self.simulateStopSimulation)



#-- TAB #6  Raw data  -----------------------------------------------------------------------------
        tabSix = TabPanel(self)
        self.AddPage(tabSix, "Raw data")
        self.rawDataImage = wx.Bitmap("hyd-image.gif")
        self.rawDataAccent = wx.StaticBitmap(tabSix, -1, self.rawDataImage)
        self.rawDataAccent.SetPosition((410, 40))

        # Raw data address / sub-address / data
        wx.StaticBox(tabSix, label='Raw data', pos=(30, 30), size=(345, 125))
        ADV_POS = 55
        self.textDeviceAddress = wx.StaticText(tabSix, label='Device address', pos=(45, ADV_POS))
        self.textDeviceSubAddress = wx.StaticText(tabSix, label='Sub-address', pos=(155, ADV_POS))
        self.textDeviceData = wx.StaticText(tabSix, label='Data byte', pos=(265, ADV_POS))
        self.textDeviceAddress.SetFont(self.smallFont)
        self.textDeviceSubAddress.SetFont(self.smallFont)
        self.textDeviceData.SetFont(self.smallFont)

        self.textDeviceAddress.SetToolTip(wx.ToolTip("8-bit DOA DEVICE address"))
        self.textDeviceSubAddress.SetToolTip(wx.ToolTip("8-bit DOA sub-address"))
        self.textDeviceData.SetToolTip(wx.ToolTip("8-bit DOA data"))
        self.deviceAddressEntry = wx.TextCtrl(tabSix, pos=(45, ADV_POS+15), size=(70, 25))
        self.deviceAddressEntry.Value = "0x59"
        self.deviceSubAddressEntry = wx.TextCtrl(tabSix, pos=(155, ADV_POS+15), size=(70, 25))
        self.deviceDataEntry = wx.TextCtrl(tabSix, pos=(265, ADV_POS+15), size=(70, 25))

        self.buttonAdvancedSend = wx.Button(tabSix, label="Send", pos=(287, ADV_POS+60), size=(75, 25))
        self.buttonAdvancedSend.SetToolTip(wx.ToolTip("send data"))
        self.buttonAdvancedSend.SetBackgroundColour('#99ccff')
        self.buttonAdvancedSend.SetForegroundColour('#000000')
        self.buttonAdvancedSend.Bind(wx.EVT_BUTTON, self.advancedSend)

        self.errorDeviceAddress = wx.StaticBitmap(tabSix, -1, self.errorImage)
        self.errorDeviceSubAddress = wx.StaticBitmap(tabSix, -1, self.errorImage)
        self.errorDeviceData = wx.StaticBitmap(tabSix, -1, self.errorImage)
        self.errorDeviceAddress.SetPosition((117, ADV_POS+15))
        self.errorDeviceSubAddress.SetPosition((227, ADV_POS+15))
        self.errorDeviceData.SetPosition((337, ADV_POS+15))
        self.errorDeviceAddress.Hide()
        self.errorDeviceSubAddress.Hide()
        self.errorDeviceData.Hide()

        # "allow all" checkbox
        self.allowAll = wx.CheckBox(tabSix, label='Allow all', pos=(50, 120), size=(100, 25))
        self.allowAll.SetValue(False)
        self.allowAll.SetToolTip(wx.ToolTip("allow any device command"))
        self.allowAll.Bind(wx.EVT_CHECKBOX, self.allowAllCheckbox)



#-- TAB #7  Adjustments  --------------------------------------------------------------------------
        tabSeven = TabPanel(self)
        self.AddPage(tabSeven, "Adjustments")
        self.gearsImage = wx.Bitmap("gears.gif")
        self.gearsAccent = wx.StaticBitmap(tabSeven, -1, self.gearsImage)
        self.gearsAccent.SetPosition((410, 30))

        # Text output: warning - disconnect HYD
        warningFont = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
        textAdjustWarning = wx.StaticText(tabSeven, label='Check  that  the  HYD  indicators  are  * NOT *  connected!', pos=(30, 20))
        textAdjustWarning.SetFont(warningFont)
        textAdjustWarning.SetForegroundColour('#ff0000')
        wx.StaticLine(tabSeven, -1, (20, 40), (375, 3))

        # adjustment object selection
        adjustButtonList = ['Symmetry', 'Hyd A', 'Hyd B']
        self.adjustObjectBox = wx.RadioBox(tabSeven, label = 'Adjust setting', pos = (20,60),
                                           choices = adjustButtonList, majorDimension = 1)
        self.adjustObjectBox.Bind(wx.EVT_RADIOBOX,self.onAdjustObject)
        self.adjustObject = 0

        # Text output for the HYD A tests
        instructionFont = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.buttonAdjustHydA = wx.Button(tabSeven, label="Activate Hyd A stator coil outputs", pos=(150, 70), size=(245, 25))
        self.buttonAdjustHydA.SetToolTip(wx.ToolTip("Start adjustment: set Hyd A stator coils to max amplitude"))
        self.buttonAdjustHydA.SetBackgroundColour('#99ccff')
        self.buttonAdjustHydA.SetForegroundColour('#000000')
        self.buttonAdjustHydA.Bind(wx.EVT_BUTTON, self.adjustHydAOutput)
        self.buttonAdjustHydA.Hide()
        self.buttonAdjustHydAState = 0

        self.textAdjustHydA1a = wx.StaticText(tabSeven, label='Measure AC voltage on HYD-PRS-A pin  [ RT ]', pos=(160, 120))
        self.textAdjustHydA2a = wx.StaticText(tabSeven, label='Measure AC voltage on HYD-PRS-A pin  [ S1 ]', pos=(160, 120))
        self.textAdjustHydA3a = wx.StaticText(tabSeven, label='Measure AC voltage on HYD-PRS-A pin  [ S3 ]', pos=(160, 120))
        self.textAdjustHydA1a.SetFont(instructionFont)
        self.textAdjustHydA2a.SetFont(instructionFont)
        self.textAdjustHydA3a.SetFont(instructionFont)
        self.textAdjustHydA1a.SetForegroundColour('#0000ff')
        self.textAdjustHydA2a.SetForegroundColour('#0000ff')
        self.textAdjustHydA3a.SetForegroundColour('#0000ff')
        self.textAdjustHydA1a.Hide()
        self.textAdjustHydA2a.Hide()
        self.textAdjustHydA3a.Hide()
        self.textAdjustHydA1b = wx.StaticText(tabSeven, label='Adjust trimpot P2 to output voltage 6.60V', pos=(160, 140))
        self.textAdjustHydA2b = wx.StaticText(tabSeven, label='Adjust trimpot P4 to output voltage 2.99V', pos=(160, 140))
        self.textAdjustHydA3b = wx.StaticText(tabSeven, label='Adjust trimpot P5 to output voltage 2.99V', pos=(160, 140))
        self.textAdjustHydA1b.SetFont(instructionFont)
        self.textAdjustHydA2b.SetFont(instructionFont)
        self.textAdjustHydA3b.SetFont(instructionFont)
        self.textAdjustHydA1b.SetForegroundColour('#0000ff')
        self.textAdjustHydA2b.SetForegroundColour('#0000ff')
        self.textAdjustHydA3b.SetForegroundColour('#0000ff')
        self.textAdjustHydA1b.Hide()
        self.textAdjustHydA2b.Hide()
        self.textAdjustHydA3b.Hide()

        self.adjustHydA1done = wx.CheckBox(tabSeven, label=' Adjustment Hyd A rotor coil done.', pos=(160, 180), size=(240, 25))
        self.adjustHydA1done.SetValue(False)
        self.adjustHydA1done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustHydA1done.Bind(wx.EVT_CHECKBOX, self.adjustHydAS1checkbox)
        self.adjustHydA2done = wx.CheckBox(tabSeven, label=' Adjustment Hyd A stator coil S1 done.', pos=(160, 200), size=(240, 25))
        self.adjustHydA2done.SetValue(False)
        self.adjustHydA2done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustHydA2done.Bind(wx.EVT_CHECKBOX, self.adjustHydAS2checkbox)
        self.adjustHydA3done = wx.CheckBox(tabSeven, label=' Adjustment Hyd A stator coil S3 done.', pos=(160, 220), size=(240, 25))
        self.adjustHydA3done.SetValue(False)
        self.adjustHydA3done.SetToolTip(wx.ToolTip("after adjustment, tick box to finish adjustment"))
        self.adjustHydA3done.Bind(wx.EVT_CHECKBOX, self.adjustHydAS3checkbox)
        self.adjustHydA1done.Hide()
        self.adjustHydA2done.Hide()
        self.adjustHydA3done.Hide()

        # Text output for the HYD B tests
        self.buttonAdjustHydB = wx.Button(tabSeven, label="Activate Hyd B stator coil outputs", pos=(150, 70), size=(245, 25))
        self.buttonAdjustHydB.SetToolTip(wx.ToolTip("Start adjustment: set Hyd B stator coils to max amplitude"))
        self.buttonAdjustHydB.SetBackgroundColour('#99ccff')
        self.buttonAdjustHydB.SetForegroundColour('#000000')
        self.buttonAdjustHydB.Bind(wx.EVT_BUTTON, self.adjustHydBOutput)
        self.buttonAdjustHydB.Hide()
        self.buttonAdjustHydBState = 0

        self.textAdjustHydB1a = wx.StaticText(tabSeven, label='Measure AC voltage on HYD-PRS-B pin  [ RT ]', pos=(160, 120))
        self.textAdjustHydB2a = wx.StaticText(tabSeven, label='Measure AC voltage on HYD-PRS-B pin  [ S1 ]', pos=(160, 120))
        self.textAdjustHydB3a = wx.StaticText(tabSeven, label='Measure AC voltage on HYD-PRS-B pin  [ S3 ]', pos=(160, 120))
        self.textAdjustHydB1a.SetFont(instructionFont)
        self.textAdjustHydB2a.SetFont(instructionFont)
        self.textAdjustHydB3a.SetFont(instructionFont)
        self.textAdjustHydB1a.SetForegroundColour('#0000ff')
        self.textAdjustHydB2a.SetForegroundColour('#0000ff')
        self.textAdjustHydB3a.SetForegroundColour('#0000ff')
        self.textAdjustHydB1a.Hide()
        self.textAdjustHydB2a.Hide()
        self.textAdjustHydB3a.Hide()
        self.textAdjustHydB1b = wx.StaticText(tabSeven, label='Adjust trimpot P3 to output voltage 6.60V', pos=(160, 140))
        self.textAdjustHydB2b = wx.StaticText(tabSeven, label='Adjust trimpot P7 to output voltage 2.99V', pos=(160, 140))
        self.textAdjustHydB3b = wx.StaticText(tabSeven, label='Adjust trimpot P6 to output voltage 2.99V', pos=(160, 140))
        self.textAdjustHydB1b.SetFont(instructionFont)
        self.textAdjustHydB2b.SetFont(instructionFont)
        self.textAdjustHydB3b.SetFont(instructionFont)
        self.textAdjustHydB1b.SetForegroundColour('#0000ff')
        self.textAdjustHydB2b.SetForegroundColour('#0000ff')
        self.textAdjustHydB3b.SetForegroundColour('#0000ff')
        self.textAdjustHydB1b.Hide()
        self.textAdjustHydB2b.Hide()
        self.textAdjustHydB3b.Hide()

        self.adjustHydB1done = wx.CheckBox(tabSeven, label=' Adjustment Hyd B rotor coil done.', pos=(160, 180), size=(240, 25))
        self.adjustHydB1done.SetValue(False)
        self.adjustHydB1done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustHydB1done.Bind(wx.EVT_CHECKBOX, self.adjustHydBS1checkbox)
        self.adjustHydB2done = wx.CheckBox(tabSeven, label=' Adjustment Hyd B stator coil S1 done.', pos=(160, 200), size=(240, 25))
        self.adjustHydB2done.SetValue(False)
        self.adjustHydB2done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustHydB2done.Bind(wx.EVT_CHECKBOX, self.adjustHydBS2checkbox)
        self.adjustHydB3done = wx.CheckBox(tabSeven, label=' Adjustment Hyd B stator coil S3 done.', pos=(160, 220), size=(240, 25))
        self.adjustHydB3done.SetValue(False)
        self.adjustHydB3done.SetToolTip(wx.ToolTip("after adjustment, tick box to finish adjustment"))
        self.adjustHydB3done.Bind(wx.EVT_CHECKBOX, self.adjustHydBS3checkbox)
        self.adjustHydB1done.Hide()
        self.adjustHydB2done.Hide()
        self.adjustHydB3done.Hide()

        # Text output for the signal symmetry adjustment
        self.textAdjustSymm1 = wx.StaticText(tabSeven, label='Measure AC voltage on TestPin 1  [ TP1 ]', pos=(160, 120))
        self.textAdjustSymm2 = wx.StaticText(tabSeven, label='Measure AC voltage on TestPin 2  [ TP2 ]', pos=(160, 140))
        self.textAdjustSymm1.SetFont(instructionFont)
        self.textAdjustSymm2.SetFont(instructionFont)
        self.textAdjustSymm1.SetForegroundColour('#0000ff')
        self.textAdjustSymm2.SetForegroundColour('#0000ff')
        #self.textAdjustSymm1.Hide()
        #self.textAdjustSymm2.Hide()
        self.textAdjustSymmb = wx.StaticText(tabSeven,\
             label='Adjust trimpot [ SYM ]\n            so that TP2 equals TP1 voltage', pos=(160, 180))
        self.textAdjustSymmb.SetFont(instructionFont)
        self.textAdjustSymmb.SetForegroundColour('#0000ff')
        #self.textAdjustSymmb.Hide()

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)


# -------------------------------------------------------------------------------------------------------

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        # print('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        # if leaving the "Adjustment" tab : disable Sin/Cos Alignment
        if old == 5:
            if self.adjustObjectBox.GetStringSelection() == "Hyd A":
                self.adjustObject = 0
                if self.buttonAdjustHydAState == 1:
                    # adjustment HYD A is active: abort it
                    self.buttonAdjustHydAState = 0
                    self.buttonAdjustHydA.SetLabel("Activate Hyd A stator coil outputs")
                    self.buttonAdjustHydA.SetBackgroundColour('#99ccff')  # blue-ish
                    self.buttonAdjustHydA.SetForegroundColour('#000000')
                    self.buttonAdjustHydA.SetToolTip(wx.ToolTip("Start adjustment: set Hyd A stator coils to max amplitude"))
                    self.adjustHydA1done.SetValue(False)
                    self.adjustHydA2done.SetValue(False)
                    self.adjustHydA3done.SetValue(False)
                    self.textAdjustHydA1a.Hide()
                    self.textAdjustHydA1b.Hide()
                    self.textAdjustHydA2a.Hide()
                    self.textAdjustHydA2b.Hide()
                    self.textAdjustHydA3a.Hide()
                    self.textAdjustHydA3b.Hide()
                    self.adjustHydA1done.Hide()
                    self.adjustHydA2done.Hide()
                    self.adjustHydA3done.Hide()
                    self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AX, 0)
                    self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AY, 0)
                    self.sendData(self.HYDdeviceAddress, self.CMD_HYDA_POL, 0)
                    print("[i] hyd A adjustment terminated")
            elif self.adjustObjectBox.GetStringSelection() == "Hyd B":
                self.adjustObject = 1
                if self.buttonAdjustHydBState == 1:
                    # adjustment HYD B is active: abort it
                    self.buttonAdjustHydBState = 0
                    self.buttonAdjustHydB.SetLabel("Activate Hyd B stator coil outputs")
                    self.buttonAdjustHydB.SetBackgroundColour('#99ccff')  # blue-ish
                    self.buttonAdjustHydB.SetForegroundColour('#000000')
                    self.buttonAdjustHydB.SetToolTip(wx.ToolTip("Start adjustment: set Hyd B stator coils to max amplitude"))
                    self.adjustHydB1done.SetValue(False)
                    self.adjustHydB2done.SetValue(False)
                    self.adjustHydB3done.SetValue(False)
                    self.textAdjustHydB1a.Hide()
                    self.textAdjustHydB1b.Hide()
                    self.textAdjustHydB2a.Hide()
                    self.textAdjustHydB2b.Hide()
                    self.textAdjustHydB3a.Hide()
                    self.textAdjustHydB3b.Hide()
                    self.adjustHydB1done.Hide()
                    self.adjustHydB2done.Hide()
                    self.adjustHydB3done.Hide()
                    self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BX, 0)
                    self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BY, 0)
                    self.sendData(self.HYDdeviceAddress, self.CMD_HYDB_POL, 0)
                    print("[i] hyd B adjustment terminated")
            else: # self.adjustObjectBox.GetStringSelection() == "Symmetry":
                self.adjustObject = 2
                self.adjustHydAHideItems()
                self.adjustHydBHideItems()
                self.buttonAdjustHydA.Hide()
                self.buttonAdjustHydB.Hide()
                self.textAdjustSymm1.Show()
                self.textAdjustSymm2.Show()
                self.textAdjustSymmb.Show()
            #print('>   Synchro stator adjustment de-activated\n')
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        print('OnPageChanging:,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()

# =================================================================================================

    def onConnectionBox(self, e): 
        if self.rbox.GetStringSelection() == "PHCC":
            self.channelSelection = "PHCC"
            print("[i] Connection =", self.channelSelection)
        else:
            self.channelSelection = "USB"
            print("[i] Connection =", self.channelSelection)


    def enaTXdataPrintCheckbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.printTxData = True
            print("[i] printing transmitted data enabled")
        else:
            self.printTxData = False
            print("[i] printing transmitted data disabled")


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
            elif (self.buttonCommOpen.GetLabel() == "Close COM port"):
                self.closeCOMMport(self.commPortID)
                self.buttonCommOpen.SetLabel("Open COM port")
                self.textStatusOpened.Hide()
                self.textStatusClosed.Show()


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


    def onCloseMessageReceived(self, text):
        self.closeCOMMport(self.commPortID)


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
        self.sendData(self.HYDdeviceAddress, self.CMD_DIAGMODE, self.DiagLEDdatabyte)
        print("[i] Diagnostic LED function changed")
        if (self.commPortOpened == True):
            # update "Set" button color only to grey if data was actually sent!
            self.buttonDiagLED.SetBackgroundColour('#cccccc')


    def toggleOutputXA1Checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.sendData(self.HYDdeviceAddress, self.CMD_XA1, 1)
            print("[i] user output XA1 activated")
        else:
            self.sendData(self.HYDdeviceAddress, self.CMD_XA1, 0)
            print("[i] user output XA1 de-activated")


    def toggleOutputXA5Checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.sendData(self.HYDdeviceAddress, self.CMD_XA5, 1)
            print("[i] user output XA5 activated")
        else:
            self.sendData(self.HYDdeviceAddress, self.CMD_XA5, 0)
            print("[i] user output XA5 de-activated")


    def toggleOutputXB7Checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.sendData(self.HYDdeviceAddress, self.CMD_XB7, 1)
            print("[i] user output XB7 activated")
        else:
            self.sendData(self.HYDdeviceAddress, self.CMD_XB7, 0)
            print("[i] user output XB7 de-activated")


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

    def setHydAOffsetDefault(self, event):
        self.HydAOffsetS1Entry.SetValue(self.defaultHydAS1offset)
        self.HydAOffsetS2Entry.SetValue(self.defaultHydAS2offset)
        # default values are "always" correct ==> no error flags up, "set" button OK!
        self.buttonHydAOffsetSet.SetBackgroundColour('#99ccff')

    def HydAentrySet(self, event):
        HydAvalue = self.HydAentry.GetValue()
        value = self.str2int(HydAvalue)
        if value > 1024:
            self.HydAsettingValid = False
            self.HydAEntryErrorShown = True
            self.errorHydAentry.Show()
        else:
            self.HydAsetting = value
            self.HydAsettingValid = True
            self.HydAEntryErrorShown = False
            self.errorHydAentry.Hide()
            # create correct command subaddress and data
            if value == 1024:
                value = 0
            command = int(value / 256)
            data = value - (command * 256)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AQ1 + command, data)
            print("[i] hydA setpoint updated")

    def HydAincrement(self, e):
        self.HydAsetting = self.HydAsetting + 10
        if self.HydAsetting >= 1024:
            self.HydAsetting = self.HydAsetting - 1024
        self.HydAEntryErrorShown = False
        self.errorHydAentry.Hide()
        self.HydAentry.SetValue(str(self.HydAsetting))
        # send to HydA
        value = self.HydAsetting
        if value == 1024:
            value = 0
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AQ1 + command, data)
        print("[i] hydA setpoint updated")


    def HydAdecrement(self, e):
        if self.HydAsetting >= 10:
            self.HydAsetting = self.HydAsetting - 10
        else:
            diff = 10 - self.HydAsetting
            self.HydAsetting = 1024 - diff
        self.HydAEntryErrorShown = False
        self.errorHydAentry.Hide()
        self.HydAentry.SetValue(str(self.HydAsetting))
        # send to HydA
        value = self.HydAsetting
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AQ1 + command, data)
        print("[i] hydA setpoint updated")


    def sendHydAOffsets(self, e):
        offset1 = self.HydAOffsetS1Entry.GetValue()
        offset2 = self.HydAOffsetS2Entry.GetValue()
        self.HydAS1offset = offset1
        self.HydAS2offset = offset2
        # validate data
        allDataValid = True
        s1Offset = self.str2int(offset1)
        s2Offset = self.str2int(offset2)
        max = self.maxHydAOffset
        if (s1Offset > max) or (offset1 == ""):
            allDataValid = False
        if (s2Offset > max) or (offset2 == ""):
            allDataValid = False
        if allDataValid == True:
            self.buttonHydAOffsetSet.SetBackgroundColour('#99ccff')
            # send data: LSB first, then MSB offset
            msb = int(s1Offset / 256)
            lsb = s1Offset - (msb * 256)
            self.sendData(self.HYDdeviceAddress, self.CMD_LD_OFFS_L, lsb)
            self.sendData(self.HYDdeviceAddress, self.CMD_LD_OFFS_H, msb)
            self.sendData(self.HYDdeviceAddress, self.CMD_LOAD_HYD, 1)
            msb = int(s2Offset / 256)
            lsb = s2Offset - (msb * 256)
            self.sendData(self.HYDdeviceAddress, self.CMD_LD_OFFS_L, lsb)
            self.sendData(self.HYDdeviceAddress, self.CMD_LD_OFFS_H, msb)
            self.sendData(self.HYDdeviceAddress, self.CMD_LOAD_HYD, 2)
            print("[i] hydA offsets updated")
        else:
            self.buttonHydAOffsetSet.SetBackgroundColour('#e05040')

# =================================================================================================

    def setHydBOffsetDefault(self, event):
        self.HydBOffsetS1Entry.SetValue(self.defaultHydBS1offset)
        self.HydBOffsetS2Entry.SetValue(self.defaultHydBS2offset)
        # default values are "always" correct ==> no error flags up, "set" button OK!
        self.buttonHydBOffsetSet.SetBackgroundColour('#99ccff')

    def HydBentrySet(self, event):
        HydBvalue = self.HydBentry.GetValue()
        value = self.str2int(HydBvalue)
        if value > 1024:
            self.HydBsettingValid = False
            self.HydBEntryErrorShown = True
            self.errorHydBentry.Show()
        else:
            self.HydBsetting = value
            self.HydBsettingValid = True
            self.HydBEntryErrorShown = False
            self.errorHydBentry.Hide()
            # create correct command subaddress and data
            if value == 1024:
                value = 0
            command = int(value / 256)
            data = value - (command * 256)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BQ1 + command, data)
            print("[i] hydB setpoint updated")


    def HydBincrement(self, e):
        self.HydBsetting = self.HydBsetting + 10
        if self.HydBsetting >= 1024:
            self.HydBsetting = self.HydBsetting - 1024
        self.HydBEntryErrorShown = False
        self.errorHydBentry.Hide()
        self.HydBentry.SetValue(str(self.HydBsetting))
        # send to HydB
        value = self.HydBsetting
        if value == 1024:
            value = 0
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BQ1 + command, data)
        print("[i] hydB setpoint updated")


    def HydBdecrement(self, e):
        if self.HydBsetting >= 10:
            self.HydBsetting = self.HydBsetting - 10
        else:
            diff = 10 - self.HydBsetting
            self.HydBsetting = 1024 - diff
        self.HydBEntryErrorShown = False
        self.errorHydBentry.Hide()
        self.HydBentry.SetValue(str(self.HydBsetting))
        # send to HydB
        value = self.HydBsetting
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BQ1 + command, data)
        print("[i] hydB setpoint updated")


    def sendHydBOffsets(self, e):
        offset1 = self.HydBOffsetS1Entry.GetValue()
        offset2 = self.HydBOffsetS2Entry.GetValue()
        self.HydBS1offset = offset1
        self.HydBS2offset = offset2
        # validate data
        allDataValid = True
        max = self.maxHydBOffset
        s1Offset = self.str2int(offset1)
        s2Offset = self.str2int(offset2)
        if (s1Offset > max) or (offset1 == ""):
            allDataValid = False
        if (s2Offset > max) or (offset2 == ""):
            allDataValid = False
        if allDataValid == True:
            self.buttonHydBOffsetSet.SetBackgroundColour('#99ccff')
            # send data: LSB first, then MSB offset
            msb = int(s1Offset / 256)
            lsb = s1Offset - (msb * 256)
            self.sendData(self.HYDdeviceAddress, self.CMD_LD_OFFS_L, lsb)
            self.sendData(self.HYDdeviceAddress, self.CMD_LD_OFFS_H, msb)
            self.sendData(self.HYDdeviceAddress, self.CMD_LOAD_HYD, 4)
            msb = int(s2Offset / 256)
            lsb = s2Offset - (msb * 256)
            self.sendData(self.HYDdeviceAddress, self.CMD_LD_OFFS_L, lsb)
            self.sendData(self.HYDdeviceAddress, self.CMD_LD_OFFS_H, msb)
            self.sendData(self.HYDdeviceAddress, self.CMD_LOAD_HYD, 8)
            print("[i] hydB offsets updated")
        else:
            self.buttonHydBOffsetSet.SetBackgroundColour('#e05040')

# =================================================================================================

    def onSimulateObject(self, e):
        if self.simulateObjectBox.GetStringSelection() == "Hyd A":
            if (self.simulateStatus == 1) or (self.simulateStatus == 3) :
                # Hyd A simulation active
                self.buttonsimulateStartEntrySet.SetBackgroundColour('#eeeeee')
                self.simulateStartButton.SetBackgroundColour('#eeeeee')
                self.simulateStopButton.SetBackgroundColour('#99ccff')
            else:
                # Hyd A simulation not active
                self.buttonsimulateStartEntrySet.SetBackgroundColour('#99ccff')
                self.simulateStartButton.SetBackgroundColour('#99ccff')
                self.simulateStopButton.SetBackgroundColour('#eeeeee')
            self.simulateObject = 0
            self.cbSimulateStepSelection.SetValue(self.simulateStepList[self.simulateAStepIndex])
            self.simulateStartEntry.SetValue(str(self.simHydAStartValue))
            if self.simHydAStartValue > 1023:
                self.errorsimulateStartEntry.Show()
                self.textSimulateShowSetpoint.SetValue("0")
            else:
                self.errorsimulateStartEntry.Hide()
                self.textSimulateShowSetpoint.SetValue(str(self.simulateARunningValue))
        else:
            # self.simulateObjectBox.GetStringSelection() == "Hyd B":
            if (self.simulateStatus == 2) or (self.simulateStatus == 3) :
                # Hyd B simulation active
                self.buttonsimulateStartEntrySet.SetBackgroundColour('#eeeeee')
                self.simulateStartButton.SetBackgroundColour('#eeeeee')
                self.simulateStopButton.SetBackgroundColour('#99ccff')
            else:
                # Hyd B simulation not active
                self.buttonsimulateStartEntrySet.SetBackgroundColour('#99ccff')
                self.simulateStartButton.SetBackgroundColour('#99ccff')
                self.simulateStopButton.SetBackgroundColour('#eeeeee')
            self.simulateObject = 1
            self.cbSimulateStepSelection.SetValue(self.simulateStepList[self.simulateBStepIndex])
            self.simulateStartEntry.SetValue(str(self.simHydBStartValue))
            if self.simHydBStartValue > 1023:
                self.errorsimulateStartEntry.Show()
                self.textSimulateShowSetpoint.SetValue("0")
            else:
                self.errorsimulateStartEntry.Hide()
                self.textSimulateShowSetpoint.SetValue(str(self.simulateBRunningValue))


    def simulateStartEntrySet(self, e):
        # start setpoint value only accepted when simulation is not running
        if self.simulateObject == 0:
            # Hyd A radio button selected
            if (self.simulateStatus != 1) and (self.simulateStatus != 3) :
                # HydA is not "running" : can accept new sepoint value
                value = self.str2int(self.simulateStartEntry.GetValue())
                if value > 1024:
                    self.errorsimulateStartEntry.Show()
                else:
                    self.errorsimulateStartEntry.Hide()
                    self.textSimulateShowSetpoint.SetValue(str(value))
                    self.simulateAFirstStart = True
                    # self.simulateStartButton.SetBackgroundColour('#99ccff')
                    # set hydA start value
                    self.simHydAStartValue = value
                    if value == 1024:
                        value = 0
                    command = int(value / 256)
                    data = value - (command * 256)
                    self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AQ1 + command, data)
                    print("SIM hyd A start set")
        else:  # self.simulateObject == 1:
            # Hyd B radio button selected
            if (self.simulateStatus != 2) and (self.simulateStatus != 3) :
                # HydB is not "running" : can accept new sepoint value
                value = self.str2int(self.simulateStartEntry.GetValue())
                if value > 1024:
                    self.errorsimulateStartEntry.Show()
                else:
                    self.errorsimulateStartEntry.Hide()
                    self.textSimulateShowSetpoint.SetValue(str(value))
                    self.simulateBFirstStart = True
                    # self.simulateStartButton.SetBackgroundColour('#99ccff')
                    # set hydB start value
                    self.simHydBStartValue = value
                    if value == 1024:
                        value = 0
                    command = int(value / 256)
                    data = value - (command * 256)
                    self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BQ1 + command, data)
                    print("SIM hyd B start set")


    def simulateStartSimulation(self, e):
        if self.simulateObject == 0:
            # start HydA
            if self.simulateAFirstStart == True:
                value = self.simHydAStartValue        # load start value
            else:
                value = self.simulateARunningValue    # load resume value
            if value < 1024:
                self.simulateAFirstStart = False
                self.buttonsimulateStartEntrySet.SetBackgroundColour('#eeeeee')
                self.simulateStartButton.SetBackgroundColour('#eeeeee')
                self.simulateStopButton.SetBackgroundColour('#99ccff')
                self.simulateARunningValue = value
                self.textSimulateShowSetpoint.SetValue(str(self.simulateARunningValue))
                self.simulateStatus = self.simulateStatus | 0x01
                print("simulation HydA started")
                self.startTimer(self.simulateUpdateTime)
        else:
            # start HydB
            if self.simulateBFirstStart == True:
                value = self.simHydBStartValue        # load start value
            else:
                value = self.simulateBRunningValue    # load resume value
            if value < 1024:
                self.simulateBFirstStart = False
                self.buttonsimulateStartEntrySet.SetBackgroundColour('#eeeeee')
                self.simulateStartButton.SetBackgroundColour('#eeeeee')
                self.simulateStopButton.SetBackgroundColour('#99ccff')
                self.simulateBRunningValue = value
                self.textSimulateShowSetpoint.SetValue(str(self.simulateBRunningValue))
                self.simulateStatus = self.simulateStatus | 0x02
                print("simulation HydB started")
                self.startTimer(self.simulateUpdateTime)


    def simulateStopSimulation(self, e):
        if self.simulateObject == 0:
            # stop HydA if HydA is "running"
            if self.simulateStatus == 1 or self.simulateStatus == 3:
                self.buttonsimulateStartEntrySet.SetBackgroundColour('#99ccff')
                self.simulateStartButton.SetBackgroundColour('#99ccff')
                self.simulateStopButton.SetBackgroundColour('#eeeeee')
                self.simulateStatus = self.simulateStatus & 0xFE
                print("simulation HydA stopped")
        else: # self.simulateObject == 1:
            # stop HydB if HydB is "running"
            if self.simulateStatus == 2 or self.simulateStatus == 3:
                self.buttonsimulateStartEntrySet.SetBackgroundColour('#99ccff')
                self.simulateStartButton.SetBackgroundColour('#99ccff')
                self.simulateStopButton.SetBackgroundColour('#eeeeee')
                self.simulateStatus = self.simulateStatus & 0xFD
                print("simulation HydB stopped")


    def OnSelectSimStepSize(self, entry):
        selection = entry.GetSelection()
        if self.simulateObject == 0:
            # set HydA steprate
            self.simulateAStepIndex = selection
            if selection == 0:
                self.simulateAStepValue = 1
            elif selection == 1:
                self.simulateAStepValue = 2
            elif selection == 2:
                self.simulateAStepValue = 5
            elif selection == 3:
                self.simulateAStepValue = 10
            else:
                self.simulateAStepValue = 20
        else:  # self.simulateObject == 1:
            # set HydB steprate
            self.simulateBStepIndex = selection
            if selection == 0:
                self.simulateBStepValue = 1
            elif selection == 1:
                self.simulateBStepValue = 2
            elif selection == 2:
                self.simulateBStepValue = 5
            elif selection == 3:
                self.simulateBStepValue = 10
            else:
                self.simulateBStepValue = 20


    def OnSelectSimUpdateRate(self, entry):
        self.simulateUpdateRateSelection = entry.GetSelection()
        if self.simulateUpdateRateSelection == 0:
            self.simulateUpdateTime = 200
        elif self.simulateUpdateRateSelection == 1:
            self.simulateUpdateTime = 400
        elif self.simulateUpdateRateSelection == 2:
            self.simulateUpdateTime = 600
        elif self.simulateUpdateRateSelection == 3:
            self.simulateUpdateTime = 800
        else:
            self.simulateUpdateTime = 1000


# =================================================================================================

    def advancedSend(self, event):
        advDeviceAddress = self.deviceAddressEntry.GetValue()
        advDeviceSubAddress = self.deviceSubAddressEntry.GetValue()
        advData = self.deviceDataEntry.GetValue()
        allDataValid = True
        # process entry fields
        addressValue = 89
        if self.validateDOAdata == True:
            if advDeviceAddress == "0x59" or advDeviceAddress == "0X59" or advDeviceAddress == "89" :
                portID = "HYD-A/B"
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
            if (subValue > 24) or (advDeviceSubAddress == ""):
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
            print("[i] raw data command sent")
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
            print("[i] raw data 'Allow all' selected")
        else:
            self.validateDOAdata = True
            print("[i] raw data 'Allow all' deselected")


# =================================================================================================

    def adjustHideSymmItems(self):
        self.textAdjustSymm1.Hide()
        self.textAdjustSymm2.Hide()
        self.textAdjustSymmb.Hide()


    def adjustHydAHideItems(self):
        # hide HydA adjustment procedure and de-activate start button
        self.buttonAdjustHydA.Hide()
        self.buttonAdjustHydA.SetLabel("Activate Hyd A stator coil outputs")
        self.buttonAdjustHydA.SetBackgroundColour('#99ccff')  # blue-ish
        self.buttonAdjustHydA.SetForegroundColour('#000000')
        self.buttonAdjustHydA.SetToolTip(wx.ToolTip("Start adjustment: set Hyd A stator coils to max amplitude"))
        self.adjustHydA1done.SetValue(False)
        self.adjustHydA2done.SetValue(False)
        self.adjustHydA3done.SetValue(False)
        self.textAdjustHydA1a.Hide()
        self.textAdjustHydA1b.Hide()
        self.textAdjustHydA2a.Hide()
        self.textAdjustHydA2b.Hide()
        self.textAdjustHydA3a.Hide()
        self.textAdjustHydA3b.Hide()
        self.adjustHydA1done.Hide()
        self.adjustHydA2done.Hide()
        self.adjustHydA3done.Hide()
        if self.buttonAdjustHydAState == 1:
            self.buttonAdjustHydAState = 0
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AX, 0)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AY, 0)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYDA_POL, 0)
            print("[i] hyd A adjustment terminated")


    def adjustHydAOutput(self, event):
        if self.buttonAdjustHydAState == 0:
            self.buttonAdjustHydAState = 1
            self.buttonAdjustHydA.SetLabel("De-activate Hyd A stator coil outputs")
            self.buttonAdjustHydA.SetBackgroundColour('#F48C42')  # red-ish
            self.buttonAdjustHydA.SetForegroundColour('#ffffff')
            self.buttonAdjustHydA.SetToolTip(wx.ToolTip("Stop adjustment: set Hyd A stator coils to zero"))
            # start measurement procedure
            self.textAdjustHydA1a.Show()
            self.textAdjustHydA1b.Show()
            self.adjustHydA1done.Show()
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AX, 255)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AY, 255)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYDA_POL, 0)
            print("[i] hyd A adjustment started")
        else:
            self.buttonAdjustHydAState = 0
            self.buttonAdjustHydA.SetLabel("Activate Hyd A stator coil outputs")
            self.buttonAdjustHydA.SetBackgroundColour('#99ccff')  # blue-ish
            self.buttonAdjustHydA.SetForegroundColour('#000000')
            self.buttonAdjustHydA.SetToolTip(wx.ToolTip("Start adjustment: set Hyd A stator coils to max amplitude"))
            self.adjustHydA1done.SetValue(False)
            self.adjustHydA2done.SetValue(False)
            self.adjustHydA3done.SetValue(False)
            self.textAdjustHydA1a.Hide()
            self.textAdjustHydA1b.Hide()
            self.textAdjustHydA2a.Hide()
            self.textAdjustHydA2b.Hide()
            self.textAdjustHydA3a.Hide()
            self.textAdjustHydA3b.Hide()
            self.adjustHydA1done.Hide()
            self.adjustHydA2done.Hide()
            self.adjustHydA3done.Hide()
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AX, 0)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AY, 0)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYDA_POL, 0)
            print("[i] hyd A adjustment terminated")


    def adjustHydAS1checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S2
            self.textAdjustHydA1a.Hide()
            self.textAdjustHydA1b.Hide()
            self.textAdjustHydA3a.Hide()
            self.textAdjustHydA3b.Hide()
            self.textAdjustHydA2a.Show()
            self.textAdjustHydA2b.Show()
            self.adjustHydA2done.SetValue(False)
            self.adjustHydA2done.Show()
        else:
            # back to check coil S1 (hide check S2 and S3)
            self.textAdjustHydA2a.Hide()
            self.textAdjustHydA2b.Hide()
            self.textAdjustHydA3a.Hide()
            self.textAdjustHydA3b.Hide()
            self.textAdjustHydA1a.Show()
            self.textAdjustHydA1b.Show()
            self.adjustHydA2done.SetValue(False)
            self.adjustHydA2done.Hide()
            self.adjustHydA3done.SetValue(False)
            self.adjustHydA3done.Hide()


    def adjustHydAS2checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S3
            self.textAdjustHydA1a.Hide()
            self.textAdjustHydA1b.Hide()
            self.textAdjustHydA2a.Hide()
            self.textAdjustHydA2b.Hide()
            self.textAdjustHydA3a.Show()
            self.textAdjustHydA3b.Show()
            self.adjustHydA3done.SetValue(False)
            self.adjustHydA3done.Show()
        else:
            # back to check coil S2 (hide check S3)
            self.textAdjustHydA1a.Hide()
            self.textAdjustHydA1b.Hide()
            self.textAdjustHydA3a.Hide()
            self.textAdjustHydA3b.Hide()
            self.textAdjustHydA2a.Show()
            self.textAdjustHydA2b.Show()
            self.adjustHydA2done.SetValue(False)
            self.adjustHydA2done.Show()
            self.adjustHydA3done.SetValue(False)
            self.adjustHydA3done.Hide()


    def adjustHydAS3checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # check done!
            self.textAdjustHydA1a.Hide()
            self.textAdjustHydA1b.Hide()
            self.textAdjustHydA2a.Hide()
            self.textAdjustHydA2b.Hide()
            self.textAdjustHydA3a.Hide()
            self.textAdjustHydA3b.Hide()
        else:
            # back to check coil S3
            self.textAdjustHydA1a.Hide()
            self.textAdjustHydA1b.Hide()
            self.textAdjustHydA2a.Hide()
            self.textAdjustHydA2b.Hide()
            self.textAdjustHydA3a.Show()
            self.textAdjustHydA3b.Show()
            self.adjustHydA3done.SetValue(False)


    def adjustHydBHideItems(self):
        # hide HydB adjustment procedure and de-activate start button
        self.buttonAdjustHydB.Hide()
        self.buttonAdjustHydB.SetLabel("Activate Hyd B stator coil outputs")
        self.buttonAdjustHydB.SetBackgroundColour('#99ccff')  # blue-ish
        self.buttonAdjustHydB.SetForegroundColour('#000000')
        self.buttonAdjustHydB.SetToolTip(wx.ToolTip("Start adjustment: set Hyd B stator coils to max amplitude"))
        self.adjustHydB1done.SetValue(False)
        self.adjustHydB2done.SetValue(False)
        self.adjustHydB3done.SetValue(False)
        self.textAdjustHydB1a.Hide()
        self.textAdjustHydB1b.Hide()
        self.textAdjustHydB2a.Hide()
        self.textAdjustHydB2b.Hide()
        self.textAdjustHydB3a.Hide()
        self.textAdjustHydB3b.Hide()
        self.adjustHydB1done.Hide()
        self.adjustHydB2done.Hide()
        self.adjustHydB3done.Hide()
        if self.buttonAdjustHydBState == 1:
            self.buttonAdjustHydBState = 0
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BX, 0)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BY, 0)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYDB_POL, 0)
            print("[i] hyd B adjustment terminated")


    def adjustHydBOutput(self, event):
        if self.buttonAdjustHydBState == 0:
            self.buttonAdjustHydBState = 1
            self.buttonAdjustHydB.SetLabel("De-activate Hyd B stator coil outputs")
            self.buttonAdjustHydB.SetBackgroundColour('#F48C42')  # red-ish
            self.buttonAdjustHydB.SetForegroundColour('#ffffff')
            self.buttonAdjustHydB.SetToolTip(wx.ToolTip("Stop adjustment: set Hyd B stator coils to zero"))
            # start measurement procedure
            self.textAdjustHydB1a.Show()
            self.textAdjustHydB1b.Show()
            self.adjustHydB1done.Show()
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BX, 255)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BY, 255)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYDB_POL, 0)
            print("[i] hyd B adjustment started")
        else:
            self.buttonAdjustHydBState = 0
            self.buttonAdjustHydB.SetLabel("Activate Hyd B stator coil outputs")
            self.buttonAdjustHydB.SetBackgroundColour('#99ccff')  # blue-ish
            self.buttonAdjustHydB.SetForegroundColour('#000000')
            self.buttonAdjustHydB.SetToolTip(wx.ToolTip("Start adjustment: set Hyd B stator coils to max amplitude"))
            self.adjustHydB1done.SetValue(False)
            self.adjustHydB2done.SetValue(False)
            self.adjustHydB3done.SetValue(False)
            self.textAdjustHydB1a.Hide()
            self.textAdjustHydB1b.Hide()
            self.textAdjustHydB2a.Hide()
            self.textAdjustHydB2b.Hide()
            self.textAdjustHydB3a.Hide()
            self.textAdjustHydB3b.Hide()
            self.adjustHydB1done.Hide()
            self.adjustHydB2done.Hide()
            self.adjustHydB3done.Hide()
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BX, 0)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BY, 0)
            self.sendData(self.HYDdeviceAddress, self.CMD_HYDB_POL, 0)
            print("[i] hyd B adjustment terminated")


    def adjustHydBS1checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S2
            self.textAdjustHydB1a.Hide()
            self.textAdjustHydB1b.Hide()
            self.textAdjustHydB3a.Hide()
            self.textAdjustHydB3b.Hide()
            self.textAdjustHydB2a.Show()
            self.textAdjustHydB2b.Show()
            self.adjustHydB2done.SetValue(False)
            self.adjustHydB2done.Show()
        else:
            # back to check coil S1 (hide check S2 and S3)
            self.textAdjustHydB2a.Hide()
            self.textAdjustHydB2b.Hide()
            self.textAdjustHydB3a.Hide()
            self.textAdjustHydB3b.Hide()
            self.textAdjustHydB1a.Show()
            self.textAdjustHydB1b.Show()
            self.adjustHydB2done.SetValue(False)
            self.adjustHydB2done.Hide()
            self.adjustHydB3done.SetValue(False)
            self.adjustHydB3done.Hide()


    def adjustHydBS2checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S3
            self.textAdjustHydB1a.Hide()
            self.textAdjustHydB1b.Hide()
            self.textAdjustHydB2a.Hide()
            self.textAdjustHydB2b.Hide()
            self.textAdjustHydB3a.Show()
            self.textAdjustHydB3b.Show()
            self.adjustHydB3done.SetValue(False)
            self.adjustHydB3done.Show()
        else:
            # back to check coil S2 (hide check S3)
            self.textAdjustHydB1a.Hide()
            self.textAdjustHydB1b.Hide()
            self.textAdjustHydB3a.Hide()
            self.textAdjustHydB3b.Hide()
            self.textAdjustHydB2a.Show()
            self.textAdjustHydB2b.Show()
            self.adjustHydB2done.SetValue(False)
            self.adjustHydB2done.Show()
            self.adjustHydB3done.SetValue(False)
            self.adjustHydB3done.Hide()


    def adjustHydBS3checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # check done!
            self.textAdjustHydB1a.Hide()
            self.textAdjustHydB1b.Hide()
            self.textAdjustHydB2a.Hide()
            self.textAdjustHydB2b.Hide()
            self.textAdjustHydB3a.Hide()
            self.textAdjustHydB3b.Hide()
        else:
            # back to check coil S3
            self.textAdjustHydB1a.Hide()
            self.textAdjustHydB1b.Hide()
            self.textAdjustHydB2a.Hide()
            self.textAdjustHydB2b.Hide()
            self.textAdjustHydB3a.Show()
            self.textAdjustHydB3b.Show()
            self.adjustHydB3done.SetValue(False)



    def onAdjustObject(self, e):
        if self.adjustObjectBox.GetStringSelection() == "Hyd A":
            self.adjustObject = 0
            self.adjustHydBHideItems()
            self.adjustHideSymmItems()
            self.buttonAdjustHydA.Show()
        elif self.adjustObjectBox.GetStringSelection() == "Hyd B":
            self.adjustObject = 1
            self.adjustHydAHideItems()
            self.adjustHideSymmItems()
            self.buttonAdjustHydB.Show()
        else: # self.adjustObjectBox.GetStringSelection() == "Symmetry":
            self.adjustObject = 2
            self.adjustHydAHideItems()
            self.adjustHydBHideItems()
            self.buttonAdjustHydA.Hide()
            self.buttonAdjustHydB.Hide()
            self.textAdjustSymm1.Show()
            self.textAdjustSymm2.Show()
            self.textAdjustSymmb.Show()


# =================================================================================================

    def ExitClick(self, event):
        # (leave current settings as they are)
        print("--- Exit HYD A/B board test tool.")
        self.closeCOMMport(self.commPortID)
        frame.Close()


# =================================================================================================
#  COMMUNICATION  routine: send data
# =================================================================================================

    def sendData(self, address, subAddress, data):
        if self.commPortOpened == True:
            if address == self.HYDdeviceAddress:
                if self.channelSelection == "PHCC":
                    # using PHCC Motherboard
                    if self.printTxData == True:
                        print("... sendData to", self.commPortID, \
                              "address", address, "subAddress", subAddress, "data", data)
                    phccId = 0x07
                    if self.ComPort.isOpen():
                        self.ComPort.write(phccId.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(address.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(subAddress.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                    else:
                        print("!!! COM port for HYD is not open!")
                elif self.channelSelection == "USB":
                    if self.ComPort.isOpen():
                        checksum  = (subAddress + data) & 0x00FF
                        delimiter = 0xFF
                        if self.printTxData == True:
                            print("... sendData to", self.commPortID, \
                                  "subAddress", subAddress, "data", data, \
                                  "checksum", checksum, "delimiter", delimiter)
                        self.ComPort.write(subAddress.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(checksum.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(delimiter.to_bytes(1, byteorder='big', signed=False))
                    else:
                        print("!!! COM port for HYD is not open!")
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
            #self.startTimer(300)
        # ----
        if self.HydAsettingValid == False:
            if self.HydAEntryErrorShown == True:
                self.HydAEntryErrorShown = False
                self.errorHydAentry.Hide()
                self.startTimer(300)
            else:
                self.HydAEntryErrorShown = True
                self.errorHydAentry.Show()
                self.startTimer(500)
        else:
            if self.HydAEntryErrorShown == True:
                self.HydAEntryErrorShown = False
                self.errorHydAentry.Hide()
            #self.startTimer(300)
        # ----
        if self.HydBsettingValid == False:
            if self.HydBEntryErrorShown == True:
                self.HydBEntryErrorShown = False
                self.errorHydBentry.Hide()
                self.startTimer(300)
            else:
                self.HydBEntryErrorShown = True
                self.errorHydBentry.Show()
                self.startTimer(500)
        else:
            if self.HydBEntryErrorShown == True:
                self.HydBEntryErrorShown = False
                self.errorHydBentry.Hide()
            #self.startTimer(300)
        # ----
        # ----
        if (self.simulateStatus != 0):
            # simulate setpoint update for each "running" indicator
            # but on screen update only for the selected indicator.
            if ((self.simulateStatus & 0x01) == 0x01):
                # HydA is "running"
                valueA = self.simulateARunningValue
                valueA = valueA + self.simulateAStepValue
                if valueA >= 1024:
                    valueA = valueA - 1024
                self.simulateARunningValue = valueA
                if self.simulateObject == 0:
                    self.textSimulateShowSetpoint.SetValue(str(self.simulateARunningValue))
                # send setpoint to simulated HYD A indicator
                command = int(valueA / 256)
                data = valueA - (command * 256)
                self.sendData(self.HYDdeviceAddress, self.CMD_HYD_AQ1 + command, data)
            #
            if ((self.simulateStatus & 0x02) == 0x02):
                # HydB is "running"
                valueB = self.simulateBRunningValue
                valueB = valueB + self.simulateBStepValue
                if valueB >= 1024:
                    valueB = valueB - 1024
                self.simulateBRunningValue = valueB
                if self.simulateObject == 1:
                    self.textSimulateShowSetpoint.SetValue(str(self.simulateBRunningValue))
                # send setpoint to simulated HYD B indicator
                command = int(valueB / 256)
                data = valueB - (command * 256)
                self.sendData(self.HYDdeviceAddress, self.CMD_HYD_BQ1 + command, data)
            #
            self.startTimer(self.simulateUpdateTime)



###################################################################################################
class HYDFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "HYD A/B demonstrator", size=(660,395))
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
    frame = HYDFrame()
    app.MainLoop()