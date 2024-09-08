#############################################################
#	修改时间：2019.7.24
#	文件功能：巡线、识别ApriTag
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

# 宏定义区
GRAYSCALE_THRESHOLD = [(23, 72)]
MIN_PIXELS = 100
width = 80 * 2
height = 60 * 2
RectHeight = 20
MAX_PIXEL = 200

# 直线阈值定义
Line_Thr = 1000
Line_Theta_margin = 25
Line_Margin = 25
Line_Min_degree = 0
Line_Max_degree = 179

# 感兴趣区域定义
Roi_Top = (0, 0, width, RectHeight)                         #0,0 160,20
Roi_Botton = (0, height - RectHeight, width, RectHeight)    #0,120-20  160,20
Roi_Left = (0, 0, RectHeight, height)                       #0,0  20,120
Roi_Right = (width - RectHeight, 0, RectHeight, height)     #160-20,0  20,120
Rois = [Roi_Top,Roi_Botton,Roi_Left,Roi_Right]  #

# 直线阈值定义
right_angle_threshold = (70, 90)
Line_Thr = 2000
Line_Theta_margin = 25
Line_Margin = 25
Line_Min_degree = 0
Line_Max_degree = 179

def find_all_Line(img):
    Line_All = img.find_lines(threshold = Line_Thr, theta_margin = Line_Theta_margin, rho_margin = Line_Margin)
    return Line_All

def calculate_angle(line1, line2):
    # 利用四边形的角公式， 计算出直线夹角
    angle  = (180 - abs(line1.theta() - line2.theta()))
    if angle > 90:
        angle = 180 - angle
    return angle

def is_right_angle(line1, line2):
    global right_angle_threshold
    # 判断两个直线之间的夹角是否为直角
    angle = calculate_angle(line1, line2)

    if angle >= right_angle_threshold[0] and angle <=  right_angle_threshold[1]:
        # 判断在阈值范围内
        return True
    return False

def calculate_intersection(line1, line2):
    # 计算两条线的交点
    a1 = line1.y2() - line1.y1()
    b1 = line1.x1() - line1.x2()
    c1 = line1.x2()*line1.y1() - line1.x1()*line1.y2()

    a2 = line2.y2() - line2.y1()
    b2 = line2.x1() - line2.x2()
    c2 = line2.x2() * line2.y1() - line2.x1()*line2.y2()

    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:
        cross_x = int((b1*c2-b2*c1)/(a1*b2-a2*b1))
        cross_y = int((c1*a2-c2*a1)/(a1*b2-a2*b1))
        return (cross_x, cross_y)
    return (-1, -1)

# 此函数将所看到的线条整理成一个点或直线信息
def line_info_process(lines):
    Cross_X = -1
    Cross_Y = -1
    line_info_list = [0,0,0,0,0,0,0]
    line_info_list[0] = -1

    # 如果有两条直线，此处不严谨，应该多判定两条直线
    if len(lines) == 2:
        if is_right_angle(lines[0],lines[1]):
            Cross_X , Cross_Y = calculate_intersection(lines[0],lines[1])
            line_info_list[0] = 0
            line_info_list[1] = Cross_X
            line_info_list[2] = Cross_Y


    # 如果有一条直线
    if len(lines) == 1:
        if (lines[0].x1() == 0 and lines[0].x2() == 79) or (lines[0].x2() == 0 and lines[0].x1() == 79):
            # 横线
            line_info_list[0] = 1
            line_info_list[1] = lines[0].y1()
            line_info_list[2] = lines[0].y2()
            pass
        if (lines[0].y1() == 0 and lines[0].y2() == 59) or (lines[0].y2() == 0 and lines[0].y1() == 59):
            line_info_list[0] = 2
            line_info_list[1] = lines[0].x1()
            line_info_list[2] = lines[0].x2()
            pass

    return line_info_list

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

def ProcessImg(img):
    Blobs = []

    TopBlobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi = Roi_Top[0:4], merge=True)
    BottonBlobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi = Roi_Botton[0:4], merge=True)
    LeftBlobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi = Roi_Left[0:4], merge=True)
    RightBlobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi = Roi_Right[0:4], merge=True)

    Blobs.append(TopBlobs)
    Blobs.append(BottonBlobs)
    Blobs.append(LeftBlobs)
    Blobs.append(RightBlobs)

    return Blobs

