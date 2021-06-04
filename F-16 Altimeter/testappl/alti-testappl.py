# Install Python version 2.7.14
#    - Download from https://www.python.org/downloads/
#            - Select "Downloads" and click the button Python 2.7.14
#    - Goto the Downloads folder and double-click the downloaded "python-2.7.14.msi".
#    - You can accpet all the default settings.
#
# Install wxPython for Python 2.7
#    - if you installed Python in the default folder (C:\Python27\), enter
#    - cd c:\Python27\Scripts
#    - pip install -U wxPython
#
# Install the pyserial package
#    - pip install pyserial


import wx
import serial
import time
import math


class ALTI(wx.Frame):

    # def __init__(self):
    def __init__(self, parent):
        super(ALTI, self).__init__(parent, size=(540, 290), pos=(20,20))

        panel = wx.Panel(self)
        self.SetTitle('Altimeter Demonstrator')
        self.SetBackgroundColour('#ffffff')
        self.Show()

        self.channelSelection   = "PHCC"
        self.commPortID         = ""
        self.errorCommPortShown = True
        self.awaitUsbResponse   = False
        self.altitudeSetting    = 0
        self.timerUsage         = 0            # 0 can be used for COM sign blinking (not assigned)
                                               # 1 assigned for altitude update mode
        self.useCorrection      = True
		#                0   50  100  150  200  250  300  350  400  450  500  550  600  650  700  750  800  850  900   950
		#             -----------------------------------------------------------------------------------------------------
        self.lookup=[    0,  82, 166, 248, 320, 383, 444, 490, 540, 585, 627, 665, 708, 755, 772, 805, 848, 855, 900, 925,\
                       960,1005,1030,1080,1110,1160,1200,1250,1300,1360,1420,1495,1565,1642,1722,1795,1880,1945,2020,2085,\
                      2130,2185,2230,2280,2318,2360,2398,2435,2470,2505,2550,2555,2592,2625,2665,2702,2740,2780,2824,2865,\
                      2915,2965,3020,3095,3150,3230,3307,3385,3465,3535,3578,3680,3754,3795,3860,3915,3945,3995,4030,4070,\
                      4100,4145,4180,4220,4260,4265,4294,4330,4370,4405,4445,4470,4540,4577,4630,4680,4745,4805,4882,4955,\
                      5034,5110,5190,5250,5334,5390,5450,5550,5544,5586,5630,5664,5710,5730,5780,5800,5810,5850,5900,5930,\
                      5980,6010,6050,6080,6124,6160,6204,6250,6306,6356,6422,6490,6570,6650,6734,6804,6894,6956,7030,7084,\
                      7150,7185,7236,7270,7314,7350,7390,7420,7462,7496,7530,7550,7580,7610,7656,7690,7730,7770,7810,7850,\
                      7900,7954,8004,8070,8130,8200,8280,8350,8430,8500,8586,8660,8720,8780,8830,8880,8930,8970,9010,9050,\
                      9086,9120,9160,9190,9220,9240,9270,9310,9350,9386,9420,9460,9500,9550,9596,9656,9706,9780,9840,9920,\
                      10000]
        self.setupGUI(panel)


    def setupGUI(self, panel):
        largeFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        smallFont = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        errorImage = wx.Bitmap("error.gif")  # "error in entry" indication bitmap

        # find the available COM ports (code only for Windows)
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
        self.rbox = wx.RadioBox(panel, label = 'Communication channel', pos = (35,15),
                                choices = radioButtonList, majorDimension = 1)
        self.rbox.Bind(wx.EVT_RADIOBOX,self.onRadioBox)

        # display COM port selection
        self.textCOMMport = wx.StaticText(self, label='port', pos=(230, 48))
        self.textCOMMport.SetFont(smallFont)
        self.textCOMMport.SetForegroundColour("#000000")
        self.errorCommPort = wx.StaticBitmap(self, -1, errorImage)
        self.errorCommPort.SetPosition((335, 43))
        self.cbComm = wx.ComboBox(panel, pos=(260, 45), size=(70, 25), choices=availableCOMports, style=wx.CB_READONLY)
        self.cbComm.SetToolTip(wx.ToolTip("set COM port"))
        self.cbComm.Bind(wx.EVT_COMBOBOX, self.OnSelectCommPort)

        wx.StaticLine(panel, -1, (10, 95), (500, 3))

        # Altimeter setpoint entry
        self.textAltiEntry = wx.StaticText(self, label='altimeter setting  [feet]', pos=(35, 120))
        self.textAltiEntry.SetFont(largeFont)
        self.altiEntry = wx.TextCtrl(panel, value="0", pos=(260, 119), size=(70, 25))
        self.buttonAltiEntrySet = wx.Button(panel, label="SET", pos=(335, 119), size=(60, 25))
        self.buttonAltiEntrySet.SetToolTip(wx.ToolTip("set altitude"))
        self.buttonAltiEntrySet.SetBackgroundColour('#60a0b0')
        self.buttonAltiEntrySet.SetForegroundColour('#000000')
        self.buttonAltiEntrySet.Bind(wx.EVT_BUTTON, self.altiEntrySet)
        self.errorAltiEntry = wx.StaticBitmap(self, -1, errorImage)
        self.errorAltiEntry.SetPosition((400, 120))
        self.errorAltiEntry.Hide()
        # increment/decrement buttons
        self.buttonAltiInc = wx.Button(panel, label="+20", pos=(440, 108), size=(34, 24))
        self.buttonAltiDec = wx.Button(panel, label="-20", pos=(440, 134), size=(34, 24))
        self.buttonAltiInc.SetBackgroundColour('#CC3333')
        self.buttonAltiInc.SetForegroundColour('#ffffff')
        self.buttonAltiDec.SetBackgroundColour('#CC3333')
        self.buttonAltiDec.SetForegroundColour('#ffffff')
        self.buttonAltiInc.Bind(wx.EVT_BUTTON, self.altiIncrement)
        self.buttonAltiDec.Bind(wx.EVT_BUTTON, self.altiDecrement)

        wx.StaticLine(panel, -1, (10, 165), (500, 3))
        
        # advanced checkbox
        self.advancedMode = wx.CheckBox(panel, label='Advanced', pos=(260, 190), size=(100, 25))
        self.advancedMode.SetValue(False)
        self.Centre()
        self.advancedMode.SetToolTip(wx.ToolTip("direct command access"))
        self.Show(True)
        self.advancedMode.Bind(wx.EVT_CHECKBOX, self.advancedOption)

        # alignment checkbox
        self.alignMode = wx.CheckBox(panel, label='Align', pos=(160, 190), size=(100, 25))
        self.alignMode.SetValue(False)
        self.Centre()
        self.alignMode.SetToolTip(wx.ToolTip("stator commutation alignment"))
        self.Show(True)
        self.alignMode.Bind(wx.EVT_CHECKBOX, self.alignOption)

        # cycle 10000 range checkbox
        self.cycleMode = wx.CheckBox(panel, label='Simulate', pos=(60, 190), size=(100, 25))
        self.cycleMode.SetValue(False)
        self.Centre()
        self.cycleMode.SetToolTip(wx.ToolTip("simulate altitude inc/dec"))
        self.Show(True)
        self.cycleMode.Bind(wx.EVT_CHECKBOX, self.cycleOption)

        # advanced entry fields
        self.textDeviceAddress = wx.StaticText(self, label='DEVICE ADDRESS', pos=(68, 113))
        self.textDeviceAddress.SetToolTip(wx.ToolTip("8-bit DOA DEVICE address"))
        self.textDeviceAddress.SetFont(smallFont)
        self.textDeviceAddress.Hide()
        self.textDeviceSubAddress = wx.StaticText(self, label='SUB-ADDRESS', pos=(190, 113))
        self.textDeviceSubAddress.SetToolTip(wx.ToolTip("8-bit DOA sub-address"))
        self.textDeviceSubAddress.SetFont(smallFont)
        self.textDeviceSubAddress.Hide()
        self.textDeviceData = wx.StaticText(self, label='DATA BYTE', pos=(314, 113))
        self.textDeviceData.SetToolTip(wx.ToolTip("8-bit DOA data"))
        self.textDeviceData.SetFont(smallFont)
        self.textDeviceData.Hide()
        #
        self.deviceAddressEntry = wx.TextCtrl(panel, pos=(77, 133), size=(70, 25))
        self.deviceAddressEntry.Value = "0x41"
        self.deviceAddressEntry.Hide()
        self.deviceSubAddressEntry = wx.TextCtrl(panel, pos=(192, 133), size=(70, 25))
        self.deviceSubAddressEntry.Hide()
        self.deviceDataEntry = wx.TextCtrl(panel, pos=(307, 133), size=(70, 25))
        self.deviceDataEntry.Hide()
        self.buttonAdvancedSend = wx.Button(panel, label="SEND", pos=(425, 133), size=(75, 25))
        self.buttonAdvancedSend.SetToolTip(wx.ToolTip("send DOA device / sub-address / data"))
        self.buttonAdvancedSend.SetBackgroundColour('#80e0c0')
        self.buttonAdvancedSend.SetForegroundColour('#000000')
        self.buttonAdvancedSend.Bind(wx.EVT_BUTTON, self.advancedSend)
        self.buttonAdvancedSend.Hide()

        # alignment entry fields
        self.textAlignS1 = wx.StaticText(self, label='S1 OFFSET', pos=(85, 113))
        self.textAlignS1.SetToolTip(wx.ToolTip("Stator S1 commutation offset"))
        self.textAlignS1.SetFont(smallFont)
        self.textAlignS1.Hide()
        self.textAlignS2 = wx.StaticText(self, label='S2 OFFSET', pos=(200, 113))
        self.textAlignS2.SetToolTip(wx.ToolTip("Stator S2 commutation offset"))
        self.textAlignS2.SetFont(smallFont)
        self.textAlignS2.Hide()
        self.textAlignS3 = wx.StaticText(self, label='S3 OFFSET', pos=(314, 113))
        self.textAlignS3.SetToolTip(wx.ToolTip("Stator S3 commutation offset"))
        self.textAlignS3.SetFont(smallFont)
        self.textAlignS3.Hide()
        #
        self.alignS1Entry = wx.TextCtrl(panel, pos=(77, 133), size=(70, 25))
        self.alignS1Entry.Hide()
        self.alignS2Entry = wx.TextCtrl(panel, pos=(192, 133), size=(70, 25))
        self.alignS2Entry.Hide()
        self.alignS3Entry = wx.TextCtrl(panel, pos=(307, 133), size=(70, 25))
        self.alignS3Entry.Hide()
        self.buttonAlignSend = wx.Button(panel, label="SET", pos=(425, 133), size=(75, 25))
        self.buttonAlignSend.SetToolTip(wx.ToolTip("set commutation offsets"))
        self.buttonAlignSend.SetBackgroundColour('#80e0c0')
        self.buttonAlignSend.SetForegroundColour('#000000')
        self.buttonAlignSend.Bind(wx.EVT_BUTTON, self.alignSend)
        self.buttonAlignSend.Hide()
        #
        self.buttonAlignDefault = wx.Button(panel, label="DEFAULT", pos=(425, 108), size=(75, 25))
        self.buttonAlignDefault.SetToolTip(wx.ToolTip("restore default commutation offsets"))
        self.buttonAlignDefault.SetBackgroundColour('#ffff00')
        self.buttonAlignDefault.SetForegroundColour('#000000')
        self.buttonAlignDefault.Bind(wx.EVT_BUTTON, self.alignDefault)
        self.buttonAlignDefault.Hide()

        # cycle entry fields
        self.textCycleStart = wx.StaticText(self, label='start altitude', pos=(83, 113))
        self.textCycleStart.SetToolTip(wx.ToolTip("starting altitude"))
        self.textCycleStart.SetFont(smallFont)
        self.textCycleStart.Hide()
        #
        self.textCycleSpeed = wx.StaticText(self, label='step size', pos=(205, 113))
        self.textCycleSpeed.SetToolTip(wx.ToolTip("update step size"))
        self.textCycleSpeed.SetFont(smallFont)
        self.textCycleSpeed.Hide()
        #
        self.textCycleDirection = wx.StaticText(self, label='step direction', pos=(285, 113))
        self.textCycleDirection.SetFont(smallFont)
        self.textCycleDirection.Hide()
        #
        self.cycleStartEntry = wx.TextCtrl(panel, pos=(77, 133), size=(70, 25))
        self.cycleStartEntry.Value = "0"
        self.cycleStartEntry.Hide()
        #
        self.cycleSpeedEntry = wx.TextCtrl(panel, pos=(192, 133), size=(70, 25))
        self.cycleSpeedEntry.Value = "50"
        self.cycleSpeedEntry.Hide()
        #
        self.cycleSpeedStartStop = wx.Button(panel, label="START", pos=(425, 133), size=(75, 25))
        self.cycleSpeedStartStop.SetToolTip(wx.ToolTip("start cycle mode"))
        self.cycleSpeedStartStop.SetBackgroundColour('#80e0c0')
        self.cycleSpeedStartStop.SetForegroundColour('#000000')
        self.cycleSpeedStartStop.Bind(wx.EVT_BUTTON, self.cycleStartStop)
        self.cycleSpeedStartStop.Hide()
        #
        self.cycleUpDown = wx.Button(panel, label=" UP ", pos=(280, 133), size=(75, 25))
        self.cycleUpDown.SetToolTip(wx.ToolTip("altitude change direction"))
        self.cycleUpDown.SetBackgroundColour('#80e0c0')
        self.cycleUpDown.SetForegroundColour('#000000')
        self.cycleUpDown.Bind(wx.EVT_BUTTON, self.cycleUpDownButton)
        self.cycleUpDown.Hide()

        # Exit button
        self.buttonExit = wx.Button(panel, label="Exit", pos=(400, 190), size=(100, 25))
        self.buttonExit.SetForegroundColour('#ff0000')
        self.buttonExit.Bind(wx.EVT_BUTTON, self.ExitClick)
        
        # promote myself :-)
        henkFont = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.henkie = wx.StaticText(self, label="Altimeter Demonstrator by 'henkie', 09-2017", pos=(35, 230))
        self.henkie.SetFont(henkFont)
        self.henkie.SetForegroundColour("#0000ff")

        self.errorDeviceAddress = wx.StaticBitmap(self, -1, errorImage)
        self.errorDeviceSubAddress = wx.StaticBitmap(self, -1, errorImage)
        self.errorDeviceData = wx.StaticBitmap(self, -1, errorImage)
        self.errorDeviceAddress.SetPosition((149, 133))
        self.errorDeviceSubAddress.SetPosition((264, 133))
        self.errorDeviceData.SetPosition((379, 133))
        self.errorDeviceAddress.Hide()
        self.errorDeviceSubAddress.Hide()
        self.errorDeviceData.Hide()

        self.errorAlignS1 = wx.StaticBitmap(self, -1, errorImage)
        self.errorAlignS2 = wx.StaticBitmap(self, -1, errorImage)
        self.errorAlignS3 = wx.StaticBitmap(self, -1, errorImage)
        self.errorAlignS1.SetPosition((149, 133))
        self.errorAlignS2.SetPosition((264, 133))
        self.errorAlignS3.SetPosition((379, 133))
        self.errorAlignS1.Hide()
        self.errorAlignS2.Hide()
        self.errorAlignS3.Hide()

        self.errorCycleSpeedEntry = wx.StaticBitmap(self, -1, errorImage)
        self.errorCycleSpeedEntry.SetPosition((149, 133))
        self.errorCycleSpeedEntry.Hide()

        # define timer
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timerIsRunning = False
        self.startTimer(500)                   # initially COM port not assigned


