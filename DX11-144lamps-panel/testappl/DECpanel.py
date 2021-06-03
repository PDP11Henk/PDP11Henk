import time
import wx
import serial

class Example(wx.Frame):
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        self.SetSize((950, 400))
        self.SetTitle('DX11 panel')
        self.SetBackgroundColour("#112233")
        wx.StaticLine(panel, -1, (0, 0), (948, 5))
        self.Centre()
        smallFont = wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        normFont  = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.ON  = 1
        self.OFF = 0
        self.useCOBS = True   # use Continuous Overhead Byte Stuffing YES / NO
                              # not true COBS, but 8-bit checksum and 0xFF delimiter
#
# ------ ROW 1 --------------------------------------------------------------------------
#
        Xpos = 20
        Ypos = 65
        self.ind1 = []
        for x in range(36):
            self.ind1.append( wx.ToggleButton(panel, label=' ', pos=((Xpos + x*25), Ypos), size=(20,20)) )
            self.ind1[x].SetBackgroundColour("#999999")
            self.ind1[x].Bind(wx.EVT_TOGGLEBUTTON, self.ToggleIND1)
        top   = Ypos - 44
        line1 = Ypos - 22
        line2 = Ypos - 12
        #
        txt000 = wx.StaticText(panel, label='PAR', pos=(Xpos, line1))
        wx.StaticLine(panel, -1, (Xpos-1, Ypos-27), (22, 5))
        txt001 = wx.StaticText(panel, label='NXM',   pos=(Xpos+25,  line1))
        txt002 = wx.StaticText(panel, label='SEL',   pos=(Xpos+50,  line1))
        txt003 = wx.StaticText(panel, label='SYS',   pos=(Xpos+75,  line1))
        txt004 = wx.StaticText(panel, label='RST',   pos=(Xpos+50,  line2))
        txt005 = wx.StaticText(panel, label='RST',   pos=(Xpos+75,  line2))
        wx.StaticLine(panel, -1, (Xpos-1+25, Ypos-27), (72, 5))
        txt006 = wx.StaticText(panel, label='INF',   pos=(Xpos+102, line1))
        txt007 = wx.StaticText(panel, label='CH',    pos=(Xpos+153, line1))
        txt008 = wx.StaticText(panel, label='DSC',   pos=(Xpos+100, line2))
        txt009 = wx.StaticText(panel, label='UCHKS', pos=(Xpos+120, line2))
        txt010 = wx.StaticText(panel, label='ENDS',  pos=(Xpos+150, line2))
        wx.StaticLine(panel, -1, (Xpos-1+100, Ypos-27), (72, 5))
        txt011 = wx.StaticText(panel, label='ES',    pos=(Xpos+225+3, line1))
        txt012 = wx.StaticText(panel, label='BSYS',  pos=(Xpos+175, line2))
        txt013 = wx.StaticText(panel, label='CHIS',  pos=(Xpos+200, line2))
        txt014 = wx.StaticText(panel, label='END',   pos=(Xpos+225, line2))
        wx.StaticLine(panel, -1, (Xpos-1+175, Ypos-27), (72, 5))
        txt015 = wx.StaticText(panel, label='CHD',   pos=(Xpos+250, line1))
        txt016 = wx.StaticText(panel, label='CUD',   pos=(Xpos+275, line1))
        txt017 = wx.StaticText(panel, label='ISS',   pos=(Xpos+300+2, line1))
        txt018 = wx.StaticText(panel, label='END',   pos=(Xpos+250, line2))
        txt019 = wx.StaticText(panel, label='END',   pos=(Xpos+275, line2))
        txt020 = wx.StaticText(panel, label='REJ',   pos=(Xpos+300, line2))
        wx.StaticLine(panel, -1, (Xpos-1+250, Ypos-27), (72, 5))
        txt021 = wx.StaticText(panel, label='CMD',   pos=(Xpos+325, line1))
        txt022 = wx.StaticText(panel, label='STK',   pos=(Xpos+350, line1))
        txt023 = wx.StaticText(panel, label='CMD',   pos=(Xpos+375, line1))
        txt024 = wx.StaticText(panel, label='CHN',   pos=(Xpos+325, line2))
        txt025 = wx.StaticText(panel, label='STB',   pos=(Xpos+350, line2))
        txt026 = wx.StaticText(panel, label='REJ',   pos=(Xpos+375, line2))
        wx.StaticLine(panel, -1, (Xpos-1+325, Ypos-27), (72, 5))
        txt027 = wx.StaticText(panel, label='STA',   pos=(Xpos+425, line1))
        txt028 = wx.StaticText(panel, label='CU',    pos=(Xpos+450+3, line1))
        txt029 = wx.StaticText(panel, label='ATTN',  pos=(Xpos+400, line2))
        txt030 = wx.StaticText(panel, label='MOD',   pos=(Xpos+425, line2))
        txt031 = wx.StaticText(panel, label='END',   pos=(Xpos+450, line2))
        txt032 = wx.StaticText(panel, label='BSY',   pos=(Xpos+475, line2))
        wx.StaticLine(panel, -1, (Xpos-1+403, Ypos-27), (91, 5))
        txt033 = wx.StaticText(panel, label='OPLO',  pos=(Xpos+500, line2))
        txt034 = wx.StaticText(panel, label='HLDO',  pos=(Xpos+525, line2))
        txt035 = wx.StaticText(panel, label='SELO',  pos=(Xpos+550, line2))
        txt036 = wx.StaticText(panel, label='SUPO',  pos=(Xpos+575, line2))
        txt037 = wx.StaticText(panel, label='ADRO',  pos=(Xpos+600, line2))
        txt038 = wx.StaticText(panel, label='CMDO',  pos=(Xpos+625, line2))
        txt039 = wx.StaticText(panel, label='SRVO',  pos=(Xpos+650, line2))
        wx.StaticLine(panel, -1, (Xpos-1+500, Ypos-18), (49, 2))
        txt040 = wx.StaticText(panel, label='CONTROL  FLOPS', pos=(Xpos+551, line1))
        wx.StaticLine(panel, -1, (Xpos-1+622, Ypos-18), (50, 2))
        wx.StaticLine(panel, -1, (Xpos-1+500, Ypos-27), (22, 5))
        wx.StaticLine(panel, -1, (Xpos-1+525, Ypos-27), (72, 5))
        wx.StaticLine(panel, -1, (Xpos-1+600, Ypos-27), (72, 5))
        txt041 = wx.StaticText(panel, label='PARO',  pos=(Xpos+675, line2))
        txt042 = wx.StaticText(panel, label='07',    pos=(Xpos+700+5, line2))
        txt043 = wx.StaticText(panel, label='06',    pos=(Xpos+725+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+675, Ypos-27), (72, 5))
        txt044 = wx.StaticText(panel, label='05',    pos=(Xpos+750+5, line2))
        txt045 = wx.StaticText(panel, label='04',    pos=(Xpos+775+5, line2))
        txt046 = wx.StaticText(panel, label='03',    pos=(Xpos+800+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+750, Ypos-27), (72, 5))
        txt047 = wx.StaticText(panel, label='02',    pos=(Xpos+825+5, line2))
        txt048 = wx.StaticText(panel, label='01',    pos=(Xpos+850+5, line2))
        txt049 = wx.StaticText(panel, label='00',    pos=(Xpos+875+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+825, Ypos-27), (72, 5))
        wx.StaticLine(panel, -1, (Xpos-1+675, Ypos-18), (67, 2))
        txt050 = wx.StaticText(panel, label="REC'D  BUS  OUT  LINES", pos=(Xpos+744, line1))
        wx.StaticLine(panel, -1, (Xpos-1+840, Ypos-18), (57, 2))
        txt051 = wx.StaticText(panel, label='DXDS  _ _00', pos=(Xpos+155, top))
        txt052 = wx.StaticText(panel, label='CUSR  _ _06', pos=(Xpos+410, top))
        txt053 = wx.StaticText(panel, label='DXMO  _ _14', pos=(Xpos+665, top))
        #
        txt000.SetFont(smallFont)
        txt001.SetFont(smallFont)
        txt002.SetFont(smallFont)
        txt003.SetFont(smallFont)
        txt004.SetFont(smallFont)
        txt005.SetFont(smallFont)
        txt006.SetFont(smallFont)
        txt007.SetFont(smallFont)
        txt008.SetFont(smallFont)
        txt009.SetFont(smallFont)
        txt010.SetFont(smallFont)
        txt011.SetFont(smallFont)
        txt012.SetFont(smallFont)
        txt013.SetFont(smallFont)
        txt014.SetFont(smallFont)
        txt015.SetFont(smallFont)
        txt016.SetFont(smallFont)
        txt017.SetFont(smallFont)
        txt018.SetFont(smallFont)
        txt019.SetFont(smallFont)
        txt020.SetFont(smallFont)
        txt021.SetFont(smallFont)
        txt022.SetFont(smallFont)
        txt023.SetFont(smallFont)
        txt024.SetFont(smallFont)
        txt025.SetFont(smallFont)
        txt026.SetFont(smallFont)
        txt027.SetFont(smallFont)
        txt028.SetFont(smallFont)
        txt029.SetFont(smallFont)
        txt030.SetFont(smallFont)
        txt031.SetFont(smallFont)
        txt032.SetFont(smallFont)
        txt033.SetFont(smallFont)
        txt034.SetFont(smallFont)
        txt035.SetFont(smallFont)
        txt036.SetFont(smallFont)
        txt037.SetFont(smallFont)
        txt038.SetFont(smallFont)
        txt039.SetFont(smallFont)
        txt040.SetFont(smallFont)
        txt041.SetFont(smallFont)
        txt042.SetFont(smallFont)
        txt043.SetFont(smallFont)
        txt044.SetFont(smallFont)
        txt045.SetFont(smallFont)
        txt046.SetFont(smallFont)
        txt047.SetFont(smallFont)
        txt048.SetFont(smallFont)
        txt049.SetFont(smallFont)
        txt050.SetFont(smallFont)
        txt051.SetFont(normFont)
        txt052.SetFont(normFont)
        txt053.SetFont(normFont)
        txt000.SetForegroundColour("#FFFFFF")
        txt001.SetForegroundColour("#FFFFFF")
        txt002.SetForegroundColour("#FFFFFF")
        txt003.SetForegroundColour("#FFFFFF")
        txt004.SetForegroundColour("#FFFFFF")
        txt005.SetForegroundColour("#FFFFFF")
        txt006.SetForegroundColour("#FFFFFF")
        txt007.SetForegroundColour("#FFFFFF")
        txt008.SetForegroundColour("#FFFFFF")
        txt009.SetForegroundColour("#FFFFFF")
        txt010.SetForegroundColour("#FFFFFF")
        txt011.SetForegroundColour("#FFFFFF")
        txt012.SetForegroundColour("#FFFFFF")
        txt013.SetForegroundColour("#FFFFFF")
        txt014.SetForegroundColour("#FFFFFF")
        txt015.SetForegroundColour("#FFFFFF")
        txt016.SetForegroundColour("#FFFFFF")
        txt017.SetForegroundColour("#FFFFFF")
        txt018.SetForegroundColour("#FFFFFF")
        txt019.SetForegroundColour("#FFFFFF")
        txt020.SetForegroundColour("#FFFFFF")
        txt021.SetForegroundColour("#FFFFFF")
        txt022.SetForegroundColour("#FFFFFF")
        txt023.SetForegroundColour("#FFFFFF")
        txt024.SetForegroundColour("#FFFFFF")
        txt025.SetForegroundColour("#FFFFFF")
        txt026.SetForegroundColour("#FFFFFF")
        txt027.SetForegroundColour("#FFFFFF")
        txt028.SetForegroundColour("#FFFFFF")
        txt029.SetForegroundColour("#FFFFFF")
        txt030.SetForegroundColour("#FFFFFF")
        txt031.SetForegroundColour("#FFFFFF")
        txt032.SetForegroundColour("#FFFFFF")
        txt033.SetForegroundColour("#FFFFFF")
        txt034.SetForegroundColour("#FFFFFF")
        txt035.SetForegroundColour("#FFFFFF")
        txt036.SetForegroundColour("#FFFFFF")
        txt037.SetForegroundColour("#FFFFFF")
        txt038.SetForegroundColour("#FFFFFF")
        txt039.SetForegroundColour("#FFFFFF")
        txt040.SetForegroundColour("#FFFFFF")
        txt041.SetForegroundColour("#FFFFFF")
        txt042.SetForegroundColour("#FFFFFF")
        txt043.SetForegroundColour("#FFFFFF")
        txt044.SetForegroundColour("#FFFFFF")
        txt045.SetForegroundColour("#FFFFFF")
        txt046.SetForegroundColour("#FFFFFF")
        txt047.SetForegroundColour("#FFFFFF")
        txt048.SetForegroundColour("#FFFFFF")
        txt049.SetForegroundColour("#FFFFFF")
        txt050.SetForegroundColour("#FFFFFF")
        txt051.SetForegroundColour("#FFFFFF")
        txt052.SetForegroundColour("#FFFFFF")
        txt053.SetForegroundColour("#FFFFFF")
