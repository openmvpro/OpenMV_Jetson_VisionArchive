from jetcam.csi_camera import CSICamera
import cv2

camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=360)
image = camera.read()

cv2.imwrite("01-Basics/picture.jpg", image)

camera.release()#释放摄像头