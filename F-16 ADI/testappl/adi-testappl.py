import wx
import serial
# from thread import *
# from threading import *
import time


class ADI(wx.Frame):

    def __init__(self, parent):
        super(ADI, self).__init__(parent, size=(640, 470), pos=(20,20))

        panel = wx.Panel(self)
        self.SetTitle('ADI Demonstrator')
        self.SetBackgroundColour('#eeeeee')
        self.Show()

        self.pitchPort = ""
        self.rollPort  = ""
        self.firstPHCCcommand = True
        self.pitchPortOpened = ""
        self.rollPortOpened  = ""
        self.phccPort = ""
        self.defaultPhccCOMport = "COM1"                      # default real serial port
        self.awaitPitchIDresponse = False
        self.awaitRollIDresponse  = False
        self.setupGUI(panel)


    def setupGUI(self, panel):
        wx.StaticLine(panel, -1, (25, 45), (570, 3))
        menuFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        DOAheaderFont = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        rangeFont = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)

        # GS - LOC - AUX flags
        self.textGSflagonoff = wx.StaticText(self, label='GS flag', pos=(70, 70))
        self.textGSflagonoff.SetFont(menuFont)
        self.buttonGSonoff = wx.Button(panel, label="visible", pos=(160, 65), size=(60, 25))
        self.buttonGSonoff.SetToolTip(wx.ToolTip("hide GS flag"))
        self.buttonGSonoff.SetBackgroundColour('#ffcc00')
        self.buttonGSonoff.Bind(wx.EVT_BUTTON, self.GSonoffClick)
        #
        self.textLOCflagonoff = wx.StaticText(self, label='LOC flag', pos=(70, 100))
        self.textLOCflagonoff.SetFont(menuFont)
        self.buttonLOConoff = wx.Button(panel, label="visible", pos=(160, 95), size=(60, 25))
        self.buttonLOConoff.SetToolTip(wx.ToolTip("hide LOC flag"))
        self.buttonLOConoff.SetBackgroundColour('#ffcc00')
        self.buttonLOConoff.Bind(wx.EVT_BUTTON, self.LOConoffClick)
        #
        self.textAUXflagonoff = wx.StaticText(self, label='AUX flag', pos=(70, 130))
        self.textAUXflagonoff.SetFont(menuFont)
        self.buttonAUXonoff = wx.Button(panel, label="visible", pos=(160, 125), size=(60, 25))
        self.buttonAUXonoff.SetToolTip(wx.ToolTip("hide AUX flag"))
        self.buttonAUXonoff.SetBackgroundColour('#ffcc00')
        self.buttonAUXonoff.Bind(wx.EVT_BUTTON, self.AUXonoffClick)

        # flags/RoT - GlideSlope - Sphere ENABLE
        self.textFlagsEnable = wx.StaticText(self, label='ENABLE flags and RoT', pos=(320, 70))
        self.textFlagsEnable.SetFont(menuFont)
        self.buttonFlagsEnable = wx.Button(panel, label="disabled", pos=(490, 65), size=(60, 25))
        self.buttonFlagsEnable.SetToolTip(wx.ToolTip("enable flags and RoT"))
        self.buttonFlagsEnable.SetBackgroundColour('#ff0000')
        self.buttonFlagsEnable.SetForegroundColour('#ffffff')
        self.buttonFlagsEnable.Bind(wx.EVT_BUTTON, self.FlagsEnableClick)
        #
        self.textGlideSlopeEnable = wx.StaticText(self, label='ENABLE glide slope', pos=(320, 100))
        self.textGlideSlopeEnable.SetFont(menuFont)
        self.buttonGlideSlopeEnable = wx.Button(panel, label="disabled", pos=(490, 95), size=(60, 25))
        self.buttonGlideSlopeEnable.SetToolTip(wx.ToolTip("enable glide slope"))
        self.buttonGlideSlopeEnable.SetBackgroundColour('#ff0000')
        self.buttonGlideSlopeEnable.SetForegroundColour('#ffffff')
        self.buttonGlideSlopeEnable.Bind(wx.EVT_BUTTON, self.GlideSlopeEnableClick)
        #
        self.textSphereEnable = wx.StaticText(self, label='ENABLE Roll and Pitch', pos=(320, 130))
        self.textSphereEnable.SetFont(menuFont)
        self.buttonSphereEnable = wx.Button(panel, label="disabled", pos=(490, 125), size=(60, 25))
        self.buttonSphereEnable.SetToolTip(wx.ToolTip("enable Roll & Pitch"))
        self.buttonSphereEnable.SetBackgroundColour('#ff0000')
        self.buttonSphereEnable.SetForegroundColour('#ffffff')
        self.buttonSphereEnable.Bind(wx.EVT_BUTTON, self.SphereEnableClick)
        #
        wx.StaticLine(panel, -1, (25, 170), (570, 3))

        # Glide Slope horizontal / vertical and Rate of Turn setpoint entry
        self.textGShorEntry = wx.StaticText(self, label='glide slope indicator horizontal', pos=(70, 192))
        self.textGShorEntry.SetFont(menuFont)
        self.GShorEntry = wx.TextCtrl(panel, pos=(300, 190), size=(70, 25))
        self.buttonGShorEntrySet = wx.Button(panel, label="SET", pos=(400, 189), size=(60, 25))
        self.buttonGShorEntrySet.SetToolTip(wx.ToolTip("set GS horizontal position"))
        self.buttonGShorEntrySet.SetBackgroundColour('#60a0b0')
        self.buttonGShorEntrySet.SetForegroundColour('#000000')
        self.buttonGShorEntrySet.Bind(wx.EVT_BUTTON, self.GShorEntrySet)
        self.textGShorRange = wx.StaticText(self, label='[0 .. 255]', pos=(490, 194))
        self.textGShorRange.SetFont(rangeFont)
        self.textGShorRange.SetForegroundColour("#0000ff")
        #
        self.textGSvertEntry = wx.StaticText(self, label='glide slope indicator vertical', pos=(70, 222))
        self.textGSvertEntry.SetFont(menuFont)
        self.GSvertEntry = wx.TextCtrl(panel, pos=(300, 220), size=(70, 25))
        self.buttonGSvertEntrySet = wx.Button(panel, label="SET", pos=(400, 219), size=(60, 25))
        self.buttonGSvertEntrySet.SetToolTip(wx.ToolTip("set GS vertical position"))
        self.buttonGSvertEntrySet.SetBackgroundColour('#60a0b0')
        self.buttonGSvertEntrySet.SetForegroundColour('#000000')
        self.buttonGSvertEntrySet.Bind(wx.EVT_BUTTON, self.GSvertEntrySet)
        self.textGSvertRange = wx.StaticText(self, label='[0 .. 255]', pos=(490, 224))
        self.textGSvertRange.SetFont(rangeFont)
        self.textGSvertRange.SetForegroundColour("#0000ff")
        #
        self.textRoTEntry = wx.StaticText(self, label='Rate of Turn indicator', pos=(70, 252))
        self.textRoTEntry.SetFont(menuFont)
        self.RoTEntry = wx.TextCtrl(panel, pos=(300, 250), size=(70, 25))
        self.buttonRoTEntrySet = wx.Button(panel, label="SET", pos=(400, 249), size=(60, 25))
        self.buttonRoTEntrySet.SetToolTip(wx.ToolTip("set Rate of Turn indication"))
        self.buttonRoTEntrySet.SetBackgroundColour('#60a0b0')
        self.buttonRoTEntrySet.SetForegroundColour('#000000')
        self.buttonRoTEntrySet.Bind(wx.EVT_BUTTON, self.RoTEntrySet)
        self.textGSrotRange = wx.StaticText(self, label='[0 .. 255]', pos=(490, 254))
        self.textGSrotRange.SetFont(rangeFont)
        self.textGSrotRange.SetForegroundColour("#0000ff")
        #
        wx.StaticLine(panel, -1, (25, 290), (570, 3))

        # Pitch / Roll position setpoint entry
        self.textPitchEntry = wx.StaticText(self, label='sphere PITCH indication', pos=(70, 312))
        self.textPitchEntry.SetFont(menuFont)
        self.PitchEntry = wx.TextCtrl(panel, pos=(300, 310), size=(70, 25))
        self.buttonPitchEntrySet = wx.Button(panel, label="SET", pos=(400, 309), size=(60, 25))
        self.buttonPitchEntrySet.SetToolTip(wx.ToolTip("set sphere PITCH position"))
        self.buttonPitchEntrySet.SetBackgroundColour('#60a0b0')
        self.buttonPitchEntrySet.SetForegroundColour('#000000')
        self.buttonPitchEntrySet.Bind(wx.EVT_BUTTON, self.PitchEntrySet)
        self.textGSpitchRange = wx.StaticText(self, label='[140 .. 700]', pos=(490, 314))
        self.textGSpitchRange.SetFont(rangeFont)
        self.textGSpitchRange.SetForegroundColour("#0000ff")
        #
        self.textRollEntry = wx.StaticText(self, label='sphere ROLL indication', pos=(70, 342))
        self.textRollEntry.SetFont(menuFont)
        self.RollEntry = wx.TextCtrl(panel, pos=(300, 340), size=(70, 25))
        self.buttonRollEntrySet = wx.Button(panel, label="SET", pos=(400, 339), size=(60, 25))
        self.buttonRollEntrySet.SetToolTip(wx.ToolTip("set sphere ROLL position"))
        self.buttonRollEntrySet.SetBackgroundColour('#60a0b0')
        self.buttonRollEntrySet.SetForegroundColour('#000000')
        self.buttonRollEntrySet.Bind(wx.EVT_BUTTON, self.RollEntrySet)
        self.textGSrollRange = wx.StaticText(self, label='[0 .. 1023]', pos=(490, 344))
        self.textGSrollRange.SetFont(rangeFont)
        self.textGSrollRange.SetForegroundColour("#0000ff")
        #
        wx.StaticLine(panel, -1, (25, 380), (570, 3))

        # advanced checkbox
        self.advancedMode = wx.CheckBox(panel, label='Advanced', pos=(310, 400), size=(100, 25))
        self.advancedMode.SetValue(False)
        self.Centre()
        self.advancedMode.SetToolTip(wx.ToolTip("send raw data"))
        self.Show(True)
        self.advancedMode.Bind(wx.EVT_CHECKBOX, self.advancedOption)
        #
        # advanced entry fields
        self.textDeviceAddress = wx.StaticText(self, label='DEVICE ADDRESS', pos=(70, 312))
        self.textDeviceAddress.SetToolTip(wx.ToolTip("8-bit DOA DEVICE address"))
        self.textDeviceAddress.SetFont(DOAheaderFont)
        self.textDeviceAddress.Hide()
        self.textDeviceSubAddress = wx.StaticText(self, label='SUB-ADDRESS', pos=(190, 312))
        self.textDeviceSubAddress.SetToolTip(wx.ToolTip("8-bit DOA sub-address"))
        self.textDeviceSubAddress.SetFont(DOAheaderFont)
        self.textDeviceSubAddress.Hide()
        self.textDeviceData = wx.StaticText(self, label='DATA BYTE', pos=(314, 312))
        self.textDeviceData.SetToolTip(wx.ToolTip("8-bit DOA data"))
        self.textDeviceData.SetFont(DOAheaderFont)
        self.textDeviceData.Hide()
        self.textAdvAddr = wx.StaticText(self, label='48:pitch  50:roll', pos=(76, 358))
        self.textAdvAddr.SetFont(rangeFont)
        self.textAdvAddr.SetForegroundColour("#0000ff")
        self.textAdvAddr.Hide()
        #
        self.deviceAddressEntry = wx.TextCtrl(panel, pos=(77, 330), size=(70, 25))
        self.deviceAddressEntry.Hide()
        self.deviceSubAddressEntry = wx.TextCtrl(panel, pos=(192, 330), size=(70, 25))
        self.deviceSubAddressEntry.Hide()
        self.deviceDataEntry = wx.TextCtrl(panel, pos=(307, 330), size=(70, 25))
        self.deviceDataEntry.Hide()
        self.buttonAdvancedSend = wx.Button(panel, label="SEND", pos=(440, 329), size=(60, 25))
        self.buttonAdvancedSend.SetToolTip(wx.ToolTip("send DOA device / sub-address / data"))
        self.buttonAdvancedSend.SetBackgroundColour('#80e0c0')
        self.buttonAdvancedSend.SetForegroundColour('#000000')
        self.buttonAdvancedSend.Bind(wx.EVT_BUTTON, self.advancedSend)
        self.buttonAdvancedSend.Hide()

        # Exit button
        self.buttonExit    = wx.Button(panel, label="Exit", pos=(500, 400), size=(80, 25))
        self.buttonExit.SetForegroundColour('#ff0000')
        self.buttonExit.Bind(wx.EVT_BUTTON, self.ExitClick)
        
        # promote myself :-)
        henkFont = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.henkie = wx.StaticText(self, label="ADI Demonstrator, version 2 for Python 3.6", pos=(25, 413))
        self.henkie.SetFont(henkFont)
        self.henkie.SetForegroundColour("#0000ff")

        # "error in entry" indication bitmaps
        errorImage = wx.Bitmap("error.gif")
        self.errorGShorEntry = wx.StaticBitmap(self, -1, errorImage)
        self.errorGSvertEntry = wx.StaticBitmap(self, -1, errorImage)
        self.errorRoTEntry = wx.StaticBitmap(self, -1, errorImage)
        self.errorPitchEntry = wx.StaticBitmap(self, -1, errorImage)
        self.errorRollEntry = wx.StaticBitmap(self, -1, errorImage)
        self.errorPitchPort = wx.StaticBitmap(self, -1, errorImage)
        self.errorRollPort = wx.StaticBitmap(self, -1, errorImage)
        self.errorDeviceAddress = wx.StaticBitmap(self, -1, errorImage)
        self.errorDeviceSubAddress = wx.StaticBitmap(self, -1, errorImage)
        self.errorDeviceData = wx.StaticBitmap(self, -1, errorImage)
        self.errorGShorEntry.SetPosition((373, 189))
        self.errorGSvertEntry.SetPosition((373, 219))
        self.errorRoTEntry.SetPosition((373, 249))
        self.errorPitchEntry.SetPosition((373, 309))
        self.errorRollEntry.SetPosition((373, 339))
        self.errorPitchPort.SetPosition((188, 7))
        self.errorRollPort.SetPosition((435, 7))
        self.errorDeviceAddress.SetPosition((149, 329))
        self.errorDeviceSubAddress.SetPosition((264, 329))
        self.errorDeviceData.SetPosition((379, 329))
        self.errorGShorEntry.Hide()
        self.errorGSvertEntry.Hide()
        self.errorRoTEntry.Hide()
        self.errorPitchEntry.Hide()
        self.errorRollEntry.Hide()
        self.errorPitchPort.Show()
        self.errorRollPort.Show()
        self.errorDeviceAddress.Hide()
        self.errorDeviceSubAddress.Hide()
        self.errorDeviceData.Hide()

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
        print("--- discovered COM ports:", availableCOMports)
        # show combo box with available COM ports
        self.textPITCHport = wx.StaticText(self, label='PITCH  SDI port', pos=(70, 10))
        self.textPITCHport.SetFont(menuFont)
        self.textPITCHport.SetForegroundColour("#ff0000")
        cbPitch = wx.ComboBox(panel, pos=(220, 10), choices=availableCOMports, style=wx.CB_READONLY)
        cbPitch.SetToolTip(wx.ToolTip("set PITCH SDI COM port"))
        cbPitch.Bind(wx.EVT_COMBOBOX, self.OnSelectPitchPort)
        self.textROLLport = wx.StaticText(self, label='ROLL  SDI port', pos=(320, 10))
        self.textROLLport.SetFont(menuFont)
        self.textROLLport.SetForegroundColour("#ff0000")
        cbRoll = wx.ComboBox(panel, pos=(470, 10), choices=availableCOMports, style=wx.CB_READONLY)
        cbRoll.SetToolTip(wx.ToolTip("set ROLL SDI COM port"))
        cbRoll.Bind(wx.EVT_COMBOBOX, self.OnSelectRollPort)

        # define timer
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timerIsRunning = False