#
# ------ ROW 2 --------------------------------------------------------------------------
#
        Xpos = 20
        Ypos = Ypos + 70
        self.ind2 = []
        for x in range(36):
            self.ind2.append( wx.ToggleButton(panel, label=' ', pos=((Xpos + x*25), Ypos), size=(20,20)) )
            self.ind2[x].SetBackgroundColour("#999999")
            self.ind2[x].Bind(wx.EVT_TOGGLEBUTTON, self.ToggleIND2)
        top   = Ypos - 44
        line1 = Ypos - 22
        line2 = Ypos - 12
        #
        txt100 = wx.StaticText(panel, label='07', pos=(Xpos+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1, Ypos-27), (22, 5))
        txt101 = wx.StaticText(panel, label='06',   pos=(Xpos+25+5,  line2))
        txt102 = wx.StaticText(panel, label='05',   pos=(Xpos+50+5,  line2))
        txt103 = wx.StaticText(panel, label='04',   pos=(Xpos+75+5,  line2))
        wx.StaticLine(panel, -1, (Xpos-1+25, Ypos-27), (72, 5))
        txt104 = wx.StaticText(panel, label='03',   pos=(Xpos+100+5, line2))
        txt105 = wx.StaticText(panel, label='02',   pos=(Xpos+125+5, line2))
        txt106 = wx.StaticText(panel, label='01',   pos=(Xpos+150+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+100, Ypos-27), (72, 5))
        txt107 = wx.StaticText(panel, label='00',   pos=(Xpos+175+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+175, Ypos-27), (20, 5))
        txt108 = wx.StaticText(panel, label='07',   pos=(Xpos+200+5, line2))
        txt109 = wx.StaticText(panel, label='06',   pos=(Xpos+225+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+202, Ypos-27), (45, 5))
        txt110 = wx.StaticText(panel, label='05',   pos=(Xpos+250+5, line2))
        txt111 = wx.StaticText(panel, label='04',   pos=(Xpos+275+5, line2))
        txt112 = wx.StaticText(panel, label='03',   pos=(Xpos+300+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+250, Ypos-27), (72, 5))
        txt113 = wx.StaticText(panel, label='02',   pos=(Xpos+325+5, line2))
        txt114 = wx.StaticText(panel, label='01',   pos=(Xpos+350+5, line2))
        txt115 = wx.StaticText(panel, label='00',   pos=(Xpos+375+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+325, Ypos-27), (72, 5))
        txt116 = wx.StaticText(panel, label='CH',   pos=(Xpos+400+5, line1))
        txt117 = wx.StaticText(panel, label='DEV',  pos=(Xpos+425, line1))
        txt118 = wx.StaticText(panel, label='END',  pos=(Xpos+400, line2))
        txt119 = wx.StaticText(panel, label='END',  pos=(Xpos+425, line2))
        txt120 = wx.StaticText(panel, label='UCHK', pos=(Xpos+447, line2))  # no E in text
        txt121 = wx.StaticText(panel, label='UXCP', pos=(Xpos+476, line2))  # no E in text
        wx.StaticLine(panel, -1, (Xpos-1+403, Ypos-27), (91, 5))
        txt122 = wx.StaticText(panel, label='OPLI',  pos=(Xpos+500+2, line2))
        txt123 = wx.StaticText(panel, label='SELI',  pos=(Xpos+525, line2))
        txt124 = wx.StaticText(panel, label='REQI',  pos=(Xpos+550, line2))
        txt125 = wx.StaticText(panel, label='ADRI',  pos=(Xpos+575, line2))
        txt126 = wx.StaticText(panel, label='STAI',  pos=(Xpos+600, line2))
        txt127 = wx.StaticText(panel, label='SRVI',  pos=(Xpos+625, line2))
        txt128 = wx.StaticText(panel, label='CLKO',  pos=(Xpos+650, line2))
        wx.StaticLine(panel, -1, (Xpos-1+502, Ypos-18), (43, 2))
        txt129 = wx.StaticText(panel, label='CONI  FLOPS', pos=(Xpos+547, line1))
        wx.StaticLine(panel, -1, (Xpos-1+599, Ypos-18), (48, 2))
        wx.StaticLine(panel, -1, (Xpos-1+502, Ypos-27), (20, 5))
        wx.StaticLine(panel, -1, (Xpos-1+525, Ypos-27), (72, 5))
        wx.StaticLine(panel, -1, (Xpos-1+600, Ypos-27), (72, 5))
        txt130 = wx.StaticText(panel, label='PARI',  pos=(Xpos+675, line2))
        txt131 = wx.StaticText(panel, label='07',    pos=(Xpos+700+5, line2))
        txt132 = wx.StaticText(panel, label='06',    pos=(Xpos+725+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+675, Ypos-27), (72, 5))
        txt133 = wx.StaticText(panel, label='05',    pos=(Xpos+750+5, line2))
        txt134 = wx.StaticText(panel, label='04',    pos=(Xpos+775+5, line2))
        txt135 = wx.StaticText(panel, label='03',    pos=(Xpos+800+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+750, Ypos-27), (72, 5))
        txt136 = wx.StaticText(panel, label='02',    pos=(Xpos+825+5, line2))
        txt137 = wx.StaticText(panel, label='01',    pos=(Xpos+850+5, line2))
        txt138 = wx.StaticText(panel, label='00',    pos=(Xpos+875+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+825, Ypos-27), (72, 5))
        wx.StaticLine(panel, -1, (Xpos-1+675, Ypos-18), (87, 2))
        txt139 = wx.StaticText(panel, label="BUSI  FLOPS", pos=(Xpos+764, line1))
        wx.StaticLine(panel, -1, (Xpos-1+816, Ypos-18), (81, 2))
        txt140 = wx.StaticText(panel, label='CUCR  _ _03', pos=(Xpos+60, top))
        txt141 = wx.StaticText(panel, label='CUAR  _ _02', pos=(Xpos+260, top))
        txt142 = wx.StaticText(panel, label='DXMI  _ _16', pos=(Xpos+665, top))
        #
        txt100.SetFont(smallFont)
        txt101.SetFont(smallFont)
        txt102.SetFont(smallFont)
        txt103.SetFont(smallFont)
        txt104.SetFont(smallFont)
        txt105.SetFont(smallFont)
        txt106.SetFont(smallFont)
        txt107.SetFont(smallFont)
        txt108.SetFont(smallFont)
        txt109.SetFont(smallFont)
        txt110.SetFont(smallFont)
        txt111.SetFont(smallFont)
        txt112.SetFont(smallFont)
        txt113.SetFont(smallFont)
        txt114.SetFont(smallFont)
        txt115.SetFont(smallFont)
        txt116.SetFont(smallFont)
        txt117.SetFont(smallFont)
        txt118.SetFont(smallFont)
        txt119.SetFont(smallFont)
        txt120.SetFont(smallFont)
        txt121.SetFont(smallFont)
        txt122.SetFont(smallFont)
        txt123.SetFont(smallFont)
        txt124.SetFont(smallFont)
        txt125.SetFont(smallFont)
        txt126.SetFont(smallFont)
        txt127.SetFont(smallFont)
        txt128.SetFont(smallFont)
        txt129.SetFont(smallFont)
        txt130.SetFont(smallFont)
        txt131.SetFont(smallFont)
        txt132.SetFont(smallFont)
        txt133.SetFont(smallFont)
        txt134.SetFont(smallFont)
        txt135.SetFont(smallFont)
        txt136.SetFont(smallFont)
        txt137.SetFont(smallFont)
        txt138.SetFont(smallFont)
        txt139.SetFont(smallFont)
        txt140.SetFont(normFont)
        txt141.SetFont(normFont)
        txt142.SetFont(normFont)
        txt100.SetForegroundColour("#FFFFFF")
        txt101.SetForegroundColour("#FFFFFF")
        txt102.SetForegroundColour("#FFFFFF")
        txt103.SetForegroundColour("#FFFFFF")
        txt104.SetForegroundColour("#FFFFFF")
        txt105.SetForegroundColour("#FFFFFF")
        txt106.SetForegroundColour("#FFFFFF")
        txt107.SetForegroundColour("#FFFFFF")
        txt108.SetForegroundColour("#FFFFFF")
        txt109.SetForegroundColour("#FFFFFF")
        txt110.SetForegroundColour("#FFFFFF")
        txt111.SetForegroundColour("#FFFFFF")
        txt112.SetForegroundColour("#FFFFFF")
        txt113.SetForegroundColour("#FFFFFF")
        txt114.SetForegroundColour("#FFFFFF")
        txt115.SetForegroundColour("#FFFFFF")
        txt116.SetForegroundColour("#FFFFFF")
        txt117.SetForegroundColour("#FFFFFF")
        txt118.SetForegroundColour("#FFFFFF")
        txt119.SetForegroundColour("#FFFFFF")
        txt120.SetForegroundColour("#FFFFFF")
        txt121.SetForegroundColour("#FFFFFF")
        txt122.SetForegroundColour("#FFFFFF")
        txt123.SetForegroundColour("#FFFFFF")
        txt124.SetForegroundColour("#FFFFFF")
        txt125.SetForegroundColour("#FFFFFF")
        txt126.SetForegroundColour("#FFFFFF")
        txt127.SetForegroundColour("#FFFFFF")
        txt128.SetForegroundColour("#FFFFFF")
        txt129.SetForegroundColour("#FFFFFF")
        txt130.SetForegroundColour("#FFFFFF")
        txt131.SetForegroundColour("#FFFFFF")
        txt132.SetForegroundColour("#FFFFFF")
        txt133.SetForegroundColour("#FFFFFF")
        txt134.SetForegroundColour("#FFFFFF")
        txt135.SetForegroundColour("#FFFFFF")
        txt136.SetForegroundColour("#FFFFFF")
        txt137.SetForegroundColour("#FFFFFF")
        txt138.SetForegroundColour("#FFFFFF")
        txt139.SetForegroundColour("#FFFFFF")
        txt140.SetForegroundColour("#FFFFFF")
        txt141.SetForegroundColour("#FFFFFF")
        txt142.SetForegroundColour("#FFFFFF")
