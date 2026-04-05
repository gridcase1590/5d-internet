#!/usr/bin/env python3
"""
cavity_tune.py — Find and characterize the resonance peak of the copper cavity.

Sweeps 4.5–5.0 GHz in 0.5 MHz steps, measures power at each frequency,
identifies the resonance peak and estimates Q factor.

Requires: HackRF One connected via USB, hackrf tools installed.
"""
import subprocess
import numpy as np
import sys
import time

# Configuration
F_START = 4.5e9      # Hz
F_STOP  = 5.0e9      # Hz
F_STEP  = 0.5e6      # Hz
SAMPLE_RATE = 2e6    # Hz
DWELL_TIME = 0.1     # seconds per frequency
GAIN = 40            # dB (LNA)

def measure_power(freq_hz, duration=DWELL_TIME):
    """Capture IQ samples at a given frequency and return mean power in dBm."""
    n_samples = int(SAMPLE_RATE * duration)
    cmd = [
        'hackrf_transfer',
        '-r', '/dev/stdout',
        '-f', str(int(freq_hz)),
        '-s', str(int(SAMPLE_RATE)),
        '-l', str(GAIN),
        '-n', str(n_samples)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        raw = np.frombuffer(result.stdout, dtype=np.int8)
        if len(raw) < 2:
            return -100.0
        iq = raw[0::2].astype(float) + 1j * raw[1::2].astype(float)
        power = np.mean(np.abs(iq)**2)
        if power > 0:
            return 10 * np.log10(power) - 30  # approximate dBm
        return -100.0
    except Exception as e:
        print(f"  Error at {freq_hz/1e9:.4f} GHz: {e}", file=sys.stderr)
        return -100.0

def find_q_factor(freqs, powers, peak_idx):
    """Estimate Q factor from -3dB bandwidth."""
    peak_power = powers[peak_idx]
    threshold = peak_power - 3.0  # -3 dB points
    
    # Find -3dB points
    left = peak_idx
    while left > 0 and powers[left] > threshold:
        left -= 1
    right = peak_idx
    while right < len(powers)-1 and powers[right] > threshold:
        right += 1
    
    bw = freqs[right] - freqs[left]
    f0 = freqs[peak_idx]
    
    if bw > 0:
        return f0 / bw
    return float('inf')

def main():
    print("=" * 60)
    print("  KK-5DCOMM Cavity Tuner")
    print("  Sweep: {:.3f} – {:.3f} GHz, step {:.1f} MHz".format(
        F_START/1e9, F_STOP/1e9, F_STEP/1e6))
    print("=" * 60)
    
    freqs = np.arange(F_START, F_STOP + F_STEP, F_STEP)
    powers = []
    
    print(f"\nSweeping {len(freqs)} frequencies...\n")
    
    for i, f in enumerate(freqs):
        p = measure_power(f)
        powers.append(p)
        bar = '█' * max(0, int((p + 80) / 2))
        print(f"  {f/1e9:8.4f} GHz | {p:7.1f} dBm | {bar}")
    
    powers = np.array(powers)
    peak_idx = np.argmax(powers)
    peak_freq = freqs[peak_idx]
    peak_power = powers[peak_idx]
    q_factor = find_q_factor(freqs, powers, peak_idx)
    
    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"  Resonance frequency:  {peak_freq/1e9:.4f} GHz")
    print(f"  Peak power:           {peak_power:.1f} dBm")
    print(f"  Estimated Q factor:   {q_factor:.0f}")
    print(f"  Target frequency:     4.7700 GHz")
    print(f"  Offset:               {(peak_freq - 4.77e9)/1e6:+.1f} MHz")
    print()
    
    if abs(peak_freq - 4.77e9) < 10e6:
        print("  ✓ CAVITY TUNED — within ±10 MHz of target")
    elif abs(peak_freq - 4.77e9) < 50e6:
        print("  △ CLOSE — adjust endcap depth to fine-tune")
        if peak_freq > 4.77e9:
            print("    Frequency too HIGH → sand endcap (increase height)")
        else:
            print("    Frequency too LOW → add copper shim (decrease height)")
    else:
        print("  ✗ OUT OF RANGE — check cavity dimensions")
    
    print()

if __name__ == '__main__':
    main()
