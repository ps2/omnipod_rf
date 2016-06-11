import numpy as np

def rolling(a, window):
    shape = (a.size - window + 1, window)
    strides = (a.itemsize, a.itemsize)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def find_offsets(samples, samples_per_bit):
    signs = np.array(samples >= 0, int)
    differences = np.diff(signs)
    crossings = np.nonzero((differences < 0) | (differences > 0))[0]
    cumul_widths = crossings[1:] - crossings[0]
    widths = (cumul_widths[1:] - cumul_widths[:-1])
    phases = widths % samples_per_bit
    # rotate phases on left side to right
    phases[phases<(samples_per_bit/2)]+=samples_per_bit

    packet_detect = np.absolute(rolling(phases, 4).mean(axis=1) - samples_per_bit)
    packet_detect = rolling(packet_detect, 4).max(axis=1) < 0.5

    startstop = np.nonzero(np.diff(packet_detect))[0].reshape(-1, 2)
    startstop[:,1] += 8
    startstop[:,0] += 1
    packet_offsets = cumul_widths.take(startstop)
    return packet_offsets

def get_phase(samples, samples_per_bit):
    signs = np.array(samples >= 0, int)
    differences = np.diff(signs)
    crossings = np.nonzero((differences < 0) | (differences > 0))[0]
    cumulWidths = crossings[1:] - crossings[0]
    widths = (cumulWidths[1:] - cumulWidths[:-1])
    filtered_widths = widths[(widths > 46) & (widths < 55)]
    samples_per_bit = filtered_widths.mean()
    return (crossings % samples_per_bit).mean()

def resample(samples, offset, step):
    centers = np.arange(offset, samples.size, step)
    xp = np.arange(samples.size)
    return (centers, np.interp(centers, xp, samples))

def sample_bits(samples, samples_per_bit, phase_offset):
    samples_per_bit = 50.41
    bit_center_offset = phase_offset - (samples_per_bit / 2.0)
    (centers, bits) = resample(samples, bit_center_offset, samples_per_bit)
    bits = (bits > 0).astype(int)
    return bits

def manchester_decode(bits, mode='ieee'):
    decoded = []
    if mode == 'ieee':
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

def find_end_of_preamble(bits, preamble_byte = 0x57):
    preamble = np.unpackbits(np.array([preamble_byte], dtype=np.uint8))
    for i in range(0, bits.size):
        if (bits[i:i+8] == preamble).all() and not (bits[i+8:i+16] == preamble).all():
            return i
    return -1

def decode_packet(samples, samples_per_bit):
    phase = get_phase(samples, samples_per_bit)
    raw_bits = sample_bits(samples, samples_per_bit, phase)
    m_bits = manchester_decode(raw_bits, 'g_e_thomas')
    bits = np.trim_zeros(m_bits + 1) - 1 # Trim leading and trailing errors
    byte_start = find_end_of_preamble(bits)
    return np.packbits(bits[byte_start:])
