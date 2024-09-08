####################################################################################################
#2020/11/8 18:24
#灭火机器人  V1.0
#功能：当P0接收到高电平时判断房间是否有火焰，并通过管脚P1发送高电平
####################################################################################################

from pyb import Pin, Timer, LED
import sensor, image, time, math, json,struct

#闪光灯定义-------------------------------------------------------------------------------------------
red_led	    = LED(1)
green_led   = LED(2)
blue_led	= LED(3)

#引脚'P0'高电平识别------------------------------------------------------------------------------------
pin0 = Pin('P0', Pin.IN, Pin.PULL_DOWN)#设置p_in为输入引脚，并开启下拉电阻
#引脚'P1'高电平标识找到火焰-----------------------------------------------------------------------------
pin1 = Pin('P1', Pin.OUT_PP)


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 30)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False) # turn this off.
#sensor.set_vflip(True)               #图像水平翻转
#sensor.set_hmirror(True)             #图像垂直翻转

#更改曝光值
sensor.set_auto_exposure(False, 700)

clock = time.clock()


def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

#初始定义的变量------------------------------------------------
#火焰阈值
laser_threshold = (34, 100, -128, 127, -128, 127)

while(True):
    clock.tick()

    #启动提示灯
    green_led. on()

    img = sensor.snapshot().lens_corr(1.8)

    if pin0.value():
        #白灯接收到高电平
        green_led.on()
        red_led.on()
        blue_led.on()

        blobs = img.find_blobs([laser_threshold])
        if blobs:
            blob=find_max(blobs)
            if 10 < blob.pixels():
                img.draw_rectangle(blob[0:4])
                pin1.high()
                print('OK')
        else:
            pin1.low()

    else:
        green_led.off()
        red_led.off()
        blue_led.off()
        print('无信号')
