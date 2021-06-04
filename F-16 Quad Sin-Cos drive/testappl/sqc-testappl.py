import wx
import serial
import math

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
        self.smallFont  = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.errorImage = wx.Bitmap("error.gif")
        self.sadiImage  = wx.Bitmap("sadi.gif")
        self.gearsImage = wx.Bitmap("gears.gif")

        self.channelSelection         = "USB"
        self.QSCdeviceAddress         = 0x53
        self.QSChighestSubAddress     = 39
        self.commPortID               = ""
        self.previousCommPort         = ""
        self.commPortIDtoClose        = ""
        self.commPortOpened           = False                   # flag COMM port opened
        self.commPortValid            = False                   # only for "error sign" blinking
        self.prevDiagLEDmode          = "heartbeat"
        self.validateDOAdata          = True

        self.Rollsetting              = 0                       # default "North"
        self.maxRollDigital           = 1024
        self.maxRollDegrees           = 360
        self.maxRollValue             = self.maxRollDegrees
        self.RollsettingValid         = True
        self.RollEntryErrorShown      = False

        self.Pitchsetting             = 0                       # default "leveled"
        self.maxPitchDigital          = 1024
        self.maxPitchDegrees          = 360
        self.maxPitchValue            = self.maxPitchDegrees
        self.PitchsettingValid        = True
        self.PitchEntryErrorShown     = False

        self.adjustSADIselection      = ""

        self.simRollStartValue        = 0
        self.simRollStepSize          = 1
        self.simRollUpdateRate        = 1
        self.simPitchStartValue       = 0
        self.simPitchStepSize         = 1
        self.simPitchUpdateRate       = 1
        
        self.simulateRunningValue     = 0
        self.simulateStatus           = 0
        self.simulateFirstStart       = True

        self.rollPtCsinDefault        = 512
        self.rollPtCcosDefault        = 1023
        self.RollPtCsinsetting        = self.rollPtCsinDefault
        self.RollPtCcossetting        = self.rollPtCcosDefault
        self.pitchPtCsinDefault       = 512
        self.pitchPtCcosDefault       = 1023
        self.PitchPtCsinsetting        = self.pitchPtCsinDefault
        self.PitchPtCcossetting        = self.pitchPtCcosDefault
        self.rollPtCsettingValid      = True
        self.rollPtCEntryErrorShown   = False

        # QSC interface commands (from qsc-main.jal)

        self.CMD_SADI_ROLL0           = 0      # set SADI ROLL (base value)
        self.CMD_SADI_PITCH0          = 4      # set SADI PITCH (base value)
        self.CMD_OFFFLAG              = 8      # set SADI OFF flag
#
        self.CMD_SIN_1                = 9      # SADI *SINE* base
        self.CMD_COS_1                = 13     # SADI *COSINE* base
        self.CMD_LOAD                 = 17     # SADI setpoint identification
#
        self.CMD_DVC2OUT              = 18     # digital output for DEVICE 3/4
#
        self.CMD_P2C_SIN_R1           = 19     # PULL-TO-CAGE roll sin setpoint (base value)
        self.CMD_P2C_COS_R1           = 23     # PULL-TO-CAGE roll cos setpoint (base value)
        self.CMD_P2C_SIN_P1           = 27     # PULL-TO-CAGE pitch sin setpoint (base value)
        self.CMD_P2C_COS_P1           = 31     # PULL-TO-CAGE pitch cos setpoint (base value)
#
        self.CMD_DIAGMODE             = 37     # set diagnostic LED operating mode

        # Exit button
        self.buttonExit = wx.Button(self, label="Exit", pos=(500, 300), size=(100, 25))
        self.buttonExit.SetForegroundColour('#ff0000')
        self.buttonExit.Bind(wx.EVT_BUTTON, self.ExitClick)
        
        # ID myself
        self.IDline = wx.StaticText(self, label='QSC (Quad Sin/Cos) test tool  - V2.0  May 2020.', pos=(10, 330))
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
        self.rbox = wx.RadioBox(tabOne, label = ' Connection type ', pos = (30,40),
                                choices = radioButtonList, majorDimension = 1)
        self.rbox.Bind(wx.EVT_RADIOBOX,self.onConnectionBox)

        # display COM port selection
        wx.StaticBox(tabOne, label='COM ports', pos=(180, 40), size=(170, 120))
        textQSC = wx.StaticText(tabOne, label='QSC', pos=(194, 65))
        textQSC.SetFont(self.smallFont)
        textQSC.SetForegroundColour("#000000")
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
        wx.StaticBox(tabOne, label=' Diagnostics LED ', pos=(390, 40), size=(150, 55))
        diagLEDmodes = ['heartbeat', 'off', 'on', 'ACK', 'DOA']
        self.cbDiagLED = wx.ComboBox(tabOne, pos=(400, 60), size=(80, 25), choices=diagLEDmodes, style=wx.CB_READONLY)
        self.cbDiagLED.SetToolTip(wx.ToolTip("set LED diag mode"))
        self.cbDiagLED.SetValue('heartbeat')
        self.cbDiagLED.Bind(wx.EVT_COMBOBOX, self.OnSelectDiagLED)
        self.buttonDiagLED = wx.Button(tabOne, label="Set", pos=(490, 58), size=(40, 25))
        self.buttonDiagLED.SetBackgroundColour('#cccccc')
        self.buttonDiagLED.SetForegroundColour('#000000')
        self.buttonDiagLED.Bind(wx.EVT_BUTTON, self.onSendDiagLED)

        # free available output
        wx.StaticBox(tabOne, label=' User output ', pos=(390, 120), size=(150, 60))
        self.toggleOutput = wx.CheckBox(tabOne, label='User output', pos=(400, 142), size=(100, 25))
        self.toggleOutput.SetValue(False)
        self.toggleOutput.SetToolTip(wx.ToolTip("toggle user-defined output"))
        self.toggleOutput.Bind(wx.EVT_CHECKBOX, self.toggleOutputCheckbox)


