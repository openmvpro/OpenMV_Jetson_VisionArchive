#从左到右分别是原图、5 × 5 的高斯滤波、9 × 9 的高斯滤波。可以看出,相比于均值
#滤波,高斯滤波考虑了全局信息,在达到与均值滤波差不多的去噪效果时依然有较好的
#边缘特性,但是高斯滤波要消耗更多的计算资源。

from jetcam.csi_camera import CSICamera
import numpy as np
import cv2

camera = CSICamera(capture_device=0,capture_fps=90, width=320, height=240)
while (True):
     origin = camera.read()
     rows,cols,_ = origin.shape
     # 第 一 个 参 数 是 原 图 像, 第 二 个 参 数 是 窗 口 的 大 小
     img_gauss1 = cv2.GaussianBlur(origin, (5, 5), 0)
     img_gauss2 = cv2.GaussianBlur(origin, (9, 9), 0)
     # 把图像拼接在一起显示
     img_combine = np.hstack([origin, img_gauss1, img_gauss2])

     cv2.imshow("CSI Camera", img_combine)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头