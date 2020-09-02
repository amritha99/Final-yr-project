import cv2
import numpy as np
import glob
import random
from tkinter import *
from tkinter import messagebox
import time
import os.path
import os

count=0

# Load Yolo
net = cv2.dnn.readNet("yolov3-obj_2400.weights", "yolov3-obj.cfg")

# Name custom object
classes = ["Helmet"]


#output path
path = '/Users/sreep/Desktop/project/helmet/'

# Images path
#images_path = glob.glob(r"C:\Users\sreep\OneDrive\Documents\flask_app\uploads\*.jpg")

layer_names = net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

#loading image
cap=cv2.VideoCapture("helmet.mp4") #0 for 1st webcam
font = cv2.FONT_HERSHEY_PLAIN
starting_time= time.time()
frame_id = 0

while True:
    _,frame= cap.read() # 
    frame_id+=1
    
    height,width,channels = frame.shape




# Insert here the path of your images
#random.shuffle(images_path)
# loop through all the images
#for img_path in images_path:
    # Loading image
    #img = cv2.imread(img_path)
    #img = cv2.resize(img, None, fx=0.4, fy=0.4)
    #height, width, channels = img.shape

    # Detecting objects
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (320, 320), (0, 0, 0), True, crop=False)

    net.setInput(blob)
    outs = net.forward(output_layers)

    # Showing informations on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.3:
                
                # Object detected
                print(class_id)
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.4, 0.6)
    print(indexes)
    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = colors[class_ids[i]]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), font, 1, color, 1)
    
    elapsed_time = time.time() - starting_time
    fps=frame_id/elapsed_time
    cv2.putText(frame,"FPS:"+str(round(fps,2)),(10,50),font,2,(0,0,0),1)

    #cv2.imshow("Image", frame)

    #frame_name=os.path.basename(path)             # trimm the path and give file name.
    #for i in range(len(boxes)):
    #if i in indexes:
    #if confidence >= 0.3:
    name= "/Users/sreep/Desktop/project/helmet/output/frame%d.jpg"%count
    cv2.imwrite(name, frame)     # writing to folder.
    count=count+1
    
    key = cv2.waitKey(0)
    if key == 27: #esc key stops the process
        break;
    
cap.release()
cv2.destroyAllWindows()