#-- TAB #2  SADI roll/pitch & OFF vane  -----------------------------------------------------------
        tabTwo = TabPanel(self)
        self.AddPage(tabTwo, "SADI control")
        self.sadiAccent = wx.StaticBitmap(tabTwo, -1, self.sadiImage)
        self.sadiAccent.SetPosition((420, 20))

        # Roll setpoint entry
        rollPosX = 30
        rollPosY = 25
        wx.StaticBox(tabTwo, label=' Roll setpoint ', pos=(rollPosX, rollPosY), size=(365, 90))
        setpointOptionList = ['degrees', 'digital']
        self.rollSetpointOptionBox = wx.RadioBox(tabTwo, label = '', pos=(rollPosX+10,rollPosY+15),
                                                 choices = setpointOptionList, majorDimension = 1)
        self.rollDimension = "degrees"
        self.rollSetpointOptionBox.Bind(wx.EVT_RADIOBOX,self.onRollSetpointOption)
        self.rollEntry = wx.TextCtrl(tabTwo, value="0", pos=(rollPosX+104, rollPosY+35), size=(60, 25))

        self.textRollValidValuesDigital = wx.StaticText(tabTwo, label='(0 ... 1024)', pos=(rollPosX+107, rollPosY+62))
        self.textRollValidValuesDigital.SetFont(self.smallFont)
        self.textRollValidValuesDigital.Hide()
        self.textRollValidValuesDegrees = wx.StaticText(tabTwo, label='(0 ... 360)', pos=(rollPosX+110, rollPosY+62))
        self.textRollValidValuesDegrees.SetFont(self.smallFont)

        self.buttonRollEntrySet = wx.Button(tabTwo, label="Set", pos=(rollPosX+195, rollPosY+35), size=(60, 25))
        self.buttonRollEntrySet.SetToolTip(wx.ToolTip("set Roll angle"))
        self.buttonRollEntrySet.SetBackgroundColour('#99ccff')
        self.buttonRollEntrySet.SetForegroundColour('#000000')
        self.buttonRollEntrySet.Bind(wx.EVT_BUTTON, self.RollEntrySet)
        self.errorRollEntry = wx.StaticBitmap(tabTwo, -1, self.errorImage)
        self.errorRollEntry.SetPosition((rollPosX+168, rollPosY+35))
        self.errorRollEntry.Hide()

        # Roll increment/decrement buttons
        self.buttonRolldec = wx.Button(tabTwo, label="-10", pos=(rollPosX+270, rollPosY+35), size=(40, 24))
        self.buttonRollinc = wx.Button(tabTwo, label="+10", pos=(rollPosX+315, rollPosY+35), size=(40, 24))
        self.buttonRollinc.SetBackgroundColour('#CC3333')
        self.buttonRollinc.SetForegroundColour('#ffffff')
        self.buttonRolldec.SetBackgroundColour('#CC3333')
        self.buttonRolldec.SetForegroundColour('#ffffff')
        self.buttonRollinc.Bind(wx.EVT_BUTTON, self.Rollincrement)
        self.buttonRolldec.Bind(wx.EVT_BUTTON, self.Rolldecrement)

        # Pitch setpoint entry
        pitchPosX = 30
        pitchPosY = 145
        wx.StaticBox(tabTwo, label=' Pitch setpoint ', pos=(pitchPosX, pitchPosY), size=(365, 90))
        self.pitchSetpointOptionBox = wx.RadioBox(tabTwo, label = '', pos=(pitchPosX+10,pitchPosY+15),
                                                  choices = setpointOptionList, majorDimension = 1)
        self.pitchDimension = "degrees"
        self.pitchSetpointOptionBox.Bind(wx.EVT_RADIOBOX,self.onPitchSetpointOption)
        self.pitchEntry = wx.TextCtrl(tabTwo, value="0", pos=(pitchPosX+104, pitchPosY+35), size=(60, 25))

        self.textPitchValidValuesDigital = wx.StaticText(tabTwo, label='(0 ... 1024)', pos=(pitchPosX+107, pitchPosY+62))
        self.textPitchValidValuesDigital.SetFont(self.smallFont)
        self.textPitchValidValuesDigital.Hide()
        self.textPitchValidValuesDegrees = wx.StaticText(tabTwo, label='(0 ... 360)', pos=(pitchPosX+110, pitchPosY+62))
        self.textPitchValidValuesDegrees.SetFont(self.smallFont)

        self.buttonPitchEntrySet = wx.Button(tabTwo, label="Set", pos=(pitchPosX+195, pitchPosY+35), size=(60, 25))
        self.buttonPitchEntrySet.SetToolTip(wx.ToolTip("set Pitch angle"))
        self.buttonPitchEntrySet.SetBackgroundColour('#99ccff')
        self.buttonPitchEntrySet.SetForegroundColour('#000000')
        self.buttonPitchEntrySet.Bind(wx.EVT_BUTTON, self.PitchEntrySet)
        self.errorPitchEntry = wx.StaticBitmap(tabTwo, -1, self.errorImage)
        self.errorPitchEntry.SetPosition((pitchPosX+168, pitchPosY+35))
        self.errorPitchEntry.Hide()

        # Pitch increment/decrement buttons
        self.buttonPitchdec = wx.Button(tabTwo, label="-10", pos=(pitchPosX+270, pitchPosY+35), size=(40, 24))
        self.buttonPitchinc = wx.Button(tabTwo, label="+10", pos=(pitchPosX+315, pitchPosY+35), size=(40, 24))
        self.buttonPitchinc.SetBackgroundColour('#CC3333')
        self.buttonPitchinc.SetForegroundColour('#ffffff')
        self.buttonPitchdec.SetBackgroundColour('#CC3333')
        self.buttonPitchdec.SetForegroundColour('#ffffff')
        self.buttonPitchinc.Bind(wx.EVT_BUTTON, self.Pitchincrement)
        self.buttonPitchdec.Bind(wx.EVT_BUTTON, self.Pitchdecrement)

        # OFF flag button
        self.textOFFflagentry  = wx.StaticText(tabTwo, label='OFF flag', pos=(420, 220))
        self.buttonOFFflag = wx.Button(tabTwo, label="  OFF ", pos=(480, 215), size=(60, 25))
        self.buttonOFFflag.SetBackgroundColour('#F48C42')
        self.buttonOFFflag.SetForegroundColour('#000000')
        self.buttonOFFflag.Bind(wx.EVT_BUTTON, self.OFFflag)


