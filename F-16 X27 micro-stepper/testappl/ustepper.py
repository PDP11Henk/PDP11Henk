# Install Python version 3.6.x
# Install wxPython for Python 3.6
#    - start CMD window
#    - pip install -U wxPython
# Install the pyserial package
#    - pip install pyserial


import wx
# use the following two lines, or only the third line (version incompatibility issue)
#from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub
#from wx.lib.pubsub import Publisher as pub
import serial

CLOSE_COMM_PORTS = "0"

###################################################################################################

class TabPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Exit button
        self.buttonExit = wx.Button(self, label="Exit", pos=(430, 295), size=(100, 25))
        self.buttonExit.SetForegroundColour('#ff0000')
        self.buttonExit.Bind(wx.EVT_BUTTON, self.ExitClick)

        wx.StaticLine(self, -1, (5, 288), (555, 3))


    def ExitClick(self, event):
        pub.sendMessage(CLOSE_COMM_PORTS)
        print ("Exit clicked")
        # self.closeCOMMports()
        frame.Close()

###################################################################################################

class NotebookDemo(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_TOP)

        self.channelSelection   = "PHCC"
        self.uSTPdeviceAddress  = 0x75                    # (u) microStepper DEVICE address
        self.uSTPdiagSubaddress = 40                      # DIAG LED subaddress
        self.commPortID         = ""
        self.commPortValid      = False                   # for "error sign" blinking
        self.COMMportOpened     = False                   # flag COMM ports opened
        self.DiagLEDdatabyte1   = 2                       # default = 'heartbeat'

        self.smallFont = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.positionFont = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.errorImage = wx.Bitmap("error.gif")

        self.defaultMaxMotorSteps        = 3780

        self.motor1UsesHomeSensor        = False
        self.motor1Homed                 = False
        self.motor1MaxStepsValid         = True
        self.motor1MaxStepsErrorShown    = False
        self.motor1Position              = 0
        self.motor1Direction             = "cw"
        self.motor1RelPosEntryErrorShown = False
        self.motor1AbsPosEntryErrorShown = False
        self.motor1PositionValid         = True
        self.motor1MaxSteps              = self.defaultMaxMotorSteps

        self.motor2UsesHomeSensor        = False
        self.motor2Homed                 = False
        self.motor2MaxStepsValid         = True
        self.motor2MaxStepsErrorShown    = False
        self.motor2Position              = 0
        self.motor2Direction             = "cw"
        self.motor2RelPosEntryErrorShown = False
        self.motor2AbsPosEntryErrorShown = False
        self.motor2PositionValid         = True
        self.motor2MaxSteps              = self.defaultMaxMotorSteps

        self.motor3UsesHomeSensor        = False
        self.motor3Homed                 = False
        self.motor3MaxStepsValid         = True
        self.motor3MaxStepsErrorShown    = False
        self.motor3Position              = 0
        self.motor3Direction             = "cw"
        self.motor3RelPosEntryErrorShown = False
        self.motor3AbsPosEntryErrorShown = False
        self.motor3PositionValid         = True
        self.motor3MaxSteps              = self.defaultMaxMotorSteps

        self.motor4UsesHomeSensor        = False
        self.motor4Homed                 = False
        self.motor4MaxStepsValid         = True
        self.motor4MaxStepsErrorShown    = False
        self.motor4Position              = 0
        self.motor4Direction             = "cw"
        self.motor4RelPosEntryErrorShown = False
        self.motor4AbsPosEntryErrorShown = False
        self.motor4PositionValid         = True
        self.motor4MaxSteps              = self.defaultMaxMotorSteps

        self.validateDOAdata             = True

        # define timer
        self.TIMER_USE_NONE     = 0x0000                  # nothing to blink
        self.TIMER_COMPORT      = 0x0001                  # COM port not assigned
        self.TIMER_MOTOR1_HOME  = 0x0002                  # motor #1 not homed
        self.TIMER_MOTOR2_HOME  = 0x0004                  # motor #2 not homed
        self.TIMER_MOTOR3_HOME  = 0x0008                  # motor #3 not homed
        self.TIMER_MOTOR4_HOME  = 0x0010                  # motor #4 not homed
        self.TIMER_MOTOR1_REL   = 0x0020                  # motor #1 relative position spec wrong
        self.TIMER_MOTOR2_REL   = 0x0040                  # motor #2 relative position spec wrong
        self.TIMER_MOTOR3_REL   = 0x0080                  # motor #3 relative position spec wrong
        self.TIMER_MOTOR4_REL   = 0x0100                  # motor #4 relative position spec wrong
        self.TIMER_MOTOR1_ABS   = 0x0200                  # motor #1 absolute position spec wrong
        self.TIMER_MOTOR2_ABS   = 0x0400                  # motor #2 absolute position spec wrong
        self.TIMER_MOTOR3_ABS   = 0x0800                  # motor #3 absolute position spec wrong
        self.TIMER_MOTOR4_ABS   = 0x1000                  # motor #4 absolute position spec wrong

        self.timerUsage         = self.TIMER_COMPORT + \
                                  self.TIMER_MOTOR1_HOME + self.TIMER_MOTOR2_HOME + \
                                  self.TIMER_MOTOR3_HOME + self.TIMER_MOTOR4_HOME
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timerIsRunning = False
        self.startTimer(500)                              # initially COM port not assigned

        # pub.subscribe(self.onCloseMessageReceived, CLOSE_COMM_PORTS)


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
        print ("--- discovered COM ports:", availableCOMports)

        # display radio buttons for communication channel selection: PHCC or USB
        radioButtonList = ['PHCC', 'USB']
        self.rbox = wx.RadioBox(tabOne, label = 'Communication channel', pos = (30,40),
                                choices = radioButtonList, majorDimension = 1)
        self.rbox.Bind(wx.EVT_RADIOBOX,self.onConnectionBox)

        # display COM port selection
        wx.StaticBox(tabOne, label='COM port', pos=(30, 140), size=(153, 95))
        self.cbComm1 = wx.ComboBox(tabOne, pos=(45, 161), size=(70, 25), choices=availableCOMports, style=wx.CB_READONLY)
        self.cbComm1.SetToolTip(wx.ToolTip("set COM port"))
        self.cbComm1.Bind(wx.EVT_COMBOBOX, self.OnSelectCommPort)
        self.errorCommPort = wx.StaticBitmap(tabOne, -1, self.errorImage)
        self.errorCommPort.SetPosition((125, 160))
        self.errorCommPortShown = True

        self.ComPortTextOpen = wx.StaticText(tabOne, label='OPEN', pos=(135, 166))
        portFont = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.ComPortTextOpen.SetForegroundColour('#006600')
        self.ComPortTextOpen.SetFont(portFont)
        self.ComPortTextOpen.Hide()
        self.ComPortTextClosed = wx.StaticText(tabOne, label='CLOSED', pos=(129, 166))
        self.ComPortTextClosed.SetForegroundColour('#e60000')
        self.ComPortTextClosed.SetFont(portFont)
        self.ComPortTextClosed.Hide()

        # communication channel OPEN button
        self.buttonComOpen = wx.Button(tabOne, label="Open COM port", pos=(45, 195), size=(120, 25))
        self.buttonComOpen.SetBackgroundColour('#cccccc')
        self.buttonComOpen.SetForegroundColour('#ffffff')
        self.buttonComOpen.Bind(wx.EVT_BUTTON, self.ComOpenClick)

        # diagnostic LED
        wx.StaticBox(tabOne, label='Diagnostics LED', pos=(370, 40), size=(150, 60))

        diagLEDmodes = ['heartbeat', 'off', 'on', 'ACK', 'DOA']
        self.cbDiagLED = wx.ComboBox(tabOne, pos=(380, 60), size=(80, 25), choices=diagLEDmodes, style=wx.CB_READONLY)
        self.cbDiagLED.SetToolTip(wx.ToolTip("set LED diag mode #1"))
        self.cbDiagLED.SetValue('heartbeat')
        self.cbDiagLED.Bind(wx.EVT_COMBOBOX, self.OnSelectDiagLED)

        self.buttonDiagLED = wx.Button(tabOne, label="Set", pos=(470, 58), size=(40, 25))
        self.buttonDiagLED.SetBackgroundColour('#99ccff')
        self.buttonDiagLED.SetForegroundColour('#000000')
        self.buttonDiagLED.Bind(wx.EVT_BUTTON, self.SendDiagLED)