#
# ------ ROW 3 --------------------------------------------------------------------------
#
        Xpos = 20
        Ypos = Ypos + 70
        self.ind3 = []
        for x in range(36):
            self.ind3.append( wx.ToggleButton(panel, label=' ', pos=((Xpos + x*25), Ypos), size=(20,20)) )
            self.ind3[x].SetBackgroundColour("#999999")
            self.ind3[x].Bind(wx.EVT_TOGGLEBUTTON, self.ToggleIND3)
        top   = Ypos - 44
        line1 = Ypos - 22
        line2 = Ypos - 12
        #
        txt300 = wx.StaticText(panel, label='PAR',  pos=(Xpos, line1))
        wx.StaticLine(panel, -1, (Xpos-1, Ypos-27), (22, 5))
        txt301 = wx.StaticText(panel, label='CU',   pos=(Xpos+25+3, line1))
        txt302 = wx.StaticText(panel, label='END',  pos=(Xpos+50,  line1))
        txt303 = wx.StaticText(panel, label='STP',  pos=(Xpos,     line2))
        txt304 = wx.StaticText(panel, label='FBM',  pos=(Xpos+25,  line2))
        txt305 = wx.StaticText(panel, label='EN',   pos=(Xpos+50+3, line2))
        wx.StaticLine(panel, -1, (Xpos-1+25, Ypos-27), (72, 5))
        txt306 = wx.StaticText(panel, label='BSY',  pos=(Xpos+100, line1))
        txt307 = wx.StaticText(panel, label='ON',   pos=(Xpos+150+3, line1))
        txt308 = wx.StaticText(panel, label='EN',   pos=(Xpos+100+3, line2))
        txt309 = wx.StaticText(panel, label='LINA', pos=(Xpos+150, line2))
        wx.StaticLine(panel, -1, (Xpos-1+100, Ypos-27), (72, 5))
        txt310 = wx.StaticText(panel, label='CU',   pos=(Xpos+175+3, line1))
        txt311 = wx.StaticText(panel, label='INT',  pos=(Xpos+225+3, line1))
        txt312 = wx.StaticText(panel, label='BSY',  pos=(Xpos+175, line2))
        txt313 = wx.StaticText(panel, label='DONE', pos=(Xpos+200, line2))
        txt314 = wx.StaticText(panel, label='EN',   pos=(Xpos+225+4, line2))
        wx.StaticLine(panel, -1, (Xpos-1+175, Ypos-27), (72, 5))
        txt315 = wx.StaticText(panel, label='STK',  pos=(Xpos+250, line1))
        txt316 = wx.StaticText(panel, label='XBA',  pos=(Xpos+275, line1))
        txt317 = wx.StaticText(panel, label='XBA',  pos=(Xpos+300, line1))
        txt318 = wx.StaticText(panel, label='STA',  pos=(Xpos+250, line2))
        txt319 = wx.StaticText(panel, label='17',   pos=(Xpos+275+3, line2))
        txt320 = wx.StaticText(panel, label='16',   pos=(Xpos+300+3, line2))
        wx.StaticLine(panel, -1, (Xpos-1+250, Ypos-27), (72, 5))
        txt321 = wx.StaticText(panel, label='FCTN', pos=(Xpos+325, line1))
        txt322 = wx.StaticText(panel, label='FCTN', pos=(Xpos+350, line1))
        txt323 = wx.StaticText(panel, label='2',    pos=(Xpos+325+10, line2))
        txt324 = wx.StaticText(panel, label='1',    pos=(Xpos+350+10, line2))
        txt325 = wx.StaticText(panel, label='GO',   pos=(Xpos+375+3, line2))
        wx.StaticLine(panel, -1, (Xpos-1+325, Ypos-27), (72, 5))
        txt326 = wx.StaticText(panel, label='TIM',  pos=(Xpos+450, line1))
        txt327 = wx.StaticText(panel, label='PAR',  pos=(Xpos+475, line1))
        txt328 = wx.StaticText(panel, label='DIS',  pos=(Xpos+450, line2))
        txt329 = wx.StaticText(panel, label='OK',   pos=(Xpos+475+3, line2))
        txt330 = wx.StaticText(panel, label='LOCKO', pos=(Xpos+500-2, line2))
        txt331 = wx.StaticText(panel, label='2',     pos=(Xpos+525+10, line2))
        txt332 = wx.StaticText(panel, label='1',     pos=(Xpos+550+10, line2))
        txt333 = wx.StaticText(panel, label='0',     pos=(Xpos+575+10, line2))
        txt334 = wx.StaticText(panel, label='TSFF',  pos=(Xpos+600, line2))
        txt335 = wx.StaticText(panel, label='CU',    pos=(Xpos+625+3,  line2))
        txt336 = wx.StaticText(panel, label='SYNC',  pos=(Xpos+650, line2))
        wx.StaticLine(panel, -1, (Xpos-1+528, Ypos-18), (20, 2))
        txt337 = wx.StaticText(panel, label='PHASE', pos=(Xpos+547, line1))
        wx.StaticLine(panel, -1, (Xpos-1+576, Ypos-18), (20, 2))
        wx.StaticLine(panel, -1, (Xpos-1+500, Ypos-27), (22, 5))
        wx.StaticLine(panel, -1, (Xpos-1+525, Ypos-27), (72, 5))
        wx.StaticLine(panel, -1, (Xpos-1+600, Ypos-27), (72, 5))
        txt338 = wx.StaticText(panel, label='FAST',   pos=(Xpos+625, line1))
        txt339 = wx.StaticText(panel, label='BY',     pos=(Xpos+725+3, line1))
        txt340 = wx.StaticText(panel, label='CUDX',   pos=(Xpos+675, line2))
        txt341 = wx.StaticText(panel, label='IOD',    pos=(Xpos+700+3, line2))
        txt342 = wx.StaticText(panel, label='PAS',    pos=(Xpos+725, line2))
        wx.StaticLine(panel, -1, (Xpos-1+675, Ypos-27), (72, 5))
        txt343 = wx.StaticText(panel, label='NPRX',   pos=(Xpos+750, line2))
        txt344 = wx.StaticText(panel, label='NPRT',   pos=(Xpos+775, line2))
        txt345 = wx.StaticText(panel, label='BALF',   pos=(Xpos+800, line2))
        wx.StaticLine(panel, -1, (Xpos-1+750, Ypos-27), (72, 5))
        txt346 = wx.StaticText(panel, label='LINB',   pos=(Xpos+825, line2))
        txt347 = wx.StaticText(panel, label='ECC',    pos=(Xpos+850, line2))
        txt348 = wx.StaticText(panel, label='ECD',    pos=(Xpos+875, line2))
        txt349 = wx.StaticText(panel, label='ON',     pos=(Xpos+825+3, line1))
        txt350 = wx.StaticText(panel, label='ADD',    pos=(Xpos+850, line1))
        txt351 = wx.StaticText(panel, label='ADR',    pos=(Xpos+875, line1))
        wx.StaticLine(panel, -1, (Xpos-1+825, Ypos-27), (72, 5))
        txt352 = wx.StaticText(panel, label='DXCS  _ _04', pos=(Xpos+155, top))
        txt353 = wx.StaticText(panel, label='DXMO  _ _14', pos=(Xpos+665, top))
        txt300.SetFont(smallFont)
        txt301.SetFont(smallFont)
        txt302.SetFont(smallFont)
        txt303.SetFont(smallFont)
        txt304.SetFont(smallFont)
        txt305.SetFont(smallFont)
        txt306.SetFont(smallFont)
        txt307.SetFont(smallFont)
        txt308.SetFont(smallFont)
        txt309.SetFont(smallFont)
        txt310.SetFont(smallFont)
        txt311.SetFont(smallFont)
        txt312.SetFont(smallFont)
        txt313.SetFont(smallFont)
        txt314.SetFont(smallFont)
        txt315.SetFont(smallFont)
        txt316.SetFont(smallFont)
        txt317.SetFont(smallFont)
        txt318.SetFont(smallFont)
        txt319.SetFont(smallFont)
        txt320.SetFont(smallFont)
        txt321.SetFont(smallFont)
        txt322.SetFont(smallFont)
        txt323.SetFont(smallFont)
        txt324.SetFont(smallFont)
        txt325.SetFont(smallFont)
        txt326.SetFont(smallFont)
        txt327.SetFont(smallFont)
        txt328.SetFont(smallFont)
        txt329.SetFont(smallFont)
        txt330.SetFont(smallFont)
        txt331.SetFont(smallFont)
        txt332.SetFont(smallFont)
        txt333.SetFont(smallFont)
        txt334.SetFont(smallFont)
        txt335.SetFont(smallFont)
        txt336.SetFont(smallFont)
        txt337.SetFont(smallFont)
        txt338.SetFont(smallFont)
        txt339.SetFont(smallFont)
        txt340.SetFont(smallFont)
        txt341.SetFont(smallFont)
        txt342.SetFont(smallFont)
        txt343.SetFont(smallFont)
        txt344.SetFont(smallFont)
        txt345.SetFont(smallFont)
        txt346.SetFont(smallFont)
        txt347.SetFont(smallFont)
        txt348.SetFont(smallFont)
        txt349.SetFont(smallFont)
        txt350.SetFont(smallFont)
        txt351.SetFont(smallFont)
        txt352.SetFont(normFont)
        txt353.SetFont(normFont)
        txt300.SetForegroundColour("#FFFFFF")
        txt301.SetForegroundColour("#FFFFFF")
        txt302.SetForegroundColour("#FFFFFF")
        txt303.SetForegroundColour("#FFFFFF")
        txt304.SetForegroundColour("#FFFFFF")
        txt305.SetForegroundColour("#FFFFFF")
        txt306.SetForegroundColour("#FFFFFF")
        txt307.SetForegroundColour("#FFFFFF")
        txt308.SetForegroundColour("#FFFFFF")
        txt309.SetForegroundColour("#FFFFFF")
        txt310.SetForegroundColour("#FFFFFF")
        txt311.SetForegroundColour("#FFFFFF")
        txt312.SetForegroundColour("#FFFFFF")
        txt313.SetForegroundColour("#FFFFFF")
        txt314.SetForegroundColour("#FFFFFF")
        txt315.SetForegroundColour("#FFFFFF")
        txt316.SetForegroundColour("#FFFFFF")
        txt317.SetForegroundColour("#FFFFFF")
        txt318.SetForegroundColour("#FFFFFF")
        txt319.SetForegroundColour("#FFFFFF")
        txt320.SetForegroundColour("#FFFFFF")
        txt321.SetForegroundColour("#FFFFFF")
        txt322.SetForegroundColour("#FFFFFF")
        txt323.SetForegroundColour("#FFFFFF")
        txt324.SetForegroundColour("#FFFFFF")
        txt325.SetForegroundColour("#FFFFFF")
        txt326.SetForegroundColour("#FFFFFF")
        txt327.SetForegroundColour("#FFFFFF")
        txt328.SetForegroundColour("#FFFFFF")
        txt329.SetForegroundColour("#FFFFFF")
        txt330.SetForegroundColour("#FFFFFF")
        txt331.SetForegroundColour("#FFFFFF")
        txt332.SetForegroundColour("#FFFFFF")
        txt333.SetForegroundColour("#FFFFFF")
        txt334.SetForegroundColour("#FFFFFF")
        txt335.SetForegroundColour("#FFFFFF")
        txt336.SetForegroundColour("#FFFFFF")
        txt337.SetForegroundColour("#FFFFFF")
        txt338.SetForegroundColour("#FFFFFF")
        txt339.SetForegroundColour("#FFFFFF")
        txt340.SetForegroundColour("#FFFFFF")
        txt341.SetForegroundColour("#FFFFFF")
        txt342.SetForegroundColour("#FFFFFF")
        txt343.SetForegroundColour("#FFFFFF")
        txt344.SetForegroundColour("#FFFFFF")
        txt345.SetForegroundColour("#FFFFFF")
        txt346.SetForegroundColour("#FFFFFF")
        txt347.SetForegroundColour("#FFFFFF")
        txt348.SetForegroundColour("#FFFFFF")
        txt349.SetForegroundColour("#FFFFFF")
        txt350.SetForegroundColour("#FFFFFF")
        txt351.SetForegroundColour("#FFFFFF")
        txt352.SetForegroundColour("#FFFFFF")
        txt353.SetForegroundColour("#FFFFFF")