#-- TAB #3  SADI SIMULATION  ----------------------------------------------------------------------
        tabThree = TabPanel(self)
        self.AddPage(tabThree, "SADI simulate")
        self.sadiAccent = wx.StaticBitmap(tabThree, -1, self.sadiImage)
        self.sadiAccent.SetPosition((420, 20))

        simulateButtonList = ['Roll', 'Pitch']
        self.simulateObjectBox = wx.RadioBox(tabThree, label = ' Simulate axis ', pos = (20,30),
                                             choices = simulateButtonList, majorDimension = 1)
        self.simulateObjectBox.Bind(wx.EVT_RADIOBOX,self.onSimulateObject)
        self.simulateObject = "Roll"

        wx.StaticBox(tabThree, label=' Step increment', pos=(20, 135), size=(115, 55))
        simulateStepList = ['1', '2', '5', '10', '20' ]
        self.cbSimulateStepSelection = wx.ComboBox(tabThree, pos=(30, 155), size=(75, 25), value=simulateStepList[0],
                                                   choices=simulateStepList, style=wx.CB_READONLY)
        self.cbSimulateStepSelection.SetToolTip(wx.ToolTip("set step size"))
        self.cbSimulateStepSelection.Bind(wx.EVT_COMBOBOX, self.OnSelectSimStepSize)

        wx.StaticBox(tabThree, label=' Update rate', pos=(20, 200), size=(115, 55))
        simulateUpdateList = ['200 ms', '400 ms', '600 ms', '800 ms', '1000 ms' ]
        self.cbSimulateRateSelection = wx.ComboBox(tabThree, pos=(30, 220), size=(75, 25), value=simulateUpdateList[1],
                                                   choices=simulateUpdateList, style=wx.CB_READONLY)
        self.cbSimulateRateSelection.SetToolTip(wx.ToolTip("set update rate"))
        self.cbSimulateRateSelection.Bind(wx.EVT_COMBOBOX, self.OnSelectSimUpdateRate)

        wx.StaticBox(tabThree, label=' Start setpoint', pos=(150, 30), size=(195, 80))
        self.simulateStartEntry = wx.TextCtrl(tabThree, value=str(self.simRollStartValue), pos=(165, 60), size=(60, 25))
        textSimulateValidValues = wx.StaticText(tabThree, label='(0 ... 1023)', pos=(168, 87))
        textSimulateValidValues.SetFont(self.smallFont)
        self.buttonsimulateStartEntrySet = wx.Button(tabThree, label="Set", pos=(265, 60), size=(60, 25))
        self.buttonsimulateStartEntrySet.SetToolTip(wx.ToolTip("set start value"))
        self.buttonsimulateStartEntrySet.SetBackgroundColour('#99ccff')
        self.buttonsimulateStartEntrySet.SetForegroundColour('#000000')
        self.buttonsimulateStartEntrySet.Bind(wx.EVT_BUTTON, self.simulateStartEntrySet)
        self.errorsimulateStartEntry = wx.StaticBitmap(tabThree, -1, self.errorImage)
        self.errorsimulateStartEntry.SetPosition((230, 60))
        self.errorsimulateStartEntry.Hide()

        wx.StaticBox(tabThree, label=' Simulate indication', pos=(150, 135), size=(195, 100))
        simulateDigitFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.textSimulateShowSetpoint = wx.TextCtrl(tabThree, value=str(self.simRollStartValue),
                                                    style=wx.TE_READONLY | wx.TE_CENTRE, pos=(210, 160), size=(80, 25))
        self.textSimulateShowSetpoint.SetFont(simulateDigitFont)
        self.textSimulateShowSetpoint.SetBackgroundColour('#eeeeee')
        self.textSimulateShowSetpoint.SetForegroundColour('#0000ff')

        self.simulateStartButton = wx.Button(tabThree, label="Start", pos=(180, 195), size=(60, 25))
        self.simulateStartButton.SetToolTip(wx.ToolTip("start simulation"))
        self.simulateStartButton.SetBackgroundColour('#99ccff')
        self.simulateStartButton.SetForegroundColour('#000000')
        self.simulateStartButton.Bind(wx.EVT_BUTTON, self.simulateStartSimulation)
        self.simulateStopButton = wx.Button(tabThree, label="Stop", pos=(260, 195), size=(60, 25))
        self.simulateStopButton.SetToolTip(wx.ToolTip("stop simulation"))
        self.simulateStopButton.SetBackgroundColour('#eeeeee')
        self.simulateStopButton.SetForegroundColour('#000000')
        self.simulateStopButton.Bind(wx.EVT_BUTTON, self.simulateStopSimulation)


