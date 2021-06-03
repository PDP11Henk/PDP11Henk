
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
        self.HSIdevice1Address  = 0x48
        self.commPortID         = ""
        self.previousCommPort   = ""
        self.commPortIDtoClose  = ""
        self.commPortOpened     = False                   # flag COMM port opened
        self.commPortValid      = False                   # only for "error sign" blinking
        self.prevDiagLEDmode    = "heartbeat"
        self.validateDOAdata    = True

        self.smallFont = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.errorImage = wx.Bitmap("error.gif")

        self.Headingsetting           = 0                       # default "North"
        self.maxHeadingOffset         = 1023
        self.HeadingsettingValid      = True
        self.defaultHeadingS1offset   = "600"
        self.defaultHeadingS2offset   = "941"
        self.defaultHeadingS3offset   = "258"
        self.HeadingS1offset          = self.defaultHeadingS1offset
        self.HeadingS2offset          = self.defaultHeadingS2offset
        self.HeadingS3offset          = self.defaultHeadingS3offset
        self.HeadingEntryErrorShown   = False

        self.Bearingsetting           = 0                       # default "North"
        self.maxBearingOffset         = 1023
        self.BearingsettingValid      = True
        self.defaultBearingS1offset   = "89"
        self.defaultBearingS2offset   = "430"
        self.defaultBearingS3offset   = "771"
        self.BearingS1offset          = self.defaultBearingS1offset
        self.BearingS2offset          = self.defaultBearingS2offset
        self.BearingS3offset          = self.defaultBearingS3offset
        self.BearingEntryErrorShown   = False

        self.maxMilesOffset           = 1023
        self.defaultMiles100Xoffset   = "682"
        self.defaultMiles100Yoffset   = "853"
        self.defaultMiles10Xoffset    = "682"
        self.defaultMiles10Yoffset    = "853"
        self.defaultMiles1Xoffset     = "682"
        self.defaultMiles1Yoffset     = "853"
        self.Miles100Xoffset          = self.defaultMiles100Xoffset
        self.Miles100Yoffset          = self.defaultMiles100Yoffset
        self.Miles10Xoffset           = self.defaultMiles10Xoffset
        self.Miles10Yoffset           = self.defaultMiles10Yoffset
        self.Miles1Xoffset            = self.defaultMiles1Xoffset
        self.Miles1Yoffset            = self.defaultMiles1Yoffset
        self.rangeOffsetInError       = False
        self.synchroID                = "Miles 100"
        self.MilesLowPowerEnable      = True

        self.simHeadingStartValue     = 0
        self.simBearingStartValue     = 0
        self.simRangeStartValue       = 0
        self.simulateRunningValue     = 0
        self.simulateStatus           = 0
        self.simulateFirstStart       = True

        # HSI #1 interface commands (from hsi1-main.jal)
        self.CMD_BRG_Q1      = 0      # set BEARING indicator base
        self.CMD_HDG_Q1      = 4      # set HEADING indicator base
        self.CMD_MLS_1Q1     = 8      # set MILES units indicator base
        self.CMD_MLS_2Q1     = 12     # set MILES tens indicator base
        self.CMD_MLS_3Q1     = 16     # set MILES hundreds indicator base
        self.CMD_MILSHUTR    = 20     # (de)activate MILES indicator shutter flag
        self.CMD_USROUT_A    = 21     # set user-defined output A
        self.CMD_USROUT_B    = 22     # set user-defined output B
#
        self.CMD_LD_OFFS_L   = 23     # load offset value (lo 8 bits)  (1st cmd)
        self.CMD_LD_OFFS_H   = 24     # load offset value (hi 2 bits)  (2nd cmd)
        self.CMD_LOAD_BRG    = 25     # load BEARING offset value mask (3rd cmd)
        self.CMD_LOAD_HDG    = 26     # load HEADING offset value mask (3rd cmd)
        self.CMD_LOAD_RNG    = 27     # load RANGE   offset value mask (3rd cmd)
#
        self.CMD_BRG_S1       = 28    # set output value BEARING S1
        self.CMD_BRG_S2       = 29    # set output value BEARING S2
        self.CMD_BRG_S3       = 30    # set output value BEARING S3
        self.CMD_BRG_POL      = 31    # activate BEARING S1, S2, S3 polarity
        self.CMD_HDG_S1       = 32    # set output value HEADING S1
        self.CMD_HDG_S2       = 33    # set output value HEADING S2
        self.CMD_HDG_S3       = 34    # set output value HEADING S3
        self.CMD_HDG_POL      = 35    # activate HEADING S1, S2, S3 polarity
        self.CMD_MLS_1X       = 36    # set output value MILES UNITS X
        self.CMD_MLS_1Y       = 37    # set output value MILES UNITS Y
        self.CMD_M1_POL       = 38    # activate MILES UNITS X, Y polarity
        self.CMD_MLS_2X       = 39    # set output value MILES TENS X
        self.CMD_MLS_2Y       = 40    # set output value MILES TENS Y
        self.CMD_M2_POL       = 41    # activate MILES TENS X, Y polarity
        self.CMD_MLS_3X       = 42    # set output value MILES HUNDREDS X
        self.CMD_MLS_3Y       = 43    # set output value MILES HUNDREDS Y
        self.CMD_M3_POL       = 44    # set MILES HUNDREDS X, Y polarity
        self.CMD_MLS_LOWPOWER = 45    # MILES synchros in low-power when bar is visible
        self.CMD_WTCHDOG_DIS  = 46    # disabled watchdog
        self.CMD_WTCHDOG_ENA  = 47    # enable watchdog
        self.CMD_DIAGMODE     = 48    # set diagnostic LED operating mode

        # Exit button
        self.buttonExit = wx.Button(self, label="Exit", pos=(500, 300), size=(100, 25))
        self.buttonExit.SetForegroundColour('#ff0000')
        self.buttonExit.Bind(wx.EVT_BUTTON, self.ExitClick)
        
        # ID myself
        self.IDline = wx.StaticText(self, label='HSI  board #1  test tool  - V1.4  April 2020.', pos=(10, 330))
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

        # display COM port selection
        wx.StaticBox(tabOne, label='COM ports', pos=(180, 40), size=(170, 120))
        textHSI1 = wx.StaticText(tabOne, label='HSI #1', pos=(194, 65))
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
        self.cbDiagLED.SetToolTip(wx.ToolTip("set LED diag mode"))
        self.cbDiagLED.SetValue('heartbeat')
        self.cbDiagLED.Bind(wx.EVT_COMBOBOX, self.OnSelectDiagLED)

        self.buttonDiagLED = wx.Button(tabOne, label="Set", pos=(490, 58), size=(40, 25))
        self.buttonDiagLED.SetBackgroundColour('#cccccc')
        self.buttonDiagLED.SetForegroundColour('#000000')
        self.buttonDiagLED.Bind(wx.EVT_BUTTON, self.onSendDiagLED)

        # User-defined outputs A and B
        wx.StaticBox(tabOne, label='User outputs', pos=(390, 120), size=(150, 70))
        self.toggleOutputA = wx.CheckBox(tabOne, label='User output A', pos=(400, 138), size=(100, 25))
        self.toggleOutputB = wx.CheckBox(tabOne, label='User output B', pos=(400, 158), size=(100, 25))
        self.toggleOutputA.SetValue(False)
        self.toggleOutputB.SetValue(False)
        self.toggleOutputA.SetToolTip(wx.ToolTip("toggle user-defined output A"))
        self.toggleOutputB.SetToolTip(wx.ToolTip("toggle user-defined output B"))
        self.toggleOutputA.Bind(wx.EVT_CHECKBOX, self.toggleOutputACheckbox)
        self.toggleOutputB.Bind(wx.EVT_CHECKBOX, self.toggleOutputBCheckbox)



#-- TAB #2  Heading  ------------------------------------------------------------------------------
        tabTwo = TabPanel(self)
        self.AddPage(tabTwo, "Heading")
        self.headingImage = wx.Bitmap("front-heading.gif")
        self.headingAccent = wx.StaticBitmap(tabTwo, -1, self.headingImage)
        self.headingAccent.SetPosition((410, 20))

        # Heading setpoint entry
        wx.StaticBox(tabTwo, label='Heading setpoint', pos=(30, 30), size=(295, 80))

        self.Headingentry = wx.TextCtrl(tabTwo, value="0", pos=(45, 60), size=(60, 25))
        textHeadingValidValues = wx.StaticText(tabTwo, label='(0 ... 1023)', pos=(48, 87))
        textHeadingValidValues.SetFont(self.smallFont)

        self.buttonHeadingentrySet = wx.Button(tabTwo, label="Set", pos=(145, 60), size=(60, 25))
        self.buttonHeadingentrySet.SetToolTip(wx.ToolTip("set Heading angle"))
        self.buttonHeadingentrySet.SetBackgroundColour('#99ccff')
        self.buttonHeadingentrySet.SetForegroundColour('#000000')
        self.buttonHeadingentrySet.Bind(wx.EVT_BUTTON, self.HeadingentrySet)
        self.errorHeadingentry = wx.StaticBitmap(tabTwo, -1, self.errorImage)
        self.errorHeadingentry.SetPosition((110, 60))
        self.errorHeadingentry.Hide()

        # Heading increment/decrement buttons
        self.buttonHeadingdec = wx.Button(tabTwo, label="-10", pos=(230, 60), size=(40, 24))
        self.buttonHeadinginc = wx.Button(tabTwo, label="+10", pos=(275, 60), size=(40, 24))
        self.buttonHeadinginc.SetBackgroundColour('#CC3333')
        self.buttonHeadinginc.SetForegroundColour('#ffffff')
        self.buttonHeadingdec.SetBackgroundColour('#CC3333')
        self.buttonHeadingdec.SetForegroundColour('#ffffff')
        self.buttonHeadinginc.Bind(wx.EVT_BUTTON, self.Headingincrement)
        self.buttonHeadingdec.Bind(wx.EVT_BUTTON, self.Headingdecrement)

        # Heading offset entry fields
        wx.StaticBox(tabTwo, label='Heading synchro stator offsets', pos=(30, 130), size=(345, 120))

        self.textHeadingOffsetS1 = wx.StaticText(tabTwo, label='S1 offset', pos=(45, 155))
        self.textHeadingOffsetS2 = wx.StaticText(tabTwo, label='S2 offset', pos=(120, 155))
        self.textHeadingOffsetS3 = wx.StaticText(tabTwo, label='S3 offset', pos=(195, 155))
        self.textHeadingOffsetS1.SetFont(self.smallFont)
        self.textHeadingOffsetS2.SetFont(self.smallFont)
        self.textHeadingOffsetS3.SetFont(self.smallFont)

        textHeadingValidOffset1 = wx.StaticText(tabTwo, label='Valid range  0 ... 1023', pos=(45, 206))
        textHeadingValidOffset2 = wx.StaticText(tabTwo, label='Delta value  341', pos=(45, 219))
        textHeadingValidOffset1.SetFont(self.smallFont)
        textHeadingValidOffset1.SetFont(self.smallFont)
        textHeadingValidOffset1.SetForegroundColour('#0000ff')
        textHeadingValidOffset2.SetForegroundColour('#0000ff')

        self.HeadingOffsetS1Entry = wx.TextCtrl(tabTwo, value=(self.defaultHeadingS1offset), pos=(45, 170), size=(60, 25))
        self.HeadingOffsetS2Entry = wx.TextCtrl(tabTwo, value=(self.defaultHeadingS2offset),pos=(120, 170), size=(60, 25))
        self.HeadingOffsetS3Entry = wx.TextCtrl(tabTwo, value=(self.defaultHeadingS3offset),pos=(195, 170), size=(60, 25))

        self.buttonHeadingOffsetSet = wx.Button(tabTwo, label="Set  offsets", pos=(270, 170), size=(95, 25))
        self.buttonHeadingOffsetSet.SetToolTip(wx.ToolTip("set stator offsets"))
        self.buttonHeadingOffsetSet.SetBackgroundColour('#99ccff')
        self.buttonHeadingOffsetSet.SetForegroundColour('#000000')
        self.buttonHeadingOffsetSet.Bind(wx.EVT_BUTTON, self.sendHeadingOffsets)

        self.buttonHeadingOffsetDefault = wx.Button(tabTwo, label="Load defaults", pos=(270, 210), size=(95, 25))
        self.buttonHeadingOffsetDefault.SetToolTip(wx.ToolTip("restore default offsets"))
        self.buttonHeadingOffsetDefault.SetBackgroundColour('#ffff00')
        self.buttonHeadingOffsetDefault.SetForegroundColour('#000000')
        self.buttonHeadingOffsetDefault.Bind(wx.EVT_BUTTON, self.setHeadingOffsetDefault)



