import cv2
 
# 设置gstreamer管道参数
def gstreamer_pipeline(
    capture_width=1280, #摄像头预捕获的图像宽度
    capture_height=720, #摄像头预捕获的图像高度
    display_width=1280, #窗口显示的图像宽度
    display_height=720, #窗口显示的图像高度
    imagerate=60,       #捕获帧率
    flip_method=0,      #是否旋转图像
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, imagerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            imagerate,
            flip_method,
            display_width,
            display_height,
        )
    )
 
 
if __name__ == "__main__":
    capture_width = 1280
    capture_height = 720
    display_width = 1280
    display_height = 720
    imagerate = 60
    flip_method = 0
 
    # 创建管道
    print(gstreamer_pipeline(capture_width,capture_height,display_width,display_height,imagerate,flip_method))
 
    #管道与视频流绑定
    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
 
    if cap.isOpened():
        window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
        
        # 逐帧显示
        while cv2.getWindowProperty("CSI Camera", 0) >= 0:
            print(1)
            ret_val, img = cap.read()
            cv2.imshow("CSI Camera", img)
 
            keyCode = cv2.waitKey(30) & 0xFF         
            if keyCode == 27:# ESC键退出
                break
 
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("打开摄像头失败")