#-- TAB #2  Motor #1  -----------------------------------------------------------------------------
        tabTwo = TabPanel(self)
        self.AddPage(tabTwo, " motor #1 ")

        # HOME sensor and homing
        wx.StaticBox(tabTwo, label='HOME sensor', pos=(30, 10), size=(295, 60))
        self.useHomeSensor1 = wx.CheckBox(tabTwo, label='use HOME sensor', pos=(50, 30), size=(120, 25))
        self.useHomeSensor1.SetValue(False)
        self.useHomeSensor1.SetToolTip(wx.ToolTip("use HOME sensor for MOTOR #1"))
        self.useHomeSensor1.Bind(wx.EVT_CHECKBOX, self.useHomeSensor1Checkbox)

        self.buttonHomeMotor1 = wx.Button(tabTwo, label="to HOME position", pos=(185, 30), size=(120, 25))
        self.buttonHomeMotor1.SetToolTip(wx.ToolTip("HOME motor #1"))
        self.buttonHomeMotor1.SetBackgroundColour('#99ccff')
        self.buttonHomeMotor1.SetForegroundColour('#000000')
        self.buttonHomeMotor1.Bind(wx.EVT_BUTTON, self.homeMotor1Action)

        self.motor1MaxStepsBox = wx.StaticBox(tabTwo, label='Maximum # steps', pos=(360, 10), size=(170, 60))
        self.motor1MaxStepsEntry = wx.TextCtrl(tabTwo, value=str(self.motor1MaxSteps), pos=(380, 30), size=(45, 25))
        self.motor1MaxStepsSet = wx.Button(tabTwo, label="Set", pos=(475, 30), size=(40, 25))
        self.motor1MaxStepsSet.SetToolTip(wx.ToolTip("set maximum # of steps"))
        self.motor1MaxStepsSet.SetBackgroundColour('#99ccff')
        self.motor1MaxStepsSet.SetForegroundColour('#000000')
        self.motor1MaxStepsSet.Bind(wx.EVT_BUTTON, self.onMotor1MaxStepsSet)
        self.errorMotor1MaxSteps = wx.StaticBitmap(tabTwo, -1, self.errorImage)
        self.errorMotor1MaxSteps.SetPosition((430, 30))
        self.errorMotor1MaxSteps.Hide()

        # Motor #1 movement
        wx.StaticBox(tabTwo, label='Movement tests', pos=(30, 80), size=(500, 180))
        radioButtonMotor1OptionList = ['slider update', 'relative update', 'absolute update']
        self.rboxMotor1Option = wx.RadioBox(tabTwo, label = 'Options', pos = (45, 100),
                                            choices = radioButtonMotor1OptionList, majorDimension = 0)
        self.rboxMotor1Option.Bind(wx.EVT_RADIOBOX,self.motor1MovementOptionSelect)
        wx.StaticLine(tabTwo, pos=(29, 170), size=(495, 1))

        self.motor1slider = wx.Slider(tabTwo, value=self.motor1Position, minValue=0, maxValue=self.motor1MaxSteps,
                                      pos=(40, 200), size=(400, -1), style=wx.SL_HORIZONTAL)
        self.motor1slider.Bind(wx.EVT_SLIDER, self.onMotor1SliderScroll)
        self.textMotor1slider1 = wx.StaticText(tabTwo, label='min', pos=(46, 225))
        self.textMotor1slider2 = wx.StaticText(tabTwo, label='ctr', pos=(234, 225))
        self.textMotor1slider3 = wx.StaticText(tabTwo, label='max', pos=(416, 225))
        self.textMotor1slider1.SetFont(self.smallFont)
        self.textMotor1slider2.SetFont(self.smallFont)
        self.textMotor1slider3.SetFont(self.smallFont)
        self.textMotor1slider1.SetForegroundColour("#000000")
        self.textMotor1slider2.SetForegroundColour("#000000")
        self.textMotor1slider3.SetForegroundColour("#000000")
        self.motor1EntrySet = wx.Button(tabTwo, label="Set", pos=(460, 200), size=(50, 25))
        self.motor1EntrySet.SetToolTip(wx.ToolTip("set motor #1 position"))
        self.motor1EntrySet.SetBackgroundColour('#99ccff')
        self.motor1EntrySet.SetForegroundColour('#000000')
        self.motor1EntrySet.Bind(wx.EVT_BUTTON, self.onMotor1SliderSet)
        self.motor1CurrentPositionSlider = wx.StaticText(tabTwo, label=str(self.motor1Position),
                                                         style=wx.ALIGN_CENTER, size=(28, 15))
        self.motor1CurrentPositionSlider.SetPosition((40, 180))
        self.motor1CurrentPositionSlider.SetFont(self.smallFont)
        self.motor1CurrentPositionSlider.SetForegroundColour("#ff0000")
        self.motor1CurrentPositionSlider.Hide()
        self.hideMotor1OptionSlider()

        self.motor1CurrentPositionText = wx.StaticText(tabTwo, label='position', pos=(445, 190))
        self.motor1CurrentPositionText.SetFont(self.smallFont)
        self.motor1CurrentPositionText.SetForegroundColour('#0000ff')
        self.motor1CurrentPositionField = wx.StaticText(tabTwo, label=str(self.motor1Position),
                                                        style=wx.ALIGN_CENTER, pos=(438, 210), size=(50, 35))
        self.motor1CurrentPositionField.SetFont(self.positionFont)
        self.motor1CurrentPositionField.SetForegroundColour("#ff0000")
        self.motor1CurrentPositionText.Hide()
        self.motor1CurrentPositionField.Hide()

        radioButtonMotor1DirList = ['cw', 'ccw']
        self.rboxMotor1 = wx.RadioBox(tabTwo, label = 'Direction', pos = (45, 190),
                                      choices = radioButtonMotor1DirList, majorDimension = 0)
        self.rboxMotor1.Bind(wx.EVT_RADIOBOX,self.onMotor1DirSelect)
        self.relPosMotor1Box = wx.StaticBox(tabTwo, label='Relative position update', pos=(160, 190), size=(230, 50))
        self.motor1RelPositionEntry = wx.TextCtrl(tabTwo, value="0", pos=(180, 210), size=(60, 23))
        self.buttonMotor1RelPositionSet = wx.Button(tabTwo, label="Set", pos=(305, 210), size=(60, 25))
        self.buttonMotor1RelPositionSet.SetToolTip(wx.ToolTip("update motor #1 position relative"))
        self.buttonMotor1RelPositionSet.SetBackgroundColour('#99ccff')
        self.buttonMotor1RelPositionSet.SetForegroundColour('#000000')
        self.buttonMotor1RelPositionSet.Bind(wx.EVT_BUTTON, self.onMotor1PosRelativeSet)
        self.errorMotor1RelPosition = wx.StaticBitmap(tabTwo, -1, self.errorImage)
        self.errorMotor1RelPosition.SetPosition((250, 210))
        self.hideMotor1OptionRelative()

        self.absPosMotor1Box = wx.StaticBox(tabTwo, label='Absolute position update', pos=(160, 190), size=(230, 50))
        self.motor1AbsPositionEntry = wx.TextCtrl(tabTwo, value="0", pos=(180, 210), size=(60, 23))
        self.buttonMotor1AbsPositionSet = wx.Button(tabTwo, label="Set", pos=(305, 210), size=(60, 25))
        self.buttonMotor1AbsPositionSet.SetToolTip(wx.ToolTip("update motor #1 position absolute"))
        self.buttonMotor1AbsPositionSet.SetBackgroundColour('#99ccff')
        self.buttonMotor1AbsPositionSet.SetForegroundColour('#000000')
        self.buttonMotor1AbsPositionSet.Bind(wx.EVT_BUTTON, self.onMotor1PosAbsoluteSet)
        self.errorMotor1AbsPosition = wx.StaticBitmap(tabTwo, -1, self.errorImage)
        self.errorMotor1AbsPosition.SetPosition((250, 210))
        self.hideMotor1OptionAbsolute()


#-- TAB #3  Motor #2  -----------------------------------------------------------------------------
        tabThree = TabPanel(self)
        self.AddPage(tabThree, " motor #2 ")

        # HOME sensor and homing
        wx.StaticBox(tabThree, label='HOME sensor', pos=(30, 10), size=(295, 60))
        self.useHomeSensor2 = wx.CheckBox(tabThree, label='use HOME sensor', pos=(50, 30), size=(120, 25))
        self.useHomeSensor2.SetValue(False)
        self.useHomeSensor2.SetToolTip(wx.ToolTip("use HOME sensor for MOTOR #2"))
        self.useHomeSensor2.Bind(wx.EVT_CHECKBOX, self.useHomeSensor2Checkbox)

        self.buttonHomeMotor2 = wx.Button(tabThree, label="to HOME position", pos=(185, 30), size=(120, 25))
        self.buttonHomeMotor2.SetToolTip(wx.ToolTip("HOME motor #2"))
        self.buttonHomeMotor2.SetBackgroundColour('#99ccff')
        self.buttonHomeMotor2.SetForegroundColour('#000000')
        self.buttonHomeMotor2.Bind(wx.EVT_BUTTON, self.homeMotor2Action)

        self.motor2MaxStepsBox = wx.StaticBox(tabThree, label='Maximum # steps', pos=(360, 10), size=(170, 60))
        self.motor2MaxStepsEntry = wx.TextCtrl(tabThree, value=str(self.motor2MaxSteps), pos=(380, 30), size=(45, 25))
        self.motor2MaxStepsSet = wx.Button(tabThree, label="Set", pos=(475, 30), size=(40, 25))
        self.motor2MaxStepsSet.SetToolTip(wx.ToolTip("set maximum # of steps"))
        self.motor2MaxStepsSet.SetBackgroundColour('#99ccff')
        self.motor2MaxStepsSet.SetForegroundColour('#000000')
        self.motor2MaxStepsSet.Bind(wx.EVT_BUTTON, self.onMotor2MaxStepsSet)
        self.errorMotor2MaxSteps = wx.StaticBitmap(tabThree, -1, self.errorImage)
        self.errorMotor2MaxSteps.SetPosition((430, 30))
        self.errorMotor2MaxSteps.Hide()

        # Motor #2 movement
        wx.StaticBox(tabThree, label='Movement tests', pos=(30, 80), size=(500, 180))
        radioButtonMotor2OptionList = ['slider update', 'relative update', 'absolute update']
        self.rboxMotor2Option = wx.RadioBox(tabThree, label = 'Options', pos = (45, 100),
                                            choices = radioButtonMotor2OptionList, majorDimension = 0)
        self.rboxMotor2Option.Bind(wx.EVT_RADIOBOX,self.motor2MovementOptionSelect)
        wx.StaticLine(tabThree, pos=(29, 170), size=(495, 1))

        self.motor2slider = wx.Slider(tabThree, value=self.motor2Position, minValue=0, maxValue=self.motor2MaxSteps,
                                      pos=(40, 200), size=(400, -1), style=wx.SL_HORIZONTAL)
        self.motor2slider.Bind(wx.EVT_SLIDER, self.onMotor2SliderScroll)
        self.textMotor2slider1 = wx.StaticText(tabThree, label='min', pos=(46, 225))
        self.textMotor2slider2 = wx.StaticText(tabThree, label='ctr', pos=(234, 225))
        self.textMotor2slider3 = wx.StaticText(tabThree, label='max', pos=(416, 225))
        self.textMotor2slider1.SetFont(self.smallFont)
        self.textMotor2slider2.SetFont(self.smallFont)
        self.textMotor2slider3.SetFont(self.smallFont)
        self.textMotor2slider1.SetForegroundColour("#000000")
        self.textMotor2slider2.SetForegroundColour("#000000")
        self.textMotor2slider3.SetForegroundColour("#000000")
        self.motor2EntrySet = wx.Button(tabThree, label="Set", pos=(460, 200), size=(50, 25))
        self.motor2EntrySet.SetToolTip(wx.ToolTip("set motor #2 position"))
        self.motor2EntrySet.SetBackgroundColour('#99ccff')
        self.motor2EntrySet.SetForegroundColour('#000000')
        self.motor2EntrySet.Bind(wx.EVT_BUTTON, self.onMotor2SliderSet)
        self.motor2CurrentPositionSlider = wx.StaticText(tabThree, label=str(self.motor2Position),
                                                         style=wx.ALIGN_CENTER, size=(28, 15))
        self.motor2CurrentPositionSlider.SetPosition((40, 180))
        self.motor2CurrentPositionSlider.SetFont(self.smallFont)
        self.motor2CurrentPositionSlider.SetForegroundColour("#ff0000")
        self.motor2CurrentPositionSlider.Hide()
        self.hideMotor2OptionSlider()

        self.motor2CurrentPositionText = wx.StaticText(tabThree, label='position', pos=(445, 190))
        self.motor2CurrentPositionText.SetFont(self.smallFont)
        self.motor2CurrentPositionText.SetForegroundColour('#0000ff')
        self.motor2CurrentPositionField = wx.StaticText(tabThree, label=str(self.motor2Position),
                                                        style=wx.ALIGN_CENTER, pos=(438, 210), size=(50, 35))
        self.motor2CurrentPositionField.SetFont(self.positionFont)
        self.motor2CurrentPositionField.SetForegroundColour("#ff0000")
        self.motor2CurrentPositionText.Hide()
        self.motor2CurrentPositionField.Hide()

        radioButtonMotor2DirList = ['cw', 'ccw']
        self.rboxMotor2 = wx.RadioBox(tabThree, label = 'Direction', pos = (45, 190),
                                      choices = radioButtonMotor2DirList, majorDimension = 0)
        self.rboxMotor2.Bind(wx.EVT_RADIOBOX,self.onMotor2DirSelect)
        self.relPosMotor2Box = wx.StaticBox(tabThree, label='Relative position update', pos=(160, 190), size=(230, 50))
        self.motor2RelPositionEntry = wx.TextCtrl(tabThree, value="0", pos=(180, 210), size=(60, 23))
        self.buttonMotor2RelPositionSet = wx.Button(tabThree, label="Set", pos=(305, 210), size=(60, 25))
        self.buttonMotor2RelPositionSet.SetToolTip(wx.ToolTip("update motor #2 position relative"))
        self.buttonMotor2RelPositionSet.SetBackgroundColour('#99ccff')
        self.buttonMotor2RelPositionSet.SetForegroundColour('#000000')
        self.buttonMotor2RelPositionSet.Bind(wx.EVT_BUTTON, self.onMotor2PosRelativeSet)
        self.errorMotor2RelPosition = wx.StaticBitmap(tabThree, -1, self.errorImage)
        self.errorMotor2RelPosition.SetPosition((250, 210))
        self.hideMotor2OptionRelative()

        self.absPosMotor2Box = wx.StaticBox(tabThree, label='Absolute position update', pos=(160, 190), size=(230, 50))
        self.motor2AbsPositionEntry = wx.TextCtrl(tabThree, value="0", pos=(180, 210), size=(60, 23))
        self.buttonMotor2AbsPositionSet = wx.Button(tabThree, label="Set", pos=(305, 210), size=(60, 25))
        self.buttonMotor2AbsPositionSet.SetToolTip(wx.ToolTip("update motor #2 position absolute"))
        self.buttonMotor2AbsPositionSet.SetBackgroundColour('#99ccff')
        self.buttonMotor2AbsPositionSet.SetForegroundColour('#000000')
        self.buttonMotor2AbsPositionSet.Bind(wx.EVT_BUTTON, self.onMotor2PosAbsoluteSet)
        self.errorMotor2AbsPosition = wx.StaticBitmap(tabThree, -1, self.errorImage)
        self.errorMotor2AbsPosition.SetPosition((250, 210))
        self.hideMotor2OptionAbsolute()


