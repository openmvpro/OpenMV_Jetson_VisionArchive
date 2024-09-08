from jetcam.csi_camera import CSICamera
import cv2

#MJPG编码
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
video = cv2.VideoWriter('01-Basics/video.avi', fourcc, 30.0, (640, 360))

camera = CSICamera(capture_device=0,capture_fps=30, width=640, height=360)
for i in range(1000):
    image = camera.read()
    cv2.imshow("CSI Camera", image)
    keyCode = cv2.waitKey(1) & 0xFF
    if keyCode == 27:# ESC键退出
        break    

    video.write(image)
camera.release()#释放摄像头