# encoding=utf-8
'''Write text format file to serial.
'''
from __future__ import print_function

import argparse
import math
import os.path
import subprocess
import time
import itertools


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input_file', type=argparse.FileType('r'))
    arg_parser.add_argument('output_file', type=argparse.FileType('wb'))
    arg_parser.add_argument('--semitones', type=int)
    arg_parser.add_argument('--adjust-duration', type=float)
    arg_parser.add_argument('--sync-tone', action='store_true')
    arg_parser.add_argument('--loop', type=int, default=1)

    args = arg_parser.parse_args()

    output_file = args.output_file

    if os.path.exists(output_file.name):
        subprocess.check_call(
            ['stty', '-F', output_file.name, '9600'] +
            '''
            -parenb -parodd cs8 -hupcl -cstopb cread clocal -crtscts
            -ignbrk -brkint -ignpar -parmrk inpck -istrip -inlcr -igncr
            -icrnl -ixon -ixoff
            -iuclc -ixany -imaxbel -iutf8
            -opost -olcuc -ocrnl -onlcr -onocr -onlret -ofill -ofdel nl0 cr0
            tab0 bs0 vt0 ff0
            -isig -icanon -iexten -echo -echoe -echok -echonl -noflsh -xcase
            -tostop -echoprt
            -echoctl -echoke
            '''.split()
        )
        time.sleep(2)

    if args.sync_tone:
        play_sync_tone(output_file, duration_factor=args.adjust_duration)
        time.sleep(2)

    lines = tuple(args.input_file)

    for line in itertools.chain(*itertools.repeat(lines, args.loop)):
        duration, frequency = line.strip().split()
        duration = float(duration)
        millisecs = int(duration * 1000)
        frequency = int(frequency)

        if frequency:
            if args.semitones:
                frequency = int(adjust_frequency(frequency, args.semitones))

            if args.adjust_duration:
                millisecs = int(duration * 1000.0 * args.adjust_duration)

            output_file.write(
                '-32,{0},{1}\n'.format(frequency, millisecs).encode('ascii')
            )

        time.sleep(duration)

    if args.sync_tone:
        time.sleep(2)
        play_sync_tone(output_file, duration_factor=args.adjust_duration)


def adjust_frequency(frequency, semitones):
    note = 12.0 * math.log(frequency / 440.0, 2) + 49
    note += semitones
    return max(0, 440.0 * pow(1.05946, note - 49))


def play_sync_tone(output_file, duration_factor=None):
    frequency = 220
    millisecs = 1000

    if duration_factor:
        millisecs = int(millisecs * duration_factor)

    output_file.write(
        '-32,{0},{1}\n'.format(frequency, millisecs).encode('ascii')
    )

if __name__ == '__main__':
    main()