#-- TAB #3  Bearing  ------------------------------------------------------------------------------
        tabThree = TabPanel(self)
        self.AddPage(tabThree, "Bearing")
        self.bearingImage = wx.Bitmap("front-bearing.gif")
        self.bearingAccent = wx.StaticBitmap(tabThree, -1, self.bearingImage)
        self.bearingAccent.SetPosition((410, 20))

        # Bearing setpoint entry
        wx.StaticBox(tabThree, label='Bearing setpoint', pos=(30, 30), size=(295, 80))

        self.Bearingentry = wx.TextCtrl(tabThree, value="0", pos=(45, 60), size=(60, 25))
        textBearingValidValues = wx.StaticText(tabThree, label='(0 ... 1023)', pos=(48, 87))
        textBearingValidValues.SetFont(self.smallFont)
        self.buttonBearingentrySet = wx.Button(tabThree, label="Set", pos=(145, 60), size=(60, 25))
        self.buttonBearingentrySet.SetToolTip(wx.ToolTip("set Bearing angle"))
        self.buttonBearingentrySet.SetBackgroundColour('#99ccff')
        self.buttonBearingentrySet.SetForegroundColour('#000000')
        self.buttonBearingentrySet.Bind(wx.EVT_BUTTON, self.BearingentrySet)
        self.errorBearingentry = wx.StaticBitmap(tabThree, -1, self.errorImage)
        self.errorBearingentry.SetPosition((110, 60))
        self.errorBearingentry.Hide()

        # Bearing increment/decrement buttons
        self.buttonBearingdec = wx.Button(tabThree, label="-10", pos=(230, 60), size=(40, 24))
        self.buttonBearinginc = wx.Button(tabThree, label="+10", pos=(275, 60), size=(40, 24))
        self.buttonBearinginc.SetBackgroundColour('#CC3333')
        self.buttonBearinginc.SetForegroundColour('#ffffff')
        self.buttonBearingdec.SetBackgroundColour('#CC3333')
        self.buttonBearingdec.SetForegroundColour('#ffffff')
        self.buttonBearinginc.Bind(wx.EVT_BUTTON, self.Bearingincrement)
        self.buttonBearingdec.Bind(wx.EVT_BUTTON, self.Bearingdecrement)

        # Bearing offset entry fields
        wx.StaticBox(tabThree, label='Bearing synchro stator offsets', pos=(30, 130), size=(345, 120))

        self.textBearingOffsetS1 = wx.StaticText(tabThree, label='S1 offset', pos=(45, 155))
        self.textBearingOffsetS2 = wx.StaticText(tabThree, label='S2 offset', pos=(120, 155))
        self.textBearingOffsetS3 = wx.StaticText(tabThree, label='S3 offset', pos=(195, 155))
        self.textBearingOffsetS1.SetFont(self.smallFont)
        self.textBearingOffsetS2.SetFont(self.smallFont)
        self.textBearingOffsetS3.SetFont(self.smallFont)

        textBearingValidOffset1 = wx.StaticText(tabThree, label='Valid range  0 ... 1023', pos=(45, 206))
        textBearingValidOffset2 = wx.StaticText(tabThree, label='Delta value  341', pos=(45, 219))
        textBearingValidOffset1.SetFont(self.smallFont)
        textBearingValidOffset1.SetFont(self.smallFont)
        textBearingValidOffset1.SetForegroundColour('#0000ff')
        textBearingValidOffset2.SetForegroundColour('#0000ff')

        self.BearingOffsetS1Entry = wx.TextCtrl(tabThree, value=(self.defaultBearingS1offset), pos=(45, 170), size=(60, 25))
        self.BearingOffsetS2Entry = wx.TextCtrl(tabThree, value=(self.defaultBearingS2offset),pos=(120, 170), size=(60, 25))
        self.BearingOffsetS3Entry = wx.TextCtrl(tabThree, value=(self.defaultBearingS3offset),pos=(195, 170), size=(60, 25))

        self.buttonBearingOffsetSet = wx.Button(tabThree, label="Set  offsets", pos=(270, 170), size=(95, 25))
        self.buttonBearingOffsetSet.SetToolTip(wx.ToolTip("set stator offsets"))
        self.buttonBearingOffsetSet.SetBackgroundColour('#99ccff')
        self.buttonBearingOffsetSet.SetForegroundColour('#000000')
        self.buttonBearingOffsetSet.Bind(wx.EVT_BUTTON, self.sendBearingOffsets)

        self.buttonBearingOffsetDefault = wx.Button(tabThree, label="Load defaults", pos=(270, 210), size=(95, 25))
        self.buttonBearingOffsetDefault.SetToolTip(wx.ToolTip("restore default offsets"))
        self.buttonBearingOffsetDefault.SetBackgroundColour('#ffff00')
        self.buttonBearingOffsetDefault.SetForegroundColour('#000000')
        self.buttonBearingOffsetDefault.Bind(wx.EVT_BUTTON, self.setBearingOffsetDefault)



#-- TAB #4  Range  --------------------------------------------------------------------------------
        tabFour = TabPanel(self)
        self.AddPage(tabFour, " Range ")
        self.rangeImage = wx.Bitmap("front-range.gif")
        self.rangeAccent = wx.StaticBitmap(tabFour, -1, self.rangeImage)
        self.rangeAccent.SetPosition((410, 20))

        # Range setpoint entry
        wx.StaticBox(tabFour, label='Range indication', pos=(30, 30), size=(345, 83))
        self.rangeBarImage = wx.Bitmap("range.gif")

        self.RangeHundredsEntry = wx.TextCtrl(tabFour, value="0", style=wx.TE_CENTRE, pos=(65, 60), size=(50, 25))
        self.RangeTensEntry = wx.TextCtrl(tabFour, value="0", style=wx.TE_CENTRE, pos=(120, 60), size=(50, 25))
        self.RangeOnesEntry = wx.TextCtrl(tabFour, value="0", style=wx.TE_CENTRE, pos=(175, 60), size=(50, 25))
        self.RangeHundredsEntry.SetBackgroundColour('#555555')
        self.RangeTensEntry.SetBackgroundColour('#555555')
        self.RangeOnesEntry.SetBackgroundColour('#555555')

        self.setRangeButton = wx.Button(tabFour, label='Set', pos=(270, 50), size=(60,25))
        self.setRangeButton.SetToolTip(wx.ToolTip("set Range values"))
        self.setRangeButton.SetBackgroundColour('#99ccff')
        self.setRangeButton.SetForegroundColour('#000000')
        self.setRangeButton.Bind(wx.EVT_BUTTON, self.sendRangeValue)
        self.errorRangeEntry = wx.StaticBitmap(tabFour, -1, self.errorImage)
        self.errorRangeEntry.SetPosition((230, 60))
        self.errorRangeEntry.Hide()

        self.buttonRangeValid = wx.Button(tabFour, label="invalid", pos=(270, 80), size=(60, 25))
        self.buttonRangeValid.SetToolTip(wx.ToolTip("toggle Range Bar"))
        self.buttonRangeValid.SetBackgroundColour('#F48C42')
        self.buttonRangeValid.SetForegroundColour('#000000')
        self.buttonRangeValid.Bind(wx.EVT_BUTTON, self.rangeValidFlag)
        self.rangeInvalid = wx.StaticBitmap(tabFour, -1, self.rangeBarImage)
        self.rangeInvalid.SetPosition((45, 88))
        self.textRangeValidData = wx.StaticText(tabFour, label='Valid range  0 ... 1023', pos=(95, 88))
        self.textRangeValidData.SetFont(self.smallFont)
        self.textRangeValidData.SetForegroundColour('#0000ff')
        self.textRangeValidData.Hide()

        # Range offset entry fields
        wx.StaticBox(tabFour, label='Range synchro stator offsets', pos=(30, 130), size=(345, 120))

        self.textChannelSynchro = wx.StaticText(tabFour, label='Synchro', pos=(40, 155))
        self.textChannelSynchro.SetFont(self.smallFont)
        self.textChannelSynchro.SetForegroundColour("#000000")
        synchros = ['Miles 100', 'Miles 10', 'Miles 1']
        self.cbChannel = wx.ComboBox(tabFour, pos=(40, 170), size=(75, 25), value="Miles 100", choices=synchros, style=wx.CB_READONLY)
        self.cbChannel.SetToolTip(wx.ToolTip("select Range synchro"))
        self.cbChannel.Bind(wx.EVT_COMBOBOX, self.OnSelectRangeSynchro)

        self.textOffsetX = wx.StaticText(tabFour, label='X offset', pos=(130, 155))
        self.textOffsetY = wx.StaticText(tabFour, label='Y offset', pos=(200, 155))
        self.RangeXOffsetEntry = wx.TextCtrl(tabFour, value=(self.defaultMiles100Xoffset), pos=(130, 171), size=(60, 22))
        self.RangeYOffsetEntry = wx.TextCtrl(tabFour, value=(self.defaultMiles100Yoffset),pos=(200, 171), size=(60, 22))

        textRangeValidOffset1 = wx.StaticText(tabFour, label='Valid range  0 ... 1023', pos=(132, 206))
        textRangeValidOffset2 = wx.StaticText(tabFour, label='Delta value  171', pos=(132, 219))
        textRangeValidOffset1.SetFont(self.smallFont)
        textRangeValidOffset1.SetFont(self.smallFont)
        textRangeValidOffset1.SetForegroundColour('#0000ff')
        textRangeValidOffset2.SetForegroundColour('#0000ff')

        self.buttonRangeOffsetSet = wx.Button(tabFour, label="Set  offsets", pos=(270, 170), size=(95, 24))
        self.buttonRangeOffsetSet.SetToolTip(wx.ToolTip("set stator offsets"))
        self.buttonRangeOffsetSet.SetBackgroundColour('#99ccff')
        self.buttonRangeOffsetSet.SetForegroundColour('#000000')
        self.buttonRangeOffsetSet.Bind(wx.EVT_BUTTON, self.sendRangeOffsets)

        self.buttonRangeOffsetDefault = wx.Button(tabFour, label="Load defaults", pos=(270, 210), size=(95, 25))
        self.buttonRangeOffsetDefault.SetToolTip(wx.ToolTip("restore default offsets"))
        self.buttonRangeOffsetDefault.SetBackgroundColour('#ffff00')
        self.buttonRangeOffsetDefault.SetForegroundColour('#000000')
        self.buttonRangeOffsetDefault.Bind(wx.EVT_BUTTON, self.setRangeOffsetDefault)

        # RANGE low-power mode
        self.toggleRangeLowPower = wx.CheckBox(tabFour, label=' RANGE synchros low power', pos=(410, 215), size=(170, 25))
        self.toggleRangeLowPower.SetValue(self.MilesLowPowerEnable)
        self.toggleRangeLowPower.SetToolTip(wx.ToolTip("toggle RANGE synchros low-power feature"))
        self.toggleRangeLowPower.Bind(wx.EVT_CHECKBOX, self.toggleRangeLowPowerCheckbox)



