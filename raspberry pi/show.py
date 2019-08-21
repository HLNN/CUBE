import cv2

Cap1 = cv2.VideoCapture(0)
Cap2 = cv2.VideoCapture(2)

while 1:
    ret, frame1 = Cap1.read()
    ret, frame2 = Cap2.read()
    cv2.imshow('test1', frame1)
    cv2.imshow('test2', frame2)
    cv2.waitKey(30)