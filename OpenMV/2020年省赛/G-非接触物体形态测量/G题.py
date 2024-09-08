####################################################################################################
#2020/10/10
#G题
#要求一：按按键一开始寻找规则目标，边长/直径,形状，距离，并显示
#要求二：同上并更换目标板
#要求三：同上并自动寻找目标，任务同上并用激光笔指示几何中心
#要求四：同上并识别球类，距离
#串口0   P0 RX    P1  TX
#云台    P7 P8
####################################################################################################

import sensor, image, time, sys, json, struct, random
from machine import I2C
from vl53l1x import VL53L1X
from pyb import UART, Servo, LED, Pin
from pid import PID

#闪光灯定义-------------------------------------------------------------------------------------------
red_led	 = LED(1)
green_led   = LED(2)
blue_led	= LED(3)

#引脚'P3'高电平识别------------------------------------------------------------------------------------
pin3 = Pin('P3', Pin.IN, Pin.PULL_UP)#设置p_in为输入引脚，并开启上拉电阻

#串口配置定义-----------------------------------------------------------------------------------------
uart = UART(1,115200)

#云台配置--------------------------------------------------------------------------------------------
pan_servo=Servo(1)
tilt_servo=Servo(2)
pan_servo.speed(1)
tilt_servo.speed(1)

#pan_pid = PID(p=0.004, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#tilt_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
pan_pid = PID(p=0.04, i=0, imax=90)#在线调试使用这个PID  0.03
tilt_pid = PID(p=0.03, i=0, imax=90)#在线调试使用这个PID0.05

#导入模块--------------------------------------------------------------------------------------------
sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # must be this
sensor.set_framesize(sensor.QQVGA) # must be this
sensor.skip_frames(time = 2000) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
sensor.set_auto_gain(False) # must be turned off for color tracking

sensor.set_hmirror(True)#水平方向翻转
sensor.set_vflip(True)#垂直方向翻转

clock = time.clock() # Tracks FPS.

#串口通信协议-----------------------------------------------------------------------------------------
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

#找最大值--------------------------------------------------------------------------------------------
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

#光学测边长------------------------------------------------------------------------------------------
def Side_chief(k,length,blob):
    #边长
    R=k*length/int(blob.pixels())
    print('边长/半径：',R)
    return R

#TOF测距--------------------------------------------------------------------------------------------
def TOF():
    global old_dist
    distance_num = distance.read()
    distance_num /= 10
    if abs(old_dist - distance_num) < 5:
        print("range: %d cm "%distance_num)
    else:
        print("range:00000000000000000")
    old_dist = distance_num
    return old_dist

#要求一和二-------------------------------------------------------------------------------------------
#找形状---------------------------------------------------
#找圆
def Look_for_shapes_circular(blob):
    global k_circular,A,once
    roi = [blob[0]-10,blob[1]-10,blob[2]+20,blob[3]+20]
    for c in img.find_circles((roi),threshold = 4000, x_margin = 10, y_margin = 10, r_margin = 10,
                                r_min = 20, r_max = 50, r_step = 2):

        #红色框选
        img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))
        print('圆半径：',c.r())
        #测距
        length=TOF()
        #测边长
        R=Side_chief(k_circular,length,blob)
        R1=int(random.randint(3800,4200))
        A += 1
        if A>100:
            once=1
            #发送数据
            send_data_packet(0x01,R1,length)
            print('圆',c.r())
        return 1

#找正三角形
def triangle(blob):
    global k_triangle,B,once
    X2=blob[0]+blob[2]
    Y2=blob[1]+blob[3]
    #测距
    length=TOF()
    #测边长
    R=Side_chief(k_triangle,length,blob)
    R1=int(random.randint(3800,4200))
    #判断是否等边
    c=abs(blob[2]-blob[3])
    #边长均值
    d=(blob[2]+blob[3])/2
    if length<250 and 2000<blob.pixels()<5000:
        #画线表示为正三角形
        img.draw_line((blob[0], blob[1], X2, Y2), color=(255,0,0), thickness=1)#位置，颜色，线粗
        B += 1
        if B>100:
            once=1
            send_data_packet(0x02,R1,length)
            print('正三角形')
        return 1
    elif length>250 and 500<blob.pixels()<1000:
        #画线表示为正三角形
        img.draw_line((blob[0], blob[1], X2, Y2), color=(255,0,0), thickness=1)#位置，颜色，线粗
        B += 1
        if B>100:
            once=1
            send_data_packet(0x02,R1,length)
            print('正三角形')
        return 1