#-- TAB #5  Simulate  -----------------------------------------------------------------------------
        tabFive = TabPanel(self)
        self.AddPage(tabFive, "Simulate")
        self.rawDataImage = wx.Bitmap("front-raw.gif")
        self.rawDataAccent = wx.StaticBitmap(tabFive, -1, self.rawDataImage)
        self.rawDataAccent.SetPosition((410, 20))

        simulateButtonList = ['Heading', 'Bearing', 'Range (all)']
        self.simulateObjectBox = wx.RadioBox(tabFive, label = 'Simulate indicator', pos = (20,30),
                                             choices = simulateButtonList, majorDimension = 1)
        self.simulateObjectBox.Bind(wx.EVT_RADIOBOX,self.onSimulateObject)
        self.simulateObject = 0

        wx.StaticBox(tabFive, label=' Step increment', pos=(20, 135), size=(115, 55))
        simulateStepList = ['1', '2', '5', '10', '20' ]
        self.cbSimulateStepSelection = wx.ComboBox(tabFive, pos=(30, 155), size=(75, 25), value=simulateStepList[0],
                                                   choices=simulateStepList, style=wx.CB_READONLY)
        self.cbSimulateStepSelection.SetToolTip(wx.ToolTip("set step size"))
        self.cbSimulateStepSelection.Bind(wx.EVT_COMBOBOX, self.OnSelectSimStepSize)
        self.simulateUpdateStepSelection = 1
        self.simulateStepValue = 1

        wx.StaticBox(tabFive, label=' Update rate', pos=(20, 200), size=(115, 55))
        simulateUpdateList = ['200 ms', '400 ms', '600 ms', '800 ms', '1000 ms' ]
        self.cbSimulateRateSelection = wx.ComboBox(tabFive, pos=(30, 220), size=(75, 25), value=simulateUpdateList[1],
                                                   choices=simulateUpdateList, style=wx.CB_READONLY)
        self.cbSimulateRateSelection.SetToolTip(wx.ToolTip("set update rate"))
        self.cbSimulateRateSelection.Bind(wx.EVT_COMBOBOX, self.OnSelectSimUpdateRate)
        self.simulateUpdateRateSelection = 1
        self.simulateUpdateTime = 400

        wx.StaticBox(tabFive, label=' Start setpoint', pos=(150, 30), size=(195, 80))
        self.simulateStartEntry = wx.TextCtrl(tabFive, value=str(self.simHeadingStartValue), pos=(165, 60), size=(60, 25))
        textSimulateValidValues = wx.StaticText(tabFive, label='(0 ... 1023)', pos=(168, 87))
        textSimulateValidValues.SetFont(self.smallFont)
        self.buttonsimulateStartEntrySet = wx.Button(tabFive, label="Set", pos=(265, 60), size=(60, 25))
        self.buttonsimulateStartEntrySet.SetToolTip(wx.ToolTip("set start value"))
        self.buttonsimulateStartEntrySet.SetBackgroundColour('#99ccff')
        self.buttonsimulateStartEntrySet.SetForegroundColour('#000000')
        self.buttonsimulateStartEntrySet.Bind(wx.EVT_BUTTON, self.simulateStartEntrySet)
        self.errorsimulateStartEntry = wx.StaticBitmap(tabFive, -1, self.errorImage)
        self.errorsimulateStartEntry.SetPosition((230, 60))
        self.errorsimulateStartEntry.Hide()

        wx.StaticBox(tabFive, label=' Simulate indication', pos=(150, 135), size=(195, 100))
        simulateDigitFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.textSimulateShowSetpoint = wx.TextCtrl(tabFive, value=str(self.simHeadingStartValue),
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
        self.rawDataImage = wx.Bitmap("front-raw.gif")
        self.rawDataAccent = wx.StaticBitmap(tabSix, -1, self.rawDataImage)
        self.rawDataAccent.SetPosition((410, 20))

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
        self.deviceAddressEntry.Value = "0x48"
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
        self.gearsAccent.SetPosition((410, 20))

        # Text output: warning - disconnect HSI
        warningFont = wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD)
        textAdjustWarning = wx.StaticText(tabSeven, label='Check  that  the  HSI  instrument  is  * NOT *  connected!', pos=(30, 20))
        textAdjustWarning.SetFont(warningFont)
        textAdjustWarning.SetForegroundColour('#ff0000')
        wx.StaticLine(tabSeven, -1, (20, 40), (375, 3))

        # adjustment object selection
        adjustButtonList = ['Heading', 'Bearing', 'Range (1)', 'Range (10)', 'Range (100)']
        self.adjustObjectBox = wx.RadioBox(tabSeven, label = 'Adjust indicator', pos = (20,60),
                                           choices = adjustButtonList, majorDimension = 1)
        self.adjustObjectBox.Bind(wx.EVT_RADIOBOX,self.onAdjustObject)
        self.adjustObject = 0

        # Text output for the HEADING tests
        instructionFont = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.buttonAdjustHeading = wx.Button(tabSeven, label="Activate Heading stator coil outputs", pos=(150, 70), size=(245, 25))
        self.buttonAdjustHeading.SetToolTip(wx.ToolTip("Start adjustment: set Heading stator coils to max amplitude"))
        self.buttonAdjustHeading.SetBackgroundColour('#99ccff')
        self.buttonAdjustHeading.SetForegroundColour('#000000')
        self.buttonAdjustHeading.Bind(wx.EVT_BUTTON, self.adjustHeadingOutput)
        self.buttonAdjustHeadingState = 0

        self.textAdjustHeading1a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ F ]', pos=(160, 120))
        self.textAdjustHeading2a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ G ]', pos=(160, 120))
        self.textAdjustHeading3a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ H ]', pos=(160, 120))
        self.textAdjustHeading1a.SetFont(instructionFont)
        self.textAdjustHeading2a.SetFont(instructionFont)
        self.textAdjustHeading3a.SetFont(instructionFont)
        self.textAdjustHeading1a.SetForegroundColour('#0000ff')
        self.textAdjustHeading2a.SetForegroundColour('#0000ff')
        self.textAdjustHeading3a.SetForegroundColour('#0000ff')
        self.textAdjustHeading1a.Hide()
        self.textAdjustHeading2a.Hide()
        self.textAdjustHeading3a.Hide()
        self.textAdjustHeading1b = wx.StaticText(tabSeven, label='Adjust trimpot HX to output voltage 10.00V', pos=(160, 140))
        self.textAdjustHeading2b = wx.StaticText(tabSeven, label='Adjust trimpot HY to output voltage 10.00V', pos=(160, 140))
        self.textAdjustHeading3b = wx.StaticText(tabSeven, label='Adjust trimpot HZ to output voltage 10.00V', pos=(160, 140))
        self.textAdjustHeading1b.SetFont(instructionFont)
        self.textAdjustHeading2b.SetFont(instructionFont)
        self.textAdjustHeading3b.SetFont(instructionFont)
        self.textAdjustHeading1b.SetForegroundColour('#0000ff')
        self.textAdjustHeading2b.SetForegroundColour('#0000ff')
        self.textAdjustHeading3b.SetForegroundColour('#0000ff')
        self.textAdjustHeading1b.Hide()
        self.textAdjustHeading2b.Hide()
        self.textAdjustHeading3b.Hide()

        self.adjustHeading1done = wx.CheckBox(tabSeven, label=' Adjustment Heading stator coil S1 done.', pos=(160, 180), size=(240, 25))
        self.adjustHeading1done.SetValue(False)
        self.adjustHeading1done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustHeading1done.Bind(wx.EVT_CHECKBOX, self.adjustHeadingS1checkbox)
        self.adjustHeading2done = wx.CheckBox(tabSeven, label=' Adjustment Heading stator coil S2 done.', pos=(160, 200), size=(240, 25))
        self.adjustHeading2done.SetValue(False)
        self.adjustHeading2done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustHeading2done.Bind(wx.EVT_CHECKBOX, self.adjustHeadingS2checkbox)
        self.adjustHeading3done = wx.CheckBox(tabSeven, label=' Adjustment Heading stator coil S3 done.', pos=(160, 220), size=(240, 25))
        self.adjustHeading3done.SetValue(False)
        self.adjustHeading3done.SetToolTip(wx.ToolTip("after adjustment, tick box to finish adjustment"))
        self.adjustHeading3done.Bind(wx.EVT_CHECKBOX, self.adjustHeadingS3checkbox)
        self.adjustHeading1done.Hide()
        self.adjustHeading2done.Hide()
        self.adjustHeading3done.Hide()

        # Text output for the BEARING tests
        self.buttonAdjustBearing = wx.Button(tabSeven, label="Activate Bearing stator coil outputs", pos=(150, 70), size=(245, 25))
        self.buttonAdjustBearing.SetToolTip(wx.ToolTip("Start adjustment: set Bearing stator coils to max amplitude"))
        self.buttonAdjustBearing.SetBackgroundColour('#99ccff')
        self.buttonAdjustBearing.SetForegroundColour('#000000')
        self.buttonAdjustBearing.Bind(wx.EVT_BUTTON, self.adjustBearingOutput)
        self.buttonAdjustBearing.Hide()
        self.buttonAdjustBearingState = 0

        self.textAdjustBearing1a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ P ]', pos=(160, 120))
        self.textAdjustBearing2a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ R ]', pos=(160, 120))
        self.textAdjustBearing3a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ S ]', pos=(160, 120))
        self.textAdjustBearing1a.SetFont(instructionFont)
        self.textAdjustBearing2a.SetFont(instructionFont)
        self.textAdjustBearing3a.SetFont(instructionFont)
        self.textAdjustBearing1a.SetForegroundColour('#0000ff')
        self.textAdjustBearing2a.SetForegroundColour('#0000ff')
        self.textAdjustBearing3a.SetForegroundColour('#0000ff')
        self.textAdjustBearing1a.Hide()
        self.textAdjustBearing2a.Hide()
        self.textAdjustBearing3a.Hide()
        self.textAdjustBearing1b = wx.StaticText(tabSeven, label='Adjust trimpot BX to output voltage 10.00V', pos=(160, 140))
        self.textAdjustBearing2b = wx.StaticText(tabSeven, label='Adjust trimpot BY to output voltage 10.00V', pos=(160, 140))
        self.textAdjustBearing3b = wx.StaticText(tabSeven, label='Adjust trimpot BZ to output voltage 10.00V', pos=(160, 140))
        self.textAdjustBearing1b.SetFont(instructionFont)
        self.textAdjustBearing2b.SetFont(instructionFont)
        self.textAdjustBearing3b.SetFont(instructionFont)
        self.textAdjustBearing1b.SetForegroundColour('#0000ff')
        self.textAdjustBearing2b.SetForegroundColour('#0000ff')
        self.textAdjustBearing3b.SetForegroundColour('#0000ff')
        self.textAdjustBearing1b.Hide()
        self.textAdjustBearing2b.Hide()
        self.textAdjustBearing3b.Hide()

        self.adjustBearing1done = wx.CheckBox(tabSeven, label=' Adjustment Bearing stator coil S1 done.', pos=(160, 180), size=(240, 25))
        self.adjustBearing1done.SetValue(False)
        self.adjustBearing1done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustBearing1done.Bind(wx.EVT_CHECKBOX, self.adjustBearingS1checkbox)
        self.adjustBearing2done = wx.CheckBox(tabSeven, label=' Adjustment Bearing stator coil S2 done.', pos=(160, 200), size=(240, 25))
        self.adjustBearing2done.SetValue(False)
        self.adjustBearing2done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustBearing2done.Bind(wx.EVT_CHECKBOX, self.adjustBearingS2checkbox)
        self.adjustBearing3done = wx.CheckBox(tabSeven, label=' Adjustment Bearing stator coil S3 done.', pos=(160, 220), size=(240, 25))
        self.adjustBearing3done.SetValue(False)
        self.adjustBearing3done.SetToolTip(wx.ToolTip("after adjustment, tick box to finish adjustment"))
        self.adjustBearing3done.Bind(wx.EVT_CHECKBOX, self.adjustBearingS3checkbox)
        self.adjustBearing1done.Hide()
        self.adjustBearing2done.Hide()
        self.adjustBearing3done.Hide()

        # Text output for the RANGE (1) tests
        self.buttonAdjustRange1 = wx.Button(tabSeven, label="Activate Range (1) stator coil outputs", pos=(150, 70), size=(245, 25))
        self.buttonAdjustRange1.SetToolTip(wx.ToolTip("Start adjustment: set Range (1) stator coils to max amplitude"))
        self.buttonAdjustRange1.SetBackgroundColour('#99ccff')
        self.buttonAdjustRange1.SetForegroundColour('#000000')
        self.buttonAdjustRange1.Bind(wx.EVT_BUTTON, self.adjustRange1Output)
        self.buttonAdjustRange1.Hide()
        self.buttonAdjustRange1State = 0

        self.textAdjustRange11a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ m ]', pos=(160, 120))
        self.textAdjustRange12a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ n ]', pos=(160, 120))
        self.textAdjustRange11a.SetFont(instructionFont)
        self.textAdjustRange12a.SetFont(instructionFont)
        self.textAdjustRange11a.SetForegroundColour('#0000ff')
        self.textAdjustRange12a.SetForegroundColour('#0000ff')
        self.textAdjustRange11a.Hide()
        self.textAdjustRange12a.Hide()
        self.textAdjustRange11b = wx.StaticText(tabSeven, label='Adjust trimpot M1X to output voltage 6.00V', pos=(160, 140))
        self.textAdjustRange12b = wx.StaticText(tabSeven, label='Adjust trimpot M1Y to output voltage 6.00V', pos=(160, 140))
        self.textAdjustRange11b.SetFont(instructionFont)
        self.textAdjustRange12b.SetFont(instructionFont)
        self.textAdjustRange11b.SetForegroundColour('#0000ff')
        self.textAdjustRange12b.SetForegroundColour('#0000ff')
        self.textAdjustRange11b.Hide()
        self.textAdjustRange12b.Hide()

        self.adjustRange11done = wx.CheckBox(tabSeven, label=' Adjustment Range (1) stator coil X done.', pos=(160, 180), size=(240, 25))
        self.adjustRange11done.SetValue(False)
        self.adjustRange11done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustRange11done.Bind(wx.EVT_CHECKBOX, self.adjustRange1S1checkbox)
        self.adjustRange12done = wx.CheckBox(tabSeven, label=' Adjustment Range (1) stator coil Y done.', pos=(160, 200), size=(240, 25))
        self.adjustRange12done.SetValue(False)
        self.adjustRange12done.SetToolTip(wx.ToolTip("after adjustment, tick box to finish adjustment"))
        self.adjustRange12done.Bind(wx.EVT_CHECKBOX, self.adjustRange1S2checkbox)
        self.adjustRange11done.Hide()
        self.adjustRange12done.Hide()

        # Text output for the RANGE (10) tests
        self.buttonAdjustRange2 = wx.Button(tabSeven, label="Activate Range (10) stator coil outputs", pos=(150, 70), size=(245, 25))
        self.buttonAdjustRange2.SetToolTip(wx.ToolTip("Start adjustment: set Range (10) stator coils to max amplitude"))
        self.buttonAdjustRange2.SetBackgroundColour('#99ccff')
        self.buttonAdjustRange2.SetForegroundColour('#000000')
        self.buttonAdjustRange2.Bind(wx.EVT_BUTTON, self.adjustRange2Output)
        self.buttonAdjustRange2.Hide()
        self.buttonAdjustRange2State = 0

        self.textAdjustRange21a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ p ]', pos=(160, 120))
        self.textAdjustRange22a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ q ]', pos=(160, 120))
        self.textAdjustRange21a.SetFont(instructionFont)
        self.textAdjustRange22a.SetFont(instructionFont)
        self.textAdjustRange21a.SetForegroundColour('#0000ff')
        self.textAdjustRange22a.SetForegroundColour('#0000ff')
        self.textAdjustRange21a.Hide()
        self.textAdjustRange22a.Hide()
        self.textAdjustRange21b = wx.StaticText(tabSeven, label='Adjust trimpot M2X to output voltage 6.00V', pos=(160, 140))
        self.textAdjustRange22b = wx.StaticText(tabSeven, label='Adjust trimpot M2Y to output voltage 6.00V', pos=(160, 140))
        self.textAdjustRange21b.SetFont(instructionFont)
        self.textAdjustRange22b.SetFont(instructionFont)
        self.textAdjustRange21b.SetForegroundColour('#0000ff')
        self.textAdjustRange22b.SetForegroundColour('#0000ff')
        self.textAdjustRange21b.Hide()
        self.textAdjustRange22b.Hide()

        self.adjustRange21done = wx.CheckBox(tabSeven, label=' Adjustment Range (10) stator coil X done.', pos=(160, 180), size=(240, 25))
        self.adjustRange21done.SetValue(False)
        self.adjustRange21done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustRange21done.Bind(wx.EVT_CHECKBOX, self.adjustRange2S1checkbox)
        self.adjustRange22done = wx.CheckBox(tabSeven, label=' Adjustment Range (10) stator coil Y done.', pos=(160, 200), size=(240, 25))
        self.adjustRange22done.SetValue(False)
        self.adjustRange22done.SetToolTip(wx.ToolTip("after adjustment, tick box to finish adjustment"))
        self.adjustRange22done.Bind(wx.EVT_CHECKBOX, self.adjustRange2S2checkbox)
        self.adjustRange21done.Hide()
        self.adjustRange22done.Hide()

        # Text output for the RANGE (100) tests
        self.buttonAdjustRange3 = wx.Button(tabSeven, label="Activate Range (100) stator coil outputs", pos=(150, 70), size=(245, 25))
        self.buttonAdjustRange3.SetToolTip(wx.ToolTip("Start adjustment: set Range (100) stator coils to max amplitude"))
        self.buttonAdjustRange3.SetBackgroundColour('#99ccff')
        self.buttonAdjustRange3.SetForegroundColour('#000000')
        self.buttonAdjustRange3.Bind(wx.EVT_BUTTON, self.adjustRange3Output)
        self.buttonAdjustRange3.Hide()
        self.buttonAdjustRange3State = 0

        self.textAdjustRange31a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ r ]', pos=(160, 120))
        self.textAdjustRange32a = wx.StaticText(tabSeven, label='Measure AC voltage on HSI pin  [ s ]', pos=(160, 120))
        self.textAdjustRange31a.SetFont(instructionFont)
        self.textAdjustRange32a.SetFont(instructionFont)
        self.textAdjustRange31a.SetForegroundColour('#0000ff')
        self.textAdjustRange32a.SetForegroundColour('#0000ff')
        self.textAdjustRange31a.Hide()
        self.textAdjustRange32a.Hide()
        self.textAdjustRange31b = wx.StaticText(tabSeven, label='Adjust trimpot M3X to output voltage 6.00V', pos=(160, 140))
        self.textAdjustRange32b = wx.StaticText(tabSeven, label='Adjust trimpot M3Y to output voltage 6.00V', pos=(160, 140))
        self.textAdjustRange31b.SetFont(instructionFont)
        self.textAdjustRange32b.SetFont(instructionFont)
        self.textAdjustRange31b.SetForegroundColour('#0000ff')
        self.textAdjustRange32b.SetForegroundColour('#0000ff')
        self.textAdjustRange31b.Hide()
        self.textAdjustRange32b.Hide()

        self.adjustRange31done = wx.CheckBox(tabSeven, label=' Adjustment Range (100) stator coil X done.', pos=(160, 180), size=(250, 25))
        self.adjustRange31done.SetValue(False)
        self.adjustRange31done.SetToolTip(wx.ToolTip("after adjustment, tick box to proceed"))
        self.adjustRange31done.Bind(wx.EVT_CHECKBOX, self.adjustRange3S1checkbox)
        self.adjustRange32done = wx.CheckBox(tabSeven, label=' Adjustment Range (100) stator coil Y done.', pos=(160, 200), size=(250, 25))
        self.adjustRange32done.SetValue(False)
        self.adjustRange32done.SetToolTip(wx.ToolTip("after adjustment, tick box to finish adjustment"))
        self.adjustRange32done.Bind(wx.EVT_CHECKBOX, self.adjustRange3S2checkbox)
        self.adjustRange31done.Hide()
        self.adjustRange32done.Hide()



