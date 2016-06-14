#!/usr/bin/env python2

import argparse
import binascii
import sys
import omni_rf as omni

def main(options=None):
    parser = argparse.ArgumentParser(description='Check CRC8 an omnipod packet (given as a hex string).')
    parser.add_argument('data', metavar='data', type=str, nargs='+',
                        help='data as a hex string')

    args = parser.parse_args()
    hex_str = args.data[0]
    data = hex_str[:-2].decode("hex")
    crc = ord(hex_str[-2:].decode("hex"))
    computed_crc = omni.compute_crc(data)
    if computed_crc != crc:
        print "Invalid crc. Computed = %s" % hex(computed_crc)
        sys.exit(-1)
    else:
        print "OK!"
        sys.exit(0)

if __name__ == '__main__':
    main()
