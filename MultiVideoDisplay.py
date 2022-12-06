import wx
import cv2
import pandas as pd
import yaml
import os
import re

class ImagePanel(wx.Panel):

    def __init__(self, parent, capX = None):
        super().__init__(parent)
        self.count = 0
        self.cap = capX
        self.size = None
        

    def get_frame(self):
        self.size = self.GetSize()
        print(self.size)
        if self.cap is not None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.count)
            self.ret, self.frame = self.cap.read()
            #self.height, self.width = self.frame.shape[:2]
            #self.new_w, self.new_h = self.size[0], int(self.size[0] * self.height/self.width)

            self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        

        height = self.size[0]
        width = self.size[1]
        shape = self.frame.shape[:2]  # shape = [height, width]
        ratio = min(float(height) / shape[1], float(width) / shape[0])
        new_shape = (round(shape[1] * ratio), round(shape[0] * ratio))  # new_shape = [width, height]
        self.frame = cv2.resize(self.frame, new_shape, interpolation=cv2.INTER_AREA)  # resized, no border

        self.bmp = wx.Bitmap.FromBuffer(new_shape[0], new_shape[1], self.frame)
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

    def GoToFrame(self, event, value):
        self.count = value
        self.get_frame()
        self.Refresh()



class MainPanel(wx.Panel):
    def __init__(self, parent, capList):
        super().__init__(parent = parent)
        self.SetBackgroundColour((50,150,150))

        self.capList = capList

        #Widgets and Panels
        if self.capList is not None:

            self.imagePanelList = [ImagePanel(self, self.capList[i]) for i in range(8)]

            
            back = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
            back.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK)

            forward = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
            forward.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD)

            self.slider = wx.Slider(self, id=wx.ID_ANY, value=0, minValue=0, maxValue=int(self.GetParent().video_length-1), size = (400, 35))

            imageSizer1 = wx.GridSizer(3,3,10)
            imageSizer1.Add(self.imagePanelList[0], 5, wx.EXPAND, 2)
            imageSizer1.Add(self.imagePanelList[1], 5, wx.EXPAND, 2)
            imageSizer1.Add(self.imagePanelList[2], 5, wx.EXPAND, 2)
            imageSizer1.Add(self.imagePanelList[3], 5, wx.EXPAND, 2)
            imageSizer1.Add(self.imagePanelList[4], 5, wx.EXPAND, 2)
            imageSizer1.Add(self.imagePanelList[5], 5, wx.EXPAND, 2)
            imageSizer1.Add(self.imagePanelList[6], 5, wx.EXPAND, 2)
            imageSizer1.Add(self.imagePanelList[7], 5, wx.EXPAND, 2)

            #Layout
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(back, 1, wx.EXPAND, 5)
            sizer.Add(self.slider, 8, wx.ALL|wx.EXPAND, 5)
            sizer.Add(forward, 1, wx.EXPAND, 5)

            
            self.mainSizer = wx.BoxSizer(wx.VERTICAL)
            self.mainSizer.Add(imageSizer1, 15, wx.EXPAND, 0)
            self.mainSizer.Add(sizer, 1, wx.EXPAND, 0)
            

            self.SetSizerAndFit(self.mainSizer)

            #Events

            back.Bind(wx.EVT_BUTTON, self.GoBack)
            forward.Bind(wx.EVT_BUTTON, self.GoForward)
            self.slider.Bind(wx.EVT_SCROLL, self.MoveSlider)

    def GoBack(self, event):
        self.image1.PriorFrame(event)
        self.slider.SetValue(self.slider.GetValue()-1)

    def GoForward(self, event):
        self.image1.NextFrame(event)
        self.slider.SetValue(self.slider.GetValue()+1)

    def MoveSlider(self, event):
        value = self.slider.GetValue()
        for i in range(8):
            self.imagePanelList[i].GoToFrame(event, value)





class FileMenu(wx.Menu):
    def __init__(self, parentFrame):
        super().__init__()
        self.parentFrame = parentFrame
        self.OnInit()
    
    def OnInit(self):
        newItem = wx.MenuItem(parentMenu = self, id = wx.ID_NEW, text = "&Open Video\tCTRL+O")
        self.Append(newItem)
        self.Bind(event = wx.EVT_MENU, handler = self.OnNewVideo, source = newItem)

    def OnNewVideo(self, event):
        wildcard = "Videos (*.avi)|*.avi|(*.mp4)|*.mp4"
        dialog = wx.FileDialog(self.parentFrame, "Open Video", wildcard,
                                style = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return None
        
        path = dialog.GetPath()

        capList = []
        if os.path.exists(path):
            for i, camera in enumerate([1,2,3,4,6,7,8,9]):
                capList.append(cv2.VideoCapture(path.replace("cam1", "cam"+str(camera))))
                capList[i].set(3,400)
                capList[i].set(4,300)
            

        self.parentFrame.OnInit(capList)
        self.parentFrame.Layout()
        self.parentFrame.Refresh()


class MainFrame(wx.Frame):

    def __init__(self, parent, capList):
        super().__init__(parent= None, title='Review Video', size = (850, 650))
        self.max_id = 0
        self.OnInit(capList)


    def OnInit(self, capList):
        self.capList = capList
        self.get_video_length()

        self.panelOne = MainPanel(self, capList)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panelOne, 5, wx.EXPAND)
        
        self.SetSizer(self.sizer)
        
        menuBar = wx.MenuBar()
        fileMenu = FileMenu(parentFrame=self)
        menuBar.Append(fileMenu, '&File')
        self.SetMenuBar(menuBar)


    def get_video_length(self):
        if self.capList is not None:
            self.video_length = 1
            for i in range(8):
                if self.capList[i].get(cv2.CAP_PROP_FRAME_COUNT) > self.video_length:
                    self.video_length = self.capList[i].get(cv2.CAP_PROP_FRAME_COUNT)
        else:
            self.video_length = 20



class myApp(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        self.InitFrame()
    
    def InitFrame(self):
        capList = None 
        frame = MainFrame(parent = None, capList = capList)
        frame.Show()


if __name__ == '__main__':
    app = myApp()
    app.MainLoop()