import cv2
import re
import urllib.request as requests
import time
import numpy
import threading
# import serial
import matplotlib.pyplot as plot

# import gpio
import config


class Cube:
    def __init__(self):
        self.stop = False
        self.displayUpdate = True
        self.thread = myThread(1, "display", 1, self)
        self.win = cv2.namedWindow("Cube")
        self.face = "URFDLB"
        self.hsv = (-1, -1, -1)
        self.position = {
            "U": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()},
            "R": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()},
            "F": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()},
            "D": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()},
            "L": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()},
            "B": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()}
        }
        self.blockHSV = {
            "U": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()},
            "R": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()},
            "F": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()},
            "D": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()},
            "L": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()},
            "B": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: (), 8: ()}
        }
        self.blockColor = {
            "U": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: ""},
            "R": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: ""},
            "F": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: ""},
            "D": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: ""},
            "L": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: ""},
            "B": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: "", 8: ""}
        }
        self.lastPosition = (-1, -1)
        self.blockToSet = [0, 0]
        # self.gpio = gpio.Gpio()
        self.upCap = cv2.VideoCapture
        self.downCap = cv2.VideoCapture
        self.Str = ''
        self.base = 'http://localhost:8888/'
        self.startTime = 0.0
        self.endTime = 0.0
        # self.ser = serial.
        self.moves = []
        self.frame = []
        self.frameInHSV = []
        self.frame_up = []
        self.frame_down = []
        try:
            self.upCap = cv2.VideoCapture(0)
            self.downCap = cv2.VideoCapture(1)
            ret, self.frame_up = self.upCap.read()
            ret, self.frame_down = self.downCap.read()
            self.frame = numpy.hstack((self.frame_up, self.frame_down))  # 水平拼接
            self.frameInHSV = self.frame
        except:
            print("Open camera false!")
            self.stop = True

    def detection(self):
        self.startTime = time.time()
        ret, self.frame_up = self.upCap.read()
        ret, self.frame_down = self.downCap.read()
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
        for ii in range(9):
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
        for ii in range(9):
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
        for ii in range(9):
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
        for ii in range(9):
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
        for ii in range(9):
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
        for ii in range(9):
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

        print(self.blockColor)
        self.Str = ""
        for i in range(6):
            for j in range(9):
                self.Str += self.blockColor[self.face[i]][j]
        print(self.Str)

    def solve(self):
        url = self.base + self.Str
        response = requests.urlopen(url)
        pattern = re.compile('([URFDLB]\d){1}', re.S)
        self.moves = re.findall(pattern, response)
        for move in self.moves:
            # self.gpio.move(move)
            pass

    def show(self):
        self.win = cv2.namedWindow("Cube")
        cv2.putText(self.frame, 'UP', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(self.frame, 'DOWN', (20 + 640, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.rectangle(self.frame, (10, 10), (115, 70), (0, 0, 0), 2)
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
        self.frame = numpy.hstack((self.frame_up, self.frame_down))  # 水平拼接
        self.frameInHSV = cv2.cvtColor(self.frame,  cv2.COLOR_BGR2HSV, self.frameInHSV)

        for (faceKey, face) in zip(self.position.keys(), self.position.values()):
            for (pointKey, point) in zip(face.keys(), face.values()):
                if point:
                    self.blockHSV[faceKey][pointKey] = (self.frameInHSV[point[1], point[0], 0],
                                                        self.frameInHSV[point[1], point[0], 2],
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
        self.blockToSet[1] += 1
        if self.blockToSet[1] == 9:
            self.blockToSet[1] = 0
            self.blockToSet[0] +=1
            if self.blockToSet[0] == 6:
                self.blockToSet = [0, 0]
                for (faceKey, face) in zip(self.position.keys(), self.position.values()):
                    for (pointKey, point) in zip(face.keys(), face.values()):
                        if point:
                            self.blockHSV[faceKey][pointKey] = (self.frameInHSV[point[1], point[0], 0],
                                                                self.frameInHSV[point[1], point[0], 2],
                                                                self.frameInHSV[point[1], point[0], 2])
                #input("Ready to go!!! Press any key to solve!!!")
                self.detection()
        # print(self.blockToSet)
        # print(self.position)
        # print(self.blockHSV)


    def mouseCallback(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.lastPosition = (x, y)
            self.hsv = (self.frameInHSV[y, x, 0], self.frameInHSV[y, x, 2], self.frameInHSV[y, x, 2])

        if event == cv2.EVENT_LBUTTONDOWN:
            if (10 < x < 115 and 10 < y < 70) or (650 < x < 850 and 10 < y < 70):
                self.upCap, self.downCap = self.downCap, self.upCap
                self.removeset()
                return
            self.setBolckPosition(x, y)

    def main(self):
        # self.thread.start()
        self.show()
        cv2.setMouseCallback("Cube", self.mouseCallback)
        while 1:
            self.show()
            key = cv2.waitKey(30)
            # self.detection()
            # self.solve()


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
            cv2.waitKey(30)


if __name__=="__main__":
    cube = Cube()
    cube.main()