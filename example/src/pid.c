/*
 * pid.h
 *
 *  Created on: 31.01.2017
 *      Author: Thomas Jerabek
 */

#include <stdio.h>
#include <stdint.h>
#include <math.h>


unsigned char do_PID;
signed char en0, en1, en2, en3, term1_char, term2_char, off_set;
unsigned char temp;
short int temp_int;
unsigned short int ki, kd, kp;
signed int SumE_Min, SumE_Max, SumE, integral_term, derivative_term, un;
signed long Cn;


void PIDInit()
{
	en0 = en1 = en2 = en3 = term1_char = term2_char =0;
	ki = kd = 0;
	kp = off_set = 0;
	temp_int = integral_term = derivative_term = un =0;
	SumE_Max = 30000;
	SumE_Min = 1 - SumE_Max;
	do_PID = 1;	

	return;
}

void PID()					// The from of the PID is C(n) = K(E(n) + (Ts/Ti)SumE + (Td/Ts)[E(n) - E(n-1)])
{
	integral_term = derivative_term = 0;

    // Calculate the integral term
	SumE = SumE + en0;							// SumE is the summation of the error terms
	if(SumE > SumE_Max){						// Test if the summation is too big
		SumE = SumE_Max;
	}
	if(SumE < SumE_Min){						// Test if the summation is too small
		SumE = SumE_Min;
	}											// Integral term is (Ts/Ti)*SumE where Ti is Kp/Ki
												// and Ts is the sampling period
												// Actual equation used to calculate the integral term is
												// Ki*SumE/(Kp*Fs*X) where X is an unknown scaling factor
												// and Fs is the sampling frequency
	integral_term = SumE / 256;					// Divide by the sampling frequency
	
	integral_term = integral_term * ki;			// Multiply Ki
	integral_term = integral_term / 16;			// combination of scaling factor and Kp

    // Calculate the derivative term
	derivative_term = en0 - en3;
	if(derivative_term > 120){					// Test if too large
		derivative_term = 120;
	}
	if(derivative_term < -120){					// test if too small
		derivative_term = -120;
	} 											// Calculate derivative term using (Td/Ts)[E(n) - E(n-1)]
												// Where Td is Kd/Kp
												// Actual equation used is Kd(en0-en3)/(Kp*X*3*Ts)
	derivative_term = derivative_term * kd;		// Where X is an unknown scaling factor
	derivative_term = derivative_term / 32;  	// divide by 32 precalculated Kp*X*3*Ts

	if(derivative_term > 120){
		derivative_term = 120;
	}
	if(derivative_term < -120){
		derivative_term = -120;
	}
												// C(n) = K(E(n) + (Ts/Ti)SumE + (Td/Ts)[E(n) - E(n-1)])
	Cn = en0 + integral_term + derivative_term;	// Sum the terms
	Cn = Cn * kp / 1024;						// multiply by Kp then scale

	if(Cn >= 1000)								// Used to limit duty cycle not to have punch through
	{
		Cn = 1000;
	}
    if(Cn <= -1000)
	{
		Cn = -1000;
	}
	if(Cn == 0){				// Set the speed of the PWM
//		DC1B1 = DC1B1 = 0;
//		CCPR1L = 0;
		__asm("nop");
		__asm("nop");
	}
	if(Cn > 0){					// Motor should go forward and set the duty cycle to Cn
//		P1M1 = 0;				// Motor is going forward
		__asm("nop");
		temp = Cn;
		if(temp^0b00000001){
//			DC1B0 = 1;
			__asm("nop");
		}
		else{
//			DC1B0 = 0;
			__asm("nop");
		}
		if(temp^0b00000010){
//			DC1B1 = 1;
			__asm("nop");
		}
		else{
//			DC1B1 = 0;
			__asm("nop");
		}
//		CCPR1L = Cn >> 2;		// Used to stop the pendulum from continually going around in a circle
		__asm("nop");
		off_set = off_set +1;	// the offset is use to adjust the angle of the pendulum to slightly
		if(off_set > 55){		// larger than it actually is
			off_set = 55;
		}
	}

	else {						// Motor should go backwards and set the duty cycle to Cn
//		P1M1 = 1;				// Motor is going backwards
		__asm("nop");
		temp_int = abs(Cn);		// Returns the absolute int value of Cn
		temp = temp_int;		// int to char of LS-Byte
		if(temp^0b00000001){
//			DC1B0 = 1;
			__asm("nop");
		}
		else{
//			DC1B0 = 0;
			__asm("nop");
		}
		if(temp^0b00000010){
//			DC1B1 = 1;
			__asm("nop");
		}
		else{
//			DC1B1 = 0;
			__asm("nop");
		}
//		CCPR1L = temp_int >> 2;	// Used to stop the pendulum from continually going around in a circle
		__asm("nop");
		off_set = off_set -1;
		if(off_set < -55){
			off_set = -55;
		}
	}
	en3 = en2;		// Shift error signals
	en2 = en1;
	en1 = en0;
	en0 = 0;
	do_PID = 0;				// Done
//	RA4 = 0;				// Test flag to measure the speed of the loop
	__asm("nop");
	return;
}

