# Untitled - By: HQ - 周四 7月 25 2019
#############################################################
#	修改时间：2019.7.25
#	文件功能：摄像
#	输    出：空
#
#	备    注：注意路径
##############################################################

import sensor, image, time, pyb

from pyb import UART
from pyb import LED


# LED灯定义
red_led    = LED(1)
green_led  = LED(2)
blue_led   = LED(3)


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(30)
clock = time.clock()

record_time = 20000             # 10 seconds in milliseconds
cnt = 30
img_writer = image.ImageWriter("/Stream/stream.mp4")
flag_stop = 0
start = 0

while(True):
    cnt -= 1
    pyb.delay(100)

    if cnt == 0:
        break

    if cnt%5 == 0:
        red_led.on()
    if cnt%10 == 0:
        red_led.off()


while(True):
    clock.tick()
    cnt += 1

    if cnt == 1:
        print("start................")
        start = pyb.millis()#插件重置后，返回毫秒数。
        green_led.on()
        pass

    if pyb.elapsed_millis(start) < record_time:
        img = sensor.snapshot()
        img_writer.add_frame(img)
        print(clock.fps())
        flag_stop = 1
        green_led.off()
        pass

    else:
        if flag_stop == 1:
            img_writer.close()
            print("Done.......................")
            flag_stop = 0
            blue_led.on()
            pass








