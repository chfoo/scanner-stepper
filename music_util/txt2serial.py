# encoding=utf-8
'''Write text format file to serial.
'''
from __future__ import print_function

import argparse
import time
import math


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input_file', type=argparse.FileType('r'))
    arg_parser.add_argument('output_file', type=argparse.FileType('wb'))
    arg_parser.add_argument('--semitones', type=int)

    args = arg_parser.parse_args()

    output_file = args.output_file

    for line in args.input_file:
        duration, frequency = line.strip().split()
        duration = float(duration)
        millisecs = int(duration * 1000)
        frequency = int(frequency)

        if frequency:
            if args.semitones:
                frequency = int(adjust_frequency(frequency, args.semitones))

            output_file.write(
                '-32,{0},{1}\n'.format(frequency, millisecs).encode('ascii')
            )
        else:
            output_file.write(
                '-32,-1,{0}\n'.format(millisecs).encode('ascii')
            )

        time.sleep(max(0.01, duration - 0.01))


def adjust_frequency(frequency, semitones):
    note = 12.0 * math.log(frequency / 440.0, 2) + 49
    note += semitones
    return max(0, 440.0 * pow(1.05946, note - 49))


if __name__ == '__main__':
    main()