#-- TAB #4  Motor #3  -----------------------------------------------------------------------------
        tabFour = TabPanel(self)
        self.AddPage(tabFour, " motor #3 ")

        # HOME sensor and homing
        wx.StaticBox(tabFour, label='HOME sensor', pos=(30, 10), size=(295, 60))
        self.useHomeSensor3 = wx.CheckBox(tabFour, label='use HOME sensor', pos=(50, 30), size=(120, 25))
        self.useHomeSensor3.SetValue(False)
        self.useHomeSensor3.SetToolTip(wx.ToolTip("use HOME sensor for MOTOR #3"))
        self.useHomeSensor3.Bind(wx.EVT_CHECKBOX, self.useHomeSensor3Checkbox)

        self.buttonHomeMotor3 = wx.Button(tabFour, label="to HOME position", pos=(185, 30), size=(120, 25))
        self.buttonHomeMotor3.SetToolTip(wx.ToolTip("HOME motor #3"))
        self.buttonHomeMotor3.SetBackgroundColour('#99ccff')
        self.buttonHomeMotor3.SetForegroundColour('#000000')
        self.buttonHomeMotor3.Bind(wx.EVT_BUTTON, self.homeMotor3Action)

        self.motor3MaxStepsBox = wx.StaticBox(tabFour, label='Maximum # steps', pos=(360, 10), size=(170, 60))
        self.motor3MaxStepsEntry = wx.TextCtrl(tabFour, value=str(self.motor3MaxSteps), pos=(380, 30), size=(45, 25))
        self.motor3MaxStepsSet = wx.Button(tabFour, label="Set", pos=(475, 30), size=(40, 25))
        self.motor3MaxStepsSet.SetToolTip(wx.ToolTip("set maximum # of steps"))
        self.motor3MaxStepsSet.SetBackgroundColour('#99ccff')
        self.motor3MaxStepsSet.SetForegroundColour('#000000')
        self.motor3MaxStepsSet.Bind(wx.EVT_BUTTON, self.onMotor3MaxStepsSet)
        self.errorMotor3MaxSteps = wx.StaticBitmap(tabFour, -1, self.errorImage)
        self.errorMotor3MaxSteps.SetPosition((430, 30))
        self.errorMotor3MaxSteps.Hide()

        # Motor #3 movement
        wx.StaticBox(tabFour, label='Movement tests', pos=(30, 80), size=(500, 180))
        radioButtonMotor3OptionList = ['slider update', 'relative update', 'absolute update']
        self.rboxMotor3Option = wx.RadioBox(tabFour, label = 'Options', pos = (45, 100),
                                            choices = radioButtonMotor3OptionList, majorDimension = 0)
        self.rboxMotor3Option.Bind(wx.EVT_RADIOBOX,self.motor3MovementOptionSelect)
        wx.StaticLine(tabFour, pos=(29, 170), size=(495, 1))

        self.motor3slider = wx.Slider(tabFour, value=self.motor3Position, minValue=0, maxValue=self.motor3MaxSteps,
                                      pos=(40, 200), size=(400, -1), style=wx.SL_HORIZONTAL)
        self.motor3slider.Bind(wx.EVT_SLIDER, self.onMotor3SliderScroll)
        self.textMotor3slider1 = wx.StaticText(tabFour, label='min', pos=(46, 225))
        self.textMotor3slider2 = wx.StaticText(tabFour, label='ctr', pos=(234, 225))
        self.textMotor3slider3 = wx.StaticText(tabFour, label='max', pos=(416, 225))
        self.textMotor3slider1.SetFont(self.smallFont)
        self.textMotor3slider2.SetFont(self.smallFont)
        self.textMotor3slider3.SetFont(self.smallFont)
        self.textMotor3slider1.SetForegroundColour("#000000")
        self.textMotor3slider2.SetForegroundColour("#000000")
        self.textMotor3slider3.SetForegroundColour("#000000")
        self.motor3EntrySet = wx.Button(tabFour, label="Set", pos=(460, 200), size=(50, 25))
        self.motor3EntrySet.SetToolTip(wx.ToolTip("set motor #3 position"))
        self.motor3EntrySet.SetBackgroundColour('#99ccff')
        self.motor3EntrySet.SetForegroundColour('#000000')
        self.motor3EntrySet.Bind(wx.EVT_BUTTON, self.onMotor3SliderSet)
        self.motor3CurrentPositionSlider = wx.StaticText(tabFour, label=str(self.motor3Position),
                                                         style=wx.ALIGN_CENTER, size=(28, 15))
        self.motor3CurrentPositionSlider.SetPosition((40, 180))
        self.motor3CurrentPositionSlider.SetFont(self.smallFont)
        self.motor3CurrentPositionSlider.SetForegroundColour("#ff0000")
        self.motor3CurrentPositionSlider.Hide()
        self.hideMotor3OptionSlider()

        self.motor3CurrentPositionText = wx.StaticText(tabFour, label='position', pos=(445, 190))
        self.motor3CurrentPositionText.SetFont(self.smallFont)
        self.motor3CurrentPositionText.SetForegroundColour('#0000ff')
        self.motor3CurrentPositionField = wx.StaticText(tabFour, label=str(self.motor3Position),
                                                        style=wx.ALIGN_CENTER, pos=(438, 210), size=(50, 35))
        self.motor3CurrentPositionField.SetFont(self.positionFont)
        self.motor3CurrentPositionField.SetForegroundColour("#ff0000")
        self.motor3CurrentPositionText.Hide()
        self.motor3CurrentPositionField.Hide()

        radioButtonMotor3DirList = ['cw', 'ccw']
        self.rboxMotor3 = wx.RadioBox(tabFour, label = 'Direction', pos = (45, 190),
                                      choices = radioButtonMotor3DirList, majorDimension = 0)
        self.rboxMotor3.Bind(wx.EVT_RADIOBOX,self.onMotor3DirSelect)
        self.relPosMotor3Box = wx.StaticBox(tabFour, label='Relative position update', pos=(160, 190), size=(230, 50))
        self.motor3RelPositionEntry = wx.TextCtrl(tabFour, value="0", pos=(180, 210), size=(60, 23))
        self.buttonMotor3RelPositionSet = wx.Button(tabFour, label="Set", pos=(305, 210), size=(60, 25))
        self.buttonMotor3RelPositionSet.SetToolTip(wx.ToolTip("update motor #3 position relative"))
        self.buttonMotor3RelPositionSet.SetBackgroundColour('#99ccff')
        self.buttonMotor3RelPositionSet.SetForegroundColour('#000000')
        self.buttonMotor3RelPositionSet.Bind(wx.EVT_BUTTON, self.onMotor3PosRelativeSet)
        self.errorMotor3RelPosition = wx.StaticBitmap(tabFour, -1, self.errorImage)
        self.errorMotor3RelPosition.SetPosition((250, 210))
        self.hideMotor3OptionRelative()

        self.absPosMotor3Box = wx.StaticBox(tabFour, label='Absolute position update', pos=(160, 190), size=(230, 50))
        self.motor3AbsPositionEntry = wx.TextCtrl(tabFour, value="0", pos=(180, 210), size=(60, 23))
        self.buttonMotor3AbsPositionSet = wx.Button(tabFour, label="Set", pos=(305, 210), size=(60, 25))
        self.buttonMotor3AbsPositionSet.SetToolTip(wx.ToolTip("update motor #3 position absolute"))
        self.buttonMotor3AbsPositionSet.SetBackgroundColour('#99ccff')
        self.buttonMotor3AbsPositionSet.SetForegroundColour('#000000')
        self.buttonMotor3AbsPositionSet.Bind(wx.EVT_BUTTON, self.onMotor3PosAbsoluteSet)
        self.errorMotor3AbsPosition = wx.StaticBitmap(tabFour, -1, self.errorImage)
        self.errorMotor3AbsPosition.SetPosition((250, 210))
        self.hideMotor3OptionAbsolute()


#-- TAB #5  Motor #4  -----------------------------------------------------------------------------
        tabFive = TabPanel(self)
        self.AddPage(tabFive, " motor #4 ")

        # HOME sensor and homing
        wx.StaticBox(tabFive, label='HOME sensor', pos=(30, 10), size=(295, 60))
        self.useHomeSensor4 = wx.CheckBox(tabFive, label='use HOME sensor', pos=(50, 30), size=(120, 25))
        self.useHomeSensor4.SetValue(False)
        self.useHomeSensor4.SetToolTip(wx.ToolTip("use HOME sensor for MOTOR #4"))
        self.useHomeSensor4.Bind(wx.EVT_CHECKBOX, self.useHomeSensor4Checkbox)

        self.buttonHomeMotor4 = wx.Button(tabFive, label="to HOME position", pos=(185, 30), size=(120, 25))
        self.buttonHomeMotor4.SetToolTip(wx.ToolTip("HOME motor #4"))
        self.buttonHomeMotor4.SetBackgroundColour('#99ccff')
        self.buttonHomeMotor4.SetForegroundColour('#000000')
        self.buttonHomeMotor4.Bind(wx.EVT_BUTTON, self.homeMotor4Action)

        self.motor4MaxStepsBox = wx.StaticBox(tabFive, label='Maximum # steps', pos=(360, 10), size=(170, 60))
        self.motor4MaxStepsEntry = wx.TextCtrl(tabFive, value=str(self.motor4MaxSteps), pos=(380, 30), size=(45, 25))
        self.motor4MaxStepsSet = wx.Button(tabFive, label="Set", pos=(475, 30), size=(40, 25))
        self.motor4MaxStepsSet.SetToolTip(wx.ToolTip("set maximum # of steps"))
        self.motor4MaxStepsSet.SetBackgroundColour('#99ccff')
        self.motor4MaxStepsSet.SetForegroundColour('#000000')
        self.motor4MaxStepsSet.Bind(wx.EVT_BUTTON, self.onMotor4MaxStepsSet)
        self.errorMotor4MaxSteps = wx.StaticBitmap(tabFive, -1, self.errorImage)
        self.errorMotor4MaxSteps.SetPosition((430, 30))
        self.errorMotor4MaxSteps.Hide()

        # Motor #4 movement
        wx.StaticBox(tabFive, label='Movement tests', pos=(30, 80), size=(500, 180))
        radioButtonMotor4OptionList = ['slider update', 'relative update', 'absolute update']
        self.rboxMotor4Option = wx.RadioBox(tabFive, label = 'Options', pos = (45, 100),
                                            choices = radioButtonMotor4OptionList, majorDimension = 0)
        self.rboxMotor4Option.Bind(wx.EVT_RADIOBOX,self.motor4MovementOptionSelect)
        wx.StaticLine(tabFive, pos=(29, 170), size=(495, 1))

        self.motor4slider = wx.Slider(tabFive, value=self.motor4Position, minValue=0, maxValue=self.motor4MaxSteps,
                                      pos=(40, 200), size=(400, -1), style=wx.SL_HORIZONTAL)
        self.motor4slider.Bind(wx.EVT_SLIDER, self.onMotor4SliderScroll)
        self.textMotor4slider1 = wx.StaticText(tabFive, label='min', pos=(46, 225))
        self.textMotor4slider2 = wx.StaticText(tabFive, label='ctr', pos=(234, 225))
        self.textMotor4slider3 = wx.StaticText(tabFive, label='max', pos=(416, 225))
        self.textMotor4slider1.SetFont(self.smallFont)
        self.textMotor4slider2.SetFont(self.smallFont)
        self.textMotor4slider3.SetFont(self.smallFont)
        self.textMotor4slider1.SetForegroundColour("#000000")
        self.textMotor4slider2.SetForegroundColour("#000000")
        self.textMotor4slider3.SetForegroundColour("#000000")
        self.motor4EntrySet = wx.Button(tabFive, label="Set", pos=(460, 200), size=(50, 25))
        self.motor4EntrySet.SetToolTip(wx.ToolTip("set motor #4 position"))
        self.motor4EntrySet.SetBackgroundColour('#99ccff')
        self.motor4EntrySet.SetForegroundColour('#000000')
        self.motor4EntrySet.Bind(wx.EVT_BUTTON, self.onMotor4SliderSet)
        self.motor4CurrentPositionSlider = wx.StaticText(tabFive, label=str(self.motor4Position),
                                                         style=wx.ALIGN_CENTER, size=(28, 15))
        self.motor4CurrentPositionSlider.SetPosition((40, 180))
        self.motor4CurrentPositionSlider.SetFont(self.smallFont)
        self.motor4CurrentPositionSlider.SetForegroundColour("#ff0000")
        self.motor4CurrentPositionSlider.Hide()
        self.hideMotor4OptionSlider()

        self.motor4CurrentPositionText = wx.StaticText(tabFive, label='position', pos=(445, 190))
        self.motor4CurrentPositionText.SetFont(self.smallFont)
        self.motor4CurrentPositionText.SetForegroundColour('#0000ff')
        self.motor4CurrentPositionField = wx.StaticText(tabFive, label=str(self.motor4Position),
                                                        style=wx.ALIGN_CENTER, pos=(438, 210), size=(50, 35))
        self.motor4CurrentPositionField.SetFont(self.positionFont)
        self.motor4CurrentPositionField.SetForegroundColour("#ff0000")
        self.motor4CurrentPositionText.Hide()
        self.motor4CurrentPositionField.Hide()

        radioButtonMotor4DirList = ['cw', 'ccw']
        self.rboxMotor4 = wx.RadioBox(tabFive, label = 'Direction', pos = (45, 190),
                                      choices = radioButtonMotor4DirList, majorDimension = 0)
        self.rboxMotor4.Bind(wx.EVT_RADIOBOX,self.onMotor4DirSelect)
        self.relPosMotor4Box = wx.StaticBox(tabFive, label='Relative position update', pos=(160, 190), size=(230, 50))
        self.motor4RelPositionEntry = wx.TextCtrl(tabFive, value="0", pos=(180, 210), size=(60, 23))
        self.buttonMotor4RelPositionSet = wx.Button(tabFive, label="Set", pos=(305, 210), size=(60, 25))
        self.buttonMotor4RelPositionSet.SetToolTip(wx.ToolTip("update motor #4 position relative"))
        self.buttonMotor4RelPositionSet.SetBackgroundColour('#99ccff')
        self.buttonMotor4RelPositionSet.SetForegroundColour('#000000')
        self.buttonMotor4RelPositionSet.Bind(wx.EVT_BUTTON, self.onMotor4PosRelativeSet)
        self.errorMotor4RelPosition = wx.StaticBitmap(tabFive, -1, self.errorImage)
        self.errorMotor4RelPosition.SetPosition((250, 210))
        self.hideMotor4OptionRelative()

        self.absPosMotor4Box = wx.StaticBox(tabFive, label='Absolute position update', pos=(160, 190), size=(230, 50))
        self.motor4AbsPositionEntry = wx.TextCtrl(tabFive, value="0", pos=(180, 210), size=(60, 23))
        self.buttonMotor4AbsPositionSet = wx.Button(tabFive, label="Set", pos=(305, 210), size=(60, 25))
        self.buttonMotor4AbsPositionSet.SetToolTip(wx.ToolTip("update motor #4 position absolute"))
        self.buttonMotor4AbsPositionSet.SetBackgroundColour('#99ccff')
        self.buttonMotor4AbsPositionSet.SetForegroundColour('#000000')
        self.buttonMotor4AbsPositionSet.Bind(wx.EVT_BUTTON, self.onMotor4PosAbsoluteSet)
        self.errorMotor4AbsPosition = wx.StaticBitmap(tabFive, -1, self.errorImage)
        self.errorMotor4AbsPosition.SetPosition((250, 210))
        self.hideMotor4OptionAbsolute()


