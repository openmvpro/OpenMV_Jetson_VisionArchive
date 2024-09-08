#从左到右分别是原图,5 × 5 的中值滤波,9 × 9 的中值滤波。可以看出,相比于线性
#滤波,中值滤波对于椒盐噪声的照片滤除效果非常好,但是中值滤波需要消耗比高斯滤
#波更多的计算资源。
from jetcam.csi_camera import CSICamera
import numpy as np
import cv2

camera = CSICamera(capture_device=0,capture_fps=90, width=320, height=240)
while (True):
     origin = camera.read()
     rows,cols,_ = origin.shape
     # 第 一 个 参 数 是 原 图 像, 第 二 个 参 数 是 窗 口 的 大 小
     img_mid1 = cv2.medianBlur(origin, 5)
     img_mid2 = cv2.medianBlur(origin, 9)
     # 把图像拼接在一起显示
     img_combine = np.hstack([origin, img_mid1, img_mid2])

     cv2.imshow("CSI Camera", img_combine)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头