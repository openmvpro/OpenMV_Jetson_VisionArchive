from jetcam.csi_camera import CSICamera
import cv2
import apriltag
import numpy as np

camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=360)
detector = apriltag.Detector()

camera_para_mtx = np.array([[576.56511716,   0.        ,  376.48483532],
                                                                 [  0.        , 575.95185476, 238.84099889],
                                                                 [  0.        ,   0.        ,   1.        ]])
camera_para = (camera_para_mtx[0, 0], camera_para_mtx[1, 1], camera_para_mtx[0, 2], camera_para_mtx[2, 2])
while (True):
     image = camera.read()

     # 把图片转换为灰度图
     img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     # 中值滤波
     img_mid = cv2.medianBlur(img_gray, 3)
     # 二值化
     ret,img_binary = cv2.threshold(img_mid, 90, 255, cv2.THRESH_BINARY)
     # 全局二值化

     # img_binary = cv2. adaptiveThreshold (img_mid ,255 ,1 ,1 ,11 ,20)# 自 适 应 二值化
      # 识别二维码
     detections = detector.detect(img_binary)

     # 二 维 码 识 别 和 测 量 结 果
     for det in detections:
         # 计 算 二 维 码 位 姿 信 息 , tag_size 是 apriltag 的 物 理 尺 寸 , 边 长 4 厘 米
         pose_mtx, init_error, final_error = detector.detection_pose(det,camera_para, tag_size=4)
         x = pose_mtx[0][3]
         y = pose_mtx[1][3]
         z = pose_mtx[2][3]
         print(x,y,z)
     cv2.imshow("CSI Camera", img_binary)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头