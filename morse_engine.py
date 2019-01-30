#!/usr/bin/python
# -*- coding: utf-8 -*-

# Morse Translator Engine


import time
import struct
import threading
import logging

import pyaudio
import numpy as np

# from highest to lowest: WARNING, INFO, DEBUG, NOTSET
logging.basicConfig(level=logging.DEBUG)


class Beep(object):

    CHUNK = 1024

    def __init__(self, volume=0.5, sampling_rate=44100, duration=1.0, sine_frequency=440.0):
        self._pyaudio_obj = pyaudio.PyAudio()
        self.volume = volume
        self.sampling_rate = sampling_rate
        self.duration = duration
        self.sine_frequency = sine_frequency
        self.recording = False

    def _generate_samples(self):
        """
        Generates audio samples
        :return: samples
        """
        samples = (
            np.sin(2 * np.pi * np.arange(
                self.sampling_rate * self.duration
            ) * self.sine_frequency / self.sampling_rate)
        ).astype(np.float32)

        return samples

    def open_stream(self, input_audio=False):
        """
        Opens an audio stream
        :return: stream
        """
        try:
            stream = self._pyaudio_obj.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sampling_rate,
                input=input_audio,
                output=True,
                frames_per_buffer=self.CHUNK
            )

            return stream

        except OSError as e:
            print(e)

    def play_beep(self):
        """
        Plays the samples on the stream
        :return: None
        """
        stream = self.open_stream()

        if not stream:
            return

        samples = self._generate_samples()
        stream.write(self.volume * samples)
        stream.stop_stream()
        stream.close()

    def read_beep(self):
        """

        :return:
        """
        stream = self.open_stream(input_audio=True)

        if not stream:
            return

        logging.debug("Stream initialized")

        frames = []

        while self.recording:
            data = stream.read(self.CHUNK)
            frames.append(data)

        data_int = []

        logging.debug("Converting")

        for f in frames:
            data_int.append(struct.unpack(str(self.CHUNK), f))

        print(data_int)

    def terminate_pyaudio(self):
        """
        Terminates the pyaudio object
        :return:
        """
        self._pyaudio_obj.terminate()


class InputThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.beep = Beep()
        self.recording = False
        self.stream = None

    def setup_recording(self):
        self.recording = True
        self.stream = self.beep.open_stream(input_audio=True)

    def run(self):
        self.setup_recording()
        frames = []
        data_int = []

        while self.recording:
            data = self.stream.read(self.beep.CHUNK)
            # data_int.append(struct.unpack(str(self.beep.CHUNK) + "B", data))
            data_int.append(int.from_bytes(data, byteorder='big', signed=True))
            frames.append(data)

        self.beep.


class MorseEngine(object):

    MORSE_DCT = {
        'A': '.-',
        'B': '-...',
        'C': '-.-.',
        'D': '-..',
        'E': '.',
        'F': '..-.',
        'G': '--.',
        'H': '....',
        'I': '..',
        'J': '.---',
        'K': '-.-',
        'L': '.-..',
        'M': '--',
        'N': '-.',
        'O': '---',
        'P': '.--.',
        'Q': '--.-',
        'R': '.-.',
        'S': '...',
        'T': '-',
        'U': '..-',
        'V': '...-',
        'W': '.--',
        'X': '-..-',
        'Y': '-.--',
        'Z': '--..',
        '1': '.----',
        '2': '..---',
        '3': '...--',
        '4': '....-',
        '5': '.....',
        '6': '-....',
        '7': '--...',
        '8': '---..',
        '9': '----.',
        '0': '-----',
        ',': '--..--',
        '.': '.-.-.-',
        '?': '..--..',
        '/': '-..-.',
        '-': '-....-',
        '(': '-.--.',
        ')': '-.--.-'
    }

    def __init__(self):
        self.beep = Beep()
        self.speed = 1
        self.space_duration = 1

    def encrypt(self, message):
        """
        Converts a string into a morse string
        :param message: String to convert
        :return: morse string
        """
        cipher = ''
        for letter in message:
            if letter != ' ':
                # Looks up the dictionary and adds the
                # correspponding morse code
                # along with a space to separate
                # morse codes for different characters
                cipher += self.MORSE_DCT[letter] + ' '
            else:
                # 1 space indicates different characters
                # and 2 indicates different words
                cipher += ' '

        return cipher

    def decrypt(self, message):
        """
        Converts a morse string into a string
        :param message: Morse string
        :return: String
        """
        # extra space added at the end to access the
        # last morse code
        message += ' '

        decipher = ''
        citext = ''

        for letter in message:

            # checks for space
            if letter != ' ':

                # counter to keep track of space
                i = 0

                # storing morse code of a single character
                citext += letter

            # in case of space
            else:
                # if i = 1 that indicates a new character
                i += 1

                # if i = 2 that indicates a new word
                if i == 2:

                    # adding space to separate words
                    decipher += ' '
                else:

                    # accessing the keys using their values (reverse of encryption)
                    decipher += list(
                        self.MORSE_DCT.keys()
                    )[list(
                        self.MORSE_DCT.values()
                    ).index(citext)]
                    citext = ''

        return decipher

    def convert_to_numeric(self, morse_string):
        """
        Converts a morse string into a list of numeric values
        :param morse_string: Morse-encoded string
        :return: List of numeric values
        """
        numeric_lst = []

        for character in morse_string:
            if character == " ":
                numeric_lst.append(0)

            elif character == ".":
                numeric_lst.append(0.5 * self.speed)

            elif character == "-":
                numeric_lst.append(1.5 * self.speed)

            else:
                raise ValueError("Unrecognized character in string")

        return numeric_lst

    def convert_to_audio(self, numeric_lst):
        """
        Converts a list of numeric values into audio beeps
        :param numeric_lst: List of integers
        :return: None
        """
        for i in numeric_lst:
            if i != 0:
                self.beep.duration = i
                self.beep.play_beep()

            else:
                time.sleep(0.5 * self.space_duration)


def main():
    engine = MorseEngine()
    message = "Hello World".upper()
    print("Message: {}".format(message))
    morse_str = engine.encrypt(message)
    print("Morse code: {}".format(morse_str))
    morse_numeric = engine.convert_to_numeric(morse_str)
    engine.convert_to_audio(morse_numeric)
    engine.beep.terminate_pyaudio()


def record():
    thread_input = InputThread()
    print("Recording start")
    thread_input.start()

    for i in range(10, 0, -1):
        print(i)
        time.sleep(1)

    thread_input.recording = False
    print("Recording stop")


if __name__ == "__main__":
    # main()
    record()
