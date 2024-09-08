# Untitled - By: LIANGGUANGHUA - 周六 10月 10 2020

import sensor, image, time
from pyb import Pin
from pyb import LED

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

# LED灯定义
red_led    = LED(1)
green_led  = LED(2)
blue_led   = LED(3)



pin1 = Pin('P1', Pin.IN, Pin.PULL_DOWN)#设置p_in为输入引脚，并开启上拉电阻


while(True):
    img = sensor.snapshot()

    #外部低电平开启任务
    if pin1.value():
        green_led.off()
        red_led.off()
        blue_led.off()
    else:
        green_led.on()
        red_led.on()
        blue_led.on()
        Port1 = False
