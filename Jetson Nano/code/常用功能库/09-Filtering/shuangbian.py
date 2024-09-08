#从左到右分别是原图,直径为 7 的双边滤波,直径为 9 的双边滤波。可以看出,双
#边滤波的效果还是不错的,就是要消耗大量的计算资源。



from jetcam.csi_camera import CSICamera
import numpy as np
import cv2

camera = CSICamera(capture_device=0,capture_fps=90, width=320, height=240)
while (True):
     origin = camera.read()

     rows,cols,_ = origin.shape
     # 第 一 个 参 数 是 原 图 像, 第 二 个 参 数 是 窗 口 的 大 小
     img_dual1 = cv2.bilateralFilter(origin,7,120,120)
     img_dual2 = cv2.bilateralFilter(origin,9,120,120)
     img_combine = np.hstack([origin, img_dual1, img_dual2])

     cv2.imshow("CSI Camera", img_combine)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头