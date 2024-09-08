#############################################################
#	修改时间：2019.7.24
#	文件功能：寻色块
#	输    出：FormType		类型
#			  Loaction0		像素点x
#			  Location1		像素点y
#
#	备    注：可以同时识别多种色块
##############################################################

import sensor, image, time
from pyb import UART
from pyb import LED
from pyb import Timer
# LED灯定义
red_led     = LED(1)
green_led   = LED(2)
blue_led    = LED(3)

#色块识别
red_threshold = (31, 49, 29, 60, 1, 45)
#yellow_threshold = (30, 51, -9, 18, 23, 54)
#green_threshold = (36, 52, -44, -11, 13, 42)
#blue_threshold = (14, 35, -6, 11, -38, -21)
#black_threshold = (7, 35, -8, 15, -10, 13)

#激光
Point = (44, 100, 17, 68, -21, 31)

red_blob = 1
black_blob = 2
green_blob = 2



def ExceptionVar(var):
    data = []
    data.append(0)
    data.append(0)

    if var == -1:
        data[0] = 0
        data[1] = 0
    else:
        data[0] = var & 0xFF
        data[1] = var >> 8
    return data

Frame_Cnt = 0
fCnt_tmp = [0,0]
def UART_Send(FormType, Loaction0, Location1):
    global Frame_Cnt
    global fCnt_tmp
    Frame_Head = [170,170]
    Frame_End = [85,85]
    fFormType_tmp = [FormType]
    Frame_Cnt += 1

    if Frame_Cnt > 65534 :
        FrameCnt = 0

    fHead = bytes(Frame_Head)

    fCnt_tmp[0] = Frame_Cnt & 0xFF
    fCnt_tmp[1] = Frame_Cnt >> 8
    fCnt = bytes(fCnt_tmp)

    fFormType = bytes(fFormType_tmp)
    fLoaction0 = bytes(ExceptionVar(Loaction0))
    fLoaction1 = bytes(ExceptionVar(Location1))
    fEnd = bytes(Frame_End)
    FrameBuffe = fHead + fCnt + fFormType + fLoaction0 + fLoaction1 + fEnd
    return FrameBuffe



sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((160,120))
sensor.skip_frames(30) # Let new settings take affect.
sensor.set_auto_whitebal(False)
sensor.set_auto_gain(False) # must be turned off for color tracking

#关闭白平衡。白平衡是默认开启的，在颜色识别中，需要关闭白平衡。
uart = UART(3, 115200)
clock = time.clock() # Tracks FPS.



i = 0

while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.
    flag = 0
    sum_pixels = 0
    #  pixels_threshold=100, area_threshold=100
    blobs = img.find_blobs([red_threshold], area_threshold=100, merge=True)

    # R91  G92  B93
    if blobs:
        for b in blobs:
            img.draw_rectangle(b[0:4]) # rect
            img.draw_cross(b[5], b[6]) # cx, cy

            #red_led.on()
            uart.write(UART_Send(91,b[5],b[6]))
            print("cx %d, cy %d" %(b[5], b[6]))
            flag += 1


    #img.lens_corr(1.0) # strength of 1.8 is good for the 2.8mm lens.

    #for code in img.find_qrcodes():
        #if code:
            #img.draw_rectangle(code.rect())

            #msg = code.payload()

            #print("msg: %s" %msg)

            #uart.write(UART_Send(2, px, py))


    print("%f" %(clock.fps()))



