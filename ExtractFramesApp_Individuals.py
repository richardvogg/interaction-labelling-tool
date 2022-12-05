import wx
import cv2
import os
import sys


class ImagePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.count = 0
        
        self.get_frame()

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)

            
    def get_frame(self):
        if self.GetParent().GetParent().cap is not None:
            self.GetParent().GetParent().cap.set(cv2.CAP_PROP_POS_FRAMES, self.count)
            self.ret, self.frame = self.GetParent().GetParent().cap.read()
            self.height, self.width = self.frame.shape[:2]
            self.new_w, self.new_h = 800, int(800 * self.height/self.width)

            self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        self.get_frame()
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        height = 500
        width = 800
        shape = self.frame.shape[:2]  # shape = [height, width]
        ratio = min(float(height) / shape[0], float(width) / shape[1])
        new_shape = (round(shape[1] * ratio), round(shape[0] * ratio))  # new_shape = [width, height]
        frame = cv2.resize(frame, new_shape, interpolation=cv2.INTER_AREA)  # resized, no border

        self.bmp = wx.Bitmap.FromBuffer(new_shape[0], new_shape[1], frame)
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def PriorFrame(self, event):
        if self.count > 0:
            self.count = self.count - 1
        self.get_frame()
        self.Refresh()

    def NextFrame(self, event):
        if self.count < self.GetParent().GetParent().video_length - 1:
            self.count = self.count + 1
        self.get_frame()
        self.Refresh()

    def OnKeyPress(self, event):
        keycode = event.GetKeyCode()
        speed = int(self.GetParent().speed.GetString(self.GetParent().speed.GetSelection()))
        if keycode == 316 and self.count < self.GetParent().GetParent().video_length - 1 - speed:
            self.GetParent().slider.SetValue(self.GetParent().slider.GetValue() + speed)
            self.count = self.count + speed
            self.get_frame()
            self.Refresh()
        elif keycode == 314 and self.count > speed:
            self.GetParent().slider.SetValue(self.GetParent().slider.GetValue() - speed)
            self.count = self.count - speed
            self.get_frame()
            self.Refresh()


    def GoToFrame(self, event, value):
        self.count = value
        self.get_frame()
        self.Refresh()



