import easygui
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
import os.path
plt.ion()

SAMPLES_PER_CHIRP = 64 # fast-time dimension
CHIRP_PER_FRAME = 16 # slow-time dimension
RX_ANTENNAS = 2 # spatial dimension
CHIRP_TIME = 300e-6 # s
FRAMES = 1
sampling_frequency = SAMPLES_PER_CHIRP / CHIRP_TIME # Hz
sampling_period = 1 / sampling_frequency # s

filename = None
while filename == None:
    filename = easygui.fileopenbox(title = "Choose *.txt file to analyse...", default = "*.txt")
print(filename)

rawSamples = np.genfromtxt(filename, delimiter = '')
totalSamples = len(rawSamples)
samples_in_frame = int(totalSamples / FRAMES)

FFT_FREQ_BINS = 256

for frame in range(FRAMES):
    # Datacube
    datacube = np.zeros((SAMPLES_PER_CHIRP, CHIRP_PER_FRAME, RX_ANTENNAS), dtype='complex_')

    for slowTimeIndex in range(CHIRP_PER_FRAME):
        for fastTimeIndex in range(SAMPLES_PER_CHIRP):
            for spatialIndex in range(RX_ANTENNAS):
                rawSamples_index = frame * samples_in_frame + 2 * spatialIndex + 4 * fastTimeIndex + slowTimeIndex * SAMPLES_PER_CHIRP
                datacube[fastTimeIndex, slowTimeIndex, spatialIndex] = np.add(rawSamples[rawSamples_index], 1j*rawSamples[rawSamples_index + 1])
    
    # A fast-time domain signal
    fastTime_signal = datacube[:,0,0]
    # Preprocessing on fast-time signal
    # DC offset removal
    fastTime_signal = fastTime_signal - np.mean(fastTime_signal)
    # Time
    ft_timeAxis = np.arange(start=0, stop=SAMPLES_PER_CHIRP*sampling_period, step=sampling_period)
    plt.plot(ft_timeAxis, np.real(fastTime_signal))
    plt.plot(ft_timeAxis, np.imag(fastTime_signal))
    plt.ylabel("Amplitude [% ADC scale]")
    plt.xlabel("Time [s]")
    plt.grid(True)
    ft_name = os.path.join('./P2G_processed-data', "ft_time.png")
    plt.savefig(ft_name)
    plt.show()
    plt.pause(1)
    plt.clf()
    # Frequency
    ft_FFT = np.fft.fft(fastTime_signal, n=FFT_FREQ_BINS)
    ft_FFT_magn = np.absolute(1 / len(fastTime_signal) * ft_FFT)
    ft_FFT_dB = 20 * np.log10(ft_FFT_magn)
    freqAxis = np.fft.fftfreq(FFT_FREQ_BINS)
    # freqAxis_Hz = freqAxis * sampling_frequency
    plt.plot(np.fft.fftshift(freqAxis), np.fft.fftshift(ft_FFT_dB))
    plt.ylabel("Spectrum magnitude [dB]")
    plt.xlabel("Frequency [Hz]")
    plt.grid(True)
    ft_name = os.path.join('./P2G_processed-data', "ft_freq.png")
    plt.savefig(ft_name)
    plt.show()
    plt.pause(1)
    plt.clf()

    # A slow-time domain signal
    slowTime_signal = datacube[0,:,0]
    # Preprocessing on fast-time signal
    # DC offset removal
    slowTime_signal = slowTime_signal - np.mean(slowTime_signal)
    # Time
    st_timeAxis = np.arange(start=0, stop=SAMPLES_PER_CHIRP*CHIRP_PER_FRAME*sampling_period, step=sampling_period*SAMPLES_PER_CHIRP)
    plt.plot(st_timeAxis, np.real(slowTime_signal))
    plt.plot(st_timeAxis, np.imag(slowTime_signal))
    plt.ylabel("Amplitude [% ADC scale]")
    plt.xlabel("Time [s]")
    plt.grid(True)
    st_name = os.path.join('./P2G_processed-data', "st_time.png")
    plt.savefig(st_name)
    plt.show()
    plt.pause(1)
    plt.clf()
    # Frequency
    st_FFT = np.fft.fft(slowTime_signal, n=FFT_FREQ_BINS)
    st_FFT_magn = np.absolute(1 / len(slowTime_signal) * st_FFT)
    st_FFT_dB = 20 * np.log10(st_FFT_magn)
    st_FFT_phase = np.angle(1 / len(slowTime_signal) * st_FFT)
    freqAxis = np.fft.fftfreq(FFT_FREQ_BINS)
    # freqAxis_Hz = freqAxis * sampling_frequency
    plt.plot(np.fft.fftshift(freqAxis), np.fft.fftshift(st_FFT_dB))
    plt.plot(np.fft.fftshift(freqAxis), np.fft.fftshift(st_FFT_phase))
    plt.ylabel("Spectrum magnitude [dB]")
    plt.xlabel("Frequency [Hz]")
    plt.grid(True)
    st_name = os.path.join('./P2G_processed-data', "st_freq.png")
    plt.savefig(st_name)
    plt.show()
    plt.pause(1)
    plt.clf()

    # Range-Doppler map computation
    rangeDopplerMap = np.abs(np.fft.fftshift(np.fft.fftn(datacube[:,:,0], s=(FFT_FREQ_BINS, FFT_FREQ_BINS), axes=(0,1))))
    rangeAxis = np.fft.fftshift(np.fft.fftfreq(FFT_FREQ_BINS))
    dopplerAxis = np.fft.fftshift(np.fft.fftfreq(FFT_FREQ_BINS))
    half_rangeAxis = np.split(rangeAxis, indices_or_sections=2)[1]
    half_rangeDopplerMap = np.split(rangeDopplerMap, indices_or_sections=2, axis=0)[1]
    # plt.imshow(np.abs(np.fft.fftshift(rangeDopplerMap)))
    df = DataFrame(half_rangeDopplerMap, index=half_rangeAxis, columns=dopplerAxis)
    plt.pcolor(df)
    rdm_name = os.path.join('./P2G_processed-data', "rdm.png")
    plt.savefig(rdm_name)
    plt.show()
    plt.pause(5)
    plt.clf()