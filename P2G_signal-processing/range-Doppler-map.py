import easygui
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fftshift
plt.ion()

SAMPLES_PER_CHIRP = 64 # fast-time dimension
CHIRP_PER_FRAME = 16 # slow-time dimension
RX_ANTENNAS = 2 # spatial dimension
CHIRP_TIME = 300e-6 # s
FRAMES = 10
sampling_frequency = SAMPLES_PER_CHIRP / CHIRP_TIME
sampling_period = 1 / sampling_frequency

filename = None
while filename == None:
    filename = easygui.fileopenbox(title = "Choose *.txt file to analyse...", default = "*.txt")
print(filename)

rawSamples = np.genfromtxt(filename, delimiter = '')
totalSamples = len(rawSamples)
samples_in_frame = int(totalSamples / FRAMES)

fig = plt.figure(1)
ax = fig.add_subplot(1,1,1)

for frame in range(FRAMES):
    plt.clf()
    # Datacube
    datacube = np.zeros((SAMPLES_PER_CHIRP, CHIRP_PER_FRAME, RX_ANTENNAS), dtype='complex_')

    for slowTimeIndex in range(CHIRP_PER_FRAME):
        for fastTimeIndex in range(SAMPLES_PER_CHIRP):
            for spatialIndex in range(RX_ANTENNAS):
                rawSamples_index = frame * samples_in_frame + 2 * spatialIndex + 4 * fastTimeIndex + slowTimeIndex * SAMPLES_PER_CHIRP
                datacube[fastTimeIndex, slowTimeIndex, spatialIndex] = np.add(rawSamples[rawSamples_index], 1j*rawSamples[rawSamples_index + 1])

    FFT_FREQ_BINS = 2**12

    # Range-Doppler map computation
    rangeDopplerMap = np.fft.fftn(datacube[:,:,1], s=(FFT_FREQ_BINS, FFT_FREQ_BINS), axes=(0,1))
    # plt.imshow(np.log(np.abs(np.fft.fftshift(rangeDopplerMap))**2))
    plt.imshow(np.abs(np.fft.fftshift(rangeDopplerMap))**2)
    plt.pause(2)
