from jetcam.csi_camera import CSICamera
import cv2
import numpy as np


camera = CSICamera(capture_device=0,capture_fps=5, width=640, height=360)
while (True):
     image = camera.read()

     img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     img = cv2.medianBlur(img, 5)
     circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20, np.array([]), 100, 50,10, 100)
     #print(circles)
     
     if len(circles.shape)==3:
         #print(circles)
         #print(circles.shape)
        
         a, b, c = circles.shape
         #print(str(circles))
         for i in range(b):
             cv2.circle(image, (circles[0][i][0], circles[0][i][1]), circles[0][i][2], (0, 0, 255), 3, cv2.LINE_AA)
             cv2.circle(image, (circles[0][i][0], circles[0][i][1]), 2, (0, 255, 0), 3, cv2.LINE_AA)  # draw center of circle
         
     cv2.imshow("CSI Camera", image)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头