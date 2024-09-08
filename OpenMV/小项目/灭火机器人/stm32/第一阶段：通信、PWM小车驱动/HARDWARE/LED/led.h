#ifndef _LED_H
#define _LED_H
#include "sys.h"

#define LED0 PCout(0)   	//LED0
#define LED1 PCout(1)   	//LED1
#define LED2 PCout(2)   	//LED2
#define LED3 PCout(3)   	//LED3

void LED_Init(void);
#endif
