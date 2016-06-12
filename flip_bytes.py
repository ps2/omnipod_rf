#!/usr/bin/env python2

import argparse
import binascii

def main(options=None):
    parser = argparse.ArgumentParser(description='Invert bits of a packet (given as a hex string).')
    parser.add_argument('data', metavar='data', type=str, nargs='+',
                        help='data as a hex string')

    args = parser.parse_args()
    bytes = map(lambda x: ord(x) ^ 0xff, args.data[0].decode("hex"))
    print binascii.hexlify(bytearray(bytes))

if __name__ == '__main__':
    main()