# -------------------------------------------------------------------------------------------------------

#    def OnPageChanged(self, event):
#        old = event.GetOldSelection()
#        new = event.GetSelection()
#        sel = self.GetSelection()
#        print('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
#        event.Skip()
#
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
            print("[i] Connection =", self.channelSelection)
        else:
            self.channelSelection = "USB"
            print("[i] Connection =", self.channelSelection)


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
        self.sendData(self.HSIdevice1Address, self.CMD_DIAGMODE, self.DiagLEDdatabyte)
        print("[i] Diagnostic LED function changed")
        if (self.commPortOpened == True):
            # update "Set" button color only to grey if data was actually sent!
            self.buttonDiagLED.SetBackgroundColour('#cccccc')


    def toggleOutputACheckbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.sendData(self.HSIdevice1Address, self.CMD_USROUT_A, 1)
            print("[i] user output A activated")
        else:
            self.sendData(self.HSIdevice1Address, self.CMD_USROUT_A, 0)
            print("[i] user output A de-activated")


    def toggleOutputBCheckbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.sendData(self.HSIdevice1Address, self.CMD_USROUT_B, 1)
            print("[i] user output B activated")
        else:
            self.sendData(self.HSIdevice1Address, self.CMD_USROUT_B, 0)
            print("[i] user output B de-activated")


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

    def setHeadingOffsetDefault(self, event):
        self.HeadingOffsetS1Entry.SetValue(self.defaultHeadingS1offset)
        self.HeadingOffsetS2Entry.SetValue(self.defaultHeadingS2offset)
        self.HeadingOffsetS3Entry.SetValue(self.defaultHeadingS3offset)
        # default values are "always" correct ==> no error flags up, "set" button OK!
        self.buttonHeadingOffsetSet.SetBackgroundColour('#99ccff')

    def HeadingentrySet(self, event):
        Headingvalue = self.Headingentry.GetValue()
        value = self.str2int(Headingvalue)
        if value > 1024:
            self.HeadingsettingValid = False
            self.HeadingEntryErrorShown = True
            self.errorHeadingentry.Show()
        else:
            self.Headingsetting = value
            self.HeadingsettingValid = True
            self.HeadingEntryErrorShown = False
            self.errorHeadingentry.Hide()
            # create correct command subaddress and data
            if value == 1024:
                value = 0
            command = int(value / 256)
            data = value - (command * 256)
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_Q1 + command, data)
            print("[i] heading setpoint updated")

    def Headingincrement(self, e):
        self.Headingsetting = self.Headingsetting + 10
        if self.Headingsetting >= 1024:
            self.Headingsetting = self.Headingsetting - 1024
        self.HeadingEntryErrorShown = False
        self.errorHeadingentry.Hide()
        self.Headingentry.SetValue(str(self.Headingsetting))
        # send to Heading
        value = self.Headingsetting
        if value == 1024:
            value = 0
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.HSIdevice1Address, self.CMD_HDG_Q1 + command, data)
        print("[i] heading setpoint updated")


    def Headingdecrement(self, e):
        if self.Headingsetting >= 10:
            self.Headingsetting = self.Headingsetting - 10
        else:
            diff = 10 - self.Headingsetting
            self.Headingsetting = 1024 - diff
        self.HeadingEntryErrorShown = False
        self.errorHeadingentry.Hide()
        self.Headingentry.SetValue(str(self.Headingsetting))
        # send to Heading
        value = self.Headingsetting
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.HSIdevice1Address, self.CMD_HDG_Q1 + command, data)
        print("[i] heading setpoint updated")


    def sendHeadingOffsets(self, e):
        offset1 = self.HeadingOffsetS1Entry.GetValue()
        offset2 = self.HeadingOffsetS2Entry.GetValue()
        offset3 = self.HeadingOffsetS3Entry.GetValue()
        self.HeadingS1offset = offset1
        self.HeadingS2offset = offset2
        self.HeadingS3offset = offset3
        # validate data
        allDataValid = True
        s1Offset = self.str2int(offset1)
        s2Offset = self.str2int(offset2)
        s3Offset = self.str2int(offset3)
        max = self.maxHeadingOffset
        if (s1Offset > max) or (offset1 == ""):
            allDataValid = False
        if (s2Offset > max) or (offset2 == ""):
            allDataValid = False
        if (s3Offset > max) or (offset3 == ""):
            allDataValid = False
        if allDataValid == True:
            self.buttonHeadingOffsetSet.SetBackgroundColour('#99ccff')
            # send data: LSB first, then MSB offset
            msb = int(s1Offset / 256)
            lsb = s1Offset - (msb * 256)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
            self.sendData(self.HSIdevice1Address, self.CMD_LOAD_HDG, 1)
            msb = int(s2Offset / 256)
            lsb = s2Offset - (msb * 256)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
            self.sendData(self.HSIdevice1Address, self.CMD_LOAD_HDG, 2)
            msb = int(s3Offset / 256)
            lsb = s3Offset - (msb * 256)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
            self.sendData(self.HSIdevice1Address, self.CMD_LOAD_HDG, 4)
            print("[i] heading offsets updated")
        else:
            self.buttonHeadingOffsetSet.SetBackgroundColour('#e05040')

