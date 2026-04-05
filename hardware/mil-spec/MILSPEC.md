# Mil-Spec Variant: Gridcase 1590 + DTL-38999

## Overview

Same signal path as consumer build, ruggedized for field deployment. The Gridcase 1590 replaces the Raspberry Pi. DTL-38999 Series III circular connectors replace consumer USB/SMA.

## DTL-38999 Connector Panel

Four connectors mounted on an aluminium breakout panel:

| Connector | Shell Size | Insert | Function | Pin Assignment |
|-----------|-----------|--------|----------|----------------|
| J1 DATA | Size 11 | 8-pin, #22 contacts | USB 2.0 to SDR | 1:VCC, 2:D-, 3:D+, 4:GND, 5-8:spare |
| J2 RF | Size 9 | Coax insert, 50Ω | RF signal to cavity | Centre:signal, Shell:ground |
| J3 POWER | Size 9 | 4-pin, #16 contacts | Power distribution | 1:+5V, 2:+12V, 3:GND, 4:GND |
| J4 SERIAL | Size 11 | 6-pin, #22 contacts | RS-232 debug | 1:TX, 2:RX, 3:RTS, 4:CTS, 5:GND, 6:shield |

## DTL-38999 Features

- Bayonet coupling (1/3 turn lock)
- Environmental seal: IP68
- Operating temperature: -65°C to +200°C
- Vibration: MIL-STD-202 Method 204
- Salt spray: MIL-STD-202 Method 101

## Assembly Notes

- All connectors use crimp contacts — solder contacts available but crimp preferred for field repair
- The coax insert for J2 maintains 50Ω impedance through the connector — verify with VNA if available
- Cable loom should be wrapped in braided shield between Gridcase and breakout panel
