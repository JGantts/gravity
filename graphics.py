from Tkinter import *
import tkMessageBox
import time
from math import *
import random

# a subclass of Canvas for dealing with resizing of windows
class Vector:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(vectorA, vectorB):
        return Vector(vectorA.x+vectorB.x, vectorA.y+vectorB.y)
    add = staticmethod(add)

    def mult(vectorA, intA):
        return Vector(vectorA.x*intA, vectorA.y*intA)
    mult = staticmethod(mult)

    def divVI(vectorA, intA):
        return Vector(vectorA.x/intA, vectorA.y/intA)
    divVI = staticmethod(divVI)

    def divIV(intA, vectorA):
        return Vector(intA/vectorA.x, intA/vectorA.y)
    divIV = staticmethod(divIV)

    def netDistance(vectorA, vectorB):
        return sqrt(pow(vectorA.x-vectorB.x, 2) + pow(vectorA.y-vectorB.y, 2))
    netDistance = staticmethod(netDistance)

class CelestialBody:
    force = Vector(0, 0)
    velocity = Vector(0, 0)
    position = Vector(0, 0)
    mass = 0
    diameter = 0
    color = "black"

    def __init__(self, positionX, positionY, velocityX, velocityY, mass, diameter, color):
        self.position = Vector(positionX, positionY)
        self.velocity = Vector(velocityX, velocityY)
        self.mass = mass
        self.diameter = diameter
        self.color = color

    def resetForce(self):
        self.force = Vector(0, 0)

    def addForce(self, other):
        grav = 0.01
        m1 = self.mass
        m2 = other.mass
        netDist = Vector.netDistance(other.position, self.position)
        distX = other.position.x - self.position.x
        distY = other.position.y - self.position.y
        netForce = (grav*m1*m2)/netDist
        forceX = distX * netForce / netDist
        forceY = distY * netForce / netDist
        #if(self.mass==1):
            #print ("forceX(local): " + str(forceX))
            #print ("forceY(local): " + str(forceY))
            #print ("forceX0: " + str(self.force.x))
            #print ("forceY0: " + str(self.force.y))
        self.force = Vector.add(self.force, Vector(forceX, forceY))
        #if(self.mass==1):
            #print ("netForce: " + str(netForce))
            #print ("forceX1: " + str(self.force.x))
            #print ("forceY1: " + str(self.force.y))

    def updateVelocity(self):
        #if(self.mass==1):
            #print ("forceX: " + str(self.force.x))
            #print ("forceY: " + str(self.force.y))
            #print ("velocityY: " + str(self.velocity.y))
            #print ("velocityX: " + str(self.velocity.x))
            #print (" ")
        self.velocity = Vector.add(self.velocity, Vector.divVI(self.force, self.mass))

    def updatePosition(self):
        self.position = Vector.add(self.position, self.velocity)

class World:
    bodies = NONE

    def __init__(self, bodies):
        self.bodies = bodies

    def tick(self):
        for i in range(len(self.bodies)):
            self.bodies[i].resetForce()
            for j in range(len(self.bodies)):
                if (i != j):
                #    print ("calculating force between  " + str(i) + " and " + str(j))
                    self.bodies[i].addForce(self.bodies[j])
        for i in range(len(self.bodies)):
            self.bodies[i].updateVelocity()
            self.bodies[i].updatePosition()

class ResizingCanvas(Canvas):
    windowTopLeft = Vector(0, 0)
    windowScale = 1

    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        #self.scale("all",0,0,wscale,hscale)

    def updateWorld(self, world):
        self.delete("all")
        for i in range(len(world.bodies)):
            x = (world.bodies[i].position.x-self.windowTopLeft.x)/self.windowScale
            y = (world.bodies[i].position.y-self.windowTopLeft.y)/self.windowScale
            diameter = world.bodies[i].diameter#/self.windowScale
            oval = self.create_oval(
                x,
                y,
                x+diameter,
                y+diameter,
                fill=world.bodies[i].color)
        self.update()

