#include "pwm.h" 

TIM_HandleTypeDef TIM4_Handler;      	//��ʱ����� 
TIM_OC_InitTypeDef TIM4_CH1Handler;	//��ʱ��4ͨ��1���
TIM_OC_InitTypeDef TIM4_CH2Handler;	//��ʱ��4ͨ��2���
TIM_OC_InitTypeDef TIM4_CH3Handler;	//��ʱ��4ͨ��3���
TIM_OC_InitTypeDef TIM4_CH4Handler;	//��ʱ��4ͨ��4���

//TIM4 PWM���ֳ�ʼ�� 
//arr���Զ���װֵ��
//psc��ʱ��Ԥ��Ƶ��
//��ʱ�����ʱ����㷽��:Tout=((arr+1)*(psc+1))/Ft us.
//Ft=��ʱ������Ƶ��,��λ:Mhz
//����TIM4һ���������·PWM��
void TIM4_PWM_Init(u16 arr,u16 psc)
{  
	TIM4_Handler.Instance = TIM4;          	//��ʱ��4
  TIM4_Handler.Init.Prescaler = psc;       //��ʱ����Ƶ
  TIM4_Handler.Init.CounterMode = TIM_COUNTERMODE_UP;//���ϼ���ģʽ
  TIM4_Handler.Init.Period = arr;          //�Զ���װ��ֵ
  TIM4_Handler.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  HAL_TIM_PWM_Init(&TIM4_Handler);       //��ʼ��PWM
    
	//CH1   �Һ���
  TIM4_CH1Handler.OCMode = TIM_OCMODE_PWM1; //ģʽѡ��PWM1
  TIM4_CH1Handler.Pulse = arr/2;            //���ñȽ�ֵ,��ֵ����ȷ��ռ�ձȣ�Ĭ�ϱȽ�ֵΪ�Զ���װ��ֵ��һ��,��ռ�ձ�Ϊ50%
  TIM4_CH1Handler.OCPolarity = TIM_OCPOLARITY_LOW; //����Ƚϼ���Ϊ�� 
  HAL_TIM_PWM_ConfigChannel(&TIM4_Handler,&TIM4_CH1Handler,TIM_CHANNEL_1);//����TIM14ͨ��1
	
	//CH2   ��ǰ��
	TIM4_CH2Handler.OCMode = TIM_OCMODE_PWM1; 
  TIM4_CH2Handler.Pulse = arr/2;            
  TIM4_CH2Handler.OCPolarity = TIM_OCPOLARITY_LOW; 
  HAL_TIM_PWM_ConfigChannel(&TIM4_Handler,&TIM4_CH2Handler,TIM_CHANNEL_2);//����TIM14ͨ��2
	
	//CH3   �����
	TIM4_CH3Handler.OCMode = TIM_OCMODE_PWM1; 
  TIM4_CH3Handler.Pulse = arr/2;            
  TIM4_CH3Handler.OCPolarity = TIM_OCPOLARITY_LOW; 
  HAL_TIM_PWM_ConfigChannel(&TIM4_Handler,&TIM4_CH3Handler,TIM_CHANNEL_3);//����TIM14ͨ��3
	
	//CH4   ��ǰ��
	TIM4_CH4Handler.OCMode = TIM_OCMODE_PWM1; 
  TIM4_CH4Handler.Pulse = arr/2;            
  TIM4_CH4Handler.OCPolarity = TIM_OCPOLARITY_LOW; 
  HAL_TIM_PWM_ConfigChannel(&TIM4_Handler,&TIM4_CH4Handler,TIM_CHANNEL_4);//����TIM14ͨ��4
	
	do
	{
	}
  while( HAL_TIM_PWM_Start(&TIM4_Handler,TIM_CHANNEL_1) != HAL_OK ) ;                //����PWMͨ��1
	
	do
	{
	}
  while( HAL_TIM_PWM_Start(&TIM4_Handler,TIM_CHANNEL_2) != HAL_OK ) ;                //����PWMͨ��2
	
	do
	{
	}
  while( HAL_TIM_PWM_Start(&TIM4_Handler,TIM_CHANNEL_3) != HAL_OK ) ;                //����PWMͨ��3
	
	do
	{
	}
  while( HAL_TIM_PWM_Start(&TIM4_Handler,TIM_CHANNEL_4)!= HAL_OK ) ;                //����PWMͨ��4
}


//��ʱ���ײ�������ʱ��ʹ�ܣ���������
//�˺����ᱻHAL_TIM_PWM_Init()����
//htim:��ʱ�����
void HAL_TIM_PWM_MspInit(TIM_HandleTypeDef *htim)
{
	GPIO_InitTypeDef GPIO_Initure;
	__HAL_RCC_TIM4_CLK_ENABLE();			//ʹ�ܶ�ʱ��14
	__HAL_RCC_GPIOD_CLK_ENABLE();			//����GPIODʱ��
	
	GPIO_Initure.Pin = GPIO_PIN_12|GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;           	//PD12
	GPIO_Initure.Mode = GPIO_MODE_AF_PP;  	//�����������
	GPIO_Initure.Pull = GPIO_PULLUP;          //����
	GPIO_Initure.Speed = GPIO_SPEED_HIGH;     //����
	GPIO_Initure.Alternate = GPIO_AF2_TIM4;	  //PD12����ΪTIM4_CH1
	HAL_GPIO_Init(GPIOD,&GPIO_Initure);
}


