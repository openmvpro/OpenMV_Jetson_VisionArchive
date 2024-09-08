from jetcam.csi_camera import CSICamera
import cv2
import numpy as np

camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=360)

def absdiff_demo(backgroundImg, currentImg, Threshold):
     gray_image_1 = cv2.cvtColor(backgroundImg, cv2.COLOR_BGR2GRAY)  #灰度化
     gray_image_1 = cv2.GaussianBlur(gray_image_1, (3, 3), 0)       #高斯滤波
     gray_image_2 = cv2.cvtColor(currentImg, cv2.COLOR_BGR2GRAY)
     gray_image_2 = cv2.GaussianBlur(gray_image_2, (3, 3), 0)
     d_frame = cv2.absdiff(gray_image_1, gray_image_2)
     ret, d_frame = cv2.threshold(d_frame, Threshold, 255, cv2.THRESH_BINARY)
     return d_frame

Threshold = 12 #sThre表示像素阈值
i = 0

# currentImg = np.ones((320,240),dtype=np.uint8)#random.random()方法后面不能加数据类型

while (True):
     image = camera.read()
     img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  #灰度化
     
     print(i)
      # 第一帧不处理
     if(i==0):
         i+=1
         currentImg = image
         backgroundImg = currentImg
         diffImg = absdiff_demo(backgroundImg, currentImg, Threshold)
     else:
         i+=1
         backgroundImg = currentImg
         currentImg = image
         diffImg = absdiff_demo(backgroundImg, currentImg, Threshold)

     # 把图像拼接在一起显示
     img_combine = np.hstack([img_gray, diffImg])

     cv2.imshow("CSI Camera", img_combine)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头