#-- TAB #6  Raw data  -----------------------------------------------------------------------------
        tabSix = TabPanel(self)
        self.AddPage(tabSix, "raw data")

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
        self.deviceAddressEntry.Value = hex(self.uSTPdeviceAddress)
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
        self.allowAll.SetToolTip(wx.ToolTip("allow any command"))
        self.allowAll.Bind(wx.EVT_CHECKBOX, self.allowAllCheckbox)


        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)


    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        # print ('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        #if new == 1:
        #    # motor #1 tab
        #    if self.channelSelection == "USB":
        #        print ("on tab 2 USB")
        #    if self.channelSelection == "PHCC":
        #        print ("on tab 2 PHCC")
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        # print ('OnPageChanging:,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()

# =================================================================================================

    def onConnectionBox(self,e): 
        if self.rbox.GetStringSelection() == "PHCC":
            self.channelSelection = "PHCC"
            print ("Connection =", self.channelSelection)
        else:
            self.channelSelection = "USB"
            print ("Connection =", self.channelSelection)


    def OnSelectCommPort(self, entry):
        self.closeCOMMport()
        previousCommPort = self.commPortID
        self.commPortID = entry.GetString()
        print ("previous =", previousCommPort, "new set port ID =", self.commPortID)
        self.commPortValid = True
        self.buttonComOpen.SetBackgroundColour('#0066ff')
        self.ComPortTextClosed.Show()
        self.ComPortTextOpen.Hide()


    def openCOMMport(self):
        print (">   opening COM port", self.commPortID)
        self.ComPort1 = serial.Serial(self.commPortID, baudrate=115200, parity=serial.PARITY_NONE,
                                      stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        self.COMMportOpened = True


    def closeCOMMport(self):
        print ("calling closeCOMMport")
        if (self.COMMportOpened == True):
            print (">   closing COM port", self.commPortID)
            if self.ComPort1.isOpen():
                self.ComPort1.close()
            else:
                print ("!!! COM port", self.commPortID, "is not open!")
            self.COMMportOpened = False


    def ComOpenClick(self, event):
        if (self.buttonComOpen.GetBackgroundColour() != '#cccccc'):
            # button is "green" :: open or close COM ports
            if (self.buttonComOpen.GetLabel() == "Open COM port"):
                self.openCOMMport()
                self.ComPortTextClosed.Hide()
                self.ComPortTextOpen.Show()
                self.buttonComOpen.SetLabel("Close COM port")
            else:
                self.closeCOMMport()
                self.ComPortTextOpen.Hide()
                self.ComPortTextClosed.Show()
                self.buttonComOpen.SetLabel("Open COM port")


    def onCloseMessageReceived(self, text):
        self.closeCOMMport()


    def OnSelectDiagLED(self, event):
        value = self.cbDiagLED.GetValue()
        if value == 'heartbeat':
            self.DiagLEDdatabyte1 = 2
        elif value == 'on':
            self.DiagLEDdatabyte1 = 1
        elif value == 'off':
            self.DiagLEDdatabyte1 = 0
        elif value == 'ACK':
            self.DiagLEDdatabyte1 = 3
        else:  # 'DOA'
            self.DiagLEDdatabyte1 = 4


    def SendDiagLED(self, event):
        self.sendData(self.uSTPdeviceAddress, self.uSTPdiagSubaddress, self.DiagLEDdatabyte1)

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

    def useHomeSensor1Checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.motor1UsesHomeSensor = True
            print ("    motor #1 uses its HOME sensor")
        else:
            self.motor1UsesHomeSensor = False
            print ("    motor #1 does not use its HOME sensor")
        # require homing
        self.hideMotor1OptionSlider()
        self.hideMotor1OptionRelative()
        self.hideMotor1OptionAbsolute()
        self.motor1Homed = False
        self.timerUsage = self.timerUsage | self.TIMER_MOTOR1_HOME
        if isChecked:
            self.sendData(self.uSTPdeviceAddress, 31, 1)
        else:
            self.sendData(self.uSTPdeviceAddress, 31, 0)


    def homeMotor1Action(self, event):
        self.sendData(self.uSTPdeviceAddress, 26, 1)
        if self.motor1Homed == False:
            if self.rboxMotor1Option.GetStringSelection() == "slider update":
                self.showMotor1OptionSlider()
            elif self.rboxMotor1Option.GetStringSelection() == "relative update":
                self.showMotor1OptionRelative()
            elif self.rboxMotor1Option.GetStringSelection() == "absolute update":
                self.showMotor1OptionAbsolute()
            else:
                print ("!! unknown event for motor #1 movement option selection")
        self.motor1Homed = True
        self.motor1Position = 0
        self.motor1slider.SetValue(self.motor1Position)
        self.motor1CurrentPositionField.SetLabel(str(self.motor1Position))
        self.motor1CurrentPositionSlider.SetLabel(str(self.motor1Position))
        self.motor1CurrentPositionSlider.SetPosition((40, 180))

    def onMotor1MaxStepsSet(self, event):
        maxSteps = self.motor1MaxStepsEntry.GetValue()
        value = self.str2int(maxSteps)
        if (value == 100000 or value > self.defaultMaxMotorSteps):
            self.motor1MaxStepsValid = False
            self.motor1MaxStepsErrorShown = True
            self.errorMotor1MaxSteps.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR1_ABS
        else:
            self.motor1MaxSteps = value
            self.motor1MaxStepsValid = True
            self.motor1MaxStepsErrorShown = False
            self.errorMotor1MaxSteps.Hide()
            # require homing
            self.hideMotor1OptionSlider()
            self.hideMotor1OptionRelative()
            self.hideMotor1OptionAbsolute()
            self.motor1Homed = False
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR1_HOME
            # re-define slider maximum
            self.motor1slider.SetMax(self.motor1MaxSteps)
            # set "focus" to motor #1 and set new maximum step range
            self.sendData(self.uSTPdeviceAddress, 21, 0)
            subAddress = (int)(value / 256)
            dataValue = value - (subAddress * 256)
            self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)

    def hideMotor1OptionSlider(self):
        self.motor1slider.Hide()
        self.textMotor1slider1.Hide()
        self.textMotor1slider2.Hide()
        self.textMotor1slider3.Hide()
        self.motor1EntrySet.Hide()
        self.motor1CurrentPositionSlider.Hide()

    def hideMotor1OptionRelative(self):
        self.rboxMotor1.Hide()
        self.relPosMotor1Box.Hide()
        self.motor1RelPositionEntry.Hide()
        self.buttonMotor1RelPositionSet.Hide()
        self.errorMotor1RelPosition.Hide()
        self.motor1CurrentPositionText.Hide()
        self.motor1CurrentPositionField.Hide()

    def hideMotor1OptionAbsolute(self):
        self.absPosMotor1Box.Hide()
        self.motor1AbsPositionEntry.Hide()
        self.buttonMotor1AbsPositionSet.Hide()
        self.errorMotor1AbsPosition.Hide()
        self.motor1CurrentPositionText.Hide()
        self.motor1CurrentPositionField.Hide()

    def showMotor1OptionSlider(self):
        self.motor1CurrentPositionText.Hide()
        self.motor1CurrentPositionField.Hide()
        self.motor1slider.Show()
        self.textMotor1slider1.Show()
        self.textMotor1slider2.Show()
        self.textMotor1slider3.Show()
        self.motor1EntrySet.Show()
        self.motor1CurrentPositionSlider.Show()

    def showMotor1OptionRelative(self):
        self.rboxMotor1.Show()
        self.relPosMotor1Box.Show()
        self.motor1RelPositionEntry.Show()
        self.buttonMotor1RelPositionSet.Show()
        self.motor1CurrentPositionText.Show()
        self.motor1CurrentPositionField.Show()

    def showMotor1OptionAbsolute(self):
        self.absPosMotor1Box.Show()
        self.motor1AbsPositionEntry.Show()
        self.buttonMotor1AbsPositionSet.Show()
        self.motor1CurrentPositionText.Show()
        self.motor1CurrentPositionField.Show()

    def motor1MovementOptionSelect(self, event):
        if self.motor1Homed == True:
            if self.rboxMotor1Option.GetStringSelection() == "slider update":
                self.hideMotor1OptionRelative()
                self.hideMotor1OptionAbsolute()
                self.motor1CurrentPositionSlider.SetLabel(str(self.motor1Position))
                self.motor1slider.SetValue(self.motor1Position)
                # position = "0"    --> xpos = 40
                # position = "max"  --> xpos = 405
                xpos = 40
                xspan = 405 - 40
                if self.motor1Position != 0:
                    xpos = xpos + int (( xspan * self.motor1Position ) / self.motor1MaxSteps)
                self.motor1CurrentPositionSlider.SetPosition((xpos, 180))
                self.showMotor1OptionSlider()
            elif self.rboxMotor1Option.GetStringSelection() == "relative update":
                self.hideMotor1OptionSlider()
                self.hideMotor1OptionAbsolute()
                self.motor1CurrentPositionField.SetLabel(str(self.motor1Position))
                self.showMotor1OptionRelative()
            elif self.rboxMotor1Option.GetStringSelection() == "absolute update":
                self.hideMotor1OptionSlider()
                self.hideMotor1OptionRelative()
                self.motor1CurrentPositionField.SetLabel(str(self.motor1Position))
                self.showMotor1OptionAbsolute()
            else:
                print ("!! unknown event for motor #1 movement option selection")

    def onMotor1SliderScroll(self, e):
        obj = e.GetEventObject()
        sliderMotor1Position = obj.GetValue()
        self.motor1CurrentPositionSlider.SetLabel(str(sliderMotor1Position))
        # position = "0"    --> xpos = 40
        # position = "max"  --> xpos = 405
        xpos = 40
        xspan = 405 - 40
        if sliderMotor1Position != 0:
            xpos = xpos + int (( xspan * sliderMotor1Position ) / self.motor1MaxSteps)
        self.motor1CurrentPositionSlider.SetPosition((xpos, 180))

    def onMotor1SliderSet(self, event):
        value = self.motor1slider.GetValue()
        self.motor1Position = value
        print ("    motor #1 position is", self.motor1Position)
        # set "focus" on motor #1 and determine subaddress and data
        self.sendData(self.uSTPdeviceAddress, 20, 0)
        subAddress = (int)(value / 256)
        dataValue = value - (subAddress * 256)
        self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)

    def onMotor1DirSelect(self, event):
        if self.rboxMotor1.GetStringSelection() == "cw":
            self.motor1Direction = "cw"
            print ("     motor #1 direction is CW")
        else:
            self.motor1Direction = "ccw"
            print ("     motor #1 direction is CCW")

    def onMotor1PosRelativeSet(self, event):
        relativeValue = self.motor1RelPositionEntry.GetValue()
        print ("     motor #1 current position is", self.motor1Position)
        print ("              relative step is", relativeValue)
        print ("              direction is", self.motor1Direction)

        value = self.str2int(relativeValue)
        if ((value != 100000) and (value < 128)):
            if self.motor1Direction == "cw":
                newPosition = self.motor1Position + value
            else:
                newPosition = self.motor1Position - value
        if (value > 127) or (newPosition > self.motor1MaxSteps) or (newPosition < 0):
            self.motor1PositionValid = False
            self.motor1RelPosEntryErrorShown = True
            self.errorMotor1RelPosition.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR1_REL
        else:
            self.motor1Position = newPosition
            self.motor1PositionValid = True
            self.motor1RelPosEntryErrorShown = False
            self.errorMotor1RelPosition.Hide()
            self.motor1slider.SetValue(self.motor1Position)
            self.motor1CurrentPositionField.SetLabel(str(self.motor1Position))
            self.motor1CurrentPositionSlider.SetLabel(str(self.motor1Position))
            xpos = 40
            xspan = 405 - 40
            if self.motor1Position != 0:
                xpos = xpos + int (( xspan * self.motor1Position ) / self.motor1MaxSteps)
            self.motor1CurrentPositionSlider.SetPosition((xpos, 180))
            print ("     motor #1 updated position is", self.motor1Position)
            # create correct command subaddress and data
            if value != 0:
                if self.motor1Direction == "cw":
                    self.sendData(self.uSTPdeviceAddress, 22, value)
                else:
                    self.sendData(self.uSTPdeviceAddress, 22, (value+128))

    def onMotor1PosAbsoluteSet(self, event):
        absoluteValue = self.motor1AbsPositionEntry.GetValue()
        print ("     motor #1 current position is", self.motor1Position)
        value = self.str2int(absoluteValue)
        if (value == 100000) or (value > self.motor1MaxSteps):
            self.motor1PositionValid = False
            self.motor1AbsPosEntryErrorShown = True
            self.errorMotor1AbsPosition.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR1_ABS
        else:
            self.motor1Position = value
            self.motor1PositionValid = True
            self.motor1AbsPosEntryErrorShown = False
            self.errorMotor1AbsPosition.Hide()
            self.motor1slider.SetValue(self.motor1Position)
            self.motor1CurrentPositionField.SetLabel(str(self.motor1Position))
            self.motor1CurrentPositionSlider.SetLabel(str(self.motor1Position))
            xpos = 40
            xspan = 405 - 40
            if self.motor1Position != 0:
                xpos = xpos + int (( xspan * self.motor1Position ) / self.motor1MaxSteps)
            self.motor1CurrentPositionSlider.SetPosition((xpos, 180))
            print ("     motor #1 updated position is", self.motor1Position)
            # set "focus" on motor #1 and determine subaddress and data
            self.sendData(self.uSTPdeviceAddress, 20, 0)
            if value == self.motor1MaxSteps:
                value = 0
            subAddress = (int)(value / 256)
            dataValue = value - (subAddress * 256)
            self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)