class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent = parent)
        self.SetBackgroundColour((50,0,50))

        #Widgets and Panels
        self.image = ImagePanel(self)

        self.speed = wx.Choice(self, id=wx.ID_ANY, choices = ["1", "2", "5", "10", "50", "100", "200"])
        #self.img_count_start = wx.TextCtrl(self, value = "0", size = (40,40))
        #self.count_start = wx.Button(self, style = wx.BU_EXACTFIT, label = "OK")

        back = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        back.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK)

        forward = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        forward.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD)

        self.slider = wx.Slider(self, id=wx.ID_ANY, value=0, minValue=0, maxValue=int(self.GetParent().video_length-1), size = (800, 25))

        selectEasyButton = wx.Button(self, style = wx.BU_EXACTFIT, label = "Easy Snapshot", size = (75, 55))
        selectHardButton = wx.Button(self, style = wx.BU_EXACTFIT, label = "Hard Snapshot", size = (75, 55))
        #selectButton2 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Select2", size = (75, 55))


        selectButton1 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Latalata", size = (75, 25))
        selectButton2 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Haruku", size = (75, 25))
        selectButton3 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Isabella", size = (75, 25))
        selectButton4 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Ambon", size = (75, 25))
        selectButton5 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Saparua", size = (75, 25))
        selectButton6 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Kai", size = (75, 25))
        selectButton7 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Dammai", size = (75, 25))
        selectButton8 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Bacan", size = (75, 25))
        selectButton9 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Cambodia", size = (75, 25))
        selectButton10 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Beirut", size = (75, 25))
        selectButton11 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Palestina", size = (75, 25))
        selectButton12 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Amman", size = (75, 25))
        selectButton13 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Malediva", size = (75, 25))
        selectButton14 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Taji", size = (75, 25))
        selectButton15 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Myanmar", size = (75, 25))
        selectButton16 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Agypten", size = (75, 25))
        selectButton17 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Chennai", size = (75, 25))
        selectButton18 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Rabuma", size = (75, 25))
        selectButton19 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Guluwuru", size = (75, 25))
        selectButton20 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Croker", size = (75, 25))
        selectButton21 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Inglis", size = (75, 25))
        selectButton22 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Pinos", size = (75, 25))
        selectButton23 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Floreana", size = (75, 25))
        selectButton24 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Rabita", size = (75, 25))
        selectButton25 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Genovesa", size = (75, 25))
        selectButton26 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Redonda", size = (75, 25))
        selectButton27 = wx.Button(self, style = wx.BU_EXACTFIT, label = "George", size = (75, 25))
        selectButton28 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Hermanos", size = (75, 25))
        selectButton29 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Chatam", size = (75, 25))
        selectButton30 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Darwin", size = (75, 25))
        selectButton31 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Ushakov", size = (75, 25))
        selectButton32 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Yaya", size = (75, 25))
        selectButton33 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Novaya", size = (75, 25))
        selectButton34 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Ata", size = (75, 25))
        selectButton35 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Sakhalin", size = (75, 25))
        selectButton36 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Tiwi", size = (75, 25))

        #Layout
        


        Bsizer = wx.BoxSizer(wx.VERTICAL)
        Bsizer.Add(selectButton1, 0, wx.ALL, 2)
        Bsizer.Add(selectButton2, 0, wx.ALL, 2)
        Bsizer.Add(selectButton3, 0, wx.ALL, 2)
        Bsizer.Add(selectButton4, 0, wx.ALL, 2)
        Bsizer.Add(selectButton5, 0, wx.ALL, 2)
        Bsizer.Add(selectButton6, 0, wx.ALL, 2)
        Bsizer.Add(selectButton7, 0, wx.ALL, 2)
        Bsizer.Add(selectButton8, 0, wx.ALL, 2)

        Jsizer = wx.BoxSizer(wx.VERTICAL)
        Jsizer.Add(selectButton9, 0, wx.ALL, 2)
        Jsizer.Add(selectButton10, 0, wx.ALL, 2)
        Jsizer.Add(selectButton11, 0, wx.ALL, 2)
        Jsizer.Add(selectButton12, 0, wx.ALL, 2)
        Jsizer.Add(selectButton13, 0, wx.ALL, 2)
        Jsizer.Add(selectButton14, 0, wx.ALL, 2)
        Jsizer.Add(selectButton15, 0, wx.ALL, 2)
        Jsizer.Add(selectButton16, 0, wx.ALL, 2)
        Jsizer.Add(selectButton17, 0, wx.ALL, 2)

        Ssizer = wx.BoxSizer(wx.VERTICAL)
        Ssizer.Add(selectButton18, 0, wx.ALL, 2)
        Ssizer.Add(selectButton19, 0, wx.ALL, 2)
        Ssizer.Add(selectButton20, 0, wx.ALL, 2)
        Ssizer.Add(selectButton21, 0, wx.ALL, 2)
        Ssizer.Add(selectButton22, 0, wx.ALL, 2)

        Asizer = wx.BoxSizer(wx.VERTICAL)
        Asizer.Add(selectButton23, 0, wx.ALL, 2)
        Asizer.Add(selectButton24, 0, wx.ALL, 2)
        Asizer.Add(selectButton25, 0, wx.ALL, 2)
        Asizer.Add(selectButton26, 0, wx.ALL, 2)
        Asizer.Add(selectButton27, 0, wx.ALL, 2)
        Asizer.Add(selectButton28, 0, wx.ALL, 2)
        Asizer.Add(selectButton29, 0, wx.ALL, 2)
        Asizer.Add(selectButton30, 0, wx.ALL, 2)

        Rsizer = wx.BoxSizer(wx.VERTICAL)
        Rsizer.Add(selectButton31, 0, wx.ALL, 2)
        Rsizer.Add(selectButton32, 0, wx.ALL, 2)
        Rsizer.Add(selectButton33, 0, wx.ALL, 2)
        Rsizer.Add(selectButton34, 0, wx.ALL, 2)
        Rsizer.Add(selectButton35, 0, wx.ALL, 2)
        Rsizer.Add(selectButton36, 0, wx.ALL, 2)


        sizer = wx.BoxSizer(wx.HORIZONTAL)
        #sizer.Add(self.img_count_start, 0, wx.ALL, 5)
        #sizer.Add(self.count_start, 0, wx.ALL, 5)
        sizer.Add(self.speed, 0, wx.ALL, 5)
        sizer.Add(back, 0, wx.ALL, 5)
        sizer.Add(self.slider, 1, wx.ALL, 5)
        sizer.Add(forward, 0, wx.ALL, 5)
        sizer.Add(selectEasyButton, 0, wx.ALL, 5)
        sizer.Add(selectHardButton, 0, wx.ALL, 5)
        

        imageSizer = wx.BoxSizer(wx.HORIZONTAL)
        imageSizer.Add(self.image, 10, wx.ALL | wx.EXPAND)
        imageSizer.Add(Bsizer, 1, wx.EXPAND, 0)
        imageSizer.Add(Jsizer, 1, wx.EXPAND, 0)
        imageSizer.Add(Ssizer, 1, wx.EXPAND, 0)
        imageSizer.Add(Asizer, 1, wx.EXPAND, 0)
        imageSizer.Add(Rsizer, 1, wx.EXPAND, 0)
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(imageSizer, 5, wx.EXPAND)
        self.mainSizer.Add(sizer, 1)
        

        self.SetSizerAndFit(self.mainSizer)
        #self.img_count = 0

        #Events
        #self.count_start.Bind(wx.EVT_BUTTON, self.SetImgCount)
        back.Bind(wx.EVT_BUTTON, self.GoBack)
        forward.Bind(wx.EVT_BUTTON, self.GoForward)
        self.slider.Bind(wx.EVT_SCROLL, self.MoveSlider)


        selectEasyButton.Bind(wx.EVT_BUTTON, self.ClickSelectEasy)
        selectHardButton.Bind(wx.EVT_BUTTON, self.ClickSelectHard)
        
        selectButton1.Bind(wx.EVT_BUTTON, self.ClickSelect1)
        selectButton2.Bind(wx.EVT_BUTTON, self.ClickSelect2)
        selectButton3.Bind(wx.EVT_BUTTON, self.ClickSelect3)
        selectButton4.Bind(wx.EVT_BUTTON, self.ClickSelect4)
        selectButton5.Bind(wx.EVT_BUTTON, self.ClickSelect5)
        selectButton6.Bind(wx.EVT_BUTTON, self.ClickSelect6)
        selectButton7.Bind(wx.EVT_BUTTON, self.ClickSelect7)
        selectButton8.Bind(wx.EVT_BUTTON, self.ClickSelect8)
        selectButton9.Bind(wx.EVT_BUTTON, self.ClickSelect9)
        selectButton10.Bind(wx.EVT_BUTTON, self.ClickSelect10)
        selectButton11.Bind(wx.EVT_BUTTON, self.ClickSelect11)
        selectButton12.Bind(wx.EVT_BUTTON, self.ClickSelect12)
        selectButton13.Bind(wx.EVT_BUTTON, self.ClickSelect13)
        selectButton14.Bind(wx.EVT_BUTTON, self.ClickSelect14)
        selectButton15.Bind(wx.EVT_BUTTON, self.ClickSelect15)
        selectButton16.Bind(wx.EVT_BUTTON, self.ClickSelect16)
        selectButton17.Bind(wx.EVT_BUTTON, self.ClickSelect17)
        selectButton18.Bind(wx.EVT_BUTTON, self.ClickSelect18)
        selectButton19.Bind(wx.EVT_BUTTON, self.ClickSelect19)
        selectButton20.Bind(wx.EVT_BUTTON, self.ClickSelect20)
        selectButton21.Bind(wx.EVT_BUTTON, self.ClickSelect21)
        selectButton22.Bind(wx.EVT_BUTTON, self.ClickSelect22)
        selectButton23.Bind(wx.EVT_BUTTON, self.ClickSelect23)
        selectButton24.Bind(wx.EVT_BUTTON, self.ClickSelect24)
        selectButton25.Bind(wx.EVT_BUTTON, self.ClickSelect25)
        selectButton26.Bind(wx.EVT_BUTTON, self.ClickSelect26)
        selectButton27.Bind(wx.EVT_BUTTON, self.ClickSelect27)
        selectButton28.Bind(wx.EVT_BUTTON, self.ClickSelect28)
        selectButton29.Bind(wx.EVT_BUTTON, self.ClickSelect29)
        selectButton30.Bind(wx.EVT_BUTTON, self.ClickSelect30)
        selectButton31.Bind(wx.EVT_BUTTON, self.ClickSelect31)
        selectButton32.Bind(wx.EVT_BUTTON, self.ClickSelect32)
        selectButton33.Bind(wx.EVT_BUTTON, self.ClickSelect33)
        selectButton34.Bind(wx.EVT_BUTTON, self.ClickSelect34)
        selectButton35.Bind(wx.EVT_BUTTON, self.ClickSelect35)
        selectButton36.Bind(wx.EVT_BUTTON, self.ClickSelect36)


    def SetImgCount(self, event):
        self.GetParent().img_count = int(self.img_count_start.GetValue())

    def GoBack(self, event):
        self.image.PriorFrame(event)
        self.slider.SetValue(self.slider.GetValue()-1)

    def GoForward(self, event):
        self.image.NextFrame(event)
        self.slider.SetValue(self.slider.GetValue()+1)

    def MoveSlider(self, event):
        value = self.slider.GetValue()
        self.image.GoToFrame(event, value)

    def ClickSelectEasy(self, event):
        cv2.imwrite(self.GetParent().output_path + "../Training_images_easy/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelectHard(self, event):
        cv2.imwrite(self.GetParent().output_path + "../Training_images_hard/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)


    def ClickSelect1(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupB/BFLat/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)
        
    def ClickSelect2(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupB/BMHar/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect3(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupB/BFIsa/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect4(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupB/BMAmb/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect5(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupB/BFSap/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect6(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupB/BMKai/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect7(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupB/BMDam/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect8(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupB/BMBac/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect9(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupJ/JFCam/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect10(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupJ/JFBei/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect11(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupJ/JFPal/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect12(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupJ/JMAmm/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect13(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupJ/JFMal/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect14(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupJ/JMTaj/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect15(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupJ/JMMya/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect16(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupJ/JMAgy/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect17(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupJ/JMChe/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)


    def ClickSelect18(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupS/SFRab/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect19(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupS/SMGul/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect20(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupS/SMCro/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect21(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupS/SMIng/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect22(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupS/SMPin/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect23(self, event):
        cv2.imwrite(self.GetParent().output_path + "Groupa/aFFlo/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect24(self, event):
        cv2.imwrite(self.GetParent().output_path + "Groupa/aFRab/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect25(self, event):
        cv2.imwrite(self.GetParent().output_path + "Groupa/aFGen/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect26(self, event):
        cv2.imwrite(self.GetParent().output_path + "Groupa/aFRed/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect27(self, event):
        cv2.imwrite(self.GetParent().output_path + "Groupa/aMGeo/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect28(self, event):
        cv2.imwrite(self.GetParent().output_path + "Groupa/aMHer/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect29(self, event):
        cv2.imwrite(self.GetParent().output_path + "Groupa/aMCha/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect30(self, event):
        cv2.imwrite(self.GetParent().output_path + "Groupa/aMDar/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect31(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupR/RMUsh/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect32(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupR/RFYay/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect33(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupR/RFNov/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect34(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupR/RFAta/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect35(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupR/RMSak/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    def ClickSelect36(self, event):
        cv2.imwrite(self.GetParent().output_path + "GroupR/RMTiw/" + "%s.jpg" % str(self.GetParent().filename[:-4] + "_" + str(self.image.count)), self.image.frame)

    

class FileMenu(wx.Menu):
    def __init__(self, parentFrame):
        super().__init__()
        self.parentFrame = parentFrame
        self.OnInit()

    
    def OnInit(self):
        newItem = wx.MenuItem(parentMenu = self, id = wx.ID_NEW, text = "&Open\tCTRL+O")
        self.Append(newItem)
        self.Bind(event = wx.EVT_MENU, handler = self.OnNewVideo, source = newItem)

        quitItem = wx.MenuItem(parentMenu = self, id = wx.ID_EXIT, text = "&Quit")
        self.Append(quitItem)
        self.Bind(event = wx.EVT_MENU, handler = self.OnQuit, source = quitItem)

    def OnNewVideo(self, event):
        wildcard = "Videos (*.avi)|*.avi|(*.mp4)|*.mp4"
        dialog = wx.FileDialog(self.parentFrame, "Open Video", wildcard,
                                style = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return None
        
        path = dialog.GetPath()
        elems = path.split("/")


        if os.path.exists(path):
            cap = cv2.VideoCapture(path)

        self.parentFrame.OnInit(cap, filename = elems[-1])
        self.parentFrame.Layout()
        self.parentFrame.Refresh()


    def OnQuit(self, event):
        self.parentFrame.Close()



class MainFrame(wx.Frame):

    def __init__(self, parent, cap, filename):
        super().__init__(parent= None, title='Review Video', size = (850, 550))
        self.max_id = 0
        self.output_path = "/Users/bryndan/Documents/Videoanalysis/Lemurs/Individual_images/"
        self.img_count = 0
        self.cap = cap
        self.OnInit(cap, filename)
        

    def OnInit(self, cap, filename):
        self.filename = filename
        self.cap = cap
        self.get_video_length()

        self.panelOne = MainPanel(self)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panelOne, 5, wx.EXPAND)
        
        self.SetSizer(self.sizer)
        
        menuBar = wx.MenuBar()
        fileMenu = FileMenu(parentFrame=self)
        menuBar.Append(fileMenu, '&File')
        self.SetMenuBar(menuBar)


    def get_video_length(self):
        if self.cap is not None:
            self.video_length = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        else:
            self.video_length = 20



class myApp(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        self.InitFrame()
    
    def InitFrame(self):
        cap = None 
        lines = []
        frame = MainFrame(parent = None, cap = cap, filename = "")
        frame.Show()


if __name__ == '__main__':
    app = myApp()
    app.MainLoop()
