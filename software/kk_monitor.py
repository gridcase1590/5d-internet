#!/usr/bin/env python3
"""
kk_monitor.py — Real-time monitoring dashboard for KK-5DCOMM experiment.

Displays four live panels in terminal:
  1. Spectrum (power vs frequency around f₁)
  2. Waterfall (time vs frequency heatmap)
  3. Eigenvalue tracker (Λ ratio over time)
  4. Status (detection state, Q factor, SNR)

Requires: HackRF One, numpy, hackrf tools.
Optional: matplotlib for graphical output (--gui flag).
"""
import numpy as np
import subprocess
import sys
import time
import argparse
import os
from datetime import datetime

# ═══ CONFIGURATION ═══
DEFAULT_FREQ = 4.77e9
SAMPLE_RATE = 2e6
FFT_SIZE = 1024
WATERFALL_ROWS = 40
GAIN = 40

# ═══ TERMINAL RENDERING ═══
BLOCKS = ' ░▒▓█'
SPARK = '▁▂▃▄▅▆▇█'

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def spark_line(values, width=60):
    """Render a sparkline from array of values."""
    if len(values) == 0:
        return ' ' * width
    mn, mx = np.min(values), np.max(values)
    rng = mx - mn if mx > mn else 1.0
    chars = []
    step = max(1, len(values) // width)
    for i in range(0, min(len(values), width * step), step):
        idx = int((values[i] - mn) / rng * 7)
        idx = max(0, min(7, idx))
        chars.append(SPARK[idx])
    return ''.join(chars)

def heatmap_char(val, mn, mx):
    """Map a value to a heatmap character."""
    if mx <= mn:
        return BLOCKS[0]
    idx = int((val - mn) / (mx - mn) * 4)
    return BLOCKS[max(0, min(4, idx))]

# ═══ SDR INTERFACE ═══
def capture_iq(freq_hz, n_samples=None):
    """Capture IQ samples from HackRF."""
    if n_samples is None:
        n_samples = FFT_SIZE * 16
    cmd = [
        'hackrf_transfer', '-r', '/dev/stdout',
        '-f', str(int(freq_hz)),
        '-s', str(int(SAMPLE_RATE)),
        '-l', str(GAIN),
        '-n', str(n_samples)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=5)
        raw = np.frombuffer(result.stdout, dtype=np.int8)
        if len(raw) < 2:
            return None
        return raw[0::2].astype(np.float64) + 1j * raw[1::2].astype(np.float64)
    except Exception:
        return None

def compute_spectrum(iq, fft_size=FFT_SIZE):
    """Compute power spectrum in dBm."""
    if iq is None or len(iq) < fft_size:
        return np.full(fft_size, -100.0)
    n_avg = len(iq) // fft_size
    psd = np.zeros(fft_size)
    for i in range(n_avg):
        seg = iq[i*fft_size:(i+1)*fft_size]
        spec = np.fft.fftshift(np.fft.fft(seg * np.hanning(fft_size)))
        psd += np.abs(spec)**2
    psd /= n_avg
    psd[psd == 0] = 1e-20
    return 10 * np.log10(psd) - 30

def compute_eigenvalues(iq, window_size=256):
    """Compute SVD eigenvalue ratio Λ."""
    if iq is None or len(iq) < window_size * 4:
        return 0.0, np.array([])
    n = (len(iq) // window_size) * window_size
    matrix = iq[:n].reshape(-1, window_size)
    p, n_cols = matrix.shape
    sigma2 = np.var(matrix)
    if sigma2 == 0:
        return 0.0, np.array([])
    matrix = matrix / np.sqrt(sigma2)
    U, s, Vh = np.linalg.svd(matrix, full_matrices=False)
    gamma = p / n_cols
    mp_edge = (1 + np.sqrt(gamma))**2
    lam = (s[0]**2) / mp_edge
    return lam, s[:8]

# ═══ DASHBOARD ═══
def render_dashboard(spectrum, waterfall, eigenvalues, lam_history, status, freq):
    """Render the four-panel terminal dashboard."""
    clear()
    W = 72
    ts = datetime.now().strftime('%H:%M:%S')

    print(f"  ╔{'═'*(W-4)}╗")
    print(f"  ║  KK-5DCOMM MONITOR  │  {freq/1e9:.4f} GHz  │  {ts}  {'':>{W-55}}║")
    print(f"  ╠{'═'*(W-4)}╣")

    # Panel 1: Spectrum
    print(f"  ║  SPECTRUM (power vs freq){'':>{W-30}}║")
    spec_line = spark_line(spectrum[FFT_SIZE//4:3*FFT_SIZE//4], W-8)
    print(f"  ║  {spec_line}  ║")
    peak_db = np.max(spectrum)
    floor_db = np.median(spectrum)
    print(f"  ║  peak: {peak_db:+.1f} dBm  │  floor: {floor_db:+.1f} dBm  │  SNR: {peak_db-floor_db:.1f} dB{'':>{W-62}}║")
    print(f"  ╟{'─'*(W-4)}╢")

    # Panel 2: Waterfall (last N rows)
    print(f"  ║  WATERFALL{'':>{W-15}}║")
    for row in waterfall[-8:]:
        compressed = row[FFT_SIZE//4:3*FFT_SIZE//4]
        step = max(1, len(compressed) // (W-8))
        mn, mx = np.min(waterfall), np.max(waterfall)
        chars = ''
        for i in range(0, min(len(compressed), (W-8)*step), step):
            chars += heatmap_char(compressed[i], mn, mx)
        print(f"  ║  {chars:<{W-8}}  ║")
    print(f"  ╟{'─'*(W-4)}╢")

    # Panel 3: Eigenvalues
    print(f"  ║  EIGENVALUE RATIO Λ (threshold: 3.0){'':>{W-43}}║")
    if len(lam_history) > 0:
        lam_line = spark_line(np.array(lam_history[-60:]), W-8)
        current_lam = lam_history[-1]
        marker = '  ████ DETECTION ████' if current_lam > 3.0 else ''
        print(f"  ║  {lam_line}  ║")
        print(f"  ║  Λ = {current_lam:.3f}  │  mean: {np.mean(lam_history):.3f}  │  max: {np.max(lam_history):.3f}{marker}{'':>{max(0,W-65-len(marker))}}║")
    else:
        print(f"  ║  {'waiting for data...':<{W-8}}  ║")
        print(f"  ║  {'':>{W-4}}║")
    print(f"  ╟{'─'*(W-4)}╢")

    # Panel 4: Status
    print(f"  ║  STATUS{'':>{W-12}}║")
    det = status.get('detection', False)
    streak = status.get('streak', 0)
    windows = status.get('windows', 0)
    det_str = '▲▲ ACTIVE' if det else '── nominal'
    print(f"  ║  detection: {det_str}  │  streak: {streak}/10  │  windows: {windows}{'':>{max(0,W-60)}}║")
    print(f"  ╚{'═'*(W-4)}╝")
    print(f"  Press Ctrl+C to stop")

# ═══ MAIN LOOP ═══
def main():
    parser = argparse.ArgumentParser(description='KK-5DCOMM Real-Time Monitor')
    parser.add_argument('--freq', type=float, default=DEFAULT_FREQ, help='Centre freq (Hz)')
    parser.add_argument('--duration', type=int, default=0, help='Duration in seconds (0=indefinite)')
    parser.add_argument('--interval', type=float, default=1.0, help='Update interval (s)')
    parser.add_argument('--logfile', type=str, default='kk_monitor.log')
    args = parser.parse_args()

    waterfall = [np.full(FFT_SIZE, -100.0) for _ in range(WATERFALL_ROWS)]
    lam_history = []
    status = {'detection': False, 'streak': 0, 'windows': 0}

    log = open(args.logfile, 'a')
    log.write(f"\n--- Monitor session {datetime.now().isoformat()} ---\n")

    start = time.time()
    try:
        while True:
            if args.duration > 0 and time.time() - start > args.duration:
                break

            iq = capture_iq(args.freq)
            spectrum = compute_spectrum(iq)
            lam, svs = compute_eigenvalues(iq)

            waterfall.append(spectrum)
            if len(waterfall) > WATERFALL_ROWS:
                waterfall.pop(0)

            lam_history.append(lam)
            status['windows'] += 1

            if lam > 3.0:
                status['streak'] += 1
                if status['streak'] >= 10:
                    status['detection'] = True
            else:
                status['streak'] = 0

            render_dashboard(spectrum, waterfall, svs, lam_history, status, args.freq)

            ts = datetime.now().strftime('%H:%M:%S')
            log.write(f"{ts},{lam:.4f},{status['streak']},{np.max(spectrum):.1f}\n")
            log.flush()

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n  Monitor stopped.")

    log.close()
    print(f"  Log saved to {args.logfile}")
    print(f"  Total windows: {status['windows']}")
    print(f"  Detection: {'YES' if status['detection'] else 'NO'}")

if __name__ == '__main__':
    main()