def CalcVerticalCross(x0,y0,x1,y1,x2,y2):
    if y1 != y0:
        k1 = (y1 - y0)/(x1-x0)
        k2 = -1/k1
        x = (-k1*x0 + y0 +x2*k2 - y2)/(k2 - k1)
        y = k1 * x - k1*x0 + y0
        return x,y
    else:
        return x2,y1

def CalcCross(x0,y0,x1,y1,x2,y2,x3,y3):
    # 计算两条线的交点
    a1 = y1 - y0
    b1 = x0 - x1
    c1 = x1*y0 - x0*y1

    a2 = y3 - y2
    b2 = x2 - x3
    c2 = x3 * y2 - x2*y3

    if (a1 * b2 - a2 * b1) != 0 and (a2 * b1 - a1 * b2) != 0:
        cross_x = int((b1*c2-b2*c1)/(a1*b2-a2*b1))
        cross_y = int((c1*a2-c2*a1)/(a1*b2-a2*b1))
        return (cross_x, cross_y)
    return (-1, -1)

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

def GetRectMoreInfo_V(Rect):
    x0 = Rect.x() + Rect.w()/2
    y0 = Rect.y()
    x1 = Rect.x() + Rect.w()/2
    y1 = Rect.y() + Rect.h()
    return x0,x1,y0,y1
    pass

def GetRectMoreInfo_H(Rect):
    x0 = Rect.x() + Rect.w()/2
    y0 = Rect.y()
    x1 = Rect.x() + Rect.w()/2
    y1 = Rect.y() + Rect.h()
    return x0,x1,y0,y1
    pass

def GetLtype(x0):

    pass