# =================================================================================================
#  ACTION  routines
# =================================================================================================

    def GSonoffClick(self, event):
        button = event.GetEventObject()
        buttonName = button.GetLabel()
        if buttonName == "hidden":
            self.buttonGSonoff.SetLabel("visible")
            self.buttonGSonoff.SetToolTip(wx.ToolTip("hide GS flag"))
            self.buttonGSonoff.SetBackgroundColour('#ffcc00')
            self.sendData("ROLL", 15, 0)
        else:
            self.buttonGSonoff.SetLabel("hidden")
            self.buttonGSonoff.SetToolTip(wx.ToolTip("show GS flag"))
            self.buttonGSonoff.SetBackgroundColour('#cccccc')
            self.sendData("ROLL", 15, 1)

    def LOConoffClick(self, event):
        button = event.GetEventObject()
        buttonName = button.GetLabel()
        if buttonName == "hidden":
            self.buttonLOConoff.SetLabel("visible")
            self.buttonLOConoff.SetToolTip(wx.ToolTip("hide LOC flag"))
            self.buttonLOConoff.SetBackgroundColour('#ffcc00')
            self.sendData("ROLL", 17, 0)
        else:
            self.buttonLOConoff.SetLabel("hidden")
            self.buttonLOConoff.SetToolTip(wx.ToolTip("show LOC flag"))
            self.buttonLOConoff.SetBackgroundColour('#cccccc')
            self.sendData("ROLL", 17, 1)

    def AUXonoffClick(self, event):
        button = event.GetEventObject()
        buttonName = button.GetLabel()
        if buttonName == "hidden":
            self.buttonAUXonoff.SetLabel("visible")
            self.buttonAUXonoff.SetToolTip(wx.ToolTip("hide AUX flag"))
            self.buttonAUXonoff.SetBackgroundColour('#ffcc00')
            self.sendData("ROLL", 18, 0)
        else:
            self.buttonAUXonoff.SetLabel("hidden")
            self.buttonAUXonoff.SetToolTip(wx.ToolTip("show AUX flag"))
            self.buttonAUXonoff.SetBackgroundColour('#cccccc')
            self.sendData("ROLL", 18, 1)

    def FlagsEnableClick(self, event):
        button = event.GetEventObject()
        buttonName = button.GetLabel()
        if buttonName == "disabled":
            self.buttonFlagsEnable.SetLabel("enabled")
            self.buttonFlagsEnable.SetToolTip(wx.ToolTip("disable flags and RoT"))
            self.buttonFlagsEnable.SetBackgroundColour('#00ff00')
            self.buttonFlagsEnable.SetForegroundColour('#000000')
            self.sendData("ROLL", 16, 1)
        else:
            self.buttonFlagsEnable.SetLabel("disabled")
            self.buttonFlagsEnable.SetToolTip(wx.ToolTip("enable flags and RoT"))
            self.buttonFlagsEnable.SetBackgroundColour('#ff0000')
            self.buttonFlagsEnable.SetForegroundColour('#ffffff')
            self.sendData("ROLL", 16, 0)

    def GlideSlopeEnableClick(self, event):
        button = event.GetEventObject()
        buttonName = button.GetLabel()
        if buttonName == "disabled":
            self.buttonGlideSlopeEnable.SetLabel("enabled")
            self.buttonGlideSlopeEnable.SetToolTip(wx.ToolTip("disable glide slope"))
            self.buttonGlideSlopeEnable.SetBackgroundColour('#00ff00')
            self.buttonGlideSlopeEnable.SetForegroundColour('#000000')
            self.sendData("PITCH", 16, 1)
        else:
            self.buttonGlideSlopeEnable.SetLabel("disabled")
            self.buttonGlideSlopeEnable.SetToolTip(wx.ToolTip("enable glide slope"))
            self.buttonGlideSlopeEnable.SetBackgroundColour('#ff0000')
            self.buttonGlideSlopeEnable.SetForegroundColour('#ffffff')
            self.sendData("PITCH", 16, 0)

    def SphereEnableClick(self, event):
        button = event.GetEventObject()
        buttonName = button.GetLabel()
        if buttonName == "disabled":
            self.buttonSphereEnable.SetLabel("enabled")
            self.buttonSphereEnable.SetToolTip(wx.ToolTip("disable Roll & Pitch"))
            self.buttonSphereEnable.SetBackgroundColour('#00ff00')
            self.buttonSphereEnable.SetForegroundColour('#000000')
            self.sendData("PITCH", 15, 1)
        else:
            self.buttonSphereEnable.SetLabel("disabled")
            self.buttonSphereEnable.SetToolTip(wx.ToolTip("enable Roll & Pitch"))
            self.buttonSphereEnable.SetBackgroundColour('#ff0000')
            self.buttonSphereEnable.SetForegroundColour('#ffffff')
            self.sendData("PITCH", 15, 0)

    # convert a string to a numeric, if string is not a number return 9999.
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
            return 9999
        else:
            return i

    def GShorEntrySet(self, event):
        GShorValue = self.GShorEntry.GetValue()
        value = self.str2int(GShorValue)
        if value == 9999:
            self.errorGShorEntry.Show()
        elif value < 0 or value > 255:
            self.errorGShorEntry.Show()
        else:
            self.errorGShorEntry.Hide()
            self.sendData("PITCH", 17, value)

    def GSvertEntrySet(self, event):
        GSvertValue = self.GSvertEntry.GetValue()
        value = self.str2int(GSvertValue)
        if value == 9999:
            self.errorGSvertEntry.Show()
        elif value < 0 or value > 255:
            self.errorGSvertEntry.Show()
        else:
            self.errorGSvertEntry.Hide()
            self.sendData("PITCH", 18, value)

    def RoTEntrySet(self, event):
        RoTValue = self.RoTEntry.GetValue()
        value = self.str2int(RoTValue)
        if value == 9999:
            self.errorRoTEntry.Show()
        elif value < 0 or value > 255:
            self.errorRoTEntry.Show()
        else:
            self.errorRoTEntry.Hide()
            self.sendData("ROLL", 22, value)

    def PitchEntrySet(self, event):
        pitchValue = self.PitchEntry.GetValue()
        value = self.str2int(pitchValue)
        if value == 9999:
            self.errorPitchEntry.Show()
        elif value < 140 or value > 700:
            # extra limiting for PITCH
            self.errorPitchEntry.Show()
        else:
            self.errorPitchEntry.Hide()
            if value < 256:
                address = 0
            elif value < 512:
                address = 1
                value = value - 256
            elif value < 768:
                address = 2
                value = value - 512
            else:
                address = 3
                value = value - 768
            self.sendData("PITCH", address, value)

    def RollEntrySet(self, event):
        rollValue = self.RollEntry.GetValue()
        value = self.str2int(rollValue)
        if value == 9999:
            self.errorRollEntry.Show()
        elif value < 0 or value > 1023:
            self.errorRollEntry.Show()
        else:
            self.errorRollEntry.Hide()
            if value < 256:
                address = 0
            elif value < 512:
                address = 1
                value = value - 256
            elif value < 768:
                address = 2
                value = value - 512
            else:
                address = 3
                value = value - 768
            self.sendData("ROLL", address, value)



    def advancedOption(self, event):
        
        sender = event.GetEventObject()
        isChecked = sender.GetValue()
        
        if isChecked:
            self.textPitchEntry.Hide()
            self.PitchEntry.Hide()
            self.buttonPitchEntrySet.Hide()
            self.textRollEntry.Hide()
            self.RollEntry.Hide()
            self.buttonRollEntrySet.Hide()
            self.textGSrollRange.Hide()
            self.textGSpitchRange.Hide()
            # start advanced mode
            self.textDeviceAddress.Show()
            self.textDeviceSubAddress.Show()
            self.textDeviceData.Show()
            self.deviceAddressEntry.Show()
            self.deviceSubAddressEntry.Show()
            self.deviceDataEntry.Show()
            self.buttonAdvancedSend.Show()
            self.textAdvAddr.Show()
            self.errorDeviceAddress.Hide()
            self.errorDeviceSubAddress.Hide()
            self.errorDeviceData.Hide()

        else:
            self.textPitchEntry.Show()
            self.PitchEntry.Show()
            self.buttonPitchEntrySet.Show()
            self.textRollEntry.Show()
            self.RollEntry.Show()
            self.buttonRollEntrySet.Show()
            self.textGSrollRange.Show()
            self.textGSpitchRange.Show()
            # stop advanced mode
            self.textDeviceAddress.Hide()
            self.textDeviceSubAddress.Hide()
            self.textDeviceData.Hide()
            self.deviceAddressEntry.Hide()
            self.deviceSubAddressEntry.Hide()
            self.deviceDataEntry.Hide()
            self.buttonAdvancedSend.Hide()
            self.textAdvAddr.Hide()
            self.errorDeviceAddress.Hide()
            self.errorDeviceSubAddress.Hide()
            self.errorDeviceData.Hide()

    def advancedSend(self, event):
        advDeviceAddress = self.deviceAddressEntry.GetValue()
        advDeviceSubAddress = self.deviceSubAddressEntry.GetValue()
        advData = self.deviceDataEntry.GetValue()
        print("advanced data =", advDeviceAddress, advDeviceSubAddress, advData)
        # process entry fields
        allDataValid = True
        portID = ""
        if advDeviceAddress == "0x30" or advDeviceAddress == "0X30" or advDeviceAddress == "48":
            portID = "PITCH"
        if advDeviceAddress == "0x32" or advDeviceAddress == "0X32" or advDeviceAddress == "50" :
            portID = "ROLL"
        if portID == "":
            self.errorDeviceAddress.Show()
            allDataValid = False
        else:
            self.errorDeviceAddress.Hide()
        #
        subValue = self.str2int(advDeviceSubAddress)
        if subValue > 63:
            self.errorDeviceSubAddress.Show()
            allDataValid = False
        else:
            self.errorDeviceSubAddress.Hide()
        #
        dataValue = self.str2int(advData)
        if dataValue > 255:
            self.errorDeviceData.Show()
            allDataValid = False
        else:
            self.errorDeviceData.Hide()
        if allDataValid == True:
            self.buttonAdvancedSend.SetBackgroundColour('#80e0c0')
            self.sendData(portID, subValue, dataValue)
        else:
            self.buttonAdvancedSend.SetBackgroundColour('#e05040')


    def ExitClick(self, event):
        if self.pitchPortOpened != "":
            self.closeComPort(self.pitchPortOpened, "PITCH")
        if self.rollPortOpened != "":
            self.closeComPort(self.rollPortOpened, "ROLL")
        if self.firstPHCCcommand == False:
            if self.phccPort.isOpen():
                self.phccPort.close()
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
        self.stopTimer()
        # time out can only occur for ID check PITCH or ROLL IDENTIFY command
        if self.awaitPitchIDresponse == True:
            self.awaitPitchIDresponse = False
        else:
            self.awaitRollIDresponse = False


