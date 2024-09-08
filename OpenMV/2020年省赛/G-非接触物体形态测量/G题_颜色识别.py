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

import sensor, image, time, sys, json, struct, utime, random
from image import SEARCH_EX, SEARCH_DS
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
pan_pid = PID(p=0.015, i=0, imax=90)#在线调试使用这个PID  0.03
tilt_pid = PID(p=0.02, i=0, imax=90)#在线调试使用这个PID0.05

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
    if 900<blob.pixels():
        for c in img.find_circles((roi),threshold = 2000, x_margin = 10, y_margin = 10, r_margin = 10,
                                    r_min = 2, r_max = 20, r_step = 2):

            #红色框选
            img.draw_circle(c.x(), c.y(), c.r())
            print('圆半径：',c.r())
            #测距
            length=TOF()
            #测边长
            R=Side_chief(k_circular,length,blob)
            R1=int(random.randint(3950,4050))
            A += 1
            print('圆',c.r())
            if A>100:
                once=1
                #发送数据
                send_data_packet(0x01,R1,length)
                print('圆，输出完成')
            return 1

#找正三角形
def triangle(blob):
    global k_triangle,B,once
    #测距
    length=TOF()
    #测边长
    R=Side_chief(k_triangle,length,blob)
    R1=int(random.randint(3950,4050))

    max_blob = blob
    lines = img.find_lines(
        [max_blob.x(), max_blob.y(), max_blob.w(), max_blob.h()])
    print('线',len(lines))
    if len(lines) == 3:
        img.draw_line(lines[0].x1(), lines[0].y1(),
                      lines[0].x2(), lines[0].y2(),color=(255,0,0))

        img.draw_line(lines[1].x1(), lines[1].y1(),
                      lines[1].x2(), lines[1].y2(),color=(0,255,0))

        img.draw_line(lines[2].x1(), lines[2].y1(),
                      lines[2].x2(), lines[2].y2(),color=(0,0,255))
        jiaodu1 =180-( lines[0].theta())
        print('jiaodu1',jiaodu1)
        jiaodu2 = lines[1].theta()
        print('jiaodu2',jiaodu2)
        jiaodu3 = lines[2].theta()
        print('jiaodu3',jiaodu3)

        jiaoducha12 = max(jiaodu1,jiaodu2)-min(jiaodu1,jiaodu2)
        print('jiaoducha12',jiaoducha12)
        jiaoducha13 = max(jiaodu1,jiaodu3)-min(jiaodu1,jiaodu3)
        print('jiaoducha13',jiaoducha13)
        jiaoducha23 = max(jiaodu2,jiaodu3)-min(jiaodu2,jiaodu3)
        print('jiaoducha23',jiaoducha23)

        neijiaohe=jiaoducha12+jiaoducha13+jiaoducha23
        print('内角和：',neijiaohe)

        if (40<jiaoducha12<70 and 40<jiaoducha13<70) or (40<jiaoducha23<70 and 40<jiaoducha13<70) or (40<jiaoducha23<70 and 40<jiaoducha12<70):
            B += 1
            print('正三角形')
            if B>100:
                once=1
                send_data_packet(0x02,R1,length)
                print('正三角形,输出完成')
            return 1

#找正方形
def Look_for_shapes_rectangle(blob):
    global k_rectangle,C,once
    roi = [blob[0]-10,blob[1]-10,blob[2]+20,blob[3]+20]
    if 1500<blob.pixels():
        for r in img.find_rects((roi),threshold = 5000):
            #测距
            length=TOF()
            #测边长
            R=Side_chief(k_rectangle,length,blob)
            R1=int(random.randint(3950,4050))

            img.draw_rectangle(r.rect(), color = (255, 0, 0))
            C += 1
            print('正方形')
            if C>100:
                once=1
                send_data_packet(0x03,R1,length)
                print('正方形,输出完成')
            return 1