BlobLocation = [[0, 0], [0, 0], [0, 0], [0, 0]]
Blobs = []
def RecognitionForm(Blobs,img):
    Top = 0
    Botton = 1
    Left = 2
    Right = 3
    cx = 0
    cy = 1
    MAX_WITH = 20
    MIN_WITH = 6
    MIN_HIGH = 6
    MAX_HIGH = 20

    FormType = 0xFF
    Loaction0 = 0
    Location1 = 0

    TopValid = False
    BottonValid = False
    LeftValid = False
    RightValid = False

    TopBlob = FindMaxBlobs(Blobs[0])
    BottonBlob = FindMaxBlobs(Blobs[1])
    LeftBlob = FindMaxBlobs(Blobs[2])
    RightBlob = FindMaxBlobs(Blobs[3])

    if TopBlob:
        if TopBlob.w() < MAX_WITH and TopBlob.h() > MIN_HIGH:
            BlobLocation[Top][cx] = TopBlob.cx()
            BlobLocation[Top][cy] = TopBlob.cy()
            img.draw_rectangle(TopBlob.rect())
            img.draw_cross(BlobLocation[Top][cx],BlobLocation[Top][cy])
        else:
            TopBlob = None

    if BottonBlob:
        if BottonBlob.w() < MAX_WITH and BottonBlob.h() > MIN_HIGH:
            BlobLocation[Botton][cx] = BottonBlob.cx()
            BlobLocation[Botton][cy] = BottonBlob.cy()
            img.draw_rectangle(BottonBlob.rect())
            img.draw_cross(BlobLocation[Botton][cx],BlobLocation[Botton][cy])
        else:
            BottonBlob = None
            pass

    if LeftBlob:
        if LeftBlob.w() > MIN_WITH and LeftBlob.h() < MAX_HIGH and LeftBlob.h() > MIN_HIGH:
            BlobLocation[Left][cx] = LeftBlob.cx()
            BlobLocation[Left][cy] = LeftBlob.cy()
            img.draw_rectangle(LeftBlob.rect())
            img.draw_cross(BlobLocation[Left][cx],BlobLocation[Left][cy])
        else:
            LeftBlob = None

    if RightBlob:
        if RightBlob.w() > MIN_WITH and RightBlob.h() < MAX_HIGH and RightBlob.h() > MIN_HIGH:

            BlobLocation[Right][cx] = RightBlob.cx()
            BlobLocation[Right][cy] = RightBlob.cy()
            img.draw_rectangle(RightBlob.rect())
            img.draw_cross(BlobLocation[Right][cx],BlobLocation[Right][cy])
        else:
            RightBlob = None

    if TopBlob:
        TopValid = True

    if BottonBlob:
        BottonValid = True

    if LeftBlob:
        LeftValid = True

    if RightBlob:
        RightValid = True

    # 竖线
    if TopValid and BottonValid and (not LeftValid) and (not RightValid):
        Loaction0 = (BlobLocation[Top][cx] + BlobLocation[Botton][cx])//2
        Location1 = BlobLocation[Botton][cy]//2
        FormType = 0

    # 横线
    if (not TopValid) and (not BottonValid) and LeftValid and RightValid:
        Loaction0 = BlobLocation[Right][cx]//2
        Location1 = (BlobLocation[Left][cy] + BlobLocation[Right][cy])//2
        FormType = 1

    # 十字
    if TopValid and BottonValid and LeftValid and RightValid:
        (Loaction0,Location1) = CalcCross(BlobLocation[Left][cx],BlobLocation[Left][cy],
                                          BlobLocation[Right][cx],BlobLocation[Right][cy],
                                          BlobLocation[Top][cx],BlobLocation[Top][cy],
                                          BlobLocation[Botton][cx],BlobLocation[Botton][cy])

        FormType = 2
        return FormType,Loaction0,Location1

    # T字型
    if (not TopValid) and BottonValid and LeftValid and RightValid:
        x,y = CalcVerticalCross(BlobLocation[Left][cx],BlobLocation[Left][cy],
                                BlobLocation[Right][cx],BlobLocation[Right][cy],
                                BlobLocation[Botton][cx],BlobLocation[Botton][cy])

        Loaction0 = int(x)
        Location1 = int(y)
        FormType = 3
        return FormType,Loaction0,Location1

    # 倒T字型
    if (TopValid) and (not BottonValid) and LeftValid and RightValid:
        x,y = CalcVerticalCross(BlobLocation[Left][cx],BlobLocation[Left][cy],
                                BlobLocation[Right][cx],BlobLocation[Right][cy],
                                BlobLocation[Top][cx],BlobLocation[Top][cy])
        Loaction0 = int(x)
        Location1 = int(y)

        FormType = 4
        return FormType,Loaction0,Location1

        # 粗略的检测，对YAW值要求严格
        # L字形
    if  TopValid and (not BottonValid) and (not LeftValid) and RightValid:
        FormType = 5
        return FormType,BlobLocation[Top][cx],BlobLocation[Right][cy]

        #    |
        #    |
        # ___|  字形
    if TopValid and (not BottonValid) and ( LeftValid) and (not RightValid):
        FormType = 6
        return FormType,BlobLocation[Top][cx],BlobLocation[Left][cy]
        pass

        #    ____
        #    |
        #    |  字形
        #    |
    if not TopValid and (BottonValid) and (not LeftValid) and (RightValid):
        FormType = 7
        return FormType,BlobLocation[Botton][cx],BlobLocation[Right][cy]


        #    ____
        #       |
        #       |  字形
        #       |
    if not TopValid and ( BottonValid) and ( LeftValid) and (not RightValid):
        FormType = 8
        return FormType,BlobLocation[Botton][cx],BlobLocation[Left][cy]
        pass

    return FormType,Loaction0,Location1


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
sensor.set_framesize(sensor.QQVGA) # use QVGA for speed. 80 * 60
sensor.skip_frames(30) # Let new settings take affect.
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False)
uart = UART(3, 115200)
clock = time.clock()
i = 0

while(True):
    img = sensor.snapshot()
    img.lens_corr(1.8)

    All_Line = find_all_Line(img)
    Line_Info = line_info_process(All_Line)

    (Type,P0,P1) = RecognitionForm(ProcessImg(img),img)

    if Line_Info[0] == 0:
        img.draw_circle(Line_Info[1],Line_Info[2], 3, color = 200, thickness = 2, fill = False)


    print(Type,P0,P1)
    uart.write(UART_Send(Type,P0,P1))

    i+=1
    if i % 5 == 0:
            blue_led.on()
    if i % 10 == 0:
            blue_led.off()