class ViewHandler:
    canvas = NONE
    world = NONE
    playing = NO
    speed = 4

    def __init__(self, canvas):#, world):
        self.canvas = canvas
        self.canvas.windowTopLeft = Vector(0, 0)
        self.canvas.windowScale = 1.0
        #self.world = world

    def resetWorld(self):
        self.setupSquare()
        #self.setupSquare()
        self.canvas.updateWorld(self.world)

    def resetView(self):
        self.speed = 4
        self.canvas.windowTopLeft = Vector(0, 0)
        self.canvas.windowScale = 1.0
        self.canvas.updateWorld(self.world)

    def start(self):
        if(not self.playing):
            if(self.world == NONE):
                self.resetWorld()
            self.playing = YES
            self.beginPlaying()

    def stop(self):
        self.playing = NO
        self.canvas.updateWorld(self.world)

    def slower(self):
        if(self.playing):
            if(self.speed != 1):
                self.speed -= 1
        self.canvas.updateWorld(self.world)

    def faster(self):
        if(self.playing):
            if(self.speed != 7):
                self.speed += 1
        self.canvas.updateWorld(self.world)

    def zoomIn(self):
        self.canvas.windowScale /= 2
        self.canvas.updateWorld(self.world)

    def zoomOut(self):
        self.canvas.windowScale *= 2
        self.canvas.updateWorld(self.world)
    
    def right(self):
        self.canvas.windowTopLeft = Vector.add(self.canvas.windowTopLeft, Vector(self.canvas.windowScale*50, 0))
        self.canvas.updateWorld(self.world)

    def left(self):
        self.canvas.windowTopLeft = Vector.add(self.canvas.windowTopLeft, Vector(self.canvas.windowScale*-50, 0))
        self.canvas.updateWorld(self.world)

    def up(self):
        self.canvas.windowTopLeft = Vector.add(self.canvas.windowTopLeft, Vector(0, self.canvas.windowScale*-50))
        self.canvas.updateWorld(self.world)

    def down(self):
        self.canvas.windowTopLeft = Vector.add(self.canvas.windowTopLeft, Vector(0, self.canvas.windowScale*50))
        self.canvas.updateWorld(self.world)
            

    def tickDelay(self):
        if(self.speed == 1):
            return 32
        elif(self.speed == 2):
            return 16
        elif(self.speed == 3):
            return 8
        elif(self.speed == 4):
            return 4
        elif(self.speed == 5):
            return 2
        elif(self.speed == 6):
            return 1
        elif(self.speed == 7):
            return 0

    def beginPlaying(self):
        for i in range(0, 1):
            self.world.tick()
        self.canvas.updateWorld(self.world)
        #time.sleep(0.01)
        if(self.playing):
            root.after(self.tickDelay(), self.beginPlaying)


    def setupEarthMoonSun(self):
        bodies=[CelestialBody(500, 300, -0.01575, 0,     100, 25, "yellow"),
                CelestialBody(500, 600, 1,       0.005, 1,    10, "blue"), 
                CelestialBody(500, 601, 1.1,    -0.01,  0.5,   5, "gray"), ]
        self.world = World(bodies)

    def setupSquare(self):
        delta = 20
        min = 000
        max = 1000

        count = ((max-min)/delta)*4

        bodies = [None] * (count)
        r = lambda: random.randint(127,255)
        g = lambda: random.randint(127,175)
        b = lambda: random.randint(0,64)

        velX = 0
        velY = -1

        x = min
        y = min
        i = 0
        done = NO
        while( not done ):
            #print ("X: " + str(x) + " Y: " + str(y))
            #bodies[i] = CelestialBody(x, y, velX, velY, 1, 10, '#%02X%02X%02X' % (r(),g(),b()))
            bodies[i] = CelestialBody(x, y, velX, velY, 1, 10, '#%02X%02X%02X' % (255*(count-i)/count, 255*(count-i)/count, 255*i/count))
            i+=1
            if(x==min):
                if(y!=max):
                    y += delta
                else:
                    x += delta
                    velX = -1
                    velY = 0
            elif(y==max):
                if(x!=max):
                    x += delta
                else:
                    y -= delta
                    velX = 0
                    velY = 1
            elif(x==max):
                if(y!=min):
                    y -= delta
                else:
                    x -= delta
                    velX = 1
                    velY = 0
            else:
                x -= delta
                if(x==min):
                    done = YES
        self.world = World(bodies)


class Application(Frame):
    def createWidgets(self):
        self.viewWindow = ResizingCanvas(self, bg="black", height=1600, width=1600, highlightthickness=0)
        self.viewHandler = ViewHandler(self.viewWindow)
        self.viewWindow.pack({"side": "top"}, fill=BOTH, expand=YES)

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit
        self.QUIT.pack({"side": "left"})

        self.RESET_WORLD = Button(self)
        self.RESET_WORLD["text"] = "Reset World",
        self.RESET_WORLD["command"] = self.viewHandler.resetWorld
        self.RESET_WORLD.pack({"side": "left"})

        self.RESET_VIEW = Button(self)
        self.RESET_VIEW["text"] = "Reset View",
        self.RESET_VIEW["command"] = self.viewHandler.resetView
        self.RESET_VIEW.pack({"side": "left"})

        self.START = Button(self)
        self.START["text"] = "Play",
        self.START["command"] = self.viewHandler.start
        self.START.pack({"side": "left"})

        self.STOP = Button(self)
        self.STOP["text"] = "Pause",
        self.STOP["command"] = self.viewHandler.stop
        self.STOP.pack({"side": "left"})

        self.SLOWER = Button(self)
        self.SLOWER["text"] = "Slower",
        self.SLOWER["command"] = self.viewHandler.slower
        self.SLOWER.pack({"side": "left"})

        self.FASTER = Button(self)
        self.FASTER["text"] = "Faster",
        self.FASTER["command"] = self.viewHandler.faster
        self.FASTER.pack({"side": "left"})

        self.RIGHT = Button(self)
        self.RIGHT["text"] = ">",
        self.RIGHT["command"] = self.viewHandler.right
        self.RIGHT.pack({"side": "right"})

        self.DOWN = Button(self)
        self.DOWN["text"] = "V",
        self.DOWN["command"] = self.viewHandler.down
        self.DOWN.pack({"side": "right"})

        self.UP = Button(self)
        self.UP["text"] = "^",
        self.UP["command"] = self.viewHandler.up
        self.UP.pack({"side": "right"})

        self.LEFT = Button(self)
        self.LEFT["text"] = "<",
        self.LEFT["command"] = self.viewHandler.left
        self.LEFT.pack({"side": "right"})

        self.OUT = Button(self)
        self.OUT["text"] = "Out",
        self.OUT["command"] = self.viewHandler.zoomOut
        self.OUT.pack({"side": "right"})

        self.IN = Button(self)
        self.IN["text"] = "In",
        self.IN["command"] = self.viewHandler.zoomIn
        self.IN.pack({"side": "right"})





    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack(fill=BOTH, expand=YES)
        self.createWidgets()

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()
