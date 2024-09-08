#############################################################
#	编写时间: 2019.8.7
#	文件功能: 2019年寻线机器人V1.0
#	内   容:  识别黄色，拍照条形码，识别蓝色，拍照二维码
#
#   修改时间: 2019.8.11
#   文件功能: 2019年寻线机器人V1.1
#   修改内容: 增加黄色识别不到，跳不出循环
#
#   修改时间: 2019.8.18
#   文件功能: 2019年寻线机器人V2.0
#   修改内容: 增加蓝色识别不到，识别二维码也能转头
#               增加P0开启信号，屏蔽起飞时间的外接干扰
##############################################################
import sensor, image, time, pyb
from pyb import UART
from pyb import LED
from pyb import Timer
from pyb import Pin

# LED灯定义
red_led    = LED(1)
green_led  = LED(2)
blue_led   = LED(3)



yellow_threshold = (30, 51, -9, 18, 23, 54)
blue_threshold   = (14, 35, -6, 11, -38, -21)
ROI = (10, 0, 140, 120)



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

def barcode_name(code):

    if(code.type() == image.EAN2):

        return "EAN2"

    if(code.type() == image.EAN5):

        return "EAN5"

    if(code.type() == image.EAN8):

        return "EAN8"

    if(code.type() == image.UPCE):

        return "UPCE"

    if(code.type() == image.ISBN10):

        return "ISBN10"

    if(code.type() == image.UPCA):

        return "UPCA"

    if(code.type() == image.EAN13):

        return "EAN13"

    if(code.type() == image.ISBN13):

        return "ISBN13"

    if(code.type() == image.I25):

        return "I25"

    if(code.type() == image.DATABAR):

        return "DATABAR"

    if(code.type() == image.DATABAR_EXP):

        return "DATABAR_EXP"

    if(code.type() == image.CODABAR):

        return "CODABAR"

    if(code.type() == image.CODE39):

        return "CODE39"

    if(code.type() == image.PDF417):

        return "PDF417"

    if(code.type() == image.CODE93):

        return "CODE93"

    if(code.type() == image.CODE128):

        return "CODE128"

###################################################


sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(30) # Let new settings take affect.
sensor.set_auto_whitebal(False)
sensor.set_auto_gain(False) # must be turned off for color tracking

uart = UART(3, 115200)
clock = time.clock()

#PIN0 = pyb.Pin(pyb.Pin.board.P0, pyb.Pin.IN)
pin0 = Pin('P0', Pin.IN, Pin.PULL_DOWN)#设置p_in为输入引脚，并开启上拉电阻

#起始信号
G_Flag = 0
i = 0
Port0 = False
while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    #外部低电平开启任务
    if pin0.value():
        Port0 = True
        pass

    if Port0:
        G_Flag = 1
        green_led.off()
        red_led.off()
        blue_led.off()
        break


    green_led.on()
    red_led.on()
    blue_led.on()




##########################################################
#
#                                       寻黄色异物 蓝色标杆
#
##########################################################
if G_Flag == 1:
    sensor.reset() # Initialize the camera sensor.
    sensor.set_pixformat(sensor.RGB565) # use RGB565.
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(10) # Let new settings take affect.
    sensor.set_auto_whitebal(False)
    sensor.set_auto_gain(False) # must be turned off for color tracking



blue_flag = 0
YT = (20, 10, 280, 220)
while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.
    sum_blobs = 0
    flag = 0
    qr_flag = 0
    for b in img.find_blobs([yellow_threshold, blue_threshold], roi=YT, area_threshold=80, merge=True):
        if b:
            #img.draw_rectangle(b[0:4]) # rect
            #img.draw_cross(b[5], b[6]) # cx, cy


            print("111  cx %d, cy %d" %(b[5], b[6]))
            sum_blobs += b.pixels()

            if b[8] == 1:
                flag += 1
               # break

            if b[8] == 2:
                blue_flag = 1
                pass

    if blue_flag == 1:
        uart.write(UART_Send(3, 0, 0))
        img.save("/QRCode1.jpg")
        G_Flag = 4
        break


    #if flag == 2 and sum_blobs > 60*60:
    if flag > 1 or sum_blobs > 60*60:
        uart.write(UART_Send(1,b[5],b[6]))
        img.save("/BarCode1.jpg")
        print("Bar111")
        G_Flag = 2
        green_led.on()
        uart.write(UART_Send(0, 0, 0))
        break



    img.lens_corr(1.0) # strength of 1.8 is good for the 2.8mm lens.

    for code in img.find_qrcodes():
        if code:
            img.draw_rectangle(code.rect())
            msg = code.payload()
            print("msg: %s" %msg)
            qr_flag = 1


    if qr_flag == 1:
        uart.write(UART_Send(2, 0, 0))
        img.save("/QRCode2.jpg")
        G_Flag = 5
        break


    print("%f" %(clock.fps()))




#########################################################################################
Count_num = 0
def Taking_Photo(tim4):
    global Count_num
    Count_num += 1
    pass

#########################################################################
#
#                                          拍条形码
#
####################################################################
# 条形码检测需要更高的分辨率才能正常工作，因此应始终以640x480的灰度运行。
if G_Flag == 2:
    sensor.reset() # Initialize the camera sensor.
    sensor.set_pixformat(sensor.GRAYSCALE) # use RGB565.
    sensor.set_framesize(sensor.VGA)
    sensor.skip_frames(10) # Let new settings take affect.
    sensor.set_auto_whitebal(False)
    sensor.set_auto_gain(False) # must be turned off for color tracking

