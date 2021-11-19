/*
 ===================================================================================
 Name        : extract_raw_data.c
 Author      : Infineon Technologies
 Version     :
 Copyright   : 2014-2017, Infineon Technologies AG
 Description : Example of how to extract raw data using the C communication library
 ===================================================================================
 */

/*
 * Copyright (c) 2014-2017, Infineon Technologies AG
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,are permitted provided that the
 * following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
 * disclaimer.
 *
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
 * disclaimer in the documentation and/or other materials provided with the distribution.
 *
 * Neither the name of the copyright holders nor the names of its contributors may be used to endorse or promote
 * products derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE  FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY,OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <stdio.h>
#include <string.h>
#include "include/Protocol.h"
#include "include/COMPort.h"
#include "include/EndpointRadarBase.h"

#define AUTOMATIC_DATA_FRAME_TRIGGER (1)		// define if automatic trigger is active or not

#define AUTOMATIC_DATA_TRIGER_TIME_US (1000000)	// get ADC data each 1ms in automatic trigger mode

#define FRAMES (1)

#define SAMPLES_PER_FRAME (4096)

#define TOTAL_SAMPLES (FRAMES * SAMPLES_PER_FRAME)

float ADC_data[TOTAL_SAMPLES];
int frame_index = 0;
int done = 0;


// called every time ep_radar_base_get_frame_data method is called to return measured time domain signals
void received_frame_data(void* context,
						int32_t protocol_handle,
		                uint8_t endpoint,
						const Frame_Info_t* frame_info)
{
	// Print the sampled data which can be found in frame_info->sample_data

	// Original version: only samples of first chirp
	/*
	for (uint32_t i = 0; i < frame_info->num_samples_per_chirp; i++)
	{
		printf("ADC sample %d: %f\n", i, frame_info->sample_data[i]);
		if (i==4095){
			printf("hi\n");
		}
	}
	*/

	// Modified version: samples from all chirps
	/*
	for (uint32_t i = 0; i < SAMPLES_PER_FRAME; i++)
	{
		printf("ADC sample %d: %f\n", i, frame_info->sample_data[i]);
		if (i==4095){
			printf("hi\n");
		}
	}
	*/

	// Save data to file, without print on terminal
	/*
	int written = 0;
	FILE *f = fopen("..\\P2G_raw-data_C\\raw-data.dat", "a+");
	written = fwrite(frame_info->sample_data, sizeof(uint8_t), sizeof(frame_info->sample_data), f);
	if (written == 0){
		printf("Error during writing to file!\n");
	}
	fclose(f);
	*/

	// Better to save in local variable, and then print on file after all frames are acquired
	int start_index = frame_index * SAMPLES_PER_FRAME;
	int stop_index = frame_index * SAMPLES_PER_FRAME + SAMPLES_PER_FRAME - 1;
	printf("Frame: %d\n", frame_index);
	for (uint32_t i = 0; i < SAMPLES_PER_FRAME; i++)
	{
		ADC_data[start_index+i] = frame_info->sample_data[i];
	}
	frame_index++;
	if (frame_index >= FRAMES){
		done = 1;
	}
}

int radar_auto_connect(void)
{
	int radar_handle = 0;
	int num_of_ports = 0;
	char comp_port_list[256];
	char* comport;
	const char *delim = ";";

	//----------------------------------------------------------------------------

	num_of_ports = com_get_port_list(comp_port_list, (size_t)256);

	if (num_of_ports == 0)
	{
		return -1;
	}
	else
	{
		comport = strtok(comp_port_list, delim);

		while (num_of_ports > 0)
		{
			num_of_ports--;

			// open COM port
			radar_handle = protocol_connect(comport);

			if (radar_handle >= 0)
			{
				break;
			}

			comport = strtok(NULL, delim);
		}

		return radar_handle;
	}

}

int main(void)
{
	int res = -1;
	int protocolHandle = 0;
	int endpointRadarBase = 0;
	int frame = 1;

	// open COM port
	protocolHandle = radar_auto_connect();

	// get endpoint ids
	if (protocolHandle >= 0)
	{
		for (int i = 1; i <= protocol_get_num_endpoints(protocolHandle); ++i) {
			// current endpoint is radar base endpoint
			if (ep_radar_base_is_compatible_endpoint(protocolHandle, i) == 0) {
				endpointRadarBase = i;
				continue;
			}
		}
	}


	if (endpointRadarBase >= 0)
	{
		// register call back functions for adc data
		ep_radar_base_set_callback_data_frame(received_frame_data, NULL);

		// enable/disable automatic trigger
		if (AUTOMATIC_DATA_FRAME_TRIGGER)
		{
			res = ep_radar_base_set_automatic_frame_trigger(protocolHandle,
															endpointRadarBase,
															AUTOMATIC_DATA_TRIGER_TIME_US);
		}
		else
		{
			res = ep_radar_base_set_automatic_frame_trigger(protocolHandle,
															endpointRadarBase,
															0);
		}
		while (done == 0)
		{
			// get raw data
			res = ep_radar_base_get_frame_data(protocolHandle,
											   endpointRadarBase,
											   1);
		};
		int written = 0;
		FILE *f = fopen("..\\P2G_raw-data_C\\raw-data.txt", "w+");
		for (uint32_t i = 0; i < TOTAL_SAMPLES; i++)
		{
			fprintf(f, "%f\n", ADC_data[i]);
		}
		fclose(f);
	}

	return res;
}
