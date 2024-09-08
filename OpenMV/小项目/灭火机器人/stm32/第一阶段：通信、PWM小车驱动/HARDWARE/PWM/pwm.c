#include "pwm.h" 

TIM_HandleTypeDef TIM4_Handler;      	//定时器句柄 
TIM_OC_InitTypeDef TIM4_CH1Handler;	//定时器4通道1句柄
TIM_OC_InitTypeDef TIM4_CH2Handler;	//定时器4通道2句柄
TIM_OC_InitTypeDef TIM4_CH3Handler;	//定时器4通道3句柄
TIM_OC_InitTypeDef TIM4_CH4Handler;	//定时器4通道4句柄

//TIM4 PWM部分初始化 
//arr：自动重装值。
//psc：时钟预分频数
//定时器溢出时间计算方法:Tout=((arr+1)*(psc+1))/Ft us.
//Ft=定时器工作频率,单位:Mhz
//利用TIM4一次性输出四路PWM波
void TIM4_PWM_Init(u16 arr,u16 psc)
{  
	TIM4_Handler.Instance = TIM4;          	//定时器4
  TIM4_Handler.Init.Prescaler = psc;       //定时器分频
  TIM4_Handler.Init.CounterMode = TIM_COUNTERMODE_UP;//向上计数模式
  TIM4_Handler.Init.Period = arr;          //自动重装载值
  TIM4_Handler.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  HAL_TIM_PWM_Init(&TIM4_Handler);       //初始化PWM
    
	//CH1   右后轮
  TIM4_CH1Handler.OCMode = TIM_OCMODE_PWM1; //模式选择PWM1
  TIM4_CH1Handler.Pulse = arr/2;            //设置比较值,此值用来确定占空比，默认比较值为自动重装载值的一半,即占空比为50%
  TIM4_CH1Handler.OCPolarity = TIM_OCPOLARITY_LOW; //输出比较极性为低 
  HAL_TIM_PWM_ConfigChannel(&TIM4_Handler,&TIM4_CH1Handler,TIM_CHANNEL_1);//配置TIM14通道1
	
	//CH2   右前轮
	TIM4_CH2Handler.OCMode = TIM_OCMODE_PWM1; 
  TIM4_CH2Handler.Pulse = arr/2;            
  TIM4_CH2Handler.OCPolarity = TIM_OCPOLARITY_LOW; 
  HAL_TIM_PWM_ConfigChannel(&TIM4_Handler,&TIM4_CH2Handler,TIM_CHANNEL_2);//配置TIM14通道2
	
	//CH3   左后轮
	TIM4_CH3Handler.OCMode = TIM_OCMODE_PWM1; 
  TIM4_CH3Handler.Pulse = arr/2;            
  TIM4_CH3Handler.OCPolarity = TIM_OCPOLARITY_LOW; 
  HAL_TIM_PWM_ConfigChannel(&TIM4_Handler,&TIM4_CH3Handler,TIM_CHANNEL_3);//配置TIM14通道3
	
	//CH4   左前轮
	TIM4_CH4Handler.OCMode = TIM_OCMODE_PWM1; 
  TIM4_CH4Handler.Pulse = arr/2;            
  TIM4_CH4Handler.OCPolarity = TIM_OCPOLARITY_LOW; 
  HAL_TIM_PWM_ConfigChannel(&TIM4_Handler,&TIM4_CH4Handler,TIM_CHANNEL_4);//配置TIM14通道4
	
	do
	{
	}
  while( HAL_TIM_PWM_Start(&TIM4_Handler,TIM_CHANNEL_1) != HAL_OK ) ;                //开启PWM通道1
	
	do
	{
	}
  while( HAL_TIM_PWM_Start(&TIM4_Handler,TIM_CHANNEL_2) != HAL_OK ) ;                //开启PWM通道2
	
	do
	{
	}
  while( HAL_TIM_PWM_Start(&TIM4_Handler,TIM_CHANNEL_3) != HAL_OK ) ;                //开启PWM通道3
	
	do
	{
	}
  while( HAL_TIM_PWM_Start(&TIM4_Handler,TIM_CHANNEL_4)!= HAL_OK ) ;                //开启PWM通道4
}


//定时器底层驱动，时钟使能，引脚配置
//此函数会被HAL_TIM_PWM_Init()调用
//htim:定时器句柄
void HAL_TIM_PWM_MspInit(TIM_HandleTypeDef *htim)
{
	GPIO_InitTypeDef GPIO_Initure;
	__HAL_RCC_TIM4_CLK_ENABLE();			//使能定时器14
	__HAL_RCC_GPIOD_CLK_ENABLE();			//开启GPIOD时钟
	
	GPIO_Initure.Pin = GPIO_PIN_12|GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;           	//PD12
	GPIO_Initure.Mode = GPIO_MODE_AF_PP;  	//复用推挽输出
	GPIO_Initure.Pull = GPIO_PULLUP;          //上拉
	GPIO_Initure.Speed = GPIO_SPEED_HIGH;     //高速
	GPIO_Initure.Alternate = GPIO_AF2_TIM4;	  //PD12复用为TIM4_CH1
	HAL_GPIO_Init(GPIOD,&GPIO_Initure);
}


