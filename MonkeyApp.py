import wx
import wx.lib.scrolledpanel as sp
import cv2
import pandas as pd
import yaml
import os
import re

#sys.path.insert(0, "/Users/vogg/miniconda3/envs/labelling/lib/python3.8/site-packages")


class ImagePanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        self.count = 0
        self.get_frame()
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPress)

        with open("config.yml", "r") as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)

    def get_frame(self):
        if self.GetParent().GetParent().cap is not None:
            self.GetParent().GetParent().cap.set(cv2.CAP_PROP_POS_FRAMES, self.count)
            self.ret, self.frame = self.GetParent().GetParent().cap.read()
            self.height, self.width = self.frame.shape[:2]
            self.new_w, self.new_h = 800, int(800 * self.height/self.width) #######################

            self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        
        #Draw Rectangles
        #frames = [int(item.split(",")[0]) for item in self.Parent.Parent.lines[-1]]
        #indices = [i for i, x in enumerate(frames) if x == (self.count +1)]
        #dets = [self.Parent.Parent.lines[-1][i] for i in indices]
        dets = self.Parent.Parent.line_list[-1][self.Parent.Parent.line_list[-1]["frame"] == (self.count + 1)] 
        width_factor = self.width/1920
        height_factor = self.height/1080
        down_factor = float(self.GetParent().GetParent().downsize_factor)

        if not self.GetParent().hide.GetValue():
            for index, det in dets.iterrows():
                #dt = det.split(",")
                i = float(det['id'])
                c1 = float(det['x'])/ down_factor #* width_factor
                c2 = float(det['y']) / down_factor #* height_factor
                c3 = float(det['w']) / down_factor #* width_factor
                c4 = float(det['h']) / down_factor #* height_factor

                color = (i * 100 % 255, i * 75 % 255, i * 50 % 255)


                
                if self.GetParent().multi.GetString(self.GetParent().multi.GetSelection()) == "Yes":
                    # if the labels are single class but someone selects Multi-Class, then it shows a 0 as class 
                    # to avoid problems with the "-" sign later
                    if det['class'] == "-1":
                        cls = "0"
                    else:
                        cls = str(int(det['class']))
                    label = cls + "-" + str(int(det['id']))
                else:
                    label = str(int(det['id']))

                
                cv2.rectangle(self.frame, (int(c1), int(c2)), (int(c1 + c3), int(c2 + c4)), color, int(4 * width_factor))
                if self.GetParent().multi.GetString(self.GetParent().lblbg.GetSelection()) == "Yes":
                    cv2.rectangle(self.frame, (int(c1),int(c2 + int(30 * height_factor))), (int(c1 + int(70 * width_factor)),int(c2)), (0,0,0), cv2.FILLED)
                cv2.putText(self.frame, label, (int(c1 + int(5 * width_factor)),int(c2 + int(25 * height_factor))), cv2.FONT_HERSHEY_PLAIN, 2 * width_factor, (255,255,0), 2)

        height = self.cfg['size']['height']
        width = self.cfg['size']['width']
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
        self.SetBackgroundColour((50,150,150))

        
        with open("config.yml", "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)

        #Widgets and Panels
        self.image = ImagePanel(self)
        shortcut_string = ""
        for key, value in cfg['keys'].items():
            shortcut_string += key + ": " + value + "\n"

        shortcuts = wx.StaticText(self, -1, shortcut_string, (cfg['size']['width'] + 50, 20)) #Position on the left of the video panel

        
        back = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        back.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK)

        forward = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        forward.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD)

        self.slider = wx.Slider(self, id=wx.ID_ANY, value=0, minValue=0, maxValue=int(self.GetParent().video_length-1), size = (400, 35))

        addButton = wx.Button(self, style = wx.BU_EXACTFIT, label = "Add", size = (45, 35))

        undo = wx.Button(self, style = wx.BU_EXACTFIT, size = (35, 35))
        undo.Bitmap = wx.ArtProvider.GetBitmap(wx.ART_UNDO)

        descr = wx.StaticText(self, -1, "Speed")
        self.speed = wx.Choice(self, id=wx.ID_ANY, choices = ["1", "2", "5", "10", "20", "50", "100", "200", "500", "1000"])
        self.speed.SetSelection(3)

        multi = wx.StaticText(self, -1, "Multicls?")
        self.multi = wx.Choice(self, id=wx.ID_ANY, choices = ["Yes", "No"])

        self.hide = wx.CheckBox(self, label = "Hide Boxes")

        
        if cfg['others']['multi_class']:
            sel = 0
        else:
            sel = 1
        self.multi.SetSelection(sel)

        lblbg = wx.StaticText(self, -1, "LabelBG?")
        self.lblbg = wx.Choice(self, id=wx.ID_ANY, choices = ["Yes", "No"])
        self.lblbg.SetSelection(0)


        #By default save files for tracking, interactions and log
        saving = wx.StaticText(self, id = wx.ID_ANY, label = "Save: ")
        self.track =  wx.CheckBox(self, label = "Tracking")
        self.track.SetValue(True)
        self.inter =  wx.CheckBox(self, label = "Interaction")
        self.inter.SetValue(True)


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
        sizer.Add(self.hide)
        

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
        self.hide.Bind(wx.EVT_CHECKBOX, self.MoveSlider)
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

        lns = self.GetParent().line_list[-1].copy()
        lns2 = lns.copy()

        ## how to adapt to multiclass?
        current_max = self.Parent.get_max_id()

        if "-" in self.find.GetValue():
            find_term = self.find.GetValue().split("-")
            cls = find_term[0]
            id = find_term[1]
        else:
            cls = "-1"
            id = self.find.GetValue()

        if "-" in self.replace.GetValue():
            repl_term = self.replace.GetValue().split("-")
            repl_cls = repl_term[0]
            repl_id = repl_term[1]
        else:
            repl_cls = "-1"
            repl_id = self.replace.GetValue()
                    
        if self.replace.GetValue() == "-":
            lns = lns.drop(lns[(lns['id'] == int(id)) & ((lns['class'] == int(cls)) | (lns['class'] == "-1"))].index)

        elif repl_id == "?":
            lns.loc[(lns['id'] == int(id)) & ((lns['class'] == int(cls)) | (lns['class'] == "-1")), 'id'] = int(current_max + 1)
            self.GetParent().max_id += 1
        else:
            lns.loc[(lns['id'] == int(id)) & ((lns['class'] == int(cls)) | (lns['class'] == "-1")), 'id'] = repl_id
            lns.loc[(lns['id'] == int(id)) & ((lns['class'] == int(cls)) | (lns['class'] == "-1")), 'class'] = repl_cls
        
        #lns = [x for x in lns if x!="remove"]
        self.GetParent().line_list.append(lns)
        self.GetParent().loglist.append(" ".join(["replace", self.find.GetValue(), 
                                                    self.replace.GetValue(), str(after_frame)+"\n"]))

        self.GetParent().Refresh()
        for elem in self.GetParent().loglist:
            print(elem)

        self.Refresh()
        self.image.get_frame()

    def AddAction(self, event):
        self.GetParent().panelTwo.AddLine()

    def UndoAction(self, event):

        #get last element from loglist
        action = self.GetParent().loglist[-1]
        action_items = action.split(" ")

        #if we undo a "replace" statement
        if action_items[0] == "replace":
            self.Parent.line_list.pop()
            self.Parent.loglist.pop()


        #if we undo a "groom" or "fight" statement 

        else:
            children = self.Parent.panelTwo.flexSizer.GetChildren()
            for child in children:
                if int(child.GetWindow().id) == int(action_items[-1]):
                    child.GetWindow().newPanel.permRect.pop()
                    child.GetWindow().newPanel.Refresh()
                    self.Parent.loglist.pop()

        self.Refresh()
        self.image.get_frame()
        


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
        self.Layout()


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
        newItem = wx.MenuItem(parentMenu = self, id = wx.ID_NEW, text = "&Open Video\tCTRL+O")
        self.Append(newItem)
        self.Bind(event = wx.EVT_MENU, handler = self.OnNewVideo, source = newItem)

        openItem = wx.MenuItem(parentMenu = self, id = wx.ID_OPEN, text = "&Open Detections")
        self.Append(openItem)
        self.Bind(event = wx.EVT_MENU, handler = self.OnOpen, source = openItem)

        open2Item = wx.MenuItem(parentMenu = self, id = 5, text = "&Open Interactions")
        self.Append(open2Item)
        self.Bind(event = wx.EVT_MENU, handler = self.OnOpen2, source = open2Item)

        saveItem = wx.MenuItem(parentMenu = self, id = wx.ID_SAVE, text = "&Save\tCTRL+S")
        self.Append(saveItem)
        self.Bind(event = wx.EVT_MENU, handler = self.OnSave, source = saveItem)

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
        head_tail = os.path.split(path)
        
        path_labels = os.path.join(head_tail[0], "predictions", head_tail[1], "results.txt")
        #elems.insert(-1, "predictions")
        #elems.append("results.txt")
        #path_labels = "/".join(elems)


        if os.path.exists(path):
            cap = cv2.VideoCapture(path)
            cap.set(3, 400)
            cap.set(4, 300)
            try:
                lines = pd.read_csv(path_labels, sep = ",", header = None, index_col = False, names = ['frame', 'id', 'x', 'y', 'w', 'h', 'conf', 'class', 'n'])
            except FileNotFoundError:
                lines = pd.DataFrame()
                print("No files found")
            
        

        self.parentFrame.OnInit(cap, lines, filename = head_tail[1])
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
    
    
    
    def OnOpen2(self, event):

        wildcard = "TXT files (*.txt)|*.txt"
        dialog = wx.FileDialog(self.parentFrame, "Open Text Files", wildcard,
                                style = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return None

        path = dialog.GetPath()

        if os.path.exists(path):
            #with open(path) as f:
            interactions = pd.read_csv(path, sep = " ", header = None, index_col = False, names = ['frame', 'from', 'to', 'interaction']) #f.readlines()

        # replace loglist
        self.parentFrame.loglist = ["Loglist\n--------\n"]

        def ranges(nums):
            nums = sorted(set(nums))
            gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s+1 < e]
            edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
            return list(zip(edges, edges))

        print(interactions)
        int_summ = interactions.groupby(['from', 'to', 'interaction']).agg({'frame': ranges})
        print(int_summ)
        int_summ = int_summ['frame'].apply(pd.Series).stack().reset_index()
        int_summ[['min', 'max']] = pd.DataFrame(int_summ[0].tolist(), index = int_summ.index)
        int_summ.drop(columns = ['level_3', 0], inplace = True)
        int_summ.sort_values(['from', 'to'], inplace = True)


        self.parentFrame.panelTwo.Destroy()

        self.parentFrame.OnInit(self.parentFrame.cap, self.parentFrame.lines[1], filename = self.parentFrame.filename)

        curr_from = -99
        curr_to = -99
        curr_int = ""
        rectSizer = None

        for _, row in int_summ.iterrows():
            self.parentFrame.loglist.append(row.interaction + " " + str(row['min']) + " " + str(row['max']) + " " + 
            str(row['from']) + " " + str(row.to) + ' 0\n')

            if (row['from'] != curr_from) or (row['to'] != curr_to) or (row.interaction != curr_int):
                
                if rectSizer is not None:
                    self.parentFrame.panelTwo.flexSizer.Add(rectSizer, 0)


                rectSizer = MarkerLinePanel(self.parentFrame.panelTwo, id = self.parentFrame.panelTwo.countLines)
                rectSizer.who.SetValue(str(row['from']))
                rectSizer.to.SetValue(str(row['to']))
                valCalcStart = int(400/self.parentFrame.video_length * row['min'])
                valCalcEnd = int(400/self.parentFrame.video_length * row['max'])
                rectSizer.newPanel.permRect.append([row.interaction, wx.Rect((valCalcStart, 0), 
                                (valCalcEnd - valCalcStart, 20))])
                self.parentFrame.panelTwo.countLines += 1
                curr_from = row['from']
                curr_to = row['to']
                curr_int = row.interaction

            else:
                valCalcStart = int(400/self.parentFrame.video_length * row['min'])
                valCalcEnd = int(400/self.parentFrame.video_length * row['max'])
                rectSizer.newPanel.permRect.append([row.interaction, wx.Rect((valCalcStart, 0), 
                                (valCalcEnd - valCalcStart, 20))])


        if rectSizer is not None:
            self.parentFrame.panelTwo.flexSizer.Add(rectSizer, 0)

        self.parentFrame.Refresh()
        self.parentFrame.Layout()
        
            

    def OnSave(self,event):

        dialog = wx.FileDialog(self.parentFrame, "Save the labels", defaultFile = self.parentFrame.filename+".txt",
                                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dialog.ShowModal() == wx.ID_CANCEL:
            return None

        path = dialog.GetPath()
        logs = self.parentFrame.loglist
        head_tail = os.path.split(path)

        if self.parentFrame.panelOne.track.GetValue():

            path_tracking = os.path.join(head_tail[0], "tracking_updated", head_tail[1])
            data = self.parentFrame.lines[-1]


            with open(path_tracking, "w+") as myfile:
                for line in data:
                    myfile.write(line)

            # if tracking is updated then we also want to save the log
        #if self.parentFrame.panelOne.log.GetValue():
            path_log = os.path.join(head_tail[0], "log", head_tail[1])

            with open(path_log, "w+") as myfile:
                for line in logs:
                    myfile.write(line)


        if self.parentFrame.panelOne.inter.GetValue():

            path_inter = os.path.join(head_tail[0], "interactions", head_tail[1])
            with open(path_inter, "w+") as myfile:
                for line in logs[1:]:
                    fields = line.split(" ")
                    if fields[0] != "replace":
                        for i in range(int(fields[1]),(int(fields[2])+1)):
                            myfile.write(" ".join([str(i), fields[3], fields[4], fields[0]]) + "\n")
        


    def OnQuit(self, event):
        self.parentFrame.Close()



class MainFrame(wx.Frame):

    def __init__(self, parent, cap, line_list, filename):
        super().__init__(parent= None, title='Review Video', size = (1100, 800))
        self.line_list = line_list
        self.max_id = 0
        self.OnInit(cap, line_list[-1], filename)

        with open("config.yml", "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        
        self.downsize_factor = int(cfg['others']['downsize_factor'])

    def OnInit(self, cap, lines, filename):
        self.filename = filename
        self.cap = cap
        self.get_video_length()
        
        self.line_list.append(lines) #Labels
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
        #this only works for class 0 (monkeys/lemurs) now, not for additional objects
        self.max_id = 0
        if len(self.line_list[-1].index) > 0:
            self.max_id = self.line_list[-1]['id'].max()
        return(self.max_id)



class myApp(wx.App):
    def __init__(self):
        super().__init__(clearSigInt=True)
        self.InitFrame()
    
    def InitFrame(self):
        cap = None 
        line_list = [pd.DataFrame()]
        frame = MainFrame(parent = None, cap = cap, line_list = line_list, filename = "")
        frame.Show()


if __name__ == '__main__':
    app = myApp()
    app.MainLoop()
