import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

def maxs(a,b):#两数取大
    return (((a+b)+abs(a-b))//2)

def mins(a,b):#两数取小
    return(((a-b)+abs(-a-b))//2)


b=(51, 100, -10, -44, 20, 58)
while(True):
    clock.tick()
    img = sensor.snapshot().lens_corr(1.8)
    for c in img.find_circles(threshold = 3500, x_margin = 10, y_margin = 10, r_margin = 10,
            r_min = 2, r_max = 100, r_step = 2):
        area = (c.x()-c.r(), c.y()-c.r(), 2*c.r(), 2*c.r())
        #area为识别到的圆的区域，即圆的外接矩形框
        statistics = img.get_statistics(roi=area)#像素颜色统计
        print(statistics)
        #(0,100,0,120,0,120)是红色的阈值，所以当区域内的众数（也就是最多的颜色），范围在这个阈值内，就说明是红色的圆。
        #l_mode()，a_mode()，b_mode()是L通道，A通道，B通道的众数。
        if mins(b[0],b[1])<statistics.l_mode()<maxs(b[0],b[1]) and mins(b[2],b[3])<statistics.a_mode()<maxs(b[2],b[3]) and mins(b[4],b[5])<statistics.b_mode()<maxs(b[4],b[5]):#if the circle is red
            img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))#识别到的红色圆形用红色的圆框出来
        else:
            img.draw_rectangle(area, color = (255, 255, 255))
            #将非红色的圆用白色的矩形框出来
    print("FPS %f" % clock.fps())
