#多模板匹配
#颜色模板匹配
#特征点

import time, sensor, image
from image import SEARCH_EX, SEARCH_DS

sensor.reset()
sensor.set_contrast(1)
sensor.set_gainceiling(16)
sensor.set_framesize(sensor.QQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)
clock = time.clock()
#sensor.set_hmirror(True)
#sensor.set_vflip(True)

#多模板匹配
def Multi_template_matching():
    templates = ["/11.pgm", "/A.pgm", "/3.pgm", "/6.pgm", "/G.pgm", "/H.pgm", "/T.pgm"]#需要的单模板内容

    for t in templates:
        template = image.Image(t)
        r = img.find_template(template, 0.70, step=4, search=SEARCH_EX)
        #对象，速率（越快误差率越高），区域，跳过像素量，算法（image.SEARCH_DS（快），image.SEARCH_EX）

        if r:
            img.draw_rectangle(r)
            print(t) #打印模板名字

#颜色模板匹配
def Color_template_matching():
    #改为彩色
    sensor.set_pixformat(sensor.RGB565)
    templates = ["/11.pgm", "/A.pgm", "/3.pgm", "/6.pgm", "/G.pgm", "/H.pgm", "/T.pgm"]#需要的单模板内容

    # 颜色跟踪阈值(L Min, L Max, A Min, A Max, B Min, B Max)
    thresholds = [(30, 100, 15, 127, 15, 127),
                  (30, 100, -64, -8, -32, 32),
                  (0, 15, 0, 40, -80, -20)]

    for blob in img.find_blobs(thresholds, pixels_threshold=200, area_threshold=200):
           img = img.to_grayscale()
           for t in templates:
               template = image.Image(t)
               r = img.find_template(template, 0.70, step=4, search=SEARCH_EX)
               if r:
                   img.draw_rectangle(r, color=0)
                   print(blob.code(), t)

#特征点
def draw_keypoints(img, kpts):
    if kpts:
        print(kpts)
        img.draw_keypoints(kpts)
        img = sensor.snapshot()
        time.sleep(1000)

def Characteristic_point():
    #kpts1保存目标物体的特征
    kpts1 = None
    if (kpts1 == None):
            #如果是刚开始运行程序，提取最开始的图像作为目标物体特征，kpts1保存目标物体的特征
            #默认会匹配目标特征的多种比例大小，而不仅仅是保存目标特征时的大小，比模版匹配灵活。
            # NOTE: By default find_keypoints returns multi-scale keypoints extracted from an image pyramid.
            kpts1 = img.find_keypoints(max_keypoints=150, threshold=20, scale_factor=1.2)
            #image.find_keypoints(roi=Auto, threshold=20, normalized=False, scale_factor=1.5, max_keypoints=100, corner_detector=CORNER_AGAST)
            #roi表示识别的区域，是一个元组（x,y,w,h）,默认与framsesize大小一致。
            #threshold是0~255的一个阈值，用来控制特征点检测的角点数量。用默认的AGAST特征点检测，这个阈值大概是20。用FAST特征点检测，这个阈值大概是60～80。阈值越低，获得的角点越多。
            #normalized是一个布尔数值，默认是False，可以匹配目标特征的多种大小（比ncc模版匹配效果灵活）。如果设置为True，关闭特征点检测的多比例结果，仅匹配目标特征的一种大小（类似于模版匹配），但是运算速度会更快一些。
            #scale_factor是一个大于1.0的浮点数。这个数值越高，检测速度越快，但是匹配准确率会下降。一般在1.35~1.5左右最佳。
            #max_keypoints是一个物体可提取的特征点的最大数量。如果一个物体的特征点太多导致RAM内存爆掉，减小这个数值。
            #corner_detector是特征点检测采取的算法，默认是AGAST算法。FAST算法会更快但是准确率会下降。
            draw_keypoints(img, kpts1)
            #画出此时的目标特征
        else:
            #当与最开始的目标特征进行匹配时，默认设置normalized=True，只匹配目标特征的一种大小。
            # NOTE: When extracting keypoints to match the first descriptor, we use normalized=True to extract
            # keypoints from the first scale only, which will match one of the scales in the first descriptor.
            kpts2 = img.find_keypoints(max_keypoints=150, threshold=20, normalized=True)
            #如果检测到特征物体
            if (kpts2):
                #匹配当前找到的特征和最初的目标特征的相似度
                match = image.match_descriptor(kpts1, kpts2, threshold=85)
                #image.match_descriptor(descritor0, descriptor1, threshold=70, filter_outliers=False)。本函数返回kptmatch对象。
                #threshold阈值设置匹配的准确度，用来过滤掉有歧义的匹配。这个值越小，准确度越高。阈值范围0～100，默认70
                #filter_outliers默认关闭。

                #match.count()是kpt1和kpt2的匹配的近似特征点数目。
                #如果大于10，证明两个特征相似，匹配成功。
                if (match.count()>10):
                    # If we have at least n "good matches"
                    # Draw bounding rectangle and cross.
                    #在匹配到的目标特征中心画十字和矩形框。
                    img.draw_rectangle(match.rect())
                    img.draw_cross(match.cx(), match.cy(), size=10)

                #match.theta()是匹配到的特征物体相对目标物体的旋转角度。
                print(kpts2, "matched:%d dt:%d"%(match.count(), match.theta()))
                #不建议draw_keypoints画出特征角点。
                # NOTE: uncomment if you want to draw the keypoints
                #img.draw_keypoints(kpts2, size=KEYPOINTS_SIZE, matched=True)

        # Draw FPS
        #打印帧率。
        img.draw_string(0, 0, "FPS:%.2f"%(clock.fps()))


while (True):
    clock.tick()
    img = sensor.snapshot().lens_corr(0.8)

    #多模板匹配
    #Multi_template_matching()
    #颜色模板匹配
    #Color_template_matching()
    #特征点
    #Characteristic_point()
