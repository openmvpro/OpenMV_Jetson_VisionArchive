# Untitled - By: HQ - 周五 7月 26 2019
#############################################################
#	修改时间：2019.7.24
#	文件功能：识别ApriTag
#	输    出：FormType		类型
#			  Loaction0		像素点x
#			  Location1		像素点y
#
#	备    注：
##############################################################

import sensor, image, time, network, usocket, sys
import math
from pyb import UART
from pyb import LED


# LED灯定义
green_led = LED(1)
blue_led  = LED(2)


def Find_Apriltags(img):
    X = -1
    Y = -1
    FormType = 0xff
    for tag in img.find_apriltags(families=image.TAG16H5):
        img.draw_rectangle(tag.rect(), color = (255, 0, 0))
        img.draw_cross(tag.cx(), tag.cy(), color = (0, 255, 0))
        X = tag.cx()
        Y = tag.cy()
        FormType = 100
    return FormType,X,Y

def IS_FindApriTag(img):
    GetApriTag = False

    for tag in img.find_apriltags(families=image.TAG16H5):
        GetApriTag = True

    return GetApriTag

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
    Location0_ = Loaction0
    Location1_ = Location1

    print(Loaction0, Location1)
    if Location0_ < 0:
        Location0_ = 0
    if Location1_ < 0:
        Location1_ = 0
    fLoaction0 = bytes(ExceptionVar(Loaction0))
    fLoaction1 = bytes(ExceptionVar(Location1))
    fEnd = bytes(Frame_End)
    FrameBuffe = fHead + fCnt + fFormType + fLoaction0 + fLoaction1 + fEnd
    return FrameBuffe

sensor.reset() # Initialize the camera sensor.
#sensor.set_vflip(True)
sensor.set_pixformat(sensor.GRAYSCALE) # use grayscale.
sensor.set_framesize(sensor.QQVGA) # use QVGA for speed. 160 * 120
sensor.skip_frames(30) # Let new settings take affect.
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
uart = UART(3, 115200)
clock = time.clock()
i = 0


while(True):
    clock.tick()
    img = sensor.snapshot()
    img.lens_corr(1.8)

    (Type,P0,P1) = Find_Apriltags(img)

    print(Type,P0,P1)
    uart.write(UART_Send(Type,P0,P1))

    print(clock.fps())
    i+=1
    if i % 5 == 0:
            blue_led.on()
    if i % 10 == 0:
            blue_led.off()


