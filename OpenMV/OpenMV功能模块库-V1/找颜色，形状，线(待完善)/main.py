#多颜色追踪
#多颜色组合追踪
#找形状(圆，矩形)
#找线

import sensor, image, time, math
from GeometryFeature import GeometryFeature

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # 颜色跟踪必须关闭自动增益
sensor.set_auto_whitebal(False) # 颜色跟踪必须关闭白平衡
clock = time.clock()

#多颜色追踪-------------------------------------------------------------------------------------------
def Multi_color_tracking():
    # 最多可以传递16个阈值
    thresholds = [(0, 100, 55, 127, -128, 127), # 粉色
                  (0, 100, 7, 127, 43, 127), # 黄色
                  (0, 100, -128, -35, -128, 127)] # 绿色

    for blob in img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200):
        print(blob.elongation() )
        #真实识别到颜色的区域
        if blob.elongation() > 0.01:
            img.draw_edges(blob.min_corners(), color=(255,0,0))
            img.draw_line(blob.major_axis_line(), color=(0,255,0))
            img.draw_line(blob.minor_axis_line(), color=(0,0,255))

        # 这些值始终是稳定的。
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        # 注意-色块rotation仅在0-180范围内唯一。
        #img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)
    #print(clock.fps())

#多颜色组合追踪---------------------------------------------------------------------------------------
def Color_combination():
    thresholds = [(0, 100, 55, 127, -128, 127), # 粉色           色块位: 1
                    (0, 100, 7, 127, 43, 127), # 黄色                   2
                    (0, 100, -128, -35, -128, 127)] # 绿色              4      若有第四组色块位为:8

    for blob in img.find_blobs(thresholds, pixels_threshold=100, area_threshold=100, merge=True):
        if blob.code() == 3:
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            img.draw_string(blob.x() + 2, blob.y() + 2, "r/g")
        if blob.code() == 5:
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            img.draw_string(blob.x() + 2, blob.y() + 2, "r/b")
        if blob.code() == 6:
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            img.draw_string(blob.x() + 2, blob.y() + 2, "g/b")
        if blob.code() == 7:
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())
            img.draw_string(blob.x() + 2, blob.y() + 2, "r/g/b")
        print(blob.code())

#找形状----------------------------------------------------------------------------------------------
#找圆
def Look_for_shapes_circular():
    for c in img.find_circles(threshold = 3500, x_margin = 10, y_margin = 10, r_margin = 10,
                                r_min = 2, r_max = 100, r_step = 2):
        img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))
        print(c)

    print("FPS %f" % clock.fps())
#找矩形
def Look_for_shapes_rectangle():
    for r in img.find_rects(threshold = 10000):
        img.draw_rectangle(r.rect(), color = (255, 0, 0))
        for p in r.corners(): img.draw_circle(p[0], p[1], 5, color = (0, 255, 0))
        print(r)

    print("FPS %f" % clock.fps())

#找线------------------------------------------------------------------------------------------------
#基础函数找线          把主函数的拍照函数关掉
def Find_the_line1():
    sensor.set_pixformat(sensor.GRAYSCALE)

    #设置阈值
    THRESHOLD = (0, 80)
    img = sensor.snapshot().binary([THRESHOLD])
    line = img.get_regression([(255,255)], robust = False)#对图像所有阈值像素进行线性回归计算。这一计算通过最小二乘法进行，
                                                        #通常速度较快，但不能处理任何异常值。 若 robust 为True，
                                                        #则使用Theil-Sen线性回归算法，它计算图像中所有阈值像素的斜率的中位数
    if (line):
        rho_err = abs(line.rho())-img.width()/2
        if line.theta()>90:
            theta_err = line.theta()-180
        else:
            theta_err = line.theta()
        img.draw_line(line.line(), color = 127)
        print(rho_err,line.magnitude(),rho_err)

    '''#设置是否使用img.binary()函数进行图像分割
    BINARY_VISIBLE = True
    sensor.set_pixformat(sensor.GRAYSCALE)

    img = sensor.snapshot().binary([THRESHOLD]) if BINARY_VISIBLE else sensor.snapshot()
    line = img.get_regression([(255,255) if BINARY_VISIBLE else THRESHOLD])

    if (line): img.draw_line(line.line(), color = 127)
    print("FPS %f, mag = %s" % (clock.fps(), str(line.magnitude()) if (line) else "N/A"))'''

