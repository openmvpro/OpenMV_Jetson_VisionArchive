####################################################################################################
#2020/10/08 3:33am
#版本1.0
#实现功能：（无WIFI）
#追激光
#找色块
#找组合色块
#AprilTag标记跟踪
#找二维码
#巡线
####################################################################################################

#模块导入--------------------------------------------------------------------------------------------
import sensor, image, time, sys, json
from GeometryFeature import GeometryFeature
from pyb import UART
from pyb import LED
from pyb import Timer

#串口配置--------------------------------------------------------------------------------------------
uart = UART(3, 115200)

#闪光灯定义-------------------------------------------------------------------------------------------
red_led	 = LED(1)
green_led   = LED(2)
blue_led	= LED(3)

#感光元件定义-----------------------------------------------------------------------------------------
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(100)
sensor.set_auto_whitebal(False)
sensor.set_auto_gain(False)
#关闭白平衡。白平衡是默认开启的，在颜色识别中，需要关闭白平衡。
clock = time.clock() # Tracks FPS.

#传输协议--------------------------------------------------------------------------------------------
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

#追激光    48----------------------------------------------------------------------------------------
def color_blob(img):
    uart.write(UART_Send(1,0,0))
    sensor.set_auto_exposure(False, 700)#更改曝光值
    blobs = img.find_blobs([laser_threshold])
    if blobs:
        blob=find_max(blobs)
        print('总像素点',blob.pixels())
        if 20 < blob.pixels() <200:#像素点限定目标大小
            img.draw_rectangle(blob[0:4])
            cx = blob[5]
            cy = blob[6]
            img.draw_cross(blob[5], blob[6])
            uart.write(UART_Send(48,cx,cy))
    else:
        uart.write(UART_Send(90,0,0))

#找色块  红蓝绿   91 92 93----------------------------------------------------------------------------
def find_blob(img, flag):
    uart.write(UART_Send(1,0,0))
    if flag == 0:
        blobs = img.find_blobs([red_threshold],merge=True)
        if  blobs:
            r=find_max(blobs)
            print('红色像素点：',r.pixels())
            if 200<r.pixels()<4000:
                img.draw_rectangle(r[0:4])
                img.draw_cross(r[5], r[6])
                uart.write(UART_Send(91,r[5],r[6]))
                print("cx %d, cy %d" %(r[5], r[6]))
                if (120< r[5] <200)and (90< r[6] < 150):
                    flag += 1
        else:
            uart.write(UART_Send(90,0,0))
    if flag == 1:
        sum_pixels = 0
        blobs = img.find_blobs([blue_threshold],merge=True)
        if  blobs:
            b=find_max(blobs)
            print('蓝色像素点：',b.pixels())
            if 200<b.pixels()<4000:
                img.draw_rectangle(b[0:4])
                img.draw_cross(b[5], b[6])
                uart.write(UART_Send(92,b[5],b[6]))
                print("cx %d, cy %d" %(b[5], b[6]))
                if (120< b[5] <200)and (90< b[6] < 150):
                    flag += 1
        else:
            uart.write(UART_Send(90,0,0))
    if flag == 2:
        sum_pixels = 0
        blobs = img.find_blobs([green_threshold],merge=True)
        if  blobs:
            g=find_max(blobs)
            print('绿色像素点：',g.pixels())
            if 200<g.pixels()<4000:
                img.draw_rectangle(g[0:4])
                img.draw_cross(g[5], g[6])
                uart.write(UART_Send(93,g[5],g[6]))
                print("cx %d, cy %d" %(g[5], g[6]))
    print('flag:',flag)
    return flag

#找组合颜色  94---------------------------------------------------------------------------------------
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob
def Color_combination():
    img = sensor.snapshot().lens_corr(1.8)
    for blob in img.find_blobs(thresholds, pixels_threshold=100, area_threshold=100, merge=True):
        if blob.code() == 3:
            img.draw_rectangle(blob.rect(),color=(255,0,0))
            img.draw_cross(blob.cx(), blob.cy())
            return blob
def Chasing_ball(last_blob):
    uart.write(UART_Send(1,0,0))
    now_blob = Color_combination()
    #blobs的返回值为：
    #[{"x":104, "y":46, "w":48, "h":37, "pixels":1365, "cx":127, "cy":65, "rotation":3.033448, "code":1, "count":1, "perimeter":204, "roundness":0.675996}]
    #
    if last_blob == None :
        last_blob=now_blob
    else:
        pass
    print('last_blob',last_blob)
    if now_blob:
        blobs=(now_blob,last_blob)
        print('前后帧元组：',blobs)
        blob=find_max(blobs)
        uart.write(UART_Send(94,blob[5],blob[6]))
        return now_blob
    else:
        print('无目标')
        uart.write(UART_Send(94,0,0))
        return last_blob

