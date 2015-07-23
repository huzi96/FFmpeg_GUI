#!/opt/local/bin/python2.7
# -*- coding: utf-8 -*-
import wx
import re
import os
import subprocess

state = {'fileError': -2}
REDIRECT = False


class fileError(Exception):
    def __init__(self):
        super(fileError, self).__init__()
        self.message = 'No Such File'


__metaclass__ = type


class AbstractModel():
    def __init__(self):
        self.listener = []

    def addListener(self, listenerList):
        for listener in listenerList:
            self.listener.append(listener)

    def removeListener(self, listenerList):
        for listener in listenerList:
            self.listener.remove(listener)

    def update(self):
        for listener in self.listener:
            listener()


class Model(AbstractModel):
    def __init__(self):
        super(Model, self).__init__()
        self.filename = ''
        self.targetName = ''
        self.preCmd = 'ffmpeg -i'
        self.vcodecCmd = ''
        self.vcodec = ''
        self.acodec = ''
        self.acodecCmd = ''
        self.strictCmd = '-strict -2'
        self.command = ''
        self.execCmd = []
        self.state = 'waiting'

    def loadFile(self, path):
        if not os.path.exists(path):
            raise fileError
        self.filename = path
        self.state = 'waiting'
        self.update()

    def generateCommand(self):
        splitNames = re.split('\.',self.filename)
        tagetName = ''
        for names in splitNames[0:-1]:
            tagetName += names
            tagetName += '.'
        if splitNames[-1] != 'mp4':
            tagetName += 'mp4'
        else:
            tagetName += '2.mp4'
        self.targetName = tagetName

        self.vcodec = 'libx264'
        self.vcodecCmd = '-c:v'
        self.command = ' '.join((self.preCmd, self.filename, self.vcodecCmd, self.vcodec,
                                 self.acodecCmd, self.acodec, self.strictCmd, self.targetName))
        self.execCmd = self.command.split()
        self.state = 'In progress Please wait'

    def runCommand(self):
        # # For Windows Only
        # su = subprocess.STARTUPINFO()
        # su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # su.wShowWindow = subprocess.SW_HIDE
        handle = subprocess.Popen(self.execCmd, stderr=subprocess.PIPE, universal_newlines=True)
        outlet = ['']
        timeInSecond = 0
        while True:
            line = handle.stderr.readline()
            outlet.append(line)
            durationGet = re.split('.*Duration: (\d*):(\d*):(\d*)\.(\d*).*', line)

            def parseTime(durationGet):
                dtime = int(durationGet[1])*60+int(durationGet[2])*60+int(durationGet[3])
                return dtime

            if len(durationGet) == 6:
                timeInSecond = parseTime(durationGet)

            resolve =  re.split('.*time=(\d*):(\d*):(\d*)\.(\d*).*', line)
            if len(resolve) == 6:
                crtTime = parseTime(resolve)
                # print repr((crtTime*100)/timeInSecond)+'%'
                self.state = "In progress..." + repr((crtTime*100)/timeInSecond)+'%'
                self.update()
            wx.Yield()
            if line == '':
                break
        self.state = 'Finished'



class MainWindow(wx.App):
    def __init__(self):
        super(MainWindow,self).__init__(redirect=REDIRECT)
        self.frame = Frame(parent=None, title="FFmpeg Frontend", size=(500, -1))
        self.frame.Show()
        self.SetTopWindow(self.frame)


class Frame(wx.Frame):
    def __init__(self, parent, title, size):
        super(Frame, self).__init__(parent=parent, title=title, size=size)
        self.buttonLabels = ('Select', 'Start converting into h.264 MP4 file')

        self.buttonEventProcessor=[]
        self.buttonEventProcessor.append(self.openFile)
        self.buttonEventProcessor.append(self.runCore)

        self.buttons=[]
        self.setButtons()

        self.displayWindow = 'Display'
        self.CTR = wx.TextCtrl(self)

        sizer = self.createSizer()
        self.SetSizer(sizer)

        self.model = Model()
        self.model.addListener([self.OnUpdate])

    def setButtons(self):
        for label, processor in zip(self.buttonLabels, self.buttonEventProcessor):
            oneButton = wx.Button(self, -1, label)
            self.Bind(wx.EVT_BUTTON, processor, oneButton)
            self.buttons.append(oneButton)


    def openFile(self, event):
        dirname = ''
        filename = ''
        dlg = wx.FileDialog(self, 'Select a file', dirname, '', '*.*', wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            dirname = dlg.GetDirectory()
            filename = dlg.GetFilename()
        dlg.Destroy()
        try:
            self.model.loadFile(dirname+'/'+filename)
        except fileError:
            print fileError.message
        #self.CTR.SetValue('Selected file\n'+dirname + '/' + filename)

    def runCore(self, event):
        self.model.generateCommand()
        self.model.update()
        self.model.runCommand()
        self.model.update()

    def createSizer(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.CTR, 4, flag=wx.EXPAND)
        for button in self.buttons:
            sizer.Add(button, 1, flag=wx.EXPAND)
        return sizer

    def OnInit(self):
        return True

    def OnUpdate(self):
        self.CTR.SetValue(self.model.state)


def main():
    app = MainWindow()
    app.MainLoop()

if __name__ == '__main__':
    main()
