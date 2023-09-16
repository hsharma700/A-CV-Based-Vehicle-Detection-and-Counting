from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *

# cap = cv2.VideoCapture(0) #for webcam
# cap.set(3, 640)
# cap.set(4, 480)
cap = cv2.VideoCapture("../video/traffic1.mp4")


model = YOLO("../Yolo-Weights/yolov8m.pt")

classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat", "traffic light",
              "fire hydrant",
              "stop sign", "parking meter", "bench", "bird", "cat", "horse", "sheep", "cow", "elephant", "bear",
              "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "sports ball", "kite", "baseball bat", "baseball glove",
              "skateboard", "surfboard",
              "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
              "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed", "diningtable",
              "toilet", "tvmonitor", "laptop",
              "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
              "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush", ]

mask = cv2.imread("mask1.png")

#tracking
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

#line
limits = [150, 430, 1200, 430]
totalCount = []

while True:
    success, img = cap.read()
    imgRegion = cv2.bitwise_and(img, mask)
    results = model(imgRegion, stream=True)

    detections = np.empty((0, 5))

    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Bouding Box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            # cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),3)

            w, h = x2 - x1, y2 - y1
            # cvzone.cornerRect(img, (x1, y1, w, h),l=9,t=2)

            #confidence
            conf = math.floor(box.conf[0] * 100) / 100

            #class Name
            cls = int(box.cls[0])
            currentClass = classNames[cls]

            if currentClass == "car" or currentClass == "truck" and conf > 0.3:
                # cvzone.putTextRect(img, f'{classNames[cls]} {conf}', (max(0, x1), max(30, y1)),scale=0.6,thickness=1,offset=4)
                # cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=5)
                currentArray = np.array([x1,y1,x2,y2,conf])
                detections = np.vstack((detections,currentArray))

    resultsTracker = tracker.update(detections)
    cv2.line(img, (limits[0], limits[1]),(limits[2],limits[3]),(0,0,255),5)

    for result in resultsTracker:
        x1, y1, x2, y2, id = result
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        print(result)
        w, h = x2 - x1, y2 - y1
        cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=1, t=2, colorR=(0,255,0))
        cvzone.putTextRect(img, f'{int(id)}', (max(0, x1), max(30, y1)), scale=1, thickness=1,
                           offset=8)

        cx, cy = x1+w//2, y1+h//2
        cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

        if limits[0] < cx < limits[2] and limits[1]-10 < cy < limits[1]+20:
            if totalCount.count(id) == 0:
                totalCount.append(id)
                cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
                cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 5)

        cvzone.putTextRect(img, f' Count: {len(totalCount)}', (50, 50))

    cv2.imshow("Image", img)
    # cv2.imshow("ImageRegion", imgRegion)
    cv2.waitKey(1)