#AprilTag标记跟踪  100-------------------------------------------------------------------------------
def Find_Apriltags():
    sensor.set_framesize(sensor.QQVGA)
    uart.write(UART_Send(2,0,0))
    img = sensor.snapshot().lens_corr(1.8)
    for tag in img.find_apriltags(families=image.TAG36H11):
        img.draw_rectangle(tag.rect(), color = (255, 0, 0))
        img.draw_cross(tag.cx(), tag.cy(), color = (0, 255, 0))
        X = tag.cx()
        Y = tag.cy()
        print('Apriltags_X',X,'Apriltags_Y',Y)
        uart.write(UART_Send(100,X,Y))

#找二维码  101   内容正确 102--------------------------------------------------------------------------
def QR_code(img):
    uart.write(UART_Send(1,0,0))
    sensor.set_pixformat(sensor.GRAYSCALE)
    for code in img.find_qrcodes():
        img.draw_rectangle(code.rect(),color = (255, 0, 0))
        uart.write(UART_Send(101,code[0],code[1]))
        print(code)
        print('内容：',code[4])
        if code[4]=='openmv' :
            red_led.on()
            uart.write(UART_Send(102,code[0],code[1]))
        else:
            pass

    #判别二维码内容要做处理
    #b = code[4].replace('\ufeff','')#\ufeff为字节顺序标记，出现在文本文件头部要删掉

#巡线  30~39-----------------------------------------------------------------------------------------------
IMG_WIDTH  = 64
IMG_HEIGHT = 64
#--------------直线与直角检测部分 START -------------------

BLOB_MAX_WIDTH = 60 # 色块的最大宽度
BLOB_MIN_WIDTH = 8 # 色块的最小宽度
BLOB_MAX_HEIGHT = 60 # 色块的最大高度
BLOB_MIN_HEIGHT = 8 # 色块的最小高度

# 取样窗口
ROIS = {
    'down': (0, 55, 64, 8), # 横向取样-下方 1
    'middle': (0, 28, 64, 8), # 横向取样-中间 2
    'up': (0, 0, 64, 8), # 横向取样-上方 3
    'left': (0, 0, 8, 64), # 纵向取样-左侧 4
    'right': (56, 0, 8, 64) # 纵向取样-右侧 5
}

# 是否开启debug模式
# 如果是False就不print, 不进行可视化绘制，可以提高帧率
is_debug = True

def find_blobs_in_rois(img):
    '''
    在ROIS中寻找色块，获取ROI中色块的中心区域与是否有色块的信息
    '''
    global ROIS
    global is_debug

    roi_blobs_result = {}  # 在各个ROI中寻找色块的结果记录
    for roi_direct in ROIS.keys():
        roi_blobs_result[roi_direct] = {
            'cx': -1,
            'cy': -1,
            'blob_flag': False
        }
    for roi_direct, roi in ROIS.items():
        blobs=img.find_blobs(LINE_COLOR_THRESHOLD, roi=roi, merge=True, pixels_area=10)
        if len(blobs) == 0:
            continue

        largest_blob = max(blobs, key=lambda b: b.pixels())
        x,y,width,height = largest_blob[0:4]

        if not(width >= BLOB_MIN_WIDTH and width <= BLOB_MAX_WIDTH and height >= BLOB_MIN_HEIGHT and height <= BLOB_MAX_HEIGHT):
            # 根据色块的宽度进行过滤
            continue

        roi_blobs_result[roi_direct]['cx'] = largest_blob.cx()
        roi_blobs_result[roi_direct]['cy'] = largest_blob.cy()
        roi_blobs_result[roi_direct]['blob_flag'] = True

        if is_debug:
            img.draw_rectangle((x,y,width, height), color=(255))

    return roi_blobs_result

