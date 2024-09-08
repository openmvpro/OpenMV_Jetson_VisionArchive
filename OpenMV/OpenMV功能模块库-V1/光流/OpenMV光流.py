# 通过mavlink实现光流
#
# 该脚本使用MAVLink协议向ArduPilot / PixHawk控制器发送光流检测，以使用您的OpenMV Cam进行位置控制。
#
# P4 = TXD

import image, math, pyb, sensor, struct, time, pyb
from machine import I2C
from vl53l1x import VL53L1X

# TOF#################################################################
i2c = I2C(2)
distance = VL53L1X(i2c)

# 参数#################################################################

MAV_system_id = 1
MAV_component_id = 0x54
MAV_OPTICAL_FLOW_confidence_threshold = 0.1
# 低于0.1左右（YMMV），结果只是噪音。

##############################################################################

# LED 控制
led = pyb.LED(2) # Red LED = 1, Green LED = 2, Blue LED = 3, IR LEDs = 4.
led_state = 0

def update_led():
    global led_state
    led_state = led_state + 1
    if led_state == 10:
        led.on()
    elif led_state >= 20:
        led.off()
        led_state = 0

# 链接设置

uart = pyb.UART(1, 115200, timeout_char = 1000)

# 辅助工作

packet_sequence = 0

def checksum(data, extra): # https://github.com/mavlink/c_library_v1/blob/master/checksum.h
    output = 0xFFFF
    for i in range(len(data)):
        tmp = data[i] ^ (output & 0xFF)
        tmp = (tmp ^ (tmp << 4)) & 0xFF
        output = ((output >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)) & 0xFFFF
    tmp = extra ^ (output & 0xFF)
    tmp = (tmp ^ (tmp << 4)) & 0xFF
    output = ((output >> 8) ^ (tmp << 8) ^ (tmp << 3) ^ (tmp >> 4)) & 0xFFFF
    return output

MAV_OPTICAL_FLOW_message_id = 100
MAV_OPTICAL_FLOW_id = 0 # unused
MAV_OPTICAL_FLOW_extra_crc = 175

# http://mavlink.org/messages/common#OPTICAL_FLOW
# https://github.com/mavlink/c_library_v1/blob/master/common/mavlink_msg_optical_flow.h
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
    FrameBuffe = fHead + fCnt + fFormType + fLoaction0 + fLoaction1 + fLoaction2 + fEnd
    return FrameBuffe

sensor.reset()                      # 复位并初始化传感器。

sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
#设置图像色彩格式，有RGB565色彩图和GRAYSCALE灰度图两种

sensor.set_framesize(sensor.B64X32) # 设置图像大小为64x32…(或64 x64)…B64X32

sensor.skip_frames(time = 2000)     # 等待设置生效。
clock = time.clock()                # 创建一个时钟对象来跟踪FPS帧率。

extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.RGB565)
extra_fb.replace(sensor.snapshot())

f = open('data.json','a+')
f.write('\n')
f.write('\n')
f.write('\n')
f.write('\n')
f.write('\n')
f.close()

while(True):
    pyb.LED(2).on()
    f = open('data.json','a+')
    clock.tick() # 追踪两个snapshots()之间经过的毫秒数.
    img = sensor.snapshot() # 拍一张照片，返回图像

    displacement = extra_fb.find_displacement(img)
    extra_fb.replace(img)

    # 没有滤波，偏移结果是嘈杂的，所以我们降低了一些精度。
    sub_pixel_x = int(-displacement.x_translation() * 35)
    #displacement.x_translation两个图像之间的x平移像素
    sub_pixel_y = int(displacement.y_translation() * 53)

    if(displacement.response() > MAV_OPTICAL_FLOW_confidence_threshold):
    #displacement.response两幅图像之间位移匹配结果的质量
        #send_optical_flow_packet(sub_pixel_x, sub_pixel_y, displacement.response())

        '''print(" {0:+f}x \n {1:+f}y \n {2} \n {3} ".format(sub_pixel_x, sub_pixel_y,
              displacement.response(),
              distance.read()))'''

    a = "x：{0:+f} y：{1:+f} z：{2:+f} 质量：{3} FPS: {4} ".format(sub_pixel_x, sub_pixel_y, distance.read(), displacement.response(), clock.fps())
    uart.write(UART_Send(90, sub_pixel_x, sub_pixel_y, distance.read()))
    f.write(str(a))
    f.write('\n')
    print(a)
    f.close()
