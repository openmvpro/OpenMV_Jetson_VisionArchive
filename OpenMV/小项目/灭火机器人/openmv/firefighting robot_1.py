'''
灭火机器人
阶段一：
1、先用云台寻找门口带颜色的带子
2、发送带子位置数据给32，追踪带子，引导车子进入房间
3、云台找蜡烛
4、发送蜡烛位置数据给32，追踪蜡烛，引导风扇启动
'''

'''
LED(1) 红
LED(2) 绿
LED(3) 蓝
LED(4) 两个红外
'''


#在下面输入要追踪的阈值
#门口带子阈值
a=(41, 84, -69, -5, 21, 80)
#蜡烛阈值
b=(0, 100, 11, 127, -18, 127)

import sensor, image, time, sys, json, struct, network, usocket
from pyb import UART, Servo, LED
from vl53l1x import VL53L1X
from machine import I2C
from pid import PID

pan_servo=Servo(1)
tilt_servo=Servo(2)

#pan_pid = PID(p=0.07, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#tilt_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
pan_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID
tilt_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID

#配置WIFI模块
SSID ='OPENMV_AP'    # Network SSID
KEY  ='1234567890'    # Network key (must be 10 chars)
HOST = ''           # Use first available interface
PORT = 8080         # Arbitrary non-privileged port
# 在AP模式下启动wlan模块。
wlan = network.WINC(mode=network.WINC.MODE_AP)
wlan.start_ap(SSID, key=KEY, security=wlan.WEP, channel=2)

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # must be this
sensor.set_framesize(sensor.QVGA) # must be this
sensor.skip_frames(time = 2000) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_brightness(0)
clock = time.clock() # Tracks FPS.

uart = UART(1,115200)

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

def send_data_packet(X,Y,Z):
    temp = struct.pack("<bbiiibb",
                         0xAA,
                         0xAE,
                         int(X),
                         int(Y),
                         int(Z),
                         0x0D,
                         0x0A)
    uart.write(temp)

def start_streaming(s):
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
                "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n" \
                "Cache-Control: no-cache\r\n" \
                "Pragma: no-cache\r\n\r\n")

    # FPS clock
    clock = time.clock()

    # 开始流媒体图像
    #注：禁用IDE预览以增加流式FPS。
    while (True):
        clock.tick() # Track elapsed milliseconds between snapshots().
        img = sensor.snapshot().lens_corr(1.8)

        functional()

        cframe = img.compressed(quality=35)
        header = "\r\n--openmv\r\n" \
                 "Content-Type: img/jpeg\r\n"\
                 "Content-Length:"+str(cframe.size())+"\r\n\r\n"
        client.send(header)
        client.send(cframe)

#WIFI模块
def WIFI():
    # 创建服务器套接字
    s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    try:
        # Bind and listen
        s.bind([HOST, PORT])
        s.listen(5)

        # 设置服务器套接字超时
        # 注意：由于WINC FW bug，如果客户端断开连接，服务器套接字必须
        # 关闭并重新打开。在这里使用超时关闭并重新创建套接字。
        s.settimeout(3)
        start_streaming(s)
    except OSError as e:
        s.close()
        print("socket error: ", e)
        #sys.print_exception(e)

def functional():
    LED(1).off()#红

    m=-90#水平方向初始位
    n=-90#垂直方向初始位
    t=0
    i=0

    #测距常数固定值
    K=3318
    total_pan_output=0
    length = 0

    blobs_a = img.find_blobs([a])
    blobs_b = img.find_blobs([b])

    #找带子
    if blobs_a:
        #找到带子指示灯
        #LED(2).on()#绿

        #控制云台锁定追踪
        max_blob_a = find_max(blobs_a)

        pan_error = max_blob_a.cx()-img.width()/2
        tilt_error = max_blob_a.cy()-img.height()/2

        img.draw_circle(int(max_blob_a.cx()), int(max_blob_a.cy()),int(max_blob_a.cyf()-max_blob_a.y()) , color = (204,255,204))
        img.draw_cross(max_blob_a.cx(), max_blob_a.cy(),color=(204,255,204)) # cx, cy

        pan_output=pan_pid.get_pid(pan_error,1)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)

        total_pan_output=pan_servo.angle()+pan_output
        total_tilt_output=tilt_servo.angle()-tilt_output

        pan_servo.angle(total_pan_output)
        tilt_servo.angle(total_tilt_output)

    #找蜡烛
    elif blobs_b:
        #找到蜡烛指示灯
        #LED(3).on()#蓝

        #控制云台锁定追踪
        max_blob_b = find_max(blobs_b)

        pan_error = max_blob_b.cx()-img.width()/2
        tilt_error = max_blob_b.cy()-img.height()/2

        img.draw_circle(int(max_blob_b.cx()), int(max_blob_b.cy()),int(max_blob_b.cyf()-max_blob_b.y()) , color = (255, 0, 0))
        img.draw_cross(max_blob_b.cx(), max_blob_b.cy(),color=(255,0,0)) # cx, cy

        pan_output=pan_pid.get_pid(pan_error,1)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)

        total_pan_output=pan_servo.angle()+pan_output
        total_tilt_output=tilt_servo.angle()-tilt_output

        pan_servo.angle(total_pan_output)
        tilt_servo.angle(total_tilt_output)


        #测量蜡烛距离
        img.draw_rectangle(max_blob_b[0:4]) # rect
        img.draw_cross(max_blob_b[5], max_blob_b[6]) # cx, cy
        Lm = (max_blob_b[2]+max_blob_b[3])/2
        length = K/Lm
        print(length)

    else:
        LED(1).off()
        LED(2).off()
        LED(3).off()

        if t == 0:
            m = m + 1
            if m == 90:
                t = 1
        else:
            m = m - 1
            if m == -90:
                t = 0

        if n == 90:
            n = -90
        else:
            n = n + 1

        #云台自转8字形寻找标靶
        pan_servo.angle(m)
        tilt_servo.angle(n)

    #距离蜡烛12cm~17cm发送启动风扇指令
    if 17<=length<=20:
        LED(1).on()#红
        state = 1
        #print(00,state,total_pan_output,length)
        send_data_packet(state,total_pan_output,length)
    else:
        state = 0
        send_data_packet(state,total_pan_output,length)
        #print(11,state,total_pan_output,length)