#
# ------ ROW 4 --------------------------------------------------------------------------
#
        Xpos = 20
        Ypos = Ypos + 70
        self.ind4 = []
        for x in range(36):
            self.ind4.append( wx.ToggleButton(panel, label=' ', pos=((Xpos + x*25), Ypos), size=(20,20)) )
            self.ind4[x].SetBackgroundColour("#999999")
            self.ind4[x].Bind(wx.EVT_TOGGLEBUTTON, self.ToggleIND4)
        top   = Ypos - 44
        line1 = Ypos - 22
        line2 = Ypos - 12
        #
        txt400 = wx.StaticText(panel, label='15', pos=(Xpos+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1, Ypos-27), (22, 5))
        txt401 = wx.StaticText(panel, label='14',   pos=(Xpos+25+5,  line2))
        txt402 = wx.StaticText(panel, label='13',   pos=(Xpos+50+5,  line2))
        txt403 = wx.StaticText(panel, label='12',   pos=(Xpos+75+5,  line2))
        wx.StaticLine(panel, -1, (Xpos-1+25, Ypos-27), (72, 5))
        txt404 = wx.StaticText(panel, label='11',   pos=(Xpos+100+5, line2))
        txt405 = wx.StaticText(panel, label='10',   pos=(Xpos+125+5, line2))
        txt406 = wx.StaticText(panel, label='09',   pos=(Xpos+150+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+100, Ypos-27), (72, 5))
        txt407 = wx.StaticText(panel, label='08',   pos=(Xpos+175+5, line2))
        txt408 = wx.StaticText(panel, label='07',   pos=(Xpos+200+5, line2))
        txt409 = wx.StaticText(panel, label='06',   pos=(Xpos+225+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+175, Ypos-27), (72, 5))
        txt410 = wx.StaticText(panel, label='05',   pos=(Xpos+250+5, line2))
        txt411 = wx.StaticText(panel, label='04',   pos=(Xpos+275+5, line2))
        txt412 = wx.StaticText(panel, label='03',   pos=(Xpos+300+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+250, Ypos-27), (72, 5))
        txt413 = wx.StaticText(panel, label='02',   pos=(Xpos+325+5, line2))
        txt414 = wx.StaticText(panel, label='01',   pos=(Xpos+350+5, line2))
        txt415 = wx.StaticText(panel, label='00',   pos=(Xpos+375+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+325, Ypos-27), (72, 5))
        txt416 = wx.StaticText(panel, label='ODD',  pos=(Xpos+400, line2))
        txt417 = wx.StaticText(panel, label='TO',   pos=(Xpos+425+3, line2))
        txt418 = wx.StaticText(panel, label='CLEN', pos=(Xpos+450, line2))
        txt419 = wx.StaticText(panel, label='TO',   pos=(Xpos+475+3, line2))
        txt420 = wx.StaticText(panel, label='NPR',  pos=(Xpos+425, line1))
        txt421 = wx.StaticText(panel, label='MN',   pos=(Xpos+450+3, line1))
        txt422 = wx.StaticText(panel, label='DX',   pos=(Xpos+475+3, line1))
        txt423 = wx.StaticText(panel, label='15',   pos=(Xpos+500+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+500, Ypos-27), (22, 5))
        txt424 = wx.StaticText(panel, label='14',   pos=(Xpos+525+5,  line2))
        txt425 = wx.StaticText(panel, label='13',   pos=(Xpos+550+5,  line2))
        txt426 = wx.StaticText(panel, label='12',   pos=(Xpos+575+5,  line2))
        wx.StaticLine(panel, -1, (Xpos-1+525, Ypos-27), (72, 5))
        txt427 = wx.StaticText(panel, label='11',   pos=(Xpos+600+5, line2))
        txt428 = wx.StaticText(panel, label='10',   pos=(Xpos+625+5, line2))
        txt429 = wx.StaticText(panel, label='09',   pos=(Xpos+650+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+600, Ypos-27), (72, 5))
        txt430 = wx.StaticText(panel, label='08',   pos=(Xpos+675+5, line2))
        txt431 = wx.StaticText(panel, label='07',   pos=(Xpos+700+5, line2))
        txt432 = wx.StaticText(panel, label='06',   pos=(Xpos+725+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+675, Ypos-27), (72, 5))
        txt433 = wx.StaticText(panel, label='05',   pos=(Xpos+750+5, line2))
        txt434 = wx.StaticText(panel, label='04',   pos=(Xpos+775+5, line2))
        txt435 = wx.StaticText(panel, label='03',   pos=(Xpos+800+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+750, Ypos-27), (72, 5))
        txt436 = wx.StaticText(panel, label='02',   pos=(Xpos+825+5, line2))
        txt437 = wx.StaticText(panel, label='01',   pos=(Xpos+850+5, line2))
        txt438 = wx.StaticText(panel, label='00',   pos=(Xpos+875+5, line2))
        wx.StaticLine(panel, -1, (Xpos-1+825, Ypos-27), (72, 5))
        txt439 = wx.StaticText(panel, label='DXBA  _ _10', pos=(Xpos+155, top))
        txt440 = wx.StaticText(panel, label='DXND  _ _22', pos=(Xpos+665, top))
        #
        txt400.SetFont(smallFont)
        txt401.SetFont(smallFont)
        txt402.SetFont(smallFont)
        txt403.SetFont(smallFont)
        txt404.SetFont(smallFont)
        txt405.SetFont(smallFont)
        txt406.SetFont(smallFont)
        txt407.SetFont(smallFont)
        txt408.SetFont(smallFont)
        txt409.SetFont(smallFont)
        txt410.SetFont(smallFont)
        txt411.SetFont(smallFont)
        txt412.SetFont(smallFont)
        txt413.SetFont(smallFont)
        txt414.SetFont(smallFont)
        txt415.SetFont(smallFont)
        txt416.SetFont(smallFont)
        txt417.SetFont(smallFont)
        txt418.SetFont(smallFont)
        txt419.SetFont(smallFont)
        txt420.SetFont(smallFont)
        txt421.SetFont(smallFont)
        txt422.SetFont(smallFont)
        txt423.SetFont(smallFont)
        txt424.SetFont(smallFont)
        txt425.SetFont(smallFont)
        txt426.SetFont(smallFont)
        txt427.SetFont(smallFont)
        txt428.SetFont(smallFont)
        txt429.SetFont(smallFont)
        txt430.SetFont(smallFont)
        txt431.SetFont(smallFont)
        txt432.SetFont(smallFont)
        txt433.SetFont(smallFont)
        txt434.SetFont(smallFont)
        txt435.SetFont(smallFont)
        txt436.SetFont(smallFont)
        txt437.SetFont(smallFont)
        txt438.SetFont(smallFont)
        txt439.SetFont(normFont)
        txt440.SetFont(normFont)
        txt400.SetForegroundColour("#FFFFFF")
        txt401.SetForegroundColour("#FFFFFF")
        txt402.SetForegroundColour("#FFFFFF")
        txt403.SetForegroundColour("#FFFFFF")
        txt404.SetForegroundColour("#FFFFFF")
        txt405.SetForegroundColour("#FFFFFF")
        txt406.SetForegroundColour("#FFFFFF")
        txt407.SetForegroundColour("#FFFFFF")
        txt408.SetForegroundColour("#FFFFFF")
        txt409.SetForegroundColour("#FFFFFF")
        txt410.SetForegroundColour("#FFFFFF")
        txt411.SetForegroundColour("#FFFFFF")
        txt412.SetForegroundColour("#FFFFFF")
        txt413.SetForegroundColour("#FFFFFF")
        txt414.SetForegroundColour("#FFFFFF")
        txt415.SetForegroundColour("#FFFFFF")
        txt416.SetForegroundColour("#FFFFFF")
        txt417.SetForegroundColour("#FFFFFF")
        txt418.SetForegroundColour("#FFFFFF")
        txt419.SetForegroundColour("#FFFFFF")
        txt420.SetForegroundColour("#FFFFFF")
        txt421.SetForegroundColour("#FFFFFF")
        txt422.SetForegroundColour("#FFFFFF")
        txt423.SetForegroundColour("#FFFFFF")
        txt424.SetForegroundColour("#FFFFFF")
        txt425.SetForegroundColour("#FFFFFF")
        txt426.SetForegroundColour("#FFFFFF")
        txt427.SetForegroundColour("#FFFFFF")
        txt428.SetForegroundColour("#FFFFFF")
        txt429.SetForegroundColour("#FFFFFF")
        txt430.SetForegroundColour("#FFFFFF")
        txt431.SetForegroundColour("#FFFFFF")
        txt432.SetForegroundColour("#FFFFFF")
        txt433.SetForegroundColour("#FFFFFF")
        txt434.SetForegroundColour("#FFFFFF")
        txt435.SetForegroundColour("#FFFFFF")
        txt436.SetForegroundColour("#FFFFFF")
        txt437.SetForegroundColour("#FFFFFF")
        txt438.SetForegroundColour("#FFFFFF")
        txt439.SetForegroundColour("#FFFFFF")
        txt440.SetForegroundColour("#FFFFFF")
        #
        # define the "shadow output state" array
        self.outputs = [0] * 20
        wx.StaticLine(panel, -1, (0, 310), (948, 3))
        #
        # find the available COM ports (code works only for Windows)
        self.commPortID        = ""
        self.previousCommPort  = ""
        self.commPortIDtoClose = ""
        self.commPortOpened    = False                   # flag COMM port opened
        self.commPortValid     = False                   # only for "error sign" blinking
        self.errorImage        = wx.Bitmap("error.gif")
        #
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
        #
        # COM port selection / "Open" & "Closed" text / error image
        self.cbComm1 = wx.ComboBox(panel, pos=(20, 326), size=(70, 25), choices=availableCOMports, style=wx.CB_READONLY)
        self.cbComm1.SetToolTip(wx.ToolTip("set COM port"))
        self.cbComm1.Bind(wx.EVT_COMBOBOX, self.OnSelectCommPort)
        openClosedFont = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.textStatusOpened = wx.StaticText(panel, label='Open', pos=(230, 330))
        self.textStatusClosed = wx.StaticText(panel, label='Closed', pos=(230, 330))
        self.textStatusOpened.SetFont(openClosedFont)
        self.textStatusClosed.SetFont(openClosedFont)
        self.textStatusOpened.SetForegroundColour("#04B431")
        self.textStatusClosed.SetForegroundColour("#FF0000")
        self.textStatusOpened.Hide()
        self.textStatusClosed.Hide()
        self.errorCommPort = wx.StaticBitmap(panel, -1, self.errorImage)
        self.errorCommPort.SetPosition((100, 325))
        self.errorCommPortShown = True
        #
        # communication channel OPEN / CLOSE button
        self.buttonCommOpen = wx.Button(panel, label="Open COM port", pos=(100, 325), size=(120, 25))
        self.buttonCommOpen.SetBackgroundColour('#FFCC00')
        self.buttonCommOpen.SetForegroundColour('#000000')
        self.buttonCommOpen.Bind(wx.EVT_BUTTON, self.onCommOpenClick)
        self.buttonCommOpen.Hide()
        #
        # define timer
        self.timer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timerIsRunning = False
        self.startTimer(500)                  # and start: initially COM port not assigned
        #
        # Exit button
        self.buttonExit = wx.Button(panel, label="Exit", pos=(352, 325), size=(70, 25))
        self.buttonExit.SetBackgroundColour('#99CCFF')
        self.buttonExit.SetForegroundColour('#FF0000')
        self.buttonExit.Bind(wx.EVT_BUTTON, self.ExitClick)
        #
        # COBS (Continuous Overhead Byte Stuffing
        #self.toggleCOBS = wx.CheckBox(panel, label='COBS', pos=(290, 328), size=(40, 20))
        #self.toggleCOBS.SetValue(False)
        #self.toggleCOBS.SetFont(smallFont)
        #self.toggleCOBS.SetForegroundColour("#FFFF00")
        #self.toggleCOBS.Bind(wx.EVT_CHECKBOX, self.toggleSettingCOBS)
        #
        # spare outputs (available in hardware, but not connected to DX11 panel)
        Xpos = 520
        Ypos = 330
        self.ind5 = []
        for x in range(16):
            self.ind5.append( wx.ToggleButton(panel, label=' ', pos=((Xpos + x*25), Ypos), size=(20,20)) )
            self.ind5[x].SetBackgroundColour("#999999")
            self.ind5[x].Bind(wx.EVT_TOGGLEBUTTON, self.ToggleIND5)
        line = Ypos - 12
        txt500 = wx.StaticText(panel, label='15', pos=(Xpos+5, line))
        txt501 = wx.StaticText(panel, label='14', pos=(Xpos+25+5, line))
        txt502 = wx.StaticText(panel, label='13', pos=(Xpos+50+5, line))
        txt503 = wx.StaticText(panel, label='12', pos=(Xpos+75+5, line))
        txt504 = wx.StaticText(panel, label='11', pos=(Xpos+100+5, line))
        txt505 = wx.StaticText(panel, label='10', pos=(Xpos+125+5, line))
        txt506 = wx.StaticText(panel, label='09', pos=(Xpos+150+5, line))
        txt507 = wx.StaticText(panel, label='08', pos=(Xpos+175+5, line))
        txt508 = wx.StaticText(panel, label='07', pos=(Xpos+200+5, line))
        txt509 = wx.StaticText(panel, label='06', pos=(Xpos+225+5, line))
        txt510 = wx.StaticText(panel, label='05', pos=(Xpos+250+5, line))
        txt511 = wx.StaticText(panel, label='04', pos=(Xpos+275+5, line))
        txt512 = wx.StaticText(panel, label='03', pos=(Xpos+300+5, line))
        txt513 = wx.StaticText(panel, label='02', pos=(Xpos+325+5, line))
        txt514 = wx.StaticText(panel, label='01', pos=(Xpos+350+5, line))
        txt515 = wx.StaticText(panel, label='00', pos=(Xpos+375+5, line))
        txt500.SetFont(smallFont)
        txt501.SetFont(smallFont)
        txt502.SetFont(smallFont)
        txt503.SetFont(smallFont)
        txt504.SetFont(smallFont)
        txt505.SetFont(smallFont)
        txt506.SetFont(smallFont)
        txt507.SetFont(smallFont)
        txt508.SetFont(smallFont)
        txt509.SetFont(smallFont)
        txt510.SetFont(smallFont)
        txt511.SetFont(smallFont)
        txt512.SetFont(smallFont)
        txt513.SetFont(smallFont)
        txt514.SetFont(smallFont)
        txt515.SetFont(smallFont)
        txt500.SetForegroundColour("#00FFFF")
        txt501.SetForegroundColour("#00FFFF")
        txt502.SetForegroundColour("#00FFFF")
        txt503.SetForegroundColour("#00FFFF")
        txt504.SetForegroundColour("#00FFFF")
        txt505.SetForegroundColour("#00FFFF")
        txt506.SetForegroundColour("#00FFFF")
        txt507.SetForegroundColour("#00FFFF")
        txt508.SetForegroundColour("#00FFFF")
        txt509.SetForegroundColour("#00FFFF")
        txt510.SetForegroundColour("#00FFFF")
        txt511.SetForegroundColour("#00FFFF")
        txt512.SetForegroundColour("#00FFFF")
        txt513.SetForegroundColour("#00FFFF")
        txt514.SetForegroundColour("#00FFFF")
        txt515.SetForegroundColour("#00FFFF")
