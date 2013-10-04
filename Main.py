from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
from direct.task import Task
from direct.interval.ProjectileInterval import ProjectileInterval
from panda3d.core import Point3
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import *
from panda3d.core import WindowProperties
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from random import randint
import sys

loadPrcFileData("", """fullscreen 1 
                      win-size 1366 768
                      load-display pandadx9""")


class Myapp(ShowBase):
    
    def __init__(self):
        ShowBase.__init__(self)
        self.accept("escape",sys.exit)
        self.accept("mouse1", self.startShoot)
        self.accept("mouse1-up", self.endShoot)
        
        base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        self.heading = 0
        self.pitch = 0
        self.mousex = 0
        self.mousey = 0
        self.flight = []
        self.cs_flight = []
        self.explosion = []
        self.score = 0
        self.life = 20
        self.m1down = 1
         
        self.environ = self.loader.loadModel("models/terrain")
        self.environ.reparentTo(self.render)
        self.environ.setScale(0.8, 0.8, 0.8)
        self.environ.setPos(0,0,-10)
        self.environ.setHpr(-90,0,0)
        
        for k in range(0,5):
            self.flight.append(self.loader.loadModel("models/spitfire"))
            self.flight[k].reparentTo(self.render)
            self.flight[k].setScale(0.1, 0.1, 0.1)
            self.flight[k].setPos(randint(-40,20), randint(300,400),randint(10,20))
            self.cs_flight.append( self.flight[k].attachNewNode(CollisionNode(str(k))))
            self.cs_flight[k].node().addSolid(CollisionSphere(0,0,5,30))
            #self.cs_flight[k].show()
            self.flight[k].setCollideMask(BitMask32.bit(1))
        
        self.bullets = [] 
        
        self.crosshair = OnscreenImage(image = 'models/crosshair.png', pos = (0,0,0))
        self.crosshair.setScale(0.03,0.03,0.03)
        self.crosshair.setTransparency(TransparencyAttrib.MAlpha) 
        self.title = OnscreenText(" ",
                              style=1, fg=(1,1,1,1),
                              pos=(0,0), scale = .07)
        
        self.taskMgr.add(self.mouse_control, "mouse_control")
        self.taskMgr.add(self.update_flight, "update_flight")

        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue() 

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))

        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP,self.pq)   
        
        self.gun = OnscreenImage(image = 'models/gun.png', pos = (0.24, 0, -0.54)) 
        self.gun.setScale(1,0.6,0.6)
        self.gun.setTransparency(TransparencyAttrib.MAlpha)
        
        self.sound = base.loader.loadSfx("models/sound.ogg")
    
        base.setFrameRateMeter(True)
           
    def mouse_control(self,task):
        md = base.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if base.win.movePointer(0, 100, 100):
            self.heading = self.heading - (x - 100) * 0.1
            self.pitch = self.pitch - (y - 100) * 0.1
        if (self.pitch < -10): self.pitch = -10
        if (self.pitch >  20): self.pitch =  20
        if (self.heading < -40): self.heading = -40
        if (self.heading >  30): self.heading =  30
        base.camera.setHpr(self.heading,self.pitch,0)

        return Task.cont

    def update_flight(self,task):
        i = 0
        while(i<len(self.flight)):
            x = self.flight[i].getY()
            if x<-3:
                self.flight[i].setPos(randint(-40,20), randint(200,300),randint(10,20))
                if(self.life ==0):
                    self.game_end()
                else:
                    self.life -= 1
            else:
                x -= 0.7
                self.flight[i].setPos(self.flight[i].getX(), x, self.flight[i].getZ())
            i+=1
        self.title.destroy()
        self.title = OnscreenText(text='Life: ' + str(self.life)+' Score: '+str(self.score),
                              style=1, fg=(1,1,1,1),
                              pos=(-1.5,0.9), scale = .07)
        return Task.cont
               
    def removeBullet(self,task):
        if len(self.bullets) < 1: return
        self.bulletNP = self.bullets.pop(0)
        self.bulletNP.removeNode()
        return task.done
             
    def shootBullet(self,task):
        self.ball = self.loader.loadModel("models/bullet")
        self.ball.reparentTo(self.render)
        self.ball.setScale(0.02,0.02,0.02)
        self.ball.setPos(0,0,0) 
        self.bullets.append(self.ball)
        self.bt = ProjectileInterval(self.ball,
                                     startPos = Point3(0,0,-5),
                                     endPos = Point3(self.heading * -2 , 100 , self.pitch*2), duration = 0.3 ,
                                     gravityMult = -2 )    
        self.bt.start()
        self.taskMgr.doMethodLater(0.3, self.removeBullet, 'removeBullet')
        self.hit_flight()
        if(self.m1down):
            self.taskMgr.doMethodLater(0.2, self.shootBullet, 'shootbullet')

    def hit_flight(self):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode,0,0)
            self.picker.traverse(render)
            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
                pickedObj = self.pq.getEntry(0).getIntoNodePath()
                if pickedObj.getName() != 'CINEMA4D_Mesh' :
                    k = int(pickedObj.getName())
                    self.score += 1
                    self.explode(self.flight[k].getX(),self.flight[k].getY(),self.flight[k].getZ())
                    self.flight[k].setPos(randint(-40,20), randint(200,300),randint(10,20))
    
    def game_end(self):
        self.crosshair.remove()
        self.gov = OnscreenText("Game Over",
                              style=1, fg=(1,1,1,1),
                              pos=(0,0), scale = 0.07)
        self.taskMgr.remove("mouse_control")
        self.taskMgr.remove("update_flight")
        #self.explode(20,20,20)
        p = open('score.txt','r')
        score = p.readline()
        p.close()
        if(self.score > int(score)):
            p = open('score.txt','w')
            p.write(str(self.score))
            p.close()


    def explode(self,x,y,z):
        k = len(self.explosion) 
        self.explosion.append(loader.loadModel('explosion/flip.egg'))
        self.explosion[k].reparentTo(self.render)
        self.explosion[k].setPos(x,y,z)
        self.explosion[k].setScale(5,5,5)
        self.taskMgr.doMethodLater(0.6, self.removeExplosion, 'removeExp')  
        
    def removeExplosion(self,task):
        if len(self.explosion) < 1: return
        self.explosion[0].removeNode()
        del self.explosion[0]
        return task.done

    def endShoot(self):
        self.m1down = 0
        self.sound.stop()
     
    def startShoot(self):
        self.sound.play()
        self.m1down = 1
        self.taskMgr.doMethodLater(0.1, self.shootBullet, 'shootbullet')
        
app = Myapp()
app.run()