#引入TOF模块
def TOF():
    LED(1).off()#红

    #TOF
    i2c = I2C(2)
    distance = VL53L1X(i2c)

    m=-90#水平方向初始位
    n=-90#垂直方向初始位
    t=0
    i=0

    #测距常数固定值
    K=3318

    total_pan_output=0
    length = 0

    blobs_a = img.find_blobs([a])
    blobs_b = img.find_blobs([b])

    #找带子
    if blobs_a:
        #找到带子指示灯
        #LED(2).on()#绿

        #控制云台锁定追踪
        max_blob_a = find_max(blobs_a)

        pan_error = max_blob_a.cx()-img.width()/2
        tilt_error = max_blob_a.cy()-img.height()/2

        img.draw_circle(int(max_blob_a.cx()), int(max_blob_a.cy()),int(max_blob_a.cyf()-max_blob_a.y()) , color = (204,255,204))
        img.draw_cross(max_blob_a.cx(), max_blob_a.cy(),color=(204,255,204)) # cx, cy

        pan_output=pan_pid.get_pid(pan_error,1)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)

        total_pan_output=pan_servo.angle()+pan_output
        total_tilt_output=tilt_servo.angle()-tilt_output

        pan_servo.angle(total_pan_output)
        tilt_servo.angle(total_tilt_output)

    #找蜡烛
    elif blobs_b:
        #找到蜡烛指示灯
        #LED(3).on()#蓝

        #控制云台锁定追踪
        max_blob_b = find_max(blobs_b)

        pan_error = max_blob_b.cx()-img.width()/2
        tilt_error = max_blob_b.cy()-img.height()/2

        img.draw_circle(int(max_blob_b.cx()), int(max_blob_b.cy()),int(max_blob_b.cyf()-max_blob_b.y()) , color = (255, 0, 0))
        img.draw_cross(max_blob_b.cx(), max_blob_b.cy(),color=(255,0,0)) # cx, cy

        pan_output=pan_pid.get_pid(pan_error,1)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)

        total_pan_output=pan_servo.angle()+pan_output
        total_tilt_output=tilt_servo.angle()-tilt_output

        pan_servo.angle(total_pan_output)
        tilt_servo.angle(total_tilt_output)

    else:
        LED(1).off()
        LED(2).off()
        LED(3).off()

        if t == 0:
            m = m + 1
            if m == 90:
                t = 1
        else:
            m = m - 1
            if m == -90:
                t = 0

        if n == 90:
            n = -90
        else:
            n = n + 1

        #云台自转8字形寻找标靶
        pan_servo.angle(m)
        tilt_servo.angle(n)

    #距离蜡烛170mm~200mm发送启动风扇指令
    if 170<=distance.read()<=200:
        LED(1).on()#红
        state = 1
        print(22,state,total_pan_output,distance.read())
        send_data_packet(state,total_pan_output,distance.read())
    else:
        state = 0
        send_data_packet(state,total_pan_output,distance.read())
        print(11,state,total_pan_output,distance.read())


while(True):
    #板子启动指示灯
    #LED(1).on()#红

    clock.tick() # Track elapsed milliseconds between snapshots().帧率
    img = sensor.snapshot().lens_corr(1.8) # Take a picture and return the image.

    #print(distance.read())

    #引入功能模块
    functional()

    #引入TOF测距
    #TOF()

    #引入WIFI模块
    #WIFI()