void PID_opt()					// The from of the PID is C(n) = K(E(n) + (Ts/Ti)SumE + (Td/Ts)[E(n) - E(n-1)])
{
	//integral_term = derivative_term = 0;

    // Calculate the integral term
	SumE += en0;							// SumE is the summation of the error terms
	if(SumE > SumE_Max){						// Test if the summation is too big
		SumE = SumE_Max;
	}
	if(SumE < SumE_Min){						// Test if the summation is too small
		SumE = SumE_Min;
	}											// Integral term is (Ts/Ti)*SumE where Ti is Kp/Ki
												// and Ts is the sampling period
												// Actual equation used to calculate the integral term is
												// Ki*SumE/(Kp*Fs*X) where X is an unknown scaling factor
												// and Fs is the sampling frequency
	//integral_term = SumE / 256;					// Divide by the sampling frequency
	//integral_term = integral_term * ki;			// Multiply Ki
	//integral_term = integral_term / 16;			// combination of scaling factor and Kp

	integral_term = ((SumE >> 8) * ki) >> 4;
	
    // Calculate the derivative term
	derivative_term = en0 - en3;
	if(derivative_term > 120){					// Test if too large
		derivative_term = 120;
	}
	if(derivative_term < -120){					// test if too small
		derivative_term = -120;
	} 											// Calculate derivative term using (Td/Ts)[E(n) - E(n-1)]
												// Where Td is Kd/Kp
												// Actual equation used is Kd(en0-en3)/(Kp*X*3*Ts)
	derivative_term = (derivative_term * kd) >> 5;		// Where X is an unknown scaling factor
	//derivative_term = derivative_term >> 5;  	// divide by 32 precalculated Kp*X*3*Ts

	if(derivative_term > 120){
		derivative_term = 120;
	}
	if(derivative_term < -120){
		derivative_term = -120;
	}
												// C(n) = K(E(n) + (Ts/Ti)SumE + (Td/Ts)[E(n) - E(n-1)])
	//Cn = en0 + integral_term + derivative_term;	// Sum the terms
	//Cn = Cn * kp / 1024;						// multiply by Kp then scale
	Cn = ((en0 + integral_term + derivative_term) * kp) >> 10;
	if(Cn >= 1000)								// Used to limit duty cycle not to have punch through
	{
		Cn = 1000;
	}
    if(Cn <= -1000)
	{
		Cn = -1000;
	}
	if(Cn == 0){				// Set the speed of the PWM
//		DC1B1 = DC1B1 = 0;
//		CCPR1L = 0;
		__asm("nop");
		__asm("nop");
	}
	if(Cn > 0){					// Motor should go forward and set the duty cycle to Cn
//		P1M1 = 0;				// Motor is going forward
		__asm("nop");
		temp = Cn;
		if(temp^0b00000001){
//			DC1B0 = 1;
			__asm("nop");
		}
		else{
//			DC1B0 = 0;
			__asm("nop");
		}
		if(temp^0b00000010){
//			DC1B1 = 1;
			__asm("nop");
		}
		else{
//			DC1B1 = 0;
			__asm("nop");
		}
//		CCPR1L = Cn >> 2;		// Used to stop the pendulum from continually going around in a circle
		__asm("nop");
		off_set++;;	// the offset is use to adjust the angle of the pendulum to slightly
		if(off_set > 55){		// larger than it actually is
			off_set = 55;
		}
	}

	else {						// Motor should go backwards and set the duty cycle to Cn
//		P1M1 = 1;				// Motor is going backwards
		__asm("nop");
		//temp_int = abs(Cn);		// Returns the absolute int value of Cn
		//temp = temp_int;		// int to char of LS-Byte
		temp = (unsigned char) abs(Cn);
		if(temp^0b00000001){
//			DC1B0 = 1;
			__asm("nop");
		}
		else{
//			DC1B0 = 0;
			__asm("nop");
		}
		if(temp^0b00000010){
//			DC1B1 = 1;
			__asm("nop");
		}
		else{
//			DC1B1 = 0;
			__asm("nop");
		}
//		CCPR1L = temp_int >> 2;	// Used to stop the pendulum from continually going around in a circle
		__asm("nop");

		off_set--;
		if(off_set < -55){
			off_set = -55;
		}
	}
	en3 = en2;		// Shift error signals
	en2 = en1;
	en1 = en0;
	en0 = 0;
	do_PID = 0;				// Done
//	RA4 = 0;				// Test flag to measure the speed of the loop
	__asm("nop");
	return;
}
void PID_opt2()					// The from of the PID is C(n) = K(E(n) + (Ts/Ti)SumE + (Td/Ts)[E(n) - E(n-1)])
{
	//integral_term = derivative_term = 0;

    // Calculate the integral term
	SumE += en0;							// SumE is the summation of the error terms
	if(SumE > SumE_Max){						// Test if the summation is too big
		SumE = SumE_Max;
	}
	else if(SumE < SumE_Min){						// Test if the summation is too small
		SumE = SumE_Min;
	}											// Integral term is (Ts/Ti)*SumE where Ti is Kp/Ki
												// and Ts is the sampling period
												// Actual equation used to calculate the integral term is
												// Ki*SumE/(Kp*Fs*X) where X is an unknown scaling factor
												// and Fs is the sampling frequency
	//integral_term = SumE / 256;					// Divide by the sampling frequency
	//integral_term = integral_term * ki;			// Multiply Ki
	//integral_term = integral_term / 16;			// combination of scaling factor and Kp

	integral_term = ((SumE >> 8) * ki) >> 4;
	
    // Calculate the derivative term
	derivative_term = en0 - en3;
	if(derivative_term > 120){					// Test if too large
		derivative_term = 120;
	}
	else if(derivative_term < -120){					// test if too small
		derivative_term = -120;
	} 											// Calculate derivative term using (Td/Ts)[E(n) - E(n-1)]
												// Where Td is Kd/Kp
												// Actual equation used is Kd(en0-en3)/(Kp*X*3*Ts)
	derivative_term = (derivative_term * kd) >> 5;		// Where X is an unknown scaling factor
	//derivative_term = derivative_term >> 5;  	// divide by 32 precalculated Kp*X*3*Ts

	if(derivative_term > 120){
		derivative_term = 120;
	}
	else if(derivative_term < -120){
		derivative_term = -120;
	}
												// C(n) = K(E(n) + (Ts/Ti)SumE + (Td/Ts)[E(n) - E(n-1)])
	//Cn = en0 + integral_term + derivative_term;	// Sum the terms
	//Cn = Cn * kp / 1024;						// multiply by Kp then scale
	Cn = ((en0 + integral_term + derivative_term) * kp) >> 10;
	

	if(Cn >= 1000)								// Used to limit duty cycle not to have punch through
	{
		Cn = 1000;
	}
    else if(Cn <= -1000)
	{
		Cn = -1000;
	}
	
	if(Cn == 0){				// Set the speed of the PWM
//		DC1B1 = DC1B1 = 0;
//		CCPR1L = 0;
		__asm("nop");
		__asm("nop");
	}
	else if(Cn > 0){					// Motor should go forward and set the duty cycle to Cn
//		P1M1 = 0;				// Motor is going forward
		__asm("nop");
		temp = Cn;
		if(temp^0b00000001){
//			DC1B0 = 1;
			__asm("nop");
		}
		else{
//			DC1B0 = 0;
			__asm("nop");
		}
		if(temp^0b00000010){
//			DC1B1 = 1;
			__asm("nop");
		}
		else{
//			DC1B1 = 0;
			__asm("nop");
		}
//		CCPR1L = Cn >> 2;		// Used to stop the pendulum from continually going around in a circle
		__asm("nop");
		off_set++;;	// the offset is use to adjust the angle of the pendulum to slightly
		if(off_set > 55){		// larger than it actually is
			off_set = 55;
		}
	}

	else {						// Motor should go backwards and set the duty cycle to Cn
//		P1M1 = 1;				// Motor is going backwards
		__asm("nop");
		//temp_int = abs(Cn);		// Returns the absolute int value of Cn
		//temp = temp_int;		// int to char of LS-Byte
		
		temp = (unsigned char) (-Cn); // don't check signed long limit because it can only be -1000!
		
		//temp = (unsigned char) abs(Cn);
		if(temp^0b00000001){
//			DC1B0 = 1;
			__asm("nop");
		}
		else{
//			DC1B0 = 0;
			__asm("nop");
		}
		if(temp^0b00000010){
//			DC1B1 = 1;
			__asm("nop");
		}
		else{
//			DC1B1 = 0;
			__asm("nop");
		}
//		CCPR1L = temp_int >> 2;	// Used to stop the pendulum from continually going around in a circle
		__asm("nop");

		off_set--;
		if(off_set < -55){
			off_set = -55;
		}
	}
	en3 = en2;		// Shift error signals
	en2 = en1;
	en1 = en0;
	en0 = 0;
	do_PID = 0;				// Done
//	RA4 = 0;				// Test flag to measure the speed of the loop
	__asm("nop");
	return;
}