#加权重找线
def Find_the_line2():
    sensor.set_pixformat(sensor.GRAYSCALE)
    # 跟踪线的阈值
    GRAYSCALE_THRESHOLD = [(0, 64)]
    # 每个roi为(x, y, w, h)，线检测算法将尝试找到每个roi中最大的blob的质心。
    # 然后用不同的权重对质心的x位置求平均值，其中最大的权重分配给靠近图像底部的roi，
    # 较小的权重分配给下一个roi，以此类推。
    ROIS = [ # [ROI, weight]
            (0, 100, 160, 20, 0.7), # 你需要为你的应用程序调整权重
            (0, 050, 160, 20, 0.3), # 取决于你的机器人是如何设置的。
            (0, 000, 160, 20, 0.1)
           ]
    #roi代表三个取样区域，（x,y,w,h,weight）,代表左上顶点（x,y）宽高分别为w和h的矩形，
    #weight为当前矩形的权值。注意本例程采用的QQVGA图像大小为160x120，roi即把图像横分成三个矩形。
    #三个矩形的阈值要根据实际情况进行调整，离机器人视野最近的矩形权值要最大，
    #如上图的最下方的矩形，即(0, 100, 160, 20, 0.7)

    # Compute the weight divisor (we're computing this so you don't have to make weights add to 1).
    weight_sum = 0 #权值和初始化
    for r in ROIS: weight_sum += r[4] # r[4] is the roi weight.
    #计算权值和。遍历上面的三个矩形，r[4]即每个矩形的权值。

    centroid_sum = 0
    #利用颜色识别分别寻找三个矩形区域内的线段
    for r in ROIS:
            blobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi=r[0:4], merge=True)

            if blobs:
                most_pixels = 0
                largest_blob = 0
                for i in range(len(blobs)):
                #目标区域找到的颜色块（线段块）可能不止一个，找到最大的一个，作为本区域内的目标直线
                    if blobs[i].pixels() > most_pixels:
                        most_pixels = blobs[i].pixels()
                        #merged_blobs[i][4]是这个颜色块的像素总数，如果此颜色块像素总数大于
                        #most_pixels，则把本区域作为像素总数最大的颜色块。更新most_pixels和largest_blob
                        largest_blob = i

                img.draw_rectangle(blobs[largest_blob].rect())
                img.draw_cross(blobs[largest_blob].cx(),
                               blobs[largest_blob].cy())

                centroid_sum += blobs[largest_blob].cx() * r[4]   #计算centroid_sum，centroid_sum等于每个区域的最大颜色块的中心点的x坐标值乘本区域的权值

    center_pos = (centroid_sum / weight_sum)    #中间公式

    deflection_angle = 0                                       #角度计算.80 60 分别为图像宽和高的一半，图像大小为QQVGA 160x120.
    deflection_angle = -math.atan((center_pos-80)/60)          #弧度值

    deflection_angle = math.degrees(deflection_angle)           #将计算结果的弧度值转化为角度值

    print("Turn Angle: %f" % deflection_angle)




#五区域找线
#直线灰度图颜色阈值
LINE_COLOR_THRESHOLD = [(91, 0)]

IMG_WIDTH  = 64
IMG_HEIGHT = 64
#--------------直线与直角检测部分 START -------------------

