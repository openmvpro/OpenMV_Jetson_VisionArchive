from jetcam.csi_camera import CSICamera
import cv2

camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=360)
while (True):
     image = camera.read()
     cv2.imshow("CSI Camera", image)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头