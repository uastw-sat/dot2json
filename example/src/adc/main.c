/*
 * main.c
 *
 *  Created on: 04.02.2016
 *      Author: Thomas Jerabek
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <XMC4500.h>
#include <adc.h>

#define MAX_ADC_VALUES  64
#define WCET_ANALYSIS    1


/** function prototypes **/
void bubblesort(uint16_t*, uint16_t);
void test(uint8_t);
uint64_t fib(uint64_t);
void processData(uint16_t);



/** simple sorting algorithm  **/
void bubblesort(uint16_t *array, uint16_t length)
{
    uint16_t i, j, tmp;

	for (i=0;i<length-1;i++) 
	{
		for (j=0;j<(length-i-1);j++) 
		{
			if (array[j] > array[j+1]) 
			{
				tmp = array[j];
				array[j] = array[j+1];
				array[j + 1] = tmp;
			}
		}
	}
}

/** useless function - only relevant for CFG tests**/
void test(uint8_t n)
{
	uint8_t i = 0;
	uint32_t x = 0;
	uint32_t y = 2;

	for(i=0;i<=n;i++)
	{
		if(x>y)
		{
			y = y+2;
		}
		else
		{
			x = x + i;
		}
	}
} 

/** calculates fibonacci number; maximum: fib(93) **/
uint64_t fib(uint64_t n)
{
  int  i, new, old, temp;
  new = 1;  old = 0;
  for(i=2;i<=n;i++)
  {
    temp = new;
    new = new + old;
    old = temp;
  }
  return new;
}




/** stub function **/
void processData(uint16_t sensorValue)
{
    if(sensorValue > 4095) // max. ADC Value
    {
        return;
    }
    while(sensorValue--)
    {
        __NOP();
    }
}


/** Main routine that reads values from ADC input P14.1, creates the mean value and uses it for further processing.
    Additionally, it sorts the values and toggles LED1. **/
int main(void)
{    
	uint16_t adc_values[MAX_ADC_VALUES];
	uint16_t adc_mean = 0;
	uint64_t ret = 0;
	uint16_t count = 0;
    uint8_t i;
    
    for(i=0;i<MAX_ADC_VALUES;i++) adc_values[i] = 0; // init array with zeros
    
    PORT1->IOCR0 |= 0x8000; // configure P1.1 output, push pull 
    
    ADC_Init(); 
   
    i = 0; // do not set i to 1 within the endless loop!
	while(1)
	{
	    ret = fib(20); // calculate fibonacci number, fib(20) = 6765
	    
		if(ret <300)
		{		
			adc_mean = 0;
			ADC_Stop();
			for(count=0;count<=MAX_ADC_VALUES;count++)
			{
				if(adc_mean>ret)
				{
					ret += 2;
				}
				else
				{
					adc_mean += count;
				}
			}

		}
		else if(ret == 6765)
		{
			(void) ADC_Read(); // read old ADC value and discard them -> clear result register
			ADC_Start(); // start analog digital conversion

			count = 0;
			while(count < MAX_ADC_VALUES)
			{
				adc_values[count] = ADC_Read_Blocking();  // read value from ADC - suitable for WCET Analysis
				count++; //
				ADC_FLAG = 0;   // clear ADC conversion done Flag
				ADC_Start();    // start another analog digital conversion
			}

		    adc_mean=0;
			for(count=0; count<MAX_ADC_VALUES; count++)
			{
				adc_mean += adc_values[count];
			}

			adc_mean = (uint16_t)(adc_mean/count);
		}
		else
		{
			ret = ADC_Read(); // read old ADC value and discard them -> clear result register
			ADC_Stop();
			adc_mean = ret;
		}


        PORT1->OUT = 0x2; // write 1 to P1.1 -> LED1 ON

		processData(adc_mean);  // do something with the adc data ... 
		
	    PORT1->OUT = 0x0; // write 0 to P1.1 -> LED1 OFF
		
		//bubblesort(adc_values, MAX_ADC_VALUES); // sort the values ascending
		    
		// exit condition (should not reachable but is necessary for WCET evaluation)
		// otherwise: disconnected Control-Flow-Graph -> OTAWA error 
		if(i==1)
		{
		    break;
		}
	}

	return 0;
}