#-- TAB #4  QSC ADJUSTMENT  ----------------------------------------------------------------------
        tabFour = TabPanel(self)
        self.AddPage(tabFour, "QSC Pull-to-Cage")
        self.gearsAccent = wx.StaticBitmap(tabFour, -1, self.gearsImage)
        self.gearsAccent.SetPosition((420, 20))

        # Roll Pull-to-Cage setpoint entry
        rollPtCPosX = 30
        rollPtCPosY = 25
        wx.StaticBox(tabFour, label=' Roll PtC setpoint ', pos=(rollPtCPosX, rollPtCPosY), size=(365, 100))

        textRollSin = wx.StaticText(tabFour, label='Sine', pos=(rollPtCPosX+20, rollPtCPosY+28))
        textRollCos = wx.StaticText(tabFour, label='Cosine', pos=(rollPtCPosX+20, rollPtCPosY+67))
        self.rollPtCsinEntry = wx.TextCtrl(tabFour, value=str(self.rollPtCsinDefault), pos=(rollPtCPosX+84, rollPtCPosY+25), size=(60, 23))
        self.rollPtCcosEntry = wx.TextCtrl(tabFour, value=str(self.rollPtCcosDefault), pos=(rollPtCPosX+84, rollPtCPosY+64), size=(60, 23))

        self.textRollPtCValidValues = wx.StaticText(tabFour, label='(0 ... 1024)', pos=(rollPtCPosX+87, rollPtCPosY+48))
        self.textRollPtCValidValues.SetFont(self.smallFont)

        self.buttonRollPtCEntrySet = wx.Button(tabFour, label="Set", pos=(rollPtCPosX+175, rollPtCPosY+42), size=(60, 25))
        self.buttonRollPtCEntrySet.SetToolTip(wx.ToolTip("set Roll Pull-to-Cage angle"))
        self.buttonRollPtCEntrySet.SetBackgroundColour('#99ccff')
        self.buttonRollPtCEntrySet.SetForegroundColour('#000000')
        self.buttonRollPtCEntrySet.Bind(wx.EVT_BUTTON, self.RollPtCEntrySet)
        self.errorRollPtCEntry = wx.StaticBitmap(tabFour, -1, self.errorImage)
        self.errorRollPtCEntry.SetPosition((rollPtCPosX+148, rollPtCPosY+42))
        self.errorRollPtCEntry.Hide()

        self.rollPtCdefaultsSet = wx.Button(tabFour, label="Load defaults", pos=(rollPtCPosX+250, rollPtCPosY+42), size=(95, 25))
        self.rollPtCdefaultsSet.SetToolTip(wx.ToolTip("load Roll PtC sin/cos defaults"))
        self.rollPtCdefaultsSet.SetBackgroundColour('#ffff00')
        self.rollPtCdefaultsSet.SetForegroundColour('#000000')
        self.rollPtCdefaultsSet.Bind(wx.EVT_BUTTON, self.loadRollPtCdefaults)

        # Pitch Pull-to-Cage setpoint entry
        pitchPtCPosX = 30
        pitchPtCPosY = 145
        wx.StaticBox(tabFour, label=' Pitch PtC setpoint ', pos=(pitchPtCPosX, pitchPtCPosY), size=(365, 100))

        textPitchSin = wx.StaticText(tabFour, label='Sine', pos=(pitchPtCPosX+20, pitchPtCPosY+28))
        textPitchCos = wx.StaticText(tabFour, label='Cosine', pos=(pitchPtCPosX+20, pitchPtCPosY+67))
        self.pitchPtCsinEntry = wx.TextCtrl(tabFour, value=str(self.pitchPtCsinDefault), pos=(pitchPtCPosX+84, pitchPtCPosY+25), size=(60, 23))
        self.pitchPtCcosEntry = wx.TextCtrl(tabFour, value=str(self.pitchPtCcosDefault), pos=(pitchPtCPosX+84, pitchPtCPosY+64), size=(60, 23))

        self.textPitchPtCValidValues = wx.StaticText(tabFour, label='(0 ... 1024)', pos=(pitchPtCPosX+87, pitchPtCPosY+48))
        self.textPitchPtCValidValues.SetFont(self.smallFont)

        self.buttonPitchPtCEntrySet = wx.Button(tabFour, label="Set", pos=(pitchPtCPosX+175, pitchPtCPosY+42), size=(60, 25))
        self.buttonPitchPtCEntrySet.SetToolTip(wx.ToolTip("set Pitch Pull-to-Cage angle"))
        self.buttonPitchPtCEntrySet.SetBackgroundColour('#99ccff')
        self.buttonPitchPtCEntrySet.SetForegroundColour('#000000')
        self.buttonPitchPtCEntrySet.Bind(wx.EVT_BUTTON, self.PitchPtCEntrySet)
        self.errorPitchPtCEntry = wx.StaticBitmap(tabFour, -1, self.errorImage)
        self.errorPitchPtCEntry.SetPosition((pitchPtCPosX+148, pitchPtCPosY+42))
        self.errorPitchPtCEntry.Hide()

        self.pitchPtCdefaultsSet = wx.Button(tabFour, label="Load defaults", pos=(pitchPtCPosX+250, pitchPtCPosY+42), size=(95, 25))
        self.pitchPtCdefaultsSet.SetToolTip(wx.ToolTip("load Pitch PtC sin/cos defaults"))
        self.pitchPtCdefaultsSet.SetBackgroundColour('#ffff00')
        self.pitchPtCdefaultsSet.SetForegroundColour('#000000')
        self.pitchPtCdefaultsSet.Bind(wx.EVT_BUTTON, self.loadPitchPtCdefaults)


