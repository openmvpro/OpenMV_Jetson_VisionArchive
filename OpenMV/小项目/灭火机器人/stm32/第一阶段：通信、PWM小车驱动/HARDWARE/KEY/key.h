#ifndef _KEY_H
#define _KEY_H
#include "sys.h"


//����ķ�ʽ��ͨ��λ��������ʽ��ȡIO
//#define KEY0        PGin(9)  			//KEY0����PG9
//#define KEY1        PGin(10) 			//KEY1����PG10
//#define KEY2        PGin(11) 			//KEY2����PG11
//#define KEY3        PGin(13) 			//KEY3����PG13


//����ķ�ʽ��ͨ��ֱ�Ӳ���HAL�⺯����ʽ��ȡIO
#define KEY0        HAL_GPIO_ReadPin(GPIOG,GPIO_PIN_9)    			//KEY0����PE4
#define KEY1        HAL_GPIO_ReadPin(GPIOG,GPIO_PIN_10)   			//KEY1����PE3
#define KEY2        HAL_GPIO_ReadPin(GPIOG,GPIO_PIN_11) 				//KEY2����PE2
#define KEY3      	HAL_GPIO_ReadPin(GPIOG,GPIO_PIN_13)   			//WKUP����PA0
#define WEKEUP      HAL_GPIO_ReadPin(GPIOA,GPIO_PIN_0)   

#define KEY0_PRES 	1
#define KEY1_PRES		2
#define KEY2_PRES		3
#define KEY3_PRES   4
#define WEKEUP_PRES   5

void KEY_Init(void);
u8 KEY_Scan(u8 mode);

#endif
