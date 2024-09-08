'''
正面从左到右
PCA9658-----Jetson Nano
1-----------2
2-----------1
3-----------3
4-----------5
6-----------6
'''

from adafruit_servokit import ServoKit
from jetcam.csi_camera import CSICamera
import numpy as np
import cv2

#选择通道
kit=ServoKit(channels=16)
#复位
pan=90
tilt =90
kit.servo[0].angle=pan
kit.servo[1].angle=tilt 

font = cv2.FONT_HERSHEY_SIMPLEX
lower_green = np.array([35, 110, 106]) # 绿色范围低阈值
upper_green = np.array([77, 255, 255]) # 绿色范围高阈值
#需要更多颜色,可以去百度一下HSV阈值!

width=640
height=360
camera = CSICamera(capture_device=0,capture_fps=90, width=width, height=height)
while (True):
    frame = camera.read()

    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_green = cv2.inRange(hsv_img, lower_green, upper_green) # 根据颜色范围删选
    mask_green = cv2.medianBlur(mask_green, 7) # 中值滤波
    contours, hierarchy = cv2.findContours(mask_green, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.putText(frame, "Green", (x, y - 5), font, 0.7, (0, 255, 0), 2)

        code_x = x + w/2
        code_y = y + h/2

        errorPan = code_x - width/2
        errorTilt = code_y - height/2

        if abs(errorPan)>15:#误差超过15像素调整
            pan=pan-errorPan/75#误差比例系数，具体自己调
        if abs(errorTilt)>15:
            tilt=tilt-errorTilt/75
 
        if pan>180:
            pan=180
            print("Pan Out of  Range")   
        if pan<0:
            pan=0
            print("Pan Out of  Range") 
        if tilt>180:
            tilt=180
            print("Tilt Out of  Range") 
        if tilt<0:
            tilt=0
            print("Tilt Out of  Range")                 
 
        kit.servo[0].angle=pan
        kit.servo[1].angle=tilt 

    cv2.imshow("CSI Camera", frame)
    keyCode = cv2.waitKey(1) & 0xFF
    if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头