#-- TAB #5  QSC ADJUSTMENT  ----------------------------------------------------------------------
        tabFive = TabPanel(self)
        self.AddPage(tabFive, "QSC adjustment")
        self.gearsAccent = wx.StaticBitmap(tabFive, -1, self.gearsImage)
        self.gearsAccent.SetPosition((420, 20))

        # adjustment entry fields
        adjustSelPosX = 30
        adjustSelPosY = 25
        wx.StaticBox(tabFive, label=' Sin / Cos pair ', pos=(adjustSelPosX, adjustSelPosY), size=(365, 60))
        sincosPairs = ['Roll', 'Pitch', 'Device 3', 'Device 4']
        self.adjustSADIchannel = wx.ComboBox(tabFive, pos=(adjustSelPosX+20, adjustSelPosY+25), size=(80, 25),
                                             choices=sincosPairs, style=wx.CB_READONLY)
        self.adjustSADIchannel.SetToolTip(wx.ToolTip("select Sin/Cos pair"))
        self.adjustSADIchannel.Bind(wx.EVT_COMBOBOX, self.onAdjustSADIchannelOption)
        self.errorAdjustSinCos = wx.StaticBitmap(tabFive, -1, self.errorImage)
        self.errorAdjustSinCos.SetPosition((adjustSelPosX+105, adjustSelPosY+24))
        self.errorAdjustSinCos.Hide()

        adjustPosX = 30
        adjustPosY = 110
        wx.StaticBox(tabFive, label=' Adjustment options ', pos=(adjustPosX, adjustPosY), size=(365, 140))
        radioAdjustList = ['min', 'zero', 'max', 'var']
        self.radioAdjustbox = wx.RadioBox(tabFive, pos = (adjustPosX+20, adjustPosY+18),
                                         choices = radioAdjustList, majorDimension = 1)
        self.radioAdjustbox.Bind(wx.EVT_RADIOBOX, self.onRadioAdjustBox)
        self.slider = wx.Slider(tabFive, value=512, minValue=0, maxValue=1023,
                                pos=(adjustPosX+100, adjustPosY+80), size=(250, -1), style=wx.SL_HORIZONTAL)

        self.slider.Bind(wx.EVT_SLIDER, self.OnSliderScroll)
        self.slider.Hide()
        self.textSlider11 = wx.StaticText(tabFive, label='0',    pos=(adjustPosX+107, adjustPosY+102))
        self.textSlider12 = wx.StaticText(tabFive, label='512',  pos=(adjustPosX+216, adjustPosY+102))
        self.textSlider13 = wx.StaticText(tabFive, label='1023', pos=(adjustPosX+330, adjustPosY+102))
        self.textSlider21 = wx.StaticText(tabFive, label='-10',  pos=(adjustPosX+100, adjustPosY+113))
        self.textSlider22 = wx.StaticText(tabFive, label='0',    pos=(adjustPosX+223, adjustPosY+113))
        self.textSlider23 = wx.StaticText(tabFive, label='+10',  pos=(adjustPosX+333, adjustPosY+113))
        self.textSlider11.SetFont(self.smallFont)
        self.textSlider12.SetFont(self.smallFont)
        self.textSlider13.SetFont(self.smallFont)
        self.textSlider21.SetFont(self.smallFont)
        self.textSlider22.SetFont(self.smallFont)
        self.textSlider23.SetFont(self.smallFont)
        self.textSlider11.SetForegroundColour("#000000")
        self.textSlider12.SetForegroundColour("#000000")
        self.textSlider13.SetForegroundColour("#000000")
        self.textSlider21.SetForegroundColour("#0000FF")
        self.textSlider22.SetForegroundColour("#0000FF")
        self.textSlider23.SetForegroundColour("#0000FF")
        self.textSlider11.Hide()
        self.textSlider12.Hide()
        self.textSlider13.Hide()
        self.textSlider21.Hide()
        self.textSlider22.Hide()
        self.textSlider23.Hide()

        self.textSliderValue = wx.StaticText(tabFive, label='512', pos=(adjustPosX+245, adjustPosY+30))
        self.textSliderValue.SetFont(self.smallFont)
        self.textSliderValue.SetForegroundColour("#FF0000")
        self.textSliderValue.Hide()
        self.buttonAdjustSet = wx.Button(tabFive, label="Set", pos=(adjustPosX+280, adjustPosY+25), size=(60, 25))
        self.buttonAdjustSet.SetToolTip(wx.ToolTip("set value"))
        self.buttonAdjustSet.SetBackgroundColour('#99ccff')
        self.buttonAdjustSet.SetForegroundColour('#000000')
        self.buttonAdjustSet.Bind(wx.EVT_BUTTON, self.sendAdjustSet)


#-- TAB #6  Raw data  -----------------------------------------------------------------------------
        tabSix = TabPanel(self)
        self.AddPage(tabSix, "Raw data")
        self.rawDataAccent = wx.StaticBitmap(tabSix, -1, self.gearsImage)
        self.rawDataAccent.SetPosition((420, 20))

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
        self.deviceAddressEntry.Value = str(self.QSCdeviceAddress)
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

        # default communication is USB
        self.textDeviceAddress.Hide()
        self.deviceAddressEntry.Hide()
        self.allowAll.Hide()


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
        self.deviceAddressEntry.Value = str(self.QSCdeviceAddress)
        self.buttonAdvancedSend.SetBackgroundColour('#99ccff')
        self.errorDeviceAddress.Hide()
        if self.rbox.GetStringSelection() == "PHCC":
            self.channelSelection = "PHCC"
            self.textDeviceAddress.Show()
            self.deviceAddressEntry.Show()
            self.allowAll.Show()
        else:
            self.channelSelection = "USB"
            self.textDeviceAddress.Hide()
            self.deviceAddressEntry.Hide()
            self.allowAll.Hide()
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
        # DIAGLED_OFF       = 0   -- DIAG LED mode :: always OFF
        # DIAGLED_ON        = 1   -- DIAG LED mode :: always ON
        # DIAGLED_HEARTBEAT = 2   -- DIAG LED flash at heartbeat rate
        # DIAGLED_MSG_ACK   = 3   -- DIAG LED ON/OFF per received message

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
        self.sendData(self.QSCdeviceAddress, self.CMD_DIAGMODE, self.DiagLEDdatabyte)
        print("[i] Diagnostic LED function changed")
        if (self.commPortOpened == True):
            # update "Set" button color only to grey if data was actually sent!
            self.buttonDiagLED.SetBackgroundColour('#cccccc')


    def toggleOutputCheckbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.sendData(self.QSCdeviceAddress, self.CMD_DVC2OUT, 1)
            print("[i] user output activated")
        else:
            self.sendData(self.QSCdeviceAddress, self.CMD_DVC2OUT, 0)
            print("[i] user output de-activated")


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

    def onRollSetpointOption(self, event):
        if self.rollSetpointOptionBox.GetStringSelection() == "degrees":
            self.rollDimension = "degrees"
            self.maxRollValue = self.maxRollDegrees
            self.textRollValidValuesDigital.Hide()
            self.textRollValidValuesDegrees.Show()
        else:
            self.rollDimension = "digital"
            self.maxRollValue = self.maxRollDigital
            self.textRollValidValuesDegrees.Hide()
            self.textRollValidValuesDigital.Show()
        print("[i] Roll setpoint dimension =", self.rollDimension)

    def onPitchSetpointOption(self, event):
        if self.pitchSetpointOptionBox.GetStringSelection() == "degrees":
            self.pitchDimension = "degrees"
            self.maxPitchValue = self.maxPitchDegrees
            self.textPitchValidValuesDigital.Hide()
            self.textPitchValidValuesDegrees.Show()
        else:
            self.pitchDimension = "digital"
            self.maxPitchValue = self.maxPitchDigital
            self.textPitchValidValuesDegrees.Hide()
            self.textPitchValidValuesDigital.Show()
        print("[i] Pitch setpoint dimension =", self.pitchDimension)

    def RollEntrySet(self, event):
        Rollvalue = self.rollEntry.GetValue()
        value = self.str2int(Rollvalue)
        if value > self.maxRollValue:
            self.RollsettingValid = False
            self.RollEntryErrorShown = True
            self.errorRollEntry.Show()
        else:
            self.Rollsetting = value
            self.RollsettingValid = True
            self.RollEntryErrorShown = False
            self.errorRollEntry.Hide()
            # create correct command subaddress and data
            if value == self.maxRollValue:
                value = 0
