#ifndef _KEY_H
#define _KEY_H
#include "sys.h"


//下面的方式是通过位带操作方式读取IO
//#define KEY0        PGin(9)  			//KEY0按键PG9
//#define KEY1        PGin(10) 			//KEY1按键PG10
//#define KEY2        PGin(11) 			//KEY2按键PG11
//#define KEY3        PGin(13) 			//KEY3按键PG13


//下面的方式是通过直接操作HAL库函数方式读取IO
#define KEY0        HAL_GPIO_ReadPin(GPIOG,GPIO_PIN_9)    			//KEY0按键PE4
#define KEY1        HAL_GPIO_ReadPin(GPIOG,GPIO_PIN_10)   			//KEY1按键PE3
#define KEY2        HAL_GPIO_ReadPin(GPIOG,GPIO_PIN_11) 				//KEY2按键PE2
#define KEY3      	HAL_GPIO_ReadPin(GPIOG,GPIO_PIN_13)   			//WKUP按键PA0
#define WEKEUP      HAL_GPIO_ReadPin(GPIOA,GPIO_PIN_0)   

#define KEY0_PRES 	1
#define KEY1_PRES		2
#define KEY2_PRES		3
#define KEY3_PRES   4
#define WEKEUP_PRES   5

void KEY_Init(void);
u8 KEY_Scan(u8 mode);

#endif
