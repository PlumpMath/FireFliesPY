from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import loadPrcFileData
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from pandac.PandaModules import TextNode
from direct.gui.OnscreenImage import OnscreenImage
import os

loadPrcFileData("", """fullscreen 0 
                      win-size 600 600
                    window-title FireFlies by Ajay""")

def setText():
    os.system('Main.py')
 
class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.hs = OnscreenText(' ', style=1, fg=(1,1,1,1),
                              pos=(-0.4,-0.8), scale = .1)
        bg = OnscreenImage(image = 'models/banner.png', pos = (0,0,0))  
        b = DirectButton(text = ("Play"), text_bg=(255,255,255,0) ,text_scale = (0.5,0.5), text_fg = (0,0,255,255) ,scale=.2, command=setText)
        b.setPos(0.55,0,-0.75)
        self.taskMgr.add(self.update, "update")

    def update(self, task):
        p = open('score.txt','r')
        score = p.readline()
        p.close()
        self.hs.destroy()
        self.hs = OnscreenText(score, style=1, fg=(1,1,1,1),
                            pos=(-0.4,-0.8), scale = .1)
        return Task.cont
 
app = MyApp()
app.run()