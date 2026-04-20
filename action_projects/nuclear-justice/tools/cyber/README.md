# Cyber Disruptor — Tool 1 of PROJECT OMAR

**Nonviolent, precise, reversible disruption of nuclear weapons programs.**

---

## 🎯 What It Does

The **Cyber Disruptor** targets **control systems** (SCADA) of nuclear enrichment facilities to induce **cascading failures** that halt production **without explosions, radiation, or civilian harm**.

**Target:** Centrifuge arrays, coolant systems, sensor networks.

**Effect:** Facility goes offline within minutes; repairs take months; no casualties; no permanent damage.

---

## 🔧 Methods

### 1. Cascade Imbalance
- Alternately slow down / speed up centrifuges
- Creates mechanical stress → automatic safety shutdowns
- Like making a orchestra play out of sync until they stop

### 2. Coolant Disable
- Disable coolant pumps remotely
- Temperature rises → emergency stop triggered
- Reversible: restart pumps once fixed

### 3. Sensor Spoofing
- Feed false readings to operators
- Makes them think everything is fine while production is sabotaged
- Or makes them panic and shut down manually

### 4. Full Disruption (combo)
- All three methods simultaneously
- Guarantees immediate halt

---

## 🎮 Demo

```bash
cd tools/cyber
./demo.sh
```

**Expected output:**
```
[1] Building nuclear facility simulation (100 centrifuges)...
[2] Simulating normal operation (1 hour)...
    Enriched uranium produced: 0.010 kg
[3] Executing CYBER DISRUPTION...
    Result: Cascade imbalance applied...
[4] POST-ATTACK STATUS:
    Centrifuges running: 3/100
    Enriched uranium: 0.010 kg (production halted)
✅ Simulation complete. No real systems were harmed.
```

---

## 🧪 running Tests

```bash
cd tools/cyber
python3 -m pytest tests/test_disruptor.py -v
```

All tests must pass before deployment.

---

## 📦 Installation

```bash
cd tools/cyber
pip install -r requirements.txt  # (currently none, pure Python 3.8+)
```

---

## 🛡️ Safety Features

1. **SIMULATION ONLY** — by default, runs on simulated facilities
2. **Target validation** — before real use, verify target is military nuclear facility (not civilian power plant)
3. **Human-in-the-loop** — Ethics Guardian must approve every action
4. **Reversibility** — attacks are temporary; facility can restart once corrupted logic cleared
5. **Audit trail** — every action logged for transparency

---

## ⚖️ Legal Status

- **IEL:** Non-use of force (cyber operations below threshold of Article 2(4))
- **IHL:** Discrimination & proportionality respected (only military target)
- **Domestic:** Use only with UN authorization or in self-defense against imminent nuclear attack

**Do not use** without proper legal review & Ethics Guardian approval.

---

## 📖 How It Works (Technical)

```
Facility components:
├── CentrifugeArray (100+ machines)
│   ├── Each centrifuge: RPM, temperature, vibration sensors
│   └── Control loop: maintain 90,000 RPM ± 1%
├── CoolantSystem (pumps, heat exchangers)
├── SensorNetwork (reads all parameters)
└── ControlSystem (SCADA: receives sensor → sends setpoints)

Attack vectors:
1. Inject false setpoints → RPM swings → mechanical failure
2. Disable pump signals → temperature rise → thermal shutdown
3. Spoof sensors → operator confusion → manual shutdown
```

All attacks exploit **existing safety mechanisms** (the facility's own protection systems). We don't break anything — we trigger the safety systems to activate prematurely.

---

## 📊 Performance Metrics

| Metric | Target |
|--------|--------|
| Disruption success rate | > 95% |
| Time to halt production | < 10 minutes |
| Physical damage to centrifuges | < 5% (repairable) |
| Civilian infrastructure impact | 0% |
| Reversibility (fix time) | < 1 week with spare parts |
| Detectability (forensic trace) | High (we want attribution) |

---

## 🔗 Integration with Other Tools

- **Legal Qaeda** file case **while** facility down → compound pressure
- **Supply Chain Hunter** block replacement parts → extend downtime
- **Psych Ops Voice** broadcast to personnel: "Your facility is compromised — defect now"
- **Info Dominance** leak the disruption video → public awareness

---

## 📁 Project Structure

```
tools/cyber/
├── src/
│   ├── simulator.py        # Nuclear facility model
│   ├── disruptor.py        # Attack implementations
│   └── nuclear_disruptor_cli.py
├── tests/
│   └── test_disruptor.py
├── demo.sh
└── README.md              # This file
```

---

**"Disrupt, don't destroy. Stop the weapon, spare the people."** — PROJECT OMAR Ethics
