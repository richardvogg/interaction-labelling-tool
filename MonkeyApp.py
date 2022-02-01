import wx
import wx.lib.scrolledpanel as sp
import cv2
import os
import sys



sys.path.insert(0, "/Users/vogg/miniconda3/envs/opencv/lib/python3.8/site-packages")

'''
with open('/Users/vogg/Documents/Python/learning-opencv/data/results.txt') as f:
    lines = f.readlines()
'''



class ImagePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        self.count = 0
        self.get_frame()

    def get_frame(self):
        if self.GetParent().GetParent().cap is not None:
            self.GetParent().GetParent().cap.set(cv2.CAP_PROP_POS_FRAMES, self.count)
            ret, self.frame = self.GetParent().GetParent().cap.read()
            self.height, self.width = self.frame.shape[:2]
            self.new_w, self.new_h = 800, int(800 * self.height/self.width)

            self.Bind(wx.EVT_PAINT, self.OnPaint)

    def letterbox(img, height=608, width=1088):  # resize a rectangular image to a padded rectangular
        shape = img.shape[:2]  # shape = [height, width]
        ratio = min(float(height) / shape[0], float(width) / shape[1])
        new_shape = (round(shape[1] * ratio), round(shape[0] * ratio))  # new_shape = [width, height]
        dw = (width - new_shape[0]) / 2  # width padding
        dh = (height - new_shape[1]) / 2  # height padding
        top, bottom = round(dh - 0.1), round(dh + 0.1)
        left, right = round(dw - 0.1), round(dw + 0.1)
        img = cv2.resize(img, new_shape, interpolation=cv2.INTER_AREA)  # resized, no border
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(100,100,100))  # padded rectangular
        return img

    def OnPaint(self, event):
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        
        #Draw Rectangles
        frames = [int(item.split(",")[0]) for item in self.Parent.Parent.lines]
        indices = [i for i, x in enumerate(frames) if x == (self.count +1)]
        dets = [self.Parent.Parent.lines[i] for i in indices]
        
        for det in dets:
            dt = det.split(",")

            i = float(dt[1])
            c1 = float(dt[2])
            c2 = float(dt[3])
            c3 = float(dt[4])
            c4 = float(dt[5])

            color = (i * 100 % 255, i * 75 % 255, i * 50 % 255)

            cv2.rectangle(self.frame, (int(c1), int(c2)), (int(c1 + c3), int(c2 + c4)), color, 4)
            cv2.rectangle(self.frame, (int(c1),int(c2 + 30)), (int(c1 + 30),int(c2)), (255,255,255), cv2.FILLED)
            cv2.putText(self.frame, dt[1], (int(c1 + 5),int(c2 + 25)), cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,0))

        height = 500
        width = 800
        shape = self.frame.shape[:2]  # shape = [height, width]
        ratio = min(float(height) / shape[0], float(width) / shape[1])
        new_shape = (round(shape[1] * ratio), round(shape[0] * ratio))  # new_shape = [width, height]
        self.frame = cv2.resize(self.frame, new_shape, interpolation=cv2.INTER_AREA)  # resized, no border

        self.bmp = wx.Bitmap.FromBuffer(new_shape[0], new_shape[1], self.frame)
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def PriorFrame(self, event):
        self.count = self.count - 1
        self.GetParent().GetParent().cap.set(cv2.CAP_PROP_POS_FRAMES, self.count)
        ret, self.frame = self.GetParent().GetParent().cap.read()
        if ret:
            self.Refresh()
    

    def NextFrame(self, event):
        self.count = self.count + 1
        self.GetParent().GetParent().cap.set(cv2.CAP_PROP_POS_FRAMES, self.count)
        ret, self.frame = self.GetParent().GetParent().cap.read()
        
        if ret:
            self.Refresh()
        print(self.height, self.width)

    def GoToFrame(self, event, value):
        self.count = value
        self.GetParent().GetParent().cap.set(cv2.CAP_PROP_POS_FRAMES, value)
        ret, self.frame = self.GetParent().GetParent().cap.read()
        if ret:
            self.Refresh()



