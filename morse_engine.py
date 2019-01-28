#!/usr/bin/python
# -*- coding: utf-8 -*-

# Morse Translator Engine


import time

import pyaudio
import numpy as np


class Beep(object):

    def __init__(self, volume=0.5, sampling_rate=44100, duration=1.0, sine_frequency=440.0):
        self._pyaudio_obj = pyaudio.PyAudio()
        self.volume = volume
        self.sampling_rate = sampling_rate
        self.duration = duration
        self.sine_frequency = sine_frequency

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

    def _open_stream(self):
        """
        Opens an audio stream
        :return: stream
        """
        try:
            stream = self._pyaudio_obj.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sampling_rate,
                output=True
            )

            return stream

        except OSError as e:
            print(e)

    def play_beep(self):
        """
        Plays the samples on the stream
        :return: None
        """
        stream = self._open_stream()

        if not stream:
            return

        samples = self._generate_samples()
        stream.write(self.volume * samples)
        stream.stop_stream()
        stream.close()

    def terminate_pyaudio(self):
        """
        Terminates the pyaudio object
        :return:
        """
        self._pyaudio_obj.terminate()


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

    @staticmethod
    def convert_to_numeric(morse_string):
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
                numeric_lst.append(0.5)

            elif character == "-":
                numeric_lst.append(1.5)

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
                time.sleep(0.5)


def main():
    engine = MorseEngine()
    message = "Hello World".upper()
    print("Message: {}".format(message))
    morse_str = engine.encrypt(message)
    print("Morse code: {}".format(morse_str))
    morse_numeric = engine.convert_to_numeric(morse_str)
    engine.convert_to_audio(morse_numeric)
    engine.beep.terminate_pyaudio()


if __name__ == "__main__":
    main()
