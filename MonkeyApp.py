import wx
import wx.lib.scrolledpanel as sp
import cv2
import yaml
import os
import sys



#sys.path.insert(0, "/Users/vogg/miniconda3/envs/labelling/lib/python3.8/site-packages")




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
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        
        #Draw Rectangles
        frames = [int(item.split(",")[0]) for item in self.Parent.Parent.lines[-1]]
        indices = [i for i, x in enumerate(frames) if x == (self.count +1)]
        dets = [self.Parent.Parent.lines[-1][i] for i in indices]
        
        width_factor = self.width/1920
        print(width_factor)
        height_factor = self.height/1080

        for det in dets:
            dt = det.split(",")



            i = float(dt[1])
            c1 = float(dt[2]) #* width_factor
            c2 = float(dt[3]) #* height_factor
            c3 = float(dt[4]) #* width_factor
            c4 = float(dt[5]) #* height_factor

            color = (i * 100 % 255, i * 75 % 255, i * 50 % 255)


            
            if self.GetParent().multi.GetString(self.GetParent().multi.GetSelection()) == "Yes":
                label = dt[7] + "-" + dt[1]
            else:
                label = dt[1]

            
            cv2.rectangle(self.frame, (int(c1), int(c2)), (int(c1 + c3), int(c2 + c4)), color, int(4 * width_factor))
            if self.GetParent().multi.GetString(self.GetParent().lblbg.GetSelection()) == "Yes":
                cv2.rectangle(self.frame, (int(c1),int(c2 + int(30 * height_factor))), (int(c1 + int(50 * width_factor)),int(c2)), (0,0,0), cv2.FILLED)
            cv2.putText(self.frame, label, (int(c1 + int(5 * width_factor)),int(c2 + int(25 * height_factor))), cv2.FONT_HERSHEY_PLAIN, 2 * width_factor, (255,255,0), 2)

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

    def OnKeyPress(self, event):
        self.GetParent().OnKeyPress(event)
    



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

        self.slider = wx.Slider(self, id=wx.ID_ANY, value=0, minValue=0, maxValue=int(self.GetParent().video_length-1), size = (400, 35))

        addButton = wx.Button(self, style = wx.BU_EXACTFIT, label = "Add", size = (45, 35))

        undo = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        undo.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_UNDO)

        descr = wx.StaticText(self, -1, "Playback speed")
        self.speed = wx.Choice(self, id=wx.ID_ANY, choices = ["1", "2", "5", "10"])
        self.speed.SetSelection(3)

        multi = wx.StaticText(self, -1, "Multicls?")
        self.multi = wx.Choice(self, id=wx.ID_ANY, choices = ["Yes", "No"])
        self.multi.SetSelection(0)

        lblbg = wx.StaticText(self, -1, "LabelBG?")
        self.lblbg = wx.Choice(self, id=wx.ID_ANY, choices = ["Yes", "No"])
        self.lblbg.SetSelection(0)


        #By default save files for tracking, interactions and log
        saving = wx.StaticText(self, id = wx.ID_ANY, label = "Save: ")
        self.track =  wx.CheckBox(self, label = "Tracking")
        self.track.SetValue(True)
        self.inter =  wx.CheckBox(self, label = "Interaction")
        self.inter.SetValue(True)
        #self.log =  wx.CheckBox(self, label = "Log")
        #self.log.SetValue(True)

        self.find = wx.TextCtrl(self, size = (80,25), value = "Find")
        self.replace = wx.TextCtrl(self, size = (80, 25), value = "Replace")
        self.current =  wx.CheckBox(self, label = "After current?")
        replButton = wx.Button(self, style = wx.BU_EXACTFIT, label = "OK", size = (45, 35))
        

        #Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(back, 0, wx.ALL, 5)
        sizer.Add(self.slider, 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(forward, 0, wx.ALL, 5)
        sizer.Add(addButton, 0, wx.ALL, 5)
        sizer.Add(undo, 0, wx.ALL, 5)
        sizer.Add(descr)
        sizer.Add(self.speed, 0, wx.ALL, 5)
        sizer.Add(multi)
        sizer.Add(self.multi, 0, wx.ALL, 5)
        sizer.Add(lblbg)
        sizer.Add(self.lblbg, 0, wx.ALL, 5)
        

        track_sizer = wx.BoxSizer(wx.HORIZONTAL)
        track_sizer.Add(self.find, 0, wx.ALL|wx.EXPAND, 5)
        track_sizer.Add(self.replace, 0, wx.ALL|wx.EXPAND, 5)
        track_sizer.Add(self.current, 0, wx.ALL, 5)
        track_sizer.Add(replButton, 0, wx.ALL, 5)
        track_sizer.Add(saving, 0, wx.ALL, 5)
        track_sizer.Add(self.track, 0, wx.ALL, 5)
        track_sizer.Add(self.inter, 0, wx.ALL, 5)
        #track_sizer.Add(self.log, 0, wx.ALL, 5)


        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.image, 1, wx.EXPAND, 0)
        self.mainSizer.Add(sizer, 0)
        self.mainSizer.Add(track_sizer, 0)
        

        self.SetSizerAndFit(self.mainSizer)

        #Events

        back.Bind(wx.EVT_BUTTON, self.GoBack)
        forward.Bind(wx.EVT_BUTTON, self.GoForward)
        self.slider.Bind(wx.EVT_SCROLL, self.MoveSlider)
        replButton.Bind(wx.EVT_BUTTON, self.ClickOK)
        addButton.Bind(wx.EVT_BUTTON, self.AddAction)
        undo.Bind(wx.EVT_BUTTON, self.UndoAction)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)



    def GoBack(self, event):
        self.image.PriorFrame(event)
        self.slider.SetValue(self.slider.GetValue()-1)

    def GoForward(self, event):
        self.image.NextFrame(event)
        self.slider.SetValue(self.slider.GetValue()+1)

    def MoveSlider(self, event):
        value = self.slider.GetValue()
        self.image.GoToFrame(event, value)


    def OnKeyPress(self, event):
        keycode = event.GetKeyCode()
        speed = int(self.speed.GetString(self.speed.GetSelection()))
        if keycode == 316 and self.slider.GetValue() < self.GetParent().video_length - 1 - speed:
            
            self.slider.SetValue(self.slider.GetValue() + speed)
            self.image.count += speed
            self.image.get_frame()
            
            self.image.Refresh()
            self.Refresh()
        elif keycode == 314 and self.slider.GetValue() > speed:
            
            self.slider.SetValue(self.slider.GetValue() - speed)
            self.image.count -= speed
            self.image.get_frame()
            self.image.Refresh()
            self.Refresh()

    def ClickOK(self, event):

        if self.current.GetValue() == True:
            after_frame = self.slider.GetValue()
        else:
            after_frame = 0

        lns = self.GetParent().lines[-1].copy()
        lns2 = lns.copy()

        print(len(lns))
        current_max = self.Parent.get_max_id()
        for i, line in enumerate(lns2):
            fields = line.split(",")

            if int(fields[0]) >= after_frame:
                if str(fields[1]) == str(self.find.GetValue()):
                    
                    if self.replace.GetValue() == "-":
                        lns[i] = "remove"
                    elif self.replace.GetValue() == "?":
                        
                        fields[1] = str(current_max + 1)
                        lns[i] = ",".join(fields)
                        self.GetParent().max_id += 1
                    else:
                        fields[1] = self.replace.GetValue()
                        lns[i] = ",".join(fields)
        
        lns = [x for x in lns if x!="remove"]
        self.GetParent().lines.append(lns)
        self.GetParent().loglist.append(" ".join(["replace", self.find.GetValue(), 
                                                    self.replace.GetValue(), str(after_frame)+"\n"]))

        self.GetParent().Refresh()
        for elem in self.GetParent().loglist:
            print(elem)

    def AddAction(self, event):
        self.GetParent().panelTwo.AddLine()

    def UndoAction(self, event):

        #get last element from loglist
        action = self.GetParent().loglist[-1]
        action_items = action.split(" ")

        #if we undo a "replace" statement
        if action_items[0] == "replace":
            self.Parent.lines.pop()
            self.Parent.loglist.pop()


        #if we undo a "groom" or "fight" statement 

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
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)


    def OnPaint(self, evt):
        dc1 = wx.PaintDC(self)
        with open("config.yml", "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        for rect in self.permRect:
            for i, key in enumerate(cfg["keys"]):
                if rect[0] == cfg["keys"][key]:
                    dc1.SetBrush(wx.Brush(wx.Colour(i*10 % 255, i * 100 % 255, i * 200 % 255)))
                dc1.DrawRectangle(rect[1])
                
        if self.dot:
            for i, key in enumerate(cfg["keys"]):
                if self.dot[0] == cfg["keys"][key]:
                    dc1.SetBrush(wx.Brush(wx.Colour(i*10 % 255, i * 100 % 255, i * 200 % 255)))
            dc1.DrawCircle(self.dot[1],5)

    def OnKeyPress(self,event):
        keycode = event.GetKeyCode()

        with open("config.yml", "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        
        keylist = []

        for key in cfg["keys"]:
            keylist.append(int(ord(key.upper())))
            if keycode == int(ord(key.upper())):
                action = cfg["keys"][key]

        #ascii keys: https://theasciicode.com.ar
        #if keycode == 70:
        #    action = "fight"
        #elif keycode == 71:
        #    action = "groom"
        #elif keycode == 76:
        #    action = "looking_at"

        if keycode in keylist: 
            if self.dot is None:
                val = self.Parent.Parent.Parent.panelOne.slider.GetValue()
                self.selectionStart = val
                self.selectionStartCalc = int(400/self.GetParent().GetParent().GetParent().video_length * val)
                self.dot = [action,wx.Point(self.selectionStartCalc, 5)]
            else:
                val = self.Parent.Parent.Parent.panelOne.slider.GetValue()
                valCalc = int(400/self.GetParent().GetParent().GetParent().video_length * val)
                self.permRect.append([action, wx.Rect((self.selectionStartCalc, 0), 
                                (valCalc - self.selectionStartCalc,20))])
                vmin = min(self.selectionStart, val)
                vmax = max(self.selectionStart, val)
                self.Parent.Parent.Parent.loglist.append(" ".join([action, str(vmin), str(vmax), self.Parent.who.GetValue(), self.Parent.to.GetValue(), str(self.Parent.id)+"\n"]))
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
        newItem = wx.MenuItem(parentMenu = self, id = wx.ID_NEW, text = "&Open\tCTRL+O")
        self.Append(newItem)
        self.Bind(event = wx.EVT_MENU, handler = self.OnNewVideo, source = newItem)

        openItem = wx.MenuItem(parentMenu = self, id = wx.ID_OPEN, text = "&Open Detections")
        self.Append(openItem)
        self.Bind(event = wx.EVT_MENU, handler = self.OnOpen, source = openItem)

        save2Item = wx.MenuItem(parentMenu = self, id = wx.ID_SAVE, text = "&Save\tCTRL+S")
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
            try:
                with open(path_labels) as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []
                print("No files found")
            
        

        self.parentFrame.OnInit(cap, lines, filename = elems[-2])
        self.parentFrame.panelTwo.OnInit()
        self.parentFrame.Layout()
        self.parentFrame.Refresh()

    def OnOpen(self, event):
        wildcard = "TXT files (*.txt)|*.txt"
        dialog = wx.FileDialog(self.parentFrame, "Open Text Files", wildcard,
                                style = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return None

        path = dialog.GetPath()

        if os.path.exists(path):
            with open(path) as f:
                lines = f.readlines()
        
        self.parentFrame.OnInit(self.parentFrame.cap, lines, filename = self.parentFrame.filename)
        self.parentFrame.panelTwo.OnInit()
        self.parentFrame.Layout()
        self.parentFrame.Refresh()
    
        

    def OnSave2(self,event):

        dialog = wx.FileDialog(self.parentFrame, "Save the labels", defaultFile = self.parentFrame.filename+".txt",
                                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return None

        path = dialog.GetPath()
        print(path)
        logs = self.parentFrame.loglist
        elems = path.split("/")

        if self.parentFrame.panelOne.track.GetValue():


            elems1 = elems.copy()
            elems1.insert(-1, "tracking_updated")
            path_tracking = "/".join(elems1)
            data = self.parentFrame.lines[-1]


            with open(path_tracking, "w+") as myfile:
                for line in data:
                    myfile.write(line)

            # if tracking is updated then we also want to save the log
        #if self.parentFrame.panelOne.log.GetValue():
            elems2 = elems.copy()
            elems2.insert(-1, "log")
            path_log = "/".join(elems2)

            with open(path_log, "w+") as myfile:
                for line in logs:
                    myfile.write(line)


        if self.parentFrame.panelOne.inter.GetValue():

            elems3 = elems.copy()
            elems3.insert(-1, "interactions")
            path_inter = "/".join(elems3)
            with open(path_inter, "w+") as myfile:
                for line in logs[1:]:
                    fields = line.split(" ")
                    if fields[0] != "replace":
                        for i in range(int(fields[1]),(int(fields[2])+1)):
                            myfile.write(" ".join([str(i), fields[3], fields[4], fields[0]]) + "\n")
        


    def OnQuit(self, event):
        self.parentFrame.Close()



class MainFrame(wx.Frame):

    def __init__(self, parent, cap, lines, filename):
        super().__init__(parent= None, title='Review Video', size = (850, 650))
        self.lines = []
        self.max_id = 0
        self.OnInit(cap, lines, filename)
        

    def OnInit(self, cap, lines, filename):
        self.filename = filename
        self.cap = cap
        self.get_video_length()
        
        self.lines.append(lines) #Labels
        self.get_max_id()
        self.loglist = ["Loglist\n--------\n"]


        self.panelOne = MainPanel(self)
        self.panelTwo = MarkerFlexPanel(self)
        self.panelTwo.OnInit()


        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panelOne, 5, wx.EXPAND)
        self.sizer.Add(self.panelTwo, 2, wx.EXPAND)
        
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

    def get_max_id(self):
        self.max_id = 0
        if len(self.lines) > 0:
            for line in self.lines[-1]:
                fields = line.split(",")
                if int(fields[1]) > self.max_id:
                    self.max_id = int(fields[1])
        return(self.max_id)



class myApp(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        self.InitFrame()
    
    def InitFrame(self):
        cap = None 
        lines = []
        frame = MainFrame(parent = None, cap = cap, lines = lines, filename = "")
        frame.Show()


if __name__ == '__main__':
    app = myApp()
    app.MainLoop()
