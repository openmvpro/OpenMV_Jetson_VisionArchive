# Measure the distance

import sensor, image, time

yellow_threshold   = (62, 78, -13, 4, 8, 59)
BLACK_THRESHOLD = (30, 46, 17, 60, -6, 31)

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # use RGB565.
sensor.set_framesize(sensor.VGA) # use QQVGA for speed.
#sensor.set_windowing((80,60))
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
clock = time.clock() # Tracks FPS.

#就是先让球距离摄像头10cm，打印出摄像头里直径的像素值，然后相乘，就得到了k的值！
#   16cm / 12
#   27cm / 8
#
K = 20*15
#K=5000#the value should be measured

while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    blobs = img.find_blobs([BLACK_THRESHOLD])
    if len(blobs) == 1:

        b = blobs[0]
        img.draw_rectangle(b[0:4]) # rect
        print("1111   %d"%b[3])
        img.draw_cross(b[5], b[6]) # cx, cy

        length = K/b[3]
        print("2222222   %d"%length)