class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent = parent)
        self.SetBackgroundColour((50,0,50))

        #Widgets and Panels
        self.image = ImagePanel(self)
        
        back = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        back.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK)

        forward = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        forward.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD)

        self.slider = wx.Slider(self, id=wx.ID_ANY, value=0, minValue=0, maxValue=self.GetParent().video_length-1, size = (400, 35))

        self.find = wx.TextCtrl(self, size = (80,35), value = "Find")
        self.replace = wx.TextCtrl(self, size = (80, 35), value = "Replace")

        replButton = wx.Button(self, style = wx.BU_EXACTFIT, label = "OK", size = (45, 35))
        addButton = wx.Button(self, style = wx.BU_EXACTFIT, label = "Add", size = (45, 35))

        undo = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        undo.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_UNDO)


        #Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(back, 0, wx.ALL, 5)
        sizer.Add(self.slider, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(forward, 0, wx.ALL, 5)
        sizer.Add(self.find, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(self.replace, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(replButton, 0, wx.ALL, 5)
        sizer.Add(addButton, 0, wx.ALL, 5)
        sizer.Add(undo, 0, wx.ALL, 5)


        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.image, 1, wx.EXPAND, 0)
        self.mainSizer.Add(sizer, 0)     
        

        self.SetSizerAndFit(self.mainSizer)

        #Events
        back.Bind(wx.EVT_BUTTON, self.GoBack)
        forward.Bind(wx.EVT_BUTTON, self.GoForward)
        self.slider.Bind(wx.EVT_SCROLL, self.MoveSlider)
        replButton.Bind(wx.EVT_BUTTON, self.ClickOK)
        addButton.Bind(wx.EVT_BUTTON, self.AddAction)
        undo.Bind(wx.EVT_BUTTON, self.UndoAction)


    def GoBack(self, event):
        self.image.PriorFrame(event)
        self.slider.SetValue(self.slider.GetValue()-1)

    def GoForward(self, event):
        self.image.NextFrame(event)
        self.slider.SetValue(self.slider.GetValue()+1)

    def MoveSlider(self, event):
        value = self.slider.GetValue()
        self.image.GoToFrame(event, value)

    def ClickOK(self, event):
        for i, line in enumerate(self.Parent.lines):
            fields = line.split(",")
            if str(fields[1]) == str(self.find.GetValue()):
                fields[1] = self.replace.GetValue()
            self.Parent.lines[i] = ",".join(fields)
        self.Parent.loglist.append(" ".join(["replace",self.find.GetValue(),self.replace.GetValue()]))
        for elem in self.Parent.loglist:
            print(elem)

    def AddAction(self, event):
        self.GetParent().panelTwo.AddLine()

    def UndoAction(self, event):

        #get last element from loglist
        action = self.GetParent().loglist[-1]
        action_items = action.split(" ")

        #if we undo a "replace" statement, simply replace the values in the original labeling file
        if action_items[0] == "replace":
            for i, line in enumerate(self.Parent.lines):
                fields = line.split(",")
                if str(fields[1]) == action_items[2]:
                    fields[1] = action_items[1]
                self.Parent.lines[i] = ",".join(fields)
            self.Parent.loglist.pop()


        #if we undo a "groom" or "fight" statement we have to find the correct line and then remove the last element

        else:
            children = self.Parent.panelTwo.flexSizer.GetChildren()
            for child in children:
                if str(child.GetWindow().id) == action_items[-1]:
                    child.GetWindow().newPanel.permRect.pop()
                    child.GetWindow().newPanel.Refresh()
                    self.Parent.loglist.pop()


class MarkerPanel(wx.Panel):
    def __init__(self, parent, size = (200,30)):
        super().__init__(parent, size = size)
        self.SetBackgroundColour((0,100,50))
        self.permRect = []
        self.dot = None
        self.selectionStart = None
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        #self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)


    def OnPaint(self, evt):
        dc1 = wx.PaintDC(self)
        for rect in self.permRect:
            if rect[0] == "fight":
                dc1.SetBrush(wx.BLUE_BRUSH)
            else:
                dc1.SetBrush(wx.RED_BRUSH)
            dc1.DrawRectangle(rect[1])
        if self.dot:
            if self.dot[0] == "fight":
                dc1.SetBrush(wx.BLUE_BRUSH)
            else:
                dc1.SetBrush(wx.RED_BRUSH)
            dc1.DrawCircle(self.dot[1],5)
    '''
    def OnLeftDown(self, evt):
        self.CaptureMouse()
        self.selectionStart = evt.Position

    def OnLeftUp(self, evt):
        if not self.HasCapture():
            return
        self.ReleaseMouse()
        if evt.Position[0]-self.selectionStart[0] > 1:
            self.permRect.append(wx.Rect((self.selectionStart[0], 0), 
                                    (evt.Position[0]-self.selectionStart[0],20)))

            print(self.permRect)

        self.selectionStart = None
        self.Refresh()
    '''

    def OnKeyPress(self,event):
        keycode = event.GetKeyCode()

        if keycode == 70:
            action = "fight"
        elif keycode == 71:
            action = "groom"

        if (keycode == 70) | (keycode == 71): #Spacebar
            if self.dot is None:
                val = self.Parent.Parent.Parent.panelOne.slider.GetValue()
                self.selectionStart = (int(400/self.GetParent().GetParent().GetParent().video_length * val),0)
                self.dot = [action,wx.Point(int(400/self.GetParent().GetParent().GetParent().video_length * val), 5)]
            else:
                val = self.Parent.Parent.Parent.panelOne.slider.GetValue()
                self.permRect.append([action,wx.Rect((self.selectionStart[0], 0), 
                                (400/self.GetParent().GetParent().GetParent().video_length * val -self.selectionStart[0],20))])
                vmin = min(self.selectionStart[0], val)
                vmax = max(self.selectionStart[0], val)
                self.Parent.Parent.Parent.loglist.append(" ".join([action, str(vmin), str(vmax), self.Parent.who.GetValue(), self.Parent.to.GetValue(), str(self.Parent.id)]))
                for elem in self.Parent.Parent.Parent.loglist:
                    print(elem)
                
                self.dot = None
                self.selectionStart = None
            self.Refresh()


class MarkerLinePanel(wx.Panel):
    def __init__(self, parent, id):
        super().__init__(parent, id)

        self.id = id

        self.emptyPanel = wx.Panel(self, size = (35, 35))
        self.newPanel = MarkerPanel(self, size = (400, 25))
        self.who = wx.TextCtrl(self, size = (80,35), value = "From")
        self.to = wx.TextCtrl(self, size = (80, 35), value = "To")
        self.both = wx.CheckBox(self, label = "Both")
        
        self.rectSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.rectSizer.Add(self.emptyPanel, 0, wx.ALL, 5)
        self.rectSizer.Add(self.newPanel, 1, wx.ALL|wx.EXPAND, 5)
        self.rectSizer.Add(self.who, 0, wx.ALL, 5)
        self.rectSizer.Add(self.to, 0, wx.ALL, 5)
        self.rectSizer.Add(self.both)

        self.SetSizer(self.rectSizer)


class MarkerFlexPanel(sp.ScrolledPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.OnInit()

    def OnInit(self):
        self.SetBackgroundColour((50,50,50))
        self.SetupScrolling()

        self.countLines = 0

        self.flexSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.flexSizer)
        self.GetParent().Layout()


    def AddLine(self):
        rectSizer = MarkerLinePanel(self, id = self.countLines)

        self.countLines += 1
        self.flexSizer.Add(rectSizer, 0)
        self.GetParent().Layout()



class FileMenu(wx.Menu):
    def __init__(self, parentFrame):
        super().__init__()
        self.parentFrame = parentFrame
        self.OnInit()
        
    
    def OnInit(self):
        newItem = wx.MenuItem(parentMenu = self, id = wx.ID_NEW, text = "&New\tCTRL+N")
        self.Append(newItem)
        self.Bind(event = wx.EVT_MENU, handler = self.OnNewVideo, source = newItem)

        openItem = wx.MenuItem(parentMenu = self, id = wx.ID_OPEN, text = "&Open")
        self.Append(openItem)
        self.Bind(event = wx.EVT_MENU, handler = self.OnOpen, source = openItem)

        save1Item = wx.MenuItem(parentMenu = self, id = wx.ID_SAVE, text = "&Save Detections")
        self.Append(save1Item)
        self.Bind(event = wx.EVT_MENU, handler = self.OnSave, source = save1Item)

        save2Item = wx.MenuItem(parentMenu = self, id = wx.ID_SAVE, text = "&Save Interactions")
        self.Append(save2Item)
        self.Bind(event = wx.EVT_MENU, handler = self.OnSave2, source = save2Item)

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
        elems.insert(-1, "predictions")
        elems.append("results.txt")
        path_labels = "/".join(elems)

        if os.path.exists(path):
            cap = cv2.VideoCapture(path)
            with open(path_labels) as f:
                lines = f.readlines()
        
        self.parentFrame.OnInit(cap, lines)
        self.parentFrame.panelTwo.OnInit()
        self.parentFrame.Layout()

    def OnOpen(self, event):
        wildcard = "TXT files (*.txt)|*.txt"
        dialog = wx.FileDialog(self.parentFrame, "Open Text Files", wildcard,
                                style = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return None

        path = dialog.GetPath()
        if os.path.exists(path):
            with open(path) as f:
                self.parentFrame.lines = f.readlines()
    
    def OnSave(self, event):
        dialog = wx.FileDialog(self.parentFrame, "Save the updated detections", defaultFile = "dets.txt",
                                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return None

        path = dialog.GetPath()
        data = self.parentFrame.lines
        with open(path, "w+") as myfile:
            for line in data:
                myfile.write(line)

    def OnSave2(self,event):
        dialog = wx.FileDialog(self.parentFrame, "Save the interaction labels", defaultFile = "interactions.txt",
                                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return None

        path = dialog.GetPath()
        logs = self.parentFrame.loglist

        with open(path, "w+") as myfile:
            for line in logs[1:]:
                fields = line.split(" ")
                if fields[0] != "replace":
                    for i in range(int(fields[1]),(int(fields[2])+1)):
                        myfile.write(" ".join([str(i), fields[3], fields[4], fields[0]]) + "\n")
        

        

    def OnQuit(self, event):
        self.parentFrame.Close()



class MainFrame(wx.Frame):

    def __init__(self, parent, cap, lines):
        super().__init__(parent= None, title='Review Video', size = (850, 650))
        self.cap = cap #Video
        self.lines = lines
        self.OnInit(self.cap, self.lines)
        

    def OnInit(self, cap, lines):
        self.cap = cap
        self.get_video_length()
        self.lines = lines #Labels
        self.loglist = ["Loglist\n--------"]


        self.panelOne = MainPanel(self)
        self.panelTwo = MarkerFlexPanel(self)
        self.panelTwo.OnInit()


        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panelOne, 2, wx.EXPAND)
        self.sizer.Add(self.panelTwo, 1, wx.EXPAND)
        

        self.SetSizer(self.sizer)
        

        menuBar = wx.MenuBar()
        fileMenu = FileMenu(parentFrame=self)
        menuBar.Append(fileMenu, '&File')
        self.SetMenuBar(menuBar)

    def get_video_length(self):
        if self.cap is not None:
            self.video_length = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        else:
            self.video_length = 0

    


class myApp(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        self.InitFrame()
    
    def InitFrame(self):
        cap = None #cv2.VideoCapture('/Users/vogg/Documents/Python/learning-opencv/data/VID_20210223_123630_0.mp4')
        with open('/Users/vogg/Documents/Python/learning-opencv/data/results.txt') as f:
            lines = f.readlines()

        lines = None
        frame = MainFrame(parent = None, cap = cap, lines = lines)
        frame.Show()


if __name__ == '__main__':
    app = myApp()
    app.MainLoop()
