from jetcam.csi_camera import CSICamera
import pyzbar.pyzbar as pyzbar
import cv2

camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=360)
while (True):
     image = camera.read()

     barcodes = pyzbar.decode(image)
     for barcode in barcodes:
         barcodeData = barcode.data.decode("utf-8")
         print(barcodeData)

         (x, y, w, h) = barcode.rect
         cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)

     cv2.imshow("CSI Camera", image)
     keyCode = cv2.waitKey(1) & 0xFF
     if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头