# =================================================================================================

    def useHomeSensor2Checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.motor2UsesHomeSensor = True
            print ("    motor #2 uses its HOME sensor")
        else:
            self.motor2UsesHomeSensor = False
            print ("    motor #2 does not use its HOME sensor")
        # require homing
        self.hideMotor2OptionSlider()
        self.hideMotor2OptionRelative()
        self.hideMotor2OptionAbsolute()
        self.motor2Homed = False
        self.timerUsage = self.timerUsage | self.TIMER_MOTOR2_HOME
        if isChecked:
            self.sendData(self.uSTPdeviceAddress, 32, 1)
        else:
            self.sendData(self.uSTPdeviceAddress, 32, 0)

    def homeMotor2Action(self, event):
        self.sendData(self.uSTPdeviceAddress, 27, 1)
        if self.motor2Homed == False:
            if self.rboxMotor2Option.GetStringSelection() == "slider update":
                self.showMotor2OptionSlider()
            elif self.rboxMotor2Option.GetStringSelection() == "relative update":
                self.showMotor2OptionRelative()
            elif self.rboxMotor2Option.GetStringSelection() == "absolute update":
                self.showMotor2OptionAbsolute()
            else:
                print ("!! unknown event for motor #2 movement option selection")
        self.motor2Homed = True
        self.motor2Position = 0
        self.motor2slider.SetValue(self.motor2Position)
        self.motor2CurrentPositionField.SetLabel(str(self.motor2Position))
        self.motor2CurrentPositionSlider.SetLabel(str(self.motor2Position))
        self.motor2CurrentPositionSlider.SetPosition((40, 180))

    def onMotor2MaxStepsSet(self, event):
        maxSteps = self.motor2MaxStepsEntry.GetValue()
        value = self.str2int(maxSteps)
        if (value == 100000 or value > self.defaultMaxMotorSteps):
            self.motor2MaxStepsValid = False
            self.motor2MaxStepsErrorShown = True
            self.errorMotor2MaxSteps.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR2_ABS
        else:
            self.motor2MaxSteps = value
            self.motor2MaxStepsValid = True
            self.motor2MaxStepsErrorShown = False
            self.errorMotor2MaxSteps.Hide()
            # require homing
            self.hideMotor2OptionSlider()
            self.hideMotor2OptionRelative()
            self.hideMotor2OptionAbsolute()
            self.motor2Homed = False
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR2_HOME
            # re-define slider maximum
            self.motor2slider.SetMax(self.motor2MaxSteps)
            # set "focus" to motor #2 and set new maximum step range
            self.sendData(self.uSTPdeviceAddress, 21, 1)
            subAddress = (int)(value / 256)
            dataValue = value - (subAddress * 256)
            self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)

    def hideMotor2OptionSlider(self):
        self.motor2slider.Hide()
        self.textMotor2slider1.Hide()
        self.textMotor2slider2.Hide()
        self.textMotor2slider3.Hide()
        self.motor2EntrySet.Hide()
        self.motor2CurrentPositionSlider.Hide()

    def hideMotor2OptionRelative(self):
        self.rboxMotor2.Hide()
        self.relPosMotor2Box.Hide()
        self.motor2RelPositionEntry.Hide()
        self.buttonMotor2RelPositionSet.Hide()
        self.errorMotor2RelPosition.Hide()
        self.motor2CurrentPositionText.Hide()
        self.motor2CurrentPositionField.Hide()

    def hideMotor2OptionAbsolute(self):
        self.absPosMotor2Box.Hide()
        self.motor2AbsPositionEntry.Hide()
        self.buttonMotor2AbsPositionSet.Hide()
        self.errorMotor2AbsPosition.Hide()
        self.motor2CurrentPositionText.Hide()
        self.motor2CurrentPositionField.Hide()

    def showMotor2OptionSlider(self):
        self.motor2CurrentPositionText.Hide()
        self.motor2CurrentPositionField.Hide()
        self.motor2slider.Show()
        self.textMotor2slider1.Show()
        self.textMotor2slider2.Show()
        self.textMotor2slider3.Show()
        self.motor2EntrySet.Show()
        self.motor2CurrentPositionSlider.Show()

    def showMotor2OptionRelative(self):
        self.rboxMotor2.Show()
        self.relPosMotor2Box.Show()
        self.motor2RelPositionEntry.Show()
        self.buttonMotor2RelPositionSet.Show()
        self.motor2CurrentPositionText.Show()
        self.motor2CurrentPositionField.Show()

    def showMotor2OptionAbsolute(self):
        self.absPosMotor2Box.Show()
        self.motor2AbsPositionEntry.Show()
        self.buttonMotor2AbsPositionSet.Show()
        self.motor2CurrentPositionText.Show()
        self.motor2CurrentPositionField.Show()

    def motor2MovementOptionSelect(self, event):
        if self.motor2Homed == True:
            if self.rboxMotor2Option.GetStringSelection() == "slider update":
                self.hideMotor2OptionRelative()
                self.hideMotor2OptionAbsolute()
                self.motor2CurrentPositionSlider.SetLabel(str(self.motor2Position))
                self.motor2slider.SetValue(self.motor2Position)
                # position = "0"    --> xpos = 40
                # position = "max"  --> xpos = 405
                xpos = 40
                xspan = 405 - 40
                if self.motor2Position != 0:
                    xpos = xpos + int (( xspan * self.motor2Position ) / self.motor2MaxSteps)
                self.motor2CurrentPositionSlider.SetPosition((xpos, 180))
                self.showMotor2OptionSlider()
            elif self.rboxMotor2Option.GetStringSelection() == "relative update":
                self.hideMotor2OptionSlider()
                self.hideMotor2OptionAbsolute()
                self.motor2CurrentPositionField.SetLabel(str(self.motor2Position))
                self.showMotor2OptionRelative()
            elif self.rboxMotor2Option.GetStringSelection() == "absolute update":
                self.hideMotor2OptionSlider()
                self.hideMotor2OptionRelative()
                self.motor2CurrentPositionField.SetLabel(str(self.motor2Position))
                self.showMotor2OptionAbsolute()
            else:
                print ("!! unknown event for motor #2 movement option selection")

    def onMotor2SliderScroll(self, e):
        obj = e.GetEventObject()
        sliderMotor2Position = obj.GetValue()
        self.motor2CurrentPositionSlider.SetLabel(str(sliderMotor2Position))
        # position = "0"    --> xpos = 40
        # position = "max"  --> xpos = 405
        xpos = 40
        xspan = 405 - 40
        if sliderMotor2Position != 0:
            xpos = xpos + int (( xspan * sliderMotor2Position ) / self.motor2MaxSteps)
        self.motor2CurrentPositionSlider.SetPosition((xpos, 180))

    def onMotor2SliderSet(self, event):
        value = self.motor2slider.GetValue()
        self.motor2Position = value
        print ("    motor #2 position is", self.motor2Position)
        # set "focus" on motor #2 and determine subaddress and data
        self.sendData(self.uSTPdeviceAddress, 20, 1)
        subAddress = (int)(value / 256)
        dataValue = value - (subAddress * 256)
        self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)

    def onMotor2DirSelect(self, event):
        if self.rboxMotor2.GetStringSelection() == "cw":
            self.motor2Direction = "cw"
            print ("     motor #2 direction is CW")
        else:
            self.motor2Direction = "ccw"
            print ("     motor #2 direction is CCW")

    def onMotor2PosRelativeSet(self, event):
        relativeValue = self.motor2RelPositionEntry.GetValue()
        print ("     motor #2 current position is", self.motor2Position)
        print ("              relative step is", relativeValue)
        print ("              direction is", self.motor2Direction)

        value = self.str2int(relativeValue)
        if ((value != 100000) and (value < 128)):
            if self.motor2Direction == "cw":
                newPosition = self.motor2Position + value
            else:
                newPosition = self.motor2Position - value
        if (value > 127) or (newPosition > self.motor2MaxSteps) or (newPosition < 0):
            self.motor2PositionValid = False
            self.motor2RelPosEntryErrorShown = True
            self.errorMotor2RelPosition.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR2_REL
        else:
            self.motor2Position = newPosition
            self.motor2PositionValid = True
            self.motor2RelPosEntryErrorShown = False
            self.errorMotor2RelPosition.Hide()
            self.motor2slider.SetValue(self.motor2Position)
            self.motor2CurrentPositionField.SetLabel(str(self.motor2Position))
            self.motor2CurrentPositionSlider.SetLabel(str(self.motor2Position))
            xpos = 40
            xspan = 405 - 40
            if self.motor2Position != 0:
                xpos = xpos + int (( xspan * self.motor2Position ) / self.motor2MaxSteps)
            self.motor2CurrentPositionSlider.SetPosition((xpos, 180))
            print ("     motor #2 updated position is", self.motor2Position)
            # create correct command subaddress and data
            if value != 0:
                if self.motor1Direction == "cw":
                    self.sendData(self.uSTPdeviceAddress, 23, value)
                else:
                    self.sendData(self.uSTPdeviceAddress, 23, (value+128))

    def onMotor2PosAbsoluteSet(self, event):
        absoluteValue = self.motor2AbsPositionEntry.GetValue()
        print ("     motor #2 current position is", self.motor2Position)
        value = self.str2int(absoluteValue)
        if (value == 100000) or (value > self.motor2MaxSteps):
            self.motor2PositionValid = False
            self.motor2AbsPosEntryErrorShown = True
            self.errorMotor2AbsPosition.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR2_ABS
        else:
            self.motor2Position = value
            self.motor2PositionValid = True
            self.motor2AbsPosEntryErrorShown = False
            self.errorMotor2AbsPosition.Hide()
            self.motor2slider.SetValue(self.motor2Position)
            self.motor2CurrentPositionField.SetLabel(str(self.motor2Position))
            self.motor2CurrentPositionSlider.SetLabel(str(self.motor2Position))
            xpos = 40
            xspan = 405 - 40
            if self.motor2Position != 0:
                xpos = xpos + int (( xspan * self.motor2Position ) / self.motor2MaxSteps)
            self.motor2CurrentPositionSlider.SetPosition((xpos, 180))
            print ("     motor #2 updated position is", self.motor2Position)
            # set "focus" on motor #2 and determine subaddress and data
            self.sendData(self.uSTPdeviceAddress, 20, 1)
            if value == self.motor2MaxSteps:
                value = 0
            subAddress = (int)(value / 256)
            dataValue = value - (subAddress * 256)
            self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)


