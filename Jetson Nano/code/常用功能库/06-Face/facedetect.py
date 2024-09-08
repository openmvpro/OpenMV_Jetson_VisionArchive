from jetcam.csi_camera import CSICamera
import cv2

camera = CSICamera(capture_device=0,capture_fps=5, width=640, height=360)

#加载口罩识别训练数据
classifier0=cv2.CascadeClassifier("/home/lgh/code/06-Face/HOG_SVM_DATA.xml")
#加载人脸识别训练数据
#classifier1=cv2.CascadeClassifier("/home/lgh/code/06-Face/haarcascade_frontalface_alt.xml")
#加载左眼睛识别训练数据
#classifier2=cv2.CascadeClassifier("/home/lgh/code/06-Face/haarcascade_lefteye_2splits.xml")
#加载右眼睛识别训练数据
#classifier3=cv2.CascadeClassifier("/home/lgh/code/06-Face/haarcascade_righteye_2splits.xml")

while (True):
     image = camera.read()

     #转换成灰度图像
     image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
     #直方图均衡化
     cv2.equalizeHist(image)
     #检测
     faceRects1 = classifier1.detectMultiScale(image, 1.2, 2,cv2.CASCADE_SCALE_IMAGE, (30,40))

     #在原图像上标出检测
     if len(faceRects1)>0:
         for faceRect in faceRects1:
             x,y,w,h=faceRect
             cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2, 8, 0)

     '''
     faceRects1 = classifier1.detectMultiScale(image, 1.2, 2,cv2.CASCADE_SCALE_IMAGE, (30,40))
     faceRects2 = classifier2.detectMultiScale(image, 1.2, 2,cv2.CASCADE_SCALE_IMAGE, (30,40))
     faceRects3 = classifier3.detectMultiScale(image, 1.2, 2,cv2.CASCADE_SCALE_IMAGE, (30,40))
     if len(faceRects1)>0:
         for faceRect in faceRects1:
             x,y,w,h=faceRect
             cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2, 8, 0)
     if len(faceRects2)>0:
         for faceRect in faceRects2:
             x,y,w,h=faceRect
             cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2, 8, 0)
     if len(faceRects3)>0:
         for faceRect in faceRects3:
             x,y,w,h=faceRect
             cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2, 8, 0)
     '''
     cv2.imshow("CSI Camera", image)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头