def visualize_result(canvas, cx_mean, cx, cy, is_turn_left, is_turn_right, is_T_type, is_cross, reslut):
    '''
    可视化结果
    '''
    all_T_type = False
    for i in is_T_type:
        if i:
            all_T_type = True

    if not(is_turn_left or is_turn_right or all_T_type or is_cross):
        mid_x = int(canvas.width()/2)
        mid_y = int(canvas.height()/2)
        # 绘制x的均值点
        canvas.draw_circle(int(cx_mean), mid_y, 5, color=(255))
        # 绘制屏幕中心点
        canvas.draw_circle(mid_x, mid_y, 8, color=(0))
        canvas.draw_line((mid_x, mid_y, int(cx_mean), mid_y), color=(255))

    turn_type = 'N' # 啥转角也不是

    if all_T_type or is_cross:
        # 十字形或者T形
        canvas.draw_cross(int(cx), int(cy), size=10, color=(255))
        canvas.draw_circle(int(cx), int(cy), 5, color=(255))

    if all_T_type:
        turn_type = 'T' # T字形状
    elif is_cross:
        turn_type = 'C' # 十字形
    elif is_turn_left:
        turn_type = 'L' # 左转
    elif is_turn_right:
        turn_type = 'R' # 右转

    canvas.draw_string(0, 0, turn_type, color=(0))


#--------------直线与直角检测部分 END -------------------
#巡线主功能
def Line_patrol():
    sensor.set_pixformat(sensor.GRAYSCALE)
    sensor.set_framesize(sensor.B64X64)
    sensor.set_brightness(0)
    img = sensor.snapshot().lens_corr(1.5)

    lines = img.find_lines(threshold=1000, theta_margin = 50, rho_margin = 50)
    # 寻找相交的点 要求满足角度阈值
    intersect_pt = GeometryFeature.find_interserct_lines(lines, angle_threshold=(45,90),
    window_size=(IMG_WIDTH, IMG_HEIGHT))

    if intersect_pt is None:
        # 直线与直线之间的夹角不满足阈值范围
        intersect_x = 0
        intersect_y = 0
    else:
        intersect_x, intersect_y = intersect_pt
    #img.draw_cross(intersect_x, intersect_y,size=2, color=(255))

    reslut = find_blobs_in_rois(img)

    # 判断是否需要左转与右转
    is_turn_left = False
    is_turn_right = False
    turn_left_over = False
    turn_right_over = False
    is_T_NO1 = False
    is_T_NO2 = False
    is_T_NO3 = False
    is_T_NO4 = False
    is_cross = False

    #   ———————
    #         |
    #         |
    #         |
    if (not reslut['up']['blob_flag'] ) and reslut['down']['blob_flag']:
        if reslut['left']['blob_flag'] and (not reslut['right']['blob_flag']):
            is_turn_left = True


    #         |
    #         |
    #         |
    #   ———————
    if  reslut['up']['blob_flag']  and (not reslut['down']['blob_flag']):
        if reslut['left']['blob_flag'] and (not reslut['right']['blob_flag']):
            turn_left_over = True


    #   ———————
    #   |
    #   |
    #   |
    if (not reslut['up']['blob_flag'] ) and reslut['down']['blob_flag']:
        if (not reslut['left']['blob_flag']) and reslut['right']['blob_flag']:
            is_turn_right = True



    #   |
    #   |
    #   |
    #   ———————
    if reslut['up']['blob_flag']  and (not reslut['down']['blob_flag']):
        if (not reslut['left']['blob_flag']) and reslut['right']['blob_flag']:
            turn_right_over = True


    #       |
    #       |       1号T
    #       |
    #   —————————
    if reslut['up']['blob_flag']  and (not reslut['down']['blob_flag']):
        if reslut['left']['blob_flag'] and reslut['right']['blob_flag']:
            is_T_NO1 = True


    #   —————————
    #       |
    #       |       2号T
    #       |
    if (not reslut['up']['blob_flag'])  and reslut['down']['blob_flag']:
        if reslut['left']['blob_flag'] and reslut['right']['blob_flag']:
            is_T_NO2 = True



    #   |
    #   |
    #   |————————— 3号T
    #   |
    #   |
    if  reslut['up']['blob_flag']  and reslut['down']['blob_flag']:
        if (not reslut['left']['blob_flag']) and reslut['right']['blob_flag']:
            is_T_NO3 = True


    #             |
    #             |
    #    —————————| 4号T
    #             |
    #             |
    if  reslut['up']['blob_flag']  and reslut['down']['blob_flag']:
        if reslut['left']['blob_flag'] and (not reslut['right']['blob_flag']):
            is_T_NO4 = True


    #         |
    #         |
    #    —————|————-
    #         |
    #         |
    if  reslut['up']['blob_flag']  and reslut['down']['blob_flag']:
        if reslut['left']['blob_flag'] and  reslut['right']['blob_flag']:
            is_cross = True


    # cx_mean 用于确定视角中的轨道中心
    # 用于表示左右偏移量
    cx_mean = 0
    for roi_direct in ['up', 'down', 'middle']:
       if reslut[roi_direct]['blob_flag']:
           cx_mean += reslut[roi_direct]['cx']
       else:
           cx_mean += IMG_WIDTH / 2
    cx_mean /= 3

    # cx, cy 只有在T形区域检测出来的时候才有用，
    # 用于确定轨道中圆形的大致区域， 用于定点， 是计算圆心的一种近似方法

    cx = 0
    cy = 0

    if is_cross or is_T_NO1 or is_T_NO2 or is_T_NO3 or is_T_NO4:
        # 只在出现十字形或者T字形才计算圆心坐标
        cnt = 0
        for roi_direct in ['up', 'down']:
            if reslut[roi_direct]['blob_flag']:
                cnt += 1
                cx += reslut[roi_direct]['cx']
        if cnt == 0:
            cx = last_cx
        else:
            cx /= cnt

        cnt = 0
        for roi_direct in ['left', 'right']:
            if reslut[roi_direct]['blob_flag']:
                cnt += 1
                cy += reslut[roi_direct]['cy']
        if cnt == 0:
            cy = last_cy
        else:
            cy /= cnt


    last_cx = cx
    last_cy = cy

    is_T_type = [is_T_NO1,is_T_NO2,is_T_NO3,is_T_NO4]

    if is_debug:
        visualize_result(img, cx_mean, cx, cy, is_turn_left, is_turn_right, is_T_type, is_cross, reslut)

    if   is_turn_left:
        uart.write(UART_Send(30,intersect_x,intersect_y)) #前往交点
    elif turn_left_over:
        uart.write(UART_Send(31,reslut['up']['cx'],reslut['up']['cy'])) #完成左转,发送上框坐标

    elif is_turn_right:
        uart.write(UART_Send(32,intersect_x,intersect_y)) #前往交点
    elif turn_right_over:
        uart.write(UART_Send(33,reslut['up']['cx'],reslut['up']['cy'])) #完成右转,发送上框坐标

    elif is_T_NO1:
        uart.write(UART_Send(34,intersect_x,intersect_y)) #前往交点

    elif is_T_NO2:
        uart.write(UART_Send(35,intersect_x,intersect_y)) #前往交点

    elif is_T_NO3:
        uart.write(UART_Send(36,intersect_x,intersect_y)) #NO1完成左转  NO2完成右转

    elif is_T_NO4:
        uart.write(UART_Send(37,intersect_x,intersect_y)) #NO1完成右转  NO2完成左转

    elif is_cross:
        uart.write(UART_Send(38,intersect_x,intersect_y)) #前往交点

    else:
        uart.write(UART_Send(39,int(cx_mean),0)) #默认直线前行，x为左右偏移量

