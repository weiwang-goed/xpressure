import sounddevice as sd
import numpy as np
from datetime import datetime
from scipy.io import wavfile
import threading

fs = 22000
audioPath = './audio/'

sd.default.samplerate = fs
sd.default.channels = 1



def recordAudio(t):
    def thread_func(t, fname):
        myrecording = sd.rec(int(t * fs))
        sd.wait()
        wavfile.write(audioPath + fname, fs, myrecording)
        print("recording over!:", fname)

    now = datetime.now().strftime("%H.%M")
    fname = now + '.wav'
    print('file is: ', fname) 

    x = threading.Thread(target=thread_func, args=(t,fname))
    x.start()
    return audioPath+fname


def voiceCounting(wav):
    return 