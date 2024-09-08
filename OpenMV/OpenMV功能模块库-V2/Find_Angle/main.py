#############################################################
#	修改时间：2019.7.24
#	文件功能：巡曲线
#	输    出：FormType		类型
#			  Loaction0		x像素点
#			  Location1		需要转的角度
#
#	备    注：适合有头寻迹
##############################################################


import sensor, image, time, math
from pyb import UART
from pyb import LED


# LED灯定义
green_led  = LED(1)
blue_led   = LED(2)


#red_led = LED(1)
#green_led = LED(2)
#blue_led = LED(3)

GRAYSCALE_THRESHOLD = [(0, 64)]


ROIS = [
        #(10, 10, 140, 20, 0.7), # You'll need to tweak the weights for you app
        (10, 10, 140, 20), # depending on how your robot is setup.#60
        (10, 50, 140, 20)                                         #100
       ]

#计算权值和。遍历上面的三个矩形，r[4]即每个矩形的权值。
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


# Camera setup...

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # use grayscale.
#sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((160,120))
sensor.skip_frames(30) # Let new settings take affect.
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
uart = UART(3, 115200)
clock = time.clock() # Tracks FPS.8


i = 0

while(True):

    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.
    up_blob_x = 0
    up_blob_y = 0
    cur_blob_x = 0
    cur_blob_y = 0

    deflection_angle = 0
    flag = 0

    for r in ROIS:
        blobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi=r[0:4], merge=True)
        #找到视野中的线,merge=true,将找到的图像区域合并成一个
        if blobs:
            most_pixels = 0
            largest_blob = 0
            for i in range(len(blobs)):
                if blobs[i].pixels() > most_pixels:
                    most_pixels = blobs[i].pixels()
                    largest_blob = i

            flag += 1

            img.draw_rectangle(blobs[largest_blob].rect())
            img.draw_cross(blobs[largest_blob].cx(), blobs[largest_blob].cy())

            if blobs[largest_blob].cy() < 35:
                up_blob_x = blobs[largest_blob].cx()
                up_blob_y = blobs[largest_blob].cy()
            if blobs[largest_blob].cy() > 45 and blobs[largest_blob].cy() < 75:
                cur_blob_x = blobs[largest_blob].cx()
                cur_blob_y = blobs[largest_blob].cy()

    if flag == 2:
        px = up_blob_x - cur_blob_x
        py = up_blob_y - cur_blob_y

        Cen_angle = (px / py)
        deflection_angle = math.atan(Cen_angle)
        deflection_angle = math.degrees(deflection_angle)

        #将计算结果的弧度值转化为角度值
        print("Turn Angle: %f" % deflection_angle)
        return_angle = int(deflection_angle) + 90   #偏置
        uart.write(UART_Send(11, cur_blob_x, return_angle))
        #将结果打印在terminal中
        pass

    print(clock.fps())

    #green_led.on()
    blue_led.on()
