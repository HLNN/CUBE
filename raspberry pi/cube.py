import cv2
import re
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
        # Mouse position
        self.lastPosition = (-1, -1)
        # Block position to set [face, point]
        self.blockToSet = [0, 0]
        # self.gpio = gpio.Gpio()
        self.upCap = cv2.VideoCapture
        self.downCap = cv2.VideoCapture
        self.Str = ''
        self.base = 'http://localhost:8080/'
        self.startTime = 0.0
        self.endTime = 0.0
        self.serial = serial.Serial("/dev/ttyUSB0",9600,timeout=0.5)
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

        '''
        for (faceKey, face) in zip(self.blockHSV.keys(), self.blockHSV.values()):
            for (pointKey, point) in zip(face.keys(), face.values()):
                # 使用S的阈值先把白色的识别出来
                if point[1] < int(0.2 * 255):
                    self.blockColor[faceKey][pointKey] = "D"
        '''
        for ii in range(8):
            s_min = -1
            face_min = -1
            block_min = -1
            for i in range(6):
                for j in range(9):
                    if s_min < self.blockHSV[self.face[i]][j][1] and not self.blockColor[self.face[i]][j]:
                        s_min = self.blockHSV[self.face[i]][j][1]
                        face_min = i
                        block_min = j
            if face_min >= 0 and block_min >= 0:
                self.blockColor[self.face[face_min]][block_min] = "D"

        # 然后按照H的大小依次分出 Red Orange Yellow Green Blue
        # find Red
        for ii in range(8):
            h_min = 255
            face_min = -1
            block_min = -1
            for i in range(6):
                for j in range(9):
                    if h_min > self.blockHSV[self.face[i]][j][0] and not self.blockColor[self.face[i]][j]:
                        h_min = self.blockHSV[self.face[i]][j][0]
                        face_min = i
                        block_min = j
            if face_min >= 0 and block_min >= 0:
                self.blockColor[self.face[face_min]][block_min] = "F"

        # find Orange
        for ii in range(8):
            h_min = 255
            face_min = -1
            block_min = -1
            for i in range(6):
                for j in range(9):
                    if h_min > self.blockHSV[self.face[i]][j][0] and not self.blockColor[self.face[i]][j]:
                        h_min = self.blockHSV[self.face[i]][j][0]
                        face_min = i
                        block_min = j
            if face_min >= 0 and block_min >= 0:
                self.blockColor[self.face[face_min]][block_min] = "B"

        # find for Yellow
        for ii in range(8):
            h_min = 255
            face_min = -1
            block_min = -1
            for i in range(6):
                for j in range(9):
                    if h_min > self.blockHSV[self.face[i]][j][0] and not self.blockColor[self.face[i]][j]:
                        h_min = self.blockHSV[self.face[i]][j][0]
                        face_min = i
                        block_min = j
            if face_min >= 0 and block_min >= 0:
                self.blockColor[self.face[face_min]][block_min] = "U"

        # find for Green
        for ii in range(8):
            h_min = 255
            face_min = -1
            block_min = -1
            for i in range(6):
                for j in range(9):
                    if h_min > self.blockHSV[self.face[i]][j][0] and not self.blockColor[self.face[i]][j]:
                        h_min = self.blockHSV[self.face[i]][j][0]
                        face_min = i
                        block_min = j
            if face_min >= 0 and block_min >= 0:
                self.blockColor[self.face[face_min]][block_min] = "R"

        # find for Blue
        for ii in range(8):
            h_min = 255
            face_min = -1
            block_min = -1
            for i in range(6):
                for j in range(9):
                    if h_min > self.blockHSV[self.face[i]][j][0] and not self.blockColor[self.face[i]][j]:
                        h_min = self.blockHSV[self.face[i]][j][0]
                        face_min = i
                        block_min = j
            if face_min >= 0 and block_min >= 0:
                self.blockColor[self.face[face_min]][block_min] = "L"

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
        url = self.base + self.Str
        response = requests.urlopen(url).read()
        self.move(response)
        # pattern = re.compile('([URFDLB]\d){1}', re.S)
        # self.moves = re.findall(pattern, response)
        # for move in self.moves:
        #     # self.gpio.move(move)
        #     pass

    def show(self):
        self.win = cv2.namedWindow("Cube")
        cv2.putText(self.frame, 'UP', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.rectangle(self.frame, (10, 10), (115, 70), (0, 0, 0), 2)
        cv2.putText(self.frame, 'DOWN', (20 + 640, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.rectangle(self.frame, (650, 10), (850, 70), (0, 0, 0), 2)

        if self.lastPosition[0] > 640:
            cv2.putText(self.frame, "H:" + str(self.hsv[0]), (10 + 640, 390),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(self.frame, "S:" + str(self.hsv[1]), (10 + 640, 420),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(self.frame, "V:" + str(self.hsv[2]), (10 + 640, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
        else:
            cv2.putText(self.frame, "H:" + str(self.hsv[0]), (10, 390),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(self.frame, "S:" + str(self.hsv[1]), (10, 420),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(self.frame, "V:" + str(self.hsv[2]), (10, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)

        for face in self.position.values():
            for point in face.values():
                if point:
                    cv2.circle(self.frame, point, 3, (0, 0, 0), -1)

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
                self.colorstr()
                self.ready = True
        # print(self.blockToSet)
        # print(self.position)
        # print(self.blockHSV)


    def mouseCallback(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.lastPosition = (x, y)
            self.hsv = (self.frameInHSV[y, x, 0], self.frameInHSV[y, x, 1], self.frameInHSV[y, x, 2])

        if event == cv2.EVENT_LBUTTONDOWN:
            if (10 < x < 115 and 10 < y < 70) or (650 < x < 850 and 10 < y < 70):
                self.upCap, self.downCap = self.downCap, self.upCap
                self.removeset()
            else:
                self.setBolckPosition(x, y)

    def color(self, hsv):
        if hsv[1] < 60 or (hsv[1] < 85 and hsv[2] < 180):
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
        self.rand()
        
        
        while 1:
            self.show()
            key = cv2.waitKey(30)
            if self.ready:
                self.displayUpdate = True
                # cv2.waitKey(300)
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