# =======================================================================================
# =======================================================================================

    def getBitPos(self, indNo):
        if (indNo == 0):
            return 7
        elif (indNo == 1):
            return 6
        elif (indNo == 2):
            return 5
        elif (indNo == 3):
            return 4
        elif (indNo == 4):
            return 3
        elif (indNo == 5):
            return 2
        elif (indNo == 6):
            return 1
        else:
            return 0

    def sendUpdate(self, address, data):
        if self.commPortOpened == True:
            if self.ComPort.isOpen():
                if (self.useCOBS == False):
                    print("... sendUpdate address %02X data %02X" % (address, data))
                    self.ComPort.write(address.to_bytes(1, byteorder='big', signed=False))
                    self.ComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                else:
                    # "COBS" : check 3rd byte: 8-bit checksum and 4th byte: 0xFF delimiter
                    checksum  = (address + data) & 0x00FF
                    delimiter = 0xFF
                    print("... sendUpdate address %02X data %02X checksum %02X delimiter %02X" % (address, data, checksum, delimiter))
                    self.ComPort.write(address.to_bytes(1, byteorder='big', signed=False))
                    self.ComPort.write(data.to_bytes(1, byteorder='big', signed=False))
                    self.ComPort.write(checksum.to_bytes(1, byteorder='big', signed=False))
                    self.ComPort.write(delimiter.to_bytes(1, byteorder='big', signed=False))
            else:
                print("!!! COM port is closed!")
        else:
            print("COM port not opened: no data sent")

    def modifyIndicator(self, group, bitPos, state):
        current = self.outputs[group]
        mask = (1 << bitPos)
        if (state == self.ON):
            current = current | mask
        else:
            current = current & (255 - mask)
        self.outputs[group] = current
        self.sendUpdate(group, current)

    def ToggleIND1(self, e):
        obj = e.GetEventObject()
        x = self.ind1.index(obj)
        isPressed = obj.GetValue()
        group = int(x / 8)
        bitPos = self.getBitPos(x % 8)
        if isPressed:
            self.ind1[x].SetBackgroundColour("#FF0000")
            self.modifyIndicator(group, bitPos, self.ON)
        else:
            self.ind1[x].SetBackgroundColour("#999999")
            self.modifyIndicator(group, bitPos, self.OFF)

    def ToggleIND2(self, e):
        obj = e.GetEventObject()
        x = self.ind2.index(obj)
        isPressed = obj.GetValue()
        shiftX = x + 4
        group = int(shiftX / 8) + 4
        bitPos = self.getBitPos(shiftX % 8)
        if isPressed:
            self.ind2[x].SetBackgroundColour("#FF0000")
            self.modifyIndicator(group, bitPos, self.ON)
        else:
            self.ind2[x].SetBackgroundColour("#999999")
            self.modifyIndicator(group, bitPos, self.OFF)

    def ToggleIND3(self, e):
        obj = e.GetEventObject()
        x = self.ind3.index(obj)
        isPressed = obj.GetValue()
        group = int(x / 8) + 9
        bitPos = self.getBitPos(x % 8)
        if isPressed:
            self.ind3[x].SetBackgroundColour("#FF0000")
            self.modifyIndicator(group, bitPos, self.ON)
        else:
            self.ind3[x].SetBackgroundColour("#999999")
            self.modifyIndicator(group, bitPos, self.OFF)

    def ToggleIND4(self, e):
        obj = e.GetEventObject()
        x = self.ind4.index(obj)
        shiftX = x + 12
        isPressed = obj.GetValue()
        group = int(shiftX / 8) + 12
        bitPos = self.getBitPos(shiftX % 8)
        if isPressed:
            self.ind4[x].SetBackgroundColour("#FF0000")
            self.modifyIndicator(group, bitPos, self.ON)
        else:
            self.ind4[x].SetBackgroundColour("#999999")
            self.modifyIndicator(group, bitPos, self.OFF)

    def ToggleIND5(self, e):
        obj = e.GetEventObject()
        x = self.ind5.index(obj)
        shiftX = x + 16
        isPressed = obj.GetValue()
        group = int(shiftX / 8) + 16
        bitPos = self.getBitPos(shiftX % 8)
        if isPressed:
            self.ind5[x].SetBackgroundColour("#FF0000")
            self.modifyIndicator(group, bitPos, self.ON)
        else:
            self.ind5[x].SetBackgroundColour("#999999")
            self.modifyIndicator(group, bitPos, self.OFF)

