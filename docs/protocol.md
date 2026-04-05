# Experimental Protocol

## 7-Phase Procedure (~3 hours)

### Phase 1: Calibration (20 min)
1. Connect 50Ω terminator to HackRF antenna port (no cavity, no antenna)
2. Run `cavity_tune.py` — record baseline noise floor
3. Verify: flat noise, no spurious peaks. If peaks exist with terminator → SDR artifact, not real

### Phase 2: Cavity Tuning (30 min)
1. Connect cavity in signal path
2. Run `cavity_tune.py` — sweep 4.5–5.0 GHz
3. Find resonance peak. Record frequency, power, estimated Q
4. If off-target: sand endcap (lowers f) or add copper shim (raises f)
5. Both nodes' cavities must match within ±5 MHz

### Phase 3: Passive Monitoring (30 min)
1. Both nodes in receive-only mode
2. Run `eigenvalue_detect.py --freq 4.77e9 --duration 1800`
3. Record eigenvalue statistics — this is your null hypothesis baseline
4. Any detection in passive mode = environmental interference, not KK

### Phase 4: Active Probing (30 min)
1. Node A transmits narrowband CW at f₁
2. Node B monitors with eigenvalue detector
3. Establish conventional RF link as control
4. Compare eigenvalue statistics with Phase 3

### Phase 5: Frequency Sweep (30 min)
1. Sweep f₁ ± 100 MHz in 1 MHz steps
2. At each step: 30s dwell, record eigenvalue ratio Λ
3. Look for anomalous Λ peak at or near f₁

### Phase 6: Cavity Detuning Control (20 min)
1. Deliberately detune cavity (loosen one endcap slightly)
2. Repeat Phase 4 measurements
3. If previous signal disappears → geometry-dependent (good)
4. If signal persists → conventional RF, not KK coupling

### Phase 7: Analysis (30 min)
1. Compare Λ distributions across all phases
2. Apply detection criterion: Λ > 3 for 10+ consecutive windows
3. Statistical tests: Kolmogorov-Smirnov vs null distribution
4. Document results, save all raw IQ data

## Detection Criteria

A positive detection requires ALL of:
- [ ] Λ > 3 sustained for ≥10 consecutive windows
- [ ] Signal present in Phase 4/5 but absent in Phase 3
- [ ] Signal disappears when cavity is detuned (Phase 6)
- [ ] Signal is NOT present with 50Ω terminator (Phase 1)
- [ ] Repeatable across multiple sessions

## If Detection Occurs

1. **Don't celebrate yet.** Run the full protocol again.
2. Swap nodes (A↔B). Run again.
3. Move to different location. Run again.
4. If it persists through all three: document everything and contact the authors.
