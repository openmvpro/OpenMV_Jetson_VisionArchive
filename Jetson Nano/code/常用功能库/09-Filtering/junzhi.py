#从左到右分别是原图、5 × 5 的均值滤波、10 × 10 的均值滤波。可以看出,滤波器窗
#口越大,对噪声的滤除效果越好,但是图像也越模糊。



from jetcam.csi_camera import CSICamera
import numpy as np
import cv2

camera = CSICamera(capture_device=0,capture_fps=90, width=320, height=240)
while (True):
     origin = camera.read()

     rows,cols,_ = origin.shape
     # 第 一 个 参 数 是 原 图 像, 第 二 个 参 数 是 窗 口 的 大 小
     img_mean1 = cv2.blur(origin, (5,5))
     img_mean2 = cv2.blur(origin, (10,10))
     img_combine = np.hstack([origin, img_mean1, img_mean2])

     cv2.imshow("CSI Camera", img_combine)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头