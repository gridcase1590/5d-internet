# 5d-internet

**An experiment to detect a fifth dimension using a copper pipe and a $200 radio.**

![Status](https://img.shields.io/badge/status-experimental-orange)
![Cost](https://img.shields.io/badge/cost-€350%2Fnode-green)
![Freq](https://img.shields.io/badge/frequency-4.77%20GHz-blue)

## What

If spacetime has a compact extra dimension with radius R ≈ 1 cm ([ADD model](https://arxiv.org/abs/hep-ph/9803315) upper limit), the first Kaluza-Klein excitation frequency is:

```
f₁ = c / (2πR) ≈ 4.77 GHz
```

That's a microwave frequency. You can build hardware for that.

This repo contains everything needed to test this: theory, paper, hardware build guide, detection software, and — if it works — the foundation for routing IP packets through the fifth dimension.

## Why Not a Collider?

Colliders use energy to probe extra dimensions. We use geometry. Same physics that makes the Casimir effect work with plates instead of particle beams. A tuned copper cavity creates standing waves whose nodal structure matches the KK compactification circle. If the geometry aligns, energy couples to the bulk.

**Predicted SNR: ~33 dB.** That's not marginal. That's loud.

## Hardware (€350/node)

| Component | Purpose | Cost |
|-----------|---------|------|
| Raspberry Pi 4B | GNU Radio host | €60 |
| HackRF One | SDR transceiver (1 MHz – 6 GHz) | €200 |
| Copper cavity | TE₀₁₁ resonator at 4.77 GHz | €15 |
| WA5VJB LPDA | Log-periodic antenna (1–6.5 GHz) | €20 |
| SMA cables + misc | 50Ω signal path | €55 |

The cavity is a 28mm copper pipe, 25mm tall, two endcaps, two SMA connectors. You can build it with plumbing supplies and a soldering iron.

Full build instructions: [`hardware/BUILD.md`](hardware/BUILD.md)

## Detection

We don't look for power spikes — WiFi and radar live at 5 GHz too. Instead we use **eigenvalue-based detection**: SVD of the IQ covariance matrix, looking for singular values that exceed the Marchenko-Pastur random matrix edge. A KK signal is coherent in a way that interference isn't.

```
Λ = σ_max / σ_MP > 3  (sustained for 10+ windows)
```

## The 5D Internet Part

If you can send a signal through the bulk, you can modulate it. If you can modulate it, you can frame packets. If you can frame packets, you can route IP.

```
[ Ethernet ] → [ Pi ] → [ HackRF ] → [ Cavity ] → [ KK Bulk ] → [ Cavity ] → [ HackRF ] → [ Pi ] → [ Ethernet ]
                                                        ↑
                                              fifth spatial dimension
                                              latency: ~0.21 ns
```

That's faster than fiber. No repeaters. No cables. No line-of-sight requirement (the bulk doesn't care about 4D obstacles).

This is speculative. But the hardware to test it costs less than a nice dinner for two.

## Papers

- [Geometric Microwave Coupling to Kaluza-Klein Extra Dimensions](paper/kk5dcomm_paper.pdf) — this project's paper
- [A Geometric Halting Detector](https://doi.org/10.5281/zenodo.19412086) — related prior work
- [The Spiral Angle of the Non-Closing Torus](https://zenodo.org) — Euler-Mascheroni constant geometry (related)

## Repo Structure

```
5d-internet/
├── README.md
├── LICENSE
├── paper/
│   └── kk5dcomm_paper.pdf        # Preprint
├── hardware/
│   ├── BUILD.md                   # Complete construction guide
│   ├── BOM.md                     # Bill of materials
│   └── mil-spec/                  # Gridcase 1590 + DTL-38999 variant
│       └── MILSPEC.md
├── software/
│   ├── cavity_tune.py             # Cavity resonance finder
│   ├── eigenvalue_detect.py       # KK signal detection (SVD)
│   ├── kk_monitor.py              # Real-time monitoring dashboard
│   └── gnuradio/
│       └── kk_flowgraph.grc       # GNU Radio companion flowgraph
└── docs/
    ├── theory.md                  # Physics background
    ├── protocol.md                # 7-phase experiment procedure
    └── faq.md                     # Common questions
```

## Quick Start

```bash
# 1. Build two nodes (see hardware/BUILD.md)
# 2. Flash Raspberry Pi OS 64-bit
# 3. Install dependencies
sudo apt install gnuradio hackrf gr-osmosdr python3-numpy python3-scipy

# 4. Tune your cavity
python3 software/cavity_tune.py

# 5. Run detection
python3 software/eigenvalue_detect.py --freq 4.77e9 --duration 1800
```

## Related Work

- Arkani-Hamed, Dimopoulos, Dvali — [ADD Model (1998)](https://arxiv.org/abs/hep-ph/9803315)
- Megidish et al. — [Temporal Entanglement (2013)](https://arxiv.org/abs/1209.4191)
- Wesson — Space-Time-Matter (1999)

## Authors
([@v3rdad](https://t.me/v3rdad)) — Theory, experimental design, hardware

With analytical contributions by **Claude (Opus)**, Anthropic

## License

MIT. Build it. Test it. If it works, tell everyone.