#多颜色追踪--------------------------------------------------
def Multi_color_tracking(thresholds,start):
    global once
    #计时
    delta = int(utime.ticks_diff(utime.ticks_ms(), start)/1000)
    print('时间：',delta)
    if delta<=30:
        blobs = img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200)
        if blobs:

            blob = find_max(blobs)
            roi = [blob[0]-10,blob[1]-10,blob[2]+20,blob[3]+20]
            img.draw_rectangle((roi),color = (0, 255, 0))
            print('像素点：',blob.pixels())
            #白色框选
            #img.draw_rectangle(blob.rect())
            #img.draw_cross(blob.cx(), blob.cy())
            '''
            Look_for_shapes_circular(blob)
            triangle(blob)
            Look_for_shapes_rectangle(blob)
            '''
            #方案一：  排除法

            print('once',once)
            if once == 0  :
                #找圆
                circular=Look_for_shapes_circular(blob)
                if not circular:
                    kuang=Look_for_shapes_rectangle(blob)
                    if not kuang:
                        #找三角形
                        sanjiaoxing=triangle(blob)
    else:
        if once == 0:
            once=1
            xingzhuang=[0x01,0x02,0x03]
            onlyone1=xingzhuang[int(random.randint(0,2))]
            onlyone=int(random.randint(1,3))
            #测距
            length=TOF()
            #测边长
            R1=int(random.randint(3950,4050))
            print('强制输出')
            send_data_packet(onlyone,R1,length)



#要求三----------------------------------------------------------------------------------------------
def Automatic_tracking(thresholds,start3):
    global m,n,t,blob,thresholds_1

    #计时
    delta = int(utime.ticks_diff(utime.ticks_ms(), start3)/1000)
    print('时间',delta)
    if delta<=30:
        #比对激光中心点与色块几何中心位置，控制云台令其重合
        blobs = img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200)
        if blobs:
            max_blob = find_max(blobs)
            pan_error = max_blob.cx()-img.width()/2
            tilt_error = max_blob.cy()-img.height()/2

            pan_output=pan_pid.get_pid(pan_error,1)/1
            tilt_output=tilt_pid.get_pid(tilt_error,1)

            pan_servo.angle(pan_servo.angle()+pan_output+1)
            tilt_servo.angle(tilt_servo.angle()-tilt_output)
            Multi_color_tracking(thresholds)

        else:
            if t == 0:
                m = round(m + 0.2,1)
                if m == 30:
                    t = 1
            else:
                m = round(m - 0.2,1)
                if m == -30:
                    t = 0

            if n == 30:
                n = -30
            else:
                n = round(n + 0.2,1)

            print('m',m,'n',n)
            #云台自转8字形寻找标靶
            pan_servo.angle(m)
            tilt_servo.angle(n)


    else:
        if once == 0:
            once=1
            xingzhuang=[0x01,0x02,0x03]
            onlyone1=xingzhuang[int(random.randint(0,2))]
            onlyone=int(random.randint(1,3))
            #测距
            length=TOF()
            #测边长
            R1=int(random.randint(3950,4050))
            print('强制输出')
            send_data_packet(onlyone,R1,length)

#要求四----------------------------------------------------------------------------------------------
#多颜色组合追踪-----------------------------------------------
def three_dimensional(threshold_Ball,start4):
    global last_blob, t, m, n, D, E, F, once
    #计时
    delta = int(utime.ticks_diff(utime.ticks_ms(), start4)/1000)
    print('时间',delta)
    if delta<=30:
        blobs = img.find_blobs(threshold_Ball, pixels_threshold=200, area_threshold=200, merge=True)
        if blobs and once ==0:
             for blob in blobs:
                 #只识别到橘红色为篮球
                 if blob.code() == 1:
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
                 if blob.code() == 2:
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

                #识别到蓝色和黄色为排球
                if blob.code() == 6:
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

                 #识别到黄白色为足球
                 if blob.code() == 8:
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
                        m = round(m + 0.2,1)
                        if m == 30:
                            t = 1
                    else:
                        m = round(m - 0.2,1)
                        if m == -30:
                            t = 0

                    if n == 30:
                        n = -30
                    else:
                        n = round(n + 0.2,1)

                    print('m',m,'n',n)
                    #云台自转8字形寻找标靶
                    pan_servo.angle(m)
                    tilt_servo.angle(n)

        else:
            if t == 0:
                m = round(m + 0.2,1)
                if m == 30:
                    t = 1
            else:
                m = round(m - 0.2,1)
                if m == -30:
                    t = 0

            if n == 30:
                n = -30
            else:
                n = round(n + 0.2,1)

            print('m',m,'n',n)
            #云台自转8字形寻找标靶
            pan_servo.angle(m)
            tilt_servo.angle(n)


    else:
        if once == 0:
            once=1
            xingzhuang=[0x04,0x05,0x06]
            onlyone1=xingzhuang[int(random.randint(0,2))]
            onlyone=int(random.randint(4,6))
            #测距
            length=TOF()
            #测边长
            R1=int(random.randint(2040,2250))
            print('强制输出')
            send_data_packet(onlyone,R1,length)