#初始化变量-------------------------------------------------------------------------------------------
#找单一色块阈值   红蓝绿------------------------------------------------
red_threshold = (0, 100, 28, 127, -128, 127)
green_threshold = (0, 100, -128, -23, -128, 127)
blue_threshold = (0, 100, -128, -8, -128, -9)

#找组合色块阈值--------------------------------------------------------
thresholds = [(0, 100, 32, 127, -128, 127),
                (0, 100, -128, 127, -128, -36)]

#激光阈值-------------------------------------------------------------
#下午四点 (0, 100, -128, 127, 14, 127)
laser_threshold = (0, 100, -128, 127, 14, 127)

#巡线阈值-------------------------------------------------------------
LINE_COLOR_THRESHOLD = [(0, 131)]

flag=0
last_blob=None
while(True):
    img = sensor.snapshot().lens_corr(1.8)
    img.draw_rectangle((120,90,80,60))
    #功能区-----------------------------------------------------------------
    #分辨率     标志位
    #QVGA      1
    #QQVGA     2
    #QQQVGA    3
    #B64X64    4
    #无用       90

    #追激光                     48------------------------------------------
    #color_blob(img)
    #找色块                     90 91 92 93---------------------------------
    #flag=find_blob(img, flag)
    #找组合色块                  94------------------------------------------
    #last_blob=Chasing_ball(last_blob)
    #AprilTag标记跟踪            100-----------------------------------------
    #Find_Apriltags()
    #找二维码                    101   内容正确 102---------------------------
    #QR_code(img)
    #巡线                       30~39---------------------------------------
    Line_patrol()

