import numpy as np
import cv2
from collections import deque




def draw_on_canvas(points, color, thickness):
    for i in range(len(points)):
        for j in range(1, len(points[i])):
            if points[i][j - 1] is None or points[i][j] is None:
                continue
            cv2.line(paintWindow, points[i][j - 1], points[i][j], color, thickness)
            cv2.line(frame, points[i][j - 1], points[i][j], color, thickness)
            


bpoints = [deque(maxlen=1024)] 
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]



blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0



kernel = np.ones((5, 5), np.uint8)



colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0



paintWindow = np.ones((471, 636, 3), dtype=np.uint8) * 255 
paintWindow = cv2.rectangle(paintWindow, (40, 1), (140, 65), (0, 0, 0), 2) 
paintWindow = cv2.rectangle(paintWindow, (160, 1), (255, 65), colors[0], -1)
paintWindow = cv2.rectangle(paintWindow, (275, 1), (370, 65), colors[1], -1)
paintWindow = cv2.rectangle(paintWindow, (390, 1), (485, 65), colors[2], -1)
paintWindow = cv2.rectangle(paintWindow, (505, 1), (600, 65), colors[3], -1)        
cv2.putText(paintWindow, "CLEAR", (49, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "BLUE", (185, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "GREEN", (298, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(paintWindow, "RED", (420, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)#here we have the coordinates for the text and its scale
cv2.putText(paintWindow, "YELLOW", (520, 33), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 2, cv2.LINE_AA)




cap = cv2.VideoCapture(0)



cv2.namedWindow("Color detectors")
cv2.createTrackbar("Upper Hue", "Color detectors", 140, 180, lambda x: None)
cv2.createTrackbar("Upper Saturation", "Color detectors", 255, 255, lambda x: None)
cv2.createTrackbar("Upper Value", "Color detectors", 204, 255, lambda x: None)
cv2.createTrackbar("Lower Hue", "Color detectors", 99, 180, lambda x: None)
cv2.createTrackbar("Lower Saturation", "Color detectors", 149, 255, lambda x: None)
cv2.createTrackbar("Lower Value", "Color detectors", 80, 255, lambda x: None)#moving these trackbars allows us to calibrate our values


while True:
    ret, frame = cap.read()
    if not ret:
        break

   
    frame = cv2.flip(frame, 1)

   
    paint_resized = cv2.resize(paintWindow, (frame.shape[1], frame.shape[0]))

    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)         

    
    u_hue = cv2.getTrackbarPos("Upper Hue", "Color detectors")
    u_saturation = cv2.getTrackbarPos("Upper Saturation", "Color detectors")
    u_value = cv2.getTrackbarPos("Upper Value", "Color detectors")
    l_hue = cv2.getTrackbarPos("Lower Hue", "Color detectors")
    l_saturation = cv2.getTrackbarPos("Lower Saturation", "Color detectors")
    l_value = cv2.getTrackbarPos("Lower Value", "Color detectors")

    
    upper_hsv = np.array([u_hue, u_saturation, u_value]) 
    lower_hsv = np.array([l_hue, l_saturation, l_value])

   
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
    mask = cv2.erode(mask, kernel, iterations=1) 
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1) 

    # find contours
    cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if len(cnts) > 0:
        # We need to find only the largest contour
        cnt = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)
        M = cv2.moments(cnt)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))#find average x contour and y contour by dividing with 0th moment

        # Check for button presses
        if center[1] <= 65:
            if 40 <= center[0] <= 140:  
                bpoints = [deque(maxlen=1024)]
                gpoints = [deque(maxlen=1024)]
                rpoints = [deque(maxlen=1024)]
                ypoints = [deque(maxlen=1024)]
                blue_index = green_index = red_index = yellow_index = 0
                paintWindow[67:, :, :] = 255
            elif 160 <= center[0] <= 255:
                colorIndex = 0  # Blue
            elif 275 <= center[0] <= 370:
                colorIndex = 1  # Green
            elif 390 <= center[0] <= 485:
                colorIndex = 2  # Red
            elif 505 <= center[0] <= 600:
                colorIndex = 3  # Yellow
        else:
            if colorIndex == 0:
                bpoints[blue_index].appendleft(center)
            elif colorIndex == 1:
                gpoints[green_index].appendleft(center)
            elif colorIndex == 2:
                rpoints[red_index].appendleft(center)
            elif colorIndex == 3:
                ypoints[yellow_index].appendleft(center)
    else:
        # Add a break in the drawing
        if colorIndex == 0:
            bpoints.append(deque(maxlen=1024))
            blue_index += 1
        elif colorIndex == 1:
            gpoints.append(deque(maxlen=1024))
            green_index += 1
        elif colorIndex == 2:
            rpoints.append(deque(maxlen=1024))
            red_index += 1
        elif colorIndex == 3:
            ypoints.append(deque(maxlen=1024))
            yellow_index += 1

    # Draw on canvas
    points = [bpoints, gpoints, rpoints, ypoints]
    for i in range(len(points)):
        draw_on_canvas(points[i], colors[i], 3)

    # Overlay the paint window on the webcam feed
    overlay = cv2.addWeighted(frame, 0.8, paint_resized, 0.2, 0)

    # Show windows
    cv2.imshow("Tracking", overlay)
    cv2.imshow("Paint", paintWindow)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()


