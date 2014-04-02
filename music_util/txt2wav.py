# encoding=utf-8
'''Convert text format file to WAV file.'''
from __future__ import print_function

import argparse
import math
import numpy
import scipy.io.wavfile


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input_file', type=argparse.FileType('r'))
    arg_parser.add_argument('output_filename')

    args = arg_parser.parse_args()

    chunks = []

    for line in args.input_file:
        duration, frequency = line.strip().split()
        duration = float(duration)
        frequency = int(frequency)

        chunks.append(sine(frequency, duration))

    data = numpy.concatenate(chunks, axis=1)
    scipy.io.wavfile.write(args.output_filename, 44100, data)


def sine(frequency, seconds, sample_rate=44100):
    # http://milkandtang.com/blog/2013/02/16/making-noise-in-python/
    # http://stackoverflow.com/questions/9794616/
    # concatenating-synthesized-tones-in-python
    length = int(seconds * sample_rate)
    factor = float(frequency) * (math.pi * 2) / sample_rate
    data = numpy.sin(numpy.arange(length) * factor) * 2 ** 15 * 0.8
    return data.astype(numpy.int16)


if __name__ == '__main__':
    main()
