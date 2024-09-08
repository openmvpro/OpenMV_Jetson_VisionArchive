#############################################################
#	修改时间：2019.7.26
#	文件功能：识别黑点
#	输    出： FormType		类型
#			  Loaction0		像素点x
#			  Location1		像素点y
#
#	备    注：
##############################################################
import sensor, image, time, network, usocket, sys
import math
from pyb import Pin, Timer, LED, UART


# LED灯定义
green_led = LED(1)
blue_led  = LED(2)




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


def FindMaxBlobs(BlobList):
    most_pixels = 0
    largest_blob = 0
    if BlobList:
        for i in range(len(BlobList)):
            if BlobList[i].pixels() > most_pixels:
                most_pixels = BlobList[i].pixels()
                largest_blob = i
        return BlobList[largest_blob]
    return None


sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)#设置灰度信息  #GRAYSCALE  #RGB565
sensor.set_framesize(sensor.QQVGA)#设置图像大小
sensor.set_brightness(3)    #设置相机图像亮度。-3至+3。
sensor.skip_frames(30)#相机自检几张图片
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False)#关闭白平衡 #若您想追踪颜色，则需关闭白平衡。
uart = UART(3, 115200)
clock = time.clock()#打开时钟

i = 0
Roi_BLACK = (5, 5, 150, 110)

black_threshold = [(0, 64)]
binary_threshold = [(0, 60)]        #60
##########################识别黑点##########
while(True):
    clock.tick()
    Cross_x = 0;
    Cross_y = 0;
    img = sensor.snapshot()

    #寻找blob
    blobs = img.find_blobs(black_threshold, roi=Roi_BLACK[0:4], merge=True)
    #img.binary(binary_threshold)
    if blobs:
        blackblob = FindMaxBlobs(blobs)

        Cross_x = int(blackblob.cx())
        Cross_y = int(blackblob.cy())

        img.draw_cross(Cross_x, Cross_y)
        img.draw_rectangle(blackblob.rect())

        print(50, Cross_x, Cross_y)
        uart.write(UART_Send(50, Cross_x, Cross_y))


    i+=1
    if i % 5 == 0:
        green_led.on()
        blue_led.on()
    if i % 10 == 0:
        green_led.off()
        blue_led.off()
    pass