# =================================================================================================

    def setBearingOffsetDefault(self, event):
        self.BearingOffsetS1Entry.SetValue(self.defaultBearingS1offset)
        self.BearingOffsetS2Entry.SetValue(self.defaultBearingS2offset)
        self.BearingOffsetS3Entry.SetValue(self.defaultBearingS3offset)
        # default values are "always" correct ==> no error flags up, "set" button OK!
        self.buttonBearingOffsetSet.SetBackgroundColour('#99ccff')

    def BearingentrySet(self, event):
        Bearingvalue = self.Bearingentry.GetValue()
        value = self.str2int(Bearingvalue)
        if value > 1024:
            self.BearingsettingValid = False
            self.BearingEntryErrorShown = True
            self.errorBearingentry.Show()
        else:
            self.Bearingsetting = value
            self.BearingsettingValid = True
            self.BearingEntryErrorShown = False
            self.errorBearingentry.Hide()
            # create correct command subaddress and data
            if value == 1024:
                value = 0
            command = int(value / 256)
            data = value - (command * 256)
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_Q1 + command, data)
            print("[i] bearing setpoint updated")


    def Bearingincrement(self, e):
        self.Bearingsetting = self.Bearingsetting + 10
        if self.Bearingsetting >= 1024:
            self.Bearingsetting = self.Bearingsetting - 1024
        self.BearingEntryErrorShown = False
        self.errorBearingentry.Hide()
        self.Bearingentry.SetValue(str(self.Bearingsetting))
        # send to Bearing
        value = self.Bearingsetting
        if value == 1024:
            value = 0
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.HSIdevice1Address, self.CMD_BRG_Q1 + command, data)
        print("[i] bearing setpoint updated")


    def Bearingdecrement(self, e):
        if self.Bearingsetting >= 10:
            self.Bearingsetting = self.Bearingsetting - 10
        else:
            diff = 10 - self.Bearingsetting
            self.Bearingsetting = 1024 - diff
        self.BearingEntryErrorShown = False
        self.errorBearingentry.Hide()
        self.Bearingentry.SetValue(str(self.Bearingsetting))
        # send to Bearing
        value = self.Bearingsetting
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.HSIdevice1Address, self.CMD_BRG_Q1 + command, data)
        print("[i] bearing setpoint updated")


    def sendBearingOffsets(self, e):
        offset1 = self.BearingOffsetS1Entry.GetValue()
        offset2 = self.BearingOffsetS2Entry.GetValue()
        offset3 = self.BearingOffsetS3Entry.GetValue()
        self.BearingS1offset = offset1
        self.BearingS2offset = offset2
        self.BearingS3offset = offset3
        # validate data
        allDataValid = True
        max = self.maxBearingOffset
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
            self.buttonBearingOffsetSet.SetBackgroundColour('#99ccff')
            # send data: LSB first, then MSB offset
            msb = int(s1Offset / 256)
            lsb = s1Offset - (msb * 256)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
            self.sendData(self.HSIdevice1Address, self.CMD_LOAD_BRG, 1)
            msb = int(s2Offset / 256)
            lsb = s2Offset - (msb * 256)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
            self.sendData(self.HSIdevice1Address, self.CMD_LOAD_BRG, 2)
            msb = int(s3Offset / 256)
            lsb = s3Offset - (msb * 256)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
            self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
            self.sendData(self.HSIdevice1Address, self.CMD_LOAD_BRG, 4)
            print("[i] bearing offsets updated")
        else:
            self.buttonBearingOffsetSet.SetBackgroundColour('#e05040')

# =================================================================================================

    def rangeValidFlag(self, event):
        button = event.GetEventObject()
        buttonName = button.GetLabel()
        if buttonName == "invalid":
            button.SetLabel(" valid ")
            self.buttonRangeValid.SetBackgroundColour('#AAAAAA')
            self.buttonRangeValid.SetForegroundColour('#FFFFFF')
            self.rangeInvalid.Hide()
            self.textRangeValidData.Show()

            digit3 = self.RangeHundredsEntry.GetValue()
            digit2 = self.RangeTensEntry.GetValue()
            digit1 = self.RangeOnesEntry.GetValue()
            value3 = self.str2int(digit3)
            value2 = self.str2int(digit2)
            value1 = self.str2int(digit1)
            if ((value3 > 1024) | (value2 > 1024) | (value1 > 1024)):
                self.errorRangeEntry.Show()
            else:
                self.errorRangeEntry.Hide()
            self.RangeHundredsEntry.SetBackgroundColour('#eeeeee')
            self.RangeTensEntry.SetBackgroundColour('#eeeeee')
            self.RangeOnesEntry.SetBackgroundColour('#eeeeee')
            self.RangeHundredsEntry.Hide()
            self.RangeTensEntry.Hide()
            self.RangeOnesEntry.Hide()
            self.RangeHundredsEntry.Show()
            self.RangeTensEntry.Show()
            self.RangeOnesEntry.Show()
            self.sendData(self.HSIdevice1Address, self.CMD_MILSHUTR, 1)
            print("[i] range invalid bar hidden")
        else:
            button.SetLabel("invalid")
            self.buttonRangeValid.SetBackgroundColour('#F48C42')
            self.buttonRangeValid.SetForegroundColour('#000000')
            self.textRangeValidData.Hide()
            self.errorRangeEntry.Hide()
            self.rangeInvalid.Show()
            self.RangeHundredsEntry.SetBackgroundColour('#555555')
            self.RangeTensEntry.SetBackgroundColour('#555555')
            self.RangeOnesEntry.SetBackgroundColour('#555555')
            self.RangeHundredsEntry.Hide()
            self.RangeTensEntry.Hide()
            self.RangeOnesEntry.Hide()
            self.RangeHundredsEntry.Show()
            self.RangeTensEntry.Show()
            self.RangeOnesEntry.Show()
            self.sendData(self.HSIdevice1Address, self.CMD_MILSHUTR, 0)
            print("[i] range invalid bar shown")

    def validateXoffset(self, string, number):
        if (number > self.maxMilesOffset) or (string == ""):
            self.rangeOffsetInError = True

    def validateYoffset(self, string, number):
        if (number > self.maxMilesOffset) or (string == ""):
            self.rangeOffsetInError = True


    def sendRangeValue(self, event):
        digit3 = self.RangeHundredsEntry.GetValue()
        digit2 = self.RangeTensEntry.GetValue()
        digit1 = self.RangeOnesEntry.GetValue()
        value3 = self.str2int(digit3)
        value2 = self.str2int(digit2)
        value1 = self.str2int(digit1)

        if ((value3 > 1024) | (value2 > 1024) | (value1 > 1024)):
            self.errorRangeEntry.Show()
        else:
            self.errorRangeEntry.Hide()
            # create correct command subaddress and data
            if value3 == 1024:
                value3 = 0
            if value2 == 1024:
                value2 = 0
            if value1 == 1024:
                value1 = 0
            command3 = int(value3 / 256)
            command2 = int(value2 / 256)
            command1 = int(value1 / 256)
            data3 = value3 - (command3 * 256)
            data2 = value2 - (command2 * 256)
            data1 = value1 - (command1 * 256)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_3Q1 + command3, data3)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_2Q1 + command2, data2)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_1Q1 + command1, data1)
            print("[i] range indication updated")

    def OnSelectRangeSynchro(self, entry):
        self.synchroID = entry.GetString()
        self.rangeOffsetInError = False
        if self.synchroID == "Miles 100":
            self.RangeXOffsetEntry.SetValue(self.Miles100Xoffset)
            self.RangeYOffsetEntry.SetValue(self.Miles100Yoffset)
            offsetXstring = self.Miles100Xoffset
            offsetYstring = self.Miles100Yoffset
            offsetXnumber = self.str2int(offsetXstring)
            offsetYnumber = self.str2int(offsetYstring)
            self.validateXoffset(offsetXstring, offsetXnumber)
            self.validateYoffset(offsetYstring, offsetYnumber)
        elif self.synchroID == "Miles 10":
            self.RangeXOffsetEntry.SetValue(self.Miles10Xoffset)
            self.RangeYOffsetEntry.SetValue(self.Miles10Yoffset)
            offsetXstring = self.Miles10Xoffset
            offsetYstring = self.Miles10Yoffset
            offsetXnumber = self.str2int(offsetXstring)
            offsetYnumber = self.str2int(offsetYstring)
            self.validateXoffset(offsetXstring, offsetXnumber)
            self.validateYoffset(offsetYstring, offsetYnumber)
        else:  # "Miles 1"
            self.RangeXOffsetEntry.SetValue(self.Miles1Xoffset)
            self.RangeYOffsetEntry.SetValue(self.Miles1Yoffset)
            offsetXstring = self.Miles1Xoffset
            offsetYstring = self.Miles1Yoffset
            offsetXnumber = self.str2int(offsetXstring)
            offsetYnumber = self.str2int(offsetYstring)
            self.validateXoffset(offsetXstring, offsetXnumber)
            self.validateYoffset(offsetYstring, offsetYnumber)
        if self.rangeOffsetInError == False:
            self.buttonRangeOffsetSet.SetBackgroundColour('#99ccff')
        else:
            self.buttonRangeOffsetSet.SetBackgroundColour('#e05040')

    def setRangeOffsetDefault(self, event):
        self.buttonRangeOffsetSet.SetBackgroundColour('#99ccff')
        if self.synchroID == "Miles 100":
            self.RangeXOffsetEntry.SetValue(self.defaultMiles100Xoffset)
            self.RangeYOffsetEntry.SetValue(self.defaultMiles100Yoffset)
        elif self.synchroID == "Miles 10":
            self.RangeXOffsetEntry.SetValue(self.defaultMiles10Xoffset)
            self.RangeYOffsetEntry.SetValue(self.defaultMiles10Yoffset)
        else: # "Miles 1":
            self.RangeXOffsetEntry.SetValue(self.defaultMiles1Xoffset)
            self.RangeYOffsetEntry.SetValue(self.defaultMiles1Yoffset)

    def sendRangeOffsets(self, event):
        self.rangeOffsetInError = False
        if self.synchroID == "Miles 100":
            self.Miles100Xoffset = self.RangeXOffsetEntry.GetValue()
            self.Miles100Yoffset = self.RangeYOffsetEntry.GetValue()
            offsetXstring = self.Miles100Xoffset
            offsetYstring = self.Miles100Yoffset
            offsetXnumber = self.str2int(offsetXstring)
            offsetYnumber = self.str2int(offsetYstring)
            self.validateXoffset(offsetXstring, offsetXnumber)
            self.validateYoffset(offsetYstring, offsetYnumber)
        elif self.synchroID == "Miles 10":
            self.Miles10Xoffset = self.RangeXOffsetEntry.GetValue()
            self.Miles10Yoffset = self.RangeYOffsetEntry.GetValue()
            offsetXstring = self.Miles10Xoffset
            offsetYstring = self.Miles10Yoffset
            offsetXnumber = self.str2int(offsetXstring)
            offsetYnumber = self.str2int(offsetYstring)
            self.validateXoffset(offsetXstring, offsetXnumber)
            self.validateYoffset(offsetYstring, offsetYnumber)
        else: # "Miles 1":
            self.Miles1Xoffset = self.RangeXOffsetEntry.GetValue()
            self.Miles1Yoffset = self.RangeYOffsetEntry.GetValue()
            offsetXstring = self.Miles1Xoffset
            offsetYstring = self.Miles1Yoffset
            offsetXnumber = self.str2int(offsetXstring)
            offsetYnumber = self.str2int(offsetYstring)
            self.validateXoffset(offsetXstring, offsetXnumber)
            self.validateYoffset(offsetYstring, offsetYnumber)
        if self.rangeOffsetInError == False:
            self.buttonRangeOffsetSet.SetBackgroundColour('#99ccff')
            if self.synchroID == "Miles 100":
                msb = int(offsetXnumber / 256)
                lsb = offsetXnumber - (msb * 256)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
                self.sendData(self.HSIdevice1Address, self.CMD_LOAD_RNG, 0x10)
                msb = int(offsetYnumber / 256)
                lsb = offsetYnumber - (msb * 256)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
                self.sendData(self.HSIdevice1Address, self.CMD_LOAD_RNG, 0x20)
                print("[i] range (100) offsets updated")
            elif self.synchroID == "Miles 10":
                msb = int(offsetXnumber / 256)
                lsb = offsetXnumber - (msb * 256)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
                self.sendData(self.HSIdevice1Address, self.CMD_LOAD_RNG, 4)
                msb = int(offsetYnumber / 256)
                lsb = offsetYnumber - (msb * 256)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
                self.sendData(self.HSIdevice1Address, self.CMD_LOAD_RNG, 8)
                print("[i] range (10) offsets updated")
            else: # "Miles 1":
                msb = int(offsetXnumber / 256)
                lsb = offsetXnumber - (msb * 256)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
                self.sendData(self.HSIdevice1Address, self.CMD_LOAD_RNG, 1)
                msb = int(offsetYnumber / 256)
                lsb = offsetYnumber - (msb * 256)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_L, lsb)
                self.sendData(self.HSIdevice1Address, self.CMD_LD_OFFS_H, msb)
                self.sendData(self.HSIdevice1Address, self.CMD_LOAD_RNG, 2)
                print("[i] range (1) offsets updated")
        else:
            self.buttonRangeOffsetSet.SetBackgroundColour('#e05040')

    def toggleRangeLowPowerCheckbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.MilesLowPowerEnable = True
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_LOWPOWER, 1)
            print("[i] RANGE synchros low-power mode enabled")
        else:
            self.MilesLowPowerEnable = False
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_LOWPOWER, 0)
            print("[i] RANGE synchros low-power mode disabled")

