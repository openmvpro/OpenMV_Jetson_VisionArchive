from jetcam.csi_camera import CSICamera
import numpy as np
import cv2


# center定义
center = 320
camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=480)
while (True):
     frame = camera.read()
     cv2.imshow("recognize_face", frame) 
     # 转化为灰度图 
     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
     # 大津法二值化 
     retval, dst = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU) 
     # 膨胀，白区域变大 
     dst = cv2.dilate(dst, None, iterations=2) 
      # # 腐蚀，白区域变小 # 
     #dst = cv2.erode(dst, None, iterations=6) 
     # 单看第400行的像素值s 
     color = dst[400] 
     try:
        # 找到白色的像素点个数，如寻黑色，则改为0
        white_count = np.sum(color == 255)
        # 找到白色的像素点索引，如寻黑色，则改为0
        white_index = np.where(color == 255)
        # 防止white_count=0的报错
        if white_count == 0:
            white_count = 1
        # 找到黑色像素的中心点位置
        # 计算方法应该是边缘检测，计算白色边缘的位置和/2，即是白色的中央位置。
        center = (white_index[0][white_count - 1] + white_index[0][0]) / 2
        # 计算出center与标准中心点的偏移量，因为图像大小是640，因此标准中心是320，因此320不能改。
        direction = center - 320
        print(direction)
     except:
        continue



     cv2.imshow("CSI Camera", dst)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头