# =================================================================================================

    def useHomeSensor3Checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.motor3UsesHomeSensor = True
            print ("    motor #3 uses its HOME sensor")
        else:
            self.motor3UsesHomeSensor = False
            print ("    motor #3 does not use its HOME sensor")
        # require homing
        self.hideMotor3OptionSlider()
        self.hideMotor3OptionRelative()
        self.hideMotor3OptionAbsolute()
        self.motor3Homed = False
        self.timerUsage = self.timerUsage | self.TIMER_MOTOR3_HOME
        if isChecked:
            self.sendData(self.uSTPdeviceAddress, 33, 1)
        else:
            self.sendData(self.uSTPdeviceAddress, 33, 0)

    def homeMotor3Action(self, event):
        self.sendData(self.uSTPdeviceAddress, 28, 1)
        if self.motor3Homed == False:
            if self.rboxMotor3Option.GetStringSelection() == "slider update":
                self.showMotor3OptionSlider()
            elif self.rboxMotor3Option.GetStringSelection() == "relative update":
                self.showMotor3OptionRelative()
            elif self.rboxMotor3Option.GetStringSelection() == "absolute update":
                self.showMotor3OptionAbsolute()
            else:
                print ("!! unknown event for motor #3 movement option selection")
        self.motor3Homed = True
        self.motor3Position = 0
        self.motor3slider.SetValue(self.motor3Position)
        self.motor3CurrentPositionField.SetLabel(str(self.motor3Position))
        self.motor3CurrentPositionSlider.SetLabel(str(self.motor3Position))
        self.motor3CurrentPositionSlider.SetPosition((40, 180))

    def onMotor3MaxStepsSet(self, event):
        maxSteps = self.motor3MaxStepsEntry.GetValue()
        value = self.str2int(maxSteps)
        if (value == 100000 or value > self.defaultMaxMotorSteps):
            self.motor3MaxStepsValid = False
            self.motor3MaxStepsErrorShown = True
            self.errorMotor3MaxSteps.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR3_ABS
        else:
            self.motor3MaxSteps = value
            self.motor3MaxStepsValid = True
            self.motor3MaxStepsErrorShown = False
            self.errorMotor3MaxSteps.Hide()
            # require homing
            self.hideMotor3OptionSlider()
            self.hideMotor3OptionRelative()
            self.hideMotor3OptionAbsolute()
            self.motor3Homed = False
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR3_HOME
            # re-define slider maximum
            self.motor3slider.SetMax(self.motor3MaxSteps)
            # set "focus" to motor #3 and set new maximum step range
            self.sendData(self.uSTPdeviceAddress, 21, 2)
            subAddress = (int)(value / 256)
            dataValue = value - (subAddress * 256)
            self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)

    def hideMotor3OptionSlider(self):
        self.motor3slider.Hide()
        self.textMotor3slider1.Hide()
        self.textMotor3slider2.Hide()
        self.textMotor3slider3.Hide()
        self.motor3EntrySet.Hide()
        self.motor3CurrentPositionSlider.Hide()

    def hideMotor3OptionRelative(self):
        self.rboxMotor3.Hide()
        self.relPosMotor3Box.Hide()
        self.motor3RelPositionEntry.Hide()
        self.buttonMotor3RelPositionSet.Hide()
        self.errorMotor3RelPosition.Hide()
        self.motor3CurrentPositionText.Hide()
        self.motor3CurrentPositionField.Hide()

    def hideMotor3OptionAbsolute(self):
        self.absPosMotor3Box.Hide()
        self.motor3AbsPositionEntry.Hide()
        self.buttonMotor3AbsPositionSet.Hide()
        self.errorMotor3AbsPosition.Hide()
        self.motor3CurrentPositionText.Hide()
        self.motor3CurrentPositionField.Hide()

    def showMotor3OptionSlider(self):
        self.motor3CurrentPositionText.Hide()
        self.motor3CurrentPositionField.Hide()
        self.motor3slider.Show()
        self.textMotor3slider1.Show()
        self.textMotor3slider2.Show()
        self.textMotor3slider3.Show()
        self.motor3EntrySet.Show()
        self.motor3CurrentPositionSlider.Show()

    def showMotor3OptionRelative(self):
        self.rboxMotor3.Show()
        self.relPosMotor3Box.Show()
        self.motor3RelPositionEntry.Show()
        self.buttonMotor3RelPositionSet.Show()
        self.motor3CurrentPositionText.Show()
        self.motor3CurrentPositionField.Show()

    def showMotor3OptionAbsolute(self):
        self.absPosMotor3Box.Show()
        self.motor3AbsPositionEntry.Show()
        self.buttonMotor3AbsPositionSet.Show()
        self.motor3CurrentPositionText.Show()
        self.motor3CurrentPositionField.Show()

    def motor3MovementOptionSelect(self, event):
        if self.motor3Homed == True:
            if self.rboxMotor3Option.GetStringSelection() == "slider update":
                self.hideMotor3OptionRelative()
                self.hideMotor3OptionAbsolute()
                self.motor3CurrentPositionSlider.SetLabel(str(self.motor3Position))
                self.motor3slider.SetValue(self.motor3Position)
                # position = "0"    --> xpos = 40
                # position = "max"  --> xpos = 405
                xpos = 40
                xspan = 405 - 40
                if self.motor3Position != 0:
                    xpos = xpos + int (( xspan * self.motor3Position ) / self.motor3MaxSteps)
                self.motor3CurrentPositionSlider.SetPosition((xpos, 180))
                self.showMotor3OptionSlider()
            elif self.rboxMotor3Option.GetStringSelection() == "relative update":
                self.hideMotor3OptionSlider()
                self.hideMotor3OptionAbsolute()
                self.motor3CurrentPositionField.SetLabel(str(self.motor3Position))
                self.showMotor3OptionRelative()
            elif self.rboxMotor3Option.GetStringSelection() == "absolute update":
                self.hideMotor3OptionSlider()
                self.hideMotor3OptionRelative()
                self.motor3CurrentPositionField.SetLabel(str(self.motor3Position))
                self.showMotor3OptionAbsolute()
            else:
                print ("!! unknown event for motor #3 movement option selection")

    def onMotor3SliderScroll(self, e):
        obj = e.GetEventObject()
        sliderMotor3Position = obj.GetValue()
        self.motor3CurrentPositionSlider.SetLabel(str(sliderMotor3Position))
        # position = "0"    --> xpos = 40
        # position = "max"  --> xpos = 405
        xpos = 40
        xspan = 405 - 40
        if sliderMotor3Position != 0:
            xpos = xpos + int (( xspan * sliderMotor3Position ) / self.motor3MaxSteps)
        self.motor3CurrentPositionSlider.SetPosition((xpos, 180))

    def onMotor3SliderSet(self, event):
        value = self.motor3slider.GetValue()
        self.motor3Position = value
        print ("    motor #3 position is", self.motor3Position)
        # set "focus" on motor #3 and determine subaddress and data
        self.sendData(self.uSTPdeviceAddress, 20, 2)
        subAddress = (int)(value / 256)
        dataValue = value - (subAddress * 256)
        self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)

    def onMotor3DirSelect(self, event):
        if self.rboxMotor3.GetStringSelection() == "cw":
            self.motor3Direction = "cw"
            print ("     motor #3 direction is CW")
        else:
            self.motor3Direction = "ccw"
            print ("     motor #3 direction is CCW")

    def onMotor3PosRelativeSet(self, event):
        relativeValue = self.motor3RelPositionEntry.GetValue()
        print ("     motor #3 current position is", self.motor3Position)
        print ("              relative step is", relativeValue)
        print ("              direction is", self.motor3Direction)

        value = self.str2int(relativeValue)
        if ((value != 100000) and (value < 128)):
            if self.motor3Direction == "cw":
                newPosition = self.motor3Position + value
            else:
                newPosition = self.motor3Position - value
        if (value > 127) or (newPosition > self.motor3MaxSteps) or (newPosition < 0):
            self.motor3PositionValid = False
            self.motor3RelPosEntryErrorShown = True
            self.errorMotor3RelPosition.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR3_REL
        else:
            self.motor3Position = newPosition
            self.motor3PositionValid = True
            self.motor3RelPosEntryErrorShown = False
            self.errorMotor3RelPosition.Hide()
            self.motor3slider.SetValue(self.motor3Position)
            self.motor3CurrentPositionField.SetLabel(str(self.motor3Position))
            self.motor3CurrentPositionSlider.SetLabel(str(self.motor3Position))
            xpos = 40
            xspan = 405 - 40
            if self.motor3Position != 0:
                xpos = xpos + int (( xspan * self.motor3Position ) / self.motor3MaxSteps)
            self.motor3CurrentPositionSlider.SetPosition((xpos, 180))
            print ("    motor #3 updated position is", self.motor3Position)
            # create correct command subaddress and data
            if value != 0:
                if self.motor1Direction == "cw":
                    self.sendData(self.uSTPdeviceAddress, 24, value)
                else:
                    self.sendData(self.uSTPdeviceAddress, 24, (value+128))

    def onMotor3PosAbsoluteSet(self, event):
        absoluteValue = self.motor3AbsPositionEntry.GetValue()
        print ("     motor #3 current position is", self.motor3Position)
        value = self.str2int(absoluteValue)
        if (value == 100000) or (value > self.motor3MaxSteps):
            self.motor3PositionValid = False
            self.motor3AbsPosEntryErrorShown = True
            self.errorMotor3AbsPosition.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR3_ABS
        else:
            self.motor3Position = value
            self.motor3PositionValid = True
            self.motor3AbsPosEntryErrorShown = False
            self.errorMotor3AbsPosition.Hide()
            self.motor3slider.SetValue(self.motor3Position)
            self.motor3CurrentPositionField.SetLabel(str(self.motor3Position))
            self.motor3CurrentPositionSlider.SetLabel(str(self.motor3Position))
            xpos = 40
            xspan = 405 - 40
            if self.motor3Position != 0:
                xpos = xpos + int (( xspan * self.motor3Position ) / self.motor3MaxSteps)
            self.motor3CurrentPositionSlider.SetPosition((xpos, 180))
            print ("     motor #3 updated position is", self.motor3Position)
            # set "focus" on motor #3 and determine subaddress and data
            self.sendData(self.uSTPdeviceAddress, 20, 2)
            if value == self.motor3MaxSteps:
                value = 0
            subAddress = (int)(value / 256)
            dataValue = value - (subAddress * 256)
            self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)


