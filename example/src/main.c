/*
 * main.c
 *
 *  Created on: 31.01.2017
 *      Author: Thomas Jerabek
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <XMC4500.h>
#include <pid.h>


int main(void)
{    
    uint8_t exitcond;

    PORT1->IOCR0 |= 0x8000; // configure P1.1 output, push pull 

    PIDInit();
 
    exitcond = 0; // do not set i to 1 within the endless loop!
	while(1)
	{
        PORT1->OUT = 0x2; // write 1 to P1.1 -> LED1 ON
 
        PID();
        
	    PORT1->OUT = 0x0; // write 0 to P1.1 -> LED1 OFF

        PID_opt();
        
        PID_opt2();


		// exit condition (should not reachable but is necessary for WCET evaluation)
		// otherwise: disconnected Control-Flow-Graph -> OTAWA error 
		if(exitcond==1)
		{
		    break;
		}
	}

	return 0;
}