# ==============================================================================
#  ACTION  routines
# ==============================================================================

    def onRadioBox(self,e): 
        if self.rbox.GetStringSelection() == "PHCC":
            self.channelSelection = "PHCC"
        else:
            self.channelSelection = "USB"


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

    def altitudeCorrection(self, altitudeSetpoint):
        #
        # The altimeter shows a different value than the requested setpoint.
        # Measurements show that it seems there is a small sine superimposed on the actual shown altitude and the setpoint.
        # Over one electrical period of the altimeter (0 .. 10000 feet) there are six full sine periods. Initially the
        # indicated altitude is too low, then there is a half period where the indication is too high. This repeats 6
        # times over the electrical period. By *modifying* the requested setpoint with a "superimposed" sine it is attempted
        # to linearize the resulting plot in such a way that the requested setpoint results in the correct indicated altitude.
        #
        if self.useCorrection == True :
            # ==== using sine correction =====================================================================================
            # determine correction sine value
            #sinePeriod = value % (10000.0 / 6.0)
            #periodAngle = 2.0 * math.pi * sinePeriod / (10000.0 / 6.0)
            #sineValue = math.sin(periodAngle)
            #
            # The measurements also show that the superimposed sine is not
            # symmetrical. That is, the "too low" altitude indications are more
            # "too low" than the "too high" indications. This asymmetry is
            # compensated by shifting the sine zero value to match the theoretical
            # graph of the setpoint / altimeter indication line.
            #
            #measuredPositiveDelta = 105
            #measuredNegativeDelta = 135
            #averagedDeviation     = (measuredNegativeDelta - measuredPositiveDelta) / 2
            #sineScalingFactor     = measuredNegativeDelta - averagedDeviation
            #sineAmplitude         = sineValue * sineScalingFactor
            # The "if" for positive/negative sineValue enables to apply a different sine scaling factor
            #if sineValue <= 0.0 :
            #    correctedSetpoint = value + int(sineAmplitude)
            #else:
            #    correctedSetpoint = value + int(sineAmplitude)
            #print "... sine value =", sineValue, "   sine amplitude =", sineAmplitude, "factor =", sineScalingFactor
            #print "... integer sine amplitude =", int(sineAmplitude)
            #print "... entered altitude setpoint =", value, "   corrected setpoint =", correctedSetpoint
            #
            #
            # ==== using lookup with linar interpolation correction ==========================================================
            entry = int(altitudeSetpoint / 50)
            span = self.lookup[entry+1] - self.lookup[entry]
            increment = span / 50.0
            interpolation = int((altitudeSetpoint - (entry * 50.0)) * increment)
            correctedSetpoint = self.lookup[entry] + interpolation
            return correctedSetpoint
        else:
            return altitudeSetpoint

    def altiEntrySet(self, event):
        altitude = self.altiEntry.GetValue()
        value = self.str2int(altitude)
        if value > 99999:
            self.errorAltiEntry.Show()
        else:
            self.altitudeSetting = value
            self.errorAltiEntry.Hide()
            value = value % 10000
            correctedSetpoint = self.altitudeCorrection(value)
            # create correct command subaddress and data
            position = (correctedSetpoint * 4096) / 10000
            address = int(position / 256)
            value = int(position - (address * 256))
            self.sendData(address, value)

    def altiIncrement(self, e):
        if self.altitudeSetting < 99980:
            self.altitudeSetting = self.altitudeSetting + 20
        else:
            remainder = 100000 - self.altitudeSetting
            self.altitudeSetting = 20 - remainder
        self.errorAltiEntry.Hide()
        self.altiEntry.SetValue(str(self.altitudeSetting))
        # send to altimeter
        value = self.altitudeSetting
        value = value % 10000
        correctedSetpoint = self.altitudeCorrection(value)
        position = (correctedSetpoint * 4096) / 10000
        address = int(position / 256)
        value = int(position - (address * 256))
        self.sendData(address, value)

    def altiDecrement(self, e):
        if self.altitudeSetting >= 20:
            self.altitudeSetting = self.altitudeSetting - 20
        else:
            remainder = 20 - self.altitudeSetting
            self.altitudeSetting = 100000 - remainder
        self.errorAltiEntry.Hide()
        self.altiEntry.SetValue(str(self.altitudeSetting))
        # send to altimeter
        value = self.altitudeSetting
        value = value % 10000
        correctedSetpoint = self.altitudeCorrection(value)
        position = (correctedSetpoint * 4096) / 10000
        address = int(position / 256)
        value = int(position - (address * 256))
        self.sendData(address, value)



    def advancedOption(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.textAltiEntry.Hide()
            self.altiEntry.Hide()
            self.buttonAltiEntrySet.Hide()
            self.errorAltiEntry.Hide()
            self.buttonAltiInc.Hide()
            self.buttonAltiDec.Hide()
            self.textAlignS1.Hide()
            self.textAlignS2.Hide()
            self.textAlignS3.Hide()
            self.alignS1Entry.Hide()
            self.alignS2Entry.Hide()
            self.alignS3Entry.Hide()
            self.buttonAlignSend.Hide()
            self.buttonAlignDefault.Hide()
            self.errorAlignS1.Hide()
            self.errorAlignS2.Hide()
            self.errorAlignS3.Hide()
            self.alignMode.SetValue(False)
            self.textCycleStart.Hide()
            self.cycleStartEntry.Hide()
            self.textCycleSpeed.Hide()
            self.cycleSpeedEntry.Hide()
            self.cycleSpeedStartStop.Hide()
            self.textCycleDirection.Hide()
            self.cycleUpDown.Hide()
            self.errorCycleSpeedEntry.Hide()
            self.cycleMode.SetValue(False)
            # start advanced mode
            self.textDeviceAddress.Show()
            self.textDeviceSubAddress.Show()
            self.textDeviceData.Show()
            self.deviceAddressEntry.Show()
            self.deviceSubAddressEntry.Show()
            self.deviceDataEntry.Show()
            self.buttonAdvancedSend.Show()
            self.errorDeviceAddress.Hide()
            self.errorDeviceSubAddress.Hide()
            self.errorDeviceData.Hide()
        else:
            self.textAltiEntry.Show()
            self.altiEntry.Show()
            self.buttonAltiEntrySet.Show()
            self.buttonAltiInc.Show()
            self.buttonAltiDec.Show()
            # stop advanced mode
            self.textDeviceAddress.Hide()
            self.textDeviceSubAddress.Hide()
            self.textDeviceData.Hide()
            self.deviceAddressEntry.Hide()
            self.deviceSubAddressEntry.Hide()
            self.deviceDataEntry.Hide()
            self.buttonAdvancedSend.Hide()
            self.errorDeviceAddress.Hide()
            self.errorDeviceSubAddress.Hide()
            self.errorDeviceData.Hide()

    def alignOption(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.textAltiEntry.Hide()
            self.altiEntry.Hide()
            self.buttonAltiEntrySet.Hide()
            self.errorAltiEntry.Hide()
            self.buttonAltiInc.Hide()
            self.buttonAltiDec.Hide()
            self.textDeviceAddress.Hide()
            self.textDeviceSubAddress.Hide()
            self.textDeviceData.Hide()
            self.deviceAddressEntry.Hide()
            self.deviceSubAddressEntry.Hide()
            self.deviceDataEntry.Hide()
            self.buttonAdvancedSend.Hide()
            self.errorDeviceAddress.Hide()
            self.errorDeviceSubAddress.Hide()
            self.errorDeviceData.Hide()
            self.advancedMode.SetValue(False)
            self.cycleSpeedStartStop.Hide()
            self.textCycleDirection.Hide()
            self.cycleUpDown.Hide()
            self.textCycleStart.Hide()
            self.cycleStartEntry.Hide()
            self.textCycleSpeed.Hide()
            self.cycleSpeedEntry.Hide()
            self.errorCycleSpeedEntry.Hide()
            self.cycleMode.SetValue(False)
            # start alignment mode
            self.textAlignS1.Show()
            self.textAlignS2.Show()
            self.textAlignS3.Show()
            self.alignS1Entry.Show()
            self.alignS2Entry.Show()
            self.alignS3Entry.Show()
            self.buttonAlignSend.Show()
            self.buttonAlignDefault.Show()
            self.errorAlignS1.Hide()
            self.errorAlignS2.Hide()
            self.errorAlignS3.Hide()
        else:
            self.textAltiEntry.Show()
            self.altiEntry.Show()
            self.buttonAltiEntrySet.Show()
            self.buttonAltiInc.Show()
            self.buttonAltiDec.Show()
            # stop alignment mode
            self.textAlignS1.Hide()
            self.textAlignS2.Hide()
            self.textAlignS3.Hide()
            self.alignS1Entry.Hide()
            self.alignS2Entry.Hide()
            self.alignS3Entry.Hide()
            self.buttonAlignSend.Hide()
            self.buttonAlignDefault.Hide()
            self.errorAlignS1.Hide()
            self.errorAlignS2.Hide()
            self.errorAlignS3.Hide()


    def cycleOption(self, event):
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        if isChecked:
            self.textAltiEntry.Hide()
            self.altiEntry.Hide()
            self.buttonAltiEntrySet.Hide()
            self.errorAltiEntry.Hide()
            self.buttonAltiInc.Hide()
            self.buttonAltiDec.Hide()
            self.textDeviceAddress.Hide()
            self.textDeviceSubAddress.Hide()
            self.textDeviceData.Hide()
            self.deviceAddressEntry.Hide()
            self.deviceSubAddressEntry.Hide()
            self.deviceDataEntry.Hide()
            self.buttonAdvancedSend.Hide()
            self.errorDeviceAddress.Hide()
            self.errorDeviceSubAddress.Hide()
            self.errorDeviceData.Hide()
            self.textAlignS1.Hide()
            self.textAlignS2.Hide()
            self.textAlignS3.Hide()
            self.alignS1Entry.Hide()
            self.alignS2Entry.Hide()
            self.alignS3Entry.Hide()
            self.buttonAlignSend.Hide()
            self.buttonAlignDefault.Hide()
            self.errorAlignS1.Hide()
            self.errorAlignS2.Hide()
            self.errorAlignS3.Hide()
            self.advancedMode.SetValue(False)
            self.alignMode.SetValue(False)
            # start cycle mode
            self.textCycleStart.Show()
            self.cycleStartEntry.Value = self.altiEntry.GetValue()
            self.cycleStartEntry.Show()
            self.textCycleSpeed.Show()
            self.cycleSpeedEntry.Show()
            self.cycleSpeedStartStop.Show()
            self.textCycleDirection.Show()
            self.cycleUpDown.Show()
        else:
            self.textAltiEntry.Show()
            self.altiEntry.Show()
            self.buttonAltiEntrySet.Show()
            self.buttonAltiInc.Show()
            self.buttonAltiDec.Show()
            # stop cycle mode
            self.textCycleStart.Hide()
            self.cycleStartEntry.Hide()
            self.textCycleSpeed.Hide()
            self.cycleSpeedEntry.Hide()
            self.cycleSpeedStartStop.Hide()
            self.textCycleDirection.Hide()
            self.cycleUpDown.Hide()
            self.errorCycleSpeedEntry.Hide()



    def advancedSend(self, event):
        advDeviceAddress = self.deviceAddressEntry.GetValue()
        advDeviceSubAddress = self.deviceSubAddressEntry.GetValue()
        advData = self.deviceDataEntry.GetValue()
        print ("advanced data =", advDeviceAddress, advDeviceSubAddress, advData)
        # process entry fields
        allDataValid = True
        portID = ""
        if advDeviceAddress == "0x41" or advDeviceAddress == "0X41" or advDeviceAddress == "65" :
            portID = "ALTI"
        if portID == "":
            self.errorDeviceAddress.Show()
            allDataValid = False
        else:
            self.errorDeviceAddress.Hide()
        #
        subValue = self.str2int(advDeviceSubAddress)
        if (subValue > 45) or (advDeviceSubAddress == "") :
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
            self.buttonAdvancedSend.SetBackgroundColour('#80e0c0')
            self.sendData(subValue, dataValue)
        else:
            self.buttonAdvancedSend.SetBackgroundColour('#e05040')


    def alignSend(self, event):
        alignS1offset = self.alignS1Entry.GetValue()
        alignS2offset = self.alignS2Entry.GetValue()
        alignS3offset = self.alignS3Entry.GetValue()
        print ("alignment data =", alignS1offset, alignS2offset, alignS3offset)
        # process entry fields
        allDataValid = True
        #
        s1Offset = self.str2int(alignS1offset)
        s2Offset = self.str2int(alignS2offset)
        s3Offset = self.str2int(alignS3offset)
        if (s1Offset > 4095) or (alignS1offset == "") :
            self.errorAlignS1.Show()
            allDataValid = False
        else:
            self.errorAlignS1.Hide()
        if (s2Offset > 4095) or (alignS2offset == "") :
            self.errorAlignS2.Show()
            allDataValid = False
        else:
            self.errorAlignS2.Hide()
        if (s3Offset > 4095) or (alignS3offset == "") :
            self.errorAlignS3.Show()
            allDataValid = False
        else:
            self.errorAlignS3.Hide()
        if allDataValid == True:
            self.buttonAlignSend.SetBackgroundColour('#80e0c0')
            # first LSB then MSB offset
            s1Msb = int(s1Offset / 256)
            s1Lsb = s1Offset - (s1Msb * 256)
            self.sendData(26, s1Lsb)
            self.sendData(27, s1Msb)
            #
            s2Msb = int(s2Offset / 256)
            s2Lsb = s2Offset - (s2Msb * 256)
            self.sendData(28, s2Lsb)
            self.sendData(29, s2Msb)
            #
            s3Msb = int(s3Offset / 256)
            s3Lsb = s3Offset - (s3Msb * 256)
            self.sendData(30, s3Lsb)
            self.sendData(31, s3Msb)
        else:
            self.buttonAlignSend.SetBackgroundColour('#e05040')


    def alignDefault(self, event):
        #   S1DEFAULTANGLE = 2365
        #   S2DEFAULTANGLE = 3730
        #   S3DEFAULTANGLE = 999
        self.alignS1Entry.Value = "2365"
        self.alignS2Entry.Value = "3730"
        self.alignS3Entry.Value = "999"


    def cycleStartStop(self, event):
        if self.commPortID != "":
            # start only allowed if a COM port has been selected
            button = event.GetEventObject()
            buttonName = button.GetLabel()
            if buttonName == "START":
                stepDelay = self.cycleSpeedEntry.GetValue()
                value = self.str2int(stepDelay)
                if value > 500:
                    print ("step delay too large")
                    self.errorCycleSpeedEntry.Show()
                    self.cycleSpeedStartStop.SetLabel("START")
                    self.cycleSpeedStartStop.SetToolTip(wx.ToolTip("start altitude update mode"))
                    self.cycleSpeedStartStop.SetBackgroundColour('#80e0c0')
                else:
                    self.errorCycleSpeedEntry.Hide()
                    self.cycleSpeedStartStop.SetLabel("STOP")
                    self.cycleSpeedStartStop.SetToolTip(wx.ToolTip("stop altitude update mode"))
                    self.cycleSpeedStartStop.SetBackgroundColour('#ffcc00')
                    self.timerUsage = 1
                    self.startTimer(500)
                    print ("ALTITUDE UPDATE MODE STARTED")
            else:
                self.cycleSpeedStartStop.SetLabel("START")
                self.cycleSpeedStartStop.SetToolTip(wx.ToolTip("start altitude update mode"))
                self.cycleSpeedStartStop.SetBackgroundColour('#80e0c0')
                self.timerUsage = 0
                self.stopTimer()
                print ("ALTITUDE UPDATE MODE STOPPED")

    def cycleUpDownButton(self, event):
        button = event.GetEventObject()
        buttonName = button.GetLabel()
        if buttonName == " UP ":
            button.SetLabel("DOWN")
        else:
            button.SetLabel(" UP ")




    def ExitClick(self, event):
        if self.commPortID != "":
            self.closeComPort(self.commPortID)
        self.Close()


# timer handling

    def stopTimer(self):
        if self.timerIsRunning == True:
            self.timer.Stop()
            self.timerIsRunning = False

    def startTimer(self, rate):
        if self.timerIsRunning == False:
            self.timerIsRunning = True
            self.timer.Start(rate)

    def OnTimer(self, event):
        if self.timerUsage == 0:
            self.stopTimer()
            # ---- handle no COM port defined flashing ERROR sign
            if self.commPortID == "":
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
                self.errorCommPortShown = False
                self.errorCommPort.Hide()
            # ----
        elif self.timerUsage == 1:
            # altitude update mode active
            setpoint  = self.cycleStartEntry.GetValue()
            stepSize  = self.cycleSpeedEntry.GetValue()
            direction = self.cycleUpDown.GetLabel()
            numSetpoint = self.str2int(setpoint)
            numStepSize = self.str2int(stepSize)
            # send setpoint to altimeter
            value = numSetpoint
            value = value % 10000
            correctedSetpoint = self.altitudeCorrection(value)
            position = (correctedSetpoint * 4096) / 10000
            address = int(position / 256)
            value = int(position - (address * 256))
            self.sendData(address, value)
            print ("...", numSetpoint, numStepSize, direction)
            # generate next setpoint
            if direction == " UP ":
                if numSetpoint < (100000 - numStepSize):
                    numSetpoint = numSetpoint + numStepSize
                else:
                    remainder = 100000 - numSetpoint
                    numSetpoint = numStepSize - remainder
            else:
                if numSetpoint >= numStepSize:
                    numSetpoint = numSetpoint - numStepSize
                else:
                    remainder = numStepSize - numSetpoint
                    numSetpoint = 100000 - remainder
            self.cycleStartEntry.SetValue(str(numSetpoint))
        else:
            print ("? unknown timer usage timer pulse")


# =================================================================================================
#  COM port assignments
# =================================================================================================

    def OnSelectCommPort(self, entry):
        previousCommPort = self.commPortID
        self.commPortID  = entry.GetString()
        if previousCommPort != "":
            # a COM port is already in use: close if not identical to new COM port
            if previousCommPort != self.commPortID:
                self.closeComPort(previousCommPort)
                self.openComPort(self.commPortID)
        else:
            # initial state: no COM port opened
            self.errorCommPort.Hide()
            self.openComPort(self.commPortID)
        

    def openComPort(self, portID):
        print (">   opening COM port", portID)
        self.ComPort = serial.Serial(portID, baudrate=115200, parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)


    def closeComPort(self, portID):
        print (">   closing COM port", portID)
        if self.ComPort.isOpen():
            self.ComPort.close()
        else:
            print ("!!! COM port", portID, "is not open!")


# =================================================================================================
#  COMMUNICATION  routine: send data
# =================================================================================================

    def sendData(self, subAddress, data):
        if self.commPortID != "":
            print ("... sendData to", self.commPortID, "subAddress", subAddress, "data", data)
            if self.channelSelection == "PHCC":
                # using PHCC Motherboard
                if self.ComPort.isOpen():
                    phccId = 0x07
                    address = 0x41
                    self.ComPort.write(phccId.to_bytes(1, byteorder='big', signed=False))
                    self.ComPort.write(address.to_bytes(1, byteorder='big', signed=False))
                    self.ComPort.write(subAddress.to_bytes(1, byteorder='big', signed=False))
                    self.ComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                else:
                    print ("!!! COM port is not open!")
            elif self.channelSelection == "USB":
                if self.ComPort.isOpen():
                    self.ComPort.write(subAddress.to_bytes(1, byteorder='big', signed=False))
                    self.ComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                else:
                    print ("!!! COM port is not open!")
            else:
                print ("!!! no communication channel selected (software bug)")




if __name__ == '__main__':
    app = wx.App()
    window = ALTI(None)
    app.MainLoop()
