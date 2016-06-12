# Decode Omnipod RF Packets


## Prerequisites

* [GNURadio](http://gnuradio.org/), or at least the gnuradio python libraries.
* numpy


## Capturing data

I use [SDR# (SDR Sharp)](http://airspy.com/download/) to capture my iq files, and there are many different ways of doing this. But whatever software you use, you'll need to capture at 2024000 samples per second, and tune your SDR to 433.90MHz.

It should look like this in the end:

![alt text](https://files.slack.com/files-tmb/T0B2X082E-F1FL1CK7F-fffd8ffa8e/pdm_1_packet_1024.png "PDM signal")

Notice that the signal appears to be alternating between two different frequencies. This is [FSK](https://en.wikipedia.org/wiki/Frequency-shift_keying) modulation.  If the signal is too weak (the waves are small), move the pod/pdm closer.  If the waves are clipped at the top, the signal is too strong.

## Running the decoder

```
$python omni_decode.py find_pdm.wav
Filename = find_pdm.wav
Using Volk machine: avx_64_mmx
158ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
457ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
756ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
1055ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
1353ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
1652ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
1951ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
2093ms:
2250ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
2549ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
2848ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
3146ms: 54c3000000005c00000000fbf9f8fbe0feb7d4fc8072
```
