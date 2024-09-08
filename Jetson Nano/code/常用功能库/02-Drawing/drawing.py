from jetcam.csi_camera import CSICamera
import cv2

camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=360)
while (True):
     image = camera.read()

     #画线,(0,0)到(100,100),蓝色,宽度3个像素点
     cv2.line(image, (0,0), (100,100), (255,0,0), 3)
     #矩形,设置左上顶点和右下顶点,红色,宽度1
     cv2.rectangle(image, (100,0), (200,100), (0,255,0), 1)
     #圆形,圆心,半径,颜色,宽度(-1表示填充)
     cv2.circle(image,(200,200),20,(0,0,255),-1)
     #椭圆,中心,(⻓轴,短轴),椭圆沿逆时针选择角度,椭圆沿顺时针方向起始角度和结束角度,颜色,宽度(-1表示填充)
     cv2.ellipse(image,(150,150),(100,50),0,0,360,(255,255,0),1)
     #字符串,内容,位置,字体,缩放,颜色,线宽度
     cv2.putText(image,'jester nano',(0,100), cv2.FONT_HERSHEY_PLAIN, 2,(255,255,255), 1)


     cv2.imshow("CSI Camera", image)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break

camera.release()#释放摄像头