# ---------------------------------------------------------------------------------------
    #def toggleSettingCOBS(self, event):
    #    sender = event.GetEventObject()
    #    isChecked = sender.GetValue()
    #    if isChecked:
    #        self.useCOBS = True
    #    else:
    #        self.useCOBS = False


# ---------------------------------------------------------------------------------------
    def OnSelectCommPort(self, entry):
        self.previousCommPort = self.commPortID
        self.commPortID = entry.GetString()
        self.commPortValid = True   # stop error blinking
        if (self.previousCommPort == ""):
            # no COM port ever selected yet : initial situation only
            pass
        if (self.previousCommPort == self.commPortID):
            # selection is the same as current selection : no change
            pass
        if (self.previousCommPort != self.commPortID):
            # if previous selected port was opened, it must be closed first
            self.closeCOMMport(self.previousCommPort)
            self.textStatusOpened.Hide()
            self.textStatusClosed.Show()
            self.buttonCommOpen.SetLabel("Open COM port")

    def openCOMMport(self):
        print(">   opening COM port", self.commPortID)
        self.ComPort = serial.Serial(self.commPortID, baudrate=19200, parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
        self.commPortOpened = True
        self.textStatusClosed.Hide()
        self.textStatusOpened.Show()

    def closeCOMMport(self, portIDtoClose):
        if (self.commPortOpened == True):
            print(">   closing COM port", portIDtoClose)
            self.ComPort.close()
            self.textStatusOpened.Hide()
            self.textStatusClosed.Show()
        self.commPortOpened = False

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

# ---------------------------------------------------------------------------------------
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
            self.buttonCommOpen.Show()
            self.textStatusClosed.Show()
            #self.startTimer(300)   # timer no longer needed

    def ExitClick(self, event):
        self.closeCOMMport(self.commPortID)
        print("--- Exit DX11 panel test tool.")
        self.Close()

# ---------------------------------------------------------------------------------------
def main():
    app = wx.App()
    ex = Example(None)
    ex.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()