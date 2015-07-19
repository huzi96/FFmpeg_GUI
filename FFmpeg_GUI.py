import wx
import re


class Frame(wx.Frame):
    def __init__(self, parent, title, size):
        super(Frame, self).__init__(parent=parent, title=title, size=size)


class MainWindow(wx.App):

    def OnInit(self):
        self.frame = Frame(None, "FFmpeg Frontend", (500, 500))
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True


def main():
    app = MainWindow(redirect=True)
    app.MainLoop()

if __name__ == '__main__':
    main()
