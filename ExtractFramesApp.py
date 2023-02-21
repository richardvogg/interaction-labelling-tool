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
        height = 600
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
            self.count = self.count + speed
            self.get_frame()
            self.Refresh()
        elif keycode == 314 and self.count > speed:
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

        self.speed = wx.Choice(self, id=wx.ID_ANY, choices = ["1", "2", "5", "10"])
        self.img_count_start = wx.TextCtrl(self, value = "0", size = (40,40))
        self.count_start = wx.Button(self, style = wx.BU_EXACTFIT, label = "OK")

        back = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        back.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK)

        forward = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        forward.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD)

        self.slider = wx.Slider(self, id=wx.ID_ANY, value=0, minValue=0, maxValue=int(self.GetParent().video_length-1), size = (400, 35))

        selectButton = wx.Button(self, style = wx.BU_EXACTFIT, label = "Select", size = (75, 55))
        selectButton2 = wx.Button(self, style = wx.BU_EXACTFIT, label = "Select2", size = (75, 55))

        #Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.img_count_start, 0, wx.ALL, 5)
        sizer.Add(self.count_start, 0, wx.ALL, 5)
        sizer.Add(self.speed, 0, wx.ALL, 5)
        sizer.Add(back, 0, wx.ALL, 5)
        sizer.Add(self.slider, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(forward, 0, wx.ALL, 5)
        sizer.Add(selectButton, 0, wx.ALL, 5)
        sizer.Add(selectButton2, 0, wx.ALL, 5)
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.image, 1, wx.EXPAND, 0)
        self.mainSizer.Add(sizer, 0)
        

        self.SetSizerAndFit(self.mainSizer)
        #self.img_count = 0

        #Events
        self.count_start.Bind(wx.EVT_BUTTON, self.SetImgCount)
        back.Bind(wx.EVT_BUTTON, self.GoBack)
        forward.Bind(wx.EVT_BUTTON, self.GoForward)
        self.slider.Bind(wx.EVT_SCROLL, self.MoveSlider)
        selectButton.Bind(wx.EVT_BUTTON, self.ClickSelect)
        selectButton2.Bind(wx.EVT_BUTTON, self.ClickSelect2)


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

    def ClickSelect(self, event):
        after_frame = self.slider.GetValue()

        #cv2.imwrite(self.GetParent().output_path + "images/" + "img_%s_1.jpg" % str(self.img_count).zfill(5), 
        cv2.imwrite(self.GetParent().output_path + "img_%s_1.jpg" % str(self.GetParent().img_count).zfill(5), 
        self.image.frame)

        self.GetParent().img_count += 1
        

    def ClickSelect2(self, event):
        after_frame = self.slider.GetValue()

        cv2.imwrite(self.GetParent().output_path + "images/" + "img_%s_2.jpg" % str(self.img_count - 1).zfill(5), 
        self.image.frame)




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
        
        self.parentFrame.OnInit(cap, filename = elems[-2])
        self.parentFrame.Layout()
        self.parentFrame.Refresh()


    def OnQuit(self, event):
        self.parentFrame.Close()



class MainFrame(wx.Frame):

    def __init__(self, parent, cap, filename):
        super().__init__(parent= None, title='Review Video', size = (850, 550))
        self.max_id = 0
        self.output_path = "/Users/vogg/Documents/Labeling/ExplorationRoom/Neda/"
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
