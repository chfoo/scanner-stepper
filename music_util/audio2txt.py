# encoding=utf-8
'''Convert audio file to text format.

If aubio was not compiled with decoders, the audio file should be a
16-bit PCM WAV file.
'''
from __future__ import print_function, division

import argparse
import aubio
import itertools
import numpy


NOTES = numpy.array(tuple(itertools.chain(
    [0],
    [
    int(440.0 * pow(1.05946, note_num - 49))
    for note_num in range(1, 89)
    ]
)))


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('input_filename')
    arg_parser.add_argument('output_file', type=argparse.FileType('w'))
    arg_parser.add_argument('--nearest', action='store_true')

    args = arg_parser.parse_args()
    pitches = get_pitches(args.input_filename)

    pitch_data = []

    prev_confidence = 0.0
    prev_frequency = 0
    prev_seconds = 0.0
    bin_seconds = 0.0

    for offset_seconds, frequency, confidence in pitches:
        if confidence > prev_confidence and confidence > 0.5:
            if args.nearest:
                frequency = find_nearest(NOTES, frequency)

            prev_frequency = int(frequency)
            prev_confidence = confidence

        bin_seconds += offset_seconds - prev_seconds
        prev_seconds = offset_seconds

        if bin_seconds >= 0.1:
            if pitch_data and pitch_data[-1][1] == prev_frequency:
                pitch_data[-1][0] += bin_seconds
            else:
                pitch_data.append([bin_seconds, prev_frequency])

            bin_seconds = 0.0
            prev_confidence = 0.0
            prev_frequency = 0

    for duration, frequency in pitch_data:
        args.output_file.write('{0} {1}\n'.format(duration, frequency))


def get_pitches(filename, hop_size=512, window_size=4096):
    source = aubio.source(filename, 0, hop_size)
    sample_rate = source.samplerate
    pitch_detector = aubio.pitch('default', window_size, hop_size, sample_rate)
    sample_counter = 0

    while True:
        samples, num_samples = source()
        frequency = int(pitch_detector(samples)[0])
        confidence = pitch_detector.get_confidence()
        offset_seconds = sample_counter / sample_rate

        yield (offset_seconds, frequency, confidence)

        sample_counter += num_samples

        if num_samples < hop_size:
            break


def find_nearest(array, value):
    # http://stackoverflow.com/questions/2566412/
    # find-nearest-value-in-numpy-array
    idx = (numpy.abs(array - value)).argmin()
    return array[idx]

if __name__ == '__main__':
    main()
