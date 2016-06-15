#!/usr/bin/env python2

import argparse
import binascii
import json

def main(options=None):
    parser = argparse.ArgumentParser(description='Print out structured version of packet (given as a hex string).')
    parser.add_argument('data', metavar='data', type=str, nargs='+',
                        help='data as a hex string')
    parser.add_argument('--json', action='store_true',
                        help='print as json (default: text line)')

    args = parser.parse_args()
    hex_str = args.data[0]

    pod_address_1 = hex_str[0:8]
    byte5 = ord(hex_str[8:10].decode("hex"))
    packet_type = byte5 >> 5
    sequence = byte5 & 0b11111
    pod_address_2 = hex_str[10:18]
    body = ""
    message_type = ""
    if len(hex_str) > 20:
        unknown = hex_str[18:2]
        message_type = hex_str[18:2]
        body = hex_str[22:-2]
    crc = ord(hex_str[-2:].decode("hex"))

    # attr style
    #print "addr1=%s addr2=%s" % (addr1, addr2)

    # compact style:
    if args.json:
        obj = {
            "pod_address_1": pod_address_1,
            "packet_type": packet_type,
            "sequence": sequence,
            "pod_address_2": pod_address_2,
            "body": body,
            "crc": crc,
            "raw_packet": hex_str,
        }
        print json.dumps(obj, sort_keys=True,indent=4, separators=(',', ': '))
    else:
        print "ID1:%s PTYPE:%s SEQ:%d ID2:%s MTYPE:%s BODY:%s CRC:%02x" % (pod_address_1, format(packet_type, '#05b')[2:], sequence, pod_address_2, message_type, body, crc)

if __name__ == '__main__':
    main()
