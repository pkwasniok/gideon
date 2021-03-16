import wave
import os
from playsound import playsound

DIR = "C://repos/JSONN/"

num = 3

phonemes = ["sa", "mo", "chod", "au", "to", "wi", "taj"]


def play(infiles, num):
    data = []
    w = None
    for infile in infiles:
        w = wave.open(DIR + infile, 'rb')
        data.append([w.getparams(), w.readframes(w.getnframes())])
        w.close()

    output = None
    output = wave.open(DIR + str(num) + "gen.wav", 'w')
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()
    playsound(DIR + str(num) + "gen.wav", 'w')


while True:
    strinput = input()

    phonemes_output = []
    last_index = 0

    for i in range(0, 20):
        for phoneme in phonemes:
            if strinput.find(phoneme, last_index) == last_index:
                last_index += len(phoneme)
                phonemes_output.append(phoneme)

    print(phonemes_output)

    infiles = []

    for phonem in phonemes_output:
        infiles.append("p_" + phonem + ".wav")

    num += 1
    play(infiles, num)
