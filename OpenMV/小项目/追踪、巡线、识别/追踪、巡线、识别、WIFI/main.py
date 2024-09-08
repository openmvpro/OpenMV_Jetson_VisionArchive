#追踪、巡线、识别、WIFI

#视频流浏览网址192.168.1.1:8080

# Blob Detection Example
#
# This example shows off how to use the find_blobs function to find color
# blobs in the image. This example in particular looks for dark green objects.


import sensor, image, time, network, usocket, sys, json
import car
from pid import PID
from pyb import LED

SSID ='OPENMV_AP'    # Network SSID
KEY  ='1234567890'    # Network key (must be 10 chars)
HOST = ''           # Use first available interface
PORT = 8080         # Arbitrary non-privileged port

sensor.reset() # Initialize the camera sensor.
sensor.set_contrast(1)
sensor.set_brightness(1)
sensor.set_saturation(1)
sensor.set_gainceiling(16)
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.skip_frames(100) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off. 要关闭白平衡，否则影响颜色追踪效果
sensor.set_vflip(True)#图像垂直翻转
sensor.set_hmirror(True)#图像水平翻转

clock = time.clock() # Tracks FPS.

# 在AP模式下启动wlan模块。
wlan = network.WINC(mode=network.WINC.MODE_AP)
wlan.start_ap(SSID, key=KEY, security=wlan.WEP, channel=2)

# For color tracking to work really well you should ideally be in a very, very,
# very, controlled enviroment where the lighting is constant...
#为了让颜色跟踪工作的很好，你最好是在一个非常，非常，
#非常可控的环境，那里的光线是恒定的。。。

#y=ax+b
rho_pid = PID(p=0.4, i=0)#类似于b  控制线在视野中的位置偏移
theta_pid = PID(p=0.001, i=0)#类似于a  调整线在视野中与底部的角度

#开灯补光稳定光源
LED(1).on()
LED(2).on()
LED(3).on()

#追踪线的阈值
THRESHOLD = (5, 70, -23, 15, -57, 0) # Grayscale threshold for dark things...
#追踪小球的阈值
green_threshold   = (76, 96, -110, -30, 8, 66)

size_threshold = 2000 #像素点面积阈值
x_pid = PID(p=0.5, i=1, imax=100)#方向PID 控制方向 改变p参数调整拐弯角度 p大越大
h_pid = PID(p=0.05, i=0.1, imax=50)#距离PID 控制速度 改变p参数调整速度 p大越大

def response(s):
    print ('Waiting for connections..')
    client, addr = s.accept()
    # 将客户端套接字超时设置为2秒
    client.settimeout(2.0)
    print ('Connected to ' + addr[0] + ':' + str(addr[1]))

    # 从客户端读取请求
    data = client.recv(1024)
    # 应该在这里解析客户端请求

    # 发送多部分head
    client.send("HTTP/1.1 200 OK\r\n" \
                "Server: OpenMV\r\n" \
                "Content-Type: application/json\r\n" \
                "Cache-Control: no-cache\r\n" \
                "Pragma: no-cache\r\n\r\n")

    # FPS clock
    clock = time.clock()

    # Start streaming images
    # NOTE: Disable IDE preview to increase streaming FPS.







    #追小球
    ball()

    #巡线
    #line()

    #扫码识别
    #distinguish()








    cframe = img.compressed(quality=35)
    header = "\r\n--openmv\r\n" \
             "Content-Type: img/jpeg\r\n"\
             "Content-Length:"+str(cframe.size())+"\r\n\r\n"
    client.send(header)
    client.send(cframe)

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

def ball():
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    blobs = img.find_blobs([green_threshold])
    #blobs的返回值为：
    #[{"x":104, "y":46, "w":48, "h":37, "pixels":1365, "cx":127, "cy":65, "rotation":3.033448, "code":1, "count":1, "perimeter":204, "roundness":0.675996}]
    #                                    像素数量        中心x坐标            色块的旋转弧度
    if blobs:
        max_blob = find_max(blobs)
        x_error = max_blob[5]-img.width()/2
        h_error = max_blob[2]*max_blob[3]-size_threshold
        print("x error: ", x_error)
        '''
        for b in blobs:
            # Draw a rect around the blob.
            img.draw_rectangle(b[0:4]) # rect
            img.draw_cross(b[5], b[6]) # cx, cy
        '''
        img.draw_rectangle(max_blob[0:4]) # rect 找到的色块画矩形
        img.draw_cross(max_blob[5], max_blob[6]) # cx, cy 找到的色块中心画十字
        x_output=x_pid.get_pid(x_error,1)
        h_output=h_pid.get_pid(h_error,1)
        print("h_output",h_output)
        car.run(-h_output-x_output,-h_output+x_output)
    else:
        car.run(10,-10)

def line():
    #小分辨率确保线性回归get_regression运算速度的保证
    sensor.set_framesize(sensor.QQQVGA) # use QQVGA for speed.

    clock.tick()
    img = sensor.snapshot().binary([THRESHOLD])#对获取的图片在设定的阈值内进行二值化分割
    line = img.get_regression([(100,100,0,0,0,0)], robust = True)
    if (line):
        rho_err = abs(line.rho())-img.width()/2  #计算返回的line与图像中央的偏移距离像素

        #对直线的坐标进行角度变换，以正y轴方向为0°，正x轴方向为90°
        if line.theta()>90:
            theta_err = line.theta()-180
        else:
            theta_err = line.theta()

        img.draw_line(line.line(), color = 127)#把线性回归返回的值画出来

        print(rho_err,line.magnitude(),rho_err)
        if line.magnitude()>8:  #返回的模越大线性效果越好
            #if -40<b_err<40 and -30<t_err<30:
            rho_output = rho_pid.get_pid(rho_err,1)
            theta_output = theta_pid.get_pid(theta_err,1)
            output = rho_output+theta_output
            car.run(50+output, 50-output)#以中央速度50位基准，可调整其速度
        else:
            car.run(0,0)
    else:
        car.run(50,-50)
        pass
    #print(clock.fps())

def distinguish():
    sensor.set_framesize(sensor.QVGA)    #增大分辨率提升扫码成功率

    img = sensor.snapshot()
    img.lens_corr(1.8) # strength of 1.8 is good for the 2.8mm lens.
    for code in img.find_qrcodes():
        print(code)

while(True):
    # Create server socket
    s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    try:
        # Bind and listen
        s.bind([HOST, PORT])
        s.listen(5)

        # Set server socket timeout
        # NOTE: Due to a WINC FW bug, the server socket must be closed and reopened if
        # the client disconnects. Use a timeout here to close and re-create the socket.
        s.settimeout(3)
        response(s)
    except OSError as e:
        s.close()
        print("socket error: ", e)
        #sys.print_exception(e)
