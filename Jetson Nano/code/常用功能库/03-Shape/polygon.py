from jetcam.csi_camera import CSICamera
import cv2
import numpy as np

camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=360)
while (True):
     image = camera.read()

     # 把图片转换为灰度图
     img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     # 中值滤波
     img_mid = cv2.medianBlur(img_gray, 3)
     # 二值化
     ret,img_binary = cv2.threshold(img_mid, 125, 255, cv2.THRESH_BINARY_INV) #固 定 值 二 值 化 , 二 值 化 阈 值 125
     # img_binary = cv2. adaptiveThreshold (img_mid , 255 , cv2.ADAPTIVE_THRESH_MEAN_C ,cv2. THRESH_BINARY ,3 ,2)# 自 适 应 二 值 化
     # 搜 索 连 通 域
     print(cv2.findContours(img_binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE))
     
     contours,hierachy = cv2.findContours(img_binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
     # 连 通 域 逐 个 检 测
     for cnt in range(len(contours)):

         # 拟 合 度 参 数 设 置 , 系 数 可 修 改
         epsilon = 0.05 * cv2.arcLength(contours[cnt],True)
         # 多 边 形 拟 合
         approx = cv2.approxPolyDP(contours[cnt],epsilon,True)

         # 角 点 检 测
         corners = len(approx)
         # 计 算 面 积, 用 于 滤 去 面 积 过 大 或 过 小 的 连 通 域
         area = cv2.contourArea(contours[cnt])

         if area > 30: # 面 积 范 围 可 随 环 境 变 化 修 改
             # 利 用 图 形 矩 计 算 连 通 域 质 心
             mm = cv2.moments(contours[cnt])
             cx = int(mm['m10'] / mm['m00'])
             cy = int(mm['m01'] / mm['m00'])

             # 绘 制 质 心
             #cv2. circle (img_gray , (cx , cy), 3, 0, -1)

             # 检 测 角 点
             if corners == 3:
                 cv2.drawContours(img_gray,contours[cnt],-1,0,3)
                 cv2.putText(img_gray, "triangle ", (cx-30, cy), cv2.FONT_HERSHEY_PLAIN, 1.2, 255, 1)
             elif corners == 4:
                 cv2.drawContours(img_gray,contours[cnt],-1,0,3)
                 cv2.putText(img_gray, "square ", (cx-30, cy), cv2.FONT_HERSHEY_PLAIN, 1.2, 255, 1)
             elif corners == 5:
                 cv2.drawContours(img_gray,contours[cnt],-1,0,3)
                 cv2.putText(img_gray, "pentagon ", (cx-30, cy), cv2.FONT_HERSHEY_PLAIN, 1.2, 255, 1)
             elif corners == 6:
                 cv2.drawContours(img_gray,contours[cnt],-1,0,3)
                 cv2.putText(img_gray, "hexagon ", (cx-30, cy), cv2.FONT_HERSHEY_PLAIN, 1.2, 255, 1)

     img_combine = np.hstack([img_gray,img_binary])

     cv2.imshow("CSI Camera", img_combine)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头