# =================================================================================================
    def onSimulateObject(self, e):
        self.buttonsimulateStartEntrySet.SetBackgroundColour('#99ccff')
        self.simulateStartButton.SetBackgroundColour('#99ccff')
        self.simulateStopButton.SetBackgroundColour('#eeeeee')
        self.simulateStatus = 0
        self.simulateFirstStart = True
        if self.simulateObjectBox.GetStringSelection() == "Heading":
            self.simulateObject = 0
            self.simulateStartEntry.SetValue(str(self.simHeadingStartValue))
            if self.simHeadingStartValue > 1023:
                self.errorsimulateStartEntry.Show()
                self.textSimulateShowSetpoint.SetValue("0")
            else:
                self.errorsimulateStartEntry.Hide()
                self.textSimulateShowSetpoint.SetValue(str(self.simHeadingStartValue))
        elif  self.simulateObjectBox.GetStringSelection() == "Bearing":
            self.simulateObject = 1
            self.simulateStartEntry.SetValue(str(self.simBearingStartValue))
            if self.simBearingStartValue > 1023:
                self.errorsimulateStartEntry.Show()
                self.textSimulateShowSetpoint.SetValue("0")
            else:
                self.errorsimulateStartEntry.Hide()
                self.textSimulateShowSetpoint.SetValue(str(self.simBearingStartValue))
        else:
            # self.simulateObjectBox.GetStringSelection() == "Range (all)"
            self.simulateObject = 2
            self.simulateStartEntry.SetValue(str(self.simRangeStartValue))
            if self.simRangeStartValue > 1023:
                self.errorsimulateStartEntry.Show()
                self.textSimulateShowSetpoint.SetValue("0")
            else:
                self.errorsimulateStartEntry.Hide()
                self.textSimulateShowSetpoint.SetValue(str(self.simRangeStartValue))


    def simulateStartEntrySet(self, e):
        if self.simulateStatus == 0:
            value = self.str2int(self.simulateStartEntry.GetValue())
            if value > 1024:
                self.errorsimulateStartEntry.Show()
            else:
                self.errorsimulateStartEntry.Hide()
                self.textSimulateShowSetpoint.SetValue(str(value))
                self.simulateStartButton.SetBackgroundColour('#99ccff')
                self.simulateFirstStart = True
                if self.simulateObject == 0:
                    # set heading start value
                    self.simHeadingStartValue = value
                    if value == 1024:
                        value = 0
                    command = int(value / 256)
                    data = value - (command * 256)
                    self.sendData(self.HSIdevice1Address, self.CMD_HDG_Q1 + command, data)
                    print("SIM heading start set")
                elif self.simulateObject == 1:
                    # set bearing start value
                    self.simBearingStartValue = value
                    if value == 1024:
                        value = 0
                    command = int(value / 256)
                    data = value - (command * 256)
                    self.sendData(self.HSIdevice1Address, self.CMD_BRG_Q1 + command, data)
                    print("SIM bearing start set")
                else:
                    # set range start value
                    self.simRangeStartValue = value
                    if value == 1024:
                        value = 0
                    command = int(value / 256)
                    data = value - (command * 256)
                    self.sendData(self.HSIdevice1Address, self.CMD_MLS_3Q1 + command, data)
                    self.sendData(self.HSIdevice1Address, self.CMD_MLS_2Q1 + command, data)
                    self.sendData(self.HSIdevice1Address, self.CMD_MLS_1Q1 + command, data)
                    print("SIM range start set")


    def simulateStartSimulation(self, e):
        if self.simulateStatus == 0:
            if self.simulateFirstStart == True:
                # load start value
                if self.simulateObject == 0:
                    value = self.simHeadingStartValue
                elif self.simulateObject == 1:
                    value = self.simBearingStartValue
                else:
                    value = self.simRangeStartValue
            else:
                # load resume value
                value = self.simulateRunningValue
            if value < 1024:
                self.simulateFirstStart = False
                self.buttonsimulateStartEntrySet.SetBackgroundColour('#eeeeee')
                self.simulateStartButton.SetBackgroundColour('#eeeeee')
                self.simulateStopButton.SetBackgroundColour('#99ccff')
                self.simulateRunningValue = value
                self.textSimulateShowSetpoint.SetValue(str(self.simulateRunningValue))
                self.simulateStatus = 1
                print("simulation started")
                self.startTimer(self.simulateUpdateTime)


    def simulateStopSimulation(self, e):
        if self.simulateStatus == 1:
            self.buttonsimulateStartEntrySet.SetBackgroundColour('#99ccff')
            self.simulateStartButton.SetBackgroundColour('#99ccff')
            self.simulateStopButton.SetBackgroundColour('#eeeeee')
            self.simulateStatus = 0
            print("simulation stopped")


    def OnSelectSimStepSize(self, entry):
        selection = entry.GetSelection()
        if selection == 0:
            self.simulateStepValue = 1
        elif selection == 1:
            self.simulateStepValue = 2
        elif selection == 2:
            self.simulateStepValue = 5
        elif selection == 3:
            self.simulateStepValue = 10
        else:
            self.simulateStepValue = 20


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
        addressValue = 72
        if self.validateDOAdata == True:
            if advDeviceAddress == "0x48" or advDeviceAddress == "0X48" or advDeviceAddress == "72" :
                portID = "HSI-1"
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
            if (subValue > 49) or (advDeviceSubAddress == ""):
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
    def adjustHeadingHideItems(self):
        # hide Heading adjustment procedure and de-activate start button
        self.buttonAdjustHeading.Hide()
        self.buttonAdjustHeading.SetLabel("Activate Heading stator coil outputs")
        self.buttonAdjustHeading.SetBackgroundColour('#99ccff')  # blue-ish
        self.buttonAdjustHeading.SetForegroundColour('#000000')
        self.buttonAdjustHeading.SetToolTip(wx.ToolTip("Start adjustment: set Heading stator coils to max amplitude"))
        self.adjustHeading1done.SetValue(False)
        self.adjustHeading2done.SetValue(False)
        self.adjustHeading3done.SetValue(False)
        self.textAdjustHeading1a.Hide()
        self.textAdjustHeading1b.Hide()
        self.textAdjustHeading2a.Hide()
        self.textAdjustHeading2b.Hide()
        self.textAdjustHeading3a.Hide()
        self.textAdjustHeading3b.Hide()
        self.adjustHeading1done.Hide()
        self.adjustHeading2done.Hide()
        self.adjustHeading3done.Hide()
        if self.buttonAdjustHeadingState == 1:
            self.buttonAdjustHeadingState = 0
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_S1, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_S2, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_S3, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_POL, 0)
            print("[i] heading adjustment terminated")


    def adjustHeadingOutput(self, event):
        if self.buttonAdjustHeadingState == 0:
            self.buttonAdjustHeadingState = 1
            self.buttonAdjustHeading.SetLabel("De-activate Heading stator coil outputs")
            self.buttonAdjustHeading.SetBackgroundColour('#F48C42')  # red-ish
            self.buttonAdjustHeading.SetForegroundColour('#ffffff')
            self.buttonAdjustHeading.SetToolTip(wx.ToolTip("Stop adjustment: set Heading stator coils to zero"))
            # start measurement procedure
            self.textAdjustHeading1a.Show()
            self.textAdjustHeading1b.Show()
            self.adjustHeading1done.Show()
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_S1, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_S2, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_S3, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_POL, 0)
            print("[i] heading adjustment started")
        else:
            self.buttonAdjustHeadingState = 0
            self.buttonAdjustHeading.SetLabel("Activate Heading stator coil outputs")
            self.buttonAdjustHeading.SetBackgroundColour('#99ccff')  # blue-ish
            self.buttonAdjustHeading.SetForegroundColour('#000000')
            self.buttonAdjustHeading.SetToolTip(wx.ToolTip("Start adjustment: set Heading stator coils to max amplitude"))
            self.adjustHeading1done.SetValue(False)
            self.adjustHeading2done.SetValue(False)
            self.adjustHeading3done.SetValue(False)
            self.textAdjustHeading1a.Hide()
            self.textAdjustHeading1b.Hide()
            self.textAdjustHeading2a.Hide()
            self.textAdjustHeading2b.Hide()
            self.textAdjustHeading3a.Hide()
            self.textAdjustHeading3b.Hide()
            self.adjustHeading1done.Hide()
            self.adjustHeading2done.Hide()
            self.adjustHeading3done.Hide()
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_S1, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_S2, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_S3, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_HDG_POL, 0)
            print("[i] heading adjustment terminated")


    def adjustHeadingS1checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S2
            self.textAdjustHeading1a.Hide()
            self.textAdjustHeading1b.Hide()
            self.textAdjustHeading3a.Hide()
            self.textAdjustHeading3b.Hide()
            self.textAdjustHeading2a.Show()
            self.textAdjustHeading2b.Show()
            self.adjustHeading2done.SetValue(False)
            self.adjustHeading2done.Show()
        else:
            # back to check coil S1 (hide check S2 and S3)
            self.textAdjustHeading2a.Hide()
            self.textAdjustHeading2b.Hide()
            self.textAdjustHeading3a.Hide()
            self.textAdjustHeading3b.Hide()
            self.textAdjustHeading1a.Show()
            self.textAdjustHeading1b.Show()
            self.adjustHeading2done.SetValue(False)
            self.adjustHeading2done.Hide()
            self.adjustHeading3done.SetValue(False)
            self.adjustHeading3done.Hide()


    def adjustHeadingS2checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S3
            self.textAdjustHeading1a.Hide()
            self.textAdjustHeading1b.Hide()
            self.textAdjustHeading2a.Hide()
            self.textAdjustHeading2b.Hide()
            self.textAdjustHeading3a.Show()
            self.textAdjustHeading3b.Show()
            self.adjustHeading3done.SetValue(False)
            self.adjustHeading3done.Show()
        else:
            # back to check coil S2 (hide check S3)
            self.textAdjustHeading1a.Hide()
            self.textAdjustHeading1b.Hide()
            self.textAdjustHeading3a.Hide()
            self.textAdjustHeading3b.Hide()
            self.textAdjustHeading2a.Show()
            self.textAdjustHeading2b.Show()
            self.adjustHeading2done.SetValue(False)
            self.adjustHeading2done.Show()
            self.adjustHeading3done.SetValue(False)
            self.adjustHeading3done.Hide()


    def adjustHeadingS3checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # check done!
            self.textAdjustHeading1a.Hide()
            self.textAdjustHeading1b.Hide()
            self.textAdjustHeading2a.Hide()
            self.textAdjustHeading2b.Hide()
            self.textAdjustHeading3a.Hide()
            self.textAdjustHeading3b.Hide()
        else:
            # back to check coil S3
            self.textAdjustHeading1a.Hide()
            self.textAdjustHeading1b.Hide()
            self.textAdjustHeading2a.Hide()
            self.textAdjustHeading2b.Hide()
            self.textAdjustHeading3a.Show()
            self.textAdjustHeading3b.Show()
            self.adjustHeading3done.SetValue(False)


    def adjustBearingHideItems(self):
        # hide Bearing adjustment procedure and de-activate start button
        self.buttonAdjustBearing.Hide()
        self.buttonAdjustBearing.SetLabel("Activate Bearing stator coil outputs")
        self.buttonAdjustBearing.SetBackgroundColour('#99ccff')  # blue-ish
        self.buttonAdjustBearing.SetForegroundColour('#000000')
        self.buttonAdjustBearing.SetToolTip(wx.ToolTip("Start adjustment: set Bearing stator coils to max amplitude"))
        self.adjustBearing1done.SetValue(False)
        self.adjustBearing2done.SetValue(False)
        self.adjustBearing3done.SetValue(False)
        self.textAdjustBearing1a.Hide()
        self.textAdjustBearing1b.Hide()
        self.textAdjustBearing2a.Hide()
        self.textAdjustBearing2b.Hide()
        self.textAdjustBearing3a.Hide()
        self.textAdjustBearing3b.Hide()
        self.adjustBearing1done.Hide()
        self.adjustBearing2done.Hide()
        self.adjustBearing3done.Hide()
        if self.buttonAdjustBearingState == 1:
            self.buttonAdjustBearingState = 0
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_S1, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_S2, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_S3, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_POL, 0)
            print("[i] bearing adjustment terminated")


    def adjustBearingOutput(self, event):
        if self.buttonAdjustBearingState == 0:
            self.buttonAdjustBearingState = 1
            self.buttonAdjustBearing.SetLabel("De-activate Bearing stator coil outputs")
            self.buttonAdjustBearing.SetBackgroundColour('#F48C42')  # red-ish
            self.buttonAdjustBearing.SetForegroundColour('#ffffff')
            self.buttonAdjustBearing.SetToolTip(wx.ToolTip("Stop adjustment: set Bearing stator coils to zero"))
            # start measurement procedure
            self.textAdjustBearing1a.Show()
            self.textAdjustBearing1b.Show()
            self.adjustBearing1done.Show()
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_S1, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_S2, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_S3, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_POL, 0)
            print("[i] bearing adjustment started")
        else:
            self.buttonAdjustBearingState = 0
            self.buttonAdjustBearing.SetLabel("Activate Bearing stator coil outputs")
            self.buttonAdjustBearing.SetBackgroundColour('#99ccff')  # blue-ish
            self.buttonAdjustBearing.SetForegroundColour('#000000')
            self.buttonAdjustBearing.SetToolTip(wx.ToolTip("Start adjustment: set Bearing stator coils to max amplitude"))
            self.adjustBearing1done.SetValue(False)
            self.adjustBearing2done.SetValue(False)
            self.adjustBearing3done.SetValue(False)
            self.textAdjustBearing1a.Hide()
            self.textAdjustBearing1b.Hide()
            self.textAdjustBearing2a.Hide()
            self.textAdjustBearing2b.Hide()
            self.textAdjustBearing3a.Hide()
            self.textAdjustBearing3b.Hide()
            self.adjustBearing1done.Hide()
            self.adjustBearing2done.Hide()
            self.adjustBearing3done.Hide()
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_S1, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_S2, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_S3, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_BRG_POL, 0)
            print("[i] bearing adjustment terminated")


    def adjustBearingS1checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S2
            self.textAdjustBearing1a.Hide()
            self.textAdjustBearing1b.Hide()
            self.textAdjustBearing3a.Hide()
            self.textAdjustBearing3b.Hide()
            self.textAdjustBearing2a.Show()
            self.textAdjustBearing2b.Show()
            self.adjustBearing2done.SetValue(False)
            self.adjustBearing2done.Show()
        else:
            # back to check coil S1 (hide check S2 and S3)
            self.textAdjustBearing2a.Hide()
            self.textAdjustBearing2b.Hide()
            self.textAdjustBearing3a.Hide()
            self.textAdjustBearing3b.Hide()
            self.textAdjustBearing1a.Show()
            self.textAdjustBearing1b.Show()
            self.adjustBearing2done.SetValue(False)
            self.adjustBearing2done.Hide()
            self.adjustBearing3done.SetValue(False)
            self.adjustBearing3done.Hide()


    def adjustBearingS2checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S3
            self.textAdjustBearing1a.Hide()
            self.textAdjustBearing1b.Hide()
            self.textAdjustBearing2a.Hide()
            self.textAdjustBearing2b.Hide()
            self.textAdjustBearing3a.Show()
            self.textAdjustBearing3b.Show()
            self.adjustBearing3done.SetValue(False)
            self.adjustBearing3done.Show()
        else:
            # back to check coil S2 (hide check S3)
            self.textAdjustBearing1a.Hide()
            self.textAdjustBearing1b.Hide()
            self.textAdjustBearing3a.Hide()
            self.textAdjustBearing3b.Hide()
            self.textAdjustBearing2a.Show()
            self.textAdjustBearing2b.Show()
            self.adjustBearing2done.SetValue(False)
            self.adjustBearing2done.Show()
            self.adjustBearing3done.SetValue(False)
            self.adjustBearing3done.Hide()


    def adjustBearingS3checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # check done!
            self.textAdjustBearing1a.Hide()
            self.textAdjustBearing1b.Hide()
            self.textAdjustBearing2a.Hide()
            self.textAdjustBearing2b.Hide()
            self.textAdjustBearing3a.Hide()
            self.textAdjustBearing3b.Hide()
        else:
            # back to check coil S3
            self.textAdjustBearing1a.Hide()
            self.textAdjustBearing1b.Hide()
            self.textAdjustBearing2a.Hide()
            self.textAdjustBearing2b.Hide()
            self.textAdjustBearing3a.Show()
            self.textAdjustBearing3b.Show()
            self.adjustBearing3done.SetValue(False)


    def adjustRange1HideItems(self):
        # hide Range (1) adjustment procedure and de-activate start button
        self.buttonAdjustRange1.Hide()
        self.buttonAdjustRange1.SetLabel("Activate Range (1) stator coil outputs")
        self.buttonAdjustRange1.SetBackgroundColour('#99ccff')  # blue-ish
        self.buttonAdjustRange1.SetForegroundColour('#000000')
        self.buttonAdjustRange1.SetToolTip(wx.ToolTip("Start adjustment: set Range (1) stator coils to max amplitude"))
        self.adjustRange11done.SetValue(False)
        self.adjustRange12done.SetValue(False)
        self.textAdjustRange11a.Hide()
        self.textAdjustRange11b.Hide()
        self.textAdjustRange12a.Hide()
        self.textAdjustRange12b.Hide()
        self.adjustRange11done.Hide()
        self.adjustRange12done.Hide()
        if self.buttonAdjustRange1State == 1:
            self.buttonAdjustRange1State = 0
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_1X, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_1Y, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_M1_POL, 0)
            print("[i] range (1) adjustment terminated")


    def adjustRange1Output(self, event):
        if self.buttonAdjustRange1State == 0:
            self.buttonAdjustRange1State = 1
            self.buttonAdjustRange1.SetLabel("De-activate Range (1) stator coil outputs")
            self.buttonAdjustRange1.SetBackgroundColour('#F48C42')  # red-ish
            self.buttonAdjustRange1.SetForegroundColour('#ffffff')
            self.buttonAdjustRange1.SetToolTip(wx.ToolTip("Stop adjustment: set Range (1) stator coils to zero"))
            # start measurement procedure
            self.textAdjustRange11a.Show()
            self.textAdjustRange11b.Show()
            self.adjustRange11done.Show()
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_1X, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_1Y, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_M1_POL, 0)
            print("[i] range (1) adjustment started")
        else:
            self.buttonAdjustRange1State = 0
            self.buttonAdjustRange1.SetLabel("Activate Range (1) stator coil outputs")
            self.buttonAdjustRange1.SetBackgroundColour('#99ccff')  # blue-ish
            self.buttonAdjustRange1.SetForegroundColour('#000000')
            self.buttonAdjustRange1.SetToolTip(wx.ToolTip("Start adjustment: set Range (1) stator coils to max amplitude"))
            self.adjustRange11done.SetValue(False)
            self.adjustRange12done.SetValue(False)
            self.textAdjustRange11a.Hide()
            self.textAdjustRange11b.Hide()
            self.textAdjustRange12a.Hide()
            self.textAdjustRange12b.Hide()
            self.adjustRange11done.Hide()
            self.adjustRange12done.Hide()
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_1X, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_1Y, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_M1_POL, 0)
            print("[i] range (1) adjustment terminated")


    def adjustRange1S1checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S2
            self.textAdjustRange11a.Hide()
            self.textAdjustRange11b.Hide()
            self.textAdjustRange12a.Show()
            self.textAdjustRange12b.Show()
            self.adjustRange12done.SetValue(False)
            self.adjustRange12done.Show()
        else:
            # back to check coil S1 (hide check S2)
            self.textAdjustRange12a.Hide()
            self.textAdjustRange12b.Hide()
            self.textAdjustRange11a.Show()
            self.textAdjustRange11b.Show()
            self.adjustRange12done.SetValue(False)
            self.adjustRange12done.Hide()


    def adjustRange1S2checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # check done!
            self.textAdjustRange11a.Hide()
            self.textAdjustRange11b.Hide()
            self.textAdjustRange12a.Hide()
            self.textAdjustRange12b.Hide()
        else:
            # back to check coil S2
            self.textAdjustRange11a.Hide()
            self.textAdjustRange11b.Hide()
            self.textAdjustRange12a.Show()
            self.textAdjustRange12b.Show()
            self.adjustRange12done.SetValue(False)


    def adjustRange2HideItems(self):
        # hide Range (10) adjustment procedure and de-activate start button
        self.buttonAdjustRange2.Hide()
        self.buttonAdjustRange2.SetLabel("Activate Range (10) stator coil outputs")
        self.buttonAdjustRange2.SetBackgroundColour('#99ccff')  # blue-ish
        self.buttonAdjustRange2.SetForegroundColour('#000000')
        self.buttonAdjustRange2.SetToolTip(wx.ToolTip("Start adjustment: set Range (10) stator coils to max amplitude"))
        self.adjustRange21done.SetValue(False)
        self.adjustRange22done.SetValue(False)
        self.textAdjustRange21a.Hide()
        self.textAdjustRange21b.Hide()
        self.textAdjustRange22a.Hide()
        self.textAdjustRange22b.Hide()
        self.adjustRange21done.Hide()
        self.adjustRange22done.Hide()
        if self.buttonAdjustRange2State == 1:
            self.buttonAdjustRange2State = 0
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_2X, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_2Y, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_M2_POL, 0)
            print("[i] range (10) adjustment terminated")


    def adjustRange2Output(self, event):
        if self.buttonAdjustRange2State == 0:
            self.buttonAdjustRange2State = 1
            self.buttonAdjustRange2.SetLabel("De-activate Range (10) stator coil outputs")
            self.buttonAdjustRange2.SetBackgroundColour('#F48C42')  # red-ish
            self.buttonAdjustRange2.SetForegroundColour('#ffffff')
            self.buttonAdjustRange2.SetToolTip(wx.ToolTip("Stop adjustment: set Range (10) stator coils to zero"))
            # start measurement procedure
            self.textAdjustRange21a.Show()
            self.textAdjustRange21b.Show()
            self.adjustRange21done.Show()
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_2X, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_2Y, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_M2_POL, 0)
            print("[i] range (10) adjustment started")
        else:
            self.buttonAdjustRange2State = 0
            self.buttonAdjustRange2.SetLabel("Activate Range (10) stator coil outputs")
            self.buttonAdjustRange2.SetBackgroundColour('#99ccff')  # blue-ish
            self.buttonAdjustRange2.SetForegroundColour('#000000')
            self.buttonAdjustRange2.SetToolTip(wx.ToolTip("Start adjustment: set Range (10) stator coils to max amplitude"))
            self.adjustRange21done.SetValue(False)
            self.adjustRange22done.SetValue(False)
            self.textAdjustRange21a.Hide()
            self.textAdjustRange21b.Hide()
            self.textAdjustRange22a.Hide()
            self.textAdjustRange22b.Hide()
            self.adjustRange21done.Hide()
            self.adjustRange22done.Hide()
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_2X, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_2Y, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_M2_POL, 0)
            print("[i] range (10) adjustment terminated")


    def adjustRange2S1checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S2
            self.textAdjustRange21a.Hide()
            self.textAdjustRange21b.Hide()
            self.textAdjustRange22a.Show()
            self.textAdjustRange22b.Show()
            self.adjustRange22done.SetValue(False)
            self.adjustRange22done.Show()
        else:
            # back to check coil S1 (hide check S2)
            self.textAdjustRange22a.Hide()
            self.textAdjustRange22b.Hide()
            self.textAdjustRange21a.Show()
            self.textAdjustRange21b.Show()
            self.adjustRange22done.SetValue(False)
            self.adjustRange22done.Hide()


    def adjustRange2S2checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # check done!
            self.textAdjustRange21a.Hide()
            self.textAdjustRange21b.Hide()
            self.textAdjustRange22a.Hide()
            self.textAdjustRange22b.Hide()
        else:
            # back to check coil S2
            self.textAdjustRange21a.Hide()
            self.textAdjustRange21b.Hide()
            self.textAdjustRange22a.Show()
            self.textAdjustRange22b.Show()
            self.adjustRange22done.SetValue(False)


    def adjustRange3HideItems(self):
        # hide Range (100) adjustment procedure and de-activate start button
        self.buttonAdjustRange3.Hide()
        self.buttonAdjustRange3.SetLabel("Activate Range (100) stator coil outputs")
        self.buttonAdjustRange3.SetBackgroundColour('#99ccff')  # blue-ish
        self.buttonAdjustRange3.SetForegroundColour('#000000')
        self.buttonAdjustRange3.SetToolTip(wx.ToolTip("Start adjustment: set Range (100) stator coils to max amplitude"))
        self.adjustRange31done.SetValue(False)
        self.adjustRange32done.SetValue(False)
        self.textAdjustRange31a.Hide()
        self.textAdjustRange31b.Hide()
        self.textAdjustRange32a.Hide()
        self.textAdjustRange32b.Hide()
        self.adjustRange31done.Hide()
        self.adjustRange32done.Hide()
        if self.buttonAdjustRange3State == 1:
            self.buttonAdjustRange3State = 0
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_3X, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_3Y, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_M3_POL, 0)
            print("[i] range (100) adjustment terminated")


    def adjustRange3Output(self, event):
        if self.buttonAdjustRange3State == 0:
            self.buttonAdjustRange3State = 1
            self.buttonAdjustRange3.SetLabel("De-activate Range (100) stator coil outputs")
            self.buttonAdjustRange3.SetBackgroundColour('#F48C42')  # red-ish
            self.buttonAdjustRange3.SetForegroundColour('#ffffff')
            self.buttonAdjustRange3.SetToolTip(wx.ToolTip("Stop adjustment: set Range (100) stator coils to zero"))
            # start measurement procedure
            self.textAdjustRange31a.Show()
            self.textAdjustRange31b.Show()
            self.adjustRange31done.Show()
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_3X, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_3Y, 255)
            self.sendData(self.HSIdevice1Address, self.CMD_M3_POL, 0)
            print("[i] range (100) adjustment started")
        else:
            self.buttonAdjustRange3State = 0
            self.buttonAdjustRange3.SetLabel("Activate Range (100) stator coil outputs")
            self.buttonAdjustRange3.SetBackgroundColour('#99ccff')  # blue-ish
            self.buttonAdjustRange3.SetForegroundColour('#000000')
            self.buttonAdjustRange3.SetToolTip(wx.ToolTip("Start adjustment: set Range (100) stator coils to max amplitude"))
            self.adjustRange31done.SetValue(False)
            self.adjustRange32done.SetValue(False)
            self.textAdjustRange31a.Hide()
            self.textAdjustRange31b.Hide()
            self.textAdjustRange32a.Hide()
            self.textAdjustRange32b.Hide()
            self.adjustRange31done.Hide()
            self.adjustRange32done.Hide()
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_3X, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_MLS_3Y, 0)
            self.sendData(self.HSIdevice1Address, self.CMD_M3_POL, 0)
            print("[i] range (100) adjustment terminated")


    def adjustRange3S1checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # move to check coil S2
            self.textAdjustRange31a.Hide()
            self.textAdjustRange31b.Hide()
            self.textAdjustRange32a.Show()
            self.textAdjustRange32b.Show()
            self.adjustRange32done.SetValue(False)
            self.adjustRange32done.Show()
        else:
            # back to check coil S1 (hide check S2)
            self.textAdjustRange32a.Hide()
            self.textAdjustRange32b.Hide()
            self.textAdjustRange31a.Show()
            self.textAdjustRange31b.Show()
            self.adjustRange32done.SetValue(False)
            self.adjustRange32done.Hide()


    def adjustRange3S2checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            # check done!
            self.textAdjustRange31a.Hide()
            self.textAdjustRange31b.Hide()
            self.textAdjustRange32a.Hide()
            self.textAdjustRange32b.Hide()
        else:
            # back to check coil S2
            self.textAdjustRange31a.Hide()
            self.textAdjustRange31b.Hide()
            self.textAdjustRange32a.Show()
            self.textAdjustRange32b.Show()
            self.adjustRange32done.SetValue(False)


    def onAdjustObject(self, e):
        if self.adjustObjectBox.GetStringSelection() == "Heading":
            self.adjustObject = 0
            self.adjustBearingHideItems()
            self.adjustRange1HideItems()
            self.adjustRange2HideItems()
            self.adjustRange3HideItems()
            self.buttonAdjustHeading.Show()
        elif  self.adjustObjectBox.GetStringSelection() == "Bearing":
            self.adjustObject = 1
            self.adjustHeadingHideItems()
            self.adjustRange1HideItems()
            self.adjustRange2HideItems()
            self.adjustRange3HideItems()
            self.buttonAdjustBearing.Show()
        elif  self.adjustObjectBox.GetStringSelection() == "Range (1)":
            self.adjustObject = 2
            self.adjustHeadingHideItems()
            self.adjustBearingHideItems()
            self.adjustRange2HideItems()
            self.adjustRange3HideItems()
            self.buttonAdjustRange1.Show()
        elif  self.adjustObjectBox.GetStringSelection() == "Range (10)":
            self.adjustObject = 3
            self.adjustHeadingHideItems()
            self.adjustBearingHideItems()
            self.adjustRange1HideItems()
            self.adjustRange3HideItems()
            self.buttonAdjustRange2.Show()
        else:
            # self.adjustObjectBox.GetStringSelection() == "Range (100)"
            self.adjustObject = 4
            self.adjustHeadingHideItems()
            self.adjustBearingHideItems()
            self.adjustRange1HideItems()
            self.adjustRange2HideItems()
            self.buttonAdjustRange3.Show()



