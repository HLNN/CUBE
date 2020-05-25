import cv2
import re
import os
import time
import numpy
import random
import serial
import urllib.request as requests


def add2(a, b):
    if len(a) == len(b):
        return tuple(a[i] + b[i] for i in range(len(a)))


def mul2(a, num):
    return tuple(a[i] * num for i in range(len(a)))


class Cube:
    def __init__(self, display=True, serialName="/dev/ttyUSB0"):
        self.face = "URFDLB"
        self.upCap = cv2.VideoCapture
        self.downCap = cv2.VideoCapture
        self.urlBase = "http://localhost:5555/"
        self.serial = serial.Serial(serialName, 9600, timeout=0.5)
        print("Serial is OK!") if self.serial.isOpen() else print("Open serial failed!")
        time.sleep(1)
        self.initMove()
        # Stop and quit the program
        self.stop = False
        # Ready for solving
        self.ready = False
        # True when position info was modified
        self.needSave = False
        # Print debug info
        self.debug = True
        # HSV value at the point of the mouse
        self.hsv = (-1, -1, -1)
        # Start and finish timestamp of single solving
        self.startTime = 0.0
        self.finishTime = 0.0
        # Facelet color string
        self.Str = ""
        # Solving step list
        self.moves = []
        # Single frame from camera
        self.frame_up = []
        self.frame_down = []
        self.frame = []
        self.mask = []
        self.frameInHSV = []
        # Position info of every facelet
        # Each facelet include several ROIs
        self.position = {
            "U": {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
            "R": {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
            "F": {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
            "D": {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
            "L": {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
            "B": {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
        }
        # HSV and BGR value of every facelet
        # Mean of points in ROIs
        self.faceletHSV = {
            "U": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "R": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "F": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "D": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "L": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "B": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
        }
        self.faceletBGR = {
            "U": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "R": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "F": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "D": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "L": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
            "B": {0: (), 1: (), 2: (), 3: (), 4: (), 5: (), 6: (), 7: ()},
        }
        # Color of every facelet
        self.faceletColor = {
            "U": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
            "R": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
            "F": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
            "D": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
            "L": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
            "B": {0: "", 1: "", 2: "", 3: "", 4: "", 5: "", 6: "", 7: ""},
        }
        # Attribute for display and mouse callback
        self.display = display
        if self.display:
            self.win = cv2.namedWindow("Cube")
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.line = cv2.LINE_AA
        # Color bar setting
        self.origin = (450, 285)
        self.lenth = 30
        # Using real color to fill the color bar
        self.realColor = False
        self.baseAll = {
            "U": self.offset(self.origin, 3, -3),
            "R": self.offset(self.origin, 6, 0),
            "F": self.offset(self.origin, 3, 0),
            "D": self.offset(self.origin, 3, 3),
            "L": self.origin,
            "B": self.offset(self.origin, 9, 0),
        }
        self.colorValue = {
            "U": (0, 255, 255),  # yellow
            "R": (0, 255, 0),  # green
            "F": (0, 0, 255),  # red
            "D": (255, 255, 255),  # white
            "L": (255, 0, 0),  # blue
            "B": (0, 165, 255),  # orange
        }
        # Mouse position
        self.lastPosition = (-1, -1)
        # Facelet going to set
        self.faceletToSet = [0, 0]
        # Saving as a stack
        self.faceletToSetLast = []
        try:
            self.upCap = cv2.VideoCapture(0)
            self.downCap = cv2.VideoCapture(2)
            self.getFrame()
            self.mask = cv2.cvtColor(self.frame.copy(), cv2.COLOR_BGR2GRAY)
        except:
            print("Open camera failed!")
            self.stop = True

    def getFrame(self):
        ret, self.frame_up = self.upCap.read()
        ret, self.frame_down = self.downCap.read()
        self.frame_up = cv2.flip(self.frame_up, -1)
        self.frame_down = cv2.flip(self.frame_down, -1)
        self.frame = numpy.hstack((self.frame_up, self.frame_down))
        self.frameInHSV = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

    def detect(self):
        self.getFrame()
        # U-yellow R-green F-red D-white L-blue B-orange
        for (faceKey, face) in zip(self.position.keys(), self.position.values()):
            for (faceletKey, facelet) in zip(face.keys(), face.values()):
                self.faceletColor[faceKey][faceletKey] = ""
                if facelet:
                    rois = facelet
                    faceletColor = (0, 0, 0)
                    roiNum = 0
                    self.mask[:, :] = 0
                    for roi in rois:
                        if isinstance(roi, list):
                            continue
                        roiNum += 1
                        cv2.fillPoly(self.mask, numpy.array([roi]), (255, 255, 255))
                    if roiNum > 0:
                        # Remove alpha
                        roiHSVColor = cv2.mean(self.frameInHSV, self.mask)[:-1]
                        roiBGRColor = cv2.mean(self.frame, self.mask)[:-1]
                        self.faceletHSV[faceKey][faceletKey] = roiHSVColor
                        self.faceletBGR[faceKey][faceletKey] = roiBGRColor
                        self.faceletColor[faceKey][faceletKey] = self.color(roiHSVColor)
        self.colorstr()

    def colorstr(self):
        self.Str = ""
        for i in range(6):
            for j in range(9):
                if j == 4:
                    self.Str += self.face[i]
                elif j < 4:
                    self.Str += self.faceletColor[self.face[i]][j]
                else:
                    self.Str += self.faceletColor[self.face[i]][j - 1]
        # print(self.Str)

    def solve(self):
        for _ in range(5):
            # Try up to 5 times
            self.detect()
            if self.debug:
                print(self.faceletColor)
                print(self.Str)
            # Checking str len
            if len(self.Str) != 54:
                if len(self.Str) < 54:
                    print("Error! Bad facelet str len. Less than 54.")
                else:
                    rint("Error! Bad facelet str len. More than 54.")
                continue
            # Checking str color
            colors = {"U": 0, "R": 0, "F": 0, "D": 0, "L": 0, "B": 0}
            for c in range(54):
                colors[self.Str[c]] += 1
            if not all(num == 9 for num in colors):
                print("Error! Bad facelet str color. Not 9 for each color.")
                continue
            # Solving
            url = self.urlBase + self.Str
            ti = time.time()
            response = requests.urlopen(url).read()
            moves = re.findall("\n.*?\(", response.decode(), re.S)
            if self.debug:
                print(time.time() - ti)
                print(response)
                print(moves)
            if moves:
                self.move(moves[0])
                return

    def show(self):
        cv2.putText(self.frame, "UP", (20, 60), self.font, 2, (0, 0, 0), 2, self.line)
        cv2.rectangle(self.frame, (10, 10), (115, 70), (0, 0, 0), 2)
        cv2.putText(self.frame, "DOWN", (20 + 640, 60), self.font, 2, (0, 0, 0), 2, self.line)
        cv2.rectangle(self.frame, (650, 10), (850, 70), (0, 0, 0), 2)
        cv2.putText(self.frame, "RAND", (460, 60), self.font, 2, (0, 0, 0), 2, self.line)
        cv2.rectangle(self.frame, (450, 10), (630, 70), (0, 0, 0), 2)
        cv2.putText(self.frame, "SOLVE", (430 + 640, 60), self.font, 2, (0, 0, 0), 2, self.line)
        cv2.rectangle(self.frame, (1070, 10), (1270, 70), (0, 0, 0), 2)

        if self.lastPosition[0] > 640:
            cv2.putText(self.frame, "H:" + str(self.hsv[0]), (500 + 640, 390), self.font, 1, (0, 0, 0), 1, self.line)
            cv2.putText(self.frame, "S:" + str(self.hsv[1]), (500 + 640, 420), self.font, 1, (0, 0, 0), 1, self.line)
            cv2.putText(self.frame, "V:" + str(self.hsv[2]), (500 + 640, 450), self.font, 1, (0, 0, 0), 1, self.line)
        else:
            cv2.putText(self.frame, "H:" + str(self.hsv[0]), (30, 390), self.font, 1, (0, 0, 0), 1, self.line)
            cv2.putText(self.frame, "S:" + str(self.hsv[1]), (30, 420), self.font, 1, (0, 0, 0), 1, self.line)
            cv2.putText(self.frame, "V:" + str(self.hsv[2]), (30, 450), self.font, 1, (0, 0, 0), 1, self.line)

        #   U
        # L F R B
        #   D
        baseAll = self.baseAll

        # Background of color bar
        cv2.rectangle(self.frame, baseAll["L"], self.offset(baseAll["B"], 3, 3), (127, 127, 127), -1)
        cv2.rectangle(self.frame, baseAll["U"], self.offset(baseAll["D"], 3, 3), (127, 127, 127), -1)

        # Position rois and color bar
        for (faceKey, face) in zip(self.position.keys(), self.position.values()):
            # Center facelet of every face
            colorBarBase = self.baseAll[faceKey]
            colorBarStart = self.offset(colorBarBase, 1, 1)
            colorBarEnd = self.offset(colorBarBase, 2, 2)
            colorValue = self.colorValue[faceKey]
            cv2.rectangle(self.frame, colorBarStart, colorBarEnd, colorValue, -1)

            for (faceletKey, facelet) in zip(face.keys(), face.values()):
                if facelet:
                    # Draw position rois on cube
                    for roi in facelet:
                        if len(roi):
                            start = roi[0]
                            lastPoint = start
                            for (i, point) in enumerate(roi):
                                cv2.circle(self.frame, point, 3, (0, 0, 0), -1)
                                cv2.line(self.frame, lastPoint, point, (0, 0, 0))
                                lastPoint = point
                            if isinstance(roi, tuple):
                                cv2.line(self.frame, lastPoint, start, (0, 0, 0))
                    # Fill facelet colot in color bar
                    color = self.faceletColor[faceKey][faceletKey]
                    if color:
                        if self.realColor:
                            colorValue = self.faceletBGR[faceKey][faceletKey]
                        else:
                            colorValue = self.colorValue[color]
                        if faceletKey >= 4:
                            faceletKey += 1
                        colorBarStart = self.offset(colorBarBase, divmod(faceletKey, 3)[::-1])
                        colorBarEnd = self.offset(colorBarBase, add2(divmod(faceletKey, 3)[::-1], (1, 1)))
                        cv2.rectangle(self.frame, colorBarStart, colorBarEnd, colorValue, -1)

        # Face outline
        cv2.rectangle(self.frame, baseAll["L"], self.offset(baseAll["B"], 3, 3), (0, 0, 0), 1)
        cv2.rectangle(self.frame, baseAll["U"], self.offset(baseAll["D"], 3, 3), (0, 0, 0), 1)
        cv2.rectangle(self.frame, baseAll["R"], self.offset(baseAll["R"], 3, 3), (0, 0, 0), 1)

        # Facelet outline
        cv2.rectangle(self.frame, self.offset(baseAll["L"], 1, 0), self.offset(baseAll["L"], 2, 3), (0, 0, 0), 1)
        cv2.rectangle(self.frame, self.offset(baseAll["U"], 1, 0), self.offset(baseAll["D"], 2, 3), (0, 0, 0), 1)
        cv2.rectangle(self.frame, self.offset(baseAll["R"], 1, 0), self.offset(baseAll["R"], 2, 3), (0, 0, 0), 1)
        cv2.rectangle(self.frame, self.offset(baseAll["B"], 1, 0), self.offset(baseAll["B"], 2, 3), (0, 0, 0), 1)

        cv2.rectangle(self.frame, self.offset(baseAll["U"], 0, 1), self.offset(baseAll["U"], 3, 2), (0, 0, 0), 1)
        cv2.rectangle(self.frame, self.offset(baseAll["L"], 0, 1), self.offset(baseAll["B"], 3, 2), (0, 0, 0), 1)
        cv2.rectangle(self.frame, self.offset(baseAll["D"], 0, 1), self.offset(baseAll["D"], 3, 2), (0, 0, 0), 1)

        # Double thickness the edge of setting facelet
        faceletToSet = self.faceletToSet.copy()
        faceletBase = self.baseAll[self.face[faceletToSet[0]]]
        if faceletToSet[1] >= 4:
            faceletToSet[1] += 1
        faceletStart = self.offset(faceletBase, divmod(faceletToSet[1], 3)[::-1])
        faceletEnd = self.offset(faceletBase, add2(divmod(faceletToSet[1], 3)[::-1], (1, 1)))
        cv2.rectangle(self.frame, faceletStart, faceletEnd, (0, 0, 0), 2)

        # Display and read next frame
        if self.display:
            cv2.imshow("Cube", self.frame)
        self.getFrame()

    def removePositionSetting(self):
        self.faceletToSet = [0, 0]
        for (faceKey, face) in zip(self.position.keys(), self.position.values()):
            for (pointKey, point) in zip(face.keys(), face.values()):
                self.position[faceKey][pointKey] = []
                # self.faceletHSV[faceKey][pointKey] = ()
                # self.faceletBGR[faceKey][pointKey] = ()

    def savePosition(self):
        print("Saving position...")
        numpy.save("position.npy", self.position)

    def loadPosition(self):
        if os.path.isfile("position.npy"):
            print("Loading position...")
            self.position = numpy.load("position.npy").item()
        else:
            print("No position file")

    def mouseCallback(self, event, x, y, flags, param):
        if self.debug and event != 0:
            print(event)
        if event == cv2.EVENT_MOUSEMOVE:
            self.lastPosition = (x, y)
            if x < 1280 and y < 480:
                self.hsv = (self.frameInHSV[y, x, 0], self.frameInHSV[y, x, 1], self.frameInHSV[y, x, 2])
        elif event == cv2.EVENT_LBUTTONDOWN:
            if (10 < x < 115 and 10 < y < 70) or (650 < x < 850 and 10 < y < 70):
                # "UP" or "DOWN": Exchange camera cap
                self.upCap, self.downCap = self.downCap, self.upCap
                self.removePositionSetting()
            elif 450 < x < 630 and 10 < y < 70:
                # RAND: Random moves
                self.randomMove()
            elif 1070 < x < 1270 and 10 < y < 70:
                # SOLVE: Going to solve the cube
                # TODO: check whether position info are all set
                self.ready = True
            elif (
                self.baseAll["L"][0] < x < self.baseAll["B"][0] + self.lenth * 3
                and self.baseAll["L"][1] < y < self.baseAll["B"][1] + self.lenth * 3
            ) or (
                self.baseAll["U"][0] < x < self.baseAll["D"][0] + self.lenth * 3
                and self.baseAll["U"][1] < y < self.baseAll["D"][1] + self.lenth * 3
            ):
                if len(self.facelet()) and isinstance(self.facelet()[-1], list):
                    # Setting facelet not finish, can't set another one
                    return
                # Going to set position info of another facelet
                # Not set by order, so it need to record last setting facelet
                if self.debug:
                    print(self.faceletToSet, self.faceletToSetLast)
                self.faceletToSetLast.append(self.faceletToSet.copy())
                self.clickColorBar(x, y)
                if self.debug:
                    print(self.faceletToSet, self.faceletToSetLast)
            else:
                # Not the special cases, click on cube
                if self.roiNotDone():
                    # TODO: Checking distance
                    # lastPoint = self.facelet()[-1][-1]
                    self.facelet()[-1].append((x, y))
                else:
                    self.facelet().append([(x, y)])
            if self.debug:
                print(event, ': EVENT_LBUTTONDOWN')
                print(self.position)
        elif event == cv2.EVENT_RBUTTONDOWN:
            if self.roiNotDone():
                # Remove a point in not finished ROI
                if len(self.facelet()[-1]) > 0:
                    self.facelet()[-1].pop()
            if self.debug:
                print(event, ': EVENT_RBUTTONDOWN')
                print(self.position)
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            roi = self.facelet().pop()
            if len(roi) > 3:
                # Complete a not finished ROI
                # ROI with at least 3 point
                # Double click will add the last point twice, remove one
                self.facelet().append(tuple(roi[:-1]))
            elif len(roi) == 2:
                # Move to next facelet
                # If len(roi) == 3, that means this roi only have two point, remove
                self.nextFacelet()
            if self.debug:
                print(event, ': EVENT_LBUTTONDBLCLK')
                print(self.position)
        elif event == cv2.EVENT_RBUTTONDBLCLK:
            # Remove last ROI
            if len(self.facelet()) > 0:
                self.facelet().pop()
            if self.debug:
                print(event, ': EVENT_RBUTTONDBLCLK')
                print(self.position)

    def facelet(self):
        return self.position[self.face[self.faceletToSet[0]]][self.faceletToSet[1]]

    def nextFacelet(self):
        if self.faceletToSetLast:
            self.faceletToSet = self.faceletToSetLast.pop()            
        else:
            self.faceletToSet[1] += 1
            if self.faceletToSet[1] == 8:
                self.faceletToSet[1] = 0
                self.faceletToSet[0] += 1
                if self.faceletToSet[0] == 6:
                    self.faceletToSet = [0, 0]
                    print("Ready to go!")
        self.detect()
        if len(self.Str) == 54:
            self.savePosition()

    def roiNotDone(self):
        # Last ROI is finish or not
        if len(self.facelet()) == 0 or isinstance(self.facelet()[-1], tuple):
            return False
        else:
            return True

    def clickColorBar(self, x, y):
        # Click on which face
        #   U
        # L F R B
        #   D
        # U0 R1 F2 D3 L4 B5"
        base = ()
        if x < self.baseAll["U"][0]:
            # In face L
            base = self.baseAll["L"]
            self.faceletToSet[0] = 4
        elif x < self.baseAll["R"][0]:
            # In face U F D
            if y < self.baseAll["F"][1]:
                # In face U
                base = self.baseAll["U"]
                self.faceletToSet[0] = 0
            elif y < self.baseAll["D"][1]:
                # In face F
                base = self.baseAll["F"]
                self.faceletToSet[0] = 2
            else:
                # In face D
                base = self.baseAll["D"]
                self.faceletToSet[0] = 3
        elif x < self.baseAll["B"][0]:
            # In face R
            base = self.baseAll["R"]
            self.faceletToSet[0] = 1
        else:
            # In face B
            base = self.baseAll["B"]
            self.faceletToSet[0] = 5

        # Click on which facelet
        # 0 1 2
        # 3 X 4
        # 5 6 7
        if x < base[0] + self.lenth:
            # Facelet 0 3 5
            if y < base[1] + self.lenth:
                # Facelet 0
                self.faceletToSet[1] = 0
            elif y < base[1] + self.lenth * 2:
                # Facelet 3
                self.faceletToSet[1] = 3
            else:
                # Facelet 5
                self.faceletToSet[1] = 5
        elif x < base[0] + self.lenth * 2:
            # Facelet 1 X 6
            if y < base[1] + self.lenth:
                # Facelet 1
                self.faceletToSet[1] = 1
            elif y < base[1] + self.lenth * 2:
                # Facelet X, ignore
                self.faceletToSet = self.faceletToSetLast.pop()
            else:
                # Facelet 6
                self.faceletToSet[1] = 6
        else:
            # In facelet 2 4 7
            if y < base[1] + self.lenth:
                # In facelet 2
                self.faceletToSet[1] = 2
            elif y < base[1] + self.lenth * 2:
                # In facelet 4
                self.faceletToSet[1] = 4
            else:
                # In facelet 7
                self.faceletToSet[1] = 7

    def color(self, hsv):
        if hsv[1] < 60: # or (hsv[1] < 80 and hsv[2] < 160):
            return "D"
        else:
            if hsv[0] < 10:
                return "F"
            elif hsv[0] < 18:
                return "B"
            elif hsv[0] < 50:
                return "U"
            elif hsv[0] < 90:
                return "R"
            else:
                return "L"

    def randomMove(self):
        randStr = ""
        for i in range(50):
            randStr += self.face[random.randint(0, 5)]
            randStr += str(random.randint(1, 3))
        print("*" + randStr + "*")
        self.move(randStr)
        
    def initMove(self):
        self.move("U1U3R1R3F1F3D1D3L1L3B1B3")

    def move(self, moves):
        if isinstance(moves, str):
            self.serial.write(moves.encode())
        if isinstance(moves, bytes):
            self.serial.write(moves)

    def offset(self, base, x, y=None):
        if isinstance(x, int):
            return add2(base, mul2((x, y), self.lenth))
        else:
            return add2(base, mul2(x, self.lenth))

    def main(self):
        # TODO: input buffer and command table
        if self.display:
            self.show()
            cv2.setMouseCallback("Cube", self.mouseCallback)
        self.loadPosition()
        while not self.stop:
            self.detect()
            if self.display:
                self.show()
            key = cv2.waitKey(30)
            if self.ready:
                self.startTime = time.time()
                self.solve()
                self.finishTime = time.time()
                print("Using time: ", self.finishTime - self.startTime)
                self.ready = False


if __name__ == "__main__":
    cube = Cube()
    cube.main()
