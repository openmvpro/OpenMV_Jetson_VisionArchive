'''
正面从左到右
PCA9658-----Jetson Nano
1-----------2
2-----------1
3-----------3
4-----------5
6-----------6
'''

from adafruit_servokit import ServoKit
import time
myKit=ServoKit(channels=16)

i=0
a=0
while(True):
    if  i ==180 :
        a=1
    if i == 0:
        a=0
    if a==1:
        i = i-1
    if a==0:
        i = i+1

    myKit.servo[0].angle=i
    myKit.servo[1].angle=i

    print(i)

    time.sleep(0.05)

