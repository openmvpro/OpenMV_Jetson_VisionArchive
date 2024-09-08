#include "key.h"
#include "delay.h"


//按键初始化函数
void KEY_Init(void)
{
    GPIO_InitTypeDef GPIO_Initure;
    __HAL_RCC_GPIOG_CLK_ENABLE();           //开启GPIOG时钟
		GPIO_Initure.Pin=GPIO_PIN_9|GPIO_PIN_10|GPIO_PIN_11|GPIO_PIN_13; //PG9,10,11,13
    GPIO_Initure.Mode=GPIO_MODE_INPUT;      //输入
    GPIO_Initure.Pull=GPIO_PULLUP;          //上拉
    GPIO_Initure.Speed=GPIO_SPEED_HIGH;     //高速
    HAL_GPIO_Init(GPIOG,&GPIO_Initure);
	
	  __HAL_RCC_GPIOA_CLK_ENABLE();
		GPIO_Initure.Pin=GPIO_PIN_0;
		GPIO_Initure.Pull=GPIO_PULLDOWN; 
		HAL_GPIO_Init(GPIOA,&GPIO_Initure);
	
    
}

//按键处理函数
//返回按键值
//mode:0,不支持连续按;1,支持连续按;
//0，没有任何按键按下
//1，WKUP按下 WK_UP
//注意此函数有响应优先级,KEY0>KEY1>KEY2>WK_UP!!
u8 KEY_Scan(u8 mode)
{
    static u8 key_up=1;     //按键松开标志
    if(mode==1)key_up=1;    //支持连按
    if(key_up&&(KEY0==0||KEY1==0||KEY2==0||KEY3==0||WEKEUP==1))
    {
        delay_ms(10);
        key_up=0;
        if(KEY0==0)       return KEY0_PRES;
        else if(KEY1==0)  return KEY1_PRES;
        else if(KEY2==0)  return KEY2_PRES;
        else if(KEY3==0) 	return KEY3_PRES;
				else if(WEKEUP==1) return WEKEUP_PRES;
    }
		else if(KEY0==1&&KEY1==1&&KEY2==1&&KEY3==1&&WEKEUP==0)key_up=1;
    return 0;   //无按键按下
}
