from picamera.array import PiRGBArray
from picamera import PiCamera
from time import sleep
import sys
import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
camera = PiCamera() #Initializes the camera and grab a reference to the raw camera capture.

def objectDet(objType):
    #Takes an image and processes it subject to the objType input.
    sleep(1)
    camera.capture('/home/pi/Printrun/imag.jpg') #Captures the image.

    img = cv2.imread('imag.jpg', 0) #Sends the image to OpenCV to read for processing.
    img = cv2.medianBlur(img,5) #Blurs image for ease of information extraction.
    
    if objType == 'feedthrough': #If the object being detected is a feedthrough.
        img = img[220:370, 800:950] #Crops the image around where the feedthrough is.
        img_inv = ~img #Creates an inverted image.
        circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,2,100,param1=180,param2=40,minRadius=35,maxRadius=45); #Tries to draw a circle around the outer side of the feedthrough to confirm that it is present.
        if circles is None: #If no circle is drawn, no feedthrough is present.
            return 'No Feedthrough Detected.'
        else: #If a circle is drawn.
            circles = np.uint16(np.around(circles))
            circles2 = cv2.HoughCircles(img_inv,cv2.HOUGH_GRADIENT,2,100,param1=180,param2=25,minRadius=2,maxRadius=15); #Tries to draw a circle around the inner side of the feedthrough to determine dimensions.
            for i in circles[0,:]: #Draws the outer circle .   
                cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
                outerRad = i[2] #Saves the radius of the circle.
                
            if (outerRad < 50) & (outerRad > 35): #If the outer radius is within the required dimensions.
                if circles is None: #But no inner circle is drawn, then the feedthrough is incorrectly sized.
                    return 'Incorrect Size Feedthrough Detected.'
                else:
                    circles2 = np.uint16(np.around(circles2)) 
                    for i in circles2[0,:]: #Draw the inner circle
                        cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
                        innerRad = i[2] #Saves the radius of the circle.
                    if (innerRad > 12): #If the inner radius is greater than the minimum size.
                        return 'Correct Size Feedthrough Detected.' #Returns correct feedthrough.
                    else:
                        return 'Incorrect Size Feedthrough Detected.' #Otherwise returns incorrect feedthrough.
            else: #Otherwise, if a circle outside of the dimensions is detected, this corresponds to camera issue, and not a feedthrough.
                return 'No Feedthrough Detected.' #Returns no feedthrough detected.
    elif objType == 'preform': #If the object being detected is a preform. 
        img = img[180:400, 850:1100] #Crops the image around where the preform is.
        circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,2,100,param1=180,param2=40,minRadius=75,maxRadius=110); #Tries to draw a circle around the outer side of the preform to confirm that it is present.
        if circles is None: #If no circle is drawn, no preform is present.
            return 'No Preform Detected.'
        else: #Otherwise, a preform is detected.
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                cv2.circle(img,(i[0],i[1]),i[2],(0,255,0),2)
                outerRad = i[2]
            return 'Preform Detected.' #Returns preform detected.
    return
