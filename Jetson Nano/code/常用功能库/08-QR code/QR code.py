from jetcam.csi_camera import CSICamera
import cv2
from pyzbar import pyzbar
import numpy as np

camera = CSICamera(capture_device=0,capture_fps=90, width=640, height=360)
while (True):
    frame = camera.read()

    #start = time.time()
    #解码
    tests = pyzbar.decode(frame)
    #end = time.time()
    data = ""
    #遍历所有结果
    for test in tests:
        #获取data并准换到utf8编码
        testdata = test.data.decode('utf-8')
        #获取位置信息
        testpolygon = test.polygon
        if len(testpolygon) == 4:
            points =np.array([testpolygon[0],testpolygon[1],testpolygon[2],testpolygon[3]], np.int32)
            #在原图上标记出识别到的二维码
            cv2.polylines(frame, [points], 1, (0, 0, 255), 2)
        #在原图左上角打印出二维码内容
        cv2.putText(frame, testdata, (0,10), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0),1)
        #print(testdata, end-start, len(testpolygon))
        data = testdata + '\r\n'

    cv2.imshow("CSI Camera", frame)
    keyCode = cv2.waitKey(1) & 0xFF
    if keyCode == 27:# ESC键退出
        break
camera.release()#释放摄像头