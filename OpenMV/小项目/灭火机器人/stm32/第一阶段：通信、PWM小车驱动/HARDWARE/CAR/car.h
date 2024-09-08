#ifndef _CAR_H
#define _CAR_H
#include "sys.h"

//��ǰ�ֵ��
#define IN1 PCout(0)
#define IN2 PCout(1)

//����ֵ��
#define IN3 PCout(2)
#define IN4 PCout(3)

//��ǰ�ֵ��
#define IN5 PCout(4)
#define IN6 PCout(5)

//�Һ��ֵ��
#define IN7 PCout(6)
#define IN8 PCout(7)


void CAR_Init(void);
void CAR_GoForward(void);
void CAR_GoBack(void);
void CAR_TurnLeft(void);
void CAR_TurnRight(void);
void CAR_Stop(void);

#endif