tim4 = Timer(4)
tim4.init(freq=1)        #每秒一次
tim4.callback(Taking_Photo)



#########################################################################
while G_Flag == 2:
    clock.tick()
    img = sensor.snapshot()
    green_led.off()
    for code in img.find_barcodes():
        if code:
            #img.draw_rectangle(code.rect())

            msg = code.payload()
            print("msg: %s" %msg)

            #uart.write(UART_Send(1,code[5],code[6]))
            #print("222   cx %d, cy %d" %(code[5], code[6]))
            #BA_flag = 1
            img.save("/BarCode2.jpg")
            print("Bar222")



    if Count_num > 3:
        img.save("/BarCode3.jpg")
        print("Bar333")
        G_Flag = 3
        tim4.deinit()
        break


    i+=1
    if i % 5 == 0:
        blue_led.on()
    if i % 10 == 0:
        blue_led.off()
    pass



#######################################################


GRAYSCALE_THRESHOLD = [(67, 108)]



ROIS = [
        (100, 10, 120, 60), # depending on how your robot is setup.#60
        #(10, 50, 140, 20)                                         #100
        (100, 170, 120, 60)
       ]

RED_THREOLSD = (34, 54, 39, 62, 3, 42)
ROI = (100, 10, 120, 220)
###################################################
#
#                               寻蓝色杆子
#
####################################################

if G_Flag == 3:
    sensor.reset() # Initialize the camera sensor.
    sensor.set_pixformat(sensor.RGB565) # use grayscale.
    sensor.set_framesize(sensor.QVGA) #320*240
    #sensor.set_windowing((160,120))
    sensor.skip_frames(10) # Let new settings take affect.
    sensor.set_auto_gain(False) # must be turned off for color tracking
    sensor.set_auto_whitebal(False) # must be turned off for color tracking


####################
BLOB_flag = 0
BLOB_num = 0
BLOB_cnt = 0
########################
while G_Flag == 3:

    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    flag = 0
    Sum_pixel = 0
    for r in ROIS:
        #blobs = img.find_blobs(RED_THREOLSD, roi=r[0:4], merge=True)
        blobs = img.find_blobs([blue_threshold], roi=ROI, area_threshold=100, merge=True)
        #找到视野中的线,merge=true,将找到的图像区域合并成一个
        if blobs:
            most_pixels = 0
            largest_blob = 0
            for j in range(len(blobs)):
                if blobs[j].pixels() > most_pixels:
                    most_pixels = blobs[j].pixels()
                    largest_blob = j



            #img.draw_rectangle(blobs[largest_blob].rect())
            #img.draw_cross(blobs[largest_blob].cx(), blobs[largest_blob].cy())

            #if blobs[largest_blob].pixels() > 60*40/3:
            Sum_pixel += blobs[largest_blob].pixels()
            flag += 1



    #if  flag == 2 and Sum_pixel > 60*40:
    if flag != 0:
        uart.write(UART_Send(3, 0, 0))
        img.save("/QRCode1.jpg")
        print(i)
        blue_led.on()
        G_Flag = 4
        break
    #else:
        #uart.write(UART_Send(0, 0, 0))


    i+=1
    if i % 10 == 0:
        green_led.on()
        blue_led.on()
    if i % 20 == 0:
        green_led.off()
        blue_led.off()
    pass

#######################################
#
#                   拍二维码
#
#############################################
if G_Flag == 4:
    sensor.reset() # Initialize the camera sensor.
    sensor.set_pixformat(sensor.GRAYSCALE) # use RGB565.
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(10) # Let new settings take affect.
    sensor.set_auto_whitebal(False)
    sensor.set_auto_gain(False) # must be turned off for color tracking

QR_num = 0
QR_cnt = 0
QR_flag = 0
QR_fflag = 0
def Taking_Photo_P(tim3):
    global QR_cnt
    QR_cnt += 1
    pass


tim3 = Timer(3)
tim3.init(freq=1)        #每秒一次
tim3.callback(Taking_Photo_P)

##########################################################################
while(True):
    clock.tick()

    img = sensor.snapshot()

    img.lens_corr(1.0) # strength of 1.8 is good for the 2.8mm lens.

    for code in img.find_qrcodes():
        if code:
            #img.draw_rectangle(code.rect())

            px = code.x() + int(code.w()/2)
            py = code.y() + int(code.h()/2)

            msg = code.payload()

            print("msg: %s" %msg)

            uart.write(UART_Send(2, px, py))

            if QR_flag == 0:
                img.save("/QRCode2.jpg")
                print("222")
                uart.write(UART_Send(11, 0, 0))
            QR_flag = 1

    if QR_cnt == 1:
        uart.write(UART_Send(10, 0, 0))


    if QR_cnt == 4 and QR_fflag == 0:
        img.save("/QRCode3.jpg")
        print("333")
        uart.write(UART_Send(11, 0, 0))
        QR_fflag == 1

    if QR_cnt > 5:
        tim3.deinit()


    red_led.off()
    green_led.off()
    blue_led.off()
    pass

########################################################################
