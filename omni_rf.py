import numpy as np
import crcmod

def rolling(a, window):
    shape = (a.size - window + 1, window)
    strides = (a.itemsize, a.itemsize)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def find_offsets(samples, samples_per_bit, minimum_bits=80):
    signs = np.array(samples >= 0, int)
    differences = np.diff(signs)
    crossings = np.nonzero((differences < 0) | (differences > 0))[0]
    cumul_widths = crossings[1:] - crossings[0]
    widths = (cumul_widths[1:] - cumul_widths[:-1])
    phases = widths % samples_per_bit
    # rotate phases on left side to right
    phases[phases<(samples_per_bit/2)]+=samples_per_bit

    # Rolling 4 point average of phase; if we're within a half sample of the
    # expected bitrate, then this is packet data.
    packet_detect = np.absolute(rolling(phases, 4).mean(axis=1) - samples_per_bit)
    packet_detect = rolling(packet_detect, 4).max(axis=1) < 0.5

    # Bookend
    packet_detect_crossings = np.nonzero(np.diff(packet_detect))[0]
    if packet_detect[0]:
        packet_detect_crossings = np.insert(packet_detect_crossings, 0, 0)
    if packet_detect[-1]:
        packet_detect_crossings = np.append(packet_detect_crossings, len(cumul_widths)-9)
    #print "packet_detect[0] = %s" % packet_detect[0]
    #print "packet_detect_crossings = %s" % packet_detect_crossings
    startstop = packet_detect_crossings.reshape(-1, 2)
    startstop[:,1] += 8
    startstop[:,0] += 1
    offsets = [x for x in cumul_widths.take(startstop) if (x[1] - x[0]) >= (minimum_bits*samples_per_bit)]
    return offsets

def get_phase(samples, samples_per_bit):
    signs = np.array(samples >= 0, int)
    differences = np.diff(signs)
    crossings = np.nonzero((differences < 0) | (differences > 0))[0]
    cumulWidths = crossings[1:] - crossings[0]
    widths = (cumulWidths[1:] - cumulWidths[:-1])
    filtered_widths = widths[(widths > 46) & (widths < 55)]
    if filtered_widths.size == 0:
        return -1
    samples_per_bit = filtered_widths.mean()
    return (crossings % samples_per_bit).mean()

def resample(samples, offset, step):
    centers = np.arange(offset, samples.size, step)
    xp = np.arange(samples.size)
    return (centers, np.interp(centers, xp, samples))

def sample_bits(samples, samples_per_bit, phase_offset):
    bit_center_offset = phase_offset - (samples_per_bit / 2.0)
    (centers, bits) = resample(samples, bit_center_offset, samples_per_bit)
    bits = (bits > 0).astype(int)
    return bits

def manchester_decode(bits, manchester_variant):
    decoded = []
    if manchester_variant == 'ieee':
        hi_low = 0
        low_hi = 1
    else:
        hi_low = 1
        low_hi = 0

    prev = None
    for bit in bits:
        if prev == None:
            prev = bit
            continue

        if prev == 0 and bit == 1:
            d = low_hi
            prev = None
        elif prev == 1 and bit == 0:
            d = hi_low
            prev = None
        else:
            d = -1 # Error
            prev = bit

        decoded.append(d)
    return np.array(decoded)

def find_end_of_preamble(bits, preamble_byte):
    preamble = np.unpackbits(np.array([preamble_byte], dtype=np.uint8))
    if bits.size < 24:
        return -1
    for i in range(0, bits.size-16):
        if (bits[i:i+8] == preamble).all() and not (bits[i+8:i+16] == preamble).all():
            return i+16 # Skip sync word
    return -1

def decode_packet(samples, samples_per_bit, manchester_variant='ieee', preamble_byte=0x54):
    phase = get_phase(samples, samples_per_bit)
    if phase < 0:
        return []
    raw_bits = sample_bits(samples, samples_per_bit, phase)
    if raw_bits.size < 48: # Need at least 3 bytes
        return []
    m_bits = manchester_decode(raw_bits, manchester_variant)
    bits = np.trim_zeros(m_bits + 1) - 1 # Trim leading and trailing errors
    byte_start = find_end_of_preamble(bits, preamble_byte)
    return np.packbits(bits[byte_start:])

def compute_crc(data):
    #omnicrc8 = crcmod.mkCrcFun(0x1e0, initCrc=0xce, xorOut=0x00)
    omnicrc8 = crcmod.predefined.mkCrcFun('crc-8')
    return omnicrc8(data)
