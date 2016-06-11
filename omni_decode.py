#!/usr/bin/env python2
from fskdemod import FskDemod
import argparse
import numpy as np
import omni_rf as omni

def main(options=None):

    parser = argparse.ArgumentParser(description='Decode omnipod packets from fsk iq wav file.')
    parser.add_argument('filename', metavar='filename', type=str, nargs='+',
                        help='filename of iq file')

    args = parser.parse_args()
    print "Filename = %s" % args.filename[0]
    demod = FskDemod(args.filename[0], '.demod.dat')
    demod.run()

    sample_rate = 2048000      # sample rate of sdr
    samples_per_bit = 50.41    # This was computed based on previously seen data.

    samples = np.fromfile('.demod.dat',dtype=np.float32)
    packets_offsets = omni.find_offsets(samples,samples_per_bit)

    for po in packets_offsets:
        packet_samples = samples[slice(*po)]
        bytes = omni.decode_packet(
            packet_samples,
            samples_per_bit,
            manchester_variant='ieee',
            preamble_byte=0x54)
        hex_str = "".join([format(n, '02x') for n in bytes])
        print "%sms: %s" % (int((po[0]/float(sample_rate))*1000), hex_str)

if __name__ == '__main__':
    main()
