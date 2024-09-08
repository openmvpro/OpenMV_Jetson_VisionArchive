from jetcam.csi_camera import CSICamera
import numpy as np
import cv2

camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=360)
while (True):
     image = camera.read()

     #灰度
     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     #全局阈值
     #ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY |cv2.THRESH_OTSU)
     #ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_TRIANGLE)
     #ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)
     ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
     #局部阈值
     #binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 25, 10)

     cv2.imshow("CSI Camera", binary)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头