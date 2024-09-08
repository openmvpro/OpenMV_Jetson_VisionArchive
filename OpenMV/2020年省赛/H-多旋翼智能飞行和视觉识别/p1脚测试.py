####################################################################################################
#2020/10/09 23:45pm
#版本1.0
#实现功能：
#1、找二维码并发送位置信息
#2、根据'P1'高低电平进行AprilTag标记跟踪
####################################################################################################

#模块导入--------------------------------------------------------------------------------------------
import sensor, image, time, sys, json
from pyb import UART
from pyb import Pin
from pyb import LED

#引脚'P2'高电平识别Apriltags--------------------------------------------------------------------------
pin0 = Pin('P0', Pin.IN, Pin.PULL_DOWN)#设置p_in为输入引脚，并开启上拉电阻


#闪光灯定义-------------------------------------------------------------------------------------------
red_led	 = LED(1)
green_led   = LED(2)
blue_led	= LED(3)

#感光元件定义-----------------------------------------------------------------------------------------
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(20)
sensor.set_auto_whitebal(True)
sensor.set_auto_gain(True)
#关闭白平衡。白平衡是默认开启的，在颜色识别中，需要关闭白平衡。
clock = time.clock() # Tracks FPS.

#拍照计数
i=0
#照片顺序
a=1


while(True):
    clock.tick()
    print('i',i)
    print('a',a)
    img = sensor.snapshot().lens_corr(1.8)
    print(clock.fps())

    if pin0.value():
        if a==1 and (i==0 or i==1 or i==2 or i==3 or i==4):
            if i==0:
                i+=1

            elif i==1:
                i+=1

            elif i==2:
                i+=1

            elif i==3:
                i+=1

            elif i==4:
                i+=1
                a=2

        elif a==2 and (i==0 or i==1 or i==2 or i==3 or i==4):
            if i==0:
                i+=1

            elif i==1:
                i+=1

            elif i==2:
                i+=1

            elif i==3:
                i+=1

            elif i==4:
                i+=1
                a=3


        elif a==3 and (i==0 or i==1 or i==2 or i==3 or i==4):
            if i==0:
                i+=1


            elif i==1:
                i+=1


            elif i==2:
                i+=1


            elif i==3:
                i+=1


            elif i==4:
                i+=1
                a=4


        elif a==4 and (i==0 or i==1 or i==2 or i==3 or i==4):
            if i==0:
                i+=1


            elif i==1:
                i+=1


            elif i==2:
                i+=1


            elif i==3:
                i+=1


            elif i==4:
                i+=1
                a=5


        elif a==5 and (i==0 or i==1 or i==2 or i==3 or i==4):
            if i==0:
                i+=1


            elif i==1:
                i+=1


            elif i==2:
                i+=1


            elif i==3:
                i+=1


            elif i==4:
                i+=1
                a=6
    else:
        i = 0
        green_led.off()
        red_led.off()
        blue_led.off()