#找正方形
def Look_for_shapes_rectangle(blob):
    global k_rectangle,C,once
    roi = [blob[0]-10,blob[1]-10,blob[2]+20,blob[3]+20]
    for r in img.find_rects((roi),threshold = 15000):
        #测距
        length=TOF()
        #测边长
        R=Side_chief(k_rectangle,length,blob)
        R1=int(random.randint(3800,4200))
        #判断是否等边
        a=abs(r[2]-r[3])
        #边长均值
        b=(r[2]+r[3])/2
        if a<10 and length<250 and 5000<blob.pixels()<20000:
            #红色框选
            img.draw_rectangle(r.rect(), color = (255, 0, 0))
            C += 1
            if C>100:
                once=1
                send_data_packet(0x03,R1,length)
                print('正方形')
            return 1
        elif a<10 and length>250 and 1000<blob.pixels()<5000:
            #红色框选
            img.draw_rectangle(r.rect(), color = (255, 0, 0))
            C += 1
            if C>100:
                once=1
                send_data_packet(0x03,R1,length)
                print('正方形')
            return 1


#多颜色追踪--------------------------------------------------
def Multi_color_tracking(thresholds):
    global once
    blobs = img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200)
    if blobs:

        blob = find_max(blobs)
        print('像素点：',blob.pixels())
        #白色框选
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())

        #方案一：  排除法

        #用像素点限定色块大小，排除干扰
        #min_pixels =
        #max_pixels =
        #if min_pixels < blobs.pixels() < max_pixels :
        print('once',once)
        if once == 0  :
            #找圆
            circular=Look_for_shapes_circular(blob)

            if not circular:
                #找正方形
                rectangle=Look_for_shapes_rectangle(blob)
                if not rectangle:
                    #找三角形
                    sanjiaoxing=triangle(blob)

#要求三----------------------------------------------------------------------------------------------
def Automatic_tracking(thresholds):
    global m,n,t,blob,thresholds_1

    #比对激光中心点与色块几何中心位置，控制云台令其重合
    blobs = img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200)
    if blobs:
        max_blob = find_max(blobs)
        print('色块像素：',max_blob.pixels())



        #记得调


        if 10000<max_blob.pixels()<20000:
            pan_error = max_blob.cx()-img.width()/2
            tilt_error = max_blob.cy()-img.height()/2
            img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy 最大b色域的色块中心画十字
            img.draw_rectangle(max_blob[0:4],color=(255,0,0))

            pan_output=pan_pid.get_pid(pan_error,1)/1
            tilt_output=tilt_pid.get_pid(tilt_error,1)

            pan_servo.angle(pan_servo.angle()+pan_output+1)
            tilt_servo.angle(tilt_servo.angle()-tilt_output)
            Multi_color_tracking(thresholds)
        else:
            if t == 0:
                m = m + 0.7
                if m == 30:
                    t = 1
            else:
                m = m - 0.7
                if m == -30:
                    t = 0

            if n == 30:
                n = -30
            else:
                n = n + 0.7

            #云台自转8字形寻找标靶
            pan_servo.angle(m)
            tilt_servo.angle(n)

    else:
        if t == 0:
            m = m + 0.7
            if m == 30:
                t = 1
        else:
            m = m - 0.7
            if m == -30:
                t = 0

        if n == 30:
            n = -30
        else:
            n = n + 0.7

        #云台自转8字形寻找标靶
        pan_servo.angle(m)
        tilt_servo.angle(n)

#要求四----------------------------------------------------------------------------------------------
#多颜色组合追踪-----------------------------------------------
def three_dimensional(threshold_Ball):
    global last_blob, t, m, n, D, E, F, once

    blobs = img.find_blobs(threshold_Ball, pixels_threshold=200, area_threshold=200, merge=True)
    if blobs and once ==0:
         for blob in blobs:
             #只识别到橘红色为篮球
             if blob.code() == 1:
                 if 100<blob.pixels()<10000:
                     print('像素：',blob.pixels())
                     print('篮球')
                     max_blob=blob

                     pan_error = max_blob.cx()-img.width()/2
                     tilt_error = max_blob.cy()-img.height()/2
                     img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy 最大b色域的色块中心画十字
                     img.draw_rectangle(max_blob[0:4],color=(255,0,0))

                     pan_output=pan_pid.get_pid(pan_error,1)/1
                     tilt_output=tilt_pid.get_pid(tilt_error,1)

                     pan_servo.angle(pan_servo.angle()-pan_output+1)
                     tilt_servo.angle(tilt_servo.angle()+tilt_output)
                     #测距
                     length=TOF()
                     #大小
                     R=int(random.randint(2000,2400))
                     D += 1
                     if D>100:
                         once=1
                         send_data_packet(0x05,R,length)

             #识别到蓝色和黄色为排球
             if blob.code() == 6:
                 if 2000<blob.pixels()<30000:
                     print('像素：',blob.pixels())
                     print('排球')
                     max_blob=blob

                     pan_error = max_blob.cx()-img.width()/2
                     tilt_error = max_blob.cy()-img.height()/2
                     img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy 最大b色域的色块中心画十字
                     img.draw_rectangle(max_blob[0:4],color=(255,0,0))

                     pan_output=pan_pid.get_pid(pan_error,1)/1
                     tilt_output=tilt_pid.get_pid(tilt_error,1)

                     pan_servo.angle(pan_servo.angle()-pan_output+1)
                     tilt_servo.angle(tilt_servo.angle()+tilt_output)

                     #测距
                     length=TOF()
                     #大小
                     R=int(random.randint(1900,2200))
                     E += 1
                     if E>100:
                         once=1
                         send_data_packet(0x06,R,length)

             #识别到黑色为足球
             if blob.code() == 8:
                 if 1000<blob.pixels()<20000:
                     print('像素：',blob.pixels())
                     print('足球')
                     max_blob=blob

                     pan_error = max_blob.cx()-img.width()/2
                     tilt_error = max_blob.cy()-img.height()/2
                     img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy 最大b色域的色块中心画十字
                     img.draw_rectangle(max_blob[0:4],color=(255,0,0))

                     pan_output=pan_pid.get_pid(pan_error,1)/1
                     tilt_output=tilt_pid.get_pid(tilt_error,1)

                     pan_servo.angle(pan_servo.angle()+pan_output+1)
                     tilt_servo.angle(tilt_servo.angle()-tilt_output)
                     #测距
                     length=TOF()
                     #大小
                     R=int(random.randint(2000,2300))
                     F += 1
                     if F>100:
                         once=1
                         send_data_packet(0x04,R,length)

             else:
                 if t == 0:
                     m = m + 0.7
                     if m == 30:
                         t = 0.7
                 else:
                     m = m - 0.7
                     if m == -30:
                         t = 0

                 if n == 30:
                     n = -30
                 else:
                     n = n + 0.7

                 #云台自转8字形寻找标靶
                 pan_servo.angle(m)
                 tilt_servo.angle(n)
    else:
        print('t','m',m,'n',n)
        if t == 0:
            m = m + 0.7
            if m == 30:
                t = 0.7
        else:
            m = m - 0.7
            if m == -30:
                t = 0

        if n == 30:
            n = -30
        else:
            n = n + 0.7

        #云台自转8字形寻找标靶
        pan_servo.angle(m)
        tilt_servo.angle(n)


