#省赛 D题
import sensor, image, time, json
from pyb import UART
from pyb import Pin

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 1000)
sensor.set_auto_gain(False)  # 必须关闭此功能，以防止图像冲洗…
sensor.set_auto_whitebal(False) # turn this off.

#色块识别
red_threshold = (4, 100, 12, 28, -9, 27)
green_threshold = (4, 100, -113, 127, -118, -33)
#red_threshold = (13, 100, 16, 126, -78, 7)
#green_threshold = (13, 100, -93, -10, 30, 117)
thresholds = [red_threshold,green_threshold]
#-----------------------------串口 start-----------------------------
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
flag = 0
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

#关闭白平衡。白平衡是默认开启的，在颜色识别中，需要关闭白平衡。
uart = UART(3, 115200)

#----------------------------串口 end----------------------------

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
        return max_blob
#----------------------------找颜色------------------------------
red_num = False
green_num = False
def blob_find(img):
    global red_num
    global green_num

    blob_red = img.find_blobs([red_threshold], pixels_threshold=500, area_threshold=100)
    if blob_red:
        blob_red_max = find_max(blob_red)
        red_num = True
        img.draw_rectangle(blob_red_max.rect())
        img.draw_cross(blob_red_max.cx(), blob_red_max.cy())
        print(blob_red_max.cx(), blob_red_max.cy())
        uart.write(UART_Send(91,blob_red_max.cx(),blob_red_max.cy()))
    else:
        red_num = False

    blob_green = img.find_blobs([green_threshold], pixels_threshold=500, area_threshold=100)
    if blob_green:
        blob_green_max = find_max(blob_green)
        green_num = True
        img.draw_rectangle(blob_green_max.rect())
        img.draw_cross(blob_green_max.cx(), blob_green_max.cy())
        print(blob_green_max.cx(), blob_green_max.cy())
        uart.write(UART_Send(93,blob_green_max.cx(),blob_green_max.cy()))
    else:
        green_num = False

    if red_num==True and green_num==True:
        uart.write(UART_Send(95,0,0))
        print(2)
    elif (red_num==True and green_num==True) or (red_num==False and green_num==True) or (red_num==True and green_num==False):
        print(1)
    else:
        uart.write(UART_Send(90,0,0))
        print(0)
#测距： 距离 = 一个常数/直径的像素
#就是先让杆距离摄像头10cm，打印出摄像头里直径的像素值，然后相乘，就得到了k的值！
K=5000#the value should be measured



while(True):
    img = sensor.snapshot()
    blob_find(img)










