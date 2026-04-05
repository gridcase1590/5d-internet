# Hardware Build Guide

## Overview

Two identical nodes. Each node: Pi + HackRF + Cavity + LPDA. Total cost ~€350/node.

## Copper Cavity Construction

### Materials
- 28mm OD copper pipe (Type L, 1mm wall) — 30mm length
- 28mm copper endcaps × 2
- SMA female bulkhead connectors (panel mount, 50Ω) × 2
- Silver solder (lead-free, flux-core)
- Flux paste (plumbing grade)

### Tools
- Pipe cutter (28mm)
- Drill + 6.35mm (1/4") bit
- Soldering iron 60W+
- 400-grit sandpaper
- Calipers
- Deburring tool

### Steps

**Step 1: Cut pipe**
Cut to exactly 25mm. Use a pipe cutter for a clean perpendicular cut. Deburr both edges.

**Step 2: Sand interior**
Sand the interior surface to 400-grit mirror finish. Surface roughness directly affects Q factor. A smooth interior = higher Q = stronger resonance = better coupling.

**Step 3: Drill SMA holes**
Drill two 6.35mm holes at 90° offset from each other, both at 12.5mm height (midpoint). These are for the SMA bulkhead connectors. Mark carefully — misalignment degrades the mode structure.

**Step 4: Solder bottom endcap**
Apply flux to the pipe exterior and endcap interior. Heat evenly, feed solder around the entire circumference. The seal must be continuous — any gap creates a microwave leak.

**Step 5: Insert SMA connectors**
Thread the SMA bulkhead connectors through the holes. The centre probe pin should extend **exactly 3mm** into the cavity interior. Solder the flange to the pipe wall. This is the most critical dimension — 3mm probe depth sets the coupling coefficient.

**Step 6: Solder top endcap**
Same procedure as bottom. You now have a sealed cylindrical resonator.

### Final Dimensions
- Outer diameter: 28mm
- Inner diameter: 26mm (1mm wall × 2)
- Height: 25mm
- Probe depth: 3mm
- Target frequency: TE₀₁₁ mode at ~4.77 GHz
- Target Q factor: > 1000

## PCB Stack Assembly

### Wiring
1. **Power**: USB-C 5V/3A PSU → Pi USB-C port
2. **Data**: Pi USB 3.0 (blue port) → HackRF USB micro-B (short cable, <30cm)
3. **RF out**: HackRF SMA → SMA male-to-male 50Ω cable → Cavity SMA input
4. **RF antenna**: Cavity SMA output → SMA cable → LPDA antenna SMA

### Critical Notes
- Use the **blue** USB 3.0 ports on the Pi. USB 2.0 has insufficient bandwidth for full SDR streaming.
- All SMA connections: finger-tight + 1/4 turn with wrench. Do NOT overtighten.
- All RF cables must be 50Ω impedance. Do not use random cables.

## Log-Periodic Antenna

Buy the **WA5VJB 1–6.5 GHz PCB log-periodic** (~$20, wa5vjb.com). It covers the full KK search band with 5–7 dBi gain. SMA connector at the rear. Radiation pattern is directional — short elements point toward the other node.

## Two-Node Setup

1. Build two identical nodes
2. Place on bench, antennas facing each other
3. Minimum separation: 2m indoor, 10m+ outdoor
4. Verify both cavities resonate within ±5 MHz of each other (run `cavity_tune.py` on both)
5. Either node can transmit or receive — they're interchangeable

## Mil-Spec Variant

See [`mil-spec/MILSPEC.md`](mil-spec/MILSPEC.md) for the Gridcase 1590 + DTL-38999 ruggedized version.