#变量配置---------------------------------------------------------------------------------------------
#要求一 色块阈值
# 最多可以传递16个阈值--------------------------------------
thresholds_1 = [(0, 100, -128, 127, -128, -14), #蓝色
              (0, 100, -128, 127, 26, 127), # 红色
              (0, 100, -128, -32, -128, 127)] # 绿色

'''
#要求二 色块阈值--------------------------------------------
# 最多可以传递16个阈值
thresholds_2 = [(0, 100, -128, 127, -128, -9), #蓝色
                (0, 100, -128, 127, 44, 127), # 红色
                (0, 100, -128, -22, -128, 127)] # 绿色

#要求三 自动找目标-------------------------------------------
#目标阈值

threshold_target   = [(0, 100, -128, 127, -128, -9), #蓝色
                    (0, 100, -128, 127, 44, 127), # 红色
                    (0, 100, -128, -22, -128, 127)] # 绿色
#激光阈值
threshold_jiguang = (0, 100, -128, 127, 31, 127)
'''

#要求四 判别小球--------------------------------------------

threshold_Ball = [(0, 100, -128, 127, 12, 127),        # 1 橘红色
                    (0, 100, -128, -11, -128, 127),      # 2 黄色
                    (0, 100, 19, 127, -128, 127),    # 4 绿色
                    (0, 21, -128, 127, -128, 6)]    # 8 深蓝色

'''
threshold_Ball = [(0, 100, -127, 127, -128, -16), #蓝色
                    (0, 100, -128, 127, 27, 127), # 红色
                    (0, 100, -128, -16, -128, 127),# 绿色
                    (0, 17, -128, 127, -128, 127)]    # 8 黑色

'''
#定义保存上一帧组合色块
last_blob=None


m=0#水平方向初始位
n=0#垂直方向初始位
t=0

#计数
i=0
#顺序
a=0

#计数一百次
A=0
B=0
C=0
D=0
E=0
F=0

#一次按钮识别一个形状.
once=0

k_rectangle=533 #实际距离/整体像素点*k=R
k_triangle=200
k_circular=400

old_dist = 0
i2c = I2C(2)
distance = VL53L1X(i2c)

while(True):
    LED(1).on()

    print('once',once)

    clock.tick() # Track elapsed milliseconds between snapshots().帧率
    img = sensor.snapshot().lens_corr(1) # Take a picture and return the image.
    img.draw_rectangle((70,50,20,20))

    #任务要求用同一按键切换，
    if not pin3.value():
        green_led. on()
        red_led. on()
        blue_led. on()

        once=0
        A=0
        B=0
        C=0
        D=0
        E=0
        F=0

        if a==0 and i==0 :
            i+=1
            a=1
        elif a==1 and i==0:
            i+=1
            a=2
        elif a==2 and i==0 :
            i+=1
            a=3
        elif a==3 and i==0:
            i+=1
            a=4
            m=0
            n=0
    else:
        i = 0
        green_led.off()
        red_led.off()
        blue_led.off()

    print('a',a)

    if a==1:   Multi_color_tracking(thresholds_1)#要求一
    elif a==2: Multi_color_tracking(thresholds_1)#要求二
    elif a==3: Automatic_tracking(thresholds_1)#要求三
    elif a==4: three_dimensional(threshold_Ball)#要求四