# =================================================================================================

    def useHomeSensor4Checkbox(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.motor4UsesHomeSensor = True
            print ("    motor #4 uses its HOME sensor")
        else:
            self.motor4UsesHomeSensor = False
            print ("    motor #4 does not use its HOME sensor")
        # require homing
        self.hideMotor4OptionSlider()
        self.hideMotor4OptionRelative()
        self.hideMotor4OptionAbsolute()
        self.motor4Homed = False
        self.timerUsage = self.timerUsage | self.TIMER_MOTOR4_HOME
        if isChecked:
            self.sendData(self.uSTPdeviceAddress, 34, 1)
        else:
            self.sendData(self.uSTPdeviceAddress, 34, 0)

    def homeMotor4Action(self, event):
        self.sendData(self.uSTPdeviceAddress, 29, 1)
        if self.motor4Homed == False:
            if self.rboxMotor4Option.GetStringSelection() == "slider update":
                self.showMotor4OptionSlider()
            elif self.rboxMotor4Option.GetStringSelection() == "relative update":
                self.showMotor4OptionRelative()
            elif self.rboxMotor4Option.GetStringSelection() == "absolute update":
                self.showMotor4OptionAbsolute()
            else:
                print ("!! unknown event for motor #4 movement option selection")
        self.motor4Homed = True
        self.motor4Position = 0
        self.motor4slider.SetValue(self.motor4Position)
        self.motor4CurrentPositionField.SetLabel(str(self.motor4Position))
        self.motor4CurrentPositionSlider.SetLabel(str(self.motor4Position))
        self.motor4CurrentPositionSlider.SetPosition((40, 180))

    def onMotor4MaxStepsSet(self, event):
        maxSteps = self.motor4MaxStepsEntry.GetValue()
        value = self.str2int(maxSteps)
        if (value == 100000 or value > self.defaultMaxMotorSteps):
            self.motor4MaxStepsValid = False
            self.motor4MaxStepsErrorShown = True
            self.errorMotor4MaxSteps.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR4_ABS
        else:
            self.motor4MaxSteps = value
            self.motor4MaxStepsValid = True
            self.motor4MaxStepsErrorShown = False
            self.errorMotor4MaxSteps.Hide()
            # require homing
            self.hideMotor4OptionSlider()
            self.hideMotor4OptionRelative()
            self.hideMotor4OptionAbsolute()
            self.motor4Homed = False
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR4_HOME
            # re-define slider maximum
            self.motor4slider.SetMax(self.motor4MaxSteps)
            # set "focus" to motor #4 and set new maximum step range
            self.sendData(self.uSTPdeviceAddress, 21, 3)
            subAddress = (int)(value / 256)
            dataValue = value - (subAddress * 256)
            self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)

    def hideMotor4OptionSlider(self):
        self.motor4slider.Hide()
        self.textMotor4slider1.Hide()
        self.textMotor4slider2.Hide()
        self.textMotor4slider3.Hide()
        self.motor4EntrySet.Hide()
        self.motor4CurrentPositionSlider.Hide()

    def hideMotor4OptionRelative(self):
        self.rboxMotor4.Hide()
        self.relPosMotor4Box.Hide()
        self.motor4RelPositionEntry.Hide()
        self.buttonMotor4RelPositionSet.Hide()
        self.errorMotor4RelPosition.Hide()
        self.motor4CurrentPositionText.Hide()
        self.motor4CurrentPositionField.Hide()

    def hideMotor4OptionAbsolute(self):
        self.absPosMotor4Box.Hide()
        self.motor4AbsPositionEntry.Hide()
        self.buttonMotor4AbsPositionSet.Hide()
        self.errorMotor4AbsPosition.Hide()
        self.motor4CurrentPositionText.Hide()
        self.motor4CurrentPositionField.Hide()

    def showMotor4OptionSlider(self):
        self.motor4CurrentPositionText.Hide()
        self.motor4CurrentPositionField.Hide()
        self.motor4slider.Show()
        self.textMotor4slider1.Show()
        self.textMotor4slider2.Show()
        self.textMotor4slider3.Show()
        self.motor4EntrySet.Show()
        self.motor4CurrentPositionSlider.Show()

    def showMotor4OptionRelative(self):
        self.rboxMotor4.Show()
        self.relPosMotor4Box.Show()
        self.motor4RelPositionEntry.Show()
        self.buttonMotor4RelPositionSet.Show()
        self.motor4CurrentPositionText.Show()
        self.motor4CurrentPositionField.Show()

    def showMotor4OptionAbsolute(self):
        self.absPosMotor4Box.Show()
        self.motor4AbsPositionEntry.Show()
        self.buttonMotor4AbsPositionSet.Show()
        self.motor4CurrentPositionText.Show()
        self.motor4CurrentPositionField.Show()

    def motor4MovementOptionSelect(self, event):
        if self.motor4Homed == True:
            if self.rboxMotor4Option.GetStringSelection() == "slider update":
                self.hideMotor4OptionRelative()
                self.hideMotor4OptionAbsolute()
                self.motor4CurrentPositionSlider.SetLabel(str(self.motor4Position))
                self.motor4slider.SetValue(self.motor4Position)
                # position = "0"    --> xpos = 40
                # position = "max"  --> xpos = 405
                xpos = 40
                xspan = 405 - 40
                if self.motor4Position != 0:
                    xpos = xpos + int (( xspan * self.motor4Position ) / self.motor4MaxSteps)
                self.motor4CurrentPositionSlider.SetPosition((xpos, 180))
                self.showMotor4OptionSlider()
            elif self.rboxMotor4Option.GetStringSelection() == "relative update":
                self.hideMotor4OptionSlider()
                self.hideMotor4OptionAbsolute()
                self.motor4CurrentPositionField.SetLabel(str(self.motor4Position))
                self.showMotor4OptionRelative()
            elif self.rboxMotor4Option.GetStringSelection() == "absolute update":
                self.hideMotor4OptionSlider()
                self.hideMotor4OptionRelative()
                self.motor4CurrentPositionField.SetLabel(str(self.motor4Position))
                self.showMotor4OptionAbsolute()
            else:
                print ("!! unknown event for motor #4 movement option selection")

    def onMotor4SliderScroll(self, e):
        obj = e.GetEventObject()
        sliderMotor4Position = obj.GetValue()
        self.motor4CurrentPositionSlider.SetLabel(str(sliderMotor4Position))
        # position = "0"    --> xpos = 40
        # position = "max"  --> xpos = 405
        xpos = 40
        xspan = 405 - 40
        if sliderMotor4Position != 0:
            xpos = xpos + int (( xspan * sliderMotor4Position ) / self.motor4MaxSteps)
        self.motor4CurrentPositionSlider.SetPosition((xpos, 180))

    def onMotor4SliderSet(self, event):
        value = self.motor4slider.GetValue()
        self.motor4Position = value
        print ("    motor #4 position is", self.motor4Position)
        # set "focus" on motor #4 and determine subaddress and data
        self.sendData(self.uSTPdeviceAddress, 20, 3)
        subAddress = (int)(value / 256)
        dataValue = value - (subAddress * 256)
        self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)

    def onMotor4DirSelect(self, event):
        if self.rboxMotor4.GetStringSelection() == "cw":
            self.motor4Direction = "cw"
            print ("     motor #4 direction is CW")
        else:
            self.motor4Direction = "ccw"
            print ("     motor #4 direction is CCW")

    def onMotor4PosRelativeSet(self, event):
        relativeValue = self.motor4RelPositionEntry.GetValue()
        print ("     motor #4 current position is", self.motor4Position)
        print ("              relative step is", relativeValue)
        print ("              direction is", self.motor4Direction)

        value = self.str2int(relativeValue)
        if ((value != 100000) and (value < 128)):
            if self.motor4Direction == "cw":
                newPosition = self.motor4Position + value
            else:
                newPosition = self.motor4Position - value
        if (value > 127) or (newPosition > self.motor4MaxSteps) or (newPosition < 0):
            self.motor4PositionValid = False
            self.motor4RelPosEntryErrorShown = True
            self.errorMotor4RelPosition.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR4_REL
        else:
            self.motor4Position = newPosition
            self.motor4PositionValid = True
            self.motor4RelPosEntryErrorShown = False
            self.errorMotor4RelPosition.Hide()
            self.motor4slider.SetValue(self.motor4Position)
            self.motor4CurrentPositionField.SetLabel(str(self.motor4Position))
            self.motor4CurrentPositionSlider.SetLabel(str(self.motor4Position))
            xpos = 40
            xspan = 405 - 40
            if self.motor4Position != 0:
                xpos = xpos + int (( xspan * self.motor4Position ) / self.motor4MaxSteps)
            self.motor4CurrentPositionSlider.SetPosition((xpos, 180))
            print ("     motor #4 updated position is", self.motor4Position)
            # create correct command subaddress and data
            if value != 0:
                if self.motor1Direction == "cw":
                    self.sendData(self.uSTPdeviceAddress, 25, value)
                else:
                    self.sendData(self.uSTPdeviceAddress, 25, (value+128))

    def onMotor4PosAbsoluteSet(self, event):
        absoluteValue = self.motor4AbsPositionEntry.GetValue()
        print ("     motor #4 current position is", self.motor4Position)
        value = self.str2int(absoluteValue)
        if (value == 100000) or (value > self.motor4MaxSteps):
            self.motor4PositionValid = False
            self.motor4AbsPosEntryErrorShown = True
            self.errorMotor4AbsPosition.Show()
            self.timerUsage = self.timerUsage | self.TIMER_MOTOR4_ABS
        else:
            self.motor4Position = value
            self.motor4PositionValid = True
            self.motor4AbsPosEntryErrorShown = False
            self.errorMotor4AbsPosition.Hide()
            self.motor4slider.SetValue(self.motor4Position)
            self.motor4CurrentPositionField.SetLabel(str(self.motor4Position))
            self.motor4CurrentPositionSlider.SetLabel(str(self.motor4Position))
            xpos = 40
            xspan = 405 - 40
            if self.motor4Position != 0:
                xpos = xpos + int (( xspan * self.motor4Position ) / self.motor4MaxSteps)
            self.motor4CurrentPositionSlider.SetPosition((xpos, 180))
            print ("     motor #4 updated position is", self.motor4Position)
            # set "focus" on motor #4 and determine subaddress and data
            self.sendData(self.uSTPdeviceAddress, 20, 3)
            if value == self.motor4MaxSteps:
                value = 0
            subAddress = (int)(value / 256)
            dataValue = value - (subAddress * 256)
            self.sendData(self.uSTPdeviceAddress, subAddress, dataValue)


