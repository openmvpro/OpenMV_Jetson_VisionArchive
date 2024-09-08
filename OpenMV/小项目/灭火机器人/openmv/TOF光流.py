# 通过mavlink实现光流
#
# 该脚本使用MAVLink协议向ArduPilot / PixHawk控制器发送光流检测，以使用您的OpenMV Cam进行位置控制。
#
# P1 = TXD   P4
# P0 = RXD   P5


import image, math, pyb, sensor, struct, time, pyb
from machine import I2C
from pyb import UART
from vl53l1x import VL53L1X

# TOF###############################################################################################
i2c = I2C(2)
distance = VL53L1X(i2c)

# 参数###############################################################################################
uart = UART(1, 115200)


# LED 控制###########################################################################################
led = pyb.LED(2) # Red LED = 1, Green LED = 2, Blue LED = 3, IR LEDs = 4.


#串口通信协议##########################################################################################
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
def UART_Send(FormType, Loaction0, Location1, Location2):
    global Frame_Cnt
    global fCnt_tmp
    Frame_Head = [170,170]
    Frame_End = [85,85]
    fFormType_tmp = [FormType]
    Frame_Cnt += 1
    print('Frame_Cnt:',Frame_Cnt)
    if Frame_Cnt > 65534 :
        FrameCnt = 0

    fHead = bytes(Frame_Head)

    fCnt_tmp[0] = Frame_Cnt & 0xFF
    fCnt_tmp[1] = Frame_Cnt >> 8
    fCnt = bytes(fCnt_tmp)
    print('fCnt:',fCnt)

    fFormType = bytes(fFormType_tmp)
    fLoaction0 = bytes(ExceptionVar(Loaction0))
    fLoaction1 = bytes(ExceptionVar(Location1))
    fLoaction2 = bytes(ExceptionVar(Location2))
    fEnd = bytes(Frame_End)
    FrameBuffe = fHead + fCnt + fFormType + fLoaction0 + fLoaction1 + fLoaction2 + fEnd
    return FrameBuffe


#方案三：TOF光学测距###################################################################################
def TOF(old_dist):
    distance_num = distance.read()
    distance_num /= 10
    if abs(old_dist - distance_num) < 5:
        print("range_OK: %d cm "%distance_num)
        print('异常变量：',ExceptionVar(int(distance_num)))
        print('字节后_OK：',bytes(ExceptionVar(int(distance_num))),'\n')
        uart.write(UART_Send(90, 0, 0, int(distance_num)))
    else:
        print("range: %d cm "%old_dist)
        print('异常变量：',ExceptionVar(int(old_dist)))
        print('字节后：',bytes(ExceptionVar(int(old_dist))))
        uart.write(UART_Send(90, 0, 0, int(old_dist)))
    return distance_num

sensor.reset()                      # 复位并初始化传感器。
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.B64X32) # 设置图像大小为64x32…(或64 x64)…B64X32
sensor.skip_frames(time = 2000)     # 等待设置生效。

old_dist = 0
while(True):
    pyb.LED(2).on()
    img = sensor.snapshot() # 拍一张照片，返回图像
    old_dist=TOF(old_dist)