# =================================================================================================

    def ExitClick(self, event):
        print("--- Exit HSI board #1 test tool.")
        self.closeCOMMport(self.commPortID)
        frame.Close()


# =================================================================================================
#  COMMUNICATION  routine: send data
# =================================================================================================

    def sendData(self, address, subAddress, data):
        if self.commPortOpened == True:
            if address == self.HSIdevice1Address:
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
                        print("!!! COM port for HSI #1 is not open!")
                elif self.channelSelection == "USB":
                    if self.ComPort.isOpen():
                        print("... sendData to", self.commPortID, \
                              "subAddress", subAddress, "data", data)
                        self.ComPort.write(subAddress.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                    else:
                        print("!!! COM port for HSI #1 is not open!")
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
        if self.HeadingsettingValid == False:
            if self.HeadingEntryErrorShown == True:
                self.HeadingEntryErrorShown = False
                self.errorHeadingentry.Hide()
                self.startTimer(300)
            else:
                self.HeadingEntryErrorShown = True
                self.errorHeadingentry.Show()
                self.startTimer(500)
        else:
            if self.HeadingEntryErrorShown == True:
                self.HeadingEntryErrorShown = False
                self.errorHeadingentry.Hide()
            #self.startTimer(300)
        # ----
        if self.BearingsettingValid == False:
            if self.BearingEntryErrorShown == True:
                self.BearingEntryErrorShown = False
                self.errorBearingentry.Hide()
                self.startTimer(300)
            else:
                self.BearingEntryErrorShown = True
                self.errorBearingentry.Show()
                self.startTimer(500)
        else:
            if self.BearingEntryErrorShown == True:
                self.BearingEntryErrorShown = False
                self.errorBearingentry.Hide()
            #self.startTimer(300)
        # ----
        # ----
        if (self.simulateStatus == 1):
            # simulate setpoint update
            value = self.simulateRunningValue
            value = value + self.simulateStepValue
            if value >= 1024:
                value = value - 1024
            self.simulateRunningValue = value
            self.textSimulateShowSetpoint.SetValue(str(self.simulateRunningValue))
            # send setpoint to simulated HSI indicator
            command = int(value / 256)
            data = value - (command * 256)
            if self.simulateObject == 0:
                self.sendData(self.HSIdevice1Address, self.CMD_HDG_Q1 + command, data)
            elif self.simulateObject == 1:
                self.sendData(self.HSIdevice1Address, self.CMD_BRG_Q1 + command, data)
            else:
                self.sendData(self.HSIdevice1Address, self.CMD_MLS_1Q1 + command, data)
                self.sendData(self.HSIdevice1Address, self.CMD_MLS_2Q1 + command, data)
                self.sendData(self.HSIdevice1Address, self.CMD_MLS_3Q1 + command, data)
            self.startTimer(self.simulateUpdateTime)



###################################################################################################
class HSIFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "HSI #1 demonstrator", size=(660,395))
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