# $$$$$$
            if self.rollDimension == "degrees":
                value = int((math.sin( value * 2.0 * 3.14159 / 1024.0 ) ) * 1024.0)
                print ("sine value = ", value)
# $$$$$$
            command = int(value / 256)
            data = value - (command * 256)
            self.sendData(self.QSCdeviceAddress, self.CMD_SADI_ROLL0 + command, data)
            print("[i] roll setpoint updated")

    def Rollincrement(self, e):
        self.Rollsetting = self.Rollsetting + 10
        if self.Rollsetting >= self.maxRollValue:
            self.Rollsetting = self.Rollsetting - self.maxRollValue
        self.RollsettingValid = True
        self.RollEntryErrorShown = False
        self.errorRollEntry.Hide()
        self.rollEntry.SetValue(str(self.Rollsetting))
        # send to Roll
        value = self.Rollsetting
        if value == self.maxRollValue:
            value = 0
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.QSCdeviceAddress, self.CMD_SADI_ROLL0 + command, data)
        print("[i] roll setpoint updated")


    def Rolldecrement(self, e):
        if self.Rollsetting >= 10:
            self.Rollsetting = self.Rollsetting - 10
        else:
            diff = 10 - self.Rollsetting
            self.Rollsetting = self.maxRollValue - diff
        self.RollsettingValid = True
        self.RollEntryErrorShown = False
        self.errorRollEntry.Hide()
        self.rollEntry.SetValue(str(self.Rollsetting))
        # send to Roll
        value = self.Rollsetting
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.QSCdeviceAddress, self.CMD_SADI_ROLL0 + command, data)
        print("[i] roll setpoint updated")

    def PitchEntrySet(self, event):
        Pitchvalue = self.pitchEntry.GetValue()
        value = self.str2int(Pitchvalue)
        if value > self.maxPitchValue:
            self.PitchsettingValid = False
            self.PitchEntryErrorShown = True
            self.errorPitchEntry.Show()
        else:
            self.Pitchsetting = value
            self.PitchsettingValid = True
            self.PitchEntryErrorShown = False
            self.errorPitchEntry.Hide()
            # create correct command subaddress and data
            if value == self.maxPitchValue:
                value = 0
            command = int(value / 256)
            data = value - (command * 256)
            self.sendData(self.QSCdeviceAddress, self.CMD_SADI_PITCH0 + command, data)
            print("[i] pitch setpoint updated")

    def Pitchincrement(self, e):
        self.Pitchsetting = self.Pitchsetting + 10
        if self.Pitchsetting >= self.maxPitchValue:
            self.Pitchsetting = self.Pitchsetting - self.maxPitchValue
        self.PitchsettingValid = True
        self.PitchEntryErrorShown = False
        self.errorPitchEntry.Hide()
        self.pitchEntry.SetValue(str(self.Pitchsetting))
        # send to Pitch
        value = self.Pitchsetting
        if value == self.maxPitchValue:
            value = 0
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.QSCdeviceAddress, self.CMD_SADI_PITCH0 + command, data)
        print("[i] pitch setpoint updated")


    def Pitchdecrement(self, e):
        if self.Pitchsetting >= 10:
            self.Pitchsetting = self.Pitchsetting - 10
        else:
            diff = 10 - self.Pitchsetting
            self.Pitchsetting = self.maxPitchValue - diff
        self.PitchsettingValid = True
        self.PitchEntryErrorShown = False
        self.errorPitchEntry.Hide()
        self.pitchEntry.SetValue(str(self.Pitchsetting))
        # send to Pitch
        value = self.Pitchsetting
        command = int(value / 256)
        data = value - (command * 256)
        self.sendData(self.QSCdeviceAddress, self.CMD_SADI_PITCH0 + command, data)
        print("[i] pitch setpoint updated")


    def OFFflag(self, event):
        button = event.GetEventObject()
        buttonName = button.GetLabel()
        if buttonName == "  OFF ":
            button.SetLabel("hidden")
            self.buttonOFFflag.SetBackgroundColour('#AAAAAA')
            self.buttonOFFflag.SetForegroundColour('#FFFFFF')
            self.sendData(self.QSCdeviceAddress, self.CMD_OFFFLAG, 1)
        else:
            button.SetLabel("  OFF ")
            self.buttonOFFflag.SetBackgroundColour('#F48C42')
            self.buttonOFFflag.SetForegroundColour('#000000')
            self.sendData(self.QSCdeviceAddress, self.CMD_OFFFLAG, 0)


