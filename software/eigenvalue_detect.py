#!/usr/bin/env python3
"""
eigenvalue_detect.py — KK signal detection via SVD of IQ covariance matrix.

Monitors a frequency band around f₁ ≈ 4.77 GHz. Computes singular values
of windowed IQ data. A KK coupling signal appears as an anomalous eigenvalue
exceeding the Marchenko-Pastur random matrix edge.

Detection criterion: Λ = σ_max / σ_MP > 3 for 10+ consecutive windows.
"""
import numpy as np
import subprocess
import sys
import time
import argparse
from datetime import datetime

# Marchenko-Pastur upper edge for a random matrix
def mp_edge(n, p, sigma2=1.0):
    """Upper edge of Marchenko-Pastur distribution."""
    gamma = p / n
    return sigma2 * (1 + np.sqrt(gamma))**2

def capture_iq(freq_hz, sample_rate, n_samples, gain=40):
    """Capture IQ samples from HackRF."""
    cmd = [
        'hackrf_transfer', '-r', '/dev/stdout',
        '-f', str(int(freq_hz)),
        '-s', str(int(sample_rate)),
        '-l', str(gain),
        '-n', str(n_samples)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        raw = np.frombuffer(result.stdout, dtype=np.int8)
        iq = raw[0::2].astype(np.float64) + 1j * raw[1::2].astype(np.float64)
        return iq
    except Exception as e:
        print(f"Capture error: {e}", file=sys.stderr)
        return None

def analyze_window(iq_data, window_size=256, n_windows=64):
    """
    Build a Hankel-like matrix from IQ data, compute SVD,
    return ratio of max singular value to MP edge.
    """
    n = min(len(iq_data), window_size * n_windows)
    iq_data = iq_data[:n]
    
    # Reshape into matrix: rows = windows, cols = samples per window
    n_complete = (len(iq_data) // window_size) * window_size
    iq_data = iq_data[:n_complete]
    matrix = iq_data.reshape(-1, window_size)
    
    p, n_cols = matrix.shape
    
    # Normalize
    sigma2 = np.var(matrix)
    if sigma2 == 0:
        return 0.0, np.array([])
    matrix = matrix / np.sqrt(sigma2)
    
    # SVD
    U, s, Vh = np.linalg.svd(matrix, full_matrices=False)
    
    # Marchenko-Pastur edge
    edge = mp_edge(n_cols, p)
    
    # Detection ratio
    lambda_ratio = (s[0]**2) / edge
    
    return lambda_ratio, s[:10]  # return top 10 singular values

def main():
    parser = argparse.ArgumentParser(description='KK Eigenvalue Detector')
    parser.add_argument('--freq', type=float, default=4.77e9, help='Centre frequency (Hz)')
    parser.add_argument('--duration', type=int, default=1800, help='Total duration (seconds)')
    parser.add_argument('--interval', type=float, default=1.0, help='Measurement interval (s)')
    parser.add_argument('--threshold', type=float, default=3.0, help='Detection threshold (sigma)')
    parser.add_argument('--consecutive', type=int, default=10, help='Required consecutive detections')
    parser.add_argument('--logfile', type=str, default='kk_detect.log', help='Output log file')
    args = parser.parse_args()
    
    sample_rate = 2e6
    n_samples = int(sample_rate * 0.5)  # 0.5s capture per window
    
    print("=" * 65)
    print("  KK-5DCOMM Eigenvalue Detector")
    print(f"  Frequency:   {args.freq/1e9:.4f} GHz")
    print(f"  Duration:    {args.duration}s")
    print(f"  Threshold:   Λ > {args.threshold}")
    print(f"  Consecutive: {args.consecutive} windows")
    print("=" * 65)
    
    consecutive_count = 0
    detection = False
    history = []
    
    log = open(args.logfile, 'a')
    log.write(f"\n--- Session {datetime.now().isoformat()} ---\n")
    log.write(f"freq={args.freq}, threshold={args.threshold}\n")
    
    start = time.time()
    window_num = 0
    
    while time.time() - start < args.duration:
        iq = capture_iq(args.freq, sample_rate, n_samples)
        if iq is None or len(iq) < 256:
            time.sleep(args.interval)
            continue
        
        lam, svs = analyze_window(iq)
        window_num += 1
        
        ts = datetime.now().strftime('%H:%M:%S')
        status = '  '
        
        if lam > args.threshold:
            consecutive_count += 1
            status = '▲▲'
            if consecutive_count >= args.consecutive and not detection:
                detection = True
                status = '██'
                print(f"\n  ████ DETECTION at window {window_num} ████")
                print(f"  ████ Λ = {lam:.2f} sustained for {consecutive_count} windows ████\n")
                log.write(f"DETECTION: window={window_num}, lambda={lam:.4f}, consecutive={consecutive_count}\n")
        else:
            consecutive_count = 0
        
        sv_str = ', '.join(f'{s:.1f}' for s in svs[:5])
        print(f"  {ts} | w{window_num:04d} | Λ={lam:6.2f} | {status} | streak={consecutive_count:2d} | σ=[{sv_str}]")
        log.write(f"{ts},{window_num},{lam:.4f},{consecutive_count}\n")
        
        history.append(lam)
        time.sleep(args.interval)
    
    # Summary
    history = np.array(history)
    print("\n" + "=" * 65)
    print("  SESSION SUMMARY")
    print("=" * 65)
    print(f"  Windows analyzed: {len(history)}")
    print(f"  Mean Λ:           {np.mean(history):.3f}")
    print(f"  Max Λ:            {np.max(history):.3f}")
    print(f"  Std Λ:            {np.std(history):.3f}")
    print(f"  Exceedances:      {np.sum(history > args.threshold)}")
    print(f"  Detection:        {'YES ████' if detection else 'NO'}")
    print()
    
    log.write(f"SUMMARY: n={len(history)}, mean={np.mean(history):.4f}, max={np.max(history):.4f}, detected={detection}\n")
    log.close()

if __name__ == '__main__':
    main()
