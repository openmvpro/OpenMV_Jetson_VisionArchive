# Optical Flow Example



#

# Your OpenMV Cam can use optical flow to determine the displacement between



# two images. This allows your OpenMV Cam to track movement like how your laser



# mouse tracks movement. By tacking the difference between successive images



# you can determine instaneous displacement with your OpenMV Cam too!



import sensor, image, time



sensor.reset() # Initialize the camera
sensor. sensor.set_pixformat(sensor.GRAYSCALE) # or sensor.GRAYSCALE
sensor.set_framesize(sensor.B64x32) # or B40x30 or B64x64
clock = time.clock() # Tracks FPS.

#find_displacement 这个功能函数使用是是2D FFT算法获得新旧两张图像的相位移动，由于OPenMV上单片机内存的问题，
#只能计算64x64或者64*32的图片（openmv-2），如果使用OPenMV3或许可以计算128*32或者32*128的图片
old = sensor.snapshot() //获取一帧图像

while(True):
    clock.tick() # 获取时间
    img = sensor.snapshot() # 获取一帧图像
    [delta_x, delta_y, response] = old.find_displacement(img) #获取前面一张图像与刚捕获的图像之间的偏移
    old = img.copy()
    print("%0.1f X\t%0.1f Y\t%0.2f QoR\t%0.2f FPS" % \ (delta_x, delta_y, response, clock.fps()))


'''
解析：



find_displacement这个函数讲返回当前图片相对于前一张图片的偏移量，使用的是相位偏移算法，最终调用的算法为：在phasecorrelation.c这个文件中，源码为：



/*****************************************************************************************************************************



*函数名称：imlib_phasecorrelate *功能说明：计算当前图片相对于模板图片的相位偏移*参 数:img0->当前图片数据指针

* img1->模板图片数据指针，也就是摄像头捕获的前一张图片

* x_offset->x轴方向的变量指针

* x_offset->y轴方向的变量指针

* response->置信值取值范围0.0~1.0



******************************************************************************************************************************/



void imlib_phasecorrelate(image_t *img0, image_t *img1, float *x_offset, float *y_offset, float *response)



{



fft2d_controller_t fft0, fft1; rectangle_t roi0, roi1;



roi0.x = 0; roi0.y = 0;



roi0.w = img0->w; roi0.h = img0->h;



roi1.x = 0; roi1.y = 0;

 '''
