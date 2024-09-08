import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
clock = time.clock()

#亮度
sensor.set_brightness(0)#-3~3

#自动增益
sensor.set_auto_gain(True)

#白平衡
sensor.set_auto_whitebal(True)

#翻转
sensor.set_hmirror(False)#水平方向翻转

sensor.set_vflip(False)#垂直方向翻转

while(True):
    clock.tick()
    #畸变校正
    img = sensor.snapshot().lens_corr(strength = 1.8, zoom = 1.0)#strength越小校正越好，zoom缩放
    print(clock.fps())
