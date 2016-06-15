#!/usr/bin/env python2
from fskdemod import FskDemod
import argparse
import numpy as np
import omni_rf as omni

def main(options=None):

    parser = argparse.ArgumentParser(description='Decode omnipod packets from rtl_sdr or hackrf.')

    args = parser.parse_args()
    demod = FskDemod(None, '-')
    # run until ctrl-c
    demod.run()

if __name__ == '__main__':
    main()
