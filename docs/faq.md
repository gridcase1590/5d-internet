# FAQ

**Is this real physics or pseudoscience?**
The Kaluza-Klein framework is mainstream physics (1921–present). The ADD large extra dimension model is actively searched for at the LHC. The novel part is the detection method: geometric resonance instead of high-energy collisions. That's a legitimate experimental proposal, not a claim of discovery.

**Has anyone else tried this?**
Not with this specific approach. Extra dimension searches use colliders (ATLAS, CMS), torsion balances (Eöt-Wash), or neutron bound states. Microwave cavity coupling to KK modes is new.

**Why 4.77 GHz specifically?**
f₁ = c/(2πR) for R = 1 cm. The 1 cm radius is the current experimental upper limit for a single large extra dimension from gravitational inverse-square-law tests. If R is smaller, f₁ is higher — but 4.77 GHz is the easiest to build for.

**Won't WiFi at 5 GHz interfere?**
Yes, which is why we don't use power detection. The eigenvalue method (SVD) distinguishes coherent KK coupling from incoherent interference. A KK signal has a specific algebraic signature in the covariance matrix that WiFi doesn't.

**What if R isn't exactly 1 cm?**
That's what the frequency sweep (Phase 5) is for. We scan ±100 MHz around the predicted frequency. If R = 0.95 cm, f₁ ≈ 5.02 GHz. If R = 1.05 cm, f₁ ≈ 4.54 GHz. All within HackRF range.

**What's the most likely outcome?**
Null result. The coupling constant ε is unknown and may be far too small for consumer hardware. But a null result still constrains the ADD parameter space in a regime nobody has tested.

**Can I actually send HTTP over the fifth dimension?**
Not yet. First we need to confirm the coupling exists. If it does, the modulation and framing are straightforward engineering. The latency would be ~0.21 ns through the bulk — faster than any fiber or wireless link.

**How do I know my cavity is good?**
Run `cavity_tune.py`. You should see a clear resonance peak. The Q factor should be >1000. If you see a broad hump instead of a sharp peak, your solder joints have gaps — the cavity is leaking microwaves.

**Can I use an ADALM-PLUTO instead of HackRF?**
Yes. The PlutoSDR covers 325 MHz – 3.8 GHz (nominally) but can be hacked to cover up to ~6 GHz. Slightly cheaper than HackRF. Same signal path.
