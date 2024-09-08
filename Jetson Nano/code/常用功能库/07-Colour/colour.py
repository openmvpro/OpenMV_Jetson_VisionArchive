from jetcam.csi_camera import CSICamera
import numpy as np
import cv2

font = cv2.FONT_HERSHEY_SIMPLEX
lower_green = np.array([35, 110, 106]) # 绿色范围低阈值
upper_green = np.array([77, 255, 255]) # 绿色范围高阈值
lower_red = np.array([0, 127, 128]) # 红色范围低阈值
upper_red = np.array([10, 255, 255]) # 红色范围高阈值
#需要更多颜色,可以去百度一下HSV阈值!

camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=360)
while (True):
    frame = camera.read()

    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask_green = cv2.inRange(hsv_img, lower_green, upper_green) # 根据颜色范围删选
    mask_red = cv2.inRange(hsv_img, lower_red, upper_red)
    # 根据颜色范围删选
    mask_green = cv2.medianBlur(mask_green, 7) # 中值滤波
    mask_red = cv2.medianBlur(mask_red, 7) # 中值滤波
    mask = cv2.bitwise_or(mask_green, mask_red)
    contours, hierarchy = cv2.findContours(mask_green, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    contours2, hierarchy2 = cv2.findContours(mask_red, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.putText(frame, "Green", (x, y - 5), font, 0.7, (0, 255, 0), 2)
    for cnt2 in contours2:
        (x2, y2, w2, h2) = cv2.boundingRect(cnt2)
        cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (0, 255, 255), 2)
        cv2.putText(frame, "Red", (x2, y2 - 5), font, 0.7, (0, 0, 255), 2)

    cv2.imshow("CSI Camera", frame)
    keyCode = cv2.waitKey(1) & 0xFF
    if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头