# =================================================================================================

    def onSimulateObject(self, e):
        self.buttonsimulateStartEntrySet.SetBackgroundColour('#99ccff')
        self.simulateStartButton.SetBackgroundColour('#99ccff')
        self.simulateStopButton.SetBackgroundColour('#eeeeee')
        self.simulateStatus = 0
        self.simulateFirstStart = True
        if self.simulateObjectBox.GetStringSelection() == "Roll":
            self.simulateObject = 0
            self.simulateStartEntry.SetValue(str(self.simRollStartValue))
            if self.simRollStartValue > (self.maxRollDigital - 1):
                self.errorsimulateStartEntry.Show()
                self.textSimulateShowSetpoint.SetValue("0")
            else:
                self.errorsimulateStartEntry.Hide()
                self.textSimulateShowSetpoint.SetValue(str(self.simRollStartValue))
        else:
            self.simulateObject = 2
            self.simulateStartEntry.SetValue(str(self.simPitchStartValue))
            if self.simPitchStartValue > (self.maxPitchDigital - 1):
                self.errorsimulateStartEntry.Show()
                self.textSimulateShowSetpoint.SetValue("0")
            else:
                self.errorsimulateStartEntry.Hide()
                self.textSimulateShowSetpoint.SetValue(str(self.simPitchStartValue))


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
                    # set roll start value
                    self.simRollStartValue = value
                    if value == self.maxRollDigital:
                        value = 0
                    command = int(value / 256)
                    data = value - (command * 256)
                    self.sendData(self.QSCdeviceAddress, self.CMD_SADI_ROLL0 + command, data)
                    print("SIM roll start set")
                else:
                    # set pitch start value
                    self.simPitchStartValue = value
                    if value == self.maxPitchDigital:
                        value = 0
                    command = int(value / 256)
                    data = value - (command * 256)
                    self.sendData(self.QSCdeviceAddress, self.CMD_SADI_PITCH0 + command, data)
                    print("SIM pitch start set")


    def simulateStartSimulation(self, e):
        if self.simulateStatus == 0:
            if self.simulateFirstStart == True:
                # load start value
                if self.simulateObject == 0:
                    value = self.simRollStartValue
                else:
                    value = self.simPitchStartValue
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

    def loadRollPtCdefaults(self, event):
        self.rollPtCsinEntry.SetValue(str(self.rollPtCsinDefault))
        self.rollPtCcosEntry.SetValue(str(self.rollPtCcosDefault))

    def loadPitchPtCdefaults(self, event):
        self.pitchPtCsinEntry.SetValue(str(self.pitchPtCsinDefault))
        self.pitchPtCcosEntry.SetValue(str(self.pitchPtCcosDefault))

    def RollPtCEntrySet(self, event):
        rollSinValue = self.rollPtCsinEntry.GetValue()
        rollCosValue = self.rollPtCcosEntry.GetValue()
        sinValue = self.str2int(rollSinValue)
        cosValue = self.str2int(rollCosValue)
        if ((sinValue > self.maxRollDigital) or (cosValue > self.maxRollDigital)):
            self.rollPtCsettingValid = False
            self.rollPtCEntryErrorShown = True
            self.errorRollPtCEntry.Show()
        else:
            self.RollPtCsinsetting = sinValue
            self.RollPtCcossetting = cosValue
            self.rollPtCsettingValid = True
            self.rollPtCEntryErrorShown = False
            self.errorRollPtCEntry.Hide()
            # create correct command subaddress and data
            if self.RollPtCsinsetting == self.maxRollDigital:
                self.RollPtCsinsetting = 0
            if self.RollPtCcossetting == self.maxRollDigital:
                self.RollPtCcossetting = 0
            sinCommand = int(self.RollPtCsinsetting / 256)
            cosCommand = int(self.RollPtCcossetting / 256)
            sinData = self.RollPtCsinsetting - (sinCommand * 256)
            cosData = self.RollPtCcossetting - (cosCommand * 256)
            self.sendData(self.QSCdeviceAddress, self.CMD_P2C_SIN_R1 + sinCommand, sinData)
            self.sendData(self.QSCdeviceAddress, self.CMD_P2C_COS_R1 + cosCommand, cosData)
            print("[i] Roll Pull-to-Cage sin/cos setpoint updated")

    def PitchPtCEntrySet(self, event):
        pitchSinValue = self.pitchPtCsinEntry.GetValue()
        pitchCosValue = self.pitchPtCcosEntry.GetValue()
        sinValue = self.str2int(pitchSinValue)
        cosValue = self.str2int(pitchCosValue)
        if ((sinValue > self.maxPitchDigital) or (cosValue > self.maxPitchDigital)):
            self.pitchPtCsettingValid = False
            self.pitchPtCEntryErrorShown = True
            self.errorPitchPtCEntry.Show()
        else:
            self.PitchPtCsinsetting = sinValue
            self.PitchPtCcossetting = cosValue
            self.pitchPtCsettingValid = True
            self.pitchPtCEntryErrorShown = False
            self.errorPitchPtCEntry.Hide()
            # create correct command subaddress and data
            if self.PitchPtCsinsetting == self.maxPitchDigital:
                self.PitchPtCsinsetting = 0
            if self.PitchPtCcossetting == self.maxPitchDigital:
                self.PitchPtCcossetting = 0
            sinCommand = int(self.PitchPtCsinsetting / 256)
            cosCommand = int(self.PitchPtCcossetting / 256)
            sinData = self.PitchPtCsinsetting - (sinCommand * 256)
            cosData = self.PitchPtCcossetting - (cosCommand * 256)
            self.sendData(self.QSCdeviceAddress, self.CMD_P2C_SIN_P1 + sinCommand, sinData)
            self.sendData(self.QSCdeviceAddress, self.CMD_P2C_COS_P1 + cosCommand, cosData)
            print("[i] Pitch Pull-to-Cage sin/cos setpoint updated")


