#在下面输入要追踪靶心的阈值
b=(0, 99, -128, -12, 127, 3)


import sensor, image, time, sys, json
from pyb import UART
from pyb import Servo
from pid import PID

pan_servo=Servo(1)
tilt_servo=Servo(2)

#pan_pid = PID(p=0.07, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#tilt_pid = PID(p=0.05, i=0, imax=90) #脱机运行或者禁用图像传输，使用这个PID
pan_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID
tilt_pid = PID(p=0.05, i=0, imax=90)#在线调试使用这个PID

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # must be this
sensor.set_framesize(sensor.QQQVGA) # must be this
sensor.skip_frames(time = 2000) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_hmirror(True)#水平方向翻转
sensor.set_vflip(True)#垂直方向翻转
clock = time.clock() # Tracks FPS.

uart = UART(3,115200)



def maxs(a,b):#两数取大
    return (((a+b)+abs(a-b))//2)

def mins(a,b):#两数取小
    return(((a-b)+abs(-a-b))//2)


m=-180#水平方向初始位
n=-180#垂直方向初始位
t=0

while(True):
    if t == 0:
        m = m + 1
        if m == 180:
            t = 1
    else:
        m = m - 1
        if m == -180:
            t = 0

    if n == 180:
        n = -180
    else:
        n = n + 1

    clock.tick() # Track elapsed milliseconds between snapshots().帧率
    img = sensor.snapshot().lens_corr(1.8) # Take a picture and return the image.

    #找到阈值为b的圆
    for c in img.find_circles(threshold = 2500, x_margin = 10, y_margin = 10, r_margin = 10,
            r_min = 2, r_max = 100, r_step = 2):  #threshold检测像素点大小，step渐增半径数
        area = (c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r())#area为识别到的圆的区域，即圆的外接矩形框 x,y为圆中心坐标
        statistics = img.get_statistics(roi=area)#像素颜色统计
        #(0,100,0,120,0,120)是红色的阈值，所以当区域内的众数（也就是最多的颜色），范围在这个阈值内，就说明是红色的圆。
        #l_mode()，a_mode()，b_mode()是L通道，A通道，B通道的众数。

        if mins(b[0],b[1])<statistics.l_mode()<maxs(b[0],b[1]) and mins(b[2],b[3])<statistics.a_mode()<maxs(b[2],b[3]) and mins(b[4],b[5])<statistics.b_mode()<maxs(b[4],b[5]):#if the circle is red
            #发送开启激光指令
            uart.write("begin\r\n")


            #识别到的b色域的圆用红色的圆框出来
            img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))

            #让云台追着靶心走
            # cx, cy 最大b色域的色块中心画红色十字
            img.draw_cross(c.x(), c.y(), color = (255, 0, 0))

            pan_error = c.x()-img.width()/2
            tilt_error = c.y()-img.height()/2

            pan_output=pan_pid.get_pid(pan_error,1)/2
            tilt_output=tilt_pid.get_pid(tilt_error,1)

            pan_servo.angle(pan_servo.angle()+pan_output)
            tilt_servo.angle(tilt_servo.angle()-tilt_output)

        else:
            #发送关闭激光指令
            uart.write("close\r\n")

            #云台自转8字形寻找标靶
            pan_output=pan_pid.get_pid(m,1)/2
            tilt_output=tilt_pid.get_pid(n,1)

            pan_servo.angle(pan_servo.angle()+pan_output)
            tilt_servo.angle(tilt_servo.angle()-tilt_output)