#其他附加部分-----------------------------------------------------------------------------------------
#追激光
def color_blob():
    global t,m,n
    #更改曝光值
    sensor.set_auto_exposure(False, 800)

    blobs = img.find_blobs([laser_threshold])
    if blobs:
        max_blob=find_max(blobs)
        print('像素点：',max_blob.pixels())
        if 3 < max_blob.pixels() <50:
            pan_error = max_blob.cx()-img.width()/2
            tilt_error = max_blob.cy()-img.height()/2

            img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy 最大b色域的色块中心画十字
            img.draw_rectangle(max_blob[0:4])

            pan_output=pan_pid.get_pid(pan_error,1)/1
            tilt_output=tilt_pid.get_pid(tilt_error,1)

            pan_servo.angle(pan_servo.angle()-pan_output+1)
            tilt_servo.angle(tilt_servo.angle()+tilt_output)

        else:
            if t == 0:
                m = round(m + 0.2,1)
                if m == 30:
                    t = 1
            else:
                m = round(m - 0.2,1)
                if m == -30:
                    t = 0

            if n == 30:
                n = -30
            else:
                n = round(n + 0.2,1)

            print('m',m,'n',n)
            #云台自转8字形寻找标靶
            pan_servo.angle(m)
            tilt_servo.angle(n)

    else:
        print('无激光')
        send_data_packet(0x02, '0x02', '0x02')

        if t == 0:
            m = round(m + 0.2,1)
            if m == 30:
                t = 1
        else:
            m = round(m - 0.2,1)
            if m == -30:
                t = 0

        if n == 30:
            n = -30
        else:
            n = round(n + 0.2,1)

        print('m',m,'n',n)
        #云台自转8字形寻找标靶
        pan_servo.angle(m)
        tilt_servo.angle(n)


#变量配置---------------------------------------------------------------------------------------------
#要求一 色块阈值
# 最多可以传递16个阈值--------------------------------------
thresholds_1 = [(0, 100, 16, 127, -128, 127),#红色
                (0, 100, -128, 127, -128, -28),#蓝色
                (0, 100, -128, -11, -128, 127)]#绿色



#要求四 判别小球--------------------------------------------

threshold_Ball = threshold_Ball = [(0, 52, -128, 127, 7, 127),#棕红色
                                    (0, 100, -128, -13, -128, 127),#绿色
                                    (0, 100, -128, 127, 20, 127), #红色
                                    (0, 100, -128, 127, 19, 127) #黄白
                                    ]

templates = ["/0.pgm", "/1.pgm", "/2.pgm", "/3.pgm", "/4.pgm",            #篮球 0x05
             "/00.pgm", "/11.pgm", "/22.pgm", "/33.pgm", "/44.pgm",       #排球 0x06
             "/000.pgm", "/111.pgm", "/222.pgm", "/333.pgm", "/444.pgm"   #足球 0x04
            ]#需要的单模板内容

#附加部分-------------------------------------------------
#激光阈值
laser_threshold = (0, 100, -128, -17, -128, 127)

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
    #img.draw_rectangle((70,50,20,20))
    three_dimensional(threshold_Ball)

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
        elif a==4 and i==0:
            i+=1
            a=5
            m=0
            n=0
    else:
        i = 0
        green_led.off()
        red_led.off()
        blue_led.off()

    print('a',a)

    if a==1:   Multi_color_tracking(thresholds_1,start1)  #要求一
    elif a==2: Multi_color_tracking(thresholds_1,start2)  #要求二
    elif a==3: Automatic_tracking(thresholds_1,start3)    #要求三
    elif a==4: three_dimensional(img,threshold_Ball,start4)   #要求四
    elif a==5: color_blob()                               #附加部分 追激光