# =================================================================================================

    def onAdjustSADIchannelOption(self, event):
        if self.adjustSADIchannel.GetStringSelection() == "Roll":
            self.adjustSADIselection = "Roll"
        elif self.adjustSADIchannel.GetStringSelection() == "Pitch":
            self.adjustSADIselection = "Pitch"
        elif self.adjustSADIchannel.GetStringSelection() == "Device 3":
            self.adjustSADIselection = "Device 3"
        else:
            self.adjustSADIselection = "Device 4"
        self.errorAdjustSinCos.Hide()
        print("[i] Sin/Cos pair adjustment for ", self.adjustSADIselection)

    def hideAdjustSliderItems(self):
        self.slider.Hide()
        self.textSliderValue.Hide()
        self.textSlider11.Hide()
        self.textSlider12.Hide()
        self.textSlider13.Hide()
        self.textSlider21.Hide()
        self.textSlider22.Hide()
        self.textSlider23.Hide()

    def onRadioAdjustBox(self,e):
        if self.radioAdjustbox.GetStringSelection() == "min":
            self.hideAdjustSliderItems()
        elif self.radioAdjustbox.GetStringSelection() == "max":
            self.hideAdjustSliderItems()
        elif self.radioAdjustbox.GetStringSelection() == "zero":
            self.hideAdjustSliderItems()
        else:
            self.slider.Show()
            self.textSliderValue.Show()
            self.textSlider11.Show()
            self.textSlider12.Show()
            self.textSlider13.Show()
            self.textSlider21.Show()
            self.textSlider22.Show()
            self.textSlider23.Show()

    def OnSliderScroll(self, e):
        obj = e.GetEventObject()
        self.sliderValue = obj.GetValue()
        self.textSliderValue.Label = str(self.sliderValue)
        self.textSliderValue.Show()

    def sendAdjustSet(self, e):
        sinCosPair = self.adjustSADIchannel.GetValue()
        if sinCosPair == "":
            self.errorAdjustSinCos.Show()
        else:
            self.errorAdjustSinCos.Hide()
            if self.radioAdjustbox.GetStringSelection() == "min":
                value = 0
                self.slider.SetValue(0)
                self.textSliderValue.Label = "0"
            elif self.radioAdjustbox.GetStringSelection() == "zero":
                value = 512
                self.slider.SetValue(512)
                self.textSliderValue.Label = "512"
            elif self.radioAdjustbox.GetStringSelection() == "max":
                value = 1023
                self.slider.SetValue(1023)
                self.textSliderValue.Label = "1023"
            else:
                value = self.slider.GetValue()
            # determine subaddress and offset
            if sinCosPair == "Roll":
                device = 0
            elif sinCosPair == "Pitch":
                device = 1
            elif sinCosPair == "Device 3":
                device = 2
            else:
                device = 3
            offset = int(value / 256)
            data = value - (offset * 256)
            baseSinAddress = self.CMD_SIN_1 + offset
            baseCosAddress = self.CMD_COS_1 + offset
            self.sendData(self.QSCdeviceAddress, baseSinAddress, data)
            self.sendData(self.QSCdeviceAddress, baseCosAddress, data)
            self.sendData(self.QSCdeviceAddress, self.CMD_LOAD, device)

# =================================================================================================

    def advancedSend(self, event):
        advDeviceAddress = self.deviceAddressEntry.GetValue()
        advDeviceSubAddress = self.deviceSubAddressEntry.GetValue()
        advData = self.deviceDataEntry.GetValue()
        allDataValid = True
        # process entry fields
        addressValue = 83
        if self.validateDOAdata == True:
            if advDeviceAddress == "0x53" or advDeviceAddress == "0X53" or advDeviceAddress == "83" :
                portID = "QSC"
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
            if (subValue > self.QSChighestSubAddress) or (advDeviceSubAddress == ""):
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


# == TAB 7 ========================================================================================


# =================================================================================================

    def ExitClick(self, event):
        print("--- Exit QSC board test tool.")
        self.closeCOMMport(self.commPortID)
        frame.Close()


# =================================================================================================
#  COMMUNICATION  routine: send data
# =================================================================================================

    def sendData(self, address, subAddress, data):
        if self.commPortOpened == True:
            if address == self.QSCdeviceAddress:
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
                        print("!!! COM port for QSC is not open!")
                elif self.channelSelection == "USB":
                    if self.ComPort.isOpen():
                        print("... sendData to", self.commPortID, \
                              "subAddress", subAddress, "data", data)
                        self.ComPort.write(subAddress.to_bytes(1, byteorder='big', signed=False))
                        self.ComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                    else:
                        print("!!! COM port for QSC is not open!")
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
        if self.RollsettingValid == False:
            if self.RollEntryErrorShown == True:
                self.RollEntryErrorShown = False
                self.errorRollEntry.Hide()
                self.startTimer(300)
            else:
                self.RollEntryErrorShown = True
                self.errorRollEntry.Show()
                self.startTimer(500)
        else:
            if self.RollEntryErrorShown == True:
                self.RollEntryErrorShown = False
                self.errorRollEntry.Hide()
            #self.startTimer(300)
        # ----
        if self.PitchsettingValid == False:
            if self.PitchEntryErrorShown == True:
                self.PitchEntryErrorShown = False
                self.errorPitchEntry.Hide()
                self.startTimer(300)
            else:
                self.PitchEntryErrorShown = True
                self.errorPitchEntry.Show()
                self.startTimer(500)
        else:
            if self.PitchEntryErrorShown == True:
                self.PitchEntryErrorShown = False
                self.errorPitchEntry.Hide()
            self.startTimer(300)
        # ----
#       if (self.simulateStatus == 1):
            # simulate setpoint update
#           value = self.simulateRunningValue
#           value = value + self.simulateStepValue
#           if value >= 1024:
#               value = value - 1024
#           self.simulateRunningValue = value
#           self.textSimulateShowSetpoint.SetValue(str(self.simulateRunningValue))
            # send setpoint to simulated HSI indicator
#           command = int(value / 256)
#           data = value - (command * 256)
#           if self.simulateObject == 0:
#               self.sendData(self.QSCdeviceAddress, self.CMD_HDG_Q1 + command, data)
#           elif self.simulateObject == 1:
#               self.sendData(self.QSCdeviceAddress, self.CMD_BRG_Q1 + command, data)
#           else:
#               self.sendData(self.QSCdeviceAddress, self.CMD_MLS_1Q1 + command, data)
#               self.sendData(self.QSCdeviceAddress, self.CMD_MLS_2Q1 + command, data)
#               self.sendData(self.QSCdeviceAddress, self.CMD_MLS_3Q1 + command, data)
#           self.startTimer(self.simulateUpdateTime)



###################################################################################################
class HSIFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "QSC demonstrator", size=(660,395))
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