BLOB_MAX_WIDTH = 20 # 色块的最大宽度
BLOB_MIN_WIDTH = 5 # 色块的最小宽度
BLOB_MAX_HEIGHT = 20 # 色块的最大高度
BLOB_MIN_HEIGHT = 5 # 色块的最小高度

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
        x,y,width,height = largest_blob[:4]

        if not(width >= BLOB_MIN_WIDTH and width <= BLOB_MAX_WIDTH and height >= BLOB_MIN_HEIGHT and height <= BLOB_MAX_HEIGHT):
            # 根据色块的宽度进行过滤
            continue

        roi_blobs_result[roi_direct]['cx'] = largest_blob.cx()
        roi_blobs_result[roi_direct]['cy'] = largest_blob.cy()
        roi_blobs_result[roi_direct]['blob_flag'] = True

        if is_debug:
            img.draw_rectangle((x,y,width, height), color=(255))

    return roi_blobs_result

def visualize_result(canvas, cx_mean, cx, cy, is_turn_left, is_turn_right, is_t, is_cross, reslut):
    '''
    可视化结果
    '''
    if not(is_turn_left or is_turn_right or is_t or is_cross):
        mid_x = int(canvas.width()/2)
        mid_y = int(canvas.height()/2)
        # 绘制x的均值点
        canvas.draw_circle(int(cx_mean), mid_y, 5, color=(255))
        # 绘制屏幕中心点
        canvas.draw_circle(mid_x, mid_y, 8, color=(0))
        canvas.draw_line((mid_x, mid_y, int(cx_mean), mid_y), color=(255))

    turn_type = 'N' # 啥转角也不是
    #走直线角度
    angle = reslut['middle']['cx'] - canvas.width()/2

    if is_t or is_cross:
        # 十字形或者T形
        canvas.draw_cross(int(cx), int(cy), size=10, color=(255))
        canvas.draw_circle(int(cx), int(cy), 5, color=(255))

    if is_t:
        turn_type = 'T' # T字形状
        #默认左转
        angle = reslut['left']['cx'] - canvas.width()/2
    elif is_cross:
        turn_type = 'C' # 十字形
        #默认右转
        angle = reslut['right']['cx'] - canvas.width()/2
    elif is_turn_left:
        turn_type = 'L' # 左转
        angle = reslut['left']['cx'] - canvas.width()/2
    elif is_turn_right:
        turn_type = 'R' # 右转
        angle = reslut['right']['cx'] - canvas.width()/2

    print(angle)

    canvas.draw_string(0, 0, turn_type, color=(0))

#--------------直线与直角检测部分 END -------------------
#巡线主功能
def Find_the_line3():
    sensor.set_pixformat(sensor.GRAYSCALE)
    sensor.set_framesize(sensor.B64X64)                  # 分辨率为B64X64

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

    reslut = find_blobs_in_rois(img)

    # 判断是否需要左转与右转
    is_turn_left = False
    is_turn_right = False


    if (not reslut['up']['blob_flag'] ) and reslut['down']['blob_flag']:
        if reslut['left']['blob_flag']:
            is_turn_left = True
        if reslut['right']['blob_flag']:
            is_turn_right = True


    # 判断是否为T形的轨道
    is_t = False
    # 判断是否十字形轨道
    is_cross = False

    cnt = 0
    for roi_direct in ['up', 'down', 'left', 'right']:
        if reslut[roi_direct]['blob_flag']:
            cnt += 1
    is_t = cnt == 3
    is_cross = cnt == 4

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

    if is_cross or is_t:
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

    if is_debug:
        visualize_result(img, cx_mean, cx, cy, is_turn_left, is_turn_right, is_t, is_cross, reslut)


while(True):
    clock.tick()
    #使用基础函数找线,加权重找线要关掉
    #img = sensor.snapshot().lens_corr(1.8)
    #多颜色追踪---------------------------------------------------------------------------------------
    #Multi_color_tracking()
    #多颜色组合追踪------------------------------------------------------------------------------------
    #Color_combination()
    #找形状------------------------------------------------------------------------------------------
    #找圆
    #Look_for_shapes_circular()
    #Look_for_shapes_rectangle()
    #找线--------------------------------------------------------------------------------------------
    #基础函数找线        把主函数的拍照函数关掉
    Find_the_line1()
    #加权重找线
    #Find_the_line2()
    #五区域找线
    #Find_the_line3()
