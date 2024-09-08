# Untitled - By: HQ - 周六 8月 3 2019

# 利用特征点检测特定物体例程。
# 向相机显示一个对象，然后运行该脚本。 一组关键点将被提取一次，然后
# 在以下帧中进行跟踪。 如果您想要一组新的关键点，请重新运行该脚本。
import sensor, time, image

sensor.reset()
sensor.set_contrast(3)
sensor.set_gainceiling(32)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing((320, 240))
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False, value=100)

#画出特征点

def draw_keypoints(img, kpts):
    if kpts:
        print(kpts)
        img.draw_keypoints(kpts)
        img = sensor.snapshot()
        time.sleep(1000)

kpts1 = None

clock = time.clock()

while (True):
    clock.tick()
    img = sensor.snapshot()
    if (kpts1 == None):
        kpts1 = img.find_keypoints(max_keypoints=150, threshold=10, scale_factor=1.35)

        draw_keypoints(img, kpts1)
    else:
        kpts2 = img.find_keypoints(max_keypoints=150, threshold=10, normalized=True)
        #如果检测到特征物体
        if (kpts2):
            #匹配当前找到的特征和最初的目标特征的相似度
            match = image.match_descriptor(kpts1, kpts2, threshold=85)

            if (match.count()>10):
                img.draw_rectangle(match.rect())
                img.draw_cross(match.cx(), match.cy(), size=10)
            print(kpts2, "matched:%d dt:%d"%(match.count(), match.theta()))
    img.draw_string(0, 0, "FPS:%.2f"%(clock.fps()))