# =================================================================================================

    def advancedSend(self, event):
        advDeviceAddress = self.deviceAddressEntry.GetValue()
        advDeviceSubAddress = self.deviceSubAddressEntry.GetValue()
        advData = self.deviceDataEntry.GetValue()
        print ("advanced data =", advDeviceAddress, advDeviceSubAddress, advData)
        allDataValid = True
        # process entry fields
        if self.validateDOAdata == True:
            if advDeviceAddress == "0x75" or advDeviceAddress == "0X75" or advDeviceAddress == "117" :
                portID = "USTP"
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
            if (subValue > 42) or (advDeviceSubAddress == ""):
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
            self.sendData(advDeviceAddress, subValue, dataValue)
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
#  COMMUNICATION  routine: send data
# =================================================================================================

    def sendData(self, address, subAddress, data):
        if self.COMMportOpened == True:
            if address == self.uSTPdeviceAddress:
                print ("... sendData to", self.commPortID, "address", address, "subAddress", subAddress, "data", data)
                if self.channelSelection == "PHCC":
                    # using PHCC Motherboard
                    if self.ComPort1.isOpen():
                        self.ComPort1.write(7)
                        adrs = bytes([address])
                        subadr = bytes([subAddress])
                        databyte = bytes([data])
                        print ("    ====> address =", adrs, "  subadr =", subadr, "  datbyt =", databyte)
                        self.ComPort1.write(adrs)
                        self.ComPort1.write(subadr)
                        self.ComPort1.write(databyte)
                    else:
                        print ("!!! COM port for microStepper is not open!")
                elif self.channelSelection == "USB":
                    if self.ComPort1.isOpen():
                        subadr = bytes([subAddress])
                        databyte = bytes([data])
                        print ("    ====> subadr =", subadr, "  datbyt =", databyte)
                        self.ComPort1.write(subadr)
                        self.ComPort1.write(databyte)
                    else:
                        print ("!!! COM port for microStepper is not open!")
                else:
                    print ("!!! no communication channel selected (software bug)")
        else:
            print ("COM port not opened: no data sent")

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
        # handle "blinking" indicators
        if (self.timerUsage & self.TIMER_COMPORT) == 0x0001:
            # COM port not (yet) assigned
            if self.commPortValid == False:
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
                self.timerUsage = self.timerUsage & ~self.TIMER_COMPORT
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR1_HOME) == 0x0002:
            # motor #1 not (yet) homed
            backgroundColor = self.buttonHomeMotor1.GetBackgroundColour()
            if self.motor1Homed == False:
                if backgroundColor == '#99ccff':
                    self.buttonHomeMotor1.SetBackgroundColour('#ffcc99')
                    self.startTimer(300)
                else:
                    self.buttonHomeMotor1.SetBackgroundColour('#99ccff')
                    self.startTimer(500)
            else:
                if backgroundColor == '#ffcc99':
                    self.buttonHomeMotor1.SetBackgroundColour('#99ccff')
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR1_HOME
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR2_HOME) == 0x0004:
            # motor #2 not (yet) homed
            backgroundColor = self.buttonHomeMotor2.GetBackgroundColour()
            if self.motor2Homed == False:
                if backgroundColor == '#99ccff':
                    self.buttonHomeMotor2.SetBackgroundColour('#ffcc99')
                    self.startTimer(300)
                else:
                    self.buttonHomeMotor2.SetBackgroundColour('#99ccff')
                    self.startTimer(500)
            else:
                if backgroundColor == '#ffcc99':
                    self.buttonHomeMotor2.SetBackgroundColour('#99ccff')
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR2_HOME
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR3_HOME) == 0x0008:
            # motor #3 not (yet) homed
            backgroundColor = self.buttonHomeMotor3.GetBackgroundColour()
            if self.motor3Homed == False:
                if backgroundColor == '#99ccff':
                    self.buttonHomeMotor3.SetBackgroundColour('#ffcc99')
                    self.startTimer(300)
                else:
                    self.buttonHomeMotor3.SetBackgroundColour('#99ccff')
                    self.startTimer(500)
            else:
                if backgroundColor == '#ffcc99':
                    self.buttonHomeMotor3.SetBackgroundColour('#99ccff')
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR3_HOME
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR4_HOME) == 0x0010:
            # motor #4 not (yet) homed
            backgroundColor = self.buttonHomeMotor4.GetBackgroundColour()
            if self.motor4Homed == False:
                if backgroundColor == '#99ccff':
                    self.buttonHomeMotor4.SetBackgroundColour('#ffcc99')
                    self.startTimer(300)
                else:
                    self.buttonHomeMotor4.SetBackgroundColour('#99ccff')
                    self.startTimer(500)
            else:
                if backgroundColor == '#ffcc99':
                    self.buttonHomeMotor4.SetBackgroundColour('#99ccff')
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR4_HOME
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR1_REL) == 0x0020:
            # motor #1 relative position running out of range
            if self.motor1PositionValid == False:
                if self.motor1RelPosEntryErrorShown == True:
                    self.motor1RelPosEntryErrorShown = False
                    self.errorMotor1RelPosition.Hide()
                    self.startTimer(300)
                else:
                    self.motor1RelPosEntryErrorShown = True
                    self.errorMotor1RelPosition.Show()
                    self.startTimer(500)
            else:
                if self.motor1RelPosEntryErrorShown == True:
                    self.motor1RelPosEntryErrorShown = False
                    self.errorMotor1RelPosition.Hide()
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR1_REL
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR2_REL) == 0x0040:
            # motor #2 relative position running out of range
            if self.motor2PositionValid == False:
                if self.motor2RelPosEntryErrorShown == True:
                    self.motor2RelPosEntryErrorShown = False
                    self.errorMotor2RelPosition.Hide()
                    self.startTimer(300)
                else:
                    self.motor2RelPosEntryErrorShown = True
                    self.errorMotor2RelPosition.Show()
                    self.startTimer(500)
            else:
                if self.motor2RelPosEntryErrorShown == True:
                    self.motor2RelPosEntryErrorShown = False
                    self.errorMotor2RelPosition.Hide()
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR2_REL
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR3_REL) == 0x0080:
            # motor #3 relative position running out of range
            if self.motor3PositionValid == False:
                if self.motor3RelPosEntryErrorShown == True:
                    self.motor3RelPosEntryErrorShown = False
                    self.errorMotor3RelPosition.Hide()
                    self.startTimer(300)
                else:
                    self.motor3RelPosEntryErrorShown = True
                    self.errorMotor3RelPosition.Show()
                    self.startTimer(500)
            else:
                if self.motor3RelPosEntryErrorShown == True:
                    self.motor3RelPosEntryErrorShown = False
                    self.errorMotor3RelPosition.Hide()
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR3_REL
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR4_REL) == 0x0100:
            # motor #4 relative position running out of range
            if self.motor4PositionValid == False:
                if self.motor4RelPosEntryErrorShown == True:
                    self.motor4RelPosEntryErrorShown = False
                    self.errorMotor4RelPosition.Hide()
                    self.startTimer(300)
                else:
                    self.motor4RelPosEntryErrorShown = True
                    self.errorMotor4RelPosition.Show()
                    self.startTimer(500)
            else:
                if self.motor4RelPosEntryErrorShown == True:
                    self.motor4RelPosEntryErrorShown = False
                    self.errorMotor4RelPosition.Hide()
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR4_REL
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR1_ABS) == 0x0200:
            # motor #1 absolute position out of range
            if self.motor1PositionValid == False:
                if self.motor1AbsPosEntryErrorShown == True:
                    self.motor1AbsPosEntryErrorShown = False
                    self.errorMotor1AbsPosition.Hide()
                    self.startTimer(300)
                else:
                    self.motor1AbsPosEntryErrorShown = True
                    self.errorMotor1AbsPosition.Show()
                    self.startTimer(500)
            else:
                if self.motor1AbsPosEntryErrorShown == True:
                    self.motor1AbsPosEntryErrorShown = False
                    self.errorMotor1AbsPosition.Hide()
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR1_ABS
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR2_ABS) == 0x0400:
            # motor #2 absolute position out of range
            if self.motor2PositionValid == False:
                if self.motor2AbsPosEntryErrorShown == True:
                    self.motor2AbsPosEntryErrorShown = False
                    self.errorMotor2AbsPosition.Hide()
                    self.startTimer(300)
                else:
                    self.motor2AbsPosEntryErrorShown = True
                    self.errorMotor2AbsPosition.Show()
                    self.startTimer(500)
            else:
                if self.motor2AbsPosEntryErrorShown == True:
                    self.motor2AbsPosEntryErrorShown = False
                    self.errorMotor2AbsPosition.Hide()
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR2_ABS
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR3_ABS) == 0x0800:
            # motor #3 absolute position out of range
            if self.motor3PositionValid == False:
                if self.motor3AbsPosEntryErrorShown == True:
                    self.motor3AbsPosEntryErrorShown = False
                    self.errorMotor3AbsPosition.Hide()
                    self.startTimer(300)
                else:
                    self.motor3AbsPosEntryErrorShown = True
                    self.errorMotor3AbsPosition.Show()
                    self.startTimer(500)
            else:
                if self.motor3AbsPosEntryErrorShown == True:
                    self.motor3AbsPosEntryErrorShown = False
                    self.errorMotor3AbsPosition.Hide()
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR3_ABS
                self.startTimer(300)
        # --
        if (self.timerUsage & self.TIMER_MOTOR4_ABS) == 0x1000:
            # motor #4 absolute position out of range
            if self.motor4PositionValid == False:
                if self.motor4AbsPosEntryErrorShown == True:
                    self.motor4AbsPosEntryErrorShown = False
                    self.errorMotor4AbsPosition.Hide()
                    self.startTimer(300)
                else:
                    self.motor4AbsPosEntryErrorShown = True
                    self.errorMotor4AbsPosition.Show()
                    self.startTimer(500)
            else:
                if self.motor4AbsPosEntryErrorShown == True:
                    self.motor4AbsPosEntryErrorShown = False
                    self.errorMotor4AbsPosition.Hide()
                self.timerUsage = self.timerUsage & ~self.TIMER_MOTOR4_ABS
                self.startTimer(300)
        # --
        if self.motor1MaxStepsValid == False:
            # motor #1 max # steps in error
            if self.motor1MaxStepsErrorShown == True:
                self.motor1MaxStepsErrorShown = False
                self.errorMotor1MaxSteps.Hide()
                self.startTimer(300)
            else:
                self.motor1MaxStepsErrorShown = True
                self.errorMotor1MaxSteps.Show()
                self.startTimer(500)
        else:
            if self.motor1MaxStepsErrorShown == True:
                self.motor1MaxStepsErrorShown = False
                self.errorMotor1MaxSteps.Hide()
            self.startTimer(300)
        # --
        if self.motor2MaxStepsValid == False:
            # motor #2 max # steps in error
            if self.motor2MaxStepsErrorShown == True:
                self.motor2MaxStepsErrorShown = False
                self.errorMotor2MaxSteps.Hide()
                self.startTimer(300)
            else:
                self.motor2MaxStepsErrorShown = True
                self.errorMotor2MaxSteps.Show()
                self.startTimer(500)
        else:
            if self.motor2MaxStepsErrorShown == True:
                self.motor2MaxStepsErrorShown = False
                self.errorMotor2MaxSteps.Hide()
            self.startTimer(300)
        # --
        if self.motor3MaxStepsValid == False:
            # motor #3 max # steps in error
            if self.motor3MaxStepsErrorShown == True:
                self.motor3MaxStepsErrorShown = False
                self.errorMotor3MaxSteps.Hide()
                self.startTimer(300)
            else:
                self.motor3MaxStepsErrorShown = True
                self.errorMotor3MaxSteps.Show()
                self.startTimer(500)
        else:
            if self.motor3MaxStepsErrorShown == True:
                self.motor3MaxStepsErrorShown = False
                self.errorMotor3MaxSteps.Hide()
            self.startTimer(300)
        # --
        if self.motor4MaxStepsValid == False:
            # motor #4 max # steps in error
            if self.motor4MaxStepsErrorShown == True:
                self.motor4MaxStepsErrorShown = False
                self.errorMotor4MaxSteps.Hide()
                self.startTimer(300)
            else:
                self.motor4MaxStepsErrorShown = True
                self.errorMotor4MaxSteps.Show()
                self.startTimer(500)
        else:
            if self.motor4MaxStepsErrorShown == True:
                self.motor4MaxStepsErrorShown = False
                self.errorMotor4MaxSteps.Hide()
            self.startTimer(300)
        # ----




###################################################################################################
class HSIFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "µStepper demonstrator", size=(600,400))
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