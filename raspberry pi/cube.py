import cv2
import re
import os
import urllib.request as requests
import time
import numpy
import threading
import random
import serial
import matplotlib.pyplot as plot

# import gpio
import config


class Cube:
    def __init__(self):
        self.stop = False
        self.ready = False
        self.displayUpdate = False
        self.thread = myThread(1, "display", 1, self)
        self.win = cv2.namedWindow("Cube")
        self.face = "URFDLB"
        self.hsv = (-1, -1, -1)
        self.position = {
            "U": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "R": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "F": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "D": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "L": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "B": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()}
        }
        self.blockHSV = {
            "U": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "R": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "F": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "D": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "L": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "B": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()}
        }
        self.blockColor = {
            "U": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
            "R": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
            "F": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
            "D": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
            "L": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
            "B": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""}
        }
        self.base = (450, 285)
        self.lenth = 30
        self.uBase = (self.base[0] + self.lenth * 3, self.base[1] - self.lenth * 3)
        self.rBase = (self.base[0] + self.lenth * 6, self.base[1])
        self.fBase = (self.base[0] + self.lenth * 3, self.base[1])
        self.dBase = (self.base[0] + self.lenth * 3, self.base[1] + self.lenth * 3)
        self.lBase = self.base
        self.bBase = (self.base[0] + self.lenth * 9, self.base[1])
        self.baseAll = {
            "U": self.uBase,
            "R": self.rBase,
            "F": self.fBase,
            "D": self.dBase,
            "L": self.lBase,
            "B": self.bBase,
        }
        self.colorValue = {
            "U": (0, 255, 255), # yellow
            "R": (0, 255, 0), # green
            "F": (0, 0, 255), # red
            "D": (255, 255, 255), # white
            "L": (255, 0, 0), # blue
            "B": (0, 165, 255), # orange
        }
        # Mouse position
        self.lastPosition = (-1, -1)
        # Block position to set [face, point]
        self.blockToSet = [0, 0]
        # self.gpio = gpio.Gpio()
        self.upCap = cv2.VideoCapture
        self.downCap = cv2.VideoCapture
        self.Str = ''
        self.urlBase = 'http://localhost:8080/'
        self.startTime = 0.0
        self.endTime = 0.0
        self.serial = serial.Serial("/dev/ttyUSB0",9600,timeout=0.5)
        print(self.serial.isOpen())
        self.moves = []
        self.frame = []
        self.frameInHSV = []
        self.frame_up = []
        self.frame_down = []
        try:
            self.upCap = cv2.VideoCapture(0)
            self.downCap = cv2.VideoCapture(2)
            ret, self.frame_up = self.upCap.read()
            ret, self.frame_down = self.downCap.read()
            self.frame_up = cv2.flip(self.frame_up, -1)
            self.frame_down = cv2.flip(self.frame_down, -1)
            self.frame = numpy.hstack((self.frame_up, self.frame_down))  # 水平拼接
            self.frameInHSV = self.frame
        except:
            print("Open camera false!")
            self.stop = True

    def detection(self):
        self.startTime = time.time()
        ret, self.frame_up = self.upCap.read()
        ret, self.frame_down = self.downCap.read()
        self.frame_up = cv2.flip(self.frame_up, -1)
        self.frame_down = cv2.flip(self.frame_down, -1)
        self.frame = numpy.hstack((self.frame_up, self.frame_down))  # 水平拼接
        self.frameInHSV = cv2.cvtColor(self.frame,  cv2.COLOR_BGR2HSV, self.frameInHSV)

        # U-yellow R-green F-red D-white L-blue B-orange
        for (faceKey, face) in zip(self.position.keys(), self.position.values()):
            for (pointKey, point) in zip(face.keys(), face.values()):
                x, y = self.position[faceKey][pointKey]
                color = self.color(self.frameInHSV[y, x])
                self.blockColor[faceKey][pointKey] = color
        ti = time.time()
        self.show()
        print(time.time()-ti)
        # cv2.waitKey(3000)

        self.colorstr()

    def colorstr(self):
        print(self.blockColor)
        self.Str = ""
        for i in range(6):
            for j in range(9):
                if j == 4:
                    self.Str += self.face[i]
                elif j < 4:
                    self.Str += self.blockColor[self.face[i]][j]
                else:
                    self.Str += self.blockColor[self.face[i]][j - 1]
            # self.Str += ' '
        print(self.Str)

    def solve(self):
        url = self.urlBase + self.Str
        response = requests.urlopen(url).read()
        print(response)
        pattern = re.compile('\n.*?\(', re.S)
        moves = re.findall(pattern, response.decode())
        if moves:
            self.move(moves[0])

    def show(self):
        self.win = cv2.namedWindow("Cube")
        cv2.putText(self.frame, 'UP', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.rectangle(self.frame, (10, 10), (115, 70), (0, 0, 0), 2)
        cv2.putText(self.frame, 'DOWN', (20 + 640, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.rectangle(self.frame, (650, 10), (850, 70), (0, 0, 0), 2)
        cv2.putText(self.frame, 'RAND', (460, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.rectangle(self.frame, (450, 10), (630, 70), (0, 0, 0), 2)
        cv2.putText(self.frame, 'SOLVE', (430 + 640, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.rectangle(self.frame, (1070, 10), (1270, 70), (0, 0, 0), 2)
        
        if self.lastPosition[0] > 640:
            cv2.putText(self.frame, "H:" + str(self.hsv[0]), (500 + 640, 390),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(self.frame, "S:" + str(self.hsv[1]), (500 + 640, 420),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(self.frame, "V:" + str(self.hsv[2]), (500 + 640, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
        else:
            cv2.putText(self.frame, "H:" + str(self.hsv[0]), (30, 390),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(self.frame, "S:" + str(self.hsv[1]), (30, 420),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(self.frame, "V:" + str(self.hsv[2]), (30, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
        
        #   U
        # L F R B
        #   D
        lenth = self.lenth
        uBase = (self.base[0] + lenth * 3, self.base[1] - lenth * 3)
        rBase = (self.base[0] + lenth * 6, self.base[1])
        fBase = (self.base[0] + lenth * 3, self.base[1])
        dBase = (self.base[0] + lenth * 3, self.base[1] + lenth * 3)
        lBase = self.base
        bBase = (self.base[0] + lenth * 9, self.base[1])
        
        # background
        cv2.rectangle(self.frame, lBase, (bBase[0] + lenth * 3,  bBase[1] + lenth * 3), (127, 127, 127), -1)
        cv2.rectangle(self.frame, uBase, (dBase[0] + lenth * 3,  dBase[1] + lenth * 3), (127, 127, 127), -1)
        
        # position point and color bar
        for (faceKey, face) in zip(self.position.keys(), self.position.values()):
            # colot bar center 
            colorBarBase = self.baseAll[faceKey]
            colorBarStart = (colorBarBase[0] + lenth, colorBarBase[1] + lenth)
            colorBarEnd = (colorBarBase[0] + lenth * 2, colorBarBase[1] + lenth * 2)
            colorValue = self.colorValue[faceKey]
            cv2.rectangle(self.frame, colorBarStart, colorBarEnd, colorValue, -1)
            
            for (pointKey, point) in zip(face.keys(), face.values()):
                if point:
                    # position point
                    cv2.circle(self.frame, point, 3, (0, 0, 0), -1)
                    # color bar
                    color = self.blockColor[faceKey][pointKey]
                    if color:
                        colorValue = self.colorValue[color]
                        if pointKey >= 4:
                            pointKey += 1
                        colorBarStart = (colorBarBase[0] + lenth * (pointKey % 3), colorBarBase[1] + lenth * (pointKey // 3))
                        colorBarEnd = (colorBarBase[0] + lenth * (pointKey % 3 + 1), colorBarBase[1] + lenth * (pointKey // 3 + 1))
                        cv2.rectangle(self.frame, colorBarStart, colorBarEnd, colorValue, -1)
                    
        # face
        cv2.rectangle(self.frame, lBase, (bBase[0] + lenth * 3,  bBase[1] + lenth * 3), (0, 0, 0), 1)
        cv2.rectangle(self.frame, uBase, (dBase[0] + lenth * 3,  dBase[1] + lenth * 3), (0, 0, 0), 1)
        cv2.rectangle(self.frame, rBase, (rBase[0] + lenth * 3,  rBase[1] + lenth * 3), (0, 0, 0), 1)
        
        # block      
        cv2.rectangle(self.frame, (lBase[0] + lenth, lBase[1]), (lBase[0] + lenth * 2,  lBase[1] + lenth * 3), (0, 0, 0), 1)
        cv2.rectangle(self.frame, (uBase[0] + lenth, uBase[1]), (dBase[0] + lenth * 2,  dBase[1] + lenth * 3), (0, 0, 0), 1)
        cv2.rectangle(self.frame, (rBase[0] + lenth, rBase[1]), (rBase[0] + lenth * 2,  rBase[1] + lenth * 3), (0, 0, 0), 1)
        cv2.rectangle(self.frame, (bBase[0] + lenth, bBase[1]), (bBase[0] + lenth * 2,  bBase[1] + lenth * 3), (0, 0, 0), 1)
        
        cv2.rectangle(self.frame, (uBase[0], uBase[1] + lenth), (uBase[0] + lenth * 3,  uBase[1] + lenth * 2), (0, 0, 0), 1)
        cv2.rectangle(self.frame, (lBase[0], lBase[1] + lenth), (bBase[0] + lenth * 3,  bBase[1] + lenth * 2), (0, 0, 0), 1)
        cv2.rectangle(self.frame, (dBase[0], dBase[1] + lenth), (dBase[0] + lenth * 3,  dBase[1] + lenth * 2), (0, 0, 0), 1)

        

        cv2.imshow("Cube", self.frame)
        ret, self.frame_up = self.upCap.read()
        ret, self.frame_down = self.downCap.read()
        self.frame_up = cv2.flip(self.frame_up, -1)
        self.frame_down = cv2.flip(self.frame_down, -1)
        self.frame = numpy.hstack((self.frame_up, self.frame_down))  # 水平拼接
        self.frameInHSV = cv2.cvtColor(self.frame,  cv2.COLOR_BGR2HSV, self.frameInHSV)

        # extract HSV value from frameInHSV
        for (faceKey, face) in zip(self.position.keys(), self.position.values()):
            for (pointKey, point) in zip(face.keys(), face.values()):
                if point:
                    self.blockHSV[faceKey][pointKey] = (self.frameInHSV[point[1], point[0], 0],
                                                        self.frameInHSV[point[1], point[0], 1],
                                                        self.frameInHSV[point[1], point[0], 2])
        # cv2.imshow("hsv", self.frameInHSV)

    def removeset(self):
        self.blockToSet = [0, 0]
        for (faceKey, face) in zip(self.position.keys(), self.position.values()):
            for (pointKey, point) in zip(face.keys(), face.values()):
                self.position[faceKey][pointKey] = ()
                self.blockHSV[faceKey][pointKey] = ()

    def setBolckPosition(self, x, y):
        self.position[self.face[self.blockToSet[0]]][self.blockToSet[1]] = (x, y)
        color = self.color(self.frameInHSV[y, x])
        self.blockColor[self.face[self.blockToSet[0]]][self.blockToSet[1]] = color
        print(self.frameInHSV[y, x])
        print(color)
        self.blockToSet[1] += 1
        if self.blockToSet[1] == 8:
            self.blockToSet[1] = 0
            self.blockToSet[0] += 1
            if self.blockToSet[0] == 6:
                self.blockToSet = [0, 0]
                for (faceKey, face) in zip(self.position.keys(), self.position.values()):
                    for (pointKey, point) in zip(face.keys(), face.values()):
                        if point:
                            self.blockHSV[faceKey][pointKey] = (self.frameInHSV[point[1], point[0], 0],
                                                                self.frameInHSV[point[1], point[0], 1],
                                                                self.frameInHSV[point[1], point[0], 2])
                            #color = self.color(self.blockHSV[faceKey][pointKey])
                            #self.blockColor[faceKey][pointKey] = color
                #input("Ready to go!!! Press any key to solve!!!")
                # self.detection()
                self.savePosition()
                self.colorstr()
                self.ready = True
        # print(self.blockToSet)
        # print(self.position)
        # print(self.blockHSV)
        
    def savePosition(self):
        # Save
        print('Saving position...')
        numpy.save('position.npy', self.position)

    def loadPosition(self):
        # Load
        if os.path.isfile('position.npy'):
            print('Loading position...')
            self.position = numpy.load('position.npy').item()
        else:
            print('No position file')
        
    def mouseCallback(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.lastPosition = (x, y)
            if x < 1280 and y < 480:
                self.hsv = (self.frameInHSV[y, x, 0], self.frameInHSV[y, x, 1], self.frameInHSV[y, x, 2])

        if event == cv2.EVENT_LBUTTONDOWN:
            if (10 < x < 115 and 10 < y < 70) or (650 < x < 850 and 10 < y < 70):
                self.upCap, self.downCap = self.downCap, self.upCap
                self.removeset()
            elif 450 < x < 630 and 10 < y < 70:
                self.rand()
            elif 1070 < x < 1270 and 10 < y < 70:
                self.detection()
                self.ready = True
            else:
                self.setBolckPosition(x, y)

    def color(self, hsv):
        if hsv[1] < 60 or (hsv[1] < 85 and hsv[2] < 160):
            return 'D'
        else:
            if hsv[0] < 10:
                return 'F'
            elif hsv[0] < 18:
                return 'B'
            elif hsv[0] < 50:
                return 'U'
            elif hsv[0] < 90:
                return 'R'
            else:
                return 'L'
            
    def rand(self):
        randStr = ''
        for i in range(50):
            randStr += self.face[random.randint(0, 5)]
            randStr += str(random.randint(1, 3))
        self.move(randStr)
        
    def move(self, moves):
        if isinstance(moves, str):
            self.serial.write(moves.encode())
        if isinstance(moves, bytes):
            self.serial.write(moves)


    def main(self):
        # self.thread.start()
        self.show()
        cv2.setMouseCallback("Cube", self.mouseCallback)
        self.loadPosition()
        # self.rand()
        # self.Str = 'FDFBURUULBDLLRFRRBRBULFULDBDBURDFFURLLFRLFDBBDLUDBUDFR'
        # self.ready = 1
        while 1:
            self.show()
            key = cv2.waitKey(30)
            if self.ready:
                self.displayUpdate = True
                cv2.waitKey(200)
                # self.detection()
                self.solve()
                self.displayUpdate = False
                self.ready = False


class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, Cube):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.cube = Cube
        
    def run(self):
        while self.cube.displayUpdate and not self.cube.stop:
            self.cube.show()
            print('bbb')
            cv2.waitKey(30)
            
    def pause(self):
        self.__flag.clear() # set to False

    def resume(self):
        self.__flag.set() # set to True

    def stop(self):
        self.__flag.set() # resume if pause
        self.__running.clear() # set to False  

if __name__=="__main__":
    cube = Cube()
    cube.main()