# =================================================================================================
#  COM port assignments
# =================================================================================================

    def OnSelectPitchPort(self, entry):
        previousPitchPort = self.pitchPort
        self.pitchPort = entry.GetString()

        if self.firstPHCCcommand == False:
            # "switching" from PHCC mode to USB mode: close defaultPhccCOMport first
            if self.phccPort.isOpen():
                self.phccPort.close()

        if previousPitchPort == "":          # initial state
            # no previously opened port, but the selected port may already be in use!
            # if the selected port is in use: do not open port, "!" already shown
            # if the selected port is not in use: hide Exclamation Sign, do open port
            if self.pitchPort == self.rollPort:
                self.pitchPort = ""
            else:
                self.errorPitchPort.Hide()
                previousPitchPort = self.pitchPort
                self.openComPort(self.pitchPort, "PITCH")
                self.pitchPortOpened = self.pitchPort
        #
        elif self.pitchPort == self.rollPort:
            # selected COM port is in use by ROLL SDI: show "!" , do not open port
            self.errorPitchPort.Show()
            # if a COM port was assigned, close it.
            self.closeComPort(previousPitchPort, "PITCH")
            self.pitchPortOpened = ""
            previousPitchPort = self.pitchPort
        #
        elif previousPitchPort == self.pitchPort:
            # Same COM port selected, possible cases: 
            #  1. COM port is not opened (because it is assigned to ROLL SDI)
            #  2. COM port is already opened, just selected again
            #  3. COM port is not opened, but available -> open it
            if self.pitchPort == self.rollPort:
                self.errorPitchPort.Show()                   # 1.
            elif self.pitchPortOpened == self.pitchPort:
                self.errorPitchPort.Hide()                   # 2.
            else:
                self.errorPitchPort.Hide()                   # 3.
                self.openComPort(self.pitchPort, "PITCH")
                self.pitchPortOpened = self.pitchPort
        #
        else:
            # port not in use: assign it!
            # check if already (another) port was opened: then close that one first!
            if self.pitchPortOpened != self.pitchPort:
                # close previous port first
                self.closeComPort(self.pitchPortOpened, "PITCH")
                self.pitchPortOpened = ""
            previousPitchPort = self.pitchPort
            self.errorPitchPort.Hide()
            self.openComPort(self.pitchPort, "PITCH")
            self.pitchPortOpened = self.pitchPort

    def OnSelectRollPort(self, entry):
        previousRollPort = self.rollPort
        self.rollPort = entry.GetString()

        if self.firstPHCCcommand == False:
            # "switching" from PHCC mode to USB mode: close defaultPhccCOMport first
            if self.phccPort.isOpen():
                self.phccPort.close()

        if previousRollPort == "":           # initial state
            # no previously opened port, but the selected port may already be in use!
            # if the selected port is in use: do not open port, "!" already shown
            # if the selected port is not in use: hide Exclamation Sign, do open port
            if self.rollPort == self.pitchPort:
                self.rollPort = ""
            else:
                self.errorRollPort.Hide()
                previousRollPort = self.rollPort
                self.openComPort(self.rollPort, "ROLL")
                self.rollPortOpened = self.rollPort
        #
        elif self.rollPort == self.pitchPort:
            # selected COM port is in use by PITCH SDI: show "!" , do not open port
            self.errorRollPort.Show()
            # if a COM port was assigned, close it.
            self.closeComPort(previousRollPort, "ROLL")
            self.rollPortOpened = ""
            previousRollPort = self.rollPort
        #
        elif previousRollPort == self.rollPort:
            # Same COM port selected, possible cases: 
            #  1. COM port is not opened (because it is assigned to PITCH SDI)
            #  2. COM port is already opened, just selected again
            #  3. COM port is not opened, but available -> open it
            if self.rollPort == self.pitchPort:
                self.errorRollPort.Show()                    # 1.
            elif self.rollPortOpened == self.rollPort:
                self.errorRollPort.Hide()                    # 2.
            else:
                self.errorRollPort.Hide()                    # 3.
                self.openComPort(self.rollPort, "ROLL")
                self.rollPortOpened = self.rollPort
        #
        else:
            # port not in use: assign it!
            # check if already (another) port was opened: then close that one first!
            if self.rollPortOpened != self.rollPort:
                # close previous port first
                self.closeComPort(self.rollPortOpened, "ROLL")
                self.rollPortOpened = ""
            previousRollPort = self.rollPort
            self.errorRollPort.Hide()
            self.openComPort(self.rollPort, "ROLL")
            self.rollPortOpened = self.rollPort


    def openComPort(self, portID, SDIname):
        print(">   openCOMport", portID, "for SDI", SDIname)
        if SDIname == "ROLL":
            self.rollComPort  = serial.Serial(portID, baudrate=115200, parity=serial.PARITY_NONE,
                                              stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        elif SDIname == "PITCH":
            self.pitchComPort = serial.Serial(portID, baudrate=115200, parity=serial.PARITY_NONE,
                                              stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        else:
            print("!!! opening COM port", portID, "for SDI", SDIname, "failed!")
        

    def closeComPort(self, portID, SDIname):
        print(">   closeCOMport", portID, "for SDI", SDIname)
        if SDIname == "ROLL":
            if self.rollComPort.isOpen():
                self.rollComPort.close()
            else:
                print("!!! COM port", portID, "for SDI", SDIname, "is not open!")
        elif SDIname == "PITCH":
            if self.pitchComPort.isOpen():
                self.pitchComPort.close()
            else:
                print("!!! COM port", portID, "for SDI", SDIname, "is not open!")
        else:
            print("!!! closing COM port", portID, "for SDI", SDIname, "failed!")


# =================================================================================================
#  COMMUNICATION  routine: send data
# =================================================================================================

    def sendData(self, portID, subAddress, data):
    #
    # this function is called whenever a button is clicked to send a command.
    # If the COM port for PITCH *and* for ROLL has not been defined, it is assumed that
    #  1. PHCC Motherboard is used
    #  2. serial port defaultPhccCOMport is connected to the PHCC Motherboard
    # Note that the first command must open the defaultPhccCOMport port!
    #
    # If one of the COM ports (for PITCH or ROLL) has been defined, it is assumed that
    #  1. USB interfaces are used to connect to SDI modules
    #  2. that assigned COM port will be used.

#        print("... sendData to", portID, "subAddress", subAddress, "data", data)
        
#        if self.rollPortOpened == "" and self.pitchPortOpened == "":
            # using PHCC Motherboard
#            if self.firstPHCCcommand == True:
                # open defaultPhccCOMport port first
#                self.phccPort = serial.Serial(self.defaultPhccCOMport, baudrate=115200, parity=serial.PARITY_NONE,
#                                              stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
#                self.firstPHCCcommand = False
#            if self.phccPort.isOpen():
#                if portID == "PITCH":
#                    self.phccPort.write(chr(0x07))
#                    self.phccPort.write(chr(0x30))
#                    self.phccPort.write(chr(subAddress))
#                    self.phccPort.write(chr(data))
#                elif portID == "ROLL":
#                    self.phccPort.write(chr(0x07))
#                    self.phccPort.write(chr(0x32))
#                    self.phccPort.write(chr(subAddress))
#                    self.phccPort.write(chr(data))
#                else:
#                    print("!!! Undefined SDI identification for PHCC!")
#            else:
#                print("!!!", self.defaultPhccCOMport, "port for PHCC is not open!")

#        else:
            # using USB connections
            if portID == "ROLL":
                if self.rollPortOpened != "":
                    if self.rollComPort.isOpen():
                        self.rollComPort.write(subAddress.to_bytes(1, byteorder='big', signed=False))
                        self.rollComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                        print("  ROLL  command:", subAddress, data)
                    else:
                        print("!!! COM port", self.rollPortOpened, "for SDI", portID, "is not open!")
                else:
                    print("!!! no COM port defined for SDI", portID)
            elif portID == "PITCH":
                if self.pitchPortOpened != "":
                    if self.pitchComPort.isOpen():
                        self.pitchComPort.write(subAddress.to_bytes(1, byteorder='big', signed=False))
                        self.pitchComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                        print("  PITCH command:", subAddress, data)
                    else:
                        print("!!! COM port", self.pitchPortOpened, "for SDI", portID, "is not open!")
                else:
                    print("!!! no COM port defined for SDI", portID)
            else:
                print("!!! sending data to unknown SDI module", portID)



if __name__ == '__main__':
    app = wx.App()
    window = ADI(None)
    app.MainLoop()
